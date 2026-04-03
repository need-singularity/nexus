#!/usr/bin/env python3
"""
Equation Uniqueness Checker
=====================================================
Checks whether arithmetic equations are uniquely satisfied by n=6
(or any target) among all positive integers up to a given limit.

Uses sieve-based precomputation for speed: all arithmetic functions
(sigma, tau, phi, omega, Omega, sopfr, rad, mu, sigma_k) are computed
via a single factorization sieve pass, not per-number factoring.

Usage:
  # Check a single equation
  python3 calc/equation_uniqueness_checker.py --equation "n-2=tau(n)" --limit 10000

  # Scan for ALL equations uniquely satisfied by n=6
  python3 calc/equation_uniqueness_checker.py --scan --limit 10000

  # Batch verify from file (one equation per line)
  python3 calc/equation_uniqueness_checker.py --verify-list equations.txt --limit 10000

  # JSON output for machine consumption
  python3 calc/equation_uniqueness_checker.py --scan --limit 5000 --json

  # Change target from 6 to another number
  python3 calc/equation_uniqueness_checker.py --scan --limit 5000 --target 28
"""

import argparse
import json
import math
import sys
import time
from collections import defaultdict
from fractions import Fraction

try:
    import tecsrs
    _HAS_TECSRS = True
except ImportError:
    _HAS_TECSRS = False


# ═══════════════════════════════════════════════════════════════
# Sieve-based arithmetic function precomputation
# ═══════════════════════════════════════════════════════════════

def sieve_arithmetic_functions(limit):
    """
    Precompute all standard arithmetic functions for n in [1, limit].
    Uses tecsrs Rust sieve when available (50-200x speedup), falls back to Python.

    Functions computed:
      tau(n), sigma(n), sigma_m1(n), sigma2(n), phi(n),
      omega(n), Omega(n), sopfr(n), rad(n), mu(n)
    """
    N = limit + 1

    if _HAS_TECSRS:
        # Rust sieve: sigma, tau, phi, sopfr, omega in one call
        rust = tecsrs.sieve_all(limit)
        sigma = list(rust['sigma'])
        tau = list(rust['tau'])
        phi_arr = list(rust['phi'])
        sopfr = list(rust['sopfr'])
        omega = list(rust['omega'])

        # sigma_m1 = sigma(n)/n
        sigma_m1_float = [0.0] * N
        for n in range(1, N):
            sigma_m1_float[n] = sigma[n] / n

        # sigma2 via divisor sieve (not in tecsrs yet)
        sigma2 = [0] * N
        for d in range(1, N):
            d2 = d * d
            for multiple in range(d, N, d):
                sigma2[multiple] += d2

        # Omega, rad, mu need SPF-based factorization (not in tecsrs yet)
        spf = list(range(N))
        for i in range(2, int(limit**0.5) + 1):
            if spf[i] == i:
                for j in range(i * i, N, i):
                    if spf[j] == j:
                        spf[j] = i

        Omega = [0] * N
        rad = [1] * N
        mu = [1] * N
        for n in range(2, N):
            temp = n
            square_free = True
            while temp > 1:
                p = spf[temp]
                exp = 0
                while temp % p == 0:
                    temp //= p
                    exp += 1
                Omega[n] += exp
                rad[n] *= p
                if exp >= 2:
                    square_free = False
                    mu[n] = 0
                else:
                    mu[n] *= -1
            if not square_free:
                mu[n] = 0

        return {
            'tau': tau, 'sigma': sigma, 'sigma_m1': sigma_m1_float,
            'sigma2': sigma2, 'phi': phi_arr, 'omega': omega,
            'Omega': Omega, 'sopfr': sopfr, 'rad': rad, 'mu': mu, 'spf': spf,
        }

    # Python fallback
    tau = [0] * N
    sigma = [0] * N
    omega = [0] * N
    Omega = [0] * N
    sopfr = [0] * N
    rad = [1] * N
    mu = [1] * N

    spf = list(range(N))
    for i in range(2, int(limit**0.5) + 1):
        if spf[i] == i:
            for j in range(i * i, N, i):
                if spf[j] == j:
                    spf[j] = i

    for n in range(2, N):
        temp = n
        square_free = True
        while temp > 1:
            p = spf[temp]
            exp = 0
            while temp % p == 0:
                temp //= p
                exp += 1
            omega[n] += 1
            Omega[n] += exp
            sopfr[n] += p * exp
            rad[n] *= p
            if exp >= 2:
                square_free = False
                mu[n] = 0
            else:
                mu[n] *= -1
        if not square_free:
            mu[n] = 0

    phi_arr = list(range(N))
    for p in range(2, N):
        if spf[p] == p:
            for j in range(p, N, p):
                phi_arr[j] = phi_arr[j] // p * (p - 1)

    for d in range(1, N):
        for multiple in range(d, N, d):
            tau[multiple] += 1
            sigma[multiple] += d

    sigma_m1_float = [0.0] * N
    for n in range(1, N):
        sigma_m1_float[n] = sigma[n] / n

    sigma2 = [0] * N
    for d in range(1, N):
        d2 = d * d
        for multiple in range(d, N, d):
            sigma2[multiple] += d2

    return {
        'tau': tau, 'sigma': sigma, 'sigma_m1': sigma_m1_float,
        'sigma2': sigma2, 'phi': phi_arr, 'omega': omega,
        'Omega': Omega, 'sopfr': sopfr, 'rad': rad, 'mu': mu, 'spf': spf,
    }


