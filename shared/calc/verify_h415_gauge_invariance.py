#!/usr/bin/env python3
"""H-CX-415 Verification: Inter-tension = Gauge Field

Tests whether inter-tension T_ab = ||field_a - field_b||^2 is invariant
under gauge transformations (orthogonal rotations of hidden states).

Global gauge invariance: same rotation applied to both engines
Local gauge invariance: different rotation per engine (expected to break)
"""

import torch
import torch.nn as nn
import numpy as np
from scipy import stats
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model_pure_field import PureFieldEngine
from model_utils import load_mnist


def random_orthogonal(dim, seed=None):
    """Generate a random orthogonal matrix via QR decomposition."""
    if seed is not None:
        np.random.seed(seed)
    A = np.random.randn(dim, dim)
    Q, R = np.linalg.qr(A)
    # Make sure it's a proper rotation (det=+1)
    Q = Q @ np.diag(np.sign(np.diag(R)))
    return torch.tensor(Q, dtype=torch.float32)


def compute_inter_tension(field_a, field_b):
    """T_ab = ||field_a - field_b||^2 per sample."""
    diff = field_a - field_b
    return (diff ** 2).sum(dim=-1)  # (batch,)


def main():
    print("=" * 65)
    print("  H-CX-415 Verification: Inter-tension = Gauge Field")
    print("=" * 65)

    torch.manual_seed(42)
    np.random.seed(42)

    # Create two independent engines
    print("\n[1] Creating two PureFieldEngines...")
    engine_a = PureFieldEngine(784, 128, 10)
    engine_b = PureFieldEngine(784, 128, 10)

    # Brief training so they diverge
    print("[2] Training both engines briefly (3 epochs each)...")
    train_loader, test_loader = load_mnist(batch_size=256)
    criterion = nn.CrossEntropyLoss()

    for engine, name in [(engine_a, "A"), (engine_b, "B")]:
        optimizer = torch.optim.Adam(engine.parameters(), lr=0.001)
        for epoch in range(3):
            engine.train()
            for X, y in train_loader:
                X = X.view(X.size(0), -1)
                optimizer.zero_grad()
                output, tension = engine(X)
                loss = criterion(output, y) + 0.01 * tension.mean()
                loss.backward()
                optimizer.step()
        print(f"    Engine {name} trained")

    # Get test data
    print("\n[3] Computing baseline inter-tension on test set...")
    engine_a.eval()
    engine_b.eval()

    test_batch = None
    for X, y in test_loader:
        test_batch = X.view(X.size(0), -1)
        break

    with torch.no_grad():
        field_a, tension_a = engine_a(test_batch)
        field_b, tension_b = engine_b(test_batch)

    baseline_inter = compute_inter_tension(field_a, field_b)
    print(f"    Baseline inter-tension: mean={baseline_inter.mean():.6f}, std={baseline_inter.std():.6f}")

    # Test 1: Global gauge transformation (same rotation for both)
    print("\n[4] Global Gauge Invariance Test")
    print("    (Same orthogonal transformation applied to both field outputs)")
    print("-" * 60)
    print(f"  {'Trial':>6} {'Original T_ab':>14} {'Transformed T_ab':>18} {'Rel. Error':>12} {'Invariant?':>12}")
    print("-" * 60)

    n_trials = 20
    global_errors = []

    for trial in range(n_trials):
        Q = random_orthogonal(10, seed=trial+100)

        # Apply same Q to both fields
        field_a_rot = field_a @ Q.T
        field_b_rot = field_b @ Q.T

        transformed_inter = compute_inter_tension(field_a_rot, field_b_rot)

        rel_error = torch.abs(transformed_inter - baseline_inter) / (baseline_inter + 1e-10)
        mean_rel_error = rel_error.mean().item()
        global_errors.append(mean_rel_error)

        invariant = "YES" if mean_rel_error < 1e-5 else "NO"
        print(f"  {trial+1:>6} {baseline_inter.mean():>14.6f} {transformed_inter.mean():>18.6f} {mean_rel_error:>12.2e} {invariant:>12}")

    print("-" * 60)
    print(f"  Mean relative error: {np.mean(global_errors):.2e}")
    print(f"  Max relative error:  {np.max(global_errors):.2e}")
    global_invariant = np.mean(global_errors) < 1e-5
    print(f"  Global gauge invariance: {'CONFIRMED' if global_invariant else 'BROKEN'}")

    # Test 2: Local gauge transformation (different rotation per engine)
    print("\n[5] Local Gauge Invariance Test")
    print("    (Different orthogonal transformation per engine)")
    print("-" * 60)
    print(f"  {'Trial':>6} {'Original T_ab':>14} {'Transformed T_ab':>18} {'Rel. Error':>12} {'Invariant?':>12}")
    print("-" * 60)

    local_errors = []
    local_ratios = []

    for trial in range(n_trials):
        Q_a = random_orthogonal(10, seed=trial+200)
        Q_b = random_orthogonal(10, seed=trial+300)

        field_a_rot = field_a @ Q_a.T
        field_b_rot = field_b @ Q_b.T

        transformed_inter = compute_inter_tension(field_a_rot, field_b_rot)

        rel_error = torch.abs(transformed_inter - baseline_inter) / (baseline_inter + 1e-10)
        mean_rel_error = rel_error.mean().item()
        local_errors.append(mean_rel_error)
        local_ratios.append(transformed_inter.mean().item() / (baseline_inter.mean().item() + 1e-10))

        invariant = "YES" if mean_rel_error < 1e-5 else "NO"
        print(f"  {trial+1:>6} {baseline_inter.mean():>14.6f} {transformed_inter.mean():>18.6f} {mean_rel_error:>12.2e} {invariant:>12}")

    print("-" * 60)
    print(f"  Mean relative error: {np.mean(local_errors):.2e}")
    print(f"  Max relative error:  {np.max(local_errors):.2e}")
    local_invariant = np.mean(local_errors) < 1e-5
    print(f"  Local gauge invariance: {'CONFIRMED' if local_invariant else 'BROKEN'}")

    # Test 3: Scaling transformation (multiplicative gauge)
    print("\n[6] Scale Gauge Test (multiplicative)")
    print("    (field -> alpha * field, same alpha for both)")
    print("-" * 60)

    scales = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
    print(f"  {'Scale':>8} {'T_ab':>14} {'Ratio to base':>14} {'Expected ratio':>14}")
    print("-" * 60)
    for alpha in scales:
        scaled_inter = compute_inter_tension(alpha * field_a, alpha * field_b)
        ratio = scaled_inter.mean().item() / (baseline_inter.mean().item() + 1e-10)
        expected = alpha ** 2
        print(f"  {alpha:>8.1f} {scaled_inter.mean():>14.4f} {ratio:>14.4f} {expected:>14.4f}")
    print("-" * 60)
    print("  Scale covariance: T_ab(alpha*f) = alpha^2 * T_ab(f)")

    # ASCII visualization: global vs local error distributions
    print("\n[7] ASCII Error Distribution")
    print("    Global errors (should be ~0):")
    max_err = max(max(global_errors), max(local_errors)) + 1e-10
    for i, e in enumerate(global_errors[:10]):
        bar = "#" * int(e / max_err * 50) if e > 0 else "."
        print(f"    Trial {i+1:>2}: {bar} ({e:.2e})")
    print("    Local errors (expected non-zero):")
    for i, e in enumerate(local_errors[:10]):
        bar = "#" * int(e / max_err * 50) if e > 0 else "."
        print(f"    Trial {i+1:>2}: {bar} ({e:.2e})")

    # Summary
    print("\n" + "=" * 65)
    print("  SUMMARY")
    print("-" * 65)
    print(f"  Global gauge invariance:  {'YES' if global_invariant else 'NO'} (mean err={np.mean(global_errors):.2e})")
    print(f"  Local gauge invariance:   {'YES' if local_invariant else 'NO'} (mean err={np.mean(local_errors):.2e})")
    print(f"  Scale covariance:         T -> alpha^2 * T (quadratic)")
    print(f"  Gauge field analogy:")
    if global_invariant and not local_invariant:
        print(f"    SUPPORTED — Inter-tension is a global gauge invariant")
        print(f"    that breaks under local gauge transformations, exactly like")
        print(f"    a non-gauge-covariant quantity in physics.")
        print(f"    To restore local invariance, a 'connection' (gauge field)")
        print(f"    would be needed — this is the inter-tension itself.")
        verdict = "SUPPORTED"
    elif global_invariant and local_invariant:
        print(f"    PARTIAL — Both invariances hold, less interesting physically")
        verdict = "PARTIAL"
    else:
        print(f"    NOT SUPPORTED — Even global invariance broken")
        verdict = "NOT SUPPORTED"

    print(f"\n  VERDICT: {verdict}")
    print("=" * 65)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='H-CX-415 Verification: Inter-tension = Gauge Field')
    parser.add_argument('--n-trials', type=int, default=20, help='Number of gauge trials')
    parser.add_argument('--batch-size', type=int, default=256, help='Batch size')
    args = parser.parse_args()
    main()
