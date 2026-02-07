#!/usr/bin/env bash
# =============================================================================
# ACE Music — GPU Server Setup
# One-shot setup for a fresh Ubuntu/CUDA machine (RunPod, Vast.ai, bare metal)
# =============================================================================
set -euo pipefail

ACESTEP_DIR="${ACESTEP_DIR:-/workspace/ACE-Step-1.5}"
ACESTEP_BRANCH="${ACESTEP_BRANCH:-main}"
MODEL="${ACESTEP_CONFIG_PATH:-acestep-v15-turbo}"
LM_MODEL="${ACESTEP_LM_MODEL_PATH:-acestep-5Hz-lm-1.7B}"

log() { echo "[$(date '+%H:%M:%S')] $*"; }
err() { echo "[$(date '+%H:%M:%S')] ERROR: $*" >&2; }

# ---------------------------------------------------------------------------
log "=== ACE-Step GPU Server Setup ==="
log "Install dir: $ACESTEP_DIR"

# 1. System check
log "Checking prerequisites..."

if ! command -v nvidia-smi &>/dev/null; then
    err "nvidia-smi not found. NVIDIA drivers required."
    err "Install: https://docs.nvidia.com/datacenter/tesla/driver-installation-guide/"
    exit 1
fi

GPU_INFO=$(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits 2>/dev/null || true)
if [ -z "$GPU_INFO" ]; then
    err "No GPU detected. This script requires a CUDA-capable GPU."
    exit 1
fi
log "GPU detected: $GPU_INFO"

PYTHON_VERSION=$(python3 --version 2>/dev/null | grep -oP '\d+\.\d+' || echo "none")
if [[ "$PYTHON_VERSION" != "3.11" ]]; then
    log "Python 3.11 required (found: $PYTHON_VERSION). Installing..."
    if command -v apt-get &>/dev/null; then
        apt-get update -qq && apt-get install -y -qq python3.11 python3.11-venv python3.11-dev 2>/dev/null || {
            err "Could not install Python 3.11 via apt. Install manually."
            exit 1
        }
    else
        err "Python 3.11 required but not found. Install manually."
        exit 1
    fi
fi

# 2. Install uv
if ! command -v uv &>/dev/null; then
    log "Installing uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi
log "uv version: $(uv --version)"

# 3. Clone ACE-Step
if [ -d "$ACESTEP_DIR" ]; then
    log "ACE-Step directory exists, pulling latest..."
    cd "$ACESTEP_DIR"
    git pull origin "$ACESTEP_BRANCH" 2>/dev/null || log "Pull failed, using existing"
else
    log "Cloning ACE-Step v1.5..."
    git clone --branch "$ACESTEP_BRANCH" https://github.com/ACE-Step/ACE-Step-1.5.git "$ACESTEP_DIR"
    cd "$ACESTEP_DIR"
fi

# 4. Install dependencies
log "Installing Python dependencies (this may take a few minutes)..."
uv sync

# 5. Download models
log "Downloading models (this may take 10-20 minutes on first run)..."
uv run acestep-download || {
    log "acestep-download failed, models will download on first launch"
}

# 6. Summary
log "=== Setup Complete ==="
log "ACE-Step installed at: $ACESTEP_DIR"
log "To start the API server:"
log "  cd $ACESTEP_DIR && uv run acestep-api --host 0.0.0.0 --port 8001"
log "To start the Gradio UI:"
log "  cd $ACESTEP_DIR && uv run acestep --server-name 0.0.0.0 --port 7860"
