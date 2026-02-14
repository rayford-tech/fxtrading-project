"""Paper trading broker implementation."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from fxagent.domain.models import Order, Position
from fxagent.execution.simulator import FillSimulator
from fxagent.types import OrderType, Pair, PositionStatus, Side


class PaperBroker:
    """Simulated broker for backtesting and paper trading."""

    def __init__(self, simulator: FillSimulator) -> None:
        self._simulator = simulator
        self._orders: dict[str, Order] = {}
        self._positions: dict[str, Position] = {}
        self._fill_prices: dict[str, Decimal] = {}

    def submit_order(
        self,
        pair: Pair,
        side: Side,
        quantity: Decimal,
        order_type: OrderType,
        price: Decimal,
        stop_loss: Decimal,
        take_profit: Decimal,
    ) -> str:
        order_id = uuid4().hex[:12]
        order = Order(
            order_id=order_id,
            pair=pair,
            side=side,
            quantity=quantity,
            order_type=order_type,
            price=price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            timestamp=datetime.now(),
        )
        self._orders[order_id] = order

        # Immediate fill for market orders
        if order_type == OrderType.MARKET:
            fill_price = self._simulator.simulate_fill(pair, side, price)
            self._fill_prices[order_id] = fill_price
            position = Position(
                position_id=order_id,
                order=order,
                fill_price=fill_price,
            )
            self._positions[order_id] = position

        return order_id

    def cancel_order(self, order_id: str) -> bool:
        if order_id in self._orders:
            del self._orders[order_id]
            return True
        return False

    def get_position(self, order_id: str) -> PositionStatus:
        pos = self._positions.get(order_id)
        if pos is None:
            return PositionStatus.CLOSED
        return pos.status

    def get_fill_price(self, order_id: str) -> Decimal:
        return self._fill_prices.get(order_id, Decimal("0"))

    def get_open_positions(self) -> list[Position]:
        return [p for p in self._positions.values() if p.status == PositionStatus.OPEN]

    def get_all_positions(self) -> list[Position]:
        return list(self._positions.values())

    def check_sl_tp(self, high: Decimal, low: Decimal, timestamp: datetime) -> list[Position]:
        """Check and close positions that hit SL or TP. Returns closed positions."""
        closed: list[Position] = []
        for pos in self._positions.values():
            if pos.status != PositionStatus.OPEN:
                continue

            order = pos.order
            if pos.side == Side.BUY:
                # SL hit if low <= stop_loss
                if low <= order.stop_loss:
                    pos.close(order.stop_loss, timestamp)
                    closed.append(pos)
                # TP hit if high >= take_profit
                elif high >= order.take_profit:
                    pos.close(order.take_profit, timestamp)
                    closed.append(pos)
            else:
                # Short: SL hit if high >= stop_loss
                if high >= order.stop_loss:
                    pos.close(order.stop_loss, timestamp)
                    closed.append(pos)
                # TP hit if low <= take_profit
                elif low <= order.take_profit:
                    pos.close(order.take_profit, timestamp)
                    closed.append(pos)

        return closed
