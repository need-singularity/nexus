"""
Task 1: RIGOROUS asymptotic investigation for π_R(x)

The refined script showed π_R(x) / (x/ln x) is still growing (11→33 over x=100→500000).
This means the leading term is NOT x/ln(x).

Let's examine what the true asymptotic is by:
1. Analyzing the growth rate of the ratio more carefully
2. Testing specific analytic forms
3. Understanding WHY composites contribute so much
"""

import math
from fractions import Fraction
from functools import lru_cache

def sieve_primes(limit):
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, limit+1, i):
                is_prime[j] = False
    return [i for i in range(2, limit+1) if is_prime[i]]

def compute_pi_R_recursive(x_max, primes, prime_r_vals):
    """
    Count distinct R values ≤ x_max.
    Use the structure: R values are products of R(p_i^{a_i}).
    """
    distinct = set()
    distinct.add(Fraction(1))

    # All R(p) ≤ x_max (from primes)
    prime_contributions = [(p, rp) for p, rp in prime_r_vals if rp <= x_max]
    for p, rp in prime_contributions:
        distinct.add(rp)

    # All R(p^a) ≤ x_max for a ≥ 2
    power_contributions = []
    for p in primes:
        for a in range(2, 30):
            rpa = Fraction(p**(a+1) - 1, p * (a+1))
            if rpa > x_max:
                break
            distinct.add(rpa)
            power_contributions.append((p, a, rpa))

    # Products: R(p1)*R(p2)*...*R(pk) * R(q1^a1)*... ≤ x_max
    # Build all combinations up to x_max using DFS/recursion

    all_base_vals = [(rp, 'prime', p) for p, rp in prime_contributions] + \
                    [(rpa, 'power', (p,a)) for p, a, rpa in power_contributions]
    all_base_vals.sort(key=lambda x: float(x[0]))

    # Use a BFS approach: start from 1 and multiply by each base value
    # but avoid reusing the same prime
    # R(n) = ∏ R(p^a) where different p are used

    # Key: all base values must use DIFFERENT primes
    # prime_r_vals: {p: r_value} mapping

    # Build by prime sets
    # For each subset S of primes + their exponents, compute product R
    # This is exponential in |S|, so we use a generating approach

    # Approach: iterate over "building" R values by adding one prime at a time
    # State: (current_product, set_of_primes_used)
    # This is essentially enumerating all R(n) values

    # For tractability, we generate R values by multiplying one factor at a time
    # Use a set to avoid duplicates

    # Start with {1} and expand
    current_set = {Fraction(1): set()}  # value -> set of primes used

    # Process primes in order
    for p, rp in prime_contributions:
        if rp > x_max:
            break
        new_entries = {}
        for val, primes_used in current_set.items():
            if p not in primes_used:  # Each prime can only be used once
                new_val = val * rp
                if new_val <= x_max:
                    existing = current_set.get(new_val, set()) | new_entries.get(new_val, set())
                    new_entries[new_val] = primes_used | {p}
        current_set.update(new_entries)

    # Now add prime powers (replacing R(p) with R(p^a))
    for p, a, rpa in power_contributions:
        # Replace the prime-only contribution of p with higher power
        new_entries = {}
        for val, primes_used in current_set.items():
            if p not in primes_used:  # p not yet used
                new_val = val * rpa
                if new_val <= x_max:
                    if new_val not in current_set and new_val not in new_entries:
                        new_entries[new_val] = primes_used | {p}
                    elif new_val in new_entries:
                        pass  # already found a way
        current_set.update(new_entries)

    return len(current_set)

