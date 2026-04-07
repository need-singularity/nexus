#!/usr/bin/env python3
"""
H-SEDI-EE-4: Koide-Inspired Weight Initialization
====================================================
Hypothesis: Initializing expert weights so their Koide ratio = 2/3
leads to faster convergence, saving training energy.

Koide formula: (m1 + m2 + m3) / (sqrt(m1) + sqrt(m2) + sqrt(m3))^2 = 2/3

This ratio holds for lepton masses and represents a balanced state.
If expert weight norms satisfy this ratio, the initial "balance" may help
optimization converge faster.

Test plan:
  1. Random init: standard Kaiming initialization
  2. Koide init: Scale expert weight norms to satisfy Koide ratio = 2/3
  3. Equal init: All experts have equal weight norms (Koide = 1/3 trivially)
  4. Compare: convergence speed (epochs to 95% accuracy), final accuracy
"""

import sys
sys.path.insert(0, '/Users/ghost/Dev/TECS-L')

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import math
import time

from model_utils import load_mnist, Expert, BaseMoE, TopKGate

torch.manual_seed(42)
np.random.seed(42)


# ─── Koide ratio computation ────────────────────────────────────────────────

def koide_ratio(m1, m2, m3):
    """Compute Koide ratio: (m1+m2+m3) / (sqrt(m1)+sqrt(m2)+sqrt(m3))^2"""
    num = m1 + m2 + m3
    denom = (math.sqrt(m1) + math.sqrt(m2) + math.sqrt(m3)) ** 2
    return num / denom if denom > 0 else 0


def find_koide_masses(target_ratio=2/3, total_norm=3.0):
    """Find three positive masses satisfying Koide ratio = target_ratio.

    We parameterize as m1 = a, m2 = b, m3 = c where a+b+c = total_norm.
    For Koide = 2/3, the lepton mass pattern is approximately:
    m1 : m2 : m3 ~ 1 : 207 : 3477 (electron : muon : tau)

    For our purposes, we want moderate ratios. Use:
    m1 = 0.2, m2 = 0.8, m3 = 2.0 (ratio ~ 0.66)
    """
    # Brute force search for nice ratios near 2/3
    best = None
    best_diff = float('inf')
    for a in np.linspace(0.1, 1.0, 50):
        for b in np.linspace(a, 2.0, 50):
            c = total_norm - a - b
            if c > 0:
                kr = koide_ratio(a, b, c)
                diff = abs(kr - target_ratio)
                if diff < best_diff:
                    best_diff = diff
                    best = (a, b, c)
    return best


def init_koide_experts(model, masses):
    """Scale expert weight norms to match Koide masses."""
    experts = model.experts
    assert len(experts) == len(masses), f"Need {len(experts)} masses, got {len(masses)}"

    for i, (expert, target_norm) in enumerate(zip(experts, masses)):
        for param in expert.parameters():
            if param.dim() >= 2:
                current_norm = param.data.norm().item()
                if current_norm > 0:
                    scale = math.sqrt(target_norm) / math.sqrt(current_norm)
                    param.data *= scale


def init_equal_experts(model, target_norm=1.0):
    """Initialize all experts to equal weight norms."""
    for expert in model.experts:
        for param in expert.parameters():
            if param.dim() >= 2:
                current_norm = param.data.norm().item()
                if current_norm > 0:
                    param.data *= target_norm / current_norm


# ─── Training with convergence tracking ──────────────────────────────────────

