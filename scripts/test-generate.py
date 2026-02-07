#!/usr/bin/env python3
"""Generate a test track via the ACE-Step API.

Creates a short ambient track to verify the full generation pipeline works.
Requires a running ACE-Step API server (GPU REQUIRED).

Usage:
    python scripts/test-generate.py
    python scripts/test-generate.py --caption "upbeat pop" --duration 60
    python scripts/test-generate.py --caption "spa meditation" --duration 30 --instrumental
"""

import asyncio
import sys
import time
from pathlib import Path

import click

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console

from src.ace_client import AceStepClient, GenerationParams
from src.config import get_settings


@click.command()
@click.option("--caption", default="ambient lounge jazz, soft piano, gentle strings", help="Style description")
@click.option("--duration", default=30, help="Duration in seconds (keep short for testing)")
@click.option("--instrumental", is_flag=True, help="Instrumental only, no vocals")
@click.option("--format", "audio_format", default="mp3", type=click.Choice(["mp3", "wav", "flac"]))
@click.option("--output-dir", default="outputs", help="Output directory")
def main(
    caption: str,
    duration: int,
    instrumental: bool,
    audio_format: str,
    output_dir: str,
) -> None:
    """Generate a test track via ACE-Step API."""
    asyncio.run(_generate(caption, duration, instrumental, audio_format, Path(output_dir)))


async def _generate(
    caption: str,
    duration: int,
    instrumental: bool,
    audio_format: str,
    output_dir: Path,
) -> None:
    console = Console()
    settings = get_settings()

    console.print("\n[bold]ACE-Step Test Generation[/bold]")
    console.print(f"  API: {settings.acestep_api_url}")
    console.print(f"  Caption: {caption}")
    console.print(f"  Duration: {duration}s")
    console.print(f"  Instrumental: {instrumental}")
    console.print(f"  Format: {audio_format}")
    console.print()

    params = GenerationParams(
        prompt=caption,
        audio_duration=duration,
        audio_format=audio_format,
        # If instrumental, set lyrics to empty (ACE-Step interprets this as instrumental)
        lyrics="" if instrumental else "",
    )

    async with AceStepClient(
        settings.acestep_api_url,
        settings.acestep_api_key,
    ) as client:
        # Submit
        console.print("[yellow]Submitting generation task...[/yellow]")
        start_time = time.monotonic()
        task_id = await client.generate(params)
        console.print(f"  Task ID: {task_id}")

        # Wait
        console.print("[yellow]Waiting for completion...[/yellow]")
        result = await client.wait_for_completion(
            task_id,
            poll_interval=settings.poll_interval,
            timeout=settings.poll_timeout,
        )
        gen_time = time.monotonic() - start_time
        console.print(f"  Generation time: {gen_time:.1f}s")

        # Download
        filename = f"test-{task_id[:8]}.{audio_format}"
        output_path = await client.download_audio(result.result, output_dir / filename)
        file_size = output_path.stat().st_size / (1024 * 1024)

        console.print()
        console.print("[green bold]Generation complete![/green bold]")
        console.print(f"  File: {output_path}")
        console.print(f"  Size: {file_size:.1f} MB")
        console.print(f"  Time: {gen_time:.1f}s")


if __name__ == "__main__":
    main()
