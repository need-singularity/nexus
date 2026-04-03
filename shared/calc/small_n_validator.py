#!/usr/bin/env python3
"""
small_n_validator.py -- Small-sample correlation validator.

Detects misleading correlations from tiny sample sizes (n<=5).
Reports exact p-values, power analysis, and minimum n for significance.

Usage:
  python3 calc/small_n_validator.py --x "4.21,2.31,2.08" --y "98.1,89.1,54.0" --label "H0_ep1 vs accuracy"
  python3 calc/small_n_validator.py --x "0.0358,0.0358,0.0338" --y "0.953,0.871,0.612" --label "dH0/dep vs AUC"
"""
import argparse
import math
import numpy as np
from scipy import stats


def validate_correlation(x, y, label="", alpha=0.05):
    """Validate correlation with small-n awareness."""
    n = len(x)
    x, y = np.array(x), np.array(y)

    print(f"{'='*60}")
    print(f"Small-N Correlation Validator")
    print(f"{'='*60}")
    print(f"Label: {label}")
    print(f"n = {n}")
    print()

    # Data
    print("Data:")
    for i in range(n):
        print(f"  x[{i}] = {x[i]:.6f}  y[{i}] = {y[i]:.6f}")
    print()

    # Unique values check
    x_unique = len(set(np.round(x, 6)))
    y_unique = len(set(np.round(y, 6)))
    if x_unique < n:
        print(f"  WARNING: Only {x_unique}/{n} unique x-values! Correlation driven by {n - x_unique + 1} identical points.")
    if y_unique < n:
        print(f"  WARNING: Only {y_unique}/{n} unique y-values!")
    print()

    # Spearman
    r_s, p_s = stats.spearmanr(x, y)
    print(f"Spearman:  r = {r_s:.4f},  p = {p_s:.4f}")

    # Pearson
    if n >= 3:
        r_p, p_p = stats.pearsonr(x, y)
        print(f"Pearson:   r = {r_p:.4f},  p = {p_p:.4f}")
    print()

    # Small-n warnings
    warnings = []
    if n <= 3:
        warnings.append(f"CRITICAL: n={n}. With 3 points, any monotonic order gives |r|=1.0.")
        warnings.append(f"  Random monotonic probability = 2/{math.factorial(n)} = {2/math.factorial(n):.2%}")
        warnings.append(f"  Minimum p-value achievable = {2/math.factorial(n):.4f}")
    elif n <= 5:
        warnings.append(f"WARNING: n={n} is very small. Results are fragile.")
    elif n <= 10:
        warnings.append(f"CAUTION: n={n}. Results should be interpreted carefully.")

    if p_s > alpha:
        warnings.append(f"NOT SIGNIFICANT: p={p_s:.4f} > alpha={alpha}")
    else:
        print(f"  Significant at alpha={alpha}")

    for w in warnings:
        print(f"  {w}")
    print()

    # Power analysis: minimum n for significance
    if abs(r_s) > 0.01:
        print("Minimum n for significance (at observed effect size):")
        for target_alpha in [0.05, 0.01, 0.001]:
            # Approximate: for Spearman, critical r decreases with n
            # Use t-distribution approximation
            for test_n in range(3, 200):
                t_crit = stats.t.ppf(1 - target_alpha / 2, test_n - 2)
                r_crit = t_crit / math.sqrt(t_crit**2 + test_n - 2)
                if abs(r_s) > r_crit:
                    print(f"  alpha={target_alpha}: n >= {test_n}")
                    break
            else:
                print(f"  alpha={target_alpha}: n >= 200+ (effect too small)")
    print()

    # Verdict
    print("VERDICT:")
    if n <= 3 and p_s > alpha:
        print("  INSUFFICIENT — Cannot establish significance with n<=3")
        print(f"  Status recommendation: PRELIMINARY / WEAK")
    elif n <= 5 and p_s > alpha:
        print(f"  WEAK — n={n} too small for reliable inference")
    elif p_s <= alpha:
        print(f"  SIGNIFICANT at p={p_s:.4f}, but n={n} means results are fragile")
        if n <= 10:
            print(f"  Recommend replication with larger sample")
    print(f"{'='*60}")

    return {
        "n": n, "r_spearman": r_s, "p_spearman": p_s,
        "significant": p_s <= alpha, "warnings": warnings
    }


def batch_validate(datasets):
    """Validate multiple hypothesis correlations at once."""
    results = []
    for label, x, y in datasets:
        r = validate_correlation(x, y, label)
        results.append((label, r))
        print()

    # Summary table
    print("\n" + "="*70)
    print("BATCH SUMMARY")
    print("="*70)
    print(f"{'Hypothesis':<35} {'n':>3} {'r':>7} {'p':>8} {'Sig?':>5}")
    print("-"*70)
    for label, r in results:
        sig = "YES" if r["significant"] else "NO"
        print(f"{label:<35} {r['n']:>3} {r['r_spearman']:>7.3f} {r['p_spearman']:>8.4f} {sig:>5}")
    print("="*70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Small-N Correlation Validator")
    parser.add_argument("--x", type=str, help="Comma-separated x values")
    parser.add_argument("--y", type=str, help="Comma-separated y values")
    parser.add_argument("--label", type=str, default="", help="Hypothesis label")
    parser.add_argument("--batch", action="store_true", help="Run all known weak hypotheses")
    args = parser.parse_args()

    if args.batch:
        batch_validate([
            ("H-CX-64 dH0/dep vs AUC",
             [0.0358, 0.0358, 0.0338], [0.953, 0.871, 0.612]),
            ("H-CX-101 H0_ep1 vs accuracy",
             [4.21, 2.31, 2.08], [98.1, 89.1, 54.0]),
            ("H-CX-103 tension*H0 vs acc (MNIST epochs)",
             # placeholder: need actual epoch data
             [0.1, 0.2, 0.3, 0.4, 0.5], [0.8, 0.85, 0.9, 0.93, 0.95]),
        ])
    elif args.x and args.y:
        x = [float(v) for v in args.x.split(",")]
        y = [float(v) for v in args.y.split(",")]
        validate_correlation(x, y, args.label)
    else:
        parser.print_help()
