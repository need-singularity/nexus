#!/usr/bin/env python3
"""
Verify H-MP-15: R(n) = sigma(n)*phi(n)/(n*tau(n)) spectrum has Cantor-like structure.

Computes R(n) for n=2..50000, then analyzes:
  1. Distinct R values and their distribution
  2. Gap structure for various thresholds
  3. Box-counting dimension estimate
  4. Hausdorff dimension estimate
"""

import math
import numpy as np
from collections import Counter

# --- Arithmetic functions ---

def sigma(n):
    s = 0
    for i in range(1, int(n**0.5)+1):
        if n % i == 0:
            s += i + (n//i if i*i != n else 0)
    return s

def tau(n):
    t = 0
    for i in range(1, int(n**0.5)+1):
        if n % i == 0:
            t += 1 + (1 if i*i != n else 0)
    return t

def phi(n):
    r = n; t = n; p = 2
    while p*p <= t:
        if t % p == 0:
            while t % p == 0: t //= p
            r -= r // p
        p += 1
    if t > 1: r -= r // t
    return r

# --- Step 1: Compute all R(n) ---
print("=" * 70)
print("H-MP-15 VERIFICATION: Cantor-like structure of R(n) spectrum")
print("  R(n) = sigma(n) * phi(n) / (n * tau(n))")
print("=" * 70)

N_MAX = 50000
print(f"\nComputing R(n) for n = 2 .. {N_MAX} ...")

r_values = []
for n in range(2, N_MAX + 1):
    s = sigma(n)
    p = phi(n)
    t = tau(n)
    r = (s * p) / (n * t)
    r_values.append(r)

r_array = np.array(r_values)
distinct = np.sort(np.unique(r_array))

print(f"  Total R values computed: {len(r_values)}")
print(f"  Distinct R values:       {len(distinct)}")
print(f"  R range: [{distinct[0]:.6f}, {distinct[-1]:.6f}]")
print(f"  Mean:    {np.mean(r_array):.6f}")
print(f"  Median:  {np.median(r_array):.6f}")
print(f"  Std:     {np.std(r_array):.6f}")

# --- Step 2: Distribution summary ---
print("\n" + "=" * 70)
print("DISTRIBUTION OF R(n) VALUES")
print("=" * 70)

boundaries = [0, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0, 10.0, 20.0, 50.0, 100.0]
print(f"\n{'Interval':<20} {'Count':>8} {'Pct':>8} {'Distinct':>10}")
print("-" * 50)
for i in range(len(boundaries) - 1):
    lo, hi = boundaries[i], boundaries[i+1]
    mask = (r_array >= lo) & (r_array < hi)
    cnt = int(np.sum(mask))
    pct = 100.0 * cnt / len(r_array)
    d_mask = (distinct >= lo) & (distinct < hi)
    d_cnt = int(np.sum(d_mask))
    print(f"  [{lo:6.1f}, {hi:6.1f})  {cnt:8d}  {pct:7.2f}%  {d_cnt:10d}")

# --- Step 3: Gap analysis for various thresholds ---
print("\n" + "=" * 70)
print("GAP ANALYSIS")
print("  For each threshold T, analyze gaps in [0, T]")
print("=" * 70)

thresholds = [1, 2, 3, 5, 10, 20, 50, 100]
print(f"\n{'T':>6} {'Distinct':>10} {'#Gaps>0.01':>12} {'TotalGap':>12} {'GapFrac':>10} {'MaxGap':>10}")
print("-" * 65)

for T in thresholds:
    vals_in = distinct[distinct < T]
    if len(vals_in) < 2:
        print(f"  {T:6.0f}  {len(vals_in):10d}  {'N/A':>12}  {'N/A':>12}  {'N/A':>10}  {'N/A':>10}")
        continue
    gaps = np.diff(vals_in)
    total_gap = 0.0
    n_big_gaps = 0
    max_gap = 0.0
    # Gap = intervals NOT covered. Total range covered by values is vals_in[-1] - vals_in[0]
    # But we measure against [0, T]. Gaps are spaces between consecutive distinct values.
    # We include the gap from 0 to first value, and from last value to T.
    all_gaps = np.concatenate([[vals_in[0] - 0], gaps, [T - vals_in[-1]]])
    # A "gap" is significant if > some small threshold (say 0.01)
    sig_gaps = all_gaps[all_gaps > 0.01]
    total_gap = float(np.sum(all_gaps))  # This equals T minus measure of point set (which is 0 for discrete)
    # For a discrete set, total gap = T (trivially). Instead, let's use a resolution.
    # Better: use a small epsilon to "fatten" points, then measure coverage.
    eps = 0.001
    # Coverage: union of [v-eps, v+eps] for each v in vals_in, clipped to [0, T]
    intervals = []
    for v in vals_in:
        intervals.append((max(0, v - eps), min(T, v + eps)))
    # Merge overlapping intervals
    intervals.sort()
    merged = [intervals[0]]
    for lo, hi in intervals[1:]:
        if lo <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], hi))
        else:
            merged.append((lo, hi))
    coverage = sum(hi - lo for lo, hi in merged)
    gap_frac = 1.0 - coverage / T
    max_gap_val = float(np.max(all_gaps))
    n_big = int(np.sum(all_gaps > 0.01))
    print(f"  {T:6.0f}  {len(vals_in):10d}  {n_big:12d}  {T - coverage:12.4f}  {gap_frac:10.6f}  {max_gap_val:10.6f}")

