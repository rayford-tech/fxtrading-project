"""Tests for M5 scalper strategy."""

import pandas as pd

from fxagent.config import Settings
from fxagent.features.pipeline import enrich
from fxagent.strategy.m5_scalper import M5Scalper
from fxagent.types import Pair, SignalType


class TestM5Scalper:
    def test_returns_none_for_first_bar(self, sample_ohlcv_df: pd.DataFrame) -> None:
        settings = Settings()
        strategy = M5Scalper(settings)
        df = enrich(sample_ohlcv_df, settings)
        result = strategy.evaluate(Pair.USDJPY, df, 0)
        assert result is None

    def test_returns_none_when_indicators_nan(self, sample_ohlcv_df: pd.DataFrame) -> None:
        settings = Settings()
        strategy = M5Scalper(settings)
        df = enrich(sample_ohlcv_df, settings)
        # Early bars will have NaN indicators
        result = strategy.evaluate(Pair.USDJPY, df, 1)
        assert result is None

    def test_signal_has_valid_sl_tp(self, sample_ohlcv_df: pd.DataFrame) -> None:
        settings = Settings()
        strategy = M5Scalper(settings)
        df = enrich(sample_ohlcv_df, settings)

        # Scan for any signal in the data
        for idx in range(30, len(df)):
            signal = strategy.evaluate(Pair.USDJPY, df, idx)
            if signal is not None:
                if signal.signal_type == SignalType.LONG:
                    assert signal.stop_loss < signal.entry_price
                    assert signal.take_profit > signal.entry_price
                else:
                    assert signal.stop_loss > signal.entry_price
                    assert signal.take_profit < signal.entry_price
                break

    def test_evaluates_full_dataset_without_error(self, sample_ohlcv_df: pd.DataFrame) -> None:
        settings = Settings()
        strategy = M5Scalper(settings)
        df = enrich(sample_ohlcv_df, settings)
        signals = []
        for idx in range(len(df)):
            signal = strategy.evaluate(Pair.USDJPY, df, idx)
            if signal is not None:
                signals.append(signal)
        # Just verify it doesn't crash and signals are valid types
        for s in signals:
            assert s.signal_type in (SignalType.LONG, SignalType.SHORT)
