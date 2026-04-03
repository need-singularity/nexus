#!/usr/bin/env python3
"""
sync_readme_all.py — 전 프로젝트 JSON SSOT → README.md 자동 반영

각 리포의 JSON 원본에서 통계를 읽어 README 마커 구간을 자동 업데이트.
마커: <!-- AUTO:{SECTION}:START --> ... <!-- AUTO:{SECTION}:END -->

사용법:
  python3 .shared/sync_readme_all.py           # dry-run
  python3 .shared/sync_readme_all.py --apply   # 실제 적용
  python3 .shared/sync_readme_all.py --check   # CI용

지원 리포: TECS-L, anima, sedi, n6-architecture, brainwire, hexa-lang, papers
"""

import json
import sys
import glob
import argparse
from pathlib import Path

SHARED_DIR = Path(__file__).resolve().parent
BASE = SHARED_DIR.parent          # ~/Dev/TECS-L
PARENT = BASE.parent              # ~/Dev/


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


def replace_section(text, section, content):
    start = f"<!-- AUTO:{section}:START -->"
    end = f"<!-- AUTO:{section}:END -->"
    si = text.find(start)
    ei = text.find(end)
    if si == -1 or ei == -1:
        return text, False
    new = text[:si + len(start)] + "\n" + content + "\n" + text[ei:]
    return new, new != text


def apply_sections(readme_path, sections):
    text = readme_path.read_text(encoding="utf-8")
    changed = False
    missing = []
    for name, content in sections.items():
        if f"<!-- AUTO:{name}:START -->" not in text:
            missing.append(name)
            continue
        text, c = replace_section(text, name, content)
        if c:
            changed = True
    return text, changed, missing


# ═══════════════════════════════════════════════════════════════
# Per-repo generators
# ═══════════════════════════════════════════════════════════════

def gen_tecs_l(repo):
    """TECS-L: 가설 수, 도구 수, 발견 수"""
    n_hypo = count_md(repo / "docs" / "hypotheses")
    n_tools = count_glob(str(repo / "*.py")) + count_glob(str(repo / "math" / "*.py"))
    projects = load_json(repo / "shared" / "projects.json") if (repo / "shared").exists() else load_json(SHARED_DIR / "projects.json")
    stats = {}
    for p in projects.get("projects", []):
        if p["id"] == "tecs-l":
            stats = p.get("stats", {})

    chars = stats.get("characterizations", "?")
    discoveries = stats.get("major_discoveries", "?")

    badge = (
        f'[![Hypotheses](https://img.shields.io/badge/Hypotheses-{n_hypo}+-orange.svg)](docs/hypotheses/)\n'
        f'[![Tools](https://img.shields.io/badge/Tools-{n_tools}+-blue.svg)](tools/)'
    )

    stats_block = f"""\
```
  n=6 characterizations:  {chars}
  Major discoveries:      {discoveries}
  Hypotheses:             {n_hypo}+
  Tools:                  {n_tools}+
```"""

    return {"BADGE": badge, "STATS": stats_block}


def gen_anima(repo):
    """Anima: anima 전용 sync_readme.py에 위임"""
    script = repo / "scripts" / "sync_readme.py"
    if script.exists():
        import subprocess
        subprocess.run([sys.executable, str(script), "--apply"], cwd=str(repo), capture_output=True)
    return {}  # anima는 자체 스크립트로 처리


def gen_sedi(repo):
    """SEDI: 가설 수, 등급 분포"""
    grades = load_json(repo / "data" / "sedi-grades.json")
    n_hypo = count_md(repo / "docs" / "hypotheses")

    total = grades.get("total_hypotheses", n_hypo)
    tiers = grades.get("tier_distribution", grades.get("tier_counts", {}))
    tier_a = tiers.get("A", "?")
    tier_b = tiers.get("B", "?")
    mean_bits = grades.get("mean_bits", "?")

    badge = (
        f'[![Hypotheses](https://img.shields.io/badge/Hypotheses-{total}+-orange.svg)](docs/hypotheses/)'
    )

    stats_block = f"""\
```
  Hypotheses:     {total} ({n_hypo} docs)
  Tier A (확정):  {tier_a}
  Tier B:         {tier_b}
  Mean bits:      {mean_bits}
```"""

    return {"BADGE": badge, "STATS": stats_block}


def gen_n6(repo):
    """N6 Architecture: DSE 도메인, BT, 테스트"""
    projects = load_json(repo / "shared" / "projects.json")
    stats = {}
    for p in projects.get("projects", []):
        if p["id"] == "n6-architecture":
            stats = p.get("stats", {})

    ai = stats.get("ai_techniques", "?")
    dse = stats.get("dse_domains", "?")
    dse_paths = stats.get("dse_paths", "?")
    if isinstance(dse_paths, int) and dse_paths >= 1_000_000:
        dse_paths_str = f"{dse_paths / 1_000_000:.1f}M"
    else:
        dse_paths_str = str(dse_paths)

    # nexus6 테스트 수
    nexus6_tests = "?"
    nexus6_dir = repo / "tools" / "nexus6"
    if nexus6_dir.exists():
        import subprocess
        r = subprocess.run(["grep", "-r", "#\\[test\\]", str(nexus6_dir / "src")],
                           capture_output=True, text=True)
        if r.returncode == 0:
            nexus6_tests = len(r.stdout.strip().split("\n"))

    badge = (
        f'[![DSE](https://img.shields.io/badge/DSE-{dse}%20domains-blue.svg)](docs/dse-map.toml)\n'
        f'[![NEXUS-6](https://img.shields.io/badge/NEXUS--6-{nexus6_tests}%20tests-green.svg)](tools/nexus6/)'
    )

    stats_block = f"""\
```
  AI techniques:    {ai}
  DSE domains:      {dse}
  DSE paths:        {dse_paths_str}+
  NEXUS-6 tests:    {nexus6_tests}
```"""

    return {"BADGE": badge, "STATS": stats_block}


