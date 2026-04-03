#!/usr/bin/env python3
"""DFS n=6 Identity Miner -- Systematic search for new arithmetic identities unique to n=6

Combines arithmetic functions (sigma, tau, phi, sopfr, omega, rad, etc.)
with operations (+, -, *, /, //, **, %) and tests for n=6 uniqueness.

For each identity found at n=6:
  1. Tests n=28 (next perfect number)
  2. Tests all n in [1, LIMIT] for uniqueness
  3. Estimates Texas Sharpshooter significance

Usage:
  PYTHONPATH=. python3 calc/dfs_n6_identity_miner.py
  PYTHONPATH=. python3 calc/dfs_n6_identity_miner.py --limit 10000
  PYTHONPATH=. python3 calc/dfs_n6_identity_miner.py --limit 5000 --depth 3
"""

import math
import argparse
import sys
import time
from collections import defaultdict
from itertools import combinations_with_replacement, product

# ═══════════════════════════════════════════════════════════════
# Arithmetic function tables (pure Python sieves)
# ═══════════════════════════════════════════════════════════════

def sieve_sigma(limit):
    """Sum of divisors sieve."""
    s = [0] * (limit + 1)
    for d in range(1, limit + 1):
        for m in range(d, limit + 1, d):
            s[m] += d
    return s

def sieve_tau(limit):
    """Number of divisors sieve."""
    t = [0] * (limit + 1)
    for d in range(1, limit + 1):
        for m in range(d, limit + 1, d):
            t[m] += 1
    return t

def sieve_phi(limit):
    """Euler's totient sieve."""
    p = list(range(limit + 1))
    for i in range(2, limit + 1):
        if p[i] == i:  # i is prime
            for j in range(i, limit + 1, i):
                p[j] = p[j] // i * (i - 1)
    return p

def sieve_sopfr(limit):
    """Sum of prime factors with repetition."""
    s = [0] * (limit + 1)
    # First find smallest prime factor
    spf = list(range(limit + 1))
    for i in range(2, int(limit**0.5) + 1):
        if spf[i] == i:  # prime
            for j in range(i*i, limit + 1, i):
                if spf[j] == j:
                    spf[j] = i
    for n in range(2, limit + 1):
        m = n
        while m > 1:
            p = spf[m]
            s[n] += p
            m //= p
    return s

def sieve_omega(limit):
    """Number of distinct prime factors."""
    w = [0] * (limit + 1)
    for p in range(2, limit + 1):
        if w[p] == 0:  # p is prime (not yet incremented)
            # Actually omega counts distinct prime factors, not primality
            pass
    # Redo properly
    w = [0] * (limit + 1)
    is_prime = [True] * (limit + 1)
    for p in range(2, limit + 1):
        if is_prime[p]:
            for m in range(p, limit + 1, p):
                w[m] += 1
                if m > p:
                    is_prime[m] = False  # not needed for omega but doesn't hurt
    # Fix: is_prime sieve interferes. Redo cleanly.
    w = [0] * (limit + 1)
    for p in range(2, limit + 1):
        # Check if p is prime by seeing if it has no factor <= sqrt(p)
        pass
    # Simple correct approach
    w = [0] * (limit + 1)
    for p in range(2, limit + 1):
        if all(p % d != 0 for d in range(2, int(p**0.5) + 1)):
            # p is prime
            for m in range(p, limit + 1, p):
                w[m] += 1
    return w

def sieve_Omega(limit):
    """Number of prime factors with repetition."""
    O = [0] * (limit + 1)
    spf = list(range(limit + 1))
    for i in range(2, int(limit**0.5) + 1):
        if spf[i] == i:
            for j in range(i*i, limit + 1, i):
                if spf[j] == j:
                    spf[j] = i
    for n in range(2, limit + 1):
        m = n
        while m > 1:
            O[n] += 1
            m //= spf[m]
    return O

