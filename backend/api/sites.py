"""Reviewer-approved site evidence and downloadable provenance JSON."""

from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from adapters import store
from domain.handoff import export_envelope, site_key, site_summaries
from domain.records import summary_eligibility

RecordClass = Literal["authentic", "synthetic", "evaluation"]
router = APIRouter(prefix="/api", tags=["site summary and export"])


@router.get("/sites")
def sites(record_class: RecordClass = "authentic") -> dict:
    return site_summaries(store.list_all(), record_class)


def download(records: list[dict], filename: str) -> JSONResponse:
    generated_at = datetime.now(timezone.utc).isoformat()
    return JSONResponse(export_envelope(records, generated_at), headers={
        "Content-Disposition": f'attachment; filename="{filename}"',
    })


@router.get("/sites/{key}/export")
def export_site(key: str, record_class: RecordClass = "authentic") -> JSONResponse:
    records = [rec for rec in store.list_all()
               if rec["record_class"] == record_class and site_key(rec) == key]
    if not records:
        raise HTTPException(404, "site not found for this record class")
    approved = [rec for rec in records if summary_eligibility(rec)["eligible"]]
    if not approved:
        raise HTTPException(409, "This site has no reports explicitly approved for export.")
    return download(approved, f"riparia-site-{key}-{record_class}.json")


@router.get("/observations/{oid}/export")
def export_observation(oid: str) -> JSONResponse:
    rec = store.get(oid)
    if rec is None:
        raise HTTPException(404, "observation not found")
    eligibility = summary_eligibility(rec)
    if not eligibility["eligible"]:
        raise HTTPException(409, eligibility["reason"])
    return download([rec], f"riparia-observation-{oid}-{rec['record_class']}.json")
