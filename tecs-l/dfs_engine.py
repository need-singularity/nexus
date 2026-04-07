#!/usr/bin/env python3
"""DFS Automatic Search Engine — Automates ralph-loop manual iteration

Instead of manually trying constant combinations, systematically explore all combinations with DFS.
Automatically detects cross-island bridges.

Usage:
  python3 dfs_engine.py                          # default depth=2, threshold=0.001
  python3 dfs_engine.py --depth 3                # 3-level recursive combination
  python3 dfs_engine.py --threshold 0.0001       # Within 0.01% error only
  python3 dfs_engine.py --depth 2 --threshold 0.001
"""

import numpy as np
import argparse
import os
import sys
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')
import tecsrs

# ─────────────────────────────────────────
# Constants — from nexus SSOT
# ─────────────────────────────────────────
_shared = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.shared')
if _shared not in sys.path:
    sys.path.insert(0, _shared)

from n6_constants import ISLANDS, TARGETS


# ─────────────────────────────────────────
# Island tracking (for verification pipeline)
# ─────────────────────────────────────────

def extract_base_constants(expr):
    """Extract base constant names used in the expression string"""
    all_names = set()
    for island_consts in ISLANDS.values():
        for name in island_consts:
            if name in expr:
                all_names.add(name)
    return all_names


# ─────────────────────────────────────────
# DFS Engine Core — powered by tecsrs Rust
# ─────────────────────────────────────────

def _build_engine(depth_limit, threshold):
    """Build tecsrs DfsEngine with project constants and targets."""
    engine = tecsrs.DfsEngine()
    island_map = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
    for island_id, consts in ISLANDS.items():
        for name, val in consts.items():
            engine.add_constant(name, float(val), island_map[island_id])
    for tname, tval in TARGETS.items():
        engine.add_target(tname, float(tval))
    return engine


def build_level(depth_limit):
    """Generate expressions via tecsrs Rust engine. Returns expression count."""
    engine = _build_engine(depth_limit, 0.001)
    expr_count = engine.expression_count(depth_limit)
    print(f"  [tecsrs] Generated {expr_count:,} expressions at depth {depth_limit}")
    return expr_count


def check_targets(depth_limit, threshold=0.001):
    """Run DFS search entirely in Rust, return Python dicts for verification."""
    engine = _build_engine(depth_limit, threshold)
    raw_matches = engine.search(depth_limit, threshold)

    matches = []
    for m in raw_matches:
        matches.append({
            'target': m.target,
            'target_val': m.target_val,
            'formula': m.formula,
            'formula_val': m.formula_val,
            'error': m.error,
            'error_pct': m.error_pct,
            'islands': m.islands,
            'n_islands': m.n_islands,
            'significance': m.significance,
            'is_exact': m.is_exact,
        })

    print(f"  [tecsrs] {len(matches):,} matches found")
    return matches


def filter_best(matches, top_per_target=5):
    """Keep only best matches per target"""
    by_target = {}
    for m in matches:
        key = m['target']
        if key not in by_target:
            by_target[key] = []
        by_target[key].append(m)

    filtered = []
    for key, group in by_target.items():
        group.sort(key=lambda x: (-x['n_islands'], x['error']))
        filtered.extend(group[:top_per_target])

    return filtered


def find_cross_island(matches):
    """Extract only cross-island connections"""
    return [m for m in matches if m['n_islands'] >= 2]


# ─────────────────────────────────────────
# Verification Pipeline (automatically executed upon discovery)
# ─────────────────────────────────────────

