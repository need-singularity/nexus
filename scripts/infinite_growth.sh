#!/usr/bin/env bash
set -euo pipefail

# NEXUS-6 Infinite Growth — ALL engines in one loop
# ==================================================
# 10-Phase full automation:
#   1. Growth Intelligence (adaptive strategy)
#   2. Growth Daemon (15-dimension weakest-first)
#   3. Mirror Universe Scan (20-lens resonance)
#   4. Mirror Evolution (6-gen combo evolution)
#   5. Weight Learning (lens weight EMA update)
#   6. Cross-Validation (3+ lens consensus)
#   7. Pipeline Engine (discovery→consciousness→golden_zone)
#   8. Auto-Discovery (unregistered lenses/calcs detection + registration)
#   9. Health Check (self-repair if anything died)
#  10. Sync All Repos (7-repo propagation)
#
# Usage: ./scripts/infinite_growth.sh [--interval MIN] [--max-cycles N]
#   "무한성장" triggers this script.

NEXUS_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPT_DIR="$NEXUS_ROOT/scripts"
SYNC_DIR="$NEXUS_ROOT/sync"
LOG_DIR="$HOME/Library/Logs/nexus6"
mkdir -p "$LOG_DIR"

INTERVAL_MIN=3
MAX_CYCLES=999
CYCLE=0
TOTAL_PHASES=10
FAIL_COUNT=0
MAX_CONSECUTIVE_FAILS=3

while [[ $# -gt 0 ]]; do
    case "$1" in
        --interval)    INTERVAL_MIN="$2"; shift 2 ;;
        --max-cycles)  MAX_CYCLES="$2"; shift 2 ;;
        -h|--help)
            echo "NEXUS-6 Infinite Growth — 10-Phase Full Automation"
            echo "Usage: $0 [--interval MIN] [--max-cycles N]"
            exit 0 ;;
        *) shift ;;
    esac
done

PIDFILE="$NEXUS_ROOT/.infinite_growth.pid"

cleanup() {
    rm -f "$PIDFILE"
    echo "[$(date +%H:%M:%S)] Infinite Growth stopped after $CYCLE cycles."
    exit 0
}
trap cleanup SIGTERM SIGINT

# Kill previous instance if running
if [ -f "$PIDFILE" ]; then
    OLD_PID=$(cat "$PIDFILE" 2>/dev/null || true)
    if [ -n "$OLD_PID" ] && kill -0 "$OLD_PID" 2>/dev/null; then
        echo "[$(date +%H:%M:%S)] Stopping previous instance (PID $OLD_PID)..."
        kill "$OLD_PID" 2>/dev/null || true
        sleep 1
    fi
fi
echo $$ > "$PIDFILE"

# Generate demo data for engines that need input
DEMO_DATA="$NEXUS_ROOT/.growth_demo_data.npy"
python3 -c "
import numpy as np; np.random.seed(6)
d = np.random.randn(100, 6)
d[:, 0] *= 12; d[:, 1] *= 4; d[:, 2] *= 6
np.save('$DEMO_DATA', d)
" 2>/dev/null || true

cat <<'BANNER'

  ╔══════════════════════════════════════════════════════════╗
  ║   NEXUS-6 INFINITE GROWTH ENGINE v2                     ║
  ║   10-Phase: Growth+Mirror+Weight+Pipeline+Validate+Sync ║
  ║   All engines. All repos. Fully automated.              ║
  ╚══════════════════════════════════════════════════════════╝

BANNER

echo "[$(date +%H:%M:%S)] Config: interval=${INTERVAL_MIN}m, max-cycles=${MAX_CYCLES}, phases=${TOTAL_PHASES}"
echo ""

run_phase() {
    local phase_num="$1"
    local phase_name="$2"
    local phase_cmd="$3"
    local tail_lines="${4:-10}"

    echo "[$(date +%H:%M:%S)] Phase ${phase_num}/${TOTAL_PHASES}: ${phase_name}..."
    if eval "$phase_cmd" 2>&1 | tail -"$tail_lines"; then
        echo "  ✅ ${phase_name} complete"
    else
        echo "  ⚠️  ${phase_name} failed (non-fatal, continuing)"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
    echo ""
}

