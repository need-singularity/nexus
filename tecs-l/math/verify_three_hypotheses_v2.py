#!/usr/bin/env python3
"""
Verify three hypotheses: H-AI-5, H-CX-5, H-CS-5
Single script with tables and ASCII plots.
"""
import math
from collections import defaultdict

# ── Number theory helpers ──────────────────────────────────────────

def sigma(n):
    """Sum of divisors σ(n)"""
    s = 0
    for i in range(1, int(n**0.5) + 1):
        if n % i == 0:
            s += i
            if i != n // i:
                s += n // i
    return s

def tau(n):
    """Number of divisors τ(n)"""
    t = 0
    for i in range(1, int(n**0.5) + 1):
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

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

# ══════════════════════════════════════════════════════════════════════
# H-AI-5: σφ/(nτ) as regularizer
# ══════════════════════════════════════════════════════════════════════
print("=" * 72)
print("  H-AI-5: sigma(d)*phi(d)/(d*tau(d)) as complexity regularizer")
print("=" * 72)

# Part 1: R(d) and derived quantities for key dimensions
dims = [32, 64, 128, 256, 512, 768, 1024, 2048, 4096]
print("\n-- Part 1: R(d), R(d)/d, B(d)=sigma*phi/d^2 for key dimensions --\n")
print(f"{'d':>6} | {'sigma':>8} | {'phi':>8} | {'tau':>5} | {'R(d)':>12} | {'R(d)/d':>12} | {'B(d)':>12}")
print("-" * 78)

rd_vals = {}
rd_over_d = {}
for d in dims:
    s = sigma(d)
    p = euler_phi(d)
    t = tau(d)
    R = s * p / (d * t)
    B = s * p / (d * d)
    rd_vals[d] = R
    rd_over_d[d] = R / d
    print(f"{d:>6} | {s:>8} | {p:>8} | {t:>5} | {R:>12.4f} | {R/d:>12.6f} | {B:>12.6f}")

# Part 2: Sensitivity |R(d)-R(d+-1)|
print("\n-- Part 2: Sensitivity |R(d)-R(d+-1)| --\n")
print(f"{'d':>6} | {'R(d)':>12} | {'R(d-1)':>12} | {'R(d+1)':>12} | {'|D-|':>10} | {'|D+|':>10} | {'avg D':>10}")
print("-" * 86)
for d in dims:
    s, p, t = sigma(d), euler_phi(d), tau(d)
    R = s * p / (d * t)
    s1, p1, t1 = sigma(d-1), euler_phi(d-1), tau(d-1)
    R_m = s1 * p1 / ((d-1) * t1)
    s2, p2, t2 = sigma(d+1), euler_phi(d+1), tau(d+1)
    R_p = s2 * p2 / ((d+1) * t2)
    dm = abs(R - R_m)
    dp = abs(R - R_p)
    print(f"{d:>6} | {R:>12.4f} | {R_m:>12.4f} | {R_p:>12.4f} | {dm:>10.4f} | {dp:>10.4f} | {(dm+dp)/2:>10.4f}")

# Part 3: Monotonicity of R(d)/d for d=2..200
print("\n-- Part 3: Monotonicity of R(d)/d for d=2..200 --\n")
rd_d_series = []
for d in range(2, 201):
    s, p, t = sigma(d), euler_phi(d), tau(d)
    R = s * p / (d * t)
    rd_d_series.append((d, R / d))

# Check monotonicity
increasing = 0
decreasing = 0
for i in range(1, len(rd_d_series)):
    if rd_d_series[i][1] > rd_d_series[i-1][1]:
        increasing += 1
    elif rd_d_series[i][1] < rd_d_series[i-1][1]:
        decreasing += 1

print(f"  Increases: {increasing} times")
print(f"  Decreases: {decreasing} times")
print(f"  -> R(d)/d is {'NOT ' if decreasing > 0 else ''}monotonically increasing")

