from __future__ import annotations

import asyncio
import logging
import os

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .logging_config import configure_logging
from .models import InstrumentConfig
from .simulator import run_price_simulation, run_trade_simulation
from .state import BookState

configure_logging()
logger = logging.getLogger(__name__)


INSTRUMENTS: list[InstrumentConfig] = [
    InstrumentConfig(symbol="EURUSD", start_price=1.08, spread_bps=1.2, volatility_bps=2.0),
    InstrumentConfig(symbol="GBPUSD", start_price=1.27, spread_bps=1.5, volatility_bps=2.5),
    InstrumentConfig(symbol="USDJPY", start_price=151.0, spread_bps=1.0, volatility_bps=1.6),
    InstrumentConfig(symbol="XAUUSD", start_price=2300.0, spread_bps=2.0, volatility_bps=3.5),
]

CLIENTS = ["C1", "C2", "C3", "C4", "C5"]

app = FastAPI(title="Risk Management Dashboard API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

state = BookState(instruments=INSTRUMENTS, clients=CLIENTS)

BROADCAST_INTERVAL_SEC = float(os.getenv("BROADCAST_INTERVAL_SEC", "0.5"))


async def run_broadcast_loop() -> None:
    logger.info("Broadcast loop started (interval=%ss)", BROADCAST_INTERVAL_SEC)
    while True:
        await asyncio.sleep(BROADCAST_INTERVAL_SEC)
        async with state.lock:
            snapshot = state.get_snapshot().model_dump(mode="json")
            stale_clients: list[WebSocket] = []
            for ws in state.connections:
                try:
                    await ws.send_json(snapshot)
                except Exception as exc:
                    logger.warning(
                        "Failed to push snapshot to websocket client; removing: %s",
                        exc,
                        exc_info=True,
                    )
                    stale_clients.append(ws)
            for ws in stale_clients:
                state.connections.discard(ws)


@app.on_event("startup")
async def startup_event() -> None:
    symbols = [i.symbol for i in INSTRUMENTS]
    logger.info(
        "Starting Risk Dashboard API | instruments=%s clients=%s",
        symbols,
        CLIENTS,
    )
    asyncio.create_task(run_price_simulation(state))
    asyncio.create_task(run_trade_simulation(state))
    asyncio.create_task(run_broadcast_loop())
    logger.info("Background tasks scheduled: price_simulation, trade_simulation, broadcast_loop")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/snapshot")
async def snapshot() -> dict:
    logger.debug("GET /snapshot")
    async with state.lock:
        return state.get_snapshot().model_dump(mode="json")


def _client_label(websocket: WebSocket) -> str:
    if websocket.client:
        return f"{websocket.client.host}:{websocket.client.port}"
    return "unknown"


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    label = _client_label(websocket)
    async with state.lock:
        state.connections.add(websocket)
        await websocket.send_json(state.get_snapshot().model_dump(mode="json"))
    logger.info(
        "WebSocket connected | client=%s | active_connections=%d",
        label,
        len(state.connections),
    )

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected (client closed) | client=%s", label)
    except Exception:
        logger.warning("WebSocket error | client=%s", label, exc_info=True)
    finally:
        async with state.lock:
            state.connections.discard(websocket)
        logger.debug("WebSocket connection closed | client=%s", label)
