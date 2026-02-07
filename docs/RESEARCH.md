# ACE Music Platform — Research Documentation

> **Last Updated:** 2026-02-07
> **Phase:** 1 (Research & Infrastructure)
> **Status:** Complete

---

## Executive Summary

**For non-technical readers:** ACE-Step v1.5 is a free, open-source AI that generates music from text descriptions. It can create a full 4-minute song in under 2 seconds on professional hardware, supports over 2,000 musical styles and 50 languages, and produces 48kHz stereo audio comparable to commercial services like Suno. The software is MIT licensed, meaning we can use it commercially with no per-track fees — our only cost is renting GPU computing time (~$16 for 15,000 tracks vs ~$1,000 with Mureka). We can also fine-tune the AI to learn specific styles matching our brand requirements (hotel lobbies, spas, retail, etc.).

**Recommendation:** ACE-Step v1.5 is the best available open-source option for our use case. Proceed with cloud GPU testing to evaluate real-world quality across our genre matrix.

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Architecture](#architecture)
3. [Model Variants](#model-variants)
4. [Generation Capabilities](#generation-capabilities)
5. [REST API Server](#rest-api-server)
6. [Generation Parameters](#generation-parameters)
7. [LoRA Fine-Tuning](#lora-fine-tuning)
8. [Community UI Evaluation](#community-ui-evaluation)
9. [Cloud GPU Options](#cloud-gpu-options)
10. [Competitive Analysis](#competitive-analysis)
11. [Known Limitations](#known-limitations)
12. [Recommendations](#recommendations)

---

## System Requirements

| Requirement | Specification |
|-------------|--------------|
| Python | 3.11 (exact version required) |
| GPU | CUDA-capable, 4GB+ VRAM minimum |
| CUDA | 12.8 |
| PyTorch | 2.7.1 (Windows) / 2.10.0 (Linux) |
| Disk | ~20GB for models |
| Package Manager | uv (replaces pip) |
| OS | Windows 10+, Linux x86_64, macOS ARM64 |

### VRAM Tier Behavior (Auto-Detected)

| VRAM | Max Duration | Batch Size | LM Model |
|------|-------------|------------|----------|
| <6GB | 30s | 1 | Disabled |
| 6-8GB | 30s | 1 | 0.6B |
| 8-12GB | 60s | 2 | 0.6B-1.7B |
| 12-16GB | 120s | 4 | 1.7B |
| 16-24GB | 300s | 6 | 1.7B-4B |
| >24GB | 600s | 8 | 4B |

### Installation

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone https://github.com/ACE-Step/ACE-Step-1.5.git
cd ACE-Step-1.5
uv sync
```

First run triggers automatic model download (~10GB, 12-18 min at 100 Mbps).

---

## Architecture

ACE-Step v1.5 uses a hybrid two-component design:

### Language Model (LM) — "The Planner"
- Transforms text prompts into comprehensive song blueprints
- Chain-of-thought reasoning for metadata inference (BPM, key, structure)
- Generates 5Hz audio codes as semantic blueprint for the DiT
- Available sizes: 0.6B, 1.7B (recommended), 4B parameters
- Optional — can be disabled for lower VRAM or faster processing

### Diffusion Transformer (DiT) — "The Composer"
- Synthesizes audio from the LM's blueprint + text conditioning
- Iterative denoising process (8-100 steps depending on model variant)
- Uses 1D VAE for waveform-domain processing (not Mel-spectrogram)
- Advantage: eliminates phase loss, superior bass and percussion transients

### Generation Pipeline
1. Input Processing — parse captions, lyrics, metadata parameters
2. LM Processing (if enabled) — metadata inference, semantic code generation
3. DiT Processing — condition assembly, iterative diffusion denoising
4. VAE Decoding — latent space to 48kHz stereo audio waveform
5. Output — normalization, format conversion (MP3/WAV/FLAC), file saving

---

## Model Variants

### DiT Models (Audio Generation)

| Model | Steps | CFG Support | Speed | Quality | Best For |
|-------|-------|------------|-------|---------|----------|
| turbo (default) | 8 | No | Fastest | High | Daily production use |
| turbo-shift1 | 8 | No | Fastest | High | Texture-rich, detailed |
| turbo-shift3 | 8 | No | Fastest | High | Semantic clarity, clean |
| sft | 50 | Yes | Medium | Highest | Quality evaluation, fine control |
| base | 32-100 | Yes | Slow | High | Extract/lego/complete tasks |

**Shift variants explained:** The shift parameter controls how denoising effort is distributed across steps. Larger shift (shift3) = stronger semantic clarity. Smaller shift (shift1) = more texture detail. Default turbo uses shift=[1,2,3] for balanced output.

**Our recommendation:** Use **turbo** for production, **sft** for quality evaluation sessions.

### Language Models (Planning)

| Model | Parameters | VRAM | Knowledge Depth | Notes |
|-------|-----------|------|-----------------|-------|
| None | -- | 0 | -- | Speed priority, cover mode |
| 0.6B | 600M | ~2GB | Basic | Low VRAM systems |
| 1.7B | 1.7B | ~4GB | Medium | Recommended default |
| 4B | 4B | ~8GB | Rich | Professional workflows |

**Our recommendation:** Use **1.7B** for best balance of quality and VRAM usage.

---

## Generation Capabilities

### Speed Benchmarks

| GPU | Time per Song | Tracks per Hour |
|-----|--------------|-----------------|
| A100 (80GB) | <2 seconds | ~1,800 |
| RTX 4090 (24GB) | ~3-5 seconds | ~720-1,200 |
| RTX 3090 (24GB) | <10 seconds | ~360-600 |
| RTX 3060 (12GB) | ~30-40 seconds | ~90-120 |

### Output Specifications

| Spec | Value |
|------|-------|
| Sample Rate | 48kHz |
| Channels | Stereo |
| Formats | MP3, WAV, FLAC |
| Duration Range | 10-600 seconds |
| Batch Size | 1-8 simultaneous |

### Supported Content

- **Languages:** 50+ (strongest: English, Chinese, Japanese, Korean, Spanish, German, French)
- **Styles:** 2,000+ (any genre description works, common genres most reliable)
- **Instruments:** 1,000+ (fine-grained timbre descriptions supported)
- **Task Types:** text2music, cover, repaint, extract, lego, complete

### Quality Benchmarks (SongEval)

Quality positioning: between Suno v4.5 and Suno v5.

| Metric | ACE-Step v1.5 | Suno v5 |
|--------|--------------|---------|
| AudioBox CU Score | 8.09 | -- |
| AudioBox PQ Score | 8.35 | -- |
| Coherence | 4.72 | ~4.72 |
| Style Alignment | 35.4% | 46.8% |
| Lyric Adherence | 26.1% | 34.2% |

Style alignment and lyric adherence are weaker than top commercial models, but audio quality metrics are competitive.

---

## REST API Server

### Launch Commands

```bash
# Standalone API (port 8001)
uv run acestep-api

# Gradio UI + API (ports 7860 + 8001)
uv run acestep --enable-api

# With authentication
uv run acestep-api --api-key sk-your-secret-key

# With specific models
ACESTEP_CONFIG_PATH=acestep-v15-turbo ACESTEP_LM_MODEL_PATH=acestep-5Hz-lm-1.7B uv run acestep-api
```

**Critical constraint:** Must run with `workers=1` — the async job queue is in-memory and not shared across processes.

### Authentication

- Environment variable: `ACESTEP_API_KEY`
- Request header: `Authorization: Bearer <key>`
- Request body field: `ai_token`

### Endpoints

#### POST /release_task
Submit a music generation job.

**Request (JSON):**
```json
{
  "prompt": "ambient lounge jazz, soft piano",
  "lyrics": "",
  "audio_duration": 120,
  "bpm": 80,
  "key_scale": "C major",
  "time_signature": "4/4",
  "seed": -1,
  "batch_size": 1,
  "audio_format": "mp3",
  "task_type": "text2music",
  "vocal_language": "en",
  "thinking": false,
  "inference_steps": 8
}
```

**Response:** `{"task_id": "<uuid>", "status": "queued", "queue_position": 0}`

**Content-Types:** application/json, multipart/form-data, application/x-www-form-urlencoded

**Parameter aliases:** The API accepts both camelCase and snake_case (e.g., `audioDuration` / `audio_duration`, `caption` / `prompt`).

#### POST /query_result
Batch poll task status.

**Request:** `{"task_id_list": ["id1", "id2", "id3"]}`

**Response:**
```json
[
  {"task_id": "id1", "status": 1, "result": "/tmp/output_1.mp3"},
  {"task_id": "id2", "status": 0, "result": ""},
  {"task_id": "id3", "status": 2, "result": "error message"}
]
```

Status codes: `0` = queued/running, `1` = success, `2` = failed.

#### POST /format_input
LLM-enhanced caption/lyrics refinement.

**Request:** `{"prompt": "jazz music", "lyrics": "", "temperature": 0.85}`

**Response:** Enhanced prompt, formatted lyrics, inferred metadata.

#### GET /v1/models
List available DiT models (requires API key).

**Response:** `{"models": [{"name": "turbo", "is_default": true}], "default_model": "turbo"}`

#### GET /v1/audio?path=\<url-encoded-path\>
Download generated audio file. Returns audio/mpeg content.

#### GET /health
Health check.

**Response:** `{"status": "ok", "service": "acestep", "version": "1.5"}`

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| ACESTEP_CONFIG_PATH | acestep-v15-turbo | DiT model to load |
| ACESTEP_LM_MODEL_PATH | acestep-5Hz-lm-1.7B | Language model |
| ACESTEP_LM_BACKEND | vllm | LM runtime (vllm or pt) |
| ACESTEP_DEVICE | cuda | Compute device |
| ACESTEP_API_HOST | 0.0.0.0 | Bind address |
| ACESTEP_API_PORT | 8001 | API port |
| ACESTEP_API_KEY | (none) | Authentication key |
| ACESTEP_OUTPUT_DIR | ./outputs | Audio output directory |
| ACESTEP_QUEUE_WORKERS | 1 | Queue worker threads |
| ACESTEP_QUEUE_MAXSIZE | 200 | Max queue depth |
| ACESTEP_INIT_LLM | auto | LLM init (true/false/auto) |
| ACESTEP_DOWNLOAD_SOURCE | auto | Model source (huggingface/modelscope) |
| ACESTEP_CACHE_DIR | .cache/local_redis | Cache location |

### Queue Management

- Max queue size: 200 tasks (configurable)
- Completed jobs expire after 24 hours (auto-cleanup every 5 min)
- Task timeout: 3,600 seconds (1 hour)
- Results cached via diskcache (7-day expiration)

---

## Generation Parameters

### Core Parameters

| Parameter | Type | Default | Range | Notes |
|-----------|------|---------|-------|-------|
| prompt/caption | string | "" | free text | Style description |
| lyrics | string | "" | text | Use [verse]/[chorus]/[bridge] tags |
| audio_duration | float | varies | 10-600s | 30-240s most stable |
| bpm | int | auto | 30-280 | 60-180 most stable |
| key_scale | string | "" | e.g. "C major" | C,G,D,Am,Em most reliable |
| time_signature | string | "" | e.g. "4/4" | 4/4 most reliable |
| seed | int | -1 | any int | -1 for random |
| batch_size | int | 1 | 1-8 | Limited by VRAM tier |
| inference_steps | int | 8 | 1-100 | 8 for turbo, 50 for sft |
| guidance_scale | float | 7.0 | 1.0-15.0 | Only for sft/base models |
| task_type | string | "text2music" | see below | Generation mode |
| vocal_language | string | "en" | ISO code | 50+ supported |
| audio_format | string | "mp3" | mp3/wav/flac | Output format |

### Task Types

| Type | Description | Requires |
|------|-------------|----------|
| text2music | Generate from text description | prompt |
| cover | Maintain structure, change style | src_audio_path + prompt |
| repaint | Selective segment regeneration | src_audio_path + time range |
| extract | Separate stems/tracks | src_audio_path |
| lego | Recombine separated stems | extracted stems |
| complete | Auto-complete partial audio | src_audio_path |

### LM (Thinking Mode) Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| thinking | false | Enable LM code generation |
| use_format | false | LLM-enhance caption/lyrics |
| sample_mode | false | Auto-generate via LM |
| lm_temperature | 0.85 | LM sampling temperature |
| lm_cfg_scale | 2.5 | LM guidance scale |
| lm_top_p | 0.9 | Nucleus sampling |

### Guidance Notes

- **Turbo models** largely ignore guidance_scale — don't over-tune
- **SFT/base models** respond well to guidance_scale adjustments
- **BPM stability:** 60-180 is reliable; extreme values (30, 280) may drift
- **Key reliability:** C, G, D, Am, Em are most consistent; rare keys may shift
- **Duration sweet spots:** 30-60s and 2-4 minutes are most structurally coherent
- **Longer than 5 min:** May lose structural coherence

---

## LoRA Fine-Tuning

### Overview

LoRA (Low-Rank Adaptation) allows training lightweight style adapters on custom audio samples without modifying the base model. This is how we would create genre-specific models for our zone types.

### Three-Stage Process

**Stage 1: Dataset Building**
- Minimum: 5-20 high-quality audio files (10-100+ recommended)
- Supported formats: WAV, MP3, FLAC, OGG, Opus
- Duration per sample: 30-180 seconds recommended
- Auto-labeling via AI: captions, genre, BPM, key, time signature, lyrics, language
- Manual metadata editing available per-sample

**Stage 2: Preprocessing**
- One-time computation of VAE latents and text embeddings
- Pre-computes .pt tensor files for efficient training
- Generates manifest.json for the training data loader

**Stage 3: Training**
- Hardware: 12GB+ VRAM minimum (16GB+ recommended)
- Training time: ~1 hour on consumer GPU (RTX 3090)
- Fixed settings for turbo: shift=3.0, 8 inference steps, BFloat16
- Target modules: attention projections (q_proj, k_proj, v_proj, o_proj)

### LoRA Configuration

| Parameter | Range | Default | Notes |
|-----------|-------|---------|-------|
| Rank (r) | 32-128 | 64 | Higher = more capacity, larger file |
| Alpha | 64-256 | 128 | Usually 2x rank |
| Dropout | 0.0-0.2 | 0.0 | Regularization |
| Epochs | 200-1000 | 500 | Fewer for larger datasets |
| Output size | 10-100MB | ~50MB | Depends on rank |

### BMAsia Use Cases

| Zone Type | Training Approach | Sample Source |
|-----------|------------------|---------------|
| Hotel Lobby | Fine-tune on 20+ curated ambient/jazz tracks | Existing Mureka library |
| Fashion Retail | Fine-tune on 20+ upbeat pop/electronic tracks | Existing library |
| Spa/Wellness | Fine-tune on 20+ ambient/meditation tracks | Existing library |

### Deployment Strategy
- Train LoRA on base model (highest plasticity)
- Deploy with turbo model for speed
- Multiple LoRA adapters can be loaded simultaneously
- Hot-swap between adapters without restarting server

---

## Community UI Evaluation

### Project: ace-step-ui
- **Repository:** https://github.com/fspecii/ace-step-ui
- **Stack:** React 18, TypeScript, Express.js, SQLite, TailwindCSS
- **License:** MIT
- **Stars:** 385 (as of Feb 2026)
- **Status:** Very new (created Feb 2026)

### Features
- Spotify-like professional dark/light UI
- Preset/template management
- Batch generation (1-4 variations, 1-10 bulk jobs)
- Full audio player with waveform visualization
- Library management with likes and playlists
- AudioMass audio editor integration
- Demucs stem extraction
- Album art generation

### Critical Issues (Feb 2026)
- LLM integration failures ("Format failed. The LLM may not be available")
- Empty song generation on some installs
- Broken lyrics functionality
- Deprecated API arguments (`--lm-backend`, `--lm-model` removed from ACE-Step)
- Installation dependency resolution failures
- Multiple unresolved bugs in latest releases

### Verdict

**Do NOT adopt ace-step-ui for production.** It is too new and unstable. The API integration is fragile and several core features are broken. However, it is excellent design reference material for our own UI (Phase 4). Use it for UI/UX inspiration only.

---

## Cloud GPU Options

### Provider Comparison

| Factor | RunPod | Vast.ai |
|--------|--------|---------|
| RTX 3090 Cost | $0.44-0.69/hr | $0.30-0.50/hr |
| A100 Cost | $1.50-2.50/hr | $1.00-2.00/hr |
| Setup Ease | High (templates) | Medium |
| ACE-Step Template | Community | Official serverless |
| Persistence | Network Volumes | Disk storage |
| Billing Minimum | $10 | $5 |
| API | Yes | Yes |

### Docker Images Available

| Image | Description |
|-------|-------------|
| `valyriantech/ace-step-1.5` | API server with turbo model, production-ready |
| `thelocallab/ace-step` | Alternative community build |

### Recommended Setup

- **Testing (Phase 3):** RTX 3090 on RunPod (~$0.50/hr) — fastest to set up
- **Quality Evaluation:** RTX 3090 or 4090 on either provider
- **Production Batches:** A100 on Vast.ai (~$1.50/hr) — best value for large runs

### Cost Projections

| Scenario | GPU | Hours | Tracks | Cost | Per Track |
|----------|-----|-------|--------|------|-----------|
| First test | RTX 3090 | 0.5 | 20 | $0.35 | $0.018 |
| Quality eval | RTX 3090 | 2 | 200 | $1.40 | $0.007 |
| Small batch | A100 | 3 | 2,000 | $6.00 | $0.003 |
| Full catalog | A100 | 8 | 15,000 | $16.00 | $0.001 |
| **Mureka** | -- | -- | 15,000 | **$1,000** | **$0.057** |

**Self-hosted is 57x cheaper than Mureka for large batches.**

---

## Competitive Analysis

### Open-Source Music Generation Models

| Factor | ACE-Step v1.5 | MusicGen (Meta) | Stable Audio v2 |
|--------|--------------|-----------------|------------------|
| License | MIT | CC-BY-NC | Restricted |
| Commercial Use | Yes | No | Limited |
| Speed (A100) | <2s/song | ~30s/song | ~15s/song |
| Max Duration | 600s | 30s | 180s |
| Batch Generation | Up to 8 | Single | Single |
| LoRA Fine-tune | Yes | Limited | No |
| Style Control | 2000+ styles | Limited | Moderate |
| Lyrics/Vocals | Yes (50+ langs) | No | Limited |
| Self-Hosted | Yes | Yes | Yes |
| Community | 4.4K stars, active | Large, mature | Moderate |

### Why ACE-Step is the Best Choice

1. **MIT License** — Only major model with full commercial use rights
2. **Speed** — 10-120x faster than alternatives
3. **Duration** — Up to 10 minutes vs 30 seconds (MusicGen)
4. **LoRA** — Can fine-tune for our specific genre needs
5. **Batch** — Generate 8 tracks simultaneously
6. **Vocals** — Full vocal support in 50+ languages
7. **Cost** — No per-track fees, only GPU compute time
8. **Quality** — Comparable to Suno v4.5-v5 on benchmarks

### Comparison with Current Solution (Mureka)

| Factor | ACE-Step (self-hosted) | Mureka |
|--------|----------------------|--------|
| Per-track cost | ~$0.001-0.018 | ~$0.057 |
| 15K tracks cost | ~$16 | ~$1,000 |
| Style control | Full (prompt + LoRA) | Prompt only |
| Custom training | Yes (LoRA) | No |
| Dependency | Self-managed GPU | Third-party service |
| Quality | TBD (needs testing) | Known good |
| Setup complexity | High (initial) | Low |
| Ongoing effort | Moderate | Low |

---

## Known Limitations

### Output Quality
- **Inconsistent results** — Highly sensitive to random seeds; "gacha-style" quality variation
- **Style adherence ceiling** — Some genres/styles may not be accurately reproduced
- **Vocal synthesis** — Coarse compared to commercial models; lacks vocal nuance
- **Long-form coherence** — Tracks >5 minutes may lose structural integrity

### Genre-Specific Weaknesses
- Chinese rap and niche rap subgenres underperform
- Less common languages may produce lower quality due to training data imbalance
- Rare instruments may not render accurately
- Complex time signatures (5/4, 7/8) are unstable

### Editing Limitations
- Repainting/extend operations can produce unnatural transitions
- Only small lyric segments can be modified without distortion
- Multiple sequential edits degrade quality

### Technical Constraints
- LLM inference slows for audio >2 minutes
- API must run with workers=1 (no multi-process scaling)
- VRAM auto-detection may limit batch size unexpectedly
- First run requires 10GB+ model download

### Mitigation Strategies
- Generate multiple variations per prompt and select best (batch_size=4-8)
- Use turbo for production speed, sft for quality-critical evaluation
- Keep background music tracks to 2-4 minutes for best coherence
- Test thoroughly across our genre matrix before committing to production

---

## Recommendations

### Immediate Next Steps (Phase 2-3)

1. **Set up infrastructure** — Python environment, Docker config, launch scripts
2. **Rent cloud GPU** — Start with RTX 3090 on RunPod ($0.50/hr)
3. **Generate first test tracks** — 3-5 tracks across our key genres
4. **Evaluate quality** — Are the tracks "good enough" for our venues?

### If Quality is Sufficient (Phase 4-6)

5. **Build minimal platform UI** — Track generation, preview, tagging, export
6. **Create genre presets** — One per zone type from our genre matrix
7. **Run batch generation** — 100+ tracks for comprehensive quality evaluation
8. **A/B test vs Mureka** — Blind comparison with team
9. **LoRA fine-tuning** — Train genre-specific adapters from our best Mureka tracks
10. **Production deployment** — A100 on Vast.ai for cost-effective batch generation

### Decision Point

After Phase 3 (first test tracks), we need to make a go/no-go decision:
- **GO:** Quality meets our venue standards → proceed to Phase 4
- **NO-GO:** Quality insufficient → evaluate LoRA fine-tuning potential, or abandon
- **PARTIAL:** Quality good for some genres only → build for those, keep Mureka for others

### Cost-Benefit Summary

| Approach | Annual Cost (est.) | Quality | Control | Effort |
|----------|-------------------|---------|---------|--------|
| Mureka only | ~$4,000-8,000 | Proven | Low | Low |
| ACE-Step only | ~$200-500 | TBD | High | High (initial) |
| Hybrid | ~$2,000-4,000 | Best of both | Medium | Medium |
