"""CLI interface using Typer."""

from __future__ import annotations

from pathlib import Path

import typer

from fxagent.backtest.engine import BacktestEngine
from fxagent.config import Settings
from fxagent.data.ingestion import CSVProvider
from fxagent.metrics.performance import format_report
from fxagent.types import Pair

app = typer.Typer(name="fxagent", help="FX Trading Agent - M5 Scalping System")


@app.command()
def backtest(
    data_dir: Path = typer.Option("./data", help="Directory containing OHLCV data files"),
    pair: str = typer.Option("USDJPY", help="Currency pair (USDJPY or GBPUSD)"),
    timeframe: str = typer.Option("5min", help="Timeframe for OHLCV data"),
) -> None:
    """Run a backtest on historical data."""
    try:
        currency_pair = Pair(pair)
    except ValueError:
        typer.echo(f"Invalid pair: {pair}. Must be one of: {[p.value for p in Pair]}")
        raise typer.Exit(1) from None

    settings = Settings()
    provider = CSVProvider(data_dir)
    engine = BacktestEngine(provider=provider, settings=settings)

    typer.echo(f"Running backtest: {currency_pair.value} @ {timeframe}")
    typer.echo(f"Initial equity: {settings.initial_equity:,.2f}")
    typer.echo("")

    result = engine.run(currency_pair, timeframe)

    typer.echo(format_report(result.report))
    typer.echo(f"\nFinal Equity: {result.final_equity:,.2f}")


@app.command()
def info() -> None:
    """Show current configuration."""
    settings = Settings()
    typer.echo("FX Agent Configuration")
    typer.echo("=" * 40)
    for field_name, value in settings.model_dump().items():
        typer.echo(f"  {field_name}: {value}")


if __name__ == "__main__":
    app()
