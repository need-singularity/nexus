```python
#!/usr/bin/env python3
"""Hypothesis 265: Does tension_scale converge to 1/3?

Experimental design:
  1. RepulsionFieldEngine (MNIST) — 5 initial tension_scale values
  2. FiberBundleEngine (MNIST) — 5 initial curvature_scale values
  3. RepulsionFieldEngine (CIFAR) — 5 initial tension_scale values
  4. Analysis: init vs final, attractor strength, ASCII visualization

Key questions:
  - Is 1/3 a true attractor, or is it initial value bias?
  - Does it converge to the same value across different datasets?
"""

import sys
import os
import torch
import torch.nn as nn
import numpy as np
import math
import time
import copy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from model_utils import (
    load_mnist, load_cifar10, train_and_evaluate, count_params,
)
from model_meta_engine import RepulsionFieldEngine
from model_fiber_bundle import FiberBundleEngine


# ─────────────────────────────────────────
# Helper: create model with custom initial scale
# ─────────────────────────────────────────

def make_repulsion_engine(init_tension, input_dim=784, hidden_dim=48, output_dim=10):
    """RepulsionFieldEngine with custom initial tension_scale."""
    model = RepulsionFieldEngine(input_dim, hidden_dim, output_dim)
    with torch.no_grad():
        model.tension_scale.fill_(init_tension)
    return model


def make_fiber_engine(init_curvature, input_dim=784, hidden_dim=48, output_dim=10,
                      fiber_dim=32):
    """FiberBundleEngine with custom initial curvature_scale."""
    model = FiberBundleEngine(input_dim, hidden_dim, output_dim, fiber_dim)
    with torch.no_grad():
        model.curvature_scale.fill_(init_curvature)
    return model


def make_repulsion_engine_cifar(init_tension, input_dim=3072, hidden_dim=96, output_dim=10):
    """RepulsionFieldEngine for CIFAR-10 (3x32x32 = 3072)."""
    model = RepulsionFieldEngine(input_dim, hidden_dim, output_dim)
    with torch.no_grad():
        model.tension_scale.fill_(init_tension)
    return model


# ─────────────────────────────────────────
# Training wrapper that tracks parameter history
# ─────────────────────────────────────────

def train_with_tracking(model, train_loader, test_loader, param_name,
                        epochs=10, lr=0.001, flatten=True):
    """Train model and track a named parameter each epoch.

    Returns dict with training results and parameter trajectory.
    """
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()

    # Get reference to tracked parameter
    param_ref = dict(model.named_parameters())[param_name]
    init_value = param_ref.item()

    trajectory = [init_value]
    train_losses = []
    test_accs = []

    for epoch in range(epochs):
        model.train()
        total_loss = 0
        for X, y in train_loader:
            if flatten:
                X = X.view(X.size(0), -1)
            optimizer.zero_grad()
            out = model(X)

            if isinstance(out, tuple):
                logits, aux = out
                loss = criterion(logits, y) + 0.1 * aux
            else:
                logits = out
                loss = criterion(logits, y)

            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        avg_loss = total_loss / len(train_loader)
        train_losses.append(avg_loss)

        # Evaluate
        model.eval()
        correct = total = 0
        with torch.no_grad():
            for X, y in test_loader:
                if flatten:
                    X = X.view(X.size(0), -1)
                out = model(X)
                if isinstance(out, tuple):
                    out = out[0]
                correct += (out.argmax(1) == y).sum().item()
                total += y.size(0)
        acc = correct / total
        test_accs.append(acc)

        # Track parameter
        current_val = param_ref.item()
        trajectory.append(current_val)

    final_value = param_ref.item()
    return {
        'init': init_value,
        'final': final_value,
        'trajectory': trajectory,
        'delta': final_value - init_value,
        'acc': test_accs[-1],
        'loss': train_losses[-1],
        'train_losses': train_losses,
        'test_accs': test_accs,
    }


# ─────────────────────────────────────────
# ASCII plotting
# ─────────────────────────────────────────

def ascii_scatter(title, data, xlabel="Init", ylabel="Final", width=60, height=20):
    """ASCII scatter plot of (init, final) pairs.

    data: list of (init_val, final_val, label)
    """
    inits = [d[0] for d in data]
    finals = [d[1] for d in data]

    x_min = min(inits) * 0.9 if min(inits) > 0 else min(inits) * 1.1
    x_max = max(inits) * 1.1
    y_min = min(finals) * 0.9 if min(finals) > 0 else min(finals) * 1.1
    y_max = max(finals) * 1.1

    if x_max == x_min:
        x_max = x_min + 1
    if y_max == y_min:
        y_max = y_min + 1

    grid = [[' ' for _ in range(width)] for _ in range(height)]

    # Plot y=x diagonal (init bias line)
    for i in range(min(width, height * 3)):
        x_val = x_min + (x_max - x_min) * i / width
        y_val = x_val
        if y_min <= y_val <= y_max:
            row = height - 1 - int((y_val - y_min) / (y_max - y_min) * (height - 1))
            col = int(i / width * (width - 1))
            row = max(0, min(height - 1, row))
            col = max(0, min(width - 1, col))
            if grid[row][col] == ' ':
                grid[row][col] = '.'

    # Plot data points
    markers = 'ABCDE'
    for idx, (x, y, label) in enumerate(data):
        col = int((x - x_min) / (x_max - x_min) * (width - 1))
        row = height - 1 - int((y - y_min) / (y_max - y_min) * (height - 1))
        col = max(0, min(width - 1, col))
        row = max(0, min(height - 1, row))
        grid[row][col] = markers[idx % len(markers)]

    lines = []
    lines.append(f"\n  {title}")
    lines.append(f"  {'=' * (width + 8)}")
    for r in range(height):
        y_val = y_max - (y_max - y_min) * r / (height - 1)
        if r == 0 or r == height - 1 or r == height // 2:
            lines.append(f"  {y_val:6.3f} |{''.join(grid[r])}|")
        else:
            lines.append(f"         |{''.join(grid[r])}|")
    lines.append(f"         +{'-' * width}+")
    lines.append(f"  {xlabel:>8} {x_min:<10.3f}{' ' * (width - 22)}{x_max:>10.3f}")

    # Legend
    lines.append(f"\n  Legend: (. = y=x diagonal / init bias line)")
    for idx, (x, y, label) in enumerate(data):
        lines.append(f"    {markers[idx]} = {label} (init={x:.4f} -> final={y:.4f})")

    return '\n'.join(lines)


def ascii_trajectory(title, trajectories, width=70, height=15):
    """ASCII line chart for parameter trajectories over epochs.

    trajectories: list of (label, [values])
    """
    all_vals = [v for _, vals in trajectories for v in vals]
    y_min = min(all_vals) * 0.95 if min(all_vals) > 0 else min(all_vals) * 1.05
    y_max = max(all_vals) * 1.05
    if y_max == y_min:
        y_max = y_min + 0.1

    max_len = max(len(vals) for _, vals in trajectories)
    grid = [[' ' for _ in range(width)] for _ in range(height)]

    markers = '*+oxs'
    for t_idx, (label, vals) in enumerate(trajectories):
        for i, v in enumerate(vals):
            col = int(i / (max_len - 1) * (width - 1)) if max_len > 1 else 0
            row = height - 1 - int((v - y_min) / (y_max - y_min) * (height - 1))
            row = max(0, min(height - 1, row))
            col = max(0, min(width - 1, col))
            grid[row][col] = markers[t_idx % len(markers)]

    # Add 1/3 reference line
    ref_row = height - 1 - int((1/3 - y_min) / (y_max - y_min) * (height - 1))
    if 0 <= ref_row < height:
        for c in range(width):
            if grid[ref_row][c] == ' ':
                grid[ref_row][c] = '-'

    lines = []
    lines.append(f"\n  {title}")
    lines.append(f"  {'=' * (width + 8)}")
    for r in range(height):
        y_val = y_max - (y_max - y_min) * r / (height - 1)
        if r == 0 or r == height - 1 or r == height // 2:
            lines.append(f"  {y_val:6.3f} |{''.join(grid[r])}|")
        else:
            lines.append(f"         |{''.join(grid[r])}|")
    lines.append(f"         +{'-' * width}+")
    lines.append(f"  Epoch    0{' ' * (width - 5)}{max_len - 1}")

    lines.append(f"\n  Legend: (--- = 1/3 reference)")
    for idx, (label, vals) in enumerate(trajectories):
        lines.append(f"    {markers[idx]} = {label} (init={vals[0]:.4f} -> final={vals[-1]:.4f})")

    return '\n'.join(lines)


# ─────────────────────────────────────────
# Analysis
# ─────────────────────────────────────────

def analyze_convergence(results, model_name, expected_attractor=None):
    """Analyze whether results converge to a common attractor."""
    finals = [r['final'] for r in results]
    inits = [r['init'] for r in results]
    mean_final = np.mean(finals)
    std_final = np.std(finals)

    # Correlation between init and final
    if len(set(inits)) > 1:
        corr = np.corrcoef(inits, finals)[0, 1]
    else:
        corr = 0.0

    # Attractor strength: avg |final - init| / |range of inits|
    deltas = [abs(r['final'] - r['init']) for r in results]
    init_range = max(inits) - min(inits)
    avg_movement = np.mean(deltas)

    lines = []
    lines.append(f"\n## {model_name} Analysis")
    lines.append(f"")
    lines.append(f"| Init | Final | Delta | Acc |")
    lines.append(f"|-----:|------:|------:|----:|")
    for r in results:
        lines.append(f"| {r['init']:.4f} | {r['final']:.4f} | {r['delta']:+.4f} | {r['acc']*100:.1f}% |")

    lines.append(f"")
    lines.append(f"  Mean final:       {mean_final:.6f}")
    lines.append(f"  Std final:        {std_final:.6f}")
    lines.append(f"  Init-Final corr:  {corr:.4f}")
    lines.append(f"  Avg movement:     {avg_movement:.6f}")
    lines.append(f"  Init range:       {init_range:.4f}")

    if expected_attractor is not None:
        lines.append(f"  Expected:         {expected_attractor:.6f}")
        lines.append(f"  Mean - Expected:  {mean_final - expected_attractor:+.6f}")

    # Verdict
    lines.append(f"")
    if corr > 0.8:
        lines.append(f"  VERDICT: INITIAL VALUE BIAS (corr={corr:.2f} >> 0)")
        lines.append(f"    Final ~ Init. The parameter stays near where it started.")
        verdict = "BIAS"
    elif std_final < 0.05 * abs(mean_final) and avg_movement > 0.01:
        lines.append(f"  VERDICT: TRUE ATTRACTOR at ~{mean_final:.4f} (std={std_final:.6f})")
        lines.append(f"    All inits converge to the same value regardless of start.")
        verdict = "ATTRACTOR"
    elif std_final < 0.1 * abs(mean_final):
        lines.append(f"  VERDICT: WEAK ATTRACTOR at ~{mean_final:.4f} (std={std_final:.6f})")
        lines.append(f"    Partial convergence. Some init-dependence remains.")
        verdict = "WEAK_ATTRACTOR"
    else:
        lines.append(f"  VERDICT: NO CLEAR ATTRACTOR (std={std_final:.6f}, corr={corr:.2f})")
        lines.append(f"    Finals are scattered. Neither bias nor attractor.")
        verdict = "NONE"

    return '\n'.join(lines), verdict, mean_final


# ─────────────────────────────────────────
# Main experiment
# ─────────────────────────────────────────

def run_experiment():
    print("=" * 78)
    print("  EXPERIMENT: Is 1/3 a true attractor for tension_scale?")
    print("  Hypothesis 265")
    print("=" * 78)

    EPOCHS = 10
    SEED = 42

    # ─────────────────────────────────────
    # Load data
    # ─────────────────────────────────────
    print("\n[1/4] Loading datasets...")
    t0 = time.time()
    train_mnist, test_mnist = load_mnist(batch_size=128)
    print(f"  MNIST loaded in {time.time()-t0:.1f}s")

    t0 = time.time()
    train_cifar, test_cifar = load_cifar10(batch_size=128)
    print(f"  CIFAR-10 loaded in {time.time()-t0:.1f}s")

    # ─────────────────────────────────────
    # Experiment 1: RepulsionFieldEngine on MNIST
    # ─────────────────────────────────────
    print("\n" + "=" * 78)
    print("  [2/4] RepulsionFieldEngine on MNIST — tension_scale")
    print("=" * 78)

    repulsion_inits = [0.01, 0.1, 1/3, 0.7, 2.0]
    repulsion_mnist_results = []

    for init_val in repulsion_inits:
        torch.manual_seed(SEED)
        np.random.seed(SEED)
        print(f"\n  --- init tension_scale = {init_val:.4f} ---")
        model = make_repulsion_engine(init_val)
        result = train_with_tracking(
            model, train_mnist, test_mnist,
            param_name='tension_scale',
            epochs=EPOCHS, lr=0.001, flatten=True,
        )
        repulsion_mnist_results.append(result)
        print(f"  Final: {result['final']:.6f}  (delta={result['delta']:+.6f})  Acc={result['acc']*100:.1f}%")

    # ─────────────────────────────────────
    # Experiment 2: FiberBundleEngine on MNIST
    # ─────────────────────────────────────
    print("\n" + "=" * 78)
    print("  [3/4] FiberBundleEngine on MNIST — curvature_scale")
    print("=" * 78)

    fiber_inits = [0.01, 0.1, 1/3, 1.0, 3.0]
    fiber_results = []

    for init_val in fiber_inits:
        torch.manual_seed(SEED)
        np.random.seed(SEED)
        print(f"\n  --- init curvature_scale = {init_val:.4f} ---")
        model = make_fiber_engine(init_val)
        result = train_with_tracking(
            model, train_mnist, test_mnist,
            param_name='curvature_scale',
            epochs=EPOCHS, lr=0.001, flatten=True,
        )
        fiber_results.append(result)
        print(f"  Final: {result['final']:.6f}  (delta={result['delta']:+.6f})  Acc={result['acc']*100:.1f}%")

    # ─────────────────────────────────────
    # Experiment 3: RepulsionFieldEngine on CIFAR
    # ─────────────────────────────────────
    print("\n" + "=" * 78)
    print("  [4/4] RepulsionFieldEngine on CIFAR-10 — tension_scale")
    print("=" * 78)

    repulsion_cifar_results = []

    for init_val in repulsion_inits:
        torch.manual_seed(SEED)
        np.random.seed(SEED)
        print(f"\n  --- init tension_scale = {init_val:.4f} ---")
        model = make_repulsion_engine_cifar(init_val)
        result = train_with_tracking(
            model, train_cifar, test_cifar,
            param_name='tension_scale',
            epochs=EPOCHS, lr=0.001, flatten=True,
        )
        repulsion_cifar_results.append(result)
        print(f"  Final: {result['final']:.6f}  (delta={result['delta']:+.6f})  Acc={result['acc']*100:.1f}%")

    # ─────────────────────────────────────
    # Analysis
    # ─────────────────────────────────────
    print("\n" + "=" * 78)
    print("  ANALYSIS")
    print("=" * 78)

    # 1. RepulsionField MNIST
    analysis1, verdict1, mean1 = analyze_convergence(
        repulsion_mnist_results, "RepulsionFieldEngine (MNIST)", expected_attractor=1/3)
    print(analysis1)

    scatter1_data = [(r['init'], r['final'], f"init={r['init']:.2f}")
                     for r in repulsion_mnist_results]
    print(ascii_scatter("RepulsionField MNIST: Init vs Final tension_scale",
                        scatter1_data, "Init", "Final"))

    traj1 = [(f"init={r['init']:.2f}", r['trajectory'])
             for r in repulsion_mnist_results]
    print(ascii_trajectory("RepulsionField MNIST: tension_scale trajectory", traj1))

    # 2. FiberBundle MNIST
    analysis2, verdict2, mean2 = analyze_convergence(
        fiber_results, "FiberBundleEngine (MNIST)", expected_attractor=1/3)
    print(analysis2)

    scatter2_data = [(r['init'], r['final'], f"init={r['init']:.2f}")
                     for r in fiber_results]
    print(ascii_scatter("FiberBundle MNIST: Init vs Final curvature_scale",
                        scatter2_data, "Init", "Final"))

    traj2 = [(f"init={r['init']:.2f}", r['trajectory'])
             for r in fiber_results]
    print(ascii_trajectory("FiberBundle MNIST: curvature_scale trajectory", traj2))

    # 3. RepulsionField CIFAR
    analysis3, verdict3, mean3 = analyze_convergence(
        repulsion_cifar_results, "RepulsionFieldEngine (CIFAR-10)", expected_attractor=1/3)
    print(analysis3)

    scatter3_data = [(r['init'], r['final'], f"init={r['init']:.2f}")
                     for r in repulsion_cifar_results]
    print(ascii_scatter("RepulsionField CIFAR: Init vs Final tension_scale",
                        scatter3_data, "Init", "Final"))

    traj3 = [(f"init={r['init']:.2f}", r['trajectory'])
             for r in repulsion_cifar_results]
    print(ascii_trajectory("RepulsionField CIFAR: tension_scale trajectory", traj3))

    # ─────────────────────────────────────
    # Cross-dataset comparison
    # ─────────────────────────────────────
    print("\n" + "=" * 78)
    print("  CROSS-DATASET COMPARISON")
    print("=" * 78)

    print(f"\n  | Dataset      | Model           | Mean Final | Std Final | Verdict         |")
    print(f"  |-------------|-----------------|------------|-----------|-----------------|")

    finals_rm = [r['final'] for r in repulsion_mnist_results]
    finals_fb = [r['final'] for r in fiber_results]
    finals_rc = [r['final'] for r in repulsion_cifar_results]

    print(f"  | MNIST       | RepulsionField  | {np.mean(finals_rm):10.6f} | {np.std(finals_rm):9.6f} | {verdict1:<15} |")
    print(f"  | MNIST       | FiberBundle     | {np.mean(finals_fb):10.6f} | {np.std(finals_fb):9.6f} | {verdict2:<15} |")
    print(f"  | CIFAR-10    | RepulsionField  | {np.mean(finals_rc):10.6f} | {np.std(finals_rc):9.6f} | {verdict3:<15} |")

    # Same attractor across datasets?
    print(f"\n  1/3 = {1/3:.6f}")
    print(f"  RepulsionField MNIST mean:  {np.mean(finals_rm):.6f}  (diff from 1/3: {np.mean(finals_rm) - 1/3:+.6f})")
    print(f"  RepulsionField CIFAR mean:  {np.mean(finals_rc):.6f}  (diff from 1/3: {np.mean(finals_rc) - 1/3:+.6f})")
    print(f"  FiberBundle MNIST mean:     {np.mean(finals_fb):.6f}  (diff from 1/3: {np.mean(finals_fb) - 1/3:+.6f})")

    # ─────────────────────────────────────
    # Final verdict
    # ─────────────────────────────────────
    print("\n" + "=" * 78)
    print("  FINAL VERDICT")
    print("=" * 78)

    verdicts = [verdict1, verdict2, verdict3]
    n_attractor = sum(1 for v in verdicts if 'ATTRACTOR' in v)
    n_bias = sum(1 for v in verdicts if v == 'BIAS')

    if n_attractor == 3:
        print("""
  1/3 IS A TRUE ATTRACTOR across all models and datasets.
  All initial values converge to approximately the same final value.
  This is consistent with 1/3 being the meta fixed-point of the
  contraction mapping f(I) = 0.7I + 0.1.
""")
    elif n_attractor >= 1:
        print(f"""
  MIXED RESULTS: {n_attractor}/3 experiments show attractor behavior.
  1/3 may be an attractor in some contexts but not universally.
  The attractor strength may depend on model architecture or data.
""")
    elif n_bias >= 2:
        print("""
  1/3 IS LIKELY INITIAL VALUE BIAS.
  Final values correlate strongly with initial values.
  The parameter does not converge to a universal value.
  The 1/3 in trained models is there because we initialized it there.
""")
    else:
        print("""
  INCONCLUSIVE: No clear pattern. More epochs or different
  learning rates may be needed to observe convergence.
""")

    # Attractor strength summary
    print("  Attractor Strength (avg |delta| per experiment):")
    for name, results in [
        ("RepulsionField MNIST", repulsion_mnist_results),
        ("FiberBundle MNIST", fiber_results),
        ("RepulsionField CIFAR", repulsion_cifar_results),
    ]:
        deltas = [abs(r['delta']) for r in results]
        print(f"    {name:<25}: avg |delta| = {np.mean(deltas):.6f}")

    print("\n" + "=" * 78)
    print("  Experiment complete.")
    print("=" * 78)


if __name__ == '__main__':
    run_experiment()
```