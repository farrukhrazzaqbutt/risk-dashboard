## AI Usage Disclosure

This project was developed with assistance from Cursor (AI-powered IDE).
AI was used for code suggestions, debugging, and structuring parts of the application.

All implementation decisions, architecture, and validation were performed by the developer.

# Agent Guidance

This file exists because the take-home task asks for Markdown in the repository when development is agent-assisted. It orients automated assistants and human reviewers on how to work safely in this codebase.

## What this project is

A small **risk management dashboard MVP**: simulated bid/ask prices, simulated client trades, an in-memory book, and a **FastAPI** backend that exposes REST + WebSocket snapshots. A **React + Vite** frontend subscribes over WebSocket and charts metrics (PnL, attribution, quotes, positions, trades). See [README.md](README.md) and [ARCHITECTURE.md](ARCHITECTURE.md) for full detail.

## Evaluation criteria (from the brief)

When changing code, prefer outcomes that match what reviewers care about:

1. **Reproducibility** — keep `uv.lock`, Docker paths, and documented setup accurate; do not commit `node_modules/`, `.venv/`, or `dist/`.
2. **Stability** — avoid breaking the dev or Docker Compose flows; run tests before concluding work.
3. **Performance / real-time feel** — respect `BROADCAST_INTERVAL_SEC` and bounded deques; avoid unnecessary work on the hot path without measuring need.
4. **Scalability (10×)** — document or use existing knobs (`SIMULATION_LOAD_MULTIPLIER`, broadcast interval) rather than adding heavy infrastructure unless the brief explicitly requires it.
5. **Readability** — keep book and risk logic in **Python**; keep the frontend a thin subscriber to snapshots; match existing style (Ruff/Flake8, line length 100).

## Where logic lives

| Area | Location |
|------|----------|
| API, WebSocket, lifespan | `backend/app/main.py` |
| Simulation (prices, trades) | `backend/app/simulator.py` |
| In-memory state and snapshot | `backend/app/state.py`, `backend/app/metrics.py` |
| Models / DTOs | `backend/app/models.py` |
| Frontend WebSocket + UI | `frontend/src/` |

## Commands agents should use

- **Backend (local):** from `backend/`, `python -m uv sync --frozen --extra dev` then `python -m uv run pytest`, Ruff, Flake8 as in [backend/README.md](backend/README.md).
- **CI parity:** Docker build/run described under “Same checks as CI (Docker)” in [backend/README.md](backend/README.md).
- **Full stack:** from repo root, `docker compose up --build` (see [README.md](README.md)).

## Conventions for edits

- Prefer **small, focused diffs**; do not refactor unrelated modules.
- **Do not** weaken type safety or error handling on WebSocket/REST paths without a clear reason.
- **Frontend** is functional over pretty; keep charts and tables consistent with existing components.
- After substantive backend changes, run **pytest** (and Ruff if available).

## Human contributors

See [CONTRIBUTING.md](CONTRIBUTING.md) for the documentation index and pre-PR checks.
