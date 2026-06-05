#!/usr/bin/env bash
# News Brief runner — called by a scheduler (macOS LaunchAgent or cron) at your chosen time.
# Uses Sonnet 4.6 for cost-efficient research.

set -euo pipefail

# Add the directory containing the `claude` binary to PATH if it isn't already.
# Adjust as needed for your install (this covers common Homebrew + user-local paths).
export PATH="$HOME/.local/bin:/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:$PATH"

ENV_FILE="$HOME/.config/news-brief/.env"
if [ -f "$ENV_FILE" ]; then
    set -a
    source "$ENV_FILE"
    set +a
fi

LOG_DIR="$HOME/.config/news-brief/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/newsbrief.log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] News Brief starting..." >> "$LOG_FILE"

MAX_ATTEMPTS=4
ATTEMPT=1
EXIT_CODE=1
BACKOFF=60

set +e
while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Attempt $ATTEMPT/$MAX_ATTEMPTS" >> "$LOG_FILE"
    claude \
        --model claude-sonnet-4-6 \
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
