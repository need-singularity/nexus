#!/usr/bin/env python3
"""Depth Reachability Analyzer — H-CX-463/467

Analyzes how reachability changes with depth for a specific domain.
Shows which targets become reachable at each depth level and
what expressions reach them.

Depth levels:
  0: Raw constants (direct match)
  1: Unary ops + binary ops on pairs of base constants
  2: binary_ops(depth1_result, base_constant)
  3: binary_ops(depth2_result, base_constant)

Usage:
  python3 calc/depth_reachability.py --domain S --depth 2
  python3 calc/depth_reachability.py --domain Q --depth 3
  python3 calc/depth_reachability.py --domain N --depth 2 --threshold 0.0001
"""

import argparse
import sys
import os
import warnings
from collections import defaultdict

import numpy as np

warnings.filterwarnings("ignore", category=RuntimeWarning)

# Import DOMAINS from convergence_engine.py
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from convergence_engine import DOMAINS

# ═══════════════════════════════════════════════════════════════
# 9 default convergence targets
# ═══════════════════════════════════════════════════════════════

DEFAULT_TARGETS = {
    "sqrt(2)":  np.sqrt(2),
    "sqrt(3)":  np.sqrt(3),
    "5/6":      5.0 / 6.0,
    "e":        np.e,
    "zeta(3)":  1.2020569031,
    "ln(4/3)":  np.log(4.0 / 3.0),
    "ln(2)":    np.log(2),
    "gamma_EM": 0.5772156649,
    "1/2":      0.5,
}

# ═══════════════════════════════════════════════════════════════
# Binary and unary operations
# ═══════════════════════════════════════════════════════════════

def binary_ops(na, va, nb, vb):
    """All binary operations on two values. Returns [(value, expr), ...]"""
    results = []

    def _add(v, expr):
        if isinstance(v, (int, float)) and np.isfinite(v) and 1e-15 < abs(v) < 1e12:
            results.append((v, expr))

    _add(va + vb, f"({na}+{nb})")
    _add(va - vb, f"({na}-{nb})")
    _add(vb - va, f"({nb}-{na})")
    _add(va * vb, f"({na}*{nb})")

    if vb != 0:
        _add(va / vb, f"({na}/{nb})")
    if va != 0:
        _add(vb / va, f"({nb}/{na})")

    if va > 0 and abs(vb) < 20:
        try:
            _add(va ** vb, f"({na}^{nb})")
        except (OverflowError, ValueError):
            pass
    if vb > 0 and abs(va) < 20:
        try:
            _add(vb ** va, f"({nb}^{na})")
        except (OverflowError, ValueError):
            pass

    if va > 0 and va != 1 and vb > 0:
        try:
            _add(np.log(vb) / np.log(va), f"log_{na}({nb})")
        except (ValueError, ZeroDivisionError):
            pass
    if vb > 0 and vb != 1 and va > 0:
        try:
            _add(np.log(va) / np.log(vb), f"log_{nb}({na})")
        except (ValueError, ZeroDivisionError):
            pass

    if abs(va * vb) < 20:
        try:
            _add(np.exp(va * vb), f"exp({na}*{nb})")
        except OverflowError:
            pass

    if va * vb > 0:
        _add(np.sqrt(va * vb), f"sqrt({na}*{nb})")

    if va > 0 and vb != 0 and abs(1 / vb) < 20:
        try:
            _add(va ** (1 / vb), f"{na}^(1/{nb})")
        except (OverflowError, ValueError):
            pass
    if vb > 0 and va != 0 and abs(1 / va) < 20:
        try:
            _add(vb ** (1 / va), f"{nb}^(1/{na})")
        except (OverflowError, ValueError):
            pass

    return results


def matches(result, target, threshold):
    """Check if result matches target within threshold relative error."""
    if np.isnan(result) or np.isinf(result):
        return False
    if target == 0:
        return abs(result) < 1e-10
    return abs(result - target) / abs(target) < threshold


# ═══════════════════════════════════════════════════════════════
# Depth generation
# ═══════════════════════════════════════════════════════════════

def generate_depth0(constants):
    """Depth 0: raw base constants + unary ops."""
    results = {}
    for na, va in constants.items():
        results[na] = (na, va)
        if va > 0:
            results[f"ln({na})"] = (f"ln({na})", np.log(va))
            results[f"sqrt({na})"] = (f"sqrt({na})", np.sqrt(va))
        if va != 0:
            results[f"1/{na}"] = (f"1/{na}", 1.0 / va)
        if va < 500:
            ev = np.exp(va)
            if np.isfinite(ev) and abs(ev) < 1e12:
                results[f"exp({na})"] = (f"exp({na})", ev)
    return results


