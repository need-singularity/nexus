#!/usr/bin/env python3
"""
H-ROB-11: Silent Consensus = Distributed Robot Agreement
Simulate N robots forming regular polygons WITHOUT communication.
Each robot uses only local sensing (nearest neighbors) + potential-based control.
Measure consensus quality via cosine similarity to ideal formation.
"""

import numpy as np
from collections import defaultdict
import time

np.random.seed(42)

# ─── Parameters ───
N_VALUES = [2, 3, 4, 6, 12]
N_TRIALS = 100
MAX_STEPS = 2000
DT = 0.01
CONVERGENCE_THRESHOLD = 1e-4
SENSING_RADIUS_FACTOR = 3.0  # relative to desired spacing
TARGET_SPACING = 1.0

# Lennard-Jones-like potential parameters
EPSILON = 1.0
SIGMA = TARGET_SPACING  # equilibrium distance


def ideal_polygon(n):
    """Generate vertices of a regular n-gon centered at origin, radius=TARGET_SPACING."""
    if n == 2:
        return np.array([[0, -TARGET_SPACING/2], [0, TARGET_SPACING/2]])
    angles = np.linspace(0, 2*np.pi, n, endpoint=False)
    # radius so that edge length = TARGET_SPACING
    radius = TARGET_SPACING / (2 * np.sin(np.pi / n))
    return np.column_stack([radius * np.cos(angles), radius * np.sin(angles)])


def lj_force(r_vec, sigma=SIGMA, epsilon=EPSILON):
    """Lennard-Jones-like force between two particles. Attractive at long range, repulsive at short."""
    r = np.linalg.norm(r_vec)
    if r < 1e-10:
        return np.array([0.0, 0.0])
    # Modified LJ: F = 24*eps/r * [2*(sigma/r)^12 - (sigma/r)^6] * r_hat
    sr6 = (sigma / r) ** 6
    sr12 = sr6 ** 2
    f_mag = 24 * epsilon / r * (2 * sr12 - sr6)
    return f_mag * (r_vec / r)


def angular_spring_force(pos_i, neighbors, target_angle):
    """Soft angular force encouraging equal angles between neighbors."""
    if len(neighbors) < 2:
        return np.array([0.0, 0.0])
    # Sort neighbors by angle relative to pos_i
    vecs = neighbors - pos_i
    angles = np.arctan2(vecs[:, 1], vecs[:, 0])
    idx = np.argsort(angles)
    # Encourage uniform angular spacing
    force = np.array([0.0, 0.0])
    for k in range(len(idx)):
        k_next = (k + 1) % len(idx)
        diff = angles[idx[k_next]] - angles[idx[k]]
        if diff < 0:
            diff += 2 * np.pi
        error = diff - target_angle
        # Push perpendicular to balance angles
        mid_angle = (angles[idx[k]] + angles[idx[k_next]]) / 2
        perp = np.array([-np.sin(mid_angle), np.cos(mid_angle)])
        force += 0.3 * error * perp
    return force


def simulate_robots(n, use_communication=False):
    """Simulate n robots forming a regular polygon.

    If use_communication=True, robots share global centroid info.
    If False, robots only sense nearest neighbors within radius.
    """
    # Random initial positions in [-3, 3]
    positions = np.random.uniform(-3, 3, (n, 2))
    sensing_radius = SENSING_RADIUS_FACTOR * TARGET_SPACING
    target_angle = 2 * np.pi / n if n > 2 else np.pi

    for step in range(MAX_STEPS):
        forces = np.zeros_like(positions)

        for i in range(n):
            # Find neighbors
            if use_communication:
                # With communication: knows all positions
                neighbors_idx = [j for j in range(n) if j != i]
            else:
                # Without communication: only nearest neighbors within sensing radius
                dists = np.linalg.norm(positions - positions[i], axis=1)
                dists[i] = np.inf
                neighbors_idx = np.where(dists < sensing_radius)[0].tolist()

                # If no neighbors in range, move toward center (simple heuristic)
                if len(neighbors_idx) == 0:
                    forces[i] = -0.1 * positions[i]
                    continue

            # LJ forces from neighbors
            for j in neighbors_idx:
                r_vec = positions[j] - positions[i]
                forces[i] += lj_force(r_vec)

            # Angular spring for polygon shape (if enough neighbors)
            if len(neighbors_idx) >= 2:
                neighbor_pos = positions[neighbors_idx]
                forces[i] += angular_spring_force(positions[i], neighbor_pos, target_angle)

            # Centering force (mild)
            centroid = np.mean(positions, axis=0) if use_communication else np.mean(positions[neighbors_idx], axis=0)
            forces[i] += 0.05 * (centroid - positions[i])

        # Damped dynamics
        damping = max(0.5, 1.0 - step / MAX_STEPS)
        positions += DT * damping * forces

        # Check convergence
        if step > 100:
            all_dists = []
            for i in range(n):
                for j in range(i+1, n):
                    all_dists.append(np.linalg.norm(positions[i] - positions[j]))
            if len(all_dists) > 0:
                std_dists = np.std(all_dists)
                if n == 2 and std_dists < CONVERGENCE_THRESHOLD:
                    return positions, step
                elif std_dists / (np.mean(all_dists) + 1e-10) < CONVERGENCE_THRESHOLD:
                    return positions, step

    return positions, MAX_STEPS


