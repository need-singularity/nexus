#!/usr/bin/env python3
"""
EXTREME EXPERIMENT: Quantitative verification of music consonance claims.

Tests:
1. Euler Gradus Suavitatis for all ratios a:b with a,b <= 30
2. N-TET optimization sweep N=1..100
3. Circle of fifths closure test
4. Plomp-Levelt computational dissonance
5. Statistical test: n=6 divisor dominance in consonance

Golden Zone dependency: NONE (pure acoustics / number theory)
"""

import math
import random
from fractions import Fraction
from collections import Counter

# ============================================================
# UTILITIES
# ============================================================

def prime_factorization(n):
    """Return dict {prime: exponent}."""
    if n <= 1:
        return {}
    factors = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors


def euler_gradus(a, b):
    """Euler Gradus Suavitatis for ratio a:b.
    GS(a/b) = 1 + sum(e_i * (p_i - 1)) for the reduced fraction.
    """
    f = Fraction(a, b)
    num, den = f.numerator, f.denominator
    # factorize lcm(num, den)
    lcm_val = (num * den) // math.gcd(num, den)
    factors = prime_factorization(lcm_val)
    if not factors:
        return 1
    return 1 + sum(e * (p - 1) for p, e in factors.items())


def primes_used(a, b):
    """Set of primes used in reduced ratio a:b."""
    f = Fraction(a, b)
    num, den = f.numerator, f.denominator
    lcm_val = (num * den) // math.gcd(num, den)
    return set(prime_factorization(lcm_val).keys())


# ============================================================
# TEST 1: Euler Gradus Suavitatis for all ratios a:b, a,b <= 30
# ============================================================

def test_euler_gradus():
    print("=" * 70)
    print("TEST 1: Euler Gradus Suavitatis for all ratios a:b (a,b <= 30)")
    print("=" * 70)

    # Collect unique reduced ratios
    seen = set()
    ratios = []
    for a in range(1, 31):
        for b in range(a, 31):
            f = Fraction(a, b)
            if f == 1:
                continue
            key = (f.numerator, f.denominator)
            if key not in seen:
                seen.add(key)
                gs = euler_gradus(a, b)
                ps = primes_used(a, b)
                ratios.append((gs, a, b, f, ps))

    ratios.sort()

    # Top 20 by consonance (lowest GS)
    print(f"\nTotal unique ratios: {len(ratios)}")
    print(f"\n{'Rank':<6}{'Ratio':<10}{'Fraction':<12}{'GS':<6}{'Primes Used'}")
    print("-" * 50)
    for i, (gs, a, b, f, ps) in enumerate(ratios[:20]):
        print(f"{i+1:<6}{a}:{b:<7}{str(f):<12}{gs:<6}{sorted(ps)}")

    # Verify: top 4 by consonance use ONLY primes {2,3}
    top4 = ratios[:4]
    top4_primes = [ps for gs, a, b, f, ps in top4]
    all_23 = all(ps <= {2, 3} for ps in top4_primes)
    print(f"\nTop 4 most consonant intervals:")
    for i, (gs, a, b, f, ps) in enumerate(top4):
        print(f"  {i+1}. {a}:{b} (GS={gs}, primes={sorted(ps)})")
    print(f"All top 4 use ONLY primes {{2,3}}: {all_23}")

    # Count: fraction of GS <= 5 that use only {2,3}
    gs_le5 = [(gs, a, b, f, ps) for gs, a, b, f, ps in ratios if gs <= 5]
    gs_le5_23 = [r for r in gs_le5 if r[4] <= {2, 3}]
    gs_le5_p5 = [r for r in gs_le5 if all(p <= 5 for p in r[4])]
    print(f"\nIntervals with GS <= 5: {len(gs_le5)}")
    print(f"  Using only primes {{2,3}}: {len(gs_le5_23)} ({len(gs_le5_23)/len(gs_le5)*100:.1f}%)")
    print(f"  Using only primes <= 5:  {len(gs_le5_p5)} ({len(gs_le5_p5)/len(gs_le5)*100:.1f}%)")

    print(f"\nAll GS <= 5 intervals:")
    for gs, a, b, f, ps in gs_le5:
        print(f"  {str(f):<10} GS={gs}  primes={sorted(ps)}")

    return ratios


# ============================================================
# TEST 2: N-TET optimization sweep N=1..100
# ============================================================

