#!/bin/bash
# beyond_omega_daily_chain.sh — nxs-20260425-004 cycle 32
#
# Daily chain: ghost_trace --cron + atlas_bridge.
# 사용처: tool/com.nexus.beyond-omega-daily.plist 의 ProgramArguments.
# 이 wrapper 가 (1) ghost ceiling daily snapshot 누적 (2) atlas_health_timeline 에
# REAL findings 7 rows append.

set -u
LOG=/tmp/nexus_beyond_omega_daily_chain.log
REPO=/Users/ghost/core/nexus
PY=/opt/homebrew/bin/python3

ts() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }

echo "[$(ts)] === daily chain start ===" >> "$LOG"

# Step 1: ghost ceiling daily snapshot
"$PY" "$REPO/tool/beyond_omega_ghost_trace.py" --cron >> "$LOG" 2>&1
RC1=$?
echo "[$(ts)] ghost_trace --cron rc=$RC1" >> "$LOG"

# Step 2: atlas absorption bridge (REAL findings only)
if [[ -f "$REPO/tool/beyond_omega_atlas_bridge.py" ]]; then
    "$PY" "$REPO/tool/beyond_omega_atlas_bridge.py" >> "$LOG" 2>&1
    RC2=$?
    echo "[$(ts)] atlas_bridge rc=$RC2" >> "$LOG"
else
    echo "[$(ts)] atlas_bridge MISSING — skipped" >> "$LOG"
    RC2=127
fi

echo "[$(ts)] === daily chain end (rc1=$RC1 rc2=$RC2) ===" >> "$LOG"
exit $((RC1 == 0 && RC2 == 0 ? 0 : 1))
