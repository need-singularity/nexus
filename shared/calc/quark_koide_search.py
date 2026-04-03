#!/usr/bin/env python3
"""Quark Koide Search — Find Koide-like parametrizations using n=6 arithmetic

Searches for generalized Koide formulas connecting quark masses to
perfect number 6 constants: sigma=12, tau=4, phi=2, P1=6, R=1.

For leptons, the Koide formula K = (sum m_i)/(sum sqrt(m_i))^2 = 2/3 = tau/P1
with angle delta = 2/9 = phi*tau^2/sigma^2 determines all 3 masses to 5 ppm.

This script searches for analogous relations in the quark sector.

Usage:
  python3 calc/quark_koide_search.py              # Full search
  python3 calc/quark_koide_search.py --extended    # Extended alpha/beta search
  python3 calc/quark_koide_search.py --ckm         # CKM analysis only
  python3 calc/quark_koide_search.py --verbose     # Show all attempts
"""

import argparse
import math
import sys
from fractions import Fraction
from itertools import product

# ═══════════════════════════════════════════════════════════════
# Constants
# ═══════════════════════════════════════════════════════════════

# n=6 arithmetic constants
SIGMA = 12    # sum of divisors sigma(6)
TAU = 4       # number of divisors tau(6)
PHI = 2       # Euler totient phi(6)
P1 = 6        # the perfect number itself
R = 1         # R(6) = sigma(6)/6 - 1 = 1
SOPFR = 5     # sum of prime factors with repetition: 2+3

# PDG 2024 quark masses (MeV)
# MS-bar at 2 GeV for light quarks, pole mass for top
MU = 2.16      # up
MD = 4.67      # down
MS = 93.4      # strange
MC = 1270.0    # charm
MB = 4180.0    # bottom
MT = 172500.0  # top (pole mass)

# Lepton masses (MeV) for reference
ME = 0.51099895   # electron
M_MU = 105.6584   # muon
M_TAU = 1776.86   # tau

# CKM matrix elements (PDG 2024 magnitudes)
V_UD = 0.97373;  V_US = 0.2243;  V_UB = 0.00382
V_CD = 0.221;    V_CS = 0.975;   V_CB = 0.0408
V_TD = 0.0086;   V_TS = 0.0415;  V_TB = 1.014

CABIBBO_ANGLE_DEG = 13.02  # degrees
CABIBBO_ANGLE_RAD = math.radians(CABIBBO_ANGLE_DEG)

# n=6 target values for matching
N6_TARGETS = {}
# Build target dictionary from n=6 arithmetic
_vals = {
    'sigma': SIGMA, 'tau': TAU, 'phi': PHI, 'P1': P1, 'R': R, 'sopfr': SOPFR,
}
# Single values
for name, v in _vals.items():
    N6_TARGETS[name] = v
# Ratios
for n1, v1 in _vals.items():
    for n2, v2 in _vals.items():
        if n1 != n2 and v2 != 0:
            key = f"{n1}/{n2}"
            N6_TARGETS[key] = v1 / v2
# Products
for n1, v1 in _vals.items():
    for n2, v2 in _vals.items():
        if n1 <= n2:
            key = f"{n1}*{n2}"
            N6_TARGETS[key] = v1 * v2
# Simple fractions with small integers
for p in range(1, 25):
    for q in range(1, 25):
        f = Fraction(p, q)
        key = f"{f.numerator}/{f.denominator}"
        if key not in N6_TARGETS and f.numerator <= 24 and f.denominator <= 24:
            N6_TARGETS[key] = float(f)
# Special combinations
N6_TARGETS['2/3'] = 2/3       # lepton Koide
N6_TARGETS['2/9'] = 2/9       # lepton Koide angle
N6_TARGETS['1/3'] = 1/3       # meta fixed point
N6_TARGETS['1/6'] = 1/6
N6_TARGETS['5/6'] = 5/6
N6_TARGETS['1/e'] = 1/math.e
N6_TARGETS['phi*tau^2/sigma^2'] = PHI * TAU**2 / SIGMA**2  # = 2/9
N6_TARGETS['tau/P1'] = TAU / P1  # = 2/3
N6_TARGETS['phi/P1'] = PHI / P1  # = 1/3
N6_TARGETS['phi/sigma'] = PHI / SIGMA  # = 1/6
N6_TARGETS['tau/sigma'] = TAU / SIGMA  # = 1/3
N6_TARGETS['sopfr/sigma'] = SOPFR / SIGMA  # = 5/12
N6_TARGETS['(tau-1)/sigma'] = 3 / SIGMA  # = 1/4
N6_TARGETS['phi/tau'] = PHI / TAU  # = 1/2
N6_TARGETS['sigma/P1^2'] = SIGMA / P1**2  # = 1/3
N6_TARGETS['tau^2/sigma'] = TAU**2 / SIGMA  # = 4/3
N6_TARGETS['sigma^2/P1^3'] = SIGMA**2 / P1**3  # = 2/3
N6_TARGETS['ln2'] = math.log(2)


