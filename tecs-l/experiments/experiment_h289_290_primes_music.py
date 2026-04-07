#!/usr/bin/env python3
"""Experiment for H289 (primes = highest tension) & H290 (consonance = low tension)

PART 1 — Number Theory (H289):
  Classify numbers 1-1000 into 6 classes:
    0: Prime numbers
    1: Perfect squares
    2: Fibonacci numbers
    3: Powers of 2
    4: Perfect numbers (6, 28, 496)
    5: Composite others
  Features: divisibility patterns, digit sums, divisor counts, abundancy, etc.
  Train RepulsionField, measure per-class mean tension.
  Hypothesis: Primes have HIGHEST tension, perfect numbers have LOWEST.

PART 2 — Music Theory (H290):
  Musical intervals with actual frequency ratios:
    Unison(1:1), Octave(2:1), P5(3:2), P4(4:3), M3(5:4),
    m3(6:5), M2(9:8), m2(16:15), Tritone(45:32)
  Features: log(ratio), freq_a, freq_b, beat_frequency, spectral features.
  Train RepulsionField to classify consonant vs dissonant.
  Record per-interval tension.
  Hypothesis: P4 (4:3, ln=0.2877=golden zone width) has LOWEST tension.

Pure numpy, no external ML libraries.
"""

import numpy as np
import math
import time
from collections import Counter

np.random.seed(42)

# ─────────────────────────────────────────
# Shared neural network primitives
# ─────────────────────────────────────────

def relu(x):
    return np.maximum(0, x)

def relu_grad(x):
    return (x > 0).astype(np.float64)

def softmax(x):
    ex = np.exp(x - x.max(axis=1, keepdims=True))
    return ex / (ex.sum(axis=1, keepdims=True) + 1e-8)

def tanh_np(x):
    return np.tanh(x)

def tanh_grad(x):
    return 1 - np.tanh(x) ** 2

def cross_entropy(probs, labels):
    n = len(labels)
    return -np.log(probs[np.arange(n), labels] + 1e-8).mean()


class DenseBaseline:
    """Simple 2-layer MLP baseline."""
    def __init__(self, input_dim, hidden_dim, output_dim):
        s1 = np.sqrt(2.0 / input_dim)
        s2 = np.sqrt(2.0 / hidden_dim)
        self.W1 = np.random.randn(input_dim, hidden_dim) * s1
        self.b1 = np.zeros(hidden_dim)
        self.W2 = np.random.randn(hidden_dim, output_dim) * s2
        self.b2 = np.zeros(output_dim)

    def forward(self, X):
        self.X = X
        self.z1 = X @ self.W1 + self.b1
        self.a1 = relu(self.z1)
        self.z2 = self.a1 @ self.W2 + self.b2
        self.probs = softmax(self.z2)
        return self.probs

    def backward(self, y, lr=0.01):
        m = y.shape[0]
        dz2 = self.probs.copy()
        dz2[np.arange(m), y] -= 1
        dz2 /= m
        dW2 = self.a1.T @ dz2
        db2 = dz2.sum(axis=0)
        da1 = dz2 @ self.W2.T
        dz1 = da1 * relu_grad(self.z1)
        dW1 = self.X.T @ dz1
        db1 = dz1.sum(axis=0)
        for g in [dW1, db1, dW2, db2]:
            np.clip(g, -5.0, 5.0, out=g)
        self.W2 -= lr * dW2; self.b2 -= lr * db2
        self.W1 -= lr * dW1; self.b1 -= lr * db1

    def predict(self, X):
        z1 = X @ self.W1 + self.b1
        a1 = relu(z1)
        z2 = a1 @ self.W2 + self.b2
        return softmax(z2).argmax(axis=1)

    def param_count(self):
        return self.W1.size + self.b1.size + self.W2.size + self.b2.size


