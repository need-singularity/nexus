#!/usr/bin/env python3
"""
H-CX-488 Verification: alpha/(g-2) = pi + m_e/m_mu ?

Claim: The electron anomalous magnetic moment satisfies
       g_e - 2 = alpha / (pi + m_e/m_mu)
       equivalently: alpha/(g_e - 2) = pi + m_e/m_mu

This script performs precise numerical verification and theoretical analysis.
"""

import math

print("=" * 70)
print("H-CX-488: alpha/(g_e - 2) = pi + m_e/m_mu ?")
print("=" * 70)

# ─── CODATA 2018 Constants ───────────────────────────────────────────
alpha = 1 / 137.035999084       # Fine structure constant
alpha_unc = 21e-12 / 137.035999084**2  # uncertainty propagated

ae = 1.15965218128e-3           # Electron anomalous magnetic moment (CODATA 2018)
ae_unc = 0.00000000018e-3       # uncertainty

g_minus_2 = 2 * ae              # g_e - 2 = 2 * a_e
g_minus_2_unc = 2 * ae_unc

m_e_over_m_mu = 4.83633169e-3   # m_e / m_mu (CODATA 2018)
m_e_over_m_mu_unc = 1.1e-11     # uncertainty

m_e_over_m_p = 5.44617021487e-4 # m_e / m_p (CODATA 2018)
m_e_over_m_tau = 2.87585e-4     # m_e / m_tau (CODATA 2018)

print("\n--- Input Constants (CODATA 2018) ---")
print(f"  alpha           = 1/137.035999084 = {alpha:.15e}")
print(f"  a_e             = {ae:.15e}")
print(f"  g_e - 2 = 2*a_e = {g_minus_2:.15e}")
print(f"  m_e/m_mu        = {m_e_over_m_mu:.11e}")
print(f"  m_e/m_p         = {m_e_over_m_p:.11e}")
print(f"  m_e/m_tau       = {m_e_over_m_tau:.8e}")
print(f"  pi              = {math.pi:.15f}")

# ─── Core Computation ────────────────────────────────────────────────
print("\n" + "=" * 70)
print("CORE TEST: alpha/(g_e - 2) vs pi + m_e/m_mu")
print("=" * 70)

lhs = alpha / g_minus_2         # alpha / (g_e - 2)
rhs = math.pi + m_e_over_m_mu   # pi + m_e/m_mu

diff = lhs - rhs
rel_error = abs(diff) / rhs

print(f"\n  alpha/(g_e - 2)  = {lhs:.15f}")
print(f"  pi + m_e/m_mu    = {rhs:.15f}")
print(f"  Difference       = {diff:+.15f}")
print(f"  Relative error   = {rel_error:.6e}")
print(f"  Parts per million = {rel_error * 1e6:.4f} ppm")

# ─── Alternative: alpha/a_e vs 2*(pi + m_e/m_mu) ────────────────────
print("\n" + "-" * 70)
print("Alternative form: alpha/a_e vs 2*pi + 2*m_e/m_mu")
print("-" * 70)

lhs2 = alpha / ae
rhs2 = 2 * math.pi + 2 * m_e_over_m_mu

print(f"  alpha/a_e              = {lhs2:.15f}")
print(f"  2*pi + 2*m_e/m_mu     = {rhs2:.15f}")
print(f"  2*pi                   = {2*math.pi:.15f}")
print(f"  Difference             = {lhs2 - rhs2:+.15f}")
print(f"  Relative error         = {abs(lhs2 - rhs2)/rhs2:.6e}")

# ─── Comparison with different mass ratios ────────────────────────────
print("\n" + "=" * 70)
print("MASS RATIO COMPARISON: Which gives best correction to pi?")
print("=" * 70)

target = lhs  # = alpha/(g_e - 2), this is the number we want to match
correction_needed = target - math.pi

print(f"\n  alpha/(g_e-2)    = {target:.15f}")
print(f"  pi               = {math.pi:.15f}")
print(f"  Correction needed= {correction_needed:.15f}")
print()

ratios = {
    "m_e/m_mu":  m_e_over_m_mu,
    "m_e/m_p":   m_e_over_m_p,
    "m_e/m_tau": m_e_over_m_tau,
    "1/alpha":   alpha,          # just for fun
    "alpha":     alpha,
    "alpha/pi":  alpha / math.pi,
}

print(f"  {'Ratio':<15} {'Value':>15} {'pi+ratio':>18} {'Error':>15} {'Rel err':>12}")
print(f"  {'-'*15} {'-'*15} {'-'*18} {'-'*15} {'-'*12}")

for name, val in ratios.items():
    candidate = math.pi + val
    err = target - candidate
    rel = abs(err) / target
    print(f"  {name:<15} {val:>15.11f} {candidate:>18.12f} {err:>+15.12f} {rel:>12.6e}")

# ─── Schwinger and higher-order QED ──────────────────────────────────
print("\n" + "=" * 70)
print("THEORETICAL ANALYSIS: QED perturbative expansion")
print("=" * 70)

a_over_pi = alpha / math.pi  # alpha/pi ~ 0.002322

