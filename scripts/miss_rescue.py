#!/usr/bin/env python3
"""
miss_rescue.py — MISS 엔트리 구출 스크립트
MISS 엔트리를 확장 n=6 표현식으로 재검사하여
EXACT/CLOSE/NEAR로 승격 가능한 항목을 발굴한다.
"""

import json
import math
from collections import defaultdict
from pathlib import Path

LOG_PATH = Path(__file__).resolve().parent.parent / "shared" / "discovery_log.jsonl"

# ═══════════════════════════════════════════════════
# n=6 타겟 사전: expression_name → numeric_value
# 모든 매치 대상을 미리 계산하여 딕셔너리에 등록
# ═══════════════════════════════════════════════════

TARGETS = {}

def _reg(name, val):
    """타겟 등록 (유한한 값만)"""
    if isinstance(val, (int, float)) and math.isfinite(val):
        TARGETS[name] = val

# 기본 7상수
_n, _sigma, _phi, _tau, _sopfr, _mu, _J2 = 6, 12, 2, 4, 5, 1, 24

BASICS = {
    "n": _n, "sigma": _sigma, "phi": _phi, "tau": _tau,
    "sopfr": _sopfr, "mu": _mu, "J2": _J2,
}

# 모든 쌍 산술
names = list(BASICS.keys())
vals = list(BASICS.values())

for i, (na, va) in enumerate(zip(names, vals)):
    _reg(na, va)
    for j, (nb, vb) in enumerate(zip(names, vals)):
        if i != j:
            _reg(f"{na}+{nb}", va + vb)
            _reg(f"{na}-{nb}", va - vb)
            _reg(f"{na}*{nb}", va * vb)
            if vb != 0:
                _reg(f"{na}/{nb}", va / vb)
            if va > 0 and -20 < vb < 20:
                _reg(f"{na}^{nb}", va ** vb)

# 삼중 곱 (a*b*c) 주요 조합
for i, (na, va) in enumerate(zip(names, vals)):
    for j, (nb, vb) in enumerate(zip(names, vals)):
        if j <= i: continue
        for k, (nc, vc) in enumerate(zip(names, vals)):
            if k <= j: continue
            _reg(f"{na}*{nb}*{nc}", va * vb * vc)

# 유도 상수
derived = {
    "sigma-phi": 10, "sigma-tau": 8, "sigma-mu": 11,
    "sigma-sopfr": 7, "n/phi": 3, "J2-tau": 20,
    "J2-n": 18, "J2+tau": 28,
}
for dn, dv in derived.items():
    _reg(dn, dv)
    for na, va in BASICS.items():
        _reg(f"({dn})*{na}", dv * va)
        if va != 0:
            _reg(f"({dn})/{na}", dv / va)
        _reg(f"{na}*({dn})", va * dv)
        if dv != 0:
            _reg(f"{na}/({dn})", va / dv)
        if dv > 0 and 0 < va < 10:
            _reg(f"({dn})^{na}", dv ** va)

# 유도 x 유도
for dn1, dv1 in derived.items():
    for dn2, dv2 in derived.items():
        if dn1 < dn2:
            _reg(f"({dn1})*({dn2})", dv1 * dv2)
            if dv2 != 0:
                _reg(f"({dn1})/({dn2})", dv1 / dv2)

# 거듭제곱 확장
for na, va in list(BASICS.items()) + list(derived.items()):
    if va > 0:
        for exp in [2, 3, 4, 5, 6]:
            _reg(f"({na})^{exp}", va ** exp)
        _reg(f"sqrt({na})", math.sqrt(va))
        _reg(f"cbrt({na})", va ** (1/3))
    for exp in range(-6, 0):
        if va > 0:
            _reg(f"({na})^{exp}", va ** exp)

# 2의 거듭제곱
for na, va in list(BASICS.items()) + list(derived.items()):
    if isinstance(va, (int, float)) and -30 < va < 30:
        _reg(f"2^({na})", 2 ** va)

# n의 거듭제곱
for exp in range(1, 8):
    _reg(f"n^{exp}", 6 ** exp)
    _reg(f"sigma^{exp}", 12 ** exp)

# 계승
_reg("n!", 720)
_reg("n!/n", 120)
_reg("n!/sigma", 60)
_reg("n!/J2", 30)
_reg("n!/sigma^2", 5)
_reg("tau!", 24)
_reg("sopfr!", 120)

# 특수 상수
_reg("P2", 28)
_reg("K6_kissing", 72)
_reg("pi^2/n", math.pi**2/6)
_reg("e^phi", math.e**2)
_reg("1/e", 1/math.e)
_reg("ln(4/3)", math.log(4/3))
_reg("R(6)", 1)
_reg("sigma/(sigma-phi)", 1.2)
_reg("1/(sigma-phi)", 0.1)
_reg("golden_ratio", (1+math.sqrt(5))/2)
_reg("pi", math.pi)
_reg("e", math.e)
_reg("ln2", math.log(2))
_reg("ln6", math.log(6))

