from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from .client import get_current_client
from .releases import Release
from .tags import stringify_tags
from .types import Observation, ObservationsResult

if TYPE_CHECKING:
    from .categories import Category
    from .tags import Tag


class Series:
    """Class for FRED series operations."""

    def __init__(self, series_id: str | None = None, **kwargs) -> None:
        if not series_id and not kwargs.get("id"):
            raise ValueError("Either series_id or series_id must be provided")
        self.series_id: str | None = series_id or kwargs.get("id")
        self.realtime_start: date | None = kwargs.get("realtime_start")
        self.realtime_end: date | None = kwargs.get("realtime_end")
        self.title: str | None = kwargs.get("title")
        self.observation_start: date | None = kwargs.get("observation_start")
        self.observation_end: date | None = kwargs.get("observation_end")
        self.frequency: str | None = kwargs.get("frequency")
        self.frequency_short: str | None = kwargs.get("frequency_short")
        self.units: str | None = kwargs.get("units")
        self.units_short: str | None = kwargs.get("units_short")
        self.seasonal_adjustment: str | None = kwargs.get("seasonal_adjustment")
        self.seasonal_adjustment_short: str | None = kwargs.get("seasonal_adjustment_short")
        self.last_updated: date | None = kwargs.get("last_updated")
        self.popularity: int | None = kwargs.get("popularity")
        self.notes: str | None = kwargs.get("notes")
        if not self.realtime_start and not self.realtime_end and not self.title and not self.observation_start:
            self.info()

    def categories(
        self,
        realtime_start: date | None = None,
        realtime_end: date | None = None,
    ) -> list["Category"]:
        from .categories import Category

        client = get_current_client()
        response = client.request("series/categories", params={"series_id": self.series_id})
        return [Category(**category) for category in response.get("categories", [])]

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
            "series_id": self.series_id,
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
        client = get_current_client()

        params = {
            "series_id": self.series_id,
            "realtime_start": (
                realtime_start.isoformat() if realtime_start else None
            ),
            "realtime_end": (
                realtime_end.isoformat() if realtime_end else None
            ),
        }

        response = client.request("series/release", params=params)
        releases = response.get("releases", [])
        if not releases:
            raise RuntimeError(
                f"No release metadata returned for series_id='{self.series_id}'."
            )

        release_data = releases[0]
        release = Release(**release_data)
        return release
    
    @staticmethod
    def search(
        search_text: str,
        search_type: str | None = None,
        realtime_start: date | None = None,
        realtime_end: date | None = None,
        limit: int | None = None,
        offset: int | None = None,
        order_by: str | None = None,
        sort_order: str | None = None,
        filter_variable: str | None = None,
        filter_value: str | None = None,
        tag_names: list[str] | list["Tag"] | None = None,
        exclude_tag_names: list[str] | None = None,
    ) -> list["Series"]:
        client = get_current_client()

        params = {
            "search_text": search_text,
            "search_type": search_type,
            "realtime_start": realtime_start,
            "realtime_end": realtime_end,
            "limit": limit,
            "offset": offset,
            "order_by": order_by,
            "sort_order": sort_order,
            "filter_variable": filter_variable,
            "filter_value": filter_value,
            "tag_names": ";".join(tag_names) if tag_names else None,
            "exclude_tag_names": ";".join(exclude_tag_names) if exclude_tag_names else None,
        }

        response = client.request("series/search", params=params).get("seriess", [])
        return [Series(**ser) for ser in response]
    
    @staticmethod
    def search_tags(
        series_search_text: str,
        realtime_start: date | None = None,
        realtime_end: date | None = None,
        tag_names: list[str] | None = None,
        tag_group_id: int | None = None,
        # url encode the search text
        tag_search_text: str | None = None,
    ) -> list["Tag"]:
        from .tags import Tag

        client = get_current_client()

        params = {
            "series_search_text": series_search_text,
            "realtime_start": realtime_start,
            "realtime_end": realtime_end,
            "tag_names": stringify_tags(tag_names),
            "tag_group_id": tag_group_id,
            "tag_search_text": tag_search_text
        }
    
        response = client.request("series/search/tags", params=params).get("tags", [])
        print(response)
        return [Tag(**tag) for tag in response]

    @staticmethod
    def search_related_tags(
        series_search_text: str,
        realtime_start: date | None = None,
        realtime_end: date | None = None,
        tag_names: list[str] | list["Tag"] | None = None,
        exclude_tag_names: list[str] | list["Tag"] | None = None,
        tag_group_id: int | None = None,
        tag_search_text: str | None = None,
    ) -> list["Tag"]:
        from .tags import Tag

        client = get_current_client()

        params = {
            "series_search_text": series_search_text,
            "realtime_start": realtime_start,
            "realtime_end": realtime_end,
            "tag_names": stringify_tags(tag_names),
            "exclude_tag_names": stringify_tags(exclude_tag_names),
            "tag_group_id": tag_group_id,
            "tag_search_text": tag_search_text
        }

        response = client.request("series/search/related_tags", params=params).get("tags", [])
        return [Tag(**tag) for tag in response]
    
    def tags(
        self,
        realtime_start: date | None = None,
        realtime_end: date | None = None,
        order_by: str | None = None,
        sort_order: str | None = None
    ) -> list["Tag"]:
        from .tags import Tag

        client = get_current_client()

        params = {
            "series_id": self.series_id,
            "realtime_start": realtime_start,
            "realtime_end": realtime_end,
            "order_by": order_by,
            "sort_order": sort_order,
        }

        response = client.request("series/tags", params=params).get("tags", [])
        return [Tag(**tag) for tag in response]

    def updates(
        self,
        realtime_start: date | None = None,
        realtime_end: date | None = None,
        filter_value: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> list[Series]:
        client = get_current_client()

        params = {
            "series_id": self.series_id,
            "realtime_start": realtime_start,
            "realtime_end": realtime_end,
            "filter_value": filter_value,
            "start_time": start_time.isoformat() if start_time else None,
            "end_time": end_time.isoformat() if end_time else None,
        }

        response = client.request("series/updates", params=params).get("seriess", [])
        return [Series(**ser) for ser in response]
    
    def vintage_dates(
        self,
        realtime_start: date | None = None,
        realtime_end: date | None = None,
        sort_order: str | None = None
    ) -> list[date]:
        client = get_current_client()

        params = {
            "series_id": self.series_id,
            "realtime_start": realtime_start,
            "realtime_end": realtime_end,
            "sort_order": sort_order,
        }

        response = client.request("series/vintagedates", params=params).get(
            "vintage_dates", []
        )
        return [
            datetime.strptime(vintage_date, "%Y-%m-%d").date()
            for vintage_date in response
        ]
    
    def info(self) -> Series:
        client = get_current_client()

        params = {
            "series_id": self.series_id,
        }

        response = client.request("series", params=params).get("seriess", [])
        if not response:
            raise ValueError(f"No series found with id {self.series_id}")
        series = Series(**response[0])
        self.realtime_start = series.realtime_start
        self.realtime_end = series.realtime_end
        self.title = series.title
        self.observation_start = series.observation_start
        self.observation_end = series.observation_end
        self.frequency = series.frequency
        self.frequency_short = series.frequency_short
        self.units = series.units
        self.units_short = series.units_short
        self.seasonal_adjustment = series.seasonal_adjustment
        self.seasonal_adjustment_short = series.seasonal_adjustment_short
        self.last_updated = series.last_updated
        self.popularity = series.popularity
        self.notes = series.notes
        return series

    def __repr__(self) -> str:
        return f"Series(series_id={self.series_id}, title={self.title})"

    def __str__(self) -> str:
        return f"Series ID: {self.series_id}, Title: {self.title} \n" \
               f"Observation Start: {self.observation_start}, Observation End: {self.observation_end} \n" \
               f"Frequency: {self.frequency}, Units: {self.units}"
    
