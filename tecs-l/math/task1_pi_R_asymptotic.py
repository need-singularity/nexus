"""
Task 1: Rigorous asymptotic for π_R(x)
π_R(x) = number of distinct R(n) values ≤ x
where R(n) = σ(n)φ(n)/(n·τ(n))

R is multiplicative: R(p^a) = (p^(a+1)-1)(p^a - p^(a-1)) / (p^a · (a+1) · (p-1)^... )
More precisely: R(p^a) = σ(p^a)·φ(p^a) / (p^a · τ(p^a))
  σ(p^a) = (p^(a+1)-1)/(p-1)
  φ(p^a) = p^a - p^(a-1) = p^(a-1)(p-1)
  τ(p^a) = a+1
  So R(p^a) = [(p^(a+1)-1)/(p-1)] · [p^(a-1)(p-1)] / [p^a · (a+1)]
            = (p^(a+1)-1) · p^(a-1) / (p^a · (a+1))
            = (p^(a+1)-1) / (p · (a+1))

Special case: R(p) = (p^2-1)/(2p) = (p-1)(p+1)/(2p)
"""

import math
from fractions import Fraction
from collections import defaultdict
import numpy as np

def R_prime_power(p, a):
    """R(p^a) = (p^(a+1) - 1) / (p * (a+1))"""
    return Fraction(p**(a+1) - 1, p * (a+1))

def compute_R(n):
    """Compute R(n) = σ(n)·φ(n)/(n·τ(n)) as a Fraction."""
    if n == 1:
        return Fraction(1)

    # Factor n
    factors = {}
    temp = n
    d = 2
    while d * d <= temp:
        while temp % d == 0:
            factors[d] = factors.get(d, 0) + 1
            temp //= d
        d += 1
    if temp > 1:
        factors[temp] = factors.get(temp, 0) + 1

    # R is multiplicative
    result = Fraction(1)
    for p, a in factors.items():
        result *= R_prime_power(p, a)
    return result

def sieve_primes(limit):
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, limit+1, i):
                is_prime[j] = False
    return [i for i in range(2, limit+1) if is_prime[i]]

def compute_pi_R(X_max, n_max=50000):
    """Compute π_R(x) for x up to X_max by computing R(n) for n up to n_max."""
    print(f"Computing R(n) for n=1..{n_max}, counting distinct values ≤ {X_max}")

    distinct_R_values = set()

    for n in range(1, n_max + 1):
        r = compute_R(n)
        if r <= X_max:
            distinct_R_values.add(r)
        if n % 10000 == 0:
            print(f"  n={n}, distinct R values ≤ {X_max}: {len(distinct_R_values)}")

    return distinct_R_values