# Egyptian fractions
_reg("egyptian_1/2", 0.5)
_reg("egyptian_1/3", 1/3)
_reg("egyptian_1/6", 1/6)
_reg("egyptian_1/2+1/3", 5/6)
_reg("egyptian_1/2+1/6", 2/3)
_reg("egyptian_1/3+1/6", 0.5)
_reg("egyptian_1/2+1/3+1/6", 1.0)

# 역수 Egyptian
_reg("1/egyptian_1/2", 2)
_reg("1/egyptian_1/3", 3)
_reg("1/egyptian_1/6", 6)

# 주요 산업/물리 상수 (n=6 기반)
_reg("HBM3_GB", 24)  # σ·φ
_reg("HBM3e_GB", 36)  # n²
_reg("HBM4_GB", 48)   # σ·τ
_reg("SM_count_A100", 108)  # σ·(σ-tau-mu)
_reg("SM_count_H100", 132)  # σ·(σ-mu)
_reg("SM_count_AD102", 144) # σ²
_reg("SM_count_B200", 160)  # (sigma-phi)·phi^tau
_reg("SQ_bandgap", 4/3)  # τ/n/φ... no, τ²/σ
_reg("BERT_dim", 768)  # 2^σ * (n/φ)/σ... no, just register
_reg("GPT3_dim", 12288)

# 큰 스케일
_reg("10^n", 1e6)
_reg("10^sigma", 1e12)
_reg("10^(sigma-phi)", 1e10)
_reg("10^sopfr", 1e5)
_reg("10^tau", 1e4)
_reg("10^(sigma-tau)", 1e8)

print(f"등록된 타겟 수: {len(TARGETS)}")

# 역인덱스: 값 → [(name, exact_val)] (빠른 검색용)
# 버킷 해시 방식
from collections import defaultdict
BUCKET = defaultdict(list)
for name, val in TARGETS.items():
    # 정수 근사 버킷 + 실수 버킷
    key = round(val * 1000)  # milli-precision bucket
    BUCKET[key].append((name, val))


def grade_match(value, target):
    """값과 타겟 비교 → (등급, 오차율) 또는 None"""
    if target == 0:
        if abs(value) < 1e-9:
            return ("EXACT", 0.0)
        return None
    err = abs(value - target) / abs(target)
    if err < 0.001:
        return ("EXACT", err)
    elif err < 0.01:
        return ("CLOSE", err)
    elif err < 0.05:
        return ("NEAR", err)
    return None


def check_value(v):
    """
    값 v를 타겟 사전에 대해 검사.
    최선의 매치 (grade, expression, error) 반환. 없으면 None.
    """
    if v is None or not math.isfinite(v):
        return None

    best_grade_rank = 99
    best_error = 99.0
    best_grade = None
    best_expr = None

    grade_rank = {"EXACT": 0, "CLOSE": 1, "NEAR": 2}

    # 버킷 검색: v의 근처 버킷만 확인
    key = round(v * 1000)
    # 5% 범위의 버킷 검색
    spread = max(1, abs(int(v * 50)))  # ~5% spread in milli-units
    for bk in range(key - spread, key + spread + 1):
        for name, target in BUCKET.get(bk, []):
            result = grade_match(v, target)
            if result:
                g, e = result
                gr = grade_rank[g]
                if (gr, e) < (best_grade_rank, best_error):
                    best_grade_rank = gr
                    best_error = e
                    best_grade = g
                    best_expr = name

    # 버킷이 커버 못하는 큰 값은 전수 검색 (느리지만 정확)
    if best_grade is None and (abs(v) > 100 or abs(v) < 0.01):
        for name, target in TARGETS.items():
            result = grade_match(v, target)
            if result:
                g, e = result
                gr = grade_rank[g]
                if (gr, e) < (best_grade_rank, best_error):
                    best_grade_rank = gr
                    best_error = e
                    best_grade = g
                    best_expr = name

    if best_grade is None:
        return None
    return (best_grade, best_expr, best_error)


