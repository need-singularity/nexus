#!/usr/bin/env python3
"""Integer Sequence Scanner — Find n=6 characterizations in ANY sequence

Usage:
  python3 calc/sequence_scanner.py
  python3 calc/sequence_scanner.py --n 6 --range 500
  python3 calc/sequence_scanner.py --custom 1,1,2,3,5,8,13,21,34,55,89,144
"""
import sys, os, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sympy import (divisor_sigma, totient, divisor_count, factorint,
                   binomial, factorial, fibonacci)
import math


def n_constants(n=6):
    s = int(divisor_sigma(n))
    p = int(totient(n))
    t = int(divisor_count(n))
    sopfr = sum(pr * e for pr, e in factorint(n).items())
    return {
        'n': n, 'sigma': s, 'phi': p, 'tau': t, 'sopfr': sopfr,
        'sigma*phi': s * p, 'sigma*tau': s * t, 'sigma-tau': s - t,
        'sigma/tau': s // t if t > 0 and s % t == 0 else None,
        'n^2': n ** 2, 'n!': math.factorial(n),
        'C(n,2)': n * (n - 1) // 2, 'T(n)': n * (n + 1) // 2,
    }


def builtin_sequences():
    """Return dictionary of named sequences."""
    seqs = {}

    # Fibonacci
    fib = [0, 1]
    for _ in range(48): fib.append(fib[-1] + fib[-2])
    seqs['Fibonacci'] = fib

    # Lucas
    luc = [2, 1]
    for _ in range(48): luc.append(luc[-1] + luc[-2])
    seqs['Lucas'] = luc

    # Pell
    pell = [0, 1]
    for _ in range(30): pell.append(2 * pell[-1] + pell[-2])
    seqs['Pell'] = pell

    # Tribonacci
    trib = [0, 0, 1]
    for _ in range(30): trib.append(trib[-1] + trib[-2] + trib[-3])
    seqs['Tribonacci'] = trib

    # Padovan
    pad = [1, 1, 1]
    for _ in range(30): pad.append(pad[-2] + pad[-3])
    seqs['Padovan'] = pad

    # Motzkin
    motz = [1, 1]
    for k in range(2, 20):
        motz.append(((2 * k + 1) * motz[-1] + 3 * (k - 1) * motz[-2]) // (k + 2))
    seqs['Motzkin'] = motz

    # Catalan
    cat = [1]
    for k in range(1, 20):
        cat.append(cat[-1] * 2 * (2 * k - 1) // (k + 1))
    seqs['Catalan'] = cat

    # Bell
    from sympy.functions.combinatorial.numbers import bell
    seqs['Bell'] = [int(bell(k)) for k in range(15)]

    # Tetranacci
    tetra = [0, 0, 0, 1]
    for _ in range(20): tetra.append(sum(tetra[-4:]))
    seqs['Tetranacci'] = tetra

    return seqs


def scan_sequence(name, seq, constants, max_check=200):
    """Scan a sequence for n=6 characterizations."""
    hits = []
    const_names = {v: k for k, v in constants.items() if v is not None and isinstance(v, int) and v > 1}

    for idx in range(len(seq)):
        val = seq[idx]
        if val in const_names:
            # Check if the index is also a constant
            idx_name = const_names.get(idx, str(idx))
            val_name = const_names[val]
            hits.append((idx, idx_name, val, val_name))

    # Check: seq[const] = const (at constant indices, value is also constant)
    for const_name, const_val in constants.items():
        if const_val is not None and isinstance(const_val, int) and 0 <= const_val < len(seq):
            val = seq[const_val]
            if val in const_names:
                val_name = const_names[val]
                hits.append((const_val, const_name, val, val_name))

    # Check: seq[const] = const^2 or other compositions
    for const_name, const_val in constants.items():
        if const_val is not None and isinstance(const_val, int) and 0 <= const_val < len(seq):
            val = seq[const_val]
            if val == const_val ** 2:
                hits.append((const_val, const_name, val, f'{const_name}^2'))

    # Uniqueness check for best hits
    unique_hits = []
    for idx, idx_name, val, val_name in hits:
        # Count how many n have seq[f(n)] = g(n) for same f,g
        count = 0
        for nn in range(2, min(max_check, len(seq))):
            c2 = n_constants(nn)
            for cn, cv in c2.items():
                if cv == idx and cv is not None and isinstance(cv, int) and 0 <= cv < len(seq):
                    if seq[cv] == val:
                        count += 1
        unique_hits.append((idx, idx_name, val, val_name, count))

    return unique_hits


def main():
    parser = argparse.ArgumentParser(description='Integer Sequence Scanner')
    parser.add_argument('--n', type=int, default=6)
    parser.add_argument('--range', type=int, default=200)
    parser.add_argument('--custom', type=str, help='Comma-separated custom sequence')
    args = parser.parse_args()

    constants = n_constants(args.n)
    print(f"{'=' * 60}")
    print(f"  Integer Sequence Scanner — n = {args.n}")
    print(f"{'=' * 60}")
    print(f"  Constants: {', '.join(f'{k}={v}' for k, v in constants.items() if v is not None)}")
    print()

    if args.custom:
        seqs = {'Custom': list(map(int, args.custom.split(',')))}
    else:
        seqs = builtin_sequences()

    for name, seq in seqs.items():
        hits = scan_sequence(name, seq, constants, args.range)
        if hits:
            print(f"  {name}:")
            seen = set()
            for idx, idx_name, val, val_name, count in hits:
                key = (idx, val)
                if key not in seen:
                    seen.add(key)
                    uniq = 'UNIQUE' if count <= 1 else f'{count} hits'
                    print(f"    [{name}]({idx_name}={idx}) = {val} = {val_name}  ({uniq})")
            print()

    print(f"{'=' * 60}")


if __name__ == '__main__':
    main()