# ═══════════════════════════════════════════════════════════════
# Koide Formula Utilities
# ═══════════════════════════════════════════════════════════════

def koide_ratio(m1, m2, m3):
    """Standard Koide ratio K = (m1+m2+m3)/(sqrt(m1)+sqrt(m2)+sqrt(m3))^2"""
    num = m1 + m2 + m3
    den = (math.sqrt(m1) + math.sqrt(m2) + math.sqrt(m3)) ** 2
    return num / den

def koide_angle(m1, m2, m3):
    """Extract Koide angle delta from masses.
    Parametrization: sqrt(m_k) = A(1 + sqrt(2)*cos(2*pi*k/3 + delta))
    """
    s = [math.sqrt(m) for m in (m1, m2, m3)]
    A = sum(s) / 3.0
    # Normalized: y_k = s_k/A - 1, then y_k = sqrt(2)*cos(2*pi*k/3 + delta)
    y = [(si / A - 1) for si in s]
    # delta from y[0] = sqrt(2)*cos(delta)
    cos_d = y[0] / math.sqrt(2)
    if abs(cos_d) > 1:
        return None
    delta = math.acos(cos_d)
    # Verify with y[1]
    y1_pred = math.sqrt(2) * math.cos(2 * math.pi / 3 + delta)
    if abs(y[1] - y1_pred) > 0.01 * (abs(y[1]) + 0.001):
        delta = -delta  # try negative
        y1_pred = math.sqrt(2) * math.cos(2 * math.pi / 3 + delta)
        if abs(y[1] - y1_pred) > 0.01 * (abs(y[1]) + 0.001):
            return None  # parametrization doesn't fit well
    return delta

def masses_from_koide(A, delta):
    """Reconstruct masses from Koide parameters A and delta."""
    masses = []
    for k in range(3):
        s = A * (1 + math.sqrt(2) * math.cos(2 * math.pi * k / 3 + delta))
        if s < 0:
            return None
        masses.append(s ** 2)
    return masses

def generalized_koide(masses, alpha, beta):
    """Generalized Koide: K = (sum m_i^alpha) / (sum m_i^beta)^(alpha/beta)"""
    num = sum(m ** alpha for m in masses)
    den = sum(m ** beta for m in masses)
    if den == 0:
        return None
    return num / den ** (alpha / beta)

def find_n6_match(value, threshold=0.01):
    """Find best n=6 arithmetic match for a value."""
    best = None
    best_err = float('inf')
    for name, target in N6_TARGETS.items():
        if target == 0:
            continue
        err = abs(value - target) / abs(target)
        if err < best_err:
            best_err = err
            best = (name, target, err)
    return best


# ═══════════════════════════════════════════════════════════════
# Section 1: Standard Koide on Quark Triplets
# ═══════════════════════════════════════════════════════════════

