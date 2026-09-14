"""Canonical copy for every design artboard.

Every string here is lifted VERBATIM from backend/domain/field_protocol.py, so the
mockups say exactly what the product says. Artboards are generated from this one
dict: design is then the only variable between them, which is the entire premise
of putting them side by side.

A review of the first draft found the safety instruction had drifted into FOUR
different versions across four artboards -- one dropped "and off the shoreline",
another added "do not let animals drink", two dropped the lead-in. That is how
protective advice quietly becomes a design detail. It cannot happen again from
here: there is one string and everything reads it.
"""

COPY = {
    "brand": "RIPARIA",
    "site": "Mondego tributary, by the footbridge",

    "prompt_kicker": "While you're still there",
    "question": "Which of these does it look most like?",
    "question_sub": (
        "These look similar and mean very different things. "
        "You are standing there and we are not."
    ),

    # field_protocol.INDICATORS["green_growth"]["differential"]["options"]
    "opt1": "Long green strands or hair-like mats",
    "opt1_name": "Filamentous algae",
    "opt2": "Blue-green, like spilled paint or scum on the surface",
    "opt2_name": "Cyanobacterial scum",
    "opt3": "Grey or dirty-white slimy strands coating the bed",
    "opt3_name": "Sewage fungus",

    "reading_label": "Possible cyanobacterial bloom",
    # ...["cyanobacteria"]["explain"]
    "reading": (
        "Blooms can produce toxins that affect people and animals, and they can "
        "develop and disperse within days — so timing matters for a reviewer."
    ),

    "precaution_label": "For you and anyone with you",
    # ONE_HEALTH_READINGS["cyanobacterial_scum"] -- safety copy, never trimmed
    "precaution": (
        "Keep children and dogs out of the water and off the shoreline until this "
        "has been assessed, and do not let animals drink. Dogs have died after "
        "drinking at affected water."
    ),

    "footer": "Recorded and sent for human review. Nothing here is decided automatically.",
}
