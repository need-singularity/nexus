#!/usr/bin/env python3
"""
family_fdr_corrector.py -- Benjamini-Hochberg FDR correction across hypothesis families.

When 50+ hypotheses are tested on the same system, individual p-values are misleading.
This tool applies family-wise FDR correction (Benjamini-Hochberg, Bonferroni, Holm).

Usage:
  python3 calc/family_fdr_corrector.py --p "H-CX-280:0.01,H-CX-281:0.01,H-CX-282:0.005,H-CX-248:0.07"
  python3 calc/family_fdr_corrector.py --input hypothesis_pvalues.csv
  python3 calc/family_fdr_corrector.py --p "H1:0.001,H2:0.01,H3:0.03,H4:0.05,H5:0.08" --q 0.01
"""
import argparse
import csv
import sys

# ── Correction methods ────────────────────────────────────────────────
def bonferroni(p_values, alpha=0.05):
    """
    Bonferroni correction: reject if p_i < alpha / n.

    Returns list of (name, p, threshold, survives).
    """
    n = len(p_values)
    threshold = alpha / n
    results = []
    for name, p in p_values:
        results.append((name, p, threshold, p < threshold))
    return results, threshold


def holm_bonferroni(p_values, alpha=0.05):
    """
    Holm-Bonferroni step-down procedure.

    Sort by p ascending. For rank k (1-indexed), reject if p_k < alpha/(n-k+1).
    Stop at first non-rejection; all subsequent also fail.
    """
    n = len(p_values)
    sorted_pv = sorted(p_values, key=lambda x: x[1])
    results = []
    rejected_so_far = True

    for k, (name, p) in enumerate(sorted_pv, 1):
        threshold = alpha / (n - k + 1)
        if rejected_so_far and p < threshold:
            results.append((name, p, threshold, True))
        else:
            rejected_so_far = False
            results.append((name, p, threshold, False))

    return results


def benjamini_hochberg(p_values, q=0.05):
    """
    Benjamini-Hochberg procedure for FDR control.

    Sort by p ascending. For rank k (1-indexed), BH threshold = k * q / n.
    Find largest k where p_k <= k*q/n. Reject all ranks 1..k.
    """
    n = len(p_values)
    sorted_pv = sorted(p_values, key=lambda x: x[1])

    # Find the largest k where p_(k) <= k*q/n
    max_k = 0
    thresholds = []
    for k, (name, p) in enumerate(sorted_pv, 1):
        bh_thresh = k * q / n
        thresholds.append(bh_thresh)
        if p <= bh_thresh:
            max_k = k

    results = []
    for k, (name, p) in enumerate(sorted_pv, 1):
        bh_thresh = thresholds[k - 1]
        survives = (k <= max_k)
        results.append((name, p, bh_thresh, survives))

    return results


# ── Display ───────────────────────────────────────────────────────────
def print_table(title, results, note=""):
    """Print a formatted results table."""
    print(f"\n  {title}")
    if note:
        print(f"  {note}")
    print()
    print(f"  {'Rank':>4}  {'Hypothesis':<16}  {'p-value':>9}  {'Threshold':>10}  {'Survives?':>10}")
    print(f"  {'----':>4}  {'-'*16}  {'-'*9}  {'-'*10}  {'-'*10}")
    for i, (name, p, thresh, surv) in enumerate(results, 1):
        marker = "YES" if surv else "NO"
        icon = "  " if surv else "  "
        print(f"  {i:>4}  {name:<16}  {p:>9.5f}  {thresh:>10.5f}  {icon}{marker:>6}")
    n_survive = sum(1 for _, _, _, s in results if s)
    print(f"\n  Survives: {n_survive}/{len(results)}")


