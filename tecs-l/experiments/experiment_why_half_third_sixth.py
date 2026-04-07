#!/usr/bin/env python3
"""Why is {1/2, 1/3, 1/6} optimal? Systematic investigation.

CONTEXT: {1/2, 1/3, 1/6} fixed weights beat learned weights on BOTH MNIST and CIFAR.
These are the reciprocals of divisors of the perfect number 6.
Sum = 1 (valid probability distribution).

This experiment systematically tests:
1. Exhaustive weight comparison (10+ schemes)
2. Entropy analysis (is there an optimal entropy?)
3. Weight drift analysis (do learned weights converge to {1/2,1/3,1/6}?)
4. Asymmetry vs exact values (is it the specific fractions or the shape?)
5. CIFAR validation (top schemes from MNIST)
"""

import os
import sys
import builtins

# Force flush on every print
_original_print = builtins.print
def print(*args, **kwargs):
    kwargs.setdefault('flush', True)
    _original_print(*args, **kwargs)
builtins.print = print

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import math
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from model_utils import (
    Expert, TopKGate, BoltzmannGate, BaseMoE, DenseModel,
    load_mnist, load_cifar10, train_and_evaluate, compare_results, count_params,
    SIGMA, TAU, PHI, DIVISOR_RECIPROCALS, H_TARGET
)
from model_meta_engine import (
    EngineA, EngineE, EngineG, EngineF,
    ContractionMetaRouter, DivisorCombiner, MetaEngine,
)


def set_seed(seed):
    torch.manual_seed(seed)
    np.random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


# ─────────────────────────────────────────
# Custom MetaEngine with injectable weights
# ─────────────────────────────────────────

class MetaEngineCustomWeights(nn.Module):
    """MetaEngine(AEGF, routing='fixed') with custom initial combiner weights.

    DivisorCombiner uses F.softmax(self.weights) in forward().
    To get desired output weights w*, we set init = log(w*).
    """
    def __init__(self, input_dim=784, hidden_dim=48, output_dim=10,
                 target_weights=None, freeze_combiner=True):
        super().__init__()
        self.engine_names = list('AEGF')
        self.engines = nn.ModuleDict({
            'A': EngineA(input_dim, hidden_dim, output_dim),
            'E': EngineE(input_dim, hidden_dim, output_dim),
            'G': EngineG(input_dim, hidden_dim, output_dim),
            'F': EngineF(input_dim, hidden_dim, output_dim),
        })
        n = 4
        self.combiner = DivisorCombiner(n)

        if target_weights is not None:
            tw = torch.tensor(target_weights, dtype=torch.float)
            tw = tw / tw.sum()
            log_tw = torch.log(tw + 1e-10)
            self.combiner.weights = nn.Parameter(log_tw)

        if freeze_combiner:
            self.combiner.weights.requires_grad = False

        self.routing_mode = 'fixed'
        self.aux_loss = torch.tensor(0.0)

    def forward(self, x):
        engine_outputs = []
        self.aux_loss = torch.tensor(0.0, device=x.device)
        for name in self.engine_names:
            out = self.engines[name](x)
            engine_outputs.append(out)
            if name == 'G' and hasattr(self.engines['G'], 'entropy_loss'):
                self.aux_loss = self.aux_loss + self.engines['G'].entropy_loss
        routed = self.combiner(engine_outputs)
        return (routed, self.aux_loss)

    def get_effective_weights(self):
        with torch.no_grad():
            return F.softmax(self.combiner.weights, dim=0).numpy()


# ─────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────

def shannon_entropy(weights):
    w = np.array(weights, dtype=np.float64)
    w = w[w > 1e-9]
    w = w / w.sum()
    return -np.sum(w * np.log(w))


def train_scheme(weights, train_loader, test_loader,
                 epochs=10, seed=42, input_dim=784, verbose=False):
    set_seed(seed)
    model = MetaEngineCustomWeights(
        input_dim=input_dim, target_weights=weights, freeze_combiner=True
    )
    eff_w = model.get_effective_weights()
    if verbose:
        print(f"    Effective weights: [{', '.join(f'{x:.4f}' for x in eff_w)}]")
    _, accs = train_and_evaluate(
        model, train_loader, test_loader, epochs=epochs,
        aux_lambda=0.01, verbose=verbose
    )
    return accs[-1], eff_w


