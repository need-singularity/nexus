#!/usr/bin/env python3
"""
H-ROB-9: Confusion Matrix = Grasp Failure Map
Verify that neural network confusion pairs predict grasp parameter confusion.
"""

import numpy as np
from collections import defaultdict

np.random.seed(42)

# ============================================================
# 1. Define 10 common graspable objects with grasp parameters
# ============================================================
# Parameters: (width_mm, approach_angle_deg, force_N)
# width: gripper opening, angle: approach direction, force: grip strength

OBJECTS = {
    'cup':    (80, 90, 3.0),    # vertical, medium grip
    'ball':   (70, 45, 2.5),    # angled, gentle
    'bottle': (65, 90, 3.5),    # vertical, firm
    'book':   (30, 0, 4.0),     # horizontal, strong
    'pen':    (15, 0, 1.0),     # horizontal, light
    'phone':  (25, 0, 2.0),     # horizontal, medium
    'plate':  (35, 0, 1.5),     # horizontal, light
    'box':    (100, 90, 5.0),   # vertical, strong
    'banana': (50, 45, 1.5),    # angled, gentle
    'hammer': (40, 0, 6.0),     # horizontal, very strong
}

obj_names = list(OBJECTS.keys())
n_objects = len(obj_names)
grasp_params = np.array([OBJECTS[o] for o in obj_names])

# Normalize grasp parameters for fair distance computation
grasp_norm = grasp_params.copy().astype(float)
for col in range(3):
    mn, mx = grasp_norm[:, col].min(), grasp_norm[:, col].max()
    if mx > mn:
        grasp_norm[:, col] = (grasp_norm[:, col] - mn) / (mx - mn)

# ============================================================
# 2. Grasp similarity matrix (Euclidean distance in normalized space)
# ============================================================
grasp_dist = np.zeros((n_objects, n_objects))
for i in range(n_objects):
    for j in range(n_objects):
        grasp_dist[i, j] = np.linalg.norm(grasp_norm[i] - grasp_norm[j])

# Convert distance to similarity (1 - normalized distance)
max_dist = grasp_dist.max()
grasp_sim = 1.0 - grasp_dist / max_dist
np.fill_diagonal(grasp_sim, 0)  # zero self-similarity for comparison

print("=" * 70)
print("H-ROB-9: Confusion Matrix = Grasp Failure Map")
print("=" * 70)

print("\n[1] Object Grasp Parameters (raw)")
print(f"{'Object':<10} {'Width(mm)':>10} {'Angle(deg)':>11} {'Force(N)':>9}")
print("-" * 42)
for name in obj_names:
    w, a, f = OBJECTS[name]
    print(f"{name:<10} {w:>10.0f} {a:>11.0f} {f:>9.1f}")

# ============================================================
# 3. Generate synthetic sensor readings for neural network
# ============================================================
# Each object generates sensor features with noise
# Features: shape_factor, weight_est, texture, reflectance, size_est
n_features = 5
n_samples_per_class = 200

# Define feature centers correlated with but not identical to grasp params
feature_centers = np.zeros((n_objects, n_features))
for i, name in enumerate(obj_names):
    w, a, f = grasp_norm[i]
    feature_centers[i] = [
        w * 0.8 + 0.1,           # shape ~ width
        f * 0.7 + 0.15,          # weight ~ force
        np.sin(a * np.pi) * 0.5 + 0.5,  # texture ~ angle
        0.3 + 0.4 * w,           # reflectance ~ width
        w * 0.6 + a * 0.3 + 0.1  # size ~ width + angle
    ]

X_train, y_train = [], []
X_test, y_test = [], []

for i in range(n_objects):
    noise_scale = 0.15
    samples = feature_centers[i] + np.random.randn(n_samples_per_class, n_features) * noise_scale
    split = int(n_samples_per_class * 0.7)
    X_train.append(samples[:split])
    y_train.extend([i] * split)
    X_test.append(samples[split:])
    y_test.extend([i] * (n_samples_per_class - split))

X_train = np.vstack(X_train)
y_train = np.array(y_train)
X_test = np.vstack(X_test)
y_test = np.array(y_test)

# ============================================================
# 4. Train simple neural network (2-layer MLP from scratch)
# ============================================================
def softmax(x):
    e = np.exp(x - x.max(axis=1, keepdims=True))
    return e / e.sum(axis=1, keepdims=True)

def relu(x):
    return np.maximum(0, x)

# Initialize weights
hidden_size = 32
W1 = np.random.randn(n_features, hidden_size) * 0.1
b1 = np.zeros(hidden_size)
W2 = np.random.randn(hidden_size, n_objects) * 0.1
b2 = np.zeros(n_objects)

lr = 0.01
n_epochs = 300

