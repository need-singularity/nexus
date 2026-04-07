"""
H-CX-71: R-spectrum fractal dimension convergence to 1/(2*pi)
Hypothesis: box-counting dim of {R(n): n=1..N} -> 1/(2*pi) as N->inf
R(n) = sigma(n)*phi(n) / (n * tau(n))
"""
import math
import numpy as np
from sympy import divisor_sigma, totient, divisors, factorint

TARGET = 1 / (2 * math.pi)
print(f"Target: 1/(2*pi) = {TARGET:.8f}")
print("=" * 70)
print("H-CX-71: R-spectrum fractal dimension convergence analysis")
print("=" * 70)

def tau(n):
    return len(divisors(n))

def sigma(n):
    return int(divisor_sigma(n, 1))

def phi(n):
    return int(totient(n))

def R(n):
    return sigma(n) * phi(n) / (n * tau(n))

# Precompute R values for N_max
N_max = 50000
print(f"\nPrecomputing R(n) for n=1..{N_max}...")

R_vals = np.zeros(N_max + 1)
for n in range(1, N_max + 1):
    R_vals[n] = R(n)
    if n % 10000 == 0:
        print(f"  Progress: {n}/{N_max}")

print("Done precomputing.")

def box_counting_dim(data, epsilons=None):
    """
    Compute box-counting dimension of a 1D set of values.
    For each epsilon, count how many intervals of size epsilon
    contain at least one point.
    Returns (d_box, r_squared, counts, epsilons_used)
    """
    data_arr = np.array(sorted(set(data)))
    data_min = data_arr.min()
    data_max = data_arr.max()
    data_range = data_max - data_min

    if data_range == 0:
        return 0.0, 1.0, [], []

    if epsilons is None:
        epsilons = np.logspace(-3, 0, 50) * data_range

    counts = []
    valid_eps = []
    for eps in epsilons:
        if eps <= 0:
            continue
        # Number of boxes of size eps needed
        n_boxes = len(set(np.floor((data_arr - data_min) / eps).astype(int)))
        if n_boxes > 1:
            counts.append(n_boxes)
            valid_eps.append(eps)

    if len(counts) < 5:
        return np.nan, np.nan, counts, valid_eps

    log_eps_inv = np.log(1.0 / np.array(valid_eps))
    log_counts = np.log(np.array(counts))

    # Linear regression: log(N) = d * log(1/eps) + const
    coeffs = np.polyfit(log_eps_inv, log_counts, 1)
    d_box = coeffs[0]

    # R^2
    predicted = np.polyval(coeffs, log_eps_inv)
    ss_res = np.sum((log_counts - predicted)**2)
    ss_tot = np.sum((log_counts - log_counts.mean())**2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 1.0

    return d_box, r2, counts, valid_eps

# N values to test
N_list = [100, 500, 1000, 2000, 5000, 10000, 20000, 50000]

results = []

print(f"\n{'N':>8} | {'Unique R':>10} | {'d_box':>10} | {'R^2':>8} | {'|d-1/2pi|':>12} | {'Ratio d/(1/2pi)':>16}")
print("-" * 75)

for N in N_list:
    data = R_vals[1:N+1]
    # Filter to [0, 5] as specified
    data_filtered = data[(data >= 0) & (data <= 5)]

    unique_vals = np.unique(data_filtered)
    n_unique = len(unique_vals)

    d_box, r2, counts, eps_used = box_counting_dim(unique_vals)

    diff = abs(d_box - TARGET) if not math.isnan(d_box) else float('nan')
    ratio = d_box / TARGET if not math.isnan(d_box) else float('nan')

    results.append({
        'N': N,
        'n_unique': n_unique,
        'd_box': d_box,
        'r2': r2,
        'diff': diff,
        'ratio': ratio
    })

    print(f"{N:>8} | {n_unique:>10} | {d_box:>10.6f} | {r2:>8.4f} | {diff:>12.6f} | {ratio:>16.4f}")

print(f"\nTarget: 1/(2*pi) = {TARGET:.8f}")

# ASCII plot: d_box vs log(N)
print("\n--- ASCII Plot: d_box vs N ---")
valid_results = [r for r in results if not math.isnan(r['d_box'])]
if valid_results:
    d_vals = [r['d_box'] for r in valid_results]
    n_vals = [r['N'] for r in valid_results]

    d_min = min(d_vals) - 0.02
    d_max = max(d_vals) + 0.02
    height = 20
    width = 60

    print(f"d_box")
    print(f"{d_max:.4f} |")
    rows = []
    for i in range(height):
        d_level = d_max - i * (d_max - d_min) / height
        row = [' '] * width
        # Mark 1/(2*pi) line
        target_row = int((d_max - TARGET) / (d_max - d_min) * height)
        if i == target_row:
            row = ['-'] * width
            row[0] = '|'
        rows.append((d_level, row))

    # Place data points
    for r in valid_results:
        col_idx = int((math.log(r['N']) - math.log(n_vals[0])) /
                      (math.log(n_vals[-1]) - math.log(n_vals[0])) * (width - 1))
        row_idx = int((d_max - r['d_box']) / (d_max - d_min) * height)
        row_idx = max(0, min(height - 1, row_idx))
        col_idx = max(0, min(width - 1, col_idx))
        if rows[row_idx][1][col_idx] == '-':
            rows[row_idx][1][col_idx] = 'X'
        else:
            rows[row_idx][1][col_idx] = '*'

    for d_level, row in rows:
        print(f"{d_level:.4f} |{''.join(row)}")
    print(f"{d_min:.4f} |")
    print(f"        +{'-'*width}")
    # x-axis labels
    n_labels = "         " + "|".join([f"{r['N']:^7}" for r in valid_results[:8]])
    print(f"N:  {n_labels}")
    print(f"         (log scale)")
    print(f"Legend: * = d_box(N), --- = target 1/(2*pi)={TARGET:.5f}, X = d_box on target line")

# Convergence analysis
print("\n--- Convergence Analysis ---")
if len(valid_results) >= 3:
    # Fit d_box vs log(N) to see trend
    log_n = np.array([math.log(r['N']) for r in valid_results])
    d_arr = np.array([r['d_box'] for r in valid_results])
    coeffs = np.polyfit(log_n, d_arr, 1)
    slope = coeffs[0]
    intercept = coeffs[1]
    print(f"Linear fit: d_box = {slope:.6f} * log(N) + {intercept:.6f}")
    print(f"Trend: {'increasing' if slope > 0 else 'decreasing'} with slope {slope:.6f}")

    # Extrapolate to large N
    for N_extrap in [100000, 1000000, 10000000]:
        d_extrap = slope * math.log(N_extrap) + intercept
        print(f"  Extrapolated d_box(N={N_extrap:,}) = {d_extrap:.6f}")

    # Statistical test: is the trend heading toward TARGET?
    # Check if the last few values are closer to target than first few
    first_half = valid_results[:len(valid_results)//2]
    second_half = valid_results[len(valid_results)//2:]
    avg_first = np.mean([r['diff'] for r in first_half])
    avg_second = np.mean([r['diff'] for r in second_half])
    print(f"\nMean |d_box - 1/(2*pi)|:")
    print(f"  First half (smaller N): {avg_first:.6f}")
    print(f"  Second half (larger N): {avg_second:.6f}")
    print(f"  Converging toward target? {'YES' if avg_second < avg_first else 'NO'}")

    # Check specifically: is d_box trending toward 0.155 or 0.159?
    print(f"\nFinal d_box at N={N_list[-1]}: {valid_results[-1]['d_box']:.6f}")
    print(f"Target 1/(2*pi) = {TARGET:.6f} = {TARGET:.8f}")
    print(f"Is d_box(N=50000) within 10% of 1/(2*pi)? {abs(valid_results[-1]['d_box'] - TARGET) < 0.1 * TARGET}")
    print(f"Is d_box(N=50000) within 5% of 1/(2*pi)?  {abs(valid_results[-1]['d_box'] - TARGET) < 0.05 * TARGET}")
    print(f"Is d_box(N=50000) within 1% of 1/(2*pi)?  {abs(valid_results[-1]['d_box'] - TARGET) < 0.01 * TARGET}")

# Show R distribution summary
print("\n--- R(n) Distribution Summary ---")
data_full = R_vals[1:N_max+1]
data_full = data_full[(data_full >= 0) & (data_full <= 5)]
print(f"Min R:    {data_full.min():.6f}")
print(f"Max R:    {data_full.max():.6f}")
print(f"Mean R:   {data_full.mean():.6f}")
print(f"Median R: {np.median(data_full):.6f}")
print(f"Unique R values in [0,5] for N=50000: {len(np.unique(data_full))}")

# Histogram of R values
print("\n--- ASCII Histogram of R(n) distribution (N=50000) ---")
hist_vals = np.array(data_full)
bins = np.linspace(0, 3, 31)
hist, edges = np.histogram(hist_vals, bins=bins)
max_h = hist.max()
bar_width = 40
for i, (lo, hi, count) in enumerate(zip(edges[:-1], edges[1:], hist)):
    bar_len = int(count / max_h * bar_width)
    print(f"[{lo:.2f}-{hi:.2f}] {'#'*bar_len} {count}")

print("\nDone.")
