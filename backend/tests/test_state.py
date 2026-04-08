from __future__ import annotations

import pytest


def test_get_notional_by_instrument(book_state, sample_instruments) -> None:
    sym = sample_instruments[0].symbol
    st = book_state.symbols[sym]
    st.mid = 1.1
    book_state.positions_qty[sym] = -20_000.0
    book_state.avg_price[sym] = 1.0
    notionals = book_state.get_notional_by_instrument()
    assert notionals[sym] == pytest.approx(20_000.0 * 1.1)


def test_get_pnl_attribution_matches_unrealized_logic(book_state, sample_instruments) -> None:
    sym = sample_instruments[0].symbol
    st = book_state.symbols[sym]
    st.mid = 1.1
    book_state.positions_qty[sym] = 10_000.0
    book_state.avg_price[sym] = 1.0
    attr = book_state.get_pnl_attribution()
    assert attr[sym] == pytest.approx(10_000.0 * (1.1 - 1.0))


def test_snapshot_contains_expected_keys(book_state) -> None:
    snap = book_state.get_snapshot()
    data = snap.model_dump()
    for key in (
        "total_pnl",
        "realized_pnl",
        "unrealized_pnl",
        "monetization",
        "client_yield",
        "trade_count",
        "positions",
        "recent_trades",
        "pnl_history",
        "pnl_attribution",
        "notional_by_instrument",
        "client_pnl",
        "prices",
    ):
        assert key in data
