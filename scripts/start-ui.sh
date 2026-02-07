#!/usr/bin/env bash
# =============================================================================
# ACE Music — Start ACE-Step Gradio UI
# Launches the web UI for manual exploration and testing
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ACESTEP_DIR="${ACESTEP_DIR:-/workspace/ACE-Step-1.5}"

log() { echo "[$(date '+%H:%M:%S')] $*"; }

# Load .env if present
if [ -f "$PROJECT_DIR/.env" ]; then
    set -a; source "$PROJECT_DIR/.env"; set +a
fi

HOST="${ACESTEP_UI_HOST:-0.0.0.0}"
PORT="${ACESTEP_UI_PORT:-7860}"
ENABLE_API="${ACESTEP_UI_ENABLE_API:-false}"

CMD="uv run acestep --server-name $HOST --port $PORT --init_service true"

if [ "$ENABLE_API" = "true" ]; then
    CMD="$CMD --enable-api"
    API_KEY="${ACESTEP_API_KEY:-}"
    if [ -n "$API_KEY" ]; then
        CMD="$CMD --api-key $API_KEY"
    fi
fi

cd "$ACESTEP_DIR"
log "Starting ACE-Step Gradio UI..."
log "  URL: http://$HOST:$PORT"
log "  API enabled: $ENABLE_API"
log ""
exec $CMD
