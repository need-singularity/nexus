#!/usr/bin/env python3
"""Direction Analyzer — Decompose tension into magnitude (confidence) and direction (concept)

H339/H341 verification:
  output = tension_scale * sqrt(tension) * direction
  direction = normalize(engine_A(x) - engine_G(x))
  magnitude = sqrt(tension) = ||A - G||

Usage:
  python3 calc/direction_analyzer.py --dataset mnist
  python3 calc/direction_analyzer.py --dataset fashion --epochs 20
  python3 calc/direction_analyzer.py --dataset cifar --epochs 15
"""

import sys, argparse
sys.path.insert(0, '/Users/ghost/Dev/logout')

try:
    import torch, torch.nn as nn, torch.nn.functional as F, numpy as np
    from model_pure_field import PureFieldEngine
    from model_utils import load_mnist
    _HAS_DEPS = True
except ImportError as e:
    _HAS_DEPS = False
    _IMPORT_ERR = str(e)

DATASETS = {
    'mnist':   dict(dim=784, norm=(0.1307, 0.3081), cls_names=[str(i) for i in range(10)]),
    'fashion': dict(dim=784, norm=(0.2860, 0.3530),
                    cls_names=['Tshirt','Trouser','Pullvr','Dress','Coat',
                               'Sandal','Shirt','Sneakr','Bag','Boot']),
    'cifar':   dict(dim=3072, norm=((0.5,0.5,0.5),(0.5,0.5,0.5)),
                    cls_names=['plane','auto','bird','cat','deer',
                               'dog','frog','horse','ship','truck']),
}

def load_data(name, bs=256):
    from torchvision import datasets, transforms
    from torch.utils.data import DataLoader
    cfg = DATASETS[name]
    n = cfg['norm']
    mean, std = (n[0], n[1]) if isinstance(n[0], tuple) else ((n[0],), (n[1],))
    t = transforms.Compose([transforms.ToTensor(), transforms.Normalize(mean, std)])
    DS = {'mnist': datasets.MNIST, 'fashion': datasets.FashionMNIST, 'cifar': datasets.CIFAR10}[name]
    tr = DS('/tmp/data', train=True, download=True, transform=t)
    te = DS('/tmp/data', train=False, transform=t)
    return cfg['dim'], DataLoader(tr, bs, True), DataLoader(te, 512), cfg['cls_names']

def normalize_rows(v):
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    return v / np.clip(n, 1e-8, None)

def cosine_sim(a, b):
    return (normalize_rows(a) * normalize_rows(b)).sum(-1)

def ascii_heatmap(mat, labels, title):
    chars = ' ░▒▓█'
    lo, hi = mat.min(), mat.max()
    print(f"\n  {title}")
    print(f"  {'':>7}", end='')
    for l in labels: print(f'{l:>7}', end='')
    print()
    for i, row in enumerate(mat):
        print(f"  {labels[i]:>7}", end='')
        for v in row:
            idx = int((v - lo) / (hi - lo + 1e-8) * (len(chars) - 1))
            c = chars[min(idx, len(chars)-1)]
            print(f'  {v:.2f}{c}', end='')
        print()
    print(f"  scale: {lo:.3f}={chars[0]}  {hi:.3f}={chars[-1]}")

def ascii_bars(values, labels, title, width=40):
    print(f"\n  {title}")
    mx = max(abs(v) for v in values) if values else 1
    for l, v in zip(labels, values):
        bar_len = int(v / mx * width)
        bar = '█' * bar_len + '░' * (width - bar_len)
        print(f"  {l:>7} |{bar}| {v:.2f}")

