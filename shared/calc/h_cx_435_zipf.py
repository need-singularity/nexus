#!/usr/bin/env python3
"""H-CX-435: Zipf's Law Exponent and Golden Zone
Verify whether Zipf's law and information-theoretic properties relate to Golden Zone constants.
"""
import numpy as np
from scipy import stats

print("=" * 70)
print("H-CX-435: Zipf's Law Exponent and Golden Zone")
print("=" * 70)

# Golden Zone constants
GZ_upper = 0.5          # 1/2
GZ_center = 1/np.e      # 1/e ≈ 0.3679
GZ_lower = 0.5 - np.log(4/3)  # ≈ 0.2123
GZ_width = np.log(4/3)  # ≈ 0.2877

print(f"\n--- Golden Zone Constants ---")
print(f"  Upper  = 1/2       = {GZ_upper:.4f}")
print(f"  Center = 1/e       = {GZ_center:.4f}")
print(f"  Lower  = 1/2-ln(4/3) = {GZ_lower:.4f}")
print(f"  Width  = ln(4/3)   = {GZ_width:.4f}")

# ============================================================
# 1. Zipf's Law: entropy as function of exponent α
# ============================================================
print(f"\n{'='*70}")
print("1. ENTROPY OF ZIPF DISTRIBUTION vs EXPONENT α")
print("="*70)

def zipf_entropy(alpha, N=10000):
    """Compute entropy of Zipf distribution with exponent alpha over N ranks."""
    ranks = np.arange(1, N+1, dtype=np.float64)
    probs = 1.0 / ranks**alpha
    probs /= probs.sum()
    # Shannon entropy in nats
    H = -np.sum(probs * np.log(probs + 1e-300))
    H_max = np.log(N)
    return H, H_max, H / H_max

N = 10000
alphas = np.arange(0.5, 2.01, 0.05)
results = []
for a in alphas:
    H, H_max, ratio = zipf_entropy(a, N)
    results.append((a, H, H_max, ratio))

print(f"\n  {'α':>5s} | {'H (nats)':>10s} | {'H/H_max':>8s} | Bar")
print(f"  -----+------------+----------+{'─'*35}")
for a, H, Hmax, r in results:
    bar_len = int(r * 30)
    bar = "█" * bar_len
    marker = ""
    if abs(r - GZ_center) < 0.02:
        marker = " ← 1/e!"
    elif abs(r - GZ_upper) < 0.02:
        marker = " ← 1/2!"
    elif abs(r - GZ_lower) < 0.02:
        marker = " ← GZ_lower!"
    print(f"  {a:5.2f} | {H:10.4f} | {r:8.4f} | {bar}{marker}")

# Find α where H/H_max = 1/e
print(f"\n--- Key Points ---")
for target_name, target_val in [("1/e", GZ_center), ("1/2", GZ_upper), ("GZ_lower", GZ_lower)]:
    # Interpolate
    ratios = np.array([r[3] for r in results])
    alpha_vals = np.array([r[0] for r in results])
    # Find crossing
    diffs = ratios - target_val
    crossings = []
    for i in range(len(diffs)-1):
        if diffs[i] * diffs[i+1] <= 0:
            # Linear interpolation
            a_cross = alpha_vals[i] + (alpha_vals[i+1] - alpha_vals[i]) * abs(diffs[i]) / (abs(diffs[i]) + abs(diffs[i+1]))
            crossings.append(a_cross)
    if crossings:
        print(f"  H/H_max = {target_name} ({target_val:.4f}) at α ≈ {crossings[0]:.3f}")
    else:
        print(f"  H/H_max = {target_name} ({target_val:.4f}): no crossing in range")

# ============================================================
# 2. Optimal communication: α=1 analysis
# ============================================================
print(f"\n{'='*70}")
print("2. ZIPF α=1 (NATURAL LANGUAGE) INFORMATION ANALYSIS")
print("="*70)

H_at_1, Hmax_at_1, ratio_at_1 = zipf_entropy(1.0, N)
print(f"  At α=1.0 (Zipf's law, natural language):")
print(f"    H = {H_at_1:.4f} nats")
print(f"    H_max = {Hmax_at_1:.4f} nats (= ln({N}))")
print(f"    H/H_max = {ratio_at_1:.4f}")
print(f"    1 - H/H_max = {1-ratio_at_1:.4f}  (redundancy)")

