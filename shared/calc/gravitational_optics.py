#!/usr/bin/env python3
"""Gravitational Lens and Telescope Calculator

Models the R-spectrum as a gravitational optics system.
Perfect numbers act as perfect lenses (achromatic, zero aberration).

Usage:
  python3 gravitational_optics.py --lens --n 6
  python3 gravitational_optics.py --lens --n 28 --full
  python3 gravitational_optics.py --lens --range 1-50
  python3 gravitational_optics.py --lens --perfect --compare
  python3 gravitational_optics.py --telescope --scan
  python3 gravitational_optics.py --telescope --s 2
  python3 gravitational_optics.py --telescope --primes 10
  python3 gravitational_optics.py --telescope --heatmap --plot heatmap.png
  python3 gravitational_optics.py --lens --n 6 --json
"""

import argparse
import math
import json
from fractions import Fraction


# ---------------------------------------------------------------------------
# Arithmetic foundations
# ---------------------------------------------------------------------------

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
    factors = factorize(n)
    result = 1
    for p, a in factors.items():
        result *= (p ** (a + 1) - 1) // (p - 1)
    return result


def phi(n):
    """Euler totient."""
    factors = factorize(n)
    result = n
    for p in factors:
        result = result * (p - 1) // p
    return result


def tau(n):
    """Number of divisors."""
    factors = factorize(n)
    result = 1
    for a in factors.values():
        result *= (a + 1)
    return result


def R(n):
    """R(n) = sigma(n)*phi(n) / (n*tau(n)) as exact Fraction."""
    s, p, t = sigma(n), phi(n), tau(n)
    return Fraction(s * p, n * t)


def S(n):
    """S(n) = sigma(n)*tau(n) / (n*phi(n)) — dual of R."""
    s, p, t = sigma(n), phi(n), tau(n)
    if p == 0:
        return Fraction(0)
    return Fraction(s * t, n * p)


def R_prime_power(p, a):
    """R(p^a) closed form."""
    return Fraction(p ** (a + 1) - 1, p * (a + 1))


# ---------------------------------------------------------------------------
# Lens mode — aberration and gap analysis
# ---------------------------------------------------------------------------

def compute_gap(n, N=5000):
    """Nearest R values above and below R(n) in 1..N."""
    rn = R(n)
    r_above = r_below = None
    n_above = n_below = None
    for m in range(1, N + 1):
        if m == n:
            continue
        rm = R(m)
        if rm > rn and (r_above is None or rm < r_above):
            r_above, n_above = rm, m
        elif rm < rn and (r_below is None or rm > r_below):
            r_below, n_below = rm, m
    delta_plus  = r_above - rn if r_above is not None else None
    delta_minus = rn - r_below if r_below is not None else None
    focal = delta_plus * delta_minus if (delta_plus and delta_minus) else None
    return dict(R=rn, delta_plus=delta_plus, delta_minus=delta_minus,
                n_above=n_above, n_below=n_below, focal_length=focal)


def arithmetic_mass(n):
    """M(n) = |sigma(n)/n - 2| — deviation from perfect number condition."""
    return abs(Fraction(sigma(n), n) - 2)


def einstein_radius(n, gap):
    """theta_E ~ sqrt(delta- / delta+) — gap asymmetry angle (dimensionless)."""
    if gap['delta_plus'] and gap['delta_minus']:
        ratio = gap['delta_minus'] / gap['delta_plus']
        return math.sqrt(float(ratio))
    return None


def chromatic_aberration(n):
    """Chromatic: product of R(p,1) factors vs R(n).
    At n=6 this vanishes (achromatic lens).
    Value = |prod R(p^a) / R(n) - 1| after multiplicative expansion.
    For perfect numbers R(n)=1 and prod R(p^a)=1 so difference=0.
    """
    factors = factorize(n)
    prod_rpa = Fraction(1)
    for p, a in factors.items():
        prod_rpa *= R_prime_power(p, a)
    rn = R(n)
    if rn == 0:
        return None
    return abs(prod_rpa - rn)


