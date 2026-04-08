from __future__ import annotations

import pytest
from app.metrics import calculate_spread_capture, calculate_unrealized_pnl


@pytest.mark.parametrize(
    ("qty", "avg", "mid", "expected"),
    [
        (1000.0, 1.0, 1.1, 100.0),
        (1000.0, 1.1, 1.0, -100.0),
        (-5000.0, 1.2, 1.1, 500.0),
        (-5000.0, 1.0, 1.2, -1000.0),
        (0.0, 1.0, 1.5, 0.0),
    ],
)
def test_calculate_unrealized_pnl(qty: float, avg: float, mid: float, expected: float) -> None:
    assert calculate_unrealized_pnl(qty, avg, mid) == pytest.approx(expected)


def test_calculate_spread_capture_buy() -> None:
    bid, ask = 1.0, 1.002
    mid = (bid + ask) / 2
    trade = ask
    cap = calculate_spread_capture("BUY", trade, bid, ask)
    assert cap == pytest.approx(trade - mid)


def test_calculate_spread_capture_sell() -> None:
    bid, ask = 100.0, 100.2
    mid = (bid + ask) / 2
    trade = bid
    cap = calculate_spread_capture("SELL", trade, bid, ask)
    assert cap == pytest.approx(mid - trade)
