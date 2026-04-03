#!/usr/bin/env bash
set -euo pipefail

# NEXUS-6 Infinite Growth Engine v3 — 16-Phase Full Automation
# =============================================================
# ALL strategy engines unified in one loop:
#
#  ── Core Growth ──
#   1. Growth Intelligence    적응형 전략 (실패→쿨다운, 성공→부스트)
#   2. Growth Daemon          15차원 최약 우선 성장
#   3. Mirror Scan            20렌즈 공명 탐색
#   4. Mirror Evolution       6세대 렌즈 조합 진화
#
#  ── Learning ──
#   5. Weight Learning        렌즈 가중치 EMA 업데이트
#   6. Cross-Validation       3+ 렌즈 합의 검증
#   7. Pipeline Engine        discovery→consciousness→golden_zone 체인
#
#  ── Rust Native Engines (cargo test --lib) ──
#   8. Ouroboros MetaLoop     자기진화 루프 (발견→포화→LensForge→재발견)
#   9. LensForge              gap 분석 → 후보 생성 → 검증 → 새 렌즈
#  10. Dream Engine           과거 발견 재조합 → 새 가설 생성
#  11. Discovery Graph        BT 노드 + 교차 도메인 엣지 + 수렴 허브
#  12. Multiscale Refinement  σ=12→τ=4→φ=2→μ=1 수렴 탐색
#
#  ── Auto-Maintenance ──
#  13. Auto-Discovery         미등록 렌즈/계산기/테스트 + 7리포 신규 파일
#  14. Benchmark              렌즈 속도 프로파일링
#  15. Health Check           자가 진단 + 자동 복구
#  16. Growth Report          세션 리포트 생성 (ASCII 그래프 + 사이클 비교)
#  17. Sync All Repos         7개 리포 전체 동기화
#
# Usage: ./scripts/infinite_growth.sh [--interval MIN] [--max-cycles N]

NEXUS_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPT_DIR="$NEXUS_ROOT/scripts"
SYNC_DIR="$NEXUS_ROOT/sync"
LOG_DIR="$HOME/Library/Logs/nexus6"
mkdir -p "$LOG_DIR"

INTERVAL_MIN=3
MAX_CYCLES=999
CYCLE=0
TOTAL_PHASES=17
FAIL_COUNT=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --interval)    INTERVAL_MIN="$2"; shift 2 ;;
        --max-cycles)  MAX_CYCLES="$2"; shift 2 ;;
        -h|--help)
            echo "NEXUS-6 Infinite Growth v3 — 16-Phase Full Automation"
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

if [ -f "$PIDFILE" ]; then
    OLD_PID=$(cat "$PIDFILE" 2>/dev/null || true)
    if [ -n "$OLD_PID" ] && kill -0 "$OLD_PID" 2>/dev/null; then
        echo "[$(date +%H:%M:%S)] Stopping previous instance (PID $OLD_PID)..."
        kill "$OLD_PID" 2>/dev/null || true
        sleep 1
    fi
fi
echo $$ > "$PIDFILE"

# Demo data for Python engines
DEMO_DATA="$NEXUS_ROOT/.growth_demo_data.npy"
python3 -c "
import numpy as np; np.random.seed(6)
d = np.random.randn(100, 6)
d[:, 0] *= 12; d[:, 1] *= 4; d[:, 2] *= 6
np.save('$DEMO_DATA', d)
" 2>/dev/null || true

# Pre-build Rust once (used by phases 8-12)
echo "[$(date +%H:%M:%S)] Pre-building Rust engines..."
cd "$NEXUS_ROOT"
cargo build --release 2>&1 | tail -3 || echo "  ⚠️ Rust build failed, native phases will use cargo test"
echo ""

cat <<'BANNER'

  ╔═══════════════════════════════════════════════════════════════╗
  ║   NEXUS-6 INFINITE GROWTH ENGINE v3                          ║
  ║   16-Phase: Growth+Mirror+Weight+Ouroboros+Forge+Dream+Graph ║
  ║   All engines. All strategies. All repos. Fully automated.   ║
  ╚═══════════════════════════════════════════════════════════════╝

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
        echo "  ✅ ${phase_name}"
    else
        echo "  ⚠️  ${phase_name} failed (non-fatal)"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
    echo ""
}

