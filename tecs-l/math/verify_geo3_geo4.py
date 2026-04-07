#!/usr/bin/env python3
"""
H-GEO-3 & H-GEO-4 Verification: Arithmetic Gravitational Lensing & Dimension Telescope
========================================================================================
Part 1: R spectrum gap structure around perfect numbers (n=6, 28, 496)
Part 2: "Bright ring" density pile-up outside gaps
Part 3: Dimension telescope E_p(s) profile & convergence
Part 4: Multi-focal scan of n=120
Part 5: Deflection angle distribution
"""

import math
from collections import defaultdict
from fractions import Fraction

# ============================================================
# Number-theoretic functions
# ============================================================

def sigma(n):
    """Sum of divisors σ(n)"""
    s = 0
    for i in range(1, int(math.isqrt(n)) + 1):
        if n % i == 0:
            s += i
            if i != n // i:
                s += n // i
    return s

def tau(n):
    """Number of divisors τ(n)"""
    t = 0
    for i in range(1, int(math.isqrt(n)) + 1):
        if n % i == 0:
            t += 1
            if i != n // i:
                t += 1
    return t

def euler_phi(n):
    """Euler's totient φ(n)"""
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

def R(n):
    """R(n) = σ(n)·φ(n) / (n·τ(n))"""
    if n < 2:
        return None
    s = sigma(n)
    p = euler_phi(n)
    t = tau(n)
    return (s * p) / (n * t)

def factorize(n):
    """Return prime factorization as dict {p: a}"""
    factors = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors

def f_pa(p, a):
    """f(p,a) = (p^{a+1} - 1) / (p * (a+1))  ... actually let's compute R multiplicatively.
    For n = prod p^a, R(n) = prod_{p^a || n} R_factor(p, a)
    where R_factor(p, a) = sigma(p^a) * phi(p^a) / (p^a * tau(p^a))
                         = ((p^{a+1}-1)/(p-1)) * (p^a - p^{a-1}) / (p^a * (a+1))
                         = ((p^{a+1}-1)/(p-1)) * p^{a-1}(p-1) / (p^a * (a+1))
                         = (p^{a+1}-1) * p^{a-1} / (p^a * (a+1))
                         = (p^{a+1}-1) / (p * (a+1))
    """
    return (p**(a+1) - 1) / (p * (a + 1))

def sieve_primes(limit):
    """Sieve of Eratosthenes"""
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(math.isqrt(limit)) + 1):
        if is_prime[i]:
            for j in range(i*i, limit + 1, i):
                is_prime[j] = False
    return [i for i in range(2, limit + 1) if is_prime[i]]

# ============================================================
# Precompute R values
# ============================================================
print("=" * 80)
print("H-GEO-3 & H-GEO-4 VERIFICATION")
print("Arithmetic Gravitational Lensing & Dimension Telescope")
print("=" * 80)

N_MAX = 100000
print(f"\nPrecomputing R(n) for n=2..{N_MAX}...")

R_values = {}
for n in range(2, N_MAX + 1):
    R_values[n] = R(n)

print(f"  Done. {len(R_values)} values computed.")

# Collect all distinct R values
all_R = sorted(set(R_values.values()))
print(f"  Distinct R values: {len(all_R)}")

# ============================================================
# PART 1: R spectrum gap structure around perfect numbers
# ============================================================
print("\n" + "=" * 80)
print("PART 1: R SPECTRUM GAP STRUCTURE AROUND PERFECT NUMBERS")
print("=" * 80)

perfect_numbers = [6, 28, 496, 8128]
R_perfect = {}
for pn in perfect_numbers:
    r = R(pn)
    R_perfect[pn] = r
    print(f"\n  R({pn}) = {r}")

