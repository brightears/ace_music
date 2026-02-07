#!/usr/bin/env bash
# =============================================================================
# ACE Music — Download ACE-Step Models
# Pre-download model files to avoid blocking on first generation
# =============================================================================
set -euo pipefail

ACESTEP_DIR="${ACESTEP_DIR:-/workspace/ACE-Step-1.5}"
CHECKPOINTS_DIR="${ACESTEP_CHECKPOINTS_DIR:-$ACESTEP_DIR/checkpoints}"

log() { echo "[$(date '+%H:%M:%S')] $*"; }

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Download ACE-Step model files.

Options:
  --list          List available models
  --all           Download all models
  --model NAME    Download a specific model
  --dir PATH      Custom checkpoints directory (default: $CHECKPOINTS_DIR)
  --force         Force re-download even if exists
  -h, --help      Show this help

Models:
  acestep-v15-turbo       DiT turbo (default, 8-step, fastest)
  acestep-v15-sft         DiT SFT (50-step, highest quality)
  acestep-v15-base        DiT base (for extract/lego/complete)
  acestep-5Hz-lm-0.6B    Language model 0.6B (lightweight)
  acestep-5Hz-lm-1.7B    Language model 1.7B (recommended)
  acestep-5Hz-lm-4B      Language model 4B (highest quality)

Examples:
  $(basename "$0") --list
  $(basename "$0")                    # Download default (turbo + 1.7B LM)
  $(basename "$0") --model acestep-v15-sft
  $(basename "$0") --all
EOF
    exit 0
}

# Parse args
ACTION="default"
MODEL=""
FORCE=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --list) ACTION="list"; shift ;;
        --all) ACTION="all"; shift ;;
        --model) MODEL="$2"; ACTION="specific"; shift 2 ;;
        --dir) CHECKPOINTS_DIR="$2"; shift 2 ;;
        --force) FORCE="--force"; shift ;;
        -h|--help) usage ;;
        *) err "Unknown option: $1"; usage ;;
    esac
done

cd "$ACESTEP_DIR"

case "$ACTION" in
    list)
        log "Available models:"
        uv run acestep-download --list
        ;;
    all)
        log "Downloading ALL models to $CHECKPOINTS_DIR..."
        uv run acestep-download --all --dir "$CHECKPOINTS_DIR" $FORCE
        ;;
    specific)
        log "Downloading model: $MODEL"
        uv run acestep-download --model "$MODEL" --dir "$CHECKPOINTS_DIR" $FORCE
        ;;
    default)
        log "Downloading default models (turbo + 1.7B LM)..."
        uv run acestep-download --dir "$CHECKPOINTS_DIR" $FORCE
        ;;
esac

log "Done. Models stored in: $CHECKPOINTS_DIR"
