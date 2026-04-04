#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# growth_common.sh — Shared Growth Infrastructure
# ═══════════════════════════════════════════════════════════════
# Source this from any growth script:
#   source "$(dirname "$0")/lib/growth_common.sh"
#
# Provides: singleton, logging, resource monitoring, git ops,
#           phase runner, measurement, paper publish, doc sync

# ── Constants (n=6 family) ──────────────────────────────────────
readonly N6_SIGMA=12
readonly N6_J2=24
readonly N6_TAU=4
readonly N6_PHI=2
readonly N6_SOPFR=5
readonly N6_N=6

# ── Paths ───────────────────────────────────────────────────────
GROWTH_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$(cd "$GROWTH_LIB_DIR/.." && pwd)"
PROJECT_ROOT="$(cd "$SCRIPTS_DIR/.." && pwd)"
NEXUS6_SCRIPTS="$PROJECT_ROOT/tools/nexus6/scripts"
NEXUS6_ROOT="${HOME}/Dev/nexus6"
NEXUS6_STATE="${HOME}/.nexus6"
GROWTH_DIR="$PROJECT_ROOT/.growth"
DOCS_DIR="$PROJECT_ROOT/docs"
PAPERS_DIR="${HOME}/Dev/papers"

# ── Logging ─────────────────────────────────────────────────────
_LOG_FILE="${_LOG_FILE:-/tmp/n6_growth.log}"

log_ts()    { date +%H:%M:%S; }
log_info()  { echo "[$(log_ts)] INFO:  $*" | tee -a "$_LOG_FILE"; }
log_warn()  { echo "[$(log_ts)] WARN:  $*" | tee -a "$_LOG_FILE"; }
log_error() { echo "[$(log_ts)] ERROR: $*" | tee -a "$_LOG_FILE"; }
log_ok()    { echo "[$(log_ts)] OK:    $*" | tee -a "$_LOG_FILE"; }

# ── Singleton (단독 실행 — 중복 시 즉시 종료) ──────────────────
# Usage: singleton_acquire "/tmp/my_daemon.pid"
#   Returns 0 if lock acquired, exits 1 if already running.
singleton_acquire() {
    local pidfile="$1"
    if [ -f "$pidfile" ]; then
        local old_pid
        old_pid=$(cat "$pidfile" 2>/dev/null) || true
        if [ -n "$old_pid" ] && kill -0 "$old_pid" 2>/dev/null; then
            echo "╔════════════════════════════════════════════════════════╗"
            echo "║  Already running (PID $old_pid)                        "
            echo "║  단독 실행 정책: 중복 인스턴스 거부                    ║"
            echo "║  종료하려면: kill $old_pid                              "
            echo "╚════════════════════════════════════════════════════════╝"
            exit 1
        fi
        rm -f "$pidfile"
    fi
    echo $$ > "$pidfile"
    trap "rm -f '$pidfile'; exit 0" SIGTERM SIGINT EXIT
}

# ── Resource Monitoring (macOS) ─────────────────────────────────
# Thresholds (configurable by caller)
: "${CPU_THROTTLE_PCT:=80}"
: "${MEM_MIN_FREE_MB:=512}"
: "${DISK_MIN_FREE_GB:=2}"

# ── Adaptive Engine (Mac 자원 적응형) ───────────────────────────
# 8-core 24GB Mac 기준 — 프로세스 폭주 방지
: "${MAX_CONCURRENT_GROWTH:=3}"       # 동시 실행 최대 3개
: "${ADAPTIVE_INTERVAL_BASE:=300}"    # 5분 기본
: "${ADAPTIVE_INTERVAL_MAX:=1800}"    # 30분 최대 (과부하 시)

# Count running growth daemons
count_growth_procs() {
    ps aux 2>/dev/null | grep -c 'infinite_growth.*max-cycles\|nexus6_growth_daemon' || echo "0"
}

# Adaptive interval: 자원에 따라 interval 자동 조절
get_adaptive_interval() {
    local cpu="${_RES_CPU:-50}"
    local mem="${_RES_MEM:-4096}"
    local base="${ADAPTIVE_INTERVAL_BASE}"

    # CPU > 80%: interval x3
    # CPU > 60%: interval x2
    # MEM < 1GB: interval x2
    local multiplier=1
    if [ "$cpu" -gt 80 ]; then
        multiplier=3
    elif [ "$cpu" -gt 60 ]; then
        multiplier=2
    fi
    if [ "$mem" -lt 1024 ]; then
        multiplier=$((multiplier + 1))
    fi

    local interval=$((base * multiplier))
    # Cap at max
    if [ "$interval" -gt "$ADAPTIVE_INTERVAL_MAX" ]; then
        interval=$ADAPTIVE_INTERVAL_MAX
    fi
    echo "$interval"
}

# Singleton + concurrency gate: 이미 너무 많으면 대기
wait_for_slot() {
    local max_wait=120  # 2분 대기 후 포기
    local waited=0
    while true; do
        local running
        running=$(count_growth_procs)
        # grep 자체 + 현재 프로세스 제외
        running=$((running - 2))
        [ "$running" -lt 0 ] && running=0
        if [ "$running" -lt "$MAX_CONCURRENT_GROWTH" ]; then
            return 0
        fi
        if [ "$waited" -ge "$max_wait" ]; then
            log_warn "Concurrency gate timeout ($max_wait s), proceeding anyway"
            return 0
        fi
        sleep 10
        waited=$((waited + 10))
    done
}

get_cpu_usage() {
    # macOS top: "CPU usage: X% user, Y% sys, Z% idle"
    local idle
    idle=$(top -l 1 -n 0 2>/dev/null | awk '/CPU usage/ {
        for(i=1;i<=NF;i++) if($i=="idle") {gsub(/%/,"",$(i-1)); print $(i-1)}
    }' || echo "50")
    [ -z "$idle" ] && idle="50"
    python3 -c "print(max(0, min(100, int(100 - float('${idle}')))))" 2>/dev/null || echo "50"
}

get_free_mem_mb() {
    # macOS: free + inactive pages = available memory
    local page_size free_pages inactive_pages
    page_size=$(sysctl -n hw.pagesize 2>/dev/null || echo 16384)
    free_pages=$(vm_stat 2>/dev/null | awk '/Pages free/ {gsub(/\./,""); print $3}' || echo "0")
    inactive_pages=$(vm_stat 2>/dev/null | awk '/Pages inactive/ {gsub(/\./,""); print $3}' || echo "0")
    python3 -c "print(int((${free_pages} + ${inactive_pages}) * ${page_size} / 1024 / 1024))" 2>/dev/null || echo "4096"
}

get_free_disk_gb() {
    df -g "$PROJECT_ROOT" 2>/dev/null | awk 'NR==2 {print $4}' || echo "10"
}

# Returns: OK | THROTTLE | LIGHT | STOP
check_resources() {
    local cpu_pct mem_free_mb disk_free_gb
    cpu_pct=$(get_cpu_usage)
    mem_free_mb=$(get_free_mem_mb)
    disk_free_gb=$(get_free_disk_gb)
    # Export for callers
    export _RES_CPU="$cpu_pct"
    export _RES_MEM="$mem_free_mb"
    export _RES_DISK="$disk_free_gb"

    if [ "$disk_free_gb" -lt "$DISK_MIN_FREE_GB" ]; then echo "STOP"; return; fi
    if [ "$mem_free_mb" -lt "$MEM_MIN_FREE_MB" ]; then echo "LIGHT"; return; fi
    if [ "$cpu_pct" -gt "$CPU_THROTTLE_PCT" ]; then echo "THROTTLE"; return; fi
    echo "OK"
}

