#!/usr/bin/env python3
"""Discovery Loop — TECS-L Infinite Self-Improving Discovery Engine

Orchestrates all 6 TECS-L engines in a closed loop:
  DFS → Convergence → Quantum Formula → Perfect Number → Verify → Grow → Paper → Repeat

Inspired by:
  - nexus OUROBOROS: 2-level loop + mutation + convergence detection + lens forging
  - anima closed-loop: checkpoint→scan→law discovery→intervention→next cycle
  - anima growth: 5-stage developmental progression

Architecture:
  ┌─────────────────────────────────────────────────────────┐
  │                   DISCOVERY LOOP                        │
  │                                                         │
  │  ┌──────┐  ┌──────────┐  ┌─────────┐  ┌──────────┐    │
  │  │ DFS  │→ │Convergence│→ │ Quantum │→ │ Perfect  │    │
  │  └──┬───┘  └────┬─────┘  └────┬────┘  └────┬─────┘    │
  │     │           │              │             │          │
  │     └───────────┴──────────────┴─────────────┘          │
  │                         │                               │
  │                    ��────▼────┐                          │
  │                    │ Verify  │  Texas + Grade            │
  │                    └────┬────┘                          │
  │                         │                               │
  │                    ┌────▼────┐                          │
  │                    │  Grow   │  Feed back discoveries    │
  │                    │         │  as new constants/atoms   │
  │                    └────┬────┘                          │
  │                         │                               │
  │                    ┌────▼────┐                          │
  │                    │ Paper?  │  Auto-generate if         │
  │                    │         │  threshold met            │
  │                    └────┬────┘                          │
  │                         │                               │
  │                    ┌────▼────┐                          │
  │                    │Converge?│  Saturated → forge new    │
  │                    │         │  constants → continue     │
  │                    └─────────┘                          │
  └─────────────────────────────────────────────────────────┘

Usage:
  python3 discovery_loop.py                    # default: 6 cycles
  python3 discovery_loop.py --cycles 0         # infinite (until saturated)
  python3 discovery_loop.py --cycles 12        # 12 cycles
  python3 discovery_loop.py --paper            # auto-generate paper drafts
  python3 discovery_loop.py --threshold 0.0001 # tighter matching
"""

import argparse
import json
import math
import os
import re
import signal
import subprocess
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

import numpy as np

# ─────────────────────────────────────────
# SSOT constants
# ─────────────────────────────────────────
_shared = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.shared')
if _shared not in sys.path:
    sys.path.insert(0, _shared)

from n6_constants import (
    N, SIGMA, TAU, PHI, SOPFR, JORDAN_J2, MOBIUS_MU,
    GZ_CENTER, GZ_WIDTH, GZ_LOWER, GZ_UPPER,
    ISLANDS, TARGETS, DOMAINS, KNOWN_VALUES,
    BASE_CONSTANTS,
)

# ─────────────────────────────────────────
# Engine imports (lazy — only when needed)
# ─────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(SCRIPT_DIR, 'results', 'loop')
STATE_FILE = os.path.join(RESULTS_DIR, 'loop_state.json')
DISCOVERIES_FILE = os.path.join(RESULTS_DIR, 'discoveries.jsonl')
PAPER_DIR = os.path.join(SCRIPT_DIR, 'docs', 'papers', 'auto')
NEXUS_ROOT = os.path.expanduser('~/Dev/nexus')
GROWTH_BUS = os.path.join(NEXUS_ROOT, 'shared', 'growth_bus.jsonl')
DISCOVERY_LOG = os.path.join(NEXUS_ROOT, 'shared', 'discovery_log.jsonl')
DSE_BIN = os.path.join(NEXUS_ROOT, 'shared', 'dse', 'universal-dse')
DSE_DOMAINS_DIR = os.path.join(NEXUS_ROOT, 'shared', 'dse', 'domains')

os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(PAPER_DIR, exist_ok=True)


# ═════════════════════════════════════════════════════════════════
# DISCOVERY RECORD
# ═════════════════════════════════════════════════════════════════

class Discovery:
    """A single discovery from any engine."""
    def __init__(self, formula, value, target, error, engine, domains=None,
                 grade='', cycle=0, timestamp=None):
        self.formula = formula
        self.value = value
        self.target = target
        self.error = error
        self.engine = engine
        self.domains = domains or []
        self.grade = grade  # 🟩 🟧 ⚪ ⬛
        self.cycle = cycle
        self.timestamp = timestamp or datetime.now().isoformat()
        self.is_novel = True
        self.paper_worthy = False
        self.consensus = 0  # n lenses agreeing (3-way validation)
        self.validate_externally = False  # flag: needs WebSearch novelty check
        self.external_validated = False   # True after Claude confirms novelty via WebSearch
        self.synergy_score = None  # DSE cross-domain synergy (0-1), None if not evaluated

    def to_dict(self):
        return {
            'formula': self.formula, 'value': self.value,
            'target': self.target, 'error': self.error,
            'engine': self.engine, 'domains': self.domains,
            'grade': self.grade, 'cycle': self.cycle,
            'timestamp': self.timestamp, 'is_novel': self.is_novel,
            'paper_worthy': self.paper_worthy, 'consensus': self.consensus,
            'validate_externally': self.validate_externally,
            'external_validated': self.external_validated,
            'synergy_score': self.synergy_score,
        }

    @classmethod
    def from_dict(cls, d):
        disc = cls(d['formula'], d['value'], d['target'], d['error'],
                   d['engine'], d.get('domains', []), d.get('grade', ''),
                   d.get('cycle', 0), d.get('timestamp'))
        disc.is_novel = d.get('is_novel', True)
        disc.paper_worthy = d.get('paper_worthy', False)
        disc.consensus = d.get('consensus', 0)
        disc.validate_externally = d.get('validate_externally', False)
        disc.external_validated = d.get('external_validated', False)
        disc.synergy_score = d.get('synergy_score')
        return disc


# ═════════════════════════════════════════════════════════════════
# CONVERGENCE TRACKER (from nexus ouroboros pattern)
# ═════════════════════════════════════════════════════════════════

class ConvergenceTracker:
    """Tracks discovery rate across cycles to detect saturation."""

    def __init__(self, window=SIGMA - PHI):  # σ-φ=10 window (nexus style)
        self.history = []  # (cycle, n_discoveries, n_novel)
        self.window = window

    def record(self, cycle, n_discoveries, n_novel):
        self.history.append((cycle, n_discoveries, n_novel))

    @property
    def status(self):
        if len(self.history) < 3:
            return 'exploring'
        recent = self.history[-self.window:]
        novel_counts = [h[2] for h in recent]
        if len(recent) >= 3 and all(n == 0 for n in novel_counts[-3:]):
            return 'saturated'
        if len(recent) >= 3 and novel_counts[-1] < novel_counts[0] * 0.5:
            return 'converging'
        return 'exploring'

    @property
    def total_discoveries(self):
        return sum(h[1] for h in self.history)

    @property
    def total_novel(self):
        return sum(h[2] for h in self.history)


# ═════════════════════════════════════════════════════════════════
# GROWTH ENGINE (from anima developmental stages)
# ═════════════════════════════════════════════════════════════════

class GrowthEngine:
    """Manages the loop's growth by feeding discoveries back as new constants."""

    # Developmental stages (anima-inspired)
    STAGES = [
        {'name': 'seed',    'min_discoveries': 0,   'depth': 2, 'threshold': 0.001},
        {'name': 'sprout',  'min_discoveries': 10,  'depth': 2, 'threshold': 0.0005},
        {'name': 'sapling', 'min_discoveries': 50,  'depth': 2, 'threshold': 0.0001},
        {'name': 'tree',    'min_discoveries': 200, 'depth': 3, 'threshold': 0.0001},
        {'name': 'forest',  'min_discoveries': 500, 'depth': 3, 'threshold': 0.00005},
        {'name': 'cosmos',  'min_discoveries': 1000,'depth': 3, 'threshold': 0.00001},
    ]

    def __init__(self):
        self.stage_idx = 0
        self.injected_constants = {}  # name -> value (discovered constants fed back)
        self.all_discoveries = []

    @property
    def stage(self):
        return self.STAGES[self.stage_idx]

    @property
    def depth(self):
        return self.stage['depth']

    @property
    def threshold(self):
        return self.stage['threshold']

    def check_stage_up(self):
        """Check if we should advance to next developmental stage."""
        n = len(self.all_discoveries)
        while (self.stage_idx < len(self.STAGES) - 1 and
               n >= self.STAGES[self.stage_idx + 1]['min_discoveries']):
            self.stage_idx += 1
            print(f"  ★ STAGE UP → {self.stage['name']} "
                  f"(depth={self.depth}, threshold={self.threshold})")

    def absorb(self, discoveries):
        """Feed discoveries back as new constants for next cycle."""
        new_count = 0
        for d in discoveries:
            self.all_discoveries.append(d)
            if d.grade in ('🟩', '🟧') and d.is_novel:
                key = f"disc_{len(self.injected_constants)}"
                if d.value not in self.injected_constants.values():
                    self.injected_constants[key] = d.value
                    new_count += 1
        if new_count:
            print(f"  → {new_count} discoveries injected as new constants "
                  f"(total pool: {len(self.injected_constants)})")
        self.check_stage_up()

    def get_augmented_islands(self):
        """Return ISLANDS augmented with discovered constants."""
        augmented = {}
        for k, v in ISLANDS.items():
            augmented[k] = dict(v)
        # Add discovered constants as new island 'X' (cross-discoveries)
        if self.injected_constants:
            augmented['X'] = dict(self.injected_constants)
        return augmented


# ═════════════════════════════════════════════════════════════════
# DISCOVERY GRAPH (from nexus OUROBOROS persistent graph)
# ═════════════════════════════════════════════════════════════════

GRAPH_FILE = os.path.join(RESULTS_DIR, 'discovery_graph.json')


class DiscoveryGraph:
    """Persistent graph where discoveries are nodes and relationships are edges.

    Mirrors nexus OUROBOROS graph: nodes = discoveries, edges = derives/supports/bridges.
    Internally stored as adjacency dict for efficient hub detection.
    """

    def __init__(self):
        self.nodes = {}       # id -> {value, grade, engine, cycle, target, formula}
        self.adjacency = {}   # id -> [{neighbor, relation}, ...]
        self._next_id = 0

    def add_node(self, discovery):
        """Add a discovery as a graph node. Returns the node id."""
        node_id = f"d{self._next_id}"
        self._next_id += 1
        self.nodes[node_id] = {
            'id': node_id,
            'value': discovery.value,
            'grade': discovery.grade,
            'engine': discovery.engine,
            'cycle': discovery.cycle,
            'target': discovery.target,
            'formula': discovery.formula,
        }
        self.adjacency[node_id] = []
        return node_id

    def add_edge(self, d1, d2, relation):
        """Add an undirected edge: d1 --relation-- d2.

        Relations:
          'derives'  -- d2 value derived from d1
          'supports' -- both target the same quantity
          'bridges'  -- cross-engine, same value within tolerance
        """
        if d1 not in self.nodes or d2 not in self.nodes:
            return
        edge_fwd = {'neighbor': d2, 'relation': relation}
        edge_rev = {'neighbor': d1, 'relation': relation}
        if edge_fwd not in self.adjacency[d1]:
            self.adjacency[d1].append(edge_fwd)
        if edge_rev not in self.adjacency[d2]:
            self.adjacency[d2].append(edge_rev)

    def auto_link(self, new_id, all_ids):
        """Automatically detect and add relationships for a new node.

        Rules:
          - Same target -> 'supports'
          - Different engines, values within 0.1% -> 'bridges'
          - One node's value appears in another's formula string -> 'derives'
        """
        new_node = self.nodes.get(new_id)
        if not new_node:
            return

        for other_id in all_ids:
            if other_id == new_id:
                continue
            other = self.nodes[other_id]

            # supports: same target
            if (new_node['target'] and other['target']
                    and new_node['target'] == other['target']):
                self.add_edge(new_id, other_id, 'supports')
                continue

            # bridges: different engines, values within 0.1%
            if new_node['engine'] != other['engine']:
                if other['value'] != 0:
                    rel_err = abs(new_node['value'] - other['value']) / abs(other['value'])
                    if rel_err < 0.001:
                        self.add_edge(new_id, other_id, 'bridges')
                        continue

            # derives: one's value string appears in other's formula
            val_str = f"{other['value']:.6g}"
            if len(val_str) >= 3 and val_str in new_node.get('formula', ''):
                self.add_edge(other_id, new_id, 'derives')

    def get_hubs(self, min_edges=3):
        """Return highly-connected nodes (hubs) sorted by edge count descending."""
        hubs = []
        for node_id, edges in self.adjacency.items():
            if len(edges) >= min_edges:
                hubs.append({
                    'id': node_id,
                    'edges': len(edges),
                    'node': self.nodes[node_id],
                    'relations': edges,
                })
        hubs.sort(key=lambda h: -h['edges'])
        return hubs

    def save(self, filepath=None):
        """Save graph to JSON."""
        filepath = filepath or GRAPH_FILE
        with open(filepath, 'w') as f:
            json.dump({
                'nodes': self.nodes,
                'adjacency': self.adjacency,
                'next_id': self._next_id,
            }, f, indent=2, ensure_ascii=False)

    def load(self, filepath=None):
        """Load graph from JSON."""
        filepath = filepath or GRAPH_FILE
        if not os.path.exists(filepath):
            return
        with open(filepath) as f:
            data = json.load(f)
        self.nodes = data.get('nodes', {})
        self.adjacency = data.get('adjacency', {})
        self._next_id = data.get('next_id', 0)


# ═════════════════════════════════════════════════════════════════
# MUTATION ENGINE (from nexus ouroboros/mutation.rs)
# ═════════════════════════════════════════════════════════════════

