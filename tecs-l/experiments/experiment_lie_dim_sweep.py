#!/usr/bin/env python3
"""Experiment: Lie Algebra Representation Dimensions as Hidden Dims

Hypothesis (H-LIE-3):
  Exceptional Lie algebras have specific representation/adjoint dimensions:
    G2: dim = 14   (rank 2, adjoint rep)
    F4: dim = 52   (rank 4, adjoint rep)
    E6: dim = 78   (rank 6, adjoint rep)
    E7: dim = 133  (rank 7, adjoint rep)
    E8: dim = 248  (rank 8, adjoint rep)

  These are exact Lie algebra dimensions (not root counts).
  They arise from:
    dim(g) = rank + |roots|
    G2: 2 + 12 = 14
    F4: 4 + 48 = 52
    E6: 6 + 72 = 78
    E7: 7 + 126 = 133
    E8: 8 + 240 = 248

  Hypothesis: Using these as hidden_dim for neural network experts yields
  superior performance compared to standard powers of 2 {32, 64, 128, 256, 512}.

  This tests whether the combinatorial structure of maximum-symmetry Lie algebras
  has computational advantages beyond coincidence.

Experiment design:
  Part 1 (MNIST):
    - PureFieldEngine (repulsion model from model_pure_field.py) with Lie dims
    - Golden MoE (n=12, k=4) with Lie dims
    - Standard powers-of-2 baseline for both
    - Fair comparison: parameter counts normalized where possible

  Part 2 (CIFAR-10):
    - CNN backbone with Lie hidden dims vs power-of-2
    - More challenging dataset to reveal structural differences

Device: MPS (batch=64) or CPU fallback
Epochs: 10 per trial, 3 seeds
"""

import sys
import os
import time
import math

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from torchvision import datasets, transforms
from torch.utils.data import DataLoader

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))

from model_utils import load_mnist, count_params

# ─────────────────────────────────────────────────────────────
# Lie algebra dimension constants
# ─────────────────────────────────────────────────────────────
# dim(g) = rank + |root_system|
LIE_DIMS = {
    'G2 (2+12)':   14,
    'F4 (4+48)':   52,
    'E6 (6+72)':   78,
    'E7 (7+126)': 133,
    'E8 (8+240)': 248,
}

POWER2_DIMS = {
    'Pow2-16':   16,
    'Pow2-32':   32,
    'Pow2-64':   64,
    'Pow2-128': 128,
    'Pow2-256': 256,
    'Pow2-512': 512,
}

# Lie root system sizes (from Experiment 1, for MoE experts parameter)
LIE_EXPERTS = {
    'G2': 12,
    'F4': 48,
    'E6': 72,
}


# ─────────────────────────────────────────────────────────────
# Models
# ─────────────────────────────────────────────────────────────
class PureFieldEngine(nn.Module):
    """Pure repulsion field model from model_pure_field.py.
    output = engine_A(x) - engine_G(x).
    Used here with variable hidden_dim to test Lie dims.
    """

    def __init__(self, input_dim=784, hidden_dim=128, output_dim=10, dropout=0.3):
        super().__init__()
        self.engine_a = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, output_dim),
        )
        self.engine_g = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, output_dim),
        )

    def forward(self, x):
        out_a = self.engine_a(x)
        out_g = self.engine_g(x)
        output = out_a - out_g
        tension = (output ** 2).mean(dim=-1)
        return output, tension


class Expert(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim),
        )

    def forward(self, x):
        return self.net(x)


