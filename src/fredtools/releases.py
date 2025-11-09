from datetime import date, datetime

from .client import get_current_client
from .types import Release


class Releases:
    """Class for FRED release operations."""

    def release(
        self,
        series_id: str,
        realtime_start: date | None = None,
        realtime_end: date | None = None,
    ) -> Release:
        """Fetch the release metadata associated with a series."""
        client = get_current_client()

        params = {
            "series_id": series_id,
            "realtime_start": (
                realtime_start.isoformat() if realtime_start else None
            ),
            "realtime_end": realtime_end.isoformat() if realtime_end else None,
        }

        response = client.request("series/release", params=params)
        releases = response.get("releases", [])
        if not releases:
            raise RuntimeError(
                f"No release metadata returned for series_id='{series_id}'."
            )

        release_data = releases[0]
        return Release(
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
