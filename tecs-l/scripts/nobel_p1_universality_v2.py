#!/usr/bin/env python3
"""
H-NOBEL-1 v2: HONEST decomposition of universality exponents into n=6 arithmetic.

Key difference from v1: STRICT atom set. Only genuine n=6 number-theoretic functions.
No arbitrary integers allowed in numerator/denominator.

n=6 atoms (8 values):
  n=6, sigma(6)=12, tau(6)=4, phi(6)=2, sopfr(6)=5, omega(6)=2,
  Also: 1 (identity), 0 (additive identity)

Allowed operations at each depth:
  Depth 0: single atom
  Depth 1: a op b where a,b are atoms. ops: +, -, *, /
  Depth 2: (a op b) op c where a,b,c are atoms

We count: how many of 45 exponents can be expressed this way?
Then: how often can RANDOM numbers be expressed? (proper baseline)
"""

import math
import random
from fractions import Fraction
from collections import defaultdict

# === STRICT n=6 atoms ===
ATOM_NAMES = {
    'n': 6,
    'sigma': 12,
    'tau': 4,
    'phi': 2,
    'sopfr': 5,
    'omega': 2,  # same as phi, will deduplicate
}

# Unique atom values (with multiplicities noted)
ATOMS = {
    '1': Fraction(1),
    'phi': Fraction(2),   # = omega
    'tau': Fraction(4),
    'sopfr': Fraction(5),
    'n': Fraction(6),
    'sigma': Fraction(12),
}

ATOM_LIST = list(ATOMS.items())

# === Build expression library ===

def build_depth0():
    """Single atoms."""
    exprs = {}  # value -> (expression_string, depth)
    for name, val in ATOM_LIST:
        if val not in exprs:
            exprs[val] = (name, 0)
    # Also 0
    exprs[Fraction(0)] = ('0', 0)
    return exprs

def build_depth1(depth0):
    """a op b for all atoms a, b."""
    exprs = dict(depth0)
    atoms = [(n, v) for n, v in ATOM_LIST]

    for n1, v1 in atoms:
        for n2, v2 in atoms:
            # a + b
            val = v1 + v2
            expr = f"{n1}+{n2}"
            if val not in exprs or exprs[val][1] > 1:
                exprs[val] = (expr, 1)

            # a - b
            val = v1 - v2
            if val >= Fraction(-20) and val <= Fraction(20):
                expr = f"{n1}-{n2}"
                if val not in exprs or exprs[val][1] > 1:
                    exprs[val] = (expr, 1)

            # a * b
            val = v1 * v2
            expr = f"{n1}*{n2}"
            if val not in exprs or exprs[val][1] > 1:
                exprs[val] = (expr, 1)

            # a / b
            if v2 != 0:
                val = v1 / v2
                expr = f"{n1}/{n2}"
                if val not in exprs or exprs[val][1] > 1:
                    exprs[val] = (expr, 1)

    return exprs

def build_depth2(depth1):
    """(depth1_expr) op atom, for all depth1 expressions and atoms."""
    exprs = dict(depth1)
    d1_items = list(depth1.items())
    atoms = [(n, v) for n, v in ATOM_LIST]

    for val1, (expr1, _) in d1_items:
        for n2, v2 in atoms:
            # expr1 + atom
            val = val1 + v2
            expr = f"({expr1})+{n2}"
            if val not in exprs or exprs[val][1] > 2:
                exprs[val] = (expr, 2)

            # expr1 - atom
            val = val1 - v2
            expr = f"({expr1})-{n2}"
            if val not in exprs or exprs[val][1] > 2:
                exprs[val] = (expr, 2)

            # atom - expr1
            val = v2 - val1
            expr = f"{n2}-({expr1})"
            if val not in exprs or exprs[val][1] > 2:
                exprs[val] = (expr, 2)

            # expr1 * atom
            val = val1 * v2
            expr = f"({expr1})*{n2}"
            if val not in exprs or exprs[val][1] > 2:
                exprs[val] = (expr, 2)

            # expr1 / atom
            if v2 != 0:
                val = val1 / v2
                expr = f"({expr1})/{n2}"
                if val not in exprs or exprs[val][1] > 2:
                    exprs[val] = (expr, 2)

            # atom / expr1
            if val1 != 0:
                val = v2 / val1
                expr = f"{n2}/({expr1})"
                if val not in exprs or exprs[val][1] > 2:
                    exprs[val] = (expr, 2)

    # Also: depth1 op depth1 (two-operand depth 2)
    for val1, (expr1, d1) in d1_items:
        if d1 > 1:
            continue  # only combine actual depth-0 or depth-1
        for val2, (expr2, d2) in d1_items:
            if d2 > 1:
                continue

            # d1 + d1
            val = val1 + val2
            expr = f"({expr1})+({expr2})"
            if val not in exprs or exprs[val][1] > 2:
                exprs[val] = (expr, 2)

            # d1 - d1
            val = val1 - val2
            expr = f"({expr1})-({expr2})"
            if val not in exprs or exprs[val][1] > 2:
                exprs[val] = (expr, 2)

            # d1 * d1
            val = val1 * val2
            expr = f"({expr1})*({expr2})"
            if val not in exprs or exprs[val][1] > 2:
                exprs[val] = (expr, 2)

            # d1 / d1
            if val2 != 0:
                val = val1 / val2
                expr = f"({expr1})/({expr2})"
                if val not in exprs or exprs[val][1] > 2:
                    exprs[val] = (expr, 2)

    return exprs


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