def test_standard_koide():
    """Test standard Koide formula on all quark triplet combinations."""
    print("=" * 72)
    print("SECTION 1: STANDARD KOIDE FORMULA ON QUARK TRIPLETS")
    print("=" * 72)
    print()
    print("  Koide formula: K = (m1+m2+m3) / (sqrt(m1)+sqrt(m2)+sqrt(m3))^2")
    print("  Lepton value:  K = 2/3 = 0.6667 (exact to 5 ppm)")
    print()

    quarks = {
        'u': MU, 'd': MD, 's': MS, 'c': MC, 'b': MB, 't': MT
    }
    qnames = list(quarks.keys())
    qvals = list(quarks.values())

    # Named triplets
    named = [
        ("up-type (u,c,t)",     MU, MC, MT),
        ("down-type (d,s,b)",   MD, MS, MB),
        ("gen-1 (u,d,s)",       MU, MD, MS),
        ("gen-1+2 (u,d,c)",     MU, MD, MC),
        ("heavy (c,b,t)",       MC, MB, MT),
        ("light (u,d,s)",       MU, MD, MS),
        ("cross-1 (u,s,b)",     MU, MS, MB),
        ("cross-2 (d,c,t)",     MD, MC, MT),
        ("cross-3 (u,s,t)",     MU, MS, MT),
        ("cross-4 (d,c,b)",     MD, MC, MB),
    ]
    # Also add leptons for reference
    named.insert(0, ("LEPTONS (e,mu,tau)", ME, M_MU, M_TAU))

    results = []
    print(f"  {'Triplet':<24s} {'K':>10s} {'Best n=6':>20s} {'Error':>10s}")
    print(f"  {'-'*24} {'-'*10} {'-'*20} {'-'*10}")

    for label, m1, m2, m3 in named:
        K = koide_ratio(m1, m2, m3)
        match = find_n6_match(K)
        flag = " ***" if match and match[2] < 0.01 else ""
        err_str = f"{match[2]*100:.4f}%" if match else "N/A"
        print(f"  {label:<24s} {K:10.6f} {match[0]:>20s} {err_str:>10s}{flag}")
        results.append((label, K, match))

    # Koide angle analysis
    print()
    print("  Koide Angle Analysis (delta in the parametrization):")
    print(f"  {'Triplet':<24s} {'delta':>10s} {'delta/pi':>10s} {'Best n=6':>20s} {'Error':>10s}")
    print(f"  {'-'*24} {'-'*10} {'-'*10} {'-'*20} {'-'*10}")

    for label, m1, m2, m3 in named:
        d = koide_angle(m1, m2, m3)
        if d is not None:
            d_over_pi = d / math.pi
            match_d = find_n6_match(d)
            match_dp = find_n6_match(d_over_pi)
            # pick better match
            if match_d and match_dp:
                if match_d[2] < match_dp[2]:
                    best = match_d
                    val_str = f"{d:.6f}"
                    label2 = f"delta={best[0]}"
                else:
                    best = match_dp
                    val_str = f"{d_over_pi:.6f}"
                    label2 = f"d/pi={best[0]}"
            elif match_d:
                best = match_d
                val_str = f"{d:.6f}"
                label2 = f"delta={best[0]}"
            else:
                best = match_dp
                val_str = f"{d_over_pi:.6f}"
                label2 = f"d/pi={best[0]}"
            flag = " ***" if best[2] < 0.01 else ""
            err_str = f"{best[2]*100:.4f}%"
            print(f"  {label:<24s} {d:10.6f} {d_over_pi:10.6f} {label2:>20s} {err_str:>10s}{flag}")
        else:
            print(f"  {label:<24s} {'N/A':>10s}")

    return results


# ═══════════════════════════════════════════════════════════════
# Section 2: Generalized Koide Angle Search
# ═══════════════════════════════════════════════════════════════

