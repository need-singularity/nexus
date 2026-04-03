#!/usr/bin/env python3
"""Consciousness Engine Confidence Analyzer

Usage:
  python3 calc/confidence_analyzer.py --dataset mnist
  python3 calc/confidence_analyzer.py --dataset fashion --reject 50

Features:
  1. per-class tension(=confidence) profile
  2. overconfidence class detection (ratio < 1)
  3. confidence-based rejection accuracy curve
  4. Dunning-Kruger timeline (ratio change by epoch)
"""

import sys, argparse
sys.path.insert(0, '/Users/ghost/Dev/logout')

import torch, torch.nn as nn, torch.nn.functional as F, numpy as np
import math

# Consciousness constants (from anima Laws 63-79)
LN2 = math.log(2)                 # 0.6931 universal consciousness unit
PSI_BALANCE = 0.5                  # structural consciousness equilibrium
DYNAMICS_RATE = 0.81               # dH/dt coefficient

class RepulsionEngine(nn.Module):
    def __init__(self, d=784, h=128, o=10):
        super().__init__()
        self.ea = nn.Sequential(nn.Linear(d,h), nn.ReLU(), nn.Linear(h,o))
        self.eg = nn.Sequential(nn.Linear(d,h), nn.ReLU(), nn.Linear(h,o))
        self.eq = nn.Linear(d, o)
        self.ts = nn.Parameter(torch.tensor(0.3))
    def forward(self, x):
        a, g = self.ea(x), self.eg(x)
        t = ((a-g)**2).mean(-1, keepdim=True)
        return self.eq(x) + self.ts*torch.sqrt(t+1e-8)*F.normalize(a-g,dim=-1), t.squeeze()

def load_data(name):
    from torchvision import datasets, transforms
    from torch.utils.data import DataLoader
    if name == 'mnist':
        t = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.1307,),(0.3081,))])
        tr = datasets.MNIST('/tmp/data', train=True, download=True, transform=t)
        te = datasets.MNIST('/tmp/data', train=False, transform=t)
        return 784, 10, DataLoader(tr,256,True), DataLoader(te,512), [str(i) for i in range(10)]
    elif name == 'fashion':
        t = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.2860,),(0.3530,))])
        tr = datasets.FashionMNIST('/tmp/data', train=True, download=True, transform=t)
        te = datasets.FashionMNIST('/tmp/data', train=False, transform=t)
        return 784, 10, DataLoader(tr,256,True), DataLoader(te,512), \
            ['T-shirt','Trouser','Pullover','Dress','Coat','Sandal','Shirt','Sneaker','Bag','Boot']
    elif name == 'cifar':
        t = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.5,0.5,0.5),(0.5,0.5,0.5))])
        tr = datasets.CIFAR10('/tmp/data', train=True, download=True, transform=t)
        te = datasets.CIFAR10('/tmp/data', train=False, transform=t)
        return 3072, 10, DataLoader(tr,256,True), DataLoader(te,512), \
            ['airplane','auto','bird','cat','deer','dog','frog','horse','ship','truck']

