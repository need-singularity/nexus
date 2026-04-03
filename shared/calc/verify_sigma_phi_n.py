#!/usr/bin/env python3
"""
Rigorous verification: sigma(n)/phi(n) = n iff n in {1, 6}.

Equivalently: sigma(n) = n * phi(n).

Verifies every inequality and claim in the proof.
"""

from math import gcd
from fractions import Fraction
from sympy import factorint, divisor_sigma, totient, isprime, nextprime


# ============================================================
# Section 1: Define f(p^a) = sigma(p^a) / (p^a * phi(p^a))
# ============================================================

def f_prime_power(p: int, a: int) -> Fraction:
    """Compute f(p^a) = sigma(p^a) / (p^a * phi(p^a)) exactly."""
    # sigma(p^a) = (p^(a+1) - 1) / (p - 1)
    sigma_pa = (p**(a+1) - 1) // (p - 1)
    # phi(p^a) = p^(a-1) * (p - 1)
    phi_pa = p**(a-1) * (p - 1)
    # p^a * phi(p^a)
    denom = p**a * phi_pa
    return Fraction(sigma_pa, denom)


def f_product(n: int) -> Fraction:
    """Compute prod f(p^a) over prime factorization of n."""
    if n == 1:
        return Fraction(1)
    fac = factorint(n)
    result = Fraction(1)
    for p, a in fac.items():
        result *= f_prime_power(p, a)
    return result


# ============================================================
# Section 2: Brute-force check up to 10^6
# ============================================================

def brute_force_check(limit: int):
    """Check sigma(n) = n * phi(n) for all n in [1, limit]."""
    solutions = []
    for n in range(1, limit + 1):
        s = divisor_sigma(n)
        p = totient(n)
        if s == n * p:
            solutions.append(n)
    return solutions


# ============================================================
# Section 3: Verify specific f values
# ============================================================

def verify_f_values():
    """Verify all f(p^a) values cited in the proof."""
    print("=" * 60)
    print("SECTION 1: f(p^a) values for small prime powers")
    print("=" * 60)

    cases = [
        (2, 1, Fraction(3, 2)),
        (3, 1, Fraction(2, 3)),
        (5, 1, Fraction(3, 10)),
        (7, 1, Fraction(4, 21)),
        (11, 1, Fraction(6, 55)),
        (2, 2, Fraction(7, 8)),
        (2, 3, Fraction(15, 32)),
        (3, 2, Fraction(13, 54)),
    ]

    all_ok = True
    for p, a, expected in cases:
        actual = f_prime_power(p, a)
        ok = actual == expected
        if not ok:
            all_ok = False
        print(f"  f({p}^{a}) = {actual} = {float(actual):.6f}  "
              f"{'OK' if ok else 'MISMATCH (expected ' + str(expected) + ')'}")

    # Also print f(p) for primes up to 50
    print("\n  f(p) for primes p <= 50:")
    p = 2
    while p <= 50:
        val = f_prime_power(p, 1)
        print(f"    f({p}) = {val} = {float(val):.6f}")
        p = nextprime(p)

    return all_ok


# ============================================================
# Section 4: Verify Lemma — f(p) = (p+1)/(p(p-1)) for a=1
# ============================================================

def verify_f_formula():
    """Verify f(p) = (p+1)/(p^2-p) for primes."""
    print("\n" + "=" * 60)
    print("SECTION 2: Verify f(p) = (p+1)/(p(p-1))")
    print("=" * 60)

    all_ok = True
    p = 2
    while p <= 100:
        computed = f_prime_power(p, 1)
        formula = Fraction(p + 1, p * (p - 1))
        ok = computed == formula
        if not ok:
            all_ok = False
            print(f"  MISMATCH at p={p}: computed={computed}, formula={formula}")
        p = nextprime(p)

    print(f"  f(p) = (p+1)/(p(p-1)) verified for all primes <= 100: "
          f"{'PASS' if all_ok else 'FAIL'}")
    return all_ok


# ============================================================
# Section 5: Verify f(2) is the ONLY prime with f > 1
# ============================================================

