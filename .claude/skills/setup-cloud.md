---
name: setup-cloud
description: Step-by-step guide for deploying ACE-Step on a cloud GPU (RunPod/Vast.ai)
user_invocable: true
---

# /setup-cloud

Interactive deployment guide for getting ACE-Step running on a cloud GPU.

## Usage
```
/setup-cloud                    # Full guided setup
/setup-cloud --provider runpod  # RunPod-specific
/setup-cloud --provider vastai  # Vast.ai-specific
```

## Quick Start (Fastest Path to First Track)

**Estimated time: 15-30 minutes. Estimated cost: $0.50-2.00 for a test session.**

### Option A: RunPod (Recommended for First Test)

1. Create account at https://runpod.io
2. Add billing ($10 minimum, pay-as-you-go)
3. Deploy a GPU Pod:
   - Template: Custom Docker image
   - Image: `valyriantech/ace-step-1.5`
   - GPU: RTX 3090 (24GB) — ~$0.44/hr community, ~$0.69/hr secure
   - Volume: 30GB (for model cache)
   - Expose HTTP port: 8001
   - Environment vars:
     ```
     ACESTEP_API_KEY=sk-your-test-key
     ACESTEP_CONFIG_PATH=acestep-v15-turbo
     ACESTEP_LM_MODEL_PATH=acestep-5Hz-lm-1.7B
     ```
4. Wait for pod startup + model download (~5-15 min first time)
5. Access API at: `https://<pod-id>-8001.proxy.runpod.net`
6. Test: `curl https://<pod-id>-8001.proxy.runpod.net/health`
7. Update your `.env`:
   ```
   ACESTEP_API_URL=https://<pod-id>-8001.proxy.runpod.net
   ACESTEP_API_KEY=sk-your-test-key
   ```
8. Run `/generate-track` to create your first track

### Option B: Vast.ai (Cheaper for Longer Sessions)

1. Create account at https://vast.ai
2. Add billing (minimum $5)
3. Search instances: Filter for RTX 3090 or A100, Docker capable
4. Select "ACE-Step" template if available, or use custom Docker:
   - Image: `valyriantech/ace-step-1.5`
   - Ports: 8001
5. Configure environment variables (same as RunPod above)
6. Launch and wait for model download
7. Test health endpoint and update `.env`

## GPU Recommendations

| Use Case | GPU | VRAM | Approx. Cost/hr | Speed |
|----------|-----|------|-----------------|-------|
| Quick test (10-20 tracks) | RTX 3090 | 24GB | $0.44-0.69 | ~6s/track |
| Quality eval (100+ tracks) | RTX 4090 | 24GB | $0.55-0.89 | ~4s/track |
| Batch generation (5K+ tracks) | A100 | 80GB | $1.50-2.50 | ~2s/track |

## Cost Estimates

| Session Type | GPU | Duration | Tracks | Est. Cost |
|-------------|-----|----------|--------|-----------|
| Quick test | RTX 3090 | 30 min | 20 | ~$0.35 |
| Quality eval | RTX 3090 | 2 hours | 200 | ~$1.40 |
| Small batch | A100 | 3 hours | 2,000 | ~$6.00 |
| Full catalog | A100 | 8 hours | 15,000 | ~$16.00 |

**Compare: Mureka for 15,000 tracks = ~$1,000. Self-hosted = ~$16.**

## Persistence (Don't Reinstall Every Time)

### RunPod
- Use **Network Volumes** to persist model checkpoints between sessions
- Create a volume, mount at `/app/checkpoints`
- First session downloads models to volume; subsequent sessions skip download

### Vast.ai
- Use **disk storage** option when creating instance
- Models persist on instance disk while instance exists (even when stopped)
- "Stop" instance instead of "destroy" to keep state

## Shutdown Checklist
- [ ] Download any generated audio you want to keep
- [ ] Stop (don't destroy) instance if you want to resume later
- [ ] Destroy instance if done — stops all charges
- [ ] Verify billing dashboard shows no active instances

## Troubleshooting

| Problem | Solution |
|---------|----------|
| /health not responding | Wait 5-15 min for model download on first launch |
| Out of memory | Use turbo model, disable LLM (ACESTEP_INIT_LLM=false) |
| Slow generation | Check GPU utilization, ensure CUDA is being used |
| Connection refused | Check port exposure settings in cloud provider |
| Authentication failed | Verify ACESTEP_API_KEY matches between server and client |