def gen_brainwire(repo):
    """BrainWire: modalities, 테스트, 가설"""
    projects = load_json(repo / "shared" / "projects.json")
    stats = {}
    for p in projects.get("projects", []):
        if p["id"] == "brainwire":
            stats = p.get("stats", {})

    modalities = stats.get("modalities", "?")

    # 테스트 수 (pytest 기반)
    n_tests = count_glob(str(repo / "tests" / "test_*.py"))
    # 가설 수
    n_hypo = count_md(repo / "docs" / "hypotheses") if (repo / "docs" / "hypotheses").exists() else 0

    badge = (
        f'[![Modalities](https://img.shields.io/badge/Modalities-{modalities}-blue.svg)]()'
    )

    stats_block = f"""\
```
  Modalities:       {modalities}
  Test files:       {n_tests}
  Hypothesis docs:  {n_hypo}
```"""

    return {"BADGE": badge, "STATS": stats_block}


def gen_hexa(repo):
    """HEXA-LANG: keywords, operators, primitives, DSE combos"""
    projects = load_json(repo / "shared" / "projects.json")
    stats = {}
    for p in projects.get("projects", []):
        if p["id"] == "hexa-lang":
            stats = p.get("stats", {})

    kw = stats.get("keywords", "?")
    ops = stats.get("operators", "?")
    prims = stats.get("primitives", "?")
    combos = stats.get("dse_combos", "?")
    if isinstance(combos, int):
        combos_str = f"{combos:,}"
    else:
        combos_str = str(combos)

    badge = (
        f'[![Keywords](https://img.shields.io/badge/Keywords-{kw}-blue.svg)]()\n'
        f'[![DSE](https://img.shields.io/badge/DSE-{combos_str}%20combos-gold.svg)]()'
    )

    stats_block = f"""\
```
  Keywords:      {kw} (σ·τ+sopfr)
  Operators:     {ops} (J₂)
  Primitives:    {prims} (σ-τ)
  DSE combos:    {combos_str}
```"""

    return {"BADGE": badge, "STATS": stats_block}


def gen_papers(repo):
    """Papers: 총 논문 수"""
    manifest = load_json(repo / "zenodo" / "manifest.json") if (repo / "zenodo").exists() else {}
    # fallback: TECS-L
    if not manifest:
        manifest = load_json(BASE / "zenodo" / "manifest.json")

    papers = manifest.get("papers", {})
    total = sum(len(v) for v in papers.values())
    by_project = {k: len(v) for k, v in papers.items()}

    badge = (
        f'[![Papers](https://img.shields.io/badge/Papers-{total}-blue.svg)]()'
    )

    lines = ["```"]
    lines.append(f"  Total papers: {total}")
    for proj, count in sorted(by_project.items()):
        lines.append(f"  {proj}: {count}")
    lines.append("```")

    return {"BADGE": badge, "STATS": "\n".join(lines)}


# ═══════════════════════════════════════════════════════════════

REPOS = {
    "TECS-L":           (BASE, gen_tecs_l),
    "anima":            (PARENT / "anima", gen_anima),
    "sedi":             (PARENT / "sedi", gen_sedi),
    "n6-architecture":  (PARENT / "n6-architecture", gen_n6),
    "brainwire":        (PARENT / "brainwire", gen_brainwire),
    "hexa-lang":        (PARENT / "hexa-lang", gen_hexa),
    "papers":           (PARENT / "papers", gen_papers),
}


def main():
    parser = argparse.ArgumentParser(description="All-repo JSON SSOT → README sync")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--repo", help="특정 리포만 (예: sedi)")
    args = parser.parse_args()

    any_fail = False

    for name, (repo_path, generator) in REPOS.items():
        if args.repo and args.repo != name:
            continue

        readme = repo_path / "README.md"
        if not readme.exists():
            continue

        print(f"[{name}]")

        sections = generator(repo_path)
        if not sections:
            print(f"  (자체 스크립트 위임)")
            continue

        text, changed, missing = apply_sections(readme, sections)

        if missing:
            print(f"  ⚠️  마커 없음: {', '.join(missing)}")

        if changed:
            if args.apply:
                readme.write_text(text, encoding="utf-8")
                print(f"  ✅ 업데이트 적용됨")
            else:
                print(f"  🔄 변경 감지 (--apply로 적용)")
            if args.check:
                any_fail = True
        else:
            print(f"  ── 변경 없음")

    if args.check and any_fail:
        print("\n❌ 불일치 발견!")
        sys.exit(1)


if __name__ == "__main__":
    main()
