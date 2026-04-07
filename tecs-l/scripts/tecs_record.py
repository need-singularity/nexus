#!/usr/bin/env python3
"""TECS-L Discovery Recorder — writes confirmed discoveries to atlas and hypothesis files."""

import json
import os
import sys
from datetime import datetime

TECS_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOOP_STATE_PATH = os.path.join(TECS_ROOT, 'config', 'loop_state.json')
DISCOVERY_LOG = os.path.join(TECS_ROOT, 'config', 'discovery_log.jsonl')
HYPOTHESES_DIR = os.path.join(TECS_ROOT, 'docs', 'hypotheses')


def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)


def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def notify_bridge(recorded):
    """Notify nexus-bridge of new discoveries for growth + routing."""
    if not recorded:
        return {'notified': False, 'reason': 'no discoveries'}

    bridge_path = os.path.expanduser('~/Dev/nexus')
    bridge_pkg = os.path.join(bridge_path, 'nexus-bridge')

    if not os.path.isdir(bridge_pkg):
        return {'notified': False, 'reason': 'nexus-bridge not found'}

    try:
        sys.path.insert(0, bridge_pkg)
        from bridge import NexusBridge

        bridge = NexusBridge(nexus_root=bridge_path)

        # Add growth points for discoveries
        points = len(recorded) * bridge.config['growth']['points_per_discovery']
        bridge._add_growth(points, f"tecs-loop: {len(recorded)} discoveries")

        # Route each discovery to relevant projects
        routed = 0
        for disc in recorded:
            domain = disc.get('domain', 'N')
            # Map domain to content type for routing
            content_type_map = {
                'N': 'hypothesis', 'A': 'hypothesis', 'G': 'hypothesis',
                'T': 'hypothesis', 'C': 'hypothesis', 'Q': 'physics',
                'I': 'computation', 'S': 'physics',
            }
            content_type = content_type_map.get(domain, 'hypothesis')
            target = bridge.route(content_type, 'TECS-L')
            if target:
                routed += 1

        bridge._save_state()
        return {'notified': True, 'points': points, 'routed': routed}
    except Exception as e:
        return {'notified': False, 'reason': str(e)}


def record_discoveries():
    """Move CONFIRMED discoveries from buffer to permanent storage."""
    state = load_json(LOOP_STATE_PATH)
    recorded = []
    remaining = []

    for disc in state['discovery_buffer']:
        if disc.get('grade') == 'CONFIRMED' and disc.get('validated'):
            # Append to discovery log (JSONL)
            with open(DISCOVERY_LOG, 'a') as f:
                f.write(json.dumps(disc, ensure_ascii=False) + '\n')

            recorded.append(disc)
        else:
            remaining.append(disc)

    state['discovery_buffer'] = remaining
    state['_meta']['updated'] = datetime.now().isoformat()
    save_json(LOOP_STATE_PATH, state)

    # Run atlas sync if discoveries were recorded
    if recorded:
        atlas_script = os.path.join(TECS_ROOT, '.shared', 'scan_math_atlas.py')
        if os.path.isfile(atlas_script):
            os.system(f'{sys.executable} {atlas_script} --save --summary 2>/dev/null')

    # Notify nexus-bridge
    bridge_result = notify_bridge(recorded)

    return {
        'recorded': len(recorded),
        'remaining_buffer': len(remaining),
        'total_in_log': sum(1 for _ in open(DISCOVERY_LOG)) if os.path.isfile(DISCOVERY_LOG) else 0,
        'bridge': bridge_result if recorded else None,
    }


if __name__ == '__main__':
    result = record_discoveries()
    print(json.dumps(result, indent=2))