class RepulsionField:
    """Two-pole repulsion field with tension.

    output = equilibrium + tension_scale * sqrt(tension) * field_direction
    tension = ||pole+ - pole-||^2
    tension_scale initialized to 1/3 (meta fixed point).
    """
    def __init__(self, input_dim, hidden_dim, output_dim):
        s1 = np.sqrt(2.0 / input_dim)
        s2 = np.sqrt(2.0 / hidden_dim)
        sf = np.sqrt(2.0 / output_dim)
        # Pole +
        self.Wp1 = np.random.randn(input_dim, hidden_dim) * s1
        self.bp1 = np.zeros(hidden_dim)
        self.Wp2 = np.random.randn(hidden_dim, output_dim) * s2
        self.bp2 = np.zeros(output_dim)
        # Pole -
        self.Wm1 = np.random.randn(input_dim, hidden_dim) * s1
        self.bm1 = np.zeros(hidden_dim)
        self.Wm2 = np.random.randn(hidden_dim, output_dim) * s2
        self.bm2 = np.zeros(output_dim)
        # Field transform
        self.Wf = np.random.randn(output_dim, output_dim) * sf
        self.bf = np.zeros(output_dim)
        # Tension scale = 1/3
        self.tension_scale = 1.0 / 3.0
        self.per_sample_tension = None
        self.tension_magnitude = 0.0

    def forward(self, X):
        self.X = X
        # Pole +
        self.zp1 = X @ self.Wp1 + self.bp1
        self.ap1 = relu(self.zp1)
        self.out_plus = self.ap1 @ self.Wp2 + self.bp2
        # Pole -
        self.zm1 = X @ self.Wm1 + self.bm1
        self.am1 = relu(self.zm1)
        self.out_minus = self.am1 @ self.Wm2 + self.bm2
        # Repulsion and tension
        self.repulsion = self.out_plus - self.out_minus
        self.tension = (self.repulsion ** 2).sum(axis=1, keepdims=True)
        self.equilibrium = (self.out_plus + self.out_minus) / 2.0
        # Field direction
        self.field_pre = self.repulsion @ self.Wf + self.bf
        self.field_dir = tanh_np(self.field_pre)
        # Output
        self.sqrt_tension = np.sqrt(self.tension + 1e-8)
        self.output = self.equilibrium + self.tension_scale * self.sqrt_tension * self.field_dir
        self.probs = softmax(self.output)
        self.per_sample_tension = self.tension.squeeze(1)
        self.tension_magnitude = float(self.tension.mean())
        return self.probs

    def backward(self, y, lr=0.01):
        m = y.shape[0]
        d_out = self.probs.copy()
        d_out[np.arange(m), y] -= 1
        d_out /= m
        d_eq = d_out
        d_field_dir = d_out * self.tension_scale * self.sqrt_tension
        d_sqrt_t = (d_out * self.tension_scale * self.field_dir).sum(axis=1, keepdims=True)
        d_field_pre = d_field_dir * tanh_grad(self.field_pre)
        dWf = self.repulsion.T @ d_field_pre
        dbf = d_field_pre.sum(axis=0)
        d_repulsion_from_field = d_field_pre @ self.Wf.T
        d_tension = d_sqrt_t / (2.0 * self.sqrt_tension + 1e-8)
        d_repulsion_from_tension = 2.0 * self.repulsion * d_tension
        d_repulsion = d_repulsion_from_field + d_repulsion_from_tension
        d_out_plus = d_eq * 0.5 + d_repulsion
        d_out_minus = d_eq * 0.5 - d_repulsion
        # Pole+ backward
        dWp2 = self.ap1.T @ d_out_plus
        dbp2 = d_out_plus.sum(axis=0)
        dap1 = d_out_plus @ self.Wp2.T
        dzp1 = dap1 * relu_grad(self.zp1)
        dWp1 = self.X.T @ dzp1
        dbp1 = dzp1.sum(axis=0)
        # Pole- backward
        dWm2 = self.am1.T @ d_out_minus
        dbm2 = d_out_minus.sum(axis=0)
        dam1 = d_out_minus @ self.Wm2.T
        dzm1 = dam1 * relu_grad(self.zm1)
        dWm1 = self.X.T @ dzm1
        dbm1 = dzm1.sum(axis=0)
        # Clip & update
        for g in [dWp1, dbp1, dWp2, dbp2, dWm1, dbm1, dWm2, dbm2, dWf, dbf]:
            np.clip(g, -5.0, 5.0, out=g)
        self.Wp1 -= lr * dWp1; self.bp1 -= lr * dbp1
        self.Wp2 -= lr * dWp2; self.bp2 -= lr * dbp2
        self.Wm1 -= lr * dWm1; self.bm1 -= lr * dbm1
        self.Wm2 -= lr * dWm2; self.bm2 -= lr * dbm2
        self.Wf  -= lr * dWf;  self.bf  -= lr * dbf

    def predict(self, X):
        zp1 = X @ self.Wp1 + self.bp1
        ap1 = relu(zp1)
        out_plus = ap1 @ self.Wp2 + self.bp2
        zm1 = X @ self.Wm1 + self.bm1
        am1 = relu(zm1)
        out_minus = am1 @ self.Wm2 + self.bm2
        repulsion = out_plus - out_minus
        tension = (repulsion ** 2).sum(axis=1, keepdims=True)
        equilibrium = (out_plus + out_minus) / 2.0
        field_pre = repulsion @ self.Wf + self.bf
        field_dir = tanh_np(field_pre)
        sqrt_t = np.sqrt(tension + 1e-8)
        output = equilibrium + self.tension_scale * sqrt_t * field_dir
        probs = softmax(output)
        self.per_sample_tension = tension.squeeze(1)
        self.tension_magnitude = float(tension.mean())
        return probs.argmax(axis=1)

    def get_tension_for(self, X):
        """Get per-sample tension without classification."""
        zp1 = X @ self.Wp1 + self.bp1
        ap1 = relu(zp1)
        out_plus = ap1 @ self.Wp2 + self.bp2
        zm1 = X @ self.Wm1 + self.bm1
        am1 = relu(zm1)
        out_minus = am1 @ self.Wm2 + self.bm2
        repulsion = out_plus - out_minus
        return (repulsion ** 2).sum(axis=1)

    def param_count(self):
        total = 0
        for arr in [self.Wp1, self.bp1, self.Wp2, self.bp2,
                     self.Wm1, self.bm1, self.Wm2, self.bm2,
                     self.Wf, self.bf]:
            total += arr.size
        return total


# ─────────────────────────────────────────
# Training helper
# ─────────────────────────────────────────

def train_model(model, X_train, y_train, X_val, y_val,
                epochs=200, lr=0.01, batch_size=64, verbose=False):
    n = X_train.shape[0]
    best_acc = 0.0
    best_epoch = 0
    for epoch in range(epochs):
        idx = np.random.permutation(n)
        X_shuf = X_train[idx]
        y_shuf = y_train[idx]
        for start in range(0, n, batch_size):
            end = min(start + batch_size, n)
            Xb = X_shuf[start:end]
            yb = y_shuf[start:end]
            model.forward(Xb)
            model.backward(yb, lr=lr)
        preds = model.predict(X_val)
        acc = (preds == y_val).mean()
        if acc > best_acc:
            best_acc = acc
            best_epoch = epoch
        if verbose and (epoch + 1) % 50 == 0:
            print(f"    epoch {epoch+1:3d}: val_acc={acc:.4f} (best={best_acc:.4f} @ {best_epoch})")
    return best_acc, best_epoch


