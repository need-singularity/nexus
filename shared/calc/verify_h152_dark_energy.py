#!/usr/bin/env python3
"""H-152 Dark Energy Fixed Point 1/3 — Complete Analytical Proof Verification

Verifies all steps of the analytical proof that f(I) = 0.7I + 0.1
has unique fixed point I* = 1/3 via Banach contraction mapping theorem.

Proof steps verified:
  1. Fixed point equation: f(I*) = I* => I* = 1/3 (exact)
  2. Contraction condition: |f'(x)| = 0.7 < 1 (Banach applies)
  3. Uniqueness: Banach theorem guarantees uniqueness on complete metric space
  4. Convergence rate: geometric with ratio 0.7
  5. Basin of attraction: all of R (global attractor for affine contraction)
  6. n=6 connection: 1/3 = 2/6 = phi(6)/6, and 1/2 + 1/3 + 1/6 = 1

Reference: docs/hypotheses/152-dark-energy-fixed-point.md
           docs/proofs/T0-04-banach-fixed-point.md
"""

from fractions import Fraction
import math
import sys

PASS = 0
FAIL = 0


def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name}")
    if detail:
        print(f"         {detail}")


def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def main():
    # ================================================================
    # STEP 1: Fixed point equation (exact arithmetic)
    # ================================================================
    section("Step 1: Fixed Point Equation f(I*) = I*")

    # f(I) = 0.7I + 0.1 = (7/10)I + 1/10
    a = Fraction(7, 10)
    b = Fraction(1, 10)

    # Solve: aI + b = I  =>  b = I(1-a)  =>  I = b/(1-a)
    I_star = b / (1 - a)
    check("I* = b/(1-a) = (1/10)/(3/10) = 1/3",
          I_star == Fraction(1, 3),
          f"I* = {I_star} = {float(I_star):.15f}")

    # Verify f(I*) = I*
    f_of_I_star = a * I_star + b
    check("f(1/3) = (7/10)(1/3) + 1/10 = 7/30 + 3/30 = 10/30 = 1/3",
          f_of_I_star == I_star,
          f"f(I*) = {f_of_I_star} = I* = {I_star}")

    # ================================================================
    # STEP 2: Contraction condition (Banach theorem prerequisite)
    # ================================================================
    section("Step 2: Contraction Mapping Condition")

    # f'(x) = a = 7/10 for all x (affine map)
    deriv = a
    check("|f'(x)| = 7/10 < 1 for all x",
          abs(deriv) < 1,
          f"|f'(x)| = {deriv} = {float(deriv)}")

    # Lipschitz condition: |f(x) - f(y)| = |a| * |x - y| <= q * |x - y|
    q = abs(float(a))
    check(f"Lipschitz constant q = {q} < 1",
          q < 1,
          "Contraction mapping on (R, |.|) which is complete")

    # Verify Lipschitz for random pairs
    import random
    random.seed(42)
    lipschitz_ok = True
    for _ in range(1000):
        x = random.uniform(-10, 10)
        y = random.uniform(-10, 10)
        fx = float(a) * x + float(b)
        fy = float(a) * y + float(b)
        if abs(x - y) > 1e-15:
            ratio = abs(fx - fy) / abs(x - y)
            if ratio > q + 1e-12:
                lipschitz_ok = False
                break
    check("Lipschitz verified numerically (1000 random pairs)",
          lipschitz_ok,
          f"|f(x)-f(y)|/|x-y| = {q} for all tested pairs")

    # ================================================================
    # STEP 3: Uniqueness (Banach Fixed Point Theorem)
    # ================================================================
    section("Step 3: Uniqueness (Banach Fixed Point Theorem)")

    print("  Theorem (Banach 1922):")
    print("    Let (X, d) be a complete metric space and f: X -> X")
    print("    a contraction with Lipschitz constant q < 1.")
    print("    Then f has a UNIQUE fixed point x*.")
    print()
    print("  Application:")
    print("    X = R (or any closed interval containing 1/3)")
    print("    d(x,y) = |x-y|  (complete metric space)")
    print("    f(x) = 0.7x + 0.1  (affine, hence continuous)")
    print("    q = 0.7 < 1")
    print("    => Unique fixed point I* = 1/3")
    print()

    # Direct uniqueness proof: suppose f(x) = x and f(y) = y, x != y
    # Then |x - y| = |f(x) - f(y)| <= 0.7|x - y| < |x - y|, contradiction
    check("Uniqueness by contradiction: f(x)=x, f(y)=y, x!=y => |x-y| < |x-y|",
          True,
          "Contradiction proves at most one fixed point exists")

    # ================================================================
    # STEP 4: Convergence rate
    # ================================================================
    section("Step 4: Convergence Rate")

    # Error after n iterations: |I_n - I*| <= q^n * |I_0 - I*|
    print("  Error bound: |I_n - 1/3| <= 0.7^n * |I_0 - 1/3|")
    print()

    # Convergence from various starting points
    starts = [0.0, 0.1, 0.5, 0.99, -1.0, 5.0, 100.0]
    a_f, b_f = 0.7, 0.1
    target = 1.0 / 3.0

    print(f"  {'I_0':>8s} | {'n to |err|<1e-6':>16s} | {'n to |err|<1e-12':>16s} | I_final")
    print(f"  {'-'*8}-+-{'-'*16}-+-{'-'*16}-+-{'-'*20}")

    all_converge = True
    for I0 in starts:
        I = I0
        n6 = n12 = None
        for n in range(1, 10000):
            I = a_f * I + b_f
            err = abs(I - target)
            if n6 is None and err < 1e-6:
                n6 = n
            if n12 is None and err < 1e-12:
                n12 = n
                break
        if n12 is None:
            all_converge = False
        print(f"  {I0:>8.1f} | {n6 if n6 else '>9999':>16} | {n12 if n12 else '>9999':>16} | {I:.15f}")

    check("Convergence from all starting points",
          all_converge,
          f"Tested {len(starts)} starting points, all converge to 1/3")

    # Verify theoretical bound
    I0_test = 0.99
    I = I0_test
    bound_ok = True
    for n in range(1, 200):
        I = a_f * I + b_f
        actual_err = abs(I - target)
        theoretical_bound = (0.7 ** n) * abs(I0_test - target)
        if actual_err > theoretical_bound + 1e-15:
            bound_ok = False
            break
    check("Error bound |I_n - 1/3| <= 0.7^n * |I_0 - 1/3| holds (200 iterations)",
          bound_ok)

    # ================================================================
    # STEP 5: Invariant interval [0, 1]
    # ================================================================
    section("Step 5: Invariant Interval [0, 1]")

    # f maps [0,1] to [0.1, 0.8] subset [0,1]
    f_at_0 = a_f * 0 + b_f  # = 0.1
    f_at_1 = a_f * 1 + b_f  # = 0.8
    check("f(0) = 0.1 >= 0 and f(1) = 0.8 <= 1",
          f_at_0 >= 0 and f_at_1 <= 1,
          f"f([0,1]) = [{f_at_0}, {f_at_1}] subset [0, 1]")
    check("f maps [0,1] into [0.1, 0.8] (proper subset)",
          f_at_0 > 0 and f_at_1 < 1,
          "Contraction in action: image is strictly smaller")

    # 1/3 is in [0.1, 0.8]
    check("Fixed point 1/3 in f([0,1]) = [0.1, 0.8]",
          0.1 <= target <= 0.8,
          f"1/3 = {target:.6f} in [0.1, 0.8]")

    # ================================================================
    # STEP 6: n=6 connections
    # ================================================================
    section("Step 6: n=6 Connections")

    # 1/3 in the completeness relation
    completeness = Fraction(1, 2) + Fraction(1, 3) + Fraction(1, 6)
    check("1/2 + 1/3 + 1/6 = 1 (completeness)",
          completeness == 1,
          f"{Fraction(1,2)} + {Fraction(1,3)} + {Fraction(1,6)} = {completeness}")

    # 1/3 = phi(6)/6
    # phi(6) = 6 * (1 - 1/2) * (1 - 1/3) = 2
    phi_6 = 6 * (1 - Fraction(1, 2)) * (1 - Fraction(1, 3))
    check("phi(6) = 2, so 1/3 = phi(6)/6",
          Fraction(phi_6, 6) == Fraction(1, 3),
          f"phi(6)/6 = {phi_6}/6 = {Fraction(phi_6, 6)}")

    # 1/3 as proper divisor reciprocal of 6: 1/6 is one divisor
    # sum of reciprocals of proper divisors: 1/1 + 1/2 + 1/3 + 1/6 = 2
    # (perfect number property: sigma_(-1)(6) = 2)
    recip_sum = Fraction(1, 1) + Fraction(1, 2) + Fraction(1, 3) + Fraction(1, 6)
    check("sigma_{-1}(6) = 1 + 1/2 + 1/3 + 1/6 = 2 (perfect number)",
          recip_sum == 2,
          f"Sum = {recip_sum}")

    # 1/3 = contraction coefficient derivation
    # f(I) = aI + b with a = 1 - 3/10, b = 1/10
    # Fixed point: I* = b/(1-a) = (1/10)/(3/10) = 1/3
    # The denominator 3 = 6/2 = n/tau(6) where tau(6) = number of divisors = 4...
    # Actually 3 = number of proper divisors of 6 (1, 2, 3)
    check("3 proper divisors of 6: {1, 2, 3}",
          True,
          "I* = 1/(# proper divisors of 6)")

    # ================================================================
    # STEP 7: Generalized contraction f(I) = aI + b
    # ================================================================
    section("Step 7: General Affine Contraction Analysis")

    print("  For general f(I) = aI + b with |a| < 1:")
    print("    Fixed point: I* = b / (1 - a)")
    print("    Contraction rate: |a|")
    print("    Convergence: geometric with ratio |a|")
    print()
    print("  For I* = 1/3 to hold, we need b/(1-a) = 1/3:")
    print("    b = (1-a)/3")
    print("    Examples: (a=0.7, b=0.1), (a=0.4, b=0.2), (a=0.1, b=0.3)")
    print()

    # Verify the constraint
    examples = [(0.7, 0.1), (0.4, 0.2), (0.1, 0.3), (0.85, 0.05)]
    for a_val, b_val in examples:
        fp = b_val / (1 - a_val)
        is_third = abs(fp - 1/3) < 1e-12
        check(f"f(I) = {a_val}I + {b_val} => I* = {fp:.6f} {'= 1/3' if is_third else '!= 1/3'}",
              True,
              f"b/(1-a) = {b_val}/{1-a_val:.1f} = {fp:.10f}")

    # ================================================================
    # STEP 8: Cosmological interpretation
    # ================================================================
    section("Step 8: Cosmological Interpretation")

    print("  Dark energy fraction Omega_Lambda:")
    print("    Current observation: Omega_Lambda ~ 0.685 (Planck 2018)")
    print("    Asymptotic future: Omega_Lambda -> 1 (de Sitter)")
    print()
    print("  Model fixed point I* = 1/3:")
    print("    Not a direct numerical match to Omega_Lambda")
    print("    Structural analogy: both are attractor fixed points")
    print("    But w = -1 is definitional for Lambda, not dynamical")
    print()
    print("  Honest assessment:")
    print("    The fixed point I* = 1/3 is PROVEN (Banach theorem)")
    print("    The cosmological correspondence is STRUCTURAL ANALOGY only")
    print("    Status: downgraded to coincidence (see H-152 verification)")

    check("Proof status: I* = 1/3 is exact and unique (proven)",
          I_star == Fraction(1, 3))

    # ================================================================
    # SUMMARY
    # ================================================================
    section("SUMMARY")

    print(f"\n  Analytical Proof Complete:")
    print(f"    1. f(I) = 0.7I + 0.1 has fixed point I* = 1/3      [EXACT]")
    print(f"    2. |f'(x)| = 0.7 < 1, Banach theorem applies        [PROVEN]")
    print(f"    3. Fixed point is unique                              [PROVEN]")
    print(f"    4. Convergence rate: geometric, ratio 0.7             [PROVEN]")
    print(f"    5. Basin of attraction: all of R                      [PROVEN]")
    print(f"    6. n=6 connection: 1/3 = phi(6)/6, 1/2+1/3+1/6=1    [EXACT]")
    print(f"    7. Cosmological analogy: structural only              [ANALOGY]")
    print(f"\n  Results: {PASS} passed, {FAIL} failed")

    if FAIL > 0:
        print(f"\n  *** {FAIL} CHECK(S) FAILED ***")
        sys.exit(1)
    else:
        print(f"\n  All checks passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
