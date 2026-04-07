#!/usr/bin/env python3
"""Experiment TREE-7: Is detach() equivalent to Information Bottleneck?

Tishby's IB theory: optimal representation compresses input while preserving
label information. The IB optimal frontier maximizes I(Z;Y) for a given I(X;Z).

Hypothesis: detach() forces the observer into IB-optimal compression.
- detach cuts gradient flow -> observer must compress (can't overfit to input)
- This should push the observer's representation toward the IB frontier:
  lower I(X;Z) (more compression) with similar I(Z;Y) (label preservation)

Method:
  1. Train RepulsionFieldQuad + observer (detach vs no-detach) on MNIST
  2. Extract internal representations Z from the observer layer
  3. Approximate MI using binned histograms on top-2 PCA components:
     - I(X;Z): mutual information between input (PCA of X) and representation Z
     - I(Z;Y): mutual information between representation Z and label Y
  4. Plot on IB plane: detach should be closer to IB frontier
     (lower I(X;Z), similar or higher I(Z;Y))

Approximation: 10 bins per dimension, first 2 PCA components for tractability.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import time
import sys

sys.path.insert(0, '/Users/ghost/Dev/logout')

from model_utils import load_mnist, count_params
from model_meta_engine import EngineA, EngineG, EngineE, EngineF


# ─────────────────────────────────────────
# RepulsionFieldQuad with Observer (configurable detach)
# ─────────────────────────────────────────

class RepulsionFieldQuadWithObserver(nn.Module):
    """RepulsionFieldQuad + observer that reads pole outputs.

    Args:
        use_detach: if True, observer reads detached pole outputs (no gradient).
    """
    def __init__(self, input_dim=784, hidden_dim=48, output_dim=10, use_detach=True):
        super().__init__()
        self.use_detach = use_detach

        # 4 poles (same as RepulsionFieldQuad)
        self.engine_a = EngineA(input_dim, hidden_dim, output_dim)
        self.engine_e = EngineE(input_dim, hidden_dim, output_dim)
        self.engine_g = EngineG(input_dim, hidden_dim, output_dim)
        self.engine_f = EngineF(input_dim, hidden_dim, output_dim)

        self.field_transform = nn.Sequential(
            nn.Linear(output_dim * 2, output_dim),
            nn.Tanh(),
        )
        self.tension_scale = nn.Parameter(torch.tensor(1/3))

        # Observer: reads all 4 poles' outputs
        self.observer = nn.Sequential(
            nn.Linear(output_dim * 4, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, output_dim),
        )
        self.observer_scale = nn.Parameter(torch.tensor(0.1))

        self.aux_loss = torch.tensor(0.0)
        self.tension_content = 0.0
        self.tension_structure = 0.0

        # Storage for representation extraction
        self._observer_input = None
        self._observer_output = None

    def forward(self, x):
        out_a = self.engine_a(x)
        out_e = self.engine_e(x)
        out_g = self.engine_g(x)
        out_f = self.engine_f(x)

        # Repulsion axes
        repulsion_content = out_a - out_g
        repulsion_structure = out_e - out_f

        t_content = (repulsion_content ** 2).sum(dim=-1, keepdim=True)
        t_structure = (repulsion_structure ** 2).sum(dim=-1, keepdim=True)

        equilibrium = (out_a + out_e + out_g + out_f) / 4

        combined_repulsion = torch.cat([repulsion_content, repulsion_structure], dim=-1)
        field_direction = self.field_transform(combined_repulsion)

        total_tension = torch.sqrt((t_content * t_structure) + 1e-8)
        field_output = equilibrium + self.tension_scale * torch.sqrt(total_tension + 1e-8) * field_direction

        # Observer
        if self.use_detach:
            observed = torch.cat([out_a.detach(), out_e.detach(),
                                  out_g.detach(), out_f.detach()], dim=-1)
        else:
            observed = torch.cat([out_a, out_e, out_g, out_f], dim=-1)

        # Store for MI analysis
        self._observer_input = observed.detach()

        correction = self.observer(observed)
        self._observer_output = correction.detach()

        output = field_output + self.observer_scale * correction

        self.aux_loss = getattr(self.engine_g, 'entropy_loss', torch.tensor(0.0))

        with torch.no_grad():
            self.tension_content = t_content.mean().item()
            self.tension_structure = t_structure.mean().item()

        return (output, self.aux_loss)


# ─────────────────────────────────────────
# Training loop
# ─────────────────────────────────────────

def train_model(model, train_loader, test_loader, epochs=10, lr=0.001):
    """Train and return final accuracy."""
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()

    for epoch in range(epochs):
        model.train()
        total_loss = 0
        correct = 0
        total = 0
        for X, y in train_loader:
            X = X.view(X.size(0), -1)
            optimizer.zero_grad()
            out = model(X)
            if isinstance(out, tuple):
                logits, aux = out
                loss = criterion(logits, y) + 0.1 * aux
            else:
                logits = out
                loss = criterion(logits, y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
            pred = logits.argmax(dim=1)
            correct += (pred == y).sum().item()
            total += y.size(0)

        if (epoch + 1) % 2 == 0 or epoch == 0:
            acc = 100.0 * correct / total
            print(f"  Epoch {epoch+1}/{epochs}  loss={total_loss/len(train_loader):.4f}  train_acc={acc:.1f}%")

    # Final test accuracy
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for X, y in test_loader:
            X = X.view(X.size(0), -1)
            out = model(X)
            if isinstance(out, tuple):
                logits = out[0]
            else:
                logits = out
            pred = logits.argmax(dim=1)
            correct += (pred == y).sum().item()
            total += y.size(0)

    test_acc = 100.0 * correct / total
    return test_acc


# ─────────────────────────────────────────
# PCA (manual, numpy only)
# ─────────────────────────────────────────

def pca_2d(data):
    """Reduce data to 2D via PCA. data: (N, D) numpy array."""
    data = data - data.mean(axis=0)
    # Use SVD for numerical stability
    U, S, Vt = np.linalg.svd(data, full_matrices=False)
    return data @ Vt[:2].T  # (N, 2)


# ─────────────────────────────────────────
# Mutual Information estimation (binned histogram)
# ─────────────────────────────────────────

def estimate_mi_binned(x, y, n_bins=10):
    """Estimate MI between two arrays using binned histograms.

    x: (N,) or (N, d) -- continuous values, will be discretized
    y: (N,) -- discrete labels or continuous values

    Returns MI in nats.
    """
    N = len(x)

    # Discretize x into bins
    if x.ndim == 1:
        x = x.reshape(-1, 1)

    # Bin each dimension
    x_binned = np.zeros(N, dtype=int)
    n_dims = x.shape[1]
    multiplier = 1
    for d in range(n_dims):
        col = x[:, d]
        # Use percentile-based bins for robustness
        percentiles = np.linspace(0, 100, n_bins + 1)
        edges = np.percentile(col, percentiles)
        edges[-1] += 1e-10  # include max
        bins = np.digitize(col, edges[1:])  # 0 to n_bins-1
        bins = np.clip(bins, 0, n_bins - 1)
        x_binned += bins * multiplier
        multiplier *= n_bins

    # Discretize y if continuous
    if y.dtype in [np.float32, np.float64]:
        percentiles = np.linspace(0, 100, n_bins + 1)
        edges = np.percentile(y, percentiles)
        edges[-1] += 1e-10
        y_binned = np.digitize(y, edges[1:])
        y_binned = np.clip(y_binned, 0, n_bins - 1)
    else:
        y_binned = y.astype(int)

    # Joint distribution
    joint = {}
    for i in range(N):
        key = (int(x_binned[i]), int(y_binned[i]))
        joint[key] = joint.get(key, 0) + 1

    # Marginals
    px = {}
    py = {}
    for (xk, yk), c in joint.items():
        px[xk] = px.get(xk, 0) + c
        py[yk] = py.get(yk, 0) + c

    # MI = sum p(x,y) log(p(x,y) / (p(x)p(y)))
    mi = 0.0
    for (xk, yk), c in joint.items():
        p_xy = c / N
        p_x = px[xk] / N
        p_y = py[yk] / N
        if p_xy > 0 and p_x > 0 and p_y > 0:
            mi += p_xy * np.log(p_xy / (p_x * p_y))

    return mi


# ─────────────────────────────────────────
# Extract representations
# ─────────────────────────────────────────

def extract_representations(model, data_loader, max_samples=5000):
    """Extract observer input (Z_in), observer output (Z_out), input X, and labels Y."""
    model.eval()
    all_x = []
    all_z_in = []
    all_z_out = []
    all_y = []
    n = 0

    with torch.no_grad():
        for X, y in data_loader:
            X_flat = X.view(X.size(0), -1)
            _ = model(X_flat)

            all_x.append(X_flat.numpy())
            all_z_in.append(model._observer_input.numpy())
            all_z_out.append(model._observer_output.numpy())
            all_y.append(y.numpy())

            n += X.size(0)
            if n >= max_samples:
                break

    X = np.concatenate(all_x)[:max_samples]
    Z_in = np.concatenate(all_z_in)[:max_samples]
    Z_out = np.concatenate(all_z_out)[:max_samples]
    Y = np.concatenate(all_y)[:max_samples]

    return X, Z_in, Z_out, Y


# ─────────────────────────────────────────
# IB Plane plot (ASCII)
# ─────────────────────────────────────────

def ascii_ib_plane(results, width=60, height=20):
    """Plot I(X;Z) vs I(Z;Y) on ASCII IB plane."""
    print("\n" + "=" * 70)
    print("  INFORMATION BOTTLENECK PLANE")
    print("  x-axis: I(X;Z) [compression - lower is better]")
    print("  y-axis: I(Z;Y) [label info - higher is better]")
    print("  IB frontier = upper-left corner")
    print("=" * 70)

    # Collect all points
    all_ixz = []
    all_izy = []
    labels = []
    markers = []

    for name, data in results.items():
        all_ixz.append(data['I_XZ'])
        all_izy.append(data['I_ZY'])
        labels.append(name)
        markers.append(data.get('marker', '*'))

    x_min = min(all_ixz) * 0.9
    x_max = max(all_ixz) * 1.1
    y_min = min(all_izy) * 0.9
    y_max = max(all_izy) * 1.1

    if x_max == x_min:
        x_max = x_min + 0.1
    if y_max == y_min:
        y_max = y_min + 0.1

    # Build grid
    grid = [[' ' for _ in range(width)] for _ in range(height)]

    # Plot points
    for i, (ixz, izy) in enumerate(zip(all_ixz, all_izy)):
        col = int((ixz - x_min) / (x_max - x_min) * (width - 1))
        row = int((izy - y_min) / (y_max - y_min) * (height - 1))
        col = max(0, min(width - 1, col))
        row = max(0, min(height - 1, row))
        grid[row][col] = markers[i]

    # Draw IB frontier line (upper-left diagonal as reference)
    for r in range(height):
        c = width - 1 - int(r * (width - 1) / (height - 1))
        c = max(0, min(width - 1, c))
        if grid[r][c] == ' ':
            grid[r][c] = '.'

    # Print
    for row in range(height - 1, -1, -1):
        y_val = y_min + (y_max - y_min) * row / (height - 1)
        if row == height - 1:
            prefix = f"  {y_val:>6.3f} |"
        elif row == 0:
            prefix = f"  {y_val:>6.3f} |"
        elif row == height // 2:
            prefix = f"  {y_val:>6.3f} |"
        else:
            prefix = f"         |"
        print(prefix + ''.join(grid[row]) + "|")

    print(f"         +{'-' * width}+")
    print(f"          {x_min:<6.3f}{' ' * (width // 2 - 12)}I(X;Z){' ' * (width // 2 - 6)}{x_max:>6.3f}")

    # Legend
    print("\n  Legend:")
    for i, name in enumerate(labels):
        ixz = all_ixz[i]
        izy = all_izy[i]
        m = markers[i]
        print(f"    [{m}] {name}: I(X;Z)={ixz:.4f}, I(Z;Y)={izy:.4f}")

    # IB efficiency = I(Z;Y) / I(X;Z)  (higher = more efficient compression)
    print("\n  IB Efficiency = I(Z;Y) / I(X;Z):")
    for i, name in enumerate(labels):
        ixz = all_ixz[i]
        izy = all_izy[i]
        eff = izy / max(ixz, 1e-10)
        print(f"    {name}: {eff:.4f}")


# ─────────────────────────────────────────
# ASCII bar chart
# ─────────────────────────────────────────

def ascii_bars(values, labels, title, width=40):
    """Simple horizontal bar chart."""
    print(f"\n  {title}")
    vmax = max(values) if values else 1
    for label, val in zip(labels, values):
        bar_len = int(val / vmax * width)
        bar = '#' * bar_len
        print(f"    {label:>20s} |{bar} {val:.4f}")


# ─────────────────────────────────────────
# Main experiment
# ─────────────────────────────────────────

def main():
    print("=" * 70)
    print("  TREE-7: Is detach() equivalent to Information Bottleneck?")
    print("=" * 70)
    print()
    print("  Tishby IB theory: optimal Z compresses X while preserving Y info.")
    print("  Hypothesis: detach() -> observer forced into IB-optimal compression.")
    print("  Test: compare I(X;Z) and I(Z;Y) for detach vs no-detach observer.")
    print()

    # Load data
    print("[1/5] Loading MNIST...")
    train_loader, test_loader = load_mnist(batch_size=128)
    print("  Done.\n")

    # Train detach model
    print("[2/5] Training RepulsionFieldQuad + Observer (DETACH)...")
    t0 = time.time()
    model_detach = RepulsionFieldQuadWithObserver(use_detach=True)
    n_params = count_params(model_detach)
    print(f"  Parameters: {n_params}")
    acc_detach = train_model(model_detach, train_loader, test_loader, epochs=10)
    t_detach = time.time() - t0
    print(f"  Test accuracy: {acc_detach:.2f}%  ({t_detach:.1f}s)\n")

    # Train no-detach model
    print("[3/5] Training RepulsionFieldQuad + Observer (NO-DETACH)...")
    t0 = time.time()
    model_nodetach = RepulsionFieldQuadWithObserver(use_detach=False)
    acc_nodetach = train_model(model_nodetach, train_loader, test_loader, epochs=10)
    t_nodetach = time.time() - t0
    print(f"  Test accuracy: {acc_nodetach:.2f}%  ({t_nodetach:.1f}s)\n")

    # Extract representations
    print("[4/5] Extracting representations and computing MI...")
    N_BINS = 10
    MAX_SAMPLES = 5000

    results = {}

    for name, model in [("Detach", model_detach), ("No-Detach", model_nodetach)]:
        print(f"\n  --- {name} ---")
        X, Z_in, Z_out, Y = extract_representations(model, test_loader, max_samples=MAX_SAMPLES)

        # PCA on input X (784D -> 2D)
        X_pca = pca_2d(X)

        # PCA on observer input Z_in (40D -> 2D)
        Z_in_pca = pca_2d(Z_in)

        # PCA on observer output Z_out (10D -> 2D)
        Z_out_pca = pca_2d(Z_out)

        # I(X;Z) using observer output (how much input info is retained)
        # Approximate: MI between PCA(X) components and PCA(Z_out) components
        mi_xz_0 = estimate_mi_binned(X_pca[:, 0], Z_out_pca[:, 0], n_bins=N_BINS)
        mi_xz_1 = estimate_mi_binned(X_pca[:, 1], Z_out_pca[:, 1], n_bins=N_BINS)
        I_XZ = mi_xz_0 + mi_xz_1  # sum over PCA dimensions

        # I(Z;Y) using observer output (how much label info is preserved)
        mi_zy_0 = estimate_mi_binned(Z_out_pca[:, 0], Y, n_bins=N_BINS)
        mi_zy_1 = estimate_mi_binned(Z_out_pca[:, 1], Y, n_bins=N_BINS)
        I_ZY = mi_zy_0 + mi_zy_1

        # Also measure from observer input (Z_in) for comparison
        mi_xzin_0 = estimate_mi_binned(X_pca[:, 0], Z_in_pca[:, 0], n_bins=N_BINS)
        mi_xzin_1 = estimate_mi_binned(X_pca[:, 1], Z_in_pca[:, 1], n_bins=N_BINS)
        I_XZ_in = mi_xzin_0 + mi_xzin_1

        mi_ziny_0 = estimate_mi_binned(Z_in_pca[:, 0], Y, n_bins=N_BINS)
        mi_ziny_1 = estimate_mi_binned(Z_in_pca[:, 1], Y, n_bins=N_BINS)
        I_ZY_in = mi_ziny_0 + mi_ziny_1

        print(f"  Observer Output: I(X;Z)={I_XZ:.4f}  I(Z;Y)={I_ZY:.4f}  efficiency={I_ZY/max(I_XZ,1e-10):.4f}")
        print(f"  Observer Input:  I(X;Z)={I_XZ_in:.4f}  I(Z;Y)={I_ZY_in:.4f}  efficiency={I_ZY_in/max(I_XZ_in,1e-10):.4f}")

        marker = 'D' if name == "Detach" else 'N'
        results[f"{name} (output)"] = {
            'I_XZ': I_XZ, 'I_ZY': I_ZY, 'marker': marker,
            'acc': acc_detach if name == "Detach" else acc_nodetach
        }
        results[f"{name} (input)"] = {
            'I_XZ': I_XZ_in, 'I_ZY': I_ZY_in,
            'marker': marker.lower(),
        }

    # Plot IB plane
    print("\n[5/5] IB Plane Analysis...")
    ascii_ib_plane(results)

    # Summary
    print("\n" + "=" * 70)
    print("  SUMMARY")
    print("=" * 70)

    d_out = results["Detach (output)"]
    n_out = results["No-Detach (output)"]

    print(f"\n  Accuracy:  Detach={acc_detach:.2f}%  No-Detach={acc_nodetach:.2f}%  delta={acc_detach-acc_nodetach:+.2f}%")
    print()
    print(f"  Observer Output MI:")
    print(f"    Detach:    I(X;Z)={d_out['I_XZ']:.4f}  I(Z;Y)={d_out['I_ZY']:.4f}")
    print(f"    No-Detach: I(X;Z)={n_out['I_XZ']:.4f}  I(Z;Y)={n_out['I_ZY']:.4f}")
    print()

    # IB analysis
    eff_d = d_out['I_ZY'] / max(d_out['I_XZ'], 1e-10)
    eff_n = n_out['I_ZY'] / max(n_out['I_XZ'], 1e-10)

    compression_ratio = d_out['I_XZ'] / max(n_out['I_XZ'], 1e-10)
    label_ratio = d_out['I_ZY'] / max(n_out['I_ZY'], 1e-10)

    print(f"  IB Efficiency (I(Z;Y)/I(X;Z)):")
    print(f"    Detach:    {eff_d:.4f}")
    print(f"    No-Detach: {eff_n:.4f}")
    print(f"    Ratio:     {eff_d/max(eff_n,1e-10):.4f}x")
    print()
    print(f"  Compression: I(X;Z)_detach / I(X;Z)_nodetach = {compression_ratio:.4f}")
    print(f"  Label info:  I(Z;Y)_detach / I(Z;Y)_nodetach = {label_ratio:.4f}")
    print()

    # Verdict
    ib_optimal = (d_out['I_XZ'] < n_out['I_XZ']) and (d_out['I_ZY'] >= n_out['I_ZY'] * 0.95)
    more_compressed = d_out['I_XZ'] < n_out['I_XZ']
    more_efficient = eff_d > eff_n

    print("  HYPOTHESIS TEST: detach() -> IB-optimal compression")
    print(f"    More compressed (lower I(X;Z)):     {'YES' if more_compressed else 'NO'}")
    print(f"    Preserves label info (I(Z;Y)):       {'YES' if label_ratio >= 0.95 else 'NO'} (ratio={label_ratio:.3f})")
    print(f"    Higher IB efficiency:                {'YES' if more_efficient else 'NO'} ({eff_d:.3f} vs {eff_n:.3f})")
    print(f"    IB-optimal (compressed + preserves): {'YES' if ib_optimal else 'NO'}")
    print()

    if ib_optimal:
        print("  RESULT: CONFIRMED -- detach() acts as Information Bottleneck")
        print("  The observer compresses input information while preserving label info,")
        print("  consistent with Tishby's IB theory.")
    elif more_efficient:
        print("  RESULT: PARTIALLY CONFIRMED -- detach() improves IB efficiency")
        print("  The observer achieves better compression-to-label ratio,")
        print("  even if not strictly on the IB frontier.")
    else:
        print("  RESULT: NOT CONFIRMED -- detach() does not clearly produce IB-optimal compression")
        print("  The relationship between detach and IB theory needs further investigation.")

    # Bar charts
    ascii_bars(
        [d_out['I_XZ'], n_out['I_XZ']],
        ['Detach', 'No-Detach'],
        'I(X;Z) - Input Compression (lower = more compressed)'
    )
    ascii_bars(
        [d_out['I_ZY'], n_out['I_ZY']],
        ['Detach', 'No-Detach'],
        'I(Z;Y) - Label Preservation (higher = better)'
    )
    ascii_bars(
        [eff_d, eff_n],
        ['Detach', 'No-Detach'],
        'IB Efficiency = I(Z;Y)/I(X;Z) (higher = better)'
    )

    print("\n" + "=" * 70)
    print("  TREE-7 experiment complete.")
    print("=" * 70)


if __name__ == '__main__':
    main()
