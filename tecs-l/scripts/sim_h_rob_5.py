#!/usr/bin/env python3
"""H-ROB-5: Mitosis = Swarm Fission simulation.
Simulates swarm coverage problem with fission into N sub-groups.
Measures per-robot efficiency and coordination overhead.
"""
import math
import random
import sys

random.seed(42)

# --- Parameters ---
AREA_SIZE = 100.0        # 100x100 area
SENSE_RADIUS = 15.0      # neighbor sensing radius R
STEPS = 500              # simulation steps
ROBOT_SPEED = 1.0        # movement per step
GRID_RES = 20            # coverage grid resolution (20x20 cells)
N_TRIALS = 5             # average over trials
N_VALUES = [1, 2, 3, 4, 5, 6, 8, 10, 12]

def simulate_swarm(n_groups, trial_seed):
    """Simulate swarm coverage with fission into n_groups sub-groups."""
    rng = random.Random(trial_seed)

    # Total robots = n_groups (1 robot per sub-group for fair comparison)
    # Each sub-group is assigned a region
    n_robots = n_groups

    # Assign regions: split area into n_groups vertical strips
    strip_width = AREA_SIZE / n_groups

    # Initialize robots at center of their strip
    robots = []
    for i in range(n_robots):
        cx = strip_width * i + strip_width / 2
        cy = AREA_SIZE / 2
        robots.append([cx, cy])

    # Coverage grid
    cell_size = AREA_SIZE / GRID_RES
    covered = set()

    # Communication overhead counter
    comm_events = 0

    for step in range(STEPS):
        for idx, (rx, ry) in enumerate(robots):
            # Determine assigned strip
            group_id = idx
            strip_lo = strip_width * group_id
            strip_hi = strip_lo + strip_width

            # Random walk biased toward uncovered cells in own strip
            # Simple: move toward nearest uncovered cell center in strip
            best_dist = float('inf')
            best_target = None
            for gi in range(GRID_RES):
                for gj in range(GRID_RES):
                    cx_cell = (gi + 0.5) * cell_size
                    cy_cell = (gj + 0.5) * cell_size
                    if cx_cell < strip_lo or cx_cell >= strip_hi:
                        continue
                    if (gi, gj) in covered:
                        continue
                    d = math.hypot(cx_cell - rx, cy_cell - ry)
                    if d < best_dist:
                        best_dist = d
                        best_target = (cx_cell, cy_cell)

            if best_target is None:
                # All covered in strip, random walk
                angle = rng.uniform(0, 2 * math.pi)
                dx = ROBOT_SPEED * math.cos(angle)
                dy = ROBOT_SPEED * math.sin(angle)
            else:
                dx = best_target[0] - rx
                dy = best_target[1] - ry
                norm = math.hypot(dx, dy)
                if norm > 0:
                    dx = ROBOT_SPEED * dx / norm
                    dy = ROBOT_SPEED * dy / norm

            nx = max(0, min(AREA_SIZE, rx + dx))
            ny = max(0, min(AREA_SIZE, ry + dy))
            robots[idx] = [nx, ny]

            # Mark coverage
            gi = min(int(nx / cell_size), GRID_RES - 1)
            gj = min(int(ny / cell_size), GRID_RES - 1)
            covered.add((gi, gj))

        # Communication: count neighbor pairs within SENSE_RADIUS
        for i in range(n_robots):
            for j in range(i + 1, n_robots):
                d = math.hypot(robots[i][0] - robots[j][0],
                               robots[i][1] - robots[j][1])
                if d < SENSE_RADIUS:
                    comm_events += 1

    total_cells = GRID_RES * GRID_RES
    coverage_ratio = len(covered) / total_cells

    # Coordination overhead = comm_events normalized
    coord_overhead = comm_events / (STEPS * max(1, n_robots * (n_robots - 1) / 2))

    return coverage_ratio, coord_overhead

print("=" * 65)
print("H-ROB-5: Mitosis = Swarm Fission Simulation")
print("=" * 65)
print(f"Area: {AREA_SIZE}x{AREA_SIZE}, Steps: {STEPS}, Sense R: {SENSE_RADIUS}")
print(f"Grid: {GRID_RES}x{GRID_RES} = {GRID_RES**2} cells, Trials: {N_TRIALS}")
print()

