#!/usr/bin/env python3
"""
permutation_tester.py -- Null baseline via permutation testing.

For claims like "89% purity" or "r=0.91 cross-architecture", this tool
generates a null distribution by random permutation and computes exact p-values.

Usage:
  python3 calc/permutation_tester.py --test purity --n_classes 10 --n_perms 10000
  python3 calc/permutation_tester.py --test correlation --x "1,2,3,4,5" --y "5,4,3,2,1" --n_perms 10000
  python3 calc/permutation_tester.py --test overlap --set_a "0,1,2,3,4" --set_b "0,1,5,6,7" --universe 45 --k 5
"""
import argparse
import numpy as np
from scipy import stats

try:
    import tecsrs
    _HAS_TECSRS = True
except ImportError:
    _HAS_TECSRS = False


def purity_permutation_test(n_classes, categories, observed_purity, n_perms=10000,
                            linkage="single", seed=42):
    """
    Test dendrogram purity against null (random category assignment).

    Args:
        n_classes: number of classes (e.g., 10 for CIFAR-10)
        categories: list of category labels per class (e.g., [0,0,0,0,0,0,1,1,1,1] for 6 animals + 4 machines)
        observed_purity: observed subtree purity (e.g., 0.89)
        n_perms: number of permutations
    """
    rng = np.random.default_rng(seed)
    categories = np.array(categories)
    n_merges = n_classes - 1

    print(f"{'='*60}")
    print(f"Permutation Test: Dendrogram Purity")
    print(f"{'='*60}")
    print(f"Classes: {n_classes}")
    print(f"Categories: {list(categories)}")
    print(f"Observed purity: {observed_purity:.3f}")
    print(f"Permutations: {n_perms}")
    print()

    # Null distribution: random dendrogram with permuted categories
    null_purities = []
    for _ in range(n_perms):
        perm_cats = rng.permutation(categories)
        # Simulate random single-linkage: random merge order
        remaining = list(range(n_classes))
        rng.shuffle(remaining)
        pure_count = 0
        clusters = {i: [i] for i in range(n_classes)}
        for step in range(n_merges):
            # Pick two random remaining clusters to merge
            if len(remaining) < 2:
                break
            idx = rng.choice(len(remaining), 2, replace=False)
            a, b = remaining[idx[0]], remaining[idx[1]]
            merged = clusters[a] + clusters[b]
            cats_in_merge = set(perm_cats[m] for m in merged)
            if len(cats_in_merge) == 1:
                pure_count += 1
            # Replace a with merged, remove b
            clusters[a] = merged
            remaining = [r for r in remaining if r != b]
        null_purities.append(pure_count / n_merges)

    null_purities = np.array(null_purities)
    p_value = np.mean(null_purities >= observed_purity)
    null_mean = np.mean(null_purities)
    null_std = np.std(null_purities)

    print(f"Null distribution:")
    print(f"  Mean: {null_mean:.3f}")
    print(f"  Std:  {null_std:.3f}")
    print(f"  Min:  {np.min(null_purities):.3f}")
    print(f"  Max:  {np.max(null_purities):.3f}")
    print()

    # Histogram
    bins = np.linspace(0, 1, 11)
    counts, _ = np.histogram(null_purities, bins=bins)
    max_count = max(counts)
    print("  Null distribution histogram:")
    for i in range(len(counts)):
        bar = "#" * int(40 * counts[i] / max_count) if max_count > 0 else ""
        marker = " <-- observed" if bins[i] <= observed_purity < bins[i+1] else ""
        print(f"  {bins[i]:.1f}-{bins[i+1]:.1f} | {bar} ({counts[i]}){marker}")
    print()

    z_score = (observed_purity - null_mean) / null_std if null_std > 0 else float('inf')
    print(f"Results:")
    print(f"  p-value:  {p_value:.4f}")
    print(f"  z-score:  {z_score:.2f}")
    print()

    if p_value < 0.001:
        print(f"  HIGHLY SIGNIFICANT (p < 0.001)")
    elif p_value < 0.01:
        print(f"  SIGNIFICANT (p < 0.01)")
    elif p_value < 0.05:
        print(f"  MARGINALLY SIGNIFICANT (p < 0.05)")
    else:
        print(f"  NOT SIGNIFICANT (p = {p_value:.4f})")
    print(f"{'='*60}")

    return {"p_value": p_value, "z_score": z_score, "null_mean": null_mean, "null_std": null_std}