def verify_discovery(match):
    """Automatically verify non-triviality of discovery.

    Returns:
        match with added fields: verified_grade, warnings[], verification_detail
    """
    warnings_list = []
    grade = match.get('is_exact', False)

    expr = match['formula']
    target = match['target']
    error_pct = match['error_pct']
    val = match['formula_val']
    target_val = match['target_val']

    # 1. Double-check arithmetic accuracy
    # (already checked in check_targets, double check)

    # 2. Ad hoc correction check: +1, -1 in expression?
    if '+1)' in expr or '-1)' in expr or expr.endswith('+1') or expr.endswith('-1'):
        warnings_list.append('AD_HOC: Contains +1/-1 correction')

    # 3. Strong Law of Small Numbers: all involved constants <100?
    base_consts = extract_base_constants(expr)
    all_small = True
    for name in base_consts:
        for consts in ISLANDS.values():
            if name in consts and abs(consts[name]) >= 100:
                all_small = False
    if all_small and len(base_consts) >= 2:
        # Combinations of small numbers have high chance of coincidence
        warnings_list.append('SMALL_NUMS: All constants <100 (possible coincidence)')

    # 4. Generalization test (if perfect number related)
    if any(name in ['sigma', 'tau', '6'] for name in base_consts):
        # Does it hold for perfect number 28 too?
        warnings_list.append('GENERALIZE: Needs verification for perfect number 28 (not performed)')

    # 5. Simple p-value estimation
    # Estimate "degrees of freedom" of expression: number of constants used × number of operations
    n_consts = len(base_consts)
    # Approximate number of combinations
    total_consts = sum(len(v) for v in ISLANDS.values())
    n_ops = 12  # Types of binary operations
    if n_consts <= 1:
        est_trials = total_consts * 5  # unary only
    elif n_consts == 2:
        est_trials = total_consts * (total_consts - 1) * n_ops
    else:
        est_trials = total_consts ** n_consts * n_ops

    # Number of targets within error range / total space
    # Range: target ± threshold → 2 * threshold * target
    # Space: approximately [0.01, 1000] → 1000
    if target_val != 0:
        p_single = (2 * match['error'] * abs(target_val)) / 1000
    else:
        p_single = 0.001
    p_bonferroni = min(1.0, p_single * est_trials)

    match['p_single'] = p_single
    match['p_bonferroni'] = p_bonferroni
    match['est_trials'] = est_trials

    if p_bonferroni > 0.05:
        warnings_list.append(f'P_VALUE: Bonferroni p={p_bonferroni:.4f} > 0.05 (possible coincidence)')

    # 6. Approximate vs exact grade determination
    if match['is_exact']:
        if not warnings_list:
            verified_grade = '🟩 Exact (verification passed)'
        else:
            verified_grade = '🟩 Exact (caution: ' + '; '.join(warnings_list) + ')'
    elif error_pct < 0.01:
        if p_bonferroni < 0.01:
            verified_grade = '🟧★ Approximate (very precise, p<0.01)'
        elif p_bonferroni < 0.05:
            verified_grade = '🟧 Approximate (precise, p<0.05)'
        else:
            verified_grade = '🟧? Approximate (precise but p>0.05)'
    elif error_pct < 0.1:
        verified_grade = '🟧 Approximate (medium precision)'
    elif error_pct < 1.0:
        verified_grade = '🟧△ Approximate (weak)'
    else:
        verified_grade = '⬜ Meaningless'

    match['verified_grade'] = verified_grade
    match['warnings'] = warnings_list
    match['verification_detail'] = (
        f"grade={verified_grade}, p_bonf={p_bonferroni:.4f}, "
        f"trials≈{est_trials}, warnings={len(warnings_list)}"
    )

    return match


def verify_all(matches):
    """Apply verification pipeline to all discoveries."""
    return [verify_discovery(m) for m in matches]


# ─────────────────────────────────────────
# Output
# ─────────────────────────────────────────

