#!/usr/bin/env python3
"""H-CX-421: Telepathy = Quantum Entanglement Analog (Bell/CHSH Inequality)
Test if non-shared engines exhibit non-classical correlation (|S| > 2).
"""
import numpy as np
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score
import warnings
warnings.filterwarnings('ignore')

np.random.seed(42)

# Load data
X, y = load_digits(return_X_y=True)
X = X / 16.0

# Split into completely non-overlapping subsets for two engines
indices = np.arange(len(X))
np.random.shuffle(indices)
half = len(indices) // 2
idx_A = indices[:half]
idx_B = indices[half:]

X_A, y_A = X[idx_A], y[idx_A]
X_B, y_B = X[idx_B], y[idx_B]

# Separate test set from a third split
X_A_train, X_A_test, y_A_train, y_A_test = train_test_split(X_A, y_A, test_size=0.3, random_state=42)
X_B_train, X_B_test, y_B_train, y_B_test = train_test_split(X_B, y_B, test_size=0.3, random_state=42)

# Common test set for correlation measurement
X_common_test = np.vstack([X_A_test, X_B_test])
y_common_test = np.concatenate([y_A_test, y_B_test])

print("=" * 70)
print("H-CX-421: Bell/CHSH Inequality Analog — Tension Entanglement")
print("=" * 70)
print(f"Engine A trained on {len(X_A_train)} samples (no overlap with B)")
print(f"Engine B trained on {len(X_B_train)} samples (no overlap with A)")
print(f"Common test set: {len(X_common_test)} samples")
print()

# Train two engines on non-overlapping data
engine_A = MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=500, random_state=42, alpha=0.01)
engine_B = MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=500, random_state=99, alpha=0.01)

engine_A.fit(X_A_train, y_A_train)
engine_B.fit(X_B_train, y_B_train)

acc_A = accuracy_score(y_common_test, engine_A.predict(X_common_test))
acc_B = accuracy_score(y_common_test, engine_B.predict(X_common_test))
print(f"Engine A accuracy on common test: {acc_A:.4f}")
print(f"Engine B accuracy on common test: {acc_B:.4f}")
print()

# Get probability vectors (tension analog)
prob_A = engine_A.predict_proba(X_common_test)  # shape: (N, 10)
prob_B = engine_B.predict_proba(X_common_test)  # shape: (N, 10)

# Define "tension" as entropy of probability distribution
def entropy(probs):
    """Per-sample entropy."""
    return -np.sum(probs * np.log(probs + 1e-10), axis=1)

tension_A = entropy(prob_A)  # shape: (N,)
tension_B = entropy(prob_B)

print(f"Tension A: mean={tension_A.mean():.4f}, std={tension_A.std():.4f}")
print(f"Tension B: mean={tension_B.mean():.4f}, std={tension_B.std():.4f}")

# Basic correlation
corr_raw = np.corrcoef(tension_A, tension_B)[0, 1]
print(f"Raw tension correlation (no shared data): r = {corr_raw:.4f}")
print()

# ========== CHSH ANALOG ==========
# "Measurement direction" = projection axis in probability space
# Tension along direction theta = dot(prob_vector, direction_vector)

def make_direction(theta, dim=10):
    """Create a measurement direction in probability space."""
    d = np.zeros(dim)
    # Use two principal components with angle theta
    d[0] = np.cos(theta)
    d[1] = np.sin(theta)
    return d

def measure_tension(probs, theta):
    """Project probabilities onto direction theta, return sign (+1/-1)."""
    direction = make_direction(theta, dim=probs.shape[1])
    projection = probs @ direction
    # Binarize: above median = +1, below = -1
    median = np.median(projection)
    return np.where(projection >= median, 1, -1)

def correlation_E(probs_A, probs_B, theta_a, theta_b):
    """Compute E(a,b) = <A(a) * B(b)>."""
    meas_A = measure_tension(probs_A, theta_a)
    meas_B = measure_tension(probs_B, theta_b)
    return np.mean(meas_A * meas_B)