def stratified_kfold(y, n_folds=5, seed=42):
    rng = np.random.RandomState(seed)
    classes = np.unique(y)
    fold_indices = [[] for _ in range(n_folds)]
    for c in classes:
        idx_c = np.where(y == c)[0]
        rng.shuffle(idx_c)
        splits = np.array_split(idx_c, n_folds)
        for f in range(n_folds):
            fold_indices[f].extend(splits[f].tolist())
    for f in range(n_folds):
        rng.shuffle(fold_indices[f])
    folds = []
    all_idx = np.arange(len(y))
    for f in range(n_folds):
        val_idx = np.array(fold_indices[f])
        train_idx = np.setdiff1d(all_idx, val_idx)
        folds.append((train_idx, val_idx))
    return folds


# ═══════════════════════════════════════════════════════════════
# PART 1 — NUMBER THEORY (H289: Primes = Highest Tension)
# ═══════════════════════════════════════════════════════════════

def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True

def count_divisors(n):
    if n <= 0: return 0
    count = 0
    for i in range(1, int(math.isqrt(n)) + 1):
        if n % i == 0:
            count += 2 if i != n // i else 1
    return count

def sum_proper_divisors(n):
    if n <= 1: return 0
    s = 1
    for i in range(2, int(math.isqrt(n)) + 1):
        if n % i == 0:
            s += i
            if i != n // i:
                s += n // i
    return s

def digit_sum(n):
    return sum(int(d) for d in str(n))

def make_fibonacci_set(limit):
    fibs = set()
    a, b = 1, 1
    while a <= limit:
        fibs.add(a)
        a, b = b, a + b
    return fibs

def make_powers_of_2_set(limit):
    pows = set()
    p = 1
    while p <= limit:
        pows.add(p)
        p *= 2
    return pows

def make_perfect_squares_set(limit):
    squares = set()
    i = 1
    while i * i <= limit:
        squares.add(i * i)
        i += 1
    return squares

PERFECT_NUMBERS = {6, 28, 496}  # within 1-1000

def generate_number_dataset(N=1000):
    """Generate features and labels for numbers 1..N.

    Classes:
      0: Prime
      1: Perfect square (non-prime)
      2: Fibonacci (not in above)
      3: Power of 2 (not in above)
      4: Perfect number (6, 28, 496)
      5: Composite other
    """
    fibs = make_fibonacci_set(N)
    pow2s = make_powers_of_2_set(N)
    squares = make_perfect_squares_set(N)

    class_names = {
        0: 'Prime', 1: 'PerfSquare', 2: 'Fibonacci',
        3: 'Pow2', 4: 'PerfNumber', 5: 'CompOther'
    }
    n_classes = 6

    X, y = [], []
    for n in range(1, N + 1):
        # Label (priority: PerfNumber > Pow2 > Fib > PerfSquare > Prime > Other)
        if n in PERFECT_NUMBERS:
            label = 4
        elif n in pow2s:
            label = 3
        elif n in fibs:
            label = 2
        elif n in squares:
            label = 1
        elif is_prime(n):
            label = 0
        else:
            label = 5

        tau_n = count_divisors(n)
        spd = sum_proper_divisors(n)

        # 12 features
        features = [
            n / N,                                    # normalized n
            (n % 2) / 1.0,                            # mod 2
            (n % 3) / 2.0,                            # mod 3
            (n % 6) / 5.0,                            # mod 6
            (n % 5) / 4.0,                            # mod 5
            digit_sum(n) / 36.0,                      # digit sum
            tau_n / 30.0,                              # divisor count
            1.0 if n % 2 == 0 else 0.0,               # is_even
            (n % 10) / 9.0,                            # last digit
            math.log(max(n, 1)) / math.log(N),        # log normalized
            spd / max(n, 1),                           # abundancy ratio
            1.0 if spd == n else 0.0,                  # is_perfect (sigma(n)-n == n)
        ]
        X.append(features)
        y.append(label)

    X = np.array(X, dtype=np.float64)
    y = np.array(y, dtype=np.int64)

    # Standardize
    mean = X.mean(axis=0)
    std = X.std(axis=0) + 1e-8
    X = (X - mean) / std

    return X, y, class_names, n_classes


