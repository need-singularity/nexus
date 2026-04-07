#!/usr/bin/env python3
"""H-ROB-6: Inter-tension = Collision Avoidance simulation.
Two robots navigate toward goals; inter-tension triggers avoidance.
Compares tension-based vs no-avoidance vs artificial potential field.
"""
import math
import random

random.seed(42)

# --- Parameters ---
ARENA = 50.0
STEPS = 300
SPEED = 0.5
N_SCENARIOS = 50     # random goal pairs
THRESHOLD_SCAN = [0.01, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35,
                  0.40, 0.45, 0.50, 0.60, 0.80, 1.00]
COLLISION_DIST = 2.0  # collision if distance < this
DODGE_STRENGTH = 2.0

def generate_scenario(rng):
    """Generate start/goal for 2 robots that cross paths."""
    # Robot A: left side -> right side
    ax, ay = rng.uniform(0, 10), rng.uniform(15, 35)
    agx, agy = rng.uniform(40, 50), rng.uniform(15, 35)
    # Robot B: top -> bottom (crosses A's path)
    bx, by = rng.uniform(15, 35), rng.uniform(40, 50)
    bgx, bgy = rng.uniform(15, 35), rng.uniform(0, 10)
    return (ax, ay, agx, agy), (bx, by, bgx, bgy)

def move_toward(x, y, gx, gy, speed):
    dx, dy = gx - x, gy - y
    d = math.hypot(dx, dy)
    if d < speed:
        return gx, gy
    return x + speed * dx / d, y + speed * dy / d

def inter_tension(ax, ay, bx, by):
    """T_ab = 1/distance^2"""
    d = math.hypot(ax - bx, ay - by)
    if d < 0.1:
        d = 0.1
    return 1.0 / (d * d)

def simulate_no_avoidance(scA, scB):
    ax, ay, agx, agy = scA
    bx, by, bgx, bgy = scB
    collisions = 0
    total_dist_a = 0
    total_dist_b = 0
    for _ in range(STEPS):
        nax, nay = move_toward(ax, ay, agx, agy, SPEED)
        nbx, nby = move_toward(bx, by, bgx, bgy, SPEED)
        total_dist_a += math.hypot(nax - ax, nay - ay)
        total_dist_b += math.hypot(nbx - bx, nby - by)
        ax, ay = nax, nay
        bx, by = nbx, nby
        if math.hypot(ax - bx, ay - by) < COLLISION_DIST:
            collisions += 1
    reached_a = math.hypot(ax - agx, ay - agy) < 2.0
    reached_b = math.hypot(bx - bgx, by - bgy) < 2.0
    return collisions, total_dist_a + total_dist_b, reached_a and reached_b

def simulate_tension_avoidance(scA, scB, threshold):
    ax, ay, agx, agy = scA
    bx, by, bgx, bgy = scB
    collisions = 0
    total_dist_a = 0
    total_dist_b = 0
    avoidance_count = 0
    for _ in range(STEPS):
        T = inter_tension(ax, ay, bx, by)
        if T > threshold:
            avoidance_count += 1
            # Perpendicular dodge
            dx = bx - ax
            dy = by - ay
            norm = math.hypot(dx, dy)
            if norm > 0:
                # A dodges perpendicular (left)
                perp_ax = -dy / norm * DODGE_STRENGTH
                perp_ay = dx / norm * DODGE_STRENGTH
                # B dodges perpendicular (right)
                perp_bx = dy / norm * DODGE_STRENGTH
                perp_by = -dx / norm * DODGE_STRENGTH
            else:
                perp_ax = perp_ay = perp_bx = perp_by = 0

            nax, nay = move_toward(ax + perp_ax, ay + perp_ay, agx, agy, SPEED)
            nbx, nby = move_toward(bx + perp_bx, by + perp_by, bgx, bgy, SPEED)
        else:
            nax, nay = move_toward(ax, ay, agx, agy, SPEED)
            nbx, nby = move_toward(bx, by, bgx, bgy, SPEED)

        total_dist_a += math.hypot(nax - ax, nay - ay)
        total_dist_b += math.hypot(nbx - bx, nby - by)
        ax, ay = nax, nay
        bx, by = nbx, nby
        if math.hypot(ax - bx, ay - by) < COLLISION_DIST:
            collisions += 1
    reached_a = math.hypot(ax - agx, ay - agy) < 2.0
    reached_b = math.hypot(bx - bgx, by - bgy) < 2.0
    return collisions, total_dist_a + total_dist_b, reached_a and reached_b, avoidance_count

