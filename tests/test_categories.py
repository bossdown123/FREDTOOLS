from __future__ import annotations

from datetime import date

import pytest

from fredtools.categories import Category
from tests.conftest import StubResponse


def make_category() -> Category:
    return Category(category_id=1, name="Root", parent_id=10)


def test_category_init_requires_identifier() -> None:
    with pytest.raises(ValueError):
        Category()


def test_category_init_invokes_info_when_missing_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    called = {"count": 0}

    def fake_info(self: Category) -> Category:
        called["count"] += 1
        self.name = "Loaded"
        self.parent_id = 1
        return self

    monkeypatch.setattr(Category, "info", fake_info)
    Category(category_id=1, name="Name", parent_id=None)
    assert called["count"] == 1


def test_category_children_returns_instances(make_stub_client) -> None:
    response = {
        "categories": [
            {"id": 2, "name": "Child", "parent_id": 1},
        ]
    }
    stub = make_stub_client([StubResponse("category/children", response)])
    children = make_category().children()
    assert len(children) == 1
    assert isinstance(children[0], Category)
    assert children[0].name == "Child"
    stub.assert_complete()


def test_category_related_returns_instances(make_stub_client) -> None:
    response = {
        "categories": [
            {"id": 3, "name": "Related", "parent_id": 1},
        ]
    }
    stub = make_stub_client([StubResponse("category/related", response)])
    related = make_category().related()
    assert related[0].name == "Related"
    stub.assert_complete()


def test_category_series_returns_series_objects(make_stub_client) -> None:
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
    stub = make_stub_client([StubResponse("category/series", response)])
    result = make_category().series(limit=1)
    assert result[0].series_id == "S1"
    stub.assert_complete()


def test_category_info_fetches_and_populates(make_stub_client) -> None:
    response = {
        "categories": [
            {
                "id": 5,
                "name": "Updated",
                "parent_id": 1,
            }
        ]
    }
    stub = make_stub_client([StubResponse("category", response)])
    category = Category(category_id=5, name="Old", parent_id=1)
    category.info()
    assert category.name == "Updated"
    assert category.parent_id == 1
    stub.assert_complete()


def test_category_repr_includes_core_fields() -> None:
    text = repr(make_category())
    assert "Category(id=1" in text and "name=Root" in text