def search_koide_angles():
    """Search for n=6 arithmetic expressions matching quark Koide angles."""
    print()
    print("=" * 72)
    print("SECTION 2: KOIDE ANGLE SEARCH (delta from n=6 arithmetic)")
    print("=" * 72)
    print()
    print("  Parametrization: sqrt(m_k) = A(1 + sqrt(2)*cos(2*pi*k/3 + delta))")
    print("  Lepton delta = 2/9 = phi*tau^2/sigma^2 = 0.2222...")
    print()

    triplets = [
        ("up-type (u,c,t)", [MU, MC, MT]),
        ("down-type (d,s,b)", [MD, MS, MB]),
    ]

    # Build candidate deltas from n=6 arithmetic
    # Form: (a*phi + b*tau + c*sigma + d*P1) / (e*phi + f*tau + g*sigma + h*P1)
    # with small integer coefficients
    candidate_deltas = {}
    vals = {'phi': PHI, 'tau': TAU, 'sigma': SIGMA, 'P1': P1, 'sopfr': SOPFR}

    # Rational combinations p/q from n=6 related numbers
    n6_nums = [1, 2, 3, 4, 5, 6, 8, 9, 10, 12, 16, 18, 20, 24, 36, 48, 72, 144]
    for p in n6_nums:
        for q in n6_nums:
            if p != q:
                val = p / q
                # Only interested in values that could be angles (roughly 0 to pi)
                if 0 < val < 4:
                    f = Fraction(p, q)
                    candidate_deltas[f"{f.numerator}/{f.denominator}"] = val

    # Also try products/powers of n=6 constants
    for n1, v1 in vals.items():
        for n2, v2 in vals.items():
            for n3, v3 in vals.items():
                # v1 * v2 / v3^2
                if v3 != 0:
                    val = v1 * v2 / v3**2
                    if 0 < val < 4:
                        candidate_deltas[f"{n1}*{n2}/{n3}^2"] = val
                # v1 / (v2 * v3)
                if v2 * v3 != 0:
                    val = v1 / (v2 * v3)
                    if 0 < val < 4:
                        candidate_deltas[f"{n1}/({n2}*{n3})"] = val

    for label, masses in triplets:
        print(f"  --- {label} ---")

        # Get actual Koide angle
        actual_delta = koide_angle(*masses)
        if actual_delta is None:
            print(f"  Koide parametrization does not fit this triplet well.")
            print()
            continue

        K = koide_ratio(*masses)
        print(f"  Koide ratio K = {K:.6f}")
        print(f"  Actual delta   = {actual_delta:.6f} ({actual_delta/math.pi:.6f} pi)")
        print()

        # Search for matching delta
        hits = []
        for name, d_candidate in candidate_deltas.items():
            err = abs(actual_delta - d_candidate) / abs(actual_delta)
            if err < 0.05:  # within 5%
                # Reconstruct masses and check
                A_val = sum(math.sqrt(m) for m in masses) / 3.0
                pred_masses = masses_from_koide(A_val, d_candidate)
                if pred_masses:
                    mass_errs = [abs(pred - act) / act * 100
                                 for pred, act in zip(sorted(pred_masses), sorted(masses))]
                    hits.append((name, d_candidate, err, mass_errs))

        hits.sort(key=lambda x: x[2])
        if hits:
            print(f"  {'Expression':<25s} {'delta':>10s} {'Error':>10s} {'Mass errors (%)':>30s}")
            print(f"  {'-'*25} {'-'*10} {'-'*10} {'-'*30}")
            for name, d_val, err, merrs in hits[:15]:
                merr_str = ", ".join(f"{e:.2f}" for e in merrs)
                flag = " ***" if err < 0.01 else ""
                print(f"  {name:<25s} {d_val:10.6f} {err*100:9.4f}% [{merr_str}]{flag}")
        else:
            print(f"  No n=6 matches within 5% for delta={actual_delta:.6f}")
        print()

    # Direct mass ratio search
    print("  --- Mass Ratio Analysis ---")
    print()
    all_quarks = [('u', MU), ('d', MD), ('s', MS), ('c', MC), ('b', MB), ('t', MT)]
    print(f"  {'Ratio':<12s} {'Value':>12s} {'Best n=6':>20s} {'Error':>10s}")
    print(f"  {'-'*12} {'-'*12} {'-'*20} {'-'*10}")

    for i in range(len(all_quarks)):
        for j in range(i+1, len(all_quarks)):
            n1, m1 = all_quarks[i]
            n2, m2 = all_quarks[j]
            ratio = m2 / m1
            # Check ratio
            match = find_n6_match(ratio, 0.05)
            # Check sqrt of ratio
            sr = math.sqrt(ratio)
            match_s = find_n6_match(sr, 0.05)
            # Check log of ratio
            lr = math.log(ratio)
            match_l = find_n6_match(lr, 0.05)

            candidates = []
            if match:
                candidates.append((match, ratio, ''))
            if match_s:
                candidates.append((match_s, sr, 'sqrt'))
            if match_l:
                candidates.append((match_l, lr, 'log'))
            candidates.sort(key=lambda x: x[0][2])

            # Just show everything with decent matches
            for m, v, typ in [(match, ratio, ''), (match_s, sr, 'sqrt'), (match_l, lr, 'log')]:
                if m and m[2] < 0.01:
                    flag = " ***"
                    lbl = f"{n2}/{n1}" if typ == '' else f"{typ}({n2}/{n1})"
                    print(f"  {lbl:<12s} {v:12.4f} {m[0]:>20s} {m[2]*100:9.4f}%{flag}")


# ═══════════════════════════════════════════════════════════════
# Section 3: Extended Koide Formulas
# ═══════════════════════════════════════════════════════════════

