"""Spread and slippage simulation for realistic order fills."""

from __future__ import annotations

from decimal import Decimal

from fxagent.config import Settings
from fxagent.types import Pair, Side


class FillSimulator:
    """Simulates realistic fill prices with spread and slippage."""

    def __init__(self, settings: Settings) -> None:
        self._s = settings

    def simulate_fill(self, pair: Pair, side: Side, mid_price: Decimal) -> Decimal:
        spread = self._s.default_spread_pips * pair.pip_value
        slippage = self._s.slippage_pips * pair.pip_value

        half_spread = spread / 2
        if side == Side.BUY:
            # Buy at ask (mid + half spread) + slippage
            return mid_price + half_spread + slippage
        else:
            # Sell at bid (mid - half spread) - slippage
            return mid_price - half_spread - slippage

    def get_spread(self, pair: Pair) -> Decimal:
        return self._s.default_spread_pips * pair.pip_value
