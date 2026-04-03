#!/usr/bin/env python3
"""Domain Distance Calculator — Inter-domain distance/overlap and topology visualization

Computes overlap and distance matrices between convergence engine domains,
analyzes domain specialization by constant category, and classifies targets
into phase-map quadrants.

Based on H-CX-468 (phase map) and H-CX-480 (domain specialization).

Usage:
  python3 calc/domain_distance.py --overlap
  python3 calc/domain_distance.py --distance
  python3 calc/domain_distance.py --specialization
  python3 calc/domain_distance.py --phase-map
  python3 calc/domain_distance.py --overlap --specialization
  python3 calc/domain_distance.py --overlap --threshold 0.0001
"""

import argparse
import os
import sys
import warnings
from collections import defaultdict

import numpy as np

warnings.filterwarnings("ignore", category=RuntimeWarning)

# Import DOMAINS from convergence_engine.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from convergence_engine import DOMAINS, TARGETS, binary_ops


# ═════════════════════════════════════════════════════════════════
# CONSTANT CATEGORIES
# ═════════════════════════════════════════════════════════════════

CATEGORIES = {
    "Algebraic irrational": {
        "sqrt(2)": np.sqrt(2),
        "sqrt(3)": np.sqrt(3),
        "sqrt(5)": np.sqrt(5),
        "phi_gold": (1 + np.sqrt(5)) / 2,
    },
    "Transcendental": {
        "e": np.e,
        "pi": np.pi,
        "gamma_EM": 0.5772156649,
        "zeta(3)": 1.2020569031,
    },
    "Logarithmic": {
        "ln(2)": np.log(2),
        "ln(3)": np.log(3),
        "ln(4/3)": np.log(4 / 3),
    },
    "Project": {
        "GZ_width": np.log(4 / 3),
        "1/e": 1 / np.e,
        "GZ_center": 1 / np.e,
        "GZ_lower": 0.5 - np.log(4 / 3),
        "5/6": 5 / 6,
        "1/3": 1 / 3,
    },
}

# All category targets combined
ALL_TARGETS = {}
for cat_targets in CATEGORIES.values():
    ALL_TARGETS.update(cat_targets)

# Also include a broader set for overlap/distance
BROAD_TARGETS = {}
BROAD_TARGETS.update(TARGETS)


# ═════════════════════════════════════════════════════════════════
# DOMAIN REACHABILITY — which targets a domain can reach
# ═════════════════════════════════════════════════════════════════

def compute_reachable(domain_key, targets, threshold=0.001):
    """Compute which targets a domain can reach via depth-1 binary ops.

    Returns dict: {target_name: (value, expr, error)} for reachable targets.
    """
    domain = DOMAINS[domain_key]
    consts = domain["constants"]
    names = list(consts.keys())
    vals = [consts[n] for n in names]

    reachable = {}

    # Check single constants
    for i, (n, v) in enumerate(zip(names, vals)):
        for tname, tval in targets.items():
            if tval == 0:
                continue
            err = abs(v - tval) / abs(tval)
            if err < threshold:
                if tname not in reachable or err < reachable[tname][2]:
                    reachable[tname] = (v, n, err)

    # Check binary ops on all pairs
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            ops = binary_ops(names[i], vals[i], names[j], vals[j])
            for val, expr in ops:
                for tname, tval in targets.items():
                    if tval == 0:
                        continue
                    err = abs(val - tval) / abs(tval)
                    if err < threshold:
                        if tname not in reachable or err < reachable[tname][2]:
                            reachable[tname] = (val, expr, err)

    return reachable


# ═════════════════════════════════════════════════════════════════
# OVERLAP MATRIX
# ═════════════════════════════════════════════════════════════════

def compute_overlap_matrix(threshold=0.001):
    """Compute overlap matrix: how many shared targets each domain pair can both reach."""
    domain_keys = sorted(DOMAINS.keys())

    # Compute reachable sets
    reachable = {}
    for dk in domain_keys:
        print(f"  Scanning domain {dk} ({DOMAINS[dk]['name']})...")
        reachable[dk] = set(compute_reachable(dk, BROAD_TARGETS, threshold).keys())
        print(f"    -> {len(reachable[dk])} targets reachable")

    n = len(domain_keys)
    overlap = np.zeros((n, n), dtype=int)
    for i in range(n):
        for j in range(n):
            overlap[i, j] = len(reachable[domain_keys[i]] & reachable[domain_keys[j]])

    return domain_keys, overlap, reachable


