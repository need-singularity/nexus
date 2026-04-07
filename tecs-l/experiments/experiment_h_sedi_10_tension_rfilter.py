#!/usr/bin/env python3
"""H-SEDI-10: R-filter on tension vectors detects anomalies.
Apply SEDI ratio detection to per-class tension vectors from trained PureField.
Look for structured patterns (golden ratio, sigma/tau, phi/tau ratios).
"""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import torch, torch.nn as nn, numpy as np
from model_pure_field import PureFieldEngine
from model_utils import load_mnist

# Key ratios from SEDI / TECS-L constant system
TARGETS = {
    'sigma/tau': 12/4,       # 3.0
    'phi/tau': 2/4,          # 0.5
    'sigma_inv': 2.0,
    '1/e': 1/np.e,           # 0.3679
    'golden': (1+np.sqrt(5))/2,  # 1.618
    'ln(4/3)': np.log(4/3),     # 0.2877
}

def ratio_scan(values, tolerance=0.05):
    """Scan all consecutive ratios for known constants."""
    hits = {k: 0 for k in TARGETS}
    total_ratios = 0
    all_ratios = []
    for i in range(len(values) - 1):
        if abs(values[i+1]) > 1e-8 and abs(values[i]) > 1e-8:
            r = values[i] / values[i+1]
            r_inv = values[i+1] / values[i]
            all_ratios.extend([r, r_inv])
            total_ratios += 2
            for name, target in TARGETS.items():
                if abs(r - target) / target < tolerance or abs(r_inv - target) / target < tolerance:
                    hits[name] += 1
    return hits, total_ratios, all_ratios

def main():
    print("=" * 60)
    print("H-SEDI-10: R-filter on Tension Vectors")
    print("=" * 60)
    train_loader, test_loader = load_mnist(batch_size=64)

    # Train model
    model = PureFieldEngine(784, 128, 10)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.CrossEntropyLoss()
    for epoch in range(5):
        model.train()
        for X, y in train_loader:
            X = X.view(X.size(0), -1)
            optimizer.zero_grad()
            out, _ = model(X)
            loss = criterion(out, y)
            loss.backward()
            optimizer.step()
    print("  Model trained (5 epochs)")

    # Extract per-class tensions
    model.eval()
    class_tensions = {i: [] for i in range(10)}
    with torch.no_grad():
        for X, y in test_loader:
            X = X.view(X.size(0), -1)
            out, tension = model(X)
            for i in range(len(y)):
                class_tensions[y[i].item()].append(tension[i].item())

    print(f"\n--- Per-Class Tension Statistics ---")
    print(f"{'Class':>6} {'Mean':>10} {'Std':>10} {'N':>6}")
    print("-" * 35)
    mean_tensions = []
    for c in range(10):
        t = np.array(class_tensions[c])
        mean_tensions.append(t.mean())
        print(f"{c:>6} {t.mean():>10.4f} {t.std():>10.4f} {len(t):>6}")

    # R-filter: ratio scan on sorted class tensions
    sorted_tensions = np.sort(mean_tensions)
    hits, total, all_ratios = ratio_scan(sorted_tensions)
    print(f"\n--- Ratio Scan (sorted class means, tol=5%) ---")
    print(f"{'Target':>12} {'Value':>8} {'Hits':>6}")
    print("-" * 30)
    total_hits = 0
    for name, target in TARGETS.items():
        print(f"{name:>12} {target:>8.4f} {hits[name]:>6}")
        total_hits += hits[name]

    # Also scan all pairwise ratios (not just consecutive)
    print(f"\n--- All Pairwise Ratio Scan ---")
    pw_hits = {k: 0 for k in TARGETS}
    pw_total = 0
    for i in range(10):
        for j in range(10):
            if i != j and mean_tensions[j] > 1e-8:
                r = mean_tensions[i] / mean_tensions[j]
                pw_total += 1
                for name, target in TARGETS.items():
                    if abs(r - target) / target < 0.05:
                        pw_hits[name] += 1
    print(f"{'Target':>12} {'Value':>8} {'Hits':>6} {'Rate':>8}")
    print("-" * 38)
    for name, target in TARGETS.items():
        rate = pw_hits[name] / pw_total if pw_total > 0 else 0
        print(f"{name:>12} {target:>8.4f} {pw_hits[name]:>6} {rate:>7.1%}")

    # Random baseline: shuffle tensions, repeat
    print(f"\n--- Random Baseline (1000 shuffles) ---")
    rng = np.random.default_rng(42)
    random_hits_total = {k: 0 for k in TARGETS}
    for _ in range(1000):
        shuffled = rng.permutation(mean_tensions)
        rh, _, _ = ratio_scan(shuffled)
        for k in TARGETS:
            random_hits_total[k] += rh[k]
    print(f"{'Target':>12} {'Real':>6} {'Random(avg)':>12} {'Ratio':>8}")
    print("-" * 42)
    structured = False
    for name in TARGETS:
        real = hits[name]
        rand_avg = random_hits_total[name] / 1000
        ratio = real / rand_avg if rand_avg > 0 else float('inf') if real > 0 else 1.0
        if real > 0 and ratio > 2.0:
            structured = True
        print(f"{name:>12} {real:>6} {rand_avg:>12.2f} {ratio:>7.1f}x")

    print(f"\n{'='*60}")
    print(f"VERDICT:")
    print(f"  Total consecutive ratio hits: {total_hits}/{total}")
    print(f"  Structured patterns found = {structured}")
    status = "SUPPORTED" if structured else "PARTIAL" if total_hits > 0 else "REFUTED"
    print(f"  Status: {status}")

if __name__ == '__main__':
    main()
