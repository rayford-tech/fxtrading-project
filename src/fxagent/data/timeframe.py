"""Timeframe utilities for OHLCV data."""

from __future__ import annotations

from enum import StrEnum


class Timeframe(StrEnum):
    M1 = "1min"
    M5 = "5min"
    M15 = "15min"
    H1 = "1h"
    H4 = "4h"
    D1 = "1D"

    @property
    def pandas_freq(self) -> str:
        return self.value

    @property
    def minutes(self) -> int:
        mapping = {"1min": 1, "5min": 5, "15min": 15, "1h": 60, "4h": 240, "1D": 1440}
        return mapping[self.value]
