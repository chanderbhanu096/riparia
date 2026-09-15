"""A bounded site summary and a reproducible handoff, never a health diagnosis.

Only an explicit, current reviewer approval admits evidence. Ecological wording
comes from field_protocol through assess; no new ecology is invented here.
"""

import hashlib
import json
from typing import Any

from .assess import assess
from .field_protocol import PROTOCOL_VERSION
from .records import content_fingerprint, differentials_from, summary_eligibility

SCHEMA_VERSION = "riparia.provenance.v1"
LIMITATIONS = [
    "Reports describe what people observed; they do not establish water safety, exposure, disease or a Water Framework Directive status.",
    "Only reports explicitly approved by a named reviewer are included as evidence. Approval is an attributed judgment, not ground truth.",
    "Authentic, simulated and evaluation records are kept separate. Record class and reviewer identity are self-declared in this prototype.",
    "Site groups use the submitted name and coordinates, not a verified site registry. No trend or representativeness is inferred.",
]


def site_key(rec: dict[str, Any]) -> str:
    """Conservative grouping: never spatially guess that two reports share a site."""
    name = " ".join((rec.get("site_name") or "").split()).casefold()
    if name in {"unnamed reach", "unnamed site"}:
        name = ""
    identity = [name, rec.get("lat"), rec.get("lon")]
    if not name and rec.get("lat") is None and rec.get("lon") is None:
        identity.append(rec["id"])
    return hashlib.sha256(json.dumps(identity, ensure_ascii=False).encode()).hexdigest()[:16]


def assessment_for(rec: dict[str, Any]) -> dict[str, Any]:
    return assess(rec["answers"], rec.get("photo_findings"),
                  rec["review_status"], differentials_from(rec))


def site_summaries(records: list[dict[str, Any]], record_class: str) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for rec in records:
        if rec["record_class"] == record_class:
            groups.setdefault(site_key(rec), []).append(rec)
    sites = []
    for key, group in groups.items():
        approved = [rec for rec in group if summary_eligibility(rec)["eligible"]]
        approved.sort(key=lambda rec: rec["created_at"], reverse=True)
        evidence, notes = [], []
        for rec in approved:
            assessment = assessment_for(rec)
            notes.extend(assessment["ecological_urgency"]["one_health_notes"])
            evidence.append({
                "id": rec["id"], "created_at": rec["created_at"],
                "record_class": rec["record_class"], "review": rec["review"],
                "assessment": assessment, "photo_path": rec.get("photo_path"),
                "export_url": f"/api/observations/{rec['id']}/export",
            })
        count = len(approved)
        summary = (f"{count} report{'s' if count != 1 else ''} explicitly approved for this site summary. "
                   "Read the recorded observations and reviewer decisions below.") if count else (
                       "No reports have been approved for this site summary. There is no reviewed evidence to summarise yet.")
        sites.append({
            "site_key": key, "site_name": group[0].get("site_name") or "Unnamed site",
            "record_class": record_class,
            "coordinates": {"lat": group[0].get("lat"), "lon": group[0].get("lon")},
            "approved_count": count, "pending_count": len(group) - count,
            "high_urgency_count": sum(item["assessment"]["ecological_urgency"]["level"] == "high" for item in evidence),
            "latest_approved_at": max((rec["review"]["at"] for rec in approved), default=None),
            "summary": summary, "one_health_notes": list(dict.fromkeys(notes)),
            "records": evidence,
            "export_url": f"/api/sites/{key}/export?record_class={record_class}",
        })
    sites.sort(key=lambda site: (-site["approved_count"], site["site_name"].casefold(), site["site_key"]))
    return {"record_class": record_class, "count": len(sites), "sites": sites,
            "approved_count": sum(site["approved_count"] for site in sites),
            "pending_count": sum(site["pending_count"] for site in sites),
            "limitations": LIMITATIONS}


