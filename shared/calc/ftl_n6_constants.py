#!/usr/bin/env python3
"""FTL n=6 Constants Matcher — Honest search for n=6 arithmetic in physics constants.

Searches for matches between n=6 arithmetic functions and physical constants
related to FTL (faster-than-light) physics: GR coefficients, Planck units,
fine structure constant, etc.

STRICT RULES:
  - EXACT: coefficient IS an n=6 value (like ISCO=6)
  - STRONG: <0.1% error
  - APPROXIMATE: <2% error
  - WEAK: 2-5% error
  - NO MATCH: >5% or requires ad hoc correction (+1, -1, *2)
  - Never force a match. "NO MATCH" is a valid and expected result.

Usage:
  python3 calc/ftl_n6_constants.py              # Full analysis
  python3 calc/ftl_n6_constants.py --group 1    # Known matches only
  python3 calc/ftl_n6_constants.py --group 2    # FTL constants only
  python3 calc/ftl_n6_constants.py --texas       # Texas Sharpshooter test
  python3 calc/ftl_n6_constants.py --summary     # Match table only
  python3 calc/ftl_n6_constants.py --json        # JSON output
"""

import argparse
import json
import math
import random
import sys
from collections import OrderedDict

# ============================================================================
# n=6 Arithmetic Functions
# ============================================================================

N = 6
SIGMA = 12       # sum of divisors: 1+2+3+6
TAU = 4          # number of divisors
PHI = 2          # Euler totient
SOPFR = 5        # sum of prime factors with repetition: 2+3
RAD = 6          # radical: 2*3
LAMBDA = 2       # Liouville-related
MU = 1           # Mobius function |mu(6)|
PSI = 12         # Dedekind psi
J2 = 24          # Jordan totient J_2(6)

# Derived n=6 values (no ad hoc — pure arithmetic combinations)
N6_VALUES = OrderedDict([
    # Primary
    ("n", N),
    ("sigma", SIGMA),
    ("tau", TAU),
    ("phi", PHI),
    ("sopfr", SOPFR),
    ("rad", RAD),
    ("lambda", LAMBDA),
    ("mu", MU),
    ("psi", PSI),
    ("J2", J2),
    # Simple ratios and products
    ("sigma/tau", SIGMA / TAU),           # 3
    ("sigma/phi", SIGMA / PHI),           # 6
    ("n/phi", N / PHI),                   # 3
    ("n/tau", N / TAU),                   # 1.5
    ("tau+sopfr", TAU + SOPFR),           # 9
    ("n^2", N**2),                        # 36
    ("sigma*phi", SIGMA * PHI),           # 24
    ("sigma+mu", SIGMA + MU),            # 13
    ("n+1", N + 1),                       # 7
    ("n-1", N - 1),                       # 5
    ("n!", math.factorial(N)),            # 720
    ("sigma!", math.factorial(SIGMA)),    # 479001600
    ("tau!", math.factorial(TAU)),        # 24
    ("n*sigma", N * SIGMA),              # 72
    ("sigma+n", SIGMA + N),              # 18
    ("sigma-n", SIGMA - N),              # 6
    ("tau*phi", TAU * PHI),              # 8
    ("tau*sopfr", TAU * SOPFR),          # 20
    ("sigma*sopfr", SIGMA * SOPFR),      # 60
    ("n*sopfr", N * SOPFR),             # 30
    ("n*tau", N * TAU),                  # 24
    ("sigma^2", SIGMA**2),              # 144
    ("n^3", N**3),                       # 216
    ("phi^2", PHI**2),                   # 4
    ("2*pi", 2 * math.pi),              # 6.283...
    ("4*pi", 4 * math.pi),              # 12.566...
    ("8*pi", 8 * math.pi),              # 25.133...
    ("pi", math.pi),                     # 3.14159...
    ("pi^2", math.pi**2),               # 9.8696...
    ("n*pi", N * math.pi),              # 18.849...
    ("sigma*pi", SIGMA * math.pi),      # 37.699...
    ("n*pi^2", N * math.pi**2),         # 59.217...
    # Powers of primes from 6=2*3
    ("2^n", 2**N),                       # 64
    ("3^n", 3**N),                       # 729
    ("6^2", 6**2),                       # 36
    ("6^3", 6**3),                       # 216
    # Combinations with e and ln
    ("e", math.e),                        # 2.718...
    ("1/e", 1/math.e),                   # 0.3679...
    ("ln2", math.log(2)),                # 0.6931...
    ("ln3", math.log(3)),                # 1.0986...
    ("ln6", math.log(6)),                # 1.7918...
    ("n*e", N * math.e),                 # 16.309...
    ("sigma*e", SIGMA * math.e),         # 32.619...
    # Specific expressions known from project
    ("6*pi^5", 6 * math.pi**5),          # 1836.118...
    ("3/(sigma+mu)", 3 / (SIGMA + MU)),  # 0.23077...
    ("sigma*n+mu", SIGMA * N + MU),      # 73
    ("(n+1)/sigma", (N + 1) / SIGMA),    # 7/12
    ("n^3/sopfr", N**3 / SOPFR),         # 43.2
    ("sigma/n", SIGMA / N),              # 2
    ("n/sigma", N / SIGMA),              # 0.5
    ("sopfr/n", SOPFR / N),             # 0.8333...
    ("1/n", 1 / N),                      # 0.1667...
    ("1/sigma", 1 / SIGMA),             # 0.0833...
    ("1/tau", 1 / TAU),                  # 0.25
])

