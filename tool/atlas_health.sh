#!/usr/bin/env bash
# tool/atlas_health.sh — atlas data-shard SHA256 integrity check (cron-friendly)
#
# Iterate state/atlas_sha256.tsv (10 shards as of Ω-cycle 2026-04-26: atlas.n6 main
# + 9 active append shards; chip-p5-2 already retired to _retired/). For each shard:
# recompute SHA256, compare to the pinned baseline. Mismatch → STATUS=TAMPERED.
# Append timeline JSONL to state/atlas_health_timeline.jsonl (shared with bridge/
# falsifier health for unified rotation watch).
#
# Defense layer R5 — closes the final gap left by R1 (cmd/bridge file SHA) +
# falsifier_registry hash-chain. Atlas data files are the substrate verified
# indirectly by falsifiers (e.g. F1 sigma=12); a bulk silent edit to atlas.n6
# touching values that NO falsifier covers would slip past every other defense.
# This tool reports such drift; it never auto-rewrites atlas content (raw 71).
#
# usage:
#   tool/atlas_health.sh           # human-readable + sentinel + timeline append
#   tool/atlas_health.sh --quiet   # only sentinel line
#   tool/atlas_health.sh --json    # JSONL summary on stdout (no timeline)
#   tool/atlas_health.sh --strict  # fail (exit 76) if baseline TSV is missing
#
# Exit:
#   0  all PASS
#   76 any TAMPERED (raw 23 schema-guard analog)
#   1  usage error
#
# Sentinel (raw 80):
#   __ATLAS_HEALTH__ <PASS|WARN|FAIL> total=N pass=P tampered=T duration_ms=DD
#
# Compliance:
#   raw 66 — reason+fix trailers on every error path
#   raw 71 — REPORTS only; never modifies n6/atlas*.n6 contents (rotation lives in
#            atlas_sha256_rotate.sh, mirroring the bridge defense topology)
#   raw 73 — minimal: bash 3.2 portable, no python required
#   raw 77 — additive: leaves untouched TSV rows + comment lines verbatim
#   raw 80 — new sentinel surface (no prior version to break)
# Origin: design/hexa_sim/2026-04-26_atlas_R5_tracking_omega_cycle.json

set -uo pipefail

NEXUS_ROOT="${NEXUS_ROOT:-$HOME/core/nexus}"
TIMELINE="${ATLAS_HEALTH_TIMELINE:-$NEXUS_ROOT/state/atlas_health_timeline.jsonl}"
ATLAS_SHA_TSV="${ATLAS_SHA_TSV:-$NEXUS_ROOT/state/atlas_sha256.tsv}"

QUIET=0
JSON=0
STRICT=0

while [ $# -gt 0 ]; do
    case "$1" in
        --quiet)  QUIET=1; shift ;;
        --json)   JSON=1; shift ;;
        --strict) STRICT=1; shift ;;
        --help|-h) sed -n '3,33p' "$0"; exit 0 ;;
        *)
            echo "usage error: unknown flag: $1" >&2
            echo "  reason: unrecognised CLI argument" >&2
            echo "  fix:    use --quiet | --json | --strict | --help" >&2
            exit 1
            ;;
    esac
done

# Helper: SHA256 of a file (first 16 hex chars). Tries shasum (BSD) then sha256sum (GNU).
sha256_file_16() {
    local _h
    _h=$(shasum -a 256 "$1" 2>/dev/null | awk '{print $1}')
    [ -z "$_h" ] && _h=$(sha256sum "$1" 2>/dev/null | awk '{print $1}')
    printf '%s' "${_h:0:16}"
}

if [ ! -f "$ATLAS_SHA_TSV" ]; then
    if [ "$STRICT" = "1" ]; then
        echo "atlas_health: baseline TSV missing at $ATLAS_SHA_TSV" >&2
        echo "  reason: --strict requested but state/atlas_sha256.tsv absent" >&2
        echo "  fix:    regenerate via Step 2 scaffold in design/hexa_sim/2026-04-26_atlas_R5_tracking_omega_cycle.json" >&2
        exit 76
    fi
    [ "$QUIET" = "0" ] && [ "$JSON" = "0" ] && {
        echo "atlas_health: no baseline at $ATLAS_SHA_TSV (vacuously PASS)"
    }
    if [ "$JSON" = "1" ]; then
        printf '{"sentinel":"__ATLAS_HEALTH__","status":"PASS","total":0,"pass":0,"tampered":0,"duration_ms":0,"baseline":"missing"}\n'
    else
        echo "__ATLAS_HEALTH__ PASS total=0 pass=0 tampered=0 duration_ms=0"
    fi
    exit 0
