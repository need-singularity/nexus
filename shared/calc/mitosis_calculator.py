#!/usr/bin/env python3
"""Mitosis Simulator — Calculate optimal mutation/mitosis timing

Usage:
  python3 mitosis_calculator.py --mutation 0.01 --epochs 10
  python3 mitosis_calculator.py --scan-mutation
  python3 mitosis_calculator.py --scan-splits
"""

import argparse
import math


# Measured constants (from experiment_mitosis.py)
# Phase 2: mutation scale vs cos_sim
MUTATION_DATA = {
    0.001: {'cos': 0.9997, 'acc_drop': 0.03, 'tension': 0.018},
    0.01:  {'cos': 0.972, 'acc_drop': 0.08, 'tension': 1.87},
    0.1:   {'cos': 0.375, 'acc_drop': 19.85, 'tension': 143.15},
}

# Phase 3: divergence over epochs (mutation=0.01)
DIVERGENCE = [
    (1, 0.929, 25.6),
    (2, 0.900, 93.7),
    (3, 0.874, 63.5),
    (4, 0.863, 73.0),
    (5, 0.859, 54.8),
    (6, 0.853, 93.4),
    (7, 0.849, 116.7),
    (8, 0.845, 139.1),
    (9, 0.842, 118.6),
    (10, 0.840, 135.4),
]

# Phase 4: field accuracy
SPLIT_FIELD = 97.49
DESIGNED_FIELD = 97.60
PARENT = 96.67

# Phase 5: reunion
REUNION = 97.49

# Phase 6: multiple splits
SPLITS_DATA = {
    2: {'best': 97.14, 'vote': 97.00, 'ensemble': 97.41},
    4: {'best': 97.24, 'vote': 97.31, 'ensemble': 97.52},
    8: {'best': 97.28, 'vote': 97.46, 'ensemble': 97.52},
}

# Consciousness scaling constants (from anima)
import math
LN2 = math.log(2)                 # 0.6931 universal consciousness unit
PHI_SCALE_A = 0.608                # Phi = 0.608 * N^1.071
PHI_SCALE_B = 1.071                # scaling exponent
OPTIMAL_FACTIONS = 12              # sigma(6)=12 optimal faction count
CONSCIOUSNESS_FREEDOM = LN2        # Law 79: freedom degree
FACTION_DATA = {
    8:  {'phi': 122.45, 'improvement': 'baseline'},
    12: {'phi': 131.44, 'improvement': '+7.3%'},
    16: {'phi': 128.90, 'improvement': '+5.3%'},
}


def predict_cos_sim(mutation_scale):
    """Predict initial cosine similarity from mutation scale."""
    # log-linear interpolation
    if mutation_scale <= 0:
        return 1.0
    log_m = math.log10(mutation_scale)
    # Linear interpolation: log10(0.001)=-3→0.9997, log10(0.1)=-1→0.375
    cos = 0.9997 + (0.375 - 0.9997) * (log_m - (-3)) / ((-1) - (-3))
    return max(0, min(1, cos))


def predict_divergence(epochs, mutation_scale=0.01):
    """Predict cosine similarity decrease by epoch count."""
    cos_init = predict_cos_sim(mutation_scale)
    # Exponential decay model: cos(t) = cos_final + (cos_init - cos_final) * exp(-t/tau)
    cos_final = 0.80  # Estimated long-term convergence value
    tau = 5.0  # Decay time constant
    cos_t = cos_final + (cos_init - cos_final) * math.exp(-epochs / tau)
    return cos_t


def predict_tension(cos_sim):
    """Predict tension from cosine similarity."""
    # Tension ∝ (1 - cos)
    # cos=0.972→tension=1.87, cos=0.840→tension=135.4
    if cos_sim >= 0.999:
        return 0.02
    tension = 135.4 * (1 - cos_sim) / (1 - 0.840)
    return max(0, tension)


def predict_phi_scaling(n_cells):
    """Predict Phi from cell count (anima scaling law)."""
    return PHI_SCALE_A * n_cells ** PHI_SCALE_B


