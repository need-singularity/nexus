"""
Task 1: FAST asymptotic investigation for π_R(x)

Key insight: R values are rational numbers.
To count distinct ones ≤ x, we use floats with high precision,
but we need to be careful about equality detection.

R(p) = (p²-1)/(2p) = p/2 - 1/(2p)
These are all distinct since they're strictly increasing in p.

R(p)R(q) = (p²-1)(q²-1)/(4pq)
Are these distinct? We need to check for collisions.

Strategy: Use a fast DFS with float hashing, then validate with exact arithmetic.
"""

import math
from fractions import Fraction

def sieve_primes(limit):
    is_prime = bytearray([1]) * (limit + 1)
    is_prime[0] = is_prime[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            is_prime[i*i::i] = bytearray(len(is_prime[i*i::i]))
    return [i for i in range(2, limit+1) if is_prime[i]]

def r_prime(p):
    """R(p) as a fraction."""
    return Fraction(p*p - 1, 2*p)

def r_prime_power(p, a):
    """R(p^a) as a fraction."""
    return Fraction(p**(a+1) - 1, p * (a+1))

def count_distinct_R_values(x_max, primes):
    """
    Count distinct R values ≤ x_max using exact arithmetic.
    R values are products ∏ R(p_i^{a_i}) where p_i are distinct primes.

    Strategy: BFS/DFS building products.
    Key: we iterate over prime index (in sorted order of R(p))
    and build all valid products.
    """
    x_frac = Fraction(x_max)

    # Get all prime R-values ≤ x
    prime_r = []
    for p in primes:
        rp = r_prime(p)
        if rp > x_frac:
            break
        prime_r.append((p, rp))

    # Get all prime-power R-values (a ≥ 2) ≤ x
    # R(p^2) = (p^3-1)/(3p) ~ p^2/3
    # R(p^3) = (p^4-1)/(4p) ~ p^3/4
    # These are much smaller than R(p) for same "size" prime
    power_r = []  # list of (p, a, r_value)
    for p in primes:
        for a in range(2, 40):
            rpa = r_prime_power(p, a)
            if rpa > x_frac:
                break
            power_r.append((p, a, rpa))
        if r_prime_power(p, 2) > x_frac:
            break

    n_prime = len(prime_r)
    # Each prime can appear ONCE (either as p^1, p^2, p^3, etc.)
    # The "choices" for prime p are: not used, used as p^1, p^2, p^3...

    # Build all possible R values by combining prime contributions
    # Using DFS: at each step, decide what to do with next prime

    # Build a list: for each prime index i, the possible R-contributions
    prime_choices = {}
    for p, rp in prime_r:
        choices = [rp]  # a=1
        for a in range(2, 40):
            rpa = r_prime_power(p, a)
            if rpa > x_frac:
                break
            choices.append(rpa)
        prime_choices[p] = choices

    # DFS
    distinct_values = set()
    distinct_values.add(Fraction(1))  # n=1

    def dfs(idx, current_product):
        """Add current_product and all extensions."""
        distinct_values.add(current_product)
        for i in range(idx, n_prime):
            p, rp = prime_r[i]
            # Try each power of p
            for choice in prime_choices[p]:
                new_product = current_product * choice
                if new_product > x_frac:
                    break  # choices are in increasing order within p
                dfs(i + 1, new_product)

    dfs(0, Fraction(1))

    return len(distinct_values)

def main():
    print("="*70)
    print("TASK 1: FAST EXACT ASYMPTOTIC ANALYSIS v4")
    print("="*70)

    print("Sieving primes up to 2,000,000...")
    primes = sieve_primes(2000000)
    print(f"Found {len(primes)} primes")

    x_vals = [100, 500, 1000, 5000, 10000, 50000, 100000, 500000, 1000000]

    print(f"\n{'x':>10} {'π_R(x)':>12} {'π(2x)':>8} {'ratio π_R/π(2x)':>18} {'π_R·lnx/x':>12}")
    print("-"*65)

    data = []
    for x in x_vals:
        pi_x = count_distinct_R_values(x, primes)
        pi_2x = sum(1 for p in primes if p <= 2*x)
        ratio = pi_x / pi_2x if pi_2x > 0 else 0
        lnx = math.log(x)
        r2 = pi_x * lnx / x
        data.append((x, pi_x, pi_2x))
        print(f"{x:>10} {pi_x:>12} {pi_2x:>8} {ratio:>18.4f} {r2:>12.4f}")

    print("\nLog-log regression:")
    log_x = [math.log(x) for x, _, _ in data]
    log_pi = [math.log(pi) for _, pi, _ in data]

    n = len(log_x)
    sx = sum(log_x)
    sy = sum(log_pi)
    sxy = sum(log_x[i]*log_pi[i] for i in range(n))
    sx2 = sum(log_x[i]**2 for i in range(n))

    slope = (n*sxy - sx*sy) / (n*sx2 - sx**2)
    intercept = (sy - slope*sx) / n

    print(f"  π_R(x) ~ {math.exp(intercept):.4f} · x^{slope:.4f}")

    print("\nDetailed analysis:")
    print(f"{'x':>10} {'prime contrib':>14} {'composite contrib':>18} {'comp/prime ratio':>18}")
    print("-"*65)
    for x, pi_x, pi_2x in data:
        comp = pi_x - pi_2x
        ratio = comp / pi_2x if pi_2x > 0 else 0
        print(f"{x:>10} {pi_2x:>14} {comp:>18} {ratio:>18.4f}")

    print("\n\nIs composite contribution ~ C · x/ln(x)?")
    print(f"{'x':>10} {'composite':>12} {'x/ln(x)':>12} {'ratio':>10}")
    print("-"*50)
    for x, pi_x, pi_2x in data:
        comp = pi_x - pi_2x
        xlnx = x / math.log(x)
        ratio = comp / xlnx if xlnx > 0 else 0
        print(f"{x:>10} {comp:>12} {xlnx:>12.2f} {ratio:>10.4f}")

    print("\n\nBreakdown by number of prime factors in R(n):")
    # For x=10000, count by k-prime products
    x_test = 10000
    x_frac = Fraction(x_test)
    prime_r = [(p, Fraction(p*p-1, 2*p)) for p in primes if Fraction(p*p-1, 2*p) <= x_frac]

    by_k = {0: 1}  # k=0: just R(1)=1

    def count_by_k(idx, current, k):
        if current > x_frac:
            return
        by_k[k] = by_k.get(k, 0) + (1 if k > 0 else 0)

        for i in range(idx, len(prime_r)):
            p, rp = prime_r[i]
            new = current * rp
            if new > x_frac:
                break
            count_by_k(i+1, new, k+1)

    # This overcounts distinct values since collisions can happen
    # But gives structure
    count_by_k(0, Fraction(1), 0)

    # Instead, count exact distinct values by k
    by_k_distinct = {}
    all_by_k = {0: {Fraction(1)}}

    def dfs_by_k(idx, current, k):
        if k not in all_by_k:
            all_by_k[k] = set()
        all_by_k[k].add(current)
        for i in range(idx, len(prime_r)):
            p, rp = prime_r[i]
            new = current * rp
            if new > x_frac:
                break
            dfs_by_k(i+1, new, k+1)

    print(f"\nFor x={x_test}:")
    dfs_by_k(0, Fraction(1), 0)

    # Count distinct values per k (not double counting across k)
    already_seen = set()
    for k in sorted(all_by_k.keys()):
        new_in_k = all_by_k[k] - already_seen
        already_seen |= new_in_k
        print(f"  k={k}: {len(all_by_k[k])} products, {len(new_in_k)} new distinct values")

    print(f"  Total distinct: {len(already_seen)}")

if __name__ == "__main__":
    main()