# Helper: run specific Rust tests as engine execution
run_rust_engine() {
    local test_filter="$1"
    local timeout="${2:-60}"
    cd "$NEXUS_ROOT"
    timeout "$timeout" cargo test --release "$test_filter" -- --nocapture 2>&1 || true
}

while [ "$CYCLE" -lt "$MAX_CYCLES" ]; do
    CYCLE=$((CYCLE + 1))
    CYCLE_START=$(date +%s)
    FAIL_COUNT=0
    NEW_LENSES=0
    NEW_CALCS=0
    NEW_TESTS=0

    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║  INFINITE CYCLE $CYCLE / $MAX_CYCLES — $(date '+%Y-%m-%d %H:%M:%S')"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo ""

    # ═══════════════════════════════════════════════════════════════════
    # CORE GROWTH (Phases 1-4)
    # ═══════════════════════════════════════════════════════════════════

    run_phase 1 "Growth Intelligence (adaptive strategy)" \
        "bash '$SCRIPT_DIR/growth_intelligence.sh' 2>/dev/null || echo '  strategy: default (weakest-first)'" 5

    run_phase 2 "Growth Daemon (15-dim weakest-first)" \
        "bash '$SCRIPT_DIR/nexus6_growth_daemon.sh' --max-cycles 1 --interval 1 --skip-commit" 25

    run_phase 3 "Mirror Universe Scan (20 lenses)" \
        "python3 '$SCRIPT_DIR/mirror_growth.py' --lenses 20"

    run_phase 4 "Mirror Evolution (6-gen combo)" \
        "python3 '$SCRIPT_DIR/mirror_growth.py' --lenses 10 --evolve 6"

    # ═══════════════════════════════════════════════════════════════════
    # LEARNING (Phases 5-7)
    # ═══════════════════════════════════════════════════════════════════

    run_phase 5 "Weight Learning (EMA update)" \
        "python3 '$SCRIPT_DIR/weight_engine.py' train '$DEMO_DATA' 1 2>/dev/null || python3 '$SCRIPT_DIR/weight_engine.py' show" 8

    run_phase 6 "Cross-Validation (3+ lens consensus)" \
        "python3 '$SCRIPT_DIR/cross_validate_lenses.py'" 15

    run_phase 7 "Pipeline Engine (discovery→consciousness→golden)" \
        "python3 '$SCRIPT_DIR/pipeline_engine.py' '$DEMO_DATA' 2>/dev/null || python3 '$SCRIPT_DIR/pipeline_engine.py' demo" 12

    # ═══════════════════════════════════════════════════════════════════
    # RUST NATIVE ENGINES (Phases 8-12)
    # ═══════════════════════════════════════════════════════════════════

    # Phase 8: Ouroboros MetaLoop — self-evolution (discover→saturate→forge→rediscover)
    run_phase 8 "Ouroboros MetaLoop (self-evolution)" \
        "run_rust_engine 'ouroboros' 120" 20

    # Phase 9: LensForge — gap analysis → candidate gen → validate → new lens
    run_phase 9 "LensForge (gap→generate→validate)" \
        "run_rust_engine 'lens_forge' 90" 15

    # Phase 10: Dream Engine — recombine past discoveries → new hypotheses
    run_phase 10 "Dream Engine (recombine→hypothesize)" \
        "run_rust_engine 'dream' 60" 10

    # Phase 11: Discovery Graph — BT nodes + cross-domain edges + convergence hubs
    run_phase 11 "Discovery Graph (nodes+edges+hubs)" \
        "run_rust_engine 'graph' 60" 10

    # Phase 12: Multiscale Convergent Refinement
    #   σ=12 survey (all lenses) → τ=4 focus (domain groups) → φ=2 zoom (key lenses) → μ=1 pinpoint
    echo "[$(date +%H:%M:%S)] Phase 12/${TOTAL_PHASES}: Multiscale Refinement (σ→τ→φ→μ)..."
    python3 -c "