def sieve_rad(limit):
    """Radical (product of distinct prime factors)."""
    r = [1] * (limit + 1)
    r[0] = 0
    spf = list(range(limit + 1))
    for i in range(2, int(limit**0.5) + 1):
        if spf[i] == i:
            for j in range(i*i, limit + 1, i):
                if spf[j] == j:
                    spf[j] = i
    for n in range(2, limit + 1):
        m = n
        seen = set()
        while m > 1:
            p = spf[m]
            if p not in seen:
                r[n] *= p
                seen.add(p)
            m //= p
    return r

def sieve_aliquot(limit, sigma):
    """Aliquot sum s(n) = sigma(n) - n."""
    return [sigma[i] - i if i > 0 else 0 for i in range(limit + 1)]

def harmonic_divisor_sum(n):
    """H(n) = sum of 1/d for d | n."""
    s = 0
    for d in range(1, n + 1):
        if n % d == 0:
            s += 1.0 / d
    return s

def build_all_tables(limit):
    """Build all arithmetic function tables."""
    print(f"  Building sieve tables up to n={limit}...", flush=True)
    t0 = time.time()
    sigma = sieve_sigma(limit)
    tau = sieve_tau(limit)
    phi = sieve_phi(limit)
    sopfr = sieve_sopfr(limit)
    omega = sieve_omega(limit)
    Omega = sieve_Omega(limit)
    rad = sieve_rad(limit)
    aliq = sieve_aliquot(limit, sigma)
    t1 = time.time()
    print(f"  Done in {t1-t0:.1f}s", flush=True)
    return {
        'sigma': sigma,
        'tau': tau,
        'phi': phi,
        'sopfr': sopfr,
        'omega': omega,
        'Omega': Omega,
        'rad': rad,
        'aliq': aliq,
    }


# ═══════════════════════════════════════════════════════════════
# Identity templates -- systematic generation
# ═══════════════════════════════════════════════════════════════

# Function names for expressions
FUNC_NAMES = ['n', 'sigma', 'tau', 'phi', 'sopfr', 'omega', 'Omega', 'rad', 'aliq']

def get_val(name, n, T):
    """Get value of named function at n."""
    if name == 'n':
        return n
    return T[name][n]


