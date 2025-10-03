# Echoes of Mercy Backend

FastAPI-based backend for the "Echoes of Mercy" VR experience. Implements AI-driven dialogue, emotional TTS synthesis, 3D model generation via TripoSR with robust fallback, session management, and WebSocket streaming.

## Features
- FastAPI HTTP endpoints and WebSockets
- PostgreSQL/SQLite via SQLAlchemy ORM
- Redis for caching and rate limiting
- Celery for async heavy tasks (3D gen, TTS)
- 3D generation via TripoSR (Hugging Face), with embedding-based fallback to cached assets
- ElevenLabs TTS with caching

## Quickstart

1. Create and activate a Python 3.11+ environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set environment variables (see below).
4. Run the API:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
5. Optional: Start Celery worker:
   ```bash
   celery -A app.celery_app.celery_app worker --loglevel=INFO
   ```

Open `http://localhost:8000/docs` for interactive API docs.

## Environment Variables

- `DATABASE_URL` — SQLAlchemy URL (e.g., `postgresql+psycopg2://user:pass@host:5432/db`); defaults to `sqlite:///./eom.db` for dev.
- `REDIS_URL` — Redis connection URL (e.g., `redis://localhost:6379/0`).
- `ELEVENLABS_API_KEY` — ElevenLabs API key for TTS.
- `HF_TOKEN` — Hugging Face token for TripoSR Inference.
- `S3_ENDPOINT_URL` — MinIO/S3 endpoint (optional).
- `S3_ACCESS_KEY`, `S3_SECRET_KEY`, `S3_BUCKET` — S3/MinIO credentials (optional).
- `RATE_LIMIT_3D_PER_MIN` — Requests per minute per session for `/3d/generate` (default: 1).

## Notes

- In dev, the 3D generation call is stubbed and will fall back to the best cached asset if generation times out or is unavailable.
- Embeddings are computed via `sentence-transformers` and stored in `3d_assets.metadata` under key `embedding` for similarity search.
- Imprint events are logged (console) but not persisted per spec.

## Project Structure

```
app/
  main.py            # FastAPI app and routes
  config.py          # Environment and settings
  database.py        # SQLAlchemy engine/session
  models.py          # ORM models
  schemas.py         # Pydantic schemas
  celery_app.py      # Celery configuration
  tasks.py           # Celery tasks for TTS and 3D gen
  services/
    embeddings.py    # Text embeddings and cosine similarity
    three_d.py       # TripoSR integration + fallback logic
    tts.py           # ElevenLabs TTS integration + caching
    storage.py       # S3/MinIO storage helpers (optional)
    rate_limit.py    # Per-session rate limiter
```

## Testing

- Minimal tests are not included; use the interactive docs and curl.
- Once DB and Redis are configured, endpoints should operate with basic functionality.

## License

Internal project, no external distribution license included.