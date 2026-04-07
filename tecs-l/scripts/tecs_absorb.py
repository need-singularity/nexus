#!/usr/bin/env python3
"""TECS-L Keyword Absorb — expand domain classifiers from discovery content."""

import json
import os
import sys
import re
from datetime import datetime
from collections import Counter

TECS_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DISCOVERY_LOG = os.path.join(TECS_ROOT, 'config', 'discovery_log.jsonl')
ABSORB_STATE = os.path.join(TECS_ROOT, 'config', 'absorbed_keywords.json')

# Known n=6 function/constant names that appear in formulas
N6_TOKENS = {
    'sigma', 'phi', 'tau', 'mu', 'sopfr', 'J2', 'jordan',
    'euler', 'gamma', 'golden', 'pi', 'ln', 'log', 'exp', 'sqrt',
    'zeta', 'bernoulli', 'ramanujan', 'dedekind', 'carmichael',
    'mertens', 'boltzmann', 'mobius', 'dirichlet',
}

# Stop words — too common to be useful as domain keywords
STOP_WORDS = {
    'the', 'and', 'for', 'with', 'from', 'that', 'this', 'are', 'was',
    'err', 'error', 'value', 'result', 'cross', 'type', 'mode',
    'convergence', 'discovery', 'cycle', 'domain', 'target',
}


def load_json(path):
    if not os.path.isfile(path):
        return {}
    with open(path, 'r') as f:
        return json.load(f)


def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def extract_tokens(content):
    """Extract meaningful tokens from discovery content."""
    # Extract words and function-like tokens
    words = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*', content)
    # Filter: length 3+, not stop words, not pure numbers
    tokens = []
    for w in words:
        w_lower = w.lower()
        if len(w_lower) >= 3 and w_lower not in STOP_WORDS:
            tokens.append(w_lower)
    return tokens


def absorb_keywords():
    """Scan recent discoveries and extract new keywords per domain."""
    if not os.path.isfile(DISCOVERY_LOG):
        return {'absorbed': 0, 'reason': 'no discovery log'}

    # Load existing absorbed keywords
    absorbed = load_json(ABSORB_STATE)
    if not absorbed:
        absorbed = {
            '_meta': {'description': 'Auto-absorbed keywords from discoveries', 'updated': ''},
            'domains': {},
            'global_frequency': {},
        }

    # Read all discoveries
    discoveries = []
    with open(DISCOVERY_LOG) as f:
        for line in f:
            try:
                discoveries.append(json.loads(line.strip()))
            except json.JSONDecodeError:
                pass

    if not discoveries:
        return {'absorbed': 0, 'reason': 'no discoveries'}

    # Count token frequency per domain
    domain_tokens = {}
    global_freq = Counter()

    for d in discoveries:
        domain = d.get('domain', '?')
        content = d.get('content', '')
        tokens = extract_tokens(content)

        domain_tokens.setdefault(domain, Counter())
        domain_tokens[domain].update(tokens)
        global_freq.update(tokens)

    # Find domain-specific keywords (appear more in one domain than others)
    new_keywords = {}
    total_new = 0

    for domain, token_counts in domain_tokens.items():
        domain_specific = []
        for token, count in token_counts.most_common(20):
            # Skip if it's an n=6 constant (already known)
            if token in N6_TOKENS:
                continue

            # Domain specificity: this domain's share of total occurrences
            global_count = global_freq[token]
            if global_count > 0:
                specificity = count / global_count
            else:
                specificity = 1.0

            # Keep if: appears 2+ times AND >50% in this domain
            if count >= 2 and specificity > 0.5:
                domain_specific.append({
                    'keyword': token,
                    'count': count,
                    'specificity': round(specificity, 3),
                })

        if domain_specific:
            existing = set(absorbed.get('domains', {}).get(domain, {}).get('keywords', []))
            new_only = [k for k in domain_specific if k['keyword'] not in existing]

            if new_only:
                absorbed.setdefault('domains', {}).setdefault(domain, {'keywords': [], 'history': []})
                for k in new_only:
                    absorbed['domains'][domain]['keywords'].append(k['keyword'])
                    absorbed['domains'][domain]['history'].append({
                        'keyword': k['keyword'],
                        'absorbed_at': datetime.now().isoformat(),
                        'count': k['count'],
                        'specificity': k['specificity'],
                    })

                new_keywords[domain] = [k['keyword'] for k in new_only]
                total_new += len(new_only)

    # Save
    absorbed['_meta']['updated'] = datetime.now().isoformat()
    absorbed['global_frequency'] = dict(global_freq.most_common(50))
    save_json(ABSORB_STATE, absorbed)

    return {
        'absorbed': total_new,
        'by_domain': new_keywords,
        'top_global': dict(global_freq.most_common(10)),
    }


if __name__ == '__main__':
    result = absorb_keywords()
    print(json.dumps(result, indent=2))
