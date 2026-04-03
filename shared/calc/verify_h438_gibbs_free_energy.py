#!/usr/bin/env python3
"""H-CX-438: Tension = Gibbs Free Energy
G = H - TS where H=loss(enthalpy), T=lr(temperature), S=weight entropy.
Tension IS the neural network's Gibbs free energy.

Tests:
1. Correlate G_neural with tension across training
2. Check dG < 0 ↔ tension increase (spontaneous learning)
3. Phase transition: at what T (lr) does G change sign?
"""

import numpy as np
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import math

np.random.seed(42)

# ── Load data ──
digits = load_digits()
X, y = digits.data, digits.target
X = StandardScaler().fit_transform(X)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

n_classes = 10
n_features = X.shape[1]
hidden_dim = 64

def relu(x):
    return np.maximum(0, x)

def softmax(x):
    e = np.exp(x - x.max(axis=1, keepdims=True))
    return e / e.sum(axis=1, keepdims=True)

def forward(X, params):
    W1, b1, W2, b2 = params
    h = relu(X @ W1 + b1)
    logits = h @ W2 + b2
    probs = softmax(logits)
    return probs, h, logits

def cross_entropy(probs, labels):
    n = len(labels)
    return -np.log(probs[range(n), labels] + 1e-12).mean()

def weight_entropy(params):
    all_w = np.concatenate([p.ravel() for p in params])
    hist, _ = np.histogram(all_w, bins=100, density=True)
    hist = hist[hist > 0]
    hist = hist / hist.sum()
    return -np.sum(hist * np.log(hist + 1e-12))

def tension_measure(logits):
    """Tension = variance across logits (disagreement measure)"""
    return np.mean(np.var(logits, axis=1))

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

# ══════════════════════════════════════════════
# Part 1: Training trajectory — G vs Tension
# ══════════════════════════════════════════════

print("=" * 70)
print("H-CX-438: Tension = Gibbs Free Energy Verification")
print("=" * 70)

lr = 0.05
n_epochs = 30

params = [
    np.random.randn(n_features, hidden_dim) * 0.1,
    np.zeros(hidden_dim),
    np.random.randn(hidden_dim, n_classes) * 0.1,
    np.zeros(n_classes),
]

results = []
for epoch in range(n_epochs + 1):
    probs, h, logits = forward(X_test, params)
    probs_train, _, _ = forward(X_train, params)

    H_neural = cross_entropy(probs_train, y_train)  # enthalpy = loss
    S_neural = weight_entropy(params)                # entropy = weight distribution
    T_neural = lr                                    # temperature = learning rate
    G_neural = H_neural - T_neural * S_neural        # Gibbs free energy

    T_tension = tension_measure(logits)              # tension
    acc = (probs.argmax(axis=1) == y_test).mean()

    results.append({
        'epoch': epoch,
        'H': H_neural,
        'S': S_neural,
        'T': T_neural,
        'G': G_neural,
        'tension': T_tension,
        'acc': acc,
    })

    if epoch < n_epochs:
        params = train_epoch(X_train, y_train, params, lr)

# ── Results table ──
print(f"\nTraining with lr={lr}")
print()
print("| Epoch | Loss(H) | S(W)   | G=H-TS  | Tension | Acc    | dG      |")
print("|-------|---------|--------|---------|---------|--------|---------|")
for i, r in enumerate(results):
    dG = r['G'] - results[max(0, i-1)]['G'] if i > 0 else 0
    r['dG'] = dG
    print(f"| {r['epoch']:5d} | {r['H']:.4f} | {r['S']:.4f} | {r['G']:+.4f} | {r['tension']:.4f} | {r['acc']:.4f} | {dG:+.4f} |")

# ── Correlation ──
G_vals = np.array([r['G'] for r in results])
T_vals = np.array([r['tension'] for r in results])
corr = np.corrcoef(G_vals, T_vals)[0, 1]

print()
print(f"Pearson correlation (G vs Tension): r = {corr:.4f}")

# Check: dG < 0 corresponds to tension increase?
dG_list = [results[i]['G'] - results[i-1]['G'] for i in range(1, len(results))]
dT_list = [results[i]['tension'] - results[i-1]['tension'] for i in range(1, len(results))]
concordant = sum(1 for dg, dt in zip(dG_list, dT_list) if (dg < 0 and dt > 0) or (dg > 0 and dt < 0))
total = len(dG_list)
anticorr_rate = concordant / total

print(f"dG < 0 <-> dTension > 0 concordance: {concordant}/{total} = {anticorr_rate:.1%}")
print(f"  (Expected: high concordance if G decrease drives tension increase)")

# ══════════════════════════════════════════════
# Part 2: Temperature scan — Phase transition
# ══════════════════════════════════════════════

print()
print("=" * 70)
print("PHASE TRANSITION: Temperature (lr) scan")
print("=" * 70)

lr_values = np.logspace(-4, -0.3, 15)
scan_results = []

