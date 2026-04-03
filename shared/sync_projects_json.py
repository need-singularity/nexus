#!/usr/bin/env python3
"""
sync_projects_json.py — 실제 JSON 원본 → projects.json + projects.md 자동 갱신

루프 렌즈: 실제 데이터에서 통계를 읽어 projects.json의 stats를 업데이트하고,
projects.md의 하드코딩된 숫자도 자동 반영.

사용법:
  python3 .shared/sync_projects_json.py           # dry-run
  python3 .shared/sync_projects_json.py --apply   # 실제 적용
"""

import json
import re
import sys
import glob
import subprocess
import argparse
from pathlib import Path

SHARED_DIR = Path(__file__).resolve().parent
BASE = SHARED_DIR.parent          # ~/Dev/TECS-L
PARENT = BASE.parent              # ~/Dev/
PROJECTS_JSON = BASE / "shared" / "projects.json"
PROJECTS_MD = SHARED_DIR / "projects.md"


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def count_md(directory):
    return len(glob.glob(str(directory / "**" / "*.md"), recursive=True))


def count_glob(pattern):
    return len(glob.glob(pattern, recursive=True))


def grep_count(pattern, directory):
    """파일 내 패턴 매칭 수 (테스트 카운트 등)"""
    try:
        r = subprocess.run(["grep", "-r", pattern, str(directory)],
                           capture_output=True, text=True)
        if r.returncode == 0:
            return len(r.stdout.strip().split("\n"))
    except Exception:
        pass
    return 0


# ═══════════════════════════════════════════════════════════════
# Stat collectors — 각 프로젝트의 실제 JSON에서 통계 수집
# ═══════════════════════════════════════════════════════════════

def collect_tecs_l():
    n_hypo = count_md(BASE / "docs" / "hypotheses")
    n_tools = count_glob(str(BASE / "*.py")) + count_glob(str(BASE / "math" / "*.py"))
    return {
        "characterizations": 150,  # 수동 유지 (구조적 카운트 불가)
        "major_discoveries": 8,    # 수동 유지
        "tools": n_tools,
        "hypotheses": n_hypo,
    }


def collect_anima():
    laws = load_json(PARENT / "anima" / "anima" / "config" / "consciousness_laws.json")
    meta = laws.get("_meta", {})
    return {
        "laws": meta.get("total_laws", 0),
        "meta_laws": meta.get("total_meta", 0),
        "topo_laws": meta.get("total_topo", 0),
        "hexad_modules": 6,
    }


def collect_sedi():
    grades = load_json(PARENT / "sedi" / "data" / "sedi-grades.json")
    return {
        "hypotheses": grades.get("total_hypotheses", 0),
        "data_sources": 77,  # 수동 유지 (데이터 소스는 코드에 분산)
    }


def collect_n6():
    # DSE 도메인 수: dse-map.toml 파싱 또는 projects.json 유지
    dse_toml = PARENT / "n6-architecture" / "docs" / "dse-map.toml"
    dse_domains = 0
    if dse_toml.exists():
        text = dse_toml.read_text()
        dse_domains = text.count("[[domain]]")
    # NEXUS-6 테스트 수
    nexus6_src = PARENT / "n6-architecture" / "tools" / "nexus6" / "src"
    n_tests = grep_count("#\\[test\\]", nexus6_src) if nexus6_src.exists() else 0
    return {
        "ai_techniques": 16,  # 고정 상수 (n=6 기반)
        "dse_domains": dse_domains or 323,
        "nexus6_tests": n_tests,
    }


def collect_brainwire():
    return {
        "modalities": 12,  # 하드웨어 상수
    }


def collect_hexa():
    # lexer.rs에서 키워드 수 카운트
    lexer = PARENT / "hexa-lang" / "src" / "lexer.rs"
    kw = 53  # fallback
    if lexer.exists():
        text = lexer.read_text()
        kw_matches = re.findall(r'"[a-z_]+"\s*=>\s*Token', text)
        if kw_matches:
            kw = len(kw_matches)
    return {
        "keywords": kw or 53,
        "operators": 24,    # n=6 기반 고정
        "primitives": 8,    # σ-τ 기반 고정
        "dse_combos": 21952,  # 고정 (n6 계산)
    }


COLLECTORS = {
    "tecs-l": collect_tecs_l,
    "anima": collect_anima,
    "sedi": collect_sedi,
    "n6-architecture": collect_n6,
    "brainwire": collect_brainwire,
    "hexa-lang": collect_hexa,
}


