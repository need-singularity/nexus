#!/usr/bin/env python3
"""
H-NOBEL-1: Decompose universality class exponents into n=6 arithmetic.

n=6 constants:
  n=6, sigma=12, tau=4, phi=2, sopfr=5, omega=2
  n^2=36, sigma^2=144, tau^2=16
  GZ: 1/e, 1/2, 1/3, 1/6, ln(4/3)
"""

import math
from fractions import Fraction
from itertools import product as iterproduct

# === n=6 constants ===
N = 6
SIGMA = 12      # sum of divisors
TAU = 4         # number of divisors
PHI = 2         # Euler totient
SOPFR = 5       # sum of prime factors (2+3)
OMEGA = 2       # number of distinct prime factors

# Building blocks for exact fractions
ATOMS = {
    'n': 6, 'sigma': 12, 'tau': 4, 'phi': 2, 'sopfr': 5, 'omega': 2,
    'n^2': 36, 'sigma^2': 144, 'tau^2': 16,
    '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '12': 12, '24': 24,
}

# Extended atoms for numerator/denominator search
NUM_ATOMS = list(range(0, 145))  # 0..144

# GZ constants for approximate matching
GZ_CONSTS = {
    '1/e': 1/math.e,
    'ln(4/3)': math.log(4/3),
    '1-1/e': 1 - 1/math.e,
}

# === Universality classes ===
CLASSES = {
    'Ising 2D': {
        'exact': True,
        'exponents': {
            'alpha': Fraction(0),
            'beta': Fraction(1, 8),
            'gamma': Fraction(7, 4),
            'delta': Fraction(15),
            'nu': Fraction(1),
            'eta': Fraction(1, 4),
        }
    },
    'Ising 3D': {
        'exact': False,
        'exponents': {
            'alpha': 0.110,
            'beta': 0.3265,
            'gamma': 1.2372,
            'delta': 4.789,
            'nu': 0.6301,
            'eta': 0.0364,
        }
    },
    'XY 3D': {
        'exact': False,
        'exponents': {
            'alpha': -0.0146,
            'beta': 0.3485,
            'gamma': 1.3177,
            'nu': 0.6717,
            'eta': 0.0381,
        }
    },
    'Heisenberg 3D': {
        'exact': False,
        'exponents': {
            'alpha': -0.1336,
            'beta': 0.3689,
            'gamma': 1.3960,
            'nu': 0.7112,
            'eta': 0.0375,
        }
    },
    'Mean Field': {
        'exact': True,
        'exponents': {
            'alpha': Fraction(0),
            'beta': Fraction(1, 2),
            'gamma': Fraction(1),
            'delta': Fraction(3),
            'nu': Fraction(1, 2),
            'eta': Fraction(0),
        }
    },
    'Percolation 2D': {
        'exact': True,
        'exponents': {
            'nu': Fraction(4, 3),
            'beta': Fraction(5, 36),
            'gamma': Fraction(43, 18),
            'eta': Fraction(5, 24),
        }
    },
    'SAW 2D': {
        'exact': True,
        'exponents': {
            'nu': Fraction(3, 4),
            'gamma': Fraction(43, 32),
        }
    },
    'SAW 3D': {
        'exact': False,
        'exponents': {
            'nu': 0.5876,
            'gamma': 1.1575,
        }
    },
    'Directed Percolation': {
        'exact': False,
        'exponents': {
            'beta': 0.276,
            'nu_perp': 0.7333,
            'nu_par': 1.0972,
        }
    },
    'KPZ': {
        'exact': True,
        'exponents': {
            'alpha': Fraction(1, 2),
            'beta': Fraction(1, 3),
            'z': Fraction(3, 2),
        }
    },
    'Tricritical Ising': {
        'exact': True,
        'exponents': {
            'beta': Fraction(1, 24),
            'gamma': Fraction(7, 6),
            'nu': Fraction(5, 9),
        }
    },
}

# === Search functions ===

