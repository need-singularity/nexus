#!/usr/bin/env python3
"""
Quadratic Form Representation Calculator
==========================================
Compute r_k(n) = number of representations of n as sum of k squares.
Includes Jacobi's theorem connections to sigma(n).

Usage:
  python3 quadratic_form_calculator.py --n 6
  python3 quadratic_form_calculator.py --n 6 --k 4
  python3 quadratic_form_calculator.py --perfect  # check all perfect numbers
  python3 quadratic_form_calculator.py --scan K N  # find r_K(n) = sigma-related
"""

import argparse
from sympy import factorint, divisors, totient, isprime, divisor_sigma
from math import gcd, isqrt
from fractions import Fraction


def sigma(n):
    return sum(divisors(n))

def tau(n):
    return len(divisors(n))

def phi(n):
    return totient(n)


def r_2(n):
    """Number of representations as sum of 2 squares (signed, ordered)."""
    count = 0
    for x in range(-isqrt(n), isqrt(n) + 1):
        rem = n - x * x
        if rem >= 0:
            y = isqrt(rem)
            if y * y == rem:
                count += 1 if y == 0 else 2
    return count


def r_3(n):
    """Number of representations as sum of 3 squares (signed, ordered)."""
    count = 0
    for x in range(-isqrt(n), isqrt(n) + 1):
        rem1 = n - x * x
        if rem1 >= 0:
            count += r_2(rem1)
    return count


def r_4_jacobi(n):
    """Jacobi's formula: r_4(n) = 8 * sum(d | n, 4 does not divide d)."""
    return 8 * sum(d for d in divisors(n) if d % 4 != 0)


def r_k_recursive(n, k, cache=None):
    """General r_k(n) via recursion. Slow for large k or n."""
    if cache is None:
        cache = {}
    key = (n, k)
    if key in cache:
        return cache[key]
    if k == 0:
        result = 1 if n == 0 else 0
    elif k == 1:
        result = 2 if n > 0 and isqrt(n) ** 2 == n else 0
        if n == 0:
            result = 1
    else:
        result = 0
        for x in range(-isqrt(n), isqrt(n) + 1):
            rem = n - x * x
            if rem >= 0:
                result += r_k_recursive(rem, k - 1, cache)
    cache[key] = result
    return result


def r_8_formula(n):
    """r_8(n) = 16 * sum_{d|n} (-1)^{n-d} * d^3."""
    return 16 * sum((-1) ** (n - d) * d ** 3 for d in divisors(n))


def analyze_n(n, max_k=8):
    """Full analysis of r_k(n) for k=1..max_k."""
    sig = sigma(n)
    t = tau(n)
    ph = phi(n)

    print(f"\n{'='*60}")
    print(f"Quadratic Form Analysis: n = {n}")
    print(f"{'='*60}")
    print(f"sigma({n}) = {sig}, tau({n}) = {t}, phi({n}) = {ph}")
    print(f"sigma*phi = {sig*ph}, tau! = {1 if t<=1 else __import__('math').factorial(t)}")
    print()

    # Check if 4 divides n
    divides_4 = (n % 4 == 0)
    print(f"4 | {n}: {divides_4}")
    if not divides_4:
        print(f"  => r_4({n}) = 8*sigma({n}) = {8*sig} (Jacobi full)")
    else:
        sigma_no4 = sum(d for d in divisors(n) if d % 4 != 0)
        print(f"  => r_4({n}) = 8*{sigma_no4} = {8*sigma_no4} (< 8*sigma = {8*sig})")
    print()

    # Check Legendre condition for r_3
    # n has r_3(n) = 0 iff n = 4^a(8b+7) for some a,b >= 0
    temp = n
    while temp % 4 == 0:
        temp //= 4
    r3_zero = (temp % 8 == 7)
    print(f"r_3({n}) = 0 (Legendre): {r3_zero}")
    print()

    print(f"{'k':>3} | {'r_k(n)':>10} | {'Connection':>30}")
    print("-" * 50)

    for k in range(1, max_k + 1):
        if k <= 4:
            if k == 4:
                rk = r_4_jacobi(n)
            elif k == 3:
                rk = r_3(n)
            elif k == 2:
                rk = r_2(n)
            else:
                rk = 2 if isqrt(n) ** 2 == n else 0
        elif k == 8:
            rk = r_8_formula(n)
        else:
            rk = r_k_recursive(n, k)

        # Check connections
        conn = ""
        if rk == sig:
            conn = f"= sigma({n})"
        elif rk == t:
            conn = f"= tau({n})"
        elif rk == ph:
            conn = f"= phi({n})"
        elif rk == sig * ph:
            conn = f"= sigma*phi = {sig*ph}"
        elif rk == 8 * sig:
            conn = f"= 8*sigma({n})"
        elif rk > 0 and isqrt(rk) ** 2 == rk:
            conn = f"= {isqrt(rk)}^2"

        print(f"{k:>3} | {rk:>10} | {conn:>30}")


def check_perfect_numbers():
    """Analyze r_k for the first few perfect numbers."""
    perfects = [6, 28, 496, 8128]
    for n in perfects:
        print(f"\n{'#'*60}")
        print(f"Perfect number P = {n}")
        print(f"{'#'*60}")
        sig = sigma(n)
        divides_4 = (n % 4 == 0)
        r4 = r_4_jacobi(n)
        print(f"  sigma = {sig}, 4|n = {divides_4}")
        print(f"  r_4 = {r4}, 8*sigma = {8*sig}")
        print(f"  r_4 = 8*sigma: {r4 == 8*sig}")
        if n <= 28:
            r3 = r_3(n)
            print(f"  r_3 = {r3}")
        if n <= 28:
            r8 = r_8_formula(n)
            print(f"  r_8 = {r8}, sqrt = {isqrt(r8) if r8 > 0 and isqrt(r8)**2 == r8 else 'not square'}")


def main():
    parser = argparse.ArgumentParser(description="Quadratic form representation calculator")
    parser.add_argument('--n', type=int, help='Analyze r_k(n)')
    parser.add_argument('--k', type=int, help='Specific k value')
    parser.add_argument('--max-k', type=int, default=8, help='Max k for analysis')
    parser.add_argument('--perfect', action='store_true', help='Check perfect numbers')
    args = parser.parse_args()

    if args.perfect:
        check_perfect_numbers()
    elif args.n:
        if args.k:
            if args.k == 4:
                print(f"r_4({args.n}) = {r_4_jacobi(args.n)}")
            elif args.k == 8:
                print(f"r_8({args.n}) = {r_8_formula(args.n)}")
            else:
                print(f"r_{args.k}({args.n}) = {r_k_recursive(args.n, args.k)}")
        else:
            analyze_n(args.n, max_k=args.max_k)
    else:
        # Demo
        analyze_n(6)
        print("\n")
        check_perfect_numbers()


if __name__ == '__main__':
    main()