# CHSH: S = E(a,b) - E(a,b') + E(a',b) + E(a',b')
# Quantum optimal: a=0, a'=pi/4, b=pi/8, b'=3pi/8
# Classical bound: |S| <= 2
# Quantum bound (Tsirelson): |S| <= 2*sqrt(2) ≈ 2.828

print("=" * 70)
print("CHSH INEQUALITY TEST")
print("=" * 70)
print("Classical bound: |S| <= 2")
print("Quantum bound:   |S| <= 2*sqrt(2) = 2.828")
print()

# Test with quantum-optimal angles
angle_configs = [
    ("Quantum optimal", 0, np.pi/4, np.pi/8, 3*np.pi/8),
    ("Rotated pi/6",    np.pi/6, np.pi/6 + np.pi/4, np.pi/6 + np.pi/8, np.pi/6 + 3*np.pi/8),
    ("Rotated pi/3",    np.pi/3, np.pi/3 + np.pi/4, np.pi/3 + np.pi/8, np.pi/3 + 3*np.pi/8),
    ("Uniform spread",  0, np.pi/3, np.pi/6, np.pi/2),
    ("Tight angles",    0, np.pi/8, np.pi/16, 3*np.pi/16),
    ("Wide angles",     0, np.pi/2, np.pi/4, 3*np.pi/4),
]

print(f"| Config            | E(a,b) | E(a,b') | E(a',b) | E(a',b') | S      | |S|>2? |")
print(f"|-------------------|--------|---------|---------|----------|--------|-------|")

s_values = []
for name, a, a_prime, b, b_prime in angle_configs:
    Eab = correlation_E(prob_A, prob_B, a, b)
    Eab_prime = correlation_E(prob_A, prob_B, a, b_prime)
    Ea_prime_b = correlation_E(prob_A, prob_B, a_prime, b)
    Ea_prime_b_prime = correlation_E(prob_A, prob_B, a_prime, b_prime)

    S = Eab - Eab_prime + Ea_prime_b + Ea_prime_b_prime
    violation = "YES" if abs(S) > 2 else "no"
    s_values.append((name, S))
    print(f"| {name:17s} | {Eab:+.4f} | {Eab_prime:+.4f}  | {Ea_prime_b:+.4f}  | {Ea_prime_b_prime:+.4f}   | {S:+.4f} | {violation:5s} |")

# Sweep angles systematically
print()
print("=" * 70)
print("ANGLE SWEEP: S value across angle configurations")
print("=" * 70)

max_S = 0
max_S_config = (0, 15)
sweep_results = []

for a_deg in range(0, 180, 15):
    for offset in range(15, 90, 15):
        a = np.radians(a_deg)
        a_prime = a + np.radians(offset)
        b = a + np.radians(offset/2)
        b_prime = a + np.radians(3*offset/2)

        Eab = correlation_E(prob_A, prob_B, a, b)
        Eab_prime = correlation_E(prob_A, prob_B, a, b_prime)
        Ea_prime_b = correlation_E(prob_A, prob_B, a_prime, b)
        Ea_prime_b_prime = correlation_E(prob_A, prob_B, a_prime, b_prime)

        S = Eab - Eab_prime + Ea_prime_b + Ea_prime_b_prime
        sweep_results.append((a_deg, offset, S))

        if abs(S) > abs(max_S):
            max_S = S
            max_S_config = (a_deg, offset)

print(f"Max |S| found: {abs(max_S):.4f} at a={max_S_config[0]}deg, offset={max_S_config[1]}deg")
print(f"Classical violation: {'YES' if abs(max_S) > 2 else 'NO'}")
print()

# ASCII Graph: S vs offset angle (for a=0)
print("--- ASCII Graph: |S| vs offset angle (a=0 fixed) ---")
for offset in range(15, 90, 5):
    a = 0
    a_prime = np.radians(offset)
    b = np.radians(offset/2)
    b_prime = np.radians(3*offset/2)

    Eab = correlation_E(prob_A, prob_B, a, b)
    Eab_prime = correlation_E(prob_A, prob_B, a, b_prime)
    Ea_prime_b = correlation_E(prob_A, prob_B, a_prime, b)
    Ea_prime_b_prime = correlation_E(prob_A, prob_B, a_prime, b_prime)
    S = Eab - Eab_prime + Ea_prime_b + Ea_prime_b_prime

    bar_len = int(abs(S) / 3.0 * 40) + 1
    bar_len = min(bar_len, 50)
    violation_mark = " !!!" if abs(S) > 2 else ""
    print(f"  off={offset:2d}deg |{'#' * bar_len}{' ' * (41 - bar_len)}| S={S:+.4f}{violation_mark}")

