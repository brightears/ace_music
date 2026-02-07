# ACE Music Platform

## Project Overview

BMAsia Group internal music creation platform for generating background music across 2,100+ zones in Asia-Pacific (hotels, restaurants, fashion retail, QSR chains). Built on ACE-Step v1.5, an open-source AI music generation model.

**Goal:** Evaluate ACE-Step as a replacement for Mureka (~$1,000 per 15-20K tracks). If quality is sufficient, build a self-hosted generation pipeline. This is a test/evaluation project — build flexible, easy to abandon if needed.

**Current services:** Soundtrack Your Brand + Beat Breeze (our own platform).

## Technical Stack

- **AI Model:** ACE-Step v1.5 (MIT License, commercial use OK)
- **Runtime:** Python 3.11, CUDA 12.8, PyTorch 2.7+
- **Package Manager:** uv
- **API Server:** ACE-Step built-in REST API (port 8001)
- **Deployment:** Docker on cloud GPU (RunPod / Vast.ai)
- **Platform UI:** FastAPI + Jinja2 + HTMX + SQLite (custom-built, NOT ace-step-ui)
- **CSS Framework:** Pico CSS (classless, from CDN)

## Key Technical Decisions

1. **Turbo model for production** — 8-step inference, <2s on A100, good quality
2. **1.7B language model** — Best quality/VRAM balance for 12-16GB cards
3. **Docker deployment** — Reproducible, uses `valyriantech/ace-step-1.5` image
4. **Cloud GPU (RunPod)** — RTX 3090 for testing, A100 for production batches
5. **REST API integration** — Programmatic access, not Gradio UI
6. **Build our own UI** — ace-step-ui too new/buggy (Feb 2026), build minimal internal tool
7. **LoRA fine-tuning** — For genre-specific customization (hotel lobby, spa, retail styles)

## API Quick Reference

```
POST /release_task        — Submit generation job → returns task_id
POST /query_result        — Poll task status (batch) → status 0/1/2
POST /format_input        — LLM-enhance caption/lyrics
GET  /v1/models           — List available DiT models
GET  /v1/audio?path=<p>   — Download generated audio file
GET  /health              — Health check
```

Auth: `Authorization: Bearer <ACESTEP_API_KEY>` header or `ai_token` body field.

## Build & Run

### ACE-Step (on GPU server)
```bash
# Install
git clone https://github.com/ACE-Step/ACE-Step-1.5.git
cd ACE-Step-1.5
uv sync

# Launch API server
uv run acestep-api

# Launch Gradio UI
uv run acestep

# Launch both
uv run acestep --enable-api
```

### Docker
```bash
docker compose up -d
# API at http://localhost:8001
# UI at http://localhost:7860
```

### Local Python Client
```bash
uv sync                                 # Install dependencies
python scripts/test-connection.py       # Test API connectivity
python scripts/test-generate.py         # Generate a test track
```

### Web UI (local)
```bash
bash scripts/start-web.sh              # Start web UI at http://127.0.0.1:8000
# Or directly: python3 -m uvicorn src.web.app:app --port 8000
```

## File Structure

```
ACE Music/
├── CLAUDE.md                # This file
├── pyproject.toml           # Python project config (httpx, pydantic, etc.)
├── docker-compose.yml       # Docker deployment using valyriantech image
├── .gitignore
├── .env.example
├── .claude/
│   ├── agents/              # Subagent definitions
│   │   ├── researcher.md    # Read-only research (Haiku)
│   │   ├── code-writer.md   # Implementation (Sonnet)
│   │   ├── doc-writer.md    # Documentation (Sonnet)
│   │   └── quality-checker.md # Code review (Sonnet)
│   └── skills/              # Slash command skills
│       ├── generate-track.md
│       ├── batch-generate.md
│       ├── setup-cloud.md
│       ├── test-quality.md
│       └── deploy.md
├── configs/                 # Deployment-specific .env templates
│   ├── local-dev.env
│   ├── cloud-runpod.env
│   └── cloud-vastai.env
├── docs/
│   ├── RESEARCH.md          # Comprehensive research findings
│   ├── SETUP.md             # Setup guide (3 deployment paths)
│   └── GPU_SETUP.md         # Cloud GPU provider guide + cost estimates
├── scripts/
│   ├── setup-gpu-server.sh  # Full GPU server setup from scratch
│   ├── start-api.sh         # Launch ACE-Step API server
│   ├── start-ui.sh          # Launch Gradio web UI (on GPU server)
│   ├── start-web.sh         # Launch FastAPI web UI (local)
│   ├── download-models.sh   # Pre-download model files
│   ├── health-check.sh      # Verify API server health
│   ├── test-connection.py   # Test API connectivity
│   └── test-generate.py     # Generate a test track
├── src/
│   ├── __init__.py
│   ├── ace_client.py        # Async Python client for ACE-Step API
│   ├── config.py            # Pydantic settings management
│   ├── web/                 # FastAPI web UI (Phase 4)
│   │   ├── app.py           # FastAPI app, lifespan, static mounts
│   │   ├── routes.py        # HTTP endpoints (pages, API, partials)
│   │   ├── database.py      # SQLAlchemy Track model, sessions
│   │   └── generation.py    # Generation orchestration, background tasks
│   └── templates/           # Jinja2 templates (Phase 4)
│       ├── base.html        # Layout (Pico CSS + HTMX from CDN)
│       ├── generate.html    # Generation form (14 params)
│       ├── library.html     # Track library with search
│       ├── partials/        # HTMX partials (track_row, progress, result, error)
│       └── static/styles.css
├── data/                    # SQLite database (auto-created)
├── outputs/                 # Generated audio files
├── tests/                   # Test suite (Phase 6)
└── presets/                 # Generation preset files (Phase 5)
```

## Key Links

- ACE-Step v1.5: https://github.com/ace-step/ACE-Step-1.5
- DeepWiki Docs: https://deepwiki.com/ace-step/ACE-Step-1.5
- HuggingFace: https://huggingface.co/ACE-Step/Ace-Step1.5
- Docker Image: https://hub.docker.com/r/valyriantech/ace-step-1.5
- Community UI (reference): https://github.com/fspecii/ace-step-ui
- Our Repo: https://github.com/brightears/ace_music

## Project Phases

- [x] Phase 1: Research & Infrastructure (CLAUDE.md, agents, skills, RESEARCH.md)
- [x] Phase 2: Infrastructure Setup (scripts, client library, Docker, configs)
- [x] Phase 3: Cloud GPU Setup (GPU_SETUP.md, provider comparison, cost estimates)
- [x] Phase 4: Music Creation Platform (FastAPI + HTMX web UI, SQLite, track management)
- [ ] Phase 5: Batch Generation Pipeline (CSV/JSON presets, thousands of tracks)
- [ ] Phase 6: Testing & Quality Plan (genre matrix, A/B vs Mureka)

## Rules

- No GPU available locally — mark GPU-dependent steps with "GPU REQUIRED"
- Keep docs clear for non-technical readers (summaries accessible, technical detail in guides)
- Commit to repo at end of each phase
- Use subagents for research, keep main context for decisions
- Environment variables for ALL configuration — never hardcode secrets
- Python type hints on all function signatures
- Async/await for API interactions

## Compaction Instructions

When compacting, always preserve:
- Current phase status and objectives
- Key technical decisions (7 items above)
- API endpoint signatures
- Environment variable names
- File being actively worked on
- Any errors or blockers encountered

Safe to drop:
- Research history already documented in docs/RESEARCH.md
- Decision rationale already captured in this file
- Verbose tool output from completed steps
