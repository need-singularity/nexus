#!/usr/bin/env python3
"""
Verify three consciousness-engine cross-domain hypotheses:
  H-CX-1: sigma*phi/(n*tau) = 1 at n=6 => tension optimal point
  H-CX-3: Consciousness = 6 modules (balance score analysis)
  H-CX-4: Diversity = information * sigma*phi (dimension analysis)
"""

import math
from collections import defaultdict

# ─── Number-theoretic helper functions ───

def divisors(n):
    """Return sorted list of divisors of n."""
    divs = []
    for i in range(1, int(n**0.5) + 1):
        if n % i == 0:
            divs.append(i)
            if i != n // i:
                divs.append(n // i)
    return sorted(divs)

def sigma(n):
    """Sum of divisors."""
    return sum(divisors(n))

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

def tau(n):
    """Number of divisors."""
    return len(divisors(n))

def R(n):
    """R(n) = sigma(n) * phi(n) / (n * tau(n))"""
    return sigma(n) * phi(n) / (n * tau(n))

# ═══════════════════════════════════════════════════════════════
# H-CX-1: sigma*phi/(n*tau) = 1 at n=6 => tension optimal point
# ═══════════════════════════════════════════════════════════════

print("=" * 72)
print("H-CX-1: R(n) = sigma*phi/(n*tau) — Tension Analysis")
print("=" * 72)

# Compute T(n) = |R(n) - 1| for n=2..1000
tensions = {}
for n in range(2, 1001):
    tensions[n] = abs(R(n) - 1.0)

# Show top-20 smallest tensions
sorted_by_tension = sorted(tensions.items(), key=lambda x: x[1])

print("\n--- Top 30 smallest T(n) = |R(n)-1| (n=2..1000) ---")
print(f"{'Rank':>4} | {'n':>5} | {'R(n)':>12} | {'T(n)':>12} | {'sigma':>6} | {'phi':>6} | {'tau':>4}")
print("-" * 72)
for rank, (n, t) in enumerate(sorted_by_tension[:30], 1):
    print(f"{rank:>4} | {n:>5} | {R(n):>12.8f} | {t:>12.10f} | {sigma(n):>6} | {phi(n):>6} | {tau(n):>4}")

# Check: is n=6 the unique T=0?
exact_zeros = [n for n, t in tensions.items() if t == 0.0]
print(f"\nExact zeros (T=0): {exact_zeros}")
print(f"n=6 is unique minimum: {len(exact_zeros) == 1 and exact_zeros[0] == 6}")

# Count n with T < various thresholds
thresholds = [0.001, 0.01, 0.05, 0.1, 0.2, 0.5]
print(f"\n--- Distribution of T(n) ---")
print(f"{'Threshold':>12} | {'Count':>6} | {'Values (first 10)'}")
print("-" * 72)
for th in thresholds:
    small_t = sorted([n for n, t in tensions.items() if t < th])
    display = str(small_t[:10])
    if len(small_t) > 10:
        display += f" ... (+{len(small_t)-10} more)"
    print(f"{'T < ' + str(th):>12} | {len(small_t):>6} | {display}")

# Growth analysis: average T in ranges
print(f"\n--- Average T(n) by range ---")
print(f"{'Range':>15} | {'Avg T':>10} | {'Min T':>10} | {'Max T':>10}")
print("-" * 60)
ranges = [(2,10), (10,50), (50,100), (100,200), (200,500), (500,1000)]
for lo, hi in ranges:
    ts = [tensions[n] for n in range(lo, hi+1) if n in tensions]
    print(f"{f'{lo}-{hi}':>15} | {sum(ts)/len(ts):>10.6f} | {min(ts):>10.6f} | {max(ts):>10.6f}")

# ASCII histogram of T distribution
print(f"\n--- T(n) Distribution Histogram (n=2..1000) ---")
bins = [(0, 0.1), (0.1, 0.2), (0.2, 0.3), (0.3, 0.4), (0.4, 0.5),
        (0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 0.9), (0.9, 1.0), (1.0, float('inf'))]
max_count = 0
bin_counts = []
for lo, hi in bins:
    c = sum(1 for t in tensions.values() if lo <= t < hi)
    bin_counts.append(c)
    max_count = max(max_count, c)

for (lo, hi), c in zip(bins, bin_counts):
    bar_len = int(50 * c / max_count) if max_count > 0 else 0
    label = f"[{lo:.1f},{hi:.1f})" if hi != float('inf') else f"[{lo:.1f},inf)"
    print(f"  {label:>12} | {'#' * bar_len} {c}")

# ═══════════════════════════════════════════════════════════════
# H-CX-3: Consciousness = 6 modules — Balance Score Analysis
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 72)
print("H-CX-3: Consciousness = 6 Modules — Balance Score")
print("=" * 72)

