"""HTTP routes for ACE Music web UI."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from src.ace_client import GenerationParams
from src.config import get_settings
from src.web import database as db
from src.web.generation import submit_generation

log = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))

settings = get_settings()


# ── Pages ────────────────────────────────────────────────────────────────────


@router.get("/", response_class=HTMLResponse)
async def home():
    """Redirect to generation page."""
    return RedirectResponse("/generate", status_code=302)


@router.get("/generate", response_class=HTMLResponse)
async def generate_page(
    request: Request,
    prompt: str = "",
    audio_duration: float = 0,
    audio_format: str = "",
):
    """Show the music generation form. Supports pre-fill via query params for re-generate."""
    return templates.TemplateResponse("generate.html", {
        "request": request,
        "settings": settings,
        "prefill_prompt": prompt,
        "prefill_duration": audio_duration if audio_duration > 0 else settings.default_duration,
        "prefill_format": audio_format or settings.default_format,
    })


@router.get("/library", response_class=HTMLResponse)
async def library_page(request: Request, search: str = ""):
    """Show the track library."""
    tracks = await db.get_tracks(search_query=search or None)
    return templates.TemplateResponse("library.html", {
        "request": request,
        "tracks": tracks,
        "search": search,
    })


# ── Generation API ───────────────────────────────────────────────────────────


@router.post("/api/generate", response_class=HTMLResponse)
async def api_generate(
    request: Request,
    prompt: Annotated[str, Form()],
    lyrics: Annotated[str, Form()] = "",
    audio_duration: Annotated[float, Form()] = 120.0,
    audio_format: Annotated[str, Form()] = "mp3",
    bpm: Annotated[str, Form()] = "",
    key_scale: Annotated[str, Form()] = "",
    time_signature: Annotated[str, Form()] = "",
    seed: Annotated[int, Form()] = -1,
    inference_steps: Annotated[int, Form()] = 8,
    guidance_scale: Annotated[float, Form()] = 7.0,
    thinking: Annotated[str, Form()] = "",
):
    """Submit a generation task. Returns progress partial for HTMX."""
    if not prompt.strip():
        return templates.TemplateResponse("partials/error.html", {
            "request": request,
            "message": "Prompt is required.",
        })

    params = GenerationParams(
        prompt=prompt.strip(),
        lyrics=lyrics.strip(),
        audio_duration=audio_duration,
        audio_format=audio_format,
        bpm=int(bpm) if bpm.strip() else None,
        key_scale=key_scale.strip(),
        time_signature=time_signature.strip(),
        seed=seed,
        inference_steps=inference_steps,
        guidance_scale=guidance_scale,
        thinking=thinking == "on",
    )

    try:
        track = await submit_generation(params)
    except Exception as e:
        log.exception("Generation submission failed")
        return templates.TemplateResponse("partials/error.html", {
            "request": request,
            "message": f"Failed to submit: {e}",
        })

    return templates.TemplateResponse("partials/progress.html", {
        "request": request,
        "track": track,
    })


# ── Track Status (HTMX polling) ─────────────────────────────────────────────


@router.get("/api/tracks/{track_id}/status", response_class=HTMLResponse)
async def api_track_status(request: Request, track_id: int):
    """Return progress or result partial. HTMX polls this every 2s."""
    track = await db.get_track(track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    if track.status in ("queued", "generating"):
        return templates.TemplateResponse("partials/progress.html", {
            "request": request,
            "track": track,
        })

    if track.status == "completed":
        return templates.TemplateResponse("partials/result.html", {
            "request": request,
            "track": track,
        })

    # Failed
    return templates.TemplateResponse("partials/error.html", {
        "request": request,
        "message": track.error_message or "Generation failed.",
    })


# ── Track Management ─────────────────────────────────────────────────────────


@router.get("/api/tracks/{track_id}/download")
async def api_download_track(track_id: int):
    """Download a track file."""
    track = await db.get_track(track_id)
    if not track or not track.file_path:
        raise HTTPException(status_code=404, detail="Track not found")

    path = Path(track.file_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")

    # Build a readable filename from prompt
    safe_name = "".join(c if c.isalnum() or c in " -_" else "" for c in track.prompt[:40]).strip()
    safe_name = safe_name or "track"
    filename = f"{safe_name}.{track.audio_format}"

    return FileResponse(
        path,
        media_type=f"audio/{track.audio_format}",
        filename=filename,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.delete("/api/tracks/{track_id}", response_class=HTMLResponse)
async def api_delete_track(track_id: int):
    """Delete a track (file + database record). Returns empty for HTMX swap."""
    track = await db.delete_track(track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    # Remove audio file if it exists
    if track.file_path:
        path = Path(track.file_path)
        if path.exists():
            path.unlink()
            log.info("Deleted audio file: %s", path)

    return HTMLResponse("")
