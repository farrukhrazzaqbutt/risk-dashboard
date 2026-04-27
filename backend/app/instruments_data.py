from __future__ import annotations

from .models import InstrumentConfig

# Shared between API and Celery worker (same universe of clients/instruments).
INSTRUMENTS: list[InstrumentConfig] = [
    InstrumentConfig(symbol="EURUSD", start_price=1.08, spread_bps=1.2, volatility_bps=2.0),
    InstrumentConfig(symbol="GBPUSD", start_price=1.27, spread_bps=1.5, volatility_bps=2.5),
    InstrumentConfig(symbol="USDJPY", start_price=151.0, spread_bps=1.0, volatility_bps=1.6),
    InstrumentConfig(symbol="XAUUSD", start_price=2300.0, spread_bps=2.0, volatility_bps=3.5),
]

CLIENTS = ["C1", "C2", "C3", "C4", "C5"]
