#!/usr/bin/env python3
"""
Investigate the probability distribution of R(n) = sigma(n)*phi(n)/(n*tau(n)).
Tasks:
1. Histogram of log(R(n)) for n=2..100000
2. Mean/variance of log(R(n)) for N=1000, 10000, 100000
3. Normality test: skewness, kurtosis
4. Density of integer R(n)
5. Erdos-Kac type standardization
"""

import math
from collections import Counter

NMAX = 100000

# --- Sieve-based computation of sigma, phi, tau ---

def compute_arithmetic_functions(N):
    """Compute sigma(n), phi(n), tau(n) for n=0..N using sieves."""
    sigma = [0] * (N + 1)  # sum of divisors
    phi = list(range(N + 1))  # Euler totient (init to n)
    tau = [0] * (N + 1)  # number of divisors

    # tau and sigma by sieving
    for d in range(1, N + 1):
        for multiple in range(d, N + 1, d):
            tau[multiple] += 1
            sigma[multiple] += d

    # phi by sieving with smallest prime factor
    spf = list(range(N + 1))  # smallest prime factor
    for i in range(2, int(N**0.5) + 1):
        if spf[i] == i:  # i is prime
            for j in range(i * i, N + 1, i):
                if spf[j] == j:
                    spf[j] = i

    # Compute phi using factorization via spf
    phi[0] = 0
    phi[1] = 1
    for n in range(2, N + 1):
        if spf[n] == n:  # n is prime
            phi[n] = n - 1
        else:
            p = spf[n]
            m = n // p
            if m % p == 0:
                phi[n] = phi[m] * p
            else:
                phi[n] = phi[m] * (p - 1)

    return sigma, phi, tau


print("Computing arithmetic functions for n up to", NMAX, "...")
sigma, phi, tau = compute_arithmetic_functions(NMAX)

# --- Compute R(n) and log(R(n)) ---
print("Computing R(n) and log(R(n))...")

logR = [0.0] * (NMAX + 1)  # logR[n] for n >= 2
R_values = [0.0] * (NMAX + 1)

for n in range(2, NMAX + 1):
    r = (sigma[n] * phi[n]) / (n * tau[n])
    R_values[n] = r
    logR[n] = math.log(r)

# ============================================================
# TASK 1: ASCII Histogram of log(R(n)) for n=2..100000
# ============================================================
print("\n" + "=" * 70)
print("TASK 1: Histogram of log(R(n)) for n = 2..100000")
print("=" * 70)

vals = [logR[n] for n in range(2, NMAX + 1)]
vmin, vmax = min(vals), max(vals)
print(f"  min(log R) = {vmin:.6f}  at n = {vals.index(vmin)+2}")
print(f"  max(log R) = {vmax:.6f}  at n = {vals.index(vmax)+2}")

NBINS = 50
bin_width = (vmax - vmin) / NBINS
bins = [0] * NBINS
for v in vals:
    idx = int((v - vmin) / bin_width)
    if idx >= NBINS:
        idx = NBINS - 1
    bins[idx] += 1

max_count = max(bins)
BAR_WIDTH = 60

print(f"\n  Histogram ({NBINS} bins, n=2..{NMAX}):")
print(f"  {'log(R)':>10s}  {'count':>7s}  bar")
print(f"  {'-'*10}  {'-'*7}  {'-'*BAR_WIDTH}")
for i in range(NBINS):
    lo = vmin + i * bin_width
    bar_len = int(bins[i] / max_count * BAR_WIDTH)
    bar = '#' * bar_len
    print(f"  {lo:10.4f}  {bins[i]:7d}  {bar}")

# ============================================================
# TASK 2: Mean and Variance for different N
# ============================================================
print("\n" + "=" * 70)
print("TASK 2: Mean and Variance of log(R(n)) for N = 1000, 10000, 100000")
print("=" * 70)

results = {}
for N in [1000, 10000, 100000]:
    data = [logR[n] for n in range(2, N + 1)]
    count = len(data)
    mean = sum(data) / count
    var = sum((x - mean)**2 for x in data) / count
    std = math.sqrt(var)
    results[N] = (mean, var, std)

print(f"\n  | {'N':>8s} | {'mean':>12s} | {'variance':>12s} | {'std dev':>12s} |")
print(f"  |{'-'*10}|{'-'*14}|{'-'*14}|{'-'*14}|")
for N in [1000, 10000, 100000]:
    m, v, s = results[N]
    print(f"  | {N:>8d} | {m:>12.8f} | {v:>12.8f} | {s:>12.8f} |")

# ============================================================
# TASK 3: Normality test — skewness and kurtosis
# ============================================================
print("\n" + "=" * 70)
print("TASK 3: Skewness and Kurtosis of log(R(n))")
print("=" * 70)

