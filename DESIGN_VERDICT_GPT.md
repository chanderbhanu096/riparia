# DESIGN_VERDICT_GPT.md — Codex / GPT picks a design direction

| | |
|---|---|
| **Reviewer** | Codex (GPT), via `duet` |
| **Run** | `20260915-064407-d0f5f5` |
| **Date** | 2026-09-15 |
| **Verdict** | **BROADSHEET.** Cyanotype rejected. |
| **Raw report** | `.duet/runs/20260915-064407-d0f5f5/REPORT.md` |

> Stated limit, its own words: it can read source but **cannot see rendered output**.
> Its layout and hierarchy judgements rest on the rendering notes it was given plus
> the source. Sunlight legibility it explicitly refused to rule on.

---

## 1. The pick

> "Pick BROADSHEET. Its strongest-at-a-glance hierarchy [...] serves a panel scoring
> many entries quickly, and its light ground with Archivo body text offers the most
> economical foundation for the two reviewer surfaces."

Rubric reasoning, its framing: Impact (30%) is served by making the observation, the
precaution and the human decision immediately understandable; Innovation (20%) lives
in the field question and accountable review, **not in historical styling**;
Technical (20%) is better demonstrated by a complete consistent three-surface
workflow than by decorative filters; UX (15%) by readable evidence and unmistakable
states; Feasibility (15%) by reusing one simple type/rule/status system in the time
left.

## 2. Why Cyanotype was rejected

- **The Atkins reference does not confer legitimacy.** *"Freshwater expertise does not
  imply photographic-history recognition."* It can read as erudite to someone who
  catches it; claiming it confers scientific standing **risks pretension with this
  panel**. Demote it to an optional one-line design credit.
- **The real liability is not Victorian influence** — it is *"small, delicate text and
  decorative hierarchy during outdoor use."*
- **Sunlight:** cannot be established from source. *"Pale text on dark blue can have
  strong nominal contrast while reflections obscure it."* Needs a real phone outdoors.
  Broadsheet is *"the better starting choice, not a verified sunlight solution."*

## 3. The decisive argument — the reviewer surfaces

Two of the three remaining surfaces are dense reviewer UI: a triage queue and a detail
view with four separate assessment dimensions. That is where a strong aesthetic breaks.

Broadsheet extends as an **information system**: cream ground, dark sans body, aligned
columns, thin row rules. Keep Bodoni for the masthead and one heavy rule; **do not
repeat 33px headlines or black panels in every queue row.** Consequence, completeness
and review status get separate text labels. And a hard guardrail, consistent with
D-012: *"never let a red ecological-urgency label resemble a final ecological
classification or human verdict."*

## 4. Five cheap corrections before carrying it through (~half a day)

1. **"Water notice" → "Field observation"** — so a citizen report does not masquerade
   as an official warning.
2. Add an explicit **"Your answer"** label and a check to the selected option; reserve
   red for consequential precautions only.
3. **16px** citizen body and safety text; allow scrolling rather than shrinking copy to
   fit a fixed artboard.
4. Put a clear **"Awaiting human review"** status beside the possible reading; keep all
   canonical precaution text.
5. Drop the paper grain; define reusable colour, type and rule tokens.

> "Do not spend the remaining week building another theme."

## 5. Blunt — what it called slop

- *"Familiar components are not evidence of incompetent AI assembly."* — pushback on
  D-026's "generic Tailwind is a tell".
- *"Caustics are decoration, not evidence of field suitability."* The dawn/dusk
  justification for Nocturne was thin, and our own note that its middle renders flat
  weakens the optical conceit further.
- **The sharpest catch — the drawings throw away the primary diagnostic signal:**
  *"monochrome silhouettes discard the color distinctions named in the options and lack
  demonstrated diagnostic accuracy."* The three options are literally "Long **green**
  strands", "**Blue-green**, like spilled paint", "**Grey or dirty-white** slimy
  strands". Colour is the first thing a person matches, and every direction drew all
  three in one ink.
- *"Keep them as schematic aids beside the descriptions, never as authoritative
  identification plates."* Atkins does not validate our drawings.
- **Broadsheet's own self-indulgence:** *"treating every report as a consequential
  public notice; routine and unresolved states need visibly calmer treatment."*
- Worth more than another historical paragraph: *"a short ecologist review and a few
  non-specialist comparisons against real field examples."* (Already open as AUDIT Q8/Q9.)

## 6. What it could not verify

Rendered screens, the Broadsheet reviewer queue and detail at real density,
direct-sunlight readability on a phone, enlarged-text layout, and whether
non-specialists can actually use the schematic specimens correctly.
