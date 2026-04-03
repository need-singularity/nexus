#!/usr/bin/env python3
"""
H-PH-9 Cosmology, CP Violation, and Quantum Information Verification
=====================================================================
Rigorous numerical verification of all claims in H-PH-9 related to:
  1. Cosmological constant Lambda = 1/(6 * 496^45)
  2. Dark energy/matter fractions from pi
  3. CP violation asymmetry function S(n)
  4. Quantum information: Tsirelson, SU(2)_k quantum dimensions
  5. Page entropy at d=phi(6)=2
  6. PPT criterion for C^2 x C^3
  7. Ising CFT central charge

Uses sympy for exact arithmetic where possible.
"""

import math
from fractions import Fraction
from decimal import Decimal, getcontext

# High precision
getcontext().prec = 60

try:
    from sympy import (
        Rational, pi as sym_pi, log, sqrt, sin, N, S,
        harmonic, Sum, Symbol, oo, factorial, binomial,
        simplify, nsimplify
    )
    HAS_SYMPY = True
except ImportError:
    HAS_SYMPY = False
    print("WARNING: sympy not available, using float arithmetic only\n")


# ============================================================
# n=6 Constants
# ============================================================
n = 6
sigma = 12      # sum of divisors of 6
tau = 4         # number of divisors of 6
phi = 2         # Euler totient of 6
sopfr = 5       # sum of prime factors 2+3
P2 = 496        # third perfect number (actually P3; P2=28)

print("=" * 72)
print("H-PH-9 COSMOLOGY, CP VIOLATION & QUANTUM INFORMATION VERIFICATION")
print("=" * 72)
print()
print(f"n=6 constants: sigma={sigma}, tau={tau}, phi={phi}, sopfr={sopfr}")
print(f"P2(496) used in cosmological constant formula")
print()


# ============================================================
# SECTION 1: COSMOLOGICAL CONSTANT
# ============================================================
print("=" * 72)
print("SECTION 1: COSMOLOGICAL CONSTANT")
print("  Claim: Lambda = 1/(6 * 496^45)")
print("=" * 72)
print()

# Verify 45 = sigma*tau - sigma/tau
val_45_check = sigma * tau - sigma // tau
print(f"  45 = sigma*tau - sigma/tau = {sigma}*{tau} - {sigma}/{tau}")
print(f"     = {sigma*tau} - {sigma//tau} = {val_45_check}")
print(f"     Match: {val_45_check == 45}")
print()

# dim(SO(10)) = 10*9/2 = 45
dim_so10 = 10 * 9 // 2
print(f"  dim(SO(10)) = 10*9/2 = {dim_so10}")
print(f"  45 = dim(SO(10)): {dim_so10 == 45}")
print()

# Compute log10(Lambda) = log10(1/(6 * 496^45)) = -log10(6) - 45*log10(496)
log10_6 = math.log10(6)
log10_496 = math.log10(496)
log10_Lambda = -log10_6 - 45 * log10_496
print(f"  log10(6)   = {log10_6:.15f}")
print(f"  log10(496) = {log10_496:.15f}")
print(f"  log10(Lambda) = -log10(6) - 45*log10(496)")
print(f"                = -{log10_6:.15f} - 45*{log10_496:.15f}")
print(f"                = {log10_Lambda:.15f}")
print()

if HAS_SYMPY:
    # Exact with sympy
    log10_Lambda_exact = -N(log(6, 10) + 45 * log(496, 10), 50)
    print(f"  log10(Lambda) [sympy 50-digit] = {log10_Lambda_exact}")
    print()

# Compare to observations
obs_textbook = -122
obs_planck2018 = -121.54  # Planck 2018: Lambda ~ 2.888e-122 Planck units
# Actually: Lambda_obs ~ 1.1056e-52 m^-2, in Planck units ~ 2.888e-122
# log10(2.888e-122) = log10(2.888) + (-122) = 0.4607 - 122 = -121.539

