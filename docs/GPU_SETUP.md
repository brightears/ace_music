# ACE Music Platform — Cloud GPU Setup Guide

> **Last Updated:** 2026-02-07
> **Phase:** 3 (Cloud GPU Setup)

---

## Executive Summary

**For non-technical readers:** To generate AI music, we need to rent a powerful graphics card (GPU) in the cloud. Think of it like renting a powerful computer by the hour. The cheapest option costs about $0.20/hour — so a 30-minute test session to hear our first AI-generated tracks costs less than a cup of coffee (~$0.10-0.35). A full production run of 15,000 tracks costs roughly $16 on an A100 GPU, compared to ~$1,000 with our current Mureka service.

**Recommendation:** Start with RunPod (easiest setup, ~$0.20-0.46/hr for RTX 3090). Switch to Vast.ai for production batch generation (cheaper for longer sessions). TensorDock is worth considering for budget runs.

**Time to first track:** 15-30 minutes from creating an account.

---

## Table of Contents

1. [Provider Comparison](#provider-comparison)
2. [GPU Selection Guide](#gpu-selection-guide)
3. [Quick Start: RunPod](#quick-start-runpod)
4. [Quick Start: Vast.ai](#quick-start-vastai)
5. [Quick Start: TensorDock](#quick-start-tensordock)
6. [Connecting from Your Laptop](#connecting-from-your-laptop)
7. [Persistence](#persistence--dont-reinstall-every-time)
8. [Cost Estimates](#cost-estimates)
9. [Scaling for Batch Generation](#scaling-for-batch-generation)
10. [Security](#security)
11. [Shutdown Checklist](#shutdown-checklist)
12. [Troubleshooting](#troubleshooting)

---

## Provider Comparison

| Factor | RunPod | Vast.ai | TensorDock |
|--------|--------|---------|------------|
| **Best For** | First test, ease of use | Production batches, lowest cost | Budget testing |
| **RTX 3090 (24GB)** | $0.20-0.46/hr (community) | $0.15-0.40/hr | $0.09-0.40/hr |
| **RTX 4090 (24GB)** | $0.44-0.69/hr | $0.30-0.50/hr | $0.30-0.50/hr |
| **A100 80GB** | $1.33-1.90/hr | $0.80-1.50/hr | $0.80-1.20/hr |
| **Minimum Deposit** | $10 | $5 | $5 |
| **Billing** | Per-second | Per-second | Per-minute |
| **Docker Support** | Excellent | Good | Good |
| **HTTP Port Proxy** | Built-in (*.proxy.runpod.net) | Manual setup required | Manual setup |
| **Setup Ease** | Easiest (5/5) | Medium (3/5) | Medium (3/5) |
| **Persistent Storage** | Network Volumes ($0.07/GB/mo) | Disk storage on instance | Block storage |
| **ACE-Step Template** | None (use Docker image) | Serverless template available | None |
| **Spot/Interruptible** | Yes (cheaper but can be preempted) | Yes (bid-based pricing) | Limited |

**Prices are approximate and fluctuate based on demand. Check provider websites for current rates.**

### Our Recommendation

| Scenario | Provider | GPU | Why |
|----------|----------|-----|-----|
| First test | **RunPod** | RTX 3090 | Easiest setup, proxy URL built-in, 15 min to first track |
| Quality evaluation | RunPod or Vast.ai | RTX 3090/4090 | Either works, Vast.ai cheaper for 2+ hour sessions |
| Production batch | **Vast.ai** | A100 80GB | Lowest cost for long-running jobs |
| Budget testing | TensorDock | RTX 3090 | Cheapest hourly rates |

---

## GPU Selection Guide

| GPU | VRAM | ACE-Step Speed | Max Duration | Max Batch | Best For |
|-----|------|---------------|-------------|-----------|----------|
| RTX 3090 | 24GB | ~6s/track | 10 min | 8 | Testing, small batches |
| RTX 4090 | 24GB | ~4s/track | 10 min | 8 | Faster testing |
| A100 40GB | 40GB | ~3s/track | 10 min | 8 | Production batches |
| A100 80GB | 80GB | ~2s/track | 10 min | 8 | Maximum throughput |
| H100 | 80GB | ~1.5s/track | 10 min | 8 | Overkill for our needs |

**For our use case (background music generation):** RTX 3090 is the sweet spot for testing. A100 80GB is ideal for generating thousands of tracks.

---

## Quick Start: RunPod

**Goal:** Generate your first test track. Time: ~15-30 minutes. Cost: <$1.

### Step 1: Create Account

1. Go to https://www.runpod.io
2. Click "Sign Up" and create an account
3. Go to **Settings > Billing** and add $10 credit (minimum)
4. Verify your account

### Step 2: Deploy a GPU Pod

1. Go to **Pods** in the left sidebar
2. Click **+ Deploy**
3. Select your GPU:
   - For first test: **RTX 3090** (Community Cloud, ~$0.20-0.46/hr)
   - For quality evaluation: **RTX 4090** or **A100 80GB**
4. Under **Container Image**, enter: `valyriantech/ace-step-1.5`
5. Click **Edit Template** to configure:
   - **Container Disk:** 20 GB (for temporary files)
   - **Volume Disk:** 5 GB (for output persistence — optional)
   - **Expose HTTP Ports:** `8001,7860` (comma-separated, no spaces)
   - **Environment Variables:**
     ```
     ACESTEP_API_KEY=sk-your-test-key-here
     ```
6. Click **Deploy On-Demand** (or **Spot** for cheaper but interruptible)
7. Wait for the pod to start (status changes from "Creating" to "Running")

### Step 3: Wait for Initialization

The first startup takes 2-5 minutes because the Docker image already includes the models. Watch the logs:

1. Click your pod name to see details
2. Click **Logs** to monitor startup
3. Wait until you see: `Uvicorn running on http://0.0.0.0:8000`

**Note:** The ValyrianTech image runs on port 8000 internally. RunPod maps this via the proxy.

### Step 4: Get Your API URL

1. In your pod details, look for **Connect**
2. Find the HTTP Service URL for port 8001:
   - Format: `https://<POD_ID>-8001.proxy.runpod.net`
3. Test it:
   ```bash
   curl https://<POD_ID>-8001.proxy.runpod.net/health
   # Expected: {"status": "ok", ...}
   ```

**Important:** The proxy URL maps host port 8001 to container port 8000 automatically when using the ValyrianTech image. If /health doesn't respond on 8001, try port 8000:
- `https://<POD_ID>-8000.proxy.runpod.net/health`

### Step 5: Generate Your First Track

On your laptop:
```bash
cd "ACE Music"

# Create .env from RunPod template
cp configs/cloud-runpod.env .env

# Edit .env — set your pod URL and API key:
# ACESTEP_API_URL=https://<POD_ID>-8001.proxy.runpod.net
# ACESTEP_API_KEY=sk-your-test-key-here

# Test connection
python scripts/test-connection.py

# Generate a 30-second test track
python scripts/test-generate.py --caption "ambient lounge jazz, soft piano" --duration 30
```

Your first AI-generated track will be saved in the `outputs/` folder.

### Step 6: Explore (Optional)

Access the Gradio UI for hands-on exploration:
- URL: `https://<POD_ID>-7860.proxy.runpod.net`
- This gives you a visual interface to tweak parameters and hear results instantly

---

## Quick Start: Vast.ai

**Goal:** Cheaper alternative for longer sessions. Time: ~20-40 minutes.

### Step 1: Create Account

1. Go to https://vast.ai
2. Create an account
3. Add $5+ credit via Settings > Billing

### Step 2: Find an Instance

1. Go to **Search** (or **Create** > **Instance**)
2. Set filters:
   - **GPU:** RTX 3090 or A100
   - **Docker Image:** `valyriantech/ace-step-1.5`
   - **Disk Space:** 30+ GB
   - Sort by: **Price (low to high)**
3. Look for instances with:
   - Good reliability score (>95%)
   - Low latency to your region
   - "Docker" support enabled

### Step 3: Configure and Launch

1. Select your instance
2. Set the Docker image: `valyriantech/ace-step-1.5`
3. Configure environment variables:
   ```
   ACESTEP_API_KEY=sk-your-test-key-here
   ```
4. Expose port **8001** (and optionally **7860**)
5. Click **Rent** to launch

### Step 4: Connect

1. Wait for the instance to show "Running" status
2. Find the public IP and mapped port in the instance details
3. Your API URL will be: `http://<PUBLIC_IP>:<MAPPED_PORT>`
4. Test: `curl http://<PUBLIC_IP>:<MAPPED_PORT>/health`

### Step 5: Generate

Same as RunPod Step 5 — update your `.env` with the Vast.ai URL and run the test scripts.

**Vast.ai Note:** Port mapping works differently than RunPod. Vast.ai assigns random external ports. Check your instance details for the actual mapped port number.

---

## Quick Start: TensorDock

### Step 1: Create Account

1. Go to https://www.tensordock.com
2. Create an account and add credit ($5 minimum)

### Step 2: Deploy

1. Go to **Deploy** > **Cloud GPU**
2. Select RTX 3090 (look for lowest price)
3. Choose **Docker** deployment
4. Image: `valyriantech/ace-step-1.5`
5. Expose ports 8001 and 7860
6. Set `ACESTEP_API_KEY` environment variable
7. Deploy and wait for startup

### Step 3: Connect and Generate

Same workflow as RunPod/Vast.ai — get your instance IP, update `.env`, run test scripts.

---

## Connecting from Your Laptop

After deploying on any provider, the workflow is the same:

```bash
cd "ACE Music"

# 1. Copy the appropriate config template
cp configs/cloud-runpod.env .env   # or cloud-vastai.env

# 2. Edit .env with your actual values
#    ACESTEP_API_URL=<your-instance-url>
#    ACESTEP_API_KEY=<your-api-key>

# 3. Verify connection
python scripts/test-connection.py

# 4. Run health check
bash scripts/health-check.sh

# 5. Generate your first track
python scripts/test-generate.py

# 6. Generate with custom parameters
python scripts/test-generate.py \
  --caption "spa wellness, nature sounds, meditation" \
  --duration 60 \
  --instrumental
```

### Using the Python Client Library

```python
import asyncio
from pathlib import Path
from src.ace_client import AceStepClient, GenerationParams
from src.config import get_settings

async def main():
    settings = get_settings()
    async with AceStepClient(settings.acestep_api_url, settings.acestep_api_key) as client:
        # Generate an ambient track
        params = GenerationParams(
            prompt="hotel lobby ambient, soft piano, gentle strings, warm atmosphere",
            audio_duration=120,
            audio_format="mp3",
        )
        path = await client.generate_and_download(params, Path("outputs"))
        print(f"Track saved: {path}")

asyncio.run(main())
```

---

## Persistence — Don't Reinstall Every Time

The biggest time waste is re-downloading models on every session. Here's how to avoid it:

### RunPod: Network Volumes

1. Go to **Storage** in the sidebar
2. Create a **Network Volume** (5 GB is enough for outputs, the Docker image has models baked in)
3. When creating a pod, attach the volume
4. Mount it at `/app/outputs` for output persistence
5. Models are in the Docker image — they don't need separate storage

**Key insight:** The `valyriantech/ace-step-1.5` image includes models (~15GB). You don't need to download models separately when using Docker. Network volumes are only needed for persisting output files across sessions.

### Vast.ai: Instance Disk

1. When renting, choose an instance with enough disk (30+ GB)
2. **Stop** (don't destroy) your instance when done — this preserves all state
3. **Restart** when needed — everything is still there
4. Only **destroy** when you're completely done — this deletes everything

**Stopping vs Destroying:**
- **Stop:** GPU released (no compute charge), disk preserved (small storage charge ~$0.01-0.05/hr)
- **Destroy:** Everything deleted, no charges

### Bare Metal Setup (No Docker)

If you set up ACE-Step manually (not Docker), models are in `./checkpoints/`:
1. Use a persistent volume for the entire ACE-Step directory
2. First session: run `scripts/setup-gpu-server.sh` (downloads ~12-15GB of models)
3. Subsequent sessions: just run `scripts/start-api.sh` (instant start)

---

## Cost Estimates

### Per-Session Estimates

| Session Type | GPU | Duration | Tracks | RunPod Cost | Vast.ai Cost |
|-------------|-----|----------|--------|-------------|-------------|
| Quick test | RTX 3090 | 30 min | 20 | ~$0.10-0.23 | ~$0.08-0.20 |
| Extended test | RTX 3090 | 1 hour | 100 | ~$0.20-0.46 | ~$0.15-0.40 |
| Quality eval | RTX 3090 | 2 hours | 300 | ~$0.40-0.92 | ~$0.30-0.80 |
| Small batch | A100 80GB | 2 hours | 2,000 | ~$2.66-3.80 | ~$1.60-3.00 |
| Medium batch | A100 80GB | 5 hours | 5,000 | ~$6.65-9.50 | ~$4.00-7.50 |
| Full catalog | A100 80GB | 8 hours | 15,000 | ~$10.64-15.20 | ~$6.40-12.00 |

**Notes:**
- Estimates include ~5-10 min startup overhead per session
- Actual track count depends on duration settings (shorter tracks = more per hour)
- Assumes 120s tracks on RTX 3090 (~6s/track), 120s tracks on A100 (~2s/track)

### Cost Comparison: ACE-Step vs Mureka

| Volume | ACE-Step (Vast.ai A100) | ACE-Step (RunPod 3090) | Mureka |
|--------|------------------------|------------------------|--------|
| 100 tracks | ~$0.30 | ~$0.50 | ~$6 |
| 1,000 tracks | ~$1.50 | ~$3.00 | ~$57 |
| 5,000 tracks | ~$5.00 | ~$10.00 | ~$285 |
| 15,000 tracks | ~$10.00 | ~$20.00 | ~$1,000 |

**Bottom line:** Self-hosted ACE-Step is 50-100x cheaper than Mureka at scale.

### Monthly Budget Scenarios

| Usage Pattern | Provider | Monthly Cost |
|---------------|----------|-------------|
| Light testing (2 hrs/week) | RunPod RTX 3090 | ~$4-8/month |
| Regular generation (8 hrs/week) | Vast.ai RTX 3090 | ~$5-12/month |
| Production batches (20 hrs/month) | Vast.ai A100 | ~$20-30/month |
| Heavy production (80 hrs/month) | Vast.ai A100 | ~$65-120/month |

---

## Scaling for Batch Generation

For generating thousands of tracks efficiently:

### Single-Instance Optimization

ACE-Step can generate up to 8 tracks simultaneously (batch_size=8) on 24GB+ VRAM:
- RTX 3090: batch_size=6-8, ~6s per batch of 8 = 4,800 tracks/hour
- A100 80GB: batch_size=8, ~2s per batch of 8 = 14,400 tracks/hour

### Multi-Instance Scaling

For maximum throughput, run multiple ACE-Step instances:

1. Deploy 2-4 GPU pods on the same provider
2. Each runs its own ACE-Step API server
3. Your batch generation script distributes work across instances
4. Combine outputs when all instances finish

**Example: 15,000 tracks on 4x A100:**
- Each instance generates ~3,750 tracks
- Time: ~30 minutes per instance
- Cost: 4 instances x 0.5 hours x ~$1.50/hr = ~$3.00 total
- Compare: Mureka = ~$1,000

### API Constraint Reminder

Each ACE-Step instance must run with `workers=1` (in-memory queue). Do NOT try to scale by increasing workers — deploy separate instances instead.

---

## Security

### API Key Management

- **Always set `ACESTEP_API_KEY`** when deploying to cloud — without it, anyone who discovers your URL can generate tracks on your GPU
- Use strong random keys: `openssl rand -hex 32` generates a good key
- Store keys in `.env` (git-ignored), never in code or config templates
- Rotate keys between sessions if concerned about exposure

### Network Exposure

- **RunPod:** URLs are semi-private (requires knowing the pod ID), but not truly secret. Always use an API key.
- **Vast.ai:** Public IP is visible. API key is essential.
- **TensorDock:** Same as Vast.ai — public IP, needs API key.

### Best Practices

1. Set a unique API key for each session: `ACESTEP_API_KEY=sk-$(openssl rand -hex 16)`
2. Don't share proxy URLs or IPs publicly
3. Shut down instances when not in use (no exposure when off)
4. Keep `.env` in `.gitignore` (already configured)

---

## Shutdown Checklist

**Run through this EVERY TIME you finish a session to avoid surprise charges.**

- [ ] **Download outputs:** Copy any generated audio you want to keep from the GPU server to your laptop
  ```bash
  # If using API, your test scripts already download locally
  # If using Gradio UI, manually download tracks you want to keep
  ```
- [ ] **Stop or destroy the instance:**
  - **RunPod:** Pod details > **Stop Pod** (preserves state) or **Terminate** (deletes)
  - **Vast.ai:** Instance > **Stop** (preserves disk) or **Destroy** (deletes)
  - **TensorDock:** Instance > **Stop** or **Delete**
- [ ] **Verify no active instances:** Check the provider's dashboard/billing page
- [ ] **Check billing:** Confirm no unexpected charges in the provider's billing section
- [ ] **Clear your .env** (optional): Remove or comment out the cloud API URL to avoid accidentally connecting to a non-existent server

### Common Billing Gotcha

**Stopped instances still cost money on some providers** (disk storage charges). If you're done for the week:
- **RunPod:** Terminate the pod, keep the Network Volume (cheap: $0.07/GB/month)
- **Vast.ai:** Destroy the instance (no charges). Re-create when needed (models are in Docker image, fast restart)
- **TensorDock:** Delete the instance

---

## Troubleshooting

### Connection Issues

| Problem | Likely Cause | Solution |
|---------|-------------|----------|
| `Connection refused` | Server not started yet | Wait 2-5 min after pod creation for Docker startup |
| `502 Bad Gateway` | Server still loading models | Wait for startup. Check pod logs for progress |
| `Connection timeout` | Wrong URL or port | Double-check proxy URL format. RunPod: `https://<POD_ID>-<PORT>.proxy.runpod.net` |
| `401 Unauthorized` | API key mismatch | Ensure ACESTEP_API_KEY matches between server env and your .env |
| `/health` works but `/release_task` fails | Port mapping issue | ValyrianTech image uses port 8000 internally. Try port 8000 in proxy URL |

### Generation Issues

| Problem | Likely Cause | Solution |
|---------|-------------|----------|
| Empty/silent audio file | OOM (out of memory) | Reduce duration, use batch_size=1, disable LLM: `ACESTEP_INIT_LLM=false` |
| Very slow generation (>60s) | CPU inference, not GPU | Check `nvidia-smi` in pod terminal. GPU should show utilization |
| Task stays at status=0 | Previous task still running | Wait. Queue is sequential. Check with repeated poll calls |
| Task failed (status=2) | Various | Check server logs. Common: unsupported parameters, model not loaded |
| Audio sounds wrong/distorted | Bad parameters | Try different seed (-1 for random). Reduce guidance_scale. Use turbo model |

### Provider-Specific Issues

**RunPod:**
- Pod stuck in "Creating" > Check if selected GPU is available. Try a different region.
- Proxy URL not working > Ensure HTTP ports (8001,7860) are listed in pod config.
- "Insufficient funds" > Add more credit. RunPod pre-authorizes based on estimated usage.

**Vast.ai:**
- Instance won't start > Host might be offline. Choose a different instance.
- Can't expose ports > Check that instance supports "Direct" port exposure (not all do).
- Random port numbers > Vast.ai assigns external ports dynamically. Check instance details for mapping.

**TensorDock:**
- Limited GPU availability > TensorDock has fewer hosts. Check during off-peak hours.
- Docker not working > Not all TensorDock instances support Docker. Filter for Docker-capable instances.

### Emergency: Instance Won't Stop

If you can't stop an instance through the UI:
1. **RunPod:** Use the API: `curl -X POST https://api.runpod.io/v2/<POD_ID>/stop -H "Authorization: Bearer <API_KEY>"`
2. **Vast.ai:** Use the CLI tool: `vastai destroy instance <INSTANCE_ID>`
3. **Any provider:** Contact support immediately if billing is a concern

---

## Quick Reference Card

For printing or saving as a cheat sheet:

```
=== ACE Music — Cloud GPU Quick Reference ===

SETUP:
  1. Copy config:    cp configs/cloud-runpod.env .env
  2. Edit .env:      Set ACESTEP_API_URL and ACESTEP_API_KEY
  3. Test:           python scripts/test-connection.py
  4. Generate:       python scripts/test-generate.py

RUNPOD URL FORMAT:
  https://<POD_ID>-8001.proxy.runpod.net

VASTAI URL FORMAT:
  http://<PUBLIC_IP>:<MAPPED_PORT>

DOCKER IMAGE:
  valyriantech/ace-step-1.5

ENV VARS (set on GPU server):
  ACESTEP_API_KEY=sk-your-key
  ACESTEP_CONFIG_PATH=acestep-v15-turbo  (optional, default in image)

COST:
  Quick test:   ~$0.10-0.35  (30 min, 20 tracks)
  Quality eval: ~$0.50-1.50  (2 hrs, 200+ tracks)
  Full catalog: ~$10-20      (8 hrs, 15,000 tracks)

SHUTDOWN:
  Always stop/terminate when done!
  Check billing dashboard for active instances.
```
