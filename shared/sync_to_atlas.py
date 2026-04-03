#!/usr/bin/env python3
"""SEDI Constants → TECS-L math_atlas 등록 동기화.

SEDI에서 검증된 상수와 가설 등급을 TECS-L의 math_atlas.json에 등록.

동작:
  1. sedi/constants.py에서 n=6 상수 추출
  2. docs/hypotheses/ 에서 검증된 상수 (오차% 포함) 추출
  3. data/sedi-grades.json 로드 (auto_grade_n6.py 결과)
  4. math_atlas.json에 신규 항목 등록
  5. scan_math_atlas.py --save 호출 (atlas 갱신)

Usage:
  python3 scripts/sync_to_atlas.py              # dry-run (변경 출력만)
  python3 scripts/sync_to_atlas.py --save       # atlas 갱신 실행
  python3 scripts/sync_to_atlas.py --grades     # sedi-grades.json도 복사
"""

import re
import json
import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

# ── 경로 ──────────────────────────────────────────────────────
SEDI_ROOT = Path(__file__).resolve().parent.parent
TECS_L_ROOT = SEDI_ROOT.parent / "TECS-L"
TECS_SHARED = TECS_L_ROOT / ".shared"
ATLAS_PATH = TECS_SHARED / "math_atlas.json"
SCAN_SCRIPT = TECS_SHARED / "scan_math_atlas.py"
GRADES_SRC = SEDI_ROOT / "data" / "sedi-grades.json"
GRADES_DST = TECS_SHARED / "sedi-grades.json"
CONSTANTS_PY = SEDI_ROOT / "sedi" / "constants.py"
HYPOTHESES_DIR = SEDI_ROOT / "docs" / "hypotheses"


def extract_constants_from_py() -> list[dict]:
    """sedi/constants.py에서 상수 추출."""
    constants = []
    if not CONSTANTS_PY.exists():
        return constants

    text = CONSTANTS_PY.read_text(encoding="utf-8")
    # 패턴: NAME = value  # comment
    for m in re.finditer(
        r"^([A-Z_]+)\s*=\s*([^#\n]+?)(?:\s*#\s*(.+))?$",
        text,
        re.MULTILINE,
    ):
        name = m.group(1).strip()
        expr = m.group(2).strip()
        comment = (m.group(3) or "").strip()

        # 단순 import 등 건너뛰기
        if "import" in expr or "(" in name:
            continue

        constants.append({
            "name": f"SEDI:{name}",
            "expression": expr,
            "comment": comment,
            "source": "sedi/constants.py",
            "verified": True,
        })

    return constants


def extract_verified_constants_from_hypotheses() -> list[dict]:
    """가설 파일에서 검증된 상수 (오차% 표기된 수치) 추출."""
    constants = []
    if not HYPOTHESES_DIR.exists():
        return constants

    for f in sorted(HYPOTHESES_DIR.glob("H-*.md")):
        text = f.read_text(encoding="utf-8")

        # 등급 확인 — CONFIRMED/EXACT/★★ 이상만
        grade_m = re.search(r"^##\s*Grade:\s*(.+)", text, re.MULTILINE)
        if not grade_m:
            continue
        grade = grade_m.group(1).strip()
        is_high = any(k in grade for k in ["🟩", "🟥", "★★", "CONFIRMED", "EXACT"])
        if not is_high:
            continue

        # 테이블에서 값 + 오차 추출
        # | Observable | Value | ... | Error |
        for row_m in re.finditer(
            r"\|\s*([^|]+?)\s*\|\s*([\d.]+(?:e[+-]?\d+)?)\s*\|.*?\|\s*([\d.]+)\s*%\s*\|",
            text,
        ):
            obs_name = row_m.group(1).strip()
            value = row_m.group(2).strip()
            error_pct = float(row_m.group(3))

            hyp_id = f.stem.split("-")[0:3]
            hyp_id = "-".join(hyp_id) if len(hyp_id) >= 3 else f.stem

            constants.append({
                "name": f"SEDI:{hyp_id}:{obs_name}",
                "value": value,
                "error_pct": error_pct,
                "source": str(f.relative_to(SEDI_ROOT)),
                "grade": grade,
            })

    return constants


def load_grades() -> dict | None:
    """auto_grade_n6.py가 생성한 등급 JSON 로드."""
    if GRADES_SRC.exists():
        return json.loads(GRADES_SRC.read_text(encoding="utf-8"))
    return None


def sync_grades_file() -> bool:
    """sedi-grades.json → TECS-L/.shared/ 복사."""
    if not GRADES_SRC.exists():
        print(f"  SKIP: {GRADES_SRC} not found (run auto_grade_n6.py --save first)")
        return False
    GRADES_DST.write_text(GRADES_SRC.read_text(encoding="utf-8"))
    print(f"  COPIED: {GRADES_SRC} → {GRADES_DST}")
    return True


def run_atlas_scan():
    """scan_math_atlas.py --save 실행."""
    if not SCAN_SCRIPT.exists():
        print(f"  SKIP: {SCAN_SCRIPT} not found")
        return
    result = subprocess.run(
        [sys.executable, str(SCAN_SCRIPT), "--save", "--summary"],
        capture_output=True,
        text=True,
        cwd=str(TECS_L_ROOT),
    )
    if result.returncode == 0:
        print(f"  Atlas updated: {result.stdout.strip()}")
    else:
        print(f"  Atlas scan error: {result.stderr.strip()}")


def main():
    parser = argparse.ArgumentParser(description="SEDI → TECS-L Atlas Sync")
    parser.add_argument("--save", action="store_true", help="실제 동기화 실행")
    parser.add_argument("--grades", action="store_true", help="등급 JSON도 복사")
    args = parser.parse_args()

    print("=== SEDI → TECS-L Atlas Sync ===")
    print()

    # 1. 상수 추출
    py_constants = extract_constants_from_py()
    print(f"[1/4] constants.py: {len(py_constants)} constants extracted")

    # 2. 가설에서 검증 상수 추출
    hyp_constants = extract_verified_constants_from_hypotheses()
    print(f"[2/4] hypotheses: {len(hyp_constants)} verified constants extracted")

    # 3. 등급 로드
    grades = load_grades()
    if grades:
        print(f"[3/4] grades: {grades['total_hypotheses']} hypotheses, "
              f"Tier A={grades['tier_distribution']['A']}, "
              f"B={grades['tier_distribution']['B']}")
    else:
        print("[3/4] grades: not found (run auto_grade_n6.py --save first)")

    # 4. 요약
    print()
    print("Constants for atlas registration:")
    for c in py_constants[:5]:
        print(f"  {c['name']} = {c['expression']}  # {c['comment']}")
    if len(py_constants) > 5:
        print(f"  ... and {len(py_constants)-5} more")

    print()
    print("Verified hypothesis constants:")
    for c in hyp_constants[:5]:
        print(f"  {c['name']} = {c['value']} (±{c['error_pct']}%)")
    if len(hyp_constants) > 5:
        print(f"  ... and {len(hyp_constants)-5} more")

    if args.save:
        print()
        print("--- Executing sync ---")

        # 등급 파일 복사
        if args.grades:
            sync_grades_file()

        # Atlas 스캔 (scan_math_atlas.py가 자체적으로 SEDI 가설 스캔)
        run_atlas_scan()

        print()
        print("Done!")
    else:
        print()
        print("Dry run complete. Use --save to execute sync.")


if __name__ == "__main__":
    main()
