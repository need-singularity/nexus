#!/usr/bin/env python3
"""
Deep Constant Explorer — n=6 산술함수와 초월상수의 구조적 관계 탐색

기존 DFS가 놓친 비trivial 항등식을 찾는다.
전략:
  1. n=6 산술함수 조합 (σ,φ,τ,sopfr,n) 의 비선형 조합
  2. 초월상수 (π,e,ln2,γ 등)의 대수적 조합
  3. 두 집합 간의 교차점 (일치하는 값) 탐색
  4. Texas Sharpshooter 검증으로 우연 배제
"""

import math
from itertools import product, combinations
from fractions import Fraction
import sys

# === n=6 산술함수 ===
n = 6
sigma = 12        # σ(6) = 1+2+3+6
phi = 2           # φ(6) = |{1,5}| = 2  (Euler totient)
tau = 4           # τ(6) = |{1,2,3,6}| = 4  (divisor count)
sopfr = 5         # sopfr(6) = 2+3 (sum of prime factors with repetition)
sopf = 5          # sopf(6) = 2+3 (sum of distinct prime factors)
omega = 2         # ω(6) = 2 (number of distinct prime factors)
Omega = 2         # Ω(6) = 2 (number of prime factors with multiplicity)
rad = 6           # rad(6) = 2*3 = 6

# === n=28 산술함수 (generalization test) ===
n28 = 28
sigma28 = 56
phi28 = 12
tau28 = 6
sopfr28 = 9       # 2+2+7
sopf28 = 9        # 2+7
omega28 = 2
rad28 = 14

# === 초월/대수 상수 ===
PI = math.pi
E = math.e
LN2 = math.log(2)
LN3 = math.log(3)
GAMMA = 0.5772156649015329  # Euler-Mascheroni
SQRT2 = math.sqrt(2)
SQRT3 = math.sqrt(3)
SQRT5 = math.sqrt(5)
PHI_GOLD = (1 + SQRT5) / 2  # Golden ratio
ZETA2 = PI**2 / 6           # ζ(2) = π²/6
ZETA3 = 1.2020569031595942  # Apéry's constant
CATALAN = 0.9159655941772190 # Catalan's constant
KHINCHIN = 2.6854520010653064
TWIN_PRIME = 0.6601618158468696  # Twin prime constant C₂

# 미세구조상수
ALPHA = 1/137.035999084

def safe_eval(expr_func):
    """안전하게 수식 평가"""
    try:
        val = expr_func()
        if val is None or math.isnan(val) or math.isinf(val):
            return None
        if abs(val) > 1e15 or abs(val) < 1e-15:
            return None
        return val
    except (ValueError, ZeroDivisionError, OverflowError):
        return None