def match_exact(target_frac, expr_db):
    """Try exact fraction match."""
    if target_frac in expr_db:
        expr, depth = expr_db[target_frac]
        return {
            'match': True, 'exact_match': True,
            'value': float(target_frac), 'expression': expr, 'depth': depth,
            'error_pct': 0.0,
        }
    return None

def match_approximate(target_val, expr_db, tol=0.005):
    """Find closest expression within tolerance."""
    best = None
    best_err = tol
    for frac_val, (expr, depth) in expr_db.items():
        val = float(frac_val)
        if target_val != 0:
            err = abs(val - target_val) / abs(target_val)
        else:
            err = abs(val - target_val)
        if err < best_err:
            best_err = err
            best = {
                'match': True, 'exact_match': (err == 0),
                'value': val, 'expression': expr, 'depth': depth,
                'error_pct': err * 100,
            }
    return best


def search_exponent(name, target, is_exact, expr_db):
    """Search for match."""
    if is_exact:
        target_frac = target if isinstance(target, Fraction) else Fraction(target).limit_denominator(1000)
        result = match_exact(target_frac, expr_db)
        if result:
            return result
        # Also try approximate in case of rounding
        return match_approximate(float(target_frac), expr_db, tol=0.001) or {
            'match': False, 'value': float(target_frac), 'expression': '---', 'error_pct': None
        }
    else:
        # For numerical exponents, allow 0.5% tolerance
        result = match_approximate(float(target), expr_db, tol=0.005)
        if result:
            return result
        # Wider: 1%
        result = match_approximate(float(target), expr_db, tol=0.01)
        if result:
            return result
        return {
            'match': False, 'value': float(target), 'expression': '---', 'error_pct': None
        }


def random_baseline(expr_db, n_trials=50000, tol=0.005):
    """What fraction of random numbers in [-0.2, 5] match within tolerance?"""
    random.seed(42)
    hits = 0
    for _ in range(n_trials):
        target = random.uniform(-0.2, 5.0)
        result = match_approximate(target, expr_db, tol=tol)
        if result:
            hits += 1
    return hits / n_trials


def random_baseline_exact(expr_db, n_trials=50000):
    """What fraction of random rationals p/q (small q) match exactly?"""
    random.seed(42)
    hits = 0
    for _ in range(n_trials):
        # Generate random fraction with denominator up to 36
        num = random.randint(-5, 50)
        den = random.randint(1, 36)
        f = Fraction(num, den)
        if f in expr_db:
            hits += 1
    return hits / n_trials


