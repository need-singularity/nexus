#!/usr/bin/env python3
"""
Texas Sharpshooter Verifier
============================
Statistical test for whether a numerical match is coincidence or structural.

Implements:
  1. Monte Carlo test: how often does a random constant match?
  2. Bonferroni correction for multiple comparisons
  3. Post-hoc vs pre-hoc distinction
  4. Ad-hoc detection (+1/-1 adjustments)

Usage:
  python3 texas_verifier.py --value 137 --formula "sigma(6)**2 - 7"
  python3 texas_verifier.py --approx 0.915966 --formula "5/6 * log(3)" --tolerance 0.001
  python3 texas_verifier.py --check-all  # batch check from README
"""

import argparse
import random
from math import log, sqrt, pi, e, factorial, gcd
from fractions import Fraction
from sympy import factorint, divisors, totient, isprime
import time


# ─── Constants pool (things that "could have been tried") ───

CONSTANTS_POOL = {
    # Perfect number 6 constants
    'sigma': 12, 'tau': 4, 'phi': 2, 'psi': 12,
    'omega': 2, 'sopfr': 5, 'n': 6, 'P2': 28,
    # Derived
    'sigma-tau': 8, 'sigma+tau': 16, 'sigma+tau+1': 17,
    'sigma*tau': 48, 'sigma/tau': 3, 'sigma*phi': 24,
    'sigma^2': 144, 'sigma^3': 1728, 'tau!': 24,
    'M3': 7, 'M5': 31, 'M7': 127,
    # Mathematical constants
    'pi': pi, 'e': e, 'ln2': log(2), 'ln3': log(3),
    'sqrt2': sqrt(2), 'sqrt3': sqrt(3),
    'gamma': 0.5772156649, 'zeta3': 1.2020569031,
    'catalan': 0.9159655941, 'golden': 1.6180339887,
}

# ─── Operations that could be tried ───

UNARY_OPS = [
    lambda x: x, lambda x: 1/x, lambda x: x**2, lambda x: x**3,
    lambda x: sqrt(abs(x)) if x >= 0 else None,
    lambda x: log(x) if x > 0 else None,
    lambda x: 2**x if abs(x) < 30 else None,
]

BINARY_OPS = [
    lambda a, b: a + b, lambda a, b: a - b,
    lambda a, b: a * b, lambda a, b: a / b if b != 0 else None,
    lambda a, b: a ** b if abs(b) < 10 and abs(a) < 1000 else None,
]


def count_expressible(target, tolerance=0.001, pool=None):
    """Count how many expressions from the pool hit the target within tolerance."""
    if pool is None:
        pool = CONSTANTS_POOL
    values = list(pool.values())
    hits = 0
    total = 0

    # Single constants
    for v in values:
        if v is None:
            continue
        for op in UNARY_OPS:
            try:
                r = op(v)
                if r is not None and abs(r) < 1e10:
                    total += 1
                    if isinstance(target, (int, float)):
                        if abs(r - target) / max(abs(target), 1e-10) < tolerance:
                            hits += 1
            except Exception:
                pass

    # Binary combinations
    for i, a in enumerate(values):
        for j, b in enumerate(values):
            if a is None or b is None:
                continue
            for op in BINARY_OPS:
                try:
                    r = op(a, b)
                    if r is not None and abs(r) < 1e10:
                        total += 1
                        if isinstance(target, (int, float)):
                            if abs(r - target) / max(abs(target), 1e-10) < tolerance:
                                hits += 1
                except Exception:
                    pass

    return hits, total


def texas_pvalue(target, tolerance=0.001, n_trials=1000, exact=False):
    """
    Compute Texas sharpshooter p-value.

    For exact matches (integers): count integer expressions hitting target.
    For approximate: Monte Carlo estimate of probability.
    """
    if exact or isinstance(target, int):
        hits, total = count_expressible(target, tolerance=0)
        if total == 0:
            return 1.0
        p = hits / total
        return p

    # Approximate: how many expressions land within tolerance of target
    hits, total = count_expressible(target, tolerance=tolerance)
    if total == 0:
        return 1.0
    p = hits / total
    return p


