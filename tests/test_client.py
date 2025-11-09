from __future__ import annotations

import io
import json
from types import SimpleNamespace

import pytest

from fredtools import client as client_module
from fredtools.client import (
    Fred,
    FredConfig,
    get_current_client,
    set_default_client,
    use_client,
)


class DummyClient:
    pass


def test_set_and_get_current_client_returns_same_instance() -> None:
    dummy = DummyClient()
    set_default_client(dummy)  # type: ignore[arg-type]
    assert get_current_client() is dummy


def test_get_current_client_without_default_raises() -> None:
    with pytest.raises(RuntimeError):
        get_current_client()


def test_use_client_context_manager_sets_and_restores_client() -> None:
    primary = DummyClient()
    secondary = DummyClient()
    set_default_client(primary)  # type: ignore[arg-type]
    with use_client(secondary):  # type: ignore[arg-type]
        assert get_current_client() is secondary
    assert get_current_client() is primary


def test_fred_init_registers_default_client() -> None:
    config = FredConfig(api_key="key")
    fred = Fred(config)
    assert get_current_client() is fred


def test_fred_init_without_register_flag_leaves_default_empty() -> None:
    config = FredConfig(api_key="key")
    Fred(config, register_default=False)
    with pytest.raises(RuntimeError):
        get_current_client()


def test_build_url_strips_extra_slashes() -> None:
    fred = Fred(FredConfig(api_key="k", base_url="https://example.com/"), register_default=False)
    assert fred._build_url("/release/data") == "https://example.com/release/data"


def test_build_params_merges_user_values_and_drops_none() -> None:
    fred = Fred(FredConfig(api_key="k"), register_default=False)
    params = fred._build_params({"foo": "bar", "none": None})
    assert params == {"api_key": "k", "file_type": "json", "foo": "bar"}


def test_get_transport_prefers_configured_transport() -> None:
    def custom_transport(url: str, params: dict[str, str], timeout: float | None) -> dict[str, str]:
        return {"url": url}

    config = FredConfig(api_key="k", transport=custom_transport)
    fred = Fred(config, register_default=False)
    assert fred._get_transport() is custom_transport


def test_get_transport_defaults_to_internal() -> None:
    fred = Fred(FredConfig(api_key="k"), register_default=False)
    transport = fred._get_transport()
    assert hasattr(transport, "__func__")
    assert transport.__func__ is fred._default_transport.__func__  # type: ignore[attr-defined]


def test_default_transport_builds_query_and_loads_json(monkeypatch: pytest.MonkeyPatch) -> None:
    fred = Fred(FredConfig(api_key="k"), register_default=False)
    captured: dict[str, object] = {}

    def fake_urlopen(url: str, timeout: float | None = None) -> SimpleNamespace:
        captured["url"] = url
        captured["timeout"] = timeout

        class DummyResponse:
            def __enter__(self) -> io.StringIO:
                return io.StringIO(json.dumps({"status": "ok"}))

            def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
                return None

        return DummyResponse()

    monkeypatch.setattr(client_module.urlrequest, "urlopen", fake_urlopen)
    result = fred._default_transport("https://fred", {"a": "1"}, timeout=3.0)
    assert captured == {"url": "https://fred?a=1", "timeout": 3.0}
    assert result == {"status": "ok"}


def test_request_invokes_transport_with_prepared_values() -> None:
    captured: dict[str, object] = {}

    def fake_transport(url: str, params: dict[str, str], timeout: float | None) -> dict[str, str]:
        captured["url"] = url
        captured["params"] = params
        captured["timeout"] = timeout
        return {"ok": "yes"}

    config = FredConfig(api_key="k", base_url="https://example.org", transport=fake_transport)
    fred = Fred(config, register_default=False)
    result = fred.request("release/series", params={"limit": 10}, timeout=2.5)
    assert result == {"ok": "yes"}
    assert captured["url"] == "https://example.org/release/series"
    assert captured["timeout"] == 2.5
    assert captured["params"] == {"api_key": "k", "file_type": "json", "limit": 10}