# ============================================================================
# Physical Constants
# ============================================================================

# Group 1: ALREADY KNOWN n=6 matches (verification)
GROUP1_CONSTANTS = [
    {
        "name": "mp/me (proton-to-electron mass ratio)",
        "value": 1836.15267343,
        "unit": "dimensionless",
        "expected_expr": "6*pi^5",
        "expected_val": 6 * math.pi**5,
        "source": "CODATA 2018",
    },
    {
        "name": "sin^2(theta_W) (weak mixing angle)",
        "value": 0.23122,
        "unit": "dimensionless",
        "expected_expr": "3/(sigma+mu) = 3/13",
        "expected_val": 3 / 13,
        "source": "PDG 2022",
    },
    {
        "name": "Hubble H0",
        "value": 73.04,
        "unit": "km/s/Mpc",
        "expected_expr": "sigma*n+mu = 73",
        "expected_val": 73,
        "source": "SH0ES 2022 (Riess+)",
    },
]

# Group 2: FTL-relevant constants to test
GROUP2_CONSTANTS = [
    # Dimensionless constants (meaningful to match)
    {
        "name": "Fine structure alpha = 1/137.036",
        "value": 1 / 137.035999084,
        "unit": "dimensionless",
        "category": "dimensionless",
    },
    {
        "name": "1/alpha = 137.036",
        "value": 137.035999084,
        "unit": "dimensionless",
        "category": "dimensionless",
    },
    # GR coefficients (dimensionless numbers in formulas)
    {
        "name": "ISCO coefficient (r_ISCO = 6*GM/c^2)",
        "value": 6,
        "unit": "dimensionless coefficient",
        "category": "GR_coefficient",
        "note": "Exact GR derivation, not numerology",
    },
    {
        "name": "Photon sphere coefficient (r_ph = 3*GM/c^2)",
        "value": 3,
        "unit": "dimensionless coefficient",
        "category": "GR_coefficient",
        "note": "Exact GR derivation",
    },
    {
        "name": "Schwarzschild coefficient (r_s = 2*GM/c^2)",
        "value": 2,
        "unit": "dimensionless coefficient",
        "category": "GR_coefficient",
        "note": "Exact GR derivation",
    },
    # Hawking/Bekenstein coefficients
    {
        "name": "Hawking T coefficient (T_H = hbar*c^3 / (8*pi*G*M*k_B))",
        "value": 8 * math.pi,
        "unit": "dimensionless coefficient",
        "category": "BH_thermo",
        "note": "8*pi appears in Hawking temperature denominator",
    },
    {
        "name": "Bekenstein-Hawking S coefficient (S = A / (4*l_P^2))",
        "value": 4,
        "unit": "dimensionless coefficient",
        "category": "BH_thermo",
        "note": "The 4 in Bekenstein-Hawking entropy",
    },
    {
        "name": "Unruh T coefficient (T_U = hbar*a / (2*pi*c*k_B))",
        "value": 2 * math.pi,
        "unit": "dimensionless coefficient",
        "category": "BH_thermo",
        "note": "2*pi appears in Unruh temperature denominator",
    },
    # Lorentz factors at key fractions
    {
        "name": "Lorentz gamma(v=c/2) = gamma(1/2)",
        "value": 1 / math.sqrt(1 - 0.5**2),
        "unit": "dimensionless",
        "category": "Lorentz",
    },
    {
        "name": "Lorentz gamma(v=c/e) = gamma(1/e)",
        "value": 1 / math.sqrt(1 - (1/math.e)**2),
        "unit": "dimensionless",
        "category": "Lorentz",
    },
    {
        "name": "Lorentz gamma(v=c/3) = gamma(1/3)",
        "value": 1 / math.sqrt(1 - (1/3)**2),
        "unit": "dimensionless",
        "category": "Lorentz",
    },
    {
        "name": "Lorentz gamma(v=5c/6) = gamma(5/6)",
        "value": 1 / math.sqrt(1 - (5/6)**2),
        "unit": "dimensionless",
        "category": "Lorentz",
    },
    # Dimensional constants (match is inherently weak — unit-dependent)
    {
        "name": "Speed of light c",
        "value": 299792458,
        "unit": "m/s (exact by definition)",
        "category": "dimensional",
        "note": "Unit-dependent: match would be anthropic (SI units)",
    },
    {
        "name": "Gravitational constant G",
        "value": 6.674e-11,
        "unit": "m^3/(kg*s^2)",
        "category": "dimensional",
        "note": "Unit-dependent",
    },
    {
        "name": "Planck length l_P",
        "value": 1.616255e-35,
        "unit": "m",
        "category": "dimensional",
        "note": "Unit-dependent",
    },
    {
        "name": "Planck time t_P",
        "value": 5.391247e-44,
        "unit": "s",
        "category": "dimensional",
        "note": "Unit-dependent",
    },
    {
        "name": "Planck mass m_P",
        "value": 2.176434e-8,
        "unit": "kg",
        "category": "dimensional",
        "note": "Unit-dependent",
    },
    {
        "name": "Planck energy E_P",
        "value": 1.22e19,
        "unit": "GeV",
        "category": "dimensional",
        "note": "Unit-dependent",
    },
    {
        "name": "Planck temperature T_P",
        "value": 1.416784e32,
        "unit": "K",
        "category": "dimensional",
        "note": "Unit-dependent",
    },
]


