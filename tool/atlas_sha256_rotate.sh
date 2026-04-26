#!/usr/bin/env bash
# tool/atlas_sha256_rotate.sh — R5 chain extension to atlas_sha256.tsv (2026-04-26)
#
# Detects atlas .n6 shards whose live SHA256 differs from the per-shard baseline
# in state/atlas_sha256.tsv. For each drift: rotates the TSV row (col 2 sha + col
# 3 lines + col 4 last_verified_utc) and appends a hash-chained ledger entry to
# state/atlas_sha256_rotation_log.jsonl using the same R5 OPT-D pattern as the
# falsifier registry rotation log (`prev_hash` = sha256(prev_line) | "genesis").
#
# Why a standalone tool (not a pre-commit hook):
#   .githooks/ was retired in commit e3137be2. R5 chain extension must honour that
#   decision. This tool is invokable by cron, manually, or by future automation —
#   without resurrecting the deleted hook. Mirrors bridge_sha256_rotate.sh.
#
# Modes:
#   default                  — scan + rotate any drift; print human summary + sentinel
#   --dry-run                — scan + report drift only; never mutate TSV/ledger
#   --shard PATH             — scan only the named shard (relative to NEXUS_ROOT, or
#                              absolute) e.g. --shard n6/atlas.append.forge-triple.n6
#   --reason <text>          — record per-rotation reason in ledger (raw 73 admissibility)
#   --quiet                  — sentinel only
#   --json                   — JSON summary on stdout
#
# Sentinel (raw 80, additive only):
#   __ATLAS_SHA256_ROTATE__ <ROTATED|SKIPPED|ERROR|EMPTY> shard=<basename> old=<sha> new=<sha>
#   followed by aggregate sentinel:
#   __ATLAS_ROTATE__ <PASS|FAIL|EMPTY> scanned=N rotated=K dry_run=<0|1>
#
# Exit:
#   0  all-clean OR rotation completed cleanly OR dry-run reporting drift
#   1  usage / infra error
#
# Compliance:
#   raw 66 — reason+fix trailers on every error path
#   raw 71 — REPORTS+ROTATES baseline only; never modifies n6/atlas*.n6 contents
#   raw 73 — minimal: bash 3.2 portable, no python required
#   raw 77 — additive: leaves untouched TSV rows + comment lines verbatim
#   raw 80 — sentinel evolution backward-compat (new tool ⇒ no prior surface to break)
#
# Verify chain integrity afterwards with:
#   bash tool/ledger_verify.sh --ledger atlas

set -uo pipefail

NEXUS_ROOT="${NEXUS_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null)}"
if [ -z "${NEXUS_ROOT}" ] || [ ! -d "${NEXUS_ROOT}" ]; then
    NEXUS_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fi

ATLAS_TSV="${NEXUS_ROOT}/state/atlas_sha256.tsv"
ATLAS_LOG="${NEXUS_ROOT}/state/atlas_sha256_rotation_log.jsonl"

DRY_RUN=0
QUIET=0
JSON=0
ONLY_SHARD=""
REASON=""

while [ "$#" -gt 0 ]; do
    case "${1:-}" in
        --dry-run) DRY_RUN=1; shift ;;
        --quiet)   QUIET=1; shift ;;
        --json)    JSON=1; shift ;;
        --shard)
            shift
            if [ "$#" -eq 0 ]; then
                echo "atlas_sha256_rotate: --shard requires a path" >&2
                echo "  reason: missing arg after --shard" >&2
                echo "  fix: --shard n6/atlas.n6 | --shard n6/atlas.append.forge-triple.n6 | ..." >&2
                exit 1
            fi
            ONLY_SHARD="${1}"; shift
            ;;
        --reason)
            shift
            if [ "$#" -eq 0 ]; then
                echo "atlas_sha256_rotate: --reason requires text" >&2
                echo "  reason: missing arg after --reason" >&2
                echo "  fix: --reason 'legitimate edit per commit abc123'" >&2
                exit 1
            fi
            REASON="${1}"; shift
            ;;
        --help|-h)
            sed -n '3,40p' "$0"
            exit 0
            ;;
        "") shift ;;
        *)
            echo "atlas_sha256_rotate: unknown arg '${1}'" >&2
            echo "  reason: only --dry-run|--quiet|--json|--shard PATH|--reason TEXT|--help supported" >&2
            echo "  fix: re-run with one of the above" >&2
            exit 1
            ;;
    esac
done

if [ ! -f "${ATLAS_TSV}" ]; then
    [ "${QUIET}" = "0" ] && [ "${JSON}" = "0" ] && {
        echo "atlas_sha256_rotate: no baseline at ${ATLAS_TSV}"
        echo "  reason: state/atlas_sha256.tsv missing"
        echo "  fix: regenerate baseline first (Step 2 of design/hexa_sim/2026-04-26_atlas_R5_tracking_omega_cycle.json)"
    }
    if [ "${JSON}" = "1" ]; then
        printf '{"sentinel":"__ATLAS_ROTATE__","status":"EMPTY","scanned":0,"rotated":0,"dry_run":%d}\n' "${DRY_RUN}"
    else
        echo "__ATLAS_ROTATE__ EMPTY scanned=0 rotated=0 dry_run=${DRY_RUN}"
    fi
    exit 0
fi

sha_tool=""
if command -v shasum >/dev/null 2>&1; then
    sha_tool="shasum -a 256"
elif command -v sha256sum >/dev/null 2>&1; then
    sha_tool="sha256sum"
else
    echo "atlas_sha256_rotate: no sha tool available" >&2
    echo "  reason: neither 'shasum' nor 'sha256sum' on PATH" >&2
    echo "  fix: install coreutils" >&2
    exit 1
fi