# --- Step 4: Box-counting dimension ---
print("\n" + "=" * 70)
print("BOX-COUNTING DIMENSION ESTIMATE")
print("  Range: [0, 10]")
print("=" * 70)

vals_010 = distinct[(distinct >= 0) & (distinct <= 10)]
print(f"  Distinct R values in [0,10]: {len(vals_010)}")

epsilons = [0.5, 0.2, 0.1, 0.05, 0.02, 0.01, 0.005, 0.002, 0.001]
box_counts = []

print(f"\n{'epsilon':>10} {'N(eps)':>10} {'log(1/eps)':>12} {'log(N)':>10}")
print("-" * 46)

for eps in epsilons:
    # Count boxes of width eps in [0, 10] that contain at least one value
    n_boxes = int(10.0 / eps)
    occupied = set()
    for v in vals_010:
        box_idx = int(v / eps)
        if box_idx >= n_boxes:
            box_idx = n_boxes - 1
        occupied.add(box_idx)
    N_eps = len(occupied)
    box_counts.append(N_eps)
    print(f"  {eps:10.4f}  {N_eps:10d}  {math.log(1/eps):12.4f}  {math.log(N_eps):10.4f}")

# Linear fit: log(N) = d * log(1/eps) + c
log_inv_eps = np.array([math.log(1/e) for e in epsilons])
log_N = np.array([math.log(n) for n in box_counts])

# Fit using numpy
coeffs = np.polyfit(log_inv_eps, log_N, 1)
d_box = coeffs[0]
c_box = coeffs[1]

print(f"\n  Linear fit: log(N) = {d_box:.6f} * log(1/eps) + {c_box:.4f}")
print(f"  Box-counting dimension estimate: d = {d_box:.6f}")
print(f"  R-squared: ", end="")
ss_res = np.sum((log_N - (d_box * log_inv_eps + c_box))**2)
ss_tot = np.sum((log_N - np.mean(log_N))**2)
r_sq = 1 - ss_res / ss_tot
print(f"{r_sq:.6f}")

if d_box < 1.0:
    print(f"\n  >>> d = {d_box:.4f} < 1  =>  CANTOR-LIKE (fractal) spectrum!")
else:
    print(f"\n  >>> d = {d_box:.4f} >= 1  =>  NOT Cantor-like (fills interval)")

# --- Step 5: Hausdorff dimension estimate via correlation dimension ---
print("\n" + "=" * 70)
print("HAUSDORFF DIMENSION ESTIMATE (via correlation integral)")
print("  Range: [0, 10]")
print("=" * 70)

# Correlation dimension: C(r) ~ r^d
# C(r) = fraction of pairs with |xi - xj| < r
# Use a subsample for speed
vals_sub = vals_010
if len(vals_sub) > 5000:
    rng = np.random.RandomState(42)
    vals_sub = rng.choice(vals_010, 5000, replace=False)
    vals_sub = np.sort(vals_sub)

n_pts = len(vals_sub)
print(f"  Using {n_pts} points for correlation dimension")