def generate_binary_identities():
    """Generate all a OP b == c OP d patterns.

    Forms tested:
      a*b == c*d    (multiplicative)
      a+b == c+d    (additive)
      a+b == c      (sum)
      a*b == c      (product)
      a-b == c      (difference)
      a == c^2      (square)
      a^b == c      (power, small b)
      a*b+c == d    (linear combo)
      a*b-c == d
      a*(b+c) == d
      a*(b-c) == d
      a*b == c+d
      a*b == c*d + e  (off by one func)
      n^a == b*c    (power of n)
    """
    templates = []

    # Type 1: a*b == c*d  (4-func multiplicative)
    for (a, b) in combinations_with_replacement(FUNC_NAMES, 2):
        for (c, d) in combinations_with_replacement(FUNC_NAMES, 2):
            if (a, b) >= (c, d):
                continue
            templates.append({
                'name': f'{a}*{b} == {c}*{d}',
                'lhs': lambda n, T, a=a, b=b: get_val(a, n, T) * get_val(b, n, T),
                'rhs': lambda n, T, c=c, d=d: get_val(c, n, T) * get_val(d, n, T),
            })

    # Type 2: a+b == c  (2-func sum equals 1-func)
    for (a, b) in combinations_with_replacement(FUNC_NAMES, 2):
        for c in FUNC_NAMES:
            if a == b == c:
                continue
            templates.append({
                'name': f'{a}+{b} == {c}',
                'lhs': lambda n, T, a=a, b=b: get_val(a, n, T) + get_val(b, n, T),
                'rhs': lambda n, T, c=c: get_val(c, n, T),
            })

    # Type 3: a-b == c  (difference)
    for a in FUNC_NAMES:
        for b in FUNC_NAMES:
            if a == b:
                continue
            for c in FUNC_NAMES:
                if c in (a, b) and len(set([a,b,c])) < 3:
                    continue
                templates.append({
                    'name': f'{a}-{b} == {c}',
                    'lhs': lambda n, T, a=a, b=b: get_val(a, n, T) - get_val(b, n, T),
                    'rhs': lambda n, T, c=c: get_val(c, n, T),
                })

    # Type 4: a*b == c  (product equals single)
    for (a, b) in combinations_with_replacement(FUNC_NAMES, 2):
        for c in FUNC_NAMES:
            templates.append({
                'name': f'{a}*{b} == {c}',
                'lhs': lambda n, T, a=a, b=b: get_val(a, n, T) * get_val(b, n, T),
                'rhs': lambda n, T, c=c: get_val(c, n, T),
            })

    # Type 5: a+b == c+d  (4-func additive)
    for (a, b) in combinations_with_replacement(FUNC_NAMES, 2):
        for (c, d) in combinations_with_replacement(FUNC_NAMES, 2):
            if (a, b) >= (c, d):
                continue
            templates.append({
                'name': f'{a}+{b} == {c}+{d}',
                'lhs': lambda n, T, a=a, b=b: get_val(a, n, T) + get_val(b, n, T),
                'rhs': lambda n, T, c=c, d=d: get_val(c, n, T) + get_val(d, n, T),
            })

    # Type 6: a*b+c == d  (linear combo)
    for (a, b) in combinations_with_replacement(FUNC_NAMES, 2):
        for c in FUNC_NAMES:
            for d in FUNC_NAMES:
                templates.append({
                    'name': f'{a}*{b}+{c} == {d}',
                    'lhs': lambda n, T, a=a, b=b, c=c: get_val(a, n, T) * get_val(b, n, T) + get_val(c, n, T),
                    'rhs': lambda n, T, d=d: get_val(d, n, T),
                })

    # Type 7: a*b-c == d
    for (a, b) in combinations_with_replacement(FUNC_NAMES, 2):
        for c in FUNC_NAMES:
            for d in FUNC_NAMES:
                if d == c:
                    continue
                templates.append({
                    'name': f'{a}*{b}-{c} == {d}',
                    'lhs': lambda n, T, a=a, b=b, c=c: get_val(a, n, T) * get_val(b, n, T) - get_val(c, n, T),
                    'rhs': lambda n, T, d=d: get_val(d, n, T),
                })

    # Type 8: a*b == c+d  (product = sum)
    for (a, b) in combinations_with_replacement(FUNC_NAMES, 2):
        for (c, d) in combinations_with_replacement(FUNC_NAMES, 2):
            templates.append({
                'name': f'{a}*{b} == {c}+{d}',
                'lhs': lambda n, T, a=a, b=b: get_val(a, n, T) * get_val(b, n, T),
                'rhs': lambda n, T, c=c, d=d: get_val(c, n, T) + get_val(d, n, T),
            })

    # Type 9: a^2 == b*c  (square identity)
    for a in FUNC_NAMES:
        for (b, c) in combinations_with_replacement(FUNC_NAMES, 2):
            templates.append({
                'name': f'{a}^2 == {b}*{c}',
                'lhs': lambda n, T, a=a: get_val(a, n, T) ** 2,
                'rhs': lambda n, T, b=b, c=c: get_val(b, n, T) * get_val(c, n, T),
            })

    # Type 10: a*(b+c) == d  (distributed)
    for a in FUNC_NAMES:
        for (b, c) in combinations_with_replacement(FUNC_NAMES, 2):
            if b == c:
                continue
            for d in FUNC_NAMES:
                templates.append({
                    'name': f'{a}*({b}+{c}) == {d}',
                    'lhs': lambda n, T, a=a, b=b, c=c: get_val(a, n, T) * (get_val(b, n, T) + get_val(c, n, T)),
                    'rhs': lambda n, T, d=d: get_val(d, n, T),
                })

    # Type 11: a*(b-c) == d
    for a in FUNC_NAMES:
        for b in FUNC_NAMES:
            for c in FUNC_NAMES:
                if b == c:
                    continue
                for d in FUNC_NAMES:
                    templates.append({
                        'name': f'{a}*({b}-{c}) == {d}',
                        'lhs': lambda n, T, a=a, b=b, c=c: get_val(a, n, T) * (get_val(b, n, T) - get_val(c, n, T)),
                        'rhs': lambda n, T, d=d: get_val(d, n, T),
                    })

    # Type 12: a*b*c == d  (triple product)
    for (a, b, c) in combinations_with_replacement(FUNC_NAMES, 3):
        for d in FUNC_NAMES:
            templates.append({
                'name': f'{a}*{b}*{c} == {d}',
                'lhs': lambda n, T, a=a, b=b, c=c: get_val(a, n, T) * get_val(b, n, T) * get_val(c, n, T),
                'rhs': lambda n, T, d=d: get_val(d, n, T),
            })

    # Type 13: a*b*c == d*e  (triple vs double product)
    for (a, b, c) in combinations_with_replacement(FUNC_NAMES, 3):
        for (d, e) in combinations_with_replacement(FUNC_NAMES, 2):
            templates.append({
                'name': f'{a}*{b}*{c} == {d}*{e}',
                'lhs': lambda n, T, a=a, b=b, c=c: get_val(a, n, T) * get_val(b, n, T) * get_val(c, n, T),
                'rhs': lambda n, T, d=d, e=e: get_val(d, n, T) * get_val(e, n, T),
            })

    # Type 14: Integer constant identities -- a OP b == K (small integer)
    for (a, b) in combinations_with_replacement(FUNC_NAMES, 2):
        for K in range(1, 61):
            templates.append({
                'name': f'{a}*{b} == {K}',
                'lhs': lambda n, T, a=a, b=b: get_val(a, n, T) * get_val(b, n, T),
                'rhs': lambda n, T, K=K: K,
            })
            templates.append({
                'name': f'{a}+{b} == {K}',
                'lhs': lambda n, T, a=a, b=b: get_val(a, n, T) + get_val(b, n, T),
                'rhs': lambda n, T, K=K: K,
            })

    # Type 15: a/b == K (integer ratio)
    for a in FUNC_NAMES:
        for b in FUNC_NAMES:
            if a == b:
                continue
            for K in range(1, 13):
                templates.append({
                    'name': f'{a}/{b} == {K}',
                    'lhs': lambda n, T, a=a, b=b: get_val(a, n, T),
                    'rhs': lambda n, T, b=b, K=K: get_val(b, n, T) * K,
                })

    # Type 16: Factorial/triangular connections
    # n! == a*b*c (factorial equals product of 3 functions)
    for (a, b, c) in combinations_with_replacement(FUNC_NAMES, 3):
        templates.append({
            'name': f'n! == {a}*{b}*{c}',
            'lhs': lambda n, T: math.factorial(min(n, 20)),  # cap at 20 to avoid overflow
            'rhs': lambda n, T, a=a, b=b, c=c: get_val(a, n, T) * get_val(b, n, T) * get_val(c, n, T),
        })

    return templates


