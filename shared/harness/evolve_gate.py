#!/usr/bin/env python3
# evolve_gate.py — roadmap 자율 진화 엔진
# 모든 nexus roadmap 프로젝트 (millennium / nexus / anima / n6-architecture / hexa-lang / ...) 를
# 주기 감시, deferred=0 + planned=0 + 정직성 조건 충족 시 **자동 vN+1 승격**.
#
# 원칙 (상속 — millennium 정직성 헌장):
#   1. BT/결과 해결 주장 금지 (progress 는 tool/catalog 개선만)
#   2. 외부 의존 명시 (environment / external data / approval)
#   3. MISS 조건 사전
#   4. OUROBOROS 주기 감사
#   5. 진화 이벤트 audit log (evolve_history.jsonl)
#
# 사용:
#   python3 evolve_gate.py                    # 모든 프로젝트 감시 + auto-promote
#   python3 evolve_gate.py --dry-run          # preview only
#   python3 evolve_gate.py --project X        # 단일 프로젝트
#   python3 evolve_gate.py --project X --force # MANDATORY 조건 우회 (위험)

import argparse
import json
import re
import sys
import time
from pathlib import Path
from datetime import datetime

NEXUS_ROOT = Path("/Users/ghost/Dev/nexus")
ROADMAPS = NEXUS_ROOT / "shared/roadmaps"
ATLAS = NEXUS_ROOT / "shared/n6/atlas.n6"
HISTORY = NEXUS_ROOT / "shared/harness/evolve_history.jsonl"

# 프로젝트별 진화 config
# (자동 감지 default + per-project override)
PROJECT_CONFIGS = {
    "millennium": {
        "file": "millennium.json",
        "track_pattern": ["E Empirical", "T Theoretical", "M Meta"],
        "honesty_invariant": "BT 해결 0/6 유지",
        "version_key": "_meta.schema_version",
    },
    "nexus": {
        "file": "nexus.json",
        "track_pattern": ["INFRA", "GROWTH", "META"],
        "honesty_invariant": "infrastructure tool 개선만, 자체 지능 주장 없음",
        "version_key": "_meta.schema_version",
    },
    "anima": {
        "file": "anima.json",
        "track_pattern": ["PHI", "DUAL_TRACK", "CONSCIOUSNESS"],
        "honesty_invariant": "의식 주장 없음, measurement 만",
        "version_key": "_meta.schema_version",
    },
    "n6-architecture": {
        "file": "n6-architecture.json",
        "track_pattern": ["TRACK_SCAN", "TRACK_DSE", "TRACK_META"],
        "honesty_invariant": "n=6 prior, 증명 주장 없음",
        "version_key": "_meta.schema_version",
    },
    "hexa-lang": {
        "file": "hexa-lang.json",
        "track_pattern": ["LANG", "COMPILER", "ECOSYSTEM"],
        "honesty_invariant": "language tool 개선, AGI 주장 없음",
        "version_key": "_meta.schema_version",
    },
}


def get_nested(d: dict, path: str):
    """'_meta.schema_version' 같은 dot path 로 값 추출"""
    cur = d
    for part in path.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return None
    return cur


def set_nested(d: dict, path: str, value):
    parts = path.split(".")
    cur = d
    for p in parts[:-1]:
        if p not in cur or not isinstance(cur[p], dict):
            cur[p] = {}
        cur = cur[p]
    cur[parts[-1]] = value


def get_statistics(roadmap: dict) -> dict:
    """task/phase 통계 추출 — 전 version (top-level + _v*_phases) 합산"""
    stats = roadmap.get("statistics", {})
    total = stats.get("total_tasks", 0) if stats else 0
    done = stats.get("done_tasks", 0) if stats else 0
    partial = stats.get("partial_tasks", 0) if stats else 0
    deferred = stats.get("deferred_tasks", 0) if stats else 0
    planned = stats.get("planned_tasks", 0) if stats else 0

    # top-level phases (statistics 없을 때) counting
    if total == 0:
        for p in roadmap.get("phases", []):
            if isinstance(p, dict):
                for par in p.get("parallel", [{}]):
                    if isinstance(par, dict):
                        for t in par.get("tasks", []):
                            total += 1
                            st = t.get("status", "planned")
                            if st == "done": done += 1
                            elif st == "partial": partial += 1
                            elif st == "deferred": deferred += 1
                            else: planned += 1

    # _v*_phases (자율 진화 후 버전별 phase 블록) 전수 집계
    for key, val in roadmap.items():
        m = re.match(r"_v(\d+)_phases$", key)
        if m and isinstance(val, dict):
            for phase_id, phase in val.items():
                if isinstance(phase, dict):
                    for t in phase.get("tasks", []):
                        total += 1
                        st = t.get("status", "planned")
                        if st == "done":
                            done += 1
                        elif st == "partial":
                            partial += 1
                        elif st == "deferred":
                            deferred += 1
                        else:
                            planned += 1

    return dict(total=total, done=done, partial=partial, deferred=deferred, planned=planned)