def build_n6_fractions():
    """Build all a/b fractions where a,b come from n=6 atom values."""
    atom_vals = sorted(set(ATOMS.values()))  # unique values from atoms
    # Also include small integers and key combinations
    nums = sorted(set(list(range(0, 50)) + [v for v in atom_vals] +
                      [a+b for a in atom_vals for b in atom_vals if a+b <= 200] +
                      [a*b for a in atom_vals for b in atom_vals if a*b <= 200] +
                      [abs(a-b) for a in atom_vals for b in atom_vals]))
    dens = sorted(set([v for v in atom_vals if v > 0] +
                      list(range(1, 50)) +
                      [a*b for a in atom_vals for b in atom_vals if 0 < a*b <= 200] +
                      [a+b for a in atom_vals for b in atom_vals if a+b <= 200 and a+b > 0]))

    fracs = {}
    for n in nums:
        for d in dens:
            f = Fraction(n, d)
            if f not in fracs:
                fracs[f] = (n, d)
    return fracs

def describe_n6_fraction(num, den):
    """Try to describe num and den in terms of n=6 atoms."""
    def describe_val(v):
        # Direct atom match
        for name, val in ATOMS.items():
            if v == val:
                return name
        # Products of two atoms
        for n1, v1 in ATOMS.items():
            for n2, v2 in ATOMS.items():
                if v1 * v2 == v and v1 <= v2:
                    if n1 == '1':
                        return n2
                    return f"{n1}*{n2}"
        # Sums of two atoms
        for n1, v1 in ATOMS.items():
            for n2, v2 in ATOMS.items():
                if v1 + v2 == v:
                    return f"{n1}+{n2}"
        # Differences
        for n1, v1 in ATOMS.items():
            for n2, v2 in ATOMS.items():
                if v1 - v2 == v and v1 > v2:
                    return f"{n1}-{n2}"
        # Product + or - atom
        for n1, v1 in ATOMS.items():
            for n2, v2 in ATOMS.items():
                for n3, v3 in ATOMS.items():
                    if v1*v2 + v3 == v:
                        return f"{n1}*{n2}+{n3}"
                    if v1*v2 - v3 == v and v1*v2 > v3:
                        return f"{n1}*{n2}-{n3}"
        return str(v)

    num_desc = describe_val(num)
    den_desc = describe_val(den)

    if den == 1:
        return num_desc
    return f"({num_desc})/({den_desc})"

def search_exact(target_frac, n6_fracs):
    """Search for exact match of a Fraction in n=6 fractions."""
    if target_frac in n6_fracs:
        num, den = n6_fracs[target_frac]
        desc = describe_n6_fraction(num, den)
        return {
            'match': True,
            'exact': True,
            'value': float(target_frac),
            'expression': desc,
            'fraction': f"{num}/{den}" if den != 1 else str(num),
            'error_pct': 0.0,
        }
    return None

def search_approximate(target_val, n6_fracs, tol=0.005):
    """Search for approximate match within tolerance."""
    best = None
    best_err = tol

    for frac, (num, den) in n6_fracs.items():
        val = float(frac)
        if target_val != 0:
            err = abs(val - target_val) / abs(target_val)
        else:
            err = abs(val - target_val)
        if err < best_err:
            best_err = err
            desc = describe_n6_fraction(num, den)
            best = {
                'match': True,
                'exact': False,
                'value': val,
                'expression': desc,
                'fraction': f"{num}/{den}" if den != 1 else str(num),
                'error_pct': err * 100,
            }
    return best

