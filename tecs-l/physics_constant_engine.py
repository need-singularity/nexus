#!/usr/bin/env python3
"""Physics Constant Matching Engine — Search for CODATA physics constants with sigma,tau expressions

Systematically explores how well expressions derived from sigma=12, tau=4 of perfect number 6
can approximate physical constants.

Usage:
  python3 physics_constant_engine.py                    # Default search (1%)
  python3 physics_constant_engine.py --threshold 0.1    # Within 0.1% only
  python3 physics_constant_engine.py --deep             # Deep search (more expressions)
  python3 physics_constant_engine.py --element          # Element analysis mode
"""

import argparse
import math
import random
from itertools import combinations, product as iterproduct

# ─────────────────────────────────────────
# Base constants: derived from perfect number 6
# ─────────────────────────────────────────
SIGMA = 12          # σ(6) = 1+2+3+6
TAU = 4             # τ(6) = divisor count
P1 = 6              # The perfect number itself
M3 = 7              # Mersenne prime M3 = 2^3 - 1
PERFECT_PAIR = 28   # Second perfect number

# Derived constants
DERIVED = {
    'sigma':    SIGMA,          # 12
    'tau':      TAU,            # 4
    'P1':       P1,             # 6
    'M3':       M3,             # 7
    's-t':      SIGMA - TAU,    # 8 = SU(3)
    's+t':      SIGMA + TAU,    # 16
    's*t':      SIGMA * TAU,    # 48
    's/t':      SIGMA / TAU,    # 3
    't!':       math.factorial(TAU),  # 24
    'P1!':      720,            # 6! = 720
    's+P1':     SIGMA + P1,     # 18
    'T(s)':     SIGMA * (SIGMA + 1) // 2,  # Triangular number T(12) = 78
    'T(t)':     TAU * (TAU + 1) // 2,      # Triangular number T(4) = 10
    'T(P1)':    P1 * (P1 + 1) // 2,        # Triangular number T(6) = 21
    '2':        2,
    '3':        3,
    '1':        1,
    '5':        5,
    '17':       17,             # Fermat prime
    '137':      137,            # Fine structure constant
    '153':      153,            # Triangular number T(17)
}

# ─────────────────────────────────────────
# CODATA physical constants + nuclear physics + elements
# ─────────────────────────────────────────
PHYSICS_CONSTANTS = {
    # Electromagnetic
    '1/alpha':          137.035999084,      # Fine structure constant inverse
    'alpha':            1/137.035999084,     # Fine structure constant
    # Mass ratios
    'm_p/m_e':          1836.15267343,       # Proton/electron mass ratio
    'm_mu/m_e':         206.7682830,         # Muon/electron mass ratio
    'm_tau/m_e':        3477.48,             # Tau lepton/electron mass ratio
    # Electroweak
    'sin2_thetaW':      0.23122,             # Weinberg angle sin²θ_W
    'alpha_s(M_Z)':     0.1179,              # Strong coupling constant at M_Z
    # Atomic physics
    'Rydberg_eV':       13.605693122994,     # Rydberg constant (eV)
    'a0/r_e':           137.036**2,          # Bohr radius/classical electron radius
    # Nuclear magic numbers
    'magic_2':          2,
    'magic_8':          8,
    'magic_20':         20,
    'magic_28':         28,
    'magic_50':         50,
    'magic_82':         82,
    'magic_126':        126,
}

# Element atomic numbers
ELEMENTS = {
    'H(1)':   1,   'He(2)':  2,   'C(6)':   6,   'N(7)':   7,
    'O(8)':   8,   'Si(14)': 14,  'Fe(26)': 26,  'Au(79)': 79,
    'U(92)':  92,  'Pb(82)': 82,
}

# Already known matches (existing project discoveries)
KNOWN_MATCHES = {
    '1/alpha':      ('8*17+1', 8*17+1, 137),
    'm_p/m_e':      ('sigma*153', SIGMA * 153, 1836),
    'sin2_thetaW':  ('s/t / (s+1)', (SIGMA/TAU) / (SIGMA+1), 3/13),
}


def factorial(n):
    """Safe factorial (integer, range limited)"""
    if isinstance(n, float):
        n = int(n)
    if 0 <= n <= 12:
        return math.factorial(n)
    return None


def triangular(n):
    """Triangular number T(n) = n(n+1)/2"""
    if isinstance(n, float):
        n = int(n)
    if 0 <= n <= 1000:
        return n * (n + 1) // 2
    return None


