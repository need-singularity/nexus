#!/usr/bin/env python3
"""Q-Domain Barrier Checker — Which constants can quantum coupling constants reach?

Analyzes reachability of target constants from the Q-domain (quantum coupling
constants) via arithmetic operations (+, -, *, /, ^) at depth 1 and 2.
Based on H-CX-493/500.

Usage:
  python3 q_barrier_checker.py --target 0.5
  python3 q_barrier_checker.py --target-name GZ_upper
  python3 q_barrier_checker.py --gz
  python3 q_barrier_checker.py --all
  python3 q_barrier_checker.py --classify
  python3 q_barrier_checker.py --depth 3 --gz
"""

import argparse
import math
import itertools
import random
from collections import defaultdict

# ── Q-domain constants ──────────────────────────────────────────────────────

Q_CONSTANTS = {
    "1/alpha":      137.035999084,
    "alpha":        1 / 137.035999084,
    "alpha_s":      0.1185,
    "sin2_thetaW":  0.231,
    "g_e-2":        0.00232,
    "m_e/m_p":      0.000544617,
    "m_e/m_mu":     0.00483633,
    "N_gen":        3.0,
    "CMB":          2.7255,
    "17":           17.0,
}

# ── Target constants ────────────────────────────────────────────────────────

GZ_TARGETS = {
    "GZ_upper":      0.5,
    "GZ_width":      math.log(4 / 3),
    "GZ_lower":      0.5 - math.log(4 / 3),
    "GZ_center":     1 / math.e,
    "compass_upper": 5 / 6,
    "meta_fixed":    1 / 3,
}

STANDARD_TARGETS = {
    **GZ_TARGETS,
    "sqrt2":    math.sqrt(2),
    "sqrt3":    math.sqrt(3),
    "e":        math.e,
    "pi":       math.pi,
    "ln2":      math.log(2),
    "gamma":    0.5772156649,
    "zeta3":    1.2020569031,
    "phi":      (1 + math.sqrt(5)) / 2,
    "1/6":      1 / 6,
    "1":        1.0,
    "2":        2.0,
    "6":        6.0,
}

TARGET_CATEGORIES = {
    "GZ_upper":      "rational",
    "GZ_width":      "analytic_limit",
    "GZ_lower":      "analytic_limit",
    "GZ_center":     "analytic_limit",
    "compass_upper": "rational",
    "meta_fixed":    "rational",
    "sqrt2":         "algebraic_irrational",
    "sqrt3":         "algebraic_irrational",
    "e":             "analytic_limit",
    "pi":            "analytic_limit",
    "ln2":           "analytic_limit",
    "gamma":         "analytic_limit",
    "zeta3":         "analytic_limit",
    "phi":           "algebraic_irrational",
    "1/6":           "rational",
    "1":             "rational",
    "2":             "rational",
    "6":             "rational",
}

# ── Operations ───────────────────────────────────────────────────────────────

def safe_ops(a, b):
    """Return dict of {op_name: result} for a op b, skipping invalid."""
    results = {}
    results["a+b"] = a + b
    results["a-b"] = a - b
    results["b-a"] = b - a
    results["a*b"] = a * b
    if b != 0:
        results["a/b"] = a / b
    if a != 0:
        results["b/a"] = b / a
    # Power: only for small exponents to avoid overflow
    try:
        if abs(b) < 50 and abs(a) < 1e6 and a > 0:
            val = a ** b
            if math.isfinite(val) and abs(val) < 1e15:
                results["a^b"] = val
    except (OverflowError, ValueError):
        pass
    try:
        if abs(a) < 50 and abs(b) < 1e6 and b > 0:
            val = b ** a
            if math.isfinite(val) and abs(val) < 1e15:
                results["b^a"] = val
    except (OverflowError, ValueError):
        pass
    return results


def unary_ops(a):
    """Unary transforms of a single constant."""
    results = {"id": a}
    if a > 0:
        results["sqrt"] = math.sqrt(a)
        results["ln"] = math.log(a)
    results["inv"] = 1 / a if a != 0 else None
    results["sq"] = a * a
    results = {k: v for k, v in results.items() if v is not None and math.isfinite(v)}
    return results


# ── Reachability engine ─────────────────────────────────────────────────────