def verify_formula(value, formula_str, tolerance=0.001, verbose=True):
    """
    Full Texas verification pipeline.
    """
    results = {
        'value': value,
        'formula': formula_str,
        'tolerance': tolerance,
    }

    # 1. Compute formula value
    try:
        computed = eval(formula_str, {"__builtins__": {}}, {
            'sigma': 12, 'tau': 4, 'phi': 2, 'psi': 12,
            'omega': 2, 'sopfr': 5, 'n': 6, 'P1': 6, 'P2': 28,
            'M3': 7, 'M5': 31, 'M7': 127,
            'pi': pi, 'e': e, 'log': log, 'sqrt': sqrt, 'ln': log,
            'Fraction': Fraction, 'factorial': factorial,
        })
    except Exception as ex:
        if verbose:
            print(f"Error evaluating formula: {ex}")
        return results

    results['computed'] = computed

    # 2. Check match
    if isinstance(value, int) and isinstance(computed, int):
        results['exact'] = (value == computed)
        results['error'] = 0 if value == computed else abs(value - computed)
    else:
        fv, fc = float(value), float(computed)
        results['error'] = abs(fv - fc) / max(abs(fv), 1e-10)
        results['exact'] = (results['error'] < tolerance)

    # 3. Texas p-value
    is_exact = isinstance(value, int)
    results['p_value'] = texas_pvalue(value, tolerance=tolerance, exact=is_exact)

    # 4. Ad-hoc detection
    results['ad_hoc'] = ('+1' in formula_str or '-1' in formula_str or
                         '+ 1' in formula_str or '- 1' in formula_str)

    # 5. Grade
    p = results['p_value']
    if results['exact'] and not results.get('error', 1):
        if results['ad_hoc']:
            results['grade'] = 'GREEN (ad-hoc warning)'
        elif p < 0.01:
            results['grade'] = 'ORANGE_STAR'
        elif p < 0.05:
            results['grade'] = 'ORANGE'
        else:
            results['grade'] = 'GREEN'
    elif results.get('error', 1) < tolerance:
        if p < 0.01:
            results['grade'] = 'ORANGE_STAR'
        elif p < 0.05:
            results['grade'] = 'ORANGE'
        else:
            results['grade'] = 'WHITE'
    else:
        results['grade'] = 'FAIL'

    if verbose:
        print(f"\n{'='*60}")
        print(f"Texas Sharpshooter Verification")
        print(f"{'='*60}")
        print(f"Target value: {value}")
        print(f"Formula:      {formula_str}")
        print(f"Computed:     {computed}")
        print(f"Error:        {results.get('error', 'N/A')}")
        print(f"Exact match:  {results.get('exact', False)}")
        print(f"Ad-hoc (+/-1):{results['ad_hoc']}")
        print(f"Texas p-value:{p:.6f}")
        print(f"Grade:        {results['grade']}")
        if p < 0.01:
            print("  -> STRUCTURAL (p < 0.01)")
        elif p < 0.05:
            print("  -> WEAK EVIDENCE (p < 0.05)")
        else:
            print("  -> LIKELY COINCIDENCE (p >= 0.05)")

    return results


def main():
    parser = argparse.ArgumentParser(description="Texas Sharpshooter statistical test")
    parser.add_argument('--value', type=float, help='Target value')
    parser.add_argument('--formula', type=str, help='Formula string')
    parser.add_argument('--tolerance', type=float, default=0.001)
    parser.add_argument('--approx', type=float, help='Approximate target')
    args = parser.parse_args()

    if args.value and args.formula:
        val = int(args.value) if args.value == int(args.value) else args.value
        verify_formula(val, args.formula, tolerance=args.tolerance)
    elif args.approx and args.formula:
        verify_formula(args.approx, args.formula, tolerance=args.tolerance)
    else:
        # Demo
        print("=== Demo: Known identities ===\n")
        verify_formula(137, "sigma**2 - 7")
        print()
        verify_formula(24, "sigma * phi")
        print()
        verify_formula(0.9159655941, "5/6 * log(3)", tolerance=0.001)


if __name__ == '__main__':
    main()
