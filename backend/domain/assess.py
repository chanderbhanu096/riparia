"""
Four-dimension assessment of a citizen stream observation.

Design contract (AUDIT.md D-012) -- read before changing anything here:

  There is NO single "confidence score". Four dimensions are computed and shown
  separately, because collapsing them invents a truth measure we cannot validate.

    completeness           which fields are present/absent      -- never implies error
    detected_inconsistency named tensions needing a human look  -- never called "error"
    ecological_urgency     could this matter, if true?          -- NEVER lowered by uncertainty
    review_status          not_reviewed | in_review | reviewer_assessed

  Nothing here accepts, rejects, or validates an observation. Only a reviewer does
  that, explicitly. These functions describe; they do not decide.

Three rules were DELETED after review and must not come back (D-012):
  1. "clear water + sewage odour = contradiction" -- ecologically WRONG. Dissolved
     sewage produces odour with no turbidity.
  2. "turbidity without recent rain = implausible" -- BACKWARDS. That pattern
     suggests a discharge event, the most report-worthy case there is.
  3. "missing EXIF GPS = weaker record" -- UNFAIR. Most phones strip EXIF by
     default. Missing evidence is missing evidence, never evidence against a person.

Note on what an "inconsistency" can honestly be: answer-vs-answer contradictions
barely exist in freshwater ecology -- almost any odd combination is physically
possible. So tensions here are almost all photo-vs-answer, where the model holds
independent evidence (the image) to compare against the citizen's account. Every
one is phrased as a question to the citizen, never as a verdict about them.
"""

from typing import Any

from . import field_protocol as fp

UNSURE = "unsure"

# Context fields plus one incident channel -- the shape real rapid-assessment
# protocols use: a few habitat descriptors for context, and a separate list of
# specific indicators that may each warrant follow-up.
#
# `indicators` holds keys from field_protocol.INDICATORS. Odour and litter live
# there too rather than as free-standing questions, because each one carries its
# own reading and its own urgency and they do not belong on a shared scale.
#
# "unsure" is a first-class answer everywhere (AUDIT.md D-012).
CORE_FIELDS = [
    "water_clarity",
    "flow",
    "surrounding_land_use",
    "indicators",
    "wildlife_seen",
]

URGENCY_ORDER = {"low": 0, "medium": 1, "high": 2}


def completeness(answers: dict[str, Any]) -> dict[str, Any]:
    """Which fields are present. Absence is described, never penalised as error.

    'unsure' counts as ANSWERED. A citizen saying "I don't know" has told us
    something true and useful; treating it as a gap would teach people to guess.
    """
    missing = [f for f in CORE_FIELDS if _is_blank(answers.get(f))]
    unsure = [f for f in CORE_FIELDS if answers.get(f) == UNSURE]
    answered = len(CORE_FIELDS) - len(missing)
    return {
        "answered": answered,
        "total": len(CORE_FIELDS),
        "missing": missing,
        "marked_unsure": unsure,
        "note": (
            "Fields left blank are simply not recorded. "
            "'Unsure' is a valid answer and is not a gap."
        ),
    }


def _is_blank(v: Any) -> bool:
    """Only a genuinely absent answer is blank.

    An EMPTY LIST is an answer, not a gap: on a multi-select like visible_impacts,
    selecting nothing means "I looked and saw none of these", which is a real and
    useful observation. Counting it as missing would nag a citizen who did the
    right thing, and would quietly pressure people to tick something.
    """
    if v is None:
        return True
    if isinstance(v, str):
        return v.strip() == ""
    return False


