# Risk Management Dashboard MVP

A lightweight full-stack MVP that simulates market data and client trading activity, then streams real-time book and risk metrics to a browser dashboard.

## Project overview

This project demonstrates a practical risk/book monitoring loop:

- market prices are simulated via random walk
- clients generate random trades against bid/ask quotes
- internal book exposure is updated in memory
- risk metrics are recalculated and pushed over WebSocket (default **500ms**; override with `BROADCAST_INTERVAL_SEC`)

## Architecture summary

- `backend/` (FastAPI)
  - simulation tasks for prices and trades
  - in-memory state store for prices, positions, pnl, and trades
  - REST + WebSocket endpoints for dashboard data
  - `uv` + `uv.lock` for reproducible Python environments/dependencies
  - snapshot includes **PnL attribution by instrument**, **gross notional by instrument**, **per-client PnL proxy**, and **live bid/ask/mid**
- `frontend/` (React + Vite)
  - WebSocket subscription to backend snapshots
  - metric cards (including realized / unrealized PnL), PnL curve, client PnL chart (full width of main column), live quotes strip, positions, recent trades (full page width)
  - browser console logging with a `[risk-dashboard]` prefix (see `frontend/src/logger.js`)
- See **`ARCHITECTURE.md`** for flow, scalability knobs (`BROADCAST_INTERVAL_SEC`, `SIMULATION_LOAD_MULTIPLIER`), and explicit MVP simplifications.

## CI

GitHub Actions (`.github/workflows/ci.yml`) runs on push/PR to `main`/`master`. It builds **`backend/Dockerfile.test`** and runs **ruff**, **flake8**, **pytest**, **radon**, and **xenon** inside that container (same environment as production Python 3.11 + locked deps).

To rehearse locally before push, see **“Same checks as CI (Docker)”** in `backend/README.md` (`docker build` + `docker run` — not part of `docker compose`).

## Logging

- **Backend**: structured logs to stdout; control verbosity with `LOG_LEVEL` (`INFO` by default). See `backend/README.md`.
- **Frontend**: `log.info` / `log.warn` / `log.error` (+ `log.debug` in dev only) via `src/logger.js`.

## Stack rationale

- **FastAPI**: simple async API and WebSocket support
- **React + Vite**: fast local dev and minimal setup
- **Recharts**: interactive charting with built-in tooltip support
- **In-memory state**: lowest complexity for MVP and technical exercise scope
- **uv**: reproducible Python dependency resolution + lockfile workflow

## Local setup

### Backend (uv, recommended)

```bash
cd backend
python -m uv sync --frozen --extra dev
python -m uv run uvicorn app.main:app --reload
```

(`--extra dev` includes pytest, ruff, flake8, radon, xenon; omit it for a minimal runtime-only install.)

Optional: `LOG_LEVEL=DEBUG` for verbose backend logs (see `backend/README.md`).

Backend runs at `http://localhost:8000`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`.

## Run with Docker Compose

From the repository root:

```bash
docker compose up --build
```

Add `-d` to run detached in the background. Backend image respects `LOG_LEVEL` (see `docker-compose.yml`).

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`

## Checklist before submit (for you / the reviewer)

- [ ] Clone fresh, then either **`docker compose up --build`** or backend `uv sync` + `uv run uvicorn …` and frontend `npm install` + `npm run dev`.
- [ ] Open **`/docs`** on the backend for interactive API docs; confirm **`/health`**, **`/snapshot`**, and **`/ws`**.
- [ ] Do **not** commit **`node_modules/`**, **`backend/.venv/`**, or **`frontend/dist/`** (all listed in `.gitignore`).
- [ ] Optional stress demo: `SIMULATION_LOAD_MULTIPLIER=10` and, if needed, raise `BROADCAST_INTERVAL_SEC` (see `ARCHITECTURE.md`).

## Assumptions and simplifications

- No database; state is reset on restart
- Simplified PnL and book model suitable for MVP/demo
- **Exposure rule** enforced:
  - client buys -> we are short
  - client sells -> we are long
- Monetization is a simple spread-capture proxy
- Client yield uses: `total_client_pnl / total_client_trade_count`

## Possible future improvements

- Add filters by client/instrument/time range
- Add richer attribution (realized vs unrealized by symbol)
- Add reconnect strategy/backoff in frontend websocket client
- Add tests for simulator math and exposure transitions
- Add persistence and historical replay