#!/usr/bin/env python3
"""
H-CX-489 & H-CX-494 Verification
==================================
H-CX-489: For perfect number P_n = 2^(p-1)(2^p - 1), k_min = 2p - 1
           where k_min = minimum k for 1 = sum(1/a_i) with lcm(a_i) = P_n.

H-CX-494: P_3 = 496 (p=5): prediction k_min = 9.

Strategy: Since lcm(a_i) must equal P_n, all a_i must be divisors of P_n.
          Search all subsets of divisors(P_n) \ {1} whose reciprocal sum = 1.
"""

from itertools import combinations
from math import gcd, lcm
from functools import reduce
from fractions import Fraction


def get_divisors(n):
    """Return sorted list of divisors of n."""
    divs = []
    for i in range(1, int(n**0.5) + 1):
        if n % i == 0:
            divs.append(i)
            if i != n // i:
                divs.append(n // i)
    return sorted(divs)


def multi_lcm(lst):
    """LCM of a list of integers."""
    return reduce(lcm, lst)


def search_egyptian_fractions(n, verbose=True):
    """
    Find all subsets of divisors(n) \ {1} whose reciprocal sum = 1
    and whose lcm = n.
    Returns dict: k -> list of solutions.
    """
    divs = get_divisors(n)
    divs_no1 = [d for d in divs if d > 1]

    if verbose:
        print(f"\n{'='*60}")
        print(f"  Searching P = {n}")
        print(f"  Divisors (excl. 1): {divs_no1}")
        print(f"  Number of candidate divisors: {len(divs_no1)}")
        print(f"{'='*60}")

    # Precompute reciprocals as Fractions for exact arithmetic
    recips = {d: Fraction(1, d) for d in divs_no1}

    solutions_by_k = {}
    total_checked = 0

    # Search subsets of size k from 2 up to len(divs_no1)
    for k in range(2, len(divs_no1) + 1):
        solutions = []
        # Pruning: if min possible sum > 1, skip this k
        sorted_recips_asc = sorted(recips.values())
        min_sum_k = sum(sorted_recips_asc[:k])
        if min_sum_k > 1:
            if verbose:
                print(f"  k={k}: min possible sum = {float(min_sum_k):.6f} > 1, skipping")
            continue

        for combo in combinations(divs_no1, k):
            total_checked += 1
            s = sum(Fraction(1, d) for d in combo)
            if s == 1:
                l = multi_lcm(combo)
                if l == n:
                    solutions.append(combo)

        if solutions:
            solutions_by_k[k] = solutions
            if verbose:
                print(f"  k={k}: {len(solutions)} solution(s) with lcm={n}")
                for sol in solutions:
                    terms = " + ".join(f"1/{d}" for d in sol)
                    print(f"         {terms} = 1")
                    print(f"         lcm = {multi_lcm(sol)}")
        else:
            if verbose:
                print(f"  k={k}: no solutions")

    if verbose:
        print(f"  Total subsets checked: {total_checked}")

    return solutions_by_k


def verify_perfect_number(p, predicted_kmin):
    """Verify k_min for perfect number 2^(p-1) * (2^p - 1)."""
    mersenne = 2**p - 1
    perfect = 2**(p-1) * mersenne
    print(f"\n{'#'*60}")
    print(f"  Perfect number P = 2^{p-1} * (2^{p}-1) = {2**(p-1)} * {mersenne} = {perfect}")
    print(f"  Mersenne prime: {mersenne}")
    print(f"  Predicted k_min = 2*{p} - 1 = {predicted_kmin}")
    print(f"{'#'*60}")

    solutions = search_egyptian_fractions(perfect)

    if solutions:
        actual_kmin = min(solutions.keys())
        match = "CONFIRMED" if actual_kmin == predicted_kmin else "FAILED"
        print(f"\n  >>> k_min({perfect}) = {actual_kmin}  (predicted: {predicted_kmin}) [{match}]")
    else:
        print(f"\n  >>> No solutions found!")

    return solutions


def analyze_mathematical_reason():
    """Analyze WHY k_min = 2p - 1 might hold."""
    print(f"\n{'#'*60}")
    print(f"  MATHEMATICAL ANALYSIS: Why k_min = 2p - 1?")
    print(f"{'#'*60}")

    print("""
  Structure of perfect number P = 2^(p-1) * (2^p - 1):
  - Divisors: 2^a * q where 0 <= a <= p-1, q in {1, 2^p - 1}
  - So divisors = {1, 2, 4, ..., 2^(p-1)} union {M, 2M, 4M, ..., 2^(p-1)*M}
    where M = 2^p - 1 (Mersenne prime)
  - Total number of divisors: 2p

  Divisors >= 2 (candidates): 2p - 1 divisors (all except 1)

  Key observation: The reciprocal sum of ALL divisors >= 2 equals:
    sum(1/d for d in divisors if d >= 2) = sigma_{-1}(P) - 1
    For perfect numbers, sigma_{-1}(P) = 2, so the sum = 1.

  This means the FULL SET of divisors >= 2 always gives sum = 1.
  That set has exactly 2p - 1 elements.
  """)

    for p in [2, 3, 5]:
        M = 2**p - 1
        P = 2**(p-1) * M
        divs = get_divisors(P)
        divs_ge2 = [d for d in divs if d >= 2]
        s = sum(Fraction(1, d) for d in divs_ge2)
        print(f"  P={P} (p={p}): divisors >= 2 = {divs_ge2}")
        print(f"    count = {len(divs_ge2)}, reciprocal sum = {s} = {float(s):.6f}")
        print(f"    sigma_{{-1}}(P) = {float(sum(Fraction(1,d) for d in divs)):.6f}")
        print()

    print("""
  So the question becomes: Can ANY proper subset of divisors >= 2
  also sum to 1 (with lcm still = P)?

  If not, then k_min = 2p - 1 = |divisors >= 2|, meaning you need
  ALL non-trivial divisors.

  Let's check if removing any single divisor still gives sum = 1:
  Removing divisor d changes sum by -1/d.
  New sum = 1 - 1/d < 1 for any d >= 2.
  So no (2p-2)-element subset works.

  But could a DIFFERENT k < 2p-1 subset (not obtained by removal) work?
  That's what the exhaustive search answers.
  """)

    # Additional check: can we replace a removed element?
    print("  Checking if any divisor can be decomposed into others:")
    print("  (i.e., 1/d = 1/a + 1/b for divisors a,b of P, a,b != d)")
    for p in [2, 3, 5]:
        M = 2**p - 1
        P = 2**(p-1) * M
        divs = get_divisors(P)
        divs_ge2 = [d for d in divs if d >= 2]
        print(f"\n  P={P} (p={p}):")
        found_decomp = False
        for d in divs_ge2:
            for a in divs_ge2:
                for b in divs_ge2:
                    if a <= b and a != d and b != d:
                        if Fraction(1, d) == Fraction(1, a) + Fraction(1, b):
                            print(f"    1/{d} = 1/{a} + 1/{b}")
                            found_decomp = True
        if not found_decomp:
            print(f"    No decompositions found among divisors.")


def main():
    print("=" * 60)
    print("  H-CX-489 & H-CX-494 VERIFICATION")
    print("  Egyptian fraction k_min for perfect numbers")
    print("=" * 60)

    # Part 1: P_1 = 6 (p=2), predicted k_min = 3
    sol6 = verify_perfect_number(p=2, predicted_kmin=3)

    # Part 2: P_2 = 28 (p=3), predicted k_min = 5
    sol28 = verify_perfect_number(p=3, predicted_kmin=5)

    # Part 3: P_3 = 496 (p=5), predicted k_min = 9
    sol496 = verify_perfect_number(p=5, predicted_kmin=9)

    # Part 4: Mathematical analysis
    analyze_mathematical_reason()

    # Summary
    print(f"\n{'='*60}")
    print(f"  SUMMARY")
    print(f"{'='*60}")
    results = [
        (6, 2, 3, sol6),
        (28, 3, 5, sol28),
        (496, 5, 9, sol496),
    ]
    print(f"\n  {'P':>5} | {'p':>3} | {'predicted':>9} | {'actual':>6} | {'status':>10}")
    print(f"  {'-'*5}-+-{'-'*3}-+-{'-'*9}-+-{'-'*6}-+-{'-'*10}")
    for P, p, pred, sols in results:
        if sols:
            actual = min(sols.keys())
            status = "CONFIRMED" if actual == pred else "FAILED"
        else:
            actual = "N/A"
            status = "NO SOLN"
        print(f"  {P:>5} | {p:>3} | {pred:>9} | {str(actual):>6} | {status:>10}")

    print(f"\n  H-CX-489 formula: k_min = 2p - 1")

    all_confirmed = all(
        min(sols.keys()) == pred
        for P, p, pred, sols in results
        if sols
    )
    if all_confirmed:
        print(f"  STATUS: ALL THREE CASES CONFIRMED")
        print(f"\n  Key insight: For perfect number P with 2p divisors,")
        print(f"  ALL 2p-1 non-trivial divisors are needed because")
        print(f"  sigma_{{-1}}(P) = 2 => sum of reciprocals of ALL divisors >= 2 is exactly 1,")
        print(f"  and no proper subset achieves sum = 1 with lcm = P.")
    else:
        print(f"  STATUS: FORMULA NOT FULLY CONFIRMED")

    print()


if __name__ == "__main__":
    main()
