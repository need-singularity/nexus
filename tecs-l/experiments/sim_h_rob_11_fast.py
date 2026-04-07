#!/usr/bin/env python3
"""
H-ROB-11: Silent Consensus = Distributed Robot Agreement (Fast version)
Reduced parameters for quick verification: 20 trials, 500 max steps.
"""

import numpy as np
import time

np.random.seed(42)

N_VALUES = [2, 3, 4, 6, 12]
N_TRIALS = 20
MAX_STEPS = 500
DT = 0.02
CONVERGENCE_THRESHOLD = 1e-3
SENSING_RADIUS_FACTOR = 3.0
TARGET_SPACING = 1.0
EPSILON = 1.0
SIGMA = TARGET_SPACING


def ideal_polygon(n):
    if n == 2:
        return np.array([[0, -TARGET_SPACING/2], [0, TARGET_SPACING/2]])
    angles = np.linspace(0, 2*np.pi, n, endpoint=False)
    radius = TARGET_SPACING / (2 * np.sin(np.pi / n))
    return np.column_stack([radius * np.cos(angles), radius * np.sin(angles)])


def lj_force(r_vec, sigma=SIGMA, epsilon=EPSILON):
    r = np.linalg.norm(r_vec)
    if r < 1e-10:
        return np.array([0.0, 0.0])
    sr6 = (sigma / r) ** 6
    sr12 = sr6 ** 2
    f_mag = 24 * epsilon / r * (2 * sr12 - sr6)
    return f_mag * (r_vec / r)


def simulate_robots(n, use_communication=False):
    positions = np.random.uniform(-3, 3, (n, 2))
    sensing_radius = SENSING_RADIUS_FACTOR * TARGET_SPACING
    target_angle = 2 * np.pi / n if n > 2 else np.pi

    for step in range(MAX_STEPS):
        forces = np.zeros_like(positions)
        for i in range(n):
            if use_communication:
                neighbors_idx = [j for j in range(n) if j != i]
            else:
                dists = np.linalg.norm(positions - positions[i], axis=1)
                dists[i] = np.inf
                neighbors_idx = np.where(dists < sensing_radius)[0].tolist()
                if len(neighbors_idx) == 0:
                    forces[i] = -0.1 * positions[i]
                    continue

            for j in neighbors_idx:
                r_vec = positions[j] - positions[i]
                forces[i] += lj_force(r_vec)

            centroid = np.mean(positions, axis=0) if use_communication else np.mean(positions[neighbors_idx], axis=0)
            forces[i] += 0.05 * (centroid - positions[i])

        damping = max(0.5, 1.0 - step / MAX_STEPS)
        positions += DT * damping * forces

        if step > 50:
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
    pos = positions - np.mean(positions, axis=0)
    ideal = ideal_polygon(n)
    ideal = ideal - np.mean(ideal, axis=0)
    actual_scale = np.max(np.linalg.norm(pos, axis=1))
    ideal_scale = np.max(np.linalg.norm(ideal, axis=1))
    if actual_scale > 1e-10:
        pos = pos * (ideal_scale / actual_scale)

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
    return np.dot(actual_d, ideal_d) / (np.linalg.norm(actual_d) * np.linalg.norm(ideal_d))


print("=" * 70)
print("H-ROB-11: Silent Consensus = Distributed Robot Agreement")
print("=" * 70)
print(f"  Trials: {N_TRIALS}, Max steps: {MAX_STEPS}, dt: {DT}")

t0 = time.time()
results = {}

for n in N_VALUES:
    print(f"\n  N = {n} robots...")
    nc_cos, nc_time, nc_succ = [], [], 0
    wc_cos, wc_time, wc_succ = [], [], 0

    for trial in range(N_TRIALS):
        np.random.seed(trial * 1000 + n)
        pos, steps = simulate_robots(n, use_communication=False)
        cs = formation_cosine_similarity(pos, n)
        nc_cos.append(cs)
        nc_time.append(steps)
        if cs > 0.95: nc_succ += 1

        np.random.seed(trial * 1000 + n)
        pos, steps = simulate_robots(n, use_communication=True)
        cs = formation_cosine_similarity(pos, n)
        wc_cos.append(cs)
        wc_time.append(steps)
        if cs > 0.95: wc_succ += 1

    results[n] = {
        'no_comm': {'cos_mean': np.mean(nc_cos), 'cos_std': np.std(nc_cos),
                    'time_mean': np.mean(nc_time), 'success_rate': nc_succ/N_TRIALS},
        'comm': {'cos_mean': np.mean(wc_cos), 'cos_std': np.std(wc_cos),
                 'time_mean': np.mean(wc_time), 'success_rate': wc_succ/N_TRIALS},
    }
    nc = results[n]['no_comm']
    wc = results[n]['comm']
    print(f"    No Comm:   cos={nc['cos_mean']:.4f}+/-{nc['cos_std']:.4f}  time={nc['time_mean']:.0f}  success={nc['success_rate']*100:.0f}%")
    print(f"    With Comm: cos={wc['cos_mean']:.4f}+/-{wc['cos_std']:.4f}  time={wc['time_mean']:.0f}  success={wc['success_rate']*100:.0f}%")

# Summary table
print(f"\n{'='*70}")
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

# ASCII graphs
print(f"\n{'='*70}")
print("  ASCII GRAPH: N vs Consensus Quality (cosine similarity)")
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

print(f"\n{'='*70}")
print("  ASCII GRAPH: Communication Benefit")
print("="*70)
for n in N_VALUES:
    benefit = results[n]['comm']['cos_mean'] - results[n]['no_comm']['cos_mean']
    bar = '#' * max(1, int(abs(benefit) * 200))
    sign = '+' if benefit >= 0 else '-'
    print(f"  {n:>2} | {sign}{bar:<48} {benefit:+.4f}")

# N=6 specialness
print(f"\n{'='*70}")
print("  N=6 SPECIALNESS TEST")
print("="*70)
cos_6 = results[6]['no_comm']['cos_mean']
other_cos = [results[n]['no_comm']['cos_mean'] for n in N_VALUES if n != 6]
avg_other = np.mean(other_cos)
print(f"  N=6 consensus (no comm): {cos_6:.4f}")
print(f"  Other N average:         {avg_other:.4f}")
print(f"  N=6 advantage:           {cos_6 - avg_other:+.4f}")
print(f"  H-CX-150 target:  0.9860")
print(f"  N=6 actual:       {cos_6:.4f}")
print(f"  Difference:       {abs(cos_6 - 0.986):.4f}")

ranked = sorted(N_VALUES, key=lambda n: results[n]['no_comm']['cos_mean'], reverse=True)
print(f"\n  Ranking by consensus quality (no comm):")
for rank, n in enumerate(ranked, 1):
    marker = " <-- HEXAGON" if n == 6 else ""
    print(f"    {rank}. N={n}: {results[n]['no_comm']['cos_mean']:.4f}{marker}")

elapsed = time.time() - t0
print(f"\n  Total time: {elapsed:.1f}s")
