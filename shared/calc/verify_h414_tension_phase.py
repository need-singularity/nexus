#!/usr/bin/env python3
"""H-CX-414 Verification: Tension Phase Diagram = Phase Transition

Scans learning rate (temperature proxy) and measures converged tension.
Looks for phase transition signatures: discontinuity (1st order) or
power-law divergence (2nd order) near a critical point.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from scipy import stats
from scipy.optimize import curve_fit
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model_pure_field import PureFieldEngine
from model_utils import load_mnist

def train_at_temperature(lr, train_loader, epochs=5, seed=42):
    """Train PureFieldEngine at given learning rate, return final tension stats."""
    torch.manual_seed(seed)
    model = PureFieldEngine(784, 128, 10)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()

    tension_history = []

    for epoch in range(epochs):
        model.train()
        epoch_tensions = []
        for X, y in train_loader:
            X = X.view(X.size(0), -1)
            optimizer.zero_grad()
            output, tension = model(X)
            loss = criterion(output, y) + 0.01 * tension.mean()
            loss.backward()
            optimizer.step()
            epoch_tensions.append(tension.mean().item())
        tension_history.append(np.mean(epoch_tensions))

    # Evaluate final tension on full pass
    model.eval()
    final_tensions = []
    with torch.no_grad():
        for X, y in train_loader:
            X = X.view(X.size(0), -1)
            _, tension = model(X)
            final_tensions.extend(tension.numpy().tolist())

    return {
        'mean': np.mean(final_tensions),
        'std': np.std(final_tensions),
        'median': np.median(final_tensions),
        'history': tension_history,
    }


def power_law(x, a, beta, x_c):
    """Power law near critical point: a * |x - x_c|^(-beta)"""
    return a * np.abs(x - x_c + 1e-10) ** (-beta)


def main():
    print("=" * 65)
    print("  H-CX-414 Verification: Tension Phase Diagram")
    print("=" * 65)

    torch.manual_seed(42)
    np.random.seed(42)

    print("\n[1] Loading MNIST (subset for speed)...")
    train_loader, _ = load_mnist(batch_size=256)

    # Use subset for speed
    subset_data = []
    for i, (X, y) in enumerate(train_loader):
        subset_data.append((X, y))
        if i >= 19:  # ~5000 samples
            break

    # Scan temperatures (learning rates)
    temperatures = np.logspace(-4, -0.3, 20)  # 0.0001 to ~0.5

    print(f"\n[2] Scanning {len(temperatures)} temperatures (lr)...")
    print("-" * 65)
    print(f"  {'lr':>12} {'Mean T':>10} {'Std T':>10} {'Median T':>10} {'T trend':>10}")
    print("-" * 65)

    results = []
    for lr in temperatures:
        res = train_at_temperature(lr, subset_data, epochs=5)
        trend = res['history'][-1] - res['history'][0] if len(res['history']) > 1 else 0
        results.append(res)
        print(f"  {lr:>12.6f} {res['mean']:>10.4f} {res['std']:>10.4f} {res['median']:>10.4f} {trend:>+10.4f}")

    print("-" * 65)

    # Extract arrays
    means = np.array([r['mean'] for r in results])
    stds = np.array([r['std'] for r in results])
    log_lr = np.log10(temperatures)

    # Compute derivative (dT/d(log_lr)) to find discontinuities
    dT = np.diff(means) / np.diff(log_lr)
    d2T = np.diff(dT) / np.diff(log_lr[:-1])

    print("\n[3] Phase Transition Analysis")
    print("-" * 55)

    # Find max derivative (steepest change = potential transition)
    max_dT_idx = np.argmax(np.abs(dT))
    critical_lr = 10**((log_lr[max_dT_idx] + log_lr[max_dT_idx+1])/2)
    max_dT_val = dT[max_dT_idx]

    print(f"  Max |dT/d(log lr)| at lr = {critical_lr:.6f}")
    print(f"  dT/d(log lr) = {max_dT_val:.4f}")

    # Check for discontinuity vs smooth transition
    jump_ratio = np.max(np.abs(dT)) / (np.mean(np.abs(dT)) + 1e-10)
    print(f"  Jump ratio (max/mean dT): {jump_ratio:.2f}")

    if jump_ratio > 5:
        print(f"  --> Strong discontinuity detected (1st order candidate)")
        transition_type = "1st order"
    elif jump_ratio > 2:
        print(f"  --> Moderate transition (could be 2nd order)")
        transition_type = "2nd order candidate"
    else:
        print(f"  --> Smooth crossover (no sharp transition)")
        transition_type = "crossover"

    # Try power-law fit near critical point
    print("\n[4] Power-law fit attempt: T ~ |lr - lr_c|^(-beta)")
    try:
        # Use points near the transition
        mask = np.abs(log_lr - np.log10(critical_lr)) < 1.0
        if mask.sum() > 4:
            popt, pcov = curve_fit(power_law, temperatures[mask], means[mask],
                                    p0=[1.0, 0.5, critical_lr], maxfev=5000)
            a_fit, beta_fit, lrc_fit = popt
            residuals = means[mask] - power_law(temperatures[mask], *popt)
            ss_res = np.sum(residuals**2)
            ss_tot = np.sum((means[mask] - means[mask].mean())**2)
            r2 = 1 - ss_res / (ss_tot + 1e-10)

            print(f"  a = {a_fit:.4f}, beta = {beta_fit:.4f}, lr_c = {lrc_fit:.6f}")
            print(f"  R^2 = {r2:.4f}")

            if r2 > 0.8 and beta_fit > 0:
                print(f"  --> Power-law fits well: critical exponent beta = {beta_fit:.3f}")
                print(f"      (Mean-field theory predicts beta=0.5)")
            else:
                print(f"  --> Power-law fit is poor (R^2={r2:.4f})")
        else:
            print("  Not enough points near transition for fit")
            r2 = 0
            beta_fit = 0
    except Exception as e:
        print(f"  Power-law fit failed: {e}")
        r2 = 0
        beta_fit = 0

    # Susceptibility (variance as function of temperature)
    print("\n[5] Susceptibility (variance) analysis")
    print("-" * 55)
    print(f"  {'lr':>12} {'Variance':>12} {'Suscept.':>12}")
    print("-" * 55)
    suscept = stds**2  # chi ~ variance of order parameter
    for i in range(len(temperatures)):
        bar = "#" * int(suscept[i] / (suscept.max() + 1e-10) * 30)
        print(f"  {temperatures[i]:>12.6f} {suscept[i]:>12.4f} {bar}")
    print("-" * 55)

    max_suscept_idx = np.argmax(suscept)
    print(f"  Peak susceptibility at lr = {temperatures[max_suscept_idx]:.6f}")
    print(f"  (Diverging susceptibility = 2nd order phase transition signature)")

    # ASCII phase diagram
    print("\n[6] ASCII Phase Diagram: Tension vs Temperature (log lr)")
    height = 16
    width = 50

    t_min, t_max = means.min(), means.max()
    t_range = t_max - t_min + 1e-10

    # Build grid
    grid = [[' '] * width for _ in range(height)]
    for i, (lr_val, t_val) in enumerate(zip(log_lr, means)):
        x = int((lr_val - log_lr[0]) / (log_lr[-1] - log_lr[0] + 1e-10) * (width - 1))
        y = int((t_val - t_min) / t_range * (height - 1))
        x = max(0, min(width-1, x))
        y = max(0, min(height-1, y))
        grid[y][x] = '*'

    # Mark critical point
    cx = int((np.log10(critical_lr) - log_lr[0]) / (log_lr[-1] - log_lr[0] + 1e-10) * (width - 1))
    cx = max(0, min(width-1, cx))
    for row in range(height):
        if grid[row][cx] == ' ':
            grid[row][cx] = '|'

    print(f"  T ^")
    for row in reversed(range(height)):
        line = f"  {t_min + (row/height)*t_range:>6.2f}|{''.join(grid[row])}"
        print(line)
    print(f"       +{''.join(['-']*width)}> log(lr)")
    print(f"        {log_lr[0]:.1f}{' '*(width-10)}{log_lr[-1]:.1f}")
    print(f"        (| = critical point at lr={critical_lr:.4f})")

    # Verdict
    print("\n" + "=" * 65)
    print(f"  TRANSITION TYPE: {transition_type}")
    print(f"  CRITICAL LR:     {critical_lr:.6f}")
    print(f"  JUMP RATIO:      {jump_ratio:.2f}")
    if r2 > 0.5:
        print(f"  CRITICAL EXP:    beta = {beta_fit:.3f} (R^2={r2:.3f})")
    print(f"  PEAK SUSCEPT:    lr = {temperatures[max_suscept_idx]:.6f}")

    if jump_ratio > 2 or r2 > 0.7:
        print(f"\n  VERDICT: SUPPORTED — Phase transition behavior detected")
    else:
        print(f"\n  VERDICT: PARTIAL — Smooth crossover, no sharp transition")
    print("=" * 65)


if __name__ == '__main__':
    main()
