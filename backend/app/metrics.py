from __future__ import annotations


def calculate_unrealized_pnl(quantity: float, avg_price: float, mid_price: float) -> float:
    """
    Long quantity (>0): qty * (mid - avg)
    Short quantity (<0): abs(qty) * (avg - mid)
    """
    if quantity >= 0:
        return quantity * (mid_price - avg_price)
    return abs(quantity) * (avg_price - mid_price)


def calculate_spread_capture(side: str, trade_price: float, bid: float, ask: float) -> float:
    """
    Monetization proxy: spread capture around mid.

    If client buys, we sell near ask. Capture is (trade - mid).
    If client sells, we buy near bid. Capture is (mid - trade).
    """
    mid = (bid + ask) / 2
    if side == "BUY":
        return trade_price - mid
    return mid - trade_price
