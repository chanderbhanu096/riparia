"""RIPARIA API -- a human-in-the-loop trust layer for citizen stream assessments.

OneAquaHealth IEEE Global Hackathon 2026, Track 3 (AI-Supported Assessment).
Design decisions and their reasoning live in ../AUDIT.md. Read D-012 before
changing any endpoint here.

The contract these routes keep:
  - Nothing is auto-accepted and nothing is auto-rejected.
  - The citizen's original answers are returned alongside every clarification,
    so a reviewer always sees what was first said.
  - Nothing is described as "validated" until a named reviewer says so.
  - When the vision model is unavailable the observation is still accepted in
    full and routed to human review. Degraded, never dropped.
"""

import shutil
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

import field_protocol as fp
import store
import vision
from assess import assess

UPLOADS = Path(__file__).parent / "uploads"
UPLOADS.mkdir(exist_ok=True)

app = FastAPI(
    title="RIPARIA",
    description=(
        "A human-in-the-loop trust layer for citizen stream assessments. "
        "This API describes citizen observations across four separate dimensions. "
        "It does not score, validate, accept or reject them -- only a named "
        "reviewer does that."
    ),
    version="0.1.0",
)

# Dev-wide CORS: this is a hackathon prototype with no accounts and no private
# data. ponytail: open CORS, lock to an origin list if this is ever deployed for real.
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=UPLOADS), name="uploads")


@app.on_event("startup")
def _startup() -> None:
    store.init()


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {"ok": True, "service": "riparia"}


@app.get("/api/protocol")
def protocol() -> dict[str, Any]:
    """The indicator list the citizen form is built from.

    Served from field_protocol so the domain content has exactly one home. The
    frontend renders whatever this returns and holds no ecological knowledge of
    its own -- which is also what makes the domain layer reviewable by a
    freshwater ecologist in isolation (AUDIT.md Q9).
    """
    return {
        "indicators": [
            {"key": k, "label": v["label"], "has_differential": bool(v.get("differential"))}
            for k, v in fp.INDICATORS.items()
        ],
        "note": (
            "Indicators are limited to what a person can observe without equipment "
            "or training. Nothing here requires a test kit or species identification."
        ),
    }


def _differentials_from(rec: dict[str, Any]) -> dict[str, str]:
    """Rebuild the citizen's differential answers from the clarification log.

    Derived, never stored twice: the clarification log is the record, and this is
    a read of it. That keeps the original answers immutable (D-012) while still
    letting the assessment reflect what the citizen said afterwards.
    """
    out: dict[str, str] = {}
    for c in rec.get("clarifications", []):
        if c.get("indicator") and c.get("option_key"):
            out[c["indicator"]] = c["option_key"]
    return out


def _vision(photo_path: Path | None) -> tuple[dict[str, Any] | None, str]:
    """Photo pass. Delegates to vision.py, which can only ever raise questions.

    Every failure mode inside vision.analyse() returns (None, "unavailable"), and
    that path is the one the system was built on first -- so a model outage is an
    ordinary, well-exercised state here, not an emergency (AUDIT.md A4, D-023).
    """
    return vision.analyse(photo_path)


@app.post("/api/observations")
async def create_observation(
    answers_json: str = Form(...),
    record_class: str = Form("authentic"),
    site_name: str | None = Form(None),
    lat: float | None = Form(None),
    lon: float | None = Form(None),
    photo: UploadFile | None = File(None),
) -> JSONResponse:
    """Submit an observation. Always accepted, always stored, never auto-judged."""
    import json
    try:
        answers = json.loads(answers_json)
    except json.JSONDecodeError:
        raise HTTPException(400, "answers_json must be valid JSON")
    if not isinstance(answers, dict):
        raise HTTPException(400, "answers_json must be a JSON object")
    if record_class not in store.RECORD_CLASSES:
        raise HTTPException(400, f"record_class must be one of {store.RECORD_CLASSES}")

    photo_path = None
    if photo is not None and photo.filename:
        dest = UPLOADS / f"{photo.filename}"
        with dest.open("wb") as fh:
            shutil.copyfileobj(photo.file, fh)
        photo_path = f"/uploads/{dest.name}"

    findings, vision_status = _vision(UPLOADS / Path(photo_path).name if photo_path else None)

    oid = store.create(answers, record_class, site_name, lat, lon, photo_path, findings)
    rec = store.get(oid)
    return JSONResponse({
        "id": oid,
        "observation": rec,
        "assessment": assess(answers, findings, "not_reviewed", {}),
        "vision_status": vision_status,
        "notice": (
            "Photo analysis is unavailable, so fewer clarifying questions could be "
            "offered. Your observation has been recorded in full and sent for human "
            "review."
        ) if vision_status == "unavailable" else None,
    })


