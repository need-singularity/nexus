#!/usr/bin/env python3
"""Topological Lens and Telescope Calculator

Treats the R-spectrum as a 1D point cloud and applies persistent homology
(beta_0 = connected components) to study its topological structure.

Usage:
  python3 topological_optics.py --lens --n 6
  python3 topological_optics.py --lens --n 6 --N 2000 --focus 1.0
  python3 topological_optics.py --telescope --n 6
  python3 topological_optics.py --telescope --n 6 --epsilon-range 0.001-0.5 --steps 50
  python3 topological_optics.py --telescope --n 6 --local 1.0 --width 0.5
  python3 topological_optics.py --lens --n 6 --plot lens.png --json
"""

import argparse
import math
import json
from fractions import Fraction
from collections import defaultdict


# ---------------------------------------------------------------------------
# Arithmetic functions (mirrors r_spectrum.py)
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
    if n <= 0:
        return 0
    factors = factorize(n)
    result = 1
    for p, a in factors.items():
        result *= (p ** (a + 1) - 1) // (p - 1)
    return result


def phi(n):
    if n <= 0:
        return 0
    factors = factorize(n)
    result = n
    for p in factors:
        result = result * (p - 1) // p
    return result


def tau(n):
    if n <= 0:
        return 0
    factors = factorize(n)
    result = 1
    for a in factors.values():
        result *= (a + 1)
    return result


def R_exact(n):
    """R(n) = sigma(n)*phi(n)/(n*tau(n)) as exact Fraction."""
    if n <= 0:
        return Fraction(0)
    return Fraction(sigma(n) * phi(n), n * tau(n))


def R_float(n):
    return float(R_exact(n))


# ---------------------------------------------------------------------------
# Union-Find (pure Python, path compression + union by rank)
# ---------------------------------------------------------------------------

class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.count = n

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        self.count -= 1


def beta0(points, epsilon):
    """Count connected components when edges connect points within epsilon."""
    n = len(points)
    if n == 0:
        return 0
    uf = UnionFind(n)
    sorted_pts = sorted(range(n), key=lambda i: points[i])
    for k in range(len(sorted_pts) - 1):
        i = sorted_pts[k]
        j = sorted_pts[k + 1]
        if abs(points[j] - points[i]) <= epsilon:
            uf.union(i, j)
    return uf.count


# ---------------------------------------------------------------------------
# Optional ripser
# ---------------------------------------------------------------------------

try:
    import ripser as _ripser
    HAS_RIPSER = True
except ImportError:
    HAS_RIPSER = False


def ripser_barcode(points):
    """Compute H0 barcode via ripser (1D sorted points = Vietoris-Rips)."""
    import numpy as np
    pts = np.array(sorted(points)).reshape(-1, 1)
    dgms = _ripser.ripser(pts, maxdim=0)['dgms']
    bars = dgms[0]  # (birth, death) pairs
    features = []
    for birth, death in bars:
        p = death - birth if not math.isinf(death) else float('inf')
        features.append((float(birth), float(death), p))
    features.sort(key=lambda x: -x[2])
    return features


def pure_barcode(points):
    """Compute H0 barcode via sorted gaps (pure Python, exact for 1D)."""
    if not points:
        return []
    pts = sorted(points)
    gaps = []
    for i in range(len(pts) - 1):
        gaps.append((pts[i + 1] - pts[i], i))
    gaps.sort(reverse=True)

    # Each gap corresponds to one component dying
    # Birth = 0 for all, death = gap size / 2 (Rips convention)
    bars = []
    for gap_size, idx in gaps:
        birth = 0.0
        death = gap_size / 2.0
        bars.append((birth, death, death - birth))

    # Longest-lived component: infinite bar
    bars.append((0.0, float('inf'), float('inf')))
    bars.sort(key=lambda x: -x[2])
    return bars


# ---------------------------------------------------------------------------
# R-spectrum point cloud
# ---------------------------------------------------------------------------

def build_spectrum(N, low=None, high=None):
    """Compute R(n) for n=1..N, return sorted float list."""
    pts = []
    for n in range(1, N + 1):
        r = R_float(n)
        if low is not None and r < low:
            continue
        if high is not None and r > high:
            continue
        pts.append(r)
    return sorted(pts)


