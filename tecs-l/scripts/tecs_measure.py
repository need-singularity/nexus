#!/usr/bin/env python3
"""TECS-L Domain Health Measurement — scans 8 domains and updates registry."""

import json
import os
import sys
import glob
from datetime import datetime

TECS_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(TECS_ROOT, '.shared'))

REGISTRY_PATH = os.path.join(TECS_ROOT, 'config', 'domain_registry.json')
HYPOTHESES_DIR = os.path.join(TECS_ROOT, 'docs', 'hypotheses')
VERIFY_DIR = os.path.join(TECS_ROOT, 'verify')

# Domain keyword mapping — matches hypothesis filenames to domains
DOMAIN_KEYWORDS = {
    'N': ['number', 'sigma', 'tau', 'phi', 'perfect', 'divisor', 'prime', 'euler-totient',
          'mobius', 'sopfr', 'arithmetic'],
    'A': ['analysis', 'zeta', 'log', 'ln', 'sqrt', 'pi', 'euler-mascheroni',
          'riemann', 'gamma', 'golden'],
    'G': ['group', 'algebra', 'su2', 'su3', 'e8', 'lie', 'symmetry',
          'representation', 'lattice', 'leech'],
    'T': ['topology', 'kissing', 'betti', 'homology', 'manifold', 'knot',
          'dimension', 'euler-char', 'homotopy'],
    'C': ['combinat', 'fibonacci', 'catalan', 'bell', 'partition', 'ramsey',
          'feigenbaum', 'stirling', 'graph'],
    'Q': ['quantum', 'fine-structure', 'alpha', 'planck', 'bohr', 'mass-ratio',
          'cmb', 'neutrino', 'weinberg'],
    'I': ['information', 'entropy', 'shannon', 'channel', 'capacity', 'qubit',
          'qutrit', 'holevo', 'coding'],
    'S': ['statistic', 'ising', 'boltzmann', 'critical', 'onsager', 'thermo',
          'percolation', 'phase-transition', 'mean-field'],
}


def classify_hypothesis(filename):
    """Classify a hypothesis file into domain(s) by keyword matching."""
    fname_lower = filename.lower()
    matches = []
    for domain, keywords in DOMAIN_KEYWORDS.items():
        for kw in keywords:
            if kw in fname_lower:
                matches.append(domain)
                break
    return matches if matches else ['N']  # default to Number Theory


def count_exact_in_file(filepath):
    """Count EXACT grades in a hypothesis/verification file."""
    try:
        content = open(filepath, 'r', encoding='utf-8', errors='ignore').read()
        return content.upper().count('EXACT')
    except Exception:
        return 0


def measure_all_domains():
    """Scan hypothesis and verify dirs, compute per-domain metrics."""
    # Load current registry
    with open(REGISTRY_PATH, 'r') as f:
        registry = json.load(f)

    # Reset counts
    for d in registry['domains']:
        registry['domains'][d]['hypothesis_count'] = 0
        registry['domains'][d]['verified_count'] = 0
        registry['domains'][d]['exact_count'] = 0

    # Count hypotheses per domain
    if os.path.isdir(HYPOTHESES_DIR):
        for fpath in glob.glob(os.path.join(HYPOTHESES_DIR, '*.md')):
            fname = os.path.basename(fpath)
            domains = classify_hypothesis(fname)
            exact = count_exact_in_file(fpath)
            for d in domains:
                if d in registry['domains']:
                    registry['domains'][d]['hypothesis_count'] += 1
                    registry['domains'][d]['exact_count'] += exact

    # Count verifications per domain
    if os.path.isdir(VERIFY_DIR):
        for fpath in glob.glob(os.path.join(VERIFY_DIR, '*.py')):
            fname = os.path.basename(fpath)
            domains = classify_hypothesis(fname)
            for d in domains:
                if d in registry['domains']:
                    registry['domains'][d]['verified_count'] += 1

    # Compute health for each domain
    for code, dom in registry['domains'].items():
        total = dom['hypothesis_count']
        verified = dom['verified_count']
        exact = dom['exact_count']

        if total == 0:
            exact_rate = 0.0
            verify_rate = 0.0
        else:
            exact_rate = exact / max(total, 1)
            verify_rate = verified / max(total, 1)

        target = dom['target_exact_rate']
        progress = min(exact_rate / target, 1.0) if target > 0 else 1.0
        dom['gap'] = round(1.0 - progress, 4)

        # Health classification
        if dom['gap'] > 0.75:
            dom['health'] = 'critical'
        elif dom['stagnant_cycles'] >= 3:
            dom['health'] = 'stagnant'
        elif dom['gap'] > 0.4:
            dom['health'] = 'behind'
        elif dom['gap'] > 0.1:
            dom['health'] = 'on_track'
        else:
            dom['health'] = 'thriving'

    registry['_meta']['updated'] = datetime.now().isoformat()

    with open(REGISTRY_PATH, 'w') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)

    return registry


def pick_weakest(registry):
    """Pick the domain with highest gap * impact_weight."""
    best_domain = None
    best_score = -1.0
    for code, dom in registry['domains'].items():
        score = dom['gap'] * dom['impact_weight']
        if score > best_score:
            best_score = score
            best_domain = code
    return best_domain, best_score


if __name__ == '__main__':
    registry = measure_all_domains()
    target, score = pick_weakest(registry)
    print(json.dumps({
        'target_domain': target,
        'priority_score': round(score, 4),
        'domain_name': registry['domains'][target]['name'],
        'health': registry['domains'][target]['health'],
        'gap': registry['domains'][target]['gap'],
    }))
