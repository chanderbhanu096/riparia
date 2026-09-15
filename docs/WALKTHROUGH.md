# RIPARIA — six-case scripted walkthrough

**Executed:** 2026-09-15 08:09 UTC. **Result:** 6 scenarios passed; 50/50 expected software-behavior checks passed.

**This is not a study.** These are six fixed, invented cases chosen by the development team, executed against the current pure assessment functions. There was no independent assessor, field sampling, human timing experiment or measured environmental/health impact. The pass count is not ecological accuracy.

## Actual before/after output

W1, W3, W4 and W5 compare the same original report before and after a separately supplied citizen clarification. W2 repeats the same report without clarification. W6 compares sparse and complete-context versions of a serious report; it does not edit a saved original. All photo findings are absent. No model, network, database or image is used.

| Case | Potential urgency | Answered core fields | Pending citizen field questions | Precaution notes | Proposed reviewer handling | Result |
|---|---|---|---|---|---|---|
| W1 · Foam → citizen unsure | high → high | 5/5 → 5/5 | 1 → 0 | 0 → 0 | Urgency unchanged: prompt human review remains appropriate; unsure is not reassurance. | PASS |
| W2 · Clear water + sewage odour | high → high | 5/5 → 5/5 | 0 → 0 | 0 → 0 | Unchanged: no invented contradiction or clarifying question; retain prompt review for the reported odour. | PASS |
| W3 · Green growth → citizen unsure | high → high | 5/5 → 5/5 | 1 → 0 | 0 → 0 | Urgency unchanged: the serious possible reading remains open to a reviewer. | PASS |
| W4 · Green growth → paint-like answer | high → high | 5/5 → 5/5 | 1 → 0 | 0 → 1 | Urgency unchanged; added citizen detail triggers the protocol precaution for people and animals. | PASS |
| W5 · Sheen → film shatters and stays apart | high → low | 5/5 → 5/5 | 1 → 0 | 0 → 0 | Changed: lower rule-based priority after a specific citizen answer; still needs a named review, not a water-safety verdict. | PASS |
| W6 · Sparse dead-fish report vs complete context | high → high | 1/5 → 5/5 | 0 → 0 | 0 → 0 | Urgency unchanged: both versions outrank the complete routine comparator; the sparse serious version ranks first. | PASS |

**All before and after states remained `not_reviewed`.** All had zero detected inconsistencies. Each input dictionary remained unchanged after assessment. These checks verify the pure function's behavior; database immutability and the browser flow require their own tests.

### Queue-order evidence

The implementation's internal ordering values were **133.3** for the sparse dead-fish report, **100.0** for its complete-context comparator, and **10.0** for a complete routine report. Thus the incomplete serious report outranked both complete comparators. These values are arbitrary ordering weights, **not confidence, probability, trust or a scientific severity scale**. No reviewer time saving was measured.

### Actual added precaution in W4

> Keep children and dogs out of the water and off the shoreline until this has been assessed, and do not let animals drink. Dogs have died after drinking at affected water.

This is the existing protocol output triggered by the scripted citizen answer. The walkthrough does not verify the appearance, organism, toxins, exposure or effectiveness of this guidance. Scientific content still requires independent domain review.

## What changed, and what did not

- **W1 / W3:** a citizen's unsure answer was supplied as a separate input and interpreted as `undetermined`; high urgency remained. Pending prompts fell from one to zero because the question had been answered. **That is not evidence that ecological uncertainty was resolved.**
- **W2:** clear water plus reported sewage odour generated no contradiction. Its high urgency remained; no clarification was needed by these rules.
- **W4:** the paint-like answer added a specific provisional reading and a precaution. Urgency stayed high because the unresolved growth was already potentially serious.
- **W5:** a specific shatter-test answer lowered the rule-based urgency from high to low. The low label does not establish safe water or remove the need for human review.
- **W6:** missing context increased the serious report's ordering priority while leaving its high urgency unchanged. This is a software ranking demonstration, not an observed change in a reviewer's behavior.

## Limitations and important misses

No requested software expectation failed in this run. That narrow result does not establish that these are the right ecological thresholds, that all important cases are covered, or that a real reviewer would choose the proposed handling above.

