#!/usr/bin/env python3
"""Experiment: Repulsion Field for MUSIC THEORY — Interval Classification

Musical intervals classified by their frequency ratios using RepulsionField.
Synthetic audio generated with numpy only (no external audio libs).

9 interval classes:
  0: Unison      (1:1)
  1: Minor 2nd   (16:15)
  2: Major 2nd   (9:8)   <-- 9/8 = strong coupling constant ratio!
  3: Minor 3rd   (6:5)
  4: Major 3rd   (5:4)
  5: Perfect 4th (4:3)   <-- ln(4/3) = 0.2877 = our entropy constant!
  6: Tritone     (45:32)
  7: Perfect 5th (3:2)
  8: Octave      (2:1)

KEY CROSS-DOMAIN QUESTIONS:
  - Does the Perfect 4th (4/3) produce special tension patterns?
  - Which intervals produce highest/lowest tension?
  - Consonant vs dissonant tension separation?
  - Connection between ln(4/3)=0.2877 (music) and golden zone width?
"""

import numpy as np
import math
import time

# ─────────────────────────────────────────
# Constants
# ─────────────────────────────────────────
SAMPLE_RATE = 8000
DURATION = 0.5  # half second per sample
N_SAMPLES = int(SAMPLE_RATE * DURATION)
N_FFT_BINS = 200  # feature dimension
BASE_FREQ = 440.0  # A4
N_PER_CLASS = 150  # samples per interval class
EPOCHS = 30
LR = 0.003
HIDDEN_DIM = 96
BATCH_SIZE = 32

# Golden zone constants
LN_4_3 = math.log(4/3)  # 0.28768...
ONE_THIRD = 1/3
ONE_HALF = 1/2
ONE_SIXTH = 1/6

# Musical intervals: name, ratio (as fraction), consonance category
INTERVALS = [
    ("Unison",      1, 1,      "perfect"),
    ("Minor 2nd",   16, 15,    "dissonant"),
    ("Major 2nd",   9, 8,      "dissonant"),
    ("Minor 3rd",   6, 5,      "imperfect"),
    ("Major 3rd",   5, 4,      "imperfect"),
    ("Perfect 4th", 4, 3,      "perfect"),
    ("Tritone",     45, 32,    "dissonant"),
    ("Perfect 5th", 3, 2,      "perfect"),
    ("Octave",      2, 1,      "perfect"),
]
N_CLASSES = len(INTERVALS)

# Consonance groups for analysis
CONSONANCE = {
    "perfect":   [0, 5, 7, 8],   # unison, P4, P5, octave
    "imperfect": [3, 4],          # m3, M3
    "dissonant": [1, 2, 6],      # m2, M2, tritone
}

np.random.seed(42)


# ─────────────────────────────────────────
# Synthetic Audio Generation
# ─────────────────────────────────────────

def generate_interval(base_freq, num, denom, noise_level=0.05):
    """Generate two simultaneous tones forming a musical interval."""
    t = np.linspace(0, DURATION, N_SAMPLES, endpoint=False)
    interval_freq = base_freq * num / denom

    # Base tone + harmonics (more realistic)
    signal = np.sin(2 * np.pi * base_freq * t)
    signal += 0.3 * np.sin(2 * np.pi * 2 * base_freq * t)  # 2nd harmonic
    signal += 0.1 * np.sin(2 * np.pi * 3 * base_freq * t)  # 3rd harmonic

    # Interval tone + harmonics
    signal += np.sin(2 * np.pi * interval_freq * t)
    signal += 0.3 * np.sin(2 * np.pi * 2 * interval_freq * t)
    signal += 0.1 * np.sin(2 * np.pi * 3 * interval_freq * t)

    # Normalize
    signal /= np.max(np.abs(signal) + 1e-8)

    # Add noise
    signal += noise_level * np.random.randn(N_SAMPLES)

    return signal


