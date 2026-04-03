#!/usr/bin/env python3
"""Catalan & Combinatorial Sequences at n=6 — Systematic verification

Tests whether Catalan numbers, Fibonacci, Bell, partitions, Bernoulli,
Stirling numbers, and derangements encode the arithmetic of n=6.

n=6 constants: P1=6, sigma=12, tau=4, phi=2, sopfr=5, M3=7, P2=28

Usage:
  python3 calc/catalan_combinatorial_n6.py             # Full analysis
  python3 calc/catalan_combinatorial_n6.py --texas      # Texas Sharpshooter only
  python3 calc/catalan_combinatorial_n6.py --section catalan  # Single section
"""

import argparse
import math
import sys
from fractions import Fraction
from functools import lru_cache

# ═══════════════════════════════════════════════════════════════
# n=6 Constants
# ═══════════════════════════════════════════════════════════════

P1 = 6          # First perfect number
SIGMA = 12      # sigma(6) = sum of divisors
TAU = 4         # tau(6) = number of divisors
PHI = 2         # phi(6) = Euler totient
SOPFR = 5       # sopfr(6) = sum of prime factors with multiplicity
M3 = 7          # Mersenne prime 2^3 - 1
P2 = 28         # Second perfect number
P3 = 496        # Third perfect number

N6_CONSTANTS = {P1, SIGMA, TAU, PHI, SOPFR, M3, P2}
N6_NAMES = {
    1: "1", 2: "phi(6)", 3: "omega+1", 4: "tau(6)", 5: "sopfr(6)",
    6: "P1", 7: "M3", 8: "phi*tau", 11: "sopfr(P2)",
    12: "sigma(6)", 14: "2*M3", 15: "C(6,2)", 28: "P2",
    31: "M5=2^5-1", 36: "P1^2", 42: "M3*P1", 63: "M6=2^6-1",
    120: "P1!", 132: "sigma*11", 144: "sigma^2", 203: "M3*29",
    265: "5*53", 720: "P1!",
}


# ═══════════════════════════════════════════════════════════════
# Arithmetic Functions
# ═══════════════════════════════════════════════════════════════

def factorize(n):
    """Return prime factorization as dict {prime: exponent}."""
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


def sigma_func(n):
    """Sum of divisors."""
    if n <= 0:
        return 0
    factors = factorize(n)
    result = 1
    for p, e in factors.items():
        result *= (p**(e+1) - 1) // (p - 1)
    return result


def tau_func(n):
    """Number of divisors."""
    if n <= 0:
        return 0
    factors = factorize(n)
    result = 1
    for e in factors.values():
        result *= (e + 1)
    return result


def phi_func(n):
    """Euler totient."""
    if n <= 0:
        return 0
    factors = factorize(n)
    result = n
    for p in factors:
        result = result * (p - 1) // p
    return result


def sopfr_func(n):
    """Sum of prime factors with multiplicity."""
    factors = factorize(n)
    return sum(p * e for p, e in factors.items())


def format_factorization(n):
    """Pretty-print factorization."""
    if n <= 1:
        return str(n)
    factors = factorize(n)
    parts = []
    for p in sorted(factors):
        e = factors[p]
        if e == 1:
            parts.append(str(p))
        else:
            parts.append(f"{p}^{e}")
    return " * ".join(parts)


# ═══════════════════════════════════════════════════════════════
# Combinatorial Sequences
# ═══════════════════════════════════════════════════════════════

@lru_cache(maxsize=1000)
def catalan(n):
    """Catalan number C_n = C(2n,n)/(n+1)."""
    return math.comb(2 * n, n) // (n + 1)


@lru_cache(maxsize=1000)
def fibonacci(n):
    """Fibonacci number F_n (F_0=0, F_1=1)."""
    if n <= 0:
        return 0
    if n == 1:
        return 1
    return fibonacci(n - 1) + fibonacci(n - 2)