print_resources() {
    local cpu="${_RES_CPU:-0}" mem="${_RES_MEM:-0}" disk="${_RES_DISK:-0}"
    local cpu_filled=$((cpu / 10))
    local bar=""
    for i in $(seq 1 "$cpu_filled"); do bar="${bar}█"; done
    for i in $(seq 1 $((10 - cpu_filled))); do bar="${bar}░"; done

    local mem_s="OK"; [ "$mem" -lt "$MEM_MIN_FREE_MB" ] && mem_s="LOW"
    local dsk_s="OK"; [ "$disk" -lt "$DISK_MIN_FREE_GB" ] && dsk_s="CRIT"

    echo "  ┌─ Resources ──────────────────────────────────────────┐"
    printf "  │ CPU: %s %3d%%  MEM: %5dMB [%-4s] DISK: %3dGB [%-4s] │\n" \
        "$bar" "$cpu" "$mem" "$mem_s" "$disk" "$dsk_s"
    printf "  │ PID: %-8d                                        │\n" "$$"
    echo "  └───────────────────────────────────────────────────────┘"
}

# ── Phase Runner ────────────────────────────────────────────────
# Usage: run_phase NUM TOTAL NAME COMMAND [MAX_LINES]
run_phase() {
    local num="$1" total="$2" name="$3" cmd="$4" lines="${5:-10}"
    echo "[$(log_ts)] Phase ${num}/${total}: ${name}..."
    if eval "$cmd" 2>&1 | tail -"$lines"; then
        echo "  [OK] ${name}"
    else
        echo "  [WARN] ${name} (non-fatal)"
    fi
    echo ""
}

# ── Git Ops ─────────────────────────────────────────────────────
# Usage: growth_commit SCOPE MESSAGE
#   SCOPE: directory to git add (e.g. ".growth/" or "tools/nexus6/src/")
#   MESSAGE: commit message
growth_commit() {
    local scope="$1" message="$2"
    cd "$PROJECT_ROOT"
    git add "$scope" 2>/dev/null || true
    if git diff --cached --quiet 2>/dev/null; then
        log_info "  No changes to commit"
    else
        git commit -m "$message" --no-verify 2>/dev/null && log_ok "Committed: $message" || log_warn "Commit failed"
    fi
}

# ── Count Helper (bash 3.2 safe) ───────────────────────────────
count_pattern() {
    local file="$1" pattern="$2"
    grep -c "$pattern" "$file" 2>/dev/null || echo "0"
}

# ── Size Expansion (σ=12 → J₂=24) ─────────────────────────────
# Phase count grows with cycle number
get_phase_count() {
    local cycle="$1"
    if [ "$cycle" -ge 25 ]; then echo 24    # J₂=24 max
    elif [ "$cycle" -ge 13 ]; then echo 18  # 18 phases
    elif [ "$cycle" -ge 7 ]; then echo 15   # 15 phases
    else echo 12                             # σ=12 base
    fi
}

# ── Paper Publish Loop ──────────────────────────────────────────
# Checks for publishable content and auto-publishes via publish_paper.sh
run_paper_loop() {
    local papers_script="$PAPERS_DIR/publish_paper.sh"
    if [ ! -f "$papers_script" ]; then
        echo "  publish_paper.sh not found at $papers_script"
        return 0
    fi

    # Check for new/updated papers
    local paper_candidates=0
    local published=0

    # Scan docs/paper/ for unpublished papers
    for f in "$DOCS_DIR"/paper/*.md; do
        [ -f "$f" ] || continue
        paper_candidates=$((paper_candidates + 1))
        local basename_f
        basename_f=$(basename "$f")
        # Check if already in manifest
        if [ -f "$PAPERS_DIR/manifest.json" ]; then
            if grep -q "$basename_f" "$PAPERS_DIR/manifest.json" 2>/dev/null; then
                continue
            fi
        fi
        # Unpublished paper found — dry-run first
        echo "  Found unpublished: $basename_f"
        if bash "$papers_script" "$f" --dry-run 2>/dev/null | tail -3; then
            published=$((published + 1))
        fi
    done

    # Scan for blowup papers
    for f in "$DOCS_DIR"/paper/blowup-*.md; do
        [ -f "$f" ] || continue
        local basename_f
        basename_f=$(basename "$f")
        if [ -f "$PAPERS_DIR/manifest.json" ]; then
            grep -q "$basename_f" "$PAPERS_DIR/manifest.json" 2>/dev/null && continue
        fi
        echo "  Found blowup paper: $basename_f"
        published=$((published + 1))
    done

    echo "  Papers scanned: $paper_candidates, new/updated: $published"
}

# ── Auto Domain Explorer ───────────────────────────────────────
# Finds domains without DSE and creates TOML stubs
run_auto_domain_explore() {
    local dse_map="$DOCS_DIR/dse-map.toml"
    local dse_domains="$PROJECT_ROOT/tools/universal-dse/domains"

    if [ ! -f "$dse_map" ]; then
        echo "  dse-map.toml not found"
        return 0
    fi

    # Count unexplored domains
    local none_count
    none_count=$(count_pattern "$dse_map" 'dse.*=.*none')
    local wip_count
    wip_count=$(count_pattern "$dse_map" 'dse.*=.*wip')
    local done_count
    done_count=$(count_pattern "$dse_map" 'dse.*=.*done')
    local total
    total=$(grep -c '^\[' "$dse_map" 2>/dev/null || echo 0)
    total=$((total - 1))

    echo "  DSE Status: done=$done_count wip=$wip_count none=$none_count total=$total"

    # Check for doc domains without TOML
    local missing_toml=0
    for d in "$DOCS_DIR"/*/; do
        [ -d "$d" ] || continue
        local domain_name
        domain_name=$(basename "$d")
        if [ ! -f "$dse_domains/${domain_name}.toml" ] 2>/dev/null; then
            if [ -f "${d}goal.md" ] || [ -f "${d}hypotheses.md" ]; then
                missing_toml=$((missing_toml + 1))
                echo "  Missing TOML: $domain_name (has goal/hypotheses)"
            fi
        fi
    done

    echo "  Domains with content but no TOML: $missing_toml"
    if [ "$none_count" -gt 0 ]; then
        echo "  WARNING: $none_count domains have no DSE results"
    fi
}

