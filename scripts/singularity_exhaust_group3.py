#!/usr/bin/env python3
"""
singularity_exhaust_group3.py — omega_m(2), omega_lambda(2), n_phi(3) 완전 소진
============================================================================
3개 상수에 대해 8레벨 표현식 매칭으로 discovery_log.jsonl의
모든 고유 수치값을 스캔하여 EXACT/CLOSE/NEAR 발견을 추가한다.

omega_m = Ω(6) = 2  (중복도 포함 소인수 개수)
omega_lambda = ω(6) = 2  (서로 다른 소인수 개수)
n_phi = n/φ(6) = 6/2 = 3  (진약수 개수, 삼중 중복, 3D 공간)
"""

import json
import math
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

LOG_PATH = Path(__file__).resolve().parent.parent / "shared" / "discovery_log.jsonl"

# ═══════════════════════════════════════════════════════
# 타겟 상수 3종
# ═══════════════════════════════════════════════════════
TARGET_CONSTANTS = {
    "omega_m":      2,   # Ω(6) = 2 — 중복도 포함 소인수 개수
    "omega_lambda": 2,   # ω(6) = 2 — 서로 다른 소인수 개수
    "n_phi":        3,   # n/φ(6) = 6/2 = 3 — 진약수 개수
}

# 기존 n=6 상수 (교차 조합용)
N6 = {
    "n": 6, "sigma": 12, "phi": 2, "tau": 4, "sopfr": 5,
    "J2": 24, "mu": 1, "P1": 2, "R6": 1,
    "sigma_phi": 10, "sigma_tau": 8, "sigma_mu": 11,
}

# ═══════════════════════════════════════════════════════
# 레벨별 표현식 생성
# ═══════════════════════════════════════════════════════