def main():
    print("="*70)
    print("TASK 1: ASYMPTOTIC ANALYSIS v3 - EXACT COMPUTATION")
    print("="*70)

    # Pre-compute primes
    PRIME_LIMIT = 1100000  # 2x for x up to 500000
    print(f"Sieving primes up to {PRIME_LIMIT}...")
    primes = sieve_primes(PRIME_LIMIT)
    print(f"Found {len(primes)} primes")

    # Pre-compute R(p) values
    prime_r_vals = [(p, Fraction(p*p-1, 2*p)) for p in primes]

    x_vals = [100, 500, 1000, 5000, 10000, 50000, 100000, 500000, 1000000]

    print("\nComputing π_R(x) with exact prime product enumeration...")
    print(f"{'x':>10} {'π_R(x)':>12} {'ln ratio':>12}")
    print("-"*40)

    data = []
    for x in x_vals:
        pi_x = compute_pi_R_recursive(x, primes, prime_r_vals)
        if x > 1 and len(data) > 0:
            prev_x, prev_pi = data[-1]
            ln_ratio = math.log(pi_x / prev_pi) / math.log(x / prev_x)
        else:
            ln_ratio = 0
        data.append((x, pi_x))
        print(f"{x:>10} {pi_x:>12} {ln_ratio:>12.4f}")

    print("\nln π_R(x) vs ln x fit:")
    print("(slope should give the power law exponent)")
    import sys

    # Linear regression on log-log
    log_x = [math.log(x) for x, _ in data[2:]]  # skip first two
    log_pi = [math.log(pi) for _, pi in data[2:]]

    n = len(log_x)
    sum_x = sum(log_x)
    sum_y = sum(log_pi)
    sum_xy = sum(log_x[i]*log_pi[i] for i in range(n))
    sum_x2 = sum(log_x[i]**2 for i in range(n))

    slope = (n*sum_xy - sum_x*sum_y) / (n*sum_x2 - sum_x**2)
    intercept = (sum_y - slope*sum_x) / n

    print(f"  log π_R(x) = {slope:.4f} · log(x) + {intercept:.4f}")
    print(f"  π_R(x) ~ exp({intercept:.4f}) · x^{slope:.4f}")
    print(f"  C = exp({intercept:.4f}) = {math.exp(intercept):.4f}")

    print("\nTesting specific forms:")
    print(f"{'x':>10} {'π_R(x)':>12} {'π_R/π(2x)':>12} {'π_R·lnx/x':>14} {'π_R·ln²x/x':>14}")
    print("-"*65)

    for x, pi_x in data:
        pi_2x = sum(1 for p in primes if p <= 2*x)
        if x > 1:
            lnx = math.log(x)
            r1 = pi_x / pi_2x if pi_2x > 0 else 0
            r2 = pi_x * lnx / x
            r3 = pi_x * lnx**2 / x
            print(f"{x:>10} {pi_x:>12} {r1:>12.4f} {r2:>14.4f} {r3:>14.4f}")

    print("\n\nAnalysis of the ratio π_R(x) / π(2x):")
    print("π(2x) = # primes ≤ 2x = # primes p with R(p) ≤ x")
    print("This ratio = 1 + (fraction from composite R-values)")
    print()
    for x, pi_x in data:
        pi_2x = sum(1 for p in primes if p <= 2*x)
        frac = pi_x / pi_2x if pi_2x > 0 else 0
        print(f"  x={x:>8}: total={pi_x:>8}, from primes={pi_2x:>7}, ratio={frac:.4f}, composite R-values={pi_x-pi_2x}")

    print("\n\nHypothesis: π_R(x) ~ C · π(2x) for some C > 1?")
    print("If C is constant, then π_R(x) ~ C · 2x/ln(x)")
    print("But the ratio is growing, so C is not constant.")

    # Test if ratio grows like a power of log
    print("\nTesting: ratio = π_R(x)/π(2x) vs log forms:")
    print(f"{'x':>10} {'ratio':>8} {'ln ln x':>10} {'(ln x)^0.5':>12}")
    print("-"*45)
    for x, pi_x in data:
        pi_2x = sum(1 for p in primes if p <= 2*x)
        if pi_2x > 0 and x > 1:
            ratio = pi_x / pi_2x
            lnlnx = math.log(math.log(x))
            sqrtlnx = math.sqrt(math.log(x))
            print(f"{x:>10} {ratio:>8.4f} {lnlnx:>10.4f} {sqrtlnx:>12.4f}")

if __name__ == "__main__":
    main()
