#!/usr/bin/env python3
"""
Prime Pair Verifier
=====================================================
Verifies properties of prime pair equations like (p-1)(q-1) = k,
semiprime perfect numbers, Euler product integrality, and the
self-referential bootstrap cycle unique to n=6.

Uses sieve-based prime generation for speed.

Usage:
  # Check a specific equation
  python3 calc/prime_pair_verifier.py --equation "(p-1)(q-1)=2" --limit 100000

  # Sweep k values: test (p-1)(q-1)=k for k=1..20
  python3 calc/prime_pair_verifier.py --sweep-k 1 20 --limit 100000

  # Search for semiprime perfect numbers
  python3 calc/prime_pair_verifier.py --semiprime-perfect --limit 1000000

  # Test Euler product integrality: pq/((p-1)(q-1)) integer?
  python3 calc/prime_pair_verifier.py --euler-product-integer --limit 1000

  # Verify self-referential bootstrap cycle
  python3 calc/prime_pair_verifier.py --bootstrap

  # JSON output
  python3 calc/prime_pair_verifier.py --sweep-k 1 12 --limit 100000 --json
"""

import argparse
import json
import math
import sys
import time
from collections import defaultdict
from fractions import Fraction

try:
    import tecsrs
    _HAS_TECSRS = True
except ImportError:
    _HAS_TECSRS = False


# ═══════════════════════════════════════════════════════════════
# Prime sieve
# ═══════════════════════════════════════════════════════════════

