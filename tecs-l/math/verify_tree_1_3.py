#!/usr/bin/env python3
"""
Verify H-TREE-1 (Dynamical Systems) and H-TREE-3 (Probability) hypotheses.
R(n) = sigma(n)*phi(n) / (n*tau(n))

H-TREE-1: floor(R(n)) chain dynamics, cycles, basins, chain lengths
H-TREE-3: Distribution of R(n), R(n)/n statistics, scaling
"""

import math
import sys
from collections import defaultdict, Counter

# ─────────────────────────────────────────────────────────────
# Core arithmetic functions via sieve
# ─────────────────────────────────────────────────────────────

def compute_functions(N):
    """Compute sigma(n), phi(n), tau(n) for all n <= N using sieves."""
    sigma = [0] * (N + 1)
    phi = list(range(N + 1))
    tau = [0] * (N + 1)

    for d in range(1, N + 1):
        for multiple in range(d, N + 1, d):
            tau[multiple] += 1
            sigma[multiple] += d

    for p in range(2, N + 1):
        if phi[p] == p:  # p is prime
            for multiple in range(p, N + 1, p):
                phi[multiple] = phi[multiple] // p * (p - 1)

    return sigma, phi, tau


def R_exact(n, sigma, phi, tau):
    """Return R(n) = sigma(n)*phi(n) / (n*tau(n)) as (numerator, denominator)."""
    num = sigma[n] * phi[n]
    den = n * tau[n]
    g = math.gcd(num, den)
    return num // g, den // g


def R_float(n, sigma, phi, tau):
    """Return R(n) as float."""
    return (sigma[n] * phi[n]) / (n * tau[n])


def R_floor(n, sigma, phi, tau):
    """Return floor(R(n))."""
    return (sigma[n] * phi[n]) // (n * tau[n])


# ─────────────────────────────────────────────────────────────
# ASCII histogram helper
# ─────────────────────────────────────────────────────────────

def ascii_histogram(data, bins=20, width=50, title=""):
    """Print ASCII histogram of data."""
    if not data:
        print("  (no data)")
        return
    mn, mx = min(data), max(data)
    if mn == mx:
        print(f"  All values = {mn}")
        return

    if title:
        print(f"\n  {title}")
        print(f"  {'─' * (width + 20)}")

    bin_width = (mx - mn) / bins
    counts = [0] * bins
    for v in data:
        idx = min(int((v - mn) / bin_width), bins - 1)
        counts[idx] += 1

    max_count = max(counts) if counts else 1
    for i in range(bins):
        lo = mn + i * bin_width
        hi = lo + bin_width
        bar_len = int(counts[i] / max_count * width) if max_count > 0 else 0
        bar = '█' * bar_len
        print(f"  [{lo:10.3f},{hi:10.3f}) |{bar:<{width}}| {counts[i]}")


def ascii_int_histogram(counter, width=50, title="", max_keys=30):
    """Print histogram for integer-keyed Counter."""
    if not counter:
        print("  (no data)")
        return

    if title:
        print(f"\n  {title}")
        print(f"  {'─' * (width + 20)}")

    keys = sorted(counter.keys())
    if len(keys) > max_keys:
        keys = keys[:max_keys]
        print(f"  (showing first {max_keys} keys)")

    max_count = max(counter[k] for k in keys)
    for k in keys:
        bar_len = int(counter[k] / max_count * width) if max_count > 0 else 0
        bar = '█' * bar_len
        print(f"  {k:6d} |{bar:<{width}}| {counter[k]}")


# ─────────────────────────────────────────────────────────────
# H-TREE-1: Dynamical Systems Branch
# ─────────────────────────────────────────────────────────────

