from __future__ import annotations

import numpy as np
from typing import List

try:
    from sentence_transformers import SentenceTransformer
    _model = SentenceTransformer("all-MiniLM-L6-v2")
except Exception:
    _model = None


def embed_text(text: str) -> List[float]:
    if _model is None:
        # Fallback simple embedding: character frequency vector
        vec = np.zeros(26)
        for ch in text.lower():
            if "a" <= ch <= "z":
                vec[ord(ch) - ord("a")] += 1
        norm = np.linalg.norm(vec) or 1.0
        return (vec / norm).tolist()
    emb = _model.encode([text], normalize_embeddings=True)[0]
    return emb.tolist()


def cosine_similarity(a: List[float], b: List[float]) -> float:
    va = np.array(a)
    vb = np.array(b)
    denom = (np.linalg.norm(va) * np.linalg.norm(vb)) or 1.0
    return float(np.dot(va, vb) / denom)