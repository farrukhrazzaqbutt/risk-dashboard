from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Side = Literal["BUY", "SELL"]


class InstrumentConfig(BaseModel):
    symbol: str
    start_price: float
    spread_bps: float
    volatility_bps: float


class PriceTick(BaseModel):
    symbol: str
    bid: float
    ask: float
    mid: float
    ts: datetime


class TradeEvent(BaseModel):
    trade_id: int
    client_id: str
    symbol: str
    side: Side
    quantity: float
    price: float
    ts: datetime


class PositionSnapshot(BaseModel):
    symbol: str
    quantity: float
    avg_price: float
    market_price: float
    unrealized_pnl: float


class PnLPoint(BaseModel):
    ts: datetime
    total_pnl: float


class DashboardSnapshot(BaseModel):
    ts: datetime
    total_pnl: float
    realized_pnl: float
    unrealized_pnl: float
    monetization: float
    client_yield: float
    trade_count: int
    positions: list[PositionSnapshot] = Field(default_factory=list)
    recent_trades: list[TradeEvent] = Field(default_factory=list)
    pnl_history: list[PnLPoint] = Field(default_factory=list)
    pnl_attribution: dict[str, float] = Field(default_factory=dict)
    # Gross notional exposure per symbol: abs(quantity) * mid (MVP cross-terms ignored).
    notional_by_instrument: dict[str, float] = Field(default_factory=dict)
    # Cumulative simplified PnL proxy per client (for desk-style attribution).
    client_pnl: dict[str, float] = Field(default_factory=dict)
    prices: dict[str, PriceTick] = Field(default_factory=dict)
