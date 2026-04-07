#!/usr/bin/env python3
"""H-CX-14 Verification: Anomaly Detection = Gravitational Lens Structural Isomorphism Quantification

Method:
1. Write correspondence matrix between R(n) = sigma*phi/(n*tau) spectrum and T(x) tension structure
2. Quantify 6 structural correspondences (name, function form, scaling, boundary)
3. Fit AUROC(K) data: 1-a/K^b vs 1-a*exp(-bK) vs sigmoid
4. Compare structure with mathematical F(s)~1/(s-1) divergence
5. Calculate correspondence consistency score
"""

import numpy as np
from scipy.optimize import curve_fit
import warnings
warnings.filterwarnings('ignore')

np.random.seed(42)

print("=" * 70)
print("H-CX-14 Verification: Anomaly Detection = Gravitational Lens Structural Isomorphism")
print("=" * 70)

# ─────────────────────────────────────────
# 1. R Spectrum Calculation
# ─────────────────────────────────────────

print("\n" + "─" * 70)
print("1. R Spectrum: R(n) = sigma(n)*phi(n) / (n*tau(n))")
print("─" * 70)

def sigma(n):
    """Sum of divisors."""
    return sum(d for d in range(1, n+1) if n % d == 0)

def tau(n):
    """Number of divisors."""
    return sum(1 for d in range(1, n+1) if n % d == 0)

def euler_phi(n):
    """Euler's totient."""
    count = 0
    for i in range(1, n+1):
        if gcd(i, n) == 1:
            count += 1
    return count

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def R(n):
    """R spectrum."""
    return sigma(n) * euler_phi(n) / (n * tau(n))

# R(n) for n=1..100
ns = list(range(1, 101))
Rs = [R(n) for n in ns]

print(f"\n  Perfect Number R values:")
for n in [6, 28]:
    print(f"    R({n}) = {R(n):.6f}")

print(f"\n  Numbers near R=1 (gap analysis):")
for n in ns[:30]:
    if abs(R(n) - 1.0) < 0.3:
        print(f"    R({n:3d}) = {R(n):.4f}  {'*** Perfect!' if R(n) == 1.0 else ''}")

# Gap: Both sides of R=1
rs_array = np.array(Rs)
below_1 = rs_array[rs_array < 1.0]
above_1 = rs_array[rs_array > 1.0]

if len(below_1) > 0 and len(above_1) > 0:
    gap_below = 1.0 - np.max(below_1)
    gap_above = np.min(above_1) - 1.0
    print(f"\n  Gap (around R=1):")
    print(f"    Max below: R = {np.max(below_1):.4f} (gap = {gap_below:.4f})")
    print(f"    Min above: R = {np.min(above_1):.4f} (gap = {gap_above:.4f})")
    total_gap = gap_below + gap_above
    print(f"    Total gap: {total_gap:.4f}")

# ─────────────────────────────────────────
# 2. AUROC(K) Fitting
# ─────────────────────────────────────────

print("\n" + "─" * 70)
print("2. AUROC(K) Data Fitting (H298)")
print("─" * 70)

# Measured data (H298)
K_data = np.array([0, 1, 2, 5, 10, 20, 50])
AUROC_data = np.array([0.58, 0.58, 0.69, 0.67, 0.74, 0.84, 0.95])

# Model 1: Power law: AUROC = 1 - a * K^(-b) (K>0)
def power_model(K, a, b):
    return 1.0 - a * np.power(K + 0.1, -b)

# Model 2: Exponential: AUROC = 1 - a * exp(-b*K)
def exp_model(K, a, b):
    return 1.0 - a * np.exp(-b * K)

# Model 3: Sigmoid: AUROC = L / (1 + a * exp(-b*K))
def sigmoid_model(K, L, a, b):
    return L / (1.0 + a * np.exp(-b * K))

models = {
    "Power law: 1 - a*K^(-b)": (power_model, [0.4, 0.5], 2),
    "Exponential: 1 - a*exp(-bK)": (exp_model, [0.4, 0.05], 2),
    "Sigmoid: L/(1+a*exp(-bK))": (sigmoid_model, [1.0, 2.0, 0.1], 3),
}

fit_results = {}
print(f"\n  {'Model':>30} | {'SSE':>10} | {'R^2':>8} | Parameters")
print(f"  {'─'*30}─┼─{'─'*10}─┼─{'─'*8}─┼─{'─'*30}")

ss_tot = np.sum((AUROC_data - np.mean(AUROC_data))**2)

for name, (func, p0, n_params) in models.items():
    try:
        popt, pcov = curve_fit(func, K_data, AUROC_data, p0=p0, maxfev=10000)
        y_pred = func(K_data, *popt)
        sse = np.sum((AUROC_data - y_pred)**2)
        r2 = 1 - sse / ss_tot
        params_str = ", ".join([f"{p:.4f}" for p in popt])
        print(f"  {name:>30} | {sse:>10.6f} | {r2:>7.4f} | {params_str}")
        fit_results[name] = {"func": func, "params": popt, "sse": sse, "r2": r2}
    except Exception as e:
        print(f"  {name:>30} | {'FAIL':>10} | {'---':>8} | {str(e)[:30]}")

