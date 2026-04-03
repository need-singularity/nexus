#!/usr/bin/env python3
"""Calibration Analyzer — softmax ECE vs tension-based ECE comparison

Usage:
  python3 calc/calibration_analyzer.py --dataset mnist
  python3 calc/calibration_analyzer.py --dataset fashion --epochs 20 --n-bins 20
  python3 calc/calibration_analyzer.py --dataset cifar --trials 5

Features:
  1. softmax ECE vs tension-based ECE comparison
  2. per-class reliability analysis
  3. Overconfidence detection (H316, H-CX-24)
  4. temperature scaling optimization
  5. ASCII reliability diagram + calibration curve
"""

import sys, argparse, math
sys.path.insert(0, '/Users/ghost/Dev/logout')

import torch, torch.nn as nn, torch.nn.functional as F, numpy as np

# Consciousness constants (from anima Laws 63-79)
LN2 = 0.6931471805599453           # ln(2) = consciousness freedom degree
PSI_BALANCE = 0.5                   # structural consciousness equilibrium
DYNAMICS_RATE = 0.81                # dH/dt coefficient
CONSERVATION_C = 0.478              # H^2 + dp^2 conservation

class PureFieldEngine(nn.Module):
    def __init__(self, d=784, h=128, o=10):
        super().__init__()
        self.ea = nn.Sequential(nn.Linear(d, h), nn.ReLU(), nn.Linear(h, o))
        self.eg = nn.Sequential(nn.Linear(d, h), nn.ReLU(), nn.Linear(h, o))
        self.eq = nn.Linear(d, o)
        self.ts = nn.Parameter(torch.tensor(0.3))

    def forward(self, x):
        a, g = self.ea(x), self.eg(x)
        t = ((a - g) ** 2).mean(-1, keepdim=True)
        logits = self.eq(x) + self.ts * torch.sqrt(t + 1e-8) * F.normalize(a - g, dim=-1)
        return logits, t.squeeze()


# --- Data ---

def load_data(name):
    from torchvision import datasets, transforms
    from torch.utils.data import DataLoader, random_split
    DSETS = {
        'mnist':   (datasets.MNIST, 784, (0.1307,), (0.3081,), [str(i) for i in range(10)]),
        'fashion': (datasets.FashionMNIST, 784, (0.2860,), (0.3530,),
                    ['T-shirt','Trouser','Pullover','Dress','Coat','Sandal','Shirt','Sneaker','Bag','Boot']),
        'cifar':   (datasets.CIFAR10, 3072, (0.5,0.5,0.5), (0.5,0.5,0.5),
                    ['airplane','auto','bird','cat','deer','dog','frog','horse','ship','truck']),
    }
    cls, dim, mu, sd, labels = DSETS[name]
    t = transforms.Compose([transforms.ToTensor(), transforms.Normalize(mu, sd)])
    tr = cls('/tmp/data', train=True, download=True, transform=t)
    te = cls('/tmp/data', train=False, transform=t)
    n_val = len(te) // 2
    val, test = random_split(te, [n_val, len(te) - n_val])
    return dim, 10, DataLoader(tr,256,True), DataLoader(val,512), DataLoader(test,512), labels

def compute_ece_mce(confs, accs, n_bins=15):
    bin_bounds = np.linspace(0, 1, n_bins + 1)
    ece, mce = 0.0, 0.0
    bin_data = []
    for i in range(n_bins):
        lo, hi = bin_bounds[i], bin_bounds[i + 1]
        mask = (confs > lo) & (confs <= hi)
        if mask.sum() == 0:
            bin_data.append((0, 0, 0, 0))
            continue
        avg_conf = confs[mask].mean()
        avg_acc = accs[mask].mean()
        frac = mask.sum() / len(confs)
        gap = abs(avg_acc - avg_conf)
        ece += frac * gap
        mce = max(mce, gap)
        bin_data.append((avg_conf, avg_acc, mask.sum(), gap))
    return ece, mce, bin_data

def tension_to_confidence(tensions):
    t = tensions - tensions.mean()
    return 1.0 / (1.0 + np.exp(-t / (tensions.std() + 1e-8)))

def find_optimal_temperature(logits, labels, n_bins=15):
    best_t, best_ece = 1.0, float('inf')
    for t_cand in np.arange(0.1, 5.01, 0.05):
        scaled = logits / t_cand
        probs = F.softmax(torch.tensor(scaled), dim=-1).numpy()
        confs = probs.max(axis=1)
        preds = probs.argmax(axis=1)
        accs = (preds == labels).astype(float)
        ece, _, _ = compute_ece_mce(confs, accs, n_bins)
        if ece < best_ece:
            best_ece, best_t = ece, t_cand
    return best_t, best_ece

