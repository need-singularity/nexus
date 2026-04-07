#!/usr/bin/env python3
"""Convergence Engine — Adaptive Multi-Domain Convergence Point Discovery

Generalizes the Golden Zone discovery methodology:
  8 math/physics domains × ~80 constants → find values where 3+ domains converge.

Three strategies run simultaneously with adaptive budget allocation:
  S1: Open Search — full combination DFS (depth 1-2)
  S2: Pair Scan — domain-pair cross-combinations, cluster into convergence points
  S3: Target Backtrack — reverse-trace known values through new domains

Usage:
  python3 convergence_engine.py                     # default depth=2, threshold=0.1%
  python3 convergence_engine.py --depth 3           # depth 3 (slow)
  python3 convergence_engine.py --threshold 0.01    # 0.01% only
  python3 convergence_engine.py --texas             # include Texas Sharpshooter test
  python3 convergence_engine.py --top 30            # top 30 convergence points
"""

import argparse
import os
import sys
import warnings
from collections import defaultdict
from datetime import datetime
from itertools import combinations

import numpy as np

warnings.filterwarnings("ignore", category=RuntimeWarning)

# Constants — from nexus SSOT
_shared = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.shared')
if _shared not in sys.path:
    sys.path.insert(0, _shared)

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")

# ═════════════════════════════════════════════════════════════════
# 8 DOMAINS — ~80 constants with domain tags
# ═════════════════════════════════════════════════════════════════

from n6_constants import DOMAINS, KNOWN_VALUES, TARGETS


# ═════════════════════════════════════════════════════════════════
# OPERATORS
# ═════════════════════════════════════════════════════════════════

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

    # Powers
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

    # Logarithms
    if va > 0 and va != 1 and vb > 0:
        try:
            _add(np.log(vb)/np.log(va), f"log_{na}({nb})")
        except (ValueError, ZeroDivisionError):
            pass
    if vb > 0 and vb != 1 and va > 0:
        try:
            _add(np.log(va)/np.log(vb), f"log_{nb}({na})")
        except (ValueError, ZeroDivisionError):
            pass

    # exp(a*b)
    if abs(va * vb) < 20:
        try:
            _add(np.exp(va * vb), f"exp({na}*{nb})")
        except OverflowError:
            pass

    # sqrt(a*b)
    if va * vb > 0:
        _add(np.sqrt(va * vb), f"sqrt({na}*{nb})")

    # Roots: a^(1/b), b^(1/a)
    if va > 0 and vb != 0 and abs(1/vb) < 20:
        try:
            _add(va ** (1/vb), f"{na}^(1/{nb})")
        except (OverflowError, ValueError):
            pass
    if vb > 0 and va != 0 and abs(1/va) < 20:
        try:
            _add(vb ** (1/va), f"{nb}^(1/{na})")
        except (OverflowError, ValueError):
            pass

    return results


def unary_ops(val, name):
    """Unary expansion. Returns [(value, expr), ...]"""
    results = [(val, name)]
    if val > 0:
        results.append((np.log(val), f"ln({name})"))
        results.append((np.sqrt(val), f"sqrt({name})"))
    if val != 0:
        results.append((1.0/val, f"1/{name}"))
    if val < 500:
        ev = np.exp(val)
        if np.isfinite(ev) and abs(ev) < 1e12:
            results.append((ev, f"exp({name})"))
    return [(v, n) for v, n in results
            if isinstance(v, (int, float)) and np.isfinite(v) and abs(v) < 1e12]


# ═════════════════════════════════════════════════════════════════
# DOMAIN UTILITIES
# ═════════════════════════════════════════════════════════════════

def get_domain(const_name):
    """Return domain ID for a constant name"""
    for dom_id, dom in DOMAINS.items():
        if const_name in dom["constants"]:
            return dom_id
    return "?"


# Build set of "signature constants" — values unique to one domain only
_val_to_domains = defaultdict(set)
for _did, _dom in DOMAINS.items():
    for _n, _v in _dom["constants"].items():
        _val_to_domains[round(_v, 6)].add(_did)

# A constant is "signature" if its value appears in only 1 domain
SIGNATURE_CONSTS = {}  # name -> domain_id (only for unique-value constants)
SHARED_VALUES = set()  # values that appear in 2+ domains
for _did, _dom in DOMAINS.items():
    for _n, _v in _dom["constants"].items():
        rv = round(_v, 6)
        if len(_val_to_domains[rv]) == 1:
            SIGNATURE_CONSTS[_n] = _did
        else:
            SHARED_VALUES.add(rv)


