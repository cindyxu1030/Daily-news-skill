#!/usr/bin/env bash
# News Brief runner — called by a scheduler (macOS LaunchAgent or cron) at your chosen time.
# Local test:  NEWSBRIEF_DRY_RUN=1 ./scripts/run_brief.sh   (writes to ~/Documents/NewsBrief/, no send)

set -euo pipefail

# Add the directory containing the `claude` binary to PATH if it isn't already.
# Adjust for your install (covers common Homebrew + user-local paths).
export PATH="$HOME/.local/bin:/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:$PATH"

ENV_FILE="$HOME/.config/news-brief/.env"
if [ -f "$ENV_FILE" ]; then
    set -a
    source "$ENV_FILE"
    set +a
fi

# Model is configurable. Default to the `sonnet` alias so it tracks the current
# Sonnet without a hardcoded version. Override with NEWSBRIEF_MODEL=opus (etc.).
MODEL="${NEWSBRIEF_MODEL:-sonnet}"

# DRY_RUN=1 → skill writes to the local archive only and skips Lark/email.
# Exported so the skill prompt can read it. Defaults to 0 (real delivery).
export NEWSBRIEF_DRY_RUN="${NEWSBRIEF_DRY_RUN:-0}"

LOG_DIR="$HOME/.config/news-brief/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/newsbrief.log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] News Brief starting (model=$MODEL, dry_run=$NEWSBRIEF_DRY_RUN)..." >> "$LOG_FILE"

MAX_ATTEMPTS=4
ATTEMPT=1
EXIT_CODE=1
BACKOFF=60

set +e
while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Attempt $ATTEMPT/$MAX_ATTEMPTS" >> "$LOG_FILE"
    claude \
        --model "$MODEL" \
        -p "Run news brief" \
        >> "$LOG_FILE" 2>&1
    EXIT_CODE=$?
    if [ $EXIT_CODE -eq 0 ]; then
        break
    fi
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Attempt $ATTEMPT failed (exit $EXIT_CODE). Sleeping ${BACKOFF}s." >> "$LOG_FILE"
    sleep $BACKOFF
    BACKOFF=$((BACKOFF * 2))
    ATTEMPT=$((ATTEMPT + 1))
done
set -e

if [ $EXIT_CODE -eq 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] News Brief completed." >> "$LOG_FILE"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] News Brief FAILED after $MAX_ATTEMPTS attempts (exit $EXIT_CODE)." >> "$LOG_FILE"
fi

exit $EXIT_CODE