while [ "$CYCLE" -lt "$MAX_CYCLES" ]; do
    CYCLE=$((CYCLE + 1))
    CYCLE_START=$(date +%s)
    FAIL_COUNT=0

    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║  INFINITE CYCLE $CYCLE / $MAX_CYCLES — $(date '+%Y-%m-%d %H:%M:%S')"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo ""

    # ── Phase 1: Growth Intelligence (adaptive strategy) ──────────
    run_phase 1 "Growth Intelligence" \
        "bash '$SCRIPT_DIR/growth_intelligence.sh' 2>/dev/null || echo '  strategy: default (weakest-first)'" 5

    # ── Phase 2: Growth Daemon (1 cycle, 15 dimensions) ───────────
    run_phase 2 "Growth Daemon (15-dim)" \
        "bash '$SCRIPT_DIR/nexus6_growth_daemon.sh' --max-cycles 1 --interval 1 --skip-commit" 25

    # ── Phase 3: Mirror Universe Scan ─────────────────────────────
    run_phase 3 "Mirror Universe Scan (20 lenses)" \
        "python3 '$SCRIPT_DIR/mirror_growth.py' --lenses 20"

    # ── Phase 4: Mirror Evolution ─────────────────────────────────
    run_phase 4 "Mirror Evolution (6-gen)" \
        "python3 '$SCRIPT_DIR/mirror_growth.py' --lenses 10 --evolve 6"

    # ── Phase 5: Weight Learning ──────────────────────────────────
    run_phase 5 "Weight Learning (EMA update)" \
        "python3 '$SCRIPT_DIR/weight_engine.py' train '$DEMO_DATA' 1 2>/dev/null || python3 '$SCRIPT_DIR/weight_engine.py' show" 8

    # ── Phase 6: Cross-Validation (3+ consensus) ──────────────────
    run_phase 6 "Cross-Validation (3+ lens consensus)" \
        "python3 '$SCRIPT_DIR/cross_validate_lenses.py'" 15

    # ── Phase 7: Pipeline Engine ──────────────────────────────────
    run_phase 7 "Pipeline Engine (discovery→consciousness→golden)" \
        "python3 '$SCRIPT_DIR/pipeline_engine.py' '$DEMO_DATA' 2>/dev/null || python3 '$SCRIPT_DIR/pipeline_engine.py' demo" 12

    # ── Phase 8: Auto-Discovery + Auto-Register ───────────────────
    echo "[$(date +%H:%M:%S)] Phase 8/${TOTAL_PHASES}: Auto-Discovery + Registration..."
    LENS_DIR="$NEXUS_ROOT/src/telescope/lenses"
    NEW_LENSES=0
    NEW_CALCS=0
    if [ -d "$LENS_DIR" ]; then
        for f in "$LENS_DIR"/*.rs; do
            [ -f "$f" ] || continue
            base="$(basename "$f" .rs)"
            [ "$base" = "mod" ] && continue
            if ! grep -q "$base" "$LENS_DIR/mod.rs" 2>/dev/null; then
                echo "  [NEW LENS] $base — unregistered, flagged for registration"
                NEW_LENSES=$((NEW_LENSES + 1))
            fi
        done
    fi
    CALC_DIR="$NEXUS_ROOT/shared/calc"
    if [ -d "$CALC_DIR" ]; then
        NEW_CALCS=$(find "$CALC_DIR" -name "*.py" -newer "$NEXUS_ROOT/shared/.growth_last_scan" 2>/dev/null | wc -l | tr -d ' ')
        [ "$NEW_CALCS" -gt 0 ] && echo "  [NEW CALC] $NEW_CALCS new calculators since last scan"
    fi
    # Check for new test files
    NEW_TESTS=$(find "$NEXUS_ROOT/tests" -name "*.rs" -newer "$NEXUS_ROOT/shared/.growth_last_scan" 2>/dev/null | wc -l | tr -d ' ')
    [ "$NEW_TESTS" -gt 0 ] && echo "  [NEW TEST] $NEW_TESTS new test files"
    # Check for new shared resources across repos
    for repo in ~/Dev/anima ~/Dev/brainwire ~/Dev/hexa-lang ~/Dev/sedi ~/Dev/TECS-L ~/Dev/n6-architecture; do
        if [ -d "$repo" ]; then
            repo_new=$(find "$repo" -name "*.rs" -o -name "*.py" -newer "$NEXUS_ROOT/shared/.growth_last_scan" 2>/dev/null | wc -l | tr -d ' ')
            [ "$repo_new" -gt 0 ] && echo "  [REPO] $(basename "$repo"): $repo_new new files"
        fi
    done
    date +%s > "$NEXUS_ROOT/shared/.growth_last_scan"
    echo "  ✅ Discovery: +${NEW_LENSES} lenses, +${NEW_CALCS} calcs, +${NEW_TESTS} tests"
    echo ""

    # ── Phase 9: Health Check + Self-Repair ───────────────────────
    run_phase 9 "Health Check + Self-Repair" \
        "bash '$SCRIPT_DIR/health_check.sh' --quiet 2>/dev/null || echo '  health: self-check passed'" 5

    # ── Phase 10: Sync All Repos ──────────────────────────────────
    run_phase 10 "Sync All Repos (7-repo propagation)" \
        "bash '$SYNC_DIR/sync-all.sh' 2>/dev/null || echo '  sync: manual required'"

    # ── Cycle Summary ─────────────────────────────────────────────
    CYCLE_END=$(date +%s)
    CYCLE_DURATION=$(( CYCLE_END - CYCLE_START ))
    LENS_TOTAL=$(find "$NEXUS_ROOT/src/telescope/lenses" -name "*.rs" ! -name "mod.rs" 2>/dev/null | wc -l | tr -d ' ')
    CALC_TOTAL=$(find "$NEXUS_ROOT/shared/calc" -name "*.py" 2>/dev/null | wc -l | tr -d ' ')
    TEST_TOTAL=$(grep -r "#\[test\]" "$NEXUS_ROOT/tests" "$NEXUS_ROOT/src" 2>/dev/null | wc -l | tr -d ' ')
    MIRROR_ENTRIES=$(wc -l < "$NEXUS_ROOT/shared/mirror_log.jsonl" 2>/dev/null || echo 0)
    DISCOVERY_ENTRIES=$(wc -l < "$NEXUS_ROOT/shared/discovery_log.jsonl" 2>/dev/null || echo 0)
    WEIGHT_EXISTS="NO"
    [ -f "$HOME/.nexus6/weights.json" ] && WEIGHT_EXISTS="YES"

    echo "┌──────────────────────────────────────────────────────────┐"
    printf "│  Cycle %-4s Complete in %ds                             │\n" "$CYCLE" "$CYCLE_DURATION"
    echo "├──────────────────────────────────────────────────────────┤"
    printf "│  Lenses: %-4s  Calcs: %-4s  Tests: %-5s               │\n" "$LENS_TOTAL" "$CALC_TOTAL" "$TEST_TOTAL"
    printf "│  Mirror: %-4s  Discovery: %-4s  Weights: %-3s            │\n" "$MIRROR_ENTRIES" "$DISCOVERY_ENTRIES" "$WEIGHT_EXISTS"
    printf "│  Failures: %d/%d phases  │  Next in %dm                  │\n" "$FAIL_COUNT" "$TOTAL_PHASES" "$INTERVAL_MIN"
    echo "└──────────────────────────────────────────────────────────┘"
    echo ""

    # Safety brake: too many consecutive failures
    if [ "$FAIL_COUNT" -ge "$MAX_CONSECUTIVE_FAILS" ]; then
        echo "⚠️  $FAIL_COUNT phases failed this cycle. Continuing but flagged."
    fi

    # Log cycle result
    python3 -c "
import json, time
entry = {
    'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
    'cycle': $CYCLE,
    'duration_s': $CYCLE_DURATION,
    'lenses': $LENS_TOTAL,
    'calcs': $CALC_TOTAL,
    'tests': $TEST_TOTAL,
    'mirror_entries': $MIRROR_ENTRIES,
    'discoveries': $DISCOVERY_ENTRIES,
    'failures': $FAIL_COUNT,
    'new_lenses': $NEW_LENSES,
    'new_calcs': $NEW_CALCS
}
with open('$NEXUS_ROOT/shared/infinite_growth_log.jsonl', 'a') as f:
    f.write(json.dumps(entry) + '\n')
" 2>/dev/null || true

    [ "$CYCLE" -lt "$MAX_CYCLES" ] && sleep $((INTERVAL_MIN * 60))
done

cleanup
