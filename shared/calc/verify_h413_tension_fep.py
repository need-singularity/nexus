#!/usr/bin/env python3
"""H-CX-413 Verification: Tension = Free Energy (Friston)

Tests whether PureField tension is isomorphic to variational free energy.
Computes both tension and FEP-style free energy proxy on MNIST, measures correlation.

Free Energy: F = E_q[ln q(s) - ln p(o,s)] ~ cross_entropy + KL(q||prior)
Tension:     T = mean(|A(x) - G(x)|^2)

If tension ~ free energy, we expect Pearson r > 0.8.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from scipy import stats
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model_pure_field import PureFieldEngine
from model_utils import load_mnist

def compute_free_energy_proxy(logits, targets, field_output):
    """FEP-style free energy = surprise + complexity.

    Surprise  = -log p(o|s) ~ cross-entropy loss per sample
    Complexity = KL(q(s)||p(s)) ~ 0.5 * ||field||^2 (Gaussian prior assumption)
    Free Energy = Surprise + Complexity
    """
    # Per-sample cross-entropy (surprise)
    ce = F.cross_entropy(logits, targets, reduction='none')  # (batch,)

    # Complexity: KL divergence with N(0,1) prior on field activations
    # For Gaussian q with mean=field, var=1: KL = 0.5 * ||mean||^2
    complexity = 0.5 * (field_output ** 2).mean(dim=-1)  # (batch,)

    free_energy = ce + complexity
    return free_energy, ce, complexity


def main():
    print("=" * 65)
    print("  H-CX-413 Verification: Tension = Free Energy (Friston FEP)")
    print("=" * 65)

    torch.manual_seed(42)
    np.random.seed(42)

    # Load MNIST
    print("\n[1] Loading MNIST...")
    train_loader, test_loader = load_mnist(batch_size=256)

    # Create and train model briefly
    print("[2] Training PureFieldEngine (5 epochs)...")
    model = PureFieldEngine(784, 128, 10)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.CrossEntropyLoss()

    for epoch in range(5):
        model.train()
        total_loss = 0
        for X, y in train_loader:
            X = X.view(X.size(0), -1)
            optimizer.zero_grad()
            output, tension = model(X)
            loss = criterion(output, y) + 0.01 * tension.mean()
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"    Epoch {epoch+1}: Loss={total_loss/len(train_loader):.4f}")

    # Collect tension and free energy on test set
    print("\n[3] Computing tension and free energy on test set...")
    model.eval()
    all_tension = []
    all_fe = []
    all_surprise = []
    all_complexity = []

    with torch.no_grad():
        for X, y in test_loader:
            X = X.view(X.size(0), -1)
            output, tension = model(X)
            fe, surprise, complexity = compute_free_energy_proxy(output, y, output)

            all_tension.append(tension.numpy())
            all_fe.append(fe.numpy())
            all_surprise.append(surprise.numpy())
            all_complexity.append(complexity.numpy())

    tension_arr = np.concatenate(all_tension)
    fe_arr = np.concatenate(all_fe)
    surprise_arr = np.concatenate(all_surprise)
    complexity_arr = np.concatenate(all_complexity)

    n = len(tension_arr)
    print(f"    Samples: {n}")

    # Correlations
    r_fe, p_fe = stats.pearsonr(tension_arr, fe_arr)
    r_surp, p_surp = stats.pearsonr(tension_arr, surprise_arr)
    r_comp, p_comp = stats.pearsonr(tension_arr, complexity_arr)

    # Spearman (rank) correlations
    rho_fe, sp_fe = stats.spearmanr(tension_arr, fe_arr)
    rho_surp, sp_surp = stats.spearmanr(tension_arr, surprise_arr)

    print("\n[4] Results — Correlation Analysis")
    print("-" * 55)
    print(f"  {'Comparison':<32} {'Pearson r':>10} {'p-value':>12}")
    print("-" * 55)
    print(f"  {'Tension vs Free Energy':<32} {r_fe:>10.4f} {p_fe:>12.2e}")
    print(f"  {'Tension vs Surprise (CE)':<32} {r_surp:>10.4f} {p_surp:>12.2e}")
    print(f"  {'Tension vs Complexity (KL)':<32} {r_comp:>10.4f} {p_comp:>12.2e}")
    print("-" * 55)
    print(f"  {'Tension vs FE (Spearman rho)':<32} {rho_fe:>10.4f} {sp_fe:>12.2e}")
    print(f"  {'Tension vs Surprise (Spearman)':<32} {rho_surp:>10.4f} {sp_surp:>12.2e}")
    print("-" * 55)

    # Descriptive stats
    print("\n[5] Descriptive Statistics")
    print("-" * 55)
    print(f"  {'Metric':<20} {'Mean':>10} {'Std':>10} {'Min':>10} {'Max':>10}")
    print("-" * 55)
    for name, arr in [("Tension", tension_arr), ("Free Energy", fe_arr),
                       ("Surprise", surprise_arr), ("Complexity", complexity_arr)]:
        print(f"  {name:<20} {arr.mean():>10.4f} {arr.std():>10.4f} {arr.min():>10.4f} {arr.max():>10.4f}")
    print("-" * 55)

    # ASCII scatter (binned)
    print("\n[6] ASCII Scatter: Tension (x) vs Free Energy (y)")
    print("    (binned into 20x20 grid)")

    nx, ny = 40, 20
    t_min, t_max = np.percentile(tension_arr, [1, 99])
    f_min, f_max = np.percentile(fe_arr, [1, 99])

    grid = np.zeros((ny, nx))
    for t, f in zip(tension_arr, fe_arr):
        xi = int((t - t_min) / (t_max - t_min + 1e-10) * (nx - 1))
        yi = int((f - f_min) / (f_max - f_min + 1e-10) * (ny - 1))
        xi = max(0, min(nx-1, xi))
        yi = max(0, min(ny-1, yi))
        grid[yi][xi] += 1

    chars = " .,:;+*#@"
    max_count = grid.max()
    print(f"    FE ^")
    for row in reversed(range(ny)):
        line = "    |"
        for col in range(nx):
            idx = int(grid[row][col] / (max_count + 1) * len(chars))
            idx = min(idx, len(chars) - 1)
            line += chars[idx]
        print(line)
    print(f"    +{''.join(['-']*nx)}> Tension")
    print(f"     {t_min:.2f}{' '*(nx-12)}{t_max:.2f}")

    # Per-class analysis
    print("\n[7] Per-class Tension vs Free Energy")
    print("-" * 55)
    print(f"  {'Class':<8} {'Mean T':>10} {'Mean FE':>10} {'r':>10}")
    print("-" * 55)

    all_labels = []
    with torch.no_grad():
        for X, y in test_loader:
            all_labels.append(y.numpy())
    labels = np.concatenate(all_labels)

    class_rs = []
    for c in range(10):
        mask = labels == c
        if mask.sum() > 10:
            t_c = tension_arr[mask]
            f_c = fe_arr[mask]
            r_c, _ = stats.pearsonr(t_c, f_c)
            class_rs.append(r_c)
            print(f"  {c:<8} {t_c.mean():>10.4f} {f_c.mean():>10.4f} {r_c:>10.4f}")
    print("-" * 55)
    print(f"  {'Mean r':<8} {'':>10} {'':>10} {np.mean(class_rs):>10.4f}")

    # Verdict
    print("\n" + "=" * 65)
    threshold = 0.7
    if abs(r_fe) > threshold:
        print(f"  VERDICT: SUPPORTED (r={r_fe:.4f} > {threshold})")
        print(f"  Tension and Free Energy are strongly correlated.")
        print(f"  Isomorphism direction: higher tension = higher free energy")
    elif abs(r_fe) > 0.4:
        print(f"  VERDICT: PARTIAL (r={r_fe:.4f}, moderate correlation)")
        print(f"  Tension correlates with Free Energy but not isomorphic.")
    else:
        print(f"  VERDICT: NOT SUPPORTED (r={r_fe:.4f} < 0.4)")
        print(f"  Tension and Free Energy appear independent.")
    print("=" * 65)

    return {
        'r_fe': r_fe, 'p_fe': p_fe,
        'r_surprise': r_surp, 'r_complexity': r_comp,
        'rho_fe': rho_fe, 'mean_class_r': np.mean(class_rs),
    }


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='H-CX-413 Verification: Tension = Free Energy (Friston FEP)')
    parser.add_argument('--epochs', type=int, default=5, help='Training epochs')
    parser.add_argument('--batch-size', type=int, default=256, help='Batch size')
    args = parser.parse_args()
    main()