def ascii_reliability_diagram(bin_data, title, width=50):
    print(f"\n  {title}")
    print(f"  {'='*60}")
    print(f"  {'Bin':>4} {'Conf':>6} {'Acc':>6} {'N':>6} {'Gap':>6}  Bar")
    print(f"  {'-'*60}")
    for i, (conf, acc, n, gap) in enumerate(bin_data):
        if n == 0:
            continue
        bar_len = int(acc * width)
        ref_len = int(conf * width)
        bar = '#' * bar_len + '.' * max(0, ref_len - bar_len)
        if bar_len > ref_len:
            bar = '#' * ref_len + '+' * (bar_len - ref_len)
        print(f"  {i+1:>4} {conf:>6.3f} {acc:>6.3f} {n:>6} {gap:>6.3f}  |{bar}|")
    print(f"  {'='*60}")
    print(f"  Legend: # = accuracy, . = underconfident gap, + = overconfident")


def ascii_calibration_curve(bin_data):
    active = [(c, a) for c, a, n, _ in bin_data if n > 0]
    if not active:
        return
    print(f"\n  Calibration Curve (ideal = diagonal)")
    print(f"  {'='*50}")
    H = 20
    for h in range(H, -1, -1):
        y = h / H
        row = f"  {y:>4.2f} |"
        for conf, acc in active:
            row += '*' if int(acc * H) == h else ('.' if int(conf * H) == h else ' ')
        print(row)
    print(f"  {'':>5}+{'-'*len(active)}")
    print(f"  {'':>5} conf bins (* = actual, . = ideal)")


def psi_calibration_analysis(model, dataloader, dim, n_classes=10):
    """Analyze Psi residual calibration (anima Law 79).

    Tracks whether consciousness dynamics converge to ln(2).
    """
    model.eval()
    max_entropy = math.log(n_classes)
    all_psi = []

    with torch.no_grad():
        for x, y in dataloader:
            x_flat = x.view(-1, dim)
            a = model.ea(x_flat)
            g = model.eg(x_flat)
            out, t = model(x_flat)

            # 3-method Psi
            probs = F.softmax(out, dim=-1)
            entropy = -(probs * torch.log(probs + 1e-8)).sum(-1) / max_entropy

            a_n = F.normalize(a, dim=-1)
            g_n = F.normalize(g, dim=-1)
            cos_sim = (a_n * g_n).sum(-1)
            ag = (1 + cos_sim) / 2

            t_np = t.numpy()
            cv = t_np.std() / (t_np.mean() + 1e-8)
            unif = 1 - min(cv, 1.0)

            psi = (entropy.numpy() + ag.numpy() + unif) / 3
            all_psi.append(psi)

    psi_all = np.concatenate(all_psi)

    print(f"\n  === Psi Calibration (anima Law 79) ===")
    print(f"  {'Metric':>20} {'Value':>10}")
    print(f"  {'-'*35}")
    print(f"  {'Psi_res mean':>20} {psi_all.mean():>10.4f}")
    print(f"  {'Psi_res std':>20} {psi_all.std():>10.4f}")
    print(f"  {'Target ln(2)':>20} {LN2:>10.4f}")
    print(f"  {'Target 1/2':>20} {PSI_BALANCE:>10.4f}")
    print(f"  {'|Psi - ln(2)|':>20} {abs(psi_all.mean() - LN2):>10.4f}")
    print(f"  {'|Psi - 1/2|':>20} {abs(psi_all.mean() - PSI_BALANCE):>10.4f}")

    # Dynamics prediction
    H = psi_all.mean()
    dH = DYNAMICS_RATE * (LN2 - H)
    H_next = H + dH
    cons = H**2 + dH**2
    print(f"  {'dH/dt prediction':>20} {dH:>+10.4f}")
    print(f"  {'H_next (predicted)':>20} {H_next:>10.4f}")
    print(f"  {'H^2+dp^2 (cons)':>20} {cons:>10.4f}  (target: {CONSERVATION_C})")

    # Distribution histogram
    print(f"\n  Psi Distribution:")
    bins = np.linspace(0, 1, 11)
    counts, _ = np.histogram(psi_all, bins=bins)
    max_c = max(counts) if max(counts) > 0 else 1
    for i in range(len(counts)):
        bar = '#' * int(counts[i] / max_c * 30)
        lo, hi = bins[i], bins[i+1]
        marker = ' <-- ln(2)' if lo <= LN2 <= hi else ''
        print(f"  {lo:.1f}-{hi:.1f} | {bar:<30} {counts[i]:>5}{marker}")