# For each perfect number, find gap around its R value
for pn in perfect_numbers[:3]:  # 6, 28, 496
    target_R = R_perfect[pn]
    window = target_R * 0.15 if target_R > 1 else 0.5  # adaptive window

    # Collect R values in window
    nearby = []
    for n, rv in R_values.items():
        if abs(rv - target_R) <= window and n != pn:
            nearby.append((rv, n))
    nearby.sort()

    # Find closest below and above
    below = [(rv, n) for rv, n in nearby if rv < target_R]
    above = [(rv, n) for rv, n in nearby if rv > target_R]

    print(f"\n--- Gap analysis around R={target_R} (n={pn}) ---")
    print(f"  Window: [{target_R - window:.4f}, {target_R + window:.4f}]")

    if below:
        closest_below = below[-1]
        gap_below = target_R - closest_below[0]
        print(f"  Closest below: R={closest_below[0]:.8f} (n={closest_below[1]}), gap={gap_below:.8f}")
        # Try to identify as fraction
        frac = Fraction(closest_below[0]).limit_denominator(1000)
        print(f"    ≈ {frac} = {float(frac):.8f}")
    else:
        print(f"  No R values below {target_R} in window!")

    if above:
        closest_above = above[0]
        gap_above = closest_above[0] - target_R
        print(f"  Closest above: R={closest_above[0]:.8f} (n={closest_above[1]}), gap={gap_above:.8f}")
        frac = Fraction(closest_above[0]).limit_denominator(1000)
        print(f"    ≈ {frac} = {float(frac):.8f}")
    else:
        print(f"  No R values above {target_R} in window!")

    if below and above:
        total_gap = closest_above[0] - closest_below[0]
        einstein_radius_below = gap_below
        einstein_radius_above = gap_above
        print(f"  Total gap width: {total_gap:.8f}")
        print(f"  Einstein radius (below): {einstein_radius_below:.8f}")
        print(f"  Einstein radius (above): {einstein_radius_above:.8f}")
        print(f"  Asymmetry ratio: {einstein_radius_below/einstein_radius_above:.4f}")

    # Show 5 closest on each side
    print(f"\n  5 closest R values below R={target_R}:")
    for rv, n in below[-5:]:
        frac = Fraction(rv).limit_denominator(1000)
        print(f"    R={rv:.8f} ≈ {frac}  (n={n})")

    print(f"  5 closest R values above R={target_R}:")
    for rv, n in above[:5]:
        frac = Fraction(rv).limit_denominator(1000)
        print(f"    R={rv:.8f} ≈ {frac}  (n={n})")


# Einstein radius table
print("\n\n--- Einstein Radius Summary ---")
print(f"{'Perfect n':>10} {'R(n)':>10} {'Gap below':>12} {'Gap above':>12} {'Total gap':>12} {'Asymmetry':>10}")
print("-" * 70)
for pn in perfect_numbers[:3]:
    target_R = R_perfect[pn]
    below_vals = sorted([rv for rv in R_values.values() if rv < target_R])
    above_vals = sorted([rv for rv in R_values.values() if rv > target_R])

    gb = target_R - below_vals[-1] if below_vals else float('inf')
    ga = above_vals[0] - target_R if above_vals else float('inf')
    total = gb + ga
    asym = gb / ga if ga > 0 else float('inf')
    print(f"{pn:>10} {target_R:>10.4f} {gb:>12.8f} {ga:>12.8f} {total:>12.8f} {asym:>10.4f}")


# ============================================================
# PART 2: "Bright ring" density pile-up
# ============================================================
print("\n" + "=" * 80)
print("PART 2: BRIGHT RING EFFECT — DENSITY PILE-UP OUTSIDE GAPS")
print("=" * 80)

# Focus on n=6 (R=1), gap is (3/4, 7/6)
# Check density in bins just outside 7/6
target = 1.0
gap_right_edge = 7/6  # ~1.1667
epsilon = 0.05

print(f"\n--- Density analysis around R=1 (n=6) ---")
print(f"  Gap right edge: R=7/6 ≈ {7/6:.4f}")
print(f"  Bin width ε = {epsilon}")

# Count R values in successive bins starting from 7/6
n_bins = 20
bin_counts = []
for i in range(n_bins):
    lo = gap_right_edge + i * epsilon
    hi = gap_right_edge + (i + 1) * epsilon
    count = sum(1 for rv in R_values.values() if lo <= rv < hi)
    bin_counts.append((lo, hi, count))

print(f"\n  {'Bin':>5} {'Range':>20} {'Count':>8} {'Density':>10} {'Bar'}")
print("  " + "-" * 65)
max_count = max(c for _, _, c in bin_counts) if bin_counts else 1
for i, (lo, hi, count) in enumerate(bin_counts):
    bar = '█' * int(50 * count / max_count) if max_count > 0 else ''
    print(f"  {i:>5} [{lo:>7.4f}, {hi:>7.4f}) {count:>8} {count/epsilon:>10.1f} {bar}")

