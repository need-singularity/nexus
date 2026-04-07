#!/usr/bin/env python3
"""Experiment: ADE Activation Threshold vs Golden Zone Boundary

Hypothesis (H-LIE-2):
  The optimal MoE activation threshold is derived from the Lie/n=6 structure,
  not from an arbitrary hand-tuned value.

  Three candidate thresholds:
    1/e   ~ 0.368  — Golden Zone center (natural constant)
    1/3   ~ 0.333  — Meta fixed point, tau(6)/sigma(6) = 4/12
    1/2   = 0.500  — Riemann critical line, Golden Zone upper
    1-1/e ~ 0.632  — P!=NP gap ratio, H-CX-15 optimal activation

  ADE-derived: G2 has 12 roots; using sigma/tau = 12/4 ratio:
    3 active out of 12  =>  ratio = 1/4 = 0.250
    4 active out of 12  =>  ratio = 1/3 = 0.333  (meta fixed point)
    6 active out of 12  =>  ratio = 1/2 = 0.500  (Riemann line)

  We sweep activation ratio on a fixed n=12 experts model (|G2| size)
  and compare against n=8 with the same ratios.

Additional sweep:
  Part 2: Temperature (softness) sweep with Boltzmann gate, T in
  {0.1, 1/3, 1/e, 1/2, 1.0, e, 2, 5}
  to test if T=e (Boltzmann golden zone) is superior to T=1/3 or T=1/2.

Dataset: MNIST
Epochs:  10 per trial, 3 seeds
Device:  MPS or CPU
"""

import sys
import os
import time
import math

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))

from model_utils import load_mnist, count_params

INV_E = 1.0 / math.e
ONE_MINUS_INV_E = 1.0 - INV_E
E = math.e


# ─────────────────────────────────────────────────────────────
# Model components
# ─────────────────────────────────────────────────────────────
class Expert(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim),
        )

    def forward(self, x):
        return self.net(x)


class TopKMoE(nn.Module):
    """Fixed-k TopK gate."""

    def __init__(self, input_dim, hidden_dim, output_dim, n_experts, k):
        super().__init__()
        self.n_experts = n_experts
        self.k = k
        self.experts = nn.ModuleList([Expert(input_dim, hidden_dim, output_dim) for _ in range(n_experts)])
        self.gate = nn.Linear(input_dim, n_experts)
        self._counts = torch.zeros(n_experts)

    def forward(self, x):
        scores = self.gate(x)
        topk_vals, topk_idx = scores.topk(self.k, dim=-1)
        mask = torch.zeros_like(scores).scatter(-1, topk_idx, 1.0)
        weights = F.softmax(scores, dim=-1) * mask
        weights = weights / (weights.sum(-1, keepdim=True) + 1e-8)
        outs = torch.stack([e(x) for e in self.experts], dim=1)
        result = (weights.unsqueeze(-1) * outs).sum(dim=1)
        with torch.no_grad():
            self._counts += (weights > 0).float().sum(0).cpu()
        return result

    def norm_entropy(self):
        c = self._counts / (self._counts.sum() + 1e-8)
        ent = -(c * (c + 1e-9).log()).sum().item()
        return ent / math.log(self.n_experts) if self.n_experts > 1 else 0.0

    def reset(self):
        self._counts = torch.zeros(self.n_experts)


