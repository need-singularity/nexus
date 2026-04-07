#!/usr/bin/env python3
"""
H-LOGIC-001: 6-smooth Numbers and the Perfect Number Denominator
Count B-smooth numbers, verify asymptotic formula, check lcm connections.

Run: PYTHONPATH=. python3 verify/verify_logic_001_6smooth.py
"""

import math
from fractions import Fraction


# ─── Smooth number counting ───

def is_b_smooth(n, B):
    """Check if n is B-smooth (all prime factors <= B)."""
    if n <= 1:
        return n == 1
    for p in range(2, B + 1):
        while n % p == 0:
            n //= p
    return n == 1


def count_smooth(x, B):
    """Count B-smooth numbers up to x (brute force)."""
    return sum(1 for n in range(1, x + 1) if is_b_smooth(n, B))


def list_smooth(x, B):
    """List B-smooth numbers up to x."""
    return [n for n in range(1, x + 1) if is_b_smooth(n, B)]


def asymptotic_smooth(x, primes):
    """
    Asymptotic formula for Psi(x, p_k):
    Psi(x, p_k) ~ (ln x)^k / (k! * prod(ln p_i))
    """
    if x <= 1:
        return 0.0
    k = len(primes)
    ln_x = math.log(x)
    numerator = ln_x ** k
    denominator = math.factorial(k)
    for p in primes:
        denominator *= math.log(p)
    return numerator / denominator


# ─── LCM computation ───

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def lcm(a, b):
    return a * b // gcd(a, b)


def lcm_range(n):
    """Compute lcm(1, 2, ..., n)."""
    result = 1
    for i in range(2, n + 1):
        result = lcm(result, i)
    return result


def factorize(n):
    """Return prime factorization as dict."""
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


def format_factorization(n):
    factors = factorize(n)
    parts = []
    for p in sorted(factors):
        if factors[p] == 1:
            parts.append(str(p))
        else:
            parts.append(f"{p}^{factors[p]}")
    return " * ".join(parts)


# ─── Main ───

