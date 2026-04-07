#!/usr/bin/env python3
"""TECS-L R-Spectrum Lens Analysis of CMS Dimuon Data

Applies the gravitational/topological lens framework (n=6 perfect number optics)
to 100k real CMS dimuon events. Six analysis tasks + hypothesis generation.

Usage:
    python3 analyze_dimuon_lens.py
"""

import csv
import math
import sys
import os
from fractions import Fraction
from collections import defaultdict
import random
import time

# ---------------------------------------------------------------------------
# Arithmetic functions (from r_spectrum.py)
# ---------------------------------------------------------------------------

def factorize(n):
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
    factors = factorize(n)
    result = 1
    for p, a in factors.items():
        result *= (p ** (a + 1) - 1) // (p - 1)
    return result

def phi(n):
    factors = factorize(n)
    result = n
    for p in factors:
        result = result * (p - 1) // p
    return result

def tau(n):
    factors = factorize(n)
    result = 1
    for a in factors.values():
        result *= (a + 1)
    return result

def R(n):
    """R(n) = sigma(n)*phi(n)/(n*tau(n))"""
    s, p, t = sigma(n), phi(n), tau(n)
    return Fraction(s * p, n * t)

def R_float(n):
    return float(R(n))

def sieve(limit):
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit ** 0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, limit + 1, i):
                is_prime[j] = False
    return [i for i in range(2, limit + 1) if is_prime[i]]

# ---------------------------------------------------------------------------
# Zeta approximation for telescope
# ---------------------------------------------------------------------------

def zeta_approx(s, terms=100000):
    """Approximate zeta(s) by direct summation for s > 1."""
    if s <= 1.0:
        return float('inf')
    val = 0.0
    for n in range(1, terms + 1):
        val += 1.0 / (n ** s)
    return val

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dimuon_data.csv')

def load_masses(filepath=DATA_FILE):
    """Load dimuon invariant masses from CSV."""
    masses = []
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                m = float(row['M'])
                if m > 0:
                    masses.append(m)
            except (ValueError, KeyError):
                continue
    return masses

# ---------------------------------------------------------------------------
# Build R-spectrum reference values
# ---------------------------------------------------------------------------

def build_r_spectrum(nmax=30):
    """Build R(n) for n=2..nmax, return dict {n: R_float}."""
    return {n: R_float(n) for n in range(2, nmax + 1)}

