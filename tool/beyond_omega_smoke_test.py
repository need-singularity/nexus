#!/usr/bin/env python3
"""
beyond_omega_smoke_test.py — nxs-20260425-004 cycle 40 (real implementation)

Single integration smoke test for the entire beyond-omega toolchain.

Motivation:
  16 commits + 38+ cycles produced ~22 scripts (Python + shell + JSON manifest).
  None had automated tests. A future change could silently break the chain
  (e.g. atlas_bridge schema drift, ghost_trace argv break, plist plutil failure).
  Cycle 40 = single integration smoke test to catch silent breakage.

Strategy (per script):
  - Python (.py): always run `python3 -m py_compile` (syntax check, zero side-effect).
  - Shell (.sh): always run `bash -n` (syntax check, zero side-effect).
  - JSON (.json): parse with json.load (schema-agnostic well-formedness).
  - Plist (.plist): run `plutil -lint` if available.
  - For a small whitelist of safe-to-execute scripts (read-only / pure analysis
    / idempotent overwrite), also actually invoke them and capture rc + elapsed
    + first/last 5 lines of output. NEVER invoke scripts that spawn cmd_omega
    (force_approach.sh, emit_capture_wrapper.sh, daily_chain.sh) or that mutate
    external state in a non-idempotent way.

Output:
  state/beyond_omega_smoke_test.json with per-script results + aggregate
  pass_count / total / failures.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "tool"
STATE_OUT = REPO / "state" / "beyond_omega_smoke_test.json"

# Scripts that are safe to actually execute (read-only / pure analysis / idempotent).
# All others get syntax-only validation.
SAFE_TO_EXECUTE = {
    # Pure data analysis — no probe, no external process spawn
    "beyond_omega_cycle23_meta_chain_analysis.py",
    "beyond_omega_cycle26_spine_geometry.py",
    # Read-only audits / validators
    "beyond_omega_atlas_schema_validate.py",
    "beyond_omega_tmp_sink_audit.py",  # default mode = read-only (no --write)
    # Idempotent state-derived emit (reads ghost_summary + cross_axis, computes)
    "beyond_omega_cross_axis_join.py",
    # Sidecar annotation (writes its own sidecar file, no external invocation)
    "beyond_omega_cycle39_v3_axis_b_annotation.py",
}

# Scripts explicitly EXCLUDED from execution (would spawn cmd_omega — expensive).
NEVER_EXECUTE = {
    "beyond_omega_cycle4_force_approach.sh",
    "beyond_omega_emit_capture_wrapper.sh",
    "beyond_omega_daily_chain.sh",
    # cycle*_*.py probes that import + run cmd_omega
    "beyond_omega_ghost_trace.py",  # default writes summary + trace; could be safe
    # but skip as it scans repo & writes state — not strictly idempotent
    "beyond_omega_cycle9_meta_squared.py",
    "beyond_omega_cycle12_exp_injector.py",
    "beyond_omega_cycle13_omega_squared.py",
    "beyond_omega_cycle15_p1_omega_tower.py",
    "beyond_omega_cycle16_p2_goodstein.py",
    "beyond_omega_cycle17_p3_gentzen.py",
    "beyond_omega_cycle18_gamma_zero.py",
    "beyond_omega_cycle19_ck_omega.py",
    "beyond_omega_cycle22_veblen_cnf.py",
    "beyond_omega_cycle25_omega_omega.py",
    "beyond_omega_meta_back_action.py",
    # atlas_bridge / atlas_backfill_history append rows to atlas timeline —
    # syntax check only (would mutate atlas_health_timeline.jsonl)
    "beyond_omega_atlas_bridge.py",
    "beyond_omega_atlas_backfill_history.py",
    # Rotate script writes/deletes archived /tmp files — syntax only
    "beyond_omega_tmp_sink_rotate.sh",
}


def _truncate_lines(text: str, n: int = 5) -> dict:
    if not text:
        return {"first": [], "last": [], "total_lines": 0}
    lines = text.splitlines()
    return {
        "first": lines[:n],
        "last": lines[-n:] if len(lines) > n else [],
        "total_lines": len(lines),
    }


def syntax_check_python(script: Path) -> dict:
    t0 = time.time()
    proc = subprocess.run(
        ["python3", "-m", "py_compile", str(script)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    return {
        "mode": "py_compile",
        "rc": proc.returncode,
        "elapsed_ms": int((time.time() - t0) * 1000),
        "stdout": _truncate_lines(proc.stdout),
        "stderr": _truncate_lines(proc.stderr),
        "passed": proc.returncode == 0,
    }


def syntax_check_shell(script: Path) -> dict:
    t0 = time.time()
    # Use bash -n for both #!/bin/bash and #!/usr/bin/env bash shebangs.
    proc = subprocess.run(
        ["bash", "-n", str(script)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    return {
        "mode": "bash_n",
        "rc": proc.returncode,
        "elapsed_ms": int((time.time() - t0) * 1000),
        "stdout": _truncate_lines(proc.stdout),
        "stderr": _truncate_lines(proc.stderr),
        "passed": proc.returncode == 0,
    }


def syntax_check_json(script: Path) -> dict:
    t0 = time.time()
    err = ""
    passed = False
    try:
        with open(script) as fh:
            json.load(fh)
        passed = True
    except (OSError, json.JSONDecodeError) as exc:
        err = f"{type(exc).__name__}: {exc}"
    return {
        "mode": "json_parse",
        "rc": 0 if passed else 1,
        "elapsed_ms": int((time.time() - t0) * 1000),
        "stdout": {"first": [], "last": [], "total_lines": 0},
        "stderr": _truncate_lines(err),
        "passed": passed,
    }


def syntax_check_plist(script: Path) -> dict:
    t0 = time.time()
    proc = subprocess.run(
        ["plutil", "-lint", str(script)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    return {
        "mode": "plutil_lint",
        "rc": proc.returncode,
        "elapsed_ms": int((time.time() - t0) * 1000),
        "stdout": _truncate_lines(proc.stdout),
        "stderr": _truncate_lines(proc.stderr),
        "passed": proc.returncode == 0,
    }


def execute_python(script: Path) -> dict:
    t0 = time.time()
    proc = subprocess.run(
        ["python3", str(script)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(REPO),
    )
    return {
        "mode": "execute",
        "rc": proc.returncode,
        "elapsed_ms": int((time.time() - t0) * 1000),
        "stdout": _truncate_lines(proc.stdout),
        "stderr": _truncate_lines(proc.stderr),
        "passed": proc.returncode == 0,
    }


def main():
    results = []

    # Discover all beyond_omega_* scripts
    candidates = sorted(
        list(TOOL.glob("beyond_omega_*.py"))
        + list(TOOL.glob("beyond_omega_*.sh"))
        + list(TOOL.glob("beyond_omega_*.json"))
    )
    # Also include com.nexus.beyond-omega-daily.plist if present
    plist = TOOL / "com.nexus.beyond-omega-daily.plist"
    if plist.exists():
        candidates.append(plist)

    for script in candidates:
        name = script.name
        suffix = script.suffix
        entry = {
            "script": name,
            "path": str(script.relative_to(REPO)),
            "checks": [],
        }

        # Syntax check
        if suffix == ".py":
            entry["checks"].append(syntax_check_python(script))
        elif suffix == ".sh":
            entry["checks"].append(syntax_check_shell(script))
        elif suffix == ".json":
            entry["checks"].append(syntax_check_json(script))
        elif suffix == ".plist":
            entry["checks"].append(syntax_check_plist(script))

        # Optional execution for whitelisted safe scripts
        if name in SAFE_TO_EXECUTE and suffix == ".py":
            entry["checks"].append(execute_python(script))

        # Aggregate per-script pass: ALL checks must pass
        entry["passed"] = all(c.get("passed", False) for c in entry["checks"])
        entry["execution_policy"] = (
            "executed"
            if name in SAFE_TO_EXECUTE
            else ("syntax_only_safety" if name in NEVER_EXECUTE else "syntax_only_default")
        )
        results.append(entry)

    pass_count = sum(1 for r in results if r["passed"])
    total = len(results)
    failures = [r for r in results if not r["passed"]]

    out = {
        "schema": "nxs_004.cycle40.smoke_test.v1",
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "tool_path": "tool/beyond_omega_smoke_test.py",
        "n_scripts_total": total,
        "pass_count": pass_count,
        "fail_count": total - pass_count,
        "pass_ratio": round(pass_count / total, 3) if total else None,
        "scripts_executed": [
            r["script"] for r in results if r["execution_policy"] == "executed"
        ],
        "scripts_syntax_only_safety": [
            r["script"] for r in results
            if r["execution_policy"] == "syntax_only_safety"
        ],
        "scripts_syntax_only_default": [
            r["script"] for r in results
            if r["execution_policy"] == "syntax_only_default"
        ],
        "results": results,
        "failures_summary": [
            {
                "script": f["script"],
                "checks": [
                    {
                        "mode": c.get("mode"),
                        "rc": c.get("rc"),
                        "stderr_last": c.get("stderr", {}).get("last"),
                    }
                    for c in f["checks"]
                    if not c.get("passed", False)
                ],
            }
            for f in failures
        ],
    }

    STATE_OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_OUT, "w") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)

    print(
        f"⊙ smoke_test {pass_count}/{total} pass "
        f"(ratio={out['pass_ratio']}) → {STATE_OUT.relative_to(REPO)}"
    )
    if failures:
        print(f"  failures ({len(failures)}):")
        for f in failures:
            print(f"    - {f['script']}")
            for c in f["checks"]:
                if not c.get("passed", False):
                    print(f"        {c.get('mode')}: rc={c.get('rc')} stderr={c.get('stderr', {}).get('last')}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