class LieMoE(nn.Module):
    """MoE with TopK gate, variable n_experts and hidden_dim."""

    def __init__(self, input_dim, hidden_dim, output_dim, n_experts=12, k=4):
        super().__init__()
        self.n_experts = n_experts
        self.k = k
        self.experts = nn.ModuleList([Expert(input_dim, hidden_dim, output_dim) for _ in range(n_experts)])
        self.gate = nn.Linear(input_dim, n_experts)

    def forward(self, x):
        scores = self.gate(x)
        topk_vals, topk_idx = scores.topk(self.k, dim=-1)
        mask = torch.zeros_like(scores).scatter(-1, topk_idx, 1.0)
        weights = F.softmax(scores, dim=-1) * mask
        weights = weights / (weights.sum(-1, keepdim=True) + 1e-8)
        outs = torch.stack([e(x) for e in self.experts], dim=1)
        return (weights.unsqueeze(-1) * outs).sum(dim=1)


# Simple CNN for CIFAR-10
class LieCNN(nn.Module):
    """Small CNN with variable hidden (FC) dimension for CIFAR-10."""

    def __init__(self, hidden_dim=128, output_dim=10):
        super().__init__()
        # Convolutional backbone: fixed
        self.conv = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1), nn.ReLU(),
            nn.MaxPool2d(2),                              # 16x16
            nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(),
            nn.MaxPool2d(2),                              # 8x8
            nn.Conv2d(64, 64, 3, padding=1), nn.ReLU(),
            nn.AdaptiveAvgPool2d(4),                      # 4x4
        )
        # Classifier with variable hidden_dim
        self.fc = nn.Sequential(
            nn.Linear(64 * 4 * 4, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim, output_dim),
        )

    def forward(self, x):
        feat = self.conv(x).flatten(1)
        return self.fc(feat)


# ─────────────────────────────────────────────────────────────
# Data loaders
# ─────────────────────────────────────────────────────────────
def load_cifar10(batch_size=64, data_dir='data'):
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])
    train_ds = datasets.CIFAR10(data_dir, train=True, download=True, transform=transform)
    test_ds = datasets.CIFAR10(data_dir, train=False, transform=transform)
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=0)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False, num_workers=0)
    return train_loader, test_loader


def get_device():
    if torch.backends.mps.is_available():
        return torch.device('mps')
    if torch.cuda.is_available():
        return torch.device('cuda')
    return torch.device('cpu')


# ─────────────────────────────────────────────────────────────
# Training helpers
# ─────────────────────────────────────────────────────────────
def train_eval_flatten(model, train_loader, test_loader, device, epochs=10, lr=1e-3):
    """Train+eval with flattened input (MNIST)."""
    model.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()

    for epoch in range(epochs):
        model.train()
        for bx, by in train_loader:
            bx = bx.view(bx.size(0), -1).to(device)
            by = by.to(device)
            optimizer.zero_grad()
            out = model(bx)
            if isinstance(out, tuple):
                out = out[0]
            loss = criterion(out, by)
            loss.backward()
            optimizer.step()

    model.eval()
    correct = total = 0
    final_loss = 0.0
    with torch.no_grad():
        for bx, by in test_loader:
            bx = bx.view(bx.size(0), -1).to(device)
            by = by.to(device)
            out = model(bx)
            if isinstance(out, tuple):
                out = out[0]
            final_loss += criterion(out, by).item()
            correct += (out.argmax(-1) == by).sum().item()
            total += by.size(0)
    return correct / total * 100.0, final_loss / len(test_loader)


def train_eval_cnn(model, train_loader, test_loader, device, epochs=10, lr=1e-3):
    """Train+eval for CNN (CIFAR-10, 2D input)."""
    model.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()

    for epoch in range(epochs):
        model.train()
        for bx, by in train_loader:
            bx = bx.to(device)
            by = by.to(device)
            optimizer.zero_grad()
            out = model(bx)
            loss = criterion(out, by)
            loss.backward()
            optimizer.step()

    model.eval()
    correct = total = 0
    final_loss = 0.0
    with torch.no_grad():
        for bx, by in test_loader:
            bx = bx.to(device)
            by = by.to(device)
            out = model(bx)
            final_loss += criterion(out, by).item()
            correct += (out.argmax(-1) == by).sum().item()
            total += by.size(0)
    return correct / total * 100.0, final_loss / len(test_loader)


