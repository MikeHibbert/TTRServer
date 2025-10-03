from __future__ import annotations

from celery import Celery
from .config import settings


celery_app = Celery(
    "echoes_of_mercy",
    broker=settings.redis_url or "redis://localhost:6379/0",
    backend=settings.redis_url or "redis://localhost:6379/0",
)

celery_app.conf.update(
    task_routes={
        "app.tasks.generate_3d_task": {"queue": "3d"},
        "app.tasks.tts_task": {"queue": "tts"},
    }
)