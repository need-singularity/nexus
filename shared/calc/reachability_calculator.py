#!/usr/bin/env python3
"""Reachability Calculator — Measure what fraction of integers are reachable from an operand set.

Given operands like {2, 3, 4, 6, 12} (divisors + sigma + tau + phi of perfect number 6)
and operations {+, -, *, /, ^}, determine what percentage of integers in [1, N] can be
produced using up to K binary operations. This measures how "impressive" a numerical
match really is — if 40% of integers are reachable, a single hit is not surprising.

Usage:
  python3 calc/reachability_calculator.py                         # default analysis
  python3 calc/reachability_calculator.py --target 138            # check if 138 is reachable
  python3 calc/reachability_calculator.py --range 1-500           # expand range
  python3 calc/reachability_calculator.py --max-ops 3             # allow 3 operations
  python3 calc/reachability_calculator.py --extended              # include ln, exp, pi, e
  python3 calc/reachability_calculator.py --operands 2,3,6,12,28,56  # custom operands
"""

import argparse
import math
from itertools import product


# Maximum allowed result magnitude (to prevent overflow in exponentiation)
MAX_VAL = 1e15


def build_reachable(operands, max_ops=2, ops=None, extended=False):
    """Build the full set of reachable rational values and record how each was produced.

    Returns:
        dict mapping reachable integer -> expression string
    """
    if ops is None:
        ops = ['+', '-', '*', '/', '^']

    # Start with base operands (as floats) and their expressions
    # values: dict of float -> expression string
    base = {}
    for v in operands:
        base[float(v)] = str(int(v)) if v == int(v) else str(v)

    if extended:
        base[math.pi] = 'pi'
        base[math.e] = 'e'

    # Apply unary functions to base operands if extended
    unary_expanded = dict(base)
    if extended:
        for v, expr in list(base.items()):
            if v > 0:
                lv = math.log(v)
                if abs(lv) < MAX_VAL:
                    unary_expanded[lv] = f'ln({expr})'
            ev = math.exp(v)
            if ev < MAX_VAL:
                unary_expanded[ev] = f'exp({expr})'

    # Also include each operand's negative and reciprocal as implicit 0-op values?
    # No — those require an operation. Keep base clean.

    # Layers: layer[k] = dict of float -> expression for values reachable in exactly k ops
    layers = [dict(unary_expanded)]  # 0 ops = the operands themselves

    for step in range(max_ops):
        new_layer = {}
        # Combine any value from layers[0..step] with any value from layers[0..step]
        # but at least one operand must come from the latest frontier or we'd duplicate
        all_prev = {}
        for layer in layers:
            all_prev.update(layer)

        # To avoid exponential blowup, combine all_prev x all_prev
        # but only keep integer-valued results in a reasonable range
        items = list(all_prev.items())

        for (a, ea), (b, eb) in product(items, repeat=2):
            for op in ops:
                val = None
                expr = None
                try:
                    if op == '+':
                        val = a + b
                        expr = f'({ea} + {eb})'
                    elif op == '-':
                        val = a - b
                        expr = f'({ea} - {eb})'
                    elif op == '*':
                        val = a * b
                        expr = f'({ea} * {eb})'
                    elif op == '/':
                        if b == 0:
                            continue
                        val = a / b
                        expr = f'({ea} / {eb})'
                    elif op == '^':
                        if a == 0 and b < 0:
                            continue
                        if a < 0 and b != int(b):
                            continue
                        if abs(b) > 100:
                            continue
                        if a == 0:
                            val = 0.0
                        else:
                            log_est = abs(b) * math.log(abs(a)) if a != 0 else 0
                            if log_est > 35:  # e^35 ~ 1.6e15
                                continue
                            val = a ** b
                        expr = f'({ea} ^ {eb})'
                except (OverflowError, ValueError, ZeroDivisionError):
                    continue

                if val is None:
                    continue
                if abs(val) > MAX_VAL:
                    continue
                # Only keep if close to an integer
                rounded = round(val)
                if abs(val - rounded) < 1e-9 and rounded not in all_prev and rounded not in new_layer:
                    new_layer[float(rounded)] = expr
                elif abs(val - rounded) >= 1e-9:
                    # Keep non-integers too — they may combine in next step
                    if val not in all_prev and val not in new_layer:
                        new_layer[val] = expr

        layers.append(new_layer)

    # Collect all integer results
    all_vals = {}
    for layer in layers:
        for v, expr in layer.items():
            rounded = round(v)
            if abs(v - rounded) < 1e-9 and rounded not in all_vals:
                all_vals[rounded] = expr

    return all_vals


