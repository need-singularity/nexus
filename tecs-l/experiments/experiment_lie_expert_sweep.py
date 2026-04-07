#!/usr/bin/env python3
"""Experiment: Lie Algebra Root System Size vs MoE Expert Count

Hypothesis (H-LIE-1):
  The sizes of exceptional Lie algebra root systems are arithmetic in n=6:
    |G2| = 12 = sigma(6)
    |F4| = 48 = 8 * sigma(6)
    |E6| = 72 = 12 * sigma(6) - sigma(6) * 2 = 6 * tau(6) * sigma(6) / tau(6)
    |E7| = 126 = C(9,2) = 9*7
    |E8| = 240 = sigma_1(120) related

  These numbers may be optimal for MoE expert counts, because they arise from
  the same combinatorial structure that governs maximum symmetry.

Comparison:
  Lie root system sizes:  {4, 6, 8, 12, 24, 48, 72, 126, 240}
  Standard powers of 2:   {4, 8, 16, 32, 64, 128, 256}
  (4 and 8 overlap to provide a fair shared baseline)

Metrics:
  - Final accuracy (mean +/- std over 3 seeds)
  - Training loss
  - Expert utilization balance (std of usage distribution)
  - Load balance entropy (higher = more balanced)
  - Active ratio
  - Params per expert

Dataset: MNIST (flat 784-dim)
Model:   MoE with TopK gate, hidden_dim=48 per expert (fixed, comparable params)
Epochs:  10 per trial, 3 seeds
Device:  MPS (Apple Silicon) or CPU fallback
"""

import sys
import os
import time
import math

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

# --- path for model_utils ---
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))

from model_utils import load_mnist, count_params

# ─────────────────────────────────────────────────────────────
# Constants from Lie theory and n=6 arithmetic
# ─────────────────────────────────────────────────────────────
LIE_ROOT_SIZES = {
    'A3(n=6 trivial)':  4,   # A1 minimal nontrivial, included for baseline overlap
    'A5':               6,
    'D4':               8,   # also 2^3, baseline overlap
    'G2':              12,   # |G2| = 12 = sigma(6)
    'D6':              24,
    'F4':              48,   # |F4| = 48
    'E6':              72,   # |E6| = 72
    'E7':             126,   # |E7| = 126
    'E8':             240,   # |E8| = 240
}

POWER_OF_2_SIZES = {
    'Pow2-4':    4,
    'Pow2-8':    8,
    'Pow2-16':  16,
    'Pow2-32':  32,
    'Pow2-64':  64,
    'Pow2-128': 128,
    'Pow2-256': 256,
}

# Active fraction k/n derived from n=6 arithmetic: tau(6)/sigma(6) = 4/12 = 1/3
ACTIVE_RATIO = 1.0 / 3.0


# ─────────────────────────────────────────────────────────────
# Model
# ─────────────────────────────────────────────────────────────
class LieExpert(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim),
        )

    def forward(self, x):
        return self.net(x)


class LieMoE(nn.Module):
    """MoE with a TopK gate.  k = max(1, round(n_experts * active_ratio))."""

    def __init__(self, input_dim, hidden_dim, output_dim, n_experts, active_ratio=ACTIVE_RATIO):
        super().__init__()
        self.n_experts = n_experts
        self.k = max(1, round(n_experts * active_ratio))
        self.experts = nn.ModuleList([
            LieExpert(input_dim, hidden_dim, output_dim)
            for _ in range(n_experts)
        ])
        self.gate = nn.Linear(input_dim, n_experts)

        # Tracking
        self.expert_counts = torch.zeros(n_experts)
        self.n_batches = 0

    def forward(self, x):
        scores = self.gate(x)                                   # (B, n)
        topk_vals, topk_idx = scores.topk(self.k, dim=-1)       # (B, k)
        mask = torch.zeros_like(scores).scatter(-1, topk_idx, 1.0)
        weights = F.softmax(scores, dim=-1) * mask              # (B, n)
        weights = weights / (weights.sum(-1, keepdim=True) + 1e-8)

        outs = torch.stack([e(x) for e in self.experts], dim=1)  # (B, n, out)
        result = (weights.unsqueeze(-1) * outs).sum(dim=1)       # (B, out)

        with torch.no_grad():
            self.expert_counts += (weights > 0).float().sum(dim=0).cpu()
            self.n_batches += 1

        return result

    def get_utilization_metrics(self):
        counts = self.expert_counts / (self.expert_counts.sum() + 1e-8)
        usage_std = counts.std().item()
        # Entropy of usage distribution: higher = more balanced
        entropy = -(counts * (counts + 1e-9).log()).sum().item()
        max_entropy = math.log(self.n_experts)
        norm_entropy = entropy / max_entropy if max_entropy > 0 else 0.0
        active_ratio = self.k / self.n_experts
        return {
            'usage_std': usage_std,
            'load_entropy': entropy,
            'norm_entropy': norm_entropy,
            'active_ratio': active_ratio,
            'k': self.k,
        }

    def reset_metrics(self):
        self.expert_counts = torch.zeros(self.n_experts)
        self.n_batches = 0


