#!/usr/bin/env python3
"""
Claim Verification Calculator
=====================================================
Comprehensive pre-publication verification for mathematical claims.
Catches false claims BEFORE they are published.

Designed to prevent errors like:
  - H-PH-15: "Anomaly cancellation <-> perfect numbers" claimed PROVEN
    but biconditional not established
  - del Pezzo |Aut(S_6)| = 72 was FALSE (Aut is infinite)
  - pi_6(S^3) = sigma(6) was coincidental (12 = 24/2 from Bernoulli)
  - H-PH-27 FQHE match was chance (Texas p=0.40)

Pipeline:
  1. Arithmetic verification (exact or tolerance)
  2. Ad hoc correction detection (+1/-1 flags)
  3. Texas Sharpshooter Monte Carlo (p-value)
  4. Generalization test (other perfect numbers)
  5. Claim text pitfall scan (overclaim patterns)
  6. Grade assignment

Usage:
  python3 calc/claim_verifier.py --help
  python3 calc/claim_verifier.py --claim "sigma*tau*sopfr" --target 240
  python3 calc/claim_verifier.py --texas 240 --factors 3
  python3 calc/claim_verifier.py --generalize "sigma*tau" --perfect-numbers
  python3 calc/claim_verifier.py --full "pi_6(S3) = sigma(6)" --target 12
  python3 calc/claim_verifier.py --pitfalls "This is proven: A iff B"
  python3 calc/claim_verifier.py --batch claims.json
"""

import argparse
import itertools
import json
import math
import os
import random
import re
import sys
from fractions import Fraction

# ═══════════════════════════════════════════════════════════════
# Number-Theoretic Helpers
# ═══════════════════════════════════════════════════════════════

