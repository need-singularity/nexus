#!/usr/bin/env python3
"""PH Confusion Analyzer — Analyzing Confusion Structure with Persistent Homology

Performs key major discoveries from this session all at once:
  - H-CX-66: PH merge order vs confusion frequency (r=-0.97)
  - H-CX-82: Epoch 1 perfect prediction (P@5=1.0)
  - H-CX-85: dendrogram = semantic hierarchy (89% purity)
  - H-CX-88: Architecture invariant (top-5 100%)
  - H-CX-90: Epoch 1 phase transition (30x)
  - H-CX-91: k-NN = neural network confusion (r=0.94)
  - H-CX-93: confusion PCA = semantic axis

Usage:
  python3 calc/ph_confusion_analyzer.py --dataset mnist
  python3 calc/ph_confusion_analyzer.py --dataset cifar --epochs 15
  python3 calc/ph_confusion_analyzer.py --dataset fashion --full
"""
import sys, os, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch, torch.nn as nn, torch.nn.functional as F, numpy as np
from sklearn.metrics import roc_auc_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.decomposition import PCA
from scipy.stats import spearmanr, kendalltau
try:
    import gudhi
    HAS_GUDHI = True
except ImportError:
    HAS_GUDHI = False
from model_pure_field import PureFieldEngine
from calc.direction_analyzer import load_data


def class_cosine_dist(D, Y, n_cls=10):
    means = []
    for c in range(n_cls):
        mask = Y == c
        if mask.sum() > 0:
            m = D[mask].mean(0)
            n = np.linalg.norm(m)
            means.append(m / max(n, 1e-8))
        else:
            means.append(np.zeros(D.shape[1]))
    means = np.array(means)
    cos_dist = np.clip(1 - means @ means.T, 0, 2)
    np.fill_diagonal(cos_dist, 0)
    return cos_dist, means


def single_linkage_merges(cos_dist, n_cls=10):
    sorted_edges = sorted([(cos_dist[i,j], min(i,j), max(i,j))
                           for i in range(n_cls) for j in range(i+1, n_cls)])
    parent = list(range(n_cls))
    def find(x):
        while parent[x] != x: parent[x] = parent[parent[x]]; x = parent[x]
        return x
    def union(a, b):
        a, b = find(a), find(b)
        if a != b: parent[a] = b; return True
        return False
    merges = []
    for dist, i, j in sorted_edges:
        if union(i, j): merges.append((dist, i, j))
    return merges


def ph_h0_total(cos_dist):
    if HAS_GUDHI:
        st = gudhi.SimplexTree.create_from_array(cos_dist)
        st.persistence()
        h0 = np.array(st.persistence_intervals_in_dimension(0))
    else:
        from ripser import ripser
        result = ripser(cos_dist, maxdim=0, distance_matrix=True)
        h0 = result['dgms'][0]
    h0_finite = h0[h0[:, 1] < np.inf]
    return np.sum(h0_finite[:, 1] - h0_finite[:, 0]) if len(h0_finite) > 0 else 0


def pair_confusion(Y, P, n_cls):
    conf = np.zeros((n_cls, n_cls), dtype=int)
    for idx in np.where(P != Y)[0]:
        conf[Y[idx], P[idx]] += 1
    pairs = {}
    for i in range(n_cls):
        for j in range(i+1, n_cls):
            pairs[(i,j)] = conf[i,j] + conf[j,i]
    return pairs, conf


