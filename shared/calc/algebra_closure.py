#!/usr/bin/env python3
"""Algebraic Closure Checker — Relations among convergence points

Checks pairwise algebraic relations (a op b ~ c) among 9 convergence points,
finds ratio matches to {1/2, 1/3, 1/6}, and triples with ratio-sum ~ 1.
Based on H-CX-454/470.

Usage:
  python3 algebra_closure.py --check
  python3 algebra_closure.py --ratios
  python3 algebra_closure.py --sum-one
  python3 algebra_closure.py --texas
  python3 algebra_closure.py --check --ratios --sum-one
  python3 algebra_closure.py --custom "1.414,1.732,2.718"
"""

import argparse
import math
import itertools
import random

# ── 9 Convergence Points ────────────────────────────────────────────────────

CONVERGENCE_POINTS = {
    "sqrt(2)":  math.sqrt(2),
    "sqrt(3)":  math.sqrt(3),
    "5/6":      5 / 6,
    "e":        math.e,
    "zeta(3)":  1.2020569031,
    "ln(4/3)":  math.log(4 / 3),
    "ln(2)":    math.log(2),
    "gamma":    0.5772156649,
    "1/2":      0.5,
}

# Divisor reciprocals of 6
DIVISOR_RATIOS = {
    "1/2": 0.5,
    "1/3": 1 / 3,
    "1/6": 1 / 6,
}

# ── Operations ───────────────────────────────────────────────────────────────

def binary_ops(a, b):
    """Return list of (op_name, result) for a op b."""
    results = []
    results.append(("+", a + b))
    results.append(("-", a - b))
    if a > b:
        results.append(("-rev", b - a))
    results.append(("*", a * b))
    if b != 0:
        results.append(("/", a / b))
    if a != 0:
        results.append(("/rev", b / a))
    return results


# ── Check: pairwise closure ─────────────────────────────────────────────────

def run_check(points, threshold):
    """Find all a op b ~ c within threshold."""
    names = list(points.keys())
    vals = list(points.values())
    n = len(names)

    print(f"\n{'=' * 70}")
    print(f"  Algebraic Closure Check: {n} convergence points")
    print(f"  Threshold: {threshold * 100:.1f}%")
    print(f"{'=' * 70}\n")

    hits = []

    for i in range(n):
        for j in range(i, n):
            for op_name, result in binary_ops(vals[i], vals[j]):
                if not math.isfinite(result) or abs(result) < 1e-10:
                    continue
                for k in range(n):
                    if vals[k] == 0:
                        continue
                    rel_err = abs(result - vals[k]) / abs(vals[k])
                    if rel_err < threshold:
                        hits.append((names[i], op_name, names[j], names[k], result, vals[k], rel_err))

    # Print results
    if hits:
        print(f"  Found {len(hits)} closure relations:\n")
        print(f"  {'A':<10} {'op':>4} {'B':<10} {'= C':<10} {'Result':>10} {'Target':>10} {'Error':>10}")
        print(f"  {'-'*10} {'-'*4} {'-'*10} {'-'*10} {'-'*10} {'-'*10} {'-'*10}")
        for a, op, b, c, result, target, err in sorted(hits, key=lambda x: x[6]):
            op_sym = op.replace("rev", "~")
            print(f"  {a:<10} {op_sym:>4} {b:<10} {'~ ' + c:<10} {result:>10.6f} {target:>10.6f} {err:>10.4%}")
    else:
        print("  No closure relations found.")

    print(f"\n  Total closure hits: {len(hits)}")
    return hits


# ── Ratios: match to {1/2, 1/3, 1/6} ────────────────────────────────────────

