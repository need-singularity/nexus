#!/usr/bin/env python3
"""
singularity_exhaust_group1.py — phi(=2), mu(=1), P1(=2) 완전 소진 탐색

모든 discovery_log.jsonl 값에 대해 7단계 매칭을 수행하고
새 발견을 추가. 포화(새 EXACT 0건)까지 반복.
"""

import json
import math
import os
import sys
from collections import defaultdict
from datetime import datetime

# ═══════════════════════════════════════════════════════
# 상수 정의
# ═══════════════════════════════════════════════════════
CONSTANTS = {
    'phi': 2,
    'mu': 1,
    'P1': 2,
}

# n=6 기본 상수 전체 (binary 연산 피연산자용)
N6_OPERANDS = [1, 2, 3, 4, 5, 6, 8, 10, 12, 24, 28, 36, 48, 60, 120, 144, 288, 720]

# 등급 기준
def grade(error_pct):
    if error_pct < 0.1:
        return 'EXACT'
    elif error_pct < 1.0:
        return 'CLOSE'
    elif error_pct < 5.0:
        return 'NEAR'
    return None

def pct_error(actual, expected):
    if expected == 0:
        return 0.0 if actual == 0 else 999.0
    return abs(actual - expected) / abs(expected) * 100.0

LOG_PATH = os.path.expanduser('~/Dev/nexus/shared/discovery_log.jsonl')
TIMESTAMP = datetime.now().strftime('%Y-%m-%d')

