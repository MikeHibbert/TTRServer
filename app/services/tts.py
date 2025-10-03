from __future__ import annotations

import hashlib
import json
from typing import Optional
from redis import Redis
import requests


def _cache_key(text: str, emotion: Optional[str]) -> str:
    h = hashlib.sha256(f"{text}|{emotion or ''}".encode()).hexdigest()
    return f"tts:{h}"


def synthesize_tts(text: str, emotion: Optional[str], api_key: Optional[str], redis: Optional[Redis]) -> str:
    """Return audio URL; cache in Redis for 1 hour."""
    key = _cache_key(text, emotion)
    if redis:
        cached = redis.get(key)
        if cached:
            return cached.decode()

    # Placeholder: If no API key, return a demo URL
    if not api_key:
        url = f"https://example.com/audio/{key}.mp3"
    else:
        # ElevenLabs API call (simplified)
        try:
            # This is a placeholder endpoint. Replace with proper ElevenLabs API route.
            resp = requests.post(
                "https://api.elevenlabs.io/v1/text-to-speech",
                headers={"xi-api-key": api_key, "Content-Type": "application/json"},
                data=json.dumps({"text": text, "emotion": emotion or "neutral"}),
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            url = data.get("audio_url") or f"https://example.com/audio/{key}.mp3"
        except Exception:
            url = f"https://example.com/audio/{key}.mp3"

    if redis:
        redis.setex(key, 3600, url)
    return url