# ═══════════════════════════════════════════════════════════════
# projects.md 자동 갱신 — 하드코딩된 숫자를 실제 값으로 교체
# ═══════════════════════════════════════════════════════════════

def update_projects_md(stats_by_id):
    """projects.md 내 숫자를 실제 값으로 교체"""
    if not PROJECTS_MD.exists():
        return False

    text = PROJECTS_MD.read_text(encoding="utf-8")
    original = text

    # anima: "179 laws" → "1030 laws"
    anima = stats_by_id.get("anima", {})
    if anima.get("laws"):
        text = re.sub(r'\d+ laws', f'{anima["laws"]} laws', text)
    if anima.get("meta_laws"):
        text = re.sub(r'\d+ Meta Laws', f'{anima["meta_laws"]} Meta Laws', text)

    # tecs-l: "150 characterizations + 8 Major Discoveries + 44 tools"
    tecs = stats_by_id.get("tecs-l", {})
    if tecs.get("tools"):
        text = re.sub(r'\d+ tools', f'{tecs["tools"]} tools', text)

    # sedi: "678 hypotheses"
    sedi = stats_by_id.get("sedi", {})
    if sedi.get("hypotheses"):
        text = re.sub(r'(\d+) hypotheses', f'{sedi["hypotheses"]} hypotheses', text)

    # n6: "112 tests"
    n6 = stats_by_id.get("n6-architecture", {})
    if n6.get("nexus6_tests"):
        text = re.sub(r'(\d+) tests', f'{n6["nexus6_tests"]} tests', text)

    # n6: "323 DSE domains" (embedded in description)
    n6 = stats_by_id.get("n6-architecture", {})
    # dse_domains is not directly mentioned as "N domains" in projects.md

    # hexa: "53 keywords", "24 operators", "21,952 combos"
    hexa = stats_by_id.get("hexa-lang", {})
    if hexa.get("keywords"):
        text = re.sub(r'\d+ keywords', f'{hexa["keywords"]} keywords', text)
    if hexa.get("dse_combos"):
        text = re.sub(r'[\d,]+ combos', f'{hexa["dse_combos"]:,} combos', text)

    # papers: "79 papers" + per-project counts
    # zenodo manifest 기반
    manifest = load_json(BASE / "zenodo" / "manifest.json")
    papers = manifest.get("papers", {})
    if papers:
        total = sum(len(v) for v in papers.values())
        text = re.sub(r'(\d+) papers\)', f'{total} papers)', text)
        # per-project: "TECS-L+N6 (31) + anima (25) + SEDI (23)"
        tl = len(papers.get("tecs-l", []))
        an = len(papers.get("anima", []))
        se = len(papers.get("sedi", []))
        text = re.sub(
            r'TECS-L\+N6 \(\d+\) \+ anima \(\d+\) \+ SEDI \(\d+\)',
            f'TECS-L+N6 ({tl}) + anima ({an}) + SEDI ({se})',
            text
        )

    changed = text != original
    if changed:
        PROJECTS_MD.write_text(text, encoding="utf-8")
    return changed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    # 1. projects.json 로드
    projects = load_json(PROJECTS_JSON)
    if not projects:
        print("Error: projects.json not found")
        sys.exit(1)

    # 2. 실제 통계 수집
    stats_by_id = {}
    any_changed = False

    for proj in projects.get("projects", []):
        pid = proj["id"]
        collector = COLLECTORS.get(pid)
        if not collector:
            continue

        new_stats = collector()
        old_stats = proj.get("stats", {})
        stats_by_id[pid] = new_stats

        # 변경 확인
        diffs = []
        for k, v in new_stats.items():
            old = old_stats.get(k)
            if old != v:
                diffs.append(f"{k}: {old} → {v}")

        if diffs:
            any_changed = True
            print(f"  [{pid}] {', '.join(diffs)}")
            if args.apply:
                proj["stats"] = new_stats
        else:
            print(f"  [{pid}] OK")

    # 3. projects.json 저장
    if args.apply and any_changed:
        with open(PROJECTS_JSON, "w", encoding="utf-8") as f:
            json.dump(projects, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"\n  ✅ projects.json 업데이트")

    # 4. projects.md 업데이트
    if args.apply:
        md_changed = update_projects_md(stats_by_id)
        if md_changed:
            print(f"  ✅ projects.md 업데이트")
        else:
            print(f"  ── projects.md 변경 없음")

    if not args.apply and any_changed:
        print(f"\n  ℹ️  dry-run — `--apply`로 적용")


if __name__ == "__main__":
    main()