def simulate_potential_field(scA, scB):
    """Standard artificial potential field (repulsive force)."""
    ax, ay, agx, agy = scA
    bx, by, bgx, bgy = scB
    collisions = 0
    total_dist_a = 0
    total_dist_b = 0
    REP_GAIN = 5.0
    REP_DIST = 8.0
    for _ in range(STEPS):
        # Attractive force toward goal
        dax, day = agx - ax, agy - ay
        da = math.hypot(dax, day)
        if da > 0:
            fax, fay = SPEED * dax / da, SPEED * day / da
        else:
            fax, fay = 0, 0

        dbx, dby = bgx - bx, bgy - by
        db = math.hypot(dbx, dby)
        if db > 0:
            fbx, fby = SPEED * dbx / db, SPEED * dby / db
        else:
            fbx, fby = 0, 0

        # Repulsive force between robots
        rx, ry = ax - bx, ay - by
        rd = math.hypot(rx, ry)
        if 0 < rd < REP_DIST:
            rep = REP_GAIN * (1.0 / rd - 1.0 / REP_DIST) / (rd * rd)
            fax += rep * rx / rd
            fay += rep * ry / rd
            fbx -= rep * rx / rd
            fby -= rep * ry / rd

        # Normalize to speed
        fa_norm = math.hypot(fax, fay)
        if fa_norm > SPEED:
            fax, fay = SPEED * fax / fa_norm, SPEED * fay / fa_norm
        fb_norm = math.hypot(fbx, fby)
        if fb_norm > SPEED:
            fbx, fby = SPEED * fbx / fb_norm, SPEED * fby / fb_norm

        nax, nay = ax + fax, ay + fay
        nbx, nby = bx + fbx, by + fby
        total_dist_a += math.hypot(nax - ax, nay - ay)
        total_dist_b += math.hypot(nbx - bx, nby - by)
        ax, ay = nax, nay
        bx, by = nbx, nby
        if math.hypot(ax - bx, ay - by) < COLLISION_DIST:
            collisions += 1
    reached_a = math.hypot(ax - agx, ay - agy) < 2.0
    reached_b = math.hypot(bx - bgx, by - bgy) < 2.0
    return collisions, total_dist_a + total_dist_b, reached_a and reached_b

# --- Generate scenarios ---
rng = random.Random(42)
scenarios = [generate_scenario(rng) for _ in range(N_SCENARIOS)]

print("=" * 70)
print("H-ROB-6: Inter-Tension = Collision Avoidance Simulation")
print("=" * 70)
print(f"Arena: {ARENA}x{ARENA}, Steps: {STEPS}, Scenarios: {N_SCENARIOS}")
print(f"Collision distance: {COLLISION_DIST}, Robot speed: {SPEED}")
print()

# --- Baseline: No avoidance ---
no_avoid_collisions = 0
no_avoid_dist = 0
no_avoid_reached = 0
for scA, scB in scenarios:
    c, d, r = simulate_no_avoidance(scA, scB)
    no_avoid_collisions += c
    no_avoid_dist += d
    no_avoid_reached += int(r)

print(f"BASELINE (no avoidance):")
print(f"  Total collisions: {no_avoid_collisions}")
print(f"  Avg collisions/scenario: {no_avoid_collisions / N_SCENARIOS:.2f}")
print(f"  Avg total distance: {no_avoid_dist / N_SCENARIOS:.1f}")
print(f"  Goal reached: {no_avoid_reached}/{N_SCENARIOS}")
print()

# --- Potential field ---
pf_collisions = 0
pf_dist = 0
pf_reached = 0
for scA, scB in scenarios:
    c, d, r = simulate_potential_field(scA, scB)
    pf_collisions += c
    pf_dist += d
    pf_reached += int(r)