def train_meta_with_tracking(train_loader, test_loader, epochs=10, seed=42):
    """Train MetaEngine with meta routing, track route weight evolution."""
    set_seed(seed)
    model = MetaEngine(routing='meta')
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.CrossEntropyLoss()

    weight_snapshots = []

    for epoch in range(epochs):
        model.train()
        total_loss = 0
        batch_route_weights = []

        for X, y in train_loader:
            X = X.view(X.size(0), -1)
            optimizer.zero_grad()
            out, aux = model(X)
            loss = criterion(out, y) + 0.01 * aux
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

            with torch.no_grad():
                rw = model.router(X)
                batch_route_weights.append(rw.mean(dim=0).cpu().numpy())

        avg_rw = np.mean(batch_route_weights, axis=0)
        weight_snapshots.append(avg_rw.copy())

        model.eval()
        correct = total = 0
        with torch.no_grad():
            for X, y in test_loader:
                X = X.view(X.size(0), -1)
                out, _ = model(X)
                correct += (out.argmax(1) == y).sum().item()
                total += y.size(0)
        acc = correct / total

        if (epoch + 1) % 2 == 0 or epoch == 0:
            print(f"    Epoch {epoch+1:>2}/{epochs}: Loss={total_loss/len(train_loader):.4f}, "
                  f"Acc={acc*100:.1f}%, RouteW=[{', '.join(f'{w:.3f}' for w in avg_rw)}]")

    return acc, weight_snapshots


# ─────────────────────────────────────────
# Main experiment
# ─────────────────────────────────────────