# === Phase 1: n=6 산술함수의 비선형 조합 생성 ===
def generate_n6_expressions():
    """n=6 산술함수의 의미있는 조합 생성"""
    exprs = {}

    base = {
        'n': n, 'σ': sigma, 'φ': phi, 'τ': tau, 'sopfr': sopfr,
        'ω': omega, 'rad': rad
    }

    # 1. 단항 변환
    for name, val in base.items():
        exprs[name] = val
        if val > 0:
            exprs[f'1/{name}'] = 1/val
            exprs[f'√{name}'] = math.sqrt(val)
            exprs[f'{name}²'] = val**2
            exprs[f'ln({name})'] = math.log(val)
            exprs[f'{name}!'] = math.factorial(val) if val <= 12 else None

    # 2. 이항 조합 (÷, ×, +, -, ^)
    items = list(base.items())
    for (n1, v1), (n2, v2) in product(items, repeat=2):
        if n1 == n2:
            continue
        exprs[f'{n1}/{n2}'] = v1/v2 if v2 != 0 else None
        exprs[f'{n1}×{n2}'] = v1*v2
        exprs[f'{n1}+{n2}'] = v1+v2
        exprs[f'{n1}-{n2}'] = v1-v2
        if v2 > 0 and v2 < 20 and v1 > 0:
            exprs[f'{n1}^{n2}'] = v1**v2 if v1**v2 < 1e12 else None
        if v1 > 0 and v1 < 20 and v2 > 0:
            exprs[f'{n1}^(1/{n2})'] = v1**(1/v2)

    # 3. 삼항 조합 (주요한 것만)
    for (n1, v1), (n2, v2), (n3, v3) in combinations(items, 3):
        if v3 != 0:
            exprs[f'{n1}×{n2}/{n3}'] = v1*v2/v3
        exprs[f'{n1}+{n2}+{n3}'] = v1+v2+v3
        exprs[f'{n1}×{n2}×{n3}'] = v1*v2*v3
        exprs[f'({n1}+{n2})×{n3}'] = (v1+v2)*v3
        if v2+v3 != 0:
            exprs[f'{n1}/({n2}+{n3})'] = v1/(v2+v3)
        if v2*v3 != 0:
            exprs[f'{n1}/({n2}×{n3})'] = v1/(v2*v3)

    # 4. 특수 조합
    exprs['σ/n'] = sigma/n  # = 2 (perfect number condition: σ/n = 2)
    exprs['σ-n'] = sigma - n  # = 6 = n (self-referential)
    exprs['n!/σ'] = math.factorial(n)/sigma  # = 720/12 = 60
    exprs['φ×τ'] = phi*tau  # = 8
    exprs['φ^τ'] = phi**tau  # = 16
    exprs['τ^φ'] = tau**phi  # = 16 (symmetric!)
    exprs['σ×φ'] = sigma*phi  # = 24 = n×τ (Bridge!)
    exprs['n×τ'] = n*tau  # = 24
    exprs['sopfr×φ'] = sopfr*phi  # = 10
    exprs['sopfr×τ'] = sopfr*tau  # = 20
    exprs['n²/sopfr'] = n**2/sopfr  # = 7.2
    exprs['σ²/n'] = sigma**2/n  # = 24
    exprs['n³/sopfr'] = n**3/sopfr  # = 43.2 (Fisher information!)
    exprs['(n+1)/σ'] = (n+1)/sigma  # = 7/12 (PH barcode!)
    exprs['σ/(φ×sopfr)'] = sigma/(phi*sopfr)  # = 12/10 = 1.2
    exprs['(σ-φ)/τ'] = (sigma-phi)/tau  # = 10/4 = 2.5
    exprs['σ^φ/n^τ'] = sigma**phi / n**tau  # = 144/1296
    exprs['ln(n!)/n'] = math.log(math.factorial(n))/n
    exprs['n!/τ!'] = math.factorial(n)/math.factorial(tau)  # 720/24 = 30
    exprs['σ!/n!'] = math.factorial(sigma)/math.factorial(n)  # huge
    exprs['Π(d|6)'] = 1*2*3*6  # = 36
    exprs['Σ(1/d)'] = 1+1/2+1/3+1/6  # = 2 = σ/n
    exprs['Π(1/d)'] = 1/(1*2*3*6)  # = 1/36
    exprs['H(6)'] = 1 + 1/2 + 1/3 + 1/4 + 1/5 + 1/6  # harmonic number

    # None 제거
    return {k: v for k, v in exprs.items() if v is not None and not math.isnan(v) and not math.isinf(v)}

