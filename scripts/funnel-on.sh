#!/usr/bin/env bash
#
# funnel-on.sh — Enable Tailscale Funnel for the Office Hours Intake Bot.
#
# Called by Claude Code's SessionStart hook (startup, resume).
# Idempotent: no-ops if Funnel is already active.
# Uses /usr/local/bin/tailscale (macOS app CLI) to avoid Nix version warning.

set -euo pipefail

TAILSCALE=/usr/local/bin/tailscale
PORT=8443
BACKEND=8000

# Guard: check current state before calling tailscale.
FUNNEL_STATUS="$("$TAILSCALE" funnel status 2>/dev/null || true)"
if printf '%s' "$FUNNEL_STATUS" | grep -q "Funnel on"; then
    exit 0  # already active
fi

"$TAILSCALE" funnel --bg --https "$PORT" --yes "$BACKEND" 2>/dev/null
printf 'Tailscale Funnel enabled: https://mac-minicore.gerbil-matrix.ts.net:%s/\n' "$PORT"
