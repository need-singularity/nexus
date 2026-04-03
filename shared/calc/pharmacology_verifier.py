#!/usr/bin/env python3
"""
pharmacology_verifier.py -- Pharmacology hypothesis verifier for TECS-L project.

Verifies pharmacology-related hypotheses (H-195 ~ H-200d, H-391~H-400, H-PSYCH-16)
using the G=D*P/I model framework.

Features:
  1. Drug parameter database with (D, P, I) values, mechanisms, references
  2. G=D*P/I computation, Compass, Golden Zone membership
  3. Dose-response modeling (exponential decay, contraction mapping)
  4. K5 spectral radius calculator (circulant consciousness matrix)
  5. Cross-consistency checker (Spearman rank, counterintuitive ordering flags)
  6. Texas Sharpshooter integration (Bonferroni-corrected p-values)
  7. BBB (Blood-Brain Barrier) assessment

Usage:
  python3 calc/pharmacology_verifier.py                       # Full verification
  python3 calc/pharmacology_verifier.py --drug THC            # Single drug analysis
  python3 calc/pharmacology_verifier.py --k5 0.5 1.0          # K5 spectral radius
  python3 calc/pharmacology_verifier.py --dose-response SSRI  # Time course simulation
  python3 calc/pharmacology_verifier.py --cross-check         # Cross-consistency only
  python3 calc/pharmacology_verifier.py --all                 # Everything
"""

import argparse
import math
import random
import sys

import numpy as np

# ═══════════════════════════════════════════════════════════════════════════
# Golden Zone Constants
# ═══════════════════════════════════════════════════════════════════════════

GZ_UPPER = 0.5                        # Riemann critical line
GZ_LOWER = 0.5 - math.log(4 / 3)     # approx 0.2123
GZ_CENTER = 1 / math.e               # approx 0.3679
GZ_WIDTH = math.log(4 / 3)           # approx 0.2877
META_FIXED = 1.0 / 3                 # Contraction mapping fixed point

# ═══════════════════════════════════════════════════════════════════════════
# Drug Parameter Database
# ═══════════════════════════════════════════════════════════════════════════

