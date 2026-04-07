#!/usr/bin/env python3
"""TECS-L Domain Split — auto-split oversized domains into focused sub-domains."""

import json
import os
import sys
import glob
from datetime import datetime
from collections import Counter

TECS_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY_PATH = os.path.join(TECS_ROOT, 'config', 'domain_registry.json')
HYPOTHESES_DIR = os.path.join(TECS_ROOT, 'docs', 'hypotheses')

SPLIT_THRESHOLD = 500  # split when hypothesis_count exceeds this

# Sub-domain definitions for splittable domains
SPLIT_MAP = {
    'N': {
        'N1': {
            'name': 'Prime/Divisor',
            'keywords': ['prime', 'divisor', 'factor', 'sieve', 'twin', 'mersenne',
                         'fermat', 'goldbach', 'gap', 'distribution'],
        },
        'N2': {
            'name': 'Arithmetic Functions',
            'keywords': ['sigma', 'tau', 'phi', 'euler', 'totient', 'mobius', 'sopfr',
                         'perfect', 'abundant', 'deficient', 'aliquot'],
        },
        'N3': {
            'name': 'Sequences/Constants',
            'keywords': ['fibonacci', 'catalan', 'bernoulli', 'harmonic', 'pi', 'e',
                         'golden', 'gamma', 'zeta', 'constant', 'sequence'],
        },
    },
    'A': {
        'A1': {
            'name': 'Real/Complex Analysis',
            'keywords': ['continuous', 'differentiable', 'integral', 'series',
                         'convergence', 'analytic', 'holomorphic', 'residue'],
        },
        'A2': {
            'name': 'Special Functions',
            'keywords': ['zeta', 'gamma', 'beta', 'bessel', 'legendre',
                         'hypergeometric', 'elliptic', 'modular'],
        },
    },
}


def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)


def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def classify_to_subdomain(filename, subdomain_map):
    """Classify a hypothesis file into a sub-domain."""
    fname_lower = filename.lower()
    for sub_code, sub_def in subdomain_map.items():
        for kw in sub_def['keywords']:
            if kw in fname_lower:
                return sub_code
    return None


def count_exact_in_file(filepath):
    try:
        content = open(filepath, 'r', encoding='utf-8', errors='ignore').read()
        return content.upper().count('EXACT')
    except Exception:
        return 0


def split_domains():
    """Check for oversized domains and split them."""
    registry = load_json(REGISTRY_PATH)
    splits = []

    for parent_code, parent_dom in list(registry['domains'].items()):
        # Only split if above threshold and has split map
        if parent_dom.get('hypothesis_count', 0) < SPLIT_THRESHOLD:
            continue
        if parent_code not in SPLIT_MAP:
            continue

        # Check if already split (sub-domains exist)
        subdomain_map = SPLIT_MAP[parent_code]
        already_split = any(sc in registry['domains'] for sc in subdomain_map)
        if already_split:
            continue

        # Count hypotheses per sub-domain
        sub_counts = {sc: {'hyp': 0, 'exact': 0} for sc in subdomain_map}
        unclassified = 0

        if os.path.isdir(HYPOTHESES_DIR):
            for fpath in glob.glob(os.path.join(HYPOTHESES_DIR, '*.md')):
                fname = os.path.basename(fpath)
                sub = classify_to_subdomain(fname, subdomain_map)
                if sub:
                    sub_counts[sub]['hyp'] += 1
                    sub_counts[sub]['exact'] += count_exact_in_file(fpath)
                else:
                    # Check if it belongs to parent domain at all
                    from tecs_measure import classify_hypothesis, DOMAIN_KEYWORDS
                    domains = classify_hypothesis(fname)
                    if parent_code in domains:
                        unclassified += 1

        # Create sub-domains
        parent_weight = parent_dom.get('impact_weight', 0.12)
        n_subs = len(subdomain_map)

        for sub_code, sub_def in subdomain_map.items():
            counts = sub_counts[sub_code]
            registry['domains'][sub_code] = {
                'name': sub_def['name'],
                'hypothesis_count': counts['hyp'],
                'verified_count': 0,
                'exact_count': counts['exact'],
                'last_discovery': None,
                'health': 'unknown',
                'gap': 1.0,
                'impact_weight': round(parent_weight / n_subs, 4),
                'target_exact_rate': 0.6,
                'stagnant_cycles': 0,
                'parent_domain': parent_code,
                'split_from': parent_code,
                'split_at': datetime.now().isoformat(),
            }

        splits.append({
            'parent': parent_code,
            'children': list(subdomain_map.keys()),
            'sub_counts': {k: v['hyp'] for k, v in sub_counts.items()},
            'unclassified': unclassified,
        })

    if splits:
        registry['_meta']['updated'] = datetime.now().isoformat()
        save_json(REGISTRY_PATH, registry)

    return {
        'splits': len(splits),
        'details': splits,
        'total_domains': len(registry['domains']),
    }


if __name__ == '__main__':
    # Add scripts dir to path for tecs_measure import
    sys.path.insert(0, os.path.join(TECS_ROOT, 'scripts'))
    result = split_domains()
    print(json.dumps(result, indent=2))