# ─────────────────────────────────────────────────────────────
# Training helpers
# ─────────────────────────────────────────────────────────────
def get_device():
    if torch.backends.mps.is_available():
        return torch.device('mps')
    if torch.cuda.is_available():
        return torch.device('cuda')
    return torch.device('cpu')


def train_and_eval(model, train_loader, test_loader, device, epochs=10, lr=1e-3):
    model.to(device)
    model.reset_metrics()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()

    losses = []
    for epoch in range(epochs):
        model.train()
        total_loss = 0.0
        for bx, by in train_loader:
            bx = bx.view(bx.size(0), -1).to(device)
            by = by.to(device)
            optimizer.zero_grad()
            out = model(bx)
            loss = criterion(out, by)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        losses.append(total_loss / len(train_loader))

    model.eval()
    correct = total = 0
    with torch.no_grad():
        for bx, by in test_loader:
            bx = bx.view(bx.size(0), -1).to(device)
            by = by.to(device)
            pred = model(bx).argmax(dim=-1)
            correct += (pred == by).sum().item()
            total += by.size(0)
    acc = correct / total * 100.0
    final_loss = losses[-1]
    return acc, final_loss, losses


# ─────────────────────────────────────────────────────────────
# ASCII bar chart
# ─────────────────────────────────────────────────────────────
def ascii_bar(value, lo, hi, width=40):
    if hi <= lo:
        bar_len = width
    else:
        bar_len = int((value - lo) / (hi - lo) * width)
    bar_len = max(0, min(width, bar_len))
    return '#' * bar_len + '.' * (width - bar_len)


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────
def run_group(name_sizes, label, train_loader, test_loader, device,
              hidden_dim=48, epochs=10, n_seeds=3):
    """Run all configs in a name->n_experts dict, return list of result dicts."""
    results = []
    for config_name, n_exp in name_sizes.items():
        accs, final_losses, util_records = [], [], []
        for seed in [42, 137, 256]:
            torch.manual_seed(seed)
            np.random.seed(seed)
            model = LieMoE(784, hidden_dim, 10, n_experts=n_exp)
            acc, loss, _ = train_and_eval(
                model, train_loader, test_loader, device,
                epochs=epochs, lr=1e-3
            )
            util = model.get_utilization_metrics()
            accs.append(acc)
            final_losses.append(loss)
            util_records.append(util)
            print(f"    {config_name:20s} n={n_exp:4d}  seed={seed}  acc={acc:.2f}%  loss={loss:.4f}")

        params = count_params(LieMoE(784, hidden_dim, 10, n_experts=n_exp))
        mean_util = {k: np.mean([u[k] for u in util_records]) for k in util_records[0]}
        results.append({
            'name': config_name,
            'group': label,
            'n_experts': n_exp,
            'mean_acc': np.mean(accs),
            'std_acc': np.std(accs),
            'mean_loss': np.mean(final_losses),
            'std_loss': np.std(final_losses),
            'params': params,
            **mean_util,
        })
    return results


