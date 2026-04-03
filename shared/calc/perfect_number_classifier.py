#!/usr/bin/env python3
"""Perfect Number Classifier — Systematic classification of n=6 properties

Classifies every arithmetic identity into:
  Class A: UNIVERSAL  — holds for all even perfect numbers (theorem)
  Class B: P1-ONLY    — holds only for n=6 (first perfect uniqueness)
  Class C: NON-PERFECT — holds for non-perfect numbers too (not special)

Uses closed-form formulas for even perfect numbers n = 2^(p-1)(2^p - 1):
  σ(n) = 2n,  τ(n) = 2p,  φ(n) = 2^(p-2)(2^p - 2)
  ω(n) = 2,   Ω(n) = p,   sopfr(n) = 2(p-1) + (2^p - 1)

Usage:
  python3 calc/perfect_number_classifier.py                  # Full classification
  python3 calc/perfect_number_classifier.py --table          # Arithmetic table only
  python3 calc/perfect_number_classifier.py --class A        # Show only universal
  python3 calc/perfect_number_classifier.py --class B        # Show only P1-unique
  python3 calc/perfect_number_classifier.py --controls       # Include non-perfect controls
  python3 calc/perfect_number_classifier.py --formula "sigma*phi == n*tau"
  python3 calc/perfect_number_classifier.py --discover       # Auto-discover new universals
"""

import argparse
import math
import sys
from fractions import Fraction
from itertools import combinations_with_replacement


# ═══════════════════════════════════════════════════════════════
# Arithmetic Functions (exact, works for any positive integer)
# ═══════════════════════════════════════════════════════════════

def factorize(n):
    """Return prime factorization as dict {prime: exponent}."""
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


def sigma(n):
    """Sum of divisors σ(n)."""
    factors = factorize(n)
    result = 1
    for p, e in factors.items():
        result *= (p**(e+1) - 1) // (p - 1)
    return result


def tau(n):
    """Number of divisors τ(n)."""
    factors = factorize(n)
    result = 1
    for e in factors.values():
        result *= (e + 1)
    return result


def phi(n):
    """Euler's totient φ(n)."""
    factors = factorize(n)
    result = n
    for p in factors:
        result = result * (p - 1) // p
    return result


def omega(n):
    """Number of distinct prime factors ω(n)."""
    return len(factorize(n))


def bigomega(n):
    """Number of prime factors with multiplicity Ω(n)."""
    return sum(factorize(n).values())


def sopfr(n):
    """Sum of prime factors with multiplicity."""
    return sum(p * e for p, e in factorize(n).items())


def sopf(n):
    """Sum of distinct prime factors."""
    return sum(factorize(n).keys())


def rad(n):
    """Radical of n (product of distinct primes)."""
    result = 1
    for p in factorize(n):
        result *= p
    return result


def mobius(n):
    """Möbius function μ(n)."""
    factors = factorize(n)
    for e in factors.values():
        if e > 1:
            return 0
    return (-1) ** len(factors)


def sigma_k(n, k):
    """Sum of k-th powers of divisors σ_k(n)."""
    factors = factorize(n)
    result = 1
    for p, e in factors.items():
        result *= sum(p**(k*i) for i in range(e+1))
    return result


def sigma_minus1(n):
    """σ_{-1}(n) = σ(n)/n for perfect numbers."""
    return Fraction(sigma(n), n)


def lpf(n):
    """Least prime factor."""
    if n <= 1:
        return n
    d = 2
    while d * d <= n:
        if n % d == 0:
            return d
        d += 1
    return n


def gpf(n):
    """Greatest prime factor."""
    factors = factorize(n)
    return max(factors.keys()) if factors else n