@app.get("/api/observations/{oid}")
def get_observation(oid: str) -> dict[str, Any]:
    rec = store.get(oid)
    if rec is None:
        raise HTTPException(404, "observation not found")
    return {
        "observation": rec,
        "assessment": assess(rec["answers"], rec["photo_findings"],
                             rec["review_status"], _differentials_from(rec)),
    }


@app.post("/api/observations/{oid}/clarify")
def clarify(oid: str, question_id: str = Form(...), question: str = Form(...),
            field: str = Form(...), response: str = Form(...),
            citizen_disagrees: bool = Form(False),
            indicator: str | None = Form(None),
            option_key: str | None = Form(None)) -> dict[str, Any]:
    """Record the citizen's answer to a clarifying question.

    This appends. It never edits the original answers -- a reviewer must be able to
    see what was first reported next to what was said after being prompted, because
    the difference between those two is the thing this whole project is about.
    """
    if store.get(oid) is None:
        raise HTTPException(404, "observation not found")
    store.add_clarification(oid, question_id, question, field, response,
                            citizen_disagrees, indicator, option_key)
    return get_observation(oid)


@app.get("/api/queue")
def queue() -> dict[str, Any]:
    """Reviewer queue, ordered by consequence under uncertainty (D-012).

    Deliberately NOT newest-first. An uncertain report of something serious sits
    above a tidy report of nothing much, because that is where a reviewer's time
    changes an outcome.
    """
    items = []
    for rec in store.list_all():
        a = assess(rec["answers"], rec["photo_findings"], rec["review_status"],
                   _differentials_from(rec))
        items.append({
            "id": rec["id"],
            "created_at": rec["created_at"],
            "record_class": rec["record_class"],
            "site_name": rec["site_name"],
            "photo_path": rec["photo_path"],
            "review_status": rec["review_status"],
            "assessment": a,
        })
    items.sort(key=lambda i: (i["review_status"] != "not_reviewed",
                              -i["assessment"]["triage"]["score"]))
    return {"count": len(items), "items": items,
            "ordering": "consequence under uncertainty, then unreviewed first"}


@app.post("/api/observations/{oid}/review")
def review(oid: str, reviewer: str = Form(...), decision: str = Form(...),
           note: str = Form("")) -> dict[str, Any]:
    """Record a named reviewer's attributed assessment.

    `decision` is free text on purpose. Forcing it into accept/reject would
    reintroduce exactly the binary verdict D-012 removed.
    """
    if store.get(oid) is None:
        raise HTTPException(404, "observation not found")
    if not reviewer.strip():
        raise HTTPException(400, "a reviewer must be named -- decisions are attributed")
    store.set_review(oid, reviewer.strip(), decision, note)
    return get_observation(oid)


# --- static frontend -----------------------------------------------------------
# Mounted LAST so every /api route above wins. In development this directory does
# not exist (Vite serves the frontend on its own port) and the block is skipped.
DIST = Path(__file__).parent.parent / "frontend" / "dist"

if DIST.is_dir():
    app.mount("/assets", StaticFiles(directory=DIST / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa(full_path: str) -> FileResponse:
        """Serve the SPA, falling back to index.html for client-side routes.

        A real file wins if one exists (favicon, icons); anything else returns the
        app shell so a deep link does not 404.
        """
        candidate = DIST / full_path
        if full_path and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(DIST / "index.html")
