#!/usr/bin/env python3
"""Theta-Perfect Pattern Verifier

Conjecture: Theta_{4k-1} = sigma(P_k) for perfect numbers P_k.

Investigates whether any standard lattice theta series Theta_L(n)
produces values matching sigma(P_k) = 2*P_k at indices n = 4k-1.

Target sequence (sigma of perfect numbers):
  k=1: sigma(6)    = 12    at index 3
  k=2: sigma(28)   = 56    at index 7
  k=3: sigma(496)  = 992   at index 11
  k=4: sigma(8128) = 16256 at index 15
  k=5: sigma(33550336) = 67100672 at index 19

Lattice theta series tested:
  1. Z^d lattice: r_d(n) = #{(x1,...,xd) : x1^2+...+xd^2 = n}
  2. D_d lattice
  3. E8 lattice (Jacobi theta series)
  4. Leech lattice (Lambda_24)
  5. Jacobi theta_3(0,q) powers

Includes Texas Sharpshooter test for statistical significance.

Usage:
  python3 calc/theta_perfect_pattern.py
  python3 calc/theta_perfect_pattern.py --max-dim 32
  python3 calc/theta_perfect_pattern.py --texas
"""

import argparse
import math
import sys
from fractions import Fraction

# ═══════════════════════════════════════════════════════════════
# Perfect Number Arithmetic
# ═══════════════════════════════════════════════════════════════

# Known Mersenne primes (exponents)
MERSENNE_EXPONENTS = [2, 3, 5, 7, 13, 17, 19, 31]

def perfect_number(k):
    """k-th even perfect number (1-indexed). P_1=6, P_2=28, ..."""
    p = MERSENNE_EXPONENTS[k - 1]
    return 2**(p - 1) * (2**p - 1)

def sigma_perfect(k):
    """sigma(P_k) = 2 * P_k for perfect numbers."""
    return 2 * perfect_number(k)


# ═══════════════════════════════════════════════════════════════
# Lattice Theta Series Computations
# ═══════════════════════════════════════════════════════════════

def r_squares(d, n):
    """Number of representations of n as sum of d squares.
    r_d(n) = #{(x1,...,xd) in Z^d : x1^2 + ... + xd^2 = n}
    Uses recursive approach for moderate d and n.
    """
    if n < 0:
        return 0
    if n == 0:
        return 1
    if d == 0:
        return 0
    if d == 1:
        # n = x^2, so x = +/-sqrt(n) if perfect square
        s = int(math.isqrt(n))
        if s * s == n:
            return 2 if s > 0 else 1
        return 0
    # Recursive: sum over x_d from -floor(sqrt(n)) to floor(sqrt(n))
    count = 0
    limit = int(math.isqrt(n))
    for x in range(-limit, limit + 1):
        count += r_squares(d - 1, n - x * x)
    return count


def r_squares_fast(d, n_max):
    """Compute r_d(n) for n=0..n_max using generating function (theta_3 power).
    Returns list of coefficients.
    """
    # theta_3(q) = sum_{m=-inf}^{inf} q^{m^2} = 1 + 2*sum_{m=1}^{inf} q^{m^2}
    # r_d(n) = coefficient of q^n in theta_3(q)^d

    # Start with theta_3 coefficients up to q^n_max
    theta = [0] * (n_max + 1)
    theta[0] = 1
    m = 1
    while m * m <= n_max:
        theta[m * m] += 2
        m += 1

    # Raise to d-th power by repeated convolution
    result = [0] * (n_max + 1)
    result[0] = 1  # Start with 1 (0th power)

    for _ in range(d):
        new_result = [0] * (n_max + 1)
        for i in range(n_max + 1):
            if result[i] == 0:
                continue
            for j in range(n_max + 1 - i):
                if theta[j] == 0:
                    continue
                new_result[i + j] += result[i] * theta[j]
        result = new_result

    return result


def e8_theta_series(n_max):
    """Theta series of E8 lattice.
    Theta_E8(q) = 1 + 240*sum_{n=1}^{inf} sigma_3(n)*q^n
    where sigma_3(n) = sum of cubes of divisors of n.

    Coefficients give number of vectors of norm 2n in E8.
    Actually: number of vectors of squared norm 2n.
    The coefficient of q^n is the number of lattice vectors with |v|^2 = 2n.
    """
    def sigma_k(n, k=3):
        """Sum of k-th powers of divisors."""
        s = 0
        for d in range(1, n + 1):
            if n % d == 0:
                s += d**k
        return s

    coeffs = [0] * (n_max + 1)
    coeffs[0] = 1
    for n in range(1, n_max + 1):
        coeffs[n] = 240 * sigma_k(n, 3)
    return coeffs


