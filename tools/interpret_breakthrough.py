"""사이클 결과 JSON + discovery_log → 규칙 후보 md. 로컬만."""
import json
from pathlib import Path


def load_and_rank(
    breakthrough_json: Path, discovery_log: Path, min_strength: float = 0.5
) -> list[dict]:
    data = json.loads(Path(breakthrough_json).read_text(encoding="utf-8"))
    patterns = data.get("converged_patterns", [])
    notes_by_pattern: dict[str, str] = {}
    if Path(discovery_log).exists():
        for line in Path(discovery_log).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            pname = rec.get("pattern")
            if pname and "note" in rec:
                notes_by_pattern[pname] = rec["note"]
    filtered = [p for p in patterns if p.get("strength", 0) >= min_strength]
    filtered.sort(key=lambda p: p.get("strength", 0), reverse=True)
    for p in filtered:
        if p["name"] in notes_by_pattern:
            p["note"] = notes_by_pattern[p["name"]]
    return filtered


_RULE_TEMPLATES = {
    "reuse_dominance": (
        "동일 (tool, args) 호출이 세션 내 반복될 경우 두 번째 호출부터 "
        "결과를 재인용하거나 더 좁은 범위(Grep/offset)로 대체하라."
    ),
    "size_concentration": (
        "Read/Bash 결과가 큰 바이트에 집중되는 경향 확인. 파일 크기 미지 시 "
        "먼저 head 100줄 또는 Grep으로 좁힌 뒤 필요 영역만 offset으로 읽어라."
    ),
    "session_reexploration": (
        "세션 시작 직후 이전 세션에서 이미 열었던 파일을 재Read하는 패턴. "
        "SessionStart에서 메모리/핸드오프 파일을 먼저 확인하고 중복 Read를 피하라."
    ),
}

_counter = {"n": 0}


def translate_to_rule(pattern: dict, source_hypothesis: str) -> dict:
    _counter["n"] += 1
    rid = f"R{_counter['n']}"
    name = pattern.get("name", "unknown")
    text = _RULE_TEMPLATES.get(
        name, f"(템플릿 미등록) 패턴 {name}에 대해 사람 검토 필요."
    )
    consts = pattern.get("constants_matched") or []
    rationale = (
        f"pattern={name} strength={pattern.get('strength', 0):.2f} "
        f"constants={','.join(consts) or '-'}"
    )
    if "note" in pattern:
        rationale += f" note={pattern['note']}"
    return {
        "id": rid,
        "text": text,
        "source": source_hypothesis,
        "rationale": rationale,
    }


def reset_rule_counter():
    _counter["n"] = 0