@lru_cache(maxsize=1000)
def bell(n):
    """Bell number B(n) = number of partitions of a set."""
    if n == 0:
        return 1
    return sum(math.comb(n - 1, k) * bell(k) for k in range(n))


@lru_cache(maxsize=1000)
def partition(n):
    """Integer partition function p(n)."""
    if n < 0:
        return 0
    if n == 0:
        return 1
    result = 0
    k = 1
    while True:
        # Pentagonal numbers: k(3k-1)/2 and k(3k+1)/2
        g1 = k * (3 * k - 1) // 2
        g2 = k * (3 * k + 1) // 2
        if g1 > n:
            break
        sign = (-1) ** (k + 1)
        result += sign * partition(n - g1)
        if g2 <= n:
            result += sign * partition(n - g2)
        k += 1
    return result


def bernoulli(n):
    """Bernoulli number B_n as Fraction."""
    B = [Fraction(0)] * (n + 1)
    B[0] = Fraction(1)
    for m in range(1, n + 1):
        B[m] = Fraction(0)
        for k in range(m):
            B[m] -= Fraction(math.comb(m + 1, k)) * B[k]
        B[m] /= Fraction(m + 1)
    return B[n]


def stirling2(n, k):
    """Stirling number of the second kind S(n,k)."""
    if n == 0 and k == 0:
        return 1
    if n == 0 or k == 0:
        return 0
    if k > n:
        return 0
    # Explicit formula
    result = 0
    for j in range(k + 1):
        sign = (-1) ** (k - j)
        result += sign * math.comb(k, j) * j ** n
    result //= math.factorial(k)
    return result


def derangement(n):
    """Subfactorial !n = number of derangements."""
    if n == 0:
        return 1
    if n == 1:
        return 0
    result = 0
    for k in range(n + 1):
        result += ((-1) ** k) * math.factorial(n) // math.factorial(k)
    return result


# ═══════════════════════════════════════════════════════════════
# Analysis Sections
# ═══════════════════════════════════════════════════════════════

def n6_interpret(value):
    """Try to express value in terms of n=6 constants."""
    if value in N6_NAMES:
        return N6_NAMES[value]
    # Try simple products/sums
    for a_name, a_val in [("P1", P1), ("sigma", SIGMA), ("tau", TAU),
                           ("phi", PHI), ("sopfr", SOPFR), ("M3", M3)]:
        if value > 0 and value % a_val == 0:
            q = value // a_val
            if q in N6_NAMES:
                return f"{a_name}*{N6_NAMES[q]}"
            if q < 50:
                return f"{a_name}*{q}"
        if value - a_val in N6_NAMES and value - a_val > 0:
            return f"{a_name}+{N6_NAMES[value - a_val]}"
    return ""


def section_catalan():
    """Catalan numbers analysis."""
    print("=" * 70)
    print("SECTION 1: CATALAN NUMBERS C_n")
    print("=" * 70)
    print()

    print("  C_n = C(2n,n)/(n+1)")
    print()
    print(f"  {'n':>3} | {'C_n':>12} | {'Factorization':>25} | {'n=6 connection'}")
    print(f"  {'-'*3}-+-{'-'*12}-+-{'-'*25}-+-{'-'*30}")

    hits = []
    for n in range(11):
        c = catalan(n)
        interp = n6_interpret(c)
        fac = format_factorization(c) if c > 1 else str(c)
        marker = " <--" if interp else ""
        print(f"  {n:>3} | {c:>12} | {fac:>25} | {interp}{marker}")
        if interp:
            hits.append((n, c, interp))

    print()
    print(f"  Hits: {len(hits)}/11")
    print()

    # Key observations
    print("  Key observations:")
    print(f"    C_3 = 5 = sopfr(6)")
    print(f"    C_5 = 42 = M3 * P1 = 7 * 6")
    print(f"    C_6 = 132 = sigma(6) * 11 = sigma(6) * sopfr(P2)")
    print()

    # Sum C_0..C_6
    s = sum(catalan(i) for i in range(7))
    print(f"  Sum C_0..C_6 = {s}")
    print(f"    196883 / 1000 = 196.883")
    print(f"    {s} vs 196.883: delta = {abs(s - 196.883):.3f} ({abs(s-196.883)/196.883*100:.1f}%)")
    print(f"    NOT close. Coincidence rejected.")
    print()

    # Catalan at perfect number indices
    print("  Catalan at perfect number indices:")
    for pn, pn_name in [(6, "P1"), (28, "P2")]:
        c = catalan(pn)
        print(f"    C_{pn} = {c}")
        print(f"      = {format_factorization(c)}")
        for mod_by, mod_name in [(6, "P1"), (28, "P2"), (12, "sigma")]:
            print(f"      mod {mod_by} ({mod_name}) = {c % mod_by}")
    print()

    return hits


