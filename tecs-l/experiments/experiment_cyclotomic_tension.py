#!/usr/bin/env python3
"""H-CX-343: Cyclotomic Polynomial Phi_6(x) = x^2 - x + 1 in Tension Dynamics

Hypothesis: The 6th cyclotomic polynomial governs tension ratio dynamics.
- Phi_6(x) = x^2 - x + 1, roots are e^{+/- i*pi/3} (|root| = 1)
- If tension ratios r_n = t_{n+1}/t_n converge to |root|=1, dynamics are cyclotomic
- Period-6 oscillation would connect to 6th roots of unity
- Cross-validated on MNIST, Fashion-MNIST, CIFAR-10

Texas Sharpshooter: compare observed Phi_6 residuals against random polynomials.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import numpy as np
from model_pure_field import PureFieldEngine

# ─────────────────────────────────────────
# Data loaders
# ─────────────────────────────────────────
def load_mnist(batch_size=64):
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    train_ds = datasets.MNIST('data', train=True, download=True, transform=transform)
    test_ds = datasets.MNIST('data', train=False, transform=transform)
    return (DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=0),
            DataLoader(test_ds, batch_size=batch_size, shuffle=False, num_workers=0))


def load_fashion_mnist(batch_size=64):
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.2860,), (0.3530,))
    ])
    train_ds = datasets.FashionMNIST('data', train=True, download=True, transform=transform)
    test_ds = datasets.FashionMNIST('data', train=False, transform=transform)
    return (DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=0),
            DataLoader(test_ds, batch_size=batch_size, shuffle=False, num_workers=0))


def load_cifar10(batch_size=64):
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])
    train_ds = datasets.CIFAR10('data', train=True, download=True, transform=transform)
    test_ds = datasets.CIFAR10('data', train=False, transform=transform)
    return (DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=0),
            DataLoader(test_ds, batch_size=batch_size, shuffle=False, num_workers=0))


# ─────────────────────────────────────────
# Training with tension tracking
# ─────────────────────────────────────────
def train_with_tension_tracking(model, train_loader, test_loader, epochs=10,
                                 lr=0.001, flatten=True):
    """Train PureFieldEngine and record per-epoch mean tension."""
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()

    epoch_data = []

    for epoch in range(epochs):
        model.train()
        total_loss = 0
        all_tensions = []
        n_batches = 0

        for X, y in train_loader:
            if flatten:
                X = X.view(X.size(0), -1)
            optimizer.zero_grad()
            logits, tension = model(X)
            # Use mean tension as aux loss (weight 0.1)
            loss = criterion(logits, y) + 0.1 * tension.mean()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()
            all_tensions.append(tension.mean().item())
            n_batches += 1

        avg_loss = total_loss / n_batches
        mean_tension = np.mean(all_tensions)

        # Evaluate
        model.eval()
        correct = total = 0
        eval_tensions = []
        with torch.no_grad():
            for X, y in test_loader:
                if flatten:
                    X = X.view(X.size(0), -1)
                logits, tension = model(X)
                correct += (logits.argmax(1) == y).sum().item()
                total += y.size(0)
                eval_tensions.append(tension.mean().item())

        acc = correct / total
        eval_tension = np.mean(eval_tensions)

        epoch_data.append({
            'epoch': epoch + 1,
            'loss': avg_loss,
            'accuracy': acc,
            'train_tension': mean_tension,
            'eval_tension': eval_tension,
        })

    return epoch_data


# ─────────────────────────────────────────
# Cyclotomic analysis
# ─────────────────────────────────────────
def phi6(x):
    """Phi_6(x) = x^2 - x + 1"""
    return x**2 - x + 1


def analyze_cyclotomic(epoch_data, dataset_name):
    """Analyze tension ratios for cyclotomic structure."""
    tensions = [d['train_tension'] for d in epoch_data]
    accs = [d['accuracy'] for d in epoch_data]

    # Compute tension ratios r_n = t_{n+1} / t_n
    ratios = []
    for i in range(len(tensions) - 1):
        if tensions[i] > 1e-10:
            ratios.append(tensions[i + 1] / tensions[i])
        else:
            ratios.append(float('nan'))

    # Phi_6 residuals: how close is Phi_6(r_n) to 0?
    phi6_residuals = [phi6(r) for r in ratios if not np.isnan(r)]

    # |r_n| convergence to 1 (root magnitude)
    ratio_deviations = [abs(r - 1.0) for r in ratios if not np.isnan(r)]

    # Period-6 analysis: autocorrelation at lag 6
    if len(ratios) >= 7:
        ratios_clean = [r for r in ratios if not np.isnan(r)]
        if len(ratios_clean) >= 7:
            mean_r = np.mean(ratios_clean)
            var_r = np.var(ratios_clean)
            if var_r > 1e-15:
                autocorr_6 = np.mean([(ratios_clean[i] - mean_r) * (ratios_clean[i-6] - mean_r)
                                       for i in range(6, len(ratios_clean))]) / var_r
            else:
                autocorr_6 = 0.0
        else:
            autocorr_6 = float('nan')
    else:
        autocorr_6 = float('nan')

    # Fit: least squares for a*x^2 + b*x + c to ratios
    # Compare with Phi_6 coefficients (1, -1, 1)
    if len(ratios) >= 3:
        valid_ratios = [r for r in ratios if not np.isnan(r)]
        x_vals = np.arange(len(valid_ratios))
        if len(valid_ratios) >= 3:
            coeffs = np.polyfit(x_vals, valid_ratios, 2)
        else:
            coeffs = [0, 0, 0]
    else:
        coeffs = [0, 0, 0]

    return {
        'dataset': dataset_name,
        'tensions': tensions,
        'ratios': ratios,
        'phi6_residuals': phi6_residuals,
        'ratio_deviations': ratio_deviations,
        'mean_phi6_residual': np.mean(np.abs(phi6_residuals)) if phi6_residuals else float('nan'),
        'mean_ratio_deviation': np.mean(ratio_deviations) if ratio_deviations else float('nan'),
        'final_ratio': ratios[-1] if ratios and not np.isnan(ratios[-1]) else float('nan'),
        'autocorr_6': autocorr_6,
        'poly_fit_coeffs': coeffs,
        'accuracies': accs,
    }


# ─────────────────────────────────────────
# Texas Sharpshooter
# ─────────────────────────────────────────
def texas_sharpshooter(results, n_random=10000):
    """Compare Phi_6 residual fit vs random degree-2 polynomials."""
    # Observed: mean |Phi_6(r)| across all datasets
    all_residuals = []
    all_ratios = []
    for r in results:
        all_residuals.extend([abs(x) for x in r['phi6_residuals']])
        all_ratios.extend([x for x in r['ratios'] if not np.isnan(x)])

    if not all_residuals or not all_ratios:
        return {'p_value': 1.0, 'observed': float('nan'), 'random_mean': float('nan')}

    observed_score = np.mean(all_residuals)
    ratios_arr = np.array(all_ratios)

    # Generate random degree-2 polynomials and compute residuals
    rng = np.random.default_rng(42)
    count_better = 0
    random_scores = []

    for _ in range(n_random):
        # Random coefficients in [-2, 2]
        a, b, c = rng.uniform(-2, 2, 3)
        rand_residuals = np.abs(a * ratios_arr**2 + b * ratios_arr + c)
        score = np.mean(rand_residuals)
        random_scores.append(score)
        if score <= observed_score:
            count_better += 1

    p_value = count_better / n_random
    random_scores = np.array(random_scores)

    return {
        'p_value': p_value,
        'observed': observed_score,
        'random_mean': np.mean(random_scores),
        'random_std': np.std(random_scores),
        'z_score': (observed_score - np.mean(random_scores)) / (np.std(random_scores) + 1e-15),
        'n_random': n_random,
    }


# ─────────────────────────────────────────
# ASCII graph
# ─────────────────────────────────────────
def ascii_graph(title, series_dict, width=60, height=15):
    """Print ASCII graph. series_dict: {label: [values]}"""
    print(f"\n  {title}")
    print(f"  {'=' * (width + 10)}")

    all_vals = []
    for vals in series_dict.values():
        all_vals.extend([v for v in vals if not np.isnan(v)])
    if not all_vals:
        print("  (no data)")
        return

    vmin = min(all_vals)
    vmax = max(all_vals)
    if vmax - vmin < 1e-10:
        vmax = vmin + 1

    symbols = ['*', 'o', '+', '#', 'x']

    # Print legend
    for i, (label, vals) in enumerate(series_dict.items()):
        sym = symbols[i % len(symbols)]
        print(f"  {sym} = {label}")

    print()
    for row in range(height - 1, -1, -1):
        y_val = vmin + (vmax - vmin) * row / (height - 1)
        line = f"  {y_val:>8.4f} |"
        max_len = max(len(v) for v in series_dict.values())
        chars = [' '] * max_len

        for i, (label, vals) in enumerate(series_dict.items()):
            sym = symbols[i % len(symbols)]
            for j, v in enumerate(vals):
                if np.isnan(v):
                    continue
                v_row = round((v - vmin) / (vmax - vmin) * (height - 1))
                if v_row == row:
                    chars[j] = sym

        col_width = max(1, width // max_len)
        line += ''.join(c.center(col_width) for c in chars[:max_len])
        print(line)

    # X-axis
    max_len = max(len(v) for v in series_dict.values())
    col_width = max(1, width // max_len)
    print(f"  {'':>8} +{''.join(str(i+1).center(col_width) for i in range(max_len))}")
    print(f"  {'':>8}  {'Epoch'.center(width)}")


# ─────────────────────────────────────────
# Main
# ─────────────────────────────────────────
def main():
    print("=" * 70)
    print("  H-CX-343: Cyclotomic Polynomial Phi_6(x) in Tension Dynamics")
    print("  Phi_6(x) = x^2 - x + 1 (6th cyclotomic polynomial)")
    print("  Roots: e^{+/-i*pi/3}, |root| = 1")
    print("=" * 70)

    torch.manual_seed(42)
    np.random.seed(42)

    datasets_config = [
        ('MNIST', load_mnist, 784, True),
        ('Fashion-MNIST', load_fashion_mnist, 784, True),
        ('CIFAR-10', load_cifar10, 3072, True),
    ]

    all_results = []
    all_epoch_data = {}

    for ds_name, loader_fn, input_dim, flatten in datasets_config:
        print(f"\n{'─' * 70}")
        print(f"  Dataset: {ds_name} (input_dim={input_dim})")
        print(f"{'─' * 70}")

        train_loader, test_loader = loader_fn(batch_size=64)
        model = PureFieldEngine(input_dim=input_dim, hidden_dim=128, output_dim=10)
        n_params = sum(p.numel() for p in model.parameters())
        print(f"  Parameters: {n_params:,}")

        epoch_data = train_with_tension_tracking(
            model, train_loader, test_loader, epochs=10, lr=0.001, flatten=flatten
        )
        all_epoch_data[ds_name] = epoch_data

        # Per-epoch table
        print(f"\n  | Epoch | Loss     | Accuracy | Train Tension | Eval Tension | Ratio r_n |")
        print(f"  |-------|----------|----------|---------------|--------------|-----------|")
        for i, d in enumerate(epoch_data):
            if i > 0:
                ratio = d['train_tension'] / epoch_data[i-1]['train_tension'] if epoch_data[i-1]['train_tension'] > 1e-10 else float('nan')
            else:
                ratio = float('nan')
            ratio_str = f"{ratio:.6f}" if not np.isnan(ratio) else "---"
            print(f"  | {d['epoch']:>5} | {d['loss']:.4f}   | {d['accuracy']*100:>6.2f}%  "
                  f"| {d['train_tension']:>13.6f} | {d['eval_tension']:>12.6f} | {ratio_str:>9} |")

        result = analyze_cyclotomic(epoch_data, ds_name)
        all_results.append(result)

        # Phi_6 residuals
        print(f"\n  Phi_6(r_n) residuals:")
        print(f"  | Epoch Pair | r_n      | Phi_6(r_n) | |Phi_6(r_n)| | |r_n - 1| |")
        print(f"  |------------|----------|------------|-------------|----------|")
        for i, (r, p6) in enumerate(zip(result['ratios'], result['phi6_residuals'])):
            if not np.isnan(r):
                print(f"  | {i+1}->{i+2:>2}     | {r:.6f} | {p6:>+10.6f} | {abs(p6):>11.6f} | {abs(r-1):.6f} |")

        print(f"\n  Summary for {ds_name}:")
        print(f"    Mean |Phi_6(r_n)|:     {result['mean_phi6_residual']:.6f}")
        print(f"    Mean |r_n - 1|:        {result['mean_ratio_deviation']:.6f}")
        print(f"    Final ratio r_9:       {result['final_ratio']:.6f}")
        print(f"    Autocorrelation lag-6: {result['autocorr_6']}")
        print(f"    Poly fit coeffs (a,b,c): {result['poly_fit_coeffs']}")

    # ─────────────────────────────────────────
    # Cross-dataset comparison
    # ─────────────────────────────────────────
    print(f"\n{'=' * 70}")
    print(f"  Cross-Dataset Comparison")
    print(f"{'=' * 70}")
    print(f"\n  | Dataset       | Mean |Phi_6(r)| | Mean |r-1| | Final r_9 | Final Acc | AutoCorr-6 |")
    print(f"  |---------------|-----------------|-------------|-----------|-----------|------------|")
    for r in all_results:
        ac6_str = f"{r['autocorr_6']:.4f}" if not np.isnan(r['autocorr_6']) else "N/A"
        print(f"  | {r['dataset']:<13} | {r['mean_phi6_residual']:>15.6f} | {r['mean_ratio_deviation']:>11.6f} "
              f"| {r['final_ratio']:>9.6f} | {r['accuracies'][-1]*100:>7.2f}%  | {ac6_str:>10} |")

    # ─────────────────────────────────────────
    # Convergence to |root|=1 analysis
    # ─────────────────────────────────────────
    print(f"\n{'=' * 70}")
    print(f"  Convergence Analysis: Do ratios converge to |root|=1?")
    print(f"{'=' * 70}")
    for r in all_results:
        ratios = [x for x in r['ratios'] if not np.isnan(x)]
        if len(ratios) >= 4:
            first_half = ratios[:len(ratios)//2]
            second_half = ratios[len(ratios)//2:]
            dev_first = np.mean([abs(x - 1.0) for x in first_half])
            dev_second = np.mean([abs(x - 1.0) for x in second_half])
            converging = dev_second < dev_first
            print(f"\n  {r['dataset']}:")
            print(f"    First half  mean |r-1|: {dev_first:.6f}")
            print(f"    Second half mean |r-1|: {dev_second:.6f}")
            print(f"    Converging to 1?  {'YES' if converging else 'NO'} (ratio: {dev_second/dev_first:.4f})")

    # ─────────────────────────────────────────
    # ASCII Graphs
    # ─────────────────────────────────────────
    # Graph 1: Tension ratios
    ratio_series = {}
    for r in all_results:
        ratio_series[r['dataset']] = r['ratios']
    ascii_graph("Tension Ratios r_n = t_{n+1}/t_n by Dataset", ratio_series)

    # Graph 2: |Phi_6(r_n)| residuals
    residual_series = {}
    for r in all_results:
        residual_series[r['dataset']] = [abs(x) for x in r['phi6_residuals']]
    ascii_graph("|Phi_6(r_n)| Residuals by Dataset", residual_series)

    # Graph 3: Tensions
    tension_series = {}
    for r in all_results:
        tension_series[r['dataset']] = r['tensions']
    ascii_graph("Mean Tension by Epoch", tension_series)

    # ─────────────────────────────────────────
    # Texas Sharpshooter
    # ─────────────────────────────────────────
    print(f"\n{'=' * 70}")
    print(f"  Texas Sharpshooter Test")
    print(f"  H0: Phi_6 residuals are no better than random degree-2 polynomials")
    print(f"{'=' * 70}")

    texas = texas_sharpshooter(all_results, n_random=10000)

    print(f"\n  Observed mean |Phi_6(r)|:  {texas['observed']:.6f}")
    print(f"  Random mean (10000 poly):  {texas['random_mean']:.6f} +/- {texas['random_std']:.6f}")
    print(f"  Z-score:                   {texas['z_score']:.4f}")
    print(f"  p-value:                   {texas['p_value']:.4f}")

    if texas['p_value'] < 0.01:
        grade = "STRUCTURAL (p < 0.01)"
    elif texas['p_value'] < 0.05:
        grade = "WEAK EVIDENCE (p < 0.05)"
    else:
        grade = "COINCIDENCE (p > 0.05)"
    print(f"  Verdict:                   {grade}")

    # ─────────────────────────────────────────
    # Final verdict
    # ─────────────────────────────────────────
    print(f"\n{'=' * 70}")
    print(f"  H-CX-343 Final Verdict")
    print(f"{'=' * 70}")

    # Check all three criteria
    all_converge = all(
        np.mean([abs(x - 1.0) for x in r['ratios'][len(r['ratios'])//2:] if not np.isnan(x)]) <
        np.mean([abs(x - 1.0) for x in r['ratios'][:len(r['ratios'])//2] if not np.isnan(x)])
        for r in all_results if len([x for x in r['ratios'] if not np.isnan(x)]) >= 4
    )

    mean_phi6_all = np.mean([r['mean_phi6_residual'] for r in all_results])
    mean_dev_all = np.mean([r['mean_ratio_deviation'] for r in all_results])

    print(f"\n  1. Ratios converge to |root|=1?      {'YES' if all_converge else 'NO'}")
    print(f"  2. Mean |Phi_6(r)| across datasets:   {mean_phi6_all:.6f}")
    print(f"  3. Mean |r-1| across datasets:        {mean_dev_all:.6f}")
    print(f"  4. Texas p-value:                     {texas['p_value']:.4f}")
    autocorr_strs = []
    for r in all_results:
        val = r['autocorr_6']
        autocorr_strs.append(f'{val:.4f}' if not np.isnan(val) else 'N/A')
    print(f"  5. Period-6 autocorrelation:          {autocorr_strs}")

    # Interpretation
    if mean_dev_all < 0.05 and texas['p_value'] < 0.01:
        print(f"\n  STRONG: Tension ratios converge to 1 (cyclotomic root magnitude)")
        print(f"  and Phi_6 fit is statistically significant.")
    elif mean_dev_all < 0.1 and texas['p_value'] < 0.05:
        print(f"\n  MODERATE: Some cyclotomic structure detected but weak.")
    else:
        print(f"\n  WEAK/NONE: Tension ratios {'converge to 1' if all_converge else 'do not converge to 1'}.")
        print(f"  Note: convergence to r=1 is expected for any stabilizing training process.")
        print(f"  The key question is whether Phi_6 specifically fits better than arbitrary polynomials.")
        if texas['p_value'] > 0.05:
            print(f"  Texas test says NO (p={texas['p_value']:.4f}) -- likely coincidence.")

    print(f"\n{'=' * 70}")
    print(f"  Experiment complete.")
    print(f"{'=' * 70}")


if __name__ == '__main__':
    main()