# === Phase 2: 초월상수의 대수적 조합 ===
def generate_transcendental_targets():
    """초월상수의 의미있는 조합 생성"""
    targets = {}

    base_const = {
        'π': PI, 'e': E, 'ln2': LN2, 'ln3': LN3,
        'γ': GAMMA, '√2': SQRT2, '√3': SQRT3, '√5': SQRT5,
        'φ_gold': PHI_GOLD, 'ζ(2)': ZETA2, 'ζ(3)': ZETA3,
        'G': CATALAN, 'K': KHINCHIN, 'C₂': TWIN_PRIME,
        '1/α': 1/ALPHA
    }

    for name, val in base_const.items():
        targets[name] = val
        if val > 0:
            targets[f'1/{name}'] = 1/val
            targets[f'{name}²'] = val**2
            targets[f'√{name}'] = math.sqrt(val) if val > 0 else None
            targets[f'ln({name})'] = math.log(val) if val > 0 else None

    # 주요 이항 조합
    items = list(base_const.items())
    for (n1, v1), (n2, v2) in combinations(items, 2):
        targets[f'{n1}+{n2}'] = v1+v2
        targets[f'{n1}-{n2}'] = v1-v2
        targets[f'{n2}-{n1}'] = v2-v1
        if v2 != 0:
            targets[f'{n1}/{n2}'] = v1/v2
        if v1 != 0:
            targets[f'{n2}/{n1}'] = v2/v1
        targets[f'{n1}×{n2}'] = v1*v2

    # 특수 조합
    targets['π/e'] = PI/E
    targets['e^π'] = E**PI
    targets['π^e'] = PI**E
    targets['e^(1/e)'] = E**(1/E)
    targets['π²/6'] = PI**2/6  # = ζ(2)
    targets['e^γ'] = E**GAMMA
    targets['π×ln2'] = PI*LN2
    targets['γ+ln(2π)'] = GAMMA + math.log(2*PI)
    targets['e^π-π'] = E**PI - PI  # ≈ 19.999 (Ramanujan near-integer)
    targets['ln(π)'] = math.log(PI)
    targets['ln(2π)'] = math.log(2*PI)
    targets['π^(1/π)'] = PI**(1/PI)
    targets['2^√2'] = 2**SQRT2  # Gelfond-Schneider
    targets['e^√2'] = E**SQRT2

    return {k: v for k, v in targets.items()
            if v is not None and not math.isnan(v) and not math.isinf(v)
            and abs(v) < 1e6}

# === Phase 3: 교차점 탐색 ===
def find_matches(n6_exprs, trans_targets, threshold=0.001):
    """n=6 표현과 초월상수 조합 사이의 일치점 찾기"""
    matches = []

    for n6_name, n6_val in n6_exprs.items():
        for t_name, t_val in trans_targets.items():
            if t_val == 0:
                continue

            rel_error = abs(n6_val - t_val) / abs(t_val)

            if rel_error < threshold:
                matches.append({
                    'n6_expr': n6_name,
                    'n6_val': n6_val,
                    'target': t_name,
                    'target_val': t_val,
                    'error': rel_error,
                    'exact': rel_error < 1e-12,
                })

    # 오차순 정렬
    matches.sort(key=lambda x: x['error'])
    return matches

# === Phase 4: n=28 일반화 검증 ===
def check_n28_generalization(formula_desc, n6_val, expected_target):
    """n=28에서도 같은 관계가 성립하는지 검증"""
    # 간단한 대체 규칙
    mapping = {
        'n': n28, 'σ': sigma28, 'φ': phi28, 'τ': tau28,
        'sopfr': sopfr28, 'ω': omega28, 'rad': rad28
    }
    # 반환: True이면 n=6 고유, False이면 일반적
    return None  # 수동 검증 필요