def search_extended_koide(verbose=False):
    """Search for generalized Koide formulas with varying exponents."""
    print()
    print("=" * 72)
    print("SECTION 3: EXTENDED KOIDE FORMULAS")
    print("=" * 72)
    print()
    print("  K_ext = (sum m_i^alpha) / (sum m_i^beta)^(alpha/beta)")
    print("  alpha, beta in {1/4, 1/3, 1/2, 2/3, 1, 3/2, 2, 3}")
    print()

    triplets = [
        ("up-type (u,c,t)", [MU, MC, MT]),
        ("down-type (d,s,b)", [MD, MS, MB]),
        ("LEPTONS (e,mu,tau)", [ME, M_MU, M_TAU]),
    ]

    exponents = [
        (Fraction(1, 4), '1/4'),
        (Fraction(1, 3), '1/3'),
        (Fraction(1, 2), '1/2'),
        (Fraction(2, 3), '2/3'),
        (Fraction(1, 1), '1'),
        (Fraction(3, 2), '3/2'),
        (Fraction(2, 1), '2'),
        (Fraction(3, 1), '3'),
    ]

    for label, masses in triplets:
        print(f"  --- {label} ---")
        hits = []

        for (a, a_name), (b, b_name) in product(exponents, repeat=2):
            if a == b:
                continue
            af, bf = float(a), float(b)
            try:
                K = generalized_koide(masses, af, bf)
                if K is None or K <= 0 or math.isnan(K) or math.isinf(K):
                    continue
                match = find_n6_match(K)
                if match and match[2] < 0.01:
                    hits.append((a_name, b_name, K, match[0], match[1], match[2]))
            except (ValueError, OverflowError, ZeroDivisionError):
                continue

        hits.sort(key=lambda x: x[5])
        if hits:
            print(f"  {'alpha':>6s} {'beta':>6s} {'K_ext':>12s} {'n=6 match':>20s} {'target':>10s} {'Error':>10s}")
            print(f"  {'-'*6} {'-'*6} {'-'*12} {'-'*20} {'-'*10} {'-'*10}")
            for a_n, b_n, K, mname, mtarget, merr in hits[:20]:
                flag = " ***" if merr < 0.005 else ""
                print(f"  {a_n:>6s} {b_n:>6s} {K:12.6f} {mname:>20s} {mtarget:10.6f} {merr*100:9.4f}%{flag}")
        else:
            print(f"  No matches with error < 1%")
        print()

    # Also try K = (sum m_i^a) / (sum m_i^b) without the power normalization
    print("  --- Simple ratio: K = (sum m_i^a) / (sum m_i^b)  [no power rescaling] ---")
    print()
    for label, masses in triplets:
        print(f"  {label}:")
        hits = []
        for (a, a_name), (b, b_name) in product(exponents, repeat=2):
            if a == b:
                continue
            af, bf = float(a), float(b)
            try:
                num = sum(m ** af for m in masses)
                den = sum(m ** bf for m in masses)
                if den == 0:
                    continue
                K = num / den
                if K <= 0 or math.isnan(K) or math.isinf(K):
                    continue
                match = find_n6_match(K)
                if match and match[2] < 0.01:
                    hits.append((a_name, b_name, K, match[0], match[1], match[2]))
            except (ValueError, OverflowError, ZeroDivisionError):
                continue

        hits.sort(key=lambda x: x[5])
        if hits:
            print(f"    {'alpha':>6s} {'beta':>6s} {'K':>14s} {'n=6 match':>20s} {'target':>12s} {'Error':>10s}")
            print(f"    {'-'*6} {'-'*6} {'-'*14} {'-'*20} {'-'*12} {'-'*10}")
            for a_n, b_n, K, mname, mtarget, merr in hits[:20]:
                flag = " ***" if merr < 0.005 else ""
                print(f"    {a_n:>6s} {b_n:>6s} {K:14.6f} {mname:>20s} {mtarget:12.6f} {merr*100:9.4f}%{flag}")
        else:
            print(f"    No matches with error < 1%")
        print()


# ═══════════════════════════════════════════════════════════════
# Section 4: CKM Matrix and n=6
# ═══════════════════════════════════════════════════════════════