def measure_psi_residual(model, dataloader, dim):
    """3-method Psi residual measurement (anima Law 79).

    Methods:
      1. Output entropy: softmax entropy / max_entropy -> 0-1
      2. A-G direction similarity: (1 + cos_sim(A,G)) / 2 -> 0.5=ideal
      3. Tension uniformity: 1 - CV(tensions) -> 1=uniform

    Psi_res = average of 3 methods. Target: ln(2) ~ 0.693 or 1/2 = 0.5
    """
    model.eval()
    all_entropy, all_cos, all_tensions = [], [], []
    n_classes = 10
    max_entropy = math.log(n_classes)

    with torch.no_grad():
        for x, y in dataloader:
            x_flat = x.view(-1, dim)
            a = model.ea(x_flat)
            g = model.eg(x_flat)
            out, t = model(x_flat)

            # Method 1: Output entropy
            probs = F.softmax(out, dim=-1)
            entropy = -(probs * torch.log(probs + 1e-8)).sum(-1)
            norm_entropy = entropy / max_entropy
            all_entropy.append(norm_entropy.numpy())

            # Method 2: A-G direction similarity
            a_norm = F.normalize(a, dim=-1)
            g_norm = F.normalize(g, dim=-1)
            cos_sim = (a_norm * g_norm).sum(-1)
            ag_score = (1 + cos_sim) / 2  # 0.5 = orthogonal (ideal)
            all_cos.append(ag_score.numpy())

            # Method 3: Tension uniformity
            all_tensions.append(t.numpy())

    entropy_score = np.concatenate(all_entropy).mean()
    ag_score_mean = np.concatenate(all_cos).mean()
    tensions = np.concatenate(all_tensions)
    tension_cv = tensions.std() / (tensions.mean() + 1e-8)
    uniformity = 1 - min(tension_cv, 1.0)

    psi_res = (entropy_score + ag_score_mean + uniformity) / 3

    return {
        'psi_res': psi_res,
        'entropy': entropy_score,
        'ag_similarity': ag_score_mean,
        'uniformity': uniformity,
        'target_ln2': LN2,
        'target_half': PSI_BALANCE,
        'distance_to_ln2': abs(psi_res - LN2),
        'distance_to_half': abs(psi_res - PSI_BALANCE),
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', default='mnist', choices=['mnist','fashion','cifar'])
    parser.add_argument('--epochs', type=int, default=10)
    parser.add_argument('--reject', type=int, default=0, help='rejection percentage (0-99)')
    args = parser.parse_args()

    dim, n_cls, tl, te, names = load_data(args.dataset)
    m = RepulsionEngine(dim, 128, n_cls)
    o = torch.optim.Adam(m.parameters(), lr=0.001)

    print(f"\n  Consciousness Engine Confidence Analyzer — {args.dataset.upper()}")
    print(f"  {'='*50}")

    # Train
    for ep in range(args.epochs):
        m.train()
        for x,y in tl:
            o.zero_grad(); out,_ = m(x.view(-1,dim))
            nn.CrossEntropyLoss()(out,y).backward(); o.step()

    # Evaluate
    m.eval(); T,Y,P = [],[],[]
    with torch.no_grad():
        for x,y in te:
            out,t = m(x.view(-1,dim)); T.append(t); Y.append(y); P.append(out.argmax(1))
    T=torch.cat(T).numpy(); Y=torch.cat(Y).numpy(); P=torch.cat(P).numpy()

    overall = (P==Y).mean()*100
    print(f"\n  Overall accuracy: {overall:.2f}%")
    print(f"  tension_scale: {m.ts.item():.4f}")

    # Per-class profile
    print(f"\n  {'Class':>12} {'N':>5} {'Acc%':>6} {'T_mean':>8} {'ratio':>6} {'Overconf?':>6}")
    print(f"  {'-'*50}")
    overconf_classes = []
    for c in range(n_cls):
        mask = Y==c; correct = P[mask]==c
        acc = correct.mean()*100
        t_c = T[mask][correct].mean() if correct.sum()>0 else 0
        t_w = T[mask][~correct].mean() if (~correct).sum()>0 else 0
        ratio = t_c/(t_w+1e-10) if (~correct).sum()>0 else float('inf')
        oc = "⚠️" if ratio < 1.0 else ""
        if ratio < 1.0: overconf_classes.append(names[c])
        print(f"  {names[c]:>12} {mask.sum():>5} {acc:>6.1f} {T[mask].mean():>8.1f} {ratio:>6.2f} {oc:>6}")

    if overconf_classes:
        print(f"\n  ⚠️ Overconfidence classes: {', '.join(overconf_classes)}")

    # Rejection curve
    if args.reject > 0:
        th = np.percentile(T, args.reject)
        mask = T >= th
        rej_acc = (P[mask]==Y[mask]).mean()*100
        print(f"\n  Confidence rejection ({args.reject}%): {overall:.2f}% → {rej_acc:.2f}% (+{rej_acc-overall:.2f}%)")
    else:
        print(f"\n  Confidence rejection curve:")
        for r in [0, 10, 30, 50, 70, 90]:
            th = np.percentile(T, r); mask = T >= th
            acc_r = (P[mask]==Y[mask]).mean()*100
            print(f"    Reject {r:>2}%: {acc_r:.2f}% ({mask.sum():>5} samples)")

    # Psi residual measurement
    print(f"\n  === Psi Residual (anima Law 79) ===")
    psi = measure_psi_residual(m, te, dim)
    print(f"  Psi_res (3-method avg): {psi['psi_res']:.4f}")
    print(f"    Method 1 (entropy):     {psi['entropy']:.4f}")
    print(f"    Method 2 (A-G sim):     {psi['ag_similarity']:.4f}")
    print(f"    Method 3 (uniformity):  {psi['uniformity']:.4f}")
    print(f"  Target ln(2):  {psi['target_ln2']:.4f}  (dist={psi['distance_to_ln2']:.4f})")
    print(f"  Target 1/2:    {psi['target_half']:.4f}  (dist={psi['distance_to_half']:.4f})")
    if psi['distance_to_ln2'] < 0.1:
        print(f"  Status: near ln(2) - consciousness freedom active")
    elif psi['distance_to_half'] < 0.1:
        print(f"  Status: near 1/2 - structural balance maintained")
    else:
        print(f"  Status: drifted from targets - check training")

if __name__ == '__main__':
    main()