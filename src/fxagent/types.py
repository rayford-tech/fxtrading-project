"""Core type definitions and protocols."""

from __future__ import annotations

from decimal import Decimal
from enum import StrEnum
from typing import Protocol, runtime_checkable

import pandas as pd


class Side(StrEnum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(StrEnum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"


class PositionStatus(StrEnum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class SignalType(StrEnum):
    LONG = "LONG"
    SHORT = "SHORT"
    FLAT = "FLAT"


class Pair(StrEnum):
    USDJPY = "USDJPY"
    GBPUSD = "GBPUSD"

    @property
    def pip_value(self) -> Decimal:
        if self == Pair.USDJPY:
            return Decimal("0.01")
        return Decimal("0.0001")


@runtime_checkable
class OHLCVProvider(Protocol):
    def load(self, pair: Pair, timeframe: str) -> pd.DataFrame: ...


@runtime_checkable
class BrokerAdapter(Protocol):
    def submit_order(
        self,
        pair: Pair,
        side: Side,
        quantity: Decimal,
        order_type: OrderType,
        price: Decimal,
        stop_loss: Decimal,
        take_profit: Decimal,
    ) -> str: ...

    def cancel_order(self, order_id: str) -> bool: ...

    def get_position(self, order_id: str) -> PositionStatus: ...

    def get_fill_price(self, order_id: str) -> Decimal: ...
