#!/usr/bin/env python3
"""
project_lens.py — 프로젝트 인프라 망원경 (3 렌즈)

  🔁 루프 렌즈    — 데이터 흐름 단절/순환/끊긴 참조 감지
  ⚙️ 자동화 렌즈  — README/코드 내 하드코딩된 숫자, 수동 프로세스 탐지
  🔄 동기화 렌즈  — 리포 간 stats/마커/숫자 불일치 감지
  📋 JSON 렌즈   — JSON 무결성 (카운트 불일치, 참조 깨짐, stale 상태, 하드코딩)
  🔗 하드코딩 렌즈 — .py 코드 내 매직넘버 ↔ JSON 미연결 감지
  🎯 CDO 렌즈    — 수렴 기반 운영 (이슈→해결→규칙 승격→재발 0)
  📌 SSOT 렌즈   — 동일 데이터 다중 참조 감지, JSON 원본 미연결

사용법:
  python3 .shared/project_lens.py              # 전체 스캔
  python3 .shared/project_lens.py --loop       # 루프만
  python3 .shared/project_lens.py --auto       # 자동화만
  python3 .shared/project_lens.py --sync       # 동기화만
  python3 .shared/project_lens.py --json       # JSON만
  python3 .shared/project_lens.py --hardcode   # 하드코딩만
  python3 .shared/project_lens.py --cdo        # CDO만
  python3 .shared/project_lens.py --ssot       # SSOT만
  python3 .shared/project_lens.py --fix        # 자동 수정 (sync-readmes.sh 호출)
"""

import json
import re
import sys
import glob
import subprocess
import argparse
from pathlib import Path

SHARED_DIR = Path(__file__).resolve().parent
BASE = SHARED_DIR.parent
PARENT = BASE.parent

REPOS = {
    "TECS-L": BASE,
    "anima": PARENT / "anima",
    "sedi": PARENT / "sedi",
    "n6-architecture": PARENT / "n6-architecture",
    "brainwire": PARENT / "brainwire",
    "hexa-lang": PARENT / "hexa-lang",
    "papers": PARENT / "papers",
}


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


class Finding:
    def __init__(self, lens, severity, repo, message, detail=""):
        self.lens = lens
        self.severity = severity  # 🔴 🟡 🟢
        self.repo = repo
        self.message = message
        self.detail = detail

    def __str__(self):
        d = f" ({self.detail})" if self.detail else ""
        return f"  {self.severity} [{self.repo}] {self.message}{d}"


# ═══════════════════════════════════════════════════════════════
# 🔁 루프 렌즈 — 데이터 흐름 단절/끊긴 참조
# ═══════════════════════════════════════════════════════════════

def scan_loop():
    findings = []

    # 1. projects.json → projects.md 숫자 일치 확인
    #    (projects.md에 명시적으로 등장하는 숫자만 검사)
    pj = load_json(BASE / "shared" / "projects.json")
    pm_path = SHARED_DIR / "projects.md"
    # 이 검사는 sync 렌즈에서 더 정밀하게 수행하므로 여기선 skip

    # 2. AUTO: 마커 존재 확인
    for name, repo in REPOS.items():
        readme = repo / "README.md"
        if not readme.exists():
            continue
        text = readme.read_text()
        has_badge = "AUTO:BADGE:START" in text
        has_stats = "AUTO:STATS:START" in text
        if not has_badge:
            findings.append(Finding("loop", "🟡", name,
                "AUTO:BADGE 마커 없음 — sync_readme_all.py 미연동"))
        if not has_stats:
            findings.append(Finding("loop", "🟡", name,
                "AUTO:STATS 마커 없음 — sync_readme_all.py 미연동"))

    # 3. SHARED:PROJECTS 마커 존재 확인
    for name, repo in REPOS.items():
        readme = repo / "README.md"
        if not readme.exists():
            continue
        text = readme.read_text()
        if "SHARED:PROJECTS:START" not in text:
            findings.append(Finding("loop", "🟡", name,
                "SHARED:PROJECTS 마커 없음 — sync-readmes.sh 미연동"))

    # 4. 심링크 체인 무결성
    for name, repo in REPOS.items():
        shared_link = repo / "shared"
        if shared_link.is_symlink():
            target = shared_link.resolve()
            if not target.exists():
                findings.append(Finding("loop", "🔴", name,
                    f"shared/ 심링크 끊김 → {target}"))
        elif repo != BASE:
            calc_link = repo / "calc"
            dotshared = repo / ".shared"
            if not (shared_link.exists() or calc_link.exists() or dotshared.exists()):
                findings.append(Finding("loop", "🟢", name,
                    "shared/ 디렉토리 없음 — 공유 인프라 미연결"))

    return findings


