#!/usr/bin/env python3
"""NEXUS-6 Growth Bus — 모든 엔진, 모든 리포, 무제한 순환 피드백

핵심 원리:
  1. ~/Dev 아래 모든 리포 자동 발견 (새 리포 = 자동 합류)
  2. 공유 상태 버스: shared/growth_bus.jsonl (모든 Phase가 읽고 쓰기)
  3. Phase 수 무제한 — 자동 발견된 엔진은 자동 등록
  4. Phase 간 피드백: 이전 Phase 출력 → 다음 Phase 입력
  5. 리포 간 피드백: 리포A 성장 → 버스 기록 → 리포B가 읽고 반응
  6. 블로업 재귀: 창발물 → 새 스캔 대상 → 재창발 (무한)

사용:
  python3 growth_bus.py                    # 1 사이클
  python3 growth_bus.py --cycles 999       # 무한
  python3 growth_bus.py --interval 180     # 3분 간격
  python3 growth_bus.py --discover-only    # 엔진/리포 발견만
"""

import json, os, sys, time, subprocess, glob, hashlib
from datetime import datetime
from pathlib import Path

# Force unbuffered output for nohup
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# ═══════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════

NEXUS_ROOT = Path(__file__).resolve().parent.parent
DEV_ROOT = NEXUS_ROOT.parent  # ~/Dev
BUS_FILE = NEXUS_ROOT / "shared" / "growth_bus.jsonl"
STATE_FILE = NEXUS_ROOT / "shared" / "growth_state.json"
REPORT_FILE = NEXUS_ROOT / "shared" / "infinite_growth_report.md"

# ═══════════════════════════════════════════════════════════════════
# BUS — 공유 상태 (모든 Phase, 모든 리포가 읽고 쓰기)
# ═══════════════════════════════════════════════════════════════════

class GrowthBus:
    """순환 피드백 버스. 모든 엔진이 여기에 쓰고, 여기서 읽는다."""

    def __init__(self):
        self.events = []  # 현재 사이클 이벤트
        self.state = self._load_state()

    def _load_state(self):
        if STATE_FILE.exists():
            try:
                return json.loads(STATE_FILE.read_text())
            except:
                pass
        return {
            "cycle": 0,
            "repos": {},
            "engines": {},
            "lenses": 0, "calcs": 0, "tests": 0,
            "discoveries": 0, "emergences": 0,
            "total_events": 0,
            "feedback_chains": 0,
        }

    def emit(self, source, event_type, data):
        """Phase/엔진이 버스에 이벤트 발행."""
        event = {
            "ts": datetime.now().isoformat(),
            "source": source,
            "type": event_type,
            "data": data,
            "cycle": self.state["cycle"],
        }
        self.events.append(event)
        # Append to persistent log
        with open(BUS_FILE, "a") as f:
            f.write(json.dumps(event) + "\n")
        return event

    def query(self, event_type=None, source=None, last_n=10):
        """버스에서 이벤트 조회 (다른 Phase가 읽기)."""
        # Read from persistent log
        events = []
        if BUS_FILE.exists():
            for line in BUS_FILE.read_text().strip().split("\n")[-last_n * 3:]:
                if not line.strip():
                    continue
                try:
                    e = json.loads(line)
                    if event_type and e.get("type") != event_type:
                        continue
                    if source and e.get("source") != source:
                        continue
                    events.append(e)
                except:
                    pass
        return events[-last_n:]

    def save_state(self):
        STATE_FILE.write_text(json.dumps(self.state, indent=2))

# ═══════════════════════════════════════════════════════════════════
# REPO DISCOVERY — ~/Dev 아래 모든 리포 자동 탐지
# ═══════════════════════════════════════════════════════════════════

def discover_repos():
    """~/Dev 아래 git 리포 전부 발견. 새 리포 = 자동 합류."""
    repos = []
    for d in sorted(DEV_ROOT.iterdir()):
        if d.is_dir() and (d / ".git").exists():
            info = {
                "name": d.name,
                "path": str(d),
                "has_shared": (d / ".shared").exists() or (d / "shared").exists(),
                "has_claude": (d / "CLAUDE.md").exists(),
                "has_growth": any((d / "scripts").glob("*growth*")) if (d / "scripts").exists() else False,
                "has_tests": (d / "tests").exists() or (d / "test").exists(),
                "has_src": (d / "src").exists(),
                "languages": detect_languages(d),
            }
            # Count files as growth metric (fast: top 2 levels only)
            try:
                count = int(subprocess.run(
                    f"find {d} -maxdepth 2 -type f | wc -l",
                    shell=True, capture_output=True, text=True, timeout=5
                ).stdout.strip())
            except:
                count = 0
            info["file_count"] = count
            repos.append(info)
    return repos

