"""FRED Tools package."""

from .client import Fred, FredConfig
from .series import Series
from .types import Observation, ObservationsResult
from .releases import Release
from .categories import Category
from .tags import Tag
__all__ = [
    "__version__", "Fred", "FredConfig", "Series", "Observation",
    "Category", "Release", "ObservationsResult", "Tag"
    ]
__version__ = "0.1.0"
