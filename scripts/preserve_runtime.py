"""Run INSIDE the Azure app container before deployment; no Azure secrets needed.

Default: verified backup + persistent copy while writes remain enabled.
--freeze: briefly block writes to the old runtime DB, then refresh that copy.
--unfreeze: rollback the maintenance gate if deployment does not activate.

Never run --freeze until the release is ready to deploy. The new app uses the
persistent DB, from which maintenance triggers are removed before activation.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3

TRIGGERS = [f"riparia_deploy_block_{operation.lower()}" for operation in ("INSERT", "UPDATE", "DELETE")]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path):
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        return con.execute("SELECT * FROM observations ORDER BY id").fetchall()
    finally:
        con.close()


def gate(path, freeze):
    con = sqlite3.connect(path, timeout=30)
    try:
        with con:
            con.execute("BEGIN IMMEDIATE")
            for operation, name in zip(("INSERT", "UPDATE", "DELETE"), TRIGGERS):
                if freeze:
                    con.execute(f"CREATE TRIGGER IF NOT EXISTS {name} BEFORE {operation} ON observations "
                                "BEGIN SELECT RAISE(ABORT, 'Brief deployment maintenance; please retry shortly'); END")
                else:
                    con.execute(f"DROP TRIGGER IF EXISTS {name}")
    finally:
        con.close()


def backup(source, destination):
    src = sqlite3.connect(f"file:{source}?mode=ro", uri=True)
    dst = sqlite3.connect(destination)
    try:
        src.backup(dst)
        integrity = dst.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise RuntimeError("Database integrity check failed")
    finally:
        dst.close()
        src.close()


def preserve(runtime, persistent, freeze=False, unfreeze=False):
    source = runtime / "adapters" / "riparia.db"
    target = persistent / "riparia.db"
    if not source.is_file():
        raise RuntimeError(f"Expected current runtime database at {source}")
    if source.resolve() == target.resolve():
        raise RuntimeError("Source already uses persistent storage; no migration is needed")
    if unfreeze:
        gate(source, False)
        print(json.dumps({"writes_restored": True, "source": str(source)}))
        return
    if freeze:
        gate(source, True)
    try:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        archive = persistent.parent / "riparia-backups" / stamp
        archive.mkdir(parents=True)
        backup(source, archive / "riparia.db")
        source_uploads = runtime / "uploads"
        if source_uploads.exists():
            shutil.copytree(source_uploads, archive / "uploads")
        else:
            (archive / "uploads").mkdir()
        archived_rows = rows(archive / "riparia.db")
        if archived_rows != rows(source):
            raise RuntimeError("Source changed during backup; rerun at the final write freeze")
        persistent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            source_ids = {row[0] for row in archived_rows}
            target_ids = {row[0] for row in rows(target)}
            if target_ids - source_ids:
                raise RuntimeError("Persistent DB contains additional records; refusing to overwrite it")
        candidate = persistent / "riparia.db.next"
        shutil.copy2(archive / "riparia.db", candidate)
        gate(candidate, False)
        os.replace(candidate, target)
        shutil.copytree(archive / "uploads", persistent / "uploads", dirs_exist_ok=True)
        if rows(target) != archived_rows:
            raise RuntimeError("Persistent record verification failed")
        con = sqlite3.connect(target)
        try:
            references = [row[0] for row in con.execute("SELECT photo_path FROM observations WHERE photo_path IS NOT NULL")]
        finally:
            con.close()
        missing = []
        photo_hashes = {}
        for reference in references:
            filename = Path(reference).name
            original = archive / "uploads" / filename
            copied = persistent / "uploads" / filename
            if not original.is_file():
                missing.append(reference)
                continue
            if not copied.is_file() or digest(original) != digest(copied):
                raise RuntimeError(f"Photo verification failed: {filename}")
            photo_hashes[filename] = digest(copied)
        manifest = {"backup": str(archive), "persistent": str(persistent),
                    "records": len(archived_rows), "photo_references": len(references),
                    "distinct_photo_references": len(set(references)),
                    "preserved_photos": len(photo_hashes),
                    "already_missing_photo_references": missing,
                    "old_runtime_writes_frozen": freeze,
                    "database_sha256": digest(target),
                    "photo_hashes": photo_hashes}
        (archive / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        print(json.dumps(manifest))
    except BaseException:
        if freeze:
            gate(source, False)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", type=Path, default=Path(os.environ.get("APP_PATH", ".")))
    parser.add_argument("--persistent", type=Path, default=Path("/home/data/riparia"))
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--freeze", action="store_true")
    group.add_argument("--unfreeze", action="store_true")
    args = parser.parse_args()
    preserve(args.runtime, args.persistent, args.freeze, args.unfreeze)
