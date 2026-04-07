#!/usr/bin/env python3
"""
Control test: can n=7 or n=8 or n=10 atoms decompose these exponents equally well?
If n=6 is not special, other perfect/non-perfect numbers should work similarly.

Also: deeper analysis of the denominator structure claim.
"""

import math
import random
from fractions import Fraction
from collections import defaultdict

def number_theory_atoms(n):
    """Compute number-theoretic functions for n."""
    # Divisors
    divs = [d for d in range(1, n+1) if n % d == 0]
    sigma = sum(divs)
    tau = len(divs)
    # Euler totient
    phi = sum(1 for k in range(1, n+1) if math.gcd(k, n) == 1)
    # Sum of prime factors with multiplicity
    sopfr = 0
    temp = n
    for p in range(2, n+1):
        while temp % p == 0:
            sopfr += p
            temp //= p
    # Omega (distinct prime factors)
    omega = len(set(p for p in range(2, n+1) if n % p == 0))
    return {
        'n': n, 'sigma': sigma, 'tau': tau, 'phi': phi,
        'sopfr': sopfr, 'omega': omega
    }

def build_atoms(nt):
    """Build atom dict from number theory values."""
    atoms = {'1': Fraction(1)}
    for key in ['phi', 'tau', 'sopfr', 'n', 'sigma']:
        val = nt[key]
        if val not in [v for v in atoms.values()]:  # avoid exact duplicates
            atoms[key] = Fraction(val)
        else:
            atoms[key] = Fraction(val)  # keep it anyway for expression naming
    return atoms

def build_expressions(atoms, max_depth=2):
    """Build all expressions up to given depth."""
    atom_list = list(atoms.items())

    # Depth 0
    exprs = {}
    for name, val in atom_list:
        if val not in exprs:
            exprs[val] = name
    exprs[Fraction(0)] = '0'

    if max_depth == 0:
        return exprs

    # Depth 1: a op b
    d1 = dict(exprs)
    for n1, v1 in atom_list:
        for n2, v2 in atom_list:
            pairs = [
                (v1 + v2, f"{n1}+{n2}"),
                (v1 - v2, f"{n1}-{n2}"),
                (v1 * v2, f"{n1}*{n2}"),
            ]
            if v2 != 0:
                pairs.append((v1 / v2, f"{n1}/{n2}"))
            for val, expr in pairs:
                if val not in d1:
                    d1[val] = expr

    if max_depth == 1:
        return d1

    # Depth 2: d1 op atom, d1 op d1
    d2 = dict(d1)
    d1_items = list(d1.items())

    for val1, expr1 in d1_items:
        for n2, v2 in atom_list:
            pairs = [
                (val1 + v2, f"({expr1})+{n2}"),
                (val1 - v2, f"({expr1})-{n2}"),
                (v2 - val1, f"{n2}-({expr1})"),
                (val1 * v2, f"({expr1})*{n2}"),
            ]
            if v2 != 0:
                pairs.append((val1 / v2, f"({expr1})/{n2}"))
            if val1 != 0:
                pairs.append((v2 / val1, f"{n2}/({expr1})"))
            for val, expr in pairs:
                if val not in d2:
                    d2[val] = expr

    # d1 op d1
    for val1, expr1 in d1_items:
        for val2, expr2 in d1_items:
            pairs = [
                (val1 + val2, f"({expr1})+({expr2})"),
                (val1 - val2, f"({expr1})-({expr2})"),
                (val1 * val2, f"({expr1})*({expr2})"),
            ]
            if val2 != 0:
                pairs.append((val1 / val2, f"({expr1})/({expr2})"))
            for val, expr in pairs:
                if val not in d2:
                    d2[val] = expr

    return d2