def formation_cosine_similarity(positions, n):
    """Compute cosine similarity between actual formation and ideal regular polygon.

    We compare sorted inter-robot distance vectors.
    Handles rotation/translation/permutation invariance.
    """
    # Center both
    pos = positions - np.mean(positions, axis=0)
    ideal = ideal_polygon(n)
    ideal = ideal - np.mean(ideal, axis=0)

    # Scale actual to match ideal (size-invariant comparison)
    actual_scale = np.max(np.linalg.norm(pos, axis=1))
    ideal_scale = np.max(np.linalg.norm(ideal, axis=1))
    if actual_scale > 1e-10:
        pos = pos * (ideal_scale / actual_scale)

    # Compute pairwise distance matrices
    def pdist(p):
        d = []
        for i in range(len(p)):
            for j in range(i+1, len(p)):
                d.append(np.linalg.norm(p[i] - p[j]))
        return np.sort(d)

    actual_d = pdist(pos)
    ideal_d = pdist(ideal)

    if np.linalg.norm(actual_d) < 1e-10 or np.linalg.norm(ideal_d) < 1e-10:
        return 0.0

    # Cosine similarity of sorted distance vectors
    cos_sim = np.dot(actual_d, ideal_d) / (np.linalg.norm(actual_d) * np.linalg.norm(ideal_d))
    return cos_sim


def run_experiment():
    """Run full experiment for all N values."""
    results = {}

    for n in N_VALUES:
        print(f"\n{'='*60}")
        print(f"  N = {n} robots (target: regular {n}-gon)")
        print(f"{'='*60}")

        # Without communication
        cos_sims_no_comm = []
        conv_times_no_comm = []
        successes_no_comm = 0

        for trial in range(N_TRIALS):
            np.random.seed(trial * 1000 + n)
            pos, steps = simulate_robots(n, use_communication=False)
            cos_sim = formation_cosine_similarity(pos, n)
            cos_sims_no_comm.append(cos_sim)
            conv_times_no_comm.append(steps)
            if cos_sim > 0.95:
                successes_no_comm += 1

        # With communication
        cos_sims_comm = []
        conv_times_comm = []
        successes_comm = 0

        for trial in range(N_TRIALS):
            np.random.seed(trial * 1000 + n)
            pos, steps = simulate_robots(n, use_communication=True)
            cos_sim = formation_cosine_similarity(pos, n)
            cos_sims_comm.append(cos_sim)
            conv_times_comm.append(steps)
            if cos_sim > 0.95:
                successes_comm += 1

        results[n] = {
            'no_comm': {
                'cos_mean': np.mean(cos_sims_no_comm),
                'cos_std': np.std(cos_sims_no_comm),
                'cos_all': cos_sims_no_comm,
                'time_mean': np.mean(conv_times_no_comm),
                'time_std': np.std(conv_times_no_comm),
                'success_rate': successes_no_comm / N_TRIALS,
            },
            'comm': {
                'cos_mean': np.mean(cos_sims_comm),
                'cos_std': np.std(cos_sims_comm),
                'cos_all': cos_sims_comm,
                'time_mean': np.mean(conv_times_comm),
                'time_std': np.std(conv_times_comm),
                'success_rate': successes_comm / N_TRIALS,
            }
        }

        nc = results[n]['no_comm']
        wc = results[n]['comm']
        print(f"  No Comm  — cos: {nc['cos_mean']:.4f} +/- {nc['cos_std']:.4f}  "
              f"time: {nc['time_mean']:.0f}  success: {nc['success_rate']*100:.0f}%")
        print(f"  With Comm — cos: {wc['cos_mean']:.4f} +/- {wc['cos_std']:.4f}  "
              f"time: {wc['time_mean']:.0f}  success: {wc['success_rate']*100:.0f}%")

    return results


