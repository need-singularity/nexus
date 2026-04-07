#!/usr/bin/env python3
"""TECS-L Discovery Loop Report — ASCII dashboard (anima 극가속 양식 호환)."""

import json
import os
import sys
from datetime import datetime

TECS_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOOP_STATE_PATH = os.path.join(TECS_ROOT, 'config', 'loop_state.json')
REGISTRY_PATH = os.path.join(TECS_ROOT, 'config', 'domain_registry.json')
DISCOVERY_LOG = os.path.join(TECS_ROOT, 'config', 'discovery_log.jsonl')
LOOP_RESULTS = os.path.join(TECS_ROOT, 'results', 'loop')
GRAPH_PATH = os.path.join(LOOP_RESULTS, 'discovery_graph.json')

W = 65  # box inner width


def load_json(path):
    if not os.path.isfile(path):
        return {}
    with open(path, 'r') as f:
        return json.load(f)


def read_log_all():
    entries = []
    if not os.path.isfile(DISCOVERY_LOG):
        return entries
    with open(DISCOVERY_LOG) as f:
        for line in f:
            try:
                entries.append(json.loads(line.strip()))
            except json.JSONDecodeError:
                pass
    return entries


def bar(filled, total, width=12):
    if total == 0:
        return '░' * width
    ratio = min(filled / total, 1.0)
    n = int(ratio * width)
    return '█' * n + '░' * (width - n)


def stage_for_discoveries(n):
    """Map total discoveries to growth stage."""
    if n >= 1000:
        return 'cosmic', 5
    if n >= 500:
        return 'forest', 4
    if n >= 200:
        return 'tree', 3
    if n >= 50:
        return 'sapling', 2
    if n >= 10:
        return 'sprout', 1
    return 'seed', 0


def pad(text, width):
    """Pad text to width accounting for wide chars and emoji."""
    # Count display width (CJK = 2, emoji ~ 2, ASCII = 1)
    display_w = 0
    for ch in text:
        cp = ord(ch)
        if cp > 0x1F600 or (0x2600 <= cp <= 0x27BF) or (0xFE00 <= cp <= 0xFE0F):
            display_w += 2
        elif (0x3000 <= cp <= 0x9FFF) or (0xAC00 <= cp <= 0xD7AF) or (0xF900 <= cp <= 0xFAFF):
            display_w += 2
        else:
            display_w += 1
    padding = max(0, width - display_w)
    return text + ' ' * padding


def L(lines, text):
    """Add a box line."""
    lines.append(f'│  {pad(text, W - 2)}│')