def verify_htree1(sigma_arr, phi_arr, tau_arr, N_chain, N_fixed, N_basin):
    print("=" * 70)
    print("H-TREE-1: DYNAMICAL SYSTEMS BRANCH")
    print("R-chain: n → floor(R(n)) → floor(R(floor(R(n)))) → ... → 1 or cycle")
    print("=" * 70)

    # --- 1. Compute R-chain orbits for n=2..N_chain ---
    print(f"\n## 1. R-chain orbits for n=2..{N_chain}")

    chain_lengths = {}  # n -> steps to reach 1 (or -1 if cycle)
    chains_through_6 = 0
    longest_chain_len = 0
    longest_chain_start = 0
    longest_chain_path = []
    cycle_found = []

    for n in range(2, N_chain + 1):
        path = [n]
        current = n
        visited = {n}
        steps = 0

        while current > 1:
            if current > len(sigma_arr) - 1:
                # Out of sieve range, stop
                steps = -1
                break
            fl = R_floor(current, sigma_arr, phi_arr, tau_arr)
            if fl == 0:
                # floor(R(n)) = 0, chain terminates
                steps = len(path)
                break
            if fl in visited and fl != 1:
                # Cycle detected!
                cycle_found.append((n, fl, path))
                steps = -1
                break
            path.append(fl)
            visited.add(fl)
            current = fl
            steps += 1

        if steps >= 0:
            chain_lengths[n] = len(path) - 1  # steps (edges)
        else:
            chain_lengths[n] = -1

        # Check if 6 is in the path
        if 6 in path:
            chains_through_6 += 1

        # Track longest
        if len(path) > longest_chain_len and steps >= 0:
            longest_chain_len = len(path)
            longest_chain_start = n
            longest_chain_path = path[:]

    # Chain length distribution
    valid_lengths = [v for v in chain_lengths.values() if v >= 0]
    length_counter = Counter(valid_lengths)

    print(f"\n### Chain length distribution (n=2..{N_chain})")
    print(f"| Length | Count | Fraction |")
    print(f"|--------|-------|----------|")
    total = len(valid_lengths)
    for k in sorted(length_counter.keys()):
        frac = length_counter[k] / total
        print(f"| {k:6d} | {length_counter[k]:5d} | {frac:.6f} |")

    ascii_int_histogram(length_counter, title="Chain Length Histogram")

    # --- 2. Cycles / fixed points ---
    print(f"\n## 2. Fixed points: floor(R(n)) = n for n=2..{N_fixed}")
    fixed_points = []
    for n in range(2, min(N_fixed + 1, len(sigma_arr))):
        fl = R_floor(n, sigma_arr, phi_arr, tau_arr)
        if fl == n:
            fixed_points.append(n)

    if fixed_points:
        print(f"  Fixed points found: {fixed_points[:30]}")
        if len(fixed_points) > 30:
            print(f"  ... and {len(fixed_points) - 30} more")
    else:
        print("  No fixed points found (other than trivial n=1).")

    # Also check: floor(R(n)) = 1 (maps to 1 directly)
    maps_to_1 = []
    for n in range(2, min(N_chain + 1, len(sigma_arr))):
        fl = R_floor(n, sigma_arr, phi_arr, tau_arr)
        if fl == 1:
            maps_to_1.append(n)
    print(f"\n  Numbers with floor(R(n))=1 (n=2..{N_chain}): {len(maps_to_1)}")
    if len(maps_to_1) <= 50:
        print(f"  Values: {maps_to_1}")
    else:
        print(f"  First 50: {maps_to_1[:50]}")

    print(f"\n  Cycles detected: {len(cycle_found)}")
    if cycle_found:
        for start, cyc_val, path in cycle_found[:10]:
            print(f"    n={start}: cycle at {cyc_val}, path={path[:10]}...")

    # --- 3. Basin of attraction of n=6 ---
    print(f"\n## 3. Basin of attraction of n=6")
    print(f"  Chains passing through 6 (n=2..{N_chain}): {chains_through_6}")
    print(f"  Fraction: {chains_through_6 / (N_chain - 1):.6f}")

    # Find direct preimages: floor(R(m)) = 6
    preimage_6 = []
    for m in range(2, min(N_basin + 1, len(sigma_arr))):
        if R_floor(m, sigma_arr, phi_arr, tau_arr) == 6:
            preimage_6.append(m)
    print(f"  Direct preimages (floor(R(m))=6, m≤{N_basin}): {len(preimage_6)}")
    if len(preimage_6) <= 30:
        print(f"  Values: {preimage_6}")
    else:
        print(f"  First 30: {preimage_6[:30]}")

    # --- 4. Longest chain ---
    print(f"\n## 4. Longest chain (n≤{N_chain})")
    print(f"  Start: n={longest_chain_start}")
    print(f"  Length: {longest_chain_len - 1} steps ({longest_chain_len} nodes)")
    print(f"  Path: {' → '.join(str(x) for x in longest_chain_path)}")

    # Show some notable long chains
    print(f"\n### Top 20 longest chains:")
    sorted_chains = sorted(chain_lengths.items(), key=lambda x: -x[1])
    print(f"| Rank | Start n | Length |")
    print(f"|------|---------|--------|")
    for i, (n, l) in enumerate(sorted_chains[:20]):
        print(f"| {i+1:4d} | {n:7d} | {l:6d} |")

    # --- 5. Statistics ---
    if valid_lengths:
        mean_len = sum(valid_lengths) / len(valid_lengths)
        median_len = sorted(valid_lengths)[len(valid_lengths) // 2]
        max_len = max(valid_lengths)
        print(f"\n### Summary statistics (chain lengths)")
        print(f"| Statistic | Value |")
        print(f"|-----------|-------|")
        print(f"| Mean      | {mean_len:.4f} |")
        print(f"| Median    | {median_len} |")
        print(f"| Max       | {max_len} |")
        print(f"| Total chains | {total} |")


# ─────────────────────────────────────────────────────────────
# H-TREE-3: Probability Branch
# ─────────────────────────────────────────────────────────────

def verify_htree3(sigma_arr, phi_arr, tau_arr, N_prob):
    print("\n" + "=" * 70)
    print("H-TREE-3: PROBABILITY BRANCH")
    print("Distribution of R(n) = sigma(n)*phi(n) / (n*tau(n))")
    print("=" * 70)

    # --- 1. Compute R(n) for n=2..N_prob ---
    print(f"\n## 1. R(n) for n=2..{N_prob}")

    R_values = []  # (n, R_float)
    R_over_n = []  # R(n)/n ratios

    for n in range(2, N_prob + 1):
        rv = R_float(n, sigma_arr, phi_arr, tau_arr)
        R_values.append((n, rv))
        R_over_n.append(rv / n)

    r_floats = [rv for _, rv in R_values]

    # --- 2. Statistics of R(n)/n ---
    print(f"\n## 2. R(n)/n statistics (n=2..{N_prob})")
    mean_ratio = sum(R_over_n) / len(R_over_n)
    sorted_ratios = sorted(R_over_n)
    median_ratio = sorted_ratios[len(sorted_ratios) // 2]
    var_ratio = sum((x - mean_ratio) ** 2 for x in R_over_n) / len(R_over_n)
    std_ratio = var_ratio ** 0.5

    print(f"| Statistic | Value |")
    print(f"|-----------|-------|")
    print(f"| Mean(R(n)/n) | {mean_ratio:.6f} |")
    print(f"| Median(R(n)/n) | {median_ratio:.6f} |")
    print(f"| Std(R(n)/n) | {std_ratio:.6f} |")
    print(f"| Min(R(n)/n) | {min(R_over_n):.6f} (n={R_values[R_over_n.index(min(R_over_n))][0]}) |")
    print(f"| Max(R(n)/n) | {max(R_over_n):.6f} (n={R_values[R_over_n.index(max(R_over_n))][0]}) |")

    # --- 3. Histogram of R(n)/n ---
    ascii_histogram(R_over_n, bins=25, title="Histogram of R(n)/n")

    # Also log-scale histogram
    log_R = [math.log(rv) for _, rv in R_values if rv > 0]
    ascii_histogram(log_R, bins=25, title="Histogram of log(R(n))")

    # --- 4. Scaling: E[R(n)] for n in [N, 2N] ---
    print(f"\n## 4. Scaling of E[R(n)] in windows [N, 2N]")
    print(f"| N | E[R(n)] in [N,2N] | E[R(n)]/N | Samples |")
    print(f"|---|--------------------|-----------|---------|")

    for N_win in [100, 500, 1000, 2000, 5000, 10000, 20000]:
        lo = N_win
        hi = min(2 * N_win, N_prob)
        if lo >= N_prob:
            break
        vals = [R_float(n, sigma_arr, phi_arr, tau_arr) for n in range(lo, hi + 1)]
        mean_r = sum(vals) / len(vals)
        print(f"| {N_win:6d} | {mean_r:18.4f} | {mean_r/N_win:.6f} | {len(vals)} |")

    # --- 5. Fraction thresholds ---
    print(f"\n## 5. Fraction of n with R(n) > n/2, > n/3, < n/10")
    gt_half = sum(1 for n, rv in R_values if rv > n / 2)
    gt_third = sum(1 for n, rv in R_values if rv > n / 3)
    lt_tenth = sum(1 for n, rv in R_values if rv < n / 10)
    total = len(R_values)

    print(f"| Condition | Count | Fraction |")
    print(f"|-----------|-------|----------|")
    print(f"| R(n) > n/2 | {gt_half} | {gt_half/total:.6f} |")
    print(f"| R(n) > n/3 | {gt_third} | {gt_third/total:.6f} |")
    print(f"| R(n) < n/10 | {lt_tenth} | {lt_tenth/total:.6f} |")

    # --- 6. Convergence of R(n)/n as n grows ---
    print(f"\n## 6. R(n)/n concentration as n grows")
    print(f"  (Mean R(n)/n in windows of size 1000)")
    print(f"| Window | Mean(R/n) | Std(R/n) |")
    print(f"|--------|-----------|----------|")

    window_size = 1000
    window_means = []
    window_stds = []
    for start in range(0, len(R_over_n) - window_size + 1, window_size):
        chunk = R_over_n[start:start + window_size]
        m = sum(chunk) / len(chunk)
        v = sum((x - m) ** 2 for x in chunk) / len(chunk)
        s = v ** 0.5
        n_lo = start + 2
        n_hi = start + window_size + 1
        window_means.append(m)
        window_stds.append(s)
        if len(window_means) <= 30 or start % 5000 == 0:
            print(f"| [{n_lo:6d},{n_hi:6d}) | {m:.6f} | {s:.6f} |")

    if window_means:
        print(f"\n  Overall trend: mean(R/n) from {window_means[0]:.6f} to {window_means[-1]:.6f}")
        print(f"  Overall trend: std(R/n) from {window_stds[0]:.6f} to {window_stds[-1]:.6f}")

    # --- 7. Integer R(n) statistics ---
    print(f"\n## 7. Integer R(n) (exact divisibility)")
    integer_count = 0
    integer_vals = Counter()
    for n in range(2, N_prob + 1):
        num = sigma_arr[n] * phi_arr[n]
        den = n * tau_arr[n]
        if num % den == 0:
            integer_count += 1
            integer_vals[num // den] += 1

    print(f"  Count of n with integer R(n): {integer_count} / {N_prob - 1} = {integer_count/(N_prob-1):.6f}")
    print(f"\n  Distribution of integer R(n) values:")
    print(f"  | R(n) | Count |")
    print(f"  |------|-------|")
    for k in sorted(integer_vals.keys())[:30]:
        print(f"  | {k:4d} | {integer_vals[k]:5d} |")


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Sieve up to max needed N
    N_SIEVE = 100000  # covers chain lookups and probability analysis
    # H-TREE-1 params
    N_CHAIN = 50000   # chain orbits n=2..50000
    N_FIXED = 100000  # fixed point search
    N_BASIN = 100000  # basin of attraction search
    # H-TREE-3 params
    N_PROB = 50000    # probability distribution analysis

    print(f"Sieving arithmetic functions up to {N_SIEVE}...")
    sys.stdout.flush()
    sigma_arr, phi_arr, tau_arr = compute_functions(N_SIEVE)
    print(f"Sieve complete.\n")

    # Spot check: R(6) should be 1
    r6 = R_float(6, sigma_arr, phi_arr, tau_arr)
    print(f"Sanity check: R(6) = sigma(6)*phi(6)/(6*tau(6)) = {sigma_arr[6]}*{phi_arr[6]}/(6*{tau_arr[6]}) = {r6}")
    assert abs(r6 - 1.0) < 1e-10, f"R(6) should be 1, got {r6}"
    print(f"R(6) = 1 ✓\n")

    verify_htree1(sigma_arr, phi_arr, tau_arr, N_CHAIN, N_FIXED, N_BASIN)
    print()
    verify_htree3(sigma_arr, phi_arr, tau_arr, N_PROB)

    print("\n" + "=" * 70)
    print("VERIFICATION COMPLETE")
    print("=" * 70)
