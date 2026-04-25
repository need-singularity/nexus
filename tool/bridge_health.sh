#!/usr/bin/env bash
# tool/bridge_health.sh — bridge registry health check (cron-friendly)
#
# Iterate the 16 registered hexa-sim bridges (mirrored from cli/run.hexa
# _hexa_sim_bridge_dispatch). For each: gtimeout 30 hexa run <bridge> --selftest.
# Classify PASS / FAIL / OFFLINE-FALLBACK / TAMPERED based on sentinel + exit code.
# Append timeline JSONL line to state/atlas_health_timeline.jsonl.
#
# usage:
#   tool/bridge_health.sh           # human-readable + sentinel + timeline append
#   tool/bridge_health.sh --quiet   # only sentinel line
#   tool/bridge_health.sh --json    # JSONL summary on stdout (no timeline)
#   tool/bridge_health.sh --strict  # also verify each bridge file SHA256 vs pinned baseline
#
# Exit:
#   0 if all PASS
#   76 if any FAIL/TAMPERED (raw 23 schema-guard analog)
#   1 on usage
#
# Sentinel (raw 80):
#   __BRIDGE_HEALTH__ <PASS|WARN|FAIL> total=N pass=P fail=F tampered=K duration_ms=T
#
# Compliance: raw 66 (reason+fix trailers) + raw 71 (report-only) + raw 80
#             + raw 77 (audit-append-only over baseline TSV)
# R1 (bridge_sha256 per-bridge): each bridge file is hashed at runtime and compared
#   against state/bridge_sha256.tsv pinned baseline — mismatch → STATUS=TAMPERED.
#   Defeats silent .hexa rewrite (e.g. selftest sentinel injected into mutated body).
#   Bridges face higher attack risk than falsifiers because external API selftest
#   paths could be subverted. Propagated from falsifier_health.sh R1 (Ω-cycle).
# Origin: design/hexa_sim/2026-04-26_bridge_health_check.md (productionised runner)
#         design/hexa_sim/2026-04-26_bridge_health_R1_propagation_omega_cycle.json

set -uo pipefail

NEXUS_ROOT="${NEXUS_ROOT:-$HOME/core/nexus}"
HEXA_BIN="${HEXA_BIN:-$HOME/core/hexa-lang/hexa}"
TIMELINE="${ATLAS_HEALTH_TIMELINE:-$NEXUS_ROOT/state/atlas_health_timeline.jsonl}"
BRIDGE_SHA_TSV="${BRIDGE_SHA_TSV:-$NEXUS_ROOT/state/bridge_sha256.tsv}"
TIMEOUT_BIN="${TIMEOUT_BIN:-gtimeout}"
TIMEOUT_SECS="${BRIDGE_TIMEOUT:-30}"

QUIET=0
JSON=0
STRICT=0

while [ $# -gt 0 ]; do
    case "$1" in
        --quiet)  QUIET=1; shift ;;
        --json)   JSON=1; shift ;;
        --strict) STRICT=1; shift ;;
        --help|-h) sed -n '3,32p' "$0"; exit 0 ;;
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

# Lookup declared sha256_16 for a given bridge name from baseline TSV.
# Returns empty string if name absent or TSV missing.
declared_sha_for() {
    local _name="$1"
    [ -f "$BRIDGE_SHA_TSV" ] || { printf ''; return; }
    awk -v n="$_name" -F '\t' '!/^#/ && $1==n {print $3; exit}' "$BRIDGE_SHA_TSV"
}

# 16 bridges in registry order (mirrors _hexa_sim_bridge_dispatch in cli/run.hexa).
# Each entry: "<short-name>:<script-relative-to-NEXUS_ROOT>"
BRIDGES="
codata:tool/codata_bridge.hexa
oeis:tool/oeis_live_bridge.hexa
gw:tool/gw_observatory_bridge.hexa
horizons:tool/horizons_bridge.hexa
arxiv:tool/arxiv_realtime_bridge.hexa
cmb:tool/cmb_planck_bridge.hexa
nanograv:tool/nanograv_pulsar_bridge.hexa
simbad:tool/simbad_bridge.hexa
icecube:tool/icecube_neutrino_bridge.hexa
nist_atomic:tool/nist_atomic_bridge.hexa
wikipedia:tool/wikipedia_summary_bridge.hexa
openalex:tool/openalex_bridge.hexa
gaia:tool/gaia_bridge.hexa
lhc:tool/lhc_opendata_bridge.hexa
pubchem:tool/pubchem_bridge.hexa
uniprot:tool/uniprot_bridge.hexa
"

NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)
WALL_START=$(date +%s)
TOTAL=0; PASS=0; FAIL=0; OFFLINE=0; TAMPERED=0

if [ "$QUIET" = "0" ] && [ "$JSON" = "0" ]; then
    echo "═══ BRIDGE HEALTH — $NOW (UTC)"
    echo "hexa: $HEXA_BIN  timeout=${TIMEOUT_SECS}s  baseline=$BRIDGE_SHA_TSV"
fi

# R1 strict baseline check — warn (not fail) if TSV missing (raw 71 report-only)
if [ "$STRICT" = "1" ] && [ ! -f "$BRIDGE_SHA_TSV" ]; then
    echo "warning: --strict requested but bridge_sha256.tsv not found at $BRIDGE_SHA_TSV" >&2
    echo "  reason: bridge SHA256 baseline file missing" >&2
    echo "  fix:    regenerate via tool/bridge_sha256_pin.py or restore from git history" >&2
fi

# Resolve timeout binary (gtimeout on mac, timeout on linux).
command -v "$TIMEOUT_BIN" >/dev/null 2>&1 || TIMEOUT_BIN=$(command -v timeout || true)

for entry in $BRIDGES; do
    NAME="${entry%%:*}"
    REL="${entry#*:}"
    SCRIPT="$NEXUS_ROOT/$REL"
    TOTAL=$((TOTAL+1))
    if [ ! -f "$SCRIPT" ]; then
        FAIL=$((FAIL+1))
        if [ "$QUIET" = "0" ] && [ "$JSON" = "0" ]; then
            printf '  %-12s  FAIL       ec=N/A  reason=script_missing  fix=restore_from_git\n' "$NAME"
        fi
        continue
    fi
    # R1 bridge_sha256 verification — recompute hash of bridge file; mismatch → TAMPERED
    # Defeats silent .hexa rewrite (sentinel-injection into mutated body).
    # Skipped only if no baseline entry exists for this bridge (raw 71 report-only).
    SHA_DECL=$(declared_sha_for "$NAME")
    if [ -n "$SHA_DECL" ]; then
        SHA_LIVE=$(sha256_file_16 "$SCRIPT")
        if [ "$SHA_LIVE" != "$SHA_DECL" ]; then
            STATUS="TAMPERED"; TAMPERED=$((TAMPERED+1)); FAIL=$((FAIL+1))
            if [ "$QUIET" = "0" ] && [ "$JSON" = "0" ]; then
                printf '  %-12s  %-9s  ec=N/A  reason=bridge_sha256_mismatch  fix=audit_git_log_or_refresh_baseline  declared=%s  live=%s\n' \
                    "$NAME" "$STATUS" "$SHA_DECL" "$SHA_LIVE"
            fi
            continue
        fi
    fi
    T0=$(date +%s)
    if [ -n "$TIMEOUT_BIN" ]; then
        OUT=$(HEXA_RESOLVER_NO_REROUTE=1 "$TIMEOUT_BIN" "$TIMEOUT_SECS" "$HEXA_BIN" run "$SCRIPT" --selftest 2>&1); EC=$?
    else
        OUT=$(HEXA_RESOLVER_NO_REROUTE=1 "$HEXA_BIN" run "$SCRIPT" --selftest 2>&1); EC=$?
    fi
    T1=$(date +%s)
    DUR=$((T1 - T0))
    # Status disambiguation (Ω-cycle 2026-04-26 health_check_status_disambiguation):
    #   ec=0 + sentinel match           → PASS
    #   ec=0 + sentinel match + fb str  → PASS + OFFLINE-FALLBACK counter
    #   ec=0 + no sentinel              → FAIL (selftest silently dropped sentinel)
    #   ec≠0 + fallback hint in OUT     → OFFLINE-FALLBACK (bridge degraded but ran)
    #   ec≠0 + no fallback              → FAIL (true error: hexa runtime / network / parse)
    # Bridges have heterogeneous sentinel formats — both __NAME_BRIDGE__ PASS and
    # [name_bridge selftest] OK accepted (raw 73 admissibility).
    STATUS="FAIL"
    if [ "$EC" = "0" ] && printf '%s' "$OUT" | grep -Eq '(__[A-Z_]+(_BRIDGE)?__[[:space:]]+PASS\b|\[[a-z0-9_]+_bridge[^]]*selftest\][[:space:]]+OK\b)'; then
        STATUS="PASS"; PASS=$((PASS+1))
        # OFFLINE-FALLBACK detection: bridge passed but used hardcoded fallback.
        if printf '%s' "$OUT" | grep -Eqi 'fallback|offline|no.?fetch'; then
            OFFLINE=$((OFFLINE+1))
        fi
    elif [ "$EC" != "0" ] && printf '%s' "$OUT" | grep -Eqi 'fallback|offline|no.?fetch'; then
        # ec≠0 but bridge engaged offline fallback path — degraded, not failed
        STATUS="OFFLINE"; OFFLINE=$((OFFLINE+1)); FAIL=$((FAIL+1))
    else
        FAIL=$((FAIL+1))
    fi
    if [ "$QUIET" = "0" ] && [ "$JSON" = "0" ]; then
        if [ "$STATUS" = "FAIL" ]; then
            printf '  %-12s  %-9s  ec=%-3s  %3ss  reason=selftest_failed  fix=run_verbose_then_check_design\n' "$NAME" "$STATUS" "$EC" "$DUR"
        else
            printf '  %-12s  %-9s  ec=%-3s  %3ss\n' "$NAME" "$STATUS" "$EC" "$DUR"
        fi
    fi