# Domain transfer targets for Strategy 3
TRANSFER_DOMAINS = ['number_theory', 'topology', 'physics', 'information',
                    'biology', 'consciousness', 'quantum', 'thermodynamics']


def mutate_targets(discoveries, existing_targets):
    """Generate new target values from discoveries (nexus mutation strategies)."""
    new_targets = {}
    n6 = [N, SIGMA, TAU, PHI, SOPFR, JORDAN_J2]

    for d in discoveries:
        if d.grade not in ('🟩', '🟧'):
            continue
        v = d.value

        # Strategy 1: Parameter shift (apply n=6 constants)
        for name, c in BASE_CONSTANTS.items():
            if c == 0:
                continue
            candidate = v * c
            if 1e-10 < abs(candidate) < 1e10:
                key = f"mut_{d.target}*{name}"
                if key not in existing_targets:
                    new_targets[key] = candidate
            candidate = v / c
            if 1e-10 < abs(candidate) < 1e10:
                key = f"mut_{d.target}/{name}"
                if key not in existing_targets:
                    new_targets[key] = candidate

        # Strategy 2: Combination (bridge discovered values)
        for d2 in discoveries:
            if d2 is d or d2.grade not in ('🟩', '🟧'):
                continue
            combo = v + d2.value
            key = f"mut_{d.target}+{d2.target}"
            if 1e-10 < abs(combo) < 1e10 and key not in existing_targets:
                new_targets[key] = combo

        # Strategy 3: DomainTransfer — cross-engine hypothesis
        # Take a discovery and suggest testing in other domains
        d_domains = set(d.domains) if d.domains else set()
        for domain in TRANSFER_DOMAINS:
            if domain not in d_domains:
                key = f"transfer_{d.target}>{domain}"
                if key not in existing_targets:
                    new_targets[key] = v  # same value, new context

        # Strategy 4: Inversion — reciprocal and negation
        if v != 0:
            key_recip = f"inv_1/{d.target}"
            if key_recip not in existing_targets:
                recip = 1.0 / v
                if 1e-10 < abs(recip) < 1e10:
                    new_targets[key_recip] = recip
            key_neg = f"inv_-{d.target}"
            if key_neg not in existing_targets:
                new_targets[key_neg] = -v

    return new_targets


# ═════════════════════════════════════════════════════════════════
# ENGINE RUNNERS (wrap existing one-shot engines)
# ═════════════════════════════════════════════════════════════════

def run_with_timeout(func, timeout=30):
    """Run function with timeout — prevents engine blocking.

    signal.alarm only works in the main thread; when called from a
    ThreadPoolExecutor worker, skip the alarm and run without timeout.
    """
    import threading
    if threading.current_thread() is not threading.main_thread():
        # Cannot use signal.alarm in non-main thread — run directly
        return func()

    def handler(signum, frame):
        raise TimeoutError(f"Engine timed out after {timeout}s")

    old = signal.signal(signal.SIGALRM, handler)
    signal.alarm(timeout)
    try:
        result = func()
    except TimeoutError:
        result = []
        print(f"  ⏰ Timeout after {timeout}s")
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old)
    return result


def _dfs_python_fallback(depth, threshold, augmented_islands=None):
    """Pure Python DFS search fallback when tecsrs.DfsEngine is unavailable.

    Performs brute-force constant combination search over ISLANDS/TARGETS,
    mirroring what the Rust DfsEngine does but slower.
    """
    islands = augmented_islands if augmented_islands else ISLANDS
    # Flatten all constants
    all_consts = {}
    island_map = {}  # name -> island_id
    for isl_id, consts in islands.items():
        for name, val in consts.items():
            all_consts[name] = float(val)
            island_map[name] = isl_id

    names = list(all_consts.keys())
    vals = [all_consts[n] for n in names]
    matches = []

    def _ops(na, va, nb, vb):
        """Binary operations between two constants."""
        results = []
        results.append((va + vb, f"({na}+{nb})"))
        results.append((va - vb, f"({na}-{nb})"))
        results.append((vb - va, f"({nb}-{na})"))
        results.append((va * vb, f"({na}*{nb})"))
        if vb != 0:
            results.append((va / vb, f"({na}/{nb})"))
        if va != 0:
            results.append((vb / va, f"({nb}/{na})"))
        if va > 0 and abs(vb) < 20:
            try:
                results.append((va ** vb, f"({na}^{nb})"))
            except (OverflowError, ValueError):
                pass
        if vb > 0 and abs(va) < 20:
            try:
                results.append((vb ** va, f"({nb}^{na})"))
            except (OverflowError, ValueError):
                pass
        return results

    def _check(val, expr, used_names):
        for t_name, t_val in TARGETS.items():
            if t_val == 0:
                continue
            try:
                rel_err = abs(val - float(t_val)) / abs(float(t_val))
            except (TypeError, ZeroDivisionError):
                continue
            if rel_err < threshold:
                used_islands = set(island_map.get(n, '?') for n in used_names)
                matches.append({
                    'target': t_name,
                    'target_val': float(t_val),
                    'formula': expr,
                    'formula_val': val,
                    'error': rel_err,
                    'error_pct': rel_err * 100,
                    'islands': list(used_islands),
                    'n_islands': len(used_islands),
                    'significance': 1.0 / max(rel_err, 1e-15),
                    'is_exact': rel_err < 1e-12,
                })

    # depth-1: single constants
    for i, (n, v) in enumerate(zip(names, vals)):
        if np.isfinite(v):
            _check(v, n, [n])

    # depth-2: binary combinations
    if depth >= 2:
        for i in range(len(names)):
            for j in range(i, len(names)):
                na, va = names[i], vals[i]
                nb, vb = names[j], vals[j]
                if not (np.isfinite(va) and np.isfinite(vb)):
                    continue
                for val, expr in _ops(na, va, nb, vb):
                    if np.isfinite(val) and abs(val) < 1e15:
                        _check(val, expr, [na, nb])

    print(f"  [DFS-py] {len(matches):,} matches found (Python fallback, depth={depth})")
    return matches


def run_dfs(depth, threshold, augmented_islands=None):
    """Run DFS engine and return discoveries."""
    # Try Rust-powered DFS first, fall back to pure Python
    rust_available = False
    try:
        import tecsrs
        tecsrs.DfsEngine  # check attribute exists
        rust_available = True
    except (ImportError, AttributeError):
        pass

    if rust_available:
        try:
            from dfs_engine import build_level, check_targets, filter_best, verify_all
        except ImportError as e:
            print(f"  [DFS] Import error: {e}")
            rust_available = False

    def _run():
        if rust_available:
            expr_count = build_level(depth)
            matches = check_targets(depth, threshold=threshold)
        else:
            matches = _dfs_python_fallback(depth, threshold, augmented_islands)

        if not matches:
            return []

        # Sort and keep best per target
        by_target = {}
        for m in matches:
            key = m['target']
            if key not in by_target:
                by_target[key] = []
            by_target[key].append(m)
        filtered = []
        for key, group in by_target.items():
            group.sort(key=lambda x: (-x.get('n_islands', 0), x.get('error', 1)))
            filtered.extend(group[:TAU])

        if rust_available:
            from dfs_engine import verify_all
            filtered = verify_all(filtered)

        discoveries = []
        for m in filtered:
            d = Discovery(
                formula=m.get('formula', m.get('expr', '')),
                value=m.get('formula_val', m.get('value', 0)),
                target=m.get('target', m.get('target_name', '')),
                error=m.get('error', 1.0),
                engine='dfs',
                grade=m.get('grade', ''),
            )
            discoveries.append(d)
        return discoveries

    try:
        return run_with_timeout(_run, timeout=30)
    except Exception as e:
        print(f"  [DFS] Error: {e}")
        return []


def run_convergence(depth, threshold):
    """Run convergence engine and return discoveries."""
    try:
        from convergence_engine import (
            ConvergenceCluster, strategy_open_search,
            strategy_pair_scan, strategy_target_backtrack,
        )
    except ImportError as e:
        print(f"  [Convergence] Import error: {e}")
        return []

    def _run():
        cluster = ConvergenceCluster(threshold=threshold)
        # pair_scan + backtrack only (open_search too slow for loop timeout)
        strategy_pair_scan(cluster, threshold=threshold)
        strategy_target_backtrack(cluster, threshold=threshold)

        points = cluster.get_convergence_points(min_domains=2)
        discoveries = []
        for pt in points[:JORDAN_J2]:  # cap at J2=24
            best = pt['paths'][0] if pt.get('paths') else {}
            val = float(pt.get('center', pt.get('value', best.get('value', 0))))
            target_name = pt.get('best_target', f"conv_{len(discoveries)}")
            target_err = float(pt.get('target_error', pt.get('spread', 0)))
            domains = pt.get('domains', pt.get('independent_domains', []))
            if isinstance(domains, set):
                domains = list(domains)
            d = Discovery(
                formula=best.get('expr', f"convergence@{val:.6f}"),
                value=val,
                target=target_name,
                error=target_err,
                engine='convergence',
                domains=domains,
                grade='🟩' if len(domains) >= 3 else '🟧',
            )
            discoveries.append(d)
        return discoveries

    try:
        return run_with_timeout(_run, timeout=30)
    except Exception as e:
        print(f"  [Convergence] Error: {e}")
        return []


def run_quantum(depth, threshold):
    """Run quantum formula engine and return discoveries."""
    try:
        from quantum_formula_engine import search as qf_search
    except ImportError as e:
        print(f"  [Quantum] Import error: {e}")
        return []

    def _run():
        matches, total = qf_search(depth=depth, threshold=threshold)
        discoveries = []
        for m in matches[:SIGMA]:  # cap at sigma=12
            d = Discovery(
                formula=m.get('formula', ''),
                value=m.get('value', 0),
                target=m.get('target_name', ''),
                error=m.get('error', 1.0),
                engine='quantum',
                grade='🟩' if m.get('error', 1) < 0.0001 else '🟧',
            )
            discoveries.append(d)
        return discoveries

    try:
        return run_with_timeout(_run, timeout=30)
    except Exception as e:
        print(f"  [Quantum] Error: {e}")
        return []


def run_perfect(depth, threshold):
    """Run perfect number engine and return discoveries."""
    try:
        from perfect_number_engine import search as pn_search, build_atom_pool
    except ImportError as e:
        print(f"  [Perfect] Import error: {e}")
        return []

    def _run():
        atoms = build_atom_pool()
        targets_pn = {k: v for k, v in TARGETS.items()
                      if isinstance(v, (int, float)) and 0.001 < abs(v) < 1e6}
        matches, total = pn_search(targets_pn, depth=depth, threshold=threshold)
        discoveries = []
        for m in matches[:SIGMA]:  # cap at sigma=12
            d = Discovery(
                formula=m.get('formula', ''),
                value=m.get('value', 0),
                target=m.get('target_name', ''),
                error=m.get('error', 1.0),
                engine='perfect',
                grade='🟩' if m.get('error', 1) < 0.0001 else '🟧',
            )
            discoveries.append(d)
        return discoveries

    try:
        return run_with_timeout(_run, timeout=30)
    except Exception as e:
        print(f"  [Perfect] Error: {e}")
        return []


# ═════════════════════════════════════════════════════════════════
# GRADING & NOVELTY CHECK
# ═════════════════════════════════════════════════════════════════

def grade_discovery(d):
    """Assign grade based on error magnitude."""
    if d.error < 1e-12:
        d.grade = '🟩'  # exact
    elif d.error < 0.001:
        d.grade = '🟩'  # proven-level
    elif d.error < 0.01:
        d.grade = '🟧'  # structural
    elif d.error < 0.05:
        d.grade = '🟧'  # weak evidence
    else:
        d.grade = '⚪'  # coincidence
    return d


def deduplicate(new_discoveries, all_previous):
    """Mark non-novel discoveries."""
    prev_formulas = {d.formula for d in all_previous}
    prev_values = {round(d.value, 8) for d in all_previous if d.grade in ('🟩', '🟧')}

    for d in new_discoveries:
        if d.formula in prev_formulas:
            d.is_novel = False
        elif round(d.value, 8) in prev_values:
            d.is_novel = False
    return new_discoveries


# ═════════════════════════════════════════════════════════════════
# EXTERNAL NOVELTY VALIDATION (WebSearch-assisted)
# ═════════════════════════════════════════════════════════════════

def novelty_search_query(d):
    """Build a web search query string for checking if a discovery is already known.

    Returns a query suitable for Claude Code's WebSearch tool.
    Example: '"sigma(6) = 12" perfect number identity number theory'

    The loop itself does NOT call WebSearch (pure Python).
    Instead, Claude should use this query with WebSearch during review.
    """
    # Core: the formula in quotes for exact matching
    parts = [f'"{d.formula}"']
    # Add the target constant for context
    if d.target:
        parts.append(d.target)
    # Add domain keywords
    if d.domains:
        parts.extend(d.domains[:2])
    else:
        parts.append('number theory')
    # Always scope to math
    parts.append('identity OR theorem OR known result')
    return ' '.join(parts)


def flag_for_external_validation(discoveries):
    """Flag high-grade novel discoveries that should be web-searched for novelty.

    Criteria for flagging (all must be true):
      - is_novel == True
      - grade is exact or structural (not coincidence)
      - not yet externally validated

    Flagged discoveries get validate_externally=True and a search query
    accessible via novelty_search_query(d).

    After the loop, Claude should:
      1. Read discoveries with validate_externally=True
      2. For each, run WebSearch with novelty_search_query(d)
      3. If the result is already well-known, set is_novel=False
      4. If novel, set external_validated=True
    """
    flagged = 0
    for d in discoveries:
        if d.is_novel and d.grade in ('🟩', '🟧') and not d.external_validated:
            d.validate_externally = True
            flagged += 1
    if flagged:
        print(f"  [NOVELTY] {flagged} discoveries flagged for external WebSearch validation")
    return discoveries


