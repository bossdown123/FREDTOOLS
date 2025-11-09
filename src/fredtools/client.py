"""Client for interacting with the FRED API."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from typing import Any, Callable, Mapping, MutableMapping
from urllib import parse as urlparse
from urllib import request as urlrequest
from contextvars import ContextVar


_current_client: ContextVar[Fred | None] = ContextVar("_current_client", default=None)


def set_default_client(client: "Fred") -> None:
    _current_client.set(client)


class use_client:
    def __init__(self, client: "Fred") -> None:
        self._token = None
        self.client = client

    def __enter__(self) -> None:
        self._token = _current_client.set(self.client)

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if self._token is not None:
            _current_client.reset(self._token)


def get_current_client() -> Fred:
    client = _current_client.get()
    if client is None:
        raise RuntimeError(
            "No current Client set. Pass client=... or call set_default_client(...)."
        )
    return client


DEFAULT_BASE_URL = "https://api.stlouisfed.org/fred"


Transport = Callable[[str, Mapping[str, Any], float | None], Any]


@dataclass(slots=True)
class FredConfig:
    """Configuration for the FRED client."""

    api_key: str
    base_url: str = DEFAULT_BASE_URL
    transport: Transport | None = None

class Fred:
    """Client for interacting with the FRED API."""

    def __init__(
        self,
        config: FredConfig,
        register_default: bool = True,
    ) -> None:
        self._config = config
        self._base_url = self._config.base_url.rstrip("/")
        if register_default:
            set_default_client(self)

    def _default_transport(
        self,
        url: str,
        params: Mapping[str, Any],
        timeout: float | None = None,
    ) -> Any:
        query_string = urlparse.urlencode(params)
        full_url = f"{url}?{query_string}"
        with urlrequest.urlopen(full_url, timeout=timeout) as response:
            return json.load(response)

    def _get_transport(self) -> Transport:
        if self._config.transport is not None:
            return self._config.transport
        return self._default_transport

    def _build_url(self, endpoint: str) -> str:
        endpoint = endpoint.lstrip("/")
        return f"{self._base_url}/{endpoint}"

    def _build_params(
        self,
        params: Mapping[str, Any] | None,
    ) -> dict[str, Any]:
        prepared: dict[str, Any] = {
            "api_key": self._config.api_key,
            "file_type": "json",
        }
        if params:
            for key, value in params.items():
                if value is None:
                    continue
                prepared[key] = value
        return prepared

    def request(
        self,
        endpoint: str,
        params: Mapping[str, Any] | None = None,
        timeout: float | None = None,
    ) -> Any:
        url = self._build_url(endpoint)
        prepared_params = self._build_params(params)
        transport = self._get_transport()
        return transport(url, prepared_params, timeout)