def verify_f2_unique_above_1():
    """Prove f(p) > 1 iff p = 2 (for a=1)."""
    print("\n" + "=" * 60)
    print("SECTION 3: f(p) > 1 iff p = 2")
    print("=" * 60)

    # f(p) = (p+1)/(p(p-1))
    # f(p) > 1 iff p+1 > p(p-1) = p^2 - p iff p^2 - 2p - 1 < 0
    # p^2 - 2p - 1 = 0 at p = 1 + sqrt(2) ~ 2.414
    # So f(p) > 1 for p < 1+sqrt(2), i.e., only p=2.

    # Verify numerically
    p = 2
    above_1 = []
    while p <= 1000:
        if f_prime_power(p, 1) > 1:
            above_1.append(p)
        p = nextprime(p)

    ok = above_1 == [2]
    print(f"  Primes with f(p) > 1 among p <= 1000: {above_1}")
    print(f"  Algebraic: f(p) > 1 iff p+1 > p(p-1) iff p^2-2p-1 < 0")
    print(f"  Root: p = 1+sqrt(2) ~ 2.414, so only integer prime p=2.")
    print(f"  PASS" if ok else "  FAIL")

    # Also check higher powers of 2
    print("\n  f(2^a) for a = 1..10:")
    for a in range(1, 11):
        val = f_prime_power(2, a)
        print(f"    f(2^{a}) = {val} = {float(val):.8f}  {'> 1' if val > 1 else '<= 1'}")

    # Verify f(2^a) < 1 for a >= 2
    all_below = all(f_prime_power(2, a) < 1 for a in range(2, 100))
    print(f"\n  f(2^a) < 1 for all a in [2,99]: {'PASS' if all_below else 'FAIL'}")

    return ok and all_below


# ============================================================
# Section 6: Verify f(2^a) formula and monotone decrease for a>=2
# ============================================================

def verify_f2a_decreasing():
    """Verify f(2^a) = (2^(a+1)-1)/2^(2a-1) and strictly decreasing for a>=1."""
    print("\n" + "=" * 60)
    print("SECTION 4: f(2^a) = (2^(a+1)-1) / 2^(2a-1), decreasing")
    print("=" * 60)

    all_ok = True
    prev = None
    for a in range(1, 20):
        computed = f_prime_power(2, a)
        formula = Fraction(2**(a+1) - 1, 2**(2*a - 1))
        ok = computed == formula
        if not ok:
            all_ok = False
            print(f"  MISMATCH at a={a}")
        if prev is not None and computed >= prev:
            all_ok = False
            print(f"  NOT DECREASING at a={a}: {computed} >= {prev}")
        prev = computed

    print(f"  Formula and monotonicity verified for a in [1,19]: "
          f"{'PASS' if all_ok else 'FAIL'}")

    # Prove: f(2^a) -> 0 as a -> infty
    # f(2^a) = (2^(a+1)-1)/2^(2a-1) < 2^(a+1)/2^(2a-1) = 2^(2-a) -> 0
    print(f"  Limit: f(2^a) < 2^(a+1)/2^(2a-1) = 4/2^a -> 0")
    return all_ok


# ============================================================
# Section 7: Verify f(p) < 2/3 for odd primes p >= 5
# ============================================================