print(f"  Observed (textbook):    log10(Lambda) ~ {obs_textbook}")
print(f"  Observed (Planck 2018): log10(Lambda) ~ {obs_planck2018}")
print(f"  Model prediction:       log10(Lambda) = {log10_Lambda:.6f}")
print()
print(f"  Error vs textbook (-122):    {abs(log10_Lambda - obs_textbook):.6f}")
print(f"  Error vs Planck (-121.54):   {abs(log10_Lambda - obs_planck2018):.6f}")
print()

# Detailed breakdown
print(f"  Breakdown: 45 * log10(496) = {45 * log10_496:.10f}")
print(f"             log10(6)         = {log10_6:.10f}")
print(f"             Total exponent   = {log10_Lambda:.10f}")
print()


# ============================================================
# SECTION 2: DARK ENERGY / MATTER FRACTIONS
# ============================================================
print("=" * 72)
print("SECTION 2: DARK ENERGY / MATTER / BARYON FRACTIONS")
print("  Model: DE = 1-1/pi, DM = 5/(6*pi), Baryon = 1/(6*pi)")
print("=" * 72)
print()

pi_val = math.pi
DE_model = 1 - 1/pi_val
DM_model = 5 / (6 * pi_val)
B_model = 1 / (6 * pi_val)

print(f"  Dark Energy  = 1 - 1/pi      = {DE_model:.10f}")
print(f"  Dark Matter  = 5/(6*pi)       = {DM_model:.10f}")
print(f"  Baryonic     = 1/(6*pi)       = {B_model:.10f}")
print(f"  Sum          = {DE_model + DM_model + B_model:.15f}")
print()

# Verify sum = 1 algebraically
# 1 - 1/pi + 5/(6pi) + 1/(6pi) = 1 - 1/pi + 6/(6pi) = 1 - 1/pi + 1/pi = 1
if HAS_SYMPY:
    DE_sym = 1 - 1/sym_pi
    DM_sym = Rational(5, 6) / sym_pi
    B_sym = Rational(1, 6) / sym_pi
    total_sym = simplify(DE_sym + DM_sym + B_sym)
    print(f"  Sympy exact sum: {total_sym}")
    print(f"  Sum = 1: {total_sym == 1}  (algebraic proof: 1-1/pi + 5/(6pi) + 1/(6pi) = 1-1/pi+1/pi = 1)")
print()

# Planck 2018 values
DE_planck = 0.6847
DE_planck_err = 0.0073
DM_planck = 0.2642  # This is Omega_cdm (cold dark matter only)
DM_planck_err = 0.0060
B_planck = 0.0493
B_planck_err = 0.0006

print("  Comparison with Planck 2018:")
print(f"  {'Parameter':<15} {'Model':>12} {'Planck 2018':>14} {'Error':>12} {'Sigma':>8}")
print(f"  {'-'*15} {'-'*12} {'-'*14} {'-'*12} {'-'*8}")

for name, model_val, planck_val, planck_err in [
    ("Dark Energy", DE_model, DE_planck, DE_planck_err),
    ("Dark Matter", DM_model, DM_planck, DM_planck_err),
    ("Baryonic", B_model, B_planck, B_planck_err),
]:
    abs_err = abs(model_val - planck_val)
    sigma_away = abs_err / planck_err if planck_err > 0 else float('inf')
    pct_err = 100 * abs_err / planck_val
    print(f"  {name:<15} {model_val:>12.6f} {planck_val:>10.4f}+/-{planck_err:.4f} "
          f"{pct_err:>8.2f}% {sigma_away:>7.1f}sigma")

print()
print("  Note: 5/(6*pi) = sopfr/(n*pi) -- uses n=6 arithmetic functions")
print(f"  Note: 1/(6*pi) = 1/(n*pi) = {B_model:.6f}")
print()


# ============================================================
# SECTION 3: CP VIOLATION
# ============================================================
print("=" * 72)
print("SECTION 3: CP VIOLATION ASYMMETRY")
print("  S(n) = [sigma(n)*phi(n) - n*tau(n)]^2 + [sigma(n)*(n+phi(n)) - n*tau(n)^2]^2")
print("=" * 72)
print()


