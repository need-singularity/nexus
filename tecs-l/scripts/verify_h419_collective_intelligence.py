#!/usr/bin/env python3
"""H-CX-419: N=6 Engines = Optimal Collective Intelligence
Test if N=6 engines achieves optimal diversity-accuracy Pareto front.
"""
import numpy as np
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score
import warnings
warnings.filterwarnings('ignore')

np.random.seed(42)

# Load digits dataset
X, y = load_digits(return_X_y=True)
X = X / 16.0  # normalize
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

def create_diverse_engines(n_engines, X_train, y_train):
    """Create n diverse engines via bootstrap + architecture variation."""
    engines = []
    hidden_sizes = [(32,), (64,), (32, 16), (64, 32), (48,), (24, 12),
                    (40,), (56,), (32, 32), (48, 24), (64, 16), (36,)]
    for i in range(n_engines):
        # Bootstrap sampling for diversity
        idx = np.random.choice(len(X_train), size=len(X_train), replace=True)
        X_boot, y_boot = X_train[idx], y_train[idx]

        h = hidden_sizes[i % len(hidden_sizes)]
        clf = MLPClassifier(hidden_layer_sizes=h, max_iter=300,
                           random_state=i*17+3, alpha=0.01)
        clf.fit(X_boot, y_boot)
        engines.append(clf)
    return engines

def measure_ensemble(engines, X_test, y_test):
    """Measure accuracy, diversity, and their product."""
    # Get predictions from each engine
    preds = np.array([e.predict(X_test) for e in engines])
    n = len(engines)

    # Majority vote accuracy
    from scipy import stats
    majority_vote = stats.mode(preds, axis=0)[0].flatten()
    accuracy = accuracy_score(y_test, majority_vote)

    # Diversity: average pairwise disagreement rate
    disagreements = 0
    pairs = 0
    for i in range(n):
        for j in range(i+1, n):
            disagreements += np.mean(preds[i] != preds[j])
            pairs += 1
    diversity = disagreements / pairs if pairs > 0 else 0

    # Count distinct voting patterns
    patterns = set()
    for col in range(preds.shape[1]):
        pattern = tuple(preds[:, col])
        patterns.add(pattern)
    n_patterns = len(patterns)

    # Subgroup analysis: for divisors of N, check subgroup voting
    divisors = [d for d in range(1, n+1) if n % d == 0]

    return accuracy, diversity, accuracy * diversity, n_patterns, divisors

# Test N = 1..12
test_ns = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12]
results = {}

print("=" * 70)
print("H-CX-419: Collective Intelligence — N engines experiment")
print("=" * 70)
print(f"Dataset: sklearn digits (1797 samples, 10 classes)")
print(f"Train: {len(X_train)}, Test: {len(X_test)}")
print()

for n in test_ns:
    engines = create_diverse_engines(n, X_train, y_train)
    acc, div, prod, n_pat, divs = measure_ensemble(engines, X_test, y_test)
    results[n] = (acc, div, prod, n_pat, divs)
    print(f"N={n:2d}: Acc={acc:.4f}  Div={div:.4f}  Prod={prod:.4f}  Patterns={n_pat:3d}  Divisors={divs}")

print()
print("=" * 70)
print("RESULTS TABLE")
print("=" * 70)
print(f"| N  | Accuracy | Diversity | Acc×Div  | Patterns | #Divisors |")
print(f"|----|----------|-----------|----------|----------|-----------|")
for n in test_ns:
    acc, div, prod, n_pat, divs = results[n]
    print(f"| {n:2d} | {acc:.4f}  | {div:.4f}   | {prod:.4f}  | {n_pat:3d}      | {len(divs):2d}        |")

# Find optimal N
best_prod_n = max(results, key=lambda n: results[n][2])
best_acc_n = max(results, key=lambda n: results[n][0])
print()
print(f"Best Acc×Div product: N={best_prod_n} (product={results[best_prod_n][2]:.4f})")
print(f"Best accuracy:        N={best_acc_n} (acc={results[best_acc_n][0]:.4f})")

# ASCII graph: Accuracy
print()
print("--- ASCII Graph: Accuracy vs N ---")
accs = [results[n][0] for n in test_ns]
min_a, max_a = min(accs), max(accs)
for n in test_ns:
    acc = results[n][0]
    bar_len = int((acc - min_a) / (max_a - min_a + 1e-9) * 40) + 1
    marker = " ***" if n == best_acc_n else ""
    print(f"  N={n:2d} |{'#' * bar_len}{' ' * (41 - bar_len)}| {acc:.4f}{marker}")

# ASCII graph: Acc×Div product
print()
print("--- ASCII Graph: Acc×Div Product vs N ---")
prods = [results[n][2] for n in test_ns]
min_p, max_p = min(prods), max(prods)
for n in test_ns:
    prod = results[n][2]
    bar_len = int((prod - min_p) / (max_p - min_p + 1e-9) * 40) + 1
    marker = " ***" if n == best_prod_n else ""
    print(f"  N={n:2d} |{'#' * bar_len}{' ' * (41 - bar_len)}| {prod:.4f}{marker}")

# ASCII graph: Diversity
print()
print("--- ASCII Graph: Diversity vs N ---")
divs_vals = [results[n][1] for n in test_ns]
min_d, max_d = min(divs_vals), max(divs_vals)
for n in test_ns:
    div = results[n][1]
    if max_d - min_d > 0:
        bar_len = int((div - min_d) / (max_d - min_d) * 40) + 1
    else:
        bar_len = 20
    print(f"  N={n:2d} |{'#' * bar_len}{' ' * (41 - bar_len)}| {div:.4f}")

# Perfect number analysis
print()
print("=" * 70)
print("PERFECT NUMBER ANALYSIS")
print("=" * 70)
print(f"sigma(6)  = 12,  tau(6) = 4,  phi(6) = 2,  sigma_-1(6) = 2")
print(f"Proper divisors of 6: {{1, 2, 3}} — sum = 6 (perfect)")
print()

# Divisor flexibility score
print("Divisor flexibility (# of proper subgroup sizes):")
for n in test_ns:
    divs = [d for d in range(1, n+1) if n % d == 0]
    proper = [d for d in divs if d < n]
    print(f"  N={n:2d}: divisors={divs}, proper subgroups={proper}, flex={len(proper)}")

# Check sigma_-1 relationship
print()
print("sigma_-1(n) = sum(1/d for d in divisors):")
for n in [6, 12, 28]:
    divs = [d for d in range(1, n+1) if n % d == 0]
    sigma_inv = sum(1/d for d in divs)
    print(f"  sigma_-1({n}) = {sigma_inv:.4f}")

# Phase transition check
print()
print("Phase transition check (Acc×Div jumps):")
for i in range(1, len(test_ns)):
    n_prev, n_curr = test_ns[i-1], test_ns[i]
    delta = results[n_curr][2] - results[n_prev][2]
    arrow = ">>>" if abs(delta) > 0.005 else "   "
    print(f"  N={n_prev:2d}→{n_curr:2d}: delta(Prod)={delta:+.4f} {arrow}")

print()
print("DONE")