print(f"POTENTIAL FIELD (standard robotics):")
print(f"  Total collisions: {pf_collisions}")
print(f"  Avg collisions/scenario: {pf_collisions / N_SCENARIOS:.2f}")
print(f"  Avg total distance: {pf_dist / N_SCENARIOS:.1f}")
print(f"  Goal reached: {pf_reached}/{N_SCENARIOS}")
print()

# --- Tension-based avoidance: scan thresholds ---
print("-" * 70)
print("THRESHOLD SCAN: Tension-based avoidance")
print("-" * 70)
print(f"| {'Threshold':>10} | {'Collisions':>10} | {'Avg/Scen':>8} | {'Distance':>9} | {'Reached':>7} | {'Avoids':>7} |")
print(f"|{'---':->12}|{'---':->12}|{'---':->10}|{'---':->11}|{'---':->9}|{'---':->9}|")

threshold_results = {}
for thr in THRESHOLD_SCAN:
    t_coll = 0
    t_dist = 0
    t_reached = 0
    t_avoids = 0
    for scA, scB in scenarios:
        c, d, r, a = simulate_tension_avoidance(scA, scB, thr)
        t_coll += c
        t_dist += d
        t_reached += int(r)
        t_avoids += a

    score = t_coll / N_SCENARIOS + (1 - t_reached / N_SCENARIOS) * 10 + (t_dist / N_SCENARIOS - no_avoid_dist / N_SCENARIOS) / 100
    threshold_results[thr] = {
        'collisions': t_coll,
        'avg_coll': t_coll / N_SCENARIOS,
        'distance': t_dist / N_SCENARIOS,
        'reached': t_reached,
        'avoids': t_avoids / N_SCENARIOS,
        'score': score,
    }
    print(f"| {thr:10.2f} | {t_coll:10d} | {t_coll / N_SCENARIOS:8.2f} | {t_dist / N_SCENARIOS:9.1f} | {t_reached:3d}/{N_SCENARIOS:3d} | {t_avoids / N_SCENARIOS:7.1f} |")

# Find optimal threshold
best_thr = min(THRESHOLD_SCAN, key=lambda t: threshold_results[t]['score'])
print()
print(f"Optimal threshold (min score): {best_thr:.2f}")
print(f"  Score formula: avg_collisions + 10*(1-reach_rate) + detour/100")
print(f"  Golden Zone: [0.212, 0.500]")
in_gz = 0.212 <= best_thr <= 0.500
print(f"  Optimal in Golden Zone? {'YES' if in_gz else 'NO'} (threshold={best_thr:.2f})")
print()

# ASCII Graph: Threshold vs Collisions
print("=" * 55)
print("ASCII GRAPH 1: Threshold vs Avg Collisions/Scenario")
print("=" * 55)
max_c = max(threshold_results[t]['avg_coll'] for t in THRESHOLD_SCAN) or 1
for thr in THRESHOLD_SCAN:
    c = threshold_results[thr]['avg_coll']
    bar_len = int(35 * c / max_c) if max_c > 0 else 0
    gz = "*" if 0.212 <= thr <= 0.500 else " "
    opt = " <<< OPTIMAL" if thr == best_thr else ""
    print(f"  {gz} T={thr:4.2f} |{'#' * bar_len:<35}| {c:.2f}{opt}")
print("  (* = inside Golden Zone)")
print()

# ASCII Graph: Threshold vs Avoidance maneuvers
print("=" * 55)
print("ASCII GRAPH 2: Threshold vs Avoidance Maneuvers/Scenario")
print("=" * 55)
max_a = max(threshold_results[t]['avoids'] for t in THRESHOLD_SCAN) or 1
for thr in THRESHOLD_SCAN:
    a = threshold_results[thr]['avoids']
    bar_len = int(35 * a / max_a) if max_a > 0 else 0
    gz = "*" if 0.212 <= thr <= 0.500 else " "
    print(f"  {gz} T={thr:4.2f} |{'#' * bar_len:<35}| {a:.1f}")
print("  (* = inside Golden Zone)")
print()

# ASCII Trajectory: one example scenario
print("=" * 55)
print("ASCII GRAPH 3: Example Trajectory (Scenario 0)")
print("=" * 55)
scA, scB = scenarios[0]
# Simulate with optimal threshold and record positions
ax, ay, agx, agy = scA
bx, by, bgx, bgy = scB