def build_depth1(q_vals):
    """All values reachable at depth 1: unary(q) or q_i op q_j."""
    reachable = {}  # value -> expression string

    names = list(q_vals.keys())
    vals = list(q_vals.values())

    # Unary on each
    for i, (n, v) in enumerate(zip(names, vals)):
        for op, r in unary_ops(v).items():
            expr = f"{op}({n})" if op != "id" else n
            reachable[r] = expr

    # Pairwise (including self-pairs)
    for i in range(len(names)):
        for j in range(i, len(names)):
            for op, r in safe_ops(vals[i], vals[j]).items():
                expr = f"{names[i]} {op.replace('a','').replace('b','')} {names[j]}"
                # Nicer expression
                expr = f"({names[i]} op {names[j]})[{op}]"
                reachable[r] = f"{names[i]} {op} {names[j]}"

    return reachable


def build_depth2(depth1_vals, q_vals):
    """Depth 2: combine depth-1 results with Q constants or with each other."""
    reachable = dict(depth1_vals)

    d1_items = list(depth1_vals.items())[:500]  # cap for performance
    q_items = list(q_vals.items())

    # depth1 op Q
    for val1, expr1 in d1_items:
        for qname, qval in q_items:
            for op, r in safe_ops(val1, qval).items():
                if r not in reachable:
                    reachable[r] = f"({expr1}) {op} {qname}"

    # depth1 op depth1 (sample to keep tractable)
    sample = d1_items[:200]
    for i in range(len(sample)):
        for j in range(i, min(i + 50, len(sample))):
            val1, expr1 = sample[i]
            val2, expr2 = sample[j]
            for op, r in safe_ops(val1, val2).items():
                if r not in reachable:
                    reachable[r] = f"({expr1}) {op} ({expr2})"

    return reachable


def check_target(target_val, reachable, threshold=0.005):
    """Check if target is reachable within relative threshold."""
    best_dist = float('inf')
    best_expr = None
    best_val = None

    for val, expr in reachable.items():
        if target_val == 0:
            dist = abs(val)
        else:
            dist = abs(val - target_val) / abs(target_val)
        if dist < best_dist:
            best_dist = dist
            best_expr = expr
            best_val = val

    hit = best_dist < threshold
    return hit, best_dist, best_val, best_expr


# ── Display ──────────────────────────────────────────────────────────────────

def print_header(title):
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}")


def run_gz(args):
    """Check Golden Zone constants."""
    print_header("Q-Domain Barrier: Golden Zone Constants")
    print(f"  Depth: {args.depth}   Threshold: {args.threshold * 100:.1f}%")
    print(f"  Q-domain: {len(Q_CONSTANTS)} quantum constants")

    depth1 = build_depth1(Q_CONSTANTS)
    reachable = depth1
    if args.depth >= 2:
        reachable = build_depth2(depth1, Q_CONSTANTS)

    print(f"  Reachable values generated: {len(reachable)}")
    print()
    print(f"  {'Target':<16} {'Value':>10} {'Status':<10} {'Best Match':>10} {'Error':>10}  Expression")
    print(f"  {'-'*16} {'-'*10} {'-'*10} {'-'*10} {'-'*10}  {'-'*30}")

    blocked = 0
    for name, val in GZ_TARGETS.items():
        hit, dist, best_val, expr = check_target(val, reachable, args.threshold)
        status = "REACHABLE" if hit else "BLOCKED"
        marker = "  " if hit else "XX"
        if not hit:
            blocked += 1
        bv = f"{best_val:.6f}" if best_val is not None else "---"
        print(f"  {name:<16} {val:>10.6f} {status:<10} {bv:>10} {dist:>10.4%}  {expr or '---'}")

    print()
    print(f"  Summary: {blocked}/{len(GZ_TARGETS)} Golden Zone constants BLOCKED from Q-domain")
    print(f"  Barrier rate: {blocked/len(GZ_TARGETS)*100:.0f}%")
    return blocked


def run_all(args):
    """Check all standard targets."""
    print_header("Q-Domain Barrier: All Standard Targets")
    print(f"  Depth: {args.depth}   Threshold: {args.threshold * 100:.1f}%")

    depth1 = build_depth1(Q_CONSTANTS)
    reachable = depth1
    if args.depth >= 2:
        reachable = build_depth2(depth1, Q_CONSTANTS)

    print(f"  Reachable values generated: {len(reachable)}")
    print()
    print(f"  {'Target':<16} {'Value':>10} {'Status':<10} {'Error':>10}")
    print(f"  {'-'*16} {'-'*10} {'-'*10} {'-'*10}")

    results = {}
    for name, val in STANDARD_TARGETS.items():
        hit, dist, best_val, expr = check_target(val, reachable, args.threshold)
        status = "REACHABLE" if hit else "BLOCKED"
        results[name] = (hit, dist)
        print(f"  {name:<16} {val:>10.6f} {status:<10} {dist:>10.4%}")

    reached = sum(1 for h, _ in results.values() if h)
    blocked = len(results) - reached
    print()
    print(f"  Reachable: {reached}/{len(results)}")
    print(f"  Blocked:   {blocked}/{len(results)}")
    print(f"  Barrier rate: {blocked/len(results)*100:.0f}%")


