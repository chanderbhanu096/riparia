"""Domain layer: field indicators and the differential diagnostics that separate them.

EVERY entry in this file traces to published guidance or peer-reviewed literature,
cited inline next to the logic it justifies (AUDIT.md D-021). Nothing here is
invented. If you cannot cite it, it does not belong in this file.

This module is deliberately isolated from assess.py and from every web concern, so
that a freshwater ecologist can review the project's entire domain content by
reading this one file and nothing else (AUDIT.md Q9).

--------------------------------------------------------------------------------
WHAT THIS MODULE IS NOT
--------------------------------------------------------------------------------
The urgency levels below are TRIAGE categories -- "should a person look at this,
and how soon?" They are NOT ecological status classes.

The EU Water Framework Directive (2000/60/EC) defines five ecological status
classes (High / Good / Moderate / Poor / Bad) derived from biological quality
elements, sampled over time by accredited methods. A single visual report from a
member of the public is not a WFD classification and must never be rendered in
WFD vocabulary. Conflating the two would misrepresent a regulatory instrument
(AUDIT.md D-022).

--------------------------------------------------------------------------------
DESIGN PRECEDENT: ARMI / Riverfly Monitoring Initiative
--------------------------------------------------------------------------------
ARMI is a deployed, proven human-in-the-loop system in UK freshwater citizen
science: >2,000 volunteers across >1,600 sites in 35 regional hubs. Volunteers
take standardised 3-minute kick-samples and score pollution-sensitive
macroinvertebrate taxa. Each site has a "trigger level" set by the regulator;
when a score falls below it, the LOCAL COORDINATOR SCREENS THE RESULT FIRST, and
only then is the Environment Agency notified to investigate. Some investigations
have ended in prosecution.

  Brooks, S.J. et al. (2019) "Anglers' Riverfly Monitoring Initiative (ARMI):
  A UK-wide citizen science project for water quality assessment."
  Freshwater Science 38(2). https://doi.org/10.1086/703397

ARMI works because of two things: a trigger level, and a human screen before
escalation. But it requires TRAINED volunteers doing kick-sampling -- high
barrier, low volume, taxonomic. A low-barrier visual reporting app is the
opposite: untrained, high volume, visual and olfactory. It has neither a trigger
level nor a coordinator screen.

This module supplies the trigger-level equivalent; the review queue supplies the
coordinator screen.
"""

from typing import Any

PROTOCOL_VERSION = "2026-09-15.1"

# -----------------------------------------------------------------------------
# Indicators a member of the public can genuinely observe without equipment.
#
# Scope deliberately excludes anything needing kit or training: no pH, no
# dissolved oxygen, no macroinvertebrate identification. Asking an untrained
# person for those produces confident numbers that are wrong, which is worse
# than no data -- and it is the failure mode ARMI avoids by training people
# properly before trusting a score.
# -----------------------------------------------------------------------------

