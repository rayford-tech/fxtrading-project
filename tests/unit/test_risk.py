"""Tests for risk manager."""

from datetime import datetime
from decimal import Decimal

from fxagent.config import Settings
from fxagent.domain.events import DailyLossLimitHit, RiskRejected
from fxagent.domain.models import Order, Position, Signal
from fxagent.risk.manager import RiskDecision, RiskManager
from fxagent.types import Pair, SignalType


def _make_signal(pair: Pair = Pair.USDJPY) -> Signal:
    return Signal(
        pair=pair,
        signal_type=SignalType.LONG,
        timestamp=datetime(2024, 1, 2, 10, 0),
        entry_price=Decimal("150.000"),
        stop_loss=Decimal("149.800"),
        take_profit=Decimal("150.300"),
    )


def _make_position(pair: Pair = Pair.USDJPY) -> Position:
    signal = _make_signal(pair)
    order = Order.from_signal(signal, Decimal("1000"), datetime(2024, 1, 2, 10, 0))
    return Position(position_id=order.order_id, order=order, fill_price=Decimal("150.010"))


class TestRiskManager:
    def test_approve_valid_signal(self, settings: Settings) -> None:
        rm = RiskManager(settings)
        result = rm.evaluate(
            signal=_make_signal(),
            equity=Decimal("100000"),
            daily_pnl=Decimal("0"),
            open_positions=[],
            current_spread=Decimal("0.015"),
            current_atr=Decimal("0.200"),
        )
        assert isinstance(result, RiskDecision)
        assert result.approved
        assert result.quantity > 0

    def test_reject_daily_loss_limit(self, settings: Settings) -> None:
        rm = RiskManager(settings)
        result = rm.evaluate(
            signal=_make_signal(),
            equity=Decimal("100000"),
            daily_pnl=Decimal("-5000"),
            open_positions=[],
            current_spread=Decimal("0.015"),
            current_atr=Decimal("0.200"),
        )
        assert isinstance(result, DailyLossLimitHit)

    def test_reject_max_positions(self, settings: Settings) -> None:
        rm = RiskManager(settings)
        positions = [
            _make_position(Pair.GBPUSD),
            _make_position(Pair.GBPUSD),
            _make_position(Pair.GBPUSD),
        ]
        result = rm.evaluate(
            signal=_make_signal(),
            equity=Decimal("100000"),
            daily_pnl=Decimal("0"),
            open_positions=positions,
            current_spread=Decimal("0.015"),
            current_atr=Decimal("0.200"),
        )
        assert isinstance(result, RiskRejected)
        assert "Max concurrent" in result.reason

    def test_reject_duplicate_pair(self, settings: Settings) -> None:
        rm = RiskManager(settings)
        result = rm.evaluate(
            signal=_make_signal(Pair.USDJPY),
            equity=Decimal("100000"),
            daily_pnl=Decimal("0"),
            open_positions=[_make_position(Pair.USDJPY)],
            current_spread=Decimal("0.015"),
            current_atr=Decimal("0.200"),
        )
        assert isinstance(result, RiskRejected)
        assert "Already have" in result.reason

    def test_reject_high_spread_atr(self, settings: Settings) -> None:
        rm = RiskManager(settings)
        result = rm.evaluate(
            signal=_make_signal(),
            equity=Decimal("100000"),
            daily_pnl=Decimal("0"),
            open_positions=[],
            current_spread=Decimal("0.100"),
            current_atr=Decimal("0.100"),  # ratio = 1.0 > 0.3
        )
        assert isinstance(result, RiskRejected)
        assert "Spread/ATR" in result.reason

    def test_position_sizing(self, settings: Settings) -> None:
        rm = RiskManager(settings)
        result = rm.evaluate(
            signal=_make_signal(),
            equity=Decimal("100000"),
            daily_pnl=Decimal("0"),
            open_positions=[],
            current_spread=Decimal("0.015"),
            current_atr=Decimal("0.200"),
        )
        assert isinstance(result, RiskDecision)
        # 1% of 100000 = 1000; SL distance = 0.200; qty = 1000/0.200 = 5000
        assert result.quantity == Decimal("5000")