def parse_version(v: str) -> tuple:
    """'2.3' -> (2, 3), '3.0' -> (3, 0)"""
    try:
        parts = v.split(".")
        return (int(parts[0]), int(parts[1]) if len(parts) > 1 else 0)
    except (ValueError, AttributeError):
        return (1, 0)


def next_major(v: str) -> str:
    maj, _ = parse_version(v)
    return f"{maj + 1}.0"


def check_saturation(stats: dict) -> tuple:
    """(saturation_ok, reason) — deferred + planned == 0 이면 saturation"""
    if stats["total"] == 0:
        return False, "no tasks defined (skip)"
    if stats["deferred"] > 0:
        return False, f"{stats['deferred']} deferred 미해결"
    if stats["planned"] > 0:
        return False, f"{stats['planned']} planned 미시작"
    return True, f"saturation {stats['done']}/{stats['total']} done (+{stats['partial']} partial)"


def check_atlas_r14_clean() -> tuple:
    """OUROBOROS 간이 check — v2 report 있으면 읽기"""
    report = NEXUS_ROOT.parent / "n6-architecture/reports/ouroboros_v2_report.json"
    if not report.exists():
        return None, "ouroboros report 없음 (skip check)"
    try:
        d = json.loads(report.read_text())
        critical = d.get("severity_distribution", {}).get("CRITICAL", 0)
        if critical == 0:
            return True, f"R14 CLEAN ({d.get('total_cycles', 0)} cycles, 0 CRITICAL)"
        return False, f"R14 VIOLATION ({critical} CRITICAL cycles)"
    except Exception as e:
        return None, f"report parse error: {e}"


def check_honesty_preserved(roadmap: dict, project: str) -> tuple:
    """정직성 invariant 체크 — 프로젝트 config 기반"""
    cfg = PROJECT_CONFIGS.get(project, {})
    invariant = cfg.get("honesty_invariant", "")
    # 간이 체크: _meta.description 또는 _v*_meta 에 honesty charter 언급 있는지
    meta = roadmap.get("_meta", {})
    desc = meta.get("description", "")
    if "정직" in desc or "honest" in desc.lower() or "0/6" in desc:
        return True, f"정직성 invariant present: {invariant}"
    return None, "정직성 invariant 확인 불가 (수동 review)"


def design_next_version(roadmap: dict, project: str, current_version: str, next_version: str, stats: dict) -> dict:
    """다음 버전 meta + phase 블록 설계"""
    cfg = PROJECT_CONFIGS.get(project, {})
    tracks = cfg.get("track_pattern", ["TRACK_A", "TRACK_B", "TRACK_C"])
    now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    new_meta_key = f"_v{next_version.split('.')[0]}_meta"
    new_phases_key = f"_v{next_version.split('.')[0]}_phases"

    new_meta = {
        "schema_version": next_version,
        "auto_promoted": True,
        "promoted_at": now,
        "parent_version": current_version,
        "parent_completion": {
            "total": stats["total"],
            "done": stats["done"],
            "partial": stats["partial"],
            "deferred": stats["deferred"],
            "planned": stats["planned"],
        },
        "honesty_charter": [
            "BT 해결 주장 금지",
            "외부 의존 명시",
            "MISS 조건 사전",
            "OUROBOROS 주기 감사",
            f"project invariant: {cfg.get('honesty_invariant', 'N/A')}",
        ],
        "tracks": tracks,
        "promotion_source": "shared/harness/evolve_gate.py (자율 진화 엔진)",
    }

    # 각 track 에 placeholder phase 생성
    new_phases = {}
    for i, track in enumerate(tracks, 1):
        phase_id = f"P{i}_v{next_version.split('.')[0]}"
        new_phases[phase_id] = {
            "id": phase_id,
            "name": f"v{next_version} {track} Track",
            "track": track,
            "status": "auto_planned",
            "tasks": [{
                "id": f"{phase_id}-T1-seed",
                "task": f"{track} track seed task — 이전 버전 발견 사항 분석 및 후속 작업 식별",
                "cost": "M",
                "status": "planned",
                "created_by": "evolve_gate auto-generation",
            }],
        }

    return {
        "meta_key": new_meta_key,
        "meta_value": new_meta,
        "phases_key": new_phases_key,
        "phases_value": new_phases,
    }