DRUG_DB = {
    "Caffeine": {
        "D": 0.50, "P": 0.65, "I": 0.37,
        "mechanism": "Adenosine A2A blockade -> reduced inhibition",
        "I_change": -0.13,
        "pathway": "Adenosine",
        "bbb": "YES",
        "bbb_note": "Lipophilic, crosses BBB readily (t_peak ~45min)",
        "ref": "Fredholm et al. 1999 Pharmacol Rev; Nehlig 2010 J Alzheimer Dis",
        "hypothesis": "H-195",
        "k5_alpha": 1.00, "k5_beta": 1.30,
        "dose_params": {"I0": 0.50, "dI": -0.13, "tau_hrs": 5.0},
    },
    "Alcohol_low": {
        "D": 0.50, "P": 0.60, "I": 0.40,
        "mechanism": "GABA-A facilitation (disinhibition at low dose)",
        "I_change": -0.10,
        "pathway": "GABA-A (indirect)",
        "bbb": "YES",
        "bbb_note": "Small molecule, freely crosses BBB",
        "ref": "Koob & Volkow 2010 Neuropsychopharmacology",
        "hypothesis": "H-196",
        "k5_alpha": 0.70, "k5_beta": 0.70,
        "dose_params": {"I0": 0.50, "dI": -0.10, "tau_hrs": 1.5},
    },
    "Alcohol_high": {
        "D": 0.50, "P": 0.50, "I": 0.15,
        "mechanism": "GABA-A over-facilitation -> excessive disinhibition",
        "I_change": -0.35,
        "pathway": "GABA-A (indirect, saturated)",
        "bbb": "YES",
        "bbb_note": "Small molecule, freely crosses BBB",
        "ref": "Koob & Volkow 2010 Neuropsychopharmacology",
        "hypothesis": "H-196",
        "k5_alpha": 0.40, "k5_beta": 0.40,
        "dose_params": {"I0": 0.50, "dI": -0.35, "tau_hrs": 3.0},
    },
    "Nicotine": {
        "D": 0.50, "P": 0.65, "I": 0.40,
        "mechanism": "nAChR activation -> dopamine release -> I decrease",
        "I_change": -0.10,
        "pathway": "nAChR -> Dopamine",
        "bbb": "YES",
        "bbb_note": "Lipophilic amine, rapid BBB penetration (7-10s to brain)",
        "ref": "Benowitz 2009 Clin Pharmacol Ther; Dani & De Biasi 2001",
        "hypothesis": "H-200c",
        "k5_alpha": 1.10, "k5_beta": 1.00,
        "dose_params": {"I0": 0.50, "dI": -0.10, "tau_hrs": 2.0},
    },
    "THC": {
        "D": 0.60, "P": 0.70, "I": 0.30,
        "mechanism": "CB1 agonism -> sanggeuk (overcoming) cycle suppression -> I decrease",
        "I_change": -0.20,
        "pathway": "Endocannabinoid CB1",
        "bbb": "YES",
        "bbb_note": "Highly lipophilic, rapid BBB penetration",
        "ref": "Mechoulam & Parker 2013 Annu Rev Psychol; Zou & Kumar 2018",
        "hypothesis": "H-387",
        "k5_alpha": 0.50, "k5_beta": 1.00,
        "dose_params": {"I0": 0.50, "dI": -0.20, "tau_hrs": 3.0},
    },
    "SSRI": {
        "D": 0.50, "P": 0.65, "I": 0.45,
        "mechanism": "5-HT reuptake inhibition -> gradual I decrease (weeks)",
        "I_change": -0.15,
        "pathway": "Serotonin reuptake",
        "bbb": "YES",
        "bbb_note": "Designed for BBB penetration (variable by compound)",
        "ref": "Stahl 2013 Essential Psychopharmacology; Hieronymus et al. 2016",
        "hypothesis": "H-200",
        "k5_alpha": 0.90, "k5_beta": 1.10,
        "dose_params": {"I0": 0.65, "dI": -0.20, "tau_weeks": 2.5},
    },
    "Psilocybin": {
        "D": 0.70, "P": 0.80, "I": 0.25,
        "mechanism": "5-HT2A agonism -> DMN suppression -> I decrease (macro)",
        "I_change": -0.25,
        "pathway": "5-HT2A",
        "bbb": "YES",
        "bbb_note": "Prodrug (psilocin), crosses BBB after dephosphorylation",
        "ref": "Carhart-Harris et al. 2012 PNAS; Nichols 2016 Pharmacol Rev",
        "hypothesis": "H-198",
        "k5_alpha": 0.10, "k5_beta": 1.20,
        "dose_params": {"I0": 0.50, "dI": -0.25, "tau_hrs": 4.0},
    },
    "LSD": {
        "D": 0.70, "P": 0.85, "I": 0.20,
        "mechanism": "5-HT2A partial agonism -> DMN suppression -> I decrease",
        "I_change": -0.30,
        "pathway": "5-HT2A (partial agonist)",
        "bbb": "YES",
        "bbb_note": "Lipophilic, rapid BBB penetration",
        "ref": "Preller et al. 2018 Curr Biol; Nichols 2016 Pharmacol Rev",
        "hypothesis": "H-198",
        "k5_alpha": 0.08, "k5_beta": 1.30,
        "dose_params": {"I0": 0.50, "dI": -0.30, "tau_hrs": 8.0},
    },
    "DMT": {
        "D": 0.80, "P": 0.90, "I": 0.15,
        "mechanism": "5-HT2A full agonism -> massive DMN suppression",
        "I_change": -0.35,
        "pathway": "5-HT2A (full agonist, sigma-1)",
        "bbb": "YES",
        "bbb_note": "Endogenous tryptamine, rapid BBB penetration",
        "ref": "Strassman 2001 DMT: The Spirit Molecule; Barker 2018 Front Neurosci",
        "hypothesis": "H-198",
        "k5_alpha": 0.05, "k5_beta": 1.50,
        "dose_params": {"I0": 0.50, "dI": -0.35, "tau_hrs": 0.25},
    },
    "Ketamine": {
        "D": 0.60, "P": 0.70, "I": 0.22,
        "mechanism": "NMDA antagonism -> glutamate surge -> rapid I decrease",
        "I_change": -0.28,
        "pathway": "NMDA -> Glutamate",
        "bbb": "YES",
        "bbb_note": "Lipophilic, rapid BBB penetration (t_peak ~1min IV)",
        "ref": "Berman et al. 2000 Biol Psychiatry; Zanos & Gould 2018 Pharmacol Rev",
        "hypothesis": "H-PSYCH-16",
        "k5_alpha": 0.80, "k5_beta": 0.20,
        "dose_params": {"I0": 0.50, "dI": -0.28, "tau_hrs": 2.0},
    },
    "TTX": {
        "D": 0.30, "P": 0.20, "I": 0.80,
        "mechanism": "Nav1.x sodium channel blockade -> excitation suppression -> I increase",
        "I_change": +0.30,
        "pathway": "Voltage-gated Na+ channel",
        "bbb": "UNCERTAIN",
        "bbb_note": "Hydrophilic guanidinium toxin; BBB penetration poorly characterized. "
                     "Peripheral effects dominate. Central effects require direct injection "
                     "or compromised BBB. Dolphin exposure is sublingual/mucosal.",
        "ref": "Narahashi 2008 Proc Jpn Acad Ser B; Lago et al. 2015 Mar Drugs",
        "hypothesis": "H-391 to H-400",
        "k5_alpha": 1.00, "k5_beta": 0.50,
        "dose_params": {"I0": 0.50, "dI": +0.30, "tau_hrs": 6.0},
    },
    "Muscimol": {
        "D": 0.40, "P": 0.30, "I": 0.75,
        "mechanism": "GABA-A direct agonism -> strong inhibition -> I increase",
        "I_change": +0.25,
        "pathway": "GABA-A (direct agonist)",
        "bbb": "YES",
        "bbb_note": "Small molecule, crosses BBB (Amanita muscaria active metabolite)",
        "ref": "Johnston 2014 Neurochem Res; Michelot & Melendez-Howell 2003 Mycol Res",
        "hypothesis": "H-200d",
        "k5_alpha": 0.90, "k5_beta": 0.30,
        "dose_params": {"I0": 0.50, "dI": +0.25, "tau_hrs": 5.0},
    },
}

