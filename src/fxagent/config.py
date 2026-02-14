"""Application configuration using pydantic-settings."""

from __future__ import annotations

from decimal import Decimal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_prefix": "FXAGENT_"}

    initial_equity: Decimal = Decimal("100000")
    risk_per_trade: Decimal = Decimal("0.01")
    max_daily_loss: Decimal = Decimal("0.03")
    max_concurrent_positions: int = 3
    default_spread_pips: Decimal = Decimal("1.5")
    slippage_pips: Decimal = Decimal("0.5")

    # Strategy parameters
    ema_fast: int = 9
    ema_slow: int = 21
    rsi_period: int = 14
    stoch_period: int = 14
    bb_period: int = 20
    bb_std: float = 2.0
    atr_period: int = 14
    atr_sl_multiplier: Decimal = Decimal("1.2")
    atr_tp_multiplier: Decimal = Decimal("1.8")

    # RSI thresholds
    rsi_buy_low: float = 40.0
    rsi_buy_high: float = 65.0
    rsi_sell_low: float = 35.0
    rsi_sell_high: float = 60.0

    # Risk gates
    spread_atr_max_ratio: Decimal = Decimal("0.3")
