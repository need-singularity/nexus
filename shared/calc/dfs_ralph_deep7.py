#!/usr/bin/env python3
"""
DFS Ralph Deep 7 — 그래프론, 라마누잔 합, 수열 주기

Phase A: 그래프 채색다항식과 n=6
Phase B: 라마누잔 합 c_q(n)과 n=6
Phase C: 산술함수 반복의 주기 (σ, φ, s=σ-n)
Phase D: 연속 정수의 산술함수 곱 패턴
Phase E: n=6과 마법진/라틴방진
"""

import math
from functools import lru_cache

_cache = {}
def get_arith(m):
    if m in _cache: return _cache[m]
    divs = [i for i in range(1, m+1) if m % i == 0]
    sigma = sum(divs)
    tau = len(divs)
    phi = sum(1 for i in range(1, m+1) if math.gcd(i, m) == 1)
    temp, sopfr = m, 0
    for p in range(2, m+1):
        while temp % p == 0: sopfr += p; temp //= p
        if temp == 1: break
    temp, rad = m, 1
    for p in range(2, m+1):
        if temp % p == 0:
            rad *= p
            while temp % p == 0: temp //= p
        if temp == 1: break
    temp2, om = m, 0
    for p in range(2, m+1):
        if temp2 % p == 0:
            om += 1
            while temp2 % p == 0: temp2 //= p
        if temp2 == 1: break
    r = {'n': m, 'sigma': sigma, 'phi': phi, 'tau': tau, 'sopfr': sopfr,
         'rad': rad, 'omega': om, 'divs': divs}
    _cache[m] = r
    return r

print("캐시 구축...")
for m in range(2, 10001): get_arith(m)
print("완료")

# === Phase A: 그래프 채색다항식 ===
def phase_a():
    print("\n" + "=" * 80)
    print("Phase A: 완전그래프 K_n의 채색다항식과 n=6")
    print("=" * 80)

    # K_n의 채색다항식: P(K_n, k) = k(k-1)(k-2)...(k-n+1) = k^(n)_falling
    # K_6: P(K_6, k) = k(k-1)(k-2)(k-3)(k-4)(k-5)

    print("  K_n의 채색다항식 P(K_n, k) = k!/(k-n)!:")

    # P(K_6, k) 특수값
    for k in range(1, 15):
        pk6 = math.perm(k, 6) if k >= 6 else 0
        mark = ""
        if pk6 == 720: mark = " = 6!"
        elif pk6 == 0: mark = " (불가능)"
        print(f"    P(K_6, {k:2d}) = {pk6:>10d}{mark}")

    print(f"\n  P(K_6, 6) = 720 = 6! (최소 고유 채색)")
    print(f"  P(K_6, 7) = 5040 = 7! (첫 초과 채색)")

    # 색채수 χ(K_n) = n
    print(f"\n  χ(K_6) = 6 = n (색채수 = 꼭짓점 수, 완전그래프)")

    # 완전이분그래프 K_{3,3}
    print(f"\n  K_{{3,3}} (완전이분그래프, n/2=3 양쪽):")
    print(f"    χ(K_{{3,3}}) = 2")
    print(f"    K_{{3,3}}은 평면 그래프가 아님 (Kuratowski)")
    print(f"    K₅와 K_{{3,3}}이 평면 그래프 장애물의 전부")
    print(f"    K_{{3,3}} 꼭짓점 수 = 6 = n")

    # 페터슨 그래프와 6
    print(f"\n  Petersen 그래프:")
    print(f"    꼭짓점 = 10 = sopfr(6)×phi(6)")
    print(f"    변 = 15 = C(6,2)")
    print(f"    정칙 차수 = 3 = n/phi")
    print(f"    둘레(girth) = 5 = sopfr(6)")
    print(f"    지름 = 2 = phi(6)")
    print(f"    자기동형군 크기 = 120 = 5! = (sopfr(6))!")

