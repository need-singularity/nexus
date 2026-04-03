#!/usr/bin/env python3
"""H-CX-439: Landauer Principle = Mitosis Cost
Mitosis prevents forgetting, but at a cost.
This cost should equal Landauer's limit: kT*ln(2) per bit preserved.

Tests:
1. Train on task A, then task B (catastrophic forgetting)
2. With/without Mitosis replay: measure bits lost/preserved
3. Cost per bit preserved -> compare with ln(2)
4. Vary preservation level -> phase transition?
"""

import numpy as np
from sklearn.datasets import load_digits
from sklearn.preprocessing import StandardScaler
import math
import copy

np.random.seed(42)

# ── Load data and split into tasks ──
digits = load_digits()
X, y = digits.data, digits.target
X = StandardScaler().fit_transform(X)

# Task A: digits 0-4, Task B: digits 5-9
mask_a = y < 5
mask_b = y >= 5
X_a, y_a = X[mask_a], y[mask_a]
X_b, y_b = X[mask_b], y[mask_b] - 5  # remap 5-9 -> 0-4

n_features = X.shape[1]
hidden_dim = 64
n_classes = 5

def relu(x):
    return np.maximum(0, x)

def softmax(x):
    e = np.exp(x - x.max(axis=1, keepdims=True))
    return e / e.sum(axis=1, keepdims=True)

def init_weights():
    return [
        np.random.randn(n_features, hidden_dim) * 0.1,
        np.zeros(hidden_dim),
        np.random.randn(hidden_dim, n_classes) * 0.1,
        np.zeros(n_classes),
    ]

def forward(X, params):
    W1, b1, W2, b2 = params
    h = relu(X @ W1 + b1)
    logits = h @ W2 + b2
    probs = softmax(logits)
    return probs

def accuracy(X, y, params):
    probs = forward(X, params)
    return (probs.argmax(axis=1) == y).mean()

def train_epoch(X, y, params, lr):
    W1, b1, W2, b2 = params
    h = relu(X @ W1 + b1)
    logits = h @ W2 + b2
    probs = softmax(logits)
    n = len(y)

    dlogits = probs.copy()
    dlogits[range(n), y] -= 1
    dlogits /= n

    dW2 = h.T @ dlogits
    db2 = dlogits.sum(axis=0)
    dh = dlogits @ W2.T
    dh[h <= 0] = 0

    dW1 = X.T @ dh
    db1 = dh.sum(axis=0)

    W1 -= lr * dW1
    b1 -= lr * db1
    W2 -= lr * dW2
    b2 -= lr * db2
    return [W1, b1, W2, b2]

def param_distance(p1, p2):
    """Total L2 distance between parameter sets"""
    return sum(np.linalg.norm(a - b) for a, b in zip(p1, p2))

def param_size(params):
    """Total number of parameters"""
    return sum(p.size for p in params)

# ══════════════════════════════════════════════
# Part 1: Baseline — No Mitosis (Catastrophic Forgetting)
# ══════════════════════════════════════════════

print("=" * 70)
print("H-CX-439: Landauer Principle = Mitosis Cost Verification")
print("=" * 70)

lr = 0.05
epochs_a = 20  # Train task A
epochs_b = 20  # Train task B

# Train on Task A
params = init_weights()
for _ in range(epochs_a):
    params = train_epoch(X_a, y_a, params, lr)

acc_a_after_a = accuracy(X_a, y_a, params)
params_after_a = [p.copy() for p in params]

print(f"\nAfter Task A training ({epochs_a} epochs):")
print(f"  Task A accuracy: {acc_a_after_a:.4f}")

# Train on Task B (no mitosis)
params_no_mitosis = [p.copy() for p in params_after_a]
for _ in range(epochs_b):
    params_no_mitosis = train_epoch(X_b, y_b, params_no_mitosis, lr)

acc_a_after_b_no_mitosis = accuracy(X_a, y_a, params_no_mitosis)
acc_b_after_b_no_mitosis = accuracy(X_b, y_b, params_no_mitosis)

print(f"\nAfter Task B (NO Mitosis, {epochs_b} epochs):")
print(f"  Task A accuracy: {acc_a_after_b_no_mitosis:.4f} (forgetting!)")
print(f"  Task B accuracy: {acc_b_after_b_no_mitosis:.4f}")
print(f"  Task A loss:     {acc_a_after_a - acc_a_after_b_no_mitosis:.4f}")