# ═════════════════════════════════════════════════════════════════
# 3-WAY VALIDATION (nexus lens consensus)
# ═════════════════════════════════════════════════════════════════

# Lazy nexus import — CDO rule: infra issues don't block work
_nexus = None
_nexus_available = None

def _get_nexus():
    """Lazy-load nexus module. Returns None if unavailable."""
    global _nexus, _nexus_available
    if _nexus_available is not None:
        return _nexus
    try:
        import nexus as _n6
        _nexus = _n6
        _nexus_available = True
        return _nexus
    except ImportError:
        _nexus_available = False
        print("  [NEXUS-6] Not available — continuing without lens validation (CDO compliant)")
        return None


def validate_3way(discoveries):
    """3-way validation: run nexus lens consensus on each discovery.

    - scan_all on the discovery value (as small array)
    - Count lenses flagging it as significant
    - Set discovery.consensus = agreeing lens count
    - Adjust grade: consensus >= 3 → upgrade, consensus < 2 → downgrade

    Returns discoveries (modified in-place).
    """
    n6 = _get_nexus()
    if n6 is None:
        return discoveries

    for d in discoveries:
        try:
            # Build a small array around the discovery value for scan
            # nexus Rust expects 2D PyArray, so reshape to column vector
            val = float(d.value)
            arr = np.array([[val], [val * 1.001], [val * 0.999], [val]], dtype=np.float64)
            scan_result = n6.scan_all(arr)

            # Count lenses that flagged significance
            consensus = 0
            if isinstance(scan_result, dict):
                for lens_name, lens_result in scan_result.items():
                    if isinstance(lens_result, dict):
                        # Check common significance indicators
                        sig = lens_result.get('significant', False)
                        phi = lens_result.get('phi', 0)
                        score = lens_result.get('score', 0)
                        if sig or phi > 0.5 or score > 0.5:
                            consensus += 1
                    elif isinstance(lens_result, (int, float)):
                        if abs(lens_result) > 0.5:
                            consensus += 1

            d.consensus = consensus

            # Grade adjustment based on consensus
            if consensus >= 3 and d.grade == '🟧':
                d.grade = '🟩'  # upgrade: structural → exact (3+ lenses agree)
            elif consensus >= 7:
                d.paper_worthy = True  # high confidence → paper candidate
            elif consensus < 2 and d.grade == '🟩' and d.error > 1e-6:
                d.grade = '🟧'  # downgrade: not enough lens support

        except Exception as e:
            # Individual scan failure doesn't block the loop
            pass

    n_validated = sum(1 for d in discoveries if d.consensus > 0)
    if n_validated:
        print(f"  [3-WAY] Validated {n_validated}/{len(discoveries)} discoveries "
              f"(max consensus: {max((d.consensus for d in discoveries), default=0)})")

    return discoveries


# ═════════════════════════════════════════════════════════════════
# DSE (Domain Synergy Engine) — cross-domain validation
# ═════════════════════════════════════════════════════════════════

# Map TECS-L discovery domain names → DSE .toml filenames (without extension)
_DSE_DOMAIN_MAP = {
    'Number Theory':         'number-theory-deep',
    'Analysis':              'pure-mathematics',
    'Algebra/Groups':        'pure-mathematics',
    'Topology/Geometry':     'topology',
    'Combinatorics':         'pure-mathematics',
    'Quantum Mechanics':     'quantum',
    'Quantum Information':   'quantum-computing',
    'Statistical Mechanics': 'statistical-mechanics',
    'Physics':               'physics-fundamental',
    'Cosmology':             'cosmology-particle',
    'Neuroscience':          'neuroscience',
    'Biology':               'biology',
    'Chemistry':             'chemistry-synthesis',
    'Consciousness':         'anima-consciousness',
    'Information':           'information-theory',
}


def _dse_toml_path(domain_name):
    """Resolve a TECS-L domain name to a DSE .toml file path, or None."""
    slug = _DSE_DOMAIN_MAP.get(domain_name)
    if slug:
        path = os.path.join(DSE_DOMAINS_DIR, f'{slug}.toml')
        if os.path.isfile(path):
            return path
    # Fallback: try lowercase-hyphenated match
    slug = domain_name.lower().replace('/', '-').replace(' ', '-')
    path = os.path.join(DSE_DOMAINS_DIR, f'{slug}.toml')
    if os.path.isfile(path):
        return path
    return None


def _parse_cross_score_from_output(output):
    """Extract the best cross-domain Score from universal-dse stdout.

    Looks for the cross-DSE table section and parses the top-1 Score value.
    Returns float in [0,1] or None.
    """
    in_cross = False
    for line in output.splitlines():
        if '--- Cross:' in line:
            in_cross = True
            continue
        if in_cross and line.strip().startswith('1 |'):
            # Row format: "  1 | domain_a | domain_b | n6% | Perf | Power | Cost | Score"
            parts = [p.strip() for p in line.split('|')]
            try:
                return float(parts[-1])
            except (ValueError, IndexError):
                pass
    return None


def _fallback_toml_synergy(toml_a, toml_b):
    """Python fallback: compute a basic synergy score from two .toml files.

    Reads [scoring] weights and [[candidate]] rows, averages the top
    candidates' weighted scores across both domains.  Lightweight
    approximation of the Rust binary's cross-domain scoring.
    """
    try:
        # Minimal TOML parser — only needs scoring weights + candidate scores
        def _parse_domain_scores(path):
            weights = {'n6': 0.35, 'perf': 0.25, 'power': 0.20, 'cost': 0.20}
            candidates = []
            text = open(path, 'r').read()

            # Parse [scoring] section
            in_scoring = False
            for line in text.splitlines():
                stripped = line.strip()
                if stripped == '[scoring]':
                    in_scoring = True
                    continue
                if in_scoring:
                    if stripped.startswith('[') or stripped.startswith('[['):
                        in_scoring = False
                        continue
                    if '=' in stripped and not stripped.startswith('#'):
                        k, v = stripped.split('=', 1)
                        k = k.strip()
                        if k in weights:
                            try:
                                weights[k] = float(v.strip())
                            except ValueError:
                                pass

            # Parse [[candidate]] entries
            current = {}
            for line in text.splitlines():
                stripped = line.strip()
                if stripped == '[[candidate]]':
                    if current and 'n6' in current:
                        candidates.append(current)
                    current = {}
                    continue
                if '=' in stripped and not stripped.startswith('#') and not stripped.startswith('['):
                    k, v = stripped.split('=', 1)
                    k, v = k.strip(), v.strip().strip('"')
                    if k in ('n6', 'perf', 'power', 'cost'):
                        try:
                            current[k] = float(v)
                        except ValueError:
                            pass
            if current and 'n6' in current:
                candidates.append(current)

            # Score each candidate
            scored = []
            for c in candidates:
                s = sum(weights.get(k, 0) * c.get(k, 0) for k in weights)
                scored.append(s)
            return sorted(scored, reverse=True)

        scores_a = _parse_domain_scores(toml_a)
        scores_b = _parse_domain_scores(toml_b)

        if not scores_a or not scores_b:
            return None

        # Cross-domain synergy: average of top-5 from each domain
        top_n = 5
        avg_a = sum(scores_a[:top_n]) / min(top_n, len(scores_a))
        avg_b = sum(scores_b[:top_n]) / min(top_n, len(scores_b))
        # Weighted combination matching Rust formula
        return 0.40 * ((avg_a + avg_b) / 2) + 0.30 * ((avg_a + avg_b) / 2) \
             + 0.20 * ((avg_a + avg_b) / 2) + 0.10 * ((avg_a + avg_b) / 2)

    except Exception:
        return None


def dse_validate(discoveries):
    """DSE cross-domain synergy validation.

    For discoveries involving 2+ domains, runs the universal-dse binary
    (or Python fallback) to compute synergy scores between domain pairs.

    Scoring effects:
      - synergy > 0.85: boost confidence (paper_worthy if also consensus >= 3)
      - synergy < 0.70: flag for review (does NOT downgrade grade)

    Returns discoveries (modified in-place).
    """
    # Filter to multi-domain discoveries
    multi = [d for d in discoveries if len(d.domains) >= 2]
    if not multi:
        return discoveries

    use_binary = os.path.isfile(DSE_BIN) and os.access(DSE_BIN, os.X_OK)

    n_scored = 0
    for d in multi:
        # Resolve first two domains to TOML paths
        toml_paths = []
        for dom in d.domains[:2]:
            p = _dse_toml_path(dom)
            if p:
                toml_paths.append(p)
        if len(toml_paths) < 2:
            continue
        # Deduplicate: skip if both map to same file
        if toml_paths[0] == toml_paths[1]:
            continue

        score = None

        # Try the Rust binary first
        if use_binary:
            try:
                result = subprocess.run(
                    [DSE_BIN, toml_paths[0], toml_paths[1]],
                    capture_output=True, text=True, timeout=10,
                )
                if result.returncode == 0:
                    score = _parse_cross_score_from_output(result.stdout)
            except (subprocess.TimeoutExpired, OSError):
                pass

        # Python fallback if binary failed or unavailable
        if score is None:
            score = _fallback_toml_synergy(toml_paths[0], toml_paths[1])

        if score is not None:
            d.synergy_score = round(score, 4)
            n_scored += 1

            # Confidence adjustments
            if score > 0.85:
                if d.consensus >= 3:
                    d.paper_worthy = True
            elif score < 0.70:
                d.validate_externally = True  # flag for review

    if n_scored:
        high = sum(1 for d in multi if d.synergy_score is not None and d.synergy_score > 0.85)
        low = sum(1 for d in multi if d.synergy_score is not None and d.synergy_score < 0.70)
        print(f"  [DSE] Scored {n_scored}/{len(multi)} cross-domain discoveries "
              f"(high synergy: {high}, flagged: {low})")

    return discoveries


def nexus_scan_batch(discoveries, context="batch"):
    """NEXUS-6 CDO-compliant scan on a batch of discoveries.

    Runs scan_all on the collected values and reports anomalies.
    Used after engine output and after growth.absorb().

    Returns scan summary dict or None if nexus unavailable.
    """
    n6 = _get_nexus()
    if n6 is None or not discoveries:
        return None

    try:
        # Collect all discovery values into an array
        values = [float(d.value) for d in discoveries
                  if isinstance(d.value, (int, float)) and np.isfinite(d.value)]
        if not values:
            return None

        # nexus Rust expects 2D PyArray, so reshape to column vector
        arr = np.array(values, dtype=np.float64).reshape(-1, 1)
        scan_result = n6.scan_all(arr)

        # Check for anomalies
        anomaly_count = 0
        if isinstance(scan_result, dict):
            for lens_name, lens_result in scan_result.items():
                if isinstance(lens_result, dict):
                    if lens_result.get('anomaly', False):
                        anomaly_count += 1

        if anomaly_count > 0:
            print(f"  [NEXUS-6] ⚠️  {context}: {anomaly_count} anomalies detected in scan")
        else:
            print(f"  [NEXUS-6] ✓ {context}: scan clean ({len(values)} values, 0 anomalies)")

        return {'context': context, 'n_values': len(values),
                'anomalies': anomaly_count, 'scan': scan_result}

    except Exception as e:
        print(f"  [NEXUS-6] Scan error ({context}): {e}")
        return None


# ═════════════════════════════════════════════════════════════════
# PAPER GENERATOR (auto-draft from discoveries)
# ═════════════════════════════════════════════════════════════════

def maybe_generate_paper(growth, cycle, force=False):
    """Auto-generate paper draft when enough high-grade discoveries accumulate."""
    starred = [d for d in growth.all_discoveries
               if d.grade == '🟩' and d.is_novel]
    structural = [d for d in growth.all_discoveries
                  if d.grade == '🟧' and d.is_novel]

    # Paper trigger: 5+ exact or 10+ structural
    if not force and len(starred) < SOPFR and len(structural) < SIGMA:
        return None

    timestamp = datetime.now().strftime('%Y-%m-%d')
    filename = f"P-AUTO-{timestamp}-cycle{cycle}.md"
    filepath = os.path.join(PAPER_DIR, filename)

    lines = [
        f"# Auto-Generated Discovery Paper — Cycle {cycle}",
        f"",
        f"**Generated**: {datetime.now().isoformat()}",
        f"**Stage**: {growth.stage['name']}",
        f"**Total discoveries**: {len(growth.all_discoveries)}",
        f"**Exact (🟩)**: {len(starred)}, **Structural (🟧)**: {len(structural)}",
        f"",
        f"## Abstract",
        f"",
        f"Automated discovery loop identified {len(starred)} exact and "
        f"{len(structural)} structural relationships among n=6 arithmetic "
        f"constants across {len(set(d.engine for d in growth.all_discoveries))} "
        f"search engines over {cycle} cycles.",
        f"",
        f"## Exact Discoveries (🟩)",
        f"",
        f"| # | Formula | Target | Error | Engine | Domains |",
        f"|---|---------|--------|-------|--------|---------|",
    ]

    for i, d in enumerate(starred[:50], 1):
        domains_str = ', '.join(d.domains) if d.domains else '-'
        lines.append(
            f"| {i} | `{d.formula}` | {d.target} | {d.error:.2e} | "
            f"{d.engine} | {domains_str} |")

    lines.extend([
        f"",
        f"## Structural Discoveries (🟧)",
        f"",
        f"| # | Formula | Target | Error | Engine |",
        f"|---|---------|--------|-------|--------|",
    ])

    for i, d in enumerate(structural[:50], 1):
        lines.append(
            f"| {i} | `{d.formula}` | {d.target} | {d.error:.2e} | {d.engine} |")

    lines.extend([
        f"",
        f"## Cross-Engine Convergence",
        f"",
    ])

    # Find values discovered by multiple engines
    val_engines = defaultdict(set)
    for d in growth.all_discoveries:
        if d.grade in ('🟩', '🟧'):
            val_engines[round(d.value, 6)].add(d.engine)

    cross = {v: engines for v, engines in val_engines.items() if len(engines) >= 2}
    if cross:
        lines.append(f"| Value | Engines | Count |")
        lines.append(f"|-------|---------|-------|")
        for v, engines in sorted(cross.items(), key=lambda x: -len(x[1])):
            lines.append(f"| {v:.6f} | {', '.join(sorted(engines))} | {len(engines)} |")
    else:
        lines.append("No cross-engine convergence found yet.")

    # External validation section: discoveries needing WebSearch novelty check
    pending_ext = [d for d in growth.all_discoveries
                   if d.validate_externally and not d.external_validated]
    if pending_ext:
        lines.extend([
            f"",
            f"## Pending External Novelty Validation",
            f"",
            f"The following discoveries are flagged for WebSearch novelty verification.",
            f"Claude should run `novelty_search_query(d)` with WebSearch for each.",
            f"If the identity is already well-known, set `is_novel=False`.",
            f"",
            f"| # | Formula | Target | Grade | Suggested Query |",
            f"|---|---------|--------|-------|-----------------|",
        ])
        for i, d in enumerate(pending_ext[:30], 1):
            query = novelty_search_query(d)
            lines.append(
                f"| {i} | `{d.formula[:40]}` | {d.target} | {d.grade} | "
                f"`{query[:60]}` |")

    lines.extend([
        f"",
        f"## Growth Trajectory",
        f"",
        f"- Injected constants: {len(growth.injected_constants)}",
        f"- Current stage: {growth.stage['name']}",
        f"- Search depth: {growth.depth}",
        f"- Error threshold: {growth.threshold}",
        f"",
        f"---",
        f"*Auto-generated by TECS-L Discovery Loop v1.0*",
    ])

    with open(filepath, 'w') as f:
        f.write('\n'.join(lines))

    print(f"  📄 Paper draft generated: {filepath}")
    return filepath