def d_lattice_theta(d, n_max):
    """Theta series of D_d lattice.
    D_d = {x in Z^d : sum(x_i) is even}
    Theta_D_d(q) = (theta_3(q)^d + theta_4(q)^d) / 2
    where theta_4(q) = sum_{m=-inf}^{inf} (-1)^m q^{m^2}
    """
    # theta_3 coefficients
    theta3 = [0] * (n_max + 1)
    theta3[0] = 1
    m = 1
    while m * m <= n_max:
        theta3[m * m] += 2
        m += 1

    # theta_4 coefficients: (-1)^m factor
    theta4 = [0] * (n_max + 1)
    theta4[0] = 1
    m = 1
    while m * m <= n_max:
        theta4[m * m] += 2 * ((-1)**m)
        m += 1

    # Raise each to d-th power
    def poly_power(coeffs, d, n_max):
        result = [0] * (n_max + 1)
        result[0] = 1
        for _ in range(d):
            new_result = [0] * (n_max + 1)
            for i in range(n_max + 1):
                if result[i] == 0:
                    continue
                for j in range(n_max + 1 - i):
                    if coeffs[j] == 0:
                        continue
                    new_result[i + j] += result[i] * coeffs[j]
            result = new_result
        return result

    t3d = poly_power(theta3, d, n_max)
    t4d = poly_power(theta4, d, n_max)

    # Average
    result = [0] * (n_max + 1)
    for i in range(n_max + 1):
        val = t3d[i] + t4d[i]
        assert val % 2 == 0, f"D_{d} theta at {i}: {val} not even"
        result[i] = val // 2

    return result


def leech_theta_series(n_max):
    """Theta series of the Leech lattice Lambda_24.
    The coefficient of q^n gives the number of vectors of norm 2n.

    Known first few coefficients:
    Theta = 1 + 196560*q^2 + 16773120*q^3 + 398034000*q^4 + ...

    No vectors of norm 2 (kissing number property).
    For norm 2n: use the formula involving Ramanujan tau and E_12.

    Theta_Leech(q) = (theta_3^24 + theta_4^24 + theta_2^24) / 3 + ... (complicated)

    Simpler: use known formula with Eisenstein series
    Theta = 1 + sum_{n>=2} a(n) q^n where
    a(n) = (65520/691) * (sigma_11(n) - tau(n))
    where tau is Ramanujan's tau function.
    """
    def sigma_11(n):
        s = 0
        for d in range(1, n + 1):
            if n % d == 0:
                s += d**11
        return s

    def ramanujan_tau(n):
        """Ramanujan tau function via q-expansion of Delta.
        Delta(q) = q * prod_{n>=1} (1-q^n)^24
        """
        if n == 0:
            return 0
        # Compute product (1-q^n)^24 up to q^n
        # Then tau(n) = coefficient of q^n in Delta = q * product
        # So tau(n) = coefficient of q^{n-1} in product
        prod = [0] * (n + 1)
        prod[0] = 1
        for k in range(1, n + 1):
            # Multiply by (1 - q^k)^24
            # Use binomial: (1-x)^24 = sum C(24,j)(-1)^j x^j
            # But more efficient: multiply by (1-q^k) twenty-four times
            for _ in range(24):
                for i in range(n, k - 1, -1):
                    prod[i] -= prod[i - k]
        # tau(n) = coefficient of q^{n-1} in prod (since Delta = q * prod)
        if n - 1 <= n:
            return prod[n - 1]
        return 0

    coeffs = [0] * (n_max + 1)
    coeffs[0] = 1
    # No norm-2 vectors in Leech lattice, so coeffs[1] = 0
    for n in range(1, n_max + 1):
        s11 = sigma_11(n)
        tau_n = ramanujan_tau(n)
        # Number of vectors of norm 2n
        val = Fraction(65520, 691) * (s11 - tau_n)
        coeffs[n] = int(val)

    return coeffs