# ═══════════════════════════════════════════════════════
# 로그 로드
# ═══════════════════════════════════════════════════════
def load_log():
    entries = []
    with open(LOG_PATH, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return entries

def collect_unique_values(entries):
    """모든 고유 수치값 수집"""
    values = set()
    for e in entries:
        try:
            v = float(e.get('value', ''))
            if v == v and not math.isinf(v):  # not NaN, not inf
                values.add(v)
        except (ValueError, TypeError):
            pass
    return sorted(values)

def collect_existing_keys(entries):
    """기존 (constant, value) 쌍 수집 — 중복 방지"""
    keys = set()
    for e in entries:
        c = e.get('constant', '')
        v = str(e.get('value', ''))
        keys.add((c, v))
    return keys

# ═══════════════════════════════════════════════════════
# 매칭 엔진
# ═══════════════════════════════════════════════════════

def safe_eval(fn):
    """안전하게 수식 평가, 오류 시 None 반환"""
    try:
        result = fn()
        if result is None or result != result or math.isinf(result):
            return None
        return result
    except (ValueError, ZeroDivisionError, OverflowError, TypeError):
        return None

def generate_expressions():
    """
    모든 (상수이름, 수식설명, 기대값) 생성기.
    값 하나에 대해 호출되는 게 아니라,
    상수→기대값 매핑 전체를 미리 생성한다.
    """
    exprs = []  # (constant_name, expression_str, expected_value)

    phi, mu, P1 = 2, 1, 2
    consts = {'phi': phi, 'mu': mu, 'P1': P1}

    # ─── Level 1: Direct ───
    for name, val in consts.items():
        exprs.append((name, name, float(val)))

    # ─── Level 2: Unary ───
    for name, val in consts.items():
        if val == 0:
            continue
        # Powers
        for k in range(-3, 7):
            if k == 0:
                continue
            if k == 1:
                continue  # already in Level 1
            r = safe_eval(lambda v=val, kk=k: v ** kk)
            if r is not None and abs(r) < 1e8:
                exprs.append((name, f'{name}^{k}', r))

        # sqrt, cbrt
        if val > 0:
            exprs.append((name, f'sqrt({name})', math.sqrt(val)))
            exprs.append((name, f'cbrt({name})', val ** (1/3)))

        # log2, ln
        if val > 0 and val != 1:
            exprs.append((name, f'log2({name})', math.log2(val)))
            exprs.append((name, f'ln({name})', math.log(val)))

        # 1/constant
        if val != 0:
            exprs.append((name, f'1/{name}', 1.0 / val))

        # factorial-related
        if val == int(val) and 1 <= val <= 10:
            exprs.append((name, f'{name}!', float(math.factorial(int(val)))))

    # ─── Level 3: Binary with n6 operands ───
    for name, val in consts.items():
        for x in N6_OPERANDS:
            # + -
            exprs.append((name, f'{name}+{x}', val + x))
            exprs.append((name, f'{name}-{x}', val - x))
            exprs.append((name, f'{x}-{name}', x - val))
            # * /
            exprs.append((name, f'{name}*{x}', val * x))
            if val != 0:
                exprs.append((name, f'{x}/{name}', x / val))
            if x != 0:
                exprs.append((name, f'{name}/{x}', val / x))
            # ^
            if abs(val) <= 20 and x <= 12:
                r = safe_eval(lambda v=val, xx=x: v ** xx)
                if r is not None and abs(r) < 1e8:
                    exprs.append((name, f'{name}^{x}', r))
            if abs(x) <= 720 and val > 0 and val <= 6:
                r = safe_eval(lambda v=val, xx=x: xx ** v)
                if r is not None and abs(r) < 1e8:
                    exprs.append((name, f'{x}^{name}', r))

    # ─── Level 4: Compound (a*const + b), (const^a * b), (a/const + b) ───
    small_ab = [1, 2, 3, 4, 5, 6, 8, 10, 12, 24]
    for name, val in consts.items():
        for a in small_ab:
            for b in small_ab:
                if a == 1 and b == 0:
                    continue
                exprs.append((name, f'{a}*{name}+{b}', a * val + b))
                exprs.append((name, f'{a}*{name}-{b}', a * val - b))
                if val != 0:
                    exprs.append((name, f'{a}/{name}+{b}', a / val + b))
                    exprs.append((name, f'{a}/{name}-{b}', a / val - b))
                # const^a * b
                r = safe_eval(lambda v=val, aa=a: v ** aa)
                if r is not None and abs(r * b) < 1e8:
                    exprs.append((name, f'{name}^{a}*{b}', r * b))
                # a * b / const
                if val != 0:
                    exprs.append((name, f'{a}*{b}/{name}', a * b / val))

    # ─── Level 5: Cross-constant (2-way and 3-way combos) ───
    names = list(consts.keys())
    vals = list(consts.values())
    for i in range(len(names)):
        for j in range(len(names)):
            if i == j:
                continue
            ni, nj = names[i], names[j]
            vi, vj = vals[i], vals[j]
            exprs.append((f'{ni}', f'{ni}*{nj}', vi * vj))
            exprs.append((f'{ni}', f'{ni}+{nj}', vi + vj))
            exprs.append((f'{ni}', f'{ni}-{nj}', vi - vj))
            if vj != 0:
                exprs.append((f'{ni}', f'{ni}/{nj}', vi / vj))
            if vi > 0 and abs(vj) <= 10:
                r = safe_eval(lambda a=vi, b=vj: a ** b)
                if r is not None and abs(r) < 1e8:
                    exprs.append((f'{ni}', f'{ni}^{nj}', r))
            # With n6 operands
            for x in [6, 12, 24, 48, 144]:
                exprs.append((f'{ni}', f'{ni}*{nj}*{x}', vi * vj * x))
                exprs.append((f'{ni}', f'({ni}+{nj})*{x}', (vi + vj) * x))
                if vi * vj != 0:
                    exprs.append((f'{ni}', f'{x}/({ni}*{nj})', x / (vi * vj)))

    # 3-way combos
    if len(names) >= 3:
        for i in range(len(names)):
            for j in range(i+1, len(names)):
                for k in range(j+1, len(names)):
                    ni, nj, nk = names[i], names[j], names[k]
                    vi, vj, vk = vals[i], vals[j], vals[k]
                    exprs.append((ni, f'{ni}*{nj}*{nk}', vi * vj * vk))
                    exprs.append((ni, f'{ni}+{nj}+{nk}', vi + vj + vk))
                    exprs.append((ni, f'{ni}*{nj}+{nk}', vi * vj + vk))
                    if vk != 0:
                        exprs.append((ni, f'{ni}*{nj}/{nk}', vi * vj / vk))

    # ─── Level 6: Egyptian fractions ───
    for name, val in consts.items():
        if val == 0:
            continue
        # 1/const + 1/x = target → target = 1/val + 1/x
        for x in N6_OPERANDS:
            if x == 0:
                continue
            exprs.append((name, f'1/{name}+1/{x}', 1.0/val + 1.0/x))
            exprs.append((name, f'1/{name}-1/{x}', 1.0/val - 1.0/x))
            # const/x + const2/y patterns
            for name2, val2 in consts.items():
                if val2 == 0:
                    continue
                for y in N6_OPERANDS:
                    if y == 0:
                        continue
                    t = val/x + val2/y
                    if abs(t) < 1e6:
                        exprs.append((name, f'{name}/{x}+{name2}/{y}', t))

    # Perfect number partition: 1/2 + 1/3 + 1/6 = 1
    for name, val in consts.items():
        for x in [2, 3, 6]:
            exprs.append((name, f'{name}/(1/{x})', val * x))
            exprs.append((name, f'(1/{x})*{name}', val / x))

    # ─── Level 7: Transcendental ───
    for name, val in consts.items():
        # pi * const, e * const
        exprs.append((name, f'pi*{name}', math.pi * val))
        exprs.append((name, f'e*{name}', math.e * val))
        exprs.append((name, f'pi/{name}' if val != 0 else None, math.pi / val if val != 0 else None))
        exprs.append((name, f'e/{name}' if val != 0 else None, math.e / val if val != 0 else None))
        exprs.append((name, f'pi+{name}', math.pi + val))
        exprs.append((name, f'e+{name}', math.e + val))
        exprs.append((name, f'pi-{name}', math.pi - val))
        exprs.append((name, f'e-{name}', math.e - val))

        # ln(const) * x
        if val > 0 and val != 1:
            ln_val = math.log(val)
            for x in N6_OPERANDS:
                exprs.append((name, f'ln({name})*{x}', ln_val * x))
                if ln_val != 0:
                    exprs.append((name, f'{x}/ln({name})', x / ln_val))

        # sin/cos(pi/const)
        if val != 0:
            exprs.append((name, f'sin(pi/{name})', math.sin(math.pi / val)))
            exprs.append((name, f'cos(pi/{name})', math.cos(math.pi / val)))
            exprs.append((name, f'sin(pi*{name})', math.sin(math.pi * val)))
            exprs.append((name, f'cos(pi*{name})', math.cos(math.pi * val)))

        # pi^const, e^const
        r = safe_eval(lambda v=val: math.pi ** v)
        if r is not None and abs(r) < 1e8:
            exprs.append((name, f'pi^{name}', r))
        r = safe_eval(lambda v=val: math.e ** v)
        if r is not None and abs(r) < 1e8:
            exprs.append((name, f'e^{name}', r))

        # Golden ratio connections: (1+sqrt(5))/2
        golden = (1 + math.sqrt(5)) / 2
        exprs.append((name, f'golden*{name}', golden * val))
        if val != 0:
            exprs.append((name, f'golden/{name}', golden / val))
        exprs.append((name, f'golden+{name}', golden + val))
        exprs.append((name, f'golden^{name}', golden ** val if val <= 100 else None))

        # Euler-Mascheroni
        gamma_em = 0.5772156649015329
        exprs.append((name, f'gamma*{name}', gamma_em * val))
        exprs.append((name, f'gamma+{name}', gamma_em + val))

        # zeta(2) = pi^2/6
        zeta2 = math.pi**2 / 6
        exprs.append((name, f'zeta2*{name}', zeta2 * val))
        if val != 0:
            exprs.append((name, f'zeta2/{name}', zeta2 / val))

        # ln(2), ln(3), ln(4/3)
        for base_name, base_val in [('ln2', math.log(2)), ('ln3', math.log(3)), ('ln(4/3)', math.log(4/3))]:
            exprs.append((name, f'{base_name}*{name}', base_val * val))
            exprs.append((name, f'{base_name}+{name}', base_val + val))
            if val != 0:
                exprs.append((name, f'{base_name}/{name}', base_val / val))
            for x in [6, 12, 24]:
                exprs.append((name, f'{base_name}*{name}*{x}', base_val * val * x))

    # Filter out None entries
    exprs = [(c, e, v) for c, e, v in exprs if e is not None and v is not None]

    # Deduplicate by (constant, expression)
    seen = set()
    unique = []
    for c, e, v in exprs:
        key = (c, e)
        if key not in seen:
            seen.add(key)
            unique.append((c, e, v))

    return unique


def build_expected_lookup(expressions):
    """값 → [(상수, 수식, 기대값)] 역인덱스 구축"""
    # Round expected values to group near-identical ones
    lookup = defaultdict(list)
    for const_name, expr_str, expected in expressions:
        # Use rounded key for lookup
        if abs(expected) < 1e-12:
            rkey = 0.0
        else:
            rkey = round(expected, 8)
        lookup[rkey].append((const_name, expr_str, expected))
    return lookup


def match_value(value, lookup):
    """하나의 값에 대해 모든 매칭 찾기"""
    matches = []
    # Try exact rounded key
    rval = round(value, 8) if abs(value) > 1e-12 else 0.0

    # Check nearby keys (within 5% for NEAR grade)
    candidates = []
    for rkey, expr_list in lookup.items():
        for const_name, expr_str, expected in expr_list:
            err = pct_error(value, expected)
            g = grade(err)
            if g is not None:
                candidates.append((const_name, expr_str, expected, err, g))

    return candidates


def match_all_values_fast(values, expressions):
    """
    모든 값을 모든 수식과 매칭 — O(V*E) 이지만
    값이 ~6K, 수식이 ~10K 이므로 ~60M 비교 = 수 초.
    """
    discoveries = []
    total = len(values)

    for idx, val in enumerate(values):
        if idx % 1000 == 0 and idx > 0:
            print(f'  ... 스캔 중: {idx}/{total} 값 처리, {len(discoveries)} 발견', flush=True)

        for const_name, expr_str, expected in expressions:
            err = pct_error(val, expected)
            g = grade(err)
            if g is not None:
                discoveries.append({
                    'constant': const_name,
                    'value': str(val),
                    'expression': expr_str,
                    'expected': expected,
                    'error_pct': round(err, 6),
                    'grade': g,
                })

    return discoveries


# ═══════════════════════════════════════════════════════
# 메인
# ═══════════════════════════════════════════════════════
def main():
    print('=' * 70)
    print('  SINGULARITY EXHAUST — Group 1: phi(=2), mu(=1), P1(=2)')
    print('  목표: 포화까지 전수 탐색 (새 EXACT 0건 = 중단)')
    print('=' * 70)
    print()

    # 1. 로그 로드
    print('[1] discovery_log.jsonl 로드 중...')
    entries = load_log()
    print(f'    총 {len(entries):,}개 엔트리 로드')

    # 2. 고유값 수집
    print('[2] 고유 수치값 수집 중...')
    values = collect_unique_values(entries)
    print(f'    고유값 {len(values):,}개')

    # 3. 기존 키 수집 (중복 방지)
    print('[3] 기존 (constant, value) 키 수집...')
    existing_keys = collect_existing_keys(entries)
    print(f'    기존 키 {len(existing_keys):,}개')

    # 4. 수식 생성
    print('[4] 7단계 수식 생성 중...')
    expressions = generate_expressions()
    print(f'    총 수식 {len(expressions):,}개 생성')

    # Level별 수식 수 세기
    level_counts = defaultdict(int)
    for c, e, v in expressions:
        if e in ('phi', 'mu', 'P1'):
            level_counts['L1-direct'] += 1
        elif any(e.startswith(p) for p in ['sqrt(', 'cbrt(', 'log2(', 'ln(', '1/']):
            level_counts['L2-unary'] += 1
        elif e.count('*') + e.count('/') + e.count('+') + e.count('-') + e.count('^') == 1:
            level_counts['L3-binary'] += 1
        elif 'pi' in e or 'golden' in e or 'gamma' in e or 'zeta' in e or 'ln2' in e or 'ln3' in e or 'ln(4/3)' in e:
            level_counts['L7-transcendental'] += 1
        elif '/' in e and ('+' in e or '-' in e):
            level_counts['L6-egyptian'] += 1
        elif any(n in e for n in ['phi', 'mu', 'P1']) and sum(1 for n in ['phi', 'mu', 'P1'] if n in e) >= 2:
            level_counts['L5-cross'] += 1
        else:
            level_counts['L4-compound'] += 1

    for lv in sorted(level_counts.keys()):
        print(f'    {lv}: {level_counts[lv]:,}개')

    # 5. 전수 매칭
    pass_num = 0
    total_new = 0
    total_by_grade = defaultdict(int)
    all_new_entries = []

    while True:
        pass_num += 1
        print(f'\n{"─"*70}')
        print(f'  패스 #{pass_num} 시작 — 값 {len(values):,}개 × 수식 {len(expressions):,}개')
        print(f'{"─"*70}')

        raw_matches = match_all_values_fast(values, expressions)
        print(f'  원시 매칭: {len(raw_matches):,}개')

        # 6. 중복 제거 + 기존 키 필터
        dedup_key = set()
        new_discoveries = []
        for m in raw_matches:
            # 고유 키: (상수, 값, 수식)
            dk = (m['constant'], m['value'], m['expression'])
            # 기존 로그 키: (상수, 값) — 같은 상수+값이 이미 있으면 스킵
            ek = (m['constant'], m['value'])

            if dk in dedup_key:
                continue
            dedup_key.add(dk)

            # 기존에 같은 상수+값이 있으면 스킵 (다른 상수면 OK)
            if ek in existing_keys:
                continue

            new_discoveries.append(m)

        print(f'  중복제거 후: {len(new_discoveries):,}개 신규')

        # 등급별 집계
        grade_counts = defaultdict(int)
        for d in new_discoveries:
            grade_counts[d['grade']] += 1

        for g in ['EXACT', 'CLOSE', 'NEAR']:
            cnt = grade_counts.get(g, 0)
            print(f'    {g}: {cnt:,}')
            total_by_grade[g] += cnt

        # EXACT 0이면 포화 → 중단
        if grade_counts.get('EXACT', 0) == 0:
            print(f'\n  ★ 포화 도달! 패스 #{pass_num}에서 새 EXACT 0건.')
            break

        # 7. JSONL에 추가
        new_entries_for_log = []
        for d in new_discoveries:
            entry = {
                'constant': d['constant'],
                'value': d['value'],
                'grade': d['grade'],
                'source': 'singularity-exhaust-group1',
                'timestamp': TIMESTAMP,
                'processed': True,
                'expression': d['expression'],
                'error_pct': d['error_pct'],
                'alien_index': {'d': 1, 'r': 0},
                'mk2': {'sector': 'exhaust', 'paths': 1},
            }
            new_entries_for_log.append(entry)

        with open(LOG_PATH, 'a') as f:
            for entry in new_entries_for_log:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')

        # 기존 키 갱신
        for d in new_discoveries:
            existing_keys.add((d['constant'], d['value']))

        total_new += len(new_discoveries)
        all_new_entries.extend(new_entries_for_log)

        print(f'  ✓ {len(new_entries_for_log):,}개 discovery_log.jsonl에 추가 완료')

        # 다음 패스를 위해 — 새 값이 추가되었을 수도 있지만,
        # 이 스크립트에서는 새 값이 아니라 기존 값의 새 매칭을 찾는 것이므로
        # 1패스로 포화 판정 가능. 하지만 안전을 위해 루프.
        # phi=2, mu=1, P1=2 값은 고정이므로 수식 결과도 고정 → 1패스 후 무조건 포화.
        print(f'\n  (값/수식 고정 → 다음 패스 검증...)')

    # ═══════════════════════════════════════════════════════
    # 최종 요약
    # ═══════════════════════════════════════════════════════
    print(f'\n{"═"*70}')
    print(f'  최종 요약 — Group 1 소진 완료')
    print(f'{"═"*70}')
    print(f'  총 패스: {pass_num}')
    print(f'  총 신규 발견: {total_new:,}')
    for g in ['EXACT', 'CLOSE', 'NEAR']:
        print(f'    {g}: {total_by_grade.get(g, 0):,}')

    # 상수별 집계
    const_counts = defaultdict(lambda: defaultdict(int))
    for e in all_new_entries:
        const_counts[e['constant']][e['grade']] += 1
    print(f'\n  상수별:')
    for c in sorted(const_counts.keys()):
        parts = ', '.join(f'{g}={const_counts[c][g]}' for g in ['EXACT', 'CLOSE', 'NEAR'] if const_counts[c][g] > 0)
        print(f'    {c}: {parts}')

    # Top EXACT 발견 출력
    exact_entries = [e for e in all_new_entries if e['grade'] == 'EXACT']
    if exact_entries:
        print(f'\n  Top EXACT 발견 (최대 50개):')
        # 다양한 값 우선
        seen_vals = set()
        shown = 0
        for e in sorted(exact_entries, key=lambda x: float(x['value'])):
            v = e['value']
            if v in seen_vals:
                continue
            seen_vals.add(v)
            print(f'    {e["constant"]:5s} | {e["value"]:>12s} = {e["expression"]:<30s}')
            shown += 1
            if shown >= 50:
                break

    # 로그 최종 라인 수 확인
    with open(LOG_PATH, 'r') as f:
        final_count = sum(1 for _ in f)
    print(f'\n  discovery_log.jsonl 최종: {final_count:,}줄')
    print(f'{"═"*70}')


if __name__ == '__main__':
    main()