class BoltzmannMoE(nn.Module):
    """Soft Boltzmann gate — activate top-k by probability, temperature T."""

    def __init__(self, input_dim, hidden_dim, output_dim, n_experts, k, temperature=E):
        super().__init__()
        self.n_experts = n_experts
        self.k = k
        self.temperature = temperature
        self.experts = nn.ModuleList([Expert(input_dim, hidden_dim, output_dim) for _ in range(n_experts)])
        self.gate = nn.Linear(input_dim, n_experts)
        self._counts = torch.zeros(n_experts)

    def forward(self, x):
        scores = self.gate(x) / self.temperature
        probs = F.softmax(scores, dim=-1)
        topk_vals, topk_idx = probs.topk(self.k, dim=-1)
        mask = torch.zeros_like(probs).scatter(-1, topk_idx, 1.0)
        weights = probs * mask
        weights = weights / (weights.sum(-1, keepdim=True) + 1e-8)
        outs = torch.stack([e(x) for e in self.experts], dim=1)
        result = (weights.unsqueeze(-1) * outs).sum(dim=1)
        with torch.no_grad():
            self._counts += (weights > 0).float().sum(0).cpu()
        return result

    def norm_entropy(self):
        c = self._counts / (self._counts.sum() + 1e-8)
        ent = -(c * (c + 1e-9).log()).sum().item()
        return ent / math.log(self.n_experts) if self.n_experts > 1 else 0.0

    def reset(self):
        self._counts = torch.zeros(self.n_experts)


# ─────────────────────────────────────────────────────────────
# Training
# ─────────────────────────────────────────────────────────────
def get_device():
    if torch.backends.mps.is_available():
        return torch.device('mps')
    if torch.cuda.is_available():
        return torch.device('cuda')
    return torch.device('cpu')


def train_eval(model, train_loader, test_loader, device, epochs=10, lr=1e-3):
    model.to(device)
    model.reset()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()

    for epoch in range(epochs):
        model.train()
        for bx, by in train_loader:
            bx = bx.view(bx.size(0), -1).to(device)
            by = by.to(device)
            optimizer.zero_grad()
            loss = criterion(model(bx), by)
            loss.backward()
            optimizer.step()

    model.eval()
    correct = total = 0
    final_loss = 0.0
    with torch.no_grad():
        for bx, by in test_loader:
            bx = bx.view(bx.size(0), -1).to(device)
            by = by.to(device)
            out = model(bx)
            final_loss += criterion(out, by).item()
            pred = out.argmax(-1)
            correct += (pred == by).sum().item()
            total += by.size(0)

    acc = correct / total * 100.0
    final_loss = final_loss / len(test_loader)
    ent = model.norm_entropy()
    return acc, final_loss, ent


def multi_seed(model_fn, train_loader, test_loader, device, epochs=10, seeds=(42, 137, 256)):
    accs, losses, ents = [], [], []
    for seed in seeds:
        torch.manual_seed(seed)
        np.random.seed(seed)
        model = model_fn()
        acc, loss, ent = train_eval(model, train_loader, test_loader, device, epochs=epochs)
        accs.append(acc)
        losses.append(loss)
        ents.append(ent)
    return np.mean(accs), np.std(accs), np.mean(losses), np.mean(ents)