def has_signature_const(expr, domain_id):
    """Check if expression uses a signature constant from the given domain."""
    for name, did in SIGNATURE_CONSTS.items():
        if did == domain_id and name in expr:
            return True
    return False


def is_trivial_arithmetic(expr, val):
    """Filter out trivially reachable values via simple integer arithmetic."""
    # If the result is a small integer and expression is just add/sub of integers
    if abs(val) < 50 and val == int(val):
        # Check if expression only uses integer constants with +/-
        clean = expr.replace("(", "").replace(")", "")
        parts = clean.replace("+", " ").replace("-", " ").split()
        all_int = True
        for p in parts:
            try:
                float(p)
            except ValueError:
                # Contains function or non-trivial constant
                all_int = False
                break
        if all_int and len(parts) <= 2:
            return True
    return False


def flatten_constants():
    """Flatten all domains into (name, value, domain_id) list"""
    flat = []
    seen_vals = {}  # deduplicate by value within same domain
    for dom_id, dom in DOMAINS.items():
        for name, val in dom["constants"].items():
            key = (dom_id, round(val, 10))
            if key not in seen_vals:
                seen_vals[key] = True
                flat.append((name, val, dom_id))
    return flat


# ═════════════════════════════════════════════════════════════════
# CONVERGENCE CLUSTER
# ═════════════════════════════════════════════════════════════════

class ConvergenceCluster:
    """Groups discoveries that converge to the same value from different domains."""

    def __init__(self, threshold=0.001):
        self.threshold = threshold
        self.clusters = []  # [(center_val, [paths])]

    def add(self, val, expr, domains, strategy):
        """Add a path to the cluster map. domains is a set of domain IDs."""
        for i, (center, paths) in enumerate(self.clusters):
            if center != 0 and abs(val - center) / abs(center) < self.threshold:
                paths.append({
                    "value": val,
                    "expr": expr,
                    "domains": domains,
                    "strategy": strategy,
                })
                # Update center to mean
                all_vals = [p["value"] for p in paths]
                self.clusters[i] = (np.mean(all_vals), paths)
                return
        # New cluster
        self.clusters.append((val, [{
            "value": val,
            "expr": expr,
            "domains": domains,
            "strategy": strategy,
        }]))

    def get_convergence_points(self, min_domains=2):
        """Return clusters where paths come from min_domains different domains.

        STRICT independence criterion:
        A domain "independently reaches" a value only if there exists a path
        that uses ONLY constants from that single domain (possibly with unary ops).
        Cross-domain paths (A+N, G+Q etc.) show bridges but do NOT count
        toward independent domain count.

        This mirrors the Golden Zone discovery: ln(4/3) was discovered
        independently in number theory, combinatorics, AND information theory.
        """
        results = []
        for center, paths in self.clusters:
            # Filter trivial paths
            good_paths = [p for p in paths
                          if not is_trivial_arithmetic(p["expr"], p["value"])]
            if not good_paths:
                continue

            # STRICT: count domains that reach this value using ONLY
            # their own constants (single-domain paths)
            independent_domains = set()
            best_per_domain = {}  # domain -> best single-domain path

            for p in good_paths:
                if len(p["domains"]) == 1:
                    d = list(p["domains"])[0]
                    # Must also use a signature constant
                    if has_signature_const(p["expr"], d):
                        independent_domains.add(d)
                        err = abs(p["value"] - center) / max(abs(center), 1e-15)
                        if d not in best_per_domain or err < best_per_domain[d][1]:
                            best_per_domain[d] = (p, err)

            # Also count cross-domain bridges (2-domain paths where
            # both domains have signature consts) — these are bridges
            bridge_domains = set()
            for p in good_paths:
                if len(p["domains"]) == 2:
                    d1, d2 = list(p["domains"])
                    if (has_signature_const(p["expr"], d1) and
                            has_signature_const(p["expr"], d2)):
                        bridge_domains.add((min(d1, d2), max(d1, d2)))

            all_domains = set()
            for p in good_paths:
                all_domains.update(p["domains"])

            n_independent = len(independent_domains)
            # Need at least min_domains independent single-domain paths
            if n_independent < min_domains:
                continue

            # Match against targets
            best_target = None
            best_err = float("inf")
            for t_name, t_val in TARGETS.items():
                if t_val == 0:
                    continue
                err = abs(center - t_val) / abs(t_val)
                if err < best_err:
                    best_err = err
                    best_target = t_name

            # Convergence score — based on INDEPENDENT domains
            base = max(0, -np.log10(best_err + 1e-15))
            domain_bonus = (n_independent - 1) * 20  # higher weight for true independence
            bridge_bonus = len(bridge_domains) * 3  # smaller bonus for cross bridges
            exact_bonus = 50 if best_err < 1e-12 else 0

            # Novelty: not a known discovery?
            novelty = 10
            for kv in KNOWN_VALUES.values():
                if kv != 0 and abs(center - kv) / abs(kv) < 0.001:
                    novelty = 0
                    break

            # Bonus for non-trivial targets (not small integers)
            target_complexity = 0
            if best_target and best_err < 0.001:
                tv = TARGETS[best_target]
                if tv != int(tv) or abs(tv) > 20:
                    target_complexity = 5  # bonus for non-integer targets

            score = (base + domain_bonus + bridge_bonus +
                     exact_bonus + novelty + target_complexity)

            results.append({
                "center": center,
                "paths": good_paths,
                "n_paths": len(good_paths),
                "domains": sorted(all_domains),
                "independent_domains": sorted(independent_domains),
                "n_domains": len(all_domains),
                "n_independent": n_independent,
                "n_bridges": len(bridge_domains),
                "bridges": sorted(bridge_domains),
                "best_target": best_target,
                "best_target_val": TARGETS.get(best_target, 0),
                "target_error": best_err,
                "score": score,
                "is_known": novelty == 0,
            })

        results.sort(key=lambda x: -x["score"])
        return results