def verify_f_bound_odd():
    """Verify f(p) < 2/3 for all odd primes p >= 5."""
    print("\n" + "=" * 60)
    print("SECTION 5: f(p) < 2/3 for odd primes p >= 5")
    print("=" * 60)

    # f(p) = (p+1)/(p(p-1)). For p >= 5:
    # f(5) = 6/20 = 3/10.
    # f is decreasing for p >= 3 (derivative of (x+1)/(x^2-x) is negative).
    # f(3) = 4/6 = 2/3 exactly. So f(p) < 2/3 for p >= 5.

    # Verify f(3) = 2/3 exactly
    f3 = f_prime_power(3, 1)
    ok_f3 = f3 == Fraction(2, 3)
    print(f"  f(3) = {f3} = 2/3 exactly: {'PASS' if ok_f3 else 'FAIL'}")

    # Verify f(p) < 2/3 for p = 5,7,...,997
    p = 5
    all_below = True
    max_f = Fraction(0)
    while p <= 997:
        val = f_prime_power(p, 1)
        if val >= Fraction(2, 3):
            all_below = False
            print(f"  VIOLATION at p={p}: f(p) = {val}")
        if val > max_f:
            max_f = val
        p = nextprime(p)

    print(f"  max f(p) for odd p in [5,997] = {max_f} = {float(max_f):.6f}")
    print(f"  All f(p) < 2/3 for odd p in [5,997]: {'PASS' if all_below else 'FAIL'}")

    # Prove algebraically: f(p) < 2/3 for p >= 5
    # (p+1)/(p(p-1)) < 2/3  iff  3(p+1) < 2p(p-1) = 2p^2 - 2p
    # iff  2p^2 - 5p - 3 > 0  iff  (2p+1)(p-3) > 0
    # For p >= 5: 2p+1 >= 11 > 0 and p-3 >= 2 > 0. QED.
    print(f"\n  Algebraic proof:")
    print(f"    f(p) < 2/3 iff 3(p+1) < 2p(p-1)")
    print(f"    iff 2p^2 - 5p - 3 > 0")
    print(f"    iff (2p+1)(p-3) > 0")
    print(f"    For p >= 5: (2p+1) >= 11 > 0 and (p-3) >= 2 > 0. QED.")

    # Verify the factorization
    from sympy import symbols, factor
    x = symbols('x')
    expr = 2*x**2 - 5*x - 3
    factored = factor(expr)
    print(f"    Sympy factor(2p^2 - 5p - 3) = {factored}")

    return ok_f3 and all_below


# ============================================================
# Section 8: Verify f(p) is strictly decreasing for p >= 3
# ============================================================

def verify_f_decreasing():
    """f(p) = (p+1)/(p(p-1)) is strictly decreasing for p >= 2."""
    print("\n" + "=" * 60)
    print("SECTION 6: f(p) strictly decreasing for p >= 2")
    print("=" * 60)

    # Check numerically
    prev_p = 2
    prev_f = f_prime_power(2, 1)
    p = 3
    all_decreasing = True
    while p <= 200:
        cur_f = f_prime_power(p, 1)
        if cur_f >= prev_f:
            all_decreasing = False
            print(f"  NOT DECREASING: f({prev_p})={prev_f}, f({p})={cur_f}")
        prev_p, prev_f = p, cur_f
        p = nextprime(p)

    print(f"  Strictly decreasing for consecutive primes in [2,200]: "
          f"{'PASS' if all_decreasing else 'FAIL'}")

    # Algebraic: g(x) = (x+1)/(x^2-x), g'(x) = -(x^2+2x-1)/(x^2-x)^2
    # For x >= 2: x^2+2x-1 >= 4+4-1 = 7 > 0, so g'(x) < 0. QED.
    print(f"  Algebraic: g(x)=(x+1)/(x^2-x), g'(x)=-(x^2+2x-1)/(x^2-x)^2")
    print(f"  For x>=2: numerator x^2+2x-1 >= 7 > 0, so g'<0. QED.")
    return all_decreasing


# ============================================================
# Section 9: Verify the key bound for higher powers
# ============================================================

def verify_higher_power_bounds():
    """f(p^a) < f(p) for a >= 2, and f(p^a) < 1 for p >= 3, a >= 2."""
    print("\n" + "=" * 60)
    print("SECTION 7: f(p^a) bounds for a >= 2")
    print("=" * 60)

    # Check f(p^a) <= f(p^1) for small cases
    all_ok = True
    for p in [2, 3, 5, 7, 11, 13]:
        f1 = f_prime_power(p, 1)
        for a in range(2, 8):
            fa = f_prime_power(p, a)
            if fa >= f1:
                all_ok = False
                print(f"  VIOLATION: f({p}^{a})={fa} >= f({p}^1)={f1}")

    print(f"  f(p^a) < f(p^1) for p in {{2,3,5,7,11,13}}, a in [2,7]: "
          f"{'PASS' if all_ok else 'FAIL'}")

    # Check f(p^a) < 1 for all p >= 3, a >= 1
    all_below_1 = True
    for p in [3, 5, 7, 11, 13, 17, 19, 23]:
        for a in range(1, 10):
            fa = f_prime_power(p, a)
            if fa >= 1:
                all_below_1 = False
                print(f"  VIOLATION: f({p}^{a})={fa} >= 1")

    print(f"  f(p^a) < 1 for odd p in {{3..23}}, a in [1,9]: "
          f"{'PASS' if all_below_1 else 'FAIL'}")

    return all_ok and all_below_1


