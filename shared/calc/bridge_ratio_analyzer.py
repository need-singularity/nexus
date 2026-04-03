#!/usr/bin/env python3
"""Bridge/Independent Ratio Analyzer — H-CX-461/462

Computes bridge-to-independent ratio for convergence targets.
Bridge = cross-domain path (constants from two different domains).
Independent = single-domain path (both constants from same domain).

High ratio => constant is "inter-domain glue" (hard to reach internally,
easy via cross-domain combinations).

Usage:
  python3 calc/bridge_ratio_analyzer.py --all --classify
  python3 calc/bridge_ratio_analyzer.py --target "zeta(3)"
  python3 calc/bridge_ratio_analyzer.py --all --threshold 0.0001
"""

import argparse
import sys
import os
import warnings
from collections import defaultdict
from itertools import combinations

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
    # Consciousness constants (from anima Laws 63-79)
    "Psi_steps":    3.0 / np.log(2),       # 4.328 consciousness evolution number
    "Psi_coupling": np.log(2) / 2**5.5,    # 0.01534 consciousness coupling
    "conservation": 0.478,                  # H^2 + dp^2 conservation
    "tanh3_ln2":    np.tanh(3)*np.log(2),  # 0.6895 consciousness saturation
}

# ═══════════════════════════════════════════════════════════════
# Binary operations
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
# Core analysis functions
# ═══════════════════════════════════════════════════════════════

def find_single_domain_paths(target_val, threshold):
    """Find single-domain paths reaching target. Returns {domain_id: [(expr, val, err%), ...]}"""
    domain_paths = defaultdict(list)
    for did, dinfo in DOMAINS.items():
        consts = list(dinfo["constants"].items())
        for i in range(len(consts)):
            for j in range(len(consts)):
                if i == j:
                    continue
                a_name, a_val = consts[i]
                b_name, b_val = consts[j]
                ops = binary_ops(a_name, a_val, b_name, b_val)
                for v, expr in ops:
                    if matches(v, target_val, threshold):
                        err = abs(v - target_val) / abs(target_val) * 100 if target_val != 0 else 0
                        domain_paths[did].append((expr, v, err))
    return domain_paths


def find_bridge_paths(target_val, threshold):
    """Find cross-domain bridge paths reaching target. Returns {(d1,d2): [(expr, val, err%), ...]}"""
    domain_ids = list(DOMAINS.keys())
    pair_paths = defaultdict(list)
    for d1, d2 in combinations(domain_ids, 2):
        consts1 = list(DOMAINS[d1]["constants"].items())
        consts2 = list(DOMAINS[d2]["constants"].items())
        for a_name, a_val in consts1:
            for b_name, b_val in consts2:
                ops = binary_ops(a_name, a_val, b_name, b_val)
                for v, expr in ops:
                    if matches(v, target_val, threshold):
                        err = abs(v - target_val) / abs(target_val) * 100 if target_val != 0 else 0
                        pair_paths[(d1, d2)].append((expr, v, err))
    return pair_paths


def classify_target(ratio):
    """Classify target based on bridge/independent ratio."""
    if ratio == float('inf'):
        return "Interface (pure bridge)"
    elif ratio > 7:
        return "Interface"
    elif ratio >= 3:
        return "Balanced"
    else:
        return "Intrinsic"


def analyze_target(tname, tval, threshold):
    """Full analysis for one target."""
    single_paths = find_single_domain_paths(tval, threshold)
    bridge_paths = find_bridge_paths(tval, threshold)

    single_domain_count = len(single_paths)
    single_path_count = sum(len(v) for v in single_paths.values())
    bridge_pair_count = len(bridge_paths)
    bridge_path_count = sum(len(v) for v in bridge_paths.values())

    if single_domain_count == 0:
        ratio = float('inf') if bridge_pair_count > 0 else 0
    else:
        ratio = bridge_pair_count / single_domain_count

    # Best path per domain
    best_per_domain = {}
    for did, paths in single_paths.items():
        best = min(paths, key=lambda x: x[2])  # min error
        best_per_domain[did] = best

    return {
        "name": tname,
        "value": tval,
        "single_domains": single_domain_count,
        "single_paths": single_path_count,
        "bridge_pairs": bridge_pair_count,
        "bridge_paths": bridge_path_count,
        "ratio": ratio,
        "classification": classify_target(ratio),
        "best_per_domain": best_per_domain,
        "all_single": single_paths,
        "all_bridge": bridge_paths,
    }


