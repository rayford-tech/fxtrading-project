"""Backtest engine — composition root that orchestrates the trading loop."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

import pandas as pd

from fxagent.config import Settings
from fxagent.domain.events import (
    DailyLossLimitHit,
    OrderFilled,
    OrderPlaced,
    PositionClosed,
    RiskRejected,
    SignalGenerated,
)
from fxagent.domain.models import Order
from fxagent.execution.paper import PaperBroker
from fxagent.execution.simulator import FillSimulator
from fxagent.features.pipeline import enrich
from fxagent.ledger.trade_ledger import TradeLedger
from fxagent.metrics.performance import PerformanceReport, calculate_performance
from fxagent.risk.manager import RiskDecision, RiskManager
from fxagent.strategy.m5_scalper import M5Scalper
from fxagent.types import OHLCVProvider, OrderType, Pair


@dataclass
class BacktestResult:
    report: PerformanceReport
    ledger: TradeLedger
    final_equity: Decimal


class BacktestEngine:
    """Orchestrates a full backtest run."""

    def __init__(
        self,
        provider: OHLCVProvider,
        settings: Settings | None = None,
    ) -> None:
        self._provider = provider
        self._settings = settings or Settings()
        self._strategy = M5Scalper(self._settings)
        self._risk = RiskManager(self._settings)
        self._simulator = FillSimulator(self._settings)
        self._broker = PaperBroker(self._simulator)
        self._ledger = TradeLedger()

    def run(self, pair: Pair, timeframe: str = "5min") -> BacktestResult:
        df = self._provider.load(pair, timeframe)
        df = enrich(df, self._settings)
        equity = self._settings.initial_equity
        daily_loss_halt = False

        for idx in range(len(df)):
            row = df.iloc[idx]
            timestamp = pd.Timestamp(row["timestamp"]).to_pydatetime()

            # Reset daily halt on new day
            if idx > 0:
                prev_ts = pd.Timestamp(df.iloc[idx - 1]["timestamp"]).to_pydatetime()
                if timestamp.date() != prev_ts.date():
                    daily_loss_halt = False

            # Check SL/TP on open positions
            high = Decimal(str(row["high"]))
            low = Decimal(str(row["low"]))
            closed = self._broker.check_sl_tp(high, low, timestamp)
            for pos in closed:
                equity += pos.pnl
                self._ledger.record_trade(pos)
                self._ledger.record_event(
                    PositionClosed(
                        timestamp=timestamp,
                        position_id=pos.position_id,
                        pair=pos.pair,
                        side=pos.side,
                        pnl=pos.pnl,
                        close_price=pos.close_price or Decimal("0"),
                    )
                )

            if daily_loss_halt:
                continue

            # Generate signal
            signal = self._strategy.evaluate(pair, df, idx)
            if signal is None:
                continue

            self._ledger.record_event(
                SignalGenerated(
                    timestamp=timestamp,
                    pair=signal.pair,
                    signal_type=signal.signal_type,
                    entry_price=signal.entry_price,
                    stop_loss=signal.stop_loss,
                    take_profit=signal.take_profit,
                )
            )

            # Risk check
            atr_val = Decimal(str(row["atr"])) if not pd.isna(row.get("atr")) else Decimal("0")
            spread = self._simulator.get_spread(pair)
            daily_pnl = self._ledger.daily_pnl(timestamp)
            open_positions = self._broker.get_open_positions()

            decision = self._risk.evaluate(
                signal=signal,
                equity=equity,
                daily_pnl=daily_pnl,
                open_positions=open_positions,
                current_spread=spread,
                current_atr=atr_val,
            )

            if isinstance(decision, DailyLossLimitHit):
                self._ledger.record_event(decision)
                daily_loss_halt = True
                continue

            if isinstance(decision, RiskRejected):
                self._ledger.record_event(decision)
                continue

            assert isinstance(decision, RiskDecision)

            # Place order
            order = Order.from_signal(signal, decision.quantity, timestamp)
            order_id = self._broker.submit_order(
                pair=order.pair,
                side=order.side,
                quantity=order.quantity,
                order_type=OrderType.MARKET,
                price=order.price,
                stop_loss=order.stop_loss,
                take_profit=order.take_profit,
            )

            fill_price = self._broker.get_fill_price(order_id)
            self._ledger.record_event(
                OrderPlaced(
                    timestamp=timestamp,
                    order_id=order_id,
                    pair=order.pair,
                    side=order.side,
                    quantity=order.quantity,
                    price=order.price,
                )
            )
            self._ledger.record_event(
                OrderFilled(timestamp=timestamp, order_id=order_id, fill_price=fill_price)
            )

        # Close remaining positions at last close price
        last_row = df.iloc[-1]
        last_ts = pd.Timestamp(last_row["timestamp"]).to_pydatetime()
        last_close = Decimal(str(last_row["close"]))
        for pos in self._broker.get_open_positions():
            pos.close(last_close, last_ts)
            equity += pos.pnl
            self._ledger.record_trade(pos)

        report = calculate_performance(self._ledger, self._settings.initial_equity)
        return BacktestResult(report=report, ledger=self._ledger, final_equity=equity)

    def run_multi(self, pairs: list[Pair], timeframe: str = "5min") -> list[BacktestResult]:
        """Run backtest on multiple pairs independently."""
        results: list[BacktestResult] = []
        for pair in pairs:
            # Reset broker and ledger for each pair
            self._broker = PaperBroker(self._simulator)
            self._ledger = TradeLedger()
            results.append(self.run(pair, timeframe))
        return results