def divisor_functions(m):
    """Compute sigma, tau, phi for integer m."""
    if m <= 0:
        return 0, 0, 0
    divs = [d for d in range(1, m + 1) if m % d == 0]
    sig = sum(divs)
    ta = len(divs)
    # Euler totient
    ph = sum(1 for k in range(1, m + 1) if math.gcd(k, m) == 1)
    return sig, ta, ph


def S_func(m):
    """CP violation asymmetry function S(n)."""
    sig, ta, ph = divisor_functions(m)
    term1 = sig * ph - m * ta
    term2 = sig * (m + ph) - m * ta**2
    return term1**2 + term2**2


# Compute S for n=5,6,7
print("  Computing S(n) for n = 1..10:")
print(f"  {'n':>4} {'sigma':>6} {'tau':>4} {'phi':>4} {'term1':>10} {'term2':>10} {'S(n)':>15}")
print(f"  {'---':>4} {'---':>6} {'---':>4} {'---':>4} {'---':>10} {'---':>10} {'---':>15}")

for m in range(1, 11):
    sig, ta, ph = divisor_functions(m)
    t1 = sig * ph - m * ta
    t2 = sig * (m + ph) - m * ta**2
    s_val = t1**2 + t2**2
    marker = " <-- S=0 (perfect!)" if s_val == 0 else ""
    print(f"  {m:>4} {sig:>6} {ta:>4} {ph:>4} {t1:>10} {t2:>10} {s_val:>15}{marker}")

print()

# S(5) and S(7) exactly
S5 = S_func(5)
S7 = S_func(7)
S6 = S_func(6)

print(f"  S(5)  = {S5}")
print(f"  S(6)  = {S6}  (perfect number => S=0)")
print(f"  S(7)  = {S7}")
print()

# Asymmetry A
if S5 + S7 != 0:
    A = Fraction(S7 - S5, S7 + S5)
    print(f"  A = (S(7)-S(5))/(S(7)+S(5)) = ({S7}-{S5})/({S7}+{S5})")
    print(f"    = {S7-S5}/{S7+S5}")
    print(f"    = {A} = {float(A):.15f}")
    print()
else:
    A = Fraction(0)
    print("  A = 0 (S5 = S7 = 0)")

# Jarlskog invariant: J = A / sigma^4
sigma4 = sigma**4
print(f"  sigma^4 = {sigma}^4 = {sigma4}")
J_model = float(A) / sigma4
print(f"  J = A/sigma^4 = {float(A):.10f}/{sigma4} = {J_model:.6e}")
print(f"  J (measured) = 3.18e-5 (PDG 2024: (3.18 +/- 0.15) x 10^-5)")
print(f"  Error: {abs(J_model - 3.18e-5)/3.18e-5 * 100:.2f}%")
print()

# epsilon_K: A / (sigma^2 * phi)
sigma2_phi = sigma**2 * phi
print(f"  sigma^2 * phi = {sigma}^2 * {phi} = {sigma2_phi}")
eps_K_model = float(A) / sigma2_phi
print(f"  epsilon_K = A/(sigma^2*phi) = {float(A):.10f}/{sigma2_phi} = {eps_K_model:.6e}")
print(f"  epsilon_K (measured) = 2.228e-3 (PDG: |epsilon| = (2.228 +/- 0.011) x 10^-3)")
print(f"  Error: {abs(eps_K_model - 2.228e-3)/2.228e-3 * 100:.2f}%")
print()

# sin(2beta)
sin2beta_model = float(A)
print(f"  sin(2beta) = A = {sin2beta_model:.6f}")
print(f"  sin(2beta) (measured) = 0.699 +/- 0.017 (PDG/HFLAV)")
print(f"  Error: {abs(sin2beta_model - 0.699)/0.017:.2f} sigma ({abs(sin2beta_model - 0.699)/0.699 * 100:.2f}%)")
print()


# ============================================================
# SECTION 4: QUANTUM INFORMATION
# ============================================================
print("=" * 72)
print("SECTION 4: QUANTUM INFORMATION")
print("=" * 72)
print()