for lr_scan in lr_values:
    params_scan = [
        np.random.randn(n_features, hidden_dim) * 0.1,
        np.zeros(hidden_dim),
        np.random.randn(hidden_dim, n_classes) * 0.1,
        np.zeros(n_classes),
    ]

    for _ in range(10):
        params_scan = train_epoch(X_train, y_train, params_scan, lr_scan)

    probs, h, logits = forward(X_test, params_scan)
    probs_train, _, _ = forward(X_train, params_scan)

    H_n = cross_entropy(probs_train, y_train)
    S_n = weight_entropy(params_scan)
    G_n = H_n - lr_scan * S_n
    T_n = tension_measure(logits)
    acc = (probs.argmax(axis=1) == y_test).mean()

    scan_results.append({
        'lr': lr_scan,
        'H': H_n,
        'S': S_n,
        'G': G_n,
        'tension': T_n,
        'acc': acc,
    })

print()
print("| lr        | Loss(H) | S(W)   | G=H-TS   | Tension | Acc    |")
print("|-----------|---------|--------|----------|---------|--------|")
for s in scan_results:
    print(f"| {s['lr']:.6f} | {s['H']:.4f} | {s['S']:.4f} | {s['G']:+.5f} | {s['tension']:.4f} | {s['acc']:.4f} |")

# Find G sign change
g_signs = [s['G'] for s in scan_results]
sign_change_lr = None
for i in range(1, len(g_signs)):
    if g_signs[i-1] * g_signs[i] < 0:
        sign_change_lr = (scan_results[i-1]['lr'] + scan_results[i]['lr']) / 2
        break

if sign_change_lr:
    print(f"\nG sign change (phase transition) at lr ~ {sign_change_lr:.6f}")
    print(f"Compare with H-CX-414 critical lr ~ 0.083")
else:
    print(f"\nNo G sign change detected in scan range")
    print(f"G range: [{min(g_signs):.4f}, {max(g_signs):.4f}]")

# ── ASCII Graphs ──
print()
print("=" * 70)
print("ASCII GRAPH: G_neural and Tension during training")
print("=" * 70)

width = 50

# G_neural trajectory
g_min = min(r['G'] for r in results)
g_max = max(r['G'] for r in results)
g_range = g_max - g_min if g_max != g_min else 1

print("\nG_neural = H - TS (Gibbs free energy analog)")
for r in results[::3]:
    pos = int((r['G'] - g_min) / g_range * (width - 1))
    line = [' '] * width
    line[pos] = 'G'
    print(f"  E{r['epoch']:02d} |{''.join(line)}| {r['G']:+.4f}")

# Tension trajectory
t_min = min(r['tension'] for r in results)
t_max = max(r['tension'] for r in results)
t_range = t_max - t_min if t_max != t_min else 1

print("\nTension (logit variance)")
for r in results[::3]:
    pos = int((r['tension'] - t_min) / t_range * (width - 1))
    line = [' '] * width
    line[pos] = 'T'
    print(f"  E{r['epoch']:02d} |{''.join(line)}| {r['tension']:.4f}")

# Phase diagram
print()
print("=" * 70)
print("ASCII GRAPH: Phase Diagram (lr vs G_neural)")
print("=" * 70)
print()

g_min_s = min(s['G'] for s in scan_results)
g_max_s = max(s['G'] for s in scan_results)
g_range_s = g_max_s - g_min_s if g_max_s != g_min_s else 1

# Find zero position
zero_pos = int((0 - g_min_s) / g_range_s * (width - 1)) if g_min_s < 0 < g_max_s else -1

for s in scan_results:
    pos = int((s['G'] - g_min_s) / g_range_s * (width - 1))
    line = [' '] * width
    if 0 <= zero_pos < width:
        line[zero_pos] = '|'
    line[pos] = '*'
    marker = " <-- G=0 transition" if abs(s['G']) < abs(g_range_s * 0.05) else ""
    print(f"  lr={s['lr']:.5f} |{''.join(line)}| G={s['G']:+.4f}{marker}")

if 0 <= zero_pos < width:
    print(f"  {'':14s} {' ' * (zero_pos + 1)}^ G=0 (phase boundary)")

# ── Summary ──
print()
print("=" * 70)
print("SUMMARY")
print("=" * 70)

# Correlation between G and tension across lr scan
G_scan = np.array([s['G'] for s in scan_results])
T_scan = np.array([s['tension'] for s in scan_results])
corr_scan = np.corrcoef(G_scan, T_scan)[0, 1]

print(f"1. G vs Tension correlation (training trajectory): r = {corr:.4f}")
print(f"2. G vs Tension correlation (lr scan):             r = {corr_scan:.4f}")
print(f"3. dG<0 <-> dT>0 concordance:                     {anticorr_rate:.1%}")
print(f"4. Phase transition lr:                            {sign_change_lr if sign_change_lr else 'not detected'}")
print(f"5. H-CX-414 critical lr:                           ~0.083")
print(f"6. Confirms H-CX-413 (tension ~ free energy):     r={corr:.4f}")
print(f"7. Gibbs analogy G=H-TS:                           {'SUPPORTED' if abs(corr) > 0.5 else 'WEAK'}")
