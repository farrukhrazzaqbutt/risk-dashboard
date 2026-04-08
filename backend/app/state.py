from __future__ import annotations

import asyncio
import logging
from collections import deque
from datetime import UTC, datetime

from fastapi import WebSocket

from .models import (
    DashboardSnapshot,
    InstrumentConfig,
    PnLPoint,
    PositionSnapshot,
    PriceTick,
    TradeEvent,
)

logger = logging.getLogger(__name__)


def utc_now() -> datetime:
    return datetime.now(UTC)


class SymbolState:
    def __init__(self, config: InstrumentConfig) -> None:
        self.config = config
        self.mid = config.start_price
        self.bid = config.start_price
        self.ask = config.start_price


class BookState:
    def __init__(self, instruments: list[InstrumentConfig], clients: list[str]) -> None:
        self.lock = asyncio.Lock()
        self.symbols: dict[str, SymbolState] = {ins.symbol: SymbolState(ins) for ins in instruments}
        self.clients = clients

        self.positions_qty: dict[str, float] = {ins.symbol: 0.0 for ins in instruments}
        self.avg_price: dict[str, float] = {ins.symbol: 0.0 for ins in instruments}

        self.realized_pnl = 0.0
        self.unrealized_pnl = 0.0
        self.monetization = 0.0
        self.trade_count = 0

        self.recent_trades: deque[TradeEvent] = deque(maxlen=100)
        self.pnl_history: deque[PnLPoint] = deque(maxlen=500)

        self.next_trade_id = 1
        self.clients_total_pnl: dict[str, float] = {c: 0.0 for c in clients}
        self.clients_trade_count: dict[str, int] = {c: 0 for c in clients}

        self.connections: set[WebSocket] = set()

        logger.info(
            "BookState initialized | instruments=%d | clients=%d | "
            "pnl_history_cap=500 | trades_cap=100",
            len(instruments),
            len(clients),
        )

    def get_price_tick_map(self) -> dict[str, PriceTick]:
        ts = utc_now()
        return {
            symbol: PriceTick(symbol=symbol, bid=st.bid, ask=st.ask, mid=st.mid, ts=ts)
            for symbol, st in self.symbols.items()
        }

    def get_pnl_attribution(self) -> dict[str, float]:
        attribution: dict[str, float] = {}
        for symbol in self.symbols:
            qty = self.positions_qty[symbol]
            avg = self.avg_price[symbol]
            mid = self.symbols[symbol].mid
            if qty >= 0:
                pnl = qty * (mid - avg)
            else:
                pnl = abs(qty) * (avg - mid)
            attribution[symbol] = pnl
        return attribution

    def get_notional_by_instrument(self) -> dict[str, float]:
        """Gross notional: |qty| * mid (single-currency simplification for MVP)."""
        out: dict[str, float] = {}
        for symbol, st in self.symbols.items():
            qty = self.positions_qty[symbol]
            out[symbol] = abs(qty) * st.mid
        return out

    def get_positions_snapshot(self) -> list[PositionSnapshot]:
        positions: list[PositionSnapshot] = []
        for symbol, st in self.symbols.items():
            qty = self.positions_qty[symbol]
            avg = self.avg_price[symbol]
            if qty >= 0:
                unrealized = qty * (st.mid - avg)
            else:
                unrealized = abs(qty) * (avg - st.mid)
            positions.append(
                PositionSnapshot(
                    symbol=symbol,
                    quantity=qty,
                    avg_price=avg,
                    market_price=st.mid,
                    unrealized_pnl=unrealized,
                )
            )
        return positions

    def get_snapshot(self) -> DashboardSnapshot:
        positions = self.get_positions_snapshot()
        self.unrealized_pnl = sum(p.unrealized_pnl for p in positions)
        total_pnl = self.realized_pnl + self.unrealized_pnl

        point = PnLPoint(ts=utc_now(), total_pnl=total_pnl)
        self.pnl_history.append(point)

        client_trade_total = sum(self.clients_trade_count.values())
        client_pnl_total = sum(self.clients_total_pnl.values())
        client_yield = client_pnl_total / client_trade_total if client_trade_total else 0.0

        return DashboardSnapshot(
            ts=utc_now(),
            total_pnl=total_pnl,
            realized_pnl=self.realized_pnl,
            unrealized_pnl=self.unrealized_pnl,
            monetization=self.monetization,
            client_yield=client_yield,
            trade_count=self.trade_count,
            positions=positions,
            recent_trades=list(self.recent_trades),
            pnl_history=list(self.pnl_history),
            pnl_attribution=self.get_pnl_attribution(),
            notional_by_instrument=self.get_notional_by_instrument(),
            client_pnl=dict(self.clients_total_pnl),
            prices=self.get_price_tick_map(),
        )