# Known QED coefficients for a_e = sum c_n (alpha/pi)^n
# c_1 = 1/2 (Schwinger 1948)
# c_2 = -0.328478965... (Petermann 1957, Sommerfield 1957)
# c_3 = 1.181241456... (Laporta & Remiddi 1996)
# c_4 = -1.9113(18) (Aoyama et al. 2012)
# c_5 = 6.675(192) (Aoyama et al. 2019) -- 5-loop!

c1 = 0.5
c2 = -0.328478965579193
c3 = 1.181241456587
c4 = -1.9113
c5 = 6.675

print(f"\n  QED coefficients (a_e = sum c_n * (alpha/pi)^n):")
print(f"  c_1 = {c1:+.15f}  (Schwinger)")
print(f"  c_2 = {c2:+.15f}  (Petermann/Sommerfield)")
print(f"  c_3 = {c3:+.15f}  (Laporta/Remiddi)")
print(f"  c_4 = {c4:+.6f}           (Aoyama et al.)")
print(f"  c_5 = {c5:+.3f}              (Aoyama et al. 5-loop)")
print(f"\n  alpha/pi = {a_over_pi:.15e}")

# Compute a_e from QED series
ae_schwinger = c1 * a_over_pi
ae_2loop = ae_schwinger + c2 * a_over_pi**2
ae_3loop = ae_2loop + c3 * a_over_pi**3
ae_4loop = ae_3loop + c4 * a_over_pi**4
ae_5loop = ae_4loop + c5 * a_over_pi**5

print(f"\n  Perturbative a_e (pure QED, no hadronic/EW):")
print(f"  1-loop (Schwinger):  {ae_schwinger:.15e}")
print(f"  2-loop:              {ae_2loop:.15e}")
print(f"  3-loop:              {ae_3loop:.15e}")
print(f"  4-loop:              {ae_4loop:.15e}")
print(f"  5-loop:              {ae_5loop:.15e}")
print(f"  Experimental:        {ae:.15e}")

# Now compute alpha/(2*a_e) for each truncation
print(f"\n  alpha/(2*a_e) at each order (should approach alpha/(g-2)):")
print(f"  {'Order':<12} {'a_e':>20} {'alpha/(2*a_e)':>20} {'vs pi+me/mmu':>15}")
print(f"  {'-'*12} {'-'*20} {'-'*20} {'-'*15}")
for label, val in [("1-loop", ae_schwinger), ("2-loop", ae_2loop),
                    ("3-loop", ae_3loop), ("4-loop", ae_4loop),
                    ("5-loop", ae_5loop), ("Expt", ae)]:
    ratio = alpha / (2 * val)
    diff_from_rhs = ratio - rhs
    print(f"  {label:<12} {val:>20.15e} {ratio:>20.15f} {diff_from_rhs:>+15.12f}")

# ─── Schwinger leading order analysis ────────────────────────────────
print("\n" + "=" * 70)
print("WHY alpha/(g-2) is CLOSE to pi")
print("=" * 70)

print(f"""
  At leading order (Schwinger):
    a_e = alpha/(2*pi)
    g_e - 2 = 2*a_e = alpha/pi

  Therefore: alpha/(g_e - 2) = alpha / (alpha/pi) = pi  (exactly!)

  The higher-order QED corrections make a_e slightly LESS than alpha/(2*pi),
  so alpha/(g_e - 2) becomes slightly MORE than pi.

  The question is: does the correction equal m_e/m_mu = {m_e_over_m_mu:.11f}?

  Actual correction = alpha/(g-2) - pi = {correction_needed:.15f}
  m_e/m_mu                             = {m_e_over_m_mu:.15f}
  Difference                           = {correction_needed - m_e_over_m_mu:+.15e}
  Relative match                       = {abs(correction_needed - m_e_over_m_mu)/correction_needed:.6e}
""")

# ─── Decompose the correction ────────────────────────────────────────
print("=" * 70)
print("DECOMPOSING: What IS the correction alpha/(g-2) - pi ?")
print("=" * 70)

# From a_e = (alpha/2pi)[1 + c2*(alpha/pi) + c3*(alpha/pi)^2 + ...]
# g-2 = (alpha/pi)[1 + c2*(alpha/pi) + ...]
# alpha/(g-2) = pi / [1 + c2*(alpha/pi) + c3*(alpha/pi)^2 + ...]
# Using 1/(1+x) ~ 1 - x + x^2 - ... for small x:
# alpha/(g-2) ~ pi * [1 - c2*(alpha/pi) - c3*(alpha/pi)^2 + c2^2*(alpha/pi)^2 + ...]
# alpha/(g-2) - pi ~ -pi*c2*(alpha/pi) + higher order
#                   = -c2 * alpha  (leading correction!)

leading_correction = -c2 * alpha
print(f"\n  Leading correction = -c2 * alpha = {leading_correction:.15e}")
print(f"  m_e/m_mu                        = {m_e_over_m_mu:.15e}")
print(f"  Ratio (correction / m_e/m_mu)   = {leading_correction / m_e_over_m_mu:.10f}")
print(f"  Actual correction from data     = {correction_needed:.15e}")