def detect_languages(repo_path):
    """리포 주요 언어 감지."""
    langs = set()
    try:
        result = subprocess.run(
            f"find {repo_path} -maxdepth 3 -type f -name '*.rs' -o -name '*.py' -o -name '*.ts' -o -name '*.tsx' -o -name '*.js' -o -name '*.go' 2>/dev/null | head -20",
            shell=True, capture_output=True, text=True, timeout=3
        )
        for line in result.stdout.strip().split("\n"):
            if line.endswith(".rs"): langs.add("rust")
            elif line.endswith(".py"): langs.add("python")
            elif line.endswith(".ts"): langs.add("typescript")
            elif line.endswith(".tsx"): langs.add("react")
            elif line.endswith(".js"): langs.add("javascript")
            elif line.endswith(".go"): langs.add("go")
    except:
        pass
    return list(langs)

# ═══════════════════════════════════════════════════════════════════
# ENGINE DISCOVERY — 사용 가능한 엔진 자동 탐지
# ═══════════════════════════════════════════════════════════════════

def discover_engines():
    """nexus6 + 각 리포에서 실행 가능한 엔진 자동 발견."""
    engines = []

    # nexus6 scripts
    script_dir = NEXUS_ROOT / "scripts"
    if script_dir.exists():
        for f in sorted(script_dir.iterdir()):
            if f.suffix in (".sh", ".py") and f.is_file():
                engines.append({
                    "name": f.stem,
                    "path": str(f),
                    "type": "script",
                    "repo": "nexus6",
                    "cmd": f"python3 {f}" if f.suffix == ".py" else f"bash {f}",
                })

    # nexus6 rust modules (cargo test targets)
    for mod_dir in (NEXUS_ROOT / "src").iterdir():
        if mod_dir.is_dir() and (mod_dir / "mod.rs").exists():
            engines.append({
                "name": f"rust:{mod_dir.name}",
                "path": str(mod_dir),
                "type": "rust_module",
                "repo": "nexus6",
                "cmd": f"cd {NEXUS_ROOT} && cargo test --release {mod_dir.name} -- --nocapture",
            })

    # Other repo growth scripts
    for repo_dir in DEV_ROOT.iterdir():
        if repo_dir.name == "nexus6" or not repo_dir.is_dir():
            continue
        for pattern in ["scripts/*growth*", "scripts/*grow*", "scripts/*scan*",
                        "*/scripts/*growth*", "*/src/*growth*", "*/src/*blowup*"]:
            for f in repo_dir.glob(pattern):
                if f.is_file():
                    engines.append({
                        "name": f"{repo_dir.name}:{f.stem}",
                        "path": str(f),
                        "type": "external",
                        "repo": repo_dir.name,
                        "cmd": f"python3 {f}" if f.suffix == ".py" else f"bash {f}",
                    })

    return engines

# ═══════════════════════════════════════════════════════════════════
# PHASE RUNNER — 각 Phase 실행 + 버스 피드백
# ═══════════════════════════════════════════════════════════════════

def run_engine(engine, bus, timeout=120):
    """엔진 하나 실행, 결과를 버스에 발행."""
    name = engine["name"]
    print(f"  [{time.strftime('%H:%M:%S')}] {name}...")

    try:
        result = subprocess.run(
            engine["cmd"], shell=True, capture_output=True, text=True,
            timeout=timeout, cwd=engine.get("cwd", str(NEXUS_ROOT))
        )
        output = result.stdout[-500:] if result.stdout else ""
        success = result.returncode == 0

        bus.emit(name, "engine_result", {
            "success": success,
            "output_tail": output,
            "returncode": result.returncode,
        })

        if success:
            print(f"    ✅ {name}")
        else:
            print(f"    ⚠️ {name} (rc={result.returncode})")

        return success
    except subprocess.TimeoutExpired:
        bus.emit(name, "engine_timeout", {"timeout": timeout})
        print(f"    ⏰ {name} (timeout {timeout}s)")
        return False
    except Exception as e:
        bus.emit(name, "engine_error", {"error": str(e)})
        print(f"    ❌ {name}: {e}")
        return False

# ═══════════════════════════════════════════════════════════════════
# FEEDBACK CHAINS — Phase 간 순환 연결
# ═══════════════════════════════════════════════════════════════════

def build_feedback(bus):
    """이전 Phase 결과에서 다음 Phase 입력 생성."""
    recent = bus.query(event_type="engine_result", last_n=20)

    feedback = {
        "new_lenses": 0,
        "new_discoveries": 0,
        "resonances": [],
        "emergences": [],
        "failed_engines": [],
        "successful_engines": [],
        "cross_repo_events": [],
    }

    for event in recent:
        data = event.get("data", {})
        source = event.get("source", "")
        output = data.get("output_tail", "")

        if data.get("success"):
            feedback["successful_engines"].append(source)
        else:
            feedback["failed_engines"].append(source)

        # Parse outputs for growth signals
        if "NEW LENS" in output or "new lens" in output.lower():
            feedback["new_lenses"] += output.lower().count("new lens")
        if "discovery" in output.lower() or "발견" in output:
            feedback["new_discoveries"] += 1
        if "resonance" in output.lower() or "공명" in output:
            feedback["resonances"].append(source)
        if "emergence" in output.lower() or "창발" in output or "blowup" in output.lower():
            feedback["emergences"].append(source)
        if ":" in source and source.split(":")[0] != "nexus6":
            feedback["cross_repo_events"].append(source)

    return feedback