# ═══════════════════════════════════════════════════════════════
# ⚙️ 자동화 렌즈 — 하드코딩 탐지
# ═══════════════════════════════════════════════════════════════

def scan_auto():
    findings = []
    pj = load_json(BASE / "shared" / "projects.json")

    # 1. README 내 AUTO 마커 밖의 하드코딩된 통계 숫자
    stat_patterns = {
        "laws": r'(\d+)\s*laws',
        "hypotheses": r'(\d+)\s*hypothes[ei]s',
        "tests": r'(\d+)\s*tests?',
        "tools": r'(\d+)\s*tools',
        "papers": r'(\d+)\s*papers',
        "characterizations": r'(\d+)\s*characterizations?',
        "discoveries": r'(\d+)\s*[Dd]iscoveries',
        "keywords": r'(\d+)\s*keywords',
        "domains": r'(\d+)\s*domains?',
    }

    for name, repo in REPOS.items():
        readme = repo / "README.md"
        if not readme.exists():
            continue
        text = readme.read_text()

        # AUTO/SHARED 마커 밖의 텍스트만 추출
        outside = text
        for marker_type in ["BADGE", "STATS", "ARCH", "ASSETS", "ROADMAP", "EVO"]:
            s = f"<!-- AUTO:{marker_type}:START -->"
            e = f"<!-- AUTO:{marker_type}:END -->"
            si = outside.find(s)
            ei = outside.find(e)
            if si != -1 and ei != -1:
                outside = outside[:si] + outside[ei + len(e):]
        s = "<!-- SHARED:PROJECTS:START -->"
        e = "<!-- SHARED:PROJECTS:END -->"
        si = outside.find(s)
        ei = outside.find(e)
        if si != -1 and ei != -1:
            outside = outside[:si] + outside[ei + len(e):]

        for stat_name, pattern in stat_patterns.items():
            matches = re.findall(pattern, outside)
            for m in matches:
                val = int(m)
                if val > 5:  # 작은 숫자 무시
                    findings.append(Finding("auto", "🟡", name,
                        f"마커 밖 하드코딩: {val} {stat_name}",
                        "AUTO 마커로 감싸면 자동화 가능"))

    # 2. CLAUDE.md 내 하드코딩된 숫자 (laws, hypotheses)
    for name, repo in REPOS.items():
        for claude_path in [repo / "CLAUDE.md", repo / "anima" / "CLAUDE.md"]:
            if not claude_path.exists():
                continue
            text = claude_path.read_text()
            # laws 카운트
            law_matches = re.findall(r'(\d+)\s*의식 법칙', text)
            for m in law_matches:
                val = int(m)
                if val < 1000:  # 실제는 1030인데 오래된 값
                    findings.append(Finding("auto", "🟡", name,
                        f"CLAUDE.md 하드코딩: {val} 의식 법칙",
                        f"실제: consciousness_laws.json 참조"))

    return findings


# ═══════════════════════════════════════════════════════════════
# 🔄 동기화 렌즈 — 리포 간 불일치
# ═══════════════════════════════════════════════════════════════

