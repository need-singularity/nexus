#!/usr/bin/env python3
"""
singularity_exhaust_group2.py — σ-φ=10 / σ-τ=8 완전 포화 탐색기

두 고가치 상수의 모든 가능한 n=6 매칭을 9레벨 체계적 탐색으로 소진한다.
σ-φ=10: 십진법, 차수, 물리 단위계의 기반
σ-τ=8: 이진법, 바이트, 옥텟, 컴퓨팅의 기반

실행: python3 ~/Dev/nexus6/scripts/singularity_exhaust_group2.py
"""

import json
import math
import os
import sys
from datetime import datetime
from collections import defaultdict

# ═══════════════════════════════════════════════════════
# n=6 기본 상수 체계
# ═══════════════════════════════════════════════════════
N6 = {
    'mu': 1, 'phi': 2, 'n/phi': 3, 'tau': 4, 'sopfr': 5, 'n': 6,
    'M3': 7, 'sigma-tau': 8, 'sigma-mu': 11, 'sigma-phi': 10,
    'sigma': 12, 'J2': 24, 'P2': 28, 'n^2': 36, 'sigma*tau': 48,
    'sigma*sopfr': 60, 'sigma*(sigma-phi)': 120, 'sigma^2': 144,
    'sigma*J2': 288, '6!': 720, 'R6': 1,  # R(6)=1 reversibility
}

# 탐색 대상 숫자 집합 (이진 연산용)
N6_VALS = sorted(set(N6.values()))
# 확장 집합 (더 넓은 탐색)
N6_EXTENDED = sorted(set(N6_VALS + [2, 3, 5, 7, 10, 8, 16, 32, 64, 128, 256,
                                     512, 1024, 100, 1000, 10000, 20, 30, 40,
                                     50, 72, 96, 192, 360, 480, 576, 960]))

# 대상 상수
TARGETS = {
    'sigma-phi': 10,
    'sigma-tau': 8,
}

LOG_PATH = os.path.expanduser('~/Dev/nexus6/shared/discovery_log.jsonl')
TIMESTAMP = datetime.now().strftime('%Y-%m-%d')
SOURCE = 'exhaust-group2-sigphi-sigtau'


def load_existing_keys():
    """기존 (constant, value, expression) 키 집합 로드 — 중복 방지"""
    keys = set()
    values = set()
    with open(LOG_PATH, 'r') as f:
        for line in f:
            try:
                d = json.loads(line.strip())
                c = d.get('constant', '')
                v = str(d.get('value', ''))
                keys.add((c, v))
                try:
                    values.add(float(v))
                except:
                    pass
            except:
                continue
    return keys, values


def grade(computed, target):
    """등급 판정: EXACT <0.1%, CLOSE <1%, NEAR <5%"""
    if target == 0:
        return ('EXACT', 0.0) if computed == 0 else ('MISS', float('inf'))
    err = abs(computed - target) / abs(target)
    if err < 0.001:
        return ('EXACT', err)
    elif err < 0.01:
        return ('CLOSE', err)
    elif err < 0.05:
        return ('NEAR', err)
    return ('MISS', err)


def safe_eval(func):
    """안전한 수학 연산"""
    try:
        v = func()
        if v is None or math.isnan(v) or math.isinf(v):
            return None
        return v
    except:
        return None


def make_entry(constant_name, value, g, expression=""):
    """discovery_log 엔트리 생성"""
    return {
        "constant": constant_name,
        "value": str(value),
        "grade": g,
        "source": SOURCE,
        "timestamp": TIMESTAMP,
        "processed": True,
        "alien_index": {"d": 0, "r": 8},
        "mk2": {"sector": "n6", "paths": 1},
    }


