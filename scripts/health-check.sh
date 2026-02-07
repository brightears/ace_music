#!/usr/bin/env bash
# =============================================================================
# ACE Music — Health Check
# Verify the ACE-Step API server is running and responsive
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Load .env if present
if [ -f "$PROJECT_DIR/.env" ]; then
    set -a; source "$PROJECT_DIR/.env"; set +a
fi

API_URL="${ACESTEP_API_URL:-http://localhost:8001}"
API_KEY="${ACESTEP_API_KEY:-}"

log() { echo "[$(date '+%H:%M:%S')] $*"; }
ok()  { echo "[$(date '+%H:%M:%S')] OK: $*"; }
fail() { echo "[$(date '+%H:%M:%S')] FAIL: $*" >&2; }

AUTH_HEADER=""
if [ -n "$API_KEY" ]; then
    AUTH_HEADER="-H \"Authorization: Bearer $API_KEY\""
fi

PASSED=0
FAILED=0

# Test 1: Health endpoint
log "Checking $API_URL/health ..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$API_URL/health" 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    ok "/health returned 200"
    HEALTH=$(curl -s --max-time 10 "$API_URL/health" 2>/dev/null)
    log "  Response: $HEALTH"
    PASSED=$((PASSED + 1))
else
    fail "/health returned $HTTP_CODE (expected 200)"
    if [ "$HTTP_CODE" = "000" ]; then
        fail "  Connection refused. Is the server running at $API_URL?"
    fi
    FAILED=$((FAILED + 1))
fi

# Test 2: Models endpoint
log "Checking $API_URL/v1/models ..."
if [ -n "$API_KEY" ]; then
    MODELS_RESP=$(curl -s --max-time 10 -H "Authorization: Bearer $API_KEY" "$API_URL/v1/models" 2>/dev/null || echo "")
else
    MODELS_RESP=$(curl -s --max-time 10 "$API_URL/v1/models" 2>/dev/null || echo "")
fi

if [ -n "$MODELS_RESP" ] && echo "$MODELS_RESP" | python3 -c "import sys,json; json.load(sys.stdin)" 2>/dev/null; then
    ok "/v1/models returned valid JSON"
    log "  Response: $MODELS_RESP"
    PASSED=$((PASSED + 1))
else
    fail "/v1/models failed or returned invalid response"
    FAILED=$((FAILED + 1))
fi

# Summary
log ""
log "=== Health Check Summary ==="
log "API URL: $API_URL"
log "Passed: $PASSED / $((PASSED + FAILED))"

if [ "$FAILED" -gt 0 ]; then
    fail "$FAILED check(s) failed"
    exit 1
else
    ok "All checks passed"
fi
