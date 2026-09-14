# REVIEW_GPT.md — Independent strategy review by Codex / GPT

| | |
|---|---|
| **Reviewer** | Codex (GPT), via `duet` skill, adversarial strategy review |
| **Run ID** | `20260914-215657-dbebe6` |
| **Date** | 2026-09-14 |
| **Subject** | `AUDIT.md` §0–§5, decisions D-001…D-009 |
| **Verdict** | **REVISE** — keep Track 3 provisionally, cut one component, fix the validation model |
| **Raw report** | `.duet/runs/20260914-215657-dbebe6/REPORT.md` |

> A prior run (`20260914-215306-6baadf`) was executed with roles inverted and returned a
> placeholder finding. It is **discarded**; it carries no weight. Recorded here only so the
> run directory is not mistaken for a second opinion.

---

## Reviewer's one-paragraph verdict (verbatim)

> "Track 3 is a defensible choice, but AUDIT.md overstates its evidence and underestimates
> validation and delivery risk. Keep Track 3 provisionally, cut component 4's
> calibration/learning product, and demonstrate a narrow improvement in expert triage.
> Track 7 deserves a serious comparison based on a concrete interoperability workflow;
> presumed low competition alone is not a winning argument."

---

## Q1 — Track choice (D-002)

**Reviewer position:** *"I agree with D-002's recommendation more than its reasoning."*

Findings against our reasoning:

| Our claim | Reviewer's objection | Our verdict |
|---|---|---|
| "401 ⇒ no participant can get useful data" | A 401 proves *those endpoints* need auth. It does not prove no open, organiser-provided, or participant-collected data exists. Lack of consortium access is a reason to avoid **historical-analysis dependence**, not to dismiss Track 2 categorically. | **ACCEPTED** → D-010 |
| "Track 2 is the most crowded track" | Unverified. No entry counts were obtained. Crowding was asserted, not measured. | **ACCEPTED** → D-010 |
| "We built the trust layer that makes the dashboards usable" | This pitch **implicitly disparages the hosts' own working systems** (Resilience Map, City Dashboards, GEOSSIP). The judges built those. | **ACCEPTED — this is the sharpest catch in the review** → D-012 |
| D-003 "reversal costs under one day" | Overpromises. Changing a headline in a day cannot supply missing evidence of useful insight. | **ACCEPTED** → D-010 |

**Reviewer's decision rule, adopted:**
> *"Choose the track with the strongest demonstrable outcome and credible delivery, not the
> most elaborate architecture or guessed entrant density."*

## Q1b — Track 7 (FHIR) stress test

**Reviewer explicitly disagrees with D-002's dismissal of Track 7.**

- "UX is judged *for intended users*" — an integration analyst importing a record, seeing
  actionable validation errors, and getting a provenance-preserving result **can have
  excellent UX**. Our "FHIR demos badly" argument was wrong on the rubric's own terms.
- But: "least crowded" is unverified, and offers **no advantage at all if prizes are ranked
  across all tracks** rather than per track. Our scarcity argument was weak.
- Warning on D-007: *"a generic FAIR/ODH-aligned envelope is not evidence of
  interoperability, and selecting human-exposure fields alone does not establish FHIR
  conformance. State the chosen version, profile and validator, or limit the claim to a
  proposed mapping."*

**Our verdict:** stay on Track 3 (reviewer concurs: *"Otherwise keep Track 3"*). **Reject**
the proposed half-day Track 7 bake-off — too expensive at 15 days. **Accept** the conformance
guardrail in full → D-014.

---

## Q2 — Scope

**Reviewer: yes, overscoped. Cut component 4.**

> *"Cut exactly component 4: 'Closed learning loop + honest calibration.' Retain expert
> corrections as ordinary provenance within component 3, but remove the calibration
> dashboard and learning claims. A handful of staged expert labels cannot establish
> calibration, and this component adds statistical obligations as well as UI work."*

**Highest-Impact component:** component **3, expert triage** — *"it connects better reporting
to scarce expert attention and a subsequent action. Its value must be demonstrated, not
assumed."*

**Calendar error caught:** §2 ran to D16 = **Sept 30**, contradicting the stated "submit by
Sept 29" buffer policy. Reviewer supplied real dates: freeze features **Sept 25**, harden
**Sept 26–27**, record/document **Sept 28–29**, submit **Sept 29**.

**Sequencing error caught:** the clarification flow *is* the ethical core, yet it was
scheduled D7–D8 — *"leaving the ethical core until D7–D8 risks spending the first week on
peripheral checks."*

**Our verdict:** all **ACCEPTED** → D-011, D-013.

---

## Q3 — Blind spots

**Reviewer disagrees with D-001's framing-is-half-the-grade premise:**
> *"A video communicates evidence but does not substitute for it."*

**On novelty:** *"Clarification prompts and human review are established patterns."* The
genuinely distinctive contribution would be narrower and more defensible:
**selecting a useful question under uncertainty, preserving the citizen's account, and
showing that it changes reviewer handling.**