def run_ratios(points, threshold):
    """Check pairwise ratios against divisor reciprocals of 6."""
    names = list(points.keys())
    vals = list(points.values())
    n = len(names)

    print(f"\n{'=' * 70}")
    print(f"  Ratio Check: a/b ~ {{1/2, 1/3, 1/6}}")
    print(f"  Threshold: {threshold * 100:.1f}%")
    print(f"{'=' * 70}\n")

    hits = []

    for i in range(n):
        for j in range(n):
            if i == j or vals[j] == 0:
                continue
            ratio = vals[i] / vals[j]
            for rname, rval in DIVISOR_RATIOS.items():
                rel_err = abs(ratio - rval) / rval
                if rel_err < threshold:
                    hits.append((names[i], names[j], ratio, rname, rval, rel_err))

    if hits:
        print(f"  Found {len(hits)} ratio matches:\n")
        print(f"  {'A':<10} {'/ B':<10} {'Ratio':>10} {'~ Target':<10} {'Error':>10}")
        print(f"  {'-'*10} {'-'*10} {'-'*10} {'-'*10} {'-'*10}")
        for a, b, ratio, rname, rval, err in sorted(hits, key=lambda x: x[5]):
            print(f"  {a:<10} {'/ ' + b:<10} {ratio:>10.6f} {'~ ' + rname:<10} {err:>10.4%}")
    else:
        print("  No ratio matches to {1/2, 1/3, 1/6} found.")

    print(f"\n  Total ratio hits: {len(hits)}")
    return hits


# ── Sum-one: triples with ratio-sum ~ 1 ─────────────────────────────────────

def run_sum_one(points, threshold):
    """Find triples (a, b, c) where a/b + c/d + e/f ~ 1 using ratios."""
    names = list(points.keys())
    vals = list(points.values())
    n = len(names)

    print(f"\n{'=' * 70}")
    print(f"  Sum-One Check: Find triples with ratio-sum ~ 1")
    print(f"  Testing: a_i/a_j + a_k/a_l + a_m/a_n ~ 1")
    print(f"  Threshold: {threshold * 100:.1f}%")
    print(f"{'=' * 70}\n")

    # Collect all distinct ratios first
    ratios = []
    for i in range(n):
        for j in range(n):
            if i == j or vals[j] == 0:
                continue
            r = vals[i] / vals[j]
            if 0 < r < 2:  # reasonable range
                ratios.append((f"{names[i]}/{names[j]}", r))

    hits = []
    seen = set()

    # Check triples of ratios summing to 1
    for i in range(len(ratios)):
        for j in range(i + 1, len(ratios)):
            for k in range(j + 1, len(ratios)):
                s = ratios[i][1] + ratios[j][1] + ratios[k][1]
                err = abs(s - 1.0)
                if err < threshold:
                    key = tuple(sorted([ratios[i][0], ratios[j][0], ratios[k][0]]))
                    if key not in seen:
                        seen.add(key)
                        hits.append((ratios[i][0], ratios[j][0], ratios[k][0],
                                     ratios[i][1], ratios[j][1], ratios[k][1], s, err))

    if hits:
        # Sort by error, show top 20
        hits.sort(key=lambda x: x[7])
        show = hits[:20]
        print(f"  Found {len(hits)} triples (showing top {len(show)}):\n")
        print(f"  {'R1':<14} {'R2':<14} {'R3':<14} {'Sum':>8} {'Error':>10}")
        print(f"  {'-'*14} {'-'*14} {'-'*14} {'-'*8} {'-'*10}")
        for r1n, r2n, r3n, r1v, r2v, r3v, s, err in show:
            print(f"  {r1n:<14} {r2n:<14} {r3n:<14} {s:>8.5f} {err:>10.6f}")
    else:
        print("  No sum-one triples found.")

    print(f"\n  Total sum-one triples: {len(hits)}")
    return hits


# ── Texas: Monte Carlo comparison ────────────────────────────────────────────

