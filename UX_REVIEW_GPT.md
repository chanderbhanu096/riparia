# UX_REVIEW_GPT.md — Codex / GPT UX & UI review

| | |
|---|---|
| **Reviewer** | Codex (GPT), via `duet` |
| **Run** | `20260915-074256-dc9d8c` · 2026-09-15 |
| **Verdict** | **REVISE** — keep Broadsheet, add 6px corners to controls, refine the reading hierarchy. Largest risk is the clarification flow, not the styling. |
| **Raw report** | `.duet/runs/20260915-074256-dc9d8c/REPORT.md` |

> Stated limit: source inspection only, no rendered page. Real-phone, keyboard,
> VoiceOver, forced-colour and outdoor checks remain unverified.

---

## 1. Rounded corners — the owner is right

> "Use exactly **6px** on radio-chip labels, indicator buttons, differential-option
> buttons, text inputs, textareas, the file-selector button, and filled or outlined
> action buttons in both roles. **Keep the masthead, divider rules, queue rows,
> definition-list rows, specimen drawings, photographs, metadata tags, precaution
> panels and explanatory cards square.**"

The reasoning is sound: the editorial identity lives in *paper, typography, rules and
restrained colour* — none of it requires square controls. This gives visible softness
without turning the reviewer surface into rounded cards. **Accepted exactly as specified.**

## 2. Typography — concrete replacements, all accepted

| Element | Was | Now |
|---|---|---|
| Page titles (Bodoni) | `clamp(2.3rem, 5.6vw, 3.6rem)` / lh 0.96 | `clamp(32px, 4vw, 48px)` / lh 1.1 / `-0.01em` |
| Section headings | Bodoni, various | **Archivo 20/26, 600, tracking 0** — Bodoni is masthead + page titles ONLY |
| Field questions | `.meta` mono uppercase 11.5px | **Archivo 16/22, 600, sentence case** |
| Body & options | 15/20–21 | **16/24** |
| Supporting copy | 13–13.5 | **14/20** |
| Metadata | mono 11.5px, tracking 0.1em, always uppercase | **Plex Mono 12/18, 500, tracking 0.04em**; uppercase only for short stage labels |
| Action labels | 13px uppercase, tracking 0.18em | **Archivo 15/20, 600, sentence case** |
| Reviewer inputs | 15px | **16px** — below 16px iOS zooms on focus |
| Hints & caveats | 12/16 | **14/20** |

Plus: apply the 62ch measure to the queue intro and detail explanations, which
currently span the full 896px container.

## 3–5. What it found beyond the styling

**F3 — the worst one. "Let me update that" collects no update.** The button stores the
literal string *"Citizen updated their answer after review"* and the UI then claims
*"your update sits alongside your original answer"* — **but no input is ever shown and
no replacement answer is captured.** A correction that contains no correction, in the
one flow the whole product is about. **Accepted; fixed.**

**F5 — "One quick check" can be three questions.** Every eligible indicator yields a
differential, so ticking sheen + foam + green growth produces three, under a heading
promising one. **Accepted; the heading now counts honestly.**

**F4 — no pending or error handling on the central path.** `clarify` is awaited with no
catch, no pending state and no double-click guard; in the reviewer detail the error
branch replaces the entire view **including a reviewer's typed-but-unsaved assessment.**
**Accepted; fixed.**

**F7 — red used where it has no business.** The "While you're still there" kicker and
generic network errors both wore `#b02d18`, the colour reserved exclusively for citizen
safety precautions — contradicting our own rule in `index.css`. **Accepted; fixed.**

**F6 — keyboard focus is invisible on the radio chips.** The outline lands on the
`sr-only` input, not the visible chip. **Accepted; fixed.**

**F10 — the paper texture is almost certainly invisible.** `body::before` sits at
z-index 0 beneath an opaque `bg-ground` root at z-index 1. Also: darken interactive
control borders from `#cdc5b4` to `#6d6354` so control boundaries are robust, keeping
the pale rule for decorative dividers only. **Accepted; fixed.**

**F9 — touch targets.** Report / Review / Back are below 44×44. Also: render original
answers through protocol labels rather than raw underscored identifiers, and add a
non-colour "selected" cue that survives forced-colour rendering. **Accepted.**

## Its ranking, which I followed

> "Square corners, absence of search and lack of a decorative progress percentage are
> much less consequential. Likely UX deductions come from **a citizen leaving before
> answering, an invisible keyboard position, an apparently successful correction that
> contains no answer, or a reviewer losing their work on failure.**"

Deferred as explicitly not submission blockers: queue search, alternate sorting, and a
pre-send summary screen.