# Best model
best_model = max(fit_results.items(), key=lambda x: x[1]["r2"])
print(f"\n  Best model: {best_model[0]} (R^2 = {best_model[1]['r2']:.4f})")

# AUROC prediction
print(f"\n  Best model predictions:")
K_pred = [0, 1, 2, 5, 10, 20, 50, 100, 200, 500]
for K in K_pred:
    pred = best_model[1]["func"](np.array([K]), *best_model[1]["params"])[0]
    pred = min(pred, 1.0)
    actual = ""
    for i, kd in enumerate(K_data):
        if kd == K:
            actual = f" (measured: {AUROC_data[i]:.2f})"
            break
    print(f"    K={K:>4}: AUROC = {pred:.4f}{actual}")

# ASCII graph
print(f"\n  AUROC vs K (measured * vs fitted -):")
height = 12
width = 50
grid = [['.' for _ in range(width)] for _ in range(height)]

K_fine = np.linspace(0, 55, width)
AUROC_fine = best_model[1]["func"](K_fine, *best_model[1]["params"])
AUROC_fine = np.clip(AUROC_fine, 0.5, 1.0)

for i, K in enumerate(K_fine):
    y = int((AUROC_fine[i] - 0.5) / 0.5 * (height - 1))
    y = height - 1 - max(0, min(height - 1, y))
    grid[y][i] = '-'

for i, K in enumerate(K_data):
    x = int(K / 55 * (width - 1))
    y = int((AUROC_data[i] - 0.5) / 0.5 * (height - 1))
    y = height - 1 - max(0, min(height - 1, y))
    x = max(0, min(width - 1, x))
    grid[y][x] = '*'

print(f"    1.0 ^")
for row in grid:
    print(f"        |{''.join(row)}")
print(f"    0.5 +{'─' * width}> K")
print(f"        0          10         20         30         40         50")

# ─────────────────────────────────────────
# 3. Structural Correspondence Matrix
# ─────────────────────────────────────────

print("\n" + "─" * 70)
print("3. Structural Correspondence Matrix: R Spectrum <-> Anomaly Detection")
print("─" * 70)

correspondences = [
    {
        "math": "R(n) = 1 (perfect number)",
        "engine": "T(x) = T_expected (normal)",
        "type": "Identity/Fixed point",
        "math_property": "sigma(n)/n = 2",
        "engine_property": "tension = class mean",
        "structural_match": True,
        "reason": "Both define 'ideal balance point'",
    },
    {
        "math": "R(n) != 1 (non-perfect)",
        "engine": "T(x) >> T_expected (anomaly)",
        "type": "Deviation detection",
        "math_property": "|R(n)-1| > gap",
        "engine_property": "|T-T_mean| > threshold",
        "structural_match": True,
        "reason": "Both detect 'deviation from ideal'",
    },
    {
        "math": "gap width (around R=1)",
        "engine": "decision boundary width",
        "type": "Sensitivity/Resolution",
        "math_property": f"total gap = {total_gap:.4f}",
        "engine_property": "threshold = percentile",
        "structural_match": True,
        "reason": "Wider gap = higher sensitivity",
    },
    {
        "math": "s parameter (Dirichlet)",
        "engine": "K (training epochs)",
        "type": "Scale/Resolution",
        "math_property": "F(s) ~ 1/(s-1) as s->1",
        "engine_property": f"AUROC(K) ~ {best_model[0]}",
        "structural_match": "s->1 divergence" in best_model[0] or best_model[1]["r2"] > 0.9,
        "reason": "Both 'max resolution at limit'",
    },
    {
        "math": "lens (n=6: infinite lens)",
        "engine": "split (scale=0: identical copy)",
        "type": "Focusing mechanism",
        "math_property": "M(6)=0 → 1/|M|=∞",
        "engine_property": "scale=0 → perfect copy → max AUROC",
        "structural_match": True,
        "reason": "'Perfect' = 'infinite lens' = 'perfect observation'",
    },
    {
        "math": "(s, R_0) 2D space",
        "engine": "(objective, tension_type) 2x2 matrix",
        "type": "Parameter space",
        "math_property": "2 continuous dims",
        "engine_property": "2 categorical dims",
        "structural_match": False,
        "reason": "Same dimension count but continuous/categorical difference",
    },
]

n_match = sum(1 for c in correspondences if c["structural_match"])
total_corr = len(correspondences)
consistency_score = n_match / total_corr

print(f"\n  | # | Math (R Spectrum) | Engine (Anomaly Detection) | Type | Match? |")
print(f"  |---|---|---|---|---|")
for i, c in enumerate(correspondences):
    match = "O" if c["structural_match"] else "X"
    print(f"  | {i+1} | {c['math'][:25]:25s} | {c['engine'][:25]:25s} | {c['type'][:20]:20s} | {match} |")

