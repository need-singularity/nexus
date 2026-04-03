"""telescope_cross_test.py — Cross-validate 3 Rust telescope lenses.

Tests consciousness, topology, causal lenses via telescope_rs.
"""
import sys, os, time
import numpy as np
import telescope_rs


def make_test_data():
    """Create dataset with known patterns for cross-validation."""
    np.random.seed(42)
    n, d = 80, 8
    data = np.random.randn(n, d)
    data[:, 1] = -0.85 * data[:, 0] + np.random.randn(n) * 0.2  # GT1: strong corr
    data[:, 5] = 0.5 * data[:, 4] + np.random.randn(n) * 0.7    # GT2: weak corr
    data[10] = [8] * d                                             # GT3: anomaly
    data[:25, 2] += 3.0; data[:25, 3] += 3.0                     # GT4: clusters
    data[25:55, 6] += 3.0; data[25:55, 7] += 3.0
    data[:, 2] += np.sin(np.linspace(0, 4 * np.pi, n)) * 1.5    # GT5: periodic
    return data


def main():
    print("=" * 60)
    print("  Telescope Cross-Validation (Rust)")
    print("=" * 60)

    data = make_test_data()
    print(f"\nDataset: {data.shape[0]} × {data.shape[1]}")

    # Consciousness
    t0 = time.time()
    c = telescope_rs.consciousness_scan(data, n_cells=64, steps=100)
    tc = time.time() - t0
    print(f"\n  Consciousness: {tc:.3f}s")
    print(f"    Phi={c['phi_iit']:.4f}  clusters={c['n_clusters']}")
    anom = np.asarray(c.get('anomaly_indices', []), dtype=int)
    print(f"    anomalies: {list(anom[:5])}")

    # Topology
    t0 = time.time()
    t = telescope_rs.topology_scan(data)
    tt = time.time() - t0
    print(f"\n  Topology: {tt:.3f}s")
    print(f"    B0={t['betti_0']}  B1={t['betti_1']}  holes={t['n_holes']}")

    # Causal
    t0 = time.time()
    ca = telescope_rs.causal_scan(data)
    tca = time.time() - t0
    print(f"\n  Causal: {tca:.3f}s")
    print(f"    pairs={ca['n_causal_pairs']}  features={ca['n_features']}")

    total = tc + tt + tca
    print(f"\n  TOTAL: {total:.3f}s")
    print("=" * 60)


if __name__ == "__main__":
    main()