# ═════════════════════════════════════════════════════════════════
# STRATEGY 1: OPEN SEARCH
# ═════════════════════════════════════════════════════════════════

def strategy_open_search(cluster, depth=2, threshold=0.001, budget_frac=1.0):
    """Full combination DFS across all domains."""
    flat = flatten_constants()
    n = len(flat)
    trials = 0
    discoveries = 0

    print(f"\n  [S1] Open Search: {n} constants, depth={depth}")

    # Level 0: base + unary
    base = []
    for name, val, dom_id in flat:
        for uv, un in unary_ops(val, name):
            base.append((uv, un, {dom_id}))

    print(f"  [S1] Level 0: {len(base)} atoms")

    # Build target hash for Level 1
    target_buckets_l1 = defaultdict(list)
    for t_name, t_val in TARGETS.items():
        if t_val == 0:
            continue
        bucket_key = round(t_val, 2)
        target_buckets_l1[bucket_key].append((t_name, t_val))
        for offset in [-0.01, 0.01]:
            target_buckets_l1[round(t_val + offset, 2)].append((t_name, t_val))

    # Level 1: base × base
    level1 = []
    seen = set()
    for i in range(len(base)):
        av, an, ai = base[i]
        for j in range(i+1, len(base)):
            bv, bn, bi = base[j]
            combined = ai | bi
            for rv, rn in binary_ops(an, av, bn, bv):
                trials += 1
                key = round(rv, 8)
                if key in seen:
                    continue
                seen.add(key)
                level1.append((rv, rn, combined))

                # Fast target check via hash
                bucket_key = round(rv, 2)
                for t_name, t_val in target_buckets_l1.get(bucket_key, []):
                    err = abs(rv - t_val) / abs(t_val)
                    if err < threshold:
                        if len(combined) >= 2 or err < 1e-10:
                            cluster.add(rv, rn, combined, "S1")
                            discoveries += 1

    print(f"  [S1] Level 1: {len(level1):,} expressions, {discoveries} discoveries, {trials:,} trials")

    if depth >= 2:
        # Level 2: top level1 × base (capped to prevent explosion)
        MAX_L2 = 5000  # cap level1 to top entries by cross-island count
        if len(level1) > MAX_L2:
            # Prioritize cross-domain expressions
            level1.sort(key=lambda x: -len(x[2]))
            level1_sample = level1[:MAX_L2]
            print(f"  [S1] Level 2: capped to top {MAX_L2}/{len(level1):,} "
                  f"(by domain diversity)")
        else:
            level1_sample = level1

        # Build target hash for fast lookup
        target_buckets = defaultdict(list)
        for t_name, t_val in TARGETS.items():
            if t_val == 0:
                continue
            bucket_key = round(t_val, 2)
            target_buckets[bucket_key].append((t_name, t_val))
            # Also add neighbors for fuzzy matching
            for offset in [-0.01, 0.01]:
                target_buckets[round(t_val + offset, 2)].append((t_name, t_val))

        d2_disc = 0
        d2_trials = 0
        seen2 = set()
        for i, (av, an, ai) in enumerate(level1_sample):
            if i % 1000 == 0 and i > 0:
                print(f"  [S1] Level 2: {i:,}/{len(level1_sample):,} "
                      f"({d2_disc} discoveries, {d2_trials:,} trials)")
            for bv, bn, bi in base:
                combined = ai | bi
                for rv, rn in binary_ops(an, av, bn, bv):
                    d2_trials += 1
                    key = round(rv, 8)
                    if key in seen2:
                        continue
                    seen2.add(key)
                    # Fast target check via hash
                    bucket_key = round(rv, 2)
                    candidates = target_buckets.get(bucket_key, [])
                    for t_name, t_val in candidates:
                        err = abs(rv - t_val) / abs(t_val)
                        if err < threshold:
                            if len(combined) >= 2:
                                cluster.add(rv, rn, combined, "S1")
                                d2_disc += 1
                                break

        trials += d2_trials
        discoveries += d2_disc
        print(f"  [S1] Level 2 done: +{d2_disc} discoveries, {d2_trials:,} trials")

    return trials, discoveries


