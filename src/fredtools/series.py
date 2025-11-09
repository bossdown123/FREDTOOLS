from dataclasses import dataclass
from datetime import date, datetime

from .client import get_current_client
from .releases import Releases
from .types import Observation, ObservationsResult, Release


@dataclass
class SeriesConfig:
    """Configuration for FRED series operations."""

    series_id: str


class Series:
    """Class for FRED series operations."""

    def __init__(
        self,
        series_id: str | None = None
    ) -> None:
        if series_id is not None:
            self._config = SeriesConfig(series_id=series_id)
        else:
            raise ValueError("series_id must be provided")

    def observations(
        self,
        realtime_start: date | None = None,
        realtime_end: date | None = None,
        observation_start: date | None = None,
        observation_end: date | None = None,
        units: str | None = None,
        frequency: str | None = None,
        aggregation_method: str | None = None,
        output_type: int | None = None,
    ) -> ObservationsResult:
        client = get_current_client()

        params = {
            "series_id": self._config.series_id,
            "realtime_start": (
                realtime_start.isoformat() if realtime_start else None
            ),
            "realtime_end": realtime_end.isoformat() if realtime_end else None,
            "observation_start": (
                observation_start.isoformat() if observation_start else None
            ),
            "observation_end": (
                observation_end.isoformat() if observation_end else None
            ),
            "units": units,
            "frequency": frequency,
            "aggregation_method": aggregation_method,
            "output_type": output_type,
        }

        response = client.request("series/observations", params=params)

        def _parse_date(value: str) -> date:
            return datetime.strptime(value, "%Y-%m-%d").date()

        def _parse_value(value: str) -> float:
            if value in ("", "."):
                return float("nan")
            return float(value)

        observations = ObservationsResult(
            Observation(
                realtime_start=_parse_date(observation["realtime_start"]),
                realtime_end=_parse_date(observation["realtime_end"]),
                date=_parse_date(observation["date"]),
                value=_parse_value(observation["value"]),
            )
            for observation in response.get("observations", [])
        )

        return observations

    def release(
        self,
        realtime_start: date | None = None,
        realtime_end: date | None = None,
    ) -> Release:
        releases_client = Releases()
        return releases_client.release(
            series_id=self._config.series_id,
            realtime_start=realtime_start,
            realtime_end=realtime_end,
        )