def multi_seed_run(model_fn, train_fn, train_loader, test_loader, device,
                   epochs=10, seeds=(42, 137, 256)):
    accs, losses = [], []
    for seed in seeds:
        torch.manual_seed(seed)
        np.random.seed(seed)
        model = model_fn()
        acc, loss = train_fn(model, train_loader, test_loader, device, epochs=epochs)
        accs.append(acc)
        losses.append(loss)
        print(f"    seed={seed}  acc={acc:.2f}%  loss={loss:.4f}")
    return np.mean(accs), np.std(accs), np.mean(losses)


# ─────────────────────────────────────────────────────────────
# Reporting
# ─────────────────────────────────────────────────────────────
def ascii_bar(value, lo, hi, width=40):
    if hi <= lo:
        return '#' * width
    bar_len = max(0, min(width, int((value - lo) / (hi - lo) * width)))
    return '#' * bar_len + '.' * (width - bar_len)


def print_dim_table(results, title):
    print(f"\n--- Markdown Table: {title} ---")
    print("| dim | group | mean_acc% | std_acc | mean_loss | params |")
    print("|-----|-------|-----------|---------|-----------|--------|")
    for r in sorted(results, key=lambda x: x['dim']):
        print(f"| {r['dim']} | {r['group']} | {r['mean_acc']:.2f} | {r['std_acc']:.2f} | {r['mean_loss']:.4f} | {r['params']:,} |")


def print_dim_chart(results, title):
    accs = [r['mean_acc'] for r in results]
    lo, hi = min(accs), max(accs)
    print(f"\nASCII Chart: Hidden Dim vs Accuracy — {title}")
    print("=" * 70)
    for r in sorted(results, key=lambda x: x['dim']):
        bar = ascii_bar(r['mean_acc'], lo, hi)
        group_tag = '[LIE]' if r['group'] == 'lie' else '[P2 ]'
        print(f"  {group_tag} dim={r['dim']:4d} ({r['name'][:12]:12s}) |{bar}| {r['mean_acc']:.2f}%")


