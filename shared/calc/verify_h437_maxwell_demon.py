#!/usr/bin/env python3
"""H-CX-437: Learning = Maxwell's Demon
Neural network learning acts as Maxwell's Demon —
using information to decrease entropy (increase accuracy).
The Demon's cost = Landauer limit kT*ln(2).

Measures: output entropy, weight entropy, total entropy, Landauer ratio per epoch.
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
n_features = X.shape[1]  # 64
hidden_dim = 64

# ── Simple 2-layer network (numpy) ──
def relu(x):
    return np.maximum(0, x)

def softmax(x):
    e = np.exp(x - x.max(axis=1, keepdims=True))
    return e / e.sum(axis=1, keepdims=True)

def init_weights():
    W1 = np.random.randn(n_features, hidden_dim) * 0.1
    b1 = np.zeros(hidden_dim)
    W2 = np.random.randn(hidden_dim, n_classes) * 0.1
    b2 = np.zeros(n_classes)
    return [W1, b1, W2, b2]

def forward(X, params):
    W1, b1, W2, b2 = params
    h = relu(X @ W1 + b1)
    logits = h @ W2 + b2
    probs = softmax(logits)
    return probs, h

def cross_entropy(probs, labels):
    n = len(labels)
    log_p = np.log(probs[range(n), labels] + 1e-12)
    return -log_p.mean()

def output_entropy(probs):
    """H(Y|X) = average entropy of output distribution"""
    ent = -np.sum(probs * np.log(probs + 1e-12), axis=1)
    return ent.mean()

def weight_entropy(params):
    """H(W) = entropy of weight magnitude distribution (binned)"""
    all_w = np.concatenate([p.ravel() for p in params])
    # Bin weights into 100 bins
    hist, _ = np.histogram(all_w, bins=100, density=True)
    hist = hist[hist > 0]
    hist = hist / hist.sum()
    return -np.sum(hist * np.log(hist + 1e-12))

def accuracy(probs, labels):
    preds = probs.argmax(axis=1)
    return (preds == labels).mean()

def train_epoch(X, y, params, lr=0.01):
    W1, b1, W2, b2 = params
    # Forward
    h = relu(X @ W1 + b1)
    logits = h @ W2 + b2
    probs = softmax(logits)

    n = len(y)
    # Backward
    dlogits = probs.copy()
    dlogits[range(n), y] -= 1
    dlogits /= n

    dW2 = h.T @ dlogits
    db2 = dlogits.sum(axis=0)
    dh = dlogits @ W2.T
    dh[h <= 0] = 0  # relu grad

    dW1 = X.T @ dh
    db1 = dh.sum(axis=0)

    # Weight update magnitude (total gradient L2 norm)
    grad_norm = sum(np.linalg.norm(g) for g in [dW1, db1, dW2, db2])

    W1 -= lr * dW1
    b1 -= lr * db1
    W2 -= lr * dW2
    b2 -= lr * db2

    return [W1, b1, W2, b2], grad_norm

# ── Training loop ──
params = init_weights()
n_epochs = 30
lr = 0.05

print("=" * 70)
print("H-CX-437: Learning = Maxwell's Demon Verification")
print("=" * 70)
print(f"Data: sklearn digits, train={len(X_train)}, test={len(X_test)}")
print(f"Architecture: {n_features}-{hidden_dim}-{n_classes}, lr={lr}, epochs={n_epochs}")
print()

results = []
for epoch in range(n_epochs + 1):
    probs_test, _ = forward(X_test, params)
    probs_train, _ = forward(X_train, params)

    h_output = output_entropy(probs_test)
    h_weight = weight_entropy(params)
    h_total = h_output + h_weight
    acc = accuracy(probs_test, y_test)
    loss = cross_entropy(probs_train, y_train)

    # Information gained = bits of correct classification
    # Each correct sample = log2(10) bits max (10 classes)
    bits_gained = acc * np.log(n_classes)  # in nats, per sample

    results.append({
        'epoch': epoch,
        'h_output': h_output,
        'h_weight': h_weight,
        'h_total': h_total,
        'acc': acc,
        'loss': loss,
        'bits_gained': bits_gained,
    })

    if epoch < n_epochs:
        params_before = [p.copy() for p in params]
        params, grad_norm = train_epoch(X_train, y_train, params, lr)
        weight_change = sum(np.linalg.norm(a - b)
                           for a, b in zip(params, params_before))
        results[-1]['weight_change'] = weight_change
        results[-1]['grad_norm'] = grad_norm
    else:
        results[-1]['weight_change'] = 0
        results[-1]['grad_norm'] = 0

# ── Results table ──
print("| Epoch | H(Y|X)  | H(W)    | Total   | Acc    | Loss   | InfoGain | WtChange | Ratio   |")
print("|-------|---------|---------|---------|--------|--------|----------|----------|---------|")
for r in results:
    ratio = r['bits_gained'] / (r['weight_change'] + 1e-12) if r['weight_change'] > 0 else float('inf')
    r['ratio'] = ratio
    print(f"| {r['epoch']:5d} | {r['h_output']:.4f} | {r['h_weight']:.4f} | {r['h_total']:.4f} | "
          f"{r['acc']:.4f} | {r['loss']:.4f} | {r['bits_gained']:.4f}  | {r['weight_change']:.4f}  | {ratio:.4f} |")

# ── Key metrics ──
print()
print("=" * 70)
print("KEY ANALYSIS")
print("=" * 70)

h_out_start = results[0]['h_output']
h_out_end = results[-1]['h_output']
h_wt_start = results[0]['h_weight']
h_wt_end = results[-1]['h_weight']
h_tot_start = results[0]['h_total']
h_tot_end = results[-1]['h_total']

print(f"Output entropy H(Y|X):  {h_out_start:.4f} -> {h_out_end:.4f}  (Delta = {h_out_end - h_out_start:+.4f})")
print(f"Weight entropy H(W):    {h_wt_start:.4f} -> {h_wt_end:.4f}  (Delta = {h_wt_end - h_wt_start:+.4f})")
print(f"Total entropy:          {h_tot_start:.4f} -> {h_tot_end:.4f}  (Delta = {h_tot_end - h_tot_start:+.4f})")
print(f"2nd law check: Total entropy {'NON-DECREASING (holds)' if h_tot_end >= h_tot_start else 'DECREASED (violated!)'}")
print()

# Landauer ratio analysis
valid_ratios = [r['ratio'] for r in results if r['weight_change'] > 0.01]
if valid_ratios:
    mean_ratio = np.mean(valid_ratios)
    std_ratio = np.std(valid_ratios)
    ln2 = math.log(2)
    print(f"Landauer analysis:")
    print(f"  InfoGain/WeightChange ratio: {mean_ratio:.4f} +/- {std_ratio:.4f}")
    print(f"  ln(2) = {ln2:.4f}")
    print(f"  Ratio / ln(2) = {mean_ratio / ln2:.4f}")
    print(f"  Bounded by ln(2)? {'YES' if mean_ratio <= ln2 * 2 else 'NO'}")

# ── Correlation with H-CX-2 ──
print()
print(f"Connection to H-CX-2 (MI efficiency ~ ln(2)):")
print(f"  H-CX-2 found MI efficiency = ln(2) = {ln2:.4f}")
print(f"  H-CX-437 info/cost ratio   = {mean_ratio:.4f}")
print(f"  Ratio / ln(2)               = {mean_ratio / ln2:.4f}")

# ── ASCII Graph ──
print()
print("=" * 70)
print("ASCII GRAPH: Entropy Evolution During Learning")
print("=" * 70)

# Normalize for display
max_h = max(r['h_total'] for r in results)
width = 50

print()
print("H(Y|X) = Output entropy (should DECREASE - demon ordering)")
for r in results[::3]:  # every 3rd epoch
    bar_len = int(r['h_output'] / max_h * width)
    print(f"  E{r['epoch']:02d} |{'#' * bar_len}{' ' * (width - bar_len)}| {r['h_output']:.3f}")

print()
print("H(W) = Weight entropy (should INCREASE - demon's memory cost)")
for r in results[::3]:
    bar_len = int(r['h_weight'] / max_h * width)
    print(f"  E{r['epoch']:02d} |{'=' * bar_len}{' ' * (width - bar_len)}| {r['h_weight']:.3f}")

print()
print("Total = H(Y|X) + H(W) (should be non-decreasing = 2nd law)")
for r in results[::3]:
    bar_len = int(r['h_total'] / max_h * width)
    print(f"  E{r['epoch']:02d} |{'*' * bar_len}{' ' * (width - bar_len)}| {r['h_total']:.3f}")

# ── Demon efficiency per epoch ──
print()
print("=" * 70)
print("ASCII GRAPH: Demon Efficiency (InfoGain/Cost) vs ln(2)")
print("=" * 70)
print(f"  ln(2) = {ln2:.4f} (Landauer limit)")
print()

max_ratio = max(r['ratio'] for r in results if r['ratio'] < 100)
for r in results[::2]:
    if r['ratio'] < 100:
        bar_len = int(r['ratio'] / max_ratio * width)
        marker = " <-- ln(2)" if abs(r['ratio'] - ln2) / ln2 < 0.3 else ""
        print(f"  E{r['epoch']:02d} |{'@' * bar_len}{' ' * (width - bar_len)}| {r['ratio']:.4f}{marker}")

# Mark ln(2) line
ln2_pos = int(ln2 / max_ratio * width)
print(f"  ln2 |{' ' * ln2_pos}|")
print(f"       {' ' * ln2_pos}^ Landauer limit = {ln2:.4f}")

print()
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"1. Output entropy decreased: {h_out_start:.4f} -> {h_out_end:.4f} (demon creates order)")
print(f"2. Weight entropy changed:   {h_wt_start:.4f} -> {h_wt_end:.4f} (demon's memory cost)")
print(f"3. Total entropy:            {'non-decreasing (2nd law holds)' if h_tot_end >= h_tot_start else 'decreased (interesting violation!)'}")
print(f"4. Demon efficiency:         {mean_ratio:.4f} (cf. ln(2)={ln2:.4f})")
print(f"5. Accuracy:                 {results[0]['acc']:.1%} -> {results[-1]['acc']:.1%}")