# ============================================================
# Section 10: Prove n=6 is the only non-trivial solution
# ============================================================

def verify_product_constraints():
    """
    For n = 2 * m (m odd, m > 1):
    Need product of f(p^a) over odd prime powers in m = 2/3.
    Show this forces m = 3.
    """
    print("\n" + "=" * 60)
    print("SECTION 8: Product constraint analysis")
    print("=" * 60)

    target = Fraction(2, 3)
    print(f"  Target: product of f(p_i^a_i) for odd part = {target}")
    print()

    # Case 1: m = p (single odd prime)
    print("  Case 1: m = p (single odd prime, a=1)")
    print("  f(3) = 2/3 = target. SOLUTION: n = 2*3 = 6.")
    f3 = f_prime_power(3, 1)
    assert f3 == target
    p = 5
    while p <= 50:
        fp = f_prime_power(p, 1)
        print(f"    f({p}) = {fp} = {float(fp):.6f} < 2/3")
        assert fp < target
        p = nextprime(p)
    print("  f(p) < 2/3 for p >= 5 (proven in Section 5). No other single-prime solution.")

    # Case 2: m = p^a (single odd prime, a >= 2)
    print("\n  Case 2: m = p^a (single odd prime, a >= 2)")
    print("  Need f(p^a) = 2/3.")
    for p in [3, 5, 7]:
        for a in range(2, 8):
            fa = f_prime_power(p, a)
            if fa == target:
                print(f"    FOUND: f({p}^{a}) = {fa}")
            # f(3^a) for a >= 2: decreasing below 2/3
    print(f"    f(3^2) = {f_prime_power(3,2)} = {float(f_prime_power(3,2)):.6f} < 2/3")
    print(f"    f(p^a) < f(p) <= f(3) = 2/3 for p >= 3, a >= 2. No solution.")

    # Case 3: m = p*q (two distinct odd primes)
    print("\n  Case 3: m = p*q (two distinct odd primes, a=b=1)")
    print("  Product f(p)*f(q). Maximum when p=3, q=5:")
    f3f5 = f_prime_power(3, 1) * f_prime_power(5, 1)
    print(f"    f(3)*f(5) = {f3f5} = {float(f3f5):.6f} < 2/3")
    assert f3f5 < target
    print("  Since f is decreasing: f(p)*f(q) <= f(3)*f(5) < 2/3 for p >= 3, q >= 5.")
    print("  Also f(3)*f(3) is impossible (distinct primes). No solution.")

    # Case 4: m has >= 3 distinct odd prime factors
    print("\n  Case 4: m has >= 3 distinct odd prime factors")
    f3f5f7 = f_prime_power(3, 1) * f_prime_power(5, 1) * f_prime_power(7, 1)
    print(f"    f(3)*f(5)*f(7) = {f3f5f7} = {float(f3f5f7):.6f} < 2/3")
    print("  Product only gets smaller. No solution.")

    # Case 5: n = 2^a * m, a >= 2
    print("\n  Case 5: n = 2^a * m (a >= 2)")
    print(f"    f(2^2) = {f_prime_power(2,2)} < 1")
    print(f"    All f(p^b) < 1 for odd p^b. Product of values all < 1 is < 1.")
    print(f"    No solution.")

    # Case 6: n odd (not divisible by 2)
    print("\n  Case 6: n odd")
    print("    All f(p^a) < 1 for p >= 3. Product < 1. No solution.")

    # Case 7: n = 1
    print("\n  Case 7: n = 1")
    print("    Empty product = 1. sigma(1) = 1, phi(1) = 1, 1*1 = 1. SOLUTION.")

    print("\n  CONCLUSION: n in {1, 6} are the ONLY solutions. QED.")


# ============================================================
# Section 11: Exhaustive brute force
# ============================================================