def generate_depth1(constants):
    """Depth 1: all binary ops on all pairs of base constants (+ unary)."""
    results = generate_depth0(constants)

    names = list(constants.keys())
    values = list(constants.values())
    for i in range(len(names)):
        for j in range(len(names)):
            if i == j:
                continue
            ops = binary_ops(names[i], values[i], names[j], values[j])
            for v, expr in ops:
                results[expr] = (expr, v)
    return results


def generate_next_depth(prev_level, base_constants):
    """Generate next depth: binary ops between prev_level results and base constants."""
    results = {}
    prev_items = list(prev_level.values())
    base_items = list(base_constants.items())

    for p_expr, p_val in prev_items:
        for b_name, b_val in base_items:
            ops = binary_ops(p_expr, p_val, b_name, b_val)
            for v, expr in ops:
                # Keep only if not already in results (or better)
                if expr not in results:
                    results[expr] = (expr, v)
    return results


def check_targets(level_results, targets, threshold):
    """Check which targets are reached at this level. Returns {target_name: (expr, val, err%)}"""
    hit = {}
    for tname, tval in targets.items():
        best_err = float('inf')
        best_expr = None
        best_val = None
        for expr, val in level_results.values():
            if matches(val, tval, threshold):
                err = abs(val - tval) / abs(tval) * 100 if tval != 0 else 0
                if err < best_err:
                    best_err = err
                    best_expr = expr
                    best_val = val
        if best_expr is not None:
            hit[tname] = (best_expr, best_val, best_err)
    return hit


# ═══════════════════════════════════════════════════════════════
# Main analysis
# ═══════════════════════════════════════════════════════════════

def analyze_domain(domain_id, max_depth, targets, threshold):
    """Analyze reachability for a single domain across depth levels."""
    if domain_id not in DOMAINS:
        print(f"ERROR: Unknown domain '{domain_id}'")
        print(f"Available: {', '.join(DOMAINS.keys())}")
        sys.exit(1)

    dinfo = DOMAINS[domain_id]
    constants = dinfo["constants"]

    print(f"Domain: {domain_id} ({dinfo['name']})")
    print(f"Base constants: {len(constants)}")
    print(f"Max depth: {max_depth}")
    print(f"Threshold: {threshold*100}%")
    print(f"Targets: {len(targets)}")
    print()

    cumulative_reached = {}  # tname -> (depth, expr, val, err%)
    depth_results = []  # per-depth info

    # Depth 0: unary on base
    print(f"--- Depth 0 (base + unary) ---")
    level0 = generate_depth0(constants)
    print(f"  Search space: {len(level0)} expressions")
    hits0 = check_targets(level0, targets, threshold)
    new0 = set(hits0.keys()) - set(cumulative_reached.keys())
    for tname in new0:
        expr, val, err = hits0[tname]
        cumulative_reached[tname] = (0, expr, val, err)
    depth_results.append({
        "depth": 0,
        "space_size": len(level0),
        "total_reached": len(cumulative_reached),
        "new_targets": sorted(new0),
        "hits": hits0,
    })
    print(f"  Targets reached: {len(cumulative_reached)}/{len(targets)}")
    if new0:
        print(f"  New: {', '.join(sorted(new0))}")
    print()

    # Depth 1: binary on pairs
    print(f"--- Depth 1 (binary on pairs) ---")
    level1 = generate_depth1(constants)
    print(f"  Search space: {len(level1)} expressions")
    hits1 = check_targets(level1, targets, threshold)
    new1 = set(hits1.keys()) - set(cumulative_reached.keys())
    for tname in new1:
        expr, val, err = hits1[tname]
        cumulative_reached[tname] = (1, expr, val, err)
    depth_results.append({
        "depth": 1,
        "space_size": len(level1),
        "total_reached": len(cumulative_reached),
        "new_targets": sorted(new1),
        "hits": hits1,
    })
    print(f"  Targets reached: {len(cumulative_reached)}/{len(targets)}")
    if new1:
        print(f"  New: {', '.join(sorted(new1))}")
    print()

    # Deeper levels
    prev_level = level1
    for d in range(2, max_depth + 1):
        print(f"--- Depth {d} (level{d-1} x base) ---")
        next_level = generate_next_depth(prev_level, constants)
        total_space = len(next_level)
        print(f"  Search space: {total_space} expressions")

        hits = check_targets(next_level, targets, threshold)
        new = set(hits.keys()) - set(cumulative_reached.keys())
        for tname in new:
            expr, val, err = hits[tname]
            cumulative_reached[tname] = (d, expr, val, err)
        depth_results.append({
            "depth": d,
            "space_size": total_space,
            "total_reached": len(cumulative_reached),
            "new_targets": sorted(new),
            "hits": hits,
        })
        print(f"  Targets reached: {len(cumulative_reached)}/{len(targets)}")
        if new:
            print(f"  New: {', '.join(sorted(new))}")
        print()

        prev_level = next_level

    return cumulative_reached, depth_results