def analyze(p_values, q=0.05, alpha=0.05):
    """Run all three correction methods and print comparison."""
    n = len(p_values)

    print(f"\n{'='*70}")
    print(f"  Family-wise FDR Correction")
    print(f"{'='*70}")
    print(f"\n  Family size: {n} hypotheses tested")
    print(f"  FDR threshold: q = {q}")
    print(f"  FWER alpha: {alpha}")

    # Sort input for display
    sorted_input = sorted(p_values, key=lambda x: x[1])
    print(f"\n  Input p-values (sorted):")
    for name, p in sorted_input:
        print(f"    {name:<16}  p = {p:.5f}")

    # Benjamini-Hochberg
    bh_results = benjamini_hochberg(p_values, q=q)
    print_table(
        f"Benjamini-Hochberg (FDR q={q})",
        bh_results,
        f"BH threshold for rank k: k * {q} / {n}"
    )

    # Holm-Bonferroni
    holm_results = holm_bonferroni(p_values, alpha=alpha)
    print_table(
        f"Holm-Bonferroni (alpha={alpha})",
        holm_results,
        f"Holm threshold for rank k: {alpha} / ({n} - k + 1)"
    )

    # Bonferroni
    bonf_results, bonf_thresh = bonferroni(p_values, alpha=alpha)
    # Sort for display
    bonf_sorted = sorted(bonf_results, key=lambda x: x[1])
    bonf_sorted_with_thresh = [(n, p, bonf_thresh, s) for n, p, _, s in bonf_sorted]
    print_table(
        f"Bonferroni (alpha/n = {bonf_thresh:.5f})",
        bonf_sorted_with_thresh,
        f"Uniform threshold: {alpha} / {n} = {bonf_thresh:.5f}"
    )

    # Summary comparison
    bh_n = sum(1 for _, _, _, s in bh_results if s)
    holm_n = sum(1 for _, _, _, s in holm_results if s)
    bonf_n = sum(1 for _, _, _, s in bonf_results if s)

    print(f"\n  {'='*55}")
    print(f"  Summary Comparison")
    print(f"  {'='*55}")
    print(f"\n  {'Method':<25}  {'Survive':>8}  {'Power':>8}")
    print(f"  {'-'*25}  {'-'*8}  {'-'*8}")
    print(f"  {'Bonferroni':<25}  {bonf_n:>4}/{n:<3}  {'lowest':>8}")
    print(f"  {'Holm-Bonferroni':<25}  {holm_n:>4}/{n:<3}  {'medium':>8}")
    print(f"  {'Benjamini-Hochberg':<25}  {bh_n:>4}/{n:<3}  {'highest':>8}")
    print()

    # Identify which hypotheses fail all methods
    bh_pass = {name for name, _, _, s in bh_results if s}
    holm_pass = {name for name, _, _, s in holm_results if s}
    bonf_pass = {name for name, _, _, s in bonf_results if s}
    all_names = {name for name, _ in p_values}

    fail_all = all_names - bh_pass
    if fail_all:
        print(f"  Verdict:")
        for name in sorted(fail_all):
            p_val = dict(p_values)[name]
            print(f"    {name} (p={p_val:.5f}) does not survive ANY correction method.")
    else:
        print(f"  Verdict: All hypotheses survive at least one correction method.")

    pass_all = bonf_pass  # Bonferroni is strictest
    if pass_all:
        print(f"\n  Robust (survives all methods): {', '.join(sorted(pass_all))}")

    bh_only = bh_pass - holm_pass
    if bh_only:
        print(f"  BH-only (survives FDR but not FWER): {', '.join(sorted(bh_only))}")

    print(f"\n{'='*70}")


# ── Input parsing ─────────────────────────────────────────────────────
def parse_p_string(p_str):
    """Parse 'H1:0.01,H2:0.05' format."""
    pairs = []
    for item in p_str.split(","):
        item = item.strip()
        if ":" in item:
            name, p = item.rsplit(":", 1)
            pairs.append((name.strip(), float(p.strip())))
        else:
            # Just a number, auto-name
            pairs.append((f"H{len(pairs)+1}", float(item.strip())))
    return pairs


def parse_csv(filepath):
    """Parse CSV with columns: hypothesis,p_value (header optional)."""
    pairs = []
    with open(filepath, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 2:
                continue
            name = row[0].strip()
            try:
                p = float(row[1].strip())
                pairs.append((name, p))
            except ValueError:
                # Skip header or malformed rows
                continue
    return pairs


# ── CLI ───────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Family FDR Corrector -- Benjamini-Hochberg, Holm, and "
                    "Bonferroni correction for hypothesis families.")
    parser.add_argument("--p", type=str,
                        help='P-values as "H1:0.01,H2:0.05,..." or just "0.01,0.05,..."')
    parser.add_argument("--input", type=str,
                        help="CSV file with hypothesis,p_value columns")
    parser.add_argument("--q", type=float, default=0.05,
                        help="FDR threshold for Benjamini-Hochberg (default: 0.05)")
    parser.add_argument("--alpha", type=float, default=0.05,
                        help="FWER alpha for Bonferroni/Holm (default: 0.05)")
    args = parser.parse_args()

    p_values = None

    if args.p:
        p_values = parse_p_string(args.p)
    elif args.input:
        p_values = parse_csv(args.input)
    else:
        parser.print_help()
        return

    if not p_values:
        print("Error: no valid p-values found.")
        sys.exit(1)

    if len(p_values) < 2:
        print("Error: need at least 2 hypotheses for family-wise correction.")
        sys.exit(1)

    analyze(p_values, q=args.q, alpha=args.alpha)


if __name__ == "__main__":
    main()
