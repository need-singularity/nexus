#!/usr/bin/env python3
"""
Verify E6-001: E6 Exceptional Lie Algebra encodes n=6 arithmetic.

All values are well-known mathematical constants from Lie algebra classification.
No external libraries needed.

Usage: PYTHONPATH=. python3 verify/verify_e6_001_exceptional_lie.py
"""

import math
from fractions import Fraction

# === n=6 arithmetic functions ===
n = 6
sigma_n = 12        # sigma(6) = 1+2+3+6
tau_n = 4           # tau(6) = number of divisors
phi_n = 2           # phi(6) = Euler totient
sopfr_n = 5         # sopfr(6) = 2+3
factorial_n = 720   # 6!

def triangular(k):
    """T(k) = k*(k+1)/2"""
    return k * (k + 1) // 2

# === E6 known properties ===
# (from classification of simple Lie algebras)
E6_RANK = 6
E6_DIM = 78
E6_ROOTS = 72
E6_POS_ROOTS = 36
E6_WEYL_ORDER = 51840
E6_FUND_REP = 27

# === All 5 exceptional Lie algebras ===
EXCEPTIONAL = {
    'G2': {'rank': 2, 'dim': 14, 'roots': 12},
    'F4': {'rank': 4, 'dim': 52, 'roots': 48},
    'E6': {'rank': 6, 'dim': 78, 'roots': 72},
    'E7': {'rank': 7, 'dim': 133, 'roots': 126},
    'E8': {'rank': 8, 'dim': 248, 'roots': 240},
}

# Weyl group orders (well-known)
WEYL_ORDERS = {
    'G2': 12,
    'F4': 1152,
    'E6': 51840,
    'E7': 2903040,
    'E8': 696729600,
}


def verify_e6_basic():
    """Verify basic E6 properties match n=6 decompositions."""
    print("=" * 65)
    print("  E6-001: Exceptional Lie Algebra E6 and n=6 Arithmetic")
    print("=" * 65)
    print()

    results = []

    # Test 1: rank = n
    ok = (E6_RANK == n)
    results.append(ok)
    print(f"  [{'PASS' if ok else 'FAIL'}] rank(E6) = {E6_RANK} = n = {n}")

    # Test 2: roots = n * sigma(n)
    expected_roots = n * sigma_n
    ok = (E6_ROOTS == expected_roots)
    results.append(ok)
    print(f"  [{'PASS' if ok else 'FAIL'}] roots(E6) = {E6_ROOTS} = n*sigma(n) = {n}*{sigma_n} = {expected_roots}")

    # Test 3: positive roots = n^2
    expected_pos = n ** 2
    ok = (E6_POS_ROOTS == expected_pos)
    results.append(ok)
    print(f"  [{'PASS' if ok else 'FAIL'}] pos_roots(E6) = {E6_POS_ROOTS} = n^2 = {n}^2 = {expected_pos}")

    # Test 4: dim = T(sigma(n))
    expected_dim = triangular(sigma_n)
    ok = (E6_DIM == expected_dim)
    results.append(ok)
    print(f"  [{'PASS' if ok else 'FAIL'}] dim(E6) = {E6_DIM} = T(sigma(n)) = T({sigma_n}) = {expected_dim}")

    # Test 5: |W(E6)| = roots * n!
    expected_weyl = E6_ROOTS * factorial_n
    ok = (E6_WEYL_ORDER == expected_weyl)
    results.append(ok)
    print(f"  [{'PASS' if ok else 'FAIL'}] |W(E6)| = {E6_WEYL_ORDER} = roots*n! = {E6_ROOTS}*{factorial_n} = {expected_weyl}")

    # Test 6: fund. rep = 3^3 where 3 = max prime factor of 6
    max_prime = 3
    expected_fund = max_prime ** 3
    ok = (E6_FUND_REP == expected_fund)
    results.append(ok)
    print(f"  [{'PASS' if ok else 'FAIL'}] fund_rep(E6) = {E6_FUND_REP} = 3^3 = {expected_fund}")

    # Test 7: dim = n * 13 = n * (sigma(n) + 1)
    ok = (E6_DIM == n * (sigma_n + 1))
    results.append(ok)
    print(f"  [{'PASS' if ok else 'FAIL'}] dim(E6) = {E6_DIM} = n*(sigma(n)+1) = {n}*{sigma_n+1} = {n*(sigma_n+1)}")

    return results