**On memorability, concrete and adopted:**
> *"Use one memorable case: apparently ordinary water, a reported unusual odour, AI
> uncertainty, a neutral follow-up, and expert escalation with visible reasons. Repeat that
> same observation across the demo rather than touring five screens."*

**On synthetic data (D-006):** labelling **helps** versus concealment — but *"a generator
proves reproducibility, not realism"* and *"one genuine capture proves the input path works,
not reliability."* Three record classes must be kept visibly separate: synthetic walkthrough
records · authentic observations · independently reviewed evaluation cases.

**Our verdict:** **ACCEPTED** → D-012, D-015.

---

## Q4 — Risk (the most important section of this review)

**Reviewer: R2's mitigation is insufficient, and it contradicts our own design.**

> *"R2 promises 'Never auto-reject' and human judgment, but D-004 component 3 says
> unambiguous observations 'auto-accept.' … A human answering a leading question is not
> meaningful oversight."*

**Four concrete domain errors in our Confidence Engine — all correct, all accepted:**

1. **"Clear water can smell of sewage; this is not an internal contradiction."**
   Our flagship contradiction rule was **ecologically wrong**. Dissolved sewage produces
   odour without turbidity. A panel of freshwater ecologists would have caught this on
   sight.
2. **"Turbidity after dry weather can be a valuable anomaly."** Our rainfall-plausibility
   check would have **down-weighted exactly the most interesting signal** — turbidity with
   no rain suggests a discharge event, which is the thing worth reporting.
3. **"Local rainfall alone cannot establish plausibility across a catchment."** Upstream
   rain hours away drives downstream turbidity; a point weather lookup is not a catchment.
4. **"Missing EXIF is missing evidence, not evidence against a citizen."** Most phones strip
   EXIF GPS by default. Our check would have penalised privacy-conscious and
   default-configured users.

**Structural fix demanded — collapse-to-one-score is the root error:**
> *"Separate record completeness, detected inconsistencies, ecological urgency and review
> status; do not collapse them into an unvalidated truth score."*

**Worse unlisted risk identified:**
> *"Confident scientific error that contaminates observations or deprioritises a real
> incident."*

Additional requirements: preserve original answers verbatim · permit "unsure" · permit the
citizen to disagree with the model · ask **neutral** questions, not leading ones · require
**explicit reviewer approval** before anything is called "validated" · rank uncertain reports
with potentially serious consequences **visibly higher**, not lower · record expert judgments
as *attributed assessments*, not ground truth · **demonstrate one report the model questions
incorrectly**, and show it stays available for review · human-health summaries must describe
*an observation and an appropriate review action*, never infer exposure safety from a photo.

**Our verdict:** **ACCEPTED IN FULL** → D-012 (the largest single revision in this project).

---

## Q5 — Additions (cheap Impact wins)

| # | Addition | Cost | Our verdict |
|---|---|---|---|
| A1 | Small **disclosed** comparison: same fixed cases reviewed with and without clarification+triage. Report unresolved fields, follow-ups needed, serious cases surfaced, **and any important misses**. If no independent assessor: call it a *scripted walkthrough*, not a validated study. | ~0.5–1 day | **ACCEPTED** → D-015 |
| A2 | One **observation-to-action diagram**: citizen report → expert review → possible local investigation → benefit for stream ecology, animals, people. Name the reviewer role. Label the pathway **proposed**, not agreed. | 2–4 h | **ACCEPTED** → D-016 |
| A3 | One **annotated export example**: original answer + clarification + reviewer decision + provenance, making the handoff tangible. | 2–3 h | **ACCEPTED** → D-016 |
| A4 | Visible **model-unavailable state** that preserves the observation and routes it to human review; any demo replay must be labelled. | 2 h | **ACCEPTED** → D-013 |

> Reviewer's framing, adopted: *"These are evaluation and presentation improvements within
> the current scope, not new product components. They strengthen Impact more credibly than
> another model integration."*

---

## Reviewer's stated verification limits

Read-only document inspection. No code existed to review. The reviewer did **not**
independently verify event rules, eligibility, prize allocation, track participation, or
API/data availability — it relied on our `AUDIT.md`. Eligibility (§5 Q1) and team capacity
(§5 Q2) remain unresolved external dependencies.

---

## Net effect on the plan

- Track 3 **held**, but its justification is rebuilt on demonstrable outcome rather than on
  unverified crowding claims. → D-010
- Component 4 (calibration) **cut**. → D-011
- Confidence Engine **redesigned** from one truth score into four separate, honestly-named
  dimensions; three ecologically wrong rules removed. → D-012
- Schedule **re-dated** against the real calendar; ethical core moved to the front. → D-013
- FHIR claim **bounded** to a named profile + validator, or downgraded to "proposed mapping". → D-014
- Three cheap Impact artefacts **added**. → D-015, D-016