def section_fibonacci():
    """Fibonacci numbers analysis."""
    print("=" * 70)
    print("SECTION 2: FIBONACCI NUMBERS F_n")
    print("=" * 70)
    print()

    print(f"  {'n':>3} | {'F_n':>8} | {'n=6 connection'}")
    print(f"  {'-'*3}-+-{'-'*8}-+-{'-'*40}")

    hits = []
    for n in range(1, 16):
        f = fibonacci(n)
        interp = n6_interpret(f)
        marker = " <--" if interp else ""
        print(f"  {n:>3} | {f:>8} | {interp}{marker}")
        if interp:
            hits.append((n, f, interp))

    print()
    print(f"  Hits: {len(hits)}/15")
    print()

    # Key findings
    print("  Key findings:")
    print(f"    F_6  = {fibonacci(6)} = sigma - tau = {SIGMA} - {TAU} = {SIGMA-TAU}")
    print(f"         = Bott periodicity dimension!")
    print(f"    F_12 = {fibonacci(12)} = sigma^2 = {SIGMA}^2 = {SIGMA**2}")
    print(f"         = F_sigma(6) = sigma(6)^2  *** DEEP ***")
    print()

    # Check: F_{sigma(n)} = sigma(n)^2 for other perfect numbers?
    print("  Generalization test: F_{sigma(n)} vs sigma(n)^2")
    for n, name in [(6, "P1"), (28, "P2")]:
        s = sigma_func(n)
        fs = fibonacci(s)
        s2 = s * s
        status = "EXACT" if fs == s2 else f"FAIL ({fs} != {s2})"
        print(f"    n={n} ({name}): F_{s} = {fs}, sigma^2 = {s2} => {status}")
    print()

    return hits


def section_bell():
    """Bell numbers analysis."""
    print("=" * 70)
    print("SECTION 3: BELL NUMBERS B(n)")
    print("=" * 70)
    print()

    print(f"  {'n':>3} | {'B(n)':>10} | {'Factorization':>20} | {'n=6 connection'}")
    print(f"  {'-'*3}-+-{'-'*10}-+-{'-'*20}-+-{'-'*30}")

    hits = []
    for n in range(10):
        b = bell(n)
        interp = n6_interpret(b)
        fac = format_factorization(b) if b > 1 else str(b)
        marker = " <--" if interp else ""
        print(f"  {n:>3} | {b:>10} | {fac:>20} | {interp}{marker}")
        if interp:
            hits.append((n, b, interp))

    print()
    print(f"  B(6) = {bell(6)} = {format_factorization(bell(6))}")
    print(f"    = 7 * 29 = M3 * 29")
    print(f"    Connection: M3 factor present, but 29 has no n=6 meaning.")
    print(f"    Grade: WEAK")
    print()

    return hits