# --- 4a: Tsirelson bound ---
print("--- 4a: Tsirelson Bound ---")
print("  Claim: 2*sqrt(sigma(P)/P) = 2*sqrt(2) for all perfect numbers P")
print()
print("  For ANY perfect number P: sigma(P) = 2P (by definition)")
print("  Therefore: 2*sqrt(sigma(P)/P) = 2*sqrt(2P/P) = 2*sqrt(2)")
print("  This is TRIVIALLY TRUE for all perfect numbers.")
print()
print(f"  2*sqrt(2) = {2*math.sqrt(2):.10f}")
print(f"  Tsirelson bound (CHSH) = 2*sqrt(2) = {2*math.sqrt(2):.10f}")
print("  The Tsirelson bound for the CHSH inequality IS 2*sqrt(2).")
print("  The 'derivation' from perfect numbers is circular: sigma(P)=2P is the DEFINITION.")
print()

# --- 4b: SU(2)_k quantum dimensions ---
print("--- 4b: SU(2) Level k=tau(6)=4 Quantum Dimensions ---")
print("  Claim: D^2 = sigma(6) = 12")
print()
print("  SU(2) WZW model at level k has (k+1) primary fields j = 0, 1/2, 1, ..., k/2")
print("  (or equivalently j=0,1,...,k in integer-spin labeling)")
print("  Quantum dimension: d_j = sin((j+1)*pi/(k+2)) / sin(pi/(k+2))")
print()

k = tau  # k = 4
print(f"  k = tau(6) = {k}")
print(f"  k+2 = {k+2}")
print(f"  Number of primary fields = k+1 = {k+1}")
print()

print(f"  {'j':>4} {'d_j':>15} {'d_j^2':>15} {'exact d_j':>20}")
print(f"  {'---':>4} {'---':>15} {'---':>15} {'---':>20}")

total_D2 = 0.0
if HAS_SYMPY:
    from sympy import pi as spi, Rational as Rat
    total_D2_exact = S(0)

for j in range(k + 1):
    num = math.sin((j + 1) * math.pi / (k + 2))
    den = math.sin(math.pi / (k + 2))
    d_j = num / den
    d_j_sq = d_j**2
    total_D2 += d_j_sq

    if HAS_SYMPY:
        d_j_sym = sin((j + 1) * spi / (k + 2)) / sin(spi / (k + 2))
        d_j_sym_simplified = simplify(d_j_sym)
        d_j_sq_sym = simplify(d_j_sym**2)
        total_D2_exact += d_j_sq_sym
        exact_str = f"{d_j_sym_simplified}"
    else:
        exact_str = f"{d_j:.10f}"

    print(f"  {j:>4} {d_j:>15.10f} {d_j_sq:>15.10f} {exact_str:>20}")

print(f"  {'':>4} {'':>15} {'--------':>15}")
print(f"  {'Sum':>4} {'':>15} {total_D2:>15.10f}")
print()

if HAS_SYMPY:
    total_D2_exact_simplified = simplify(total_D2_exact)
    print(f"  D^2 (sympy exact) = {total_D2_exact_simplified}")
    print(f"  D^2 = sigma(6) = 12: {total_D2_exact_simplified == 12}")
else:
    print(f"  D^2 (float) = {total_D2:.10f}")
    print(f"  D^2 = 12: {abs(total_D2 - 12) < 1e-10}")

print()
print(f"  Number of primary fields = {k+1} = sopfr(6) = {sopfr}: {k+1 == sopfr}")
print()

# Verify the ALTERNATIVE formula: D^2 = (k+2)/sin^2(pi/(k+2))
# This formula is WRONG. The correct formula is D^2 = sum of d_j^2.
alt_D2 = (k + 2) / (math.sin(math.pi / (k + 2))**2)
print(f"  CHECKING alternative formula D^2 = (k+2)/sin^2(pi/(k+2)):")
print(f"  = {k+2}/sin^2(pi/{k+2}) = {k+2}/{math.sin(math.pi/(k+2))**2:.10f}")
print(f"  = {alt_D2:.10f}")
print(f"  This formula gives {alt_D2:.4f}, NOT 12.")
print(f"  sin(pi/6) = {math.sin(math.pi/6):.10f}, sin^2(pi/6) = {math.sin(math.pi/6)**2:.10f}")
print(f"  6/0.25 = {6/0.25}")
print(f"  The alternative formula is INCORRECT for total quantum dimension.")
print(f"  The CORRECT result from summing d_j^2 is: {total_D2:.6f} = {round(total_D2)}")
print()


