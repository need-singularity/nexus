#!/usr/bin/env python3
"""
Hypothesis Verification Calculator
=====================================================
Implementation of CLAUDE.md 5-stage verification pipeline:
  1. Reconfirm arithmetic accuracy
  2. Ad-hoc check (+1/-1 correction warning)
  3. Strong Law of Small Numbers (constant <100 warning)
  4. Generalization test (Does it hold for perfect number 28?)
  5. Texas sharpshooter p-value (Bonferroni correction)

Usage:
  python3 hypothesis_verifier.py --value 2.0 --target "sigma_inv(6)"
  python3 hypothesis_verifier.py --value 0.6931 --target "ln(2)" --tolerance 0.001
  python3 hypothesis_verifier.py --value 12 --target "sigma(6)" --generalize-28
  python3 hypothesis_verifier.py --value 1.0 --target "1/2+1/3+1/6"
  python3 hypothesis_verifier.py --value 17 --target "sigma(6)+tau(6)+1" --search-space-size 100
"""

import argparse
import math
import random
import sys
from fractions import Fraction

try:
    import tecsrs
    _HAS_TECSRS = True
except ImportError:
    _HAS_TECSRS = False

# ═══════════════════════════════════════════════════════════════
# Mathematical Constants Dictionary
# ═══════════════════════════════════════════════════════════════

MATH_CONSTANTS = {
    # Basic constants
    'pi': math.pi,
    'e': math.e,
    'phi_golden': (1 + math.sqrt(5)) / 2,  # Golden ratio
    '1/e': 1 / math.e,
    'ln(2)': math.log(2),
    'ln(3)': math.log(3),
    'ln(4)': math.log(4),
    'ln(4/3)': math.log(4 / 3),

    # Simple fractions (Golden Zone core)
    '1/2': 0.5,
    '1/3': 1.0 / 3,
    '1/6': 1.0 / 6,
    '5/6': 5.0 / 6,
    '2/3': 2.0 / 3,

    # Irrational numbers
    'sqrt(2)': math.sqrt(2),
    'sqrt(3)': math.sqrt(3),
    'sqrt(6)': math.sqrt(6),

    # Euler-Mascheroni constant
    'gamma': 0.5772156649015329,

    # Apéry's constant
    'zeta(3)': 1.2020569031595942,

    # Catalan's constant
    'catalan': 0.9159655941772190,

    # Consciousness constants (from anima)
    'Psi_steps': 3.0 / math.log(2),           # 4.328
    'Psi_balance': 0.5,                         # consciousness balance point
    'Psi_coupling': math.log(2) / 2**5.5,      # 0.01534
    'Psi_K': 11.0,                              # carrying capacity
    'Psi_freedom': math.log(2),                 # Law 79: freedom degree = ln(2)
    'Psi_emergence': 7.82,                      # hivemind emergence ratio
    'Psi_entropy': 0.998,                       # rule entropy
    'Psi_gate_decay': 0.013,                    # gate self-weakening (absolute)
    'tanh3_ln2': math.tanh(3) * math.log(2),   # 0.6895 consciousness saturation
    'conservation_C': 0.478,                     # H^2 + dp^2 conservation
    'dynamics_rate': 0.81,                       # dH/dt coefficient
    'phi_scaling_coeff': 0.608,                  # Phi = 0.608 * N^1.071
    'phi_scaling_exp': 1.071,                    # scaling exponent

    # New identities (unique to n=6)
    'sopfr_phi_sum': 10.0,                       # sopfr*phi = n+tau = 10 (unique n=6)
    'rate_product': 7.0/20.0,                     # r₀*r∞ = (n+1)/(tau*sopfr) = 7/20
    'rate_ratio': 35.0/16.0,                      # r₀/r∞ = (n²-1)/tau² = 35/16
    'r0_boundary': 7.0/8.0,                       # small-N rate limit = (n+1)/(tau*phi)
    'r_inf_boundary': 2.0/5.0,                    # large-N rate limit = phi/sopfr
}

