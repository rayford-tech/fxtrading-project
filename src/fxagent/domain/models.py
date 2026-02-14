"""Domain models for trading entities."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from fxagent.types import OrderType, Pair, PositionStatus, Side, SignalType


@dataclass(frozen=True)
class Signal:
    pair: Pair
    signal_type: SignalType
    timestamp: datetime
    entry_price: Decimal
    stop_loss: Decimal
    take_profit: Decimal
    strength: float = 0.0
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Order:
    order_id: str
    pair: Pair
    side: Side
    quantity: Decimal
    order_type: OrderType
    price: Decimal
    stop_loss: Decimal
    take_profit: Decimal
    timestamp: datetime

    @staticmethod
    def from_signal(signal: Signal, quantity: Decimal, timestamp: datetime) -> Order:
        side = Side.BUY if signal.signal_type == SignalType.LONG else Side.SELL
        return Order(
            order_id=uuid4().hex[:12],
            pair=signal.pair,
            side=side,
            quantity=quantity,
            order_type=OrderType.MARKET,
            price=signal.entry_price,
            stop_loss=signal.stop_loss,
            take_profit=signal.take_profit,
            timestamp=timestamp,
        )


@dataclass
class Position:
    position_id: str
    order: Order
    fill_price: Decimal
    status: PositionStatus = PositionStatus.OPEN
    close_price: Decimal | None = None
    close_timestamp: datetime | None = None
    pnl: Decimal = Decimal("0")

    @property
    def pair(self) -> Pair:
        return self.order.pair

    @property
    def side(self) -> Side:
        return self.order.side

    @property
    def quantity(self) -> Decimal:
        return self.order.quantity

    def close(self, price: Decimal, timestamp: datetime) -> None:
        self.status = PositionStatus.CLOSED
        self.close_price = price
        self.close_timestamp = timestamp
        if self.side == Side.BUY:
            self.pnl = (price - self.fill_price) * self.quantity
        else:
            self.pnl = (self.fill_price - price) * self.quantity


@dataclass(frozen=True)
class OHLCV:
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