# Exponent targets (exact + numerical)
EXACT_TARGETS = {
    'Ising2D_alpha': Fraction(0),
    'Ising2D_beta': Fraction(1, 8),
    'Ising2D_gamma': Fraction(7, 4),
    'Ising2D_delta': Fraction(15),
    'Ising2D_nu': Fraction(1),
    'Ising2D_eta': Fraction(1, 4),
    'MF_alpha': Fraction(0),
    'MF_beta': Fraction(1, 2),
    'MF_gamma': Fraction(1),
    'MF_delta': Fraction(3),
    'MF_nu': Fraction(1, 2),
    'MF_eta': Fraction(0),
    'Perc2D_nu': Fraction(4, 3),
    'Perc2D_beta': Fraction(5, 36),
    'Perc2D_gamma': Fraction(43, 18),
    'Perc2D_eta': Fraction(5, 24),
    'SAW2D_nu': Fraction(3, 4),
    'SAW2D_gamma': Fraction(43, 32),
    'KPZ_alpha': Fraction(1, 2),
    'KPZ_beta': Fraction(1, 3),
    'KPZ_z': Fraction(3, 2),
    'Tri_beta': Fraction(1, 24),
    'Tri_gamma': Fraction(7, 6),
    'Tri_nu': Fraction(5, 9),
}

NUMERICAL_TARGETS = {
    'Ising3D_alpha': 0.110,
    'Ising3D_beta': 0.3265,
    'Ising3D_gamma': 1.2372,
    'Ising3D_delta': 4.789,
    'Ising3D_nu': 0.6301,
    'Ising3D_eta': 0.0364,
    'XY3D_alpha': -0.0146,
    'XY3D_beta': 0.3485,
    'XY3D_gamma': 1.3177,
    'XY3D_nu': 0.6717,
    'XY3D_eta': 0.0381,
    'Heis3D_alpha': -0.1336,
    'Heis3D_beta': 0.3689,
    'Heis3D_gamma': 1.3960,
    'Heis3D_nu': 0.7112,
    'Heis3D_eta': 0.0375,
    'SAW3D_nu': 0.5876,
    'SAW3D_gamma': 1.1575,
    'DP_beta': 0.276,
    'DP_nu_perp': 0.7333,
    'DP_nu_par': 1.0972,
}


def test_number(n, verbose=False):
    """Test how many exponents n's atoms can express."""
    nt = number_theory_atoms(n)
    atoms = build_atoms(nt)
    exprs = build_expressions(atoms, max_depth=2)

    n_exprs = len(exprs)

    # Exact matches
    exact_hits = 0
    exact_total = len(EXACT_TARGETS)
    for name, target in EXACT_TARGETS.items():
        if target in exprs:
            exact_hits += 1
            if verbose:
                print(f"    EXACT {name} = {target} -> {exprs[target]}")
        else:
            if verbose:
                print(f"    MISS  {name} = {target}")

    # Numerical matches (1% tolerance)
    num_hits = 0
    num_total = len(NUMERICAL_TARGETS)
    for name, target in NUMERICAL_TARGETS.items():
        best_err = 0.01
        best_expr = None
        for val, expr in exprs.items():
            fval = float(val)
            if target != 0:
                err = abs(fval - target) / abs(target)
            else:
                err = abs(fval - target)
            if err < best_err:
                best_err = err
                best_expr = expr
        if best_expr:
            num_hits += 1
            if verbose:
                print(f"    APPROX {name} = {target} -> {best_expr} (err={best_err*100:.3f}%)")
        else:
            if verbose:
                print(f"    MISS   {name} = {target}")

    # Random baseline for this n
    random.seed(42)
    rand_hits = 0
    rand_total = 5000
    for _ in range(rand_total):
        target = random.uniform(-0.2, 5.0)
        found = False
        for val in exprs:
            fval = float(val)
            if abs(target) > 0.01:
                err = abs(fval - target) / abs(target)
            else:
                err = abs(fval - target)
            if err < 0.01:
                found = True
                break
        if found:
            rand_hits += 1

    return {
        'n': n,
        'atoms': nt,
        'n_exprs': n_exprs,
        'exact_hits': exact_hits,
        'exact_total': exact_total,
        'num_hits': num_hits,
        'num_total': num_total,
        'total_hits': exact_hits + num_hits,
        'total': exact_total + num_total,
        'rand_rate': rand_hits / rand_total,
    }


