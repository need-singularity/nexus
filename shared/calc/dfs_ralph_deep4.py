#!/usr/bin/env python3
"""
DFS Ralph Deep 4 — 미개척 영역

Phase A: 약수 다항식과 n=6 (약수를 근으로 하는 다항식)
Phase B: 행렬식/행렬 고유값과 n=6
Phase C: 그래프론 — 약수 그래프의 불변량
Phase D: p-adic valuation 패턴
Phase E: Collatz-like 반복과 n=6
Phase F: 초월수론 — Liouville 수와 n=6
"""

import math
from itertools import combinations, product
from functools import lru_cache

# === 산술함수 ===
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

print("캐시 구축 중...")
for m in range(2, 10001): get_arith(m)
print("완료")

# === Phase A: 약수 다항식 ===
def phase_a():
    print("\n" + "=" * 80)
    print("Phase A: 약수 다항식 — 약수를 근으로 하는 다항식의 성질")
    print("=" * 80)

    # D_n(x) = Π(x - d) for d|n
    # n=6: D₆(x) = (x-1)(x-2)(x-3)(x-6)
    #            = x⁴ - 12x³ + 47x² - 72x + 36

    # 계수 분석
    divs6 = [1, 2, 3, 6]
    # 뉴턴 항등식: e₁=σ, e₄=Π(d)
    e1 = sum(divs6)  # = 12 = σ
    e2 = sum(a*b for a, b in combinations(divs6, 2))  # pairs
    e3 = sum(a*b*c for a, b, c in combinations(divs6, 3))
    e4 = math.prod(divs6)

    print(f"  n=6 약수: {divs6}")
    print(f"  D₆(x) = (x-1)(x-2)(x-3)(x-6)")
    print(f"  = x⁴ - {e1}x³ + {e2}x² - {e3}x + {e4}")
    print(f"  계수: [1, -{e1}, {e2}, -{e3}, {e4}]")
    print(f"  = [1, -12, 47, -72, 36]")

    # 계수의 산술적 의미
    print(f"\n  계수 분석:")
    print(f"    e₁ = {e1} = σ(6) (약수합)")
    print(f"    e₂ = {e2} (쌍곱합)")
    print(f"    e₃ = {e3} = σ(6)×n = 12×6 (삼중곱합)")
    print(f"    e₄ = {e4} = n^(τ/2) = 6² (약수곱)")
    print(f"    47 = 소수! (47번째 소수 아님)")
    print(f"    72 = 8×9 = 2³×3²")

    # D₆(0) = 36 = 6² = Π(d|6)
    # D₆(σ) = D₆(12) = (12-1)(12-2)(12-3)(12-6) = 11×10×9×6 = 5940
    d6_at_sigma = 11*10*9*6
    print(f"\n  D₆(σ) = D₆(12) = 11×10×9×6 = {d6_at_sigma}")
    print(f"    5940 = {5940} = 2²×3³×5×11")
    print(f"    5940/720 = {5940/720} = 8.25")
    print(f"    5940/6! = {5940/720}")

    # D₆(7) = (7-1)(7-2)(7-3)(7-6) = 6×5×4×1 = 120 = 5!
    d6_at_7 = 6*5*4*1
    print(f"\n  D₆(n+1) = D₆(7) = 6×5×4×1 = {d6_at_7} = 5! = (n-1)!")
    print(f"  ★ D_n(n+1) = Π(n+1-d) for d|n")

    # D₆(-1) = (-1-1)(-1-2)(-1-3)(-1-6) = (-2)(-3)(-4)(-7) = 168
    d6_at_neg1 = (-2)*(-3)*(-4)*(-7)
    print(f"\n  D₆(-1) = (-2)(-3)(-4)(-7) = {d6_at_neg1}")
    print(f"    168 = 8×21 = 2³×3×7")
    print(f"    168 = σ(6)×14 = 12×14")
    print(f"    168 = 6×28 = P₁×P₂ ★★")
    print(f"    → D₆(-1) = n×P₂!")

    # 다른 완전수에서도?
    divs28 = [1, 2, 4, 7, 14, 28]
    d28_at_neg1 = math.prod(-1-d for d in divs28)
    print(f"\n  D₂₈(-1) = {d28_at_neg1}")
    print(f"    = Π(-1-d) for d|28")
    print(f"    {d28_at_neg1} / 28 = {d28_at_neg1/28}")

    # D₆(-1) = P₁×P₂ 검증
    print(f"\n  ★★ D₆(-1) = 168 = 6×28 = P₁×P₂")
    print(f"  이것은 n=6에서만 성립하는가?")
    print(f"  검증: Π(-1-d) for d|n = n×(다음 완전수)?")

    # 판별식
    # D₆의 판별식 = Π(dᵢ-dⱼ)² for i<j
    disc = 1
    for i, j in combinations(range(4), 2):
        disc *= (divs6[j] - divs6[i])**2
    print(f"\n  판별식 Δ(D₆) = Π(dⱼ-dᵢ)² = {disc}")
    print(f"  = (2-1)²(3-1)²(6-1)²(3-2)²(6-2)²(6-3)² ")
    print(f"  = 1×4×25×1×16×9 = {1*4*25*1*16*9}")
    print(f"  √Δ = {int(math.sqrt(disc))} = {1*2*5*1*4*3}")
    print(f"  Δ = 14400 = 120² = (5!)²")
    print(f"  ★ 판별식 = (n-1)!² ← D₆(n+1)과 연결!")

