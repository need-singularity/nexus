"""
H-CX-71: R-spectrum fractal dimension convergence to 1/(2*pi)
R(n) = sigma(n)*phi(n)/(n*tau(n))

Key finding first: R(n) is unbounded (grows like p/2 for primes p),
so [0,5] filter loses >99% of data.

We analyze three variants:
1. Full R(n) in [0.75, max] -- actual set
2. log(R(n)) -- logarithmic transform
3. Normalized: R(n)/n -- scaled version
4. Restricted to composite n only (avoid prime dominance)
"""
import math
import numpy as np
from sympy import divisor_sigma, totient, divisors, isprime
from functools import lru_cache

TARGET = 1 / (2 * math.pi)
print(f"Target: 1/(2*pi) = {TARGET:.8f}")
print("=" * 70)
print("H-CX-71 v2: R-spectrum fractal dimension (corrected range)")
print("=" * 70)

# Fast precomputation using sieve-like approach
def precompute_arith(N_max):
    sigma_arr = np.zeros(N_max + 1, dtype=np.int64)
    tau_arr = np.zeros(N_max + 1, dtype=np.int64)
    phi_arr = np.arange(N_max + 1, dtype=np.int64)

    # Sieve for sigma and tau
    for d in range(1, N_max + 1):
        for multiple in range(d, N_max + 1, d):
            sigma_arr[multiple] += d
            tau_arr[multiple] += 1

    # Sieve for phi (Euler's product)
    for p in range(2, N_max + 1):
        if phi_arr[p] == p:  # p is prime
            for multiple in range(p, N_max + 1, p):
                phi_arr[multiple] -= phi_arr[multiple] // p

    return sigma_arr, tau_arr, phi_arr

N_max = 50000
print(f"\nPrecomputing arithmetic functions via sieve for n=1..{N_max}...")
sigma_arr, tau_arr, phi_arr = precompute_arith(N_max)
print("Done.")

# Compute R(n) for all n
R_arr = (sigma_arr[1:] * phi_arr[1:]).astype(np.float64) / (np.arange(1, N_max+1) * tau_arr[1:])

print(f"\nR(n) statistics for n=1..{N_max}:")
print(f"  Min:      {R_arr.min():.6f}  (at n={np.argmin(R_arr)+1})")
print(f"  Max:      {R_arr.max():.6f}  (at n={np.argmax(R_arr)+1})")
print(f"  Mean:     {R_arr.mean():.6f}")
print(f"  Median:   {np.median(R_arr):.6f}")
print(f"  Unique:   {len(np.unique(R_arr))}")
print(f"  In [0,5]: {(R_arr <= 5).sum()} ({100*(R_arr<=5).mean():.1f}%)")
print(f"  In [0,1]: {(R_arr <= 1).sum()} ({100*(R_arr<=1).mean():.1f}%)")