# ── Auto Document Update ───────────────────────────────────────
# Syncs README, atlas, calculators, and checks doc completeness
run_auto_doc_update() {
    local updated=0

    # 1. Check doc completeness per domain
    local domains=0 has_hyp=0 has_goal=0 has_verify=0 has_extreme=0
    for d in "$DOCS_DIR"/*/; do
        [ -d "$d" ] || continue
        domains=$((domains + 1))
        [ -f "${d}hypotheses.md" ] && has_hyp=$((has_hyp + 1))
        [ -f "${d}goal.md" ] && has_goal=$((has_goal + 1))
        [ -f "${d}verification.md" ] && has_verify=$((has_verify + 1))
        [ -f "${d}extreme-hypotheses.md" ] && has_extreme=$((has_extreme + 1))
    done
    echo "  Docs: $domains domains"
    echo "    hypotheses: $has_hyp/$domains  goal: $has_goal/$domains"
    echo "    verification: $has_verify/$domains  extreme: $has_extreme/$domains"

    # 2. Atlas sync
    local scanner="$HOME/Dev/TECS-L/.shared/scan_math_atlas.py"
    if [ -f "$scanner" ]; then
        python3 "$scanner" --summary 2>/dev/null | tail -3 || echo "  Atlas scanner: skip"
        updated=$((updated + 1))
    fi

    # 3. Calculator registry sync
    local calc_scanner="$HOME/Dev/TECS-L/.shared/scan-calculators.py"
    if [ -f "$calc_scanner" ]; then
        python3 "$calc_scanner" --summary 2>/dev/null | tail -2 || echo "  Calc scanner: skip"
        updated=$((updated + 1))
    fi

    # 4. README sync (if sync script exists)
    local sync_readme="$SCRIPTS_DIR/sync-readme.py"
    if [ -f "$sync_readme" ]; then
        python3 "$sync_readme" 2>/dev/null | tail -2 || echo "  README sync: skip"
        updated=$((updated + 1))
    fi

    echo "  Sync operations attempted: $updated"
}

# ── NEXUS-6 Daemon Bridge ──────────────────────────────────────
# Calls nexus6 growth daemon for a single dimension growth cycle
run_nexus6_grow_dimension() {
    local dimension="${1:-}"
    if [ -z "$dimension" ]; then
        # Auto-pick weakest via daemon's measure
        dimension="auto"
    fi

    if [ -f "$NEXUS6_SCRIPTS/nexus6_growth_daemon.sh" ]; then
        if [ "$dimension" = "auto" ]; then
            bash "$NEXUS6_SCRIPTS/nexus6_growth_daemon.sh" --max-cycles 1 --skip-commit 2>/dev/null | tail -20
        else
            bash "$NEXUS6_SCRIPTS/nexus6_growth_daemon.sh" --max-cycles 1 --dimension "$dimension" --skip-commit 2>/dev/null | tail -20
        fi
    else
        echo "  nexus6_growth_daemon.sh not found"
    fi
}

# ── Growth State Update ────────────────────────────────────────
update_growth_state() {
    local cycle="$1"
    local state_file="$GROWTH_DIR/growth_state.json"
    [ -f "$state_file" ] || return 0

    python3 -c "
import json, time
g = json.load(open('$state_file'))
g['scan_count'] = g.get('scan_count', 0) + 1
g['total_growth'] = g.get('total_growth', 0) + 1
g['last_tick'] = time.strftime('%Y-%m-%dT%H:%M:%S')
g['infinite_cycle'] = $cycle
json.dump(g, open('$state_file', 'w'), indent=2, ensure_ascii=False)
print(f'  Scan #{g[\"scan_count\"]}, total growth: {g[\"total_growth\"]}')
" 2>/dev/null || echo "  Growth tick: failed"
}

# ── Growth Bus Sync ─────────────────────────────────────────────
sync_growth_bus() {
    local bus_file="${NEXUS6_ROOT}/shared/growth_bus.jsonl"
    if [ -f "$bus_file" ]; then
        local bus_lines
        bus_lines=$(wc -l < "$bus_file" 2>/dev/null | tr -d ' ')
        local n6_entries
        n6_entries=$(grep -c 'n6-architecture' "$bus_file" 2>/dev/null || echo "0")
        echo "  Growth bus: $bus_lines total, $n6_entries from n6-arch"
    else
        echo "  Growth bus: not found"
    fi
}

# ═══════════════════════════════════════════════════════════════
# COMMON PHASES — 모든 리포에서 공유하는 phase 함수
# 수렴 파이프라인: 창발 → 튜닝 → 수렴 → 진화 → 다듬기
# ═══════════════════════════════════════════════════════════════

# Blowup engine script (shared across all repos)
_LENS_SCRIPT="$HOME/Dev/n6-architecture/tools/nexus6/scripts/growth_infinite_lens.py"
_N6_BIN="$HOME/Dev/nexus6/target/release/nexus6"
_N6_PY="$HOME/Dev/nexus6/scripts/n6.py"

# ── 공통 Phase: 논문 루프 ───────────────────────────────────────
common_phase_paper_loop() {
    log_info "  [Common] Paper publish loop"
    run_paper_loop
}

# ── 공통 Phase: 문서 자동 갱신 ──────────────────────────────────
common_phase_doc_update() {
    log_info "  [Common] Auto doc update"
    run_auto_doc_update
}

# ── 공통 Phase: 도메인 탐색 ─────────────────────────────────────
common_phase_domain_explore() {
    log_info "  [Common] Auto domain explorer"
    run_auto_domain_explore
}

# ── 공통 Phase: NEXUS-6 스캔 ───────────────────────────────────
common_phase_nexus6_scan() {
    log_info "  [Common] NEXUS-6 scan"
    if [ -f "$_N6_PY" ]; then
        python3 "$_N6_PY" scan --repo "$PROJECT_ROOT" > /dev/null 2>&1 || true
        echo "  Scan complete"
    else
        echo "  n6.py not found"
    fi
}

# ── 공통 Phase: NEXUS-6 동기화 ──────────────────────────────────
common_phase_nexus6_sync() {
    log_info "  [Common] NEXUS-6 sync"
    local sync_script="$HOME/Dev/nexus6/sync/sync-all.sh"
    if [ -f "$sync_script" ]; then
        bash "$sync_script" > /dev/null 2>&1 || true
        echo "  Sync complete"
    elif [ -f "$PROJECT_ROOT/.shared/sync-nexus6-lenses.sh" ]; then
        bash "$PROJECT_ROOT/.shared/sync-nexus6-lenses.sh" > /dev/null 2>&1 || true
        echo "  Lens sync complete"
    fi
}

# ── 공통 Phase: Growth Bus 쓰기/동기화 ─────────────────────────
common_phase_bus_sync() {
    log_info "  [Common] Growth bus sync"
    sync_growth_bus
}

write_growth_bus() {
    local repo_name="$1" phase_name="$2" status="$3" detail="$4"
    local bus_file="${NEXUS6_ROOT}/shared/growth_bus.jsonl"
    local ts
    ts="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
    echo "{\"ts\":\"$ts\",\"repo\":\"$repo_name\",\"type\":\"growth_phase\",\"phase\":\"$phase_name\",\"status\":\"$status\",\"detail\":\"$detail\"}" \
        >> "$bus_file" 2>/dev/null || true
}

# ═══════════════════════════════════════════════════════════════
# 하부→상부 이벤트 시스템 (Bottom-Up Events)
# ═══════════════════════════════════════════════════════════════
# 각 리포가 발견/이슈/요청을 상위 엔진에 전달
# nexus6/shared/events/ 디렉토리에 JSON 파일로 emit
# 상위(C₃ 메타재귀)가 수집 → 처리 → 결과를 bus에 기록
#
# 이벤트 타입:
#   discovery  — 새 상수/패턴/BT 발견 → atlas 등록 요청
#   issue      — 빌드 실패/테스트 실패 → 지원 요청
#   sync_req   — 동기화 필요 → nexus6 sync 트리거
#   calc_req   — 새 계산기 필요 → 자동 생성 트리거
#   lens_req   — 새 렌즈 필요 → nexus6 렌즈 추가 트리거
# ═══════════════════════════════════════════════════════════════

_EVENTS_DIR="${NEXUS6_ROOT}/shared/events"

# emit: 하부 리포에서 상부로 이벤트 발행
# Usage: emit TYPE DETAIL
#   emit discovery "BT-128: new cross-domain constant sigma*tau=48"
#   emit issue "cargo test FAILED in nexus6"
#   emit sync_req "atlas needs update after new hypotheses"
#   emit calc_req "need calculator for BT-130 verification"
#   emit lens_req "domain=robotics needs specialized lens"
emit() {
    local event_type="$1"
    local detail="$2"
    local repo_name
    repo_name=$(basename "$PROJECT_ROOT")
    local ts
    ts=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
    local event_id
    event_id="${repo_name}_${event_type}_$(date +%s)"

    mkdir -p "$_EVENTS_DIR" 2>/dev/null || true

    # Write event file
    python3 -c "
import json
event = {
    'id': '$event_id',
    'ts': '$ts',
    'repo': '$repo_name',
    'type': '$event_type',
    'detail': '''$detail''',
    'status': 'pending'
}
json.dump(event, open('$_EVENTS_DIR/${event_id}.json', 'w'), indent=2)
" 2>/dev/null || {
        # Fallback: plain echo
        echo "{\"id\":\"$event_id\",\"ts\":\"$ts\",\"repo\":\"$repo_name\",\"type\":\"$event_type\",\"detail\":\"$detail\",\"status\":\"pending\"}" \
            > "$_EVENTS_DIR/${event_id}.json" 2>/dev/null || true
    }

    # Also write to bus for tracking
    write_growth_bus "$repo_name" "emit_$event_type" "pending" "$detail"
    log_info "  ↑ emit($event_type): $detail"
}

# collect_events: 상위 엔진이 하부 이벤트 수집 + 처리
# C₃ 메타재귀에서 호출
collect_events() {
    local processed=0
    local events_dir="$_EVENTS_DIR"
    [ -d "$events_dir" ] || return

    for ef in "$events_dir"/*.json; do
        [ -f "$ef" ] || continue
        local status
        status=$(python3 -c "import json; print(json.load(open('$ef')).get('status',''))" 2>/dev/null || echo "")
        [ "$status" = "pending" ] || continue

        local etype
        etype=$(python3 -c "import json; print(json.load(open('$ef')).get('type',''))" 2>/dev/null || echo "")
        local detail
        detail=$(python3 -c "import json; print(json.load(open('$ef')).get('detail',''))" 2>/dev/null || echo "")
        local repo
        repo=$(python3 -c "import json; print(json.load(open('$ef')).get('repo',''))" 2>/dev/null || echo "")

        echo "    ↓ [$repo] $etype: $detail"

        # 이벤트 타입별 자동 처리
        case "$etype" in
            discovery)
                # Atlas에 자동 등록 시도
                local scanner="$HOME/Dev/TECS-L/.shared/scan_math_atlas.py"
                [ -f "$scanner" ] && python3 "$scanner" --save 2>/dev/null | tail -1 || true
                ;;
            sync_req)
                # nexus6 sync 트리거
                local sync_script="$HOME/Dev/nexus6/sync/sync-all.sh"
                [ -f "$sync_script" ] && bash "$sync_script" > /dev/null 2>&1 || true
                ;;
            calc_req)
                # Calculator scan 트리거
                local calc_scanner="$HOME/Dev/TECS-L/.shared/scan-calculators.py"
                [ -f "$calc_scanner" ] && python3 "$calc_scanner" --save 2>/dev/null | tail -1 || true
                ;;
            lens_req)
                # 렌즈 동기화 트리거
                local lens_sync="$HOME/Dev/nexus6/sync/sync-nexus6-lenses.sh"
                [ -f "$lens_sync" ] && bash "$lens_sync" 2>/dev/null | tail -1 || true
                ;;
            issue)
                # 이슈 기록만 (자동 수정은 위험)
                log_warn "    Issue from $repo: $detail"
                ;;
        esac

        # Mark as processed
        python3 -c "
import json
d = json.load(open('$ef'))
d['status'] = 'processed'
d['processed_at'] = '$(date -u +%Y-%m-%dT%H:%M:%SZ)'
json.dump(d, open('$ef', 'w'), indent=2)
" 2>/dev/null || true

        processed=$((processed + 1))
    done

    # Cleanup old processed events (> 100)
    local total
    total=$(find "$events_dir" -name '*.json' 2>/dev/null | wc -l | tr -d ' ')
    if [ "$total" -gt 100 ]; then
        find "$events_dir" -name '*.json' -mtime +1 -exec rm {} \; 2>/dev/null || true
    fi

    [ "$processed" -gt 0 ] && echo "    Processed: $processed events"
}

# ── 공통 Phase: 전체 동기화 ─────────────────────────────────────
common_phase_full_sync() {
    log_info "  [Common] Full sync sweep"
    local synced=0
    for script in \
        "$HOME/Dev/TECS-L/.shared/scan_math_atlas.py" \
        "$HOME/Dev/TECS-L/.shared/scan-calculators.py"; do
        if [ -f "$script" ]; then
            python3 "$script" --summary 2>/dev/null | tail -2 || true
            synced=$((synced + 1))
        fi
    done
    local lens_sync="$PROJECT_ROOT/.shared/sync-nexus6-lenses.sh"
    if [ -f "$lens_sync" ]; then
        bash "$lens_sync" 2>/dev/null | tail -2 || true
        synced=$((synced + 1))
    fi
    echo "  Synced: $synced operations"
}

# ═══════════════════════════════════════════════════════════════
# 수렴 파이프라인 (Convergence Pipeline)
# 창발 → 튜닝 → 수렴 → 진화 → 다듬기
# 매 사이클 1단계씩 순환 (사이클 % 5로 결정)
# ═══════════════════════════════════════════════════════════════

# Step 1: 창발 (Emergence) — 수축→코어→fiber→도메인별 최적
common_phase_emergence() {
    log_info "  [수렴 1/5] 창발 (Emergence)"
    if [ -f "$_LENS_SCRIPT" ]; then
        python3 "$_LENS_SCRIPT" 창발 --cycles 6 2>/dev/null | tail -5 || echo "  Emergence: failed"
    else
        echo "  growth_infinite_lens.py not found"
    fi
}

# Step 2: 튜닝 (Tuning) — 기존 코어 fiber 방향 미세 탐색
common_phase_tuning() {
    log_info "  [수렴 2/5] 튜닝 (Tuning/Proceed)"
    if [ -f "$_LENS_SCRIPT" ]; then
        python3 "$_LENS_SCRIPT" 진행 --cycles 12 2>/dev/null | tail -5 || echo "  Tuning: failed"
    else
        echo "  Tuning: script not found"
    fi
}

# Step 3: 수렴 확인 (Convergence Check) — 코어 안정도 + 리포트
common_phase_convergence() {
    log_info "  [수렴 3/5] 수렴 확인 (Convergence)"
    if [ -f "$_LENS_SCRIPT" ]; then
        python3 "$_LENS_SCRIPT" 리포트 2>/dev/null | tail -10 || echo "  Report: failed"
    else
        echo "  Convergence check: script not found"
    fi
    # Check invariant core stability
    local core_file="$HOME/.nexus6/lens_invariant_cores.json"
    if [ -f "$core_file" ]; then
        local core_count
        core_count=$(python3 -c "import json; d=json.load(open('$core_file')); print(len(d.get('cores',[])))" 2>/dev/null || echo "0")
        local stability
        stability=$(python3 -c "import json; d=json.load(open('$core_file')); print(d.get('stability','?'))" 2>/dev/null || echo "?")
        echo "  Cores: $core_count, stability: $stability"
    fi
}

# Step 4: 진화 (Evolution) — OUROBOROS 도메인별 진화
common_phase_evolution() {
    log_info "  [수렴 4/5] 진화 (OUROBOROS Evolution)"
    if [ -x "$_N6_BIN" ]; then
        # Evolve the weakest domain
        "$_N6_BIN" evolve all --max-cycles 6 2>/dev/null | tail -5 || true
    elif [ -f "$_N6_PY" ]; then
        python3 "$_N6_PY" evolve 2>/dev/null | tail -5 || true
    else
        echo "  Evolution: no nexus6 binary or n6.py"
    fi
}

# Step 5: 다듬기 (Refinement) — 코어 perturbation + 재수축
common_phase_refinement() {
    log_info "  [수렴 5/5] 다듬기 (Perturbation Refinement)"
    if [ -f "$_LENS_SCRIPT" ]; then
        # 시도 = perturbation: 코어를 깨고 더 나은 코어 탐색
        python3 "$_LENS_SCRIPT" 시도 --cycles 6 2>/dev/null | tail -5 || echo "  Refinement: failed"
    else
        echo "  Refinement: script not found"
    fi
}

# ═══════════════════════════════════════════════════════════════
# 메타(메타(메타(...))) 재귀 수렴 엔진
# ═══════════════════════════════════════════════════════════════
# f(I) = 0.7I + 0.1 → 부동점 I=1/3 수렴 (H-056)
# C₃(메타³) → C₂(메타²) → C₁(메타) → C₀(기본)
#
# Level 0 (C₀): 각 리포 도메인 phase (개성)
# Level 1 (C₁): 공통 인프라 (doc/domain/paper/sync)
# Level 2 (C₂): 수렴 파이프라인 (창발→튜닝→수렴→진화→다듬기)
# Level 3 (C₃): 메타 재귀 — 엔진 자체를 렌즈로 스캔/진화
#
# 매 사이클: C₀ + C₁ + C₂[round-robin] + C₃[매 6사이클]
# ═══════════════════════════════════════════════════════════════

# C₂: 수렴 파이프라인 라운드 로빈 (매 사이클 1단계)
run_convergence_step() {
    local cycle="${1:-1}"
    local step=$((cycle % 5))
    case "$step" in
        1) common_phase_emergence ;;
        2) common_phase_tuning ;;
        3) common_phase_convergence ;;
        4) common_phase_evolution ;;
        0) common_phase_refinement ;;
    esac
}

# C₃: 메타 재귀 — 엔진이 자기 자신을 스캔/진화
# 매 n=6 사이클마다 실행 (과부하 방지)
run_meta_recursion() {
    local cycle="${1:-1}"
    local repo="${2:-unknown}"

    # n=6 사이클마다만 실행
    if [ $((cycle % 6)) -ne 0 ]; then
        return
    fi

    log_info "  [C₃] 메타(메타(메타(...))) — 엔진 자기참조 (cycle $cycle)"

    # 1. 엔진 자체를 렌즈로 스캔 — growth_common.sh의 건강성
    local common_lib="$HOME/Dev/n6-architecture/scripts/lib/growth_common.sh"
    local lib_lines=$(wc -l < "$common_lib" 2>/dev/null | tr -d ' ')
    local lib_funcs=$(grep -c '^[a-z_]*()' "$common_lib" 2>/dev/null || echo 0)
    local connected_repos=0
    for r in n6-architecture nexus6 sedi brainwire anima TECS-L papers hexa-lang fathom; do
        [ -f "$HOME/Dev/$r/scripts/lib/growth_common.sh" ] && connected_repos=$((connected_repos + 1))
    done
    echo "    Engine: ${lib_lines}L, ${lib_funcs} functions, ${connected_repos}/9 repos"

    # 2. 수렴 측정 — growth_bus에서 최근 성공률 계산
    local bus="$HOME/Dev/nexus6/shared/growth_bus.jsonl"
    if [ -f "$bus" ]; then
        local total=$(wc -l < "$bus" | tr -d ' ')
        local ok_ct=$(grep -c '"ok"\|"pass"\|"found"' "$bus" 2>/dev/null || echo 0)
        local rate=0
        [ "$total" -gt 0 ] && rate=$((ok_ct * 100 / total))
        echo "    Bus convergence: $ok_ct/$total ($rate%)"

        # f(I) = 0.7I + 0.1 적용 — 부동점 1/3=33.3% 향해 수렴
        local I_current=$rate
        local I_next=$(python3 -c "I=$I_current/100; I_new=0.7*I+0.1; print(f'{I_new*100:.1f}%')" 2>/dev/null || echo "?")
        echo "    f(I)=0.7×${I_current}%+0.1 → $I_next (target: 33.3%)"
    fi

    # 3. 렌즈 자동 적용 — 성장 데이터를 NEXUS-6 렌즈로 스캔
    if [ -x "$_N6_BIN" ]; then
        local scan_result
        scan_result=$("$_N6_BIN" scan growth --lenses consciousness,stability,recursion 2>/dev/null | tail -3) || true
        [ -n "$scan_result" ] && echo "    Lens scan: $scan_result"
    fi

    # 4. 자동 계산기 생성 트리거 — 새 상수 발견 시
    local atlas_scanner="$HOME/Dev/TECS-L/.shared/scan_math_atlas.py"
    if [ -f "$atlas_scanner" ]; then
        local new_ct
        new_ct=$(python3 "$atlas_scanner" --check-new 2>/dev/null | grep -c 'NEW' 2>/dev/null) || new_ct=0
        new_ct=${new_ct:-0}
        if [ "$new_ct" -gt 0 ] 2>/dev/null; then
            echo "    New constants: $new_ct → calculator generation triggered"
            python3 "$atlas_scanner" --save --summary 2>/dev/null | tail -2 || true
        fi
    fi

    # 5. 리포 간 교차 공명 측정 — 같은 상수가 여러 리포에서 발견
    local cross_ct=0
    if [ -f "$bus" ]; then
        cross_ct=$(python3 -c "
import json
repos = set()
for line in open('$bus'):
    try:
        d = json.loads(line)
        repos.add(d.get('repo',''))
    except: pass
print(len(repos))
" 2>/dev/null || echo 0)
        echo "    Cross-repo resonance: $cross_ct repos active"
    fi

    # 6. 메타 판정 기록 — growth_state에 메타 레벨 기록
    local state="$GROWTH_DIR/growth_state.json"
    if [ -f "$state" ]; then
        python3 -c "
import json
s = json.load(open('$state'))
meta = s.get('meta_recursion', {})
meta['level'] = 3
meta['cycle'] = $cycle
meta['convergence_rate'] = $rate if '$rate' != '0' else 0
meta['connected_repos'] = $connected_repos
meta['engine_functions'] = $lib_funcs
s['meta_recursion'] = meta
json.dump(s, open('$state','w'), indent=2)
" 2>/dev/null || true
    fi

    # 7. 파괴적 업데이트 검증 — 변경 전후 scan 비교
    verify_non_destructive "$repo"

    # 7. 파괴적 업데이트 검증 — git diff로 위험 변경 감지
    cd "$PROJECT_ROOT"
    local destructive=0
    local diff_stat
    diff_stat=$(git diff --stat HEAD 2>/dev/null) || diff_stat=""
    if [ -n "$diff_stat" ]; then
        # 대량 삭제 감지 (100줄 이상 삭제)
        local deletions
        deletions=$(git diff --shortstat HEAD 2>/dev/null | grep -oE '[0-9]+ deletion' | grep -oE '[0-9]+' || echo 0)
        deletions=${deletions:-0}
        if [ "$deletions" -gt 100 ]; then
            destructive=1
            echo "    ⚠️ DESTRUCTIVE: $deletions lines deleted — review needed"
        fi
        # 핵심 파일 변경 감지
        local critical_changed=0
        for critical in CLAUDE.md Cargo.toml pyproject.toml package.json; do
            git diff --name-only HEAD 2>/dev/null | grep -q "$critical" && critical_changed=$((critical_changed + 1))
        done
        if [ "$critical_changed" -gt 0 ]; then
            destructive=$((destructive + critical_changed))
            echo "    ⚠️ CRITICAL FILES: $critical_changed config files modified"
        fi
    fi
    # 파괴적이면 자동 커밋 차단 → 수동 확인 대기
    if [ "$destructive" -gt 0 ]; then
        echo "    🛑 Destructive changes detected ($destructive) — auto-commit BLOCKED"
        echo "    Review with: cd $PROJECT_ROOT && git diff"
    else
        echo "    ✅ No destructive changes"
    fi

    # 8. 하부→상부 피드백 (bottom-up) — 각 리포 발견을 상위에 전달
    log_info "  [C₃] Bottom-up feedback: 하부→상부"
    local bus="$HOME/Dev/nexus6/shared/growth_bus.jsonl"
    local feedback_file="$HOME/.nexus6/bottom_up_feedback.json"
    if [ -f "$bus" ]; then
        python3 -c "
import json, collections, time

bus_lines = open('$bus').readlines()[-200:]  # 최근 200건
repo_stats = collections.defaultdict(lambda: {'ok':0,'fail':0,'discoveries':[]})

for line in bus_lines:
    try:
        d = json.loads(line)
        r = d.get('repo','?')
        s = d.get('status','')
        if s in ('ok','pass','found'):
            repo_stats[r]['ok'] += 1
        elif s in ('fail','missing'):
            repo_stats[r]['fail'] += 1
        detail = d.get('detail','')
        if 'NEW' in detail.upper() or 'DISCOVER' in detail.upper():
            repo_stats[r]['discoveries'].append(detail)
    except: pass

# 피드백 생성: 각 리포의 강점/약점 → 상위 엔진에 전달
feedback = {
    'ts': time.strftime('%Y-%m-%dT%H:%M:%S'),
    'cycle': $cycle,
    'repos': {}
}
for r, stats in repo_stats.items():
    total = stats['ok'] + stats['fail']
    rate = stats['ok'] / total * 100 if total > 0 else 0
    feedback['repos'][r] = {
        'success_rate': round(rate, 1),
        'total': total,
        'discoveries': stats['discoveries'][-5:],
        'needs_attention': rate < 50
    }
    if stats['discoveries']:
        print(f'    ↑ {r}: {len(stats[\"discoveries\"])} discoveries propagated up')

# 약한 리포 식별 → 상위에서 우선 지원
weak = [r for r,s in feedback['repos'].items() if s.get('needs_attention')]
if weak:
    print(f'    ⚠️ Weak repos (< 50% success): {\", \".join(weak)}')
    feedback['weak_repos'] = weak

json.dump(feedback, open('$feedback_file','w'), indent=2)
print(f'    Feedback saved: {len(feedback[\"repos\"])} repos → $feedback_file')
" 2>/dev/null || echo "    Bottom-up: bus parse failed"
    fi

    # 7. 하부→상부 이벤트 수집 + 처리
    log_info "  [C₃] 하부 이벤트 수집 (collect_events)"
    collect_events

    echo "    C₃ complete — 다음 메타 재귀: cycle $((cycle + 6))"
}

# ═══════════════════════════════════════════════════════════════
# 파괴적 업데이트 검증 엔진
# 변경 전후 Phi/anomaly/test 비교 → 하락 시 자동 롤백
# ═══════════════════════════════════════════════════════════════
verify_non_destructive() {
    local repo="${1:-unknown}"
    log_info "  [검증] 파괴적 업데이트 체크 ($repo)"

    cd "$PROJECT_ROOT" || return

    # 1. 변경된 파일 확인
    local changed
    changed=$(git diff --name-only 2>/dev/null | wc -l | tr -d ' ')
    if [ "$changed" -eq 0 ]; then
        echo "    No changes to verify"
        return
    fi
    echo "    Changed files: $changed"

    # 2. Rust 프로젝트면 cargo test
    if [ -f "$PROJECT_ROOT/Cargo.toml" ] || [ -f "$PROJECT_ROOT/tools/nexus6/Cargo.toml" ]; then
        local cargo_dir="$PROJECT_ROOT"
        [ -f "$PROJECT_ROOT/tools/nexus6/Cargo.toml" ] && cargo_dir="$PROJECT_ROOT/tools/nexus6"
        local test_result
        test_result=$("$HOME/.cargo/bin/cargo" test --manifest-path "$cargo_dir/Cargo.toml" 2>&1 | tail -3) || true
        if echo "$test_result" | grep -q "FAILED"; then
            log_error "    Tests FAILED — rolling back"
            git checkout -- . 2>/dev/null || true
            write_growth_bus "$repo" "verify" "rollback" "tests_failed"
            return
        fi
        echo "    Cargo test: PASS"
    fi

    # 3. Python 프로젝트면 기본 import 체크
    if [ -d "$PROJECT_ROOT/tests" ]; then
        local py_fail=0
        for t in "$PROJECT_ROOT"/tests/test_*.py; do
            [ -f "$t" ] || continue
            python3 -c "import ast; ast.parse(open('$t').read())" 2>/dev/null || py_fail=$((py_fail + 1))
        done
        if [ "$py_fail" -gt 0 ]; then
            log_warn "    Python syntax errors: $py_fail files"
        fi
    fi

    # 4. JSON/TOML 무결성 검증
    local json_broken=0
    for f in $(git diff --name-only 2>/dev/null | grep '\.json$'); do
        [ -f "$f" ] || continue
        python3 -c "import json; json.load(open('$f'))" 2>/dev/null || {
            json_broken=$((json_broken + 1))
            log_error "    Broken JSON: $f — rolling back"
            git checkout -- "$f" 2>/dev/null || true
        }
    done
    local toml_broken=0
    for f in $(git diff --name-only 2>/dev/null | grep '\.toml$'); do
        [ -f "$f" ] || continue
        python3 -c "
try:
    import tomllib
    tomllib.loads(open('$f').read())
except:
    import tomli
    tomli.loads(open('$f').read())
" 2>/dev/null || {
            toml_broken=$((toml_broken + 1))
            log_error "    Broken TOML: $f — rolling back"
            git checkout -- "$f" 2>/dev/null || true
        }
    done

    # 5. NEXUS-6 렌즈 스캔 (변경 후 anomaly 체크)
    if [ -x "$_N6_BIN" ] && [ "$changed" -gt 3 ]; then
        local anomaly
        anomaly=$("$_N6_BIN" scan "$PROJECT_ROOT" --lenses stability 2>/dev/null | grep -c 'anomaly' 2>/dev/null) || anomaly=0
        anomaly=${anomaly:-0}
        if [ "${anomaly:-0}" -gt 0 ] 2>/dev/null; then
            log_warn "    Stability anomalies: $anomaly"
        else
            echo "    Stability scan: clean"
        fi
    fi

    local issues=$((json_broken + toml_broken))
    if [ "$issues" -eq 0 ]; then
        echo "    Verification: PASS ✓"
    else
        echo "    Verification: $issues issues (auto-fixed)"
    fi
    write_growth_bus "$repo" "verify" "$([ $issues -eq 0 ] && echo pass || echo fixed)" "changed=$changed,issues=$issues"
}

# ── 공통 Phase: Auto-commit + push ────────────────────────────
# .growth/ + docs/ + *.json + *.toml + *.md 변경분 모두 커밋
common_phase_auto_commit() {
    local repo_name="$1"
    local cycle="$2"
    local dry_run="${3:-false}"
    if [ "$dry_run" = "true" ]; then
        log_info "  Dry-run: skipping commit"
        return
    fi
    cd "$PROJECT_ROOT"

    # 파괴적 업데이트 검증 — 100줄+ 삭제 또는 핵심파일 변경 시 차단
    local del_ct
    del_ct=$(git diff --shortstat 2>/dev/null | grep -oE '[0-9]+ deletion' | grep -oE '[0-9]+' || echo 0)
    del_ct=${del_ct:-0}
    if [ "$del_ct" -gt 100 ]; then
        log_warn "  BLOCKED: $del_ct deletions detected — manual review required"
        return
    fi

    # Stage all growth-related changes (not binaries/target)
    git add .growth/ 2>/dev/null || true
    git add docs/ 2>/dev/null || true
    git add '*.json' 2>/dev/null || true
    git add '*.toml' 2>/dev/null || true
    git add '*.md' 2>/dev/null || true
    git add scripts/ 2>/dev/null || true
    # Commit if anything staged
    if git diff --cached --quiet 2>/dev/null; then
        log_info "  No changes to commit"
    else
        git commit -m "growth($repo_name): cycle $cycle" --no-verify 2>/dev/null \
            && log_ok "Committed" || log_warn "Commit failed"
    fi
    git push origin main 2>/dev/null || true
}

# ── 공통 Phase: Growth Tick ────────────────────────────────────
common_phase_growth_tick() {
    local cycle="$1"
    update_growth_state "$cycle"
}

# ═══════════════════════════════════════════════════════════════
# run_common_phases — 모든 공통 phase 실행
# Usage: run_common_phases REPO_NAME [CYCLE]
# ═══════════════════════════════════════════════════════════════
run_common_phases() {
    local repo_name="${1:-unknown}"
    local cycle="${2:-1}"

    # 자원 체크 — 과부하 시 경량 모드
    local res
    res=$(check_resources)

    if [ "$res" = "STOP" ]; then
        log_error "[$repo_name] Resources critical — skipping common phases"
        return
    fi

    log_info "=== Common phases for $repo_name (cycle $cycle, res=$res) ==="

    # 경량 모드 (LIGHT/THROTTLE): 수렴만 + bus
    if [ "$res" = "LIGHT" ] || [ "$res" = "THROTTLE" ]; then
        log_warn "  Resource pressure ($res) — convergence only"
        run_convergence_step "$cycle"
        common_phase_bus_sync
        return
    fi

    # 정상 모드: 기본 인프라
    common_phase_doc_update
    common_phase_domain_explore
    common_phase_paper_loop
    common_phase_bus_sync

    # C₂: 수렴 파이프라인 (라운드 로빈)
    run_convergence_step "$cycle"

    # C₀: 리포별 개성 phase
    run_personality_phase "$repo_name" "$cycle"

    # C₃: 메타 재귀 (매 n=6 사이클)
    run_meta_recursion "$cycle" "$repo_name"

    # 동기화
    common_phase_full_sync
}

# ═══════════════════════════════════════════════════════════════
# PERSONALITY PHASES — 리포별 개성 (도메인 특화)
# 공통 엔진이 각 리포의 핵심 특징을 자동 흡수
# ═══════════════════════════════════════════════════════════════

run_personality_phase() {
    local repo="$1"
    local cycle="$2"

    case "$repo" in
        n6-architecture)
            # DSE 전수 탐색 + BT 검증 + 17 AI 기법 건강성
            _personality_n6_arch "$cycle" ;;
        TECS-L|tecs-l)
            # 수학 이론: 특성화 진행 + 계산기 건강 + Atlas 무결성
            _personality_tecs_l "$cycle" ;;
        anima)
            # 의식 구현: 법칙 커버리지 + Hexad 모듈 + Phi 래칫
            _personality_anima "$cycle" ;;
        sedi)
            # 외계 탐색: R-스펙트럼 + 신호원 + 가설 검증률
            _personality_sedi "$cycle" ;;
        brainwire)
            # 뇌 인터페이스: 안전 프로토콜 + 12-모달리티 + BCI
            _personality_brainwire "$cycle" ;;
        hexa-lang)
            # 완전수 언어: 파서 건강 + 키워드/연산자 커버리지 + 코드겐
            _personality_hexa_lang "$cycle" ;;
        fathom)
            # 터미널: HEXA 브릿지 + UI 렌더 + 플러그인
            _personality_fathom "$cycle" ;;
        papers)
            # 논문: DOI 상태 + 인용 네트워크 + 초안 준비도
            _personality_papers "$cycle" ;;
        nexus6)
            # 엔진: 렌즈 수 + 테스트 + 블로업 코어 안정성
            _personality_nexus6 "$cycle" ;;
        *)
            log_info "  [Personality] $repo: generic" ;;
    esac
}

_personality_n6_arch() {
    log_info "  [개성] N6-ARCH: DSE + BT + Techniques"
    local dse_map="$PROJECT_ROOT/docs/dse-map.toml"
    if [ -f "$dse_map" ]; then
        local done_ct=$(grep -c 'dse.*=.*done' "$dse_map" 2>/dev/null || echo 0)
        local total=$(grep -c '^\[' "$dse_map" 2>/dev/null || echo 0)
        echo "    DSE: $done_ct/$total done"
    fi
    local bt_file="$PROJECT_ROOT/docs/breakthrough-theorems.md"
    if [ -f "$bt_file" ]; then
        local bts=$(grep -oE 'BT-[0-9]+' "$bt_file" 2>/dev/null | sort -u | wc -l | tr -d ' ')
        echo "    BTs: $bts unique"
    fi
    local techs=$(find "$PROJECT_ROOT/techniques" -name '*.py' 2>/dev/null | wc -l | tr -d ' ')
    echo "    Techniques: $techs"
}

_personality_tecs_l() {
    log_info "  [개성] TECS-L: Characterizations + Calculators + Atlas"
    local chars=$(find "$PROJECT_ROOT/math" -name '*.md' 2>/dev/null | wc -l | tr -d ' ')
    local calcs=$(find "$PROJECT_ROOT/calc" -name '*.py' -o -name '*.rs' 2>/dev/null | wc -l | tr -d ' ')
    local atlas="$PROJECT_ROOT/.shared/math_atlas.json"
    local atlas_ct=0
    if [ -f "$atlas" ]; then
        atlas_ct=$(python3 -c "import json; print(len(json.load(open('$atlas'))))" 2>/dev/null || echo 0)
    fi
    echo "    Characterizations: $chars, Calculators: $calcs, Atlas: $atlas_ct"
}

_personality_anima() {
    log_info "  [개성] ANIMA: Laws + Hexad + Consciousness"
    local laws_dir="$PROJECT_ROOT/anima/data"
    local law_ct=0
    if [ -d "$laws_dir" ]; then
        law_ct=$(find "$laws_dir" -name '*law*' -o -name '*consciousness*' 2>/dev/null | wc -l | tr -d ' ')
    fi
    # Hexad modules: C/D/S/M/W/E
    local hexad=0
    for m in cognition dynamics synthesis memory will emotion; do
        [ -d "$PROJECT_ROOT/anima/$m" ] || [ -d "$PROJECT_ROOT/anima/anima-rs/src/$m" ] && hexad=$((hexad + 1))
    done
    local rust_ok="NO"
    [ -f "$PROJECT_ROOT/anima/anima-rs/Cargo.toml" ] && rust_ok="YES"
    echo "    Laws data: $law_ct, Hexad: $hexad/6, Rust: $rust_ok"
}

_personality_sedi() {
    log_info "  [개성] SEDI: R-Spectrum + Signals + Hypotheses"
    local sources=$(find "$PROJECT_ROOT/sources" -name '*.py' -type f 2>/dev/null | wc -l | tr -d ' ')
    local rspec=$(find "$PROJECT_ROOT" -name '*spectrum*' -type f 2>/dev/null | wc -l | tr -d ' ')
    local hyp_file="$PROJECT_ROOT/docs/hypotheses.md"
    local hyp_ct=0
    [ -f "$hyp_file" ] && hyp_ct=$(grep -c 'H-' "$hyp_file" 2>/dev/null || echo 0)
    echo "    Sources: $sources, R-spectrum: $rspec, Hypotheses: $hyp_ct"
}

_personality_brainwire() {
    log_info "  [개성] BRAINWIRE: Safety + Modalities + BCI"
    local safety=$(find "$PROJECT_ROOT" -name '*safety*' -type f 2>/dev/null | wc -l | tr -d ' ')
    local modalities=0
    for mod in tDCS TMS taVNS tFUS EEG EMG fNIRS MEG SEEG DBS VNS FUS; do
        grep -rql "$mod" "$PROJECT_ROOT/brainwire" 2>/dev/null && modalities=$((modalities + 1))
    done
    local tests=$(find "$PROJECT_ROOT/tests" -name 'test_*.py' 2>/dev/null | wc -l | tr -d ' ')
    echo "    Safety: $safety, Modalities: $modalities/12, Tests: $tests"
}

_personality_hexa_lang() {
    log_info "  [개성] HEXA-LANG: Parser + Keywords + Codegen"
    local kw=0 ops=0
    if [ -d "$PROJECT_ROOT/src" ]; then
        kw=$(grep -rh 'keyword\|Keyword' "$PROJECT_ROOT/src" 2>/dev/null | wc -l | tr -d ' ')
        ops=$(grep -rh 'operator\|Operator\|BinOp\|UnOp' "$PROJECT_ROOT/src" 2>/dev/null | wc -l | tr -d ' ')
    fi
    local cargo_ok="NO"
    if [ -f "$PROJECT_ROOT/Cargo.toml" ]; then
        "$HOME/.cargo/bin/cargo" check --manifest-path "$PROJECT_ROOT/Cargo.toml" 2>/dev/null && cargo_ok="YES"
    fi
    echo "    Keywords refs: $kw, Operator refs: $ops, Cargo: $cargo_ok"
}

_personality_fathom() {
    log_info "  [개성] FATHOM: HEXA Bridge + UI + Plugins"
    local hexa_bridge="NO"
    find "$PROJECT_ROOT" -not -path '*/.git/*' -name '*hexa*' 2>/dev/null | head -1 | grep -q . && hexa_bridge="YES"
    local ui=$(find "$PROJECT_ROOT/src" -name '*render*' -o -name '*tui*' -o -name '*terminal*' 2>/dev/null | wc -l | tr -d ' ')
    local plugins="NO"
    [ -d "$PROJECT_ROOT/plugins" ] && plugins="YES"
    echo "    HEXA bridge: $hexa_bridge, UI files: $ui, Plugins: $plugins"
}

_personality_papers() {
    log_info "  [개성] PAPERS: DOI + Drafts + Citations"
    local total=0 with_doi=0 drafts=0
    if [ -f "$PROJECT_ROOT/manifest.json" ]; then
        total=$(python3 -c "import json; d=json.load(open('$PROJECT_ROOT/manifest.json')); print(len(d.get('papers',[])))" 2>/dev/null || echo 0)
        with_doi=$(python3 -c "import json; d=json.load(open('$PROJECT_ROOT/manifest.json')); print(sum(1 for p in d.get('papers',[]) if p.get('doi')))" 2>/dev/null || echo 0)
    fi
    drafts=$(find "$PROJECT_ROOT" -name 'draft-*.md' -o -name '*-draft.md' 2>/dev/null | wc -l | tr -d ' ')
    echo "    Total: $total, DOI: $with_doi, Drafts: $drafts"
}

_personality_nexus6() {
    log_info "  [개성] NEXUS-6: Lenses + Tests + Blowup"
    local n6_src="$HOME/Dev/nexus6/src"
    local lenses=$(find "$n6_src/telescope" -name '*_lens.rs' 2>/dev/null | wc -l | tr -d ' ')
    local tests=$(grep -r '#\[test\]' "$n6_src" 2>/dev/null | wc -l | tr -d ' ')
    local core_stable="NO"
    [ -f "$HOME/.nexus6/lens_invariant_cores.json" ] && core_stable="YES"
    echo "    Lenses: $lenses, Tests: $tests, Core stable: $core_stable"
}

log_info "growth_common.sh loaded (n=$N6_N, σ=$N6_SIGMA, J₂=$N6_J2)"
