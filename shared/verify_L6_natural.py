#!/usr/bin/env python3
"""reality_map.json v8.5 검증 스크립트"""
import json, sys

with open('/Users/ghost/Dev/nexus/shared/reality_map.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

nodes_with_id = [n for n in data['nodes'] if isinstance(n, dict) and 'id' in n]
print(f"=== reality_map.json 검증 ===")
print(f"버전: {data.get('version')} / meta: {data['_meta'].get('version')}")
print(f"총 노드 수: {len(nodes_with_id)}")

new_levels = [
    'L6_biology','L6_chemistry','L6_thermodynamics','L6_astronomy',
    'L6_botany','L6_zoology','L6_ecology','L6_paleontology',
    'L6_mineralogy','L6_glaciology','L6_volcanology','L6_seismology',
    'L6_hydrology','L6_atmospheric_physics'
]

print("\n도메인별 노드 수:")
total_new = 0
for lv in new_levels:
    cnt = sum(1 for n in nodes_with_id if n.get('level') == lv)
    status = "OK" if cnt >= 5 else "WARN"
    print(f"  [{status}] {lv}: {cnt}")
    total_new += cnt

print(f"\n신규 도메인 합계: {total_new}")

# grade 분포
grade_dist = {}
for n in nodes_with_id:
    if n.get('level', '') in new_levels:
        g = n.get('grade', 'UNKNOWN')
        grade_dist[g] = grade_dist.get(g, 0) + 1

print("\nGrade 분포 (신규 도메인):")
for g, cnt in sorted(grade_dist.items()):
    print(f"  {g}: {cnt}")

# orphan 체크 (id 중복 확인)
ids = [n['id'] for n in nodes_with_id]
dupes = [id for id in ids if ids.count(id) > 1]
if dupes:
    print(f"\n경고: 중복 id 발견: {set(dupes)}")
else:
    print("\nid 중복 없음 (OK)")

# 레벨 등록 확인
print("\n레벨 등록 확인:")
for lv in new_levels:
    status = "OK" if lv in data['_meta']['levels'] else "MISSING"
    print(f"  [{status}] {lv}")

# grade_stats
print(f"\n전체 grade_stats: {data['_meta']['grade_stats']}")
print(f"origin_stats: {data['_meta']['origin_stats']}")
print(f"\nchangelog 마지막: {data['_meta']['changelog'][-1]}")
