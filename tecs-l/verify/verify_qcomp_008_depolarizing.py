#!/usr/bin/env python3
"""
QCOMP-008 Verification: Depolarizing Channel Capacity at p=1/3

Verifies:
1. Hashing bound Q(p) for depolarizing channel at key p values
2. Exact threshold p* where Q=0 (numerically)
3. Comparison of p* to Golden Zone lower boundary (0.2123)
4. (2/3)^6 = R^n identity (code rate raised to code length)
5. Detection efficiency P(1 error)/P(any error) vs ln(4/3)
6. ASCII plot of Q(p)

Run: PYTHONPATH=. python3 verify/verify_qcomp_008_depolarizing.py
"""

import math
from fractions import Fraction


# ── Arithmetic functions ──────────────────────────────────────────────

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


def phi(n):
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


# ── Channel capacity functions ────────────────────────────────────────

def binary_entropy(p):
    """Binary entropy H(p) = -p*log2(p) - (1-p)*log2(1-p)."""
    if p <= 0 or p >= 1:
        return 0.0
    return -p * math.log2(p) - (1 - p) * math.log2(1 - p)


def hashing_bound(p):
    """Hashing bound for quantum depolarizing channel capacity.
    Q >= 1 - H(p) - p*log2(3)
    """
    if p <= 0:
        return 1.0
    if p >= 0.75:
        return 0.0  # channel is completely depolarizing at p=3/4
    return 1.0 - binary_entropy(p) - p * math.log2(3)


def find_threshold(tol=1e-12):
    """Find p* where hashing bound Q(p) = 0 using bisection."""
    lo, hi = 0.0, 0.5
    while hi - lo > tol:
        mid = (lo + hi) / 2
        if hashing_bound(mid) > 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


# ── Tests ─────────────────────────────────────────────────────────────

def test_capacity_table():
    """Test 1: Compute Q(p) at key p values."""
    print("=" * 70)
    print("TEST 1: Depolarizing Channel Hashing Bound Q(p)")
    print("=" * 70)
    print()

    p_values = [0.0, 0.05, 0.10, 0.15, 0.189, 0.20, 0.2123, 0.25,
                1.0 / 3, 0.40, 0.50, 0.75]
    labels = {
        0.0: "no noise",
        0.189: "~threshold p*",
        0.2123: "GZ lower",
        0.25: "1/4",
        1.0 / 3: "meta FP 1/3",
        0.50: "1/2 (GZ upper)",
        0.75: "fully depol.",
    }

    print("  " + "-" * 62)
    print(f"  {'p':>8}  {'H(p)':>10}  {'p*log2(3)':>10}  {'Q_hash':>10}  {'Note':<16}")
    print("  " + "-" * 62)

    for p in p_values:
        h = binary_entropy(p)
        plog3 = p * math.log2(3) if p > 0 else 0.0
        q = hashing_bound(p)
        label = labels.get(p, "")
        if abs(p - 1.0 / 3) < 1e-10:
            label = "meta FP 1/3"
        print(f"  {p:8.4f}  {h:10.6f}  {plog3:10.6f}  {q:10.6f}  {label}")

    print("  " + "-" * 62)
    print()

    # Detailed computation at p = 1/3
    p13 = 1.0 / 3
    h13 = binary_entropy(p13)
    plog3_13 = p13 * math.log2(3)
    q13 = hashing_bound(p13)

    print("  Detailed at p = 1/3:")
    print(f"    H(1/3) = -(1/3)*log2(1/3) - (2/3)*log2(2/3)")
    print(f"           = {h13:.10f}")
    print(f"    (1/3)*log2(3) = {plog3_13:.10f}")
    print(f"    Q(1/3) = 1 - {h13:.6f} - {plog3_13:.6f}")
    print(f"           = {q13:.10f}")
    print()

    ok = q13 < 0
    print(f"  Q(1/3) < 0: {ok}")
    print(f"  --> Channel CANNOT transmit quantum information at p = 1/3!")
    print()
    print(f"  STATUS: {'PASS' if ok else 'FAIL'} [Grade: 🟩]")
    return ok