def format_results(matches, cross_only=False):
    """Return sorted results as string"""
    if cross_only:
        matches = find_cross_island(matches)

    matches.sort(key=lambda x: -x['significance'])

    lines = []
    lines.append("=" * 80)
    lines.append("DFS Automatic Search Results")
    lines.append(f"Total {len(matches)} discoveries")
    lines.append("=" * 80)
    lines.append("")

    # Exact matches
    exact = [m for m in matches if m['is_exact']]
    if exact:
        lines.append(f"## Exact Matches ({len(exact)} items)")
        lines.append("")
        for m in exact:
            lines.append(f"  {m['formula']} = {m['target']}  "
                         f"[Islands: {m['islands']}]")
        lines.append("")

    # Approximate matches (cross-connections)
    cross = [m for m in matches if not m['is_exact'] and m['n_islands'] >= 2]
    if cross:
        lines.append(f"## Cross-connection Approximations ({len(cross)} items)")
        lines.append("")
        lines.append(f"  {'Formula':<45} {'Target':<15} {'Error%':>8}  {'Islands':>8}")
        lines.append(f"  {'-'*45} {'-'*15} {'-'*8}  {'-'*8}")
        for m in cross[:50]:
            lines.append(f"  {m['formula']:<45} {m['target']:<15} "
                         f"{m['error_pct']:>7.4f}%  {m['islands']:>8}")
        lines.append("")

    # Single-island approximations
    single = [m for m in matches if not m['is_exact'] and m['n_islands'] < 2]
    if single:
        lines.append(f"## Single-island Approximations ({len(single)} items, top 20)")
        lines.append("")
        for m in single[:20]:
            lines.append(f"  {m['formula']:<45} ~ {m['target']:<15} "
                         f"({m['error_pct']:.4f}%)")
        lines.append("")

    # Cross-connection statistics
    bridge_counts = {}
    for m in matches:
        if m['n_islands'] >= 2:
            key = m['islands']
            bridge_counts[key] = bridge_counts.get(key, 0) + 1
    if bridge_counts:
        lines.append("## Inter-island Bridge Statistics")
        lines.append("")
        for bridge, count in sorted(bridge_counts.items(),
                                     key=lambda x: -x[1]):
            lines.append(f"  {bridge}: {count} connections")
        lines.append("")

    return '\n'.join(lines)


def save_markdown(matches, depth, threshold, output_path):
    """Save results as markdown"""
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    lines = []
    lines.append(f"# DFS Automatic Search Results")
    lines.append(f"")
    lines.append(f"- Generated: {now}")
    lines.append(f"- depth: {depth}")
    lines.append(f"- threshold: {threshold} ({threshold*100}%)")
    lines.append(f"- Total discoveries: {len(matches)} items")
    lines.append(f"")

    # Exact matches
    exact = [m for m in matches if m['is_exact']]
    exact.sort(key=lambda x: -x['significance'])
    if exact:
        lines.append(f"## Exact Matches ({len(exact)} items)")
        lines.append(f"")
        lines.append("```")
        for m in exact:
            lines.append(f"  {m['formula']} = {m['target']}  "
                         f"[Islands: {m['islands']}]")
        lines.append("```")
        lines.append("")

    # Cross-connections (core)
    cross = sorted(find_cross_island(matches),
                   key=lambda x: -x['significance'])
    if cross:
        lines.append(f"## Cross-connection Discoveries ({len(cross)} items)")
        lines.append(f"")
        lines.append("| Formula | Target | Error% | Island Connection | Significance |")
        lines.append("|---------|--------|---------|-------------------|--------------|")
        for m in cross[:80]:
            exact_tag = " **exact**" if m['is_exact'] else ""
            lines.append(
                f"| `{m['formula']}` | {m['target']} | "
                f"{m['error_pct']:.5f}%{exact_tag} | "
                f"{m['islands']} | {m['significance']:.1f} |"
            )
        lines.append("")

    # Single-island top
    single = [m for m in matches if m['n_islands'] < 2 and not m['is_exact']]
    single.sort(key=lambda x: x['error'])
    if single:
        lines.append(f"## Single-island Approximations (top 30)")
        lines.append(f"")
        lines.append("| Formula | Target | Error% |")
        lines.append("|---------|--------|--------|")
        for m in single[:30]:
            lines.append(f"| `{m['formula']}` | {m['target']} | "
                         f"{m['error_pct']:.5f}% |")
        lines.append("")

    # Bridge statistics
    bridge_counts = {}
    for m in matches:
        if m['n_islands'] >= 2:
            key = m['islands']
            bridge_counts[key] = bridge_counts.get(key, 0) + 1
    if bridge_counts:
        lines.append("## Inter-island Bridge Summary")
        lines.append("")
        lines.append("```")
        for bridge, count in sorted(bridge_counts.items(),
                                     key=lambda x: -x[1]):
            bar = '#' * min(count, 50)
            lines.append(f"  {bridge:>8}: {count:>4} items  {bar}")
        lines.append("```")
        lines.append("")

    # Key discoveries (top 10 by significance)
    top10 = sorted(matches, key=lambda x: -x['significance'])[:10]
    if top10:
        lines.append("## Top 10 Key Discoveries")
        lines.append("")
        lines.append("```")
        for i, m in enumerate(top10, 1):
            tag = "EXACT" if m['is_exact'] else f"{m['error_pct']:.5f}%"
            lines.append(f"  {i:>2}. {m['formula']}")
            lines.append(f"      = {m['target']} ({tag})  "
                         f"[Islands: {m['islands']}, sig: {m['significance']:.1f}]")
        lines.append("```")
        lines.append("")

    content = '\n'.join(lines)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return output_path