def print_overlap_matrix(domain_keys, overlap):
    """Print overlap matrix as ASCII heatmap."""
    n = len(domain_keys)
    max_val = overlap.max()

    print("\n" + "=" * 60)
    print("  OVERLAP MATRIX (shared reachable targets)")
    print("=" * 60)

    # Header
    header = "       " + "  ".join(f"{dk:>5}" for dk in domain_keys)
    print(header)
    print("       " + "------" * n)

    # Heatmap chars
    chars = " .:-=+*#@"

    for i, dk in enumerate(domain_keys):
        row = f"  {dk:>3} |"
        for j in range(n):
            val = overlap[i, j]
            if i == j:
                row += f" [{val:3d}]"
            else:
                # ASCII heatmap character
                level = int((val / max(max_val, 1)) * (len(chars) - 1))
                c = chars[level]
                row += f"  {val:3d}{c}"
        print(row)

    print()

    # Top pairs
    pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            pairs.append((overlap[i, j], domain_keys[i], domain_keys[j]))
    pairs.sort(reverse=True)

    print("  Top domain pairs by overlap:")
    for count, d1, d2 in pairs[:10]:
        name1 = DOMAINS[d1]["name"]
        name2 = DOMAINS[d2]["name"]
        bar = "#" * min(count, 50)
        print(f"    {d1}-{d2} ({name1} x {name2}): {count:3d} |{bar}")

    print()


# ═════════════════════════════════════════════════════════════════
# DISTANCE MATRIX
# ═════════════════════════════════════════════════════════════════

def compute_distance_matrix(domain_keys, overlap, reachable):
    """Compute Jaccard distance: 1 - |A&B|/|AuB|."""
    n = len(domain_keys)
    dist = np.zeros((n, n))

    for i in range(n):
        for j in range(n):
            if i == j:
                dist[i, j] = 0.0
            else:
                si = reachable[domain_keys[i]]
                sj = reachable[domain_keys[j]]
                union = len(si | sj)
                inter = len(si & sj)
                dist[i, j] = 1.0 - (inter / union) if union > 0 else 1.0

    return dist


def print_distance_matrix(domain_keys, dist):
    """Print distance matrix as ASCII heatmap."""
    n = len(domain_keys)

    print("\n" + "=" * 60)
    print("  DISTANCE MATRIX (Jaccard: 1 - |A&B|/|AuB|)")
    print("=" * 60)

    # Header
    header = "       " + "  ".join(f"{dk:>6}" for dk in domain_keys)
    print(header)
    print("       " + "-------" * n)

    # Heatmap chars (inverted: close = dense, far = sparse)
    chars = "@#*=+-:. "

    for i, dk in enumerate(domain_keys):
        row = f"  {dk:>3} |"
        for j in range(n):
            val = dist[i, j]
            if i == j:
                row += f" [{val:5.3f}]"
            else:
                level = int(val * (len(chars) - 1))
                level = min(level, len(chars) - 1)
                c = chars[level]
                row += f" {val:5.3f}{c}"
        print(row)

    print()

    # Closest pairs
    pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            pairs.append((dist[i, j], domain_keys[i], domain_keys[j]))
    pairs.sort()

    print("  Closest domain pairs (smallest distance):")
    for d, d1, d2 in pairs[:5]:
        name1 = DOMAINS[d1]["name"]
        name2 = DOMAINS[d2]["name"]
        bar_len = int((1 - d) * 40)
        bar = "#" * bar_len + "." * (40 - bar_len)
        print(f"    {d1}-{d2}: {d:.3f}  |{bar}|  {name1} x {name2}")

    print("\n  Most distant domain pairs:")
    for d, d1, d2 in pairs[-5:]:
        name1 = DOMAINS[d1]["name"]
        name2 = DOMAINS[d2]["name"]
        bar_len = int((1 - d) * 40)
        bar = "#" * bar_len + "." * (40 - bar_len)
        print(f"    {d1}-{d2}: {d:.3f}  |{bar}|  {name1} x {name2}")

    print()


# ═════════════════════════════════════════════════════════════════
# SPECIALIZATION
# ═════════════════════════════════════════════════════════════════

def compute_specialization(threshold=0.001):
    """Compute which constant categories each domain specializes in."""
    domain_keys = sorted(DOMAINS.keys())
    cat_names = list(CATEGORIES.keys())

    # Domain x Category reachability
    spec = {}
    for dk in domain_keys:
        spec[dk] = {}
        for cat, cat_targets in CATEGORIES.items():
            reachable = compute_reachable(dk, cat_targets, threshold)
            total = len(cat_targets)
            reached = len(reachable)
            spec[dk][cat] = (reached, total)

    return domain_keys, cat_names, spec


