#!/usr/bin/env python3
"""
Verify: tau(n) + 2 = n has n=6 as the unique solution among all positive integers.

Proof outline:
  1. tau(n) <= 2*sqrt(n) for all n >= 1  (classical divisor bound)
  2. tau(n) + 2 = n  =>  n - 2 <= 2*sqrt(n)  =>  n <= 7
  3. Exhaustive check n=1..7 yields only n=6

This script:
  (a) Verifies the bound tau(n) <= 2*sqrt(n) up to N
  (b) Exhaustively checks tau(n)+2=n for n=1..N
  (c) Checks all known even perfect numbers
"""

import math
import sys


def tau(n: int) -> int:
    """Number of positive divisors of n."""
    if n < 1:
        raise ValueError(f"tau undefined for n={n}")
    if n == 1:
        return 1
    count = 0
    for d in range(1, int(math.isqrt(n)) + 1):
        if n % d == 0:
            count += 2 if d * d != n else 1
    return count


def verify_bound(limit: int) -> bool:
    """Verify tau(n) <= 2*sqrt(n) for all n in [1, limit]."""
    violations = []
    for n in range(1, limit + 1):
        t = tau(n)
        bound = 2 * math.sqrt(n)
        if t > bound:
            violations.append((n, t, bound))
    if violations:
        print(f"  BOUND VIOLATED at {len(violations)} points!")
        for n, t, b in violations[:10]:
            print(f"    n={n}: tau={t}, 2*sqrt={b:.4f}")
        return False
    print(f"  tau(n) <= 2*sqrt(n) verified for all n in [1, {limit}]")
    return True


def find_solutions(limit: int) -> list:
    """Find all n in [1, limit] with tau(n)+2 = n."""
    solutions = []
    for n in range(1, limit + 1):
        if tau(n) + 2 == n:
            solutions.append(n)
    return solutions


def theoretical_upper_bound() -> int:
    """
    Derive: tau(n)+2=n => n-2 <= 2*sqrt(n)
    Let x = sqrt(n): x^2 - 2x - 2 <= 0 => x <= 1 + sqrt(3)
    So n <= (1+sqrt(3))^2 = 4 + 2*sqrt(3) ~ 7.464
    """
    bound = (1 + math.sqrt(3)) ** 2
    return int(math.floor(bound))


def check_even_perfect_numbers():
    """
    Even perfect numbers: P_k = 2^(p-1) * (2^p - 1) where 2^p-1 is Mersenne prime.
    tau(P_k) = 2p.  Check 2p + 2 = P_k.
    """
    # Known Mersenne prime exponents (first 20)
    mersenne_exponents = [
        2, 3, 5, 7, 13, 17, 19, 31, 61, 89,
        107, 127, 521, 607, 1279, 2203, 2281, 3217, 4253, 4423,
    ]
    print("\n  Even perfect numbers P_k = 2^(p-1)*(2^p - 1):")
    print(f"  {'p':>6} | {'tau(P_k)=2p':>12} | {'tau+2':>12} | {'P_k':>20} | {'match':>5}")
    print(f"  {'-'*6}-+-{'-'*12}-+-{'-'*12}-+-{'-'*20}-+-{'-'*5}")
    for p in mersenne_exponents:
        pk = 2 ** (p - 1) * (2**p - 1)
        tau_pk = 2 * p
        lhs = tau_pk + 2
        match = "YES" if lhs == pk else "no"
        pk_str = str(pk) if pk < 10**18 else f"~10^{len(str(pk))-1}"
        print(f"  {p:>6} | {tau_pk:>12} | {lhs:>12} | {pk_str:>20} | {match:>5}")
    print()
    print("  Only p=2 (n=6) satisfies tau(n)+2=n among even perfect numbers.")


def main():
    print("=" * 70)
    print("  THEOREM: tau(n) + 2 = n has unique solution n = 6")
    print("=" * 70)

    # Step 1: Theoretical bound
    ub = theoretical_upper_bound()
    print(f"\n[Step 1] Theoretical upper bound from tau(n) <= 2*sqrt(n):")
    print(f"  n <= (1 + sqrt(3))^2 = 4 + 2*sqrt(3) = {(1+math.sqrt(3))**2:.6f}")
    print(f"  So n <= {ub}")

    # Step 2: Verify the divisor bound computationally
    CHECK_BOUND = 10_000
    print(f"\n[Step 2] Verify tau(n) <= 2*sqrt(n) for n=1..{CHECK_BOUND}:")
    verify_bound(CHECK_BOUND)

    # Step 3: Exhaustive check n=1..7 (the theoretical range)
    print(f"\n[Step 3] Exhaustive check n=1..{ub}:")
    print(f"  {'n':>3} | {'tau(n)':>6} | {'tau(n)+2':>8} | {'= n?':>5}")
    print(f"  {'-'*3}-+-{'-'*6}-+-{'-'*8}-+-{'-'*5}")
    for n in range(1, ub + 1):
        t = tau(n)
        eq = "YES" if t + 2 == n else "no"
        print(f"  {n:>3} | {t:>6} | {t+2:>8} | {eq:>5}")

    solutions_small = find_solutions(ub)
    print(f"\n  Solutions in [1, {ub}]: {solutions_small}")

    # Step 4: Extended computational check (beyond what the proof requires)
    EXTENDED = 10**6
    print(f"\n[Step 4] Extended brute-force check n=1..{EXTENDED} (redundant but reassuring):")
    solutions_ext = find_solutions(EXTENDED)
    print(f"  Solutions in [1, {EXTENDED}]: {solutions_ext}")
    assert solutions_ext == [6], f"Unexpected solutions: {solutions_ext}"
    print("  Confirmed: n=6 is the only solution up to 10^6.")

    # Step 5: Even perfect numbers
    print(f"\n[Step 5] Even perfect numbers:")
    check_even_perfect_numbers()

    # Step 6: Summary
    print("=" * 70)
    print("  RESULT: tau(n) + 2 = n  <=>  n = 6")
    print()
    print("  Proof method:")
    print("    tau(n) <= 2*sqrt(n)  =>  n-2 <= 2*sqrt(n)  =>  n <= 7")
    print("    Exhaustive check n=1..7: only n=6 works (tau(6)=4, 4+2=6)")
    print()
    print("  Corollary: Among even perfect numbers, only n=6 satisfies this.")
    print("    (For P_k = 2^(p-1)*(2^p-1): equation 2p+2=P_k holds only at p=2)")
    print("=" * 70)


if __name__ == "__main__":
    main()