def box_counting_dim_full(data, n_eps=50):
    """Box-counting for 1D set. Returns d_box and R^2."""
    data_arr = np.unique(data)
    if len(data_arr) < 2:
        return np.nan, np.nan
    d_min = data_arr.min()
    d_max = data_arr.max()
    d_range = d_max - d_min
    if d_range == 0:
        return 0.0, 1.0

    # Use log-spaced epsilons relative to data range
    epsilons = np.logspace(-4, 0, n_eps) * d_range

    counts = []
    valid_eps = []
    for eps in epsilons:
        if eps <= 0:
            continue
        boxes = np.floor((data_arr - d_min) / eps).astype(np.int64)
        n_boxes = len(np.unique(boxes))
        if n_boxes > 1:
            counts.append(n_boxes)
            valid_eps.append(eps)

    if len(counts) < 5:
        return np.nan, np.nan

    log_eps_inv = np.log(1.0 / np.array(valid_eps))
    log_counts = np.log(np.array(counts))

    # Linear regression
    coeffs = np.polyfit(log_eps_inv, log_counts, 1)
    d_box = coeffs[0]

    predicted = np.polyval(coeffs, log_eps_inv)
    ss_res = np.sum((log_counts - predicted)**2)
    ss_tot = np.sum((log_counts - log_counts.mean())**2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 1.0

    return d_box, r2

N_list = [100, 500, 1000, 2000, 5000, 10000, 20000, 50000]

print("\n" + "=" * 70)
print("VARIANT 1: Full R(n) set (no range restriction)")
print("=" * 70)
print(f"\n{'N':>8} | {'Unique R':>10} | {'d_box':>10} | {'R^2':>8} | {'|d-1/2pi|':>12} | {'Ratio':>8}")
print("-" * 70)

results_v1 = []
for N in N_list:
    data = R_arr[:N]
    d_box, r2 = box_counting_dim_full(data)
    diff = abs(d_box - TARGET) if not math.isnan(d_box) else float('nan')
    ratio = d_box / TARGET if not math.isnan(d_box) else float('nan')
    n_unique = len(np.unique(data))
    results_v1.append({'N': N, 'd': d_box, 'r2': r2, 'diff': diff, 'ratio': ratio, 'nu': n_unique})
    print(f"{N:>8} | {n_unique:>10} | {d_box:>10.6f} | {r2:>8.4f} | {diff:>12.6f} | {ratio:>8.4f}")

print("\n" + "=" * 70)
print("VARIANT 2: log(R(n)) set")
print("=" * 70)
print(f"\n{'N':>8} | {'Unique':>10} | {'d_box':>10} | {'R^2':>8} | {'|d-1/2pi|':>12} | {'Ratio':>8}")
print("-" * 70)

results_v2 = []
for N in N_list:
    data = np.log(R_arr[:N])
    d_box, r2 = box_counting_dim_full(data)
    diff = abs(d_box - TARGET) if not math.isnan(d_box) else float('nan')
    ratio = d_box / TARGET if not math.isnan(d_box) else float('nan')
    n_unique = len(np.unique(data))
    results_v2.append({'N': N, 'd': d_box, 'r2': r2, 'diff': diff, 'ratio': ratio, 'nu': n_unique})
    print(f"{N:>8} | {n_unique:>10} | {d_box:>10.6f} | {r2:>8.4f} | {diff:>12.6f} | {ratio:>8.4f}")

print("\n" + "=" * 70)
print("VARIANT 3: R(n) restricted to composite n (no primes)")
print("Motivation: primes dominate R(n) range, composites have richer structure")
print("=" * 70)
# is_prime sieve
is_prime_arr = np.ones(N_max + 1, dtype=bool)
is_prime_arr[0] = is_prime_arr[1] = False
for p in range(2, int(N_max**0.5)+1):
    if is_prime_arr[p]:
        is_prime_arr[p*p::p] = False

print(f"\n{'N':>8} | {'Composites':>12} | {'Unique':>10} | {'d_box':>10} | {'R^2':>8} | {'|d-1/2pi|':>12}")
print("-" * 75)

results_v3 = []
for N in N_list:
    composite_mask = ~is_prime_arr[1:N+1]
    data = R_arr[:N][composite_mask]
    if len(data) < 10:
        results_v3.append({'N': N, 'd': np.nan, 'r2': np.nan, 'diff': np.nan, 'nu': 0, 'nc': 0})
        continue
    d_box, r2 = box_counting_dim_full(data)
    diff = abs(d_box - TARGET) if not math.isnan(d_box) else float('nan')
    n_unique = len(np.unique(data))
    results_v3.append({'N': N, 'd': d_box, 'r2': r2, 'diff': diff, 'nu': n_unique, 'nc': len(data)})
    print(f"{N:>8} | {len(data):>12} | {n_unique:>10} | {d_box:>10.6f} | {r2:>8.4f} | {diff:>12.6f}")

print("\n" + "=" * 70)
print("VARIANT 4: R(n) in [0.75, 5] (original hypothesis range)")
print("=" * 70)
print(f"\n{'N':>8} | {'In[0.75,5]':>12} | {'Unique':>10} | {'d_box':>10} | {'R^2':>8} | {'|d-1/2pi|':>12}")
print("-" * 75)

results_v4 = []
for N in N_list:
    data_all = R_arr[:N]
    data = data_all[(data_all >= 0.75) & (data_all <= 5)]
    n_filt = len(data)
    n_unique = len(np.unique(data))
    if n_unique < 5:
        results_v4.append({'N': N, 'd': np.nan, 'r2': np.nan, 'diff': np.nan, 'nu': n_unique, 'nf': n_filt})
        print(f"{N:>8} | {n_filt:>12} | {n_unique:>10} | {'N/A':>10} | {'N/A':>8} | {'N/A':>12}")
        continue
    d_box, r2 = box_counting_dim_full(data)
    diff = abs(d_box - TARGET) if not math.isnan(d_box) else float('nan')
    results_v4.append({'N': N, 'd': d_box, 'r2': r2, 'diff': diff, 'nu': n_unique, 'nf': n_filt})
    print(f"{N:>8} | {n_filt:>12} | {n_unique:>10} | {d_box:>10.6f} | {r2:>8.4f} | {diff:>12.6f}")

# Convergence analysis for each variant
print("\n" + "=" * 70)
print("CONVERGENCE ANALYSIS")
print("=" * 70)

for name, results in [("V1 Full R(n)", results_v1), ("V2 log(R(n))", results_v2), ("V3 Composites", results_v3)]:
    valid = [r for r in results if not math.isnan(r.get('d', float('nan')))]
    if len(valid) < 3:
        continue
    log_n = np.array([math.log(r['N']) for r in valid])
    d_arr = np.array([r['d'] for r in valid])
    coeffs = np.polyfit(log_n, d_arr, 1)
    slope = coeffs[0]
    intercept = coeffs[1]
    final_d = valid[-1]['d']
    print(f"\n{name}:")
    print(f"  Slope (d_box vs log N): {slope:.6f}")
    print(f"  d_box(N={valid[-1]['N']:,}) = {final_d:.6f}")
    print(f"  Target 1/(2*pi) = {TARGET:.6f}")
    print(f"  Ratio d/target = {final_d/TARGET:.4f}")
    if abs(slope) < 1e-6:
        # Flat -- converged or stuck
        print(f"  Status: FLAT (no convergence toward target)")
    elif (slope > 0 and final_d < TARGET) or (slope < 0 and final_d > TARGET):
        print(f"  Status: Trending TOWARD target")
        # Extrapolate where it would reach target
        # TARGET = slope * log(N_cross) + intercept
        if abs(slope) > 1e-10:
            log_n_cross = (TARGET - intercept) / slope
            n_cross = math.exp(log_n_cross)
            print(f"  Would reach target at N ~ {n_cross:.2e}")
    else:
        print(f"  Status: Trending AWAY from target")

# ASCII convergence plot for V1
print("\n--- ASCII Plot: d_box vs N for V1 (Full R(n)) ---")
valid_v1 = [r for r in results_v1 if not math.isnan(r['d'])]
if valid_v1:
    d_vals = [r['d'] for r in valid_v1]
    n_vals_plot = [r['N'] for r in valid_v1]
    d_min_plot = min(min(d_vals), TARGET) - 0.02
    d_max_plot = max(max(d_vals), TARGET) + 0.02
    height = 20
    width = 60

    rows = []
    for i in range(height):
        d_level = d_max_plot - i * (d_max_plot - d_min_plot) / height
        row = list(' ' * width)
        rows.append([d_level, row])

    # Mark target line
    target_row_idx = int((d_max_plot - TARGET) / (d_max_plot - d_min_plot) * height)
    target_row_idx = max(0, min(height-1, target_row_idx))
    rows[target_row_idx][1] = list('-' * width)

    # Place data points
    for r in valid_v1:
        col = int((math.log(r['N']) - math.log(n_vals_plot[0])) /
                  (math.log(n_vals_plot[-1]) - math.log(n_vals_plot[0])) * (width-1))
        row_i = int((d_max_plot - r['d']) / (d_max_plot - d_min_plot) * height)
        row_i = max(0, min(height-1, row_i))
        col = max(0, min(width-1, col))
        rows[row_i][1][col] = '*'

    print(f"d_box (V1 Full R)")
    for d_level, row in rows:
        marker = f"{d_level:.4f}" if abs(d_level - TARGET) < (d_max_plot - d_min_plot) / height else f"{d_level:.4f}"
        print(f"{d_level:.4f} |{''.join(row)}")
    print(f"       +{'-'*width}")
    print(f"N:       {' '*5}".join([f"{r['N']:>7}" for r in valid_v1[:4]]))
    print(f"Legend: * = d_box(N), --- = 1/(2*pi)={TARGET:.5f}")

# Final summary
print("\n" + "=" * 70)
print("FINAL VERDICT")
print("=" * 70)
print(f"\nTarget hypothesis: d_box -> 1/(2*pi) = {TARGET:.6f}")
print()

# Check the closest variant
for name, results in [("V1 Full", results_v1), ("V2 log", results_v2), ("V3 Comp", results_v3)]:
    valid = [r for r in results if not math.isnan(r.get('d', float('nan')))]
    if valid:
        final = valid[-1]
        within_10 = abs(final['d'] - TARGET) < 0.1 * TARGET
        within_5 = abs(final['d'] - TARGET) < 0.05 * TARGET
        within_1 = abs(final['d'] - TARGET) < 0.01 * TARGET
        print(f"{name}: d={final['d']:.6f}, ratio={final['d']/TARGET:.3f}x target")
        print(f"  Within 10%: {within_10}, Within 5%: {within_5}, Within 1%: {within_1}")

print("\nDone.")