def print_results(domain_id, cumulative_reached, depth_results, targets):
    """Print formatted results."""
    dinfo = DOMAINS[domain_id]

    # Summary table by depth
    print("=" * 70)
    print("Reachability by Depth")
    print("=" * 70)
    print(f"{'Depth':<8} {'Space Size':>12} {'Reached':>10} {'New Targets'}")
    print("-" * 70)
    for dr in depth_results:
        new_str = ", ".join(dr["new_targets"]) if dr["new_targets"] else "-"
        print(f"  {dr['depth']:<6} {dr['space_size']:>12,} {dr['total_reached']:>7}/{len(targets)}   {new_str}")
    print("-" * 70)

    # ASCII growth chart
    print("\nReachability Growth (ASCII)")
    print("=" * 70)
    max_targets = len(targets)
    bar_width = 40
    for dr in depth_results:
        filled = int(dr["total_reached"] / max_targets * bar_width)
        bar = "#" * filled + "." * (bar_width - filled)
        print(f"  Depth {dr['depth']}: [{bar}] {dr['total_reached']}/{max_targets}")

    # Best expression for each reached target
    print("\n" + "=" * 70)
    print("Best Expression per Target")
    print("=" * 70)
    print(f"{'Target':<12} {'Depth':>6} {'Expression':<50} {'Error%':>8}")
    print("-" * 80)
    for tname in sorted(targets.keys()):
        if tname in cumulative_reached:
            depth, expr, val, err = cumulative_reached[tname]
            # Truncate long expressions
            expr_disp = expr if len(expr) <= 48 else expr[:45] + "..."
            print(f"  {tname:<10} {depth:>6} {expr_disp:<50} {err:.4f}%")
        else:
            print(f"  {tname:<10} {'---':>6} {'NOT REACHED':<50}")
    print("-" * 80)

    # Unreached targets
    unreached = sorted(set(targets.keys()) - set(cumulative_reached.keys()))
    if unreached:
        print(f"\nUnreached targets ({len(unreached)}): {', '.join(unreached)}")
    else:
        print(f"\nAll {len(targets)} targets reached!")

    # Space growth rate
    if len(depth_results) > 1:
        print("\n" + "=" * 70)
        print("Search Space Growth")
        print("=" * 70)
        for i in range(1, len(depth_results)):
            prev = depth_results[i - 1]["space_size"]
            curr = depth_results[i]["space_size"]
            growth = curr / prev if prev > 0 else float('inf')
            print(f"  Depth {depth_results[i-1]['depth']} -> {depth_results[i]['depth']}: "
                  f"{prev:,} -> {curr:,} (x{growth:.1f})")


# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Depth Reachability Analyzer (H-CX-463/467)")
    parser.add_argument("--domain", type=str, required=True,
                        help="Domain ID to analyze (N/A/G/T/C/Q/I/S)")
    parser.add_argument("--depth", type=int, default=2,
                        help="Max depth to test (1-3, default: 2)")
    parser.add_argument("--targets", type=str, nargs="*",
                        help="Custom target list (default: 9 standard targets)")
    parser.add_argument("--threshold", type=float, default=0.001,
                        help="Relative error threshold (default: 0.001)")
    args = parser.parse_args()

    if args.depth < 1 or args.depth > 3:
        print("ERROR: depth must be 1-3")
        sys.exit(1)

    print("=" * 70)
    print("Depth Reachability Analyzer (H-CX-463/467)")
    print("=" * 70)

    # Parse targets
    if args.targets:
        targets = {}
        for t in args.targets:
            if t in DEFAULT_TARGETS:
                targets[t] = DEFAULT_TARGETS[t]
            else:
                try:
                    tval = float(eval(t, {"__builtins__": {}}, {
                        "sqrt": np.sqrt, "log": np.log, "ln": np.log,
                        "exp": np.exp, "pi": np.pi, "e": np.e,
                    }))
                    targets[t] = tval
                except Exception:
                    print(f"WARNING: Cannot parse target '{t}', skipping")
    else:
        targets = DEFAULT_TARGETS

    cumulative_reached, depth_results = analyze_domain(
        args.domain, args.depth, targets, args.threshold
    )

    print_results(args.domain, cumulative_reached, depth_results, targets)
    print("\nDone.")


if __name__ == "__main__":
    main()
