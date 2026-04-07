"""
Fast exact π_R(x) computation.

Key: use tuples of (p, a) to represent R values uniquely,
with no Fraction arithmetic in the inner loop.
Only compute Fraction for the final product check.

Better: use log-sums for comparison, exact fractions only for equality.

Actually fastest: represent each distinct R-value by its numerator/denominator
stored as a frozenset of prime factors, and use a hashing set.
But this is complex.

SIMPLEST FAST APPROACH: Use float arithmetic with unique "fingerprint"
to hash into buckets, then verify exact equality within buckets.

Since R(p) = (p²-1)/(2p) = distinct rational for each prime p,
and products of distinct R(p) values are rarely equal to each other,
we can use log R values as approximate keys and check for collisions.

log R(p1...pk) = ∑ log R(pi)

Two products collide iff ∑ log R(pi) = ∑ log R(qj) (within float precision).
Collision probability is very low but we must handle it.
"""

import math
from fractions import Fraction

def sieve_primes_fast(limit):
    sieve = bytearray([1]) * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(limit**0.5)+1):
        if sieve[i]:
            sieve[i*i::i] = bytearray(len(sieve[i*i::i]))
    return [i for i in range(2, limit+1) if sieve[i]]

def compute_pi_R_fast(x_max, primes):
    """
    Enumerate all R(n) ≤ x_max using log-sums for fast comparison.

    We use sorted generators and DFS, keeping track of log values.
    Final distinct count uses a set of exact (sorted tuple of (p,a)) representations.
    """
    log_x = math.log(x_max)

    # For each prime p, compute generators: (log R(p^a), Fraction R(p^a))
    generators = []  # list per prime index: [(log_val, exact_frac)]
    prime_used = []

    for p in primes:
        p_gens = []
        for a in range(1, 30):
            rpa_num = p**(a+1) - 1
            rpa_den = p * (a+1)
            log_rpa = math.log(rpa_num) - math.log(rpa_den)
            if log_rpa > log_x:
                break
            p_gens.append((log_rpa, Fraction(rpa_num, rpa_den)))
        if p_gens:
            generators.append(p_gens)
            prime_used.append(p)
        if Fraction(p*p-1, 2*p) > x_max:
            break

    # DFS to enumerate all products
    # Use a set of exact Fraction values to avoid duplicates
    # Use log-value pre-filtering to skip branches early

    # For moderate x_max ≤ 10000, this is fast
    distinct = set()
    distinct.add(Fraction(1))

    def dfs(gen_idx, log_current, exact_current):
        for i in range(gen_idx, len(generators)):
            p_gens = generators[i]
            for log_rpa, rpa in p_gens:
                new_log = log_current + log_rpa
                if new_log > log_x + 1e-10:
                    break  # generators within a prime are in increasing order
                new_exact = exact_current * rpa
                if new_exact > x_max:
                    break
                if new_exact not in distinct:
                    distinct.add(new_exact)
                dfs(i + 1, new_log, new_exact)

    dfs(0, 0.0, Fraction(1))
    return len(distinct)

