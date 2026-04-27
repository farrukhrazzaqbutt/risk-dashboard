from __future__ import annotations

import json
import os
from typing import Any

import redis

SNAPSHOT_REDIS_KEY = "risk_dashboard:snapshot:v1"


def get_redis_client() -> redis.Redis:
    url = (os.environ.get("REDIS_URL") or "").strip() or "redis://localhost:6379/0"
    return redis.Redis.from_url(url, decode_responses=True)


def load_snapshot(r: redis.Redis) -> dict[str, Any] | None:
    raw = r.get(SNAPSHOT_REDIS_KEY)
    if not raw:
        return None
    if isinstance(raw, (bytes, bytearray)):
        raw = raw.decode("utf-8")
    return json.loads(raw)