# Find min and max
min_val = min(rd_d_series, key=lambda x: x[1])
max_val = max(rd_d_series, key=lambda x: x[1])
print(f"  Min R(d)/d = {min_val[1]:.6f} at d={min_val[0]}")
print(f"  Max R(d)/d = {max_val[1]:.6f} at d={max_val[0]}")

# ASCII plot of R(d)/d
print("\n  R(d)/d for d=2..200 (ASCII histogram, binned by 10):")
bins = []
for start in range(2, 201, 10):
    end = min(start + 10, 201)
    chunk = [v for d, v in rd_d_series if start <= d < end]
    if chunk:
        bins.append((start, end - 1, sum(chunk) / len(chunk)))

max_bar = max(b[2] for b in bins)
for start, end, avg in bins:
    bar_len = int(40 * avg / max_bar) if max_bar > 0 else 0
    print(f"  {start:>3}-{end:>3} | {'#' * bar_len} {avg:.4f}")

# Part 4: Powers of 2 vs neighbors
print("\n-- Part 4: R(d)/d for d=2^k vs d=2^k+-1 --\n")
print(f"{'d':>6} | {'R(d)/d':>12} | {'R(d-1)/(d-1)':>14} | {'R(d+1)/(d+1)':>14} | {'2^k lowest?':>12}")
print("-" * 72)
for k in range(1, 13):
    d = 2**k
    vals = {}
    for dd in [d-1, d, d+1]:
        if dd < 2:
            vals[dd] = float('inf')
            continue
        s, p, t = sigma(dd), euler_phi(dd), tau(dd)
        R = s * p / (dd * t)
        vals[dd] = R / dd
    lowest = "YES" if vals[d] <= min(vals[d-1], vals[d+1]) else "NO"
    print(f"{d:>6} | {vals[d]:>12.6f} | {vals[d-1]:>14.6f} | {vals[d+1]:>14.6f} | {lowest:>12}")

# Part 5: Correlation R(d)/d vs 1/tau(d)
print("\n-- Part 5: Correlation between R(d)/d and 1/tau(d) --\n")
xs = []  # R(d)/d
ys = []  # 1/tau(d)
for d in range(2, 201):
    s, p, t = sigma(d), euler_phi(d), tau(d)
    R = s * p / (d * t)
    xs.append(R / d)
    ys.append(1.0 / t)

n = len(xs)
mx = sum(xs) / n
my = sum(ys) / n
cov = sum((xs[i] - mx) * (ys[i] - my) for i in range(n)) / n
sx = (sum((x - mx)**2 for x in xs) / n) ** 0.5
sy = (sum((y - my)**2 for y in ys) / n) ** 0.5
corr = cov / (sx * sy) if sx * sy > 0 else 0
print(f"  Pearson correlation r(R(d)/d, 1/tau(d)) = {corr:.6f}")
print(f"  -> {'Strong' if abs(corr) > 0.7 else 'Moderate' if abs(corr) > 0.4 else 'Weak'} {'positive' if corr > 0 else 'negative'} correlation")

print(f"\n  Note: R(d)/d = [sigma(d)/d] * [phi(d)/d] * [1/tau(d)]")
print(f"  = abundancy(d) * coprime_density(d) / tau(d)")
print(f"  For primes p: sigma/p=(p+1)/p~1, phi/p=(p-1)/p~1, tau=2 -> R/p~(p^2-1)/(2p^2)->1/2")
print(f"  For 2^k: sigma/d=(2^(k+1)-1)/2^k~2, phi/d=1/2, tau=k+1 -> R/d~1/(k+1)->0")

# ══════════════════════════════════════════════════════════════════════
# H-CX-5: Repulsion field = tau/phi imbalance
# ══════════════════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("  H-CX-5: Repulsion field = tau(n)/phi(n) imbalance")
print("=" * 72)

# Part 1-2: tau/phi for n=2..500
print("\n-- Part 1-2: tau(n)/phi(n) for selected n --\n")
tf_ratios = {}
for nn in range(2, 501):
    t = tau(nn)
    p = euler_phi(nn)
    tf_ratios[nn] = t / p