def generate_report():
    now = datetime.now()
    state = load_json(LOOP_STATE_PATH)
    reg = load_json(REGISTRY_PATH)
    graph = load_json(GRAPH_PATH)
    loop = state.get('loop', {})
    papers = state.get('publish_history', [])
    all_disc = read_log_all()
    total = len(all_disc)

    # Grade counts (priority: 🟩 > 🟧 > ⚪)
    grade_exact = 0
    grade_struct = 0
    grade_other = 0
    for d in all_disc:
        raw = d.get('grade_raw', '')
        if '🟩' in raw or d.get('grade') == 'CONFIRMED':
            grade_exact += 1
        elif '🟧' in raw:
            grade_struct += 1
        else:
            grade_other += 1

    # Novel count
    novel = sum(1 for d in all_disc if d.get('consensus', 0) >= 0)

    # Graph stats
    nodes = len(graph.get('nodes', {}))
    edges = sum(len(e) for e in graph.get('adjacency', {}).values()) // 2
    hubs = len([n for n, e in graph.get('adjacency', {}).items() if len(e) >= 3])

    # Stage
    stage_name, stage_idx = stage_for_discoveries(total)
    stages = ['seed', 'sprout', 'sapling', 'tree', 'forest', 'cosmic']

    # Per-cycle discovery counts
    cycle_map = {}
    for d in all_disc:
        # Use timestamp to group by rough cycle
        mode = d.get('mode', '?')
        cycle_map.setdefault(mode, 0)
        cycle_map[mode] += 1

    # Engine distribution
    engine_dist = {}
    for d in all_disc:
        eng = d.get('type', '?')
        engine_dist[eng] = engine_dist.get(eng, 0) + 1

    # Domain distribution
    domain_dist = {}
    for d in all_disc:
        dom = d.get('domain', '?')
        domain_dist[dom] = domain_dist.get(dom, 0) + 1

    # Bridge
    bs = None
    try:
        bridge_pkg = os.path.expanduser('~/Dev/nexus/nexus-bridge')
        sys.path.insert(0, bridge_pkg)
        from bridge import NexusBridge
        b = NexusBridge(nexus_root=os.path.expanduser('~/Dev/nexus'))
        bs = b.status()
    except Exception:
        pass

    # ── Render ──────────────────────────────────────────
    lines = []

    lines.append(f'┌{"─" * (W + 2)}┐')
    L(lines, f'🔬 TECS-L Discovery Loop — {now.strftime("%Y-%m-%d %H:%M")}')
    lines.append(f'├{"─" * (W + 2)}┤')
    L(lines, '')

    # ■ Loop status
    L(lines, f'■ 발견 루프')
    status = 'exploring' if loop.get('consecutive_failures', 0) == 0 else 'stalled'
    L(lines, f'Cycle: {loop.get("cycle", 0)} | Stage: {stage_name} | Status: {status}')
    L(lines, f'Discoveries: {total} (🟩{grade_exact} 🟧{grade_struct} ⚪{grade_other}) | Novel: {novel}')
    L(lines, f'Injected: {total} | Graph: {nodes}n/{edges}e | Hubs: {hubs}')
    L(lines, '─' * (W - 2))

    # Stage progress
    L(lines, '📈 발달 단계:')
    stage_line1 = ''
    stage_line2 = ''
    for i, s in enumerate(stages[:3]):
        abbr = s[:4]
        if i < stage_idx:
            stage_line1 += f'{abbr} {"█" * 4} ✅  '
        elif i == stage_idx:
            stage_line1 += f'{abbr} {"█" * 2}{"░" * 2} 🔄  '
        else:
            stage_line1 += f'{abbr} {"░" * 4}      '
    for i, s in enumerate(stages[3:6], 3):
        abbr = s[:4]
        if i < stage_idx:
            stage_line2 += f'{abbr} {"█" * 4} ✅  '
        elif i == stage_idx:
            stage_line2 += f'{abbr} {"█" * 2}{"░" * 2} 🔄  '
        else:
            stage_line2 += f'{abbr} {"░" * 4}      '
    L(lines, stage_line1.rstrip())
    L(lines, stage_line2.rstrip())
    L(lines, '')

    # Discovery per cycle chart
    L(lines, '📊 발견 추이:')
    cycle_count = loop.get('cycle', 0)
    if papers:
        for i, p in enumerate(papers[-6:], 1):
            cnt = p.get('discovery_count', 0)
            b = '█' * min(cnt, 20)
            L(lines, f'    C{i:2} |{b:<20}|  {cnt}')
    elif cycle_count > 0:
        avg = total / max(cycle_count, 1)
        L(lines, f'    avg {avg:.1f}/cycle × {cycle_count} cycles = {total} total')
    L(lines, '')

    # Engine breakdown
    L(lines, '⚙️  엔진별:')
    for eng, cnt in sorted(engine_dist.items(), key=lambda x: -x[1]):
        L(lines, f'  {eng:<18} {cnt} discoveries')
    L(lines, '')

    # Domain breakdown
    L(lines, '🗺️  도메인별:')
    domains = reg.get('domains', {})
    for code in ['N', 'A', 'G', 'T', 'C', 'Q', 'I', 'S']:
        d = domains.get(code, {})
        name = d.get('name', code)[:14]
        hyp = d.get('hypothesis_count', 0)
        exact = d.get('exact_count', 0)
        disc = domain_dist.get(code, 0)
        h = d.get('health', '?')[:4]
        if disc > 0:
            L(lines, f'  {code} {name:<14} {hyp:>4}H {exact:>4}E +{disc:<3} {h}')
        else:
            L(lines, f'  {code} {name:<14} {hyp:>4}H {exact:>4}E       {h}')
    L(lines, '')

    # Papers
    L(lines, f'📄 자동 논문 ({len(papers)}편)')
    for p in papers[-3:]:
        pid = p.get('paper_id', '?')[-15:]
        cnt = p.get('discovery_count', 0)
        zen = '✅' if p.get('zenodo', {}).get('success') else '⏳'
        osf = '✅' if p.get('osf', {}).get('success') else '⏳'
        L(lines, f'  {pid} | {cnt}건 | Zen:{zen} OSF:{osf}')
    L(lines, '')

    # Bridge
    if bs:
        stage_b = bs.get('stage', '?')
        gp = bs.get('growth_points', 0)
        active = bs.get('active', 0)
        health = bs.get('health', 0)
        L(lines, f'🌉 NEXUS-BRIDGE: {stage_b} | {gp:,} pts | {active} active')
    L(lines, '')

    # Recent discoveries (last 5)
    L(lines, '🔍 최근 발견:')
    for d in all_disc[-5:]:
        content = d.get('content', '')[:50]
        L(lines, f'  {content}')
    L(lines, '')

    lines.append(f'└{"─" * (W + 2)}┘')

    return '\n'.join(lines)


if __name__ == '__main__':
    print(generate_report())