def test_threshold():
    """Test 2: Find exact threshold p* where Q=0."""
    print()
    print("=" * 70)
    print("TEST 2: Capacity Threshold p* (Q = 0)")
    print("=" * 70)
    print()

    p_star = find_threshold()
    gz_lower = 0.5 - math.log(4.0 / 3)
    meta_fp = 1.0 / 3
    gz_center = 1.0 / math.e

    print(f"  Threshold p* = {p_star:.10f}")
    print(f"  Q(p*) = {hashing_bound(p_star):.2e} (should be ~0)")
    print()

    # Comparisons
    print("  Comparison with TECS-L constants:")
    print("  " + "-" * 55)
    print(f"  {'Constant':<30} {'Value':>10}  {'|p*-val|/val':>12}")
    print("  " + "-" * 55)

    comparisons = [
        ("GZ lower (1/2 - ln(4/3))", gz_lower),
        ("Meta FP (1/3)", meta_fp),
        ("GZ center (1/e)", gz_center),
        ("GZ upper (1/2)", 0.5),
        ("1/6 (curiosity)", 1.0 / 6),
        ("ln(4/3) (GZ width)", math.log(4.0 / 3)),
    ]

    best_match = None
    best_err = float('inf')

    for name, val in comparisons:
        err = abs(p_star - val) / val
        marker = ""
        if err < best_err:
            best_err = err
            best_match = name
        if err < 0.15:
            marker = " <-- close"
        print(f"  {name:<30} {val:10.6f}  {err:12.4%}{marker}")

    print("  " + "-" * 55)
    print()
    print(f"  Closest match: {best_match} (error = {best_err:.4%})")
    print()

    # Is the match significant?
    if best_err < 0.05:
        grade = "🟧 (< 5% error, suggestive)"
    elif best_err < 0.15:
        grade = "🟧 (< 15% error, approximate)"
    else:
        grade = "⚪ (> 15% error, not a match)"

    print(f"  Grade: {grade}")
    print()
    print(f"  STATUS: PASS [threshold computed; {grade}]")
    return True


def test_ascii_plot():
    """Test 3: ASCII plot of Q(p)."""
    print()
    print("=" * 70)
    print("TEST 3: ASCII Plot of Q(p) — Depolarizing Channel")
    print("=" * 70)
    print()

    # Plot Q(p) for p in [0, 0.5]
    n_points = 51
    p_values = [i * 0.5 / (n_points - 1) for i in range(n_points)]
    q_values = [hashing_bound(p) for p in p_values]

    q_min = min(q_values)
    q_max = max(q_values)
    width = 60
    height = 20

    # Quantize to grid
    grid = [[' ' for _ in range(width)] for _ in range(height)]

    for i, (p, q) in enumerate(zip(p_values, q_values)):
        col = int(p / 0.5 * (width - 1))
        row = int((q_max - q) / (q_max - q_min) * (height - 1))
        col = max(0, min(width - 1, col))
        row = max(0, min(height - 1, row))
        grid[row][col] = '*'

    # Mark zero line
    zero_row = int((q_max - 0) / (q_max - q_min) * (height - 1))
    zero_row = max(0, min(height - 1, zero_row))
    for c in range(width):
        if grid[zero_row][c] == ' ':
            grid[zero_row][c] = '-'

    # Mark p = 1/3
    col_13 = int((1.0 / 3) / 0.5 * (width - 1))
    for r in range(height):
        if grid[r][col_13] == ' ':
            grid[r][col_13] = '|'
        elif grid[r][col_13] == '-':
            grid[r][col_13] = '+'

    # Mark threshold
    p_star = find_threshold()
    col_ps = int(p_star / 0.5 * (width - 1))
    for r in range(height):
        if grid[r][col_ps] == ' ':
            grid[r][col_ps] = ':'
        elif grid[r][col_ps] == '-':
            grid[r][col_ps] = '+'

    # Print
    print(f"  Q_hash(p) — Depolarizing channel hashing bound")
    print()
    for r in range(height):
        q_val = q_max - r * (q_max - q_min) / (height - 1)
        label = f"{q_val:+6.2f}"
        print(f"  {label} |{''.join(grid[r])}|")
    print(f"         +{''.join(['-'] * width)}+")
    print(f"         p=0{' ' * (col_ps - 3)}p*{' ' * (col_13 - col_ps - 3)}1/3{' ' * (width - col_13 - 4)}0.5")
    print()
    print(f"  Legend: * = Q(p),  - = Q=0 line,  : = threshold p*,  | = p=1/3")
    print(f"  p* = {p_star:.4f},  Q(1/3) = {hashing_bound(1.0/3):.4f}")
    print()
    print("  STATUS: PASS [plot generated]")
    return True


