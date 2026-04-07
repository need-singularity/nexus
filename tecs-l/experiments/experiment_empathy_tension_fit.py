#!/usr/bin/env python3
"""Experiment: Hypothesis 266 — E = k/(1+aT) empathy-tension inverse law.

Rigorous test of the empathy-tension inverse relationship.

Plan:
  1. Train EmpathyEngine on MNIST (10 epochs)
  2. Collect per-SAMPLE empathy and tension for all 10,000 test samples
  3. Fit multiple models: Linear, Inverse, Exponential, Power
  4. Compare R^2 for each fit
  5. Per-digit analysis: fit separately for each digit
  6. ASCII scatter plot: tension vs empathy (10,000 points)
  7. Residual analysis: which model has smallest residuals?
  8. Bootstrap: resample 1000 times, confidence intervals for r
  9. Key question: is E = k/(1+aT) really the best model?

Output: fit parameters, R^2 values, ASCII scatter/residual plots, CIs.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import math
import time
import warnings
from scipy.optimize import curve_fit
from scipy.stats import pearsonr

from model_utils import (
    load_mnist, train_and_evaluate, count_params,
)
from model_empathy_engine import EmpathyEngine
from model_temporal_engine import ascii_graph, ascii_scatter


# ─────────────────────────────────────────
# Fit models
# ─────────────────────────────────────────

def model_linear(T, a, b):
    """E = a + b*T"""
    return a + b * T

def model_inverse(T, k, alpha):
    """E = k / (1 + alpha*T)"""
    return k / (1.0 + alpha * T)

def model_exponential(T, k, alpha):
    """E = k * exp(-alpha*T)"""
    return k * np.exp(-alpha * T)

def model_power(T, k, alpha):
    """E = k * T^(-alpha)  (requires T > 0)"""
    return k * np.power(T + 1e-8, -alpha)


def r_squared(y_true, y_pred):
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    if ss_tot < 1e-15:
        return 0.0
    return 1.0 - ss_res / ss_tot


def fit_all_models(T, E, label=""):
    """Fit all four models, return dict of results."""
    results = {}

    # Linear: E = a + b*T
    try:
        popt, _ = curve_fit(model_linear, T, E, p0=[np.mean(E), -0.01], maxfev=10000)
        y_pred = model_linear(T, *popt)
        r2 = r_squared(E, y_pred)
        residuals = E - y_pred
        results['Linear'] = {
            'params': {'a': popt[0], 'b': popt[1]},
            'r2': r2,
            'residuals': residuals,
            'y_pred': y_pred,
            'formula': f'E = {popt[0]:.6f} + {popt[1]:.6f}*T',
        }
    except Exception as ex:
        results['Linear'] = {'params': {}, 'r2': -1, 'residuals': np.zeros_like(E),
                             'y_pred': np.zeros_like(E), 'formula': f'FAILED: {ex}'}

    # Inverse: E = k / (1 + alpha*T)
    try:
        popt, _ = curve_fit(model_inverse, T, E,
                            p0=[np.max(E), 1.0], maxfev=10000,
                            bounds=([0, 0], [np.inf, np.inf]))
        y_pred = model_inverse(T, *popt)
        r2 = r_squared(E, y_pred)
        residuals = E - y_pred
        results['Inverse'] = {
            'params': {'k': popt[0], 'alpha': popt[1]},
            'r2': r2,
            'residuals': residuals,
            'y_pred': y_pred,
            'formula': f'E = {popt[0]:.6f} / (1 + {popt[1]:.6f}*T)',
        }
    except Exception as ex:
        results['Inverse'] = {'params': {}, 'r2': -1, 'residuals': np.zeros_like(E),
                              'y_pred': np.zeros_like(E), 'formula': f'FAILED: {ex}'}

    # Exponential: E = k * exp(-alpha*T)
    try:
        popt, _ = curve_fit(model_exponential, T, E,
                            p0=[np.max(E), 0.1], maxfev=10000,
                            bounds=([0, 0], [np.inf, np.inf]))
        y_pred = model_exponential(T, *popt)
        r2 = r_squared(E, y_pred)
        residuals = E - y_pred
        results['Exponential'] = {
            'params': {'k': popt[0], 'alpha': popt[1]},
            'r2': r2,
            'residuals': residuals,
            'y_pred': y_pred,
            'formula': f'E = {popt[0]:.6f} * exp(-{popt[1]:.6f}*T)',
        }
    except Exception as ex:
        results['Exponential'] = {'params': {}, 'r2': -1, 'residuals': np.zeros_like(E),
                                  'y_pred': np.zeros_like(E), 'formula': f'FAILED: {ex}'}

    # Power: E = k * T^(-alpha)
    try:
        # Filter T > 0 for power fit
        mask = T > 1e-6
        if mask.sum() > 10:
            popt, _ = curve_fit(model_power, T[mask], E[mask],
                                p0=[np.max(E), 0.5], maxfev=10000,
                                bounds=([0, 0], [np.inf, 10.0]))
            y_pred_full = model_power(T, *popt)
            r2 = r_squared(E[mask], model_power(T[mask], *popt))
            residuals = E - y_pred_full
            results['Power'] = {
                'params': {'k': popt[0], 'alpha': popt[1]},
                'r2': r2,
                'residuals': residuals,
                'y_pred': y_pred_full,
                'formula': f'E = {popt[0]:.6f} * T^(-{popt[1]:.6f})',
            }
        else:
            raise ValueError("Not enough T > 0 samples")
    except Exception as ex:
        results['Power'] = {'params': {}, 'r2': -1, 'residuals': np.zeros_like(E),
                            'y_pred': np.zeros_like(E), 'formula': f'FAILED: {ex}'}

    return results


def ascii_scatter_dense(xs, ys, title, width=70, height=25,
                        label_x="x", label_y="y"):
    """ASCII scatter for many points with density markers."""
    if len(xs) == 0:
        print(f"  [{title}] (no data)")
        return

    x_min, x_max = float(np.min(xs)), float(np.max(xs))
    y_min, y_max = float(np.min(ys)), float(np.max(ys))
    if x_max == x_min:
        x_max = x_min + 1e-8
    if y_max == y_min:
        y_max = y_min + 1e-8

    # Count density per cell
    grid = [[0 for _ in range(width)] for _ in range(height)]
    for x, y in zip(xs, ys):
        col = int((x - x_min) / (x_max - x_min) * (width - 1))
        row = int((y - y_min) / (y_max - y_min) * (height - 1))
        col = min(max(col, 0), width - 1)
        row = min(max(row, 0), height - 1)
        grid[row][col] += 1

    # Density chars
    density_chars = ' .,:;+*#@'
    max_count = max(max(row) for row in grid)
    if max_count == 0:
        max_count = 1

    print(f"\n  {title}")
    print(f"  {label_y}  (n={len(xs)})")

    for row in range(height - 1, -1, -1):
        if row == height - 1:
            line = f"  {y_max:>8.4f} |"
        elif row == 0:
            line = f"  {y_min:>8.4f} |"
        elif row == height // 2:
            mid = (y_max + y_min) / 2
            line = f"  {mid:>8.4f} |"
        else:
            line = "           |"

        for col in range(width):
            count = grid[row][col]
            if count == 0:
                line += ' '
            else:
                idx = min(int(count / max_count * (len(density_chars) - 1)), len(density_chars) - 1)
                idx = max(idx, 1)  # at least '.'
                line += density_chars[idx]

        print(line)

    print("           +" + "-" * width)
    print(f"   {label_x}: {x_min:.4f}{' ' * (width - 24)}{x_max:.4f}")


def ascii_residual_plot(residuals, title, width=70, height=15):
    """ASCII plot of residuals (horizontal histogram-like)."""
    if len(residuals) == 0:
        return

    # Sort residuals into bins
    n_bins = width
    r_min, r_max = float(np.min(residuals)), float(np.max(residuals))
    if r_max == r_min:
        r_max = r_min + 1e-8

    bins = np.linspace(r_min, r_max, n_bins + 1)
    counts, _ = np.histogram(residuals, bins=bins)
    max_count = max(counts) if len(counts) > 0 else 1

    print(f"\n  {title}")
    print(f"  Residual distribution (mean={np.mean(residuals):.6f}, std={np.std(residuals):.6f})")

    for row in range(height - 1, -1, -1):
        threshold = max_count * row / (height - 1)
        line = "           |"
        for col in range(min(n_bins, len(counts))):
            if counts[col] >= threshold:
                line += '#'
            else:
                line += ' '
        print(line)

    print("           +" + "-" * n_bins)
    print(f"   residual: {r_min:.4f}{' ' * (n_bins - 24)}{r_max:.4f}")


# ─────────────────────────────────────────
# Main experiment
# ─────────────────────────────────────────

def main():
    print()
    print("=" * 75)
    print("   Hypothesis 266: E = k/(1+aT) Empathy-Tension Inverse Law")
    print("   Rigorous curve fitting on per-sample data (10,000 test points)")
    print("=" * 75)

    # ══════════════════════════════════════════
    # 1. Train EmpathyEngine on MNIST
    # ══════════════════════════════════════════

    print("\n[1] Training EmpathyEngine on MNIST (10 epochs)...")
    train_loader, test_loader = load_mnist(batch_size=128)
    input_dim, hidden_dim, output_dim = 784, 48, 10
    epochs = 10

    model = EmpathyEngine(
        input_dim, hidden_dim, output_dim,
        state_dim=32, n_self_ref_steps=3,
    )

    losses, accs = train_and_evaluate(
        model, train_loader, test_loader, epochs, aux_lambda=0.01
    )

    print(f"\n  Final accuracy: {accs[-1]*100:.2f}%")
    print(f"  Final loss:     {losses[-1]:.4f}")
    print(f"  Parameters:     {count_params(model):,}")

    # ══════════════════════════════════════════
    # 2. Collect per-sample empathy and tension
    # ══════════════════════════════════════════

    print("\n[2] Collecting per-sample empathy and tension for 10,000 test samples...")
    model.eval()
    model.reset_empathy_state()
    model.base.reset_temporal_state()

    all_empathy_a = []
    all_empathy_g = []
    all_mutual_empathy = []
    all_tension = []
    all_labels = []
    all_correct = []

    t_start = time.time()
    with torch.no_grad():
        for X, y in test_loader:
            X_flat = X.view(X.size(0), -1)
            batch_size = X_flat.size(0)

            # Get pole outputs
            pole_plus = model.base.base_field.pole_plus
            pole_minus = model.base.base_field.pole_minus
            out_a = pole_plus(X_flat)
            out_g = pole_minus(X_flat)

            # Empathy predictions
            a_input = torch.cat([X_flat, out_a], dim=-1)
            a_pred_g = model.a_models_g(a_input)
            g_input = torch.cat([X_flat, out_g], dim=-1)
            g_pred_a = model.g_models_a(g_input)

            # Empathy errors and quality per sample
            err_a = (a_pred_g - out_g).pow(2).sum(dim=-1)  # (batch,)
            err_g = (g_pred_a - out_a).pow(2).sum(dim=-1)  # (batch,)
            emp_a = 1.0 / (1.0 + err_a)  # (batch,)
            emp_g = 1.0 / (1.0 + err_g)  # (batch,)
            mutual = (emp_a + emp_g) / 2.0

            # Tension per sample
            repulsion = out_a - out_g
            tension = (repulsion ** 2).sum(dim=-1)  # (batch,)

            # Classification
            out, _ = model(X_flat)
            preds = out.argmax(dim=1)

            for i in range(batch_size):
                all_empathy_a.append(emp_a[i].item())
                all_empathy_g.append(emp_g[i].item())
                all_mutual_empathy.append(mutual[i].item())
                all_tension.append(tension[i].item())
                all_labels.append(y[i].item())
                all_correct.append(int(preds[i].item() == y[i].item()))

    elapsed = time.time() - t_start
    print(f"  Collected {len(all_tension)} samples in {elapsed:.1f}s")

    T = np.array(all_tension)
    E = np.array(all_mutual_empathy)
    E_a = np.array(all_empathy_a)
    E_g = np.array(all_empathy_g)
    labels = np.array(all_labels)
    correct = np.array(all_correct)

    print(f"\n  Tension:  min={T.min():.4f}, max={T.max():.4f}, mean={T.mean():.4f}, std={T.std():.4f}")
    print(f"  Empathy:  min={E.min():.4f}, max={E.max():.4f}, mean={E.mean():.4f}, std={E.std():.4f}")
    print(f"  Emp(A->G): mean={E_a.mean():.4f}, std={E_a.std():.4f}")
    print(f"  Emp(G->A): mean={E_g.mean():.4f}, std={E_g.std():.4f}")

    # Pearson correlation
    r_val, p_val = pearsonr(T, E)
    print(f"\n  Pearson r(T, E) = {r_val:.6f}, p = {p_val:.2e}")

    # ══════════════════════════════════════════
    # 3. Fit multiple models (global)
    # ══════════════════════════════════════════

    print("\n" + "=" * 75)
    print("[3] Fitting 4 models to ALL 10,000 samples")
    print("=" * 75)

    fit_results = fit_all_models(T, E, label="Global")

    print(f"\n  {'Model':<15} {'R^2':>10} {'Residual std':>14}  Formula")
    print("  " + "-" * 75)
    best_model = None
    best_r2 = -1
    for name in ['Linear', 'Inverse', 'Exponential', 'Power']:
        r = fit_results[name]
        res_std = np.std(r['residuals']) if r['r2'] >= 0 else float('inf')
        marker = ""
        if r['r2'] > best_r2:
            best_r2 = r['r2']
            best_model = name
        print(f"  {name:<15} {r['r2']:>10.6f} {res_std:>14.6f}  {r['formula']}")

    # Mark best
    print(f"\n  >>> Best model: {best_model} (R^2 = {best_r2:.6f})")

    # ══════════════════════════════════════════
    # 4. ASCII scatter: tension vs empathy
    # ══════════════════════════════════════════

    print("\n" + "=" * 75)
    print("[4] Scatter plot: Tension vs Empathy (10,000 points)")
    print("=" * 75)

    ascii_scatter_dense(
        T.tolist(), E.tolist(),
        "Tension vs Mutual Empathy",
        width=70, height=25,
        label_x="tension", label_y="empathy"
    )

    # Also scatter for A->G and G->A separately
    ascii_scatter_dense(
        T.tolist(), E_a.tolist(),
        "Tension vs Empathy(A->G)",
        width=70, height=20,
        label_x="tension", label_y="empathy_a"
    )

    ascii_scatter_dense(
        T.tolist(), E_g.tolist(),
        "Tension vs Empathy(G->A)",
        width=70, height=20,
        label_x="tension", label_y="empathy_g"
    )

    # ══════════════════════════════════════════
    # 5. Residual analysis
    # ══════════════════════════════════════════

    print("\n" + "=" * 75)
    print("[5] Residual analysis")
    print("=" * 75)

    for name in ['Linear', 'Inverse', 'Exponential', 'Power']:
        r = fit_results[name]
        if r['r2'] < 0:
            print(f"\n  {name}: FAILED (skipping)")
            continue
        res = r['residuals']
        print(f"\n  {name}:")
        print(f"    Mean residual:   {np.mean(res):>12.8f}")
        print(f"    Std residual:    {np.std(res):>12.8f}")
        print(f"    Max |residual|:  {np.max(np.abs(res)):>12.8f}")
        print(f"    Skewness:        {float(np.mean((res - np.mean(res))**3) / (np.std(res)**3 + 1e-15)):>12.6f}")

        ascii_residual_plot(
            res, f"Residuals: {name} (R^2={r['r2']:.6f})",
            width=60, height=10
        )

    # ══════════════════════════════════════════
    # 6. Per-digit analysis
    # ══════════════════════════════════════════

    print("\n" + "=" * 75)
    print("[6] Per-digit fit analysis")
    print("=" * 75)

    print(f"\n  {'Digit':>5} | {'n':>5} | {'Linear R2':>10} | {'Inverse R2':>11} | {'Exp R2':>10} | {'Power R2':>10} | {'Best':>12} | {'r(T,E)':>8}")
    print("  " + "-" * 95)

    digit_best_models = {}
    for d in range(10):
        mask_d = labels == d
        T_d = T[mask_d]
        E_d = E[mask_d]
        n_d = mask_d.sum()

        if n_d < 20:
            print(f"  {d:>5} | {n_d:>5} | {'(too few)':>10} |")
            continue

        r_d, _ = pearsonr(T_d, E_d)
        dr = fit_all_models(T_d, E_d, label=f"Digit {d}")

        r2s = {name: dr[name]['r2'] for name in ['Linear', 'Inverse', 'Exponential', 'Power']}
        best_d = max(r2s, key=r2s.get)
        digit_best_models[d] = best_d

        print(f"  {d:>5} | {n_d:>5} | {r2s['Linear']:>10.6f} | {r2s['Inverse']:>11.6f} | {r2s['Exponential']:>10.6f} | {r2s['Power']:>10.6f} | {best_d:>12} | {r_d:>8.4f}")

    # Summary: which model wins most?
    model_wins = {}
    for d, m in digit_best_models.items():
        model_wins[m] = model_wins.get(m, 0) + 1
    print(f"\n  Model wins across digits:")
    for m, count in sorted(model_wins.items(), key=lambda x: -x[1]):
        print(f"    {m:<15}: {count}/10 digits")

    # ══════════════════════════════════════════
    # 7. Bootstrap confidence intervals
    # ══════════════════════════════════════════

    print("\n" + "=" * 75)
    print("[7] Bootstrap: 1000 resamples for correlation CI")
    print("=" * 75)

    n_bootstrap = 1000
    n_samples = len(T)
    rng = np.random.RandomState(42)

    bootstrap_r = []
    bootstrap_r2_linear = []
    bootstrap_r2_inverse = []

    print(f"\n  Running {n_bootstrap} bootstrap iterations...")
    t_boot_start = time.time()

    for b in range(n_bootstrap):
        idx = rng.choice(n_samples, size=n_samples, replace=True)
        T_b = T[idx]
        E_b = E[idx]

        # Pearson r
        r_b, _ = pearsonr(T_b, E_b)
        bootstrap_r.append(r_b)

        # Quick fits for linear and inverse only (speed)
        try:
            popt_lin, _ = curve_fit(model_linear, T_b, E_b,
                                    p0=[np.mean(E_b), -0.01], maxfev=5000)
            y_pred_lin = model_linear(T_b, *popt_lin)
            bootstrap_r2_linear.append(r_squared(E_b, y_pred_lin))
        except Exception:
            bootstrap_r2_linear.append(np.nan)

        try:
            popt_inv, _ = curve_fit(model_inverse, T_b, E_b,
                                    p0=[np.max(E_b), 1.0], maxfev=5000,
                                    bounds=([0, 0], [np.inf, np.inf]))
            y_pred_inv = model_inverse(T_b, *popt_inv)
            bootstrap_r2_inverse.append(r_squared(E_b, y_pred_inv))
        except Exception:
            bootstrap_r2_inverse.append(np.nan)

    t_boot_elapsed = time.time() - t_boot_start
    print(f"  Bootstrap completed in {t_boot_elapsed:.1f}s")

    bootstrap_r = np.array(bootstrap_r)
    bootstrap_r2_linear = np.array([x for x in bootstrap_r2_linear if not np.isnan(x)])
    bootstrap_r2_inverse = np.array([x for x in bootstrap_r2_inverse if not np.isnan(x)])

    # Confidence intervals
    r_mean = np.mean(bootstrap_r)
    r_lo = np.percentile(bootstrap_r, 2.5)
    r_hi = np.percentile(bootstrap_r, 97.5)
    print(f"\n  Pearson r(T, E):")
    print(f"    Mean:     {r_mean:.6f}")
    print(f"    95% CI:   [{r_lo:.6f}, {r_hi:.6f}]")
    print(f"    Std:      {np.std(bootstrap_r):.6f}")

    if len(bootstrap_r2_linear) > 0:
        print(f"\n  Linear R^2:")
        print(f"    Mean:     {np.mean(bootstrap_r2_linear):.6f}")
        print(f"    95% CI:   [{np.percentile(bootstrap_r2_linear, 2.5):.6f}, {np.percentile(bootstrap_r2_linear, 97.5):.6f}]")

    if len(bootstrap_r2_inverse) > 0:
        print(f"\n  Inverse R^2:")
        print(f"    Mean:     {np.mean(bootstrap_r2_inverse):.6f}")
        print(f"    95% CI:   [{np.percentile(bootstrap_r2_inverse, 2.5):.6f}, {np.percentile(bootstrap_r2_inverse, 97.5):.6f}]")

    # R^2 difference: Inverse - Linear
    if len(bootstrap_r2_inverse) > 0 and len(bootstrap_r2_linear) > 0:
        min_len = min(len(bootstrap_r2_inverse), len(bootstrap_r2_linear))
        r2_diff = bootstrap_r2_inverse[:min_len] - bootstrap_r2_linear[:min_len]
        print(f"\n  R^2 difference (Inverse - Linear):")
        print(f"    Mean:     {np.mean(r2_diff):.6f}")
        print(f"    95% CI:   [{np.percentile(r2_diff, 2.5):.6f}, {np.percentile(r2_diff, 97.5):.6f}]")
        pct_inverse_wins = np.mean(r2_diff > 0) * 100
        print(f"    Inverse > Linear in {pct_inverse_wins:.1f}% of bootstrap samples")

    # Distribution of bootstrap r
    ascii_residual_plot(
        bootstrap_r, "Bootstrap distribution of r(T, E)",
        width=60, height=10
    )

    # ══════════════════════════════════════════
    # 8. Empathy vs correct/incorrect
    # ══════════════════════════════════════════

    print("\n" + "=" * 75)
    print("[8] Empathy and tension by correctness")
    print("=" * 75)

    correct_mask = correct == 1
    wrong_mask = correct == 0

    print(f"\n  {'':>12} | {'Correct':>10} | {'Wrong':>10} | {'Diff':>10}")
    print("  " + "-" * 50)
    print(f"  {'Empathy':>12} | {E[correct_mask].mean():>10.6f} | {E[wrong_mask].mean():>10.6f} | {E[correct_mask].mean() - E[wrong_mask].mean():>10.6f}")
    print(f"  {'Tension':>12} | {T[correct_mask].mean():>10.4f} | {T[wrong_mask].mean():>10.4f} | {T[correct_mask].mean() - T[wrong_mask].mean():>10.4f}")
    print(f"  {'Emp(A->G)':>12} | {E_a[correct_mask].mean():>10.6f} | {E_a[wrong_mask].mean():>10.6f} | {E_a[correct_mask].mean() - E_a[wrong_mask].mean():>10.6f}")
    print(f"  {'Emp(G->A)':>12} | {E_g[correct_mask].mean():>10.6f} | {E_g[wrong_mask].mean():>10.6f} | {E_g[correct_mask].mean() - E_g[wrong_mask].mean():>10.6f}")
    print(f"  {'N':>12} | {correct_mask.sum():>10} | {wrong_mask.sum():>10} |")

    # ══════════════════════════════════════════
    # 9. Final verdict
    # ══════════════════════════════════════════

    print("\n" + "=" * 75)
    print("[9] VERDICT: Is E = k/(1+aT) the best model?")
    print("=" * 75)

    print(f"\n  Global fit comparison:")
    for name in ['Linear', 'Inverse', 'Exponential', 'Power']:
        r = fit_results[name]
        marker = " <<<" if name == best_model else ""
        print(f"    {name:<15} R^2 = {r['r2']:>10.6f}{marker}")

    r2_inv = fit_results['Inverse']['r2']
    r2_lin = fit_results['Linear']['r2']
    r2_exp = fit_results['Exponential']['r2']

    print(f"\n  Key comparisons:")
    print(f"    Inverse vs Linear:      R^2 diff = {r2_inv - r2_lin:+.6f}")
    print(f"    Inverse vs Exponential: R^2 diff = {r2_inv - r2_exp:+.6f}")

    if best_model == 'Inverse':
        if r2_inv - r2_lin > 0.01:
            print(f"\n  RESULT: E = k/(1+aT) is clearly the best model.")
            print(f"          The inverse law is SUPPORTED with substantial margin.")
        elif r2_inv - r2_lin > 0.001:
            print(f"\n  RESULT: E = k/(1+aT) wins, but marginally.")
            print(f"          Linear is nearly as good. The inverse form may be overfitting.")
        else:
            print(f"\n  RESULT: E = k/(1+aT) wins by a hair.")
            print(f"          Practically indistinguishable from linear. Parsimony favors linear.")
    elif best_model == 'Linear':
        print(f"\n  RESULT: Linear model wins. E = k/(1+aT) is NOT the best fit.")
        print(f"          The empathy-tension relationship is adequately described by a line.")
    elif best_model == 'Exponential':
        print(f"\n  RESULT: Exponential decay wins over inverse.")
        print(f"          E = k*exp(-aT) fits better than E = k/(1+aT).")
    else:
        print(f"\n  RESULT: Power law wins: E = k*T^(-a).")

    # Correlation strength interpretation
    print(f"\n  Correlation strength: r = {r_val:.4f}")
    abs_r = abs(r_val)
    if abs_r > 0.7:
        print(f"    Strong {'negative' if r_val < 0 else 'positive'} correlation.")
    elif abs_r > 0.4:
        print(f"    Moderate {'negative' if r_val < 0 else 'positive'} correlation.")
    elif abs_r > 0.2:
        print(f"    Weak {'negative' if r_val < 0 else 'positive'} correlation.")
    else:
        print(f"    Very weak or no correlation.")

    print(f"\n  Bootstrap 95% CI for r: [{r_lo:.4f}, {r_hi:.4f}]")
    if r_lo > 0 or r_hi < 0:
        print(f"    CI excludes zero -> correlation is statistically significant.")
    else:
        print(f"    CI includes zero -> correlation is NOT statistically significant.")

    # Final summary
    print(f"\n  === HYPOTHESIS 266 SUMMARY ===")
    print(f"  E = k/(1+aT) empathy-tension inverse law")
    if fit_results['Inverse']['r2'] >= 0:
        inv_params = fit_results['Inverse']['params']
        print(f"  Best-fit: E = {inv_params.get('k', '?'):.6f} / (1 + {inv_params.get('alpha', '?'):.6f} * T)")
        print(f"  R^2 = {fit_results['Inverse']['r2']:.6f}")
    print(f"  Pearson r = {r_val:.6f} (p = {p_val:.2e})")
    print(f"  Best overall model: {best_model}")
    print(f"  Per-digit winner: {max(model_wins, key=model_wins.get)} ({max(model_wins.values())}/10)")

    if r_val < -0.3 and best_model in ('Inverse', 'Exponential'):
        print(f"\n  CONCLUSION: Empathy-tension inverse relationship CONFIRMED.")
        print(f"  Higher tension -> lower empathy. The functional form is {best_model.lower()}.")
    elif r_val < -0.1:
        print(f"\n  CONCLUSION: Weak negative relationship exists.")
        print(f"  Direction is consistent with hypothesis but effect is small.")
    elif abs(r_val) < 0.1:
        print(f"\n  CONCLUSION: No meaningful empathy-tension relationship detected.")
        print(f"  Hypothesis 266 is NOT supported by this data.")
    else:
        print(f"\n  CONCLUSION: Positive relationship (opposite of hypothesis).")
        print(f"  Hypothesis 266 is REFUTED.")

    print("\n" + "=" * 75)
    print("  Experiment complete.")
    print("=" * 75)
    print()


if __name__ == '__main__':
    warnings.filterwarnings('ignore', category=RuntimeWarning)
    main()