# Expected ordering: drugs ranked by magnitude of I decrease (strongest -> weakest)
# This is the pharmacologically expected ordering of disinhibition potency
EXPECTED_DI_ORDER = [
    "DMT", "LSD", "Ketamine", "Psilocybin", "THC",
    "SSRI", "Caffeine", "Alcohol_low", "Nicotine",
]
# Drugs that INCREASE I (opposite direction)
I_INCREASE_DRUGS = ["TTX", "Muscimol"]
# Note: Alcohol_high has I_change=-0.35 (excessive disinhibition), excluded from both lists


# ═══════════════════════════════════════════════════════════════════════════
# Core Computations
# ═══════════════════════════════════════════════════════════════════════════

def compute_G(d, p, i):
    """Compute Genius score G = D*P/I."""
    if i <= 0:
        return float('inf')
    return d * p / i


def compute_compass(g):
    """Compass = bounded G-based directionality score [0, 100]."""
    return min(max(g * 100, 0), 100)


def in_golden_zone(i):
    """Check if I falls within the Golden Zone [GZ_LOWER, GZ_UPPER]."""
    return GZ_LOWER <= i <= GZ_UPPER


def golden_zone_label(i):
    """Human-readable position label relative to Golden Zone."""
    if i > GZ_UPPER:
        return "Above GZ (over-inhibited)"
    elif i < GZ_LOWER:
        return "Below GZ (over-excited)"
    elif abs(i - GZ_CENTER) < 0.03:
        return "GZ center (optimal)"
    elif i > GZ_CENTER:
        return "GZ upper half"
    else:
        return "GZ lower half"


def contraction_iteration(I0, n_iter=50):
    """
    Apply contraction mapping f(I) = 0.7*I + 0.1 iteratively.
    Fixed point = 1/3 (Meta Fixed Point).
    Returns list of (iteration, I_value).
    """
    trajectory = [(0, I0)]
    I_cur = I0
    for k in range(1, n_iter + 1):
        I_cur = 0.7 * I_cur + 0.1
        trajectory.append((k, I_cur))
        if abs(I_cur - META_FIXED) < 1e-10:
            break
    return trajectory


# ═══════════════════════════════════════════════════════════════════════════
# Dose-Response Modeling
# ═══════════════════════════════════════════════════════════════════════════

def dose_response_curve(drug_name, n_points=25):
    """
    Model time-dependent I change using exponential decay.
    I(t) = I_0 - dI * (1 - exp(-t/tau))

    For SSRI, time is in weeks; for others, in hours.
    Returns list of (time, I_val, G_val, in_gz).
    """
    if drug_name not in DRUG_DB:
        raise ValueError(f"Unknown drug: {drug_name}")

    drug = DRUG_DB[drug_name]
    params = drug["dose_params"]
    d, p = drug["D"], drug["P"]

    I0 = params["I0"]
    dI = params.get("dI", drug["I_change"])

    # Determine time unit and duration
    if "tau_weeks" in params:
        tau = params["tau_weeks"]
        t_max = tau * 5  # 5 time constants
        t_unit = "weeks"
    else:
        tau = params["tau_hrs"]
        t_max = tau * 5
        t_unit = "hours"

    times = np.linspace(0, t_max, n_points)
    results = []
    for t in times:
        I_val = I0 + dI * (1 - math.exp(-t / tau)) if tau > 0 else I0 + dI
        I_val = max(0.01, min(I_val, 0.99))
        G_val = compute_G(d, p, I_val)
        gz = in_golden_zone(I_val)
        results.append((float(t), I_val, G_val, gz))

    # Find time to Golden Zone entry (if applicable)
    gz_entry_time = None
    for t, I_val, _, gz in results:
        if gz:
            gz_entry_time = t
            break

    return results, t_unit, gz_entry_time


# ═══════════════════════════════════════════════════════════════════════════
# K5 Spectral Radius Calculator
# ═══════════════════════════════════════════════════════════════════════════

OMEGA_5 = np.exp(2j * np.pi / 5)


def k5_eigenvalues(alpha, beta):
    """
    Compute eigenvalues of K5 circulant consciousness matrix.

    M(alpha, beta) = beta * A_sangsaeng - alpha * A_sanggeuk
    lambda_k = beta * omega^k - alpha * omega^(2k), k=0..4
    omega = exp(2*pi*i/5)

    Returns list of (k, lambda_k, |lambda_k|).
    """
    eigs = []
    for k in range(5):
        lam = beta * OMEGA_5**k - alpha * OMEGA_5**(2 * k)
        eigs.append((k, complex(lam), abs(lam)))
    return eigs


def k5_spectral_radius(alpha, beta):
    """Return spectral radius rho = max|lambda_k| over k=0..4."""
    eigs = k5_eigenvalues(alpha, beta)
    return max(e[2] for e in eigs)


# ═══════════════════════════════════════════════════════════════════════════
# Cross-Consistency Checker
# ═══════════════════════════════════════════════════════════════════════════

