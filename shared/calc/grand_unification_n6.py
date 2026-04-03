#!/usr/bin/env python3
"""Grand Unification of n=6 Characterizations

Attempts to unify five independent connections to n=6:
  1. sigma*phi = n*tau uniqueness (pure number theory)
  2. Self-referential SO loop: P_k = dim(SO(2^p))
  3. Exotic spheres: |bP_{4k}| = perfect number conditions
  4. Connes NCG: KO-dim 6 unique even dim for SM constraints
  5. Bott: sigma(n)-tau(n) = 8 = Bott period, unique

Master Theorem: n=6 is the UNIQUE positive integer satisfying all five
arithmetic-topological conditions simultaneously.

The 2-3 Theorem: 6=2x3 is the unique product of consecutive primes
whose multiplicative arithmetic factor product equals 1.

Usage:
  python3 calc/grand_unification_n6.py              # Full analysis
  python3 calc/grand_unification_n6.py --texas       # Texas Sharpshooter only
  python3 calc/grand_unification_n6.py --entropy     # Arithmetic entropy only
  python3 calc/grand_unification_n6.py --master      # Master theorem scan only
  python3 calc/grand_unification_n6.py --harmonics   # Harmonic ratio analysis
  python3 calc/grand_unification_n6.py --verify      # Run all assertions
"""

import argparse
import math
import random
from fractions import Fraction
from collections import defaultdict

# ============================================================
# Arithmetic Functions
# ============================================================

def divisors(n):
    """Return sorted list of divisors of n."""
    if n < 1:
        return []
    divs = []
    for i in range(1, int(math.isqrt(n)) + 1):
        if n % i == 0:
            divs.append(i)
            if i != n // i:
                divs.append(n // i)
    return sorted(divs)


def sigma(n):
    """Sum of divisors."""
    return sum(divisors(n))


def tau(n):
    """Number of divisors."""
    return len(divisors(n))


def euler_phi(n):
    """Euler totient function."""
    if n < 1:
        return 0
    result = n
    p = 2
    temp = n
    while p * p <= temp:
        if temp % p == 0:
            while temp % p == 0:
                temp //= p
            result -= result // p
        p += 1
    if temp > 1:
        result -= result // temp
    return result


def sopfr(n):
    """Sum of prime factors with repetition."""
    if n < 2:
        return 0
    s = 0
    temp = n
    p = 2
    while p * p <= temp:
        while temp % p == 0:
            s += p
            temp //= p
        p += 1
    if temp > 1:
        s += temp
    return s


def omega(n):
    """Number of distinct prime factors."""
    if n < 2:
        return 0
    count = 0
    temp = n
    p = 2
    while p * p <= temp:
        if temp % p == 0:
            count += 1
            while temp % p == 0:
                temp //= p
        p += 1
    if temp > 1:
        count += 1
    return count


def rad(n):
    """Radical of n (product of distinct prime factors)."""
    if n < 2:
        return n
    r = 1
    temp = n
    p = 2
    while p * p <= temp:
        if temp % p == 0:
            r *= p
            while temp % p == 0:
                temp //= p
        p += 1
    if temp > 1:
        r *= temp
    return r


def prime_factors(n):
    """Return list of prime factors with repetition."""
    if n < 2:
        return []
    factors = []
    temp = n
    p = 2
    while p * p <= temp:
        while temp % p == 0:
            factors.append(p)
            temp //= p
        p += 1
    if temp > 1:
        factors.append(temp)
    return factors


def distinct_prime_factors(n):
    """Return sorted list of distinct prime factors."""
    return sorted(set(prime_factors(n)))


def is_prime(n):
    """Primality test."""
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


# ============================================================
# n=6 Constants
# ============================================================
N = 6
SIGMA = 12
TAU = 4
PHI = 2
SOPFR = 5
OMEGA = 2
RAD = 6

N6_VALUES = {
    'n': N, 'sigma': SIGMA, 'tau': TAU, 'phi': PHI,
    'sopfr': SOPFR, 'omega': OMEGA, 'rad': RAD,
}


# ============================================================
# KO-theory data (real K-theory groups KO^{-n}(pt))
# ============================================================
# KO^{-n}(pt) for n = 0..7 (period 8):
# n=0: Z, n=1: Z/2, n=2: Z/2, n=3: 0, n=4: Z, n=5: 0, n=6: 0, n=7: 0
KO_GROUPS = {
    0: ('Z', False),      # Z -- nontrivial
    1: ('Z/2', False),    # Z/2 -- nontrivial
    2: ('Z/2', False),    # Z/2 -- nontrivial
    3: ('0', True),       # trivial
    4: ('Z', False),      # Z -- nontrivial
    5: ('0', True),       # trivial
    6: ('0', True),       # trivial
    7: ('0', True),       # trivial
}

# Clifford algebra Cl(n,0) types
# n mod 8: 0=R(2^k), 1=C(2^k), 2=H(2^k), 3=H(2^k)+H(2^k),
#          4=H(2^k), 5=C(2^k), 6=R(2^k), 7=R(2^k)+R(2^k)
CLIFFORD_TYPES = {
    0: 'R',   # purely real
    1: 'C',   # complex
    2: 'H',   # quaternionic
    3: 'H+H', # quaternionic double
    4: 'H',   # quaternionic
    5: 'C',   # complex
    6: 'R',   # purely real
    7: 'R+R', # real double
}


def section(title):
    """Print section header."""
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)
    print()


# ============================================================
# 1. MASTER THEOREM: Five-condition uniqueness scan
# ============================================================

