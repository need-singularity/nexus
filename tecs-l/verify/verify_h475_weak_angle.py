"""
H-CX-475: sin^2(theta_W) x N_gen ~ ln(2)
=========================================
Claim: The weak mixing angle times the number of fermion generations
       equals approximately 1 bit of information.

sin^2(theta_W) = 0.23122, N_gen = 3, product = 0.69366
vs ln(2) = 0.69315, error = 0.074%.

Verification:
  1. High precision check with multiple sin^2(theta_W) values
  2. Literature search for known observation
  3. Texas Sharpshooter test
  4. Physical interpretation
  5. Landauer limit check (2*ln(2))
"""

import math
import random
from itertools import combinations

# ============================================================
# 1. HIGH PRECISION CHECK
# ============================================================
print("=" * 70)
print("H-CX-475: sin^2(theta_W) x N_gen vs ln(2)")
print("=" * 70)

ln2 = math.log(2)
N_gen = 3
predicted_sin2 = ln2 / N_gen

print(f"\nTarget: ln(2) = {ln2:.10f}")
print(f"Predicted sin^2(theta_W) = ln(2)/3 = {predicted_sin2:.10f}")

# Three standard values of sin^2(theta_W)
schemes = [
    ("On-shell (at M_Z)",       0.22337, 0.00010),
    ("MS-bar (at M_Z) [PDG]",   0.23122, 0.00003),
    ("Low energy (MS-bar)",     0.23857, 0.00005),
]

print(f"\n{'Scheme':<30s} {'sin^2_W':>12s} {'3*sin^2_W':>12s} {'ln(2)':>12s} {'Error%':>10s} {'sigma':>8s}")
print("-" * 90)

for name, val, unc in schemes:
    product = val * N_gen
    err_pct = abs(product - ln2) / ln2 * 100
    diff = abs(val - predicted_sin2)
    sigma = diff / unc if unc > 0 else float('inf')
    print(f"{name:<30s} {val:>12.5f} {product:>12.5f} {ln2:>12.5f} {err_pct:>10.4f} {sigma:>8.1f}")

print(f"\nClosest match analysis:")
print(f"  MS-bar value: 0.23122 +/- 0.00003")
print(f"  Prediction:   {predicted_sin2:.5f}")
print(f"  Difference:   {0.23122 - predicted_sin2:.5f}")
print(f"  Sigma:        {(0.23122 - predicted_sin2) / 0.00003:.1f} sigma")
print(f"  --> The difference is ~5.7 sigma: statistically EXCLUDED as exact.")

# ============================================================
# 2. KNOWN IN LITERATURE?
# ============================================================
print("\n" + "=" * 70)
print("2. LITERATURE CHECK")
print("=" * 70)
print("""
Known relations involving sin^2(theta_W):
  - Tree-level SM prediction: sin^2(theta_W) = 3/8 = 0.375 (GUT scale)
  - Radiative corrections bring it to ~0.231 at M_Z
  - Weinberg's original: sin^2(theta_W) = e^2 / g^2 (gauge coupling ratio)

Is sin^2(theta_W) * N_gen = ln(2) known?
  - NOT a standard relation in particle physics literature.
  - The number 3 generations is unexplained in the SM.
  - No known information-theoretic derivation connects theta_W to ln(2).
  - The GUT prediction 3/8 gives 3*(3/8) = 9/8 = 1.125, NOT ln(2).
  - So the near-match is specific to the LOW-ENERGY measured value.
  - This makes it more likely numerological: the RG flow to M_Z gives
    a number that happens to be near ln(2)/3.

Note: sin^2(theta_W) runs with energy. At the GUT scale ~10^16 GeV,
sin^2(theta_W) = 3/8, and 3*(3/8) = 1.125 != ln(2).
The match only works at the Z-mass scale.
""")

# ============================================================
# 3. TEXAS SHARPSHOOTER TEST
# ============================================================
print("=" * 70)
print("3. TEXAS SHARPSHOOTER TEST")
print("=" * 70)

# Pool of particle physics / QFT constants that could plausibly be combined
constants = {
    "sin2_W":       0.23122,
    "alpha_em":     1/137.036,
    "alpha_s":      0.1179,
    "N_gen":        3,
    "N_color":      3,
    "N_quarks":     6,
    "N_leptons":    6,
    "N_fermions":   12,     # per generation: 2 quarks + 2 leptons (x3 colors for quarks -> but 12 Dirac)
    "1/alpha_em":   137.036,
    "sin2_W_onshell": 0.22337,
    "m_W/m_Z":     80.377 / 91.1876,  # cos(theta_W)
    "m_e/m_mu":    0.511 / 105.66,
    "m_mu/m_tau":  105.66 / 1776.86,
    "pi":          math.pi,
    "e":           math.e,
    "2":           2,
    "3":           3,
    "5":           5,
    "6":           6,
    "1/2":         0.5,
    "1/3":         1/3,
    "1/6":         1/6,
}