# === Phase B: GCD 행렬 ===
def phase_b():
    print("\n" + "=" * 80)
    print("Phase B: GCD 행렬과 Smith 행렬식")
    print("=" * 80)

    # Smith 행렬: S_n = [gcd(i,j)]_{i,j=1..n}
    # det(S_n) = Π_{k=1}^{n} φ(k)

    def smith_det(n):
        """Smith 행렬식 = Π φ(k)"""
        prod = 1
        for k in range(1, n+1):
            prod *= sum(1 for i in range(1, k+1) if math.gcd(i, k) == 1) if k > 1 else 1
        return prod

    print(f"  Smith 행렬식 det[gcd(i,j)]_(n×n) = Π φ(k):")
    for n in range(1, 13):
        d = smith_det(n)
        print(f"    det(S_{n:2d}) = {d:>12d}", end="")
        if n >= 2:
            a = get_arith(n)
            if d % n == 0:
                print(f"  [n|det, det/n={d//n}]", end="")
        print()

    # n=6에서의 Smith 행렬
    print(f"\n  S₆ = [gcd(i,j)]_{{i,j=1..6}}:")
    for i in range(1, 7):
        row = [math.gcd(i, j) for j in range(1, 7)]
        print(f"    {row}")

    det_s6 = smith_det(6)
    print(f"\n  det(S₆) = {det_s6}")
    print(f"  = 1×1×2×2×4×2 = {1*1*2*2*4*2}")
    print(f"  = Π φ(k) for k=1..6")
    print(f"  = φ(1)×φ(2)×φ(3)×φ(4)×φ(5)×φ(6)")
    print(f"  = 1×1×2×2×4×2 = 32 = 2⁵")
    print(f"  ★ det(S₆) = 2⁵ = 32 = φ(6)^5 = 2^sopfr(6)")

    # 다른 n과 비교
    print(f"\n  det(S_n) = 2^? 패턴:")
    for n in [4, 5, 6, 7, 8, 10, 12]:
        d = smith_det(n)
        if d > 0:
            log2_d = math.log2(d) if d > 0 else 0
            is_power2 = d > 0 and (d & (d-1)) == 0
            print(f"    det(S_{n:2d}) = {d:>10d}, log₂ = {log2_d:.2f}, 2의 거듭제곱: {is_power2}")

    # 약수만으로 구성된 GCD 행렬
    divs6 = [1, 2, 3, 6]
    print(f"\n  약수 GCD 행렬 [gcd(dᵢ,dⱼ)]:")
    for d1 in divs6:
        row = [math.gcd(d1, d2) for d2 in divs6]
        print(f"    {row}")

    # 행렬식 직접 계산 (4×4)
    M = [[math.gcd(divs6[i], divs6[j]) for j in range(4)] for i in range(4)]
    # 4×4 행렬식 (Leibniz formula)
    def det4(m):
        return (m[0][0]*(m[1][1]*(m[2][2]*m[3][3]-m[2][3]*m[3][2])-m[1][2]*(m[2][1]*m[3][3]-m[2][3]*m[3][1])+m[1][3]*(m[2][1]*m[3][2]-m[2][2]*m[3][1]))
               -m[0][1]*(m[1][0]*(m[2][2]*m[3][3]-m[2][3]*m[3][2])-m[1][2]*(m[2][0]*m[3][3]-m[2][3]*m[3][0])+m[1][3]*(m[2][0]*m[3][2]-m[2][2]*m[3][0]))
               +m[0][2]*(m[1][0]*(m[2][1]*m[3][3]-m[2][3]*m[3][1])-m[1][1]*(m[2][0]*m[3][3]-m[2][3]*m[3][0])+m[1][3]*(m[2][0]*m[3][1]-m[2][1]*m[3][0]))
               -m[0][3]*(m[1][0]*(m[2][1]*m[3][2]-m[2][2]*m[3][1])-m[1][1]*(m[2][0]*m[3][2]-m[2][2]*m[3][0])+m[1][2]*(m[2][0]*m[3][1]-m[2][1]*m[3][0])))

    det_div = det4(M)
    print(f"  det = {det_div}")
    print(f"  {det_div} = {det_div} (약수 GCD 행렬식)")
    if det_div > 0:
        print(f"  = φ(1)×φ(2)×φ(3)×φ(6) = 1×1×2×2 = 4")

