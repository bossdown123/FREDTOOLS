from __future__ import annotations

import builtins
import sys
from datetime import date
from types import SimpleNamespace

import pytest

from fredtools.types import Observation, ObservationsResult


def make_observation() -> Observation:
    return Observation(
        realtime_start=date(2020, 1, 1),
        realtime_end=date(2020, 1, 31),
        date=date(2020, 1, 15),
        value=1.23,
    )


def test_observations_result_behaves_like_list() -> None:
    observation = make_observation()
    result = ObservationsResult([observation])
    assert len(result) == 1
    assert result[0] is observation


def test_observations_result_df_uses_pandas(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_pd = SimpleNamespace(
        DataFrame=lambda data: {"called_with": data},
    )
    monkeypatch.setitem(sys.modules, "pandas", fake_pd)
    result = ObservationsResult([make_observation()])
    frame = result.df
    assert frame["called_with"][0]["value"] == 1.23


def test_observations_result_df_raises_without_pandas(monkeypatch: pytest.MonkeyPatch) -> None:
    original_import = builtins.__import__

    def fake_import(name: str, *args, **kwargs):
        if name == "pandas":
            raise ImportError("missing pandas")
        return original_import(name, *args, **kwargs)

    monkeypatch.delitem(sys.modules, "pandas", raising=False)
    monkeypatch.setattr(builtins, "__import__", fake_import)
    result = ObservationsResult([make_observation()])
    with pytest.raises(RuntimeError) as excinfo:
        _ = result.df
    assert "pandas is required" in str(excinfo.value)