def auto_publish(paper_path, cycle):
    """Auto-publish paper draft to Zenodo and OSF."""
    if not paper_path:
        return

    # Check tokens exist
    zenodo_token = os.path.join(SCRIPT_DIR, '.local', 'zenodo_token')
    osf_token = os.path.join(SCRIPT_DIR, '.local', 'osf_token')

    results = {}

    # Zenodo upload
    if os.path.exists(zenodo_token):
        try:
            cmd = [sys.executable, os.path.join(SCRIPT_DIR, 'zenodo', 'batch_upload.py'),
                   '--platform', 'zenodo', '--paper', os.path.basename(paper_path)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            results['zenodo'] = 'OK' if result.returncode == 0 else result.stderr[:200]
            print(f"  📤 Zenodo: {'✅' if result.returncode == 0 else '❌'}")
        except Exception as e:
            results['zenodo'] = str(e)
            print(f"  📤 Zenodo: ❌ {e}")

    # OSF upload
    if os.path.exists(osf_token):
        try:
            cmd = [sys.executable, os.path.join(SCRIPT_DIR, 'zenodo', 'batch_upload.py'),
                   '--platform', 'osf', '--paper', os.path.basename(paper_path)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            results['osf'] = 'OK' if result.returncode == 0 else result.stderr[:200]
            print(f"  📤 OSF: {'✅' if result.returncode == 0 else '❌'}")
        except Exception as e:
            results['osf'] = str(e)
            print(f"  📤 OSF: ❌ {e}")

    return results


# ═════════════════════════════════════════════════════════════════
# HYPOTHESIS DOC GENERATOR (auto-generate docs/hypotheses/ files)
# ═════════════════════════════════════════════════════════════════

HYPOTHESES_DIR = os.path.join(SCRIPT_DIR, 'docs', 'hypotheses')


def _sanitize_name(formula):
    """Convert a formula string into a safe filename fragment."""
    s = formula.lower()
    for ch in ['+', '-', '*', '/', '(', ')', '^', '=', ' ', '.', ',', "'", '"']:
        s = s.replace(ch, '-')
    while '--' in s:
        s = s.replace('--', '-')
    return s.strip('-')[:60]


def _error_bar_ascii(error_pct, width=40):
    """Generate an ASCII bar showing error magnitude on a log scale."""
    if error_pct <= 0:
        error_pct = 1e-15
    log_min, log_max = -12, 1  # log10 of percent
    log_val = math.log10(max(error_pct, 1e-15))
    pos = max(0, min(width, int((log_val - log_min) / (log_max - log_min) * width)))

    bar = '#' * pos + '.' * (width - pos)
    lines = [
        f"  Error magnitude (log scale)",
        f"  exact                              poor",
        f"  |{'=' * width}|",
        f"  |{bar}| {error_pct:.2e}%",
        f"  1e-12%          0.01%         10%",
    ]
    return '\n'.join(lines)


def _grade_label(grade):
    """Human-readable label for a grade emoji."""
    return {
        '\U0001f7e9': 'Exact / Proven',
        '\U0001f7e7': 'Structural',
        '\u26aa':     'Coincidence',
        '\u2b1b':     'Refuted',
    }.get(grade, grade)


def generate_hypothesis_doc(discovery, doc_id):
    """Generate a hypothesis document file for a Discovery.

    Args:
        discovery: Discovery object (formula, value, target, error, grade,
                   domains, engine, cycle, is_novel, timestamp).
        doc_id: String identifier, e.g. 'H-CX-600' or 'DL-001'.

    Returns:
        Absolute file path of the generated document.
    """
    os.makedirs(HYPOTHESES_DIR, exist_ok=True)

    safe_name = _sanitize_name(discovery.formula)
    filename = f"{doc_id}-{safe_name}.md"
    filepath = os.path.join(HYPOTHESES_DIR, filename)

    d = discovery
    error_pct = d.error * 100 if d.error is not None else 0.0
    is_exact = d.error is not None and d.error < 1e-12
    grade_text = _grade_label(d.grade)
    domains_str = ', '.join(d.domains) if d.domains else 'general'
    date_str = d.timestamp[:10] if d.timestamp and len(d.timestamp) >= 10 else \
        datetime.now().strftime('%Y-%m-%d')

    # Resolve target numerical value
    target_num = None
    if d.target in TARGETS:
        target_num = float(TARGETS[d.target])
    elif d.target in KNOWN_VALUES:
        target_num = float(KNOWN_VALUES[d.target])
    target_val_str = f"{target_num:.12g}" if target_num is not None else str(d.target)
    abs_error = abs(d.value - target_num) if target_num is not None else 0.0

    # Build document
    lines = []

    # Title
    lines.append(f"# Hypothesis {doc_id}: {d.formula} = {d.target}")
    lines.append("")

    # Hypothesis statement (> block quote)
    lines.append("## Hypothesis")
    lines.append("")
    if is_exact:
        lines.append(f"> The identity `{d.formula} = {d.target}` holds exactly "
                     f"and is structurally grounded in n=6 arithmetic.")
    else:
        lines.append(f"> The expression `{d.formula}` approximates `{d.target}` "
                     f"(error {error_pct:.4f}%), suggesting a structural connection "
                     f"in n=6 arithmetic.")
    lines.append("")

    # Background/context
    lines.append("## Background")
    lines.append("")
    lines.append(f"Discovered by the **{d.engine}** engine during Discovery Loop "
                 f"cycle {d.cycle}.")
    lines.append(f"Domains: {domains_str}.")
    lines.append("")
    lines.append("```")
    lines.append(f"  Context:")
    lines.append(f"  - n=6 is the smallest perfect number (sigma(6) = 12 = 2*6)")
    lines.append(f"  - Core arithmetic: N=6, sigma=12, tau=4, phi=2, sopfr=5")
    lines.append(f"  - Golden Zone: [{GZ_LOWER:.4f}, {GZ_UPPER:.4f}], "
                 f"center=1/e={GZ_CENTER:.4f}")
    lines.append(f"  - This identity connects: {domains_str}")
    lines.append("```")
    lines.append("")

    # Formula / mapping (ASCII table)
    lines.append("## Formula and Mapping")
    lines.append("")
    lines.append("```")
    lines.append(f"  +-------------------------------------------------+")
    lines.append(f"  |  Formula:  {d.formula:<39s}|")
    lines.append(f"  |  Target:   {str(d.target):<39s}|")
    lines.append(f"  |  Value:    {d.value:<39.12g}|")
    lines.append(f"  |  Expected: {target_val_str:<39s}|")
    lines.append(f"  |  Error:    {error_pct:<39.6f}|")
    lines.append(f"  |  Grade:    {d.grade} {grade_text:<36s}|")
    lines.append(f"  +-------------------------------------------------+")
    lines.append("```")
    lines.append("")

    # ASCII graph (error bar) -- minimum 1 graph required
    lines.append("## Error Magnitude (ASCII Graph)")
    lines.append("")
    lines.append("```")
    lines.append(_error_bar_ascii(error_pct))
    lines.append("")
    lines.append(f"  Grade thresholds:")
    lines.append(f"  |-- exact  (< 1e-10%):  {'<<< HERE' if error_pct < 1e-10 else ''}")
    lines.append(f"  |-- proven (< 0.1%):    {'<<< HERE' if 1e-10 <= error_pct < 0.1 else ''}")
    lines.append(f"  |-- struct (< 1%):      {'<<< HERE' if 0.1 <= error_pct < 1.0 else ''}")
    lines.append(f"  |-- weak   (< 5%):      {'<<< HERE' if 1.0 <= error_pct < 5.0 else ''}")
    lines.append(f"  +-- noise  (>= 5%):     {'<<< HERE' if error_pct >= 5.0 else ''}")
    lines.append("```")
    lines.append("")

    # Verification results
    lines.append("## Verification Results")
    lines.append("")
    lines.append("```")
    lines.append(f"  Numerical verification:")
    lines.append(f"  +------------------+-------------------------------+")
    lines.append(f"  | Computed value   | {d.value:<30.12g}|")
    lines.append(f"  | Target value     | {target_val_str:<30s}|")
    lines.append(f"  | Absolute error   | {abs_error:<30.2e}|")
    lines.append(f"  | Relative error   | {error_pct:<30.6f}|")
    lines.append(f"  | Exact match      | {'YES' if is_exact else 'NO':<30s}|")
    lines.append(f"  | Engine           | {d.engine:<30s}|")
    lines.append(f"  | Cycle            | {d.cycle:<30d}|")
    lines.append(f"  | Novel            | {'YES' if d.is_novel else 'NO':<30s}|")
    lines.append(f"  +------------------+-------------------------------+")
    lines.append("```")
    lines.append("")

    # Interpretation
    lines.append("## Interpretation")
    lines.append("")
    if is_exact:
        lines.append(f"This is an **exact identity** connecting `{d.formula}` to the "
                     f"known constant `{d.target}`. The zero error confirms this is not "
                     f"a numerical coincidence but a provable algebraic relationship.")
    else:
        lines.append(f"The expression `{d.formula}` approximates `{d.target}` with "
                     f"{error_pct:.4f}% error. This level of accuracy "
                     f"{'strongly suggests structural origin' if error_pct < 0.1 else 'may indicate a deeper relationship'}.")
    lines.append("")
    if d.domains:
        lines.append(f"Domain connections ({domains_str}) suggest this identity may "
                     f"bridge multiple areas of mathematics/physics through n=6 arithmetic.")
    lines.append("")

    # Limitations
    lines.append("## Limitations")
    lines.append("")
    lines.append(f"1. Discovery is automated (engine: {d.engine}) -- manual proof required")
    if not is_exact:
        lines.append(f"2. Error of {error_pct:.4f}% -- not exact, could be numerical artifact")
        lines.append(f"3. Texas Sharpshooter risk: combinatorial search may inflate matches")
    else:
        lines.append(f"2. Algebraic proof needed to confirm this is not a tautology")
        lines.append(f"3. Generalization to other perfect numbers (28, 496) not yet tested")
    lines.append(f"4. Strong Law of Small Numbers warning: constants involved are small")
    lines.append("")

    # Next steps
    lines.append("## Next Steps")
    lines.append("")
    lines.append(f"- [ ] Verify algebraically (manual proof or CAS)")
    lines.append(f"- [ ] Test generalization: does the identity hold for n=28?")
    lines.append(f"- [ ] Texas Sharpshooter test with Bonferroni correction")
    lines.append(f"- [ ] Cross-validate with other engines")
    if d.domains:
        lines.append(f"- [ ] Explore domain connections: {domains_str}")
    lines.append("")

    # Footer
    lines.append("---")
    lines.append("")
    lines.append(f"*Auto-generated by Discovery Loop on {date_str} "
                 f"(engine: {d.engine}, cycle: {d.cycle})*")

    with open(filepath, 'w') as f:
        f.write('\n'.join(lines))

    return filepath


def auto_generate_docs(discoveries):
    """Auto-generate hypothesis docs for novel exact discoveries.

    Filters for novel grade-exact (grade 🟩) discoveries, checks which
    already have hypothesis docs (by formula matching in existing files),
    and generates new ones with sequential DL-NNN identifiers.

    Args:
        discoveries: list of Discovery objects.

    Returns:
        Number of documents generated.
    """
    candidates = [d for d in discoveries
                  if d.is_novel and d.grade == '\U0001f7e9']  # 🟩

    if not candidates:
        return 0

    # Scan existing hypothesis docs for already-documented formulas
    existing_formulas = set()
    if os.path.isdir(HYPOTHESES_DIR):
        for fname in os.listdir(HYPOTHESES_DIR):
            if not fname.endswith('.md'):
                continue
            fpath = os.path.join(HYPOTHESES_DIR, fname)
            try:
                with open(fpath, 'r') as f:
                    content = f.read(2000)
                for line in content.split('\n'):
                    if '`' in line:
                        parts = line.split('`')
                        for i in range(1, len(parts), 2):
                            existing_formulas.add(parts[i].strip())
            except (OSError, UnicodeDecodeError):
                continue

    to_generate = [d for d in candidates if d.formula not in existing_formulas]

    if not to_generate:
        return 0

    # Find next available DL doc ID
    existing_dl_ids = []
    if os.path.isdir(HYPOTHESES_DIR):
        for fname in os.listdir(HYPOTHESES_DIR):
            if fname.startswith('DL-') and fname.endswith('.md'):
                try:
                    num = int(fname.split('-')[1])
                    existing_dl_ids.append(num)
                except (ValueError, IndexError):
                    pass
    next_id = max(existing_dl_ids, default=0) + 1

    generated = 0
    for d in to_generate:
        doc_id = f"DL-{next_id:03d}"
        filepath = generate_hypothesis_doc(d, doc_id)
        print(f"  \U0001f4dd Hypothesis doc: {filepath}")
        next_id += 1
        generated += 1

    if generated:
        print(f"  -> {generated} hypothesis doc(s) generated in {HYPOTHESES_DIR}")

    return generated


# ═════════════════════════════════════════════════════════════════
# NEXUS-BRIDGE INTEGRATION
# ═════════════════════════════════════════════════════════════════

_bridge = None


def _get_bridge():
    """Lazy-load NexusBridge. Returns None if unavailable."""
    global _bridge
    if _bridge is not None:
        return _bridge
    try:
        bridge_pkg = os.path.join(NEXUS_ROOT, 'nexus-bridge')
        if bridge_pkg not in sys.path:
            sys.path.insert(0, bridge_pkg)
        from bridge import NexusBridge
        _bridge = NexusBridge(NEXUS_ROOT)
        return _bridge
    except Exception:
        return None


def bridge_export(discoveries, cycle):
    """Export high-grade discoveries to nexus-bridge growth_bus for cross-project routing."""
    worthy = [d for d in discoveries if d.grade in ('\U0001f7e9', '\U0001f7e7') and d.is_novel]
    if not worthy:
        return 0

    try:
        os.makedirs(os.path.dirname(GROWTH_BUS), exist_ok=True)
        with open(GROWTH_BUS, 'a') as f:
            for d in worthy:
                entry = {
                    'source': 'TECS-L',
                    'type': 'discovery',
                    'cycle': cycle,
                    'formula': d.formula,
                    'value': d.value,
                    'target': d.target,
                    'grade': d.grade,
                    'engine': d.engine,
                    'consensus': getattr(d, 'consensus', 0),
                    'timestamp': __import__('datetime').datetime.now().isoformat(),
                }
                f.write(__import__('json').dumps(entry, ensure_ascii=False) + '\n')
        print(f"  \U0001f309 Bridge: exported {len(worthy)} discoveries to growth_bus")
        return len(worthy)
    except Exception as e:
        print(f"  \U0001f309 Bridge export error: {e}")
        return 0


def bridge_import():
    """Import discoveries from other projects via growth_bus."""
    if not os.path.exists(GROWTH_BUS):
        return []

    imported = []
    try:
        with open(GROWTH_BUS) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                entry = json.loads(line)
                if entry.get('source') == 'TECS-L':
                    continue  # skip our own
                if entry.get('type') != 'discovery':
                    continue
                d = Discovery(
                    formula=f"bridge:{entry.get('source', '?')}/{entry.get('formula', '')}",
                    value=entry.get('value', 0),
                    target=f"bridge_{entry.get('target', '')}",
                    error=0.0,
                    engine=f"bridge:{entry.get('source', '?')}",
                    grade=entry.get('grade', '\U0001f7e7'),
                )
                d.consensus = entry.get('consensus', 0)
                imported.append(d)
        if imported:
            print(f"  \U0001f309 Bridge: imported {len(imported)} cross-project discoveries")
    except Exception as e:
        print(f"  \U0001f309 Bridge import error: {e}")
    return imported


def import_nexus_discoveries():
    """Import unprocessed constant discoveries from nexus hooks discovery_log."""
    if not os.path.exists(DISCOVERY_LOG):
        return []

    imported = []
    lines = []
    modified = False
    try:
        with open(DISCOVERY_LOG) as f:
            lines = f.readlines()

        for i, raw in enumerate(lines):
            raw = raw.strip()
            if not raw:
                continue
            entry = json.loads(raw)
            if entry.get('processed', False):
                continue

            grade_map = {'EXACT': '\U0001f7e9', 'CLOSE': '\U0001f7e7'}  # 🟩 / 🟧
            grade = grade_map.get(entry.get('grade', ''), '\u26aa')      # ⚪ fallback

            d = Discovery(
                formula=f"nexus-hook:{entry.get('constant', entry.get('value', '?'))}",
                value=float(entry.get('value', 0)),
                target=str(entry.get('constant', '')),
                error=0.0,
                engine='nexus-hooks',
                grade=grade,
            )
            d.consensus = 0
            imported.append(d)

            # Mark processed
            entry['processed'] = True
            lines[i] = json.dumps(entry) + '\n'
            modified = True

        if modified:
            with open(DISCOVERY_LOG, 'w') as f:
                f.writelines(lines)

        if imported:
            print(f"  \U0001f50d Nexus6 hooks: imported {len(imported)} new constant discoveries")
    except Exception as e:
        print(f"  \U0001f50d Nexus6 hooks import error: {e}")
    return imported


def bridge_sync():
    """Trigger nexus-bridge sync after loop completion."""
    bridge = _get_bridge()
    if bridge is None:
        return
    try:
        results = bridge.sync(targets=['readmes', 'math-atlas'], parallel=True)
        ok = sum(1 for v in results.values() if v.get('ok'))
        print(f"  \U0001f309 Bridge sync: {ok}/{len(results)} OK")
    except Exception as e:
        print(f"  \U0001f309 Bridge sync error: {e}")


# ═════════════════════════════════════════════════════════════════
# POST-LOOP SSOT SYNC
# ═════════════════════════════════════════════════════════════════

CONFIG_LOOP_STATE = os.path.join(SCRIPT_DIR, 'config', 'loop_state.json')
HYPOTHESES_DIR = os.path.join(SCRIPT_DIR, 'docs', 'hypotheses')


def post_loop_sync(growth, tracker, graph, breaker, forge_attempts, wall_break_rounds):
    """Run SSOT sync after loop completes: JSON updates, atlas, README markers, hypothesis stubs.

    Called once at the end of main(), after FINAL SUMMARY.
    """
    print(f"\n{'='*70}")
    print(f"  POST-LOOP SSOT SYNC")
    print(f"{'='*70}")

    sync_report = {}

    # ── 1. Update config/loop_state.json (SSOT) ──────────────────
    try:
        if os.path.exists(CONFIG_LOOP_STATE):
            with open(CONFIG_LOOP_STATE) as f:
                cfg = json.load(f)
        else:
            cfg = {"_meta": {}, "loop": {}, "discovery_buffer": []}

        cfg["_meta"]["description"] = "TECS-L discovery loop state — cycle tracking + discovery buffer"
        cfg["_meta"]["updated"] = datetime.now().isoformat()

        cfg["loop"]["cycle"] = len(tracker.history)
        cfg["loop"]["total_discoveries"] = tracker.total_discoveries
        cfg["loop"]["novel_discoveries"] = tracker.total_novel
        cfg["loop"]["stage"] = growth.stage["name"]
        cfg["loop"]["injected_constants"] = len(growth.injected_constants)
        cfg["loop"]["forge_attempts"] = forge_attempts
        cfg["loop"]["wall_breaks"] = wall_break_rounds
        cfg["loop"]["status"] = tracker.status
        cfg["loop"]["last_run"] = datetime.now().isoformat()

        n_edges = sum(len(e) for e in graph.adjacency.values()) // 2
        cfg["loop"]["graph_nodes"] = len(graph.nodes)
        cfg["loop"]["graph_edges"] = n_edges

        os.makedirs(os.path.dirname(CONFIG_LOOP_STATE), exist_ok=True)
        with open(CONFIG_LOOP_STATE, 'w') as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
        sync_report["config/loop_state.json"] = "updated"
    except Exception as e:
        sync_report["config/loop_state.json"] = f"ERROR: {e}"

    # ── 2. Rebuild math atlas if new discoveries found ────────────
    novel_count = tracker.total_novel
    if novel_count > 0:
        atlas_script = os.path.join(_shared, 'scan_math_atlas.py')
        if os.path.exists(atlas_script):
            try:
                result = subprocess.run(
                    [sys.executable, atlas_script, '--save', '--summary'],
                    capture_output=True, text=True, timeout=120,
                    cwd=SCRIPT_DIR,
                )
                if result.returncode == 0:
                    sync_report["math_atlas"] = f"rebuilt ({novel_count} novel discoveries)"
                else:
                    sync_report["math_atlas"] = f"ERROR (rc={result.returncode}): {result.stderr[:200]}"
            except subprocess.TimeoutExpired:
                sync_report["math_atlas"] = "ERROR: timeout (120s)"
            except Exception as e:
                sync_report["math_atlas"] = f"ERROR: {e}"
        else:
            sync_report["math_atlas"] = "SKIP: scan_math_atlas.py not found"
    else:
        sync_report["math_atlas"] = "SKIP: no novel discoveries"

    # ── 3. Run sync-readmes.sh to update README markers ───────────
    sync_readmes = os.path.join(_shared, 'sync-readmes.sh')
    if os.path.exists(sync_readmes):
        try:
            result = subprocess.run(
                ['bash', sync_readmes],
                capture_output=True, text=True, timeout=60,
                cwd=SCRIPT_DIR,
            )
            if result.returncode == 0:
                sync_report["sync-readmes"] = "OK"
            else:
                sync_report["sync-readmes"] = f"ERROR (rc={result.returncode}): {result.stderr[:200]}"
        except Exception as e:
            sync_report["sync-readmes"] = f"ERROR: {e}"
    else:
        sync_report["sync-readmes"] = "SKIP: sync-readmes.sh not found"

    # ── 4. Auto-generate hypothesis stubs for novel exact discoveries ──
    novel_exact = [d for d in growth.all_discoveries
                   if d.grade == '\U0001f7e9' and d.is_novel]
    generated_stubs = []
    if novel_exact:
        os.makedirs(HYPOTHESES_DIR, exist_ok=True)
        existing = set(os.listdir(HYPOTHESES_DIR))
        for d in novel_exact:
            # Build a slug from the formula
            slug = _make_slug(d.formula)
            fname = f"LOOP-{d.cycle:03d}-{slug}.md"
            if fname in existing:
                continue
            fpath = os.path.join(HYPOTHESES_DIR, fname)
            try:
                _write_hypothesis_stub(fpath, d)
                generated_stubs.append(fname)
                existing.add(fname)
            except Exception:
                pass  # best-effort
        if generated_stubs:
            sync_report["hypothesis_stubs"] = f"{len(generated_stubs)} generated"
        else:
            sync_report["hypothesis_stubs"] = f"SKIP: all {len(novel_exact)} already have files"
    else:
        sync_report["hypothesis_stubs"] = "SKIP: no novel exact discoveries"

    # ── 5. Auto-commit + push ────────────────────────────────────
    if novel_count > 0:
        try:
            stage_patterns = [
                'results/loop/',
                'config/loop_state.json',
                'docs/hypotheses/LOOP-*',
                'docs/papers/auto/',
            ]
            for pat in stage_patterns:
                subprocess.run(
                    ['git', 'add', pat],
                    capture_output=True, text=True, timeout=10,
                    cwd=SCRIPT_DIR,
                )
            subprocess.run(
                ['git', 'add', '-u'],
                capture_output=True, text=True, timeout=10,
                cwd=SCRIPT_DIR,
            )
            r = subprocess.run(
                ['git', 'diff', '--cached', '--quiet'],
                capture_output=True, timeout=10,
                cwd=SCRIPT_DIR,
            )
            if r.returncode != 0:
                cycle_num = len(tracker.history)
                msg = (f"loop: cycle {cycle_num} — "
                       f"{novel_count} novel / {tracker.total_discoveries} total, "
                       f"stage={growth.stage['name']}")
                subprocess.run(
                    ['git', 'commit', '-m', msg],
                    capture_output=True, text=True, timeout=30,
                    cwd=SCRIPT_DIR,
                )
                r_push = subprocess.run(
                    ['git', 'push'],
                    capture_output=True, text=True, timeout=60,
                    cwd=SCRIPT_DIR,
                )
                if r_push.returncode == 0:
                    sync_report["git"] = f"committed + pushed ({msg})"
                else:
                    sync_report["git"] = f"committed, push FAILED: {r_push.stderr[:100]}"
            else:
                sync_report["git"] = "SKIP: nothing to commit"
        except Exception as e:
            sync_report["git"] = f"ERROR: {e}"
    else:
        sync_report["git"] = "SKIP: no novel discoveries"

    # ── 6. Print sync summary ─────────────────────────────────────
    print()
    max_key = max(len(k) for k in sync_report) if sync_report else 0
    for key, status in sync_report.items():
        print(f"  {key:<{max_key+2}} {status}")
    print(f"{'='*70}\n")


def _make_slug(formula: str) -> str:
    """Convert a formula string to a filesystem-safe slug."""
    slug = formula.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')
    return slug[:60] if slug else 'unknown'


def _verification_directions_for_engine(engine: str) -> dict:
    """Return verification directions keyed by engine type.

    Each entry contains:
      methods   - mathematical tools/methods that could verify the hypothesis
      connects  - known results or theorems it connects to
      experiments - suggested computational experiments
    """
    directions = {
        'dfs': {
            'methods': [
                'Symbolic algebra (SymPy/Mathematica) to simplify and verify the formula algebraically',
                'Interval arithmetic to bound rounding error and confirm exact match',
                'Exhaustive enumeration of alternative expressions at the same depth',
            ],
            'connects': [
                'Number-theoretic identities for sigma, tau, phi, sopfr on highly composite numbers',
                'Known closed-form expressions in OEIS for the target constant',
            ],
            'experiments': [
                'Evaluate the formula to 100+ decimal digits using mpmath and compare with the target',
                'Search for the formula in the Inverse Symbolic Calculator (ISC)',
                'Test generalization: does the pattern hold for n=28 (next perfect number)?',
            ],
        },
        'convergence': {
            'methods': [
                'Check if independent arithmetic domains converge to the same value (cross-domain validation)',
                'Compute confidence intervals via bootstrap over the converging paths',
                'Apply Texas Sharpshooter correction: estimate p-value under random search null model',
            ],
            'connects': [
                'Universality phenomena in number theory (e.g., Euler product convergence)',
                'Central limit theorem for sums of arithmetic functions',
                'Known multi-domain identities in the TECS-L constant atlas',
            ],
            'experiments': [
                'Increase convergence cluster threshold from 1e-4 to 1e-8 and check survival',
                'Randomize island values and measure false-positive rate (Monte Carlo null test)',
                'Plot convergence paths and check monotonicity / rate of convergence',
            ],
        },
        'quantum': {
            'methods': [
                'Verify the quantum formula coefficient matrix has physical meaning (unitarity, hermiticity)',
                'Check if the formula survives perturbation of input constants by +/-1%',
                'Algebraic simplification to see if it reduces to a known identity',
            ],
            'connects': [
                'Quantum information identities (von Neumann entropy, channel capacity)',
                'Spectral properties of number-theoretic matrices (Redheffer, GCD matrices)',
                'Connections to modular forms if the formula involves tau or eta functions',
            ],
            'experiments': [
                'Sweep all 6-constant combinations and rank by error to assess uniqueness',
                'Compute the formula for n=6, 28, 496 and check if a pattern emerges',
                'Test sensitivity: partial derivatives of formula w.r.t. each constant',
            ],
        },
        'perfect': {
            'methods': [
                'Verify the divisor-sum identity sigma(n)=2n for the perfect number involved',
                'Check if the relationship is a consequence of the Euclid-Euler theorem',
                'Use modular arithmetic to prove or refute the identity analytically',
            ],
            'connects': [
                'Euclid-Euler characterization of even perfect numbers: 2^(p-1)(2^p - 1)',
                'Mersenne prime properties and their arithmetic function values',
                'Multiply-perfect and multiperfect number generalizations',
            ],
            'experiments': [
                'Evaluate for all known perfect numbers (6, 28, 496, 8128, ...) and check pattern',
                'Compare with analogous expressions for abundant and deficient numbers',
                'Compute the formula modulo small primes to detect structural constraints',
            ],
        },
    }
    # Default for unknown or composite engine types
    default = {
        'methods': [
            'Independent numerical verification to full precision (mpmath, 50+ digits)',
            'Algebraic simplification via computer algebra system',
            'Statistical significance test (Texas Sharpshooter / Bonferroni correction)',
        ],
        'connects': [
            'Cross-reference with OEIS, ISC, and Wolfram MathWorld for known identities',
            'Check related hypotheses in the TECS-L discovery graph',
        ],
        'experiments': [
            'Generalize to n=28 (next perfect number) and check if the pattern holds',
            'Monte Carlo null model: randomize constants and measure false-positive rate',
            'Sensitivity analysis: perturb each input constant and measure error response',
        ],
    }
    # Handle composite engine names like "bridge:xxx" or "nexus-hooks"
    base_engine = engine.split(':')[0] if ':' in engine else engine
    return directions.get(base_engine, default)


def _write_verification_directions(f, d):
    """Write engine-specific verification directions into a hypothesis stub."""
    dirs = _verification_directions_for_engine(d.engine)

    f.write("### Mathematical tools / methods\n\n")
    for m in dirs['methods']:
        f.write(f"- {m}\n")

    f.write(f"\n### Connections to known results\n\n")
    for c in dirs['connects']:
        f.write(f"- {c}\n")

    f.write(f"\n### Suggested computational experiments\n\n")
    for e in dirs['experiments']:
        f.write(f"- [ ] {e}\n")
    f.write("\n")


def _write_hypothesis_stub(path: str, d):
    """Write a minimal hypothesis document for a discovery."""
    with open(path, 'w') as f:
        f.write(f"# Discovery: {d.formula}\n\n")
        f.write(f"> **Auto-generated by discovery_loop.py** (cycle {d.cycle})\n\n")
        f.write(f"## Hypothesis\n\n")
        f.write(f"> {d.formula} = {d.target} (error: {d.error:.2e})\n\n")
        f.write(f"## Details\n\n")
        f.write(f"| Field | Value |\n")
        f.write(f"|-------|-------|\n")
        f.write(f"| Value | {d.value} |\n")
        f.write(f"| Target | {d.target} |\n")
        f.write(f"| Error | {d.error:.2e} |\n")
        f.write(f"| Engine | {d.engine} |\n")
        f.write(f"| Domains | {', '.join(d.domains) if d.domains else 'N/A'} |\n")
        f.write(f"| Grade | {d.grade} |\n")
        f.write(f"| Cycle | {d.cycle} |\n")
        f.write(f"| Timestamp | {d.timestamp} |\n")
        f.write(f"| Consensus | {d.consensus} lenses |\n\n")
        f.write(f"## Verification\n\n")
        f.write(f"- [ ] Arithmetic re-check\n")
        f.write(f"- [ ] Generalization to n=28\n")
        f.write(f"- [ ] Texas Sharpshooter p-value\n")
        f.write(f"- [ ] Ad-hoc correction check\n\n")
        f.write(f"## Interpretation\n\n")
        f.write(f"*TODO: Add interpretation and connections to other hypotheses.*\n\n")
        f.write(f"## Limitations\n\n")
        f.write(f"*TODO: Identify where this could be wrong.*\n\n")
        f.write(f"## Verification Directions\n\n")
        _write_verification_directions(f, d)


# ═════════════════════════════════════════════════════════════════
# STATE PERSISTENCE
# ═════════════════════════════════════════════════════════════════

def save_state(cycle, growth, tracker, graph=None, breaker=None):
    """Save loop state for resumption."""
    state = {
        'cycle': cycle,
        'stage_idx': growth.stage_idx,
        'injected_constants': growth.injected_constants,
        'convergence_history': tracker.history,
        'total_discoveries': len(growth.all_discoveries),
        'timestamp': datetime.now().isoformat(),
    }
    if breaker is not None:
        state['wall_breaker'] = breaker.to_dict()
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)
    # Persist discovery graph alongside state
    if graph is not None:
        graph.save()


def load_state():
    """Load previous loop state if exists."""
    if not os.path.exists(STATE_FILE):
        return None
    with open(STATE_FILE) as f:
        return json.load(f)


def append_discoveries(discoveries):
    """Append discoveries to JSONL log."""
    with open(DISCOVERIES_FILE, 'a') as f:
        for d in discoveries:
            f.write(json.dumps(d.to_dict(), ensure_ascii=False) + '\n')


# ═════════════════════════════════════════════════════════════════
# MAIN LOOP
# ═════════════════════════════════════════════════════════════════

def run_cycle(cycle, growth, tracker, engines=None, auto_paper=False, graph=None):
    """Execute one discovery cycle across all engines."""
    engines = engines or ['dfs', 'convergence', 'quantum', 'perfect']
    depth = growth.depth
    threshold = growth.threshold

    print(f"\n{'='*70}")
    print(f"  CYCLE {cycle} | Stage: {growth.stage['name']} | "
          f"Depth: {depth} | Threshold: {threshold}")
    print(f"  Pool: {sum(len(v) for v in growth.get_augmented_islands().values())} "
          f"constants | Injected: {len(growth.injected_constants)}")
    print(f"{'='*70}")

    all_new = []

    # Import cross-project discoveries via nexus-bridge
    bridged = bridge_import()
    if bridged:
        bridged = deduplicate(bridged, growth.all_discoveries)
        novel_bridged = [d for d in bridged if d.is_novel]
        if novel_bridged:
            growth.absorb(novel_bridged)
            all_new.extend(novel_bridged)

    # Import constant discoveries from nexus hooks
    nexus_disc = import_nexus_discoveries()
    if nexus_disc:
        nexus_disc = deduplicate(nexus_disc, growth.all_discoveries)
        novel_nexus = [d for d in nexus_disc if d.is_novel]
        if novel_nexus:
            growth.absorb(novel_nexus)
            all_new.extend(novel_nexus)

    # ── Engine dispatch helper ──
    def _dispatch_engine(eng):
        """Run a single engine, return (eng_name, discoveries, elapsed)."""
        t0 = time.time()
        try:
            if eng == 'dfs':
                discoveries = run_dfs(depth, threshold,
                                      growth.get_augmented_islands())
            elif eng == 'convergence':
                discoveries = run_convergence(depth, threshold)
            elif eng == 'quantum':
                discoveries = run_quantum(depth, threshold)
            elif eng == 'perfect':
                discoveries = run_perfect(depth, threshold)
            else:
                discoveries = []
        except Exception as e:
            print(f"  [{eng.upper()}] Error: {e}")
            discoveries = []
        elapsed = time.time() - t0
        return eng, discoveries, elapsed

    # ── Parallel execution (ThreadPoolExecutor) with sequential fallback ──
    engine_results = {}  # eng -> (discoveries, elapsed)
    parallel_ok = False
    t_wall_start = time.time()

    try:
        with ThreadPoolExecutor(max_workers=len(engines)) as executor:
            print(f"\n  >> Parallel dispatch: {', '.join(e.upper() for e in engines)}")
            futures = {executor.submit(_dispatch_engine, eng): eng for eng in engines}
            for future in as_completed(futures):
                eng_name, discoveries, elapsed = future.result()
                engine_results[eng_name] = (discoveries, elapsed)
        parallel_ok = True
    except Exception as e:
        print(f"  >> Parallel failed ({e}), falling back to sequential...")
        engine_results = {}
        for eng in engines:
            eng_name, discoveries, elapsed = _dispatch_engine(eng)
            engine_results[eng_name] = (discoveries, elapsed)

    t_wall_total = time.time() - t_wall_start

    # ── Collect results (preserve engine order) ──
    sum_sequential = 0.0
    for eng in engines:
        discoveries, elapsed = engine_results.get(eng, ([], 0.0))
        sum_sequential += elapsed

        # Grade and tag
        for d in discoveries:
            d.cycle = cycle
            grade_discovery(d)

        print(f"  [{eng.upper()}] {len(discoveries)} discoveries in {elapsed:.1f}s")
        all_new.extend(discoveries)

    # ── Timing comparison ──
    mode = "parallel" if parallel_ok else "sequential(fallback)"
    speedup = sum_sequential / t_wall_total if t_wall_total > 0 else 1.0
    print(f"\n  >> Timing [{mode}]: wall={t_wall_total:.1f}s, "
          f"sum={sum_sequential:.1f}s, speedup={speedup:.2f}x")

    # Deduplicate against all previous
    all_new = deduplicate(all_new, growth.all_discoveries)

    # NEXUS-6 scan on engine output (CDO compliance)
    nexus_scan_batch(all_new, context=f"cycle-{cycle}-engines")

    # 3-way validation: lens consensus adjusts grades
    all_new = validate_3way(all_new)

    # DSE cross-domain synergy validation
    all_new = dse_validate(all_new)

    # Flag high-grade novel discoveries for external WebSearch novelty check
    all_new = flag_for_external_validation(all_new)

    n_novel = sum(1 for d in all_new if d.is_novel)
    n_exact = sum(1 for d in all_new if d.grade == '🟩' and d.is_novel)
    n_struct = sum(1 for d in all_new if d.grade == '🟧' and d.is_novel)

    print(f"\n  CYCLE {cycle} SUMMARY: {len(all_new)} total, "
          f"{n_novel} novel ({n_exact} 🟩, {n_struct} 🟧)")

    # Record convergence
    tracker.record(cycle, len(all_new), n_novel)

    # Growth: absorb discoveries as new constants
    novel_discoveries = [d for d in all_new if d.is_novel]
    growth.absorb(novel_discoveries)

    # NEXUS-6 scan after growth.absorb() — verify injected constants (CDO compliance)
    if growth.injected_constants:
        injected_discs = [Discovery(
            formula=f"injected:{k}", value=v, target=k,
            error=0, engine='growth'
        ) for k, v in growth.injected_constants.items()]
        nexus_scan_batch(injected_discs, context=f"cycle-{cycle}-injected")

    # Update discovery graph: add nodes and auto-link relationships
    if graph is not None:
        existing_ids = list(graph.nodes.keys())
        new_ids = []
        for d in all_new:
            nid = graph.add_node(d)
            new_ids.append(nid)
        for nid in new_ids:
            graph.auto_link(nid, existing_ids + new_ids)
        # Report hubs
        hubs = graph.get_hubs(min_edges=3)
        if hubs:
            top = hubs[0]
            print(f"  [GRAPH] {len(graph.nodes)} nodes, "
                  f"{sum(len(e) for e in graph.adjacency.values()) // 2} edges, "
                  f"top hub: {top['node']['target']} ({top['edges']} edges)")

    # Persist
    append_discoveries(all_new)
    save_state(cycle, growth, tracker, graph=graph)

    # Export discoveries to nexus-bridge growth_bus
    bridge_export(all_new, cycle)

    # Paper generation + auto-publish
    if auto_paper:
        paper_path = maybe_generate_paper(growth, cycle)
        if paper_path:
            auto_publish(paper_path, cycle)

    # Periodic dashboard report
    print_dashboard(cycle, growth, tracker, graph, engines)

    return all_new


REPORT_FILE = os.path.join(RESULTS_DIR, 'report.txt')


def _render_dashboard(cycle, growth, tracker, graph, engines_used):
    """Build dashboard lines list. Used by both print and file save."""
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    stage = growth.stage['name']
    total = tracker.total_discoveries
    novel = tracker.total_novel
    injected = len(growth.injected_constants)
    n_nodes = len(graph.nodes) if graph else 0
    n_edges = sum(len(e) for e in graph.adjacency.values()) // 2 if graph else 0
    hubs = graph.get_hubs(min_edges=3) if graph else []
    status = tracker.status

    all_d = growth.all_discoveries
    n_exact = sum(1 for d in all_d if d.grade == '🟩')
    n_struct = sum(1 for d in all_d if d.grade == '🟧')
    n_weak = sum(1 for d in all_d if d.grade == '⚪')

    # Stage progress
    stage_bars = []
    for i, s in enumerate(GrowthEngine.STAGES):
        sn = s['name'][:4]
        if i < growth.stage_idx:
            stage_bars.append(f'{sn} ████ ✅')
        elif i == growth.stage_idx:
            stage_bars.append(f'{sn} ██░░ 🔄')
        else:
            stage_bars.append(f'{sn} ░░░░   ')

    # Discovery trend (last 6 cycles)
    hist = tracker.history[-6:]
    max_d = max((h[1] for h in hist), default=1) or 1

    # Engine stats
    eng_counts = defaultdict(int)
    for d in all_d:
        eng_counts[d.engine] += 1

    # Top discoveries (novel, highest grade)
    top_discs = sorted(
        [d for d in all_d if d.is_novel and d.grade in ('🟩', '🟧')],
        key=lambda d: (d.grade == '🟩', -d.error), reverse=True
    )[:5]

    # Bridge stats
    bridge = _get_bridge()
    bridge_stage = bridge_pts = bridge_active = ""
    if bridge:
        try:
            bs = bridge.status()
            bridge_stage = bs.get("stage", "?")
            bridge_pts = f'{bs.get("growth_points", 0):,}'
            bridge_active = str(bs.get("active", 0))
        except Exception:
            pass

    # Git status
    git_hash = git_msg = git_dirty = ""
    try:
        r = subprocess.run(['git', 'log', '--oneline', '-1'], capture_output=True,
                           text=True, cwd=SCRIPT_DIR, timeout=5)
        if r.returncode == 0:
            parts = r.stdout.strip().split(' ', 1)
            git_hash = parts[0]
            git_msg = parts[1] if len(parts) > 1 else ""
        r2 = subprocess.run(['git', 'status', '--porcelain'], capture_output=True,
                            text=True, cwd=SCRIPT_DIR, timeout=5)
        if r2.returncode == 0:
            n_dirty = len([l for l in r2.stdout.strip().split('\n') if l.strip()])
            git_dirty = f'{n_dirty} files' if n_dirty else 'clean'
    except Exception:
        pass

    w = 67
    sep = '─' * w
    L = []

    def line(content=''):
        if content:
            # Pad to width
            vis_len = len(content)
            padding = w - 2 - vis_len
            if padding < 0:
                padding = 0
            L.append(f'  │  {content}{" " * padding}│')
        else:
            L.append(f'  │{" " * w}│')

    def sep_line():
        L.append(f'  │  {"─" * (w - 2)}│')

    L.append(f'  ┌{sep}┐')
    L.append(f'  │  🔬 TECS-L Discovery Loop — {now:<{w - 34}}│')
    L.append(f'  ├{sep}┤')
    line()
    line(f'■ 발견 루프 — {stage} {"🏔️" if stage == "cosmos" else "🌱" if stage == "seed" else "🌿"}')
    line(f'Cycle: {cycle} | Stage: {stage} | Status: {status}')
    line(f'Discoveries: {total} (🟩{n_exact} 🟧{n_struct} ⚪{n_weak}) | Novel: {novel}')
    line(f'Injected: {injected} | Graph: {n_nodes}n/{n_edges}e | Hubs: {len(hubs)}')
    sep_line()
    line('📈 발달 단계:')
    # Show detailed progress per stage with stats
    for i, s in enumerate(GrowthEngine.STAGES):
        sn = s['name']
        min_d = s['min_discoveries']
        bar_total = 12
        if i < growth.stage_idx:
            bar = '█' * bar_total
            marker = '✅'
            detail = f'{min_d}+ disc'
        elif i == growth.stage_idx:
            if i + 1 < len(GrowthEngine.STAGES):
                next_min = GrowthEngine.STAGES[i + 1]['min_discoveries']
            else:
                next_min = min_d + 1000
            progress = min(1.0, (total - min_d) / max(1, next_min - min_d))
            filled = int(progress * bar_total)
            bar = '█' * filled + '░' * (bar_total - filled)
            marker = '🔄'
            detail = f'{total}/{next_min} disc'
        else:
            bar = '░' * bar_total
            marker = '  '
            detail = f'@{min_d}'
        line(f'  {sn:<8} {bar} {marker} ({detail})')
    line()
    line()

    # Engine breakdown with bars
    line('■ 엔진별 발견')
    sep_line()
    max_eng = max(eng_counts.values(), default=1) or 1
    for eng, cnt in sorted(eng_counts.items(), key=lambda x: -x[1]):
        bar_len = int(cnt / max_eng * 10)
        bar = '━' * bar_len + '░' * (10 - bar_len)
        line(f'  {eng:<16} {bar} {cnt:>5,}')
    line()

    # Top discoveries
    if top_discs:
        line('■ 주요 발견 (Top 5)')
        sep_line()
        for d in top_discs:
            line(f'  {d.grade} {d.formula[:35]:<35} → {d.target}')
        line()

    # Discovery trend — horizontal bar + ASCII line graph
    line('📊 발견 추이:')
    for h in hist:
        bar_len = int(h[1] / max_d * 20)
        line(f'  C{h[0]:>2} |{"█" * bar_len}{"░" * (20 - bar_len)}| {h[1]:>3} ({h[2]} novel)')
    if not hist:
        line('  (no data yet)')
    line()

    # ASCII line graph (novel discoveries curve)
    if len(hist) >= 2:
        novel_vals = [h[2] for h in hist]
        g_max = max(novel_vals) or 1
        g_rows = 5  # graph height
        line('📉 Novel 발견 곡선:')
        for row in range(g_rows, -1, -1):
            threshold = g_max * row / g_rows
            label = f'{int(threshold):>5}' if row in (0, g_rows, g_rows // 2) else '     '
            chars = []
            for i, v in enumerate(novel_vals):
                prev_v = novel_vals[i - 1] if i > 0 else v
                cur_level = v >= threshold
                prev_level = prev_v >= threshold if i > 0 else cur_level
                if cur_level and not prev_level:
                    chars.append('╭──')
                elif not cur_level and prev_level:
                    chars.append('╯  ')
                elif cur_level:
                    chars.append('───')
                else:
                    chars.append('   ')
            line(f'  {label}│{"".join(chars)}')
        line(f'       └{"───" * len(novel_vals)}── Cycle')
        cycle_labels = ''.join(f'C{h[0]:<2}' for h in hist)
        line(f'        {cycle_labels}')
        line()

    # Bridge
    if bridge_stage:
        line(f'■ NEXUS-BRIDGE 🌉 {bridge_stage}')
        line(f'Growth: {bridge_pts} pts | {bridge_active} active')
    line()

    # External validation pending
    pending_ext = [d for d in all_d
                   if d.validate_externally and not d.external_validated]
    validated_ext = sum(1 for d in all_d if d.external_validated)
    if pending_ext or validated_ext:
        line(f'■ External Novelty Check (WebSearch)')
        sep_line()
        line(f'  Pending: {len(pending_ext)} | Validated: {validated_ext}')
        for d in pending_ext[:3]:
            line(f'  → {d.grade} {d.formula[:40]}')
        if len(pending_ext) > 3:
            line(f'  ... and {len(pending_ext) - 3} more')
        line()

    # Git
    if git_hash:
        line(f'■ Git: {git_hash} {git_msg[:45]}')
        line(f'■ Dirty: {git_dirty}')
        line()

    L.append(f'  └{sep}┘')
    return L


def print_dashboard(cycle, growth, tracker, graph, engines_used):
    """Print periodic dashboard report. Also saves to report.txt."""
    lines = _render_dashboard(cycle, growth, tracker, graph, engines_used)
    print('\n' + '\n'.join(lines))

    try:
        with open(REPORT_FILE, 'w') as f:
            f.write('\n'.join(lines) + '\n')
    except Exception:
        pass


def forge_new_constants(growth, tracker):
    """When saturated, try to forge new search directions (nexus LensForge pattern)."""
    print(f"\n  ⚗️  FORGING — search space saturated, generating new targets...")

    # Mutation: create new targets from existing discoveries
    new_targets = mutate_targets(growth.all_discoveries, TARGETS)

    if new_targets:
        # Inject top mutations as new targets
        top_mutations = dict(list(new_targets.items())[:JORDAN_J2])  # cap at J2=24
        TARGETS.update(top_mutations)
        print(f"  ⚗️  Forged {len(top_mutations)} new target values")
        return True
    else:
        print(f"  ⚗️  No new targets could be forged — truly saturated")
        return False


# ═════════════════════════════════════════════════════════════════
# WALL BREAKERS — 6 mechanisms to prevent permanent saturation
# ═════════════════════════════════════════════════════════════════

class WallBreaker:
    """Detects walls and breaks through them. Prevents loop from dying."""

    WALLS = [
        'domain_forge',      # #1: auto-create new domains
        'cross_pollinate',   # #2: cross-domain injection
        'domain_split',      # #3: split overcrowded domains
        'wall_depth_up',     # #4: increase depth on stagnation
        'keyword_absorb',    # #5: extract keywords from discoveries
        'engine_chain',      # #6: chain engine outputs
    ]

    def __init__(self):
        self.walls_broken = defaultdict(int)  # wall_name -> times broken
        self.stagnant_cycles = 0
        self.forged_domains = {}  # name -> {'constants': [...], 'source': ...}
        self.absorbed_keywords = set()
        self.chain_buffer = []  # discoveries from previous engine in chain

    def detect_walls(self, cycle, growth, tracker):
        """Detect which walls are blocking progress. Returns list of wall names."""
        walls = []
        hist = tracker.history

        # Wall 1: Fixed domains — all discoveries from same domains
        if len(hist) >= 3:
            recent_domains = set()
            for d in growth.all_discoveries[-50:]:
                recent_domains.update(d.domains)
            if len(recent_domains) <= 2:
                walls.append('domain_forge')

        # Wall 2: Single engine — no diversity
        recent_engines = set()
        for d in growth.all_discoveries[-30:]:
            recent_engines.add(d.engine)
        if len(recent_engines) <= 1 and len(hist) >= 2:
            walls.append('cross_pollinate')
            walls.append('engine_chain')

        # Wall 3: Domain overcrowding — one domain has 90%+ discoveries
        domain_counts = defaultdict(int)
        for d in growth.all_discoveries:
            for dom in d.domains:
                domain_counts[dom] += 1
        total_d = max(len(growth.all_discoveries), 1)
        for dom, cnt in domain_counts.items():
            if cnt / total_d > 0.8:
                walls.append('domain_split')
                break

        # Wall 4: Stagnation — 3+ cycles with 0 novel
        if len(hist) >= 3:
            last3_novel = [h[2] for h in hist[-3:]]
            if all(n == 0 for n in last3_novel):
                self.stagnant_cycles += 1
                walls.append('wall_depth_up')
            else:
                self.stagnant_cycles = 0

        # Wall 5: Fixed keywords — no new patterns discovered
        if len(hist) >= 4:
            recent_formulas = {d.formula for d in growth.all_discoveries[-20:]}
            old_formulas = {d.formula for d in growth.all_discoveries[:-20]}
            new_patterns = recent_formulas - old_formulas
            if len(new_patterns) < 2:
                walls.append('keyword_absorb')

        return walls

    def break_wall(self, wall_name, growth, tracker):
        """Execute wall-breaking strategy. Returns True if something changed."""
        method = getattr(self, f'_break_{wall_name}', None)
        if method is None:
            return False
        result = method(growth, tracker)
        if result:
            self.walls_broken[wall_name] += 1
            print(f"  🧱→💥 Wall broken: {wall_name} "
                  f"(#{self.walls_broken[wall_name]})")
        return result

    def _break_domain_forge(self, growth, tracker):
        """#1: Create new domain from discovery clusters that don't fit existing ones."""
        # Cluster discoveries by value proximity
        orphans = [d for d in growth.all_discoveries
                   if d.is_novel and d.grade in ('🟩', '🟧') and len(d.domains) <= 1]
        if len(orphans) < 3:
            return False

        # Group orphans by value range
        orphans.sort(key=lambda d: d.value)
        clusters = []
        current = [orphans[0]]
        for d in orphans[1:]:
            if abs(d.value - current[-1].value) < 0.5:
                current.append(d)
            else:
                if len(current) >= 2:
                    clusters.append(current)
                current = [d]
        if len(current) >= 2:
            clusters.append(current)

        if not clusters:
            return False

        # Create new domain from largest cluster
        cluster = max(clusters, key=len)
        domain_id = f'F{len(self.forged_domains)}'
        domain_name = f'Forged_{domain_id}'
        values = {f'{domain_id}_{i}': d.value for i, d in enumerate(cluster)}

        self.forged_domains[domain_name] = {
            'constants': values,
            'source': [d.formula for d in cluster[:5]],
            'center': np.mean([d.value for d in cluster]),
        }

        # Inject into ISLANDS
        ISLANDS[domain_id] = values
        DOMAINS[domain_id] = domain_name

        print(f"  🌐 Domain Forge: created '{domain_name}' with "
              f"{len(values)} constants (center={self.forged_domains[domain_name]['center']:.4f})")
        return True

    def _break_cross_pollinate(self, growth, tracker):
        """#2: Inject domain A discoveries as search targets for domain B."""
        # Get discoveries grouped by engine
        by_engine = defaultdict(list)
        for d in growth.all_discoveries:
            if d.grade in ('🟩', '🟧') and d.is_novel:
                by_engine[d.engine].append(d)

        if len(by_engine) < 1:
            return False

        # Take top discoveries from each engine and cross-inject as targets
        new_targets = {}
        for eng, discs in by_engine.items():
            for d in discs[:SOPFR]:  # top 5 per engine
                for other_eng in by_engine:
                    if other_eng != eng:
                        key = f'xpoll_{eng}→{other_eng}_{d.target}'
                        if key not in TARGETS:
                            new_targets[key] = d.value

        if new_targets:
            TARGETS.update(new_targets)
            print(f"  🌸 Cross-Pollinate: {len(new_targets)} cross-engine targets")
            return True
        return False

    def _break_domain_split(self, growth, tracker):
        """#3: Split overcrowded domain into sub-domains."""
        domain_counts = defaultdict(list)
        for d in growth.all_discoveries:
            for dom in d.domains:
                domain_counts[dom].append(d)

        split_done = False
        for dom, discs in domain_counts.items():
            if len(discs) < 50:
                continue
            # Split by value range into 3 sub-domains
            discs.sort(key=lambda d: d.value)
            n = len(discs)
            thirds = [discs[:n//3], discs[n//3:2*n//3], discs[2*n//3:]]
            suffixes = ['_lo', '_mid', '_hi']

            for chunk, suffix in zip(thirds, suffixes):
                sub_id = f'{dom}{suffix}'
                if sub_id not in ISLANDS:
                    values = {f'{sub_id}_{i}': d.value for i, d in enumerate(chunk[:10])}
                    ISLANDS[sub_id] = values
                    DOMAINS[sub_id] = f'{DOMAINS.get(dom, dom)}{suffix}'
                    split_done = True

            if split_done:
                print(f"  🔀 Domain Split: '{dom}' → "
                      f"{dom}_lo, {dom}_mid, {dom}_hi ({len(discs)} discoveries)")
                break

        return split_done

    def _break_wall_depth_up(self, growth, tracker):
        """#4: Increase search depth and tighten threshold on stagnation."""
        current_stage = growth.stage
        old_depth = current_stage['depth']
        old_thresh = current_stage['threshold']

        # Increase depth by 1 (max 4)
        new_depth = min(old_depth + 1, 4)
        # Tighten threshold by 10x
        new_thresh = old_thresh * 0.1

        if new_depth == old_depth and new_thresh >= old_thresh:
            return False

        # Apply to current stage
        current_stage['depth'] = new_depth
        current_stage['threshold'] = new_thresh

        print(f"  🔽 Depth Up: depth {old_depth}→{new_depth}, "
              f"threshold {old_thresh:.1e}→{new_thresh:.1e}")
        return True

    def _break_keyword_absorb(self, growth, tracker):
        """#5: Extract keywords from discovery formulas to expand classifier."""
        new_keywords = set()
        for d in growth.all_discoveries:
            if d.grade not in ('🟩', '🟧'):
                continue
            # Extract function names and constant names from formulas
            import re
            tokens = re.findall(r'[a-zA-Z_]\w+', d.formula)
            for tok in tokens:
                if tok not in self.absorbed_keywords and len(tok) > 2:
                    new_keywords.add(tok)

        if not new_keywords:
            return False

        self.absorbed_keywords.update(new_keywords)

        # Inject absorbed keywords as new search hints
        for kw in list(new_keywords)[:SIGMA]:  # cap at 12
            for name, val in KNOWN_VALUES.items():
                if kw.lower() in name.lower():
                    key = f'absorb_{kw}_{name}'
                    if key not in TARGETS:
                        TARGETS[key] = val

        print(f"  🧲 Keyword Absorb: {len(new_keywords)} new keywords "
              f"(total: {len(self.absorbed_keywords)})")
        return True

    def _break_engine_chain(self, growth, tracker):
        """#6: Chain engines — output of one becomes input of next."""
        # Collect recent high-grade discoveries
        recent = [d for d in growth.all_discoveries[-20:]
                  if d.grade in ('🟩', '🟧')]
        if not recent:
            return False

        # Create chain targets: each discovery value becomes target for next engine
        chain_targets = {}
        for d in recent:
            # Create compound targets by combining with n=6 constants
            for name, c in [('sigma', SIGMA), ('tau', TAU), ('phi', PHI)]:
                if d.value != 0:
                    chain_targets[f'chain_{d.target}*{name}'] = d.value * c
                    chain_targets[f'chain_{d.target}/{name}'] = d.value / c
                    chain_targets[f'chain_{name}/{d.target}'] = c / d.value

        if chain_targets:
            # Only add novel chain targets
            novel_chains = {k: v for k, v in chain_targets.items()
                           if k not in TARGETS and 1e-6 < abs(v) < 1e8}
            TARGETS.update(dict(list(novel_chains.items())[:JORDAN_J2]))
            self.chain_buffer = recent
            print(f"  🔗 Engine Chain: {len(novel_chains)} chained targets from "
                  f"{len(recent)} discoveries")
            return True
        return False

    def break_all_walls(self, cycle, growth, tracker):
        """Detect and break all walls. Returns number of walls broken."""
        walls = self.detect_walls(cycle, growth, tracker)
        if not walls:
            return 0

        print(f"\n  🧱 Walls detected at cycle {cycle}: {', '.join(walls)}")
        broken = 0
        for wall in walls:
            if self.break_wall(wall, growth, tracker):
                broken += 1

        return broken

    def to_dict(self):
        return {
            'walls_broken': dict(self.walls_broken),
            'stagnant_cycles': self.stagnant_cycles,
            'forged_domains': self.forged_domains,
            'absorbed_keywords': list(self.absorbed_keywords),
        }

    def from_dict(self, d):
        self.walls_broken = defaultdict(int, d.get('walls_broken', {}))
        self.stagnant_cycles = d.get('stagnant_cycles', 0)
        self.forged_domains = d.get('forged_domains', {})
        self.absorbed_keywords = set(d.get('absorbed_keywords', []))


def cmd_report():
    """Print current loop status from saved state (no loop needed).
    Fully reconstructs growth/tracker/graph from persisted files."""
    state = load_state()
    if not state:
        print("  No loop state found. Run the loop first.")
        return

    growth = GrowthEngine()
    growth.stage_idx = state.get('stage_idx', 0)
    growth.injected_constants = state.get('injected_constants', {})

    tracker = ConvergenceTracker()
    tracker.history = state.get('convergence_history', [])

    graph = DiscoveryGraph()
    graph.load()

    # Reconstruct full discovery list from JSONL
    if os.path.exists(DISCOVERIES_FILE):
        with open(DISCOVERIES_FILE) as f:
            for ln in f:
                ln = ln.strip()
                if ln:
                    try:
                        growth.all_discoveries.append(Discovery.from_dict(json.loads(ln)))
                    except Exception:
                        pass

    # Re-check stage based on actual discovery count
    growth.check_stage_up()

    cycle = state.get('cycle', 0)
    engines = list({d.engine for d in growth.all_discoveries}) or ['convergence']

    # Print full dashboard
    print_dashboard(cycle, growth, tracker, graph, engines)

    # Also print quick summary for session chat
    n_exact = sum(1 for d in growth.all_discoveries if d.grade == '🟩')
    n_struct = sum(1 for d in growth.all_discoveries if d.grade == '🟧')
    n_novel = sum(1 for d in growth.all_discoveries if d.is_novel)
    pending_ext = sum(1 for d in growth.all_discoveries
                      if d.validate_externally and not d.external_validated)
    print(f"\n  Quick: {len(growth.all_discoveries)} disc "
          f"(🟩{n_exact} 🟧{n_struct}) | Novel: {n_novel} | "
          f"WebSearch pending: {pending_ext}")


def main():
    # Handle subcommands: report
    if len(sys.argv) > 1 and sys.argv[1] == 'report':
        cmd_report()
        return

    parser = argparse.ArgumentParser(
        description='Discovery Loop — TECS-L Infinite Self-Improving Engine')
    parser.add_argument('--cycles', type=int, default=N,
                        help=f'Number of cycles (0=infinite, default={N})')
    parser.add_argument('--threshold', type=float, default=None,
                        help='Override error threshold')
    parser.add_argument('--depth', type=int, default=None,
                        help='Override search depth')
    parser.add_argument('--paper', action='store_true',
                        help='Auto-generate paper drafts')
    parser.add_argument('--engines', nargs='+',
                        default=['dfs', 'convergence', 'quantum', 'perfect'],
                        help='Engines to run')
    parser.add_argument('--resume', action='store_true',
                        help='Resume from previous state')
    args = parser.parse_args()

    print(f"{'='*70}")
    print(f"  TECS-L DISCOVERY LOOP v1.0")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Cycles: {'∞' if args.cycles == 0 else args.cycles}")
    print(f"  Engines: {', '.join(args.engines)}")
    print(f"  Paper: {'ON' if args.paper else 'OFF'}")
    print(f"{'='*70}")

    growth = GrowthEngine()
    tracker = ConvergenceTracker()
    graph = DiscoveryGraph()
    breaker = WallBreaker()

    # Resume if requested
    start_cycle = 1
    if args.resume:
        state = load_state()
        if state:
            start_cycle = state['cycle'] + 1
            growth.stage_idx = state.get('stage_idx', 0)
            growth.injected_constants = state.get('injected_constants', {})
            tracker.history = state.get('convergence_history', [])
            if 'wall_breaker' in state:
                breaker.from_dict(state['wall_breaker'])
            print(f"  Resumed from cycle {start_cycle - 1}, "
                  f"stage={growth.stage['name']}, "
                  f"{len(growth.injected_constants)} injected constants")
        graph.load()  # load persisted graph if it exists

    if args.threshold:
        for s in GrowthEngine.STAGES:
            s['threshold'] = args.threshold
    if args.depth:
        for s in GrowthEngine.STAGES:
            s['depth'] = args.depth

    max_cycles = args.cycles if args.cycles > 0 else 10000
    forge_attempts = 0
    max_forge = N * TAU  # n=6 × τ=4 = 24 forge attempts before true halt
    wall_break_rounds = 0
    max_wall_rounds = SIGMA  # σ=12 wall-breaking rounds

    for cycle in range(start_cycle, start_cycle + max_cycles):
        discoveries = run_cycle(cycle, growth, tracker,
                                engines=args.engines, auto_paper=args.paper,
                                graph=graph)

        # Check convergence
        status = tracker.status
        if status == 'saturated':
            print(f"\n  ⚠️  SATURATED at cycle {cycle}")

            # Step 1: Try standard forge
            if forge_attempts < max_forge:
                forged = forge_new_constants(growth, tracker)
                if forged:
                    forge_attempts += 1
                    print(f"  → Forge attempt {forge_attempts}/{max_forge}, continuing...")
                    continue

            # Step 2: Wall breakers — the singularity mechanism
            if wall_break_rounds < max_wall_rounds:
                broken = breaker.break_all_walls(cycle, growth, tracker)
                if broken > 0:
                    wall_break_rounds += 1
                    # Reset tracker so it doesn't immediately re-saturate
                    tracker.history.append((cycle, 0, 0))
                    print(f"  → Wall break round {wall_break_rounds}/{max_wall_rounds}, "
                          f"{broken} walls broken, continuing...")
                    continue

            print(f"\n  🏁 LOOP COMPLETE — truly saturated after "
                  f"{forge_attempts} forges + {wall_break_rounds} wall breaks")
            break
        elif status == 'converging':
            print(f"  📉 Convergence detected — discovery rate declining")
            # Proactive wall detection even before full saturation
            breaker.break_all_walls(cycle, growth, tracker)

    # Final summary
    print(f"\n{'='*70}")
    print(f"  FINAL SUMMARY")
    print(f"{'='*70}")
    print(f"  Total cycles: {len(tracker.history)}")
    print(f"  Total discoveries: {tracker.total_discoveries}")
    print(f"  Novel discoveries: {tracker.total_novel}")
    print(f"  Final stage: {growth.stage['name']}")
    print(f"  Injected constants: {len(growth.injected_constants)}")
    print(f"  Forge attempts: {forge_attempts}")
    print(f"  Wall breaks: {wall_break_rounds} ({dict(breaker.walls_broken)})")
    print(f"  Forged domains: {len(breaker.forged_domains)}")
    print(f"  Absorbed keywords: {len(breaker.absorbed_keywords)}")
    print(f"  Status: {tracker.status}")
    n_edges = sum(len(e) for e in graph.adjacency.values()) // 2
    print(f"  Graph: {len(graph.nodes)} nodes, {n_edges} edges, "
          f"{len(graph.get_hubs())} hubs")

    # Force paper if requested and not generated yet
    if args.paper:
        paper_path = maybe_generate_paper(growth, len(tracker.history), force=True)
        if paper_path:
            auto_publish(paper_path, len(tracker.history))

    # Sync nexus-bridge (readmes + atlas)
    bridge_sync()

    # Post-loop SSOT sync: update JSONs, rebuild atlas, generate hypothesis stubs
    post_loop_sync(growth, tracker, graph, breaker, forge_attempts, wall_break_rounds)

    print(f"\n  Results: {RESULTS_DIR}")
    print(f"  Discoveries: {DISCOVERIES_FILE}")


if __name__ == '__main__':
    main()
