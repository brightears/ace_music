"""FastAPI application for ACE Music web UI."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.config import get_settings
from src.web.database import init_db, close_db

log = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup, cleanup on shutdown."""
    # Ensure output directory exists
    Path(settings.output_dir).mkdir(parents=True, exist_ok=True)
    Path("data").mkdir(parents=True, exist_ok=True)

    await init_db()
    log.info("Database initialized: %s", settings.database_url)
    yield
    await close_db()


app = FastAPI(
    title="ACE Music",
    description="BMAsia AI Music Generation Platform",
    version="0.1.0",
    lifespan=lifespan,
)

# Ensure directories exist before mounting static files
_audio_dir = Path(settings.output_dir)
_audio_dir.mkdir(parents=True, exist_ok=True)
app.mount("/audio", StaticFiles(directory=str(_audio_dir)), name="audio")

_static_dir = Path(__file__).parent.parent / "templates" / "static"
_static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(_static_dir)), name="static")

# Import and include routes (after app is created)
from src.web.routes import router  # noqa: E402

app.include_router(router)
