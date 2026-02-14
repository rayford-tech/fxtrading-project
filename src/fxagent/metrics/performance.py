"""Performance metrics calculation."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from fxagent.ledger.trade_ledger import TradeLedger


@dataclass
class PerformanceReport:
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: Decimal
    avg_pnl: Decimal
    max_win: Decimal
    max_loss: Decimal
    profit_factor: float
    avg_rr: float
    max_drawdown: Decimal
    sharpe_ratio: float


def calculate_performance(ledger: TradeLedger, initial_equity: Decimal) -> PerformanceReport:
    trades = ledger.trades
    total = len(trades)

    if total == 0:
        return PerformanceReport(
            total_trades=0,
            winning_trades=0,
            losing_trades=0,
            win_rate=0.0,
            total_pnl=Decimal("0"),
            avg_pnl=Decimal("0"),
            max_win=Decimal("0"),
            max_loss=Decimal("0"),
            profit_factor=0.0,
            avg_rr=0.0,
            max_drawdown=Decimal("0"),
            sharpe_ratio=0.0,
        )

    pnls = [t.pnl for t in trades]
    winners = [p for p in pnls if p > 0]
    losers = [p for p in pnls if p < 0]

    total_pnl = sum(pnls, Decimal("0"))
    gross_profit = sum(winners, Decimal("0"))
    gross_loss = abs(sum(losers, Decimal("0")))

    profit_factor = float(gross_profit / gross_loss) if gross_loss > 0 else float("inf")

    # Max drawdown
    equity_curve: list[Decimal] = []
    running_equity = initial_equity
    for pnl in pnls:
        running_equity += pnl
        equity_curve.append(running_equity)

    peak = initial_equity
    max_dd = Decimal("0")
    for eq in equity_curve:
        if eq > peak:
            peak = eq
        dd = peak - eq
        if dd > max_dd:
            max_dd = dd

    # Sharpe ratio (simplified: daily returns approximation)
    avg_pnl_float = float(total_pnl) / total
    if total > 1:
        variance = sum((float(p) - avg_pnl_float) ** 2 for p in pnls) / (total - 1)
        std_dev = variance**0.5
        sharpe = (avg_pnl_float / std_dev * (252**0.5)) if std_dev > 0 else 0.0
    else:
        sharpe = 0.0

    # Average risk/reward
    avg_win = float(sum(winners, Decimal("0"))) / len(winners) if winners else 0.0
    avg_loss_val = float(abs(sum(losers, Decimal("0")))) / len(losers) if losers else 0.0
    avg_rr = avg_win / avg_loss_val if avg_loss_val > 0 else 0.0

    return PerformanceReport(
        total_trades=total,
        winning_trades=len(winners),
        losing_trades=len(losers),
        win_rate=len(winners) / total * 100,
        total_pnl=total_pnl,
        avg_pnl=Decimal(str(round(float(total_pnl) / total, 2))),
        max_win=max(pnls),
        max_loss=min(pnls),
        profit_factor=round(profit_factor, 2),
        avg_rr=round(avg_rr, 2),
        max_drawdown=max_dd,
        sharpe_ratio=round(sharpe, 2),
    )


def format_report(report: PerformanceReport) -> str:
    lines = [
        "=" * 50,
        "PERFORMANCE REPORT",
        "=" * 50,
        f"Total Trades:     {report.total_trades}",
        f"Win Rate:         {report.win_rate:.1f}%",
        f"Total PnL:        {report.total_pnl:,.2f}",
        f"Avg PnL/Trade:    {report.avg_pnl:,.2f}",
        f"Max Win:          {report.max_win:,.2f}",
        f"Max Loss:         {report.max_loss:,.2f}",
        f"Profit Factor:    {report.profit_factor:.2f}",
        f"Avg R:R:          {report.avg_rr:.2f}",
        f"Max Drawdown:     {report.max_drawdown:,.2f}",
        f"Sharpe Ratio:     {report.sharpe_ratio:.2f}",
        "=" * 50,
    ]
    return "\n".join(lines)
