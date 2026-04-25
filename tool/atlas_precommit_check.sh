#!/usr/bin/env bash
# tool/atlas_precommit_check.sh — Tier-2 i14 from improvement_ideas_omega_cycle (2026-04-26)
#
# pre-commit guard 도구 — staged atlas 변경의 sanity check + diff summary emit.
# 사용자 결정에 따라 .git/hooks/pre-commit 으로 등록 가능 (default = manual run).
# raw 25 (concurrent-git-lock) 충돌 회피 — git 호출 최소화 + flock 사용.
# self-host 회피 (bash + git, no hexa dep).
#
# usage:
#   tool/atlas_precommit_check.sh                 # check current staged
#   tool/atlas_precommit_check.sh --install-hook  # install as .git/hooks/pre-commit
#   tool/atlas_precommit_check.sh --uninstall-hook
#
# checks:
#   1. atlas.n6 또는 atlas.append.* 변경 시 → diff summary
#   2. 새 entry 의 grade format 검증 (raw 70 schema-guard)
#   3. duplicate id detection (한 commit 내 같은 id 추가)
#   4. lock-aware (raw 25): .git/index.lock 존재 시 다른 git 작업 wait
#
# exit codes:
#   0 = no issues OR confirmation accepted
#   1 = usage
#   2 = atlas changes have issues (block commit if hook installed)
# sentinel: __ATLAS_PRECOMMIT__ PASS|FAIL added=N issues=I
# origin: design/hexa_sim/2026-04-26_improvement_ideas_omega_cycle.json axis_i14

set -uo pipefail

NEXUS_ROOT="${NEXUS_ROOT:-$HOME/core/nexus}"
HOOK_PATH="$NEXUS_ROOT/.git/hooks/pre-commit"

# ─── install/uninstall ─────────────────────────────────────────

install_hook() {
    if [ -f "$HOOK_PATH" ]; then
        # Check if already installed
        if grep -q "atlas_precommit_check.sh" "$HOOK_PATH" 2>/dev/null; then
            echo "hook already installed at $HOOK_PATH"
            return 0
        fi
        echo "WARN: existing pre-commit hook at $HOOK_PATH — backup to ${HOOK_PATH}.bak"
        cp "$HOOK_PATH" "${HOOK_PATH}.bak"
    fi
    cat > "$HOOK_PATH" <<'EOF'
#!/usr/bin/env bash
# Atlas pre-commit guard (installed by tool/atlas_precommit_check.sh)
exec "$(git rev-parse --show-toplevel)/tool/atlas_precommit_check.sh"
EOF
    chmod +x "$HOOK_PATH"
    echo "installed at $HOOK_PATH (existing → ${HOOK_PATH}.bak if any)"
    echo "to uninstall: $0 --uninstall-hook"
}

uninstall_hook() {
    if [ ! -f "$HOOK_PATH" ]; then
        echo "no hook at $HOOK_PATH"
        return 0
    fi
    if ! grep -q "atlas_precommit_check.sh" "$HOOK_PATH" 2>/dev/null; then
        echo "hook at $HOOK_PATH does not appear to be ours — refuse to remove"
        return 1
    fi
    if [ -f "${HOOK_PATH}.bak" ]; then
        mv "${HOOK_PATH}.bak" "$HOOK_PATH"
        echo "restored backup ${HOOK_PATH}.bak → $HOOK_PATH"
    else
        rm -f "$HOOK_PATH"
        echo "removed $HOOK_PATH (no backup found)"
    fi
}

# ─── check logic ───────────────────────────────────────────────

# raw 25 awareness: brief wait if .git/index.lock exists from another process
wait_for_lock() {
    local lock="$NEXUS_ROOT/.git/index.lock"
    local waited=0
    while [ -f "$lock" ] && [ "$waited" -lt 5 ]; do
        sleep 1
        waited=$((waited + 1))
    done
    if [ -f "$lock" ]; then
        echo "WARN: .git/index.lock present after ${waited}s wait — may be stale or another session active"
    fi
}