def print_specialization(domain_keys, cat_names, spec):
    """Print specialization bar chart."""
    print("\n" + "=" * 70)
    print("  DOMAIN SPECIALIZATION (reachable / total per category)")
    print("=" * 70)

    # Table header
    cat_short = {
        "Algebraic irrational": "Algebraic",
        "Transcendental": "Transcend",
        "Logarithmic": "Logarithm",
        "Project": "Project",
    }

    header = f"  {'Domain':>12} |"
    for cat in cat_names:
        header += f" {cat_short.get(cat, cat):>10} |"
    header += "  Total"
    print(header)
    print("  " + "-" * (len(header) - 2))

    for dk in domain_keys:
        name = DOMAINS[dk]["name"][:12]
        row = f"  {name:>12} |"
        total_reached = 0
        total_possible = 0
        for cat in cat_names:
            reached, possible = spec[dk][cat]
            total_reached += reached
            total_possible += possible
            pct = reached / possible * 100 if possible > 0 else 0
            row += f"   {reached}/{possible} {pct:4.0f}% |"
        pct_total = total_reached / total_possible * 100 if total_possible > 0 else 0
        row += f"  {total_reached}/{total_possible} ({pct_total:.0f}%)"
        print(row)

    # Bar chart
    print("\n  Specialization bar chart:")
    for dk in domain_keys:
        name = DOMAINS[dk]["name"][:15]
        print(f"\n    {dk} ({name}):")
        for cat in cat_names:
            reached, possible = spec[dk][cat]
            pct = reached / possible if possible > 0 else 0
            bar_full = int(pct * 30)
            bar = "#" * bar_full + "." * (30 - bar_full)
            label = cat_short.get(cat, cat)
            print(f"      {label:>10}: |{bar}| {reached}/{possible}")

    print()


# ═════════════════════════════════════════════════════════════════
# PHASE MAP
# ═════════════════════════════════════════════════════════════════

def compute_phase_map(threshold=0.001):
    """Classify targets into 4 quadrants based on domain reach.

    CORE:   Many domains reach it, high overlap among those domains
    BRIDGE: Many domains reach it, low overlap (connects distant domains)
    LOCAL:  Few domains reach it, high overlap (domain cluster exclusive)
    PORTAL: Few domains reach it, low overlap (isolated pathway)
    """
    domain_keys = sorted(DOMAINS.keys())

    # Compute reachable for each domain
    reachable_by_domain = {}
    for dk in domain_keys:
        reachable_by_domain[dk] = set(compute_reachable(dk, BROAD_TARGETS, threshold).keys())

    # For each target, find which domains reach it
    target_domains = defaultdict(set)
    for dk in domain_keys:
        for t in reachable_by_domain[dk]:
            target_domains[t].add(dk)

    # Only targets reached by at least 1 domain
    active_targets = {t: doms for t, doms in target_domains.items() if len(doms) >= 1}

    if not active_targets:
        print("  No targets reachable at this threshold.")
        return

    # Compute two axes:
    #   X = domain_count (how many domains reach this target)
    #   Y = avg pairwise overlap among reaching domains
    n_domains = len(domain_keys)
    median_count = np.median([len(doms) for doms in active_targets.values()])

    results = []
    for tname, doms in active_targets.items():
        dom_count = len(doms)
        # Average pairwise Jaccard similarity among reaching domains
        if dom_count >= 2:
            sims = []
            dom_list = sorted(doms)
            for i in range(len(dom_list)):
                for j in range(i + 1, len(dom_list)):
                    si = reachable_by_domain[dom_list[i]]
                    sj = reachable_by_domain[dom_list[j]]
                    union = len(si | sj)
                    inter = len(si & sj)
                    sims.append(inter / union if union > 0 else 0)
            avg_sim = np.mean(sims)
        else:
            avg_sim = 0.0

        results.append((tname, dom_count, avg_sim, doms))

    # Classify into quadrants
    count_thresh = median_count
    sim_values = [r[2] for r in results if r[1] >= 2]
    sim_thresh = np.median(sim_values) if sim_values else 0.5

    quadrants = {"CORE": [], "BRIDGE": [], "LOCAL": [], "PORTAL": []}
    for tname, dom_count, avg_sim, doms in results:
        if dom_count >= count_thresh:
            if avg_sim >= sim_thresh:
                q = "CORE"
            else:
                q = "BRIDGE"
        else:
            if avg_sim >= sim_thresh:
                q = "LOCAL"
            else:
                q = "PORTAL"
        quadrants[q].append((tname, dom_count, avg_sim, doms))

    # Sort each quadrant
    for q in quadrants:
        quadrants[q].sort(key=lambda x: (-x[1], -x[2]))

    return quadrants, count_thresh, sim_thresh, results


