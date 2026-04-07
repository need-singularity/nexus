#!/usr/bin/env python3
"""Experiment: B-C Island Connection
Does collective agreement affect individual identity stability?

Island B = Collective Intelligence (multiple agents agreeing)
Island C = Time/Identity (TemporalContinuityEngine's identity_vector, identity_stability)

Hypothesis: When multiple agents unanimously agree on a prediction,
each agent's identity is MORE stable (higher identity_stability).

Design:
  1. Train 5 TemporalContinuityEngines with different seeds (8 epochs)
  2. For each test sample: all 5 predict independently
  3. Record agreement level (1/5 to 5/5) and consciousness metrics
  4. Analysis: does identity_stability increase with agreement level?
  5. Bonus: do identity vectors become more similar when agents agree?
"""

import torch
import torch.nn.functional as F
import numpy as np
import time
import sys

from model_utils import load_mnist, train_and_evaluate, count_params
from model_temporal_engine import TemporalContinuityEngine, ascii_graph


def set_seed(seed):
    torch.manual_seed(seed)
    np.random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def cosine_similarity_matrix(vectors):
    """Compute pairwise cosine similarity for a list of vectors."""
    n = len(vectors)
    sims = []
    for i in range(n):
        for j in range(i + 1, n):
            v1 = vectors[i]
            v2 = vectors[j]
            norm1 = np.linalg.norm(v1)
            norm2 = np.linalg.norm(v2)
            if norm1 < 1e-10 or norm2 < 1e-10:
                sims.append(0.0)
            else:
                sims.append(np.dot(v1, v2) / (norm1 * norm2))
    return np.mean(sims) if sims else 0.0


def ascii_bar(values, labels, title, width=50, label_width=8):
    """Horizontal bar chart."""
    if not values:
        print(f"  [{title}] (no data)")
        return
    v_max = max(values) if values else 1.0
    v_min = min(values) if values else 0.0

    print(f"\n  {title}")
    print(f"  {'':>{label_width}} {'':>3} |{'':^{width}}|")
    for label, val in zip(labels, values):
        bar_len = int((val - v_min) / (v_max - v_min + 1e-10) * width) if v_max > v_min else width // 2
        bar_len = max(1, bar_len)
        bar = "#" * bar_len
        print(f"  {label:>{label_width}} {val:>7.4f} |{bar:<{width}}|")
    print(f"  {'':>{label_width}} {'':>7} +{'-' * width}+")
    print(f"  {'':>{label_width}} {'':>7}  {v_min:.4f}{' ' * (width - 14)}{v_max:.4f}")


