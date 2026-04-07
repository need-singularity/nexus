#!/usr/bin/env python3
"""
H-HARMONIC-001 Verification: Ramanujan Sum c_6(n) Structure

Verifies all claims in the hypothesis document:
- c_6(n) values for n=1..30
- c_6(n) depends only on gcd(n,6)
- c_6(n) = 2*cos(n*pi/3)
- Sum over complete residue system = 0
- Value set = {1, -1, -phi(6), phi(6)}
- Comparison with c_28(n) for perfect number 28

Run: PYTHONPATH=. python3 verify/verify_harmonic_001_ramanujan_sum.py
"""

import math
import cmath


def euler_phi(n):
    """Euler's totient function."""
    result = n
    p = 2
    temp = n
    while p * p <= temp:
        if temp % p == 0:
            while temp % p == 0:
                temp //= p
            result -= result // p
        p += 1
    if temp > 1:
        result -= result // temp
    return result


def moebius(n):
    """Moebius function mu(n)."""
    if n == 1:
        return 1
    count = 0
    temp = n
    d = 2
    while d * d <= temp:
        if temp % d == 0:
            count += 1
            temp //= d
            if temp % d == 0:
                return 0  # squared factor
        d += 1
    if temp > 1:
        count += 1
    return (-1) ** count


def gcd(a, b):
    """Greatest common divisor."""
    while b:
        a, b = b, a % b
    return a


def ramanujan_sum_formula(q, n):
    """Compute c_q(n) using explicit formula: mu(q/d) * phi(q) / phi(q/d)."""
    d = gcd(n, q)
    qd = q // d
    mu_qd = moebius(qd)
    if mu_qd == 0:
        return 0
    return mu_qd * euler_phi(q) // euler_phi(qd) if euler_phi(q) % euler_phi(qd) == 0 else mu_qd * euler_phi(q) / euler_phi(qd)


def ramanujan_sum_direct(q, n):
    """Compute c_q(n) directly from definition: sum of e^(2*pi*i*a*n/q) for gcd(a,q)=1."""
    total = 0.0
    for a in range(1, q + 1):
        if gcd(a, q) == 1:
            total += cmath.exp(2j * cmath.pi * a * n / q).real
    return round(total)


def tau(n):
    """Number of divisors."""
    count = 0
    for i in range(1, int(math.isqrt(n)) + 1):
        if n % i == 0:
            count += 1
            if i != n // i:
                count += 1
    return count


