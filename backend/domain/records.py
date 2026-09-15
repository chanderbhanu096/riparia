"""Pure reads of the immutable report and its append-only clarification trail."""

import hashlib
import json
from typing import Any


def differentials_from(rec: dict[str, Any]) -> dict[str, str]:
    """The most recent citizen answer to each field differential."""
    out = {}
    for item in rec.get("clarifications", []):
        if item.get("indicator") and item.get("option_key"):
            out[item["indicator"]] = item["option_key"]
    return out


def content_fingerprint(rec: dict[str, Any]) -> str:
    """Bind approval to the exact report content the reviewer saw.

    This detects subsequent clarification; it is not a digital signature or proof
    of identity. Canonical JSON preserves values, not the original wire formatting.
    """
    content = {key: rec.get(key) for key in
               ("answers", "clarifications", "photo_findings", "photo_path",
                "site_name", "lat", "lon", "record_class")}
    canonical = json.dumps(content, sort_keys=True, separators=(",", ":"),
                           ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def summary_eligibility(rec: dict[str, Any]) -> dict[str, Any]:
    review = rec.get("review") or {}
    if (rec.get("review_status") != "reviewer_assessed"
            or not str(review.get("reviewer") or "").strip()
            or not str(review.get("decision") or "").strip()
            or review.get("approved_for_summary") is not True):
        return {"eligible": False, "reason": "A named reviewer has not approved this report for the site summary."}
    if review.get("reviewed_content_sha256") != content_fingerprint(rec):
        return {"eligible": False, "reason": "The report changed after approval. A reviewer must assess it again."}
    return {"eligible": True, "reason": "A named reviewer approved this version for the site summary."}
