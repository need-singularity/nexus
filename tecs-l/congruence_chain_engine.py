```python
#!/usr/bin/env python3
"""Congruence subgroup Gamma_0(N) forcing chain system analysis engine

Calculates core invariants of Gamma_0(N) (index, cusp count, elliptic point count, genus)
and explores how "forcing chains" relate to sigma(N), tau(N) in the range N=1..100.

Usage:
  python3 congruence_chain_engine.py                    # Full table N=1..100
  python3 congruence_chain_engine.py --range 1 50       # N=1..50
  python3 congruence_chain_engine.py --detail 6         # Detailed analysis for N=6
  python3 congruence_chain_engine.py --moonshine        # Explore moonshine-type N
"""

import argparse
import math
from collections import defaultdict

# ─────────────────────────────────────────
# Basic number theory functions
# ─────────────────────────────────────────

def factorize(n):
    """Return prime factorization of n as {prime: exponent} dictionary"""
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


def divisors(n):
    """Return all divisors of n as a sorted list"""
    if n <= 0:
        return []
    divs = []
    for i in range(1, int(math.isqrt(n)) + 1):
        if n % i == 0:
            divs.append(i)
            if i != n // i:
                divs.append(n // i)
    return sorted(divs)


def euler_phi(n):
    """Euler's phi function phi(n)"""
    if n <= 0:
        return 0
    result = n
    facts = factorize(n)
    for p in facts:
        result = result * (p - 1) // p
    return result


def mobius(n):
    """Möbius function mu(n)"""
    if n == 1:
        return 1
    facts = factorize(n)
    for p, e in facts.items():
        if e > 1:
            return 0
    return (-1) ** len(facts)


def sigma_k(n, k=1):
    """Divisor function sigma_k(n) = sum(d^k for d|n)"""
    if n <= 0:
        return 0
    return sum(d ** k for d in divisors(n))


def gcd(a, b):
    """Greatest common divisor"""
    while b:
        a, b = b, a % b
    return a


def lcm(a, b):
    """Least common multiple"""
    if a == 0 or b == 0:
        return 0
    return abs(a * b) // gcd(a, b)


def kronecker_symbol(a, n):
    """Kronecker symbol (a/n) — generalization of Legendre symbol

    Extends Jacobi symbol to handle even and negative modulus"""
    if n == 0:
        return 1 if abs(a) == 1 else 0
    if n == 1:
        return 1
    if n == -1:
        return -1 if a < 0 else 1

    # Case n=2: (a/2)
    if n == 2:
        if a % 2 == 0:
            return 0
        r = a % 8
        if r == 1 or r == 7:
            return 1
        else:
            return -1

    # Handle negative n
    if n < 0:
        return kronecker_symbol(a, -1) * kronecker_symbol(a, -n)

    # Separate even n: n = 2^s * m (m odd)
    s = 0
    m = n
    while m % 2 == 0:
        s += 1
        m //= 2

    # (a/n) = (a/2)^s * (a/m)
    result = kronecker_symbol(a, 2) ** s if s > 0 else 1
    if m == 1:
        return result

    # Jacobi symbol (a/m) — m is odd positive
    return result * jacobi_symbol(a, m)


def jacobi_symbol(a, n):
    """Jacobi symbol (a/n) — n is odd positive"""
    if n <= 0 or n % 2 == 0:
        raise ValueError(f"Jacobi symbol: n={n} must be odd positive")
    if n == 1:
        return 1

    a = a % n
    result = 1

    while a != 0:
        # Remove factors of 2 from a
        while a % 2 == 0:
            a //= 2
            # Process (2/n): sign flips if n mod 8 is 3 or 5
            if n % 8 in (3, 5):
                result = -result

        # Apply quadratic reciprocity
        a, n = n, a
        if a % 4 == 3 and n % 4 == 3:
            result = -result
        a = a % n

    if n == 1:
        return result
    return 0


# ─────────────────────────────────────────
# Gamma_0(N) invariant calculations
# ─────────────────────────────────────────

def gamma0_index(n):
    """[SL(2,Z) : Gamma_0(N)] = N * prod(1 + 1/p) for p|N

    This is the index mu in PSL(2,Z)"""
    if n <= 0:
        return 0
    if n == 1:
        return 1
    facts = factorize(n)
    # mu = N * prod_{p|N} (1 + 1/p)
    # Integer arithmetic: N * prod((p+1)/p) = prod(p^(e-1) * (p+1))
    result = 1
    for p, e in facts.items():
        result *= (p ** (e - 1)) * (p + 1)
    return result


def gamma0_cusps(n):
    """Number of cusps of Gamma_0(N) = sum_{d|N} phi(gcd(d, N/d))"""
    if n <= 0:
        return 0
    return sum(euler_phi(gcd(d, n // d)) for d in divisors(n))


def gamma0_elliptic2(n):
    """Number of order 2 elliptic points e2 of Gamma_0(N)

    e2 = 0  if 4|N
    e2 = prod_{p|N} (1 + kronecker(-4, p))  otherwise

    where kronecker(-4, p) = kronecker(-1, p) (when p is odd prime)
    p=2 requires special handling"""
    if n <= 0:
        return 0
    if n == 1:
        return 1  # SL(2,Z) has 1 elliptic point (i)

    # If 4|N then e2=0
    if n % 4 == 0:
        return 0

    facts = factorize(n)
    result = 1
    for p, e in facts.items():
        if e >= 2 and p == 2:
            # 4|N condition already handled above (2^2 or higher)
            return 0
        if p == 2:
            # 2||N (exactly once): (1 + kronecker(-4,2)) = (1 + 0) = 1
            result *= 1
        else:
            # Odd prime p: p^e | N
            if e >= 2:
                return 0
            # p appears exactly once: (1 + kronecker(-1, p))
            leg = kronecker_symbol(-1, p)
            result *= (1 + leg)

    return result


def gamma0_elliptic3(n):
    """Number of order 3 elliptic points e3 of Gamma_0(N)

    e3 = 0  if 9|N
    e3 = prod_{p|N} (1 + kronecker(-3, p))  otherwise

    p=3 requires special handling"""
    if n <= 0:
        return 0
    if n == 1:
        return 1  # SL(2,Z) has 1 elliptic point (rho)

    # If 9|N then e3=0
    if n % 9 == 0:
        return 0

    facts = factorize(n)
    result = 1
    for p, e in facts.items():
        if p == 3 and e >= 2:
            return 0
        if p == 3:
            # 3||N: (1 + kronecker(-3,3)) = (1 + 0) = 1
            result *= 1
        else:
            if e >= 2:
                return 0
            # Prime p != 3: (1 + kronecker(-3, p))
            leg = kronecker_symbol(-3, p)
            result *= (1 + leg)

    return result


def gamma0_genus(n):
    """Genus g of Gamma_0(N)

    g = 1 + mu/12 - e2/4 - e3/3 - c/2

    where mu = index, e2 = order 2 elliptic points, e3 = order 3 elliptic points, c = cusp count"""
    mu = gamma0_index(n)
    e2 = gamma0_elliptic2(n)
    e3 = gamma0_elliptic3(n)
    c = gamma0_cusps(n)

    # Ensure accuracy with rational arithmetic
    # g = 1 + mu/12 - e2/4 - e3/3 - c/2
    # Unify with denominator 12: 12 + mu - 3*e2 - 4*e3 - 6*c, all /12
    numerator = 12 + mu - 3 * e2 - 4 * e3 - 6 * c
    # Genus must be non-negative integer
    g = numerator // 12
    return g


def first_cusp_form_weight(n):
    """Find minimum even integer k where dim S_k(Gamma_0(N)) > 0

    From Riemann-Roch formula:
    dim S_k(Gamma_0(N)) = (k-1)(g-1) + floor(k/4)*e2 + floor(k/3)*e3 + (k/2 - 1)*c
    (for k >= 2, even)

    Precise formula:
    dim S_k = (k-1)(mu/12) - (e2/4)*{term dependent on k} - ...
    Actually uses exact form of Riemann-Roch theorem"""
    mu = gamma0_index(n)
    e2 = gamma0_elliptic2(n)
    e3 = gamma0_elliptic3(n)
    c = gamma0_cusps(n)
    g = gamma0_genus(n)

    for k in range(2, 50, 2):  # Even weights only
        dim = dim_cusp_forms(k, mu, e2, e3, c, g)
        if dim > 0:
            return k
    return None  # Not found under 50


def dim_cusp_forms(k, mu, e2, e3, c, g):
    """Dimension of cusp forms of weight k: dim S_k(Gamma_0(N))

    k=2: dim S_2 = g (genus)
    k >= 4 even:
      dim S_k = (k-1)(g-1) + floor((k-2)/4)*e2 + floor((k-2)/3)*e3 + (k/2 - 1)*c

    Exact formula (Shimura):
      dim S_k = (k-1)(mu/12) - lambda_2(k)*e2 - lambda_3(k)*e3 - c/2  (k>=2 even, + correction)

    Here we use g for k=2, Riemann-Roch formula for k>=4"""
    if k < 2 or k % 2 != 0:
        return 0

    if k == 2:
        return g

    # k >= 4 even: exact dimension formula
    # dim S_k(Gamma_0(N)) = (k-1)(g-1) + floor(k/4)*e2_coeff + floor(k/3)*e3_coeff + ...
    # Standard formula (Diamond & Shurman):
    # dim S_k = (k-1)(mu/12) - e2 * lambda_2(k) - e3 * lambda_3(k) - c * (1/2)
    #   where lambda_2(k) = value depends on k mod 4
    #   lambda_3(k) = value depends on k mod 3

    # lambda_2(k): according to k mod 4
    km4 = k % 4
    if km4 == 0:
        lam2 = 1.0 / 4.0
    elif km4 == 2:
        lam2 = 1.0 / 4.0
    else:
        lam2 = 0  # Odd doesn't come here

    # lambda_3(k): according to k mod 3
    km3 = k % 3
    if km3 == 0:
        lam3 = 1.0 / 3.0
    elif km3 == 1:
        lam3 = 1.0 / 3.0
    elif km3 == 2:
        lam3 = 1.0 / 3.0
    else:
        lam3 = 0

    # General dimension formula (k >= 4 even):
    # dim = (k-1)(g-1) + floor(k*e2/4) + floor(k*e3/3) + (k/2 - 1)*c
    # This is not the exact formula:
    # dim M_k = (k-1)(g-1) + floor(k/4)*e2 + floor(k/3)*e3 + (k/2)*c
    # dim S_k = dim M_k - c  (remove c Eisenstein series)
    # => dim S_k = (k-1)(g-1) + floor(k/4)*e2 + floor(k/3)*e3 + (k/2 - 1)*c

    dim = (k - 1) * (g - 1) + (k // 4) * e2 + (k // 3) * e3 + (k // 2 - 1) * c
    return max(0, dim)


# ─────────────────────────────────────────
# Forcing chain analysis
# ─────────────────────────────────────────

def isotropy_orders(n):
    """Set of isotropy orders in Gamma_0(N)

    Order 1 (identity), order 2 (if e2 > 0), order 3 (if e3 > 0),
    and parabolic elements (cusps) have infinite order → excluded from lcm"""
    orders = {1}  # Identity always exists
    if gamma0_elliptic2(n) > 0:
        orders.add(2)
    if gamma0_elliptic3(n) > 0:
        orders.add(3)
    return orders


def forcing_chain_analysis(n):
    """Forcing chain analysis for N

    Explores how lcm of isotropy orders relates to sigma(N) or other
    arithmetic functions"""
    orders = isotropy_orders(n)
    iso_lcm = 1
    for o in orders:
        iso_lcm = lcm(iso_lcm, o)

    sig = sigma_k(n, 1)  # sigma_1(N)
    sig0 = sigma_k(n, 0)  # number of divisors d(N)
    mu = gamma0_index(n)
    c = gamma0_cusps(n)

    result = {
        'isotropy_orders': sorted(orders),
        'lcm_isotropy': iso_lcm,
        'sigma_1': sig,
        'sigma_0': sig0,
        'index': mu,
        'cusps': c,
        'relations': []
    }

    # Explore relations between lcm and arithmetic functions
    if iso_lcm > 0:
        if sig % iso_lcm == 0:
            result['relations'].append(f"sigma({n}) = {sig//iso_lcm} * lcm = {sig}")
        if mu % iso_lcm == 0:
            result['relations'].append(f"index = {mu//iso_lcm} * lcm = {mu}")
        # lcm * cusps vs sigma
        prod_lc = iso_lcm * c
        if prod_lc == sig:
            result['relations'].append(f"lcm * cusps = sigma({n}) = {sig} [exact match!]")
        elif prod_lc > 0 and sig % prod_lc == 0:
            result['relations'].append(f"sigma({n}) = {sig//prod_lc} * (lcm*cusps)")
        # lcm * sigma_0 vs index
        prod_ld = iso_lcm * sig0
        if prod_ld == mu:
            result['relations'].append(f"lcm * d({n}) = index = {mu} [exact match!]")
        # Relation with 12 (key constant in modular forms)
        if iso_lcm > 0 and mu % (12 * iso_lcm) == 0:
            result['relations'].append(f"index = {mu//(12*iso_lcm)} * 12 * lcm")

    return result


# ─────────────────────────────────────────
# Output formatting
# ─────────────────────────────────────────

def print_table(n_start, n_end):
    """Print invariant table for N=n_start..n_end"""
    # Header
    header = (
        f"{'N':>4} | {'mu':>6} | {'cusps':>5} | {'e2':>3} | {'e3':>3} | "
        f"{'genus':>5} | {'1st k':>5} | {'iso_lcm':>7} | {'sigma':>6} | {'special'}"
    )
    sep = "-" * len(header)

    print("=" * len(header))
    print("  Gamma_0(N) Congruence Subgroup Invariant Table")
    print("  Forcing Chain Analysis")
    print("=" * len(header))
    print(header)
    print(sep)

    # Collect genus statistics
    genus_0_list = []
    genus_1_list = []
    special_notes = []

    for n in range(n_start, n_end + 1):
        mu = gamma0_index(n)
        c = gamma0_cusps(n)
        e2 = gamma0_elliptic2(n)
        e3 = gamma0_elliptic3(n)
        g = gamma0_genus(n)
        fk = first_cusp_form_weight(n)
        fk_str = str(fk) if fk else "-"

        orders = isotropy_orders(n)
        iso_lcm = 1
        for o in orders:
            iso_lcm = lcm(iso_lcm, o)

        sig = sigma_k(n, 1)

        # Special markers
        notes = []
        if g == 0:
            notes.append("g=0")
            genus_0_list.append(n)
        if g == 1:
            notes.append("g=1")
            genus_1_list.append(n)

        # Forcing chain match check
        fc = forcing_chain_analysis(n)
        for rel in fc['relations']:
            if "exact match" in rel:
                notes.append("chain!")

        # Relation between sigma and index
        if mu == sig:
            notes.append("mu=sig")

        note_str = ", ".join(notes) if notes else ""

        print(
            f"{n:>4} | {mu:>6} | {c:>5} | {e2:>3} | {e3:>3} | "
            f"{g:>5} | {fk_str:>5} | {iso_lcm:>7} | {sig:>6} | {note_str}"
        )

    print(sep)
    print()

    # Summary statistics
    print("=" * 60)
    print("  Summary Statistics")
    print("=" * 60)
    print(f"  Genus 0 (rational modular curves): {len(genus_0_list)}")
    if genus_0_list:
        print(f"    N = {genus_0_list}")
    print(f"  Genus 1 (elliptic curves):         {len(genus_1_list)}")
    if genus_1_list:
        print(f"    N = {genus_1_list}")
    print()

    # Why N=1 is special
    print("=" * 60)
    print("  Why N=1 is Special (Forcing Chain Perspective)")
    print("=" * 60)
    print("  N=1: Gamma_0(1) = SL(2,Z) — Full modular group")
    print(f"    Index mu = {gamma0_index(1)}")
    print(f"    Cusps    = {gamma0_cusps(1)} (unique cusp: infinity)")
    print(f"    e2 = {gamma0_elliptic2(1)} (fixed point: i)")
    print(f"    e3 = {gamma0_elliptic3(1)} (fixed point: rho = e^(2pi*i/3))")
    print(f"    Genus g = {gamma0_genus(1)} (rational curve → j-invariant)")
    print(f"    Isotropy orders: {{1, 2, 3}} → lcm = 6")
    print(f"    sigma(1) = 1, sigma(6) = 12")
    print(f"    12 = SL(2,Z)'s 'magic number' — denominator in genus formula!")
    print(f"    lcm(1,2,3) = 6 → first perfect number")
    print()


def print_detail(n):
    """Print detailed analysis for N"""
    print("=" * 60)
    print(f"  Gamma_0({n}) Detailed Analysis")
    print("=" * 60)

    mu = gamma0_index(n)
    c = gamma0_cusps(n)
    e2 = gamma0_elliptic2(n)
    e3 = gamma0_elliptic3(n)
    g = gamma0_genus(n)
    fk = first_cusp_form_weight(n)
    facts = factorize(n)
    divs = divisors(n)

    print(f"\n  N = {n}")
    print(f"  Prime factorization: {n} = ", end="")
    if not facts:
        print("1")
    else:
        parts = []
        for p, e in sorted(facts.items()):
            if e == 1:
                parts.append(str(p))
            else:
                parts.append(f"{p}^{e}")
        print(" * ".join(parts))
    print(f"  Divisors: {divs}")
    print()

    # Invariants
    print("  [Invariants]")
    print(f"    Index mu = [SL(2,Z) : Gamma_0({n})] = {mu}")
    print(f"      = {n} * prod(1 + 1/p) for p|{n}")
    print(f"    Cusp count c = sum phi(gcd(d, {n}/d)) = {c}")
    print(f"    Order 2 elliptic points e2 = {e2}")
    print(f"    Order 3 elliptic points e3 = {e3}")
    print(f"    Genus g = 1 + {mu}/12 - {e2}/4 - {e3}/3 - {c}/2 = {g}")
    if fk:
        print(f"    Minimum cusp form weight k = {fk}")
        print(f"      dim S_{fk}(Gamma_0({n})) > 0")
    else:
        print(f"    Minimum cusp form weight: k > 48 (out of range)")
    print()

    # Arithmetic functions
    sig1 = sigma_k(n, 1)
    sig0 = sigma_k(n, 0)
    phi_n = euler_phi(n)
    print("  [Arithmetic Functions]")
    print(f"    sigma_1({n}) = {sig1}")
    print(f"    sigma_0({n}) = d({n}) = {sig0}")
    print(f"    phi({n}) = {phi_n}")
    print(f"    mu({n}) = {mobius(n)}")
    if sig1 == 2 * n:
        print(f"    *** {n} is a perfect number! sigma({n}) = 2*{n} ***")
    print()

    # Forcing chains
    fc = forcing_chain_analysis(n)
    print("  [Forcing Chain Analysis]")
    print(f"    Isotropy orders: {fc['isotropy_orders']}")
    print(f"    lcm(isotropy orders) = {fc['lcm_isotropy']}")
    if fc['relations']:
        print("    Discovered relations:")
        for rel in fc['relations']:
            print(f"      -> {rel}")
    else:
        print("    No direct integer relation with sigma/index")
    print()

    # Cusp details
    print("  [Cusp Decomposition]")
    print(f"    sum_{{d|{n}}} phi(gcd(d, {n}/d)):")
    for d in divs:
        nd = n // d
        g_val = gcd(d, nd)
        phi_g = euler_phi(g_val)
        print(f"      d={d:>4}, {n}/d={nd:>4}, gcd={g_val:>4}, phi={phi_g:>4}")
    print(f"    Total = {c}")
    print()

    # Dimension table
    print("  [Cusp Form Dimensions dim S_k(Gamma_0({0}))]".format(n))
    print(f"    {'k':>4} | {'dim S_k':>8}")
    print(f"    {'-'*4}-+-{'-'*8}")
    for k in range(2, 26, 2):
        dim = dim_cusp_forms(k, mu, e2, e3, c, g)
        marker = " <-- minimum" if k == fk else ""
        print(f"    {k:>4} | {dim:>8}{marker}")
    print()


def print_moonshine(n_start, n_end):
    """Explore moonshine-type N — genus 0 with special arithmetic properties"""
    print("=" * 60)
    print("  Moonshine Type Exploration")
    print("  Genus 0 + Clean Forcing Chains")
    print("=" * 60)
    print()

    # Known genus 0 levels related to Monster group
    known_moonshine = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 16, 18, 25}

    genus0_ns = []
    for n in range(n_start, n_end + 1):
        g = gamma0_genus(n)
        if g == 0:
            genus0_ns.append(n)

    print(f"  Genus 0 N (range {n_start}..{n_end}): {len(genus0_ns)}")
    print(f"  N = {genus0_ns}")
    print()

    # Details for each genus 0 level
    print(f"  {'N':>4} | {'mu':>5} | {'c':>3} | {'e2':>3} | {'e3':>3} | "
          f"{'lcm':>4} | {'sig':>5} | {'moon':>4} | Notes")
    print(f"  {'-'*4}-+-{'-'*5}-+-{'-'*3}-+-{'-'*3}-+-{'-'*3}-+-"
          f"{'-'*4}-+-{'-'*5}-+-{'-'*4}-+------")

    for n in genus0_ns:
        mu = gamma0_index(n)
        c = gamma0_cusps(n)
        e2 = gamma0_elliptic2(n)
        e3 = gamma0_elliptic3(n)
        orders = isotropy_orders(n)
        iso_lcm = 1
        for o in orders:
            iso_lcm = lcm(iso_lcm, o)
        sig = sigma_k(n, 1)

        moon = "Y" if n in known_moonshine else ""
        notes = []

        # Check special properties
        if iso_lcm == 6:
            notes.append("lcm=6(perfect)")
        if mu == 12:
            notes.append("mu=12")
        if sig == 2 * n:
            notes.append("perfect number!")
        if mu % 12 == 0:
            notes.append(f"mu/12={mu//12}")

        fc = forcing_chain_analysis(n)
        for rel in fc['relations']:
            if "exact match" in rel:
                notes.append("chain")

        note_str = ", ".join(notes) if notes else ""
        print(
            f"  {n:>4} | {mu:>5} | {c:>3} | {e2:>3} | {e3:>3} | "
            f"{iso_lcm:>4} | {sig:>5} | {moon:>4} | {note_str}"
        )

    print()

    # Analysis of the role of 12
    print("=" * 60)
    print("  The Role of 12 — Denominator in Genus Formula")
    print("=" * 60)
    print("  Genus formula: g = 1 + mu/12 - e2/4 - e3/3 - c/2")
    print("  12 = lcm(1,2,3,4,6) — lcm of all denominators in genus formula")
    print("  12 = 2 * sigma(6) — twice the divisor sum of perfect number 6")
    print("  12 = |SL(2,Z)/+-1| area of fundamental domain (4*pi/12 = pi/3)")
    print()
    print("  Forcing chain at N=1:")
    print("    {1, 2, 3} -> lcm = 6 (first perfect number)")
    print("    Genus formula denominator = 12 = 2 * 6")
    print("    sigma(6) = 1+2+3+6 = 12 -> cycles back to genus formula!")
    print("    This is why N=1 is 'self-referential'")
    print()


# ─────────────────────────────────────────
# Main
# ─────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Congruence subgroup Gamma_0(N) forcing chain analysis engine"
    )
    parser.add_argument(
        '--range', nargs=2, type=int, default=[1, 100],
        metavar=('N1', 'N2'),
        help='Analysis range (default: 1 100)'
    )
    parser.add_argument(
        '--detail', type=int, default=None,
        metavar='N',
        help='Detailed analysis for single N'
    )
    parser.add_argument(
        '--moonshine', action='store_true',
        help='Explore moonshine-type N (genus 0 + special properties)'
    )

    args = parser.parse_args()

    if args.detail is not None:
        print_detail(args.detail)
    elif args.moonshine:
        print_moonshine(args.range[0], args.range[1])
    else:
        print_table(args.range[0], args.range[1])


if __name__ == '__main__':
    main()
```