"""Tests for configuration."""

from decimal import Decimal

from fxagent.config import Settings


class TestSettings:
    def test_defaults(self) -> None:
        s = Settings()
        assert s.initial_equity == Decimal("100000")
        assert s.risk_per_trade == Decimal("0.01")
        assert s.max_concurrent_positions == 3

    def test_custom_values(self) -> None:
        s = Settings(initial_equity=Decimal("50000"), max_concurrent_positions=5)
        assert s.initial_equity == Decimal("50000")
        assert s.max_concurrent_positions == 5

    def test_strategy_params(self) -> None:
        s = Settings()
        assert s.ema_fast == 9
        assert s.ema_slow == 21
        assert s.atr_sl_multiplier == Decimal("1.2")
        assert s.atr_tp_multiplier == Decimal("1.8")
