#!/usr/bin/env python3
"""Dual Mechanism Quantifier — Anomaly Detection via Internal vs Inter-model Tension

H296-H307: Measures internal/inter-model tension of two independent PureFieldEngines
to quantify the separation between normal vs anomalous samples.

Usage:
  python3 calc/dual_mechanism.py --dataset mnist
  python3 calc/dual_mechanism.py --dataset fashion --normal-classes 0,1,2,3 --anomaly-classes 7,8,9
  python3 calc/dual_mechanism.py --dataset breast_cancer --epochs 20
"""

import argparse, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import torch
import torch.nn as nn
import numpy as np
from scipy import stats as scipy_stats
from model_pure_field import PureFieldEngine
from model_utils import load_mnist

# ─────────────────────────────────────────
# Data loaders
# ─────────────────────────────────────────
def load_dataset(name, normal_classes, anomaly_classes, batch_size=256):
    """Load dataset and split into normal/anomaly by class."""
    from torchvision import datasets, transforms
    if name == 'mnist':
        tfm = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))])
        train_ds = datasets.MNIST('data', train=True, download=True, transform=tfm)
        test_ds = datasets.MNIST('data', train=False, transform=tfm)
        input_dim = 784
    elif name == 'fashion':
        tfm = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.2860,), (0.3530,))])
        train_ds = datasets.FashionMNIST('data', train=True, download=True, transform=tfm)
        test_ds = datasets.FashionMNIST('data', train=False, transform=tfm)
        input_dim = 784
    elif name == 'breast_cancer':
        from sklearn.datasets import load_breast_cancer
        d = load_breast_cancer()
        X = torch.tensor(d.data, dtype=torch.float32)
        X = (X - X.mean(0)) / (X.std(0) + 1e-8)
        y = torch.tensor(d.target, dtype=torch.long)
        # 0=malignant(anomaly), 1=benign(normal)
        n = len(y)
        perm = torch.randperm(n)
        split = int(0.7 * n)
        train_X, train_y = X[perm[:split]], y[perm[:split]]
        test_X, test_y = X[perm[split:]], y[perm[split:]]
        normal_mask_tr = train_y == 1
        normal_mask_te = test_y == 1
        return train_X[normal_mask_tr], test_X, (1 - test_y).numpy(), 30
    else:
        raise ValueError(f"Unknown dataset: {name}")

    # Filter train: normal only; test: both with labels
    def extract(ds):
        imgs, labels = [], []
        for img, lbl in ds:
            imgs.append(img.view(-1))
            labels.append(lbl)
        return torch.stack(imgs), torch.tensor(labels)

    train_X, train_y = extract(train_ds)
    test_X, test_y = extract(test_ds)

    normal_set = set(normal_classes)
    anomaly_set = set(anomaly_classes)

    train_mask = torch.tensor([y.item() in normal_set for y in train_y])
    test_mask = torch.tensor([y.item() in normal_set or y.item() in anomaly_set for y in test_y])
    test_labels = torch.tensor([0 if y.item() in normal_set else 1 for y in test_y])

    return train_X[train_mask], test_X[test_mask], test_labels[test_mask].numpy(), input_dim


# ─────────────────────────────────────────
# Training
# ─────────────────────────────────────────
def train_model(train_X, input_dim, output_dim=10, hidden_dim=128, epochs=15, lr=1e-3, seed=None):
    """Train a PureFieldEngine on normal data only (minimize tension)."""
    if seed is not None:
        torch.manual_seed(seed)
    model = PureFieldEngine(input_dim, hidden_dim, output_dim)
    opt = torch.optim.Adam(model.parameters(), lr=lr)

    for ep in range(epochs):
        model.train()
        perm = torch.randperm(len(train_X))
        total_loss = 0
        for i in range(0, len(train_X), 256):
            batch = train_X[perm[i:i+256]]
            out, tension = model(batch)
            loss = tension.mean()
            opt.zero_grad(); loss.backward(); opt.step()
            total_loss += loss.item()
        if (ep + 1) % 5 == 0 or ep == 0:
            print(f"      Model ep {ep+1:>2}/{epochs}: tension={total_loss/(len(train_X)//256+1):.4f}")
    return model


# ─────────────────────────────────────────
# Tension extraction
# ─────────────────────────────────────────
def extract_tensions(model, X):
    """Return (internal_tension, engine_a_out, engine_g_out) arrays."""
    model.eval()
    with torch.no_grad():
        out_a = model.engine_a(X)
        out_g = model.engine_g(X)
        internal = ((out_a - out_g) ** 2).mean(dim=-1).numpy()
    return internal, out_a.numpy(), out_g.numpy()


