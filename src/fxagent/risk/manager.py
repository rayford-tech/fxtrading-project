"""Risk manager — gate that approves/rejects/sizes orders."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from fxagent.config import Settings
from fxagent.domain.events import DailyLossLimitHit, RiskRejected
from fxagent.domain.models import Position, Signal
from fxagent.types import PositionStatus


@dataclass
class RiskDecision:
    approved: bool
    quantity: Decimal
    reason: str


class RiskManager:
    def __init__(self, settings: Settings) -> None:
        self._s = settings

    def evaluate(
        self,
        signal: Signal,
        equity: Decimal,
        daily_pnl: Decimal,
        open_positions: list[Position],
        current_spread: Decimal,
        current_atr: Decimal,
    ) -> RiskDecision | RiskRejected | DailyLossLimitHit:
        # Daily loss kill switch
        max_loss = equity * self._s.max_daily_loss
        if daily_pnl < -max_loss:
            return DailyLossLimitHit(
                timestamp=signal.timestamp,
                daily_pnl=daily_pnl,
                limit=max_loss,
            )

        # Max concurrent positions
        open_count = sum(1 for p in open_positions if p.status == PositionStatus.OPEN)
        if open_count >= self._s.max_concurrent_positions:
            return RiskRejected(
                timestamp=signal.timestamp,
                reason=f"Max concurrent positions ({self._s.max_concurrent_positions}) reached",
                pair=signal.pair,
                signal_type=signal.signal_type,
            )

        # No duplicate pair positions
        for p in open_positions:
            if p.status == PositionStatus.OPEN and p.pair == signal.pair:
                return RiskRejected(
                    timestamp=signal.timestamp,
                    reason=f"Already have open position on {signal.pair.value}",
                    pair=signal.pair,
                    signal_type=signal.signal_type,
                )

        # Spread/ATR ratio gate
        if current_atr > 0:
            spread_ratio = current_spread / current_atr
            if spread_ratio > self._s.spread_atr_max_ratio:
                return RiskRejected(
                    timestamp=signal.timestamp,
                    reason=f"Spread/ATR ratio {spread_ratio:.4f} exceeds {self._s.spread_atr_max_ratio}",
                    pair=signal.pair,
                    signal_type=signal.signal_type,
                )

        # Position sizing: risk 1% of equity
        risk_amount = equity * self._s.risk_per_trade
        sl_distance = abs(signal.entry_price - signal.stop_loss)
        if sl_distance <= 0:
            return RiskRejected(
                timestamp=signal.timestamp,
                reason="Stop loss distance is zero",
                pair=signal.pair,
                signal_type=signal.signal_type,
            )

        quantity = risk_amount / sl_distance
        # Round to whole units
        quantity = Decimal(int(quantity))

        if quantity <= 0:
            return RiskRejected(
                timestamp=signal.timestamp,
                reason="Calculated position size is zero",
                pair=signal.pair,
                signal_type=signal.signal_type,
            )

        return RiskDecision(
            approved=True,
            quantity=quantity,
            reason="Approved",
        )