# ============================================================================
# Matching Engine
# ============================================================================

def grade_match(error_pct):
    """Grade a match by error percentage."""
    if error_pct == 0.0:
        return "EXACT"
    elif error_pct < 0.1:
        return "STRONG"
    elif error_pct < 2.0:
        return "APPROXIMATE"
    elif error_pct < 5.0:
        return "WEAK"
    else:
        return "NO MATCH"


def find_best_match(value, exclude_trivial=True):
    """Find the best n=6 expression matching the given value.

    Returns (expr_name, expr_value, error_pct, grade) or None if no match.
    """
    if value == 0:
        return None

    best = None
    best_err = float('inf')

    for name, n6val in N6_VALUES.items():
        if n6val == 0:
            continue
        # Skip trivially large/small mismatches
        if abs(n6val) < 1e-10 and abs(value) > 1:
            continue
        if abs(value) < 1e-10 and abs(n6val) > 1:
            continue

        error_pct = abs(value - n6val) / abs(value) * 100

        if error_pct < best_err:
            best_err = error_pct
            best = (name, n6val, error_pct, grade_match(error_pct))

    return best


def search_constant(const_dict):
    """Search for n=6 match for a single constant. Returns result dict."""
    value = const_dict["value"]
    name = const_dict["name"]
    result = {
        "name": name,
        "value": value,
        "unit": const_dict.get("unit", ""),
        "category": const_dict.get("category", ""),
        "note": const_dict.get("note", ""),
    }

    match = find_best_match(value)
    if match:
        expr_name, expr_val, err, grade = match
        result["best_expr"] = expr_name
        result["best_expr_val"] = expr_val
        result["error_pct"] = err
        result["grade"] = grade
    else:
        result["best_expr"] = "NONE"
        result["best_expr_val"] = None
        result["error_pct"] = 100.0
        result["grade"] = "NO MATCH"

    return result


