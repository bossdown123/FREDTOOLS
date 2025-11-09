from __future__ import annotations

from datetime import date

import pytest

from fredtools.tags import Tag, stringify_tags
from tests.conftest import StubResponse


def make_tag() -> Tag:
    return Tag(name="macro", group_id=1, notes="Macro", created=date(2020, 1, 1), popularity=10, series_count=5)


def test_tag_init_invokes_info_when_incomplete(monkeypatch: pytest.MonkeyPatch) -> None:
    called = {"count": 0}

    def fake_info(self: Tag) -> Tag:
        called["count"] += 1
        self.group_id = 1
        return self

    monkeypatch.setattr(Tag, "info", fake_info)
    Tag(name="macro")
    assert called["count"] == 1


def test_tag_series_uses_self_name(make_stub_client) -> None:
    response = {
        "seriess": [
            {
                "series_id": "S1",
                "title": "Series",
                "realtime_start": date(2020, 1, 1),
                "realtime_end": date(2020, 1, 2),
            }
        ]
    }
    stub = make_stub_client([StubResponse("tags/series", response)])
    result = make_tag().series()
    assert result[0].series_id == "S1"
    stub.assert_complete()


def test_tag_search_returns_tags(make_stub_client) -> None:
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
    stub = make_stub_client([StubResponse("tags/search", response)])
    result = make_tag().search("macro")
    assert result[0].name == "macro"
    stub.assert_complete()


def test_tag_related_tags_returns_tags(make_stub_client) -> None:
    response = {
        "tags": [
            {
                "name": "related",
                "group_id": 2,
                "notes": "Related",
                "created": date(2020, 2, 2),
                "popularity": 5,
                "series_count": 3,
            }
        ]
    }
    stub = make_stub_client([StubResponse("tag/related_tags", response)])
    related = make_tag().related_tags()
    assert related[0].name == "related"
    stub.assert_complete()


def test_tag_all_returns_tags(make_stub_client) -> None:
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
    stub = make_stub_client([StubResponse("tags", response)])
    result = make_tag().all()
    assert result[0].name == "macro"
    stub.assert_complete()


def test_tag_info_populates_fields(make_stub_client) -> None:
    response = {
        "tags": [
            {
                "name": "macro",
                "group_id": 3,
                "notes": "Updated",
                "created": date(2020, 3, 3),
                "popularity": 12,
                "series_count": 7,
            }
        ]
    }
    stub = make_stub_client([StubResponse("tags", response)])
    tag = Tag(name="macro", group_id=1, notes="Old", created=date(2020, 1, 1), popularity=1, series_count=1)
    tag.info()
    assert tag.group_id == 3
    assert tag.notes == "Updated"
    stub.assert_complete()


def test_tag_repr_contains_fields() -> None:
    text = repr(make_tag())
    assert "macro" in text and "group_id=1" in text


def test_stringify_tags_handles_mixed_inputs() -> None:
    t = make_tag()
    assert stringify_tags(["a", "b"]) == "a;b"
    assert stringify_tags([t, "b"]) == "macro;b"
    assert stringify_tags([]) is None
