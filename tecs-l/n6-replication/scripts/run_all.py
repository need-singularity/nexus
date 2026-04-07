#!/usr/bin/env python3
"""Minimal replication entrypoint -- works WITHOUT pip install.

Usage:
    python3 run_all.py              # Tier 1 + 2
    python3 run_all.py --tier 1     # Tier 1 only (pytest, ~30s)
    python3 run_all.py --tier 2     # Tier 2 only (verify/*.py, ~10min)
    python3 run_all.py --tier 1 2   # Both tiers

No dependencies beyond stdlib + pytest (for tier 1).
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path


def find_repo_root() -> Path:
    """Walk up from this script to find the repo root (contains verify/)."""
    p = Path(__file__).resolve().parent
    for _ in range(10):
        if (p / "verify").is_dir():
            return p
        p = p.parent
    sys.exit("ERROR: Cannot find repo root (no verify/ directory found).")


def run_tier1(repo_root: Path, verbose: bool = False) -> bool:
    """Run Tier 1 pytest suite."""
    test_dir = repo_root / "n6-replication" / "tests" / "tier1"
    if not test_dir.is_dir():
        print(f"SKIP  Tier 1 -- {test_dir} not found")
        return False

    print("=" * 60)
    print("TIER 1: Pure-math identity tests (pytest)")
    print("=" * 60)

    cmd = [sys.executable, "-m", "pytest", str(test_dir), "-v", "--tb=short"]
    result = subprocess.run(cmd, cwd=str(repo_root))
    ok = result.returncode == 0

    print()
    print(f"TIER 1: {'PASS' if ok else 'FAIL'}")
    print()
    return ok


def run_tier2(repo_root: Path, timeout: int = 120) -> dict:
    """Run Tier 2: all verify/*.py and frontier_*.py scripts."""
    verify_dir = repo_root / "verify"
    scripts = sorted(verify_dir.glob("*.py"))
    if not scripts:
        print("SKIP  Tier 2 -- no scripts in verify/")
        return {"pass": 0, "fail": 0, "timeout": 0, "skip": 0}

    print("=" * 60)
    print(f"TIER 2: Verification scripts ({len(scripts)} files, timeout={timeout}s)")
    print("=" * 60)

    counts = {"pass": 0, "fail": 0, "timeout": 0, "skip": 0}
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo_root) + os.pathsep + env.get("PYTHONPATH", "")

    for script in scripts:
        name = script.name
        t0 = time.time()
        try:
            result = subprocess.run(
                [sys.executable, str(script)],
                cwd=str(repo_root),
                env=env,
                timeout=timeout,
                capture_output=True,
                text=True,
            )
            elapsed = time.time() - t0
            if result.returncode == 0:
                counts["pass"] += 1
                status = "PASS"
            else:
                counts["fail"] += 1
                status = "FAIL"
        except subprocess.TimeoutExpired:
            elapsed = timeout
            counts["timeout"] += 1
            status = "TIMEOUT"

        print(f"  {status:7s} {elapsed:6.1f}s  {name}")

    print()
    total = sum(counts.values())
    print(
        f"TIER 2: {counts['pass']}/{total} passed, "
        f"{counts['fail']} failed, {counts['timeout']} timeout"
    )
    print()
    return counts


def main():
    parser = argparse.ArgumentParser(
        description="Run TECS-L replication checks (no pip install needed)."
    )
    parser.add_argument(
        "--tier",
        nargs="+",
        type=int,
        default=[1, 2],
        choices=[1, 2],
        help="Which tiers to run (default: 1 2)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="Per-script timeout in seconds for Tier 2 (default: 120)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output",
    )
    args = parser.parse_args()

    repo_root = find_repo_root()
    print(f"Repo root: {repo_root}")
    print()

    results = {}

    if 1 in args.tier:
        results["tier1"] = run_tier1(repo_root, verbose=args.verbose)

    if 2 in args.tier:
        results["tier2"] = run_tier2(repo_root, timeout=args.timeout)

    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    all_ok = True
    if "tier1" in results:
        ok = results["tier1"]
        print(f"  Tier 1 (pytest):  {'PASS' if ok else 'FAIL'}")
        if not ok:
            all_ok = False

    if "tier2" in results:
        c = results["tier2"]
        tier2_ok = c["fail"] == 0 and c["timeout"] == 0
        print(f"  Tier 2 (verify):  {c['pass']}/{sum(c.values())} passed")
        if not tier2_ok:
            all_ok = False

    print()
    if all_ok:
        print("ALL PASSED")
    else:
        print("SOME FAILURES -- see above for details")
        sys.exit(1)


if __name__ == "__main__":
    main()
