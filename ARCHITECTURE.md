# Architecture notes (interviewer / reviewer)

## End-to-end flow

1. **Price simulator** updates mid via random walk and rebuilds bid/ask from configured spread (bps).
2. **Trade simulator** generates random client orders against current bid/ask; the **internal book** is updated (weighted average, realized PnL on closes/reversals).
3. On each broadcast tick, **`get_snapshot()`** builds a single JSON document: aggregates, positions, recent trades, bounded history deques, **PnL attribution by instrument**, **gross notional by instrument**, **per-client PnL proxy**, and **live quotes**.
4. **WebSocket** fans out that snapshot to all connected dashboards (same payload shape as `GET /snapshot`).

## Why one snapshot payload

The UI stays a thin client: **all book/risk logic stays in Python**, which matches the task emphasis on readability and avoids duplicating rules in the browser.

## Scalability and “10× load” (task prompt)

This MVP is intentionally single-process and in-memory. If you turn up event rates:

| Knob | Effect |
|------|--------|
| `SIMULATION_LOAD_MULTIPLIER` | Speeds price ticks and trade arrivals (e.g. `10` for a stress demo). |
| `BROADCAST_INTERVAL_SEC` | How often full snapshots are built and pushed over WS (default `0.5`). Increase (e.g. `1.0`) to reduce CPU and payload rate if the UI or network becomes the bottleneck. |

**Bounded memory:** recent trades and PnL history use capped deques (`100` / `500`), so backlog does not grow without bound.

**Not overbuilt:** no Redis/Kafka; throttling is a single sleep interval and back-pressure is “drop broken websocket clients.”

## Simplifications

- **Cross-currency / notionals:** `notional_by_instrument` uses `|qty| × mid` as a **single-currency style proxy** across symbols (acceptable for an MVP; production would normalize to a reporting currency).
- **Client PnL:** follows the same simplified client-side accumulation used for **client yield** in the README—defensible as a demo, not a regulatory PnL report.
