#!/usr/bin/env bash
# tool/bridge_health_parallel.sh — parallel bridge registry health check
#
# Drop-in equivalent of tool/bridge_health.sh, but uses python3
# concurrent.futures.ProcessPoolExecutor to fan out gtimeout-wrapped
# `hexa run <bridge> --selftest` invocations across N workers
# (default = cpu_count()). Aggregates results in main process,
# emits IDENTICAL sentinel + timeline JSONL to sequential version.
#
# usage:
#   tool/bridge_health_parallel.sh           # human + sentinel + timeline append
#   tool/bridge_health_parallel.sh --quiet   # only sentinel line on stdout
#   tool/bridge_health_parallel.sh --json    # JSONL summary on stdout
#   tool/bridge_health_parallel.sh --strict  # also verify each bridge SHA256 (warn-only)
#   tool/bridge_health_parallel.sh -j 8      # worker count (default cpu_count)
#
# Exit:
#   0 if all PASS
#   76 if any FAIL/TAMPERED (raw 23 schema-guard analog)
#   1 on usage
#
# Sentinel (raw 80 — IDENTICAL to bridge_health.sh):
#   __BRIDGE_HEALTH__ <PASS|WARN|FAIL> total=N pass=P fail=F tampered=K duration_ms=T
#
# Compliance: raw 66 (reason+fix trailers) + raw 71 (report-only) +
#             raw 73 (admissibility — output equivalent to sequential) +
#             raw 77 (read-only registry) + raw 80 (sentinel format unchanged)
# Origin: design/hexa_sim/2026-04-26_bridge_health_parallelize_omega_cycle.json
#
# Docker bottleneck note (Ω-cycle 2026-04-26 falsifier_health_parallelize lineage):
#   Each bridge invokes `hexa run <bridge>.hexa --selftest` with
#   HEXA_RESOLVER_NO_REROUTE=1 — this short-circuits the resolver's
#   docker-exec round-trip and uses build/hexa.real directly. Therefore
#   parallel calls do NOT serialise at the hexa-exec container level —
#   each worker is an independent native dispatcher. Speedup is limited
#   only by cpu_count + per-bridge external API I/O latency.

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
JOBS=0   # 0 → python picks cpu_count()

while [ $# -gt 0 ]; do
    case "$1" in
        --quiet)  QUIET=1; shift ;;
        --json)   JSON=1; shift ;;
        --strict) STRICT=1; shift ;;
        -j)
            shift
            JOBS="${1:-0}"
            shift || true
            ;;
        -j*)
            JOBS="${1#-j}"
            shift
            ;;
        --jobs=*)
            JOBS="${1#--jobs=}"
            shift
            ;;
        --help|-h)
            sed -n '3,32p' "$0"
            exit 0
            ;;
        *)
            echo "usage error: unknown flag: $1" >&2
            echo "  reason: unrecognised CLI argument" >&2
            echo "  fix:    use --quiet | --json | --strict | -j N | --help" >&2
            exit 1
            ;;
    esac
done

# Resolve timeout binary (gtimeout on mac, timeout on linux).
command -v "$TIMEOUT_BIN" >/dev/null 2>&1 || TIMEOUT_BIN=$(command -v timeout || true)

# 16 bridges in registry order (mirrors _hexa_sim_bridge_dispatch in cli/run.hexa).
# IDENTICAL to bridge_health.sh BRIDGES inventory.
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

if [ "$QUIET" = "0" ] && [ "$JSON" = "0" ]; then
    echo "═══ BRIDGE HEALTH (parallel) — $NOW (UTC)"
    echo "hexa: $HEXA_BIN  timeout=${TIMEOUT_SECS}s  baseline=$BRIDGE_SHA_TSV"
fi

# R1 strict baseline check — warn (not fail) if TSV missing (raw 71 report-only)
if [ "$STRICT" = "1" ] && [ ! -f "$BRIDGE_SHA_TSV" ]; then
    echo "warning: --strict requested but bridge_sha256.tsv not found at $BRIDGE_SHA_TSV" >&2
    echo "  reason: bridge SHA256 baseline file missing" >&2
    echo "  fix:    regenerate via tool/bridge_sha256_pin.py or restore from git history" >&2
fi

# Materialise BRIDGES as TSV for python worker (one entry per line: name<TAB>relpath)
BRIDGES_TSV="$(mktemp -t bridge_health_inventory.XXXXXX).tsv"
trap 'rm -f "$BRIDGES_TSV" "$WORKER_PY"' EXIT
for entry in $BRIDGES; do
    name="${entry%%:*}"
    rel="${entry#*:}"
    printf '%s\t%s\n' "$name" "$rel" >> "$BRIDGES_TSV"
done

# Hand off to python worker. ProcessPoolExecutor needs a real importable
# module path (cannot fork from a heredoc <stdin> source), so we materialise
# the worker to a temp .py file and exec it.
WORKER_PY="$(mktemp -t bridge_health_worker.XXXXXX).py"

cat >"$WORKER_PY" <<'PYEOF'
import concurrent.futures
import hashlib
import json
import os
import re
import subprocess
import sys
import time