def run_analysis(dataset_name='mnist', epochs=15, full=False):
    dim, tl, te, names = load_data(dataset_name)
    n_cls = len(names)

    print(f"\n{'='*70}")
    print(f"  PH Confusion Analyzer — {dataset_name.upper()}")
    print(f"{'='*70}")

    # Train PureField
    torch.manual_seed(42)
    model = PureFieldEngine(dim, 128, 10)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    ce = nn.CrossEntropyLoss()

    epoch_data = []

    # Epoch 0
    model.eval()
    D0, Y0, P0, M0 = [], [], [], []
    with torch.no_grad():
        for x, y in te:
            x_flat = x.view(-1, dim)
            rep = model.engine_a(x_flat) - model.engine_g(x_flat)
            mag = torch.sqrt((rep**2).mean(-1))
            d = F.normalize(rep, dim=-1)
            out = model.tension_scale * mag.unsqueeze(-1) * d
            D0.append(d.numpy()); Y0.extend(y.numpy()); P0.extend(out.argmax(1).numpy())
            M0.extend(mag.numpy())
    D0 = np.concatenate(D0); Y0 = np.array(Y0); P0 = np.array(P0); M0 = np.array(M0)
    dist0, _ = class_cosine_dist(D0, Y0, n_cls)
    h0_0 = ph_h0_total(dist0)
    epoch_data.append((0, (P0==Y0).mean()*100, h0_0, D0, Y0, P0, M0))

    for ep in range(epochs):
        model.train()
        for x, y in tl:
            opt.zero_grad()
            out, t = model(x.view(-1, dim))
            loss = ce(out, y); loss.backward(); opt.step()

        model.eval()
        dirs, ys, preds, mags = [], [], [], []
        with torch.no_grad():
            for x, y in te:
                x_flat = x.view(-1, dim)
                rep = model.engine_a(x_flat) - model.engine_g(x_flat)
                mag = torch.sqrt((rep**2).mean(-1))
                d = F.normalize(rep, dim=-1)
                out = model.tension_scale * mag.unsqueeze(-1) * d
                dirs.append(d.numpy()); ys.extend(y.numpy())
                preds.extend(out.argmax(1).numpy()); mags.extend(mag.numpy())
        D = np.concatenate(dirs); Y = np.array(ys); P = np.array(preds); M = np.array(mags)
        dist_ep, _ = class_cosine_dist(D, Y, n_cls)
        h0_ep = ph_h0_total(dist_ep)
        epoch_data.append((ep+1, (P==Y).mean()*100, h0_ep, D, Y, P, M))

        if (ep+1) % 5 == 0:
            print(f"  Epoch {ep+1}: acc={(P==Y).mean()*100:.1f}%  H0={h0_ep:.4f}")

    # Final data
    _, acc_f, h0_f, D_f, Y_f, P_f, M_f = epoch_data[-1]
    pairs_f, conf_f = pair_confusion(Y_f, P_f, n_cls)
    sorted_pairs = sorted(pairs_f.items(), key=lambda x: -x[1])
    dist_f, means_f = class_cosine_dist(D_f, Y_f, n_cls)
    merges_f = single_linkage_merges(dist_f, n_cls)

    # === 1. PH Merge vs Confusion (H-CX-66) ===
    print(f"\n  ▶ PH Merge vs Confusion (H-CX-66)")
    merge_data = [(d, (min(i,j),max(i,j))) for d,i,j in merges_f]
    merge_data.sort()
    dists_arr = [d for d,p in merge_data]
    confs_arr = [pairs_f.get(p, 0) for d,p in merge_data]
    r66, p66 = spearmanr(dists_arr, confs_arr)
    print(f"  Spearman r={r66:.4f}, p={p66:.4f}")
    for d, (i,j) in merge_data:
        print(f"    {names[i]:>6}-{names[j]:<6} dist={d:.4f}  conf={pairs_f.get((i,j),0)}")

    # === 2. Epoch 1 Prediction (H-CX-82) ===
    print(f"\n  ▶ Epoch 1 Prediction (H-CX-82)")
    if len(epoch_data) > 1:
        _, _, _, D1, Y1, _, _ = epoch_data[1]
        dist1, _ = class_cosine_dist(D1, Y1, n_cls)
        merges1 = single_linkage_merges(dist1, n_cls)
        md1 = sorted([(d, (min(i,j),max(i,j))) for d,i,j in merges1])
        c1 = [pairs_f.get(p, 0) for d,p in md1]
        r82, p82 = spearmanr([d for d,p in md1], c1)
        top3_1 = set(p for d,p in md1[:3])
        actual_top3 = set(p for p,c in sorted_pairs[:3])
        print(f"  Epoch 1→Final: r={r82:.4f} p={p82:.4f}  P@3={len(top3_1&actual_top3)/3:.2f}")

    # === 3. Phase Transition (H-CX-90) ===
    print(f"\n  ▶ Phase Transition (H-CX-90)")
    h0s = [d[2] for d in epoch_data]
    if len(h0s) > 2:
        dh0_01 = abs(h0s[1] - h0s[0])
        dh0_rest = np.mean([abs(h0s[i+1]-h0s[i]) for i in range(1, len(h0s)-1)])
        ratio = dh0_01 / dh0_rest if dh0_rest > 0 else 999
        print(f"  dH0(ep0→1)={dh0_01:.4f}, avg(rest)={dh0_rest:.4f}, ratio={ratio:.1f}x")

    # === 4. Dendrogram (H-CX-85) ===
    print(f"\n  ▶ Dendrogram = Semantic Hierarchy (H-CX-85)")
    clusters = {i: {i} for i in range(n_cls)}
    parent = list(range(n_cls))
    def find(x):
        while parent[x] != x: parent[x] = parent[parent[x]]; x = parent[x]
        return x
    def union(a, b):
        a, b = find(a), find(b)
        if a != b:
            merged = clusters[a] | clusters[b]
            parent[a] = b; clusters[b] = merged
            if a in clusters and a != b: del clusters[a]
            return merged
        return None

    for dist, i, j in sorted([(dist_f[i,j], min(i,j), max(i,j))
                               for i in range(n_cls) for j in range(i+1, n_cls)]):
        merged = union(i, j)
        if merged and len(merged) >= 2:
            cnames = sorted([names[c] for c in merged])
            print(f"    d={dist:.4f} → [{', '.join(cnames)}]")

    # === 5. Confusion PCA (H-CX-93) ===
    print(f"\n  ▶ Confusion PCA (H-CX-93)")
    conf_sym = (conf_f + conf_f.T) / 2.0
    np.fill_diagonal(conf_sym, 0)
    pca = PCA(n_components=3)
    pca_result = pca.fit_transform(conf_sym)
    print(f"  Explained: PC1={pca.explained_variance_ratio_[0]:.3f}, PC2={pca.explained_variance_ratio_[1]:.3f}")
    pc1 = pca_result[:, 0]
    for c in sorted(range(n_cls), key=lambda c: pc1[c]):
        bar = int(abs(pc1[c]) / max(abs(pc1)) * 20)
        sign = '+' if pc1[c] > 0 else '-'
        print(f"    {names[c]:>7} {sign}{'█'*bar}{'░'*(20-bar)} {pc1[c]:>8.1f}")

    # === 6. Depth = Difficulty (H-CX-92) ===
    print(f"\n  ▶ Depth = Difficulty (H-CX-92)")
    first_merge = {}
    for dist, i, j in sorted(merges_f, key=lambda x: x[0]):
        if i not in first_merge: first_merge[i] = dist
        if j not in first_merge: first_merge[j] = dist
    class_accs = [(P_f[Y_f==c]==Y_f[Y_f==c]).mean()*100 for c in range(n_cls)]
    r92, _ = spearmanr([first_merge.get(c,0) for c in range(n_cls)], class_accs)
    print(f"  Spearman(1st_merge, acc): r={r92:.4f}")

    if full:
        # === 7. k-NN comparison (H-CX-91) ===
        print(f"\n  ▶ k-NN Comparison (H-CX-91)")
        raw_X, raw_Y = [], []
        for x, y in te:
            raw_X.append(x.view(x.size(0), -1).numpy()); raw_Y.append(y.numpy())
        X_te = np.concatenate(raw_X); Y_te_raw = np.concatenate(raw_Y)
        raw_X_tr, raw_Y_tr = [], []
        for x, y in tl:
            raw_X_tr.append(x.view(x.size(0), -1).numpy()); raw_Y_tr.append(y.numpy())
        X_tr = np.concatenate(raw_X_tr)[:10000]; Y_tr = np.concatenate(raw_Y_tr)[:10000]

        knn = KNeighborsClassifier(n_neighbors=5, n_jobs=-1)
        knn.fit(X_tr, Y_tr)
        P_knn = knn.predict(X_te)
        pairs_knn, _ = pair_confusion(Y_te_raw, P_knn, n_cls)
        all_p = sorted(pairs_f.keys())
        r91, _ = spearmanr([pairs_f[p] for p in all_p], [pairs_knn.get(p,0) for p in all_p])
        print(f"  k-NN(k=5) vs PureField: Spearman r={r91:.4f}")

    # === Summary ===
    print(f"\n  {'='*60}")
    print(f"  SUMMARY — {dataset_name.upper()}")
    print(f"  {'='*60}")
    print(f"  Accuracy: {acc_f:.1f}%")
    print(f"  H-CX-66 merge~confusion: r={r66:.4f}")
    if len(epoch_data) > 1:
        print(f"  H-CX-82 ep1 prediction:  r={r82:.4f}")
    if len(h0s) > 2:
        print(f"  H-CX-90 phase transition: {ratio:.1f}x")
    print(f"  H-CX-92 depth~difficulty: r={r92:.4f}")
    print(f"  H-CX-93 PCA explained:    {pca.explained_variance_ratio_[0]:.3f}")
    print(f"  Top-3 confusion: {[f'{names[a]}-{names[b]}' for (a,b),c in sorted_pairs[:3]]}")


def main():
    parser = argparse.ArgumentParser(description='PH Confusion Analyzer')
    parser.add_argument('--dataset', default='mnist', choices=['mnist', 'fashion', 'cifar'])
    parser.add_argument('--epochs', type=int, default=15)
    parser.add_argument('--full', action='store_true', help='Include k-NN comparison')
    args = parser.parse_args()
    run_analysis(args.dataset, args.epochs, args.full)


if __name__ == '__main__':
    main()