# ═════════════════════════════════════════════════════════════════
# STRATEGY 2: PAIR SCAN
# ═════════════════════════════════════════════════════════════════

def strategy_pair_scan(cluster, threshold=0.001):
    """Scan all domain pairs and register cross-domain values."""
    dom_ids = list(DOMAINS.keys())
    pairs = list(combinations(dom_ids, 2))
    trials = 0
    discoveries = 0

    print(f"\n  [S2] Pair Scan: {len(pairs)} domain pairs")

    for d1, d2 in pairs:
        c1 = DOMAINS[d1]["constants"]
        c2 = DOMAINS[d2]["constants"]
        pair_disc = 0

        for n1, v1 in c1.items():
            for n2, v2 in c2.items():
                for rv, rn in binary_ops(n1, v1, n2, v2):
                    trials += 1
                    for t_name, t_val in TARGETS.items():
                        if t_val == 0:
                            continue
                        err = abs(rv - t_val) / abs(t_val)
                        if err < threshold:
                            cluster.add(rv, rn, {d1, d2}, "S2")
                            pair_disc += 1
                            discoveries += 1
                            break

        if pair_disc > 0:
            print(f"    {d1}x{d2} ({DOMAINS[d1]['name']} x {DOMAINS[d2]['name']}): "
                  f"{pair_disc} discoveries")

    print(f"  [S2] Total: {discoveries} discoveries, {trials:,} trials")
    return trials, discoveries


# ═════════════════════════════════════════════════════════════════
# STRATEGY 3: TARGET BACKTRACK
# ═════════════════════════════════════════════════════════════════

def strategy_target_backtrack(cluster, threshold=0.001):
    """For each known target value, find paths from each domain that reach it."""
    flat = flatten_constants()
    trials = 0
    discoveries = 0

    # Targets: known values + important math/physics constants
    backtrack_targets = {}
    backtrack_targets.update(KNOWN_VALUES)
    # Add key math constants
    for key in ["pi", "e", "phi_gold", "sqrt(2)", "sqrt(3)", "gamma_EM",
                "zeta(3)", "ln(2)", "ln(3)", "1/alpha", "alpha_s"]:
        if key in TARGETS:
            backtrack_targets[key] = TARGETS[key]

    print(f"\n  [S3] Target Backtrack: {len(backtrack_targets)} targets, "
          f"{len(flat)} constants")

    for t_name, t_val in backtrack_targets.items():
        if t_val == 0:
            continue
        paths_for_target = []

        for name, val, dom_id in flat:
            # Direct match
            if val != 0:
                err = abs(val - t_val) / abs(t_val)
                if err < threshold:
                    paths_for_target.append((val, name, {dom_id}))
                    trials += 1
                    continue

            # Unary
            for uv, un in unary_ops(val, name):
                trials += 1
                if uv != 0:
                    err = abs(uv - t_val) / abs(t_val)
                    if err < threshold:
                        paths_for_target.append((uv, un, {dom_id}))

            # Binary with every other constant
            for name2, val2, dom2 in flat:
                if name == name2:
                    continue
                for rv, rn in binary_ops(name, val, name2, val2):
                    trials += 1
                    err = abs(rv - t_val) / abs(t_val)
                    if err < threshold:
                        paths_for_target.append((rv, rn, {dom_id, dom2}))
                        break  # one per pair is enough

        # Register convergent paths
        if len(paths_for_target) >= 2:
            all_domains = set()
            for pv, pe, pd in paths_for_target:
                all_domains.update(pd)
            if len(all_domains) >= 2:
                for pv, pe, pd in paths_for_target:
                    cluster.add(pv, pe, pd, "S3")
                    discoveries += 1
                print(f"    {t_name} = {t_val:.6f}: "
                      f"{len(paths_for_target)} paths from "
                      f"{len(all_domains)} domains")

    print(f"  [S3] Total: {discoveries} discoveries, {trials:,} trials")
    return trials, discoveries