print("\n[2] Training 2-layer MLP...")
for epoch in range(n_epochs):
    # Forward
    h = relu(X_train @ W1 + b1)
    logits = h @ W2 + b2
    probs = softmax(logits)

    # Loss
    loss = -np.log(probs[np.arange(len(y_train)), y_train] + 1e-8).mean()

    # Backward
    dlogits = probs.copy()
    dlogits[np.arange(len(y_train)), y_train] -= 1
    dlogits /= len(y_train)

    dW2 = h.T @ dlogits
    db2 = dlogits.sum(axis=0)
    dh = dlogits @ W2.T
    dh[h <= 0] = 0
    dW1 = X_train.T @ dh
    db1 = dh.sum(axis=0)

    W2 -= lr * dW2
    b2 -= lr * db2
    W1 -= lr * dW1
    b1 -= lr * db1

# Test accuracy
h_test = relu(X_test @ W1 + b1)
logits_test = h_test @ W2 + b2
preds = logits_test.argmax(axis=1)
accuracy = (preds == y_test).mean()
print(f"Test accuracy: {accuracy:.1%}")

# ============================================================
# 5. Build confusion matrix
# ============================================================
conf_matrix = np.zeros((n_objects, n_objects), dtype=int)
for true, pred in zip(y_test, preds):
    conf_matrix[true, pred] += 1

# Neural confusion similarity (off-diagonal, symmetrized)
neural_conf = conf_matrix.astype(float)
np.fill_diagonal(neural_conf, 0)
neural_conf_sym = (neural_conf + neural_conf.T) / 2.0
# Normalize
nc_max = neural_conf_sym.max()
if nc_max > 0:
    neural_conf_norm = neural_conf_sym / nc_max
else:
    neural_conf_norm = neural_conf_sym

print("\n[3] Neural Network Confusion Matrix")
print(f"{'':>8}", end='')
for name in obj_names:
    print(f"{name[:4]:>5}", end='')
print()
for i, name in enumerate(obj_names):
    print(f"{name[:7]:>8}", end='')
    for j in range(n_objects):
        val = conf_matrix[i, j]
        if val == 0:
            print(f"{'·':>5}", end='')
        else:
            print(f"{val:>5}", end='')
    print()

print("\n[4] Grasp Similarity Matrix (normalized)")
print(f"{'':>8}", end='')
for name in obj_names:
    print(f"{name[:4]:>6}", end='')
print()
for i, name in enumerate(obj_names):
    print(f"{name[:7]:>8}", end='')
    for j in range(n_objects):
        val = grasp_sim[i, j]
        print(f"{val:>6.2f}", end='')
    print()

# ============================================================
# 6. Correlation: neural confusion vs grasp similarity
# ============================================================
# Extract upper triangle (off-diagonal) pairs
pairs_neural = []
pairs_grasp = []
pair_labels = []
for i in range(n_objects):
    for j in range(i + 1, n_objects):
        pairs_neural.append(neural_conf_norm[i, j])
        pairs_grasp.append(grasp_sim[i, j])
        pair_labels.append(f"{obj_names[i][:3]}-{obj_names[j][:3]}")

pairs_neural = np.array(pairs_neural)
pairs_grasp = np.array(pairs_grasp)

# Pearson correlation
def pearson_r(x, y):
    mx, my = x.mean(), y.mean()
    num = ((x - mx) * (y - my)).sum()
    den = np.sqrt(((x - mx)**2).sum() * ((y - my)**2).sum())
    return num / den if den > 0 else 0.0

# Spearman rank correlation
def spearman_r(x, y):
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    return pearson_r(rx, ry)

r_pearson = pearson_r(pairs_neural, pairs_grasp)
r_spearman = spearman_r(pairs_neural, pairs_grasp)

n_pairs = len(pairs_neural)
# t-test for significance
t_stat = r_pearson * np.sqrt((n_pairs - 2) / (1 - r_pearson**2 + 1e-10))

print("\n[5] Correlation Analysis")
print(f"  Number of object pairs: {n_pairs}")
print(f"  Pearson  r = {r_pearson:.4f}")
print(f"  Spearman r = {r_spearman:.4f}")
print(f"  t-statistic = {t_stat:.3f} (df={n_pairs-2})")
print(f"  |r| > 0.3 → meaningful correlation: {'YES' if abs(r_pearson) > 0.3 else 'NO'}")

# ============================================================
# 7. Top confused pairs vs top grasp-similar pairs
# ============================================================
# Sort by neural confusion (descending)
idx_neural = np.argsort(-pairs_neural)
idx_grasp = np.argsort(-pairs_grasp)