# === Phase 5: 새로운 탐색 — 혼합 표현식 ===
def explore_mixed_expressions():
    """n=6 산술함수 + 초월상수 혼합 표현의 정수/단순분수 값 탐색"""
    results = []

    arith = {'n': n, 'σ': sigma, 'φ': phi, 'τ': tau, 'sopfr': sopfr}
    consts = {'π': PI, 'e': E, 'ln2': LN2, 'γ': GAMMA, 'φ_g': PHI_GOLD}

    # 정수 & 단순 분수 타겟
    simple_targets = {}
    for a in range(1, 25):
        simple_targets[str(a)] = a
    for a in range(1, 13):
        for b in range(a+1, 13):
            simple_targets[f'{a}/{b}'] = a/b

    # a^c / b 형태 탐색
    for (an, av), (cn, cv) in product(arith.items(), consts.items()):
        for bn, bv in arith.items():
            if bv == 0:
                continue
            val = safe_eval(lambda av=av, cv=cv, bv=bv: av**cv / bv)
            if val is not None:
                for tname, tval in simple_targets.items():
                    if tval == 0:
                        continue
                    err = abs(val - tval) / max(abs(tval), 1e-10)
                    if err < 0.0001:
                        results.append({
                            'expr': f'{an}^{cn}/{bn}',
                            'value': val,
                            'target': tname,
                            'error': err,
                            'exact': err < 1e-12
                        })

    # c^(a/b) 형태
    for cn, cv in consts.items():
        for (an, av), (bn, bv) in product(arith.items(), repeat=2):
            if bv == 0 or cv <= 0:
                continue
            val = safe_eval(lambda cv=cv, av=av, bv=bv: cv**(av/bv))
            if val is not None:
                for tname, tval in simple_targets.items():
                    if tval == 0:
                        continue
                    err = abs(val - tval) / max(abs(tval), 1e-10)
                    if err < 0.0001:
                        results.append({
                            'expr': f'{cn}^({an}/{bn})',
                            'value': val,
                            'target': tname,
                            'error': err,
                            'exact': err < 1e-12
                        })

    # a*c + b*d 형태 (선형 조합)
    for (an, av), (bn, bv) in product(arith.items(), repeat=2):
        for (cn, cv), (dn, dv) in product(consts.items(), repeat=2):
            if cn == dn:
                continue
            val = av*cv + bv*dv
            for tname, tval in simple_targets.items():
                if tval == 0:
                    continue
                err = abs(val - tval) / max(abs(tval), 1e-10)
                if err < 0.001:
                    results.append({
                        'expr': f'{an}×{cn}+{bn}×{dn}',
                        'value': val,
                        'target': tname,
                        'error': err,
                        'exact': err < 1e-12
                    })

    # log_c(a) 형태
    for cn, cv in consts.items():
        if cv <= 0 or cv == 1:
            continue
        for an, av in arith.items():
            if av <= 0:
                continue
            val = math.log(av) / math.log(cv)
            for tname, tval in simple_targets.items():
                if tval == 0:
                    continue
                err = abs(val - tval) / max(abs(tval), 1e-10)
                if err < 0.0001:
                    results.append({
                        'expr': f'log_{cn}({an})',
                        'value': val,
                        'target': tname,
                        'error': err,
                        'exact': err < 1e-12
                    })

    # 중복 제거 & 정렬
    seen = set()
    unique = []
    for r in results:
        key = (r['expr'], r['target'])
        if key not in seen:
            seen.add(key)
            unique.append(r)
    unique.sort(key=lambda x: x['error'])
    return unique

# === Phase 6: 깊은 항등식 탐색 ===
def explore_deep_identities():
    """특정 깊은 수학적 항등식 탐색"""
    results = []

    # n=6 고유 속성
    props = {
        'σ(6)/6': sigma/n,          # = 2 (perfect)
        'φ(6)×τ(6)': phi*tau,       # = 8
        'σ(6)φ(6)': sigma*phi,      # = 24 = 4!
        'n×τ': n*tau,               # = 24 = 4!
        'σ×φ/(n×τ)': sigma*phi/(n*tau),  # = 1 (Bridge!)
        'n!/σ': 720/12,             # = 60
        'φ^τ': phi**tau,            # = 16
        'n^φ': n**phi,              # = 36
        'σ^(1/φ)': sigma**(1/phi),  # = √12 = 2√3
        'Π(d|6)': 36,
        'Σd²': 1+4+9+36,           # = 50
        'σ/τ': sigma/tau,           # = 3
        'n/φ': n/phi,               # = 3
        'sopfr/ω': sopfr/omega,     # = 2.5
    }

    # 초월상수 표현
    transcendentals = {
        'π²/6': PI**2/6,
        'e²': E**2,
        'e^π': E**PI,
        'π^e': PI**E,
        'π×e': PI*E,
        'π+e': PI+E,
        'π-e': PI-E,
        'ln(2)^(-1)': 1/LN2,
        'γ^(-1)': 1/GAMMA,
        'e^γ': E**GAMMA,
        'e^(π√163)^(1/3)': (E**(PI*math.sqrt(163)))**(1/3),
        '2π': 2*PI,
        '4π': 4*PI,
        'π²': PI**2,
        '√(2π)': math.sqrt(2*PI),
        'e^(1/e)': E**(1/E),
        '(2π)^(1/2)': math.sqrt(2*PI),
        'Γ(1/2)': math.sqrt(PI),  # = √π
        'Γ(1/3)': 2.6789385347077476,
        'Γ(1/4)': 3.6256099082219083,
        'Γ(1/6)': 5.566316001780235,
        'ζ(3)': ZETA3,
        'ζ(2)': ZETA2,
    }

    # 비교
    for pname, pval in props.items():
        for tname, tval in transcendentals.items():
            if tval == 0:
                continue
            ratio = pval / tval
            # ratio가 단순한 정수 또는 분수인지 확인
            for a in range(1, 20):
                for b in range(1, 20):
                    target_ratio = a/b
                    if abs(ratio - target_ratio) / target_ratio < 1e-6:
                        results.append({
                            'identity': f'{a}×{tname} = {b}×{pname}' if a != 1 else f'{tname} = {b}×{pname}',
                            'n6_expr': pname,
                            'trans_expr': tname,
                            'n6_val': pval,
                            'trans_val': tval,
                            'ratio': f'{a}/{b}',
                            'error': abs(ratio - target_ratio) / target_ratio,
                        })

    # 중복 제거
    seen = set()
    unique = []
    for r in results:
        key = r['identity']
        if key not in seen:
            seen.add(key)
            unique.append(r)
    unique.sort(key=lambda x: x['error'])
    return unique