# Show key values
key_ns = [2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 18, 20, 24, 28, 30, 36, 48, 60, 120, 240, 360, 496]
print(f"{'n':>5} | {'tau':>5} | {'phi':>5} | {'tau/phi':>10} | {'perfect?':>9} | {'note':>20}")
print("-" * 65)
for nn in key_ns:
    if nn > 500:
        continue
    t = tau(nn)
    p = euler_phi(nn)
    perf = "YES" if sigma(nn) == 2 * nn else ""
    note = ""
    if nn == 6:
        note = "1st perfect, tau/phi=2"
    elif nn == 28:
        note = "2nd perfect, tau/phi=0.5"
    elif nn == 496:
        note = "3rd perfect"
    print(f"{nn:>5} | {t:>5} | {p:>5} | {t/p:>10.4f} | {perf:>9} | {note:>20}")

# Part 3: Histogram of tau/phi
print("\n-- Part 3: Distribution of tau(n)/phi(n) for n=2..500 --\n")
vals_list = list(tf_ratios.values())
# Bin into ranges
hist_bins = [(0, 0.1), (0.1, 0.2), (0.2, 0.3), (0.3, 0.4), (0.4, 0.5),
             (0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 0.9), (0.9, 1.0),
             (1.0, 1.2), (1.2, 1.5), (1.5, 2.0), (2.0, 3.0), (3.0, 5.0)]
max_count = 0
hist_data = []
for lo, hi in hist_bins:
    count = sum(1 for v in vals_list if lo <= v < hi)
    hist_data.append((lo, hi, count))
    max_count = max(max_count, count)

for lo, hi, count in hist_data:
    bar_len = int(50 * count / max_count) if max_count > 0 else 0
    marker = " << n=6 here" if lo <= 2.0 < hi else ""
    print(f"  [{lo:.1f},{hi:.1f}) | {'#' * bar_len} {count}{marker}")

# Part 4: Is tau/phi=2 a local max at n=6?
print("\n-- Part 4: Is tau/phi=2 a local maximum at n=6? --\n")
print(f"  n=4: tau/phi = {tau(4)}/{euler_phi(4)} = {tau(4)/euler_phi(4):.4f}")
print(f"  n=5: tau/phi = {tau(5)}/{euler_phi(5)} = {tau(5)/euler_phi(5):.4f}")
print(f"  n=6: tau/phi = {tau(6)}/{euler_phi(6)} = {tau(6)/euler_phi(6):.4f}")
print(f"  n=7: tau/phi = {tau(7)}/{euler_phi(7)} = {tau(7)/euler_phi(7):.4f}")
print(f"  n=8: tau/phi = {tau(8)}/{euler_phi(8)} = {tau(8)/euler_phi(8):.4f}")

# Check neighborhood more broadly
neighborhood = [(nn, tf_ratios[nn]) for nn in range(2, 20)]
print(f"\n  tau/phi for n=2..19:")
for nn, r in neighborhood:
    marker = " <<<" if nn == 6 else ""
    print(f"    n={nn:>2}: tau/phi = {r:.4f}{marker}")

is_local_max = tf_ratios[6] > tf_ratios[5] and tf_ratios[6] > tf_ratios[7]
print(f"\n  tau/phi(6) > tau/phi(5) and tau/phi(6) > tau/phi(7)? {is_local_max}")

# Check if it's a global max in small range
max_in_range = max(((nn, r) for nn, r in tf_ratios.items() if 2 <= nn <= 20), key=lambda x: x[1])
print(f"  Max tau/phi in [2,20]: n={max_in_range[0]}, tau/phi={max_in_range[1]:.4f}")

# Global max in [2,500]
global_max = max(tf_ratios.items(), key=lambda x: x[1])
print(f"  Max tau/phi in [2,500]: n={global_max[0]}, tau/phi={global_max[1]:.4f}")
# Top 10
top10 = sorted(tf_ratios.items(), key=lambda x: -x[1])[:10]
print(f"\n  Top 10 tau/phi values in [2,500]:")
for nn, r in top10:
    perf = " [PERFECT]" if sigma(nn) == 2*nn else ""
    print(f"    n={nn:>3}: tau/phi = {r:.4f}  (tau={tau(nn)}, phi={euler_phi(nn)}){perf}")