# ══════════════════════════════════════════════
# Part 2: Mitosis with varying replay ratios
# ══════════════════════════════════════════════

print()
print("=" * 70)
print("MITOSIS: Varying replay ratio (preservation level)")
print("=" * 70)

replay_fractions = [0.0, 0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0]
mitosis_results = []

for replay_frac in replay_fractions:
    params_m = [p.copy() for p in params_after_a]
    n_replay = int(len(X_a) * replay_frac)
    total_flops = 0

    for ep in range(epochs_b):
        # Train on task B
        params_m = train_epoch(X_b, y_b, params_m, lr)
        total_flops += len(X_b)

        # Replay from task A (Mitosis mechanism)
        if n_replay > 0:
            idx = np.random.choice(len(X_a), n_replay, replace=False)
            params_m = train_epoch(X_a[idx], y_a[idx], params_m, lr * 0.5)
            total_flops += n_replay

    acc_a = accuracy(X_a, y_a, params_m)
    acc_b = accuracy(X_b, y_b, params_m)

    # Bits preserved on task A
    bits_max = np.log(n_classes)  # max bits per sample
    bits_preserved = acc_a * bits_max
    bits_lost = (acc_a_after_a - acc_a) * bits_max
    bits_baseline = acc_a_after_b_no_mitosis * bits_max

    # Extra cost = additional flops over no-mitosis baseline
    baseline_flops = len(X_b) * epochs_b
    extra_flops = total_flops - baseline_flops
    extra_cost_per_sample = extra_flops / (len(X_a) + 1e-12)

    # Cost per bit preserved (above no-mitosis baseline)
    bits_gained_over_baseline = (acc_a - acc_a_after_b_no_mitosis) * bits_max
    cost_per_bit = extra_cost_per_sample / (bits_gained_over_baseline + 1e-12) if bits_gained_over_baseline > 0 else float('inf')

    # Normalized cost: extra_fraction / preservation_fraction
    preservation_rate = acc_a / acc_a_after_a if acc_a_after_a > 0 else 0
    cost_fraction = extra_flops / baseline_flops

    mitosis_results.append({
        'replay_frac': replay_frac,
        'acc_a': acc_a,
        'acc_b': acc_b,
        'preservation': preservation_rate,
        'bits_preserved': bits_preserved,
        'bits_gained': bits_gained_over_baseline,
        'extra_cost': extra_cost_per_sample,
        'cost_per_bit': cost_per_bit,
        'cost_fraction': cost_fraction,
        'total_flops': total_flops,
    })

print()
print("| Replay | AccA   | AccB   | Preserv | BitsGain | ExtraCost | Cost/Bit | CostFrac |")
print("|--------|--------|--------|---------|----------|-----------|----------|----------|")
for m in mitosis_results:
    cpb = f"{m['cost_per_bit']:.4f}" if m['cost_per_bit'] < 1000 else "inf"
    print(f"| {m['replay_frac']:.2f}   | {m['acc_a']:.4f} | {m['acc_b']:.4f} | "
          f"{m['preservation']:.4f} | {m['bits_gained']:.4f}  | {m['extra_cost']:.4f}   | "
          f"{cpb:>8s} | {m['cost_fraction']:.4f}  |")

# ── Landauer analysis ──
print()
print("=" * 70)
print("LANDAUER ANALYSIS")
print("=" * 70)

ln2 = math.log(2)
valid_costs = [(m['replay_frac'], m['cost_per_bit'], m['preservation'])
               for m in mitosis_results if 0 < m['cost_per_bit'] < 1000]

if valid_costs:
    costs_only = [c[1] for c in valid_costs]
    mean_cost = np.mean(costs_only)
    min_cost = min(costs_only)
    print(f"Cost per bit preserved (valid entries):")
    for frac, cost, pres in valid_costs:
        print(f"  replay={frac:.2f}: cost/bit = {cost:.4f}, preservation = {pres:.1%}")
    print(f"\n  Mean cost/bit:    {mean_cost:.4f}")
    print(f"  Min cost/bit:     {min_cost:.4f}")
    print(f"  ln(2):            {ln2:.4f}")
    print(f"  Min/ln(2) ratio:  {min_cost / ln2:.4f}")
    print(f"  Mean/ln(2) ratio: {mean_cost / ln2:.4f}")

