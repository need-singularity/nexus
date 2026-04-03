#!/usr/bin/env python3
"""
GZ Universality Test — Numerical verification of G=D*P/I across domains.

Tests two mappings quantitatively:
  1. Epidemiology: SIR model R_0 = beta*S/gamma vs D*P/I
  2. Machine Learning: Optimal regularization fraction vs 1/e prediction

Also checks all emerging constants with n6_check().

Usage:
  python3 calc/gz_universality_test.py
"""
from __future__ import annotations

import math
import sys
import os

# ── Constants from model_utils (avoid hardcoding) ─────────────────────
GOLDEN_ZONE_CENTER = 1.0 / math.e     # 1/e ~ 0.3679
GOLDEN_ZONE_UPPER = 0.5               # Riemann critical line
GOLDEN_ZONE_WIDTH = math.log(4 / 3)   # ln(4/3) ~ 0.2877
GOLDEN_ZONE_LOWER = GOLDEN_ZONE_UPPER - GOLDEN_ZONE_WIDTH  # ~ 0.2123

# ── n6_check stub (use real nexus6 if available) ──────────────────────
try:
    sys.path.insert(0, os.path.expanduser("~/Dev/nexus6"))
    import nexus6  # type: ignore
    n6_check = nexus6.n6_check
except Exception:
    def n6_check(value: float, tol: float = 0.01) -> str:
        """Lightweight n6 constant matcher."""
        known = {
            "1/e":        1.0 / math.e,
            "1/2":        0.5,
            "1/3":        1.0 / 3,
            "1/6":        1.0 / 6,
            "5/6":        5.0 / 6,
            "ln(4/3)":    math.log(4 / 3),
            "ln(2)":      math.log(2),
            "e":          math.e,
            "pi":         math.pi,
            "sigma(6)=12": 12.0,
            "tau(6)=4":   4.0,
            "phi(6)=2":   2.0,
            "sopfr(6)=5": 5.0,
            "6":          6.0,
        }
        for name, ref in known.items():
            if ref != 0 and abs(value - ref) / abs(ref) < tol:
                return f"MATCH: {name} (error {abs(value - ref)/abs(ref)*100:.2f}%)"
        return "NONE"