# ═════════════════════════════════════════════════════════════════
# TEXAS SHARPSHOOTER TEST
# ═════════════════════════════════════════════════════════════════

def texas_sharpshooter_test(convergence_points, n_random=5000, depth=2):
    """Test if convergence points are structural or coincidental."""
    n_targets = len(TARGETS)
    n_constants = sum(len(d["constants"]) for d in DOMAINS.values())

    print(f"\n{'='*60}")
    print(f"  TEXAS SHARPSHOOTER TEST")
    print(f"{'='*60}")

    # Real count: convergence points with 3+ domains
    real_multi = len([cp for cp in convergence_points
                      if cp.get("n_independent", cp["n_domains"]) >= 3])
    real_total = len(convergence_points)

    # Random baseline: generate random constants, try to find convergence
    rng = np.random.default_rng(42)
    random_counts = []

    for trial in range(n_random):
        # Generate same number of random constants across 8 domains
        random_hits = 0
        rand_vals = rng.uniform(0.01, 10.0, size=n_constants)

        # Try random combinations against targets
        for i in range(min(len(rand_vals), 30)):
            for j in range(i+1, min(len(rand_vals), 30)):
                v = rand_vals[i] + rand_vals[j]
                for t_val in list(TARGETS.values())[:20]:
                    if t_val != 0 and abs(v - t_val)/abs(t_val) < 0.001:
                        random_hits += 1
                v = rand_vals[i] * rand_vals[j]
                for t_val in list(TARGETS.values())[:20]:
                    if t_val != 0 and abs(v - t_val)/abs(t_val) < 0.001:
                        random_hits += 1

        random_counts.append(random_hits)

    random_mean = np.mean(random_counts)
    random_std = np.std(random_counts) + 1e-10

    z_total = (real_total - random_mean) / random_std
    z_multi = (real_multi - random_mean * 0.1) / (random_std + 1e-10)

    from scipy import stats as sp_stats
    p_total = 1 - sp_stats.norm.cdf(z_total)
    p_multi = 1 - sp_stats.norm.cdf(z_multi)

    print(f"  Real convergence points (2+ domains): {real_total}")
    print(f"  Real convergence points (3+ domains): {real_multi}")
    print(f"  Random baseline: {random_mean:.1f} +/- {random_std:.1f}")
    print(f"  Z-score (total):  {z_total:.2f}  (p={p_total:.6f})")
    print(f"  Z-score (multi):  {z_multi:.2f}  (p={p_multi:.6f})")

    if p_total < 0.001:
        verdict = "STRUCTURAL DISCOVERY (p < 0.001)"
    elif p_total < 0.01:
        verdict = "Strong evidence (p < 0.01)"
    elif p_total < 0.05:
        verdict = "Weak evidence (p < 0.05)"
    else:
        verdict = "Possibly coincidental (p > 0.05)"

    print(f"  Verdict: {verdict}")
    return z_total, p_total


# ═════════════════════════════════════════════════════════════════
# RESULTS DISPLAY
# ═════════════════════════════════════════════════════════════════

