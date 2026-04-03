#!/usr/bin/env python3
"""R-Spectrum Calculator — Arithmetic balance ratio analysis

Computes R(n) = sigma(n)*phi(n)/(n*tau(n)) and related invariants.
Implements all proved theorems from H-SPEC-1.

Usage:
  python3 r_spectrum.py --n 6
  python3 r_spectrum.py --n 6 --full
  python3 r_spectrum.py --range 1-100
  python3 r_spectrum.py --perfect 4
  python3 r_spectrum.py --gap 6
  python3 r_spectrum.py --identity-test 6
  python3 r_spectrum.py --spectrum 1000 --plot spectrum.png
"""

import argparse
import math
from fractions import Fraction
from collections import defaultdict


def factorize(n):
    """Return prime factorization as {p: a} dict."""
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
    """Sum of divisors."""
    if n <= 0:
        return 0
    factors = factorize(n)
    result = 1
    for p, a in factors.items():
        result *= (p ** (a + 1) - 1) // (p - 1)
    return result


def phi(n):
    """Euler totient."""
    if n <= 0:
        return 0
    factors = factorize(n)
    result = n
    for p in factors:
        result = result * (p - 1) // p
    return result


def tau(n):
    """Number of divisors."""
    if n <= 0:
        return 0
    factors = factorize(n)
    result = 1
    for a in factors.values():
        result *= (a + 1)
    return result


def R(n):
    """R(n) = sigma(n)*phi(n)/(n*tau(n)) as exact Fraction."""
    if n <= 0:
        return Fraction(0)
    s, p, t = sigma(n), phi(n), tau(n)
    return Fraction(s * p, n * t)


def R_prime_power(p, a):
    """R(p^a) = (p^{a+1}-1)/(p*(a+1)) — closed form."""
    return Fraction(p ** (a + 1) - 1, p * (a + 1))


def R_factored(n):
    """R(n) via multiplicative decomposition: R(n) = prod R(p^a)."""
    factors = factorize(n)
    result = Fraction(1)
    components = []
    for p, a in sorted(factors.items()):
        rpa = R_prime_power(p, a)
        components.append((p, a, rpa))
        result *= rpa
    return result, components


def gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def compute_gap(n, N=10000):
    """Compute delta+, delta-, focal length for R(n)."""
    rn = R(n)
    r_above = None
    r_below = None
    n_above = None
    n_below = None

    for m in range(1, N + 1):
        rm = R(m)
        if rm > rn:
            if r_above is None or rm < r_above:
                r_above = rm
                n_above = m
        elif rm < rn:
            if r_below is None or rm > r_below:
                r_below = rm
                n_below = m

    delta_plus = r_above - rn if r_above else None
    delta_minus = rn - r_below if r_below else None
    focal = delta_plus * delta_minus if delta_plus and delta_minus else None

    return {
        'R': rn,
        'delta_plus': delta_plus,
        'delta_minus': delta_minus,
        'n_above': n_above,
        'n_below': n_below,
        'focal_length': focal,
    }


def identity_tests(n):
    """Run all characterization tests from H-SPEC-1."""
    s, p, t = sigma(n), phi(n), tau(n)
    rn = R(n)
    results = []

    # #1: sigma*phi = n*tau (master formula, R=1)
    master = (s * p == n * t)
    results.append(('sigma*phi = n*tau (R=1)', master, f'{s}*{p}={s*p}, {n}*{t}={n*t}'))

    # #183: phi/tau + tau/sigma + 1/n = 1
    completeness = Fraction(p, t) + Fraction(t, s) + Fraction(1, n)
    results.append(('phi/tau + tau/sigma + 1/n = 1', completeness == 1,
                    f'{Fraction(p,t)} + {Fraction(t,s)} + {Fraction(1,n)} = {completeness}'))

    # #184: phi/n = tau/sigma
    ratio_eq = Fraction(p, n) == Fraction(t, s)
    results.append(('phi/n = tau/sigma (=1/3)', ratio_eq,
                    f'{Fraction(p,n)} vs {Fraction(t,s)}'))

    # #177: R(6n) = R(n) test (if gcd(n,6)=1)
    if gcd(n, 6) == 1:
        r6n = R(6 * n)
        coprime_id = (rn == r6n)
        results.append(('R(6n) = R(n) [gcd(n,6)=1]', coprime_id,
                        f'R({n})={float(rn):.4f}, R({6*n})={float(r6n):.4f}'))

    # #190: phi+tau=n AND sigma=2n
    pt_n = (p + t == n) and (s == 2 * n)
    results.append(('phi+tau=n AND sigma=2n', pt_n,
                    f'phi+tau={p+t}, n={n}, sigma={s}, 2n={2*n}'))

    # Multiplicativity check
    factors = factorize(n)
    r_mult, components = R_factored(n)
    mult_ok = (r_mult == rn)
    results.append(('R = prod R(p^a) [multiplicativity]', mult_ok,
                    ' * '.join(f'R({p}^{a})={float(r):.4f}' for p, a, r in components)))

    return results