done

WALL_END=$(date +%s)
DURATION_MS=$(( (WALL_END - WALL_START) * 1000 ))

VERDICT="PASS"
EXIT_CODE=0
if [ "$FAIL" -gt 0 ]; then
    VERDICT="FAIL"
    EXIT_CODE=76
fi

JSONL_LINE=$(printf '{"ts":"%s","scope":"bridge_registry","total":%d,"pass":%d,"fail":%d,"offline_fallback":%d,"tampered":%d,"duration_ms":%d,"checker":"bridge_health.sh"}' \
    "$NOW" "$TOTAL" "$PASS" "$FAIL" "$OFFLINE" "$TAMPERED" "$DURATION_MS")

if [ "$JSON" = "1" ]; then
    printf '%s\n' "$JSONL_LINE"
else
    printf '%s\n' "$JSONL_LINE" >> "$TIMELINE"
fi

if [ "$QUIET" = "0" ] && [ "$JSON" = "0" ]; then
    echo "─── summary"
    printf '  total=%d  pass=%d  fail=%d  offline_fallback=%d  tampered=%d  wall=%dms\n' \
        "$TOTAL" "$PASS" "$FAIL" "$OFFLINE" "$TAMPERED" "$DURATION_MS"
    if [ "$EXIT_CODE" = "76" ]; then
        echo "  reason: $FAIL bridge(s) failed selftest ($TAMPERED tampered)"
        echo "  fix:    bash $NEXUS_ROOT/tool/bridge_health.sh (verbose); consult design/hexa_sim/2026-04-26_bridge_health_check.md"
        if [ "$TAMPERED" -gt 0 ]; then
            echo "  fix:    audit git log of mutated bridge(s); if intended, refresh $BRIDGE_SHA_TSV"
        fi
    fi
fi

echo "__BRIDGE_HEALTH__ $VERDICT total=$TOTAL pass=$PASS fail=$FAIL tampered=$TAMPERED duration_ms=$DURATION_MS"
exit $EXIT_CODE
