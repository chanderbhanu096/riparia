"""Helpers shared across routers."""

import pathlib
import config
from domain.records import differentials_from

UPLOADS = (config.DATA_DIR / "uploads" if config.DATA_DIR else
           pathlib.Path(__file__).parent.parent / "uploads")
UPLOADS.mkdir(parents=True, exist_ok=True)
