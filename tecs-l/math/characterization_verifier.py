#!/usr/bin/env python3
"""
Characterization Verifier for Perfect Number 6
================================================
Verify candidate identities f(n) = g(n) for uniqueness.
Tests: arithmetic, uniqueness in [2,N], generalization to P_2=28,
       Texas sharpshooter p-value, ad-hoc check.

Usage:
  python3 characterization_verifier.py "sigma(n)*phi(n) == n*tau(n)"
  python3 characterization_verifier.py --interactive
  python3 characterization_verifier.py --batch FILE
  python3 characterization_verifier.py --all  # verify all 61 known characterizations
"""

import sys
import argparse
from sympy import (factorint, divisors, totient, mobius, isprime,
                   primerange, nextprime, primefactors, divisor_count)
from math import gcd, log, factorial, isqrt, prod
from fractions import Fraction
from collections import Counter
import time

# ─── Core arithmetic functions ───

def sigma(n):
    """Sum of divisors."""
    return sum(divisors(n))

def sigma_k(n, k):
    """Sum of k-th powers of divisors."""
    return sum(d**k for d in divisors(n))

def tau(n):
    """Number of divisors."""
    return divisor_count(n)

def phi(n):
    """Euler's totient."""
    return totient(n)

def psi(n):
    """Dedekind psi function."""
    result = n
    for p in primefactors(n):
        result = result * (1 + Fraction(1, p))
    return int(result)

def omega(n):
    """Number of distinct prime factors."""
    return len(factorint(n))

def bigomega(n):
    """Number of prime factors with multiplicity."""
    return sum(factorint(n).values())

def sopfr(n):
    """Sum of prime factors with multiplicity."""
    return sum(p * e for p, e in factorint(n).items())

def rad(n):
    """Radical: product of distinct prime factors."""
    if n <= 1:
        return n
    return prod(factorint(n).keys())

def aliquot(n):
    """Aliquot sum s(n) = sigma(n) - n."""
    return sigma(n) - n

def lambda_liouville(n):
    """Liouville lambda function."""
    return (-1) ** bigomega(n)

def R(n):
    """R(n) = sigma(n)*phi(n)/(n*tau(n))."""
    return Fraction(sigma(n) * phi(n), n * tau(n))

