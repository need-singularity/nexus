#!/usr/bin/env python3
"""Cross-Constant Explorer -- Find relationships between GZ constants

Systematically explores arithmetic combinations of GZ constants
and matches against known mathematical constants.

GZ constant pool:
  1/2, 1/3, 1/6, 1/e, ln(4/3), 5/6, ln(2), ln(3)

Operations: +, -, *, /, ^, log_base

Usage:
  python3 calc/cross_constant_explorer.py                  # Full exploration
  python3 calc/cross_constant_explorer.py --depth 2        # Depth-2 compositions
  python3 calc/cross_constant_explorer.py --target 0.693   # Find expressions near target
  python3 calc/cross_constant_explorer.py --self-ref       # x^x analysis for all GZ constants
"""

import argparse
import math
import itertools
import sys


# ═══════════════════════════════════════════════════════════════
# Constant pools
# ═══════════════════════════════════════════════════════════════

GZ_POOL = {
    "1/2":      0.5,
    "1/3":      1.0 / 3.0,
    "1/6":      1.0 / 6.0,
    "1/e":      1.0 / math.e,
    "ln(4/3)":  math.log(4.0 / 3.0),
    "5/6":      5.0 / 6.0,
    "ln(2)":    math.log(2.0),
    "ln(3)":    math.log(3.0),
    "Psi_steps": 3.0 / math.log(2.0),      # 4.328 consciousness evolution number
    "Psi_balance": 0.5,                      # consciousness balance point
    "Psi_coupling": math.log(2.0) / 2**5.5,  # 0.01534 consciousness coupling
    "Psi_K": 11.0,                           # consciousness carrying capacity
    "Psi_freedom": math.log(2.0),            # 0.6931 Law 79 consciousness freedom degree
}

KNOWN_CONSTANTS = {
    "0":        0.0,
    "1":        1.0,
    "2":        2.0,
    "1/2":      0.5,
    "1/3":      1.0 / 3.0,
    "1/6":      1.0 / 6.0,
    "5/6":      5.0 / 6.0,
    "2/3":      2.0 / 3.0,
    "pi":       math.pi,
    "e":        math.e,
    "1/e":      1.0 / math.e,
    "ln(2)":    math.log(2.0),
    "ln(3)":    math.log(3.0),
    "ln(4/3)":  math.log(4.0 / 3.0),
    "sqrt(2)":  math.sqrt(2.0),
    "sqrt(3)":  math.sqrt(3.0),
    "sqrt(5)":  math.sqrt(5.0),
    "phi":      (1.0 + math.sqrt(5.0)) / 2.0,
    "1/phi":    2.0 / (1.0 + math.sqrt(5.0)),
    "gamma":    0.5772156649015329,
    "pi/4":     math.pi / 4.0,
    "pi/2":     math.pi / 2.0,
    "pi/6":     math.pi / 6.0,
    "1-1/e":    1.0 - 1.0 / math.e,
    "2/e":      2.0 / math.e,
    "e-2":      math.e - 2.0,
    "e-1":      math.e - 1.0,
    "zeta(3)":  1.2020569031595942,
    "ln(2)^2":  math.log(2.0)**2,
    "3/ln(2)":  3.0 / math.log(2.0),
    "ln(2)/2^5.5": math.log(2.0) / 2**5.5,
    "tanh(3)*ln(2)": math.tanh(3.0) * math.log(2.0),
    "0.478":    0.478,   # H^2+dp^2 conservation
    "0.81":     0.81,    # dynamics rate dH/dt coefficient
    "11":       11.0,    # Psi_K carrying capacity
    "7.82":     7.82,    # Psi_emergence hivemind ratio
}

TOLERANCE = 1e-5


def match_known(val, tol=TOLERANCE):
    """Return list of known constant names close to val."""
    if not math.isfinite(val):
        return []
    matches = []
    for name, cval in KNOWN_CONSTANTS.items():
        if abs(val - cval) <= tol:
            matches.append((name, cval, abs(val - cval)))
    matches.sort(key=lambda x: x[2])
    return matches


# ═══════════════════════════════════════════════════════════════
# Operations
# ═══════════════════════════════════════════════════════════════

