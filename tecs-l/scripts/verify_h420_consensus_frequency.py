#!/usr/bin/env python3
"""H-CX-420: Silent Consensus Frequency = 40Hz (Gamma)
Test if consensus oscillation of 6 engines has a dominant frequency related to gamma band.
"""
import numpy as np
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.metrics.pairwise import cosine_similarity
import warnings
warnings.filterwarnings('ignore')

np.random.seed(42)

# Load data
X, y = load_digits(return_X_y=True)
X = X / 16.0
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

print("=" * 70)
print("H-CX-420: Silent Consensus Frequency Experiment")
print("=" * 70)
print(f"Dataset: sklearn digits, Train={len(X_train)}, Test={len(X_test)}")
print()

N_ENGINES = 6
BATCH_SIZE = 32
N_EPOCHS = 15

# Create 6 engines and track consensus during training
engines = []
hidden_sizes = [(64,), (48, 24), (32, 32), (64, 16), (40, 20), (56,)]
for i in range(N_ENGINES):
    clf = MLPClassifier(hidden_layer_sizes=hidden_sizes[i],
                       max_iter=1, warm_start=True,
                       batch_size=BATCH_SIZE,
                       random_state=i*7+1, alpha=0.01,
                       learning_rate_init=0.005)
    engines.append(clf)

# Track consensus over mini-batch iterations
consensus_series = []
accuracy_series = []
batch_count = 0

n_batches_per_epoch = len(X_train) // BATCH_SIZE

print(f"Engines: {N_ENGINES}, Batch size: {BATCH_SIZE}")
print(f"Batches/epoch: {n_batches_per_epoch}, Epochs: {N_EPOCHS}")
print(f"Total iterations: ~{n_batches_per_epoch * N_EPOCHS}")
print()

for epoch in range(N_EPOCHS):
    # Bootstrap sample for each engine (diversity)
    for i, clf in enumerate(engines):
        idx = np.random.choice(len(X_train), size=len(X_train), replace=True)
        clf.fit(X_train[idx], y_train[idx])

    # Measure consensus at multiple points within epoch
    # Simulate sub-epoch measurements by evaluating on random subsets
    for sub in range(n_batches_per_epoch):
        # Random test subset
        sub_idx = np.random.choice(len(X_test), size=min(100, len(X_test)), replace=False)
        X_sub = X_test[sub_idx]

        # Get probability predictions from each engine
        probs = []
        for clf in engines:
            try:
                p = clf.predict_proba(X_sub)
                probs.append(p)
            except:
                pass

        if len(probs) >= 2:
            # Consensus = average pairwise cosine similarity of probability vectors
            flat_probs = [p.flatten() for p in probs]
            cos_sim_matrix = cosine_similarity(flat_probs)
            # Average off-diagonal
            n = len(flat_probs)
            total = 0
            count = 0
            for i in range(n):
                for j in range(i+1, n):
                    total += cos_sim_matrix[i][j]
                    count += 1
            avg_consensus = total / count if count > 0 else 0
            consensus_series.append(avg_consensus)

            # Ensemble accuracy
            all_preds = np.array([clf.predict(X_sub) for clf in engines])
            from scipy import stats
            majority = stats.mode(all_preds, axis=0)[0].flatten()
            acc = np.mean(majority == y[sub_idx])
            accuracy_series.append(acc)

            batch_count += 1

print(f"Collected {len(consensus_series)} consensus measurements")
print()

# Analyze consensus time series
consensus = np.array(consensus_series)
print(f"Consensus stats: mean={consensus.mean():.4f}, std={consensus.std():.4f}")
print(f"  min={consensus.min():.4f}, max={consensus.max():.4f}")
print()

# Detrend: remove moving average
window = 10
if len(consensus) > window:
    trend = np.convolve(consensus, np.ones(window)/window, mode='same')
    detrended = consensus - trend
else:
    detrended = consensus - consensus.mean()

# FFT analysis
fft_vals = np.fft.rfft(detrended)
fft_power = np.abs(fft_vals) ** 2
freqs = np.fft.rfftfreq(len(detrended))

# Skip DC component
fft_power_no_dc = fft_power[1:]
freqs_no_dc = freqs[1:]

# Find dominant frequencies
top_k = 5
top_indices = np.argsort(fft_power_no_dc)[-top_k:][::-1]