def print_analysis(n, full=False):
    """Print complete R-spectrum analysis for n."""
    s, p, t = sigma(n), phi(n), tau(n)
    rn = R(n)
    factors = factorize(n)

    print(f'\n{"="*60}')
    print(f'  R-Spectrum Analysis: n = {n}')
    print(f'{"="*60}')
    print(f'  Factorization: {" * ".join(f"{p}^{a}" if a > 1 else str(p) for p, a in sorted(factors.items()))}')
    print(f'  sigma({n}) = {s}')
    print(f'  phi({n})   = {p}')
    print(f'  tau({n})   = {t}')
    print(f'  R({n})     = {rn} = {float(rn):.10f}')
    print()

    # Multiplicative decomposition
    r_mult, components = R_factored(n)
    if len(components) > 1:
        print(f'  Multiplicative: R({n}) = ' +
              ' * '.join(f'R({p}{"^"+str(a) if a>1 else ""})' for p, a, _ in components))
        print(f'                       = ' +
              ' * '.join(f'{r}' for _, _, r in components) + f' = {r_mult}')
        print()

    # Log-R in Golden Zone Width units
    if rn > 0:
        W = math.log(4 / 3)
        log_r = math.log(float(rn))
        print(f'  log(R) = {log_r:.6f} = {log_r/W:.4f} * W  (W = ln(4/3) = GZ Width)')
        print()

    # Identity tests
    print(f'  --- Characterization Tests ---')
    tests = identity_tests(n)
    for name, passed, detail in tests:
        mark = 'PASS' if passed else '  --'
        print(f'  [{mark}] {name}')
        if full or passed:
            print(f'         {detail}')
    print()

    if full:
        # Gap structure
        print(f'  --- Gap Structure (N=10000) ---')
        gap = compute_gap(n, N=10000)
        if gap['delta_plus']:
            print(f'  delta+ = {gap["delta_plus"]} = {float(gap["delta_plus"]):.6f}  (nearest above: n={gap["n_above"]})')
        if gap['delta_minus']:
            print(f'  delta- = {gap["delta_minus"]} = {float(gap["delta_minus"]):.6f}  (nearest below: n={gap["n_below"]})')
        if gap['focal_length']:
            f_val = gap['focal_length']
            print(f'  f = delta+*delta- = {f_val} = {float(f_val):.10f}')
            spf = Fraction(s * p, 1) * f_val
            print(f'  sigma*phi*f = {spf} = {float(spf):.6f}' +
                  (' = 1 !!!' if spf == 1 else ''))
        print()

        # Self-referential check (only meaningful for R=1)
        if rn == 1:
            print(f'  --- Self-Referential Structure ---')
            print(f'  R(phi({n})) = R({p}) = {float(R(p)):.6f}  (= R(n) - 1/tau = {float(1 - Fraction(1,t)):.6f})')
            print(f'  R(tau({n})) = R({t}) = {float(R(t)):.6f}  (= R(n) + 1/n  = {float(1 + Fraction(1,n)):.6f})')
            print(f'  Neighbors = {{phi, tau}} = {{{p}, {t}}} — self-referential!')
            print()


def print_range(start, end):
    """Print R values for a range of n."""
    print(f'\n  n | {"R(n)":>12s} | {"decimal":>10s} | factors')
    print(f'  --+-{"-"*12}-+-{"-"*10}-+--------')
    for n in range(start, end + 1):
        rn = R(n)
        factors = factorize(n)
        fstr = '*'.join(f'{p}^{a}' if a > 1 else str(p) for p, a in sorted(factors.items()))
        if not fstr:
            fstr = '1'
        print(f'  {n:>2d} | {str(rn):>12s} | {float(rn):>10.6f} | {fstr}')
    print()


def print_perfect(count):
    """Print R values for perfect numbers."""
    mersenne_exponents = [2, 3, 5, 7, 13, 17, 19, 31]
    print(f'\n  R(P_k) for even perfect numbers (Fermat theorem: always integer)')
    print(f'  {"p":>3s} | {"P_k":>12s} | {"R(P_k)":>12s} | formula 2^(p-1)(2^(p-1)-1)/p')
    print(f'  ---+-{"-"*12}-+-{"-"*12}-+---')
    for i, p in enumerate(mersenne_exponents[:count]):
        Pk = 2 ** (p - 1) * (2 ** p - 1)
        r = Fraction(2 ** (p - 1) * (2 ** (p - 1) - 1), p)
        print(f'  {p:>3d} | {Pk:>12d} | {str(r):>12s} | 2^{p-1}*{2**(p-1)-1}/{p}')
    print()