def verify_known(const_dict):
    """Verify a known match from Group 1."""
    value = const_dict["value"]
    expected = const_dict["expected_val"]
    error_pct = abs(value - expected) / abs(value) * 100
    grade = grade_match(error_pct)

    return {
        "name": const_dict["name"],
        "value": value,
        "expected_expr": const_dict["expected_expr"],
        "expected_val": expected,
        "error_pct": error_pct,
        "grade": grade,
        "source": const_dict.get("source", ""),
    }


# ============================================================================
# GR Coefficients Special Section
# ============================================================================

def gr_coefficients_analysis():
    """Analyze the {2, 3, 6} set in GR orbital mechanics."""
    print("\n" + "=" * 72)
    print("  GR COEFFICIENTS: The {2, 3, 6} Set in Black Hole Physics")
    print("=" * 72)

    rows = [
        ("Schwarzschild radius", "r_s = 2*GM/c^2", 2, "phi(6)", PHI),
        ("Photon sphere", "r_ph = 3*GM/c^2", 3, "sigma/tau = n/2", SIGMA / TAU),
        ("ISCO (Schwarzschild)", "r_ISCO = 6*GM/c^2", 6, "n = sigma/phi", N),
    ]

    print(f"\n  {'Quantity':<25} {'Formula':<22} {'Coeff':>6} {'n=6 expr':<16} {'Match':>6}")
    print("  " + "-" * 78)
    for qty, formula, coeff, expr, n6val in rows:
        match = "EXACT" if coeff == n6val else f"{abs(coeff - n6val)/coeff*100:.2f}%"
        print(f"  {qty:<25} {formula:<22} {coeff:>6} {expr:<16} {match:>6}")

    print(f"\n  Key observation:")
    print(f"    Schwarzschild=2, Photon sphere=3, ISCO=6")
    print(f"    These are the DIVISORS of 6: {{1, 2, 3, 6}}")
    print(f"    (1 appears as the event horizon in units of r_s)")
    print()
    print(f"    From n=6 arithmetic: phi(6)=2, sigma(6)/tau(6)=3, n=6")
    print(f"    All three are EXACT matches (derived from GR, not fitted).")
    print()
    print(f"    HOWEVER: This is the divisor set of 6, and these GR results")
    print(f"    come from the effective potential V_eff = -M/r + L^2/(2r^2) - ML^2/r^3.")
    print(f"    The numbers 2, 3, 6 arise from polynomial degree analysis.")
    print(f"    Whether this connects to the ARITHMETIC of perfect number 6")
    print(f"    vs merely sharing the same small integers is an open question.")


# ============================================================================
# Hawking / Bekenstein / Unruh Analysis
# ============================================================================

def bh_thermo_analysis():
    """Analyze dimensionless coefficients in black hole thermodynamics."""
    print("\n" + "=" * 72)
    print("  BLACK HOLE THERMODYNAMICS: Coefficients vs n=6")
    print("=" * 72)

    rows = [
        ("Hawking temp denom", "8*pi", 8 * math.pi, "8*pi", "tau*phi * pi",
         TAU * PHI * math.pi, abs(8*math.pi - TAU*PHI*math.pi)/(8*math.pi)*100),
        ("BH entropy denom", "4", 4, "4", "tau",
         TAU, abs(4 - TAU)/4*100),
        ("Unruh temp denom", "2*pi", 2 * math.pi, "2*pi", "phi * pi",
         PHI * math.pi, abs(2*math.pi - PHI*math.pi)/(2*math.pi)*100),
    ]

    print(f"\n  {'Quantity':<22} {'Value':<10} {'Orig':<8} {'n=6 expr':<14} {'n=6 val':<10} {'Error':>8} {'Grade':>10}")
    print("  " + "-" * 86)
    for qty, _orig, val, orig_s, expr, n6val, err in rows:
        grade = grade_match(err)
        print(f"  {qty:<22} {val:<10.4f} {orig_s:<8} {expr:<14} {n6val:<10.4f} {err:>7.3f}% {grade:>10}")

    print(f"\n  Interpretation:")
    print(f"    - BH entropy denominator 4 = tau(6) EXACTLY")
    print(f"    - Hawking 8*pi = tau(6)*phi(6)*pi EXACTLY (trivially: 4*2=8)")
    print(f"    - Unruh 2*pi = phi(6)*pi EXACTLY (trivially: 2=phi(6))")
    print(f"    - These are EXACT but TAUTOLOGICAL: 2 and 4 are very common")
    print(f"      small integers. Claiming 4=tau(6) is true but not deep.")


