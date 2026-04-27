from __future__ import annotations

import os

from celery import Celery
from celery.signals import worker_process_init


def _broker_url() -> str:
    return (os.environ.get("REDIS_URL") or "redis://localhost:6379/0").strip()


celery_app = Celery(
    "risk_dashboard",
    broker=_broker_url(),
    backend=_broker_url(),
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    result_expires=3600,
)


@celery_app.task(name="health.ping")
def ping() -> str:
    return "pong"


@worker_process_init.connect(weak=False)
def _start_simulation_on_worker(**_kwargs) -> None:
    """
    Run the pricing/trading + Redis snapshot loop in a dedicated thread.

    Do not run multiple consumer processes for this worker image: each
    would start its own book simulation. Scale API horizontally instead.
    """
    if os.environ.get("SKIP_CELERY_SIMULATION", "").strip() in ("1", "true", "True"):
        return
    import threading

    from .celery_simulation import run_celery_simulation_forever

    t = threading.Thread(
        target=run_celery_simulation_forever, name="celery-simulation", daemon=True
    )
    t.start()
