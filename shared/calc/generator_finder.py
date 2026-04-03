#!/usr/bin/env python3
"""Generator Finder — Minimal generating sets for convergence constants

Finds the smallest subset of constants that can approximate all other
convergence points through basic arithmetic operations (+, -, *, /, ^).

Based on H-CX-476: {zeta(3), ln(2)} generates 5/9 at depth 1, 10/10 at depth 2.

Usage:
  python3 calc/generator_finder.py --pair
  python3 calc/generator_finder.py --triple --depth 2
  python3 calc/generator_finder.py --custom "1.20206,0.69315" --depth 2
  python3 calc/generator_finder.py --pair --threshold 0.01
  python3 calc/generator_finder.py --pair --targets "0.5,1.41421,2.71828"
"""

import argparse
import math
import itertools
import sys

# ── Default convergence points ──────────────────────────────────────────────

DEFAULT_TARGETS = {
    'sqrt(2)':   math.sqrt(2),     # 1.41421
    'sqrt(3)':   math.sqrt(3),     # 1.73205
    '5/6':       5.0 / 6.0,        # 0.83333
    'e':         math.e,            # 2.71828
    'zeta(3)':   1.2020569031595942,# Apery's constant
    'ln(4/3)':   math.log(4.0/3),  # 0.28768
    'ln(2)':     math.log(2),      # 0.69315
    'gamma':     0.5772156649015329,# Euler-Mascheroni
    '1/2':       0.5,
    # Consciousness constants (from anima Laws 63-79)
    'Psi_steps':    3.0 / math.log(2),       # 4.328 consciousness evolution number
    'Psi_coupling': math.log(2) / 2**5.5,    # 0.01534 consciousness coupling
    'conservation': 0.478,                    # H^2 + dp^2 conservation
    'dynamics':     0.81,                     # dH/dt coefficient
    'tanh3_ln2':    math.tanh(3)*math.log(2), # 0.6895 consciousness saturation
}


def safe_pow(a, b):
    """Power with overflow/domain protection."""
    if a == 0 and b <= 0:
        return None
    if abs(b) > 20:
        return None
    if a < 0 and not float(b).is_integer():
        return None
    try:
        r = a ** b
        if abs(r) > 1e15 or math.isnan(r) or math.isinf(r):
            return None
        return r
    except (OverflowError, ValueError, ZeroDivisionError):
        return None


def binary_ops(a, b):
    """Return list of (value, expr_str) for all binary ops on a, b."""
    results = []
    results.append((a + b, '+'))
    results.append((a - b, '-'))
    results.append((b - a, 'r-'))  # reverse subtract
    results.append((a * b, '*'))
    if b != 0:
        results.append((a / b, '/'))
    if a != 0:
        results.append((b / a, 'r/'))  # reverse divide
    pw = safe_pow(a, b)
    if pw is not None:
        results.append((pw, '^'))
    pw2 = safe_pow(b, a)
    if pw2 is not None:
        results.append((pw2, 'r^'))
    return results


def format_binop(name_a, name_b, op):
    """Format a binary operation as human-readable string."""
    if op == '+':
        return f"{name_a} + {name_b}"
    elif op == '-':
        return f"{name_a} - {name_b}"
    elif op == 'r-':
        return f"{name_b} - {name_a}"
    elif op == '*':
        return f"{name_a} * {name_b}"
    elif op == '/':
        return f"{name_a} / {name_b}"
    elif op == 'r/':
        return f"{name_b} / {name_a}"
    elif op == '^':
        return f"{name_a} ^ {name_b}"
    elif op == 'r^':
        return f"{name_b} ^ {name_a}"
    return f"{name_a} ? {name_b}"


def generate_depth1(generators):
    """Generate all reachable values at depth 1.

    Args:
        generators: dict {name: value}

    Returns:
        dict {value: expression_str} (best/shortest expression per value)
    """
    reachable = {}
    names = list(generators.keys())
    vals = list(generators.values())

    # Generators themselves are reachable
    for n, v in generators.items():
        reachable[v] = n

    # All pairs (including same element with itself)
    for i in range(len(names)):
        for j in range(len(names)):
            for val, op in binary_ops(vals[i], vals[j]):
                if val is not None and not math.isnan(val) and not math.isinf(val):
                    expr = format_binop(names[i], names[j], op)
                    if val not in reachable or len(expr) < len(reachable[val]):
                        reachable[val] = expr

    return reachable