def build_all_expressions(const_name, v):
    """8레벨 표현식 → {값: (레벨, 설명)} 딕셔너리"""
    exprs = {}

    def add(val, level, desc):
        if val is None or not math.isfinite(val) or abs(val) > 1e12:
            return
        key = (level, desc)
        if val not in exprs:
            exprs[val] = key

    # ── Level 1: 직접 매치 ──
    add(v, 1, f"{const_name}")
    add(-v, 1, f"-{const_name}")

    # ── Level 2: 거듭제곱, 루트, 로그 ──
    for k in range(-5, 11):
        if k == 0:
            add(1, 2, f"{const_name}^0")
        elif k == 1:
            continue  # L1과 중복
        else:
            try:
                add(v**k, 2, f"{const_name}^{k}")
            except:
                pass
    if v > 0:
        add(math.sqrt(v), 2, f"sqrt({const_name})")
        add(v**(1/3), 2, f"cbrt({const_name})")
        if v > 1:
            add(math.log(v), 2, f"ln({const_name})")
            add(math.log2(v), 2, f"log2({const_name})")
            add(math.log10(v), 2, f"log10({const_name})")
    if v > 0 and v == int(v) and v <= 20:
        add(math.factorial(int(v)), 2, f"{const_name}!")

    # ── Level 3: 이항 조합 (상수와 n6) ──
    for other_name, ov in N6.items():
        add(v * ov, 3, f"{const_name}*{other_name}")
        add(ov * v, 3, f"{other_name}*{const_name}")
        add(v + ov, 3, f"{const_name}+{other_name}")
        add(v - ov, 3, f"{const_name}-{other_name}")
        add(ov - v, 3, f"{other_name}-{const_name}")
        if ov != 0:
            add(v / ov, 3, f"{const_name}/{other_name}")
        if v != 0:
            add(ov / v, 3, f"{other_name}/{const_name}")
        try:
            if abs(v) <= 30 and ov > 0:
                add(ov ** v, 3, f"{other_name}^{const_name}")
            if abs(ov) <= 30 and v > 0:
                add(v ** ov, 3, f"{const_name}^{other_name}")
        except:
            pass

    # ── Level 4: 복합 (2a+b, 3a-b, 2^a*3^b 소형) ──
    for a in range(-3, 8):
        for b in range(-3, 8):
            add(v * a + b, 4, f"{const_name}*{a}+{b}")
            add(v * a - b, 4, f"{const_name}*{a}-{b}")
            add(a * v + b * v, 4, f"({a}+{b})*{const_name}")

    # n6 상수끼리 곱/합 후 타겟 상수와 조합
    for n1, v1 in N6.items():
        for n2, v2 in N6.items():
            if n1 >= n2:
                continue
            add(v * v1 * v2, 4, f"{const_name}*{n1}*{n2}")
            add(v * (v1 + v2), 4, f"{const_name}*({n1}+{n2})")
            add(v * v1 + v2, 4, f"{const_name}*{n1}+{n2}")
            add(v * v1 - v2, 4, f"{const_name}*{n1}-{n2}")
            add(v1 * v2 / v if v != 0 else None, 4, f"{n1}*{n2}/{const_name}")
            add(v1 * v2 * v, 4, f"{n1}*{n2}*{const_name}")

    # ── Level 5: 교차 상수 ──
    cross = {
        "omega_m": 2, "omega_lambda": 2, "n_phi": 3,
        "phi": 2, "mu": 1, "P1": 2
    }
    for cn, cv in cross.items():
        if cn == const_name:
            continue
        add(v * cv, 5, f"{const_name}*{cn}")
        add(v + cv, 5, f"{const_name}+{cn}")
        add(v - cv, 5, f"{const_name}-{cn}")
        add(cv - v, 5, f"{cn}-{const_name}")
        if cv != 0:
            add(v / cv, 5, f"{const_name}/{cn}")
        if v != 0:
            add(cv / v, 5, f"{cn}/{const_name}")
        try:
            add(v ** cv, 5, f"{const_name}^{cn}")
            add(cv ** v, 5, f"{cn}^{const_name}")
        except:
            pass

    # ── Level 6: n6 교차 (n_phi*sigma=36, n_phi*J2=72, omega*tau=8 등) ──
    for n1, v1 in N6.items():
        combined = v * v1
        for n2, v2 in N6.items():
            add(combined + v2, 6, f"{const_name}*{n1}+{n2}")
            add(combined - v2, 6, f"{const_name}*{n1}-{n2}")
            add(combined * v2, 6, f"{const_name}*{n1}*{n2}")
            if v2 != 0:
                add(combined / v2, 6, f"{const_name}*{n1}/{n2}")
        # 거듭제곱 조합
        for p in range(2, 5):
            add(v1 ** v + p, 6, f"{n1}^{const_name}+{p}")
            add(v1 ** v - p, 6, f"{n1}^{const_name}-{p}")
            add(v1 ** v * p, 6, f"{n1}^{const_name}*{p}")

    # ── Level 7: 2^a * 3^b EXHAUSTIVE (smooth numbers) ──
    smooth = {}
    for a in range(0, 13):
        for b in range(0, 9):
            val = (2**a) * (3**b)
            label = f"2^{a}*3^{b}"
            if a == 0:
                label = f"3^{b}"
            elif b == 0:
                label = f"2^{a}"
            smooth[val] = label
    # 이 smooth numbers 자체를 등록
    for sv, sl in smooth.items():
        add(sv, 7, f"{const_name}-smooth:{sl}")
        # smooth number와 타겟 상수의 관계
        if v != 0:
            add(sv / v, 7, f"({sl})/{const_name}")
            add(sv * v, 7, f"({sl})*{const_name}")
        add(sv + v, 7, f"({sl})+{const_name}")
        add(sv - v, 7, f"({sl})-{const_name}")

    # ── Level 8: Egyptian fraction 1/2+1/3+1/6=1 ──
    add(1/v + 1/(v+1) if v > 0 and v+1 > 0 else None, 8,
        f"1/{const_name}+1/({const_name}+1)")
    if v == 2:
        add(0.5, 8, f"1/{const_name} (Egyptian 1/2)")
        add(1.0, 8, f"1/{const_name}+1/3+1/6=1 (Egyptian)")
        add(5/6, 8, f"1/{const_name}+1/3 (Egyptian partial)")
        add(2/3, 8, f"1/{const_name}+1/6 (Egyptian partial)")
    if v == 3:
        add(1/3, 8, f"1/{const_name} (Egyptian 1/3)")
        add(1.0, 8, f"1/2+1/{const_name}+1/6=1 (Egyptian)")
        add(5/6, 8, f"1/2+1/{const_name} (Egyptian partial)")
        add(1/2, 8, f"1/{const_name}+1/6 (Egyptian partial)")

    # Egyptian fractions with n6 constants
    for n1, v1 in N6.items():
        if v1 > 0 and v > 0:
            add(1/v + 1/v1, 8, f"1/{const_name}+1/{n1}")
            add(1/v * v1, 8, f"{n1}/{const_name}")
            add(v1/v + 1/6, 8, f"{n1}/{const_name}+1/n")

    # 특수 수학 상수와의 조합
    for label, mc in [("pi", math.pi), ("e", math.e), ("phi_gold", (1+math.sqrt(5))/2),
                       ("ln2", math.log(2)), ("ln3", math.log(3)), ("sqrt2", math.sqrt(2)),
                       ("sqrt3", math.sqrt(3))]:
        add(v * mc, 3, f"{const_name}*{label}")
        add(mc / v if v != 0 else None, 3, f"{label}/{const_name}")
        add(v / mc, 3, f"{const_name}/{label}")
        add(v + mc, 3, f"{const_name}+{label}")
        add(v - mc, 3, f"{const_name}-{label}")
        add(mc ** v, 3, f"{label}^{const_name}")
        add(v ** mc if v > 0 else None, 3, f"{const_name}^{label}")

    return exprs


