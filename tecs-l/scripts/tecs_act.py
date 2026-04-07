#!/usr/bin/env python3
"""TECS-L Discovery Action — runs discovery_loop.py (4 engines) and harvests results."""

import json
import os
import sys
import subprocess
from datetime import datetime

TECS_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LOOP_STATE_PATH = os.path.join(TECS_ROOT, 'config', 'loop_state.json')
REGISTRY_PATH = os.path.join(TECS_ROOT, 'config', 'domain_registry.json')

# discovery_loop.py outputs here
DISC_LOOP_JSONL = os.path.join(TECS_ROOT, 'results', 'loop', 'discoveries.jsonl')
DISC_LOOP_STATE = os.path.join(TECS_ROOT, 'results', 'loop', 'loop_state.json')

# Mode → engine selection
MODE_ENGINES = {
    'dfs': ['dfs', 'convergence'],
    'pair': ['convergence', 'quantum'],
    'backtrack': ['convergence', 'perfect'],
}


def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)


def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def count_jsonl_lines(path):
    """Count lines in a JSONL file."""
    if not os.path.isfile(path):
        return 0
    with open(path) as f:
        return sum(1 for _ in f)


def read_jsonl_tail(path, skip=0):
    """Read JSONL entries after skip lines."""
    entries = []
    if not os.path.isfile(path):
        return entries
    with open(path) as f:
        for i, line in enumerate(f):
            if i >= skip:
                try:
                    entries.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    pass
    return entries


def run_discovery_loop(mode):
    """Run discovery_loop.py --cycles 1 --resume with mode-appropriate engines."""
    engine_path = os.path.join(TECS_ROOT, 'discovery_loop.py')
    if not os.path.isfile(engine_path):
        return {'success': False, 'error': 'discovery_loop.py not found'}

    engines = MODE_ENGINES.get(mode, ['dfs', 'convergence', 'quantum', 'perfect'])

    cmd = [
        sys.executable, engine_path,
        '--cycles', '1',
        '--resume',
        '--engines',
    ] + engines

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=300,
            cwd=TECS_ROOT
        )
        if result.returncode == 0:
            return {'success': True, 'stdout': result.stdout[-1000:]}
        else:
            return {
                'success': False,
                'error': (result.stderr or result.stdout or 'unknown')[:500],
            }
    except subprocess.TimeoutExpired:
        return {'success': False, 'error': 'timeout (300s)'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def act(domain_code, mode):
    """Execute discovery action: run 1 cycle of discovery_loop, harvest new discoveries."""
    state = load_json(LOOP_STATE_PATH)
    now = datetime.now().isoformat()

    # Count existing discoveries before running
    before_count = count_jsonl_lines(DISC_LOOP_JSONL)

    # Run discovery_loop.py --cycles 1 --resume
    loop_result = run_discovery_loop(mode)

    # Harvest new discoveries from JSONL
    discoveries = []
    if loop_result['success']:
        new_entries = read_jsonl_tail(DISC_LOOP_JSONL, skip=before_count)
        for entry in new_entries[:12]:  # cap at σ=12
            # Map discovery_loop format to our buffer format
            content_parts = []
            if entry.get('formula'):
                content_parts.append(entry['formula'])
            if entry.get('target'):
                content_parts.append(f"= {entry['target']}")
            if entry.get('value') is not None:
                content_parts.append(f"({entry['value']})")
            if entry.get('error') is not None:
                content_parts.append(f"err={entry['error']}")
            content = ' '.join(content_parts) or json.dumps(entry)

            # Classify domain from entry
            disc_domains = entry.get('domains', [])
            disc_domain = domain_code
            if disc_domains:
                # Map discovery_loop domain names to our codes
                domain_map = {
                    'number': 'N', 'analysis': 'A', 'algebra': 'G',
                    'topology': 'T', 'combinat': 'C', 'quantum': 'Q',
                    'information': 'I', 'statistic': 'S',
                }
                for dd in disc_domains:
                    for key, code in domain_map.items():
                        if key in dd.lower():
                            disc_domain = code
                            break

            discoveries.append({
                'type': entry.get('engine', 'discovery_loop'),
                'domain': disc_domain,
                'content': content,
                'timestamp': entry.get('timestamp', now),
                'mode': mode,
                'validated': False,
                'grade_raw': entry.get('grade', ''),
                'error': entry.get('error'),
                'value': entry.get('value'),
                'consensus': entry.get('consensus', 0),
            })

    # Update state
    if discoveries:
        state['loop']['consecutive_failures'] = 0
        state['discovery_buffer'].extend(discoveries)
    else:
        state['loop']['consecutive_failures'] += 1

    state['loop']['cycle'] += 1
    state['loop']['last_run'] = now
    state['_meta']['updated'] = now

    # Mode rotation on stagnation
    reg = load_json(REGISTRY_PATH)
    domain_data = reg['domains'].get(domain_code, {})
    stagnant = domain_data.get('stagnant_cycles', 0)
    if not discoveries:
        domain_data['stagnant_cycles'] = stagnant + 1
        if domain_data['stagnant_cycles'] >= state['mode_stagnation_trigger']:
            modes = state['mode_rotation']
            current_idx = modes.index(state['loop']['mode']) if state['loop']['mode'] in modes else 0
            state['loop']['mode'] = modes[(current_idx + 1) % len(modes)]
            domain_data['stagnant_cycles'] = 0
    else:
        domain_data['stagnant_cycles'] = 0
    reg['domains'][domain_code] = domain_data
    save_json(REGISTRY_PATH, reg)

    save_json(LOOP_STATE_PATH, state)

    return {
        'discoveries': len(discoveries),
        'cycle': state['loop']['cycle'],
        'mode': state['loop']['mode'],
        'consecutive_failures': state['loop']['consecutive_failures'],
        'buffer_size': len(state['discovery_buffer']),
        'engine_success': loop_result['success'],
        'engine_error': loop_result.get('error', ''),
    }


if __name__ == '__main__':
    domain = sys.argv[1] if len(sys.argv) > 1 else 'N'
    mode = sys.argv[2] if len(sys.argv) > 2 else 'dfs'
    result = act(domain, mode)
    print(json.dumps(result, indent=2))