def main():
    print("=" * 72)
    print("H-NOBEL-1 v2: STRICT n=6 Arithmetic Decomposition")
    print("  Atoms: {1, phi=2, tau=4, sopfr=5, n=6, sigma=12}")
    print("  Depth 0: single atom")
    print("  Depth 1: atom op atom")
    print("  Depth 2: (atom op atom) op atom, or (d1) op (d1)")
    print("=" * 72)

    # Build expression database
    print("\nBuilding expression database...")
    d0 = build_depth0()
    print(f"  Depth 0: {len(d0)} unique values")
    d1 = build_depth1(d0)
    print(f"  Depth 1: {len(d1)} unique values")
    d2 = build_depth2(d1)
    print(f"  Depth 2: {len(d2)} unique values")

    # Show coverage: how many distinct rationals in [0,5] does depth-2 cover?
    in_range = sum(1 for v in d2 if Fraction(-1) <= v <= Fraction(20))
    print(f"  Values in [-1, 20]: {in_range}")

    all_results = []
    class_summaries = []

    for cls_name, cls_data in CLASSES.items():
        is_exact = cls_data['exact']
        exponents = cls_data['exponents']

        print(f"\n{'='*65}")
        print(f"  {cls_name}  {'(exact)' if is_exact else '(numerical, tol=0.5%/1%)'}")
        print(f"{'='*65}")

        hits = 0
        total = len(exponents)

        for exp_name, exp_val in exponents.items():
            result = search_exponent(exp_name, exp_val, is_exact, d2)
            result['class'] = cls_name
            result['exponent'] = exp_name
            result['target'] = float(exp_val)
            all_results.append(result)

            if result['match']:
                hits += 1
                err_str = f"{result['error_pct']:.3f}%" if result['error_pct'] > 0 else "EXACT"
                print(f"  {exp_name:10s} = {float(exp_val):>10.4f}  ->  {result['expression']:35s}  = {result['value']:.6f}  [{err_str}, d={result['depth']}]")
            else:
                print(f"  {exp_name:10s} = {float(exp_val):>10.4f}  ->  NO MATCH")

        pct = hits / total * 100
        class_summaries.append((cls_name, hits, total, pct, is_exact))
        print(f"  --- {cls_name}: {hits}/{total} ({pct:.0f}%) ---")

    # === Grand summary ===
    print("\n" + "=" * 72)
    print("GRAND SUMMARY")
    print("=" * 72)

    total_hits = sum(1 for r in all_results if r['match'])
    total_exp = len(all_results)
    exact_classes = [r for r in all_results if r['class'] in
                     [c for c, d in CLASSES.items() if d['exact']]]
    numerical_classes = [r for r in all_results if r['class'] in
                         [c for c, d in CLASSES.items() if not d['exact']]]

    exact_hits = sum(1 for r in exact_classes if r['match'])
    exact_total = len(exact_classes)
    num_hits = sum(1 for r in numerical_classes if r['match'])
    num_total = len(numerical_classes)

    print(f"\nTotal exponents tested:     {total_exp}")
    print(f"Total matches:             {total_hits}/{total_exp} ({total_hits/total_exp*100:.1f}%)")
    print(f"  Exact classes (known):   {exact_hits}/{exact_total} ({exact_hits/exact_total*100:.1f}%)")
    print(f"  Numerical classes:       {num_hits}/{num_total} ({num_hits/num_total*100:.1f}%)")
    print(f"  Exact value matches:     {sum(1 for r in all_results if r.get('exact_match'))}")
    print(f"  Approx matches (<1%):    {sum(1 for r in all_results if r['match'] and not r.get('exact_match') and r['error_pct'] < 1.0)}")

    print("\n--- By universality class ---")
    print(f"{'Class':25s} {'Type':>8s} {'Hits':>5s} {'Total':>6s} {'Rate':>6s}")
    print("-" * 55)
    for name, hits, total, pct, is_exact in class_summaries:
        typ = "exact" if is_exact else "num"
        print(f"{name:25s} {typ:>8s} {hits:>5d} {total:>6d} {pct:>5.0f}%")

    # === Failures ===
    failures = [r for r in all_results if not r['match']]
    if failures:
        print(f"\n--- FAILURES ({len(failures)}) ---")
        for r in failures:
            print(f"  {r['class']:25s}  {r['exponent']:10s}  = {r['target']:.4f}")
    else:
        print("\n--- No failures ---")

    # === Statistical baseline ===
    print("\n--- Statistical Baseline ---")
    print("Testing: how often do RANDOM numbers match n=6 expressions?")

    # Test with same tolerance as numerical exponents
    bl_05 = random_baseline(d2, n_trials=50000, tol=0.005)
    bl_10 = random_baseline(d2, n_trials=50000, tol=0.01)
    print(f"  Random baseline (tol=0.5%): {bl_05*100:.1f}%")
    print(f"  Random baseline (tol=1.0%): {bl_10*100:.1f}%")

    # For exact fractions
    bl_exact = random_baseline_exact(d2, n_trials=50000)
    print(f"  Random exact fraction hit:  {bl_exact*100:.1f}%")

    # Proper significance test
    # For numerical exponents (21 tested, using 1% tol)
    if num_total > 0:
        p_base = bl_10  # baseline for 1% tolerance
        import scipy.stats as stats
        # Binomial test: observed num_hits out of num_total, expected p_base
        pval = stats.binom_test(num_hits, num_total, p_base, alternative='greater') if hasattr(stats, 'binom_test') else None
        if pval is None:
            # scipy >= 1.7
            from scipy.stats import binomtest
            res = binomtest(num_hits, num_total, p_base, alternative='greater')
            pval = res.pvalue

        se = math.sqrt(p_base * (1-p_base) / num_total) if p_base > 0 else 0.001
        z = (num_hits/num_total - p_base) / se if se > 0 else 0

        print(f"\n  Numerical exponents: {num_hits}/{num_total} matched")
        print(f"  Expected by chance:  {p_base*100:.1f}% = {p_base*num_total:.1f}/{num_total}")
        print(f"  Binomial p-value:    {pval:.6f}")
        print(f"  Z-score:             {z:.1f}")

    # === Error distribution ===
    print("\n--- Error Distribution (matched exponents) ---")
    matched = [r for r in all_results if r['match']]
    bins_labels = [
        ('EXACT',  lambda e: e == 0),
        ('<0.01%', lambda e: 0 < e < 0.01),
        ('<0.1%',  lambda e: 0.01 <= e < 0.1),
        ('<0.5%',  lambda e: 0.1 <= e < 0.5),
        ('<1.0%',  lambda e: 0.5 <= e < 1.0),
    ]
    max_c = 0
    counts = []
    for label, cond in bins_labels:
        c = sum(1 for r in matched if cond(r['error_pct']))
        counts.append(c)
        max_c = max(max_c, c)

    for (label, _), count in zip(bins_labels, counts):
        bar = '#' * int(count / max_c * 40) if max_c > 0 else ''
        print(f"  {label:>8s} | {bar} {count}")

    # === Markdown table ===
    print("\n\n=== MARKDOWN TABLE (for hypothesis document) ===\n")
    print("| Class | Exponent | Target | n=6 Expression | Value | Error% | Depth |")
    print("|-------|----------|--------|----------------|-------|--------|-------|")
    for r in all_results:
        target_str = f"{r['target']:.4f}"
        if r['match']:
            val_str = f"{r['value']:.6f}"
            err_str = f"{r['error_pct']:.3f}" if r['error_pct'] > 0 else "0"
            expr = r['expression']
            depth = str(r.get('depth', '?'))
        else:
            val_str = "---"
            err_str = "MISS"
            expr = "---"
            depth = "---"
        print(f"| {r['class']} | {r['exponent']} | {target_str} | `{expr}` | {val_str} | {err_str} | {depth} |")

    # === Check Percolation 2D specifically ===
    print("\n\n=== PERCOLATION 2D DETAIL (reference check) ===")
    perc = CLASSES['Percolation 2D']['exponents']
    for name, val in perc.items():
        print(f"  {name} = {val} = {float(val):.6f}")
        if val in d2:
            expr, depth = d2[val]
            print(f"    -> {expr} (depth {depth})")

    # === Key question: do EXACT exponents have special structure? ===
    print("\n\n=== EXACT CLASS ANALYSIS ===")
    print("All exact exponents are rational. Question: are their denominators")
    print("always products of divisors of 6 (i.e., 1,2,3,6)?")
    print()
    for cls_name, cls_data in CLASSES.items():
        if not cls_data['exact']:
            continue
        for exp_name, exp_val in cls_data['exponents'].items():
            f = exp_val if isinstance(exp_val, Fraction) else Fraction(exp_val).limit_denominator(1000)
            den = f.denominator
            # Factor the denominator
            factors = []
            d = den
            for p in [2, 3, 5, 7, 11, 13]:
                while d % p == 0:
                    factors.append(p)
                    d //= p
            if d > 1:
                factors.append(d)
            only_23 = all(p in [2, 3] for p in factors)
            marker = "YES" if only_23 else f"NO (has {[p for p in factors if p not in [2,3]]})"
            print(f"  {cls_name:20s} {exp_name:8s} = {str(f):8s}  den={den:4d}  factors={factors}  div6-only: {marker}")


if __name__ == '__main__':
    main()
