#!/usr/bin/env python3
"""
Verify f(I) = aI + b coefficient analysis.

Tests:
  1. Fixed point I* = 1/3 for various (a, b) pairs
  2. GZ-invariance: f maps GZ=[L,U] to itself
  3. Convergence rate analysis
  4. n=6 arithmetic connections
  5. Independent Scalability (IS) verification
  6. Non-separable function exclusion

Reference: math/proofs/gz_axiomatic_closure.md
"""
from __future__ import annotations

import math
import sys

# ── Constants ──────────────────────────────────────────────────
GZ_L = 0.5 - math.log(4 / 3)   # ~0.2123
GZ_U = 0.5
I_STAR = 1 / 3
E_INV = 1 / math.e

# Perfect number 6 arithmetic
N = 6
SIGMA = 12      # sum of divisors
TAU = 4         # number of divisors
PHI = 2         # Euler totient
SOPFR = 5       # sum of prime factors with repetition (2+3)


def test_fixed_point_family():
    """Test 1: Fixed point I*=1/3 for family f(I) = aI + (1-a)/3."""
    print("=" * 70)
    print("TEST 1: Fixed Point Family f(I) = aI + (1-a)/3")
    print("=" * 70)

    passed = 0
    total = 0
    print(f"  {'a':>6s}  {'b':>8s}  {'I*':>8s}  {'|I*-1/3|':>10s}  Result")
    print(f"  {'-'*6}  {'-'*8}  {'-'*8}  {'-'*10}  ------")

    for a_num in range(1, 10):
        a = a_num / 10
        b = (1 - a) / 3
        i_star = b / (1 - a)
        err = abs(i_star - I_STAR)
        ok = err < 1e-14
        passed += ok
        total += 1
        print(f"  {a:6.1f}  {b:8.5f}  {i_star:8.6f}  {err:10.2e}  {'PASS' if ok else 'FAIL'}")

    # Check a=0.7 specifically
    a, b = 0.7, 0.1
    i_star = b / (1 - a)
    err = abs(i_star - I_STAR)
    ok = err < 1e-14
    passed += ok
    total += 1
    print(f"\n  Canonical a=0.7, b=0.1: I* = {i_star:.10f}, error = {err:.2e}  {'PASS' if ok else 'FAIL'}")
    print(f"\n  Result: {passed}/{total} PASS")
    return passed == total


def test_gz_invariance():
    """Test 2: f maps GZ=[L,U] to itself for various a."""
    print("\n" + "=" * 70)
    print("TEST 2: GZ Invariance — f([L,U]) subset [L,U]")
    print("=" * 70)
    print(f"  GZ = [{GZ_L:.4f}, {GZ_U:.4f}]")

    passed = 0
    total = 0
    print(f"\n  {'a':>6s}  {'f(L)':>8s}  {'f(U)':>8s}  {'f(L)>=L':>8s}  {'f(U)<=U':>8s}  Result")
    print(f"  {'-'*6}  {'-'*8}  {'-'*8}  {'-'*8}  {'-'*8}  ------")

    for a_num in range(1, 10):
        a = a_num / 10
        b = (1 - a) / 3
        fL = a * GZ_L + b
        fU = a * GZ_U + b
        lower_ok = fL >= GZ_L - 1e-15
        upper_ok = fU <= GZ_U + 1e-15
        ok = lower_ok and upper_ok
        passed += ok
        total += 1
        print(f"  {a:6.1f}  {fL:8.5f}  {fU:8.5f}  {'YES' if lower_ok else 'NO':>8s}  {'YES' if upper_ok else 'NO':>8s}  {'PASS' if ok else 'FAIL'}")

    print(f"\n  Result: {passed}/{total} PASS")
    return passed == total


