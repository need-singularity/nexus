#!/usr/bin/env python3
"""TECS-L Cross-Pollinate — inject discoveries across domains for emergent connections."""

import json
import os
import sys
import re
from datetime import datetime

TECS_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DISCOVERY_LOG = os.path.join(TECS_ROOT, 'config', 'discovery_log.jsonl')
LOOP_STATE_PATH = os.path.join(TECS_ROOT, 'config', 'loop_state.json')
REGISTRY_PATH = os.path.join(TECS_ROOT, 'config', 'domain_registry.json')
POLLINATE_LOG = os.path.join(TECS_ROOT, 'config', 'pollinate_log.jsonl')


def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)


def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def extract_values(content):
    """Extract numeric values from discovery content."""
    pattern = r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?'
    matches = re.findall(pattern, content)
    values = []
    for m in matches:
        try:
            v = float(m)
            if 0.001 < abs(v) < 10000:  # reasonable range
                values.append(v)
        except ValueError:
            pass
    return values


def extract_expressions(content):
    """Extract mathematical expressions from discovery content."""
    # Match patterns like "sigma(6)", "phi(6)^2", "mu(6)/gamma_EM"
    expr_pattern = r'[\w()/*^+-]+\s*=\s*[\w()/*^+-]+'
    return re.findall(expr_pattern, content)


def cross_pollinate():
    """Take recent discoveries and create cross-domain injection candidates."""
    if not os.path.isfile(DISCOVERY_LOG):
        return {'pollinated': 0, 'reason': 'no discovery log'}

    registry = load_json(REGISTRY_PATH)
    state = load_json(LOOP_STATE_PATH)
    domains = list(registry['domains'].keys())

    # Read recent discoveries
    discoveries = []
    with open(DISCOVERY_LOG) as f:
        for line in f:
            try:
                discoveries.append(json.loads(line.strip()))
            except json.JSONDecodeError:
                pass

    if not discoveries:
        return {'pollinated': 0, 'reason': 'no discoveries'}

    # Group by source domain
    by_domain = {}
    for d in discoveries:
        dom = d.get('domain', '?')
        by_domain.setdefault(dom, []).append(d)

    # Cross-pollinate: for each domain's discoveries, create injection targets for OTHER domains
    injections = []
    now = datetime.now().isoformat()

    for src_domain, src_discs in by_domain.items():
        # Get unique values from this domain's discoveries
        all_values = set()
        all_expressions = []
        for d in src_discs[-12:]:  # last sigma=12
            values = extract_values(d.get('content', ''))
            all_values.update(values)
            exprs = extract_expressions(d.get('content', ''))
            all_expressions.extend(exprs)

        # Inject into other domains
        for tgt_domain in domains:
            if tgt_domain == src_domain:
                continue

            # Create cross-domain discovery candidates
            for val in list(all_values)[:6]:  # cap at n=6
                injections.append({
                    'type': 'cross_pollinate',
                    'source_domain': src_domain,
                    'target_domain': tgt_domain,
                    'domain': tgt_domain,
                    'content': f'[CROSS:{src_domain}->{tgt_domain}] value={val}',
                    'value': val,
                    'timestamp': now,
                    'mode': 'pollinate',
                    'validated': False,
                })

    # Add to discovery buffer (not log -- needs validation first)
    if injections:
        # Cap total injections at J2=24
        injections = injections[:24]
        state['discovery_buffer'].extend(injections)
        state['_meta']['updated'] = now
        save_json(LOOP_STATE_PATH, state)

        # Log pollination event
        with open(POLLINATE_LOG, 'a') as f:
            f.write(json.dumps({
                'timestamp': now,
                'injected': len(injections),
                'source_domains': list(by_domain.keys()),
                'target_domains': list(set(i['target_domain'] for i in injections)),
            }) + '\n')

    return {
        'pollinated': len(injections),
        'source_domains': list(by_domain.keys()),
        'unique_values': len(set(i.get('value') for i in injections)),
    }


if __name__ == '__main__':
    result = cross_pollinate()
    print(json.dumps(result, indent=2))
