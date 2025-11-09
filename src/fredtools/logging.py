"""Lightweight logging utilities for fredtools."""

from __future__ import annotations

import logging
import os

_LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"
_DEFAULT_LEVEL_NAME = os.getenv("FREDTOOLS_LOG_LEVEL", "WARNING")


def _coerce_level(level: str | int | None = None) -> int:
    """Convert a textual/numeric log level into the logging module constant."""
    value: str | int | None = level or _DEFAULT_LEVEL_NAME
    if isinstance(value, int):
        return value
    resolved = logging.getLevelName(value.upper())
    if isinstance(resolved, int):
        return resolved
    raise ValueError(f"Unsupported log level: {value!r}")


def configure_logging(
    level: str | int | None = None,
    *,
    fmt: str | None = None,
    handler: logging.Handler | None = None,
) -> logging.Logger:
    """Configure the root fredtools logger (idempotent)."""
    logger = logging.getLogger("fredtools")
    logger.setLevel(_coerce_level(level))
    if logger.handlers:
        logger.handlers = [
            existing
            for existing in logger.handlers
            if not isinstance(existing, logging.NullHandler)
        ]
    active_handler = handler or logging.StreamHandler()
    formatter = logging.Formatter(fmt or _LOG_FORMAT)
    active_handler.setFormatter(formatter)
    if active_handler not in logger.handlers:
        logger.addHandler(active_handler)
    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    """Return a logger in the fredtools namespace."""
    if not name:
        return logging.getLogger("fredtools")
    if name.startswith("fredtools"):
        return logging.getLogger(name)
    return logging.getLogger(f"fredtools.{name}")


def log_requests(level: str | int = "INFO") -> logging.Logger:
    """One-liner to log every client request at the chosen level."""
    configure_logging(level=level)
    client_logger = logging.getLogger("fredtools.client")
    client_logger.setLevel(_coerce_level(level))
    return client_logger


logging.getLogger("fredtools").addHandler(logging.NullHandler())

__all__ = ["configure_logging", "get_logger", "log_requests"]
