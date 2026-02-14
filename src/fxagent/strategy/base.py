"""Base strategy protocol."""

from __future__ import annotations

from typing import Protocol

import pandas as pd

from fxagent.domain.models import Signal
from fxagent.types import Pair


class Strategy(Protocol):
    def evaluate(self, pair: Pair, df: pd.DataFrame, idx: int) -> Signal | None: ...