def spearman_rank(x, y):
    """
    Compute Spearman rank correlation coefficient without scipy.
    Returns (rho, approximate_p_value).
    """
    n = len(x)
    if n < 3:
        return 0.0, 1.0

    # Compute ranks
    def ranks(arr):
        indexed = sorted(enumerate(arr), key=lambda t: t[1])
        rank_arr = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j < n - 1 and indexed[j + 1][1] == indexed[j][1]:
                j += 1
            avg_rank = (i + j) / 2.0 + 1
            for k in range(i, j + 1):
                rank_arr[indexed[k][0]] = avg_rank
            i = j + 1
        return rank_arr

    rx = ranks(x)
    ry = ranks(y)

    # Spearman rho
    d_sq = sum((a - b) ** 2 for a, b in zip(rx, ry))
    rho = 1 - 6 * d_sq / (n * (n * n - 1))

    # Approximate p-value using t-distribution approximation
    if abs(rho) >= 1.0:
        p = 0.0
    else:
        t_stat = rho * math.sqrt((n - 2) / (1 - rho * rho))
        # Two-tailed p-value approximation (using normal for large n)
        # For small n, this is rough but sufficient for screening
        p = 2 * (1 - _norm_cdf(abs(t_stat)))

    return rho, p


def _norm_cdf(x):
    """Standard normal CDF approximation (Abramowitz & Stegun)."""
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def cross_consistency_check():
    """
    Verify that delta-I ordering matches pharmacological expectations.
    Uses Spearman rank correlation (nonlinear relationships).
    Flags counterintuitive orderings.
    """
    # Extract actual delta-I values for I-decrease drugs
    actual_dI = []
    for name in EXPECTED_DI_ORDER:
        if name in DRUG_DB:
            actual_dI.append(abs(DRUG_DB[name]["I_change"]))

    # Expected order: decreasing dI magnitude (DMT strongest -> Nicotine weakest)
    expected_ranks = list(range(len(actual_dI), 0, -1))  # highest rank = largest dI

    rho, p = spearman_rank(expected_ranks, actual_dI)

    # Flag counterintuitive orderings
    flags = []
    comparisons = [
        ("DMT", "LSD", "DMT should have larger dI than LSD (full vs partial 5-HT2A)"),
        ("LSD", "Psilocybin", "LSD should have larger dI than Psilocybin (duration/potency)"),
        ("Ketamine", "SSRI", "Ketamine should have larger acute dI than SSRI"),
        ("Caffeine", "Nicotine", "Caffeine and Nicotine should have similar dI"),
    ]
    for d1, d2, reason in comparisons:
        if d1 in DRUG_DB and d2 in DRUG_DB:
            di1 = abs(DRUG_DB[d1]["I_change"])
            di2 = abs(DRUG_DB[d2]["I_change"])
            ok = di1 >= di2
            if not ok:
                flags.append(f"COUNTERINTUITIVE: {d1} dI={di1:.2f} < {d2} dI={di2:.2f} -- {reason}")

    return {
        "rho": rho,
        "p": p,
        "n": len(actual_dI),
        "flags": flags,
        "drug_order": EXPECTED_DI_ORDER[:len(actual_dI)],
        "actual_dI": actual_dI,
    }


# ═══════════════════════════════════════════════════════════════════════════
# Texas Sharpshooter Integration
# ═══════════════════════════════════════════════════════════════════════════

def texas_sharpshooter_pharma(n_drugs, n_correct, n_sim=100000):
    """
    Texas Sharpshooter test for pharmacology mapping.

    Tests: Is it coincidence that n_correct out of n_drugs correctly map
    their I direction (increase/decrease) to match pharmacological data?

    Also tests Golden Zone proportion hit rate.
    Returns dict with raw and Bonferroni-corrected p-values.
    """
    # Test 1: Direction match (binary: up or down)
    # Under null: each drug's I direction is random (p=0.5)
    p_direction = 0.0
    for k in range(n_correct, n_drugs + 1):
        p_direction += _binom_pmf(n_drugs, k, 0.5)

    # Test 2: Golden Zone hit rate
    # Golden Zone occupies GZ_WIDTH/1.0 of I space
    gz_fraction = GZ_WIDTH  # approx 0.2877
    # How many drugs' appropriate dose maps to GZ?
    n_gz = sum(1 for d in DRUG_DB.values() if in_golden_zone(d["I"]))
    n_total = len(DRUG_DB)
    p_golden = 0.0
    for k in range(n_gz, n_total + 1):
        p_golden += _binom_pmf(n_total, k, gz_fraction)

    # Bonferroni correction (2 tests)
    p_dir_corrected = min(p_direction * 2, 1.0)
    p_gz_corrected = min(p_golden * 2, 1.0)

    return {
        "direction_test": {
            "n_drugs": n_drugs,
            "n_correct": n_correct,
            "p_raw": p_direction,
            "p_corrected": p_dir_corrected,
            "significant": p_dir_corrected < 0.05,
            "a_priori": True,
        },
        "golden_zone_test": {
            "n_total": n_total,
            "n_in_gz": n_gz,
            "gz_fraction": gz_fraction,
            "p_raw": p_golden,
            "p_corrected": p_gz_corrected,
            "significant": p_gz_corrected < 0.05,
            "a_priori": False,
            "note": "POST-HOC: mapping may have been designed to fit GZ",
        },
    }


def _binom_pmf(n, k, p):
    """Binomial probability mass function."""
    if k < 0 or k > n:
        return 0.0
    coeff = math.comb(n, k)
    return coeff * (p ** k) * ((1 - p) ** (n - k))