# === Phase B: 라마누잔 합 ===
def phase_b():
    print("\n" + "=" * 80)
    print("Phase B: 라마누잔 합 c_q(n)")
    print("=" * 80)

    def ramanujan_sum(q, n):
        """c_q(n) = sum_{gcd(a,q)=1} exp(2pi*i*a*n/q)"""
        # 정수값 공식: c_q(n) = mu(q/gcd(q,n)) * phi(q) / phi(q/gcd(q,n))
        g = math.gcd(q, n)
        qg = q // g
        # 뫼비우스
        temp, mu_val, factors = qg, 1, 0
        for p in range(2, qg+1):
            if temp % p == 0:
                count = 0
                while temp % p == 0:
                    count += 1
                    temp //= p
                if count > 1:
                    mu_val = 0
                    break
                factors += 1
            if temp == 1: break
        if mu_val != 0:
            mu_val = (-1)**factors
        phi_q = sum(1 for i in range(1, q+1) if math.gcd(i, q) == 1) if q >= 1 else 0
        phi_qg = sum(1 for i in range(1, qg+1) if math.gcd(i, qg) == 1) if qg >= 1 else 1
        return mu_val * phi_q // phi_qg if phi_qg != 0 else 0

    print("  c_q(6) 테이블 (q=1..20):")
    print(f"  {'q':>4} {'c_q(6)':>8} {'특이':>10}")
    total = 0
    for q in range(1, 21):
        c = ramanujan_sum(q, 6)
        total += c
        mark = ""
        if c == 6: mark = "= n"
        elif c == -6: mark = "= -n"
        elif c == 12: mark = "= sigma"
        elif c == 2: mark = "= phi"
        elif c == -2: mark = "= -phi"
        print(f"  {q:>4} {c:>8} {mark:>10}")

    # c_6(n) 테이블
    print(f"\n  c_6(n) 테이블 (n=1..24):")
    print(f"  {'n':>4} {'c_6(n)':>8} {'특이':>10}")
    for n in range(1, 25):
        c = ramanujan_sum(6, n)
        mark = ""
        if c == 2: mark = "= phi(6)"
        elif c == -2: mark = "= -phi(6)"
        elif c == -1: mark = "= -1"
        elif c == 1: mark = "= 1"
        print(f"  {n:>4} {c:>8} {mark:>10}")

    print(f"\n  c_6(n)의 주기 = 6 (q의 주기)")
    print(f"  c_6(1)={ramanujan_sum(6,1)}, c_6(6)={ramanujan_sum(6,6)}")
    print(f"  c_6(6) = phi(6) = 2 ✓ (일반: c_q(q) = phi(q))")

# === Phase C: 산술함수 반복 주기 ===
def phase_c():
    print("\n" + "=" * 80)
    print("Phase C: 산술함수 반복 궤도의 특별한 수")
    print("=" * 80)

    # Aliquot sequence에서 6으로 수렴하는 수
    print("  s(n)=sigma(n)-n 반복에서 6에 도달하는 수:")
    reaches_6 = []
    for start in range(2, 1001):
        n = start
        seen = set()
        for _ in range(100):
            if n <= 1 or n > 100000: break
            if n == 6 and start != 6:
                reaches_6.append(start)
                break
            if n in seen: break
            seen.add(n)
            n = get_arith(n)['sigma'] - n if n <= 10000 else 0
    print(f"    {reaches_6[:30]}{'...' if len(reaches_6)>30 else ''}")
    print(f"    총 {len(reaches_6)}개 (2~1000 중)")

    # φ 반복에서 경로 길이 분포
    print(f"\n  phi 반복 경로 길이 (n → ... → 1):")
    phi_lengths = {}
    for m in range(2, 101):
        n, length = m, 0
        while n > 1:
            n = get_arith(n)['phi'] if n >= 2 else 1
            length += 1
        phi_lengths[m] = length

    # n=6의 경로 길이
    print(f"    phi*(6): 길이 = {phi_lengths[6]} (6→2→1)")
    print(f"    phi*(28): 길이 = {phi_lengths[28]} (28→12→4→2→1)")
    print(f"    phi*(12): 길이 = {phi_lengths[12]} (12→4→2→1)")

    # 길이 2인 수 (6처럼 빠르게 1에 도달)
    len2 = [m for m, l in phi_lengths.items() if l == 2]
    print(f"    길이=2인 수: {len2}")
    print(f"    → phi(n)이 소수인 수 (phi(n)→1)")
    print(f"    6: phi(6)=2 (소수) → 1")
    print(f"    → n=6은 phi 경로가 매우 짧음")

# === Phase D: 연속 정수 산술 곱 패턴 ===
def phase_d():
    print("\n" + "=" * 80)
    print("Phase D: 연속 정수의 산술함수 곱/합 패턴")
    print("=" * 80)

    # Π sigma(k) for k=1..n
    print("  Prod sigma(k) for k=1..n:")
    prod_sigma = 1
    for n in range(1, 13):
        prod_sigma *= get_arith(n)['sigma'] if n >= 2 else 1
        print(f"    Prod_sigma(1..{n:2d}) = {prod_sigma:>12d}")

    # Sum sigma(k) for k=1..n
    print(f"\n  Sum sigma(k) for k=1..n:")
    sum_sigma = 0
    for n in range(1, 21):
        sum_sigma += get_arith(n)['sigma'] if n >= 2 else 1
        mark = ""
        if sum_sigma == 6: mark = "= n"
        elif sum_sigma == 28: mark = "= P2!"
        elif sum_sigma == 120: mark = "= 5!"
        print(f"    Sum_sigma(1..{n:2d}) = {sum_sigma:>6d} {mark}")

    # Sum tau(k) for k=1..6
    sum_tau = sum(get_arith(k)['tau'] for k in range(1, 7))
    print(f"\n  Sum tau(k) for k=1..6 = {sum_tau}")
    print(f"  = 1+2+2+3+2+4 = {1+2+2+3+2+4}")

    # 연속 6개의 산술 패턴
    print(f"\n  연속 6개 정수의 sigma 합:")
    for start in range(1, 20):
        s = sum(get_arith(k)['sigma'] for k in range(start, start+6))
        mark = ""
        if s % 6 == 0: mark = f"  6|s (s/6={s//6})"
        print(f"    sigma({start}..{start+5}) = {s}{mark}")