def analyze(operands, lo, hi, max_ops=2, ops=None, extended=False, targets=None):
    """Run reachability analysis and print results."""
    print('=' * 60)
    print('  Reachability Calculator')
    print('=' * 60)

    op_names = {'+': '+', '-': '-', '*': '*', '/': '/', '^': '^'}
    ops_used = ops if ops else ['+', '-', '*', '/', '^']
    ops_str = ', '.join(op_names.get(o, o) for o in ops_used)

    print(f'  Operands:   {{{", ".join(str(int(x)) if x == int(x) else str(x) for x in operands)}}}')
    print(f'  Operations: {ops_str}  (max {max_ops} ops)')
    print(f'  Extended:   {"yes (ln, exp, pi, e)" if extended else "no"}')
    print(f'  Range:      [{lo}, {hi}]')
    print()

    reachable = build_reachable(operands, max_ops=max_ops, ops=ops_used, extended=extended)

    # Filter to range
    in_range = {k: v for k, v in reachable.items() if lo <= k <= hi}
    total = hi - lo + 1
    count = len(in_range)
    pct = count / total * 100

    print(f'  Reachable:  {count}/{total} = {pct:.1f}%')
    print()

    # Show histogram by decade
    decade_size = max(1, (hi - lo + 1) // 10)
    print('  Distribution by sub-range:')
    print(f'  {"Range":<16} {"Reached":>8} {"Total":>8} {"Pct":>8}')
    print(f'  {"-"*16} {"-"*8} {"-"*8} {"-"*8}')
    for i in range(10):
        d_lo = lo + i * decade_size
        d_hi = min(d_lo + decade_size - 1, hi)
        if d_lo > hi:
            break
        d_count = sum(1 for k in in_range if d_lo <= k <= d_hi)
        d_total = d_hi - d_lo + 1
        bar = '#' * int(d_count / d_total * 30) if d_total > 0 else ''
        print(f'  [{d_lo:>4}-{d_hi:>4}]   {d_count:>8} {d_total:>8} {d_count/d_total*100:>7.1f}% {bar}')
    print()

    # Unreachable examples
    unreachable = sorted(k for k in range(lo, hi + 1) if k not in in_range)
    if unreachable:
        sample = unreachable[:15]
        print(f'  Unreachable examples: {", ".join(str(x) for x in sample)}{"..." if len(unreachable) > 15 else ""}')
        print(f'  Total unreachable: {len(unreachable)}')
    else:
        print('  All integers in range are reachable!')
    print()

    # Check specific targets
    if targets:
        print('  Target lookups:')
        for t in targets:
            t_int = int(t)
            if t_int in in_range:
                print(f'    {t_int}: REACHABLE via {in_range[t_int]}')
            elif t_int in reachable:
                print(f'    {t_int}: REACHABLE (outside range) via {reachable[t_int]}')
            else:
                print(f'    {t_int}: NOT REACHABLE with {max_ops} ops')
        print()

    # Summary for Texas Sharpshooter calibration
    print('  Texas Sharpshooter calibration:')
    print(f'    If you find a match to an integer in [{lo}, {hi}],')
    print(f'    the prior probability is {pct:.1f}% (baseline {count}/{total}).')
    if pct > 30:
        print(f'    WARNING: >30% reachable — single matches are NOT surprising.')
    elif pct > 15:
        print(f'    MODERATE: 15-30% reachable — matches are weakly interesting.')
    else:
        print(f'    LOW: <15% reachable — matches are genuinely notable.')
    print()
    print('=' * 60)

    return in_range, reachable


def main():
    parser = argparse.ArgumentParser(
        description='Reachability Calculator — what fraction of integers can be produced from operands')
    parser.add_argument('--operands', type=str, default='2,3,4,6,12',
                        help='Comma-separated operand set (default: 2,3,4,6,12 from P1=6)')
    parser.add_argument('--range', type=str, default='1-200', dest='range_str',
                        help='Target range lo-hi (default: 1-200)')
    parser.add_argument('--max-ops', type=int, default=2,
                        help='Maximum number of binary operations (default: 2)')
    parser.add_argument('--target', type=int, nargs='*', default=None,
                        help='Specific target integer(s) to check')
    parser.add_argument('--extended', action='store_true',
                        help='Include ln, exp, pi, e as extra operands')
    parser.add_argument('--ops', type=str, default=None,
                        help='Allowed operations, comma-separated (default: +,-,*,/,^)')
    args = parser.parse_args()

    operands = [float(x) for x in args.operands.split(',')]
    lo, hi = (int(x) for x in args.range_str.split('-'))
    ops = args.ops.split(',') if args.ops else None

    analyze(operands, lo, hi, max_ops=args.max_ops, ops=ops,
            extended=args.extended, targets=args.target)


if __name__ == '__main__':
    main()
