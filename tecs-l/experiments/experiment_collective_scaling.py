#!/usr/bin/env python3
"""Hypothesis 267: Does the collective phase transition scale with N?

Experiment: Train N DenseModel agents (N = 3, 5, 7, 9, 11) on MNIST with
different seeds, measure:
  - Majority vote accuracy
  - Unanimous accuracy (all N agree AND correct)
  - Unanimous coverage (fraction where all N agree)
  - Accuracy at each agreement level (k/N for k=ceil(N/2)..N)
  - Sweet spot: argmax(accuracy * coverage)

DenseModel only (~153K params, fastest). 8 epochs each.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import torch
import numpy as np
import time
import math
from collections import Counter

from model_utils import DenseModel, load_mnist, train_and_evaluate, count_params


# ─────────────────────────────────────────
# Config
# ─────────────────────────────────────────
INPUT_DIM = 784
HIDDEN_DIM = 192
OUTPUT_DIM = 10
EPOCHS = 8
LR = 0.001
N_VALUES = [3, 5, 7, 9, 11]


# ─────────────────────────────────────────
# Train one agent
# ─────────────────────────────────────────
def train_agent(seed, train_loader, test_loader):
    """Train one DenseModel with a given seed. Returns (model, final_acc)."""
    torch.manual_seed(seed)
    np.random.seed(seed)
    model = DenseModel(INPUT_DIM, HIDDEN_DIM, OUTPUT_DIM)
    _, accs = train_and_evaluate(model, train_loader, test_loader,
                                 epochs=EPOCHS, lr=LR, verbose=False)
    return model, accs[-1]


# ─────────────────────────────────────────
# Collect predictions
# ─────────────────────────────────────────
def collect_predictions(models, test_loader):
    """Return (preds, labels) where preds is (N, n_samples)."""
    all_preds = []
    labels_out = None
    for model in models:
        model.eval()
        preds_list = []
        labels_list = []
        with torch.no_grad():
            for X, y in test_loader:
                X = X.view(X.size(0), -1)
                out = model(X)
                preds_list.append(out.argmax(1).cpu().numpy())
                labels_list.append(y.cpu().numpy())
        all_preds.append(np.concatenate(preds_list))
        if labels_out is None:
            labels_out = np.concatenate(labels_list)
    return np.stack(all_preds, axis=0), labels_out


# ─────────────────────────────────────────
# Analyze agreement levels
# ─────────────────────────────────────────
def analyze_agreement(preds, labels):
    """Analyze accuracy at each agreement level k.

    Args:
        preds: (N, n_samples) predicted classes
        labels: (n_samples,) true labels

    Returns dict with majority, unanimous, and per-level results.
    """
    N = preds.shape[0]
    n_samples = preds.shape[1]

    # Per-sample: most common prediction and its count
    vote_preds = np.zeros(n_samples, dtype=int)
    vote_counts = np.zeros(n_samples, dtype=int)
    for j in range(n_samples):
        counter = Counter(preds[:, j])
        pred, cnt = counter.most_common(1)[0]
        vote_preds[j] = pred
        vote_counts[j] = cnt

    # Per-agent accuracy
    agent_accs = [(preds[i] == labels).mean() for i in range(N)]

    # Per agreement level k (from ceil(N/2) to N)
    majority_k = math.ceil(N / 2)
    levels = {}
    for k in range(majority_k, N + 1):
        mask = vote_counts >= k
        n_covered = mask.sum()
        n_correct = (vote_preds[mask] == labels[mask]).sum() if n_covered > 0 else 0
        acc = float(n_correct / n_covered) if n_covered > 0 else 0.0
        cov = float(n_covered / n_samples)
        levels[k] = {
            'accuracy': acc,
            'coverage': cov,
            'score': acc * cov,
        }

    return {
        'agent_accs': agent_accs,
        'mean_agent_acc': float(np.mean(agent_accs)),
        'majority': levels[majority_k],
        'unanimous': levels[N],
        'levels': levels,
    }


# ─────────────────────────────────────────
# ASCII helpers
# ─────────────────────────────────────────
def ascii_bar(value, max_val=1.0, width=40):
    filled = int(round(value / max_val * width)) if max_val > 0 else 0
    filled = max(0, min(width, filled))
    return '#' * filled + '.' * (width - filled)


def ascii_hchart(title, labels, values, width=40, fmt=".2f", unit="%"):
    """Horizontal bar chart."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")
    max_val = max(values) if values else 1
    for lbl, val in zip(labels, values):
        bar = ascii_bar(val, max_val, width)
        print(f"  N={lbl:>2} |{bar}| {val:{fmt}}{unit}")
    print()