def detected_inconsistency(
    answers: dict[str, Any],
    photo_findings: dict[str, Any] | None = None,
) -> list[dict[str, str]]:
    """Named tensions worth a human look. Returns [] when there is nothing to ask.

    Each item carries a neutral question for the citizen -- never an accusation,
    never a correction applied on their behalf. The citizen may disagree, and
    their disagreement is recorded (D-012).

    photo_findings comes from the vision pass and is advisory only. When it is
    absent (offline, model unavailable), this returns fewer tensions -- it never
    invents one and never treats absence as suspicion.
    """
    out: list[dict[str, str]] = []
    pf = photo_findings or {}

    # The photo does not appear to show a watercourse at all. Without a stream in
    # frame, no ecological reading of the image is possible -- so this is asked
    # first and phrased as "did the right image attach?", not "you are wrong".
    if pf.get("shows_watercourse") is False:
        out.append({
            "id": "photo_subject",
            "field": "photo",
            "question": (
                "This photo doesn't clearly show a stream or watercourse. "
                "Is this the image you meant to attach?"
            ),
            "basis": "photo",
        })

    # Litter: the image suggests debris, the form says none. Genuinely ambiguous --
    # natural woody debris reads as litter to a model and is ecologically normal.
    # So it is offered as a choice, with the innocent reading stated explicitly.
    if answers.get("litter") == "none" and pf.get("visible_litter") is True:
        out.append({
            "id": "litter_vs_photo",
            "field": "litter",
            "question": (
                "There appears to be debris near the bank in your photo. "
                "Would you like to update the litter answer, or is that "
                "natural material like branches and leaves?"
            ),
            "basis": "photo",
        })

    # Clarity: the image reads as turbid, the form says clear. Light, shade, depth
    # and bed colour all fool this -- so the citizen, who was standing there, decides.
    if answers.get("water_clarity") == "clear" and pf.get("appears_turbid") is True:
        out.append({
            "id": "clarity_vs_photo",
            "field": "water_clarity",
            "question": (
                "The water looks cloudy in the photo, though you recorded it as "
                "clear. Shade, depth or a dark streambed can all cause that. "
                "Which matches what you saw?"
            ),
            "basis": "photo",
        })

    # Location: only ever raised when the device actually supplied coordinates.
    # Absence of GPS is NEVER a tension (D-012, deleted rule 3).
    drift_km = pf.get("location_drift_km")
    if isinstance(drift_km, (int, float)) and drift_km > 1.0:
        out.append({
            "id": "location_drift",
            "field": "location",
            "question": (
                f"The photo's location is about {drift_km:.1f} km from the site "
                "you selected. Did you pick the right site, or was the photo "
                "taken elsewhere?"
            ),
            "basis": "photo",
        })

    return out


def ecological_urgency(answers: dict[str, Any],
                      differentials: dict[str, str] | None = None) -> dict[str, Any]:
    """Could this matter, if it is accurate?

    Every reading comes from field_protocol, where each one is tied to published
    guidance. Nothing is graded here on an invented scale (AUDIT.md D-021).

    Deliberately ignores how complete or certain the record is. An uncertain
    report of a fish kill is still a possible fish kill (D-012). And an indicator
    that has NOT yet been narrowed down is held at the highest reading it could
    be, not the average and not the most convenient -- consequence under
    uncertainty, the ARMI trigger-level principle applied to visual reports.
    """
    differentials = differentials or {}
    indicators = answers.get("indicators") or []

    readings, one_health, reasons = [], [], []
    resolved: dict[str, Any] = {}
    for ind in indicators:
        r = fp.resolve(ind, differentials.get(ind))
        readings.append(r)
        resolved[ind] = {"reading": r["reading"], "urgency": r["urgency"],
                         "explain": r["explain"], "one_health": r.get("one_health")}
        label = fp.INDICATORS.get(ind, {}).get("label", ind)
        askable = bool(fp.differential_for(ind))
        if r["reading"] == "unresolved" and askable:
            reasons.append(f"{label} — not yet narrowed down")
        else:
            reasons.append(f"{label} — {r['explain']}")
        if r.get("one_health"):
            one_health.append(r["one_health"])

    # Very murky water is a context field, not an indicator, but it still carries
    # standing on its own: heavy suspended solids smother habitat and often
    # accompany an input upstream.
    if answers.get("water_clarity") == "very_turbid":
        readings.append({"urgency": "medium"})
        reasons.append("Water reported as very murky")

    level = "low"
    for r in readings:
        if URGENCY_ORDER[r["urgency"]] > URGENCY_ORDER[level]:
            level = r["urgency"]

    return {
        "level": level,
        "reasons": reasons or ["Nothing of concern was reported"],
        "resolved": resolved,
        "one_health_notes": one_health,
        "unresolved_indicators": [r["indicator"] for r in readings
                                  if r.get("reading") == "unresolved"
                                  and fp.differential_for(r.get("indicator", ""))],
        "note": (
            "A triage judgement about whether a person should look, and how soon. "
            "Not an ecological status classification, and deliberately not reduced "
            "when a record is incomplete or uncertain."
        ),
    }


