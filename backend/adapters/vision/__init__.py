"""Vision providers.

One narrow interface, one function:

    analyse(photo_path) -> (findings | None, status)

status is "ok" | "unavailable" | "no_photo". Findings are tri-state and advisory
only -- see providers for why that constraint is absolute.

Adding a provider is one file plus one branch in `_provider()`. Nothing in
domain/ or api/ changes.
"""

import pathlib
from typing import Any

import config

from . import null


def _provider():
    if config.VISION_PROVIDER == "null":
        return null
    if config.azure_vision() is not None:
        from . import azure_openai
        return azure_openai
    return null


def analyse(photo_path: pathlib.Path | None, timeout: float = 20.0
            ) -> tuple[dict[str, Any] | None, str]:
    """Run the configured provider. Never raises -- a model problem must never
    cost a citizen their observation (AUDIT.md A4)."""
    if photo_path is None or not photo_path.exists():
        return None, "no_photo"
    try:
        return _provider().analyse(photo_path, timeout)
    except Exception:
        return None, "unavailable"


def active_provider() -> str:
    return _provider().NAME
