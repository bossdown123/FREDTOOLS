from dataclasses import asdict, dataclass
from datetime import date
from typing import Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd



@dataclass
class Release:
    """Represents a FRED release."""

    id: int
    realtime_start: date
    realtime_end: date
    name: str
    press_release: bool
    link: str



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
