#!/usr/bin/env bash
# News Brief setup checker. Run after install to find what's missing before your first brief.
#   ./scripts/doctor.sh
# Exits non-zero if anything REQUIRED for your chosen delivery is broken.

CFG="$HOME/.config/news-brief"
OK=0
WARN=0
FAIL=0

pass() { printf '  \033[32m✓\033[0m %s\n' "$1"; OK=$((OK+1)); }
warn() { printf '  \033[33m!\033[0m %s\n' "$1"; WARN=$((WARN+1)); }
fail() { printf '  \033[31m✗\033[0m %s\n' "$1"; FAIL=$((FAIL+1)); }

# Read the delivery mode (lark|email|file) from settings.json, if present.
DELIVERY=""
if [ -f "$CFG/settings.json" ]; then
  DELIVERY=$(grep -o '"delivery"[[:space:]]*:[[:space:]]*"[^"]*"' "$CFG/settings.json" 2>/dev/null | sed 's/.*"\([^"]*\)"[[:space:]]*$/\1/')
fi

echo "News Brief — setup check"
echo

echo "Core:"
if command -v claude >/dev/null 2>&1; then pass "claude CLI found ($(command -v claude))"; else fail "claude CLI not on PATH — install Claude Code"; fi

echo
echo "Config (~/.config/news-brief):"
if [ -f "$CFG/profile.md" ]; then pass "profile.md exists (your reader profile)"; else warn "profile.md missing — run /news-brief once to build it (onboarding)"; fi
if [ -f "$CFG/sources.json" ]; then pass "sources.json exists"; else warn "sources.json missing — copy config/sources.example.json or let onboarding seed it"; fi
if [ -f "$CFG/settings.json" ]; then
  pass "settings.json exists (delivery: ${DELIVERY:-unknown})"
else
  warn "settings.json missing — copy config/settings.example.json or let onboarding seed it"
fi

echo
echo "Delivery — ${DELIVERY:-not set}:"
case "$DELIVERY" in
  lark)
    if command -v lark-cli >/dev/null 2>&1; then
      pass "lark-cli found"
      if lark-cli auth status >/dev/null 2>&1; then pass "lark-cli authenticated"; else fail "lark-cli not authenticated — run: lark-cli auth login (see lark-agents-bridge)"; fi
    else
      fail "delivery=lark but lark-cli not found — set up https://github.com/cindyxu1030/lark-agents-bridge"
    fi
    # open_id only matters for Lark.
    if grep -rq "<YOUR_LARK_OPEN_ID>" "$CFG" 2>/dev/null; then fail "delivery=lark but lark_open_id is still <YOUR_LARK_OPEN_ID> — set your real open_id"; fi
    ;;
  email)
    if [ -n "${NEWSBRIEF_SMTP_USER:-}" ] || grep -q "NEWSBRIEF_SMTP_USER" "$CFG/.env" 2>/dev/null; then pass "SMTP env present"; else fail "delivery=email but no SMTP creds — add them to ~/.config/news-brief/.env (see TUTORIAL.md)"; fi
    ;;
  file)
    pass "delivery=file — writes to ~/Documents/NewsBrief/, nothing else required"
    ;;
  *)
    warn "delivery not set to lark|email|file — defaulting behavior; set it in settings.json"
    ;;
esac

echo
echo "Summary: $OK ok · $WARN warnings · $FAIL failures"
[ $FAIL -eq 0 ]
