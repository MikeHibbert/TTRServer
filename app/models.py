from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    Enum as SAEnum,
    JSON,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
import enum
import uuid

from .database import Base


class Character(str, enum.Enum):
    Gavel = "Gavel"
    Scales = "Scales"
    Weights = "Weights"


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[str | None] = mapped_column(String, nullable=True)
    character: Mapped[Character] = mapped_column(SAEnum(Character), nullable=False)
    start_ts: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    progress: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    dialogues: Mapped[list["DialogueCache"]] = relationship(back_populates="session")


class DialogueCache(Base):
    __tablename__ = "dialogue_cache"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sessions.id"))
    prompt: Mapped[str] = mapped_column(String)
    response: Mapped[dict] = mapped_column(JSON)
    ts: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    hits: Mapped[int] = mapped_column(Integer, default=0)

    session: Mapped["Session"] = relationship(back_populates="dialogues")


class Asset3D(Base):
    __tablename__ = "3d_assets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prompt: Mapped[str] = mapped_column(String)
    gltf_url: Mapped[str] = mapped_column(String)
    meta: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # includes vertices, textures, embedding
    gen_ts: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    usage_count: Mapped[int] = mapped_column(Integer, default=0)


class Vignette(Base):
    __tablename__ = "vignettes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    house_num: Mapped[int] = mapped_column(Integer)
    base_prompt: Mapped[str] = mapped_column(String)
    objects: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    memory_script: Mapped[str | None] = mapped_column(String, nullable=True)