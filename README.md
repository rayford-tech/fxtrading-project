# FX Trading Agent

A production-grade Python AI Forex trading agent for M5 scalping on USDJPY and GBPUSD with backtesting and paper trading capabilities.

## Architecture

```
CSV/Parquet → data/ingestion → features/pipeline → strategy/m5_scalper
                                                          ↓
                                          risk/manager (gate: approve/reject/size)
                                                          ↓
                                          execution/simulator (spread + slippage)
                                                          ↓
                                          ledger/trade_ledger → metrics/performance
                                                          ↓
                                          backtest/engine (orchestrates the loop)
```

## M5 Scalping Strategy

- **EMA(9)/EMA(21)** crossover for trend direction
- **RSI(14)** momentum filter (40–65 buy, 35–60 sell)
- **Stochastic %K(14)** turning point confirmation
- **VWAP** intraday bias
- **Bollinger Bands(20, 2)** squeeze detection
- **ATR(14)**-based SL (1.2×) and TP (1.8×) → 1.5:1 R:R

## Risk Management

- 1% equity per trade
- 3% daily max loss kill switch
- Max 3 concurrent positions
- Spread/ATR ratio gate (reject if > 0.3)

## Project Structure

```
src/fxagent/
├── config.py              Settings via pydantic-settings
├── types.py               Core types, enums, protocols
├── domain/                Models (Signal, Order, Position) and events
├── data/                  CSV/Parquet ingestion, timeframe utilities
├── features/              Pure indicator functions and enrichment pipeline
├── strategy/              Strategy protocol and M5 scalper implementation
├── risk/                  Risk manager gate
├── execution/             Broker protocol, fill simulator, paper broker
├── ledger/                Trade ledger (append-only record)
├── metrics/               Performance report calculation
├── backtest/              Backtest engine (composition root)
└── cli.py                 Typer CLI
```

## Setup

```bash
# Create virtual environment and install
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Or with uv
uv venv .venv && source .venv/bin/activate
uv pip install -e ".[dev]"
```

## Usage

### Run a backtest

```bash
fxagent backtest --data-dir ./data --pair USDJPY --timeframe 5min
```

Data files should be named `{PAIR}_{TIMEFRAME}.csv` (or `.parquet`) with columns: `timestamp`, `open`, `high`, `low`, `close`, `volume`.

### Show configuration

```bash
fxagent info
```

### Configuration via environment variables

Copy `.env.example` to `.env` and adjust values:

```bash
FXAGENT_INITIAL_EQUITY=100000
FXAGENT_RISK_PER_TRADE=0.01
FXAGENT_MAX_DAILY_LOSS=0.03
FXAGENT_MAX_CONCURRENT_POSITIONS=3
FXAGENT_DEFAULT_SPREAD_PIPS=1.5
FXAGENT_SLIPPAGE_PIPS=0.5
```

## Development

```bash
make test       # Run tests with coverage
make lint       # ruff + mypy
make format     # Auto-fix lint issues
make clean      # Remove build artifacts
```

## Docker

```bash
make docker-build
docker run fxagent backtest --help
```

## Design Decisions

- **Decimal** for all prices and quantities (no float rounding errors)
- **Protocol-based DI** for `OHLCVProvider` and `BrokerAdapter`
- **Pure indicator functions** (stateless, pandas Series in/out)
- **Risk manager as gate** — approves, rejects, or sizes; never modifies strategy intent
- **Backtest engine as composition root** — wires all modules with acyclic dependencies
