#!/usr/bin/env python3
"""H-CX-451: PCA Centroids Improve Raw Data Confusion Prediction

H-CX-450 showed raw pixel centroids predict confusion (Fashion r=-0.81),
but CIFAR was weak (r=-0.56) because pixel distance != semantic distance.

Test: Does PCA dimensionality reduction improve prediction?
Compare: raw pixels vs PCA-50 vs PCA-10 centroids.

If PCA improves CIFAR prediction significantly, the confusion signal
is in global structure, not pixel noise.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch, torch.nn as nn, torch.nn.functional as F, numpy as np
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


def cosine_dist_matrix(vecs):
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    norms = np.maximum(norms, 1e-8)
    normed = vecs / norms
    cos_dist = np.clip(1 - normed @ normed.T, 0, 2)
    np.fill_diagonal(cos_dist, 0)
    return cos_dist


def pair_confusion(Y, P, n_cls=10):
    pairs = {}
    for i in range(n_cls):
        for j in range(i+1, n_cls):
            mask = ((Y == i) & (P == j)) | ((Y == j) & (P == i))
            pairs[(i,j)] = mask.sum()
    return pairs


def compute_confusion_correlation(centroids, pairs, n_cls=10):
    """Compute Spearman r between centroid distances and confusion counts."""
    dist = cosine_dist_matrix(centroids)
    dists = [dist[i,j] for i in range(n_cls) for j in range(i+1, n_cls)]
    confs = [pairs.get((i,j), 0) for i in range(n_cls) for j in range(i+1, n_cls)]
    r, p = spearmanr(dists, confs)
    return r, p


def top5_overlap(centroids, pairs, n_cls=10):
    dist = cosine_dist_matrix(centroids)
    # Closest 5 pairs by centroid distance
    all_pairs = [(dist[i,j], (i,j)) for i in range(n_cls) for j in range(i+1, n_cls)]
    all_pairs.sort()
    raw_top5 = set(p for d,p in all_pairs[:5])
    # Most confused 5 pairs
    conf_top5 = set(k for k,v in sorted(pairs.items(), key=lambda x: -x[1])[:5])
    return len(raw_top5 & conf_top5)


def run_dataset(name):
    print(f"\n{'='*70}")
    print(f"  {name.upper()}")
    print(f"{'='*70}")

    torch.manual_seed(42)
    tr, te, dim, names = load_dataset(name)

    # Collect all test data
    all_x, all_y = [], []
    for x, y in te:
        all_x.append(x.view(x.size(0), -1).numpy())
        all_y.append(y.numpy())
    X = np.concatenate(all_x)
    Y = np.concatenate(all_y)

    # Train model for ground truth confusion
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

    model.eval()
    all_p = []
    with torch.no_grad():
        for x, y in te:
            out, _ = model(x.view(-1, dim))
            all_p.append(out.argmax(1).numpy())
    P = np.concatenate(all_p)
    acc = (P == Y).mean() * 100
    pairs = pair_confusion(Y, P)
    print(f"  Trained accuracy: {acc:.2f}%")

    # Compare different representations
    results = {}

    # 1. Raw pixels
    raw_centroids = np.array([X[Y == c].mean(0) for c in range(10)])
    r_raw, p_raw = compute_confusion_correlation(raw_centroids, pairs)
    t5_raw = top5_overlap(raw_centroids, pairs)
    results['raw'] = {'r': r_raw, 'p': p_raw, 'top5': t5_raw, 'dims': dim}

    # 2-4. PCA at various dimensions
    for n_comp in [50, 20, 10]:
        pca = PCA(n_components=n_comp, random_state=42)
        X_pca = pca.fit_transform(X)
        var_explained = pca.explained_variance_ratio_.sum()
        pca_centroids = np.array([X_pca[Y == c].mean(0) for c in range(10)])
        r_pca, p_pca = compute_confusion_correlation(pca_centroids, pairs)
        t5_pca = top5_overlap(pca_centroids, pairs)
        results[f'pca{n_comp}'] = {'r': r_pca, 'p': p_pca, 'top5': t5_pca,
                                    'dims': n_comp, 'var': var_explained}

    # 5. Euclidean distance instead of cosine
    raw_centroids_euc = np.array([X[Y == c].mean(0) for c in range(10)])
    euc_dists = []
    confs = []
    for i in range(10):
        for j in range(i+1, 10):
            euc_dists.append(np.linalg.norm(raw_centroids_euc[i] - raw_centroids_euc[j]))
            confs.append(pairs.get((i,j), 0))
    r_euc, p_euc = spearmanr(euc_dists, confs)
    results['euclidean'] = {'r': r_euc, 'p': p_euc, 'top5': t5_raw, 'dims': dim}

    # Print results
    print(f"\n  {'Method':<12} | {'Dims':>5} | {'Spearman r':>10} | {'p-value':>10} | {'Top5':>4} | {'Var%':>5}")
    print(f"  {'-'*12}-+-{'-'*5}-+-{'-'*10}-+-{'-'*10}-+-{'-'*4}-+-{'-'*5}")
    for method in ['raw', 'pca50', 'pca20', 'pca10', 'euclidean']:
        r = results[method]
        var_str = f"{r.get('var',0)*100:.1f}" if 'var' in r else "  -"
        print(f"  {method:<12} | {r['dims']:>5} | {r['r']:>10.4f} | {r['p']:>10.2e} | {r['top5']:>4}/5 | {var_str:>5}")

    best = max(results.items(), key=lambda x: abs(x[1]['r']))
    print(f"\n  Best method: {best[0]} (r={best[1]['r']:.4f})")

    return results


def main():
    print("=" * 70)
    print("  H-CX-451: PCA Centroids Improve Confusion Prediction?")
    print("=" * 70)

    all_results = {}
    for ds in ['mnist', 'fashion', 'cifar']:
        all_results[ds] = run_dataset(ds)

    # Cross-dataset summary
    print(f"\n{'='*70}")
    print(f"  CROSS-DATASET COMPARISON (best method per dataset)")
    print(f"{'='*70}")
    print(f"\n  {'Dataset':<8} | {'Raw r':>7} | {'PCA50 r':>8} | {'PCA20 r':>8} | {'PCA10 r':>8} | {'Best':>8}")
    print(f"  {'-'*8}-+-{'-'*7}-+-{'-'*8}-+-{'-'*8}-+-{'-'*8}-+-{'-'*8}")
    for ds in ['mnist', 'fashion', 'cifar']:
        r = all_results[ds]
        best = max(r.items(), key=lambda x: abs(x[1]['r']))
        print(f"  {ds:<8} | {r['raw']['r']:>7.4f} | {r['pca50']['r']:>8.4f} | {r['pca20']['r']:>8.4f} | {r['pca10']['r']:>8.4f} | {best[0]:>8}")

    # Did PCA improve CIFAR?
    cifar_raw = abs(all_results['cifar']['raw']['r'])
    cifar_best_pca = max(abs(all_results['cifar'][f'pca{n}']['r']) for n in [50,20,10])
    improvement = (cifar_best_pca - cifar_raw) / cifar_raw * 100
    print(f"\n  CIFAR improvement with PCA: {cifar_raw:.4f} -> {cifar_best_pca:.4f} ({improvement:+.1f}%)")

if __name__ == '__main__':
    main()