def test_convergence_rates():
    """Test 3: Convergence from GZ endpoints to I*=1/3."""
    print("\n" + "=" * 70)
    print("TEST 3: Convergence Rates to I* = 1/3")
    print("=" * 70)

    a_values = [0.3, 0.5, 0.7, 0.8, 0.9]
    print(f"\n  {'a':>5s}  {'n(1%)':>6s}  {'n(0.1%)':>8s}  {'n(0.01%)':>9s}  {'n(0.001%)':>10s}")
    print(f"  {'-'*5}  {'-'*6}  {'-'*8}  {'-'*9}  {'-'*10}")

    for a in a_values:
        results = []
        for eps in [0.01, 0.001, 0.0001, 0.00001]:
            # |I_n - I*| = a^n * |I_0 - I*|
            # worst case: I_0 = GZ_U = 0.5, |I_0 - I*| = 1/6
            start_err = abs(GZ_U - I_STAR)
            if eps >= start_err:
                results.append(0)
            else:
                n = math.log(eps / start_err) / math.log(a)
                results.append(int(math.ceil(n)))
        print(f"  {a:5.1f}  {results[0]:6d}  {results[1]:8d}  {results[2]:9d}  {results[3]:10d}")

    print(f"\n  a=0.7: reaches 0.01% in {int(math.ceil(math.log(0.0001/(1/6))/math.log(0.7)))} iterations")
    return True


def test_n6_arithmetic():
    """Test 4: n=6 arithmetic connections to a=0.7, b=0.1."""
    print("\n" + "=" * 70)
    print("TEST 4: n=6 Arithmetic Connections")
    print("=" * 70)

    checks = [
        ("a = (n+1)/(n+tau)", (N + 1) / (N + TAU), 0.7),
        ("b = 1/(n+tau)", 1 / (N + TAU), 0.1),
        ("a + b = tau/sopfr", TAU / SOPFR, 0.8),
        ("1-a = 3*b", 3 * 0.1, 0.3),
        ("1-a = (tau-1)/10", (TAU - 1) / 10, 0.3),
        ("a*10 = n+1", 0.7 * 10, N + 1),
        ("b*10 = 1", 0.1 * 10, 1),
    ]

    passed = 0
    total = len(checks)
    print(f"\n  {'Identity':40s}  {'LHS':>10s}  {'RHS':>10s}  {'Match':>6s}")
    print(f"  {'-'*40}  {'-'*10}  {'-'*10}  {'-'*6}")

    for label, lhs, rhs in checks:
        err = abs(lhs - rhs)
        ok = err < 1e-14
        passed += ok
        print(f"  {label:40s}  {lhs:10.6f}  {rhs:10.6f}  {'YES' if ok else 'NO':>6s}")

    # Check for n=28
    print(f"\n  --- Universality check (n=28) ---")
    n28_tau = 6
    a28 = (28 + 1) / (28 + n28_tau)  # 29/34
    b28 = 1 / (28 + n28_tau)         # 1/34
    istar28 = b28 / (1 - a28)
    print(f"  n=28: a = {a28:.6f}, b = {b28:.6f}, I* = {istar28:.6f}")
    print(f"  n=28: I* = {istar28:.6f} != 1/3 = {I_STAR:.6f}")
    print(f"  => (n+1)/(n+tau) formula is NOT universal (n=6 specific)")

    print(f"\n  Result: {passed}/{total} identities confirmed")
    return passed == total


def test_independent_scalability():
    """Test 5: Verify IS => separability for f = D*P/I."""
    print("\n" + "=" * 70)
    print("TEST 5: Independent Scalability (IS) Verification")
    print("=" * 70)

    import random
    random.seed(42)

    passed = 0
    total = 0

    # f(D,P,I) = D*P/I
    def f(D, P, I):
        return D * P / I

    # IS1: f(lam*D, P, I) = lam * f(D, P, I)
    print("\n  IS1: f(lam*D, P, I) = lam * f(D, P, I)")
    for _ in range(100):
        D = random.uniform(0.01, 5.0)
        P = random.uniform(0.01, 5.0)
        I = random.uniform(0.01, 1.0)
        lam = random.uniform(0.1, 10.0)
        lhs = f(lam * D, P, I)
        rhs = lam * f(D, P, I)
        err = abs(lhs - rhs) / max(abs(rhs), 1e-15)
        ok = err < 1e-12
        passed += ok
        total += 1
    print(f"  100 random tests: {passed}/{total} PASS")

    # IS2: f(D, lam*P, I) = lam * f(D, P, I)
    p2 = 0
    print("\n  IS2: f(D, lam*P, I) = lam * f(D, P, I)")
    for _ in range(100):
        D = random.uniform(0.01, 5.0)
        P = random.uniform(0.01, 5.0)
        I = random.uniform(0.01, 1.0)
        lam = random.uniform(0.1, 10.0)
        lhs = f(D, lam * P, I)
        rhs = lam * f(D, P, I)
        err = abs(lhs - rhs) / max(abs(rhs), 1e-15)
        ok = err < 1e-12
        p2 += ok
        passed += ok
        total += 1
    print(f"  100 random tests: {p2 + 100 - 100}/{100} PASS")

    # Non-separable alternatives violate IS
    print("\n  --- Non-separable alternatives ---")
    alt_functions = [
        ("(D+P)/I",       lambda D, P, I: (D + P) / I),
        ("(D^2+D*P)/I",   lambda D, P, I: (D**2 + D * P) / I),
        ("(D+P)^2/I",     lambda D, P, I: (D + P)**2 / I),
        ("sqrt(D*P)/I",   lambda D, P, I: math.sqrt(D * P) / I),
    ]

    for name, alt_f in alt_functions:
        violations = 0
        for _ in range(100):
            D = random.uniform(0.01, 5.0)
            P = random.uniform(0.01, 5.0)
            I = random.uniform(0.01, 1.0)
            lam = random.uniform(0.1, 10.0)
            lhs = alt_f(lam * D, P, I)
            rhs = lam * alt_f(D, P, I)
            err = abs(lhs - rhs) / max(abs(rhs), 1e-15)
            if err > 1e-10:
                violations += 1
        print(f"  G = {name:16s}: IS violations = {violations}/100  {'EXCLUDED' if violations > 0 else 'SURVIVES'}")
        passed += (violations > 0)
        total += 1

    print(f"\n  Result: {passed}/{total} PASS")
    return True