# ═══════════════════════════════════════════════════════════════
# Term library for systematic scanning
# ═══════════════════════════════════════════════════════════════

def build_term_library(funcs, limit):
    """
    Build a library of arithmetic expression terms.
    Each term is (name, values_dict) where values_dict maps n -> value.
    """
    tau = funcs['tau']
    sigma = funcs['sigma']
    sigma_m1 = funcs['sigma_m1']
    sigma2 = funcs['sigma2']
    phi = funcs['phi']
    omega = funcs['omega']
    Omega_arr = funcs['Omega']
    sopfr = funcs['sopfr']
    rad = funcs['rad']
    mu = funcs['mu']

    N = limit + 1
    terms = []

    def add_term(name, func):
        """Add a term, computing values for n in [2, limit]."""
        vals = {}
        for n in range(2, N):
            try:
                v = func(n)
                if v is not None and not (isinstance(v, float) and (math.isinf(v) or math.isnan(v))):
                    vals[n] = v
            except:
                pass
        terms.append((name, vals))

    # Basic n-expressions
    add_term("n", lambda n: n)
    add_term("n-1", lambda n: n - 1)
    add_term("n-2", lambda n: n - 2)
    add_term("n+1", lambda n: n + 1)
    add_term("n+2", lambda n: n + 2)
    add_term("2n", lambda n: 2 * n)
    add_term("3n", lambda n: 3 * n)
    add_term("n^2", lambda n: n * n)
    add_term("n/2", lambda n: n / 2)
    add_term("n/3", lambda n: n / 3)

    # Arithmetic function terms
    func_map = {
        'tau': lambda n: tau[n],
        'sigma': lambda n: sigma[n],
        'phi': lambda n: phi[n],
        'omega': lambda n: omega[n],
        'Omega': lambda n: Omega_arr[n],
        'sopfr': lambda n: sopfr[n],
        'rad': lambda n: rad[n],
        'mu': lambda n: mu[n],
        'sigma_m1': lambda n: sigma_m1[n],
        'sigma2': lambda n: sigma2[n],
    }

    for fname, fn in func_map.items():
        add_term(fname, fn)
        add_term(f"{fname}+1", lambda n, f=fn: f(n) + 1)
        add_term(f"{fname}-1", lambda n, f=fn: f(n) - 1)
        add_term(f"{fname}*2", lambda n, f=fn: f(n) * 2)
        add_term(f"{fname}^2", lambda n, f=fn: f(n) ** 2)
        if fname not in ('omega', 'Omega', 'mu'):
            add_term(f"n/{fname}", lambda n, f=fn: n / f(n) if f(n) != 0 else None)
            add_term(f"{fname}/n", lambda n, f=fn: f(n) / n)

    # Cross-function products and sums
    cross_pairs = [
        ('tau', 'phi'), ('tau', 'omega'), ('sigma', 'phi'),
        ('sigma', 'tau'), ('phi', 'omega'), ('phi', 'rad'),
        ('tau', 'rad'), ('sigma', 'omega'), ('sopfr', 'omega'),
    ]
    for f1_name, f2_name in cross_pairs:
        f1, f2 = func_map[f1_name], func_map[f2_name]
        add_term(f"{f1_name}*{f2_name}", lambda n, a=f1, b=f2: a(n) * b(n))
        add_term(f"{f1_name}+{f2_name}", lambda n, a=f1, b=f2: a(n) + b(n))
        if f2_name not in ('omega', 'Omega', 'mu'):
            add_term(f"{f1_name}/{f2_name}",
                     lambda n, a=f1, b=f2: a(n) / b(n) if b(n) != 0 else None)

    # Special combinations
    add_term("sigma-n", lambda n: sigma[n] - n)
    add_term("(sigma-n)/n", lambda n: (sigma[n] - n) / n)
    add_term("tau*phi/n", lambda n: tau[n] * phi[n] / n)
    add_term("n*omega", lambda n: n * omega[n])
    add_term("phi+tau", lambda n: phi[n] + tau[n])
    add_term("phi*tau", lambda n: phi[n] * tau[n])
    add_term("sigma-phi", lambda n: sigma[n] - phi[n])
    add_term("n-phi", lambda n: n - phi[n])
    add_term("sigma/phi", lambda n: sigma[n] / phi[n] if phi[n] != 0 else None)
    add_term("n+tau", lambda n: n + tau[n])
    add_term("n*tau", lambda n: n * tau[n])
    add_term("n-tau", lambda n: n - tau[n])
    add_term("sigma-tau", lambda n: sigma[n] - tau[n])
    add_term("rad*omega", lambda n: rad[n] * omega[n])
    add_term("n-rad", lambda n: n - rad[n])
    add_term("sopfr-omega", lambda n: sopfr[n] - omega[n])
    add_term("n-sopfr", lambda n: n - sopfr[n])
    add_term("sigma_m1*n", lambda n: sigma[n])  # sigma_{-1}*n = sigma(n)/n * n = sigma(n) ... skip duplicate
    # Remove last duplicate and replace
    terms.pop()
    add_term("sopfr+tau", lambda n: sopfr[n] + tau[n])
    add_term("rad-phi", lambda n: rad[n] - phi[n])

    # Constants
    for c in [1, 2, 3, 4, 5, 6, 8, 10, 12, 24]:
        add_term(str(c), lambda n, v=c: v)

    return terms