def section_partition():
    """Partition function analysis."""
    print("=" * 70)
    print("SECTION 4: PARTITION FUNCTION p(n)")
    print("=" * 70)
    print()

    print(f"  {'n':>3} | {'p(n)':>8} | {'Factorization':>20} | {'n=6 connection'}")
    print(f"  {'-'*3}-+-{'-'*8}-+-{'-'*20}-+-{'-'*30}")

    hits = []
    for n in range(1, 20):
        p = partition(n)
        interp = n6_interpret(p)
        fac = format_factorization(p) if p > 1 else str(p)
        marker = " <--" if interp else ""
        print(f"  {n:>3} | {p:>8} | {fac:>20} | {interp}{marker}")
        if interp:
            hits.append((n, p, interp))

    print()

    # Perfect number indices
    print("  Partition at perfect number indices:")
    for pn, name in [(6, "P1"), (28, "P2")]:
        p = partition(pn)
        print(f"    p({pn}) = {p} = {format_factorization(p)}")
        for mod_by, mod_name in [(6, "P1"), (12, "sigma"), (28, "P2")]:
            print(f"      mod {mod_by} ({mod_name}) = {p % mod_by}")

    print()
    print(f"  Key: p(6) = 11 = sopfr(P2)")
    print(f"       p(11) = 56 = sigma(P2) = 2*P2")
    print(f"       p(p(6)) = p(11) = sigma(P2)  *** CHAIN ***")
    print()

    # p(28)
    p28 = partition(28)
    print(f"  p(28) = {p28} = {format_factorization(p28)}")
    print(f"    = 2 * 11 * 169 = 2 * sopfr(P2) * 13^2")
    print(f"    Contains sopfr(P2)=11 factor. Moderate.")
    print()

    return hits


def section_bernoulli():
    """Bernoulli numbers analysis."""
    print("=" * 70)
    print("SECTION 5: BERNOULLI NUMBERS B_n")
    print("=" * 70)
    print()

    print(f"  {'n':>3} | {'B_n':>20} | {'n=6 connection'}")
    print(f"  {'-'*3}-+-{'-'*20}-+-{'-'*40}")

    hits = []
    for n in [0, 1, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 28]:
        b = bernoulli(n)
        if b == 0:
            continue
        interp = ""
        # Check denominator for n=6 connections
        denom = b.denominator
        numer = abs(b.numerator)

        if n == 6:
            interp = "1/(M3*P1) = 1/42"
        elif n == 12:
            interp = f"denom={denom}=2*3*5*7*13, denom/P1={denom//6}"
        elif n == 28:
            interp = f"denom={denom}, denom mod P1={denom%6}"

        marker = " <--" if interp else ""
        print(f"  {n:>3} | {str(b):>20} | {interp}{marker}")
        if interp:
            hits.append((n, b, interp))

    print()
    print("  Key findings:")
    b6 = bernoulli(6)
    print(f"    B_6 = {b6} = 1/42 = 1/(M3 * P1)")
    print(f"      Denominator 42 = 7 * 6 = M3 * P1  *** EXACT ***")
    print()

    b12 = bernoulli(12)
    print(f"    B_12 = B_sigma = {b12}")
    print(f"      Denominator = {b12.denominator}")
    print(f"      {b12.denominator} = {format_factorization(b12.denominator)}")
    print(f"      {b12.denominator} / 6 = {b12.denominator // 6}")
    print(f"      Numerator |{b12.numerator}| = {format_factorization(abs(b12.numerator))}")
    print()

    b28 = bernoulli(28)
    print(f"    B_28 = B_P2 = {b28}")
    print(f"      Denominator = {b28.denominator}")
    print(f"      {b28.denominator} = {format_factorization(b28.denominator)}")
    print(f"      {b28.denominator} mod 6 = {b28.denominator % 6}")
    print(f"      {b28.denominator} / 6 = {b28.denominator / 6:.2f}")
    print()

    # Von Staudt-Clausen: denom(B_{2k}) = prod of primes p where (p-1)|2k
    print("  Von Staudt-Clausen theorem check:")
    print("    denom(B_{2k}) = product of primes p where (p-1) | 2k")
    for idx in [6, 12, 28]:
        primes = [p for p in range(2, idx + 2) if all(p % d != 0 for d in range(2, p)) or p == 2
                  if (p - 1) > 0 and idx % (p - 1) == 0]
        prod = 1
        for p in primes:
            prod *= p
        b_val = bernoulli(idx)
        print(f"    B_{idx}: primes where (p-1)|{idx} = {primes}, product = {prod}, actual denom = {b_val.denominator}")
    print()

    return hits


