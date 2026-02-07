"""Async Python client for the ACE-Step v1.5 REST API.

Usage:
    from src.ace_client import AceStepClient
    from src.config import get_settings

    settings = get_settings()
    async with AceStepClient(settings.acestep_api_url, settings.acestep_api_key) as client:
        health = await client.health()
        task_id = await client.generate({"prompt": "ambient jazz", "audio_duration": 60})
        result = await client.wait_for_completion(task_id)
        path = await client.download_audio(result["result"], Path("outputs/test.mp3"))
"""

from __future__ import annotations

import asyncio
import time
from pathlib import Path
from typing import Any

import httpx
from pydantic import BaseModel


class GenerationParams(BaseModel):
    """Parameters for a music generation request."""

    prompt: str = ""
    lyrics: str = ""
    audio_duration: float = 120.0
    bpm: int | None = None
    key_scale: str = ""
    time_signature: str = ""
    seed: int = -1
    batch_size: int = 1
    audio_format: str = "mp3"
    task_type: str = "text2music"
    vocal_language: str = "en"
    inference_steps: int = 8
    guidance_scale: float = 7.0
    thinking: bool = False


class TaskResult(BaseModel):
    """Result from polling a generation task."""

    task_id: str
    status: int  # 0=queued, 1=success, 2=failed
    result: str = ""


class AceStepClient:
    """Async client for the ACE-Step v1.5 REST API.

    Handles authentication, task submission, polling, and audio download.
    Use as an async context manager for automatic resource cleanup.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8001",
        api_key: str = "",
        timeout: float = 30.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        headers: dict[str, str] = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=headers,
            timeout=timeout,
        )

    async def __aenter__(self) -> AceStepClient:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.aclose()

    # ── Health & Info ────────────────────────────────────────────────

    async def health(self) -> dict[str, Any]:
        """Check API server health. Returns status dict."""
        resp = await self._client.get("/health")
        resp.raise_for_status()
        return resp.json()

    async def list_models(self) -> dict[str, Any]:
        """List available DiT models."""
        resp = await self._client.get("/v1/models")
        resp.raise_for_status()
        return resp.json()

    # ── Generation ───────────────────────────────────────────────────

    async def generate(self, params: dict[str, Any] | GenerationParams) -> str:
        """Submit a generation task. Returns task_id."""
        if isinstance(params, GenerationParams):
            payload = params.model_dump(exclude_none=True)
        else:
            payload = params

        resp = await self._client.post("/release_task", json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data["task_id"]

    async def poll_results(self, task_ids: list[str]) -> list[TaskResult]:
        """Batch poll task statuses. Returns list of TaskResult."""
        resp = await self._client.post(
            "/query_result",
            json={"task_id_list": task_ids},
        )
        resp.raise_for_status()
        raw = resp.json()
        # API returns a list of dicts with task_id, status, result
        if isinstance(raw, list):
            return [TaskResult(**item) for item in raw]
        # Some API versions wrap in a dict
        return [TaskResult(**item) for item in raw.get("results", raw.get("data", []))]

    async def wait_for_completion(
        self,
        task_id: str,
        poll_interval: float = 2.0,
        timeout: float = 300.0,
    ) -> TaskResult:
        """Poll until a task completes or fails. Raises TimeoutError on timeout."""
        start = time.monotonic()
        while True:
            elapsed = time.monotonic() - start
            if elapsed > timeout:
                raise TimeoutError(
                    f"Task {task_id} did not complete within {timeout}s"
                )

            results = await self.poll_results([task_id])
            if results:
                result = results[0]
                if result.status == 1:
                    return result
                if result.status == 2:
                    raise RuntimeError(
                        f"Task {task_id} failed: {result.result}"
                    )

            await asyncio.sleep(poll_interval)

    # ── Audio Download ───────────────────────────────────────────────

    async def download_audio(self, audio_path: str, output_path: Path) -> Path:
        """Download a generated audio file to local disk.

        Args:
            audio_path: Server-side path returned in task result.
            output_path: Local path to save the audio file.

        Returns:
            The output_path where the file was saved.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        resp = await self._client.get("/v1/audio", params={"path": audio_path})
        resp.raise_for_status()

        output_path.write_bytes(resp.content)
        return output_path

    # ── Convenience ──────────────────────────────────────────────────

    async def generate_and_download(
        self,
        params: dict[str, Any] | GenerationParams,
        output_dir: Path = Path("outputs"),
        filename: str | None = None,
        poll_interval: float = 2.0,
        timeout: float = 300.0,
    ) -> Path:
        """Generate a track and download the result in one call.

        Args:
            params: Generation parameters.
            output_dir: Directory to save the audio file.
            filename: Override filename (default: auto from task_id).
            poll_interval: Seconds between status polls.
            timeout: Max seconds to wait for completion.

        Returns:
            Path to the downloaded audio file.
        """
        if isinstance(params, dict):
            params_obj = GenerationParams(**params)
        else:
            params_obj = params

        task_id = await self.generate(params_obj)
        result = await self.wait_for_completion(task_id, poll_interval, timeout)

        if filename is None:
            filename = f"{task_id}.{params_obj.audio_format}"

        output_path = output_dir / filename
        return await self.download_audio(result.result, output_path)

    async def format_input(
        self,
        prompt: str,
        lyrics: str = "",
        temperature: float = 0.85,
    ) -> dict[str, Any]:
        """Use LLM to enhance caption and lyrics."""
        resp = await self._client.post(
            "/format_input",
            json={
                "prompt": prompt,
                "lyrics": lyrics,
                "temperature": temperature,
            },
        )
        resp.raise_for_status()
        return resp.json()
