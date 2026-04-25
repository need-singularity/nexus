#!/usr/bin/env bash
# tool/hexa_runtime_check.sh — Tier-1 i2 from improvement_ideas_omega_cycle (2026-04-26)
#
# hexa runtime health watchdog. self-host 회피 — hexa 없이 작동.
# 본 세션 (2026-04-26) 발견 issue: hexa.real silent fail (exit 137 SIGKILL on hello world).
# Mac memory pressure 또는 runtime crash 시 모든 hexa-based 도구 dead → 본 도구가
# 첫 indicator + recovery hint 제공.
#
# usage: tool/hexa_runtime_check.sh [--verbose] [--recover-hint]
# exit codes: 0 = healthy, 1 = usage, 2 = wrapper missing, 3 = real binary missing,
#             4 = real binary exists but exec fails, 5 = simple test fails
# sentinel: __HEXA_RUNTIME_CHECK__ PASS|FAIL stage=<N> reason=<...>
# origin: design/hexa_sim/2026-04-26_improvement_ideas_omega_cycle.json axis_i2

set -uo pipefail

VERBOSE=0
RECOVER_HINT=0
for arg in "$@"; do
    case "$arg" in
        --verbose|-v) VERBOSE=1 ;;
        --recover-hint) RECOVER_HINT=1 ;;
        --help|-h)
            echo "usage: $0 [--verbose] [--recover-hint]"
            echo "  --verbose       per-stage output"
            echo "  --recover-hint  on FAIL, emit recovery commands"
            echo "exit: 0 healthy / 1 usage / 2-5 various failures"
            echo "sentinel: __HEXA_RUNTIME_CHECK__ PASS|FAIL stage=<N> reason=<...>"
            exit 0
            ;;
        *)
            echo "unknown arg: $arg" >&2
            exit 1
            ;;
    esac
done

emit_pass() {
    local stage="$1"
    local detail="$2"
    if [ "$VERBOSE" = "1" ]; then
        echo "  [stage $stage] PASS — $detail"
    fi
}

emit_fail() {
    local stage="$1"
    local reason="$2"
    local code="$3"
    echo "__HEXA_RUNTIME_CHECK__ FAIL stage=$stage reason=\"$reason\""
    if [ "$RECOVER_HINT" = "1" ]; then
        echo "RECOVERY HINT:"
        case "$stage" in
            2) echo "  - hexa wrapper missing at \$HOME/core/hexa-lang/hexa"
               echo "  - check: ls -la \$HOME/core/hexa-lang/hexa"
               echo "  - re-clone: cd \$HOME/core && git clone <hexa-lang-repo>" ;;
            3) echo "  - hexa.real binary missing at \$HOME/core/hexa-lang/build/hexa.real"
               echo "  - check: ls -la \$HOME/core/hexa-lang/build/hexa.real"
               echo "  - rebuild: cd \$HOME/core/hexa-lang && make rebuild OR docker hexa-runner build" ;;
            4) echo "  - hexa.real exists but exec fails (exit 137 = SIGKILL, often macOS memory pressure)"
               echo "  - free memory: sudo purge   OR   kill heavy processes (Activity Monitor)"
               echo "  - reboot may be needed if persistent"
               echo "  - macOS sandbox check: spctl --status; codesign --verify \$HOME/core/hexa-lang/build/hexa.real" ;;
            5) echo "  - hexa.real runs but simple test fails — likely interp/dispatch bug"
               echo "  - rebuild: cd \$HOME/core/hexa-lang && make rebuild"
               echo "  - check git status for uncommitted breaking changes" ;;
        esac
    fi
    exit "$code"
}

# Stage 1: env basics
HOME_DIR="${HOME:-/Users/ghost}"
WRAPPER="$HOME_DIR/core/hexa-lang/hexa"
REAL_BIN="$HOME_DIR/core/hexa-lang/build/hexa.real"
emit_pass 1 "HOME=$HOME_DIR resolved"

# Stage 2: wrapper script presence
if [ ! -x "$WRAPPER" ]; then
    emit_fail 2 "wrapper not found at $WRAPPER" 2
fi
emit_pass 2 "wrapper exists at $WRAPPER ($(ls -la "$WRAPPER" | awk '{print $5}') bytes)"

# Stage 3: real binary presence
if [ ! -x "$REAL_BIN" ]; then
    emit_fail 3 "real binary not found at $REAL_BIN" 3
fi
REAL_SIZE=$(ls -la "$REAL_BIN" | awk '{print $5}')
REAL_MTIME=$(stat -f '%Sm' -t '%Y-%m-%d %H:%M' "$REAL_BIN" 2>/dev/null || stat -c '%y' "$REAL_BIN" 2>/dev/null | cut -c1-16)
emit_pass 3 "real binary exists ($REAL_SIZE bytes, mtime $REAL_MTIME)"

# Stage 4: real binary can exec
TEST_OUT=$("$REAL_BIN" --version 2>&1 || true)
TEST_EXIT=$?
if [ "$TEST_EXIT" = "137" ]; then
    emit_fail 4 "real binary exec exit 137 (SIGKILL — macOS killed, likely memory/sandbox)" 4
fi
if [ "$TEST_EXIT" = "139" ]; then
    emit_fail 4 "real binary exec exit 139 (SIGSEGV — segfault, rebuild needed)" 4
fi
emit_pass 4 "real binary exec exit=$TEST_EXIT"

# Stage 5: simple hello-world test
TMPHEX=$(mktemp -t hexa_check.XXXXX.hexa)
echo 'fn main() { println("hexa_alive") }' > "$TMPHEX"
HELLO_OUT=$(HEXA_RESOLVER_NO_REROUTE=1 "$WRAPPER" run "$TMPHEX" 2>&1)
HELLO_EXIT=$?
rm -f "$TMPHEX"

if [ "$HELLO_EXIT" = "137" ]; then
    # SIGKILL on hello-world but --version worked: macOS likely killing on memory/sandbox under load
    echo "__HEXA_RUNTIME_CHECK__ FAIL stage=5 reason=\"hello-world exit 137 SIGKILL (real binary dies under load — macOS memory/sandbox)\""
    if [ "$RECOVER_HINT" = "1" ]; then
        echo "RECOVERY HINT:"
        echo "  - hexa.real --version exits 0, but exec under load → exit 137 (SIGKILL)"
        echo "  - macOS killing process. Common causes:"
        echo "    1. memory pressure: sudo purge; close heavy apps; check Activity Monitor"
        echo "    2. sandbox/Gatekeeper: spctl -a \$HOME/core/hexa-lang/build/hexa.real"
        echo "    3. codesign drift after rebuild: codesign --verify --verbose \$HOME/core/hexa-lang/build/hexa.real"
        echo "    4. 4GB RSS cap (raw 36): hexa interp under-budgeted; rebuild needed"
        echo "  - workaround: HEXA_LOCAL=1 routes to remote (hetzner/ubu) when cgroup hard-cap available"
        echo "  - persistent: reboot Mac, re-test"
    fi
    exit 4
fi
if [ "$HELLO_EXIT" != "0" ]; then
    emit_fail 5 "hello-world exit=$HELLO_EXIT output: $HELLO_OUT" 5
fi
if [ "$HELLO_OUT" != "hexa_alive" ]; then
    emit_fail 5 "hello-world expected 'hexa_alive' got: '$HELLO_OUT'" 5
fi
emit_pass 5 "hello-world output='$HELLO_OUT'"

# All stages PASS
echo "__HEXA_RUNTIME_CHECK__ PASS stage=5 reason=\"hexa runtime healthy (wrapper + real + exec + hello)\""
exit 0
