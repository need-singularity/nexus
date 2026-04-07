#!/usr/bin/env python3
"""Hysteresis Verifier — Proving I is a cusp control variable

Landau free energy F(G, I) = G⁴/4 - f(I)·G²/2 + (D×P)·G
dG/dt = -dF/dG = -G³ + f(I)·G - D×P

If G trajectory differs when cycling I, hysteresis confirmed → 🟩 Upgrade

Usage:
  python3 hysteresis_verifier.py                    # Default run
  python3 hysteresis_verifier.py --dp 0.3           # Specify D×P
  python3 hysteresis_verifier.py --sweep 0.1 0.9    # I range
  python3 hysteresis_verifier.py --ic 0.5           # Specify I_c
  python3 hysteresis_verifier.py --scan-ic          # Search for optimal I_c
"""

import math
import argparse


def landau_force(G, a, b):
    """dG/dt = -dF/dG = -G³ + a·G - b"""
    return -G**3 + a * G - b


def f_of_I(I, I_c, c=3.0):
    """I → Landau control variable a mapping
    f(I) = c·(I_c - I)
    I < I_c → a > 0 (double well, hysteresis possible)
    I > I_c → a < 0 (single well, no hysteresis)
    """
    return c * (I_c - I)


def simulate_sweep(I_start, I_end, dp, I_c, c=3.0, n_steps=200, dt=0.01, relax=50):
    """Sweep I from I_start → I_end and track G trajectory

    Small relax causes hysteresis (equilibrium not reached)
    Large relax eliminates hysteresis (always at equilibrium)
    """
    I_values = []
    G_values = []

    # Initial G: start at free energy minimum
    a_init = f_of_I(I_start, I_c, c)
    if a_init > 0:
        # Forward: left well, Backward: right well
        if I_end > I_start:
            G = -math.sqrt(a_init) - 0.1  # Left well depth
        else:
            G = math.sqrt(a_init) + 0.1   # Right well depth
    else:
        G = 0.0

    dI = (I_end - I_start) / n_steps

    for step in range(n_steps + 1):
        I = I_start + dI * step
        a = f_of_I(I, I_c, c)

        # Limited relaxation: prevent complete equilibration
        for _ in range(relax):
            force = landau_force(G, a, dp)
            G = G + dt * force
            G = max(-10, min(10, G))

        I_values.append(I)
        G_values.append(G)

    return I_values, G_values


def measure_hysteresis(forward_I, forward_G, backward_I, backward_G, threshold=0.3):
    """Measure hysteresis width: forward vs backward G difference at same I"""
    hysteresis_points = []

    for i, I_f in enumerate(forward_I):
        # Find closest I in backward
        best_j = min(range(len(backward_I)),
                     key=lambda j: abs(backward_I[j] - I_f))
        if abs(backward_I[best_j] - I_f) < 0.02:
            diff = abs(forward_G[i] - backward_G[best_j])
            if diff > threshold:
                hysteresis_points.append({
                    'I': I_f,
                    'G_forward': forward_G[i],
                    'G_backward': backward_G[best_j],
                    'diff': diff,
                })

    return hysteresis_points


