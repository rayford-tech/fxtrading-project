"""Tests for indicator functions."""

import numpy as np
import pandas as pd

from fxagent.features.indicators import atr, bollinger_bands, ema, rsi, sma, stochastic_k, vwap


class TestEMA:
    def test_ema_length(self) -> None:
        s = pd.Series(range(50), dtype=float)
        result = ema(s, 9)
        assert len(result) == 50

    def test_ema_values(self) -> None:
        s = pd.Series([1.0] * 20)
        result = ema(s, 9)
        assert abs(result.iloc[-1] - 1.0) < 1e-10


class TestSMA:
    def test_sma_constant(self) -> None:
        s = pd.Series([5.0] * 30)
        result = sma(s, 10)
        assert abs(result.iloc[-1] - 5.0) < 1e-10

    def test_sma_nan_prefix(self) -> None:
        s = pd.Series(range(20), dtype=float)
        result = sma(s, 10)
        assert pd.isna(result.iloc[0])
        assert not pd.isna(result.iloc[9])


class TestRSI:
    def test_rsi_range(self) -> None:
        np.random.seed(42)
        s = pd.Series(np.random.normal(0, 1, 100).cumsum() + 100)
        result = rsi(s, 14)
        valid = result.dropna()
        assert (valid >= 0).all()
        assert (valid <= 100).all()

    def test_rsi_constant_price(self) -> None:
        s = pd.Series([100.0] * 30)
        rsi(s, 14)  # Just verify it doesn't crash with constant prices


class TestStochasticK:
    def test_stoch_range(self) -> None:
        np.random.seed(42)
        n = 50
        close = pd.Series(np.random.normal(100, 1, n).cumsum())
        high = close + abs(np.random.normal(0, 0.5, n))
        low = close - abs(np.random.normal(0, 0.5, n))
        result = stochastic_k(high, low, close, 14)
        valid = result.dropna()
        assert (valid >= 0).all()
        assert (valid <= 100).all()


class TestBollingerBands:
    def test_band_order(self) -> None:
        s = pd.Series(np.random.normal(100, 1, 50))
        upper, middle, lower = bollinger_bands(s, 20, 2.0)
        valid_idx = ~(upper.isna() | middle.isna() | lower.isna())
        assert (upper[valid_idx] >= middle[valid_idx]).all()
        assert (middle[valid_idx] >= lower[valid_idx]).all()


class TestATR:
    def test_atr_positive(self) -> None:
        np.random.seed(42)
        n = 50
        close = pd.Series(100 + np.random.normal(0, 0.5, n).cumsum())
        high = close + 0.5
        low = close - 0.5
        result = atr(high, low, close, 14)
        valid = result.dropna()
        assert (valid > 0).all()


class TestVWAP:
    def test_vwap_reasonable(self) -> None:
        high = pd.Series([101.0, 102.0, 103.0])
        low = pd.Series([99.0, 100.0, 101.0])
        close = pd.Series([100.0, 101.0, 102.0])
        volume = pd.Series([1000.0, 1000.0, 1000.0])
        result = vwap(high, low, close, volume)
        assert len(result) == 3
        assert result.iloc[0] == 100.0  # (101+99+100)/3 = 100
