"""Reproduce the labelled synthetic handoff fixture, without any database or model."""

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from domain.field_protocol import differential_for
from domain.handoff import export_envelope
from domain.records import content_fingerprint


def example():
    diff = differential_for("green_growth")
    record = {
        "id": "demo00cyano1", "created_at": "2026-09-15T10:00:00+00:00",
        "record_class": "synthetic", "site_name": "Demonstration reach (simulated)",
        "lat": None, "lon": None, "photo_path": None, "photo_findings": None,
        "answers": {"water_clarity": "clear", "flow": "slow",
                    "surrounding_land_use": "park", "indicators": ["green_growth"],
                    "wildlife_seen": "unsure"},
        "clarifications": [{"question_id": diff["id"], "question": diff["question"],
                            "field": "indicators", "indicator": "green_growth",
                            "option_key": "cyanobacteria",
                            "response": diff["options"]["cyanobacteria"]["label"],
                            "citizen_disagrees": False, "at": "2026-09-15T10:01:00+00:00"}],
        "review_status": "reviewer_assessed",
    }
    fingerprint = content_fingerprint(record)
    record["review"] = {
        "reviewer": "DEMO coordinator — scripted role, not an independent expert",
        "decision": "Escalate for a local site visit",
        "note": "Scripted demonstration: the reported paint-like appearance warrants follow-up. No bloom, toxin, exposure or health outcome is confirmed.",
        "at": "2026-09-15T10:04:00+00:00", "approved_for_summary": True,
        "reviewed_content_sha256": fingerprint,
        "history": [{"reviewer": "DEMO coordinator — scripted role",
                     "decision": "Record the proposed follow-up action",
                     "note": "Scripted first assessment; summary approval not yet selected.",
                     "at": "2026-09-15T10:03:00+00:00", "approved_for_summary": False,
                     "reviewed_content_sha256": fingerprint}],
    }
    return export_envelope([record], "2026-09-15T10:05:00+00:00")


if __name__ == "__main__":
    destination = Path(__file__).with_name("approved-synthetic-observation.json")
    destination.write_text(json.dumps(example(), ensure_ascii=False, indent=2) + "\n")
    print(destination)
