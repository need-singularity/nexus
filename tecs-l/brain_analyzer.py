#!/usr/bin/env python3
"""Brain Data Analyzer — GABA/Structure/Plasticity → D,P,I Mapping → Golden Zone Determination

Usage:
  python3 brain_analyzer.py --gaba 0.8 --deficit 0.4 --plasticity 0.85
  python3 brain_analyzer.py --profile einstein
  python3 brain_analyzer.py --profile savant
"""

import numpy as np
import argparse
import sys
sys.path.append('.')

def gaba_to_inhibition(gaba_mmol):
    """GABA concentration(mmol/L) → Inhibition mapping (Hypothesis 155)"""
    # Normal GABA ≈ 1.0 mmol/L → I ≈ 0.6
    # Linear mapping: I = 0.6 × gaba
    I = np.clip(0.6 * gaba_mmol, 0.05, 0.95)
    return I

def analyze_brain(D, P, I, name=""):
    """Brain parameters → Genius Score + Golden Zone determination"""
    G = D * P / I

    # Population statistics
    rng = np.random.default_rng(42)
    pop_d = rng.beta(2, 5, 50000).clip(0.01, 0.99)
    pop_p = rng.beta(5, 2, 50000).clip(0.01, 0.99)
    pop_i = rng.beta(5, 2, 50000).clip(0.05, 0.99)
    pop_g = pop_d * pop_p / pop_i

    z = (G - pop_g.mean()) / pop_g.std()

    # Golden Zone determination
    if 0.213 <= I <= 0.500:
        zone = "🎯 Golden Zone!"
    elif I < 0.213:
        zone = "⚡ Below Golden Zone (Chaos risk)"
    else:
        zone = "○ Outside Golden Zone (Over-inhibited)"

    # Singularity grade
    if abs(z) > 5:
        grade = "🔴 Extreme singularity"
    elif abs(z) > 3:
        grade = "🟠 Strong singularity"
    elif abs(z) > 2:
        grade = "🟡 Singularity"
    else:
        grade = "○ Normal range"

    # Conservation law
    conservation = D * P  # G×I = D×P

    print(f"\n  {'═' * 50}")
    if name:
        print(f"  Profile: {name}")
    print(f"  {'═' * 50}")
    print(f"  Input:")
    print(f"    Deficit          = {D:.2f}")
    print(f"    Plasticity       = {P:.2f}")
    print(f"    Inhibition       = {I:.2f}")
    print(f"  {'─' * 50}")
    print(f"  Results:")
    print(f"    Genius Score = {G:.2f}")
    print(f"    Z-Score      = {z:.2f}σ  {grade}")
    print(f"    Golden Zone  = {zone}")
    print(f"    G×I = D×P    = {conservation:.4f} (conserved)")

    # Graph
    pos = int(np.clip(I, 0, 1) * 40)
    line = list("·" * 41)
    golden_lo = int(0.213 * 40)
    golden_hi = int(0.500 * 40)
    for gi in range(golden_lo, golden_hi + 1):
        if gi < 41: line[gi] = "░"
    third = int(1/3 * 40)
    if third < 41: line[third] = "│"
    if pos < 41: line[pos] = "●"
    print(f"    {''.join(line)}")
    print(f"    0{'─'*8}0.21{'░'*5}1/3{'░'*5}0.50{'─'*8}1.0")
    print(f"  {'═' * 50}")

PROFILES = {
    'normal': {'D': 0.1, 'P': 0.6, 'I': 0.6, 'name': 'Normal person'},
    'einstein': {'D': 0.5, 'P': 0.9, 'I': 0.4, 'name': 'Einstein (estimated)'},
    'savant': {'D': 0.7, 'P': 0.85, 'I': 0.35, 'name': 'Savant (estimated)'},
    'epilepsy': {'D': 0.6, 'P': 0.7, 'I': 0.15, 'name': 'Epilepsy patient (estimated)'},
    'meditation': {'D': 0.3, 'P': 0.8, 'I': 0.36, 'name': 'Meditation practitioner (estimated)'},
    'child': {'D': 0.2, 'P': 0.95, 'I': 0.5, 'name': 'Child'},
    'elderly': {'D': 0.15, 'P': 0.3, 'I': 0.7, 'name': 'Elderly'},
    'acquired': {'D': 0.6, 'P': 0.7, 'I': 0.3, 'name': 'Acquired savant (estimated)'},
    'sylvian': {'D': 0.4, 'P': 0.85, 'I': 0.4, 'name': 'Partial Sylvian fissure absence'},
}

def main():
    parser = argparse.ArgumentParser(description="Brain Data Analyzer")
    parser.add_argument('--deficit', type=float, default=None)
    parser.add_argument('--plasticity', type=float, default=None)
    parser.add_argument('--inhibition', type=float, default=None)
    parser.add_argument('--gaba', type=float, default=None, help="GABA concentration (mmol/L)")
    parser.add_argument('--profile', type=str, default=None, choices=list(PROFILES.keys()))
    parser.add_argument('--all', action='store_true', help="Compare all profiles")
    args = parser.parse_args()

    print("═" * 60)
    print("   🧠 Brain Data Analyzer")
    print("═" * 60)

    if args.all:
        for key, prof in PROFILES.items():
            analyze_brain(prof['D'], prof['P'], prof['I'], prof['name'])
    elif args.profile:
        prof = PROFILES[args.profile]
        analyze_brain(prof['D'], prof['P'], prof['I'], prof['name'])
    elif args.deficit is not None:
        I = args.inhibition or (gaba_to_inhibition(args.gaba) if args.gaba else 0.5)
        P = args.plasticity or 0.8
        analyze_brain(args.deficit, P, I)
    else:
        print("  Specify --profile, --all, or --deficit/--plasticity/--inhibition")
        print(f"  Profiles: {', '.join(PROFILES.keys())}")

if __name__ == '__main__':
    main()