def field_differentials(answers: dict[str, Any],
                        differentials: dict[str, str] | None = None) -> list[dict[str, Any]]:
    """The field questions worth asking the citizen while they are still at the stream.

    These are real differential diagnostics from field practice -- the shatter
    test for a sheen, foam character, telling cyanobacteria from filamentous
    algae from sewage fungus -- not generic model-generated prompts (D-022).

    Only asked where a member of the public can safely and reliably resolve it.
    Where they cannot, nothing is asked.
    """
    differentials = differentials or {}
    out = []
    for ind in (answers.get("indicators") or []):
        if ind in differentials:
            continue
        d = fp.differential_for(ind)
        if d:
            out.append({
                "id": d["id"],
                "indicator": ind,
                "field": "indicators",
                "question": d["question"],
                "options": [{"key": k, "label": v["label"]} for k, v in d["options"].items()],
                "basis": "field_protocol",
            })
    return out


def triage_priority(urgency: dict[str, Any], comp: dict[str, Any],
                    tensions: list[dict[str, str]]) -> dict[str, Any]:
    """Rank by consequence under uncertainty -- the inversion D-012 demands.

    Uncertainty RAISES priority on a serious report instead of lowering it: an
    unclear report of an oil sheen is exactly what a reviewer should see first,
    because that is where their attention changes the outcome. On a low-urgency
    record, uncertainty barely moves the ranking -- there is little at stake either way.
    """
    base = {"high": 100, "medium": 40, "low": 10}[urgency["level"]]

    unresolved = (len(comp["missing"]) + len(comp["marked_unsure"]) + len(tensions)
                  + len(urgency.get("unresolved_indicators", [])))
    # Scaled by base, so uncertainty amplifies what is already consequential
    # rather than pushing trivial-but-messy records to the top.
    uplift = min(unresolved, 6) / 6.0 * (base * 0.5)

    return {
        "score": round(base + uplift, 1),
        "rationale": (
            f"{urgency['level']} potential consequence"
            + (f", {unresolved} unresolved point(s) a reviewer could settle"
               if unresolved else ", record is complete")
        ),
    }


def assess(answers: dict[str, Any],
           photo_findings: dict[str, Any] | None = None,
           review_status: str = "not_reviewed",
           differentials: dict[str, str] | None = None) -> dict[str, Any]:
    """Full four-dimension assessment. Describes only -- decides nothing."""
    comp = completeness(answers)
    tensions = detected_inconsistency(answers, photo_findings)
    urg = ecological_urgency(answers, differentials)
    return {
        "completeness": comp,
        "detected_inconsistency": tensions,
        "ecological_urgency": urg,
        "review_status": review_status,
        "field_differentials": field_differentials(answers, differentials),
        "triage": triage_priority(urg, comp, tensions),
        "disclaimer": (
            "This is a description of a citizen report, not a validation of it. "
            "No observation is accepted, rejected or called validated without an "
            "explicit reviewer decision."
        ),
    }