# Helper: count lines (newlines) in a file portably (mac wc may pad spaces).
count_lines() {
    awk 'END{print NR}' "$1" 2>/dev/null
}

scanned=0
rotated=0
status="PASS"

# Iterate non-comment, non-blank rows of the TSV.
# Format: shard_path<TAB>sha256_16<TAB>lines<TAB>last_verified_utc
while IFS=$'\t' read -r shard_path declared_sha decl_lines last_ts; do
    case "${shard_path}" in
        ''|'#'*|'shard_path') continue ;;
    esac
    if [ -n "${ONLY_SHARD}" ] && [ "${shard_path}" != "${ONLY_SHARD}" ]; then
        continue
    fi

    scanned=$((scanned + 1))
    case "${shard_path:0:1}" in
        '/') abs_path="${shard_path}" ;;
        *)   abs_path="${NEXUS_ROOT}/${shard_path}" ;;
    esac
    base_name=$(basename "${shard_path}")
    if [ ! -f "${abs_path}" ]; then
        [ "${QUIET}" = "0" ] && [ "${JSON}" = "0" ] && {
            echo "  ${base_name}: SKIP (file missing: ${shard_path})"
        }
        echo "__ATLAS_SHA256_ROTATE__ SKIPPED shard=${base_name} old=${declared_sha} new=missing"
        continue
    fi

    live_sha_full=$(${sha_tool} "${abs_path}" 2>/dev/null | awk '{print $1}')
    live_sha=$(printf '%s' "${live_sha_full}" | cut -c1-16)
    live_lines=$(count_lines "${abs_path}")

    if [ "${live_sha}" = "${declared_sha}" ]; then
        [ "${QUIET}" = "0" ] && [ "${JSON}" = "0" ] && {
            echo "  ${base_name}: clean (sha=${declared_sha} lines=${live_lines})"
        }
        continue
    fi

    # Drift detected
    rotated=$((rotated + 1))
    [ "${QUIET}" = "0" ] && [ "${JSON}" = "0" ] && {
        echo "  ${base_name}: drift detected"
        echo "    declared: ${declared_sha} (lines=${decl_lines})"
        echo "    live:     ${live_sha} (lines=${live_lines})"
    }

    if [ "${DRY_RUN}" = "1" ]; then
        echo "__ATLAS_SHA256_ROTATE__ SKIPPED shard=${base_name} old=${declared_sha} new=${live_sha}"
        continue
    fi

    # Rotate TSV row in place. Match by column 1 (shard_path) only — atlas TSV
    # has only one row per path so this is unambiguous.
    TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    TMP_TSV="${ATLAS_TSV}.tmp.$$"
    awk -F'\t' -v OFS='\t' \
        -v rpath="${shard_path}" -v new_sha="${live_sha}" -v new_lines="${live_lines}" -v ts="${TS}" '
        /^#/ || NF == 0 { print; next }
        $1 == "shard_path" { print; next }
        $1 == rpath { $2 = new_sha; $3 = new_lines; $4 = ts; print; next }
        { print }
    ' "${ATLAS_TSV}" > "${TMP_TSV}"
    if [ ! -s "${TMP_TSV}" ]; then
        echo "atlas_sha256_rotate: TSV rewrite produced empty output for ${base_name}" >&2
        echo "  reason: awk filter unexpectedly emitted no lines" >&2
        echo "  fix: inspect ${ATLAS_TSV} and ${TMP_TSV}; do not commit" >&2
        rm -f "${TMP_TSV}"
        status="FAIL"
        echo "__ATLAS_SHA256_ROTATE__ ERROR shard=${base_name} old=${declared_sha} new=${live_sha}"
        continue
    fi
    mv "${TMP_TSV}" "${ATLAS_TSV}"

    # Append hash-chained ledger entry (R5 OPT-D)
    mkdir -p "$(dirname "${ATLAS_LOG}")"
    PREV_HASH="genesis"
    if [ -s "${ATLAS_LOG}" ]; then
        LAST_LINE=$(tail -n 1 "${ATLAS_LOG}" 2>/dev/null)
        if [ -n "${LAST_LINE}" ]; then
            PREV_HASH=$(printf '%s' "${LAST_LINE}" | ${sha_tool} | awk '{print $1}')
            [ -z "${PREV_HASH}" ] && PREV_HASH="genesis"
        fi
    fi

    REASON_FIELD="${REASON:-unspecified}"
    REASON_ESC=$(printf '%s' "${REASON_FIELD}" | sed 's/\\/\\\\/g; s/"/\\"/g')
    printf '{"ts":"%s","shard":"%s","old_sha":"%s","new_sha":"%s","old_lines":"%s","new_lines":"%s","trigger":"manual","reason":"%s","prev_hash":"%s"}\n' \
        "${TS}" "${shard_path}" "${declared_sha}" "${live_sha}" "${decl_lines}" "${live_lines}" "${REASON_ESC}" "${PREV_HASH}" >> "${ATLAS_LOG}"

    echo "__ATLAS_SHA256_ROTATE__ ROTATED shard=${base_name} old=${declared_sha} new=${live_sha}"
done < "${ATLAS_TSV}"

if [ "${JSON}" = "1" ]; then
    printf '{"sentinel":"__ATLAS_ROTATE__","status":"%s","scanned":%d,"rotated":%d,"dry_run":%d}\n' \
        "${status}" "${scanned}" "${rotated}" "${DRY_RUN}"
else
    [ "${QUIET}" = "0" ] && {
        echo "atlas_sha256_rotate: scanned=${scanned} rotated=${rotated} dry_run=${DRY_RUN}"
    }
    echo "__ATLAS_ROTATE__ ${status} scanned=${scanned} rotated=${rotated} dry_run=${DRY_RUN}"
fi

[ "${status}" = "FAIL" ] && exit 1
exit 0
