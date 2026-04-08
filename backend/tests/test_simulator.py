from __future__ import annotations

import pytest
from app.simulator import update_position_with_trade


def test_open_flat_to_long(book_state, sample_instruments) -> None:
    sym = sample_instruments[0].symbol
    r = update_position_with_trade(book_state, sym, 10_000.0, 1.105)
    assert r == 0.0
    assert book_state.positions_qty[sym] == 10_000.0
    assert book_state.avg_price[sym] == pytest.approx(1.105)


def test_add_same_direction_weighted_avg(book_state, sample_instruments) -> None:
    sym = sample_instruments[0].symbol
    update_position_with_trade(book_state, sym, 10_000.0, 1.0)
    update_position_with_trade(book_state, sym, 10_000.0, 1.2)
    assert book_state.positions_qty[sym] == 20_000.0
    assert book_state.avg_price[sym] == pytest.approx(1.1)


def test_reduce_long_realizes_pnl(book_state, sample_instruments) -> None:
    sym = sample_instruments[0].symbol
    update_position_with_trade(book_state, sym, 10_000.0, 1.0)
    realized = update_position_with_trade(book_state, sym, -4_000.0, 1.05)
    assert realized == pytest.approx(4_000.0 * (1.05 - 1.0))
    assert book_state.positions_qty[sym] == 6_000.0


def test_flat_after_full_close(book_state, sample_instruments) -> None:
    sym = sample_instruments[0].symbol
    update_position_with_trade(book_state, sym, 5_000.0, 1.0)
    update_position_with_trade(book_state, sym, -5_000.0, 1.1)
    assert book_state.positions_qty[sym] == 0.0
    assert book_state.avg_price[sym] == 0.0


def test_flip_short_sets_new_avg(book_state, sample_instruments) -> None:
    sym = sample_instruments[0].symbol
    update_position_with_trade(book_state, sym, 1_000.0, 1.0)
    realized = update_position_with_trade(book_state, sym, -3_000.0, 1.2)
    assert book_state.positions_qty[sym] == -2_000.0
    assert book_state.avg_price[sym] == pytest.approx(1.2)
    assert realized == pytest.approx(1_000.0 * (1.2 - 1.0))


def test_short_cover_realizes(book_state, sample_instruments) -> None:
    sym = sample_instruments[0].symbol
    update_position_with_trade(book_state, sym, -8_000.0, 1.5)
    realized = update_position_with_trade(book_state, sym, 3_000.0, 1.4)
    assert realized == pytest.approx(3_000.0 * (1.5 - 1.4))
    assert book_state.positions_qty[sym] == -5_000.0