def compute_auroc(scores, labels):
    """Manual AUROC via Mann-Whitney U statistic."""
    pos = scores[labels == 1]
    neg = scores[labels == 0]
    if len(pos) == 0 or len(neg) == 0:
        return 0.5
    # Use scipy for efficiency
    u_stat, _ = scipy_stats.mannwhitneyu(pos, neg, alternative='greater')
    return u_stat / (len(pos) * len(neg))


# ─────────────────────────────────────────
# ASCII visualization
# ─────────────────────────────────────────
def ascii_histogram(data_normal, data_anomaly, title, width=50, bins=20):
    """Side-by-side ASCII histogram."""
    all_data = np.concatenate([data_normal, data_anomaly])
    lo, hi = np.percentile(all_data, 1), np.percentile(all_data, 99)
    edges = np.linspace(lo, hi, bins + 1)

    h_n, _ = np.histogram(data_normal, bins=edges)
    h_a, _ = np.histogram(data_anomaly, bins=edges)
    max_count = max(h_n.max(), h_a.max(), 1)

    print(f"\n  {title}")
    print(f"  {'─' * (width + 20)}")
    for i in range(bins):
        mid = (edges[i] + edges[i+1]) / 2
        bar_n = int(h_n[i] / max_count * (width // 2))
        bar_a = int(h_a[i] / max_count * (width // 2))
        line_n = '.' * bar_n
        line_a = '#' * bar_a
        print(f"  {mid:>8.2f} | {line_n:<{width//2}} {line_a:<{width//2}}")
    print(f"  {'':>8}   {'Normal (.)':<{width//2}} {'Anomaly (#)':<{width//2}}")


def ascii_bar(labels, values, title, width=40):
    """Horizontal bar chart."""
    print(f"\n  {title}")
    print(f"  {'─' * (width + 20)}")
    max_v = max(values) if values else 1
    for lbl, v in zip(labels, values):
        bar_len = int(v / max(max_v, 0.01) * width)
        bar = '=' * bar_len
        print(f"  {lbl:<20} |{bar:<{width}}| {v:.4f}")


# ─────────────────────────────────────────
# Main
# ─────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description='Dual Mechanism Quantifier')
    parser.add_argument('--dataset', default='mnist', choices=['mnist', 'fashion', 'breast_cancer'])
    parser.add_argument('--normal-classes', default='0,1,2,3,4,5,6,7')
    parser.add_argument('--anomaly-classes', default='8,9')
    parser.add_argument('--epochs', type=int, default=15)
    args = parser.parse_args()

    normal_cls = [int(c) for c in args.normal_classes.split(',')]
    anomaly_cls = [int(c) for c in args.anomaly_classes.split(',')]

    print('=' * 60)
    print('  Dual Mechanism Quantifier (H296-H307)')
    print('=' * 60)
    print(f'  Dataset:  {args.dataset}')
    print(f'  Normal:   {normal_cls}')
    print(f'  Anomaly:  {anomaly_cls}')
    print(f'  Epochs:   {args.epochs}')

    # Load data
    train_X, test_X, test_labels, input_dim = load_dataset(
        args.dataset, normal_cls, anomaly_cls)
    n_normal = (test_labels == 0).sum()
    n_anomaly = (test_labels == 1).sum()
    print(f'  Train (normal only): {len(train_X)}')
    print(f'  Test normal: {n_normal}, anomaly: {n_anomaly}')

    output_dim = max(max(normal_cls), max(anomaly_cls)) + 1 if args.dataset != 'breast_cancer' else 2

    # Train two independent models
    print(f'\n  --- Training Model 1 (seed=42) ---')
    model1 = train_model(train_X, input_dim, output_dim, epochs=args.epochs, seed=42)
    print(f'\n  --- Training Model 2 (seed=137) ---')
    model2 = train_model(train_X, input_dim, output_dim, epochs=args.epochs, seed=137)

    # Extract tensions
    int1, a1, g1 = extract_tensions(model1, test_X)
    int2, a2, g2 = extract_tensions(model2, test_X)

    # Inter-model tension: ||model1_output - model2_output||^2
    model1.eval(); model2.eval()
    with torch.no_grad():
        out1, _ = model1(test_X)
        out2, _ = model2(test_X)
        inter_tension = ((out1 - out2) ** 2).mean(dim=-1).numpy()

    # Combined: internal_avg + inter
    internal_avg = (int1 + int2) / 2
    combined = internal_avg + inter_tension

    # Compute AUROCs
    metrics = {
        'Internal (M1)':  int1,
        'Internal (M2)':  int2,
        'Internal (avg)': internal_avg,
        'Inter-model':    inter_tension,
        'Combined':       combined,
    }
    aurocs = {}
    for name, scores in metrics.items():
        aurocs[name] = compute_auroc(scores, test_labels)

    # 2x2 matrix: mean tensions
    print('\n' + '=' * 60)
    print('  2x2 Tension Matrix (mean)')
    print('=' * 60)
    print(f'  {"":>18} | {"Normal":>12} | {"Anomaly":>12} | {"Ratio":>8}')
    print(f'  {"─"*18}-+-{"─"*12}-+-{"─"*12}-+-{"─"*8}')
    for name in ['Internal (avg)', 'Inter-model']:
        s = metrics[name]
        mn = s[test_labels == 0].mean()
        ma = s[test_labels == 1].mean()
        ratio = ma / mn if mn > 1e-8 else float('inf')
        print(f'  {name:>18} | {mn:>12.4f} | {ma:>12.4f} | {ratio:>7.2f}x')

    # AUROC table
    print('\n' + '=' * 60)
    print('  AUROC Results')
    print('=' * 60)
    for name, auc in aurocs.items():
        marker = ' <-- best' if auc == max(aurocs.values()) else ''
        print(f'  {name:<18}: {auc:.4f}{marker}')

    # Mann-Whitney U tests
    print('\n' + '=' * 60)
    print('  Mann-Whitney U Test (normal vs anomaly)')
    print('=' * 60)
    for name, scores in metrics.items():
        normal_s = scores[test_labels == 0]
        anomaly_s = scores[test_labels == 1]
        u_stat, p_val = scipy_stats.mannwhitneyu(anomaly_s, normal_s, alternative='two-sided')
        sig = '***' if p_val < 0.001 else '**' if p_val < 0.01 else '*' if p_val < 0.05 else 'ns'
        print(f'  {name:<18}: U={u_stat:>10.0f}, p={p_val:.2e} {sig}')

    # ASCII histograms
    ascii_histogram(int1[test_labels == 0], int1[test_labels == 1],
                    'Internal Tension (Model 1): Normal vs Anomaly')
    ascii_histogram(inter_tension[test_labels == 0], inter_tension[test_labels == 1],
                    'Inter-model Tension: Normal vs Anomaly')

    # AUROC bar chart
    ascii_bar(list(aurocs.keys()), list(aurocs.values()), 'AUROC Comparison')

    # Duality check
    print('\n' + '=' * 60)
    print('  Duality Check')
    print('  Expected: normal=internal_low+inter_low, anomaly=internal_high+inter_high')
    print('=' * 60)
    int_n = internal_avg[test_labels == 0].mean()
    int_a = internal_avg[test_labels == 1].mean()
    inter_n = inter_tension[test_labels == 0].mean()
    inter_a = inter_tension[test_labels == 1].mean()

    int_dir = 'UP' if int_a > int_n else 'DOWN'
    inter_dir = 'UP' if inter_a > inter_n else 'DOWN'

    print(f'  Internal: normal={int_n:.4f}, anomaly={int_a:.4f} -> anomaly {int_dir}')
    print(f'  Inter:    normal={inter_n:.4f}, anomaly={inter_a:.4f} -> anomaly {inter_dir}')

    expected = (int_a > int_n) and (inter_a > inter_n)
    print(f'\n  Dual mechanism confirmed: {"YES" if expected else "NO"}')
    if expected:
        print('  -> Both internal and inter-model tension rise for anomalies.')
        print('  -> Two independent engines agree: anomalies create tension everywhere.')
    else:
        alt = (int_a > int_n) and (inter_a < inter_n)
        if alt:
            print('  -> Alternative duality: internal UP + inter DOWN for anomalies.')
            print('  -> Anomalies stress individual models but models diverge less.')
        else:
            print(f'  -> Unexpected pattern: internal {int_dir}, inter {inter_dir}')

    # Correlation between internal and inter
    corr = np.corrcoef(internal_avg, inter_tension)[0, 1]
    print(f'\n  Correlation(internal, inter): r={corr:.4f}')
    print(f'  -> {"Complementary (low r)" if abs(corr) < 0.3 else "Redundant (high r)" if abs(corr) > 0.7 else "Moderate overlap"}')

    print('\n' + '=' * 60)


if __name__ == '__main__':
    main()