def analyze_ckm():
    """Check if CKM mixing matrix elements relate to n=6 constants."""
    print()
    print("=" * 72)
    print("SECTION 4: CKM MATRIX AND n=6 RELATIONS")
    print("=" * 72)
    print()

    # CKM matrix
    ckm = {
        'V_ud': V_UD, 'V_us': V_US, 'V_ub': V_UB,
        'V_cd': V_CD, 'V_cs': V_CS, 'V_cb': V_CB,
        'V_td': V_TD, 'V_ts': V_TS, 'V_tb': V_TB,
    }

    print("  CKM Matrix Elements vs n=6 Arithmetic:")
    print()
    print(f"  {'Element':<8s} {'Value':>10s} {'Best n=6':>20s} {'Target':>10s} {'Error':>10s}")
    print(f"  {'-'*8} {'-'*10} {'-'*20} {'-'*10} {'-'*10}")

    for name, val in ckm.items():
        match = find_n6_match(val)
        flag = " ***" if match and match[2] < 0.01 else ""
        if match:
            print(f"  {name:<8s} {val:10.6f} {match[0]:>20s} {match[1]:10.6f} {match[2]*100:9.4f}%{flag}")

    # Cabibbo angle
    print()
    print("  Cabibbo Angle Analysis:")
    theta_c = CABIBBO_ANGLE_RAD
    print(f"  theta_c = {CABIBBO_ANGLE_DEG:.2f} deg = {theta_c:.6f} rad")

    # Test various expressions
    tests = [
        ("sin(theta_c)", math.sin(theta_c)),
        ("cos(theta_c)", math.cos(theta_c)),
        ("tan(theta_c)", math.tan(theta_c)),
        ("theta_c/pi", theta_c / math.pi),
        ("theta_c", theta_c),
        ("sin^2(theta_c)", math.sin(theta_c)**2),
        ("1-cos(theta_c)", 1 - math.cos(theta_c)),
        ("sin(2*theta_c)", math.sin(2 * theta_c)),
        ("theta_c * sigma", theta_c * SIGMA),
        ("theta_c * P1", theta_c * P1),
        ("theta_c * tau", theta_c * TAU),
        ("sin(theta_c)*sigma", math.sin(theta_c) * SIGMA),
        ("sin(theta_c)*P1", math.sin(theta_c) * P1),
        ("V_us/V_ud", V_US / V_UD),
        ("V_us^2", V_US**2),
        ("V_cb/V_us", V_CB / V_US),
        ("V_ub/V_cb", V_UB / V_CB),
        ("V_td/V_ts", V_TD / V_TS),
        ("V_us*V_cb", V_US * V_CB),
        ("V_us*V_cb/V_ub", V_US * V_CB / V_UB),
    ]

    print()
    print(f"  {'Expression':<22s} {'Value':>10s} {'Best n=6':>20s} {'Error':>10s}")
    print(f"  {'-'*22} {'-'*10} {'-'*20} {'-'*10}")

    for expr, val in tests:
        match = find_n6_match(val)
        flag = " ***" if match and match[2] < 0.01 else ""
        if match:
            print(f"  {expr:<22s} {val:10.6f} {match[0]:>20s} {match[2]*100:9.4f}%{flag}")

    # Wolfenstein parameters
    print()
    print("  Wolfenstein Parameters:")
    lam = V_US  # lambda ~ V_us
    A_w = V_CB / lam**2  # A
    print(f"  lambda = {lam:.4f}")
    print(f"  A      = {A_w:.4f}")

    match_lam = find_n6_match(lam)
    match_A = find_n6_match(A_w)
    if match_lam:
        flag = " ***" if match_lam[2] < 0.01 else ""
        print(f"  lambda ~ {match_lam[0]} (err={match_lam[2]*100:.4f}%){flag}")
    if match_A:
        flag = " ***" if match_A[2] < 0.01 else ""
        print(f"  A      ~ {match_A[0]} (err={match_A[2]*100:.4f}%){flag}")

    # Jarlskog invariant
    J = 3.08e-5  # PDG value
    print()
    print(f"  Jarlskog invariant J = {J:.2e}")
    match_J = find_n6_match(J)
    # Try J * n6 constants
    for name, mult in [('sigma^4', SIGMA**4), ('P1^6', P1**6),
                        ('sigma^3*P1', SIGMA**3*P1), ('P1^5', P1**5)]:
        val = J * mult
        match = find_n6_match(val)
        if match and match[2] < 0.05:
            flag = " ***" if match[2] < 0.01 else ""
            print(f"  J * {name} = {val:.6f} ~ {match[0]} (err={match[2]*100:.4f}%){flag}")


# ═══════════════════════════════════════════════════════════════
# Section 5: Direct n=6 Mass Formulas
# ═══════════════════════════════════════════════════════════════

