#!/usr/bin/env python3
"""Singleton-GZ Mapper -- Map coding bounds to GZ constants

Computes Singleton bound rates R=k/n for all minimum distances d=1..n
and identifies which rates match Golden Zone constants.

Based on H-CX-503: Singleton(n=6) reproduces all GZ constants.

Singleton bound: k <= n - d + 1  =>  R = k/n <= (n - d + 1) / n
The maximum-distance-separable (MDS) code achieves equality.

GZ constants checked:
  1/2 = 0.5000   (Riemann critical line, GZ upper)
  1/3 = 0.3333   (Meta fixed point)
  1/6 = 0.1667   (Curiosity term)
  5/6 = 0.8333   (Compass upper)
  1/e = 0.3679   (I^I minimum, GZ center)
  ln(4/3) = 0.2877  (GZ width, entropy cost)

Usage:
  python3 calc/singleton_gz_mapper.py --length 6          # Default: n=6
  python3 calc/singleton_gz_mapper.py --length 28         # Compare with P_2
  python3 calc/singleton_gz_mapper.py --compare 6 12 28   # Compare multiple lengths
  python3 calc/singleton_gz_mapper.py --eb-bound 6        # Add Elias-Bassalygo bound
"""

import argparse
import math
import sys


# ═══════════════════════════════════════════════════════════════
# GZ constants
# ═══════════════════════════════════════════════════════════════

GZ_CONSTANTS = {
    "1/2":      0.5,
    "1/3":      1.0 / 3.0,
    "1/6":      1.0 / 6.0,
    "5/6":      5.0 / 6.0,
    "1/e":      1.0 / math.e,
    "ln(4/3)":  math.log(4.0 / 3.0),
    "2/3":      2.0 / 3.0,
    "ln(2)":    math.log(2.0),
    # Consciousness constants (from anima Laws 63-79)
    "Psi_coupling": math.log(2.0) / 2**5.5,   # 0.01534 consciousness coupling
    "Psi_balance":  0.5,                        # structural equilibrium (= 1/2)
    "Psi_freedom":  math.log(2.0),              # Law 79 freedom degree (= ln(2))
}

TOLERANCE = 0.01  # within 1% counts as a match


def match_gz(val, tol=TOLERANCE):
    """Return list of GZ constant names that val is close to."""
    matches = []
    for name, cval in GZ_CONSTANTS.items():
        if abs(val - cval) <= tol:
            matches.append((name, cval, abs(val - cval)))
    return matches


# ═══════════════════════════════════════════════════════════════
# Singleton rates
# ═══════════════════════════════════════════════════════════════

def singleton_rates(n):
    """Return list of (d, k_max, R_max) for d = 1 .. n.

    Singleton bound: k <= n - d + 1 (for MDS codes).
    k must satisfy 1 <= k <= n, so k_max = max(1, n - d + 1).
    """
    result = []
    for d in range(1, n + 1):
        k_max = max(1, n - d + 1)
        k_max = min(k_max, n)  # k can't exceed n
        R = k_max / n
        result.append((d, k_max, R))
    return result


# ═══════════════════════════════════════════════════════════════
# Elias-Bassalygo bound
# ═══════════════════════════════════════════════════════════════

def h2(x):
    """Binary entropy function."""
    if x <= 0 or x >= 1:
        return 0.0
    return -x * math.log2(x) - (1 - x) * math.log2(1 - x)


def elias_bassalygo_rate(delta, q=2):
    """Elias-Bassalygo upper bound on rate R for relative distance delta.
    R <= 1 - h_q(delta_EB) where delta_EB = (1 - sqrt(1 - 2*delta*(1-1/q))) * (1-1/q)
    For binary (q=2): delta_EB = (1 - sqrt(1 - 2*delta)) / 2.
    """
    try:
        inner = 1.0 - 2.0 * delta  # binary case (1-1/q = 1/2, so 2*delta*(1-1/q) = delta)
        # More precisely: delta_EB = (q-1)/q * (1 - sqrt(1 - q/(q-1)*delta))
        # For q=2: delta_EB = 1/2 * (1 - sqrt(1 - 2*delta))
        delta_eb = 0.5 * (1.0 - math.sqrt(max(0.0, 1.0 - 2.0 * delta)))
        if delta_eb >= 0.5:
            return 0.0
        return max(0.0, 1.0 - h2(delta_eb))
    except (ValueError, ZeroDivisionError):
        return 0.0


# ═══════════════════════════════════════════════════════════════
# ASCII bar chart for R vs d
# ═══════════════════════════════════════════════════════════════