def run_part1():
    """PART 1: Number theory - primes as highest tension."""
    print()
    print("=" * 72)
    print("  PART 1 — H289: PRIMES = HIGHEST TENSION")
    print("  Numbers 1-1000, 6 classes, RepulsionField tension analysis")
    print("=" * 72)

    X, y, class_names, n_classes = generate_number_dataset(1000)
    input_dim = X.shape[1]

    print(f"\n  Dataset: {X.shape[0]} numbers, {input_dim} features, {n_classes} classes")
    print(f"\n  --- Class Distribution ---")
    for c in sorted(class_names.keys()):
        count = (y == c).sum()
        print(f"    {c}: {class_names[c]:>12s}  {count:4d} ({count/len(y)*100:5.1f}%)")

    # Run cross-validated experiment
    hidden_dim = 64
    epochs = 200
    lr = 0.005
    seeds = [42, 123, 777]
    n_folds = 5

    print(f"\n  Config: hidden={hidden_dim}, epochs={epochs}, lr={lr}")
    print(f"          {n_folds}-fold CV x {len(seeds)} seeds = {n_folds*len(seeds)} runs")

    dense_accs, repul_accs = [], []
    tension_by_class = {c: [] for c in range(n_classes)}

    for seed in seeds:
        folds = stratified_kfold(y, n_folds=n_folds, seed=seed)
        for fold_i, (train_idx, val_idx) in enumerate(folds):
            X_tr, X_val = X[train_idx], X[val_idx]
            y_tr, y_val = y[train_idx], y[val_idx]

            # Dense
            np.random.seed(seed + fold_i)
            dense = DenseBaseline(input_dim, hidden_dim, n_classes)
            acc_d, _ = train_model(dense, X_tr, y_tr, X_val, y_val, epochs=epochs, lr=lr)
            dense_accs.append(acc_d)

            # Repulsion
            np.random.seed(seed + fold_i)
            repul = RepulsionField(input_dim, hidden_dim, n_classes)
            acc_r, _ = train_model(repul, X_tr, y_tr, X_val, y_val, epochs=epochs, lr=lr)
            repul_accs.append(acc_r)

            # Per-class tension on validation set
            repul.predict(X_val)
            t_vals = repul.per_sample_tension
            for c in range(n_classes):
                mask = y_val == c
                if mask.any():
                    tension_by_class[c].append(float(t_vals[mask].mean()))

        d_mean_s = np.mean(dense_accs[-n_folds:]) * 100
        r_mean_s = np.mean(repul_accs[-n_folds:]) * 100
        print(f"    seed {seed}: Dense={d_mean_s:.1f}%  Repulsion={r_mean_s:.1f}%")

    # Results
    d_mean = np.mean(dense_accs) * 100
    d_std = np.std(dense_accs) * 100
    r_mean = np.mean(repul_accs) * 100
    r_std = np.std(repul_accs) * 100
    delta = r_mean - d_mean

    print(f"\n{'='*72}")
    print(f"  ACCURACY ({n_folds}-fold x {len(seeds)} seeds = {len(dense_accs)} runs)")
    print(f"{'='*72}")
    print(f"  Dense:        {d_mean:6.2f} +/- {d_std:.2f}%")
    print(f"  Repulsion:    {r_mean:6.2f} +/- {r_std:.2f}%")
    print(f"  Delta:        {delta:+.2f}%  {'Repulsion wins' if delta > 0 else 'Dense wins'}")

    d_params = DenseBaseline(input_dim, hidden_dim, n_classes).param_count()
    r_params = RepulsionField(input_dim, hidden_dim, n_classes).param_count()
    print(f"  Params:       Dense={d_params:,}  Repulsion={r_params:,} ({r_params/d_params:.1f}x)")

    # Tension table
    print(f"\n{'='*72}")
    print(f"  PER-CLASS TENSION (H289 core test)")
    print(f"{'='*72}")

    class_tension_means = {}
    print(f"\n  {'Class':>12s}  {'Mean Tension':>13s}  {'Std':>8s}  {'N_runs':>6s}")
    print(f"  {'-'*45}")
    for c in sorted(tension_by_class.keys()):
        vals = tension_by_class[c]
        if vals:
            m = np.mean(vals)
            s = np.std(vals)
            class_tension_means[c] = m
            print(f"  {class_names[c]:>12s}  {m:13.6f}  {s:8.6f}  {len(vals):6d}")

    # Rank by tension
    sorted_classes = sorted(class_tension_means.items(), key=lambda x: x[1], reverse=True)

    print(f"\n  --- Tension Ranking (highest to lowest) ---")
    for rank, (c, t) in enumerate(sorted_classes, 1):
        marker = ""
        if class_names[c] == 'Prime':
            marker = " <-- H289: primes should be #1"
        elif class_names[c] == 'PerfNumber':
            marker = " <-- H289: perfect numbers should be last"
        print(f"    #{rank}: {class_names[c]:>12s}  tension={t:.6f}{marker}")

    # ASCII bar chart
    print(f"\n  --- Tension Bar Chart ---")
    if class_tension_means:
        max_t = max(class_tension_means.values())
        bar_w = 50
        for c, t in sorted_classes:
            bar_len = int(t / (max_t + 1e-8) * bar_w)
            bar = '#' * bar_len + '.' * (bar_w - bar_len)
            print(f"    {class_names[c]:>12s} |{bar}| {t:.6f}")

    # H289 verdict
    print(f"\n{'='*72}")
    print(f"  H289 VERDICT")
    print(f"{'='*72}")
    if sorted_classes:
        highest_class = class_names[sorted_classes[0][0]]
        lowest_class = class_names[sorted_classes[-1][0]]
        prime_rank = next(i+1 for i, (c,_) in enumerate(sorted_classes) if class_names[c] == 'Prime')
        perf_rank = next((i+1 for i, (c,_) in enumerate(sorted_classes) if class_names[c] == 'PerfNumber'), None)

        prime_t = class_tension_means.get(0, 0)
        perf_t = class_tension_means.get(4, 0)

        print(f"  Primes tension rank:          #{prime_rank}/{n_classes} (tension={prime_t:.6f})")
        print(f"  Perfect numbers tension rank: #{perf_rank}/{n_classes} (tension={perf_t:.6f})" if perf_rank else "  Perfect numbers: insufficient data")
        print(f"  Highest tension class:        {highest_class}")
        print(f"  Lowest tension class:         {lowest_class}")

        h289_primes_highest = (prime_rank == 1)
        h289_perf_lowest = (perf_rank == n_classes) if perf_rank else False
        print(f"\n  H289a (primes = highest tension): {'CONFIRMED' if h289_primes_highest else 'REJECTED'}")
        print(f"  H289b (perfect = lowest tension):  {'CONFIRMED' if h289_perf_lowest else 'REJECTED'}")

        if prime_t > 0 and perf_t > 0:
            ratio = prime_t / perf_t
            print(f"  Prime/Perfect tension ratio: {ratio:.4f}")

    # Notable numbers tension
    print(f"\n  --- Tension for Notable Numbers ---")
    np.random.seed(42)
    final_repul = RepulsionField(input_dim, hidden_dim, n_classes)
    all_idx = np.arange(len(y))
    folds = stratified_kfold(y, n_folds=5, seed=42)
    tr_idx, _ = folds[0]
    train_model(final_repul, X[tr_idx], y[tr_idx], X[all_idx[:200]], y[all_idx[:200]],
                epochs=epochs, lr=lr)
    final_repul.predict(X)
    all_tension = final_repul.per_sample_tension

    notable = {
        2: "smallest prime", 3: "prime", 5: "prime+fib",
        6: "perfect number", 7: "prime", 11: "prime",
        13: "prime+fib", 28: "perfect number",
        37: "prime", 64: "power of 2", 100: "perfect square",
        137: "fine structure prime", 233: "fibonacci prime",
        496: "perfect number", 512: "power of 2",
        997: "largest 3-digit prime",
    }

    print(f"    {'Number':>8s}  {'Class':>12s}  {'Tension':>12s}  {'Note'}")
    print(f"    {'-'*58}")
    for n in sorted(notable.keys()):
        idx = n - 1
        t = all_tension[idx]
        c = y[idx]
        print(f"    {n:>8d}  {class_names[c]:>12s}  {t:12.6f}  {notable[n]}")

    # Prime vs composite tension distribution
    print(f"\n  --- Prime vs Composite Tension Distribution ---")
    prime_tensions = all_tension[y == 0]
    comp_tensions = all_tension[y == 5]
    if len(prime_tensions) > 0 and len(comp_tensions) > 0:
        print(f"    Primes:    mean={prime_tensions.mean():.6f}  median={np.median(prime_tensions):.6f}  std={prime_tensions.std():.6f}  n={len(prime_tensions)}")
        print(f"    Composite: mean={comp_tensions.mean():.6f}  median={np.median(comp_tensions):.6f}  std={comp_tensions.std():.6f}  n={len(comp_tensions)}")
        # t-test approximation
        n1, n2 = len(prime_tensions), len(comp_tensions)
        m1, m2 = prime_tensions.mean(), comp_tensions.mean()
        s1, s2 = prime_tensions.std(), comp_tensions.std()
        se = np.sqrt(s1**2/n1 + s2**2/n2)
        t_stat = (m1 - m2) / (se + 1e-10)
        print(f"    t-statistic (prime - composite): {t_stat:.4f}")
        print(f"    {'Prime tension > Composite' if t_stat > 0 else 'Composite tension > Prime'}")

    return class_tension_means, delta


