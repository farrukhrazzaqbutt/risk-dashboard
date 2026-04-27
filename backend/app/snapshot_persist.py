from __future__ import annotations

import asyncio
import json
import logging

import redis

from .snapshot_store import SNAPSHOT_REDIS_KEY
from .state import BookState

logger = logging.getLogger(__name__)


async def run_snapshot_persist_loop(state: BookState, r: redis.Redis, interval_sec: float) -> None:
    """Persists a JSON snapshot to Redis for the API process to serve (Celery worker)."""
    logger.info(
        "Snapshot persist loop started (interval=%ss, key=%s)",
        interval_sec,
        SNAPSHOT_REDIS_KEY,
    )
    while True:
        await asyncio.sleep(interval_sec)
        async with state.lock:
            payload = state.get_snapshot().model_dump(mode="json")
        r.set(SNAPSHOT_REDIS_KEY, json.dumps(payload, separators=(",", ":")))