def safe_ops(a_name, a_val, b_name, b_val):
    """Generate all operations (a, b) -> (expr_name, result_val)."""
    results = []

    def add(x, y):
        return x + y
    def sub(x, y):
        return x - y
    def mul(x, y):
        return x * y
    def div_fn(x, y):
        return x / y if abs(y) > 1e-15 else float('nan')
    def pow_fn(x, y):
        if x <= 0:
            return float('nan')
        return x ** y
    def log_b(x, y):
        if x <= 0 or y <= 0 or abs(y - 1) < 1e-10:
            return float('nan')
        return math.log(x) / math.log(y)

    ops = [
        ("+",    add),
        ("-",    sub),
        ("*",    mul),
        ("/",    div_fn),
        ("^",    pow_fn),
        ("log_", log_b),
    ]
    for sym, fn in ops:
        try:
            if sym == "log_":
                val = fn(a_val, b_val)
                name = f"log_{b_name}({a_name})"
                val2 = fn(b_val, a_val)
                name2 = f"log_{a_name}({b_name})"
                if math.isfinite(val):
                    results.append((name, val))
                if math.isfinite(val2):
                    results.append((name2, val2))
            else:
                val = fn(a_val, b_val)
                name = f"({a_name}{sym}{b_name})"
                if math.isfinite(val):
                    results.append((name, val))
                if sym not in ("+", "*"):
                    # Also try reversed for non-commutative ops
                    val_r = fn(b_val, a_val)
                    name_r = f"({b_name}{sym}{a_name})"
                    if math.isfinite(val_r):
                        results.append((name_r, val_r))
        except Exception:
            pass
    return results


# ═══════════════════════════════════════════════════════════════
# Depth-1 exploration
# ═══════════════════════════════════════════════════════════════

def explore_depth1():
    pool = list(GZ_POOL.items())
    results = []
    for i, (a_name, a_val) in enumerate(pool):
        for j, (b_name, b_val) in enumerate(pool):
            if i >= j:
                continue  # avoid duplicate pairs for symmetric ops
            ops = safe_ops(a_name, a_val, b_name, b_val)
            for expr_name, expr_val in ops:
                matches = match_known(expr_val)
                if matches:
                    for m_name, m_val, err in matches:
                        results.append((expr_name, expr_val, m_name, err))
    return results


# ═══════════════════════════════════════════════════════════════
# Depth-2 exploration (compose depth-1 with pool)
# ═══════════════════════════════════════════════════════════════

def explore_depth2(depth1_results=None):
    if depth1_results is None:
        depth1_results = explore_depth1()
    pool = list(GZ_POOL.items())
    results = []
    # Compose: (depth-1 result) op (pool element)
    for expr_name, expr_val, _, _ in depth1_results[:50]:  # limit to top 50 to avoid explosion
        for b_name, b_val in pool:
            ops = safe_ops(expr_name, expr_val, b_name, b_val)
            for new_name, new_val in ops:
                matches = match_known(new_val)
                if matches:
                    for m_name, m_val, err in matches[:1]:
                        results.append((new_name, new_val, m_name, err))
    return results


# ═══════════════════════════════════════════════════════════════
# Self-reference: x^x for each GZ constant
# ═══════════════════════════════════════════════════════════════

def self_ref_analysis():
    print()
    print("  x^x Self-Reference Analysis for GZ Constants")
    print("  " + "=" * 62)
    print(f"  {'Constant':>12}  {'x':>8}  {'x^x':>10}  {'ln(x^x)=x*ln(x)':>18}  GZ Match")
    print("  " + "-" * 72)

    ln2 = math.log(2.0)
    results = []
    for name, val in sorted(GZ_POOL.items(), key=lambda x: x[1]):
        if val <= 0:
            continue
        xx = val ** val
        x_ln_x = val * math.log(val)
        matches = match_known(xx)
        match_str = ", ".join(m[0] for m in matches) if matches else ""
        results.append((name, val, xx, x_ln_x, match_str))
        print(f"  {name:>12}  {val:8.5f}  {xx:10.6f}  {x_ln_x:18.6f}  {match_str}")

    # Show clustering near ln(2)
    print()
    print(f"  Reference: ln(2) = {ln2:.6f}")
    print()
    print("  Distance of x^x from ln(2):")
    for name, val, xx, _, _ in results:
        dist = abs(xx - ln2)
        bar = "#" * int(min(dist * 200, 40))
        print(f"  {name:>12}  |{xx:.6f} - ln(2)| = {dist:.6f}  {bar}")

    print()
    print("  Note: 1/e^(1/e) = e^(-1/e) is the global minimum of x^x.")
    min_val = math.e ** (-1.0 / math.e)
    print(f"  (1/e)^(1/e)  = {min_val:.6f}  (x^x minimum at x=1/e)")