print(f"\n  | {'N':>8s} | {'skewness':>12s} | {'kurtosis':>12s} | {'excess kurt':>12s} |")
print(f"  |{'-'*10}|{'-'*14}|{'-'*14}|{'-'*14}|")

for N in [1000, 10000, 100000]:
    data = [logR[n] for n in range(2, N + 1)]
    count = len(data)
    mean = sum(data) / count
    var = sum((x - mean)**2 for x in data) / count
    std = math.sqrt(var)

    m3 = sum((x - mean)**3 for x in data) / count
    m4 = sum((x - mean)**4 for x in data) / count

    skew = m3 / (std**3) if std > 0 else 0
    kurt = m4 / (std**4) if std > 0 else 0
    excess_kurt = kurt - 3.0

    print(f"  | {N:>8d} | {skew:>12.6f} | {kurt:>12.6f} | {excess_kurt:>12.6f} |")

print("\n  Normal distribution: skewness = 0, kurtosis = 3, excess kurtosis = 0")

# ============================================================
# TASK 4: Density of integer R(n)
# ============================================================
print("\n" + "=" * 70)
print("TASK 4: Density of {n : R(n) is integer} among [2, N]")
print("=" * 70)

print(f"\n  | {'N':>8s} | {'# integer R':>12s} | {'density':>12s} |")
print(f"  |{'-'*10}|{'-'*14}|{'-'*14}|")

for N in [1000, 10000, 100000]:
    int_count = 0
    for n in range(2, N + 1):
        # R(n) = sigma(n)*phi(n) / (n*tau(n))
        num = sigma[n] * phi[n]
        den = n * tau[n]
        if num % den == 0:
            int_count += 1
    density = int_count / (N - 1)
    print(f"  | {N:>8d} | {int_count:>12d} | {density:>12.8f} |")

# Show first few n where R(n) is integer
print("\n  First 30 values of n where R(n) is integer:")
int_ns = []
for n in range(2, NMAX + 1):
    num = sigma[n] * phi[n]
    den = n * tau[n]
    if num % den == 0:
        int_ns.append(n)
    if len(int_ns) >= 30:
        break

for i in range(0, min(30, len(int_ns)), 10):
    chunk = int_ns[i:i+10]
    vals_str = ", ".join(f"{x}" for x in chunk)
    r_str = ", ".join(f"{R_values[x]:.0f}" for x in chunk)
    print(f"    n = {vals_str}")
    print(f"    R = {r_str}")

# Distribution of integer R values
if int_ns:
    int_r_vals = [int(R_values[n]) for n in int_ns]
    ctr = Counter(int_r_vals)
    print(f"\n  Distribution of integer R(n) values (first {len(int_ns)}):")
    for rv, cnt in sorted(ctr.items())[:15]:
        print(f"    R = {rv}: {cnt} times")

# ============================================================
# TASK 5: Erdos-Kac type standardization
# ============================================================
print("\n" + "=" * 70)
print("TASK 5: Erdos-Kac type: is (log(R(n)) - mean) / std ~ Normal?")
print("=" * 70)

# For N=100000, compute standardized values and check empirical CDF vs normal
N = 100000
data = [logR[n] for n in range(2, N + 1)]
count = len(data)
mean = sum(data) / count
var = sum((x - mean)**2 for x in data) / count
std = math.sqrt(var)

standardized = [(x - mean) / std for x in data]

# Empirical CDF at standard quantiles vs normal CDF
def normal_cdf(x):
    """Approximation of standard normal CDF."""
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))

quantiles = [-3, -2.5, -2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 2.5, 3]

print(f"\n  Comparison of empirical CDF vs standard normal CDF (N={N}):")
print(f"  | {'z':>6s} | {'Phi(z) normal':>14s} | {'F_emp(z)':>14s} | {'difference':>12s} |")
print(f"  |{'-'*8}|{'-'*16}|{'-'*16}|{'-'*14}|")

standardized_sorted = sorted(standardized)
for z in quantiles:
    phi_z = normal_cdf(z)
    # empirical: fraction of standardized values <= z
    # binary search
    lo, hi = 0, count
    while lo < hi:
        mid = (lo + hi) // 2
        if standardized_sorted[mid] <= z:
            lo = mid + 1
        else:
            hi = mid
    f_emp = lo / count
    diff = f_emp - phi_z
    print(f"  | {z:>6.1f} | {phi_z:>14.6f} | {f_emp:>14.6f} | {diff:>+12.6f} |")