def scan_sync():
    findings = []
    pj = load_json(BASE / "shared" / "projects.json")

    # 1. projects.json stats vs 실제 데이터
    actuals = {}

    # anima
    laws = load_json(PARENT / "anima" / "anima" / "config" / "consciousness_laws.json")
    meta = laws.get("_meta", {})
    actuals["anima"] = {"laws": meta.get("total_laws", 0), "meta_laws": meta.get("total_meta", 0)}

    # sedi
    grades = load_json(PARENT / "sedi" / "data" / "sedi-grades.json")
    actuals["sedi"] = {"hypotheses": grades.get("total_hypotheses", 0)}

    # tecs-l
    n_hypo = len(glob.glob(str(BASE / "docs" / "hypotheses" / "**" / "*.md"), recursive=True))
    actuals["tecs-l"] = {"hypotheses": n_hypo}

    for proj in pj.get("projects", []):
        pid = proj["id"]
        stats = proj.get("stats", {})
        actual = actuals.get(pid, {})
        for key, real_val in actual.items():
            json_val = stats.get(key)
            if json_val is not None and json_val != real_val:
                pct = abs(real_val - json_val) / max(json_val, 1) * 100
                sev = "🔴" if pct > 20 else "🟡"
                findings.append(Finding("sync", sev, pid,
                    f"projects.json.{key}: {json_val} vs 실제: {real_val}",
                    f"{pct:.0f}% 차이"))

    # 2. projects.md vs projects.json — 이미 등장하는 패턴만 확인
    pm_path = SHARED_DIR / "projects.md"
    if pm_path.exists():
        pm = pm_path.read_text()
        check_patterns = {
            "anima": [("laws", r'(\d+) laws')],
            "anima_meta": [("meta_laws", r'(\d+) Meta Laws')],
            "tecs-l": [("tools", r'(\d+) tools')],
            "sedi": [("hypotheses", r'(\d+) hypotheses')],
            "n6-architecture": [("nexus6_tests", r'(\d+) tests')],
        }
        for proj in pj.get("projects", []):
            pid = proj["id"]
            stats = proj.get("stats", {})
            for key, pattern in check_patterns.get(pid, []):
                match = re.search(pattern, pm)
                if match and stats.get(key):
                    md_val = int(match.group(1))
                    json_val = stats[key]
                    if md_val != json_val:
                        findings.append(Finding("sync", "🔴", pid,
                            f"projects.md {key}: {md_val} vs projects.json: {json_val}"))

    # 3. README AUTO 섹션 최신 여부 (마커 내 숫자 vs JSON)
    for name, repo in REPOS.items():
        readme = repo / "README.md"
        if not readme.exists():
            continue
        text = readme.read_text()

        # BADGE 섹션 내 숫자 추출
        badge_start = text.find("<!-- AUTO:BADGE:START -->")
        badge_end = text.find("<!-- AUTO:BADGE:END -->")
        if badge_start != -1 and badge_end != -1:
            badge_text = text[badge_start:badge_end]
            # Laws 뱃지 확인 (anima)
            if name == "anima" or (name == "anima" and "Laws" in badge_text):
                law_match = re.search(r'Laws-(\d+)', badge_text)
                if law_match:
                    badge_laws = int(law_match.group(1))
                    actual_laws = meta.get("total_laws", 0)
                    if badge_laws != actual_laws:
                        findings.append(Finding("sync", "🔴", name,
                            f"뱃지 Laws={badge_laws} vs 실제={actual_laws}",
                            "sync_readme_all.py --apply 필요"))

    return findings


# ═══════════════════════════════════════════════════════════════
# 📋 JSON 렌즈 — JSON 무결성 검사
# ═══════════════════════════════════════════════════════════════