# === Phase C: p-adic valuation 패턴 ===
def phase_c():
    print("\n" + "=" * 80)
    print("Phase C: p-adic valuation 패턴")
    print("=" * 80)

    def v_p(n, p):
        """p-adic valuation of n"""
        if n == 0: return float('inf')
        v = 0
        while n % p == 0:
            v += 1
            n //= p
        return v

    # n=6 산술함수의 p-adic valuation
    vals = {'n': 6, 'σ': 12, 'φ': 2, 'τ': 4, 'sopfr': 5, 'n!': 720}
    print(f"  v_p(f(6)) 테이블:")
    print(f"  {'함수':>8} {'값':>6} {'v₂':>4} {'v₃':>4} {'v₅':>4} {'v₇':>4}")
    print(f"  {'-'*32}")
    for name, val in vals.items():
        print(f"  {name:>8} {val:>6} {v_p(val,2):>4} {v_p(val,3):>4} {v_p(val,5):>4} {v_p(val,7):>4}")

    print(f"\n  관찰:")
    print(f"    v₂(6) = 1, v₃(6) = 1 → 6 = 2¹×3¹ (squarefree)")
    print(f"    v₂(σ) = 2, v₃(σ) = 1 → σ = 2²×3¹ = 12")
    print(f"    v₂(6!) = 4 = τ(6)")
    print(f"    v₃(6!) = 2 = φ(6) = ω(6)")
    print(f"    v₅(6!) = 1 = v₂(6) = v₃(6)")
    print(f"    ★ v₂(n!) = τ(n) for n=6")

    # v₂(n!) = τ(n) 검색
    print(f"\n  v₂(n!) = τ(n) 검색 [2,100]:")
    solutions = []
    for m in range(2, 101):
        a = get_arith(m)
        # v₂(m!) = m - s₂(m) where s₂ is digit sum in base 2 (Legendre)
        v2_fact = m - bin(m).count('1')
        if v2_fact == a['tau']:
            solutions.append(m)
            print(f"    n={m}: v₂({m}!)={v2_fact} = τ({m})={a['tau']} ✓")

    # v₃(n!) = φ(n) 검색
    print(f"\n  v₃(n!) = φ(n) 검색 [2,100]:")
    for m in range(2, 101):
        a = get_arith(m)
        # v₃(m!) = (m - s₃(m))/2 where s₃ is digit sum in base 3
        temp, s3 = m, 0
        while temp > 0:
            s3 += temp % 3
            temp //= 3
        v3_fact = (m - s3) // 2
        if v3_fact == a['phi']:
            print(f"    n={m}: v₃({m}!)={v3_fact} = φ({m})={a['phi']} ✓")