def print_markdown_table(results):
    """Print full results as markdown table."""
    header = (
        "| Config | Group | n_exp | k | active_ratio | "
        "mean_acc% | std_acc | mean_loss | usage_std | norm_entropy | params |"
    )
    sep = "|" + "|".join(["---"] * 12) + "|"
    print(header)
    print(sep)
    for r in results:
        print(
            f"| {r['name']} | {r['group']} | {r['n_experts']} | {r['k']} "
            f"| {r['active_ratio']:.3f} "
            f"| {r['mean_acc']:.2f} | {r['std_acc']:.2f} "
            f"| {r['mean_loss']:.4f} | {r['usage_std']:.4f} "
            f"| {r['norm_entropy']:.4f} | {r['params']:,} |"
        )


def print_ascii_charts(results):
    W = 45
    all_accs = [r['mean_acc'] for r in results]
    lo, hi = min(all_accs), max(all_accs)

    print("\nASCII Chart: Expert Count vs Accuracy")
    print("=" * 70)
    for r in sorted(results, key=lambda x: x['n_experts']):
        bar = ascii_bar(r['mean_acc'], lo, hi, W)
        group_tag = '[LIE]' if r['group'] == 'lie' else '[P2 ]'
        print(f"  {group_tag} n={r['n_experts']:4d} ({r['name'][:10]:10s}) |{bar}| {r['mean_acc']:.2f}%")

    all_entropies = [r['norm_entropy'] for r in results]
    lo_e, hi_e = min(all_entropies), max(all_entropies)

    print("\nASCII Chart: Expert Count vs Load Balance Entropy (higher=better)")
    print("=" * 70)
    for r in sorted(results, key=lambda x: x['n_experts']):
        bar = ascii_bar(r['norm_entropy'], lo_e, hi_e, W)
        group_tag = '[LIE]' if r['group'] == 'lie' else '[P2 ]'
        print(f"  {group_tag} n={r['n_experts']:4d} ({r['name'][:10]:10s}) |{bar}| {r['norm_entropy']:.4f}")


def analyze_groups(results):
    lie_results = [r for r in results if r['group'] == 'lie']
    p2_results = [r for r in results if r['group'] == 'power2']

    # exclude shared overlap values {4, 8} from comparison to avoid double-counting
    lie_only = [r for r in lie_results if r['n_experts'] not in (4, 8)]
    p2_only = [r for r in p2_results if r['n_experts'] not in (4, 8)]

    lie_mean_acc = np.mean([r['mean_acc'] for r in lie_only]) if lie_only else float('nan')
    p2_mean_acc = np.mean([r['mean_acc'] for r in p2_only]) if p2_only else float('nan')
    lie_mean_ent = np.mean([r['norm_entropy'] for r in lie_only]) if lie_only else float('nan')
    p2_mean_ent = np.mean([r['norm_entropy'] for r in p2_only]) if p2_only else float('nan')

    print("\n" + "=" * 70)
    print("GROUP ANALYSIS (excluding shared baselines n=4, n=8)")
    print("=" * 70)
    print(f"  Lie root sizes (unique): {[r['n_experts'] for r in lie_only]}")
    print(f"  Power-of-2  (unique):    {[r['n_experts'] for r in p2_only]}")
    print()
    print(f"  Mean accuracy  — Lie: {lie_mean_acc:.2f}%  |  Power-of-2: {p2_mean_acc:.2f}%")
    print(f"  Delta (Lie - P2):  {lie_mean_acc - p2_mean_acc:+.2f}%")
    print()
    print(f"  Mean norm-entropy — Lie: {lie_mean_ent:.4f}  |  Power-of-2: {p2_mean_ent:.4f}")
    print(f"  Delta (Lie - P2):  {lie_mean_ent - p2_mean_ent:+.4f}")

    # Best configs per group
    best_lie = max(lie_results, key=lambda r: r['mean_acc'])
    best_p2 = max(p2_results, key=lambda r: r['mean_acc'])
    print()
    print(f"  Best Lie config:    {best_lie['name']} (n={best_lie['n_experts']})  acc={best_lie['mean_acc']:.2f}%")
    print(f"  Best Power-of-2:    {best_p2['name']}  (n={best_p2['n_experts']})  acc={best_p2['mean_acc']:.2f}%")

    # Hypothesis verdict
    print()
    if lie_mean_acc > p2_mean_acc:
        print("  VERDICT: Lie root system sizes OUTPERFORM power-of-2 on average.")
        print("           H-LIE-1 SUPPORTED (accuracy)")
    else:
        print("  VERDICT: Power-of-2 sizes match or outperform Lie root system sizes.")
        print("           H-LIE-1 NOT SUPPORTED by accuracy alone.")
    if lie_mean_ent > p2_mean_ent:
        print("           Load balance is BETTER for Lie sizes (higher entropy).")
    else:
        print("           Load balance is WORSE or equal for Lie sizes.")