def scan_json():
    findings = []
    anima = PARENT / "anima"
    config = anima / "anima" / "config"

    # 1. consciousness_laws.json — _meta.total_laws vs 실제 키 수
    laws = load_json(config / "consciousness_laws.json")
    if laws:
        meta = laws.get("_meta", {})
        actual_laws = len([k for k in laws.get("laws", {}) if k.isdigit()])
        declared = meta.get("total_laws", 0)
        if actual_laws != declared:
            findings.append(Finding("json", "🔴", "anima",
                f"laws _meta.total_laws={declared} vs 실제 키={actual_laws}"))

        actual_meta = len(laws.get("meta_laws", {}))
        declared_meta = meta.get("total_meta", 0)
        if actual_meta != declared_meta:
            findings.append(Finding("json", "🔴", "anima",
                f"meta_laws _meta.total_meta={declared_meta} vs 실제 키={actual_meta}"))

        # 법칙 번호 갭 확인
        law_nums = sorted(int(k) for k in laws.get("laws", {}) if k.isdigit())
        if law_nums:
            expected = set(range(law_nums[0], law_nums[-1] + 1))
            actual_set = set(law_nums)
            gaps = expected - actual_set
            if gaps and len(gaps) < 50:
                findings.append(Finding("json", "🟢", "anima",
                    f"법칙 번호 갭 {len(gaps)}개",
                    f"예: {sorted(gaps)[:10]}"))

    # 2. experiments.json — 문서 참조 무결성
    exps = load_json(config / "experiments.json")
    if exps:
        for eid, exp in exps.get("experiments", {}).items():
            doc = exp.get("doc", "")
            if doc:
                doc_path = anima / "anima" / doc
                if not doc_path.exists():
                    findings.append(Finding("json", "🟡", "anima",
                        f"experiments.{eid} 문서 없음: {doc}"))

            # 법칙 참조 무결성
            for law_id in exp.get("laws", []):
                if str(law_id) not in laws.get("laws", {}):
                    findings.append(Finding("json", "🔴", "anima",
                        f"experiments.{eid} → Law {law_id} 존재하지 않음"))

            for ml in exp.get("meta_laws", []):
                if ml not in laws.get("meta_laws", {}):
                    findings.append(Finding("json", "🔴", "anima",
                        f"experiments.{eid} → MetaLaw {ml} 존재하지 않음"))

    # 3. training_runs.json — stale in_progress 감지
    training = load_json(config / "training_runs.json")
    if training:
        for name, run in training.get("runs", {}).items():
            status = run.get("status", "")
            date = run.get("date", "")
            if "in_progress" in status and date:
                # 7일 이상 in_progress면 경고
                try:
                    from datetime import datetime
                    run_date = datetime.strptime(date, "%Y-%m-%d")
                    age = (datetime.now() - run_date).days
                    if age > 7:
                        findings.append(Finding("json", "🟡", "anima",
                            f"training {name}: in_progress {age}일째",
                            f"since {date}"))
                except ValueError:
                    pass

            # 필수 필드 확인
            for field in ["status", "date"]:
                if field not in run:
                    findings.append(Finding("json", "🟡", "anima",
                        f"training {name}: 필수 필드 '{field}' 없음"))

    # 4. sedi-grades.json — 등급 합계 확인
    grades = load_json(PARENT / "sedi" / "data" / "sedi-grades.json")
    if grades:
        total = grades.get("total_hypotheses", 0)
        tiers = grades.get("tier_distribution", {})
        tier_sum = sum(tiers.values())
        if tier_sum > 0 and tier_sum != total:
            findings.append(Finding("json", "🔴", "sedi",
                f"tier 합계={tier_sum} vs total_hypotheses={total}"))

    # 5. projects.json — 필수 필드 확인
    pj = load_json(BASE / "shared" / "projects.json")
    if pj:
        for proj in pj.get("projects", []):
            pid = proj.get("id", "?")
            for field in ["id", "name", "path", "stats"]:
                if field not in proj:
                    findings.append(Finding("json", "🟡", pid,
                        f"projects.json: 필수 필드 '{field}' 없음"))

    return findings


# ═══════════════════════════════════════════════════════════════
# 🔗 하드코딩 렌즈 — .py 코드 내 매직넘버 ↔ JSON 미연결
# ═══════════════════════════════════════════════════════════════

