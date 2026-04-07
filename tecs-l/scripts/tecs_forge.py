#!/usr/bin/env python3
"""TECS-L Domain Forge — auto-create new domains from discovery clusters."""

import json
import os
import sys
import re
from datetime import datetime
from collections import Counter

TECS_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY_PATH = os.path.join(TECS_ROOT, 'config', 'domain_registry.json')
DISCOVERY_LOG = os.path.join(TECS_ROOT, 'config', 'discovery_log.jsonl')
LOOP_STATE_PATH = os.path.join(TECS_ROOT, 'config', 'loop_state.json')

# Candidate new domains with seed keywords
FORGE_CANDIDATES = {
    'M': {
        'name': 'Music/Audio',
        'keywords': ['music', 'audio', 'semitone', 'octave', 'harmonic', 'frequency',
                     'Hz', 'pitch', 'chord', 'interval', 'rhythm', 'tempo', 'tuning',
                     'consonance', 'dissonance', 'clef', 'note', 'scale'],
        'impact_weight': 0.12,
        'related_bt': ['BT-48', 'BT-72', 'BT-108'],
    },
    'K': {
        'name': 'Consciousness',
        'keywords': ['conscious', 'awareness', 'phi', 'iit', 'qualia', 'subjective',
                     'emergence', 'integration', 'attention', 'binding', 'metacognition',
                     'self-reference', 'observer'],
        'impact_weight': 0.13,
        'related_bt': ['BT-36', 'BT-105'],
    },
    'E': {
        'name': 'Evolution',
        'keywords': ['evolution', 'darwin', 'mutation', 'fitness', 'selection', 'adaptation',
                     'speciation', 'phylogeny', 'genetic', 'allele', 'population',
                     'drift', 'niche', 'ouroboros'],
        'impact_weight': 0.11,
        'related_bt': ['BT-51', 'BT-103'],
    },
    'B': {
        'name': 'Biology',
        'keywords': ['biology', 'gene', 'dna', 'rna', 'codon', 'amino', 'protein',
                     'cell', 'mitosis', 'photosynthesis', 'glucose', 'atp',
                     'enzyme', 'metabolism', 'organism'],
        'impact_weight': 0.12,
        'related_bt': ['BT-51', 'BT-101', 'BT-103'],
    },
    'D': {
        'name': 'Material Science',
        'keywords': ['material', 'crystal', 'diamond', 'carbon', 'graphene', 'lattice',
                     'alloy', 'polymer', 'ceramic', 'semiconductor', 'bandgap',
                     'coordination', 'doping', 'synthesis'],
        'impact_weight': 0.11,
        'related_bt': ['BT-85', 'BT-86', 'BT-87', 'BT-88', 'BT-93'],
    },
    'P': {
        'name': 'Cosmology/Particle',
        'keywords': ['cosmology', 'dark', 'neutrino', 'cmb', 'particle', 'higgs',
                     'quark', 'lepton', 'boson', 'inflation', 'big-bang',
                     'baryon', 'antimatter', 'weinberg'],
        'impact_weight': 0.10,
        'related_bt': ['BT-97', 'BT-110'],
    },
}


def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)


def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def scan_hypotheses_for_domain(candidate):
    """Count how many hypotheses match a candidate domain's keywords."""
    import glob
    hyp_dir = os.path.join(TECS_ROOT, 'docs', 'hypotheses')
    if not os.path.isdir(hyp_dir):
        return 0
    count = 0
    for fpath in glob.glob(os.path.join(hyp_dir, '*.md')):
        fname = os.path.basename(fpath).lower()
        for kw in candidate['keywords']:
            if kw.lower() in fname:
                count += 1
                break
    return count


def scan_discoveries_for_domain(candidate):
    """Count how many logged discoveries match a candidate domain."""
    if not os.path.isfile(DISCOVERY_LOG):
        return 0
    count = 0
    with open(DISCOVERY_LOG) as f:
        for line in f:
            try:
                d = json.loads(line.strip())
                content = d.get('content', '').lower()
                for kw in candidate['keywords']:
                    if kw.lower() in content:
                        count += 1
                        break
            except json.JSONDecodeError:
                pass
    return count


def check_all_thriving(registry):
    """Check if all existing domains are thriving (no urgent gaps)."""
    for code, dom in registry['domains'].items():
        if dom.get('health') in ('critical', 'behind'):
            return False
    return True


def forge_domains():
    """Check conditions and forge new domains if warranted."""
    registry = load_json(REGISTRY_PATH)
    state = load_json(LOOP_STATE_PATH)

    # Only forge when existing domains are healthy
    all_healthy = check_all_thriving(registry)

    forged = []
    for code, candidate in FORGE_CANDIDATES.items():
        # Skip if already exists
        if code in registry['domains']:
            continue

        # Count hypothesis coverage
        hyp_count = scan_hypotheses_for_domain(candidate)
        disc_count = scan_discoveries_for_domain(candidate)

        # Forge threshold: at least 10 hypotheses OR all domains thriving
        if hyp_count >= 10 or (all_healthy and hyp_count >= 3):
            registry['domains'][code] = {
                'name': candidate['name'],
                'hypothesis_count': hyp_count,
                'verified_count': 0,
                'exact_count': 0,
                'last_discovery': None,
                'health': 'unknown',
                'gap': 1.0,
                'impact_weight': candidate['impact_weight'],
                'target_exact_rate': 0.6,
                'stagnant_cycles': 0,
                'forged': True,
                'forged_at': datetime.now().isoformat(),
                'related_bt': candidate.get('related_bt', []),
            }
            forged.append({
                'code': code,
                'name': candidate['name'],
                'hypothesis_count': hyp_count,
                'discovery_count': disc_count,
            })

    if forged:
        registry['_meta']['updated'] = datetime.now().isoformat()
        save_json(REGISTRY_PATH, registry)

    return {
        'forged': len(forged),
        'domains': forged,
        'total_domains': len(registry['domains']),
        'all_healthy': all_healthy,
    }


if __name__ == '__main__':
    result = forge_domains()
    print(json.dumps(result, indent=2))
