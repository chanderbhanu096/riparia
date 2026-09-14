"""The reviewer queue and the recording of an attributed assessment."""

from typing import Any

from fastapi import APIRouter, Form, HTTPException

from adapters import store
from domain import assess

from .shared import differentials_from

router = APIRouter(prefix="/api", tags=["review"])


@router.get("/queue")
def queue() -> dict[str, Any]:
    """Ordered by consequence under uncertainty (AUDIT.md D-012).

    Deliberately NOT newest-first. An uncertain report of something serious sits
    above a tidy report of nothing much, because that is where a reviewer's time
    changes an outcome.
    """
    items = []
    for rec in store.list_all():
        a = assess.assess(rec["answers"], rec["photo_findings"], rec["review_status"],
                          differentials_from(rec))
        items.append({
            "id": rec["id"], "created_at": rec["created_at"],
            "record_class": rec["record_class"], "site_name": rec["site_name"],
            "photo_path": rec["photo_path"], "review_status": rec["review_status"],
            "assessment": a,
        })
    items.sort(key=lambda i: (i["review_status"] != "not_reviewed",
                              -i["assessment"]["triage"]["score"]))
    return {"count": len(items), "items": items,
            "ordering": "consequence under uncertainty, then unreviewed first"}


@router.post("/observations/{oid}/review")
def review(oid: str, reviewer: str = Form(...), decision: str = Form(...),
           note: str = Form("")) -> dict[str, Any]:
    """Record a named reviewer's attributed assessment.

    `decision` is free text on purpose. Forcing it into accept/reject would
    reintroduce the binary verdict D-012 removed.
    """
    rec = store.get(oid)
    if rec is None:
        raise HTTPException(404, "observation not found")
    if not reviewer.strip():
        raise HTTPException(400, "a reviewer must be named -- decisions are attributed")
    store.set_review(oid, reviewer.strip(), decision, note)
    rec = store.get(oid)
    return {
        "observation": rec,
        "assessment": assess.assess(rec["answers"], rec["photo_findings"],
                                    rec["review_status"], differentials_from(rec)),
    }