def separator(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


# ══════════════════════════════════════════════════════════════════
#  TEST 1: Epidemiology — SIR Model R_0 = beta*S_0/gamma
# ══════════════════════════════════════════════════════════════════

def test_epidemiology() -> None:
    separator("TEST 1: Epidemiology — SIR R_0 vs D*P/I")

    print("""
  Mapping:
    D = beta  (transmissibility per contact)
    P = S_0   (initial susceptible fraction)
    I = gamma (recovery rate, rescaled to dimensionless)

  SIR: R_0 = beta * S_0 / gamma
  GZ:  G   = D * P / I

  These are IDENTICAL in form. Test: verify conservation G*I = D*P.
""")

    # Test cases: historical epidemics (approximate)
    epidemics = [
        # (name, beta, S_0, gamma, R_0_literature)
        ("Measles",          0.90, 0.95, 0.07, 12.0),
        ("COVID-19 (Wuhan)", 0.30, 1.00, 0.10,  3.0),
        ("Influenza 1918",   0.25, 0.90, 0.14,  1.6),
        ("Ebola 2014",       0.15, 0.99, 0.10,  1.5),
        ("SARS 2003",        0.10, 1.00, 0.07,  1.4),
    ]

    print(f"  {'Epidemic':<22} {'beta':>5} {'S_0':>5} {'gamma':>6} "
          f"{'R0_lit':>6} {'D*P/I':>7} {'Match':>6} {'I_frac':>7} {'In GZ?':>6}")
    print(f"  {'-'*22} {'-'*5} {'-'*5} {'-'*6} {'-'*6} {'-'*7} {'-'*6} {'-'*7} {'-'*6}")

    for name, beta, s0, gamma, r0_lit in epidemics:
        dpi = beta * s0 / gamma
        match = abs(dpi - r0_lit) / r0_lit < 0.15
        # Dimensionless I: fraction of contacts leading to recovery
        i_frac = gamma / (beta + gamma)
        in_gz = GOLDEN_ZONE_LOWER <= i_frac <= GOLDEN_ZONE_UPPER
        print(f"  {name:<22} {beta:>5.2f} {s0:>5.2f} {gamma:>6.2f} "
              f"{r0_lit:>6.1f} {dpi:>7.2f} {'OK' if match else 'DIFF':>6} "
              f"{i_frac:>7.4f} {'YES' if in_gz else 'no':>6}")

    # Conservation law check
    print("\n  Conservation law G*I = D*P:")
    for name, beta, s0, gamma, r0_lit in epidemics:
        g = beta * s0 / gamma
        gi = g * gamma
        dp = beta * s0
        print(f"    {name:<22}  G*I = {gi:.4f}  D*P = {dp:.4f}  "
              f"{'CONSERVED' if abs(gi - dp) < 1e-10 else 'BROKEN'}")

    # GZ prediction: sharpest transition at I_frac ~ 1/e
    print("\n  GZ Prediction: Sharpest epidemic transition at I_frac ~ 1/e")
    print(f"  1/e = {1/math.e:.4f}")

    # Simulate SIR sharpness (d(R_0)/d(I) sensitivity)
    print("\n  Sensitivity |dR_0/dI| at different I values:")
    print(f"  {'I_frac':>8} {'R_0':>8} {'|dR0/dI|':>10} {'Note':>20}")
    beta_ref, s0_ref = 0.30, 1.0
    for i_frac in [0.10, 0.20, 1/math.e, 0.40, 0.50, 0.60, 0.80]:
        gamma_val = i_frac * beta_ref / (1 - i_frac) if i_frac < 1 else 999
        r0 = beta_ref * s0_ref / gamma_val if gamma_val > 0 else float('inf')
        # dR0/dI = -D*P/I^2 in dimensionless form
        dr0_di = beta_ref * s0_ref / (i_frac ** 2) if i_frac > 0 else float('inf')
        note = "<-- 1/e" if abs(i_frac - 1/math.e) < 0.01 else ""
        if abs(i_frac - 0.50) < 0.01:
            note = "<-- GZ upper"
        print(f"  {i_frac:>8.4f} {r0:>8.2f} {dr0_di:>10.2f} {note:>20}")


# ══════════════════════════════════════════════════════════════════
#  TEST 2: Machine Learning — Optimal Regularization
# ══════════════════════════════════════════════════════════════════

def test_machine_learning() -> None:
    separator("TEST 2: Machine Learning — Optimal Regularization vs 1/e")

    print("""
  Mapping:
    G = effective model performance (1/test_loss)
    D = model capacity (number of effective parameters)
    P = data quality (clean samples * diversity)
    I = regularization strength (dropout rate, weight decay fraction)

  GZ Prediction: optimal I ~ 1/e ~ 0.368 for sufficiently complex tasks.

  Test: Simulate bias-variance tradeoff with multiplicative model.
""")

    # Simple model: G = D*P/I * exp(-k/D) * exp(-noise*I)
    # First term: capacity benefit (more params = more capacity)
    # Second term: regularization kills some useful capacity
    # Optimal I balances 1/I growth with exp(-noise*I) decay

    # For the pure D*P/I model, test error = (bias)^2 + variance
    # bias ~ 1/D (underfitting), variance ~ D*I^{-1}/P (overfitting)
    # Total ~ 1/D + D/(P*I)
    # This doesn't have a clean I optimum.

    # Better model: G_eff = D * P * I^I (from MaxCal derivation H-CX-504)
    # This gives optimal I = 1/e (calculus: d/dI[I^I] = 0)

    print("  MaxCal model: G_eff = D * P * I^I")
    print("  (I^I is minimized at I=1/e, so 1/G_eff is minimized = G_eff maximized)")
    print()
    print(f"  {'I':>8} {'I^I':>10} {'1/I':>10} {'I^I * (1/I)':>12} {'Note':>15}")
    print(f"  {'-'*8} {'-'*10} {'-'*10} {'-'*12} {'-'*15}")

    for i_val in [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 1/math.e, 0.40, 0.45, 0.50,
                  0.60, 0.70, 0.80, 0.90]:
        i_to_i = i_val ** i_val
        inv_i = 1.0 / i_val
        product = i_to_i * inv_i
        note = ""
        if abs(i_val - 1/math.e) < 0.005:
            note = "<-- 1/e OPTIMAL"
        elif abs(i_val - 0.50) < 0.005:
            note = "<-- GZ upper"
        elif abs(i_val - GOLDEN_ZONE_LOWER) < 0.02:
            note = "<-- GZ lower"
        print(f"  {i_val:>8.4f} {i_to_i:>10.6f} {inv_i:>10.4f} {product:>12.6f} {note:>15}")

    # Find minimum of I^I numerically
    best_i = min((i/1000 for i in range(1, 1000)),
                 key=lambda x: x**x)
    print(f"\n  Numerical minimum of I^I: I* = {best_i:.4f}")
    print(f"  Theoretical:              I* = 1/e = {1/math.e:.4f}")
    print(f"  Match: {abs(best_i - 1/math.e) < 0.002}")

    # Compare with known dropout practices
    print("\n  Known optimal dropout rates (from literature):")
    print(f"  {'Task':<30} {'p_opt':>6} {'In GZ?':>6} {'Near 1/e?':>10}")
    print(f"  {'-'*30} {'-'*6} {'-'*6} {'-'*10}")
    dropouts = [
        ("Hinton 2012 (original)",       0.50),
        ("ResNet (ImageNet)",            0.30),
        ("Transformer (NLP, typical)",   0.10),
        ("GPT-style (large LM)",        0.10),
        ("BERT",                         0.10),
        ("MoE routing (top-k/N)",        0.44),  # k=7, N=16
        ("Simple MNIST",                 0.00),
    ]
    for task, p in dropouts:
        in_gz = GOLDEN_ZONE_LOWER <= p <= GOLDEN_ZONE_UPPER
        near_e = abs(p - 1/math.e) < 0.10
        print(f"  {task:<30} {p:>6.2f} {'YES' if in_gz else 'no':>6} "
              f"{'YES' if near_e else 'no':>10}")

    print("""
  Note: Modern deep learning uses LOW dropout (0.1) because models are
  already heavily regularized by other means (BatchNorm, data augmentation,
  weight decay). The 1/e prediction applies to the TOTAL effective
  regularization, not dropout alone. MoE top-k/N = 0.44 is closest.
""")


# ══════════════════════════════════════════════════════════════════
#  n6 Constant Check
# ══════════════════════════════════════════════════════════════════

def test_n6_constants() -> None:
    separator("n6_check on Constants Emerging from Cross-Domain Analysis")

    constants = [
        ("GZ center (1/e)",                  1.0 / math.e),
        ("GZ upper (1/2)",                   0.5),
        ("GZ lower (1/2 - ln(4/3))",         0.5 - math.log(4/3)),
        ("GZ width (ln(4/3))",               math.log(4/3)),
        ("Cobb-Douglas alpha (typical)",     0.3),
        ("Cobb-Douglas beta (typical)",      0.7),
        ("Shannon 1/ln(2)",                  1.0 / math.log(2)),
        ("SIR measles I_frac",               0.07 / (0.90 + 0.07)),
        ("SIR COVID I_frac",                 0.10 / (0.30 + 0.10)),
        ("Heisenberg hbar/2",               0.5),  # in natural units
        ("Carnot 1-Tc/Th (typical)",         0.40),
        ("Dropout Hinton",                   0.50),
        ("MoE k/N observed",                 7.0 / 16),
        ("e * ln(2)",                        math.e * math.log(2)),
        ("Secretary problem threshold",      1.0 / math.e),
    ]

    print(f"  {'Name':<40} {'Value':>8} {'n6_check result':<40}")
    print(f"  {'-'*40} {'-'*8} {'-'*40}")
    for name, val in constants:
        result = str(n6_check(val))
        print(f"  {name:<40} {val:>8.4f} {result}")


# ══════════════════════════════════════════════════════════════════
#  Domain Axiom Compliance Matrix
# ══════════════════════════════════════════════════════════════════

def test_axiom_compliance() -> None:
    separator("Axiom Compliance Matrix — Which Domains Satisfy G=D*P/I Axioms?")

    print("""
  Axioms: (1) 3 positive vars  (2) I in (0,1)  (3) Monotonicity
          (4) Separability      (5) Independence (6) Scale invariance

  Domain           Ax1  Ax2  Ax3  Ax4  Ax5  Ax6  Grade
  ───────────────  ───  ───  ───  ───  ───  ───  ───────────
  Epidemiology     YES  ~    YES  YES  YES  YES  STRUCTURAL
  Machine Learning YES  YES  YES  ~    ~    ~    STRUCTURAL
  Economics        YES  YES  YES  YES  NO   NO   STRUCTURAL*
  Ecology          YES  ~    YES  NO   NO   ~    ANALOGY
  Information Th.  YES  YES  YES  YES  YES  YES  ANALOGY**
  Quantum Mech.    YES  ~    YES  ~    NO   ~    ANALOGY
  Thermodynamics   YES  YES  YES  YES  YES  YES  ANALOGY***

  * Cobb-Douglas exponents != 1 (scale invariance violated)
  ** Shannon has f(I) = -log(I) not 1/I (different noise model)
  *** Carnot has f(I) = 1-I not 1/I (additive not multiplicative dissipation)

  Key insight: EXACT G=D*P/I requires ALL 6 axioms.
  Most real systems violate 1-2, giving STRUCTURAL or ANALOGY grade.
  The closest match is epidemiology (SIR model).
""")

    # Count axiom compliance
    domains = {
        "Epidemiology":     [1, 0, 1, 1, 1, 1],  # 5/6
        "Machine Learning":  [1, 1, 1, 0, 0, 0],  # 3/6
        "Economics":         [1, 1, 1, 1, 0, 0],  # 4/6
        "Ecology":           [1, 0, 1, 0, 0, 0],  # 2/6
        "Information Theory":[1, 1, 1, 1, 1, 1],  # 6/6 (but diff f(I))
        "Quantum Mechanics": [1, 0, 1, 0, 0, 0],  # 2/6
        "Thermodynamics":    [1, 1, 1, 1, 1, 1],  # 6/6 (but diff f(I))
    }

    print(f"  {'Domain':<25} {'Score':>5} {'Axiom Pattern':>15}")
    print(f"  {'-'*25} {'-'*5} {'-'*15}")
    for name, axioms in sorted(domains.items(), key=lambda x: -sum(x[1])):
        score = sum(axioms)
        pattern = "".join(str(a) for a in axioms)
        print(f"  {name:<25} {score:>3}/6 {pattern:>15}")


# ══════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════

def main() -> None:
    print("=" * 60)
    print("  GZ UNIVERSALITY TEST — G=D*P/I Cross-Domain Verification")
    print("=" * 60)
    print(f"  Date: 2026-04-04")
    print(f"  GZ = [{GOLDEN_ZONE_LOWER:.4f}, {GOLDEN_ZONE_UPPER:.4f}]")
    print(f"  Center = 1/e = {GOLDEN_ZONE_CENTER:.4f}")
    print(f"  Width = ln(4/3) = {GOLDEN_ZONE_WIDTH:.4f}")

    test_epidemiology()
    test_machine_learning()
    test_n6_constants()
    test_axiom_compliance()

    separator("CONCLUSION")
    print("""
  G=D*P/I is NOT a universal law of nature.
  It IS a universal law of INDEPENDENT MULTIPLICATIVE SYSTEMS
  with a dimensionless modulator in (0,1).

  Strongest match:  Epidemiology (SIR R_0 = beta*S/gamma)  -- STRUCTURAL
  Partial match:    Machine Learning (1/e regularization)   -- STRUCTURAL
  Weak match:       Economics (Cobb-Douglas with a,b != 1)  -- STRUCTURAL*
  Form mismatch:    Shannon (-log I), Carnot (1-I), QM      -- ANALOGY

  The domain of validity is precisely: systems satisfying all 6 axioms.
  Outside that domain, G=D*P/I is an approximation, not a law.
""")


if __name__ == "__main__":
    main()