def generate_ratio_identities():
    """Generate ratio-based identities: a/b == c/d, etc."""
    templates = []

    # a/b == c/d  (cross-multiply to avoid division: a*d == b*c)
    func_no_zero = [f for f in FUNC_NAMES if f != 'aliq']  # aliq can be 0
    for (a, b) in product(func_no_zero, repeat=2):
        if a == b:
            continue
        for (c, d) in product(func_no_zero, repeat=2):
            if c == d:
                continue
            if (a, b) >= (c, d):
                continue
            templates.append({
                'name': f'{a}/{b} == {c}/{d}',
                'lhs': lambda n, T, a=a, d=d: get_val(a, n, T) * get_val(d, n, T),
                'rhs': lambda n, T, b=b, c=c: get_val(b, n, T) * get_val(c, n, T),
            })

    return templates


# ═══════════════════════════════════════════════════════════════
# Testing engine
# ═══════════════════════════════════════════════════════════════

def test_identity_at_n(template, n, T):
    """Test if identity holds at n. Returns True/False."""
    try:
        lhs = template['lhs'](n, T)
        rhs = template['rhs'](n, T)
        if lhs is None or rhs is None:
            return False
        return lhs == rhs and lhs != 0  # exclude trivial 0==0
    except (ZeroDivisionError, OverflowError, ValueError, IndexError):
        return False