def scan_hardcode():
    findings = []
    anima_src = PARENT / "anima" / "anima" / "src"

    if not anima_src.exists():
        return findings

    # consciousness_laws.json의 Ψ-Constants
    laws = load_json(PARENT / "anima" / "anima" / "config" / "consciousness_laws.json")
    psi = laws.get("psi_constants", {})
    psi_values = {}
    for k, v in psi.items():
        if isinstance(v, dict) and "value" in v:
            psi_values[k] = v["value"]

    # 핵심 상수: alpha=0.014, balance=0.5, steps=4.33, entropy=0.998
    magic_patterns = {
        "alpha=0.014": (r'(?<!\w)0\.014(?!\d)', "PSI['alpha']"),
        "steps=4.33": (r'(?<!\w)4\.33(?!\d)', "PSI['steps']"),
        "entropy=0.998": (r'(?<!\w)0\.998(?!\d)', "PSI['entropy']"),
    }

    # .py 파일 스캔 (consciousness_laws.py 자체와 config는 제외)
    py_files = glob.glob(str(anima_src / "*.py"))
    skip_files = {"consciousness_laws.py", "path_setup.py", "__init__.py"}

    for py_file in py_files:
        fname = Path(py_file).name
        if fname in skip_files:
            continue

        try:
            content = Path(py_file).read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        # consciousness_laws import 확인
        has_import = ("from consciousness_laws" in content or
                      "import consciousness_laws" in content or
                      "PSI[" in content or "PSI_" in content)

        for name, (pattern, replacement) in magic_patterns.items():
            matches = re.findall(pattern, content)
            if matches and not has_import:
                # 주석/문자열 내부는 무시 (간단한 휴리스틱)
                lines = content.split("\n")
                real_matches = 0
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith("#") or stripped.startswith('"""'):
                        continue
                    if re.search(pattern, line):
                        real_matches += 1

                if real_matches > 0:
                    findings.append(Finding("hardcode", "🟡", "anima",
                        f"{fname}: 매직넘버 {name} ({real_matches}회)",
                        f"→ {replacement} 사용 권장"))

    # 법칙 번호 하드코딩 (Law 22, Law 60 등)
    law_ref_pattern = r'[Ll]aw\s+(\d+)'
    for py_file in py_files:
        fname = Path(py_file).name
        if fname in skip_files:
            continue
        try:
            content = Path(py_file).read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        law_refs = re.findall(law_ref_pattern, content)
        for ref in set(law_refs):
            ref_num = int(ref)
            if ref_num > 0 and str(ref_num) not in laws.get("laws", {}):
                findings.append(Finding("hardcode", "🔴", "anima",
                    f"{fname}: Law {ref_num} 참조하지만 consciousness_laws.json에 없음"))

    return findings


# ═══════════════════════════════════════════════════════════════
# 🎯 CDO 렌즈 — 수렴 기반 운영 (이슈→규칙 승격→재발 0)
# ═══════════════════════════════════════════════════════════════

