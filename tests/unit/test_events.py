"""Tests for domain events."""

from datetime import datetime
from decimal import Decimal

from fxagent.domain.events import (
    DailyLossLimitHit,
    OrderPlaced,
    RiskRejected,
    SignalGenerated,
)
from fxagent.types import Pair, Side, SignalType


class TestEvents:
    def test_signal_generated(self) -> None:
        event = SignalGenerated(
            timestamp=datetime(2024, 1, 2, 10, 0),
            pair=Pair.USDJPY,
            signal_type=SignalType.LONG,
            entry_price=Decimal("150.0"),
            stop_loss=Decimal("149.8"),
            take_profit=Decimal("150.3"),
        )
        assert event.pair == Pair.USDJPY

    def test_order_placed(self) -> None:
        event = OrderPlaced(
            timestamp=datetime(2024, 1, 2, 10, 0),
            order_id="abc123",
            pair=Pair.USDJPY,
            side=Side.BUY,
            quantity=Decimal("1000"),
            price=Decimal("150.0"),
        )
        assert event.order_id == "abc123"

    def test_risk_rejected(self) -> None:
        event = RiskRejected(
            timestamp=datetime(2024, 1, 2, 10, 0),
            reason="Max positions reached",
            pair=Pair.USDJPY,
            signal_type=SignalType.LONG,
        )
        assert "Max positions" in event.reason

    def test_daily_loss_limit(self) -> None:
        event = DailyLossLimitHit(
            timestamp=datetime(2024, 1, 2, 10, 0),
            daily_pnl=Decimal("-3500"),
            limit=Decimal("3000"),
        )
        assert event.daily_pnl < 0
