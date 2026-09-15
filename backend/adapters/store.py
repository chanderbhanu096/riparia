"""SQLite persistence. stdlib sqlite3, no ORM -- the schema is seven columns wide.

The one rule this module exists to enforce (AUDIT.md D-012):

    `answers` is written ONCE at submission and is never updated thereafter.

Clarifications and reviewer decisions are appended to their own columns. The
citizen's original account stays readable forever, next to whatever was added
later. There is deliberately no code path in this file that UPDATEs `answers`.
"""

import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from domain.records import content_fingerprint
import config

DB_PATH = (config.DATA_DIR / "riparia.db" if config.DATA_DIR else
           Path(__file__).parent / "riparia.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS observations (
    id            TEXT PRIMARY KEY,
    created_at    TEXT NOT NULL,
    record_class  TEXT NOT NULL,   -- synthetic | authentic | evaluation (D-015)
    site_name     TEXT,
    lat           REAL,
    lon           REAL,
    photo_path    TEXT,
    answers       TEXT NOT NULL,   -- JSON. WRITE ONCE. Never UPDATEd.
    clarifications TEXT NOT NULL,  -- JSON list, appended
    photo_findings TEXT,           -- JSON or NULL when the model was unavailable
    review        TEXT,            -- JSON attributed assessment, or NULL
    review_status TEXT NOT NULL    -- not_reviewed | in_review | reviewer_assessed
);
"""

RECORD_CLASSES = ("synthetic", "authentic", "evaluation")


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        with con:
            yield con
    finally:
        con.close()


def init() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with connect() as con:
        con.executescript(SCHEMA)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create(answers: dict[str, Any], record_class: str, site_name: str | None = None,
           lat: float | None = None, lon: float | None = None,
           photo_path: str | None = None,
           photo_findings: dict[str, Any] | None = None) -> str:
    if record_class not in RECORD_CLASSES:
        raise ValueError(f"record_class must be one of {RECORD_CLASSES}")
    oid = uuid.uuid4().hex[:12]
    with connect() as con:
        con.execute(
            "INSERT INTO observations (id, created_at, record_class, site_name, lat,"
            " lon, photo_path, answers, clarifications, photo_findings, review,"
            " review_status) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (oid, _now(), record_class, site_name, lat, lon, photo_path,
             json.dumps(answers), json.dumps([]),
             json.dumps(photo_findings) if photo_findings else None,
             None, "not_reviewed"),
        )
    return oid


def add_clarification(oid: str, question_id: str, question: str, field: str,
                      response: str, citizen_disagrees: bool = False,
                      indicator: str | None = None,
                      option_key: str | None = None) -> None:
    """Append a clarification. The original `answers` row is untouched, always.

    `citizen_disagrees` records that the citizen stood by their original account
    against the model's prompt. That is a legitimate and expected outcome, and it
    is stored as data rather than treated as a problem to resolve (D-012).
    """
    with connect() as con:
        con.execute("BEGIN IMMEDIATE")
        row = con.execute(
            "SELECT clarifications FROM observations WHERE id=?", (oid,)
        ).fetchone()
        if row is None:
            raise KeyError(oid)
        items = json.loads(row["clarifications"])
        items.append({
            "question_id": question_id,
            "question": question,
            "field": field,
            "response": response,
            "citizen_disagrees": citizen_disagrees,
            "indicator": indicator,
            "option_key": option_key,
            "at": _now(),
        })
        con.execute("UPDATE observations SET clarifications=? WHERE id=?",
                    (json.dumps(items), oid))


def set_review(oid: str, reviewer: str, decision: str, note: str,
               approved_for_summary: bool = False,
               reviewed_content_sha256: str | None = None) -> None:
    """Record a reviewer's ATTRIBUTED assessment -- not 'ground truth' (D-012).

    A reviewer is a named person with an opinion, and reviewers disagree with each
    other. Storing the name alongside the decision keeps that visible instead of
    laundering one person's judgement into fact.
    """
    with connect() as con:
        con.execute("BEGIN IMMEDIATE")
        row = con.execute("SELECT * FROM observations WHERE id=?", (oid,)).fetchone()
        if row is None:
            raise KeyError(oid)
        rec = _hydrate(row)
        fingerprint = content_fingerprint(rec)
        if approved_for_summary and reviewed_content_sha256 != fingerprint:
            raise ValueError("The report changed or no reviewed version was supplied. Reload and review the current report before approving it.")
        previous = rec.get("review") or {}
        history = list(previous.get("history", []))
        if previous:
            history.append({key: value for key, value in previous.items() if key != "history"})
        review = {"reviewer": reviewer, "decision": decision, "note": note,
                  "at": _now(), "approved_for_summary": approved_for_summary,
                  "reviewed_content_sha256": fingerprint,
                  "history": history}
        con.execute(
            "UPDATE observations SET review=?, review_status=? WHERE id=?",
            (json.dumps(review), "reviewer_assessed", oid),
        )


def set_in_review(oid: str) -> None:
    with connect() as con:
        con.execute(
            "UPDATE observations SET review_status='in_review' WHERE id=?"
            " AND review_status='not_reviewed'", (oid,))


def get(oid: str) -> dict[str, Any] | None:
    with connect() as con:
        row = con.execute("SELECT * FROM observations WHERE id=?", (oid,)).fetchone()
    return _hydrate(row) if row else None


def list_all() -> list[dict[str, Any]]:
    with connect() as con:
        rows = con.execute(
            "SELECT * FROM observations ORDER BY created_at DESC").fetchall()
    return [_hydrate(r) for r in rows]


def _hydrate(row: sqlite3.Row) -> dict[str, Any]:
    d = dict(row)
    d["answers"] = json.loads(d["answers"])
    d["clarifications"] = json.loads(d["clarifications"])
    d["photo_findings"] = json.loads(d["photo_findings"]) if d["photo_findings"] else None
    d["review"] = json.loads(d["review"]) if d["review"] else None
    return d