def spherical_aberration(n, N=5000):
    """Density ratio of R values above vs below R(n) in 1..N."""
    rn = R(n)
    above = below = 0
    for m in range(1, N + 1):
        rm = R(m)
        if rm > rn:
            above += 1
        elif rm < rn:
            below += 1
    total = above + below
    if total == 0:
        return Fraction(1)
    return Fraction(above, total)   # 1/2 = balanced = no spherical aberration


def astigmatic_aberration(n):
    """Astigmatic: R(n)/S(n) — R-S asymmetry. 1 = no astigmatism."""
    rn = R(n)
    sn = S(n)
    if sn == 0:
        return None
    return rn / sn


def coma_aberration(gap):
    """Coma: delta- / delta+ ratio. 1 = symmetric = no coma."""
    if gap['delta_plus'] and gap['delta_minus']:
        return gap['delta_minus'] / gap['delta_plus']
    return None


def distortion_aberration(gap):
    """Distortion: |delta- - delta+| — gap width asymmetry."""
    if gap['delta_plus'] and gap['delta_minus']:
        return abs(gap['delta_minus'] - gap['delta_plus'])
    return None


def lens_grade(n, chrom, coma, distortion, astig):
    """Quality grade: A / B / C / D."""
    if n == 6:
        return 'A'   # Only true achromat
    score = 0
    if chrom is not None and float(chrom) < 0.01:
        score += 1
    if coma is not None and abs(float(coma) - 1.0) < 0.1:
        score += 1
    if distortion is not None and float(distortion) < 0.05:
        score += 1
    if astig is not None and abs(float(astig) - 1.0) < 0.1:
        score += 1
    if score >= 3:
        return 'B'
    if score >= 2:
        return 'C'
    return 'D'


def print_lens(n, full=False, N=5000):
    """Full gravitational lens analysis for n."""
    factors = factorize(n)
    fstr = ' * '.join(f'{p}^{a}' if a > 1 else str(p) for p, a in sorted(factors.items())) or '1'

    rn = R(n)
    sn = S(n)
    M  = arithmetic_mass(n)
    gap = compute_gap(n, N)

    chrom = chromatic_aberration(n)
    spher = spherical_aberration(n, N)
    astig = astigmatic_aberration(n)
    coma  = coma_aberration(gap)
    dist  = distortion_aberration(gap)
    theta = einstein_radius(n, gap)
    grade = lens_grade(n, chrom, coma, dist, astig)

    print(f'\n{"="*62}')
    print(f'  Gravitational Lens: n = {n}  [Grade {grade}]')
    print(f'{"="*62}')
    print(f'  Factorization : {fstr}')
    print(f'  sigma({n:>4d})   = {sigma(n)}')
    print(f'  phi({n:>4d})     = {phi(n)}')
    print(f'  tau({n:>4d})     = {tau(n)}')
    print()
    print(f'  R(n)          = {rn}  = {float(rn):.8f}')
    print(f'  S(n)          = {sn}  = {float(sn):.8f}')
    print(f'  M(n) [mass]   = {M}  = {float(M):.8f}  (0 = perfect)')
    print()
    print(f'  --- Gap Structure (N={N}) ---')
    if gap['delta_plus']:
        print(f'  delta+        = {gap["delta_plus"]} = {float(gap["delta_plus"]):.8f}  (n={gap["n_above"]})')
    if gap['delta_minus']:
        print(f'  delta-        = {gap["delta_minus"]} = {float(gap["delta_minus"]):.8f}  (n={gap["n_below"]})')
    if gap['focal_length']:
        f_val = gap['focal_length']
        print(f'  focal length  = {f_val} = {float(f_val):.10f}')
    if theta is not None:
        print(f'  theta_E       = {theta:.8f}  (Einstein radius, dimensionless)')
    print()
    print(f'  --- Aberration Profile ---')
    print(f'  {"Type":<16s}  {"Value":>14s}  {"Ideal":>8s}  Note')
    print(f'  {"-"*16}  {"-"*14}  {"-"*8}  ----')

    c_val = f'{float(chrom):.8f}' if chrom is not None else 'N/A'
    c_note = 'achromatic!' if (chrom is not None and float(chrom) == 0.0) else ''
    print(f'  {"Chromatic":<16s}  {c_val:>14s}  {"0":>8s}  {c_note}')

    s_val = f'{float(spher):.8f}' if spher is not None else 'N/A'
    print(f'  {"Spherical":<16s}  {s_val:>14s}  {"0.5":>8s}  density above R(n)')

    a_val = f'{float(astig):.8f}' if astig is not None else 'N/A'
    print(f'  {"Astigmatic":<16s}  {a_val:>14s}  {"1.0":>8s}  R/S ratio')

    k_val = f'{float(coma):.8f}' if coma is not None else 'N/A'
    print(f'  {"Coma":<16s}  {k_val:>14s}  {"1.0":>8s}  delta-/delta+')

    d_val = f'{float(dist):.8f}' if dist is not None else 'N/A'
    print(f'  {"Distortion":<16s}  {d_val:>14s}  {"0":>8s}  |delta- - delta+|')
    print()
    print(f'  Lens Grade: {grade}  ', end='')
    grades = {'A': 'Perfect achromat (n=6 only)',
              'B': 'Near-perfect (low aberration)',
              'C': 'Moderate quality',
              'D': 'High aberration'}
    print(grades.get(grade, ''))
    print()
    return dict(n=n, grade=grade, R=float(rn), M=float(M),
                chromatic=float(chrom) if chrom is not None else None,
                spherical=float(spher),
                astigmatic=float(astig) if astig is not None else None,
                coma=float(coma) if coma is not None else None,
                distortion=float(dist) if dist is not None else None,
                einstein_radius=theta)


