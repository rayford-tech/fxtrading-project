"""Integration test — full backtest run."""

from decimal import Decimal

import pandas as pd

from fxagent.backtest.engine import BacktestEngine
from fxagent.config import Settings
from fxagent.data.ingestion import DataFrameProvider
from fxagent.types import Pair


class TestFullBacktest:
    def test_backtest_runs_to_completion(self, sample_ohlcv_df: pd.DataFrame) -> None:
        provider = DataFrameProvider({("USDJPY", "5min"): sample_ohlcv_df})
        settings = Settings(initial_equity=Decimal("100000"))
        engine = BacktestEngine(provider=provider, settings=settings)

        result = engine.run(Pair.USDJPY, "5min")

        assert result.report.total_trades >= 0
        assert result.final_equity > 0
        assert result.ledger is not None

    def test_backtest_events_recorded(self, sample_ohlcv_df: pd.DataFrame) -> None:
        provider = DataFrameProvider({("USDJPY", "5min"): sample_ohlcv_df})
        settings = Settings(initial_equity=Decimal("100000"))
        engine = BacktestEngine(provider=provider, settings=settings)

        result = engine.run(Pair.USDJPY, "5min")

        # Events should be recorded even if no trades happen
        assert isinstance(result.ledger.events, list)

    def test_backtest_equity_conservation(self, sample_ohlcv_df: pd.DataFrame) -> None:
        """Final equity should equal initial + total PnL."""
        provider = DataFrameProvider({("USDJPY", "5min"): sample_ohlcv_df})
        settings = Settings(initial_equity=Decimal("100000"))
        engine = BacktestEngine(provider=provider, settings=settings)

        result = engine.run(Pair.USDJPY, "5min")

        expected_equity = settings.initial_equity + result.ledger.total_pnl
        assert result.final_equity == expected_equity

    def test_multi_pair_backtest(self, sample_ohlcv_df: pd.DataFrame) -> None:
        provider = DataFrameProvider({
            ("USDJPY", "5min"): sample_ohlcv_df,
            ("GBPUSD", "5min"): sample_ohlcv_df,
        })
        settings = Settings(initial_equity=Decimal("100000"))
        engine = BacktestEngine(provider=provider, settings=settings)

        results = engine.run_multi([Pair.USDJPY, Pair.GBPUSD], "5min")

        assert len(results) == 2
        for r in results:
            assert r.final_equity > 0