def build_ratio_targets():
    """All target ratios to check against mass-ratio pairs."""
    targets = {}

    # R-spectrum values for primes 2..30
    primes = sieve(30)
    for p in primes:
        rv = R_float(p)
        targets[f'R({p})={rv:.4f}'] = rv

    # R-spectrum for small composites
    for n in [4, 6, 8, 9, 10, 12, 15, 16, 18, 20, 24, 28]:
        rv = R_float(n)
        targets[f'R({n})={rv:.4f}'] = rv

    # Simple integer/fraction ratios
    for val, label in [(2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6'),
                       (12, '12'), (24, '24'),
                       (0.5, '1/2'), (1.0/3, '1/3'), (0.25, '1/4'), (1.0/6, '1/6')]:
        targets[label] = val

    # Key constants
    targets['1/e=0.3679'] = 1.0 / math.e
    targets['ln(4/3)=0.2877'] = math.log(4.0 / 3.0)
    targets['sqrt(3/2)=1.2247'] = math.sqrt(1.5)  # Einstein radius

    return targets

# ---------------------------------------------------------------------------
# Task 1: R-filter on binned mass ratios
# ---------------------------------------------------------------------------

def task1_rfilter(masses):
    print('\n' + '=' * 72)
    print('  TASK 1: R-Filter on Binned Mass Ratios')
    print('=' * 72)

    # Bin masses
    bin_width = 0.1
    m_min, m_max = 0.5, 120.0
    n_bins = int((m_max - m_min) / bin_width)
    bins = [0] * n_bins
    for m in masses:
        if m_min <= m < m_max:
            idx = int((m - m_min) / bin_width)
            if 0 <= idx < n_bins:
                bins[idx] += 1

    # Non-empty bins
    nonempty = [(i, bins[i]) for i in range(n_bins) if bins[i] > 0]
    bin_centers = [(m_min + (i + 0.5) * bin_width) for i, _ in nonempty]
    bin_counts = [c for _, c in nonempty]
    print(f'\n  Non-empty bins: {len(nonempty)} (of {n_bins})')
    print(f'  Total events in bins: {sum(bin_counts)}')

    targets = build_ratio_targets()
    tolerance = 0.01  # 1%

    # Count matches
    match_counts = defaultdict(float)
    total_weighted_pairs = 0.0
    n_nonempty = len(nonempty)

    for i in range(n_nonempty):
        for j in range(i + 1, n_nonempty):
            mi, ci = bin_centers[i], bin_counts[i]
            mj, cj = bin_centers[j], bin_counts[j]
            if mi < 0.5 or mj < 0.5:
                continue
            # Always ratio > 1
            if mi > mj:
                ratio = mi / mj
            else:
                ratio = mj / mi
            weight = ci * cj

            total_weighted_pairs += weight
            for label, target in targets.items():
                t = target if target >= 1.0 else 1.0 / target
                if t > 0 and abs(ratio / t - 1.0) < tolerance:
                    match_counts[label] += weight

    print(f'  Total weighted bin pairs: {total_weighted_pairs:.0f}')
    print(f'\n  --- Matches within 1% tolerance ---')
    print(f'  {"Target Ratio":<28s} | {"Value":>8s} | {"Weighted Matches":>16s} | {"Fraction":>10s}')
    print(f'  {"-"*28}-+-{"-"*8}-+-{"-"*16}-+-{"-"*10}')

    sorted_matches = sorted(match_counts.items(), key=lambda x: -x[1])
    for label, wcount in sorted_matches[:30]:
        val = targets[label]
        frac = wcount / total_weighted_pairs if total_weighted_pairs > 0 else 0
        print(f'  {label:<28s} | {val:>8.4f} | {wcount:>16.0f} | {frac:>10.6f}')

    # Null model: what fraction of random ratios would match?
    # For uniform mass distribution, fraction of ratios within 1% of target t
    # is approximately 2*tolerance for each target
    n_targets_ge1 = sum(1 for t in targets.values() if t >= 1.0)
    n_targets_lt1 = sum(1 for t in targets.values() if t < 1.0)
    expected_rate = 2 * tolerance * (n_targets_ge1 + n_targets_lt1)
    observed_rate = sum(match_counts.values()) / total_weighted_pairs if total_weighted_pairs > 0 else 0
    print(f'\n  Expected match rate (uniform null): ~{expected_rate:.4f}')
    print(f'  Observed total match rate:          {observed_rate:.4f}')
    print(f'  Ratio observed/expected:            {observed_rate/expected_rate:.2f}' if expected_rate > 0 else '')

    return sorted_matches, total_weighted_pairs

# ---------------------------------------------------------------------------
# Task 2: Resonance peak mass ratios through R-lens
# ---------------------------------------------------------------------------

def find_peaks(masses):
    """Find resonance peaks by scanning mass histogram."""
    # High-resolution histogram
    bin_width = 0.01
    m_max = 120.0
    n_bins = int(m_max / bin_width)
    hist = [0] * n_bins
    for m in masses:
        idx = int(m / bin_width)
        if 0 <= idx < n_bins:
            hist[idx] += 1

    # Known resonance regions (GeV)
    regions = {
        'J/psi':    (2.9, 3.3),
        'psi(2S)':  (3.5, 3.9),
        'Ups(1S)':  (9.2, 9.7),
        'Ups(2S)':  (9.8, 10.2),
        'Ups(3S)':  (10.2, 10.6),
        'Z':        (85.0, 97.0),
    }

    peaks = {}
    for name, (lo, hi) in regions.items():
        lo_bin = int(lo / bin_width)
        hi_bin = int(hi / bin_width)
        best_bin = lo_bin
        best_count = 0
        for b in range(lo_bin, min(hi_bin + 1, n_bins)):
            # Smooth: sum of 5 adjacent bins
            s = sum(hist[max(0, b - 2):min(n_bins, b + 3)])
            if s > best_count:
                best_count = s
                best_bin = b
        peak_mass = (best_bin + 0.5) * bin_width
        peaks[name] = (peak_mass, best_count)

    return peaks

def task2_resonance_ratios(masses):
    print('\n' + '=' * 72)
    print('  TASK 2: Resonance Peak Mass Ratios through R-Lens')
    print('=' * 72)

    peaks = find_peaks(masses)
    print('\n  --- Measured Resonance Peaks ---')
    print(f'  {"Resonance":<12s} | {"Mass (GeV)":>12s} | {"Events (5-bin)":>14s}')
    print(f'  {"-"*12}-+-{"-"*12}-+-{"-"*14}')
    for name in ['J/psi', 'psi(2S)', 'Ups(1S)', 'Ups(2S)', 'Ups(3S)', 'Z']:
        m, c = peaks[name]
        print(f'  {name:<12s} | {m:>12.4f} | {c:>14d}')

    # Compute all ratios
    names = list(peaks.keys())
    r_spectrum = {n: R_float(n) for n in range(1, 200)}

    print('\n  --- Mass Ratios vs R-Spectrum ---')
    print(f'  {"Pair":<22s} | {"Ratio":>8s} | {"Best n":>6s} | {"R(n)":>10s} | {"Match %":>8s} | {"Note":<20s}')
    print(f'  {"-"*22}-+-{"-"*8}-+-{"-"*6}-+-{"-"*10}-+-{"-"*8}-+-{"-"*20}')

    ratio_results = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            m_i = peaks[names[i]][0]
            m_j = peaks[names[j]][0]
            if m_i < m_j:
                m_i, m_j = m_j, m_i
                n_i, n_j = names[j], names[i]
            else:
                n_i, n_j = names[i], names[j]
            ratio = m_i / m_j

            # Find closest R(n)
            best_n = None
            best_diff = float('inf')
            for n, rn in r_spectrum.items():
                if rn > 0:
                    diff = abs(ratio - rn)
                    if diff < best_diff:
                        best_diff = diff
                        best_n = n

            rn_best = r_spectrum[best_n]
            match_pct = abs(ratio / rn_best - 1.0) * 100

            # Check inverse too
            inv_ratio = 1.0 / ratio
            best_n_inv = None
            best_diff_inv = float('inf')
            for n, rn in r_spectrum.items():
                if rn > 0:
                    diff = abs(inv_ratio - rn)
                    if diff < best_diff_inv:
                        best_diff_inv = diff
                        best_n_inv = n

            note = ''
            if match_pct < 1.0:
                note = 'CLOSE (<1%)'
            elif match_pct < 5.0:
                note = 'near (<5%)'

            pair_name = f'{n_i}/{n_j}'
            ratio_results.append((pair_name, ratio, best_n, rn_best, match_pct))
            print(f'  {pair_name:<22s} | {ratio:>8.4f} | {best_n:>6d} | {rn_best:>10.4f} | {match_pct:>8.2f} | {note:<20s}')

    # Also check ratios against simple fractions
    print('\n  --- Ratios vs Simple Fractions ---')
    simple = {
        'pi': math.pi, 'e': math.e, 'phi_gold': (1 + math.sqrt(5)) / 2,
        '3': 3.0, '10/3': 10.0/3, 'sqrt(10)': math.sqrt(10),
        '2*pi': 2*math.pi, 'pi^2/6': math.pi**2/6,
    }
    for pair_name, ratio, _, _, _ in ratio_results:
        for sname, sval in simple.items():
            if abs(ratio / sval - 1.0) < 0.02:
                print(f'  {pair_name:<22s}  ratio={ratio:.4f}  ~  {sname}={sval:.4f}  ({abs(ratio/sval - 1)*100:.2f}%)')

    return peaks, ratio_results

# ---------------------------------------------------------------------------
# Task 3: Gravitational lens magnification
# ---------------------------------------------------------------------------

def task3_gravitational_lens(masses, peaks):
    print('\n' + '=' * 72)
    print('  TASK 3: Gravitational Lens Magnification (n=6 Optics)')
    print('=' * 72)

    # n=6 lens parameters
    sig6, phi6, tau6 = sigma(6), phi(6), tau(6)  # 12, 2, 4
    f_lens = 1.0 / (sig6 * phi6)  # 1/24
    theta_E = math.sqrt(sig6 / (sig6 - tau6))  # sqrt(12/8) = sqrt(3/2)
    delta_plus = 1.0 / 6  # gap+
    delta_minus = 1.0 / 4  # gap-

    print(f'\n  n=6 Lens Parameters:')
    print(f'    sigma(6)={sig6}, phi(6)={phi6}, tau(6)={tau6}')
    print(f'    Focal length f = 1/(sigma*phi) = 1/{sig6*phi6} = {f_lens:.6f}')
    print(f'    Einstein radius theta_E = sqrt(sigma/(sigma-tau)) = sqrt({sig6}/{sig6-tau6}) = {theta_E:.6f}')
    print(f'    Gap: delta+ = 1/6 = {delta_plus:.6f}, delta- = 1/4 = {delta_minus:.6f}')
    print(f'    Golden Zone width W = ln(4/3) = {math.log(4/3):.6f}')

    # Use J/psi as reference mass
    m_ref = peaks['J/psi'][0]
    print(f'\n  Reference mass: M_ref = M(J/psi) = {m_ref:.4f} GeV')

    # For each resonance, compute lens equation
    print(f'\n  --- Lens Equation: beta = theta - theta_E^2/theta ---')
    print(f'  {"Resonance":<12s} | {"M (GeV)":>10s} | {"theta":>10s} | {"beta":>10s} | {"mu":>10s} | {"Note":<20s}')
    print(f'  {"-"*12}-+-{"-"*10}-+-{"-"*10}-+-{"-"*10}-+-{"-"*10}-+-{"-"*20}')

    for name in ['J/psi', 'psi(2S)', 'Ups(1S)', 'Ups(2S)', 'Ups(3S)', 'Z']:
        m = peaks[name][0]
        theta = m / m_ref
        beta = theta - theta_E**2 / theta
        # Magnification: mu = |theta / beta| * |d(theta)/d(beta)|
        # d(beta)/d(theta) = 1 + theta_E^2/theta^2
        dbdt = 1.0 + theta_E**2 / theta**2
        if abs(dbdt) > 1e-10:
            mu = abs(theta / (theta * dbdt))  # = 1/|dbdt|
        else:
            mu = float('inf')

        note = ''
        if abs(theta - theta_E) / theta_E < 0.1:
            note = 'NEAR EINSTEIN RING'
        if abs(mu - 1.0) < 0.01:
            note = 'no magnification'

        print(f'  {name:<12s} | {m:>10.4f} | {theta:>10.4f} | {beta:>10.4f} | {mu:>10.4f} | {note:<20s}')

    # Scan: which observed masses are near the Einstein ring?
    # theta_E = sqrt(3/2) ~ 1.2247, so M_ring = theta_E * m_ref
    m_ring = theta_E * m_ref
    print(f'\n  Einstein ring mass: {theta_E:.4f} * {m_ref:.4f} = {m_ring:.4f} GeV')

    # Count events near the ring mass
    ring_tol = 0.1  # GeV
    near_ring = sum(1 for m in masses if abs(m - m_ring) < ring_tol)
    print(f'  Events within {ring_tol} GeV of ring: {near_ring}')

    # Multi-image: for a source at beta, solve theta^2 - beta*theta - theta_E^2 = 0
    print(f'\n  --- Multi-Image Prediction ---')
    print(f'  For source at each resonance beta, predict image positions:')
    print(f'  {"Source":<12s} | {"beta":>8s} | {"theta+":>10s} | {"M+(GeV)":>10s} | {"theta-":>10s} | {"M-(GeV)":>10s}')
    print(f'  {"-"*12}-+-{"-"*8}-+-{"-"*10}-+-{"-"*10}-+-{"-"*10}-+-{"-"*10}')

    for name in ['J/psi', 'psi(2S)', 'Ups(1S)', 'Z']:
        m = peaks[name][0]
        beta = m / m_ref - theta_E**2 * m_ref / m
        # Actually use the source position beta directly
        # theta^2 - beta*theta - theta_E^2 = 0
        disc = beta**2 + 4 * theta_E**2
        if disc >= 0:
            theta_p = (beta + math.sqrt(disc)) / 2
            theta_m = (beta - math.sqrt(disc)) / 2
            m_p = theta_p * m_ref
            m_m = theta_m * m_ref
            print(f'  {name:<12s} | {beta:>8.4f} | {theta_p:>10.4f} | {m_p:>10.4f} | {theta_m:>10.4f} | {m_m:>10.4f}')

    return m_ring

# ---------------------------------------------------------------------------
# Task 4: Topological persistence on mass spectrum
# ---------------------------------------------------------------------------

def task4_persistence(masses):
    print('\n' + '=' * 72)
    print('  TASK 4: Topological Persistence (H0) on Mass Spectrum')
    print('=' * 72)

    # Bin the mass spectrum more coarsely for persistence
    bin_width = 0.05
    m_max = 120.0
    n_bins = int(m_max / bin_width)
    hist = [0] * n_bins
    for m in masses:
        idx = int(m / bin_width)
        if 0 <= idx < n_bins:
            hist[idx] += 1

    # Sublevel set filtration on NEGATIVE histogram (to find peaks as persistent features)
    # We negate: f(x) = -count(x), then sublevel sets capture peaks first
    neg_hist = [-h for h in hist]

    # Compute H0 persistence diagram via union-find on 1D function
    # Sort function values, process in increasing order
    n = len(neg_hist)
    indices = sorted(range(n), key=lambda i: neg_hist[i])

    parent = list(range(n))
    rank_uf = [0] * n
    active = [False] * n
    birth = [0.0] * n
    persistence_pairs = []

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y, death_val):
        rx, ry = find(x), find(y)
        if rx == ry:
            return
        # Younger component (higher birth = less negative = smaller peak) dies
        if neg_hist[indices[0]] == 0:
            pass
        # Component born later (higher function value at birth) dies
        if birth[rx] > birth[ry]:
            # rx dies
            persistence_pairs.append((birth[rx], death_val, death_val - birth[rx]))
            dying, surviving = rx, ry
        else:
            persistence_pairs.append((birth[ry], death_val, death_val - birth[ry]))
            dying, surviving = ry, rx

        if rank_uf[surviving] < rank_uf[dying]:
            surviving, dying = dying, surviving
        parent[dying] = surviving
        if rank_uf[surviving] == rank_uf[dying]:
            rank_uf[surviving] += 1

    for idx in indices:
        active[idx] = True
        birth[idx] = neg_hist[idx]

        # Check left neighbor
        if idx > 0 and active[idx - 1]:
            if find(idx) != find(idx - 1):
                union(idx, idx - 1, neg_hist[idx])

        # Check right neighbor
        if idx < n - 1 and active[idx + 1]:
            if find(idx) != find(idx + 1):
                union(idx, idx + 1, neg_hist[idx])

    # Sort by persistence (most persistent first)
    persistence_pairs.sort(key=lambda x: -x[2])

    print(f'\n  Histogram: {n_bins} bins of {bin_width} GeV, range [0, {m_max}] GeV')
    print(f'  Max bin count: {max(hist)}')
    print(f'  Non-empty bins: {sum(1 for h in hist if h > 0)}')

    print(f'\n  --- H0 Persistence Diagram (sublevel set on -count) ---')
    print(f'  Most persistent features = tallest peaks in mass spectrum')
    print(f'  {"Rank":>4s} | {"Birth":>8s} | {"Death":>8s} | {"Persist":>8s} | {"Peak Mass":>10s} | {"Count":>6s} | {"Identity":<12s}')
    print(f'  {"-"*4}-+-{"-"*8}-+-{"-"*8}-+-{"-"*8}-+-{"-"*10}-+-{"-"*6}-+-{"-"*12}')

    # Map back to mass: find which bin corresponds to birth
    known_resonances = [
        ('Z', 88.0, 95.0),
        ('J/psi', 3.0, 3.2),
        ('psi(2S)', 3.6, 3.8),
        ('Ups(1S)', 9.3, 9.6),
        ('Ups(2S)', 9.9, 10.1),
        ('Ups(3S)', 10.3, 10.5),
        ('phi(1020)', 0.95, 1.1),
        ('omega', 0.75, 0.85),
        ('rho', 0.65, 0.85),
    ]

    top_peaks = []
    for rank, (b, d, p) in enumerate(persistence_pairs[:20], 1):
        # Birth value is the negative count at peak
        peak_count = int(-b)
        # Find the bin with this count
        candidates = [i for i in range(n_bins) if hist[i] == peak_count]
        if candidates:
            peak_bin = candidates[0]
            peak_mass = (peak_bin + 0.5) * bin_width
        else:
            # Approximate
            peak_mass = 0.0

        # Identify resonance
        identity = ''
        for rname, rlo, rhi in known_resonances:
            if rlo <= peak_mass <= rhi:
                identity = rname
                break

        top_peaks.append((rank, b, d, p, peak_mass, peak_count, identity))
        print(f'  {rank:>4d} | {b:>8.1f} | {d:>8.1f} | {p:>8.1f} | {peak_mass:>10.4f} | {peak_count:>6d} | {identity:<12s}')

    # Check persistence ratios against n=6 arithmetic
    print(f'\n  --- Persistence Ratios vs n=6 Arithmetic ---')
    if len(persistence_pairs) >= 2:
        p_vals = [p for _, _, p in persistence_pairs[:10] if p > 0]
        print(f'  {"P_i/P_j":<16s} | {"Value":>8s} | {"Close to":>20s}')
        print(f'  {"-"*16}-+-{"-"*8}-+-{"-"*20}')
        check_vals = {
            '1/2': 0.5, '1/3': 1/3, '1/4': 0.25, '1/6': 1/6,
            '2/3': 2/3, '3/4': 0.75, '5/6': 5/6,
            '1/e': 1/math.e, 'ln(4/3)': math.log(4/3),
            'R(2)=3/4': 0.75, 'R(3)=4/3': 4/3, 'R(5)=6/5': 1.2,
        }
        for i in range(min(6, len(p_vals))):
            for j in range(i + 1, min(6, len(p_vals))):
                ratio = p_vals[j] / p_vals[i] if p_vals[i] != 0 else 0
                matches = []
                for cname, cval in check_vals.items():
                    if cval > 0 and abs(ratio / cval - 1.0) < 0.05:
                        matches.append(f'{cname} ({abs(ratio/cval - 1)*100:.1f}%)')
                if matches:
                    print(f'  P_{i+1}/P_{j+1}         | {ratio:>8.4f} | {", ".join(matches)}')

    return persistence_pairs