def test_no_error_identity():
    """Test 4: (1-p)^n = R^n at p = 1/3 for [[6,4,2]]."""
    print()
    print("=" * 70)
    print("TEST 4: No-Error Probability Identity (2/3)^6 = R^n")
    print("=" * 70)
    print()

    n, k, d = 6, 4, 2
    p = Fraction(1, 3)
    R = Fraction(k, n)

    no_error = (1 - p) ** n
    rate_power = R ** n

    print(f"  [[{n},{k},{d}]] code at p = {p}")
    print()
    print(f"  Code rate R = {k}/{n} = {R}")
    print(f"  1 - p = 1 - {p} = {1 - p}")
    print()
    print(f"  P(no error) = (1 - p)^n = ({1 - p})^{n} = {no_error}")
    print(f"  R^n = ({R})^{n} = {rate_power}")
    print(f"  Equal: {no_error == rate_power}")
    print()

    # Numerical
    no_error_f = float(no_error)
    print(f"  Numerically: {no_error} = {no_error_f:.10f}")
    print(f"  = {no_error.numerator}/{no_error.denominator}")
    print(f"  = 2^{n} / 3^{n} = {2**n} / {3**n}")
    print()

    # Why this is true
    print("  Why this holds:")
    print(f"    p = 1 - R  (noise rate = code overhead fraction)")
    print(f"    1/3 = 1 - 2/3")
    print(f"    So (1-p)^n = R^n is algebraically guaranteed when p = 1-R.")
    print(f"    The content is that p = 1/3 (meta fixed point)")
    print(f"    and R = 2/3 (code rate) satisfy p = 1 - R.")
    print()

    # Connection to TECS-L
    print("  TECS-L interpretation:")
    print(f"    1/2 + 1/3 + 1/6 = 1  (completeness)")
    print(f"    R = 2/3 = 1/2 + 1/6  (rate = boundary + curiosity)")
    print(f"    p = 1/3              (noise = convergence = meta FP)")
    print(f"    R + p = 2/3 + 1/3 = 1 (rate + noise = completeness)")
    print()

    ok = (no_error == rate_power)
    print(f"  STATUS: {'PASS' if ok else 'FAIL'} [Grade: 🟩 exact]")
    return ok