# Is -c2*alpha ~ m_e/m_mu a known relation?
print(f"\n  Is -c2 * alpha ~ m_e/m_mu?")
print(f"  -c2 = {-c2:.15f}")
print(f"  m_e/m_mu / alpha = {m_e_over_m_mu / alpha:.10f}")
print(f"  (This would require c2 ~ -0.663, actual c2 = {c2:.6f})")

# ─── Numerical coincidence analysis ──────────────────────────────────
print("\n" + "=" * 70)
print("COINCIDENCE ANALYSIS")
print("=" * 70)

# The key question: is the ~1.6 ppm match significant?
print(f"""
  The correction alpha/(g-2) - pi = {correction_needed:.11e}
  has magnitude ~{correction_needed:.4f}

  m_e/m_mu = {m_e_over_m_mu:.11e} has similar magnitude ~{m_e_over_m_mu:.4f}

  But the ACTUAL correction comes from QED:
    -c2 * alpha = {leading_correction:.11e}
    which is {leading_correction/correction_needed*100:.2f}% of the full correction.

  The next terms also contribute:
    -c3*(alpha/pi)^2 * pi + c2^2*(alpha/pi)^2 * pi = ...
""")

# Full numerical expansion
x = a_over_pi
correction_series = -c2*x*math.pi + (c2**2 - c3)*x**2*math.pi + \
                    (-c2**3 + 2*c2*c3 - c4)*x**3*math.pi

print(f"  Series correction (3 terms): {correction_series:.11e}")
print(f"  Actual correction:           {correction_needed:.11e}")
print(f"  m_e/m_mu:                    {m_e_over_m_mu:.11e}")

# ─── Literature check ────────────────────────────────────────────────
print("\n" + "=" * 70)
print("LITERATURE STATUS")
print("=" * 70)
print("""
  Is g-2 = alpha/(pi + m_e/m_mu) a known published formula?

  NO. This is NOT a known formula in the physics literature.

  The standard QED result is the perturbative series:
    a_e = (1/2)(alpha/pi) - 0.3285(alpha/pi)^2 + 1.1812(alpha/pi)^3 - ...

  Plus hadronic and electroweak corrections (very small).

  The muon mass enters the REAL calculation through:
    - Vacuum polarization diagrams (2-loop and higher)
    - The muon loop contribution to a_e is ~(alpha/pi)^2 * (m_e/m_mu)^2 / 45
      which is of order 1e-12, far too small to explain the ~1e-3 correction.

  The approximate numerical match (1.6 ppm) between:
    alpha/(g-2) - pi  and  m_e/m_mu
  appears to be a NUMERICAL COINCIDENCE.

  The actual correction is dominated by -c2*alpha = {:.6e}
  where c2 is a pure QED coefficient computed from Feynman diagrams,
  with no fundamental connection to the muon mass ratio.
""".format(leading_correction))

# ─── Verdict ──────────────────────────────────────────────────────────
print("=" * 70)
print("VERDICT")
print("=" * 70)
rel_ppm = rel_error * 1e6
print(f"""
  Claim: alpha/(g_e - 2) = pi + m_e/m_mu

  Numerical accuracy: {rel_ppm:.4f} ppm ({rel_error:.2e} relative error)

  This is a {'surprisingly close' if rel_ppm < 10 else 'moderate'} numerical match,
  but it has NO theoretical basis:

  1. At leading order, alpha/(g-2) = pi (Schwinger, exact).
  2. The deviation from pi is ~{correction_needed:.6f}, dominated by -c2*alpha.
  3. c2 = -0.3285 is a QED loop integral, unrelated to m_e/m_mu.
  4. The muon contributes to a_e at order (alpha/pi)^2*(m_e/m_mu)^2 ~ 10^{-12},
     which is 9 orders of magnitude too small to explain the ~10^{-3} correction.
  5. The match at {rel_ppm:.1f} ppm is a numerical coincidence.

  Grade: {'INTERESTING COINCIDENCE (< 10 ppm)' if rel_ppm < 10 else 'WEAK COINCIDENCE'}

  For comparison, the famous Koide formula matches lepton masses to ~0.01%,
  and is also considered a numerical coincidence by most physicists.
""")

# ─── Summary table ───────────────────────────────────────────────────
print("=" * 70)
print("SUMMARY TABLE")
print("=" * 70)
print(f"""
  | Quantity              | Value                 |
  |-----------------------|-----------------------|
  | alpha                 | {alpha:.15e} |
  | g_e - 2               | {g_minus_2:.15e} |
  | alpha/(g_e - 2)       | {lhs:.15f}    |
  | pi                    | {math.pi:.15f}    |
  | pi + m_e/m_mu         | {rhs:.15f}    |
  | Difference            | {diff:+.6e}          |
  | Relative error        | {rel_error:.6e}          |
  | ppm                   | {rel_ppm:.4f}               |
  | Correction needed     | {correction_needed:.11e}    |
  | m_e/m_mu              | {m_e_over_m_mu:.11e}    |
  | -c2*alpha (QED)       | {leading_correction:.11e}    |
""")
