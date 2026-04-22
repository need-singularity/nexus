#!/bin/bash
# hosts_liveness_watchdog.sh — Mac-side ssh liveness probe + alert.
# L7 OOM 사고 (2026-04-22 ubu1+ubu2 동시 wedge) 대응 watchdog 1층 (mac-side alert).
# 독립 probe — airgenome supervisor/infra_state 불안정 상태에서도 동작.
# launchd 5min cadence. 연속 2회 실패(=10분 접속불가) 호스트 → macOS notification.
# HOSTS: ubu1 ubu2 htz. mac 자기는 skip.

set -u
AIRGENOME="${AIRGENOME:-/Users/ghost/core/airgenome/bin/airgenome}"
STATE_DIR="$HOME/.airgenome"
STATE_FILE="$STATE_DIR/watchdog_streak.tsv"
LOG="$STATE_DIR/watchdog.log"
HOSTS=(ubu1 ubu2 htz)
THRESHOLD=2

mkdir -p "$STATE_DIR"
touch "$STATE_FILE"
ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

declare -A prev_streak
while IFS=$'\t' read -r h n _; do
  [ -n "$h" ] && prev_streak[$h]="$n"
done < "$STATE_FILE"

new_tsv=""
alerted=""
for host in "${HOSTS[@]}"; do
  if AIRG_OFFLOAD_FORCE=1 "$AIRGENOME" offload "$host" true >/dev/null 2>&1; then
    streak=0
  else
    streak=$(( ${prev_streak[$host]:-0} + 1 ))
  fi
  new_tsv+="$host	$streak	$ts
"
  if [ "$streak" -ge "$THRESHOLD" ] && [ "${prev_streak[$host]:-0}" -lt "$THRESHOLD" ]; then
    alerted+="$host "
  fi
done

printf '%s' "$new_tsv" > "$STATE_FILE"
echo "$ts streaks: $(printf '%s' "$new_tsv" | tr '\n' ' ')" >> "$LOG"

if [ -n "$alerted" ]; then
  msg="hosts offline ≥${THRESHOLD} consecutive probes (≈$((THRESHOLD*5))m): ${alerted% }"
  osascript -e "display notification \"${msg}\" with title \"nexus host watchdog\" sound name \"Submarine\"" 2>/dev/null || true
  echo "$ts ALERT: $msg" >> "$LOG"
fi