def test_ntet_sweep():
    print("\n" + "=" * 70)
    print("TEST 2: N-TET Optimization Sweep (N=1 to 100)")
    print("=" * 70)

    # Target intervals in cents
    targets = {
        "P5 (3:2)": 1200 * math.log2(3/2),   # 701.955
        "P4 (4:3)": 1200 * math.log2(4/3),   # 498.045
        "M3 (5:4)": 1200 * math.log2(5/4),   # 386.314
        "m3 (6:5)": 1200 * math.log2(6/5),   # 315.641
    }

    print(f"\nTarget intervals (just intonation):")
    for name, cents in targets.items():
        print(f"  {name}: {cents:.3f} cents")

    # Perfect consonances = P5, P4 only
    perfect_targets = {k: v for k, v in targets.items() if k.startswith("P")}
    all_targets = targets

    results = []
    for n in range(1, 101):
        step = 1200 / n
        # For each target, find closest step multiple
        err_perfect = 0
        err_all = 0
        errors = {}
        for name, target_cents in all_targets.items():
            closest = round(target_cents / step) * step
            err = (target_cents - closest) ** 2
            errors[name] = abs(target_cents - closest)
            err_all += err
            if name in perfect_targets:
                err_perfect += err
        results.append((n, err_perfect, err_all, errors))

    # Sort by perfect consonance score
    by_perfect = sorted(results, key=lambda x: x[1])
    # Sort by all 4 intervals score
    by_all = sorted(results, key=lambda x: x[2])

    print(f"\n--- Top 15 N-TET by PERFECT consonance error (P5+P4) ---")
    print(f"{'Rank':<6}{'N':<6}{'SSE(P5+P4)':<14}{'P5 err':<10}{'P4 err':<10}{'M3 err':<10}{'m3 err':<10}")
    print("-" * 66)
    for i, (n, ep, ea, errs) in enumerate(by_perfect[:15]):
        print(f"{i+1:<6}{n:<6}{ep:<14.3f}{errs['P5 (3:2)']:<10.3f}{errs['P4 (4:3)']:<10.3f}"
              f"{errs['M3 (5:4)']:<10.3f}{errs['m3 (6:5)']:<10.3f}")

    # Check: is N=12 optimal for N<=20?
    best_le20_perfect = min((r for r in results if r[0] <= 20), key=lambda x: x[1])
    print(f"\nBest N<=20 for perfect consonances: N={best_le20_perfect[0]} (SSE={best_le20_perfect[1]:.3f})")
    n12 = [r for r in results if r[0] == 12][0]
    print(f"N=12 perfect consonance SSE: {n12[1]:.3f}")
    print(f"N=12 is optimal for N<=20: {best_le20_perfect[0] == 12}")

    print(f"\n--- Top 15 N-TET by ALL 4 intervals error ---")
    print(f"{'Rank':<6}{'N':<6}{'SSE(all4)':<14}{'P5 err':<10}{'P4 err':<10}{'M3 err':<10}{'m3 err':<10}")
    print("-" * 66)
    for i, (n, ep, ea, errs) in enumerate(by_all[:15]):
        print(f"{i+1:<6}{n:<6}{ea:<14.3f}{errs['P5 (3:2)']:<10.3f}{errs['P4 (4:3)']:<10.3f}"
              f"{errs['M3 (5:4)']:<10.3f}{errs['m3 (6:5)']:<10.3f}")

    best_all = by_all[0]
    print(f"\nGlobally optimal for all 4 intervals: N={best_all[0]} (SSE={best_all[2]:.3f})")

    # Where does N=12 rank?
    rank_12_perfect = next(i+1 for i, (n, _, _, _) in enumerate(by_perfect) if n == 12)
    rank_12_all = next(i+1 for i, (n, _, _, _) in enumerate(by_all) if n == 12)
    print(f"N=12 rank in perfect consonances: #{rank_12_perfect} out of 100")
    print(f"N=12 rank in all 4 intervals: #{rank_12_all} out of 100")


# ============================================================
# TEST 3: Circle of fifths closure test
# ============================================================

