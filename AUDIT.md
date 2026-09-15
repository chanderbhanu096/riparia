# AUDIT.md — OneAquaHealth IEEE Global Hackathon 2026

> **This is the single source of truth for this project.**
> Any agent or human joining this work reads this file FIRST and reads nothing else
> until they have read it end to end.
>
> **Arriving with no context — including in another tool such as Codex? Read
> [§00 START HERE](#00-start-here--full-briefing-for-anyone-opening-this-cold)
> first.** It is a complete standing briefing: the goal, every link, what exists,
> how to run and deploy it, the rules that must not be broken, what is left, and
> what has already been tried and rejected. It assumes no memory of any conversation.
>
> **Update protocol:** never delete an entry. Decisions are append-only. If a decision
> is reversed, add a NEW decision that supersedes it and set the old one's
> `Status: SUPERSEDED by D-0XX`. Append to §8 Changelog on every edit.

| | |
|---|---|
| **Created** | 2026-09-14 21:55 CEST |
| **Owner** | chanderbhanu096 |
| **Authoring agent** | Claude Code (Opus 5) |
| **Review agent** | Codex / GPT (via `duet` skill) — see §7 |
| **Status** | **P1–P4 implemented. Full-width field-station redesign (D-031), explicit-approval site summary + export (D-032), demo/submission drafts and six-case walkthrough (D-033). Live at https://riparia-oah.azurewebsites.net; new shell and existing records verified (D-034). Next: record video, physical-phone and independent ecology checks.** |

---

## 00. START HERE — full briefing for anyone opening this cold

> **You are reading the single source of truth for this project.** This section is a
> complete standing briefing: if you are a person or an agent (Claude, Codex, anything
> else) arriving with no memory of the conversation that produced this work, everything
> you need to act competently is below. Read §00 fully, then §0.2 (the rubric), then
> §1b (D-010 onward). Do not propose anything before that.

### 00.1 What this is, in one paragraph

**RIPARIA** is a hackathon entry for the **OneAquaHealth IEEE Global Hackathon 2026**,
submitted under **Track 3 — AI-Supported Assessment**. It is a web app for people who
notice something wrong with an urban stream. The citizen reports what they can see; when
they report something *ambiguous* — an oily sheen, foam, green growth — the app asks
**one real field question** with **drawn options** (for example the shatter test, which
separates harmless iron-oxidising bacteria from a petroleum spill), and the citizen's own
answer resolves it on the spot. A **named human reviewer** then decides. The AI never
scores the stream, never accepts, never rejects. It asks; a person answers; a person decides.

### 00.2 Every link

| What | Where |
|---|---|
| **Hackathon page (Devpost)** | https://oneaquahealth-ieee-hackathon.devpost.com/ |
| Hackathon rules | https://oneaquahealth-ieee-hackathon.devpost.com/rules |
| Hackathon page on the host project's site | https://www.oneaquahealth.eu/oneaquahealth-ieee-global-hackathon/ |
| **The host project (OneAquaHealth)** | https://www.oneaquahealth.eu/ |
| Host project on CORDIS (EU Horizon, ID 101086521) | https://cordis.europa.eu/project/id/101086521 |
| Their citizen-science project | https://www.oneaquahealth.eu/citizen-science-project/ |
| Their Resilience Map (already-shipped tool) | https://apps.oneaquahealth.eu/resmap/ |
| Their backing API (**401 — we have no access**) | `https://api.enora-oah.eu` |
| **Our public repository** | https://github.com/chanderbhanu096/riparia |
| **Our live application** | https://riparia-oah.azurewebsites.net |
| Our API docs (auto-generated) | https://riparia-oah.azurewebsites.net/docs |
| Our design canvas (3 directions) | https://claude.ai/artifact/Gg5A9vHAgoTA2GZWvZftzd |

### 00.3 Where this stands right now (2026-09-15)

| | |
|---|---|
| **Submission deadline** | **2026-09-30, 21:00 PDT** — target submission **2026-09-29**, a day early |
| Days left at last update | ~15 calendar days |
| Builder | **Solo student.** Not a team. Plan against one person's partial attention |
| Phases done | P0 lock · P1 ethical spine · P2 vision pass · P3 reviewer surfaces · P4 summary/export · full-width field-station redesign |
| **Phase remaining** | Harden on a physical phone · record demo video · finalise and submit the written draft |
| Deliverables status | Public repo ✅ · working prototype ✅ · **demo video: script ready, recording not started** · project description + track alignment statement: local drafts ready |
| Tests | 39 assessment checks · 12 isolated HTTP handoff tests (`backend/test_handoff.py`) · six scripted cases / 50 behavior checks (`scripts/walkthrough.py`) |

### 00.4 The product thesis, and why it is shaped this way

The problem is **not** that citizen stream data is under-visualised. It is that it is
**under-trusted**, because the things people report look alike: filamentous algae,
a cyanobacterial bloom and sewage fungus are three very different things that all read
as "green slimy stuff". Getting it wrong in either direction means a missed pollution
incident or a false alarm.

Two ideas carry the whole entry:

1. **Draw the specimens, do not describe them.** In 1843 Anna Atkins published
   *Photographs of British Algae: Cyanotype Impressions*, the first book ever illustrated
   with photographs, explicitly as a visual companion to Harvey's unillustrated manual —
   **because written descriptions of algae were not enough to identify them by.** Same
   problem, same answer, 183 years later.
2. **We are not inventing human-in-the-loop; we are extending a proven one.** The UK
   **Riverfly / ARMI** scheme (>2,000 volunteers, >1,600 sites) works because it has a
   regulator-set *trigger level* and a *local coordinator who screens results before
   escalation*. But it needs trained volunteers doing kick-sampling. A low-barrier
   visual app has neither piece. **RIPARIA supplies both for the low-barrier case.**

### 00.5 The codebase, file by file

```
backend/
  main.py              composition root only: app, middleware, routers, static
  config.py            all settings in one place (env wins over .env)
  domain/              WHAT AN OBSERVATION MEANS. Pure: no I/O, no framework.
    field_protocol.py    ← ALL ecological content, each item cited to published
                           method. A freshwater ecologist can review the entire
                           domain by reading this ONE file. Start here.
    assess.py            the four dimensions (see 00.7)
  adapters/            the only code touching the outside world
    store.py             SQLite. Enforces: original answers are WRITE-ONCE.
    vision/              model providers behind one interface
      azure_openai.py      Azure AI Foundry, gpt-4.1-mini
      null.py              offline provider; always available
  api/                 HTTP shape only, one module per resource
  test_assess.py       39 assessment checks — the guard against risk R8
  test_handoff.py      isolated HTTP checks for approval, provenance and storage
  domain/records.py    report fingerprint and current approval eligibility
  domain/handoff.py    site evidence + proposed FHIR R4 mapping
  api/sites.py         summaries and downloadable provenance JSON
frontend/src/
  App.jsx  Capture.jsx  Review.jsx  Sites.jsx    shell + report/review/summary
  Specimens.jsx                          diagnostic specimens + indicator marks
  RiverScene.jsx                         decorative landscape, not diagnostic
  index.css                              design tokens + type scale
design/                the design-direction artboards and their generator
```

**Adding an ecological indicator is one dict entry in `field_protocol.py`.** The frontend
picks it up automatically via `/api/protocol` and needs no change.

### 00.6 Running and deploying it

```bash
# backend
cd backend && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn main:app --port 8000          # .env is OPTIONAL (see 00.7)

# frontend
cd frontend && npm install && npm run dev -- --port 5180

# the one runnable check
cd backend && python3 test_assess.py
```

**Deploy** (see `docs/DEPLOYMENT.md` for data preservation and release verification; Azure App Service `riparia-oah`, resource group `signwise-rg`, on the owner's
existing B1 plan): build the frontend, stage `backend/*.py` + `domain/ adapters/ api/` +
`frontend/dist` as `static/`, zip, `az webapp deploy`. Credentials are **Azure App
Settings**, never in the repo (`.env` is gitignored, `.env.example` is committed).

> **Two deploy traps, both already paid for:**
> 1. `az webapp deploy` has exited **0 while reporting a failed instance**, and has
>    reported failure while the app was in fact healthy. **Verify against the running
>    app, never against the deploy command.** The reliable probe is the bundle hash in
>    the served `index.html`, not `/api/health`.
> 2. A cold start takes ~2 minutes. The site serves the **old** build during it.

### 00.7 Rules that must not be broken

These are the product's spine. Everything else is negotiable; these are not.

1. **No auto-accept and no auto-reject.** Nothing is "validated" without a named reviewer.
2. **There is no single confidence or trust score.** Four separate, separately-labelled
   dimensions: *completeness*, *detected inconsistency*, *ecological urgency*,
   *review status*. Merging them re-invents the unvalidated truth measure we removed.
3. **Urgency is never lowered by uncertainty.** An unclear report of something serious
   ranks **above** a tidy report of nothing much.
4. **The citizen's original answers are immutable** and always shown beside any clarification.
5. **The model may only raise a question.** It cannot set urgency, resolve an indicator,
   or alter a record. *(Our own vision model was caught inventing "rocks and vegetation"
   in a picture of two coloured rectangles, and prompt-hardening did not fix it — see D-023.)*
6. **Colour means diagnosis.** Red `#b02d18` is the citizen safety precaution and
   nothing else — not urgency, not errors. Ochre `#8a5214` is ecological urgency.
7. **The app must work with no model at all.** `VISION_PROVIDER=null`, or simply no
   `.env`. The degraded path was built first and is exercised daily.
8. **Never claim more than we can show.** The drawings are schematic aids, not
   identification plates. The FHIR export is a *proposed mapping*. Urgency is triage,
   **not** a Water Framework Directive classification.

### 00.8 What is left

1. **P4 implemented** — explicit reviewer approval, site summary, provenance JSON and proposed FHIR R4 mapping. See `docs/EXPORT.md` and D-032.
2. **Harden** — real-phone pass, outdoor legibility, keyboard and VoiceOver (all currently unverified).
3. **A2/A3 complete as local artefacts** — `docs/OBSERVATION_TO_ACTION.md` and `docs/EXPORT.md` plus reproducible synthetic JSON.
4. **A1 executed** — six invented cases, 50 software-behavior checks; `docs/WALKTHROUGH.md`. Not a study or independent validation.
5. **Demo video** — 4:25 script in `docs/DEMO_SCRIPT.md`; recording remains. Description and Track 3 statement drafted in `docs/SUBMISSION_DRAFT.md`; nothing submitted.

### 00.9 Reading order, and where answers live

| Question | File |
|---|---|
| What is this and why is it shaped this way? | **this section**, then §0 |
| Why was every decision made? | §1 and §1b of this file, D-001 … D-034 |
| What does the ecology mean? | `backend/domain/field_protocol.py` — every claim cited |
| What did an independent reviewer say? | `REVIEW_GPT.md`, `DESIGN_VERDICT_GPT.md`, `UX_REVIEW_GPT.md` |
| What does the product claim publicly? | `README.md`, including its **limitations** section |

**Decisions are append-only.** Never edit a past entry; add a new one that supersedes it
and mark the old `Status: SUPERSEDED by D-0XX`. §1b amends §1 — reading §1 alone will
rebuild mistakes that have already been caught and paid for.

### 00.10 Already tried and rejected — do not re-propose

| Idea | Why it is dead |
|---|---|
| Track 2 (dashboards) | The consortium's data is behind a 401, and they already ship Resilience Map, City Dashboards and GEOSSIP. D-002, D-010 |
| A single "confidence score" | Invents an unvalidated truth measure. D-012 |
| "Clear water + sewage odour = contradiction" | **Ecologically wrong** — dissolved sewage makes odour without turbidity. D-012 |
| "Turbidity without rain = implausible" | **Backwards** — that pattern suggests a discharge event, the most report-worthy case. D-012 |
| Penalising missing EXIF GPS | Most phones strip it. Missing evidence is not evidence against a person. D-012 |
| A calibration/learning dashboard | A handful of staged labels cannot establish calibration. D-011 |
| The Cyanotype design direction | Monochrome by process, so it cannot show the colour that identifies the growth. D-027 |
| Gradients, glassmorphism, accent-bar cards | The current house style of AI-built sites; undoes the editorial direction. D-029 |
| Queue search / sorting / pre-send summary | Explicitly ranked as non-blockers with the time left. D-030 |

---

## 0. Hard context (verified facts, with sources)

All facts below were fetched and verified on **2026-09-14**. Do not re-derive; re-verify
only if a date-sensitive item is near expiry.

### 0.1 The competition

| Item | Value | Source |
|---|---|---|
| Event | OneAquaHealth IEEE Global Hackathon 2026 | devpost |
| Submission deadline | **2026-09-30, 21:00 PDT** (= 2026-10-01 06:00 CEST) | devpost rules |
| **Time remaining at authoring** | **~15.5 days** | computed |
| Registered participants | 728 | devpost |
| Team rule | Individuals or teams; one team per participant | devpost rules |
| Prizes | $1,500 / $1,000 / $500 + 2×$250 special mention | devpost |
| Non-cash | Certificates of Merit ×3, IEEE Senior Member elevation ×5 | devpost |

### 0.2 Judging rubric — THE most important table in this file

| Criterion | Weight | What it actually rewards |
|---|---|---|
| Impact & Alignment with OneAquaHealth mission | **30%** | Improves monitoring/protection of water ecosystems AND the human–animal–environment health link |
| Innovation & Creativity | **20%** | Originality; creative use of technology |
| Technical Implementation / Architecture | **20%** | Prototype quality, architecture, functionality, effective use of tools + APIs |
| Usability & UX | **15%** | Ease of use, clarity, accessibility for intended users |
| Feasibility & Scalability | **15%** | Real-world implementation potential, integration with existing systems |

Scored 1–10 per criterion.

**Read the weights as a build instruction:** 30% of the score is *narrative alignment*,
not code. 50% (Impact + Innovation) is decided before a judge runs anything. The demo
video and the framing are therefore not "marketing" — they are half the grade.

### 0.3 Required deliverables

1. Track alignment statement
2. Project description — problem, solution, impact
3. **Demo video, 3–5 minutes**
4. **Public code repository** with source + documentation
5. Working prototype / mockup / proof-of-concept

### 0.4 The 7 tracks (verbatim framing)

| # | Track | Stated problem | Stated solution direction |
|---|---|---|---|
| 1 | Citizen Science UX | Complex tools, confusing terminology, low participation | Guided workflows, simplified ecological terms, better data accuracy |
| 2 | Data-to-Insight | Stream data is hard to interpret, patterns unclear | Dashboards, maps, trend analysis, One Health insight summaries |
| 3 | AI-Supported Assessment | Citizen observations are inconsistent and error-prone | AI prompts, validation checks, explainable AI, human-in-the-loop |
| 4 | Awareness & Storytelling | Low awareness, no engaging formats | Educational modules, storytelling, personalised insights |
| 5 | Community & Gamification | Low repeat engagement | Gamification, challenges, social features |
| 6 | Resilience Informatics | No predictive environmental tools | Predictive dashboards, alerts, resilience tools |
| 7 | Digital Health Standards | Fragmented data, no standards | FHIR models, AI agents, integration frameworks |

### 0.5 The host project (what "alignment" means)

- **OneAquaHealth** = EU Horizon project (CORDIS ID 101086521), protecting **urban** freshwater
  ecosystems to advance **One Health**.
- Core thesis: *freshwater ecosystem health and human health/wellbeing in cities are
  interconnected; improving one improves the other.*
- Pilot cities: **Coimbra (PT), Ghent (BE), Toulouse (FR), Oslo (NO), Benevento (IT)**.
- Three digital tools already exist: **Environmental Surveillance System**, **Decision &
  Support System (DSS)**, **CitizenScience App**.
- Already-shipped public tools: **Resilience Map** (`apps.oneaquahealth.eu/resmap/`),
  **City Dashboards**, **GEOSSIP**, **Catalogue of Measures**, **DipteraCAST**.
- The consortium ran participant training on **One Digital Health (ODH) + FAIR principles**
  and **HL7 FHIR** (Session 4, 2026-08-27). They care about standards.
- CitizenScience App collects: water clarity, flow, odour, surrounding land use, visible
  impacts (litter, erosion, invasive plants), wildlife presence, pollution signs, plus
  upstream/downstream photos or short video, via a guided structured scoring flow.

### 0.6 Data availability — VERIFIED, and it changes everything

| Probe | Result |
|---|---|
| `apps.oneaquahealth.eu/resmap/` | React SPA (Vite + MUI + Leaflet + Redux). No embedded data. |
| Backing API `https://api.enora-oah.eu` | **HTTP 401 on `/`, `/docs`, `/openapi.json`, `/api`, `/v1`, `/health`** |
| Downloadable datasets on devpost | **None listed** |

**Conclusion: the consortium's real stream data is NOT obtainable by participants.**
Every team is in the same position. Any project whose value depends on a corpus of real
historical observations cannot be built truthfully in this hackathon.
This is the pivotal constraint driving D-002.

---

## 1. Decision log

### D-001 — Treat the rubric weights as the objective function
> ⚠️ **AMENDED by D-017** — valid as a time-allocation rule, retracted as a scoring theory.
- **Date:** 2026-09-14
- **Status:** ACTIVE
- **Decision:** Optimise explicitly for `0.30·Impact + 0.20·Innovation + 0.20·Technical + 0.15·UX + 0.15·Scalability`, not for "coolest build".
- **Rationale:** Impact+Innovation = 50% and are both won by *problem selection and framing*, which is a decision made now and cheaply, versus Technical = 20% which costs the entire 15 days. Choosing the right problem is the highest-leverage action available.
- **Consequence:** Time budget is skewed to concept, narrative and demo video far more than a typical hackathon team would.

---

### D-002 — Primary track: **Track 3 (AI-Supported Assessment)**, NOT Track 2
> ⚠️ **AMENDED by D-010** — conclusion holds, three of its arguments are retracted. Read D-010 with it.
- **Date:** 2026-09-14
- **Status:** ACTIVE — *pending owner confirmation, owner initially preferred Track 2*
- **Decision:** Submit under **Track 3 — AI-Supported Assessment**. Deliberately absorb the visible payoff of Track 2 and the standards angle of Track 7 inside the Track 3 build.
- **Owner's stated preference was Track 2.** Owner then delegated the call: *"your task is to find the one which helps us win."* This decision exercises that delegation. Reversal path is documented in D-003.

**Evidence and reasoning:**

1. **Track 2 is data-starved (§0.6).** Its stated deliverable is "dashboards, maps, trend analysis" over *citizen-collected data* we cannot obtain. A dashboard over invented data is a dashboard over invented data, and the judges are the people who own the real data. Track 3's unit of work is a **single observation being submitted right now** — we can create that live, on camera, during the demo. **Track 3 is data-independent; Track 2 is data-dependent on data that is behind a 401.**

2. **Track 2 competes head-on with the consortium's own shipped products.** Resilience Map, City Dashboards and GEOSSIP already do maps + indicators + time comparison, built by the project's own engineers with real data and years of domain input. A 15-day student dashboard is graded against that mental benchmark. Impact (30%) collapses when the judge's honest reaction is *"we have this."*

3. **Track 2 is the default hackathon output — maximum competition density.** With 728 registrants, "we built a dashboard" is the single most probable submission. Innovation (20%) is scored comparatively. Track 3 is harder and will be far less crowded; the ones that do attempt it will mostly ship "we asked GPT to score the photo," which is precisely what the track brief warns against ("*without replacing human judgment*").

4. **Track 3 attacks the bottleneck that makes Track 2 impossible.** Citizen data is not under-visualised; it is **under-trusted**. Until inconsistent, error-prone observations can be trusted, nothing downstream — not the DSS, not the surveillance system, not a dashboard — may consume them. This yields the strongest available one-line pitch:
   > *"We didn't build another dashboard. We built the trust layer that makes the dashboards usable."*

5. **Track 3 is the consortium's own thesis.** Their flagship claim is an **AI-based Environmental Surveillance System** with human oversight. A submission about responsible, explainable, human-in-the-loop AI for stream assessment is aligned with the host project's actual research agenda, not merely its topic. This is where the 30% lives.

6. **Technical ceiling is higher (20%).** Multimodal photo checks + a deterministic contradiction engine + calibration tracking is a materially stronger architecture story than charting a CSV.

7. **Feasibility/Scalability (15%) is naturally strong.** The output is a *module that drops into their existing CitizenScience App*, not a replacement product. "Integration with existing systems" is literally the criterion wording.

**Alternatives considered and rejected:**

| Track | Verdict | Why rejected |
|---|---|---|
| 1 — Citizen Science UX | Reject | Highest competition density. Ceiling on Technical (20%) is low — it is a redesign. Judges see dozens. |
| 2 — Data-to-Insight | **Reject as primary, absorb as feature** | Data-starved (§0.6); competes with consortium's own shipped dashboards; most crowded technical track. Its best part (the One Health insight summary) is kept inside D-004. |
| 4 — Awareness & Storytelling | Reject | Technical (20%) ceiling is very low; hard to score above mid on architecture. |
| 5 — Community & Gamification | Reject | Reads as shallow to a scientific panel; Impact (30%) is weak — points/badges do not improve ecosystem monitoring. |
| 6 — Resilience Informatics | Reject | Strongest *impact* alternative, but prediction requires historical time series that §0.6 proves we cannot get. Forecasts from synthetic data are indefensible under questioning. |
| 7 — Digital Health Standards | **Reject as primary, absorb as feature** | Lowest competition density and genuinely high alignment (their own FHIR/FAIR session). But pure interoperability plumbing demos badly in 3–5 min and scores poorly on UX (15%). Absorbed as the export layer in D-006. |

---

### D-003 — Reversal path if the owner overrides back to Track 2
> ⚠️ **AMENDED by D-010** — no longer "under one day". Possible, at real cost.
- **Date:** 2026-09-14
- **Status:** ACTIVE (contingency, not executed)
- **Decision:** If the owner elects Track 2 after reading D-002, the build does **not** restart. The same system is submitted with the framing inverted: the Confidence Engine becomes the *data-quality backbone*, and the Insight view (D-004, item 5) is promoted to the headline. Estimated rework: **under one day**, confined to the narrative, README and demo script.
- **Rationale:** Architecture is deliberately chosen (D-005) so that track choice is a *framing* decision, not an engineering one. This de-risks the disagreement entirely.

---

### D-004 — The concept: a human-in-the-loop trust layer for citizen stream assessments
> ⚠️ **AMENDED by D-011 (component 4 CUT) and D-012 (components 2 & 3 REDESIGNED).** Do not build from this section alone — three of its rules are ecologically wrong and are deleted in D-012.
- **Date:** 2026-09-14
- **Status:** ACTIVE
- **Working name:** `RIPARIA` — *Reliable Insight Pipeline for Aquatic Reporting, Interpretation & Assessment*. (Name is provisional; `riparian` = the streambank zone, so it reads as domain-native rather than generic.)

**Product thesis, one sentence:**
> AI should not score the stream. AI should make the *citizen's* score trustworthy enough
> for scientists to use — and show its working every time.

**Five components, in the order a real observation flows through them:**

1. **Guided capture with AI clarification prompts** *(covers the track's "AI prompts")*
   The citizen submits photo + draft answers. The model does **not** answer for them. It
   asks *targeted clarifying questions* about what it sees:
   *"There's foam near the left bank — is it thick and white, or thin and dispersing?"*
   Ambiguity is resolved at source, by the human, while they are still standing at the stream.
   **This is the ethical core and must never be softened into auto-scoring.**

2. **The Confidence Engine** *(covers "validation checks" + "explainable AI")*
   A **hybrid** of a deterministic rule set and a multimodal model. Every check emits a
   human-readable reason. Checks include:
   - *Subject check:* does the photo actually depict a stream/watercourse?
   - *Internal contradiction:* "water crystal clear" + "strong sewage odour" → flag.
   - *Geo check:* photo EXIF GPS vs. claimed site location.
   - *Environmental plausibility:* high turbidity claim vs. recent local rainfall
     (Open-Meteo, free, keyless) — turbidity after 3 dry weeks is worth a human look.
   - *Temporal/lighting sanity:* timestamp vs. visible daylight conditions.
   Output: a **confidence score with a full evidence trail**. Never a silent auto-reject.
   The rule half is explainable *by construction* — not "explainable" because a model was
   asked to justify itself after the fact.

3. **Expert triage queue** *(covers "human-in-the-loop")*
   Ranks pending observations by **value of expert attention**, not by arrival time.
   Unambiguous ones auto-accept; genuinely ambiguous ones surface first. This is the
   scalability argument: expert time is the scarce resource in citizen science, and the
   system spends it where it changes an outcome.

4. **Closed learning loop + honest calibration**
   Every expert correction is recorded as ground truth. A calibration view shows whether
   the confidence score is *actually* predictive of expert agreement, including where it
   is wrong. **Showing a failure mode on stage is a credibility multiplier with a
   scientific panel.**

5. **One Health insight summary + export** *(absorbs Track 2 and Track 7)*
   A compact site view — validated observations only, with confidence bands visible —
   translating stream condition into the human-health framing the project cares about.
   Export carries provenance, confidence, and the full check trail in a FAIR/ODH-aligned
   envelope (see D-006).

---

### D-005 — Technical architecture (chosen for shipping in 15 days, not for a CV)
- **Date:** 2026-09-14
- **Status:** ACTIVE

| Layer | Choice | Why this and not the obvious alternative |
|---|---|---|
| Client | **PWA** (React + Vite), camera via `getUserMedia` | No app store, no native build, installs on the judge's phone from a URL. A native app costs days and buys nothing here. |
| Styling | Tailwind | Fast, and accessibility defaults are easy to keep. |
| Map | **Leaflet** | The consortium's own Resilience Map uses Leaflet — same ecosystem, reads as native to them. |
| API | **FastAPI** (Python) | Auto-generated OpenAPI docs directly serve the "effective use of tools and APIs" wording in the Technical criterion. |
| Storage | **SQLite** | Zero ops. A hackathon prototype does not need Postgres; `ponytail: single-file DB, swap to Postgres only if concurrent writers ever matter.` |
| Vision + clarifying questions | **Claude (multimodal, structured output)** | Strong image reasoning; structured output keeps responses machine-checkable. |
| Contradiction checks | **Plain Python predicate list** | Deterministic, auditable, testable, and genuinely explainable. A rules DSL would be over-engineering. |
| Weather cross-check | **Open-Meteo** | Free, keyless, historical + forecast. No signup friction during judging. |
| Deploy | One free-tier host, single URL | The judge must reach it in one click. |

**Explicit non-goals** (each one is a deliberate saving, not an oversight):
user accounts/OAuth (demo role toggle instead) · Docker/Kubernetes · microservices ·
custom-trained CV model (zero training data exists — see §0.6) · mobile-native build ·
real-time websockets · i18n beyond English.

---

### D-006 — Synthetic seed data will be labelled as synthetic, always
> ⚠️ **EXTENDED by D-015** — three record classes must stay visibly separate.
- **Date:** 2026-09-14
- **Status:** ACTIVE
- **Decision:** Since real data is unobtainable (§0.6), seed the demo with generated observations produced by a **documented, committed generator script**. Every synthetic record is visibly flagged in the UI and in the repo. Never imply it is real project data.
- **Rationale:** A scientific judging panel will punish undisclosed fake data far harder than it will punish honest simulation. Committing the generator converts a weakness into a methodology artefact. It also makes the repo reproducible, which serves FAIR.
- **Corollary:** The live demo must include **one genuinely real observation** captured on camera during the video, so the pipeline is visibly not staged.

---

### D-007 — Standards-aligned export (absorbs Track 7 without owning its costs)
> ⚠️ **BOUNDED by D-014** — name the FHIR version/profile/validator and pass it, or say "proposed mapping".
- **Date:** 2026-09-14
- **Status:** ACTIVE
- **Decision:** Ship a single export endpoint producing a FAIR/ODH-aligned record per validated observation, carrying provenance + confidence + check trail. Provide a FHIR `Observation` mapping **only** for the fields that genuinely touch human health exposure.
- **Rationale:** The consortium ran their own FHIR/FAIR training — this speaks their language and lifts the 30% Impact criterion and the 15% Scalability criterion at low cost. Guardrail: do **not** FHIR-ify ecological fields just to claim the buzzword; a panel that trained the session will notice, and misuse of a clinical standard scores *negative*.

---

### D-008 — Demo video is a first-class deliverable, not an afterthought
> ⚠️ **AMENDED by D-013 (real dates) and D-015 (single-case script).**
- **Date:** 2026-09-14
- **Status:** ACTIVE
- **Decision:** Reserve the final ~2 days for the video and README. Script it before recording. Structure: problem (30s) → the position, *"AI shouldn't replace the citizen"* (20s) → one observation end-to-end, live (2m) → expert queue + calibration incl. a real failure (1m) → export + integration path (30s).
- **Rationale:** 50% of the rubric (Impact + Innovation) is transmitted through the video. Most teams record it in the last hour and lose those points. This is the cheapest available scoring advantage.

---

### D-009 — Working directory has a trailing space
- **Date:** 2026-09-14
- **Status:** ACTIVE — hazard noted, not fixed
- **Detail:** The project path ends in a space: `.../OneAquaHealth IEEE Global Hackathon `. This breaks unquoted shell paths and some tooling.
- **Action:** quote every path. Renaming is the owner's call; flagged, not done unilaterally.

---

## 1b. Decision log — post-review revisions (2026-09-14, after Codex/GPT review)

> Decisions D-010…D-016 were produced by folding in the independent Codex/GPT review.
> Full review: [`REVIEW_GPT.md`](REVIEW_GPT.md). These **amend** D-002…D-008; the originals
> remain above unedited, per the append-only protocol.

### D-010 — Track 3 held, but its justification is rebuilt
- **Date:** 2026-09-14 · **Status:** ACTIVE · **Amends:** D-002, D-003
- **Decision:** Stay on **Track 3**. Retract three arguments used to justify it, because they were asserted rather than demonstrated:
  1. ~~"401 ⇒ no participant can obtain useful data."~~ → A 401 proves *those endpoints* require auth. It does **not** prove no open, organiser-provided, or participant-collected data exists. The defensible claim is narrower: **avoid any design that depends on a historical archive we cannot obtain.**
  2. ~~"Track 2 is the most crowded track."~~ → Never measured. Entry counts are not public. **Crowding is no longer an argument in this project.** Corollary: the same retraction applies to the "Track 7 is least crowded" claim — and if prizes are ranked across all tracks rather than per track, track density carries no weight at all.
  3. ~~"D-003 reversal costs under one day."~~ → A one-day reframe cannot manufacture evidence of useful insight. If Track 2 is chosen, it needs its own demonstrable outcome, not a relabel. D-003 is downgraded from "cheap" to **"possible, at real cost."**
- **Replacement decision rule (adopted from the reviewer):** *choose the track with the strongest **demonstrable outcome** and credible delivery — not the most elaborate architecture, and not guessed entrant density.* Track 3 still wins under this rule, because its unit of work (one observation, right now) can be demonstrated live without any archive.

### D-011 — Cut component 4 (calibration / learning loop)
- **Date:** 2026-09-14 · **Status:** ACTIVE · **Amends:** D-004
- **Decision:** **Delete** D-004 component 4 ("Closed learning loop + honest calibration"). Expert corrections are retained, but only as **ordinary provenance on the record** inside component 3. No calibration dashboard. No learning claims.
- **Rationale:** A handful of staged expert labels cannot establish calibration. Claiming it invites a statistics question we cannot answer, from a panel qualified to ask it. It also cost UI work we do not have days for. **Build count drops 5 → 4.**
- **Retained instead:** a small fixed evaluation set (see D-015), which is honest about being a walkthrough rather than a study.

### D-012 — Confidence Engine redesign: four dimensions, not one truth score
- **Date:** 2026-09-14 · **Status:** ACTIVE · **Amends:** D-004 component 2 & 3, R2
- **This is the largest and most important revision in the project.**

**Root error found by review:** collapsing everything into a single "confidence score" invents an unvalidated truth measure. Replaced with **four separately-named, separately-displayed dimensions**:

| Dimension | What it means | What it must never do |
|---|---|---|
| **Completeness** | Which fields are present/absent | Imply the citizen was wrong |
| **Detected inconsistency** | Specific named tensions between answers | Be called "error" or "contradiction" without a reviewer confirming |
| **Ecological urgency** | Could this matter, if true? | Be lowered because the record is uncertain |
| **Review status** | Not reviewed / in review / reviewer-assessed | Say "validated" before a human approves |

**Three rules deleted as ecologically wrong:**
1. ❌ *"clear water + sewage odour = contradiction."* **Wrong.** Dissolved sewage produces odour without turbidity. This was our flagship example and it was a domain error.
2. ❌ *"turbidity without recent rain = implausible."* **Backwards.** Turbidity with no rain suggests a **discharge event** — the single most report-worthy case. The rule would have buried the best signal. Also, point rainfall ≠ catchment rainfall; upstream rain hours away drives downstream turbidity.
3. ❌ *"missing EXIF GPS = weaker record."* **Unfair.** Most phones strip EXIF by default; this penalised privacy-conscious and default-configured users. Missing evidence is **missing evidence**, never evidence against a person.

**Mandatory behaviours (these are not optimisations — they are the ethical contract):**
- **No auto-accept and no auto-reject.** The earlier "unambiguous records auto-accept" directly contradicted R2's own promise. Removed.
- Preserve the citizen's **original answers verbatim**, always, alongside any clarification.
- Offer **"unsure"** as a first-class answer, and let the citizen **disagree with the model** on the record.
- Questions must be **neutral**, never leading. *A human answering a leading question is not oversight.*
- Nothing is labelled "validated" without **explicit reviewer approval**.
- Triage ranks by **consequence under uncertainty** — an uncertain report of something serious goes **up** the queue, not down.
- Expert judgments are stored as **attributed assessments**, not ground truth.
- **Show a failure on camera:** one plausible report the model questions *incorrectly*, still visible and still reviewable.
- Human-health output describes **an observation and an appropriate review action**. It never infers exposure safety from a photo.
- **New top risk (R8):** confident scientific error that contaminates the record or deprioritises a real incident.

### D-013 — Re-dated schedule, ethical core moved first
- **Date:** 2026-09-14 · **Status:** ACTIVE · **Amends:** D-008 and §2
- **Calendar error caught:** the original §2 ran to "D16" = **Sept 30**, contradicting its own "submit Sept 29" buffer policy. All phases now carry **real dates** (§2 rewritten).
- **Sequencing error caught:** the clarification flow *is* the ethical core, yet it sat at D7–D8 — risking a first week spent on peripheral checks. **Moved to the front.** The end-to-end capture→clarify→review path is built first; individual checks are added to a working spine afterwards.
- **Added (A4):** a visible **model-unavailable state** that preserves the observation and routes it to human review. The live capture in the demo cannot rely on cached responses; any replay shown must be labelled as replay.

### D-014 — FHIR claim bounded
- **Date:** 2026-09-14 · **Status:** ACTIVE · **Amends:** D-007
- **Decision:** Either state the **exact FHIR version, profile, and validator** used and pass it, or downgrade the wording to **"proposed mapping"** everywhere. No middle ground.
- **Rationale:** *"A generic FAIR/ODH-aligned envelope is not evidence of interoperability, and selecting human-exposure fields alone does not establish FHIR conformance."* The panel ran their own FHIR session; an unvalidated conformance claim scores **negative**.
- **Rejected from the review:** a bounded half-day Track 7 bake-off. Correct in principle, unaffordable at 15 days. The reviewer's own conclusion was *"Otherwise keep Track 3."*

### D-015 — One memorable case + an honest walkthrough evaluation
- **Date:** 2026-09-14 · **Status:** ACTIVE · **Amends:** D-006, D-008
- **The demo follows ONE observation, repeated, not a tour of five screens:** apparently ordinary water → a reported unusual odour → model uncertainty → a **neutral** follow-up question → expert escalation with visible reasons. Show the original report beside the clarified one, and the **changed review action**. That contrast is the product.
- **Evaluation (A1):** review a small fixed case set with and without clarification+triage. Report unresolved fields, follow-ups needed, serious cases surfaced, **and any important misses**. With no independent assessor, it is called a **scripted walkthrough — never a validated study.**
- **Three record classes stay visibly separate:** synthetic walkthrough records · authentic observations · evaluation cases. *A generator proves reproducibility, not realism; one genuine capture proves the input path works, not reliability.*
- **Novelty claim narrowed** to what is actually defensible: clarification prompts and human review are established patterns. Ours is: **selecting a useful question under uncertainty, preserving the citizen's account, and showing it changes reviewer handling.**

### D-016 — Two cheap Impact artefacts
- **Date:** 2026-09-14 · **Status:** ACTIVE · **Adds to:** §4
- **A2 — observation-to-action diagram (2–4 h):** citizen report → expert review → possible local investigation → benefit for stream ecology, animals, people. Names the intended reviewer role. Labelled **proposed**, not an agreed partnership. This is the cheapest available purchase of the 30% Impact criterion: it makes the One Health chain concrete instead of asserted.
- **A3 — one annotated export example (2–3 h):** original answer + clarification + reviewer decision + provenance, side by side, making the handoff tangible.
- **Guardrail:** never claim improved ecosystem or human-health *outcomes* from a prototype demo. Claim a **pathway**, demonstrated at the first link.

### D-017 — D-001 tempered: framing carries evidence, it does not replace it
- **Date:** 2026-09-14 · **Status:** ACTIVE · **Amends:** D-001
- **Decision:** D-001 stands as a *time-allocation* rule (the video and framing are first-class and get real days). It is **retracted as a scoring theory.** The reviewer is right: *"a video communicates evidence but does not substitute for it."* Impact and Innovation are scored on what the panel can see working. The video's job is to make a real demonstrated outcome **legible fast**, not to substitute for one.

### D-018 — Eligibility resolved; solo build confirmed
- **Date:** 2026-09-14 · **Status:** ACTIVE · **Closes:** Q1, Q2
- **Q1 (students-only?)** — Owner is a student, so the ambiguity between the Devpost overview ("Students only") and the rules page (silent) is **moot**. No organiser contact needed. Risk R5 **closed**.
- **Q2 (team size?)** — **Solo.** One builder, no contributors.
- **Consequence:** capacity is now a hard known quantity, which triggers D-019.

### D-019 — Solo re-scope: cut to a demonstrable core
- **Date:** 2026-09-14 · **Status:** ACTIVE · **Amends:** D-013, D-014, §2
- **Reasoning:** the reviewer warned *"plan against solo capacity until named contributors are committed"* (F8). That condition is now confirmed, not hypothetical. One student, ~15 calendar days, with 2 of them locked for video + submission. The honest build window is **~12 days of one person's partial attention** — not 15 days of a team's.
- **Governing rule for the rest of this project:** **a smaller thing that visibly works beats a larger thing that half-works.** A judge scoring 100+ entries spends minutes on ours; a broken fifth feature costs more than a missing one.

**Cuts made now, deliberately, while there is still time to benefit from them:**

| Cut | Was | Now | Saved |
|---|---|---|---|
| **FHIR validation** | Name version + profile + validator and pass it (D-014 option A) | **Option B taken up front: "proposed mapping", documented in the README with the exact fields and the reason it is not validated.** | ~1.5 days |
| **A1 walkthrough evaluation** | 0.5–1 day comparison | **Hard-timeboxed to 3 hours**, 6–8 fixed cases, results table in the README. Still labelled a scripted walkthrough, never a study. | ~0.5 day |
| **Map view** | Leaflet site map | **Deferred to "if P5 finishes early".** The insight summary does not need a map to make its point, and the hosts already have the best map in this domain. | ~1 day |
| **Live weather integration** | Open-Meteo catchment plausibility | **Cut entirely.** D-012 already deleted the rule it was built to serve — point rainfall cannot establish catchment plausibility. Keeping the integration with no defensible rule behind it is decoration. | ~0.5 day |

- **Net:** ~3.5 days recovered and folded into buffer and polish on the core four components.
- **Explicitly NOT cut** (and no future laziness rule may cut them): the human-in-the-loop contract (D-012), data-honesty labelling (D-006/D-015), accessibility (UX = 15%), the demo video's 2 days (D-008), and A2/A3 — the two cheapest Impact purchases we have (D-016).

### D-020 — Stack: React PWA + FastAPI + SQLite, one repo, no build exotica
- **Date:** 2026-09-14 · **Status:** ACTIVE · **Confirms:** D-005 under solo constraints
- **Verified toolchain:** Python 3.14.6 · Node 22.23.2 · npm 10.9.8 · git 2.51.0. No `uv` (use `venv` + `pip`).
- **React kept, after re-testing it against the laziness ladder.** The app carries genuinely stateful UI — a multi-step capture wizard, a live camera stream, pending clarification answers, a reviewer queue with ordering. Hand-rolled vanilla state sync across those views produces *more* code and more bugs by the third view, not less. React is the shortest path that is also correct here.
- **Tailwind kept** — fastest route to consistent, legible, accessible-by-default UI for someone with no design time.
- **Cut from the stack:** Docker · Postgres · auth/OAuth (a demo role toggle instead) · websockets · i18n · any custom-trained model (zero training data exists, §0.6).

### D-021 — Expert-grade standard: every domain choice must trace to published method
- **Date:** 2026-09-14 · **Status:** ACTIVE · **Governs:** all subsequent work
- **Owner instruction, verbatim:** *"all decision should be made from an expert it should look like that its build by an expert not just some newbie who built it using ai"*
- **Standard adopted:** no invented ecological category, threshold, or question. Every indicator, every clarifying question, and every urgency level must trace to a **named, published protocol or peer-reviewed source**, cited in the code next to the logic it justifies.
- **Audit finding that triggered this:** the first-pass field list (`water_clarity`, `odour`, `visible_impacts` …) was *plausible but invented*. It read like a reasonable guess at a protocol rather than an implementation of one. A freshwater scientist reviewing the repo would have spotted that in under a minute — and that is precisely the "built by a newbie with AI" signal the owner is warning against.
- **The tells this standard exists to eliminate:**
  - Invented categories dressed as domain knowledge.
  - Buzzword density in place of precision.
  - Uncalibrated claims ("revolutionary", "AI-powered") where an expert writes "indicative" and "proposed".
  - No stated limitations. **Experts publish what their method cannot do**; that section is now mandatory in the README.
  - Conflating distinct regulatory concepts (see D-022's WFD guardrail).
- **Applies to prose too:** README, demo script and Devpost copy are written in sober technical register. No emoji headers, no feature-tour marketing.

### D-022 — Field-protocol grounding: differential diagnostics, not generic prompts
- **Date:** 2026-09-14 · **Status:** ACTIVE · **Implements:** D-021 · **Amends:** D-004 component 1, D-012
- **This is the single largest quality upgrade in the project so far.** It converts the clarifying-question feature from "an LLM asks something plausible" into **field-protocol differential diagnostics delivered at the streambank**.

**Precedent adopted — ARMI / Riverfly Monitoring Initiative (UK).** >2,000 volunteers, >1,600 sites, 35 regional hubs. Volunteers take standardised 3-minute kick-samples and score pollution-sensitive taxa. Each site carries a **"trigger level"** set by the regulator; when a score falls below it, the **local coordinator screens the result first**, and only then is the Environment Agency notified to investigate. Investigations have produced prosecutions.
> **Why this matters to us:** we are **not inventing** a human-in-the-loop model for freshwater citizen science. ARMI has a deployed, proven one. But ARMI's model depends on *trained* volunteers doing *kick-sampling* — high barrier, low volume, taxonomic. OneAquaHealth's app is the opposite: low-barrier, high-volume, untrained, visual and olfactory. **It has no trigger-level equivalent and no coordinator screen.** RIPARIA supplies exactly those two missing pieces for the low-barrier case.
> *Brooks et al. (2019), "Anglers' Riverfly Monitoring Initiative (ARMI)", Freshwater Science 38(2).*

**Three real field diagnostics now drive the clarifying questions** (each verified against published guidance, each cited in `field_protocol.py`):

| Reported | The differential a trained surveyor actually runs | Why it matters |
|---|---|---|
| **Oily sheen** | **Shatter test.** Disturb the film with a stick. Iron-oxidising bacterial biofilm is brittle and **shatters into jagged plates that do not rejoin**. Petroleum is cohesive and **swirls back into a continuous sheet**. | Separates a harmless, naturally common phenomenon from a pollution incident. Gets this wrong in either direction and you either cry wolf or miss a spill. |
| **Foam** | Natural foam from decomposing plant matter (DOC acting as a surfactant) is **off-white to brown, light, not sticky**, and typically forms at turbulence. Synthetic surfactant foam is **bright white, sticky, and persistent**. | Foam is the single most-reported and most-misread urban stream feature. |
| **Algae / green growth** | Distinguish **filamentous green algae** (nuisance) from **cyanobacterial scum** (blue-green, paint-like surface film) and from **sewage fungus** (*Sphaerotilus natans*) — a grey-white filamentous biofilm that is a classic bioindicator of organic loading from sewage or industrial effluent. | Three visually similar things with completely different meanings and completely different urgency. |

**Cyanobacteria carries the One Health link, made concrete.** A cyanobacterial bloom is a direct **human–animal–environment** exposure pathway: dogs have died after drinking at affected water, and human exposure causes skin and gastrointestinal illness. This is the one place where a citizen's photo genuinely connects stream condition to human and animal health — so it is the anchor for the One Health summary (D-004 component 5), replacing the previous generic framing.
> **This turns the project's 30% Impact claim from an assertion into a demonstrated mechanism.**

**Guardrail — do NOT conflate with WFD classification.** The EU Water Framework Directive (2000/60/EC) five ecological status classes (High / Good / Moderate / Poor / Bad) are derived from biological quality elements sampled over time by accredited methods. **A single visual citizen report is not a WFD classification and must never be rendered in WFD vocabulary.** Our urgency levels are explicitly *triage* categories — "should a person look at this soon?" — not status classes. Stating this limitation plainly is itself the expert signal; blurring it is the newbie tell.

### D-023 — Azure AI Foundry adopted; and our own vision model caught hallucinating
- **Date:** 2026-09-14 · **Status:** ACTIVE · **Implements:** D-004 component 2, A4
- **Decision:** use the owner's existing **Azure AI Foundry / AI Services** resource (`signwise-ai`, Sweden Central) with its deployed **`gpt-4.1-mini`** (vision-capable) for the photo pass. No new key, no new cloud resource, no new subscription.
- **Ladder check:** the resource already existed and already had a multimodal deployment. Creating a dedicated resource would have bought isolation we do not need for a 15-day prototype. Reuse wins.
- **Cost/latency measured on a real call:** 87 total tokens, ~0.9 s to first token, ~1.6 s total. Negligible per observation.
- **Caveat recorded:** the deployment (`sol_signWise`) is shared with an unrelated project of the owner's. Acceptable for a prototype; a production deployment would want its own.

**THE IMPORTANT FINDING — our own model hallucinated on the first call.**

The test image was a **96×96 PNG of two flat colour bands**: green on top, brown below. No rocks. No vegetation. No water. No texture of any kind. Asked whether it showed a watercourse, `gpt-4.1-mini` answered:

> *"The image shows a flowing body of water surrounded by rocks and vegetation, which qualifies as a watercourse."*

Confident, fluent, specific, and **entirely invented**.

- **Why this matters more than it looks:** this is first-hand, reproducible evidence for **R8 — confident scientific error** — produced by the exact model we were about to trust, on the exact task we were about to trust it with. Every argument in D-012 for keeping the model out of the assertion path just stopped being theoretical.
- **Consequence for the design — the vision pass is now strictly question-raising, never fact-asserting:**
  1. Vision output **may only add a question for the citizen.** It can never set urgency, resolve an indicator, alter a record, or contribute to any decision.
  2. Findings are **tri-state** (`true` / `null`), never `false`. "I did not see litter" is not evidence there is none, and must never be recorded as if it were.
  3. The model is asked **only narrow, low-inference questions** ("is there a watercourse in frame", "is there visible debris"), never ecological interpretation. It is explicitly instructed to prefer "cannot tell".
  4. `temperature=0`, structured JSON, short output.
  5. Any error, timeout or unparseable reply falls through to the **model-unavailable path** that already existed and is exercised daily (A4).
- **Consequence for the demo (D-015):** we now have a *real, reproducible, non-staged* failure to show on camera. D-012 already required demonstrating a case the model gets wrong; this is better than a contrived one, because it is our own, and it is the model we actually ship.
  > Demo line: *"Here is the model we use, confidently describing rocks and vegetation in a picture of two rectangles. That is exactly why it is never allowed to decide anything here — it only ever asks a person a question."*
- **Recorded honestly in the README limitations section**, not buried.

**Follow-up result — prompt hardening did NOT fix it.** The production prompt instructs the model, explicitly, to report only what is literally visible, to avoid describing what a stream usually looks like, and states that "cannot tell" is the correct and preferred answer and will not be penalised. Run against the same two-rectangle image at `temperature=0` with enforced JSON output, it still returned:

> *"A narrow watercourse with rocks and vegetation on the banks."*

- **Conclusion, and it is the important one:** this failure mode is **not promptable away**. The mitigation therefore has to be **structural** — the model is denied any path to a decision — and that is exactly what D-012 and D-023 already require. We did not choose the tight constraint out of caution; we chose it, then confirmed empirically that a looser one would have failed.
- **Failure direction is contained, and deliberately so.** A false `shows_watercourse: true` means one question goes unasked — a missed prompt, not a false accusation. A false `shows_watercourse: false` means the citizen is asked "is this the image you meant?" and simply says yes. **Neither direction can harm the record or the citizen**, because vision output cannot reach urgency, cannot resolve an indicator, and cannot alter an answer.
- **The tri-state guard held:** `visible_litter` and `appears_turbid` both returned `None` rather than `False` on an image containing neither, confirming that absence of evidence is not being recorded as evidence of absence.

### D-024 — Modular structure: four seams, no ceremony
- **Date:** 2026-09-14 · **Status:** ACTIVE · **Amends:** D-005, D-020
- **Owner instruction, verbatim:** *"when building it follow the modular approach because that way adding removing or making will be much easier and will have less impact on the overall code if we need some changes later"*
- **Decision:** restructure the backend into four layers, chosen because each is a **real boundary a future change will actually fall along** — not because layering is tidy.

```
backend/
  main.py              composition root ONLY: build app, wire routers, mount static
  config.py            all settings resolved in one place (env wins over .env)
  domain/              what an observation MEANS. Pure: no I/O, no framework.
    field_protocol.py    indicators + differentials, each cited to published method
    assess.py            the four dimensions
  adapters/            the only code that touches the outside world
    store.py             persistence
    vision/              model providers behind one interface
      __init__.py          provider selection
      azure_openai.py      Azure AI Foundry
      null.py              offline; always available
  api/                 HTTP shape only. No domain knowledge.
    protocol.py  observations.py  review.py  shared.py
```

- **What each seam buys, concretely:**
  | Future change | What it touches now |
  |---|---|
  | Add or reword an ecological indicator | `domain/field_protocol.py` — one dict entry. Nothing else, frontend included (it renders `/api/protocol`). |
  | Swap the vision model (Azure → Anthropic → local) | one new file in `adapters/vision/` + one branch. Domain and API unchanged. |
  | Run with no model at all | `VISION_PROVIDER=null` — **verified working**. |
  | SQLite → Postgres | `adapters/store.py` only. |
  | Add or remove an endpoint | one file in `api/`. |
- **Why not more layers:** no repository interfaces over a 7-column table, no service layer between two thin things, no DI container. Each would be ceremony around a seam that does not exist. `domain/` importing nothing outward is the constraint that actually matters, and it is enforced by the import graph rather than by convention.
- **Bug this refactor created and then fixed — worth recording, because it is a trap:** `domain/__init__.py` initially re-exported `from .assess import assess`, which bound the package attribute `assess` to the **function**, shadowing the **module** of the same name. `from domain import assess; assess.assess(...)` then failed with `AttributeError: 'function' object has no attribute 'assess'`. Re-exports removed, and the reason is documented in that file so nobody re-adds them. **Convenience re-exports were ceremony; deleting them fixed the bug and removed the trap.**
- **Verified after refactor:** 38 contract checks green; full pipeline (submit with photo → Azure vision → citizen differential → cyanobacteria resolution → One Health precaution → queue ordering → attributed review) green; provider switching green in both directions.

### D-025 — Shipped: public repository and live deployment
- **Date:** 2026-09-14 · **Status:** ACTIVE · **Satisfies:** hackathon deliverables 4 and 5
- **Repository (public):** https://github.com/chanderbhanu096/riparia
- **Live application:** https://riparia-oah.azurewebsites.net
- **Hosting:** Azure App Service (Linux, Python 3.12) on the owner's **existing** `signwise-plan` (B1). No new plan, no new cost centre. One app serves both the API and the built SPA from a single origin — so no CORS in production and one thing to deploy.
- **Secret handling, checked rather than assumed:** `.env` is gitignored with `.env.example` committed; credentials are Azure **App Settings** (environment variables), never in the repo or the deployment artefact. Before both the first push and the first deploy, the staged tree and the zip were scanned for the literal key — **both confirmed clean**. `config.py` reads env first so the same code runs locally and in production with no branch.
- **Stale-shell bug — the app shipped with NO cache headers at all.** The owner reported still seeing the old design after a successful deploy. The server was correct (`index.html` referenced the new bundle; the old bundles returned 404) — their browser was holding a cached HTML shell that pointed at a bundle which no longer existed. Vite fingerprints assets, so the shell is the one file that must never be cached, and we were sending no `Cache-Control` at all, leaving browsers to guess.
  **Fixed at the server** (`backend/main.py`, one middleware): `/assets/*` → `public, max-age=31536000, immutable`; `/api/*` → `no-store`; everything else, the shell included → `no-cache`. Verified live.
  **Why this mattered more than it looks:** a judge opening the link twice during judging would have seen a stale or blank app, and "please hard-refresh" is not something you get to say to a judging panel.
- **Deployment gotcha — `az webapp deploy` exit code 0 does not mean success.** A deploy of the modular build printed `FailedInstances: 1` with *"the worker process failed to start within the allotted time"* and **still exited 0**. The app had in fact started correctly moments later (B1 cold start outran Azure's status check). Both readings of that output are wrong on their own: the exit code says success where the status says failure, and the status says failure where the app is healthy. **Always verify a deployment against the running app, never against the deploy command.** The reliable probe is `/api/health`, whose `vision` field only exists in the modular build, so it distinguishes new code from a stale worker.
- **Known limitation, stated:** SQLite lives on the App Service filesystem, so the demo database resets on redeploy. Acceptable for a prototype; noted rather than hidden (D-021).

### D-026 — Visual direction: draw the specimens, do not describe them
- **Date:** 2026-09-14 · **Status:** ACTIVE (awaiting owner's pick of direction) · **Amends:** D-020
- **Owner instruction, verbatim:** *"design must be amazing not boring"* — given after a first pass of three competent-but-conservative directions. Correct call: a generic Tailwind look is itself an "assembled with AI" tell (D-021), and UX is 15% of the rubric.
- **The finding that reframed the whole screen.** In 1843 Anna Atkins published *Photographs of British Algae: Cyanotype Impressions* — the first book ever illustrated with photographs. Its stated purpose was to serve as a **visual companion to Harvey's unillustrated 1841 *Manual of British Algae***, because written descriptions of algae were not sufficient to identify them by.
  > That is **this screen's exact problem**. A person at a streambank cannot separate filamentous algae from a cyanobacterial bloom from sewage fungus by reading three sentences — and a wrong call in either direction means a missed pollution incident or a false alarm. The answer has been known for 183 years: **show the specimen.**
- **Consequence — this is a product decision, not a styling one:** the differential now renders each option as a **drawn specimen**. The illustration is the feature. Geometry lives in `design/specimens.py` and is identical across every direction, drawn from the diagnostic features already in `field_protocol.py`.
- **Three directions published:** `1 · Cyanotype` (Atkins' own process — Prussian blue plate, white photograms, EB Garamond, the chosen option pulled as a positive print; **recommended**), `2 · Nocturne` (dark water-optics instrument, justified by dawn/dusk field use), `3 · Broadsheet` (a public water notice — newsprint, Bodoni Moda, one stamped red).
- **The three conservative directions were dropped**, not kept as a hedge. Files remain on disk.
- **Parity enforced by construction.** An independent review of the first pass found the safety instruction had drifted into **four different versions** across four artboards — one dropped "and off the shoreline", another added "do not let animals drink", two dropped the lead-in. That is protective advice quietly becoming a design detail. Copy now lives once in `design/content.py`, lifted verbatim from `field_protocol.py`, and every artboard is generated from it by `design/build.py`. It cannot drift again.
- **Accessibility floors enforced in the generator** after the same review found them broken: no text below 12px (was 10.5px), the urgency line is never the smallest type on the screen (it was, in all three first-pass directions — which inverts the hierarchy exactly where it costs most), body contrast at or above 4.5:1, tap targets at or above 44px, icons inline SVG only (one dingbat removed).
- **Canvas:** https://claude.ai/artifact/Gg5A9vHAgoTA2GZWvZftzd

### D-027 — Recommendation reversed: Broadsheet, not Cyanotype
- **Date:** 2026-09-15 · **Status:** ACTIVE — *awaiting owner's final pick* · **Amends:** D-026
- **Trigger:** owner asked for GPT's independent read. Codex reviewed all three directions (`duet` run `20260915-064407-d0f5f5`) and picked **Broadsheet**, explicitly rejecting the Cyanotype recommendation on record. Full write-up: [`DESIGN_VERDICT_GPT.md`](DESIGN_VERDICT_GPT.md). **Accepted.**

**The functional defect that settled it.** The three options name **colours** — "Long **green** strands", "**Blue-green**, like spilled paint", "**Grey or dirty-white** slimy strands". Every direction drew all three in a single ink.
> *"Monochrome silhouettes discard the color distinctions named in the options."*
Colour is the first thing a person matches, and we had thrown it away in the very feature built to help them match. Specimens are now drawn in their own diagnostic colours, with shape still distinct (strands / colonies / tufts) so the reading survives colour blindness and greyscale print — three redundant channels rather than one.

**And that disqualifies Cyanotype on its own terms.** A cyanotype is **monochrome by process**. Its concept structurally forbids the single most diagnostic feature of the thing it exists to identify. The concept fights the function, and function wins.

**Other arguments accepted:**
- **The reviewer surfaces decide it, and I under-weighted them.** Two of the three surfaces left to build are dense reviewer UI (triage queue, detail view with four dimensions). A light ground with a sans body extends there; an ornate dark plate does not. That is two-thirds of the remaining work.
- **The Atkins reference was over-claimed.** *"Freshwater expertise does not imply photographic-history recognition."* Demoted from a legitimacy argument to an optional one-line design credit. The historical insight that led to drawing the specimens **stands on its own** — it was right about the product even though the aesthetic it suggested was wrong.
- **Nocturne's justification was thin.** *"Caustics are decoration, not evidence of field suitability."* Agreed — and our own note that the middle renders flat undercut it further.
- **Drawings are schematic aids, never identification plates.** Not validated against real field examples. Stated on the canvas; raises the value of AUDIT Q8/Q9 (an ecologist's hour).
- **Sunlight legibility is unverified for all three** and cannot be settled from source. Needs a real phone outdoors.

**Five corrections applied to Broadsheet:** "Water notice" → **"Field observation"** (a citizen report must not masquerade as an official warning); explicit **"Your answer"** with a check instead of an inverted black row; red reserved for the precaution so a routine report does not read as an emergency; **"Awaiting review"** beside the reading; body text to 15px; paper grain removed.

**Clipping caught and fixed by measurement, not arithmetic.** Raising body text to 16px pushed the artboard **89px over** its 844px frame, clipping the end of the safety copy — *"Dogs have died after drinking at affected water"* — and the footer entirely. Found by measuring `scrollHeight` in a browser rather than estimating, trimmed everywhere **except the safety text**, and re-measured to exactly 844 with zero overflow.
> **Rule for the rest of this project: never let the safety copy be what gets cut. Measure the frame, do not estimate it.**

- **Canvas:** https://claude.ai/artifact/Gg5A9vHAgoTA2GZWvZftzd

### D-028 — Direction chosen: Broadsheet. Building it through all three surfaces
- **Date:** 2026-09-15 · **Status:** ACTIVE · **Closes:** the design question opened in D-026/D-027
- **Owner's decision, verbatim:** *"let's go with 3"* — Broadsheet. Both the independent GPT review and my own revised recommendation agreed, so this is settled and will not be reopened.
- **Design system now fixed** (tokens in `frontend/src/index.css`, one home):
  | Token | Value | Rule |
  |---|---|---|
  | ground | `#f3f0e7` newsprint | page |
  | surface | `#ffffff` | cards, rows |
  | ink | `#15120e` | all primary text |
  | rule | `#cdc5b4` | hairlines; `3px solid ink` for the masthead rule only |
  | muted | `#4a4137` / `#6d6354` | secondary text, both ≥ 4.5:1 on ground |
  | **red** | `#b02d18` | **the citizen precaution, and nothing else** |
  | ochre | `#8a5214` | ecological urgency — deliberately NOT the precaution red |
  | algae / cyano / fungus | `#3f6b24` / `#137a72` / `#7e7d74` | specimen diagnostic colours |
  | display | Bodoni Moda | masthead and page title only |
  | text | Archivo | everything a person actually reads |
- **Guardrails carried from the GPT review into the reviewer surfaces** (F3/F4 of `DESIGN_VERDICT_GPT.md`):
  1. **Extend it as an information system, not a newspaper poster.** Bodoni for the masthead and one heavy rule; **no 33px headlines and no black panels repeated in every queue row.**
  2. **Consequence, completeness and review status stay three separate, text-labelled things** — never merged into one badge. This is D-012's four dimensions surviving into the visual layer.
  3. **Urgency never wears the precaution's red**, and never reads as a verdict. It is rendered in ochre and always phrased as *potential* consequence, because an ecological classification is not ours to make and a reviewer's decision is not ours to pre-empt.
  4. **Routine states look routine.** Broadsheet's own failure mode is making every report look like an emergency.
- **Specimen drawings ported into the app** as `frontend/src/Specimens.jsx`, extended beyond green growth to the sheen shatter test and foam character so the feature is consistent wherever a differential exists. Where no drawing exists the option renders as text alone — never a placeholder.
- **Labelled as schematic aids, not identification plates**, in the UI as well as the canvas (D-027).

### D-029 — "Too plain": modernising Broadsheet without abandoning it
- **Date:** 2026-09-15 · **Status:** ACTIVE · **Amends:** D-028
- **Owner feedback, verbatim:** *"I checked the website and its too plane make it modern look"* — on the deployed app, not the mockup. Correct, and the diagnosis matters more than the fix.
- **Why the built app looked plain when the mockup did not.** The mockup was the *result* screen at 390×844: dense, illustrated, high-contrast. The first screen a visitor actually lands on is the capture form, and it had **none of that**:
  1. **The drawings — the single best thing in this design — only appeared AFTER submitting.** The opening screen was ten identical text rectangles.
  2. **Uniform rhythm.** Every section was a 15px label over a row of chips. No hierarchy, nothing to look at.
  3. **No scale.** At 1280px it was a lonely narrow column of 14–15px text.
  4. **No material.** The paper grain had been removed, leaving dead flat cream.
- **Fix, three moves and deliberately only three** (research on current editorial practice converged on the same discipline: *one* typographic system, *one* colour strategy, *one* controlled layer of depth or texture beats a page full of effects):
  1. **Illustration moved to the first screen.** Ten drawn indicator marks (`IndicatorMark` in `Specimens.jsx`), picker rebuilt as a two-column illustrated grid. This is the same argument as D-026 applied one screen earlier: show, do not describe. **The dullest surface became the most distinctive one.**
  2. **Type as architecture.** `clamp()`-scaled display sizes so the page has presence on a laptop, plus **a monospace (IBM Plex Mono) for the utility layer** — labels, counts, statuses, record ids. That separates data from prose at a glance and is where the "crafted" texture comes from. It also suits an observation record specifically.
  3. **One texture layer + real depth.** Fixed paper-fibre noise at 16% opacity, and elevation from a hairline plus a soft shadow on hover.
- **Explicitly rejected as AI-slop house style**, despite appearing in every "2026 trends" source: gradient grounds, glassmorphism, blurred colour blobs, rounded cards with a left accent bar. Adopting those would undo the reason for choosing an editorial direction at all. Recorded in `index.css` next to the code so it is not re-added later.
- **Colour discipline preserved.** Indicator marks are drawn in ink, not colour, because in this app **colour means diagnosis** (D-027) and at selection time nothing has been diagnosed. Colour still arrives at the differential, where it carries meaning.
- **Cut during the pass:** a `+1 Q` badge on indicators that carry a follow-up question. Cryptic jargon dressed as information; the question announces itself when it appears.

### D-030 — Refinement pass, and a correction flow that collected no correction
- **Date:** 2026-09-15 · **Status:** ACTIVE · **Amends:** D-028, D-029 · **Source:** [`UX_REVIEW_GPT.md`](UX_REVIEW_GPT.md), run `20260915-074256-dc9d8c`
- **Owner asked for** typographic refinement and rounded corners, and for GPT's UX/UI read. Codex agreed on both and then found three defects that matter more than either.

**THE ONE THAT MATTERED — a correction that contained no correction.**
The "Let me update that" button stored the literal sentence *"Citizen updated their answer after review"* and the UI replied *"your update sits alongside your original answer"* — **while never showing an input and never capturing a replacement answer.** The citizen was told their correction was saved; nothing had been. In the one flow this entire product exists to protect (D-012: the citizen's account is preserved and clarification is meaningful), the app was lying to them.
> Fixed: the button now opens the actual options for that field — or a free-text box where the field has none — and stores what the person really said, shown back to them in quotes. A correction containing no correction is worse than no correction at all.

**Rounded corners — owner right, and scoped.** Exactly **6px**, on interactive controls only: chips, indicator buttons, differential options, inputs, textareas, the file button, actions. **Square everywhere else** — masthead, rules, queue rows, definition rows, drawings, photographs, metadata tags, panels. The editorial identity lives in paper, type, rules and restrained colour; none of it required sharp buttons.

**Typography, to reviewed values** (see UX_REVIEW_GPT.md §2 for the table): Bodoni confined to the masthead and page titles — a display face at 20px is just a small display face and costs readability for nothing; section headings become Archivo 20/26; field questions become **prose** (Archivo 16/22 sentence case) instead of tracked-out mono labels; body to 16/24; hints from 12px up to 14/20; action labels from 13px uppercase at 0.18em tracking to Archivo 15/20 sentence case; reviewer inputs to 16px, **below which iOS zooms on focus**.

**Other accepted findings:**
- **"One quick check" could be three.** Ticking sheen + foam + green growth produced three questions under a heading promising one. Now counted honestly.
- **Red was leaking.** The "While you're still there" kicker and generic network errors both wore `#b02d18` — the colour reserved for citizen safety — contradicting our own rule. Errors are now ink, headed "Could not save", with a retry.
- **A failed save destroyed the reviewer's work.** The error branch replaced the whole detail view including a typed-but-unsaved assessment. It now keeps the text and says so.
- **No pending state or double-click guard** on the central clarification path. Added.
- **The paper texture was invisible** — painted at z-index 0 beneath an opaque app root. Moved above content at 4%, over opaque reading surfaces.
- **Keyboard focus landed on the `sr-only` radio**, so it could not be seen. Ring moved to the visible chip.
- **Control borders lightened to invisibility** at `#cdc5b4`. Interactive controls now use `#6d6354`; the pale rule stays for decorative dividers.
- Report/Review/Back raised to 44px targets; selected indicators carry a non-colour tick; original answers render through protocol labels rather than raw identifiers.

**Deferred as explicitly not submission blockers** (its ranking, which I followed): queue search, alternate sorting, a pre-send summary screen. *"Square corners, absence of search and lack of a decorative progress percentage are much less consequential"* than a citizen leaving before answering or a reviewer losing their work.

### D-031 — Full-width field station, following the owner's new design instruction
- **Date:** 2026-09-15 · **Status:** ACTIVE · **Amends:** D-028, D-029, D-030 visual specifics
- **Owner request:** use the full browser width and improve a design they still found dull. This is new authorisation to revise the earlier chosen treatment; preserving the narrow column was not a requirement.
- **Built:** removed every outer `max-w-4xl` cap; fluid page gutters, desktop two-column capture, a decorative river/topography illustration, forest ink on a light ground, larger editorial titles, clearly numbered field sections, a full-width review desk and a separate One Health summary. Controls remain clear and keyboard focus visible; panels now have restrained 8px corners. Brand colour is not a diagnostic state: diagnostic specimens keep their colours; ochre means triage; red remains precaution-only.
- **Functional improvements alongside design:** explicit Real observation / Practice report choice; synthetic records stay labelled; unfinished citizen and reviewer drafts survive navigation between views; current review status refreshes on returning to the report; original answers are visible beside clarification; missing checklist is missing evidence, never an empty observed list; clarification retry resends the failed answer.
- **Verification:** rendered desktop and 390px mobile views; measured no horizontal overflow, including 1920px desktop where the main spans the full available width. Browser walkthrough: practice report → cyanobacteria option → full precaution → named reviewer → explicit inclusion → summary → downloaded provenance, with original answers preserved. Physical-phone sunlight, VoiceOver and independent ecological usability remain unverified.

### D-032 — P4: explicit approval binds the handoff to the report a person reviewed
- **Date:** 2026-09-15 · **Status:** ACTIVE · **Implements:** D-007, D-014, D-016/A3
- **Decision:** a free-text assessment or `reviewer_assessed` status does not imply approval. The reviewer must explicitly select **Include this observation in the site summary**. Approval carries the content fingerprint shown to that reviewer. A stale approval is rejected; a later citizen clarification removes summary/export eligibility until another review.
- **Built:** `/api/sites?record_class=...`; site and individual-record JSON downloads; original answers, all clarifications, reviewer history, four dimensions, source/version and limitations. Real, synthetic and evaluation evidence never mix. Anonymous unnamed reports without coordinates are not merged into a pretend site. No trend, confirmed pollution, exposure, water-safety or WFD conclusion is inferred.
- **Standards claim:** native RIPARIA provenance JSON plus a **proposed FHIR R4 4.0.1 mapping**, only for existing contact-pathway readings. No fictional patient, measured toxin or confirmed exposure. No validated profile, validator or receiving-system integration. The host's draft OAH implementation guide is a future comparison, not a compatibility claim. See `docs/EXPORT.md` and its reproducible synthetic example.
- **Hardening:** unique uploaded filenames preserve prior photographic evidence; SQLite connections close; reviewer history is retained from this release onward. Previously overwritten history cannot be recovered.
- **Ecology regression found and fixed:** foam answered “unsure” previously fell from high to medium urgency. It now stays high. More categorical explanations such as “not a spill” were narrowed to a possible visual reading; a field answer does not establish safety.
- **Verification:** 39 assessment checks and isolated HTTP contracts pass, including unapproved exclusion, late clarification, stale approval, record-class separation, original-answer preservation, history and photo collisions. Existing local data was not used for tests.

### D-033 — Demo evidence prepared; official announcement resolves stale rules dates
- **Date:** 2026-09-15 · **Status:** ACTIVE · **Amends:** §0 dates and current delivery status
- **Prepared:** `docs/DEMO_SCRIPT.md` (4:25), `docs/SUBMISSION_DRAFT.md`, `docs/OBSERVATION_TO_ACTION.md`, and the six-case `docs/WALKTHROUGH.md` generated by `scripts/walkthrough.py`. The walkthrough passed six cases / 50 software-behavior checks. It uses invented inputs, no independent assessor, and makes no accuracy or measured-outcome claim. Answering “unsure” removes a pending question but does not resolve the ecological ambiguity.
- **Still missing:** the recorded video and a genuine field capture clip, physical-phone/assistive-technology tests, independent freshwater-practitioner review, final Devpost entry.
- **Official discrepancy verified:** the rules page still lists September 16–30 and registration close August 31. The newer [official September 14 announcement](https://oneaquahealth-ieee-hackathon.devpost.com/updates/46406-reminder-oneaquahealth-hackathon-starts-tomorrow-get-ready-to-build-submit) explicitly states **September 14–30**. Devpost's submission-start timestamp agrees (September 14, 16:00 UTC). The recorded initial build is within that newer period. Registration was confirmed by an authenticated read; the existing Untitled entry is **pre-draft**, not a completed submission. No external submission or message was sent.
- **Deadline unchanged:** September 30, 21:00 PDT; target September 29. The published 30/20/20/15/15 weights agree across current materials. Scoring-scale metadata conflicts with the rules prose, so no predicted numerical score is offered. Winning and a particular cash payout are not assured.

### D-034 — Preserve live observations across Azure releases
- **Date:** 2026-09-15 · **Status:** ACTIVE · **Amends:** D-025 storage limitation
- **Finding:** Azure Oryx serves this Python app from a temporary runtime directory. Code-relative SQLite and photo paths therefore risk being replaced on redeployment. This is a data-loss risk, not an acceptable property to carry into the new handoff.
- **Fix:** on Azure, runtime data lives in `/home/data/riparia`; ordinary local defaults stay unchanged. `RIPARIA_DATA_DIR` permits an explicit override. `scripts/preserve_runtime.py` makes a verified SQLite online backup and photo copy, supports a brief write freeze for the final transfer, and can restore old-runtime writes on rollback. Backups remain outside the served site directory.
- **Release:** `scripts/stage_release.py` stages code and the built frontend only, excludes credentials/runtime data, and checks for credential leakage without printing any key. A deployment succeeds only after the served bundle and API are verified, with the old record IDs and photo hashes still present. See `docs/DEPLOYMENT.md` for the completed release record.
- **Pre-existing missing evidence:** before deployment, all seven live records were present, but two photo references pointed to one already-missing image (HTTP 404). No local image was substituted without proof. The review view now states that the original photo is unavailable.
- **Additional hardening:** static-file paths are resolved and must remain within the frontend build directory. Encoded traversal is rejected.
- **Live verification:** public shell matches `index-a93AXrZU.js` / `index-BJBnMzlj.css`; all seven existing observation objects compare unchanged. `/api/sites` returns JSON and the public browser loads the redesigned checklist and summary without console errors.
- **Verification:** 12 isolated HTTP tests and 39 assessment checks; migration rehearsal confirms exact row/photo preservation, old write freeze, new database writes, and rollback unfreeze. Frontend build/lint and browser smoke checks pass. This remains a web prototype, not an installable offline PWA or a production identity/retention system.

---

## 2. Implementation plan — REVISED per D-013 (real dates, ethical core first)

Deadline **2026-09-30 21:00 PDT**. **Target submission: 2026-09-29**, leaving Sept 30 as
untouched buffer. Phases are ordered so a demonstrable artefact exists from P1 onward.

> **The original plan built peripheral checks first and the ethical core at D7–D8. That is
> inverted here.** The capture → clarify → reviewer spine is built first, end to end, because
> it is both the ethical contract (D-012) and the thing the demo follows (D-015). Checks are
> then added to a spine that already works.

| Phase | Dates | Deliverable | Done when |
|---|---|---|---|
| **P0 — Lock** | **Sep 14** ✅ | Track confirmed, GPT review folded in (D-010…D-017), repo public, README skeleton, **A2 observation-to-action diagram** | Owner confirms D-002/D-010; repo live. *Diagram first — it defines the story everything else serves.* |
| **P1 — Ethical spine** | **Sep 15–17** | Capture (photo + answers) → **neutral** clarifying question → record preserving original answers verbatim → reviewer view. FastAPI + SQLite + PWA shell + Leaflet | **One observation travels capture → clarify → reviewer, on a real phone** |
| **P2 — Four-dimension engine** | **Sep 18–20** | Completeness · detected inconsistency · ecological urgency · review status (D-012). Watercourse subject check. Defensible checks only | Each dimension renders **with a human-readable reason**, and no rule deleted in D-012 has crept back |
| **P3 — Triage + reviewer** | **Sep 21–22** | Queue ranked by **consequence under uncertainty**; reviewer assessment stored as attributed judgment | An uncertain-but-serious report ranks **above** a certain-but-trivial one |
| **P4 — Insight + export** | **Sep 23–25** | Site insight summary (Track 2 absorbed), export with provenance + check trail, **A3 annotated export example**, FHIR per D-014 | Export validates or is relabelled "proposed mapping". **FEATURE FREEZE end of Sep 25** |
| **P5 — Harden** | **Sep 26–27** | Accessibility pass, mobile pass, empty/error states, **model-unavailable state (A4)**, deploy, self-check tests | A judge can use it cold, on a phone, with the model offline |
| **P6 — Tell + submit** | **Sep 28–29** | **A1 scripted walkthrough evaluation**, demo video (D-015 single-case script), README, track alignment statement | **SUBMITTED Sep 29** |
| **Buffer** | **Sep 30** | — | Untouched. Devpost last-day load is a known failure mode |

**Scope guard:** build count is **4 components**, not 5 (D-011 cut calibration). Adding a
fifth requires a new decision entry explaining what it displaces.

---

## 3. Risk register

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R1 | No real data undermines credibility | High | High | D-006: documented generator, visible labelling, one real live capture in the video |
| R2 | Judges read "AI validates citizens" as replacing human judgment | Medium | **Critical** | **Superseded by D-012.** No auto-accept *and* no auto-reject; neutral questions; original answers preserved; reviewer approval required before "validated"; state the position in the first 30s of the video |
| R3 | Scope creep across 5 components | High | High | Phase gates in §2; each phase must leave a runnable system |
| R4 | Model API cost/latency during judging | Medium | Medium | Cache model responses for seeded records; pre-warm the demo path |
| ~~R5~~ | ~~Eligibility~~ | — | — | **CLOSED (D-018)** — owner is a student |
| R6 | FHIR misuse noticed by the panel that taught FHIR | Medium | High | D-007 guardrail: map only genuine human-health-exposure fields |
| R7 | Demo video rushed | Medium | High | D-008: 2 days reserved, scripted before recording |
| **R8** | **Confident scientific error** — the system contaminates a record or deprioritises a real incident | Medium | **Critical — now the top risk** | D-012: four separate dimensions instead of a truth score; three ecologically wrong rules deleted; urgency never lowered by uncertainty; show a model mistake on camera |
| R9 | Unvalidated FHIR conformance claim, noticed by the panel that taught FHIR | Medium | High | D-014: name version + profile + validator and pass it, or say "proposed mapping" everywhere |
| R10 | Narrative implicitly disparages the hosts' own shipped tools | Medium | High | D-012/§7: pitch is "helps reviewers resolve incomplete observations", **never** "makes your dashboards usable" |

---

## 4. What "winning" looks like — self-scoring target

| Criterion | Weight | Target | The specific thing that earns it |
|---|---|---|---|
| Impact & Alignment | 30% | 9 | Solves the trust bottleneck blocking their own DSS; One Health framing throughout |
| Innovation | 20% | 8 | "AI asks, human answers" inversion + calibration honesty — not another dashboard |
| Technical | 20% | 8 | Hybrid deterministic+model engine, OpenAPI, tests, real third-party integration |
| UX | 15% | 8 | PWA on a real phone, plain language, accessible, works one-handed at a streambank |
| Feasibility/Scalability | 15% | 9 | Drops into the existing CitizenScience App; standards-aligned export; expert-time economics |

> **Tempered by D-017.** These are *targets*, not predictions, and they are earned by what a
> judge can see working — not by the framing. Impact 9 in particular is unearned until the
> observation-to-action pathway (D-016/A2) is concrete and the walkthrough evaluation
> (D-015/A1) exists. Claim a **pathway demonstrated at the first link**, never an improved
> ecosystem or health *outcome* from a prototype.

---

## 5. Open questions (blocking flagged)

| # | Question | Owner | Blocking? |
|---|---|---|---|
| ~~Q1~~ | ~~Eligibility: students-only?~~ **CLOSED (D-018)** — owner is a student; moot. | — | Closed |
| ~~Q2~~ | ~~Team or solo?~~ **CLOSED (D-018)** — solo. Triggered the D-019 re-scope. | — | Closed |
| Q3 | Does the owner accept D-002 (Track 3) or override to Track 2 (→ D-003)? | Owner | Yes |
| Q4 | Can organisers grant read access to `api.enora-oah.eu`? Worth one email — a "no" costs nothing, a "yes" upgrades everything. | Owner | No, but high value |
| Q5 | Rename the working directory to drop the trailing space (D-009)? | Owner | No |
| Q6 | Confirm D-010: Track 3 held on rebuilt reasoning. Owner's original Track 2 preference is formally overridden — accept, or invoke D-003 (now "possible, at real cost", not one day)? | Owner | **YES** |
| ~~Q7~~ | ~~FHIR profile + validator by Sep 25?~~ **CLOSED (D-019)** — "proposed mapping" taken up front to buy back 1.5 days. | — | Closed |
| Q9 | D-022 raises the value of Q8 sharply: one hour from a freshwater ecologist reviewing `backend/field_protocol.py` alone would now validate the entire domain layer. Is one reachable? | Owner | No, but highest value/hour available |
| Q8 | Can any reviewer with freshwater ecology knowledge look at the check list once? One hour from a domain expert is the cheapest possible insurance against R8. | Owner | No, but very high value |

---

## 6. For any agent joining this work

**Read [§00 START HERE](#00-start-here--full-briefing-for-anyone-opening-this-cold) first** —
it is the full briefing and it assumes no prior context. Then:

1. §0.2 (the rubric) is the objective function. Argue against a decision **in rubric terms** or not at all.
2. **Read §1b (D-010 … D-034) before §1.** The later decisions amend the earlier ones; acting on D-002/D-004/D-008 alone rebuilds mistakes already caught and paid for.
3. Do not add a component that is not in D-004 as amended. Build count is **4**, not 5.
4. Ponytail mode is active: reuse before writing, stdlib before dependency, shortest thing that works. But **never** shorten the eight rules in §00.7 — they are the product's spine.
5. Append your decisions as `D-0XX`. **Never edit history**; supersede it.
6. Three independent reviews are on file (`REVIEW_GPT.md`, `DESIGN_VERDICT_GPT.md`, `UX_REVIEW_GPT.md`). Several findings in them were correct and expensive; check them before re-deriving.

---

## 7. Independent review — Codex / GPT

**Status: COMPLETE.** Full write-up: [`REVIEW_GPT.md`](REVIEW_GPT.md) ·
raw report: `.duet/runs/20260914-215657-dbebe6/REPORT.md`

| | |
|---|---|
| Reviewer | Codex (GPT), adversarial strategy review via `duet` |
| Verdict | **REVISE** — keep Track 3 provisionally; cut one component; fix the validation model |
| Findings | 8 (2 must-fix, 4 should-improve, 1 optional, 1 deliverable) |
| Accepted | **7 of 8 in full**, 1 rejected with reason (Track 7 bake-off, D-014) |
| Resulting decisions | D-010 … D-017 |

> A prior run (`20260914-215306-6baadf`) ran with roles inverted and returned a placeholder
> finding. **Discarded — it is not a second opinion.**

**The three findings that changed the product, not just the wording:**

1. **The Confidence Engine was ecologically wrong** (→ D-012). Clear water *can* smell of
   sewage — dissolved sewage produces odour without turbidity, so our flagship
   "contradiction" rule was a domain error. Turbidity after dry weather is a *valuable
   anomaly* signalling a discharge event, not implausibility — the rule would have buried
   the single most report-worthy case. Missing EXIF is missing evidence, not evidence
   against a citizen. **And the root error beneath all three: collapsing everything into one
   "confidence score" invents an unvalidated truth measure.** Replaced with four separate,
   honestly-named dimensions.

2. **Our own design contradicted our own safety promise** (→ D-012). R2 pledged "never
   auto-reject" while component 3 specified that unambiguous records "auto-accept".
   Auto-acceptance delegates a consequential judgment to the system just as surely. And
   *"a human answering a leading question is not meaningful oversight."*

3. **The pitch insulted the judges** (→ D-010, R10). *"We built the trust layer that makes
   the dashboards usable"* implicitly disparages Resilience Map, City Dashboards and
   GEOSSIP — **which the judging panel built.** Replaced with a bounded claim: *helps
   reviewers resolve incomplete observations.*

**Reasoning retracted as asserted-not-demonstrated** (→ D-010): the 401 ⇒ no-data
inference, both track-crowding claims (Track 2 "most crowded", Track 7 "least crowded" —
neither measured, and both worthless if prizes rank across all tracks), and D-003's
"one-day reversal".

**Where we disagreed with the reviewer:** it wanted a half-day Track 7 (FHIR) bake-off
before committing. Its critique of our Track 7 dismissal was correct — "FHIR demos badly"
was wrong on the rubric's own terms, since UX is judged *for the intended user*, and an
integration analyst getting actionable validation errors is good UX. But a half-day
comparison is unaffordable at 15 days, and the reviewer's own conclusion was *"Otherwise
keep Track 3."* We kept Track 3 and adopted its conformance guardrail instead (D-014).

**Standing instruction for future agents:** the reviewer's decision rule now governs this
project — *choose the track, and the feature, with the strongest **demonstrable outcome** and
credible delivery; not the most elaborate architecture, and never guessed entrant density.*

---

## 8. Changelog

| When | Who | What |
|---|---|---|
| 2026-09-14 21:55 CEST | Claude (Opus 5) | File created. D-001…D-009 recorded. Track 3 selected over owner's initial Track 2 preference, with reversal path D-003. |
| 2026-09-14 22:05 CEST | Codex (GPT) via `duet` | Adversarial strategy review, run `20260914-215657-dbebe6`. Verdict **revise**, 8 findings. Earlier run `20260914-215306-6baadf` discarded (inverted roles, placeholder output). |
| 2026-09-15 11:10 CEST | Claude (Opus 5) | Added **§00 START HERE** — a complete standing briefing so any agent or person opening this file cold (in Codex or anywhere else) has the goal, every link, the product thesis, the file-by-file codebase map, run/deploy instructions with both known deploy traps, the eight non-negotiable rules, what is left, and a table of ideas already tried and rejected. Also untracked `adapters/riparia.db` and the `design/_*.html` scratch previews, which had been committed to the public repo. |
| 2026-09-15 10:30 CEST | Claude (Opus 5) | **D-030** refinement pass on GPT's UX review. 6px corners on controls only; full type scale reset (Bodoni confined to masthead/titles, questions become prose, 16px inputs). Fixed a **correction flow that collected no correction**, a heading promising one question when it asked three, red leaking onto non-safety UI, a failed save wiping the reviewer's typed assessment, invisible keyboard focus, and a paper texture painted beneath an opaque root. |
| 2026-09-15 09:15 CEST | Claude (Opus 5) | **D-029** owner reported the built app looked plain — correct: the drawings only appeared after submitting, so the first screen was ten text rectangles. Illustration moved to the capture picker (10 drawn indicator marks), clamp-scaled display type, IBM Plex Mono for the metadata layer, one fixed paper-texture layer. Gradients/glassmorphism explicitly rejected and recorded in the CSS. |
| 2026-09-15 07:40 CEST | Claude (Opus 5) | **D-028** owner chose **Broadsheet**. Design system tokenised; specimens ported to React and extended to the sheen and foam differentials; reviewer-surface guardrails fixed (urgency never wears the precaution red, the three dimensions stay separate and text-labelled, no black panels per queue row). |
| 2026-09-15 07:00 CEST | Claude (Opus 5) | **D-027** recommendation reversed to **Broadsheet** after Codex picked it and rejected Cyanotype. Decisive: the options name colours and every direction drew them in one ink — and a cyanotype is monochrome by process, so its concept forbids the most diagnostic feature. Specimens now coloured. Five corrections applied. A 16px body pushed the artboard 89px over frame and clipped the safety copy; caught by measuring in-browser, fixed to exactly 844. |
| 2026-09-15 01:05 CEST | Claude (Opus 5) | **D-026** visual direction. Anna Atkins' 1843 cyanotypes of British algae — published because text descriptions could not identify algae — reframed the differential: draw the specimens rather than describe them. Three bold directions published; three conservative ones dropped. Copy and specimen geometry centralised so parity is structural; a11y floors enforced in the generator after a review found 10.5px labels and the urgency line set in the smallest type on screen. |
| 2026-09-15 00:10 CEST | Claude (Opus 5) | **P3 complete** (reviewer detail: triage rationale, resolved field answers, One Health precaution, model note shown *with* its unreliability stated). **D-024** modular restructure into domain/adapters/api + composition root; fixed a re-export that shadowed a module. **D-025** shipped: public repo + live Azure App Service on the existing B1 plan; secret scans clean before both push and deploy. |
| 2026-09-14 23:25 CEST | Claude (Opus 5) | **D-023**: Azure AI Foundry (`gpt-4.1-mini` on existing `signwise-ai`) adopted for the photo pass — no new key or resource. First test call **hallucinated** rocks and vegetation in a 96×96 two-colour test image; recorded as first-hand evidence for R8 and used to harden the vision pass to question-raising only (tri-state findings, never `false`; never touches urgency). Becomes the on-camera failure case D-012 requires. |
| 2026-09-14 23:05 CEST | Claude (Opus 5) | **P1 spine complete and verified in browser.** Backend (FastAPI+SQLite), `field_protocol.py` (10 cited indicators, 3 differentials), `assess.py` (4 dimensions), 38 contract checks green, React PWA. Verified live: shatter test demotes a sheen high→low *by citizen answer*; cyanobacteria path emits One Health precaution; queue ranks by consequence under uncertainty. Two bugs found and fixed by own tests/browser check (empty-list completeness; vanishing differential feedback). README written with mandatory limitations section (D-021). |
| 2026-09-14 22:40 CEST | Claude (Opus 5) | Owner required expert-grade provenance. Added **D-021** (no invented domain content; cite published method next to the logic) and **D-022** (ARMI trigger-level precedent; shatter test / foam / cyanobacteria-vs-sewage-fungus differentials; WFD non-conflation guardrail). Domain layer rebuilt as `field_protocol.py`. |
| 2026-09-14 22:20 CEST | Claude (Opus 5) | Owner confirmed **student** + **solo**. Q1/Q2/Q7 closed, R5 closed. Added **D-018…D-020**: solo re-scope cutting FHIR validation, the map, and the weather integration (~3.5 days recovered). Build count stays 4. |
| 2026-09-14 22:10 CEST | Claude (Opus 5) | Review folded in. Added §1b **D-010…D-017**. Confidence Engine redesigned (3 ecologically wrong rules deleted, single truth score replaced by 4 dimensions). Component 4 cut, build count 5→4. §2 re-dated to real calendar, ethical core moved to front. R8/R9/R10 added; R2 superseded. §7 completed. Q6–Q8 opened. |

| 2026-09-15 | Codex | **D-031–D-033:** full-width field-station design; P4 explicit-approval summaries and provenance export; practice mode and navigation preservation; storage and uncertainty fixes; six-case walkthrough, 4:25 video script, submission draft and action diagram. Verified newer official build dates and registration; actual video/submission remain outstanding. |
| 2026-09-15 | Codex | **D-034:** persistent Azure runtime data and verified backup/deployment scripts; static-path containment; 12 HTTP contracts, 39 assessment checks and responsive browser checks pass. |