results = {}
for n in N_VALUES:
    coverages = []
    overheads = []
    for t in range(N_TRIALS):
        cov, ovh = simulate_swarm(n, trial_seed=42 + t * 100 + n)
        coverages.append(cov)
        overheads.append(ovh)
    avg_cov = sum(coverages) / len(coverages)
    avg_ovh = sum(overheads) / len(overheads)
    # Per-robot efficiency = coverage / N
    efficiency = avg_cov / n
    # Net benefit = coverage - alpha * overhead * N
    alpha = 0.5  # coordination cost weight
    net_benefit = avg_cov - alpha * avg_ovh * n
    results[n] = {
        'coverage': avg_cov,
        'overhead': avg_ovh,
        'efficiency': efficiency,
        'net_benefit': net_benefit,
    }
    print(f"  N={n:2d}: coverage={avg_cov:.4f}  overhead={avg_ovh:.4f}  "
          f"eff/robot={efficiency:.4f}  net_benefit={net_benefit:.4f}")

print()
print("-" * 65)
print("RESULTS TABLE")
print("-" * 65)
print(f"| {'N':>3} | {'Coverage':>9} | {'Overhead':>9} | {'Eff/Robot':>9} | {'Net Benefit':>11} |")
print(f"|{'---':->5}|{'---':->11}|{'---':->11}|{'---':->11}|{'---':->13}|")
for n in N_VALUES:
    r = results[n]
    print(f"| {n:3d} | {r['coverage']:9.4f} | {r['overhead']:9.4f} | {r['efficiency']:9.4f} | {r['net_benefit']:11.4f} |")

# Find optimal N
best_eff_n = max(N_VALUES, key=lambda n: results[n]['efficiency'])
best_net_n = max(N_VALUES, key=lambda n: results[n]['net_benefit'])

print()
print(f"Optimal N (per-robot efficiency): N = {best_eff_n}")
print(f"Optimal N (net benefit):          N = {best_net_n}")
print()

# ASCII Graph 1: N vs Per-robot Efficiency
print("=" * 55)
print("ASCII GRAPH 1: N vs Per-Robot Efficiency")
print("=" * 55)
max_eff = max(results[n]['efficiency'] for n in N_VALUES)
for n in N_VALUES:
    e = results[n]['efficiency']
    bar_len = int(40 * e / max_eff)
    marker = " <<< OPTIMAL" if n == best_eff_n else ""
    print(f"  N={n:2d} |{'#' * bar_len:<40}| {e:.4f}{marker}")

print()

# ASCII Graph 2: N vs Coordination Overhead
print("=" * 55)
print("ASCII GRAPH 2: N vs Coordination Overhead")
print("=" * 55)
max_ovh = max(results[n]['overhead'] for n in N_VALUES) or 1
for n in N_VALUES:
    o = results[n]['overhead']
    bar_len = int(40 * o / max_ovh) if max_ovh > 0 else 0
    print(f"  N={n:2d} |{'#' * bar_len:<40}| {o:.4f}")

print()

# ASCII Graph 3: N vs Net Benefit
print("=" * 55)
print("ASCII GRAPH 3: N vs Net Benefit")
print("=" * 55)
min_nb = min(results[n]['net_benefit'] for n in N_VALUES)
max_nb = max(results[n]['net_benefit'] for n in N_VALUES)
rng_nb = max_nb - min_nb if max_nb != min_nb else 1
for n in N_VALUES:
    nb = results[n]['net_benefit']
    bar_len = int(40 * (nb - min_nb) / rng_nb)
    marker = " <<< OPTIMAL" if n == best_net_n else ""
    print(f"  N={n:2d} |{'#' * bar_len:<40}| {nb:.4f}{marker}")

print()
print("=" * 55)
print("PREDICTION CHECK: Does N=2 maximize per-robot efficiency?")
print(f"  Best N = {best_eff_n} (predicted: 2)")
print(f"  Match H297 Mitosis prediction: {'YES' if best_eff_n == 2 else 'NO (N=' + str(best_eff_n) + ')'}")
print(f"  sigma_-1(6) = 2 prediction:    {'CONFIRMED' if best_eff_n == 2 else 'NOT CONFIRMED'}")
print()
print(f"NET BENEFIT CHECK: Does N=2 maximize net benefit?")
print(f"  Best N = {best_net_n}")
print(f"  Match: {'YES' if best_net_n == 2 else 'NO (N=' + str(best_net_n) + ')'}")
print("=" * 55)
