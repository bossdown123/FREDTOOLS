from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from .client import get_current_client

if TYPE_CHECKING:
    from .series import Series


class Tag:
    def __init__(self, name: str | None = None, **kwargs) -> None:

        self.name: str | None = kwargs.get("name")
        self.group_id: int | None = kwargs.get("group_id")
        self.notes: str | None = kwargs.get("notes")
        self.created: date | None = kwargs.get("created")
        self.popularity: int | None = kwargs.get("popularity")
        self.series_count: int | None = kwargs.get("series_count")

        if (
            not self.group_id
            and not self.notes
            and not self.created
            and not self.popularity
            and not self.series_count
        ):
            self.info()

    def series(
        self,
        tag_names: list[str] | list[Tag] | None = None,
        exclude_tag_names: list[str] | list[Tag] | None = None,
        realtime_start: date | None = None,
        realtime_end: date | None = None,
        order_by: str | None = None,
        sort_order: str | None = None,
    ) -> list[Series]:
        from .series import Series

        if not tag_names and not exclude_tag_names and self.name:
            tag_names = [self.name]
        client = get_current_client()

        tag_names_str = stringify_tags(tag_names)
        exclude_tag_names_str = stringify_tags(exclude_tag_names)

        params = {
            "tag_names": tag_names_str,
            "exclude_tag_names": exclude_tag_names_str,
            "realtime_start": realtime_start,
            "realtime_end": realtime_end,
            "order_by": order_by,
            "sort_order": sort_order,
        }

        response = client.request("tags/series", params=params).get("seriess", [])
        return [Series(**ser) for ser in response]

    def search(self, search: str) -> list[Tag]:
        client = get_current_client()

        params = {"search_text": search}

        response = client.request("tags/search", params=params).get("tags", [])
        return [Tag(**tag) for tag in response]

    def related_tags(
        self,
        tag_names: list[str] | list[Tag] | None = None,
        exclude_tag_names: list[str] | list[Tag] | None = None,
        realtime_start: date | None = None,
        realtime_end: date | None = None,
        order_by: str | None = None,
        sort_order: str | None = None,
    ) -> list[Tag]:
        client = get_current_client()

        params = {
            "tag_names": stringify_tags(tag_names),
            "exclude_tag_names": stringify_tags(exclude_tag_names),
            "realtime_start": realtime_start,
            "realtime_end": realtime_end,
            "order_by": order_by,
            "sort_order": sort_order,
        }
        response = client.request("tag/related_tags", params=params).get(
            "tags", []
        )
        return [Tag(**tag) for tag in response]

    def all(
        self,
        realtime_start: date | None = None,
        realtime_end: date | None = None,
        tag_names: list[str] | None = None,
        tag_group_id: int | None = None,
    ) -> list[Tag]:
        client = get_current_client()

        params = {
            "realtime_start": realtime_start,
            "realtime_end": realtime_end,
            "tag_names": stringify_tags(tag_names),
            "tag_group_id": tag_group_id,
        }

        response = client.request("tags", params=params).get("tags", [])
        return [Tag(**tag) for tag in response]

    def info(self) -> Tag:
        client = get_current_client()

        params = {"tag_names": self.name}

        response = client.request("tags", params=params).get("tags", [])
        if not response:
            raise ValueError(f"No tag found with id {self.name}")
        tag_info = response[0]
        self.name = tag_info.get("name")
        self.group_id = tag_info.get("group_id")
        self.notes = tag_info.get("notes")
        self.created = tag_info.get("created")
        self.popularity = tag_info.get("popularity")
        self.series_count = tag_info.get("series_count")
        return self

    def __repr__(self) -> str:
        return (
            f"Tag(name={self.name}, group_id={self.group_id}, "
            f"notes={self.notes}, created={self.created}, "
            f"popularity={self.popularity}, series_count={self.series_count})"
        )


def stringify_tags(
    tags: list[str] | list[Tag] | None,
) -> str | None:
    if not tags:
        return None

    names: list[str] = []
    for tag in tags:
        if isinstance(tag, Tag):
            if tag.name is None:
                continue
            names.append(tag.name)
        else:
            names.append(tag)

    return ";".join(names) if names else None
