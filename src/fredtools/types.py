from dataclasses import asdict, dataclass, field
from datetime import date
from typing import Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


@dataclass
class Source:
    """Represents a data source in FRED."""

    id: int
    name: str
    realtime_start: date
    realtime_end: date
    link: str


@dataclass
class ReleaseTableElement:
    """Represents a single element within a release table hierarchy."""

    element_id: int
    release_id: int
    series_id: str | None
    parent_id: int | None
    line: str | None
    type: str
    name: str
    level: int | None
    children: list["ReleaseTableElement"] = field(default_factory=list)


@dataclass
class ReleaseTable:
    """Represents a release table with nested elements."""

    name: str | None
    element_id: int | None
    release_id: int | None
    elements: list[ReleaseTableElement] = field(default_factory=list)


@dataclass
class Observation:
    """Represents a single observation in a FRED series."""

    realtime_start: date
    realtime_end: date

    date: date
    value: float


class ObservationsResult(list[Observation]):
    """List-like collection that exposes pandas conveniences."""

    def __init__(self, observations: Iterable[Observation]) -> None:
        super().__init__(observations)

    @property
    def df(self) -> "pd.DataFrame":
        try:
            import pandas as pd
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError(
                "pandas is required to access .df. Install it with "
                "`pip install pandas`."
            ) from exc
        return pd.DataFrame([asdict(observation) for observation in self])