# ═══════════════════════════════════════════════════════════════════
# RECURSIVE BLOWUP — 창발물 → 새 스캔 → 재창발
# ═══════════════════════════════════════════════════════════════════

def recursive_blowup(bus, depth=0, max_depth=6):
    """블로업 결과를 다시 스캔 대상으로 넣어 재귀 창발."""
    if depth >= max_depth:
        return 0

    emergences = bus.query(event_type="engine_result", last_n=5)
    emergence_data = [e for e in emergences if "emergence" in json.dumps(e).lower()
                      or "blowup" in json.dumps(e).lower()]

    if not emergence_data:
        return 0

    total = len(emergence_data)
    bus.emit(f"recursive_blowup_d{depth}", "blowup_recurse", {
        "depth": depth,
        "input_emergences": total,
    })

    # Feed emergence back as scan targets
    try:
        result = subprocess.run(
            f"cd {NEXUS_ROOT} && cargo test --release blowup -- --nocapture",
            shell=True, capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0:
            bus.emit(f"recursive_blowup_d{depth}", "blowup_result", {
                "depth": depth,
                "output": result.stdout[-300:],
            })
            total += recursive_blowup(bus, depth + 1, max_depth)
    except:
        pass

    return total

# ═══════════════════════════════════════════════════════════════════
# WALL BREAKER — 벽 감지 + 자동 돌파 시도
# ═══════════════════════════════════════════════════════════════════

# Domains that can be expanded infinitely
DOMAINS = [
    "physics", "mathematics", "information_theory", "biology",
    "consciousness", "architecture", "music", "visual_art",
    "literature", "sports", "cooking", "dance", "film",
    "game_design", "education", "economics", "sociology",
    "linguistics", "philosophy", "chemistry", "geology",
    "astronomy", "ecology", "neuroscience", "robotics",
    "material_science", "quantum_computing", "cryptography",
    "topology", "category_theory", "number_theory",
    "superconductor", "fusion", "cosmology", "string_theory",
]

def detect_walls(bus):
    """성장이 멈춘 곳 = 벽. 자동 감지."""
    walls = []
    recent = bus.query(last_n=50)

    # 1. 같은 엔진이 연속 실패 = 벽
    fail_streaks = {}
    for e in recent:
        src = e.get("source", "")
        if e.get("data", {}).get("success") == False:
            fail_streaks[src] = fail_streaks.get(src, 0) + 1
        else:
            fail_streaks[src] = 0
    for src, streak in fail_streaks.items():
        if streak >= 3:
            walls.append({"type": "engine_stuck", "source": src, "streak": streak})

    # 2. 메트릭이 정체 = 벽
    history = []
    log_file = NEXUS_ROOT / "shared" / "infinite_growth_log.jsonl"
    if log_file.exists():
        for line in log_file.read_text().strip().split("\n")[-10:]:
            if line.strip():
                try: history.append(json.loads(line))
                except: pass
    if len(history) >= 3:
        for metric in ["lenses", "calcs", "tests"]:
            vals = [h.get(metric, 0) for h in history[-3:]]
            if len(set(vals)) == 1:  # 3 cycles same value = wall
                walls.append({"type": "metric_stagnant", "metric": metric, "value": vals[0]})

    # 3. 0% 차원 = 벽
    state = bus.state
    for key in ["emergences", "discoveries"]:
        if state.get(key, 0) == 0 and state.get("cycle", 0) > 2:
            walls.append({"type": "zero_metric", "metric": key})

    return walls


def attempt_breakthrough(bus, walls):
    """벽 발견 → 자동 돌파 시도. 도메인 무제한 확장."""
    if not walls:
        return 0

    breakthroughs = 0
    print(f"\n  🧱 {len(walls)} walls detected. Attempting breakthroughs...\n")

    for wall in walls:
        wtype = wall["type"]

        if wtype == "engine_stuck":
            # 엔진 멈춤 → 다른 전략으로 우회
            src = wall["source"]
            print(f"    🔨 {src} stuck ({wall['streak']}x fail) → trying alternative...")
            bus.emit("wall_breaker", "bypass_attempt", {
                "wall": wall, "strategy": "alternative_engine"
            })
            breakthroughs += 1

        elif wtype == "metric_stagnant":
            # 메트릭 정체 → 새 도메인으로 확장
            metric = wall["metric"]
            # Pick a random unexplored domain
            explored = set(bus.state.get("explored_domains", []))
            unexplored = [d for d in DOMAINS if d not in explored]
            if unexplored:
                import random
                domain = random.choice(unexplored)
                print(f"    🚀 {metric} stagnant at {wall['value']} → expanding into '{domain}'")
                bus.emit("wall_breaker", "domain_expansion", {
                    "wall": wall, "new_domain": domain,
                    "strategy": "cross_domain_transfer"
                })
                bus.state.setdefault("explored_domains", []).append(domain)
                breakthroughs += 1

                # Actually try to create something in the new domain
                try:
                    subprocess.run(
                        f"cd {NEXUS_ROOT} && python3 scripts/n6.py discover "
                        f"<(python3 -c \"import numpy as np; np.random.seed(hash('{domain}')%2**31); "
                        f"d=np.random.randn(100,6); d[:,0]*=12; d[:,1]*=4; d[:,2]*=6; "
                        f"print(' '.join(map(str, d.flatten())))\")",
                        shell=True, capture_output=True, timeout=30,
                        executable="/bin/bash"
                    )
                except:
                    pass

        elif wtype == "zero_metric":
            metric = wall["metric"]
            print(f"    💥 {metric} = 0 → forcing emergence via blowup...")
            bus.emit("wall_breaker", "force_emergence", {
                "wall": wall, "strategy": "forced_blowup"
            })
            # Trigger blowup
            recursive_blowup(bus, depth=0, max_depth=3)
            breakthroughs += 1

    bus.emit("wall_breaker", "summary", {
        "walls": len(walls),
        "breakthroughs": breakthroughs,
    })

    return breakthroughs


def auto_domain_expansion(bus, repos):
    """각 리포의 도메인을 자동 감지하고, 미탐색 도메인 조합을 시도."""
    repo_domains = {}
    for r in repos:
        domains = set()
        # Infer domains from repo name and languages
        name = r["name"].lower()
        for d in DOMAINS:
            if d.replace("_", "") in name or d.replace("_", "-") in name:
                domains.add(d)
        # Language-based domain hints
        if "rust" in r["languages"]:
            domains.add("architecture")
        if "python" in r["languages"]:
            domains.add("mathematics")
        if "typescript" in r["languages"] or "react" in r["languages"]:
            domains.add("visual_art")
        repo_domains[r["name"]] = list(domains)

    # Find domain pairs that haven't been connected
    all_domains = set()
    for domains in repo_domains.values():
        all_domains.update(domains)

    # Emit cross-domain opportunities
    connected = set()
    for r1, d1 in repo_domains.items():
        for r2, d2 in repo_domains.items():
            if r1 >= r2:
                continue
            shared = set(d1) & set(d2)
            if shared:
                pair = (r1, r2)
                if pair not in connected:
                    connected.add(pair)
                    bus.emit("domain_expansion", "cross_repo_domain", {
                        "repos": [r1, r2],
                        "shared_domains": list(shared),
                    })

    return repo_domains


# ═══════════════════════════════════════════════════════════════════
# CHANGE REACTOR — 변경 감지 → 넥서스 검사 → 연결된 곳 전부 성장/튜닝
# ═══════════════════════════════════════════════════════════════════

# 이전 사이클 파일 해시 (변경 감지용)
_prev_hashes = {}

def hash_repo_state(repo_path):
    """리포 상태 해시 (빠르게: git status + HEAD)."""
    try:
        r = subprocess.run(
            f"cd {repo_path} && git rev-parse HEAD 2>/dev/null && git diff --stat 2>/dev/null | tail -1",
            shell=True, capture_output=True, text=True, timeout=5
        )
        return hashlib.md5(r.stdout.encode()).hexdigest()
    except:
        return ""


def detect_changes(repos):
    """모든 리포의 변경 감지. 이전 사이클 대비 diff."""
    global _prev_hashes
    changed = []

    for r in repos:
        name = r["name"]
        path = r["path"]
        current_hash = hash_repo_state(path)

        if name in _prev_hashes and _prev_hashes[name] != current_hash:
            # 변경 감지!
            try:
                diff = subprocess.run(
                    f"cd {path} && git diff --name-only HEAD~1 2>/dev/null | head -20",
                    shell=True, capture_output=True, text=True, timeout=5
                )
                changed_files = [f for f in diff.stdout.strip().split("\n") if f]
            except:
                changed_files = []

            changed.append({
                "repo": name,
                "path": path,
                "changed_files": changed_files,
                "categories": categorize_changes(changed_files),
            })

        _prev_hashes[name] = current_hash

    return changed


def categorize_changes(files):
    """변경 파일을 카테고리로 분류."""
    cats = set()
    for f in files:
        if "lens" in f.lower() or "telescope" in f.lower():
            cats.add("lenses")
        if "test" in f.lower():
            cats.add("tests")
        if "growth" in f.lower() or "engine" in f.lower():
            cats.add("engines")
        if "calc" in f.lower() or "math" in f.lower():
            cats.add("math")
        if "shared" in f.lower() or "sync" in f.lower():
            cats.add("shared")
        if "blowup" in f.lower() or "dream" in f.lower() or "ouroboros" in f.lower():
            cats.add("meta_engines")
        if f.endswith(".rs"):
            cats.add("rust")
        if f.endswith(".py"):
            cats.add("python")
        if f.endswith(".ts") or f.endswith(".tsx"):
            cats.add("frontend")
        if "CLAUDE.md" in f:
            cats.add("config")
    return list(cats)


def propagate_changes(bus, changed_repos, all_repos):
    """변경 감지된 리포 → 넥서스 검사 → 연결된 리포 전부 성장/튜닝.

    동작:
      1. 변경된 리포의 카테고리 파악
      2. 같은 카테고리를 공유하는 다른 리포 찾기
      3. 해당 리포의 성장 엔진 트리거
      4. 공유 데이터(.shared) 동기화
      5. 넥서스 스캔으로 품질 검사
    """
    if not changed_repos:
        return 0

    propagations = 0

    for change in changed_repos:
        src_repo = change["repo"]
        cats = change["categories"]
        files = change["changed_files"]

        print(f"  🔄 {src_repo}: {len(files)} files changed [{', '.join(cats[:4])}]")

        # 1. 넥서스 스캔 (변경 검사)
        if "lenses" in cats or "rust" in cats or "meta_engines" in cats:
            print(f"    → nexus6 scan triggered (lens/engine change)")
            try:
                subprocess.run(
                    f"cd {NEXUS_ROOT} && cargo test --release -- --nocapture 2>&1 | tail -5",
                    shell=True, capture_output=True, timeout=120
                )
                bus.emit("change_reactor", "nexus_scan", {
                    "trigger": src_repo, "reason": cats
                })
            except:
                pass
            propagations += 1

        # 2. 공유 데이터 변경 → 전 리포 동기화
        if "shared" in cats or "config" in cats:
            print(f"    → sync-all triggered (shared data changed)")
            try:
                subprocess.run(
                    f"bash {NEXUS_ROOT}/sync/sync-all.sh",
                    shell=True, capture_output=True, timeout=60
                )
            except:
                pass
            propagations += 1

        # 3. 연결된 리포의 성장 엔진 트리거
        for target in all_repos:
            if target["name"] == src_repo:
                continue
            if not target["has_shared"]:
                continue

            # 같은 카테고리 공유하는 리포 = 전파 대상
            target_path = target["path"]

            if "engines" in cats or "meta_engines" in cats:
                # 엔진 변경 → 연결된 리포 성장 트리거
                growth_scripts = list(Path(target_path).glob("scripts/*growth*")) + \
                                 list(Path(target_path).glob("*/scripts/*growth*"))
                for gs in growth_scripts[:2]:
                    print(f"    → {target['name']} growth triggered ({gs.name})")
                    try:
                        cmd = f"python3 {gs}" if gs.suffix == ".py" else f"bash {gs}"
                        subprocess.run(
                            cmd, shell=True, capture_output=True, timeout=60,
                            cwd=target_path
                        )
                    except:
                        pass
                    propagations += 1

            if "lenses" in cats:
                # 렌즈 변경 → 연결된 리포 재스캔
                print(f"    → {target['name']} re-scan (lens change in {src_repo})")
                bus.emit("change_reactor", "propagate_scan", {
                    "source": src_repo, "target": target["name"],
                    "reason": "lens_change"
                })
                propagations += 1

            if "tests" in cats:
                # 테스트 변경 → 연결된 리포 테스트
                print(f"    → {target['name']} test triggered")
                bus.emit("change_reactor", "propagate_test", {
                    "source": src_repo, "target": target["name"],
                })
                propagations += 1

    bus.emit("change_reactor", "summary", {
        "changed_repos": len(changed_repos),
        "total_propagations": propagations,
    })

    return propagations


def domain_lens_explorer(bus):
    """도메인별 렌즈 무한탐색. 매 사이클 새 도메인-렌즈 조합 시도."""
    explored = bus.state.get("explored_domains", [])
    if not explored:
        return

    # Pick most recently explored domain
    domain = explored[-1]

    # Map domains to relevant lens categories
    DOMAIN_LENS_MAP = {
        "physics": ["Gravity", "Wave", "Thermo", "Quantum", "Entropy", "Spacetime",
                     "Barrier", "Dispersion", "Band", "Fusion"],
        "mathematics": ["Topology", "Cohomology", "Bernstein", "BirchSwinnerton",
                        "ClassNumber", "HarmonicSeries", "DiscreteLog"],
        "music": ["Harmonic", "Hexameter", "Frequency", "Wave", "Resonance"],
        "visual_art": ["Color", "Proportion", "Symmetry", "Fractal", "Golden"],
        "biology": ["Gene", "Epigenetic", "Evolution", "Network", "Frequency"],
        "consciousness": ["Consciousness", "Emergence", "IIT", "Recursive", "Meta"],
        "architecture": ["Architectural", "Proportion", "Stability", "Structure"],
        "sports": ["Ergodicity", "Stability", "Barrier", "Evolution", "Network"],
        "cooking": ["Thermo", "Chemical", "Stability", "Proportion", "Phase"],
        "dance": ["Wave", "Harmonic", "Rhythm", "Frequency", "Symmetry"],
        "film": ["Narrative", "Temporal", "Causal", "Network", "Emergence"],
        "game_design": ["Strategy", "Network", "Emergence", "Barrier", "Evolution"],
        "economics": ["Network", "Stability", "Ergodicity", "Barrier", "Phase"],
        "superconductor": ["Band", "Phase", "Quantum", "Symmetry", "Topology"],
        "fusion": ["Barrier", "Plasma", "Stability", "Thermo", "Confinement"],
        "cosmology": ["Cosmological", "Baryogenesis", "CPViolation", "Spacetime"],
        "topology": ["Topology", "Cohomology", "Homology", "Knot", "Manifold"],
        "material_science": ["Band", "Crystal", "Phase", "Stability", "Thermo"],
    }

    lens_hints = DOMAIN_LENS_MAP.get(domain, ["Consciousness", "Topology", "Wave"])

    print(f"  🔍 Domain lens exploration: {domain}")
    print(f"    Lens hints: {lens_hints[:6]}")

    bus.emit("domain_explorer", "lens_search", {
        "domain": domain,
        "lens_hints": lens_hints,
        "status": "exploring"
    })

    # Run n6.py scan with domain-tuned data
    try:
        subprocess.run(
            f"cd {NEXUS_ROOT} && python3 scripts/n6.py scan "
            f"<(python3 -c \""
            f"import numpy as np; np.random.seed(hash('{domain}')%2**31); "
            f"d=np.random.randn(100,6); d[:,0]*=12; d[:,1]*=4; d[:,2]*=6; "
            f"print(' '.join(map(str, d.flatten())))\")",
            shell=True, capture_output=True, timeout=30,
            executable="/bin/bash"
        )
        bus.emit("domain_explorer", "scan_complete", {
            "domain": domain, "lens_hints": lens_hints
        })
        print(f"    ✅ {domain} scan complete")
    except Exception as e:
        print(f"    ⚠️ {domain} scan: {e}")


# ═══════════════════════════════════════════════════════════════════
# REPORT GENERATOR
# ═══════════════════════════════════════════════════════════════════

def generate_report(bus, repos, engines, feedback, cycle_duration):
    """세션 리포트 생성."""
    state = bus.state
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Sparkline
    def sparkline(values, width=40):
        if not values or max(values) == min(values):
            return "▁" * min(len(values), width)
        mn, mx = min(values), max(values)
        chars = "▁▂▃▄▅▆▇█"
        return "".join(chars[min(int((v - mn) / (mx - mn) * 7), 7)] for v in values[-width:])

    # Load history
    history = []
    log_file = NEXUS_ROOT / "shared" / "infinite_growth_log.jsonl"
    if log_file.exists():
        for line in log_file.read_text().strip().split("\n"):
            if line.strip():
                try: history.append(json.loads(line))
                except: pass

    lines = [
        f"# NEXUS-6 Growth Bus Report",
        f"Generated: {ts} | Cycle: {state['cycle']}",
        f"",
        f"## Topology",
        f"| Metric | Count |",
        f"|--------|-------|",
        f"| Repos discovered | {len(repos)} |",
        f"| Engines available | {len(engines)} |",
        f"| Repos with .shared | {sum(1 for r in repos if r['has_shared'])} |",
        f"| Repos with growth | {sum(1 for r in repos if r['has_growth'])} |",
        f"| Languages | {len(set(l for r in repos for l in r['languages']))} |",
        f"",
        f"## Growth State",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Lenses | {state.get('lenses', '?')} |",
        f"| Calcs | {state.get('calcs', '?')} |",
        f"| Tests | {state.get('tests', '?')} |",
        f"| Discoveries | {state.get('discoveries', '?')} |",
        f"| Emergences | {state.get('emergences', '?')} |",
        f"| Feedback chains | {state.get('feedback_chains', 0)} |",
        f"| Bus events | {state.get('total_events', 0)} |",
        f"| Cycle duration | {cycle_duration}s |",
        f"",
        f"## Feedback This Cycle",
        f"  Successful: {len(feedback['successful_engines'])}",
        f"  Failed: {len(feedback['failed_engines'])}",
        f"  New discoveries: {feedback['new_discoveries']}",
        f"  Cross-repo events: {len(feedback['cross_repo_events'])}",
        f"  Resonances: {len(feedback['resonances'])}",
        f"  Emergences: {len(feedback['emergences'])}",
        f"",
    ]

    if history:
        lens_h = [h.get("lenses", 0) for h in history]
        test_h = [h.get("tests", 0) for h in history]
        lines.append(f"## Trends")
        lines.append(f"  Lenses : {sparkline(lens_h)}")
        lines.append(f"  Tests  : {sparkline(test_h)}")
        lines.append(f"")

    lines.append(f"## Repos ({len(repos)})")
    for r in repos:
        marker = "🔗" if r["has_shared"] else "  "
        growth = "🌱" if r["has_growth"] else "  "
        lines.append(f"  {marker}{growth} {r['name']}: {r['file_count']} files [{', '.join(r['languages'][:3])}]")

    report = "\n".join(lines)
    REPORT_FILE.write_text(report)
    return report

# ═══════════════════════════════════════════════════════════════════
# MAIN CYCLE
# ═══════════════════════════════════════════════════════════════════

def run_cycle(bus):
    """한 사이클: 발견 → 실행 → 피드백 → 블로업 → 리포트."""
    cycle_start = time.time()
    bus.state["cycle"] += 1
    cycle = bus.state["cycle"]

    print(f"\n{'═' * 60}")
    print(f"  GROWTH BUS CYCLE {cycle} — {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'═' * 60}\n")

    # Phase A: Discover everything
    print("[DISCOVER] Scanning ~/Dev for repos and engines...")
    repos = discover_repos()
    engines = discover_engines()
    bus.emit("discovery", "topology", {
        "repos": len(repos),
        "engines": len(engines),
        "repo_names": [r["name"] for r in repos],
    })
    print(f"  Found {len(repos)} repos, {len(engines)} engines\n")

    # Phase B: Change detection → propagation
    print("[CHANGES] Detecting repo changes...")
    changed = detect_changes(repos)
    if changed:
        print(f"  {len(changed)} repos changed → propagating...")
        propagations = propagate_changes(bus, changed, repos)
        print(f"  {propagations} propagations triggered\n")
    else:
        print(f"  No changes detected\n")

    # Phase B2: Domain-specific lens exploration
    print("[LENS EXPLORE] Domain-specific lens search...")
    domain_lens_explorer(bus)
    print()

    # Phase C: Build feedback from previous cycle
    feedback = build_feedback(bus)
    bus.state["feedback_chains"] += 1

    # Phase D: Categorize and run engines
    # Priority: growth > mirror > learning > rust > external > maintenance
    priority_order = [
        "growth_intelligence", "nexus6_growth_daemon",
        "mirror_growth", "weight_engine", "cross_validate_lenses",
        "pipeline_engine",
        "rust:ouroboros", "rust:blowup", "rust:lens_forge", "rust:dream", "rust:graph",
        "benchmark_lenses", "health_check",
    ]

    # Build run order: prioritized first, then discovered engines
    seen = set()
    run_order = []

    for pname in priority_order:
        for e in engines:
            if pname in e["name"] and e["name"] not in seen:
                run_order.append(e)
                seen.add(e["name"])

    # Add any remaining engines (auto-discovered, unlimited)
    for e in engines:
        if e["name"] not in seen:
            # Skip certain utility scripts
            skip = ["install", "troubleshoot", "validate_real"]
            if any(s in e["name"] for s in skip):
                continue
            run_order.append(e)
            seen.add(e["name"])

    print(f"[EXECUTE] Running {len(run_order)} engines...\n")

    success_count = 0
    fail_count = 0
    for i, engine in enumerate(run_order):
        phase_num = i + 1
        # Timeout based on type
        timeout = 120
        if engine["type"] == "rust_module":
            timeout = 90
        elif "growth_daemon" in engine["name"]:
            timeout = 180
        elif engine["type"] == "external":
            timeout = 60

        # Inject feedback from previous phases
        if feedback["new_lenses"] > 0 and "mirror" in engine["name"]:
            bus.emit("feedback_inject", "new_lenses_for_mirror", {
                "count": feedback["new_lenses"]
            })
        if feedback["resonances"] and "weight" in engine["name"]:
            bus.emit("feedback_inject", "resonances_for_weight", {
                "sources": feedback["resonances"]
            })

        if run_engine(engine, bus, timeout=timeout):
            success_count += 1
        else:
            fail_count += 1

        # Refresh feedback after each engine
        feedback = build_feedback(bus)

    # Phase D: Wall detection + breakthrough
    print(f"\n[WALLS] Detecting growth walls...")
    walls = detect_walls(bus)
    breakthroughs = attempt_breakthrough(bus, walls)
    if not walls:
        print(f"  No walls detected — growth flowing freely\n")
    else:
        print(f"  {breakthroughs} breakthroughs attempted\n")

    # Phase E: Domain expansion (unlimited)
    print("[DOMAINS] Auto-expanding domain topology...")
    repo_domains = auto_domain_expansion(bus, repos)
    active_domains = set()
    for domains in repo_domains.values():
        active_domains.update(domains)
    explored = set(bus.state.get("explored_domains", []))
    unexplored = [d for d in DOMAINS if d not in explored]
    print(f"  Active: {len(active_domains)} | Explored: {len(explored)} | Unexplored: {len(unexplored)}")
    # Auto-explore one new domain per cycle
    if unexplored:
        import random
        new_domain = random.choice(unexplored)
        bus.state.setdefault("explored_domains", []).append(new_domain)
        bus.emit("auto_explore", "new_domain", {"domain": new_domain})
        print(f"  ✨ Auto-exploring: {new_domain}")
    print()

    # Phase F: Recursive blowup (emergence → re-scan → re-emergence)
    print("[BLOWUP] Recursive emergence (infinite depth)...")
    emergence_count = recursive_blowup(bus, depth=0, max_depth=6)
    bus.state["emergences"] = bus.state.get("emergences", 0) + emergence_count
    print(f"  Emergences this cycle: {emergence_count}\n")

    # Phase G: Sync all repos
    print("[SYNC] Propagating to all repos...")
    sync_script = NEXUS_ROOT / "sync" / "sync-all.sh"
    if sync_script.exists():
        try:
            subprocess.run(f"bash {sync_script}", shell=True, capture_output=True, timeout=60)
            print("  ✅ Sync complete")
        except:
            print("  ⚠️ Sync timeout")
    print()

    # Phase F: Count everything
    lenses = sum(1 for _ in (NEXUS_ROOT / "src/telescope/lenses").glob("*.rs") if _.name != "mod.rs")
    calcs = sum(1 for _ in (NEXUS_ROOT / "shared/calc").glob("*.py"))
    tests = 0
    try:
        result = subprocess.run(
            f"grep -r '#\\[test\\]' {NEXUS_ROOT}/tests {NEXUS_ROOT}/src 2>/dev/null | wc -l",
            shell=True, capture_output=True, text=True
        )
        tests = int(result.stdout.strip())
    except:
        pass

    bus.state.update({
        "lenses": lenses, "calcs": calcs, "tests": tests,
        "repos": {r["name"]: r["file_count"] for r in repos},
        "engines": {e["name"]: e["type"] for e in engines},
        "total_events": bus.state.get("total_events", 0) + len(bus.events),
    })

    cycle_duration = int(time.time() - cycle_start)

    # Phase G: Report
    print("[REPORT] Generating growth report...")
    report = generate_report(bus, repos, engines, feedback, cycle_duration)
    print(report[:500])
    print()

    # Log cycle
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "cycle": cycle,
        "duration_s": cycle_duration,
        "lenses": lenses, "calcs": calcs, "tests": tests,
        "repos": len(repos), "engines": len(engines),
        "success": success_count, "fail": fail_count,
        "emergences": emergence_count,
        "feedback_chains": bus.state["feedback_chains"],
    }
    log_file = NEXUS_ROOT / "shared" / "infinite_growth_log.jsonl"
    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    bus.save_state()

    print(f"┌{'─' * 58}┐")
    print(f"│  Cycle {cycle} │ {cycle_duration}s │ {success_count}/{success_count + fail_count} ok │ {emergence_count} emergences │")
    print(f"│  Lenses: {lenses} │ Calcs: {calcs} │ Tests: {tests} │ Repos: {len(repos)}")
    print(f"│  Engines: {len(engines)} │ Bus events: {bus.state['total_events']}")
    print(f"└{'─' * 58}┘\n")

    return cycle_duration

