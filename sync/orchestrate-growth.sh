#!/usr/bin/env bash
set -euo pipefail
# ═══════════════════════════════════════════════════════════════
# Ecosystem Growth Orchestrator — 자원 적응형 전 리포 관리
# ═══════════════════════════════════════════════════════════════
# 8 repos를 시간차로 발사, 자원 모니터링, 과부하 방지
# Usage: bash scripts/orchestrate_growth.sh [--kill] [--status]

# Source from nexus6/lib/ (central location)
NEXUS6_LIB="$(cd "$(dirname "$0")/../lib" && pwd)"
source "$NEXUS6_LIB/growth_common.sh"

ORCH_PID="/tmp/n6_orchestrator.pid"

# ── Repo definitions (priority order) ───────────────────────────
REPOS=(
    "n6-architecture:180"    # 3min — 핵심 리포
    "nexus6:300"             # 5min — 엔진
    "TECS-L:300"             # 5min — 이론
    "sedi:600"               # 10min
    "brainwire:600"          # 10min
    "anima:600"              # 10min
    "hexa-lang:600"          # 10min
    "fathom:600"             # 10min
    "papers:900"             # 15min — 가장 경량
)

kill_all() {
    echo "Killing all growth processes..."
    for pid in $(ps aux | grep 'infinite_growth.*max-cycles\|nexus6_growth_daemon' | grep -v grep | awk '{print $2}'); do
        kill "$pid" 2>/dev/null || true
    done
    rm -f /tmp/*growth*.pid /tmp/n6_infinite*.pid $HOME/.nexus6/daemon.pid 2>/dev/null
    rm -f "$ORCH_PID"
    echo "All stopped."
    exit 0
}

show_status() {
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║  Ecosystem Growth Status                                 ║"
    echo "╠═══════════════════════════════════════════════════════════╣"
    check_resources > /dev/null
    print_resources
    echo "║                                                           ║"
    local running=0
    for entry in "${REPOS[@]}"; do
        local repo="${entry%%:*}"
        local dir="$HOME/Dev/$repo"
        local script="$dir/scripts/infinite_growth.sh"
        local status="⚫ none"
        # Check common PID file patterns
        for pf in /tmp/${repo}_growth.pid /tmp/${repo,,}_growth.pid /tmp/n6_infinite_growth.pid /tmp/tecs_l_infinite_growth.pid; do
            if [ -f "$pf" ]; then
                local pid=$(cat "$pf" 2>/dev/null)
                if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
                    status="✅ PID $pid"
                    running=$((running + 1))
                    break
                fi
            fi
        done
        printf "║  %-17s %s\n" "$repo" "$status"
    done
    echo "║                                                           ║"
    echo "║  Running: $running / ${#REPOS[@]}                                      ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    exit 0
}

# ── Parse args ──────────────────────────────────────────────────
case "${1:-}" in
    --kill)   kill_all ;;
    --status) show_status ;;
esac

# ── Singleton ───────────────────────────────────────────────────
singleton_acquire "$ORCH_PID"

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  Ecosystem Growth Orchestrator                           ║"
echo "║  8 repos, adaptive intervals, resource-aware             ║"
echo "║  PID: $$                                                  ║"
echo "╚═══════════════════════════════════════════════════════════╝"

# ── Launch repos with staggered start ───────────────────────────
launched=0
for entry in "${REPOS[@]}"; do
    repo="${entry%%:*}"
    interval="${entry##*:}"
    dir="$HOME/Dev/$repo"
    script="$dir/scripts/infinite_growth.sh"

    if [ ! -f "$script" ]; then
        echo "  ⏭️  $repo: no growth script"
        continue
    fi

    # Resource gate — wait if overloaded
    check_resources > /dev/null
    local_interval=$(get_adaptive_interval)
    if [ "$local_interval" -gt "$interval" ]; then
        interval="$local_interval"
    fi

    # Launch
    (cd "$dir" && nohup bash "$script" --max-cycles 999 --interval "$interval" > /dev/null 2>&1 &)
    launched=$((launched + 1))
    echo "  🚀 $repo (interval ${interval}s)"

    # Stagger: 30s between launches to avoid stampede
    sleep 30
done

echo ""
echo "Launched $launched repos. Orchestrator exiting (daemons run independently)."
echo "  --status: check all"
echo "  --kill:   stop all"