def run_classify(args):
    """Classify blocked targets by mathematical category."""
    print_header("Q-Domain Barrier: Classification of Blocked Targets")

    depth1 = build_depth1(Q_CONSTANTS)
    reachable = depth1
    if args.depth >= 2:
        reachable = build_depth2(depth1, Q_CONSTANTS)

    categories = defaultdict(list)
    for name, val in STANDARD_TARGETS.items():
        hit, dist, _, _ = check_target(val, reachable, args.threshold)
        cat = TARGET_CATEGORIES.get(name, "unknown")
        categories[cat].append((name, val, hit, dist))

    for cat in ["rational", "algebraic_irrational", "analytic_limit"]:
        items = categories.get(cat, [])
        if not items:
            continue
        blocked = [x for x in items if not x[2]]
        reached = [x for x in items if x[2]]
        print(f"\n  Category: {cat}")
        print(f"    Blocked: {len(blocked)}/{len(items)}")
        for name, val, hit, dist in items:
            status = "OK" if hit else "XX"
            print(f"      [{status}] {name:<16} = {val:.6f}  (min error: {dist:.4%})")

    print()
    # Summary table
    print(f"  {'Category':<25} {'Total':>6} {'Blocked':>8} {'Rate':>8}")
    print(f"  {'-'*25} {'-'*6} {'-'*8} {'-'*8}")
    for cat in ["rational", "algebraic_irrational", "analytic_limit"]:
        items = categories.get(cat, [])
        blocked = sum(1 for x in items if not x[2])
        print(f"  {cat:<25} {len(items):>6} {blocked:>8} {blocked/max(len(items),1)*100:>7.0f}%")


def run_target(args):
    """Check a single target."""
    if args.target_name:
        if args.target_name in STANDARD_TARGETS:
            val = STANDARD_TARGETS[args.target_name]
            name = args.target_name
        else:
            print(f"  Unknown target name: {args.target_name}")
            print(f"  Available: {', '.join(STANDARD_TARGETS.keys())}")
            return
    else:
        val = args.target
        name = f"custom({val})"

    print_header(f"Q-Domain Barrier Check: {name} = {val:.8f}")

    depth1 = build_depth1(Q_CONSTANTS)
    reachable = depth1
    print(f"  Depth 1: {len(reachable)} reachable values")
    hit1, dist1, bv1, expr1 = check_target(val, reachable, args.threshold)
    print(f"    Best match: {bv1:.8f}  error={dist1:.6%}")
    print(f"    Expression: {expr1}")
    print(f"    Status: {'REACHABLE' if hit1 else 'BLOCKED'} at depth 1")

    if args.depth >= 2:
        reachable = build_depth2(depth1, Q_CONSTANTS)
        print(f"\n  Depth 2: {len(reachable)} reachable values")
        hit2, dist2, bv2, expr2 = check_target(val, reachable, args.threshold)
        print(f"    Best match: {bv2:.8f}  error={dist2:.6%}")
        print(f"    Expression: {expr2}")
        print(f"    Status: {'REACHABLE' if hit2 else 'BLOCKED'} at depth 2")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Q-Domain Barrier Checker")
    parser.add_argument("--target", type=float, help="Check if Q can reach this value")
    parser.add_argument("--target-name", type=str, help="Check named target (e.g. GZ_upper)")
    parser.add_argument("--gz", action="store_true", help="Check all 6 Golden Zone constants")
    parser.add_argument("--all", action="store_true", help="Check all standard targets")
    parser.add_argument("--classify", action="store_true", help="Classify blocked targets by category")
    parser.add_argument("--depth", type=int, default=2, help="Max operation depth (default 2)")
    parser.add_argument("--threshold", type=float, default=0.005, help="Match threshold (default 0.5%%)")

    args = parser.parse_args()

    if args.gz:
        run_gz(args)
    elif args.all:
        run_all(args)
    elif args.classify:
        run_classify(args)
    elif args.target is not None or args.target_name:
        run_target(args)
    else:
        # Default: show GZ
        run_gz(args)


if __name__ == "__main__":
    main()
