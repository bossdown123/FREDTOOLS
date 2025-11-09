"""FRED Tools package."""

from .client import Fred, FredConfig
from .series import Series
from .types import Observation, ObservationsResult, Release

__all__ = ["__version__", "Fred", "FredConfig", "Series", "Observation", "ObservationsResult", "Release"]
__version__ = "0.1.0"