# ============================================================
# SECTION 5: PAGE ENTROPY
# ============================================================
print("=" * 72)
print("SECTION 5: PAGE ENTROPY at d = phi(6) = 2")
print("=" * 72)
print()

# Page formula: S_Page(m, n) = sum_{k=n+1}^{mn} 1/k - (m-1)/(2n)
# where m <= n (smaller Hilbert space dimension m, larger n)
# For a d x d^2 bipartite system: m = d = 2, n = d^2 = 4
# (subsystem A has dim d, subsystem B has dim d^2, total dim = d^3)
# Actually: S_Page(m,n) for m <= n is the average entanglement entropy
# of a random pure state in C^m tensor C^n

d = phi  # d = 2
m_page = d       # smaller dimension = 2
n_page = d**2    # larger dimension = 4 (actually this depends on the bipartition)
# For a bipartite system C^m x C^n with m <= n:
# S_Page = sum_{k=n+1}^{mn} 1/k - (m-1)/(2n)

print(f"  Bipartite system: C^{m_page} x C^{n_page} (m={m_page}, n={n_page})")
print(f"  Page formula: S_Page(m,n) = sum_{{k=n+1}}^{{mn}} 1/k - (m-1)/(2n)")
print()

mn = m_page * n_page  # = 8
harmonic_sum = Fraction(0)
print(f"  Harmonic sum: sum_{{k={n_page+1}}}^{{{mn}}} 1/k")
for k in range(n_page + 1, mn + 1):
    harmonic_sum += Fraction(1, k)
    print(f"    1/{k} = {Fraction(1, k)}")

print(f"  Sum = {harmonic_sum} = {float(harmonic_sum):.10f}")

correction = Fraction(m_page - 1, 2 * n_page)
print(f"  Correction: (m-1)/(2n) = ({m_page}-1)/(2*{n_page}) = {correction} = {float(correction):.10f}")

S_page = harmonic_sum - correction
print(f"  S_Page = {harmonic_sum} - {correction} = {S_page} = {float(S_page):.10f}")
print()

# Check if = 1/3
print(f"  S_Page = 1/3 ? : {S_page == Fraction(1, 3)}")
print(f"  S_Page = {S_page} (exact fraction)")
print(f"  1/3    = {Fraction(1, 3)}")
print(f"  Difference: {float(S_page - Fraction(1,3)):.10f}")
print()

# Also compute for d x d bipartition (m=n=2)
print("  Alternative: C^2 x C^2 bipartition (m=2, n=2):")
m2, n2 = 2, 2
mn2 = m2 * n2
harmonic_sum2 = Fraction(0)
for k in range(n2 + 1, mn2 + 1):
    harmonic_sum2 += Fraction(1, k)
correction2 = Fraction(m2 - 1, 2 * n2)
S_page2 = harmonic_sum2 - correction2
print(f"  S_Page(2,2) = sum_{{k=3}}^{{4}} 1/k - 1/4 = (1/3 + 1/4) - 1/4 = 1/3")
print(f"  S_Page(2,2) = {S_page2} = {float(S_page2):.10f}")
print(f"  S_Page(2,2) = 1/3 ? : {S_page2 == Fraction(1, 3)}")
print()

# For d x d bipartition with d = phi(6) = 2:
# S_Page(2,2) = 1/3 + 1/4 - 1/4 = 1/3 EXACTLY
# 1/3 is the GZ meta fixed point!
print("  RESULT: S_Page(d=2, d=2) = 1/3 EXACTLY")
print("  1/3 = GZ meta fixed point (contraction mapping f(I)=0.7I+0.1)")
print("  phi(6) = 2 -> Page entropy = 1/3 = 1/P1 * phi")
print()


