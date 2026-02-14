"""Tests for data ingestion."""

from pathlib import Path

import pandas as pd
import pytest

from fxagent.data.ingestion import CSVProvider, DataFrameProvider
from fxagent.types import Pair


class TestCSVProvider:
    def test_missing_file_raises(self, tmp_path: Path) -> None:
        provider = CSVProvider(tmp_path)
        with pytest.raises(FileNotFoundError):
            provider.load(Pair.USDJPY, "5min")

    def test_load_csv(self, tmp_path: Path, sample_ohlcv_df: pd.DataFrame) -> None:
        csv_path = tmp_path / "USDJPY_5min.csv"
        sample_ohlcv_df.to_csv(csv_path, index=False)

        provider = CSVProvider(tmp_path)
        df = provider.load(Pair.USDJPY, "5min")

        assert len(df) == len(sample_ohlcv_df)
        assert "timestamp" in df.columns
        assert df["close"].dtype == float

    def test_missing_columns_raises(self, tmp_path: Path) -> None:
        csv_path = tmp_path / "USDJPY_5min.csv"
        pd.DataFrame({"timestamp": [1], "open": [1]}).to_csv(csv_path, index=False)

        provider = CSVProvider(tmp_path)
        with pytest.raises(ValueError, match="Missing columns"):
            provider.load(Pair.USDJPY, "5min")


class TestDataFrameProvider:
    def test_load(self, sample_ohlcv_df: pd.DataFrame) -> None:
        provider = DataFrameProvider({("USDJPY", "5min"): sample_ohlcv_df})
        df = provider.load(Pair.USDJPY, "5min")
        assert len(df) == len(sample_ohlcv_df)

    def test_missing_key_raises(self) -> None:
        provider = DataFrameProvider({})
        with pytest.raises(KeyError):
            provider.load(Pair.USDJPY, "5min")
