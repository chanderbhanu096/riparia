"""Self-check for the assessment contract. Run: python3 test_assess.py

Not coverage theatre. Every assertion encodes a specific promise from AUDIT.md
D-012 (the human-in-the-loop contract) or D-021/D-022 (domain content must trace
to published method). Several exist because an independent review caught the
original design getting the ecology wrong.

If one of these fails, the system has started making scientific claims it cannot
defend -- risk R8, the top risk in this project.
"""

import field_protocol as fp
from assess import (
    assess, completeness, detected_inconsistency, ecological_urgency,
    field_differentials,
)

# A complete, unremarkable urban park reach.
CLEAN = {
    "water_clarity": "clear", "flow": "moderate", "surrounding_land_use": "park",
    "indicators": [], "wildlife_seen": "ducks",
}


def t(name, cond):
    assert cond, f"FAILED: {name}"
    print(f"  ok  {name}")


print("\nDeleted rules must not come back (D-012):")

# Deleted rule 1. Dissolved sewage produces odour with NO turbidity. This was the
# original flagship "contradiction" and it was a domain error.
sewage_clear = {**CLEAN, "indicators": ["smell_sewage"]}
t("clear water + sewage smell raises NO inconsistency",
  detected_inconsistency(sewage_clear) == [])
t("clear water + sewage smell IS high urgency",
  ecological_urgency(sewage_clear)["level"] == "high")

# Deleted rule 2. Turbidity with no recent rain suggests a discharge event -- the
# most report-worthy pattern there is. The old rule would have buried it.
turbid = {**CLEAN, "water_clarity": "very_turbid"}
t("turbidity raises NO plausibility inconsistency", detected_inconsistency(turbid) == [])
t("turbidity still carries standing", ecological_urgency(turbid)["level"] != "low")

# Deleted rule 3. Most phones strip EXIF by default; absence must cost nothing.
t("absent photo findings raise no tensions", detected_inconsistency(CLEAN, None) == [])
t("absent GPS raises no tension",
  detected_inconsistency(CLEAN, {"shows_watercourse": True,
                                 "location_drift_km": None}) == [])

print("\nUrgency is never lowered by uncertainty (D-012):")

sparse = {"indicators": ["dead_fish"]}
full = {**CLEAN, "indicators": ["dead_fish"]}
t("dead fish in a near-empty record is still high",
  ecological_urgency(sparse)["level"] == "high")
t("urgency identical whether sparse or complete",
  ecological_urgency(sparse)["level"] == ecological_urgency(full)["level"])

print("\nUnresolved indicators are held at their worst plausible reading (D-022):")

t("an unnarrowed sheen is treated as potential petroleum",
  ecological_urgency({"indicators": ["oily_sheen"]})["level"] == "high")
t("an unnarrowed green growth is treated as potential cyanobacteria",
  ecological_urgency({"indicators": ["green_growth"]})["level"] == "high")
t("unresolved indicators are named, not hidden",
  "oily_sheen" in ecological_urgency({"indicators": ["oily_sheen"]})["unresolved_indicators"])

print("\nThe citizen's field answer resolves it -- the model does not (D-022):")

shattered = ecological_urgency({"indicators": ["oily_sheen"]}, {"oily_sheen": "shatters"})
t("shatter test clears a sheen to low", shattered["level"] == "low")
t("and says why, in cited terms", "iron-oxidis" in shattered["reasons"][0])
reformed = ecological_urgency({"indicators": ["oily_sheen"]}, {"oily_sheen": "reforms"})
t("a sheen that swirls back stays high", reformed["level"] == "high")
t("a citizen who could not tell keeps it high (never assumed benign)",
  ecological_urgency({"indicators": ["oily_sheen"]}, {"oily_sheen": "unsure"})["level"] == "high")

print("\nDifferentials are only asked where a person can safely answer (D-022):")

qs = field_differentials({"indicators": ["oily_sheen", "dead_fish"]})
t("a sheen gets a field question", any(q["indicator"] == "oily_sheen" for q in qs))
t("a fish kill gets none -- nothing safe to resolve",
  not any(q["indicator"] == "dead_fish" for q in qs))
t("the question is the real shatter test",
  "jagged" in qs[0]["question"] or "breaks into" in qs[0]["question"])
t("an already-answered differential is not asked again",
  field_differentials({"indicators": ["oily_sheen"]}, {"oily_sheen": "shatters"}) == [])

print("\nOne Health advice is tied to a real exposure pathway (D-022):")

cyano = ecological_urgency({"indicators": ["green_growth"]}, {"green_growth": "cyanobacteria"})
t("cyanobacteria carries One Health guidance", len(cyano["one_health_notes"]) == 1)
t("guidance names animals and children",
  "dogs" in cyano["one_health_notes"][0] and "children" in cyano["one_health_notes"][0])
t("filamentous algae carries none -- no exposure pathway claimed",
  ecological_urgency({"indicators": ["green_growth"]},
                     {"green_growth": "filamentous"})["one_health_notes"] == [])
t("sewage fungus is distinguished from algae, not merged",
  fp.resolve("green_growth", "sewage_fungus")["reading"] == "sewage_fungus")

print("\nTriage ranks by consequence under uncertainty (D-012):")

t("uncertain serious report outranks certain trivial report",
  assess(sparse)["triage"]["score"] > assess(CLEAN)["triage"]["score"])
t("uncertainty RAISES priority on a serious report",
  assess(sparse)["triage"]["score"] > assess(full)["triage"]["score"])

print("\n'Unsure' is a first-class answer, not a gap (D-012):")

c = completeness({**CLEAN, "flow": "unsure"})
t("'unsure' is not counted missing", "flow" not in c["missing"])
t("'unsure' is tracked separately", "flow" in c["marked_unsure"])
t("'unsure' does not reduce answered count", c["answered"] == c["total"])
t("an empty indicator list is an answer, not a gap", "indicators" not in c["missing"])

print("\nPhoto tensions are questions, never verdicts (D-012):")

tn = detected_inconsistency(CLEAN, {"shows_watercourse": True, "appears_turbid": True})
t("photo/answer tension is raised", len(tn) == 1)
t("tension is phrased as a question", tn[0]["question"].endswith("?"))
t("tension offers the innocent reading", "Shade, depth" in tn[0]["question"])

print("\nNothing is accepted, rejected or validated here (D-012):")

a = assess(CLEAN)
t("no single confidence score exists",
  not any("confidence" in k for k in a))
t("four dimensions present",
  all(k in a for k in ("completeness", "detected_inconsistency",
                       "ecological_urgency", "review_status")))
t("defaults to not_reviewed", a["review_status"] == "not_reviewed")
t("output states it is not a validation", "not a validation" in a["disclaimer"])

print("\nNot a WFD classification (D-022 guardrail):")

# Scoped to what the system ASSERTS -- the level and its stated reasons. The
# `note` field is excluded on purpose: it is the disclaimer, and it has to be
# able to say the words "ecological status" in order to disown them.
wfd_words = {"high status", "good status", "moderate status", "poor status",
             "bad status", "ecological status"}
u = assess(full)["ecological_urgency"]
claims = (u["level"] + " " + " ".join(u["reasons"])).lower()
t("WFD status vocabulary is never asserted",
  not any(w in claims for w in wfd_words))
t("urgency explicitly disclaims being a status class",
  "not an ecological status" in assess(full)["ecological_urgency"]["note"].lower())

print("\nAll assessment-contract checks passed.\n")