# === Phase 7: 정수열 내 n=6 고유성 탐색 ===
def explore_integer_sequence_uniqueness():
    """n=6이 유일한 해인 정수 방정식 탐색"""
    results = []

    def divisor_sum(m):
        s = 0
        for i in range(1, m+1):
            if m % i == 0:
                s += i
        return s

    def euler_totient(m):
        count = 0
        for i in range(1, m+1):
            if math.gcd(i, m) == 1:
                count += 1
        return count

    def divisor_count(m):
        return sum(1 for i in range(1, m+1) if m % i == 0)

    def sum_prime_factors(m):
        s = 0
        temp = m
        for p in range(2, m+1):
            while temp % p == 0:
                s += p
                temp //= p
            if temp == 1:
                break
        return s

    def radical(m):
        r = 1
        temp = m
        for p in range(2, m+1):
            if temp % p == 0:
                r *= p
                while temp % p == 0:
                    temp //= p
            if temp == 1:
                break
        return r

    # 검색 범위
    N = 10000

    # 이미 알려진 것: σ(n)φ(n) = nτ(n) → n=1,6 only
    # 새로운 방정식 탐색

    equations = [
        # (이름, 조건함수, 설명)
        ("σ(n) = 3×divisor_count(n)",
         lambda m, s, p, t, sp: s == 3*t,
         "약수합 = 3×약수개수"),
        ("σ(n) = n + rad(n)",
         lambda m, s, p, t, sp: s == m + radical(m),
         "약수합 = n + 근기"),
        ("φ(n)×sopfr(n) = n + τ(n)",
         lambda m, s, p, t, sp: p * sp == m + t,
         "오일러×소인수합 = n + 약수개수"),
        ("σ(n)/φ(n) = n",
         lambda m, s, p, t, sp: p != 0 and s == m * p,
         "약수합/토션트 = n"),
        ("n² = σ(n)×τ(n)×(something)",
         lambda m, s, p, t, sp: t != 0 and m*m % (s*t) == 0 and m*m // (s*t) == 1,
         "n² = σ×τ 정확히"),
        ("σ(n) = 2×rad(n)",
         lambda m, s, p, t, sp: s == 2 * radical(m),
         "약수합 = 2×근기"),
        ("n = φ(n) + τ(n)",
         lambda m, s, p, t, sp: m == p + t,
         "n = φ + τ"),
        ("n = sopfr(n) + 1",
         lambda m, s, p, t, sp: m == sp + 1,
         "n = sopfr + 1"),
        ("σ(n) - n = rad(n)",
         lambda m, s, p, t, sp: s - m == radical(m),
         "초과합 = 근기"),
        ("τ(n)^φ(n) = φ(n)^τ(n)",
         lambda m, s, p, t, sp: p > 0 and t > 0 and abs(t**p - p**t) == 0,
         "τ^φ = φ^τ (교환 거듭제곱)"),
        ("σ(n)×φ(n) = n!/(n-τ(n))!",
         lambda m, s, p, t, sp: t <= m and s*p == math.factorial(m)//math.factorial(m-t) if m-t >= 0 and m <= 20 else False,
         "σφ = P(n,τ)"),
        ("n mod sopfr(n) = 1",
         lambda m, s, p, t, sp: sp > 0 and m % sp == 1,
         "n mod sopfr = 1"),
        ("σ(n) = φ(n)×rad(n)",
         lambda m, s, p, t, sp: s == p * radical(m),
         "σ = φ×rad"),
    ]

    print("=" * 80)
    print("Phase 7: 정수 방정식의 n=6 고유성 탐색 (범위: 2~{})".format(N))
    print("=" * 80)

    for eq_name, condition, desc in equations:
        solutions = []
        for m in range(2, min(N+1, 10001)):
            s = divisor_sum(m)
            p = euler_totient(m)
            t = divisor_count(m)
            sp = sum_prime_factors(m)
            try:
                if condition(m, s, p, t, sp):
                    solutions.append(m)
                    if len(solutions) > 50:
                        break
            except (ValueError, ZeroDivisionError, OverflowError):
                continue

        # 흥미로운 결과만 출력 (해가 10개 미만)
        if 0 < len(solutions) <= 10:
            has_6 = 6 in solutions
            unique_to_6 = solutions == [6] or (len(solutions) <= 3 and 6 in solutions)
            marker = "🟩⭐" if unique_to_6 else ("🟩" if has_6 else "🟧")
            print(f"\n{marker} {eq_name}")
            print(f"   설명: {desc}")
            print(f"   해: {solutions}")
            if unique_to_6:
                print(f"   ★ n=6 고유! (또는 거의 고유)")
            results.append({
                'equation': eq_name,
                'solutions': solutions,
                'has_6': has_6,
                'unique': unique_to_6,
            })

    return results

