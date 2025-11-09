from datetime import date, datetime
from typing import Any, TYPE_CHECKING

from .client import get_current_client
from .logging import get_logger
from .tags import Tag
from .types import ReleaseTable, ReleaseTableElement, Source

if TYPE_CHECKING:
    from .series import Series

class Release:
    """Class for FRED release operations."""

    def __init__(self, release_id: int | None = None, **kwargs) -> None:
        self._logger = get_logger(__name__)
        if not release_id and not kwargs.get("id"):
            raise ValueError("Either release_id or id must be provided")
        self.release_id: int | None = (
            release_id if release_id is not None else kwargs.get("id")
        )

        self.name: str | None = kwargs.get("name")
        self.realtime_start: date | None = kwargs.get("realtime_start")
        self.realtime_end: date | None = kwargs.get("realtime_end")
        if not self.name and not self.realtime_start and not self.realtime_end:
            self.info()

    def info(
        self,
        realtime_start: date | None = None,
        realtime_end: date | None = None,
    ) -> Release:
        """Fetch the release metadata associated with a series."""
        client = get_current_client()

        params = {
            "release_id": self.release_id,
            "realtime_start": (
                realtime_start.isoformat() if realtime_start else None
            ),
            "realtime_end": (
                realtime_end.isoformat() if realtime_end else None
            ),
        }

        self._logger.debug(
            "Fetching release metadata for release_id=%s", self.release_id
        )
        response = client.request("release", params=params)
        releases = response.get("releases", [])
        if not releases:
            raise ValueError(
                f"No release found with release_id={self.release_id}"
            )

        release_data = releases[0]
        release = Release(**release_data)
        self.release_id = release.release_id
        self.name = release.name
        self.realtime_start = release.realtime_start
        self.realtime_end = release.realtime_end
        return release
    
    def all(
        self,
        realtime_start: date | None = None,
        realtime_end: date | None = None,
        order_by: str | None = None,
        sort_order: str | None = None,
    ) -> list[Release]:
        """Fetch all releases."""
        client = get_current_client()

        params = {
            "realtime_start": (
                realtime_start.isoformat() if realtime_start else None
            ),
            "realtime_end": (
                realtime_end.isoformat() if realtime_end else None
            ),
            "order_by": order_by,
            "sort_order": sort_order,
        }

        self._logger.debug("Fetching all releases")
        response = client.request("releases", params=params)
        releases_data = response.get("releases", [])
        releases = []
        for release_data in releases_data:
            releases.append(
                Release(
                    id=release_data["id"],
                    realtime_start=datetime.strptime(
                        release_data["realtime_start"], "%Y-%m-%d"
                    ).date(),
                    realtime_end=datetime.strptime(
                        release_data["realtime_end"], "%Y-%m-%d"
                    ).date(),
                    name=release_data["name"],
                    press_release=release_data["press_release"],
                    link=release_data["link"],
                )
            )
        return releases
    
    def dates(
        self,
        release_id: int | None = None,
        realtime_start: date | None = None,
        realtime_end: date | None = None,
        include_release_dates_with_no_data: bool = True,
    ) -> list[date]:
        """Fetch the release dates for a given release."""
        client = get_current_client()

        params = {
            "release_id": release_id if release_id is not None else self.release_id,
            "realtime_start": (
                realtime_start.isoformat() if realtime_start else None
            ),
            "realtime_end": (
                realtime_end.isoformat() if realtime_end else None
            ),
        }

        self._logger.debug(
            "Fetching release dates for release_id=%s",
            params["release_id"],
        )
        response = client.request("release/dates", params=params)
        dates_data = response.get("release_dates", [])
        release_dates = [
            datetime.strptime(date_str, "%Y-%m-%d").date()
            for date_str in dates_data
        ]
        return release_dates    
            
    def all_dates(
        self,
        realtime_start: date | None = None,
        realtime_end: date | None = None,
        order_by: str | None = None,
        sort_order: str | None = None,
        include_release_dates_with_no_data: bool = True,
    ) -> list[date]:
        """Fetch all release dates."""
        client = get_current_client()

        params = {
            "realtime_start": (
                realtime_start.isoformat() if realtime_start else None
            ),
            "realtime_end": (
                realtime_end.isoformat() if realtime_end else None
            ),
        }

        self._logger.debug("Fetching all release dates")
        response = client.request("releases/dates", params=params)
        dates_data = response.get("release_dates", [])
        release_dates = [
            datetime.strptime(date_str, "%Y-%m-%d").date()
            for date_str in dates_data
        ]
        return release_dates

    def series(
        self,
        realtime_start: date | None = None,
        realtime_end: date | None = None,
        limit: int | None = None,
        offset: int | None = None,
        sort_order: str | None = None,
    ) -> list["Series"]:
        """Fetch series associated with this release."""
        from .series import Series

        client = get_current_client()

        params = {
            "release_id": self.release_id,
            "realtime_start": (
                realtime_start.isoformat() if realtime_start else None
            ),
            "realtime_end": (
                realtime_end.isoformat() if realtime_end else None
            ),
            "limit": limit,
            "offset": offset,
            "sort_order": sort_order,
        }

        self._logger.debug(
            "Fetching series for release_id=%s", self.release_id
        )
        response = client.request("release/series", params=params)
        series_list = response.get("seriess", [])
        return [Series(**ser) for ser in series_list]

    def sources(
        self,
        realtime_start: date | None = None,
        realtime_end: date | None = None,
    ) -> list[Source]:
        """Fetch sources associated with this release."""

        client = get_current_client()

        params = {
            "release_id": self.release_id,
            "realtime_start": (
                realtime_start.isoformat() if realtime_start else None
            ),
            "realtime_end": (
                realtime_end.isoformat() if realtime_end else None
            )
        }

        self._logger.debug(
            "Fetching sources for release_id=%s", self.release_id
        )
        response = client.request("release/sources", params=params)
        sources_list = response.get("sources", [])
        return [Source(**src) for src in sources_list]

    def table(
        self,
        release_id: int | None = None,
        element_id: int | None = None,
        observation_date: date | None = None,
        include_observation_values: bool = False,
    ) -> ReleaseTable:
        release_id = release_id if release_id is not None else self.release_id
        """Fetch the hierarchical table for this release."""
        if self.release_id is None:
            raise ValueError("release_id must be set to fetch table data")

        client = get_current_client()
        params = {
            "release_id": release_id,
            "element_id": element_id,
            "observation_date": (
                observation_date.isoformat() if observation_date else None
            ),
            "include_observation_values": (
                1 if include_observation_values else None
            ),
        }

        self._logger.debug(
            "Fetching table for release_id=%s element_id=%s",
            self.release_id,
            element_id,
        )
        response = client.request("release/tables", params=params)
        print(response)
        elements = response.get("elements", {})
        if not elements:
            raise ValueError(
                "No table data returned for "
                f"release_id={self.release_id} element_id={element_id}"
            )

        return self._parse_release_table(response, self.release_id)

    def tags(
        self,
        release_id: int | None = None,
        realtime_start: date | None = None,
        realtime_end: date | None = None,
        tag_names: list[str] | None = None,
        tag_group_id: int | None = None,
        search_text: str | None = None,
        order_by: str | None = None,
        sort_order: str | None = None,
    ) -> list[Tag]:
        """Fetch tags associated with this release."""
        client = get_current_client()

        params = {
            "release_id": release_id if release_id is not None else self.release_id,
            "realtime_start": (
                realtime_start.isoformat() if realtime_start else None
            ),
            "realtime_end": (
                realtime_end.isoformat() if realtime_end else None
            ),
            "tag_names": (
                ";".join(tag_names) if tag_names is not None else None
            ),
            "tag_group_id": tag_group_id,
            "search_text": search_text,
            "order_by": order_by,
            "sort_order": sort_order,
        }

        self._logger.debug(
            "Fetching tags for release_id=%s", params["release_id"]
        )
        response = client.request("release/tags", params=params)
        tags_list = response.get("tags", [])
        return [Tag(**tag) for tag in tags_list]

    def related_tags(
        self,
        release_id: int | None = None,
        realtime_start: date | None = None,
        realtime_end: date | None = None,
        tag_names: list[str] | None = None,
        exclude_tag_names: list[str] | None = None,
        tag_group_id: int | None = None,
        order_by: str | None = None,
        sort_order: str | None = None,
    ) -> list[Tag]:
        """Fetch related tags associated with this release."""
        client = get_current_client()

        params = {
            "release_id": release_id if release_id is not None else self.release_id,
            "realtime_start": (
                realtime_start.isoformat() if realtime_start else None
            ),
            "realtime_end": (
                realtime_end.isoformat() if realtime_end else None
            ),
            "tag_names": (
                ";".join(tag_names) if tag_names is not None else None
            ),
            "tag_group_id": tag_group_id,
            "exclude_tag_names": (
                ";".join(exclude_tag_names)
                if exclude_tag_names is not None
                else None
            ),
            "order_by": order_by,
            "sort_order": sort_order,
        }

        self._logger.debug(
            "Fetching related tags for release_id=%s", params["release_id"]
        )
        response = client.request("release/related_tags", params=params)
        tags_list = response.get("tags", [])
        return [Tag(**tag) for tag in tags_list]

    @staticmethod
    def _parse_release_table(
        data: dict[str, Any],
        fallback_release_id: int | None = None,
    ) -> ReleaseTable:
        elements_raw = data.get("elements")
        if not isinstance(elements_raw, dict) or not elements_raw:
            raise ValueError("Release table response did not include elements")

        default_release_id = Release._coerce_int(data.get("release_id"))
        if default_release_id is None:
            default_release_id = fallback_release_id
        if default_release_id is None:
            raise ValueError(
                "Release table response did not include a release identifier"
            )

        element_lookup: dict[int, ReleaseTableElement] = {}

        def _get_or_create(
            element_data: dict[str, Any],
        ) -> ReleaseTableElement:
            element_id = Release._coerce_int(element_data.get("element_id"))
            if element_id is None:
                raise ValueError("Table element is missing an element_id")

            existing = element_lookup.get(element_id)
            if existing is not None:
                return existing

            release_id = Release._coerce_int(element_data.get("release_id"))
            if release_id is None:
                release_id = default_release_id
            if release_id is None:
                raise ValueError(
                    f"Table element {element_id} is missing release data"
                )

            parent_id = Release._coerce_int(element_data.get("parent_id"))
            level = Release._coerce_int(element_data.get("level"))
            element = ReleaseTableElement(
                element_id=element_id,
                release_id=release_id,
                series_id=element_data.get("series_id"),
                parent_id=parent_id,
                line=element_data.get("line"),
                type=element_data.get("type", ""),
                name=element_data.get("name", ""),
                level=level,
            )
            element_lookup[element_id] = element
            return element

        for raw_element in elements_raw.values():
            parent = _get_or_create(raw_element)
            for child_data in raw_element.get("children") or []:
                child = _get_or_create(child_data)
                if all(
                    existing.element_id != child.element_id
                    for existing in parent.children
                ):
                    parent.children.append(child)

        root_element_id = Release._coerce_int(data.get("element_id"))

        def _collect_children(
            target_parent_id: int | None,
        ) -> list[ReleaseTableElement]:
            collected: list[ReleaseTableElement] = []
            seen_ids: set[int] = set()
            for raw_element in elements_raw.values():
                element = _get_or_create(raw_element)
                if element.element_id in seen_ids:
                    continue
                if target_parent_id is None:
                    is_top_level = (
                        element.parent_id is None
                        or element.parent_id not in element_lookup
                    )
                else:
                    is_top_level = element.parent_id == target_parent_id
                if is_top_level:
                    collected.append(element)
                    seen_ids.add(element.element_id)
            return collected

        top_level_elements = _collect_children(root_element_id)
        if not top_level_elements:
            top_level_elements = _collect_children(None)

        return ReleaseTable(
            name=data.get("name"),
            element_id=root_element_id,
            release_id=default_release_id,
            elements=top_level_elements,
        )

    @staticmethod
    def _coerce_int(value: Any) -> int | None:
        if value is None:
            return None
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return None
            try:
                return int(stripped)
            except ValueError as exc:
                raise ValueError(
                    f"Unable to convert value '{value}' to an integer"
                ) from exc
        if isinstance(value, float):
            if value.is_integer():
                return int(value)
            raise ValueError(
                f"Unable to convert non-integer float '{value}' to an int"
            )
        try:
            return int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Unable to convert value '{value}' to an integer"
            ) from exc

    def __repr__(self) -> str:
        return (
            f"Release(id={self.release_id}, name={self.name}, "
            f"realtime_start={self.realtime_start}, "
            f"realtime_end={self.realtime_end})"
        )
