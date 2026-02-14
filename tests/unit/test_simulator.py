"""Tests for fill simulator."""

from decimal import Decimal

from fxagent.config import Settings
from fxagent.execution.simulator import FillSimulator
from fxagent.types import Pair, Side


class TestFillSimulator:
    def test_buy_fill_above_mid(self) -> None:
        settings = Settings()
        sim = FillSimulator(settings)
        mid = Decimal("150.000")
        fill = sim.simulate_fill(Pair.USDJPY, Side.BUY, mid)
        assert fill > mid

    def test_sell_fill_below_mid(self) -> None:
        settings = Settings()
        sim = FillSimulator(settings)
        mid = Decimal("150.000")
        fill = sim.simulate_fill(Pair.USDJPY, Side.SELL, mid)
        assert fill < mid

    def test_spread_calculation(self) -> None:
        settings = Settings(default_spread_pips=Decimal("2.0"))
        sim = FillSimulator(settings)
        spread = sim.get_spread(Pair.USDJPY)
        assert spread == Decimal("0.02")  # 2.0 pips * 0.01

    def test_gbpusd_pip_value(self) -> None:
        settings = Settings(default_spread_pips=Decimal("1.0"))
        sim = FillSimulator(settings)
        spread = sim.get_spread(Pair.GBPUSD)
        assert spread == Decimal("0.0001")