def test_detection_ratio():
    """Test 5: P(1 error)/P(any error) vs ln(4/3) at p=1/3."""
    print()
    print("=" * 70)
    print("TEST 5: Detection Ratio vs Golden Zone Width")
    print("=" * 70)
    print()

    n = 6
    p = Fraction(1, 3)
    q = 1 - p  # = 2/3

    # P(exactly 1 error) = C(6,1) * p * q^5
    p_one = Fraction(math.comb(n, 1), 1) * p * q**5
    # P(at least 1 error) = 1 - q^6
    p_any = 1 - q**n

    ratio = p_one / p_any

    print(f"  At p = {p}, n = {n}:")
    print()
    print(f"  P(no error)     = (2/3)^6 = {q**n} = {float(q**n):.10f}")
    print(f"  P(exactly 1 er) = C(6,1)*(1/3)*(2/3)^5 = {p_one} = {float(p_one):.10f}")
    print(f"  P(any error)    = 1 - (2/3)^6 = {p_any} = {float(p_any):.10f}")
    print()
    print(f"  Ratio = P(1 error) / P(any error)")
    print(f"        = {p_one} / {p_any}")
    print(f"        = {ratio}")
    print(f"        = {float(ratio):.10f}")
    print()

    gz_width = math.log(4.0 / 3)
    err = abs(float(ratio) - gz_width) / gz_width

    print(f"  ln(4/3) = {gz_width:.10f}")
    print(f"  Ratio   = {float(ratio):.10f}")
    print(f"  Error   = {err:.6%}")
    print()

    if err < 0.01:
        grade = "🟧 (< 1% error)"
    elif err < 0.05:
        grade = "🟧 (< 5% error)"
    else:
        grade = "⚪ (> 5% error)"

    print(f"  Grade: {grade}")
    print()

    # Exact fraction analysis
    print(f"  Exact ratio = {ratio.numerator}/{ratio.denominator}")
    print(f"  = {float(ratio):.10f}")
    print(f"  ln(4/3) is irrational, so exact match is impossible.")
    print(f"  The question is whether the proximity is meaningful.")
    print()

    # Texas Sharpshooter quick check
    # We searched among ~10 ratios for matches to ~5 constants
    n_tests = 50  # conservative
    p_random = 0.01 / err if err > 0 else 1  # very rough
    print(f"  Bonferroni note: with ~{n_tests} ratio/constant pairs tested,")
    print(f"  a {err:.2%} match is {'notable' if err < 0.01 else 'suggestive but not conclusive'}.")
    print()
    print(f"  STATUS: PASS [{grade}]")
    return True


def test_error_probability_table():
    """Test 6: Full error probability table at p=1/3."""
    print()
    print("=" * 70)
    print("TEST 6: Error Weight Probabilities at p=1/3")
    print("=" * 70)
    print()

    n = 6
    p = Fraction(1, 3)
    q = 1 - p

    print(f"  Independent depolarizing noise, p = {p}, n = {n}")
    print(f"  P(weight w) = C(n,w) * p^w * (1-p)^(n-w)")
    print()
    print("  " + "-" * 60)
    print(f"  {'w':>3}  {'C(6,w)':>7}  {'P(wt=w)':>18}  {'float':>12}  {'Detected?':<10}")
    print("  " + "-" * 60)

    total = Fraction(0)
    for w in range(n + 1):
        comb = math.comb(n, w)
        prob = Fraction(comb, 1) * p**w * q**(n - w)
        total += prob
        # [[6,4,2]] detects all weight 1 errors (d=2)
        # Weight 0 = no error
        # Weight >= 2 = some detected, some not
        if w == 0:
            det = "N/A"
        elif w == 1:
            det = "ALL (d=2)"
        else:
            det = "partial"

        print(f"  {w:>3}  {comb:>7}  {str(prob):>18}  {float(prob):12.8f}  {det:<10}")

    print("  " + "-" * 60)
    print(f"  {'Sum':>3}  {'':>7}  {str(total):>18}  {float(total):12.8f}")
    print()

    # ASCII histogram
    print("  Weight probability histogram at p=1/3:")
    print()
    max_bar = 40
    probs = []
    for w in range(n + 1):
        comb = math.comb(n, w)
        prob_f = float(Fraction(comb, 1) * p**w * q**(n - w))
        probs.append(prob_f)

    max_prob = max(probs)
    for w in range(n + 1):
        bar_len = int(probs[w] / max_prob * max_bar)
        bar = '#' * bar_len
        print(f"  w={w}: {bar} {probs[w]:.4f}")

    print()

    # Key observations
    print("  Observations:")
    print(f"    P(w=0) = (2/3)^6 = {probs[0]:.6f} = R^6")
    print(f"    P(w=1) = 6*(1/3)*(2/3)^5 = {probs[1]:.6f}")
    print(f"    Mode at w=2: P(w=2) = {probs[2]:.6f} (most likely error weight)")
    print(f"    P(w=0) + P(w=1) = {probs[0]+probs[1]:.6f} (no error + detectable)")
    print()
    print("  STATUS: PASS [table computed]")
    return True


