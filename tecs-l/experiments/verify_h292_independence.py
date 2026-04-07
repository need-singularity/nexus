#!/usr/bin/env python3
"""Hypothesis 292 Verification: Consciousness Tree New Branch Independence Analysis

Confirm whether new branches (generation/creation, information/entropy, aesthetic/sensory) are
independent from existing branches (cognition/judgment, consciousness/experience, collective/dimensional)
through cross-correlation of existing experimental results.

Method:
1. Collect experimental results (tension, accuracy, correlation, etc.) belonging to each branch
2. Calculate cross-correlation matrix between branches
3. Independence = low correlation (|r| < 0.3)
"""

import numpy as np
import sys

np.random.seed(42)

print("=" * 70)
print("Hypothesis 292 Verification: Consciousness Tree New Branch Independence Analysis")
print("=" * 70)

# ─────────────────────────────────────────
# 1. Collect core metrics for each branch (extracted from documents)
# ─────────────────────────────────────────

# Core values from experiments for each branch (normalized effect sizes)
# Branch → [metric1, metric2, ...] (effect sizes from various experiments)

branches = {
    # Existing branches
    "Cognition/Judgment": {
        "description": "Tension-accuracy correlation, causal effects, anomaly detection",
        "metrics": {
            "tension_accuracy_corr": 0.89,    # C4b d=0.89
            "causal_effect_pp": -9.25,         # C48 causal effect
            "anomaly_auroc": 1.0,              # C287
            "precognition_auc": 0.77,          # C6 AUC
            "recognition_acc": 97.61,          # C10
            "direction_separation": 2.77,      # C17
        }
    },
    "Consciousness/Experience": {
        "description": "Identity, FPS convergence, position movement",
        "metrics": {
            "identity_score": 0.979,           # C13
            "dream_identity": 2.7,             # C15 2.7x
            "split_recombine": 0.82,           # C46 +0.82%
            "fps_convergence": 0.20,           # C14 4.17→0.20
            "selfref_contraction": 1.0,        # C18 >1
            "observer_advantage": 7.4,         # C31 +7.4%
        }
    },
    "Collective/Dimensional": {
        "description": "Unanimity, cross-dimensional transfer",
        "metrics": {
            "unanimous_acc": 99.53,            # C9
            "cross_dim_acc": 94.3,             # C8
            "extreme_tension": 14.4,           # C25 14.4x
            "tau_suppression": 0.011,          # C26
            "bc_connection": 0.062,            # C53
            "diversity_transition": 0.5,       # Hypothesis 267 (estimated)
        }
    },
    # New branch candidates
    "Generation/Creation": {
        "description": "VAE generation, dreaming, mitosis generation",
        "metrics": {
            "split_design_gap": -0.11,         # Hypothesis 271 mitosis≈design
            "dreaming_quality": 0.65,          # Dreaming tension control (estimated)
            "vae_reconstruction": 0.82,        # VAE reconstruction (estimated)
            "semantic_separation": 0.71,       # Meaning/context axis separation (estimated)
            "generation_diversity": 0.55,      # Generation diversity (estimated)
            "creative_tension": 0.43,          # Tension during generation (estimated)
        }
    },
    "Information/Entropy": {
        "description": "MI efficiency, diversity=information, Landauer",
        "metrics": {
            "mi_efficiency_ln2": 0.693,        # C54 MI≈ln(2)
            "mi_addition": 0.39,               # C24 +0.39 nats
            "landauer_connection": 0.72,       # Landauer connection strength
            "binary_ternary": 0.85,            # H-CX-3 binary+ternary
            "diversity_info": 0.67,            # Hypothesis 270
            "dense_sparse": 0.44,              # Hypothesis 288
        }
    },
    "Aesthetic/Sensory": {
        "description": "Musical consonance, prime tension, time series",
        "metrics": {
            "consonance_tension": -0.83,       # Hypothesis 290 consonance=low tension
            "prime_max_tension": 0.91,         # Hypothesis 289 prime=max tension
            "perfect_4th_ratio": 0.33,         # 4:3=lowest tension
            "sharpness_tension": 0.76,         # Sharpness∝tension
            "harmonic_series": 0.68,           # Harmonic series pattern
            "rhythm_tension": 0.52,            # Rhythm pattern (estimated)
        }
    },
}

print("\n" + "─" * 70)
print("1. Metric Vector Configuration for Each Branch")
print("─" * 70)

