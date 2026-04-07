"""
Final π_R(x) computation.
Use BFS-like layer approach: build distinct R values level by level.
Level k = R values with exactly k prime factors.

This avoids recomputation and is much faster.
"""

import math
import sys

def sieve(n):
    a = bytearray([1]) * (n+1)
    a[0] = a[1] = 0
    for i in range(2, int(n**0.5)+1):
        if a[i]: a[i*i::i] = bytearray(len(a[i*i::i]))
    return [i for i in range(2, n+1) if a[i]]

def gcd(a, b):
    while b: a, b = b, a % b
    return a

def fraction_leq(n1, d1, n2, d2):
    """Test n1/d1 ≤ n2/d2."""
    return n1 * d2 <= n2 * d1

def reduce_frac(n, d):
    g = gcd(n, d)
    return n//g, d//g

def pi_R(x_int):
    """
    Count distinct R(n) values ≤ x_int.
    Returns count and optionally the values.
    """
    # Get primes p with R(p) = (p²-1)/(2p) ≤ x
    primes = sieve(2*x_int + 100)

    # Generate all (reduced_num, reduced_den) for each prime's generators
    prime_gen_lists = []  # list of lists; each inner list is generators for one prime
    prime_indices = []    # the actual prime

    for p in primes:
        gens = []
        for a in range(1, 50):
            num = p**(a+1) - 1
            den = p * (a+1)
            if num > x_int * den:  # R(p^a) > x
                break
            rn, rd = reduce_frac(num, den)
            gens.append((rn, rd))
        if gens:
            prime_gen_lists.append(gens)
            prime_indices.append(p)
        # Early termination: if R(p) > x, all higher primes also have R(p) > x
        if (p*p - 1) > x_int * 2 * p:
            break

    n_primes = len(prime_gen_lists)

    # Layer 0: just {(1,1)}
    # Layer k: set of reduced (num, den) pairs reachable with exactly k distinct primes
    # Use sorted prime index constraint to avoid duplicates

    # We'll use a different data structure:
    # current_layer = set of (reduced_num, reduced_den, last_prime_index)
    # This avoids recomputation.

    all_values = set()
    all_values.add((1, 1))

    # Use (value, min_next_prime_idx) as state
    # Process layer by layer to limit memory

    frontier = [(1, 1, 0)]  # (num, den, next_prime_idx)
    # new_frontier will hold things we haven't explored yet

    # BFS: expand each state by adding one more prime
    max_k = 20  # stop after 20 prime factors (R values become huge)

    current_layer_states = [(1, 1, 0)]

    for k in range(1, max_k + 1):
        next_layer_states = []
        new_values_this_layer = 0

        for cn, cd, start_idx in current_layer_states:
            for i in range(start_idx, n_primes):
                for rn, rd in prime_gen_lists[i]:
                    nn = cn * rn
                    nd = cd * rd
                    # Reduce
                    g = gcd(nn, nd)
                    nn //= g
                    nd //= g
                    # Check ≤ x
                    if nn <= x_int * nd:
                        key = (nn, nd)
                        if key not in all_values:
                            all_values.add(key)
                            new_values_this_layer += 1
                        next_layer_states.append((nn, nd, i + 1))
                    else:
                        break  # generators for same prime are increasing
            # break outer too if no valid products found

        if new_values_this_layer == 0:
            break
        current_layer_states = next_layer_states
        print(f"  Layer k={k}: {new_values_this_layer} new values, layer size={len(current_layer_states)}")
        sys.stdout.flush()

    return len(all_values)

def main():
    print("="*70)
    print("π_R(x) LAYERED BFS COMPUTATION")
    print("="*70)

    primes_big = sieve(210000)

    def count_pi2x(x):
        return sum(1 for p in primes_big if p <= 2*x)

    x_vals = [10, 50, 100, 500, 1000, 5000, 10000, 50000, 100000]

    all_results = []

    for x in x_vals:
        print(f"\nx = {x}:")
        pi = pi_R(x)
        p2x = count_pi2x(x)
        ratio = pi / p2x if p2x else 0
        lnx = math.log(x) if x > 1 else 1
        lnlnx = math.log(lnx) if lnx > 1 else 1
        all_results.append((x, pi, p2x))
        print(f"  π_R({x}) = {pi}, π(2x) = {p2x}, ratio = {ratio:.4f}")
        sys.stdout.flush()

    print("\n\n" + "="*70)
    print("SUMMARY TABLE")
    print("="*70)
    print(f"{'x':>8} {'π_R(x)':>10} {'π(2x)':>8} {'ratio':>8} {'lnlnx':>8} {'ratio/lnlnx':>13}")
    print("-"*60)
    for x, pi, p2x in all_results:
        ratio = pi / p2x if p2x else 0
        lnx = math.log(x) if x > 1 else 1
        lnlnx = math.log(lnx) if lnx > 1 else 1
        print(f"{x:>8} {pi:>10} {p2x:>8} {ratio:>8.3f} {lnlnx:>8.4f} {ratio/lnlnx:>13.3f}")

    print()

    if len(all_results) >= 3:
        # Log-log fit
        log_x = [math.log(x) for x, _, _ in all_results if x >= 50]
        log_pi = [math.log(pi) for x, pi, _ in all_results if x >= 50]
        n = len(log_x)
        if n >= 2:
            sx = sum(log_x); sy = sum(log_pi)
            sxy = sum(a*b for a,b in zip(log_x,log_pi))
            sx2 = sum(a**2 for a in log_x)
            slope = (n*sxy - sx*sy)/(n*sx2 - sx**2)
            intercept = (sy - slope*sx)/n
            print(f"Log-log fit: π_R(x) ~ {math.exp(intercept):.4f} · x^{slope:.6f}")

    print()
    print("Checking form π_R(x) ~ C · x · lnlnx / lnx:")
    print(f"{'x':>8} {'π_R(x)':>10} {'x·lnlnx/lnx':>14} {'C':>8}")
    print("-"*45)
    for x, pi, p2x in all_results:
        if x >= 50:
            lnx = math.log(x)
            lnlnx = math.log(lnx)
            form = x * lnlnx / lnx
            C = pi / form
            print(f"{x:>8} {pi:>10} {form:>14.2f} {C:>8.4f}")

if __name__ == "__main__":
    main()