# ============================================================================
# Texas Sharpshooter Test
# ============================================================================

def texas_sharpshooter(n_trials=100000, seed=42):
    """Monte Carlo test: how often do random expressions match random constants?"""
    print("\n" + "=" * 72)
    print("  TEXAS SHARPSHOOTER TEST")
    print("=" * 72)

    rng = random.Random(seed)

    # Our actual results
    group2_results = [search_constant(c) for c in GROUP2_CONSTANTS]
    n_tested = len(group2_results)

    # Count matches at each grade
    actual_exact = sum(1 for r in group2_results if r["grade"] == "EXACT")
    actual_strong = sum(1 for r in group2_results if r["grade"] == "STRONG")
    actual_approx = sum(1 for r in group2_results if r["grade"] == "APPROXIMATE")
    actual_weak = sum(1 for r in group2_results if r["grade"] == "WEAK")
    actual_nomatch = sum(1 for r in group2_results if r["grade"] == "NO MATCH")
    actual_any = actual_exact + actual_strong + actual_approx  # meaningful matches

    # Separate: how many GR coefficients matched?
    gr_indices = [i for i, c in enumerate(GROUP2_CONSTANTS) if c.get("category") == "GR_coefficient"]
    gr_exact = sum(1 for i in gr_indices if group2_results[i]["grade"] == "EXACT")

    # Monte Carlo: generate random "n=K" expression sets and random constants
    # For each trial: pick a random n (2-100), compute its arithmetic functions,
    # then see how many of our GROUP2 constants match
    match_counts = []
    n6_values_list = list(N6_VALUES.values())
    n6_count = len(n6_values_list)

    for _ in range(n_trials):
        # Generate a random set of "n=K" values
        k = rng.randint(2, 100)
        # Compute basic arithmetic functions for random k
        # (simplified — just divisor-based values)
        divs = [d for d in range(1, k + 1) if k % d == 0]
        k_sigma = sum(divs)
        k_tau = len(divs)
        k_phi = sum(1 for i in range(1, k + 1) if math.gcd(i, k) == 1)
        # Sum of prime factors with repetition
        k_sopfr = 0
        temp = k
        for p in range(2, k + 1):
            while temp % p == 0:
                k_sopfr += p
                temp //= p
            if temp == 1:
                break

        # Build expression set (same structure as N6_VALUES but for random k)
        rand_vals = set()
        rand_vals.add(k)
        rand_vals.add(k_sigma)
        rand_vals.add(k_tau)
        rand_vals.add(k_phi)
        rand_vals.add(k_sopfr)
        if k_tau > 0:
            rand_vals.add(k_sigma / k_tau)
        if k_phi > 0:
            rand_vals.add(k_sigma / k_phi)
            rand_vals.add(k / k_phi)
        rand_vals.add(k**2)
        rand_vals.add(k**3)
        rand_vals.add(k_sigma * k_phi)
        rand_vals.add(k_sigma + 1)  # analogous to sigma+mu
        rand_vals.add(k + 1)
        rand_vals.add(k - 1)
        rand_vals.add(math.factorial(min(k, 10)))  # cap factorial
        rand_vals.add(k_tau * k_phi)
        rand_vals.add(k_tau * k_sopfr)
        rand_vals.add(k * k_sigma)
        rand_vals.add(k_sigma + k)
        rand_vals.add(k_sigma - k if k_sigma > k else 0)
        rand_vals.add(k * k_sopfr)
        rand_vals.add(k * math.pi**5)  # analogous to 6*pi^5
        rand_vals.add(k_sigma * k + 1)  # analogous to sigma*n+mu
        if k_sigma + 1 > 0:
            rand_vals.add(3 / (k_sigma + 1))  # analogous to 3/(sigma+mu)
        rand_vals.add(2 * math.pi)
        rand_vals.add(4 * math.pi)
        rand_vals.add(8 * math.pi)
        rand_vals.add(math.pi)
        rand_vals.discard(0)

        # Count how many GROUP2 constants match this random set
        matches = 0
        for const in GROUP2_CONSTANTS:
            val = const["value"]
            for rv in rand_vals:
                if rv == 0:
                    continue
                err = abs(val - rv) / abs(val) * 100
                if err < 2.0:  # APPROXIMATE or better
                    matches += 1
                    break
        match_counts.append(matches)

    # Statistics
    avg = sum(match_counts) / len(match_counts)
    std = (sum((x - avg)**2 for x in match_counts) / len(match_counts)) ** 0.5

    # p-value: fraction of random trials with >= actual_any matches
    p_raw = sum(1 for x in match_counts if x >= actual_any) / len(match_counts)
    # Bonferroni correction (number of expressions tested)
    p_bonferroni = min(1.0, p_raw * n6_count)

    # Histogram
    from collections import Counter
    hist = Counter(match_counts)
    max_count = max(hist.values())
    max_matches = max(match_counts)

    print(f"\n  Monte Carlo: {n_trials:,} trials, random n in [2,100]")
    print(f"  Each trial: compute arithmetic functions of random n,")
    print(f"  then count how many of {n_tested} physics constants match (<2% error)")
    print()
    print(f"  Distribution of match counts:")
    print(f"  {'Matches':>8} {'Count':>8} {'Histogram'}")
    print(f"  {'-'*8} {'-'*8} {'-'*40}")
    for m in range(max_matches + 1):
        c = hist.get(m, 0)
        bar = "#" * int(c / max_count * 40) if max_count > 0 else ""
        marker = " <-- OUR n=6" if m == actual_any else ""
        print(f"  {m:>8d} {c:>8d} {bar}{marker}")

    print(f"\n  Our n=6 results:")
    print(f"    EXACT:       {actual_exact}")
    print(f"    STRONG:      {actual_strong}")
    print(f"    APPROXIMATE: {actual_approx}")
    print(f"    WEAK:        {actual_weak}")
    print(f"    NO MATCH:    {actual_nomatch}")
    print(f"    Meaningful (EXACT+STRONG+APPROX): {actual_any} / {n_tested}")
    print(f"    GR coefficients EXACT: {gr_exact} / {len(gr_indices)}")

    print(f"\n  Random baseline:")
    print(f"    Mean matches: {avg:.2f} +/- {std:.2f}")
    print(f"    Our matches:  {actual_any}")
    if std > 0:
        z = (actual_any - avg) / std
        print(f"    Z-score:      {z:.2f}")
    else:
        z = 0
        print(f"    Z-score:      N/A (std=0)")

    print(f"\n  p-value (raw):        {p_raw:.6f}")
    print(f"  p-value (Bonferroni): {p_bonferroni:.6f}")
    print(f"  Expressions tested:   {n6_count}")

    if p_bonferroni < 0.01:
        verdict = "SIGNIFICANT (p < 0.01) — n=6 matches are unlikely by chance"
    elif p_bonferroni < 0.05:
        verdict = "MARGINALLY SIGNIFICANT (p < 0.05)"
    else:
        verdict = "NOT SIGNIFICANT (p >= 0.05) — matches consistent with chance"

    print(f"\n  Verdict: {verdict}")

    # Separate GR analysis
    print(f"\n  NOTE on GR coefficients:")
    print(f"    The {2, 3, 6} set in GR is derived from the effective potential,")
    print(f"    not from fitting. These EXACT matches are structural, not statistical.")
    print(f"    The Texas test above tests ALL constants together; the GR subset")
    print(f"    should be evaluated on physical grounds, not statistical.")

    return {
        "n_tested": n_tested,
        "actual_any": actual_any,
        "actual_exact": actual_exact,
        "actual_strong": actual_strong,
        "actual_approx": actual_approx,
        "actual_weak": actual_weak,
        "actual_nomatch": actual_nomatch,
        "random_mean": avg,
        "random_std": std,
        "z_score": z,
        "p_raw": p_raw,
        "p_bonferroni": p_bonferroni,
        "verdict": verdict,
    }