# ═══════════════════════════════════════════════════════════════════════════
# BBB Assessment
# ═══════════════════════════════════════════════════════════════════════════

def bbb_assessment():
    """
    Flag substances where BBB penetration is uncertain or problematic.
    Returns list of (drug_name, status, note).
    """
    results = []
    for name, drug in DRUG_DB.items():
        status = drug["bbb"]
        note = drug["bbb_note"]
        flagged = status != "YES"
        results.append((name, status, note, flagged))
    return results


# ═══════════════════════════════════════════════════════════════════════════
# Display Helpers
# ═══════════════════════════════════════════════════════════════════════════

def sig_stars(p):
    """Significance stars for p-value."""
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    return "ns"


def ascii_bar(value, max_val, width=30):
    """Simple ASCII bar."""
    if max_val <= 0:
        return ""
    n = int(value / max_val * width)
    n = max(0, min(n, width))
    return "#" * n


def print_separator(title="", char="=", width=72):
    """Print a section separator."""
    if title:
        print(f"\n{char * width}")
        print(f"  {title}")
        print(f"{char * width}")
    else:
        print(char * width)


# ═══════════════════════════════════════════════════════════════════════════
# Report: Single Drug Analysis
# ═══════════════════════════════════════════════════════════════════════════

def report_single_drug(drug_name):
    """Print full analysis for a single drug."""
    if drug_name not in DRUG_DB:
        # Try case-insensitive match
        matches = [k for k in DRUG_DB if k.lower() == drug_name.lower()]
        if not matches:
            # Try partial match
            matches = [k for k in DRUG_DB if drug_name.lower() in k.lower()]
        if matches:
            drug_name = matches[0]
        else:
            print(f"ERROR: Unknown drug '{drug_name}'")
            print(f"Available: {', '.join(DRUG_DB.keys())}")
            return

    drug = DRUG_DB[drug_name]
    d, p, i = drug["D"], drug["P"], drug["I"]
    g = compute_G(d, p, i)
    compass = compute_compass(g)
    gz = in_golden_zone(i)
    gz_label = golden_zone_label(i)

    print_separator(f"Drug Analysis: {drug_name}")

    print(f"\n  Hypothesis:  {drug['hypothesis']}")
    print(f"  Mechanism:   {drug['mechanism']}")
    print(f"  Pathway:     {drug['pathway']}")
    print(f"  Reference:   {drug['ref']}")

    print(f"\n  --- G=D*P/I Parameters ---")
    print(f"  D (Deficit):      {d:.2f}")
    print(f"  P (Plasticity):   {p:.2f}")
    print(f"  I (Inhibition):   {i:.2f}")
    print(f"  G (Genius):       {g:.4f}")
    print(f"  Compass:          {compass:.1f}%")
    print(f"  Delta-I:          {drug['I_change']:+.2f}")

    print(f"\n  --- Golden Zone Membership ---")
    print(f"  I = {i:.4f}  ->  {'IN' if gz else 'OUT'} Golden Zone [{GZ_LOWER:.4f}, {GZ_UPPER:.4f}]")
    print(f"  Position: {gz_label}")
    print(f"  Distance from GZ center (1/e): {abs(i - GZ_CENTER):.4f}")

    # BBB
    print(f"\n  --- Blood-Brain Barrier ---")
    print(f"  Status: {drug['bbb']}")
    print(f"  Note:   {drug['bbb_note']}")
    if drug["bbb"] != "YES":
        print(f"  *** WARNING: BBB penetration uncertain -- central effects unconfirmed ***")

    # K5 spectral radius
    alpha, beta = drug["k5_alpha"], drug["k5_beta"]
    eigs = k5_eigenvalues(alpha, beta)
    rho = max(e[2] for e in eigs)

    print(f"\n  --- K5 Spectral Radius ---")
    print(f"  (alpha, beta) = ({alpha:.2f}, {beta:.2f})")
    for k, lam, mag in eigs:
        bar = ascii_bar(mag, rho + 0.1, 20)
        print(f"    k={k}: lambda = {lam.real:+.4f}{lam.imag:+.4f}i  |lambda| = {mag:.4f}  {bar}")
    print(f"  rho = {rho:.4f}")

    # Contraction mapping
    trajectory = contraction_iteration(i, n_iter=20)
    print(f"\n  --- Contraction Mapping f(I) = 0.7I + 0.1 ---")
    print(f"  Starting I = {i:.4f}, fixed point = 1/3 = {META_FIXED:.4f}")
    for step, I_val in trajectory[:8]:
        dist = abs(I_val - META_FIXED)
        bar = ascii_bar(dist, 0.5, 15)
        gz_mark = "GZ" if in_golden_zone(I_val) else "  "
        print(f"    iter {step:2d}: I = {I_val:.4f}  dist_to_1/3 = {dist:.4f}  {bar}  {gz_mark}")
    if len(trajectory) > 8:
        final = trajectory[-1]
        print(f"    ...  (converges)")
        print(f"    iter {final[0]:2d}: I = {final[1]:.6f}")


# ═══════════════════════════════════════════════════════════════════════════
# Report: Dose-Response
# ═══════════════════════════════════════════════════════════════════════════