def divisors(n):
    """Return sorted list of all divisors."""
    divs = []
    for i in range(1, int(n**0.5) + 1):
        if n % i == 0:
            divs.append(i)
            if i != n // i:
                divs.append(n // i)
    return sorted(divs)


def is_perfect(n):
    """Check if n is a perfect number."""
    return sigma(n) == 2 * n


# ═══════════════════════════════════════════════════════════════
# Perfect Number Database
# ═══════════════════════════════════════════════════════════════

# Mersenne exponents for first 8 known perfect numbers
MERSENNE_EXPONENTS = [2, 3, 5, 7, 13, 17, 19, 31]

def perfect_number(p):
    """Generate even perfect number from Mersenne exponent p."""
    return 2**(p-1) * (2**p - 1)


def build_profile(n):
    """Complete arithmetic profile for any positive integer."""
    facs = factorize(n)
    divs = divisors(n)
    proper = [d for d in divs if d < n]

    profile = {
        'n': n,
        'sigma': sigma(n),
        'tau': tau(n),
        'phi': phi(n),
        'omega': omega(n),
        'bigomega': bigomega(n),
        'sopfr': sopfr(n),
        'sopf': sopf(n),
        'rad': rad(n),
        'mobius': mobius(n),
        'lpf': lpf(n),
        'gpf': gpf(n),
        'sigma_minus1': sigma_minus1(n),
        'is_perfect': is_perfect(n),
        'factorization': facs,
        'divisors': divs,
        'proper_divisors': proper,
        'n_divisors': len(divs),
    }

    # Derived ratios
    profile['sigma_over_n'] = Fraction(profile['sigma'], n)
    profile['phi_over_n'] = Fraction(profile['phi'], n)
    profile['tau_over_omega'] = profile['tau'] / profile['omega'] if profile['omega'] > 0 else 0
    profile['sigma_times_phi'] = profile['sigma'] * profile['phi']
    profile['n_times_tau'] = n * profile['tau']

    # Perfect number specific
    if is_perfect(n):
        # Find Mersenne exponent
        for p in range(2, 64):
            if 2**(p-1) * (2**p - 1) == n:
                profile['mersenne_exp'] = p
                profile['mersenne_prime'] = 2**p - 1
                break
        else:
            profile['mersenne_exp'] = None
            profile['mersenne_prime'] = None

    return profile


# ═══════════════════════════════════════════════════════════════
# Identity Library — Formulas to classify
# ═══════════════════════════════════════════════════════════════

IDENTITIES = [
    # Category: Defining properties (should be UNIVERSAL)
    ("sigma(n) == 2*n", "σ=2n (perfect number definition)", "defining"),
    ("sigma_minus1 == 2", "σ₋₁=2 (equivalent definition)", "defining"),

    # Category: Core TECS relations
    ("sigma*phi == n*tau", "σφ=nτ (Bridge identity)", "core"),
    ("tau == phi**2", "τ=φ² (divisor-totient)", "core"),
    ("phi == n//3", "φ=n/3", "core"),
    ("tau == n - 2", "τ=n-2", "core"),
    ("(n-3) == math.factorial(n-3) if n<=20 else -1", "(n-3)!=n test", "core"),
    ("sopfr * phi == n + tau", "sopfr·φ=n+τ", "core"),
    ("sigma * phi == n**2", "σφ=n²", "core"),

    # Category: Uniqueness at n=6
    ("n * sigma * sopfr * phi == math.factorial(n) if n<=20 else -1",
     "n·σ·sopfr·φ=n!", "uniqueness"),
    ("tau * (tau - 1) == sigma", "τ(τ-1)=σ", "uniqueness"),
    ("tau * sopfr == 20", "τ·sopfr=20", "uniqueness"),

    # Category: Ratios involving Mersenne exponent p
    ("tau == 2 * mersenne_exp if mersenne_exp else -1",
     "τ=2p (Mersenne)", "mersenne"),
    ("bigomega == mersenne_exp if mersenne_exp else -1",
     "Ω=p (Mersenne)", "mersenne"),
    ("omega == 2", "ω=2 (two prime factors)", "mersenne"),
    ("sopfr == 2*(mersenne_exp-1) + mersenne_prime if mersenne_exp else -1",
     "sopfr=2(p-1)+M_p", "mersenne"),

    # Category: Golden Zone constants
    ("abs(1/n - 1/sigma) < 0.001", "1/n ≈ 1/σ", "golden_zone"),
    ("abs(Fraction(1,2) + Fraction(1,3) + Fraction(1,n) - 1) == 0",
     "1/2+1/3+1/n=1", "golden_zone"),
    ("abs(phi/n - Fraction(1,3)) == 0", "φ/n=1/3", "golden_zone"),

    # Category: Lyapunov / stability
    ("all(sigma_minus1 == 2 for _ in [1])", "σ₋₁=2 stability", "stability"),

    # Category: Combinatorial
    ("tau**2 == sigma + tau", "τ²=σ+τ", "combinatorial"),
    ("sigma - tau == n + 2", "σ-τ=n+2", "combinatorial"),
    ("phi**3 == n + 2", "φ³=n+2", "combinatorial"),

    # Category: Rate invariants (from H-CX-82)
    ("abs((n+1)/(tau*phi) - 7/8) < 0.01",
     "r₀=(n+1)/(τφ) ≈ 7/8", "rate"),
    ("abs(phi/sopfr - 2/5) < 0.01",
     "r∞=φ/sopfr ≈ 2/5", "rate"),
    ("abs((n+1)/(tau*phi) * phi/sopfr - 7/20) < 0.01",
     "r₀·r∞ ≈ 7/20", "rate"),

    # Category: Cross-perfect (tau chain)
    ("tau == 2 * mersenne_exp if mersenne_exp else -1",
     "τ chain: τ(Pk)=2pk", "cross"),

    # Category: Consciousness Bridge
    ("abs(sigma/phi - n) < 0.01", "σ/φ=n (DBM equilibration)", "bridge"),
    ("abs(4 - tau) < 0.01 if is_perfect else -1",
     "RS=τ=4 (self-measurement)", "bridge"),

    # Category: Information-theoretic
    ("abs(math.log(2) - (n+1)/(2*sigma)) < 0.05",
     "ln2 ≈ (n+1)/(2σ)", "info"),
    ("abs((n+1)/sigma - Fraction(7,12)) < Fraction(1,100)",
     "(n+1)/σ=7/12 (PH barcode)", "info"),

    # Category: New universal candidates
    ("sigma == 2 * n", "σ=2n (trivial)", "universal_candidate"),
    ("sigma + n == 3 * n", "σ+n=3n", "universal_candidate"),
    ("sigma - n == n", "σ-n=n", "universal_candidate"),
    ("tau % 2 == 0", "τ is even", "universal_candidate"),
    ("phi % 2 == 0 if n > 2 else True", "φ is even", "universal_candidate"),
    ("omega == 2", "ω=2 (always two distinct primes)", "universal_candidate"),
    ("sigma * phi >= n * tau", "σφ ≥ nτ", "universal_candidate"),
    ("Fraction(sigma * phi, n * tau) == Fraction(phi, tau) * 2",
     "σφ/(nτ) = 2φ/τ", "universal_candidate"),
    ("sigma == tau * n // tau + n",
     "σ = n + n = 2n check", "universal_candidate"),
]


# ═══════════════════════════════════════════════════════════════
# Test Engine
# ═══════════════════════════════════════════════════════════════

def evaluate_identity(identity_expr, profile):
    """Evaluate an identity expression against a profile. Returns (bool, value_or_error)."""
    n = profile['n']
    _sigma = profile['sigma']
    _tau = profile['tau']
    _phi = profile['phi']
    _omega = profile['omega']
    _bigomega = profile['bigomega']
    _sopfr = profile['sopfr']
    _sopf = profile['sopf']
    _rad = profile['rad']
    _mobius = profile['mobius']
    _lpf = profile['lpf']
    _gpf = profile['gpf']
    _sigma_minus1 = profile['sigma_minus1']
    is_perf = profile['is_perfect']
    mersenne_exp = profile.get('mersenne_exp')
    mersenne_prime = profile.get('mersenne_prime')

    # Build local namespace
    ns = {
        'n': n, 'sigma': _sigma, 'tau': _tau, 'phi': _phi,
        'omega': _omega, 'bigomega': _bigomega, 'sopfr': _sopfr,
        'sopf': _sopf, 'rad': _rad, 'mobius': _mobius,
        'lpf': _lpf, 'gpf': _gpf,
        'sigma_minus1': _sigma_minus1,
        'is_perfect': is_perf,
        'mersenne_exp': mersenne_exp,
        'mersenne_prime': mersenne_prime,
        'math': math, 'Fraction': Fraction, 'abs': abs, 'all': all,
    }

    try:
        result = eval(identity_expr, {"__builtins__": {}}, ns)
        if result == -1:
            return None, "N/A"  # Not applicable
        return bool(result), result
    except Exception as e:
        return None, str(e)


def classify_identity(identity_expr, desc, category, profiles_perfect, profiles_control=None):
    """Classify an identity across perfect numbers and optional controls."""
    results_perfect = []
    for p in profiles_perfect:
        ok, val = evaluate_identity(identity_expr, p)
        results_perfect.append((p['n'], ok, val))

    results_control = []
    if profiles_control:
        for p in profiles_control:
            ok, val = evaluate_identity(identity_expr, p)
            results_control.append((p['n'], ok, val))

    # Count passes among perfect numbers
    applicable = [(n, ok, v) for n, ok, v in results_perfect if ok is not None]
    passes = sum(1 for _, ok, _ in applicable if ok)
    total = len(applicable)

    if total == 0:
        verdict = "N/A"
    elif passes == total:
        # Check controls to see if it's trivially true for non-perfects too
        if results_control:
            ctrl_applicable = [(n, ok, v) for n, ok, v in results_control if ok is not None]
            ctrl_passes = sum(1 for _, ok, _ in ctrl_applicable if ok)
            if ctrl_passes == len(ctrl_applicable) and len(ctrl_applicable) > 0:
                verdict = "TRIVIAL"  # True everywhere, not special
            else:
                verdict = "UNIVERSAL"  # True for all perfects, not for non-perfects
        else:
            verdict = "UNIVERSAL"
    elif passes == 1 and applicable[0][1]:
        verdict = "P1-ONLY"
    elif passes > 1:
        verdict = f"PARTIAL ({passes}/{total})"
    else:
        verdict = "NONE"

    return {
        'expr': identity_expr,
        'desc': desc,
        'category': category,
        'verdict': verdict,
        'passes': passes,
        'total': total,
        'results_perfect': results_perfect,
        'results_control': results_control,
    }


# ═══════════════════════════════════════════════════════════════
# Auto-Discovery Engine
# ═══════════════════════════════════════════════════════════════

def discover_universals(profiles_perfect, profiles_control, max_depth=2):
    """Search for new universal identities across perfect numbers.

    Tries combinations of arithmetic functions and checks if
    any non-trivial relation holds for ALL perfect numbers.
    """
    atoms = ['n', 'sigma', 'tau', 'phi', 'sopfr', 'omega', 'rad', 'gpf', 'lpf']
    ops = ['+', '-', '*', '/']
    discovered = []

    print("\n  Scanning for universal identities (depth=%d)..." % max_depth)
    tested = 0

    for a in atoms:
        for b in atoms:
            if a == b:
                continue
            for op in ops:
                # Test: a op b == constant across all perfects?
                expr_str = f"{a} {op} {b}"
                values = []
                valid = True
                for p in profiles_perfect:
                    ns = {k: p[k] for k in atoms if k in p}
                    try:
                        val = eval(expr_str, {"__builtins__": {}}, ns)
                        if val is None or (isinstance(val, float) and (math.isnan(val) or math.isinf(val))):
                            valid = False
                            break
                        values.append(val)
                    except:
                        valid = False
                        break

                tested += 1

                if not valid or len(values) < len(profiles_perfect):
                    continue

                # Check if constant
                if len(set(values)) == 1:
                    const = values[0]
                    # Check non-trivial (not 0 for subtraction of same, etc.)
                    if const == 0 and op == '-':
                        continue

                    # Check controls
                    ctrl_match = True
                    if profiles_control:
                        for p in profiles_control:
                            ns = {k: p[k] for k in atoms if k in p}
                            try:
                                val = eval(expr_str, {"__builtins__": {}}, ns)
                                if val != const:
                                    ctrl_match = False
                                    break
                            except:
                                ctrl_match = False
                                break

                    discovered.append({
                        'expr': f"{a} {op} {b} == {const}",
                        'value': const,
                        'trivial_in_controls': ctrl_match,
                        'type': 'constant',
                    })

                # Check if ratio is constant (for non-integer relations)
                if op == '/' and all(v != 0 for v in values):
                    ratios = [Fraction(values[0]).limit_denominator(1000)] * len(values)
                    try:
                        frac_values = [Fraction(v).limit_denominator(1000) for v in values]
                        if len(set(frac_values)) == 1:
                            # Already caught above
                            pass
                    except:
                        pass

    # Depth 2: a op1 b op2 c
    if max_depth >= 2:
        for a in atoms:
            for b in atoms:
                for c in atoms:
                    if a == b == c:
                        continue
                    for op1 in ['+', '-', '*']:
                        for op2 in ['+', '-', '*']:
                            expr_str = f"({a} {op1} {b}) {op2} {c}"
                            values = []
                            valid = True
                            for p in profiles_perfect:
                                ns = {k: p[k] for k in atoms if k in p}
                                try:
                                    val = eval(expr_str, {"__builtins__": {}}, ns)
                                    values.append(val)
                                except:
                                    valid = False
                                    break
                            tested += 1
                            if not valid or len(values) < len(profiles_perfect):
                                continue
                            if len(set(values)) == 1 and values[0] != 0:
                                ctrl_match = True
                                if profiles_control:
                                    for p in profiles_control:
                                        ns = {k: p[k] for k in atoms if k in p}
                                        try:
                                            val = eval(expr_str, {"__builtins__": {}}, ns)
                                            if val != values[0]:
                                                ctrl_match = False
                                                break
                                        except:
                                            ctrl_match = False
                                            break
                                discovered.append({
                                    'expr': f"({a} {op1} {b}) {op2} {c} == {values[0]}",
                                    'value': values[0],
                                    'trivial_in_controls': ctrl_match,
                                    'type': 'depth2',
                                })

    print(f"  Tested {tested} combinations, found {len(discovered)} universals")
    return discovered


# ═══════════════════════════════════════════════════════════════
# Ratio Pattern Discovery
# ═══════════════════════════════════════════════════════════════

def discover_ratio_patterns(profiles_perfect):
    """Find ratios that follow a pattern across perfect numbers.

    Instead of constants, look for ratios that are functions of p (Mersenne exponent).
    """
    atoms = ['n', 'sigma', 'tau', 'phi', 'sopfr', 'omega', 'rad', 'gpf', 'lpf']
    patterns = []

    print("\n  Scanning for p-dependent patterns...")

    for a in atoms:
        for b in atoms:
            if a == b:
                continue

            values = []
            ps = []
            valid = True
            for prof in profiles_perfect:
                p = prof.get('mersenne_exp')
                if p is None:
                    valid = False
                    break
                ns = {k: prof[k] for k in atoms if k in prof}
                try:
                    if ns.get(b, 0) == 0:
                        valid = False
                        break
                    val = Fraction(ns[a], ns[b])
                    values.append(val)
                    ps.append(p)
                except:
                    valid = False
                    break

            if not valid or len(values) < 3:
                continue

            # Check: is value = f(p) for simple f?
            # f(p) = p
            if all(v == p for v, p in zip(values, ps)):
                patterns.append(f"{a}/{b} = p (Mersenne exponent)")
            # f(p) = 2p
            elif all(v == 2*p for v, p in zip(values, ps)):
                patterns.append(f"{a}/{b} = 2p")
            # f(p) = p-1
            elif all(v == p-1 for v, p in zip(values, ps)):
                patterns.append(f"{a}/{b} = p-1")
            # f(p) = 2^(p-1)
            elif all(v == 2**(p-1) for v, p in zip(values, ps)):
                patterns.append(f"{a}/{b} = 2^(p-1)")
            # f(p) = 2^p - 1
            elif all(v == 2**p - 1 for v, p in zip(values, ps)):
                patterns.append(f"{a}/{b} = 2^p - 1 (Mersenne prime)")
            # Check ratio pattern: v[i+1]/v[i]
            elif len(values) >= 3:
                ratios = []
                for i in range(len(values)-1):
                    if values[i] != 0:
                        ratios.append(values[i+1] / values[i])
                if len(set(ratios)) == 1 and ratios:
                    patterns.append(f"{a}/{b}: geometric ratio = {ratios[0]}")

    return patterns


# ═══════════════════════════════════════════════════════════════
# Display Functions
# ═══════════════════════════════════════════════════════════════

def print_table(profiles, title="Arithmetic Function Table"):
    """Print comprehensive arithmetic table."""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")

    # Header
    fields = ['n', 'sigma', 'tau', 'phi', 'omega', 'bigomega', 'sopfr', 'sopf',
              'rad', 'lpf', 'gpf', 'sigma_minus1']
    labels = ['n', 'σ(n)', 'τ(n)', 'φ(n)', 'ω(n)', 'Ω(n)', 'sopfr', 'sopf',
              'rad', 'lpf', 'gpf', 'σ₋₁']

    # Determine widths
    widths = []
    for f, l in zip(fields, labels):
        vals = [str(p[f]) for p in profiles]
        widths.append(max(len(l), max(len(v) for v in vals)))

    # Print header
    header = "  " + "  ".join(l.rjust(w) for l, w in zip(labels, widths))
    print(header)
    print("  " + "  ".join("-"*w for w in widths))

    # Print data
    for p in profiles:
        perf_mark = " ★" if p.get('is_perfect') else ""
        row = "  " + "  ".join(str(p[f]).rjust(w) for f, w in zip(fields, widths))
        print(row + perf_mark)

    print()

    # Derived ratios
    print("  Derived Ratios:")
    print("  " + "-"*60)
    for p in profiles:
        n = p['n']
        r1 = f"σφ/nτ={Fraction(p['sigma']*p['phi'], p['n']*p['tau'])}"
        r2 = f"φ/n={Fraction(p['phi'], n)}"
        r3 = f"τ/ω={p['tau']//p['omega']}"
        perf = "★" if p['is_perfect'] else " "
        me = f"p={p.get('mersenne_exp','?')}" if p['is_perfect'] else ""
        print(f"  {perf} n={n:>8}: {r1:>12}  {r2:>10}  {r3:>6}  {me}")
    print()


def print_classification(results, filter_class=None):
    """Print classification results."""
    print(f"\n{'='*80}")
    print(f"  Identity Classification Report")
    print(f"{'='*80}\n")

    # Group by category
    categories = {}
    for r in results:
        cat = r['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(r)

    # Verdict icons
    icons = {
        'UNIVERSAL': '✅',
        'TRIVIAL': '⬜',
        'P1-ONLY': '🔶',
        'NONE': '⬛',
        'N/A': '⚪',
    }

    # Summary counters
    counts = {'UNIVERSAL': 0, 'TRIVIAL': 0, 'P1-ONLY': 0, 'PARTIAL': 0, 'NONE': 0, 'N/A': 0}

    for cat, items in categories.items():
        # Filter
        if filter_class:
            items = [r for r in items if filter_class.upper() in r['verdict']]
            if not items:
                continue

        print(f"  --- {cat.upper()} ---")
        for r in items:
            v = r['verdict']
            icon = icons.get(v, '🔵')
            detail = ""
            for n, ok, val in r['results_perfect']:
                if ok is True:
                    detail += f" P({n})✓"
                elif ok is False:
                    detail += f" P({n})✗"
                else:
                    detail += f" P({n})?"
            print(f"  {icon} {r['desc']:<40} {v:<12} {detail}")

            # Count
            if 'PARTIAL' in v:
                counts['PARTIAL'] += 1
            elif v in counts:
                counts[v] += 1

        print()

    # Summary
    print(f"  {'='*60}")
    print(f"  SUMMARY")
    print(f"  {'='*60}")
    total = sum(counts.values())
    for v, c in counts.items():
        pct = f"({100*c/total:.0f}%)" if total > 0 else ""
        icon = icons.get(v, '🔵')
        print(f"    {icon} {v:<12}: {c:>3} {pct}")
    print(f"    {'Total':<14}: {total:>3}")
    print()


def print_discoveries(discovered, ratio_patterns):
    """Print auto-discovered universals."""
    print(f"\n{'='*80}")
    print(f"  Auto-Discovered Universal Relations")
    print(f"{'='*80}\n")

    # Separate non-trivial from trivial
    nontrivial = [d for d in discovered if not d['trivial_in_controls']]
    trivial = [d for d in discovered if d['trivial_in_controls']]

    if nontrivial:
        print("  ★ NON-TRIVIAL (perfect-number specific):")
        for d in nontrivial:
            print(f"    ✅ {d['expr']}")
    else:
        print("  (No non-trivial universals found at this depth)")

    if trivial:
        print(f"\n  ⬜ TRIVIAL ({len(trivial)} found, true for all integers):")
        for d in trivial[:10]:
            print(f"    ⬜ {d['expr']}")
        if len(trivial) > 10:
            print(f"    ... and {len(trivial)-10} more")

    if ratio_patterns:
        print(f"\n  📐 RATIO PATTERNS (p-dependent):")
        for pat in ratio_patterns:
            print(f"    📐 {pat}")

    print()


# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Perfect Number Classifier")
    parser.add_argument('--table', action='store_true', help='Show arithmetic table only')
    parser.add_argument('--class', dest='filter_class', help='Filter by class (A/UNIVERSAL, B/P1-ONLY)')
    parser.add_argument('--controls', action='store_true', help='Include non-perfect control numbers')
    parser.add_argument('--discover', action='store_true', help='Auto-discover universal relations')
    parser.add_argument('--depth', type=int, default=2, help='Discovery search depth (default: 2)')
    parser.add_argument('--formula', type=str, help='Test a specific formula')
    parser.add_argument('--perfects', type=int, default=5, help='Number of perfect numbers to test (default: 5)')
    args = parser.parse_args()

    # Build profiles for perfect numbers
    num_perfects = min(args.perfects, len(MERSENNE_EXPONENTS))
    perfect_profiles = []
    for i in range(num_perfects):
        p = MERSENNE_EXPONENTS[i]
        n = perfect_number(p)
        perfect_profiles.append(build_profile(n))

    # Control group: non-perfect numbers
    controls = [5, 7, 10, 12, 15, 20, 24, 30, 100, 120]
    control_profiles = [build_profile(c) for c in controls] if args.controls else []

    # Print table
    if args.table or not (args.formula or args.discover):
        all_profiles = perfect_profiles + (control_profiles if args.controls else [])
        print_table(all_profiles,
                    f"Perfect Numbers P₁-P{num_perfects}" +
                    (" + Controls" if args.controls else ""))

    # Test specific formula
    if args.formula:
        print(f"\n  Testing: {args.formula}")
        print(f"  {'='*60}")
        for p in perfect_profiles:
            ok, val = evaluate_identity(args.formula, p)
            mark = "✅" if ok else ("⚪" if ok is None else "❌")
            print(f"    {mark} n={p['n']:>10}: {val}")
        if control_profiles:
            print(f"\n  Controls:")
            for p in control_profiles:
                ok, val = evaluate_identity(args.formula, p)
                mark = "✅" if ok else ("⚪" if ok is None else "❌")
                print(f"    {mark} n={p['n']:>10}: {val}")
        return

    # Run classification
    if not args.table:
        results = []
        for expr, desc, cat in IDENTITIES:
            r = classify_identity(expr, desc, cat, perfect_profiles, control_profiles)
            results.append(r)
        print_classification(results, args.filter_class)

    # Auto-discovery
    if args.discover:
        discovered = discover_universals(perfect_profiles, control_profiles, args.depth)
        ratio_patterns = discover_ratio_patterns(perfect_profiles)
        print_discoveries(discovered, ratio_patterns)


if __name__ == '__main__':
    main()