# ============================================================
# SECTION 6: PPT CRITERION
# ============================================================
print("=" * 72)
print("SECTION 6: PPT CRITERION FOR C^2 x C^3")
print("=" * 72)
print()

dim_product = phi * (phi + 1)  # 2 * 3 = 6
print(f"  System: C^phi x C^(phi+1) = C^{phi} x C^{phi+1} = C^2 x C^3")
print(f"  Product dimension = {phi} x {phi+1} = {dim_product} = P1 = n")
print()
print("  Horodecki Theorem (1996):")
print("    PPT (Positive Partial Transpose) is necessary and sufficient")
print("    for detecting entanglement in C^m x C^n when m*n <= 6.")
print("    Specifically: C^2 x C^2 (dim 4) and C^2 x C^3 (dim 6).")
print()
print("  For C^2 x C^3:")
print("    - PPT <=> separable (Horodecki, Phys. Lett. A 223, 1-8, 1996)")
print("    - This is the LARGEST system where PPT completely characterizes entanglement")
print("    - For C^2 x C^4 (dim 8) and higher, PPT is necessary but NOT sufficient")
print("      (bound entangled states exist)")
print()
print(f"  Dimensional claim: 2 x 3 = {dim_product} = P1 = 6")
print(f"  phi(6) x (phi(6)+1) = {phi} x {phi+1} = {dim_product}: VERIFIED")
print()
print("  The fact that PPT is necessary AND sufficient exactly up to")
print("  dimension 6 = P1 is a known theorem. The dimensional threshold")
print("  of the Horodecki criterion equals the first perfect number.")
print()


# ============================================================
# SECTION 7: ISING CFT
# ============================================================
print("=" * 72)
print("SECTION 7: ISING CFT CENTRAL CHARGE")
print("=" * 72)
print()

c_ising = Fraction(1, 2)
P1_over_sigma = Fraction(n, sigma)
one_over_P1 = Fraction(1, n)
c_over_3 = c_ising / 3

print(f"  Ising CFT central charge: c = 1/2")
print(f"  P1/sigma(P1) = {n}/{sigma} = {P1_over_sigma} = {float(P1_over_sigma):.10f}")
print(f"  c = P1/sigma: {c_ising == P1_over_sigma}")
print()
print(f"  Entanglement entropy coefficient = c/3 = {c_over_3}")
print(f"  (Calabrese-Cardy formula: S_EE = (c/3) * ln(L/a))")
print(f"  c/3 = 1/6 = 1/P1 = {one_over_P1}")
print(f"  c/3 = 1/P1: {c_over_3 == one_over_P1}")
print()
print("  For a 1D critical Ising chain of length L:")
print(f"  S_EE = (1/{n}) * ln(L/a)")
print(f"  The entanglement coefficient is exactly 1/P1 = 1/{n}")
print()

# Additional: c for minimal models M(p, p+1)
print("  Minimal model central charges c(p) = 1 - 6/(p(p+1)):")
for p in range(3, 10):
    c_p = Fraction(1) - Fraction(6, p * (p + 1))
    print(f"    M({p},{p+1}): c = 1 - 6/({p}*{p+1}) = 1 - {Fraction(6, p*(p+1))} = {c_p} = {float(c_p):.6f}")
print()
print(f"  The numerator 6 in c = 1 - 6/(p(p+1)) is P1 = {n}")
print(f"  M(3,4) = Ising: c = 1 - 6/12 = 1 - 1/2 = 1/2")
print(f"  The denominator 12 = sigma(6) for the Ising model!")
print()


# ============================================================
# SUMMARY TABLE
# ============================================================
print("=" * 72)
print("SUMMARY OF ALL VERIFICATIONS")
print("=" * 72)
print()
print(f"  {'#':<4} {'Claim':<45} {'Result':<20} {'Status':<10}")
print(f"  {'--':<4} {'-----':<45} {'------':<20} {'------':<10}")

