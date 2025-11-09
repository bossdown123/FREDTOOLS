from __future__ import annotations

import logging

import pytest

from fredtools import logging as fred_logging


def test_coerce_level_accepts_strings_and_ints() -> None:
    assert fred_logging._coerce_level("info") == logging.INFO
    assert fred_logging._coerce_level(logging.DEBUG) == logging.DEBUG


def test_coerce_level_rejects_invalid_values() -> None:
    with pytest.raises(ValueError):
        fred_logging._coerce_level("not-a-level")


def test_configure_logging_sets_level_and_handler() -> None:
    logger = fred_logging.configure_logging(level="DEBUG")
    try:
        assert logger.level == logging.DEBUG
        assert any(not isinstance(h, logging.NullHandler) for h in logger.handlers)
    finally:
        for handler in list(logger.handlers):
            logger.removeHandler(handler)


def test_get_logger_prefixes_non_namespace_names() -> None:
    prefixed = fred_logging.get_logger("fredtools.series")
    external = fred_logging.get_logger("series")
    assert prefixed.name == "fredtools.series"
    assert external.name == "fredtools.series"


def test_log_requests_sets_level_on_client_logger() -> None:
    logger = fred_logging.log_requests(level="INFO")
    try:
        client_logger = logging.getLogger("fredtools.client")
        assert client_logger.level == logging.INFO
        assert logger.level == logging.INFO
    finally:
        for handler in list(logger.handlers):
            logger.removeHandler(handler)