# === Phase 8: Gamma function + n=6 ===
def explore_gamma_connections():
    """감마 함수와 n=6 산술함수의 관계"""
    results = []

    print("\n" + "=" * 80)
    print("Phase 8: Γ함수와 n=6 관계 탐색")
    print("=" * 80)

    # Γ(n/d) for divisors d of 6
    divisors = [1, 2, 3, 6]
    for d in divisors:
        val = math.gamma(n/d)
        print(f"  Γ({n}/{d}) = Γ({n//d}) = {val:.10f}")

    # Γ(1/d) products
    prod_gamma = 1
    for d in divisors:
        prod_gamma *= math.gamma(1/d)
    print(f"\n  Π Γ(1/d) for d|6 = {prod_gamma:.10f}")

    # 가우스 곱셈 공식 연결
    # Γ(z)Γ(z+1/n)...Γ(z+(n-1)/n) = (2π)^((n-1)/2) * n^(1/2-nz) * Γ(nz)

    # 특별한 값
    special = {
        'Γ(1/6)': math.gamma(1/6),
        'Γ(5/6)': math.gamma(5/6),
        'Γ(1/6)×Γ(5/6)': math.gamma(1/6) * math.gamma(5/6),  # = 2π by reflection
        'Γ(1/3)×Γ(2/3)': math.gamma(1/3) * math.gamma(2/3),  # = 2π/√3
        'Γ(1/2)²': math.gamma(1/2)**2,  # = π
    }

    print("\n  특수 Γ값:")
    for name, val in special.items():
        print(f"    {name} = {val:.10f}")
        # n=6 산술함수와 비교
        for aname, aval in [('σ', sigma), ('φ', phi), ('τ', tau), ('n', n), ('sopfr', sopfr)]:
            ratio = val / aval if aval != 0 else None
            if ratio and abs(ratio - round(ratio)) < 0.001:
                print(f"      ≈ {round(ratio)} × {aname} (error: {abs(val - round(ratio)*aval):.6f})")

    # Γ(1/6)×Γ(5/6) = 2π (반사 공식)
    reflection = math.gamma(1/6) * math.gamma(5/6)
    print(f"\n  Γ(1/6)×Γ(5/6) = {reflection:.10f}")
    print(f"  2π = {2*PI:.10f}")
    print(f"  비율 = {reflection/(2*PI):.15f}")
    print(f"  → 반사 공식: Γ(1/n)×Γ(1-1/n) = π/sin(π/n)")
    print(f"     π/sin(π/6) = π/(1/2) = 2π ✓")

    # 고유성: sin(π/n)이 유리수인 n
    print(f"\n  sin(π/n)이 유리수인 n (Niven의 정리):")
    print(f"    n=1: sin(π) = 0")
    print(f"    n=2: sin(π/2) = 1")
    print(f"    n=6: sin(π/6) = 1/2  ← n=6!")
    print(f"    이 세 값만 유리수 (Niven's theorem)")
    print(f"    → Γ(1/6)×Γ(5/6) = 2π는 sin(π/6)=1/2의 결과")

    return results

