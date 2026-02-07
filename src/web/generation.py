"""Generation orchestration — bridges FastAPI routes and ace_client.py."""

from __future__ import annotations

import asyncio
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

from src.ace_client import AceStepClient, GenerationParams
from src.config import get_settings
from src.web.database import Track, get_session

log = logging.getLogger(__name__)


async def submit_generation(params: GenerationParams) -> Track:
    """Submit a generation task to ACE-Step and save to database.

    Creates a Track record, submits to the API, then fires a background
    task to poll for completion. Returns immediately with the queued track.
    """
    settings = get_settings()

    # Submit to ACE-Step API
    async with AceStepClient(settings.acestep_api_url, settings.acestep_api_key) as client:
        task_id = await client.generate(params)

    # Save to database
    track = Track(
        task_id=task_id,
        prompt=params.prompt,
        lyrics=params.lyrics or None,
        audio_duration=params.audio_duration,
        bpm=params.bpm,
        key_scale=params.key_scale or None,
        time_signature=params.time_signature or None,
        seed=params.seed,
        batch_size=params.batch_size,
        audio_format=params.audio_format,
        task_type=params.task_type,
        vocal_language=params.vocal_language,
        inference_steps=params.inference_steps,
        guidance_scale=params.guidance_scale,
        thinking=params.thinking,
        status="queued",
        generation_params=params.model_dump(),
    )
    async with get_session() as session:
        session.add(track)
        await session.flush()
        track_id = track.id

    # Fire background polling task
    asyncio.create_task(_poll_and_update(track_id, task_id))
    return track


async def _poll_and_update(track_id: int, task_id: str) -> None:
    """Background task: poll ACE-Step API until done, update database."""
    settings = get_settings()

    # Mark as generating and get audio format
    async with get_session() as session:
        track = await session.get(Track, track_id)
        if not track:
            return
        track.status = "generating"
        audio_format = track.audio_format

    start_time = time.monotonic()

    try:
        async with AceStepClient(settings.acestep_api_url, settings.acestep_api_key) as client:
            result = await client.wait_for_completion(
                task_id,
                poll_interval=settings.poll_interval,
                timeout=settings.poll_timeout,
            )

            # Download audio file
            filename = f"{task_id}.{audio_format}"
            output_dir = Path(settings.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = await client.download_audio(result.result, output_dir / filename)

            elapsed = time.monotonic() - start_time

            # Update track as completed
            async with get_session() as session:
                track = await session.get(Track, track_id)
                if track:
                    track.status = "completed"
                    track.file_path = str(output_path)
                    track.file_size = output_path.stat().st_size
                    track.generation_time = round(elapsed, 1)
                    track.updated_at = datetime.now(timezone.utc)

            log.info("Track %d completed in %.1fs: %s", track_id, elapsed, output_path)

    except TimeoutError:
        await _mark_failed(track_id, f"Timeout after {settings.poll_timeout}s")
    except Exception as e:
        log.exception("Generation failed for track %d", track_id)
        await _mark_failed(track_id, str(e))


async def _mark_failed(track_id: int, error: str) -> None:
    """Mark a track as failed with an error message."""
    async with get_session() as session:
        track = await session.get(Track, track_id)
        if track:
            track.status = "failed"
            track.error_message = error
            track.updated_at = datetime.now(timezone.utc)