def print_ascii_graphs(results):
    """Print ASCII visualizations."""

    print("\n" + "="*70)
    print("  ASCII GRAPH 1: N vs Consensus Quality (cosine similarity)")
    print("="*70)
    print()
    print("  N  | No Comm                              | With Comm")
    print("  ---+----------------------------------------+----------------------------------------")

    for n in N_VALUES:
        nc = results[n]['no_comm']['cos_mean']
        wc = results[n]['comm']['cos_mean']
        bar_nc = '#' * int(nc * 40)
        bar_wc = '#' * int(wc * 40)
        print(f"  {n:>2} | {bar_nc:<40} {nc:.4f} | {bar_wc:<40} {wc:.4f}")

    print()
    print("  " + "-"*30 + " 0.986 target (H-CX-150)")

    print("\n" + "="*70)
    print("  ASCII GRAPH 2: N vs Convergence Time (steps)")
    print("="*70)
    print()

    max_time = max(max(results[n]['no_comm']['time_mean'], results[n]['comm']['time_mean'])
                   for n in N_VALUES)

    print("  N  | No Comm                              | With Comm")
    print("  ---+----------------------------------------+----------------------------------------")

    for n in N_VALUES:
        nc_t = results[n]['no_comm']['time_mean']
        wc_t = results[n]['comm']['time_mean']
        bar_nc = '#' * int(nc_t / max_time * 40)
        bar_wc = '#' * int(wc_t / max_time * 40)
        print(f"  {n:>2} | {bar_nc:<40} {nc_t:>6.0f} | {bar_wc:<40} {wc_t:>6.0f}")

    print("\n" + "="*70)
    print("  ASCII GRAPH 3: Success Rate (cos > 0.95)")
    print("="*70)
    print()
    print("  N  | No Comm                     | With Comm")
    print("  ---+------------------------------+------------------------------")

    for n in N_VALUES:
        nc_s = results[n]['no_comm']['success_rate'] * 100
        wc_s = results[n]['comm']['success_rate'] * 100
        bar_nc = '#' * int(nc_s / 100 * 30)
        bar_wc = '#' * int(wc_s / 100 * 30)
        print(f"  {n:>2} | {bar_nc:<30} {nc_s:>5.1f}% | {bar_wc:<30} {wc_s:>5.1f}%")

    print("\n" + "="*70)
    print("  ASCII GRAPH 4: Communication Benefit (comm cos - no_comm cos)")
    print("="*70)
    print()
    print("  N  | Benefit")
    print("  ---+--------------------------------------------------")

    for n in N_VALUES:
        benefit = results[n]['comm']['cos_mean'] - results[n]['no_comm']['cos_mean']
        bar = '#' * max(1, int(abs(benefit) * 200))
        sign = '+' if benefit >= 0 else '-'
        print(f"  {n:>2} | {sign}{bar:<48} {benefit:+.4f}")


def print_summary_table(results):
    """Print summary table."""
    print("\n" + "="*70)
    print("  SUMMARY TABLE")
    print("="*70)
    print()
    print("  | N  | cos(no comm) | cos(comm) | benefit | time(nc) | time(c) | success(nc) | success(c) |")
    print("  |----|-------------|-----------|---------|----------|---------|-------------|------------|")

    for n in N_VALUES:
        nc = results[n]['no_comm']
        wc = results[n]['comm']
        benefit = wc['cos_mean'] - nc['cos_mean']
        print(f"  | {n:>2} | {nc['cos_mean']:.4f}      | {wc['cos_mean']:.4f}    | {benefit:+.4f} "
              f"| {nc['time_mean']:>7.0f}  | {wc['time_mean']:>6.0f} "
              f"| {nc['success_rate']*100:>10.1f}% | {wc['success_rate']*100:>9.1f}% |")

    # Is N=6 special?
    print("\n" + "="*70)
    print("  N=6 SPECIALNESS TEST")
    print("="*70)

    cos_6 = results[6]['no_comm']['cos_mean']
    other_cos = [results[n]['no_comm']['cos_mean'] for n in N_VALUES if n != 6]
    avg_other = np.mean(other_cos)

    print(f"\n  N=6 consensus (no comm): {cos_6:.4f}")
    print(f"  Other N average:         {avg_other:.4f}")
    print(f"  N=6 advantage:           {cos_6 - avg_other:+.4f}")

    # Does it match 0.986?
    print(f"\n  H-CX-150 target:  0.9860")
    print(f"  N=6 actual:       {cos_6:.4f}")
    print(f"  Difference:       {abs(cos_6 - 0.986):.4f}")

    # Rank by consensus quality
    ranked = sorted(N_VALUES, key=lambda n: results[n]['no_comm']['cos_mean'], reverse=True)
    print(f"\n  Ranking by consensus quality (no comm):")
    for rank, n in enumerate(ranked, 1):
        marker = " <-- HEXAGON" if n == 6 else ""
        print(f"    {rank}. N={n}: {results[n]['no_comm']['cos_mean']:.4f}{marker}")


if __name__ == '__main__':
    t0 = time.time()
    results = run_experiment()
    print_ascii_graphs(results)
    print_summary_table(results)
    elapsed = time.time() - t0
    print(f"\n  Total time: {elapsed:.1f}s")