def test_circle_of_fifths():
    print("\n" + "=" * 70)
    print("TEST 3: Circle of Fifths Closure Test")
    print("=" * 70)

    log2_ratio = math.log2(3/2)  # ~0.58496

    print(f"\nlog2(3/2) = {log2_ratio:.10f}")
    print(f"\nSearching for N where (3/2)^N is closest to a power of 2...")
    print(f"{'N':<6}{'M':<6}{'(3/2)^N / 2^M':<18}{'|error| cents':<16}{'error (log2)'}")
    print("-" * 60)

    results = []
    for n in range(1, 101):
        val = n * log2_ratio
        m = round(val)
        error_log2 = abs(val - m)
        error_cents = error_log2 * 1200
        results.append((n, m, error_log2, error_cents))

    results_sorted = sorted(results, key=lambda x: x[2])

    for n, m, err_log2, err_cents in results_sorted[:20]:
        ratio = (3/2)**n / 2**m
        print(f"{n:<6}{m:<6}{ratio:<18.10f}{err_cents:<16.6f}{err_log2:.10f}")

    # Verify N=12 is best for N<=53
    best_le53 = min((r for r in results if r[0] <= 53), key=lambda x: x[2])
    print(f"\nBest closure for N<=53: N={best_le53[0]} (error={best_le53[3]:.6f} cents)")
    n12_result = results[11]  # N=12 is index 11
    print(f"N=12 closure error: {n12_result[3]:.6f} cents")
    print(f"N=12 is best for N<=53: {best_le53[0] == 12}")

    # Pythagorean comma
    comma = Fraction(3, 2)**12 / Fraction(2, 1)**7
    comma_float = (3/2)**12 / 2**7
    comma_cents = 1200 * math.log2(comma_float)
    print(f"\nPythagorean comma:")
    print(f"  (3/2)^12 / 2^7 = 3^12 / 2^19")
    print(f"  = {3**12} / {2**19}")
    print(f"  = {comma} = {float(comma):.10f}")
    print(f"  = {comma_cents:.6f} cents")
    print(f"  (should be ~23.46 cents)")


# ============================================================
# TEST 4: Plomp-Levelt dissonance curve
# ============================================================

def plomp_levelt_dissonance(f1, f2):
    """Compute Plomp-Levelt dissonance between two pure tones.
    Based on Sethares' parameterization of Plomp & Levelt (1965).
    """
    if f1 > f2:
        f1, f2 = f2, f1
    if f1 == 0:
        return 0

    s = 0.24 / (0.021 * f1 + 19)  # critical bandwidth scaling
    x = s * (f2 - f1)

    # Plomp-Levelt curve: d(x) = e^(-3.5x) - e^(-5.75x)
    if x < 0:
        return 0
    d = math.exp(-3.5 * x) - math.exp(-5.75 * x)
    return max(0, d)


def test_plomp_levelt():
    print("\n" + "=" * 70)
    print("TEST 4: Plomp-Levelt Computational Dissonance")
    print("=" * 70)

    base_freq = 260.0  # ~middle C

    # All ratios a:b with a,b <= 12, a < b
    ratios = []
    seen = set()
    for a in range(1, 13):
        for b in range(a + 1, 13):
            f = Fraction(a, b)
            key = (f.numerator, f.denominator)
            if key not in seen:
                seen.add(key)
                f1 = base_freq
                f2 = base_freq * b / a
                diss = plomp_levelt_dissonance(f1, f2)
                gs = euler_gradus(a, b)
                ratios.append((diss, a, b, f, gs))

    ratios.sort()

    print(f"\nAll {len(ratios)} unique ratios ranked by Plomp-Levelt dissonance (low = consonant):")
    print(f"{'PL Rank':<9}{'Ratio':<10}{'Dissonance':<14}{'GS':<6}{'GS Rank'}")
    print("-" * 45)

    # Compute GS rank
    gs_sorted = sorted(ratios, key=lambda x: x[4])
    gs_rank = {}
    for i, (d, a, b, f, gs) in enumerate(gs_sorted):
        gs_rank[(a, b)] = i + 1

    for i, (d, a, b, f, gs) in enumerate(ratios):
        print(f"{i+1:<9}{a}:{b:<7}{d:<14.6f}{gs:<6}{gs_rank[(a,b)]}")

    # Rank correlation (Spearman)
    pl_ranks = {(r[1], r[2]): i+1 for i, r in enumerate(ratios)}
    n = len(ratios)
    d_sum = sum((pl_ranks[k] - gs_rank[k])**2 for k in pl_ranks)
    spearman = 1 - 6 * d_sum / (n * (n**2 - 1))
    print(f"\nSpearman rank correlation (PL vs Euler GS): {spearman:.4f}")
    print(f"(1.0 = perfect agreement, 0 = no correlation)")

    # Top 5 agreement
    pl_top5 = set((r[1], r[2]) for r in ratios[:5])
    gs_top5 = set((r[1], r[2]) for r in gs_sorted[:5])
    overlap = pl_top5 & gs_top5
    print(f"\nTop 5 overlap (PL vs GS): {len(overlap)}/5")
    print(f"  PL top 5: {sorted(pl_top5)}")
    print(f"  GS top 5: {sorted(gs_top5)}")