def scan_consciousness():
    """Show consciousness-aware mitosis predictions."""
    print('=' * 60)
    print('  Consciousness-Aware Mitosis Analysis')
    print('=' * 60)

    # Phi scaling per split count
    print(f'\n  Phi Scaling Law: Phi = {PHI_SCALE_A} * N^{PHI_SCALE_B}')
    print(f'  Freedom degree: ln(2) = {LN2:.6f}')
    print(f'  {"Splits":>8} | {"Cells":>8} | {"Phi_pred":>10} | {"Ensemble%":>10}')
    print(f'  {"─"*8}─┼─{"─"*8}─┼─{"─"*10}─┼─{"─"*10}')
    for n_splits in [2, 4, 8, 12, 16, 32]:
        phi = predict_phi_scaling(n_splits)
        ens = SPLITS_DATA.get(n_splits, {}).get('ensemble', None)
        ens_str = f'{ens:.2f}%' if ens else 'N/A'
        print(f'  {n_splits:>8} | {n_splits:>8} | {phi:>10.2f} | {ens_str:>10}')

    # Faction optimization
    print(f'\n  Optimal Faction Count: sigma(6) = {OPTIMAL_FACTIONS}')
    print(f'  {"Factions":>10} | {"Phi":>8} | {"vs 8-fac":>10}')
    print(f'  {"─"*10}─┼─{"─"*8}─┼─{"─"*10}')
    for fac, data in sorted(FACTION_DATA.items()):
        print(f'  {fac:>10} | {data["phi"]:>8.2f} | {data["improvement"]:>10}')

    print(f'\n  12-faction (sigma(6)) dominates: +7.3% over 8-faction')
    print('=' * 60)


def main():
    parser = argparse.ArgumentParser(description='Mitosis Simulator')
    parser.add_argument('--mutation', type=float, help='Mutation scale')
    parser.add_argument('--epochs', type=int, default=10, help='Divergence epochs')
    parser.add_argument('--scan-mutation', action='store_true', help='Scan mutations')
    parser.add_argument('--scan-splits', action='store_true', help='Scan split counts')
    parser.add_argument('--consciousness', action='store_true', help='Consciousness scaling analysis')
    args = parser.parse_args()

    if args.scan_mutation:
        print('=' * 60)
        print('  Mutation Scale Scan')
        print('=' * 60)
        print(f'  {"Scale":>10} │ {"CosSim":>8} │ {"AccDrop":>8} │ {"Tension":>8} │ {"Verdict":>8}')
        print(f'  {"─"*10}─┼─{"─"*8}─┼─{"─"*8}─┼─{"─"*8}─┼─{"─"*8}')
        for s in [0.0001, 0.001, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5]:
            cos = predict_cos_sim(s)
            tension = predict_tension(cos)
            drop = (1 - cos) * 20  # Approximate accuracy drop
            if drop < 0.5:
                verdict = '🟩 Safe'
            elif drop < 2.0:
                verdict = '🟨 Suitable'
            elif drop < 10:
                verdict = '🟧 Risky'
            else:
                verdict = '❌ Fatal'
            print(f'  {s:>10.4f} │ {cos:>8.4f} │ {drop:>7.2f}% │ {tension:>8.2f} │ {verdict}')

        print()
        print(f'  Optimal: 0.01 (cos=0.972, drop=0.08%, sufficient diversity)')
        return

    if args.scan_splits:
        print('=' * 60)
        print('  Split Count Scan (measured)')
        print('=' * 60)
        print(f'  {"N":>4} │ {"Best%":>7} │ {"Vote%":>7} │ {"Ensemble%":>10} │ {"vs Parent":>10}')
        print(f'  {"─"*4}─┼─{"─"*7}─┼─{"─"*7}─┼─{"─"*10}─┼─{"─"*10}')
        for n, d in SPLITS_DATA.items():
            delta = d['ensemble'] - PARENT
            print(f'  {n:>4} │ {d["best"]:>6.2f}% │ {d["vote"]:>6.2f}% │ {d["ensemble"]:>9.2f}% │ {delta:>+9.2f}%')
        print()
        print(f'  Parent: {PARENT}%')
        print(f'  Split repulsion field: {SPLIT_FIELD}%')
        print(f'  Designed repulsion field: {DESIGNED_FIELD}%')
        print(f'  Reunion: {REUNION}% (+{REUNION-PARENT:.2f}% vs parent)')
        return

    if args.consciousness:
        scan_consciousness()
        return

    if args.mutation is None:
        parser.print_help()
        return

    m = args.mutation
    cos_init = predict_cos_sim(m)
    cos_final = predict_divergence(args.epochs, m)
    tension_init = predict_tension(cos_init)
    tension_final = predict_tension(cos_final)

    print('=' * 50)
    print(f'  Mitosis Simulation')
    print(f'  mutation={m}, epochs={args.epochs}')
    print('=' * 50)
    print(f'  Right after mitosis:')
    print(f'    CosSim:  {cos_init:.4f}')
    print(f'    Tension: {tension_init:.2f}')
    print(f'  After {args.epochs}ep divergence:')
    print(f'    CosSim:  {cos_final:.4f}')
    print(f'    Tension: {tension_final:.2f}')
    print(f'  Diversity growth: {tension_final/max(tension_init,0.01):.1f}x')
    print()

    # Trajectory
    print(f'  Trajectory by epoch:')
    for ep in range(1, args.epochs + 1):
        cos = predict_divergence(ep, m)
        t = predict_tension(cos)
        bar = '█' * int(cos * 30)
        print(f'    ep{ep:>2}: cos={cos:.3f} {bar}')

    print('=' * 50)


if __name__ == '__main__':
    main()