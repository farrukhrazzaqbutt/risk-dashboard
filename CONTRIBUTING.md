# Contributing

This project is documented in Markdown throughout the repository (per task guidance when using AI-assisted development).

## Where to read

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | Overview, setup, Docker, CI, trade-offs, limitations |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Data flow, scalability knobs, MVP simplifications |
| [backend/README.md](backend/README.md) | API, logging, tunables, tests, Docker-based CI parity |

## Before opening a PR

1. Run the same checks as GitHub Actions (see **“Same checks as CI (Docker)”** in `backend/README.md`), or locally: `uv sync --frozen --extra dev` then `pytest`, `ruff`, `flake8`, `radon`, `xenon` as documented there.
2. Do not commit generated artifacts (`node_modules/`, `.venv/`, `dist/`) — see root `.gitignore`.

## Code style (backend)

- **Ruff** (lint + format) and **Flake8** use **`backend/.flake8`** (`max-line-length = 100`), copied into the CI test image.