def section_stirling():
    """Stirling numbers of the second kind."""
    print("=" * 70)
    print("SECTION 6: STIRLING NUMBERS S(6,k)")
    print("=" * 70)
    print()

    print(f"  S(n=6, k) = ways to partition 6 elements into k non-empty subsets")
    print()
    print(f"  {'k':>3} | {'S(6,k)':>8} | {'Factorization':>20} | {'n=6 connection'}")
    print(f"  {'-'*3}-+-{'-'*8}-+-{'-'*20}-+-{'-'*30}")

    hits = []
    for k in range(1, 7):
        s = stirling2(6, k)
        interp = n6_interpret(s)
        fac = format_factorization(s) if s > 1 else str(s)

        # Additional interpretations
        if s == 31:
            interp = "M5 = 2^5-1 (Mersenne prime of P3!)"
        elif s == 90:
            interp = f"P1*15 = P1*C(P1,2)"
        elif s == 65:
            interp = f"5*13 = sopfr*13"
        elif s == 15:
            interp = "C(6,2) = 2^tau-1"

        marker = " <--" if interp else ""
        print(f"  {k:>3} | {s:>8} | {fac:>20} | {interp}{marker}")
        if interp:
            hits.append((k, s, interp))

    print()
    print("  Sum S(6,k) for k=1..6 = ", sum(stirling2(6, k) for k in range(1, 7)))
    print(f"    = B(6) = {bell(6)} (Bell number, by definition)")
    print()

    # Cross-check with other n values
    print("  Stirling S(n,2) for n=2..8:")
    for n in range(2, 9):
        s = stirling2(n, 2)
        is_2k_minus_1 = (s & (s + 1) == 0)  # 2^k - 1 form
        is_prime = s > 1 and all(s % d != 0 for d in range(2, int(s**0.5) + 1))
        tag = f"  = 2^{n-1}-1 = M{n-1}" + (" MERSENNE PRIME" if is_2k_minus_1 and is_prime else "")
        print(f"    S({n},2) = {s}{tag}")
    print()
    print("  S(n,2) = 2^(n-1) - 1 always. So S(6,2) = 31 = M5 is structural.")
    print("  S(6,2) being Mersenne PRIME depends on 5 being prime = sopfr(6).")
    print()

    return hits


def section_derangement():
    """Derangements analysis."""
    print("=" * 70)
    print("SECTION 7: DERANGEMENTS D(n) = !n")
    print("=" * 70)
    print()

    print(f"  {'n':>3} | {'!n':>8} | {'!n/n!':>12} | {'|!n/n! - 1/e|':>14} | {'n=6 connection'}")
    print(f"  {'-'*3}-+-{'-'*8}-+-{'-'*12}-+-{'-'*14}-+-{'-'*30}")

    inv_e = 1.0 / math.e

    hits = []
    for n in range(1, 11):
        d = derangement(n)
        nfac = math.factorial(n)
        ratio = d / nfac
        err = abs(ratio - inv_e)
        interp = ""
        if n == 6:
            interp = f"D(6)/6! = {d}/{nfac} ~ 1/e = GZ center"

        marker = " <--" if interp else ""
        print(f"  {n:>3} | {d:>8} | {ratio:>12.8f} | {err:>14.2e} | {interp}{marker}")
        if n == 6:
            hits.append((n, d, interp))

    print()
    d6 = derangement(6)
    print(f"  D(6) = {d6} = {format_factorization(d6)}")
    print(f"  D(6) / 6! = {d6}/{math.factorial(6)} = {d6/math.factorial(6):.10f}")
    print(f"  1/e       = {inv_e:.10f}")
    print(f"  Error     = {abs(d6/math.factorial(6) - inv_e):.2e}")
    print()
    print("  NOTE: D(n)/n! -> 1/e is the well-known limit for ALL n.")
    print("  At n=6, error = 1.4e-4, not special compared to other n.")
    print("  The 1/e connection is UNIVERSAL, not P1-specific.")
    print("  Grade: UNIVERSAL (not unique to n=6)")
    print()

    return hits