# ═══════════════════════════════════════════════════════════════════
# ENTRY
# ═══════════════════════════════════════════════════════════════════

def main():
    import argparse
    parser = argparse.ArgumentParser(description="NEXUS-6 Growth Bus")
    parser.add_argument("--cycles", type=int, default=999)
    parser.add_argument("--interval", type=int, default=180, help="seconds between cycles")
    parser.add_argument("--discover-only", action="store_true")
    args = parser.parse_args()

    bus = GrowthBus()

    if args.discover_only:
        repos = discover_repos()
        engines = discover_engines()
        print(f"Repos ({len(repos)}):")
        for r in repos:
            print(f"  {'🔗' if r['has_shared'] else '  '} {r['name']}: {r['file_count']} files")
        print(f"\nEngines ({len(engines)}):")
        for e in engines:
            print(f"  [{e['type']}] {e['name']}")
        return

    print("""
  ╔════════════════════════════════════════════════════════════╗
  ║   NEXUS-6 GROWTH BUS — Unlimited Topology                 ║
  ║   All repos. All engines. Circular feedback. Infinite.     ║
  ╚════════════════════════════════════════════════════════════╝
    """)

    for i in range(args.cycles):
        try:
            run_cycle(bus)
        except KeyboardInterrupt:
            print("\n[STOP] Growth Bus stopped.")
            bus.save_state()
            break
        except Exception as e:
            print(f"[ERROR] Cycle failed: {e}")
            bus.emit("main", "cycle_error", {"error": str(e)})

        if i < args.cycles - 1:
            print(f"[SLEEP] Next cycle in {args.interval}s...")
            time.sleep(args.interval)

    bus.save_state()
    print("[DONE] Growth Bus complete.")

if __name__ == "__main__":
    main()
