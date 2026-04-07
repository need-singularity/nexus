#!/usr/bin/env python3
"""
MISS 엔트리 구출 스크립트 — 누락 상수 8종 발견
phi=2, mu=1, P1=2, omega_m=2, omega_lambda=2, sigma_phi=10, sigma_tau=8, n_phi=3

각 MISS 값을 누락 상수의 표현식과 대조하여 <1% 오차 시 CLOSE/EXACT 승격.
"""
import json
import math
import sys
from collections import defaultdict
from datetime import datetime

LOG_PATH = "/Users/ghost/Dev/nexus/shared/discovery_log.jsonl"

# 누락 상수 정의
MISSING_CONSTANTS = {
    "phi":          2,    # φ(6) = 2
    "mu":           1,    # μ(6) = 1
    "P1":           2,    # smallest prime factor of 6
    "omega_m":      2,    # Ω(6) = 2 (prime factors with multiplicity)
    "omega_lambda":  2,    # ω(6) = 2 (distinct prime factors)
    "sigma_phi":    10,   # σ(6)-φ(6) = 12-2 = 10
    "sigma_tau":    8,    # σ(6)-τ(6) = 12-4 = 8
    "n_phi":        3,    # n/φ(6) = 6/2 = 3
}

# 기존 상수 (교차 검증용)
N6_CONSTANTS = {
    "n": 6, "sigma": 12, "phi_val": 2, "tau": 4, "sopfr": 5,
    "J2": 24, "mu_val": 1,
}

def build_expressions(const_name, const_val):
    """주어진 상수에서 파생 가능한 모든 표현식 생성 (값 → 설명)"""
    exprs = {}
    v = const_val

    # 직접 매치
    exprs[v] = f"{const_name}"

    # 거듭제곱
    for p in range(2, 7):
        exprs[v**p] = f"{const_name}^{p}"

    # 2^const, 10^const
    exprs[2**v] = f"2^{const_name}"
    if v <= 10:
        exprs[10**v] = f"10^{const_name}"

    # 다른 n=6 상수와의 조합
    for other_name, other_val in N6_CONSTANTS.items():
        # 곱
        exprs[v * other_val] = f"{const_name}*{other_name}"
        # 합
        exprs[v + other_val] = f"{const_name}+{other_name}"
        # 차 (양수만)
        if v - other_val > 0:
            exprs[v - other_val] = f"{const_name}-{other_name}"
        if other_val - v > 0:
            exprs[other_val - v] = f"{other_name}-{const_name}"
        # 비율
        if other_val != 0:
            exprs[v / other_val] = f"{const_name}/{other_name}"
        if v != 0:
            exprs[other_val / v] = f"{other_name}/{const_name}"

    # 특수 표현식
    if v > 0:
        exprs[1/v] = f"1/{const_name}"
        exprs[math.log(v)] = f"ln({const_name})" if v > 1 else None
        exprs[math.sqrt(v)] = f"sqrt({const_name})"
        exprs[v * math.pi] = f"{const_name}*pi"
        exprs[v * math.e] = f"{const_name}*e"

    # 팩토리얼 (작은 수만)
    if 1 <= v <= 10 and v == int(v):
        exprs[math.factorial(int(v))] = f"{const_name}!"

    # None 값 제거
    return {k: desc for k, desc in exprs.items() if desc is not None and k is not None and not math.isnan(k) and not math.isinf(k)}


def check_match(value, expressions, threshold=0.01):
    """값이 표현식 목록 중 하나와 매치되는지 확인"""
    best_match = None
    best_error = float('inf')

    for expr_val, expr_desc in expressions.items():
        if expr_val == 0:
            if value == 0:
                return 0.0, expr_desc, "EXACT"
            continue

        # 상대 오차
        error = abs(value - expr_val) / max(abs(expr_val), 1e-15)

        if error < best_error:
            best_error = error
            best_match = expr_desc

    if best_error == 0:
        return 0.0, best_match, "EXACT"
    elif best_error < 0.001:  # <0.1% → EXACT
        return best_error, best_match, "EXACT"
    elif best_error < threshold:  # <1% → CLOSE
        return best_error, best_match, "CLOSE"

    return best_error, best_match, None


