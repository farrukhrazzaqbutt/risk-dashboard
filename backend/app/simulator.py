from __future__ import annotations

import asyncio
import logging
import os
import random

from .metrics import calculate_spread_capture
from .models import TradeEvent
from .state import BookState, utc_now

logger = logging.getLogger(__name__)

# >1 speeds up mock feeds (e.g. 10 to stress-test UI throttling vs backend).
SIMULATION_LOAD_MULTIPLIER = max(float(os.getenv("SIMULATION_LOAD_MULTIPLIER", "1")), 0.01)


def update_position_with_trade(
    state: BookState, symbol: str, book_delta: float, trade_price: float
) -> float:
    """
    Applies weighted-average price updates and realizes pnl when reducing/reversing.
    book_delta: +qty means we bought (longer), -qty means we sold (shorter).
    Returns realized pnl impact.
    """
    current_qty = state.positions_qty[symbol]
    current_avg = state.avg_price[symbol]

    if current_qty == 0:
        state.positions_qty[symbol] = book_delta
        state.avg_price[symbol] = trade_price
        return 0.0

    same_direction = current_qty * book_delta > 0
    if same_direction:
        new_qty = current_qty + book_delta
        weighted_avg = ((abs(current_qty) * current_avg) + (abs(book_delta) * trade_price)) / abs(
            new_qty
        )
        state.positions_qty[symbol] = new_qty
        state.avg_price[symbol] = weighted_avg
        return 0.0

    close_qty = min(abs(current_qty), abs(book_delta))
    if current_qty > 0:
        realized = close_qty * (trade_price - current_avg)
    else:
        realized = close_qty * (current_avg - trade_price)

    new_qty = current_qty + book_delta
    state.positions_qty[symbol] = new_qty
    if new_qty == 0:
        state.avg_price[symbol] = 0.0
    elif abs(book_delta) > abs(current_qty):
        state.avg_price[symbol] = trade_price

    return realized


async def run_price_simulation(state: BookState) -> None:
    tick_sec = 0.2 / SIMULATION_LOAD_MULTIPLIER
    logger.info(
        "Price simulation task started (tick interval=%.0fms, load_multiplier=%s)",
        tick_sec * 1000,
        SIMULATION_LOAD_MULTIPLIER,
    )
    while True:
        async with state.lock:
            for _symbol, symbol_state in state.symbols.items():
                vol = symbol_state.config.volatility_bps / 10000
                shock = random.gauss(0, vol)
                symbol_state.mid = max(0.0001, symbol_state.mid * (1 + shock))

                spread = symbol_state.mid * (symbol_state.config.spread_bps / 10000)
                symbol_state.bid = symbol_state.mid - spread / 2
                symbol_state.ask = symbol_state.mid + spread / 2
        await asyncio.sleep(tick_sec)


async def run_trade_simulation(state: BookState) -> None:
    logger.info(
        "Trade simulation task started (random interval ~150-800ms / load_multiplier=%s)",
        SIMULATION_LOAD_MULTIPLIER,
    )
    symbols = list(state.symbols.keys())
    while True:
        await asyncio.sleep(random.uniform(0.15, 0.8) / SIMULATION_LOAD_MULTIPLIER)
        async with state.lock:
            symbol = random.choice(symbols)
            client_id = random.choice(state.clients)
            side = random.choice(["BUY", "SELL"])
            quantity = random.choice([10000, 20000, 30000, 50000, 80000])

            sym = state.symbols[symbol]
            trade_price = sym.ask if side == "BUY" else sym.bid

            # Exposure rule: client buys -> we are short, client sells -> we are long.
            book_delta = -quantity if side == "BUY" else quantity
            realized = update_position_with_trade(state, symbol, book_delta, trade_price)
            state.realized_pnl += realized

            spread_capture = calculate_spread_capture(side, trade_price, sym.bid, sym.ask)
            state.monetization += spread_capture * quantity

            state.trade_count += 1
            state.clients_trade_count[client_id] += 1
            state.clients_total_pnl[client_id] += -realized

            trade = TradeEvent(
                trade_id=state.next_trade_id,
                client_id=client_id,
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=trade_price,
                ts=utc_now(),
            )
            state.next_trade_id += 1
            state.recent_trades.appendleft(trade)
            msg = "Trade executed | id=%d | client=%s | %s %s qty=%s @ %.5f | realized=%.4f"
            logger.info(
                msg,
                trade.trade_id,
                client_id,
                symbol,
                side,
                quantity,
                trade_price,
                realized,
            )