# Check: is redundancy ≈ Golden Zone width?
print(f"\n  Comparison with Golden Zone:")
print(f"    H/H_max at α=1     = {ratio_at_1:.4f}")
print(f"    1/2                 = {GZ_upper:.4f}")
print(f"    1/e                 = {GZ_center:.4f}")
print(f"    Redundancy (1-H/Hmax) = {1-ratio_at_1:.4f}")
print(f"    ln(4/3) (GZ width) = {GZ_width:.4f}")
print(f"    1-1/e               = {1-GZ_center:.4f}")

# Key insight: for Zipf α=1 with large N, H ≈ ln(N) - 1 + γ (Euler-Mascheroni)
gamma_EM = 0.5772156649
H_approx = np.log(N) - 1 + gamma_EM
print(f"\n  Analytical approximation for α=1:")
print(f"    H ≈ ln(N) - 1 + γ = {H_approx:.4f}")
print(f"    Actual H           = {H_at_1:.4f}")
print(f"    H/H_max ≈ 1 - (1-γ)/ln(N) = {1 - (1-gamma_EM)/np.log(N):.4f}")
print(f"    As N→∞, H/H_max → 1 (redundancy vanishes)")
print(f"    → H/H_max depends on vocabulary size N, not a constant!")

# ============================================================
# 3. Fixed vocabulary analysis: N where H/H_max = 1/e
# ============================================================
print(f"\n{'='*70}")
print("3. VOCABULARY SIZE N WHERE H/H_max = 1/e at α=1")
print("="*70)

# H/Hmax ≈ 1 - (1-γ)/ln(N) = 1/e
# (1-γ)/ln(N) = 1 - 1/e
# ln(N) = (1-γ)/(1-1/e)
# N = exp((1-γ)/(1-1/e))
N_golden = np.exp((1 - gamma_EM) / (1 - 1/np.e))
print(f"  Solving H/H_max = 1/e for N:")
print(f"    N = exp((1-γ)/(1-1/e))")
print(f"    N = exp({1-gamma_EM:.4f}/{1-1/np.e:.4f})")
print(f"    N ≈ {N_golden:.1f}")
print(f"    → N ≈ {int(round(N_golden))} words")
print(f"    (Very small vocabulary — not linguistically meaningful)")

# Check with actual computation
for N_test in [2, 3, 5, 7, 10, 20, 50, 100, 500, 1000, 10000]:
    h, hm, r = zipf_entropy(1.0, N_test)
    print(f"    N={N_test:6d}: H/H_max = {r:.4f}", end="")
    if abs(r - GZ_center) < 0.03:
        print(" ← ~1/e!", end="")
    print()

# ============================================================
# 4. Heap's Law: β ≈ 0.5
# ============================================================
print(f"\n{'='*70}")
print("4. HEAP'S LAW: V = K × N^β")
print("="*70)

# Heap's law empirical: β typically 0.4-0.6, often cited as ~0.5
beta_heap_empirical = 0.5
print(f"  Empirical β ≈ {beta_heap_empirical}")
print(f"  Golden Zone upper = 1/2 = {GZ_upper}")
print(f"  → β = 1/2 = GZ_upper? Numerically YES")
print(f"")
print(f"  But: β=0.5 is the SQUARE ROOT growth rate.")
print(f"  V ~ sqrt(N) is a very common mathematical phenomenon.")
print(f"  This could be coincidence rather than deep connection.")

# Theoretical relationship: for Zipf α=1, Heap's β = 1/α = 1
# But empirically β < 1 due to finite-size effects
# More precisely: β ≈ 1/α for α > 1
print(f"\n  Theoretical: β = 1/α for α>1")
print(f"  For α=1: β should be 1 (linear) but empirically ~0.5")
print(f"  The discrepancy is due to finite corpus effects and")
print(f"  the fact that real text deviates from pure Zipf.")

# ============================================================
# 5. Synthetic corpus analysis
# ============================================================
print(f"\n{'='*70}")
print("5. SYNTHETIC ZIPF CORPUS ANALYSIS")
print("="*70)

np.random.seed(42)

vocab_size = 5000
corpus_size = 100000

# Generate synthetic Zipf corpus
ranks = np.arange(1, vocab_size + 1)
probs = 1.0 / ranks  # α=1
probs /= probs.sum()

corpus = np.random.choice(vocab_size, size=corpus_size, p=probs)

# Measure Heap's law: vocabulary growth
sample_sizes = [100, 500, 1000, 5000, 10000, 50000, 100000]
vocabs = []
for ss in sample_sizes:
    v = len(set(corpus[:ss]))
    vocabs.append(v)

print(f"  Vocabulary growth (Heap's law):")
print(f"  {'N':>8s} | {'V':>6s} | {'V/N':>6s} | {'V/sqrt(N)':>10s}")
print(f"  --------+--------+--------+-----------")
for ss, v in zip(sample_sizes, vocabs):
    print(f"  {ss:8d} | {v:6d} | {v/ss:6.3f} | {v/np.sqrt(ss):10.2f}")

