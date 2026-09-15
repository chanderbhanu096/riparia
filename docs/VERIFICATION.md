# Release verification — 15 September 2026

These checks establish software behavior and layout in a browser. They do not establish ecological accuracy, an independent scientific assessment or real-world health outcomes.

## Executed

- Production frontend build and lint: pass.
- Assessment contract: 39 checks pass.
- Isolated HTTP handoff contract: 12 tests pass, using a temporary database and null vision provider.
- [Scripted assessment walkthrough](WALKTHROUGH.md): six fixed cases, 50 software-behavior checks pass.
- Browser workflow: submit a labelled practice report with green growth, answer the paint-like option, retain the full precaution and original answers, enter a named demonstration assessment, explicitly approve summary inclusion, read the synthetic site summary and inspect the downloaded provenance JSON.
- The browser-created export retained `record_class=synthetic`, the original green-growth indicator, the citizen's clarification, the named approval and `validated=false` on its proposed FHIR mapping.
- Before approval, the record was absent from approved summary evidence. Practice data stayed out of the real-observation tab.
- An unfinished reviewer assessment survived navigation to the summary and back. Citizen state survives navigation too.
- Responsive checks: 320px and 390px mobile widths, the default 1264px desktop view and 1920px desktop. No horizontal overflow. The 1920px view measured a 1905px main area (the remaining width is the scrollbar), with two working columns.
- Visually inspected desktop capture, clarification, review queue and site summary, plus mobile capture/clarification and summary. Safety content remains in normal scrolling flow, never clipped into a fixed-height card.
- Browser console: no errors or warnings during the workflow.
- Contrast calculations: primary text 11.17:1, secondary 6.62:1, hint text 4.74:1, control border 3.84:1, precaution text 5.85:1 and urgency text 5.67:1 against their intended grounds.

## Public release

The public app serves the verified new shell (`index-a93AXrZU.js` and
`index-BJBnMzlj.css`). The checklist and One Health summary load in the public
browser without console errors. All seven pre-deployment observation objects
compare unchanged. Existing reviews without explicit approval correctly remain
outside summary evidence. No new test record was added to the live data.

## Known limits

- Browser width overrides are not a physical-phone test. Camera use, sunlight readability, touch behavior, VoiceOver and a full accessibility audit remain unverified.
- Model-independent tests do not establish the optional vision model's accuracy. The historical model failure is described in the audit; no new reproducibility claim is made.
- Reviewer names and report categories are self-declared in this prototype.
- Two old live photo references already returned 404 before the release. No replacement image was substituted. The review screen now explains unavailable photos.
- Cloud release and preservation results are recorded separately in [DEPLOYMENT.md](DEPLOYMENT.md).
