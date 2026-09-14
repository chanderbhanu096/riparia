# RIPARIA

**A coordinator screen for low-barrier citizen stream reporting.**

OneAquaHealth IEEE Global Hackathon 2026 — Track 3, AI-Supported Assessment.

---

## The problem

Citizen reports of urban streams are visual and olfactory: a sheen, some foam, green
growth, a smell. These are exactly the observations that are cheap to collect at scale
and hard to act on, because the same appearance can mean very different things. An oily
film is usually harmless iron-oxidising bacteria and occasionally a fuel spill. Foam is
usually decomposing plant matter and occasionally detergent discharge. Green growth may
be filamentous algae, a cyanobacterial bloom, or sewage fungus — three things that look
alike and mean nothing alike.

Because a report cannot be interpreted without resolving that ambiguity, the reports pile
up uninterpreted. The person who could have resolved it in ten seconds — the one standing
at the stream — has already walked away.

## The precedent we are generalising

This problem has been solved once, for a different kind of report.

The **Anglers' Riverfly Monitoring Initiative (ARMI)** runs >2,000 volunteers across
>1,600 UK sites in 35 regional hubs. Volunteers take standardised 3-minute kick-samples
and score pollution-sensitive macroinvertebrate taxa. Each site carries a **trigger
level** set by the regulator. When a score falls below it, the **local coordinator
screens the result first**, and only then is the Environment Agency notified to
investigate. Some investigations have ended in prosecution.

> Brooks, S.J. et al. (2019). *Anglers' Riverfly Monitoring Initiative (ARMI): A UK-wide
> citizen science project for water quality assessment.* Freshwater Science 38(2).
> https://doi.org/10.1086/703397

ARMI works because of two things: a trigger level, and a human screen before escalation.
But it depends on **trained** volunteers doing kick-sampling — high barrier, low volume,
taxonomic. A low-barrier visual reporting app is the opposite: untrained, high volume,
visual. It has neither a trigger level nor a coordinator screen.

**RIPARIA supplies those two pieces for the low-barrier case.**

## What it does

**1. It asks the question a river surveyor would ask, while the person is still there.**

Not a generated prompt — the actual field differential:

| Reported | The differential | Why |
|---|---|---|
| Oily sheen | **Shatter test.** Disturb the film. Iron bacteria biofilm is brittle and shatters into jagged plates that stay apart. Petroleum is cohesive and swirls back into a continuous sheet. | Separates a common harmless phenomenon from a pollution incident |
| Foam | Natural DOC foam is off-white to brown, light, near turbulence. Surfactant foam is bright white, sticky, persistent. | The most-reported and most-misread urban stream feature |
| Green growth | Filamentous algae vs. cyanobacterial scum vs. sewage fungus (*Sphaerotilus natans*) | Three lookalikes, three different meanings, three different responses |

Questions are only asked where a member of the public can safely and reliably answer.
A fish kill gets no question — there is nothing for them to resolve, and the report should
simply go to a person quickly.

**2. It describes the report across four separate dimensions — never one score.**

`completeness` · `detected inconsistency` · `ecological urgency` · `review status`

There is deliberately no combined "confidence" or "trust" number anywhere in this system.
Collapsing these into one figure would invent a truth measure that cannot be validated,
and would let a tidy-looking report outrank an alarming messy one.

**3. It ranks the queue by consequence under uncertainty.**

An unresolved report of something serious ranks **above** a complete report of nothing
much. Uncertainty raises priority on a consequential report rather than lowering it —
because that is precisely where a reviewer's attention changes an outcome. Unresolved
indicators are held at the **worst reading they could plausibly be** until someone
resolves them.

**4. Nothing is validated without a named person.**

No auto-accept and no auto-reject. Reviewer decisions are stored as **attributed
assessments** with the reviewer's name against them, not as ground truth — reviewers
disagree, and that should stay visible.

## The One Health link, made concrete

The clearest environment → animal → human pathway a citizen photo can surface is a
**cyanobacterial bloom**. Blooms produce toxins; dogs have died after drinking at
affected water, and human exposure causes skin and gastrointestinal illness.

So when a citizen's answer resolves green growth to a possible cyanobacterial scum, they
immediately receive a precaution for **themselves, their children and their dog** —
before any reviewer has seen it. The same report that protects the stream protects the
person who filed it.

That is the One Health claim demonstrated as a mechanism, rather than asserted as a theme.

---

## What this system does NOT do

