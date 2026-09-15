# RIPARIA — submission draft

**Local draft, 15 September 2026.** This document does not create, update or complete a Devpost entry. Product text below is reusable; readiness notes are for the builder and should be resolved before copying it into the final form.

## Title

RIPARIA — From stream observation to human review

## One-line summary

Illustrated field questions and a traceable reviewer workflow help citizens describe unusual stream conditions while keeping human judgment in control.

## Track alignment

**Track 3 — AI-Supported Assessment.** RIPARIA supports the assessment of citizen stream reports without delegating decisions to a model. Its optional photo pass can raise neutral clarification questions; field questions and ecological triage come from a separate, documented protocol. Citizens can answer “not sure” or disagree. Original answers remain available beside clarifications, and every reviewer decision is attributed to a named person. Completeness, detected inconsistency, ecological urgency and review status remain separate. The prototype cannot automatically accept or reject a report.

The One Health site summary and provenance export support the same workflow. They are supporting capabilities, not claims of a separate validated prediction or standards product.

## Problem and target users

A person walking beside an urban stream may notice a sheen, foam, surface growth, unusual odour or dead fish. These observations can be useful, but their meaning is often uncertain. A photograph may not contain the detail a reviewer needs, and the observer may already have left when a follow-up is requested.

RIPARIA serves two users: a member of the public reporting what they can observe, and a local citizen-science coordinator or environmental reviewer deciding whether more information or investigation is appropriate. It explores how to make the handoff between those users more explicit and accountable.

## Solution

The citizen records a stream observation through a guided interface. When a reported feature has a relevant field question, illustrated choices help them add the detail they can actually see. “Not sure” remains a valid answer. The original report is preserved alongside each clarification.

A reviewer sees the original account, citizen clarifications, optional model questions and the reasons for the report's potential urgency. Missing detail does not make a serious report less urgent. The reviewer records an attributed assessment rather than an automatic yes/no verdict. The product aims to make the evidence behind that decision inspectable.

The site summary and downloadable record extend this handoff: only records explicitly approved by a reviewer count as summary evidence, pending reports remain separate, and synthetic records stay separate from real observations. A later clarification requires re-review before the record qualifies again. The export carries the original account and its subsequent clarification and assessment. Its FHIR representation is a **proposed mapping**, not validated conformance or a connected clinical system.

## Why this matters for One Health