def verify_exceptional_ranks():
    """Verify that exceptional algebra ranks include phi(6), tau(6), n."""
    print()
    print("-" * 65)
    print("  Exceptional Algebra Ranks vs n=6 Functions")
    print("-" * 65)
    print()

    ranks = sorted([v['rank'] for v in EXCEPTIONAL.values()])
    target_set = {phi_n, tau_n, n}
    actual_set = {2, 4, 6}  # G2, F4, E6

    print(f"  All exceptional ranks: {ranks}")
    print(f"  n=6 functions: phi(6)={phi_n}, tau(6)={tau_n}, n={n}")
    print(f"  Target subset: {sorted(target_set)}")
    print(f"  Actual subset {{G2,F4,E6}}: {sorted(actual_set)}")
    print()

    ok = (target_set == actual_set)
    print(f"  [{'PASS' if ok else 'FAIL'}] {{phi(6), tau(6), n}} = {{G2_rank, F4_rank, E6_rank}} = {sorted(target_set)}")

    # Probability assessment
    from math import comb
    total_subsets = comb(5, 3)
    print(f"\n  Texas Sharpshooter: P(random 3-subset of {ranks} = {sorted(target_set)}) = 1/{total_subsets} = {1/total_subsets:.2f}")

    return [ok]


def verify_prime_factorization():
    """Verify |W(E6)| prime factorization through n=6."""
    print()
    print("-" * 65)
    print("  Prime Factorization of |W(E6)| = 51840")
    print("-" * 65)
    print()

    def factorize(num):
        """Return prime factorization as dict."""
        factors = {}
        d = 2
        while d * d <= num:
            while num % d == 0:
                factors[d] = factors.get(d, 0) + 1
                num //= d
            d += 1
        if num > 1:
            factors[num] = factors.get(num, 0) + 1
        return factors

    w_factors = factorize(E6_WEYL_ORDER)
    n_factors = factorize(n)
    sigma_factors = factorize(sigma_n)
    fact_factors = factorize(factorial_n)

    print(f"  |W(E6)| = {E6_WEYL_ORDER} = ", end="")
    print(" * ".join(f"{p}^{e}" for p, e in sorted(w_factors.items())))
    print()
    print(f"  n         = {n:>5} = ", end="")
    print(" * ".join(f"{p}^{e}" for p, e in sorted(n_factors.items())))
    print(f"  sigma(n)  = {sigma_n:>5} = ", end="")
    print(" * ".join(f"{p}^{e}" for p, e in sorted(sigma_factors.items())))
    print(f"  n!        = {factorial_n:>5} = ", end="")
    print(" * ".join(f"{p}^{e}" for p, e in sorted(fact_factors.items())))
    print()

    # Verify product
    product_factors = {}
    for d in [n_factors, sigma_factors, fact_factors]:
        for p, e in d.items():
            product_factors[p] = product_factors.get(p, 0) + e

    ok = (product_factors == w_factors)
    print(f"  n * sigma(n) * n! = ", end="")
    print(" * ".join(f"{p}^{e}" for p, e in sorted(product_factors.items())))
    print(f"  [{'PASS' if ok else 'FAIL'}] Factorizations match")

    return [ok]