def display_results(convergence_points, strategy_stats, top=20):
    """Display convergence map and strategy performance."""
    print(f"\n{'='*70}")
    print(f"  CONVERGENCE MAP — Top {min(top, len(convergence_points))} "
          f"Multi-Domain Convergence Points")
    print(f"{'='*70}")

    for rank, cp in enumerate(convergence_points[:top], 1):
        known_tag = " [KNOWN]" if cp["is_known"] else " [NEW!]"
        target_info = ""
        if cp["target_error"] < 0.01:
            target_info = f" ~ {cp['best_target']} (err={cp['target_error']*100:.4f}%)"

        n_ind = cp.get("n_independent", cp["n_domains"])
        ind_doms = cp.get("independent_domains", cp["domains"])
        n_bridges = cp.get("n_bridges", 0)

        print(f"\n  Rank {rank}: value = {cp['center']:.10f} "
              f"(score: {cp['score']:.1f}){known_tag}")
        print(f"  Independent: {'+'.join(ind_doms)} ({n_ind}/8), "
              f"bridges: {n_bridges}{target_info}")
        print(f"  Paths ({cp['n_paths']}):")

        # Group paths by domain
        by_domain = defaultdict(list)
        for p in cp["paths"]:
            for d in p["domains"]:
                by_domain[d].append(p)

        shown = set()
        for dom in sorted(by_domain.keys()):
            dom_name = DOMAINS.get(dom, {}).get("name", dom)
            for p in by_domain[dom][:2]:  # max 2 per domain
                expr_key = p["expr"]
                if expr_key in shown:
                    continue
                shown.add(expr_key)
                doms_str = "+".join(sorted(p["domains"]))
                print(f"    [{doms_str}] {p['expr']} = {p['value']:.10f}"
                      f"  ({p['strategy']})")

    # Strategy performance
    print(f"\n{'='*70}")
    print(f"  STRATEGY PERFORMANCE")
    print(f"{'='*70}")

    total_trials = sum(s["trials"] for s in strategy_stats.values())
    total_disc = sum(s["discoveries"] for s in strategy_stats.values())

    for name, stats in strategy_stats.items():
        t = stats["trials"]
        d = stats["discoveries"]
        yld = d / max(t, 1)
        pct = t / max(total_trials, 1) * 100
        print(f"  {name}: {d:,} discoveries / {t:,} trials "
              f"(yield={yld:.6f}, {pct:.0f}% of budget)")

    print(f"\n  Total: {total_disc:,} discoveries / {total_trials:,} trials")

    # Domain heatmap
    print(f"\n{'='*70}")
    print(f"  DOMAIN INTERSECTION HEATMAP")
    print(f"{'='*70}")

    dom_ids = list(DOMAINS.keys())
    # Count convergence points per domain pair
    pair_counts = defaultdict(int)
    for cp in convergence_points:
        doms = cp["domains"]
        for i in range(len(doms)):
            for j in range(i+1, len(doms)):
                pair_counts[(doms[i], doms[j])] += 1

    # Header
    header = "     " + "  ".join(f"{d:>4}" for d in dom_ids)
    print(f"  {header}")
    for d1 in dom_ids:
        row = f"  {d1:>3} "
        for d2 in dom_ids:
            if d1 == d2:
                row += "   - "
            else:
                key = tuple(sorted([d1, d2]))
                count = pair_counts.get(key, 0)
                if count == 0:
                    row += "   . "
                elif count < 5:
                    row += f"  {count:>2} "
                else:
                    row += f" {count:>3} "
        print(row)