Urban freshwater is shared by stream organisms, wildlife, pets and people. A reported paint-like surface growth is one concrete example: harmful algal blooms can affect these groups, while appearance alone cannot determine whether toxins are present. RIPARIA connects that uncertainty to a precaution and a human review action. It does not infer exposure, illness, water safety or confirmed contamination from an image. [CDC guidance](https://www.cdc.gov/harmful-algal-blooms/hcp/clinical-overview/index.html), [visual-identification limit](https://cdc.gov/harmful-algal-blooms/media/pdfs/algal_bloom_tall_card.pdf).

This is a proposed route from citizen observation to a possible local investigation. The prototype demonstrates the reporting and review portion. An investigation partnership, field accuracy, reviewer time savings and ecosystem or health outcomes have not been established. The intended pathway is documented in [Observation to action](OBSERVATION_TO_ACTION.md).

## What is distinctive

The contribution is the combination of illustrated questions about a specific observation, preserved citizen answers, urgency that remains visible under uncertainty, and an attributed reviewer decision. The reviewer can inspect what changed after a question and what did not. Human review itself is an established practice; RIPARIA does not claim to have invented it.

## AI and development tools

**AI in the product:** an optional Azure AI Foundry vision provider, currently configured for `gpt-4.1-mini`, makes limited observations about the submitted image. Its output can prompt the citizen for clarification. It cannot alter the original answers, set ecological urgency or approve a record. A null provider keeps the capture, protocol questions and review flow usable when photo analysis is unavailable.

**AI in the build:** Claude Code and Codex assisted development and review. The audit records reviews that removed a combined trust score, corrected an ecologically unsound contradiction rule and repaired a clarification UI that failed to capture a user's intended update. Codex also supported the responsive design pass, the site-summary/export work and this draft. These are development activities, not independent ecological validation.

## Architecture

React and Vite provide the web interface. FastAPI exposes capture, clarification, review and supporting data endpoints. SQLite stores prototype records. Domain rules and field content are separate from storage, model providers and HTTP handlers. This lets an ecologist inspect the ecological content in `backend/domain/field_protocol.py` and lets a developer replace the vision adapter without rewriting those rules.

The existing demo runs on Azure App Service. Reviewer names are entered in a demonstration interface; production authentication, identity verification, retention controls and an operational review service remain future work. Proposed integration starts with inspecting a provenance export, not assuming an existing OneAquaHealth API connection.

A concrete future integration task is to compare the proposal with the host project's [OneAquaHealth FHIR Implementation Guide](https://build.fhir.org/ig/hl7-eu/oah/). The guide currently identifies itself as a changing, unauthorized continuous build. RIPARIA does not claim conformance to that guide.

## Evidence and testing

The demonstration follows one labelled synthetic observation from report to clarification, named review, site summary and export. A separate genuine stream capture should show the actual input path without fabricated environmental answers. The [demo script](DEMO_SCRIPT.md) states which footage and tests remain to be recorded.

Backend contract checks test the intended behavior of the assessment rules. They do not measure ecological accuracy. The [executed six-case walkthrough](WALKTHROUGH.md) records actual before/after outputs and source fingerprints: all six scripted cases passed the expected software behavior. It also states the remaining ambiguity after an unsure answer. The [release verification record](VERIFICATION.md) includes build/test results and an executed browser walkthrough. The walkthrough has not yet been recorded as a video. Real-phone, keyboard and assistive-technology results must be reported only after those checks are actually run.

### Reproduce locally

Follow the repository's current run instructions. To demonstrate the ordinary model-unavailable path, start the backend with `VISION_PROVIDER=null`, then submit a **Practice report** with green growth selected, answer its field question and record a named review. Confirm that the original answer stays visible. Explicitly approve summary inclusion, select synthetic reports in the site view and download the same record's export after installing the final P4 build. The [export guide](EXPORT.md) explains its contents and the proposed FHIR mapping.

## Links and assets

| Asset | Location / status |
|---|---|
| Public repository | [github.com/chanderbhanu096/riparia](https://github.com/chanderbhanu096/riparia) |
| Existing live demo | [riparia-oah.azurewebsites.net](https://riparia-oah.azurewebsites.net) — verify the final build before recording |
| API documentation | [Interactive API docs](https://riparia-oah.azurewebsites.net/docs) |
| Demo video | **TODO: record, upload and test playback; no video URL yet** |
| Script | [DEMO_SCRIPT.md](DEMO_SCRIPT.md) |
| Proposed action pathway | [OBSERVATION_TO_ACTION.md](OBSERVATION_TO_ACTION.md) |
| Annotated export | [Export guide](EXPORT.md) and [synthetic example](examples/approved-synthetic-observation.json) |
| Executed assessment walkthrough | [Six synthetic cases and observed results](WALKTHROUGH.md) |

### Screenshot shot list

1. Responsive capture form with the record class visible.
2. Illustrated field question with the citizen's chosen answer and the unsure option visible.
3. The same record's original answers, clarification and four separate assessment dimensions.
4. Named demonstration review and its reasons.
5. Site summary plus an opened export containing the same observation ID.

## Limitations

- The drawings are schematic aids and field interpretations are provisional; no independent ecological accuracy study has been completed.
- The app supplies triage categories, not laboratory measurements, toxin detection, clinical advice or a Water Framework Directive ecological-status classification.
- A reviewer-entered name is attribution in the prototype, not verified professional identity. An attributed judgment is not ground truth.
- The optional model can make mistakes. A development failure involving a two-colour image is documented in the audit; repeated output is not guaranteed.
- Synthetic observations are demonstrations. Genuine captures and evaluation cases must remain distinguishable.
- FHIR is a proposed mapping without profile validation or a demonstrated receiving-system import. FAIR-related metadata does not establish full FAIR compliance.
- The prototype is independent of the OneAquaHealth consortium and has no approved integration, investigation arrangement or measured environmental or health impact.
- Operational deployment would need domain review, secure reviewer access, an operational backup/retention policy, privacy decisions and a locally agreed response process.

## Official requirements checked on 15 September 2026

These facts were read through the live Devpost connector and checked against the linked official pages. They are readiness notes, not promotional copy.

| Requirement | Verified requirement / readiness |
|---|---|
| Deadline | **30 September 2026, 21:00 PDT**, equivalent to **1 October, 06:00 CEST**. Internal target remains **29 September**. [Official announcement](https://oneaquahealth-ieee-hackathon.devpost.com/updates/46406-reminder-oneaquahealth-hackathon-starts-tomorrow-get-ready-to-build-submit). |
| Core materials | Track explanation; problem, solution, users and expected impact; 3–5 minute video; public code with documentation; working prototype or proof of concept. [Event requirements](https://oneaquahealth-ieee-hackathon.devpost.com/). |
| Submission form | Live connector returned no event-specific custom questions. Video is required; a website and ZIP are not mandatory form fields. Re-check the actual form at final submission. |
| Judging | Rules specify impact/alignment 30%, innovation 20%, implementation 20%, usability 15% and feasibility 15%. [Rules](https://oneaquahealth-ieee-hackathon.devpost.com/rules). |
| Date discrepancy | The newer announcement says **14–30 September** and the submission API opens **14 September at 16:00 UTC**. The older rules page still says 16–30 September. Preserve the actual build history and reference the newer announcement. |
| Scale discrepancy | Rules prose says 1–10; the live judging API reports a maximum score of 5. Neither justifies a predicted score or chance of winning. |
| Participation | The account is registered. Its existing event-linked project was an **Untitled pre-draft** when checked; that is not evidence of a completed entry. Re-check before final submission. |

The rules' participation prose permits individuals or teams; the connector's eligibility summary also includes a team-required flag with no stated minimum. Do not infer a new teammate requirement from that flag alone. Student status is recorded in the audit. No extra eligibility attestations have been made in this drafting pass.

## Remaining work before final entry

- [x] Verify the finished report/review/summary/export workflow locally and the matching final deployed shell, public APIs and retained records. See `VERIFICATION.md`.
- [ ] Record the video and the genuine capture clip; take screenshots from the same final build.
- [x] Execute and report the six-case pure-assessment walkthrough with observed results; this is not a study or browser test.
- [x] Attach final build/test evidence and the executed browser workflow in `VERIFICATION.md`.
- [ ] Record the browser walkthrough as the submission video.
- [ ] Obtain one independent freshwater-domain review if possible; identify it honestly as a review, not a validation study.
- [ ] Check the Devpost pre-draft, exact final form and latest announcements; copy the finalized materials only during an authorized publishing/submission step.

**No prize or placement is guaranteed.** The strongest remaining improvement is credible evidence of one reliable end-to-end workflow.
