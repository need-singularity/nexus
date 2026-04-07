"""Execution engine — runs Tier 1 tests via pytest and Tier 2+3 scripts via subprocess."""

import json
import os
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

from n6_replication.parser import parse_output
from n6_replication.registry import filter_scripts, load_all

TIER1_DIR = Path(__file__).parent.parent.parent / "tests" / "tier1"
RESULTS_DIR = Path(__file__).parent.parent.parent / "results"


# ---------------------------------------------------------------------------
# Tier 1: pytest
# ---------------------------------------------------------------------------

def run_tier1(verbose: bool = False) -> list[dict]:
    """Run Tier 1 pytest tests and return a list of result dicts."""
    try:
        import pytest  # noqa: F811
    except ImportError:
        return [{
            "id": "tier1",
            "tier": 1,
            "repo": "n6-replication",
            "status": "error",
            "grade_counts": {},
            "p_values": [],
            "pass_count": 0,
            "fail_count": 0,
            "duration_seconds": 0.0,
            "stdout_snippet": "",
            "error": "pytest not installed",
        }]

    results: list[dict] = []
    collected: list = []

    class _Collector:
        """Minimal pytest plugin to collect per-test results."""

        def pytest_collection_modifyitems(self, items):
            collected.clear()
            collected.extend(items)

        def pytest_runtest_logreport(self, report):
            if report.when == "call":
                status = "pass" if report.passed else "fail"
                test_id = report.nodeid.split("::")[-1]
                results.append({
                    "id": test_id,
                    "tier": 1,
                    "repo": "n6-replication",
                    "status": status,
                    "grade_counts": {},
                    "p_values": [],
                    "pass_count": 1 if report.passed else 0,
                    "fail_count": 0 if report.passed else 1,
                    "duration_seconds": round(report.duration, 3),
                    "stdout_snippet": (report.longreprtext or "")[:500],
                    "error": None if report.passed else (report.longreprtext or "")[:500],
                })

    args = [str(TIER1_DIR), "-q", "--tb=short", "--no-header"]
    if verbose:
        args.append("-v")

    t0 = time.monotonic()
    exit_code = pytest.main(args, plugins=[_Collector()])
    elapsed = round(time.monotonic() - t0, 3)

    # If pytest collected but plugin captured nothing (e.g. all skipped), add summary
    if not results:
        results.append({
            "id": "tier1_summary",
            "tier": 1,
            "repo": "n6-replication",
            "status": "pass" if exit_code == 0 else "fail",
            "grade_counts": {},
            "p_values": [],
            "pass_count": 0,
            "fail_count": 0,
            "duration_seconds": elapsed,
            "stdout_snippet": f"pytest exit code: {exit_code}",
            "error": None if exit_code == 0 else f"pytest exit code: {exit_code}",
        })

    return results


# ---------------------------------------------------------------------------
# Tier 2+3: subprocess
# ---------------------------------------------------------------------------

def run_script(entry: dict, repo_root: str, verbose: bool = False) -> dict:
    """Run a single verification script via subprocess.

    Parameters
    ----------
    entry : dict
        Registry entry with keys: id, path, tier, requires_gpu, timeout, ...
    repo_root : str
        Absolute path to the repository root (used as cwd and PYTHONPATH).
    verbose : bool
        If True, print stdout/stderr in real time.

    Returns
    -------
    dict
        Structured result.
    """
    script_path = entry["path"]
    tier = entry.get("tier", 2)
    timeout = entry.get("timeout", 120)
    script_id = entry.get("id", Path(script_path).stem)

    # For Tier 3, the repo may be different
    cwd = entry.get("repo_path", repo_root)
    abs_script = os.path.join(cwd, script_path)

    if not os.path.isfile(abs_script):
        return _result(script_id, tier, entry, status="error",
                       error=f"Script not found: {abs_script}")

    env = os.environ.copy()
    env["PYTHONPATH"] = cwd

    t0 = time.monotonic()
    try:
        proc = subprocess.run(
            [sys.executable, abs_script],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
            env=env,
        )
        elapsed = round(time.monotonic() - t0, 3)
        stdout = proc.stdout or ""
        stderr = proc.stderr or ""

        if verbose:
            if stdout:
                print(stdout)
            if stderr:
                print(stderr, file=sys.stderr)

        parsed = parse_output(stdout)

        # If returncode != 0 and parser found nothing, mark as error
        if proc.returncode != 0 and parsed["status"] == "parse_error":
            status = "error"
            error_msg = (stderr or stdout)[:500]
        else:
            status = parsed["status"]
            error_msg = None if status == "pass" else (stderr[:500] if stderr else None)

        return _result(
            script_id, tier, entry,
            status=status,
            grade_counts=parsed["grades"],
            p_values=parsed["p_values"],
            pass_count=parsed["pass_count"],
            fail_count=parsed["fail_count"],
            duration=elapsed,
            stdout_snippet=stdout[:500],
            error=error_msg,
        )

    except subprocess.TimeoutExpired:
        elapsed = round(time.monotonic() - t0, 3)
        return _result(script_id, tier, entry, status="timeout",
                       duration=elapsed,
                       error=f"Timed out after {timeout}s")
    except Exception as exc:
        elapsed = round(time.monotonic() - t0, 3)
        return _result(script_id, tier, entry, status="error",
                       duration=elapsed,
                       error=str(exc)[:500])


