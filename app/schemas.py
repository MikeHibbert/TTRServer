from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class InitSessionRequest(BaseModel):
    character: str
    user_id: Optional[str] = None


class InitSessionResponse(BaseModel):
    session_id: str
    assistant_voice: str
    initial_prompt: str


class DialogueResponse(BaseModel):
    text: str
    emotion: str


class TTSRequest(BaseModel):
    text: str
    emotion: Optional[str] = None


class TTSResponse(BaseModel):
    audio_url: str


class Generate3DRequest(BaseModel):
    prompt: str


class Generate3DResponse(BaseModel):
    gltf_url: str
    bounds: List[float] = Field(default_factory=lambda: [1.0, 1.0, 1.0])
    metadata: Optional[dict] = None


class StoryBranchResponse(BaseModel):
    script: str
    three_d_prompt: str
    radio_line: str


class ImprintCaptureRequest(BaseModel):
    timestamp: str
    peak_emotion: str