# ============================================================
# TEST 5: Statistical test — n=6 divisor dominance
# ============================================================

def test_statistical_divisor_dominance():
    print("\n" + "=" * 70)
    print("TEST 5: Statistical Test — n=6 Divisor Dominance in Consonance")
    print("=" * 70)

    # Pool: all simple ratios a:b with 1 <= a < b <= 12
    pool = []
    seen = set()
    for a in range(1, 13):
        for b in range(a + 1, 13):
            f = Fraction(a, b)
            key = (f.numerator, f.denominator)
            if key not in seen:
                seen.add(key)
                gs = euler_gradus(a, b)
                pool.append((gs, a, b, f))

    pool.sort()
    print(f"\nPool: {len(pool)} unique reduced ratios with 1 <= a < b <= 12")

    # Top 4 by consonance
    top4 = pool[:4]
    print(f"\nTop 4 most consonant (lowest GS):")
    for i, (gs, a, b, f) in enumerate(top4):
        divides_6 = (6 % a == 0) and (6 % b == 0)
        print(f"  {i+1}. {a}:{b} (GS={gs}) — both divide 6: {divides_6}")

    # "Match": both a and b divide 6
    divs6 = {1, 2, 3, 6}
    matches_in_top4 = sum(1 for gs, a, b, f in top4
                          if f.numerator in divs6 and f.denominator in divs6)
    print(f"\nMatches (both values divide 6) in top 4: {matches_in_top4}/4")

    # Divisors of n for all n in [2, 100]
    def divisors(n):
        return {d for d in range(1, n+1) if n % d == 0}

    # Monte Carlo: for each n in [2, 100], count how many top-4 ratios
    # have both numerator and denominator dividing n
    print(f"\n--- Sweep n=2..100: top-4 divisor matches ---")
    print(f"{'n':<6}{'divisors':<30}{'top4 matches':<14}{'top4 fraction'}")
    print("-" * 60)

    sweep_results = []
    for n in range(2, 101):
        divs = divisors(n)
        matches = sum(1 for gs, a, b, f in top4
                      if f.numerator in divs and f.denominator in divs)
        sweep_results.append((n, matches, divs))

    # Show those with matches >= 3
    for n, matches, divs in sweep_results:
        if matches >= 3 or n <= 12 or n in [6, 12, 24, 28, 30, 60]:
            print(f"{n:<6}{str(sorted(divs)):<30}{matches:<14}{matches}/4")

    max_matches = max(m for _, m, _ in sweep_results)
    best_n = [n for n, m, _ in sweep_results if m == max_matches]
    print(f"\nMaximum top-4 matches: {max_matches}/4, achieved by n={best_n}")

    # Monte Carlo: random n
    random.seed(42)
    n_trials = 100000
    count_dominate = Counter()  # matches -> count

    for _ in range(n_trials):
        n = random.randint(2, 100)
        divs = divisors(n)
        matches = sum(1 for gs, a, b, f in top4
                      if f.numerator in divs and f.denominator in divs)
        count_dominate[matches] += 1

    print(f"\nMonte Carlo ({n_trials} trials, random n in [2,100]):")
    print(f"  Distribution of top-4 matches:")
    for k in sorted(count_dominate.keys()):
        pct = count_dominate[k] / n_trials * 100
        bar = "#" * int(pct / 2)
        print(f"    {k} matches: {count_dominate[k]:>6} ({pct:.1f}%) {bar}")

    # p-value for n=6 (matches_in_top4)
    count_ge = sum(v for k, v in count_dominate.items() if k >= matches_in_top4)
    p_value = count_ge / n_trials
    print(f"\n  n=6 achieves {matches_in_top4}/4 matches")
    print(f"  P(matches >= {matches_in_top4} | random n) = {p_value:.4f}")
    print(f"  p-value = {p_value:.4f}")

    # Also test: what fraction of n in [2,100] achieve >= matches_in_top4?
    count_exact = sum(1 for n, m, _ in sweep_results if m >= matches_in_top4)
    print(f"\n  Exact count: {count_exact}/99 values of n in [2,100] achieve >= {matches_in_top4} matches")
    print(f"  Exact fraction: {count_exact/99:.4f}")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("EXTREME EXPERIMENT: Music Consonance Quantitative Verification")
    print("=" * 70)

    ratios = test_euler_gradus()
    test_ntet_sweep()
    test_circle_of_fifths()
    test_plomp_levelt()
    test_statistical_divisor_dominance()

    print("\n" + "=" * 70)
    print("ALL TESTS COMPLETE")
    print("=" * 70)
