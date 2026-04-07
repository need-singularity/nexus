#!/usr/bin/env python3
"""H-CX-452: Per-Class Difficulty Prediction from Raw Data

Chain so far: H-CX-449 (arch invariance) -> H-CX-450 (raw pairwise) -> H-CX-451 (PCA)
Missing piece: Can raw data predict which CLASSES are hardest?

Metric: "class isolation" = mean cosine distance from class centroid to all others.
More isolated = easier to classify. Less isolated = harder.

Test: Spearman r between class isolation and per-class accuracy across 3 datasets.
Also test: class intra-variance (spread within class) as difficulty predictor.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch, torch.nn as nn, numpy as np
from scipy.stats import spearmanr
from sklearn.decomposition import PCA
from torchvision import datasets, transforms
from model_pure_field import PureFieldEngine


def load_dataset(name, bs=256):
    if name == 'mnist':
        t = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.1307,),(0.3081,))])
        tr = torch.utils.data.DataLoader(datasets.MNIST('~/.cache/mnist', train=True, download=True, transform=t), batch_size=bs, shuffle=True)
        te = torch.utils.data.DataLoader(datasets.MNIST('~/.cache/mnist', train=False, transform=t), batch_size=bs)
        dim, names = 784, [str(i) for i in range(10)]
    elif name == 'fashion':
        t = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.2860,),(0.3530,))])
        tr = torch.utils.data.DataLoader(datasets.FashionMNIST('~/.cache/fmnist', train=True, download=True, transform=t), batch_size=bs, shuffle=True)
        te = torch.utils.data.DataLoader(datasets.FashionMNIST('~/.cache/fmnist', train=False, transform=t), batch_size=bs)
        dim, names = 784, ['Tshirt','Trouser','Pullvr','Dress','Coat','Sandal','Shirt','Sneaker','Bag','Boot']
    elif name == 'cifar':
        t = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.4914,0.4822,0.4465),(0.2470,0.2435,0.2616))])
        tr = torch.utils.data.DataLoader(datasets.CIFAR10('~/.cache/cifar10', train=True, download=True, transform=t), batch_size=bs, shuffle=True)
        te = torch.utils.data.DataLoader(datasets.CIFAR10('~/.cache/cifar10', train=False, transform=t), batch_size=bs)
        dim, names = 3072, ['plane','car','bird','cat','deer','dog','frog','horse','ship','truck']
    return tr, te, dim, names


def run_dataset(name):
    print(f"\n{'='*70}")
    print(f"  {name.upper()}")
    print(f"{'='*70}")

    torch.manual_seed(42)
    tr, te, dim, names = load_dataset(name)

    # Collect data
    all_x, all_y = [], []
    for x, y in te:
        all_x.append(x.view(x.size(0), -1).numpy())
        all_y.append(y.numpy())
    X = np.concatenate(all_x)
    Y = np.concatenate(all_y)

    # Raw centroids + PCA centroids
    pca = PCA(n_components=20, random_state=42)
    X_pca = pca.fit_transform(X)

    # Compute per-class metrics from raw data
    raw_centroids = np.array([X[Y == c].mean(0) for c in range(10)])
    pca_centroids = np.array([X_pca[Y == c].mean(0) for c in range(10)])

    # Cosine distance matrix
    def cos_dist_mat(vecs):
        norms = np.linalg.norm(vecs, axis=1, keepdims=True)
        normed = vecs / np.maximum(norms, 1e-8)
        d = np.clip(1 - normed @ normed.T, 0, 2)
        np.fill_diagonal(d, 0)
        return d

    raw_dist = cos_dist_mat(raw_centroids)
    pca_dist = cos_dist_mat(pca_centroids)

    # Class isolation = mean distance to other classes (higher = more isolated = easier)
    raw_isolation = raw_dist.mean(axis=1)
    pca_isolation = pca_dist.mean(axis=1)

    # Class spread = mean intra-class distance (higher = more spread = harder)
    raw_spread = []
    for c in range(10):
        Xc = X[Y == c]
        centroid = Xc.mean(0)
        dists = np.linalg.norm(Xc - centroid, axis=1)
        raw_spread.append(dists.mean())
    raw_spread = np.array(raw_spread)

    # Nearest neighbor distance (min distance to any other centroid)
    raw_nn_dist = []
    for c in range(10):
        dists = raw_dist[c].copy()
        dists[c] = np.inf
        raw_nn_dist.append(dists.min())
    raw_nn_dist = np.array(raw_nn_dist)

    # Train model
    model = PureFieldEngine(dim, 128, 10)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    ce = nn.CrossEntropyLoss()
    for ep in range(15):
        model.train()
        for x, y in tr:
            opt.zero_grad()
            out, t = model(x.view(-1, dim))
            ce(out, y).backward()
            opt.step()

    # Per-class accuracy
    model.eval()
    class_correct = np.zeros(10)
    class_total = np.zeros(10)
    with torch.no_grad():
        for x, y in te:
            out, _ = model(x.view(-1, dim))
            pred = out.argmax(1)
            for c in range(10):
                mask = y == c
                class_correct[c] += (pred[mask] == y[mask]).sum().item()
                class_total[c] += mask.sum().item()
    class_acc = class_correct / np.maximum(class_total, 1) * 100

    # Correlations
    predictors = {
        'isolation (raw)': raw_isolation,
        'isolation (pca)': pca_isolation,
        'spread (raw)': raw_spread,
        'nn_dist (raw)': raw_nn_dist,
    }

    print(f"\n  Per-class data (sorted by accuracy):")
    sorted_cls = np.argsort(class_acc)
    print(f"  {'Class':>8} | {'Acc%':>5} | {'Isolation':>9} | {'Spread':>7} | {'NN Dist':>7}")
    print(f"  {'-'*8}-+-{'-'*5}-+-{'-'*9}-+-{'-'*7}-+-{'-'*7}")
    for c in sorted_cls:
        print(f"  {names[c]:>8} | {class_acc[c]:5.1f} | {raw_isolation[c]:9.4f} | {raw_spread[c]:7.2f} | {raw_nn_dist[c]:7.4f}")

    print(f"\n  Predictor correlations with per-class accuracy:")
    results = {}
    for pred_name, pred_vals in predictors.items():
        r, p = spearmanr(pred_vals, class_acc)
        sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
        expected = "+" if "isolation" in pred_name or "nn_dist" in pred_name else "-"
        actual = "+" if r > 0 else "-"
        direction = "correct" if expected == actual else "WRONG"
        print(f"    {pred_name:<20}: r={r:+.4f} (p={p:.3f}) {sig}  direction: {direction}")
        results[pred_name] = {'r': r, 'p': p}

    # ASCII chart: accuracy vs isolation
    print(f"\n  Accuracy vs Isolation:")
    for c in sorted_cls:
        acc_bar = int(class_acc[c] / 100 * 30)
        iso_bar = int(raw_isolation[c] / raw_isolation.max() * 20)
        print(f"    {names[c]:>8} acc={'█'*acc_bar:<30} iso={'#'*iso_bar}")

    return {
        'class_acc': class_acc, 'isolation': raw_isolation,
        'spread': raw_spread, 'nn_dist': raw_nn_dist,
        'results': results, 'names': names
    }


def main():
    print("=" * 70)
    print("  H-CX-452: Per-Class Difficulty Prediction from Raw Data")
    print("=" * 70)

    all_results = {}
    for ds in ['mnist', 'fashion', 'cifar']:
        all_results[ds] = run_dataset(ds)

    # Summary
    print(f"\n{'='*70}")
    print(f"  CROSS-DATASET SUMMARY")
    print(f"{'='*70}")
    print(f"\n  {'Dataset':<8} | {'Iso(raw) r':>10} | {'Iso(pca) r':>10} | {'Spread r':>9} | {'NN dist r':>9}")
    print(f"  {'-'*8}-+-{'-'*10}-+-{'-'*10}-+-{'-'*9}-+-{'-'*9}")
    for ds in ['mnist', 'fashion', 'cifar']:
        r = all_results[ds]['results']
        print(f"  {ds:<8} | {r['isolation (raw)']['r']:>+10.4f} | {r['isolation (pca)']['r']:>+10.4f} | {r['spread (raw)']['r']:>+9.4f} | {r['nn_dist (raw)']['r']:>+9.4f}")

    # Best predictor
    print(f"\n  Best single predictor per dataset:")
    for ds in ['mnist', 'fashion', 'cifar']:
        r = all_results[ds]['results']
        best = max(r.items(), key=lambda x: abs(x[1]['r']))
        print(f"    {ds}: {best[0]} (r={best[1]['r']:+.4f})")

    # Universal?
    iso_rs = [abs(all_results[ds]['results']['isolation (raw)']['r']) for ds in all_results]
    print(f"\n  Isolation predicts difficulty universally (all |r|>0.5): {'YES' if all(r > 0.5 for r in iso_rs) else 'NO'}")

if __name__ == '__main__':
    main()
