"""Feature pipeline — enriches OHLCV DataFrame with indicator columns."""

from __future__ import annotations

import pandas as pd

from fxagent.config import Settings
from fxagent.features import indicators as ind


def enrich(df: pd.DataFrame, settings: Settings) -> pd.DataFrame:
    """Add all indicator columns to an OHLCV DataFrame. Returns a new DataFrame."""
    df = df.copy()

    df["ema_fast"] = ind.ema(df["close"], settings.ema_fast)
    df["ema_slow"] = ind.ema(df["close"], settings.ema_slow)
    df["rsi"] = ind.rsi(df["close"], settings.rsi_period)
    df["stoch_k"] = ind.stochastic_k(
        df["high"], df["low"], df["close"], settings.stoch_period
    )
    df["bb_upper"], df["bb_middle"], df["bb_lower"] = ind.bollinger_bands(
        df["close"], settings.bb_period, settings.bb_std
    )
    df["atr"] = ind.atr(df["high"], df["low"], df["close"], settings.atr_period)
    df["vwap"] = ind.vwap(df["high"], df["low"], df["close"], df["volume"])

    return df
