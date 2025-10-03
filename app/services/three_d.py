from __future__ import annotations

import json
import time
from typing import Optional
from sqlalchemy.orm import Session
from redis import Redis

from ..config import settings
from ..models import Asset3D
from .embeddings import embed_text, cosine_similarity


def _inject_character_context(prompt: str, character: str) -> str:
    if character == "Gavel":
        return prompt + "; include judicial scales motif"
    if character == "Scales":
        return prompt + "; oceanic debris textures"
    if character == "Weights":
        return prompt + "; heavy iron weights aesthetic"
    return prompt


def generate_or_fallback_gltf(db: Session, redis: Optional[Redis], prompt: str, character: str) -> tuple[str, dict]:
    """
    Try to generate a GLTF via TripoSR; on timeout/failure, fall back to nearest cached asset.
    Returns (gltf_url, metadata)
    """
    # Prompt injection for character context
    prompt = _inject_character_context(prompt, character)

    # Attempt TripoSR generation via Hugging Face Inference (stubbed)
    started = time.time()
    try:
        # This block simulates a generation with timeout behavior.
        # Replace with a real HF Inference call when available.
        timeout_sec = 10
        while time.time() - started < timeout_sec:
            time.sleep(0.2)  # simulate processing
        raise TimeoutError("TripoSR generation timed out")
    except Exception:
        # Fallback using embeddings similarity against cached assets
        target_emb = embed_text(prompt)
        candidates = db.query(Asset3D).all()
        best_url = None
        best_meta = None
        best_score = -1.0
        for asset in candidates:
            meta = asset.metadata or {}
            emb = meta.get("embedding")
            if emb:
                score = cosine_similarity(target_emb, emb)
            else:
                # compute and persist embedding if missing
                emb = embed_text(asset.prompt)
                score = cosine_similarity(target_emb, emb)
                asset.metadata = {**meta, "embedding": emb}
            if score > best_score:
                best_score = score
                best_url = asset.gltf_url
                best_meta = asset.metadata or {}
        if best_url:
            # Increment usage_count
            asset = db.query(Asset3D).filter(Asset3D.gltf_url == best_url).one()
            asset.usage_count = (asset.usage_count or 0) + 1
            db.commit()
            return best_url, best_meta or {}

        # As a last resort when no assets exist, return a static placeholder
        return "https://example.com/assets/placeholder.glb", {"note": "static fallback"}