"""Configuration, resolved once, in one place.

Environment variables win over the local .env file. In production these arrive as
Azure App Service Settings; the .env is a development convenience and is
gitignored, so no credential is ever committed or baked into a build artefact.
"""

import os
import pathlib

_ENV_PATH = pathlib.Path(__file__).parent / ".env"

AZURE_KEYS = ("AZURE_AI_ENDPOINT", "AZURE_AI_DEPLOYMENT", "AZURE_AI_API_VERSION",
              "AZURE_AI_KEY")


def _dotenv() -> dict[str, str]:
    if not _ENV_PATH.exists():
        return {}
    return dict(
        line.split("=", 1)
        for line in _ENV_PATH.read_text().splitlines()
        if "=" in line and not line.startswith("#")
    )


def get(key: str, default: str | None = None) -> str | None:
    return os.environ.get(key) or _dotenv().get(key) or default


def azure_vision() -> dict[str, str] | None:
    """Azure AI Foundry settings, or None if not fully configured.

    None is a normal, supported state -- the null vision provider takes over and
    the system runs complete without any model (AUDIT.md A4).
    """
    cfg = {k: get(k) for k in AZURE_KEYS}
    return cfg if all(cfg.values()) else None


# Which vision provider to use. "auto" picks Azure when configured and the null
# provider otherwise. Set VISION_PROVIDER=null to force the offline path -- useful
# for demonstrating the degraded state on purpose.
VISION_PROVIDER = get("VISION_PROVIDER", "auto")