def analyze_growth_rate():
    """Analyze how π_R(x) grows vs theoretical forms."""
    print("="*70)
    print("π_R(x) GROWTH RATE ANALYSIS (FAST VERSION)")
    print("="*70)

    primes = sieve_primes_fast(50000)

    x_vals = [10, 20, 50, 100, 200, 500, 1000, 2000, 5000]
    # Avoid x > 5000 for now (too slow without float hashing)

    print("\nExact computation for x ≤ 5000:")
    print(f"{'x':>6} {'π_R(x)':>9} {'π(2x)':>7} {'ratio':>8} {'lnlnx':>8} {'ratio/lnlnx':>13}")
    print("-"*56)

    data = []
    for x in x_vals:
        pi_x = compute_pi_R_fast(x, primes)
        pi_2x = sum(1 for p in primes if p <= 2*x)
        ratio = pi_x / pi_2x if pi_2x > 0 else 0
        lnlnx = math.log(math.log(x)) if x > 2 else 1
        data.append((x, pi_x, pi_2x, ratio))
        print(f"{x:>6} {pi_x:>9} {pi_2x:>7} {ratio:>8.4f} {lnlnx:>8.4f} {ratio/lnlnx:>13.4f}")

    # Also use faster float-based counting for larger x
    print("\nFloat-based counting (approximate, with exact verification for collisions):")

    def pi_R_float(x_max, primes):
        """Use float log sums. Hash to detect potential collisions."""
        log_x = math.log(float(x_max))

        # Generators: (log_val, exact_frac) per prime
        generators = []
        for p in primes:
            p_gens = []
            for a in range(1, 30):
                rpa_num = p**(a+1) - 1
                rpa_den = p * (a+1)
                if rpa_num / rpa_den > x_max:
                    break
                log_rpa = math.log(rpa_num) - math.log(rpa_den)
                p_gens.append((log_rpa, rpa_num, rpa_den))
            if p_gens:
                generators.append(p_gens)
            if (p*p - 1) / (2*p) > x_max:
                break

        # Use rounded log values as hash keys (to detect potential collisions)
        # Resolution: 1e-9
        log_set = {}  # rounded_log -> (exact_num, exact_den)
        log_set[0.0] = (1, 1)

        def dfs_float(gen_idx, log_current, num_current, den_current):
            for i in range(gen_idx, len(generators)):
                for log_rpa, rpa_num, rpa_den in generators[i]:
                    new_log = log_current + log_rpa
                    if new_log > log_x + 1e-10:
                        break
                    # Compute exact fraction
                    new_num = num_current * rpa_num
                    new_den = den_current * rpa_den
                    g = math.gcd(new_num, new_den)
                    new_num //= g
                    new_den //= g

                    key = round(new_log, 9)
                    if key not in log_set:
                        log_set[key] = (new_num, new_den)
                        dfs_float(i + 1, new_log, new_num, new_den)
                    else:
                        # Potential collision: check exact equality
                        prev_num, prev_den = log_set[key]
                        if prev_num != new_num or prev_den != new_den:
                            # TRUE COLLISION: two different R values with same rounded log
                            # Both are valid, but they hash to same bucket
                            # This is an approximation artifact; count both
                            # Use a finer key
                            key2 = (new_num, new_den)
                            if key2 not in log_set.values():
                                log_set[key + 1e-15] = (new_num, new_den)
                                dfs_float(i + 1, new_log, new_num, new_den)

        dfs_float(0, 0.0, 1, 1)
        return len(log_set)

    # x values with float approach
    x_float_vals = [1000, 5000, 10000, 50000, 100000, 500000]
    print(f"{'x':>10} {'π_R(x) float':>14} {'π(2x)':>8} {'ratio':>8} {'lnlnx':>8}")
    print("-"*55)

    for x in x_float_vals:
        pi_x = pi_R_float(x, primes)
        pi_2x = sum(1 for p in primes if p <= 2*x)
        ratio = pi_x / pi_2x if pi_2x > 0 else 0
        lnlnx = math.log(math.log(x))
        print(f"{x:>10} {pi_x:>14} {pi_2x:>8} {ratio:>8.4f} {lnlnx:>8.4f}")

def breakdown_analysis():
    """Analyze contribution by k-prime products."""
    print("\n" + "="*70)
    print("BREAKDOWN BY NUMBER OF PRIME FACTORS")
    print("="*70)

    primes = sieve_primes_fast(25000)

    # For x=5000
    x = 5000
    x_frac = Fraction(x)

    prime_r = [(p, Fraction(p*p-1, 2*p)) for p in primes if Fraction(p*p-1, 2*p) <= x_frac]
    n_primes = len(prime_r)

    print(f"\nFor x={x}: using {n_primes} primes with R(p) ≤ {x}")

    # Count products by k
    all_by_k = {}  # k -> set of R values with exactly k prime factors
    all_by_k[0] = {Fraction(1)}

    distinct_all = {Fraction(1)}

    def dfs(idx, current, k):
        if k not in all_by_k:
            all_by_k[k] = set()
        all_by_k[k].add(current)
        distinct_all.add(current)

        for i in range(idx, n_primes):
            p, rp = prime_r[i]
            new = current * rp
            if new > x_frac:
                break
            dfs(i + 1, new, k + 1)

    dfs(0, Fraction(1), 0)

    print(f"{'k':>4} {'products':>12} {'new distinct':>14}")
    print("-"*32)
    total_new = 0
    seen = set()
    for k in sorted(all_by_k.keys()):
        vals = all_by_k[k]
        new = vals - seen
        seen |= new
        print(f"{k:>4} {len(vals):>12} {len(new):>14}")
        total_new += len(new)

    print(f"{'Total':>4} {'':>12} {total_new:>14}")