# ---------------------------------------------------------------------------
# Task 5: Spectral telescope scan
# ---------------------------------------------------------------------------

def task5_spectral_telescope(masses, peaks):
    print('\n' + '=' * 72)
    print('  TASK 5: Spectral Telescope Scan F(s) = zeta(s)*zeta(s+1)')
    print('=' * 72)

    # Compute F(s) for a range of s values
    print('\n  Computing zeta values (direct summation, 100k terms)...')
    s_values = [1.5 + 0.1 * i for i in range(36)]  # 1.5 to 5.0

    # Reference: F(2) = zeta(2)*zeta(3) = (pi^2/6)*1.20206...
    z2 = math.pi**2 / 6.0
    z3 = zeta_approx(3.0, 100000)
    F2 = z2 * z3
    print(f'  F(2) = zeta(2)*zeta(3) = {z2:.6f} * {z3:.6f} = {F2:.6f}')

    m_ref = peaks['J/psi'][0]
    print(f'  Reference mass: M_ref = M(J/psi) = {m_ref:.4f} GeV')

    # Compute spectral masses
    print(f'\n  --- Spectral Mass Scan ---')
    print(f'  M_F(s) = M_ref * F(s) / F(2)')
    print(f'\n  {"s":>6s} | {"zeta(s)":>10s} | {"zeta(s+1)":>10s} | {"F(s)":>12s} | {"M_F (GeV)":>10s} | {"Closest Res":>14s} | {"Off %":>8s}')
    print(f'  {"-"*6}-+-{"-"*10}-+-{"-"*10}-+-{"-"*12}-+-{"-"*10}-+-{"-"*14}-+-{"-"*8}')

    resonance_masses = {name: peaks[name][0] for name in peaks}
    spectral_hits = []

    for s in s_values:
        zs = zeta_approx(s, 50000)
        zs1 = zeta_approx(s + 1, 50000)
        Fs = zs * zs1
        M_F = m_ref * Fs / F2

        # Find closest resonance
        best_res = None
        best_diff = float('inf')
        for rname, rmass in resonance_masses.items():
            diff = abs(M_F - rmass) / rmass
            if diff < best_diff:
                best_diff = diff
                best_res = rname

        off_pct = best_diff * 100
        mark = ''
        if off_pct < 5.0:
            mark = ' <-- HIT'
            spectral_hits.append((s, M_F, best_res, off_pct))

        print(f'  {s:>6.2f} | {zs:>10.6f} | {zs1:>10.6f} | {Fs:>12.6f} | {M_F:>10.4f} | {best_res:>14s} | {off_pct:>7.2f}%{mark}')

    print(f'\n  --- Spectral Hits (within 5%) ---')
    for s, mf, rname, off in spectral_hits:
        print(f'  s={s:.2f}: M_F={mf:.4f} GeV ~ {rname} (off by {off:.2f}%)')

    # Also scan with different reference masses
    print(f'\n  --- Scan with M_ref = Z mass ---')
    m_ref_z = peaks['Z'][0]
    for s in [2.0, 2.5, 3.0, 4.0]:
        zs = zeta_approx(s, 50000)
        zs1 = zeta_approx(s + 1, 50000)
        Fs = zs * zs1
        M_F = m_ref_z * Fs / F2
        print(f'  s={s:.1f}: F(s)/F(2)={Fs/F2:.6f}, M_F={M_F:.4f} GeV')

    return spectral_hits