def divisors(n):
    """Return sorted list of divisors."""
    divs = []
    for i in range(1, int(math.isqrt(n)) + 1):
        if n % i == 0:
            divs.append(i)
            if i != n // i:
                divs.append(n // i)
    return sorted(divs)


def main():
    print("=" * 70)
    print("H-HARMONIC-001 VERIFICATION: Ramanujan Sum c_6(n) Structure")
    print("=" * 70)

    q = 6
    phi_q = euler_phi(q)

    # ── Test 1: Explicit formula for c_6 by gcd ──
    print(f"\n--- Test 1: c_6(n) by gcd(n,6) [formula method] ---")
    print()
    print(f"  d=gcd(n,6) | q/d | mu(q/d) | phi(q)={phi_q} | phi(q/d) | c_6(n)")
    print(f"  {'-'*11}-+-{'-'*3}-+-{'-'*7}-+-{'-'*9}-+-{'-'*8}-+-{'-'*6}")
    for d in divisors(q):
        qd = q // d
        mu_val = moebius(qd)
        phi_qd = euler_phi(qd)
        c_val = mu_val * phi_q // phi_qd if phi_q % phi_qd == 0 else "ERR"
        print(f"  {d:>11} | {qd:>3} | {mu_val:>7} | {phi_q:>9} | {phi_qd:>8} | {c_val:>6}")

    # ── Test 2: Verification table n=1..30 ──
    print(f"\n--- Test 2: c_6(n) for n=1..30 (formula vs direct computation) ---")
    print()
    print(f"  {'n':>3} | {'gcd(n,6)':>8} | {'formula':>8} | {'direct':>8} | {'2cos(npi/3)':>12} | {'match':>5}")
    print(f"  {'-'*3}-+-{'-'*8}-+-{'-'*8}-+-{'-'*8}-+-{'-'*12}-+-{'-'*5}")

    all_match = True
    for n in range(1, 31):
        c_formula = ramanujan_sum_formula(q, n)
        c_direct = ramanujan_sum_direct(q, n)
        c_trig = round(2 * math.cos(n * math.pi / 3))
        d = gcd(n, q)
        match = (c_formula == c_direct == c_trig)
        if not match:
            all_match = False
        status = "OK" if match else "FAIL"
        print(f"  {n:>3} | {d:>8} | {c_formula:>8} | {c_direct:>8} | {c_trig:>12} | {status:>5}")

    print(f"\n  All three methods agree: {'PASS' if all_match else 'FAIL'}")

    # ── Test 3: Value set analysis ──
    print(f"\n--- Test 3: Value set of c_6 ---")
    values = set()
    for n in range(1, 7):
        values.add(ramanujan_sum_formula(q, n))
    print(f"  Distinct values: {sorted(values)}")
    print(f"  Number of distinct values: {len(values)}")
    print(f"  tau(6) = {tau(6)}")
    print(f"  |values| = tau(6): {len(values) == tau(6)}  {'PASS' if len(values) == tau(6) else 'FAIL'}")
    print(f"  phi(6) = {phi_q}")
    print(f"  Values = {{1, -1, -phi(6), phi(6)}} = {{1, -1, -{phi_q}, {phi_q}}}: ", end="")
    expected = {1, -1, -phi_q, phi_q}
    print(f"{'PASS' if values == expected else 'FAIL'}")

    # ── Test 4: Sum over complete residue system ──
    print(f"\n--- Test 4: Sum over complete residue system ---")
    total = sum(ramanujan_sum_formula(q, n) for n in range(1, 7))
    print(f"  SUM_{{n=1}}^{{6}} c_6(n) = {total}")
    print(f"  Expected: 0")
    print(f"  Match: {total == 0}  {'PASS' if total == 0 else 'FAIL'}")

    abs_total = sum(abs(ramanujan_sum_formula(q, n)) for n in range(1, 7))
    print(f"  SUM |c_6(n)| = {abs_total} = 2^3 = 8  {'PASS' if abs_total == 8 else 'FAIL'}")

    # ── Test 5: Trigonometric identity ──
    print(f"\n--- Test 5: c_6(n) = 2*cos(n*pi/3) verification ---")
    print()
    print(f"  {'n':>3} | {'c_6(n)':>6} | {'2cos(npi/3)':>14} | {'error':>12}")
    print(f"  {'-'*3}-+-{'-'*6}-+-{'-'*14}-+-{'-'*12}")
    max_err = 0
    for n in range(1, 13):
        c = ramanujan_sum_formula(q, n)
        trig = 2 * math.cos(n * math.pi / 3)
        err = abs(c - trig)
        max_err = max(max_err, err)
        print(f"  {n:>3} | {c:>6} | {trig:>14.10f} | {err:>12.2e}")
    print(f"\n  Maximum error: {max_err:.2e}  {'PASS' if max_err < 1e-10 else 'FAIL'}")

    # ── Test 6: ASCII periodicity visualization ──
    print(f"\n--- Test 6: ASCII visualization of c_6 periodicity ---")
    print()
    width = 60
    for val in [2, 1, 0, -1, -2]:
        line = f"  {val:>3} |"
        for n in range(1, width + 1):
            c = ramanujan_sum_formula(q, n)
            if c == val:
                line += "*"
            elif val == 0:
                line += "-"
            else:
                line += " "
        print(line)
    print(f"      +{''.join(str(n % 10) for n in range(1, width + 1))}")
    print(f"       n (mod 10 shown)")
    print(f"\n  Period = 6: pattern [1, -1, -2, -1, 1, 2] repeats perfectly")

    # ── Test 7: Moebius value at q=6 ──
    print(f"\n--- Test 7: mu(6) and von Mangoldt contribution ---")
    mu6 = moebius(6)
    print(f"  mu(6) = mu(2*3) = mu(2)*mu(3) = (-1)*(-1) = {mu6}")
    print(f"  phi(6) = {phi_q}")
    print(f"  Contribution weight: mu(6)/phi(6) = {mu6}/{phi_q} = {mu6/phi_q}")
    print(f"  mu(6) = 1 means c_6 contributes with POSITIVE weight to Lambda(n)")
    print(f"  (Most composite q have mu(q) = 0, contributing nothing)")
    print()
    print(f"  Squarefree q <= 30 with mu(q) = +1 (even prime factor count):")
    positive_mu = [n for n in range(1, 31) if moebius(n) == 1]
    print(f"  {positive_mu}")
    print(f"  6 is in this set: {'PASS' if 6 in positive_mu else 'FAIL'}")

    # ── Test 8: Comparison with c_28 ──
    print(f"\n--- Test 8: Comparison with perfect number 28 ---")
    print()
    q28 = 28
    phi_28 = euler_phi(28)
    values_28 = set()
    for n in range(1, 29):
        values_28.add(ramanujan_sum_formula(q28, n))
    print(f"  q=28: phi(28) = {phi_28}")
    print(f"  c_28 value set: {sorted(values_28)}")
    print(f"  Number of distinct values: {len(values_28)}")
    print(f"  tau(28) = {tau(28)}")
    # 28 = 2^2 * 7 is NOT squarefree, so mu(28/d)=0 for some d, collapsing values
    print(f"  28 is NOT squarefree (2^2*7), so |values| < tau(28)")
    print(f"  |values| = tau(28): {len(values_28) == tau(28)}  (EXPECTED FAIL: not squarefree)")
    print(f"  n=6 is the ONLY squarefree perfect number (6=2*3)")
    sq6 = moebius(6) != 0
    print(f"  mu(6) != 0 (squarefree): {sq6}  {'PASS' if sq6 else 'FAIL'}")
    sq28 = moebius(28) != 0
    print(f"  mu(28) != 0 (squarefree): {sq28}  (expected False)")
    print()

    # Side by side
    print(f"  Comparison table:")
    print(f"  {'Property':>25} | {'q=6':>10} | {'q=28':>10}")
    print(f"  {'-'*25}-+-{'-'*10}-+-{'-'*10}")
    print(f"  {'phi(q)':>25} | {euler_phi(6):>10} | {euler_phi(28):>10}")
    print(f"  {'tau(q)':>25} | {tau(6):>10} | {tau(28):>10}")
    print(f"  {'# distinct c_q values':>25} | {len(values):>10} | {len(values_28):>10}")
    print(f"  {'mu(q)':>25} | {moebius(6):>10} | {moebius(28):>10}")
    print(f"  {'sigma(q)':>25} | {12:>10} | {56:>10}")
    print(f"  {'perfect (sigma=2n)':>25} | {'YES':>10} | {'YES':>10}")

    # ── Test 9: DFT matrix eigenvalues ──
    print(f"\n--- Test 9: 6th roots of unity (DFT eigenvalues) ---")
    print()
    omega = cmath.exp(2j * cmath.pi / 6)
    print(f"  omega = e^(2*pi*i/6) = {omega:.6f}")
    print()
    print(f"  {'k':>3} | {'omega^k':>30} | {'Re':>10} | {'Im':>10}")
    print(f"  {'-'*3}-+-{'-'*30}-+-{'-'*10}-+-{'-'*10}")
    for k in range(6):
        wk = omega ** k
        print(f"  {k:>3} | {str(wk):>30} | {wk.real:>10.6f} | {wk.imag:>10.6f}")

    print()
    print(f"  Primitive 6th roots: omega^1 and omega^5")
    print(f"  c_6(n) = omega^n + omega^(5n) = 2*Re(omega^n)")
    w1 = omega
    w5 = omega ** 5
    print(f"  omega + omega^5 = {(w1 + w5).real:.6f} = c_6(1) = 1  {'PASS' if abs((w1+w5).real - 1) < 1e-10 else 'FAIL'}")

    # ── Summary ──
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    results = [
        ("c_6 values = {1,-1,-2,2}", values == {1, -1, -2, 2}),
        ("c_6(n) = 2*cos(n*pi/3)", max_err < 1e-10),
        ("Sum over period = 0", total == 0),
        ("|values| = tau(6) = 4", len(values) == tau(6)),
        ("values = {1,-1,-phi(6),phi(6)}", values == expected),
        ("mu(6) = 1", mu6 == 1),
        ("Formula = direct computation", all_match),
        ("n=6 is squarefree (mu(6)!=0)", moebius(6) != 0),
        ("n=28 NOT squarefree (mu(28)=0)", moebius(28) == 0),
    ]

    all_pass = True
    for desc, passed in results:
        status = "PASS" if passed else "FAIL"
        icon = "[+]" if passed else "[-]"
        if not passed:
            all_pass = False
        print(f"  {icon} {desc}: {status}")

    print()
    if all_pass:
        print("  Grade: All exact identities verified.")
    else:
        print("  Grade: Some tests failed -- investigate.")

    print()


if __name__ == "__main__":
    main()
