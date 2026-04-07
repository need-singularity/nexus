#!/usr/bin/env python3
"""H-CX-344: Universe Composition Ratios in Trained Weight Distributions

Hypothesis: The trained weight distributions of PureFieldEngine spontaneously
organize into ratios matching observed universe composition:
  - Dark energy   ~ 2/3     = 0.6667
  - Dark matter   ~ 3-e     = 0.2817
  - Ordinary matter ~ 1/e^3 = 0.0498

We train PureFieldEngine on MNIST, Fashion-MNIST, CIFAR-10 (10 epochs each),
then analyze weight distributions of engine_a and engine_g using multiple
splitting strategies:
  1. Threshold-based (above median, middle range, near-zero)
  2. Percentile-based (sorted magnitude splits)
  3. K-means with k=3

Monte Carlo null: 100,000 random 3-splits to compute p-value.
Seeds: 42, 137, 256 for reproducibility.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import math
import time
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

from model_pure_field import PureFieldEngine
from model_utils import load_mnist, load_cifar10


def train_purefield(model, train_loader, test_loader, epochs=10, lr=0.001,
                    flatten=True, verbose=True):
    """Training loop for PureFieldEngine (tension is per-sample, needs .mean())."""
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()

    train_losses = []
    test_accs = []

    for epoch in range(epochs):
        model.train()
        total_loss = 0
        for X, y in train_loader:
            if flatten:
                X = X.view(X.size(0), -1)
            optimizer.zero_grad()
            logits, tension = model(X)
            loss = criterion(logits, y) + 0.1 * tension.mean()
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        avg_loss = total_loss / len(train_loader)
        train_losses.append(avg_loss)

        model.eval()
        correct = total = 0
        with torch.no_grad():
            for X, y in test_loader:
                if flatten:
                    X = X.view(X.size(0), -1)
                logits, _ = model(X)
                correct += (logits.argmax(1) == y).sum().item()
                total += y.size(0)
        acc = correct / total
        test_accs.append(acc)

        if verbose and ((epoch + 1) % 2 == 0 or epoch == 0):
            print(f"    Epoch {epoch+1:>2}/{epochs}: Loss={avg_loss:.4f}, Acc={acc*100:.1f}%")

    return train_losses, test_accs

# ─────────────────────────────────────────
# Target ratios
# ─────────────────────────────────────────
DARK_ENERGY = 2.0 / 3.0           # 0.66667
DARK_MATTER = 3.0 - math.e        # 0.28172
ORDINARY_MATTER = 1.0 / math.e**3 # 0.04979
TARGET = np.array([DARK_ENERGY, DARK_MATTER, ORDINARY_MATTER])

SEEDS = [42, 137, 256]


def load_fashion_mnist(batch_size=64, data_dir='data'):
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.2860,), (0.3530,))
    ])
    train_ds = datasets.FashionMNIST(data_dir, train=True, download=True, transform=transform)
    test_ds = datasets.FashionMNIST(data_dir, train=False, download=True, transform=transform)
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=0)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False, num_workers=0)
    return train_loader, test_loader


def get_all_weights(model, engine_name='both'):
    """Extract weights from engine_a, engine_g, or both."""
    weights = []
    for name, param in model.named_parameters():
        if engine_name == 'both' or engine_name in name:
            weights.append(param.detach().cpu().numpy().flatten())
    return np.concatenate(weights)


def l1_distance(ratios, target):
    """Sum of absolute differences between observed ratios and target."""
    return np.sum(np.abs(np.array(ratios) - np.array(target)))


# ─────────────────────────────────────────
# Splitting strategies
# ─────────────────────────────────────────

def strategy_threshold(weights):
    """Strategy 1: Threshold-based.
    Group 1 (dark energy): weights > median
    Group 2 (dark matter): weights in middle range (not near zero, not > median)
    Group 3 (ordinary matter): near zero (|w| < 0.01 * std)
    """
    median = np.median(weights)
    std = np.std(weights)
    threshold_zero = 0.01 * std

    n = len(weights)
    near_zero = np.sum(np.abs(weights) < threshold_zero)
    above_median = np.sum(weights > median)
    middle = n - above_median - near_zero

    # Ensure no negative
    if middle < 0:
        middle = 0

    total = above_median + middle + near_zero
    return np.array([above_median / total, middle / total, near_zero / total])


def strategy_percentile(weights):
    """Strategy 2: Sort by magnitude, split at target cumulative ratios.
    Top 2/3 by magnitude = group 1
    Next (3-e) fraction = group 2
    Bottom 1/e^3 fraction = group 3
    Then measure actual weight mass in each group.
    """
    magnitudes = np.abs(weights)
    sorted_mags = np.sort(magnitudes)[::-1]
    total_mass = np.sum(sorted_mags)

    n = len(sorted_mags)
    # Split indices based on count
    idx1 = int(n * DARK_ENERGY)
    idx2 = int(n * (DARK_ENERGY + DARK_MATTER))

    mass1 = np.sum(sorted_mags[:idx1])
    mass2 = np.sum(sorted_mags[idx1:idx2])
    mass3 = np.sum(sorted_mags[idx2:])

    return np.array([mass1 / total_mass, mass2 / total_mass, mass3 / total_mass])


def strategy_kmeans(weights):
    """Strategy 3: K-means with k=3 on absolute weights."""
    from sklearn.cluster import KMeans

    magnitudes = np.abs(weights).reshape(-1, 1)
    # Subsample for speed if too many weights
    if len(magnitudes) > 50000:
        idx = np.random.choice(len(magnitudes), 50000, replace=False)
        sample = magnitudes[idx]
    else:
        sample = magnitudes

    kmeans = KMeans(n_clusters=3, n_init=10, random_state=42)
    kmeans.fit(sample)

    # Predict on all data
    labels = kmeans.predict(magnitudes)
    counts = np.bincount(labels, minlength=3).astype(float)

    # Sort by cluster center (largest first)
    centers = kmeans.cluster_centers_.flatten()
    order = np.argsort(centers)[::-1]
    counts = counts[order]

    return counts / counts.sum()


def strategy_natural_breaks(weights):
    """Strategy 4: Natural breaks using histogram valleys."""
    magnitudes = np.abs(weights)
    hist, bin_edges = np.histogram(magnitudes, bins=100)

    # Smooth histogram
    kernel = np.ones(5) / 5
    smoothed = np.convolve(hist, kernel, mode='same')

    # Find two lowest valleys (natural breaks)
    valleys = []
    for i in range(1, len(smoothed) - 1):
        if smoothed[i] < smoothed[i-1] and smoothed[i] < smoothed[i+1]:
            valleys.append((smoothed[i], i))

    if len(valleys) < 2:
        # Fallback: split at 33rd and 67th percentile of magnitudes
        p33 = np.percentile(magnitudes, 33)
        p67 = np.percentile(magnitudes, 67)
    else:
        valleys.sort()
        break_indices = sorted([v[1] for v in valleys[:2]])
        p33 = bin_edges[break_indices[0]]
        p67 = bin_edges[break_indices[1]]

    if p33 > p67:
        p33, p67 = p67, p33

    g1 = np.sum(magnitudes > p67)
    g2 = np.sum((magnitudes >= p33) & (magnitudes <= p67))
    g3 = np.sum(magnitudes < p33)

    total = g1 + g2 + g3
    return np.array([g1 / total, g2 / total, g3 / total])


def strategy_weight_energy(weights):
    """Strategy 5: Split by weight energy (w^2) contribution.
    Sort weights by magnitude, find where cumulative energy reaches
    2/3 and (2/3 + 3-e) of total energy.
    """
    magnitudes = np.abs(weights)
    sorted_mags = np.sort(magnitudes)[::-1]
    energy = sorted_mags ** 2
    cumulative = np.cumsum(energy)
    total = cumulative[-1]

    # Find boundary where cumulative energy reaches target fractions
    idx1 = np.searchsorted(cumulative, total * DARK_ENERGY)
    idx2 = np.searchsorted(cumulative, total * (DARK_ENERGY + DARK_MATTER))

    n = len(weights)
    frac1 = (idx1 + 1) / n
    frac2 = (idx2 - idx1) / n
    frac3 = (n - idx2 - 1) / n

    # Normalize
    total_frac = frac1 + frac2 + frac3
    return np.array([frac1 / total_frac, frac2 / total_frac, frac3 / total_frac])


# ─────────────────────────────────────────
# Monte Carlo null
# ─────────────────────────────────────────

def monte_carlo_pvalue(observed_distance, n_trials=100000):
    """Generate random 3-splits summing to 1, compute fraction closer than observed."""
    rng = np.random.RandomState(42)
    # Dirichlet(1,1,1) = uniform over simplex
    random_splits = rng.dirichlet([1, 1, 1], size=n_trials)
    # Sort each split descending to match our convention
    random_splits = np.sort(random_splits, axis=1)[:, ::-1]
    distances = np.sum(np.abs(random_splits - TARGET), axis=1)
    p_value = np.mean(distances <= observed_distance)
    return p_value, distances


# ─────────────────────────────────────────
# ASCII histogram
# ─────────────────────────────────────────

def ascii_histogram(weights, bins=50, width=60, title="Weight Distribution"):
    """Print ASCII histogram of weight distribution."""
    hist, bin_edges = np.histogram(weights, bins=bins)
    max_count = max(hist)
    print(f"\n{'=' * (width + 20)}")
    print(f"  {title}")
    print(f"  N={len(weights):,}  mean={np.mean(weights):.6f}  std={np.std(weights):.6f}")
    print(f"  min={np.min(weights):.6f}  max={np.max(weights):.6f}  median={np.median(weights):.6f}")
    print(f"{'=' * (width + 20)}")
    for i in range(len(hist)):
        bar_len = int(hist[i] / max_count * width) if max_count > 0 else 0
        left = bin_edges[i]
        print(f"  {left:>8.4f} | {'#' * bar_len}")
    print(f"  {bin_edges[-1]:>8.4f} |")
    print()


# ─────────────────────────────────────────
# Main experiment
# ─────────────────────────────────────────

def run_experiment():
    print("=" * 80)
    print("  H-CX-344: Universe Composition Ratios in Trained Weight Distributions")
    print("=" * 80)
    print(f"\n  Target ratios (universe composition):")
    print(f"    Dark energy:    2/3      = {DARK_ENERGY:.6f}")
    print(f"    Dark matter:    3-e      = {DARK_MATTER:.6f}")
    print(f"    Ordinary matter: 1/e^3   = {ORDINARY_MATTER:.6f}")
    print(f"    Sum:                       {DARK_ENERGY + DARK_MATTER + ORDINARY_MATTER:.6f}")
    print()

    datasets_config = {
        'MNIST': {'loader': lambda bs: load_mnist(batch_size=bs), 'input_dim': 784, 'flatten': True},
        'FashionMNIST': {'loader': lambda bs: load_fashion_mnist(batch_size=bs), 'input_dim': 784, 'flatten': True},
        'CIFAR-10': {'loader': lambda bs: load_cifar10(batch_size=bs), 'input_dim': 3072, 'flatten': True},
    }

    strategy_names = ['Threshold', 'Percentile', 'K-Means', 'NaturalBreaks', 'WeightEnergy']
    strategy_fns = [strategy_threshold, strategy_percentile, strategy_kmeans,
                    strategy_natural_breaks, strategy_weight_energy]

    # Store all results
    all_results = {}  # (dataset, seed, engine, strategy) -> ratios

    for ds_name, ds_config in datasets_config.items():
        print(f"\n{'#' * 80}")
        print(f"  Dataset: {ds_name}")
        print(f"{'#' * 80}")

        train_loader, test_loader = ds_config['loader'](64)

        for seed in SEEDS:
            print(f"\n  --- Seed {seed} ---")
            torch.manual_seed(seed)
            np.random.seed(seed)

            model = PureFieldEngine(
                input_dim=ds_config['input_dim'],
                hidden_dim=128,
                output_dim=10
            )

            # Train
            _, test_accs = train_purefield(
                model, train_loader, test_loader,
                epochs=10, lr=0.001,
                flatten=ds_config['flatten'],
                verbose=True
            )
            final_acc = test_accs[-1]
            print(f"  Final accuracy: {final_acc*100:.1f}%")

            # Analyze weights for each engine
            for engine in ['engine_a', 'engine_g', 'both']:
                weights = get_all_weights(model, engine)

                if seed == 42 and engine == 'both':
                    ascii_histogram(weights, bins=40,
                                    title=f"{ds_name} — All Weights (seed=42)")

                for strat_name, strat_fn in zip(strategy_names, strategy_fns):
                    try:
                        ratios = strat_fn(weights)
                        dist = l1_distance(ratios, TARGET)
                        all_results[(ds_name, seed, engine, strat_name)] = {
                            'ratios': ratios,
                            'distance': dist,
                            'accuracy': final_acc
                        }
                    except Exception as e:
                        print(f"  WARNING: {strat_name} failed for {engine}: {e}")
                        all_results[(ds_name, seed, engine, strat_name)] = {
                            'ratios': np.array([np.nan, np.nan, np.nan]),
                            'distance': np.inf,
                            'accuracy': final_acc
                        }

    # ─────────────────────────────────────────
    # Summary tables
    # ─────────────────────────────────────────

    print("\n" + "=" * 120)
    print("  RESULTS SUMMARY")
    print("=" * 120)

    # Table 1: All strategies, all datasets, engine=both, averaged over seeds
    print("\n## Table 1: Average Ratios by Strategy and Dataset (engine=both, avg over 3 seeds)")
    print()
    print(f"| {'Dataset':<14} | {'Strategy':<14} | {'R1 (DE=.667)':<14} | {'R2 (DM=.282)':<14} | {'R3 (OM=.050)':<14} | {'L1 Dist':<10} |")
    print(f"|{'-'*16}|{'-'*16}|{'-'*16}|{'-'*16}|{'-'*16}|{'-'*12}|")

    best_overall = None
    best_dist = np.inf

    for ds_name in datasets_config:
        for strat_name in strategy_names:
            ratios_list = []
            dists_list = []
            for seed in SEEDS:
                r = all_results.get((ds_name, seed, 'both', strat_name))
                if r and not np.any(np.isnan(r['ratios'])):
                    ratios_list.append(r['ratios'])
                    dists_list.append(r['distance'])

            if ratios_list:
                avg_ratios = np.mean(ratios_list, axis=0)
                avg_dist = np.mean(dists_list)
                marker = ""
                if avg_dist < best_dist:
                    best_dist = avg_dist
                    best_overall = (ds_name, strat_name, avg_ratios, avg_dist)
                print(f"| {ds_name:<14} | {strat_name:<14} | {avg_ratios[0]:>12.6f}   | {avg_ratios[1]:>12.6f}   | {avg_ratios[2]:>12.6f}   | {avg_dist:>10.6f} |")

    print()

    # Table 2: Engine comparison (engine_a vs engine_g vs both)
    print("\n## Table 2: Engine Comparison (best strategy per engine, avg over 3 seeds)")
    print()
    print(f"| {'Dataset':<14} | {'Engine':<10} | {'Best Strategy':<14} | {'R1':<10} | {'R2':<10} | {'R3':<10} | {'L1 Dist':<10} |")
    print(f"|{'-'*16}|{'-'*12}|{'-'*16}|{'-'*12}|{'-'*12}|{'-'*12}|{'-'*12}|")

    for ds_name in datasets_config:
        for engine in ['engine_a', 'engine_g', 'both']:
            best_strat = None
            best_d = np.inf
            best_r = None
            for strat_name in strategy_names:
                dists = []
                rats = []
                for seed in SEEDS:
                    r = all_results.get((ds_name, seed, engine, strat_name))
                    if r and not np.any(np.isnan(r['ratios'])):
                        dists.append(r['distance'])
                        rats.append(r['ratios'])
                if dists:
                    avg_d = np.mean(dists)
                    if avg_d < best_d:
                        best_d = avg_d
                        best_strat = strat_name
                        best_r = np.mean(rats, axis=0)

            if best_strat:
                print(f"| {ds_name:<14} | {engine:<10} | {best_strat:<14} | {best_r[0]:>8.4f}   | {best_r[1]:>8.4f}   | {best_r[2]:>8.4f}   | {best_d:>8.4f}   |")

    print()

    # Table 3: Seed consistency
    print("\n## Table 3: Seed Consistency (best overall strategy, engine=both)")
    print()
    if best_overall:
        ds_best, strat_best = best_overall[0], best_overall[1]
        print(f"  Best: {ds_best} / {strat_best}")
        print()
        print(f"| {'Seed':<6} | {'R1 (DE=.667)':<14} | {'R2 (DM=.282)':<14} | {'R3 (OM=.050)':<14} | {'L1 Dist':<10} | {'Accuracy':<10} |")
        print(f"|{'-'*8}|{'-'*16}|{'-'*16}|{'-'*16}|{'-'*12}|{'-'*12}|")
        for seed in SEEDS:
            r = all_results.get((ds_best, seed, 'both', strat_best))
            if r and not np.any(np.isnan(r['ratios'])):
                print(f"| {seed:<6} | {r['ratios'][0]:>12.6f}   | {r['ratios'][1]:>12.6f}   | {r['ratios'][2]:>12.6f}   | {r['distance']:>10.6f} | {r['accuracy']*100:>8.1f}%  |")

    print()

    # ─────────────────────────────────────────
    # Monte Carlo p-value
    # ─────────────────────────────────────────

    print("\n## Monte Carlo Null Test (100,000 random Dirichlet splits)")
    print()

    # Collect all observed distances for engine=both
    observed_distances = {}
    for ds_name in datasets_config:
        for strat_name in strategy_names:
            dists = []
            for seed in SEEDS:
                r = all_results.get((ds_name, seed, 'both', strat_name))
                if r and not np.isinf(r['distance']):
                    dists.append(r['distance'])
            if dists:
                observed_distances[(ds_name, strat_name)] = np.mean(dists)

    # Run Monte Carlo once (same null for all)
    print("  Running Monte Carlo simulation...")
    t0 = time.time()
    # Use best observed distance
    best_obs_dist = min(observed_distances.values()) if observed_distances else np.inf
    p_value, null_distances = monte_carlo_pvalue(best_obs_dist, n_trials=100000)
    mc_time = time.time() - t0
    print(f"  Done in {mc_time:.1f}s")
    print()

    print(f"| {'Dataset':<14} | {'Strategy':<14} | {'Obs L1 Dist':<12} | {'p-value':<10} | {'Sig?':<6} |")
    print(f"|{'-'*16}|{'-'*16}|{'-'*14}|{'-'*12}|{'-'*8}|")

    for (ds_name, strat_name), obs_dist in sorted(observed_distances.items()):
        p = np.mean(null_distances <= obs_dist)
        sig = "***" if p < 0.001 else ("**" if p < 0.01 else ("*" if p < 0.05 else "ns"))
        print(f"| {ds_name:<14} | {strat_name:<14} | {obs_dist:>10.6f}   | {p:>8.6f}   | {sig:<6} |")

    print()

    # Null distribution summary
    print(f"  Null distribution (Dirichlet(1,1,1) sorted descending):")
    print(f"    Mean L1 distance:   {np.mean(null_distances):.6f}")
    print(f"    Std L1 distance:    {np.std(null_distances):.6f}")
    print(f"    5th percentile:     {np.percentile(null_distances, 5):.6f}")
    print(f"    1st percentile:     {np.percentile(null_distances, 1):.6f}")
    print(f"    Best observed:      {best_obs_dist:.6f}")
    print()

    # ASCII histogram of null distances
    print("  Null Distribution Histogram:")
    hist, bin_edges = np.histogram(null_distances, bins=30)
    max_h = max(hist)
    for i in range(len(hist)):
        bar = '#' * int(hist[i] / max_h * 50)
        marker = " <-- observed" if bin_edges[i] <= best_obs_dist < bin_edges[i+1] else ""
        print(f"    {bin_edges[i]:.3f} | {bar}{marker}")
    print(f"    {bin_edges[-1]:.3f} |")
    print()

    # ─────────────────────────────────────────
    # Additional: compare trained vs random init
    # ─────────────────────────────────────────

    print("\n## Control: Random (Untrained) Weights")
    print()
    print(f"| {'Engine':<10} | {'Strategy':<14} | {'R1':<10} | {'R2':<10} | {'R3':<10} | {'L1 Dist':<10} |")
    print(f"|{'-'*12}|{'-'*16}|{'-'*12}|{'-'*12}|{'-'*12}|{'-'*12}|")

    torch.manual_seed(42)
    random_model = PureFieldEngine(784, 128, 10)
    for engine in ['both']:
        weights = get_all_weights(random_model, engine)
        for strat_name, strat_fn in zip(strategy_names, strategy_fns):
            try:
                ratios = strat_fn(weights)
                dist = l1_distance(ratios, TARGET)
                print(f"| {engine:<10} | {strat_name:<14} | {ratios[0]:>8.4f}   | {ratios[1]:>8.4f}   | {ratios[2]:>8.4f}   | {dist:>8.4f}   |")
            except Exception as e:
                print(f"| {engine:<10} | {strat_name:<14} | ERROR: {e}")

    print()

    # ─────────────────────────────────────────
    # Final verdict
    # ─────────────────────────────────────────

    print("\n" + "=" * 80)
    print("  VERDICT")
    print("=" * 80)

    if best_overall:
        ds_best, strat_best, avg_r, avg_d = best_overall
        best_p = np.mean(null_distances <= avg_d)
        print(f"\n  Best match: {ds_best} / {strat_best}")
        print(f"    Ratios:   [{avg_r[0]:.4f}, {avg_r[1]:.4f}, {avg_r[2]:.4f}]")
        print(f"    Target:   [{DARK_ENERGY:.4f}, {DARK_MATTER:.4f}, {ORDINARY_MATTER:.4f}]")
        print(f"    L1 dist:  {avg_d:.6f}")
        print(f"    p-value:  {best_p:.6f}")

        if best_p < 0.01:
            print(f"\n  RESULT: SIGNIFICANT (p < 0.01)")
            print(f"  Universe composition ratios appear non-randomly in weight distributions.")
        elif best_p < 0.05:
            print(f"\n  RESULT: WEAKLY SIGNIFICANT (p < 0.05)")
            print(f"  Some evidence for universe composition ratios, but could be marginal.")
        else:
            print(f"\n  RESULT: NOT SIGNIFICANT (p = {best_p:.4f})")
            print(f"  No evidence that universe composition ratios emerge in trained weights.")
            print(f"  The observed match is within random chance (Dirichlet null).")

    print()
    print("  Experiment complete.")
    print("=" * 80)


if __name__ == '__main__':
    t_start = time.time()
    run_experiment()
    print(f"\n  Total time: {time.time() - t_start:.1f}s")