def ascii_plot(xs, ys, title, xlabel, ylabel, width=55, height=13):
    """Simple ASCII line plot."""
    print(f"\n  {title}")
    print(f"  {'=' * (width + 12)}")

    if not ys or len(ys) < 2:
        print("  (not enough data)")
        return

    y_min = min(ys) - (max(ys) - min(ys)) * 0.05
    y_max = max(ys) + (max(ys) - min(ys)) * 0.05
    if y_max == y_min:
        y_max = y_min + 0.01
    x_min, x_max = min(xs), max(xs)
    if x_max == x_min:
        x_max = x_min + 1

    grid = [[' '] * width for _ in range(height)]

    # Plot points and connect
    pts = sorted(zip(xs, ys))
    for x, y in pts:
        c = int((x - x_min) / (x_max - x_min) * (width - 1))
        r = height - 1 - int((y - y_min) / (y_max - y_min) * (height - 1))
        c, r = max(0, min(width-1, c)), max(0, min(height-1, r))
        grid[r][c] = '*'

    for i in range(len(pts) - 1):
        x1, y1 = pts[i]
        x2, y2 = pts[i+1]
        c1 = int((x1 - x_min) / (x_max - x_min) * (width - 1))
        c2 = int((x2 - x_min) / (x_max - x_min) * (width - 1))
        r1 = height - 1 - int((y1 - y_min) / (y_max - y_min) * (height - 1))
        r2 = height - 1 - int((y2 - y_min) / (y_max - y_min) * (height - 1))
        steps = max(abs(c2 - c1), abs(r2 - r1), 1)
        for s in range(1, steps):
            c = int(c1 + (c2 - c1) * s / steps)
            r = int(r1 + (r2 - r1) * s / steps)
            c, r = max(0, min(width-1, c)), max(0, min(height-1, r))
            if grid[r][c] == ' ':
                grid[r][c] = '-'

    for i, row in enumerate(grid):
        y_val = y_max - (y_max - y_min) * i / (height - 1)
        print(f"  {y_val:>8.4f} |{''.join(row)}|")
    print(f"  {'':>8} +{'-' * width}+")
    print(f"  {'':>8}  {x_min:<{width//2}}{x_max:>{width - width//2}}")
    print(f"  {'':>8}  {xlabel:^{width}}")