def check_direct_formulas():
    """Verify the ad hoc n=6 quark mass formulas from H-PH-9."""
    print()
    print("=" * 72)
    print("SECTION 5: DIRECT n=6 MASS FORMULAS (H-PH-9 Section 9)")
    print("=" * 72)
    print()
    print("  Checking existing predictions vs PDG 2024 masses:")
    print()

    formulas = [
        ("u", "phi = 2", PHI, MU),
        ("d", "tau(14/3) = 14/3", 14/3, MD),
        ("s", "sigma*(sigma-tau) = 12*8 = 96", SIGMA * (SIGMA - TAU), MS),
        ("c", "sigma^2*(sigma-tau+R) = 144*9 = 1296", SIGMA**2 * (SIGMA - TAU + R), MC),
        ("b", "phi^sigma = 2^12 = 4096", PHI**SIGMA, MB),
        ("t", "sigma^3*(sigma^2-sigma*tau+tau) = 172800",
         SIGMA**3 * (SIGMA**2 - SIGMA*TAU + TAU), MT),
    ]

    print(f"  {'Quark':<6s} {'Formula':<40s} {'Pred':>10s} {'PDG':>10s} {'Error':>8s}")
    print(f"  {'-'*6} {'-'*40} {'-'*10} {'-'*10} {'-'*8}")

    for quark, formula, pred, pdg in formulas:
        err = abs(pred - pdg) / pdg * 100
        flag = " ***" if err < 1 else ""
        print(f"  {quark:<6s} {formula:<40s} {pred:10.1f} {pdg:10.1f} {err:7.2f}%{flag}")

    # Check for unified pattern
    print()
    print("  Pattern analysis:")
    print("  u = phi                    = 2^1")
    print("  d = 14/3                   ~ tau + phi/3")
    print("  s = sigma*(sigma-tau)      = 12*8 = 96")
    print("  c = sigma^2*(sigma-tau+R)  = 144*9 = 1296")
    print("  b = phi^sigma              = 2^12 = 4096")
    print("  t = sigma^3*(sig^2-sig*tau+tau) = 1728*100 = 172800")
    print()

    # Look for sigma-power pattern
    print("  Log-sigma pattern:")
    for quark, _, _, pdg in formulas:
        ls = math.log(pdg) / math.log(SIGMA)
        match = find_n6_match(ls)
        flag = " ***" if match and match[2] < 0.01 else ""
        err_str = f"{match[2]*100:.4f}%" if match else "N/A"
        match_str = match[0] if match else "N/A"
        print(f"    log_12({quark}) = {ls:.4f} ~ {match_str} (err={err_str}){flag}")

    # Mass ratios between generations
    print()
    print("  Inter-generation mass ratios:")
    gen_ratios = [
        ("mc/mu", MC/MU, "charm/up"),
        ("mt/mc", MT/MC, "top/charm"),
        ("ms/md", MS/MD, "strange/down"),
        ("mb/ms", MB/MS, "bottom/strange"),
        ("mt/mu", MT/MU, "top/up"),
        ("mb/md", MB/MD, "bottom/down"),
    ]
    print(f"  {'Ratio':<10s} {'Value':>12s} {'Best n=6':>20s} {'Error':>10s}")
    print(f"  {'-'*10} {'-'*12} {'-'*20} {'-'*10}")
    for name, val, desc in gen_ratios:
        match = find_n6_match(val)
        # also try log
        lv = math.log(val)
        match_l = find_n6_match(lv)
        if match and match[2] < 0.05:
            flag = " ***" if match[2] < 0.01 else ""
            print(f"  {name:<10s} {val:12.2f} {match[0]:>20s} {match[2]*100:9.4f}%{flag}")
        if match_l and match_l[2] < 0.05:
            flag = " ***" if match_l[2] < 0.01 else ""
            print(f"  ln({name}){'':<4s} {lv:12.4f} {match_l[0]:>20s} {match_l[2]*100:9.4f}%{flag}")


# ═══════════════════════════════════════════════════════════════
# Section 6: Systematic Quark Mass Formula Search
# ═══════════════════════════════════════════════════════════════

