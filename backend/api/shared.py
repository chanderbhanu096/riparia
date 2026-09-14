"""Helpers shared across routers."""

import pathlib
from typing import Any

UPLOADS = pathlib.Path(__file__).parent.parent / "uploads"
UPLOADS.mkdir(exist_ok=True)


def differentials_from(rec: dict[str, Any]) -> dict[str, str]:
    """Rebuild the citizen's differential answers from the clarification log.

    Derived, never stored twice: the clarification log is the record and this is a
    read of it. That keeps original answers immutable (AUDIT.md D-012) while still
    letting the assessment reflect what the citizen said afterwards.
    """
    out: dict[str, str] = {}
    for c in rec.get("clarifications", []):
        if c.get("indicator") and c.get("option_key"):
            out[c["indicator"]] = c["option_key"]
    return out