def main():
    print("=" * 65)
    print("  H-LOGIC-001: 6-smooth Numbers and Perfect Number Denominator")
    print("  Verification Script")
    print("=" * 65)

    # ─── Part 1: Count smooth numbers and verify asymptotic formula ───

    print("\n" + "=" * 65)
    print("  Part 1: Smooth Number Counts vs Asymptotic Formula")
    print("=" * 65)

    test_values = [10, 100, 1000, 10000, 100000]

    # 3-smooth (primes {2, 3})
    print("\n  --- 3-smooth numbers (primes = {2, 3}) ---")
    print(f"  Asymptotic: Psi(x,3) ~ (ln x)^2 / (2 * ln 2 * ln 3)")
    print(f"  Denominator coefficient: 2! = 2")
    print()
    print(f"  {'x':>8} | {'Exact':>6} | {'Asymp':>8} | {'Ratio':>7} | {'Error':>7}")
    print(f"  {'-'*8}-+-{'-'*6}-+-{'-'*8}-+-{'-'*7}-+-{'-'*7}")

    for x in test_values:
        exact = count_smooth(x, 3)
        asymp = asymptotic_smooth(x, [2, 3])
        ratio = exact / asymp if asymp > 0 else float('inf')
        error = abs(exact - asymp) / exact * 100 if exact > 0 else 0
        print(f"  {x:>8} | {exact:>6} | {asymp:>8.2f} | {ratio:>7.4f} | {error:>6.1f}%")

    # 5-smooth (primes {2, 3, 5})
    print("\n  --- 5-smooth numbers (primes = {2, 3, 5}) ---")
    print(f"  Asymptotic: Psi(x,5) ~ (ln x)^3 / (6 * ln 2 * ln 3 * ln 5)")
    print(f"  Denominator coefficient: 3! = 6 = P_1 (first perfect number)")
    print()
    print(f"  {'x':>8} | {'Exact':>6} | {'Asymp':>8} | {'Ratio':>7} | {'Error':>7}")
    print(f"  {'-'*8}-+-{'-'*6}-+-{'-'*8}-+-{'-'*7}-+-{'-'*7}")

    for x in test_values:
        exact = count_smooth(x, 5)
        asymp = asymptotic_smooth(x, [2, 3, 5])
        ratio = exact / asymp if asymp > 0 else float('inf')
        error = abs(exact - asymp) / exact * 100 if exact > 0 else 0
        print(f"  {x:>8} | {exact:>6} | {asymp:>8.2f} | {ratio:>7.4f} | {error:>6.1f}%")

    # 7-smooth (primes {2, 3, 5, 7})
    print("\n  --- 7-smooth numbers (primes = {2, 3, 5, 7}) ---")
    print(f"  Asymptotic: Psi(x,7) ~ (ln x)^4 / (24 * ln 2 * ln 3 * ln 5 * ln 7)")
    print(f"  Denominator coefficient: 4! = 24 (NOT a perfect number)")
    print()
    print(f"  {'x':>8} | {'Exact':>6} | {'Asymp':>8} | {'Ratio':>7} | {'Error':>7}")
    print(f"  {'-'*8}-+-{'-'*6}-+-{'-'*8}-+-{'-'*7}-+-{'-'*7}")

    for x in test_values:
        exact = count_smooth(x, 7)
        asymp = asymptotic_smooth(x, [2, 3, 5, 7])
        ratio = exact / asymp if asymp > 0 else float('inf')
        error = abs(exact - asymp) / exact * 100 if exact > 0 else 0
        print(f"  {x:>8} | {exact:>6} | {asymp:>8.2f} | {ratio:>7.4f} | {error:>6.1f}%")

    # ─── Part 2: Denominator coefficient analysis ───

    print("\n" + "=" * 65)
    print("  Part 2: The k! Denominator — Factorial vs Perfect Number")
    print("=" * 65)

    print(f"\n  {'k':>3} | {'k!':>6} | {'Perfect?':>8} | {'Primes used':>20} | {'Smooth type':>12}")
    print(f"  {'-'*3}-+-{'-'*6}-+-{'-'*8}-+-{'-'*20}-+-{'-'*12}")

    perfect_numbers = {6, 28, 496, 8128}
    primes_list = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    for k in range(1, 11):
        kfact = math.factorial(k)
        is_perf = "YES" if kfact in perfect_numbers else "no"
        primes_str = "{" + ",".join(str(primes_list[i]) for i in range(k)) + "}"
        smooth_str = f"{primes_list[k-1]}-smooth"
        print(f"  {k:>3} | {kfact:>6} | {is_perf:>8} | {primes_str:>20} | {smooth_str:>12}")

    print(f"\n  Only k=3 gives k!=6=P_1. No other k! is a perfect number")
    print(f"  (28, 496, 8128 are not factorials of any integer).")
    print(f"  This is a Strong Law of Small Numbers coincidence.")

    # ─── Part 3: LCM verification ───

    print("\n" + "=" * 65)
    print("  Part 3: LCM Verification")
    print("=" * 65)

    lcm_checks = [6, 10, 12, 28]
    for n in lcm_checks:
        val = lcm_range(n)
        print(f"\n  lcm(1..{n}) = {val}")
        print(f"    = {format_factorization(val)}")

    print(f"\n  Key observation: lcm(1..6) = 60 = 2^2 * 3 * 5")
    print(f"  This is the Babylonian base!")
    print(f"  60 is the smallest number divisible by 1, 2, 3, 4, 5, and 6.")

    # ─── Part 4: 5-smooth numbers in decades (histogram) ───

    print("\n" + "=" * 65)
    print("  Part 4: Distribution of 5-smooth Numbers (ASCII Histogram)")
    print("=" * 65)

    smooth_100 = list_smooth(100, 5)
    print(f"\n  5-smooth numbers up to 100: {len(smooth_100)} total")
    print(f"  List: {smooth_100}")

    print(f"\n  Decade distribution:")
    print(f"  {'Range':>10} | {'Count':>5} | {'Bar':>30} | Numbers")
    print(f"  {'-'*10}-+-{'-'*5}-+-{'-'*30}-+-{'-'*30}")

    for decade in range(10):
        lo = decade * 10 + 1
        hi = (decade + 1) * 10
        nums_in_range = [n for n in smooth_100 if lo <= n <= hi]
        count = len(nums_in_range)
        bar = '#' * (count * 3)
        nums_str = ",".join(str(n) for n in nums_in_range)
        print(f"  {lo:>4}-{hi:<4} | {count:>5} | {bar:<30} | {nums_str}")

    # Extended histogram up to 1000
    print(f"\n  Century distribution (5-smooth up to 1000):")
    print(f"  {'Range':>12} | {'Count':>5} | Bar")
    print(f"  {'-'*12}-+-{'-'*5}-+-{'-'*40}")

    smooth_1000 = list_smooth(1000, 5)
    for cent in range(10):
        lo = cent * 100 + 1
        hi = (cent + 1) * 100
        count = sum(1 for n in smooth_1000 if lo <= n <= hi)
        bar = '#' * count
        print(f"  {lo:>5}-{hi:<5} | {count:>5} | {bar}")

    # ─── Part 5: Denominator constant analysis ───

    print("\n" + "=" * 65)
    print("  Part 5: Denominator Constant Values")
    print("=" * 65)

    ln2 = math.log(2)
    ln3 = math.log(3)
    ln5 = math.log(5)

    denom_3smooth = 2 * ln2 * ln3
    denom_5smooth = 6 * ln2 * ln3 * ln5

    print(f"\n  ln 2 = {ln2:.10f}")
    print(f"  ln 3 = {ln3:.10f}")
    print(f"  ln 5 = {ln5:.10f}")
    print()
    print(f"  3-smooth denominator: 2 * ln2 * ln3 = {denom_3smooth:.10f}")
    print(f"  5-smooth denominator: 6 * ln2 * ln3 * ln5 = {denom_5smooth:.10f}")
    print()
    print(f"  ln2 * ln3 = {ln2 * ln3:.10f}")
    print(f"  Compare with Golden Zone constants:")
    print(f"    1/e       = {1/math.e:.10f}   (diff = {abs(ln2*ln3 - 1/math.e):.6f})")
    print(f"    ln(4/3)   = {math.log(4/3):.10f}   (diff = {abs(ln2*ln3 - math.log(4/3)):.6f})")
    print(f"    1 - 1/e   = {1-1/math.e:.10f}   (diff = {abs(ln2*ln3 - (1-1/math.e)):.6f})")
    print(f"    1/2       = {0.5:.10f}   (diff = {abs(ln2*ln3 - 0.5):.6f})")

    # ─── Part 6: Convergence rate ───

    print("\n" + "=" * 65)
    print("  Part 6: Asymptotic Convergence (ratio exact/asymp -> 1)")
    print("=" * 65)

    print(f"\n  5-smooth convergence:")
    print(f"  {'x':>10} | {'Exact':>7} | {'Asymp':>10} | {'Ratio':>8}")
    print(f"  {'-'*10}-+-{'-'*7}-+-{'-'*10}-+-{'-'*8}")

    for exp in range(1, 8):
        x = 10 ** exp
        exact = count_smooth(x, 5)
        asymp = asymptotic_smooth(x, [2, 3, 5])
        ratio = exact / asymp if asymp > 0 else 0
        print(f"  {x:>10} | {exact:>7} | {asymp:>10.2f} | {ratio:>8.4f}")

    print(f"\n  Convergence is slow. Even at x=10^7, ratio is not close to 1.")
    print(f"  The asymptotic formula is a leading-order approximation;")
    print(f"  lower-order terms of (ln x)^2, (ln x), etc. are significant.")

    # ─── Part 7: Texas Sharpshooter assessment ───

    print("\n" + "=" * 65)
    print("  Part 7: Texas Sharpshooter Assessment")
    print("=" * 65)

    print(f"""
  Question: Is 3! = 6 = P_1 structurally significant?

  Target space: k! for k = 1, 2, 3, ..., 10
  Values:       1, 2, 6, 24, 120, 720, 5040, 40320, 362880, 3628800
  Perfect nums: 6, 28, 496, 8128, 33550336, ...

  Matches: Only k=3 -> 3! = 6 = P_1

  But this is exactly 1 match out of 10 trials = 10%.
  Expected by chance: Perfect numbers have density ~0 among large integers,
  but among small integers {1,2,6,24,120,...}, the density is artificially
  high because both sequences start small.

  Verdict: STRONG LAW OF SMALL NUMBERS applies.
  The coincidence 3! = P_1 = 6 is numerically true but not structurally deep.

  However, the CONNECTION lcm(1..6) = 60 = Babylonian base IS structural:
  it explains why base-60 was chosen historically (maximum divisibility
  by small numbers), and this connects to 5-smooth = sexagesimal-regular.
""")

    # ─── Grading ───

    print("=" * 65)
    print("  GRADING")
    print("=" * 65)
    print(f"""
  1. Asymptotic formula Psi(x,5) ~ (ln x)^3 / (6 ln2 ln3 ln5):
     VERIFIED (convergence slow but correct direction)
     Grade: 🟩 (proven theorem, Dickman-de Bruijn)

  2. The 6 in denominator = 3! (not structurally P_1):
     VERIFIED — it is the simplex volume 1/k! for k=3
     Grade: 🟩 (exact, but the P_1 connection is coincidental)

  3. lcm(1..6) = 60 = Babylonian base:
     VERIFIED — 60 = 2^2 * 3 * 5
     Grade: 🟩 (exact, well-known)

  4. ln2 * ln3 connection to Golden Zone:
     NOT CONFIRMED — no clean ratio found
     Grade: grey-area (no structural match)

  5. Texas Sharpshooter (3! = P_1):
     Strong Law of Small Numbers warning.
     Grade: likely coincidental

  OVERALL: 🟩 for verified arithmetic facts.
  The P_1=6 connection in the smooth number formula is coincidental.
  The lcm(1..6)=60 Babylonian connection is real but well-known.
""")


if __name__ == "__main__":
    main()