def run_verification(dp=0.3, I_c=0.5, c=3.0, I_min=0.05, I_max=0.95):
    """Full hysteresis verification"""
    print(f"\n{'═'*65}")
    print(f"  Hysteresis Verifier")
    print(f"{'═'*65}")
    print(f"\n  Parameters:")
    print(f"    D×P = {dp}")
    print(f"    I_c = {I_c} (critical I)")
    print(f"    c   = {c} (mapping strength)")
    print(f"    I range: [{I_min}, {I_max}]")

    print(f"\n  Free energy: F(G,I) = G⁴/4 - f(I)·G²/2 + (D×P)·G")
    print(f"  f(I) = {c}·({I_c} - I)")

    # Hysteresis theoretical conditions
    # 4·a³ = 27·b² → a = (27·dp²/4)^(1/3)
    a_crit = (27 * dp**2 / 4) ** (1/3)
    # f(I) = a_crit → c·(I_c - I) = a_crit → I = I_c - a_crit/c
    I_hyst_start = I_c - a_crit / c
    print(f"\n  Theoretical hysteresis start I = {I_hyst_start:.4f}")
    print(f"  (from 4·f(I)³ = 27·(D×P)²)")

    # Forward sweep: I_min → I_max
    print(f"\n{'─'*65}")
    print(f"  Forward: I = {I_min} → {I_max}")
    fwd_I, fwd_G = simulate_sweep(I_min, I_max, dp, I_c, c)

    # Backward sweep: I_max → I_min
    print(f"  Backward: I = {I_max} → {I_min}")
    bwd_I, bwd_G = simulate_sweep(I_max, I_min, dp, I_c, c)

    # Measure hysteresis
    hyst = measure_hysteresis(fwd_I, fwd_G, bwd_I, bwd_G)

    print(f"\n{'─'*65}")
    print(f"  Results")
    print(f"{'─'*65}")

    if hyst:
        I_min_h = min(h['I'] for h in hyst)
        I_max_h = max(h['I'] for h in hyst)
        max_diff = max(h['diff'] for h in hyst)
        width = I_max_h - I_min_h

        print(f"\n  ✅ Hysteresis found!")
        print(f"  Hysteresis interval: I ∈ [{I_min_h:.3f}, {I_max_h:.3f}]")
        print(f"  Hysteresis width:   {width:.3f}")
        print(f"  Maximum difference: {max_diff:.3f}")

        # Compare with Golden Zone
        gz_lower = 0.5 - math.log(4/3)  # 0.2123
        gz_upper = 0.5
        overlap_lower = max(I_min_h, gz_lower)
        overlap_upper = min(I_max_h, gz_upper)
        if overlap_lower < overlap_upper:
            overlap = overlap_upper - overlap_lower
            print(f"\n  Overlap with Golden Zone [{gz_lower:.3f}, {gz_upper:.3f}]:")
            print(f"  Overlap interval: [{overlap_lower:.3f}, {overlap_upper:.3f}]")
            print(f"  Overlap width:   {overlap:.3f}")
            print(f"  Overlap ratio: {overlap / (gz_upper - gz_lower) * 100:.1f}%")
        else:
            print(f"\n  ⚠️ No overlap with Golden Zone")

        # Sample output
        print(f"\n  Hysteresis interval samples:")
        print(f"  I      │ G(forward) │ G(backward) │ Diff")
        print(f"  ───────┼──────────┼──────────┼──────")
        step = max(1, len(hyst) // 8)
        for h in hyst[::step]:
            print(f"  {h['I']:6.3f} │ {h['G_forward']:8.3f}  │ {h['G_backward']:8.3f}  │ {h['diff']:.3f}")
    else:
        print(f"\n  ❌ No hysteresis")
        print(f"  Try adjusting parameters (--ic, --dp, --sweep)")

    # ASCII graph
    gz_lower = 0.5 - math.log(4/3)
    gz_upper = 0.5

    print(f"\n{'─'*65}")
    print(f"  G(I) Trajectory Graph")
    print(f"{'─'*65}")

    all_G = fwd_G + bwd_G
    G_min_val = min(all_G)
    G_max_val = max(all_G)
    G_range = G_max_val - G_min_val if G_max_val > G_min_val else 1

    rows = 20
    cols = 50
    grid = [[' ' for _ in range(cols)] for _ in range(rows)]

    def plot_point(I_val, G_val, char):
        col = int((I_val - I_min) / max(I_max - I_min, 0.01) * (cols - 1))
        row = int((1 - (G_val - G_min_val) / max(G_range, 0.01)) * (rows - 1))
        col = max(0, min(cols - 1, col))
        row = max(0, min(rows - 1, row))
        grid[row][col] = char

    for i in range(len(fwd_I)):
        plot_point(fwd_I[i], fwd_G[i], '→')
    for i in range(len(bwd_I)):
        plot_point(bwd_I[i], bwd_G[i], '←')

    gz_col_l = int((gz_lower - I_min) / max(I_max - I_min, 0.01) * (cols - 1))
    gz_col_u = int((gz_upper - I_min) / max(I_max - I_min, 0.01) * (cols - 1))
    for r in range(rows):
        if 0 <= gz_col_l < cols and grid[r][gz_col_l] == ' ':
            grid[r][gz_col_l] = '░'
        if 0 <= gz_col_u < cols and grid[r][gz_col_u] == ' ':
            grid[r][gz_col_u] = '░'

    print(f"\n  G")
    for r in range(rows):
        g_val = G_max_val - (G_range * r / max(rows - 1, 1))
        print(f"  {g_val:6.2f}│{''.join(grid[r])}")
    print(f"  {'':6}└{'─'*cols}")
    print(f"  {'':7}{I_min:<10}{' '*(cols-25)}{I_max:>10}")
    print(f"  {'':20}I (Inhibition)")
    print(f"\n  → = Forward (I↑)   ← = Backward (I↓)   ░ = Golden Zone boundary")

    # Judgment
    print(f"\n{'═'*65}")
    print(f"  Final Judgment")
    print(f"{'═'*65}")
    if hyst:
        overlap_exists = overlap_lower < overlap_upper if hyst else False
        if overlap_exists:
            print(f"\n  ✅ Hysteresis exists + Golden Zone overlap = 🟩 Upgrade possible!")
            print(f"  I is a cusp control variable, hysteresis interval matches Golden Zone")
        else:
            print(f"\n  ✅ Hysteresis exists, but no Golden Zone overlap")
            print(f"  I_c adjustment needed (use --scan-ic to find optimal)")
    else:
        print(f"\n  ❌ Hysteresis not confirmed, 🟨 maintained")

    return bool(hyst)


def scan_ic(dp=0.3, c=3.0):
    """Search for optimal I_c: maximizes overlap between hysteresis interval and Golden Zone"""
    print(f"\n{'═'*65}")
    print(f"  Optimal I_c Search")
    print(f"{'═'*65}")

    gz_lower = 0.5 - math.log(4/3)
    gz_upper = 0.5
    gz_center = (gz_lower + gz_upper) / 2

    print(f"\n  Golden Zone: [{gz_lower:.4f}, {gz_upper:.4f}], center: {gz_center:.4f}")
    print(f"\n  I_c    │ Hyst width │ GZ overlap │ Status")
    print(f"  ───────┼────────┼───────────┼──────")

    best_ic = None
    best_overlap = 0

    for ic_100 in range(20, 80, 5):
        I_c = ic_100 / 100

        fwd_I, fwd_G = simulate_sweep(0.05, 0.95, dp, I_c, c, n_steps=100, relax=300)
        bwd_I, bwd_G = simulate_sweep(0.95, 0.05, dp, I_c, c, n_steps=100, relax=300)
        hyst = measure_hysteresis(fwd_I, fwd_G, bwd_I, bwd_G)

        if hyst:
            I_min_h = min(h['I'] for h in hyst)
            I_max_h = max(h['I'] for h in hyst)
            width = I_max_h - I_min_h

            overlap_lower = max(I_min_h, gz_lower)
            overlap_upper = min(I_max_h, gz_upper)
            overlap = max(0, overlap_upper - overlap_lower)
            overlap_pct = overlap / (gz_upper - gz_lower) * 100

            marker = ' ★' if overlap_pct > best_overlap else ''
            print(f"  {I_c:.2f}   │ {width:6.3f}  │ {overlap_pct:8.1f}%   │ {'✅' if overlap > 0 else '❌'}{marker}")

            if overlap_pct > best_overlap:
                best_overlap = overlap_pct
                best_ic = I_c
        else:
            print(f"  {I_c:.2f}   │   ---   │    ---     │ No hyst")

    if best_ic:
        print(f"\n  Optimal I_c = {best_ic:.2f} (Golden Zone overlap {best_overlap:.1f}%)")
        print(f"\n  Detailed results:")
        run_verification(dp=dp, I_c=best_ic, c=c)
    else:
        print(f"\n  ⚠️ No hysteresis interval found. Adjust c value")


def main():
    parser = argparse.ArgumentParser(description="Hysteresis Verifier")
    parser.add_argument('--dp', type=float, default=0.3, help='D×P value (default: 0.3)')
    parser.add_argument('--ic', type=float, default=0.5, help='I_c threshold (default: 0.5)')
    parser.add_argument('--c', type=float, default=3.0, help='Mapping strength (default: 3.0)')
    parser.add_argument('--sweep', nargs=2, type=float, default=[0.05, 0.95],
                        help='I sweep range (default: 0.05 0.95)')
    parser.add_argument('--scan-ic', action='store_true', help='Search for optimal I_c')
    args = parser.parse_args()

    if args.scan_ic:
        scan_ic(dp=args.dp, c=args.c)
    else:
        run_verification(dp=args.dp, I_c=args.ic, c=args.c,
                        I_min=args.sweep[0], I_max=args.sweep[1])


if __name__ == '__main__':
    main()