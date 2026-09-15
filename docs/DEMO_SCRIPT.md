# RIPARIA — demo script

**Target length:** 4 minutes 25 seconds. **Status:** ready to rehearse; no video has been recorded by this task.

The main story follows one explicitly synthetic observation from report to reviewer handoff. It demonstrates a workflow, not a pollution finding, an accuracy study or an actual authority response. The site summary and export section must be recorded against the final working build.

## Before recording

- Record at 1920×1080 with readable browser text; briefly show the mobile capture layout. Add captions and leave the pointer still while explaining a record.
- Use the app's **Practice report** mode for the main case; it saves the record as synthetic. Never record invented answers under the authentic label. If recording an older build without a record-class selector, create the synthetic record through the documented API and label the clip; do not disguise an API-created record as a live UI submission.
- Use a fictional site name: **Demo reach — park footbridge**. Do not attach real coordinates to the invented incident. Use a clearly labelled schematic image or no photo; do not present an unrelated photograph as evidence of a bloom.
- Main case answers: water clarity **Not sure**; flow **Slow**; surroundings **Park or green space**; indicator **Green, blue-green or grey growth in or on the water**; note **Synthetic walkthrough: a visitor reports surface growth near a park footbridge.**
- On the growth question choose **Blue-green, like spilled paint or scum on the surface**. This is a scripted citizen answer, not a confirmed identification.
- Demonstration reviewer name: **Chander Bhanu — demonstration reviewer**. Decision: **Prompt local review proposed**. Note: **Scripted assessment: check the original report and clarification; consider an appropriate local investigation. No bloom, toxin or exposure is confirmed. No authority has been contacted.**
- Explicitly approve this synthetic record for inclusion in the site summary. Ordinary reviewer attribution alone does not make it summary evidence. A later clarification requires re-review before it qualifies again.
- Check the current deployed build, capture and review path, and downloaded export before starting. Use a local build with `VISION_PROVIDER=null` for a labelled model-unavailable segment; a missing network connection is a different condition.
- Add a short authentic capture clip from a safe public path. Record only what is actually present, with the actual time and place. Keep this separate from the synthetic case, and do not approach or touch suspected contamination to improve the footage. If this clip does not exist, list it as missing.

## Timed narration and shots

| Time | Show | Say |
|---|---|---|
| **0:00–0:20** | Genuine streambank photo/capture, if available. Caption: **Authentic capture • separate from the scripted case**. Then title. | “A person at an urban stream can notice something unusual before anyone else. The hard part is handing that observation to someone who can decide what should happen next. RIPARIA keeps the citizen's account, asks for useful detail, and gives a named reviewer the decision.” |
| **0:20–0:40** | Main report form. Keep **Synthetic walkthrough** visible. | “This next example is scripted. A visitor reports green growth near a park footbridge. They do not know how clear the water is. ‘Not sure’ is a useful answer here. It does not make a potentially serious observation disappear.” |
| **0:40–1:10** | Submit the synthetic record; show the illustrated growth question and all choices, including unsure. | “The follow-up comes from our documented field protocol. These drawings help the visitor describe shape and colour. They are schematic aids, not identification plates. Our visitor chooses the paint-like surface appearance. That answer is added to the record; the original ‘green growth’ report stays intact.” |
| **1:10–1:35** | The resulting possible-cyanobacteria reading, precaution and **Awaiting human review** status. | “The result is a possible concern with a precaution, not a diagnosis. A visual report cannot establish whether toxins are present. This is the One Health connection: the same water can matter to stream life, people and animals. The app keeps uncertainty visible while calling for human attention.” |
| **1:35–2:10** | Reviewer queue, then this same record's original answers, clarification and four dimensions. | “The reviewer sees four different things: completeness, detected inconsistency, ecological urgency and review status. There is no combined trust score. This report was already potentially serious before clarification; uncertainty did not lower its urgency. Now the reviewer can see exactly which detail was added, and who provided it.” |
| **2:10–2:40** | Enter the demonstration reviewer name, decision and note. Explicitly approve summary inclusion, save, then show the attributed assessment. | “I am playing the reviewer for this demonstration; this is not an independent ecological assessment. The intended user is a local citizen-science coordinator or environmental reviewer. I record my reasons and explicitly approve summary inclusion. That records my assessment; it does not contact an authority or confirm pollution.” |
| **2:40–3:10** | Same site in the One Health summary, with synthetic records selected. Show approved evidence and pending reports separately. | “The site view keeps pending reports separate from evidence a reviewer explicitly approved for this summary. It also keeps simulated records separate from real observations. A reviewed record is still not a laboratory result or a declaration that this reach is safe. New clarification requires another review.” |
| **3:10–3:40** | Download and open the same observation's provenance export. Highlight `original_answers`, `clarifications`, `review.history` and `proposed_fhir_mapping`. | “The handoff keeps the evidence chain: the original report, the citizen's clarification and the named review. The FHIR representation inside the export is a proposed mapping for integration discussion. We have not validated it against an implementation guide, and no receiving service is connected.” |
| **3:40–4:05** | Labelled development audit excerpt for the two-colour-image failure, then model-unavailable state. | “In an earlier development test recorded in our audit, the vision model described rocks and vegetation in an image of two flat colour bands. That finding shaped the architecture: model output can raise a question, but cannot change an original answer, set urgency or approve a record. When photo analysis is unavailable, the field questions and human review still work.” |
| **4:05–4:25** | Observation-to-action diagram, then repository and demo links. | “What we can show today is a traceable route from observation to human review. An agreed local investigation pathway is the next step, followed by independent field evaluation. RIPARIA is our Track 3 prototype: clearer citizen evidence, visible uncertainty, and a human decision.” |