def search_depth2_approximate(target_val, tol=0.01):
    """
    Depth-2: try a/b +/- c/d, a/b * c/d, etc. where a,b,c,d are n=6 atoms.
    Also try expressions involving GZ constants.
    """
    atom_vals = sorted(set(v for v in ATOMS.values() if v > 0))
    small_ints = list(range(1, 13))
    vals = sorted(set(atom_vals + small_ints))

    best = None
    best_err = tol

    # a/b + c/d and a/b - c/d
    simple_fracs = []
    for a in vals:
        for b in vals:
            simple_fracs.append((a, b, Fraction(a, b)))

    for a1, b1, f1 in simple_fracs:
        for a2, b2, f2 in simple_fracs:
            for op, op_name in [(lambda x,y: x+y, '+'), (lambda x,y: x-y, '-')]:
                val = float(op(f1, f2))
                if target_val != 0:
                    err = abs(val - target_val) / abs(target_val)
                else:
                    err = abs(val - target_val)
                if err < best_err:
                    best_err = err
                    d1 = describe_n6_fraction(a1, b1)
                    d2 = describe_n6_fraction(a2, b2)
                    best = {
                        'match': True,
                        'exact': False,
                        'value': val,
                        'expression': f"{d1} {op_name} {d2}",
                        'error_pct': err * 100,
                    }

    # GZ constant combinations: k * gz_const, a/b + gz_const, etc.
    for gz_name, gz_val in GZ_CONSTS.items():
        for a in vals:
            for b in vals:
                frac_val = a / b
                for op, op_name in [(lambda x,y: x+y, '+'), (lambda x,y: x-y, '-'),
                                     (lambda x,y: x*y, '*')]:
                    val = op(frac_val, gz_val)
                    if target_val != 0:
                        err = abs(val - target_val) / abs(target_val)
                    else:
                        err = abs(val - target_val)
                    if err < best_err:
                        best_err = err
                        d1 = describe_n6_fraction(a, b)
                        best = {
                            'match': True,
                            'exact': False,
                            'value': val,
                            'expression': f"{d1} {op_name} {gz_name}",
                            'error_pct': err * 100,
                        }
                    # Also gz / frac and frac / gz
                    if frac_val != 0:
                        val2 = gz_val / frac_val
                        err2 = abs(val2 - target_val) / abs(target_val) if target_val != 0 else abs(val2 - target_val)
                        if err2 < best_err:
                            best_err = err2
                            d1 = describe_n6_fraction(a, b)
                            best = {
                                'match': True,
                                'exact': False,
                                'value': val2,
                                'expression': f"{gz_name} / {d1}",
                                'error_pct': err2 * 100,
                            }

    return best


def search_exponent(name, target, is_exact, n6_fracs):
    """Full search pipeline for one exponent."""
    if is_exact:
        target_frac = target if isinstance(target, Fraction) else Fraction(target).limit_denominator(1000)
        target_val = float(target_frac)

        # Try exact match first
        result = search_exact(target_frac, n6_fracs)
        if result:
            return result

        # Try approximate in n6 fracs
        result = search_approximate(target_val, n6_fracs, tol=0.001)
        if result:
            return result

        return {
            'match': False,
            'value': target_val,
            'expression': '---',
            'error_pct': None,
        }
    else:
        target_val = float(target)

        # Try simple fraction match
        result = search_approximate(target_val, n6_fracs, tol=0.005)
        if result:
            return result

        # Try depth-2 expressions
        result = search_depth2_approximate(target_val, tol=0.01)
        if result:
            return result

        # Wider tolerance depth-2
        result = search_depth2_approximate(target_val, tol=0.05)
        if result:
            return result

        return {
            'match': False,
            'value': target_val,
            'expression': '---',
            'error_pct': None,
        }


def run_random_baseline(n6_fracs, n_trials=10000):
    """
    Statistical test: how often do random numbers in [0, 5] match n=6 fractions
    within the same tolerances we use?
    """
    import random
    random.seed(42)

    hits = 0
    total = n_trials
    for _ in range(total):
        target = random.uniform(-0.2, 5.0)
        result = search_approximate(target, n6_fracs, tol=0.005)
        if result is None:
            result = search_depth2_approximate(target, tol=0.01)
        if result is not None:
            hits += 1
    return hits / total