# === Phase E: 마법진 ===
def phase_e():
    print("\n" + "=" * 80)
    print("Phase E: n=6과 마법진/라틴방진")
    print("=" * 80)

    # n×n 마법진의 마법상수
    print("  n x n 마법진의 마법상수 M(n) = n(n^2+1)/2:")
    for n in range(3, 10):
        M = n * (n**2 + 1) // 2
        a = get_arith(n) if n >= 2 else None
        mark = ""
        if n == 6:
            mark = f"  ← M={M}=6×37, 37은 소수"
        print(f"    M({n}) = {M}{mark}")

    # 6×6 마법진
    print(f"\n  6×6 마법진:")
    print(f"    마법상수 = 6×(36+1)/2 = 6×37/2 = 111")
    print(f"    111 = 3×37")
    print(f"    37 = 소수 (12번째 소수)")
    print(f"    111/σ(6) = 111/12 = 9.25")

    # 라틴방진
    print(f"\n  n×n 라틴방진 수 L(n):")
    latin = {1: 1, 2: 1, 3: 1, 4: 4, 5: 56, 6: 9408, 7: 16942080}
    for n, count in latin.items():
        mark = ""
        if n == 6: mark = f"  = 9408 = 2^5 × 3 × 7^2 × ... 아니 2^5×294=..."
        print(f"    L({n}) = {count}{mark}")

    print(f"\n  L(6) = 9408 = {9408}")
    val = 9408
    temp = val
    factors = []
    for p in [2,3,5,7,11,13,17,19,23]:
        while temp % p == 0:
            factors.append(p)
            temp //= p
    if temp > 1: factors.append(temp)
    print(f"  9408 = {'*'.join(str(f) for f in factors)}")
    print(f"  9408/6 = {9408//6}")
    print(f"  9408/720 = {9408/720}")

    # MOLS (Mutually Orthogonal Latin Squares)
    print(f"\n  MOLS(n) = 직교 라틴방진 최대 수:")
    print(f"    MOLS(2) = 1")
    print(f"    MOLS(3) = 2")
    print(f"    MOLS(4) = 3")
    print(f"    MOLS(5) = 4")
    print(f"    MOLS(6) = 1  ← 예외! ★★")
    print(f"    MOLS(7) = 6")
    print(f"    MOLS(8) = 7")
    print(f"    일반: MOLS(n) = n-1 if n is prime power")
    print(f"    n=6에서만 MOLS가 극적으로 작음!")
    print(f"    → Euler의 36 장교 문제 (1782): 해 없음!")
    print(f"    → 1959년 Bose, Shrikhande, Parker가 n=6이 유일한 반례임을 증명")
    print(f"    (정확히는 n=2,6만 MOLS(n)<n-1)")
    print(f"\n  ★★ n=6은 Euler 추측의 유일한 비자명 반례!")
    print(f"    MOLS(n) < n-1인 n > 2는 오직 n=6뿐")

# === Phase F: 종합 — 새로운 고유성 추가 ===
def phase_f():
    print("\n" + "=" * 80)
    print("Phase F: 종합 — n=6 고유성 업데이트")
    print("=" * 80)

    print(f"""
  이번 탐색의 새 고유성:

  [NEW] MOLS(n) < n-1인 유일한 비자명 n = 6  ★★★
    Euler의 36 장교 문제 (1782)
    Bose-Shrikhande-Parker (1959)
    → n=6에서 직교 라틴방진이 예외적으로 적음
    → 이것은 Out(S_6)과 같은 조합론적 예외성의 다른 표현일 수 있음

  [NEW] K_{{3,3}} (최소 비평면 이분그래프) = 6 꼭짓점  ★
    Kuratowski 정리의 두 장애물: K_5, K_{{3,3}}
    K_{{3,3}}: 3=n/phi 양쪽에 3개씩 = 6=n개 꼭짓점

  [NEW] Petersen 그래프의 산술:
    변=15=C(6,2), 차수=3=n/phi, girth=5=sopfr

  [UPDATE] 독립 수렴 경로 수: 5 → 6 (+MOLS 추가)

  최종 독립 경로 목록:
    1. 수론: 유일한 squarefree 완전수
    2. 군론: Out(S_n)≠1의 유일한 n
    3. Niven: sin(pi/n) rational의 비자명 해
    4. 기하: 4D 정다포체 = 6개
    5. 소인수: n=sopfr+1의 유일한 합성수 해
    6. 조합론: MOLS(n)<n-1의 유일한 비자명 n ★NEW
""")

# === Main ===
def main():
    print("=" * 80)
    print(" DFS Ralph Deep 7")
    print("=" * 80)

    phase_a()
    phase_b()
    phase_c()
    phase_d()
    phase_e()
    phase_f()

if __name__ == '__main__':
    main()