# Part 5: Where else does tau/phi=2?
print("\n-- Part 5: Where tau(n)/phi(n) = 2 exactly (i.e., tau = 2*phi)? --\n")
exact_2 = [nn for nn in range(2, 501) if tau(nn) == 2 * euler_phi(nn)]
print(f"  n where tau(n) = 2*phi(n): {exact_2}")
if exact_2:
    for nn in exact_2[:20]:
        print(f"    n={nn}: tau={tau(nn)}, phi={euler_phi(nn)}, sigma={sigma(nn)}, perfect={'YES' if sigma(nn)==2*nn else 'no'}")

# Also check tau/phi close to 2
close_2 = [(nn, tf_ratios[nn]) for nn in range(2, 501) if abs(tf_ratios[nn] - 2.0) < 0.05]
print(f"\n  n where |tau/phi - 2| < 0.05: {[nn for nn, _ in close_2]}")

# Part 6: Average tau/phi as N grows
print("\n-- Part 6: Average tau(n)/phi(n) for n in [2,N] as N grows --\n")
running_sum = 0
print(f"{'N':>6} | {'avg tau/phi':>12} | {'plot':>40}")
avgs = []
for nn in range(2, 501):
    running_sum += tf_ratios[nn]
    if nn in [10, 20, 50, 100, 200, 300, 400, 500]:
        avg = running_sum / (nn - 1)
        avgs.append((nn, avg))

max_avg = max(a for _, a in avgs)
for N, avg in avgs:
    bar_len = int(40 * avg / max_avg) if max_avg > 0 else 0
    print(f"{N:>6} | {avg:>12.6f} | {'#' * bar_len}")

print(f"\n  Trend: {'converging' if abs(avgs[-1][1] - avgs[-2][1]) < 0.01 else 'still changing'}")
print(f"  Limit estimate ~ {avgs[-1][1]:.6f}")

# ASCII plot: tau/phi for n=2..50
print("\n  tau/phi for n=2..50 (ASCII plot):")
for nn in range(2, 51):
    r = tf_ratios[nn]
    bar_len = int(30 * r / 2.5)  # scale: 2.5 max
    bar_len = max(0, min(bar_len, 60))
    marker = " <<<" if nn == 6 else (" [P]" if sigma(nn) == 2*nn else "")
    print(f"  {nn:>3} | {'#' * bar_len} {r:.3f}{marker}")

# ══════════════════════════════════════════════════════════════════════
# H-CS-5: Graph coloring and 6
# ══════════════════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("  H-CS-5: Graph coloring and the number 6")
print("=" * 72)

# Part 1: R(3,3) = 6 and perfect numbers
print("\n-- Part 1: R(3,3) = 6 -- first Ramsey number and first perfect number --\n")
print("  R(3,3) = 6: the minimum n such that any 2-coloring of K_n")
print("  contains a monochromatic triangle.")
print(f"  sigma(6) = {sigma(6)}, 2*6 = 12 -> {'PERFECT' if sigma(6) == 12 else 'not perfect'}")
print(f"  6 is both R(3,3) AND the first perfect number.")
print(f"  Known perfect numbers: 6, 28, 496, 8128, ...")

# Part 2: Chromatic numbers for K_n
print("\n-- Part 2: chi(K_n) and chi'(K_n) for n=2..20 --\n")
print(f"{'n':>4} | {'chi(Kn)':>7} | {'chi_e(Kn)':>9} | {'n even?':>7} | {'sigma':>6} | {'tau':>5} | {'phi':>5}")
print("-" * 56)
for nn in range(2, 21):
    chi = nn  # chromatic number of K_n
    chi_prime = nn - 1 if nn % 2 == 0 else nn  # Vizing's theorem, K_n is Class 1 iff n even
    even = "yes" if nn % 2 == 0 else "no"
    print(f"{nn:>4} | {chi:>7} | {chi_prime:>9} | {even:>7} | {sigma(nn):>6} | {tau(nn):>5} | {euler_phi(nn):>5}")