check_staged_atlas() {
    cd "$NEXUS_ROOT" || return 1

    # Get staged changes for atlas files
    local staged_files
    staged_files=$(git diff --cached --name-only -- 'n6/atlas.n6' 'n6/atlas.append.*.n6' 2>/dev/null)
    if [ -z "$staged_files" ]; then
        echo "__ATLAS_PRECOMMIT__ PASS added=0 issues=0 (no atlas files staged)"
        return 0
    fi

    echo "atlas pre-commit check — staged atlas files:"
    while IFS= read -r f; do
        echo "  $f"
    done <<< "$staged_files"
    echo ""

    # Per-type diff summary (use existing atlas_diff_per_type logic — inline subset)
    local total_add=0 total_del=0
    local p_add=0 c_add=0 f_add=0 l_add=0 r_add=0 s_add=0 x_add=0 m_add=0 t_add=0 e_add=0
    local seen_ids=""
    local dup_ids=""
    local invalid_grades=""

    while IFS= read -r line; do
        [ -z "$line" ] && continue
        local sign type id grade
        sign=$(echo "$line" | cut -c1)
        type=$(echo "$line" | sed -nE 's/^[+\-]@([PCFLRSXMTE]) .*/\1/p')
        [ -z "$type" ] && continue
        id=$(echo "$line" | sed -nE 's/^[+\-]@[PCFLRSXMTE] ([^ ]+) =.*/\1/p')
        grade=$(echo "$line" | sed -nE 's/.*\[([^]]+)\].*/\1/p')

        if [ "$sign" = "+" ]; then
            total_add=$((total_add + 1))
            case "$type" in
                P) p_add=$((p_add + 1)) ;;
                C) c_add=$((c_add + 1)) ;;
                F) f_add=$((f_add + 1)) ;;
                L) l_add=$((l_add + 1)) ;;
                R) r_add=$((r_add + 1)) ;;
                S) s_add=$((s_add + 1)) ;;
                X) x_add=$((x_add + 1)) ;;
                M) m_add=$((m_add + 1)) ;;
                T) t_add=$((t_add + 1)) ;;
                E) e_add=$((e_add + 1)) ;;
            esac
            # duplicate id detection (within staged additions)
            if [ -n "$id" ]; then
                if echo "$seen_ids" | grep -q "|$id|"; then
                    dup_ids="$dup_ids $id"
                else
                    seen_ids="$seen_ids|$id|"
                fi
            fi
            # grade format validation (very loose: digit + optional [*+token])
            if [ -n "$grade" ]; then
                if ! echo "$grade" | grep -qE '^[0-9]+(\.[0-9]+)?[\*\!\?]?(\+[A-Z_]+)*$'; then
                    invalid_grades="$invalid_grades $id:[$grade]"
                fi
            fi
        elif [ "$sign" = "-" ]; then
            total_del=$((total_del + 1))
        fi
    done < <(git diff --cached -- 'n6/atlas.n6' 'n6/atlas.append.*.n6' 2>/dev/null | grep -E '^[+\-]@[PCFLRSXMTE] ')

    echo "diff summary:"
    echo "  +$total_add  -$total_del  (P:+$p_add C:+$c_add F:+$f_add L:+$l_add R:+$r_add S:+$s_add X:+$x_add M:+$m_add T:+$t_add E:+$e_add)"

    local issue_count=0
    if [ -n "$dup_ids" ]; then
        echo "  ⚠️ duplicate ids in staged additions:$dup_ids"
        issue_count=$((issue_count + 1))
    fi
    if [ -n "$invalid_grades" ]; then
        echo "  ⚠️ invalid grade format:$invalid_grades"
        issue_count=$((issue_count + 1))
    fi

    echo ""
    if [ "$issue_count" -gt 0 ]; then
        echo "__ATLAS_PRECOMMIT__ FAIL added=$total_add issues=$issue_count"
        echo ""
        echo "to override (commit anyway), unset hook:"
        echo "  bash $0 --uninstall-hook"
        echo "  git commit ..."
        echo "  bash $0 --install-hook  # re-install"
        return 2
    fi
    echo "__ATLAS_PRECOMMIT__ PASS added=$total_add issues=0"
    return 0
}

# ─── dispatch ──────────────────────────────────────────────────

case "${1:-}" in
    --install-hook) install_hook; exit 0 ;;
    --uninstall-hook) uninstall_hook; exit 0 ;;
    --help|-h)
        echo "usage: $0                    # check staged atlas changes"
        echo "       $0 --install-hook     # install as .git/hooks/pre-commit"
        echo "       $0 --uninstall-hook   # restore backup or remove"
        exit 0
        ;;
    "") wait_for_lock; check_staged_atlas; exit $? ;;
    *) echo "unknown: $1" >&2; exit 1 ;;
esac