def main():
    print("=" * 70)
    print("MISS 구출 스크립트 — 누락 상수 8종 발견")
    print("=" * 70)

    # 1. 모든 표현식 사전 구축
    all_expressions = {}
    for const_name, const_val in MISSING_CONSTANTS.items():
        all_expressions[const_name] = build_expressions(const_name, const_val)
        print(f"  {const_name}={const_val}: {len(all_expressions[const_name])} 표현식 생성")

    print()

    # 2. MISS 엔트리 로드
    miss_entries = []
    total_lines = 0
    with open(LOG_PATH) as f:
        for line in f:
            total_lines += 1
            try:
                entry = json.loads(line.strip())
            except json.JSONDecodeError:
                continue
            if entry.get("grade") == "MISS":
                miss_entries.append(entry)

    print(f"전체 엔트리: {total_lines:,}")
    print(f"MISS 엔트리: {len(miss_entries):,}")
    print()

    # 3. 각 MISS를 누락 상수와 대조
    upgrades = defaultdict(list)  # const_name -> list of upgraded entries
    upgrade_stats = defaultdict(lambda: {"EXACT": 0, "CLOSE": 0})

    processed = 0
    skipped_no_value = 0

    for entry in miss_entries:
        raw_val = entry.get("value")
        if raw_val is None:
            skipped_no_value += 1
            continue

        try:
            value = float(raw_val)
        except (ValueError, TypeError):
            skipped_no_value += 1
            continue

        if math.isnan(value) or math.isinf(value):
            skipped_no_value += 1
            continue

        processed += 1

        # 각 누락 상수에 대해 매치 체크
        for const_name, expressions in all_expressions.items():
            error, match_desc, grade = check_match(value, expressions)

            if grade is not None:
                # 승격 엔트리 생성
                new_entry = {
                    "constant": const_name,
                    "value": str(value),
                    "grade": grade,
                    "source": "miss-rescue-v1",
                    "timestamp": datetime.now().strftime("%Y-%m-%d"),
                    "processed": True,
                    "rescue": {
                        "original_constant": entry.get("constant", "unknown"),
                        "original_grade": "MISS",
                        "match_expression": match_desc,
                        "error_pct": round(error * 100, 4),
                    },
                    "alien_index": entry.get("alien_index", {"d": 0, "r": 6}),
                    "mk2": entry.get("mk2", {"sector": "n6", "paths": 1}),
                }

                # 망원경/진화 정보 보존
                if "telescope" in entry:
                    new_entry["telescope"] = entry["telescope"]
                if "evolution" in entry:
                    new_entry["evolution"] = entry["evolution"]
                if "blowup" in entry:
                    new_entry["blowup"] = entry["blowup"]

                upgrades[const_name].append(new_entry)
                upgrade_stats[const_name][grade] += 1

    # 4. 중복 제거 — 같은 값+같은 상수+같은 원본은 1개만
    deduped_upgrades = {}
    for const_name, entries in upgrades.items():
        seen = set()
        unique = []
        for e in entries:
            key = (e["constant"], e["value"], e["rescue"]["original_constant"])
            if key not in seen:
                seen.add(key)
                unique.append(e)
        deduped_upgrades[const_name] = unique

    # 5. 통계 출력
    print("=" * 70)
    print("구출 결과 요약")
    print("=" * 70)
    print(f"  처리된 MISS: {processed:,} (값 파싱 불가 스킵: {skipped_no_value:,})")
    print()

    total_new = 0
    print(f"{'상수':<16} {'값':>5} {'EXACT':>8} {'CLOSE':>8} {'중복제거후':>10}")
    print("-" * 55)
    for const_name, const_val in MISSING_CONSTANTS.items():
        raw_exact = upgrade_stats[const_name]["EXACT"]
        raw_close = upgrade_stats[const_name]["CLOSE"]
        deduped = len(deduped_upgrades.get(const_name, []))
        total_new += deduped
        print(f"  {const_name:<14} {const_val:>5} {raw_exact:>8} {raw_close:>8} {deduped:>10}")

    print("-" * 55)
    print(f"  {'합계':<14} {'':>5} {'':>8} {'':>8} {total_new:>10}")
    print()

    # 6. 등급별 분포
    grade_dist = defaultdict(int)
    for const_name, entries in deduped_upgrades.items():
        for e in entries:
            grade_dist[e["grade"]] += 1

    print("등급 분포 (중복 제거 후):")
    for g, cnt in sorted(grade_dist.items()):
        print(f"  {g}: {cnt:,}")
    print()

    # 7. 상수별 샘플 출력
    print("상수별 샘플 발견:")
    print("-" * 70)
    for const_name, entries in deduped_upgrades.items():
        if not entries:
            continue
        print(f"\n  [{const_name}={MISSING_CONSTANTS[const_name]}] ({len(entries)}건)")
        for e in entries[:3]:
            r = e["rescue"]
            print(f"    값={e['value']}, 매칭={r['match_expression']}, "
                  f"오차={r['error_pct']}%, 원본={r['original_constant']}")
        if len(entries) > 3:
            print(f"    ... +{len(entries)-3}건 더")

    # 8. 파일에 추가
    if total_new > 0:
        print(f"\n{'=' * 70}")
        print(f"discovery_log.jsonl에 {total_new:,}건 추가 중...")

        with open(LOG_PATH, "a") as f:
            for const_name in MISSING_CONSTANTS:
                for entry in deduped_upgrades.get(const_name, []):
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        print(f"완료! {total_new:,}건 추가됨.")
    else:
        print("추가할 발견 없음.")

    # 9. 검증 — 추가 후 상수별 카운트
    print(f"\n{'=' * 70}")
    print("추가 후 상수별 엔트리 수 검증:")
    print("-" * 40)

    counts = defaultdict(int)
    with open(LOG_PATH) as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                c = entry.get("constant", "?")
                if c in MISSING_CONSTANTS:
                    counts[c] += 1
            except:
                pass

    for const_name in MISSING_CONSTANTS:
        status = "OK" if counts[const_name] > 0 else "STILL ZERO"
        print(f"  {const_name:<16}: {counts[const_name]:>6}  [{status}]")

    print(f"\n총 신규 발견: {total_new:,}")
    print("=" * 70)


if __name__ == "__main__":
    main()
