from __future__ import annotations

from collections.abc import Callable, Mapping
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Any

import pytest

from fredtools import client as client_module


@pytest.fixture(autouse=True)
def reset_current_client(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure each test starts with a clean client ContextVar."""
    monkeypatch.setattr(
        client_module,
        "_current_client",
        ContextVar("_current_client", default=None),
    )


@dataclass
class StubResponse:
    endpoint: str | None
    response: Any
    assert_params: Callable[[Mapping[str, Any] | None], None] | None = None


class StubClient:
    """Simple stub that returns canned responses and tracks calls."""

    def __init__(self, responses: list[StubResponse]) -> None:
        self._responses = list(responses)
        self.calls: list[tuple[str, Mapping[str, Any] | None]] = []

    def request(
        self,
        endpoint: str,
        params: Mapping[str, Any] | None = None,
    ) -> Any:
        if not self._responses:
            raise AssertionError(f"Unexpected request to {endpoint!r}")
        expected = self._responses.pop(0)
        if expected.endpoint is not None:
            assert endpoint == expected.endpoint, (
                f"Expected endpoint {expected.endpoint!r} got {endpoint!r}"
            )
        if expected.assert_params:
            expected.assert_params(params)
        self.calls.append((endpoint, params))
        return expected.response() if callable(expected.response) else expected.response

    def assert_complete(self) -> None:
        if self._responses:
            remaining = [item.endpoint for item in self._responses]
            raise AssertionError(f"Unused stub responses remain: {remaining}")


@pytest.fixture
def make_stub_client() -> Callable[[list[StubResponse]], StubClient]:
    """Factory that registers a stub client as the default fred client."""

    def _factory(responses: list[StubResponse]) -> StubClient:
        stub = StubClient(responses)
        client_module.set_default_client(stub)  # type: ignore[arg-type]
        return stub

    return _factory