def focal_table(N=2000):
    """Compute focal lengths for perfect numbers P1=6, P2=28, P3=496."""
    perfect_numbers = [6, 28, 496]
    rows = []
    for pn in perfect_numbers:
        rn = R_exact(pn)
        # Nearest above and below in spectrum
        r_above = None
        r_below = None
        for m in range(1, N + 1):
            if m == pn:
                continue
            rm = R_exact(m)
            if rm > rn and (r_above is None or rm < r_above):
                r_above = rm
            elif rm < rn and (r_below is None or rm > r_below):
                r_below = rm
        delta_plus = (r_above - rn) if r_above else None
        delta_minus = (rn - r_below) if r_below else None
        focal = delta_plus * delta_minus if delta_plus and delta_minus else None
        rows.append((pn, rn, delta_plus, delta_minus, focal))
    return rows


# ---------------------------------------------------------------------------
# LENS MODE
# ---------------------------------------------------------------------------

def mode_lens(args):
    n = args.n
    N = args.N

    print(f'\n{"="*62}')
    print(f'  Topological Lens — n={n}, N={N}')
    print(f'{"="*62}')

    # Basic invariants
    s, p, t = sigma(n), phi(n), tau(n)
    rn = R_exact(n)
    print(f'\n  n={n}:  sigma={s}, phi={p}, tau={t}')
    print(f'  R({n}) = {rn} = {float(rn):.10f}')

    # Focal length table
    print(f'\n  --- Focal Length Table (perfect numbers, N={N}) ---')
    print(f'  {"P":>4s} | {"R(P)":>10s} | {"delta+":>12s} | {"delta-":>12s} | {"f=d+*d-":>14s} | {"f exact":>16s}')
    print(f'  {"":4s}-+-{"":10s}-+-{"":12s}-+-{"":12s}-+-{"":14s}-+-{"":16s}')
    rows = focal_table(N)
    for pn, rp, dp, dm, f in rows:
        dp_s = str(dp) if dp else 'N/A'
        dm_s = str(dm) if dm else 'N/A'
        f_s  = str(f)  if f  else 'N/A'
        f_fl = f'{float(f):.10f}' if f else 'N/A'
        print(f'  {pn:>4d} | {str(rp):>10s} | {dp_s:>12s} | {dm_s:>12s} | {f_s:>14s} | {f_fl:>16s}')

    # n=6 special: f = 1/24 = 1/(sigma*phi)
    print(f'\n  --- n=6 Special Identity ---')
    pn6, rp6, dp6, dm6, f6 = rows[0]
    if f6 is not None:
        inv_sphi = Fraction(1, sigma(6) * phi(6))
        match = (f6 == inv_sphi)
        print(f'  f(6)         = {f6} = {float(f6):.10f}')
        print(f'  1/(sigma*phi) = 1/({sigma(6)}*{phi(6)}) = {inv_sphi} = {float(inv_sphi):.10f}')
        print(f'  f = 1/(sigma*phi): {"YES (exact)" if match else "NO  (difference=" + str(abs(f6 - inv_sphi)) + ")"}')

    # Focus region (if --focus given)
    if args.focus is not None:
        center = args.focus
        width = 0.5
        print(f'\n  --- Focus Region [R in ({center-width:.4f}, {center+width:.4f})] ---')
        ns_in = [(m, R_float(m)) for m in range(1, N + 1)
                 if abs(R_float(m) - center) <= width]
        ns_in.sort(key=lambda x: x[1])
        print(f'  Points in region: {len(ns_in)}')
        for m, r in ns_in[:20]:
            print(f'    n={m:>5d}  R={r:.8f}')
        if len(ns_in) > 20:
            print(f'    ... ({len(ns_in)-20} more)')

    # Build point cloud
    pts = build_spectrum(N)
    print(f'\n  --- Point Cloud ---')
    print(f'  Total points: {len(pts)}')
    print(f'  Range: [{min(pts):.6f}, {max(pts):.6f}]')

    # Barcode
    print(f'\n  --- H0 Barcode (top persistent features) ---')
    if HAS_RIPSER:
        bars = ripser_barcode(pts)
        print(f'  (computed via ripser)')
    else:
        bars = pure_barcode(pts)
        print(f'  (computed via pure Python gap analysis)')

    print(f'  {"Birth":>10s} | {"Death":>12s} | {"Persistence":>12s}')
    print(f'  {"-"*10}-+-{"-"*12}-+-{"-"*12}')
    for birth, death, pers in bars[:15]:
        d_s = f'{death:.8f}' if not math.isinf(death) else 'inf'
        p_s = f'{pers:.8f}' if not math.isinf(pers) else 'inf'
        print(f'  {birth:>10.8f} | {d_s:>12s} | {p_s:>12s}')

    # Topological transitions: epsilon values where beta_0 changes
    print(f'\n  --- Topological Transitions (beta_0 step changes) ---')
    transitions = []
    prev_b0 = None
    epsilons = [i * 0.005 for i in range(1, 201)]
    for eps in epsilons:
        b = beta0(pts, eps)
        if prev_b0 is not None and b != prev_b0:
            transitions.append((eps, prev_b0, b))
        prev_b0 = b

    print(f'  {"epsilon":>10s} | {"beta_0 from":>12s} | {"beta_0 to":>10s} | {"drop":>6s}')
    print(f'  {"-"*10}-+-{"-"*12}-+-{"-"*10}-+-{"-"*6}')
    for eps, b_from, b_to in transitions[:20]:
        print(f'  {eps:>10.4f} | {b_from:>12d} | {b_to:>10d} | {b_from-b_to:>6d}')
    if len(transitions) > 20:
        print(f'  ... ({len(transitions)-20} more transitions)')

    # JSON output
    if args.json:
        out = {
            'mode': 'lens',
            'n': n,
            'N': N,
            'R_n': float(rn),
            'focal_table': [
                {'P': pn, 'R': float(rp), 'delta_plus': float(dp) if dp else None,
                 'delta_minus': float(dm) if dm else None,
                 'focal_length': float(f) if f else None}
                for pn, rp, dp, dm, f in rows
            ],
            'barcode_top5': [
                {'birth': b, 'death': d if not math.isinf(d) else None, 'persistence': p if not math.isinf(p) else None}
                for b, d, p in bars[:5]
            ],
            'transitions': [{'epsilon': e, 'from': bf, 'to': bt} for e, bf, bt in transitions[:10]],
        }
        print(f'\n  --- JSON ---')
        print(json.dumps(out, indent=2))

    # Plot
    if args.plot:
        _plot_lens(pts, bars, transitions, args.plot)

    print()


