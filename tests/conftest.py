"""Shared test fixtures."""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal

import numpy as np
import pandas as pd
import pytest

from fxagent.config import Settings
from fxagent.domain.models import Order, Position, Signal
from fxagent.types import Pair, SignalType


@pytest.fixture
def settings() -> Settings:
    return Settings(initial_equity=Decimal("100000"))


@pytest.fixture
def sample_ohlcv_df() -> pd.DataFrame:
    """Generate a synthetic M5 OHLCV DataFrame with ~200 bars."""
    np.random.seed(42)
    n = 200
    base_time = datetime(2024, 1, 2, 8, 0)
    timestamps = [base_time + timedelta(minutes=5 * i) for i in range(n)]

    # Random walk price starting at 150.0 (USDJPY-like)
    returns = np.random.normal(0, 0.0005, n)
    prices = 150.0 * np.exp(np.cumsum(returns))

    opens = prices
    highs = prices * (1 + np.abs(np.random.normal(0, 0.0003, n)))
    lows = prices * (1 - np.abs(np.random.normal(0, 0.0003, n)))
    closes = prices * (1 + np.random.normal(0, 0.0002, n))
    volumes = np.random.randint(100, 10000, n).astype(float)

    return pd.DataFrame({
        "timestamp": timestamps,
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    })


@pytest.fixture
def sample_signal() -> Signal:
    return Signal(
        pair=Pair.USDJPY,
        signal_type=SignalType.LONG,
        timestamp=datetime(2024, 1, 2, 10, 0),
        entry_price=Decimal("150.000"),
        stop_loss=Decimal("149.800"),
        take_profit=Decimal("150.300"),
        strength=55.0,
    )


@pytest.fixture
def sample_order(sample_signal: Signal) -> Order:
    return Order.from_signal(
        sample_signal,
        quantity=Decimal("5000"),
        timestamp=datetime(2024, 1, 2, 10, 0),
    )


@pytest.fixture
def sample_position(sample_order: Order) -> Position:
    return Position(
        position_id=sample_order.order_id,
        order=sample_order,
        fill_price=Decimal("150.010"),
    )
