"""M5 Scalping Strategy.

Entry conditions:
- EMA(9)/EMA(21) crossover for trend direction
- RSI(14) momentum filter (40-65 for buy, 35-60 for sell)
- Stochastic %K(14) turning point confirmation
- VWAP intraday bias
- Bollinger Band squeeze detection

SL/TP:
- Stop loss: ATR(14) * 1.2
- Take profit: ATR(14) * 1.8  →  1.5:1 R:R
"""

from __future__ import annotations

from decimal import Decimal

import pandas as pd

from fxagent.config import Settings
from fxagent.domain.models import Signal
from fxagent.types import Pair, SignalType


class M5Scalper:
    def __init__(self, settings: Settings) -> None:
        self._s = settings

    def evaluate(self, pair: Pair, df: pd.DataFrame, idx: int) -> Signal | None:
        if idx < 1:
            return None

        row = df.iloc[idx]
        prev = df.iloc[idx - 1]

        # Require indicators to be computed
        required = ["ema_fast", "ema_slow", "rsi", "stoch_k", "vwap", "atr", "bb_upper", "bb_lower"]
        for col in required:
            if pd.isna(row.get(col)):
                return None

        close = Decimal(str(row["close"]))
        atr_val = Decimal(str(row["atr"]))

        if atr_val <= 0:
            return None

        long_signal = self._check_long(row, prev)
        short_signal = self._check_short(row, prev)

        if long_signal:
            sl = close - atr_val * self._s.atr_sl_multiplier
            tp = close + atr_val * self._s.atr_tp_multiplier
            return Signal(
                pair=pair,
                signal_type=SignalType.LONG,
                timestamp=pd.Timestamp(row["timestamp"]).to_pydatetime(),
                entry_price=close,
                stop_loss=sl,
                take_profit=tp,
                strength=float(row["rsi"]),
            )

        if short_signal:
            sl = close + atr_val * self._s.atr_sl_multiplier
            tp = close - atr_val * self._s.atr_tp_multiplier
            return Signal(
                pair=pair,
                signal_type=SignalType.SHORT,
                timestamp=pd.Timestamp(row["timestamp"]).to_pydatetime(),
                entry_price=close,
                stop_loss=sl,
                take_profit=tp,
                strength=float(row["rsi"]),
            )

        return None

    def _check_long(self, row: pd.Series, prev: pd.Series) -> bool:
        # EMA crossover: fast crosses above slow
        ema_cross = bool(
            prev["ema_fast"] <= prev["ema_slow"] and row["ema_fast"] > row["ema_slow"]
        )
        ema_trend = bool(row["ema_fast"] > row["ema_slow"])
        rsi_ok = bool(self._s.rsi_buy_low <= row["rsi"] <= self._s.rsi_buy_high)
        stoch_turn = bool(row["stoch_k"] > prev["stoch_k"] and row["stoch_k"] < 80)
        vwap_bias = bool(row["close"] > row["vwap"])

        bb_width = row["bb_upper"] - row["bb_lower"]
        prev_bb_width = prev["bb_upper"] - prev["bb_lower"]
        squeeze = bool(bb_width < prev_bb_width)

        if ema_cross and rsi_ok and stoch_turn:
            return True
        return bool(ema_trend and rsi_ok and stoch_turn and vwap_bias and squeeze)

    def _check_short(self, row: pd.Series, prev: pd.Series) -> bool:
        ema_cross = bool(
            prev["ema_fast"] >= prev["ema_slow"] and row["ema_fast"] < row["ema_slow"]
        )
        ema_trend = bool(row["ema_fast"] < row["ema_slow"])
        rsi_ok = bool(self._s.rsi_sell_low <= row["rsi"] <= self._s.rsi_sell_high)
        stoch_turn = bool(row["stoch_k"] < prev["stoch_k"] and row["stoch_k"] > 20)
        vwap_bias = bool(row["close"] < row["vwap"])

        bb_width = row["bb_upper"] - row["bb_lower"]
        prev_bb_width = prev["bb_upper"] - prev["bb_lower"]
        squeeze = bool(bb_width < prev_bb_width)

        if ema_cross and rsi_ok and stoch_turn:
            return True
        return bool(ema_trend and rsi_ok and stoch_turn and vwap_bias and squeeze)