INDICATORS: dict[str, dict[str, Any]] = {

    "oily_sheen": {
        "label": "An oily, rainbow-coloured film on the surface",
        # Iron-oxidising bacteria are widespread and harmless, and their biofilm
        # is routinely mistaken for a fuel spill. The shatter test is the standard
        # field discriminator: petroleum is cohesive and reforms; bacterial film
        # is brittle and does not.
        #   Minnesota Pollution Control Agency, "Iron bacteria or petroleum?"
        #   Michigan EGLE, naturally occurring phenomena guidance.
        #   Montgomery Parks (2023), iron-oxidising bacteria field guidance.
        "differential": {
            "id": "sheen_shatter_test",
            "question": (
                "Could you gently disturb the film with a stick and tell us what "
                "happens? If it breaks into jagged pieces that stay apart, that is "
                "usually harmless iron bacteria. If it swirls back together into a "
                "continuous sheet, that suggests oil or fuel."
            ),
            "options": {
                "shatters": {
                    "label": "It broke into pieces and stayed apart",
                    "reading": "iron_bacteria",
                    "urgency": "low",
                    "explain": (
                        "Consistent with iron-oxidising bacteria — a natural biofilm, "
                        "common where iron-rich groundwater meets the surface. "
                        "This field answer supports a natural explanation; it does not establish water safety."
                    ),
                },
                "reforms": {
                    "label": "It swirled back together",
                    "reading": "petroleum",
                    "urgency": "high",
                    "explain": (
                        "Consistent with a petroleum product. This is a potential "
                        "pollution incident and should be seen by a reviewer promptly."
                    ),
                },
                "unsure": {
                    "label": "I could not tell, or could not safely reach it",
                    "reading": "undetermined",
                    "urgency": "high",
                    "explain": (
                        "Undetermined. Treated as potentially serious until a person "
                        "has looked — never reach into water you cannot safely reach."
                    ),
                },
            },
        },
    },

    "foam": {
        "label": "Foam on the water",
        # Natural foam arises from dissolved organic carbon released by decomposing
        # plant matter, which acts as a surfactant and lowers surface tension; it
        # concentrates at turbulence such as weirs. Surfactant foam from detergents
        # or industrial discharge presents differently.
        #   Environment Agency, "Foam in rivers and still waters" guidance.
        "differential": {
            "id": "foam_character",
            "question": (
                "What does the foam look like close up? Natural foam from decaying "
                "plants is usually off-white or tea-coloured, light, and gathers "
                "where the water is turbulent. Detergent foam tends to be bright "
                "white, sticky, and lingers."
            ),
            "options": {
                "natural": {
                    "label": "Off-white or brownish, light, near a weir or rapids",
                    "reading": "natural_doc_foam",
                    "urgency": "low",
                    "explain": (
                        "Consistent with natural foam from dissolved organic carbon. "
                        "Normal, and often a sign of a wooded catchment."
                    ),
                },
                "surfactant": {
                    "label": "Bright white, sticky, and it stays around",
                    "reading": "surfactant_foam",
                    "urgency": "high",
                    "explain": (
                        "Consistent with synthetic surfactants — detergents, wash-water "
                        "or industrial discharge. Worth a reviewer's attention."
                    ),
                },
                "unsure": {
                    "label": "I could not tell",
                    "reading": "undetermined",
                    "urgency": "high",
                    "explain": (
                        "Undetermined. Kept at the highest plausible urgency until "
                        "a person looks; uncertainty does not rule out surfactants."
                    ),
                },
            },
        },
    },

    "green_growth": {
        "label": "Green, blue-green or grey growth in or on the water",
        # Three visually similar things with entirely different meanings:
        #   - filamentous green algae: nuisance growth, often nutrient-related
        #   - cyanobacterial scum: paint-like blue-green surface film; produces
        #     toxins; documented dog deaths and human skin/GI illness on exposure
        #   - sewage fungus (Sphaerotilus natans): grey-white filamentous biofilm,
        #     a classic bioindicator of organic loading from sewage or effluent
        #   Angling Trust, "Sewage fungus: a field and microscopic guide" (2024).
        #   Albini et al. (2023), "Early detection and environmental drivers of
        #   sewage fungus outbreaks in rivers", Ecol. Solut. Evid. 4, e12277.
        "differential": {
            "id": "growth_type",
            "question": (
                "Which of these does it look most like? This one matters a lot — "
                "these look similar but mean very different things."
            ),
            "options": {
                "filamentous": {
                    "label": "Long green strands or hair-like mats",
                    "reading": "filamentous_algae",
                    "urgency": "medium",
                    "explain": (
                        "Consistent with filamentous green algae. Often a sign of "
                        "elevated nutrients. This visual reading does not establish water safety."
                    ),
                },
                "cyanobacteria": {
                    "label": "Blue-green, like spilled paint or scum on the surface",
                    "reading": "cyanobacterial_scum",
                    "urgency": "high",
                    "explain": (
                        "Possible cyanobacterial bloom. Blooms can produce toxins "
                        "that affect people and animals, and they can develop and "
                        "disperse within days — so timing matters for a reviewer."
                    ),
                    "one_health": True,
                },
                "sewage_fungus": {
                    "label": "Grey or dirty-white slimy strands coating the bed",
                    "reading": "sewage_fungus",
                    "urgency": "high",
                    "explain": (
                        "Consistent with sewage fungus (Sphaerotilus natans and "
                        "associated biofilm), a well-established indicator of organic "
                        "pollution — typically sewage or industrial effluent. It "
                        "strips oxygen from the water and harms river life."
                    ),
                    "one_health": True,
                },
                "unsure": {
                    "label": "I could not tell",
                    "reading": "undetermined",
                    "urgency": "high",
                    "explain": (
                        "Undetermined. Because a cyanobacterial bloom cannot be ruled "
                        "out from a distance, this is kept high until a person looks."
                    ),
                },
            },
        },
    },

    "pipe_discharge": {
        "label": "A pipe or outfall discharging into the water",
        "differential": None,  # nothing a member of the public can safely resolve
        "urgency": "high",
        "explain": (
            "A visible discharge should be seen by someone who can check whether it "
            "is permitted."
        ),
    },

    "dead_fish": {
        "label": "Dead fish",
        "differential": None,
        "urgency": "high",
        "explain": (
            "A fish kill is time-critical: the cause is often gone from the water "
            "within hours, so a prompt look matters more than a complete report."
        ),
    },

    "sewage_debris": {
        "label": "Sewage-related litter (wet wipes, sanitary items, toilet paper)",
        # Wipe/sanitary debris caught on vegetation is a durable physical marker of
        # a sewage discharge, and persists long after the discharge itself.
        "differential": None,
        "urgency": "high",
        "explain": (
            "Sewage-related debris caught on branches or banks is a physical trace "
            "of a discharge and often outlasts every other sign of one."
        ),
    },

    "smell_sewage": {
        "label": "A sewage or septic smell",
        # Deliberately independent of water clarity. Dissolved sewage produces odour
        # with NO turbidity -- an earlier version of this system treated
        # "clear water + sewage smell" as a contradiction, which was wrong
        # (AUDIT.md D-012, deleted rule 1).
        "differential": None,
        "urgency": "high",
        "explain": "An odour can be the only surface sign of a discharge.",
    },

    "smell_chemical": {
        "label": "A chemical or solvent smell",
        "differential": None,
        "urgency": "high",
        "explain": "Chemical odour suggests an input that should be traced.",
    },

    "erosion": {
        "label": "Crumbling or collapsing banks",
        "differential": None,
        "urgency": "low",
        "explain": (
            "A physical-habitat pressure rather than an incident. Useful for "
            "restoration planning; not urgent."
        ),
    },

    "litter": {
        "label": "General litter",
        "differential": None,
        "urgency": "low",
        "explain": (
            "Amenity and habitat pressure. Useful for prioritising clean-ups; not a "
            "pollution incident on its own."
        ),
    },
}