def group_analysis(results, title):
    lie_r = [r for r in results if r['group'] == 'lie']
    p2_r = [r for r in results if r['group'] == 'power2']
    print(f"\nGroup Analysis: {title}")
    print("-" * 60)
    if lie_r:
        lie_mean = np.mean([r['mean_acc'] for r in lie_r])
        lie_dims = [r['dim'] for r in lie_r]
        best_lie = max(lie_r, key=lambda r: r['mean_acc'])
        print(f"  Lie dims {lie_dims}: mean acc = {lie_mean:.2f}%  best = {best_lie['name']} ({best_lie['mean_acc']:.2f}%)")
    if p2_r:
        p2_mean = np.mean([r['mean_acc'] for r in p2_r])
        p2_dims = [r['dim'] for r in p2_r]
        best_p2 = max(p2_r, key=lambda r: r['mean_acc'])
        print(f"  P2  dims {p2_dims}: mean acc = {p2_mean:.2f}%  best = {best_p2['name']} ({best_p2['mean_acc']:.2f}%)")
    if lie_r and p2_r:
        delta = np.mean([r['mean_acc'] for r in lie_r]) - np.mean([r['mean_acc'] for r in p2_r])
        print(f"  Delta (Lie - Power2): {delta:+.2f}%")
        if delta > 0:
            print("  VERDICT: Lie dims OUTPERFORM power-of-2  -> H-LIE-3 SUPPORTED")
        else:
            print("  VERDICT: Power-of-2 dims match or outperform -> H-LIE-3 NOT CONFIRMED")


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────
def main():
    t0 = time.time()
    device = get_device()
    data_dir = os.path.join(_HERE, '..', 'data')

    print("=" * 72)
    print("  Experiment: Lie Algebra Representation Dims as Hidden Dims")
    print("  G2=14, F4=52, E6=78, E7=133, E8=248  vs  {16,32,64,128,256,512}")
    print("=" * 72)
    print(f"\n  Device: {device}")
    print(f"  dim(g) = rank + |root_system|")
    print(f"  G2: 2+12=14   F4: 4+48=52   E6: 6+72=78   E7: 7+126=133   E8: 8+240=248")

    print("\n  Loading MNIST ...", end=" ", flush=True)
    mnist_train, mnist_test = load_mnist(batch_size=64, data_dir=data_dir)
    print("done.")

    EPOCHS = 10
    INPUT_DIM = 784
    OUTPUT_DIM = 10

    # ────────────────────────────────────────────────
    # Part 1A: PureFieldEngine on MNIST with Lie dims
    # ────────────────────────────────────────────────
    print("\n" + "=" * 72)
    print("Part 1A: PureFieldEngine (repulsion) — MNIST — hidden_dim sweep")
    print("=" * 72)

    pfe_results = []

    all_dims = {**{f'LIE-{k}': v for k, v in LIE_DIMS.items()},
                **{k: v for k, v in POWER2_DIMS.items()}}

    for name, dim in sorted(all_dims.items(), key=lambda x: x[1]):
        group = 'lie' if name.startswith('LIE') else 'power2'
        print(f"\n  [{name}] dim={dim}")
        mean_acc, std_acc, mean_loss = multi_seed_run(
            lambda d=dim: PureFieldEngine(INPUT_DIM, d, OUTPUT_DIM),
            train_eval_flatten, mnist_train, mnist_test, device, epochs=EPOCHS
        )
        params = count_params(PureFieldEngine(INPUT_DIM, dim, OUTPUT_DIM))
        pfe_results.append({
            'name': name, 'dim': dim, 'group': group,
            'mean_acc': mean_acc, 'std_acc': std_acc, 'mean_loss': mean_loss,
            'params': params,
        })

    print_dim_table(pfe_results, "PureFieldEngine MNIST")
    print_dim_chart(pfe_results, "PureFieldEngine MNIST")
    group_analysis(pfe_results, "PureFieldEngine MNIST")

    # ────────────────────────────────────────────────
    # Part 1B: Golden MoE (n=12, k=4) on MNIST with Lie dims
    # ────────────────────────────────────────────────
    print("\n" + "=" * 72)
    print("Part 1B: Golden MoE (n=12, k=4) — MNIST — hidden_dim sweep")
    print("         n=12=sigma(6)=|G2|, k=4=tau(6), active ratio=1/3")
    print("=" * 72)

    moe_results = []
    N_EXPERTS = 12
    K_ACTIVE = 4

    # Only up to dim=128 to keep runtime reasonable for large dims
    dims_moe = {k: v for k, v in all_dims.items() if v <= 133}

    for name, dim in sorted(dims_moe.items(), key=lambda x: x[1]):
        group = 'lie' if name.startswith('LIE') else 'power2'
        print(f"\n  [{name}] dim={dim}")
        mean_acc, std_acc, mean_loss = multi_seed_run(
            lambda d=dim: LieMoE(INPUT_DIM, d, OUTPUT_DIM, n_experts=N_EXPERTS, k=K_ACTIVE),
            train_eval_flatten, mnist_train, mnist_test, device, epochs=EPOCHS
        )
        params = count_params(LieMoE(INPUT_DIM, dim, OUTPUT_DIM, n_experts=N_EXPERTS, k=K_ACTIVE))
        moe_results.append({
            'name': name, 'dim': dim, 'group': group,
            'mean_acc': mean_acc, 'std_acc': std_acc, 'mean_loss': mean_loss,
            'params': params,
        })

    print_dim_table(moe_results, "Golden MoE MNIST (n=12, k=4)")
    print_dim_chart(moe_results, "Golden MoE MNIST (n=12,k=4)")
    group_analysis(moe_results, "Golden MoE MNIST (n=12,k=4)")

    # ────────────────────────────────────────────────
    # Part 2: CNN on CIFAR-10 with Lie dims
    # ────────────────────────────────────────────────
    print("\n" + "=" * 72)
    print("Part 2: LieCNN — CIFAR-10 — FC hidden_dim sweep")
    print("        (CNN backbone fixed; only FC hidden layer varies)")
    print("=" * 72)

    print("\n  Loading CIFAR-10 ...", end=" ", flush=True)
    cifar_train, cifar_test = load_cifar10(batch_size=64, data_dir=data_dir)
    print("done.")

    cnn_results = []

    for name, dim in sorted(all_dims.items(), key=lambda x: x[1]):
        group = 'lie' if name.startswith('LIE') else 'power2'
        print(f"\n  [{name}] dim={dim}")
        mean_acc, std_acc, mean_loss = multi_seed_run(
            lambda d=dim: LieCNN(hidden_dim=d, output_dim=10),
            train_eval_cnn, cifar_train, cifar_test, device, epochs=EPOCHS
        )
        params = count_params(LieCNN(hidden_dim=dim))
        cnn_results.append({
            'name': name, 'dim': dim, 'group': group,
            'mean_acc': mean_acc, 'std_acc': std_acc, 'mean_loss': mean_loss,
            'params': params,
        })

    print_dim_table(cnn_results, "LieCNN CIFAR-10")
    print_dim_chart(cnn_results, "LieCNN CIFAR-10")
    group_analysis(cnn_results, "LieCNN CIFAR-10")

    # ────────────────────────────────────────────────
    # Combined summary
    # ────────────────────────────────────────────────
    elapsed = time.time() - t0

    print("\n" + "=" * 72)
    print("FINAL SUMMARY — H-LIE-3: Lie dims vs Power-of-2 dims")
    print("=" * 72)
    print(f"  Total time: {elapsed:.1f}s\n")

    for results, label in [(pfe_results, "PureField MNIST"), (moe_results, "MoE MNIST"), (cnn_results, "CNN CIFAR")]:
        lie_r = [r for r in results if r['group'] == 'lie']
        p2_r = [r for r in results if r['group'] == 'power2']
        if not lie_r or not p2_r:
            continue
        lie_mean = np.mean([r['mean_acc'] for r in lie_r])
        p2_mean = np.mean([r['mean_acc'] for r in p2_r])
        delta = lie_mean - p2_mean
        verdict = "SUPPORTED" if delta > 0 else "NOT CONFIRMED"
        print(f"  {label:20s}: Lie={lie_mean:.2f}%  P2={p2_mean:.2f}%  delta={delta:+.2f}%  [{verdict}]")

    print()
    # Check specific predictions: G2 dim=14 vs nearest P2
    g2_r_pfe = next((r for r in pfe_results if r['dim'] == 14), None)
    p2_16_pfe = next((r for r in pfe_results if r['dim'] == 16), None)
    if g2_r_pfe and p2_16_pfe:
        delta = g2_r_pfe['mean_acc'] - p2_16_pfe['mean_acc']
        print(f"  G2(14) vs Pow2(16) on PureField MNIST: {delta:+.2f}%")

    e6_r_pfe = next((r for r in pfe_results if r['dim'] == 78), None)
    p2_64_pfe = next((r for r in pfe_results if r['dim'] == 64), None)
    p2_128_pfe = next((r for r in pfe_results if r['dim'] == 128), None)
    if e6_r_pfe and p2_64_pfe and p2_128_pfe:
        best_p2_neighbor = max(p2_64_pfe['mean_acc'], p2_128_pfe['mean_acc'])
        delta = e6_r_pfe['mean_acc'] - best_p2_neighbor
        print(f"  E6(78) vs best P2 neighbor {{{64},{128}}} on PureField MNIST: {delta:+.2f}%")

    print("\n  Note: H-LIE-3 requires all three datasets to confirm.")
    print("        See markdown tables above for per-dim breakdown.")
    print("=" * 72)


if __name__ == '__main__':
    main()
