from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from .client import get_current_client

if TYPE_CHECKING:
    from .series import Series


class Category:
    def __init__(self, category_id: int | None = None, **kwargs) -> None:
        if not category_id and not kwargs.get("id"):
            raise ValueError("Either category_id or id must be provided")
        self.category_id: int | None = (
            category_id if category_id is not None else kwargs.get("id")
        )

        self.name: str | None = kwargs.get("name")
        self.parent_id: int | None = kwargs.get("parent_id")
        if not self.name or not self.parent_id:
            self.info()

    def children(
        self,
        category_id: int | None = None,
        realtime_start: date | None = None,
        realtime_end: date | None = None,
    ) -> list[Category]:
        client = get_current_client()

        params = {
            "category_id": (
                category_id if category_id is not None else self.category_id
            ),
            "realtime_start": realtime_start,
            "realtime_end": realtime_end,
        }
        response = client.request("category/children", params=params).get(
            "categories", []
        )
        return [Category(**child) for child in response]

    def related(
        self,
        category_id: int | None = None,
        realtime_start: date | None = None,
        realtime_end: date | None = None,
    ) -> list[Category]:
        client = get_current_client()

        params = {
            "category_id": (
                category_id if category_id is not None else self.category_id
            ),
            "realtime_start": realtime_start,
            "realtime_end": realtime_end,
        }
        response = client.request("category/related", params=params).get(
            "categories", []
        )
        return [Category(**child) for child in response]

    def series(
        self,
        category_id: int | None = None,
        realtime_start: date | None = None,
        realtime_end: date | None = None,
        limit: int | None = None,
        offset: int | None = None,
        sort_order: str | None = None,
    ) -> list[Series]:
        from .series import Series

        client = get_current_client()

        params = {
            "category_id": (
                category_id if category_id is not None else self.category_id
            ),
            "realtime_start": realtime_start,
            "realtime_end": realtime_end,
            "limit": limit,
            "offset": offset,
            "sort_order": sort_order,
        }
        response = client.request("category/series", params=params).get(
            "seriess", []
        )

        return [Series(**ser) for ser in response]

    def info(self) -> Category:
        client = get_current_client()

        params = {"category_id": self.category_id}

        response = client.request("category", params=params).get(
            "categories", []
        )
        if not response:
            raise ValueError(f"No category found with id {self.category_id}")
        category = Category(**response[0])
        self.name = category.name
        self.parent_id = category.parent_id
        return category

    def __repr__(self) -> str:
        return (
            f"Category(id={self.category_id}, name={self.name}, "
            f"parent_id={self.parent_id})"
        )