# ─────────────────────────────────────────────────────────────
# ASCII bar
# ─────────────────────────────────────────────────────────────
def ascii_bar(value, lo, hi, width=45):
    if hi <= lo:
        return '#' * width
    bar_len = max(0, min(width, int((value - lo) / (hi - lo) * width)))
    return '#' * bar_len + '.' * (width - bar_len)


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────
def main():
    t0 = time.time()
    device = get_device()

    print("=" * 72)
    print("  Experiment: ADE Activation Threshold vs Golden Zone Boundary")
    print("  Testing activation ratios derived from n=6 and Lie theory")
    print("=" * 72)
    print(f"\n  Device: {device}")
    print(f"  1/e = {INV_E:.4f}   1/3 = {1/3:.4f}   1/2 = 0.5000   1-1/e = {ONE_MINUS_INV_E:.4f}")
    print(f"  G2 sigma=12, tau=4 => k/n candidates: 1/4=0.25, 1/3=0.333, 1/2=0.5")

    print("\n  Loading MNIST ...", end=" ", flush=True)
    train_loader, test_loader = load_mnist(batch_size=64, data_dir=os.path.join(_HERE, '..', 'data'))
    print("done.")

    INPUT_DIM = 784
    HIDDEN_DIM = 48
    OUTPUT_DIM = 10
    EPOCHS = 10

    # ────────────────────────────────────────────────
    # Part 1: Activation ratio sweep on n=12 (G2/sigma(6))
    # ────────────────────────────────────────────────
    print("\n" + "=" * 72)
    print("Part 1: Activation Ratio Sweep  (n_experts=12, hidden=48)")
    print("        Ratios include ADE-derived: 1/4, 1/3, 1/2")
    print("=" * 72)

    # k values for n=12 covering the candidate thresholds
    k_candidates_12 = [
        (1,  '1/12=0.083'),
        (2,  '1/6 =0.167'),
        (3,  '1/4 =0.250  [G2 sigma/3]'),
        (4,  '1/3 =0.333  [tau/sigma=meta fixed pt]'),
        (5,  '5/12=0.417  '),
        (6,  '1/2 =0.500  [Riemann / Golden upper]'),
        (7,  '7/12=0.583  '),
        (8,  '2/3 =0.667  [~1-1/e]'),
        (9,  '3/4 =0.750  '),
        (10, '5/6 =0.833  [Compass upper 5/6]'),
        (11, '11/12=0.917 '),
        (12, '12/12=1.0   [Dense]'),
    ]

    part1_results = []
    for k, label in k_candidates_12:
        ratio = k / 12
        mean_acc, std_acc, mean_loss, mean_ent = multi_seed(
            lambda k=k: TopKMoE(INPUT_DIM, HIDDEN_DIM, OUTPUT_DIM, n_experts=12, k=k),
            train_loader, test_loader, device, epochs=EPOCHS
        )
        part1_results.append({
            'k': k, 'ratio': ratio, 'label': label,
            'mean_acc': mean_acc, 'std_acc': std_acc,
            'mean_loss': mean_loss, 'norm_entropy': mean_ent,
        })
        print(f"  k={k:2d} ({label:35s}) acc={mean_acc:.2f}+/-{std_acc:.2f}%  loss={mean_loss:.4f}  ent={mean_ent:.4f}")

    # markdown table Part 1
    print("\n--- Markdown Table: n=12 Activation Ratio ---")
    print("| k | ratio | label | mean_acc% | std_acc | mean_loss | norm_entropy |")
    print("|---|-------|-------|-----------|---------|-----------|--------------|")
    for r in part1_results:
        lbl = r['label'].strip()
        print(f"| {r['k']} | {r['ratio']:.4f} | {lbl} | {r['mean_acc']:.2f} | {r['std_acc']:.2f} | {r['mean_loss']:.4f} | {r['norm_entropy']:.4f} |")

    # ASCII chart
    accs = [r['mean_acc'] for r in part1_results]
    lo, hi = min(accs), max(accs)
    best_k = part1_results[max(range(len(part1_results)), key=lambda i: part1_results[i]['mean_acc'])]['k']

    print("\nASCII Chart: k vs Accuracy (n=12)")
    print("-" * 72)
    for r in part1_results:
        bar = ascii_bar(r['mean_acc'], lo, hi)
        special = ''
        if abs(r['ratio'] - 1/3) < 0.01:
            special += ' <-- 1/3 (meta fixed pt)'
        elif abs(r['ratio'] - INV_E) < 0.03:
            special += ' <-- 1/e'
        elif abs(r['ratio'] - 0.5) < 0.01:
            special += ' <-- 1/2 (Riemann)'
        elif abs(r['ratio'] - ONE_MINUS_INV_E) < 0.04:
            special += ' <-- 1-1/e'
        best_mark = ' <<<BEST' if r['k'] == best_k else ''
        print(f"  k={r['k']:2d}({r['ratio']:.3f}) |{bar}| {r['mean_acc']:.2f}%{best_mark}{special}")

    # ────────────────────────────────────────────────
    # Part 2: Same ratio sweep on n=8 (standard) for comparison
    # ────────────────────────────────────────────────
    print("\n" + "=" * 72)
    print("Part 2: Activation Ratio Sweep on n=8 (standard MoE baseline)")
    print("=" * 72)

    k_candidates_8 = [(k, f'{k}/8={k/8:.3f}') for k in range(1, 9)]
    part2_results = []
    for k, label in k_candidates_8:
        ratio = k / 8
        mean_acc, std_acc, mean_loss, mean_ent = multi_seed(
            lambda k=k: TopKMoE(INPUT_DIM, HIDDEN_DIM, OUTPUT_DIM, n_experts=8, k=k),
            train_loader, test_loader, device, epochs=EPOCHS
        )
        part2_results.append({
            'k': k, 'n': 8, 'ratio': ratio, 'label': label,
            'mean_acc': mean_acc, 'std_acc': std_acc,
            'mean_loss': mean_loss, 'norm_entropy': mean_ent,
        })
        print(f"  k={k}/8 ({label:15s}) acc={mean_acc:.2f}+/-{std_acc:.2f}%  loss={mean_loss:.4f}")

    # ────────────────────────────────────────────────
    # Part 3: Boltzmann temperature sweep on n=12
    # ────────────────────────────────────────────────
    print("\n" + "=" * 72)
    print("Part 3: Boltzmann Temperature Sweep  (n=12, k=4=tau(6))")
    print("        T in {0.1, 1/3, 1/e, 1/2, 1.0, e, 2, 5}")
    print("=" * 72)

    temperatures = [
        (0.1,       '0.100 (very sharp)'),
        (1/3,       f'1/3={1/3:.3f} (meta fixed pt)'),
        (INV_E,     f'1/e={INV_E:.3f} (Golden center)'),
        (0.5,       '1/2=0.500 (Riemann line)'),
        (1.0,       '1.0   (standard softmax)'),
        (E,         f'e={E:.3f}  (Boltzmann golden)'),
        (2.0,       '2.0   '),
        (5.0,       '5.0   (very soft)'),
    ]

    part3_results = []
    for T, label in temperatures:
        mean_acc, std_acc, mean_loss, mean_ent = multi_seed(
            lambda T=T: BoltzmannMoE(INPUT_DIM, HIDDEN_DIM, OUTPUT_DIM, n_experts=12, k=4, temperature=T),
            train_loader, test_loader, device, epochs=EPOCHS
        )
        part3_results.append({
            'T': T, 'label': label,
            'mean_acc': mean_acc, 'std_acc': std_acc,
            'mean_loss': mean_loss, 'norm_entropy': mean_ent,
        })
        print(f"  T={T:5.3f} ({label:30s}) acc={mean_acc:.2f}+/-{std_acc:.2f}%  ent={mean_ent:.4f}")

    # markdown table Part 3
    print("\n--- Markdown Table: Temperature Sweep (n=12, k=4) ---")
    print("| Temperature | Label | mean_acc% | std | mean_loss | norm_entropy |")
    print("|-------------|-------|-----------|-----|-----------|--------------|")
    for r in part3_results:
        print(f"| {r['T']:.4f} | {r['label'].strip()} | {r['mean_acc']:.2f} | {r['std_acc']:.2f} | {r['mean_loss']:.4f} | {r['norm_entropy']:.4f} |")

    # ASCII chart Part 3
    accs3 = [r['mean_acc'] for r in part3_results]
    lo3, hi3 = min(accs3), max(accs3)
    best_T = part3_results[max(range(len(part3_results)), key=lambda i: part3_results[i]['mean_acc'])]['T']

    print("\nASCII Chart: Temperature vs Accuracy (n=12, k=4)")
    print("-" * 72)
    for r in part3_results:
        bar = ascii_bar(r['mean_acc'], lo3, hi3)
        special = ''
        if abs(r['T'] - E) < 0.01:
            special = ' <-- T=e (Golden)'
        elif abs(r['T'] - 1/3) < 0.01:
            special = ' <-- T=1/3'
        elif abs(r['T'] - INV_E) < 0.01:
            special = ' <-- T=1/e'
        best_mark = ' <<<BEST' if abs(r['T'] - best_T) < 0.001 else ''
        print(f"  T={r['T']:5.3f} |{bar}| {r['mean_acc']:.2f}%{best_mark}{special}")

    # ────────────────────────────────────────────────
    # Summary
    # ────────────────────────────────────────────────
    best_k12 = max(part1_results, key=lambda r: r['mean_acc'])
    best_k8 = max(part2_results, key=lambda r: r['mean_acc'])
    best_t12 = max(part3_results, key=lambda r: r['mean_acc'])

    # Check if 1/3 ratio is near optimal for n=12
    ratio_1_3 = next((r for r in part1_results if r['k'] == 4), None)  # k=4/12 = 1/3
    ratio_1_4 = next((r for r in part1_results if r['k'] == 3), None)  # k=3/12 = 1/4

    elapsed = time.time() - t0
    print("\n" + "=" * 72)
    print("SUMMARY")
    print("=" * 72)
    print(f"\n  Total time: {elapsed:.1f}s")
    print(f"\n  Part 1 — Best activation ratio for n=12:")
    print(f"    Best k={best_k12['k']} (ratio={best_k12['ratio']:.3f}) acc={best_k12['mean_acc']:.2f}%")
    print(f"    tau(6)/sigma(6)=1/3 (k=4): acc={ratio_1_3['mean_acc']:.2f}% rank=?")
    print(f"    1/4 (k=3, G2 sigma/3):     acc={ratio_1_4['mean_acc']:.2f}%")
    print(f"    Delta best vs 1/3:  {best_k12['mean_acc'] - ratio_1_3['mean_acc']:+.2f}%")

    print(f"\n  Part 2 — Best activation ratio for n=8 (baseline):")
    print(f"    Best k={best_k8['k']}/8 (ratio={best_k8['ratio']:.3f}) acc={best_k8['mean_acc']:.2f}%")

    print(f"\n  Part 3 — Best Boltzmann temperature for n=12, k=4:")
    print(f"    Best T={best_t12['T']:.4f} ({best_t12['label'].strip()}) acc={best_t12['mean_acc']:.2f}%")
    t_e_r = next((r for r in part3_results if abs(r['T'] - E) < 0.01), None)
    t_1_3 = next((r for r in part3_results if abs(r['T'] - 1/3) < 0.01), None)
    if t_e_r:
        print(f"    T=e (Golden):  acc={t_e_r['mean_acc']:.2f}%")
    if t_1_3:
        print(f"    T=1/3:         acc={t_1_3['mean_acc']:.2f}%")

    # Verdict
    print()
    hypothesis_checks = []
    if ratio_1_3 and ratio_1_3['mean_acc'] >= best_k12['mean_acc'] - 0.2:
        print("  H-LIE-2 activation (1/3): SUPPORTED — k=4/12 within 0.2% of best")
        hypothesis_checks.append(True)
    else:
        delta = best_k12['mean_acc'] - ratio_1_3['mean_acc'] if ratio_1_3 else float('nan')
        print(f"  H-LIE-2 activation (1/3): NOT confirmed — {delta:.2f}% gap from best")
        hypothesis_checks.append(False)

    if t_e_r and t_e_r['mean_acc'] >= max(accs3) - 0.2:
        print("  H-LIE-2 temperature (T=e): SUPPORTED — T=e within 0.2% of best")
        hypothesis_checks.append(True)
    else:
        delta = max(accs3) - t_e_r['mean_acc'] if t_e_r else float('nan')
        print(f"  H-LIE-2 temperature (T=e): NOT confirmed — {delta:.2f}% gap from best")
        hypothesis_checks.append(False)

    print("=" * 72)


if __name__ == '__main__':
    main()