# Kolmogorov-Smirnov statistic
print(f"\n  Kolmogorov-Smirnov test:")
ks_stat = 0.0
for i, x in enumerate(standardized_sorted):
    f_emp = (i + 1) / count
    f_norm = normal_cdf(x)
    d = abs(f_emp - f_norm)
    if d > ks_stat:
        ks_stat = d

# Critical values: 1.36/sqrt(n) for alpha=0.05
ks_crit_05 = 1.36 / math.sqrt(count)
ks_crit_01 = 1.63 / math.sqrt(count)
print(f"  KS statistic D_n   = {ks_stat:.6f}")
print(f"  Critical (alpha=5%) = {ks_crit_05:.6f}")
print(f"  Critical (alpha=1%) = {ks_crit_01:.6f}")
if ks_stat > ks_crit_01:
    print(f"  Result: REJECT normality at 1% level (D_n >> critical)")
elif ks_stat > ks_crit_05:
    print(f"  Result: REJECT normality at 5% level")
else:
    print(f"  Result: Cannot reject normality at 5% level")

# ASCII histogram of standardized values
print(f"\n  Histogram of standardized (log(R(n)) - mean) / std:")
s_min, s_max = -4.0, 4.0  # clip to [-4, 4]
NBINS2 = 40
bin_w2 = (s_max - s_min) / NBINS2
bins2 = [0] * NBINS2
clipped = [max(s_min, min(s_max - 1e-10, x)) for x in standardized]
for v in clipped:
    idx = int((v - s_min) / bin_w2)
    if idx >= NBINS2:
        idx = NBINS2 - 1
    bins2[idx] += 1

max_count2 = max(bins2)
# Also compute expected normal counts for comparison
normal_expected = []
for i in range(NBINS2):
    lo = s_min + i * bin_w2
    hi = lo + bin_w2
    expected = count * (normal_cdf(hi) - normal_cdf(lo))
    normal_expected.append(expected)
max_expected = max(normal_expected)

# Normalize both to same scale
BWIDTH = 50
print(f"  {'z':>6s}  {'empirical':>8s}  {'normal':>7s}  bar (# = empirical, . = normal)")
print(f"  {'-'*6}  {'-'*8}  {'-'*7}  {'-'*BWIDTH}")
for i in range(NBINS2):
    lo = s_min + i * bin_w2
    e_len = int(bins2[i] / max_count2 * BWIDTH) if max_count2 > 0 else 0
    n_len = int(normal_expected[i] / max_count2 * BWIDTH) if max_count2 > 0 else 0
    # Build composite bar
    bar = []
    for j in range(max(e_len, n_len)):
        if j < e_len and j < n_len:
            bar.append('#')
        elif j < e_len:
            bar.append('#')
        else:
            bar.append('.')
    print(f"  {lo:>6.2f}  {bins2[i]:>8d}  {normal_expected[i]:>7.0f}  {''.join(bar)}")

# ============================================================
# BONUS: Special values of R(n)
# ============================================================
print("\n" + "=" * 70)
print("BONUS: Notable values of R(n)")
print("=" * 70)

# R at primes
print("\n  R(p) for first 10 primes:")
primes_found = []
for n in range(2, 200):
    if all(n % d != 0 for d in range(2, int(n**0.5)+1)):
        primes_found.append(n)
    if len(primes_found) >= 10:
        break

print(f"  | {'p':>5s} | {'sigma(p)':>9s} | {'phi(p)':>8s} | {'tau(p)':>7s} | {'R(p)':>12s} | {'log R(p)':>10s} |")
print(f"  |{'-'*7}|{'-'*11}|{'-'*10}|{'-'*9}|{'-'*14}|{'-'*12}|")
for p in primes_found:
    print(f"  | {p:>5d} | {sigma[p]:>9d} | {phi[p]:>8d} | {tau[p]:>7d} | {R_values[p]:>12.6f} | {logR[p]:>10.6f} |")

# R(p) = (p+1)(p-1)/(2p) = (p^2-1)/(2p)
print(f"\n  For prime p: R(p) = (p+1)(p-1)/(2p) = (p^2-1)/(2p)")
print(f"  As p -> inf: R(p) -> p/2, so log(R(p)) -> log(p) - log(2)")

# R at perfect numbers
print(f"\n  R at perfect numbers:")
for n in [6, 28, 496, 8128]:
    if n <= NMAX:
        print(f"    R({n}) = {R_values[n]:.6f}, log R = {logR[n]:.6f}")

# R at prime powers
print(f"\n  R(p^k) for p=2:")
n = 2
while n <= NMAX:
    print(f"    R({n}) = {R_values[n]:.6f}, log R = {logR[n]:.6f}")
    n *= 2

print("\nDone.")