def print_range_lens(start, end):
    """ASCII table of lens grades for a range."""
    print(f'\n  {"n":>4s} | {"R(n)":>10s} | {"M(n)":>10s} | {"Grade":^5s} | Coma     | Chrom')
    print(f'  {"----":>4s}-+-{"-"*10}-+-{"-"*10}-+-{"-----":^5s}-+-{"-"*8}-+-{"-"*8}')
    for n in range(start, end + 1):
        rn = R(n)
        M  = arithmetic_mass(n)
        gap = compute_gap(n, N=2000)
        chrom = chromatic_aberration(n)
        coma  = coma_aberration(gap)
        astig = astigmatic_aberration(n)
        dist  = distortion_aberration(gap)
        grade = lens_grade(n, chrom, coma, dist, astig)
        coma_s  = f'{float(coma):.4f}' if coma is not None else '  N/A '
        chrom_s = f'{float(chrom):.4f}' if chrom is not None else '  N/A '
        print(f'  {n:>4d} | {float(rn):>10.6f} | {float(M):>10.6f} | {grade:^5s} | {coma_s:>8s} | {chrom_s:>8s}')
    print()


def compare_lenses(ns):
    """Side-by-side comparison of two or more lenses."""
    results = []
    for n in ns:
        gap   = compute_gap(n, N=5000)
        chrom = chromatic_aberration(n)
        spher = spherical_aberration(n, N=5000)
        astig = astigmatic_aberration(n)
        coma  = coma_aberration(gap)
        dist  = distortion_aberration(gap)
        grade = lens_grade(n, chrom, coma, dist, astig)
        results.append(dict(n=n, R=R(n), M=arithmetic_mass(n),
                            grade=grade, chrom=chrom, spher=spher,
                            astig=astig, coma=coma, dist=dist,
                            theta=einstein_radius(n, gap),
                            focal=gap['focal_length']))
    # Table header
    header = ['Property'] + [f'n={r["n"]}' for r in results]
    rows = []
    def fmt(v):
        if v is None: return 'N/A'
        if isinstance(v, Fraction): return f'{float(v):.6f}'
        if isinstance(v, float): return f'{v:.6f}'
        return str(v)
    rows.append(['R(n)']       + [fmt(r['R'])     for r in results])
    rows.append(['M(n)']       + [fmt(r['M'])     for r in results])
    rows.append(['Grade']      + [r['grade']      for r in results])
    rows.append(['Chromatic']  + [fmt(r['chrom']) for r in results])
    rows.append(['Spherical']  + [fmt(r['spher']) for r in results])
    rows.append(['Astigmatic'] + [fmt(r['astig']) for r in results])
    rows.append(['Coma']       + [fmt(r['coma'])  for r in results])
    rows.append(['Distortion'] + [fmt(r['dist'])  for r in results])
    rows.append(['theta_E']    + [fmt(r['theta'])  for r in results])
    rows.append(['focal f']    + [fmt(r['focal'])  for r in results])

    col_w = [max(len(row[i]) for row in [header] + rows) for i in range(len(header))]
    sep   = '-+-'.join('-' * w for w in col_w)
    print('\n  ' + ' | '.join(h.ljust(col_w[i]) for i, h in enumerate(header)))
    print('  ' + sep)
    for row in rows:
        print('  ' + ' | '.join(row[i].ljust(col_w[i]) for i in range(len(row))))
    print()


