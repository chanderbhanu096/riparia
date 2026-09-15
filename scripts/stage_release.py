"""Build a code-only Azure ZIP outside the repository; never includes runtime data.

Run only after the final frontend build. Outputs the staged shell SHA256 so the
live release can be checked independently of Azure's deployment return code.
"""

import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def stage():
    dist = ROOT / "frontend" / "dist"
    if not (dist / "index.html").is_file():
        raise RuntimeError("Build the final frontend first")
    release = Path(tempfile.mkdtemp(prefix="riparia-release-"))
    tree = release / "app"
    tree.mkdir()
    for filename in ("main.py", "config.py", "requirements.txt"):
        shutil.copy2(ROOT / "backend" / filename, tree / filename)
    for package in ("api", "adapters", "domain"):
        for source in (ROOT / "backend" / package).rglob("*.py"):
            destination = tree / source.relative_to(ROOT / "backend")
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
    shutil.copytree(dist, tree / "static")
    files = sorted(path for path in tree.rglob("*") if path.is_file())
    for path in files:
        if path.suffix in {".db", ".sqlite", ".sqlite3", ".pyc", ".env"} or path.name.startswith(".env") or "uploads" in path.relative_to(tree).parts:
            raise RuntimeError(f"Forbidden runtime/secret file in release: {path.name}")
    # Read values silently for leak detection; never print credentials.
    import sys
    sys.path.insert(0, str(ROOT / "backend"))
    import config
    secrets = [value.encode() for key in ("AZURE_AI_KEY",) if (value := config.get(key))]
    for path in files:
        if any(secret in path.read_bytes() for secret in secrets):
            raise RuntimeError("Credential leak check failed; release was not archived")
    archive = release / "riparia.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for path in files:
            bundle.write(path, path.relative_to(tree))
    manifest = {"stage": str(tree), "zip": str(archive), "file_count": len(files),
                "index_sha256": hashlib.sha256((dist / "index.html").read_bytes()).hexdigest(),
                "zip_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
                "runtime_data_included": False}
    (release / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    stage()