def main():
    print(f"═══ MISS 구출 스크립트 시작 ═══")
    print(f"로그 파일: {LOG_PATH}")

    # 1) 전체 로그 읽기
    all_entries = []
    miss_entries = []
    with open(LOG_PATH, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                all_entries.append(entry)
                if entry.get("grade") == "MISS":
                    miss_entries.append(entry)
            except json.JSONDecodeError:
                pass

    print(f"전체 엔트리: {len(all_entries):,}")
    print(f"MISS 엔트리: {len(miss_entries):,}")

    # 2) 기존 (constant, value, grade!=MISS) 키 수집 → 중복 방지
    existing_keys = set()
    for entry in all_entries:
        if entry.get("grade") != "MISS":
            key = (str(entry.get("constant", "")), str(entry.get("value", "")))
            existing_keys.add(key)

    # 3) 기존 miss-rescue 소스 키도 수집
    for entry in all_entries:
        if entry.get("source") == "miss-rescue":
            key = (str(entry.get("constant", "")), str(entry.get("value", "")))
            existing_keys.add(key)

    # 4) MISS 엔트리 스캔
    upgraded = []
    grade_counts = defaultdict(int)
    skip_dup = 0
    skip_no_value = 0
    seen_in_this_run = set()

    for entry in miss_entries:
        raw_val = entry.get("value")
        try:
            v = float(raw_val)
        except (TypeError, ValueError):
            skip_no_value += 1
            continue

        # 중복 체크
        dup_key = (str(entry.get("constant", "")), str(raw_val))
        if dup_key in existing_keys or dup_key in seen_in_this_run:
            skip_dup += 1
            continue

        result = check_value(v)
        if result is None:
            continue

        new_grade, expression, error = result

        # 승격 엔트리 생성
        new_entry = {
            "constant": entry.get("constant", ""),
            "value": raw_val,
            "grade": new_grade,
            "n6_expression": expression,
            "n6_error": round(error, 6),
            "source": "miss-rescue",
            "rescued_from": "MISS",
            "processed": True,
            "timestamp": entry.get("timestamp", ""),
        }
        # 원본 메타데이터 보존
        for k in ["alien_index", "mk2", "blowup", "telescope", "evolution"]:
            if k in entry:
                new_entry[k] = entry[k]

        upgraded.append(new_entry)
        grade_counts[new_grade] += 1
        seen_in_this_run.add(dup_key)

    print(f"\n═══ 스캔 결과 ═══")
    print(f"스캔 MISS: {len(miss_entries):,}")
    print(f"숫자 변환 실패: {skip_no_value:,}")
    print(f"중복 스킵: {skip_dup:,}")
    print(f"승격 총 수: {len(upgraded):,}")
    print()
    print(f"  EXACT: {grade_counts['EXACT']:,}")
    print(f"  CLOSE: {grade_counts['CLOSE']:,}")
    print(f"  NEAR:  {grade_counts['NEAR']:,}")

    # 5) 승격 엔트리를 로그에 추가
    if upgraded:
        with open(LOG_PATH, "a") as f:
            for entry in upgraded:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        print(f"\n{len(upgraded):,}개 엔트리 → {LOG_PATH} 추가 완료")
    else:
        print("\n승격 가능한 엔트리 없음")

    # 6) 상위 발견 출력
    if upgraded:
        print(f"\n═══ 주요 발견 (EXACT 상위 30) ═══")
        exact_list = [e for e in upgraded if e["grade"] == "EXACT"]
        # 고유 expression 기준 정렬
        expr_best = {}
        for e in exact_list:
            expr = e["n6_expression"]
            if expr not in expr_best or e["n6_error"] < expr_best[expr]["n6_error"]:
                expr_best[expr] = e
        sorted_exprs = sorted(expr_best.values(), key=lambda e: e["n6_error"])
        for e in sorted_exprs[:30]:
            print(f"  값={str(e['value']):>12}  →  {e['n6_expression']:<25}  "
                  f"오차={e['n6_error']:.6f}  원본={e.get('constant','?')[:40]}")

        print(f"\n═══ 주요 발견 (CLOSE 상위 15) ═══")
        close_list = [e for e in upgraded if e["grade"] == "CLOSE"]
        expr_best_c = {}
        for e in close_list:
            expr = e["n6_expression"]
            if expr not in expr_best_c or e["n6_error"] < expr_best_c[expr]["n6_error"]:
                expr_best_c[expr] = e
        sorted_c = sorted(expr_best_c.values(), key=lambda e: e["n6_error"])
        for e in sorted_c[:15]:
            print(f"  값={str(e['value']):>12}  →  {e['n6_expression']:<25}  "
                  f"오차={e['n6_error']:.6f}  원본={e.get('constant','?')[:40]}")

        print(f"\n═══ 주요 발견 (NEAR 상위 15) ═══")
        near_list = [e for e in upgraded if e["grade"] == "NEAR"]
        expr_best_n = {}
        for e in near_list:
            expr = e["n6_expression"]
            if expr not in expr_best_n or e["n6_error"] < expr_best_n[expr]["n6_error"]:
                expr_best_n[expr] = e
        sorted_n = sorted(expr_best_n.values(), key=lambda e: e["n6_error"])
        for e in sorted_n[:15]:
            print(f"  값={str(e['value']):>12}  →  {e['n6_expression']:<25}  "
                  f"오차={e['n6_error']:.6f}  원본={e.get('constant','?')[:40]}")

        # 표현식별 빈도
        print(f"\n═══ 표현식별 승격 빈도 (상위 20) ═══")
        expr_freq = defaultdict(int)
        for e in upgraded:
            expr_freq[e["n6_expression"]] += 1
        for expr, cnt in sorted(expr_freq.items(), key=lambda x: -x[1])[:20]:
            target_val = TARGETS.get(expr, "?")
            print(f"  {expr:<30}  = {target_val:<12}  횟수={cnt}")

    print(f"\n═══ 완료 ═══")


if __name__ == "__main__":
    main()
