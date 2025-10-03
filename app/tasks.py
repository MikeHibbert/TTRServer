from __future__ import annotations

from sqlalchemy.orm import Session
from redis import Redis
from .celery_app import celery_app
from .database import SessionLocal
from .config import settings
from .services.three_d import generate_or_fallback_gltf
from .services.tts import synthesize_tts


def _get_redis() -> Redis | None:
    try:
        if not settings.redis_url:
            return None
        return Redis.from_url(settings.redis_url)
    except Exception:
        return None


@celery_app.task(name="app.tasks.generate_3d_task")
def generate_3d_task(prompt: str, character: str) -> dict:
    redis = _get_redis()
    db: Session = SessionLocal()
    try:
        url, meta = generate_or_fallback_gltf(db, redis, prompt, character)
        return {"gltf_url": url, "metadata": meta}
    finally:
        db.close()


@celery_app.task(name="app.tasks.tts_task")
def tts_task(text: str, emotion: str | None) -> dict:
    redis = _get_redis()
    url = synthesize_tts(text, emotion, settings.elevenlabs_api_key, redis)
    return {"audio_url": url}