# ═══════════════════════════════════════════════════════════════
# Display functions
# ═══════════════════════════════════════════════════════════════

def print_summary_table(results, show_classify):
    """Print summary table of all analyzed targets."""
    print("=" * 100)
    header = f"{'Target':<12} {'Value':>10} {'SingleDom':>10} {'SinglePath':>11} {'BridgePair':>11} {'BridgePath':>11} {'Ratio':>8}"
    if show_classify:
        header += f"  {'Classification':<22}"
    print(header)
    print("-" * 100)
    for r in results:
        ratio_str = f"{r['ratio']:.1f}" if r['ratio'] != float('inf') else "inf"
        line = (f"{r['name']:<12} {r['value']:>10.6f} {r['single_domains']:>10} "
                f"{r['single_paths']:>11} {r['bridge_pairs']:>11} {r['bridge_paths']:>11} "
                f"{ratio_str:>8}")
        if show_classify:
            line += f"  {r['classification']:<22}"
        print(line)
    print("-" * 100)


def print_ratio_chart(results):
    """Print ASCII bar chart of bridge-to-independent ratio."""
    print("\nBridge-to-Independent Ratio (ASCII Bar Chart)")
    print("=" * 70)
    finite_ratios = [r['ratio'] for r in results if r['ratio'] != float('inf')]
    max_ratio = max(finite_ratios) if finite_ratios else 1
    bar_width = 50

    for r in results:
        ratio = r['ratio']
        if ratio == float('inf'):
            bar_len = bar_width
            bar = "#" * bar_len + " (inf)"
        else:
            bar_len = int(ratio / max_ratio * bar_width) if max_ratio > 0 else 0
            bar = "#" * max(bar_len, 1)
        print(f"  {r['name']:<12} |{bar}")


def print_detail(result):
    """Print detailed analysis for one target."""
    r = result
    print(f"\n{'=' * 70}")
    print(f"Target: {r['name']} = {r['value']:.10f}")
    print(f"{'=' * 70}")
    print(f"  Single-domain hits:  {r['single_domains']} domains, {r['single_paths']} paths")
    print(f"  Bridge-pair hits:    {r['bridge_pairs']} pairs, {r['bridge_paths']} paths")
    ratio_str = f"{r['ratio']:.2f}" if r['ratio'] != float('inf') else "inf"
    print(f"  Ratio (bridge/single): {ratio_str}")
    print(f"  Classification: {r['classification']}")

    if r['best_per_domain']:
        print(f"\n  Best path per domain:")
        print(f"  {'Domain':<6} {'Expression':<45} {'Error%':>8}")
        print(f"  {'-' * 62}")
        for did in sorted(r['best_per_domain'].keys()):
            expr, val, err = r['best_per_domain'][did]
            dname = DOMAINS[did]["name"]
            print(f"  {did:<6} {expr:<45} {err:.4f}%")

    if r['all_bridge']:
        print(f"\n  Top bridge pairs:")
        sorted_pairs = sorted(r['all_bridge'].items(), key=lambda x: len(x[1]), reverse=True)
        for (d1, d2), paths in sorted_pairs[:5]:
            n1 = DOMAINS[d1]["name"]
            n2 = DOMAINS[d2]["name"]
            print(f"    {d1}x{d2} ({n1} x {n2}): {len(paths)} paths")
            # Show best path for this pair
            best = min(paths, key=lambda x: x[2])
            print(f"      best: {best[0]} = {best[1]:.10f} (err={best[2]:.4f}%)")


# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Bridge/Independent Ratio Analyzer (H-CX-461/462)")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--target", type=str, help="Analyze specific target (e.g. 'zeta(3)')")
    group.add_argument("--all", action="store_true", help="Analyze all 9 default targets")
    parser.add_argument("--threshold", type=float, default=0.001, help="Relative error threshold (default: 0.001)")
    parser.add_argument("--classify", action="store_true", help="Classify as Intrinsic/Balanced/Interface")
    args = parser.parse_args()

    print("=" * 70)
    print("Bridge/Independent Ratio Analyzer (H-CX-461/462)")
    print("=" * 70)
    print(f"Threshold: {args.threshold*100}% relative error")
    print(f"Domains: {len(DOMAINS)} ({', '.join(DOMAINS.keys())})")
    for did, dinfo in DOMAINS.items():
        print(f"  {did} ({dinfo['name']}): {len(dinfo['constants'])} constants")
    print()

    if args.all:
        targets = DEFAULT_TARGETS
    else:
        tname = args.target
        if tname in DEFAULT_TARGETS:
            targets = {tname: DEFAULT_TARGETS[tname]}
        else:
            # Try to evaluate as expression
            try:
                tval = float(eval(tname, {"__builtins__": {}}, {
                    "sqrt": np.sqrt, "log": np.log, "ln": np.log,
                    "exp": np.exp, "pi": np.pi, "e": np.e,
                }))
                targets = {tname: tval}
            except Exception:
                print(f"ERROR: Unknown target '{tname}'")
                print(f"Available: {', '.join(DEFAULT_TARGETS.keys())}")
                sys.exit(1)

    print(f"Analyzing {len(targets)} target(s)...\n")

    results = []
    for tname, tval in targets.items():
        r = analyze_target(tname, tval, args.threshold)
        results.append(r)

    # Sort by ratio descending
    results.sort(key=lambda x: x['ratio'] if x['ratio'] != float('inf') else 999, reverse=True)

    # Summary table
    print_summary_table(results, args.classify)

    # Ratio chart
    print_ratio_chart(results)

    # Classification summary
    if args.classify:
        print("\n" + "=" * 70)
        print("Classification Summary")
        print("=" * 70)
        classes = defaultdict(list)
        for r in results:
            classes[r['classification']].append(r['name'])
        for cls in ["Intrinsic", "Balanced", "Interface", "Interface (pure bridge)"]:
            if cls in classes:
                label = cls
                if cls == "Intrinsic":
                    label += " (ratio < 3)"
                elif cls == "Balanced":
                    label += " (3 <= ratio <= 7)"
                elif cls == "Interface":
                    label += " (ratio > 7)"
                print(f"  {label}: {', '.join(classes[cls])}")

    # Detail for single target or all
    if len(targets) == 1:
        print_detail(results[0])
    else:
        # Show detail for top 3
        print("\n" + "=" * 70)
        print("Top 3 Detailed Analysis")
        print("=" * 70)
        for r in results[:3]:
            print_detail(r)

    # Statistics
    if len(results) > 1:
        print("\n" + "=" * 70)
        print("Summary Statistics")
        print("=" * 70)
        finite_ratios = [r['ratio'] for r in results if r['ratio'] != float('inf')]
        if finite_ratios:
            print(f"  Mean ratio:   {np.mean(finite_ratios):.2f}")
            print(f"  Median ratio: {np.median(finite_ratios):.2f}")
            print(f"  Std ratio:    {np.std(finite_ratios):.2f}")
            print(f"  Min ratio:    {min(finite_ratios):.2f}")
            print(f"  Max ratio:    {max(finite_ratios):.2f}")

    print("\nDone.")


if __name__ == "__main__":
    main()