radii = [0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
corr_counts = []

for r in radii:
    count = 0
    # Efficient: since sorted, use binary search
    for i in range(n_pts):
        # Count points in (vals_sub[i], vals_sub[i] + r]
        j_lo = np.searchsorted(vals_sub, vals_sub[i] - r, side='left')
        j_hi = np.searchsorted(vals_sub, vals_sub[i] + r, side='right')
        count += (j_hi - j_lo - 1)  # exclude self
    C_r = count / (n_pts * (n_pts - 1))
    corr_counts.append(C_r)

print(f"\n{'r':>10} {'C(r)':>12} {'log(r)':>10} {'log(C)':>10}")
print("-" * 46)
valid_r = []
valid_C = []
for r, C in zip(radii, corr_counts):
    if C > 0:
        print(f"  {r:10.4f}  {C:12.8f}  {math.log(r):10.4f}  {math.log(C):10.4f}")
        valid_r.append(math.log(r))
        valid_C.append(math.log(C))
    else:
        print(f"  {r:10.4f}  {C:12.8f}  {math.log(r):10.4f}  {'  -inf':>10}")

if len(valid_r) >= 3:
    coeffs_h = np.polyfit(valid_r, valid_C, 1)
    d_corr = coeffs_h[0]
    print(f"\n  Correlation dimension estimate: d_corr = {d_corr:.6f}")

    # Also fit just the small-r regime (first 5 valid points)
    n_fit = min(5, len(valid_r))
    coeffs_small = np.polyfit(valid_r[:n_fit], valid_C[:n_fit], 1)
    d_small = coeffs_small[0]
    print(f"  Small-r regime (first {n_fit} points): d_small = {d_small:.6f}")

# --- Step 6: ASCII visualization ---
print("\n" + "=" * 70)
print("ASCII SPECTRUM DENSITY VISUALIZATION")
print("  R(n) density in [0, 10], bin width = 0.1")
print("=" * 70)

bins = np.arange(0, 10.01, 0.1)
hist, _ = np.histogram(r_array[(r_array >= 0) & (r_array <= 10)], bins=bins)
max_h = max(hist) if max(hist) > 0 else 1
width = 60

print(f"\n  {'Bin':>8}  {'Count':>6}  Distribution")
print("  " + "-" * 78)
for i in range(len(hist)):
    bar_len = int(width * hist[i] / max_h)
    bar = "#" * bar_len
    lo = bins[i]
    hi = bins[i+1]
    if i % 5 == 0 or hist[i] > 0.5 * max_h:  # Print every 5th or high-density
        print(f"  [{lo:5.1f},{hi:5.1f})  {hist[i]:6d}  {bar}")

# Distinct-value density (how many distinct values per bin)
print(f"\n  DISTINCT value density (bin=0.1):")
hist_d, _ = np.histogram(vals_010, bins=bins)
max_hd = max(hist_d) if max(hist_d) > 0 else 1

print(f"\n  {'Bin':>8}  {'#Dist':>6}  Distribution")
print("  " + "-" * 78)
for i in range(len(hist_d)):
    bar_len = int(width * hist_d[i] / max_hd)
    bar = "=" * bar_len
    lo = bins[i]
    hi = bins[i+1]
    if i % 5 == 0 or hist_d[i] > 0.5 * max_hd:
        print(f"  [{lo:5.1f},{hi:5.1f})  {hist_d[i]:6d}  {bar}")

# --- Fine-grained gap visualization ---
print(f"\n  GAP STRUCTURE in [0, 2] (bin=0.01, showing empty/occupied):")
fine_bins = np.arange(0, 2.001, 0.01)
fine_hist, _ = np.histogram(vals_010[(vals_010 >= 0) & (vals_010 <= 2)], bins=fine_bins)

# Show as a strip: '#' = occupied, '.' = empty
line_width = 100  # characters per line
n_fine = len(fine_hist)
lines_needed = (n_fine + line_width - 1) // line_width

print(f"  Each char = bin of width 0.01. '#'=occupied, '.'=empty")
for line_idx in range(lines_needed):
    start = line_idx * line_width
    end = min(start + line_width, n_fine)
    strip = ""
    for i in range(start, end):
        strip += "#" if fine_hist[i] > 0 else "."
    lo_val = fine_bins[start]
    hi_val = fine_bins[end]
    print(f"  [{lo_val:5.2f}-{hi_val:5.2f}] {strip}")

occupied_fine = sum(1 for h in fine_hist if h > 0)
empty_fine = sum(1 for h in fine_hist if h == 0)
print(f"\n  In [0,2]: {occupied_fine} occupied bins, {empty_fine} empty bins (of {n_fine} total)")
print(f"  Occupancy fraction: {occupied_fine/n_fine:.4f}")

# --- Summary ---
print("\n" + "=" * 70)
print("SUMMARY: H-MP-15 VERDICT")
print("=" * 70)
print(f"""
  R(n) = sigma(n)*phi(n) / (n*tau(n))  for n = 2..{N_MAX}

  Total values:    {len(r_values)}
  Distinct values: {len(distinct)}
  Range:           [{distinct[0]:.6f}, {distinct[-1]:.6f}]

  Box-counting dimension (in [0,10]):  d_box  = {d_box:.4f}  (R^2 = {r_sq:.4f})
  Correlation dimension (in [0,10]):   d_corr = {d_corr:.4f}

  Interpretation:
    d = 1.0  =>  fills the interval (no fractal structure)
    d < 1.0  =>  Cantor-like fractal gaps
    d > 1.0  =>  possible measurement artifact or multi-scale clustering
""")

if d_box < 0.95:
    print("  RESULT: SUPPORTED - The R(n) spectrum shows Cantor-like fractal structure")
    print(f"          with box-counting dimension d ~ {d_box:.3f} < 1")
elif d_box < 1.05:
    print("  RESULT: BORDERLINE - The R(n) spectrum is close to dimension 1")
    print(f"          d ~ {d_box:.3f}, not clearly fractal")
else:
    print("  RESULT: NOT SUPPORTED - The R(n) spectrum fills the interval")
    print(f"          d ~ {d_box:.3f} >= 1, no Cantor-like structure detected")

print("\n" + "=" * 70)
print("DONE")
print("=" * 70)
