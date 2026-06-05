#!/usr/bin/env bash
# News Brief setup checker. Run after install to find what's missing before your first brief.
#   ./scripts/doctor.sh
# Exits non-zero if anything required is broken.

CFG="$HOME/.config/news-brief"
OK=0
WARN=0
FAIL=0

pass() { printf '  \033[32m✓\033[0m %s\n' "$1"; OK=$((OK+1)); }
warn() { printf '  \033[33m!\033[0m %s\n' "$1"; WARN=$((WARN+1)); }
fail() { printf '  \033[31m✗\033[0m %s\n' "$1"; FAIL=$((FAIL+1)); }

echo "News Brief — setup check"
echo

echo "Core:"
if command -v claude >/dev/null 2>&1; then pass "claude CLI found ($(command -v claude))"; else fail "claude CLI not on PATH — install Claude Code"; fi

echo
echo "Config (~/.config/news-brief):"
if [ -f "$CFG/profile.md" ]; then pass "profile.md exists (your reader profile)"; else warn "profile.md missing — run /news-brief once to build it (onboarding)"; fi
if [ -f "$CFG/sources.json" ]; then pass "sources.json exists"; else warn "sources.json missing — copy config/sources.example.json or let onboarding seed it"; fi
if [ -f "$CFG/settings.json" ]; then
  pass "settings.json exists"
  DELIVERY=$(grep -o '"delivery"[^,}]*' "$CFG/settings.json" 2>/dev/null | head -1)
  echo "      $DELIVERY"
else
  warn "settings.json missing — copy config/settings.example.json or let onboarding seed it"
fi

echo
echo "Delivery — Lark:"
if command -v lark-cli >/dev/null 2>&1; then
  pass "lark-cli found"
  if lark-cli auth status >/dev/null 2>&1; then pass "lark-cli authenticated"; else warn "lark-cli not authenticated — run: lark-cli auth login (scope im:message.send_as_bot)"; fi
else
  warn "lark-cli not found — only needed if delivery=lark"
fi
# Flag an unreplaced placeholder anywhere in config.
if grep -rq "<YOUR_LARK_OPEN_ID>" "$CFG" 2>/dev/null; then fail "settings.json still has <YOUR_LARK_OPEN_ID> — replace with your real open_id"; fi

echo
echo "Delivery — email (optional):"
if [ -n "${NEWSBRIEF_SMTP_USER:-}" ] || grep -q "NEWSBRIEF_SMTP_USER" "$CFG/.env" 2>/dev/null; then pass "SMTP env present"; else warn "no SMTP env — only needed if delivery=email (see TUTORIAL.md)"; fi

echo
echo "Summary: $OK ok · $WARN warnings · $FAIL failures"
[ $FAIL -eq 0 ]