Stated plainly, because a method is only as trustworthy as its declared limits.

- **It does not produce a Water Framework Directive classification.** WFD (2000/60/EC)
  ecological status classes — High / Good / Moderate / Poor / Bad — are derived from
  biological quality elements sampled over time by accredited methods. A single visual
  report from a member of the public is not a WFD classification and is never rendered
  in WFD vocabulary. The urgency levels here are triage categories: *should a person
  look at this, and how soon?*
- **It does not validate observations.** It describes them. Only a named reviewer
  validates anything.
- **The vision model hallucinates, and we can prove it.** The photo pass runs
  `gpt-4.1-mini` on Azure AI Foundry. Given a 96×96 PNG of two flat colour bands —
  green above, brown below, no texture at all — it reported *"a flowing body of water
  surrounded by rocks and vegetation."* Hardening the prompt (report only what is
  literally visible; "cannot tell" is preferred and unpenalised; `temperature=0`;
  enforced JSON) did **not** fix it: the same image still returned *"a narrow
  watercourse with rocks and vegetation on the banks."*

  This is why the model is denied any path to a decision. Its output can only ever
  add a question for the citizen — it cannot set urgency, resolve an indicator, or
  alter an answer. Findings are tri-state (`true`/`null`, never `false`), because
  "I did not see litter" is not evidence that there is none. The constraint is
  structural because we confirmed empirically that a prompt-level one fails.
- **It does not measure water quality.** No pH, no dissolved oxygen, no macroinvertebrate
  identification. Asking untrained people for those yields confident numbers that are
  wrong, which is worse than no data.
- **Its accuracy is not established.** No independent assessment set exists for this
  prototype. The walkthrough in `docs/` is a **scripted walkthrough, not a validated
  study**, and is labelled as such.
- **A generator proves reproducibility, not realism.** Records marked *simulated* are
  generated for demonstration. One genuine capture proves the input path works; it does
  not prove reliability.
- **The FHIR export is a proposed mapping**, not a conformance claim. No profile has been
  validated against a validator. Described as proposed throughout.
- **It has no access to OneAquaHealth data.** The consortium's API requires
  authentication. This prototype is built independently and is not affiliated with the
  OneAquaHealth consortium.

---

## Running it

```bash
cd backend && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env    # optional: Azure AI Foundry creds for the photo pass
.venv/bin/uvicorn main:app --port 8000
```

**The `.env` is optional.** Without it the photo pass reports `unavailable`, the
citizen is told so plainly, the observation is recorded in full and routed to human
review, and every other feature works unchanged. That path was built first and is
exercised on every run, so a model outage is an ordinary state here rather than an
incident.

```bash
cd frontend && npm install && npm run dev
```

API docs at `http://localhost:8000/docs`. Interface at `http://localhost:5173`.

Run the assessment contract self-check:

```bash
cd backend && python3 test_assess.py
```

## Layout

| Path | What it is |
|---|---|
| `backend/field_protocol.py` | **All domain content.** Every indicator, differential and urgency level, each cited to published guidance next to the logic it justifies. Reviewable in isolation by a freshwater ecologist. |
| `backend/assess.py` | The four dimensions. Describes; decides nothing. |
| `backend/store.py` | SQLite. Enforces one rule: original answers are write-once. |
| `backend/vision.py` | Photo pass (Azure AI Foundry, `gpt-4.1-mini`). Structurally forbidden from deciding anything; every failure degrades to the offline path. |
| `backend/main.py` | API. Serves the protocol so the frontend holds no ecological knowledge. |
| `backend/test_assess.py` | 38 contract checks. Several exist because a review caught the first design getting the ecology wrong. |
| `AUDIT.md` | Every decision, its reasoning, and what was rejected. |
| `REVIEW_GPT.md` | Independent adversarial review and what it changed. |

## Sources

- Brooks et al. (2019), *ARMI*, Freshwater Science 38(2). https://doi.org/10.1086/703397
- Angling Trust, *Sewage fungus: a field and microscopic guide* (2024)
- Albini et al. (2023), *Early detection and environmental drivers of sewage fungus
  outbreaks in rivers*, Ecological Solutions and Evidence 4, e12277
- Environment Agency, *Foam in rivers and still waters*
- Minnesota Pollution Control Agency / Michigan EGLE, iron bacteria vs. petroleum guidance
- Directive 2000/60/EC (Water Framework Directive)

*Not affiliated with or endorsed by the OneAquaHealth consortium.*