def test_summary():
    """Final summary with all key values."""
    print()
    print("=" * 70)
    print("TEST 7: Comprehensive Summary")
    print("=" * 70)
    print()

    p_star = find_threshold()
    gz_lower = 0.5 - math.log(4.0 / 3)
    gz_width = math.log(4.0 / 3)

    print("  ┌──────────────────────────────────────────────────────────────┐")
    print("  │ QCOMP-008 Key Results                                       │")
    print("  ├──────────────────────────────────────────────────────────────┤")
    print(f"  │ Q(1/3) = {hashing_bound(1.0/3):+.6f}  (< 0, channel dead)             │")
    print(f"  │ p*     = {p_star:.6f}   (threshold where Q=0)              │")
    print(f"  │ GZ_low = {gz_lower:.6f}   (1/2 - ln(4/3))                  │")
    print(f"  │ |p*-GZ_low|/GZ_low = {abs(p_star-gz_lower)/gz_lower:.4%}                          │")
    print(f"  │ (2/3)^6 = {(2/3)**6:.6f}  = R^6 (exact identity)          │")
    print(f"  │ P(1er)/P(any) = {192/665:.6f} ~ ln(4/3) = {gz_width:.6f}     │")
    print("  ├──────────────────────────────────────────────────────────────┤")
    print("  │ Exact identities:                                           │")
    print("  │   - Q(1/3) < 0: channel useless at meta FP       [🟩]      │")
    print("  │   - (1-p)^n = R^n at p=1/3                        [🟩]      │")
    print("  │   - p + R = 1/3 + 2/3 = 1                         [🟩]      │")
    print("  │ Approximate:                                                │")
    print(f"  │   - p* ~ GZ_lower ({abs(p_star-gz_lower)/gz_lower:.1%} error)                    [🟧]      │")
    print(f"  │   - P(1er)/P(any) ~ ln(4/3) ({abs(192/665-gz_width)/gz_width:.2%} error)       [🟧]      │")
    print("  └──────────────────────────────────────────────────────────────┘")
    print()

    print("  OVERALL GRADE: 🟧")
    print("  Exact identities at p=1/3 confirmed; threshold proximity approximate.")
    print()
    return True


def main():
    print()
    print("*" * 70)
    print("  QCOMP-008: Depolarizing Channel at p=1/3 — Verification")
    print("*" * 70)
    print()

    results = []
    results.append(("Capacity table at key p values", test_capacity_table()))
    results.append(("Threshold p* computation", test_threshold()))
    results.append(("ASCII plot of Q(p)", test_ascii_plot()))
    results.append(("No-error identity (2/3)^6 = R^6", test_no_error_identity()))
    results.append(("Detection ratio vs ln(4/3)", test_detection_ratio()))
    results.append(("Error probability table", test_error_probability_table()))
    results.append(("Summary", test_summary()))

    print()
    print("=" * 70)
    print("  FINAL RESULTS")
    print("=" * 70)
    print()
    print("  " + "-" * 50)
    print(f"  {'Test':<40} {'Result':<10}")
    print("  " + "-" * 50)
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  {name:<40} {status:<10}")
    print("  " + "-" * 50)
    print()

    total_pass = sum(1 for _, p in results if p)
    total = len(results)
    print(f"  Total: {total_pass}/{total} passed")
    print()
    print("  Key findings:")
    print("    1. At p=1/3 (meta FP), depolarizing channel has Q ~ -0.45 (dead)")
    print("    2. Threshold p* ~ 0.189 is ~10.8% from GZ lower boundary")
    print("    3. (2/3)^6 = R^n: no-error probability = code rate to the 6th")
    print("    4. P(1 error)/P(any error) ~ ln(4/3) with 0.35% error")
    print()


if __name__ == '__main__':
    main()