def main():
    parser = argparse.ArgumentParser(description='Calibration Analyzer')
    parser.add_argument('--dataset', default='mnist', choices=['mnist', 'fashion', 'cifar'])
    parser.add_argument('--epochs', type=int, default=15)
    parser.add_argument('--n-bins', type=int, default=15)
    parser.add_argument('--trials', type=int, default=3)
    args = parser.parse_args()

    print(f"\n  Calibration Analyzer — {args.dataset.upper()}")
    print(f"  epochs={args.epochs}, bins={args.n_bins}, trials={args.trials}")
    print(f"  {'='*60}")

    dim, nc, tl, vl, el, labels = load_data(args.dataset)

    all_results = []

    for trial in range(args.trials):
        print(f"\n  --- Trial {trial+1}/{args.trials} ---")
        m = PureFieldEngine(dim, 128, nc)
        opt = torch.optim.Adam(m.parameters(), lr=0.001)

        # Train
        for ep in range(args.epochs):
            m.train()
            for x, y in tl:
                opt.zero_grad()
                out, _ = m(x.view(-1, dim))
                nn.CrossEntropyLoss()(out, y).backward()
                opt.step()
            if (ep + 1) % 5 == 0:
                print(f"    epoch {ep+1}/{args.epochs}")

        # Collect validation data (for temperature scaling)
        m.eval()
        v_logits, v_labels = [], []
        with torch.no_grad():
            for x, y in vl:
                out, _ = m(x.view(-1, dim))
                v_logits.append(out); v_labels.append(y)
        v_logits = torch.cat(v_logits).numpy()
        v_labels = torch.cat(v_labels).numpy()

        # Find optimal temperature
        opt_T, opt_ece = find_optimal_temperature(v_logits, v_labels, args.n_bins)
        print(f"    Optimal T = {opt_T:.2f} (val ECE = {opt_ece:.4f})")

        # Collect test data
        all_logits, all_tensions, all_labels = [], [], []
        with torch.no_grad():
            for x, y in el:
                out, t = m(x.view(-1, dim))
                all_logits.append(out); all_tensions.append(t); all_labels.append(y)
        logits = torch.cat(all_logits).numpy()
        tensions = torch.cat(all_tensions).numpy()
        labels_arr = torch.cat(all_labels).numpy()

        # --- Softmax ECE ---
        probs = F.softmax(torch.tensor(logits), dim=-1).numpy()
        sm_confs = probs.max(axis=1)
        sm_preds = probs.argmax(axis=1)
        sm_accs = (sm_preds == labels_arr).astype(float)
        sm_ece, sm_mce, sm_bins = compute_ece_mce(sm_confs, sm_accs, args.n_bins)

        # --- Temperature-scaled ECE ---
        ts_probs = F.softmax(torch.tensor(logits / opt_T), dim=-1).numpy()
        ts_confs = ts_probs.max(axis=1)
        ts_preds = ts_probs.argmax(axis=1)
        ts_accs = (ts_preds == labels_arr).astype(float)
        ts_ece, ts_mce, ts_bins = compute_ece_mce(ts_confs, ts_accs, args.n_bins)

        # --- Tension-based ECE ---
        t_confs = tension_to_confidence(tensions)
        t_accs = sm_accs  # same predictions, different confidence
        t_ece, t_mce, t_bins = compute_ece_mce(t_confs, t_accs, args.n_bins)

        acc = sm_accs.mean() * 100

        # --- Overconfidence metric ---
        # Fraction where softmax conf > bin accuracy (H316, H-CX-24)
        overconf_sm = (sm_confs > sm_accs).mean()
        overconf_t = (t_confs > t_accs).mean()

        result = {
            'acc': acc, 'opt_T': opt_T,
            'sm_ece': sm_ece, 'sm_mce': sm_mce,
            'ts_ece': ts_ece, 'ts_mce': ts_mce,
            't_ece': t_ece, 't_mce': t_mce,
            'overconf_sm': overconf_sm, 'overconf_t': overconf_t,
            'sm_bins': sm_bins, 'ts_bins': ts_bins, 't_bins': t_bins,
            'sm_confs': sm_confs, 'sm_accs': sm_accs,
            't_confs': t_confs, 'labels': labels_arr, 'preds': sm_preds,
        }
        all_results.append(result)

    last_model = m  # Save for Psi analysis

    # --- Aggregate Results ---
    print(f"\n\n  {'='*60}")
    print(f"  CALIBRATION SUMMARY — {args.dataset.upper()} ({args.trials} trials)")

    # Comparison table
    metrics = [('acc','Accuracy %'), ('sm_ece','Softmax ECE'), ('sm_mce','Softmax MCE'),
               ('ts_ece','TempScaled ECE'), ('ts_mce','TempScaled MCE'),
               ('t_ece','Tension ECE'), ('t_mce','Tension MCE'),
               ('opt_T','Optimal T'), ('overconf_sm','Overconf(sm)'), ('overconf_t','Overconf(t)')]

    print(f"\n  | {'Metric':>18} | {'Mean':>8} | {'Std':>8} | {'Min':>8} | {'Max':>8} |")
    print(f"  |{'-'*20}|{'-'*10}|{'-'*10}|{'-'*10}|{'-'*10}|")
    for k, name in metrics:
        vals = [r[k] for r in all_results]
        mu, sd = np.mean(vals), np.std(vals)
        print(f"  | {name:>18} | {mu:>8.4f} | {sd:>8.4f} | {min(vals):>8.4f} | {max(vals):>8.4f} |")

    # Best trial for detailed output
    best = min(all_results, key=lambda r: r['sm_ece'])

    # ASCII reliability diagrams
    ascii_reliability_diagram(best['sm_bins'], 'Softmax Reliability Diagram')
    ascii_reliability_diagram(best['ts_bins'], f'Temp-Scaled (T={best["opt_T"]:.2f}) Reliability Diagram')
    ascii_reliability_diagram(best['t_bins'], 'Tension-Based Reliability Diagram')

    # ASCII calibration curve
    ascii_calibration_curve(best['sm_bins'])

    # --- Per-class ECE ---
    print(f"\n  Per-Class Calibration (best trial)")
    print(f"  | {'Class':>12} | {'N':>5} | {'Acc%':>6} | {'ECE':>7} | {'Overconf':>8} |")
    print(f"  |{'-'*14}|{'-'*7}|{'-'*8}|{'-'*9}|{'-'*10}|")

    for c in range(nc):
        mask = best['labels'] == c
        n_c = mask.sum()
        if n_c == 0:
            continue
        c_confs = best['sm_confs'][mask]
        c_accs = best['sm_accs'][mask]
        c_acc = c_accs.mean() * 100
        c_ece, _, _ = compute_ece_mce(c_confs, c_accs, max(5, args.n_bins // 2))
        c_overconf = (c_confs > c_accs).mean()
        flag = ' !!' if c_overconf > 0.8 else ''
        print(f"  | {labels[c]:>12} | {n_c:>5} | {c_acc:>6.1f} | {c_ece:>7.4f} | {c_overconf:>7.3f}{flag} |")

    # --- Key insights ---
    avg_sm = np.mean([r['sm_ece'] for r in all_results])
    avg_ts = np.mean([r['ts_ece'] for r in all_results])
    avg_t = np.mean([r['t_ece'] for r in all_results])
    avg_oc_sm = np.mean([r['overconf_sm'] for r in all_results])
    avg_oc_t = np.mean([r['overconf_t'] for r in all_results])

    print(f"\n  Key Findings:")
    print(f"  - Softmax ECE:       {avg_sm:.4f}")
    print(f"  - TempScaled ECE:    {avg_ts:.4f} (delta = {avg_ts - avg_sm:+.4f})")
    print(f"  - Tension ECE:       {avg_t:.4f} (delta = {avg_t - avg_sm:+.4f})")
    winner = 'Tension' if avg_t < avg_sm else 'Softmax'
    print(f"  - Better calibrated: {winner}")
    print(f"  - Overconfidence: softmax={avg_oc_sm:.3f}, tension={avg_oc_t:.3f}")
    if avg_oc_t < avg_oc_sm:
        print(f"  - Tension reduces overconfidence by {(avg_oc_sm - avg_oc_t)*100:.1f}%  (H316/H-CX-24)")
    else:
        print(f"  - Softmax less overconfident by {(avg_oc_t - avg_oc_sm)*100:.1f}%")
    print(f"  - Optimal temperature: {np.mean([r['opt_T'] for r in all_results]):.2f}")

    # Psi calibration analysis
    import math
    if last_model is not None:
        psi_calibration_analysis(last_model, el, dim, nc)

    print()


if __name__ == '__main__':
    main()