print("\n[6] Top 10 Most Confused Pairs (Neural) vs Most Similar (Grasp)")
print(f"{'Rank':>4}  {'Neural Confused':>20} {'Score':>6}  {'Grasp Similar':>20} {'Score':>6}  {'Match':>5}")
print("-" * 70)
overlap_count = 0
top_k = 10
neural_top_set = set([pair_labels[idx_neural[i]] for i in range(top_k)])
grasp_top_set = set([pair_labels[idx_grasp[i]] for i in range(top_k)])
overlap = neural_top_set & grasp_top_set

for rank in range(top_k):
    ni = idx_neural[rank]
    gi = idx_grasp[rank]
    match = '*' if pair_labels[ni] in grasp_top_set else ''
    print(f"{rank+1:>4}  {pair_labels[ni]:>20} {pairs_neural[ni]:>6.3f}  {pair_labels[gi]:>20} {pairs_grasp[gi]:>6.3f}  {match:>5}")

overlap_pct = len(overlap) / top_k * 100
print(f"\nTop-10 overlap: {len(overlap)}/{top_k} = {overlap_pct:.0f}%")

# ============================================================
# 8. Persistent Homology (H0) from both matrices
# ============================================================
print("\n[7] Persistent Homology (H0) — Single Linkage Dendrogram")

def single_linkage_merges(dist_matrix, names):
    """Compute H0 merge order using single linkage clustering."""
    n = len(names)
    # Convert similarity to distance if needed
    active = list(range(n))
    clusters = {i: [names[i]] for i in range(n)}
    merges = []

    while len(active) > 1:
        # Find minimum distance pair
        min_dist = np.inf
        mi, mj = -1, -1
        for ii in range(len(active)):
            for jj in range(ii + 1, len(active)):
                d = dist_matrix[active[ii], active[jj]]
                if d < min_dist:
                    min_dist = d
                    mi, mj = ii, jj

        ci, cj = active[mi], active[mj]
        merge_label = f"{'+'.join(clusters[ci][:2])}+{'+'.join(clusters[cj][:2])}"
        merges.append((min_dist, clusters[ci][0], clusters[cj][0]))

        # Merge clusters
        new_id = max(clusters.keys()) + 1
        clusters[new_id] = clusters[ci] + clusters[cj]

        # Update distances (single linkage = minimum)
        new_row = np.full(dist_matrix.shape[0], np.inf)
        for k in active:
            if k != ci and k != cj:
                new_row[k] = min(dist_matrix[ci, k], dist_matrix[cj, k])

        # Expand matrix
        old_size = dist_matrix.shape[0]
        new_matrix = np.full((old_size + 1, old_size + 1), np.inf)
        new_matrix[:old_size, :old_size] = dist_matrix
        new_row_full = np.full(old_size + 1, np.inf)
        new_row_full[:old_size] = new_row
        new_row_full[new_id] = 0
        new_matrix[new_id] = new_row_full
        new_matrix[:, new_id] = new_row_full
        dist_matrix = new_matrix

        active.remove(ci)
        active.remove(cj)
        active.append(new_id)

        del clusters[ci]
        del clusters[cj]

    return merges

# Grasp merges (using grasp distance)
grasp_merges = single_linkage_merges(grasp_dist.copy(), obj_names)
print("\nGrasp PH (H0) merge order:")
for i, (dist, a, b) in enumerate(grasp_merges):
    bar = '#' * int(dist / grasp_dist.max() * 30)
    print(f"  {i+1}. d={dist:.3f} {a[:6]:>6}+{b[:6]:<6} |{bar}")

# Neural merges (using 1 - confusion as distance)
neural_dist = np.ones((n_objects, n_objects)) - neural_conf_norm
np.fill_diagonal(neural_dist, 0)
neural_merges = single_linkage_merges(neural_dist.copy(), obj_names)
print("\nNeural PH (H0) merge order:")
for i, (dist, a, b) in enumerate(neural_merges):
    bar = '#' * int(dist * 30)
    print(f"  {i+1}. d={dist:.3f} {a[:6]:>6}+{b[:6]:<6} |{bar}")

# ============================================================
# 9. Compare PH merge orders
# ============================================================
# Extract merge pairs as sets for comparison
grasp_merge_pairs = [(min(a[:4], b[:4]), max(a[:4], b[:4])) for _, a, b in grasp_merges]
neural_merge_pairs = [(min(a[:4], b[:4]), max(a[:4], b[:4])) for _, a, b in neural_merges]

# Check first 5 merges overlap
n_check = min(5, len(grasp_merge_pairs))
early_grasp = set(grasp_merge_pairs[:n_check])
early_neural = set(neural_merge_pairs[:n_check])
ph_overlap = early_grasp & early_neural

print(f"\n[8] PH Merge Order Comparison (first {n_check} merges)")
print(f"  Grasp early merges:  {[f'{a}+{b}' for a, b in grasp_merge_pairs[:n_check]]}")
print(f"  Neural early merges: {[f'{a}+{b}' for a, b in neural_merge_pairs[:n_check]]}")
print(f"  Overlap: {len(ph_overlap)}/{n_check} = {len(ph_overlap)/n_check*100:.0f}%")