def evolve_project(project: str, dry_run: bool = False, force: bool = False) -> dict:
    """단일 프로젝트 진화 시도. 반환: event log entry"""
    cfg = PROJECT_CONFIGS.get(project)
    if not cfg:
        return {"project": project, "status": "SKIP", "reason": "config 없음"}

    roadmap_path = ROADMAPS / cfg["file"]
    if not roadmap_path.exists():
        return {"project": project, "status": "SKIP", "reason": "roadmap 없음"}

    roadmap = json.loads(roadmap_path.read_text(encoding="utf-8"))

    # 현재 schema version 추출
    current_version = get_nested(roadmap, cfg["version_key"]) or "1.0"
    # 최신 _v*_meta 블록 확인 (이미 승격되어 있는지)
    latest_vmeta_key = None
    for k in roadmap.keys():
        m = re.match(r"_v(\d+)_meta$", k)
        if m:
            maj = int(m.group(1))
            cur_maj, _ = parse_version(current_version)
            if maj > cur_maj:
                current_version = get_nested(roadmap.get(k, {}), "schema_version") or f"{maj}.0"
                latest_vmeta_key = k

    # saturation check
    stats = get_statistics(roadmap)
    sat_ok, sat_reason = check_saturation(stats)
    r14_ok, r14_reason = check_atlas_r14_clean()
    hon_ok, hon_reason = check_honesty_preserved(roadmap, project)

    event = {
        "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "project": project,
        "current_version": current_version,
        "statistics": stats,
        "checks": {
            "saturation": {"pass": sat_ok, "reason": sat_reason},
            "ouroboros_r14": {"pass": r14_ok, "reason": r14_reason},
            "honesty": {"pass": hon_ok, "reason": hon_reason},
        },
    }

    # 모든 체크 통과 시 (또는 force) 승격
    critical_checks = [sat_ok, hon_ok]  # r14 는 optional
    if force or all(c is True for c in critical_checks):
        next_version = next_major(current_version)
        event["decision"] = "PROMOTE"
        event["next_version"] = next_version

        if dry_run:
            event["status"] = "DRY_RUN_PREVIEW"
            event["preview"] = design_next_version(roadmap, project, current_version, next_version, stats)
        else:
            # 실제 승격
            design = design_next_version(roadmap, project, current_version, next_version, stats)
            roadmap[design["meta_key"]] = design["meta_value"]
            roadmap[design["phases_key"]] = design["phases_value"]
            # 최상위 schema_version 유지 (backward compat), _v*_meta 가 최신
            roadmap_path.write_text(json.dumps(roadmap, indent=2, ensure_ascii=False), encoding="utf-8")
            event["status"] = "PROMOTED"
            event["new_blocks"] = [design["meta_key"], design["phases_key"]]
    else:
        event["decision"] = "HOLD"
        event["status"] = "SATURATION_NOT_REACHED"

    return event


def append_history(event: dict):
    HISTORY.parent.mkdir(parents=True, exist_ok=True)
    with HISTORY.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", help="단일 프로젝트 (생략 시 전체)")
    ap.add_argument("--dry-run", action="store_true", help="preview only")
    ap.add_argument("--force", action="store_true", help="MANDATORY check 우회 (위험)")
    args = ap.parse_args()

    projects = [args.project] if args.project else list(PROJECT_CONFIGS.keys())

    print(f"[evolve_gate] {len(projects)} 프로젝트 감시 " +
          ("(dry-run)" if args.dry_run else "") +
          ("(FORCE)" if args.force else ""))

    results = []
    for p in projects:
        ev = evolve_project(p, dry_run=args.dry_run, force=args.force)
        results.append(ev)

        status = ev.get("status", "?")
        decision = ev.get("decision", "?")
        stats = ev.get("statistics", {})
        cur_v = ev.get("current_version", "?")
        next_v = ev.get("next_version", "-")

        symbol = {"PROMOTED": "🚀", "DRY_RUN_PREVIEW": "🔍",
                  "SATURATION_NOT_REACHED": "⏸", "SKIP": "⏭"}.get(status, "?")
        print(f"  {symbol} {p}: v{cur_v} → v{next_v} | {decision} | {status}")
        print(f"      done={stats.get('done',0)}/{stats.get('total',0)} | "
              f"deferred={stats.get('deferred',0)} | planned={stats.get('planned',0)}")
        for check_name, check_data in ev.get("checks", {}).items():
            p_sym = {True: "✓", False: "✗", None: "?"}[check_data.get("pass")]
            print(f"      {p_sym} {check_name}: {check_data.get('reason', '')}")

        if not args.dry_run:
            append_history(ev)

    # 요약
    print()
    print("=" * 70)
    n_promoted = sum(1 for r in results if r.get("status") == "PROMOTED")
    n_hold = sum(1 for r in results if r.get("status") == "SATURATION_NOT_REACHED")
    n_skip = sum(1 for r in results if r.get("status") == "SKIP")
    n_preview = sum(1 for r in results if r.get("status") == "DRY_RUN_PREVIEW")
    print(f"승격 (PROMOTED):        {n_promoted}")
    print(f"보류 (HOLD):            {n_hold}")
    print(f"건너뜀 (SKIP):          {n_skip}")
    print(f"미리보기 (DRY_RUN):     {n_preview}")

    sys.exit(0)


if __name__ == "__main__":
    main()
