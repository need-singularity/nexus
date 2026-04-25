#!/bin/bash
# beyond_omega_emit_capture_wrapper.sh — nxs-20260425-004 cycle 27
#
# REAL implementation of cycle 5's leftover task:
# cmd_omega 의 NEXUS_OMEGA emit 을 host-side 에서 직접 capture 해서
# state/ghost_ceiling_trace.append.jsonl 에 atomic append.
#
# cli/run.hexa 직접 변경 없음 (parallel session nxs-20260425-003 cycle 35-42 PSI
# threshold work 와 충돌 회피). external wrapper 방식.
#
# 사용:
#   bash tool/beyond_omega_emit_capture_wrapper.sh \
#       --engines hexa.real,hexa.real --variants 2 \
#       --seeds s1,s2 --max-rounds 1
#
# 환경변수 (cycle 4 envelope 호환):
#   GATE_LOCAL=1, HEXA_REMOTE_NO_REROUTE=1, NEXUS_DRILL_DEPTH=0,
#   NEXUS_DRILL_BUDGET_S=1, NEXUS_DRILL_HISTORY_OFF=1
#   NEXUS_OMEGA_CAPTURE_TIMEOUT=6 (default 6s)
#
# emit sink (host-side capture):
#   state/ghost_ceiling_trace.append.jsonl — JSON-per-line, NEXUS_OMEGA only,
#                                            schema {ts, event, axes, path, raw}.
# stderr passthrough: 원본 stderr 도 그대로 유지 (tee).

set -u

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APPEND_SINK="${REPO_DIR}/state/ghost_ceiling_trace.append.jsonl"
HEXA_REAL="${HEXA_REAL:-/Users/ghost/.hx/bin/hexa_real}"
NEXUS_RUN="${NEXUS_RUN:-/Users/ghost/.hx/packages/nexus/cli/run.hexa}"
[[ -f "$NEXUS_RUN" ]] || NEXUS_RUN="${REPO_DIR}/cli/run.hexa"
TIMEOUT_S="${NEXUS_OMEGA_CAPTURE_TIMEOUT:-6}"
KILL_AFTER_S="${NEXUS_OMEGA_CAPTURE_KILL_AFTER:-3}"

if [[ ! -x "$HEXA_REAL" ]]; then
    echo "FATAL: hexa_real not found at $HEXA_REAL" >&2
    exit 2
fi
if [[ ! -f "$NEXUS_RUN" ]]; then
    echo "FATAL: nexus run.hexa not found at $NEXUS_RUN" >&2
    exit 2
fi

mkdir -p "$(dirname "$APPEND_SINK")"

# Parser: stdin lines → APPEND_SINK 에 NEXUS_OMEGA emit 만 atomic append.
# 동시 stderr passthrough (tee 효과). awk 사용 — sed 는 JSON escaping 취약.
parse_and_append() {
    local sink="$1"
    awk -v SINK="$sink" '
        BEGIN {
            "date -u +%Y-%m-%dT%H:%M:%SZ" | getline TS
            close("date -u +%Y-%m-%dT%H:%M:%SZ")
        }
        /NEXUS_OMEGA[[:space:]]+\{/ {
            # raw payload extract: 첫 { 부터 라인 끝까지
            payload = $0
            sub(/.*NEXUS_OMEGA[[:space:]]+/, "", payload)
            # event/axes/path field grep (best-effort, JSON 정식 parse 는 python 단)
            event = ""; axes = ""; path = ""
            if (match(payload, /"event":"[^"]*"/)) {
                event = substr(payload, RSTART+9, RLENGTH-10)
            }
            if (match(payload, /"axes":[0-9]+/)) {
                axes = substr(payload, RSTART+7, RLENGTH-7)
            }
            if (match(payload, /"path":"[^"]*"/)) {
                path = substr(payload, RSTART+8, RLENGTH-9)
            }
            # JSON line build (escape backslash + quote in raw)
            raw_esc = payload
            gsub(/\\/, "\\\\", raw_esc)
            gsub(/"/, "\\\"", raw_esc)
            line = "{\"ts\":\"" TS "\",\"event\":\"" event "\""
            if (axes != "") line = line ",\"axes\":" axes
            if (path != "") line = line ",\"path\":\"" path "\""
            line = line ",\"raw\":\"" raw_esc "\",\"source\":\"emit_capture_wrapper\"}"
            # atomic append (>>는 O_APPEND, single line write race-free)
            print line >> SINK
            close(SINK)
        }
        { print > "/dev/stderr" }
    '
}

START_TS=$(date +%s)
# 본 wrapper: stderr 만 tee 하면 됨. stdout 은 그대로 passthrough.
# Process substitution 으로 stderr 를 parser 에게 보내고 결과 stderr 도 보존.
# Note: process substitution 은 bash 전용 (#!/bin/bash 명시 — 호환).
GATE_LOCAL="${GATE_LOCAL:-1}" \
HEXA_REMOTE_NO_REROUTE="${HEXA_REMOTE_NO_REROUTE:-1}" \
HEXA_REMOTE_DISABLE="${HEXA_REMOTE_DISABLE:-1}" \
NEXUS_DRILL_DEPTH="${NEXUS_DRILL_DEPTH:-0}" \
NEXUS_DRILL_BUDGET_S="${NEXUS_DRILL_BUDGET_S:-1}" \
NEXUS_DRILL_HISTORY_OFF="${NEXUS_DRILL_HISTORY_OFF:-1}" \
timeout --kill-after=${KILL_AFTER_S}s ${TIMEOUT_S}s \
    "$HEXA_REAL" run "$NEXUS_RUN" omega "$@" \
    2> >(parse_and_append "$APPEND_SINK")
RC=$?
END_TS=$(date +%s)
ELAPSED=$((END_TS - START_TS))

echo "" >&2
echo "=== beyond_omega_emit_capture_wrapper result ===" >&2
echo "rc=$RC elapsed=${ELAPSED}s" >&2
echo "append_sink=$APPEND_SINK" >&2
if [[ -f "$APPEND_SINK" ]]; then
    LINES=$(wc -l < "$APPEND_SINK" | tr -d ' ')
    echo "append_sink_total_lines=$LINES" >&2
fi

exit $RC
