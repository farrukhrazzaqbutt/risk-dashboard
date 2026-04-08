from __future__ import annotations

import pytest
from app.models import InstrumentConfig
from app.state import BookState


@pytest.fixture
def sample_instruments() -> list[InstrumentConfig]:
    return [
        InstrumentConfig(symbol="EURUSD", start_price=1.1, spread_bps=1.0, volatility_bps=1.0),
        InstrumentConfig(symbol="XAUUSD", start_price=2000.0, spread_bps=2.0, volatility_bps=2.0),
    ]


@pytest.fixture
def book_state(sample_instruments: list[InstrumentConfig]) -> BookState:
    return BookState(sample_instruments, ["C1", "C2"])