def divisors(n):
    """Return sorted list of all divisors of n."""
    divs = []
    for i in range(1, int(math.isqrt(n)) + 1):
        if n % i == 0:
            divs.append(i)
            if i != n // i:
                divs.append(n // i)
    return sorted(divs)


def sigma(n):
    """Sum of divisors of n."""
    return sum(divisors(n))


def tau(n):
    """Number of divisors of n."""
    return len(divisors(n))


def euler_phi(n):
    """Euler's totient function."""
    count = 0
    for k in range(1, n + 1):
        if math.gcd(k, n) == 1:
            count += 1
    return count


def sigma_neg1(n):
    """Sum of reciprocals of divisors: sigma_{-1}(n)."""
    return float(sum(Fraction(1, d) for d in divisors(n)))


def sopfr(n):
    """Sum of prime factors with multiplicity."""
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


def omega(n):
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


def bigomega(n):
    """Number of prime factors with multiplicity."""
    count = 0
    d = 2
    temp = n
    while d * d <= temp:
        while temp % d == 0:
            count += 1
            temp //= d
        d += 1
    if temp > 1:
        count += 1
    return count


# ═══════════════════════════════════════════════════════════════
# Perfect Number Properties Database
# ═══════════════════════════════════════════════════════════════

def _perfect_number_props(n):
    """Compute all standard number-theoretic properties of n."""
    return {
        'n': n,
        'sigma': sigma(n),
        'tau': tau(n),
        'phi': euler_phi(n),
        'sigma_neg1': sigma_neg1(n),
        'sopfr': sopfr(n),
        'omega': omega(n),
        'bigomega': bigomega(n),
        'divisors': divisors(n),
        'sigma_sigma': sigma(sigma(n)),
    }

# Pre-computed for speed
PERFECT_NUMBERS = [6, 28, 496, 8128]
N6_PROPS = _perfect_number_props(6)

# Named constants available in expressions
N6 = {
    'n': 6, 'sigma': 12, 'phi': 2, 'tau': 4,
    'sopfr': 5, 'sigma_neg1': 2, 'omega': 2,
    'bigomega': 2, 'sigma_sigma': 28,
    'P2': 28, 'P3': 496, 'P4': 8128,
}


def _build_eval_namespace(n=6):
    """Build safe namespace for evaluating claim expressions."""
    props = _perfect_number_props(n) if n != 6 else N6_PROPS
    ns = {
        'sqrt': math.sqrt,
        'log': math.log,
        'ln': math.log,
        'exp': math.exp,
        'sin': math.sin,
        'cos': math.cos,
        'abs': abs,
        'factorial': math.factorial,
        'pi': math.pi,
        'e': math.e,
        'phi_golden': (1 + math.sqrt(5)) / 2,
        'gamma': 0.5772156649015329,
        'zeta3': 1.2020569031595942,
        # Number-theoretic values for current n
        'n': props['n'],
        'sigma': props['sigma'],
        'tau': props['tau'],
        'phi': props['phi'],
        'sigma_neg1': props['sigma_neg1'],
        'sopfr': props['sopfr'],
        'omega': props['omega'],
        'bigomega': props['bigomega'],
        'sigma_sigma': props['sigma_sigma'],
    }
    return ns


def safe_eval(expr, n=6):
    """Evaluate a mathematical expression in a restricted namespace.

    Returns (value, error_string). On success error_string is None.
    """
    ns = _build_eval_namespace(n)
    try:
        val = eval(expr, {"__builtins__": {}}, ns)
        return float(val), None
    except Exception as exc:
        return None, str(exc)


# ═══════════════════════════════════════════════════════════════
# 1. Arithmetic Verification
# ═══════════════════════════════════════════════════════════════

def verify_arithmetic(expression, expected, tolerance=0, n=6):
    """Verify that expression evaluates to expected value.

    Args:
        expression: string expression using n6 constants (e.g. "sigma*tau")
        expected: target numeric value
        tolerance: allowed absolute error (0 = exact match)
        n: perfect number context (default 6)

    Returns:
        dict with keys: ok, computed, expected, error, exact, tolerance_used
    """
    computed, err = safe_eval(expression, n=n)
    if err is not None:
        return {
            'ok': False, 'computed': None, 'expected': expected,
            'error': err, 'exact': False, 'tolerance_used': tolerance,
        }

    if tolerance == 0:
        # For integer targets, check exact integer match
        if isinstance(expected, int) or (isinstance(expected, float) and expected == int(expected)):
            exact = (round(computed) == int(expected) and abs(computed - expected) < 1e-9)
        else:
            exact = abs(computed - expected) < 1e-12
        return {
            'ok': exact, 'computed': computed, 'expected': expected,
            'error': abs(computed - expected), 'exact': True,
            'tolerance_used': 0,
        }
    else:
        within = abs(computed - expected) <= tolerance
        return {
            'ok': within, 'computed': computed, 'expected': expected,
            'error': abs(computed - expected), 'exact': False,
            'tolerance_used': tolerance,
        }


# ═══════════════════════════════════════════════════════════════
# 2. Ad Hoc Correction Detection
# ═══════════════════════════════════════════════════════════════

_ADHOC_PATTERNS = [
    (r'[+\-]\s*1\b', '+1/-1 correction detected'),
    (r'[+\-]\s*2\b', '+2/-2 correction detected'),
    (r'\bfloor\b|\bceil\b|\bround\b', 'rounding function detected'),
    (r'\bint\(', 'integer cast detected (possible rounding)'),
]


def detect_adhoc(expression):
    """Detect ad hoc corrections like +1/-1 in an expression.

    Per TECS-L rules: +1/-1 corrections DISQUALIFY a claim from star grade.

    Returns:
        list of (pattern_matched, warning_message)
    """
    warnings = []
    for pattern, msg in _ADHOC_PATTERNS:
        if re.search(pattern, expression):
            warnings.append((pattern, msg))
    return warnings


# ═══════════════════════════════════════════════════════════════
# 3. Texas Sharpshooter Test
# ═══════════════════════════════════════════════════════════════

def texas_sharpshooter(target, n_factors=3, n_trials=100000,
                       operations=None, value_pool=None, seed=42):
    """Monte Carlo test: how likely do random small-integer combinations hit the target?

    Generates random tuples of small integers, applies all binary operation
    combinations, and counts how often the target is hit.

    Args:
        target: numeric value to hit
        n_factors: how many operands per trial (default 3)
        n_trials: number of Monte Carlo trials
        operations: list of operation chars (default ['+','-','*','/'])
        value_pool: list of integers to draw from (default 1..20)
        seed: random seed for reproducibility

    Returns:
        dict with keys: p_value, z_score, hits, n_trials, grade_flag
    """
    if operations is None:
        operations = ['+', '-', '*', '/']
    if value_pool is None:
        value_pool = list(range(1, 21))

    rng = random.Random(seed)
    op_funcs = {
        '+': lambda a, b: a + b,
        '-': lambda a, b: a - b,
        '*': lambda a, b: a * b,
        '/': lambda a, b: a / b if b != 0 else float('inf'),
    }
    active_ops = [op_funcs[o] for o in operations if o in op_funcs]
    n_ops = len(active_ops)

    # Pre-compute all operation sequences for n_factors-1 slots
    op_sequences = list(itertools.product(range(n_ops), repeat=n_factors - 1))

    # Tolerance for matching: integers exact, floats within 1e-6
    if target == int(target):
        tol = 0.5
    else:
        tol = max(abs(target) * 1e-6, 1e-9)

    hits = 0
    for _ in range(n_trials):
        vals = [rng.choice(value_pool) for _ in range(n_factors)]
        for ops_idx in op_sequences:
            result = float(vals[0])
            for j, oi in enumerate(ops_idx):
                try:
                    result = active_ops[oi](result, float(vals[j + 1]))
                except (ZeroDivisionError, OverflowError):
                    continue
            if abs(result - target) < tol:
                hits += 1
                break  # count each trial at most once

    p_value = hits / n_trials
    # Z-score: how many SDs above expected under null
    if p_value > 0 and p_value < 1:
        se = math.sqrt(p_value * (1 - p_value) / n_trials)
        z_score = p_value / se if se > 0 else 0
    else:
        z_score = 0.0 if p_value == 0 else float('inf')

    if p_value > 0.05:
        grade_flag = 'COINCIDENCE'
    elif p_value > 0.01:
        grade_flag = 'BORDERLINE'
    else:
        grade_flag = 'SIGNIFICANT'

    return {
        'p_value': p_value,
        'z_score': z_score,
        'hits': hits,
        'n_trials': n_trials,
        'grade_flag': grade_flag,
        'target': target,
        'n_factors': n_factors,
    }


# ═══════════════════════════════════════════════════════════════
# 4. Generalization Test
# ═══════════════════════════════════════════════════════════════

def generalization_test(expression, target_expr=None, target_value=None,
                        test_values=None, tolerance=0):
    """Check if a formula that works for n=6 also works for other perfect numbers.

    Args:
        expression: formula string using n6 variable names (sigma, tau, etc.)
        target_expr: optional target expression to compare against
        target_value: fixed target value (used if target_expr is None)
        test_values: list of perfect numbers to test (default [28, 496, 8128])
        tolerance: allowed error

    Returns:
        dict with pass_count, fail_count, details per perfect number
    """
    if test_values is None:
        test_values = [28, 496, 8128]

    results = []
    pass_count = 0

    for pn in test_values:
        computed, err1 = safe_eval(expression, n=pn)
        if err1:
            results.append({'n': pn, 'ok': False, 'error': err1})
            continue

        if target_expr is not None:
            target, err2 = safe_eval(target_expr, n=pn)
            if err2:
                results.append({'n': pn, 'ok': False, 'error': err2})
                continue
        elif target_value is not None:
            target = target_value
        else:
            # No target: just report computed value
            results.append({'n': pn, 'ok': None, 'computed': computed})
            continue

        diff = abs(computed - target)
        ok = diff <= tolerance if tolerance > 0 else diff < 1e-9
        if ok:
            pass_count += 1
        results.append({
            'n': pn, 'ok': ok, 'computed': computed,
            'target': target, 'diff': diff,
        })

    fail_count = sum(1 for r in results if r.get('ok') is False)
    return {
        'pass_count': pass_count,
        'fail_count': fail_count,
        'total': len(results),
        'details': results,
        'n6_only': (pass_count == 0 and fail_count > 0),
    }


# ═══════════════════════════════════════════════════════════════
# 5. Common Pitfall Checks
# ═══════════════════════════════════════════════════════════════

_PITFALL_RULES = [
    {
        'pattern': r'\bproven\b|\bproof\b|\bproved\b',
        'level': 'WARNING',
        'msg': '"proven/proof" used without peer-reviewed publication. '
               'Per TECS-L rules, only pure math proofs independent of '
               'Golden Zone count as proven.',
    },
    {
        'pattern': r'\biff\b|<->|\\leftrightarrow|\\iff|\u2194',
        'level': 'WARNING',
        'msg': 'Biconditional (iff/<->) requires proving BOTH directions. '
               'Check that A->B AND B->A are independently established. '
               '(cf. H-PH-15 error: biconditional claimed but only one '
               'direction shown.)',
    },
    {
        'pattern': r'\bunique\b|\bonly\b.*\bsatisf',
        'level': 'WARNING',
        'msg': '"unique/only" claim requires exhaustive search or proof '
               'of uniqueness. Have all alternatives been ruled out?',
    },
    {
        'pattern': r'\bfinite\b.*\b(group|order|auto)',
        'level': 'WARNING',
        'msg': 'Finite group/order claimed. Verify the group is actually '
               'finite. (cf. del Pezzo Aut(S_6) error: automorphism group '
               'is infinite, not |Aut|=72.)',
    },
    {
        'pattern': r'\|Aut\b',
        'level': 'WARNING',
        'msg': 'Automorphism group order cited. Verify: is the full '
               'automorphism group finite? Some algebraic varieties have '
               'infinite automorphism groups.',
    },
    {
        'pattern': r'\bpi_\d+\(S\^?\d+\)',
        'level': 'CAUTION',
        'msg': 'Homotopy group match detected. Many homotopy group values '
               'are small integers that coincide with number-theoretic '
               'functions by chance. Run Texas Sharpshooter test. '
               '(cf. pi_6(S^3)=12=sigma(6) was coincidental.)',
    },
    {
        'pattern': r'[+\-]\s*1\s*[=)]',
        'level': 'DISQUALIFIED',
        'msg': '+1/-1 ad hoc correction in formula. Per TECS-L CLAUDE.md '
               'rules: equations with +1/-1 corrections cannot receive '
               'star grade.',
    },
    {
        'pattern': r'\bcorresponds?\b.*\bexactly\b|\bexact\s+match\b',
        'level': 'CAUTION',
        'msg': '"exact match/corresponds exactly" is a strong claim. '
               'Verify arithmetic is truly exact (not rounded). Check if '
               'the match is structural or coincidental (Texas test).',
    },
    {
        'pattern': r'\bFQHE\b|\bfractional quantum Hall\b',
        'level': 'CAUTION',
        'msg': 'FQHE filling fraction match. FQHE fractions are dense in '
               'rationals; matching by chance is likely. '
               '(cf. H-PH-27 FQHE match had Texas p=0.40.)',
    },
    {
        'pattern': r'\bMajor Discovery\b|\b(star|star)\s*(star|star)\s*(star|star)\b',
        'level': 'WARNING',
        'msg': 'Major Discovery or multi-star grade assigned. Per CLAUDE.md: '
               'grading before full verification pipeline is prohibited. '
               'Run complete pipeline first.',
    },
]


def check_pitfalls(claim_text):
    """Scan claim text for common overclaim patterns.

    Returns:
        list of dicts with keys: level, msg, match
    """
    findings = []
    for rule in _PITFALL_RULES:
        m = re.search(rule['pattern'], claim_text, re.IGNORECASE)
        if m:
            findings.append({
                'level': rule['level'],
                'msg': rule['msg'],
                'match': m.group(0),
            })
    return findings


# ═══════════════════════════════════════════════════════════════
# 6. Claim Grade Assignment
# ═══════════════════════════════════════════════════════════════

def grade_claim(arithmetic_ok, texas_p=None, generalizes=None,
                has_adhoc=False, is_tautological=False):
    """Assign grade to a claim based on verification results.

    Grading scale (from CLAUDE.md):
        BLACK_WRONG:  arithmetic wrong
        WHITE_COINC:  arithmetically correct but Texas p>0.05 (coincidence)
        ORANGE:       exact + Texas p<0.05 (weak evidence)
        ORANGE_STAR:  exact + Texas p<0.01 (structural)
        GREEN:        exact + Texas p<0.01 + verified
        GREEN_STAR:   exact + Texas p<0.01 + generalizes or proves unique

    Returns:
        dict with grade, emoji, reasoning
    """
    if not arithmetic_ok:
        return {
            'grade': 'BLACK_WRONG',
            'emoji': '\u2b1b',
            'label': 'Arithmetically wrong (refuted)',
            'reasoning': 'Arithmetic verification failed.',
        }

    if has_adhoc:
        return {
            'grade': 'WHITE_COINC',
            'emoji': '\u26aa',
            'label': 'Ad hoc correction (coincidence)',
            'reasoning': '+1/-1 or similar correction detected. '
                         'Per TECS-L rules, ad hoc corrections are disqualified from star grade.',
        }

    if texas_p is not None and texas_p > 0.05:
        return {
            'grade': 'WHITE_COINC',
            'emoji': '\u26aa',
            'label': 'Coincidence (Texas p > 0.05)',
            'reasoning': f'Texas Sharpshooter p = {texas_p:.4f}. '
                         f'Cannot reject null hypothesis of chance match.',
        }

    if texas_p is not None and texas_p > 0.01:
        return {
            'grade': 'ORANGE',
            'emoji': '\U0001f7e7',
            'label': 'Weak evidence (Texas p < 0.05)',
            'reasoning': f'Texas p = {texas_p:.4f}. Borderline significant. '
                         f'Needs stronger evidence or generalization.',
        }

    # texas_p <= 0.01 or not tested
    if generalizes is True:
        return {
            'grade': 'GREEN_STAR',
            'emoji': '\U0001f7e9\u2b50',
            'label': 'Verified + generalizes',
            'reasoning': 'Exact arithmetic, Texas p < 0.01, '
                         'and generalizes to other perfect numbers.',
        }

    if texas_p is not None and texas_p <= 0.01:
        return {
            'grade': 'ORANGE_STAR',
            'emoji': '\U0001f7e7\u2b50',
            'label': 'Structural (Texas p < 0.01)',
            'reasoning': f'Texas p = {texas_p:.4f}. Structurally significant.',
        }

    # Fallback: arithmetic ok but no Texas test run
    return {
        'grade': 'GREEN',
        'emoji': '\U0001f7e9',
        'label': 'Arithmetically correct (not fully tested)',
        'reasoning': 'Arithmetic verified. Run Texas Sharpshooter and '
                     'generalization tests for full grading.',
    }


# ═══════════════════════════════════════════════════════════════
# 7. Full Verification Pipeline
# ═══════════════════════════════════════════════════════════════

def full_verification(expression, target, claim_text='',
                      tolerance=0, n_trials=100000,
                      n_factors=3, test_generalization=True):
    """Run the complete verification pipeline on a claim.

    Args:
        expression: formula string (e.g. "sigma*tau*sopfr")
        target: expected numeric value
        claim_text: optional claim text for pitfall scanning
        tolerance: arithmetic tolerance
        n_trials: Monte Carlo trials for Texas test
        n_factors: operand count for Texas test
        test_generalization: whether to run generalization test

    Returns:
        dict with all verification results and final grade
    """
    report = {'expression': expression, 'target': target}

    # Step 1: Arithmetic
    arith = verify_arithmetic(expression, target, tolerance=tolerance)
    report['arithmetic'] = arith

    # Step 2: Ad hoc detection
    adhoc = detect_adhoc(expression)
    report['adhoc'] = adhoc

    # Step 3: Texas Sharpshooter
    texas = texas_sharpshooter(target, n_factors=n_factors, n_trials=n_trials)
    report['texas'] = texas

    # Step 4: Generalization
    if test_generalization:
        gen = generalization_test(expression, target_value=target)
        report['generalization'] = gen
    else:
        gen = None
        report['generalization'] = None

    # Step 5: Pitfalls
    if claim_text:
        pitfalls = check_pitfalls(claim_text)
    else:
        pitfalls = check_pitfalls(expression)
    report['pitfalls'] = pitfalls

    # Step 6: Grade
    generalizes = gen['pass_count'] > 0 if gen else None
    has_adhoc = len(adhoc) > 0
    grade = grade_claim(
        arithmetic_ok=arith['ok'],
        texas_p=texas['p_value'],
        generalizes=generalizes,
        has_adhoc=has_adhoc,
    )
    report['grade'] = grade

    return report


# ═══════════════════════════════════════════════════════════════
# 8. Batch Verification
# ═══════════════════════════════════════════════════════════════

def verify_batch(claims_file):
    """Verify all claims from a JSON file.

    Expected JSON format:
    [
        {
            "name": "H-XXX",
            "expression": "sigma*tau",
            "target": 48,
            "claim_text": "optional text for pitfall scan",
            "tolerance": 0,
            "n_factors": 3
        },
        ...
    ]

    Returns:
        list of full_verification results
    """
    with open(claims_file, 'r') as f:
        claims = json.load(f)

    results = []
    for claim in claims:
        name = claim.get('name', '(unnamed)')
        expr = claim.get('expression', '')
        target = claim.get('target', 0)
        text = claim.get('claim_text', '')
        tol = claim.get('tolerance', 0)
        nf = claim.get('n_factors', 3)

        result = full_verification(
            expression=expr, target=target,
            claim_text=text, tolerance=tol,
            n_factors=nf, n_trials=50000,
        )
        result['name'] = name
        results.append(result)

    return results


# ═══════════════════════════════════════════════════════════════
# Display / Reporting
# ═══════════════════════════════════════════════════════════════

def format_report(report):
    """Format a verification report as a human-readable string."""
    lines = []
    w = 50

    name = report.get('name', '')
    expr = report.get('expression', '?')
    target = report.get('target', '?')

    lines.append('')
    lines.append('=' * w)
    title = 'CLAIM VERIFICATION REPORT'
    if name:
        title += f'  [{name}]'
    lines.append(f' {title}')
    lines.append('=' * w)
    lines.append(f'  Claim: {expr} = {target}')
    lines.append('-' * w)

    # Arithmetic
    ar = report.get('arithmetic', {})
    if ar.get('ok'):
        comp = ar.get('computed', '?')
        if ar.get('exact'):
            lines.append(f'  [PASS] Arithmetic: {expr} = {comp} (EXACT)')
        else:
            lines.append(f'  [PASS] Arithmetic: {expr} = {comp} '
                         f'(within tol={ar.get("tolerance_used")})')
    else:
        err = ar.get('error', '?')
        comp = ar.get('computed', '?')
        if comp is None:
            lines.append(f'  [FAIL] Arithmetic: evaluation error: {err}')
        else:
            lines.append(f'  [FAIL] Arithmetic: {expr} = {comp}, '
                         f'expected {target} (error={err})')

    # Ad hoc
    adhoc = report.get('adhoc', [])
    if adhoc:
        for _, msg in adhoc:
            lines.append(f'  [WARN] Ad hoc: {msg}')
    else:
        lines.append(f'  [PASS] Ad hoc: None detected')

    # Texas
    tx = report.get('texas', {})
    if tx:
        p = tx.get('p_value', -1)
        flag = tx.get('grade_flag', '?')
        hits = tx.get('hits', 0)
        n_t = tx.get('n_trials', 0)
        if p > 0.05:
            prefix = '[FAIL]'
        elif p > 0.01:
            prefix = '[WARN]'
        else:
            prefix = '[PASS]'
        lines.append(f'  {prefix} Texas: p = {p:.4f} ({flag}, '
                     f'{hits}/{n_t} random hits)')

    # Generalization
    gen = report.get('generalization')
    if gen:
        pc = gen.get('pass_count', 0)
        fc = gen.get('fail_count', 0)
        total = gen.get('total', 0)
        if gen.get('n6_only'):
            lines.append(f'  [FAIL] Generalize: n=6 only '
                         f'(0/{total} other perfect numbers)')
        elif pc > 0:
            lines.append(f'  [PASS] Generalize: {pc}/{total} '
                         f'perfect numbers match')
        else:
            lines.append(f'  [    ] Generalize: {pc}/{total} match')
        for d in gen.get('details', []):
            n_val = d.get('n')
            ok = d.get('ok')
            comp = d.get('computed', '?')
            tgt = d.get('target', '?')
            status = 'PASS' if ok else ('FAIL' if ok is False else '----')
            if 'diff' in d:
                lines.append(f'           n={n_val}: computed={comp}, '
                             f'target={tgt}, diff={d["diff"]:.6g} [{status}]')
            elif 'error' in d:
                lines.append(f'           n={n_val}: error={d["error"]} [{status}]')
            else:
                lines.append(f'           n={n_val}: computed={comp} [{status}]')

    # Pitfalls
    pitfalls = report.get('pitfalls', [])
    if pitfalls:
        for pf in pitfalls:
            lv = pf['level']
            lines.append(f'  [{lv}] Pitfall: {pf["msg"]}')
            lines.append(f'           matched: "{pf["match"]}"')
    else:
        lines.append(f'  [PASS] Pitfalls: None detected')

    # Grade
    lines.append('-' * w)
    gr = report.get('grade', {})
    emoji = gr.get('emoji', '?')
    label = gr.get('label', '?')
    reason = gr.get('reasoning', '')
    lines.append(f'  GRADE: {emoji} {label}')
    lines.append(f'  Reason: {reason}')
    lines.append('=' * w)
    lines.append('')

    return '\n'.join(lines)


def format_batch_summary(results):
    """Format a summary table for batch verification."""
    lines = []
    lines.append('')
    lines.append('=' * 70)
    lines.append(' BATCH VERIFICATION SUMMARY')
    lines.append('=' * 70)
    lines.append(f'  {"Name":<20} {"Arith":>6} {"Texas p":>10} '
                 f'{"General":>8} {"Grade":<20}')
    lines.append('-' * 70)

    for r in results:
        name = r.get('name', '?')[:20]
        arith_ok = 'PASS' if r.get('arithmetic', {}).get('ok') else 'FAIL'
        tx_p = r.get('texas', {}).get('p_value', -1)
        tx_str = f'{tx_p:.4f}' if tx_p >= 0 else 'N/A'
        gen = r.get('generalization')
        if gen:
            gen_str = f'{gen["pass_count"]}/{gen["total"]}'
        else:
            gen_str = 'N/A'
        gr = r.get('grade', {})
        grade_str = f'{gr.get("emoji", "?")} {gr.get("label", "?")}'

        lines.append(f'  {name:<20} {arith_ok:>6} {tx_str:>10} '
                     f'{gen_str:>8} {grade_str}')

    lines.append('=' * 70)

    # Counts
    grades = [r.get('grade', {}).get('grade', '') for r in results]
    counts = {}
    for g in grades:
        counts[g] = counts.get(g, 0) + 1
    lines.append(f'  Totals: {len(results)} claims')
    for g, c in sorted(counts.items()):
        lines.append(f'    {g}: {c}')
    lines.append('')

    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='Claim Verification Calculator -- '
                    'prevents false claims before publication.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Verify a single claim
  python3 calc/claim_verifier.py --claim "sigma*tau*sopfr" --target 240

  # Texas Sharpshooter test only
  python3 calc/claim_verifier.py --texas 240 --factors 3

  # Generalization test
  python3 calc/claim_verifier.py --generalize "sigma*tau" --target 48

  # Full verification pipeline
  python3 calc/claim_verifier.py --full "sigma*tau*sopfr" --target 240 \\
      --claim-text "pi_6(S3) = sigma(6)"

  # Pitfall scan only
  python3 calc/claim_verifier.py --pitfalls "This is proven: A iff B"

  # Batch verify from JSON file
  python3 calc/claim_verifier.py --batch claims.json
        """,
    )

    parser.add_argument('--claim', type=str,
                        help='Expression to verify (e.g. "sigma*tau")')
    parser.add_argument('--target', type=float,
                        help='Expected target value')
    parser.add_argument('--tolerance', type=float, default=0,
                        help='Allowed absolute error (default: 0 = exact)')

    parser.add_argument('--texas', type=float,
                        help='Run Texas Sharpshooter test for this target value')
    parser.add_argument('--factors', type=int, default=3,
                        help='Number of operands for Texas test (default: 3)')
    parser.add_argument('--trials', type=int, default=100000,
                        help='Monte Carlo trials (default: 100000)')

    parser.add_argument('--generalize', type=str,
                        help='Expression to test for generalization')
    parser.add_argument('--perfect-numbers', action='store_true',
                        help='Test generalization across perfect numbers')

    parser.add_argument('--full', type=str,
                        help='Run full pipeline on this expression')
    parser.add_argument('--claim-text', type=str, default='',
                        help='Claim text for pitfall scanning (used with --full)')

    parser.add_argument('--pitfalls', type=str,
                        help='Text to scan for overclaim pitfalls')

    parser.add_argument('--batch', type=str,
                        help='JSON file with batch of claims to verify')

    parser.add_argument('--seed', type=int, default=42,
                        help='Random seed for reproducibility (default: 42)')

    args = parser.parse_args()

    # Dispatch to appropriate mode
    ran_something = False

    # Mode: Full pipeline
    if args.full:
        if args.target is None:
            print('ERROR: --full requires --target')
            sys.exit(1)
        report = full_verification(
            expression=args.full,
            target=args.target,
            claim_text=args.claim_text,
            tolerance=args.tolerance,
            n_trials=args.trials,
            n_factors=args.factors,
        )
        print(format_report(report))
        ran_something = True

    # Mode: Simple claim verification
    elif args.claim:
        if args.target is None:
            print('ERROR: --claim requires --target')
            sys.exit(1)
        arith = verify_arithmetic(args.claim, args.target, tolerance=args.tolerance)
        adhoc = detect_adhoc(args.claim)

        print()
        print('=' * 50)
        print(' ARITHMETIC VERIFICATION')
        print('=' * 50)
        if arith['ok']:
            print(f'  [PASS] {args.claim} = {arith["computed"]}')
        else:
            print(f'  [FAIL] {args.claim} = {arith["computed"]}, '
                  f'expected {args.target}')
            if arith.get('error') and isinstance(arith['error'], str):
                print(f'  Error: {arith["error"]}')
            else:
                print(f'  Diff: {arith.get("error", "?")}')
        if adhoc:
            for _, msg in adhoc:
                print(f'  [WARN] {msg}')
        print('=' * 50)
        print()
        ran_something = True

    # Mode: Texas Sharpshooter only
    if args.texas is not None:
        tx = texas_sharpshooter(
            args.texas, n_factors=args.factors,
            n_trials=args.trials, seed=args.seed,
        )
        print()
        print('=' * 50)
        print(' TEXAS SHARPSHOOTER TEST')
        print('=' * 50)
        print(f'  Target: {args.texas}')
        print(f'  Factors: {args.factors}, Trials: {args.trials}')
        print(f'  Hits: {tx["hits"]}/{tx["n_trials"]}')
        print(f'  p-value: {tx["p_value"]:.6f}')
        print(f'  Verdict: {tx["grade_flag"]}')
        if tx['p_value'] > 0.05:
            print(f'  --> COINCIDENCE: random combinations hit this '
                  f'target {tx["p_value"]*100:.2f}% of the time')
        elif tx['p_value'] > 0.01:
            print(f'  --> BORDERLINE: marginally significant')
        else:
            print(f'  --> SIGNIFICANT: unlikely to be chance')
        print('=' * 50)
        print()
        ran_something = True

    # Mode: Generalization test
    if args.generalize:
        target_val = args.target
        gen = generalization_test(
            args.generalize, target_value=target_val,
        )
        print()
        print('=' * 50)
        print(' GENERALIZATION TEST')
        print('=' * 50)
        # Show n=6 first
        v6, e6 = safe_eval(args.generalize, n=6)
        if e6:
            print(f'  n=6: ERROR: {e6}')
        else:
            print(f'  n=6: {args.generalize} = {v6}')
        for d in gen['details']:
            n_val = d['n']
            comp = d.get('computed', '?')
            ok = d.get('ok')
            if ok is True:
                print(f'  n={n_val}: {comp} [PASS]')
            elif ok is False:
                tgt = d.get('target', '?')
                print(f'  n={n_val}: {comp} (target={tgt}) [FAIL]')
            else:
                print(f'  n={n_val}: {comp}')
        if gen['n6_only']:
            print(f'  --> WARNING: Formula works for n=6 ONLY')
        elif gen['pass_count'] > 0:
            print(f'  --> {gen["pass_count"]}/{gen["total"]} '
                  f'perfect numbers match')
        print('=' * 50)
        print()
        ran_something = True

    # Mode: Pitfall scan
    if args.pitfalls:
        findings = check_pitfalls(args.pitfalls)
        print()
        print('=' * 50)
        print(' PITFALL SCAN')
        print('=' * 50)
        if findings:
            for f in findings:
                print(f'  [{f["level"]}] {f["msg"]}')
                print(f'    matched: "{f["match"]}"')
        else:
            print('  No pitfalls detected.')
        print('=' * 50)
        print()
        ran_something = True

    # Mode: Batch
    if args.batch:
        if not os.path.exists(args.batch):
            print(f'ERROR: file not found: {args.batch}')
            sys.exit(1)
        results = verify_batch(args.batch)
        for r in results:
            print(format_report(r))
        print(format_batch_summary(results))
        ran_something = True

    if not ran_something:
        parser.print_help()


if __name__ == '__main__':
    main()