def print_phase_map(quadrants, count_thresh, sim_thresh, results):
    """Print phase map scatter and quadrant listing."""
    print("\n" + "=" * 70)
    print("  PHASE MAP — Target Classification")
    print(f"  Thresholds: domain_count >= {count_thresh:.1f} (high), "
          f"avg_similarity >= {sim_thresh:.3f} (high)")
    print("=" * 70)

    labels = {
        "CORE": "CORE (many domains, high overlap — universal constants)",
        "BRIDGE": "BRIDGE (many domains, low overlap — cross-domain links)",
        "LOCAL": "LOCAL (few domains, high overlap — cluster-specific)",
        "PORTAL": "PORTAL (few domains, low overlap — isolated pathways)",
    }
    symbols = {"CORE": "@", "BRIDGE": "+", "LOCAL": "o", "PORTAL": "."}

    # ASCII scatter plot
    print("\n  Scatter (X=domain_count, Y=avg_similarity):")
    print(f"  Legend: @ CORE  + BRIDGE  o LOCAL  . PORTAL")
    print()

    max_count = max(r[1] for r in results)
    height = 20
    width = 50

    grid = [[" " for _ in range(width + 1)] for _ in range(height + 1)]

    for tname, dom_count, avg_sim, doms in results:
        x = int(dom_count / max(max_count, 1) * (width - 1))
        y = int(avg_sim * (height - 1))
        y = height - 1 - y  # invert Y axis

        # Determine quadrant
        for q, items in quadrants.items():
            if any(item[0] == tname for item in items):
                sym = symbols[q]
                break
        else:
            sym = "?"

        if grid[y][x] == " ":
            grid[y][x] = sym
        elif grid[y][x] != sym:
            grid[y][x] = "*"  # collision

    # Print grid
    for y in range(height):
        if y == 0:
            label = "1.0"
        elif y == height - 1:
            label = "0.0"
        elif y == height // 2:
            label = "sim"
        else:
            label = "   "
        print(f"  {label} |{''.join(grid[y])}|")
    print(f"      +{'-' * (width + 1)}+")
    print(f"       0{' ' * ((width - 3) // 2)}domains{' ' * ((width - 3) // 2)}{max_count}")

    # Quadrant listing
    for q in ["CORE", "BRIDGE", "LOCAL", "PORTAL"]:
        items = quadrants[q]
        print(f"\n  {labels[q]}")
        print(f"  {'─' * 60}")
        if not items:
            print("    (none)")
            continue
        for tname, dom_count, avg_sim, doms in items[:15]:
            dom_str = ",".join(sorted(doms))
            print(f"    {tname:>18}  domains={dom_count}  sim={avg_sim:.3f}  [{dom_str}]")
        if len(items) > 15:
            print(f"    ... and {len(items) - 15} more")

    # Summary
    print(f"\n  Summary:")
    for q in ["CORE", "BRIDGE", "LOCAL", "PORTAL"]:
        print(f"    {q:>7}: {len(quadrants[q]):3d} targets")
    print(f"    {'TOTAL':>7}: {sum(len(v) for v in quadrants.values()):3d} targets")
    print()


# ═════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Domain Distance Calculator — inter-domain topology analysis"
    )
    parser.add_argument("--overlap", action="store_true",
                        help="Show overlap matrix")
    parser.add_argument("--distance", action="store_true",
                        help="Show distance matrix (Jaccard)")
    parser.add_argument("--specialization", action="store_true",
                        help="Show domain specialization by constant category")
    parser.add_argument("--phase-map", action="store_true",
                        help="Classify targets into CORE/BRIDGE/LOCAL/PORTAL")
    parser.add_argument("--threshold", type=float, default=0.001,
                        help="Error threshold (default: 0.001 = 0.1%%)")

    args = parser.parse_args()

    if not any([args.overlap, args.distance, args.specialization, args.phase_map]):
        parser.print_help()
        return

    print(f"Domain Distance Calculator")
    print(f"Threshold: {args.threshold} ({args.threshold*100:.2f}%%)")
    print(f"Domains: {len(DOMAINS)}, Targets: {len(BROAD_TARGETS)}")

    if args.overlap or args.distance:
        domain_keys, overlap, reachable = compute_overlap_matrix(args.threshold)

        if args.overlap:
            print_overlap_matrix(domain_keys, overlap)

        if args.distance:
            dist = compute_distance_matrix(domain_keys, overlap, reachable)
            print_distance_matrix(domain_keys, dist)

    if args.specialization:
        dk, cn, spec = compute_specialization(args.threshold)
        print_specialization(dk, cn, spec)

    if args.phase_map:
        result = compute_phase_map(args.threshold)
        if result:
            quadrants, ct, st, results = result
            print_phase_map(quadrants, ct, st, results)


if __name__ == "__main__":
    main()
