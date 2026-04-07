#!/usr/bin/env python3
"""N-state generalization calculator — width=ln((N+1)/N)

Usage:
  python3 nstate_calculator.py              # Default table
  python3 nstate_calculator.py --n 137      # Specific N
  python3 nstate_calculator.py --find 0.118 # Find N for value
"""

import numpy as np
import argparse

def golden_zone(N):
    width = np.log((N+1)/N)
    upper = 0.5
    lower = upper - width
    center = (upper + lower) / 2
    return {'N': N, 'width': width, 'upper': upper, 'lower': lower, 'center': center}

def find_n_for_width(target_width):
    N = 1 / (np.exp(target_width) - 1)
    return int(round(N))

def main():
    parser = argparse.ArgumentParser(description="N-state calculator")
    parser.add_argument('--n', type=int, default=None)
    parser.add_argument('--find', type=float, default=None, help="Find N for this width")
    args = parser.parse_args()

    print("═" * 60)
    print("   📐 N-State Generalization Calculator")
    print("═" * 60)
    print(f"  Formula: width = ln((N+1)/N), upper = 1/2, lower = 1/2-width")

    if args.find:
        N = find_n_for_width(args.find)
        gz = golden_zone(N)
        print(f"\n  width = {args.find} → N = {N}")
        print(f"  Verification: ln({N+1}/{N}) = {gz['width']:.6f}")

    elif args.n:
        gz = golden_zone(args.n)
        print(f"\n  N = {args.n}:")
        print(f"  Width = ln({args.n+1}/{args.n}) = {gz['width']:.6f}")
        print(f"  Upper = {gz['upper']:.4f}")
        print(f"  Lower = {gz['lower']:.4f}")
        print(f"  Center = {gz['center']:.4f}")

    else:
        print(f"\n  {'N':>6} │ {'Width':>10} │ {'Lower':>8} │ {'Upper':>6} │ Physical Match")
        print(f"  {'─'*6}─┼─{'─'*10}─┼─{'─'*8}─┼─{'─'*6}─┼─{'─'*25}")

        specials = {3:'Our Model', 4:'Weinberg Angle', 6:'Perfect Number', 8:'Strong αs/Expert',
                   26:'AI Element', 137:'Fine Structure α', 100:'', 1000:''}

        for N in sorted(set([2,3,4,5,6,7,8,10,16,26,50,100,137,500,1000] + list(specials.keys()))):
            gz = golden_zone(N)
            label = specials.get(N, '')
            print(f"  {N:>6} │ {gz['width']:>10.6f} │ {gz['lower']:>8.4f} │ {gz['upper']:>6.4f} │ {label}")

    print()

if __name__ == '__main__':
    main()