print(f"\n  Correspondence consistency score: {n_match}/{total_corr} = {consistency_score:.2f}")

# ─────────────────────────────────────────
# 4. Mathematical Divergence Structure Comparison
# ─────────────────────────────────────────

print("\n" + "─" * 70)
print("4. Math's 1/(s-1) Divergence vs AUROC Convergence Comparison")
print("─" * 70)

# Math: F(s) ~ C/(s-1) as s->1
# Engine: AUROC(K) -> 1 as K -> infinity
# Correspondence: s = 1 + C/K?  (s->1 <=> K->inf)

# Under transformation s = 1 + a/K:
# F(s) = C/(s-1) = C*K/a
# If AUROC is linear under this transformation, structural isomorphism

print(f"\n  Transformation: s = 1 + a/K (s->1 as K->inf)")
print(f"  Under this transformation F(s) = C/(s-1) = C*K/a ∝ K")
print(f"  → Is AUROC linear in K? = Shared divergence structure?")

# Linear fitting (K>0)
K_pos = K_data[K_data > 0]
A_pos = AUROC_data[len(K_data) - len(K_pos):]

# 1-AUROC vs 1/K (power law test)
inv_K = 1.0 / (K_pos + 0.1)
one_minus_auroc = 1.0 - A_pos

# Log-log
log_K = np.log(K_pos + 0.1)
log_1mA = np.log(one_minus_auroc + 1e-10)

# Linear regression
slope, intercept = np.polyfit(log_K, log_1mA, 1)

print(f"\n  log(1-AUROC) vs log(K) linear fitting:")
print(f"    Slope = {slope:.4f} (negative = decay)")
print(f"    Intercept = {intercept:.4f}")
print(f"    → 1-AUROC ~ K^({slope:.2f})")
print(f"    → To correspond to math's 1/(s-1), slope ≈ -1.0")
print(f"    → Actual slope = {slope:.2f} ({'similar' if abs(slope + 1) < 0.5 else 'different'})")

# ─────────────────────────────────────────
# 5. Lens Strength vs Fission Scale Correspondence
# ─────────────────────────────────────────

print("\n" + "─" * 70)
print("5. Lens Strength M(n) vs Anomaly Detection Sensitivity")
print("─" * 70)

print(f"\n  M(n) = |sigma(n)/n - 2| (deviation from perfection)")
print(f"  Lens strength = 1/M(n)")
print(f"\n  {'n':>4} | {'sigma/n':>8} | {'M(n)':>8} | {'Lens Strength':>10} | {'Type':>8}")
print(f"  {'─'*4}─┼─{'─'*8}─┼─{'─'*8}─┼─{'─'*10}─┼─{'─'*8}")

for n in [1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 28]:
    sn = sigma(n)
    mn = abs(sn/n - 2)
    lens = 1/mn if mn > 0 else float('inf')
    ntype = "perfect" if mn == 0 else ("abundant" if sn/n > 2 else "deficient")
    lens_str = f"{lens:.2f}" if lens < 1e6 else "INF"
    print(f"  {n:>4} | {sn/n:>8.4f} | {mn:>8.4f} | {lens_str:>10} | {ntype:>8}")

# ─────────────────────────────────────────
# 6. Conclusion
# ─────────────────────────────────────────

print("\n" + "=" * 70)
print("Conclusion")
print("=" * 70)

print(f"\n  Structural correspondence consistency: {consistency_score:.0%} ({n_match}/{total_corr})")
print(f"\n  Best fitting model: {best_model[0]} (R^2={best_model[1]['r2']:.4f})")
print(f"  Divergence structure slope: {slope:.2f} (predicted -1.0)")
print(f"  R=1 gap: {total_gap:.4f}")

# Overall score (0-1)
scores = [
    consistency_score,
    best_model[1]["r2"],
    1.0 if abs(slope + 1) < 0.5 else 0.5 if abs(slope + 1) < 1.0 else 0.0,
]
total_score = np.mean(scores)

print(f"\n  Overall isomorphism score: {total_score:.2f}")

if total_score > 0.7:
    verdict = "Strong structural isomorphism — Math and anomaly detection share same structure"
elif total_score > 0.5:
    verdict = "Partial isomorphism — Some correspondences confirmed, some inconsistent"
elif total_score > 0.3:
    verdict = "Weak analogy — More metaphorical than structurally isomorphic"
else:
    verdict = "Isomorphism rejected — Coincidental similarity"

print(f"  Verdict: {verdict}")

print(f"\n  ⚠️ Limitations:")
print(f"    - AUROC data fitting with only 7 points (overfitting risk)")
print(f"    - s↔K transformation not physically justified")
print(f"    - Subjectivity in structural correspondences (5/6 match may be selection bias)")
print(f"    - Qualitative assessment, not quantitative isomorphism proof")
print("=" * 70)