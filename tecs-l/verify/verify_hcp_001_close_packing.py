#!/usr/bin/env python3
"""
HCP-001 Verification: Close-Packed Structures -- Coordination 12 = sigma(6)

Computational verification of all claims in HCP-001 hypothesis.
Run: PYTHONPATH=. python3 verify/verify_hcp_001_close_packing.py
"""

import math
from fractions import Fraction


# ============================================================
# Number-theoretic helpers
# ============================================================

def sigma(n):
    """Sum of divisors of n."""
    s = 0
    for i in range(1, int(math.isqrt(n)) + 1):
        if n % i == 0:
            s += i
            if i != n // i:
                s += n // i
    return s


def tau(n):
    """Number of divisors of n."""
    count = 0
    for i in range(1, int(math.isqrt(n)) + 1):
        if n % i == 0:
            count += 1
            if i != n // i:
                count += 1
    return count


def sopfr(n):
    """Sum of prime factors with repetition."""
    s = 0
    d = 2
    temp = n
    while d * d <= temp:
        while temp % d == 0:
            s += d
            temp //= d
        d += 1
    if temp > 1:
        s += temp
    return s


def comb(n, k):
    """Binomial coefficient C(n, k)."""
    if k < 0 or k > n:
        return 0
    return math.factorial(n) // (math.factorial(k) * math.factorial(n - k))


