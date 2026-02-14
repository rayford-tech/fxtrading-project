"""Trade ledger — immutable record of all trading activity."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from fxagent.domain.events import Event
from fxagent.domain.models import Position


@dataclass
class TradeRecord:
    position_id: str
    pair: str
    side: str
    quantity: Decimal
    entry_price: Decimal
    exit_price: Decimal
    pnl: Decimal
    entry_time: datetime
    exit_time: datetime


class TradeLedger:
    """Append-only ledger of completed trades and events."""

    def __init__(self) -> None:
        self._trades: list[TradeRecord] = []
        self._events: list[Event] = []

    def record_trade(self, position: Position) -> None:
        if position.close_price is None or position.close_timestamp is None:
            raise ValueError("Cannot record an open position")

        record = TradeRecord(
            position_id=position.position_id,
            pair=position.pair.value,
            side=position.side.value,
            quantity=position.quantity,
            entry_price=position.fill_price,
            exit_price=position.close_price,
            pnl=position.pnl,
            entry_time=position.order.timestamp,
            exit_time=position.close_timestamp,
        )
        self._trades.append(record)

    def record_event(self, event: Event) -> None:
        self._events.append(event)

    @property
    def trades(self) -> list[TradeRecord]:
        return list(self._trades)

    @property
    def events(self) -> list[Event]:
        return list(self._events)

    @property
    def total_pnl(self) -> Decimal:
        return sum((t.pnl for t in self._trades), Decimal("0"))

    @property
    def trade_count(self) -> int:
        return len(self._trades)

    def daily_pnl(self, date: datetime) -> Decimal:
        day = date.date()
        return sum(
            (t.pnl for t in self._trades if t.exit_time.date() == day),
            Decimal("0"),
        )
