"""Tests for performance metrics."""

from datetime import datetime
from decimal import Decimal

from fxagent.domain.models import Order, Position, Signal
from fxagent.ledger.trade_ledger import TradeLedger
from fxagent.metrics.performance import calculate_performance, format_report
from fxagent.types import Pair, SignalType


def _make_trade(pnl_offset: Decimal) -> Position:
    signal = Signal(
        pair=Pair.USDJPY,
        signal_type=SignalType.LONG,
        timestamp=datetime(2024, 1, 2, 10, 0),
        entry_price=Decimal("150.000"),
        stop_loss=Decimal("149.800"),
        take_profit=Decimal("150.300"),
    )
    order = Order.from_signal(signal, Decimal("1000"), datetime(2024, 1, 2, 10, 0))
    fill = Decimal("150.000")
    pos = Position(position_id=order.order_id, order=order, fill_price=fill)
    close_price = fill + pnl_offset / Decimal("1000")
    pos.close(close_price, datetime(2024, 1, 2, 11, 0))
    return pos


class TestPerformance:
    def test_empty_ledger(self) -> None:
        ledger = TradeLedger()
        report = calculate_performance(ledger, Decimal("100000"))
        assert report.total_trades == 0
        assert report.win_rate == 0.0

    def test_basic_metrics(self) -> None:
        ledger = TradeLedger()
        # 3 wins, 1 loss
        for pnl in [Decimal("500"), Decimal("300"), Decimal("200"), Decimal("-400")]:
            ledger.record_trade(_make_trade(pnl))

        report = calculate_performance(ledger, Decimal("100000"))
        assert report.total_trades == 4
        assert report.winning_trades == 3
        assert report.losing_trades == 1
        assert report.win_rate == 75.0
        assert report.total_pnl == Decimal("600")

    def test_profit_factor(self) -> None:
        ledger = TradeLedger()
        ledger.record_trade(_make_trade(Decimal("1000")))
        ledger.record_trade(_make_trade(Decimal("-500")))

        report = calculate_performance(ledger, Decimal("100000"))
        assert report.profit_factor == 2.0

    def test_format_report(self) -> None:
        ledger = TradeLedger()
        ledger.record_trade(_make_trade(Decimal("100")))
        report = calculate_performance(ledger, Decimal("100000"))
        text = format_report(report)
        assert "PERFORMANCE REPORT" in text
        assert "Total Trades" in text
