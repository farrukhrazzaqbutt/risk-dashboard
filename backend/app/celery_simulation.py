from __future__ import annotations

import asyncio
import logging
import os

from .instruments_data import CLIENTS, INSTRUMENTS
from .simulator import run_price_simulation, run_trade_simulation
from .snapshot_persist import run_snapshot_persist_loop
from .snapshot_store import get_redis_client
from .state import BookState

logger = logging.getLogger(__name__)


def run_celery_simulation_forever() -> None:
    """
    Event loop for mock feeds + in-memory book (worker only).

    The API process reads snapshots from Redis; WebSocket fan-out stays in Uvicorn.
    """
    logger.info(
        "Celery simulation: starting asyncio loop (price, trades, snapshot -> Redis)"
    )

    r = get_redis_client()
    state = BookState(INSTRUMENTS, CLIENTS)
    interval = float(os.getenv("BROADCAST_INTERVAL_SEC", "0.5"))

    async def _main() -> None:
        await asyncio.gather(
            run_price_simulation(state),
            run_trade_simulation(state),
            run_snapshot_persist_loop(state, r, interval),
        )

    asyncio.run(_main())
