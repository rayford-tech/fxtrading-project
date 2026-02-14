"""Tests for domain models."""

from datetime import datetime
from decimal import Decimal

from fxagent.domain.models import Order, Position, Signal
from fxagent.types import OrderType, Pair, PositionStatus, Side, SignalType


class TestSignal:
    def test_creation(self, sample_signal: Signal) -> None:
        assert sample_signal.pair == Pair.USDJPY
        assert sample_signal.signal_type == SignalType.LONG
        assert sample_signal.entry_price == Decimal("150.000")

    def test_frozen(self, sample_signal: Signal) -> None:
        import pytest

        with pytest.raises(AttributeError):
            sample_signal.pair = Pair.GBPUSD  # type: ignore[misc]


class TestOrder:
    def test_from_signal_long(self, sample_signal: Signal) -> None:
        order = Order.from_signal(sample_signal, Decimal("1000"), datetime(2024, 1, 2, 10, 0))
        assert order.side == Side.BUY
        assert order.quantity == Decimal("1000")
        assert order.order_type == OrderType.MARKET
        assert order.stop_loss == sample_signal.stop_loss

    def test_from_signal_short(self) -> None:
        signal = Signal(
            pair=Pair.GBPUSD,
            signal_type=SignalType.SHORT,
            timestamp=datetime(2024, 1, 2, 10, 0),
            entry_price=Decimal("1.27000"),
            stop_loss=Decimal("1.27200"),
            take_profit=Decimal("1.26700"),
        )
        order = Order.from_signal(signal, Decimal("2000"), datetime(2024, 1, 2, 10, 0))
        assert order.side == Side.SELL


class TestPosition:
    def test_close_long(self, sample_position: Position) -> None:
        sample_position.close(Decimal("150.200"), datetime(2024, 1, 2, 11, 0))
        assert sample_position.status == PositionStatus.CLOSED
        assert sample_position.pnl == (Decimal("150.200") - Decimal("150.010")) * Decimal("5000")

    def test_close_short(self) -> None:
        signal = Signal(
            pair=Pair.USDJPY,
            signal_type=SignalType.SHORT,
            timestamp=datetime(2024, 1, 2, 10, 0),
            entry_price=Decimal("150.000"),
            stop_loss=Decimal("150.200"),
            take_profit=Decimal("149.700"),
        )
        order = Order.from_signal(signal, Decimal("1000"), datetime(2024, 1, 2, 10, 0))
        pos = Position(position_id="test", order=order, fill_price=Decimal("149.990"))
        pos.close(Decimal("149.800"), datetime(2024, 1, 2, 11, 0))
        assert pos.pnl == (Decimal("149.990") - Decimal("149.800")) * Decimal("1000")
