---
name: deploy
description: Launch the full ACE Music platform (API server + web UI)
user_invocable: true
---

# /deploy

Orchestrate full platform deployment for ACE Music.

## Usage
```
/deploy                      # Full deployment with checks
/deploy --check-only         # Pre-flight checks only
/deploy --skip-validation    # Skip test generation step
```

## Deployment Stages

### Stage 1: Pre-flight Checks
- [ ] `.env` file exists with all required variables
- [ ] `ACESTEP_API_URL` is set and reachable (`/health` returns OK)
- [ ] `ACESTEP_API_KEY` is set and non-empty
- [ ] API authentication works (`/v1/models` returns model list)
- [ ] Output directory exists and is writable
- [ ] SQLite database is initialized (if platform UI is deployed)

### Stage 2: Verify ACE-Step Server
- [ ] Correct model loaded (check `/v1/models` response)
- [ ] LM model available if thinking mode needed
- [ ] Queue is accepting tasks (submit and cancel a test task)
- [ ] VRAM tier detected correctly for batch size limits

### Stage 3: Validation (unless --skip-validation)
- [ ] Generate 3 test tracks (one per genre: ambient, jazz, pop)
- [ ] All 3 complete within 60 seconds
- [ ] Audio files download successfully and are non-empty
- [ ] Run basic quality checks (duration accuracy, no silence)

### Stage 4: Platform UI (if applicable)
- [ ] Web server starts on `APP_PORT`
- [ ] Can access UI in browser
- [ ] Database migrations applied
- [ ] Can create/load generation presets
- [ ] Audio playback works in browser

### Stage 5: Operational Readiness
- [ ] Log output visible and at correct level
- [ ] Cost tracking: document GPU cost/hour for current instance
- [ ] Document endpoint URL for team access
- [ ] Confirm shutdown procedure is understood

## Quick Deploy (Minimal)

For just getting ACE-Step API running (no platform UI):

```bash
# 1. Ensure cloud GPU is running (see /setup-cloud)
# 2. Verify connection
curl -H "Authorization: Bearer $ACESTEP_API_KEY" $ACESTEP_API_URL/health

# 3. Test generation
curl -X POST $ACESTEP_API_URL/release_task \
  -H "Authorization: Bearer $ACESTEP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "ambient lounge music", "audio_duration": 30}'
```

## Rollback
If any stage fails:
1. Log the failure point and error message
2. Do NOT tear down existing working infrastructure
3. Report what succeeded and what failed
4. Provide manual remediation steps
5. If cloud GPU issue: check provider dashboard for instance status

## GPU REQUIRED
Full deployment requires a running cloud GPU instance. Use `/setup-cloud` to provision one first.