def main():
    print()
    print("=" * 72)
    print("   EXPERIMENT: Why is {1/2, 1/3, 1/6} optimal?")
    print("   Systematic investigation of weight schemes")
    print("=" * 72)

    t0 = time.time()

    print("\n[Loading MNIST...]")
    train_loader, test_loader = load_mnist()

    MNIST_EPOCHS = 10
    SEEDS = [42, 123, 777]
    N_SEEDS = len(SEEDS)

    # ═══════════════════════════════════════
    # PHASE 1: Exhaustive weight comparison
    # ═══════════════════════════════════════
    print("\n" + "=" * 72)
    print(f"  PHASE 1: Exhaustive Weight Comparison (MNIST, {MNIST_EPOCHS} epochs, {N_SEEDS} seeds)")
    print("=" * 72)

    schemes = {
        'a. {1/2,1/3,1/6,~0} original':    [1/2, 1/3, 1/6, 1e-10],
        'b. {1/4,1/4,1/4,1/4} uniform':     [1/4, 1/4, 1/4, 1/4],
        'c. {1/2,1/4,1/8,1/8} geometric':   [1/2, 1/4, 1/8, 1/8],
        'd. {1/2,1/3,1/12,1/12} extend':    [1/2, 1/3, 1/12, 1/12],
        'e. {0.4,0.3,0.2,0.1} linear':      [0.4, 0.3, 0.2, 0.1],
        'f. {0.7,0.1,0.1,0.1} dominant':    [0.7, 0.1, 0.1, 0.1],
        'g. {1/3,1/3,1/6,1/6} symmetric':   [1/3, 1/3, 1/6, 1/6],
        'i. {1/2,1/4,1/7,1/28} perf28':     [1/2, 1/4, 1/7, 1/28],
    }

    # 3 random schemes
    for rs in range(3):
        rng = np.random.RandomState(rs * 100 + 1)
        rw = rng.dirichlet([1, 1, 1, 1])
        schemes[f'j. random_{rs}'] = rw.tolist()

    results = {}

    for name, weights in schemes.items():
        print(f"\n  [{name}]")
        h = shannon_entropy(weights)
        print(f"    Target: [{', '.join(f'{w:.4f}' for w in weights)}]  H={h:.4f} nats")

        accs = []
        eff_w = None
        for si, seed in enumerate(SEEDS):
            acc, ew = train_scheme(weights, train_loader, test_loader,
                                   epochs=MNIST_EPOCHS, seed=seed, verbose=(si == 0))
            accs.append(acc)
            if si == 0:
                eff_w = ew
            print(f"    seed {seed}: {acc*100:.2f}%")

        mean_acc = np.mean(accs)
        std_acc = np.std(accs)
        results[name] = {
            'weights': weights,
            'eff_weights': eff_w,
            'mean_acc': mean_acc,
            'std_acc': std_acc,
            'accs': accs,
            'entropy': h,
        }
        print(f"    => MEAN: {mean_acc*100:.2f}% +/- {std_acc*100:.2f}%")

    # h. Learned weights (routing='meta')
    print(f"\n  [h. learned (meta routing)]")
    meta_accs = []
    for si, seed in enumerate(SEEDS):
        set_seed(seed)
        model = MetaEngine(routing='meta')
        _, accs_list = train_and_evaluate(
            model, train_loader, test_loader, epochs=MNIST_EPOCHS,
            aux_lambda=0.01, verbose=(si == 0))
        meta_accs.append(accs_list[-1])
        print(f"    seed {seed}: {accs_list[-1]*100:.2f}%")

    results['h. learned (meta)'] = {
        'weights': 'learned',
        'eff_weights': 'N/A',
        'mean_acc': np.mean(meta_accs),
        'std_acc': np.std(meta_accs),
        'accs': meta_accs,
        'entropy': 'N/A',
    }
    print(f"    => MEAN: {np.mean(meta_accs)*100:.2f}% +/- {np.std(meta_accs)*100:.2f}%")

    # ── Phase 1 Summary ──
    print("\n" + "-" * 72)
    print("  PHASE 1 RESULTS -- Sorted by accuracy")
    print("-" * 72)
    print(f"  {'Scheme':<42} {'Acc':>8} {'Std':>6} {'H(nats)':>8}")
    print("  " + "-" * 66)

    sorted_results = sorted(results.items(), key=lambda x: -x[1]['mean_acc'])
    for name, r in sorted_results:
        h_str = f"{r['entropy']:.4f}" if isinstance(r['entropy'], float) else r['entropy']
        marker = ' <-- BEST' if name == sorted_results[0][0] else ''
        print(f"  {name:<42} {r['mean_acc']*100:>7.2f}% {r['std_acc']*100:>5.2f}% {h_str:>8}{marker}")

    best_name = sorted_results[0][0]
    original_name = 'a. {1/2,1/3,1/6,~0} original'
    orig_acc = results[original_name]['mean_acc']
    best_acc = results[best_name]['mean_acc']
    orig_rank = [n for n,_ in sorted_results].index(original_name) + 1
    print(f"\n  Original {{1/2,1/3,1/6}} rank: #{orig_rank} / {len(sorted_results)}")
    print(f"  Original accuracy: {orig_acc*100:.2f}%")
    print(f"  Best accuracy:     {best_acc*100:.2f}% ({best_name})")

    # ═══════════════════════════════════════
    # PHASE 2: Entropy analysis
    # ═══════════════════════════════════════
    print("\n" + "=" * 72)
    print("  PHASE 2: Entropy vs Accuracy Analysis")
    print("=" * 72)

    entropy_acc_pairs = []
    for name, r in results.items():
        if isinstance(r['entropy'], float):
            entropy_acc_pairs.append((name, r['entropy'], r['mean_acc']))

    entropy_acc_pairs.sort(key=lambda x: x[1])

    print(f"\n  {'Scheme':<42} {'H(nats)':>8} {'Acc':>8}")
    print("  " + "-" * 60)
    for name, h, acc in entropy_acc_pairs:
        print(f"  {name:<42} {h:>8.4f} {acc*100:>7.2f}%")

    hs = [x[1] for x in entropy_acc_pairs]
    accs_arr = [x[2] for x in entropy_acc_pairs]
    corr = np.corrcoef(hs, accs_arr)[0, 1] if len(hs) > 2 else 0.0

    h_original = shannon_entropy([1/2, 1/3, 1/6, 1e-10])
    h_uniform = shannon_entropy([1/4, 1/4, 1/4, 1/4])
    print(f"\n  Pearson correlation (H vs Acc): r = {corr:.4f}")
    print(f"  H(1/2,1/3,1/6,~0) = {h_original:.4f} nats")
    print(f"  H(1/4,1/4,1/4,1/4) = {h_uniform:.4f} nats (maximum)")
    print(f"  H_TARGET from model_utils = {H_TARGET:.4f} nats (3-engine)")

    # ASCII scatter plot
    print("\n  Entropy vs Accuracy (ASCII plot):")
    min_h = min(hs) - 0.05
    max_h = max(hs) + 0.05
    min_a = min(accs_arr) - 0.005
    max_a = max(accs_arr) + 0.005
    ROWS, COLS = 15, 50

    grid = [[' ' for _ in range(COLS)] for _ in range(ROWS)]
    for name, h, acc in entropy_acc_pairs:
        col = int((h - min_h) / (max_h - min_h) * (COLS - 1))
        row = ROWS - 1 - int((acc - min_a) / (max_a - min_a) * (ROWS - 1))
        col = max(0, min(COLS - 1, col))
        row = max(0, min(ROWS - 1, row))
        ch = '*' if 'original' in name else ('U' if 'uniform' in name else
              ('r' if 'random' in name else 'o'))
        grid[row][col] = ch

    print(f"  Acc% ^")
    for i, row_data in enumerate(grid):
        acc_label = f"{(max_a - i * (max_a - min_a) / (ROWS - 1)) * 100:.1f}"
        print(f"  {acc_label:>5}|{''.join(row_data)}|")
    print(f"       +{'-' * COLS}+")
    print(f"       {min_h:.2f}{' ' * (COLS - 8)}{max_h:.2f}")
    print(f"       {'Entropy (nats)':^{COLS}}")
    print(f"       * = original, U = uniform, o = named, r = random")

    # ═══════════════════════════════════════
    # PHASE 3: Weight drift analysis
    # ═══════════════════════════════════════
    print("\n" + "=" * 72)
    print("  PHASE 3: Weight Drift Analysis")
    print("  Q: Do learned (meta) routing weights converge toward {1/2,1/3,1/6}?")
    print("=" * 72)

    print("\n  Training MetaEngine(meta routing) with weight tracking...")
    meta_acc, weight_snapshots = train_meta_with_tracking(
        train_loader, test_loader, epochs=MNIST_EPOCHS, seed=42
    )

    print(f"\n  Route weight evolution (per epoch, averaged over batches):")
    print(f"  {'Epoch':>5}  {'A':>7} {'E':>7} {'G':>7} {'F':>7}  {'Dist to {1/2,1/3,1/6,0}':>24}")
    target = np.array([1/2, 1/3, 1/6, 0.0])

    for i, ws in enumerate(weight_snapshots):
        dist = np.linalg.norm(ws - target)
        print(f"  {i+1:>5}  {ws[0]:>7.4f} {ws[1]:>7.4f} {ws[2]:>7.4f} {ws[3]:>7.4f}  {dist:>24.6f}")

    if len(weight_snapshots) >= 2:
        dist_first = np.linalg.norm(weight_snapshots[0] - target)
        dist_last = np.linalg.norm(weight_snapshots[-1] - target)
        print(f"\n  Distance at epoch 1:  {dist_first:.6f}")
        print(f"  Distance at epoch {MNIST_EPOCHS}: {dist_last:.6f}")
        if dist_last < dist_first:
            print(f"  => CONVERGING toward {{1/2,1/3,1/6,0}}  (delta = {dist_first - dist_last:.6f})")
        else:
            print(f"  => DIVERGING from {{1/2,1/3,1/6,0}}  (delta = {dist_last - dist_first:.6f})")

    # Also check: what is the closest known scheme to learned weights?
    final_w = weight_snapshots[-1]
    print(f"\n  Final learned route weights: [{', '.join(f'{w:.4f}' for w in final_w)}]")
    print(f"  Final H = {shannon_entropy(final_w):.4f} nats")

    # Distances to each named scheme
    print(f"\n  Distance from final learned weights to each scheme:")
    for name, r in results.items():
        if isinstance(r['weights'], list):
            w = np.array(r['weights'])
            w = w / w.sum()
            d = np.linalg.norm(final_w - w)
            print(f"    {name:<42} dist = {d:.6f}")

    # ═══════════════════════════════════════
    # PHASE 4: Asymmetry vs exact values
    # ═══════════════════════════════════════
    print("\n" + "=" * 72)
    print("  PHASE 4: Is it the exact fractions or the asymmetry?")
    print("=" * 72)

    asymmetry_schemes = {
        'exact {1/2,1/3,1/6,0}':                [1/2, 1/3, 1/6, 1e-10],
        'approx {0.50,0.33,0.17,0}':            [0.50, 0.33, 0.17, 1e-10],
        'same-H diff vals {0.55,0.28,0.17,0}':  [0.55, 0.28, 0.17, 1e-10],
        'reverse {1/6,1/3,1/2,0}':               [1/6, 1/3, 1/2, 1e-10],
        'shuffled {1/3,1/6,1/2,0}':              [1/3, 1/6, 1/2, 1e-10],
        'mild asym {.35,.30,.20,.15}':           [0.35, 0.30, 0.20, 0.15],
        'strong asym {.80,.10,.05,.05}':         [0.8, 0.1, 0.05, 0.05],
    }

    asym_results = {}
    for name, weights in asymmetry_schemes.items():
        print(f"\n  [{name}]")
        h = shannon_entropy(weights)
        print(f"    Target: [{', '.join(f'{w:.4f}' for w in weights)}]  H={h:.4f}")

        accs = []
        for si, seed in enumerate(SEEDS):
            acc, _ = train_scheme(weights, train_loader, test_loader,
                                  epochs=MNIST_EPOCHS, seed=seed, verbose=(si == 0))
            accs.append(acc)
            print(f"    seed {seed}: {acc*100:.2f}%")

        mean_acc = np.mean(accs)
        std_acc = np.std(accs)
        asym_results[name] = {'mean_acc': mean_acc, 'std_acc': std_acc, 'entropy': h}
        print(f"    => MEAN: {mean_acc*100:.2f}% +/- {std_acc*100:.2f}%")

    print("\n  PHASE 4 RESULTS:")
    print(f"  {'Scheme':<42} {'Acc':>8} {'Std':>6} {'H':>8}")
    print("  " + "-" * 66)
    for name, r in sorted(asym_results.items(), key=lambda x: -x[1]['mean_acc']):
        print(f"  {name:<42} {r['mean_acc']*100:>7.2f}% {r['std_acc']*100:>5.2f}% {r['entropy']:>8.4f}")

    exact_acc = asym_results['exact {1/2,1/3,1/6,0}']['mean_acc']
    approx_acc = asym_results['approx {0.50,0.33,0.17,0}']['mean_acc']
    reverse_acc = asym_results['reverse {1/6,1/3,1/2,0}']['mean_acc']

    print(f"\n  KEY COMPARISONS:")
    print(f"  Exact vs Approximate: {abs(exact_acc - approx_acc)*100:.2f}% difference")
    if abs(exact_acc - approx_acc) < 0.003:
        print("  => SIMILAR: Asymmetry pattern matters, not exact fractions")
    else:
        print("  => DIFFERENT: Exact fractions matter")

    print(f"  Exact vs Reverse order: {abs(exact_acc - reverse_acc)*100:.2f}% difference")
    if abs(exact_acc - reverse_acc) < 0.003:
        print("  => Order doesn't matter -- just the value distribution")
    else:
        print("  => Order MATTERS -- which engine gets which weight is important")
        if exact_acc > reverse_acc:
            print("  => Engine A (sigma,tau-MoE) benefits from highest weight")
        else:
            print("  => Engine G (entropy) benefits from highest weight")

    # ═══════════════════════════════════════
    # PHASE 5: CIFAR validation
    # ═══════════════════════════════════════
    print("\n" + "=" * 72)
    print("  PHASE 5: CIFAR-10 Validation (top 5 MNIST schemes)")
    print("=" * 72)

    all_named = [(n, r) for n, r in results.items() if isinstance(r['weights'], list)]
    all_named.sort(key=lambda x: -x[1]['mean_acc'])
    top5 = all_named[:5]

    must_include = [original_name, 'b. {1/4,1/4,1/4,1/4} uniform']
    top5_names = [n for n, _ in top5]
    for mi in must_include:
        if mi not in top5_names:
            top5.append((mi, results[mi]))

    print("\n[Loading CIFAR-10...]")
    cifar_train, cifar_test = load_cifar10()
    CIFAR_EPOCHS = 15
    cifar_input_dim = 3072

    cifar_results = {}
    for name, r in top5:
        weights = r['weights']
        print(f"\n  [{name}] on CIFAR-10")

        accs = []
        for si, seed in enumerate(SEEDS):
            acc, _ = train_scheme(weights, cifar_train, cifar_test,
                                  epochs=CIFAR_EPOCHS, seed=seed,
                                  input_dim=cifar_input_dim, verbose=(si == 0))
            accs.append(acc)
            print(f"    seed {seed}: {acc*100:.2f}%")

        mean_acc = np.mean(accs)
        std_acc = np.std(accs)
        cifar_results[name] = {'mean_acc': mean_acc, 'std_acc': std_acc}
        print(f"    => CIFAR: {mean_acc*100:.2f}% +/- {std_acc*100:.2f}%")

    print("\n  CIFAR-10 RESULTS:")
    print(f"  {'Scheme':<42} {'CIFAR Acc':>10} {'MNIST Acc':>10}")
    print("  " + "-" * 64)
    for name, r in sorted(cifar_results.items(), key=lambda x: -x[1]['mean_acc']):
        mnist_acc = results[name]['mean_acc'] if name in results else 0
        print(f"  {name:<42} {r['mean_acc']*100:>9.2f}% {mnist_acc*100:>9.2f}%")

    # Check if original wins on CIFAR too
    if original_name in cifar_results:
        orig_cifar = cifar_results[original_name]['mean_acc']
        cifar_sorted = sorted(cifar_results.items(), key=lambda x: -x[1]['mean_acc'])
        cifar_rank = [n for n,_ in cifar_sorted].index(original_name) + 1
        print(f"\n  Original rank on CIFAR: #{cifar_rank} / {len(cifar_sorted)}")

    # ═══════════════════════════════════════
    # FINAL ANALYSIS
    # ═══════════════════════════════════════
    print("\n" + "=" * 72)
    print("  FINAL ANALYSIS")
    print("=" * 72)

    print(f"""
  KEY FINDINGS:

  1. WEIGHT COMPARISON (Phase 1):
     - Best MNIST scheme: {sorted_results[0][0]}
       ({sorted_results[0][1]['mean_acc']*100:.2f}%)
     - Original {{1/2,1/3,1/6,~0}}: {orig_acc*100:.2f}%
       (rank #{orig_rank}/{len(sorted_results)})
     - Learned (meta routing): {results['h. learned (meta)']['mean_acc']*100:.2f}%

  2. ENTROPY ANALYSIS (Phase 2):
     - H(1/2,1/3,1/6,~0) = {h_original:.4f} nats
     - H(uniform) = {h_uniform:.4f} nats (maximum)
     - Pearson r(H, Acc) = {corr:.4f}

  3. WEIGHT DRIFT (Phase 3):
     - Learned route weights after {MNIST_EPOCHS} epochs:
       [{', '.join(f'{w:.4f}' for w in final_w)}]
     - Dist to target: {np.linalg.norm(final_w - target):.4f}

  4. ASYMMETRY (Phase 4):
     - Exact vs Approx: {abs(exact_acc - approx_acc)*100:.2f}% diff
     - Exact vs Reverse: {abs(exact_acc - reverse_acc)*100:.2f}% diff

  5. MATHEMATICAL PROPERTIES of {{1/2, 1/3, 1/6}}:
     - Divisor reciprocals of perfect number 6
     - Sum = 1 (probability distribution)
     - sigma_{{-1}}(6) = 1/1 + 1/2 + 1/3 + 1/6 = 2 (only perfect numbers)
     - H = {shannon_entropy([1/2, 1/3, 1/6]):.4f} nats (3-engine)
     - Asymmetric: one engine dominant (1/2), one moderate (1/3),
       one minor (1/6) -- like brain hemisphere specialization
     - UNIQUE Egyptian fraction: 1/2 + 1/3 + 1/6 = 1 is the only way
       to write 1 as sum of 3 distinct unit fractions with d|6
""")

    elapsed = time.time() - t0
    print(f"  Total experiment time: {elapsed:.0f}s ({elapsed/60:.1f}min)")
    print("=" * 72)


if __name__ == '__main__':
    main()