def generate_depth2(generators):
    """Generate all reachable values at depth 2.

    Depth 2 = apply binary ops to any two depth-1 results.
    To keep it tractable, we use depth-1 results as building blocks.
    """
    d1 = generate_depth1(generators)

    # Collect unique depth-1 values (limit to avoid combinatorial explosion)
    d1_items = list(d1.items())
    if len(d1_items) > 200:
        # Keep generators + best matches, sample rest
        d1_items = d1_items[:200]

    reachable = dict(d1)  # depth 2 includes depth 1

    vals = [(v, e) for v, e in d1_items]

    for i in range(len(vals)):
        for j in range(i, len(vals)):
            v_i, e_i = vals[i]
            v_j, e_j = vals[j]
            for val, op in binary_ops(v_i, v_j):
                if val is not None and not math.isnan(val) and not math.isinf(val):
                    expr = f"({e_i}) {op.replace('r', '')} ({e_j})"
                    if op.startswith('r'):
                        expr = f"({e_j}) {op[1:]} ({e_i})"
                    if val not in reachable:
                        reachable[val] = expr

    return reachable


def find_matches(reachable, targets, threshold):
    """Find which targets are matched by reachable values.

    Returns:
        list of (target_name, target_val, matched_val, expr, error)
    """
    matches = []
    for tname, tval in targets.items():
        best_err = float('inf')
        best_expr = None
        best_mval = None
        for rval, expr in reachable.items():
            err = abs(rval - tval)
            rel_err = err / abs(tval) if tval != 0 else err
            if rel_err < best_err:
                best_err = rel_err
                best_expr = expr
                best_mval = rval
        if best_err <= threshold:
            matches.append((tname, tval, best_mval, best_expr, best_err))
    return matches


def evaluate_generator_set(gen_names, gen_vals, targets, depth, threshold):
    """Evaluate a generator set: how many targets can it reach?"""
    generators = dict(zip(gen_names, gen_vals))

    # Remove generators that are also targets (they match trivially)
    non_trivial_targets = {k: v for k, v in targets.items()}

    if depth == 1:
        reachable = generate_depth1(generators)
    else:
        reachable = generate_depth2(generators)

    matches = find_matches(reachable, non_trivial_targets, threshold)
    return matches


def search_pairs(targets, depth, threshold):
    """Search all pairs from target set as generators."""
    names = list(targets.keys())
    vals = list(targets.values())
    n = len(names)

    results = []
    total = n * (n - 1) // 2
    count = 0

    for i in range(n):
        for j in range(i + 1, n):
            count += 1
            gen_names = [names[i], names[j]]
            gen_vals = [vals[i], vals[j]]
            matches = evaluate_generator_set(gen_names, gen_vals, targets, depth, threshold)
            results.append((gen_names, len(matches), matches))
            if count % 5 == 0:
                print(f"  Searching pairs... {count}/{total}", end='\r', flush=True)

    print(f"  Searched {total} pairs.             ")
    results.sort(key=lambda x: -x[1])
    return results


def search_triples(targets, depth, threshold):
    """Search all triples from target set as generators."""
    names = list(targets.keys())
    vals = list(targets.values())
    n = len(names)

    results = []
    total = n * (n - 1) * (n - 2) // 6
    count = 0

    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                count += 1
                gen_names = [names[i], names[j], names[k]]
                gen_vals = [vals[i], vals[j], vals[k]]
                matches = evaluate_generator_set(gen_names, gen_vals, targets, depth, threshold)
                results.append((gen_names, len(matches), matches))
                if count % 10 == 0:
                    print(f"  Searching triples... {count}/{total}", end='\r', flush=True)

    print(f"  Searched {total} triples.             ")
    results.sort(key=lambda x: -x[1])
    return results