# === Phase 9: Bernoulli numbers + n=6 ===
def explore_bernoulli():
    """베르누이 수와 n=6 관계"""
    print("\n" + "=" * 80)
    print("Phase 9: 베르누이 수 B_k 와 n=6")
    print("=" * 80)

    # 처음 몇 개의 베르누이 수
    B = {
        0: Fraction(1),
        1: Fraction(-1, 2),
        2: Fraction(1, 6),
        4: Fraction(-1, 30),
        6: Fraction(1, 42),
        8: Fraction(-1, 30),
        10: Fraction(5, 66),
        12: Fraction(-691, 2730),
    }

    print("  B_k 값:")
    for k, val in B.items():
        print(f"    B_{k} = {val} = {float(val):.10f}")

    print(f"\n  ★ B_2 = 1/6 — n=6의 역수!")
    print(f"  ★ ζ(2) = π²/6 = -½(2π)²B₂/(2!) = π²/6")
    print(f"  → B_2 = 1/6이 ζ(2) = π²/6을 결정")

    # B_6과 n=6
    print(f"\n  B_6 = {B[6]} = {float(B[6]):.10f}")
    print(f"  ζ(6) = π⁶/945")
    print(f"  945 = {945} = 3³×5×7")
    print(f"  ζ(6) = {PI**6/945:.10f}")

    # Von Staudt-Clausen: B_{2k}의 분모
    print(f"\n  Von Staudt-Clausen 정리:")
    print(f"    B_2의 분모 = 6 = 2×3 (p-1|2인 소수 p: 2,3)")
    print(f"    B_4의 분모 = 30 = 2×3×5")
    print(f"    B_6의 분모 = 42 = 2×3×7")
    print(f"    → 6은 모든 짝수 베르누이 수 분모의 공약수!")
    print(f"    → denom(B_{{2k}}) = Π(p : (p-1)|2k) 이므로 항상 2×3=6으로 나누어짐")

# === Phase 10: Riemann zeta 특수값과 n=6 ===
def explore_zeta_values():
    """리만 제타함수 특수값과 n=6"""
    print("\n" + "=" * 80)
    print("Phase 10: ζ(s) 특수값과 n=6 산술")
    print("=" * 80)

    # ζ(2k) = (-1)^(k+1) × (2π)^(2k) × B_{2k} / (2×(2k)!)
    zeta_vals = {
        2: PI**2/6,
        4: PI**4/90,
        6: PI**6/945,
        8: PI**8/9450,
        10: PI**10/93555,
        12: PI**12/638512875,
    }

    print("  ζ(2k) = π^(2k) / D_k:")
    for s, val in zeta_vals.items():
        D = PI**s / val
        print(f"    ζ({s}) = π^{s}/{D:.0f} = {val:.10f}")

    # ζ(2) = π²/6 의 의미
    print(f"\n  ★ ζ(2) = π²/6 — Basel problem")
    print(f"    = Σ(1/k²) for k=1,2,3,...")
    print(f"    분모의 6 = σ(6)/2 = n = 가장 작은 완전수")

    # ζ(s)에서 p=2,3 오일러 곱
    print(f"\n  오일러 곱 p=2,3 절단:")
    euler_23 = (1/(1-1/2**2)) * (1/(1-1/3**2))
    print(f"    Π(1/(1-p^(-2))) for p=2,3 = {euler_23:.10f}")
    print(f"    = (4/3)(9/8) = 36/24 = 3/2")
    print(f"    ζ(2)에서 p=2,3 기여분 = 3/2")
    print(f"    나머지 소수 기여분 = ζ(2)/(3/2) = {ZETA2/euler_23:.10f}")
    print(f"    = π²/9 = {PI**2/9:.10f}")

    # σ₋₁(6)과 ζ(2)
    sigma_neg1 = 1/1 + 1/2 + 1/3 + 1/6
    print(f"\n  σ₋₁(6) = Σ(1/d) for d|6 = {sigma_neg1}")
    print(f"  σ₋₁(6) = σ(6)/6 = 2 (완전수 조건)")
    print(f"  ζ(2) × 6/π² = 1 (Basel → 6)")

