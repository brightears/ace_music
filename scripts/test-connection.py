#!/usr/bin/env python3
"""Test connection to ACE-Step API server.

Quick diagnostic: checks /health and /v1/models endpoints.
Requires ACESTEP_API_URL and ACESTEP_API_KEY in .env or environment.

Usage:
    python scripts/test-connection.py
    ACESTEP_API_URL=http://gpu-server:8001 python scripts/test-connection.py
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.table import Table

from src.ace_client import AceStepClient
from src.config import get_settings


async def main() -> None:
    console = Console()
    settings = get_settings()

    console.print(f"\nACE-Step API Connection Test")
    console.print(f"URL: [bold]{settings.acestep_api_url}[/bold]")
    console.print(f"API Key: {'[green]set[/green]' if settings.acestep_api_key else '[yellow]not set[/yellow]'}")
    console.print()

    async with AceStepClient(
        settings.acestep_api_url,
        settings.acestep_api_key,
        timeout=15.0,
    ) as client:
        # Test 1: Health
        try:
            health = await client.health()
            console.print("[green]1. /health[/green]", health)
        except Exception as e:
            console.print(f"[red]1. /health FAILED:[/red] {e}")
            console.print("\n[yellow]Troubleshooting:[/yellow]")
            console.print("  - Is the API server running?")
            console.print("  - Check ACESTEP_API_URL in your .env file")
            console.print("  - For cloud GPU: check the proxy URL and port exposure")
            return

        # Test 2: Models
        try:
            models = await client.list_models()
            console.print("[green]2. /v1/models[/green]")
            if "models" in models:
                table = Table(title="Available Models")
                table.add_column("Name")
                table.add_column("Default")
                for m in models["models"]:
                    name = m.get("name", str(m))
                    is_default = "yes" if m.get("is_default") else ""
                    table.add_row(name, is_default)
                console.print(table)
            else:
                console.print(f"  Response: {models}")
        except Exception as e:
            console.print(f"[red]2. /v1/models FAILED:[/red] {e}")
            console.print("  This might be an authentication issue. Check ACESTEP_API_KEY.")

    console.print("\n[green bold]Connection test complete.[/green bold]")


if __name__ == "__main__":
    asyncio.run(main())