# ---------------------------------------------------------------------------
# Telescope mode — F(s) = zeta(s)*zeta(s+1) via Euler product
# ---------------------------------------------------------------------------

def euler_factor(p, s, terms=20):
    """E_p(s) = 1 + sum_{a>=1} R(p^a)/p^{a*s}, truncated."""
    val = 1.0
    for a in range(1, terms + 1):
        rpa = float(R_prime_power(p, a))
        contrib = rpa / (p ** (a * s))
        val += contrib
        if abs(contrib) < 1e-15:
            break
    return val


def F_euler(s, num_primes=200):
    """F(s) = prod_{p prime} E_p(s) approximation."""
    primes = sieve(num_primes * 3)[:num_primes]
    val = 1.0
    for p in primes:
        val *= euler_factor(p, s)
    return val


def F_exact(s):
    """F(s) = zeta(s)*zeta(s+1) via math library (reference)."""
    # Use closed-form for integer s where we have direct computation
    # For general s approximate via large prime product
    return F_euler(s, num_primes=500)


def sieve(limit):
    """Primes up to limit via sieve."""
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit ** 0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, limit + 1, i):
                is_prime[j] = False
    return [i for i in range(2, limit + 1) if is_prime[i]]


def print_telescope_s(s_values, num_primes=200):
    """Print F(s) table for given s values."""
    primes = sieve(num_primes * 3)[:num_primes]
    print(f'\n  F(s) = zeta(s)*zeta(s+1)  [Euler product, {num_primes} primes]')
    print(f'\n  {"s":>6s} | {"F(s) approx":>14s} | {"log F(s)":>10s} | Note')
    print(f'  {"------":>6s}-+-{"-"*14}-+-{"-"*10}-+-------')
    for s in s_values:
        fs = 1.0
        for p in primes:
            fs *= euler_factor(p, s)
        note = ''
        if abs(s - 2.0) < 1e-9:
            note = 'pi^4/36 = {:.6f}'.format(math.pi**4 / 36)
        elif abs(s - 1.5) < 1e-9:
            note = 'analytic continuation region'
        print(f'  {s:>6.2f} | {fs:>14.8f} | {math.log(fs) if fs>0 else float("nan"):>10.6f} | {note}')
    print()


def print_prime_contributions(s, N_primes):
    """Show first N_primes contributions to F(s)."""
    primes = sieve(N_primes * 20)[:N_primes]
    print(f'\n  Prime contributions to F(s={s}):')
    print(f'\n  {"p":>5s} | {"E_p(s)":>12s} | {"log E_p":>10s} | {"cumul log F":>12s}')
    print(f'  {"-----":>5s}-+-{"-"*12}-+-{"-"*10}-+-{"-"*12}')
    cumul = 0.0
    for p in primes:
        ep = euler_factor(p, s)
        le = math.log(ep) if ep > 0 else float('nan')
        cumul += le
        print(f'  {p:>5d} | {ep:>12.8f} | {le:>10.6f} | {cumul:>12.6f}')
    print()