fi

NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)
WALL_START=$(date +%s)
TOTAL=0; PASS=0; TAMPERED=0; MISSING=0

if [ "$QUIET" = "0" ] && [ "$JSON" = "0" ]; then
    echo "═══ ATLAS HEALTH — $NOW (UTC)"
    echo "baseline=$ATLAS_SHA_TSV"
fi

while IFS=$'\t' read -r shard_rel declared_sha decl_lines last_ts; do
    case "${shard_rel}" in
        ''|'#'*|'shard_path') continue ;;
    esac
    case "${shard_rel:0:1}" in
        '/') ABS_PATH="$shard_rel" ;;
        *)   ABS_PATH="$NEXUS_ROOT/$shard_rel" ;;
    esac
    NAME=$(basename "$shard_rel")
    TOTAL=$((TOTAL+1))
    if [ ! -f "$ABS_PATH" ]; then
        MISSING=$((MISSING+1))
        TAMPERED=$((TAMPERED+1))
        if [ "$QUIET" = "0" ] && [ "$JSON" = "0" ]; then
            printf '  %-58s  TAMPERED   reason=shard_missing  fix=restore_from_git_or_remove_baseline_row\n' "$NAME"
        fi
        continue
    fi
    SHA_LIVE=$(sha256_file_16 "$ABS_PATH")
    if [ "$SHA_LIVE" = "$declared_sha" ]; then
        PASS=$((PASS+1))
        if [ "$QUIET" = "0" ] && [ "$JSON" = "0" ]; then
            printf '  %-58s  PASS       sha=%s\n' "$NAME" "$declared_sha"
        fi
    else
        TAMPERED=$((TAMPERED+1))
        if [ "$QUIET" = "0" ] && [ "$JSON" = "0" ]; then
            printf '  %-58s  TAMPERED   declared=%s  live=%s  reason=atlas_sha256_mismatch  fix=audit_git_log_or_rotate_baseline\n' \
                "$NAME" "$declared_sha" "$SHA_LIVE"
        fi
    fi
done < "$ATLAS_SHA_TSV"

WALL_END=$(date +%s)
DURATION_MS=$(( (WALL_END - WALL_START) * 1000 ))

VERDICT="PASS"
EXIT_CODE=0
if [ "$TAMPERED" -gt 0 ]; then
    VERDICT="FAIL"
    EXIT_CODE=76
fi

JSONL_LINE=$(printf '{"ts":"%s","scope":"atlas_shards","total":%d,"pass":%d,"tampered":%d,"missing":%d,"duration_ms":%d,"checker":"atlas_health.sh"}' \
    "$NOW" "$TOTAL" "$PASS" "$TAMPERED" "$MISSING" "$DURATION_MS")

if [ "$JSON" = "1" ]; then
    printf '%s\n' "$JSONL_LINE"
else
    mkdir -p "$(dirname "$TIMELINE")"
    printf '%s\n' "$JSONL_LINE" >> "$TIMELINE"
fi

if [ "$QUIET" = "0" ] && [ "$JSON" = "0" ]; then
    echo "─── summary"
    printf '  total=%d  pass=%d  tampered=%d  missing=%d  wall=%dms\n' \
        "$TOTAL" "$PASS" "$TAMPERED" "$MISSING" "$DURATION_MS"
    if [ "$EXIT_CODE" = "76" ]; then
        echo "  reason: $TAMPERED shard(s) drifted from baseline ($MISSING missing)"
        echo "  fix:    audit git log of mutated shards; if intended, rotate via tool/atlas_sha256_rotate.sh"
        echo "  fix:    chain integrity: bash $NEXUS_ROOT/tool/ledger_verify.sh --ledger atlas"
    fi
fi

echo "__ATLAS_HEALTH__ $VERDICT total=$TOTAL pass=$PASS tampered=$TAMPERED duration_ms=$DURATION_MS"
exit $EXIT_CODE