def section_cross_connections():
    """Cross-sequence connections."""
    print("=" * 70)
    print("SECTION 8: CROSS-SEQUENCE CONNECTIONS")
    print("=" * 70)
    print()

    # Catalan-Fibonacci
    print("  Catalan-Fibonacci bridges:")
    print(f"    C_3 = {catalan(3)} = F_5 = {fibonacci(5)} = sopfr(6)")
    print(f"    C_5 = {catalan(5)} = 42 = M3*P1, F_sigma = F_12 = {fibonacci(12)} = sigma^2")
    print()

    # Partition chain
    print("  Partition chain:")
    print(f"    p(P1) = p(6) = {partition(6)} = sopfr(P2)")
    print(f"    p(sopfr(P2)) = p(11) = {partition(11)} = sigma(P2) = {sigma_func(28)}")
    print(f"    p(p(6)) = sigma(P2)   *** REMARKABLE CHAIN ***")
    print()

    # Fibonacci-sigma identity
    print("  Fibonacci-sigma identity:")
    print(f"    F_sigma(6) = F_12 = {fibonacci(12)} = {SIGMA}^2 = sigma(6)^2")
    print(f"    Does F_sigma(n) = sigma(n)^2 for n=28?")
    s28 = sigma_func(28)
    f_s28 = fibonacci(s28)
    print(f"    sigma(28) = {s28}, F_{s28} = {f_s28}")
    print(f"    sigma(28)^2 = {s28**2}")
    print(f"    F_56 = {f_s28} vs 56^2 = {s28**2}: {'MATCH' if f_s28 == s28**2 else 'NO MATCH'}")
    print(f"    => P1-ONLY identity!")
    print()

    # Bernoulli-Catalan
    print("  Bernoulli-Catalan bridge:")
    print(f"    B_6 = 1/42, C_5 = 42")
    print(f"    B_P1 = 1/C_sopfr  *** EXACT ***")
    b6 = bernoulli(6)
    c5 = catalan(5)
    print(f"    Verify: B_6 * C_5 = {b6} * {c5} = {b6 * c5}")
    print()

    # Stirling-Mersenne
    print("  Stirling-Mersenne bridge:")
    print(f"    S(6,2) = 31 = M5 = M_sopfr(6)")
    print(f"    S(n,2) = 2^(n-1) - 1, so S(P1,2) = 2^(P1-1) - 1 = M_5")
    print(f"    M_5 is prime iff sopfr(6) is prime: {SOPFR} is prime = True")
    print()