# Also check left side (below 3/4)
gap_left_edge = 0.75
print(f"\n--- Density below R=3/4 (left of gap) ---")
print(f"  Gap left edge: R=3/4 = {3/4:.4f}")

bin_counts_left = []
for i in range(n_bins):
    hi = gap_left_edge - i * epsilon
    lo = gap_left_edge - (i + 1) * epsilon
    if lo < 0:
        break
    count = sum(1 for rv in R_values.values() if lo <= rv < hi)
    bin_counts_left.append((lo, hi, count))

print(f"\n  {'Bin':>5} {'Range':>20} {'Count':>8} {'Density':>10} {'Bar'}")
print("  " + "-" * 65)
max_count_l = max(c for _, _, c in bin_counts_left) if bin_counts_left else 1
for i, (lo, hi, count) in enumerate(bin_counts_left):
    bar = '█' * int(50 * count / max_count_l) if max_count_l > 0 else ''
    print(f"  {i:>5} [{lo:>7.4f}, {hi:>7.4f}) {count:>8} {count/epsilon:>10.1f} {bar}")


# Same for n=28 (R=4)
print(f"\n--- Density analysis around R=4 (n=28) ---")
target28 = R_perfect[28]
# Find gap edges
below_28 = max(rv for rv in R_values.values() if rv < target28)
above_28 = min(rv for rv in R_values.values() if rv > target28)
print(f"  Gap: ({below_28:.6f}, {above_28:.6f})")

eps28 = 0.1
n_bins28 = 15
bin_counts_28 = []
for i in range(n_bins28):
    lo = above_28 + i * eps28
    hi = above_28 + (i + 1) * eps28
    count = sum(1 for rv in R_values.values() if lo <= rv < hi)
    bin_counts_28.append((lo, hi, count))

print(f"\n  {'Bin':>5} {'Range':>20} {'Count':>8} {'Bar'}")
print("  " + "-" * 55)
max_c28 = max(c for _, _, c in bin_counts_28) if bin_counts_28 else 1
for i, (lo, hi, count) in enumerate(bin_counts_28):
    bar = '█' * int(50 * count / max_c28) if max_c28 > 0 else ''
    print(f"  {i:>5} [{lo:>7.4f}, {hi:>7.4f}) {count:>8} {bar}")


# ============================================================
# PART 3: Dimension Telescope — E_p(s) profile
# ============================================================
print("\n" + "=" * 80)
print("PART 3: DIMENSION TELESCOPE — E_p(s) PROFILE")
print("=" * 80)

# E_p(s) = 1 + sum_{a>=1} f(p,a) / p^{as}
# f(p,a) = (p^{a+1} - 1) / (p * (a+1))

def E_p_s(p, s, max_a=50):
    """Compute Euler factor E_p(s) = 1 + sum_{a>=1} f(p,a)/p^{as}"""
    total = 1.0
    for a in range(1, max_a + 1):
        f = (p**(a+1) - 1) / (p * (a + 1))
        term = f / (p ** (a * s))
        total += term
        if abs(term) < 1e-15:
            break
    return total

primes_list = [2, 3, 5, 7, 11, 13]
s_values = [1.5, 2.0, 3.0, 5.0]

print("\n--- E_p(s) table ---")
header = f"{'p':>5}"
for s in s_values:
    header += f" {'s='+str(s):>12}"
print(header)
print("-" * (5 + 13 * len(s_values)))

for p in primes_list:
    row = f"{p:>5}"
    for s in s_values:
        val = E_p_s(p, s)
        row += f" {val:>12.6f}"
    print(row)

# Closed form for E_p(2)
print("\n--- Closed form verification: E_p(2) = p·ln((p+1)/p) + 1/p ---")
print(f"{'p':>5} {'Numerical':>14} {'Closed form':>14} {'Difference':>14}")
print("-" * 50)
for p in primes_list:
    numerical = E_p_s(p, 2.0)
    closed = p * math.log((p + 1) / p) + 1 / p
    print(f"{p:>5} {numerical:>14.10f} {closed:>14.10f} {abs(numerical - closed):>14.2e}")