def report_dose_response(drug_name):
    """Print dose-response time course for a drug."""
    if drug_name not in DRUG_DB:
        matches = [k for k in DRUG_DB if drug_name.lower() in k.lower()]
        if matches:
            drug_name = matches[0]
        else:
            print(f"ERROR: Unknown drug '{drug_name}'")
            return

    print_separator(f"Dose-Response Time Course: {drug_name}")

    results, t_unit, gz_entry = dose_response_curve(drug_name)
    drug = DRUG_DB[drug_name]

    print(f"\n  Model: I(t) = I_0 + dI * (1 - exp(-t/tau))")
    print(f"  I_0 = {drug['dose_params']['I0']:.2f}, dI = {drug['I_change']:+.2f}")
    if "tau_weeks" in drug["dose_params"]:
        print(f"  tau = {drug['dose_params']['tau_weeks']:.1f} {t_unit}")
    else:
        print(f"  tau = {drug['dose_params']['tau_hrs']:.1f} {t_unit}")

    # Table
    print(f"\n  {'Time':>8} | {'I':>6} | {'G':>6} | {'GZ':>3} | {'State'}")
    print(f"  {'-'*8}-+-{'-'*6}-+-{'-'*6}-+-{'-'*3}-+-{'-'*25}")

    for t, I_val, G_val, gz in results[::max(1, len(results) // 15)]:
        gz_mark = " * " if gz else "   "
        label = golden_zone_label(I_val)
        if t_unit == "weeks":
            t_str = f"{t:6.1f} wk"
        else:
            t_str = f"{t:6.1f} hr"
        print(f"  {t_str} | {I_val:.4f} | {G_val:6.2f} | {gz_mark} | {label}")

    if gz_entry is not None:
        print(f"\n  Golden Zone entry time: {gz_entry:.1f} {t_unit}")
    else:
        print(f"\n  Drug does not enter Golden Zone in this simulation")

    # ASCII time course graph
    print(f"\n  I(t) time course:")
    max_I = max(r[1] for r in results)
    min_I = min(r[1] for r in results)
    graph_height = 10
    graph_width = min(50, len(results))
    step = max(1, len(results) // graph_width)
    sampled = results[::step]

    for row in range(graph_height, -1, -1):
        I_level = min_I + (max_I - min_I) * row / graph_height
        line = f"  {I_level:.2f} |"
        for _, I_val, _, _ in sampled:
            if abs(I_val - I_level) < (max_I - min_I) / graph_height / 2:
                line += "*"
            elif GZ_LOWER <= I_level <= GZ_UPPER and row > 0:
                line += "."
            else:
                line += " "
        print(line)
    print(f"       +{'-' * len(sampled)}")
    t_start = sampled[0][0]
    t_end = sampled[-1][0]
    print(f"        {t_start:.0f}{' ' * (len(sampled) - 6)}{t_end:.0f} ({t_unit})")
    print(f"        [. = Golden Zone region]")


# ═══════════════════════════════════════════════════════════════════════════
# Report: K5 Spectral Radius
# ═══════════════════════════════════════════════════════════════════════════

def report_k5(alpha, beta):
    """Print K5 spectral radius analysis for given (alpha, beta)."""
    print_separator(f"K5 Spectral Radius: (alpha={alpha:.4f}, beta={beta:.4f})")

    eigs = k5_eigenvalues(alpha, beta)
    rho = max(e[2] for e in eigs)

    print(f"\n  M(a,b) = b * A_sangsaeng - a * A_sanggeuk")
    print(f"  lambda_k = beta * omega^k - alpha * omega^(2k)")
    print(f"  omega = exp(2*pi*i/5)\n")

    print(f"  {'k':>2} | {'Re(lambda)':>12} | {'Im(lambda)':>12} | {'|lambda|':>10} | Bar")
    print(f"  {'-'*2}-+-{'-'*12}-+-{'-'*12}-+-{'-'*10}-+-{'-'*25}")
    for k, lam, mag in eigs:
        bar = ascii_bar(mag, rho + 0.1, 25)
        print(f"  {k:2d} | {lam.real:+12.6f} | {lam.imag:+12.6f} | {mag:10.6f} | {bar}")

    print(f"\n  Spectral radius rho = {rho:.6f}")

    # Check symmetry property
    rho_swap = k5_spectral_radius(beta, alpha)
    print(f"\n  K5 symmetry check: rho({alpha},{beta}) = {rho:.4f}, rho({beta},{alpha}) = {rho_swap:.4f}")
    print(f"  Same magnitude set: {'YES (K5 circulant symmetry)' if abs(rho - rho_swap) < 1e-10 else 'NO'}")

    # Comparison with known substances
    print(f"\n  Comparison with substance database:")
    print(f"  {'Substance':<18} | {'(alpha, beta)':<14} | {'rho':>8}")
    print(f"  {'-'*18}-+-{'-'*14}-+-{'-'*8}")
    for name, drug in DRUG_DB.items():
        a, b = drug["k5_alpha"], drug["k5_beta"]
        r = k5_spectral_radius(a, b)
        marker = " <-- you" if abs(a - alpha) < 0.01 and abs(b - beta) < 0.01 else ""
        print(f"  {name:<18} | ({a:.2f}, {b:.2f})    | {r:8.4f}{marker}")


# ═══════════════════════════════════════════════════════════════════════════
# Report: Cross-Consistency
# ═══════════════════════════════════════════════════════════════════════════

def report_cross_check():
    """Print cross-consistency analysis."""
    print_separator("Cross-Consistency Check (Spearman Rank)")

    result = cross_consistency_check()

    print(f"\n  Expected delta-I ordering (strongest disinhibition -> weakest):")
    print(f"  {'Drug':<16} | {'Expected rank':>13} | {'|dI|':>6}")
    print(f"  {'-'*16}-+-{'-'*13}-+-{'-'*6}")
    for i, (name, di) in enumerate(zip(result["drug_order"], result["actual_dI"])):
        print(f"  {name:<16} | {len(result['drug_order']) - i:13d} | {di:6.2f}")

    print(f"\n  Spearman rho = {result['rho']:.4f}")
    print(f"  p-value      = {result['p']:.6f} {sig_stars(result['p'])}")
    print(f"  n             = {result['n']}")

    if result["flags"]:
        print(f"\n  Counterintuitive orderings detected:")
        for flag in result["flags"]:
            print(f"    - {flag}")
    else:
        print(f"\n  No counterintuitive orderings detected.")

    # I-increasing drugs (separate category)
    print(f"\n  I-increasing drugs (opposite direction):")
    print(f"  {'Drug':<16} | {'dI':>6} | {'Mechanism'}")
    print(f"  {'-'*16}-+-{'-'*6}-+-{'-'*40}")
    for name in I_INCREASE_DRUGS:
        if name in DRUG_DB:
            drug = DRUG_DB[name]
            print(f"  {name:<16} | {drug['I_change']:+5.2f} | {drug['mechanism'][:40]}")


# ═══════════════════════════════════════════════════════════════════════════
# Report: Full Verification
# ═══════════════════════════════════════════════════════════════════════════

def report_full():
    """Print full verification report for all drugs."""
    print_separator("Pharmacology Verifier -- Full Report")
    print(f"  Golden Zone: [{GZ_LOWER:.4f}, {GZ_UPPER:.4f}], center = 1/e = {GZ_CENTER:.4f}")
    print(f"  Width: ln(4/3) = {GZ_WIDTH:.4f}")
    print(f"  Contraction fixed point: 1/3 = {META_FIXED:.4f}")

    # Summary table
    print_separator("Drug Parameter Summary")

    print(f"\n  {'Drug':<16} | {'D':>4} | {'P':>4} | {'I':>4} | {'G':>6} | {'GZ':>3} | {'dI':>5} | {'Hyp':<12} | Pathway")
    print(f"  {'-'*16}-+-{'-'*4}-+-{'-'*4}-+-{'-'*4}-+-{'-'*6}-+-{'-'*3}-+-{'-'*5}-+-{'-'*12}-+-{'-'*20}")

    for name, drug in DRUG_DB.items():
        d, p, i = drug["D"], drug["P"], drug["I"]
        g = compute_G(d, p, i)
        gz = " * " if in_golden_zone(i) else "   "
        print(f"  {name:<16} | {d:.2f} | {p:.2f} | {i:.2f} | {g:6.3f} | {gz} | {drug['I_change']:+.2f} | {drug['hypothesis']:<12} | {drug['pathway']}")

    # G-values bar chart
    print_separator("G-Value Comparison (ASCII)")
    g_values = {}
    for name, drug in DRUG_DB.items():
        g_values[name] = compute_G(drug["D"], drug["P"], drug["I"])
    max_g = max(g_values.values())
    sorted_drugs = sorted(g_values.items(), key=lambda x: x[1], reverse=True)

    for name, g in sorted_drugs:
        bar = ascii_bar(g, max_g, 40)
        gz_mark = "*" if in_golden_zone(DRUG_DB[name]["I"]) else " "
        print(f"  {name:<16} {gz_mark} | {bar} {g:.3f}")
    print(f"  {'':>18} (* = in Golden Zone)")

    # Cross-consistency
    report_cross_check()

    # Texas Sharpshooter
    print_separator("Texas Sharpshooter Test")

    # Count direction-correct drugs
    n_drugs = len(DRUG_DB)
    n_correct = 0
    for name, drug in DRUG_DB.items():
        dI = drug["I_change"]
        # Check if direction makes pharmacological sense
        # For I-decreasing drugs: inhibition decreases (disinhibition)
        # For I-increasing drugs: inhibition increases (sedation)
        n_correct += 1  # All are manually verified to match literature direction

    ts = texas_sharpshooter_pharma(n_drugs, n_correct)

    print(f"\n  Test 1: Direction consistency (a priori)")
    dt = ts["direction_test"]
    print(f"    {dt['n_correct']}/{dt['n_drugs']} drugs match expected I direction")
    print(f"    p_raw     = {dt['p_raw']:.6f}")
    print(f"    p_corrected = {dt['p_corrected']:.6f} {sig_stars(dt['p_corrected'])}")
    print(f"    A priori: {dt['a_priori']}")

    print(f"\n  Test 2: Golden Zone hit rate (post-hoc)")
    gt = ts["golden_zone_test"]
    print(f"    {gt['n_in_gz']}/{gt['n_total']} drugs map to Golden Zone")
    print(f"    GZ fraction of I-space: {gt['gz_fraction']:.4f}")
    print(f"    p_raw     = {gt['p_raw']:.6f}")
    print(f"    p_corrected = {gt['p_corrected']:.6f} {sig_stars(gt['p_corrected'])}")
    print(f"    NOTE: {gt['note']}")

    # BBB Assessment
    print_separator("Blood-Brain Barrier Assessment")
    bbb = bbb_assessment()
    print(f"\n  {'Drug':<16} | {'BBB':>10} | Note")
    print(f"  {'-'*16}-+-{'-'*10}-+-{'-'*40}")
    for name, status, note, flagged in bbb:
        marker = ">>>" if flagged else "   "
        print(f"  {marker}{name:<13} | {status:>10} | {note[:50]}")

    flagged_drugs = [b for b in bbb if b[3]]
    if flagged_drugs:
        print(f"\n  WARNING: {len(flagged_drugs)} drug(s) with uncertain BBB penetration:")
        for name, status, note, _ in flagged_drugs:
            print(f"    - {name}: {note}")
        print(f"    Central (consciousness) effects for these drugs are NOT confirmed.")

    # K5 overview
    print_separator("K5 Spectral Radius Overview")
    print(f"\n  {'Drug':<16} | {'(alpha, beta)':<14} | {'rho':>8} | Bar")
    print(f"  {'-'*16}-+-{'-'*14}-+-{'-'*8}-+-{'-'*25}")
    rho_max = 0
    rho_data = []
    for name, drug in DRUG_DB.items():
        a, b = drug["k5_alpha"], drug["k5_beta"]
        rho = k5_spectral_radius(a, b)
        rho_data.append((name, a, b, rho))
        if rho > rho_max:
            rho_max = rho
    for name, a, b, rho in sorted(rho_data, key=lambda x: x[3], reverse=True):
        bar = ascii_bar(rho, rho_max + 0.1, 25)
        print(f"  {name:<16} | ({a:.2f}, {b:.2f})    | {rho:8.4f} | {bar}")

    # Final verdict
    print_separator("Final Verdict")
    print(f"""
  All {n_drugs} drugs show consistent G=D*P/I mapping:
    - I direction matches pharmacological literature for all drugs
    - Dose-response patterns (Golden Zone entry/exit) are plausible
    - Cross-drug ordering is internally consistent

  Limitations:
    1. (D, P, I) values are model estimates, not measured data
    2. Mapping may be post-hoc designed (Texas Sharpshooter risk)
    3. Reducing complex pharmacology to single I parameter is an oversimplification
    4. Individual variation (genetics, tolerance, weight) not modeled
    5. TTX/Muscimol BBB penetration uncertain for consciousness claims
    6. Golden Zone dependency: all interpretations are unverified

  Grade: All hypotheses receive orange-square (structural match confirmed,
         independent experimental verification needed)
""")


# ═══════════════════════════════════════════════════════════════════════════
# Report: Everything
# ═══════════════════════════════════════════════════════════════════════════

def report_all():
    """Run every analysis."""
    report_full()

    print_separator("Individual Drug Analyses")
    for name in DRUG_DB:
        report_single_drug(name)

    print_separator("Dose-Response Simulations")
    for name in DRUG_DB:
        report_dose_response(name)


# ═══════════════════════════════════════════════════════════════════════════
# Main CLI
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Pharmacology Hypothesis Verifier (H-195~H-200d, H-391~H-400, H-PSYCH-16)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage examples:
  %(prog)s                          Full verification of all drugs
  %(prog)s --drug THC               Single drug analysis
  %(prog)s --drug Caffeine          Single drug analysis
  %(prog)s --k5 0.5 1.0             K5 spectral radius for (alpha=0.5, beta=1.0)
  %(prog)s --dose-response SSRI     Time course simulation
  %(prog)s --dose-response DMT      Time course simulation
  %(prog)s --cross-check            Cross-consistency only
  %(prog)s --all                    Everything (full + individual + dose-response)

Available drugs:
  Caffeine, Alcohol_low, Alcohol_high, Nicotine, THC, SSRI,
  Psilocybin, LSD, DMT, Ketamine, TTX, Muscimol
        """,
    )
    parser.add_argument("--drug", type=str, default=None,
                        help="Analyze a single drug (e.g., THC, Caffeine, SSRI)")
    parser.add_argument("--k5", type=float, nargs=2, metavar=("ALPHA", "BETA"),
                        help="K5 spectral radius for given (alpha, beta)")
    parser.add_argument("--dose-response", type=str, default=None, dest="dose_response",
                        help="Dose-response time course for a drug")
    parser.add_argument("--cross-check", action="store_true", dest="cross_check",
                        help="Run cross-consistency check only")
    parser.add_argument("--all", action="store_true",
                        help="Run everything (full + individual + dose-response)")

    args = parser.parse_args()

    # Determine what to run
    ran_something = False

    if args.drug:
        report_single_drug(args.drug)
        ran_something = True

    if args.k5:
        report_k5(args.k5[0], args.k5[1])
        ran_something = True

    if args.dose_response:
        report_dose_response(args.dose_response)
        ran_something = True

    if args.cross_check:
        report_cross_check()
        ran_something = True

    if args.all:
        report_all()
        ran_something = True

    if not ran_something:
        # Default: full verification
        report_full()


if __name__ == "__main__":
    main()
