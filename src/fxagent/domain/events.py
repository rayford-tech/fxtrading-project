"""Domain events emitted during trading operations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from fxagent.types import Pair, Side, SignalType


@dataclass(frozen=True)
class Event:
    timestamp: datetime


@dataclass(frozen=True)
class SignalGenerated(Event):
    pair: Pair
    signal_type: SignalType
    entry_price: Decimal
    stop_loss: Decimal
    take_profit: Decimal


@dataclass(frozen=True)
class OrderPlaced(Event):
    order_id: str
    pair: Pair
    side: Side
    quantity: Decimal
    price: Decimal


@dataclass(frozen=True)
class OrderFilled(Event):
    order_id: str
    fill_price: Decimal


@dataclass(frozen=True)
class PositionClosed(Event):
    position_id: str
    pair: Pair
    side: Side
    pnl: Decimal
    close_price: Decimal


@dataclass(frozen=True)
class RiskRejected(Event):
    reason: str
    pair: Pair
    signal_type: SignalType


@dataclass(frozen=True)
class DailyLossLimitHit(Event):
    daily_pnl: Decimal
    limit: Decimal