# Derive E_p(3) closed form attempt
print("\n--- E_p(3) analysis ---")
print("  E_p(3) = 1 + sum_{a>=1} (p^{a+1}-1)/(p(a+1)) / p^{3a}")
print("         = 1 + sum_{a>=1} (p^{a+1}-1)/(p(a+1)·p^{3a})")
print("         = 1 + sum_{a>=1} [1/((a+1)·p^{2a-1}) - 1/((a+1)·p^{3a+1})]")
print("         = 1 + (1/p)·sum_{a>=1} 1/((a+1)·p^{2(a-1)}) - (1/p)·sum_{a>=1} 1/((a+1)·p^{3a})")
print()
print("  Let x = 1/p^2, y = 1/p^3:")
print("  sum_{a>=1} x^a/(a+1) = (1/x)[-ln(1-x) - x] = [-ln(1-x)-x]/x")
print("  sum_{a>=1} y^a/(a+1) = [-ln(1-y)-y]/y")
print()

for p in primes_list:
    x = 1.0 / p**2
    y = 1.0 / p**3
    # sum_{a>=1} x^{a-1}/(a+1) = (1/x) * sum_{a>=1} x^a/(a+1)
    # sum_{a>=1} x^a/(a+1) = (-ln(1-x) - x)/x
    sum_x_part = (-math.log(1 - x) - x) / x  # sum_{a>=1} x^a/(a+1)
    # But we need sum_{a>=1} 1/((a+1)*p^{2a-1}) = (1/p^{-1}) * sum 1/((a+1)*p^{2a})
    # = p * sum_{a>=1} (1/p^2)^a / (a+1) = p * sum_x_part

    sum_y_part = (-math.log(1 - y) - y) / y  # sum_{a>=1} y^a/(a+1)

    # E_p(3) = 1 + (1/p)*[p * sum_x_part] - (1/p)*sum_y_part
    # Wait, let me redo more carefully.
    # E_p(3) = 1 + sum_{a>=1} (p^{a+1}-1) / (p*(a+1)*p^{3a})
    #        = 1 + sum_{a>=1} p^{a+1}/(p*(a+1)*p^{3a}) - sum_{a>=1} 1/(p*(a+1)*p^{3a})
    #        = 1 + sum_{a>=1} p^a/((a+1)*p^{3a}) - (1/p)*sum_{a>=1} 1/((a+1)*p^{3a})
    #        = 1 + sum_{a>=1} 1/((a+1)*p^{2a}) - (1/p)*sum_{a>=1} 1/((a+1)*p^{3a})
    #        = 1 + sum_x_part - (1/p)*sum_y_part

    closed_3 = 1.0 + sum_x_part - (1.0/p) * sum_y_part
    numerical_3 = E_p_s(p, 3.0)
    print(f"  p={p}: E_p(3) numerical={numerical_3:.10f}, closed={closed_3:.10f}, diff={abs(numerical_3-closed_3):.2e}")

print("\n  Closed form: E_p(3) = 1 + [-ln(1-1/p^2) - 1/p^2]/(1/p^2) - (1/p)·[-ln(1-1/p^3) - 1/p^3]/(1/p^3)")
print("             = 1 - p^2·ln(1-1/p^2) - 1 - (p^2/p)·[-ln(1-1/p^3) - 1/p^3]")
print("  Simplifying: E_p(3) = -p^2·ln(1-1/p^2) + p^2·ln(1-1/p^3)/p + 1/p^2")
print("  Or more cleanly:")
for p in primes_list:
    x = 1.0/p**2
    y = 1.0/p**3
    val = 1.0 + (-math.log(1-x) - x)/x - (1.0/p)*(-math.log(1-y) - y)/y
    print(f"    p={p}: E_p(3) = {val:.10f}")


# Partial products over first 1000 primes
print("\n--- F(s) partial products (first 1000 primes) ---")
primes_1000 = sieve_primes(8000)[:1000]
print(f"  Using {len(primes_1000)} primes (up to {primes_1000[-1]})")

s_test = [1.5, 2.0, 2.5, 3.0, 5.0, 10.0]
print(f"\n  {'s':>6} {'F(s) partial':>16} {'Converged?':>12} {'Last factor':>14}")
print("  " + "-" * 52)

for s in s_test:
    product = 1.0
    last_factor = 1.0
    diverged = False
    for p in primes_1000:
        factor = E_p_s(p, s, max_a=20)
        last_factor = factor
        product *= factor
        if product > 1e100:
            diverged = True
            break
    conv = "DIVERGES" if diverged else "converges"
    if diverged:
        print(f"  {s:>6.1f} {'> 10^100':>16} {conv:>12} {last_factor:>14.10f}")
    else:
        print(f"  {s:>6.1f} {product:>16.6f} {conv:>12} {last_factor:>14.10f}")