# ---------------------------------------------------------------------------
# TELESCOPE MODE
# ---------------------------------------------------------------------------

def mode_telescope(args):
    N = args.N
    n = args.n

    # Parse epsilon range
    eps_parts = args.epsilon_range.split('-')
    eps_lo, eps_hi = float(eps_parts[0]), float(eps_parts[1])
    steps = args.steps
    epsilons = [eps_lo + i * (eps_hi - eps_lo) / (steps - 1) for i in range(steps)]

    # Local region filter
    if args.local is not None:
        center = args.local
        half = args.width / 2.0
        pts = build_spectrum(N, low=center - half, high=center + half)
        region_desc = f'R in [{center-half:.4f}, {center+half:.4f}]'
    else:
        pts = build_spectrum(N)
        region_desc = f'full spectrum n=1..{N}'

    print(f'\n{"="*62}')
    print(f'  Topological Telescope — n={n}, N={N}')
    print(f'  Region: {region_desc}')
    print(f'  Epsilon: [{eps_lo}, {eps_hi}] in {steps} steps')
    print(f'{"="*62}')
    print(f'\n  Point cloud size: {len(pts)}')

    # beta_0 sweep
    b0_vals = []
    for eps in epsilons:
        b0_vals.append(beta0(pts, eps))

    # Topological sensitivity d(beta_0)/d(epsilon)
    sensitivity = []
    for i in range(1, len(epsilons)):
        db = b0_vals[i] - b0_vals[i - 1]
        de = epsilons[i] - epsilons[i - 1]
        sensitivity.append(abs(db / de) if de != 0 else 0)

    # Phase transition: where beta_0 drops fastest
    peak_idx = sensitivity.index(max(sensitivity)) if sensitivity else 0
    peak_eps = epsilons[peak_idx + 1]
    peak_drop = abs(b0_vals[peak_idx + 1] - b0_vals[peak_idx])

    print(f'\n  Phase transition peak: epsilon = {peak_eps:.5f}')
    print(f'  beta_0 drop at peak:   {b0_vals[peak_idx]} -> {b0_vals[peak_idx+1]} (drop={peak_drop})')

    # ASCII graph of beta_0 curve
    print(f'\n  --- beta_0(epsilon) curve ---')
    _ascii_curve(epsilons, b0_vals, width=55, height=16)

    # Detailed table
    print(f'\n  --- epsilon sweep table ---')
    print(f'  {"epsilon":>10s} | {"beta_0":>7s} | {"sensitivity":>12s}')
    print(f'  {"-"*10}-+-{"-"*7}-+-{"-"*12}')
    # Print every other row to keep output manageable
    stride = max(1, steps // 25)
    for i in range(0, len(epsilons), stride):
        sens = sensitivity[i - 1] if i > 0 and i - 1 < len(sensitivity) else 0.0
        peak_mark = ' <-- peak' if i == peak_idx + 1 else ''
        print(f'  {epsilons[i]:>10.5f} | {b0_vals[i]:>7d} | {sens:>12.2f}{peak_mark}')

    # Sensitivity peaks (top 5)
    if sensitivity:
        sorted_sens = sorted(enumerate(sensitivity), key=lambda x: -x[1])
        print(f'\n  --- Top sensitivity peaks ---')
        print(f'  {"rank":>4s} | {"epsilon":>10s} | {"sensitivity":>12s} | {"beta_0 drop":>12s}')
        print(f'  {"":4s}-+-{"-"*10}-+-{"-"*12}-+-{"-"*12}')
        for rank, (idx, s_val) in enumerate(sorted_sens[:5], 1):
            drop = abs(b0_vals[idx + 1] - b0_vals[idx])
            print(f'  {rank:>4d} | {epsilons[idx+1]:>10.5f} | {s_val:>12.2f} | {drop:>12d}')

    # JSON output
    if args.json:
        out = {
            'mode': 'telescope',
            'n': n,
            'N': N,
            'region': region_desc,
            'point_count': len(pts),
            'phase_transition_epsilon': peak_eps,
            'phase_transition_drop': peak_drop,
            'sweep': [{'epsilon': epsilons[i], 'beta_0': b0_vals[i]} for i in range(len(epsilons))],
        }
        print(f'\n  --- JSON ---')
        print(json.dumps(out, indent=2))

    # Plot
    if args.plot:
        _plot_telescope(epsilons, b0_vals, sensitivity, peak_eps, args.plot)

    print()


# ---------------------------------------------------------------------------
# ASCII helpers
# ---------------------------------------------------------------------------

def _ascii_curve(xs, ys, width=55, height=14):
    if not ys:
        return
    y_min, y_max = min(ys), max(ys)
    y_range = y_max - y_min if y_max != y_min else 1
    x_range = xs[-1] - xs[0] if xs[-1] != xs[0] else 1

    grid = [[' '] * width for _ in range(height)]
    for i, (x, y) in enumerate(zip(xs, ys)):
        col = int((x - xs[0]) / x_range * (width - 1))
        row = height - 1 - int((y - y_min) / y_range * (height - 1))
        col = max(0, min(width - 1, col))
        row = max(0, min(height - 1, row))
        grid[row][col] = '*'

    print(f'  beta_0')
    print(f'  {y_max:>6d} +' + '-' * width)
    for r, row in enumerate(grid):
        y_val = y_max - r * y_range / (height - 1) if height > 1 else y_max
        if r == 0 or r == height - 1 or r == height // 2:
            label = f'{int(round(y_val)):>6d} |'
        else:
            label = '       |'
        print(f'  {label}' + ''.join(row))
    print(f'  {y_min:>6d} +' + '-' * width)
    print(f'  {"":7s}' + f'{xs[0]:.4f}' + ' ' * (width - 14) + f'{xs[-1]:.4f}')
    print(f'  {"":7s}epsilon')


# ---------------------------------------------------------------------------
# Matplotlib plots
# ---------------------------------------------------------------------------

def _plot_lens(pts, bars, transitions, plot_file):
    try:
        import matplotlib.pyplot as plt
        import numpy as np

        fig, axes = plt.subplots(1, 2, figsize=(13, 5))

        # Barcode diagram
        ax = axes[0]
        finite_bars = [(b, d, p) for b, d, p in bars if not math.isinf(d)][:20]
        for i, (birth, death, pers) in enumerate(finite_bars):
            ax.plot([birth, death], [i, i], 'b-', linewidth=2)
        # Infinite bar
        inf_bars = [(b, d, p) for b, d, p in bars if math.isinf(d)]
        if inf_bars:
            b = inf_bars[0][0]
            ax.plot([b, max(d for _, d, _ in finite_bars) * 1.1 if finite_bars else 1],
                    [len(finite_bars), len(finite_bars)], 'r-', linewidth=2, label='inf bar')
        ax.set_xlabel('R value')
        ax.set_ylabel('Feature index')
        ax.set_title('H0 Barcode — R-Spectrum')
        ax.legend(fontsize=8)

        # beta_0 transitions
        ax2 = axes[1]
        eps_vals = [e for e, _, _ in transitions]
        b0_from  = [b for _, b, _ in transitions]
        if eps_vals:
            ax2.step(eps_vals, b0_from, where='post', color='steelblue')
        ax2.set_xlabel('epsilon')
        ax2.set_ylabel('beta_0')
        ax2.set_title('beta_0 at transition points')

        plt.tight_layout()
        plt.savefig(plot_file, dpi=150)
        print(f'  Plot saved to {plot_file}')
    except ImportError:
        print('  matplotlib not available, skipping plot')


def _plot_telescope(epsilons, b0_vals, sensitivity, peak_eps, plot_file):
    try:
        import matplotlib.pyplot as plt

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

        ax1.plot(epsilons, b0_vals, 'steelblue', linewidth=1.5)
        ax1.axvline(x=peak_eps, color='red', linestyle='--', alpha=0.7, label=f'phase transition e={peak_eps:.4f}')
        ax1.set_ylabel('beta_0 (components)')
        ax1.set_title('Topological Telescope — beta_0(epsilon)')
        ax1.legend(fontsize=9)

        if sensitivity:
            sens_eps = epsilons[1:]
            ax2.plot(sens_eps, sensitivity, 'darkorange', linewidth=1.5)
            ax2.axvline(x=peak_eps, color='red', linestyle='--', alpha=0.7)
            ax2.set_ylabel('|d beta_0 / d epsilon|')
            ax2.set_xlabel('epsilon')
            ax2.set_title('Topological Sensitivity')

        plt.tight_layout()
        plt.savefig(plot_file, dpi=150)
        print(f'  Plot saved to {plot_file}')
    except ImportError:
        print('  matplotlib not available, skipping plot')


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description='Topological Lens and Telescope Calculator')

    # Mode
    parser.add_argument('--lens',       action='store_true', help='Lens mode: barcode + focal length')
    parser.add_argument('--telescope',  action='store_true', help='Telescope mode: beta_0 epsilon sweep')

    # Common
    parser.add_argument('--n',  type=int, default=6,    help='Number to analyze (default 6)')
    parser.add_argument('--N',  type=int, default=2000, help='Spectrum size (default 2000)')
    parser.add_argument('--plot', type=str, help='Save plot to PNG file')
    parser.add_argument('--json', action='store_true', help='JSON output for DFS automation')

    # Lens options
    parser.add_argument('--focus', type=float, help='Zoom into region around R value (lens mode)')

    # Telescope options
    parser.add_argument('--epsilon-range', type=str, default='0.001-0.5',
                        help='Epsilon range as lo-hi (default 0.001-0.5)')
    parser.add_argument('--steps',  type=int,   default=50,  help='Sweep steps (default 50)')
    parser.add_argument('--local',  type=float, help='Focus on R neighborhood (telescope mode)')
    parser.add_argument('--width',  type=float, default=1.0, help='Local region width (default 1.0)')

    args = parser.parse_args()

    if not args.lens and not args.telescope:
        # Default: run both
        args.lens = True
        args.telescope = True

    if args.lens:
        mode_lens(args)

    if args.telescope:
        mode_telescope(args)


if __name__ == '__main__':
    main()