# ═══════════════════════════════════════════════════════════════
# Texas Sharpshooter Test
# ═══════════════════════════════════════════════════════════════

def texas_sharpshooter_test(matches, total_comparisons, total_lattices):
    """Compute p-value for the pattern being coincidental.

    matches: number of (lattice, index) pairs where Theta_n = sigma(P_k)
    total_comparisons: total number of (lattice, index) pairs checked
    total_lattices: number of different lattice types checked
    """
    from math import comb, factorial

    # Bonferroni-corrected probability
    # Each comparison has probability p_single of matching by chance
    # For large integers, matching exactly is very unlikely
    # Estimate: for target T, probability a random theta coefficient = T
    # is roughly 1/T (generous upper bound)

    targets = [sigma_perfect(k) for k in range(1, 6)]

    # Expected matches under null hypothesis
    # Each coefficient could match any of 5 targets
    # P(match) ~ sum(1/T_k) for each coefficient (very generous)
    p_single = sum(1.0 / t for t in targets)

    expected = total_comparisons * p_single

    # Poisson approximation for number of matches
    import math as m
    if matches == 0:
        p_value = 1.0
    else:
        # P(X >= matches) where X ~ Poisson(expected)
        p_value = 0.0
        for k in range(matches):
            p_value += (expected**k * m.exp(-expected)) / m.factorial(k)
        p_value = 1.0 - p_value

    # Bonferroni correction for multiple lattice types
    p_value_corrected = min(1.0, p_value * total_lattices)

    return {
        'matches': matches,
        'total_comparisons': total_comparisons,
        'total_lattices': total_lattices,
        'expected_by_chance': expected,
        'p_value_raw': p_value,
        'p_value_corrected': p_value_corrected,
    }


# ═══════════════════════════════════════════════════════════════
# Main Analysis
# ═══════════════════════════════════════════════════════════════

def print_section(title):
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}")


