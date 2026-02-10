from __future__ import annotations

from datetime import date

import pytest

from fredtools.series import Series
from tests.conftest import StubResponse


def make_series() -> Series:
    return Series(
        series_id="S1",
        title="Series 1",
        realtime_start=date(2020, 1, 1),
        realtime_end=date(2020, 1, 2),
        observation_start=date(2020, 1, 1),
    )


def test_series_init_requires_identifier() -> None:
    with pytest.raises(ValueError):
        Series()


def test_series_init_invokes_info_when_metadata_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    called = {"count": 0}

    def fake_info(self: Series) -> Series:
        called["count"] += 1
        self.title = "Loaded"
        return self

    monkeypatch.setattr(Series, "info", fake_info)
    Series(series_id="S1", title=None, realtime_start=None, realtime_end=None, observation_start=None)
    assert called["count"] == 1


def test_series_categories_returns_category_instances(make_stub_client) -> None:
    response = {
        "categories": [
            {"id": 2, "name": "Category", "parent_id": 1},
        ]
    }
    stub = make_stub_client([StubResponse("series/categories", response)])
    result = make_series().categories()
    assert result[0].name == "Category"
    stub.assert_complete()


def test_series_observations_parses_values(make_stub_client) -> None:
    response = {
        "observations": [
            {
                "realtime_start": "2020-01-01",
                "realtime_end": "2020-01-02",
                "date": "2020-01-15",
                "value": "1.5",
            }
        ]
    }
    stub = make_stub_client([StubResponse("series/observations", response)])
    observations = make_series().observations()
    assert observations[0].value == 1.5
    assert observations[0].date == date(2020, 1, 15)
    stub.assert_complete()


def test_series_release_returns_release(make_stub_client) -> None:
    response = {
        "releases": [
            {
                "id": 10,
                "name": "Release",
                "realtime_start": date(2020, 1, 1),
                "realtime_end": date(2020, 1, 2),
            }
        ]
    }
    stub = make_stub_client([StubResponse("series/release", response)])
    release = make_series().release()
    assert release.release_id == 10
    stub.assert_complete()


def test_series_release_raises_when_missing(make_stub_client) -> None:
    stub = make_stub_client([StubResponse("series/release", {"releases": []})])
    with pytest.raises(RuntimeError):
        make_series().release()
    stub.assert_complete()


def test_series_search_returns_series(make_stub_client) -> None:
    response = {
        "seriess": [
            {
                "series_id": "S2",
                "title": "Other",
                "realtime_start": date(2020, 1, 1),
                "realtime_end": date(2020, 1, 2),
            }
        ]
    }
    stub = make_stub_client([StubResponse("series/search", response)])
    result = Series.search("gdp", tag_names=["macro"])
    assert result[0].series_id == "S2"
    stub.assert_complete()


def test_series_search_tags_returns_tags(make_stub_client) -> None:
    response = {
        "tags": [
            {
                "name": "macro",
                "group_id": 1,
                "notes": "Macro",
                "created": date(2020, 1, 1),
                "popularity": 10,
                "series_count": 5,
            }
        ]
    }
    stub = make_stub_client([StubResponse("series/search/tags", response)])
    tags = Series.search_tags("gdp", tag_names=["macro"])
    assert tags[0].name == "macro"
    stub.assert_complete()


def test_series_search_related_tags_returns_tags(make_stub_client) -> None:
    response = {
        "tags": [
            {
                "name": "related",
                "group_id": 2,
                "notes": "Related",
                "created": date(2020, 1, 2),
                "popularity": 5,
                "series_count": 2,
            }
        ]
    }
    stub = make_stub_client([StubResponse("series/search/related_tags", response)])
    tags = Series.search_related_tags("gdp", tag_names=["macro"])
    assert tags[0].name == "related"
    stub.assert_complete()


def test_series_tags_returns_tags(make_stub_client) -> None:
    response = {
        "tags": [
            {
                "name": "macro",
                "group_id": 1,
                "notes": "Macro",
                "created": date(2020, 1, 1),
                "popularity": 10,
                "series_count": 5,
            }
        ]
    }
    stub = make_stub_client([StubResponse("series/tags", response)])
    tags = make_series().tags(order_by="popularity")
    assert tags[0].name == "macro"
    stub.assert_complete()


def test_series_updates_returns_series(make_stub_client) -> None:
    response = {
        "seriess": [
            {
                "series_id": "S3",
                "title": "Updated",
                "realtime_start": date(2020, 2, 1),
                "realtime_end": date(2020, 2, 2),
            }
        ]
    }
    stub = make_stub_client([StubResponse("series/updates", response)])
    updates = make_series().updates(filter_value="macro")
    assert updates[0].series_id == "S3"
    stub.assert_complete()


def test_series_vintage_dates_returns_dates(make_stub_client) -> None:
    response = {"vintage_dates": ["2020-03-01", "2020-03-15"]}
    stub = make_stub_client([StubResponse("series/vintagedates", response)])
    dates = make_series().vintage_dates(sort_order="asc")
    assert dates == [date(2020, 3, 1), date(2020, 3, 15)]
    stub.assert_complete()


def test_series_info_updates_fields(make_stub_client) -> None:
    response = {
        "seriess": [
            {
                "id": "S1",
                "title": "Updated",
                "realtime_start": date(2020, 5, 1),
                "realtime_end": date(2020, 6, 1),
                "observation_start": date(2020, 1, 1),
                "observation_end": date(2020, 12, 31),
                "frequency": "Monthly",
                "frequency_short": "M",
                "units": "Index",
                "units_short": "Idx",
                "seasonal_adjustment": "SA",
                "seasonal_adjustment_short": "SA",
                "last_updated": date(2020, 7, 1),
                "popularity": 50,
                "notes": "Updated notes",
            }
        ]
    }
    stub = make_stub_client([StubResponse("series", response)])
    series = make_series()
    series.info()
    assert series.title == "Updated"
    assert series.frequency == "Monthly"
    stub.assert_complete()


def test_series_repr_and_str_include_fields() -> None:
    series = make_series()
    assert "Series(series_id=S1" in repr(series)
    assert "Series ID: S1" in str(series)