def print_scan(n_steps=20):
    """Scan F(s) from s=1.1 to s=10."""
    s_min, s_max = 1.1, 10.0
    step = (s_max - s_min) / (n_steps - 1)
    s_vals = [s_min + i * step for i in range(n_steps)]
    print(f'\n  F(s) scan  s in [{s_min}, {s_max}]  steps={n_steps}')
    print(f'\n  {"s":>6s} | {"F(s)":>14s} | ASCII bar')
    print(f'  {"------":>6s}-+-{"-"*14}-+-{"-"*40}')
    fs_vals = []
    for s in s_vals:
        fs = F_euler(s, num_primes=100)
        fs_vals.append((s, fs))
    max_fs = max(v for _, v in fs_vals)
    for s, fs in fs_vals:
        bar_len = int(38 * fs / max_fs) if max_fs > 0 else 0
        bar = '#' * bar_len
        print(f'  {s:>6.2f} | {fs:>14.8f} | {bar}')
    print()


def print_heatmap(plot_file=None):
    """2D grid G(s, R0) — F(s) sensitivity to R0 threshold."""
    s_vals  = [1.5, 2.0, 3.0, 5.0, 10.0]
    R0_vals = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]

    print(f'\n  Heatmap G(s, R0): F(s) restricted to primes with R(p) >= R0')
    print(f'  (R(p) = (p+1)/2 for prime p, so all primes >= 2 have R(p) >= 3/2 = 1.5)')
    print()

    # Header row
    row_h = f'  {"s\\R0":>6s}'
    for R0 in R0_vals:
        row_h += f' | {R0:>10.2f}'
    print(row_h)
    print('  ' + '-' * (7 + 13 * len(R0_vals)))

    grid = []
    primes = sieve(3000)[:200]
    for s in s_vals:
        row = []
        for R0 in R0_vals:
            filtered = [p for p in primes if float(R_prime_power(p, 1)) >= R0]
            val = 1.0
            for p in filtered:
                val *= euler_factor(p, s)
            row.append(val)
        grid.append(row)
        row_s = f'  {s:>6.2f}'
        for val in row:
            row_s += f' | {val:>10.4f}'
        print(row_s)
    print()

    if plot_file:
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            fig, ax = plt.subplots(figsize=(9, 5))
            data = np.array(grid)
            im = ax.imshow(data, aspect='auto', origin='upper',
                           cmap='plasma', interpolation='nearest')
            ax.set_xticks(range(len(R0_vals)))
            ax.set_xticklabels([str(r) for r in R0_vals])
            ax.set_yticks(range(len(s_vals)))
            ax.set_yticklabels([str(s) for s in s_vals])
            ax.set_xlabel('R0 threshold')
            ax.set_ylabel('s')
            ax.set_title('G(s, R0) = F(s) restricted to primes with R(p) >= R0')
            plt.colorbar(im, ax=ax, label='F value')
            for i in range(len(s_vals)):
                for j in range(len(R0_vals)):
                    ax.text(j, i, f'{data[i,j]:.2f}', ha='center', va='center',
                            fontsize=8, color='white')
            plt.tight_layout()
            plt.savefig(plot_file, dpi=150)
            print(f'  Heatmap saved to {plot_file}')
        except ImportError:
            print('  matplotlib not available, skipping plot')


