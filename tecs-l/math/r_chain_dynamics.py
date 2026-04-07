#!/usr/bin/env python3
"""
R-chain dynamics: R(n) = sigma(n)*phi(n)/(n*tau(n))
Investigate basins of attraction, density, chain lengths.
"""

import sys
from math import gcd
from collections import defaultdict, Counter

# --- Core arithmetic functions via sieve ---

def compute_functions(N):
    """Compute sigma(n), phi(n), tau(n) for all n <= N using sieves."""
    sigma = [0] * (N + 1)  # sum of divisors
    phi = list(range(N + 1))  # Euler's totient
    tau = [0] * (N + 1)  # number of divisors

    # Sieve for tau and sigma
    for d in range(1, N + 1):
        for multiple in range(d, N + 1, d):
            tau[multiple] += 1
            sigma[multiple] += d

    # Sieve for phi
    for p in range(2, N + 1):
        if phi[p] == p:  # p is prime
            for multiple in range(p, N + 1, p):
                phi[multiple] = phi[multiple] // p * (p - 1)

    return sigma, phi, tau


def main():
    N = 500000
    print(f"Computing arithmetic functions up to {N}...")
    sigma, phi, tau = compute_functions(N)

    # --- Compute R(n) for all n, track which are integers ---
    print("Computing R(n) values...")
    R = {}  # n -> R(n) if integer
    integer_R_count = [0] * (N + 1)  # cumulative count of integer R up to n

    count = 0
    for n in range(2, N + 1):
        numerator = sigma[n] * phi[n]
        denominator = n * tau[n]
        if numerator % denominator == 0:
            R[n] = numerator // denominator
            count += 1
        integer_R_count[n] = count

    # =========================================================
    # TASK 1: Basins of attraction - R^{-1}(v) for key values
    # =========================================================
    print("\n" + "=" * 60)
    print("TASK 1: BASINS OF ATTRACTION (PREIMAGES)")
    print("=" * 60)

    # Build reverse map
    preimage = defaultdict(list)
    for n, rv in R.items():
        preimage[rv].append(n)

    # Known chain: 193750 -> 6048 -> 120 -> 6 -> 1
    targets = [1, 6, 120, 6048, 6552]
    for t in targets:
        pre = sorted(preimage.get(t, []))
        print(f"\nR^{{-1}}({t}): {len(pre)} elements")
        if len(pre) <= 30:
            print(f"  Values: {pre}")
        else:
            print(f"  First 30: {pre[:30]}")
            print(f"  Last 5: {pre[-5:]}")

    # Full basin tree from 1 upward
    print("\n--- BASIN TREE (breadth-first from 1) ---")
    level = [1]
    depth = 0
    all_in_basin = set()
    while level and depth < 10:
        print(f"Depth {depth}: {len(level)} nodes", end="")
        if len(level) <= 20:
            print(f" = {sorted(level)}")
        else:
            print(f" (first 20: {sorted(level)[:20]})")
        all_in_basin.update(level)
        next_level = []
        for v in level:
            next_level.extend(preimage.get(v, []))
        level = next_level
        depth += 1
    print(f"\nTotal nodes in basin of 1 (up to N={N}): {len(all_in_basin)}")

    # =========================================================
    # TASK 2: Is the basin tree finitely branching? Growth?
    # =========================================================
    print("\n" + "=" * 60)
    print("TASK 2: BASIN BRANCHING ANALYSIS")
    print("=" * 60)

    # For each value v that appears as R(n), count |R^{-1}(v)|
    branching = {}
    for v in preimage:
        branching[v] = len(preimage[v])

    # Distribution of branching factors
    branch_counts = Counter(branching.values())
    print("\nBranching factor distribution (how many values have k preimages):")
    print(f"  {'k preimages':>12} | {'count':>8}")
    print(f"  {'-'*12}-+-{'-'*8}")
    for k in sorted(branch_counts.keys())[:20]:
        print(f"  {k:>12} | {branch_counts[k]:>8}")

    # Top branching values
    top_branch = sorted(branching.items(), key=lambda x: -x[1])[:20]
    print("\nTop 20 most-reached values (largest preimage sets):")
    print(f"  {'value':>10} | {'|R^-1|':>8} | {'first few preimages'}")
    print(f"  {'-'*10}-+-{'-'*8}-+-{'-'*30}")
    for v, cnt in top_branch:
        pre_sample = sorted(preimage[v])[:5]
        print(f"  {v:>10} | {cnt:>8} | {pre_sample}")

    # =========================================================
    # TASK 3: Density of integer R(n)
    # =========================================================
    print("\n" + "=" * 60)
    print("TASK 3: DENSITY OF INTEGER R(n)")
    print("=" * 60)

    checkpoints = [100, 500, 1000, 5000, 10000, 50000, 100000, 200000, 500000]
    print(f"\n  {'N':>10} | {'count':>8} | {'density':>10} | {'N*density':>10}")
    print(f"  {'-'*10}-+-{'-'*8}-+-{'-'*10}-+-{'-'*10}")
    for cp in checkpoints:
        if cp <= N:
            c = integer_R_count[cp]
            d = c / cp
            print(f"  {cp:>10} | {c:>8} | {d:>10.6f} | {cp*d:>10.2f}")

    # =========================================================
    # TASK 4: Histogram of R-chain lengths up to 100000
    # =========================================================
    print("\n" + "=" * 60)
    print("TASK 4: R-CHAIN LENGTH HISTOGRAM (n <= 100000)")
    print("=" * 60)

    # Chain length:
    #   0 = R(n) not integer
    #   1 = R(n) integer, R(R(n)) not integer (or R(n)=1)
    #   2 = chain reaches 1 in 2 steps, etc.
    # Actually let's define: length = number of steps to reach 1 (or 0 if doesn't reach)

    # First: for each n with integer R, compute chain
    chain_length = {}  # n -> length of chain to 1 (None if doesn't reach)

    def get_chain_length(n):
        if n in chain_length:
            return chain_length[n]
        if n == 1:
            chain_length[n] = 0
            return 0
        if n not in R:
            chain_length[n] = None  # R(n) not integer
            return None
        rv = R[n]
        sub = get_chain_length(rv)
        if sub is None:
            chain_length[n] = None
        else:
            chain_length[n] = 1 + sub
        return chain_length[n]

    sys.setrecursionlimit(100000)

    for n in range(1, 100001):
        get_chain_length(n)

    # Histogram
    length_hist = Counter()
    non_integer_count = 0
    reaches_1 = 0
    integer_but_no_1 = 0

    for n in range(2, 100001):
        cl = chain_length.get(n)
        if n not in R:
            non_integer_count += 1
            length_hist[0] += 1
        elif cl is None:
            integer_but_no_1 += 1
            length_hist[-1] += 1  # -1 = integer R but doesn't reach 1
        else:
            reaches_1 += 1
            length_hist[cl] += 1

    total = 99999
    print(f"\nTotal n in [2, 100000]: {total}")
    print(f"R(n) not integer:       {non_integer_count} ({100*non_integer_count/total:.2f}%)")
    print(f"R(n) integer, reaches 1: {reaches_1} ({100*reaches_1/total:.2f}%)")
    print(f"R(n) integer, no reach:  {integer_but_no_1} ({100*integer_but_no_1/total:.2f}%)")

    print(f"\n  {'chain length':>12} | {'count':>8} | {'fraction':>10}")
    print(f"  {'-'*12}-+-{'-'*8}-+-{'-'*10}")
    for length in sorted(length_hist.keys()):
        if length == 0:
            label = "non-integer"
        elif length == -1:
            label = "int,no->1"
        else:
            label = str(length)
        c = length_hist[length]
        print(f"  {label:>12} | {c:>8} | {c/total:>10.6f}")

    # Show the actual chains that reach 1
    print("\n--- ALL CHAINS REACHING 1 (n <= 100000) ---")
    chains_to_1 = []
    for n in range(2, 100001):
        cl = chain_length.get(n)
        if cl is not None and cl > 0:
            # Reconstruct chain
            chain = [n]
            cur = n
            while cur != 1:
                cur = R[cur]
                chain.append(cur)
            chains_to_1.append((len(chain) - 1, chain))

    chains_to_1.sort(key=lambda x: -x[0])
    for length, chain in chains_to_1:
        print(f"  Length {length}: {' -> '.join(map(str, chain))}")

    # Show chains that are integer but DON'T reach 1
    print("\n--- INTEGER R(n) BUT NOT REACHING 1 (n <= 100000, first 50) ---")
    no_reach = []
    for n in range(2, 100001):
        if n in R and chain_length.get(n) is None:
            # Show where chain breaks
            chain = [n]
            cur = n
            while cur in R and cur != 1:
                cur = R[cur]
                chain.append(cur)
            no_reach.append(chain)

    for chain in no_reach[:50]:
        arrow = ' -> '.join(map(str, chain))
        print(f"  {arrow} (R({chain[-1]}) not integer)")
    print(f"  ... total: {len(no_reach)}")

    # =========================================================
    # EXTRA: Extend basin search for R^{-1}(6048)
    # =========================================================
    print("\n" + "=" * 60)
    print("EXTRA: DETAILED PREIMAGE SEARCH")
    print("=" * 60)

    for target in [1, 6, 120, 6048, 6552]:
        pre = sorted(preimage.get(target, []))
        print(f"\nR^{{-1}}({target}) up to {N}: {pre}")

    # Verify the known chain
    print("\n--- VERIFICATION: 193750 -> 6048 -> 120 -> 6 -> 1 ---")
    for n in [193750, 6048, 120, 6]:
        if n <= N:
            s, p, t = sigma[n], phi[n], tau[n]
            num = s * p
            den = n * t
            print(f"  R({n}) = sigma({n})*phi({n})/({n}*tau({n})) = {s}*{p}/({n}*{t}) = {num}/{den} = {num/den}" +
                  (f" = {num//den}" if num % den == 0 else " (not integer!)"))


if __name__ == "__main__":
    main()
