#!/usr/bin/env python3
# discovery_graph_append.py — ROI #6 증분 append 유틸
# 목적: shared/discovery/discovery_graph.json 에 신규 노드/엣지만 diff-only append
# 포맷: NDJSON (1줄 = 1 {"type":"node"|"edge", ...})
# 커서: discovery_graph.json.stream_cursor (offset/mtime/size 추적)
#
# 사용:
#   python3 discovery_graph_append.py --add input.ndjson
#   python3 discovery_graph_append.py --add-stdin < new_records.ndjson
#   python3 discovery_graph_append.py --status
#
# 멱등 보장: 이미 존재하는 id (노드) / (from,to,edge_type) 조합 (엣지) 스킵
# I/O 절감: 전체 재직렬화 없음 — seek(END) + append-only

import json
import sys
import os
import time
import argparse
from pathlib import Path

GRAPH = Path('/Users/ghost/Dev/nexus/shared/discovery/discovery_graph.json')
CURSOR = Path('/Users/ghost/Dev/nexus/shared/discovery/discovery_graph.json.stream_cursor')
INDEX = Path('/Users/ghost/Dev/nexus/shared/discovery/discovery_graph.index.json')


def load_index() -> dict:
    """노드 id + 엣지 key 집합 로드. 인덱스 없으면 스캔하여 생성."""
    if INDEX.exists() and INDEX.stat().st_mtime >= GRAPH.stat().st_mtime:
        return json.loads(INDEX.read_text())
    idx = {'nodes': [], 'edges': []}
    node_set = set()
    edge_set = set()
    with GRAPH.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            if rec.get('type') == 'node':
                nid = rec.get('id')
                if nid:
                    node_set.add(nid)
            elif rec.get('type') == 'edge':
                ek = f"{rec.get('from','')}|{rec.get('to','')}|{rec.get('edge_type','')}"
                edge_set.add(ek)
    idx['nodes'] = sorted(node_set)
    idx['edges'] = sorted(edge_set)
    idx['generated_at'] = int(time.time())
    idx['graph_size'] = GRAPH.stat().st_size
    INDEX.write_text(json.dumps(idx, ensure_ascii=False))
    return idx


def save_index(idx: dict):
    idx['generated_at'] = int(time.time())
    idx['graph_size'] = GRAPH.stat().st_size
    INDEX.write_text(json.dumps(idx, ensure_ascii=False))


def save_cursor():
    st = GRAPH.stat()
    CURSOR.write_text(json.dumps({
        'offset': st.st_size,
        'mtime': st.st_mtime,
        'size': st.st_size,
        'updated_at': time.time(),
    }))


def append_records(records: list) -> dict:
    """diff-only append. 신규만 추가."""
    idx = load_index()
    node_set = set(idx['nodes'])
    edge_set = set(idx['edges'])

    new_nodes = 0
    new_edges = 0
    skipped = 0
    bytes_written = 0

    # append 모드 — 재직렬화 없음
    with GRAPH.open('a') as f:
        # 파일 끝에 개행 보장
        if GRAPH.stat().st_size > 0:
            with GRAPH.open('rb') as rf:
                rf.seek(-1, os.SEEK_END)
                last = rf.read(1)
            if last != b'\n':
                f.write('\n')

        for rec in records:
            t = rec.get('type')
            if t == 'node':
                nid = rec.get('id')
                if not nid or nid in node_set:
                    skipped += 1
                    continue
                node_set.add(nid)
                line = json.dumps(rec, ensure_ascii=False, separators=(',', ':')) + '\n'
                f.write(line)
                bytes_written += len(line.encode())
                new_nodes += 1
            elif t == 'edge':
                ek = f"{rec.get('from','')}|{rec.get('to','')}|{rec.get('edge_type','')}"
                if ek in edge_set:
                    skipped += 1
                    continue
                edge_set.add(ek)
                line = json.dumps(rec, ensure_ascii=False, separators=(',', ':')) + '\n'
                f.write(line)
                bytes_written += len(line.encode())
                new_edges += 1
            else:
                skipped += 1

    idx['nodes'] = sorted(node_set)
    idx['edges'] = sorted(edge_set)
    save_index(idx)
    save_cursor()

    return {
        'new_nodes': new_nodes,
        'new_edges': new_edges,
        'skipped': skipped,
        'bytes_written': bytes_written,
        'bytes_saved_vs_rewrite': GRAPH.stat().st_size - bytes_written,
    }


def status():
    idx = load_index()
    st = GRAPH.stat()
    print(f'graph: {GRAPH}')
    print(f'  size: {st.st_size/1024:.1f}KB ({st.st_size} bytes)')
    print(f'  mtime: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(st.st_mtime))}')
    print(f'  nodes: {len(idx["nodes"])}')
    print(f'  edges: {len(idx["edges"])}')
    if CURSOR.exists():
        c = json.loads(CURSOR.read_text())
        print(f'cursor: offset={c["offset"]} size={c["size"]}')
    if INDEX.exists():
        print(f'index: {INDEX.stat().st_size/1024:.1f}KB')


def main():
    ap = argparse.ArgumentParser(description='discovery_graph.json 증분 append (ROI #6)')
    ap.add_argument('--add', type=str, help='NDJSON 입력 파일')
    ap.add_argument('--add-stdin', action='store_true', help='stdin NDJSON 입력')
    ap.add_argument('--status', action='store_true', help='현재 상태')
    args = ap.parse_args()

    if args.status:
        status()
        return

    records = []
    if args.add:
        p = Path(args.add)
        for line in p.read_text().splitlines():
            line = line.strip()
            if line:
                records.append(json.loads(line))
    elif args.add_stdin:
        for line in sys.stdin:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    else:
        ap.print_help()
        return

    if not records:
        print('입력 레코드 없음')
        return

    result = append_records(records)
    print(f'신규 노드: {result["new_nodes"]}')
    print(f'신규 엣지: {result["new_edges"]}')
    print(f'중복 스킵: {result["skipped"]}')
    print(f'기록 바이트: {result["bytes_written"]}')
    print(f'전체재기록 대비 절감: {result["bytes_saved_vs_rewrite"]} bytes')


if __name__ == '__main__':
    main()
