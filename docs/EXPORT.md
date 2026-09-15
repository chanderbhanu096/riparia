# Site evidence and provenance export

RIPARIA exports the citizen's original account, clarification trail and named
reviewer's decision in one JSON download. The small FHIR section is a **proposed
mapping**, not a validated FHIR export or a demonstrated system integration.

## What enters the summary

A reviewer must explicitly choose to include a report in the site summary.
`reviewer_assessed` alone is insufficient, and text such as “accepted” does not
count as approval. The reviewer may retain any decision text, including a request
for a site visit, while approving that account for the summary.

Approval is bound to the displayed report's content fingerprint. A later
clarification removes the report from summary evidence and export until a new
review approves it. A stale approval attempt returns HTTP 409. Prior decisions are
retained in `review.history` from this release onward. Previously overwritten
decisions cannot be reconstructed.

Each summary shows one record class: authentic, synthetic or evaluation. Pending
counts include all reports not currently approved, including reviewed reports
whose reviewer has not opted in. Pending reports never contribute ecological
readings, urgency counts or precautions to a summary. Site grouping uses the
submitted name and coordinates; unnamed reports without coordinates remain
separate. These are not verified site identifiers or a monitoring time series.

## HTTP interface

| Request | Result |
|---|---|
| `GET /api/sites?record_class=authentic` | Default authentic-only site summaries; use `synthetic` or `evaluation` explicitly for those classes. |
| `GET /api/observations/{id}` | Report, assessment, `content_sha256` and `summary_eligibility`. |
| `POST /api/observations/{id}/review` | Form fields `reviewer`, `decision`, `note`, optional `approved_for_summary` (default false). Approval also requires `reviewed_content_sha256` copied from the displayed report's `content_sha256`. |
| `GET /api/observations/{id}/export` | One approved record as an attachment; 409 if approval is absent or stale. |
| `GET /api/sites/{site_key}/export?record_class=synthetic` | Only approved records in that site and class; 404 for absent sites, 409 if none is approved. |

The native envelope is `riparia.provenance.v1`, served as `application/json` with
`Cache-Control: no-store`. Photos are linked by path, not embedded. Original JSON
values are retained; submission formatting and image bytes are not part of the
content fingerprint. The fingerprint detects a changed report, not identity,
authenticity or cryptographic authorship. Reviewers and record classes are
self-declared in this demonstration app.

## Annotated example

[Download the complete synthetic example](examples/approved-synthetic-observation.json).
All people, times, place details and observations in it are scripted. It is not
consortium data, a field study, an expert validation or an authentic observation.

| JSON path under `records[0]` | What to inspect |
|---|---|
| `original_answers.indicators` | The original `green_growth` report is unchanged. |
| `clarifications[0]` | Exact field question, citizen-selected answer, key and time. The answer describes a paint-like appearance, not a confirmed bloom. |
| `review` | Named DEMO reviewer, decision, reasoning, explicit approval and reviewed-content fingerprint. |
| `review.history` | The earlier attributed assessment remains available. |
| `assessment` | Completeness, detected inconsistency, ecological urgency and review status stay separate. The triage score orders attention; it is not confidence. |
| `assessment.ecological_urgency.one_health_notes` | The existing field-protocol precaution is carried verbatim. No exposure or safety conclusion is inferred. |
| `provenance` | Protocol and assessment versions; current reassessment is distinguished from historical stored answers. |
| `proposed_fhir_mapping` | Explicit `validated: false`, absent profile and validator, and candidate resources only for the reported contact pathway. |

Reproduce it without touching a database or using a model:

```bash
python3 docs/examples/build_export_example.py
```

## Proposed FHIR mapping: R4 4.0.1

The mapping uses a `Location` subject, never an invented patient. It creates a
candidate `Observation` only when the existing protocol reading carries a
potential human or animal contact pathway. General litter and habitat fields
remain in native JSON. R4 permits `Location` as an Observation subject; it also
separates observations from clinical diagnoses. [HL7 Observation specification](https://hl7.org/fhir/R4/observation.html).

| Source | Candidate FHIR field | Deliberate limit |
|---|---|---|
| Citizen site name / coordinates | `Location.name` / `position` | Coordinates emitted only when both are present and within bounds. No official site registry inferred. |
| Existing protocol contact-pathway reading | `Observation.code.text`, `valueString` | Plain text; no unverified terminology code or measured toxin value. |
| Citizen submission timestamp | `Observation.issued` | `effectiveDateTime` omitted because observation time was not collected. |
| Named reviewer and export time | `Provenance.agent`, `recorded`, `target` | Self-declared name; no fabricated professional credentials. |
| Existing protocol precaution | `Observation.note` | A precaution accompanying the report, not a clinical order or safety result. |

Candidate resources are nested in the native envelope, not a FHIR transaction
Bundle or FHIR server endpoint. `Observation.status` stays `preliminary`; local
summary approval is not clinical finalisation. The proposal is unvalidated:
no implementation profile, terminology validation, recipient agreement or
integration test has been applied. The [HL7 Location](https://hl7.org/fhir/R4/location.html)
and [Provenance](https://hl7.org/fhir/R4/provenance.html) specifications are the
structural references.

The host project also has a [draft OneAquaHealth implementation guide](https://build.fhir.org/ig/hl7-eu/oah/)
and [profile catalogue](https://build.fhir.org/ig/hl7-eu/oah/artifacts.html). The page
identifies itself as an unauthorised continuous build, version 0.1.0-ci-build,
and says it is a working specification, not for implementation. A future
integration discussion should identify a suitable published profile with the
organisers, pin its version, validate the mapping and test recipient import.
RIPARIA does not claim conformance to that draft.

## Verification

```bash
cd backend
.venv/bin/python test_assess.py
.venv/bin/python -m unittest -v test_handoff
```

The handoff suite uses temporary storage and the null vision provider. It checks
approval gating, stale approvals, original-answer preservation, review history,
class separation, export exclusions, empty states and same-filename photo
preservation. It does not establish ecological accuracy, clinical validity or
FHIR conformance.
