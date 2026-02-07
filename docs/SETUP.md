# ACE Music Platform — Setup Guide

> **Last Updated:** 2026-02-07
> **Phase:** 2 (Infrastructure Setup)

---

## Executive Summary

**For non-technical readers:** This guide explains three ways to get ACE-Step running so we can generate AI music. The fastest path (Docker on a cloud GPU) takes about 15-30 minutes and costs under $1 for a test session. Once set up, you can generate music by running simple Python scripts from your laptop — the heavy computing happens on the rented GPU server.

---

## Quick Start (Fastest Path)

**Goal:** Generate your first test track in under 30 minutes.

1. Rent a GPU on RunPod ($0.50/hr, see [Cloud GPU Setup](#path-2-cloud-gpu-recommended))
2. Run the setup script on the GPU server
3. Run `python scripts/test-generate.py` from your laptop
4. Listen to the generated audio

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Path 1: Docker (Easiest)](#path-1-docker-easiest)
3. [Path 2: Cloud GPU (Recommended)](#path-2-cloud-gpu-recommended)
4. [Path 3: Local Development](#path-3-local-development)
5. [Python Client Setup](#python-client-setup)
6. [Configuration Reference](#configuration-reference)
7. [Scripts Reference](#scripts-reference)
8. [Troubleshooting](#troubleshooting)
9. [Verification Checklist](#verification-checklist)

---

## Prerequisites

### On Your Laptop (no GPU needed)
- Python 3.11+
- uv package manager: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Git

### On the GPU Server
- NVIDIA GPU with 8GB+ VRAM (24GB recommended)
- NVIDIA drivers + CUDA 12.x
- Docker (for Docker path) or Python 3.11 + uv (for bare metal)

---

## Path 1: Docker (Easiest)

Best for: Quick testing on any machine with an NVIDIA GPU and Docker.

### Step 1: Configure

```bash
cd "ACE Music"
cp .env.example .env
# Edit .env — set your ACESTEP_API_KEY
```

### Step 2: Launch

```bash
docker compose up -d
```

This pulls the `valyriantech/ace-step-1.5` image (~15GB, includes models) and starts the API server. First pull takes 10-20 minutes.

### Step 3: Verify

```bash
# Check container is running
docker compose ps

# Check health
curl http://localhost:8001/health

# Or use our script
bash scripts/health-check.sh
```

### Step 4: Test Generation

```bash
python scripts/test-generate.py
```

### Stopping

```bash
docker compose down       # Stop (keeps data)
docker compose down -v    # Stop and remove volumes
```

---

## Path 2: Cloud GPU (Recommended)

Best for: No local GPU. Rent compute on demand, pay only while testing.

### Step 1: Create RunPod Account

1. Go to https://runpod.io and create an account
2. Add $10 credit (minimum)
3. Note your API key from Settings

### Step 2: Launch a GPU Pod

**Option A: Docker Template (Easier)**
1. Go to Pods > Deploy
2. Select "Deploy" with a custom Docker image
3. Image: `valyriantech/ace-step-1.5`
4. GPU: RTX 3090 (24GB) — ~$0.44/hr community cloud
5. Volume: 30GB (for output persistence)
6. Expose HTTP ports: `8001,7860`
7. Environment variables:
   ```
   ACESTEP_API_KEY=sk-your-secret-key
   ```
8. Deploy and wait for startup (5-15 min for model loading)

**Option B: Bare Metal (More Control)**
1. Launch a GPU pod with PyTorch template (Ubuntu + CUDA)
2. SSH into the pod or use the web terminal
3. Upload and run our setup script:
   ```bash
   # On the GPU pod:
   curl -O https://raw.githubusercontent.com/brightears/ace_music/main/scripts/setup-gpu-server.sh
   chmod +x setup-gpu-server.sh
   bash setup-gpu-server.sh
   ```
4. Start the API server:
   ```bash
   bash start-api.sh
   # Or manually:
   cd /workspace/ACE-Step-1.5
   ACESTEP_API_KEY=sk-your-key uv run acestep-api --host 0.0.0.0 --port 8001
   ```

### Step 3: Connect from Your Laptop

```bash
# Update your local .env
cp configs/cloud-runpod.env .env
# Edit .env — set ACESTEP_API_URL to your pod's proxy URL:
# https://<POD_ID>-8001.proxy.runpod.net
# Also set ACESTEP_API_KEY to match the server

# Test connection
python scripts/test-connection.py

# Generate a test track
python scripts/test-generate.py
```

### Step 4: Shut Down When Done

**Important:** Stop your pod when not in use to avoid charges.

1. RunPod Dashboard > Pods
2. Click "Stop" (preserves state) or "Terminate" (deletes everything)
3. Verify no active pods in billing dashboard

---

## Path 3: Local Development

Best for: If you have a local NVIDIA GPU (RTX 3060 or better).

### Step 1: Clone ACE-Step

```bash
git clone https://github.com/ACE-Step/ACE-Step-1.5.git /path/to/ACE-Step-1.5
cd /path/to/ACE-Step-1.5
uv sync
```

### Step 2: Download Models

```bash
uv run acestep-download
# Downloads ~12-15GB of model files to ./checkpoints/
```

### Step 3: Configure

```bash
cd "ACE Music"
cp configs/local-dev.env .env
# Edit .env if needed (defaults work for local)
```

### Step 4: Launch API Server

```bash
cd /path/to/ACE-Step-1.5
uv run acestep-api --host 127.0.0.1 --port 8001
```

Or use our script:
```bash
ACESTEP_DIR=/path/to/ACE-Step-1.5 bash scripts/start-api.sh
```

### Step 5: Test

```bash
python scripts/test-connection.py
python scripts/test-generate.py
```

---

## Python Client Setup

Our platform code uses an async Python client library to talk to the ACE-Step API. Set this up on your local machine (no GPU needed).

### Install Dependencies

```bash
cd "ACE Music"
uv sync
```

### Usage

```python
import asyncio
from pathlib import Path
from src.ace_client import AceStepClient, GenerationParams
from src.config import get_settings

async def main():
    settings = get_settings()
    async with AceStepClient(settings.acestep_api_url, settings.acestep_api_key) as client:
        # Check server health
        print(await client.health())

        # Generate a track
        params = GenerationParams(
            prompt="ambient lounge jazz, soft piano",
            audio_duration=60,
            audio_format="mp3",
        )
        path = await client.generate_and_download(params, Path("outputs"))
        print(f"Track saved to: {path}")

asyncio.run(main())
```

---

## Configuration Reference

### Environment Variables

All configuration is via environment variables, loaded from `.env` file.

| Variable | Default | Description |
|----------|---------|-------------|
| **ACESTEP_API_URL** | http://localhost:8001 | ACE-Step API server URL |
| **ACESTEP_API_KEY** | (empty) | API authentication key |
| ACESTEP_CONFIG_PATH | acestep-v15-turbo | DiT model name |
| ACESTEP_LM_MODEL_PATH | acestep-5Hz-lm-1.7B | Language model name |
| ACESTEP_LM_BACKEND | vllm | LM runtime: vllm or pt |
| ACESTEP_DEVICE | cuda | Compute device |
| ACESTEP_API_HOST | 0.0.0.0 | Server bind address |
| ACESTEP_API_PORT | 8001 | Server port |
| ACESTEP_INIT_LLM | auto | LLM init: auto/true/false |
| ACESTEP_OUTPUT_DIR | ./outputs | Audio output directory |
| ACESTEP_QUEUE_WORKERS | 1 | Queue workers (must be 1) |
| ACESTEP_QUEUE_MAXSIZE | 200 | Max queue depth |

Bold = most commonly changed.

### Config Templates

Pre-configured `.env` files for common scenarios:

| Template | File | Use Case |
|----------|------|----------|
| Local Dev | `configs/local-dev.env` | Local machine with GPU |
| RunPod | `configs/cloud-runpod.env` | RunPod cloud GPU |
| Vast.ai | `configs/cloud-vastai.env` | Vast.ai cloud GPU |

Usage: `cp configs/cloud-runpod.env .env` then edit with your specific values.

---

## Scripts Reference

### GPU Server Scripts (run on the GPU machine)

| Script | Description |
|--------|-------------|
| `scripts/setup-gpu-server.sh` | Full setup from scratch: installs uv, clones ACE-Step, downloads models |
| `scripts/start-api.sh` | Start API server with config from .env |
| `scripts/start-ui.sh` | Start Gradio web UI for manual exploration |
| `scripts/download-models.sh` | Download/manage model files |
| `scripts/health-check.sh` | Verify API server health |

### Local Scripts (run from your laptop)

| Script | Description |
|--------|-------------|
| `scripts/test-connection.py` | Test API connectivity, list models |
| `scripts/test-generate.py` | Generate a test track, download audio |

---

## Troubleshooting

### Connection Issues

| Problem | Solution |
|---------|----------|
| `Connection refused` | Server not running. Check `docker compose ps` or process list |
| `401 Unauthorized` | API key mismatch. Check ACESTEP_API_KEY in both .env and server |
| `Connection timeout` | Wrong URL. For RunPod, use the proxy URL format |
| `502 Bad Gateway` | Server starting up. Wait 2-5 minutes for model loading |

### Generation Issues

| Problem | Solution |
|---------|----------|
| Empty audio file | GPU OOM. Reduce duration or disable LLM (`ACESTEP_INIT_LLM=false`) |
| Very slow | Check GPU is being used: `nvidia-smi` should show process |
| Task stays queued | Previous task may be running. Queue is sequential (workers=1) |
| Task failed (status=2) | Check server logs. Common: duration too long for VRAM tier |

### Docker Issues

| Problem | Solution |
|---------|----------|
| `nvidia-container-cli` error | Install nvidia-container-toolkit |
| Image pull slow | Image is ~15GB. Use a fast network connection |
| Container OOM killed | Reduce model size or increase Docker memory limit |

---

## Verification Checklist

After setup, verify each component:

- [ ] `.env` file exists with correct API URL and key
- [ ] `uv sync` completes without errors (local Python environment)
- [ ] `python scripts/test-connection.py` shows healthy server
- [ ] `python scripts/test-generate.py` produces an audio file
- [ ] Audio file plays correctly and sounds like music
- [ ] `bash scripts/health-check.sh` passes all checks (if running locally)
