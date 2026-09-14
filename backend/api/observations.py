"""Submitting an observation, reading one back, and answering a question about it."""

import json
import shutil
from pathlib import Path
from typing import Any

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from adapters import store, vision
from domain import assess

from .shared import UPLOADS, differentials_from

router = APIRouter(prefix="/api/observations", tags=["observations"])


@router.post("")
async def create(
    answers_json: str = Form(...),
    record_class: str = Form("authentic"),
    site_name: str | None = Form(None),
    lat: float | None = Form(None),
    lon: float | None = Form(None),
    photo: UploadFile | None = File(None),
) -> JSONResponse:
    """Submit an observation. Always accepted, always stored, never auto-judged."""
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
        dest = UPLOADS / Path(photo.filename).name
        with dest.open("wb") as fh:
            shutil.copyfileobj(photo.file, fh)
        photo_path = f"/uploads/{dest.name}"

    findings, vision_status = vision.analyse(
        UPLOADS / Path(photo_path).name if photo_path else None)

    oid = store.create(answers, record_class, site_name, lat, lon, photo_path, findings)
    return JSONResponse({
        "id": oid,
        "observation": store.get(oid),
        "assessment": assess.assess(answers, findings, "not_reviewed", {}),
        "vision_status": vision_status,
        "notice": (
            "Photo analysis is unavailable, so fewer clarifying questions could be "
            "offered. Your observation has been recorded in full and sent for human "
            "review."
        ) if vision_status == "unavailable" else None,
    })


@router.get("/{oid}")
def get_one(oid: str) -> dict[str, Any]:
    rec = store.get(oid)
    if rec is None:
        raise HTTPException(404, "observation not found")
    return {
        "observation": rec,
        "assessment": assess.assess(rec["answers"], rec["photo_findings"],
                                    rec["review_status"], differentials_from(rec)),
    }


@router.post("/{oid}/clarify")
def clarify(oid: str, question_id: str = Form(...), question: str = Form(...),
            field: str = Form(...), response: str = Form(...),
            citizen_disagrees: bool = Form(False),
            indicator: str | None = Form(None),
            option_key: str | None = Form(None)) -> dict[str, Any]:
    """Record the citizen's answer to a question.

    Appends. Never edits the original answers -- a reviewer must be able to see
    what was first reported next to what was said after being prompted, because
    the difference between those two is the point of this system.
    """
    if store.get(oid) is None:
        raise HTTPException(404, "observation not found")
    store.add_clarification(oid, question_id, question, field, response,
                            citizen_disagrees, indicator, option_key)
    return get_one(oid)