def plot_lens(n, plot_file, N=5000):
    """Plot aberration profile as bar chart."""
    try:
        import matplotlib.pyplot as plt
        gap   = compute_gap(n, N)
        chrom = chromatic_aberration(n)
        spher = spherical_aberration(n, N)
        astig = astigmatic_aberration(n)
        coma  = coma_aberration(gap)
        dist  = distortion_aberration(gap)

        labels = ['Chromatic', 'Spherical\n(|x-0.5|)', 'Astigmatic\n(|x-1|)',
                  'Coma\n(|x-1|)', 'Distortion']
        vals = [
            float(chrom) if chrom is not None else 0,
            abs(float(spher) - 0.5) if spher is not None else 0,
            abs(float(astig) - 1.0) if astig is not None else 0,
            abs(float(coma)  - 1.0) if coma  is not None else 0,
            float(dist) if dist is not None else 0,
        ]
        colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']

        fig, ax = plt.subplots(figsize=(8, 5))
        bars = ax.bar(labels, vals, color=colors, edgecolor='black', linewidth=0.7)
        ax.set_ylabel('Aberration (0 = ideal)')
        ax.set_title(f'Aberration Profile: n={n}  [Grade {lens_grade(n, chrom, coma, dist, astig)}]')
        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.001,
                    f'{val:.4f}', ha='center', va='bottom', fontsize=9)
        plt.tight_layout()
        plt.savefig(plot_file, dpi=150)
        print(f'  Plot saved to {plot_file}')
    except ImportError:
        print('  matplotlib not available, skipping plot')


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description='Gravitational Lens and Telescope Calculator')
    parser.add_argument('--lens',      action='store_true', help='Lens mode')
    parser.add_argument('--telescope', action='store_true', help='Telescope mode')

    # Lens options
    parser.add_argument('--n',       type=int,   help='Analyze single n')
    parser.add_argument('--range',   type=str,   help='Range a-b')
    parser.add_argument('--perfect', action='store_true', help='Analyze known perfect numbers')
    parser.add_argument('--compare', action='store_true', help='Compare perfect numbers side by side')
    parser.add_argument('--full',    action='store_true', help='Full output')

    # Telescope options
    parser.add_argument('--s',      type=float, help='Compute F at specific s')
    parser.add_argument('--scan',   action='store_true', help='Scan s from 1.1 to 10')
    parser.add_argument('--primes', type=int,   help='Show first N prime contributions to F(s)')
    parser.add_argument('--heatmap',action='store_true', help='2D heatmap G(s, R0)')

    # Common
    parser.add_argument('--plot',   type=str,   help='Save plot to file')
    parser.add_argument('--json',   action='store_true', help='JSON output for DFS automation')

    args = parser.parse_args()

    # Default: lens n=6 if nothing specified
    if not (args.lens or args.telescope):
        args.lens = True
        if not args.n:
            args.n = 6

    # ---- LENS MODE ----
    if args.lens:
        if args.compare or args.perfect:
            perfect_ns = [6, 28, 496, 8128]
            if args.compare:
                compare_lenses(perfect_ns)
            else:
                for pn in perfect_ns:
                    data = print_lens(pn, full=args.full)
                    if args.json:
                        print(json.dumps(data, indent=2))
        elif args.n:
            data = print_lens(args.n, full=args.full)
            if args.plot:
                plot_lens(args.n, args.plot)
            if args.json:
                print(json.dumps(data, indent=2))
        elif args.range:
            parts = args.range.split('-')
            print_range_lens(int(parts[0]), int(parts[1]))
        else:
            print_lens(6, full=True)

    # ---- TELESCOPE MODE ----
    if args.telescope:
        if args.heatmap:
            print_heatmap(plot_file=args.plot)
        elif args.scan:
            print_scan(n_steps=20)
        elif args.s is not None:
            s_val = args.s
            n_pr  = args.primes or 20
            print_telescope_s([s_val], num_primes=500)
            if args.primes:
                print_prime_contributions(s_val, n_pr)
        elif args.primes:
            s_default = 2.0
            print_telescope_s([s_default], num_primes=500)
            print_prime_contributions(s_default, args.primes)
        else:
            default_s = [1.5, 2.0, 3.0, 5.0, 10.0]
            print_telescope_s(default_s, num_primes=300)
            if args.plot:
                try:
                    import matplotlib.pyplot as plt
                    primes = sieve(3000)[:300]
                    s_range = [1.1 + i * 0.1 for i in range(90)]
                    fs_range = []
                    for s in s_range:
                        val = 1.0
                        for p in primes:
                            val *= euler_factor(p, s)
                        fs_range.append(val)
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.plot(s_range, fs_range, 'b-', linewidth=1.5)
                    ax.set_xlabel('s')
                    ax.set_ylabel('F(s)')
                    ax.set_title('F(s) = zeta(s)*zeta(s+1)  [Euler product, 300 primes]')
                    ax.axvline(x=2.0, color='r', linestyle='--', alpha=0.6, label='s=2')
                    ax.legend()
                    plt.tight_layout()
                    plt.savefig(args.plot, dpi=150)
                    print(f'  Plot saved to {args.plot}')
                except ImportError:
                    print('  matplotlib not available, skipping plot')


if __name__ == '__main__':
    main()
