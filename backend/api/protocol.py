"""The observation protocol the citizen form is built from."""

from typing import Any

from fastapi import APIRouter

from adapters import vision
from domain import field_protocol as fp

router = APIRouter(prefix="/api", tags=["protocol"])


@router.get("/protocol")
def protocol() -> dict[str, Any]:
    """Served from the domain layer so ecological content has exactly one home.

    The frontend renders whatever this returns and holds no domain knowledge of
    its own, which is also what lets a freshwater ecologist review the entire
    domain content by reading one file (AUDIT.md Q9).
    """
    return {
        "indicators": [
            {"key": k, "label": v["label"], "has_differential": bool(v.get("differential"))}
            for k, v in fp.INDICATORS.items()
        ],
        "vision_provider": vision.active_provider(),
        "note": (
            "Indicators are limited to what a person can observe without equipment "
            "or training. Nothing here requires a test kit or species identification."
        ),
    }