# Spearman on merge ranks
grasp_pair_rank = {p: i for i, p in enumerate(grasp_merge_pairs)}
neural_pair_rank = {p: i for i, p in enumerate(neural_merge_pairs)}
common_pairs = set(grasp_pair_rank.keys()) & set(neural_pair_rank.keys())
if len(common_pairs) >= 3:
    grank = np.array([grasp_pair_rank[p] for p in common_pairs])
    nrank = np.array([neural_pair_rank[p] for p in common_pairs])
    merge_r = spearman_r(grank, nrank)
    print(f"  Merge rank Spearman r = {merge_r:.4f}")
else:
    merge_r = 0.0
    print(f"  Too few common pairs for rank correlation")

# ============================================================
# 10. ASCII Scatter Plot: Grasp Similarity vs Neural Confusion
# ============================================================
print("\n[9] ASCII Scatter: Grasp Similarity (x) vs Neural Confusion (y)")
rows, cols = 20, 50
grid = [[' '] * cols for _ in range(rows)]

x_min, x_max = pairs_grasp.min(), pairs_grasp.max()
y_min, y_max = 0, max(pairs_neural.max(), 0.01)

for k in range(len(pairs_grasp)):
    xi = int((pairs_grasp[k] - x_min) / (x_max - x_min + 1e-10) * (cols - 1))
    yi = int((pairs_neural[k] - y_min) / (y_max - y_min + 1e-10) * (rows - 1))
    yi = rows - 1 - yi  # flip y
    xi = min(max(xi, 0), cols - 1)
    yi = min(max(yi, 0), rows - 1)
    grid[yi][xi] = '*'

print(f"  Neural")
print(f"  Conf. ^")
for i, row in enumerate(grid):
    if i == 0:
        label = f"{y_max:.2f}"
    elif i == rows - 1:
        label = f"{y_min:.2f}"
    else:
        label = "     "
    print(f"  {label:>5} |{''.join(row)}|")
print(f"        +{'-' * cols}+")
print(f"        {x_min:.2f}{' ' * (cols - 8)}{x_max:.2f}")
print(f"                    Grasp Similarity")

# ============================================================
# 11. ASCII Heatmap of Grasp Confusion Matrix
# ============================================================
print("\n[10] ASCII Heatmap: Grasp Similarity")
symbols = [' ', '.', ':', '+', '#', '@']
print(f"  Scale: {' '.join(f'{s}={i/5:.1f}' for i, s in enumerate(symbols))}")
print(f"{'':>8}", end='')
for name in obj_names:
    print(f"{name[:3]:>4}", end='')
print()
for i, name in enumerate(obj_names):
    print(f"{name[:7]:>8}", end='')
    for j in range(n_objects):
        if i == j:
            print(f"{'X':>4}", end='')
        else:
            level = int(grasp_sim[i, j] * (len(symbols) - 1))
            level = min(level, len(symbols) - 1)
            print(f"{symbols[level]:>4}", end='')
    print()

# ============================================================
# 12. Summary
# ============================================================
print("\n" + "=" * 70)
print("SUMMARY: H-ROB-9 Verification Results")
print("=" * 70)
print(f"  Test accuracy:           {accuracy:.1%}")
print(f"  Pearson correlation:     r = {r_pearson:.4f}")
print(f"  Spearman correlation:    r = {r_spearman:.4f}")
print(f"  Top-10 pair overlap:     {len(overlap)}/{top_k} = {overlap_pct:.0f}%")
print(f"  PH merge order overlap:  {len(ph_overlap)}/{n_check} = {len(ph_overlap)/n_check*100:.0f}%")
if len(common_pairs) >= 3:
    print(f"  PH merge rank Spearman:  r = {merge_r:.4f}")
print()

if r_pearson > 0.5:
    print("  VERDICT: STRONG support — neural confusion predicts grasp confusion")
elif r_pearson > 0.3:
    print("  VERDICT: MODERATE support — meaningful correlation exists")
elif r_pearson > 0.15:
    print("  VERDICT: WEAK support — some correlation, needs more data")
else:
    print("  VERDICT: INSUFFICIENT — no clear correlation found")

# Golden Zone check
golden_zone = (0.2123, 0.5000)
print(f"\n  Golden Zone check: r = {r_pearson:.4f}")
if golden_zone[0] <= abs(r_pearson) <= golden_zone[1]:
    print(f"  |r| in Golden Zone [{golden_zone[0]:.3f}, {golden_zone[1]:.3f}]: YES")
else:
    print(f"  |r| in Golden Zone [{golden_zone[0]:.3f}, {golden_zone[1]:.3f}]: NO")
