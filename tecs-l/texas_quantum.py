#!/usr/bin/env python3
"""Texas Sharpshooter Test — Quantum/Physics Discovery Exclusive

Scans the parameter space of each discovery to calculate chance hit probability (p-value),
and applies Bonferroni correction for multiple comparison problem.

Usage:
  python3 texas_quantum.py                        # Full test
  python3 texas_quantum.py --discovery "1/alpha"   # Specific discovery only
  python3 texas_quantum.py --monte-carlo 100000    # Monte Carlo iterations
"""

import argparse
import itertools
import math
import sys

import numpy as np

# ─── Number Theory Functions ───────────────────────────────────────────────

def divisor_sigma(n, k=1):
    """σ_k(n) = sum of k-th powers of divisors of n."""
    s = 0
    for d in range(1, n + 1):
        if n % d == 0:
            s += d ** k
    return s


def triangular(n):
    """T(n) = n(n+1)/2."""
    return n * (n + 1) // 2


# ─── Discovery List ───────────────────────────────────────────────

DISCOVERIES = [
    {
        "name": "1/alpha ≈ 137 + 1/28",
        "formula": "137 + 1/n",
        "param_range": (1, 1000),
        "target": 137.035999084,
        "threshold": 0.001,
    },
    {
        "name": "m_p/m_e ≈ sigma(6) × T(17)",
        "formula": "sigma(n) × T(k)",
        "param_range": [(1, 100), (1, 100)],
        "target": 1836.15267343,
        "threshold": 0.001,
    },
    {
        "name": "m_mu/m_e ≈ 28 × e²",
        "formula": "n × e²",
        "param_range": (1, 100),
        "target": 206.7682830,
        "threshold": 0.001,
    },
    {
        "name": "m_tau/m_e ≈ 3×19×61",
        "formula": "a × b × c",
        "param_range": [(1, 30), (1, 100), (1, 100)],
        "target": 3477.48,
        "threshold": 0.001,
    },
    {
        "name": "sin²θ_W ≈ 3/13",
        "formula": "a/b",
        "param_range": [(1, 20), (1, 200)],
        "target": 0.23122,
        "threshold": 0.005,
    },
    {
        "name": "e^(ln2·ln3) + 1 ≈ π",
        "formula": "a^ln(b) + 1",
        "param_range": None,
        "target": 3.14159265,
        "threshold": 0.0001,
    },
    {
        "name": "exp(1/(2e)) ≈ ζ(3)",
        "formula": "exp(1/(a×b))",
        "param_range": None,
        "target": 1.2020569031,
        "threshold": 0.0001,
    },
    {
        "name": "CMB ≈ e + 1/137",
        "formula": "e + 1/n",
        "param_range": (1, 1000),
        "target": 2.7255,
        "threshold": 0.001,
    },
]


# ─── Scan Engine ───────────────────────────────────────────────

def _relative_error(val, target):
    return abs(val - target) / max(abs(target), 1e-15)


def scan_1d(disc):
    """1D parameter scan. Returns: (hits, total)."""
    lo, hi = disc["param_range"]
    formula = disc["formula"]
    target = disc["target"]
    threshold = disc["threshold"]

    hits = 0
    total = hi - lo + 1

    for n in range(lo, hi + 1):
        if "137 + 1/n" in formula:
            val = 137.0 + 1.0 / n
        elif "n × e²" in formula:
            val = n * math.e ** 2
        elif "e + 1/n" in formula:
            val = math.e + 1.0 / n
        else:
            continue

        if _relative_error(val, target) < threshold:
            hits += 1

    return hits, total


def scan_2d(disc):
    """2D parameter scan. Returns: (hits, total)."""
    ranges = disc["param_range"]
    formula = disc["formula"]
    target = disc["target"]
    threshold = disc["threshold"]

    r0 = range(ranges[0][0], ranges[0][1] + 1)
    r1 = range(ranges[1][0], ranges[1][1] + 1)
    total = len(r0) * len(r1)
    hits = 0

    for a, b in itertools.product(r0, r1):
        if "sigma(n) × T(k)" in formula:
            val = divisor_sigma(a) * triangular(b)
        elif "a/b" in formula:
            if b == 0:
                continue
            val = a / b
        else:
            continue

        if _relative_error(val, target) < threshold:
            hits += 1

    return hits, total


