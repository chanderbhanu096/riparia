#!/usr/bin/env python3
"""Reproduce six disclosed, synthetic assessment scenarios; no service or model.

Run from any directory:
    python3 scripts/walkthrough.py
    python3 scripts/walkthrough.py --write

The second form writes docs/WALKTHROUGH.md only after all scenario checks pass.
This is a scripted walkthrough of software behavior, not an ecological study.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from domain.assess import assess  # noqa: E402


COMPLETE = {
    "water_clarity": "clear",
    "flow": "moderate",
    "surrounding_land_use": "park",
    "indicators": [],
    "wildlife_seen": "Synthetic scenario; no independently observed wildlife.",
}


def observation(*indicators: str) -> dict:
    return {**copy.deepcopy(COMPLETE), "indicators": list(indicators)}


CASES = [
    {
        "id": "W1", "name": "Foam → citizen unsure",
        "original": observation("foam"), "after_differentials": {"foam": "unsure"},
        "levels": ("high", "high"), "readings": ("unresolved", "undetermined"),
        "indicator": "foam", "question_counts": (1, 0),
        "handling": "Urgency unchanged: prompt human review remains appropriate; unsure is not reassurance.",
    },
    {
        "id": "W2", "name": "Clear water + sewage odour",
        "original": observation("smell_sewage"), "after_differentials": {},
        "levels": ("high", "high"), "question_counts": (0, 0),
        "handling": "Unchanged: no invented contradiction or clarifying question; retain prompt review for the reported odour.",
    },
    {
        "id": "W3", "name": "Green growth → citizen unsure",
        "original": observation("green_growth"),
        "after_differentials": {"green_growth": "unsure"},
        "levels": ("high", "high"), "readings": ("unresolved", "undetermined"),
        "indicator": "green_growth", "question_counts": (1, 0),
        "handling": "Urgency unchanged: the serious possible reading remains open to a reviewer.",
    },
    {
        "id": "W4", "name": "Green growth → paint-like answer",
        "original": observation("green_growth"),
        "after_differentials": {"green_growth": "cyanobacteria"},
        "levels": ("high", "high"), "readings": ("unresolved", "cyanobacterial_scum"),
        "indicator": "green_growth", "question_counts": (1, 0),
        "handling": "Urgency unchanged; added citizen detail triggers the protocol precaution for people and animals.",
    },
    {
        "id": "W5", "name": "Sheen → film shatters and stays apart",
        "original": observation("oily_sheen"),
        "after_differentials": {"oily_sheen": "shatters"},
        "levels": ("high", "low"), "readings": ("unresolved", "iron_bacteria"),
        "indicator": "oily_sheen", "question_counts": (1, 0),
        "handling": "Changed: lower rule-based priority after a specific citizen answer; still needs a named review, not a water-safety verdict.",
    },
    {
        "id": "W6", "name": "Sparse dead-fish report vs complete context",
        "original": {"indicators": ["dead_fish"]},
        "comparison_answers": observation("dead_fish"), "after_differentials": {},
        "levels": ("high", "high"), "question_counts": (0, 0),
        "handling": "Urgency unchanged: both versions outrank the complete routine comparator; the sparse serious version ranks first.",
    },
]


def run() -> tuple[list[dict], dict]:
    """Compare fixed expected behaviors with actual pure-function output."""
    results = []
    routine = assess(observation(), photo_findings=None)
    for case in CASES:
        before_answers = copy.deepcopy(case["original"])
        before_snapshot = copy.deepcopy(before_answers)
        after_answers = copy.deepcopy(case.get("comparison_answers", before_answers))
        after_snapshot = copy.deepcopy(after_answers)
        differentials = copy.deepcopy(case["after_differentials"])
        differential_snapshot = copy.deepcopy(differentials)
        before = assess(before_answers, photo_findings=None)
        after = assess(after_answers, photo_findings=None, differentials=differentials)

        checks = {
            "original input unchanged": before_answers == before_snapshot,
            "comparison input unchanged": after_answers == after_snapshot,
            "clarification input unchanged": differentials == differential_snapshot,
            "expected urgency before and after": (
                before["ecological_urgency"]["level"], after["ecological_urgency"]["level"]
            ) == case["levels"],
            "expected pending field-question counts": (
                len(before["field_differentials"]), len(after["field_differentials"])
            ) == case["question_counts"],
            "no automatic reviewer decision": before["review_status"] == after["review_status"] == "not_reviewed",
            "no photo-based or invented inconsistency": before["detected_inconsistency"] == after["detected_inconsistency"] == [],
        }
        if "indicator" in case:
            checks["expected interpretation before and after"] = tuple(
                a["ecological_urgency"]["resolved"][case["indicator"]]["reading"]
                for a in (before, after)
            ) == case["readings"]
        if case["id"] == "W4":
            notes = after["ecological_urgency"]["one_health_notes"]
            checks["citizen answer adds precaution"] = (
                before["ecological_urgency"]["one_health_notes"] == []
                and len(notes) == 1 and "dogs" in notes[0] and "children" in notes[0]
            )
        if case["id"] == "W5":
            checks["informed answer lowers queue priority"] = after["triage"]["score"] < before["triage"]["score"]
        if case["id"] == "W6":
            checks["sparse serious outranks complete serious and complete routine"] = (
                before["triage"]["score"] > after["triage"]["score"] > routine["triage"]["score"]
            )
            checks["completeness changes but urgency does not"] = (
                before["completeness"]["answered"] == 1
                and after["completeness"]["answered"] == 5
                and routine["completeness"]["answered"] == 5
            )
        results.append({"case": case, "before": before, "after": after, "checks": checks})
    return results, routine


def metric_pair(result: dict, fn) -> str:
    return f"{fn(result['before'])} → {fn(result['after'])}"


def render(results: list[dict], routine: dict) -> str:
    total = sum(len(r["checks"]) for r in results)
    passed = sum(sum(r["checks"].values()) for r in results)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# RIPARIA — six-case scripted walkthrough", "",
        f"**Executed:** {now}. **Result:** {len(results)} scenarios passed; {passed}/{total} expected software-behavior checks passed.", "",
        "**This is not a study.** These are six fixed, invented cases chosen by the development team, executed against the current pure assessment functions. There was no independent assessor, field sampling, human timing experiment or measured environmental/health impact. The pass count is not ecological accuracy.", "",
        "## Actual before/after output", "",
        "W1, W3, W4 and W5 compare the same original report before and after a separately supplied citizen clarification. W2 repeats the same report without clarification. W6 compares sparse and complete-context versions of a serious report; it does not edit a saved original. All photo findings are absent. No model, network, database or image is used.", "",
        "| Case | Potential urgency | Answered core fields | Pending citizen field questions | Precaution notes | Proposed reviewer handling | Result |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in results:
        pairs = [
            metric_pair(r, lambda a: a["ecological_urgency"]["level"]),
            metric_pair(r, lambda a: f"{a['completeness']['answered']}/{a['completeness']['total']}"),
            metric_pair(r, lambda a: len(a["field_differentials"])),
            metric_pair(r, lambda a: len(a["ecological_urgency"]["one_health_notes"])),
        ]
        verdict = "PASS" if all(r["checks"].values()) else "FAIL"
        lines.append(f"| {r['case']['id']} · {r['case']['name']} | {' | '.join(pairs)} | {r['case']['handling']} | {verdict} |")
    sparse = results[5]
    cyano = results[3]["after"]["ecological_urgency"]["one_health_notes"][0]
    lines.extend([
        "", "**All before and after states remained `not_reviewed`.** All had zero detected inconsistencies. Each input dictionary remained unchanged after assessment. These checks verify the pure function's behavior; database immutability and the browser flow require their own tests.", "",
        "### Queue-order evidence", "",
        f"The implementation's internal ordering values were **{sparse['before']['triage']['score']}** for the sparse dead-fish report, **{sparse['after']['triage']['score']}** for its complete-context comparator, and **{routine['triage']['score']}** for a complete routine report. Thus the incomplete serious report outranked both complete comparators. These values are arbitrary ordering weights, **not confidence, probability, trust or a scientific severity scale**. No reviewer time saving was measured.", "",
        "### Actual added precaution in W4", "",
        f"> {cyano}", "",
        "This is the existing protocol output triggered by the scripted citizen answer. The walkthrough does not verify the appearance, organism, toxins, exposure or effectiveness of this guidance. Scientific content still requires independent domain review.", "",
        "## What changed, and what did not", "",
        "- **W1 / W3:** a citizen's unsure answer was supplied as a separate input and interpreted as `undetermined`; high urgency remained. Pending prompts fell from one to zero because the question had been answered. **That is not evidence that ecological uncertainty was resolved.**",
        "- **W2:** clear water plus reported sewage odour generated no contradiction. Its high urgency remained; no clarification was needed by these rules.",
        "- **W4:** the paint-like answer added a specific provisional reading and a precaution. Urgency stayed high because the unresolved growth was already potentially serious.",
        "- **W5:** a specific shatter-test answer lowered the rule-based urgency from high to low. The low label does not establish safe water or remove the need for human review.",
        "- **W6:** missing context increased the serious report's ordering priority while leaving its high urgency unchanged. This is a software ranking demonstration, not an observed change in a reviewer's behavior.", "",
        "## Limitations and important misses", "",
        "No requested software expectation failed in this run. That narrow result does not establish that these are the right ecological thresholds, that all important cases are covered, or that a real reviewer would choose the proposed handling above.", "",
        "The pending-question count clears after an unsure answer, although the reading remains `undetermined`. It measures unanswered app prompts, not remaining scientific questions or real-world follow-ups. The internal priority formula likewise stops counting that indicator as an unanswered differential; high urgency remains, but this walkthrough does not validate within-priority ordering. Model errors, phone usability, reviewer expertise, export importability and operational response are outside this script.", "",
        "The foam case checks the repaired regression where an explicit unsure answer had reduced high urgency to medium. The present run verifies high → high; it is not a measured before/after experiment on old and new builds.", "",
        "## Reproduce", "",
        "From the repository root (Python standard library only):", "",
        "```bash", "python3 scripts/walkthrough.py", "python3 scripts/walkthrough.py --write", "```", "",
        "The first command prints the result. The second updates this document only after all checks pass. Fixed cases and expected behaviors are readable in [the script](../scripts/walkthrough.py). `--write` overwrites this generated report, so preserve manual commentary elsewhere.", "",
        "### Fixed synthetic inputs", "",
        "These values are invented test inputs, not environmental observations. `wildlife_seen` deliberately contains an explicit synthetic note; having five answered fields does not make a record truthful or scientifically complete.", "",
        "```json", json.dumps({
            "record_class": "synthetic_walkthrough_only_not_persisted",
            "cases": [{k: v for k, v in r["case"].items() if k in ("id", "name", "original", "comparison_answers", "after_differentials")} for r in results],
            "complete_routine_comparator": observation(), "photo_findings": None,
        }, indent=2, ensure_ascii=False), "```", "",
        "### Source fingerprints for this run", "",
        "SHA-256 identifies the exact local code used; it does not prove a deployment or a clean Git commit.", "",
        "| File | SHA-256 |", "|---|---|",
    ])
    for relative in ("backend/domain/assess.py", "backend/domain/field_protocol.py", "scripts/walkthrough.py"):
        lines.append(f"| `{relative}` | `{hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()}` |")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write docs/WALKTHROUGH.md after all checks pass")
    args = parser.parse_args()
    results, routine = run()
    failures = [f"{r['case']['id']}: {name}" for r in results for name, ok in r["checks"].items() if not ok]
    for r in results:
        print(f"{'PASS' if all(r['checks'].values()) else 'FAIL'} {r['case']['id']} {r['case']['name']}: "
              f"{r['before']['ecological_urgency']['level']} -> {r['after']['ecological_urgency']['level']}")
    if failures:
        print("Failed expectations:\n" + "\n".join(failures), file=sys.stderr)
        return 1
    count = sum(len(r["checks"]) for r in results)
    print(f"6 scenarios; {count}/{count} software-behavior checks passed. Not a study or accuracy estimate.")
    if args.write:
        output = ROOT / "docs" / "WALKTHROUGH.md"
        output.write_text(render(results, routine))
        print(f"Wrote {output.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
