# Backend Notes

The backend is a FastAPI service with two deployment modes:

- **In-process (default):** no `REDIS_URL` set — a single Uvicorn process runs the simulators and WebSocket fan-out in memory.
- **Redis + Celery:** with `REDIS_URL` set — a **Celery worker** runs price/trade simulation and writes snapshots to Redis; Uvicorn serves HTTP/WebSocket and streams JSON from Redis. Use **one** worker process for simulation (see `docker-compose` worker: `--pool=solo`).

## Dependency management with uv

This backend uses `uv` for reproducible Python environments and locked dependencies.

- Source of truth: `pyproject.toml`
- Locked dependency graph: `uv.lock`
- Optional exported file: `requirements.txt` (generated from lock)

### Install and run (uv)

```bash
cd backend
python -m uv sync --frozen --extra dev
python -m uv run uvicorn app.main:app --reload
```

### Tests and code quality (local)

With dev dependencies (`--extra dev`):

```bash
uv run pytest tests/ -v
uv run ruff check app tests
uv run ruff format app tests
uv run flake8 app tests
uv run radon cc app -a -nb
uv run radon mi app -nb
uv run xenon --max-absolute C --max-modules B --max-average A app
```

### Same checks as CI (Docker, from repo root)

CI builds `Dockerfile.test` and runs **ruff**, **flake8**, **pytest**, **radon**, and **xenon** inside that image. The image copies **`backend/.flake8`** so **flake8** uses `max-line-length = 100` (matching **ruff**), not the default 79.

To mirror CI **before pushing** (no Docker Compose — use plain Docker):

```bash
# From risk-dashboard/ (repository root)
docker build -f backend/Dockerfile.test -t risk-dashboard-backend-ci ./backend

docker run --rm risk-dashboard-backend-ci uv run ruff check app tests
docker run --rm risk-dashboard-backend-ci uv run ruff format --check app tests
docker run --rm risk-dashboard-backend-ci uv run flake8 app tests
docker run --rm risk-dashboard-backend-ci uv run pytest tests/ -v
docker run --rm risk-dashboard-backend-ci uv run radon cc app -a -nb
docker run --rm risk-dashboard-backend-ci uv run radon mi app -nb
docker run --rm risk-dashboard-backend-ci uv run xenon --max-absolute C --max-modules B --max-average A app
```

Quick test-only run:

```bash
docker build -f backend/Dockerfile.test -t risk-dashboard-backend-ci ./backend
docker run --rm risk-dashboard-backend-ci
```

(Default container command is `pytest tests/ -v`.)

GitHub Actions: `../.github/workflows/ci.yml`.

### Tunables (scalability / demos)

- `BROADCAST_INTERVAL_SEC` — seconds between WebSocket snapshot pushes (default `0.5`). Increase if you simulate higher load and want fewer fan-out ticks.
- `SIMULATION_LOAD_MULTIPLIER` — speeds mock price ticks and trade arrivals (default `1`; try `10` to stress the UI).

### Logging

- Format: `timestamp | LEVEL | logger_name | message` (stdout).
- Set verbosity with `LOG_LEVEL` (default `INFO`): `DEBUG`, `INFO`, `WARNING`, `ERROR`.
- Examples:
  - Linux/macOS: `LOG_LEVEL=DEBUG python -m uv run uvicorn app.main:app --reload`
  - Windows PowerShell: `$env:LOG_LEVEL="DEBUG"; python -m uv run uvicorn app.main:app --reload`
- `GET /snapshot` is logged at **DEBUG** only (avoids log spam).

## Celery + Redis (optional)

1. Start Redis (e.g. `docker run -p 6379:6379 redis:7-alpine`).
2. In one shell (from `backend/`), with `REDIS_URL` set:

   `REDIS_URL=redis://127.0.0.1:6379/0` (or Windows PowerShell: `$env:REDIS_URL="redis://127.0.0.1:6379/0"`)
3. `python -m uv run celery -A app.celery_app worker -l info --pool=solo`
4. In another: `python -m uv run uvicorn app.main:app --reload`

`docker compose` from the repo root runs `redis`, `worker`, and `backend` with `REDIS_URL` set.

## Endpoints

- `GET /health` - liveness; in redis mode the API also `PING`s Redis
- `GET /snapshot` - current dashboard snapshot JSON
- `WS /ws` - pushes snapshot updates (interval `BROADCAST_INTERVAL_SEC`, default 0.5s)

## Simulation loops

**In-process:** on startup, Uvicorn spawns three asyncio tasks: price, trades, in-memory WebSocket fan-out.

**Celery + Redis:** the worker spawns: price, trades, Redis snapshot write loop; Uvicorn spawns: WebSocket fan-out that reads the latest JSON from Redis.

## Simplified metrics

- **Unrealized PnL**
  - long: `qty * (mid - avg_price)`
  - short: `abs(qty) * (avg_price - mid)`
- **Total PnL** = realized + unrealized
- **Monetization**: spread capture proxy from execution vs mid
- **Client yield**: `total_client_pnl / total_client_trade_count`

All state is in memory; no persistence layer is used.