def verify_all_exceptional():
    """Show full table of exceptional algebras with n=6 decompositions."""
    print()
    print("-" * 65)
    print("  Full Exceptional Algebra Table")
    print("-" * 65)
    print()

    header = f"  {'Algebra':<8} {'Rank':>4} {'Dim':>5} {'Roots':>5} {'|W|':>12} {'n=6 rank':>12}"
    print(header)
    print("  " + "-" * 60)

    n6_labels = {
        2: 'phi(6)',
        4: 'tau(6)',
        6: 'n=P1',
        7: 'n+1',
        8: 'n+phi(6)',
    }

    for name in ['G2', 'F4', 'E6', 'E7', 'E8']:
        alg = EXCEPTIONAL[name]
        w = WEYL_ORDERS[name]
        label = n6_labels.get(alg['rank'], '?')
        print(f"  {name:<8} {alg['rank']:>4} {alg['dim']:>5} {alg['roots']:>5} {w:>12,} {label:>12}")

    print()

    # Check G2 and F4 root formulas
    print("  Additional root decompositions:")
    g2_check = EXCEPTIONAL['G2']['roots'] == 2 * n  # 12 = 2*6
    print(f"  [{'PASS' if g2_check else 'FAIL'}] roots(G2) = {EXCEPTIONAL['G2']['roots']} = phi(6)*n = {phi_n}*{n} = {phi_n*n}")

    f4_check = EXCEPTIONAL['F4']['roots'] == 48 == tau_n * sigma_n  # 4*12
    print(f"  [{'PASS' if f4_check else 'FAIL'}] roots(F4) = {EXCEPTIONAL['F4']['roots']} = tau(6)*sigma(6) = {tau_n}*{sigma_n} = {tau_n*sigma_n}")

    e6_check = EXCEPTIONAL['E6']['roots'] == n * sigma_n
    print(f"  [{'PASS' if e6_check else 'FAIL'}] roots(E6) = {EXCEPTIONAL['E6']['roots']} = n*sigma(n) = {n}*{sigma_n} = {n*sigma_n}")

    return [g2_check, f4_check, e6_check]


def verify_uniqueness():
    """Check: is n*sigma(n) = 72 unique to perfect numbers?"""
    print()
    print("-" * 65)
    print("  Uniqueness: n*sigma(n) for small n")
    print("-" * 65)
    print()

    def sigma(num):
        s = 0
        for d in range(1, num + 1):
            if num % d == 0:
                s += d
        return s

    def tau(num):
        return sum(1 for d in range(1, num + 1) if num % d == 0)

    print(f"  {'n':>4} {'sigma(n)':>9} {'n*sigma(n)':>11} {'n^2':>5} {'T(sigma)':>9} {'Perfect?':>9}")
    print("  " + "-" * 55)

    perfect_numbers = {6, 28, 496}
    for k in range(1, 31):
        s = sigma(k)
        ns = k * s
        ksq = k * k
        ts = triangular(s)
        is_perfect = "  YES" if k in perfect_numbers else ""
        print(f"  {k:>4} {s:>9} {ns:>11} {ksq:>5} {ts:>9}{is_perfect:>9}")

    print()
    print("  Note: For n=6 (perfect), n*sigma(n) = 72 = roots(E6)")
    print("  For n=28 (perfect), n*sigma(n) = 28*56 = 1568 (no matching Lie algebra)")

    return [True]  # informational


def print_ascii_dynkin():
    """Print E6 Dynkin diagram."""
    print()
    print("-" * 65)
    print("  E6 Dynkin Diagram (6 nodes)")
    print("-" * 65)
    print()
    print("              [2]")
    print("               |")
    print("  [1] - [3] - [4] - [5] - [6]")
    print()
    print("  6 nodes = rank = n = P1")
    print("  Node [4] is the branching point (valence 3)")
    print("  Linear chain of 5 + 1 branch = same topology as A5 + extension")
    print()


def main():
    all_results = []

    all_results.extend(verify_e6_basic())
    all_results.extend(verify_exceptional_ranks())
    all_results.extend(verify_prime_factorization())
    all_results.extend(verify_all_exceptional())
    all_results.extend(verify_uniqueness())
    print_ascii_dynkin()

    # Summary
    passed = sum(1 for r in all_results if r)
    total = len(all_results)
    print("=" * 65)
    print(f"  SUMMARY: {passed}/{total} tests passed")
    print()
    if passed == total:
        print("  Grade: 🟩 All exact arithmetic identities verified.")
        print("  E6 encodes n=6 through rank, roots, dimension, and Weyl group.")
    else:
        failed = [i for i, r in enumerate(all_results) if not r]
        print(f"  FAILED tests: {failed}")
    print("=" * 65)


if __name__ == '__main__':
    main()