# === Phase D: Collatz-like 반복 ===
def phase_d():
    print("\n" + "=" * 80)
    print("Phase D: 산술함수 반복 궤도")
    print("=" * 80)

    # σ(n)/n 반복: s(n) = σ(n) - n (aliquot sequence)
    print(f"  Aliquot sequence s(n) = σ(n)-n:")
    for start in [6, 12, 28, 30, 220]:
        seq = [start]
        n = start
        for _ in range(20):
            n = get_arith(n)['sigma'] - n if n >= 2 and n <= 10000 else 0
            if n <= 0 or n > 10000: break
            seq.append(n)
            if n == start:
                break
        cycle = "cycle!" if seq[-1] == start else ""
        print(f"    s({start}): {seq[:15]}{'...' if len(seq)>15 else ''} {cycle}")

    print(f"\n  ★ s(6) = [6] — 고정점! (완전수)")
    print(f"    s(6) = σ(6)-6 = 12-6 = 6")
    print(f"    6은 aliquot sequence의 고정점 = 완전수")

    # φ 반복
    print(f"\n  φ 반복 궤도 (항상 1로 수렴):")
    for start in [6, 12, 28, 30, 100]:
        seq = [start]
        n = start
        while n > 1:
            n = get_arith(n)['phi'] if n >= 2 else 1
            seq.append(n)
            if len(seq) > 20: break
        print(f"    φ*({start}): {seq} — 길이 {len(seq)-1}")

    print(f"    ★ φ*(6): [6,2,1] — 길이 2 (최단 경로 중 하나)")

    # σ 반복 궤도
    print(f"\n  σ 반복 궤도:")
    for start in [2, 3, 4, 5, 6, 7]:
        seq = [start]
        n = start
        for _ in range(10):
            n = get_arith(n)['sigma'] if n >= 2 and n <= 10000 else 0
            if n <= 0 or n > 10000: break
            seq.append(n)
        print(f"    σ*({start}): {seq[:12]}")

    print(f"    ★ σ*(6): [6, 12, 28, 56, 120, ...]")
    print(f"    σ(6)=12, σ(12)=28=P₂, σ(28)=56, σ(56)=120, σ(120)=360...")
    print(f"    → σ 궤도가 6→12→28(P₂)로 완전수 통과!")

    # sopfr 반복
    print(f"\n  sopfr 반복 궤도:")
    for start in [6, 12, 28, 30, 100]:
        seq = [start]
        n = start
        for _ in range(20):
            n = get_arith(n)['sopfr'] if n >= 2 else 0
            if n <= 1: break
            seq.append(n)
            if n == seq[-2] if len(seq) > 1 else False: break
        print(f"    sopfr*({start}): {seq}")

    print(f"    ★ sopfr*(6): [6, 5, 5, 5, ...] — 5에서 고정 (5는 소수)")

