from __future__ import annotations

import logging
import uuid
from typing import Optional
from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from redis import Redis

from .config import settings
from .database import Base, engine, get_db
from .models import Session as SessionModel, Character, Asset3D, Vignette
from .schemas import (
    InitSessionRequest,
    InitSessionResponse,
    DialogueResponse,
    TTSRequest,
    TTSResponse,
    Generate3DRequest,
    Generate3DResponse,
    StoryBranchResponse,
    ImprintCaptureRequest,
)
from .services.rate_limit import allow_once_per_minute
from .services.tts import synthesize_tts
from .services.three_d import generate_or_fallback_gltf


logger = logging.getLogger("eom")

app = FastAPI(title="Echoes of Mercy Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_redis() -> Redis | None:
    try:
        if not settings.redis_url:
            return None
        return Redis.from_url(settings.redis_url)
    except Exception:
        return None


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables ensured.")


@app.post("/session/init", response_model=InitSessionResponse)
def init_session(payload: InitSessionRequest, db: Session = Depends(get_db)):
    try:
        character = Character(payload.character)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid character")

    session = SessionModel(character=character, user_id=payload.user_id)
    db.add(session)
    db.commit()
    db.refresh(session)

    resp = InitSessionResponse(
        session_id=str(session.id),
        assistant_voice=f"{character.value}_raspy" if character == Character.Scales else f"{character.value}_neutral",
        initial_prompt="Child approaches: 'Are you my mother?'",
    )
    return resp


@app.get("/dialogue/{session_id}", response_model=DialogueResponse)
def get_dialogue(session_id: str, action: Optional[str] = Query(None), object: Optional[str] = Query(None)):
    # Placeholder LLM response
    text = "This... plays her song. Remember?" if (action == "hand_object" and object == "music_box") else "Are you my mother?"
    emotion = "nostalgic" if (action == "hand_object" and object == "music_box") else "neutral"
    return DialogueResponse(text=text, emotion=emotion)


@app.post("/tts/synthesize", response_model=TTSResponse)
def tts_synthesize(payload: TTSRequest, redis: Redis | None = Depends(get_redis)):
    url = synthesize_tts(payload.text, payload.emotion, settings.elevenlabs_api_key, redis)
    return TTSResponse(audio_url=url)


@app.post("/3d/generate", response_model=Generate3DResponse)
def generate_3d(payload: Generate3DRequest, session_id: str = Query(...), db: Session = Depends(get_db), redis: Redis | None = Depends(get_redis)):
    # Rate limit: 1/min per session (configurable)
    if not allow_once_per_minute(redis, key=f"3d:{session_id}", max_per_minute=settings.rate_limit_3d_per_min):
        raise HTTPException(status_code=429, detail="Rate limit exceeded for 3D generation")

    # Determine character from session for prompt injection
    sess = db.get(SessionModel, uuid.UUID(session_id))
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")

    url, meta = generate_or_fallback_gltf(db, redis, payload.prompt, sess.character.value)
    return Generate3DResponse(gltf_url=url, bounds=[1.0, 1.0, 1.0], metadata=meta)


@app.get("/story/branch/{session_id}", response_model=StoryBranchResponse)
def story_branch(session_id: str, house: int = Query(...), db: Session = Depends(get_db)):
    v = db.query(Vignette).filter(Vignette.house_num == house).first()
    if not v:
        # Basic placeholder when DB not seeded
        return StoryBranchResponse(
            script="Bad men at door—hide!",
            three_d_prompt="shadowy figures in doorway",
            radio_line="Scales: 'This one's mine—choked on fear like seawater.'",
        )
    return StoryBranchResponse(
        script=v.memory_script or "Bad men at door—hide!",
        three_d_prompt=v.base_prompt,
        radio_line="Scales: 'This one's mine—choked on fear like seawater.'",
    )


@app.post("/imprint/capture")
def imprint_capture(payload: ImprintCaptureRequest):
    # Per spec: anonymized, not persisted — just analytics/logging
    logger.info(f"Imprint captured: {payload.timestamp} | peak {payload.peak_emotion}")
    return {"status": "ok"}


@app.websocket("/ws/dialogue/{session_id}")
async def ws_dialogue(ws: WebSocket, session_id: str):
    await ws.accept()
    try:
        await ws.send_text("TTS stream starting...")
        while True:
            _ = await ws.receive_text()
            await ws.send_text("chunk: Are you my mother?")
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")