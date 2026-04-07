#!/usr/bin/env python3
"""TECS-L Engine Chain — chain discovery engines for deeper exploration."""

import json
import os
import sys
import subprocess
from datetime import datetime

TECS_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOOP_STATE_PATH = os.path.join(TECS_ROOT, 'config', 'loop_state.json')
DISCOVERY_LOG = os.path.join(TECS_ROOT, 'config', 'discovery_log.jsonl')


def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)


def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_recent_values(n=12):
    """Extract numeric values from recent discoveries as chain inputs."""
    if not os.path.isfile(DISCOVERY_LOG):
        return []

    values = []
    with open(DISCOVERY_LOG) as f:
        lines = f.readlines()

    for line in lines[-n:]:
        try:
            d = json.loads(line.strip())
            v = d.get('value')
            if v is not None and isinstance(v, (int, float)):
                values.append(v)
        except (json.JSONDecodeError, TypeError):
            pass

    return values


def run_chained_cycle(depth=2, threshold=0.001):
    """Run discovery_loop with chained parameters from previous discoveries."""
    state = load_json(LOOP_STATE_PATH)
    wall_state = state.get('wall_breaks', {})

    # Use wall-break adjusted depth/threshold if available
    effective_depth = wall_state.get('depth', depth)
    effective_threshold = wall_state.get('threshold', threshold)

    # Get chain inputs from previous discoveries
    chain_values = get_recent_values(12)

    # Select engines based on what's available and chain depth
    engine_sets = [
        ['dfs', 'convergence'],           # Level 1: basic
        ['convergence', 'quantum'],       # Level 2: cross
        ['dfs', 'convergence', 'quantum', 'perfect'],  # Level 3: full
    ]

    level = min(effective_depth - 1, len(engine_sets) - 1)
    engines = engine_sets[max(0, level)]

    # Run discovery_loop.py with adjusted parameters
    engine_path = os.path.join(TECS_ROOT, 'discovery_loop.py')
    if not os.path.isfile(engine_path):
        return {'success': False, 'error': 'discovery_loop.py not found'}

    cmd = [
        sys.executable, engine_path,
        '--cycles', '1',
        '--resume',
        '--depth', str(effective_depth),
        '--threshold', str(effective_threshold),
        '--engines',
    ] + engines

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=300,
            cwd=TECS_ROOT
        )
        return {
            'success': result.returncode == 0,
            'depth': effective_depth,
            'threshold': effective_threshold,
            'engines': engines,
            'chain_inputs': len(chain_values),
            'stdout_tail': result.stdout[-500:] if result.stdout else '',
        }
    except subprocess.TimeoutExpired:
        return {'success': False, 'error': 'timeout (300s)'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


if __name__ == '__main__':
    result = run_chained_cycle()
    print(json.dumps(result, indent=2))