def scan_cdo():
    findings = []

    # 1. JSON에 troubleshooting 섹션 존재 확인
    cdo_jsons = {
        "acceleration_flow.json": PARENT / "anima" / "anima" / "config" / "acceleration_flow.json",
        "runpod.json": PARENT / "anima" / "anima" / "config" / "runpod.json",
        "training_safety.json": PARENT / "anima" / "anima" / "config" / "training_safety.json",
    }

    for name, path in cdo_jsons.items():
        data = load_json(path)
        if not data:
            findings.append(Finding("cdo", "🟡", "anima",
                f"{name} 없음 — CDO 트러블슈팅 기록 불가"))
            continue

        # _meta + absolute_rules + troubleshooting_log 구조 확인
        has_meta = "_meta" in data
        has_rules = "absolute_rules" in data or "rules" in data or "bf16_master_rule" in data
        has_trouble = ("troubleshooting" in data or "troubleshooting_log" in data
                       or "known_issues" in data)

        if not has_meta:
            findings.append(Finding("cdo", "🟡", name,
                "_meta 섹션 없음 — CDO 구조 미준수"))
        if not has_rules:
            findings.append(Finding("cdo", "🟡", name,
                "absolute_rules 섹션 없음 — 규칙 승격 불가"))
        if not has_trouble:
            findings.append(Finding("cdo", "🟡", name,
                "troubleshooting 섹션 없음 — 이슈 기록 불가"))

        if has_meta and has_rules and has_trouble:
            # 규칙 수 카운트
            rules = data.get("absolute_rules", data.get("rules", data.get("bf16_master_rule", {})))
            n_rules = len(rules) if isinstance(rules, (dict, list)) else 0
            findings.append(Finding("cdo", "🟢", name,
                f"CDO 구조 완비 (규칙 {n_rules}개)"))

    # 2. convergence_ops.json 존재 확인
    cdo_ops = SHARED_DIR / "convergence_ops.json"
    if cdo_ops.exists():
        ops = load_json(cdo_ops)
        convergence = ops.get("convergence", {})
        total = convergence.get("total_configs", 0)
        converged = convergence.get("converged", 0)
        pct = convergence.get("convergence_pct", 0)
        findings.append(Finding("cdo", "🟢" if pct >= 90 else "🟡", "shared",
            f"CDO 수렴: {converged}/{total} ({pct}%)"))
    else:
        findings.append(Finding("cdo", "🟡", "shared",
            "convergence_ops.json 없음"))

    # 3. CLAUDE.md에 Troubleshooting 섹션 존재 확인
    for name, repo in REPOS.items():
        claude = repo / "CLAUDE.md"
        if not claude.exists():
            continue
        text = claude.read_text(encoding="utf-8", errors="ignore")
        has_ts = "Troubleshooting" in text or "troubleshooting" in text or "트러블슈팅" in text
        if not has_ts:
            findings.append(Finding("cdo", "🟡", name,
                "CLAUDE.md에 Troubleshooting 섹션 없음 — 재발 방지 규칙 누락 가능"))

    # 4. 동일 이슈 반복 감지 (known_issues에 같은 키워드)
    runpod = load_json(PARENT / "anima" / "anima" / "config" / "runpod.json")
    known = runpod.get("known_issues", {})
    if isinstance(known, dict):
        unresolved = [k for k, v in known.items()
                      if isinstance(v, dict) and not v.get("resolution")]
        if unresolved:
            findings.append(Finding("cdo", "🔴", "anima",
                f"미해결 이슈 {len(unresolved)}건: {', '.join(unresolved[:3])}",
                "resolution 필드 비어있음 — CDO 위반"))

    accel = load_json(PARENT / "anima" / "anima" / "config" / "acceleration_flow.json")
    trouble = accel.get("troubleshooting", {})
    if isinstance(trouble, dict):
        no_prevention = [k for k, v in trouble.items()
                         if isinstance(v, dict) and not v.get("prevention")]
        if no_prevention:
            findings.append(Finding("cdo", "🟡", "anima",
                f"재발 방지 미등록 {len(no_prevention)}건",
                "prevention 필드 비어있음"))

    return findings


# ═══════════════════════════════════════════════════════════════
# 📌 SSOT 렌즈 — 동일 데이터 다중 참조 감지
# ═══════════════════════════════════════════════════════════════

