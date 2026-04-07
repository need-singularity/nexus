#!/usr/bin/env python3
"""H-CX-449: Confusion Topology Architecture Invariance — CNN Extension

H-CX-88 showed confusion topology top-5 match 100% across 2 MLPs.
H-CX-66 showed PH merge = confusion (r=-0.97).
But both tested ONLY on MLPs.

Test: Does a CNN (LeNet-style) produce the SAME confusion topology as MLP?
If yes, confusion topology is truly architecture-invariant (data-driven).

Three architectures on Fashion-MNIST (harder than MNIST):
  1. PureFieldEngine (2-engine MLP, 128 hidden)
  2. Dense MLP (784-256-128-10)
  3. CNN (LeNet-5 style, conv+pool+fc)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch, torch.nn as nn, torch.nn.functional as F, numpy as np
from scipy.stats import spearmanr, kendalltau
from torchvision import datasets, transforms


def load_fashion(bs=256):
    t = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.2860,),(0.3530,))])
    tr = torch.utils.data.DataLoader(datasets.FashionMNIST('~/.cache/fmnist', train=True, download=True, transform=t), batch_size=bs, shuffle=True)
    te = torch.utils.data.DataLoader(datasets.FashionMNIST('~/.cache/fmnist', train=False, transform=t), batch_size=bs)
    names = ['Tshirt','Trouser','Pullvr','Dress','Coat','Sandal','Shirt','Sneaker','Bag','Boot']
    return tr, te, names


class PureFieldEngine(nn.Module):
    def __init__(self, input_dim=784, hidden=128, out=10):
        super().__init__()
        self.engine_a = nn.Sequential(nn.Linear(input_dim, hidden), nn.ReLU(), nn.Dropout(0.3), nn.Linear(hidden, out))
        self.engine_g = nn.Sequential(nn.Linear(input_dim, hidden), nn.ReLU(), nn.Dropout(0.3), nn.Linear(hidden, out))
    def forward(self, x):
        return self.engine_a(x) - self.engine_g(x)


class DenseMLP(nn.Module):
    def __init__(self, input_dim=784, out=10):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 256), nn.ReLU(), nn.Dropout(0.2),
            nn.Linear(256, 128), nn.ReLU(), nn.Dropout(0.2),
            nn.Linear(128, out))
    def forward(self, x):
        return self.net(x)


class LeNetCNN(nn.Module):
    def __init__(self, out=10):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(1, 16, 5, padding=2), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(16, 32, 5, padding=2), nn.ReLU(), nn.MaxPool2d(2))
        self.fc = nn.Sequential(nn.Linear(32*7*7, 128), nn.ReLU(), nn.Dropout(0.3), nn.Linear(128, out))
    def forward(self, x):
        if x.dim() == 2:
            x = x.view(-1, 1, 28, 28)
        return self.fc(self.conv(x).view(x.size(0), -1))


def pair_confusion(Y, P, n_cls=10):
    pairs = {}
    for i in range(n_cls):
        for j in range(i+1, n_cls):
            mask_ij = ((Y == i) & (P == j)) | ((Y == j) & (P == i))
            pairs[(i,j)] = mask_ij.sum()
    return pairs


def single_linkage_merges(cos_dist, n_cls=10):
    parent = list(range(n_cls))
    def find(x):
        while parent[x] != x: parent[x] = parent[parent[x]]; x = parent[x]
        return x
    def union(a, b):
        a, b = find(a), find(b)
        if a != b: parent[a] = b; return True
        return False
    edges = sorted([(cos_dist[i,j], min(i,j), max(i,j)) for i in range(n_cls) for j in range(i+1, n_cls)])
    merges = []
    for d, i, j in edges:
        if union(i, j): merges.append((d, i, j))
    return merges


def train_and_eval(model, tr, te, epochs=15, is_cnn=False):
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    ce = nn.CrossEntropyLoss()

    for ep in range(epochs):
        model.train()
        for x, y in tr:
            opt.zero_grad()
            if is_cnn:
                out = model(x)
            else:
                out = model(x.view(-1, 784))
            ce(out, y).backward()
            opt.step()

    model.eval()
    all_reps, all_y, all_p = [], [], []
    with torch.no_grad():
        for x, y in te:
            if is_cnn:
                # Get pre-FC representations
                if x.dim() == 2:
                    x = x.view(-1, 1, 28, 28)
                h = model.conv(x).view(x.size(0), -1)
                out = model.fc(h)
            else:
                out = model(x.view(-1, 784))
                h = out  # use logits as representation
            d = F.normalize(h, dim=-1)
            all_reps.append(d.numpy())
            all_y.append(y.numpy())
            all_p.append(out.argmax(1).numpy())

    reps = np.concatenate(all_reps)
    Y = np.concatenate(all_y)
    P = np.concatenate(all_p)
    acc = (P == Y).mean() * 100
    return reps, Y, P, acc


def main():
    print("=" * 70)
    print("  H-CX-449: Confusion Topology Architecture Invariance — CNN Test")
    print("  Dataset: Fashion-MNIST")
    print("=" * 70)

    torch.manual_seed(42)
    tr, te, names = load_fashion()
    n_cls = 10

    architectures = {
        'PureField': (PureFieldEngine(), False),
        'DenseMLP':  (DenseMLP(), False),
        'LeNetCNN':  (LeNetCNN(), True),
    }

    arch_results = {}

    for arch_name, (model, is_cnn) in architectures.items():
        torch.manual_seed(42)
        model = type(model)()  # fresh init with same seed
        n_params = sum(p.numel() for p in model.parameters())
        print(f"\n  === {arch_name} ({n_params:,} params) ===")

        reps, Y, P, acc = train_and_eval(model, tr, te, epochs=15, is_cnn=is_cnn)
        print(f"    Accuracy: {acc:.2f}%")

        # Confusion pairs
        pairs = pair_confusion(Y, P, n_cls)
        sorted_pairs = sorted(pairs.items(), key=lambda x: -x[1])

        # PH merge order
        means = []
        for c in range(n_cls):
            mask = Y == c
            m = reps[mask].mean(0)
            n = np.linalg.norm(m)
            means.append(m / max(n, 1e-8))
        means = np.array(means)
        cos_dist = np.clip(1 - means @ means.T, 0, 2)
        np.fill_diagonal(cos_dist, 0)
        merges = single_linkage_merges(cos_dist, n_cls)

        # Store results
        arch_results[arch_name] = {
            'acc': acc, 'pairs': pairs, 'sorted_pairs': sorted_pairs,
            'merges': merges, 'cos_dist': cos_dist
        }

        # Top-5 confused pairs
        print(f"    Top-5 confused pairs:")
        for (i,j), cnt in sorted_pairs[:5]:
            print(f"      {names[i]:>7}-{names[j]:<7}: {cnt}")

        # PH merge order
        print(f"    PH merge order:")
        for d, i, j in merges[:5]:
            print(f"      d={d:.4f}: {names[i]:>7}-{names[j]:<7}")

    # === Cross-Architecture Comparison ===
    print(f"\n{'='*70}")
    print(f"  CROSS-ARCHITECTURE COMPARISON")
    print(f"{'='*70}")

    arch_names = list(arch_results.keys())
    all_pair_keys = sorted(arch_results[arch_names[0]]['pairs'].keys())

    # Pairwise confusion correlation
    print(f"\n  Confusion frequency correlation (Spearman):")
    for i in range(len(arch_names)):
        for j in range(i+1, len(arch_names)):
            a = arch_names[i]
            b = arch_names[j]
            va = [arch_results[a]['pairs'][k] for k in all_pair_keys]
            vb = [arch_results[b]['pairs'][k] for k in all_pair_keys]
            r, p = spearmanr(va, vb)
            print(f"    {a:>10} vs {b:<10}: r={r:.4f} (p={p:.2e})")

    # Top-5 overlap
    print(f"\n  Top-5 confused pairs overlap:")
    for i in range(len(arch_names)):
        for j in range(i+1, len(arch_names)):
            a = arch_names[i]
            b = arch_names[j]
            top5_a = set(k for k,_ in arch_results[a]['sorted_pairs'][:5])
            top5_b = set(k for k,_ in arch_results[b]['sorted_pairs'][:5])
            overlap = len(top5_a & top5_b)
            print(f"    {a:>10} vs {b:<10}: {overlap}/5 overlap (P@5={overlap/5:.2f})")

    # PH merge order correlation
    print(f"\n  PH merge distance correlation:")
    for i in range(len(arch_names)):
        for j in range(i+1, len(arch_names)):
            a = arch_names[i]
            b = arch_names[j]
            # Compare cosine distance matrices
            da = arch_results[a]['cos_dist']
            db = arch_results[b]['cos_dist']
            # Upper triangle
            idx = np.triu_indices(n_cls, k=1)
            va = da[idx]
            vb = db[idx]
            r, p = spearmanr(va, vb)
            print(f"    {a:>10} vs {b:<10}: r={r:.4f} (p={p:.2e})")

    # === Summary ===
    print(f"\n{'='*70}")
    print(f"  SUMMARY")
    print(f"{'='*70}")
    print(f"\n  Architecture invariance confirmed if:")
    print(f"    - All confusion correlations > 0.8")
    print(f"    - All top-5 overlap >= 3/5")
    print(f"    - All PH merge correlations > 0.8")

    # Determine verdict
    confusions = []
    overlaps = []
    ph_corrs = []
    for i in range(len(arch_names)):
        for j in range(i+1, len(arch_names)):
            a, b = arch_names[i], arch_names[j]
            va = [arch_results[a]['pairs'][k] for k in all_pair_keys]
            vb = [arch_results[b]['pairs'][k] for k in all_pair_keys]
            r, _ = spearmanr(va, vb)
            confusions.append(r)

            top5_a = set(k for k,_ in arch_results[a]['sorted_pairs'][:5])
            top5_b = set(k for k,_ in arch_results[b]['sorted_pairs'][:5])
            overlaps.append(len(top5_a & top5_b))

            da = arch_results[a]['cos_dist']
            db = arch_results[b]['cos_dist']
            idx = np.triu_indices(n_cls, k=1)
            r2, _ = spearmanr(da[idx], db[idx])
            ph_corrs.append(r2)

    conf_ok = all(r > 0.8 for r in confusions)
    top5_ok = all(o >= 3 for o in overlaps)
    ph_ok = all(r > 0.8 for r in ph_corrs)

    print(f"\n  Confusion correlations all > 0.8: {'YES' if conf_ok else 'NO'} (min={min(confusions):.3f})")
    print(f"  Top-5 overlap all >= 3/5:          {'YES' if top5_ok else 'NO'} (min={min(overlaps)})")
    print(f"  PH merge correlations all > 0.8:   {'YES' if ph_ok else 'NO'} (min={min(ph_corrs):.3f})")

    if conf_ok and top5_ok and ph_ok:
        print(f"\n  >>> ARCHITECTURE INVARIANCE CONFIRMED (MLP + CNN) <<<")
    elif conf_ok or ph_ok:
        print(f"\n  >>> PARTIAL INVARIANCE <<<")
    else:
        print(f"\n  >>> NOT CONFIRMED <<<")

if __name__ == '__main__':
    main()