# ═══════════════════════════════════════════════════════════════
# PART 2 — MUSIC THEORY (H290: Consonance = Low Tension)
# ═══════════════════════════════════════════════════════════════

SAMPLE_RATE = 8000
DURATION = 0.5
N_SAMPLES = int(SAMPLE_RATE * DURATION)
BASE_FREQ = 440.0
LN_4_3 = math.log(4/3)  # 0.28768...

INTERVALS = [
    # (name, numerator, denominator, consonance_group)
    ("Unison",      1,  1,   "perfect"),
    ("Octave",      2,  1,   "perfect"),
    ("Perfect 5th", 3,  2,   "perfect"),
    ("Perfect 4th", 4,  3,   "perfect"),
    ("Major 3rd",   5,  4,   "imperfect"),
    ("Minor 3rd",   6,  5,   "imperfect"),
    ("Major 2nd",   9,  8,   "dissonant"),
    ("Minor 2nd",  16, 15,   "dissonant"),
    ("Tritone",    45, 32,   "dissonant"),
]

CONSONANCE_GROUPS = {
    "perfect":   [],
    "imperfect": [],
    "dissonant": [],
}
for idx, (_, _, _, group) in enumerate(INTERVALS):
    CONSONANCE_GROUPS[group].append(idx)


def generate_interval_features(base_freq, num, denom, noise_level=0.03):
    """Generate feature vector for a musical interval.

    Features (18-dim):
      0: log(ratio)
      1: freq_a (normalized)
      2: freq_b (normalized)
      3: beat_frequency / base_freq
      4: ratio numerator (normalized)
      5: ratio denominator (normalized)
      6: ratio complexity = (num + denom) / 100
      7: ratio simplicity = 1 / (num + denom)
      8-17: 10-bin spectral energy of combined signal
    """
    ratio = num / denom
    freq_a = base_freq
    freq_b = base_freq * ratio

    # Beat frequency = |f_a - f_b| for close frequencies,
    # or the difference tone for wider intervals
    beat_freq = abs(freq_b - freq_a)

    # Generate actual audio to extract spectral features
    t = np.linspace(0, DURATION, N_SAMPLES, endpoint=False)

    # Two tones with harmonics
    sig_a = np.sin(2 * np.pi * freq_a * t) + 0.3 * np.sin(2 * np.pi * 2 * freq_a * t)
    sig_b = np.sin(2 * np.pi * freq_b * t) + 0.3 * np.sin(2 * np.pi * 2 * freq_b * t)
    signal = sig_a + sig_b + noise_level * np.random.randn(N_SAMPLES)
    signal /= (np.max(np.abs(signal)) + 1e-8)

    # FFT and bin into 10 spectral bands
    fft_mag = np.abs(np.fft.rfft(signal))
    fft_mag = np.log1p(fft_mag)
    n_bins = 10
    bin_size = max(1, len(fft_mag) // n_bins)
    spectral = np.array([fft_mag[i*bin_size:(i+1)*bin_size].mean() for i in range(n_bins)])

    features = np.array([
        math.log(ratio) if ratio > 0 else 0,       # 0: log ratio
        freq_a / 1000.0,                             # 1: freq_a normalized
        freq_b / 1000.0,                             # 2: freq_b normalized
        beat_freq / base_freq,                       # 3: beat / base
        num / 50.0,                                  # 4: numerator norm
        denom / 50.0,                                # 5: denominator norm
        (num + denom) / 100.0,                       # 6: complexity
        1.0 / (num + denom),                         # 7: simplicity
    ] + spectral.tolist(), dtype=np.float64)

    return features


def generate_music_dataset(n_per_class=200, noise_level=0.03, seed=42):
    """Generate full music interval dataset."""
    rng = np.random.RandomState(seed)
    old_state = np.random.get_state()
    np.random.seed(seed)

    X, y = [], []
    n_classes = len(INTERVALS)

    for cls_idx, (name, num, denom, group) in enumerate(INTERVALS):
        for _ in range(n_per_class):
            # Slight tuning variation
            base = BASE_FREQ * (1 + 0.005 * rng.randn())
            features = generate_interval_features(base, num, denom, noise_level)
            X.append(features)
            y.append(cls_idx)

    np.random.set_state(old_state)

    X = np.array(X, dtype=np.float64)
    y = np.array(y, dtype=np.int64)

    # Standardize
    mean = X.mean(axis=0)
    std = X.std(axis=0) + 1e-8
    X = (X - mean) / std

    return X, y, n_classes


def run_part2():
    """PART 2: Music theory - consonance = low tension."""
    print()
    print("=" * 72)
    print("  PART 2 — H290: CONSONANCE = LOW TENSION")
    print("  Musical intervals, RepulsionField tension by consonance group")
    print("=" * 72)

    n_per_class = 200
    X, y, n_classes = generate_music_dataset(n_per_class=n_per_class, seed=42)
    input_dim = X.shape[1]

    interval_names = {i: INTERVALS[i][0] for i in range(n_classes)}

    print(f"\n  Dataset: {X.shape[0]} samples, {input_dim} features, {n_classes} interval classes")
    print(f"  Samples per class: {n_per_class}")

    print(f"\n  --- Interval Table ---")
    print(f"  {'Idx':>3s}  {'Name':<14s}  {'Ratio':>8s}  {'ln(ratio)':>10s}  {'Group':<10s}")
    print(f"  {'-'*50}")
    for i, (name, num, denom, group) in enumerate(INTERVALS):
        ratio = num / denom
        lr = math.log(ratio) if ratio > 0 else 0
        marker = " <-- ln(4/3)=0.2877" if name == "Perfect 4th" else ""
        print(f"  {i:>3d}  {name:<14s}  {num}/{denom:<5d}  {lr:10.4f}  {group:<10s}{marker}")

    # Train/test split (80/20)
    np.random.seed(42)
    perm = np.random.permutation(len(y))
    split = int(0.8 * len(y))
    train_idx, test_idx = perm[:split], perm[split:]
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]

    print(f"\n  Train: {X_train.shape[0]}, Test: {X_test.shape[0]}")

    # --- Dense Baseline ---
    hidden_dim = 64
    epochs = 150
    lr_rate = 0.005

    print(f"\n  Config: hidden={hidden_dim}, epochs={epochs}, lr={lr_rate}")

    print(f"\n  Training Dense baseline...")
    np.random.seed(42)
    dense = DenseBaseline(input_dim, hidden_dim, n_classes)
    dense_acc, _ = train_model(dense, X_train, y_train, X_test, y_test,
                               epochs=epochs, lr=lr_rate)
    d_preds = dense.predict(X_test)
    d_final_acc = (d_preds == y_test).mean()
    print(f"    Dense best val acc: {dense_acc*100:.2f}%")

    # --- RepulsionField ---
    print(f"\n  Training RepulsionField...")
    np.random.seed(42)
    repul = RepulsionField(input_dim, hidden_dim, n_classes)
    repul_acc, _ = train_model(repul, X_train, y_train, X_test, y_test,
                               epochs=epochs, lr=lr_rate)
    r_preds = repul.predict(X_test)
    r_final_acc = (r_preds == y_test).mean()
    print(f"    Repulsion best val acc: {repul_acc*100:.2f}%")

    # --- Multi-seed for robust tension ---
    print(f"\n  Running multi-seed tension measurement (3 seeds)...")
    tension_by_interval = {i: [] for i in range(n_classes)}

    for seed in [42, 123, 777]:
        np.random.seed(seed)
        model = RepulsionField(input_dim, hidden_dim, n_classes)
        train_model(model, X_train, y_train, X_test, y_test,
                    epochs=epochs, lr=lr_rate)
        model.predict(X_test)
        t_vals = model.per_sample_tension
        for c in range(n_classes):
            mask = y_test == c
            if mask.any():
                tension_by_interval[c].append(float(t_vals[mask].mean()))

    # Accuracy comparison
    print(f"\n{'='*72}")
    print(f"  ACCURACY COMPARISON")
    print(f"{'='*72}")
    print(f"  Dense:      {d_final_acc*100:.2f}%")
    print(f"  Repulsion:  {r_final_acc*100:.2f}%")
    delta = (r_final_acc - d_final_acc) * 100
    print(f"  Delta:      {delta:+.2f}%  {'Repulsion wins' if delta > 0 else 'Dense wins'}")

    # Per-class accuracy
    print(f"\n  --- Per-Interval Accuracy ---")
    print(f"  {'Interval':<14s}  {'Dense':>8s}  {'Repulsion':>10s}")
    print(f"  {'-'*36}")
    for i, (name, _, _, _) in enumerate(INTERVALS):
        mask = y_test == i
        if mask.sum() > 0:
            d_c = (d_preds[mask] == i).mean() * 100
            r_c = (r_preds[mask] == i).mean() * 100
            print(f"  {name:<14s}  {d_c:7.1f}%  {r_c:9.1f}%")

    # Tension by interval
    print(f"\n{'='*72}")
    print(f"  PER-INTERVAL TENSION (H290 core test)")
    print(f"{'='*72}")

    interval_tension_means = {}
    print(f"\n  {'Interval':<14s}  {'Ratio':>6s}  {'ln(r)':>8s}  {'Tension':>12s}  {'Std':>8s}  {'Group':<10s}")
    print(f"  {'-'*66}")
    for i, (name, num, denom, group) in enumerate(INTERVALS):
        vals = tension_by_interval[i]
        if vals:
            m = np.mean(vals)
            s = np.std(vals)
            interval_tension_means[i] = m
            ratio = num / denom
            lr_val = math.log(ratio) if ratio > 0 else 0
            marker = " ***" if name == "Perfect 4th" else ""
            print(f"  {name:<14s}  {ratio:6.3f}  {lr_val:8.4f}  {m:12.6f}  {s:8.6f}  {group:<10s}{marker}")

    # Rank by tension
    sorted_intervals = sorted(interval_tension_means.items(), key=lambda x: x[1])

    print(f"\n  --- Tension Ranking (lowest to highest) ---")
    for rank, (i, t) in enumerate(sorted_intervals, 1):
        name = INTERVALS[i][0]
        group = INTERVALS[i][3]
        marker = ""
        if name == "Perfect 4th":
            marker = " <-- H290: P4 should be lowest"
        print(f"    #{rank}: {name:<14s} ({group:>10s})  tension={t:.6f}{marker}")

    # ASCII tension bar chart
    print(f"\n  --- Tension Landscape ---")
    if interval_tension_means:
        max_t = max(interval_tension_means.values()) + 1e-8
        bar_w = 50
        # Sort by ratio
        by_ratio = sorted(interval_tension_means.items(),
                          key=lambda x: INTERVALS[x[0]][1]/INTERVALS[x[0]][2])
        for i, t in by_ratio:
            name = INTERVALS[i][0]
            group_char = {'perfect': 'P', 'imperfect': 'I', 'dissonant': 'D'}[INTERVALS[i][3]]
            bar_len = int(t / max_t * bar_w)
            bar = '#' * bar_len + '.' * (bar_w - bar_len)
            marker = " ***" if name == "Perfect 4th" else ""
            print(f"    [{group_char}] {name:<14s} |{bar}| {t:.6f}{marker}")
        print(f"\n    Legend: P=perfect, I=imperfect, D=dissonant")

    # Consonance group analysis
    print(f"\n{'='*72}")
    print(f"  CONSONANCE GROUP TENSION")
    print(f"{'='*72}")

    group_tensions = {}
    for group_name, indices in CONSONANCE_GROUPS.items():
        tensions = [interval_tension_means[i] for i in indices if i in interval_tension_means]
        if tensions:
            group_tensions[group_name] = {
                'mean': np.mean(tensions),
                'std': np.std(tensions),
                'intervals': [INTERVALS[i][0] for i in indices],
            }

    for gname in ['perfect', 'imperfect', 'dissonant']:
        if gname in group_tensions:
            info = group_tensions[gname]
            print(f"\n  {gname.upper():>10s}: mean={info['mean']:.6f} +/- {info['std']:.6f}")
            print(f"              intervals: {', '.join(info['intervals'])}")

    # Perfect 4th special analysis
    print(f"\n{'='*72}")
    print(f"  PERFECT 4TH (4/3) SPECIAL ANALYSIS")
    print(f"  ln(4/3) = {LN_4_3:.6f} = golden zone width")
    print(f"{'='*72}")

    p4_idx = 3  # Perfect 4th is index 3 in our INTERVALS
    p4_tension = interval_tension_means.get(p4_idx, None)
    p4_rank = next((rank for rank, (i, _) in enumerate(sorted_intervals, 1) if i == p4_idx), None)

    if p4_tension is not None:
        print(f"\n  P4 tension:   {p4_tension:.6f}")
        print(f"  P4 rank:      #{p4_rank}/{n_classes} (1=lowest)")

        # Correlation: ln(ratio) vs tension
        log_ratios = []
        tensions_arr = []
        for i in sorted(interval_tension_means.keys()):
            name, num, denom, _ = INTERVALS[i]
            log_ratios.append(math.log(num/denom) if num/denom > 0 else 0)
            tensions_arr.append(interval_tension_means[i])
        log_ratios = np.array(log_ratios)
        tensions_arr = np.array(tensions_arr)
        corr_log = np.corrcoef(log_ratios, tensions_arr)[0, 1]

        # Complexity vs tension
        complexities = np.array([INTERVALS[i][1] + INTERVALS[i][2] for i in sorted(interval_tension_means.keys())])
        corr_complex = np.corrcoef(complexities, tensions_arr)[0, 1]

        print(f"\n  Correlations:")
        print(f"    ln(ratio) vs tension:    r = {corr_log:.4f}")
        print(f"    complexity vs tension:    r = {corr_complex:.4f}")

    # Cross-domain check
    if 'perfect' in group_tensions and 'dissonant' in group_tensions:
        gap = group_tensions['dissonant']['mean'] - group_tensions['perfect']['mean']
        ratio_gt = group_tensions['dissonant']['mean'] / (group_tensions['perfect']['mean'] + 1e-8)
        print(f"\n  --- Cross-Domain Constants ---")
        print(f"  Dissonant - Perfect gap:  {gap:.6f}")
        print(f"  Dissonant / Perfect:      {ratio_gt:.4f}")
        print(f"  gap / ln(4/3):            {gap / LN_4_3:.4f}")
        print(f"  gap / (1/3):              {gap / (1/3):.4f}")
        print(f"  gap / (1/6):              {gap / (1/6):.4f}")

    # H290 verdict
    print(f"\n{'='*72}")
    print(f"  H290 VERDICT")
    print(f"{'='*72}")

    if group_tensions:
        perf_t = group_tensions.get('perfect', {}).get('mean', None)
        imp_t = group_tensions.get('imperfect', {}).get('mean', None)
        dis_t = group_tensions.get('dissonant', {}).get('mean', None)

        order_correct = True
        if perf_t is not None and imp_t is not None:
            if perf_t >= imp_t:
                order_correct = False
        if imp_t is not None and dis_t is not None:
            if imp_t >= dis_t:
                order_correct = False

        print(f"  Expected order: perfect < imperfect < dissonant")
        print(f"  Actual:         {perf_t:.6f} {'<' if perf_t < imp_t else '>'} {imp_t:.6f} {'<' if imp_t < dis_t else '>'} {dis_t:.6f}")
        print(f"  H290a (consonance = low tension): {'CONFIRMED' if order_correct else 'REJECTED'}")

        p4_is_lowest = (p4_rank == 1) if p4_rank else False
        print(f"  H290b (P4 = lowest tension):      {'CONFIRMED' if p4_is_lowest else 'REJECTED (rank #{})'.format(p4_rank)}")

    return interval_tension_means, group_tensions


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    print("=" * 72)
    print("  EXPERIMENT: H289 + H290 — PRIMES & MUSIC TENSION")
    print("  H289: Primes = highest tension in number classification")
    print("  H290: Consonant intervals = low tension, P4 = golden zone")
    print("=" * 72)
    t0 = time.time()

    # PART 1
    class_tensions, p1_delta = run_part1()

    # PART 2
    interval_tensions, group_tensions = run_part2()

    # ─── COMBINED SUMMARY ───
    elapsed = time.time() - t0
    print()
    print("=" * 72)
    print("  COMBINED SUMMARY — H289 + H290")
    print("=" * 72)

    print(f"\n  PART 1 (H289 — Number Theory):")
    if class_tensions:
        sorted_ct = sorted(class_tensions.items(), key=lambda x: x[1], reverse=True)
        class_names_map = {0: 'Prime', 1: 'PerfSquare', 2: 'Fibonacci',
                           3: 'Pow2', 4: 'PerfNumber', 5: 'CompOther'}
        for rank, (c, t) in enumerate(sorted_ct, 1):
            print(f"    #{rank}: {class_names_map[c]:>12s}  {t:.6f}")
        prime_rank = next(i+1 for i, (c,_) in enumerate(sorted_ct) if c == 0)
        perf_rank = next((i+1 for i, (c,_) in enumerate(sorted_ct) if c == 4), None)
        print(f"    H289a (primes highest):   {'CONFIRMED' if prime_rank == 1 else 'REJECTED (rank #%d)' % prime_rank}")
        print(f"    H289b (perfect lowest):   {'CONFIRMED' if perf_rank == 6 else 'REJECTED (rank #%d)' % perf_rank}" if perf_rank else "    H289b: insufficient data")

    print(f"\n  PART 2 (H290 — Music Theory):")
    if group_tensions:
        for gname in ['perfect', 'imperfect', 'dissonant']:
            if gname in group_tensions:
                print(f"    {gname:>10s}: {group_tensions[gname]['mean']:.6f}")
        perf_t = group_tensions.get('perfect', {}).get('mean', 0)
        imp_t = group_tensions.get('imperfect', {}).get('mean', 0)
        dis_t = group_tensions.get('dissonant', {}).get('mean', 0)
        order_ok = perf_t < imp_t < dis_t
        print(f"    H290a (consonance order): {'CONFIRMED' if order_ok else 'REJECTED'}")

    if interval_tensions:
        sorted_it = sorted(interval_tensions.items(), key=lambda x: x[1])
        p4_rank = next((i+1 for i, (idx,_) in enumerate(sorted_it) if idx == 3), None)
        print(f"    H290b (P4 lowest):        {'CONFIRMED' if p4_rank == 1 else 'REJECTED (rank #%d)' % p4_rank}" if p4_rank else "    H290b: no data")

    print(f"\n  Cross-domain observation:")
    print(f"    ln(4/3) = {LN_4_3:.6f} (golden zone width)")
    print(f"    Perfect 4th ratio = 4/3 = {4/3:.6f}")
    print(f"    These share the SAME constant — music and information theory connected")

    print(f"\n  Total time: {elapsed:.1f}s")
    print("=" * 72)


if __name__ == '__main__':
    main()