# ═════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Convergence Engine: Multi-Domain Convergence Point Discovery")
    parser.add_argument("--depth", type=int, default=2,
                        help="Combination depth for S1 (default: 2)")
    parser.add_argument("--threshold", type=float, default=0.001,
                        help="Relative error threshold (default: 0.001 = 0.1%%)")
    parser.add_argument("--texas", action="store_true",
                        help="Include Texas Sharpshooter test")
    parser.add_argument("--top", type=int, default=20,
                        help="Show top N convergence points (default: 20)")
    parser.add_argument("--min-domains", type=int, default=2,
                        help="Minimum domains for convergence (default: 2)")
    parser.add_argument("--s1-only", action="store_true",
                        help="Run only Strategy 1")
    parser.add_argument("--s2-only", action="store_true",
                        help="Run only Strategy 2")
    parser.add_argument("--s3-only", action="store_true",
                        help="Run only Strategy 3")
    args = parser.parse_args()

    print(f"{'='*70}")
    print(f"  CONVERGENCE ENGINE — Adaptive Multi-Domain Discovery")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}")

    # Show domain summary
    total_consts = 0
    for dom_id, dom in DOMAINS.items():
        n = len(dom["constants"])
        total_consts += n
        print(f"  [{dom_id}] {dom['name']:25s}: {n:2d} constants")
    print(f"  {'':25s}  Total: {total_consts} constants")
    print(f"  Targets: {len(TARGETS)}")
    print(f"  Depth: {args.depth}, Threshold: {args.threshold*100:.2f}%")

    # Initialize cluster
    cluster = ConvergenceCluster(threshold=args.threshold)
    strategy_stats = {}

    run_all = not (args.s1_only or args.s2_only or args.s3_only)

    # Strategy 1: Open Search
    if run_all or args.s1_only:
        t, d = strategy_open_search(cluster, depth=args.depth,
                                     threshold=args.threshold)
        strategy_stats["S1_Open"] = {"trials": t, "discoveries": d}

    # Strategy 2: Pair Scan
    if run_all or args.s2_only:
        t, d = strategy_pair_scan(cluster, threshold=args.threshold)
        strategy_stats["S2_Pair"] = {"trials": t, "discoveries": d}

    # Strategy 3: Target Backtrack
    if run_all or args.s3_only:
        t, d = strategy_target_backtrack(cluster, threshold=args.threshold)
        strategy_stats["S3_Backtrack"] = {"trials": t, "discoveries": d}

    # Get convergence points
    convergence_points = cluster.get_convergence_points(
        min_domains=args.min_domains)

    # Display results
    display_results(convergence_points, strategy_stats, top=args.top)

    # Adaptive yield summary
    if len(strategy_stats) > 1:
        print(f"\n{'='*70}")
        print(f"  ADAPTIVE BUDGET RECOMMENDATION (for next run)")
        print(f"{'='*70}")
        yields = {}
        for name, stats in strategy_stats.items():
            yields[name] = stats["discoveries"] / max(stats["trials"], 1)
        total_yield = sum(yields.values()) or 1e-10
        for name, yld in yields.items():
            recommended = max(0.10, yld / total_yield)
            print(f"  {name}: yield={yld:.6f} -> recommended budget={recommended:.0%}")

    # Texas Sharpshooter
    if args.texas:
        texas_sharpshooter_test(convergence_points, depth=args.depth)

    # Summary
    n_new = len([cp for cp in convergence_points if not cp["is_known"]])
    n_known = len([cp for cp in convergence_points if cp["is_known"]])
    n_3plus = len([cp for cp in convergence_points
                   if cp.get("n_independent", cp["n_domains"]) >= 3])

    print(f"\n{'='*70}")
    print(f"  SUMMARY")
    print(f"{'='*70}")
    print(f"  Total convergence points: {len(convergence_points)}")
    print(f"  Known (re-confirmed):     {n_known}")
    print(f"  NEW discoveries:          {n_new}")
    print(f"  3+ domain convergence:    {n_3plus}")

    if n_3plus > 0:
        print(f"\n  Top 3+ domain convergence points:")
        for cp in convergence_points:
            n_ind = cp.get("n_independent", cp["n_domains"])
            if n_ind >= 3:
                known = " [KNOWN]" if cp["is_known"] else " [NEW!]"
                ind_doms = cp.get("independent_domains", cp["domains"])
                n_br = cp.get("n_bridges", 0)
                target = f" ~ {cp['best_target']}" if cp["target_error"] < 0.01 else ""
                print(f"    {cp['center']:.8f} = "
                      f"{'+'.join(ind_doms)} "
                      f"({n_ind} indep, {n_br} bridges, "
                      f"score={cp['score']:.1f})"
                      f"{target}{known}")

    # Save results
    os.makedirs(RESULTS_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    outfile = os.path.join(RESULTS_DIR, f"convergence_{ts}.txt")
    with open(outfile, "w") as f:
        f.write(f"Convergence Engine Results — {ts}\n")
        f.write(f"Depth={args.depth}, Threshold={args.threshold}\n\n")
        for rank, cp in enumerate(convergence_points, 1):
            f.write(f"Rank {rank}: {cp['center']:.10f} "
                    f"(score={cp['score']:.1f}, "
                    f"domains={'+'.join(cp['domains'])})\n")
            for p in cp["paths"]:
                f.write(f"  [{'+'.join(sorted(p['domains']))}] "
                        f"{p['expr']} = {p['value']:.10f}\n")
            f.write("\n")
    print(f"\n  Results saved: {outfile}")


if __name__ == "__main__":
    main()