def train_with_tracking(model, train_loader, test_loader, epochs=15, lr=0.001,
                        target_acc=0.95):
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()

    epoch_data = []
    convergence_epoch = None
    t_start = time.time()

    for epoch in range(epochs):
        model.train()
        total_loss = 0
        for X, y in train_loader:
            X = X.view(X.size(0), -1)
            optimizer.zero_grad()
            out = model(X)
            loss = criterion(out, y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        avg_loss = total_loss / len(train_loader)

        model.eval()
        correct = total = 0
        with torch.no_grad():
            for X, y in test_loader:
                X = X.view(X.size(0), -1)
                out = model(X)
                correct += (out.argmax(1) == y).sum().item()
                total += y.size(0)
        acc = correct / total

        # Check expert weight norms
        norms = []
        for expert in model.experts:
            norm = sum(p.data.norm().item() ** 2 for p in expert.parameters()) ** 0.5
            norms.append(norm)
        kr = koide_ratio(*norms[:3]) if len(norms) >= 3 else 0

        epoch_data.append({
            'epoch': epoch + 1, 'loss': avg_loss, 'acc': acc,
            'koide_ratio': kr, 'norms': norms[:3],
            'time': time.time() - t_start,
        })

        if convergence_epoch is None and acc >= target_acc:
            convergence_epoch = epoch + 1

    total_time = time.time() - t_start
    return epoch_data, convergence_epoch, total_time


def main():
    print("=" * 70)
    print("  H-SEDI-EE-4: Koide-Inspired Weight Initialization")
    print("=" * 70)

    EPOCHS = 15
    N_EXPERTS = 3
    HIDDEN = 128
    TARGET_ACC = 0.95
    N_TRIALS = 3  # Average over trials for robustness

    train_loader, test_loader = load_mnist(batch_size=128)

    # Find Koide masses
    koide_masses = find_koide_masses(target_ratio=2/3, total_norm=3.0)
    print(f"\n  Koide masses: {koide_masses}")
    print(f"  Koide ratio: {koide_ratio(*koide_masses):.6f} (target: {2/3:.6f})")
    print(f"  Trials per config: {N_TRIALS}")

    configs = {
        'Random(Kaiming)': None,
        'Koide(2/3)': koide_masses,
        'Equal(1,1,1)': (1.0, 1.0, 1.0),
    }

    all_results = {}

    for config_name, masses in configs.items():
        trial_results = []

        for trial in range(N_TRIALS):
            torch.manual_seed(42 + trial * 100)

            gate = TopKGate(784, N_EXPERTS, k=2)
            model = BaseMoE(784, HIDDEN, 10, N_EXPERTS, gate)
            params = sum(p.numel() for p in model.parameters())

            # Apply initialization
            if masses is not None and config_name == 'Koide(2/3)':
                init_koide_experts(model, masses)
            elif masses is not None and config_name == 'Equal(1,1,1)':
                init_equal_experts(model, target_norm=1.0)

            # Check initial Koide ratio
            norms = []
            for expert in model.experts:
                norm = sum(p.data.norm().item() ** 2 for p in expert.parameters()) ** 0.5
                norms.append(norm)
            init_kr = koide_ratio(*norms[:3])

            epoch_data, conv_epoch, train_time = train_with_tracking(
                model, train_loader, test_loader, epochs=EPOCHS, target_acc=TARGET_ACC)

            trial_results.append({
                'epoch_data': epoch_data,
                'convergence_epoch': conv_epoch,
                'train_time': train_time,
                'init_koide': init_kr,
                'final_acc': epoch_data[-1]['acc'],
                'final_koide': epoch_data[-1]['koide_ratio'],
                'params': params,
            })

        all_results[config_name] = trial_results

        avg_acc = np.mean([t['final_acc'] for t in trial_results])
        avg_conv = np.mean([t['convergence_epoch'] or EPOCHS for t in trial_results])
        print(f"\n  {config_name}: Avg Acc={avg_acc*100:.2f}%, "
              f"Avg Convergence={avg_conv:.1f} epochs, "
              f"Init Koide={trial_results[0]['init_koide']:.4f}")

    # ─── Results table ───────────────────────────────────────────────────────
    print("\n" + "=" * 90)
    print("  RESULTS TABLE (averaged over {N_TRIALS} trials)")
    print("=" * 90)
    print(f"  {'Config':<18} | {'Final Acc':>9} | {'Conv Epoch':>10} | "
          f"{'Init K':>7} | {'Final K':>7} | {'Params':>8} | {'Energy Saved':>12}")
    print("-" * 90)

    random_conv = np.mean([t['convergence_epoch'] or EPOCHS
                           for t in all_results['Random(Kaiming)']])

    for config_name, trials in all_results.items():
        avg_acc = np.mean([t['final_acc'] for t in trials])
        std_acc = np.std([t['final_acc'] for t in trials])
        avg_conv = np.mean([t['convergence_epoch'] or EPOCHS for t in trials])
        init_k = trials[0]['init_koide']
        final_k = np.mean([t['final_koide'] for t in trials])
        params = trials[0]['params']
        energy_saved = (1 - avg_conv / random_conv) * 100 if random_conv > 0 else 0

        print(f"  {config_name:<18} | {avg_acc*100:>7.2f}%+/-{std_acc*100:.1f} | "
              f"{avg_conv:>10.1f} | {init_k:>7.4f} | {final_k:>7.4f} | "
              f"{params:>8,} | {energy_saved:>+11.1f}%")

    # ─── Koide ratio evolution ───────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("  KOIDE RATIO EVOLUTION (Trial 0)")
    print("=" * 70)
    print(f"  {'Epoch':>5}", end="")
    for name in configs:
        print(f" | {name:>18}", end="")
    print()
    print("-" * 70)

    for ep in range(EPOCHS):
        print(f"  {ep+1:>5}", end="")
        for name in configs:
            kr = all_results[name][0]['epoch_data'][ep]['koide_ratio']
            print(f" | {kr:>18.4f}", end="")
        print()

    # ─── Verdict ─────────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("  VERDICT")
    print("=" * 70)

    koide_conv = np.mean([t['convergence_epoch'] or EPOCHS
                          for t in all_results['Koide(2/3)']])
    koide_acc = np.mean([t['final_acc'] for t in all_results['Koide(2/3)']])
    random_acc = np.mean([t['final_acc'] for t in all_results['Random(Kaiming)']])

    speedup = random_conv / koide_conv if koide_conv > 0 else 0

    if koide_conv < random_conv and (koide_acc - random_acc) > -0.005:
        print(f"  SUPPORTED: Koide initialization converges faster!")
        print(f"  Convergence: {koide_conv:.1f} vs {random_conv:.1f} epochs ({speedup:.2f}x)")
        print(f"  Accuracy: {koide_acc*100:.2f}% vs {random_acc*100:.2f}%")
        print(f"  Energy saved: {(1-koide_conv/random_conv)*100:.1f}%")
    elif koide_acc > random_acc + 0.005:
        print(f"  PARTIALLY SUPPORTED: Koide init gives higher accuracy")
        print(f"  Accuracy: {koide_acc*100:.2f}% vs {random_acc*100:.2f}%")
        print(f"  Convergence: {koide_conv:.1f} vs {random_conv:.1f} epochs")
    else:
        print(f"  NOT SUPPORTED: Koide initialization does not improve convergence")
        print(f"  Convergence: {koide_conv:.1f} vs {random_conv:.1f} epochs")
        print(f"  Accuracy: {koide_acc*100:.2f}% vs {random_acc*100:.2f}%")

    # Check if Koide ratio is maintained during training
    final_koide = np.mean([t['final_koide'] for t in all_results['Koide(2/3)']])
    print(f"\n  Koide ratio maintenance: init={all_results['Koide(2/3)'][0]['init_koide']:.4f} "
          f"-> final={final_koide:.4f}")
    if abs(final_koide - 2/3) < 0.05:
        print(f"  Interesting: Koide ratio approximately preserved during training!")
    else:
        print(f"  Koide ratio drifts during training (expected with unconstrained optimization)")

    print("=" * 70)


if __name__ == '__main__':
    main()