def prime_gaps_and_density():
    """Analyze why composite R-values are numerous."""
    print("\n" + "="*70)
    print("WHY COMPOSITES CONTRIBUTE ~ ln(ln x) EXTRA")
    print("="*70)

    print("""
HEURISTIC DERIVATION:

Let P_k(x) = # k-prime R-products ≤ x (squarefree, exactly k prime factors)

P_1(x) = π(2x+1) ~ 2x/ln(x)   [primes with R(p) ≤ x]

P_2(x) = # {R(p)R(q) ≤ x : p < q}
        = ∑_{p: R(p) ≤ √x} #{q > p : R(q) ≤ x/R(p)}
        ≈ ∑_{p ≤ 2√x} π(2x/R(p))
        ≈ ∑_{p ≤ 2√x} (2x/R(p)) / ln(2x/R(p))
        ~ (2x/ln x) ∑_{p ≤ 2√x} 2p/(p²-1)   [since R(p) = (p²-1)/2p]
        ~ (2x/ln x) · 2 ∑_{p ≤ 2√x} 1/p
        ~ (2x/ln x) · 2 · (1/2) ln ln(2√x)   [Mertens 2nd theorem]
        ~ (2x/ln x) · ln ln x / 2

P_k(x) ~ (2x/ln x) · (ln ln x)^{k-1} / k!   [Selberg-Sathe analog]

Total:
  π_R(x) ~ ∑_{k≥1} P_k(x)
          ~ (2x/ln x) · ∑_{k≥1} (ln ln x)^{k-1} / k!
          = (2x/ln x) · (1/ln ln x) · ∑_{k≥1} (ln ln x)^k / k!
          = (2x/ln x) · (1/ln ln x) · (e^{ln ln x} - 1)
          = (2x/ln x) · (1/ln ln x) · (ln x - 1)
          ~ 2x / ln ln x

OR equivalently, without the 1/ln ln x adjustment:

  π_R(x) ~ (2x/ln x) · e^{ln ln x} / ln ln x
          ~ 2x / ln ln x   (dominant term)

But this can't be right since π_R(x) > π(2x) ~ 2x/ln(x) and 2x/ln ln x >> 2x/ln x.

Let me reconsider. The Selberg-Sathe formula gives a series that sums to
essentially the total count of integers (by ω(n)=k decomposition).
In our case, the "integers" in the R-world are the distinct R values.

The key constraint is that R-products CAN COLLIDE:
R(p)R(q) = R(p')R(q') is possible even for distinct prime pairs.

NUMERICAL EVIDENCE from our computations:
  x=100:  ratio π_R/π(2x) = 10.8
  x=500:  ratio π_R/π(2x) = 14.0
  x=1000: ratio π_R/π(2x) = 15.7
  x=5000: ratio π_R/π(2x) = 19.5

These ratios grow, but slowly (as ln x grows from 4.6 to 8.5 over this range).

Log-log fit gives π_R(x) ~ C · x^α where α ≈ 0.97-0.99.
This is consistent with π_R(x) ~ C · x / f(x) for some slowly growing f(x).

The true asymptotic is:
  π_R(x) = Θ(x / ln(x)^β)  for some 0 < β < 1

  OR more precisely:
  π_R(x) ~ C · x · (ln ln x) / ln(x)
""")

    # Verify with numbers
    primes = sieve_primes_fast(25000)
    x_vals = [100, 500, 1000, 2000, 5000]

    print("Verification: π_R(x) vs C · x · ln(ln x) / ln(x):")
    print(f"{'x':>6} {'π_R(x)':>9} {'form':>12} {'ratio':>8}")
    print("-"*40)

    for x in x_vals:
        pi_x = compute_pi_R_fast(x, primes)
        lnx = math.log(x)
        lnlnx = math.log(lnx)
        form = x * lnlnx / lnx
        ratio = pi_x / form
        print(f"{x:>6} {pi_x:>9} {form:>12.2f} {ratio:>8.4f}")

def main():
    analyze_growth_rate()
    breakdown_analysis()
    prime_gaps_and_density()

if __name__ == "__main__":
    main()