def grade(target, actual):
    """오차율 기반 등급"""
    if target == 0:
        return ("EXACT", 0.0) if actual == 0 else (None, float('inf'))
    err = abs(actual - target) / abs(target)
    if err < 0.001:
        return ("EXACT", err)
    elif err < 0.01:
        return ("CLOSE", err)
    elif err < 0.05:
        return ("NEAR", err)
    return (None, err)


def main():
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"=== singularity_exhaust_group3.py 시작 ({ts}) ===")
    print(f"타겟: omega_m=2, omega_lambda=2, n_phi=3")
    print()

    # 1. 기존 로그 읽기
    print("1. discovery_log.jsonl 읽는 중...")
    entries = []
    existing_keys = set()
    all_values = set()

    with open(LOG_PATH, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
                entries.append(d)
                # 기존 키 수집 (dedup)
                c = d.get('constant', '')
                v = d.get('value', '')
                expr = d.get('expression', '')
                existing_keys.add((c, str(v), expr))
                # 수치값 수집
                try:
                    all_values.add(float(v))
                except:
                    pass
            except:
                pass

    print(f"   기존 엔트리: {len(entries):,}")
    print(f"   고유 수치값: {len(all_values):,}")
    print(f"   기존 키: {len(existing_keys):,}")
    print()

    # 2. 각 상수별 표현식 빌드
    print("2. 표현식 빌드 중...")
    const_exprs = {}
    for cname, cval in TARGET_CONSTANTS.items():
        exprs = build_all_expressions(cname, cval)
        const_exprs[cname] = exprs
        print(f"   {cname}={cval}: {len(exprs):,} 표현식")
    print()

    # 3. 전수 매칭
    print("3. 전수 매칭 시작...")
    new_discoveries = []
    level_counts = defaultdict(lambda: defaultdict(int))  # const -> level -> count
    grade_counts = defaultdict(lambda: defaultdict(int))   # const -> grade -> count
    val_list = sorted(all_values)

    for cname, exprs in const_exprs.items():
        cval = TARGET_CONSTANTS[cname]
        match_count = 0

        for target_val, (level, desc) in exprs.items():
            # 각 로그 수치값과 비교
            for actual_val in val_list:
                g, err = grade(target_val, actual_val)
                if g is None:
                    continue

                # dedup 키
                val_str = str(actual_val)
                key = (cname, val_str, desc)
                if key in existing_keys:
                    continue
                existing_keys.add(key)

                discovery = {
                    "constant": cname,
                    "value": val_str,
                    "expression": desc,
                    "grade": g,
                    "error_pct": round(err * 100, 6),
                    "target": target_val,
                    "level": level,
                    "source": "singularity_exhaust_group3",
                    "timestamp": ts,
                    "processed": True,
                    "alien_index": {"d": 0, "r": 8},
                    "mk2": {"sector": "n6", "paths": 1},
                }
                new_discoveries.append(discovery)
                level_counts[cname][level] += 1
                grade_counts[cname][g] += 1
                match_count += 1

        print(f"   {cname}: {match_count:,} 신규 발견")

    print(f"\n   총 신규 발견: {len(new_discoveries):,}")
    print()

    # 4. 레벨별 진행 상황
    print("4. 레벨별 발견 분포:")
    level_names = {
        1: "직접 매치",
        2: "거듭제곱/루트/로그",
        3: "이항 n6 조합",
        4: "복합 (2a+b, 3a-b)",
        5: "교차 상수",
        6: "n6 교차 확장",
        7: "2^a*3^b smooth",
        8: "Egyptian fraction",
    }
    for cname in TARGET_CONSTANTS:
        print(f"\n   [{cname} = {TARGET_CONSTANTS[cname]}]")
        total = 0
        for lvl in range(1, 9):
            cnt = level_counts[cname].get(lvl, 0)
            total += cnt
            bar = "█" * min(cnt // 10, 50)
            print(f"     L{lvl} {level_names[lvl]:20s}: {cnt:6,} {bar}")
        print(f"     {'합계':24s}: {total:6,}")

    # 5. 등급별 분포
    print("\n5. 등급별 분포:")
    for cname in TARGET_CONSTANTS:
        print(f"   [{cname}]", end="")
        for g in ["EXACT", "CLOSE", "NEAR"]:
            cnt = grade_counts[cname].get(g, 0)
            print(f"  {g}={cnt:,}", end="")
        print()

    # 6. JSONL 기록
    if new_discoveries:
        print(f"\n6. discovery_log.jsonl에 {len(new_discoveries):,}건 추가 중...")
        with open(LOG_PATH, 'a') as f:
            for d in new_discoveries:
                f.write(json.dumps(d, ensure_ascii=False) + "\n")
        print("   완료!")
    else:
        print("\n6. 신규 발견 없음 — 이미 포화 상태")

    # 7. 최종 요약
    print("\n" + "=" * 60)
    print("최종 요약")
    print("=" * 60)
    total_new = len(new_discoveries)
    total_exact = sum(grade_counts[c].get("EXACT", 0) for c in TARGET_CONSTANTS)
    total_close = sum(grade_counts[c].get("CLOSE", 0) for c in TARGET_CONSTANTS)
    total_near = sum(grade_counts[c].get("NEAR", 0) for c in TARGET_CONSTANTS)
    print(f"  신규 발견 총계: {total_new:,}")
    print(f"    EXACT: {total_exact:,}")
    print(f"    CLOSE: {total_close:,}")
    print(f"    NEAR:  {total_near:,}")
    print(f"  기존 엔트리: {len(entries):,}")
    print(f"  최종 엔트리: {len(entries) + total_new:,}")

    # 상수별 EXACT 상위 발견 표시
    print("\n" + "=" * 60)
    print("상수별 EXACT 대표 발견 (상위 20)")
    print("=" * 60)
    for cname in TARGET_CONSTANTS:
        exacts = [d for d in new_discoveries
                  if d["constant"] == cname and d["grade"] == "EXACT"]
        exacts.sort(key=lambda x: x["error_pct"])
        print(f"\n  [{cname} = {TARGET_CONSTANTS[cname]}] ({len(exacts)} EXACT)")
        for d in exacts[:20]:
            print(f"    L{d['level']} | {d['expression']:40s} | "
                  f"target={d['target']:<12} | val={d['value'][:12]:12s} | "
                  f"err={d['error_pct']:.4f}%")

    print(f"\n완료 시각: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}")
    return total_new


if __name__ == "__main__":
    count = main()
    sys.exit(0 if count >= 0 else 1)