def main():
    print("=" * 72)
    print("CONTROL TEST: n=6 vs other numbers")
    print("=" * 72)

    # Test n = 4, 5, 6, 7, 8, 10, 12, 28 (28 = next perfect number)
    test_numbers = [4, 5, 6, 7, 8, 10, 12, 28]

    results = []
    for n in test_numbers:
        nt = number_theory_atoms(n)
        print(f"\n--- n={n} ---")
        print(f"  sigma={nt['sigma']}, tau={nt['tau']}, phi={nt['phi']}, sopfr={nt['sopfr']}, omega={nt['omega']}")
        r = test_number(n, verbose=(n == 6))
        results.append(r)
        print(f"  Expressions: {r['n_exprs']}")
        print(f"  Exact:  {r['exact_hits']}/{r['exact_total']} ({r['exact_hits']/r['exact_total']*100:.0f}%)")
        print(f"  Approx: {r['num_hits']}/{r['num_total']} ({r['num_hits']/r['num_total']*100:.0f}%)")
        print(f"  Total:  {r['total_hits']}/{r['total']} ({r['total_hits']/r['total']*100:.0f}%)")
        print(f"  Random: {r['rand_rate']*100:.1f}%")

    # Summary table
    print("\n" + "=" * 72)
    print("COMPARISON TABLE")
    print("=" * 72)
    print(f"{'n':>4s}  {'Atoms':>30s}  {'Exprs':>6s}  {'Exact':>8s}  {'Num':>8s}  {'Total':>8s}  {'Rand':>6s}")
    print("-" * 80)
    for r in results:
        nt = r['atoms']
        atoms_str = f"s={nt['sigma']},t={nt['tau']},p={nt['phi']},sf={nt['sopfr']}"
        exact_str = f"{r['exact_hits']}/{r['exact_total']}"
        num_str = f"{r['num_hits']}/{r['num_total']}"
        total_str = f"{r['total_hits']}/{r['total']}"
        perf = '*' if r['n'] in [6, 28] else ' '
        print(f"{r['n']:>3d}{perf} {atoms_str:>30s}  {r['n_exprs']:>6d}  {exact_str:>8s}  {num_str:>8s}  {total_str:>8s}  {r['rand_rate']*100:>5.1f}%")

    # === Denominator analysis ===
    print("\n" + "=" * 72)
    print("DENOMINATOR ANALYSIS")
    print("All exact exponents have denominators that factor into 2^a * 3^b")
    print("These are exactly the prime factors of 6.")
    print("=" * 72)

    print("\nExponent denominators:")
    for name, val in sorted(EXACT_TARGETS.items()):
        if val == 0:
            continue
        den = val.denominator
        # Factor
        d = den
        twos = 0
        threes = 0
        while d % 2 == 0: twos += 1; d //= 2
        while d % 3 == 0: threes += 1; d //= 3
        remainder = d
        is_23 = "2^a*3^b" if remainder == 1 else f"HAS FACTOR {remainder}"
        print(f"  {name:20s} = {str(val):8s}  den={den:4d} = 2^{twos} * 3^{threes} {'* '+str(remainder) if remainder>1 else '':<10s}  {is_23}")

    # Count: what fraction of possible denominators up to 36 are 2^a*3^b?
    smooth_23 = []
    for d in range(1, 37):
        temp = d
        while temp % 2 == 0: temp //= 2
        while temp % 3 == 0: temp //= 3
        if temp == 1:
            smooth_23.append(d)
    print(f"\n  3-smooth numbers up to 36: {smooth_23}")
    print(f"  Count: {len(smooth_23)}/36 = {len(smooth_23)/36*100:.1f}%")

    # Under null hypothesis: denominators are uniform random in [1..36]
    # Probability all 24 are 3-smooth (excluding zeros):
    non_zero_exact = [v for v in EXACT_TARGETS.values() if v != 0]
    n_nz = len(non_zero_exact)
    p_smooth = len(smooth_23) / 36
    p_all_smooth = p_smooth ** n_nz
    print(f"\n  Non-zero exact exponents: {n_nz}")
    print(f"  P(random den is 3-smooth) = {p_smooth:.3f}")
    print(f"  P(all {n_nz} are 3-smooth)  = {p_smooth:.3f}^{n_nz} = {p_all_smooth:.2e}")
    print(f"  This IS statistically significant if true.")
    print(f"\n  BUT: this is EXPECTED from conformal field theory.")
    print(f"  CFT central charges are c = 1 - 6/m(m+1),")
    print(f"  and exponents come from Kac table: h_{r,s} = ((m+1)r - ms)^2 - 1) / 4m(m+1)")
    print(f"  Denominators are always products of m and m+1,")
    print(f"  which for small m are products of 2, 3, and small primes.")


if __name__ == '__main__':
    main()