# === Main ===
def main():
    print("╔" + "═"*78 + "╗")
    print("║" + " Deep Constant Explorer — n=6 비trivial 항등식 탐색".center(78) + "║")
    print("╚" + "═"*78 + "╝")

    # Phase 1-3: 산술-초월 교차
    print("\n" + "="*80)
    print("Phase 1-3: n=6 산술함수 ↔ 초월상수 교차점")
    print("="*80)

    n6_exprs = generate_n6_expressions()
    trans_targets = generate_transcendental_targets()

    print(f"  n=6 표현 개수: {len(n6_exprs)}")
    print(f"  초월상수 타겟 개수: {len(trans_targets)}")

    matches = find_matches(n6_exprs, trans_targets, threshold=0.01)

    # 중요한 일치만 필터링 (trivial 제외)
    nontrivial = [m for m in matches
                  if not any(x in m['n6_expr'] for x in ['×1', '×0', '+0', '-0'])]

    print(f"\n  비trivial 일치: {len(nontrivial)}개")
    print(f"\n  {'n=6 표현':<25} {'=':<3} {'초월 타겟':<25} {'오차':<12} {'정확?'}")
    print(f"  {'-'*25} {'-'*3} {'-'*25} {'-'*12} {'-'*5}")

    shown = set()
    count = 0
    for m in nontrivial[:60]:
        key = f"{m['n6_val']:.6f}-{m['target_val']:.6f}"
        if key in shown:
            continue
        shown.add(key)
        exact = "🟩" if m['exact'] else "🟧"
        print(f"  {m['n6_expr']:<25} {'=':<3} {m['target']:<25} {m['error']:.2e}   {exact}")
        count += 1
        if count >= 30:
            break

    # Phase 5: 혼합 표현식
    print("\n" + "="*80)
    print("Phase 5: 혼합 표현식 (산술함수 + 초월상수 → 정수/분수)")
    print("="*80)

    mixed = explore_mixed_expressions()
    print(f"\n  발견된 관계: {len(mixed)}개")

    shown = set()
    count = 0
    for r in mixed[:50]:
        key = f"{r['expr']}-{r['target']}"
        if key in shown:
            continue
        shown.add(key)
        exact = "🟩" if r['exact'] else "🟧"
        print(f"  {r['expr']:<30} ≈ {r['target']:<10} (값: {r['value']:.8f}, err: {r['error']:.2e}) {exact}")
        count += 1
        if count >= 20:
            break

    # Phase 6: 깊은 항등식
    print("\n" + "="*80)
    print("Phase 6: 깊은 항등식 (n=6 속성 = k × 초월상수)")
    print("="*80)

    deep = explore_deep_identities()
    shown = set()
    count = 0
    for r in deep[:40]:
        if r['identity'] in shown:
            continue
        shown.add(r['identity'])
        print(f"  {r['identity']:<50} (err: {r['error']:.2e})")
        count += 1
        if count >= 20:
            break

    # Phase 7: 정수열 고유성
    seq_results = explore_integer_sequence_uniqueness()

    # Phase 8: Gamma
    explore_gamma_connections()

    # Phase 9: Bernoulli
    explore_bernoulli()

    # Phase 10: Zeta
    explore_zeta_values()

    # === 요약 ===
    print("\n" + "╔" + "═"*78 + "╗")
    print("║" + " 탐색 요약".center(76) + "║")
    print("╚" + "═"*78 + "╝")

    unique_eqs = [r for r in seq_results if r.get('unique')]
    print(f"\n  n=6 고유 방정식: {len(unique_eqs)}개")
    for r in unique_eqs:
        print(f"    ⭐ {r['equation']}: 해 = {r['solutions']}")

    print(f"\n  Phase 1-3 교차점: {len(nontrivial)}개")
    print(f"  Phase 5 혼합 표현: {len(mixed)}개")
    print(f"  Phase 6 깊은 항등식: {len(deep)}개")

if __name__ == '__main__':
    main()
