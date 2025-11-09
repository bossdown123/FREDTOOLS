from __future__ import annotations

from datetime import date

import pytest

from fredtools.releases import Release
from fredtools.types import ReleaseTable, Source
from tests.conftest import StubResponse


def make_release_instance() -> Release:
    return Release(
        release_id=53,
        name="Sample",
        realtime_start=date(2020, 1, 1),
        realtime_end=date(2020, 1, 2),
    )


def test_release_init_requires_identifier() -> None:
    with pytest.raises(ValueError):
        Release()


def test_release_init_invokes_info_when_metadata_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    called: dict[str, bool] = {"called": False}

    def fake_info(self: Release) -> Release:
        called["called"] = True
        self.name = "Loaded"
        return self

    monkeypatch.setattr(Release, "info", fake_info)
    Release(release_id=1)
    assert called["called"] is True


def test_release_info_fetches_and_updates(make_stub_client) -> None:
    payload = {
        "id": 53,
        "name": "Updated",
        "realtime_start": "2020-01-01",
        "realtime_end": "2020-01-31",
    }
    def assert_params(params):
        assert params is not None
        assert params["release_id"] == 53

    stub = make_stub_client(
        [
            StubResponse(
                "release",
                {"releases": [payload]},
                assert_params=assert_params,
            )
        ]
    )
    release = Release(release_id=53, name="Original")
    info = release.info()
    assert release.name == "Updated"
    assert info.release_id == 53
    stub.assert_complete()


def test_release_all_returns_release_instances(make_stub_client) -> None:
    response = {
        "releases": [
            {
                "id": 1,
                "name": "R1",
                "realtime_start": "2020-01-01",
                "realtime_end": "2020-01-02",
                "press_release": False,
                "link": "http://example.com/r1",
            }
        ]
    }
    stub = make_stub_client([StubResponse("releases", response)])
    release = make_release_instance()
    result = release.all(order_by="name")
    assert len(result) == 1
    assert isinstance(result[0], Release)
    assert result[0].name == "R1"
    stub.assert_complete()


def test_release_dates_returns_date_list(make_stub_client) -> None:
    response = {"release_dates": ["2020-01-01", "2020-01-15"]}
    stub = make_stub_client([StubResponse("release/dates", response)])
    release = make_release_instance()
    dates = release.dates()
    assert dates == [date(2020, 1, 1), date(2020, 1, 15)]
    stub.assert_complete()


def test_release_all_dates_returns_date_list(make_stub_client) -> None:
    response = {"release_dates": ["2021-02-03"]}
    stub = make_stub_client([StubResponse("releases/dates", response)])
    release = make_release_instance()
    dates = release.all_dates()
    assert dates == [date(2021, 2, 3)]
    stub.assert_complete()


def test_release_series_returns_series_objects(make_stub_client) -> None:
    response = {
        "seriess": [
            {
                "series_id": "S1",
                "title": "Series 1",
                "realtime_start": "2020-01-01",
                "realtime_end": "2020-01-02",
            }
        ]
    }
    stub = make_stub_client([StubResponse("release/series", response)])
    release = make_release_instance()
    series = release.series(limit=1)
    assert len(series) == 1
    assert series[0].series_id == "S1"
    stub.assert_complete()


def test_release_sources_returns_source_dataclasses(make_stub_client) -> None:
    response = {
        "sources": [
            {
                "id": 9,
                "name": "Bureau",
                "realtime_start": date(2020, 1, 1),
                "realtime_end": date(2020, 1, 2),
                "link": "https://example.com",
            }
        ]
    }
    stub = make_stub_client([StubResponse("release/sources", response)])
    release = make_release_instance()
    sources = release.sources()
    assert isinstance(sources[0], Source)
    assert sources[0].name == "Bureau"
    stub.assert_complete()


def test_release_tags_and_related_tags(make_stub_client) -> None:
    tags_payload = {
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
    stub = make_stub_client(
        [
            StubResponse("release/tags", tags_payload),
            StubResponse("release/related_tags", tags_payload),
        ]
    )
    release = make_release_instance()
    tags = release.tags(tag_names=["macro"])
    related = release.related_tags(exclude_tag_names=["micro"])
    assert tags[0].name == "macro"
    assert related[0].name == "macro"
    stub.assert_complete()


def test_release_table_fetches_and_parses(make_stub_client) -> None:
    response = {
        "name": "Parent",
        "element_id": 12886,
        "release_id": "53",
        "elements": {
            "12886": {
                "element_id": 12886,
                "release_id": 53,
                "series_id": None,
                "parent_id": None,
                "line": "3",
                "type": "section",
                "name": "Root",
                "level": "0",
                "children": [
                    {
                        "element_id": 12887,
                        "release_id": 53,
                        "series_id": "S1",
                        "parent_id": 12886,
                        "line": "4",
                        "type": "series",
                        "name": "Goods",
                        "level": "1",
                        "children": [],
                    }
                ],
            }
        },
    }

    def assert_params(params):
        assert params is not None
        assert params["element_id"] == 12886
        assert params["include_observation_values"] is None

    stub = make_stub_client(
        [StubResponse("release/tables", response, assert_params=assert_params)]
    )
    release = make_release_instance()
    table = release.table(element_id=12886)
    assert isinstance(table, ReleaseTable)
    assert table.elements[0].children[0].name == "Goods"
    stub.assert_complete()


def test_release_table_sets_include_values_flag(make_stub_client) -> None:
    response = {
        "element_id": 1,
        "release_id": 53,
        "elements": {
            "1": {
                "element_id": 1,
                "release_id": 53,
                "series_id": "S1",
                "parent_id": None,
                "line": "1",
                "type": "series",
                "name": "Top",
                "level": "0",
                "children": [],
            }
        },
    }

    def assert_params(params):
        assert params is not None
        assert params["include_observation_values"] == 1

    stub = make_stub_client(
        [StubResponse("release/tables", response, assert_params=assert_params)]
    )
    make_release_instance().table(element_id=1, include_observation_values=True)
    stub.assert_complete()


def test_release_table_raises_when_missing_elements(make_stub_client) -> None:
    stub = make_stub_client(
        [StubResponse("release/tables", {"elements": {}})]
    )
    release = make_release_instance()
    with pytest.raises(ValueError):
        release.table(element_id=1)
    stub.assert_complete()


def test_parse_release_table_handles_missing_root() -> None:
    data = {
        "element_id": None,
        "release_id": "10",
        "elements": {
            "1": {
                "element_id": 1,
                "release_id": 10,
                "series_id": "A",
                "parent_id": None,
                "line": "1",
                "type": "series",
                "name": "Top",
                "level": "0",
                "children": [],
            }
        },
    }
    table = Release._parse_release_table(data)
    assert table.release_id == 10
    assert table.elements[0].name == "Top"


def test_coerce_int_accepts_strings_and_floats() -> None:
    assert Release._coerce_int("5") == 5
    assert Release._coerce_int(7.0) == 7
    assert Release._coerce_int(None) is None


def test_coerce_int_rejects_invalid_values() -> None:
    with pytest.raises(ValueError):
        Release._coerce_int("abc")


def test_release_repr_includes_key_fields() -> None:
    release = make_release_instance()
    text = repr(release)
    assert "Sample" in text and "53" in text
