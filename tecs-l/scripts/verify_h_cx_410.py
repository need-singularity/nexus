#!/usr/bin/env python3
"""
H-CX-410: PH barcode = Learning Memory Fingerprint
Test: Compare PH barcodes before/after catastrophic forgetting vs Mitosis protection
"""
import numpy as np
from sklearn.datasets import fetch_openml
from sklearn.preprocessing import OneHotEncoder
import warnings
warnings.filterwarnings('ignore')

np.random.seed(42)

# --- Minimal neural network in numpy ---
def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))

def softmax(x):
    e = np.exp(x - x.max(axis=1, keepdims=True))
    return e / e.sum(axis=1, keepdims=True)

def relu(x):
    return np.maximum(0, x)

class SimpleNN:
    def __init__(self, input_dim, hidden_dim, output_dim):
        scale1 = np.sqrt(2.0 / input_dim)
        scale2 = np.sqrt(2.0 / hidden_dim)
        self.W1 = np.random.randn(input_dim, hidden_dim) * scale1
        self.b1 = np.zeros(hidden_dim)
        self.W2 = np.random.randn(hidden_dim, output_dim) * scale2
        self.b2 = np.zeros(output_dim)

    def forward(self, X):
        self.z1 = X @ self.W1 + self.b1
        self.a1 = relu(self.z1)
        self.z2 = self.a1 @ self.W2 + self.b2
        self.a2 = softmax(self.z2)
        return self.a2

    def train_step(self, X, Y, lr=0.01):
        m = X.shape[0]
        out = self.forward(X)
        # Cross-entropy gradient
        dz2 = out - Y
        dW2 = self.a1.T @ dz2 / m
        db2 = dz2.mean(axis=0)
        da1 = dz2 @ self.W2.T
        dz1 = da1 * (self.z1 > 0).astype(float)
        dW1 = X.T @ dz1 / m
        db1 = dz1.mean(axis=0)
        self.W1 -= lr * dW1
        self.b1 -= lr * db1
        self.W2 -= lr * dW2
        self.b2 -= lr * db2
        loss = -np.mean(np.log(np.clip(out[Y.astype(bool)], 1e-10, 1)))
        return loss

    def accuracy(self, X, y):
        pred = self.forward(X).argmax(axis=1)
        return np.mean(pred == y)

    def copy(self):
        nn = SimpleNN.__new__(SimpleNN)
        nn.W1 = self.W1.copy()
        nn.b1 = self.b1.copy()
        nn.W2 = self.W2.copy()
        nn.b2 = self.b2.copy()
        return nn

# --- PH computation (H0 count from weight distance matrix) ---
def compute_ph_h0(weight_matrix, thresholds=None):
    """Compute H0 (connected components) at various distance thresholds."""
    # Use rows of weight matrix as points
    W = weight_matrix
    # Pairwise distance
    n = min(W.shape[0], 64)  # limit for speed
    W_sub = W[:n]
    dists = np.sqrt(((W_sub[:, None, :] - W_sub[None, :, :]) ** 2).sum(axis=2))

    if thresholds is None:
        # Auto-scale thresholds based on actual distance distribution
        flat = dists[np.triu_indices(n, k=1)]
        thresholds = np.linspace(np.percentile(flat, 5), np.percentile(flat, 95), 15)

    h0_counts = []
    for eps in thresholds:
        # Count connected components via union-find
        adj = dists < eps
        visited = np.zeros(n, dtype=bool)
        components = 0
        for i in range(n):
            if not visited[i]:
                components += 1
                stack = [i]
                while stack:
                    node = stack.pop()
                    if visited[node]:
                        continue
                    visited[node] = True
                    neighbors = np.where(adj[node] & ~visited)[0]
                    stack.extend(neighbors.tolist())
        h0_counts.append(components)
    return thresholds, np.array(h0_counts)

def barcode_distance(h0_a, h0_b):
    """L2 distance between two H0 barcode vectors."""
    return np.sqrt(np.sum((h0_a - h0_b) ** 2))

# --- Load MNIST subset ---
print("Loading MNIST...")
mnist = fetch_openml('mnist_784', version=1, as_frame=False, parser='auto')
X_all, y_all = mnist.data / 255.0, mnist.target.astype(int)

# Use small subset for speed
n_train = 3000
n_test = 500
idx = np.random.permutation(len(X_all))
X_train, y_train = X_all[idx[:n_train]], y_all[idx[:n_train]]
X_test, y_test = X_all[idx[n_train:n_train+n_test]], y_all[idx[n_train:n_train+n_test]]

# One-hot encode
enc = OneHotEncoder(sparse_output=False, categories=[range(10)])
Y_train = enc.fit_transform(y_train.reshape(-1, 1))
Y_test_oh = enc.transform(y_test.reshape(-1, 1))