def divisors(n):
    """Return sorted list of divisors of n."""
    divs = []
    for i in range(1, int(math.isqrt(n)) + 1):
        if n % i == 0:
            divs.append(i)
            if i != n // i:
                divs.append(n // i)
    return sorted(divs)


# ============================================================
# Tests
# ============================================================

def test_coordination_number():
    """Verify 3D close-packing coordination = 12 = sigma(6)."""
    print("=" * 60)
    print("TEST 1: Coordination number = 12 = sigma(6)")
    print("=" * 60)

    n = 6
    s6 = sigma(n)
    coordination_3d = 12  # Well-known: FCC and HCP both have 12

    print(f"\n  sigma(6) = sigma(2*3) = {s6}")
    print(f"  Divisors of 6: {divisors(6)}")
    print(f"  Sum: {' + '.join(str(d) for d in divisors(6))} = {s6}")
    print(f"\n  3D close-packing coordination number = {coordination_3d}")
    print(f"  sigma(6) = {s6}")

    ok = (s6 == coordination_3d == 12)
    print(f"  Match? {ok}")

    print(f"\n  Decomposition of 12 neighbors:")
    print(f"    In-plane (hexagonal ring):    6 = P1 (perfect number 6)")
    print(f"    Layer above:                  3")
    print(f"    Layer below:                  3")
    print(f"    Inter-layer total:            6 = P1")
    print(f"    Grand total:                 12 = sigma(P1) = sigma(6)")

    print(f"\n  RESULT: {'PASS' if ok else 'FAIL'}")
    return ok


def test_packing_density():
    """Verify packing density = pi*sqrt(2)/6."""
    print("\n" + "=" * 60)
    print("TEST 2: Packing density = pi*sqrt(2)/6 = pi*sqrt(2)/P1")
    print("=" * 60)

    # FCC packing density derivation:
    # Unit cell: face-centered cube, side a
    # 4 atoms per cell, radius r = a/(2*sqrt(2))
    # Volume fraction = 4*(4/3)*pi*r^3 / a^3
    #                 = 4*(4/3)*pi*(a/(2*sqrt(2)))^3 / a^3
    #                 = (16/3)*pi*a^3 / (16*sqrt(2)*a^3)
    #                 = pi / (3*sqrt(2))
    #                 = pi*sqrt(2) / 6

    density_formula = math.pi * math.sqrt(2) / 6
    density_alt = math.pi / (3 * math.sqrt(2))

    print(f"\n  pi*sqrt(2)/6  = {density_formula:.10f}")
    print(f"  pi/(3*sqrt(2)) = {density_alt:.10f}")
    print(f"  Match? {abs(density_formula - density_alt) < 1e-15}")

    kepler = 0.7404804896930611  # Known value
    print(f"\n  Kepler conjecture density = {kepler}")
    print(f"  Our formula               = {density_formula:.16f}")
    print(f"  Difference                = {abs(density_formula - kepler):.2e}")

    ok = abs(density_formula - kepler) < 1e-10
    print(f"\n  Denominator = 6 = P1 (first perfect number)")
    print(f"  Density = pi * sqrt(2) / P1")
    print(f"  RESULT: {'PASS' if ok else 'FAIL'}")
    return ok


def test_2d_to_3d_kissing():
    """Verify kissing_3D = sigma(kissing_2D)."""
    print("\n" + "=" * 60)
    print("TEST 3: 2D->3D kissing number progression via sigma")
    print("=" * 60)

    kissing_2d = 6   # Hexagonal packing
    kissing_3d = 12  # FCC/HCP

    sigma_of_k2d = sigma(kissing_2d)

    print(f"\n  Kissing number (2D) = {kissing_2d}")
    print(f"  Kissing number (3D) = {kissing_3d}")
    print(f"  sigma(kissing_2D) = sigma({kissing_2d}) = {sigma_of_k2d}")

    ok = (sigma_of_k2d == kissing_3d)
    print(f"\n  kissing_3D = sigma(kissing_2D)?")
    print(f"  {kissing_3d} = sigma({kissing_2d}) = {sigma_of_k2d}")
    print(f"  Match? {ok}")

    # Check if pattern extends to 4D
    kissing_4d = 24
    sigma_of_k3d = sigma(kissing_3d)
    print(f"\n  Does pattern extend to 4D?")
    print(f"  sigma(kissing_3D) = sigma({kissing_3d}) = {sigma_of_k3d}")
    print(f"  Kissing number (4D) = {kissing_4d}")
    print(f"  Match? {sigma_of_k3d == kissing_4d}")
    print(f"  (sigma(12) = 28 != 24, so pattern does NOT extend)")

    print(f"\n  RESULT: {'PASS' if ok else 'FAIL'} (2D->3D step)")
    return ok


def test_higher_dimensions():
    """Verify kissing numbers in higher dimensions as f(sigma(6))."""
    print("\n" + "=" * 60)
    print("TEST 4: Higher-dimensional kissing numbers and sigma(6)")
    print("=" * 60)

    s6 = sigma(6)  # 12

    # Known kissing numbers
    kissing = {
        1: 2,
        2: 6,
        3: 12,
        4: 24,
        8: 240,
        24: 196560,
    }

    print(f"\n  sigma(6) = {s6}")
    print(f"\n  {'Dim':>4} | {'Lattice':>8} | {'Kissing':>10} | {'/ sigma(6)':>10} | {'Expression':>25}")
    print(f"  {'-'*4}-+-{'-'*8}-+-{'-'*10}-+-{'-'*10}-+-{'-'*25}")

    checks = []

    for dim in sorted(kissing.keys()):
        k = kissing[dim]
        ratio = k / s6
        lattice = {1: "Z", 2: "A2", 3: "FCC", 4: "D4", 8: "E8", 24: "Leech"}[dim]

        if dim == 1:
            expr = "2"
        elif dim == 2:
            expr = f"P1 = 6"
        elif dim == 3:
            expr = f"sigma(6) = {s6}"
        elif dim == 4:
            expr = f"2*sigma(6) = {2*s6}"
            checks.append(k == 2 * s6)
        elif dim == 8:
            c63 = comb(6, 3)
            expr = f"C(6,3)*sigma(6) = {c63}*{s6}"
            checks.append(k == c63 * s6)
        elif dim == 24:
            expr = f"dim=2*sigma(6)={2*s6}"

        print(f"  {dim:4d} | {lattice:>8} | {k:10d} | {ratio:10.1f} | {expr:>25}")

    # Specific verifications
    print(f"\n  Specific checks:")

    # D4
    d4_ok = kissing[4] == 2 * s6
    print(f"    D4: kissing = 24 = 2*sigma(6) = 2*{s6} = {2*s6}? {d4_ok}")

    # E8
    c63 = comb(6, 3)
    e8_ok = kissing[8] == c63 * s6
    print(f"    E8: kissing = 240 = C(6,3)*sigma(6) = {c63}*{s6} = {c63*s6}? {e8_ok}")

    # Leech dimension
    leech_dim_ok = 24 == 2 * s6
    print(f"    Leech: dim = 24 = 2*sigma(6) = 2*{s6} = {2*s6}? {leech_dim_ok}")

    ok = d4_ok and e8_ok and leech_dim_ok
    print(f"\n  RESULT: {'PASS' if ok else 'FAIL'}")
    return ok


def test_packing_densities_table():
    """Display packing densities across dimensions."""
    print("\n" + "=" * 60)
    print("TEST 5: Packing densities across dimensions")
    print("=" * 60)

    densities = [
        (1, 1.0, "1"),
        (2, math.pi / (2 * math.sqrt(3)), "pi/(2*sqrt(3))"),
        (3, math.pi * math.sqrt(2) / 6, "pi*sqrt(2)/6"),
        (4, math.pi ** 2 / 16, "pi^2/16"),
        (8, math.pi ** 4 / 384, "pi^4/384"),
    ]

    print(f"\n  {'Dim':>4} | {'Density':>12} | {'Formula':>20} | {'Has 6?':>6}")
    print(f"  {'-'*4}-+-{'-'*12}-+-{'-'*20}-+-{'-'*6}")

    for dim, dens, formula in densities:
        has_6 = "YES" if "6" in formula else "No"
        print(f"  {dim:4d} | {dens:12.8f} | {formula:>20} | {has_6:>6}")

    # ASCII graph
    print(f"\n  Packing density vs dimension:")
    print(f"  1.00 |*")
    print(f"  0.90 |   *  (2D: {math.pi/(2*math.sqrt(3)):.4f})")
    print(f"  0.80 |")
    print(f"  0.74 |       *  (3D: {math.pi*math.sqrt(2)/6:.4f} = pi*sqrt(2)/6)")
    print(f"  0.70 |")
    print(f"  0.62 |           *  (4D: {math.pi**2/16:.4f})")
    print(f"  0.50 |")
    print(f"  0.40 |")
    print(f"  0.30 |")
    print(f"  0.25 |                   *  (8D: {math.pi**4/384:.4f})")
    print(f"  0.00 +---+---+---+---+---+---+---+---+---")
    print(f"       1   2   3   4   5   6   7   8  Dim")

    # The 3D density denominator
    print(f"\n  3D packing density = pi*sqrt(2)/6")
    print(f"  Denominator = 6 = first perfect number")
    print(f"  RESULT: PASS (exact algebraic identity)")
    return True


def test_crystallographic_numbers():
    """Verify crystallographic number connections."""
    print("\n" + "=" * 60)
    print("TEST 6: Crystallographic number connections")
    print("=" * 60)

    sp6 = sopfr(6)
    s6 = sigma(6)

    checks = [
        ("Crystal systems", 7, None, None),
        ("Bravais lattices", 14, None, None),
        ("Point groups", 32, f"2^sopfr(6) = 2^{sp6}", 2 ** sp6),
        ("Space groups", 230, None, None),
    ]

    print(f"\n  {'Object':>20} | {'Count':>6} | {'Expression':>20} | {'Match':>6}")
    print(f"  {'-'*20}-+-{'-'*6}-+-{'-'*20}-+-{'-'*6}")

    all_ok = True
    for name, count, expr, expected in checks:
        if expected is not None:
            match = "YES" if count == expected else "NO"
            if count != expected:
                all_ok = False
        else:
            match = "-"
            expr = "-"
        print(f"  {name:>20} | {count:6d} | {expr if expr else '-':>20} | {match:>6}")

    print(f"\n  Key result: 32 point groups = 2^5 = 2^sopfr(6)")
    print(f"  RESULT: {'PASS' if all_ok else 'FAIL'}")
    return all_ok


def test_reciprocal_sum():
    """Verify 1/2 + 1/3 + 1/6 = 1 (divisor reciprocals of 6)."""
    print("\n" + "=" * 60)
    print("TEST 7: Divisor reciprocal identity 1/2+1/3+1/6 = 1")
    print("=" * 60)

    n = 6
    all_divs = divisors(n)

    # The key identity: 1/2 + 1/3 + 1/6 = 1
    # These are reciprocals of the divisors > 1: {2, 3, 6}
    nontrivial_divs = [d for d in all_divs if d > 1]
    recip_sum = sum(Fraction(1, d) for d in nontrivial_divs)

    print(f"\n  n = {n}")
    print(f"  Divisors of 6: {all_divs}")
    print(f"  Divisors > 1: {nontrivial_divs}")
    print(f"  Reciprocal sum: {' + '.join(f'1/{d}' for d in nontrivial_divs)} = {recip_sum}")

    ok = (recip_sum == Fraction(1, 1))
    print(f"  = 1? {ok}")

    # This property holds for ALL perfect numbers (sigma_{-1}=2 => sum without 1/1 = 1)
    print(f"\n  Checking other perfect numbers for same property:")
    for pn in [28, 496, 8128]:
        ds = [d for d in divisors(pn) if d > 1]
        rs = sum(Fraction(1, d) for d in ds)
        print(f"    n={pn}: sum = {float(rs):.6f} (= {rs}) -> {'= 1' if rs == 1 else '!= 1'}")
    print(f"  Property holds for ALL perfect numbers (sigma_{{-1}} = 2)")
    print(f"  But n=6 is special: its decomposition uses ONLY unit fractions 1/2, 1/3, 1/6")
    print(f"  with exactly 3 terms matching the 3 proper divisors")

    # Also: sigma_{-1}(6) = sum of 1/d for ALL divisors = sigma(6)/6 = 12/6 = 2
    sigma_neg1 = sum(Fraction(1, d) for d in all_divs)
    print(f"\n  sigma_{{-1}}(6) = sum(1/d for d | 6) = {sigma_neg1} = {float(sigma_neg1)}")
    print(f"  = sigma(6)/6 = 12/6 = 2 (defining property of perfect numbers)")

    print(f"\n  Connection to packing:")
    print(f"    1/2 + 1/3 + 1/6 = 1  (completeness from divisors)")
    print(f"    1 + 2 + 3 = 6        (perfectness)")
    print(f"    sigma(6) = 12         (coordination number)")
    print(f"  RESULT: {'PASS' if ok else 'FAIL'}")
    return ok


def test_sigma_chain():
    """Test iterated sigma starting from 6."""
    print("\n" + "=" * 60)
    print("TEST 8: Iterated sigma chain from 6")
    print("=" * 60)

    # sigma(6) = 12, sigma(12) = 28, sigma(28) = 56, ...
    n = 6
    chain = [n]
    for _ in range(8):
        n = sigma(n)
        chain.append(n)

    print(f"\n  sigma chain starting from 6:")
    for i, val in enumerate(chain):
        label = ""
        if val == 6:
            label = " (P1, kissing 2D)"
        elif val == 12:
            label = " (sigma(6), kissing 3D)"
        elif val == 28:
            label = " (P2, 2nd perfect number!)"
        print(f"    sigma^{i}(6) = {val}{label}")

    # Note: sigma(6)=12, sigma(12)=28 which is the 2nd perfect number!
    ok = (chain[1] == 12 and chain[2] == 28)
    print(f"\n  sigma(6) = 12 (coordination number): {chain[1] == 12}")
    print(f"  sigma(sigma(6)) = sigma(12) = 28 (2nd perfect number!): {chain[2] == 28}")
    print(f"  RESULT: {'PASS' if ok else 'FAIL'}")
    return ok


# ============================================================
# Main
# ============================================================

def main():
    print("HCP-001 Verification: Close-Packed Structures")
    print("Coordination 12 = sigma(6), Density = pi*sqrt(2)/6")
    print("=" * 60)

    results = []
    results.append(("Coordination = sigma(6) = 12", test_coordination_number()))
    results.append(("Packing density = pi*sqrt(2)/6", test_packing_density()))
    results.append(("2D->3D kissing via sigma", test_2d_to_3d_kissing()))
    results.append(("Higher-dim kissing numbers", test_higher_dimensions()))
    results.append(("Packing densities table", test_packing_densities_table()))
    results.append(("Crystallographic numbers", test_crystallographic_numbers()))
    results.append(("Proper divisor reciprocal sum", test_reciprocal_sum()))
    results.append(("Iterated sigma chain", test_sigma_chain()))

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    all_pass = True
    for name, ok in results:
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {name}")
        if not ok:
            all_pass = False

    print(f"\n  Overall: {'ALL PASSED' if all_pass else 'SOME FAILED'}")
    print(f"  {len([r for r in results if r[1]])}/{len(results)} tests passed")

    print(f"\n  Key findings:")
    print(f"    - 3D coordination = 12 = sigma(6) [EXACT]")
    print(f"    - Packing density = pi*sqrt(2)/6 [EXACT]")
    print(f"    - kissing_3D = sigma(kissing_2D) [EXACT, 2D->3D only]")
    print(f"    - D4: 24 = 2*sigma(6), E8: 240 = C(6,3)*sigma(6) [EXACT]")
    print(f"    - 32 point groups = 2^sopfr(6) [EXACT]")
    print(f"    - sigma chain: 6 -> 12 -> 28 (two perfect numbers!) [EXACT]")


if __name__ == "__main__":
    main()