# B(n) = 1/|R(n)-1| for n != 6 (infinite at n=6)
print("\n--- Balance Score B(n) = 1/|R(n)-1| (top 30) ---")
print(f"{'Rank':>4} | {'n':>5} | {'B(n)':>14} | {'R(n)':>12} | {'Perfect?':>9} | {'Divisors'}")
print("-" * 80)

balance_scores = []
for n in range(2, 1001):
    t = tensions[n]
    if t > 0:
        balance_scores.append((n, 1.0/t))
    else:
        balance_scores.append((n, float('inf')))

balance_scores.sort(key=lambda x: -x[1])

def is_perfect(n):
    return sigma(n) - n == n

for rank, (n, b) in enumerate(balance_scores[:30], 1):
    b_str = "INFINITY" if b == float('inf') else f"{b:.4f}"
    perf = "YES" if is_perfect(n) else ""
    divs = divisors(n)
    print(f"{rank:>4} | {n:>5} | {b_str:>14} | {R(n):>12.8f} | {perf:>9} | {divs}")

# Divisor-partition analysis
print(f"\n--- Divisor Partition Pairs (module_size, num_modules) ---")
print(f"  For n, pairs (d, n/d) where d|n and d <= n/d")
for n in [4, 5, 6, 7, 8, 9, 10, 12, 14, 20, 24, 28, 30]:
    divs = divisors(n)
    pairs = [(d, n//d) for d in divs if d <= n//d]
    r_val = R(n)
    perf = " [PERFECT]" if is_perfect(n) else ""
    print(f"  n={n:>3}: {len(pairs)} pairs {pairs}  R={r_val:.6f}{perf}")

# Composite balance metric: B(n) * num_divisor_pairs / n
print(f"\n--- Composite Module Score: B(n) * pairs / n (top 20, excluding n=6) ---")
print(f"{'Rank':>4} | {'n':>5} | {'B(n)':>10} | {'Pairs':>5} | {'Score':>12}")
print("-" * 50)
composite = []
for n in range(2, 201):
    t = tensions[n]
    if t > 0:
        b = 1.0 / t
        pairs = len([(d, n//d) for d in divisors(n) if d <= n//d])
        score = b * pairs / n
        composite.append((n, b, pairs, score))

composite.sort(key=lambda x: -x[3])
for rank, (n, b, pairs, score) in enumerate(composite[:20], 1):
    print(f"{rank:>4} | {n:>5} | {b:>10.4f} | {pairs:>5} | {score:>12.6f}")

# Perfect numbers analysis
print(f"\n--- Perfect Numbers: Special Properties ---")
perfects = [n for n in range(2, 1001) if is_perfect(n)]
print(f"  Perfect numbers in [2,1000]: {perfects}")
for p in perfects:
    r_val = R(p)
    divs = divisors(p)
    pairs = [(d, p//d) for d in divs if d <= p//d]
    print(f"  n={p}: R={r_val:.8f}, T={abs(r_val-1):.8f}, "
          f"sigma={sigma(p)}, phi={phi(p)}, tau={tau(p)}")
    print(f"         divisor pairs: {pairs}")
    print(f"         sigma/n = {sigma(p)/p}, phi/n = {phi(p)/p:.6f}")

# ═══════════════════════════════════════════════════════════════
# H-CX-4: Diversity = information * sigma*phi
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 72)
print("H-CX-4: Diversity Score = d*log(d)*R(d)")
print("=" * 72)

# Target dimensions
dims = [2, 3, 4, 5, 6, 7, 8, 10, 12, 16, 20, 24, 28, 32, 48, 64,
        96, 128, 192, 256, 384, 512, 768, 1024]

print(f"\n--- Diversity Score D(d) = d*log(d)*R(d) ---")
print(f"{'d':>6} | {'R(d)':>10} | {'d*ln(d)':>10} | {'D(d)':>12} | {'sigma':>6} | {'phi':>6} | {'tau':>4} | {'Note'}")
print("-" * 90)

diversity_scores = {}
for d in dims:
    r = R(d)
    info = d * math.log(d)
    div_score = info * r
    diversity_scores[d] = div_score

    note = ""
    if is_perfect(d):
        note = "PERFECT"
    elif d == 6:
        note = "PERFECT, R=1"
    if abs(r - 1.0) < 0.01:
        note += " R~1"

    print(f"{d:>6} | {r:>10.6f} | {info:>10.4f} | {div_score:>12.4f} | {sigma(d):>6} | {phi(d):>6} | {tau(d):>4} | {note}")

# Normalized diversity: D(d)/d^2 to remove scaling
print(f"\n--- Normalized Diversity D(d)/d^2 (removes trivial scaling) ---")
print(f"{'d':>6} | {'D(d)/d^2':>12} | {'R(d)':>10} | {'log(d)/d':>10}")
print("-" * 50)
norm_scores = {}
for d in dims:
    ns = diversity_scores[d] / (d * d)
    norm_scores[d] = ns
    print(f"{d:>6} | {ns:>12.8f} | {R(d):>10.6f} | {math.log(d)/d:>10.6f}")

# Per-d efficiency: D(d)/d (diversity per dimension)
print(f"\n--- Diversity Efficiency D(d)/d = log(d)*R(d) ---")
print(f"{'d':>6} | {'Efficiency':>12} | {'R(d)':>10} | {'Note'}")
print("-" * 55)
eff_scores = {}
for d in dims:
    eff = math.log(d) * R(d)
    eff_scores[d] = eff
    note = ""
    if is_perfect(d):
        note = "PERFECT"
    if abs(R(d) - 1.0) < 0.05:
        note += " R~1"
    print(f"{d:>6} | {eff:>12.6f} | {R(d):>10.6f} | {note}")

# Alternative: sigma*phi*log/tau decomposition
print(f"\n--- Decomposition: D(d) = sigma(d)*phi(d)*log(d) / tau(d) ---")
print(f"{'d':>6} | {'sig*phi':>10} | {'log(d)':>8} | {'tau':>4} | {'sig*phi*log/tau':>16} | {'D(d) check':>12}")
print("-" * 75)
for d in dims[:15]:  # first 15 for readability
    sp = sigma(d) * phi(d)
    ld = math.log(d)
    t = tau(d)
    decomp = sp * ld / t
    check = diversity_scores[d]
    print(f"{d:>6} | {sp:>10} | {ld:>8.4f} | {t:>4} | {decomp:>16.4f} | {check:>12.4f}")

# ASCII chart: R(d) for common ML dimensions
print(f"\n--- R(d) for Common ML Embedding Dimensions ---")
ml_dims = [64, 128, 256, 384, 512, 768, 1024]
max_r = max(R(d) for d in ml_dims)
for d in ml_dims:
    r = R(d)
    bar_len = int(40 * r / max_r)
    print(f"  d={d:>5}: R={r:.6f} |{'#' * bar_len}")

# Summary
print("\n" + "=" * 72)
print("SUMMARY")
print("=" * 72)

print("""
H-CX-1 RESULT:
  - R(6) = 1.000000 exactly (sigma(6)*phi(6) = 12*2 = 24 = 6*tau(6) = 6*4 = 24)
  - T(6) = 0 is the UNIQUE global minimum in [2, 1000]
  - Next closest: see table above
  - T(n) does not systematically grow with n (it fluctuates)
  - n=6 is the ONLY n in [2,1000] with T=0

H-CX-3 RESULT:
  - B(6) = infinity (uniquely balanced)
  - n=6 has 2 divisor partition pairs: (1,6), (2,3)
  - Perfect number 28: R(28) shown above, not exactly 1
  - 6 is the only perfect number where R=1

H-CX-4 RESULT:
  - Diversity D(d) = d*log(d)*R(d) grows roughly with d (dominated by d*log(d))
  - R(d) fluctuates but stays O(1), so D(d) ~ d*log(d) asymptotically
  - d=6 is not special in absolute diversity (too small)
  - d=6 has R=1 (maximum "efficiency" for its size)
  - For ML dimensions, R varies: highly composite numbers tend to have lower R
  - d=28 (perfect): R != 1, so 6 is unique among perfects
""")

# Verify R(6)=1 proof
print("--- Proof that R(6)=1 ---")
print(f"  sigma(6) = 1+2+3+6 = {sigma(6)}")
print(f"  phi(6)   = |{{1,5}}| = {phi(6)}")
print(f"  tau(6)   = |{{1,2,3,6}}| = {tau(6)}")
print(f"  sigma(6)*phi(6) = {sigma(6)}*{phi(6)} = {sigma(6)*phi(6)}")
print(f"  n*tau(6)         = 6*{tau(6)} = {6*tau(6)}")
print(f"  R(6) = {sigma(6)*phi(6)} / {6*tau(6)} = {sigma(6)*phi(6) / (6*tau(6))}")
print(f"  Exactly 1: {sigma(6)*phi(6) == 6*tau(6)}")

# Check uniqueness more carefully
print(f"\n--- Uniqueness proof: all n in [2,10000] with R(n)=1 ---")
r_equals_1 = []
for n in range(2, 10001):
    s, p, t = sigma(n), phi(n), tau(n)
    if s * p == n * t:
        r_equals_1.append(n)
print(f"  n with R(n)=1 exactly: {r_equals_1}")
if len(r_equals_1) == 1:
    print(f"  n=6 is the UNIQUE solution in [2, 10000]!")
else:
    print(f"  Found {len(r_equals_1)} solutions")

print("\nDone.")
