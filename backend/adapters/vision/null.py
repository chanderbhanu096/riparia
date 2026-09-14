"""The offline provider. Always available; never analyses anything.

This is not a stub awaiting a real implementation. It is the degraded path the
whole system was built on first, so that a model outage is an ordinary, daily
exercised state rather than an emergency (AUDIT.md A4, D-013).
"""

import pathlib
from typing import Any

NAME = "null"


def analyse(photo_path: pathlib.Path, timeout: float = 20.0
            ) -> tuple[dict[str, Any] | None, str]:
    return None, "unavailable"