def main():
    t0 = time.time()
    device = get_device()
    print("=" * 70)
    print("  Experiment: Lie Root System Sizes as Optimal MoE Expert Counts")
    print("  Hypothesis: |G2|=12, |F4|=48, |E6|=72, |E7|=126, |E8|=240")
    print("              arise from n=6 arithmetic => optimal for MoE")
    print("=" * 70)
    print(f"\n  Device: {device}")
    print(f"  Active ratio k/n = tau(6)/sigma(6) = 4/12 = 1/3 = {ACTIVE_RATIO:.4f}")
    print(f"  Hidden dim per expert: 48  |  Epochs: 10  |  Seeds: 3")

    print("\n  Loading MNIST data ...", end=" ", flush=True)
    train_loader, test_loader = load_mnist(batch_size=64, data_dir=os.path.join(_HERE, '..', 'data'))
    print("done.")

    print("\n--- Running Lie root system sizes ---")
    lie_results = run_group(LIE_ROOT_SIZES, 'lie', train_loader, test_loader, device)

    print("\n--- Running power-of-2 baseline sizes ---")
    p2_results = run_group(POWER_OF_2_SIZES, 'power2', train_loader, test_loader, device)

    all_results = lie_results + p2_results

    # ── Full markdown table ──
    print("\n\n" + "=" * 70)
    print("FULL RESULTS — Markdown Table")
    print("=" * 70)
    print_markdown_table(sorted(all_results, key=lambda r: r['n_experts']))

    # ── ASCII charts ──
    print_ascii_charts(all_results)

    # ── Group analysis ──
    analyze_groups(all_results)

    # ── Notable n=6 predictions ──
    print("\n" + "=" * 70)
    print("NOTABLE: G2/sigma(6) = 12  prediction check")
    print("=" * 70)
    g2_r = next((r for r in lie_results if r['n_experts'] == 12), None)
    d6_r = next((r for r in lie_results if r['n_experts'] == 24), None)
    p2_8 = next((r for r in p2_results if r['n_experts'] == 8), None)
    p2_16 = next((r for r in p2_results if r['n_experts'] == 16), None)
    if g2_r and p2_8 and p2_16:
        print(f"  n=12 (G2, sigma(6)):  acc={g2_r['mean_acc']:.2f}%  entropy={g2_r['norm_entropy']:.4f}")
        print(f"  n= 8 (power-of-2):    acc={p2_8['mean_acc']:.2f}%  entropy={p2_8['norm_entropy']:.4f}")
        print(f"  n=16 (power-of-2):    acc={p2_16['mean_acc']:.2f}%  entropy={p2_16['norm_entropy']:.4f}")
        g2_vs_p2 = g2_r['mean_acc'] - max(p2_8['mean_acc'], p2_16['mean_acc'])
        print(f"  G2 vs best neighbor P2: {g2_vs_p2:+.2f}%")
    if d6_r:
        p2_32 = next((r for r in p2_results if r['n_experts'] == 32), None)
        if p2_32:
            print(f"  n=24 (D6):            acc={d6_r['mean_acc']:.2f}%  entropy={d6_r['norm_entropy']:.4f}")
            print(f"  n=32 (power-of-2):    acc={p2_32['mean_acc']:.2f}%  entropy={p2_32['norm_entropy']:.4f}")

    elapsed = time.time() - t0
    print(f"\n  Total elapsed: {elapsed:.1f}s")
    print("=" * 70)


if __name__ == '__main__':
    main()