def systematic_formula_search():
    """Brute-force search for mass = f(sigma, tau, phi, P1, sopfr) formulas."""
    print()
    print("=" * 72)
    print("SECTION 6: SYSTEMATIC n=6 FORMULA SEARCH FOR QUARK MASSES")
    print("=" * 72)
    print()
    print("  Searching: m = sigma^a * tau^b * phi^c * P1^d * sopfr^e")
    print("  with a,b,c,d,e in {-3,-2,-1,0,1,2,3}")
    print()

    quarks = [('u', MU), ('d', MD), ('s', MS), ('c', MC), ('b', MB), ('t', MT)]
    consts = [('sig', SIGMA), ('tau', TAU), ('phi', PHI), ('P1', P1), ('sop', SOPFR)]

    for qname, qmass in quarks:
        hits = []
        # Search over exponent combinations
        for a in range(-3, 4):
            for b in range(-3, 4):
                for c in range(-3, 4):
                    for d in range(-3, 4):
                        # Skip trivial (all zero)
                        if a == 0 and b == 0 and c == 0 and d == 0:
                            continue
                        try:
                            val = (SIGMA**a) * (TAU**b) * (PHI**c) * (P1**d)
                            if val <= 0:
                                continue
                            err = abs(val - qmass) / qmass
                            if err < 0.05:
                                terms = []
                                for exp, nm in [(a,'sig'), (b,'tau'), (c,'phi'), (d,'P1')]:
                                    if exp != 0:
                                        if exp == 1:
                                            terms.append(nm)
                                        else:
                                            terms.append(f"{nm}^{exp}")
                                formula = "*".join(terms) if terms else "1"
                                hits.append((formula, val, err))
                        except (OverflowError, ZeroDivisionError):
                            continue

        # Also include sopfr combinations (limited to keep runtime down)
        for a in range(-2, 3):
            for b in range(-2, 3):
                for e in range(-2, 3):
                    if a == 0 and b == 0 and e == 0:
                        continue
                    try:
                        val = (SIGMA**a) * (TAU**b) * (SOPFR**e)
                        if val <= 0:
                            continue
                        err = abs(val - qmass) / qmass
                        if err < 0.05:
                            terms = []
                            for exp, nm in [(a,'sig'), (b,'tau'), (e,'sop')]:
                                if exp != 0:
                                    if exp == 1:
                                        terms.append(nm)
                                    else:
                                        terms.append(f"{nm}^{exp}")
                            formula = "*".join(terms)
                            hits.append((formula, val, err))
                    except (OverflowError, ZeroDivisionError):
                        continue

        hits.sort(key=lambda x: x[2])
        # Deduplicate by value
        seen_vals = set()
        unique_hits = []
        for h in hits:
            rounded = round(h[1], 6)
            if rounded not in seen_vals:
                seen_vals.add(rounded)
                unique_hits.append(h)

        print(f"  {qname} (PDG = {qmass} MeV):")
        if unique_hits:
            for formula, val, err in unique_hits[:5]:
                flag = " ***" if err < 0.01 else ""
                print(f"    {formula:<30s} = {val:12.2f}  err={err*100:.4f}%{flag}")
        else:
            print(f"    No exact matches within 5%")
        print()

    # Also search for polynomial combinations: a*sigma + b*tau + c*phi + ...
    print("  --- Additive combinations: m = a*sigma + b*tau + c*phi + d*P1 ---")
    print()
    for qname, qmass in quarks:
        hits = []
        for a in range(-20, 21):
            for b in range(-20, 21):
                for c in range(-20, 21):
                    val = a * SIGMA + b * TAU + c * PHI
                    if val <= 0:
                        continue
                    err = abs(val - qmass) / qmass
                    if err < 0.005:
                        terms = []
                        for coeff, nm in [(a, 'sig'), (b, 'tau'), (c, 'phi')]:
                            if coeff != 0:
                                if coeff == 1:
                                    terms.append(nm)
                                elif coeff == -1:
                                    terms.append(f"-{nm}")
                                else:
                                    terms.append(f"{coeff}*{nm}")
                        formula = "+".join(terms).replace("+-", "-")
                        hits.append((formula, val, err))

        hits.sort(key=lambda x: x[2])
        if hits:
            for formula, val, err in hits[:3]:
                flag = " ***" if err < 0.001 else ""
                print(f"  {qname}: {formula:<35s} = {val:10.2f}  err={err*100:.4f}%{flag}")
        # Only show for quarks where additive works
    print()


# ═══════════════════════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════════════════════

def print_summary():
    """Print summary of all significant findings."""
    print()
    print("=" * 72)
    print("SUMMARY: ALL FINDINGS WITH ERROR < 1%")
    print("=" * 72)
    print()
    print("  Significance threshold: error < 1% flagged with ***")
    print("  Strongest findings listed first.")
    print()
    print("  Note: With many targets tested, some matches may be coincidental.")
    print("  Texas Sharpshooter correction needed for rigorous claims.")
    print("  Number of target values tested: ~", len(N6_TARGETS))
    print()


# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Quark Koide Search with n=6 arithmetic")
    parser.add_argument('--extended', action='store_true', help='Extended alpha/beta search')
    parser.add_argument('--ckm', action='store_true', help='CKM analysis only')
    parser.add_argument('--verbose', action='store_true', help='Show all attempts')
    args = parser.parse_args()

    print()
    print("  QUARK KOIDE SEARCH — Perfect Number 6 Parametrization")
    print("  " + "=" * 56)
    print(f"  n=6 constants: sigma={SIGMA}, tau={TAU}, phi={PHI}, P1={P1}, sopfr={SOPFR}")
    print(f"  PDG 2024 masses (MeV): u={MU}, d={MD}, s={MS}, c={MC}, b={MB}, t={MT}")
    print()

    if args.ckm:
        analyze_ckm()
        return

    # Run all sections
    test_standard_koide()
    search_koide_angles()
    search_extended_koide(verbose=args.verbose)
    analyze_ckm()
    check_direct_formulas()
    systematic_formula_search()
    print_summary()


if __name__ == '__main__':
    main()