# === Phase E: 특수 수열에서의 n=6 ===
def phase_e():
    print("\n" + "=" * 80)
    print("Phase E: 특수 수열에서 n=6의 위치")
    print("=" * 80)

    # 삼각수
    print(f"  삼각수: T(n) = n(n+1)/2")
    for i in range(1, 13):
        t = i*(i+1)//2
        is_perfect = get_arith(t)['sigma'] == 2*t if t >= 2 else False
        mark = " ← P₂!" if t == 28 else (" ← P₁!" if t == 6 else "")
        print(f"    T({i:2d}) = {t:>4d}{'  (완전수!)' if is_perfect else ''}{mark}")

    print(f"\n  ★ 6 = T(3) = 삼각수")
    print(f"  ★ 28 = T(7) = 삼각수")
    print(f"  → 모든 짝수 완전수는 삼각수! (2^(p-1)(2^p-1) = T(2^p-1))")

    # 6면체수 (centered hexagonal)
    print(f"\n  육각수: H(n) = 2n²-n = n(2n-1)")
    for i in range(1, 10):
        h = i*(2*i-1)
        print(f"    H({i}) = {h}", end="")
        if h == 6:
            print(f" = 6 = P₁ ★", end="")
        if h == 28:
            print(f" = 28 = P₂ ★", end="")
        print()

    print(f"  ★ 6 = H(2) = 2번째 육각수")
    print(f"  ★ 28 = H(4) = 4번째 육각수")
    print(f"  → 모든 짝수 완전수는 육각수! (증명됨)")

    # 카탈란 수 위치
    catalans = [1, 1, 2, 5, 14, 42, 132, 429, 1430, 4862]
    print(f"\n  카탈란 수: {catalans}")
    print(f"  C₃ = 5 = sopfr(6)")
    print(f"  C₅ = 42 = σ(6)×sopfr(6) - σ(6)×φ(6) + σ(6) = ? 아니 42 = 6×7")
    print(f"  42 = n×(n+1) = 6×7")

    # 피보나치 수
    fibs = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233]
    print(f"\n  피보나치 수: {fibs}")
    print(f"  F₃=2=φ(6), F₄=3=σ/τ, F₅=5=sopfr(6), F₆=8=φ×τ")
    print(f"  F₁₂=144=σ²=12² ★")
    print(f"  → F_σ = σ² for n=6!")

    # F_{σ(n)} = σ(n)² 검색
    def fib(k):
        if k <= 0: return 0
        a, b = 1, 1
        for _ in range(k-1):
            a, b = b, a+b
        return a

    print(f"\n  F_σ(n) = σ(n)² 검색:")
    for m in range(2, 100):
        a = get_arith(m)
        if a['sigma'] <= 50:
            f_s = fib(a['sigma'])
            if f_s == a['sigma']**2:
                print(f"    n={m}: F_{a['sigma']} = {f_s} = {a['sigma']}² ✓")

    print(f"  F₁₂ = {fib(12)} = {12**2} = σ(6)² ✓")
    print(f"  F₁₂ = 144는 유일한 제곱 피보나치 수(>1) ★★★")
    print(f"  → σ(6) = 12이고, F₁₂ = 144 = 12² = σ(6)²")
    print(f"  → 유일한 제곱 피보나치 수의 인덱스 = 첫 번째 완전수의 약수합!")

    # Cohn의 정리: F_n이 완전 제곱인 n은 0, 1, 2, 12뿐
    print(f"\n  Cohn 정리: F_n = k²인 n은 {{0, 1, 2, 12}}뿐")
    print(f"    F₀=0=0², F₁=1=1², F₂=1=1², F₁₂=144=12²")
    print(f"    비자명 제곱 피보나치: F₁₂ = 144 유일!")
    print(f"    12 = σ(6) = σ(P₁)")
    print(f"    ★★★ 유일한 비자명 제곱 피보나치 인덱스 = σ(최소 완전수)")

# === Main ===
def main():
    print("╔" + "═"*78 + "╗")
    print("║" + " DFS Ralph Deep 4 — 미개척 영역 탐색".center(72) + "║")
    print("╚" + "═"*78 + "╝")

    phase_a()
    phase_b()
    phase_c()
    phase_d()
    phase_e()

    print("\n" + "╔" + "═"*78 + "╗")
    print("║" + " 최종 요약".center(76) + "║")
    print("╚" + "═"*78 + "╝")

    print(f"""
  ★★★ Deep 4 핵심 발견:

  [1] D₆(-1) = 168 = 6×28 = P₁×P₂  🟩⭐⭐
      약수 다항식의 x=-1 값 = 두 완전수의 곱

  [2] Δ(D₆) = 14400 = (5!)² = ((n-1)!)²  🟩⭐⭐
      약수 다항식의 판별식 = (n-1)! 제곱

  [3] F₁₂ = F_σ(6) = 144 = σ(6)² = 12²  🟩⭐⭐⭐
      유일한 비자명 제곱 피보나치의 인덱스 = σ(P₁)
      (Cohn 정리: F_n=k²인 n은 0,1,2,12뿐)

  [4] v₂(6!) = τ(6) = 4  🟩⭐
      6!의 2-adic valuation = 약수 개수

  [5] σ 궤도: 6→12→28(P₂) 🟩⭐⭐
      (Deep3 재확인, σ(σ(6))=P₂)

  [6] det(S₆) = 32 = 2^sopfr(6)  🟩⭐
      Smith 행렬식 = 2^(소인수합)
""")

if __name__ == '__main__':
    main()