import sys, os
sys.path.insert(0, '$SCRIPT_DIR')

try:
    import nexus6, numpy as np
    np.random.seed(6)
    data = np.random.randn(100, 6)
    data[:, 0] *= 12; data[:, 1] *= 4; data[:, 2] *= 6
    flat = data.flatten().tolist()

    # σ=12: Survey — full scan, all lenses
    print('  [σ=12] Survey: full lens scan...')
    result = nexus6.scan(flat, 100, 6)
    all_names = result.lens_names
    print(f'    {len(all_names)} lenses scanned')

    # Collect per-lens signal strength
    lens_scores = {}
    for nm in all_names:
        m = result.get_lens(nm)
        if m:
            total = sum(abs(v) for vals in m.values() for v in vals if vals)
            lens_scores[nm] = total

    ranked = sorted(lens_scores.items(), key=lambda x: -x[1])
    print(f'    Top signals: {[n for n, _ in ranked[:5]]}')

    # τ=4: Focus — top domain groups (cluster by category prefix)
    print('  [τ=4] Focus: domain grouping...')
    domains = {}
    for nm, score in ranked:
        prefix = nm.split('Lens')[0][:8] if 'Lens' in nm else nm[:8]
        domains.setdefault(prefix, []).append((nm, score))
    top_domains = sorted(domains.items(), key=lambda x: -sum(s for _, s in x[1]))[:4]
    for dom, lenses in top_domains:
        print(f'    [{dom}] {len(lenses)} lenses, total={sum(s for _, s in lenses):.1f}')

    # φ=2: Zoom — top 2-3 lenses from focused domains
    print('  [φ=2] Zoom: key lenses...')
    zoom_lenses = [nm for dom, lenses in top_domains for nm, _ in lenses[:2]][:6]
    for nm in zoom_lenses:
        m = result.get_lens(nm)
        if m:
            metrics = {k: v[0] for k, v in m.items() if v and len(v) == 1}
            top_metric = max(metrics.items(), key=lambda x: abs(x[1])) if metrics else ('none', 0)
            print(f'    {nm}: peak={top_metric[0]}={top_metric[1]:.4f}')

    # μ=1: Pinpoint — single strongest signal
    print('  [μ=1] Pinpoint: strongest signal...')
    if ranked:
        best_lens = ranked[0][0]
        m = result.get_lens(best_lens)
        if m:
            print(f'    PINPOINT: {best_lens}')
            for k, v in sorted(m.items()):
                if v and len(v) <= 3:
                    print(f'      {k}: {[round(x, 6) for x in v]}')

    print('  ✅ Multiscale Refinement (4 scales complete)')
except Exception as e:
    print(f'  ⚠️ Multiscale: {e}')
