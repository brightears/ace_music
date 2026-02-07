"""Database models and session management for ACE Music web UI."""

from __future__ import annotations

from datetime import datetime, timezone
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import JSON, Float, Integer, String, Text, Boolean, DateTime, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.config import get_settings


class Base(DeclarativeBase):
    pass


class Track(Base):
    """A generated music track with metadata."""

    __tablename__ = "tracks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)

    # Generation parameters (user input)
    prompt: Mapped[str] = mapped_column(Text, default="")
    lyrics: Mapped[str | None] = mapped_column(Text, nullable=True)
    audio_duration: Mapped[float] = mapped_column(Float, default=120.0)
    bpm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    key_scale: Mapped[str | None] = mapped_column(String(50), nullable=True)
    time_signature: Mapped[str | None] = mapped_column(String(10), nullable=True)
    seed: Mapped[int] = mapped_column(Integer, default=-1)
    batch_size: Mapped[int] = mapped_column(Integer, default=1)
    audio_format: Mapped[str] = mapped_column(String(10), default="mp3")
    task_type: Mapped[str] = mapped_column(String(20), default="text2music")
    vocal_language: Mapped[str] = mapped_column(String(5), default="en")
    inference_steps: Mapped[int] = mapped_column(Integer, default=8)
    guidance_scale: Mapped[float] = mapped_column(Float, default=7.0)
    thinking: Mapped[bool] = mapped_column(Boolean, default=False)

    # Results
    status: Mapped[str] = mapped_column(String(20), index=True, default="queued")
    file_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    generation_time: Mapped[float | None] = mapped_column(Float, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Full params JSON for re-generation
    generation_params: Mapped[dict] = mapped_column(JSON, default=dict)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


# Engine and session factory (initialized in init_db)
_engine = None
_session_factory = None


async def init_db() -> None:
    """Create the async engine and ensure tables exist."""
    global _engine, _session_factory
    settings = get_settings()
    _engine = create_async_engine(settings.database_url, echo=False)
    _session_factory = async_sessionmaker(_engine, expire_on_commit=False)

    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Dispose of the engine connection pool."""
    global _engine
    if _engine:
        await _engine.dispose()


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session."""
    if _session_factory is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    async with _session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_track(track_id: int) -> Track | None:
    """Fetch a track by primary key."""
    async with get_session() as session:
        return await session.get(Track, track_id)


async def get_track_by_task_id(task_id: str) -> Track | None:
    """Fetch a track by ACE-Step task_id."""
    async with get_session() as session:
        result = await session.execute(select(Track).where(Track.task_id == task_id))
        return result.scalar_one_or_none()


async def get_tracks(
    search_query: str | None = None,
    status: str | None = None,
    limit: int = 200,
) -> list[Track]:
    """Fetch tracks with optional filters, newest first."""
    async with get_session() as session:
        query = select(Track).order_by(Track.created_at.desc())
        if search_query:
            pattern = f"%{search_query}%"
            query = query.where(Track.prompt.like(pattern) | Track.lyrics.like(pattern))
        if status:
            query = query.where(Track.status == status)
        query = query.limit(limit)
        result = await session.execute(query)
        return list(result.scalars().all())


async def delete_track(track_id: int) -> Track | None:
    """Delete a track by primary key. Returns the track before deletion, or None."""
    async with get_session() as session:
        track = await session.get(Track, track_id)
        if track:
            await session.delete(track)
        return track