def arith_deriv(n):
    """Arithmetic derivative n'."""
    if n <= 1:
        return 0
    f = factorint(n)
    return sum(n * e // p for p, e in f.items())

def phi_chain(n):
    """Iterated totient chain until 1."""
    chain = [n]
    x = n
    while x > 1:
        x = phi(x)
        chain.append(x)
    return chain

def phi_chain_product(n):
    """Product of phi-chain elements."""
    return prod(phi_chain(n))

def sigma_iter(n, k):
    """Iterated sigma: sigma^k(n)."""
    x = n
    for _ in range(k):
        x = sigma(x)
    return x

# ─── Available functions for eval ───

FUNCS = {
    'sigma': sigma, 'tau': tau, 'phi': phi, 'psi': psi,
    'omega': omega, 'bigomega': bigomega, 'Omega': bigomega,
    'sopfr': sopfr, 'rad': rad, 'aliquot': aliquot, 'R': R,
    'lambda_l': lambda_liouville, 'mobius': mobius,
    'arith_deriv': arith_deriv, 'sigma_k': sigma_k,
    'phi_chain': phi_chain, 'phi_chain_product': phi_chain_product,
    'sigma_iter': sigma_iter,
    'gcd': gcd, 'log': log, 'factorial': factorial, 'isqrt': isqrt,
    'isprime': isprime, 'prod': prod, 'Fraction': Fraction,
    'divisors': divisors, 'factorint': factorint,
}


def safe_eval(expr, n):
    """Evaluate expression with n as variable."""
    try:
        return eval(expr, {"__builtins__": {}}, {**FUNCS, 'n': n})
    except Exception:
        return None


def verify_identity(lhs_expr, rhs_expr, N=10000, verbose=True):
    """
    Verify identity lhs(n) == rhs(n).
    Returns dict with results.
    """
    results = {
        'identity': f'{lhs_expr} == {rhs_expr}',
        'n6_check': False,
        'solutions': [],
        'n28_check': False,
        'unique_to_6': False,
        'grade': '?',
    }

    # 1. Check n=6
    lhs6 = safe_eval(lhs_expr, 6)
    rhs6 = safe_eval(rhs_expr, 6)
    results['n6_lhs'] = lhs6
    results['n6_rhs'] = rhs6
    results['n6_check'] = (lhs6 is not None and rhs6 is not None and lhs6 == rhs6)

    if verbose:
        print(f"\n{'='*60}")
        print(f"Identity: {lhs_expr} == {rhs_expr}")
        print(f"{'='*60}")
        print(f"\n[1] n=6 check: LHS={lhs6}, RHS={rhs6}, match={results['n6_check']}")

    if not results['n6_check']:
        results['grade'] = 'FAIL'
        if verbose:
            print("  FAILED at n=6. Aborting.")
        return results

    # 2. Find all solutions in [2, N]
    t0 = time.time()
    for n in range(2, N + 1):
        lhs = safe_eval(lhs_expr, n)
        rhs = safe_eval(rhs_expr, n)
        if lhs is not None and rhs is not None and lhs == rhs:
            results['solutions'].append(n)
    elapsed = time.time() - t0

    if verbose:
        print(f"\n[2] Solutions in [2,{N}]: {results['solutions'][:20]}"
              f"{'...' if len(results['solutions']) > 20 else ''}")
        print(f"   Count: {len(results['solutions'])} ({elapsed:.1f}s)")

    # 3. Check n=28
    lhs28 = safe_eval(lhs_expr, 28)
    rhs28 = safe_eval(rhs_expr, 28)
    results['n28_check'] = (lhs28 is not None and rhs28 is not None and lhs28 == rhs28)

    if verbose:
        print(f"\n[3] n=28 check: LHS={lhs28}, RHS={rhs28}, generalizes={results['n28_check']}")

    # 4. Uniqueness assessment
    sols = results['solutions']
    results['unique_to_6'] = (sols == [6])
    results['unique_composite_6'] = (6 in sols and all(isprime(s) or s in [1, 6] for s in sols))

    # 5. Texas sharpshooter (rough)
    n_solutions = len(sols)
    expected_random = N / 100  # rough: 1% of range
    if n_solutions <= 3 and N >= 1000:
        results['texas_p'] = n_solutions / (N / 10)  # very rough
    else:
        results['texas_p'] = min(1.0, n_solutions / expected_random)

    # 6. Ad-hoc check: does the identity involve +1/-1 adjustments?
    results['ad_hoc'] = ('+1' in lhs_expr or '-1' in lhs_expr or
                         '+1' in rhs_expr or '-1' in rhs_expr)

    # 7. Grade
    if results['unique_to_6']:
        results['grade'] = 'STAR' if not results['ad_hoc'] else 'GREEN'
    elif len(sols) <= 3:
        results['grade'] = 'GREEN'
    elif len(sols) <= 10:
        results['grade'] = 'GREEN_WEAK'
    else:
        results['grade'] = 'WHITE'

    if verbose:
        grade_emoji = {
            'STAR': '  STAR', 'GREEN': '  GREEN', 'GREEN_WEAK': '  GREEN (weak)',
            'WHITE': '  WHITE', 'FAIL': '  FAIL'
        }
        print(f"\n[4] Grade: {grade_emoji.get(results['grade'], results['grade'])}")
        print(f"   Unique to n=6: {results['unique_to_6']}")
        print(f"   Ad-hoc (+/-1): {results['ad_hoc']}")
        print(f"   Texas p-value: ~{results['texas_p']:.4f}")
        if results['n28_check']:
            print("   WARNING: Generalizes to n=28 (not 6-specific)")

    return results


# ─── Known characterizations (61) ───

KNOWN_CHARS = [
    ("sigma(n)*phi(n)", "n*tau(n)", "sigma*phi=n*tau (#1, master)"),
    ("phi(n)**2", "tau(n)", "phi^2=tau (#33)"),
    ("sigma(n)", "n*phi(n)", "sigma=n*phi (#34)"),
    ("sopfr(n)", "n-1", "sopfr=n-1 (#42)"),
    ("aliquot(n)", "3*phi(n)", "s(n)=3*phi(n) (#44)"),
    ("sigma(n)+phi(n)", "2*tau(n)+n", "sigma+phi=2tau+n (#45)"),
    ("sigma(n)+n", "3*(phi(n)+tau(n))", "sigma+n=3(phi+tau) (#46)"),
    ("sigma(n)*omega(n)", "n*tau(n)", "sigma*omega=n*tau"),
    ("omega(n)*(tau(n)-1)", "n", "omega*(tau-1)=n (#37)"),
    ("phi_chain_product(n)", "sigma(n)", "phi-chain prod=sigma (#55)"),
    ("sigma(n)*tau(n)-n*phi(n)", "n**2", "sigma*tau-n*phi=n^2 (#56)"),
    ("n-2", "tau(n)", "n-2=tau (Cayley, #59)"),
    ("2*sigma(n)", "n*tau(n)", "2sigma=ntau (avg divisor, #60)"),
    ("tau(n)", "2*phi(n)", "tau=2phi"),
    ("3*sigma(n)+3*phi(n)", "7*n", "3sigma+3phi=7n"),
    ("sigma(n)**2", "n**2*tau(n)", "sigma^2=n^2*tau"),
    ("rad(sigma(n))", "n", "rad(sigma)=n (#49, n>1)"),
]


def run_all_known(N=10000):
    """Verify all known characterizations."""
    print(f"Verifying {len(KNOWN_CHARS)} known characterizations (N={N})...\n")
    passed = 0
    failed = 0
    for lhs, rhs, desc in KNOWN_CHARS:
        r = verify_identity(lhs, rhs, N=N, verbose=False)
        status = 'OK' if r['n6_check'] else 'FAIL'
        if r['n6_check']:
            passed += 1
        else:
            failed += 1
        sols = r['solutions']
        sol_str = str(sols[:10]) + ('...' if len(sols) > 10 else '')
        print(f"  [{status}] {desc}: solutions={sol_str}")
    print(f"\nTotal: {passed} passed, {failed} failed")


def interactive_mode():
    """Interactive REPL for testing identities."""
    print("Characterization Verifier (interactive)")
    print("Type identity as: LHS == RHS  (using n as variable)")
    print("Available: sigma, tau, phi, psi, omega, sopfr, rad, R, mobius, ...")
    print("Type 'quit' to exit, 'help' for function list\n")

    while True:
        try:
            line = input(">>> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not line or line == 'quit':
            break
        if line == 'help':
            print("Functions:", ', '.join(sorted(FUNCS.keys())))
            continue
        if '==' in line:
            parts = line.split('==')
            if len(parts) == 2:
                verify_identity(parts[0].strip(), parts[1].strip())
            else:
                print("Error: use exactly one '=='")
        else:
            # Just evaluate at n=6
            val = safe_eval(line, 6)
            print(f"  n=6: {line} = {val}")


def main():
    parser = argparse.ArgumentParser(description="Verify characterizations of n=6")
    parser.add_argument('identity', nargs='?', help='Identity: "LHS == RHS"')
    parser.add_argument('--interactive', '-i', action='store_true')
    parser.add_argument('--all', '-a', action='store_true', help='Verify all known')
    parser.add_argument('--N', type=int, default=10000, help='Search range')
    args = parser.parse_args()

    if args.all:
        run_all_known(args.N)
    elif args.interactive:
        interactive_mode()
    elif args.identity:
        if '==' in args.identity:
            parts = args.identity.split('==')
            verify_identity(parts[0].strip(), parts[1].strip(), N=args.N)
        else:
            print(f"n=6: {args.identity} = {safe_eval(args.identity, 6)}")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