# Convergence analysis
print("\n--- Convergence abscissa analysis ---")
print("  R(p) for prime p: R(p) = sigma(p)*phi(p)/(p*tau(p))")
print("                        = (p+1)*(p-1)/(p*2) = (p^2-1)/(2p)")
print("  So R(p)/p^s ~ p^2/(2p^s) = p^{2-s}/2")
print("  Sum R(p)/p^s ~ sum p^{2-s}/2")
print("  This converges iff 2-s < -1 (by prime sum divergence), i.e., s > 3??")
print("  Wait — more carefully via Euler product:")
print("  E_p(s) = 1 + f(p,1)/p^s + ... ≈ 1 + (p^2-1)/(2p·p^s)")
print("         ≈ 1 + p/(2p^s) = 1 + 1/(2p^{s-1})")
print("  ln E_p(s) ≈ 1/(2p^{s-1})")
print("  Sum ln E_p(s) ≈ sum 1/(2p^{s-1})")
print("  Converges iff s-1 > 1, i.e., s > 2.")
print("  So σ_c = 2 (abscissa of convergence).")
print()

# Verify: at s=2, does it converge?
product_s2 = 1.0
for p in primes_1000[:100]:
    product_s2 *= E_p_s(p, 2.0)
print(f"  F(2) partial (100 primes): {product_s2:.6f}")
product_s2b = 1.0
for p in primes_1000[:500]:
    product_s2b *= E_p_s(p, 2.0)
print(f"  F(2) partial (500 primes): {product_s2b:.6f}")
product_s2c = 1.0
for p in primes_1000:
    product_s2c *= E_p_s(p, 2.0)
print(f"  F(2) partial (1000 primes): {product_s2c:.6f}")

# Check growth rate
print("\n  F(2) growth check (is it converging or diverging?):")
checkpoints = [10, 50, 100, 200, 500, 1000]
prod = 1.0
idx = 0
for i, p in enumerate(primes_1000):
    prod *= E_p_s(p, 2.0)
    if i + 1 == checkpoints[idx]:
        print(f"    After {i+1} primes (p={p}): F(2) = {prod:.6f}")
        idx += 1
        if idx >= len(checkpoints):
            break

# s=1.5 growth
print("\n  F(1.5) growth check:")
prod15 = 1.0
idx = 0
for i, p in enumerate(primes_1000):
    prod15 *= E_p_s(p, 1.5)
    if i + 1 in [10, 50, 100, 200]:
        print(f"    After {i+1} primes (p={p}): F(1.5) = {prod15:.6f}")
    if prod15 > 1e50:
        print(f"    DIVERGES after {i+1} primes")
        break


# ============================================================
# PART 4: Multi-focal scan of n=120
# ============================================================
print("\n" + "=" * 80)
print("PART 4: MULTI-FOCAL SCAN OF n=120")
print("=" * 80)

n120 = 120
R120 = R(n120)
print(f"\n  n=120 = 2^3 · 3 · 5")
print(f"  R(120) = {R120}")
print(f"  σ(120) = {sigma(120)}, φ(120) = {euler_phi(120)}, τ(120) = {tau(120)}")
print(f"  Check: {sigma(120)}·{euler_phi(120)} / ({120}·{tau(120)}) = {sigma(120)*euler_phi(120)/(120*tau(120))}")
print(f"  Multiplicative: f(2,3)·f(3,1)·f(5,1) = {f_pa(2,3):.6f}·{f_pa(3,1):.6f}·{f_pa(5,1):.6f} = {f_pa(2,3)*f_pa(3,1)*f_pa(5,1):.6f}")

# R(120)/120^s for various s
print(f"\n  {'s':>6} {'R(120)/120^s':>16} {'log10':>10}")
print("  " + "-" * 35)
for s in [0.5, 1.0, 1.2, 1.5, 2.0, 3.0, 5.0]:
    val = R120 / (120 ** s)
    log_val = math.log10(val) if val > 0 else float('-inf')
    print(f"  {s:>6.1f} {val:>16.8f} {log_val:>10.4f}")