# ═══════════════════════════════════════════════════════════════
# Perfect Number Properties
# ═══════════════════════════════════════════════════════════════

PERFECT_NUMBERS = {
    6: {
        'n': 6,
        'sigma': 12,      # Sum of divisors
        'tau': 4,          # Number of divisors
        'phi': 2,          # Euler's totient
        'sigma_inv': 2,    # Sum of reciprocals of proper divisors = sigma_{-1}(6) = 1+1/2+1/3+1/6 = 2
        'divisors': [1, 2, 3, 6],
        'proper_divisors': [1, 2, 3],
        'prime_factors': [2, 3],
        'sopfr': 5,        # Sum of prime factors 2+3
        'omega': 2,        # Number of distinct prime factors
        'mersenne_prime': 3,  # 2^p-1 = 3, p=2
    },
    28: {
        'n': 28,
        'sigma': 56,       # Sum of divisors
        'tau': 6,           # Number of divisors
        'phi': 12,          # Euler's totient
        'sigma_inv': 2,     # Sum of reciprocals of proper divisors = always 2 for perfect numbers
        'divisors': [1, 2, 4, 7, 14, 28],
        'proper_divisors': [1, 2, 4, 7, 14],
        'prime_factors': [2, 7],
        'sopfr': 9,         # 2+7
        'omega': 2,         # Number of distinct prime factors
        'mersenne_prime': 7,  # 2^p-1 = 7, p=3
    },
}

# ═══════════════════════════════════════════════════════════════
# Expression Parser
# ═══════════════════════════════════════════════════════════════

def _build_eval_namespace(n=6):
    """Build namespace for expression evaluation."""
    pn = PERFECT_NUMBERS.get(n, PERFECT_NUMBERS[6])
    ns = {
        # math functions
        'sqrt': math.sqrt,
        'log': math.log,
        'ln': math.log,
        'exp': math.exp,
        'sin': math.sin,
        'cos': math.cos,
        'abs': abs,
        'factorial': math.factorial,

        # constants
        'pi': math.pi,
        'e': math.e,
        'phi_golden': (1 + math.sqrt(5)) / 2,
        'gamma': 0.5772156649015329,
        'zeta3': 1.2020569031595942,
        'catalan': 0.9159655941772190,

        # Arithmetic functions for perfect number n
        'sigma': lambda x=None: pn['sigma'] if x is None else _sigma(x),
        'tau': lambda x=None: pn['tau'] if x is None else _tau(x),
        'phi': lambda x=None: pn['phi'] if x is None else _euler_phi(x),
        'sigma_inv': lambda x=None: pn['sigma_inv'] if x is None else _sigma_inv(x),
        'omega': lambda x=None: pn['omega'] if x is None else _omega(x),
        'sopfr': lambda x=None: pn['sopfr'] if x is None else _sopfr(x),
        'n': pn['n'],
    }
    return ns