# ═══════════════════════════════════════════════════════════════
# Equation parser for --equation mode
# ═══════════════════════════════════════════════════════════════

def parse_and_evaluate_equation(equation_str, funcs, limit):
    """
    Parse an equation like "n-2=tau(n)" and find all solutions in [2, limit].
    Returns (lhs_name, rhs_name, solutions_list).
    """
    if '=' not in equation_str:
        print(f"Error: equation must contain '='. Got: {equation_str}", file=sys.stderr)
        sys.exit(1)

    lhs_str, rhs_str = equation_str.split('=', 1)
    lhs_str = lhs_str.strip()
    rhs_str = rhs_str.strip()

    tau = funcs['tau']
    sigma = funcs['sigma']
    sigma_m1 = funcs['sigma_m1']
    sigma2 = funcs['sigma2']
    phi = funcs['phi']
    omega_arr = funcs['omega']
    Omega_arr = funcs['Omega']
    sopfr = funcs['sopfr']
    rad = funcs['rad']
    mu_arr = funcs['mu']

    def make_evaluator(expr_str):
        """Create a function n -> value from an expression string."""
        # Normalize: remove spaces, replace function names
        e = expr_str.strip()

        # Build safe evaluation context
        def evaluator(n):
            local_vars = {
                'n': n,
                'tau': tau[n],
                'sigma': sigma[n],
                'sigma_m1': sigma_m1[n],
                'sigma2': sigma2[n],
                'phi': phi[n],
                'omega': omega_arr[n],
                'Omega': Omega_arr[n],
                'sopfr': sopfr[n],
                'rad': rad[n],
                'mu': mu_arr[n],
                'sqrt': math.sqrt,
                'log': math.log,
                'abs': abs,
            }
            # Transform "tau(n)" -> "tau", "sigma(n)" -> "sigma" etc.
            safe_expr = e
            for fname in ['tau', 'sigma_m1', 'sigma2', 'sigma', 'phi',
                          'omega', 'Omega', 'sopfr', 'rad', 'mu']:
                safe_expr = safe_expr.replace(f'{fname}(n)', fname)
                safe_expr = safe_expr.replace(f'{fname}(', f'{fname}*(')  # handle tau(...)
            try:
                return eval(safe_expr, {"__builtins__": {}}, local_vars)
            except:
                return None

        return evaluator

    lhs_fn = make_evaluator(lhs_str)
    rhs_fn = make_evaluator(rhs_str)

    solutions = []
    for n in range(2, limit + 1):
        try:
            lv = lhs_fn(n)
            rv = rhs_fn(n)
            if lv is None or rv is None:
                continue
            if isinstance(lv, float) or isinstance(rv, float):
                if abs(float(lv) - float(rv)) < 1e-10:
                    solutions.append(n)
            else:
                if lv == rv:
                    solutions.append(n)
        except:
            pass

    return lhs_str, rhs_str, solutions