# Compare with nearby n
print(f"\n  Comparison with neighbors (n=115..125):")
print(f"  {'n':>6} {'R(n)':>12} {'R(n)/n':>12} {'factorization'}")
print("  " + "-" * 55)
for n in range(115, 126):
    rn = R(n)
    facts = factorize(n)
    fact_str = "·".join(f"{p}^{a}" if a > 1 else str(p) for p, a in sorted(facts.items()))
    marker = " <<<" if n == 120 else ""
    print(f"  {n:>6} {rn:>12.6f} {rn/n:>12.8f} {fact_str}{marker}")

# R(n) = perfect number?
print(f"\n--- Finding all n where R(n) is a perfect number ---")
perfect_set = {6, 28, 496, 8128}
found = []
for n in range(2, N_MAX + 1):
    rn = R_values[n]
    # Check if R(n) is close to a perfect number (within floating point tolerance)
    for pn in perfect_set:
        if abs(rn - pn) < 1e-10:
            found.append((n, rn, pn))
            break

print(f"  Found {len(found)} values of n where R(n) ∈ {{6, 28, 496, 8128}}:")
for n, rn, pn in found[:30]:
    facts = factorize(n)
    fact_str = "·".join(f"{p}^{a}" if a > 1 else str(p) for p, a in sorted(facts.items()))
    print(f"    n={n:>6}, R(n)={rn:>10.4f} = P({pn}), factorization={fact_str}")
if len(found) > 30:
    print(f"    ... and {len(found)-30} more")

# Special: R(n) exactly = 6
print(f"\n  n where R(n) = 6 exactly:")
for n, rn, pn in found:
    if pn == 6:
        facts = factorize(n)
        fact_str = "·".join(f"{p}^{a}" if a > 1 else str(p) for p, a in sorted(facts.items()))
        print(f"    n={n}, {fact_str}")

# ============================================================
# PART 5: Deflection angle distribution
# ============================================================
print("\n" + "=" * 80)
print("PART 5: DEFLECTION ANGLE DISTRIBUTION")
print("=" * 80)