# Readings that carry a direct human or animal exposure pathway. This is the
# concrete One Health link (AUDIT.md D-022): stream condition -> a specific
# recommended precaution for people and animals. It is deliberately short --
# these are the cases where the evidence for an exposure pathway is strong.
ONE_HEALTH_READINGS = {
    "cyanobacterial_scum": (
        "Keep children and dogs out of the water and off the shoreline until this "
        "has been assessed, and do not let animals drink. Dogs have died after "
        "drinking at affected water."
    ),
    "sewage_fungus": (
        "Indicates organic pollution, typically sewage. Avoid contact with the water "
        "and wash hands after being near it."
    ),
    "petroleum": (
        "Avoid contact with the film and keep animals out of the water."
    ),
}


def differential_for(indicator: str) -> dict[str, Any] | None:
    """The follow-up question for a reported indicator, if one exists.

    Returns None when there is nothing a member of the public could safely or
    reliably resolve -- in which case we ask nothing rather than asking something
    for the sake of it.
    """
    entry = INDICATORS.get(indicator)
    return entry.get("differential") if entry else None


def resolve(indicator: str, option_key: str | None) -> dict[str, Any]:
    """Interpret a reported indicator, and the citizen's differential answer if given.

    With no differential answer, the indicator's own baseline urgency applies. A
    specific citizen answer may narrow the potential consequence. An uncertain
    answer never lowers it; no reading establishes safety or approves a record
    (AUDIT.md D-012).
    """
    entry = INDICATORS.get(indicator)
    if entry is None:
        return {"indicator": indicator, "reading": "unknown", "urgency": "low",
                "explain": "Unrecognised indicator.", "one_health": None}

    diff = entry.get("differential")
    if diff and option_key and option_key in diff["options"]:
        opt = diff["options"][option_key]
        return {
            "indicator": indicator,
            "reading": opt["reading"],
            "urgency": opt["urgency"],
            "explain": opt["explain"],
            "one_health": ONE_HEALTH_READINGS.get(opt["reading"]),
            "resolved_by": "citizen answered the field differential",
        }

    # No differential answer yet. An unresolved indicator that COULD be serious is
    # treated as serious -- consequence under uncertainty (AUDIT.md D-012).
    baseline = entry.get("urgency")
    if baseline is None and diff:
        baseline = max(
            (o["urgency"] for o in diff["options"].values()),
            key=lambda u: {"low": 0, "medium": 1, "high": 2}[u],
        )
    return {
        "indicator": indicator,
        "reading": "unresolved",
        "urgency": baseline or "low",
        "explain": entry.get("explain") or (
            "Reported but not yet narrowed down. Held at the highest reading it "
            "could be until the citizen answers or a reviewer looks."
        ),
        "one_health": None,
        "resolved_by": None,
    }