def print_results(results, targets, depth, threshold, top_n=10):
    """Print ranked results table."""
    n_targets = len(targets)
    print(f"\n{'='*72}")
    print(f"  Generator Search Results  (depth={depth}, threshold={threshold:.4f})")
    print(f"  Targets: {n_targets}  |  {', '.join(targets.keys())}")
    print(f"{'='*72}\n")

    print(f"  {'Rank':<5} {'Generators':<35} {'Match':>5} / {n_targets}")
    print(f"  {'-'*5} {'-'*35} {'-'*10}")

    shown = min(top_n, len(results))
    for idx in range(shown):
        gen_names, n_match, matches = results[idx]
        gen_str = '{' + ', '.join(gen_names) + '}'
        print(f"  {idx+1:<5} {gen_str:<35} {n_match:>5} / {n_targets}")

    # Detail for top result
    if results:
        gen_names, n_match, matches = results[0]
        gen_str = '{' + ', '.join(gen_names) + '}'
        print(f"\n{'─'*72}")
        print(f"  Best generator set: {gen_str}")
        print(f"  Matches {n_match}/{n_targets} targets at depth {depth}\n")

        print(f"  {'Target':<12} {'Value':>10} {'Approx':>10} {'Error':>10} Expression")
        print(f"  {'-'*12} {'-'*10} {'-'*10} {'-'*10} {'-'*30}")

        for tname, tval, mval, expr, err in sorted(matches, key=lambda x: x[0]):
            print(f"  {tname:<12} {tval:>10.5f} {mval:>10.5f} {err:>10.6f} {expr}")

        # List unmatched
        matched_names = {m[0] for m in matches}
        unmatched = [k for k in targets if k not in matched_names]
        if unmatched:
            print(f"\n  Unmatched: {', '.join(unmatched)}")

    print()


def parse_targets(target_str):
    """Parse comma-separated values into target dict."""
    vals = [float(x.strip()) for x in target_str.split(',')]
    targets = {}
    for v in vals:
        # Try to find a nice name
        for name, default_val in DEFAULT_TARGETS.items():
            if abs(v - default_val) < 1e-4:
                targets[name] = v
                break
        else:
            targets[f"{v:.5f}"] = v
    return targets


def parse_custom_generators(custom_str):
    """Parse comma-separated generator values."""
    vals = [float(x.strip()) for x in custom_str.split(',')]
    generators = {}
    for v in vals:
        # Try to match known constant names
        for name, default_val in DEFAULT_TARGETS.items():
            if abs(v - default_val) < 1e-3:
                generators[name] = default_val
                break
        else:
            generators[f"{v:.5f}"] = v
    return generators


def main():
    parser = argparse.ArgumentParser(
        description='Generator Finder: minimal generating sets for convergence constants')
    parser.add_argument('--pair', action='store_true',
                        help='Find best generating pair from convergence points')
    parser.add_argument('--triple', action='store_true',
                        help='Find best generating triple')
    parser.add_argument('--custom', type=str, default=None,
                        help='Test custom generator set (comma-separated values)')
    parser.add_argument('--depth', type=int, default=1, choices=[1, 2],
                        help='Search depth (1 or 2, default: 1)')
    parser.add_argument('--threshold', type=float, default=0.005,
                        help='Match threshold as relative error (default: 0.005 = 0.5%%)')
    parser.add_argument('--targets', type=str, default=None,
                        help='Custom target list (comma-separated values)')

    args = parser.parse_args()

    # Build target set
    if args.targets:
        targets = parse_targets(args.targets)
    else:
        targets = dict(DEFAULT_TARGETS)

    print(f"\n  Generator Finder v1.0")
    print(f"  H-CX-476: Minimal generating sets for convergence constants")
    print(f"  Depth: {args.depth}  |  Threshold: {args.threshold:.4f} ({args.threshold*100:.1f}%)")
    print(f"  Targets ({len(targets)}): {', '.join(targets.keys())}")

    if not (args.pair or args.triple or args.custom):
        print("\n  No mode selected. Use --pair, --triple, or --custom.")
        print("  Example: python3 calc/generator_finder.py --pair")
        parser.print_help()
        return

    if args.custom:
        generators = parse_custom_generators(args.custom)
        print(f"\n  Custom generators: {{{', '.join(generators.keys())}}}")
        matches = evaluate_generator_set(
            list(generators.keys()), list(generators.values()),
            targets, args.depth, args.threshold)
        # Format as results list for print_results
        results = [(list(generators.keys()), len(matches), matches)]
        print_results(results, targets, args.depth, args.threshold, top_n=1)

    if args.pair:
        print(f"\n  Searching all pairs...")
        results = search_pairs(targets, args.depth, args.threshold)
        print_results(results, targets, args.depth, args.threshold, top_n=10)

    if args.triple:
        print(f"\n  Searching all triples...")
        results = search_triples(targets, args.depth, args.threshold)
        print_results(results, targets, args.depth, args.threshold, top_n=10)


if __name__ == '__main__':
    main()