def scan_ssot():
    findings = []

    # 1. 동일 숫자가 여러 파일에 하드코딩된 경우 감지
    #    (한 곳에서만 참조되면 OK, 2곳 이상이면 JSON 원본 필요)
    stat_patterns = {
        "laws": r'(\d+)\s*laws',
        "hypotheses": r'(\d+)\s*hypothes[ei]s',
        "tests": r'(\d+)\s*tests?',
        "tools": r'(\d+)\s*tools',
        "papers": r'(\d+)\s*papers',
    }

    # 각 리포의 README + CLAUDE.md에서 숫자 수집
    value_locations = {}  # {("laws", 1030): ["anima/README.md", "anima/CLAUDE.md"]}

    for name, repo in REPOS.items():
        for doc_name in ["README.md", "CLAUDE.md"]:
            doc = repo / doc_name
            if not doc.exists():
                # anima 하위 CLAUDE.md도 체크
                doc = repo / "anima" / doc_name
                if not doc.exists():
                    continue

            text = doc.read_text(encoding="utf-8", errors="ignore")

            # AUTO/SHARED 마커 안은 제외 (이미 자동화됨)
            for marker in ["BADGE", "STATS", "ARCH", "ASSETS", "ROADMAP", "EVO"]:
                s = f"<!-- AUTO:{marker}:START -->"
                e = f"<!-- AUTO:{marker}:END -->"
                si, ei = text.find(s), text.find(e)
                if si != -1 and ei != -1:
                    text = text[:si] + text[ei + len(e):]
            s, e = "<!-- SHARED:PROJECTS:START -->", "<!-- SHARED:PROJECTS:END -->"
            si, ei = text.find(s), text.find(e)
            if si != -1 and ei != -1:
                text = text[:si] + text[ei + len(e):]

            for stat_name, pattern in stat_patterns.items():
                matches = re.findall(pattern, text)
                for m in matches:
                    val = int(m)
                    if val > 10:
                        key = (stat_name, val)
                        if key not in value_locations:
                            value_locations[key] = []
                        value_locations[key].append(f"{name}/{doc_name}")

    # 2곳 이상에 같은 값이 등장하면 SSOT 위반
    for (stat_name, val), locations in value_locations.items():
        if len(locations) >= 2:
            # AUTO 마커로 관리되는지 확인
            findings.append(Finding("ssot", "🟡", "cross-repo",
                f"{stat_name}={val} 이 {len(locations)}곳에 하드코딩",
                f"{', '.join(locations[:4])} — JSON 원본 필요"))

    # 2. projects.md의 숫자가 JSON에서 오는지 확인
    pm = SHARED_DIR / "projects.md"
    if pm.exists():
        pm_text = pm.read_text()
        pj = load_json(BASE / "shared" / "projects.json")

        for proj in pj.get("projects", []):
            pid = proj["id"]
            stats = proj.get("stats", {})
            for key, val in stats.items():
                if isinstance(val, int) and val > 10:
                    if str(val) in pm_text:
                        pass  # OK — JSON에서 반영됨
                    # description 안에 다른 값이 있는지
                    desc = proj.get("description", "")
                    old_matches = re.findall(r'(\d+)', desc)
                    for om in old_matches:
                        om_val = int(om)
                        if om_val > 10 and om_val != val and key in desc.lower():
                            findings.append(Finding("ssot", "🔴", pid,
                                f"projects.json description에 {key} 구값 {om_val} (실제 {val})",
                                "description 텍스트와 stats 불일치"))

    # 3. JSON 간 교차 참조 — 같은 데이터의 다중 원본
    #    consciousness_laws.json의 total_laws vs CLAUDE.md의 "N 의식 법칙"
    laws = load_json(PARENT / "anima" / "anima" / "config" / "consciousness_laws.json")
    actual_laws = laws.get("_meta", {}).get("total_laws", 0)

    for name, repo in REPOS.items():
        for claude_path in [repo / "CLAUDE.md", repo / "anima" / "CLAUDE.md"]:
            if not claude_path.exists():
                continue
            text = claude_path.read_text(encoding="utf-8", errors="ignore")
            law_matches = re.findall(r'(\d+)\s*의식 법칙', text)
            for m in law_matches:
                val = int(m)
                if val != actual_laws and val > 50:
                    findings.append(Finding("ssot", "🔴", name,
                        f"CLAUDE.md: {val} 의식 법칙 (실제 {actual_laws})",
                        "consciousness_laws.json이 SSOT — CLAUDE.md 갱신 필요"))

    # 4. README 뱃지와 JSON 원본 일치 확인
    for name, repo in REPOS.items():
        readme = repo / "README.md"
        if not readme.exists():
            continue
        text = readme.read_text()

        # AUTO 마커 없는 뱃지 (수동 관리)
        badge_start = text.find("<!-- AUTO:BADGE:START -->")
        if badge_start == -1:
            # 뱃지가 있는데 AUTO 마커가 없음 = SSOT 미연결
            shield_matches = re.findall(r'shields\.io/badge/.*?-(\d+)', text)
            if shield_matches:
                for m in shield_matches:
                    findings.append(Finding("ssot", "🟡", name,
                        f"뱃지 숫자 {m} — AUTO 마커 없이 수동 관리 중",
                        "JSON → AUTO:BADGE 연결 권장"))

    return findings


