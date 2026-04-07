#!/usr/bin/env python3
"""H-CX-446: Spectral Gap <-> PH H0 <-> Tension Gap — Trinity Bridge

Cross-domain hypothesis connecting:
  - Linear Algebra: spectral gap (lambda_1 - lambda_2) of weight matrices
  - Topology: PH H0 total lifetime from class centroid cosine distances
  - Learning Theory: tension gap (max class tension - min class tension)

If all three pairwise correlations are strong (|r| > 0.8), we have a
"trinity bridge" connecting three mathematical domains through training.

Uses PureFieldEngine on MNIST (15 epochs), measures all three at each epoch.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch, torch.nn as nn, torch.nn.functional as F, numpy as np
from scipy.stats import spearmanr, pearsonr
from model_pure_field import PureFieldEngine

# --- Data loading ---
from torchvision import datasets, transforms
def load_mnist(bs=256):
    t = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.1307,),(0.3081,))])
    tr = torch.utils.data.DataLoader(datasets.MNIST('~/.cache/mnist', train=True, download=True, transform=t), batch_size=bs, shuffle=True)
    te = torch.utils.data.DataLoader(datasets.MNIST('~/.cache/mnist', train=False, transform=t), batch_size=bs)
    return tr, te

# --- Spectral gap of weight matrix ---
def spectral_gap(model):
    """Compute spectral gap (sigma_1 - sigma_2) of output layer weights."""
    gaps = []
    for name, param in model.named_parameters():
        if 'weight' in name and param.dim() == 2:
            s = torch.linalg.svdvals(param.data)
            if len(s) >= 2:
                gaps.append((s[0] - s[1]).item())
    return np.mean(gaps) if gaps else 0.0

# --- PH H0 total lifetime ---
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

def ph_h0_lifetime(cos_dist):
    """H0 total lifetime via single-linkage (no gudhi/ripser needed)."""
    n = len(cos_dist)
    parent = list(range(n))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    edges = sorted([(cos_dist[i,j], i, j) for i in range(n) for j in range(i+1, n)])
    total_life = 0.0
    for dist, i, j in edges:
        ri, rj = find(i), find(j)
        if ri != rj:
            total_life += dist  # birth=0, death=dist for each merge
            parent[ri] = rj
    return total_life

# --- Tension gap ---
def compute_tension_gap(model, loader, dim=784):
    """Max class tension - min class tension."""
    model.eval()
    class_tensions = {c: [] for c in range(10)}
    with torch.no_grad():
        for x, y in loader:
            out, tension = model(x.view(-1, dim))
            for i in range(len(y)):
                class_tensions[y[i].item()].append(tension[i].item())
    means = [np.mean(class_tensions[c]) for c in range(10)]
    return max(means) - min(means), means

# --- Extract representations ---
def extract_reps(model, loader, dim=784):
    model.eval()
    all_reps, all_labels = [], []
    with torch.no_grad():
        for x, y in loader:
            rep = model.engine_a(x.view(-1, dim)) - model.engine_g(x.view(-1, dim))
            d = F.normalize(rep, dim=-1)
            all_reps.append(d.numpy())
            all_labels.append(y.numpy())
    return np.concatenate(all_reps), np.concatenate(all_labels)

# === MAIN ===
def main():
    print("=" * 70)
    print("  H-CX-446: Spectral Gap <-> PH H0 <-> Tension Gap — Trinity Bridge")
    print("=" * 70)

    torch.manual_seed(42)
    np.random.seed(42)

    tr, te = load_mnist()
    model = PureFieldEngine(784, 128, 10)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    ce = nn.CrossEntropyLoss()

    epochs = 15
    records = []

    for ep in range(epochs + 1):
        if ep > 0:
            model.train()
            for x, y in tr:
                opt.zero_grad()
                out, t = model(x.view(-1, 784))
                loss = ce(out, y)
                loss.backward()
                opt.step()

        # Measure all three metrics
        sg = spectral_gap(model)
        reps, labels = extract_reps(model, te)
        cos_dist = class_cosine_dist(reps, labels)
        h0 = ph_h0_lifetime(cos_dist)
        tg, class_t = compute_tension_gap(model, te)

        # Accuracy
        model.eval()
        correct, total = 0, 0
        with torch.no_grad():
            for x, y in te:
                out, _ = model(x.view(-1, 784))
                correct += (out.argmax(1) == y).sum().item()
                total += len(y)
        acc = correct / total * 100

        records.append({
            'epoch': ep, 'spectral_gap': sg, 'ph_h0': h0,
            'tension_gap': tg, 'accuracy': acc, 'class_tensions': class_t
        })
        print(f"  Ep {ep:2d}: acc={acc:.1f}%  SG={sg:.4f}  H0={h0:.4f}  TG={tg:.4f}")

    # === Correlation Analysis ===
    print("\n" + "=" * 70)
    print("  CORRELATION ANALYSIS")
    print("=" * 70)

    sgs = [r['spectral_gap'] for r in records]
    h0s = [r['ph_h0'] for r in records]
    tgs = [r['tension_gap'] for r in records]

    pairs = [
        ('Spectral Gap', 'PH H0', sgs, h0s),
        ('Spectral Gap', 'Tension Gap', sgs, tgs),
        ('PH H0', 'Tension Gap', h0s, tgs),
    ]

    print(f"\n  {'Pair':<30} {'Pearson r':>10} {'p-value':>10} {'Spearman r':>11} {'p-value':>10}")
    print(f"  {'-'*71}")

    correlations = {}
    for name_a, name_b, a, b in pairs:
        pr, pp = pearsonr(a, b)
        sr, sp = spearmanr(a, b)
        label = f"{name_a} <-> {name_b}"
        print(f"  {label:<30} {pr:>10.4f} {pp:>10.2e} {sr:>11.4f} {sp:>10.2e}")
        correlations[label] = {'pearson': pr, 'spearman': sr, 'p_pearson': pp, 'p_spearman': sp}

    # === Trinity Assessment ===
    print("\n" + "=" * 70)
    print("  TRINITY BRIDGE ASSESSMENT")
    print("=" * 70)

    all_strong = all(abs(v['spearman']) > 0.8 for v in correlations.values())
    all_sig = all(v['p_spearman'] < 0.01 for v in correlations.values())

    for label, c in correlations.items():
        strength = "STRONG" if abs(c['spearman']) > 0.8 else "WEAK" if abs(c['spearman']) > 0.5 else "NONE"
        sig = "***" if c['p_spearman'] < 0.001 else "**" if c['p_spearman'] < 0.01 else "*" if c['p_spearman'] < 0.05 else "ns"
        print(f"  {label:<30} |r|={abs(c['spearman']):.3f} [{strength}] {sig}")

    if all_strong and all_sig:
        print("\n  >>> TRINITY BRIDGE CONFIRMED <<<")
        print("  Three mathematical domains connected through training dynamics!")
    elif sum(abs(v['spearman']) > 0.8 for v in correlations.values()) >= 2:
        print("\n  >>> PARTIAL BRIDGE (2/3 links strong) <<<")
    else:
        print("\n  >>> BRIDGE NOT FOUND <<<")

    # === ASCII Visualization ===
    print("\n" + "=" * 70)
    print("  EPOCH-BY-EPOCH DATA")
    print("=" * 70)

    # Normalize for ASCII chart
    def norm01(vals):
        mn, mx = min(vals), max(vals)
        if mx == mn: return [0.5] * len(vals)
        return [(v - mn) / (mx - mn) for v in vals]

    n_sgs = norm01(sgs)
    n_h0s = norm01(h0s)
    n_tgs = norm01(tgs)

    print(f"\n  {'Ep':>3} | {'SG':^20} | {'H0':^20} | {'TG':^20}")
    print(f"  {'-'*3}-+-{'-'*20}-+-{'-'*20}-+-{'-'*20}")
    for i, r in enumerate(records):
        sg_bar = int(n_sgs[i] * 18)
        h0_bar = int(n_h0s[i] * 18)
        tg_bar = int(n_tgs[i] * 18)
        print(f"  {r['epoch']:3d} | {'#'*sg_bar:<18} | {'#'*h0_bar:<18} | {'#'*tg_bar:<18}")

    # === Per-class tension at final epoch ===
    print(f"\n  Per-class tension (final epoch):")
    final_t = records[-1]['class_tensions']
    for c in sorted(range(10), key=lambda c: -final_t[c]):
        bar = int(final_t[c] / max(final_t) * 30)
        print(f"    Digit {c}: {'█'*bar} {final_t[c]:.4f}")

    # === Summary JSON for hypothesis doc ===
    print("\n  === RAW DATA (for hypothesis doc) ===")
    for r in records:
        print(f"  ep={r['epoch']:2d} sg={r['spectral_gap']:.6f} h0={r['ph_h0']:.6f} tg={r['tension_gap']:.6f} acc={r['accuracy']:.2f}")

if __name__ == '__main__':
    main()