def analyze_asymptotic():
    """Compute π_R(x) at various x values and fit asymptotic."""
    print("="*60)
    print("TASK 1: π_R(x) ASYMPTOTIC ANALYSIS")
    print("="*60)

    # First compute all R(n) for n up to 50000
    n_max = 50000
    print(f"\nComputing R(n) for n=1..{n_max}...")

    # Store R values by magnitude
    r_values = []
    for n in range(1, n_max + 1):
        r = compute_R(n)
        r_values.append(float(r))

    print(f"R(n) range: [{min(r_values):.4f}, {max(r_values):.4f}]")

    # x values to test
    x_test = [10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000]

    print("\n" + "-"*70)
    print(f"{'x':>8} {'π_R(x)':>10} {'x·√ln(x)':>12} {'ratio':>10} {'x/ln(x)':>10} {'ratio2':>8}")
    print("-"*70)

    results = []
    for x in x_test:
        # Count distinct R values ≤ x
        distinct = set()
        for n in range(1, n_max + 1):
            if r_values[n-1] <= x:
                # Need exact value for distinctness
                pass

        # Use exact fractions for small x
        distinct_exact = set()
        for n in range(1, n_max + 1):
            if r_values[n-1] <= x + 0.001:  # small buffer for float
                r_exact = compute_R(n)
                if r_exact <= x:
                    distinct_exact.add(r_exact)

        pi_x = len(distinct_exact)

        if x > 1:
            lnx = math.log(x)
            x_sqrtlnx = x * math.sqrt(lnx)
            ratio = pi_x / x_sqrtlnx if x_sqrtlnx > 0 else 0
            x_over_lnx = x / lnx
            ratio2 = pi_x / x_over_lnx if x_over_lnx > 0 else 0
        else:
            lnx = 0
            x_sqrtlnx = 0
            ratio = 0
            x_over_lnx = 0
            ratio2 = 0

        results.append((x, pi_x, ratio, ratio2))
        print(f"{x:>8} {pi_x:>10} {x_sqrtlnx:>12.2f} {ratio:>10.4f} {x_over_lnx:>10.2f} {ratio2:>8.4f}")

    print("-"*70)

    # Also try x/(ln x)^(3/2)
    print("\n" + "-"*50)
    print(f"{'x':>8} {'π_R(x)':>10} {'x/(ln x)^1.5':>14} {'ratio':>10}")
    print("-"*50)
    for x, pi_x, _, _ in results:
        if x > 1:
            lnx = math.log(x)
            denom = x / lnx**1.5
            r = pi_x / denom if denom > 0 else 0
            print(f"{x:>8} {pi_x:>10} {denom:>14.2f} {r:>10.4f}")
    print("-"*50)

    return results

def prime_contribution_analysis():
    """Analyze contribution of primes to π_R(x)."""
    print("\n" + "="*60)
    print("PRIME CONTRIBUTION ANALYSIS")
    print("="*60)

    primes = sieve_primes(2000)

    print("\nR(p) = (p²-1)/(2p) values for small primes:")
    print(f"{'p':>6} {'R(p) exact':>20} {'R(p) float':>12} {'p/2':>8}")
    for p in primes[:20]:
        rp = Fraction(p*p - 1, 2*p)
        print(f"{p:>6} {str(rp):>20} {float(rp):>12.4f} {p/2:>8.4f}")

    # For π_R(x) from primes only: count primes p with R(p) ≤ x
    # R(p) = (p²-1)/(2p) ≈ p/2 - 1/(2p)
    # So R(p) ≤ x iff p ≤ 2x + 1/(p) ≈ 2x
    # Number of such primes ~ π(2x) ~ 2x/ln(2x)

    print("\nPrime-only π_R(x) vs full π_R(x):")
    print("R(p) ≤ x iff p ≈ 2x (since R(p) ~ p/2)")
    print(f"\n{'x':>8} {'primes with R(p)≤x':>20} {'π(2x)':>10} {'2x/ln(2x)':>12}")
    print("-"*55)

    x_vals = [10, 50, 100, 500, 1000, 5000, 10000, 50000]
    for x in x_vals:
        count = sum(1 for p in primes if Fraction(p*p-1, 2*p) <= x)
        pi_2x = sum(1 for p in primes if p <= 2*x)
        asymp = 2*x / math.log(2*x) if x > 0 else 0
        print(f"{x:>8} {count:>20} {pi_2x:>10} {asymp:>12.2f}")