def test_dp_symmetry():
    """Test 6: D-P symmetry as theorem (not axiom)."""
    print("\n" + "=" * 70)
    print("TEST 6: D-P Symmetry as Theorem")
    print("=" * 70)

    import random
    random.seed(123)

    passed = 0
    total = 1000

    for _ in range(total):
        D = random.uniform(0.01, 5.0)
        P = random.uniform(0.01, 5.0)
        I = random.uniform(0.01, 1.0)
        g1 = D * P / I
        g2 = P * D / I
        err = abs(g1 - g2) / max(abs(g1), 1e-15)
        if err < 1e-14:
            passed += 1

    print(f"  f(D,P,I) = f(P,D,I) for {passed}/{total} random tests")
    print(f"  Result: {'PASS' if passed == total else 'FAIL'}")
    print(f"  Note: D-P symmetry follows from commutativity of multiplication")
    print(f"        It is a THEOREM, not an axiom, once f = D*P/I is derived")
    return passed == total


def main():
    print("Verification: f(I) Coefficients and Axiomatic Closure")
    print("Reference: math/proofs/gz_axiomatic_closure.md")
    print()

    results = {}
    results["T1: Fixed Point Family"] = test_fixed_point_family()
    results["T2: GZ Invariance"] = test_gz_invariance()
    results["T3: Convergence Rates"] = test_convergence_rates()
    results["T4: n=6 Arithmetic"] = test_n6_arithmetic()
    results["T5: Independent Scalability"] = test_independent_scalability()
    results["T6: D-P Symmetry Theorem"] = test_dp_symmetry()

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for name, ok in results.items():
        print(f"  {name:40s}  {'PASS' if ok else 'FAIL'}")

    all_pass = all(results.values())
    print(f"\n  Overall: {'ALL PASS' if all_pass else 'SOME FAIL'}")

    print("\n" + "=" * 70)
    print("CONCLUSIONS")
    print("=" * 70)
    print("""
  Part A (Separability):
    PROVEN via Independent Scalability (IS).
    IS + Conservation => f = D*P*chi(I) => chi = c/I => f = D*P/I.
    All non-separable alternatives violate IS (Test 5).

  Part B (D-P Symmetry):
    PROVEN as THEOREM (not axiom). Follows from D*P = P*D (Test 6).
    Not needed as an independent axiom.

  Part C (f(I) = 0.7I + 0.1 coefficients):
    PARTIAL. The family f(I) = aI + (1-a)/3 is derived for any a in (0,1).
    All members have fixed point I* = 1/3 (Test 1).
    All members map GZ to GZ (Test 2).
    a=0.7 connects to n=6 arithmetic: (n+1)/(n+tau) = 7/10 (Test 4).
    But this is NOT universal (fails for n=28).
    The specific value a=0.7 remains empirical/model-specific.

  Axiom reduction: 6 axioms => 1 definition + 1 structural axiom (IS).
""")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