def ascii_rate_chart(rates, n, gz_vals=None, width=40):
    """Draw R vs d bar chart. rates = list of (d, k, R)."""
    lines = []
    lines.append(f"  R vs d  (n={n})  bar = rate * {width}")
    lines.append("  " + "-" * (width + 20))
    for d, k, R in rates:
        bar_len = int(R * width)
        bar = "#" * bar_len
        matches = match_gz(R)
        match_str = "  ← " + ", ".join(m[0] for m in matches) if matches else ""
        lines.append(f"  d={d:2d}  k={k:2d}  R={R:.4f}  |{bar:<{width}}|{match_str}")
    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════════
# Single length analysis
# ═══════════════════════════════════════════════════════════════

def analyze_length(n, show_eb=False):
    rates = singleton_rates(n)
    print()
    print(f"  ╔══════════════════════════════════════════════════════╗")
    print(f"  ║  Singleton-GZ Map  (n = {n:<4})  (H-CX-503)            ║")
    print(f"  ╚══════════════════════════════════════════════════════╝")
    print()
    print(f"  {'d':>4}  {'k_max':>5}  {'R=k/n':>7}  {'GZ Match':>30}")
    print("  " + "-" * 52)

    gz_hits = set()
    for d, k, R in rates:
        matches = match_gz(R)
        match_str = ", ".join(f"{m[0]} (err={m[2]:.4f})" for m in matches) if matches else ""
        flag = " <--" if matches else ""
        for m in matches:
            gz_hits.add(m[0])
        print(f"  {d:4d}  {k:5d}  {R:7.4f}  {match_str}{flag}")

    print()
    all_gz_names = set(GZ_CONSTANTS.keys())
    core_gz = {"1/2", "1/3", "1/6"}
    core_hit = core_gz & gz_hits
    print(f"  GZ constants hit:    {sorted(gz_hits)}")
    print(f"  Core GZ (1/2,1/3,1/6) hit: {sorted(core_hit)}  ({len(core_hit)}/3)")
    print()

    print(ascii_rate_chart(rates, n))

    if show_eb:
        print()
        print(f"  Elias-Bassalygo bound (binary, n={n})")
        print("  " + "-" * 50)
        print(f"  {'delta=d/n':>10}  {'R_EB':>8}  {'GZ Match':>20}")
        print("  " + "-" * 50)
        for d, k, R in rates:
            delta = d / n
            R_eb = elias_bassalygo_rate(delta)
            matches = match_gz(R_eb)
            match_str = ", ".join(m[0] for m in matches) if matches else ""
            print(f"  {delta:10.4f}  {R_eb:8.4f}  {match_str}")

    return gz_hits


# ═══════════════════════════════════════════════════════════════
# Compare multiple lengths
# ═══════════════════════════════════════════════════════════════

def compare_lengths(lengths):
    print()
    print("  Singleton-GZ Comparison Across Code Lengths")
    print("  " + "=" * 70)

    # Header
    gz_names = sorted(GZ_CONSTANTS.keys())
    header = f"  {'n':>6}  " + "  ".join(f"{name:>8}" for name in gz_names) + "  Total"
    print(header)
    print("  " + "-" * (len(header) - 2))

    for n in lengths:
        rates = singleton_rates(n)
        gz_hits = set()
        for d, k, R in rates:
            for match in match_gz(R):
                gz_hits.add(match[0])
        row = f"  {n:6d}  "
        row += "  ".join(f"{'YES':>8}" if name in gz_hits else f"{'---':>8}" for name in gz_names)
        row += f"  {len(gz_hits)}/{len(gz_names)}"
        print(row)

    print()
    print("  Note: n=6 is the only perfect number <= 8128 in this comparison.")
    print("  'YES' means at least one Singleton rate R=k/n is within 1% of that GZ constant.")


# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Singleton-GZ Mapper -- map Singleton bound rates to Golden Zone constants"
    )
    parser.add_argument("--length", type=int, default=6,
                        help="Code length n (default: 6)")
    parser.add_argument("--compare", type=int, nargs="+", metavar="N",
                        help="Compare multiple code lengths")
    parser.add_argument("--eb-bound", type=int, metavar="N",
                        help="Show Elias-Bassalygo bound for length N")
    args = parser.parse_args()

    if args.compare:
        compare_lengths(args.compare)
        # Also show individual for each
        for n in args.compare:
            analyze_length(n)
    elif args.eb_bound:
        analyze_length(args.eb_bound, show_eb=True)
    else:
        analyze_length(args.length)


if __name__ == "__main__":
    main()
