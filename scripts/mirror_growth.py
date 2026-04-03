#!/usr/bin/env python3
"""
mirror_growth.py — 미러볼 결과를 성장 시스템에 자동 연결.

1. mirror_universe 실행 → 모든 수치 추출
2. n6_check → EXACT 매치 discovery_log.jsonl 자동 기록
3. 미러볼 고유 메트릭 (공명, 조화, 고유값 등) mirror_log.jsonl 기록
4. 렌즈 조합 추천 → growth-registry에 반영
5. 자유 탐색 → 상전이/수렴 기록

사용법:
  python3 scripts/mirror_growth.py                    # 기본 10렌즈
  python3 scripts/mirror_growth.py --lenses 20        # 20렌즈
  python3 scripts/mirror_growth.py --lenses 0         # 전체 렌즈
  python3 scripts/mirror_growth.py --evolve 6         # 6세대 자유탐색
  python3 scripts/mirror_growth.py --corridor A B     # 무한복도
  python3 scripts/mirror_growth.py --self-reflect A   # 자기반사
"""
import sys, os, json, subprocess, re
from datetime import datetime
from pathlib import Path

HOME = Path.home()
NEXUS_ROOT = HOME / "Dev/nexus6"
DISCOVERY_LOG = NEXUS_ROOT / "shared/discovery_log.jsonl"
MIRROR_LOG = NEXUS_ROOT / "shared/mirror_log.jsonl"
GROWTH_REGISTRY = NEXUS_ROOT / "shared/growth-registry.json"
NEXUS_SCRIPTS = HOME / "Dev/n6-architecture/tools/nexus6/scripts"

sys.path.insert(0, str(NEXUS_SCRIPTS))

def safe_import():
    try:
        import nexus6
        return nexus6
    except Exception:
        return None