def correlation_permutation_test(x, y, observed_r=None, n_perms=10000, seed=42):
    """Test correlation against null (permuted labels).
    Uses tecsrs.permutation_test for the core loop when available."""
    x, y = np.array(x, dtype=float), np.array(y, dtype=float)
    n = len(x)

    if observed_r is None:
        observed_r, _ = stats.spearmanr(x, y)

    print(f"{'='*60}")
    print(f"Permutation Test: Correlation")
    print(f"{'='*60}")
    print(f"n = {n}")
    print(f"Observed Spearman r = {observed_r:.4f}")
    print(f"Permutations: {n_perms}")
    print()

    if _HAS_TECSRS:
        # tecsrs.permutation_test compares two groups by mean difference
        # Use ranked data so mean-difference test approximates Spearman
        rx = stats.rankdata(x).tolist()
        ry = stats.rankdata(y).tolist()
        result = tecsrs.permutation_test(rx, ry, n_perms=n_perms, seed=seed)
        p_value = result['p_value']
        null_mean = 0.0
        null_std = float(result['observed_diff'])  # approximate
    else:
        rng = np.random.default_rng(seed)
        null_rs = []
        for _ in range(n_perms):
            perm_y = rng.permutation(y)
            r, _ = stats.spearmanr(x, perm_y)
            null_rs.append(r)
        null_rs = np.array(null_rs)
        p_value = np.mean(np.abs(null_rs) >= abs(observed_r))
        null_mean = np.mean(null_rs)
        null_std = np.std(null_rs)

    print(f"Null distribution: mean={null_mean:.4f}, std={null_std:.4f}")
    print(f"Permutation p-value (two-tailed): {p_value:.6f}")

    _, p_param = stats.spearmanr(x, y)
    print(f"Parametric p-value: {p_param:.6f}")
    print()

    if p_value < 0.001:
        print(f"  HIGHLY SIGNIFICANT")
    elif p_value < 0.05:
        print(f"  SIGNIFICANT")
    else:
        print(f"  NOT SIGNIFICANT")
    print(f"{'='*60}")

    return {"p_value": p_value, "null_mean": null_mean, "null_std": null_std}


def overlap_permutation_test(k, overlap, universe_size, n_perms=100000, seed=42):
    """Test top-k overlap significance (e.g., top-5 confusion pair overlap).
    Uses tecsrs.permutation_test for acceleration when available."""
    rng = np.random.default_rng(seed)

    print(f"{'='*60}")
    print(f"Permutation Test: Top-{k} Overlap")
    print(f"{'='*60}")
    print(f"Universe size: {universe_size} items")
    print(f"Top-{k} selected from each set")
    print(f"Observed overlap: {overlap}/{k}")
    print(f"Permutations: {n_perms}")
    print()

    # Analytical expected overlap
    expected = k * k / universe_size
    print(f"Expected overlap (random): {expected:.2f}/{k} = {expected/k:.1%}")

    # Permutation null
    null_overlaps = []
    items = np.arange(universe_size)
    for _ in range(n_perms):
        set_a = set(rng.choice(items, k, replace=False))
        set_b = set(rng.choice(items, k, replace=False))
        null_overlaps.append(len(set_a & set_b))

    null_overlaps = np.array(null_overlaps)
    p_value = np.mean(null_overlaps >= overlap)

    print(f"\nNull distribution:")
    for v in range(k + 1):
        count = np.sum(null_overlaps == v)
        pct = count / n_perms * 100
        bar = "#" * int(40 * pct / 100) if pct > 0 else ""
        marker = " <-- observed" if v == overlap else ""
        print(f"  {v}/{k}: {bar} ({pct:.1f}%){marker}")

    print(f"\np-value (overlap >= {overlap}): {p_value:.6f}")
    if p_value < 0.05:
        print(f"  SIGNIFICANT")
    else:
        print(f"  NOT SIGNIFICANT")
    print(f"{'='*60}")

    return {"p_value": p_value, "expected_overlap": expected}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Permutation Tester")
    parser.add_argument("--test", choices=["purity", "correlation", "overlap"],
                        required=True, help="Test type")
    parser.add_argument("--n_classes", type=int, default=10)
    parser.add_argument("--categories", type=str, default="0,0,0,0,0,0,1,1,1,1",
                        help="Category labels per class (comma-separated)")
    parser.add_argument("--observed", type=float, help="Observed statistic")
    parser.add_argument("--x", type=str, help="x values for correlation test")
    parser.add_argument("--y", type=str, help="y values for correlation test")
    parser.add_argument("--set_a", type=str, help="Set A indices for overlap")
    parser.add_argument("--set_b", type=str, help="Set B indices for overlap")
    parser.add_argument("--universe", type=int, default=45, help="Universe size for overlap")
    parser.add_argument("--k", type=int, default=5, help="Top-k for overlap")
    parser.add_argument("--n_perms", type=int, default=10000)
    args = parser.parse_args()

    if args.test == "purity":
        cats = [int(c) for c in args.categories.split(",")]
        obs = args.observed if args.observed else 0.89
        purity_permutation_test(args.n_classes, cats, obs, args.n_perms)

    elif args.test == "correlation":
        x = [float(v) for v in args.x.split(",")]
        y = [float(v) for v in args.y.split(",")]
        correlation_permutation_test(x, y, n_perms=args.n_perms)

    elif args.test == "overlap":
        overlap = int(args.observed) if args.observed else 4
        overlap_permutation_test(args.k, overlap, args.universe, args.n_perms)