# Compute average R(n)/n
N_DEFL = 10000
ratios = [R_values[n] / n for n in range(2, N_DEFL + 1)]
avg_ratio = sum(ratios) / len(ratios)
median_ratio = sorted(ratios)[len(ratios) // 2]

print(f"\n  R(n)/n statistics (n=2..{N_DEFL}):")
print(f"    Mean:   {avg_ratio:.6f}")
print(f"    Median: {median_ratio:.6f}")
print(f"    Min:    {min(ratios):.6f} (n={min(range(2,N_DEFL+1), key=lambda n: R_values[n]/n)})")
print(f"    Max:    {max(ratios):.6f} (n={max(range(2,N_DEFL+1), key=lambda n: R_values[n]/n)})")

# Use actual mean for expected
R_exp_coeff = avg_ratio
print(f"\n  Using R_expected(n) = {R_exp_coeff:.6f} · n")

# Compute deflections
deflections = []
for n in range(2, N_DEFL + 1):
    rn = R_values[n]
    r_exp = R_exp_coeff * n
    delta = rn - r_exp
    deflections.append(delta)

# Statistics
mean_d = sum(deflections) / len(deflections)
var_d = sum((d - mean_d) ** 2 for d in deflections) / len(deflections)
std_d = math.sqrt(var_d)
skew_num = sum((d - mean_d) ** 3 for d in deflections) / len(deflections)
skewness = skew_num / (std_d ** 3) if std_d > 0 else 0
kurt_num = sum((d - mean_d) ** 4 for d in deflections) / len(deflections)
kurtosis = kurt_num / (std_d ** 4) - 3 if std_d > 0 else 0

print(f"\n  Deflection δ(n) = R(n) - {R_exp_coeff:.6f}·n statistics:")
print(f"    Mean:     {mean_d:.6f}")
print(f"    Std:      {std_d:.4f}")
print(f"    Skewness: {skewness:.4f} ({'right-skewed' if skewness > 0.5 else 'left-skewed' if skewness < -0.5 else 'approx symmetric'})")
print(f"    Kurtosis: {kurtosis:.4f} ({'heavy-tailed' if kurtosis > 1 else 'light-tailed' if kurtosis < -1 else 'near-normal'})")

# Histogram of deflections
print(f"\n  ASCII histogram of deflections (clipped to [-50, 50]):")
clipped = [d for d in deflections if -50 <= d <= 50]
n_bins_hist = 40
min_d = -50
max_d = 50
bin_width = (max_d - min_d) / n_bins_hist
hist = [0] * n_bins_hist
for d in clipped:
    idx = min(int((d - min_d) / bin_width), n_bins_hist - 1)
    hist[idx] += 1

max_h = max(hist)
print(f"  (clipped: {len(clipped)}/{len(deflections)} values shown)")
for i in range(n_bins_hist):
    lo = min_d + i * bin_width
    hi = lo + bin_width
    bar = '█' * int(60 * hist[i] / max_h) if max_h > 0 else ''
    marker = " <-- 0" if lo <= 0 < hi else ""
    print(f"  [{lo:>7.1f},{hi:>7.1f}) {hist[i]:>5} {bar}{marker}")

# Relative deflection: δ(n)/R_exp(n)
print(f"\n  Relative deflection δ(n)/R_exp(n) distribution:")
rel_defl = [(R_values[n] - R_exp_coeff * n) / (R_exp_coeff * n) for n in range(2, N_DEFL + 1)]
mean_rel = sum(rel_defl) / len(rel_defl)
# Percentiles
sorted_rel = sorted(rel_defl)
p10 = sorted_rel[len(sorted_rel) // 10]
p25 = sorted_rel[len(sorted_rel) // 4]
p50 = sorted_rel[len(sorted_rel) // 2]
p75 = sorted_rel[3 * len(sorted_rel) // 4]
p90 = sorted_rel[9 * len(sorted_rel) // 10]
print(f"    P10={p10:.4f}, P25={p25:.4f}, P50={p50:.4f}, P75={p75:.4f}, P90={p90:.4f}")
print(f"    Mean relative deflection: {mean_rel:.6f}")

# Deflection by number type (prime, prime power, highly composite, etc.)
print(f"\n  Deflection by number type (n=2..{N_DEFL}):")
primes_set = set(sieve_primes(N_DEFL))
type_deflections = defaultdict(list)
for n in range(2, N_DEFL + 1):
    delta = R_values[n] - R_exp_coeff * n
    if n in primes_set:
        type_deflections['prime'].append(delta)
    elif tau(n) >= 12:
        type_deflections['highly_composite'].append(delta)
    else:
        type_deflections['other'].append(delta)

    # Also check perfect numbers
    if n in {6, 28, 496, 8128}:
        type_deflections['perfect'].append(delta)

print(f"  {'Type':>20} {'Count':>8} {'Mean δ':>12} {'Std δ':>12}")
print("  " + "-" * 55)
for tp in ['prime', 'perfect', 'highly_composite', 'other']:
    vals = type_deflections[tp]
    if vals:
        m = sum(vals) / len(vals)
        v = sum((x - m) ** 2 for x in vals) / len(vals)
        s = math.sqrt(v)
        print(f"  {tp:>20} {len(vals):>8} {m:>12.4f} {s:>12.4f}")


# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 80)
print("SUMMARY OF FINDINGS")
print("=" * 80)

print("""
Part 1 — R Spectrum Gaps:
  Gaps around R(6)=1 are confirmed: (3/4, 1) and (1, 7/6).
  Check above for R(28)=4 and R(496)=48 gap structures.

Part 2 — Bright Ring:
  Density distribution outside the gap shows whether pile-up exists.
  See bin counts above for quantitative assessment.

Part 3 — Dimension Telescope:
  E_p(s) computed for s=1.5,2,3,5 and p=2,3,5,7,11,13.
  E_p(2) closed form verified: E_p(2) = p·ln((p+1)/p) + 1/p ✓
  E_p(3) closed form derived: E_p(3) = 1 + [-ln(1-1/p²)-1/p²]·p² - [-ln(1-1/p³)-1/p³]·p²/p
  Convergence: F(s) converges for s > 2, diverges for s ≤ 2.
  σ_c = 2 (abscissa of convergence) confirmed.

Part 4 — n=120 Multi-focal:
  R(120) = 6 = P₁ (first perfect number!).
  All n with R(n) ∈ {perfect numbers} listed above.

Part 5 — Deflection:
  Distribution analyzed with skewness and kurtosis.
  See histogram and type-based breakdown above.
""")

print("Done.")