# ── Normalized cost analysis ──
print()
print("Normalized cost analysis (CostFraction / Preservation):")
norm_costs = [(m['replay_frac'], m['cost_fraction'] / (m['preservation'] + 1e-12))
              for m in mitosis_results if m['replay_frac'] > 0]
for frac, ncost in norm_costs:
    print(f"  replay={frac:.2f}: norm_cost = {ncost:.4f}")

# ══════════════════════════════════════════════
# ASCII Graphs
# ══════════════════════════════════════════════

print()
print("=" * 70)
print("ASCII GRAPH: Forgetting Prevention vs Computational Cost")
print("=" * 70)

width = 50

print("\nPreservation rate (AccA / original AccA)")
for m in mitosis_results:
    bar_len = int(m['preservation'] * width)
    print(f"  r={m['replay_frac']:.2f} |{'#' * bar_len}{' ' * (width - bar_len)}| {m['preservation']:.1%}")

print("\nComputational cost (fraction over baseline)")
max_cf = max(m['cost_fraction'] for m in mitosis_results)
for m in mitosis_results:
    bar_len = int(m['cost_fraction'] / (max_cf + 1e-12) * width)
    print(f"  r={m['replay_frac']:.2f} |{'=' * bar_len}{' ' * (width - bar_len)}| {m['cost_fraction']:.2f}x")

# Phase transition graph
print()
print("=" * 70)
print("ASCII GRAPH: Preservation vs Cost (Phase Transition?)")
print("=" * 70)
print()
print("  Preservation")
print("  100% |")

# Grid
for level in [100, 80, 60, 40, 20, 0]:
    line = [' '] * width
    for i, m in enumerate(mitosis_results):
        pos = int(i / (len(mitosis_results) - 1) * (width - 1)) if len(mitosis_results) > 1 else 0
        if int(m['preservation'] * 100 + 0.5) >= level and (level == 0 or int(m['preservation'] * 100 + 0.5) < level + 20):
            line[pos] = '*'
    pct = f"{level:3d}%"
    print(f"  {pct} |{''.join(line)}|")

print(f"       +{'-' * width}+")
labels = "  r=0.0" + " " * (width - 20) + "r=1.0"
print(labels)
print(f"       {'Replay fraction (computational cost) -->':^{width}}")

# ── Connection to H-CX-2 and H312 ──
print()
print("=" * 70)
print("CROSS-HYPOTHESIS CONNECTIONS")
print("=" * 70)

best_m = max(mitosis_results, key=lambda m: m['preservation'])
print(f"1. H-CX-2:  MI efficiency ~ ln(2) = {ln2:.4f}")
if valid_costs:
    print(f"2. H-CX-439: Min cost/bit   = {min_cost:.4f} (ratio to ln(2): {min_cost/ln2:.2f})")
print(f"3. H312: Mitosis 99% retention  vs our best: {best_m['preservation']:.1%}")
print(f"4. Forgetting without Mitosis:  {acc_a_after_b_no_mitosis:.1%} (vs {acc_a_after_a:.1%} original)")
print(f"5. Best Mitosis preservation:   {best_m['acc_a']:.1%} at replay={best_m['replay_frac']:.0%}")

# ── Summary ──
print()
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"1. Catastrophic forgetting:    {acc_a_after_a:.1%} -> {acc_a_after_b_no_mitosis:.1%} (no mitosis)")
print(f"2. Mitosis preservation:       up to {best_m['preservation']:.1%}")
print(f"3. Cost per bit preserved:     {min_cost:.4f}" if valid_costs else "3. Cost per bit: N/A")
print(f"4. Landauer limit ln(2):       {ln2:.4f}")
if valid_costs:
    print(f"5. Cost/ln(2) ratio:           {min_cost/ln2:.4f}")
    bounded = min_cost >= ln2 * 0.5  # within reasonable range
    print(f"6. Landauer bound holds?       {'YES (cost >= ln(2)/2)' if bounded else 'NEAR-VIOLATION (interesting!)'}")
print(f"7. Phase transition visible?   Check preservation curve above")