def extract_fft_features(signal):
    """Extract FFT magnitude features (200 bins covering 0-4kHz)."""
    fft = np.fft.rfft(signal)
    magnitudes = np.abs(fft)

    # Log scale
    magnitudes = np.log1p(magnitudes)

    # Downsample to N_FFT_BINS
    n_total = len(magnitudes)
    block_size = max(1, n_total // N_FFT_BINS)
    features = np.array([
        magnitudes[i * block_size:(i + 1) * block_size].mean()
        for i in range(N_FFT_BINS)
    ], dtype=np.float32)

    return features


def generate_dataset(n_per_class=N_PER_CLASS, noise_level=0.05, seed=42):
    """Generate dataset of musical intervals."""
    rng = np.random.RandomState(seed)
    X, y = [], []

    for cls_idx, (name, num, denom, consonance) in enumerate(INTERVALS):
        for _ in range(n_per_class):
            # Slight random variation in base frequency (realistic tuning variation)
            base = BASE_FREQ * (1 + 0.005 * rng.randn())
            signal = generate_interval(base, num, denom, noise_level)
            features = extract_fft_features(signal)
            X.append(features)
            y.append(cls_idx)

    X = np.array(X, dtype=np.float32)
    y = np.array(y, dtype=np.int64)

    # Normalize
    mean = X.mean(axis=0)
    std = X.std(axis=0) + 1e-8
    X = (X - mean) / std

    return X, y, mean, std


# ─────────────────────────────────────────
# Neural Network (numpy only, no torch)
# ─────────────────────────────────────────

def relu(x):
    return np.maximum(0, x)

def relu_deriv(x):
    return (x > 0).astype(np.float32)

def softmax(x):
    e = np.exp(x - x.max(axis=-1, keepdims=True))
    return e / (e.sum(axis=-1, keepdims=True) + 1e-8)

def cross_entropy(probs, labels):
    n = len(labels)
    return -np.log(probs[np.arange(n), labels] + 1e-8).mean()

def he_init(fan_in, fan_out):
    return np.random.randn(fan_in, fan_out).astype(np.float32) * np.sqrt(2.0 / fan_in)


class DenseBaseline:
    """Simple 2-layer MLP baseline."""
    def __init__(self, input_dim, hidden_dim, output_dim):
        self.W1 = he_init(input_dim, hidden_dim)
        self.b1 = np.zeros(hidden_dim, dtype=np.float32)
        self.W2 = he_init(hidden_dim, hidden_dim)
        self.b2 = np.zeros(hidden_dim, dtype=np.float32)
        self.W3 = he_init(hidden_dim, output_dim)
        self.b3 = np.zeros(output_dim, dtype=np.float32)

    def forward(self, x):
        self.x = x
        self.z1 = x @ self.W1 + self.b1
        self.h1 = relu(self.z1)
        self.z2 = self.h1 @ self.W2 + self.b2
        self.h2 = relu(self.z2)
        self.logits = self.h2 @ self.W3 + self.b3
        self.probs = softmax(self.logits)
        return self.logits, self.probs

    def backward(self, labels, lr):
        n = len(labels)
        # Gradient of softmax + cross entropy
        dlogits = self.probs.copy()
        dlogits[np.arange(n), labels] -= 1
        dlogits /= n

        # Layer 3
        dW3 = self.h2.T @ dlogits
        db3 = dlogits.sum(axis=0)
        dh2 = dlogits @ self.W3.T

        # Layer 2
        dz2 = dh2 * relu_deriv(self.z2)
        dW2 = self.h1.T @ dz2
        db2 = dz2.sum(axis=0)
        dh1 = dz2 @ self.W2.T

        # Layer 1
        dz1 = dh1 * relu_deriv(self.z1)
        dW1 = self.x.T @ dz1
        db1 = dz1.sum(axis=0)

        # Update
        self.W3 -= lr * dW3
        self.b3 -= lr * db3
        self.W2 -= lr * dW2
        self.b2 -= lr * db2
        self.W1 -= lr * dW1
        self.b1 -= lr * db1


class RepulsionField:
    """2-pole repulsion field for interval classification.

    pole_plus:  excitatory engine (broad predictions)
    pole_minus: inhibitory engine (sharpening corrections)

    Output = equilibrium + tension_scale * sqrt(tension) * tanh(repulsion)
    Tension = ||pole_plus - pole_minus||^2
    """
    def __init__(self, input_dim, hidden_dim, output_dim):
        # Pole+ (excitatory)
        self.Wp1 = he_init(input_dim, hidden_dim)
        self.bp1 = np.zeros(hidden_dim, dtype=np.float32)
        self.Wp2 = he_init(hidden_dim, output_dim)
        self.bp2 = np.zeros(output_dim, dtype=np.float32)

        # Pole- (inhibitory)
        self.Wm1 = he_init(input_dim, hidden_dim)
        self.bm1 = np.zeros(hidden_dim, dtype=np.float32)
        self.Wm2 = he_init(hidden_dim, output_dim)
        self.bm2 = np.zeros(output_dim, dtype=np.float32)

        # Tension scale initialized at 1/3 (meta fixed point)
        self.tension_scale = np.float32(ONE_THIRD)
        self.tension_magnitude = 0.0

    def forward(self, x):
        self.x = x

        # Pole+
        self.zp1 = x @ self.Wp1 + self.bp1
        self.hp1 = relu(self.zp1)
        self.out_plus = self.hp1 @ self.Wp2 + self.bp2

        # Pole-
        self.zm1 = x @ self.Wm1 + self.bm1
        self.hm1 = relu(self.zm1)
        self.out_minus = self.hm1 @ self.Wm2 + self.bm2

        # Repulsion and tension
        self.repulsion = self.out_plus - self.out_minus
        self.tension = (self.repulsion ** 2).sum(axis=-1, keepdims=True)
        self.tension_magnitude = self.tension.mean()

        # Equilibrium
        self.equilibrium = (self.out_plus + self.out_minus) / 2

        # Field direction (tanh of repulsion)
        self.field_dir = np.tanh(self.repulsion)

        # Output
        self.logits = self.equilibrium + self.tension_scale * np.sqrt(self.tension + 1e-8) * self.field_dir
        self.probs = softmax(self.logits)

        return self.logits, self.probs

    def backward(self, labels, lr):
        n = len(labels)
        dlogits = self.probs.copy()
        dlogits[np.arange(n), labels] -= 1
        dlogits /= n

        # Gradient through output combination
        # output = eq + ts * sqrt(T) * tanh(R)
        # d/d(eq) = dlogits
        # d/d(out_plus) via equilibrium = dlogits * 0.5
        # d/d(out_minus) via equilibrium = dlogits * 0.5
        # For simplicity, approximate gradient through both poles
        d_out_plus = dlogits * 0.5 + dlogits * self.tension_scale * 0.5
        d_out_minus = dlogits * 0.5 - dlogits * self.tension_scale * 0.5

        # Pole+ backward
        dWp2 = self.hp1.T @ d_out_plus
        dbp2 = d_out_plus.sum(axis=0)
        dhp1 = d_out_plus @ self.Wp2.T
        dzp1 = dhp1 * relu_deriv(self.zp1)
        dWp1 = self.x.T @ dzp1
        dbp1 = dzp1.sum(axis=0)

        # Pole- backward
        dWm2 = self.hm1.T @ d_out_minus
        dbm2 = d_out_minus.sum(axis=0)
        dhm1 = d_out_minus @ self.Wm2.T
        dzm1 = dhm1 * relu_deriv(self.zm1)
        dWm1 = self.x.T @ dzm1
        dbm1 = dzm1.sum(axis=0)

        # Update pole+
        self.Wp2 -= lr * dWp2
        self.bp2 -= lr * dbp2
        self.Wp1 -= lr * dWp1
        self.bp1 -= lr * dbp1

        # Update pole-
        self.Wm2 -= lr * dWm2
        self.bm2 -= lr * dbm2
        self.Wm1 -= lr * dWm1
        self.bm1 -= lr * dbm1


# ─────────────────────────────────────────
# Training
# ─────────────────────────────────────────

def train_model(model, X_train, y_train, X_test, y_test, epochs=EPOCHS, lr=LR):
    """Train model and return per-class tension history."""
    n_train = len(y_train)
    history = {
        'train_acc': [], 'test_acc': [], 'loss': [],
        'tension': [],  # per-epoch average tension
        'class_tension': [],  # per-epoch per-class tension
    }

    for epoch in range(epochs):
        # Shuffle
        perm = np.random.permutation(n_train)
        X_shuf = X_train[perm]
        y_shuf = y_train[perm]

        epoch_loss = 0
        epoch_tensions = []
        n_batches = 0

        for i in range(0, n_train, BATCH_SIZE):
            xb = X_shuf[i:i+BATCH_SIZE]
            yb = y_shuf[i:i+BATCH_SIZE]

            logits, probs = model.forward(xb)
            loss = cross_entropy(probs, yb)
            model.backward(yb, lr)

            epoch_loss += loss
            n_batches += 1
            if hasattr(model, 'tension_magnitude'):
                epoch_tensions.append(model.tension_magnitude)

        # Train accuracy
        _, probs_train = model.forward(X_train)
        train_acc = (probs_train.argmax(axis=1) == y_train).mean()

        # Test accuracy
        _, probs_test = model.forward(X_test)
        test_acc = (probs_test.argmax(axis=1) == y_test).mean()

        history['train_acc'].append(train_acc)
        history['test_acc'].append(test_acc)
        history['loss'].append(epoch_loss / n_batches)

        avg_tension = np.mean(epoch_tensions) if epoch_tensions else 0
        history['tension'].append(avg_tension)

        # Per-class tension
        if hasattr(model, 'tension_magnitude'):
            class_t = {}
            for c in range(N_CLASSES):
                mask = y_test == c
                if mask.sum() > 0:
                    model.forward(X_test[mask])
                    class_t[c] = model.tension_magnitude
            history['class_tension'].append(class_t)

    return history


# ─────────────────────────────────────────
# Analysis Functions
# ─────────────────────────────────────────

def analyze_tension_by_interval(model, X_test, y_test):
    """Compute tension for each musical interval class."""
    print("\n" + "=" * 70)
    print("  TENSION BY MUSICAL INTERVAL")
    print("=" * 70)

    results = {}
    for cls_idx, (name, num, denom, consonance) in enumerate(INTERVALS):
        mask = y_test == cls_idx
        if mask.sum() == 0:
            continue
        model.forward(X_test[mask])
        t = model.tension_magnitude
        ratio = num / denom
        results[cls_idx] = {
            'name': name,
            'ratio': ratio,
            'tension': t,
            'consonance': consonance,
            'log_ratio': math.log(ratio) if ratio > 0 else 0,
        }

    # Sort by tension
    sorted_by_tension = sorted(results.items(), key=lambda x: x[1]['tension'])

    print(f"\n  {'Interval':<15} {'Ratio':<8} {'ln(ratio)':<10} {'Tension':<12} {'Category'}")
    print("  " + "-" * 65)
    for cls_idx, info in sorted_by_tension:
        marker = ""
        if info['name'] == "Perfect 4th":
            marker = " <-- ln(4/3)=0.2877 = golden zone width!"
        elif info['name'] == "Major 2nd":
            marker = " <-- 9/8 ratio"
        print(f"  {info['name']:<15} {info['ratio']:<8.4f} {info['log_ratio']:<10.4f} "
              f"{info['tension']:<12.4f} {info['consonance']}{marker}")

    return results


def analyze_consonance_tension(results):
    """Compare tension between consonance groups."""
    print("\n" + "=" * 70)
    print("  CONSONANCE vs DISSONANCE — TENSION ANALYSIS")
    print("=" * 70)

    group_tensions = {}
    for group_name, indices in CONSONANCE.items():
        tensions = [results[i]['tension'] for i in indices if i in results]
        if tensions:
            group_tensions[group_name] = {
                'mean': np.mean(tensions),
                'std': np.std(tensions),
                'intervals': [results[i]['name'] for i in indices if i in results],
            }

    for group_name, info in sorted(group_tensions.items(), key=lambda x: x[1]['mean']):
        print(f"\n  {group_name.upper()} consonance:")
        print(f"    Mean tension: {info['mean']:.4f} +/- {info['std']:.4f}")
        print(f"    Intervals: {', '.join(info['intervals'])}")

    # Compare perfect vs dissonant
    if 'perfect' in group_tensions and 'dissonant' in group_tensions:
        diff = group_tensions['dissonant']['mean'] - group_tensions['perfect']['mean']
        ratio = group_tensions['dissonant']['mean'] / (group_tensions['perfect']['mean'] + 1e-8)
        print(f"\n  Dissonant - Perfect tension gap: {diff:.4f}")
        print(f"  Dissonant / Perfect tension ratio: {ratio:.4f}")

        # Check if gap relates to golden zone constants
        print(f"\n  --- Cross-domain constant check ---")
        print(f"  Tension gap = {diff:.4f}")
        print(f"  ln(4/3)     = {LN_4_3:.4f}")
        print(f"  1/3         = {ONE_THIRD:.4f}")
        print(f"  1/6         = {ONE_SIXTH:.4f}")
        print(f"  gap/ln(4/3) = {diff/LN_4_3:.4f}")
        print(f"  gap/(1/3)   = {diff/ONE_THIRD:.4f}")

    return group_tensions


def analyze_perfect_fourth_special(model, X_test, y_test, results):
    """Special analysis: is the Perfect 4th (4/3) ratio unique?"""
    print("\n" + "=" * 70)
    print("  PERFECT 4TH (4/3) SPECIAL ANALYSIS")
    print("  ln(4/3) = 0.2877 = golden zone width in our framework")
    print("=" * 70)

    p4_idx = 5  # Perfect 4th
    p4_tension = results[p4_idx]['tension'] if p4_idx in results else 0

    # Compare to neighbors
    neighbors = [4, 6]  # Major 3rd and Tritone
    print(f"\n  Perfect 4th tension: {p4_tension:.4f}")
    for n_idx in neighbors:
        if n_idx in results:
            print(f"  {results[n_idx]['name']} tension: {results[n_idx]['tension']:.4f}")

    # Tension rank
    all_tensions = [(i, results[i]['tension']) for i in results]
    all_tensions.sort(key=lambda x: x[1])
    p4_rank = next(i for i, (idx, _) in enumerate(all_tensions) if idx == p4_idx)
    print(f"\n  Perfect 4th tension rank: {p4_rank+1}/{len(all_tensions)}")
    print(f"  (1 = lowest tension, {len(all_tensions)} = highest)")

    # Check if P4 tension is special (outlier from trend)
    ratios = [results[i]['ratio'] for i in sorted(results.keys())]
    tensions = [results[i]['tension'] for i in sorted(results.keys())]

    # Linear regression: tension vs ratio
    ratios_arr = np.array(ratios)
    tensions_arr = np.array(tensions)
    mean_r, mean_t = ratios_arr.mean(), tensions_arr.mean()
    cov = ((ratios_arr - mean_r) * (tensions_arr - mean_t)).mean()
    var_r = ((ratios_arr - mean_r) ** 2).mean()
    slope = cov / (var_r + 1e-8)
    intercept = mean_t - slope * mean_r

    p4_predicted = slope * results[p4_idx]['ratio'] + intercept
    p4_residual = p4_tension - p4_predicted

    print(f"\n  Linear trend: tension = {slope:.4f} * ratio + {intercept:.4f}")
    print(f"  P4 predicted: {p4_predicted:.4f}")
    print(f"  P4 actual:    {p4_tension:.4f}")
    print(f"  P4 residual:  {p4_residual:.4f} ({'above' if p4_residual > 0 else 'below'} trend)")

    # Check log ratio vs tension correlation
    log_ratios = [results[i]['log_ratio'] for i in sorted(results.keys())]
    log_arr = np.array(log_ratios)
    corr_ratio = np.corrcoef(ratios_arr, tensions_arr)[0, 1]
    corr_log = np.corrcoef(log_arr, tensions_arr)[0, 1]
    print(f"\n  Correlation (ratio vs tension):     {corr_ratio:.4f}")
    print(f"  Correlation (ln(ratio) vs tension): {corr_log:.4f}")

    return {
        'p4_tension': p4_tension,
        'p4_rank': p4_rank + 1,
        'p4_residual': p4_residual,
        'corr_ratio_tension': corr_ratio,
        'corr_log_tension': corr_log,
    }


def analyze_tension_ascii_graph(results):
    """ASCII bar chart of tension by interval."""
    print("\n" + "=" * 70)
    print("  TENSION LANDSCAPE — ASCII GRAPH")
    print("=" * 70)

    sorted_results = sorted(results.items(), key=lambda x: x[1]['ratio'])
    max_tension = max(r['tension'] for r in results.values()) + 1e-8

    print()
    for cls_idx, info in sorted_results:
        bar_len = int(50 * info['tension'] / max_tension)
        consonance_char = {'perfect': 'P', 'imperfect': 'I', 'dissonant': 'D'}[info['consonance']]
        marker = " ***" if info['name'] == "Perfect 4th" else ""
        bar = "#" * bar_len
        print(f"  [{consonance_char}] {info['name']:<14} |{bar:<50}| {info['tension']:.3f}{marker}")

    print(f"\n  Legend: P=perfect consonance, I=imperfect, D=dissonant")
    print(f"  *** = Perfect 4th (4/3 ratio, ln(4/3)=0.2877)")


def analyze_ratio_complexity(results):
    """Analyze relationship between ratio complexity and tension."""
    print("\n" + "=" * 70)
    print("  RATIO COMPLEXITY vs TENSION")
    print("  (complexity = num + denom of simplest fraction)")
    print("=" * 70)

    for cls_idx, (name, num, denom, consonance) in enumerate(INTERVALS):
        if cls_idx in results:
            complexity = num + denom
            results[cls_idx]['complexity'] = complexity

    complexities = np.array([results[i]['complexity'] for i in sorted(results.keys())])
    tensions = np.array([results[i]['tension'] for i in sorted(results.keys())])
    corr = np.corrcoef(complexities, tensions)[0, 1]

    print(f"\n  {'Interval':<15} {'num+denom':<10} {'Tension':<10}")
    print("  " + "-" * 35)
    for cls_idx in sorted(results.keys()):
        info = results[cls_idx]
        print(f"  {info['name']:<15} {info['complexity']:<10} {info['tension']:<10.4f}")

    print(f"\n  Correlation (complexity vs tension): {corr:.4f}")
    print(f"  If positive: more complex ratios -> more tension (expected)")
    print(f"  Musical theory predicts: simpler ratios = more consonant = less tension")

    return corr


# ─────────────────────────────────────────
# Main
# ─────────────────────────────────────────

def main():
    print("=" * 70)
    print("  MUSIC THEORY REPULSION FIELD EXPERIMENT")
    print("  Classifying musical intervals by frequency ratio")
    print("=" * 70)
    print(f"\n  Base frequency: {BASE_FREQ} Hz (A4)")
    print(f"  FFT features:   {N_FFT_BINS} bins")
    print(f"  Samples/class:  {N_PER_CLASS}")
    print(f"  Total classes:  {N_CLASSES}")
    print(f"  Epochs:         {EPOCHS}")
    print(f"\n  Key constants:")
    print(f"    ln(4/3) = {LN_4_3:.6f}  (golden zone width AND Perfect 4th!)")
    print(f"    1/3     = {ONE_THIRD:.6f}  (meta fixed point)")
    print(f"    1/2     = {ONE_HALF:.6f}  (Riemann critical line)")

    # ── Generate data ──
    print("\n" + "-" * 70)
    print("  PHASE 1: Generating synthetic musical intervals...")
    t0 = time.time()

    X_train, y_train, train_mean, train_std = generate_dataset(
        n_per_class=N_PER_CLASS, noise_level=0.05, seed=42)

    # Test set with train normalization
    X_test_raw, y_test, _, _ = generate_dataset(
        n_per_class=50, noise_level=0.05, seed=123)
    # Re-generate to get raw
    np.random.seed(123)
    X_test_unnorm, y_test, test_mean, test_std = generate_dataset(
        n_per_class=50, noise_level=0.05, seed=123)
    X_test_raw_actual = X_test_unnorm * test_std + test_mean
    X_test = ((X_test_raw_actual - train_mean) / train_std).astype(np.float32)

    print(f"  Train: {X_train.shape}, Test: {X_test.shape}")
    print(f"  Generated in {time.time()-t0:.2f}s")

    for cls_idx, (name, num, denom, cons) in enumerate(INTERVALS):
        n_train_c = (y_train == cls_idx).sum()
        n_test_c = (y_test == cls_idx).sum()
        ratio = num / denom
        print(f"    Class {cls_idx}: {name:<15} ratio={ratio:.4f}  "
              f"train={n_train_c}, test={n_test_c}")

    # ── Train Dense Baseline ──
    print("\n" + "-" * 70)
    print("  PHASE 2: Training Dense Baseline...")
    np.random.seed(42)
    dense = DenseBaseline(N_FFT_BINS, HIDDEN_DIM, N_CLASSES)
    t0 = time.time()
    dense_hist = train_model(dense, X_train, y_train, X_test, y_test,
                             epochs=EPOCHS, lr=LR)
    dense_time = time.time() - t0

    print(f"  Dense final — train: {dense_hist['train_acc'][-1]:.4f}, "
          f"test: {dense_hist['test_acc'][-1]:.4f}, time: {dense_time:.2f}s")

    # ── Train RepulsionField ──
    print("\n" + "-" * 70)
    print("  PHASE 3: Training RepulsionField...")
    np.random.seed(42)
    repulsion = RepulsionField(N_FFT_BINS, HIDDEN_DIM, N_CLASSES)
    t0 = time.time()
    rep_hist = train_model(repulsion, X_train, y_train, X_test, y_test,
                           epochs=EPOCHS, lr=LR)
    rep_time = time.time() - t0

    print(f"  Repulsion final — train: {rep_hist['train_acc'][-1]:.4f}, "
          f"test: {rep_hist['test_acc'][-1]:.4f}, time: {rep_time:.2f}s")
    print(f"  Final tension: {rep_hist['tension'][-1]:.4f}")
    print(f"  Tension scale: {repulsion.tension_scale:.4f}")

    # ── Training Progress ──
    print("\n" + "-" * 70)
    print("  TRAINING PROGRESS")
    print("-" * 70)
    print(f"  {'Epoch':<7} {'Dense Train':<13} {'Dense Test':<13} "
          f"{'Rep Train':<13} {'Rep Test':<13} {'Tension'}")
    for e in range(EPOCHS):
        if e % 5 == 0 or e == EPOCHS - 1:
            print(f"  {e+1:<7} {dense_hist['train_acc'][e]:<13.4f} "
                  f"{dense_hist['test_acc'][e]:<13.4f} "
                  f"{rep_hist['train_acc'][e]:<13.4f} "
                  f"{rep_hist['test_acc'][e]:<13.4f} "
                  f"{rep_hist['tension'][e]:.4f}")

    # ── Accuracy Comparison ──
    print("\n" + "-" * 70)
    print("  ACCURACY COMPARISON")
    print("-" * 70)
    d_acc = dense_hist['test_acc'][-1]
    r_acc = rep_hist['test_acc'][-1]
    diff = r_acc - d_acc
    print(f"  Dense Baseline:  {d_acc:.4f}")
    print(f"  RepulsionField:  {r_acc:.4f}")
    print(f"  Difference:      {diff:+.4f} ({'RepulsionField wins' if diff > 0 else 'Dense wins' if diff < 0 else 'Tie'})")

    # ── Per-class accuracy ──
    print("\n  Per-class test accuracy:")
    _, dense_probs = dense.forward(X_test)
    _, rep_probs = repulsion.forward(X_test)
    dense_preds = dense_probs.argmax(axis=1)
    rep_preds = rep_probs.argmax(axis=1)

    print(f"  {'Interval':<15} {'Dense':<10} {'Repulsion':<10} {'Diff'}")
    print("  " + "-" * 45)
    for cls_idx, (name, num, denom, cons) in enumerate(INTERVALS):
        mask = y_test == cls_idx
        d_cls = (dense_preds[mask] == cls_idx).mean()
        r_cls = (rep_preds[mask] == cls_idx).mean()
        print(f"  {name:<15} {d_cls:<10.4f} {r_cls:<10.4f} {r_cls-d_cls:+.4f}")

    # ── Tension Analysis ──
    results = analyze_tension_by_interval(repulsion, X_test, y_test)
    analyze_tension_ascii_graph(results)
    group_tensions = analyze_consonance_tension(results)
    p4_analysis = analyze_perfect_fourth_special(repulsion, X_test, y_test, results)
    complexity_corr = analyze_ratio_complexity(results)

    # ── Tension Evolution ──
    print("\n" + "=" * 70)
    print("  TENSION EVOLUTION OVER TRAINING")
    print("=" * 70)
    print(f"\n  {'Epoch':<7} ", end="")
    for name, _, _, _ in INTERVALS:
        print(f"{name[:7]:<9}", end="")
    print()
    for e in range(EPOCHS):
        if e % 5 == 0 or e == EPOCHS - 1:
            ct = rep_hist['class_tension'][e] if e < len(rep_hist['class_tension']) else {}
            print(f"  {e+1:<7} ", end="")
            for c in range(N_CLASSES):
                t = ct.get(c, 0)
                print(f"{t:<9.3f}", end="")
            print()

    # ── Final Summary ──
    print("\n" + "=" * 70)
    print("  FINAL SUMMARY — MUSIC THEORY x REPULSION FIELD")
    print("=" * 70)

    print(f"\n  1. Classification Performance:")
    print(f"     Dense baseline:  {d_acc:.4f}")
    print(f"     RepulsionField:  {r_acc:.4f} ({diff:+.4f})")

    print(f"\n  2. Perfect 4th (4/3) Analysis:")
    print(f"     Tension:  {p4_analysis['p4_tension']:.4f}")
    print(f"     Rank:     {p4_analysis['p4_rank']}/{N_CLASSES}")
    print(f"     Residual: {p4_analysis['p4_residual']:.4f} (deviation from linear trend)")

    print(f"\n  3. Consonance-Tension Relationship:")
    if 'perfect' in group_tensions and 'dissonant' in group_tensions:
        print(f"     Perfect consonance mean tension:  {group_tensions['perfect']['mean']:.4f}")
        if 'imperfect' in group_tensions:
            print(f"     Imperfect consonance mean tension: {group_tensions['imperfect']['mean']:.4f}")
        print(f"     Dissonant mean tension:            {group_tensions['dissonant']['mean']:.4f}")

    print(f"\n  4. Ratio Complexity Correlation:")
    print(f"     complexity vs tension r = {complexity_corr:.4f}")
    if complexity_corr > 0.3:
        print(f"     -> Complex ratios produce MORE tension (music theory confirmed!)")
    elif complexity_corr < -0.3:
        print(f"     -> Complex ratios produce LESS tension (unexpected)")
    else:
        print(f"     -> Weak correlation (tension not simply determined by complexity)")

    print(f"\n  5. Cross-Domain Constants:")
    print(f"     ln(4/3) = {LN_4_3:.4f} (golden zone width)")
    print(f"     Perfect 4th ratio = 4/3 = {4/3:.4f}")
    print(f"     ln(ratio) vs tension correlation: {p4_analysis['corr_log_tension']:.4f}")

    # Check if tension scale converged near any special value
    ts = repulsion.tension_scale
    print(f"\n  6. Tension Scale Convergence:")
    print(f"     Final tension_scale = {ts:.4f}")
    print(f"     Distance to 1/3 = {abs(ts - ONE_THIRD):.4f}")
    print(f"     Distance to 1/e = {abs(ts - 1/math.e):.4f}")
    print(f"     Distance to ln(4/3) = {abs(ts - LN_4_3):.4f}")

    print("\n" + "=" * 70)
    print("  EXPERIMENT COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