def squarefree_R_analysis():
    """Analyze squarefree numbers and their R values."""
    print("\n" + "="*60)
    print("SQUAREFREE ANALYSIS")
    print("="*60)

    # R is multiplicative, so for squarefree n = p1*p2*...*pk:
    # R(n) = R(p1) * R(p2) * ... * R(pk)
    # R(pi) = (pi²-1)/(2pi) = (pi-1)(pi+1)/(2pi)

    # The distinct R values include:
    # 1. R(1) = 1
    # 2. R(p) for primes p
    # 3. R(p*q) = R(p)*R(q) for primes p < q
    # 4. R(p^2) = (p^3-1)/(3p) for primes p
    # etc.

    primes = sieve_primes(200)

    print("\nSquarefree 2-prime products R(pq):")
    print(f"{'p':>4} {'q':>4} {'R(p)':>12} {'R(q)':>12} {'R(pq)':>12} {'float':>10}")
    for i, p in enumerate(primes[:8]):
        for q in primes[i+1:i+5]:
            rp = Fraction(p*p-1, 2*p)
            rq = Fraction(q*q-1, 2*q)
            rpq = rp * rq
            print(f"{p:>4} {q:>4} {str(rp):>12} {str(rq):>12} {str(rpq):>12} {float(rpq):>10.4f}")

    # Count distinct R values by type
    print("\n\nR values by type (n ≤ 1000):")
    by_type = defaultdict(list)
    for n in range(1, 1001):
        r = compute_R(n)
        # Determine type
        temp = n
        factors = {}
        d = 2
        while d*d <= temp:
            while temp % d == 0:
                factors[d] = factors.get(d, 0) + 1
                temp //= d
            d += 1
        if temp > 1:
            factors[temp] = 1

        omega = len(factors)
        max_exp = max(factors.values()) if factors else 0
        if n == 1:
            t = "n=1"
        elif max_exp == 1:
            t = f"squarefree-{omega}"
        else:
            t = f"non-squarefree"

        by_type[t].append(float(r))

    for t in sorted(by_type.keys()):
        vals = by_type[t]
        print(f"  {t}: {len(vals)} values, range [{min(vals):.3f}, {max(vals):.3f}]")

def dickman_connection():
    """Explore connection to Dickman's function."""
    print("\n" + "="*60)
    print("DICKMAN FUNCTION CONNECTION")
    print("="*60)

    print("""
Heuristic analysis for π_R(x):

The R values come from:
  - Primes p: R(p) = (p²-1)/(2p) ~ p/2
  - Prime powers p^a: R(p^a) = (p^(a+1)-1)/(p(a+1))
  - Composites: R(n) = ∏ R(p_i^{a_i})

Key observation: R(p) ≈ p/2, so distinct prime-R values
up to x come from primes p ≤ 2x.

For squarefree products R(∏p_i) = ∏R(p_i) ≤ x:
  This is counting "R-smooth" factorizations.

The dominant contribution: primes with R(p) ≤ x
  Count ~ π(2x) ~ 2x/ln(x)

Second contribution: products R(p)R(q) ≤ x, p < q
  For each prime p, count q with R(q) ≤ x/R(p) ≈ 2x/p
  ~ π(2x/p) for each p, summed over primes p ≤ 2x^{1/2}
  ~ ∑_{p ≤ √(2x)} (2x/p)/ln(2x/p)
  ~ (2x/ln x) ∑_{p ≤ √(2x)} 1/p
  ~ (2x/ln x) · (1/2)ln ln(2x)    [Mertens theorem]
  ~ x·ln ln(x) / ln(x)

So prime pairs contribute x·ln ln(x)/ln(x),
which is smaller than x/√(ln x) asymptotically.

The empirical π_R(x) ~ C·x·√(ln x) suggests a different dominant term.
Let's check if the growth is from prime-power R-values overlapping with
or creating a richer structure than pure prime sums.
""")

def main():
    print("TASK 1: π_R(x) ASYMPTOTIC ANALYSIS")
    print("="*60)

    analyze_asymptotic()
    prime_contribution_analysis()
    squarefree_R_analysis()
    dickman_connection()

    # Final summary of empirical fit
    print("\n" + "="*60)
    print("EMPIRICAL FIT SUMMARY")
    print("="*60)
    print("""
Based on computation:
  π_R(x) = number of distinct R(n) values ≤ x

Tested forms:
  1. C·x·√(ln x)     - empirically ratio → ~4.3 (claimed)
  2. C·x/ln(x)       - from prime counting alone
  3. C·x/(ln x)^1.5  - intermediate

The prime contribution alone gives O(x/ln x),
but composite R values (products) fill in many more values,
potentially giving the √(ln x) enhancement.

This resembles the count of smooth numbers or
numbers representable as products from a specific set.
""")

if __name__ == "__main__":
    main()