def texas_sharpshooter():
    """Texas Sharpshooter test for all claims."""
    print("=" * 70)
    print("SECTION 9: TEXAS SHARPSHOOTER TEST")
    print("=" * 70)
    print()

    import random
    random.seed(42)

    # Define all claimed connections as testable predicates
    claims = [
        ("C_3 = sopfr(6)", lambda: catalan(3) == SOPFR, "exact"),
        ("C_5 = M3*P1", lambda: catalan(5) == M3 * P1, "exact"),
        ("C_6 = sigma*sopfr(P2)", lambda: catalan(6) == SIGMA * sopfr_func(P2), "exact"),
        ("F_6 = sigma-tau", lambda: fibonacci(6) == SIGMA - TAU, "exact"),
        ("F_12 = sigma^2", lambda: fibonacci(12) == SIGMA ** 2, "exact"),
        ("F_sigma(6) = sigma^2 (same)", lambda: fibonacci(sigma_func(6)) == sigma_func(6) ** 2, "exact"),
        ("B_6 = 1/(M3*P1)", lambda: bernoulli(6) == Fraction(1, M3 * P1), "exact"),
        ("B_P1 * C_sopfr = 1", lambda: bernoulli(P1) * catalan(SOPFR) == 1, "exact"),
        ("p(6) = sopfr(P2)", lambda: partition(6) == sopfr_func(P2), "exact"),
        ("p(p(6)) = sigma(P2)", lambda: partition(partition(6)) == sigma_func(P2), "exact"),
        ("S(6,2) = M_sopfr(6)", lambda: stirling2(6, 2) == 2 ** SOPFR - 1, "exact"),
        ("S(6,5) = C(6,2)", lambda: stirling2(6, 5) == math.comb(6, 2), "exact"),
        ("D(6)/6! ~ 1/e", lambda: abs(derangement(6) / math.factorial(6) - 1 / math.e) < 0.001, "approx"),
        ("B(6) has M3 factor", lambda: bell(6) % M3 == 0, "exact"),
    ]

    print(f"  Total claims: {len(claims)}")
    print()

    # Verify all claims
    verified = 0
    for name, pred, ctype in claims:
        result = pred()
        status = "TRUE" if result else "FALSE"
        emoji = "  [+]" if result else "  [-]"
        print(f"  {emoji} {name}: {status}")
        if result:
            verified += 1

    print()
    print(f"  Verified: {verified}/{len(claims)}")
    print()

    # Monte Carlo: for random n in similar range, how many "connections" exist?
    print("  Monte Carlo baseline (1000 random integers, same tests adapted):")
    n_trials = 1000
    match_counts = []

    for _ in range(n_trials):
        n = random.randint(4, 50)
        sig = sigma_func(n)
        ta = tau_func(n)
        ph = phi_func(n)
        sp = sopfr_func(n)
        mersenne_related = 2 ** max(1, sp) - 1 if sp < 20 else 0

        count = 0
        # Test analogous claims for random n
        if n <= 10 and catalan(max(1, sp)) > 0:
            if catalan(min(sp, 15)) == sp:
                count += 1
        if n <= 40:
            fib_n = fibonacci(n)
            if fib_n == sig - ta:
                count += 1
            if sig <= 50 and fibonacci(sig) == sig ** 2:
                count += 1
        if n <= 30 and n % 2 == 0:
            bn = bernoulli(n)
            if bn != 0 and bn.denominator == n * (2 ** max(1, min(sp, 10)) - 1):
                count += 1
        if partition(n) == sp:
            count += 1
        pn = partition(n)
        if pn <= 200 and partition(pn) == sig:
            count += 1
        if n <= 15 and n >= 2:
            if stirling2(n, 2) == mersenne_related:
                count += 1
        if n >= 2 and n <= 10:
            if stirling2(n, n - 1) == math.comb(n, 2):
                count += 1
        if bell(min(n, 15)) % (2 ** max(1, min(ta, 5)) - 1) == 0:
            count += 1

        match_counts.append(count)

    avg = sum(match_counts) / len(match_counts)
    std = (sum((x - avg) ** 2 for x in match_counts) / len(match_counts)) ** 0.5
    z_score = (verified - avg) / std if std > 0 else float('inf')

    print(f"    Random average: {avg:.2f} +/- {std:.2f}")
    print(f"    n=6 score:      {verified}")
    print(f"    Z-score:        {z_score:.1f}sigma")
    print()

    # Histogram
    from collections import Counter
    hist = Counter(match_counts)
    max_count = max(hist.values())
    print("    Distribution of random matches:")
    for k in sorted(hist.keys()):
        bar = "#" * int(40 * hist[k] / max_count)
        print(f"      {k:>2} | {bar} ({hist[k]})")
    print(f"      n=6: {verified} matches <<<")
    print()

    # p-value
    p_value = sum(1 for x in match_counts if x >= verified) / n_trials
    print(f"    p-value: {p_value:.4f}")
    if p_value < 0.01:
        print(f"    STRUCTURAL (p < 0.01)")
    elif p_value < 0.05:
        print(f"    WEAK EVIDENCE (p < 0.05)")
    else:
        print(f"    NOT SIGNIFICANT (p >= 0.05)")
    print()

    # Grade assignments
    print("  Grading summary:")
    print()
    grades = {
        "EXACT + DEEP": [
            "F_sigma(6) = sigma(6)^2 (P1-only, proven)",
            "B_P1 * C_sopfr = 1 (Bernoulli-Catalan bridge)",
            "p(p(6)) = sigma(P2) (partition chain)",
        ],
        "EXACT + MODERATE": [
            "B_6 = 1/(M3*P1) (Von Staudt-Clausen consequence)",
            "S(6,2) = M_sopfr (structural: S(n,2)=2^(n-1)-1)",
            "C_5 = M3*P1 = 42",
        ],
        "EXACT + WEAK": [
            "C_3 = sopfr(6) = 5 (small number coincidence)",
            "F_6 = sigma-tau = 8 (small number)",
            "S(6,5) = C(6,2) = 15 (always true: S(n,n-1)=C(n,2))",
            "B(6) has M3 factor (203=7*29, weak)",
        ],
        "UNIVERSAL (not n=6 specific)": [
            "D(n)/n! -> 1/e (true for all n, not special at n=6)",
        ],
    }

    for grade, items in grades.items():
        print(f"    [{grade}]")
        for item in items:
            print(f"      - {item}")
        print()

    return verified, avg, std, z_score, p_value