def print_spectrum(N, plot_file=None):
    """Print and optionally plot the R-spectrum."""
    R_vals = {}
    for n in range(1, N + 1):
        R_vals[n] = R(n)

    unique_R = sorted(set(R_vals.values()))
    print(f'\n  R-Spectrum Statistics (N={N})')
    print(f'  Unique R values: {len(unique_R)}')
    print(f'  Min R: {unique_R[0]} = {float(unique_R[0]):.6f}')
    print(f'  Max R: {float(unique_R[-1]):.2f}')
    print()

    # Bottom 15
    print(f'  Bottom 15 R values:')
    for i, r in enumerate(unique_R[:15]):
        ns = [n for n in range(1, N + 1) if R_vals[n] == r][:3]
        print(f'    {i+1:>2d}. R = {str(r):>10s} = {float(r):.6f}  n = {ns}')
    print()

    # Gap structure
    print(f'  Spec_R = {{3/4}} U {{1}} U [7/6, +inf)')
    print(f'  Gap (3/4, 1):   EMPTY (proved)')
    print(f'  Gap (1, 7/6):   EMPTY (proved)')
    print()

    # Fiber statistics
    fibers = defaultdict(list)
    for n in range(1, N + 1):
        fibers[R_vals[n]].append(n)

    multi = {r: ns for r, ns in fibers.items() if len(ns) > 1}
    print(f'  R-coincidences (R(n)=R(m)): {len(multi)} pairs')
    print(f'  All with ratio 6 (coprime): {sum(1 for ns in multi.values() if len(ns)==2 and ns[1]==6*ns[0])}')
    print()

    if plot_file:
        try:
            import matplotlib.pyplot as plt
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

            # R values scatter
            ns = list(range(1, min(N + 1, 501)))
            rs = [float(R(n)) for n in ns]
            ax1.scatter(ns, rs, s=2, alpha=0.5)
            ax1.set_xlabel('n')
            ax1.set_ylabel('R(n)')
            ax1.set_title(f'R-Spectrum (n=1..{min(N, 500)})')
            ax1.axhline(y=1, color='r', linestyle='--', alpha=0.5, label='R=1 (n=6)')
            ax1.axhline(y=0.75, color='b', linestyle=':', alpha=0.5, label='R=3/4 (n=2)')
            ax1.legend(fontsize=8)

            # Bottom spectrum histogram
            low_r = [float(r) for r in R_vals.values() if float(r) < 10]
            ax2.hist(low_r, bins=100, edgecolor='black', linewidth=0.3)
            ax2.set_xlabel('R value')
            ax2.set_ylabel('Count')
            ax2.set_title('R-Spectrum Distribution (R < 10)')
            ax2.axvline(x=1.0, color='r', linestyle='--', alpha=0.7, label='R=1')
            ax2.axvline(x=0.75, color='b', linestyle=':', alpha=0.7, label='R=3/4')
            ax2.legend(fontsize=8)

            plt.tight_layout()
            plt.savefig(plot_file, dpi=150)
            print(f'  Plot saved to {plot_file}')
        except ImportError:
            print('  matplotlib not available, skipping plot')


def main():
    parser = argparse.ArgumentParser(description='R-Spectrum Calculator')
    parser.add_argument('--n', type=int, help='Analyze single n')
    parser.add_argument('--full', action='store_true', help='Full analysis with gap structure')
    parser.add_argument('--range', type=str, help='Range a-b (e.g., 1-30)')
    parser.add_argument('--perfect', type=int, default=0, help='Show R for first k perfect numbers')
    parser.add_argument('--gap', type=int, help='Compute gap structure for n')
    parser.add_argument('--identity-test', type=int, help='Run identity tests for n')
    parser.add_argument('--spectrum', type=int, help='Spectrum statistics for n=1..N')
    parser.add_argument('--plot', type=str, help='Save plot to file (requires --spectrum)')
    parser.add_argument('--json', action='store_true', help='JSON output (for DFS automation)')

    args = parser.parse_args()

    if args.n:
        print_analysis(args.n, full=args.full)

    if args.range:
        parts = args.range.split('-')
        print_range(int(parts[0]), int(parts[1]))

    if args.perfect:
        print_perfect(args.perfect)

    if args.gap:
        gap = compute_gap(args.gap)
        print(f'\nGap structure for n={args.gap}:')
        print(f'  R({args.gap}) = {gap["R"]} = {float(gap["R"]):.6f}')
        if gap['delta_plus']:
            print(f'  delta+ = {gap["delta_plus"]} (n={gap["n_above"]})')
        if gap['delta_minus']:
            print(f'  delta- = {gap["delta_minus"]} (n={gap["n_below"]})')
        if gap['focal_length']:
            print(f'  f = {gap["focal_length"]}')
        print()

    if args.identity_test:
        print(f'\nIdentity tests for n={args.identity_test}:')
        for name, passed, detail in identity_tests(args.identity_test):
            mark = 'PASS' if passed else 'FAIL'
            print(f'  [{mark}] {name}: {detail}')
        print()

    if args.spectrum:
        print_spectrum(args.spectrum, plot_file=args.plot)

    if not any([args.n, args.range, args.perfect, args.gap, args.identity_test, args.spectrum]):
        # Default: show n=6 full analysis
        print_analysis(6, full=True)


if __name__ == '__main__':
    main()