print("\n  Note: chi'(K_n) = n-1 if n even, n if n odd (Vizing's theorem)")
print("  K_6: chi'=5, K_28: chi'=27, K_496: chi'=495 (all even -> Class 1)")

# Part 3: Ramsey numbers and number-theoretic functions
print("\n-- Part 3: Ramsey numbers R(s,t) and sigma, tau, phi --\n")
ramsey = {
    (3, 3): 6,
    (3, 4): 9,
    (3, 5): 14,
    (3, 6): 18,
    (3, 7): 23,
    (3, 8): 28,
    (3, 9): 36,
    (4, 4): 18,
    (4, 5): 25,
}

print(f"{'R(s,t)':>8} | {'value':>6} | {'sigma':>6} | {'tau':>4} | {'phi':>5} | {'sigma/n':>7} | {'tau/phi':>8} | {'perfect?':>9}")
print("-" * 72)
for (s, t), val in sorted(ramsey.items()):
    s_val = sigma(val)
    t_val = tau(val)
    p_val = euler_phi(val)
    perf = "YES" if s_val == 2 * val else ""
    print(f"R({s},{t})  | {val:>6} | {s_val:>6} | {t_val:>4} | {p_val:>5} | {s_val/val:>7.3f} | {t_val/p_val:>8.4f} | {perf:>9}")

# Part 4: Analysis -- is R(3,3)=6 being perfect coincidental?
print("\n-- Part 4: Is R(3,3)=6 being perfect coincidental? --\n")

# Check: is sigma(R(3,k))/R(3,k) ever 2 for k>3?
print("  sigma(R(3,k))/R(3,k) for known R(3,k):")
r3k = [(3, 6), (4, 9), (5, 14), (6, 18), (7, 23), (8, 28), (9, 36)]
for k, val in r3k:
    ratio = sigma(val) / val
    perf = " << PERFECT!" if abs(ratio - 2.0) < 1e-10 else ""
    print(f"    R(3,{k}) = {val:>3}: sigma/n = {ratio:.4f}{perf}")

print(f"\n  R(3,8) = 28 is also perfect! Two Ramsey numbers that are perfect:")
print(f"    R(3,3) = 6  = 2^1*(2^2-1)  [1st perfect]")
print(f"    R(3,8) = 28 = 2^2*(2^3-1)  [2nd perfect]")

# How many known exact Ramsey numbers?
print(f"\n  Known exact Ramsey numbers R(s,t) for s,t >= 3:")
print(f"    R(3,3)=6, R(3,4)=9, R(3,5)=14, R(3,6)=18, R(3,7)=23,")
print(f"    R(3,8)=28, R(3,9)=36, R(4,4)=18, R(4,5)=25")
print(f"    Total known: ~9 exact values")

unique_ramsey = sorted(set(ramsey.values()))
perfect_in_ramsey = [v for v in unique_ramsey if sigma(v) == 2 * v]
max_r = max(unique_ramsey)
all_perfect = [nn for nn in range(2, max_r + 1) if sigma(nn) == 2 * nn]

print(f"\n  Unique Ramsey values: {unique_ramsey}")
print(f"  Perfect among them: {perfect_in_ramsey}")
print(f"  All perfect numbers <= {max_r}: {all_perfect}")

print(f"  Perfect numbers among Ramsey: {len(perfect_in_ramsey)} out of {len(unique_ramsey)} ({100*len(perfect_in_ramsey)/len(unique_ramsey):.1f}%)")
print(f"  Expected by chance: {len(all_perfect)} out of {max_r-1} ({100*len(all_perfect)/(max_r-1):.1f}%)")

# Hypergeometric calculation
from math import comb
N_pool = max_r - 1  # total pool [2, max_r]
K_succ = len(all_perfect)  # successes in pool
n_draw = len(unique_ramsey)  # draws
k_success = len(perfect_in_ramsey)
# P(X >= k) = 1 - sum_{i=0}^{k-1} C(K,i)C(N-K,n-i)/C(N,n)
p_val = 0
for i in range(k_success):
    p_val += comb(K_succ, i) * comb(N_pool - K_succ, n_draw - i) / comb(N_pool, n_draw)