# Targets: well-known mathematical constants
targets = {
    "ln(2)":       math.log(2),
    "ln(3)":       math.log(3),
    "1/e":         1/math.e,
    "pi/4":        math.pi/4,
    "sqrt(2)":     math.sqrt(2),
    "sqrt(3)":     math.sqrt(3),
    "1":           1.0,
    "phi":         (1 + math.sqrt(5)) / 2,
    "pi":          math.pi,
    "e":           math.e,
    "gamma":       0.5772156649,  # Euler-Mascheroni
    "pi^2/6":      math.pi**2/6,
    "2*ln(2)":     2*math.log(2),  # Landauer
    "1/2":         0.5,
    "1/3":         1/3,
    "1/4":         0.25,
    "2/3":         2/3,
    "3/2":         1.5,
}

threshold_pct = 0.074  # The claimed match quality

print(f"\nSearching all pairwise products of {len(constants)} constants")
print(f"against {len(targets)} mathematical targets")
print(f"Threshold: {threshold_pct}% relative error")
print()

matches = []
const_names = list(constants.keys())

# Products a*b
for i, (n1, v1) in enumerate(constants.items()):
    for j, (n2, v2) in enumerate(constants.items()):
        if j <= i:
            continue
        product = v1 * v2
        for tname, tval in targets.items():
            if tval == 0:
                continue
            err = abs(product - tval) / abs(tval) * 100
            if err < threshold_pct:
                matches.append((n1, n2, "*", product, tname, tval, err))

# Also check ratios a/b
for i, (n1, v1) in enumerate(constants.items()):
    for j, (n2, v2) in enumerate(constants.items()):
        if j == i or v2 == 0:
            continue
        ratio = v1 / v2
        for tname, tval in targets.items():
            if tval == 0:
                continue
            err = abs(ratio - tval) / abs(tval) * 100
            if err < threshold_pct:
                matches.append((n1, n2, "/", ratio, tname, tval, err))

# Filter out trivial (involving pi matching pi, e matching e, etc.)
nontrivial = []
for m in matches:
    n1, n2, op, val, tname, tval, err = m
    # Skip if one of the operands IS the target
    trivial = False
    if tname == "pi" and ("pi" in n1 or "pi" in n2):
        trivial = True
    if tname == "e" and ("e" == n1 or "e" == n2):
        trivial = True
    if tname == "1" and n1 == n2 and op == "/":
        trivial = True
    # Skip integer * integer = integer target
    try:
        if float(n1).is_integer() and float(n2).is_integer():
            trivial = True
    except:
        pass
    if not trivial:
        nontrivial.append(m)

print(f"Total matches within {threshold_pct}%: {len(matches)} (raw), {len(nontrivial)} (nontrivial)")
print(f"\nAll nontrivial matches:")
print(f"{'Expr':<35s} {'Value':>12s} {'Target':>10s} {'TgtVal':>12s} {'Err%':>8s}")
print("-" * 80)

for m in sorted(nontrivial, key=lambda x: x[6]):
    n1, n2, op, val, tname, tval, err = m
    expr = f"{n1} {op} {n2}"
    print(f"{expr:<35s} {val:>12.6f} {tname:>10s} {tval:>12.6f} {err:>8.4f}")

# Count how many involve sin2_W
sin2_matches = [m for m in nontrivial if "sin2_W" in m[0] or "sin2_W" in m[1]]
print(f"\nOf these, {len(sin2_matches)} involve sin2_W (MS-bar)")

# Total number of pairwise comparisons
n_const = len(constants)
n_targ = len(targets)
n_products = n_const * (n_const - 1) // 2
n_ratios = n_const * (n_const - 1)
n_total = (n_products + n_ratios) * n_targ
print(f"\nTotal comparisons: ({n_products} products + {n_ratios} ratios) x {n_targ} targets = {n_total}")
print(f"Expected random matches at {threshold_pct}%: ~{n_total * threshold_pct/100 * 2:.1f}")
print(f"  (assuming uniform log-distribution, prob ~ 2*threshold/100)")

