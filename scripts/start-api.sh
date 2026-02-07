#!/usr/bin/env bash
# =============================================================================
# ACE Music — Start ACE-Step API Server
# Loads config from .env and launches the REST API on port 8001
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ACESTEP_DIR="${ACESTEP_DIR:-/workspace/ACE-Step-1.5}"

log() { echo "[$(date '+%H:%M:%S')] $*"; }

# Load .env if present
if [ -f "$PROJECT_DIR/.env" ]; then
    log "Loading config from $PROJECT_DIR/.env"
    set -a
    source "$PROJECT_DIR/.env"
    set +a
elif [ -f "$ACESTEP_DIR/.env" ]; then
    log "Loading config from $ACESTEP_DIR/.env"
    set -a
    source "$ACESTEP_DIR/.env"
    set +a
fi

# Defaults
HOST="${ACESTEP_API_HOST:-0.0.0.0}"
PORT="${ACESTEP_API_PORT:-8001}"
API_KEY="${ACESTEP_API_KEY:-}"
INIT_LLM="${ACESTEP_INIT_LLM:-auto}"
LM_MODEL="${ACESTEP_LM_MODEL_PATH:-}"

# Build command
CMD="uv run acestep-api --host $HOST --port $PORT"

if [ -n "$API_KEY" ]; then
    CMD="$CMD --api-key $API_KEY"
fi

if [ "$INIT_LLM" = "true" ]; then
    CMD="$CMD --init-llm"
fi

if [ -n "$LM_MODEL" ]; then
    CMD="$CMD --lm-model-path $LM_MODEL"
fi

# Launch
cd "$ACESTEP_DIR"
log "Starting ACE-Step API server..."
log "  Host: $HOST"
log "  Port: $PORT"
log "  API Key: ${API_KEY:+set}${API_KEY:-not set}"
log "  Init LLM: $INIT_LLM"
log "  URL: http://$HOST:$PORT"
log ""
exec $CMD
