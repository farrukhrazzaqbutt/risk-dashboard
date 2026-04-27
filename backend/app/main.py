from __future__ import annotations

import asyncio
import logging
import os
from typing import Any

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .instruments_data import CLIENTS, INSTRUMENTS
from .logging_config import configure_logging
from .simulator import run_price_simulation, run_trade_simulation
from .snapshot_store import get_redis_client, load_snapshot
from .state import BookState

configure_logging()
logger = logging.getLogger(__name__)

REDIS_URL = (os.getenv("REDIS_URL") or "").strip()
USE_REDIS = bool(REDIS_URL)

app = FastAPI(title="Risk Management Dashboard API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-process mode: in-memory book + three asyncio tasks.
# With REDIS_URL: simulation runs in Celery worker; API reads snapshot from Redis
# and only runs WebSocket fan-out.
book_state: BookState | None = None

# WebSocket clients always live in the Uvicorn process.
ws_connections: set[WebSocket] = set()
ws_lock = asyncio.Lock()

BROADCAST_INTERVAL_SEC = float(os.getenv("BROADCAST_INTERVAL_SEC", "0.5"))


def _get_book_state() -> BookState:
    if book_state is None:
        raise RuntimeError("book_state not initialized (expected in in-process mode only)")
    return book_state


async def run_in_memory_ws_broadcast() -> None:
    logger.info("In-process broadcast loop started (interval=%ss)", BROADCAST_INTERVAL_SEC)
    b = _get_book_state()
    while True:
        await asyncio.sleep(BROADCAST_INTERVAL_SEC)
        async with b.lock:
            snapshot = b.get_snapshot().model_dump(mode="json")
        stale: list[WebSocket] = []
        async with ws_lock:
            conns = list(ws_connections)
        for ws in conns:
            try:
                await ws.send_json(snapshot)
            except Exception as exc:
                logger.warning(
                    "Failed to push snapshot to websocket client; removing: %s",
                    exc,
                    exc_info=True,
                )
                stale.append(ws)
        async with ws_lock:
            for ws in stale:
                ws_connections.discard(ws)


async def run_redis_ws_broadcast() -> None:
    """
    Pushes the latest JSON snapshot (written by the Celery worker) to all WS clients.
    """
    logger.info("Redis-backed WebSocket fan-out started (interval=%ss)", BROADCAST_INTERVAL_SEC)
    r = get_redis_client()
    while True:
        await asyncio.sleep(BROADCAST_INTERVAL_SEC)
        data = await asyncio.to_thread(load_snapshot, r)
        if data is None:
            continue
        stale: list[WebSocket] = []
        async with ws_lock:
            conns = list(ws_connections)
        for ws in conns:
            try:
                await ws.send_json(data)
            except Exception as exc:
                logger.warning(
                    "Failed to push snapshot to websocket client; removing: %s",
                    exc,
                    exc_info=True,
                )
                stale.append(ws)
        async with ws_lock:
            for ws in stale:
                ws_connections.discard(ws)


@app.on_event("startup")
async def startup_event() -> None:
    symbols = [i.symbol for i in INSTRUMENTS]
    global book_state
    if USE_REDIS:
        logger.info(
            "Starting Risk Dashboard API | mode=celery+redis | instruments=%s clients=%s",
            symbols,
            CLIENTS,
        )
        asyncio.create_task(run_redis_ws_broadcast())
    else:
        book_state = BookState(instruments=INSTRUMENTS, clients=CLIENTS)
        logger.info(
            "Starting Risk Dashboard API | mode=in_process | instruments=%s clients=%s",
            symbols,
            CLIENTS,
        )
        asyncio.create_task(run_price_simulation(_get_book_state()))
        asyncio.create_task(run_trade_simulation(_get_book_state()))
        asyncio.create_task(run_in_memory_ws_broadcast())
    logger.info("Background task(s) scheduled for this process")


@app.get("/health")
async def health() -> dict[str, str]:
    if USE_REDIS:
        r = get_redis_client()
        try:
            await asyncio.to_thread(r.ping)
        except Exception as exc:
            raise HTTPException(status_code=503, detail=f"redis_unavailable: {exc}") from exc
        return {"status": "ok", "mode": "redis"}
    return {"status": "ok", "mode": "in_process"}


@app.get("/snapshot")
async def snapshot() -> dict[str, Any]:
    if not USE_REDIS:
        b = _get_book_state()
        logger.debug("GET /snapshot (in_process)")
        async with b.lock:
            return b.get_snapshot().model_dump(mode="json")
    r = get_redis_client()
    data = await asyncio.to_thread(load_snapshot, r)
    if data is None:
        raise HTTPException(
            status_code=503,
            detail="Snapshot not yet available (is the Celery worker running?)",
        )
    return data


def _client_label(websocket: WebSocket) -> str:
    if websocket.client:
        return f"{websocket.client.host}:{websocket.client.port}"
    return "unknown"


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    label = _client_label(websocket)
    async with ws_lock:
        ws_connections.add(websocket)
    if USE_REDIS:
        r = get_redis_client()
        data = await asyncio.to_thread(load_snapshot, r)
        if data is None:
            data = await asyncio.to_thread(_wait_for_snapshot, r, 10.0, BROADCAST_INTERVAL_SEC)
    else:
        b = _get_book_state()
        async with b.lock:
            data = b.get_snapshot().model_dump(mode="json")

    logger.info(
        "WebSocket connected | client=%s | active_connections=%d | mode=%s",
        label,
        len(ws_connections),
        "redis" if USE_REDIS else "in_process",
    )
    if data is not None:
        try:
            await websocket.send_json(data)
        except Exception:
            pass

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected (client closed) | client=%s", label)
    except Exception:
        logger.warning("WebSocket error | client=%s", label, exc_info=True)
    finally:
        async with ws_lock:
            ws_connections.discard(websocket)
        logger.debug("WebSocket connection closed | client=%s", label)


def _wait_for_snapshot(r, timeout_sec: float, poll_sec: float) -> dict | None:
    import time

    deadline = time.monotonic() + timeout_sec
    while time.monotonic() < deadline:
        snap = load_snapshot(r)
        if snap is not None:
            return snap
        time.sleep(poll_sec)
    return None
