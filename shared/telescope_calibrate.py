"""telescope_calibrate.py — Cross-calibration for Rust telescope lenses.

Runs 3 Rust lenses, compares findings, reports consensus.
"""
import sys, os, time
import numpy as np
import telescope_rs


def make_calibration_data():
    np.random.seed(42)
    n, d = 100, 10
    data = np.random.randn(n, d)
    data[:, 1] = -0.9 * data[:, 0] + np.random.randn(n) * 0.1
    data[50] = [10] * d
    data[:30, 3] += 4.0
    return data


def main():
    print("=" * 60)
    print("  Telescope Cross-Calibration (Rust)")
    print("=" * 60)

    data = make_calibration_data()

    c = telescope_rs.consciousness_scan(data, n_cells=64, steps=100)
    t = telescope_rs.topology_scan(data)
    ca = telescope_rs.causal_scan(data)

    print(f"\n  Consciousness: Phi={c['phi_iit']:.4f}")
    print(f"  Topology:      B0={t['betti_0']} B1={t['betti_1']}")
    print(f"  Causal:        pairs={ca['n_causal_pairs']}")

    # Consensus: non-trivial structure?
    has_structure = c['phi_iit'] > 0.5
    has_topology = t['betti_1'] > 0
    has_causality = ca['n_causal_pairs'] > 0

    n_agree = sum([has_structure, has_topology, has_causality])
    print(f"\n  Consensus: {n_agree}/3 lenses detect non-trivial structure")
    if n_agree >= 2:
        print("  → HIGH CONFIDENCE: real hidden structure")
    elif n_agree == 1:
        print("  → MODERATE: single lens detection")
    else:
        print("  → LOW: no significant structure")

    print("=" * 60)


if __name__ == "__main__":
    main()