# ─────────────────────────────────────────
# Main
# ─────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='DFS Automatic Search Engine — Systematic exploration of constant combinations')
    parser.add_argument('--depth', type=int, default=2,
                        help='Recursive combination depth (default: 2)')
    parser.add_argument('--threshold', type=float, default=0.001,
                        help='Error threshold (default: 0.001 = 0.1%%)')
    parser.add_argument('--cross-only', action='store_true',
                        help='Output cross-connections only')
    parser.add_argument('--top', type=int, default=5,
                        help='Maximum matches per target (default: 5)')
    parser.add_argument('--output', type=str,
                        default=None,
                        help='Result save path')
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = args.output or os.path.join(
        script_dir, 'docs', 'proofs', 'dfs-auto-results.md')

    print(f"DFS Automatic Search Engine")
    print(f"  depth:     {args.depth}")
    print(f"  threshold: {args.threshold} ({args.threshold*100}%)")
    print(f"  Output:    {output_path}")
    print()

    # Constant summary
    total_consts = sum(len(v) for v in ISLANDS.values())
    print(f"Input constants: {total_consts} items")
    for iid, consts in ISLANDS.items():
        names = ', '.join(consts.keys())
        print(f"  Island {iid}: {names}")
    print(f"Targets: {len(TARGETS)} items")
    print()

    # DFS build + target matching (all in Rust)
    print("Generating expressions and matching targets...")
    expr_count = build_level(args.depth)
    print(f"Total expressions: {expr_count:,} items")
    matches = check_targets(args.depth, threshold=args.threshold)
    print(f"Raw matches: {len(matches):,} items")

    # Filtering
    filtered = filter_best(matches, top_per_target=args.top)
    print(f"After filter: {len(filtered):,} items")

    # Verification pipeline
    print("Verifying...")
    filtered = verify_all(filtered)
    n_warnings = sum(1 for m in filtered if m.get('warnings'))
    n_passed = sum(1 for m in filtered if 'p>0.05' not in m.get('verified_grade', ''))
    print(f"Verification complete: {n_passed} passed, {n_warnings} warnings")

    cross = find_cross_island(filtered)
    print(f"Cross-connections: {len(cross):,} items")
    print()

    # Output
    print(format_results(filtered, cross_only=args.cross_only))

    # Verification summary output
    print("\n" + "=" * 60)
    print(" Verification Pipeline Results")
    print("=" * 60)
    for m in sorted(filtered, key=lambda x: -x['significance'])[:20]:
        grade = m.get('verified_grade', '?')
        warns = m.get('warnings', [])
        warn_str = f" ⚠ {'; '.join(warns)}" if warns else ""
        print(f"  {grade}")
        print(f"    {m['formula']} ≈ {m['target']} ({m['error_pct']:.5f}%)")
        if warn_str:
            print(f"   {warn_str}")
    print()

    # Save
    saved = save_markdown(filtered, args.depth, args.threshold, output_path)
    print(f"\nResults saved: {saved}")


if __name__ == '__main__':
    main()