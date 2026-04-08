"""Application-wide logging setup (env: LOG_LEVEL, default INFO)."""

from __future__ import annotations

import logging
import os


def configure_logging() -> None:
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(level=level, format=fmt, datefmt=datefmt, force=True)

    # Quieter access logs unless debugging
    logging.getLogger("uvicorn.access").setLevel(
        logging.INFO if level <= logging.DEBUG else logging.WARNING
    )