def proposed_fhir_mapping(rec: dict[str, Any], assessment: dict[str, Any],
                          generated_at: str) -> dict[str, Any]:
    """HL7 FHIR R4 *proposal*, intentionally not a claim of interoperability.

    R4 Observation permits a Location subject. Only the existing protocol's
    possible contact-hazard readings are projected, never a fictional patient,
    measured toxin, confirmed exposure or clinical diagnosis.
    Sources and omissions: docs/EXPORT.md.
    """
    candidates = [(indicator, reading) for indicator, reading in
                  assessment["ecological_urgency"]["resolved"].items()
                  if reading.get("one_health")]
    resources = []
    if candidates:
        location = {"resourceType": "Location", "id": f"site-{site_key(rec)}",
                    "name": rec.get("site_name") or "Unnamed reported site",
                    "description": "Citizen-supplied site; not a verified location registry."}
        lat, lon = rec.get("lat"), rec.get("lon")
        if (isinstance(lat, (int, float)) and isinstance(lon, (int, float))
                and -90 <= lat <= 90 and -180 <= lon <= 180):
            location["position"] = {"latitude": lat, "longitude": lon}
        resources.append(location)
        for indicator, reading in candidates:
            resource_id = f"{rec['id']}-{reading['reading']}".replace("_", "-")
            resources.append({
                "resourceType": "Observation", "id": resource_id,
                "status": "preliminary",
                "code": {"text": "Reported stream indicator with a potential human or animal contact pathway"},
                "subject": {"reference": f"Location/{location['id']}"},
                "issued": rec["created_at"],
                "valueString": reading["explain"],
                "method": {"text": "Citizen visual report and field answer, with attributed reviewer approval"},
                "note": [
                    {"text": f"PROPOSED MAPPING; record class: {rec['record_class']}. Not validated against a FHIR profile."},
                    {"text": "Potential contact pathway only. No human exposure, toxin measurement, diagnosis or water safety determination was recorded. issued is submission time; observation time was not collected."},
                    {"text": f"Protocol precaution: {reading['one_health']}"},
                    {"text": f"Reviewer decision: {rec['review']['decision']}"},
                ],
            })
            resources.append({
                "resourceType": "Provenance", "id": f"{resource_id}-provenance",
                "target": [{"reference": f"Observation/{resource_id}"}],
                "recorded": generated_at,
                "activity": {"text": "Exported an explicitly approved citizen report as a proposed mapping"},
                "agent": [{"type": {"text": "Reviewer (self-declared identity)"},
                           "who": {"display": rec["review"]["reviewer"]}}],
            })
    return {
        "status": "proposed mapping", "fhir_version": "4.0.1 (R4)",
        "profile": None, "validator": None, "validated": False,
        "scope": "Possible human or animal contact pathways only; no patient or measured exposure is invented.",
        "reason": ("Candidate resources supplied for integration discussion." if candidates else
                   "No protocol reading with a direct contact pathway was recorded; no FHIR Observation is proposed."),
        "resources": resources,
    }


def export_record(rec: dict[str, Any], generated_at: str) -> dict[str, Any]:
    if not summary_eligibility(rec)["eligible"]:
        raise ValueError("Only the report version explicitly approved by a named reviewer can be exported.")
    assessment = assessment_for(rec)
    return {
        "id": rec["id"], "record_class": rec["record_class"],
        "submitted_at": rec["created_at"], "observed_at": None,
        "site": {"key": site_key(rec), "name": rec.get("site_name"),
                 "latitude": rec.get("lat"), "longitude": rec.get("lon")},
        "original_answers": rec["answers"],
        "clarifications": rec["clarifications"],
        "review": rec["review"],
        "summary_eligibility": summary_eligibility(rec),
        "assessment": assessment,
        "photo": {"path": rec.get("photo_path"), "included_in_download": False,
                  "model_findings": rec.get("photo_findings"),
                  "role": "Advisory question raising only; never evidence of safety or a reviewer decision."},
        "provenance": {
            "reviewed_content_sha256": content_fingerprint(rec),
            "original_answers_write_once": True,
            "assessment_basis": "Recomputed at export from the current field protocol and recorded citizen clarifications; not a stored historical assessment.",
            "protocol_source": "backend/domain/field_protocol.py",
            "protocol_version": PROTOCOL_VERSION,
            "assessment_version": "0.4.0",
            "review_history_note": "Earlier saved assessments are preserved in review.history from this release onward; previously overwritten assessments cannot be recovered.",
            "identity_note": "Reviewer names and record classes are self-declared; this prototype has no identity verification.",
            "time_note": "Submission time is recorded. Time of observation was not collected and is not inferred.",
        },
        "proposed_fhir_mapping": proposed_fhir_mapping(rec, assessment, generated_at),
    }


def export_envelope(records: list[dict[str, Any]], generated_at: str) -> dict[str, Any]:
    return {"schema_version": SCHEMA_VERSION, "generated_at": generated_at,
            "format": "RIPARIA provenance JSON", "count": len(records),
            "records": [export_record(rec, generated_at) for rec in records],
            "limitations": LIMITATIONS + [
                "FHIR content is a proposed mapping, not a validated FHIR export. No implementation profile or validator has been applied.",
                "This JSON preserves a handoff trail; FAIR/ODH interoperability and recipient-system acceptance have not been demonstrated.",
            ]}