def run_texas(points, threshold, n_trials=10000):
    """Compare closure count vs random constant sets."""
    names = list(points.keys())
    vals = list(points.values())
    n = len(names)

    print(f"\n{'=' * 70}")
    print(f"  Texas Sharpshooter: Closure count vs random")
    print(f"  Trials: {n_trials}   Threshold: {threshold * 100:.1f}%")
    print(f"{'=' * 70}\n")

    def count_closures(values):
        """Count closure relations for a set of values."""
        count = 0
        nn = len(values)
        for i in range(nn):
            for j in range(i, nn):
                for op_name, result in binary_ops(values[i], values[j]):
                    if not math.isfinite(result) or abs(result) < 1e-10:
                        continue
                    for k in range(nn):
                        if values[k] == 0:
                            continue
                        rel_err = abs(result - values[k]) / abs(values[k])
                        if rel_err < threshold:
                            count += 1
        return count

    # Real count
    real_count = count_closures(vals)
    print(f"  Real convergence points: {real_count} closure relations")

    # Monte Carlo
    random.seed(42)
    val_range = (min(vals), max(vals))
    random_counts = []
    for _ in range(n_trials):
        rand_vals = [random.uniform(val_range[0], val_range[1]) for _ in range(n)]
        random_counts.append(count_closures(rand_vals))

    mean_rand = sum(random_counts) / len(random_counts)
    std_rand = (sum((x - mean_rand) ** 2 for x in random_counts) / len(random_counts)) ** 0.5

    if std_rand > 0:
        z_score = (real_count - mean_rand) / std_rand
    else:
        z_score = float('inf') if real_count > mean_rand else 0

    # p-value (one-sided)
    exceeding = sum(1 for c in random_counts if c >= real_count)
    p_value = exceeding / n_trials

    print(f"  Random baseline: {mean_rand:.1f} +/- {std_rand:.1f}")
    print(f"  Z-score: {z_score:.2f}")
    print(f"  p-value: {p_value:.4f}")
    print()

    # Histogram
    max_count = max(random_counts + [real_count])
    bins = 10
    bin_width = (max_count + 1) / bins
    hist = [0] * bins
    for c in random_counts:
        b = min(int(c / bin_width), bins - 1)
        hist[b] += 1

    max_bar = max(hist)
    bar_scale = 40 / max(max_bar, 1)

    print("  Distribution of random closure counts:")
    for i in range(bins):
        lo = i * bin_width
        hi = (i + 1) * bin_width
        bar = "#" * int(hist[i] * bar_scale)
        marker = " <-- REAL" if lo <= real_count < hi else ""
        print(f"  [{lo:5.1f}-{hi:5.1f}) {hist[i]:>5} |{bar}{marker}")

    print()
    if p_value < 0.01:
        print(f"  Result: STRUCTURALLY SIGNIFICANT (p={p_value:.4f})")
    elif p_value < 0.05:
        print(f"  Result: WEAKLY SIGNIFICANT (p={p_value:.4f})")
    else:
        print(f"  Result: NOT SIGNIFICANT (p={p_value:.4f})")

    return real_count, mean_rand, p_value


# ── Custom constants ─────────────────────────────────────────────────────────

def parse_custom(custom_str):
    """Parse comma-separated values into a dict."""
    vals = [float(x.strip()) for x in custom_str.split(",")]
    return {f"c{i}": v for i, v in enumerate(vals)}


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Algebraic Closure Checker")
    parser.add_argument("--check", action="store_true", help="Find pairwise closure relations")
    parser.add_argument("--ratios", action="store_true", help="Check ratios vs {1/2, 1/3, 1/6}")
    parser.add_argument("--sum-one", action="store_true", help="Find triples with ratio-sum ~ 1")
    parser.add_argument("--texas", action="store_true", help="Monte Carlo comparison vs random")
    parser.add_argument("--threshold", type=float, default=0.005, help="Match threshold (default 0.5%%)")
    parser.add_argument("--custom", type=str, help="Custom constant set (comma-separated)")

    args = parser.parse_args()

    points = CONVERGENCE_POINTS
    if args.custom:
        points = parse_custom(args.custom)
        print(f"  Using custom constants: {points}")

    ran_any = False

    if args.check:
        run_check(points, args.threshold)
        ran_any = True

    if args.ratios:
        run_ratios(points, args.threshold)
        ran_any = True

    if args.sum_one:
        run_sum_one(points, args.threshold)
        ran_any = True

    if args.texas:
        run_texas(points, args.threshold)
        ran_any = True

    if not ran_any:
        # Default: check + ratios
        run_check(points, args.threshold)
        run_ratios(points, args.threshold)


if __name__ == "__main__":
    main()