Do not read every row verbatim if the run exceeds five minutes. Keep the original-versus-clarification contrast, named review, no-model behavior and honest limits; trim transitions first.

## Recording rules that protect credibility

1. Leave the same observation ID visible when moving between reviewer detail, summary and export. This is proof of one connected workflow.
2. Keep the synthetic label in frame. A genuine photograph does not make scripted answers authentic.
3. If showing historical model output, label it **Earlier development test, recorded in AUDIT.md**. Do not claim a fresh model call returned the same result unless it actually did. Do not splice a replay into a live response without a replay label.
4. Describe the field questions as protocol-based. The optional vision pass can trigger additional neutral questions; it is not the source of every question or of the ecological rules.
5. Say **proposed local investigation** and **proposed FHIR mapping**. Never say the prototype notified a regulator, diagnosed a bloom, verified safe water or improved health outcomes.

The [annotated export guide](EXPORT.md) explains the actual download and its limits. Use the real downloaded record in the footage; a committed example is supporting documentation.

## Small walkthrough evidence plan

The [executed six-case assessment walkthrough](WALKTHROUGH.md) now records pure-function results with fixed synthetic inputs and source fingerprints. It is not a study or browser test. The following on-screen checks remain to be recorded; timebox them to three hours after the final build. These rows are **a recording plan, not results**.

| Fixed case | Evidence to capture |
|---|---|
| Green growth, citizen unsure | High potential urgency remains; original report and unsure response both visible. |
| Green growth, paint-like answer | Citizen-provided clarification, appropriate precaution, still awaiting review. |
| Sheen, cannot safely reach it | No forced answer; potentially serious report stays available for review. |
| Foam, citizen unsure | Answering unsure does not lower urgency simply because of uncertainty. |
| Clear water plus sewage odour | No invented contradiction; odour still gets human attention. |
| Model unavailable | Record, protocol question, clarification and named review remain usable. |

For each, record actual unresolved fields, actual follow-ups, queue position, any important miss and a screenshot. A second person with relevant ecology experience can review these same cases independently; report their role and disagreement honestly. Do not derive an accuracy percentage from a scripted set.

## Final asset checklist

- [ ] Authentic capture clip exists and its answers are genuine.
- [ ] Four-minute synthetic walkthrough is recorded from the final working build.
- [ ] Both portrait capture and desktop review are readable; captions are checked.
- [ ] Same observation is visible in report, review, summary and export.
- [ ] Video URL is public or accessible without a sign-in, and plays from a fresh browser.
- [ ] Runtime is between 3 and 5 minutes, as required by the [official event requirements](https://oneaquahealth-ieee-hackathon.devpost.com/).

Scientific wording is bounded by [CDC's harmful algal bloom overview](https://www.cdc.gov/harmful-algal-blooms/hcp/clinical-overview/index.html) and [CDC's cyanobacterial bloom guidance for animals](https://cdc.gov/harmful-algal-blooms/media/pdfs/algal_bloom_tall_card.pdf): potential harm warrants care, while appearance alone does not establish toxicity. Local public-health guidance would need review before operational use.