def generate_expressions(deep=False):
    """Generate expressions with sigma, tau derived constants → (value, name) list"""
    # Stage 1: base constants
    exprs = [(v, k) for k, v in DERIVED.items()]

    # Unary operations: factorial, triangular, square, cube
    unary_extra = []
    for v, n in exprs:
        if isinstance(v, (int, float)) and 1 <= v <= 12:
            f = factorial(int(v))
            if f is not None:
                unary_extra.append((f, f'{n}!'))
        if isinstance(v, (int, float)) and 1 <= v <= 200:
            t = triangular(int(v))
            if t is not None:
                unary_extra.append((t, f'T({n})'))
        # Powers
        if abs(v) < 100:
            unary_extra.append((v**2, f'{n}^2'))
            if abs(v) < 20:
                unary_extra.append((v**3, f'{n}^3'))
    exprs.extend(unary_extra)

    # Stage 2: binary operations
    base_exprs = list(exprs)
    binary = []
    for (av, an), (bv, bn) in combinations(base_exprs, 2):
        if av is None or bv is None:
            continue
        _safe_add(binary, av + bv, f'({an}+{bn})')
        _safe_add(binary, av - bv, f'({an}-{bn})')
        _safe_add(binary, bv - av, f'({bn}-{an})')
        _safe_add(binary, av * bv, f'{an}*{bn}')
        if bv != 0:
            _safe_add(binary, av / bv, f'{an}/{bn}')
        if av != 0:
            _safe_add(binary, bv / av, f'{bn}/{an}')
        # Powers (small exponents only)
        if 0 < abs(bv) <= 6 and abs(av) < 1000:
            try:
                r = av ** bv
                if abs(r) < 1e15:
                    _safe_add(binary, r, f'{an}^{bn}')
            except (OverflowError, ValueError):
                pass
        if 0 < abs(av) <= 6 and abs(bv) < 1000:
            try:
                r = bv ** av
                if abs(r) < 1e15:
                    _safe_add(binary, r, f'{bn}^{an}')
            except (OverflowError, ValueError):
                pass
    exprs.extend(binary)

    # Stage 3 (--deep): ternary operations a*b+c, a*b-c, a*b*c
    if deep:
        for (av, an), (bv, bn) in combinations(base_exprs[:20], 2):
            if av is None or bv is None:
                continue
            ab = av * bv
            ab_n = f'{an}*{bn}'
            for cv, cn in base_exprs[:20]:
                if cv is None:
                    continue
                _safe_add(exprs, ab + cv, f'({ab_n}+{cn})')
                _safe_add(exprs, ab - cv, f'({ab_n}-{cn})')
                _safe_add(exprs, ab * cv, f'{ab_n}*{cn}')
                if cv != 0:
                    _safe_add(exprs, ab / cv, f'{ab_n}/{cn}')

    return exprs


def _safe_add(lst, val, name):
    """Add only finite values"""
    if isinstance(val, (int, float)) and math.isfinite(val) and abs(val) < 1e15:
        lst.append((val, name))


def find_matches(exprs, targets, threshold):
    """Find the closest expression for each physical constant"""
    results = []
    for tname, tval in targets.items():
        if tval == 0:
            continue
        best_err = float('inf')
        best_expr = None
        best_calc = None
        for val, ename in exprs:
            if val == 0 and tval == 0:
                continue
            err = abs(val - tval) / abs(tval)
            if err < best_err:
                best_err = err
                best_expr = ename
                best_calc = val
        if best_err <= threshold:
            results.append({
                'target': tname,
                'value': tval,
                'expr': best_expr,
                'calc': best_calc,
                'error': best_err * 100,  # percent
            })
    # Sort by error
    results.sort(key=lambda x: x['error'])
    return results


def texas_sharpshooter(exprs, targets, threshold, trials=1000):
    """Texas Sharpshooter test: Compare match count vs random expressions

    Generate same number of random expressions and measure matches.
    Determine if our matches are significantly beyond chance.
    """
    # Actual match count
    actual = len(find_matches(exprs, targets, threshold))

    # Random simulation: Try matching with equal number of random values
    n_exprs = len(exprs)
    val_range = [v for v, _ in exprs if abs(v) < 1e6]
    if not val_range:
        return actual, 0.0, 0

    vmin, vmax = min(val_range), max(val_range)
    random_counts = []
    for _ in range(trials):
        # Random expressions: uniform distribution in same range
        rand_exprs = [(random.uniform(vmin, vmax), f'rand_{i}')
                      for i in range(min(n_exprs, 500))]
        cnt = len(find_matches(rand_exprs, targets, threshold))
        random_counts.append(cnt)

    avg_random = sum(random_counts) / len(random_counts) if random_counts else 0
    # p-value: fraction of random that matched actual or more
    p_value = sum(1 for c in random_counts if c >= actual) / trials
    return actual, avg_random, p_value