NEXUS_ROOT = os.environ["NEXUS_ROOT"]
HEXA_BIN = os.environ["HEXA_BIN"]
TIMEOUT_BIN = os.environ.get("TIMEOUT_BIN", "")
TIMEOUT_SECS = int(os.environ.get("TIMEOUT_SECS", "30"))
BRIDGES_TSV = os.environ["BRIDGES_TSV"]
BRIDGE_SHA_TSV = os.environ.get("BRIDGE_SHA_TSV", "")
JOBS_ENV = int(os.environ.get("JOBS", "0") or 0)

# Sentinel acceptors — heterogeneous bridge formats (raw 73 admissibility):
#   __<NAME>(_BRIDGE)?__ PASS    — uppercase sentinel
#   [<name>_bridge ...selftest] OK — lowercase tag
SENTINEL_RE = re.compile(
    r"(__[A-Z_]+(_BRIDGE)?__\s+PASS\b|\[[a-z0-9_]+_bridge[^]]*selftest\]\s+OK\b)"
)
# Fallback / offline indicators
FALLBACK_RE = re.compile(r"fallback|offline|no.?fetch", re.IGNORECASE)


def sha256_file_16(path: str) -> str:
    """First 16 hex chars of file SHA256 (mirrors sequential sha256_file_16)."""
    try:
        h = hashlib.sha256()
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()[:16]
    except Exception:
        return ""


def load_declared_shas() -> dict:
    """Parse BRIDGE_SHA_TSV → {name: sha16}. Empty dict if missing."""
    out = {}
    if not BRIDGE_SHA_TSV or not os.path.isfile(BRIDGE_SHA_TSV):
        return out
    try:
        with open(BRIDGE_SHA_TSV, "r") as fh:
            for ln in fh:
                if not ln.strip() or ln.startswith("#"):
                    continue
                parts = ln.rstrip("\n").split("\t")
                if len(parts) >= 3:
                    out[parts[0]] = parts[2]
    except Exception:
        pass
    return out


# Module-level so workers inherit (forked dict).
DECLARED_SHAS = load_declared_shas()


def classify(entry):
    """Return (name, status, ec, dur_s, offline_flag, extra) for a single bridge."""
    name, rel = entry
    script = os.path.join(NEXUS_ROOT, rel)
    if not os.path.isfile(script):
        return (name, "FAIL", "N/A", 0, 0, "script_missing")

    # R1 SHA256 verification (mirrors sequential)
    sha_decl = DECLARED_SHAS.get(name, "")
    if sha_decl:
        sha_live = sha256_file_16(script)
        if sha_live != sha_decl:
            return (name, "TAMPERED", "N/A", 0, 0,
                    f"declared={sha_decl} live={sha_live}")

    # Build command. HEXA_RESOLVER_NO_REROUTE=1 short-circuits docker-exec
    # round-trip — uses build/hexa.real native dispatcher. Each worker is
    # therefore an independent process (no hexa-exec container serialisation).
    env = os.environ.copy()
    env["HEXA_RESOLVER_NO_REROUTE"] = "1"

    if TIMEOUT_BIN:
        cmd = [TIMEOUT_BIN, str(TIMEOUT_SECS), HEXA_BIN, "run", script, "--selftest"]
    else:
        cmd = [HEXA_BIN, "run", script, "--selftest"]

    t0 = time.monotonic()
    try:
        # Subprocess timeout = TIMEOUT_SECS + 5s grace (gtimeout fires first)
        proc = subprocess.run(
            cmd, capture_output=True, text=True,
            timeout=TIMEOUT_SECS + 5, env=env,
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        ec = proc.returncode
    except subprocess.TimeoutExpired:
        return (name, "FAIL", "TIMEOUT", int(time.monotonic() - t0), 0,
                "subprocess_timeout")
    except Exception as exc:
        return (name, "FAIL", "EXC", 0, 0, f"subprocess_exc={exc}")
    dur_s = int(round(time.monotonic() - t0))

    # Status disambiguation (mirrors sequential):
    #   ec=0 + sentinel match           → PASS
    #   ec=0 + sentinel match + fb str  → PASS + OFFLINE counter
    #   ec=0 + no sentinel              → FAIL
    #   ec≠0 + fallback hint            → OFFLINE (degraded; counts toward FAIL)
    #   ec≠0 + no fallback              → FAIL
    sentinel_hit = bool(SENTINEL_RE.search(out))
    fallback_hit = bool(FALLBACK_RE.search(out))

    if ec == 0 and sentinel_hit:
        return (name, "PASS", str(ec), dur_s, 1 if fallback_hit else 0, "")
    if ec != 0 and fallback_hit:
        return (name, "OFFLINE", str(ec), dur_s, 1, "")
    return (name, "FAIL", str(ec), dur_s, 0, "")


def main():
    entries = []
    with open(BRIDGES_TSV, "r") as fh:
        for ln in fh:
            ln = ln.rstrip("\n")
            if not ln:
                continue
            parts = ln.split("\t")
            if len(parts) >= 2:
                entries.append((parts[0], parts[1]))

    workers = JOBS_ENV if JOBS_ENV > 0 else (os.cpu_count() or 4)
    wall_t0 = time.monotonic_ns()
    results = [None] * len(entries)
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(classify, e): i for i, e in enumerate(entries)}
        for fut in concurrent.futures.as_completed(futs):
            idx = futs[fut]
            try:
                results[idx] = fut.result()
            except Exception as exc:
                name = entries[idx][0]
                results[idx] = (name, "FAIL", "FUTURE", 0, 0, f"future_exc={exc}")
    wall_t1 = time.monotonic_ns()
    wall_ms = (wall_t1 - wall_t0) // 1_000_000

    total = passed = fail = offline = tampered = 0
    for r in results:
        if r is None:
            continue
        name, status, ec, dur_s, off_flag, extra = r
        total += 1
        if status == "PASS":
            passed += 1
            if off_flag:
                offline += 1
        elif status == "TAMPERED":
            tampered += 1
            fail += 1
        elif status == "OFFLINE":
            offline += 1
            fail += 1
        else:
            # FAIL
            fail += 1
        sys.stdout.write(f"{name}\t{status}\t{ec}\t{dur_s}\t{off_flag}\t{extra}\n")
    sys.stdout.write(
        f"__SUMMARY__\t{total}\t{passed}\t{fail}\t{offline}\t{tampered}\t{wall_ms}\n"
    )