def main():
    parser = argparse.ArgumentParser(description='Direction Analyzer (H339/H341)')
    parser.add_argument('--dataset', default='mnist', choices=['mnist','fashion','cifar'])
    parser.add_argument('--epochs', type=int, default=15)
    args = parser.parse_args()

    if not _HAS_DEPS:
        print(f"Error: Missing dependency — {_IMPORT_ERR}")
        print("Install with: pip install torch numpy")
        sys.exit(1)

    dim, tl, te, names = load_data(args.dataset)
    model = PureFieldEngine(dim, 128, 10)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    ce = nn.CrossEntropyLoss()

    print(f"\n  Direction Analyzer — {args.dataset.upper()}")
    print(f"  {'='*60}")
    print(f"  H339: direction encodes concept, magnitude encodes confidence")
    print(f"  Training PureFieldEngine ({args.epochs} epochs)...\n")

    # --- Train ---
    for ep in range(args.epochs):
        model.train(); loss_sum = 0
        for x, y in tl:
            opt.zero_grad()
            out, t = model(x.view(-1, dim))
            loss = ce(out, y); loss.backward(); opt.step()
            loss_sum += loss.item()
        if (ep+1) % 5 == 0 or ep == 0:
            model.eval(); correct = total = 0
            with torch.no_grad():
                for x, y in te:
                    o, _ = model(x.view(-1, dim))
                    correct += (o.argmax(1)==y).sum().item(); total += y.size(0)
            print(f"    Epoch {ep+1:>2}: loss={loss_sum/len(tl):.4f}  acc={correct/total*100:.1f}%")

    # --- Extract directions + magnitudes ---
    model.eval()
    all_dir, all_mag, all_y, all_pred = [], [], [], []
    with torch.no_grad():
        for x, y in te:
            x_flat = x.view(-1, dim)
            a = model.engine_a(x_flat)
            g = model.engine_g(x_flat)
            rep = a - g
            mag = torch.sqrt((rep**2).mean(-1))
            d = F.normalize(rep, dim=-1)
            out = model.tension_scale * mag.unsqueeze(-1) * d
            all_dir.append(d.numpy()); all_mag.append(mag.numpy())
            all_y.append(y.numpy()); all_pred.append(out.argmax(1).numpy())

    D = np.concatenate(all_dir);   M = np.concatenate(all_mag)
    Y = np.concatenate(all_y);     P = np.concatenate(all_pred)
    acc = (P==Y).mean()*100
    ts = model.tension_scale.item()
    print(f"\n  Final accuracy: {acc:.2f}%  |  tension_scale: {ts:.4f}")

    # --- 1. Per-class mean direction ---
    n_cls = 10
    class_means = np.zeros((n_cls, n_cls))
    for c in range(n_cls):
        mask = Y == c
        class_means[c] = D[mask].mean(0)

    # --- 2 & 3. Within-class vs between-class cosine similarity ---
    within_cos, between_cos, mag_stats, dir_stability = [], [], [], []
    print(f"\n  Per-class statistics:")
    print(f"  {'Class':>7} {'N':>5} {'Acc%':>6} {'|mag|':>7} {'std':>6} "
          f"{'cos_w':>6} {'cos_b':>6} {'stab':>5}")
    print(f"  {'-'*58}")

    for c in range(n_cls):
        mask = Y == c
        dc = D[mask]; mc = M[mask]
        n = mask.sum()
        c_acc = (P[mask]==c).mean()*100

        # Within-class cosine: sample vs class mean
        cm = normalize_rows(class_means[c:c+1])
        w_cos = cosine_sim(dc, np.broadcast_to(cm, dc.shape)).mean()
        within_cos.append(w_cos)

        # Between-class cosine: class mean vs other class means
        b_vals = []
        for j in range(n_cls):
            if j != c:
                b_vals.append(cosine_sim(class_means[c:c+1], class_means[j:j+1])[0])
        b_cos = np.mean(b_vals)
        between_cos.append(b_cos)

        # Magnitude stats
        mag_stats.append((mc.mean(), mc.std()))

        # Direction stability: std of within-class cosine similarities
        stab = cosine_sim(dc, np.broadcast_to(cm, dc.shape)).std()
        dir_stability.append(stab)

        print(f"  {names[c]:>7} {n:>5} {c_acc:>6.1f} {mc.mean():>7.2f} {mc.std():>6.2f} "
              f"{w_cos:>6.3f} {b_cos:>6.3f} {stab:>5.3f}")

    within_avg = np.mean(within_cos)
    between_avg = np.mean(between_cos)
    ratio = within_avg / (abs(between_avg) + 1e-8)

    print(f"\n  {'='*60}")
    print(f"  Within-class  cosine (avg): {within_avg:.4f}")
    print(f"  Between-class cosine (avg): {between_avg:.4f}")
    print(f"  Separation ratio (W/|B|):   {ratio:.2f}x")
    print(f"  H339 prediction: 3.46x on MNIST")
    if args.dataset == 'mnist':
        delta = abs(ratio - 3.46)
        print(f"  Measured delta from H339:   {delta:.2f}  {'CLOSE' if delta < 1.5 else 'DIVERGENT'}")

    # --- 5. Direction confusion matrix ---
    conf = np.zeros((n_cls, n_cls))
    cm_norm = normalize_rows(class_means)
    for i in range(n_cls):
        for j in range(n_cls):
            conf[i, j] = (cm_norm[i] * cm_norm[j]).sum()

    ascii_heatmap(conf, [n[:5] for n in names],
                  "Direction Confusion Matrix (cosine similarity)")

    # --- 6. Magnitude bar chart ---
    ascii_bars([s[0] for s in mag_stats], [n[:5] for n in names],
               "Per-class Magnitude (mean)")

    # --- Within vs Between comparison ---
    print(f"\n  Within vs Between Cosine Similarity:")
    for c in range(n_cls):
        w = within_cos[c]; b = between_cos[c]
        wbar = int(max(0, w) * 30); bbar = int(max(0, abs(b)) * 30)
        print(f"  {names[c][:5]:>5} W={'█'*wbar}{'░'*(30-wbar)} {w:.3f}")
        print(f"  {'':>5} B={'▒'*bbar}{'░'*(30-bbar)} {b:.3f}")

    # --- Direction stability ---
    print(f"\n  Direction Stability (lower = more stable):")
    max_stab = max(dir_stability) if dir_stability else 1
    for c in range(n_cls):
        s = dir_stability[c]
        bar_len = int(s / max_stab * 30)
        print(f"  {names[c][:5]:>5} |{'▓'*bar_len}{'░'*(30-bar_len)}| {s:.4f}")

    # --- Summary ---
    print(f"\n  {'='*60}")
    print(f"  SUMMARY")
    print(f"  {'='*60}")
    print(f"  Dataset:           {args.dataset.upper()}")
    print(f"  Accuracy:          {acc:.2f}%")
    print(f"  tension_scale:     {ts:.4f}")
    print(f"  Separation ratio:  {ratio:.2f}x  (H339 target: 3.46x)")
    print(f"  Mean magnitude:    {np.mean([s[0] for s in mag_stats]):.3f}")
    print(f"  Mean stability:    {np.mean(dir_stability):.4f}")
    most_confused = np.unravel_index(np.argmin(conf + np.eye(n_cls)*999), conf.shape)
    print(f"  Most confused:     {names[most_confused[0]]} <-> {names[most_confused[1]]} "
          f"(cos={conf[most_confused]:.3f})")
    most_sep = np.unravel_index(np.argmin(conf), conf.shape)
    print(f"  Most separated:    {names[most_sep[0]]} <-> {names[most_sep[1]]} "
          f"(cos={conf[most_sep]:.3f})")

if __name__ == '__main__':
    main()