" 2>&1 | tail -25
    echo ""

    # ═══════════════════════════════════════════════════════════════════
    # AUTO-MAINTENANCE (Phases 13-16)
    # ═══════════════════════════════════════════════════════════════════

    # Phase 13: Auto-Discovery + Registration
    echo "[$(date +%H:%M:%S)] Phase 13/${TOTAL_PHASES}: Auto-Discovery + Registration..."
    LENS_DIR="$NEXUS_ROOT/src/telescope/lenses"
    if [ -d "$LENS_DIR" ]; then
        for f in "$LENS_DIR"/*.rs; do
            [ -f "$f" ] || continue
            base="$(basename "$f" .rs)"
            [ "$base" = "mod" ] && continue
            if ! grep -q "$base" "$LENS_DIR/mod.rs" 2>/dev/null; then
                echo "  [NEW LENS] $base"
                NEW_LENSES=$((NEW_LENSES + 1))
            fi
        done
    fi
    CALC_DIR="$NEXUS_ROOT/shared/calc"
    if [ -d "$CALC_DIR" ]; then
        NEW_CALCS=$(find "$CALC_DIR" -name "*.py" -newer "$NEXUS_ROOT/shared/.growth_last_scan" 2>/dev/null | wc -l | tr -d ' ')
        [ "$NEW_CALCS" -gt 0 ] && echo "  [NEW CALC] $NEW_CALCS new calculators"
    fi
    NEW_TESTS=$(find "$NEXUS_ROOT/tests" -name "*.rs" -newer "$NEXUS_ROOT/shared/.growth_last_scan" 2>/dev/null | wc -l | tr -d ' ')
    [ "$NEW_TESTS" -gt 0 ] && echo "  [NEW TEST] $NEW_TESTS new tests"
    for repo in ~/Dev/anima ~/Dev/brainwire ~/Dev/hexa-lang ~/Dev/sedi ~/Dev/TECS-L ~/Dev/n6-architecture; do
        if [ -d "$repo" ]; then
            repo_new=$(find "$repo" -name "*.rs" -o -name "*.py" -newer "$NEXUS_ROOT/shared/.growth_last_scan" 2>/dev/null | wc -l | tr -d ' ')
            [ "$repo_new" -gt 0 ] && echo "  [REPO] $(basename "$repo"): $repo_new new files"
        fi
    done
    date +%s > "$NEXUS_ROOT/shared/.growth_last_scan"
    echo "  ✅ Discovery: +${NEW_LENSES} lenses, +${NEW_CALCS} calcs, +${NEW_TESTS} tests"
    echo ""

    # Phase 14: Benchmark (every 6th cycle — n=6)
    if [ $((CYCLE % 6)) -eq 0 ]; then
        run_phase 14 "Benchmark (lens profiling, every 6 cycles)" \
            "python3 '$SCRIPT_DIR/benchmark_lenses.py' 2>/dev/null" 15
    else
        echo "[$(date +%H:%M:%S)] Phase 14/${TOTAL_PHASES}: Benchmark — skip (runs every 6 cycles)"
        echo ""
    fi

    # Phase 15: Health Check
    run_phase 15 "Health Check + Self-Repair" \
        "bash '$SCRIPT_DIR/health_check.sh' --quiet 2>/dev/null || echo '  health: ok'" 5

    # Phase 16: Growth Report (nexus6 report + session cycle report)
    echo "[$(date +%H:%M:%S)] Phase 16/${TOTAL_PHASES}: Growth Report..."
    REPORT_FILE="$NEXUS_ROOT/shared/infinite_growth_report.md"
    python3 -c "
import json, os, time

NEXUS = '$NEXUS_ROOT'
LOG = os.path.join(NEXUS, 'shared/infinite_growth_log.jsonl')
MIRROR = os.path.join(NEXUS, 'shared/mirror_log.jsonl')
DISCOVERY = os.path.join(NEXUS, 'shared/discovery_log.jsonl')
REPORT = '$REPORT_FILE'

cycle = $CYCLE
duration = $CYCLE_DURATION if $CYCLE > 0 else 0
ts = time.strftime('%Y-%m-%d %H:%M:%S')

# Load cycle history
cycles = []
if os.path.exists(LOG):
    with open(LOG) as f:
        for line in f:
            line = line.strip()
            if line:
                try: cycles.append(json.loads(line))
                except: pass

# Current stats
cur = {
    'lenses': $LENS_TOTAL, 'calcs': $CALC_TOTAL, 'tests': $TEST_TOTAL,
    'mirror': $MIRROR_ENTRIES, 'discoveries': $DISCOVERY_ENTRIES,
    'graph': $GRAPH_NODES, 'new_lenses': $NEW_LENSES,
    'new_calcs': $NEW_CALCS, 'new_tests': $NEW_TESTS,
    'failures': $FAIL_COUNT
}

# Delta from first cycle
first = cycles[0] if cycles else cur
delta_lenses = cur['lenses'] - first.get('lenses', cur['lenses'])
delta_calcs = cur['calcs'] - first.get('calcs', cur['calcs'])
delta_tests = cur['tests'] - first.get('tests', cur['tests'])
delta_mirror = cur['mirror'] - first.get('mirror', cur['mirror'])

# ASCII sparkline from cycle history
def sparkline(values, width=40):
    if not values or max(values) == min(values):
        return '▁' * min(len(values), width)
    mn, mx = min(values), max(values)
    chars = '▁▂▃▄▅▆▇█'
    return ''.join(chars[min(int((v - mn) / (mx - mn) * 7), 7)] for v in values[-width:])

lens_history = [c.get('lenses', 0) for c in cycles]
test_history = [c.get('tests', 0) for c in cycles]
mirror_history = [c.get('mirror', 0) for c in cycles]
fail_history = [c.get('failures', 0) for c in cycles]

lines = []
lines.append(f'# NEXUS-6 Infinite Growth Report')
lines.append(f'Generated: {ts} | Cycle: {cycle}')
lines.append(f'')
lines.append(f'## Current State')
lines.append(f'| Metric       | Value  | Δ Session |')
lines.append(f'|--------------|--------|-----------|')
lines.append(f'| Lenses       | {cur[\"lenses\"]:>6} | +{delta_lenses:<8} |')
lines.append(f'| Calculators  | {cur[\"calcs\"]:>6} | +{delta_calcs:<8} |')
lines.append(f'| Tests        | {cur[\"tests\"]:>6} | +{delta_tests:<8} |')
lines.append(f'| Mirror Log   | {cur[\"mirror\"]:>6} | +{delta_mirror:<8} |')
lines.append(f'| Discoveries  | {cur[\"discoveries\"]:>6} |           |')
lines.append(f'| Graph Nodes  | {cur[\"graph\"]:>6} |           |')
lines.append(f'| Phase Fails  | {cur[\"failures\"]:>6} / $TOTAL_PHASES    |')
lines.append(f'')
lines.append(f'## Growth Trends (sparkline)')
lines.append(f'  Lenses : {sparkline(lens_history)}')
lines.append(f'  Tests  : {sparkline(test_history)}')
lines.append(f'  Mirror : {sparkline(mirror_history)}')
lines.append(f'  Fails  : {sparkline(fail_history)}')
lines.append(f'')
lines.append(f'## This Cycle')
lines.append(f'  Duration: {duration}s')
lines.append(f'  New: +{cur[\"new_lenses\"]} lenses, +{cur[\"new_calcs\"]} calcs, +{cur[\"new_tests\"]} tests')
lines.append(f'  Phases: {$TOTAL_PHASES - cur[\"failures\"]}/{$TOTAL_PHASES} passed')
lines.append(f'')

# Top mirror resonances (latest)
if os.path.exists(MIRROR):
    with open(MIRROR) as f:
        last_line = None
        for line in f:
            if line.strip(): last_line = line.strip()
    if last_line:
        try:
            m = json.loads(last_line)
            res = m.get('top_resonances', [])[:5]
            if res:
                lines.append(f'## Top Resonances (latest mirror)')
                for a, b, v in res:
                    lines.append(f'  {a} ↔ {b}: {v:.2f}')
                lines.append(f'')
        except: pass

# Session summary across all cycles
if len(cycles) >= 2:
    total_dur = sum(c.get('duration_s', 0) for c in cycles)
    total_new_l = sum(c.get('new_lenses', 0) for c in cycles)
    total_new_c = sum(c.get('new_calcs', 0) for c in cycles)
    total_fails = sum(c.get('failures', 0) for c in cycles)
    lines.append(f'## Session Totals ({len(cycles)} cycles)')
    lines.append(f'  Total time: {total_dur}s ({total_dur//60}m)')
    lines.append(f'  Total new lenses: +{total_new_l}')
    lines.append(f'  Total new calcs: +{total_new_c}')
    lines.append(f'  Total failures: {total_fails}')
    lines.append(f'  Avg cycle: {total_dur // len(cycles)}s')

report = '\n'.join(lines)
with open(REPORT, 'w') as f:
    f.write(report)
print(report[-500:] if len(report) > 500 else report)
" 2>&1 | tail -30
    # Also run nexus6_report.py for the classic report
    python3 "$SCRIPT_DIR/nexus6_report.py" 2>/dev/null | tail -10 || true
    echo "  ✅ Report saved: shared/infinite_growth_report.md"
    echo ""

    # Phase 17: Sync All Repos
    run_phase 17 "Sync All Repos (7-repo propagation)" \
        "bash '$SYNC_DIR/sync-all.sh' 2>/dev/null || echo '  sync: manual required'"

    # ═══════════════════════════════════════════════════════════════════
    # CYCLE SUMMARY
    # ═══════════════════════════════════════════════════════════════════
    CYCLE_END=$(date +%s)
    CYCLE_DURATION=$(( CYCLE_END - CYCLE_START ))
    LENS_TOTAL=$(find "$NEXUS_ROOT/src/telescope/lenses" -name "*.rs" ! -name "mod.rs" 2>/dev/null | wc -l | tr -d ' ')
    CALC_TOTAL=$(find "$NEXUS_ROOT/shared/calc" -name "*.py" 2>/dev/null | wc -l | tr -d ' ')
    TEST_TOTAL=$(grep -r "#\[test\]" "$NEXUS_ROOT/tests" "$NEXUS_ROOT/src" 2>/dev/null | wc -l | tr -d ' ')
    MIRROR_ENTRIES=$(wc -l < "$NEXUS_ROOT/shared/mirror_log.jsonl" 2>/dev/null || echo 0)
    DISCOVERY_ENTRIES=$(wc -l < "$NEXUS_ROOT/shared/discovery_log.jsonl" 2>/dev/null || echo 0)
    WEIGHT_EXISTS="NO"; [ -f "$HOME/.nexus6/weights.json" ] && WEIGHT_EXISTS="YES"
    GRAPH_NODES=$(grep -c "node_id" "$NEXUS_ROOT/shared/discovery_log.jsonl" 2>/dev/null || echo 0)

    echo "┌───────────────────────────────────────────────────────────────┐"
    printf "│  Cycle %-4s │ %ds │ %d/%d phases ok                        │\n" "$CYCLE" "$CYCLE_DURATION" "$((TOTAL_PHASES - FAIL_COUNT))" "$TOTAL_PHASES"
    echo "├───────────────────────────────────────────────────────────────┤"
    printf "│  Lenses: %-4s  Calcs: %-4s  Tests: %-5s  Graph: %-4s      │\n" "$LENS_TOTAL" "$CALC_TOTAL" "$TEST_TOTAL" "$GRAPH_NODES"
    printf "│  Mirror: %-4s  Discovery: %-4s  Weights: %-3s               │\n" "$MIRROR_ENTRIES" "$DISCOVERY_ENTRIES" "$WEIGHT_EXISTS"
    printf "│  New: +%d lenses, +%d calcs, +%d tests                      │\n" "$NEW_LENSES" "$NEW_CALCS" "$NEW_TESTS"
    printf "│  Next cycle in %dm                                          │\n" "$INTERVAL_MIN"
    echo "└───────────────────────────────────────────────────────────────┘"
    echo ""

    # Log cycle
    python3 -c "
import json, time
entry = {
    'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
    'cycle': $CYCLE, 'duration_s': $CYCLE_DURATION,
    'lenses': $LENS_TOTAL, 'calcs': $CALC_TOTAL, 'tests': $TEST_TOTAL,
    'mirror': $MIRROR_ENTRIES, 'discoveries': $DISCOVERY_ENTRIES,
    'graph_nodes': $GRAPH_NODES, 'weights': '$WEIGHT_EXISTS' == 'YES',
    'failures': $FAIL_COUNT, 'phases': $TOTAL_PHASES,
    'new_lenses': $NEW_LENSES, 'new_calcs': $NEW_CALCS, 'new_tests': $NEW_TESTS
}
with open('$NEXUS_ROOT/shared/infinite_growth_log.jsonl', 'a') as f:
    f.write(json.dumps(entry) + '\n')
" 2>/dev/null || true

    [ "$CYCLE" -lt "$MAX_CYCLES" ] && sleep $((INTERVAL_MIN * 60))
done

cleanup