# ============================================================
# 4. PHYSICAL INTERPRETATION
# ============================================================
print("\n" + "=" * 70)
print("4. PHYSICAL INTERPRETATION")
print("=" * 70)
print("""
IF sin^2(theta_W) * N_gen = ln(2) were exact, it would imply:

  - The total "weak charge fraction" summed over all generations = ln(2)
  - ln(2) = 1 bit (in natural units): the information content of a binary choice

Physical assessment:
  AGAINST:
    1. sin^2(theta_W) RUNS with energy. At GUT scale it's 3/8, not ln(2)/3.
       An "information-theoretic" relation should be scale-independent.
    2. The match is 5.7 sigma OFF at M_Z -- statistically excluded as exact.
    3. N_gen = 3 is not derived from sin^2(theta_W) in the Standard Model.
       They are independent parameters.
    4. No known mechanism connects gauge coupling ratios to information theory.
    5. The total weak charge is not simply sin^2(theta_W) * N_gen.
       Each fermion has different T3 and Q, so the coupling varies.

  FOR (weak):
    1. The numerical proximity IS striking (0.074% at M_Z).
    2. M_Z is a natural scale (mass of the Z boson).
    3. If there were an information-theoretic constraint on the SM,
       it might naturally apply at the EW symmetry breaking scale.

Verdict: Likely numerological. The 5.7-sigma deviation rules out exactness,
         and the energy-scale dependence undermines any deep connection.
""")

# ============================================================
# 5. LANDAUER LIMIT CHECK
# ============================================================
print("=" * 70)
print("5. LANDAUER LIMIT: sin^2(theta_W) * N_gen * 2 vs 2*ln(2)")
print("=" * 70)

val_2ln2 = 2 * ln2
product_2 = 0.23122 * 3 * 2
err_2 = abs(product_2 - val_2ln2) / val_2ln2 * 100

print(f"  2 * sin^2(theta_W) * N_gen = {product_2:.6f}")
print(f"  2 * ln(2) = kT_Landauer    = {val_2ln2:.6f}")
print(f"  Error: {err_2:.4f}%")
print(f"  (Same relative error as original claim -- just multiplied by 2)")
print(f"  This adds no new information.")

# ============================================================
# 6. MONTE CARLO: PROBABILITY OF FINDING SUCH A MATCH
# ============================================================
print("\n" + "=" * 70)
print("6. MONTE CARLO: How often does a random constant match ln(2)/N?")
print("=" * 70)

random.seed(42)
n_trials = 1_000_000
count = 0
# sin^2(theta_W) at M_Z is constrained to [0, 0.5] by definition
# (it's a mixing angle, sin^2 in [0,1], but gauge structure constrains it)
# Use uniform [0.1, 0.5] as a reasonable range for a mixing parameter

for _ in range(n_trials):
    x = random.uniform(0.1, 0.5)
    # Check x*N for N in {2, 3, 4, 5} against ln(2), ln(3), 1/e, etc.
    for N in [2, 3, 4, 5]:
        prod = x * N
        for tval in [ln2, math.log(3), 1/math.e, math.pi/4, 0.5]:
            if abs(prod - tval) / tval < threshold_pct / 100:
                count += 1
                break
        else:
            continue
        break

prob = count / n_trials
print(f"  Random sin^2 in [0.1, 0.5], multiplied by N in {{2,3,4,5}},")
print(f"  checked against 5 common targets within {threshold_pct}%:")
print(f"  Match probability = {prob:.4f} ({prob*100:.2f}%)")
print(f"  ({count} matches in {n_trials:,} trials)")

# ============================================================
# FINAL VERDICT
# ============================================================
print("\n" + "=" * 70)
print("FINAL VERDICT")
print("=" * 70)
print(f"""
  Observation:  sin^2(theta_W) * 3 = {0.23122*3:.5f} vs ln(2) = {ln2:.5f}
  Error:        0.074% -- impressively close
  Sigma:        5.7 sigma from exact -- statistically EXCLUDED

  Grading Criteria:
    - Arithmetic: CORRECT (the numbers do multiply to near ln(2))
    - Exactness:  EXCLUDED at 5.7 sigma
    - Scale-dep:  sin^2(theta_W) runs with energy -> not universal
    - Literature: NOT a known relation
    - Texas test:  Multiple similar-quality matches exist among constants

  Grade: 🟧 (Approximation, striking but not exact, scale-dependent)

  The 0.074% match at M_Z is numerically interesting but:
    (a) excluded as exact at 5.7 sigma
    (b) only works at one energy scale
    (c) not uniquely special in the Texas Sharpshooter test

  Golden Zone dependency: YES (if interpreted as information-theoretic)
""")