# Fit Heap's law
log_n = np.log(np.array(sample_sizes))
log_v = np.log(np.array(vocabs))
beta_fit, log_k, r_val, p_val, se = stats.linregress(log_n, log_v)
print(f"\n  Fitted Heap's law: V = {np.exp(log_k):.1f} × N^{beta_fit:.4f}")
print(f"  R² = {r_val**2:.6f}")
print(f"  β = {beta_fit:.4f}")
print(f"  |β - 1/2| = {abs(beta_fit - 0.5):.4f}")

# ============================================================
# 6. Information efficiency across α
# ============================================================
print(f"\n{'='*70}")
print("6. INFORMATION EFFICIENCY: MUTUAL INFORMATION PROXY")
print("="*70)

# For communication: efficiency = how much meaning per symbol
# Proxy: for Zipf distribution, compute the "effective alphabet size"
# H_eff = exp(H) / N  (fraction of alphabet effectively used)

print(f"\n  {'α':>5s} | {'H(nats)':>9s} | {'exp(H)':>8s} | {'exp(H)/N':>10s} | Efficiency bar")
print(f"  -----+-----------+----------+------------+{'─'*30}")
for a in [0.5, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.5, 2.0]:
    H, _, r = zipf_entropy(a, 1000)
    eff = np.exp(H) / 1000
    bar = "█" * int(eff * 30)
    marker = ""
    if abs(eff - GZ_center) < 0.03:
        marker = " ← ~1/e"
    if abs(eff - GZ_upper) < 0.03:
        marker = " ← ~1/2"
    print(f"  {a:5.2f} | {H:9.4f} | {np.exp(H):8.1f} | {eff:10.4f} | {bar}{marker}")

# ============================================================
# 7. ASCII Graph: H/H_max vs α with Golden Zone overlay
# ============================================================
print(f"\n{'='*70}")
print("7. ASCII GRAPH: H/H_max vs α")
print("="*70)

# Fine-grained computation
alphas_fine = np.linspace(0.5, 2.0, 31)
ratios_fine = []
for a in alphas_fine:
    _, _, r = zipf_entropy(a, 10000)
    ratios_fine.append(r)

# ASCII plot
height = 20
width = 60
y_min, y_max = 0.0, 1.0

print(f"\n  H/H_max")
for row in range(height, -1, -1):
    y = y_min + (y_max - y_min) * row / height
    line = f"  {y:5.2f} |"
    for col in range(len(alphas_fine)):
        r = ratios_fine[col]
        r_row = int((r - y_min) / (y_max - y_min) * height)
        if r_row == row:
            line += "*"
        elif abs(y - GZ_center) < (y_max - y_min) / height / 2:
            line += "-"  # 1/e line
        elif abs(y - GZ_upper) < (y_max - y_min) / height / 2:
            line += "="  # 1/2 line
        elif abs(y - GZ_lower) < (y_max - y_min) / height / 2:
            line += "."  # GZ lower line
        else:
            line += " "
    print(line)

print(f"        +{'─' * len(alphas_fine)}")
print(f"         α: 0.5{'─'*10}1.0{'─'*10}1.5{'─'*10}2.0")
print(f"  Legend: * = H/H_max, = = 1/2, - = 1/e, . = GZ_lower")

# ============================================================
# 8. Final assessment
# ============================================================
print(f"\n{'='*70}")
print("FINAL ASSESSMENT")
print("="*70)

print(f"""
  Key findings:
  1. H/H_max at α=1 depends on N (vocabulary size), NOT a constant
     → No fixed relationship between Zipf α=1 and Golden Zone

  2. For finite N=10000: H/H_max ≈ {ratio_at_1:.4f} (close to 1, not 1/e or 1/2)
     → Natural language is HIGH entropy, not in Golden Zone

  3. Heap's β ≈ 0.5 = 1/2 = GZ_upper: numerically matches
     → But β=0.5 (square root) is ubiquitous in math, likely coincidence

  4. The effective alphabet fraction exp(H)/N shows no special value at α=1

  5. H/H_max = 1/e occurs at very high α (>1.5) where distribution is
     extremely concentrated — NOT natural language territory

  Assessment: Weak structural connection at best.
  Heap's β≈1/2 is interesting but likely coincidental.
  Zipf α=1 does NOT place natural language in the Golden Zone.

  Grade: ⚪ (arithmetically correct observations, but no structural connection)
  p-value for Heap β=1/2: not meaningful (√N growth is generic)
""")
