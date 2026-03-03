#!/usr/bin/env bash
#
# funnel-off.sh — Disable Tailscale Funnel for the Office Hours Intake Bot.
#
# Called by Claude Code's SessionEnd hook.
# Exits silently on "clear" (session immediately restarts; no point disabling).
# Idempotent: no-ops if Funnel is already off.

set -euo pipefail

TAILSCALE=/usr/local/bin/tailscale
PORT=8443

# Read SessionEnd reason from stdin JSON.
# jq is managed by home-manager and available in PATH.
if [ -t 0 ]; then
    REASON="manual"
else
    REASON="$(cat - | jq -r '.reason // "unknown"')"
fi

case "$REASON" in
    logout|prompt_input_exit|manual)
        ;;   # proceed to disable
    *)
        exit 0   # clear/compact/unknown: leave Funnel alone
        ;;
esac

# Guard: check current state before calling tailscale.
FUNNEL_STATUS="$("$TAILSCALE" funnel status 2>/dev/null || true)"
if ! printf '%s' "$FUNNEL_STATUS" | grep -q "Funnel on"; then
    exit 0  # already off
fi

"$TAILSCALE" funnel --https="$PORT" off 2>/dev/null
printf 'Tailscale Funnel disabled on port %s\n' "$PORT"