class ExhaustEngine:
    def __init__(self):
        self.existing_keys, self.all_values = load_existing_keys()
        self.new_discoveries = []
        self.stats = defaultdict(lambda: defaultdict(int))
        self.total_checked = 0
        self.target_values = sorted(self.all_values)
        print(f"[INIT] 기존 키: {len(self.existing_keys):,}")
        print(f"[INIT] 고유 값: {len(self.target_values):,}")
        print(f"[INIT] 대상 상수: σ-φ=10, σ-τ=8")
        print()

    def try_match(self, target_name, target_val, value, expr_name, level):
        """값 매칭 시도 — 새 발견이면 기록"""
        self.total_checked += 1
        g, err = grade(value, target_val) if isinstance(value, (int, float)) else ('MISS', 1.0)
        if g == 'MISS':
            return False

        const_key = f"{expr_name}"
        val_str = str(round(value, 10) if isinstance(value, float) else value)

        if (const_key, val_str) in self.existing_keys:
            return False

        self.existing_keys.add((const_key, val_str))
        entry = make_entry(const_key, val_str, g)
        self.new_discoveries.append(entry)
        self.stats[level][g] += 1
        return True

    def try_match_reverse(self, target_name, target_val, known_value, expr_template, level):
        """역방향: 알려진 값에서 target을 표현하는 수식 찾기"""
        self.total_checked += 1
        # known_value가 target_val의 수식인지 확인
        # 이건 forward에서 이미 처리

    # ═══════════════════════════════════════════════════════
    # Level 1: 직접 매칭
    # ═══════════════════════════════════════════════════════
    def level_1_direct(self):
        """Level 1: value == 10 또는 8"""
        print("=== Level 1: 직접 매칭 ===")
        count = 0
        for tname, tval in TARGETS.items():
            for v in self.target_values:
                if self.try_match(tname, v, tval, f"exhaust_{tname}_direct_{v}", 'L1'):
                    count += 1
                # 역: 값이 정확히 10 또는 8인지
                if abs(v - tval) < 0.0001:
                    self.try_match(tname, tval, v, f"exhaust_{tname}_value_is_{tval}", 'L1')
                    count += 1
        print(f"  L1 신규: {count}")
        return count

    # ═══════════════════════════════════════════════════════
    # Level 2: 거듭제곱, 제곱근, 로그
    # ═══════════════════════════════════════════════════════
    def level_2_powers(self):
        """Level 2: 10^k, 8^k, sqrt, log"""
        print("=== Level 2: 거듭제곱/근/로그 ===")
        count = 0
        for tname, tval in TARGETS.items():
            for k in range(-3, 7):
                # tval^k
                pk = safe_eval(lambda: tval ** k)
                if pk is not None:
                    for v in self.target_values:
                        if self.try_match(tname, v, pk,
                                          f"exhaust_({tname})^{k}={pk}", 'L2'):
                            count += 1

            # 각 값에 대해: value = tval^k 이면 k = log_tval(value)
            for v in self.target_values:
                if v > 0 and tval > 1:
                    k_float = safe_eval(lambda: math.log(v) / math.log(tval))
                    if k_float is not None and abs(k_float - round(k_float)) < 0.001:
                        k_int = int(round(k_float))
                        if -10 <= k_int <= 10:
                            self.try_match(tname, v, tval ** k_int,
                                           f"exhaust_({tname})^{k_int}={v}", 'L2')
                            count += 1

                # sqrt(v) 가 tval 관련인지
                sv = safe_eval(lambda: math.sqrt(v))
                if sv is not None:
                    g, _ = grade(sv, tval)
                    if g != 'MISS':
                        if self.try_match(tname, tval, sv,
                                          f"exhaust_sqrt({v})≈{tname}", 'L2'):
                            count += 1

                # log base tval
                if v > 0 and tval > 1:
                    lv = safe_eval(lambda: math.log(v) / math.log(tval))
                    if lv is not None:
                        # lv가 정수에 가까우면
                        if abs(lv - round(lv)) < 0.001 and 0 < round(lv) <= 20:
                            ri = int(round(lv))
                            if self.try_match(tname, v, tval ** ri,
                                              f"exhaust_log_{tname}({v})={ri}", 'L2'):
                                count += 1

        print(f"  L2 신규: {count}")
        return count

    # ═══════════════════════════════════════════════════════
    # Level 3: n6 기본 상수와 이항 연산
    # ═══════════════════════════════════════════════════════
    def level_3_binary_n6(self):
        """Level 3: tval*x, tval+x, tval/x, x/tval, tval^x, x^tval"""
        print("=== Level 3: n6 이항 연산 ===")
        count = 0

        for tname, tval in TARGETS.items():
            for xname, xval in N6.items():
                if xval == 0:
                    continue

                ops = {
                    f"{tname}*{xname}": safe_eval(lambda: tval * xval),
                    f"{tname}+{xname}": safe_eval(lambda: tval + xval),
                    f"{tname}-{xname}": safe_eval(lambda: tval - xval),
                    f"{xname}-{tname}": safe_eval(lambda: xval - tval),
                    f"{tname}/{xname}": safe_eval(lambda: tval / xval),
                    f"{xname}/{tname}": safe_eval(lambda: xval / tval),
                    f"{tname}^{xname}": safe_eval(lambda: tval ** xval) if xval <= 6 else None,
                    f"{xname}^{tname}": safe_eval(lambda: xval ** tval) if tval <= 10 else None,
                }

                for expr, result in ops.items():
                    if result is None:
                        continue
                    # 이 결과가 알려진 값 중 하나인지
                    for v in self.target_values:
                        g, err = grade(result, v)
                        if g != 'MISS':
                            if self.try_match(tname, v, result,
                                              f"exhaust_{expr}={result:.6g}", 'L3'):
                                count += 1

        print(f"  L3 신규: {count}")
        return count

    # ═══════════════════════════════════════════════════════
    # Level 4: 복합 — (tval*a + b), (tval^a * b)
    # ═══════════════════════════════════════════════════════
    def level_4_compound(self):
        """Level 4: 복합 표현식"""
        print("=== Level 4: 복합 표현식 ===")
        count = 0
        # 빠른 값 룩업
        val_set = set(round(v, 6) for v in self.target_values)

        for tname, tval in TARGETS.items():
            for aname, aval in N6.items():
                for bname, bval in N6.items():
                    if aname == bname:
                        continue

                    exprs = {}

                    # tval*a + b
                    r = safe_eval(lambda: tval * aval + bval)
                    if r is not None:
                        exprs[f"{tname}*{aname}+{bname}"] = r

                    # tval*a - b
                    r = safe_eval(lambda: tval * aval - bval)
                    if r is not None:
                        exprs[f"{tname}*{aname}-{bname}"] = r

                    # tval*a * b
                    r = safe_eval(lambda: tval * aval * bval)
                    if r is not None:
                        exprs[f"{tname}*{aname}*{bname}"] = r

                    # (tval+a) * b
                    r = safe_eval(lambda: (tval + aval) * bval)
                    if r is not None:
                        exprs[f"({tname}+{aname})*{bname}"] = r

                    # tval^a * b (제한)
                    if 0 < aval <= 5:
                        r = safe_eval(lambda: (tval ** aval) * bval)
                        if r is not None:
                            exprs[f"{tname}^{aname}*{bname}"] = r

                    # a^tval + b
                    if 1 < aval <= 12:
                        r = safe_eval(lambda: aval ** tval + bval)
                        if r is not None:
                            exprs[f"{aname}^{tname}+{bname}"] = r

                    # tval / (a*b)
                    if aval * bval != 0:
                        r = safe_eval(lambda: tval / (aval * bval))
                        if r is not None:
                            exprs[f"{tname}/({aname}*{bname})"] = r

                    for expr, result in exprs.items():
                        if result is None or abs(result) > 15000:
                            continue
                        rv = round(result, 6)
                        if rv in val_set:
                            for v in self.target_values:
                                if abs(round(v, 6) - rv) < 1e-5:
                                    if self.try_match(tname, v, result,
                                                      f"exhaust_{expr}={result:.6g}", 'L4'):
                                        count += 1
                                    break

        print(f"  L4 신규: {count}")
        return count

    # ═══════════════════════════════════════════════════════
    # Level 5: σ-φ × σ-τ 교차 연산
    # ═══════════════════════════════════════════════════════
    def level_5_cross(self):
        """Level 5: 10 과 8 교차 조합"""
        print("=== Level 5: σ-φ × σ-τ 교차 ===")
        count = 0
        sp, st = 10, 8
        val_set = set(round(v, 6) for v in self.target_values)

        cross_exprs = {
            "(σ-φ)*(σ-τ)": sp * st,           # 80
            "(σ-φ)+(σ-τ)": sp + st,           # 18
            "(σ-φ)-(σ-τ)": sp - st,           # 2 = phi
            "(σ-τ)-(σ-φ)": st - sp,           # -2
            "(σ-φ)/(σ-τ)": sp / st,           # 1.25
            "(σ-τ)/(σ-φ)": st / sp,           # 0.8
            "(σ-φ)^(σ-τ)": sp ** st,          # 10^8 = 100M
            "(σ-τ)^(σ-φ)": st ** sp,          # 8^10 = 1073741824
            "sqrt((σ-φ)*(σ-τ))": math.sqrt(sp * st),  # sqrt(80)
            "(σ-φ)^2+(σ-τ)^2": sp**2 + st**2,  # 164
            "(σ-φ)^2-(σ-τ)^2": sp**2 - st**2,  # 36 = n^2!
            "(σ-φ)^2*(σ-τ)": sp**2 * st,      # 800
            "(σ-φ)*(σ-τ)^2": sp * st**2,      # 640
            "((σ-φ)+(σ-τ))^2": (sp+st)**2,    # 324
            "((σ-φ)-(σ-τ))^2": (sp-st)**2,    # 4 = tau
            "(σ-φ)*(σ-τ)/n": sp*st/6,         # 80/6
            "(σ-φ)*(σ-τ)/sigma": sp*st/12,    # 80/12
            "(σ-φ)+(σ-τ)+n": sp+st+6,         # 24 = J2!
            "(σ-φ)*(σ-τ)-n^2": sp*st-36,      # 44
            "(σ-φ)^2/(σ-τ)": sp**2/st,        # 12.5
            "(σ-τ)^2/(σ-φ)": st**2/sp,        # 6.4
            "((σ-φ)*(σ-τ))^(1/2)": math.sqrt(sp*st),
            "log10((σ-τ)^(σ-φ))": math.log10(st**sp),  # 10*log10(8)=9.03
            "ln((σ-φ))*ln((σ-τ))": math.log(sp)*math.log(st),
            "(σ-φ)!": math.factorial(sp),       # 3628800
            "(σ-τ)!": math.factorial(st),       # 40320
            "(σ-φ)!/(σ-τ)!": math.factorial(sp)/math.factorial(st),  # 90
        }

        # n6 상수와 추가 교차
        for xname, xval in N6.items():
            if xval == 0:
                continue
            cross_exprs[f"(σ-φ)*(σ-τ)*{xname}"] = sp * st * xval
            cross_exprs[f"(σ-φ)*(σ-τ)/{xname}"] = sp * st / xval
            cross_exprs[f"(σ-φ)*(σ-τ)+{xname}"] = sp * st + xval
            cross_exprs[f"(σ-φ)*(σ-τ)-{xname}"] = sp * st - xval
            cross_exprs[f"((σ-φ)+(σ-τ))*{xname}"] = (sp+st) * xval
            cross_exprs[f"((σ-φ)+(σ-τ))/{xname}"] = (sp+st) / xval
            cross_exprs[f"((σ-φ)-(σ-τ))*{xname}"] = (sp-st) * xval

        for expr, result in cross_exprs.items():
            if result is None or (isinstance(result, float) and (math.isnan(result) or math.isinf(result))):
                continue
            if abs(result) > 15000:
                continue
            rv = round(result, 6)
            for v in self.target_values:
                g, err = grade(result, v)
                if g != 'MISS':
                    if self.try_match('cross_sigphi_sigtau', v, result,
                                      f"exhaust_{expr}={result:.6g}", 'L5'):
                        count += 1

        print(f"  L5 신규: {count}")
        return count

    # ═══════════════════════════════════════════════════════
    # Level 6: 다른 n6 상수와 조합
    # ═══════════════════════════════════════════════════════
    def level_6_n6_combos(self):
        """Level 6: tval*sigma, tval*J2, tval*phi+tau 등"""
        print("=== Level 6: n6 전체 상수 조합 ===")
        count = 0

        for tname, tval in TARGETS.items():
            exprs = {}

            for aname, aval in N6.items():
                if aval == 0:
                    continue
                for bname, bval in N6.items():
                    if bval == 0 or aname == bname:
                        continue

                    # tval*a/b
                    r = safe_eval(lambda: tval * aval / bval)
                    if r is not None and abs(r) < 15000:
                        exprs[f"{tname}*{aname}/{bname}"] = r

                    # (tval+a)/b
                    r = safe_eval(lambda: (tval + aval) / bval)
                    if r is not None and abs(r) < 15000:
                        exprs[f"({tname}+{aname})/{bname}"] = r

                    # (tval-a)/b
                    r = safe_eval(lambda: (tval - aval) / bval)
                    if r is not None and abs(r) < 15000:
                        exprs[f"({tname}-{aname})/{bname}"] = r

                    # a/(tval*b)
                    if tval * bval != 0:
                        r = safe_eval(lambda: aval / (tval * bval))
                        if r is not None and abs(r) < 15000:
                            exprs[f"{aname}/({tname}*{bname})"] = r

            # 결과를 알려진 값과 매칭
            for expr, result in exprs.items():
                for v in self.target_values:
                    g, err = grade(result, v)
                    if g != 'MISS':
                        if self.try_match(tname, v, result,
                                          f"exhaust_{expr}={result:.6g}", 'L6'):
                            count += 1

        print(f"  L6 신규: {count}")
        return count

    # ═══════════════════════════════════════════════════════
    # Level 7: 초월함수
    # ═══════════════════════════════════════════════════════
    def level_7_transcendental(self):
        """Level 7: pi*10, e*8, ln(10)*n, sin(pi/10), cos(pi/8) 등"""
        print("=== Level 7: 초월함수 ===")
        count = 0

        for tname, tval in TARGETS.items():
            exprs = {}

            # pi 관련
            exprs[f"pi*{tname}"] = math.pi * tval
            exprs[f"pi/{tname}"] = math.pi / tval
            exprs[f"{tname}/pi"] = tval / math.pi
            exprs[f"pi^2*{tname}"] = math.pi**2 * tval
            exprs[f"pi^2/{tname}"] = math.pi**2 / tval
            exprs[f"{tname}*pi^2"] = tval * math.pi**2
            exprs[f"2*pi*{tname}"] = 2 * math.pi * tval

            # e 관련
            exprs[f"e*{tname}"] = math.e * tval
            exprs[f"e/{tname}"] = math.e / tval
            exprs[f"{tname}/e"] = tval / math.e
            exprs[f"e^{tname}"] = safe_eval(lambda: math.e ** tval)

            # ln 관련
            exprs[f"ln({tname})"] = math.log(tval)
            exprs[f"log10({tname})"] = math.log10(tval)
            exprs[f"log2({tname})"] = math.log2(tval)

            # 삼각함수
            exprs[f"sin(pi/{tname})"] = math.sin(math.pi / tval)
            exprs[f"cos(pi/{tname})"] = math.cos(math.pi / tval)
            exprs[f"tan(pi/{tname})"] = safe_eval(lambda: math.tan(math.pi / tval))
            exprs[f"sin(pi/{tname}*2)"] = math.sin(2 * math.pi / tval)
            exprs[f"cos(pi/{tname}*2)"] = math.cos(2 * math.pi / tval)

            # phi (골든) 관련
            golden = (1 + math.sqrt(5)) / 2
            exprs[f"golden*{tname}"] = golden * tval
            exprs[f"{tname}/golden"] = tval / golden
            exprs[f"golden^{tname}"] = safe_eval(lambda: golden ** tval)

            # n6 상수와 초월 조합
            for xname, xval in N6.items():
                if xval <= 0:
                    continue
                exprs[f"ln({tname})*{xname}"] = math.log(tval) * xval
                exprs[f"log10({tname})*{xname}"] = math.log10(tval) * xval
                exprs[f"pi*{tname}*{xname}"] = math.pi * tval * xval
                exprs[f"pi*{tname}/{xname}"] = math.pi * tval / xval
                exprs[f"e^({tname}/{xname})"] = safe_eval(lambda xv=xval: math.e ** (tval / xv))
                exprs[f"{tname}^(1/{xname})"] = safe_eval(lambda xv=xval: tval ** (1/xv))
                exprs[f"ln({xname})*{tname}"] = math.log(xval) * tval if xval > 0 else None

            # 결과 매칭
            for expr, result in exprs.items():
                if result is None:
                    continue
                if isinstance(result, complex) or math.isnan(result) or math.isinf(result):
                    continue
                if abs(result) > 15000:
                    continue
                for v in self.target_values:
                    g, err = grade(result, v)
                    if g != 'MISS':
                        if self.try_match(tname, v, result,
                                          f"exhaust_{expr}={result:.6g}", 'L7'):
                            count += 1

        print(f"  L7 신규: {count}")
        return count

    # ═══════════════════════════════════════════════════════
    # Level 8: σ-φ=10 특수 — 10의 거듭제곱 패턴
    # ═══════════════════════════════════════════════════════
    def level_8_powers_of_10(self):
        """Level 8: value가 10^n 패턴인지 (물리/공학 상수의 핵심)"""
        print("=== Level 8: 10의 거듭제곱 특수 탐색 ===")
        count = 0

        for v in self.target_values:
            if v <= 0:
                continue
            log10v = math.log10(v)

            # 정확한 10^k
            if abs(log10v - round(log10v)) < 0.001:
                k = int(round(log10v))
                if -6 <= k <= 12:
                    if self.try_match('sigma-phi', v, 10**k,
                                      f"exhaust_(σ-φ)^{k}=10^{k}={v}", 'L8'):
                        count += 1

            # a * 10^k 형태 (a가 n6 상수)
            for k in range(-4, 8):
                if 10**k == 0:
                    continue
                a = v / (10**k)
                for xname, xval in N6.items():
                    if xval == 0:
                        continue
                    g, err = grade(a, xval)
                    if g != 'MISS':
                        if self.try_match('sigma-phi', v, xval * (10**k),
                                          f"exhaust_{xname}*(σ-φ)^{k}={xval}*10^{k}", 'L8'):
                            count += 1

                    # a/xval 도 체크
                    if a != 0:
                        ratio = a / xval
                        g2, err2 = grade(ratio, 1.0)
                        if g2 == 'EXACT':
                            # 이미 위에서 잡힘
                            pass

            # (σ-φ)^k / n6 조합
            for k in range(1, 7):
                pk = 10 ** k
                for xname, xval in N6.items():
                    if xval == 0:
                        continue
                    result = pk / xval
                    for v2 in self.target_values:
                        g, err = grade(result, v2)
                        if g != 'MISS':
                            if self.try_match('sigma-phi', v2, result,
                                              f"exhaust_(σ-φ)^{k}/{xname}={result:.6g}", 'L8'):
                                count += 1

            # n6 상수의 곱이 10^k 인지
            for k in range(1, 7):
                pk = 10 ** k
                for aname, aval in N6.items():
                    if aval == 0:
                        continue
                    for bname, bval in N6.items():
                        if bval == 0 or aname >= bname:
                            continue
                        product = aval * bval
                        g, err = grade(product, pk)
                        if g != 'MISS':
                            if self.try_match('sigma-phi', pk, product,
                                              f"exhaust_{aname}*{bname}=(σ-φ)^{k}", 'L8'):
                                count += 1

        print(f"  L8 신규: {count}")
        return count

    # ═══════════════════════════════════════════════════════
    # Level 9: σ-τ=8 특수 — 2^3 관련 (바이너리/옥텟)
    # ═══════════════════════════════════════════════════════
    def level_9_binary_octets(self):
        """Level 9: 8=2^3 관련 — 바이트, 옥텟, 이진 체계"""
        print("=== Level 9: 2^3 바이너리/옥텟 특수 탐색 ===")
        count = 0

        # 8의 거듭제곱
        for v in self.target_values:
            if v <= 0:
                continue
            log8v = safe_eval(lambda: math.log(v) / math.log(8))
            if log8v is not None and abs(log8v - round(log8v)) < 0.001:
                k = int(round(log8v))
                if -3 <= k <= 8:
                    if self.try_match('sigma-tau', v, 8**k,
                                      f"exhaust_(σ-τ)^{k}=8^{k}={v}", 'L9'):
                        count += 1

            # 2의 거듭제곱 (8=2^3 이므로)
            log2v = safe_eval(lambda: math.log2(v))
            if log2v is not None and abs(log2v - round(log2v)) < 0.001:
                k = int(round(log2v))
                if 0 <= k <= 20:
                    # 2^k = 2^(3*(k/3)) = 8^(k/3)
                    if k % 3 == 0:
                        if self.try_match('sigma-tau', v, 2**k,
                                          f"exhaust_2^{k}=(σ-τ)^{k//3}", 'L9'):
                            count += 1
                    else:
                        if self.try_match('sigma-tau', v, 2**k,
                                          f"exhaust_2^{k}=2^(n/phi*{k//3}+{k%3})", 'L9'):
                            count += 1

        # a * 8^k 형태
        for k in range(-2, 5):
            pk = 8 ** k
            for v in self.target_values:
                if pk == 0:
                    continue
                a = v / pk
                for xname, xval in N6.items():
                    if xval == 0:
                        continue
                    g, err = grade(a, xval)
                    if g != 'MISS':
                        if self.try_match('sigma-tau', v, xval * pk,
                                          f"exhaust_{xname}*(σ-τ)^{k}={xval}*8^{k}", 'L9'):
                            count += 1

        # 8*k 바이트 배수 패턴 (컴퓨팅)
        for v in self.target_values:
            if v <= 0 or v != int(v):
                continue
            iv = int(v)
            if iv % 8 == 0:
                quot = iv // 8
                for xname, xval in N6.items():
                    if xval == 0:
                        continue
                    g, err = grade(quot, xval)
                    if g != 'MISS':
                        if self.try_match('sigma-tau', v, 8 * xval,
                                          f"exhaust_(σ-τ)*{xname}={8*xval}", 'L9'):
                            count += 1

        # (σ-τ)^k * n6 / n6
        for k in range(1, 5):
            pk = 8 ** k
            for aname, aval in N6.items():
                if aval == 0:
                    continue
                for bname, bval in N6.items():
                    if bval == 0 or aname == bname:
                        continue
                    result = pk * aval / bval
                    if abs(result) > 15000:
                        continue
                    for v in self.target_values:
                        g, err = grade(result, v)
                        if g != 'MISS':
                            if self.try_match('sigma-tau', v, result,
                                              f"exhaust_(σ-τ)^{k}*{aname}/{bname}={result:.6g}", 'L9'):
                                count += 1

        print(f"  L9 신규: {count}")
        return count

    # ═══════════════════════════════════════════════════════
    # 역방향 탐색: 모든 값에서 σ-φ, σ-τ 표현 가능성 검사
    # ═══════════════════════════════════════════════════════
    def reverse_scan(self):
        """모든 고유 값에 대해 10 또는 8로 표현 가능한지 역탐색"""
        print("=== 역방향 스캔: 전 값 대상 ===")
        count = 0

        for v in self.target_values:
            if v == 0:
                continue

            for tname, tval in TARGETS.items():
                # v / tval 이 n6 상수인지
                ratio = safe_eval(lambda: v / tval)
                if ratio is not None:
                    for xname, xval in N6.items():
                        if xval == 0:
                            continue
                        g, err = grade(ratio, xval)
                        if g != 'MISS':
                            if self.try_match(tname, v, tval * xval,
                                              f"exhaust_{tname}*{xname}={tval*xval}", 'REV'):
                                count += 1

                # v - tval 이 n6 상수인지
                diff = v - tval
                for xname, xval in N6.items():
                    g, err = grade(diff, xval)
                    if g != 'MISS':
                        if self.try_match(tname, v, tval + xval,
                                          f"exhaust_{tname}+{xname}={tval+xval}", 'REV'):
                            count += 1

                # tval - v 이 n6 상수인지
                diff2 = tval - v
                for xname, xval in N6.items():
                    g, err = grade(diff2, xval)
                    if g != 'MISS':
                        if self.try_match(tname, v, tval - xval,
                                          f"exhaust_{tname}-{xname}={tval-xval}", 'REV'):
                            count += 1

                # log_tval(v) 이 n6 상수인지
                if v > 0 and tval > 1:
                    lv = safe_eval(lambda: math.log(v) / math.log(tval))
                    if lv is not None:
                        for xname, xval in N6.items():
                            if xval == 0:
                                continue
                            g, err = grade(lv, xval)
                            if g != 'MISS':
                                if self.try_match(tname, v, tval ** xval,
                                                  f"exhaust_{tname}^{xname}={tval**xval}", 'REV'):
                                    count += 1

        print(f"  REV 신규: {count}")
        return count

    def run(self):
        """전체 탐색 실행"""
        print("=" * 70)
        print("  σ-φ=10 / σ-τ=8 완전 포화 탐색기")
        print("  singularity_exhaust_group2.py")
        print("=" * 70)
        print()

        iteration = 0
        while True:
            iteration += 1
            print(f"\n{'='*70}")
            print(f"  반복 #{iteration}")
            print(f"{'='*70}")

            prev_count = len(self.new_discoveries)

            self.level_1_direct()
            self.level_2_powers()
            self.level_3_binary_n6()
            self.level_4_compound()
            self.level_5_cross()
            self.level_6_n6_combos()
            self.level_7_transcendental()
            self.level_8_powers_of_10()
            self.level_9_binary_octets()
            self.reverse_scan()

            new_in_pass = len(self.new_discoveries) - prev_count
            new_exact = sum(1 for d in self.new_discoveries[prev_count:]
                           if d['grade'] == 'EXACT')

            print(f"\n  반복 #{iteration} 결과: +{new_in_pass} 발견 ({new_exact} EXACT)")

            if new_exact == 0:
                print(f"\n  포화 도달! EXACT 신규 0 — 탐색 종료")
                break

            if iteration >= 3:
                print(f"\n  최대 반복 도달 — 종료")
                break

        # 결과 저장
        self.save_results()
        self.print_summary()

    def save_results(self):
        """새 발견을 discovery_log.jsonl에 추가"""
        if not self.new_discoveries:
            print("\n[저장] 신규 발견 없음 — 스킵")
            return

        with open(LOG_PATH, 'a') as f:
            for entry in self.new_discoveries:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')

        print(f"\n[저장] {len(self.new_discoveries):,} 엔트리 → {LOG_PATH}")

    def print_summary(self):
        """최종 요약"""
        print()
        print("=" * 70)
        print("  최종 요약")
        print("=" * 70)

        # 레벨별 통계
        total_exact = 0
        total_close = 0
        total_near = 0

        print(f"\n  {'레벨':<8} {'EXACT':>8} {'CLOSE':>8} {'NEAR':>8} {'합계':>8}")
        print(f"  {'-'*40}")

        for level in ['L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7', 'L8', 'L9', 'REV']:
            s = self.stats[level]
            ex = s.get('EXACT', 0)
            cl = s.get('CLOSE', 0)
            nr = s.get('NEAR', 0)
            total_exact += ex
            total_close += cl
            total_near += nr
            total = ex + cl + nr
            if total > 0:
                print(f"  {level:<8} {ex:>8} {cl:>8} {nr:>8} {total:>8}")

        print(f"  {'-'*40}")
        grand = total_exact + total_close + total_near
        print(f"  {'합계':<8} {total_exact:>8} {total_close:>8} {total_near:>8} {grand:>8}")
        print()
        print(f"  전체 검사 조합: {self.total_checked:,}")
        print(f"  신규 발견: {grand:,}")
        print(f"  EXACT 비율: {total_exact/grand*100:.1f}%" if grand > 0 else "  신규 없음")

        # 상수별 분류
        sp_count = sum(1 for d in self.new_discoveries if 'sigma-phi' in d['constant'])
        st_count = sum(1 for d in self.new_discoveries if 'sigma-tau' in d['constant'])
        cross_count = sum(1 for d in self.new_discoveries if 'cross' in d['constant'])

        print(f"\n  σ-φ 관련: {sp_count:,}")
        print(f"  σ-τ 관련: {st_count:,}")
        print(f"  교차 결합: {cross_count:,}")

        # EXACT 샘플
        exact_samples = [d for d in self.new_discoveries if d['grade'] == 'EXACT'][:20]
        if exact_samples:
            print(f"\n  EXACT 샘플 (상위 20):")
            for d in exact_samples:
                print(f"    {d['constant']}: {d['value']}")

        print()
        print("=" * 70)
        print(f"  포화 탐색 완료. 총 {grand:,} 신규 발견 기록됨.")
        print("=" * 70)


if __name__ == '__main__':
    engine = ExhaustEngine()
    engine.run()