if __name__ == "__main__":
    main()
PYEOF

WORKER_OUT=$(NEXUS_ROOT="$NEXUS_ROOT" HEXA_BIN="$HEXA_BIN" \
    TIMEOUT_BIN="$TIMEOUT_BIN" TIMEOUT_SECS="$TIMEOUT_SECS" \
    BRIDGES_TSV="$BRIDGES_TSV" BRIDGE_SHA_TSV="$BRIDGE_SHA_TSV" \
    JOBS="$JOBS" python3 "$WORKER_PY")
WORKER_EC=$?

if [ "$WORKER_EC" != "0" ]; then
    echo "error: parallel worker failed (ec=$WORKER_EC)" >&2
    echo "  reason: python3 worker subprocess crashed" >&2
    echo "  fix:    re-run sequential tool/bridge_health.sh; check python3 stderr" >&2
    exit 1
fi

# Parse worker output: per-bridge rows + final __SUMMARY__ row
SUMMARY_LINE=$(printf '%s\n' "$WORKER_OUT" | grep '^__SUMMARY__' | tail -1)
TOTAL=$(printf    '%s' "$SUMMARY_LINE" | awk -F'\t' '{print $2}')
PASS=$(printf     '%s' "$SUMMARY_LINE" | awk -F'\t' '{print $3}')
FAIL=$(printf     '%s' "$SUMMARY_LINE" | awk -F'\t' '{print $4}')
OFFLINE=$(printf  '%s' "$SUMMARY_LINE" | awk -F'\t' '{print $5}')
TAMPERED=$(printf '%s' "$SUMMARY_LINE" | awk -F'\t' '{print $6}')
DURATION_MS=$(printf '%s' "$SUMMARY_LINE" | awk -F'\t' '{print $7}')

if [ "$QUIET" = "0" ] && [ "$JSON" = "0" ]; then
    # Render per-bridge rows in registry order (use BRIDGES_TSV order index)
    awk -F'\t' 'NR==FNR { idx[$1]=NR; next }
                $1 != "__SUMMARY__" { printf "%06d\t%s\n", (idx[$1]?idx[$1]:9999), $0 }' \
        "$BRIDGES_TSV" <(printf '%s\n' "$WORKER_OUT") \
        | sort -n \
        | cut -f2- \
        | while IFS=$'\t' read -r NAME STATUS EC DUR OFF EXTRA; do
            if [ "$STATUS" = "TAMPERED" ]; then
                printf '  %-12s  %-9s  ec=N/A  reason=bridge_sha256_mismatch  fix=audit_git_log_or_refresh_baseline  %s\n' \
                    "$NAME" "$STATUS" "$EXTRA"
            elif [ "$STATUS" = "FAIL" ]; then
                if [ -n "$EXTRA" ]; then
                    printf '  %-12s  %-9s  ec=%-3s  %3ss  reason=%s  fix=run_verbose_then_check_design\n' \
                        "$NAME" "$STATUS" "$EC" "$DUR" "$EXTRA"
                else
                    printf '  %-12s  %-9s  ec=%-3s  %3ss  reason=selftest_failed  fix=run_verbose_then_check_design\n' \
                        "$NAME" "$STATUS" "$EC" "$DUR"
                fi
            else
                printf '  %-12s  %-9s  ec=%-3s  %3ss\n' "$NAME" "$STATUS" "$EC" "$DUR"
            fi
        done
fi

VERDICT="PASS"
EXIT_CODE=0
if [ "$FAIL" -gt 0 ]; then
    VERDICT="FAIL"
    EXIT_CODE=76
fi

JSONL_LINE=$(printf '{"ts":"%s","scope":"bridge_registry","total":%d,"pass":%d,"fail":%d,"offline_fallback":%d,"tampered":%d,"duration_ms":%d,"checker":"bridge_health_parallel.sh"}' \
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