def _result(
    script_id: str,
    tier: int,
    entry: dict,
    *,
    status: str = "error",
    grade_counts: dict | None = None,
    p_values: list | None = None,
    pass_count: int = 0,
    fail_count: int = 0,
    duration: float = 0.0,
    stdout_snippet: str = "",
    error: str | None = None,
) -> dict:
    """Build a canonical result dict."""
    return {
        "id": script_id,
        "tier": tier,
        "repo": entry.get("repo", "TECS-L"),
        "status": status,
        "grade_counts": grade_counts or {},
        "p_values": p_values or [],
        "pass_count": pass_count,
        "fail_count": fail_count,
        "duration_seconds": duration,
        "stdout_snippet": stdout_snippet,
        "error": error,
    }


def run_tier2_3(
    tiers: list[int] | None = None,
    repo_root: str | None = None,
    parallel: int = 1,
    gpu: bool = False,
    verbose: bool = False,
) -> list[dict]:
    """Run all Tier 2+3 scripts from the registry.

    Parameters
    ----------
    tiers : list[int] | None
        Which tiers to run (default [2, 3]).
    repo_root : str | None
        Repository root. Defaults to TECS-L root (../../.. from this file).
    parallel : int
        Max parallel workers (1 = sequential).
    gpu : bool
        If False, skip scripts with requires_gpu=True.
    verbose : bool
        Pass through to run_script.

    Returns
    -------
    list[dict]
        One result per script.
    """
    if tiers is None:
        tiers = [2, 3]
    if repo_root is None:
        # Default: TECS-L root (n6-replication lives inside TECS-L)
        repo_root = str(Path(__file__).parent.parent.parent.parent)

    scripts = load_all(tiers)

    if not gpu:
        runnable = []
        skipped = []
        for s in scripts:
            if s.get("requires_gpu", False):
                skipped.append(s)
            else:
                runnable.append(s)
    else:
        runnable = scripts
        skipped = []

    results: list[dict] = []

    # Record skipped
    for s in skipped:
        results.append(_result(
            s.get("id", "unknown"),
            s.get("tier", 2),
            s,
            status="skip",
            error="requires_gpu=True but gpu=False",
        ))

    if parallel <= 1:
        # Sequential
        for entry in runnable:
            results.append(run_script(entry, repo_root, verbose=verbose))
    else:
        # Parallel
        with ProcessPoolExecutor(max_workers=parallel) as pool:
            futures = {
                pool.submit(run_script, entry, repo_root, verbose): entry
                for entry in runnable
            }
            for future in as_completed(futures):
                entry = futures[future]
                try:
                    results.append(future.result())
                except Exception as exc:
                    results.append(_result(
                        entry.get("id", "unknown"),
                        entry.get("tier", 2),
                        entry,
                        status="error",
                        error=f"ProcessPool exception: {exc}",
                    ))

    return results


# ---------------------------------------------------------------------------
# Results persistence
# ---------------------------------------------------------------------------

def save_results(results: list[dict]) -> Path:
    """Save results to results/YYYY-MM-DD-HHMMSS.json and return the path."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    path = RESULTS_DIR / f"{stamp}.json"
    with open(path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    return path
