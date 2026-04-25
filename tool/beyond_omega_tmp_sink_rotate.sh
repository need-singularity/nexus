#!/usr/bin/env bash
# beyond_omega_tmp_sink_rotate.sh — nxs-20260425-004 cycle 37 (real implementation)
#
# 7-day rotation for /tmp/nexus_omega_*.{log,out.log,err.log} +
# /tmp/nexus_beyond_omega_*.{log,out.log,err.log} sinks.
#
# Workflow:
#   1. Discover matching /tmp files
#   2. For each file with mtime > ROTATION_DAYS days: copy to
#      state/archive/tmp_sinks/YYYY-MM-DD/<basename>, then unlink
#   3. Append audit row to state/archive/tmp_sinks/_audit_log.jsonl
#
# DO NOT auto-run. User must invoke manually OR add to a launchd/cron job
# AFTER reviewing tool/beyond_omega_tmp_sink_audit.py output.
#
# Usage:
#   tool/beyond_omega_tmp_sink_rotate.sh              # 7 day default, archive+unlink
#   ROTATION_DAYS=14 tool/beyond_omega_tmp_sink_rotate.sh
#   ROTATION_MODE=delete tool/beyond_omega_tmp_sink_rotate.sh   # skip archive, just delete
#   DRY_RUN=1 tool/beyond_omega_tmp_sink_rotate.sh    # plan only, no FS mutation
#
# Cron addition (suggested, BUT user must opt-in):
#   0 3 * * 0  cd ~/core/nexus && tool/beyond_omega_tmp_sink_rotate.sh >> /tmp/nexus_beyond_omega_rotate.log 2>&1
#   (weekly Sunday 03:00 — own log file deliberately excluded from glob to avoid self-rotation)

set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
ROTATION_DAYS="${ROTATION_DAYS:-7}"
ROTATION_MODE="${ROTATION_MODE:-archive}"  # archive | delete
DRY_RUN="${DRY_RUN:-0}"

DAY="$(date -u +%Y-%m-%d)"
NOW_ISO="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
ARCHIVE_BASE="$REPO/state/archive/tmp_sinks"
ARCHIVE_DAY="$ARCHIVE_BASE/$DAY"
AUDIT_LOG="$ARCHIVE_BASE/_audit_log.jsonl"

mkdir -p "$ARCHIVE_BASE"

# Find candidates older than ROTATION_DAYS
# (BSD/macOS find: -mtime +N means strictly older than N days)
# Use a tmp file instead of mapfile (mapfile = bash 4+, macOS ships bash 3.2).
CANDIDATES_TMP="$(mktemp -t nexus_rotate_candidates.XXXXXX)"
trap 'rm -f "$CANDIDATES_TMP"' EXIT

find /tmp -maxdepth 1 -type f \( \
     -name 'nexus_omega_*.log' \
  -o -name 'nexus_omega_*.out.log' \
  -o -name 'nexus_omega_*.err.log' \
  -o -name 'nexus_beyond_omega_*.log' \
  -o -name 'nexus_beyond_omega_*.out.log' \
  -o -name 'nexus_beyond_omega_*.err.log' \
\) ! -name 'nexus_beyond_omega_rotate.log' \
   -mtime +"$((ROTATION_DAYS - 1))" 2>/dev/null \
| sort > "$CANDIDATES_TMP"

CANDIDATE_COUNT="$(wc -l < "$CANDIDATES_TMP" | tr -d ' ')"
if [[ "$CANDIDATE_COUNT" -eq 0 ]]; then
  echo "⊙ tmp_sink_rotate no candidates older than ${ROTATION_DAYS}d (nothing to do)"
  exit 0
fi

echo "⊙ tmp_sink_rotate candidates=$CANDIDATE_COUNT mode=$ROTATION_MODE dry_run=$DRY_RUN day=$DAY"

if [[ "$DRY_RUN" != "1" && "$ROTATION_MODE" == "archive" ]]; then
  mkdir -p "$ARCHIVE_DAY"
fi

ARCHIVED=0
DELETED=0
SKIPPED=0
while IFS= read -r f; do
  [[ -z "$f" ]] && continue
  base="$(basename "$f")"
  size=$(stat -f '%z' "$f" 2>/dev/null || echo 0)
  mtime=$(stat -f '%m' "$f" 2>/dev/null || echo 0)
  mtime_iso=$(date -u -r "$mtime" +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || echo "unknown")

  if [[ "$DRY_RUN" == "1" ]]; then
    echo "  [DRY] would $ROTATION_MODE $f ($size bytes, mtime=$mtime_iso)"
    SKIPPED=$((SKIPPED + 1))
    continue
  fi

  if [[ "$ROTATION_MODE" == "archive" ]]; then
    cp "$f" "$ARCHIVE_DAY/$base"
    rm "$f"
    ARCHIVED=$((ARCHIVED + 1))
    echo "  archived $base → $ARCHIVE_DAY/$base ($size bytes)"
  elif [[ "$ROTATION_MODE" == "delete" ]]; then
    rm "$f"
    DELETED=$((DELETED + 1))
    echo "  deleted $base ($size bytes)"
  else
    echo "  unknown ROTATION_MODE=$ROTATION_MODE — skip"
    SKIPPED=$((SKIPPED + 1))
    continue
  fi

  # Append audit row
  printf '{"ts":"%s","action":"%s","path":"%s","size_bytes":%s,"mtime_iso":"%s","archive_day":"%s"}\n' \
    "$NOW_ISO" "$ROTATION_MODE" "$f" "$size" "$mtime_iso" "$DAY" \
    >> "$AUDIT_LOG"
done < "$CANDIDATES_TMP"

echo "⊙ tmp_sink_rotate done archived=$ARCHIVED deleted=$DELETED skipped=$SKIPPED audit=$AUDIT_LOG"