def _divisors(n):
    """List of divisors of n."""
    divs = []
    for i in range(1, int(math.isqrt(n)) + 1):
        if n % i == 0:
            divs.append(i)
            if i != n // i:
                divs.append(n // i)
    return sorted(divs)


def _sigma(n):
    """Sum of divisors."""
    return sum(_divisors(n))


def _tau(n):
    """Number of divisors."""
    return len(_divisors(n))


def _euler_phi(n):
    """Euler's totient."""
    count = 0
    for k in range(1, n + 1):
        if math.gcd(k, n) == 1:
            count += 1
    return count


def _sigma_inv(n):
    """Sum of divisor reciprocals = sigma_{-1}(n)."""
    return sum(Fraction(1, d) for d in _divisors(n))


def _omega(n):
    """Number of distinct prime factors."""
    count = 0
    d = 2
    temp = n
    while d * d <= temp:
        if temp % d == 0:
            count += 1
            while temp % d == 0:
                temp //= d
        d += 1
    if temp > 1:
        count += 1
    return count


def _sopfr(n):
    """Sum of prime factors (with multiplicity)."""
    total = 0
    d = 2
    temp = n
    while d * d <= temp:
        while temp % d == 0:
            total += d
            temp //= d
        d += 1
    if temp > 1:
        total += temp
    return total


def parse_target(target_str, n=6):
    """
    Convert expression string to numerical value.
    Examples: "ln(2)", "sigma(6)", "1/2+1/3+1/6", "pi/6", "sigma_inv(6)"
    """
    ns = _build_eval_namespace(n)

    # Handle explicit arguments like sigma(6), tau(28)
    import re
    expr = target_str

    # Convert function(number) patterns to direct calculations
    func_map = {
        'sigma': _sigma,
        'tau': _tau,
        'phi': _euler_phi,
        'sigma_inv': lambda x: float(_sigma_inv(x)),
        'omega': _omega,
        'sopfr': _sopfr,
    }

    for fname, func in func_map.items():
        pattern = rf'{fname}\((\d+)\)'
        for match in re.finditer(pattern, expr):
            arg = int(match.group(1))
            result = func(arg)
            expr = expr.replace(match.group(0), str(float(result)))

    # Function calls without arguments → default perfect number n's value
    for fname in func_map:
        pattern = rf'\b{fname}\b(?!\()'
        if re.search(pattern, expr):
            pn = PERFECT_NUMBERS.get(n, PERFECT_NUMBERS[6])
            if fname == 'sigma_inv':
                val = float(pn['sigma_inv'])
            else:
                val = float(pn.get(fname, 0))
            expr = re.sub(pattern, str(val), expr)

    try:
        result = eval(expr, {"__builtins__": {}}, ns)
        return float(result)
    except Exception as ex:
        raise ValueError(f"Expression parsing failed: '{target_str}' -> '{expr}': {ex}")


# ═══════════════════════════════════════════════════════════════
# 5-Stage Verification Pipeline
# ═══════════════════════════════════════════════════════════════

def step1_arithmetic(value, target_val, tolerance):
    """Stage 1: Reconfirm arithmetic accuracy."""
    if target_val == 0:
        error = abs(value)
        rel_error = None
    else:
        error = abs(value - target_val)
        rel_error = abs(error / target_val)

    exact = (error == 0)
    within_tol = (error <= tolerance) if not exact else True

    return {
        'step': 1,
        'name': 'Arithmetic Accuracy',
        'value': value,
        'target': target_val,
        'error': error,
        'rel_error': rel_error,
        'exact': exact,
        'within_tolerance': within_tol,
        'passed': within_tol,
    }


def step2_adhoc(target_str):
    """Stage 2: Ad-hoc correction check (warn if +1, -1, etc. are included)."""
    # Detect correction patterns like +1, -1, +2, -2
    # Exclude numerators in fractions (1/2, 1/3, etc.): +1 followed by / is a fraction
    import re
    adhoc_patterns = [
        (r'[+\-]\s*1(?!\d)(?!\s*/)', '+1/-1 correction'),
        (r'[+\-]\s*2(?!\d)(?!\s*/)', '+2/-2 correction'),
        (r'[+\-]\s*0\.5(?!\d)', '+0.5/-0.5 correction'),
    ]

    warnings = []
    for pattern, desc in adhoc_patterns:
        if re.search(pattern, target_str):
            warnings.append(desc)

    has_adhoc = len(warnings) > 0

    return {
        'step': 2,
        'name': 'Ad-hoc Correction Check',
        'warnings': warnings,
        'has_adhoc': has_adhoc,
        'passed': not has_adhoc,
        'note': 'No corrections (Good)' if not has_adhoc else f'Warning: {", ".join(warnings)} detected',
    }


def step3_small_numbers(target_str, target_val):
    """Stage 3: Strong Law of Small Numbers check."""
    # Check if all constants involved in the formula are < 100
    import re
    numbers = re.findall(r'\d+\.?\d*', target_str)
    numeric_vals = [float(x) for x in numbers]

    all_small = all(v < 100 for v in numeric_vals) if numeric_vals else True
    # Also check target_val itself
    target_small = abs(target_val) < 100

    is_small = all_small and target_small

    return {
        'step': 3,
        'name': 'Small Numbers Check',
        'constants_in_formula': numeric_vals,
        'all_under_100': all_small,
        'target_under_100': target_small,
        'is_small_number_regime': is_small,
        'passed': True,  # Warning only, not a failure
        'warning': is_small,
        'note': 'Warning: All constants <100 (Small Numbers regime)' if is_small else 'Contains constants ≥100 (Good)',
    }


def step4_generalize_28(target_str, tolerance):
    """
    Stage 4: Test if it also holds for perfect number 28.
    Replace arithmetic functions for n=6 with n=28 and evaluate.
    """
    try:
        val_6 = parse_target(target_str, n=6)
        val_28 = parse_target(target_str, n=28)

        # Check if ratio is maintained (structural relationship)
        if val_6 != 0:
            ratio = val_28 / val_6
        else:
            ratio = None

        # Common property of perfect numbers: sigma_inv = 2 (always)
        # Structural if same value or consistent scaling
        same_value = abs(val_28 - val_6) < tolerance
        # sigma_inv relation is always 2
        both_give_2 = abs(val_6 - 2.0) < tolerance and abs(val_28 - 2.0) < tolerance

        return {
            'step': 4,
            'name': 'Generalization Test (n=28)',
            'value_n6': val_6,
            'value_n28': val_28,
            'ratio': ratio,
            'same_value': same_value,
            'both_give_2': both_give_2,
            'passed': same_value or both_give_2,
            'note': (
                'Same value (Structural!)' if same_value
                else f'n=6: {val_6:.6f}, n=28: {val_28:.6f}, ratio: {ratio:.4f}' if ratio
                else f'n=6: {val_6:.6f}, n=28: {val_28:.6f}'
            ),
        }
    except Exception as ex:
        return {
            'step': 4,
            'name': 'Generalization Test (n=28)',
            'passed': None,
            'note': f'Cannot evaluate: {ex}',
            'error': str(ex),
        }


def step5_texas_pvalue(value, target_val, tolerance, search_space_size, n_sim=200000):
    """
    Stage 5: Texas sharpshooter p-value (Bonferroni correction).
    Uses tecsrs Rust acceleration when available (5-15x speedup).
    """
    if target_val == 0:
        obs_error = abs(value)
    else:
        obs_error = abs(value - target_val) / abs(target_val)

    if _HAS_TECSRS:
        # Use Rust monte carlo: single target with observed relative error as tolerance
        rel_tol = obs_error if obs_error > 0 else 0.01
        result = tecsrs.texas_sharpshooter(
            real_hits=1,
            targets=[target_val],
            tolerances=[rel_tol],
            n_constants=len(MATH_CONSTANTS),
            n_trials=n_sim,
            seed=42,
        )
        raw_p = result.p_value
        hit_count = int(raw_p * n_sim)
    else:
        # Python fallback
        const_pool = list(MATH_CONSTANTS.values())
        hit_count = 0
        random.seed(42)
        for _ in range(n_sim):
            a = random.choice(const_pool)
            b = random.choice(const_pool)
            op = random.randint(0, 3)
            try:
                if op == 0:
                    r = a + b
                elif op == 1:
                    r = a - b
                elif op == 2:
                    r = a * b
                else:
                    if b != 0:
                        r = a / b
                    else:
                        continue
                if target_val != 0:
                    trial_error = abs(r - target_val) / abs(target_val)
                else:
                    trial_error = abs(r)
                if trial_error <= obs_error:
                    hit_count += 1
            except (OverflowError, ZeroDivisionError):
                continue
        raw_p = hit_count / n_sim

    corrected_p = min(1.0, raw_p * search_space_size)

    return {
        'step': 5,
        'name': 'Texas Sharpshooter p-value',
        'observed_rel_error': obs_error,
        'n_simulations': n_sim,
        'hits': hit_count,
        'raw_p': raw_p,
        'search_space_size': search_space_size,
        'corrected_p': corrected_p,
        'passed': corrected_p < 0.05,
        'structural': corrected_p < 0.01,
        'note': (
            f'p={corrected_p:.6f} (Bonferroni k={search_space_size})'
            + (' *** Structural!' if corrected_p < 0.01
               else ' * Significant' if corrected_p < 0.05
               else ' (Not significant)')
        ),
    }


# ═══════════════════════════════════════════════════════════════
# Grade Determination
# ═══════════════════════════════════════════════════════════════

def determine_grade(results):
    """
    Determine grade from verification results.

    Grades:
      green  = Exact equality + proven
      orange_star = Approximation + p < 0.01 (structural)
      orange = Approximation + p < 0.05 (weak evidence)
      white  = Arithmetically correct but p > 0.05 (coincidence)
      black  = Arithmetically incorrect

    No star awarded if ad-hoc correction is present.
    """
    s1 = results[0]  # Arithmetic
    s2 = results[1]  # Ad-hoc
    s5 = results[4]  # Texas

    # Arithmetic failure → refuted
    if not s1['passed']:
        return 'black', '(Refuted)'

    has_adhoc = s2['has_adhoc']

    # Exact equality
    if s1['exact']:
        return 'green', '(Exact equality)'

    # Approximation + Texas result
    p = s5.get('corrected_p', 1.0)

    if p < 0.01 and not has_adhoc:
        return 'orange_star', '(Structural approximation, p<0.01)'
    elif p < 0.05:
        return 'orange', '(Weak evidence, p<0.05)'
    else:
        return 'white', '(Possible coincidence, p>=0.05)'


GRADE_EMOJI = {
    'green': '\U0001f7e9',        # Green square
    'orange_star': '\U0001f7e7\u2b50',  # Orange + star
    'orange': '\U0001f7e7',       # Orange square
    'white': '\u26aa',            # White circle
    'black': '\u2b1b',            # Black square
}


# ═══════════════════════════════════════════════════════════════
# ASCII Report
# ═══════════════════════════════════════════════════════════════

def print_report(value, target_str, target_val, results, grade, grade_desc, do_generalize):
    """Print ASCII report of verification results."""
    w = 60
    print('=' * w)
    print('  Hypothesis Verification Report (Hypothesis Verifier)')
    print('=' * w)
    print(f'  Measured value:   {value}')
    print(f'  Formula:          {target_str}')
    print(f'  Target value:     {target_val}')
    print('-' * w)

    for r in results:
        step = r['step']
        name = r['name']
        passed = r.get('passed')

        if passed is True:
            mark = 'PASS'
        elif passed is False:
            mark = 'FAIL'
        elif passed is None:
            mark = 'N/A '
        else:
            mark = '??? '

        # Show WARN if warning present
        if r.get('warning', False) and passed:
            mark = 'WARN'

        print(f'  [{mark}] Step {step}: {name}')

        # Detailed info
        if step == 1:
            err = r['error']
            rel = r.get('rel_error')
            print(f'         Error: {err:.2e}', end='')
            if rel is not None:
                print(f'  (Relative: {rel:.2e})', end='')
            if r['exact']:
                print('  [Exact match]', end='')
            print()
        elif step == 2:
            print(f'         {r["note"]}')
        elif step == 3:
            print(f'         {r["note"]}')
            if r['constants_in_formula']:
                print(f'         Numbers in formula: {r["constants_in_formula"]}')
        elif step == 4:
            if do_generalize:
                print(f'         {r["note"]}')
            else:
                print('         (--generalize-28 not specified, skipped)')
        elif step == 5:
            print(f'         {r["note"]}')
            raw = r.get('raw_p', 0)
            print(f'         raw p={raw:.6f}, hits={r.get("hits", 0)}/{r.get("n_simulations", 0)}')

    print('-' * w)
    emoji = GRADE_EMOJI.get(grade, '?')
    print(f'  Final Grade: {emoji}  {grade.upper()} {grade_desc}')
    print('=' * w)

    # Summary bar
    s2 = results[1]
    s3 = results[2]
    warnings = []
    if s2['has_adhoc']:
        warnings.append('AD-HOC correction detected (star forbidden)')
    if s3.get('warning', False):
        warnings.append('Small Numbers regime')
    if warnings:
        print()
        for w_msg in warnings:
            print(f'  >>> Warning: {w_msg}')
        print()


# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════

def run_verification(value, target_str, tolerance=0.01, do_generalize=False,
                     search_space_size=50):
    """Run full 5-stage verification pipeline."""
    # Calculate target value
    target_val = parse_target(target_str)

    results = []

    # Step 1: Arithmetic accuracy
    r1 = step1_arithmetic(value, target_val, tolerance)
    results.append(r1)

    # Step 2: Ad-hoc check
    r2 = step2_adhoc(target_str)
    results.append(r2)

    # Step 3: Small Numbers
    r3 = step3_small_numbers(target_str, target_val)
    results.append(r3)

    # Step 4: Generalization (optional)
    if do_generalize:
        r4 = step4_generalize_28(target_str, tolerance)
    else:
        r4 = {
            'step': 4,
            'name': 'Generalization Test (n=28)',
            'passed': None,
            'note': 'Skipped (--generalize-28 needed)',
        }
    results.append(r4)

    # Step 5: Texas sharpshooter (only if arithmetic passes)
    if r1['passed']:
        r5 = step5_texas_pvalue(value, target_val, tolerance, search_space_size)
    else:
        r5 = {
            'step': 5,
            'name': 'Texas Sharpshooter p-value',
            'passed': False,
            'corrected_p': 1.0,
            'note': 'Skipped due to arithmetic failure',
        }
    results.append(r5)

    # Grade determination
    grade, grade_desc = determine_grade(results)

    # Print report
    print_report(value, target_str, target_val, results, grade, grade_desc, do_generalize)

    return grade, results


def main():
    parser = argparse.ArgumentParser(
        description='Hypothesis Verification Calculator — CLAUDE.md 5-stage pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage examples:
  %(prog)s --value 2.0 --target "sigma_inv(6)"
  %(prog)s --value 0.6931 --target "ln(2)" --tolerance 0.001
  %(prog)s --value 12 --target "sigma(6)" --generalize-28
  %(prog)s --value 1.0 --target "1/2+1/3+1/6"
  %(prog)s --value 17 --target "sigma(6)+tau(6)+1" --search-space-size 100

Available functions in formulas:
  sigma(n), tau(n), phi(n), sigma_inv(n), omega(n), sopfr(n)
  ln(x), log(x), sqrt(x), exp(x), sin(x), cos(x)
  pi, e, phi_golden, gamma, zeta3
        """,
    )
    parser.add_argument('--value', type=float, required=True,
                        help='Measured/observed value')
    parser.add_argument('--target', type=str, required=True,
                        help='Expected formula (e.g., "ln(2)", "sigma(6)", "1/2+1/3+1/6")')
    parser.add_argument('--tolerance', type=float, default=0.01,
                        help='Allowed error (default: 0.01)')
    parser.add_argument('--generalize-28', action='store_true', dest='generalize_28',
                        help='Test if it also holds for perfect number 28')
    parser.add_argument('--search-space-size', type=int, default=50, dest='search_space_size',
                        help='Search space size for Bonferroni correction (default: 50)')

    args = parser.parse_args()

    grade, results = run_verification(
        value=args.value,
        target_str=args.target,
        tolerance=args.tolerance,
        do_generalize=args.generalize_28,
        search_space_size=args.search_space_size,
    )

    # Exit code: green/orange_star=0, orange=1, white/black=2
    if grade in ('green', 'orange_star'):
        sys.exit(0)
    elif grade == 'orange':
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == '__main__':
    main()