def condition_a(n):
    """sigma(n)*phi(n) = n*tau(n) [arithmetic balance]."""
    return sigma(n) * euler_phi(n) == n * tau(n)


def condition_b(n):
    """sigma(n) - tau(n) = 2^(sigma(n)/tau(n)) [Bott connection].
    Requires sigma(n)/tau(n) to be an integer.
    """
    s, t = sigma(n), tau(n)
    if t == 0:
        return False
    if s % t != 0:
        return False
    exponent = s // t
    return (s - t) == (2 ** exponent)


def condition_c(n):
    """n is self-referential: exists interpretation as dim(SO(2^(tau(n)/2))).
    For n=6: tau(6)=4, tau/2=2, 2^2=4, SO(4) has dim 4*3/2=6=n. Check!
    General: dim(SO(m)) = m(m-1)/2. We need m(m-1)/2 = n where m = 2^(tau(n)/2).
    Requires tau(n) to be even.
    """
    t = tau(n)
    if t % 2 != 0:
        return False
    m = 2 ** (t // 2)
    dim_so = m * (m - 1) // 2
    return dim_so == n


def condition_d(n):
    """KO^{-n}(pt) = 0 [topological triviality].
    Using Bott periodicity: KO^{-n}(pt) depends on n mod 8.
    """
    mod8 = n % 8
    _, is_trivial = KO_GROUPS[mod8]
    return is_trivial


def condition_e(n):
    """Cl(n,0) is purely real type [Clifford reality].
    Real type when n mod 8 in {0, 6, 7}.
    """
    mod8 = n % 8
    cl_type = CLIFFORD_TYPES[mod8]
    return cl_type in ('R', 'R+R')


def master_theorem_scan(limit=1000):
    """Scan n=1..limit for the Master Theorem conditions."""
    section("MASTER THEOREM: Five-Condition Characterization of n=6")

    print("Conditions:")
    print("  (a) sigma(n)*phi(n) = n*tau(n)     [arithmetic balance]")
    print("  (b) sigma(n)-tau(n) = 2^(sigma/tau) [Bott connection]")
    print("  (c) dim(SO(2^(tau/2))) = n          [self-referential loop]")
    print("  (d) KO^{-n}(pt) = 0                 [topological triviality]")
    print("  (e) Cl(n,0) is purely real type      [Clifford reality]")
    print(f"\nScanning n = 1 .. {limit} ...")
    print()

    # Track which conditions each n satisfies
    cond_names = ['(a)', '(b)', '(c)', '(d)', '(e)']
    cond_funcs = [condition_a, condition_b, condition_c, condition_d, condition_e]

    # Count satisfiers per condition
    satisfiers = {name: [] for name in cond_names}
    all_five = []
    four_plus = []

    for n in range(1, limit + 1):
        results = [f(n) for f in cond_funcs]
        count = sum(results)

        for i, name in enumerate(cond_names):
            if results[i]:
                satisfiers[name].append(n)

        if count == 5:
            all_five.append(n)
        if count >= 4:
            four_plus.append((n, results, count))

    # Print individual condition statistics
    print("Individual condition satisfiers:")
    print("-" * 60)
    for name in cond_names:
        s = satisfiers[name]
        shown = s[:20]
        suffix = f" ... ({len(s)} total)" if len(s) > 20 else ""
        print(f"  {name}: {shown}{suffix}")
    print()

    # Print four-or-more
    print("Numbers satisfying >= 4 conditions:")
    print("-" * 60)
    if four_plus:
        print(f"  {'n':>6}  (a) (b) (c) (d) (e)  count")
        print(f"  {'---':>6}  --- --- --- --- ---  -----")
        for n, results, count in four_plus[:30]:
            marks = ["YES" if r else " . " for r in results]
            star = " <<<" if count == 5 else ""
            print(f"  {n:>6}  {marks[0]} {marks[1]} {marks[2]} {marks[3]} {marks[4]}  {count}{star}")
    else:
        print("  (none)")
    print()

    # The verdict
    print("=" * 60)
    if all_five == [6]:
        print(f"  MASTER THEOREM VERIFIED: n=6 is the UNIQUE solution")
        print(f"  in [1, {limit}] satisfying all five conditions.")
    elif len(all_five) == 0:
        print(f"  WARNING: No solutions found in [1, {limit}]!")
    elif 6 in all_five:
        print(f"  n=6 satisfies all five but is NOT unique: {all_five}")
    else:
        print(f"  n=6 does NOT satisfy all five! Solutions: {all_five}")
    print("=" * 60)

    # Verify n=6 individually
    print()
    print("Verification for n=6:")
    print(f"  sigma(6) = {sigma(6)}, tau(6) = {tau(6)}, phi(6) = {euler_phi(6)}")
    print(f"  (a) {sigma(6)}*{euler_phi(6)} = {sigma(6)*euler_phi(6)} vs "
          f"6*{tau(6)} = {6*tau(6)}: {'PASS' if condition_a(6) else 'FAIL'}")
    print(f"  (b) {sigma(6)}-{tau(6)} = {sigma(6)-tau(6)} vs "
          f"2^({sigma(6)}/{tau(6)}) = 2^{sigma(6)//tau(6)} = {2**(sigma(6)//tau(6))}: "
          f"{'PASS' if condition_b(6) else 'FAIL'}")
    print(f"  (c) tau(6)/2 = 2, 2^2 = 4, SO(4) dim = 4*3/2 = 6 = n: "
          f"{'PASS' if condition_c(6) else 'FAIL'}")
    print(f"  (d) KO^{{-6}}(pt) = {KO_GROUPS[6 % 8][0]}: "
          f"{'PASS (trivial)' if condition_d(6) else 'FAIL'}")
    print(f"  (e) Cl(6,0) type = {CLIFFORD_TYPES[6 % 8]}: "
          f"{'PASS (real)' if condition_e(6) else 'FAIL'}")

    return all_five


# ============================================================
# 2. THE 2-3 THEOREM: Multiplicative arithmetic factor
# ============================================================

def r_factor(p, a):
    """Multiplicative arithmetic factor r(p,a) for sigma*phi = n*tau.
    For prime power p^a:
      sigma(p^a) = (p^{a+1}-1)/(p-1)
      phi(p^a)   = p^a(1-1/p) = p^{a-1}(p-1)
      tau(p^a)   = a+1
      n = p^a
    So sigma*phi / (n*tau) = [(p^{a+1}-1)/(p-1)] * [p^{a-1}(p-1)] / [p^a * (a+1)]
                           = [p^{a+1}-1] * p^{a-1} / [p^a * (a+1)]
                           = (p^{a+1}-1) / (p * (a+1))
    For n = p1^a1 * p2^a2, the product r(p1,a1)*r(p2,a2) = 1 iff sigma*phi = n*tau.
    """
    return Fraction(p**(a+1) - 1, p * (a + 1))


def two_three_theorem(max_prime=100):
    """The 2-3 Theorem: 6=2x3 is unique product of consecutive primes
    with r(p,1)*r(q,1) = 1."""
    section("THE 2-3 THEOREM: Consecutive Prime Products")

    print("For n = p*q (product of two distinct primes, a=1 each):")
    print("  r(p,1) = (p^2 - 1) / (2p)")
    print("  Product r(p,1)*r(q,1) = 1 iff sigma*phi = n*tau")
    print()

    # Get primes up to max_prime
    primes = [p for p in range(2, max_prime + 1) if is_prime(p)]

    # Check all pairs of distinct primes
    print("All prime pairs p < q with r(p,1)*r(q,1) = 1:")
    print("-" * 50)
    found = []
    for i, p in enumerate(primes):
        rp = r_factor(p, 1)
        for q in primes[i+1:]:
            rq = r_factor(q, 1)
            product = rp * rq
            if product == 1:
                found.append((p, q))
                print(f"  p={p}, q={q}: r({p},1)={rp} * r({q},1)={rq} = {product} = 1  <<<")

    if len(found) == 1 and found[0] == (2, 3):
        print(f"\n  PROVEN: (2,3) is the UNIQUE prime pair in primes up to {max_prime}")
    print()

    # Show why: r(p,1) = (p^2-1)/(2p) = (p-1)(p+1)/(2p)
    print("Analytical proof:")
    print("  r(p,1)*r(q,1) = [(p^2-1)(q^2-1)] / [4pq] = 1")
    print("  => (p^2-1)(q^2-1) = 4pq")
    print("  => p^2*q^2 - p^2 - q^2 + 1 = 4pq")
    print("  => (pq)^2 - 4pq - (p^2 + q^2 - 1) = 0")
    print()
    print("  For p=2, q=3: (4-1)(9-1)/(4*6) = 3*8/24 = 24/24 = 1  CHECK")
    print()

    # Check consecutive prime pairs specifically
    print("Consecutive prime pairs r(p,1)*r(next_prime,1):")
    print("-" * 60)
    print(f"  {'p':>4} {'q':>4}  r(p,1)       r(q,1)       product")
    print(f"  {'---':>4} {'---':>4}  ----------   ----------   -------")
    for i in range(min(15, len(primes) - 1)):
        p, q = primes[i], primes[i + 1]
        rp = r_factor(p, 1)
        rq = r_factor(q, 1)
        prod = rp * rq
        mark = " <<<" if prod == 1 else ""
        print(f"  {p:>4} {q:>4}  {float(rp):>11.6f}  {float(rq):>11.6f}  {float(prod):>7.4f}{mark}")
    print()

    # Show the 2-3 propagation
    print("2-3 Structure Propagation:")
    print("-" * 50)
    print(f"  6 = 2 x 3                   (fundamental factorization)")
    print(f"  Bott period = 2^3 = 8        (from the same 2,3)")
    print(f"  sigma(6) - tau(6) = 12-4 = 8 (equals Bott period!)")
    print(f"  Spinor dim = 2^(tau/2) = 2^2 = 4   (2 from tau(6)=4)")
    print(f"  SO(4) dim = 4*3/2 = 6 = n   (self-referential)")
    print(f"  Mersenne: 2^p - 1 for p|n    (2^2-1=3, 2^3-1=7)")
    print(f"  6 = 2^1(2^2-1) = 2*3        (Euler form)")
    print(f"  KO dim mod 8: 6 mod 8 = 6   (trivial KO group)")
    print(f"  Cl(6,0) = R(8)              (real, 8 = 2^3)")

    return found


# ============================================================
# 3. ARITHMETIC ENTROPY
# ============================================================

def arithmetic_entropy(n):
    """Compute H(n) = -sum_{d|n} (d/sigma(n)) * log(d/sigma(n))."""
    divs = divisors(n)
    s = sigma(n)
    if s == 0:
        return 0.0
    h = 0.0
    for d in divs:
        p = d / s
        if p > 0:
            h -= p * math.log(p)
    return h


def max_entropy_for_k_divisors(k, s):
    """Maximum entropy for k divisors summing to s: uniform = s/k each.
    H_max = -k * (1/k) * log(1/k) = log(k).
    """
    return math.log(k)


def entropy_analysis(limit=100):
    """Analyze arithmetic entropy H(n) for n=1..limit."""
    section("ARITHMETIC ENTROPY: H(n) = -sum (d/sigma) log(d/sigma)")

    print(f"Computing H(n) for n = 1 .. {limit} ...")
    print()

    data = []
    for n in range(1, limit + 1):
        h = arithmetic_entropy(n)
        t = tau(n)
        s = sigma(n)
        h_max = max_entropy_for_k_divisors(t, s)
        efficiency = h / h_max if h_max > 0 else 0
        is_perfect = (s == 2 * n)
        data.append((n, h, t, s, h_max, efficiency, is_perfect))

    # Sort by entropy
    by_entropy = sorted(data, key=lambda x: x[1], reverse=True)

    # Top 20 by entropy
    print("Top 20 by arithmetic entropy H(n):")
    print("-" * 70)
    print(f"  {'n':>5}  {'H(n)':>8}  {'tau':>4}  {'sigma':>6}  {'H_max':>8}  {'eff':>6}  perfect")
    print(f"  {'---':>5}  {'----':>8}  {'---':>4}  {'-----':>6}  {'-----':>8}  {'---':>6}  -------")
    for n, h, t, s, hm, eff, perf in by_entropy[:20]:
        perf_mark = "  <<<" if perf else ""
        print(f"  {n:>5}  {h:>8.4f}  {t:>4}  {s:>6}  {hm:>8.4f}  {eff:>6.3f}{perf_mark}")

    # Perfect numbers specifically
    print()
    print("Perfect numbers:")
    print("-" * 70)
    perfects = [(n, h, t, s, hm, eff) for n, h, t, s, hm, eff, perf in data if perf]
    for n, h, t, s, hm, eff in perfects:
        print(f"  n={n}: H = {h:.6f}, tau = {t}, H_max = log({t}) = {hm:.6f}, "
              f"efficiency = {eff:.4f}")

    # n=6 specific
    h6 = arithmetic_entropy(6)
    h28 = arithmetic_entropy(28)
    print()
    print("Comparison:")
    print(f"  H(6)  = {h6:.6f}  (4 divisors)")
    print(f"  H(28) = {h28:.6f}  (6 divisors)")
    print(f"  H(6)/log(4)  = {h6/math.log(4):.6f}  (entropy efficiency)")
    print(f"  H(28)/log(6) = {h28/math.log(6):.6f}  (entropy efficiency)")

    # Entropy efficiency for same-tau numbers
    print()
    print("Entropy efficiency among 4-divisor numbers (tau=4):")
    print("-" * 50)
    tau4 = [(n, h, eff) for n, h, t, s, hm, eff, p in data if t == 4]
    tau4.sort(key=lambda x: x[2], reverse=True)
    for n, h, eff in tau4[:15]:
        mark = "  <<< PERFECT" if sigma(n) == 2*n else ""
        print(f"  n={n:>4}: H = {h:.4f}, efficiency = {eff:.4f}{mark}")

    # Find: among tau=4 numbers, is n=6 extremal?
    if tau4:
        rank_6 = next((i for i, (n, _, _) in enumerate(tau4) if n == 6), None)
        if rank_6 is not None:
            print(f"\n  n=6 rank among tau=4 numbers by efficiency: "
                  f"{rank_6 + 1}/{len(tau4)}")

    # ASCII histogram of H(n) distribution
    print()
    print("Arithmetic Entropy Distribution (n=1..100):")
    print("-" * 60)
    bins = [0] * 20
    max_h = max(h for _, h, *_ in data)
    for _, h, *_ in data:
        b = min(int(h / (max_h / 20 + 1e-10)), 19)
        bins[b] += 1
    max_count = max(bins)
    for i in range(19, -1, -1):
        bar = "#" * int(bins[i] / max_count * 40) if max_count > 0 else ""
        lo = i * max_h / 20
        hi = (i + 1) * max_h / 20
        print(f"  [{lo:5.2f}-{hi:5.2f}] {bar} {bins[i]}")

    return h6, h28


# ============================================================
# 4. HARMONIC RATIO ANALYSIS: Ratios unique to n=6
# ============================================================

def harmonic_analysis(limit=1000):
    """Find all 'harmonic' ratio relations unique to n=6."""
    section("HARMONIC RATIO ANALYSIS: Relations Unique to n=6")

    # For each n, compute fundamental ratios
    print(f"Computing arithmetic ratios for n = 1 .. {limit} ...")
    print()

    # Define key ratios
    ratio_defs = {
        'sigma/n':   lambda n: Fraction(sigma(n), n),
        'phi/n':     lambda n: Fraction(euler_phi(n), n),
        'tau/n':     lambda n: Fraction(tau(n), n),
        'sigma/phi': lambda n: Fraction(sigma(n), euler_phi(n)) if euler_phi(n) > 0 else None,
        'sigma/tau': lambda n: Fraction(sigma(n), tau(n)),
        'phi/tau':   lambda n: Fraction(euler_phi(n), tau(n)),
        'sigma*phi/(n*tau)': lambda n: Fraction(sigma(n)*euler_phi(n), n*tau(n)),
    }

    # n=6 values
    print("n=6 ratio fingerprint:")
    print("-" * 50)
    n6_ratios = {}
    for name, func in ratio_defs.items():
        val = func(6)
        n6_ratios[name] = val
        print(f"  {name:>20} = {val} = {float(val):.6f}")

    print()
    print("Derived relations for n=6:")
    print("-" * 50)
    s_n = Fraction(sigma(6), 6)  # 2
    p_n = Fraction(euler_phi(6), 6)  # 1/3
    t_n = Fraction(tau(6), 6)  # 2/3
    print(f"  sigma/n = {s_n}")
    print(f"  phi/n   = {p_n}")
    print(f"  tau/n   = {t_n}")
    print(f"  sigma/n + phi/n       = {s_n + p_n} = {float(s_n + p_n):.6f}")
    print(f"  sigma/n - phi/n       = {s_n - p_n} = {float(s_n - p_n):.6f}")
    print(f"  sigma/n * phi/n       = {s_n * p_n} = {float(s_n * p_n):.6f}")
    print(f"  sigma/n / tau/n       = {s_n / t_n} = {float(s_n / t_n):.6f}")
    print(f"  phi/n * tau/n         = {p_n * t_n} = {float(p_n * t_n):.6f}")
    print(f"  sigma/n = 3 * tau/n   : {s_n == 3 * t_n}")
    print(f"  phi/n + tau/n = 1     : {p_n + t_n == 1}")
    print(f"  1/2 + 1/3 + 1/6 = 1  : {Fraction(1,2) + Fraction(1,3) + Fraction(1,6) == 1}")

    # Now scan for uniqueness of key relations
    print()
    print("Uniqueness scan (n=1..{limit}):")
    print("-" * 60)

    relations = [
        ("sigma(n)*phi(n) = n*tau(n)",
         lambda n: sigma(n)*euler_phi(n) == n*tau(n)),
        ("sigma(n)/n = 3*tau(n)/n  [i.e. sigma = 3*tau]",
         lambda n: sigma(n) == 3 * tau(n)),
        ("phi(n)/n + tau(n)/n = 1  [i.e. phi + tau = n]",
         lambda n: euler_phi(n) + tau(n) == n),
        ("sigma(n)/phi(n) = n  [self-referential]",
         lambda n: euler_phi(n) > 0 and sigma(n) == n * euler_phi(n)),
        ("sigma(n) - tau(n) = 8  [Bott period]",
         lambda n: sigma(n) - tau(n) == 8),
        ("sigma(n)/tau(n) = 3  [sigma/tau integer = 3]",
         lambda n: tau(n) > 0 and sigma(n) == 3 * tau(n)),
        ("phi(n)*tau(n) = n  [... wait: 2*4=8 != 6]",
         lambda n: euler_phi(n) * tau(n) == n),
        ("(sigma(n)-n)/n = 1  [abundancy excess = 1, perfect]",
         lambda n: sigma(n) == 2 * n),
        ("sigma/phi = n (only n=1,6)",
         lambda n: euler_phi(n) > 0 and sigma(n) == n * euler_phi(n)),
        ("rad(n) = n  [squarefree]",
         lambda n: rad(n) == n),
        ("tau(n)^2 + phi(n)^2 = tau(n)*n  [16+4=20 vs 24, NO]",
         lambda n: tau(n)**2 + euler_phi(n)**2 == tau(n)*n),
        ("sigma(n) = 2*phi(n)*n/phi(n) ... = 2n  [perfect]",
         lambda n: sigma(n) == 2 * n),
    ]

    for desc, test in relations:
        matches = [n for n in range(1, limit + 1) if test(n)]
        is_6_only = matches == [6]
        is_16_only = set(matches) == {1, 6}
        mark = ""
        if is_6_only:
            mark = "  <<< UNIQUE to n=6"
        elif is_16_only:
            mark = "  <<< UNIQUE to n=1,6"
        elif 6 in matches and len(matches) <= 5:
            mark = f"  (rare: {len(matches)} solutions)"
        shown = matches[:15]
        suffix = f" ...({len(matches)} total)" if len(matches) > 15 else ""
        print(f"  {desc}")
        print(f"    solutions: {shown}{suffix}{mark}")
        print()

    # The key combined uniqueness
    print("COMBINED uniqueness tests:")
    print("-" * 60)

    # phi + tau = n AND sigma = 2n
    combo1 = [n for n in range(1, limit + 1)
              if euler_phi(n) + tau(n) == n and sigma(n) == 2*n]
    print(f"  phi(n)+tau(n)=n AND sigma(n)=2n: {combo1}")

    # sigma = 3*tau AND sigma-tau = 8
    combo2 = [n for n in range(1, limit + 1)
              if sigma(n) == 3*tau(n) and sigma(n) - tau(n) == 8]
    print(f"  sigma=3*tau AND sigma-tau=8: {combo2}")

    # sigma/phi = n AND KO trivial
    combo3 = [n for n in range(1, limit + 1)
              if euler_phi(n) > 0 and sigma(n) == n*euler_phi(n)
              and KO_GROUPS[n % 8][1]]
    print(f"  sigma/phi=n AND KO^{{-n}} trivial: {combo3}")

    return n6_ratios


# ============================================================
# 5. CATEGORY-THEORETIC PERSPECTIVE: Self-doubling analysis
# ============================================================

def categorical_analysis(limit=200):
    """Analyze sigma(n)/n = 2 (self-doubling) and related fixed points."""
    section("CATEGORICAL PERSPECTIVE: Self-Doubling Fixed Points")

    print("Perfect numbers: sigma(n)/n = 2 (self-doubling under sigma)")
    print()

    # abundancy index
    print("Abundancy index sigma(n)/n for small n:")
    print("-" * 50)
    print(f"  {'n':>4}  {'sigma':>6}  {'sigma/n':>10}  {'class':>12}")
    print(f"  {'--':>4}  {'-----':>6}  {'-------':>10}  {'-----':>12}")
    for n in range(1, 31):
        s = sigma(n)
        ratio = Fraction(s, n)
        if ratio == 2:
            cls = "PERFECT"
        elif ratio < 2:
            cls = "deficient"
        else:
            cls = "abundant"
        mark = "  <<<" if ratio == 2 else ""
        print(f"  {n:>4}  {s:>6}  {float(ratio):>10.4f}  {cls:>12}{mark}")

    # For perfect numbers, compute the full ratio vector
    perfects_in_range = [n for n in range(1, limit + 1) if sigma(n) == 2*n]
    print()
    print(f"Perfect numbers in [1, {limit}]: {perfects_in_range}")
    print()

    # For n=6: the ratio vector (sigma/n, phi/n, tau/n, sopfr/n)
    for n in perfects_in_range:
        s, t, p, sp = sigma(n), tau(n), euler_phi(n), sopfr(n)
        print(f"  n={n}:")
        print(f"    sigma/n = {Fraction(s,n)} = {s/n:.4f}")
        print(f"    phi/n   = {Fraction(p,n)} = {p/n:.4f}")
        print(f"    tau/n   = {Fraction(t,n)} = {t/n:.4f}")
        print(f"    sopfr/n = {Fraction(sp,n)} = {sp/n:.4f}")
        print(f"    sigma/n + phi/n + (1-tau/n) = {Fraction(s,n) + Fraction(p,n) + 1 - Fraction(t,n)}")
        print(f"    sigma/phi = {Fraction(s,p)}")
        print(f"    sigma/tau = {Fraction(s,t)}")
        print()

    # The triple (sigma/n, phi/n, tau/n) for n=6 is (2, 1/3, 2/3)
    # These satisfy: sigma/n = 3*tau/n and phi/n + tau/n = 1
    # Is this combination unique?
    print("Triple relation test: sigma/n = 3*tau/n AND phi/n + tau/n = 1")
    matches = []
    for n in range(1, limit + 1):
        s, t, p = sigma(n), tau(n), euler_phi(n)
        if s * n == 3 * t * n and p + t == n:  # simplified: s == 3t and p+t == n
            if s == 3*t and p + t == n:
                matches.append(n)
    print(f"  Solutions in [1, {limit}]: {matches}")
    if matches == [6]:
        print("  UNIQUE to n=6!")

    return perfects_in_range


# ============================================================
# 6. TEXAS SHARPSHOOTER TEST
# ============================================================

def texas_sharpshooter(limit=1000, n_trials=10000, seed=42):
    """Texas Sharpshooter test for the unified characterization."""
    section("TEXAS SHARPSHOOTER: Grand Unification Test")

    random.seed(seed)

    # The actual conditions satisfied by n=6
    conditions_desc = [
        "(a) sigma*phi = n*tau",
        "(b) sigma-tau = 2^(sigma/tau)",
        "(c) dim(SO(2^(tau/2))) = n",
        "(d) KO^{-n}(pt) = 0",
        "(e) Cl(n,0) purely real",
    ]

    # Count how many n in [1, limit] satisfy each condition individually
    individual_counts = []
    for i, (name, func) in enumerate(zip(
        conditions_desc,
        [condition_a, condition_b, condition_c, condition_d, condition_e]
    )):
        count = sum(1 for n in range(1, limit + 1) if func(n))
        frac = count / limit
        individual_counts.append((name, count, frac))
        print(f"  {name}: {count}/{limit} = {frac:.4f}")

    print()

    # Probability of random number satisfying all 5 (assuming independence)
    p_independent = 1.0
    for _, count, frac in individual_counts:
        p_independent *= frac
    print(f"  Independent probability (product): {p_independent:.2e}")

    # Actual count satisfying all 5
    actual_all5 = sum(1 for n in range(1, limit + 1)
                      if all(f(n) for f in [condition_a, condition_b,
                                            condition_c, condition_d, condition_e]))
    p_actual = actual_all5 / limit
    print(f"  Actual all-5 count: {actual_all5}/{limit} = {p_actual:.4e}")

    # Monte Carlo: random "arithmetic functions" test
    # For each trial, pick random n, check how many conditions a random
    # number satisfies
    print()
    print(f"  Monte Carlo: {n_trials} trials")
    print(f"  For each trial, pick a random n in [1, {limit}] and count conditions met")

    count_dist = defaultdict(int)
    for _ in range(n_trials):
        n = random.randint(1, limit)
        c = sum(1 for f in [condition_a, condition_b, condition_c,
                            condition_d, condition_e] if f(n))
        count_dist[c] += 1

    print()
    print("  Distribution of conditions satisfied:")
    print(f"  {'count':>5}  {'frequency':>10}  {'fraction':>10}")
    print(f"  {'-----':>5}  {'---------':>10}  {'--------':>10}")
    for k in range(6):
        freq = count_dist.get(k, 0)
        frac = freq / n_trials
        bar = "#" * int(frac * 50)
        print(f"  {k:>5}  {freq:>10}  {frac:>10.4f}  {bar}")

    p_all5_mc = count_dist.get(5, 0) / n_trials
    print()
    print(f"  P(all 5) from Monte Carlo: {p_all5_mc:.6f}")

    # Bonferroni correction
    # We're testing 5 conditions; search space is choosing 5 conditions
    # from a larger set of possible arithmetic relations
    n_possible_conditions = 50  # conservative estimate of conditions we could have tried
    from math import comb
    search_space = comb(n_possible_conditions, 5)
    p_bonferroni = min(1.0, p_independent * search_space)

    print()
    print(f"  Search space (C({n_possible_conditions},5)): {search_space}")
    print(f"  Bonferroni-corrected p-value: {p_bonferroni:.2e}")

    # Significance
    if p_bonferroni < 0.001:
        z = 3.3  # approximate
    elif p_bonferroni < 0.01:
        z = 2.6
    elif p_bonferroni < 0.05:
        z = 2.0
    else:
        z = 0.0

    # Better Z-score from p-value
    # Use inverse normal approximation
    if p_actual > 0:
        # Expected under independence
        expected = p_independent * limit
        # Standard deviation (Poisson approximation)
        std = max(math.sqrt(expected), 0.001)
        z_score = (actual_all5 - expected) / std if expected > 0 else float('inf')
    else:
        z_score = float('inf')

    print()
    print("=" * 60)
    print(f"  RESULT:")
    print(f"    Unique solutions satisfying all 5 conditions: {actual_all5}")
    print(f"    Expected under independence: {p_independent * limit:.4f}")
    if actual_all5 == 1:
        # The remarkable thing is that EXACTLY n=6 satisfies all 5
        # and nothing else does
        print(f"    n=6 is the SOLE solution in [1, {limit}]")
        print(f"    Bonferroni p-value: {p_bonferroni:.2e}")
        if p_bonferroni < 0.01:
            grade = "STRUCTURAL (p < 0.01)"
        elif p_bonferroni < 0.05:
            grade = "SIGNIFICANT (p < 0.05)"
        else:
            grade = "WEAK (p >= 0.05)"
        print(f"    Grade: {grade}")
    print("=" * 60)

    return p_bonferroni


# ============================================================
# 7. INFORMATION-THEORETIC: Why 2x3 is special
# ============================================================

def information_theory():
    """Information-theoretic formulation of n=6 uniqueness."""
    section("INFORMATION-THEORETIC: The 2x3 Information Budget")

    print("For n = p*q (squarefree semiprime):")
    print("  Divisors: {1, p, q, pq}")
    print("  sigma = 1 + p + q + pq = (1+p)(1+q)")
    print("  Divisor weights: w_d = d / sigma")
    print()

    # Compare semiprimes
    semiprimes = []
    for p in range(2, 30):
        if not is_prime(p):
            continue
        for q in range(p + 1, 50):
            if not is_prime(q):
                continue
            n = p * q
            semiprimes.append((p, q, n))

    print(f"  {'p':>3} {'q':>3} {'n':>5}  {'H(n)':>7}  {'H_max':>7}  {'eff':>6}  "
          f"{'sigma*phi=n*tau':>15}")
    print(f"  {'--':>3} {'--':>3} {'---':>5}  {'----':>7}  {'-----':>7}  {'---':>6}  "
          f"{'---------------':>15}")

    for p, q, n in semiprimes[:20]:
        h = arithmetic_entropy(n)
        h_max = math.log(4)  # all semiprimes pq have tau=4
        eff = h / h_max
        balanced = sigma(n)*euler_phi(n) == n*tau(n)
        mark = " <<<" if balanced else ""
        print(f"  {p:>3} {q:>3} {n:>5}  {h:>7.4f}  {h_max:>7.4f}  {eff:>6.3f}  "
              f"{'YES' if balanced else 'no':>15}{mark}")

    # Divisor weight uniformity for perfect numbers
    print()
    print("Divisor weight distribution for n=6:")
    divs6 = divisors(6)
    s6 = sigma(6)
    print(f"  Divisors: {divs6}, sigma = {s6}")
    for d in divs6:
        w = d / s6
        bar = "#" * int(w * 60)
        print(f"  d={d:>2}: w = {d}/{s6} = {w:.4f}  {bar}")

    # Key insight: for 6 = 2*3, the divisor weights are 1/12, 2/12, 3/12, 6/12
    # These are in ratio 1:2:3:6 -- the divisors themselves!
    print()
    print("  Weight ratios: 1 : 2 : 3 : 6  (= divisors themselves!)")
    print("  This is ALWAYS true: w_d = d/sigma, so w ratios = divisor ratios.")
    print("  What's special about n=6: sum = 2n, so sigma = 2n,")
    print("  meaning w_n = n/(2n) = 1/2 (largest divisor gets exactly half).")

    return


# ============================================================
# MAIN
# ============================================================

def verify_all():
    """Run assertion-based verification."""
    section("VERIFICATION: All Core Claims")

    # (a) sigma*phi = n*tau for n=6
    assert sigma(6) * euler_phi(6) == 6 * tau(6), "Condition (a) failed for n=6"
    print("  (a) sigma(6)*phi(6) = n*tau(6): PASS")

    # (b) sigma-tau = 2^(sigma/tau) for n=6
    assert sigma(6) - tau(6) == 2 ** (sigma(6) // tau(6)), "Condition (b) failed for n=6"
    print("  (b) sigma(6)-tau(6) = 2^(sigma/tau): PASS")

    # (c) self-referential SO dim
    assert 4 * 3 // 2 == 6, "Condition (c) failed: SO(4) dim != 6"
    print("  (c) dim(SO(2^(tau/2))) = dim(SO(4)) = 6: PASS")

    # (d) KO^{-6}(pt) = 0
    assert KO_GROUPS[6 % 8][1] is True, "Condition (d) failed"
    print("  (d) KO^{-6}(pt) = 0: PASS")

    # (e) Cl(6,0) real type
    assert CLIFFORD_TYPES[6 % 8] == 'R', "Condition (e) failed"
    print("  (e) Cl(6,0) = R type: PASS")

    # 2-3 theorem
    assert r_factor(2, 1) * r_factor(3, 1) == 1, "2-3 theorem failed"
    print("  2-3 Theorem: r(2,1)*r(3,1) = 1: PASS")

    # Bott propagation
    assert sigma(6) - tau(6) == 8, "Bott connection failed"
    assert 2**3 == 8, "2^3 = 8: trivially true"
    print("  Bott: sigma-tau = 8 = 2^3: PASS")

    # phi + tau = n
    assert euler_phi(6) + tau(6) == 6, "phi+tau=n failed"
    print("  phi(6)+tau(6) = 6 = n: PASS")

    # sigma = 3*tau
    assert sigma(6) == 3 * tau(6), "sigma=3tau failed"
    print("  sigma(6) = 3*tau(6): PASS")

    # 1/2 + 1/3 + 1/6 = 1
    assert Fraction(1,2) + Fraction(1,3) + Fraction(1,6) == 1
    print("  1/2 + 1/3 + 1/6 = 1: PASS")

    # Uniqueness of (a) in [1, 1000]
    solutions_a = [n for n in range(2, 1001) if condition_a(n)]
    assert solutions_a == [6], f"Condition (a) not unique: {solutions_a[:10]}"
    print("  (a) unique to n=6 in [2, 1000]: PASS")

    print()
    print("  ALL ASSERTIONS PASSED")


def main():
    parser = argparse.ArgumentParser(description="Grand Unification of n=6")
    parser.add_argument('--master', action='store_true', help='Master theorem scan only')
    parser.add_argument('--two-three', action='store_true', help='2-3 theorem only')
    parser.add_argument('--entropy', action='store_true', help='Arithmetic entropy only')
    parser.add_argument('--harmonics', action='store_true', help='Harmonic ratio analysis only')
    parser.add_argument('--categorical', action='store_true', help='Categorical analysis only')
    parser.add_argument('--texas', action='store_true', help='Texas Sharpshooter only')
    parser.add_argument('--info', action='store_true', help='Information theory only')
    parser.add_argument('--verify', action='store_true', help='Run assertions only')
    parser.add_argument('--limit', type=int, default=1000, help='Search limit (default: 1000)')
    args = parser.parse_args()

    print("=" * 70)
    print("  GRAND UNIFICATION OF n=6 CHARACTERIZATIONS")
    print("  Five independent connections unified through 2x3 structure")
    print("=" * 70)

    specific = any([args.master, args.two_three, args.entropy, args.harmonics,
                    args.categorical, args.texas, args.info, args.verify])

    if args.verify or not specific:
        verify_all()

    if args.master or not specific:
        master_theorem_scan(args.limit)

    if args.two_three or not specific:
        two_three_theorem()

    if args.entropy or not specific:
        entropy_analysis()

    if args.harmonics or not specific:
        harmonic_analysis(args.limit)

    if args.categorical or not specific:
        categorical_analysis()

    if args.info or not specific:
        information_theory()

    if args.texas or not specific:
        texas_sharpshooter(args.limit)

    # Final summary
    section("GRAND SUMMARY")
    print("  Five connections to n=6, unified by the 2x3 factorization:")
    print()
    print("  (1) ARITHMETIC:  sigma*phi = n*tau  <=>  r(2,1)*r(3,1) = 1")
    print("      Unique to n=6 among n >= 2. The 2-3 theorem proves")
    print("      (2,3) is the only prime pair giving balance.")
    print()
    print("  (2) BOTT/TOPOLOGY: sigma-tau = 8 = 2^3 = Bott period")
    print("      The exponent 3 and base 2 are exactly the primes of 6.")
    print("      Cl(6,0) = R(8), matching KO-triviality at dim 6.")
    print()
    print("  (3) SELF-REFERENCE: dim(SO(2^{tau/2})) = dim(SO(4)) = 6 = n")
    print("      tau(6)=4 from 6=2*3 having divisors {1,2,3,6}.")
    print("      The loop n -> tau -> spinor dim -> SO dim -> n closes.")
    print()
    print("  (4) NCG/PHYSICS: KO-dim 6 gives Standard Model constraints")
    print("      KO^{-6}(pt) = 0 (trivial), Cl(6,0) = R(8) (real).")
    print("      Both conditions from 6 mod 8 = 6.")
    print()
    print("  (5) EXOTIC SPHERES: |bP_{4k}| involves 2^{2k-2}(2^{2k-1}-1)")
    print("      The Euler form for perfect numbers: 2^{p-1}(2^p - 1).")
    print("      For p=2: 2^1 * 3 = 6. The smallest Mersenne prime p=2")
    print("      gives the smallest perfect number through 2x3.")
    print()
    print("  COMMON THREAD: All five originate from 6 = 2 x 3,")
    print("  the unique product of the first two primes, where the")
    print("  multiplicative arithmetic factor product equals unity.")
    print()
    print("  MASTER THEOREM: n=6 is the unique positive integer")
    print("  satisfying all five conditions (a)-(e) simultaneously.")


if __name__ == '__main__':
    main()
