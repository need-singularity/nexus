#!/usr/bin/env python3
"""Control Group Texas Sharpshooter — Non-perfect number validation

Tests whether n=6's special arithmetic identities are genuinely unique
to perfect numbers, or merely small-number effects.

Control group: n in {5, 7, 8, 9, 10, 12, 14, 15, 18, 20}
Perfect group: n in {6, 28, 496}

For each n, checks a battery of 20 arithmetic identities and counts
how many are satisfied. If non-perfect numbers score comparably to
perfect numbers, then n=6's results are likely coincidence.

Statistical analysis:
  - Z-score of perfect vs control group
  - Permutation test p-value (10,000 trials)
  - Bonferroni-corrected individual test p-values

Usage:
  python3 calc/control_group_texas.py                  # Full analysis
  python3 calc/control_group_texas.py --extended        # Extended control to n=100
  python3 calc/control_group_texas.py --monte-carlo 50000  # More MC trials
"""

import argparse
import math
import random
import sys
from fractions import Fraction
from collections import defaultdict


# =====================================================================
# Arithmetic functions (from perfect_number_classifier.py)
# =====================================================================

def factorize(n):
    factors = {}
    d = 2
    tmp = n
    while d * d <= tmp:
        while tmp % d == 0:
            factors[d] = factors.get(d, 0) + 1
            tmp //= d
        d += 1
    if tmp > 1:
        factors[tmp] = factors.get(tmp, 0) + 1
    return factors


def sigma(n):
    factors = factorize(n)
    result = 1
    for p, e in factors.items():
        result *= (p**(e+1) - 1) // (p - 1)
    return result


def tau(n):
    factors = factorize(n)
    result = 1
    for e in factors.values():
        result *= (e + 1)
    return result


def phi(n):
    factors = factorize(n)
    result = n
    for p in factors:
        result = result * (p - 1) // p
    return result


def omega(n):
    return len(factorize(n))


def bigomega(n):
    return sum(factorize(n).values())


def sopfr(n):
    return sum(p * e for p, e in factorize(n).items())


def rad(n):
    result = 1
    for p in factorize(n):
        result *= p
    return result


def mobius(n):
    factors = factorize(n)
    for e in factors.values():
        if e > 1:
            return 0
    return (-1) ** len(factors)