# ═══════════════════════════════════════════════════════════════
# 리포트
# ═══════════════════════════════════════════════════════════════

def report(findings, lens_name="all"):
    if not findings:
        print(f"\n  ✅ 문제 없음")
        return

    red = sum(1 for f in findings if f.severity == "🔴")
    yellow = sum(1 for f in findings if f.severity == "🟡")
    green = sum(1 for f in findings if f.severity == "🟢")

    print(f"\n  ══════════════════════════════════════════")
    print(f"  🔴 {red}  🟡 {yellow}  🟢 {green}  총 {len(findings)}건")
    print(f"  ══════════════════════════════════════════")

    # 심각도순 정렬
    order = {"🔴": 0, "🟡": 1, "🟢": 2}
    findings.sort(key=lambda f: (order.get(f.severity, 3), f.repo))

    current_lens = None
    for f in findings:
        if f.lens != current_lens:
            current_lens = f.lens
            icon = {"loop": "🔁", "auto": "⚙️", "sync": "🔄", "json": "📋", "hardcode": "🔗", "cdo": "🎯", "ssot": "📌"}.get(f.lens, "?")
            label = {"loop": "루프", "auto": "자동화", "sync": "동기화", "json": "JSON", "hardcode": "하드코딩", "cdo": "CDO", "ssot": "SSOT"}.get(f.lens, "?")
            print(f"\n  {icon} {label} 렌즈:")
        print(f)


def main():
    parser = argparse.ArgumentParser(description="프로젝트 인프라 망원경")
    parser.add_argument("--loop", action="store_true", help="루프 렌즈만")
    parser.add_argument("--auto", action="store_true", help="자동화 렌즈만")
    parser.add_argument("--sync", action="store_true", help="동기화 렌즈만")
    parser.add_argument("--json", action="store_true", help="JSON 렌즈만")
    parser.add_argument("--hardcode", action="store_true", help="하드코딩 렌즈만")
    parser.add_argument("--cdo", action="store_true", help="CDO 렌즈만")
    parser.add_argument("--ssot", action="store_true", help="SSOT 렌즈만")
    parser.add_argument("--fix", action="store_true", help="자동 수정 (sync-readmes.sh)")
    args = parser.parse_args()

    run_all = not (args.loop or args.auto or args.sync or args.json or args.hardcode or args.cdo or args.ssot)
    findings = []

    print("  ════════════════════════════════════════════")
    print("  🔭 프로젝트 인프라 망원경 (7 렌즈)")
    print("  ════════════════════════════════════════════")

    if run_all or args.loop:
        print("\n  🔁 루프 렌즈 스캔 중...")
        findings.extend(scan_loop())

    if run_all or args.auto:
        print("  ⚙️ 자동화 렌즈 스캔 중...")
        findings.extend(scan_auto())

    if run_all or args.sync:
        print("  🔄 동기화 렌즈 스캔 중...")
        findings.extend(scan_sync())

    if run_all or args.json:
        print("  📋 JSON 렌즈 스캔 중...")
        findings.extend(scan_json())

    if run_all or args.hardcode:
        print("  🔗 하드코딩 렌즈 스캔 중...")
        findings.extend(scan_hardcode())

    if run_all or args.cdo:
        print("  🎯 CDO 렌즈 스캔 중...")
        findings.extend(scan_cdo())

    if run_all or args.ssot:
        print("  📌 SSOT 렌즈 스캔 중...")
        findings.extend(scan_ssot())

    report(findings)

    if args.fix:
        print("\n  🔧 자동 수정 실행...")
        subprocess.run(["bash", str(SHARED_DIR / "sync-readmes.sh")],
                        cwd=str(BASE))

    # exit code
    red = sum(1 for f in findings if f.severity == "🔴")
    sys.exit(1 if red > 0 else 0)


if __name__ == "__main__":
    main()