def find_all_hits(template, T, limit):
    """Find all n in [2, limit] where identity holds."""
    hits = []
    for n in range(2, limit + 1):
        if test_identity_at_n(template, n, T):
            hits.append(n)
    return hits

def check_n28(template, T):
    """Check if identity also holds for n=28."""
    if 28 > len(T['sigma']) - 1:
        return None
    return test_identity_at_n(template, 28, T)


# ═══════════════════════════════════════════════════════════════
# Texas Sharpshooter p-value estimation
# ═══════════════════════════════════════════════════════════════

def texas_pvalue(n_hits, limit, n_templates):
    """Estimate p-value with Bonferroni correction.

    p_single = n_hits / limit  (probability of random hit)
    p_bonferroni = p_single * n_templates  (correct for multiple testing)
    """
    if limit <= 0:
        return 1.0
    p_single = n_hits / limit
    p_bonferroni = min(1.0, p_single * n_templates)
    return p_bonferroni


def grade_identity(hits, limit, n_templates, holds_n28):
    """Assign grade based on verification.

    Returns: emoji grade, description
    """
    if 6 not in hits:
        return None, "MISS"

    unique_to_6 = (hits == [6])
    only_6_and_1 = sorted(hits) in ([6], [1, 6])

    n_hits = len(hits)
    p_val = texas_pvalue(n_hits, limit, n_templates)

    if unique_to_6:
        if holds_n28 is False:
            return "EXACT_UNIQUE", f"UNIQUE to n=6 only (n<={limit}), NOT n=28 => structurally special"
        elif holds_n28 is True:
            return "EXACT_PERFECT", f"Holds for n=6 AND n=28 => perfect number property"
        else:
            return "EXACT_UNIQUE", f"UNIQUE to n=6 only (n<={limit})"
    elif only_6_and_1:
        return "NEAR_UNIQUE", f"Only n=1,6 (n<={limit})"
    elif n_hits <= 3:
        return "RARE", f"Rare ({n_hits} hits in [2,{limit}])"
    elif p_val < 0.01:
        return "STRUCTURAL", f"p={p_val:.4f} < 0.01 (structural)"
    elif p_val < 0.05:
        return "WEAK", f"p={p_val:.4f} < 0.05 (weak evidence)"
    else:
        return "COMMON", f"p={p_val:.4f} (coincidence)"


# ═══════════════════════════════════════════════════════════════
# Deduplication
# ═══════════════════════════════════════════════════════════════

def is_trivial(name):
    """Filter out trivially true identities."""
    # a*a == a*a type
    parts = name.split(' == ')
    if len(parts) == 2 and parts[0].strip() == parts[1].strip():
        return True
    # n*n == n*n
    if 'n*n == n*n' in name:
        return True
    return False

def hits_signature(hits):
    """Create a hashable signature from hits list for dedup."""
    return tuple(sorted(hits))


# ═══════════════════════════════════════════════════════════════
# Known identities to skip (already discovered)
# ═══════════════════════════════════════════════════════════════