def main():
    print()
    print("=" * 70)
    print("   Experiment: B-C Island Connection")
    print("   Does collective agreement affect individual identity stability?")
    print("=" * 70)

    N_ENGINES = 5
    SEEDS = [42, 137, 256, 314, 512]
    EPOCHS = 8
    INPUT_DIM, HIDDEN_DIM, OUTPUT_DIM = 784, 48, 10
    STATE_DIM = 32

    # ─────────────────────────────────────────
    # Phase 1: Train 5 engines with different seeds
    # ─────────────────────────────────────────
    print(f"\n--- Phase 1: Training {N_ENGINES} TemporalContinuityEngines ---")
    print(f"    Seeds: {SEEDS}, Epochs: {EPOCHS}")

    train_loader, test_loader = load_mnist(batch_size=128)

    engines = []
    for i, seed in enumerate(SEEDS):
        set_seed(seed)
        print(f"\n  [Engine {i}] seed={seed}")
        engine = TemporalContinuityEngine(
            INPUT_DIM, HIDDEN_DIM, OUTPUT_DIM,
            state_dim=STATE_DIM, n_self_ref_steps=3,
            contraction_coeff=0.7, identity_momentum=0.99,
        )
        train_and_evaluate(
            engine, train_loader, test_loader,
            epochs=EPOCHS, aux_lambda=0.01, verbose=True,
        )
        engines.append(engine)
        params = count_params(engine)
        print(f"    Parameters: {params:,}")

    # ─────────────────────────────────────────
    # Phase 2: Collect per-sample predictions and metrics
    # ─────────────────────────────────────────
    print(f"\n--- Phase 2: Collecting per-sample predictions and metrics ---")

    # Reset temporal states before evaluation
    for eng in engines:
        eng.reset_temporal_state()
        eng.eval()

    # We'll process one sample at a time (batch_size=1) for per-sample metrics.
    # But that's slow, so use small batches and expand.
    # Actually, we need per-sample identity vectors and metrics.
    # Process in batches but record per-batch aggregates grouped by agreement.

    # Strategy: process test set batch by batch.
    # For each batch, get predictions from all 5 engines.
    # Compute agreement level per sample.
    # Record per-engine identity_stability for each batch (last step metric).
    # Since identity metrics are tracked cumulatively, we need per-step deltas.

    # Better approach: process samples in small batches, recording the
    # identity_vector and state_change for each engine after each batch.

    # Collect data
    sample_data = []  # list of dicts per batch

    t_start = time.time()
    n_batches = 0

    # Reset again for clean metrics
    for eng in engines:
        eng.reset_temporal_state()

    with torch.no_grad():
        for batch_idx, (X, y) in enumerate(test_loader):
            X_flat = X.view(X.size(0), -1)
            batch_size = X.size(0)

            predictions = []
            identity_vectors = []
            state_changes = []
            identity_changes = []

            for eng in engines:
                # Record pre-forward state
                id_before = eng.identity_vector.clone().cpu().numpy().flatten()

                out, _ = eng(X_flat)
                pred = out.argmax(dim=1).cpu().numpy()
                predictions.append(pred)

                # Identity vector after forward
                id_after = eng.identity_vector.clone().cpu().numpy().flatten()
                identity_vectors.append(id_after)

                # State change from last step
                sc = eng._state_change_history[-1] if eng._state_change_history else 0.0
                ic = eng._identity_change_history[-1] if eng._identity_change_history else 0.0
                state_changes.append(sc)
                identity_changes.append(ic)

            # predictions: (N_ENGINES, batch_size)
            predictions = np.array(predictions)  # (5, batch_size)

            # Per-sample agreement level
            for s in range(batch_size):
                sample_preds = predictions[:, s]  # (5,)
                # Agreement = count of most common prediction / N_ENGINES
                unique, counts = np.unique(sample_preds, return_counts=True)
                max_agree = counts.max()

                sample_data.append({
                    'agreement_count': int(max_agree),
                    'agreement_level': max_agree / N_ENGINES,
                    'correct': int(unique[counts.argmax()] == y[s].item()),
                    'true_label': y[s].item(),
                    'state_changes': list(state_changes),
                    'identity_changes': list(identity_changes),
                    'identity_vectors': [iv.copy() for iv in identity_vectors],
                })

            n_batches += 1
            if n_batches % 20 == 0:
                print(f"    Processed {n_batches} batches ({n_batches * 128} samples)...",
                      flush=True)

    elapsed = time.time() - t_start
    print(f"    Done: {len(sample_data)} samples in {elapsed:.1f}s")

    # ─────────────────────────────────────────
    # Phase 3: Analysis
    # ─────────────────────────────────────────
    print(f"\n--- Phase 3: Analysis ---")

    # Group by agreement level
    agreement_levels = sorted(set(d['agreement_count'] for d in sample_data))

    print(f"\n  Agreement levels found: {agreement_levels}")

    # Table 1: Agreement level distribution
    print(f"\n  ### Table 1: Agreement Level Distribution")
    print(f"  | Agreement | Count  |   %   | Majority Correct |")
    print(f"  |-----------|--------|-------|------------------|")
    for level in agreement_levels:
        group = [d for d in sample_data if d['agreement_count'] == level]
        n = len(group)
        pct = n / len(sample_data) * 100
        correct = sum(d['correct'] for d in group) / n * 100
        print(f"  | {level}/{N_ENGINES}       | {n:>6} | {pct:>5.1f} | {correct:>15.1f}% |")

    # Table 2: Identity stability by agreement level
    # identity_stability = 1 / (1 + mean_identity_change)
    print(f"\n  ### Table 2: Identity Stability by Agreement Level")
    print(f"  | Agreement | Mean ID Change | ID Stability | State Change |")
    print(f"  |-----------|----------------|--------------|--------------|")

    level_stability = {}
    level_state_change = {}
    for level in agreement_levels:
        group = [d for d in sample_data if d['agreement_count'] == level]
        # Average identity change across all engines for this group
        id_changes = [np.mean(d['identity_changes']) for d in group]
        st_changes = [np.mean(d['state_changes']) for d in group]
        mean_ic = np.mean(id_changes)
        mean_sc = np.mean(st_changes)
        stability = 1.0 / (1.0 + mean_ic)
        level_stability[level] = stability
        level_state_change[level] = mean_sc
        print(f"  | {level}/{N_ENGINES}       | {mean_ic:>14.6f} | {stability:>12.6f} | {mean_sc:>12.6f} |")

    # Table 3: Identity vector similarity by agreement level
    print(f"\n  ### Table 3: Identity Vector Cosine Similarity by Agreement Level")
    print(f"  | Agreement | Mean Cosine Sim | Std         |")
    print(f"  |-----------|-----------------|-------------|")

    level_cosine = {}
    for level in agreement_levels:
        group = [d for d in sample_data if d['agreement_count'] == level]
        cosines = [cosine_similarity_matrix(d['identity_vectors']) for d in group]
        mean_cos = np.mean(cosines)
        std_cos = np.std(cosines)
        level_cosine[level] = mean_cos
        print(f"  | {level}/{N_ENGINES}       | {mean_cos:>15.6f} | {std_cos:>11.6f} |")

    # ── ASCII Graphs ──

    # Graph 1: Identity Stability vs Agreement Level
    labels = [f"{l}/{N_ENGINES}" for l in agreement_levels]
    stab_values = [level_stability[l] for l in agreement_levels]
    ascii_bar(stab_values, labels, "Identity Stability by Agreement Level")

    # Graph 2: State Change vs Agreement Level
    sc_values = [level_state_change[l] for l in agreement_levels]
    ascii_bar(sc_values, labels, "State Change Magnitude by Agreement Level")

    # Graph 3: Cosine Similarity vs Agreement Level
    cos_values = [level_cosine[l] for l in agreement_levels]
    ascii_bar(cos_values, labels, "Identity Vector Cosine Similarity by Agreement Level")

    # ── Correlation Analysis ──
    print(f"\n  ### Correlation Analysis")

    # Pearson correlation: agreement_count vs identity_stability (per sample)
    all_agree = np.array([d['agreement_count'] for d in sample_data], dtype=float)
    all_id_change = np.array([np.mean(d['identity_changes']) for d in sample_data])
    all_stability = 1.0 / (1.0 + all_id_change)
    all_state_ch = np.array([np.mean(d['state_changes']) for d in sample_data])
    all_cosine = np.array([cosine_similarity_matrix(d['identity_vectors']) for d in sample_data])

    # Pearson
    if np.std(all_agree) > 1e-10:
        r_stab = np.corrcoef(all_agree, all_stability)[0, 1]
        r_state = np.corrcoef(all_agree, all_state_ch)[0, 1]
        r_cos = np.corrcoef(all_agree, all_cosine)[0, 1]
    else:
        r_stab = r_state = r_cos = 0.0

    print(f"\n  Pearson correlations (agreement_count vs metric):")
    print(f"    agreement vs identity_stability:    r = {r_stab:+.6f}")
    print(f"    agreement vs state_change:          r = {r_state:+.6f}")
    print(f"    agreement vs identity_cosine_sim:   r = {r_cos:+.6f}")

    # Statistical significance (t-test for correlation)
    n_total = len(sample_data)
    for name, r in [("identity_stability", r_stab),
                    ("state_change", r_state),
                    ("identity_cosine_sim", r_cos)]:
        if abs(r) < 1.0 and n_total > 2:
            t_stat = r * np.sqrt((n_total - 2) / (1 - r ** 2 + 1e-15))
            # Approximate p-value from t distribution (two-tailed)
            # Using normal approximation for large n
            from scipy import stats as _st
            p_val = 2 * (1 - _st.t.cdf(abs(t_stat), df=n_total - 2))
            sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else "n.s."
            print(f"    {name:>30}: t={t_stat:+.2f}, p={p_val:.6f} {sig}")

    # ── Monotonicity check ──
    print(f"\n  ### Monotonicity Check")
    stab_sorted = [level_stability[l] for l in agreement_levels]
    is_monotone = all(stab_sorted[i] <= stab_sorted[i + 1]
                      for i in range(len(stab_sorted) - 1))
    is_reverse = all(stab_sorted[i] >= stab_sorted[i + 1]
                     for i in range(len(stab_sorted) - 1))

    if is_monotone:
        print(f"    Identity stability is MONOTONICALLY INCREASING with agreement.")
        print(f"    -> B-C connection CONFIRMED: collective agreement stabilizes identity.")
    elif is_reverse:
        print(f"    Identity stability is MONOTONICALLY DECREASING with agreement.")
        print(f"    -> INVERSE B-C connection: agreement DESTABILIZES identity.")
    else:
        print(f"    Identity stability is NOT monotonic with agreement.")
        trend = "increasing" if r_stab > 0 else "decreasing" if r_stab < 0 else "flat"
        print(f"    -> General trend: {trend} (r={r_stab:+.4f})")

    # ── Per-engine consciousness metrics ──
    print(f"\n  ### Per-Engine Consciousness Metrics (after full evaluation)")
    print(f"  | Engine | Steps | State Change | ID Stability | Smoothness | Tension |")
    print(f"  |--------|-------|--------------|--------------|------------|---------|")
    for i, eng in enumerate(engines):
        m = eng.get_consciousness_metrics()
        print(f"  | {i:>6} | {m['steps']:>5} | {m['state_change_magnitude']:>12.6f} | "
              f"{m['identity_stability']:>12.6f} | {m['transition_smoothness']:>10.4f} | "
              f"{m['avg_tension']:>7.4f} |")

    # ─────────────────────────────────────────
    # Summary
    # ─────────────────────────────────────────
    print(f"\n{'=' * 70}")
    print(f"   SUMMARY: B-C Island Connection Experiment")
    print(f"{'=' * 70}")
    print(f"  Engines trained: {N_ENGINES} (seeds: {SEEDS})")
    print(f"  Test samples:    {len(sample_data)}")
    print(f"  Agreement range: {min(agreement_levels)}/{N_ENGINES} to {max(agreement_levels)}/{N_ENGINES}")
    print()
    print(f"  Key results:")
    print(f"    r(agreement, identity_stability) = {r_stab:+.6f}")
    print(f"    r(agreement, state_change)       = {r_state:+.6f}")
    print(f"    r(agreement, cosine_similarity)  = {r_cos:+.6f}")
    print()

    if r_stab > 0.01:
        print(f"  CONCLUSION: POSITIVE B-C connection detected.")
        print(f"    When agents agree more, individual identity is more stable.")
        print(f"    Collective intelligence (B) stabilizes identity (C).")
    elif r_stab < -0.01:
        print(f"  CONCLUSION: NEGATIVE B-C connection detected.")
        print(f"    When agents agree more, individual identity is LESS stable.")
        print(f"    Collective agreement may homogenize identity.")
    else:
        print(f"  CONCLUSION: No significant B-C connection detected.")
        print(f"    Agreement level does not affect identity stability.")

    if abs(r_cos) > 0.01:
        direction = "more similar" if r_cos > 0 else "more distinct"
        print(f"\n    Identity vectors become {direction} when agents agree (r={r_cos:+.4f}).")

    print(f"\n{'=' * 70}")
    print()


if __name__ == '__main__':
    main()