# ─────────────────────────────────────────
# Main
# ─────────────────────────────────────────
def main():
    print("=" * 70)
    print("  HYPOTHESIS 267: Collective Phase Transition Scaling with N")
    print("  DenseModel agents on MNIST, 8 epochs each")
    print("=" * 70)

    t_start = time.time()

    print("\n  Loading MNIST...")
    train_loader, test_loader = load_mnist(batch_size=128)

    sample = DenseModel(INPUT_DIM, HIDDEN_DIM, OUTPUT_DIM)
    print(f"  DenseModel: {count_params(sample):,} params")
    del sample

    all_results = {}

    # We reuse agents: N=11 is the superset; smaller N uses first N agents
    max_n = max(N_VALUES)
    print(f"\n  Training {max_n} agents (reused for all N)...")

    models = []
    for i in range(max_n):
        seed = 42 + i * 7
        t1 = time.time()
        model, acc = train_agent(seed, train_loader, test_loader)
        models.append(model)
        dt = time.time() - t1
        print(f"    Agent {i+1:>2}/{max_n}: seed={seed:>4}, acc={acc*100:.2f}%, time={dt:.1f}s")

    # Collect all predictions once
    print(f"\n  Collecting predictions...")
    all_preds, labels = collect_predictions(models, test_loader)
    print(f"  Done. {all_preds.shape[1]} test samples.")

    # Analyze for each N
    for N in N_VALUES:
        preds_n = all_preds[:N]
        result = analyze_agreement(preds_n, labels)
        all_results[N] = result
        print(f"\n  N={N:>2}: majority={result['majority']['accuracy']*100:.2f}% "
              f"| unanimous acc={result['unanimous']['accuracy']*100:.2f}% "
              f"cov={result['unanimous']['coverage']*100:.2f}%")

    # ─────────────────────────────────────────
    # Summary table
    # ─────────────────────────────────────────
    print(f"\n\n{'=' * 80}")
    print(f"  SUMMARY TABLE")
    print(f"{'=' * 80}")
    header = (f"  | {'N':>3} | {'Indiv':>8} | {'Majority':>9} | "
              f"{'Unan.Acc':>9} | {'Unan.Cov':>9} | {'Acc*Cov':>9} |")
    print(header)
    sep = f"  |{'─'*5}|{'─'*10}|{'─'*11}|{'─'*11}|{'─'*11}|{'─'*11}|"
    print(sep)

    unan_accs, unan_covs, unan_scores, maj_accs, indiv_means = [], [], [], [], []
    for N in N_VALUES:
        r = all_results[N]
        im = r['mean_agent_acc'] * 100
        ma = r['majority']['accuracy'] * 100
        ua = r['unanimous']['accuracy'] * 100
        uc = r['unanimous']['coverage'] * 100
        sc = r['unanimous']['score'] * 100
        indiv_means.append(im); maj_accs.append(ma)
        unan_accs.append(ua); unan_covs.append(uc); unan_scores.append(sc)
        print(f"  | {N:>3} | {im:>7.2f}% | {ma:>8.2f}% | "
              f"{ua:>8.2f}% | {uc:>8.2f}% | {sc:>8.2f}% |")

    # ─────────────────────────────────────────
    # Agreement level tables
    # ─────────────────────────────────────────
    print(f"\n\n{'=' * 80}")
    print(f"  AGREEMENT LEVEL CURVES")
    print(f"{'=' * 80}")
    for N in N_VALUES:
        r = all_results[N]
        levels = r['levels']
        mk = math.ceil(N / 2)
        print(f"\n  N = {N}  (majority threshold k >= {mk})")
        print(f"  | {'k':>3} | {'k/N':>5} | {'Accuracy':>9} | {'Coverage':>9} | {'Score':>9} | {'Bar':>30} |")
        print(f"  |{'─'*5}|{'─'*7}|{'─'*11}|{'─'*11}|{'─'*11}|{'─'*32}|")
        for k in sorted(levels.keys()):
            lv = levels[k]
            bar = ascii_bar(lv['accuracy'], 1.0, 30)
            tag = " <-- unan" if k == N else ""
            print(f"  | {k:>3} | {k/N:>5.2f} | {lv['accuracy']*100:>8.2f}% | "
                  f"{lv['coverage']*100:>8.2f}% | {lv['score']*100:>8.2f}% | {bar} |{tag}")

    # ─────────────────────────────────────────
    # Sweet spot analysis
    # ─────────────────────────────────────────
    print(f"\n\n{'=' * 80}")
    print(f"  SWEET SPOT ANALYSIS: argmax(accuracy * coverage)")
    print(f"{'=' * 80}")
    print(f"  | {'N':>3} | {'Best k':>7} | {'Accuracy':>9} | {'Coverage':>9} | {'Score':>9} |")
    print(f"  |{'─'*5}|{'─'*9}|{'─'*11}|{'─'*11}|{'─'*11}|")

    global_best = None
    for N in N_VALUES:
        levels = all_results[N]['levels']
        best_k = max(levels, key=lambda k: levels[k]['score'])
        lv = levels[best_k]
        print(f"  | {N:>3} | {best_k:>3}/{N:<3} | {lv['accuracy']*100:>8.2f}% | "
              f"{lv['coverage']*100:>8.2f}% | {lv['score']*100:>8.2f}% |")
        if global_best is None or lv['score'] > global_best[1]:
            global_best = (N, lv['score'], best_k, lv['accuracy'], lv['coverage'])

    if global_best:
        gN, gs, gk, ga, gc = global_best
        print(f"\n  >>> Global sweet spot: N={gN}, k={gk}/{gN}, "
              f"acc={ga*100:.2f}%, cov={gc*100:.2f}%, score={gs*100:.2f}%")

    # ─────────────────────────────────────────
    # ASCII graphs
    # ─────────────────────────────────────────
    n_labels = [str(n) for n in N_VALUES]

    ascii_hchart("Unanimous Accuracy vs N", n_labels, unan_accs)
    ascii_hchart("Unanimous Coverage vs N", n_labels, unan_covs)
    ascii_hchart("Unanimous Score (Acc*Cov) vs N", n_labels, unan_scores)
    ascii_hchart("Majority Vote Accuracy vs N", n_labels, maj_accs)

    ns_f = [float(n) for n in N_VALUES]
    ascii_plot(ns_f, unan_accs, "Unanimous Accuracy vs N", "N (agents)", "Accuracy (%)")
    ascii_plot(ns_f, unan_covs, "Unanimous Coverage vs N", "N (agents)", "Coverage (%)")
    ascii_plot(ns_f, unan_scores, "Score (Acc*Cov) vs N", "N (agents)", "Score (%)")

    # ─────────────────────────────────────────
    # Phase transition analysis
    # ─────────────────────────────────────────
    print(f"\n\n{'=' * 80}")
    print(f"  PHASE TRANSITION ANALYSIS")
    print(f"{'=' * 80}")

    mono_acc = all(unan_accs[i] <= unan_accs[i+1] for i in range(len(unan_accs)-1))
    mono_cov = all(unan_covs[i] >= unan_covs[i+1] for i in range(len(unan_covs)-1))
    print(f"  Unanimous accuracy monotonically increasing?  {'YES' if mono_acc else 'NO'}")
    print(f"  Unanimous coverage monotonically decreasing?  {'YES' if mono_cov else 'NO'}")

    print(f"\n  Marginal changes (per +2 agents):")
    print(f"  | {'N->N+2':>8} | {'dAcc':>8} | {'dCov':>8} | {'dScore':>8} |")
    print(f"  |{'─'*10}|{'─'*10}|{'─'*10}|{'─'*10}|")
    for i in range(len(N_VALUES) - 1):
        n1, n2 = N_VALUES[i], N_VALUES[i+1]
        da = unan_accs[i+1] - unan_accs[i]
        dc = unan_covs[i+1] - unan_covs[i]
        ds = unan_scores[i+1] - unan_scores[i]
        print(f"  | {n1:>2}->{n2:<3} | {da:>+7.2f}% | {dc:>+7.2f}% | {ds:>+7.2f}% |")

    # Phase transition: at what agreement ratio does accuracy cross 99%?
    print(f"\n  99% accuracy threshold:")
    for N in N_VALUES:
        levels = all_results[N]['levels']
        threshold_k = None
        for k in sorted(levels.keys()):
            if levels[k]['accuracy'] >= 0.99:
                threshold_k = k
                break
        if threshold_k:
            print(f"    N={N:>2}: >= 99% at k={threshold_k}/{N} ({threshold_k/N:.2f}), "
                  f"coverage={levels[threshold_k]['coverage']*100:.1f}%")
        else:
            print(f"    N={N:>2}: never reaches 99%")

    # ─────────────────────────────────────────
    # Conclusions
    # ─────────────────────────────────────────
    elapsed = time.time() - t_start
    print(f"\n\n{'=' * 80}")
    print(f"  CONCLUSIONS")
    print(f"{'=' * 80}")

    acc_dir = "INCREASES" if unan_accs[-1] > unan_accs[0] else "DECREASES"
    cov_dir = "DECREASES" if unan_covs[-1] < unan_covs[0] else "INCREASES"
    best_score_n = N_VALUES[np.argmax(unan_scores)]

    print(f"\n  1. Unanimous accuracy {acc_dir} with N")
    print(f"     N=3: {unan_accs[0]:.2f}% -> N=11: {unan_accs[-1]:.2f}%")
    print(f"\n  2. Unanimous coverage {cov_dir} with N")
    print(f"     N=3: {unan_covs[0]:.2f}% -> N=11: {unan_covs[-1]:.2f}%")
    print(f"\n  3. Sweet spot (max Acc*Cov): N={best_score_n}")
    print(f"     Score = {max(unan_scores):.2f}%")
    print(f"\n  4. Phase transition: more agents -> higher confidence but narrower coverage")
    print(f"     This is the accuracy-coverage tradeoff of collective intelligence.")

    print(f"\n  Total agents trained: {max_n}")
    print(f"  Total time: {elapsed:.1f}s")
    print(f"\n{'=' * 80}")


if __name__ == '__main__':
    main()