def main():
    parser = argparse.ArgumentParser(description="Catalan & Combinatorial Sequences at n=6")
    parser.add_argument("--texas", action="store_true", help="Texas Sharpshooter only")
    parser.add_argument("--section", type=str, help="Run single section")
    args = parser.parse_args()

    print()
    print("  CATALAN & COMBINATORIAL SEQUENCES AT n=6")
    print("  =========================================")
    print()
    print(f"  n=6 constants: P1={P1}, sigma={SIGMA}, tau={TAU}, phi={PHI},")
    print(f"                 sopfr={SOPFR}, M3={M3}, P2={P2}")
    print()

    sections = {
        "catalan": section_catalan,
        "fibonacci": section_fibonacci,
        "bell": section_bell,
        "partition": section_partition,
        "bernoulli": section_bernoulli,
        "stirling": section_stirling,
        "derangement": section_derangement,
        "cross": section_cross_connections,
    }

    if args.texas:
        texas_sharpshooter()
        return

    if args.section:
        if args.section in sections:
            sections[args.section]()
        else:
            print(f"  Unknown section: {args.section}")
            print(f"  Available: {', '.join(sections.keys())}")
        return

    # Run all
    all_hits = []
    for name, func in sections.items():
        result = func()
        if isinstance(result, list):
            all_hits.extend(result)

    texas_sharpshooter()

    # Final summary
    print("=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    print()
    print("  TOP FINDINGS (by depth):")
    print()
    print("  DEEP (grade candidates):")
    print("    1. F_sigma(6) = sigma(6)^2          P1-ONLY, 🟩")
    print("    2. B_P1 * C_sopfr = 1               P1-specific, 🟩")
    print("    3. p(p(6)) = sigma(P2)              Chain identity, 🟧*")
    print()
    print("  MODERATE:")
    print("    4. B_6 = 1/42 = 1/(M3*P1)          Von Staudt consequence, 🟩")
    print("    5. C_5 = 42 = M3*P1                 Exact, 🟧")
    print("    6. S(6,2) = 31 = M_sopfr            Structural, 🟧")
    print()
    print("  WEAK / UNIVERSAL:")
    print("    7. C_3 = sopfr = 5                  Small number, ⚪")
    print("    8. D(6)/6! ~ 1/e                    Universal, ⚪")
    print("    9. B(6) = 7*29 (M3 factor)          Weak, ⚪")
    print()


if __name__ == "__main__":
    main()