results = [
    ("1a", "45 = sigma*tau - sigma/tau", f"{val_45_check}", "EXACT" if val_45_check == 45 else "FAIL"),
    ("1b", "45 = dim(SO(10))", f"{dim_so10}", "EXACT"),
    ("1c", f"log10(Lambda) = {log10_Lambda:.4f}", f"obs: -122 to -121.5", f"{abs(log10_Lambda-obs_planck2018):.2f} off"),
    ("2a", "DE+DM+B = 1", "1 (algebraic)", "EXACT"),
    ("2b", f"DE = 1-1/pi = {DE_model:.6f}", f"Planck: {DE_planck}", f"{abs(DE_model-DE_planck)/DE_planck*100:.1f}% err"),
    ("2c", f"DM = 5/(6pi) = {DM_model:.6f}", f"Planck: {DM_planck}", f"{abs(DM_model-DM_planck)/DM_planck*100:.1f}% err"),
    ("2d", f"B = 1/(6pi) = {B_model:.6f}", f"Planck: {B_planck}", f"{abs(B_model-B_planck)/B_planck*100:.1f}% err"),
    ("3a", f"S(6) = 0 (perfect number)", f"{S6}", "EXACT"),
    ("3b", f"A = {float(A):.6f}", f"sin(2beta)={sin2beta_model:.4f}", f"vs 0.699"),
    ("3c", f"J = A/sigma^4 = {J_model:.2e}", f"meas: 3.18e-5", f"{abs(J_model-3.18e-5)/3.18e-5*100:.1f}% err"),
    ("3d", f"eps_K = A/(sigma^2*phi) = {eps_K_model:.4e}", f"meas: 2.228e-3", f"{abs(eps_K_model-2.228e-3)/2.228e-3*100:.1f}% err"),
    ("4a", "Tsirelson = 2*sqrt(sigma/P)", "2*sqrt(2)", "TRIVIAL"),
    ("4b", f"D^2(SU(2)_4) = {round(total_D2)}", f"sigma(6) = 12", "EXACT" if abs(total_D2-12)<1e-10 else "FAIL"),
    ("4c", f"Primary fields = {k+1}", f"sopfr(6) = {sopfr}", "EXACT" if k+1==sopfr else "FAIL"),
    ("5a", f"S_Page(2,2) = {S_page2}", "1/3", "EXACT" if S_page2==Fraction(1,3) else "FAIL"),
    ("5b", f"S_Page(2,4) = {S_page}", "1/3?", "EXACT" if S_page==Fraction(1,3) else f"={float(S_page):.6f}"),
    ("6",  "PPT iff sep for C^2 x C^3", "dim=6=P1", "THEOREM"),
    ("7a", "c(Ising) = P1/sigma", "1/2 = 6/12", "EXACT"),
    ("7b", "c/3 = 1/P1", "1/6 = 1/6", "EXACT"),
]

for num, claim, result, status in results:
    print(f"  {num:<4} {claim:<45} {result:<20} {status:<10}")

print()
print("=" * 72)
print("VERIFICATION COMPLETE")
print("=" * 72)
print()

# Final assessment
print("ASSESSMENT:")
print("  Exact results:      1a, 1b, 2a, 3a, 4b, 4c, 5a, 6, 7a, 7b (10)")
print("  Approximate:        1c, 2b, 2c, 2d, 3b, 3c, 3d (7)")
print("  Trivially true:     4a (1)")
print()
print("  Cosmological constant: log10 = {:.4f}, off by {:.2f} from -122".format(
    log10_Lambda, abs(log10_Lambda + 122)))
print("  Dark energy fractions: sum=1 exact, individual errors 1-7%")
print("  CP violation: S(6)=0 is exact; J,eps_K,sin2beta depend on model normalization")
print("  Quantum dimensions: D^2=12=sigma(6) PROVEN EXACT")
print("  Page entropy: S_Page(2,2) = 1/3 EXACT")
print("  PPT criterion: dim 6 = P1 is Horodecki theorem (known)")
print("  Ising CFT: c=1/2=P1/sigma EXACT, c/3=1/6=1/P1 EXACT")