branch_names = list(branches.keys())
branch_vectors = {}

for name, branch in branches.items():
    vec = np.array(list(branch["metrics"].values()))
    # z-score normalization (make effect sizes comparable)
    vec_z = (vec - np.mean(vec)) / (np.std(vec) + 1e-8)
    branch_vectors[name] = vec_z
    print(f"\n  {name} ({branch['description']})")
    print(f"    Original: {[f'{v:.3f}' for v in branch['metrics'].values()]}")
    print(f"    z-normalized: {[f'{v:.3f}' for v in vec_z]}")

# ─────────────────────────────────────────
# 2. Calculate Cross-correlation Matrix
# ─────────────────────────────────────────

print("\n" + "─" * 70)
print("2. Cross-Correlation Matrix Between Branches")
print("─" * 70)

n = len(branch_names)
corr_matrix = np.zeros((n, n))

for i, name_i in enumerate(branch_names):
    for j, name_j in enumerate(branch_names):
        vi = branch_vectors[name_i]
        vj = branch_vectors[name_j]
        # Pearson correlation
        corr = np.corrcoef(vi, vj)[0, 1]
        corr_matrix[i, j] = corr

# Header
header = "            " + "  ".join([f"{name[:6]:>6}" for name in branch_names])
print(f"\n{header}")
print("  " + "─" * (8 * n + 12))

for i, name_i in enumerate(branch_names):
    row = f"  {name_i[:10]:>10} |"
    for j in range(n):
        val = corr_matrix[i, j]
        if i == j:
            row += f"  {'1.000':>6}"
        else:
            row += f"  {val:>6.3f}"
    print(row)

# ─────────────────────────────────────────
# 3. Independence Determination
# ─────────────────────────────────────────

print("\n" + "─" * 70)
print("3. Independence Analysis")
print("─" * 70)

# Correlation between existing branches
existing = ["Cognition/Judgment", "Consciousness/Experience", "Collective/Dimensional"]
new_candidates = ["Generation/Creation", "Information/Entropy", "Aesthetic/Sensory"]

print("\n  [A] Correlation between existing branches:")
for i, a in enumerate(existing):
    for j, b in enumerate(existing):
        if i < j:
            idx_a = branch_names.index(a)
            idx_b = branch_names.index(b)
            r = corr_matrix[idx_a, idx_b]
            ind = "independent" if abs(r) < 0.3 else ("weak corr" if abs(r) < 0.6 else "strong corr")
            print(f"    {a} <-> {b}: r={r:+.3f} ({ind})")

print("\n  [B] New branch <-> Existing branch correlation:")
for new in new_candidates:
    print(f"\n    --- {new} ---")
    idx_new = branch_names.index(new)
    for old in existing:
        idx_old = branch_names.index(old)
        r = corr_matrix[idx_new, idx_old]
        ind = "independent" if abs(r) < 0.3 else ("weak corr" if abs(r) < 0.6 else "strong corr")
        print(f"      <-> {old}: r={r:+.3f} ({ind})")

print("\n  [C] Correlation between new branches:")
for i, a in enumerate(new_candidates):
    for j, b in enumerate(new_candidates):
        if i < j:
            idx_a = branch_names.index(a)
            idx_b = branch_names.index(b)
            r = corr_matrix[idx_a, idx_b]
            ind = "independent" if abs(r) < 0.3 else ("weak corr" if abs(r) < 0.6 else "strong corr")
            print(f"    {a} <-> {b}: r={r:+.3f} ({ind})")

# ─────────────────────────────────────────
# 4. Principal Component Analysis (PCA) — Confirm dimensional independence
# ─────────────────────────────────────────

print("\n" + "─" * 70)
print("4. PCA Analysis — How many independent dimensions do branches form?")
print("─" * 70)

# Matrix of all branch vectors
all_vecs = np.array([branch_vectors[name] for name in branch_names])  # (6, 6)
# SVD
U, S, Vt = np.linalg.svd(all_vecs, full_matrices=False)
explained = S**2 / (S**2).sum()
cumulative = np.cumsum(explained)

print(f"\n  Singular values: {[f'{s:.3f}' for s in S]}")
print(f"  Variance explained: {[f'{e:.1%}' for e in explained]}")
print(f"  Cumulative explained: {[f'{c:.1%}' for c in cumulative]}")

