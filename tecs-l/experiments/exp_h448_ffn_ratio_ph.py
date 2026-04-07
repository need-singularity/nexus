#!/usr/bin/env python3
"""H-CX-448: FFN Expansion Ratio and PH Topology

H-EE-12 confirmed: 4/3 FFN ratio is efficiency-optimal.
Question: Does the optimal ratio show a TOPOLOGICAL signature?

Hypothesis: The 4/3 ratio produces the most structured PH (lowest H0 lifetime
per accuracy) — meaning it creates the most efficient class separation topology.

Test: Train identical transformers with FFN ratios {1.0, 1.33, 2.0, 4.0},
measure PH H0 at convergence, compare H0/accuracy efficiency.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch, torch.nn as nn, torch.nn.functional as F, numpy as np
from scipy.stats import pearsonr
from torchvision import datasets, transforms


def load_mnist(bs=256):
    t = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.1307,),(0.3081,))])
    tr = torch.utils.data.DataLoader(datasets.MNIST('~/.cache/mnist', train=True, download=True, transform=t), batch_size=bs, shuffle=True)
    te = torch.utils.data.DataLoader(datasets.MNIST('~/.cache/mnist', train=False, transform=t), batch_size=bs)
    return tr, te


class SimpleFFN(nn.Module):
    """MLP with configurable FFN expansion ratio."""
    def __init__(self, input_dim=784, hidden_dim=128, output_dim=10, ffn_ratio=4.0):
        super().__init__()
        ffn_dim = int(hidden_dim * ffn_ratio)
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim), nn.ReLU(), nn.Dropout(0.1))
        self.ffn = nn.Sequential(
            nn.Linear(hidden_dim, ffn_dim), nn.GELU(), nn.Linear(ffn_dim, hidden_dim))
        self.head = nn.Linear(hidden_dim, output_dim)

    def forward(self, x):
        h = self.encoder(x)
        h = h + self.ffn(h)  # residual
        return self.head(h)


def ph_h0(cos_dist):
    n = len(cos_dist)
    parent = list(range(n))
    def find(x):
        while parent[x] != x: parent[x] = parent[parent[x]]; x = parent[x]
        return x
    edges = sorted([(cos_dist[i,j], i, j) for i in range(n) for j in range(i+1, n)])
    total = 0.0
    for d, i, j in edges:
        ri, rj = find(i), find(j)
        if ri != rj: total += d; parent[ri] = rj
    return total


def class_cosine_dist(reps, labels, n_cls=10):
    means = []
    for c in range(n_cls):
        mask = labels == c
        if mask.sum() > 0:
            m = reps[mask].mean(0)
            n = np.linalg.norm(m)
            means.append(m / max(n, 1e-8))
        else:
            means.append(np.zeros(reps.shape[1]))
    means = np.array(means)
    cos_dist = np.clip(1 - means @ means.T, 0, 2)
    np.fill_diagonal(cos_dist, 0)
    return cos_dist


def main():
    print("=" * 70)
    print("  H-CX-448: FFN Expansion Ratio and PH Topology")
    print("=" * 70)

    torch.manual_seed(42)
    tr, te = load_mnist()

    ratios = [1.0, 4/3, 1.5, 2.0, 3.0, 4.0]
    results = {}

    for ratio in ratios:
        print(f"\n  --- FFN ratio = {ratio:.2f} ---")
        torch.manual_seed(42)
        model = SimpleFFN(ffn_ratio=ratio)
        n_params = sum(p.numel() for p in model.parameters())
        opt = torch.optim.Adam(model.parameters(), lr=1e-3)
        ce = nn.CrossEntropyLoss()

        for ep in range(1, 11):
            model.train()
            for x, y in tr:
                opt.zero_grad()
                out = model(x.view(-1, 784))
                ce(out, y).backward()
                opt.step()

        # Evaluate
        model.eval()
        all_h, all_y = [], []
        correct, total = 0, 0
        with torch.no_grad():
            for x, y in te:
                h = model.encoder(x.view(-1, 784))
                h = h + model.ffn(h)
                all_h.append(F.normalize(h, dim=-1).numpy())
                all_y.append(y.numpy())
                out = model.head(h)
                correct += (out.argmax(1) == y).sum().item()
                total += len(y)

        reps = np.concatenate(all_h)
        labels = np.concatenate(all_y)
        cos_dist = class_cosine_dist(reps, labels)
        h0 = ph_h0(cos_dist)
        acc = correct / total * 100

        # Efficiency metrics
        eff_loss_params = (1 - acc/100) * n_params / 1e6  # lower better
        eff_h0_acc = h0 / (acc/100)  # PH per accuracy (lower = more efficient topology)

        results[ratio] = {
            'acc': acc, 'h0': h0, 'params': n_params,
            'eff_loss_params': eff_loss_params, 'eff_h0_acc': eff_h0_acc
        }
        print(f"    acc={acc:.2f}%  H0={h0:.4f}  params={n_params:,}  eff(loss*params)={eff_loss_params:.4f}")

    # Summary table
    print(f"\n{'='*70}")
    print(f"  SUMMARY TABLE")
    print(f"{'='*70}")
    print(f"\n  {'Ratio':>6} | {'Accuracy':>8} | {'PH H0':>7} | {'Params':>8} | {'Loss*Params':>11} | {'H0/Acc':>8}")
    print(f"  {'-'*6}-+-{'-'*8}-+-{'-'*7}-+-{'-'*8}-+-{'-'*11}-+-{'-'*8}")
    for ratio in ratios:
        r = results[ratio]
        marker = " <-- phi(6)/6" if abs(ratio - 4/3) < 0.01 else ""
        print(f"  {ratio:6.2f} | {r['acc']:7.2f}% | {r['h0']:7.4f} | {r['params']:>8,} | {r['eff_loss_params']:11.4f} | {r['eff_h0_acc']:8.4f}{marker}")

    # Best by each metric
    best_eff = min(results, key=lambda r: results[r]['eff_loss_params'])
    best_h0_eff = min(results, key=lambda r: results[r]['eff_h0_acc'])
    best_acc = max(results, key=lambda r: results[r]['acc'])

    print(f"\n  Best loss*params efficiency: ratio={best_eff:.2f}")
    print(f"  Best H0/accuracy efficiency: ratio={best_h0_eff:.2f}")
    print(f"  Best raw accuracy:           ratio={best_acc:.2f}")
    print(f"\n  4/3 is efficiency-optimal: {'CONFIRMED' if best_eff == 4/3 else 'NOT CONFIRMED'}")
    print(f"  4/3 is PH-efficient:        {'CONFIRMED' if best_h0_eff == 4/3 else 'NOT CONFIRMED'}")

    # ASCII chart: H0 vs ratio
    print(f"\n  PH H0 vs FFN Ratio:")
    max_h0 = max(r['h0'] for r in results.values())
    for ratio in ratios:
        r = results[ratio]
        bar = int(r['h0'] / max_h0 * 40)
        print(f"    {ratio:4.2f} | {'█'*bar} {r['h0']:.4f}")

if __name__ == '__main__':
    main()