# ═══════════════════════════════════════════════════════════════
# Scan mode: find ALL unique equations
# ═══════════════════════════════════════════════════════════════

def scan_unique_equations(funcs, limit, target=6):
    """
    Find all f(n)=g(n) equations uniquely satisfied by n=target in [2, limit].
    Returns (unique_list, few_solutions_list).
    """
    terms = build_term_library(funcs, limit)
    term_names = [name for name, _ in terms]
    term_vals = {name: vals for name, vals in terms}

    unique_target = []
    few_solutions = []  # target plus at most 2 others

    for i in range(len(term_names)):
        for j in range(i + 1, len(term_names)):
            f_name = term_names[i]
            g_name = term_names[j]
            f_vals = term_vals[f_name]
            g_vals = term_vals[g_name]

            solutions = []
            for n in range(2, limit + 1):
                if n in f_vals and n in g_vals:
                    fv = f_vals[n]
                    gv = g_vals[n]
                    if isinstance(fv, float) or isinstance(gv, float):
                        if abs(float(fv) - float(gv)) < 1e-10:
                            solutions.append(n)
                    else:
                        if fv == gv:
                            solutions.append(n)

            if target in solutions:
                if len(solutions) == 1:
                    unique_target.append((f_name, g_name, solutions))
                elif len(solutions) <= 3:
                    few_solutions.append((f_name, g_name, solutions))

    # Filter trivial
    def is_trivial(f, g):
        if f == g:
            return True
        return False

    unique_target = [(f, g, s) for f, g, s in unique_target if not is_trivial(f, g)]
    few_solutions = [(f, g, s) for f, g, s in few_solutions if not is_trivial(f, g)]

    # Sort by interest
    def interest_score(f, g):
        score = 0
        arith_funcs = ['tau', 'sigma', 'phi', 'omega', 'Omega', 'rad', 'sopfr', 'mu']
        f_funcs = set(fn for fn in arith_funcs if fn in f)
        g_funcs = set(fn for fn in arith_funcs if fn in g)
        if f_funcs != g_funcs:
            score += 2
        if 'n' in f or 'n' in g:
            score += 1
        return score

    unique_target.sort(key=lambda x: -interest_score(x[0], x[1]))
    few_solutions.sort(key=lambda x: (len(x[2]), -interest_score(x[0], x[1])))

    return unique_target, few_solutions


# ═══════════════════════════════════════════════════════════════
# Output formatting
# ═══════════════════════════════════════════════════════════════

def print_results(lhs, rhs, solutions, target=6, limit=10000):
    """Print formatted results for a single equation check."""
    is_unique = (len(solutions) == 1 and solutions[0] == target)
    has_target = target in solutions

    print(f"\n{'=' * 60}")
    print(f"  Equation: {lhs} = {rhs}")
    print(f"  Range:    n in [2, {limit}]")
    print(f"  Target:   n = {target}")
    print(f"{'=' * 60}")
    print(f"  Solutions found: {len(solutions)}")

    if len(solutions) <= 20:
        print(f"  Values:   {solutions}")
    else:
        print(f"  First 20: {solutions[:20]} ... (+{len(solutions)-20} more)")

    print()
    if is_unique:
        print(f"  [PASS] n={target} is the UNIQUE solution")
    elif has_target:
        others = [s for s in solutions if s != target]
        if len(others) <= 10:
            print(f"  [INFO] n={target} is a solution, but also: {others}")
        else:
            print(f"  [INFO] n={target} is a solution among {len(solutions)} total")
    else:
        print(f"  [FAIL] n={target} is NOT a solution")
    print()


def results_to_json(lhs, rhs, solutions, target=6, limit=10000):
    """Return JSON-serializable dict for a single equation."""
    return {
        "equation": f"{lhs} = {rhs}",
        "lhs": lhs,
        "rhs": rhs,
        "limit": limit,
        "target": target,
        "num_solutions": len(solutions),
        "solutions": solutions if len(solutions) <= 100 else solutions[:100],
        "unique_to_target": (len(solutions) == 1 and solutions[0] == target),
        "target_is_solution": target in solutions,
    }


# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Check arithmetic equations for uniqueness at n=6 (or other target).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --equation "n-2=tau(n)" --limit 10000
  %(prog)s --scan --limit 5000
  %(prog)s --scan --limit 5000 --target 28
  %(prog)s --verify-list equations.txt --limit 10000
  %(prog)s --equation "sigma(n)=2*n" --limit 10000 --json
        """)

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--equation', type=str,
                       help='Single equation to check, e.g. "n-2=tau(n)"')
    group.add_argument('--scan', action='store_true',
                       help='Scan for ALL equations uniquely satisfied by target')
    group.add_argument('--verify-list', type=str, metavar='FILE',
                       help='File with one equation per line to batch verify')

    parser.add_argument('--limit', type=int, default=10000,
                        help='Upper bound for search range (default: 10000)')
    parser.add_argument('--target', type=int, default=6,
                        help='Target value to check uniqueness for (default: 6)')
    parser.add_argument('--json', action='store_true',
                        help='Output results as JSON')

    args = parser.parse_args()

    # Sieve precomputation
    t0 = time.time()
    if not args.json:
        print(f"Sieving arithmetic functions up to {args.limit}...")
    funcs = sieve_arithmetic_functions(args.limit)
    t_sieve = time.time() - t0
    if not args.json:
        print(f"  Done in {t_sieve:.2f}s\n")

    # ── Single equation mode ──
    if args.equation:
        lhs, rhs, solutions = parse_and_evaluate_equation(
            args.equation, funcs, args.limit)
        if args.json:
            result = results_to_json(lhs, rhs, solutions, args.target, args.limit)
            result["sieve_time_s"] = round(t_sieve, 3)
            print(json.dumps(result, indent=2))
        else:
            print_results(lhs, rhs, solutions, args.target, args.limit)

    # ── Scan mode ──
    elif args.scan:
        t1 = time.time()
        if not args.json:
            print(f"Scanning all equation pairs for unique solutions at n={args.target}...")
        unique, few = scan_unique_equations(funcs, args.limit, args.target)
        t_scan = time.time() - t1

        if args.json:
            result = {
                "mode": "scan",
                "limit": args.limit,
                "target": args.target,
                "sieve_time_s": round(t_sieve, 3),
                "scan_time_s": round(t_scan, 3),
                "unique_equations": [
                    {"lhs": f, "rhs": g, "solutions": s}
                    for f, g, s in unique
                ],
                "few_solution_equations": [
                    {"lhs": f, "rhs": g, "solutions": s}
                    for f, g, s in few[:50]
                ],
            }
            print(json.dumps(result, indent=2))
        else:
            print(f"\n  Scan completed in {t_scan:.2f}s")
            print(f"\n  EQUATIONS WITH UNIQUE SOLUTION n={args.target} ({len(unique)} found):")
            print(f"  {'LHS':>25} = {'RHS':<25}  Solutions")
            print(f"  {'-'*25}   {'-'*25}  {'-'*15}")
            for f_name, g_name, sols in unique:
                print(f"  {f_name:>25} = {g_name:<25}  {sols}")

            print(f"\n  EQUATIONS WITH n={args.target} + FEW OTHERS ({len(few)} found):")
            print(f"  {'LHS':>25} = {'RHS':<25}  Solutions")
            print(f"  {'-'*25}   {'-'*25}  {'-'*15}")
            for f_name, g_name, sols in few[:50]:
                print(f"  {f_name:>25} = {g_name:<25}  {sols}")

            print(f"\n  Total: {len(unique)} unique, {len(few)} near-unique")

    # ── Batch verify mode ──
    elif args.verify_list:
        try:
            with open(args.verify_list) as f:
                equations = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        except FileNotFoundError:
            print(f"Error: file not found: {args.verify_list}", file=sys.stderr)
            sys.exit(1)

        all_results = []
        for eq in equations:
            lhs, rhs, solutions = parse_and_evaluate_equation(eq, funcs, args.limit)
            res = results_to_json(lhs, rhs, solutions, args.target, args.limit)
            all_results.append(res)
            if not args.json:
                is_unique = res["unique_to_target"]
                has_target = res["target_is_solution"]
                status = "UNIQUE" if is_unique else ("HAS TARGET" if has_target else "MISS")
                print(f"  [{status:>10}] {eq:40s}  solutions={res['num_solutions']}")

        if args.json:
            output = {
                "mode": "verify_list",
                "file": args.verify_list,
                "limit": args.limit,
                "target": args.target,
                "sieve_time_s": round(t_sieve, 3),
                "results": all_results,
            }
            print(json.dumps(output, indent=2))
        else:
            unique_count = sum(1 for r in all_results if r["unique_to_target"])
            has_count = sum(1 for r in all_results if r["target_is_solution"])
            print(f"\n  Summary: {unique_count} unique, {has_count} contain target, "
                  f"{len(all_results)} total")


if __name__ == "__main__":
    main()