# Digit subsets for forgetting test
digits_A = [0, 1, 2, 3, 4]
digits_B = [5, 6, 7, 8, 9]
mask_A_train = np.isin(y_train, digits_A)
mask_B_train = np.isin(y_train, digits_B)
mask_A_test = np.isin(y_test, digits_A)
mask_B_test = np.isin(y_test, digits_B)

# --- Phase 1: Train on all digits for 5 epochs ---
print("\n=== Phase 1: Initial Training (5 epochs, all digits) ===")
hidden = 64
nn = SimpleNN(784, hidden, 10)
thresholds = None  # auto-scale based on actual distances

ph_history = []
threshold_history = []
acc_history = []
batch_size = 128

for epoch in range(5):
    # Mini-batch training
    perm = np.random.permutation(n_train)
    total_loss = 0
    n_batches = 0
    for i in range(0, n_train, batch_size):
        batch_idx = perm[i:i+batch_size]
        loss = nn.train_step(X_train[batch_idx], Y_train[batch_idx], lr=0.1)
        total_loss += loss
        n_batches += 1

    acc = nn.accuracy(X_test, y_test)
    t, h0 = compute_ph_h0(nn.W1, thresholds)
    if thresholds is None:
        thresholds = t  # fix thresholds from epoch 1 for comparability
    ph_history.append(h0.copy())
    threshold_history.append(t.copy())
    acc_history.append(acc)
    print(f"  Epoch {epoch+1}: loss={total_loss/n_batches:.4f}, acc={acc:.4f}, H0_range=[{h0.min()},{h0.max()}]")

# Save reference barcode (epoch 5)
barcode_reference = ph_history[-1].copy()
nn_trained = nn.copy()

# --- Phase 2a: Catastrophic Forgetting (train on digits B only) ---
print("\n=== Phase 2a: Catastrophic Forgetting (train on digits 5-9 only) ===")
nn_forget = nn_trained.copy()
ph_forget = [barcode_reference.copy()]
acc_A_forget = [nn_forget.accuracy(X_test[mask_A_test], y_test[mask_A_test])]
acc_B_forget = [nn_forget.accuracy(X_test[mask_B_test], y_test[mask_B_test])]

X_B = X_train[mask_B_train]
Y_B = Y_train[mask_B_train]

for epoch in range(5):
    perm = np.random.permutation(len(X_B))
    for i in range(0, len(X_B), batch_size):
        batch_idx = perm[i:i+batch_size]
        nn_forget.train_step(X_B[batch_idx], Y_B[batch_idx], lr=0.1)

    _, h0 = compute_ph_h0(nn_forget.W1, thresholds)
    ph_forget.append(h0.copy())
    a_acc = nn_forget.accuracy(X_test[mask_A_test], y_test[mask_A_test])
    b_acc = nn_forget.accuracy(X_test[mask_B_test], y_test[mask_B_test])
    acc_A_forget.append(a_acc)
    acc_B_forget.append(b_acc)
    print(f"  Epoch {epoch+1}: acc_A={a_acc:.4f}, acc_B={b_acc:.4f}, H0_range=[{h0.min()},{h0.max()}]")

# --- Phase 2b: Mitosis Protection (maintain diversity) ---
print("\n=== Phase 2b: Mitosis Protection (diversity-preserving training) ===")
nn_mitosis = nn_trained.copy()
ph_mitosis = [barcode_reference.copy()]
acc_A_mitosis = [nn_mitosis.accuracy(X_test[mask_A_test], y_test[mask_A_test])]
acc_B_mitosis = [nn_mitosis.accuracy(X_test[mask_B_test], y_test[mask_B_test])]

for epoch in range(5):
    perm = np.random.permutation(len(X_B))
    for i in range(0, len(X_B), batch_size):
        batch_idx = perm[i:i+batch_size]
        nn_mitosis.train_step(X_B[batch_idx], Y_B[batch_idx], lr=0.1)

    # Mitosis: mix in 20% old data to preserve memory
    n_replay = len(X_B) // 5
    replay_idx = np.random.choice(np.where(mask_A_train)[0], n_replay, replace=True)
    for i in range(0, n_replay, batch_size):
        bi = replay_idx[i:i+batch_size]
        nn_mitosis.train_step(X_train[bi], Y_train[bi], lr=0.05)

    # Also: regularize toward original weights (elastic weight consolidation lite)
    ewc_lambda = 0.01
    nn_mitosis.W1 = nn_mitosis.W1 - ewc_lambda * (nn_mitosis.W1 - nn_trained.W1)
    nn_mitosis.W2 = nn_mitosis.W2 - ewc_lambda * (nn_mitosis.W2 - nn_trained.W2)

    _, h0 = compute_ph_h0(nn_mitosis.W1, thresholds)
    ph_mitosis.append(h0.copy())
    a_acc = nn_mitosis.accuracy(X_test[mask_A_test], y_test[mask_A_test])
    b_acc = nn_mitosis.accuracy(X_test[mask_B_test], y_test[mask_B_test])
    acc_A_mitosis.append(a_acc)
    acc_B_mitosis.append(b_acc)
    print(f"  Epoch {epoch+1}: acc_A={a_acc:.4f}, acc_B={b_acc:.4f}, H0_range=[{h0.min()},{h0.max()}]")