def main():
    print("=" * 70)
    print("H-NOBEL-1: Universality Class Exponents -> n=6 Arithmetic")
    print("=" * 70)
    print()

    print("Building n=6 fraction database...")
    n6_fracs = build_n6_fractions()
    print(f"  {len(n6_fracs)} unique fractions from n=6 atoms")
    print()

    all_results = []
    class_summaries = []

    for cls_name, cls_data in CLASSES.items():
        is_exact = cls_data['exact']
        exponents = cls_data['exponents']

        print(f"\n{'='*60}")
        print(f"  {cls_name}  {'(exact)' if is_exact else '(numerical)'}")
        print(f"{'='*60}")

        hits = 0
        total = len(exponents)

        for exp_name, exp_val in exponents.items():
            result = search_exponent(exp_name, exp_val, is_exact, n6_fracs)
            result['class'] = cls_name
            result['exponent'] = exp_name
            result['target'] = float(exp_val)
            all_results.append(result)

            status = "HIT" if result['match'] else "MISS"
            if result['match']:
                hits += 1
                err_str = f"{result['error_pct']:.3f}%" if result['error_pct'] > 0 else "exact"
                print(f"  {exp_name:10s} = {float(exp_val):>10.4f}  ->  {result['expression']:30s}  = {result['value']:.6f}  ({err_str})")
            else:
                print(f"  {exp_name:10s} = {float(exp_val):>10.4f}  ->  NO MATCH")

        pct = hits / total * 100
        class_summaries.append((cls_name, hits, total, pct))
        print(f"  --- {cls_name}: {hits}/{total} ({pct:.0f}%) ---")

    # === Grand summary ===
    print("\n" + "=" * 70)
    print("GRAND SUMMARY")
    print("=" * 70)

    total_hits = sum(r['match'] for r in all_results)
    total_exp = len(all_results)
    exact_results = [r for r in all_results if r.get('exact')]
    approx_results = [r for r in all_results if r['match'] and not r.get('exact')]

    print(f"\nTotal exponents tested: {total_exp}")
    print(f"Total matches:         {total_hits}/{total_exp} ({total_hits/total_exp*100:.1f}%)")
    print(f"  Exact matches:       {len(exact_results)}")
    print(f"  Approximate (<1%):   {len([r for r in approx_results if r['error_pct'] < 1.0])}")
    print(f"  Approximate (1-5%):  {len([r for r in approx_results if 1.0 <= r['error_pct'] < 5.0])}")
    print(f"  Failures:            {total_exp - total_hits}")

    print("\n--- By universality class ---")
    print(f"{'Class':25s} {'Hits':>5s} {'Total':>6s} {'Rate':>6s}")
    print("-" * 45)
    for name, hits, total, pct in class_summaries:
        print(f"{name:25s} {hits:>5d} {total:>6d} {pct:>5.0f}%")

    # === Random baseline ===
    print("\n--- Statistical baseline (random numbers) ---")
    baseline_rate = run_random_baseline(n6_fracs)
    print(f"Random baseline hit rate: {baseline_rate*100:.1f}%")
    print(f"Observed hit rate:        {total_hits/total_exp*100:.1f}%")

    if baseline_rate > 0:
        # Simple z-score
        import math
        p_hat = total_hits / total_exp
        se = math.sqrt(baseline_rate * (1-baseline_rate) / total_exp)
        z = (p_hat - baseline_rate) / se if se > 0 else 0
        print(f"Z-score:                  {z:.1f}")

    # === Master table for markdown ===
    print("\n\n=== MARKDOWN TABLE ===\n")
    print("| Class | Exponent | Target | n=6 Expression | Value | Error% | Status |")
    print("|-------|----------|--------|----------------|-------|--------|--------|")
    for r in all_results:
        target_str = f"{r['target']:.4f}"
        if r['match']:
            val_str = f"{r['value']:.6f}"
            err_str = f"{r['error_pct']:.3f}" if r['error_pct'] > 0 else "0"
            status = "exact" if r.get('exact') else "approx"
            expr = r['expression']
        else:
            val_str = "---"
            err_str = "---"
            status = "MISS"
            expr = "---"
        print(f"| {r['class']} | {r['exponent']} | {target_str} | {expr} | {val_str} | {err_str} | {status} |")

    # === Failures detail ===
    failures = [r for r in all_results if not r['match']]
    print(f"\n\n=== FAILURES ({len(failures)}) ===")
    for r in failures:
        print(f"  {r['class']:25s}  {r['exponent']:10s}  = {r['target']:.4f}")

    # === ASCII chart ===
    print("\n\n=== ERROR DISTRIBUTION (matched exponents) ===")
    matched = [r for r in all_results if r['match']]
    bins = [0, 0.001, 0.01, 0.1, 0.5, 1.0, 5.0]
    bin_labels = ['exact', '<0.01%', '<0.1%', '<0.5%', '<1%', '<5%']
    counts = [0] * len(bin_labels)
    for r in matched:
        e = r['error_pct']
        if e == 0:
            counts[0] += 1
        elif e < 0.01:
            counts[1] += 1
        elif e < 0.1:
            counts[2] += 1
        elif e < 0.5:
            counts[3] += 1
        elif e < 1.0:
            counts[4] += 1
        else:
            counts[5] += 1

    max_c = max(counts) if counts else 1
    for label, count in zip(bin_labels, counts):
        bar = '#' * int(count / max_c * 40) if max_c > 0 else ''
        print(f"  {label:>8s} | {bar} {count}")


if __name__ == '__main__':
    main()