def run_brute_force():
    """Check all n up to 10^6."""
    print("\n" + "=" * 60)
    print("SECTION 9: Brute-force verification up to 10^6")
    print("=" * 60)
    print("  Computing... (this may take a minute)")

    limit = 10**6
    solutions = brute_force_check(limit)
    print(f"  Solutions of sigma(n) = n*phi(n) in [1, {limit}]: {solutions}")
    ok = solutions == [1, 6]
    print(f"  Match {'{'}1, 6{'}'}: {'PASS' if ok else 'FAIL'}")

    # Also check near-misses (ratio close to 1)
    print("\n  Top 10 closest near-misses (sigma(n)/(n*phi(n))):")
    near = []
    for n in range(2, min(limit + 1, 100001)):
        if n in (1, 6):
            continue
        s = int(divisor_sigma(n))
        p = int(totient(n))
        ratio = s / (n * p)
        near.append((abs(1 - ratio), n, ratio))
    near.sort()
    for _, n, ratio in near[:10]:
        fac = factorint(n)
        print(f"    n={n:>6} ({fac}): sigma/(n*phi) = {ratio:.8f}")

    return ok


# ============================================================
# Section 12: Verify the proof is watertight — check edge cases
# ============================================================

def verify_edge_cases():
    """Additional edge case verification."""
    print("\n" + "=" * 60)
    print("SECTION 10: Edge cases and additional checks")
    print("=" * 60)

    # n=1: trivial
    print(f"  n=1: sigma={divisor_sigma(1)}, phi={totient(1)}, "
          f"n*phi={1*totient(1)}, match={divisor_sigma(1)==1*totient(1)}")

    # n=6: the solution
    print(f"  n=6: sigma={divisor_sigma(6)}, phi={totient(6)}, "
          f"n*phi={6*totient(6)}, match={divisor_sigma(6)==6*totient(6)}")

    # n=2: f(2) = 3/2 != 1
    print(f"  n=2: sigma={divisor_sigma(2)}, phi={totient(2)}, "
          f"n*phi={2*totient(2)}, match={divisor_sigma(2)==2*totient(2)}")

    # Perfect numbers: sigma(n) = 2n, check if 2n = n*phi(n) => phi(n)=2
    # phi(n) = 2 only for n in {3,4,6}. Among those, sigma(6)=12=2*6. Check.
    print("\n  Perfect numbers check:")
    for n in [6, 28, 496, 8128]:
        s = divisor_sigma(n)
        p = totient(n)
        print(f"    n={n}: sigma={s}=2n?{s==2*n}, phi={p}, "
              f"n*phi={n*p}, sigma=n*phi?{s==n*p}")

    # Verify the multiplicative decomposition for n=6
    print("\n  Multiplicative decomposition for n=6 = 2 * 3:")
    f2 = f_prime_power(2, 1)
    f3 = f_prime_power(3, 1)
    print(f"    f(2) = {f2}, f(3) = {f3}")
    print(f"    f(2) * f(3) = {f2 * f3}")
    assert f2 * f3 == 1

    return True


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("RIGOROUS VERIFICATION: sigma(n) = n * phi(n)")
    print("  Solutions: n in {1, 6} only")
    print("=" * 60)

    results = {}
    results["f_values"] = verify_f_values()
    results["f_formula"] = verify_f_formula()
    results["f2_unique"] = verify_f2_unique_above_1()
    results["f2a_decreasing"] = verify_f2a_decreasing()
    results["f_bound_odd"] = verify_f_bound_odd()
    results["f_decreasing"] = verify_f_decreasing()
    results["higher_powers"] = verify_higher_power_bounds()
    verify_product_constraints()
    verify_edge_cases()
    results["brute_force"] = run_brute_force()

    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    all_pass = all(results.values())
    for name, ok in results.items():
        print(f"  {name}: {'PASS' if ok else 'FAIL'}")
    print(f"\n  ALL CHECKS: {'PASS' if all_pass else 'FAIL'}")
    if all_pass:
        print("\n  THEOREM VERIFIED: sigma(n)/phi(n) = n iff n in {1, 6}.")
    else:
        print("\n  SOME CHECKS FAILED. Review output above.")