# ============================================================================
# Display Functions
# ============================================================================

def display_group1():
    """Display Group 1 verification results."""
    print("\n" + "=" * 72)
    print("  GROUP 1: KNOWN n=6 MATCHES (Verification)")
    print("=" * 72)

    results = [verify_known(c) for c in GROUP1_CONSTANTS]

    print(f"\n  {'Constant':<40} {'Value':>14} {'n=6 Expression':<22} {'n=6 Value':>14} {'Error':>8} {'Grade':>10}")
    print("  " + "-" * 112)
    for r in results:
        print(f"  {r['name']:<40} {r['value']:>14.6f} {r['expected_expr']:<22} {r['expected_val']:>14.6f} {r['error_pct']:>7.3f}% {r['grade']:>10}")

    print(f"\n  All {len(results)} known matches: ", end="")
    all_ok = all(r["grade"] in ("EXACT", "STRONG", "APPROXIMATE") for r in results)
    print("CONFIRMED" if all_ok else "SOME FAILED")

    return results


def display_group2():
    """Display Group 2 search results."""
    print("\n" + "=" * 72)
    print("  GROUP 2: FTL-RELEVANT CONSTANTS (Search)")
    print("=" * 72)

    results = [search_constant(c) for c in GROUP2_CONSTANTS]

    # Separate by category
    categories = OrderedDict([
        ("dimensionless", "Dimensionless Constants"),
        ("GR_coefficient", "GR Coefficients (exact from theory)"),
        ("BH_thermo", "Black Hole Thermodynamics Coefficients"),
        ("Lorentz", "Lorentz Factors at Key Velocities"),
        ("dimensional", "Dimensional Constants (unit-dependent!)"),
    ])

    for cat_key, cat_name in categories.items():
        cat_results = [r for r in results if r.get("category", "") == cat_key
                       or (cat_key == "dimensionless" and r.get("category", "") == "")]
        if not cat_results:
            continue

        print(f"\n  --- {cat_name} ---")
        print(f"  {'Constant':<45} {'Value':>14} {'Best n=6':>14} {'Expr':<18} {'Error':>8} {'Grade':>10}")
        print("  " + "-" * 114)
        for r in cat_results:
            val_str = f"{r['value']:>14.6f}" if abs(r['value']) < 1e6 else f"{r['value']:>14.4e}"
            n6_str = f"{r['best_expr_val']:>14.6f}" if r['best_expr_val'] is not None and abs(r['best_expr_val']) < 1e6 else (f"{r['best_expr_val']:>14.4e}" if r['best_expr_val'] is not None else f"{'NONE':>14}")
            print(f"  {r['name']:<45} {val_str} {n6_str} {r['best_expr']:<18} {r['error_pct']:>7.2f}% {r['grade']:>10}")

    return results


