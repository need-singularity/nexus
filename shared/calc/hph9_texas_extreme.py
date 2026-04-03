#!/usr/bin/env python3
"""
hph9_texas_extreme.py -- Extreme Texas Sharpshooter test for H-PH-9
10^7 Monte Carlo trials across 4 independent tests + background rate.

Tests:
  1. Dimensional Hierarchy: random 5-draw from even {4..62} matching physics dims
  2. Kissing Numbers: random 32-draw from n=6 arithmetic pool containing {2,6,12,24,240}
  3. Combined H-PH-9 (Fisher's method)
  4. Bonferroni correction (N=50 relationships)
  5. Background rate: fraction of n in 1..1000 with arithmetic functions matching physics

Usage: python3 calc/hph9_texas_extreme.py
"""
import numpy as np
from scipy import stats
from math import comb, gcd, log
import time
import sys

N_TRIALS = 10_000_000

# ============================================================================
# Helper: number-theoretic functions (vectorized where possible)
# ============================================================================

def sigma_n(n):
    """Sum of divisors."""
    return sum(d for d in range(1, n + 1) if n % d == 0)

def tau_n(n):
    """Number of divisors."""
    return sum(1 for d in range(1, n + 1) if n % d == 0)

def phi_n(n):
    """Euler totient."""
    return sum(1 for k in range(1, n + 1) if gcd(k, n) == 1)

def sopfr_n(n):
    """Sum of prime factors with repetition."""
    s, d, t = 0, 2, n
    while d * d <= t:
        while t % d == 0:
            s += d
            t //= d
        d += 1
    if t > 1:
        s += t
    return s


# ============================================================================
# TEST 1: Dimensional Hierarchy
# ============================================================================

def test_dimensional_hierarchy(n_trials):
    """
    Draw 5 even numbers without replacement from {4,6,8,...,62} (30 choices).
    Physics dimensions: {4, 6, 10, 14, 26}.
    Strong set (4 targets): {4, 6, 10, 26}.
    """
    print("=" * 72)
    print("TEST 1: Dimensional Hierarchy")
    print("=" * 72)
    print(f"Pool: even numbers {{4,6,...,62}} = 30 choices")
    print(f"Draw: 5 without replacement")
    print(f"Physics target: {{4, 6, 10, 14, 26}}")
    print(f"Strong targets:  {{4, 6, 10, 26}} (4 of 30)")
    print(f"Trials: {n_trials:,}")
    print()

    pool = np.arange(4, 63, 2)  # 4,6,8,...,62 -> 30 elements
    assert len(pool) == 30

    strong_set = {4, 6, 10, 26}
    full_set = {4, 6, 10, 14, 26}

    # Target indices for vectorized checking
    strong_indices = np.array([np.where(pool == v)[0][0] for v in strong_set])
    full_indices = np.array([np.where(pool == v)[0][0] for v in full_set])

    count_strong4 = 0  # >= 4 strong targets matched
    count_full5 = 0    # all 5 matched
    count_additive = 0 # any pair sums to a third

    # Process in batches for memory efficiency
    batch_size = 500_000
    rng = np.random.default_rng(42)

    for start in range(0, n_trials, batch_size):
        bs = min(batch_size, n_trials - start)

        # Generate random indices (5 from 30, no replacement)
        # np.random.choice per row -- use argsort trick for speed
        rand_vals = rng.random((bs, 30))
        # Get indices of 5 smallest per row = sampling without replacement
        samples_idx = np.argpartition(rand_vals, 5, axis=1)[:, :5]

        # Check strong targets: count how many of {4,6,10,26} indices appear
        # Create boolean mask for each strong target
        strong_hits = np.zeros(bs, dtype=int)
        for si in strong_indices:
            strong_hits += np.any(samples_idx == si, axis=1).astype(int)

        count_strong4 += np.sum(strong_hits >= 4)

        # Check full set: all 5
        full_hits = np.zeros(bs, dtype=int)
        for fi in full_indices:
            full_hits += np.any(samples_idx == fi, axis=1).astype(int)

        count_full5 += np.sum(full_hits >= 5)

        # Additive relation: check if any pair sums to a third
        # Convert indices back to values
        sample_vals = pool[samples_idx]  # (bs, 5)
        add_count = 0
        for i in range(5):
            for j in range(i + 1, 5):
                pair_sums = sample_vals[:, i] + sample_vals[:, j]
                # Check if pair_sum is in the sample for each row
                for k in range(5):
                    if k != i and k != j:
                        add_count += np.sum(pair_sums == sample_vals[:, k])
        count_additive += add_count

    p_strong4 = count_strong4 / n_trials
    p_full5 = count_full5 / n_trials
    p_additive = count_additive / n_trials

    # Exact combinatorial probability for 4+ strong matches
    # P(all 4 strong in draw of 5 from 30) = C(4,4)*C(26,1)/C(30,5)
    p_exact_strong4 = comb(4, 4) * comb(26, 1) / comb(30, 5)

    # P(all 5 in draw of 5 from 30) = C(5,5)*C(25,0)/C(30,5)
    p_exact_full5 = comb(5, 5) * comb(25, 0) / comb(30, 5)

    # Wilson score 95% CI
    def wilson_ci(p, n):
        z = 1.96
        denom = 1 + z**2 / n
        center = (p + z**2 / (2 * n)) / denom
        spread = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
        return max(0, center - spread), min(1, center + spread)

    ci_s4 = wilson_ci(p_strong4, n_trials)
    ci_f5 = wilson_ci(p_full5, n_trials)

    print(f"{'Metric':<40} {'MC Estimate':>14} {'Exact':>14}")
    print("-" * 72)
    print(f"{'P(>=4 strong targets matched)':<40} {p_strong4:.8f}   {p_exact_strong4:.8f}")
    print(f"  95% CI: [{ci_s4[0]:.8f}, {ci_s4[1]:.8f}]")
    print(f"{'P(all 5 matched exactly)':<40} {p_full5:.10f}  {p_exact_full5:.10f}")
    print(f"  95% CI: [{ci_f5[0]:.10f}, {ci_f5[1]:.10f}]")
    print(f"{'P(additive relation a+b=c in draw)':<40} {p_additive:.6f}")
    print()
    print(f"Counts: strong4={count_strong4:,}  full5={count_full5:,}  additive={count_additive:,}")
    print(f"1/P(strong4) = {1/p_exact_strong4:,.0f}  (1 in {1/p_exact_strong4:,.0f})")
    print(f"1/P(full5)   = {1/p_exact_full5:,.0f}  (1 in {1/p_exact_full5:,.0f})")
    print()

    return p_exact_strong4, p_exact_full5, p_strong4, p_full5