def print_table(results, actual, avg_random, p_value):
    """Print results as ASCII table"""
    print("\n" + "=" * 80)
    print("  Physics Constant Matching Engine — sigma(6)=12, tau(6)=4 Expression Search")
    print("=" * 80)

    if not results:
        print("\n  No matching results. Try increasing --threshold value.")
        return

    # Header
    print(f"\n{'Rank':>4} {'Physics Const':<18} {'Actual Value':>14} {'Expression':<28} {'Calc Value':>14} {'Error%':>8}")
    print("-" * 90)

    for i, r in enumerate(results, 1):
        # Existing discovery marker
        marker = ""
        if r['target'] in KNOWN_MATCHES:
            marker = " *known*"
        print(f"{i:>4} {r['target']:<18} {r['value']:>14.6f} "
              f"{r['expr']:<28} {r['calc']:>14.6f} {r['error']:>7.4f}%{marker}")

    print("-" * 90)
    print(f"  Total matches: {len(results)}")

    # Texas sharpshooter results
    print(f"\n{'=' * 50}")
    print("  Texas Sharpshooter Test")
    print(f"{'=' * 50}")
    print(f"  Actual matches:     {actual}")
    print(f"  Random avg matches: {avg_random:.1f}")
    print(f"  p-value:            {p_value:.4f}")
    if p_value < 0.01:
        print("  Verdict: Structural discovery (p < 0.01)")
    elif p_value < 0.05:
        print("  Verdict: Weak evidence (p < 0.05)")
    else:
        print("  Verdict: Possibly chance (p >= 0.05)")


def element_analysis(exprs, threshold):
    """Element atomic number matching analysis mode"""
    print("\n" + "=" * 60)
    print("  Element Atomic Number Matching (sigma,tau expressions)")
    print("=" * 60)

    results = find_matches(exprs, ELEMENTS, threshold)
    if not results:
        print("  No matches.")
        return

    print(f"\n{'Element':<10} {'Z':>4} {'Expression':<30} {'Calc Value':>10} {'Error%':>8}")
    print("-" * 66)
    for r in results:
        print(f"{r['target']:<10} {r['value']:>4.0f} "
              f"{r['expr']:<30} {r['calc']:>10.4f} {r['error']:>7.4f}%")


def main():
    parser = argparse.ArgumentParser(
        description='Physics Constant Matching Engine — sigma,tau expression search')
    parser.add_argument('--threshold', type=float, default=1.0,
                        help='Error threshold %% (default: 1.0)')
    parser.add_argument('--deep', action='store_true',
                        help='Deep search (include ternary operations)')
    parser.add_argument('--element', action='store_true',
                        help='Element atomic number analysis mode')
    parser.add_argument('--texas-trials', type=int, default=500,
                        help='Texas sharpshooter simulation count (default: 500)')
    args = parser.parse_args()

    threshold = args.threshold / 100.0  # percent→ratio

    print(f"  Settings: threshold={args.threshold}%, deep={args.deep}")
    print(f"  Base constants: sigma={SIGMA}, tau={TAU}, P1={P1}, M3={M3}")

    # Generate expressions
    exprs = generate_expressions(deep=args.deep)
    print(f"  Generated expressions: {len(exprs)}")

    # Force add known matches
    for tname, (expr_str, calc_val, _) in KNOWN_MATCHES.items():
        exprs.append((calc_val, expr_str))

    # Physics constant matching
    results = find_matches(exprs, PHYSICS_CONSTANTS, threshold)

    # Texas sharpshooter test
    actual, avg_random, p_value = texas_sharpshooter(
        exprs, PHYSICS_CONSTANTS, threshold, trials=args.texas_trials)

    print_table(results, actual, avg_random, p_value)

    # Element analysis mode
    if args.element:
        element_analysis(exprs, threshold)

    # Known discovery summary
    print(f"\n{'=' * 50}")
    print("  Existing Discoveries (verified in project)")
    print(f"{'=' * 50}")
    for tname, (expr_str, calc_val, approx) in KNOWN_MATCHES.items():
        tv = PHYSICS_CONSTANTS.get(tname, 0)
        err = abs(calc_val - tv) / abs(tv) * 100 if tv else 0
        print(f"  {tname}: {expr_str} = {calc_val} (error {err:.4f}%)")


if __name__ == '__main__':
    main()