# Grid for trajectory visualization
TGRID = 25
traj_grid = [[' ' for _ in range(TGRID)] for _ in range(TGRID)]

def mark(grid, x, y, char, size=ARENA):
    gi = int(x / size * (TGRID - 1))
    gj = int((size - y) / size * (TGRID - 1))  # flip y
    gi = max(0, min(TGRID - 1, gi))
    gj = max(0, min(TGRID - 1, gj))
    grid[gj][gi] = char

# Mark start and goals
mark(traj_grid, scA[0], scA[1], 'A')
mark(traj_grid, scA[2], scA[3], 'a')
mark(traj_grid, scB[0], scB[1], 'B')
mark(traj_grid, scB[2], scB[3], 'b')

# Simulate and mark trajectory
ax, ay = scA[0], scA[1]
bx, by = scB[0], scB[1]
for step in range(STEPS):
    T = inter_tension(ax, ay, bx, by)
    if T > best_thr:
        dx = bx - ax
        dy = by - ay
        norm = math.hypot(dx, dy)
        if norm > 0:
            pax, pay = -dy / norm * DODGE_STRENGTH, dx / norm * DODGE_STRENGTH
            pbx, pby = dy / norm * DODGE_STRENGTH, -dx / norm * DODGE_STRENGTH
        else:
            pax = pay = pbx = pby = 0
        nax, nay = move_toward(ax + pax, ay + pay, agx, agy, SPEED)
        nbx, nby = move_toward(bx + pbx, by + pby, bgx, bgy, SPEED)
    else:
        nax, nay = move_toward(ax, ay, agx, agy, SPEED)
        nbx, nby = move_toward(bx, by, bgx, bgy, SPEED)
    ax, ay = nax, nay
    bx, by = nbx, nby
    if step % 15 == 0:
        mark(traj_grid, ax, ay, '.')
        mark(traj_grid, bx, by, '+')

# Re-mark endpoints (they may have been overwritten)
mark(traj_grid, scA[0], scA[1], 'A')
mark(traj_grid, scA[2], scA[3], 'a')
mark(traj_grid, scB[0], scB[1], 'B')
mark(traj_grid, scB[2], scB[3], 'b')

print(f"  A=Robot A start, a=goal | B=Robot B start, b=goal")
print(f"  .=A trajectory  +=B trajectory  (threshold={best_thr:.2f})")
print(f"  +{'-' * TGRID}+")
for row in traj_grid:
    print(f"  |{''.join(row)}|")
print(f"  +{'-' * TGRID}+")
print()

# Comparison table
print("=" * 70)
print("COMPARISON: Three Methods")
print("=" * 70)
tr = threshold_results[best_thr]
print(f"| {'Method':>20} | {'Collisions':>10} | {'Avg/Scen':>8} | {'Distance':>9} | {'Reached':>7} |")
print(f"|{'---':->22}|{'---':->12}|{'---':->10}|{'---':->11}|{'---':->9}|")
print(f"| {'No Avoidance':>20} | {no_avoid_collisions:10d} | {no_avoid_collisions / N_SCENARIOS:8.2f} | {no_avoid_dist / N_SCENARIOS:9.1f} | {no_avoid_reached:3d}/{N_SCENARIOS:3d} |")
print(f"| {'Potential Field':>20} | {pf_collisions:10d} | {pf_collisions / N_SCENARIOS:8.2f} | {pf_dist / N_SCENARIOS:9.1f} | {pf_reached:3d}/{N_SCENARIOS:3d} |")
print(f"| {'Tension (T={:.2f})'.format(best_thr):>20} | {tr['collisions']:10d} | {tr['avg_coll']:8.2f} | {tr['distance']:9.1f} | {tr['reached']:3d}/{N_SCENARIOS:3d} |")
print()

# Collision reduction
if no_avoid_collisions > 0:
    tension_reduction = (1 - tr['collisions'] / no_avoid_collisions) * 100
    pf_reduction = (1 - pf_collisions / no_avoid_collisions) * 100
    print(f"Collision reduction vs baseline:")
    print(f"  Tension-based: {tension_reduction:+.1f}%")
    print(f"  Potential field: {pf_reduction:+.1f}%")
print()
print("=" * 70)
