---
name: setup-cloud
description: Deploy ACE-Step on a cloud GPU — RunPod (fastest setup), Vast.ai (cheapest), or TensorDock (budget)
user_invocable: true
---

# /setup-cloud

Deploy ACE-Step on a cloud GPU and generate your first track.

**Full guide:** See `docs/GPU_SETUP.md` for provider comparison, cost estimates, persistence, scaling, and troubleshooting.

## Usage
```
/setup-cloud                    # Guided setup (defaults to RunPod)
/setup-cloud --provider runpod  # RunPod-specific
/setup-cloud --provider vastai  # Vast.ai-specific
```

## Fastest Path to First Track (~15 min, <$1)

### 1. Deploy on RunPod
- Account: https://runpod.io ($10 minimum credit)
- Deploy Pod: Image `valyriantech/ace-step-1.5`, GPU RTX 3090
- Expose HTTP ports: `8001,7860`
- Set env: `ACESTEP_API_KEY=sk-your-test-key`
- Wait 2-5 min for startup (models are baked into the Docker image)

### 2. Get Your API URL
- RunPod format: `https://<POD_ID>-8001.proxy.runpod.net`
- If 8001 doesn't respond, try 8000 (ValyrianTech image uses 8000 internally)
- Test: `curl https://<POD_ID>-8001.proxy.runpod.net/health`

### 3. Connect from Your Laptop
```bash
cp configs/cloud-runpod.env .env
# Edit .env: set ACESTEP_API_URL and ACESTEP_API_KEY
python scripts/test-connection.py
python scripts/test-generate.py
```

## Cost Quick Reference

| Session | GPU | Time | Tracks | Cost |
|---------|-----|------|--------|------|
| Quick test | RTX 3090 | 30 min | 20 | ~$0.10-0.35 |
| Quality eval | RTX 3090 | 2 hrs | 300 | ~$0.40-0.92 |
| Full catalog | A100 80GB | 8 hrs | 15,000 | ~$10-20 |

**vs Mureka: 15,000 tracks = ~$1,000. Self-hosted = ~$10-20.**

## Provider Recommendations

| Scenario | Provider | GPU | Cost/hr |
|----------|----------|-----|---------|
| First test | **RunPod** | RTX 3090 | $0.20-0.46 |
| Long sessions | **Vast.ai** | RTX 3090 | $0.15-0.40 |
| Large batches | **Vast.ai** | A100 80GB | $0.80-1.50 |
| Budget | TensorDock | RTX 3090 | $0.09-0.40 |

## Shutdown Checklist
- [ ] Download outputs you want to keep
- [ ] Stop/terminate instance in provider dashboard
- [ ] Verify no active instances on billing page
- [ ] Stopped instances may still incur storage charges — destroy if fully done

## GPU REQUIRED
This skill deploys to a cloud GPU. Have a credit card and ~$10 ready.
