"""Tests for feature pipeline."""

import pandas as pd

from fxagent.config import Settings
from fxagent.features.pipeline import enrich


class TestEnrich:
    def test_adds_indicator_columns(self, sample_ohlcv_df: pd.DataFrame) -> None:
        settings = Settings()
        result = enrich(sample_ohlcv_df, settings)

        expected_cols = ["ema_fast", "ema_slow", "rsi", "stoch_k", "bb_upper", "bb_middle", "bb_lower", "atr", "vwap"]
        for col in expected_cols:
            assert col in result.columns, f"Missing column: {col}"

    def test_does_not_mutate_input(self, sample_ohlcv_df: pd.DataFrame) -> None:
        settings = Settings()
        original_cols = set(sample_ohlcv_df.columns)
        enrich(sample_ohlcv_df, settings)
        assert set(sample_ohlcv_df.columns) == original_cols

    def test_output_length_preserved(self, sample_ohlcv_df: pd.DataFrame) -> None:
        settings = Settings()
        result = enrich(sample_ohlcv_df, settings)
        assert len(result) == len(sample_ohlcv_df)