The pending-question count clears after an unsure answer, although the reading remains `undetermined`. It measures unanswered app prompts, not remaining scientific questions or real-world follow-ups. The internal priority formula likewise stops counting that indicator as an unanswered differential; high urgency remains, but this walkthrough does not validate within-priority ordering. Model errors, phone usability, reviewer expertise, export importability and operational response are outside this script.

The foam case checks the repaired regression where an explicit unsure answer had reduced high urgency to medium. The present run verifies high → high; it is not a measured before/after experiment on old and new builds.

## Reproduce

From the repository root (Python standard library only):

```bash
python3 scripts/walkthrough.py
python3 scripts/walkthrough.py --write
```

The first command prints the result. The second updates this document only after all checks pass. Fixed cases and expected behaviors are readable in [the script](../scripts/walkthrough.py). `--write` overwrites this generated report, so preserve manual commentary elsewhere.

### Fixed synthetic inputs

These values are invented test inputs, not environmental observations. `wildlife_seen` deliberately contains an explicit synthetic note; having five answered fields does not make a record truthful or scientifically complete.

```json
{
  "record_class": "synthetic_walkthrough_only_not_persisted",
  "cases": [
    {
      "id": "W1",
      "name": "Foam → citizen unsure",
      "original": {
        "water_clarity": "clear",
        "flow": "moderate",
        "surrounding_land_use": "park",
        "indicators": [
          "foam"
        ],
        "wildlife_seen": "Synthetic scenario; no independently observed wildlife."
      },
      "after_differentials": {
        "foam": "unsure"
      }
    },
    {
      "id": "W2",
      "name": "Clear water + sewage odour",
      "original": {
        "water_clarity": "clear",
        "flow": "moderate",
        "surrounding_land_use": "park",
        "indicators": [
          "smell_sewage"
        ],
        "wildlife_seen": "Synthetic scenario; no independently observed wildlife."
      },
      "after_differentials": {}
    },
    {
      "id": "W3",
      "name": "Green growth → citizen unsure",
      "original": {
        "water_clarity": "clear",
        "flow": "moderate",
        "surrounding_land_use": "park",
        "indicators": [
          "green_growth"
        ],
        "wildlife_seen": "Synthetic scenario; no independently observed wildlife."
      },
      "after_differentials": {
        "green_growth": "unsure"
      }
    },
    {
      "id": "W4",
      "name": "Green growth → paint-like answer",
      "original": {
        "water_clarity": "clear",
        "flow": "moderate",
        "surrounding_land_use": "park",
        "indicators": [
          "green_growth"
        ],
        "wildlife_seen": "Synthetic scenario; no independently observed wildlife."
      },
      "after_differentials": {
        "green_growth": "cyanobacteria"
      }
    },
    {
      "id": "W5",
      "name": "Sheen → film shatters and stays apart",
      "original": {
        "water_clarity": "clear",
        "flow": "moderate",
        "surrounding_land_use": "park",
        "indicators": [
          "oily_sheen"
        ],
        "wildlife_seen": "Synthetic scenario; no independently observed wildlife."
      },
      "after_differentials": {
        "oily_sheen": "shatters"
      }
    },
    {
      "id": "W6",
      "name": "Sparse dead-fish report vs complete context",
      "original": {
        "indicators": [
          "dead_fish"
        ]
      },
      "comparison_answers": {
        "water_clarity": "clear",
        "flow": "moderate",
        "surrounding_land_use": "park",
        "indicators": [
          "dead_fish"
        ],
        "wildlife_seen": "Synthetic scenario; no independently observed wildlife."
      },
      "after_differentials": {}
    }
  ],
  "complete_routine_comparator": {
    "water_clarity": "clear",
    "flow": "moderate",
    "surrounding_land_use": "park",
    "indicators": [],
    "wildlife_seen": "Synthetic scenario; no independently observed wildlife."
  },
  "photo_findings": null
}
```

### Source fingerprints for this run

SHA-256 identifies the exact local code used; it does not prove a deployment or a clean Git commit.

| File | SHA-256 |
|---|---|
| `backend/domain/assess.py` | `1c125476a2e61cb43194ab4e203d0c47411c9f5562e72c2794cf2eb34cc8ce53` |
| `backend/domain/field_protocol.py` | `b571141fdd3e8bcc402ca97d9388a24a8db6f1e9cc190b4ab8cfa7e3bc854b0d` |
| `scripts/walkthrough.py` | `8cdc0167a95dfbb19a908d8b4ced49514d4e9fcae8806f92899d061936df1498` |