print("=" * 70)
print("FFT POWER SPECTRUM — Top 5 Frequencies")
print("=" * 70)
print(f"| Rank | Freq (cycles/sample) | Period (samples) | Power    |")
print(f"|------|---------------------|-----------------|----------|")
for rank, idx in enumerate(top_indices):
    f = freqs_no_dc[idx]
    period = 1/f if f > 0 else float('inf')
    p = fft_power_no_dc[idx]
    print(f"| {rank+1}    | {f:.6f}             | {period:.1f}            | {p:.4f}  |")

# Normalize to "Hz" analog
# If we treat each epoch as 1 second, each batch as dt = 1/n_batches_per_epoch
# Then frequency in Hz = freq_cycles_per_sample * n_batches_per_epoch
print()
print("Normalized frequencies (if 1 epoch = 1 second):")
print(f"  Sampling rate = {n_batches_per_epoch} samples/epoch")
for rank, idx in enumerate(top_indices[:3]):
    f = freqs_no_dc[idx]
    f_hz = f * n_batches_per_epoch
    print(f"  Rank {rank+1}: {f_hz:.2f} Hz/epoch")

# Check relationship to key numbers
print()
print("Key number relationships:")
dominant_period = 1/freqs_no_dc[top_indices[0]] if freqs_no_dc[top_indices[0]] > 0 else 0
print(f"  Dominant period = {dominant_period:.2f} samples")
print(f"  Dominant period / 6 = {dominant_period/6:.2f}")
print(f"  Dominant period / tau(6)=4 = {dominant_period/4:.2f}")
print(f"  Total samples / dominant period = {len(consensus)/dominant_period:.2f}")
print(f"  40 / dominant_freq_hz = {40 / (freqs_no_dc[top_indices[0]] * n_batches_per_epoch):.2f}" if freqs_no_dc[top_indices[0]] > 0 else "  N/A")

# ASCII Graph: Consensus time series
print()
print("--- ASCII Graph: Consensus Over Time ---")
# Downsample for display
n_display = 60
step = max(1, len(consensus) // n_display)
for i in range(0, min(len(consensus), n_display * step), step):
    val = consensus[i]
    bar_len = int((val - consensus.min()) / (consensus.max() - consensus.min() + 1e-9) * 50) + 1
    print(f"  t={i:3d} |{'#' * bar_len}{' ' * (51 - bar_len)}| {val:.4f}")

# ASCII Graph: FFT Power Spectrum
print()
print("--- ASCII Graph: FFT Power Spectrum (top 20 frequencies) ---")
n_show = min(20, len(fft_power_no_dc))
max_pow = max(fft_power_no_dc[:n_show])
for i in range(n_show):
    f = freqs_no_dc[i]
    p = fft_power_no_dc[i]
    bar_len = int(p / (max_pow + 1e-9) * 40) + 1
    marker = " <<<" if i in top_indices[:3] else ""
    print(f"  f={f:.4f} |{'#' * bar_len}{' ' * (41 - bar_len)}| {p:.2f}{marker}")

# Compare consensus at different N
print()
print("=" * 70)
print("CONSENSUS BY N (comparative)")
print("=" * 70)
for n_eng in [2, 3, 4, 6, 8, 10, 12]:
    test_engines = []
    for i in range(n_eng):
        h = hidden_sizes[i % len(hidden_sizes)]
        clf = MLPClassifier(hidden_layer_sizes=h, max_iter=50,
                           random_state=i*7+1, alpha=0.01)
        idx = np.random.choice(len(X_train), size=len(X_train), replace=True)
        clf.fit(X_train[idx], y_train[idx])
        test_engines.append(clf)

    probs = [clf.predict_proba(X_test).flatten() for clf in test_engines]
    cos_mat = cosine_similarity(probs)
    n = len(probs)
    total = sum(cos_mat[i][j] for i in range(n) for j in range(i+1,n))
    count = n*(n-1)//2
    avg_cos = total/count if count > 0 else 0
    print(f"  N={n_eng:2d}: avg consensus(cos)={avg_cos:.4f}")

print()

# Silent consensus check (cos > 0.98)
print("Silent consensus threshold check (cos > 0.98):")
silent_count = np.sum(consensus > 0.98)
print(f"  {silent_count}/{len(consensus)} measurements above 0.98 ({100*silent_count/len(consensus):.1f}%)")
high_count = np.sum(consensus > 0.986)
print(f"  {high_count}/{len(consensus)} measurements above 0.986 ({100*high_count/len(consensus):.1f}%)")

print()
print("DONE")
