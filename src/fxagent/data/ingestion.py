"""Data ingestion from CSV and Parquet files."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from fxagent.data.timeframe import Timeframe
from fxagent.types import Pair


class CSVProvider:
    """Loads OHLCV data from CSV or Parquet files."""

    def __init__(self, data_dir: Path) -> None:
        self._data_dir = data_dir

    def load(self, pair: Pair, timeframe: str) -> pd.DataFrame:
        csv_path = self._data_dir / f"{pair.value}_{timeframe}.csv"
        parquet_path = self._data_dir / f"{pair.value}_{timeframe}.parquet"

        if parquet_path.exists():
            df = pd.read_parquet(parquet_path)
        elif csv_path.exists():
            df = pd.read_csv(csv_path, parse_dates=["timestamp"])
        else:
            raise FileNotFoundError(
                f"No data file found for {pair.value} {timeframe} in {self._data_dir}"
            )

        df = self._validate_and_normalize(df)
        return df

    def _validate_and_normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        required = {"timestamp", "open", "high", "low", "close", "volume"}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"Missing columns: {missing}")

        df = df.sort_values("timestamp").reset_index(drop=True)
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        for col in ("open", "high", "low", "close", "volume"):
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df = df.dropna(subset=["open", "high", "low", "close"])
        return df


class DataFrameProvider:
    """Wraps an in-memory DataFrame as an OHLCVProvider (useful for testing)."""

    def __init__(self, data: dict[tuple[str, str], pd.DataFrame]) -> None:
        self._data = data

    def load(self, pair: Pair, timeframe: str) -> pd.DataFrame:
        key = (pair.value, timeframe)
        if key not in self._data:
            raise KeyError(f"No data registered for {key}")
        return self._data[key].copy()


def resample_ohlcv(df: pd.DataFrame, target: Timeframe) -> pd.DataFrame:
    """Resample OHLCV data to a coarser timeframe."""
    resampled = (
        df.set_index("timestamp")
        .resample(target.pandas_freq)
        .agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
        .dropna()
        .reset_index()
    )
    return resampled
