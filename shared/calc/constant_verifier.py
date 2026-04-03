#!/usr/bin/env python3
"""Constant Verifier — Texas Sharpshooter Auto-test for New Constant Discovery

Usage:
  python3 constant_verifier.py --value 0.577 --target "1/sqrt(3)"
  python3 constant_verifier.py --value 1.676 --target "5/3"
  python3 constant_verifier.py --value 1.0114 --target "1"
"""

import argparse
import math
import random


def parse_target(target_str):
    """Convert string to mathematical value."""
    replacements = {
        'sqrt': 'math.sqrt',
        'log': 'math.log',
        'ln': 'math.log',
        'pi': 'math.pi',
        'e': 'math.e',
        'phi': '((1+math.sqrt(5))/2)',
    }
    expr = target_str
    for k, v in replacements.items():
        expr = expr.replace(k, v)
    try:
        return eval(expr)
    except:
        raise ValueError(f"Cannot parse: {target_str}")


def texas_sharpshooter(value, target, search_type='simple', n_sim=100000):
    """Texas sharpshooter test.

    search_type:
      'simple': a/sqrt(b), a=1..3, b=1..20
      'ratio': a/b, a,b=1..20
      'product': a*b, a,b from known constants
    """
    error = abs(value / target - 1) if target != 0 else abs(value)

    if search_type == 'simple':
        count = 0
        total = 0
        for a in range(1, 4):
            for b in range(1, 21):
                try:
                    val = a / math.sqrt(b)
                    total += 1
                    if abs(val / target - 1) <= error:
                        count += 1
                except:
                    pass
        # Also check a^(b/c) * d^(1/e)
        for a in [2, 3, 5, 6, 7]:
            for b in range(1, 7):
                for c in range(1, 7):
                    if b == c:
                        continue
                    for d in [2, 3, 5, 6, 7]:
                        for f in [2, 3, 4, 5, 6]:
                            try:
                                val = a**(b/c) * d**(1/f)
                                total += 1
                                if abs(val / target - 1) <= error:
                                    count += 1
                            except:
                                pass
        p = count / total if total > 0 else 1.0
        return p, count, total

    elif search_type == 'ratio':
        count = 0
        total = 0
        for a in range(1, 21):
            for b in range(1, 21):
                if a == b:
                    continue
                val = a / b
                total += 1
                if abs(val / target - 1) <= error:
                    count += 1
        p = count / total if total > 0 else 1.0
        return p, count, total

    elif search_type == 'uniform':
        random.seed(42)
        lo = target * 0.5
        hi = target * 2.0
        count = sum(1 for _ in range(n_sim) if abs(random.uniform(lo, hi) / target - 1) <= error)
        p = count / n_sim
        return p, count, n_sim


def grade(p_value, error_pct):
    """Grade determination."""
    if p_value > 0.05:
        return '⚪', 'Coincidence (p > 0.05)'
    elif p_value > 0.01:
        return '🟧', f'Structural approximation (p={p_value:.4f}, {error_pct:.3f}%)'
    else:
        return '🟧★', f'Strong structural approximation (p={p_value:.4f}, {error_pct:.3f}%)'


def main():
    parser = argparse.ArgumentParser(description='Constant Texas sharpshooter tester')
    parser.add_argument('--value', type=float, required=True, help='Measured value')
    parser.add_argument('--target', type=str, required=True, help='Comparison target (e.g.: "1/sqrt(3)", "5/3")')
    parser.add_argument('--search', type=str, default='simple', help='Search type: simple, ratio, uniform')
    args = parser.parse_args()

    target_val = parse_target(args.target)
    error_pct = abs(args.value / target_val - 1) * 100

    print('=' * 50)
    print('  Constant Verifier — Texas Sharpshooter Test')
    print('=' * 50)
    print(f'  Measured:  {args.value}')
    print(f'  Target:    {args.target} = {target_val:.6f}')
    print(f'  Error:     {error_pct:.4f}%')
    print(f'  Search type: {args.search}')
    print()

    p, count, total = texas_sharpshooter(args.value, target_val, args.search)

    print(f'  Search space: {total} combinations')
    print(f'  Equal or less: {count}')
    print(f'  p-value:   {p:.4f}')
    print()

    emoji, desc = grade(p, error_pct)
    print(f'  Grade: {emoji} {desc}')
    print()

    if p <= 0.05:
        print(f'  For README record:')
        print(f'  | C?? | {emoji} | {args.target} | {args.value} vs {target_val:.4f} | Verifier | Texas p={p:.4f}, error {error_pct:.3f}% |')
    else:
        print(f'  No record needed (coincidence)')

    print('=' * 50)


if __name__ == '__main__':
    main()