def main():
    parser = argparse.ArgumentParser(description='Theta-Perfect Pattern Verifier')
    parser.add_argument('--max-dim', type=int, default=24,
                        help='Maximum lattice dimension to test (default: 24)')
    parser.add_argument('--texas', action='store_true',
                        help='Run Texas Sharpshooter test only')
    parser.add_argument('--verbose', action='store_true',
                        help='Show all theta coefficients')
    args = parser.parse_args()

    print("=" * 70)
    print("  THETA-PERFECT PATTERN VERIFIER")
    print("  Conjecture: Theta_{4k-1} = sigma(P_k)")
    print("=" * 70)

    # ── Step 1: Display target values ──
    print_section("1. TARGET VALUES: sigma(P_k) = 2 * P_k")
    print()
    print("  | k | Mersenne p | P_k          | sigma(P_k)     | Index 4k-1 |")
    print("  |---|------------|--------------|----------------|------------|")
    for k in range(1, 6):
        p = MERSENNE_EXPONENTS[k - 1]
        pk = perfect_number(k)
        spk = sigma_perfect(k)
        idx = 4 * k - 1
        print(f"  | {k} | {p:<10} | {pk:<12} | {spk:<14} | {idx:<10} |")

    print()
    print("  Note: For ANY perfect number n, sigma(n) = 2n (definition).")
    print("  sigma(P_k) = 2^p * (2^p - 1) where p = Mersenne exponent.")
    print()
    print("  Factored form of sigma(P_k):")
    for k in range(1, 6):
        p = MERSENNE_EXPONENTS[k - 1]
        print(f"    k={k}: 2^{p} * (2^{p}-1) = {2**p} * {2**p - 1} = {sigma_perfect(k)}")

    # ── Step 2: Z^d lattice theta series ──
    print_section("2. Z^d LATTICE: r_d(n) = #{sums of d squares = n}")

    targets = {4*k - 1: sigma_perfect(k) for k in range(1, 6)}
    n_max_small = max(targets.keys())  # 19

    # We need r_d(n) for various d and n in {3, 7, 11, 15, 19}
    # For computational feasibility, limit d
    max_dim_zd = min(args.max_dim, 16)  # Z^d convolution gets expensive

    matches_zd = []
    print()
    print(f"  Testing Z^d for d=1..{max_dim_zd}, at indices {{3, 7, 11, 15, 19}}")
    print()
    print("  | d  | r_d(3)  | r_d(7)  | r_d(11)  | r_d(15)  | r_d(19)  |")
    print("  |----|---------|---------|----------|----------|----------|")

    for d in range(1, max_dim_zd + 1):
        coeffs = r_squares_fast(d, n_max_small)
        vals = []
        for idx in [3, 7, 11, 15, 19]:
            v = coeffs[idx] if idx < len(coeffs) else 0
            vals.append(v)
            # Check match
            if idx in targets and v == targets[idx]:
                matches_zd.append((f"Z^{d}", idx, v))

        # Format: right-align
        line = f"  | {d:<2} "
        for v in vals:
            line += f"| {v:<7} "
        line += "|"
        print(line)

    print()
    print("  Target values for comparison:")
    print(f"    r_d(3)=12, r_d(7)=56, r_d(11)=992, r_d(15)=16256, r_d(19)=67100672")

    if matches_zd:
        print()
        print("  *** MATCHES FOUND in Z^d lattices: ***")
        for lat, idx, val in matches_zd:
            k = (idx + 1) // 4
            print(f"    {lat} at index {idx}: Theta={val} = sigma(P_{k})")
    else:
        print()
        print("  No exact matches found in Z^d lattices.")

    # ── Step 3: E8 lattice theta series ──
    print_section("3. E8 LATTICE: Theta_E8(q) = 1 + 240*sum sigma_3(n)*q^n")

    e8 = e8_theta_series(n_max_small)
    matches_e8 = []

    print()
    print("  | n  | Theta_E8(n) | Target sigma(P_k) | Match? |")
    print("  |----|-------------|-------------------|--------|")
    for n in range(0, n_max_small + 1):
        target_str = ""
        match_str = ""
        if n in targets:
            target_str = str(targets[n])
            match_str = "YES" if e8[n] == targets[n] else "no"
            if e8[n] == targets[n]:
                k = (n + 1) // 4
                matches_e8.append(("E8", n, e8[n]))
        print(f"  | {n:<2} | {e8[n]:<11} | {target_str:<17} | {match_str:<6} |")

    print()
    print("  E8 coefficients grow as 240*sigma_3(n).")
    print("  At n=1: 240*1 = 240 (well-known 240 roots of E8).")

    # ── Step 4: D_d lattice theta series (small d) ──
    print_section("4. D_d LATTICE THETA SERIES")

    max_dim_dd = min(args.max_dim, 12)
    matches_dd = []

    print()
    print(f"  Testing D_d for d=2..{max_dim_dd}")
    print()

    for d in range(2, max_dim_dd + 1):
        dd_coeffs = d_lattice_theta(d, n_max_small)
        print(f"  D_{d} theta series:")
        for idx in [3, 7, 11, 15, 19]:
            v = dd_coeffs[idx] if idx < len(dd_coeffs) else 0
            target_str = ""
            match_str = ""
            if idx in targets:
                target_str = f"target={targets[idx]}"
                if v == targets[idx]:
                    match_str = " *** MATCH ***"
                    matches_dd.append((f"D_{d}", idx, v))
            print(f"    Theta[{idx}] = {v}  {target_str}{match_str}")

    # ── Step 5: Leech lattice ──
    print_section("5. LEECH LATTICE Lambda_24")

    leech = leech_theta_series(min(n_max_small, 10))
    matches_leech = []

    print()
    print("  | n  | #vectors norm 2n | Target sigma(P_k) | Match? |")
    print("  |----|-----------------|-------------------|--------|")
    for n in range(0, min(n_max_small + 1, len(leech))):
        target_str = ""
        match_str = ""
        if n in targets:
            target_str = str(targets[n])
            match_str = "YES" if leech[n] == targets[n] else "no"
            if leech[n] == targets[n]:
                k = (n + 1) // 4
                matches_leech.append(("Leech", n, leech[n]))
        print(f"  | {n:<2} | {leech[n]:<15} | {target_str:<17} | {match_str:<6} |")

    # ── Step 6: Search for ratio patterns ──
    print_section("6. RATIO ANALYSIS: Theta(4k-1) / sigma(P_k)")

    print()
    print("  Looking for consistent ratios or offsets across lattice types...")
    print()

    # Check Z^d for interesting near-misses
    print("  Z^d lattice ratios at target indices:")
    print("  | d  | r_d(3)/12 | r_d(7)/56 | r_d(11)/992 | r_d(15)/16256 |")
    print("  |----|-----------|-----------|-------------|---------------|")
    for d in range(1, max_dim_zd + 1):
        coeffs = r_squares_fast(d, n_max_small)
        ratios = []
        for idx, tgt in [(3, 12), (7, 56), (11, 992), (15, 16256)]:
            v = coeffs[idx] if idx < len(coeffs) else 0
            if tgt > 0:
                ratios.append(v / tgt)
            else:
                ratios.append(float('inf'))
        print(f"  | {d:<2} | {ratios[0]:<9.4f} | {ratios[1]:<9.4f} | {ratios[2]:<11.6f} | {ratios[3]:<13.8f} |")

    # ── Step 7: Alternative indexing schemes ──
    print_section("7. ALTERNATIVE INDEXING: sigma(P_k) in theta series")

    print()
    print("  Instead of fixed index 4k-1, search WHERE sigma(P_k) appears")
    print("  in various theta series.")
    print()

    # For Z^d, find which index gives the target value
    for k in range(1, 4):  # Only first 3 (values get huge)
        target = sigma_perfect(k)
        print(f"  sigma(P_{k}) = {target}:")
        for d in [4, 6, 8, 12, 16]:
            if d > max_dim_zd:
                continue
            coeffs = r_squares_fast(d, max(50, 4*k))
            found_at = [n for n in range(len(coeffs)) if coeffs[n] == target]
            if found_at:
                print(f"    Z^{d}: appears at indices {found_at}")

    # ── Step 8: Modular form connection ──
    print_section("8. MODULAR FORM ANALYSIS")

    print()
    print("  sigma(P_k) = 2^p * (2^p - 1) = 2^p * M_p")
    print("  where M_p is Mersenne prime.")
    print()
    print("  Eisenstein series E_k(q) = 1 - (2k/B_k) * sum sigma_{k-1}(n) q^n")
    print("  where B_k = Bernoulli number.")
    print()
    print("  Checking: sigma_1(n) at indices 4k-1:")

    def sigma_1(n):
        return sum(d for d in range(1, n+1) if n % d == 0)

    print("  | n (=4k-1) | sigma_1(n) | 2*sigma_1(n) | Target sigma(P_k) | Ratio |")
    print("  |-----------|------------|--------------|-------------------|-------|")
    for k in range(1, 6):
        n = 4 * k - 1
        s1 = sigma_1(n)
        target = sigma_perfect(k)
        ratio = target / (2 * s1) if s1 > 0 else float('inf')
        print(f"  | {n:<9} | {s1:<10} | {2*s1:<12} | {target:<17} | {ratio:<5.2f} |")

    print()
    print("  Checking: sigma_3(n) at indices 4k-1:")

    def sigma_3(n):
        return sum(d**3 for d in range(1, n+1) if n % d == 0)

    print("  | n (=4k-1) | sigma_3(n) | 240*sigma_3(n) | Target sigma(P_k) |")
    print("  |-----------|------------|----------------|-------------------|")
    for k in range(1, 6):
        n = 4 * k - 1
        s3 = sigma_3(n)
        target = sigma_perfect(k)
        print(f"  | {n:<9} | {s3:<10} | {240*s3:<14} | {target:<17} |")

    # ── Step 9: Direct formula search ──
    print_section("9. DIRECT FORMULA SEARCH")

    print()
    print("  Is there ANY function f(n) s.t. f(4k-1) = 2^p*(2^p-1)?")
    print()
    print("  Testing simple candidates on n = {3, 7, 11, 15, 19}:")
    print()

    indices = [3, 7, 11, 15, 19]
    targets_list = [sigma_perfect(k) for k in range(1, 6)]

    # Check: a * 2^(bn+c) + d patterns
    print("  Arithmetic progression of indices: 3, 7, 11, 15, 19 = 4k-1")
    print("  Corresponding Mersenne exponents:  2, 3, 5, 7, 13")
    print()
    print("  Note: Mersenne exponents are NOT an arithmetic progression!")
    print("  So no simple formula f(4k-1) can produce sigma(P_k).")
    print("  The mapping k -> p_k (k-th Mersenne prime exponent) is irregular.")
    print()

    # Check if the pattern is really about theta of DIFFERENT lattices
    # i.e., Theta_{L_k}(something) = sigma(P_k) where L_k varies with k
    print("  Alternative: Theta at FIXED index, varying lattice dimension?")
    print("  r_d(1) for various d (representations of 1 as sum of d squares):")
    print("  r_d(1) = 2d (always, since +/-1 in any coordinate, rest 0)")
    print()
    print("  Check: is there d_k such that r_{d_k}(1) = sigma(P_k)?")
    for k in range(1, 6):
        target = sigma_perfect(k)
        d_needed = target // 2 if target % 2 == 0 else None
        check = f"d={d_needed}, r_{d_needed}(1)=2*{d_needed}={2*d_needed}" if d_needed else "N/A"
        match = "YES" if d_needed and 2*d_needed == target else "no"
        print(f"    k={k}: sigma(P_{k})={target}, need d={d_needed}  -> {match}")

    print()
    print("  TRIVIAL MATCH: r_d(1) = 2d, so r_{sigma(P_k)/2}(1) = sigma(P_k)")
    print("  This is not a deep pattern -- it holds for ANY even number.")

    # ── Step 10: Collect all matches and do Texas test ──
    print_section("10. TEXAS SHARPSHOOTER TEST")

    all_matches = matches_zd + matches_e8 + matches_dd + matches_leech
    total_comparisons = (max_dim_zd * 5) + (n_max_small + 1) + ((max_dim_dd - 1) * 5) + min(n_max_small + 1, len(leech))
    total_lattices = max_dim_zd + 1 + (max_dim_dd - 1) + 1  # Z^d + E8 + D_d + Leech

    print()
    print(f"  Total lattice types tested:  {total_lattices}")
    print(f"  Total comparisons made:      {total_comparisons}")
    print(f"  Exact matches found:         {len(all_matches)}")

    if all_matches:
        print()
        print("  Match details:")
        for lat, idx, val in all_matches:
            k = (idx + 1) // 4
            print(f"    {lat}, index {idx}: Theta = {val} = sigma(P_{k})")

    result = texas_sharpshooter_test(len(all_matches), total_comparisons, total_lattices)
    print()
    print(f"  Expected matches by chance:   {result['expected_by_chance']:.4f}")
    print(f"  p-value (raw):                {result['p_value_raw']:.6f}")
    print(f"  p-value (Bonferroni):         {result['p_value_corrected']:.6f}")

    if result['p_value_corrected'] < 0.01:
        grade = "structural"
        emoji = "star star"
    elif result['p_value_corrected'] < 0.05:
        grade = "weak evidence"
        emoji = "star"
    else:
        grade = "not significant (likely coincidence)"
        emoji = "circle"

    print(f"  Assessment:                   {grade}")

    # ── Summary ──
    print_section("SUMMARY")

    print()
    print("  Conjecture: Theta_{4k-1} = sigma(P_k) for perfect numbers P_k")
    print()

    if not all_matches:
        print("  RESULT: NO exact matches found in standard lattice theta series.")
        print()
        print("  Key obstacles:")
        print("    1. The indices 4k-1 = {3,7,11,15,19} are arithmetically regular")
        print("       but perfect number growth (via Mersenne primes) is irregular.")
        print("    2. Lattice theta coefficients grow polynomially (Z^d) or via")
        print("       divisor sums (E8, Leech), not matching 2^p*(2^p-1) growth.")
        print("    3. The Leech lattice has no norm-2 vectors, so many early")
        print("       coefficients are 0.")
        print()
        print("  The conjecture Theta_{4k-1} = sigma(P_k) is REFUTED")
        print("  for all standard lattice theta series tested (Z^d, D_d, E8, Leech).")
        print()
        print("  The only trivial connection found:")
        print("    r_{sigma(P_k)/2}(1) = sigma(P_k)  [holds for ANY even number]")
    else:
        print("  Matches found! See details above.")
        print(f"  Statistical significance: {grade}")

    # Grade
    print()
    if not all_matches:
        print("  GRADE: REFUTED (no match in any standard lattice theta series)")
    elif result['p_value_corrected'] < 0.01:
        print("  GRADE: structural discovery (p < 0.01)")
    elif result['p_value_corrected'] < 0.05:
        print("  GRADE: weak evidence (p < 0.05)")
    else:
        print("  GRADE: coincidence (p > 0.05)")

    return 0


if __name__ == '__main__':
    sys.exit(main())