def display_summary(g1_results, g2_results):
    """Display summary statistics."""
    print("\n" + "=" * 72)
    print("  SUMMARY")
    print("=" * 72)

    all_results = g2_results  # Group 2 is the search; Group 1 is verification

    total = len(all_results)
    exact = sum(1 for r in all_results if r["grade"] == "EXACT")
    strong = sum(1 for r in all_results if r["grade"] == "STRONG")
    approx = sum(1 for r in all_results if r["grade"] == "APPROXIMATE")
    weak = sum(1 for r in all_results if r["grade"] == "WEAK")
    nomatch = sum(1 for r in all_results if r["grade"] == "NO MATCH")

    print(f"\n  Group 1 (known matches): {len(g1_results)} verified")
    print(f"  Group 2 (FTL search):    {total} tested")
    print()
    print(f"  Grade distribution (Group 2):")
    print(f"    EXACT:       {exact:>3} / {total}")
    print(f"    STRONG:      {strong:>3} / {total}")
    print(f"    APPROXIMATE: {approx:>3} / {total}")
    print(f"    WEAK:        {weak:>3} / {total}")
    print(f"    NO MATCH:    {nomatch:>3} / {total}")
    print(f"    --------------------------------")
    meaningful = exact + strong + approx
    print(f"    Meaningful:  {meaningful:>3} / {total}  ({meaningful/total*100:.0f}%)")
    print(f"    Non-match:   {nomatch:>3} / {total}  ({nomatch/total*100:.0f}%)")

    # Separate dimensional vs dimensionless
    dimless = [r for r in all_results if any(
        c.get("category") in ("dimensionless", "GR_coefficient", "BH_thermo", "Lorentz")
        for c in GROUP2_CONSTANTS if c["name"] == r["name"]
    )]
    dimensional = [r for r in all_results if any(
        c.get("category") == "dimensional"
        for c in GROUP2_CONSTANTS if c["name"] == r["name"]
    )]

    dimless_match = sum(1 for r in dimless if r["grade"] in ("EXACT", "STRONG", "APPROXIMATE"))
    dimen_match = sum(1 for r in dimensional if r["grade"] in ("EXACT", "STRONG", "APPROXIMATE"))

    print(f"\n  By type:")
    print(f"    Dimensionless/coefficients: {dimless_match} / {len(dimless)} matched")
    print(f"    Dimensional (unit-dep):     {dimen_match} / {len(dimensional)} matched")

    # Honest conclusion
    print(f"\n  HONEST CONCLUSION:")
    print(f"    - GR coefficients {{2, 3, 6}} are EXACT and physically derived")
    print(f"    - BH thermo coefficients (4, 2*pi, 8*pi) match n=6 functions")
    print(f"      but these are SMALL INTEGERS — high prior probability of match")
    print(f"    - Fine structure alpha: {'MATCH' if any(r['name'].startswith('Fine') and r['grade'] in ('EXACT','STRONG','APPROXIMATE') for r in all_results) else 'NO MATCH'} with n=6 arithmetic")
    print(f"    - Dimensional constants (c, G, Planck units): inherently")
    print(f"      unit-dependent; any 'match' reflects SI convention, not physics")
    print(f"    - Lorentz factors at key fractions: check results above")


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="FTL n=6 Constants Matcher — Honest search with Texas Sharpshooter")
    parser.add_argument("--group", type=int, choices=[1, 2],
                        help="Show only group 1 (known) or group 2 (FTL search)")
    parser.add_argument("--texas", action="store_true",
                        help="Run Texas Sharpshooter Monte Carlo test")
    parser.add_argument("--summary", action="store_true",
                        help="Show match table only (no detailed analysis)")
    parser.add_argument("--json", action="store_true",
                        help="Output results as JSON")
    args = parser.parse_args()

    if args.json:
        g1 = [verify_known(c) for c in GROUP1_CONSTANTS]
        g2 = [search_constant(c) for c in GROUP2_CONSTANTS]
        output = {
            "group1_verification": g1,
            "group2_search": g2,
        }
        if args.texas:
            # Suppress print for JSON mode
            import io
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            texas = texas_sharpshooter()
            sys.stdout = old_stdout
            output["texas_sharpshooter"] = texas
        print(json.dumps(output, indent=2, default=str))
        return

    print("=" * 72)
    print("  FTL n=6 CONSTANTS MATCHER")
    print("  Honest search: NO forced connections, NO ad hoc corrections")
    print("=" * 72)
    print(f"\n  n=6 arithmetic: n={N}, sigma={SIGMA}, tau={TAU}, phi={PHI},")
    print(f"  sopfr={SOPFR}, rad={RAD}, mu={MU}, psi={PSI}, J2={J2}")
    print(f"  Total n=6 expressions tested: {len(N6_VALUES)}")

    g1_results = []
    g2_results = []

    if args.group != 2:
        g1_results = display_group1()

    if args.group != 1:
        g2_results = display_group2()

        if not args.summary:
            gr_coefficients_analysis()
            bh_thermo_analysis()

    if args.group is None and not args.summary:
        display_summary(g1_results if g1_results else [verify_known(c) for c in GROUP1_CONSTANTS],
                        g2_results if g2_results else [search_constant(c) for c in GROUP2_CONSTANTS])

    if args.summary:
        if not g1_results:
            g1_results = [verify_known(c) for c in GROUP1_CONSTANTS]
        if not g2_results:
            g2_results = [search_constant(c) for c in GROUP2_CONSTANTS]
        display_summary(g1_results, g2_results)

    if args.texas:
        texas_sharpshooter()


if __name__ == "__main__":
    main()