# ---------------------------------------------------------------------------
# Task 6: Hypothesis generation
# ---------------------------------------------------------------------------

def task6_hypotheses(masses, peaks, ratio_results, persistence_pairs,
                     spectral_hits, task1_results, total_wpairs, m_ring):
    print('\n' + '=' * 72)
    print('  TASK 6: Hypothesis Generation')
    print('=' * 72)

    hypotheses = []

    # --- H1: Mass ratio clustering around R-spectrum ---
    # Count how many of the top ratio matches exceed random expectation
    if task1_results:
        top_match = task1_results[0]
        label, wcount = top_match
        frac = wcount / total_wpairs if total_wpairs > 0 else 0
        expected = 0.02  # ~2% for random uniform
        z_score = (frac - expected) / max(0.001, math.sqrt(expected * (1 - expected) / 1000))
        hypotheses.append({
            'id': 'H-CMS-1',
            'claim': f'Dimuon mass ratios cluster preferentially near R-spectrum value {label}',
            'evidence': f'Weighted fraction {frac:.4f} vs expected ~{expected:.4f}',
            'z_score': z_score,
            'grade': 'pending'
        })

    # --- H2: J/psi to Z ratio and R-spectrum ---
    if 'Z' in peaks and 'J/psi' in peaks:
        m_z = peaks['Z'][0]
        m_j = peaks['J/psi'][0]
        ratio_zj = m_z / m_j
        # Check nearby R values
        best_n, best_r, best_diff = None, None, float('inf')
        for n in range(1, 200):
            rn = R_float(n)
            if abs(ratio_zj - rn) < best_diff:
                best_diff = abs(ratio_zj - rn)
                best_n = n
                best_r = rn
        hypotheses.append({
            'id': 'H-CMS-2',
            'claim': f'Z/J_psi mass ratio = {ratio_zj:.4f} is close to R({best_n}) = {best_r:.4f}',
            'evidence': f'Deviation = {best_diff:.4f} ({best_diff/ratio_zj*100:.2f}%)',
            'z_score': 0,
            'grade': 'pending'
        })

    # --- H3: Upsilon family ratios match R-spectrum fractions ---
    if 'Ups(1S)' in peaks and 'Ups(2S)' in peaks and 'Ups(3S)' in peaks:
        m1 = peaks['Ups(1S)'][0]
        m2 = peaks['Ups(2S)'][0]
        m3 = peaks['Ups(3S)'][0]
        r12 = m2 / m1
        r13 = m3 / m1
        r23 = m3 / m2
        hypotheses.append({
            'id': 'H-CMS-3',
            'claim': f'Upsilon family mass ratios: 2S/1S={r12:.4f}, 3S/1S={r13:.4f}, 3S/2S={r23:.4f}',
            'evidence': f'Compare: R(6)=1.000, near-unity ratios reflect nearly degenerate R-spectrum',
            'z_score': 0,
            'grade': 'pending'
        })

    # --- H4: Einstein ring mass prediction ---
    hypotheses.append({
        'id': 'H-CMS-4',
        'claim': f'n=6 Einstein ring predicts enhanced event density at M = {m_ring:.4f} GeV',
        'evidence': f'theta_E = sqrt(3/2) = {math.sqrt(1.5):.4f}, M_ring = theta_E * M(J/psi)',
        'z_score': 0,
        'grade': 'pending'
    })

    # Count events near m_ring
    near_ring = sum(1 for m in masses if abs(m - m_ring) < 0.1)
    # Compare to adjacent bins
    below = sum(1 for m in masses if abs(m - (m_ring - 0.5)) < 0.1)
    above = sum(1 for m in masses if abs(m - (m_ring + 0.5)) < 0.1)
    avg_adj = (below + above) / 2.0
    if avg_adj > 0:
        excess = near_ring / avg_adj
        hypotheses[-1]['evidence'] += f'\nEvents at ring: {near_ring}, adjacent avg: {avg_adj:.0f}, ratio: {excess:.2f}'

    # --- H5: Persistence hierarchy follows n=6 divisor structure ---
    if len(persistence_pairs) >= 4:
        p_vals = [p for _, _, p in persistence_pairs[:6] if p > 0]
        if len(p_vals) >= 2:
            r01 = p_vals[1] / p_vals[0] if p_vals[0] != 0 else 0
            hypotheses.append({
                'id': 'H-CMS-5',
                'claim': f'Persistence ratio P2/P1 = {r01:.4f} relates to n=6 divisor structure',
                'evidence': f'P1={p_vals[0]:.1f}, P2={p_vals[1]:.1f}, ratio={r01:.4f}',
                'z_score': 0,
                'grade': 'pending'
            })

    # --- H6: Spectral telescope hits ---
    if spectral_hits:
        best_hit = min(spectral_hits, key=lambda x: x[3])
        hypotheses.append({
            'id': 'H-CMS-6',
            'claim': f'F(s={best_hit[0]:.2f}) predicts mass {best_hit[1]:.4f} GeV, matching {best_hit[2]} within {best_hit[3]:.2f}%',
            'evidence': f'F(s) = zeta(s)*zeta(s+1), with M_ref = J/psi',
            'z_score': 0,
            'grade': 'pending'
        })

    # --- H7: J/psi to psi(2S) ratio ---
    if 'J/psi' in peaks and 'psi(2S)' in peaks:
        m_j = peaks['J/psi'][0]
        m_p = peaks['psi(2S)'][0]
        ratio = m_p / m_j
        # Check against R(n) values
        best_n, best_r = None, None
        best_diff = float('inf')
        for n in range(1, 100):
            rn = R_float(n)
            if abs(ratio - rn) < best_diff:
                best_diff = abs(ratio - rn)
                best_n = n
                best_r = rn
        hypotheses.append({
            'id': 'H-CMS-7',
            'claim': f'psi(2S)/J_psi = {ratio:.4f} maps to R({best_n}) = {best_r:.4f} (off {best_diff/ratio*100:.2f}%)',
            'evidence': f'Charmonium excitation ratio filtered through R-spectrum',
            'z_score': 0,
            'grade': 'pending'
        })

    # --- H8: Golden Zone width in mass spectrum ---
    W = math.log(4.0 / 3.0)
    # Check if any pair of adjacent resonances has mass ratio = e^W = 4/3
    hypotheses.append({
        'id': 'H-CMS-8',
        'claim': f'Golden Zone width W = ln(4/3) = {W:.4f} appears as mass-ratio scale',
        'evidence': 'Check: exp(W) = 4/3 = 1.3333',
        'z_score': 0,
        'grade': 'pending'
    })
    # Search for mass ratios near 4/3
    target = 4.0 / 3.0
    near_43_count = 0
    names_list = list(peaks.keys())
    for i in range(len(names_list)):
        for j in range(i+1, len(names_list)):
            mi = peaks[names_list[i]][0]
            mj = peaks[names_list[j]][0]
            r = max(mi, mj) / min(mi, mj)
            if abs(r / target - 1.0) < 0.02:
                near_43_count += 1
                hypotheses[-1]['evidence'] += f'\n  {names_list[i]}/{names_list[j]} = {r:.4f} ~ 4/3'

    # --- H9: Mass spectrum modular structure ---
    # Check if peak masses mod some value cluster
    m_vals = [peaks[name][0] for name in peaks]
    m_vals_sorted = sorted(m_vals)
    diffs = [m_vals_sorted[i+1] - m_vals_sorted[i] for i in range(len(m_vals_sorted)-1)]
    hypotheses.append({
        'id': 'H-CMS-9',
        'claim': 'Resonance mass differences show arithmetic regularity',
        'evidence': 'Mass gaps: ' + ', '.join(f'{d:.4f}' for d in diffs),
        'z_score': 0,
        'grade': 'pending'
    })

    # --- H10: Perfect number 6 as lens quality metric ---
    hypotheses.append({
        'id': 'H-CMS-10',
        'claim': 'R(6)=1 (perfect lens, zero chromatic aberration) selects mass ratios with highest population',
        'evidence': 'R(6)=1 means sigma*phi=n*tau, the only lens with zero aberration',
        'z_score': 0,
        'grade': 'pending'
    })

    # --- H11: Continuum background follows 1/M^alpha, alpha relates to R-spectrum ---
    # Fit power law to continuum (excluding resonance regions)
    exclude = [(2.8, 3.4), (3.5, 3.9), (9.0, 10.8), (85, 97)]
    continuum_masses = []
    for m in masses:
        excluded = False
        for lo, hi in exclude:
            if lo <= m <= hi:
                excluded = True
                break
        if not excluded and m > 1.0:
            continuum_masses.append(m)

    if continuum_masses:
        # Simple power law: log(count) ~ -alpha * log(M)
        log_m = [math.log(m) for m in continuum_masses]
        mean_logm = sum(log_m) / len(log_m)
        # Estimate alpha from mean
        alpha_est = 1.0 / mean_logm if mean_logm > 0 else 0

        hypotheses.append({
            'id': 'H-CMS-11',
            'claim': f'Continuum background power-law exponent relates to R-spectrum',
            'evidence': f'Mean log(M) of continuum = {mean_logm:.4f}, events={len(continuum_masses)}',
            'z_score': 0,
            'grade': 'pending'
        })

    # --- H12: Statistical test: R-spectrum ratios vs random ---
    # Monte Carlo: generate random masses from empirical distribution, check match rates
    print(f'\n  --- Monte Carlo null test (R-spectrum ratio matching) ---')
    n_mc = 1000
    rng = random.Random(42)
    targets = build_ratio_targets()
    tolerance = 0.01

    # Observed: ratio of consecutive resonance masses matching R-spectrum within 1%
    obs_hits = 0
    total_pairs_res = 0
    for rr in ratio_results:
        total_pairs_res += 1
        if rr[4] < 1.0:  # match_pct < 1%
            obs_hits += 1
    obs_rate = obs_hits / total_pairs_res if total_pairs_res > 0 else 0

    # Null: random mass pairs from 1-100 GeV
    null_hits = []
    for _ in range(n_mc):
        m1 = rng.uniform(1, 100)
        m2 = rng.uniform(1, 100)
        ratio = max(m1, m2) / min(m1, m2)
        hit = 0
        for label, target in targets.items():
            t = target if target >= 1.0 else 1.0 / target
            if t > 0 and abs(ratio / t - 1.0) < tolerance:
                hit = 1
                break
        null_hits.append(hit)

    null_rate = sum(null_hits) / n_mc
    print(f'  Observed resonance-pair R-match rate (<1%): {obs_rate:.4f} ({obs_hits}/{total_pairs_res})')
    print(f'  Null random-pair R-match rate:              {null_rate:.4f}')

    if null_rate > 0:
        enrichment = obs_rate / null_rate
        print(f'  Enrichment factor:                          {enrichment:.2f}x')
    else:
        enrichment = float('inf')
        print(f'  Enrichment factor:                          inf (no null hits)')

    hypotheses.append({
        'id': 'H-CMS-12',
        'claim': f'Resonance mass ratios are {enrichment:.1f}x enriched for R-spectrum matches vs random',
        'evidence': f'Obs rate={obs_rate:.4f}, null rate={null_rate:.4f}, MC n={n_mc}',
        'z_score': 0,
        'grade': 'pending'
    })

    # --- Compute p-values and assign grades ---
    print(f'\n  {"="*68}')
    print(f'  HYPOTHESIS SUMMARY')
    print(f'  {"="*68}')
    print(f'\n  {"ID":<12s} | {"Grade":>5s} | {"Claim (truncated)":<60s}')
    print(f'  {"-"*12}-+-{"-"*5}-+-{"-"*60}')

    for h in hypotheses:
        # Assign preliminary grade
        # Without rigorous Texas Sharpshooter test, all are pending
        h['grade'] = 'pending (needs Texas Sharpshooter test)'
        claim_short = h['claim'][:60]
        print(f'  {h["id"]:<12s} | {"??":>5s} | {claim_short:<60s}')

    print(f'\n  Total hypotheses generated: {len(hypotheses)}')
    print(f'\n  NOTE: All grades are PENDING.')
    print(f'  Per CLAUDE.md rules:')
    print(f'    - No grade assignment without Texas Sharpshooter test')
    print(f'    - No star marking before verification')
    print(f'    - Ad hoc corrections (+1/-1) cannot receive star grade')
    print(f'    - All claims are Golden-Zone-dependent (model, unverified)')

    # Print detailed hypotheses
    print(f'\n  {"="*68}')
    print(f'  DETAILED HYPOTHESES')
    print(f'  {"="*68}')
    for h in hypotheses:
        print(f'\n  --- {h["id"]} ---')
        print(f'  Claim:    {h["claim"]}')
        print(f'  Evidence: {h["evidence"]}')
        print(f'  Grade:    {h["grade"]}')

    return hypotheses


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    t0 = time.time()
    print('=' * 72)
    print('  TECS-L R-Spectrum Lens Analysis of CMS Dimuon Data')
    print('  Framework: n=6 perfect number optics (gravitational + topological)')
    print('=' * 72)

    print('\n  Loading data...')
    masses = load_masses()
    print(f'  Loaded {len(masses)} events from {DATA_FILE}')
    print(f'  Mass range: [{min(masses):.4f}, {max(masses):.4f}] GeV')
    print(f'  Mean mass: {sum(masses)/len(masses):.4f} GeV')
    print(f'  Median mass: {sorted(masses)[len(masses)//2]:.4f} GeV')

    # Quick histogram
    print(f'\n  --- Mass Distribution (ASCII) ---')
    bins_ascii = [0] * 20
    edges = [0.5 + i * 6.0 for i in range(21)]
    for m in masses:
        for b in range(20):
            if edges[b] <= m < edges[b + 1]:
                bins_ascii[b] += 1
                break
    max_count = max(bins_ascii) if bins_ascii else 1
    for b in range(20):
        bar_len = int(50 * bins_ascii[b] / max_count)
        label = f'  [{edges[b]:>5.1f},{edges[b+1]:>5.1f})'
        print(f'{label} |{"#" * bar_len} {bins_ascii[b]}')

    # Run all tasks
    task1_results, total_wpairs = task1_rfilter(masses)
    peaks, ratio_results = task2_resonance_ratios(masses)
    m_ring = task3_gravitational_lens(masses, peaks)
    persistence_pairs = task4_persistence(masses)
    spectral_hits = task5_spectral_telescope(masses, peaks)
    hypotheses = task6_hypotheses(masses, peaks, ratio_results, persistence_pairs,
                                  spectral_hits, task1_results, total_wpairs, m_ring)

    elapsed = time.time() - t0
    print(f'\n{"="*72}')
    print(f'  Analysis complete in {elapsed:.1f}s')
    print(f'  Events analyzed: {len(masses)}')
    print(f'  Hypotheses generated: {len(hypotheses)}')
    print(f'{"="*72}')


if __name__ == '__main__':
    main()
