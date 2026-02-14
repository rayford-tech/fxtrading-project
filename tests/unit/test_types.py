"""Tests for core types."""

from decimal import Decimal

from fxagent.types import Pair, Side, SignalType


class TestPair:
    def test_pip_value_usdjpy(self) -> None:
        assert Pair.USDJPY.pip_value == Decimal("0.01")

    def test_pip_value_gbpusd(self) -> None:
        assert Pair.GBPUSD.pip_value == Decimal("0.0001")

    def test_enum_values(self) -> None:
        assert Pair.USDJPY.value == "USDJPY"
        assert Pair.GBPUSD.value == "GBPUSD"


class TestSide:
    def test_values(self) -> None:
        assert Side.BUY.value == "BUY"
        assert Side.SELL.value == "SELL"


class TestSignalType:
    def test_values(self) -> None:
        assert SignalType.LONG.value == "LONG"
        assert SignalType.SHORT.value == "SHORT"
        assert SignalType.FLAT.value == "FLAT"