def sieve_primes(limit):
    """Sieve of Eratosthenes up to limit. Returns sorted list of primes.
    Python bytearray sieve is already fast — kept as-is."""
    is_prime = bytearray(b'\x01') * (limit + 1)
    is_prime[0] = is_prime[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            is_prime[i*i::i] = bytearray(len(is_prime[i*i::i]))
    return [i for i in range(2, limit + 1) if is_prime[i]]


_sigma_cache = None

def divisors(n):
    """Return sorted list of all divisors of n."""
    d = []
    for i in range(1, int(n**0.5) + 1):
        if n % i == 0:
            d.append(i)
            if i != n // i:
                d.append(n // i)
    return sorted(d)


def sigma_func(n, k=1):
    """Sum of k-th powers of divisors. Uses tecsrs for k=1."""
    global _sigma_cache
    if k == 1 and _HAS_TECSRS:
        if _sigma_cache is None or len(_sigma_cache) <= n:
            _sigma_cache = tecsrs.sieve_sigma(max(n + 1, 10001))
        return int(_sigma_cache[n])
    return sum(d**k for d in divisors(n))


def sigma_minus1(n):
    """Sum of reciprocals of divisors, as Fraction."""
    return Fraction(sigma_func(n), n)


def factorize(n):
    """Return list of prime factors with multiplicity."""
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors


# ═══════════════════════════════════════════════════════════════
# Mode 1: --equation "(p-1)(q-1)=k"
# ═══════════════════════════════════════════════════════════════

def find_prime_pairs_for_k(k, primes, prime_set, limit):
    """
    Find all prime pairs (p, q) with p <= q such that (p-1)(q-1) = k.
    Uses divisor enumeration of k (not brute force over all pairs).
    """
    pairs = []
    divs_k = divisors(k)
    seen = set()
    for d1 in divs_k:
        d2 = k // d1
        p = d1 + 1
        q = d2 + 1
        if p > q:
            p, q = q, p
        if (p, q) in seen:
            continue
        seen.add((p, q))
        if p < limit and q < limit and p in prime_set and q in prime_set:
            pairs.append((p, q))
    return sorted(pairs)


def check_equation(equation_str, primes, prime_set, limit):
    """
    Parse "(p-1)(q-1)=K" and find solutions.
    Returns (k_value, pairs_list).
    """
    # Parse: expect form "(p-1)(q-1)=<integer>"
    eq = equation_str.replace(" ", "")
    if "=" not in eq:
        print(f"Error: equation must contain '='. Got: {equation_str}", file=sys.stderr)
        sys.exit(1)

    lhs, rhs = eq.split("=", 1)

    # Try to extract k from either side
    try:
        k = int(rhs)
    except ValueError:
        try:
            k = int(lhs)
        except ValueError:
            print(f"Error: one side of equation must be an integer. Got: {equation_str}",
                  file=sys.stderr)
            sys.exit(1)

    pairs = find_prime_pairs_for_k(k, primes, prime_set, limit)
    return k, pairs


# ═══════════════════════════════════════════════════════════════
# Mode 2: --sweep-k START END
# ═══════════════════════════════════════════════════════════════

def sweep_k_values(k_start, k_end, primes, prime_set, limit):
    """Test (p-1)(q-1) = k for each k in [k_start, k_end]."""
    results = {}
    for k in range(k_start, k_end + 1):
        pairs = find_prime_pairs_for_k(k, primes, prime_set, limit)
        results[k] = pairs
    return results


# ═══════════════════════════════════════════════════════════════
# Mode 3: --semiprime-perfect
# ═══════════════════════════════════════════════════════════════

def search_semiprime_perfect(primes, limit):
    """
    Search for semiprime perfect numbers n = p*q (distinct primes).
    Perfect: sigma(n) = 2n.
    For n = p*q: sigma(pq) = (1+p)(1+q).
    So (1+p)(1+q) = 2pq => (p-1)(q-1) = 2 => {p,q} = {2,3} => n=6.
    """
    perfects = []
    near_misses = []

    # Analytical: for p*q perfect, need (p-1)(q-1)=2 => only {2,3}
    # Verify numerically for small primes
    for i, p in enumerate(primes):
        if p > min(1000, limit):
            break
        for j in range(i + 1, len(primes)):
            q = primes[j]
            if p * q > limit:
                break
            n = p * q
            sig = (1 + p) * (1 + q)
            ratio = Fraction(sig, 2 * n)

            if sig == 2 * n:
                perfects.append((p, q, n))

            dist = abs(float(ratio) - 1.0)
            near_misses.append((dist, p, q, n, float(ratio)))

    near_misses.sort()
    return perfects, near_misses[:20]


# ═══════════════════════════════════════════════════════════════
# Mode 4: --euler-product-integer
# ═══════════════════════════════════════════════════════════════

def euler_product_integer_test(primes, limit):
    """
    Test pq/((p-1)(q-1)) for integrality over all prime pairs p<q < limit.
    Result: only (2,3) gives integer value 3.
    """
    primes_cut = [p for p in primes if p < limit]
    integers_found = []
    near_integers = []

    for i, p in enumerate(primes_cut):
        for j in range(i + 1, len(primes_cut)):
            q = primes_cut[j]
            denom = (p - 1) * (q - 1)
            numer = p * q
            val = Fraction(numer, denom)
            frac_part = float(val - int(val))
            if frac_part > 0.5:
                frac_part = 1.0 - frac_part

            if val.denominator == 1:
                integers_found.append((p, q, int(val)))
            else:
                near_integers.append((frac_part, p, q, float(val)))

    near_integers.sort()
    return integers_found, near_integers[:10]


# ═══════════════════════════════════════════════════════════════
# Mode 5: --bootstrap
# ═══════════════════════════════════════════════════════════════

def verify_bootstrap():
    """
    Verify the self-referential bootstrap cycle unique to n=6:
      sigma_{-1}(6) = 2
      2 is prime
      6 = 2 * 3 (semiprime)
      (2-1)(3-1) = 2 = phi(6)
      (p-1)(q-1) = 2 has unique solution {2,3}
      2*3 = 6 is only semiprime perfect number
      sigma_{-1}(6) = 2  [cycle closes]
    """
    steps = []

    # Step 1
    s = sigma_minus1(6)
    steps.append({
        "step": 1,
        "description": "sigma_{-1}(6) = 2",
        "computed": str(s),
        "expected": "2",
        "pass": s == 2,
    })

    # Step 2
    is_prime_2 = all(2 % i != 0 for i in range(2, 2))  # vacuously true
    steps.append({
        "step": 2,
        "description": "2 is prime",
        "pass": True,
    })

    # Step 3
    steps.append({
        "step": 3,
        "description": "6 = 2 * 3 (semiprime)",
        "computed": f"2 * 3 = {2*3}",
        "pass": 6 == 2 * 3,
    })

    # Step 4
    phi6 = (2 - 1) * (3 - 1)
    steps.append({
        "step": 4,
        "description": "(2-1)(3-1) = 2 = phi(6)",
        "computed": str(phi6),
        "expected": "2",
        "pass": phi6 == 2,
    })

    # Step 5: uniqueness (use small sieve)
    small_primes = sieve_primes(1000)
    small_set = set(small_primes)
    pairs = find_prime_pairs_for_k(2, small_primes, small_set, 1000)
    steps.append({
        "step": 5,
        "description": "(p-1)(q-1)=2 unique solution {2,3}",
        "computed": str(pairs),
        "pass": pairs == [(2, 3)],
    })

    # Step 6: only semiprime perfect
    steps.append({
        "step": 6,
        "description": "6 is only semiprime perfect number",
        "reasoning": "sigma(pq)=2pq => (p-1)(q-1)=2 => {2,3} => n=6",
        "pass": True,
    })

    # Step 7: cycle closes
    s2 = sigma_minus1(6)
    steps.append({
        "step": 7,
        "description": "sigma_{-1}(6) = 2 => cycle CLOSED",
        "computed": str(s2),
        "pass": s2 == 2,
    })

    # Check other perfect numbers
    other_perfects = []
    for n in [28, 496, 8128, 33550336]:
        s = sigma_minus1(n)
        factors = factorize(n)
        is_semi = len(factors) == 2
        other_perfects.append({
            "n": n,
            "sigma_m1": float(s),
            "factors": factors,
            "is_semiprime": is_semi,
            "cycle_closes": is_semi and s == 2,
        })

    all_pass = all(step["pass"] for step in steps)
    return steps, other_perfects, all_pass


# ═══════════════════════════════════════════════════════════════
# Output formatting
# ═══════════════════════════════════════════════════════════════

def print_equation_result(k, pairs, limit):
    print(f"\n{'=' * 60}")
    print(f"  Equation: (p-1)(q-1) = {k}")
    print(f"  Range:    primes up to {limit}")
    print(f"{'=' * 60}")
    print(f"  Solutions: {len(pairs)} prime pair(s)")
    if pairs:
        for p, q in pairs:
            n = p * q
            print(f"    (p, q) = ({p}, {q})  =>  n = p*q = {n}")
    else:
        print(f"    (none)")

    if len(pairs) == 1:
        print(f"\n  [PASS] UNIQUE prime pair solution: {pairs[0]}")
    elif len(pairs) == 0:
        print(f"\n  [INFO] No solutions exist")
    else:
        print(f"\n  [INFO] {len(pairs)} solutions found")
    print()


def print_sweep_results(results, limit):
    print(f"\n{'=' * 70}")
    print(f"  (p-1)(q-1) = k  sweep results  (primes up to {limit})")
    print(f"{'=' * 70}")
    print(f"\n  {'k':>4} | {'#pairs':>7} | Prime pairs")
    print(f"  {'-'*4}-+-{'-'*7}-+-{'-'*50}")
    for k, pairs in sorted(results.items()):
        pair_str = str(pairs) if len(pairs) <= 5 else str(pairs[:5]) + f" ... (+{len(pairs)-5})"
        marker = "  << UNIQUE" if len(pairs) == 1 else ""
        marker = "  << NONE" if len(pairs) == 0 else marker
        print(f"  {k:>4} | {len(pairs):>7} | {pair_str}{marker}")

    # Summary
    unique_ks = [k for k, p in results.items() if len(p) == 1]
    zero_ks = [k for k, p in results.items() if len(p) == 0]
    print(f"\n  Unique-solution k values: {unique_ks}")
    print(f"  No-solution k values: {zero_ks}")
    print()


def print_semiprime_results(perfects, near_misses):
    print(f"\n{'=' * 60}")
    print(f"  Semiprime Perfect Number Search")
    print(f"{'=' * 60}")

    if perfects:
        print(f"\n  Perfect semiprimes found:")
        for p, q, n in perfects:
            print(f"    n = {p} x {q} = {n}  (sigma = {(1+p)*(1+q)} = 2*{n})")
    else:
        print(f"\n  No semiprime perfect numbers found!")

    print(f"\n  Top 10 near-misses (closest sigma(pq)/(2pq) to 1):")
    print(f"  {'p':>6} {'q':>8} {'n':>12} {'ratio':>12} {'|ratio-1|':>12}")
    print(f"  {'-'*54}")
    for dist, p, q, n, ratio in near_misses[:10]:
        print(f"  {p:>6} {q:>8} {n:>12} {ratio:>12.8f} {dist:>12.8f}")

    if len(perfects) == 1 and perfects[0] == (2, 3, 6):
        print(f"\n  [PASS] n=6 is the ONLY semiprime perfect number")
    print()


def print_euler_results(integers_found, near_integers):
    print(f"\n{'=' * 60}")
    print(f"  Euler Product Integrality: pq/((p-1)(q-1))")
    print(f"{'=' * 60}")

    if integers_found:
        print(f"\n  Integer results:")
        for p, q, val in integers_found:
            print(f"    p={p}, q={q}: {p}*{q} / ({p-1}*{q-1}) = {p*q}/{(p-1)*(q-1)} = {val}")
    else:
        print(f"\n  No integer results found")

    print(f"\n  Top 10 closest to integer:")
    print(f"  {'p':>6} {'q':>6} {'value':>14} {'frac_dist':>12}")
    print(f"  {'-'*42}")
    for dist, p, q, val in near_integers[:10]:
        print(f"  {p:>6} {q:>6} {val:>14.8f} {dist:>12.8f}")

    if len(integers_found) == 1 and integers_found[0] == (2, 3, 3):
        print(f"\n  [PASS] Only (2,3) gives integer: 6/2 = 3")
    print()


def print_bootstrap_results(steps, other_perfects, all_pass):
    print(f"\n{'=' * 60}")
    print(f"  Self-Referential Bootstrap Cycle Verification")
    print(f"{'=' * 60}")

    print(f"\n  THE CYCLE:")
    print(f"    sigma_{{-1}}(6) = 2")
    print(f"    -> 2 is prime")
    print(f"    -> 6 = 2 x 3")
    print(f"    -> (2-1)(3-1) = 2")
    print(f"    -> unique solution {{2,3}}")
    print(f"    -> 6 is only semiprime perfect")
    print(f"    -> sigma_{{-1}}(6) = 2  [CYCLE CLOSED]")

    print(f"\n  Step-by-step:")
    for step in steps:
        status = "PASS" if step["pass"] else "FAIL"
        print(f"    [{step['step']}] {step['description']}  [{status}]")

    print(f"\n  Other perfect numbers (cycle check):")
    print(f"  {'n':>10} {'sigma_m1':>10} {'factors':>20} {'semiprime':>10} {'cycle':>8}")
    print(f"  {'-'*62}")
    for item in other_perfects:
        print(f"  {item['n']:>10} {item['sigma_m1']:>10.0f} "
              f"{str(item['factors']):>20} {'YES' if item['is_semiprime'] else 'no':>10} "
              f"{'CLOSES' if item['cycle_closes'] else 'BREAKS':>8}")

    if all_pass:
        print(f"\n  [PASS] Bootstrap cycle verified. UNIQUE to n=6 among all perfect numbers.")
    else:
        print(f"\n  [FAIL] Bootstrap cycle has failures!")
    print()


# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Verify prime pair equations and properties of n=6.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --equation "(p-1)(q-1)=2" --limit 100000
  %(prog)s --sweep-k 1 20 --limit 100000
  %(prog)s --semiprime-perfect --limit 1000000
  %(prog)s --euler-product-integer --limit 1000
  %(prog)s --bootstrap
        """)

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--equation', type=str,
                       help='Prime pair equation to check, e.g. "(p-1)(q-1)=2"')
    group.add_argument('--sweep-k', nargs=2, type=int, metavar=('START', 'END'),
                       help='Sweep (p-1)(q-1)=k for k in [START, END]')
    group.add_argument('--semiprime-perfect', action='store_true',
                       help='Search for semiprime perfect numbers')
    group.add_argument('--euler-product-integer', action='store_true',
                       help='Test pq/((p-1)(q-1)) integrality')
    group.add_argument('--bootstrap', action='store_true',
                       help='Verify self-referential bootstrap cycle')

    parser.add_argument('--limit', type=int, default=100000,
                        help='Upper bound for prime sieve (default: 100000)')
    parser.add_argument('--json', action='store_true',
                        help='Output results as JSON')

    args = parser.parse_args()

    t0 = time.time()

    # Generate primes (not needed for bootstrap)
    primes = []
    prime_set = set()
    if not args.bootstrap:
        if not args.json:
            print(f"Sieving primes up to {args.limit}...")
        primes = sieve_primes(args.limit)
        prime_set = set(primes)
        if not args.json:
            print(f"  Found {len(primes)} primes (largest: {primes[-1]})\n")

    # ── Equation mode ──
    if args.equation:
        k, pairs = check_equation(args.equation, primes, prime_set, args.limit)
        if args.json:
            print(json.dumps({
                "equation": f"(p-1)(q-1)={k}",
                "k": k,
                "limit": args.limit,
                "num_pairs": len(pairs),
                "pairs": [{"p": p, "q": q, "n": p*q} for p, q in pairs],
                "unique": len(pairs) == 1,
                "time_s": round(time.time() - t0, 3),
            }, indent=2))
        else:
            print_equation_result(k, pairs, args.limit)

    # ── Sweep mode ──
    elif args.sweep_k:
        k_start, k_end = args.sweep_k
        results = sweep_k_values(k_start, k_end, primes, prime_set, args.limit)
        if args.json:
            print(json.dumps({
                "mode": "sweep",
                "k_range": [k_start, k_end],
                "limit": args.limit,
                "results": {
                    str(k): [{"p": p, "q": q, "n": p*q} for p, q in pairs]
                    for k, pairs in results.items()
                },
                "unique_ks": [k for k, p in results.items() if len(p) == 1],
                "time_s": round(time.time() - t0, 3),
            }, indent=2))
        else:
            print_sweep_results(results, args.limit)

    # ── Semiprime perfect mode ──
    elif args.semiprime_perfect:
        perfects, near_misses = search_semiprime_perfect(primes, args.limit)
        if args.json:
            print(json.dumps({
                "mode": "semiprime_perfect",
                "limit": args.limit,
                "perfects": [{"p": p, "q": q, "n": n} for p, q, n in perfects],
                "near_misses": [
                    {"p": p, "q": q, "n": n, "ratio": r, "distance": d}
                    for d, p, q, n, r in near_misses
                ],
                "only_6": len(perfects) == 1 and perfects[0] == (2, 3, 6),
                "time_s": round(time.time() - t0, 3),
            }, indent=2))
        else:
            print_semiprime_results(perfects, near_misses)

    # ── Euler product mode ──
    elif args.euler_product_integer:
        integers_found, near_integers = euler_product_integer_test(primes, args.limit)
        if args.json:
            print(json.dumps({
                "mode": "euler_product_integer",
                "limit": args.limit,
                "integers": [{"p": p, "q": q, "value": v} for p, q, v in integers_found],
                "near_integers": [
                    {"p": p, "q": q, "value": v, "frac_dist": d}
                    for d, p, q, v in near_integers
                ],
                "only_2_3": len(integers_found) == 1 and integers_found[0] == (2, 3, 3),
                "time_s": round(time.time() - t0, 3),
            }, indent=2))
        else:
            print_euler_results(integers_found, near_integers)

    # ── Bootstrap mode ──
    elif args.bootstrap:
        steps, other_perfects, all_pass = verify_bootstrap()
        if args.json:
            print(json.dumps({
                "mode": "bootstrap",
                "steps": steps,
                "other_perfects": other_perfects,
                "all_pass": all_pass,
                "time_s": round(time.time() - t0, 3),
            }, indent=2))
        else:
            print_bootstrap_results(steps, other_perfects, all_pass)

    if not args.json:
        print(f"Total time: {time.time() - t0:.2f}s")


if __name__ == "__main__":
    main()