p_val = 1 - p_val
print(f"\n  Hypergeometric test P(>= {k_success} perfect in {n_draw} draws from [2,{max_r}]):")
print(f"    p = {p_val:.6f}")
if p_val < 0.05:
    print(f"    -> Statistically significant (p < 0.05)")
else:
    print(f"    -> NOT statistically significant (p >= 0.05)")

# Additional: pattern in R(3,k) sequence
print("\n-- Additional: Patterns in R(3,k) sequence --\n")
print(f"{'k':>4} | {'R(3,k)':>7} | {'delta':>5} | {'R/k':>6} | {'factorization':>20}")
prev = None
for k, val in r3k:
    delta = val - prev if prev is not None else "-"
    factors = []
    temp = val
    for p in range(2, val + 1):
        while temp % p == 0:
            factors.append(p)
            temp //= p
        if temp == 1:
            break
    fact_str = " x ".join(str(f) for f in factors) if len(factors) > 1 else str(val)
    delta_str = str(delta) if isinstance(delta, int) else delta
    print(f"{k:>4} | {val:>7} | {str(delta_str):>5} | {val/k:>6.2f} | {fact_str:>20}")
    prev = val

# Check: do R(3,k) indices for perfect numbers follow a pattern?
print("\n  R(3,k) = perfect number at k=3 and k=8")
print(f"  k=3: R(3,3)=6=2*3, k=8: R(3,8)=28=4*7")
print(f"  Next perfect: 496. Is 496 = R(3,k) for some k?")
print(f"  R(3,k) grows roughly as O(k^2), so R(3,k)=496 would need k~22")
print(f"  But R(3,k) is unknown for k>=10, so we cannot verify.")

# ══════════════════════════════════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("  SUMMARY")
print("=" * 72)

print(f"""
  H-AI-5: sigma*phi/(n*tau) as regularizer
    - R(d)/d is NOT monotone (oscillates with number-theoretic structure)
    - Powers of 2 have systematically lower R/d (simpler regularization)
    - R(d)/d -> 1/2 for primes, -> 0 for high powers of 2
    - Strong correlation with 1/tau(d): r = {corr:.3f}
    - As regularizer: captures number-theoretic complexity but not monotone
    - Verdict: INTERESTING but not directly usable as-is (non-monotone)
    - Potential: use for dimension selection (prefer d where R/d is low)
""")

exact_2_str = str(exact_2) if exact_2 else "only n=6"
print(f"""  H-CX-5: Repulsion field = tau/phi imbalance
    - tau(6)/phi(6) = 4/2 = 2 (confirmed)
    - tau(28)/phi(28) = 6/12 = 0.5 (confirmed)
    - n=6 IS a local maximum of tau/phi in its neighborhood
    - tau/phi = 2 exactly at: {exact_2_str}
    - Perfect numbers show contrasting tau/phi: 6->2, 28->0.5
    - Average tau/phi converges to ~ {avgs[-1][1]:.4f}
    - Global max tau/phi in [2,500]: n={global_max[0]}, value={global_max[1]:.4f}
    - Verdict: tau/phi=2 at n=6 is structurally notable
""")

print(f"""  H-CS-5: Graph coloring and 6
    - R(3,3) = 6 is both a Ramsey number AND perfect number (confirmed)
    - R(3,8) = 28 is ALSO a perfect number! Two Ramsey-perfect numbers!
    - {len(perfect_in_ramsey)} of {len(unique_ramsey)} known exact Ramsey values are perfect ({100*len(perfect_in_ramsey)/len(unique_ramsey):.0f}%)
    - Hypergeometric p = {p_val:.4f}
    - chi'(K_6) = 5, chi'(K_28) = 27 (both Class 1, as even)
    - The R(3,k) sequence does not follow a simple formula
    - Verdict: R(3,3)=6 and R(3,8)=28 both being perfect is noteworthy
""")

print("Done.")
