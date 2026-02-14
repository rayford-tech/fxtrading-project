"""Tests for trade ledger."""

from datetime import datetime
from decimal import Decimal

from fxagent.domain.events import SignalGenerated
from fxagent.domain.models import Order, Position, Signal
from fxagent.ledger.trade_ledger import TradeLedger
from fxagent.types import Pair, SignalType


def _closed_position(pnl_value: str = "100") -> Position:
    signal = Signal(
        pair=Pair.USDJPY,
        signal_type=SignalType.LONG,
        timestamp=datetime(2024, 1, 2, 10, 0),
        entry_price=Decimal("150.000"),
        stop_loss=Decimal("149.800"),
        take_profit=Decimal("150.300"),
    )
    order = Order.from_signal(signal, Decimal("1000"), datetime(2024, 1, 2, 10, 0))
    pos = Position(position_id=order.order_id, order=order, fill_price=Decimal("150.010"))
    pos.close(Decimal("150.110"), datetime(2024, 1, 2, 11, 0))
    return pos


class TestTradeLedger:
    def test_record_trade(self) -> None:
        ledger = TradeLedger()
        pos = _closed_position()
        ledger.record_trade(pos)
        assert ledger.trade_count == 1

    def test_total_pnl(self) -> None:
        ledger = TradeLedger()
        pos = _closed_position()
        ledger.record_trade(pos)
        assert ledger.total_pnl == pos.pnl

    def test_record_event(self) -> None:
        ledger = TradeLedger()
        event = SignalGenerated(
            timestamp=datetime(2024, 1, 2, 10, 0),
            pair=Pair.USDJPY,
            signal_type=SignalType.LONG,
            entry_price=Decimal("150.0"),
            stop_loss=Decimal("149.8"),
            take_profit=Decimal("150.3"),
        )
        ledger.record_event(event)
        assert len(ledger.events) == 1

    def test_daily_pnl(self) -> None:
        ledger = TradeLedger()
        pos = _closed_position()
        ledger.record_trade(pos)
        result = ledger.daily_pnl(datetime(2024, 1, 2, 12, 0))
        assert result == pos.pnl

    def test_open_position_raises(self) -> None:
        ledger = TradeLedger()
        signal = Signal(
            pair=Pair.USDJPY,
            signal_type=SignalType.LONG,
            timestamp=datetime(2024, 1, 2, 10, 0),
            entry_price=Decimal("150.000"),
            stop_loss=Decimal("149.800"),
            take_profit=Decimal("150.300"),
        )
        order = Order.from_signal(signal, Decimal("1000"), datetime(2024, 1, 2, 10, 0))
        pos = Position(position_id=order.order_id, order=order, fill_price=Decimal("150.010"))
        import pytest
        with pytest.raises(ValueError, match="Cannot record an open position"):
            ledger.record_trade(pos)