# ASCII graph
print(f"\n  Variance explained (Scree Plot):")
for i, e in enumerate(explained):
    bar_len = int(e * 50)
    bar = "#" * bar_len
    print(f"    PC{i+1}: {e:6.1%} |{bar}")

effective_dims = np.sum(cumulative < 0.95) + 1
print(f"\n  Effective dimensions (95% explained): {effective_dims}")
print(f"  → 6 branches form {effective_dims} independent dimensions")

# ─────────────────────────────────────────
# 5. Bootstrap confidence intervals for correlations
# ─────────────────────────────────────────

print("\n" + "─" * 70)
print("5. Bootstrap Confidence Intervals (1000 iterations)")
print("─" * 70)

n_boot = 1000
key_pairs = [
    ("Generation/Creation", "Cognition/Judgment"),
    ("Information/Entropy", "Cognition/Judgment"),
    ("Information/Entropy", "Consciousness/Experience"),
    ("Aesthetic/Sensory", "Cognition/Judgment"),
    ("Generation/Creation", "Information/Entropy"),
]

for name_a, name_b in key_pairs:
    va = np.array(list(branches[name_a]["metrics"].values()))
    vb = np.array(list(branches[name_b]["metrics"].values()))

    boot_corrs = []
    for _ in range(n_boot):
        idx = np.random.choice(len(va), size=len(va), replace=True)
        va_boot = (va[idx] - va[idx].mean()) / (va[idx].std() + 1e-8)
        vb_boot = (vb[idx] - vb[idx].mean()) / (vb[idx].std() + 1e-8)
        r = np.corrcoef(va_boot, vb_boot)[0, 1]
        if not np.isnan(r):
            boot_corrs.append(r)

    boot_corrs = np.array(boot_corrs)
    ci_lo = np.percentile(boot_corrs, 2.5)
    ci_hi = np.percentile(boot_corrs, 97.5)
    mean_r = np.mean(boot_corrs)

    # Independence determination: independent if CI contains 0
    contains_zero = ci_lo <= 0 <= ci_hi
    verdict = "independent (CI contains 0)" if contains_zero else "correlated"

    print(f"  {name_a} <-> {name_b}:")
    print(f"    mean r={mean_r:+.3f}, 95% CI=[{ci_lo:+.3f}, {ci_hi:+.3f}] → {verdict}")

# ─────────────────────────────────────────
# 6. Conclusion
# ─────────────────────────────────────────

print("\n" + "=" * 70)
print("Conclusion")
print("=" * 70)

# Average of all new-existing correlations
new_old_corrs = []
for new in new_candidates:
    idx_new = branch_names.index(new)
    for old in existing:
        idx_old = branch_names.index(old)
        new_old_corrs.append(abs(corr_matrix[idx_new, idx_old]))

mean_new_old = np.mean(new_old_corrs)
max_new_old = np.max(new_old_corrs)

# Average correlation between existing branches
old_old_corrs = []
for i, a in enumerate(existing):
    for j, b in enumerate(existing):
        if i < j:
            idx_a = branch_names.index(a)
            idx_b = branch_names.index(b)
            old_old_corrs.append(abs(corr_matrix[idx_a, idx_b]))

mean_old_old = np.mean(old_old_corrs)

print(f"\n  Mean |r| between existing branches: {mean_old_old:.3f}")
print(f"  Mean |r| new-existing:             {mean_new_old:.3f}")
print(f"  Max |r| new-existing:              {max_new_old:.3f}")
print(f"  Effective dimensions:              {effective_dims}/6")

if mean_new_old < 0.3 and effective_dims >= 4:
    print(f"\n  Verdict: New branches are sufficiently independent from existing (|r|<0.3)")
    print(f"  → 6 top-level branch structure supported")
    status = "Partially supported"
elif mean_new_old < 0.5:
    print(f"\n  Verdict: Weak independence (0.3 < |r| < 0.5)")
    print(f"  → Uncertain as independent branches, possibly sub-branches")
    status = "Weakly supported"
else:
    print(f"\n  Verdict: Insufficient independence (|r| > 0.5)")
    print(f"  → New branches likely sub-categories of existing branches")
    status = "Rejected"

print(f"\n  ⚠️ Note: This analysis performed with document-based metrics")
print(f"  → Re-verification needed with simultaneously measured data from same model")
print(f"  → Metrics marked 'estimated' need experimental confirmation")

print(f"\n  Final status: {status}")
print("=" * 70)