# --- Analysis ---
print("\n" + "="*60)
print("=== PH Barcode Distance Analysis ===")
print("="*60)

print("\n--- Barcode Distance from Reference (trained state) ---")
print(f"{'Phase':<30} {'Epoch':<8} {'Distance':<12} {'Acc_A':<10} {'Acc_B':<10}")
print("-" * 70)

forget_dists = []
mitosis_dists = []

for i in range(6):
    d_f = barcode_distance(barcode_reference, ph_forget[i])
    d_m = barcode_distance(barcode_reference, ph_mitosis[i])
    forget_dists.append(d_f)
    mitosis_dists.append(d_m)
    label_f = "Forget" if i > 0 else "Reference"
    label_m = "Mitosis" if i > 0 else "Reference"
    print(f"{'Forgetting':<30} {i:<8} {d_f:<12.4f} {acc_A_forget[i]:<10.4f} {acc_B_forget[i]:<10.4f}")

print()
for i in range(6):
    d_m = mitosis_dists[i]
    print(f"{'Mitosis':<30} {i:<8} {d_m:<12.4f} {acc_A_mitosis[i]:<10.4f} {acc_B_mitosis[i]:<10.4f}")

# Correlation: barcode distance vs accuracy loss on A
acc_loss_forget = [acc_A_forget[0] - acc_A_forget[i] for i in range(6)]
acc_loss_mitosis = [acc_A_mitosis[0] - acc_A_mitosis[i] for i in range(6)]

corr_forget = np.corrcoef(forget_dists, acc_loss_forget)[0, 1] if np.std(forget_dists) > 0 else 0
corr_mitosis = np.corrcoef(mitosis_dists, acc_loss_mitosis)[0, 1] if np.std(mitosis_dists) > 0 else 0

print(f"\n--- Correlation: Barcode Distance vs Accuracy Loss ---")
print(f"  Forgetting path: r = {corr_forget:.4f}")
print(f"  Mitosis path:    r = {corr_mitosis:.4f}")

# Final comparison
print(f"\n--- Final Summary ---")
print(f"  Forgetting: barcode drift = {forget_dists[-1]:.4f}, acc_A drop = {acc_loss_forget[-1]:.4f}")
print(f"  Mitosis:    barcode drift = {mitosis_dists[-1]:.4f}, acc_A drop = {acc_loss_mitosis[-1]:.4f}")
print(f"  Barcode preservation ratio (Mitosis/Forget): {mitosis_dists[-1]/(forget_dists[-1]+1e-10):.4f}")

# ASCII graph
print("\n--- ASCII Graph: Barcode Distance Over Epochs ---")
max_d = max(max(forget_dists), max(mitosis_dists)) + 1
scale = 40.0 / (max_d + 0.01)
print(f"  Distance from reference barcode")
for i in range(5, -1, -1):
    # Find which values are at this height
    row_val = max_d * (i + 0.5) / 6
    bar = f"  {row_val:6.1f} |"
    for j in range(6):
        f_h = forget_dists[j] * 6 / max_d
        m_h = mitosis_dists[j] * 6 / max_d
        cell = "  "
        if abs(f_h - (i + 0.5)) < 0.6:
            cell = " F"
        if abs(m_h - (i + 0.5)) < 0.6:
            cell = " M" if cell == "  " else "FM"
        bar += cell + "    "
    print(bar)
print(f"         +{'------' * 6}")
print(f"          ep0   ep1   ep2   ep3   ep4   ep5")
print(f"  F = Forgetting, M = Mitosis")

# Training PH evolution
print("\n--- PH Barcode Evolution During Initial Training ---")
print(f"  {'Epoch':<8}", end="")
for t in thresholds[:8]:
    print(f"  t={t:.1f}", end="")
print()
for i, h0 in enumerate(ph_history):
    print(f"  {i+1:<8}", end="")
    for v in h0[:8]:
        print(f"  {v:5d}", end="")
    print()

print("\n=== DONE ===")
