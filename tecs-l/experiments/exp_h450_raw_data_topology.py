#!/usr/bin/env python3
"""H-CX-450: Confusion Topology is Computable from Raw Data (No Training)

If confusion topology is data-driven (H-CX-449, r>0.95 across architectures),
then the raw pixel-space class centroids should already encode it.

Test on 3 datasets:
  1. Compute class centroids in RAW pixel space (no training)
  2. Compute PH merge order from centroid cosine distances
  3. Compare with TRAINED model confusion pairs

If Spearman r > 0.8 between raw-data PH merge and trained confusion,
confusion topology is a GEOMETRIC property of data, not a learning artifact.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch, torch.nn as nn, torch.nn.functional as F, numpy as np
from scipy.stats import spearmanr
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
    cos_sim = normed @ normed.T
    cos_dist = np.clip(1 - cos_sim, 0, 2)
    np.fill_diagonal(cos_dist, 0)
    return cos_dist


def single_linkage_merges(cos_dist, n):
    parent = list(range(n))
    def find(x):
        while parent[x] != x: parent[x] = parent[parent[x]]; x = parent[x]
        return x
    edges = sorted([(cos_dist[i,j], min(i,j), max(i,j)) for i in range(n) for j in range(i+1, n)])
    merges = []
    for d, i, j in edges:
        ri, rj = find(i), find(j)
        if ri != rj: merges.append((d, i, j)); parent[ri] = rj
    return merges


def pair_confusion(Y, P, n_cls=10):
    pairs = {}
    for i in range(n_cls):
        for j in range(i+1, n_cls):
            mask = ((Y == i) & (P == j)) | ((Y == j) & (P == i))
            pairs[(i,j)] = mask.sum()
    return pairs


def run_dataset(name):
    print(f"\n{'='*70}")
    print(f"  {name.upper()}")
    print(f"{'='*70}")

    torch.manual_seed(42)
    tr, te, dim, names = load_dataset(name)
    n_cls = 10

    # === Step 1: Raw data class centroids ===
    print(f"\n  Step 1: Raw pixel-space centroids")
    all_x, all_y = [], []
    for x, y in te:
        all_x.append(x.view(x.size(0), -1).numpy())
        all_y.append(y.numpy())
    X = np.concatenate(all_x)
    Y = np.concatenate(all_y)

    raw_centroids = np.array([X[Y == c].mean(0) for c in range(n_cls)])
    raw_dist = cosine_dist_matrix(raw_centroids)
    raw_merges = single_linkage_merges(raw_dist, n_cls)

    print(f"    Raw PH merge order (top 5):")
    for d, i, j in raw_merges[:5]:
        print(f"      d={d:.4f}: {names[i]:>7}-{names[j]:<7}")

    # === Step 2: Train model and get confusion ===
    print(f"\n  Step 2: Train PureFieldEngine (15 epochs)")
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
    print(f"    Accuracy: {acc:.2f}%")

    # Trained model confusion
    pairs = pair_confusion(Y, P, n_cls)
    sorted_pairs = sorted(pairs.items(), key=lambda x: -x[1])

    print(f"    Top-5 confused pairs:")
    for (i,j), cnt in sorted_pairs[:5]:
        print(f"      {names[i]:>7}-{names[j]:<7}: {cnt}")

    # Trained model PH merge order (from representation space)
    all_reps = []
    with torch.no_grad():
        for x, y in te:
            rep = model.engine_a(x.view(-1, dim)) - model.engine_g(x.view(-1, dim))
            d = F.normalize(rep, dim=-1)
            all_reps.append(d.numpy())
    reps = np.concatenate(all_reps)
    trained_centroids = np.array([reps[Y == c].mean(0) for c in range(n_cls)])
    trained_centroids = trained_centroids / np.linalg.norm(trained_centroids, axis=1, keepdims=True)
    trained_dist = cosine_dist_matrix(trained_centroids)

    # === Step 3: Compare raw vs trained ===
    print(f"\n  Step 3: Raw data vs Trained model comparison")

    # Compare centroid distance matrices
    idx = np.triu_indices(n_cls, k=1)
    raw_upper = raw_dist[idx]
    trained_upper = trained_dist[idx]

    r_dist, p_dist = spearmanr(raw_upper, trained_upper)
    print(f"    Centroid distance correlation: Spearman r={r_dist:.4f} (p={p_dist:.2e})")

    # Compare raw PH merge order vs confusion count
    raw_merge_pairs = [(min(i,j), max(i,j)) for d,i,j in raw_merges]
    raw_merge_dists = [d for d,i,j in raw_merges]

    # For each merge pair, get confusion count
    raw_confs = [pairs.get(p, 0) for p in raw_merge_pairs]
    r_merge_conf, p_merge_conf = spearmanr(raw_merge_dists, raw_confs)
    print(f"    Raw PH merge vs trained confusion: Spearman r={r_merge_conf:.4f} (p={p_merge_conf:.2e})")

    # Compare pairwise: raw centroid distance vs confusion frequency
    all_raw_dists = [raw_dist[i,j] for i in range(n_cls) for j in range(i+1, n_cls)]
    all_confs = [pairs.get((i,j), 0) for i in range(n_cls) for j in range(i+1, n_cls)]
    r_raw_conf, p_raw_conf = spearmanr(all_raw_dists, all_confs)
    print(f"    Raw pairwise distance vs confusion: Spearman r={r_raw_conf:.4f} (p={p_raw_conf:.2e})")

    # Top-5 overlap: raw PH closest pairs vs trained confusion top-5
    raw_top5 = set(raw_merge_pairs[:5])
    trained_top5 = set(k for k,v in sorted_pairs[:5])
    overlap = len(raw_top5 & trained_top5)
    print(f"    Raw PH top-5 vs Trained confusion top-5: {overlap}/5 overlap (P@5={overlap/5:.2f})")

    # Detailed comparison table
    print(f"\n    Pair-by-pair comparison (sorted by raw distance):")
    sorted_raw = sorted([(raw_dist[i,j], i, j) for i in range(n_cls) for j in range(i+1, n_cls)])
    print(f"    {'Rank':>4} | {'Pair':<15} | {'Raw Dist':>8} | {'Confusion':>9} | {'Trained Dist':>12}")
    print(f"    {'-'*4}-+-{'-'*15}-+-{'-'*8}-+-{'-'*9}-+-{'-'*12}")
    for rank, (rd, i, j) in enumerate(sorted_raw[:10], 1):
        td = trained_dist[i, j]
        cf = pairs.get((min(i,j), max(i,j)), 0)
        print(f"    {rank:4d} | {names[i]:>7}-{names[j]:<7} | {rd:8.4f} | {cf:9d} | {td:12.4f}")

    return {
        'dataset': name, 'acc': acc,
        'r_dist': r_dist, 'r_merge_conf': r_merge_conf,
        'r_raw_conf': r_raw_conf, 'top5_overlap': overlap
    }


def main():
    print("=" * 70)
    print("  H-CX-450: Confusion Topology from Raw Data (No Training)")
    print("=" * 70)

    results = {}
    for ds in ['mnist', 'fashion', 'cifar']:
        results[ds] = run_dataset(ds)

    # === Summary ===
    print(f"\n{'='*70}")
    print(f"  CROSS-DATASET SUMMARY")
    print(f"{'='*70}")
    print(f"\n  {'Dataset':<8} | {'Dist Corr':>9} | {'Merge~Conf':>10} | {'Raw~Conf':>9} | {'Top5':>4}")
    print(f"  {'-'*8}-+-{'-'*9}-+-{'-'*10}-+-{'-'*9}-+-{'-'*4}")
    for ds in ['mnist', 'fashion', 'cifar']:
        r = results[ds]
        print(f"  {ds:<8} | {r['r_dist']:>9.4f} | {r['r_merge_conf']:>10.4f} | {r['r_raw_conf']:>9.4f} | {r['top5_overlap']:>4}/5")

    # Verdict
    all_strong = all(abs(results[ds]['r_raw_conf']) > 0.5 for ds in results)
    print(f"\n  Raw data predicts confusion (all |r|>0.5): {'YES' if all_strong else 'NO'}")

    best = max(results.values(), key=lambda r: abs(r['r_raw_conf']))
    print(f"  Strongest: {best['dataset']} (r={best['r_raw_conf']:.4f})")

if __name__ == '__main__':
    main()