# Classical bound line
print(f"           {'─' * 27}|S|=2{'─' * 14}")

# Additional: PCA-based measurement directions
print()
print("=" * 70)
print("PCA-BASED MEASUREMENT (using actual data structure)")
print("=" * 70)

from sklearn.decomposition import PCA
pca = PCA(n_components=4)
pca.fit(np.vstack([prob_A, prob_B]))

prob_A_pca = pca.transform(prob_A)
prob_B_pca = pca.transform(prob_B)

def measure_pca(pca_coords, theta):
    """Measure along angle theta in PC1-PC2 plane."""
    projection = pca_coords[:, 0] * np.cos(theta) + pca_coords[:, 1] * np.sin(theta)
    median = np.median(projection)
    return np.where(projection >= median, 1, -1)

def correlation_pca(pca_A, pca_B, theta_a, theta_b):
    meas_A = measure_pca(pca_A, theta_a)
    meas_B = measure_pca(pca_B, theta_b)
    return np.mean(meas_A * meas_B)

print("PCA angle sweep:")
max_S_pca = 0
max_S_pca_config = (0, 15)
for a_deg in range(0, 180, 10):
    for offset in [15, 22.5, 30, 45, 60]:
        a = np.radians(a_deg)
        a_prime = a + np.radians(offset)
        b = a + np.radians(offset/2)
        b_prime = a + np.radians(3*offset/2)

        Eab = correlation_pca(prob_A_pca, prob_B_pca, a, b)
        Eab_prime = correlation_pca(prob_A_pca, prob_B_pca, a, b_prime)
        Ea_prime_b = correlation_pca(prob_A_pca, prob_B_pca, a_prime, b)
        Ea_prime_b_prime = correlation_pca(prob_A_pca, prob_B_pca, a_prime, b_prime)
        S = Eab - Eab_prime + Ea_prime_b + Ea_prime_b_prime

        if abs(S) > abs(max_S_pca):
            max_S_pca = S
            max_S_pca_config = (a_deg, offset)

print(f"  Max |S| (PCA): {abs(max_S_pca):.4f} at a={max_S_pca_config[0]}deg, offset={max_S_pca_config[1]}deg")
print(f"  Classical violation: {'YES' if abs(max_S_pca) > 2 else 'NO'}")

# Summary
print()
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"  Raw tension correlation (r):     {corr_raw:.4f}")
print(f"  Max |S| (direct):                {abs(max_S):.4f}")
print(f"  Max |S| (PCA):                   {abs(max_S_pca):.4f}")
print(f"  Classical bound:                 2.0000")
print(f"  Quantum bound (Tsirelson):       2.8284")
print(f"  Violation (direct):              {'YES' if abs(max_S) > 2 else 'NO'}")
print(f"  Violation (PCA):                 {'YES' if abs(max_S_pca) > 2 else 'NO'}")
print()

if abs(max_S) > 2 or abs(max_S_pca) > 2:
    print("  RESULT: Non-classical correlation detected!")
    print("  The engines trained on non-overlapping data show")
    print("  entanglement-like correlation exceeding classical bounds.")
else:
    print("  RESULT: Correlations remain within classical bounds.")
    print("  No Bell inequality violation detected.")
    print("  This suggests engine correlations are explainable by shared")
    print("  data structure (common digit patterns) rather than entanglement.")

print()
print(f"  Note: r={corr_raw:.4f} correlation still exists with zero shared data,")
print(f"  which is informative even without CHSH violation.")
print(f"  Compare with H-CX-127 (PH entanglement r=0.897).")

print()
print("DONE")