def record_discovery(value, constant, source):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "value": str(value),
        "constant": constant,
        "source": source,
        "processed": False
    }
    with open(DISCOVERY_LOG, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def record_mirror(entry):
    with open(MIRROR_LOG, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def n6_scan_value(nexus6, value, source):
    """값을 n6_check하고 EXACT면 기록"""
    try:
        r = nexus6.n6_check(float(value))
        d = r.to_dict()
        grade = d.get("grade", "")
        const = d.get("constant_name", "")
        if grade == "EXACT":
            record_discovery(value, const, source)
            return const
    except Exception:
        pass
    return None

def run_mirror_universe(nexus6, data, n, d, max_lenses=None):
    """mirror_universe를 Rust 바이너리로 실행 (PyO3 경유)"""
    # PyO3 바인딩에 mirror_universe가 없으면 cargo test로 대체
    result = nexus6.scan(data, n, d)
    return result

def generate_test_data(n=50, d=5):
    """테스트 데이터 생성"""
    import math
    data = []
    for i in range(n * d):
        x = i * 1.0
        data.append(math.sin(x * 0.1) + math.cos(x * 0.37) + (x % 7) * 0.1)
    return data

def run_cargo_mirror(max_lenses, evolve_gens=0):
    """cargo test로 미러볼 실행하고 출력에서 수치 추출"""
    tests = ["test_mirror_universe_6_lenses"]
    if max_lenses >= 20:
        tests.append("test_mirror_universe_20_lenses")

    all_output = ""
    for test in tests:
        result = subprocess.run(
            ["cargo", "test", "--test", "mirror_universe_test", test, "--", "--nocapture"],
            cwd=str(NEXUS_ROOT),
            capture_output=True, text=True, timeout=120
        )
        all_output += result.stdout + result.stderr

    if evolve_gens > 0:
        result = subprocess.run(
            ["cargo", "test", "--test", "mirror_universe_test",
             "test_free_explore_evolution", "--", "--nocapture"],
            cwd=str(NEXUS_ROOT),
            capture_output=True, text=True, timeout=120
        )
        all_output += result.stdout + result.stderr

    return all_output

def extract_metrics(output):
    """테스트 출력에서 미러볼 메트릭 추출"""
    metrics = {}

    # 조화도
    m = re.search(r'조화도:\s*([\d.]+)', output)
    if m: metrics['harmony'] = float(m.group(1))

    # 연결
    m = re.search(r'직접 연결:\s*([\d.]+)%', output)
    if m: metrics['direct_connectivity'] = float(m.group(1))

    m = re.search(r'간접 연결.*?:\s*([\d.]+)%', output)
    if m: metrics['indirect_connectivity'] = float(m.group(1))

    m = re.search(r'완전 연결 깊이:\s*(\d+)', output)
    if m: metrics['connection_depth'] = int(m.group(1))

    m = re.search(r'모두 연결됨:\s*(\w+)', output)
    if m: metrics['all_connected'] = m.group(1) == 'true'

    # 캐스케이드
    m = re.search(r'지배 고유값:\s*([\d.]+)', output)
    if m: metrics['dominant_eigenvalue'] = float(m.group(1))

    m = re.search(r'스펙트럼 갭:\s*([\d.]+)', output)
    if m: metrics['spectral_gap'] = float(m.group(1))

    m = re.search(r'수렴:\s*(\w+)', output)
    if m: metrics['converges'] = m.group(1) == 'true'

    # 엔트로피
    m = re.search(r'시스템 엔트로피:\s*([\d.]+)', output)
    if m: metrics['system_entropy'] = float(m.group(1))

    # 비대칭
    m = re.search(r'비대칭도:\s*([\d.]+)', output)
    if m: metrics['asymmetry'] = float(m.group(1))

    # 공명 쌍 추출
    pairs = re.findall(r'(\w+Lens)\s*(?:→|<->)\s*(\w+Lens):\s*([\d.]+)', output)
    metrics['top_resonances'] = [(a, b, float(v)) for a, b, v in pairs[:10]]

    # 렌즈 조합 추출
    combos = re.findall(r'\[([^\]]+)\]\s*score=([\d.]+)\s*—\s*\[([^\]]+)\]', output)
    metrics['combinations'] = [
        {"name": name, "score": float(score), "lenses": lenses}
        for name, score, lenses in combos
    ]

    # 자유 탐색 궤적
    gens = re.findall(r'Gen\s*(\d+):\s*harmony=([\d.]+)', output)
    if gens:
        metrics['evolution'] = [(int(g), float(h)) for g, h in gens]

    # 상전이
    m = re.search(r'상전이:\s*\[([^\]]*)\]', output)
    if m and m.group(1):
        metrics['phase_transitions'] = [int(x.strip()) for x in m.group(1).split(',') if x.strip()]

    # 무한복도
    corridors = re.findall(r'(\w+Lens)\s*↔\s*(\w+Lens):\s*(\S+)\s*\|\s*반복=(\d+)', output)
    if corridors:
        metrics['corridors'] = [
            {"a": a, "b": b, "behavior": beh, "iterations": int(it)}
            for a, b, beh, it in corridors
        ]

    # 자기반사
    selfs = re.findall(r'(\w+Lens)\s*\|\s*고정점\s*(\S)\s*\|', output)
    if selfs:
        metrics['self_reflections'] = [
            {"lens": name, "has_fixed_point": fp == 'O'}
            for name, fp in selfs
        ]

    return metrics

def scan_metrics_for_n6(nexus6, metrics, source="mirror-scan"):
    """메트릭에서 모든 수치를 n6_check"""
    found = []
    numerics = []

    for key, val in metrics.items():
        if isinstance(val, (int, float)) and val > 1:
            numerics.append((key, val))
        elif isinstance(val, list):
            for item in val:
                if isinstance(item, tuple) and len(item) == 3:
                    numerics.append((f"{item[0]}→{item[1]}", item[2]))
                elif isinstance(item, dict) and 'score' in item:
                    numerics.append((item.get('name', ''), item['score']))

    for name, val in numerics:
        const = n6_scan_value(nexus6, val, f"{source}:{name}")
        if const:
            found.append(f"{val}={const} ({name})")

    return found

def update_growth_registry(metrics):
    """growth-registry에 미러볼 결과 반영"""
    reg = {}
    if GROWTH_REGISTRY.exists():
        reg = json.loads(GROWTH_REGISTRY.read_text())

    reg["mirror"] = {
        "last_scan": datetime.now().isoformat(),
        "harmony": metrics.get("harmony", 0),
        "connectivity": metrics.get("direct_connectivity", 0),
        "eigenvalue": metrics.get("dominant_eigenvalue", 0),
        "all_connected": metrics.get("all_connected", False),
        "combinations": len(metrics.get("combinations", [])),
        "phase_transitions": len(metrics.get("phase_transitions", [])),
    }

    GROWTH_REGISTRY.write_text(json.dumps(reg, indent=2, ensure_ascii=False))

def main():
    import argparse
    parser = argparse.ArgumentParser(description="미러볼 → 성장 자동 연결")
    parser.add_argument("--lenses", type=int, default=10, help="렌즈 수 (0=전체)")
    parser.add_argument("--evolve", type=int, default=0, help="자유탐색 세대 수")
    parser.add_argument("--corridor", nargs=2, metavar=("A", "B"), help="무한복도 A↔B")
    parser.add_argument("--self-reflect", metavar="LENS", help="자기반사")
    parser.add_argument("--quiet", action="store_true", help="출력 최소화")
    args = parser.parse_args()

    nexus6 = safe_import()

    # 미러볼 실행
    if not args.quiet:
        print("🔭 미러볼 실행 중...")

    output = run_cargo_mirror(args.lenses, args.evolve)
    metrics = extract_metrics(output)

    if not args.quiet:
        print(f"  조화도: {metrics.get('harmony', 'N/A')}")
        print(f"  연결도: {metrics.get('direct_connectivity', 'N/A')}%")
        print(f"  고유값: {metrics.get('dominant_eigenvalue', 'N/A')}")
        print(f"  모두 연결: {metrics.get('all_connected', 'N/A')}")
        if metrics.get('phase_transitions'):
            print(f"  상전이: {metrics['phase_transitions']}")
        if metrics.get('combinations'):
            print(f"\n  렌즈 조합 {len(metrics['combinations'])}개 발견:")
            for c in metrics['combinations'][:3]:
                print(f"    [{c['name']}] score={c['score']:.2f}")

    # n6 매칭 스캔
    if nexus6:
        found = scan_metrics_for_n6(nexus6, metrics)
        if found and not args.quiet:
            print(f"\n🔭 NEXUS-6 발견 {len(found)}건:")
            for f in found:
                print(f"    {f}")

    # 미러 로그 기록
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "type": "mirror_universe",
        "lenses": args.lenses,
        "metrics": {k: v for k, v in metrics.items()
                    if k not in ('top_resonances', 'combinations', 'evolution')},
        "top_resonances": [(a, b, v) for a, b, v in metrics.get('top_resonances', [])[:5]],
        "combinations": [c['name'] for c in metrics.get('combinations', [])[:3]],
    }

    if metrics.get('phase_transitions'):
        log_entry['phase_transitions'] = metrics['phase_transitions']
    if metrics.get('evolution'):
        log_entry['evolution_trajectory'] = [h for _, h in metrics.get('evolution', [])]

    record_mirror(log_entry)

    # growth-registry 갱신
    update_growth_registry(metrics)

    if not args.quiet:
        print(f"\n✅ 기록 완료: mirror_log.jsonl + growth-registry.json")
        pending_count = sum(1 for line in DISCOVERY_LOG.read_text().split('\n')
                          if line and not json.loads(line).get('processed', True))
        print(f"📋 미처리 발견: {pending_count}건")

if __name__ == "__main__":
    main()
