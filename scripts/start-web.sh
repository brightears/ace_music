#!/usr/bin/env bash
# =============================================================================
# ACE Music — Start Web UI
# Launches the FastAPI web interface for music generation and library management
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

log() { echo "[$(date '+%H:%M:%S')] $*"; }

# Load .env if present
if [ -f "$PROJECT_DIR/.env" ]; then
    set -a; source "$PROJECT_DIR/.env"; set +a
fi

HOST="${WEB_HOST:-127.0.0.1}"
PORT="${WEB_PORT:-8000}"
RELOAD="${WEB_RELOAD:-false}"

CMD="python3 -m uvicorn src.web.app:app --host $HOST --port $PORT"

if [ "$RELOAD" = "true" ]; then
    CMD="$CMD --reload"
fi

cd "$PROJECT_DIR"
log "Starting ACE Music Web UI..."
log "  URL: http://$HOST:$PORT"
log "  Reload: $RELOAD"
log ""
exec $CMD