def divisors(n):
    divs = []
    for i in range(1, int(n**0.5) + 1):
        if n % i == 0:
            divs.append(i)
            if i != n // i:
                divs.append(n // i)
    return sorted(divs)


def is_perfect(n):
    return sigma(n) == 2 * n


def proper_divisors(n):
    return [d for d in divisors(n) if d < n]


def harmonic_reciprocal_sum(n):
    """Sum of reciprocals of proper divisors: sum(1/d for d in proper_divisors)."""
    return sum(Fraction(1, d) for d in proper_divisors(n))


def lyapunov_product(n):
    """Product of R(d|n) = (d mod n) / n for proper divisors.
    For perfect numbers, product of d/n for proper divisors d.
    Lyapunov = ln(product). If product=1, Lyapunov=0 (edge of chaos)."""
    pd = proper_divisors(n)
    if not pd:
        return 0.0
    product = 1.0
    for d in pd:
        product *= d / n
    return product


# =====================================================================
# Identity checks — each returns (passes: bool, description: str, detail: str)
# =====================================================================

def check_identities(n):
    """Run all identity checks for integer n. Returns list of (name, passed, detail)."""
    s = sigma(n)
    p = phi(n)
    t = tau(n)
    sp = sopfr(n)
    w = omega(n)
    W = bigomega(n)
    mu = mobius(n)
    r = rad(n)
    pd = proper_divisors(n)
    ds = divisors(n)
    hrs = harmonic_reciprocal_sum(n)
    lp = lyapunov_product(n)

    results = []

    # 1. sigma(n) = 2n (perfect number definition)
    results.append(("sigma=2n", s == 2 * n,
                    f"sigma={s}, 2n={2*n}"))

    # 2. sigma*phi = n*tau (Bridge equation)
    results.append(("sigma*phi=n*tau", s * p == n * t,
                    f"s*p={s*p}, n*t={n*t}"))

    # 3. sigma/phi = n (self-referential fixed point)
    results.append(("sigma/phi=n", p != 0 and Fraction(s, p) == n,
                    f"sigma/phi={Fraction(s,p) if p else 'undef'}, n={n}"))

    # 4. Harmonic reciprocal sum = 1
    results.append(("sum(1/d)=1", hrs == 1,
                    f"sum(1/d)={float(hrs):.6f}"))

    # 5. Bridge ratio sigma*phi/(n*tau) = 1
    bridge = Fraction(s * p, n * t) if n * t != 0 else Fraction(0)
    results.append(("Bridge=1", bridge == 1,
                    f"Bridge={float(bridge):.6f}"))

    # 6. Lyapunov = 0 (product of d/n = 1)
    results.append(("Lyapunov=0", abs(lp - 1.0) < 1e-12,
                    f"product={lp:.6e}"))

    # 7. phi/n = 1/3
    results.append(("phi/n=1/3", Fraction(p, n) == Fraction(1, 3),
                    f"phi/n={float(Fraction(p,n)):.6f}"))

    # 8. sigma/n = 2 (abundancy = 2, equivalent to perfect)
    results.append(("sigma/n=2", Fraction(s, n) == 2,
                    f"sigma/n={float(Fraction(s,n)):.6f}"))

    # 9. tau divides sigma
    results.append(("tau|sigma", t != 0 and s % t == 0,
                    f"sigma={s}, tau={t}, sigma%tau={s%t if t else 'undef'}"))

    # 10. n = tau * phi (factorial capacity variant)
    results.append(("n=tau*phi", n == t * p,
                    f"tau*phi={t*p}"))

    # 11. sigma/phi = 6 (maximum among perfects, unique to n=6)
    results.append(("sigma/phi=6", p != 0 and Fraction(s, p) == 6,
                    f"sigma/phi={float(Fraction(s,p)) if p else 'undef':.4f}"))

    # 12. (n+1)/(tau*phi) = 7/8 (rate small-N)
    if t * p != 0:
        rate = Fraction(n + 1, t * p)
        results.append(("rate=7/8", rate == Fraction(7, 8),
                        f"(n+1)/(tau*phi)={float(rate):.6f}"))
    else:
        results.append(("rate=7/8", False, "undef"))

    # 13. phi/sopfr = 2/5 (rate large-N)
    if sp != 0:
        rate_inf = Fraction(p, sp)
        results.append(("phi/sopfr=2/5", rate_inf == Fraction(2, 5),
                        f"phi/sopfr={float(rate_inf):.6f}"))
    else:
        results.append(("phi/sopfr=2/5", False, "undef"))

    # 14. sopfr * phi = n + tau (unique to n=6)
    results.append(("sopfr*phi=n+tau", sp * p == n + t,
                    f"sopfr*phi={sp*p}, n+tau={n+t}"))

    # 15. n * sigma * sopfr * phi = n! (factorial capacity, 720 for n=6)
    factorial_cap = n * s * sp * p
    try:
        nfact = math.factorial(n)
        results.append(("n*s*sopfr*phi=n!", factorial_cap == nfact,
                        f"product={factorial_cap}, n!={nfact}"))
    except (ValueError, OverflowError):
        results.append(("n*s*sopfr*phi=n!", False, "overflow"))

    # 16. omega = 2 (exactly 2 distinct prime factors)
    results.append(("omega=2", w == 2,
                    f"omega={w}"))

    # 17. (n-3)! = n (unique: only n=6 satisfies this)
    if n >= 3:
        results.append(("(n-3)!=n", math.factorial(n - 3) == n,
                        f"(n-3)!={math.factorial(n-3)}"))
    else:
        results.append(("(n-3)!=n", False, "n<3"))

    # 18. tau*(tau-1) = sigma (unique to n=6)
    results.append(("tau*(tau-1)=sigma", t * (t - 1) == s,
                    f"tau*(tau-1)={t*(t-1)}, sigma={s}"))

    # 19. tau * sopfr = 20 (unique to n=6)
    results.append(("tau*sopfr=20", t * sp == 20,
                    f"tau*sopfr={t*sp}"))

    # 20. 1/2 + 1/3 + 1/6 = 1 (proper divisor reciprocals sum to 1, different from #4)
    # More precisely: the proper divisors ARE {1,2,3} and 1/1+1/2+1/3=11/6 != 1
    # Actually, for n=6, proper divisors = {1,2,3}, reciprocals = 1+1/2+1/3 = 11/6
    # The DEFINING property is sigma_{-1}(n) = sum d/n for all d|n = sigma/n = 2
    # Let's check: sum(d for d|n) / n = sigma/n
    # Instead: check if divisor reciprocals (excluding n) sum to 1 => sigma(n)/n - 1 = 1
    # => sigma(n)/n = 2 => perfect. Same as #1. Use a different check:
    # Divisor parts: can n be written as sum of ALL its proper divisors exactly?
    results.append(("n=sum(proper_d)", n == sum(pd),
                    f"sum(proper_d)={sum(pd)}"))

    return results


# =====================================================================
# Main analysis
# =====================================================================

def run_analysis(control_nums, perfect_nums, mc_trials=10000, extended=False):
    """Run full control group analysis."""

    all_nums = control_nums + perfect_nums
    all_results = {}
    identity_names = None

    print("=" * 78)
    print("  CONTROL GROUP TEXAS SHARPSHOOTER TEST")
    print("  Non-perfect numbers vs Perfect numbers: Identity comparison")
    print("=" * 78)
    print()

    # ── Compute arithmetic functions for all numbers ──
    print("--- Arithmetic Functions Table ---")
    print()
    header = f"{'n':>4} | {'perf?':>5} | {'sigma':>6} | {'phi':>5} | {'tau':>4} | {'sopfr':>5} | {'omega':>5} | {'Omega':>5} | {'mu':>3} | {'rad':>5}"
    print(header)
    print("-" * len(header))

    for n in sorted(all_nums):
        pf = "YES" if is_perfect(n) else "no"
        s, p, t, sp, w, W, mu, r = sigma(n), phi(n), tau(n), sopfr(n), omega(n), bigomega(n), mobius(n), rad(n)
        print(f"{n:>4} | {pf:>5} | {s:>6} | {p:>5} | {t:>4} | {sp:>5} | {w:>5} | {W:>5} | {mu:>3} | {r:>5}")
        all_results[n] = check_identities(n)
        if identity_names is None:
            identity_names = [r[0] for r in all_results[n]]

    print()

    # ── Ratio table ──
    print("--- Key Ratios ---")
    print()
    header2 = f"{'n':>4} | {'s/n':>7} | {'p/n':>7} | {'s/p':>7} | {'sp*p/(nt)':>10} | {'(n+1)/tp':>10} | {'p/sopfr':>10}"
    print(header2)
    print("-" * len(header2))

    for n in sorted(all_nums):
        s, p, t, sp = sigma(n), phi(n), tau(n), sopfr(n)
        sn = f"{s/n:.4f}"
        pn = f"{p/n:.4f}"
        sp_ratio = f"{s/p:.4f}" if p else "undef"
        bridge = f"{s*p/(n*t):.4f}" if n*t else "undef"
        rate = f"{(n+1)/(t*p):.4f}" if t*p else "undef"
        rinf = f"{p/sp:.4f}" if sp else "undef"
        print(f"{n:>4} | {sn:>7} | {pn:>7} | {sp_ratio:>7} | {bridge:>10} | {rate:>10} | {rinf:>10}")

    print()

    # ── Identity check matrix ──
    print("--- Identity Check Matrix ---")
    print()

    # Header
    short_names = [name[:8] for name in identity_names]
    header3 = f"{'n':>4} |" + "|".join(f"{sn:^5}" for sn in short_names) + "| TOTAL"
    print(header3)
    print("-" * len(header3))

    scores = {}
    for n in sorted(all_nums):
        checks = all_results[n]
        passed = sum(1 for _, p, _ in checks if p)
        scores[n] = passed
        row = f"{n:>4} |"
        for _, p, _ in checks:
            row += f"{'  Y  ' if p else '  .  '}|"
        pf_mark = " ***" if is_perfect(n) else ""
        row += f" {passed:>3}{pf_mark}"
        print(row)

    print()
    print("Y = identity satisfied, . = not satisfied, *** = perfect number")
    print()

    # ── Per-identity analysis ──
    print("--- Per-Identity: Perfect vs Control ---")
    print()

    identity_perf_count = defaultdict(int)
    identity_ctrl_count = defaultdict(int)

    for n in perfect_nums:
        for name, passed, _ in all_results[n]:
            if passed:
                identity_perf_count[name] += 1

    for n in control_nums:
        for name, passed, _ in all_results[n]:
            if passed:
                identity_ctrl_count[name] += 1

    print(f"{'Identity':<20} | {'Perfect':>7} | {'Control':>7} | {'Unique?':>7}")
    print("-" * 55)
    n_perfect_unique = 0
    n_shared = 0
    for name in identity_names:
        pc = identity_perf_count[name]
        cc = identity_ctrl_count[name]
        unique = "UNIQUE" if pc > 0 and cc == 0 else ("shared" if pc > 0 and cc > 0 else "-")
        if pc > 0 and cc == 0:
            n_perfect_unique += 1
        if pc > 0 and cc > 0:
            n_shared += 1
        print(f"{name:<20} | {pc:>4}/{len(perfect_nums)} | {cc:>4}/{len(control_nums)} | {unique:>7}")

    print()
    print(f"Perfect-unique identities: {n_perfect_unique}")
    print(f"Shared identities:         {n_shared}")
    print()

    # ── Score summary ──
    print("--- Score Summary ---")
    print()

    perf_scores = [scores[n] for n in perfect_nums]
    ctrl_scores = [scores[n] for n in control_nums]

    perf_mean = sum(perf_scores) / len(perf_scores) if perf_scores else 0
    ctrl_mean = sum(ctrl_scores) / len(ctrl_scores) if ctrl_scores else 0
    ctrl_std = (sum((s - ctrl_mean)**2 for s in ctrl_scores) / len(ctrl_scores))**0.5 if ctrl_scores else 1

    print(f"Perfect numbers  mean score: {perf_mean:.2f}  (n=6: {scores.get(6,0)}, n=28: {scores.get(28,0)}, n=496: {scores.get(496,0)})")
    print(f"Control numbers  mean score: {ctrl_mean:.2f}  (std={ctrl_std:.2f})")
    print()

    if ctrl_std > 0:
        z_6 = (scores.get(6, 0) - ctrl_mean) / ctrl_std
        z_28 = (scores.get(28, 0) - ctrl_mean) / ctrl_std
        z_496 = (scores.get(496, 0) - ctrl_mean) / ctrl_std
    else:
        z_6 = float('inf') if scores.get(6, 0) > ctrl_mean else 0
        z_28 = float('inf') if scores.get(28, 0) > ctrl_mean else 0
        z_496 = float('inf') if scores.get(496, 0) > ctrl_mean else 0

    print(f"Z-score n=6  vs control: {z_6:.2f}")
    print(f"Z-score n=28 vs control: {z_28:.2f}")
    print(f"Z-score n=496 vs control: {z_496:.2f}")
    print()

    # ── Permutation test ──
    print(f"--- Permutation Test ({mc_trials:,} trials) ---")
    print()

    all_scores_list = perf_scores + ctrl_scores
    observed_diff = perf_mean - ctrl_mean
    n_perf = len(perf_scores)
    count_extreme = 0

    random.seed(42)
    for _ in range(mc_trials):
        random.shuffle(all_scores_list)
        perm_perf_mean = sum(all_scores_list[:n_perf]) / n_perf
        perm_ctrl_mean = sum(all_scores_list[n_perf:]) / len(ctrl_scores)
        if perm_perf_mean - perm_ctrl_mean >= observed_diff:
            count_extreme += 1

    p_value = count_extreme / mc_trials

    # Bonferroni correction: we tested 20 identities
    n_tests = len(identity_names)
    p_bonferroni = min(p_value * n_tests, 1.0)

    print(f"Observed difference (perfect - control): {observed_diff:.2f}")
    print(f"Permutation p-value (one-sided):         {p_value:.6f}")
    print(f"Bonferroni-corrected p (k={n_tests}):       {p_bonferroni:.6f}")
    print()

    if p_value < 0.001:
        verdict = "HIGHLY SIGNIFICANT (p < 0.001)"
    elif p_value < 0.01:
        verdict = "SIGNIFICANT (p < 0.01)"
    elif p_value < 0.05:
        verdict = "MARGINALLY SIGNIFICANT (p < 0.05)"
    else:
        verdict = "NOT SIGNIFICANT (p >= 0.05)"

    print(f"Verdict: {verdict}")
    print()

    # ── ASCII bar chart ──
    print("--- Identity Count Bar Chart ---")
    print()

    max_score = max(scores.values()) if scores else 1
    bar_width = 40

    for n in sorted(all_nums):
        s = scores[n]
        bar_len = int(s / max_score * bar_width) if max_score > 0 else 0
        pf = " ***" if is_perfect(n) else ""
        bar = "#" * bar_len + "." * (bar_width - bar_len)
        print(f"  n={n:>3} [{bar}] {s:>2}{pf}")

    print()
    print("  *** = perfect number")
    print()

    # ── Individual identity details for n=6 ──
    print("--- Detailed Identity Results for n=6 ---")
    print()
    if 6 in all_results:
        for name, passed, detail in all_results[6]:
            status = "PASS" if passed else "FAIL"
            print(f"  [{status}] {name:<20} {detail}")
    print()

    # ── Extended analysis: scan n=1..100 for any non-perfect with high score ──
    if extended:
        print("--- Extended Scan: n=2..100, identity counts ---")
        print()
        ext_scores = {}
        for nn in range(2, 101):
            checks = check_identities(nn)
            ext_scores[nn] = sum(1 for _, p, _ in checks if p)

        # Sort by score descending
        ranked = sorted(ext_scores.items(), key=lambda x: -x[1])

        print(f"{'Rank':>4} | {'n':>4} | {'Score':>5} | {'Perfect?':>8}")
        print("-" * 35)
        for rank, (nn, sc) in enumerate(ranked[:20], 1):
            pf = "YES" if is_perfect(nn) else ""
            print(f"{rank:>4} | {nn:>4} | {sc:>5} | {pf:>8}")

        print()
        print(f"Top non-perfect in [2,100]: n={ranked[0][0]} with score {ranked[0][1]}"
              if not is_perfect(ranked[0][0]) else
              f"Top scorer is perfect: n={ranked[0][0]} with score {ranked[0][1]}")

        # Find best non-perfect
        for nn, sc in ranked:
            if not is_perfect(nn):
                print(f"Best non-perfect: n={nn} with score {sc}")
                break
        print()

        # Distribution histogram
        score_dist = defaultdict(int)
        for nn, sc in ext_scores.items():
            score_dist[sc] += 1

        print("Score distribution (n=2..100):")
        for sc in sorted(score_dist.keys()):
            bar = "#" * score_dist[sc]
            has_perf = ""
            for nn, s2 in ext_scores.items():
                if s2 == sc and is_perfect(nn):
                    has_perf = f" <-- n={nn} (perfect)"
                    break
            print(f"  score={sc:>2}: {bar} ({score_dist[sc]}){has_perf}")
        print()

    # ── Final summary ──
    print("=" * 78)
    print("  FINAL SUMMARY")
    print("=" * 78)
    print()
    print(f"  Control group ({len(control_nums)} numbers): {sorted(control_nums)}")
    print(f"  Perfect group ({len(perfect_nums)} numbers): {sorted(perfect_nums)}")
    print()
    print(f"  n=6 identity score:       {scores.get(6, 0)}/{len(identity_names)}")
    print(f"  n=28 identity score:      {scores.get(28, 0)}/{len(identity_names)}")
    print(f"  n=496 identity score:     {scores.get(496, 0)}/{len(identity_names)}")
    print(f"  Control mean score:       {ctrl_mean:.2f} +/- {ctrl_std:.2f}")
    print(f"  Z-score (n=6 vs ctrl):    {z_6:.2f}")
    print(f"  Permutation p-value:      {p_value:.6f}")
    print(f"  Bonferroni p-value:       {p_bonferroni:.6f}")
    print(f"  Perfect-unique identities: {n_perfect_unique}/{len(identity_names)}")
    print()

    if scores.get(6, 0) > max(ctrl_scores) and p_value < 0.05:
        print("  CONCLUSION: n=6 is STRUCTURALLY SPECIAL.")
        print("  The identity count for perfect numbers significantly exceeds")
        print("  all control numbers. This is NOT a small-number effect.")
    elif scores.get(6, 0) > ctrl_mean + ctrl_std:
        print("  CONCLUSION: n=6 shows elevated identity count,")
        print("  but not all identities are unique to perfects.")
    else:
        print("  CONCLUSION: Results are INCONCLUSIVE.")
        print("  Non-perfect numbers show comparable identity counts.")

    print()
    return scores, p_value, z_6


def main():
    parser = argparse.ArgumentParser(description="Control Group Texas Sharpshooter Test")
    parser.add_argument("--extended", action="store_true", help="Extended scan n=2..100")
    parser.add_argument("--monte-carlo", type=int, default=10000, help="MC permutation trials")
    args = parser.parse_args()

    control = [5, 7, 8, 9, 10, 12, 14, 15, 18, 20]
    perfect = [6, 28, 496]

    run_analysis(control, perfect, mc_trials=args.monte_carlo, extended=args.extended)


if __name__ == "__main__":
    main()