KNOWN_NAMES = {
    'phi*sigma == n*tau',
    'sigma == 2*n',  # perfect number definition
    '3*n-6 == sigma',  # 3n-6 = sigma
    'n-2 == tau',  # n-2 = tau
    'sigma-tau == phi*tau',  # tau*phi = sigma - tau
    'sopfr+phi == n+tau',  # rearrangement
}

def is_known(name):
    """Check if this identity is already known."""
    # Normalize
    norm = name.replace(' ', '')
    for k in KNOWN_NAMES:
        if k.replace(' ', '') == norm:
            return True
    return False


# ═══════════════════════════════════════════════════════════════
# Main mining engine
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="DFS n=6 Identity Miner")
    parser.add_argument("--limit", type=int, default=5000, help="Search limit (default: 5000)")
    parser.add_argument("--verbose", action="store_true", help="Print all tested templates")
    args = parser.parse_args()

    limit = args.limit

    print()
    print("  ================================================================")
    print("  DFS n=6 Identity Miner -- Systematic Search")
    print(f"  Search limit: n <= {limit}")
    print("  Functions: n, sigma, tau, phi, sopfr, omega, Omega, rad, aliq")
    print("  ================================================================")
    print()

    # Build tables
    T = build_all_tables(limit)

    # Verify known values at n=6
    print(f"  n=6 values: sigma={T['sigma'][6]}, tau={T['tau'][6]}, phi={T['phi'][6]}, "
          f"sopfr={T['sopfr'][6]}, omega={T['omega'][6]}, Omega={T['Omega'][6]}, "
          f"rad={T['rad'][6]}, aliq={T['aliq'][6]}")
    print()

    # Generate templates
    print("  Generating identity templates...", flush=True)
    t0 = time.time()
    templates = generate_binary_identities()
    ratio_templates = generate_ratio_identities()
    templates.extend(ratio_templates)
    t1 = time.time()
    print(f"  Generated {len(templates):,} templates in {t1-t0:.1f}s")
    print()

    # Phase 1: Quick filter -- only test at n=6 first
    print("  Phase 1: Testing all templates at n=6...", flush=True)
    t0 = time.time()
    n6_hits = []
    for i, tmpl in enumerate(templates):
        if is_trivial(tmpl['name']):
            continue
        if test_identity_at_n(tmpl, 6, T):
            n6_hits.append(tmpl)
    t1 = time.time()
    print(f"  {len(n6_hits):,} templates pass at n=6 (from {len(templates):,}) in {t1-t0:.1f}s")
    print()

    # Phase 2: Full uniqueness scan for n=6 hits
    print(f"  Phase 2: Full uniqueness scan [2, {limit}] for {len(n6_hits):,} candidates...", flush=True)
    t0 = time.time()

    results = []
    seen_signatures = set()

    for i, tmpl in enumerate(n6_hits):
        if (i + 1) % 500 == 0:
            print(f"    ... {i+1}/{len(n6_hits)}", flush=True)

        hits = find_all_hits(tmpl, T, limit)
        sig = hits_signature(hits)

        # Skip if we've seen this exact hit pattern
        if sig in seen_signatures:
            continue
        seen_signatures.add(sig)

        # Skip if known
        if is_known(tmpl['name']):
            continue

        holds_28 = check_n28(tmpl, T)
        grade, desc = grade_identity(hits, limit, len(templates), holds_28)

        if grade is None:
            continue

        results.append({
            'name': tmpl['name'],
            'hits': hits,
            'n_hits': len(hits),
            'holds_28': holds_28,
            'grade': grade,
            'desc': desc,
            'sig': sig,
        })

    t1 = time.time()
    print(f"  Done in {t1-t0:.1f}s")
    print()

    # Sort: EXACT_UNIQUE first, then by fewest hits
    priority = {
        'EXACT_UNIQUE': 0, 'EXACT_PERFECT': 1, 'NEAR_UNIQUE': 2,
        'RARE': 3, 'STRUCTURAL': 4, 'WEAK': 5, 'COMMON': 6,
    }
    results.sort(key=lambda r: (priority.get(r['grade'], 99), r['n_hits']))

    # Deduplicate by hit signature -- keep first (best-named) of each
    final_results = []
    final_sigs = set()
    for r in results:
        if r['sig'] not in final_sigs:
            final_sigs.add(r['sig'])
            final_results.append(r)

    # Report
    print("  ================================================================")
    print("  RESULTS")
    print("  ================================================================")
    print()

    grade_emoji = {
        'EXACT_UNIQUE': '+++',
        'EXACT_PERFECT': '++P',
        'NEAR_UNIQUE': '++ ',
        'RARE': '+  ',
        'STRUCTURAL': '~  ',
        'WEAK': '.  ',
        'COMMON': '   ',
    }

    counts = defaultdict(int)

    # Show top results
    for r in final_results:
        g = r['grade']
        counts[g] += 1

        if g in ('EXACT_UNIQUE', 'EXACT_PERFECT', 'NEAR_UNIQUE', 'RARE'):
            emoji = grade_emoji.get(g, '   ')
            hit_str = str(r['hits'][:15])
            if len(r['hits']) > 15:
                hit_str += f"... ({r['n_hits']} total)"
            n28_str = "YES" if r['holds_28'] else ("NO" if r['holds_28'] is False else "?")
            print(f"  [{emoji}] {r['name']}")
            print(f"         Hits: {hit_str}")
            print(f"         n=28: {n28_str}")
            print(f"         {r['desc']}")
            print()

    # Summary
    print()
    print("  ================================================================")
    print("  SUMMARY")
    print("  ================================================================")
    print()
    print(f"  Templates tested:    {len(templates):,}")
    print(f"  Pass at n=6:         {len(n6_hits):,}")
    print(f"  Unique hit patterns: {len(final_results):,}")
    print()
    for grade_name in ['EXACT_UNIQUE', 'EXACT_PERFECT', 'NEAR_UNIQUE', 'RARE',
                        'STRUCTURAL', 'WEAK', 'COMMON']:
        if counts[grade_name] > 0:
            print(f"  {grade_emoji.get(grade_name, '   ')} {grade_name:<15}: {counts[grade_name]}")
    print()

    # List all EXACT_UNIQUE for easy copy
    uniques = [r for r in final_results if r['grade'] in ('EXACT_UNIQUE', 'EXACT_PERFECT')]
    if uniques:
        print("  ================================================================")
        print("  UNIQUE TO n=6 (candidates for new constant map entries)")
        print("  ================================================================")
        print()
        for i, r in enumerate(uniques, 1):
            n28_str = "ALSO n=28" if r['holds_28'] else "NOT n=28"
            print(f"  {i:3d}. {r['name']:<50} [{n28_str}]")
        print()
        print(f"  Total unique: {len(uniques)}")

    near = [r for r in final_results if r['grade'] == 'NEAR_UNIQUE']
    if near:
        print()
        print("  ================================================================")
        print("  NEAR-UNIQUE (n=1,6 only)")
        print("  ================================================================")
        print()
        for i, r in enumerate(near, 1):
            n28_str = "ALSO n=28" if r['holds_28'] else "NOT n=28"
            print(f"  {i:3d}. {r['name']:<50} [{n28_str}]")
        print()
        print(f"  Total near-unique: {len(near)}")

    rare = [r for r in final_results if r['grade'] == 'RARE']
    if rare:
        print()
        print("  ================================================================")
        print("  RARE (2-3 hits)")
        print("  ================================================================")
        print()
        for i, r in enumerate(rare, 1):
            print(f"  {i:3d}. {r['name']:<50} hits={r['hits']}")
        print()
        print(f"  Total rare: {len(rare)}")

    print()
    print("  Done.")


if __name__ == "__main__":
    main()