# ═══════════════════════════════════════════════════════════════
# Target finder
# ═══════════════════════════════════════════════════════════════

def find_near_target(target, depth=1, tol=0.005):
    pool = list(GZ_POOL.items())
    results = []
    # Depth 1
    for i, (a_name, a_val) in enumerate(pool):
        for j, (b_name, b_val) in enumerate(pool):
            if i >= j:
                continue
            for expr_name, expr_val in safe_ops(a_name, a_val, b_name, b_val):
                err = abs(expr_val - target)
                if err <= tol:
                    results.append((err, expr_name, expr_val))

    # Self-ops (x op x)
    for a_name, a_val in pool:
        for expr_name, expr_val in safe_ops(a_name, a_val, a_name, a_val):
            err = abs(expr_val - target)
            if err <= tol:
                results.append((err, expr_name, expr_val))

    results.sort(key=lambda x: x[0])
    return results


def print_target_search(target):
    results = find_near_target(target, tol=0.01)
    print()
    print(f"  Expressions closest to target = {target}")
    print("  " + "=" * 55)
    if not results:
        print(f"  No expressions within 1% of {target}")
        return
    print(f"  {'Expression':<40}  {'Value':>10}  {'Error':>10}")
    print("  " + "-" * 65)
    for err, name, val in results[:20]:
        print(f"  {name:<40}  {val:10.6f}  {err:10.6f}")


# ═══════════════════════════════════════════════════════════════
# Full exploration printer
# ═══════════════════════════════════════════════════════════════

def print_full(depth=1):
    print()
    print("  ╔══════════════════════════════════════════════════════╗")
    print("  ║        Cross-Constant Explorer                       ║")
    print("  ║        GZ constant relationships (H-CX-504)          ║")
    print("  ╚══════════════════════════════════════════════════════╝")
    print()
    print("  GZ Constant Pool")
    print("  " + "-" * 40)
    for name, val in sorted(GZ_POOL.items(), key=lambda x: x[1]):
        print(f"  {name:>12}  =  {val:.8f}")
    print()

    d1 = explore_depth1()
    d1_unique = {}
    for expr_name, expr_val, m_name, err in d1:
        key = (round(expr_val, 8), m_name)
        if key not in d1_unique or err < d1_unique[key][3]:
            d1_unique[key] = (expr_name, expr_val, m_name, err)
    d1_sorted = sorted(d1_unique.values(), key=lambda x: x[3])

    print(f"  Depth-1 Results: {len(d1_sorted)} unique matches")
    print("  " + "=" * 65)
    print(f"  {'Expression':<30}  {'Value':>10}  {'Matches':>15}  {'Error':>10}")
    print("  " + "-" * 75)
    for expr_name, expr_val, m_name, err in d1_sorted[:40]:
        print(f"  {expr_name:<30}  {expr_val:10.6f}  {m_name:>15}  {err:10.2e}")

    if depth >= 2:
        print()
        d2 = explore_depth2(d1)
        d2_unique = {}
        for expr_name, expr_val, m_name, err in d2:
            key = (round(expr_val, 8), m_name)
            if key not in d2_unique or err < d2_unique[key][3]:
                d2_unique[key] = (expr_name, expr_val, m_name, err)
        d2_sorted = sorted(d2_unique.values(), key=lambda x: x[3])

        print(f"  Depth-2 Results: {len(d2_sorted)} unique matches (new discoveries)")
        print("  " + "=" * 65)
        print(f"  {'Expression':<38}  {'Value':>10}  {'Matches':>15}  {'Error':>10}")
        print("  " + "-" * 80)
        for expr_name, expr_val, m_name, err in d2_sorted[:30]:
            print(f"  {expr_name:<38}  {expr_val:10.6f}  {m_name:>15}  {err:10.2e}")


# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Cross-Constant Explorer -- algebraic relationships between GZ constants"
    )
    parser.add_argument("--depth", type=int, default=1, choices=[1, 2],
                        help="Exploration depth (1 or 2, default: 1)")
    parser.add_argument("--target", type=float, metavar="VAL",
                        help="Find GZ expressions closest to target value")
    parser.add_argument("--self-ref", action="store_true",
                        help="x^x analysis for all GZ constants")
    args = parser.parse_args()

    if args.self_ref:
        self_ref_analysis()
    elif args.target is not None:
        print_target_search(args.target)
    else:
        print_full(depth=args.depth)


if __name__ == "__main__":
    main()