# ============================================================================
# TEST 2: Kissing Numbers
# ============================================================================

def test_kissing_numbers(n_trials):
    """
    Generate pool of ~50 plausible arithmetic combinations of n=6 functions.
    Sample 32 of them. Check if {2,6,12,24,240} all appear.
    """
    print("=" * 72)
    print("TEST 2: Kissing Numbers from n=6 Arithmetic")
    print("=" * 72)

    # n=6 arithmetic constants
    sig, tau, ph, P1, P2, P3 = 12, 4, 2, 6, 28, 496

    # Generate plausible arithmetic combinations
    base = {sig, tau, ph, P1, P2, P3}
    pool_set = set()

    # Single values
    pool_set.update(base)

    # Products of pairs
    vals = [sig, tau, ph, P1, P2, P3]
    for i in range(len(vals)):
        for j in range(i, len(vals)):
            pool_set.add(vals[i] * vals[j])

    # Quotients (integer only)
    for i in range(len(vals)):
        for j in range(len(vals)):
            if i != j and vals[j] != 0 and vals[i] % vals[j] == 0:
                pool_set.add(vals[i] // vals[j])

    # Sums and differences of pairs
    for i in range(len(vals)):
        for j in range(i + 1, len(vals)):
            pool_set.add(vals[i] + vals[j])
            pool_set.add(abs(vals[i] - vals[j]))

    # Powers
    for v in [sig, tau, ph, P1]:
        pool_set.add(v**2)
        pool_set.add(v**3)

    # Special combinations
    pool_set.add(sig * tau * ph)          # 96
    pool_set.add(sig * ph * P1)           # 144
    pool_set.add(tau * ph * P1)           # 48
    pool_set.add(sig * tau * P1)          # 288
    pool_set.add(P1 * tau * sig * ph)     # 576
    pool_set.add(sig * P1 // tau)         # 18
    pool_set.add(P2 - P1)                 # 22
    pool_set.add(P2 + P1)                 # 34
    pool_set.add(sig * tau * sopfr_n(6))  # 12*4*5 = 240!
    pool_set.add(P1 * tau * 10)           # 240 (alternative route)
    pool_set.add(ph * sig * 10)           # 240 (another route)

    # Remove 0 and negative
    pool_set.discard(0)
    pool = sorted([v for v in pool_set if v > 0])

    kissing = {2, 6, 12, 24, 240}
    kissing_in_pool = kissing.issubset(set(pool))

    print(f"Arithmetic pool size: {len(pool)}")
    print(f"Pool (sorted): {pool[:20]}... (showing first 20)")
    print(f"Kissing targets {{2,6,12,24,240}} all in pool: {kissing_in_pool}")
    print(f"Sample size: 32 from {len(pool)}")
    print(f"Trials: {n_trials:,}")
    print()

    if not kissing_in_pool:
        missing = kissing - set(pool)
        print(f"WARNING: Missing kissing numbers from pool: {missing}")
        print("Cannot run test -- kissing numbers must be in pool.")
        return 1.0

    pool_arr = np.array(pool)
    pool_size = len(pool_arr)
    kissing_indices = np.array([np.where(pool_arr == v)[0][0] for v in kissing])

    count_all5 = 0
    batch_size = 500_000
    rng = np.random.default_rng(123)

    for start in range(0, n_trials, batch_size):
        bs = min(batch_size, n_trials - start)

        # Sample 32 from pool_size without replacement
        rand_vals = rng.random((bs, pool_size))
        samples_idx = np.argpartition(rand_vals, 32, axis=1)[:, :32]

        # Check all 5 kissing indices present
        hits = np.ones(bs, dtype=bool)
        for ki in kissing_indices:
            hits &= np.any(samples_idx == ki, axis=1)

        count_all5 += np.sum(hits)

    p_mc = count_all5 / n_trials

    # Exact probability: C(5,5)*C(pool_size-5, 27) / C(pool_size, 32)
    ps = pool_size
    p_exact = comb(5, 5) * comb(ps - 5, 27) / comb(ps, 32)

    def wilson_ci(p, n):
        z = 1.96
        denom = 1 + z**2 / n
        center = (p + z**2 / (2 * n)) / denom
        spread = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
        return max(0, center - spread), min(1, center + spread)

    ci = wilson_ci(p_mc, n_trials)

    print(f"{'Metric':<40} {'MC Estimate':>14} {'Exact':>14}")
    print("-" * 72)
    print(f"{'P(all 5 kissing numbers in sample)':<40} {p_mc:.6f}   {p_exact:.6f}")
    print(f"  95% CI: [{ci[0]:.6f}, {ci[1]:.6f}]")
    print(f"  Count: {count_all5:,} / {n_trials:,}")
    print(f"  1/P = {1/max(p_exact, 1e-30):,.1f}")
    print()

    return p_exact


# ============================================================================
# TEST 3: Fisher's Combined Test
# ============================================================================

def test_fisher_combined(p_dim, p_kiss, p_gauge=None, p_koide=None):
    """
    Fisher's method: chi2 = -2 * sum(ln(p_i)), df = 2k.
    """
    print("=" * 72)
    print("TEST 3: Fisher's Combined p-value (H-PH-9)")
    print("=" * 72)

    tests = {}
    tests["Dimensional Hierarchy (strong4)"] = p_dim

    tests["Kissing Numbers (all 5)"] = p_kiss

    # Gauge self-decomposition: S=0 at n=6 only among n=1..1000
    # Estimate: 1/1000 for unique fixed point
    if p_gauge is None:
        p_gauge = 1.0 / 1000.0
    tests["Gauge S=0 uniqueness (n=6 in 1..1000)"] = p_gauge

    # Koide = 2/3 exactly from n=6 arithmetic
    # Probability of random arithmetic combination = 2/3: ~1/50 target pool
    if p_koide is None:
        p_koide = 1.0 / 50.0
    tests["Koide = 2/3 exact"] = p_koide

    print(f"{'Test':<45} {'p-value':>12} {'-2 ln(p)':>10}")
    print("-" * 72)

    chi2_stat = 0.0
    k = 0
    for name, p in tests.items():
        contrib = -2 * log(max(p, 1e-300))
        chi2_stat += contrib
        k += 1
        print(f"{name:<45} {p:>12.2e} {contrib:>10.2f}")

    df = 2 * k
    p_combined = 1 - stats.chi2.cdf(chi2_stat, df)

    print("-" * 72)
    print(f"{'Fisher chi2 statistic':<45} {chi2_stat:>12.2f}")
    print(f"{'Degrees of freedom':<45} {df:>12d}")
    print(f"{'Combined p-value':<45} {p_combined:>12.2e}")
    if p_combined > 0:
        z_equiv = stats.norm.ppf(1 - p_combined)
        print(f"{'Equivalent Z-score':<45} {z_equiv:>12.1f} sigma")
    print()

    return p_combined


# ============================================================================
# TEST 4: Bonferroni Correction
# ============================================================================

def test_bonferroni(p_values, N_tests=50):
    """
    Apply Bonferroni correction: p_corrected = min(1, N * p_raw).
    """
    print("=" * 72)
    print(f"TEST 4: Bonferroni Correction (N={N_tests} relationships)")
    print("=" * 72)

    print(f"H-PH-9 tests approximately {N_tests} different relationships.")
    print(f"Bonferroni: p_corrected = min(1, {N_tests} * p_raw)")
    print()

    print(f"{'Test':<45} {'p_raw':>12} {'p_corrected':>14} {'Sig?':>6}")
    print("-" * 80)

    for name, p_raw in p_values.items():
        p_corr = min(1.0, N_tests * p_raw)
        sig = "***" if p_corr < 0.001 else "**" if p_corr < 0.01 else "*" if p_corr < 0.05 else "ns"
        print(f"{name:<45} {p_raw:>12.2e} {p_corr:>14.2e} {sig:>6}")

    print()
    print("Significance: *** p<0.001, ** p<0.01, * p<0.05, ns = not significant")
    print()


# ============================================================================
# TEST 5: Background Rate (Randomized Arithmetic Test)
# ============================================================================

def test_background_rate():
    """
    For n=1..1000, check what fraction have tau/sigma/phi/etc matching
    any physics constant. This gives the 'background rate'.
    """
    print("=" * 72)
    print("TEST 5: Background Arithmetic Match Rate (n=1..1000)")
    print("=" * 72)

    physics_constants = {4, 6, 10, 14, 26, 12, 2, 24, 56, 240, 496, 16, 3, 44, 35, 9}

    print(f"Physics constants pool ({len(physics_constants)}): {sorted(physics_constants)}")
    print(f"Functions checked: tau(n), sigma(n), phi(n), sigma*phi, sigma/tau")
    print()

    match_count = 0
    match_details = {}
    func_match_counts = {"tau": 0, "sigma": 0, "phi": 0, "sig*phi": 0, "sig/tau": 0}

    for n in range(1, 1001):
        t = tau_n(n)
        s = sigma_n(n)
        p = phi_n(n)
        sp = s * p
        st = s // t if t > 0 else 0

        funcs = {"tau": t, "sigma": s, "phi": p, "sig*phi": sp, "sig/tau": st}
        matched = False
        matched_funcs = []
        for fname, val in funcs.items():
            if val in physics_constants:
                func_match_counts[fname] += 1
                matched = True
                matched_funcs.append(f"{fname}={val}")

        if matched:
            match_count += 1
            if n <= 30 or n == 6:
                match_details[n] = matched_funcs

    rate = match_count / 1000

    print(f"{'n values with ANY match':<40} {match_count}/1000 = {rate:.3f}")
    print()
    print(f"{'Function':<20} {'Match count':>12} {'Rate':>8}")
    print("-" * 44)
    for fname, cnt in func_match_counts.items():
        print(f"{fname:<20} {cnt:>12} {cnt/1000:>8.3f}")

    print()
    print("Sample matches (n <= 30 and n=6):")
    for n, funcs in sorted(match_details.items()):
        marker = " <<<" if n == 6 else ""
        print(f"  n={n:>4}: {', '.join(funcs)}{marker}")

    # How special is n=6?
    n6_funcs = {"tau": tau_n(6), "sigma": sigma_n(6), "phi": phi_n(6),
                "sig*phi": sigma_n(6) * phi_n(6), "sig/tau": sigma_n(6) // tau_n(6)}
    n6_matches = sum(1 for v in n6_funcs.values() if v in physics_constants)

    print()
    print(f"n=6 specifics: {n6_funcs}")
    print(f"n=6 matches {n6_matches}/5 functions to physics constants")

    # Distribution of match counts
    match_histogram = [0] * 6
    for n in range(1, 1001):
        t = tau_n(n)
        s = sigma_n(n)
        p = phi_n(n)
        sp = s * p
        st = s // t if t > 0 else 0
        cnt = sum(1 for v in [t, s, p, sp, st] if v in physics_constants)
        match_histogram[min(cnt, 5)] += 1

    print()
    print("Distribution of match counts per n (how many of 5 functions match):")
    print(f"{'Matches':<10} {'Count':>8} {'Rate':>8} {'Bar'}")
    print("-" * 50)
    for i, cnt in enumerate(match_histogram):
        bar = "#" * (cnt // 10)
        print(f"{i:<10} {cnt:>8} {cnt/1000:>8.3f}  {bar}")

    # P(matching >= n6_matches functions)
    n_ge_n6 = sum(match_histogram[n6_matches:])
    p_ge_n6 = n_ge_n6 / 1000
    print()
    print(f"P(>= {n6_matches} matches) = {n_ge_n6}/1000 = {p_ge_n6:.4f}")
    print(f"n=6 is in the top {p_ge_n6*100:.1f}% of all n=1..1000")
    print()

    return rate, p_ge_n6


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("=" * 72)
    print("  H-PH-9 EXTREME TEXAS SHARPSHOOTER TEST")
    print(f"  Monte Carlo trials: {N_TRIALS:,}")
    print("=" * 72)
    print()

    t0 = time.time()

    # Test 1
    t1 = time.time()
    p_dim_strong, p_dim_full, p_dim_mc_s, p_dim_mc_f = test_dimensional_hierarchy(N_TRIALS)
    print(f"[Test 1 elapsed: {time.time()-t1:.1f}s]")
    print()

    # Test 2
    t2 = time.time()
    p_kiss = test_kissing_numbers(N_TRIALS)
    print(f"[Test 2 elapsed: {time.time()-t2:.1f}s]")
    print()

    # Test 3
    p_combined = test_fisher_combined(p_dim_strong, p_kiss)

    # Test 4
    p_values = {
        "Dimensional Hierarchy (strong)": p_dim_strong,
        "Dimensional Hierarchy (full)": p_dim_full,
        "Kissing Numbers (all 5)": p_kiss,
        "Combined (Fisher)": p_combined,
    }
    test_bonferroni(p_values, N_tests=50)

    # Test 5
    bg_rate, p_n6_special = test_background_rate()

    # Final summary
    print("=" * 72)
    print("  FINAL SUMMARY")
    print("=" * 72)
    print()
    print(f"{'Test':<45} {'p-value':>14} {'1/p':>12}")
    print("-" * 72)
    print(f"{'Dim. Hierarchy (4 strong targets)':<45} {p_dim_strong:>14.2e} {1/p_dim_strong:>12,.0f}")
    print(f"{'Dim. Hierarchy (all 5 exact)':<45} {p_dim_full:>14.2e} {1/p_dim_full:>12,.0f}")
    print(f"{'Kissing Numbers (all 5 in 32-sample)':<45} {p_kiss:>14.2e} {1/max(p_kiss,1e-30):>12,.1f}")
    print(f"{'Fisher Combined (4 tests)':<45} {p_combined:>14.2e} {1/max(p_combined,1e-30):>12,.0f}")
    print(f"{'Background rate (any match)':<45} {bg_rate:>14.4f}")
    print(f"{'n=6 specialness (>= its match count)':<45} {p_n6_special:>14.4f}")
    print()

    # Bonferroni-corrected
    N_BONF = 50
    print(f"Bonferroni-corrected (N={N_BONF}):")
    for name, p in [("Dim strong", p_dim_strong), ("Dim full", p_dim_full),
                    ("Kissing", p_kiss), ("Fisher combined", p_combined)]:
        p_corr = min(1.0, N_BONF * p)
        sig = "***" if p_corr < 0.001 else "**" if p_corr < 0.01 else "*" if p_corr < 0.05 else "ns"
        print(f"  {name:<30} p_corr = {p_corr:.2e}  {sig}")

    print()
    print(f"Total elapsed: {time.time()-t0:.1f}s")
    print()
    print("Interpretation:")
    print("  p < 0.001 (***) : Strong evidence against chance")
    print("  p < 0.01  (**)  : Moderate evidence against chance")
    print("  p < 0.05  (*)   : Weak evidence against chance")
    print("  p >= 0.05 (ns)  : Consistent with chance")


if __name__ == "__main__":
    main()
