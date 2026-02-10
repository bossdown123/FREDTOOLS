# fredtools

A lightweight Python client for the FRED (Federal Reserve Economic Data) API.

## Install

```bash
pip install -e .
```

## Configure

Set the FRED API key in your environment before running examples:

```bash
export FRED_API_KEY="your_key_here"
```

## Quickstart

```python
import os

from fredtools import Fred, FredConfig, Series

api_key = os.environ.get("FRED_API_KEY")
if not api_key:
    raise RuntimeError("Set FRED_API_KEY in your environment.")

client = Fred(FredConfig(api_key=api_key))

gdp = Series("GDP")
print(gdp.title)
print(gdp.observations()[:5])
```

## Notebooks

- `01_quickstart.ipynb`: Setup, series metadata, observations, revisions plot.
- `02_series_search_and_tags.ipynb`: Search workflows and tag exploration.
- `03_categories_and_releases.ipynb`: Category browsing and release endpoints.

## Notes

- The notebooks hit the live FRED API and require network access.
- Plotting revisions requires `pandas` and `matplotlib`.
