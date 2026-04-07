#!/usr/bin/env python3
"""TECS-L Wall Detect — auto-increase depth and tighten threshold on plateau."""

import json
import os
import sys
from datetime import datetime

TECS_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOOP_STATE_PATH = os.path.join(TECS_ROOT, 'config', 'loop_state.json')
WALL_LOG = os.path.join(TECS_ROOT, 'config', 'wall_breaks.jsonl')

# Wall detection parameters
DECLINE_WINDOW = 3        # consecutive declining cycles to trigger
MIN_CYCLES_BEFORE = 3     # minimum cycles before wall detection activates
MAX_DEPTH = 6             # n=6 maximum depth
THRESHOLD_FACTOR = 0.1    # multiply threshold by this on wall break


def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)


def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_cycle_history(state):
    """Extract per-cycle discovery counts from publish history."""
    counts = []
    for pub in state.get('publish_history', []):
        counts.append(pub.get('discovery_count', 0))
    return counts


def detect_wall(counts):
    """Check if last DECLINE_WINDOW cycles show declining or zero discoveries."""
    if len(counts) < DECLINE_WINDOW:
        return False, 'not enough cycles'

    recent = counts[-DECLINE_WINDOW:]

    # All zeros = wall
    if all(c == 0 for c in recent):
        return True, 'zero_wall'

    # Strictly declining = wall
    declining = all(recent[i] >= recent[i+1] for i in range(len(recent)-1))
    if declining and recent[-1] < recent[0]:
        return True, 'decline_wall'

    # Plateau (all same, non-zero) after enough cycles
    if len(set(recent)) == 1 and len(counts) >= MIN_CYCLES_BEFORE * 2:
        return True, 'plateau_wall'

    return False, 'no_wall'


def break_wall():
    """Detect walls and apply depth/threshold adjustments."""
    state = load_json(LOOP_STATE_PATH)
    loop = state['loop']

    # Initialize wall-break state if not present
    wall_state = state.setdefault('wall_breaks', {
        'depth': 2,           # current search depth
        'threshold': 0.001,   # current error threshold
        'breaks_count': 0,    # total wall breaks
        'last_break': None,
    })

    cycle_counts = get_cycle_history(state)
    is_wall, wall_type = detect_wall(cycle_counts)

    result = {
        'wall_detected': is_wall,
        'wall_type': wall_type,
        'current_depth': wall_state['depth'],
        'current_threshold': wall_state['threshold'],
        'action': 'none',
    }

    if not is_wall:
        return result

    now = datetime.now().isoformat()
    actions = []

    # Action 1: Increase depth (up to MAX_DEPTH)
    old_depth = wall_state['depth']
    if old_depth < MAX_DEPTH:
        wall_state['depth'] = old_depth + 1
        actions.append(f'depth {old_depth}\u2192{wall_state["depth"]}')

    # Action 2: Tighten threshold (multiply by 0.1)
    old_threshold = wall_state['threshold']
    new_threshold = old_threshold * THRESHOLD_FACTOR
    if new_threshold >= 1e-12:  # floor
        wall_state['threshold'] = new_threshold
        actions.append(f'threshold {old_threshold}\u2192{new_threshold}')

    # Action 3: Reset consecutive failures to give fresh start
    loop['consecutive_failures'] = 0

    # Action 4: Force mode rotation
    modes = state.get('mode_rotation', ['dfs', 'pair', 'backtrack'])
    current_mode = loop.get('mode', 'dfs')
    if current_mode in modes:
        idx = modes.index(current_mode)
        loop['mode'] = modes[(idx + 1) % len(modes)]
        actions.append(f'mode {current_mode}\u2192{loop["mode"]}')

    wall_state['breaks_count'] += 1
    wall_state['last_break'] = now
    state['_meta']['updated'] = now
    save_json(LOOP_STATE_PATH, state)

    # Log wall break
    with open(WALL_LOG, 'a') as f:
        f.write(json.dumps({
            'timestamp': now,
            'wall_type': wall_type,
            'actions': actions,
            'depth': wall_state['depth'],
            'threshold': wall_state['threshold'],
            'breaks_total': wall_state['breaks_count'],
            'cycle': loop.get('cycle', 0),
        }) + '\n')

    result.update({
        'action': 'wall_break',
        'actions': actions,
        'new_depth': wall_state['depth'],
        'new_threshold': wall_state['threshold'],
        'breaks_total': wall_state['breaks_count'],
    })

    return result


if __name__ == '__main__':
    result = break_wall()
    print(json.dumps(result, indent=2))