def scan_3d(disc):
    """3D parameter scan. Returns: (hits, total)."""
    ranges = disc["param_range"]
    target = disc["target"]
    threshold = disc["threshold"]

    r0 = range(ranges[0][0], ranges[0][1] + 1)
    r1 = range(ranges[1][0], ranges[1][1] + 1)
    r2 = range(ranges[2][0], ranges[2][1] + 1)
    total = len(r0) * len(r1) * len(r2)
    hits = 0

    for a, b, c in itertools.product(r0, r1, r2):
        val = a * b * c
        if _relative_error(val, target) < threshold:
            hits += 1

    return hits, total


def scan_monte_carlo(disc, n_trials):
    """Special test: Monte Carlo simulation. Returns: (hits, total)."""
    rng = np.random.default_rng(42)
    target = disc["target"]
    threshold = disc["threshold"]
    formula = disc["formula"]

    # Constant range: random reals between 2~10 (small constants like e≈2.718)
    hits = 0
    total = n_trials

    for _ in range(n_trials):
        a = rng.uniform(1.5, 10.0)
        b = rng.uniform(1.5, 10.0)

        if "a^ln(b) + 1" in formula:
            try:
                val = a ** math.log(b) + 1.0
            except (ValueError, OverflowError):
                continue
        elif "exp(1/(a×b))" in formula:
            try:
                val = math.exp(1.0 / (a * b))
            except (ValueError, OverflowError):
                continue
        else:
            continue

        if _relative_error(val, target) < threshold:
            hits += 1

    return hits, total


def run_single(disc, n_monte_carlo):
    """Single discovery test. Returns: (hits, total)."""
    pr = disc["param_range"]

    if pr is None:
        return scan_monte_carlo(disc, n_monte_carlo)
    elif isinstance(pr, list):
        if len(pr) == 2:
            return scan_2d(disc)
        elif len(pr) == 3:
            return scan_3d(disc)
    else:
        return scan_1d(disc)

    return 0, 1  # fallback


# ─── Verdict ─────────────────────────────────────────────────────

def verdict(bonf_p):
    if bonf_p < 0.01:
        return "★ Structural"
    elif bonf_p < 0.05:
        return "△ Weak"
    else:
        return "✕ Chance"


# ─── Main ─────────────────────────────────────────────────────

def run(discoveries, n_monte_carlo, filter_name=None):
    if filter_name:
        discoveries = [d for d in discoveries if filter_name.lower() in d["name"].lower()]
        if not discoveries:
            print(f"  No discovery matching '{filter_name}'")
            sys.exit(1)

    n_total_disc = len(DISCOVERIES)  # Bonferroni always based on total count

    print("═" * 55)
    print(" Texas Sharpshooter — Quantum Discoveries")
    print("═" * 55)
    print()

    # Header
    hdr = f" {'Discovery':<26}│ {'Single p':>10} │ {'Bonf. p':>10} │ {'Verdict'}"
    print(hdr)
    print(f" {'─' * 26}┼{'─' * 12}┼{'─' * 12}┼{'─' * 12}")

    results = []
    total_combinations = 0
    significant = 0

    for disc in discoveries:
        hits, total = run_single(disc, n_monte_carlo)
        total_combinations += total

        if total == 0:
            p_single = 1.0
        else:
            p_single = hits / total

        p_bonf = min(p_single * n_total_disc, 1.0)
        verd = verdict(p_bonf)

        if "Structural" in verd:
            significant += 1

        results.append({
            "name": disc["name"],
            "hits": hits,
            "total": total,
            "p_single": p_single,
            "p_bonf": p_bonf,
            "verdict": verd,
        })

        # Truncate name (max 26 chars)
        short = disc["name"][:26]
        print(f" {short:<26}│ {p_single:>10.6f} │ {p_bonf:>10.6f} │ {verd}")

    print()
    print(f" Total combinations: ~{total_combinations:.2e}")
    print(f" Significant discoveries: {significant}/{len(discoveries)}")
    print("═" * 55)

    # Individual details
    print()
    print("─" * 55)
    print(" Detailed Results")
    print("─" * 55)
    for r in results:
        print(f"  {r['name']}")
        print(f"    hits={r['hits']}, total={r['total']}, "
              f"p={r['p_single']:.8f}, bonf={r['p_bonf']:.8f}")
    print("─" * 55)


def main():
    parser = argparse.ArgumentParser(
        description="Texas Sharpshooter Test — Quantum/Physics Discovery Exclusive"
    )
    parser.add_argument(
        "--discovery", type=str, default=None,
        help="Test specific discovery only (partial name match)"
    )
    parser.add_argument(
        "--monte-carlo", type=int, default=100000,
        help="Monte Carlo iterations (default 100000)"
    )
    args = parser.parse_args()

    run(DISCOVERIES, args.monte_carlo, args.discovery)


if __name__ == "__main__":
    main()