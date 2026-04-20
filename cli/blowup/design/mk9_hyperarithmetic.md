# Mk.IX Hyperarithmetic Extension — Π₀² 검증 전략 설계서

**상태**: DESIGN ONLY (코드 변경 없음)
**선행**: Mk.VIII Δ₀-Absolute Blowup (`shared/blowup/modules/blowup_absolute.hexa`)
**작성일**: 2026-04-19
**목표**: Π₀² 계층 명제를 **부분적**으로 판정하는 엔진 설계.
           완전 판정은 불가능(0′ oracle 필요) — heuristic + reverse-math 경유.
**비목표**: Σ₁¹ 이상 analytical 계층 (별도 Mk.X 후속).

---

## 0. 요약 (Executive Summary)

Mk.VIII 은 Π₀¹(bounded quantifier only) 명제에 한해 Shoenfield absoluteness 를
자동 적용하여 `[10*] → [11*]` foundation 승급을 처리한다. 핵심 정리 `σ·φ=n·τ=24 iff n=6`
이 Π₀¹ 이기 때문에 전체 수학 우주(ZFC, large-cardinal, Reinhardt, Cantor-𝔚)에서
invariant 가 자동 보장된다.

그러나 atlas 에 누적되는 명제 중 실질적으로 중요한 다수는
`∀n ∃m (…)` 형태의 **Π₀²** 다. 예: "모든 큰 수 n 에 대해 더 큰 완전수 m 이 존재",
"모든 유한군 G 에 대해 Sylow p-부분군이 존재". 이들은 Shoenfield 의 직접 적용 범위
밖이고, 일반적으로 **decidable 하지 않다** (Gödel-Tarski).

Mk.IX 는 네 단계 파이프라인으로 이 틈을 부분 메운다:

1. **구문 탐지**: AST 수준에서 `∀x ∃y φ(x,y)` 추출, `φ` 가 Π₀¹ 인지 재귀 검증.
2. **Bounded witness 축소**: `y < f(x)` 가 가능하면 Π₀¹ 로 downgrade → 기존 엔진.
3. **Reverse-math 5 체계 매핑**: RCA₀/WKL₀/ACA₀/ATR₀/Π¹₁-CA₀ 에서 진릿값 검사.
4. **n=6 invariance 대조군**: n=6 대체 시 진릿값이 유지되는지 확인. 유지 = 대칭성
   확장 증거, 변화 = 등재 거부.

새 등급 `[12*]` 를 도입하여 Π₀² foundation 을 [11*] 와 분리한다. 정확도 목표는
"atlas 에 들어오는 Π₀² 명제 중 95% 판정". 완전성은 포기한다.

---

## 1. 이론 배경

### 1.1 Arithmetical hierarchy 재확인

산술 계층은 1차 Peano 산술 언어(`0, S, +, ×, =, <`) 위에서 정의된다:

- **Δ₀ = Σ₀ = Π₀**: bounded quantifier (`∀x<t`, `∃x<t`) 만 사용. `t` 는 항.
- **Σ₀¹**: `∃x₁…∃xₖ φ` — `φ ∈ Δ₀`. 동등하게 "recursively enumerable" 관계.
- **Π₀¹**: `∀x₁…∀xₖ φ` — `φ ∈ Δ₀`. 동등하게 "co-r.e." 관계.
- **Σ₀² = Σ₂**: `∃x ∀y φ` — `φ ∈ Δ₀`. Halting-with-output 류.
- **Π₀² = Π₂**: `∀x ∃y φ` — `φ ∈ Δ₀`. **Totality / uniformity / cofinality** 류.
- **Σ₀³, Π₀³, …**: alternation 수에 따라 상승. 완전한 엄격 계층.

Δ₀ ⊂ Σ₀¹ ⊊ Σ₀² ⊊ Σ₀³ ⊊ … (Post's theorem: 각 층위는 이전 층위의 jump).

Σ₁¹ (analytical) 이상은 2차 산술 (집합 변수 양화). Mk.IX 범위 밖.

### 1.2 Π₀² 의 의미

Π₀² 명제는 "모든 입력에 대해 유한 탐색이 종료한다" 류를 가장 자연스럽게 포착한다:

- **Totality**: 함수 `f: ℕ → ℕ` 이 total 이라는 주장은 Π₀². (`∀x ∃y (f 의 계산이 y 단계
  안에 멈춤)`)
- **Cofinality**: "임의 크게 가는 성질이 있다" (예: 소수의 무한성 — Euclid, 증명됨).
- **무한히 많은 해**: "…를 만족하는 n 이 무한히 많다" = "∀N ∃n>N …".

Mk.IX 가 다룰 Π₀² 예시 세 가지:

1. **완전수 무한성**: "∀N ∃m>N, σ(m)=2m". n=6 프로젝트 핵심 conjecture.
   **현재 미해결** (2026-04 기준). 알려진 짝수 완전수는 51개 (Mersenne 소수 대응).
   홀수 완전수는 존재성 미해결.

2. **Vinogradov (약 Goldbach)**: "∀n (n 홀수, n≥N₀) ∃p₁,p₂,p₃ 소수, n=p₁+p₂+p₃".
   Vinogradov(1937) 증명. 2013 Helfgott 가 N₀=7 까지 effective.
   → **증명됨, 구체 상수까지 알려짐**.

3. **Sylow theorem**: "∀유한군 G, ∀p | |G|, ∃H≤G, H 는 Sylow p-부분군".
   Sylow(1872). **증명됨, 1차 산술로 인코딩 가능** (유한군은 ℕ-encoded group table).

1번은 미해결, 2·3번은 정리. 세 경우 모두 **구문적으로는 Π₀²** 이며, 엔진은 구문
탐지와 증명 상태를 분리해 다룬다.

### 1.3 Shoenfield 의 한계

Shoenfield absoluteness (1961) 은 **Σ₁² (동등하게 Π₁²)** 사이에서 V 와 L 사이
absoluteness 를 준다. Π₀² ⊂ Σ₁² 이므로 Π₀² 의 진릿값 자체는 V↔L 에서는
보존된다 (ordinals 가 같은 transitive model 에서도 보존). 그러나 **ZFC 와 independent
인지 여부** 와 **모든 trans itive model 에서 decidable 한지** 는 다르다:

- Π₀¹ 은 decidable 한 경우가 많지는 않지만, 위증 반례가 있으면 유한 탐색으로
  찾을 수 있다 (r.e. complement).
- Π₀² 는 일반적으로 **Π₀²-complete** 가 존재하므로 arithmetic oracle 도 부족하고,
  0′(=Halting) oracle 이 필요하다. 즉 engine 은 본질적으로 불완전.

따라서 "Π₀² 이면 자동 [11*] 승급" 같은 규칙은 **작동하지 않는다**. 대신
reverse-math 체계별 증명가능성을 본다.

### 1.4 "부분 판정" 의 의미

Mk.IX 는 다음 중 하나로 판정한다:

- `ABSOLUTE-PASS (Π₀²)`: bounded witness 로 Π₀¹ downgrade 성공 → Mk.VIII 경유 확정.
- `REVERSE-PROVEN`: ACA₀ 이하 reverse-math 체계에서 증명 알려짐 (문헌 기반 whitelist).
- `REVERSE-UNKNOWN`: 5 체계 중 3+ 체계에서 일치하지만, Π¹₁-CA₀ 이상 필요하거나 open.
- `REJECT`: n=6 대조군 실패 또는 체계 간 불일치.

---

## 2. 검증 전략 4 단계

### 단계 A — Π₀² 구문 탐지

**스펙**: `is_pi02(expr: string) -> {NO, YES, UNSURE}`

입력은 atlas 라인(또는 discovery 후보)의 자연어+수식 혼합 문자열. Mk.VIII 의
`is_arithmetical()` 은 단순 키워드 검사이므로 확장이 필요하다.

**파서 설계**:

1. **1차 토크나이저**: 자연어 양화 표현 → 논리 기호 정규화.
   - 한국어: "모든" → `∀`, "어떤/존재" → `∃`, "임의의" → `∀`, "무한히 많은" →
     `∀N ∃n>N`.
   - 영어: "for all", "every", "any" → `∀`; "exists", "some", "there is" → `∃`;
     "infinitely many" → `∀N ∃n>N`.
   - 수식 `∀x<t`, `∃x<t` 는 그대로 bounded 로 표시.

2. **2차 AST 구성**: 선형 prefix 스캔으로 quantifier 순서를 추출. 결과는
   `[(kind, var, bound_term_or_None), …]` 리스트.
   - `bound_term = None` → unbounded.
   - `bound_term != None` → bounded (Δ₀ 기여).

3. **3차 분류**:
   - 모든 quantifier 가 bounded → `Δ₀`.
   - unbounded 가 `∀` 하나 또는 `∃` 하나뿐 → `Π₀¹` / `Σ₀¹`.
   - unbounded prefix 가 `∀ … ∃ … (bounded…)` → `Π₀²` 후보.
   - 더 깊은 alternation → Π₀³ 이상 (Mk.IX 범위 밖, `UNSURE` 반환).

4. **4차 matrix 재귀**: Π₀² 판정은 `φ` 부분이 Δ₀ 인지 재귀 호출로 확인. Δ₀ 가
   아니면 계층이 상승.

**실패 모드**:
- 자연어 혼동 (예: "모든 쿼크 공통" → 물리적 일반화, 수학적 ∀ 아님) →
  false positive. 해결: `@R/@C/@L` 등 prefix 와 수식 포함 여부로 confidence 조정.
- 자연어 ∃/∀ 가 metavariable (예: "어떤 n=6 에 대해…") → 실제로는 특정 n 고정.
  해결: "n=6", "= 6" 같은 고정 binding 패턴 먼저 축소.

**확장**: Mk.VIII `is_arithmetical()` 은 이 파서의 wrapping 으로 재정의.
`is_arithmetical = is_delta0 ∨ is_pi01 ∨ is_sigma01`. Π₀² 는 arithmetical 이긴 하나
absolute 엔진 경로는 분리.

**출력**: 각 atlas 항목에 메타데이터 태그 `hierarchy: Δ₀ | Π₀¹ | Σ₀¹ | Π₀² | Σ₀² | ≥Π₀³`.
기본은 comment 형식, stats 파일에 집계.

### 단계 B — Bounded witness 축소

**동기**: `∀x ∃y φ(x,y)` 가 실제로 `∀x ∃y<f(x) φ(x,y)` 로 `f` 가 (primitive) recursive
이면, 이는 equivalent 하게 Π₀¹ 이다 (bounded matrix 로 흡수). 즉 Π₀² 중 상당 부분은
**실질 Π₀¹** 이다.

**알고리즘**:

1. `∀x ∃y φ(x,y)` 추출.
2. atlas/literature 기반 **witness bound table** 조회:
   - `완전수 존재`: known bound 없음 → skip.
   - `Vinogradov`: `y = p₁+p₂+p₃, pᵢ ≤ n` → `y < n³` 으로 bound. Π₀¹ downgrade OK.
   - `Sylow p-subgroup`: `|H| = p^k ≤ |G|` → `y < |G|+1` bound. Π₀¹ downgrade OK.
   - `Bertrand postulate`: `∀n ∃p 소수 (n < p < 2n)` → `y < 2n` bound. Π₀¹ downgrade OK.
3. Bound 를 찾으면 matrix 를 `∀x ∀y<f(x) ¬φ → false` 형태 Π₀¹ 로 재구성, Mk.VIII
   엔진에 회부.

**witness bound table** 은 `shared/blowup/lib/reverse_math_check.hexa.inc` 내부에
정적 JSON 으로 두고 주기적 수동 보완. 초기 엔트리 후보:

| 명제 | Witness bound | 근거 |
|---|---|---|
| Bertrand | `2n` | Chebyshev 1852 |
| Vinogradov (strong) | poly(n) | Helfgott 2013 |
| Sylow | `|G|` | group order bound |
| Fermat little theorem | bounded by `p` | 유한 잉여류 |
| Wilson theorem | bounded by `p` | 위와 동일 |

**한계**: bound 를 모르면 강제 reject 하지 않고 단계 C 로 넘긴다. "bound 모름" 은
현재 수학의 한계 반영일 수 있다 (예: 완전수 무한성).

### 단계 C — Reverse-math 체계 매핑

**동기**: Mk.VIII 의 5 모델 (PA/ZFC/LC/Reinhardt/𝔚) 은 집합 크기 축이다. Π₀² 에는
그보다 **증명력 축** 이 더 중요하다. Reverse mathematics 의 Big Five 가 표준 기준:

- **RCA₀**: Δ₁ comprehension + Σ₁ induction. Base system. 계산 가능한 수준.
- **WKL₀**: RCA₀ + weak König's lemma. Compactness 류 ≈ Σ₁ reflection.
- **ACA₀**: arithmetical comprehension. ≈ PA. **Π₀² 정리의 대부분이 여기서 처리됨.**
- **ATR₀**: arithmetical transfinite recursion. well-ordering 다루는 단계.
- **Π¹₁-CA₀**: Π¹₁ comprehension. 최강.

**알고리즘**:

1. 명제 `P` 의 Π₀² 구조가 확인됨 (단계 A 통과, 단계 B 미해결).
2. 5 체계 각각에서:
   - **화이트리스트 조회**: 해당 체계에서 `P` 와 동치/유도관계인 정리가 문헌에
     존재하는가? 초기 table:
     - Bolzano-Weierstrass ≡ ACA₀.
     - König's lemma ≡ WKL₀ (tree 는 finitely branching).
     - Sylow theorem → RCA₀ 에서 증명 (유한 구조).
     - Ramsey(3) → ACA₀.
     - CAC(Chain-Antichain) ≡ RCA₀+더 약한 것.
   - **휴리스틱 점수**:
     - 유한 구조 관련 → RCA₀ 증명 가능성 높음.
     - compactness 사용 → WKL₀ 필요.
     - 임의 sequence 극한 사용 → ACA₀ 이상.
     - well-order 치수 비교 → ATR₀.
     - 비가산 집합 comprehension → Π¹₁-CA₀.
3. 5 체계 중 **3+ 가 PROVEN 또는 CONSISTENT** 로 나오면 `REVERSE-PROVEN`.
4. 5 체계 간 **모순** 이 나오면(거의 없지만) `CONSISTENT-ERROR` → 인간 감사.
5. 모두 UNKNOWN → `REVERSE-UNKNOWN`.

**메커니즘 세부**:
- 체계별 판정은 프로그램이 **직접 증명하지 않는다**. 알려진 reverse-math 결과를
  찾는 문헌 DB (수동 큐레이트) 룩업.
- 엔진은 "해당 체계에서 증명력이 있다" 라는 인증서 (bibliographic reference) 를
  요구한다. 없으면 UNKNOWN.
- 이는 Mk.IX 엔진이 본질적으로 **meta-검증자** 임을 의미한다. 창발적 판정은 단계 B
  의 bound 축소에서만 발생.

**체계 3/5 일치 기준**의 정당화:
- RCA₀ 증명 → 4체계 모두 자동 증명 (strength 증가 방향) → 5/5.
- ACA₀ 증명 → ACA₀/ATR₀/Π¹₁-CA₀ 3/5.
- 따라서 `3/5` 는 "ACA₀ 이상에서 설명 가능" ≈ **Π₀² 완전성의 자연 경계**.

### 단계 D — n=6 invariance 최종 체크

Mk.VIII 의 철학 계승: n=6 은 단순 수치가 아니라 atlas 전체의 **지문**. 새 엔트리는
"n=6 을 뺐을 때 다르게 증명되지 않는가?" 를 통과해야 진짜 n=6 기반 정리.

**알고리즘**:

1. 단계 C 에서 `REVERSE-PROVEN` 인 명제 `P(n=6)` 에 대해 `P[6 ↦ k]` 를 생성
   (k ∈ {2,3,4,5,7,8,12,24,28,496}). 28, 496 은 다른 완전수 대조군.
2. 치환 결과가 증명되는가:
   - 여전히 참 → `UNIVERSAL` (n=6 특이성 없음, foundation 승급 부적합).
   - n=6 에서만 참 → `N6-CORE` (foundation [12*] 승급 후보).
   - n∈{6, 28, 496} 에서만 참 → `PERFECT-CLASS` (완전수 구조 전체 적용, [12*] 가능).
   - 반례 발생 → `N6-UNIQUE` (강한 foundation).
3. 승급 규칙:
   - `N6-UNIQUE` → `[12*] n6-unique`.
   - `N6-CORE` → `[12*] n6-core`.
   - `PERFECT-CLASS` → `[12*] perfect-class`.
   - `UNIVERSAL` → `[10*]` 유지 (이미 universal 이면 Π₀² 판정은 흥미롭지만 n=6
     foundation 과는 별개).

**예시 적용**:
- Sylow theorem: `UNIVERSAL` (모든 유한군, n 독립). → foundation 승급 없음,
  그러나 `hierarchy: Π₀²` 메타만 기록.
- 완전수 무한성: 명제 자체가 n=6 의 완전성에서 유도 →
  `PERFECT-CLASS` 후보, 단 단계 C 에서 `REVERSE-UNKNOWN` (open conjecture) 이라
  승급 보류.
- `∀k ∃m (σ(m) = k·m, k=2 유일한 해 집합 존재)`: n=6 에 의존한 숫자 2 특성
  → `N6-CORE` 예상.

---

## 3. 신규 등급 `[12*]` 스펙

### 3.1 등급 체계 확장

| 등급 | 의미 | 절대성 층위 |
|---|---|---|
| `[5~8]` | 중간 (EMPIRICAL → partial) | N/A |
| `[9]` | NEAR | N/A |
| `[10]` | EXACT | 수치 검증만 |
| `[10*]` | EXACT-검증 | Π₀¹ arithmetical 확정 |
| `[11*]` | Δ₀-absolute foundation | Shoenfield, 모든 transitive model invariant |
| **`[12*]`** | **Π₀² hyperarithmetic foundation** | **ACA₀-증명 + n=6 core** |
| `[13*]` (예정) | Π₀³ / higher (Mk.X 이후) | TBD |

### 3.2 [12*] 승급 조건 (AND 전부)

1. `is_pi02()` YES 확정 또는 단계 B 로 Π₀¹ downgrade 성공 후 [11*] 부여됨을 통과.
2. 단계 C `REVERSE-PROVEN` (3/5 체계 이상 일치, ACA₀ 이상 증명 확보).
3. 단계 D `N6-UNIQUE` / `N6-CORE` / `PERFECT-CLASS` 중 하나.
4. 수동 감사 서명 (CODEOWNERS 수준, foundation 변경은 L0 guard 통과 필요).

즉 `[12*]` 는 **자동 승급하지 않는다**. 단계 A~C 까지는 자동, D 결과 +
사람이 승인해야 atlas 반영. 이는 Gödel 불완전성에 대한 합리적 타협.

### 3.3 저장 형식

`@L` 법칙 prefix + 두 줄 인증:

```
@L NAME :: foundation [12*]
  <- dependencies
  => "Π₀² statement in prose"
  => "reverse-math: proved in ACA₀ (Simpson SOSOA §III.x)"
  => "n=6 invariance: N6-CORE (k=6 only; k∈{2,4,8,28} fails)"
  !! breakthrough-YYYY-MM-DD "human-audit sign"
```

기존 `!! breakthrough` 양식 확장.

---

## 4. 구현 heuristic — 완전성 포기

Gödel 불완전성 정리 (1931): 일관된 충분 강 산술 체계 `T` 는 참이나 `T` 에서
증명불가능한 Π₀¹ (실은 Π₀²-level formalization of consistency) 명제를 포함한다.
따라서 Π₀² 를 완전 판정하는 알고리즘은 존재하지 않는다.

**엔진 정책**:

- **목표 정확도**: atlas 에 incoming 하는 Π₀² 후보 중 **95% 판정**. 판정 = 한
  범주(`ABSOLUTE-PASS` / `REVERSE-PROVEN` / `REVERSE-UNKNOWN` / `REJECT`) 부여.
  나머지 5% 는 `UNSURE` 로 별도 큐에 쌓여 주간 수동 감사.
- **False positive 허용 기준**:
  - `REVERSE-PROVEN` 으로 찍힌 명제 중 실제는 증명 없는 경우 ≤ 1%.
  - 즉 3/5 체계 휴리스틱 의 실제 오류율 target.
  - 초기에는 2% 정도까지 허용, 감사로 드리프트 탐지.
- **주기적 수동 감사**:
  - 월간 3명 독립 감사. reverse-math 문헌 대조.
  - 오류 발견 시 witness_bound_table / reverse_math_whitelist 업데이트 + 해당
    [12*] 엔트리 **강제 downgrade** (`[10*]` 로 되돌리거나 `[10*?]` 로 표시).
- **downgrade 는 가역적 foundation 변경** 이라 L0 guard 이벤트로 기록.

---

## 5. atlas 영향 분석

### 5.1 현재 상태 (atlas.n6, 110,781 줄)

`ripgrep` 기반 count 결과 (2026-04-19):

- 한국어 `"모든"` 포함 라인: **31건**. 대부분 자연어 설명 (예: "모든 쿼크 공통") 이지만
  수학적 ∀ 후보 일부 포함.
  - 후보 예시:
    - L25~27 부근 "모든 구조의 씨앗" — n=6 의 universal role, 수학적 Π₀² 아님.
    - L223 "6은 고합성수 — tau(6)=4, 이전 모든 수보다 약수 많음" → `∀m<6 τ(m)<τ(6)`
      = bounded, **Δ₀**. 이미 [10*] 타당.
    - L243 "Out(S_6)=Z/2 — 다른 모든 S_n 에서 불가능" → `∀n≠6 (Out(S_n)=1)` =
      Π₀² (n 범위 unbounded). **[12*] 승급 후보 1순위**.
    - L12592 "모든 평면 그래프 4-착색 가능" → Π₀² (∀그래프 ∃착색), 증명됨
      (Appel-Haken 1976), ACA₀ 증명 가능. n=6 무관 → `UNIVERSAL` → 승급 없음,
      단 hierarchy 태그.
    - L12604 "4차원 정다포체 수 … 모든 차원 ≥3 중 최대" → Π₀² (∀d≥3 #polytope(d) ≤ 6),
      증명됨 (Schläfli 1852). n=6 특이 → `N6-UNIQUE` 후보.
- `infinite` 2건 — 완전수 무한성 관련 가능성 확인 필요.
- `exists` 영어 라인 0건 → 대부분 한국어로 기술되어 탐색은 "모든"/"어떤"/"무한" 중심.

**초기 추정 [12*] 후보**: ~5–10건. 본 설계서 승인 후 단계 A 파서를 dry-run 해
정확한 수를 얻는다.

### 5.2 stats 파일 영향

현재 `atlas.n6.stats`:

```json
{"schema":2,"mtime":…,"size":…,"line_count":107534,"head_hash":…,"nodes":20510,"edges":54332,"hubs":19236}
```

**제안 확장** (schema 3):

```json
{"schema":3, …,
 "hierarchy": {"delta0": N1, "pi01": N2, "sigma01": N3,
               "pi02": N4, "sigma02": N5, "higher": N6, "unknown": N7},
 "foundation_tiers": {"10_star": A, "11_star": B, "12_star": C}}
```

기존 schema 2 reader 는 `hierarchy` / `foundation_tiers` 필드를 무시하도록 forward
compat 처리.

### 5.3 기존 [10*]/[11*] 의 Π₀² 감사

1회성 배치: 단계 A 파서를 전체 atlas 에 적용 → 각 @R/@C/@L 에 hierarchy 태그.
결과를 `atlas.n6.hierarchy` 별도 파일에 저장 (atlas.n6 수정 X — 본 설계 제약 준수).

---

## 6. Mk.IX 엔진 파일 구조 제안

```
shared/blowup/modules/
  blowup_absolute.hexa              (기존, 수정 금지)
  blowup_hyperarithmetic.hexa       (NEW, 7번째 core 후보)

shared/blowup/lib/
  reverse_math_check.hexa.inc       (NEW, 5 체계 whitelist + witness bound table)
  pi02_parser.hexa.inc              (NEW, 자연어 → AST → hierarchy 탐지)

shared/blowup/design/
  mk9_hyperarithmetic.md            (본 문서)
  mk9_witness_bound_table.json      (NEW, 단계 B 데이터)
  mk9_reverse_math_whitelist.json   (NEW, 단계 C 문헌 DB)
```

### 6.1 absolute → hyperarithmetic 체인

```
(discovery candidate)
  │
  ▼
blowup_absolute::is_arithmetical()         ← Π₀¹ 판정 (Mk.VIII)
  │
  ├─ YES Π₀¹ → cross_axis_verify() → [11*]
  │
  └─ NO Π₀¹ → blowup_hyperarithmetic::pipeline()
                │
                ├─ A: is_pi02()
                ├─ B: try_bound_reduction() → 성공시 absolute 로 돌아감
                ├─ C: reverse_math_whitelist_check()
                └─ D: n6_invariance_check() + 수동 감사 → [12*]
```

`blowup_hyperarithmetic.hexa` 는 `blowup_absolute.hexa` 를 **읽기 전용 의존**.
역방향 의존 없음.

### 6.2 7번째 core module 의미

Mk.VIII 는 "n=6 6번째 core" 로 완성되었다 (field/holographic/quantum/string/toe +
absolute). 7번째 core 는 n=6 구조상 **첫 번째 확장점** — n=6 은 6개 core 에서 닫혔고,
다음 core 는 n=6 자체에 대한 **상위 언급 레벨** 이 된다. Π₀² = "∀ 명제들에 대한
메타 구조" 로서 이 상위 언급 레벨과 자연스레 매칭된다.

※ 단 "7번째 core 도입" 자체는 n=6 프로젝트 철학의 변곡점 — 사용자 승인 필요.
대안: `absolute.hexa` 에 흡수된 sub-module 로 두고 core 숫자는 6 유지.

---

## 7. 리스크 & 한계

### 7.1 ω-consistency 가정

단계 C 의 reverse-math 체계들은 모두 PA 의 ω-consistency 를 암묵 가정한다.
ω-inconsistent 하지만 syntactic consistent 한 pathological 체계가 있으면 본 엔진은
잘못된 `REVERSE-PROVEN` 을 낼 수 있다. 실용적 risk 는 매우 낮지만, Mk.IX 문서에
명시 가정으로 남긴다.

### 7.2 Gödel 불완전성 직접 영향

- 엔진은 체계의 일관성을 주장하지 않는다. 외부 assumption.
- 특히 `Con(ZFC)` 관련 명제는 Π₀¹ 이지만 판정 불가 — 단계 A 는 Π₀¹ 로 분류, Mk.VIII
  는 `ABSOLUTE-PASS` 찍을 수 있다. 위험: `Con(ZFC)` 는 실제로 미확정. 해결:
  **blacklist** 에 "consistency of T" 패턴 등록 → 항상 UNSURE.

### 7.3 ACA₀ 미만 체계에서 사라지는 명제

Bolzano-Weierstrass 는 RCA₀ + WKL₀ 에서 증명되지 않고 ACA₀ 와 동치. 따라서
단계 C 의 3/5 기준은 **최소 ACA₀ 강도** 를 요구한다. 이는 의도된 설계 (Π₀²
정리의 '표준' 강도), 단 사용자는 "RCA₀/WKL₀ 만으로 증명되는 약한 Π₀² 정리" 도
존재함을 알아야 한다. 이 경우 엔진은 `REVERSE-PROVEN` 을 여전히 준다 (5/5 자동).

### 7.4 이론 부담 vs 실용 이득

- **부담**: reverse-math whitelist 유지는 수동 문헌 수집. Simpson SOSOA,
  Hirschfeldt, Dzhafarov-Mummert 등 표준 레퍼런스 기반.
- **이득**: `[12*]` 승급은 n=6 foundation 의 확장 — 현재 [11*] 두 개 뿐. 연 5~10개
  추가 정도 예상. 승급 한 건당 전체 우주 invariance 증거 하나 추가.
- **평가**: 초기 구현 공수 2~4주, 유지 공수 월 1~2일. 인간 감사 필수 단계 D 가
  자동화 병목. ROI 경계선 — 사용자 판단 필요.

### 7.5 단계 A 파서의 체계적 오분류

자연어 양화는 본질적으로 모호:
- "모든 n=6 에 대해" (metaphorical) vs "모든 자연수 n 에 대해" (quantificational).
- 한국어 조사 없음 → "모든" 이 복수 일반화인지 수학적 ∀ 인지 애매.

**대응**: 파서는 보수적으로 UNSURE 선호. atlas 의 @R/@C/@L 은 구조적 필드이므로
"`@` + 수식" 패턴일 때만 Π₀² 판정 활성화.

### 7.6 `[12*]` 후보 고갈 가능성

atlas 는 대부분 Δ₀ 또는 Π₀¹ 수치 명제 (`σ(6)=12`, `J₂(6)=24` 등). 진짜 Π₀²
후보는 "∀ 무한 집합" 류로 제한되어 수가 많지 않다. → `[12*]` 는 **희소** 하도록
설계됨. 이는 의도된 성질 (foundation tier 는 소수의 깊은 정리로 구성).

---

## 8. 테스트 시나리오

본 설계 구현 시 통과해야 할 end-to-end 시나리오.

### 8.1 T1 — 완전수 무한성 예측

**입력**:
```
@R perfect_infinite_conjecture = ∀N ∃m>N, σ(m)=2m :: conjecture [9?]
```

**기대 흐름**:
- 단계 A: `∀N ∃m>N` 탐지 → Π₀² YES. matrix `σ(m)=2m` 은 Δ₀ (m 유한, σ 는 Δ₀
  계산 가능). 확정 Π₀².
- 단계 B: witness bound table 조회 — 완전수 간격 bound 알려지지 않음 → SKIP.
- 단계 C: 5 체계 조회 — 0/5 PROVEN (open conjecture). → `REVERSE-UNKNOWN`.
- 단계 D: 실행 안 함 (C 미통과).

**기대 출력**: 등급 `[9?]` 유지, 메타 태그 `hierarchy: Π₀²`, `reverse: UNKNOWN`,
`audit_queue: yes`. `[12*]` 승급 **없음** (정답 — open conjecture 는 foundation
이 되면 안 됨).

### 8.2 T2 — Goldbach weak (Vinogradov)

**입력**:
```
@R vinogradov = ∀n odd, n≥7, ∃p₁,p₂,p₃ primes, n=p₁+p₂+p₃ :: number_theory [10?]
```

**기대 흐름**:
- 단계 A: `∀n ∃p₁p₂p₃` → Π₀² YES (matrix `n=p₁+p₂+p₃ ∧ prime(pᵢ)` 는 Δ₀).
- 단계 B: witness `pᵢ ≤ n` → `p₁+p₂+p₃ ≤ 3n` bound 로 Π₀¹ downgrade 성공.
  → Mk.VIII 경로로 회부.
- Mk.VIII: `ABSOLUTE-PASS` → `[11*]` 승급 (단, n=6 연관성 약함).
- 단계 D (Mk.IX 회귀): n=6 특이성 없음 → `UNIVERSAL` → foundation 승급은 없이
  `[10*] Π₀¹-via-bound-reduction` 정도로 마무리.

**기대 출력**: `[10*]` 또는 `[11*]` (관리자 선택), `hierarchy: Π₀² reduced to Π₀¹`,
`bound: 3n (Chebyshev-style)`.

### 8.3 T3 — n=28 대조군 (정답: 승급 실패)

**입력**: T1 을 n=28 로 복사하여 "28 = 두 번째 완전수" 기반 유사 conjecture 를
atlas 에 추가 시도.
```
@R perfect_28_foundation = ∀N ∃m>N, σ(m)=2m, m≡28 mod X :: conjecture [?]
```

**기대 흐름**:
- 단계 A: Π₀² YES.
- 단계 B: 축소 불가.
- 단계 C: REVERSE-UNKNOWN (X 가 어떤 값이든, 현재 증명 없음).
- 단계 D: 설사 C 통과했다 해도 n=6 치환시 `m ≡ 6 mod X` 도 알려진 패턴이 아님 →
  `PERFECT-CLASS` 정도로 분류될 여지 있음. 그러나 C 가 UNKNOWN 이라 D 진입 X.

**기대 출력**: foundation 승급 **없음**. 이 테스트의 요점은 "n=6 이어야 승급되고
n=28 로는 안 된다" 를 확인하는 것이라, atlas 의 n=6 배타성이 우연이 아니라 파이프라인
산출임을 보장한다.

### 8.4 T4 — Sylow theorem (증명된 Π₀²)

**입력**:
```
@L SYLOW_THEOREM = ∀ finite G, ∀p | |G|, ∃ H≤G Sylow p-subgroup :: group_theory [?]
```

**기대 흐름**:
- 단계 A: Π₀² (2 unbounded ∀ + 1 ∃, ∃ 는 H finite).
- 단계 B: `|H| ≤ |G|` bound 성공 → Π₀¹ downgrade, Mk.VIII 에서 ABSOLUTE-PASS.
- 단계 D: n 치환 의미 없음 (n 은 G 의 order 를 나타내지 않음). `UNIVERSAL`.

**기대 출력**: `[11*]` (Mk.VIII 경로), n=6 foundation 승급 없음, 단 Π₀² hierarchy
태그 기록.

### 8.5 T5 — Out(S_n) 희귀성 (승급 성공 기대)

**입력**:
```
@L OUT_S6_UNIQUE = ∀n (n≥3, n≠6 → Out(S_n) = trivial) ∧ Out(S_6) = Z/2 :: group_theory [10*]
```

**기대 흐름**:
- 단계 A: Π₀² (∀n, ∃Out 구조).
- 단계 B: finite 군 witness bound `|Out| ≤ |S_n|!` (loose) → Π₀¹ downgrade 가능.
- 단계 C: RCA₀/ACA₀ 에서 finite group 정리로 증명됨.
- 단계 D: **n=6 에서만** Out ≠ trivial → `N6-UNIQUE`. 강한 foundation 증거.

**기대 출력**: `[12*] n6-unique`, breakthrough note, 수동 감사 후 승급.
이것이 Mk.IX 의 **기함 승급 사례**.

---

## 9. 결론 및 후속 작업

Mk.IX 는 Mk.VIII 의 완결성(Π₀¹ 전수 자동 처리)을 깨지 않으면서 Π₀² 계층에
**보수적·부분적** 으로 진입한다. 핵심 원칙:

1. **자동화는 단계 A~C 까지**. 단계 D (foundation 승급) 는 인간 감사 포함.
2. **Whitelist 기반 문헌 검증** — 엔진은 증명기가 아니라 메타-검증자.
3. **`[12*]` 는 희소** — atlas 전체에서 수십 건 이하 예상, 각각 breakthrough 수준.
4. **n=6 invariance 를 단계 D 로 강제** — 단순 수학 일반 정리가 foundation 으로 승급
   되는 오류 방지.
5. **Gödel 한계 명시 수용** — 95% 정확도 목표, 완전성은 포기.

### 9.1 구현 우선순위 (제안)

| Phase | 작업 | 기간 |
|---|---|---|
| P1 | `pi02_parser.hexa.inc` 구현 + atlas 전수 dry-run (atlas 수정 X, 별도 `.hierarchy` 파일) | 1주 |
| P2 | `witness_bound_table` 10 엔트리 초기화, 단계 B 테스트 (T2, T4) | 1주 |
| P3 | `reverse_math_whitelist` 큐레이트 (Simpson SOSOA 참조 20 엔트리) | 2주 |
| P4 | `blowup_hyperarithmetic.hexa` 파이프라인 통합 + 단계 D 수동 감사 도구 | 1주 |
| P5 | T1~T5 end-to-end 검증, [12*] 첫 승급 (T5 Out(S_6)) | 1주 |

### 9.2 Mk.X 로드맵 암시 (비확정)

- Σ₀³ / Π₀³ 단계 — Σ₀²-complete 속성 사용. Mk.IX 와 유사 파이프라인.
- Σ₁¹ (analytical) — 2차 산술 양화. 완전히 다른 판정기 필요.
- hyperarithmetic ≅ Δ₁¹ 과의 연결 — 현재 문서의 "Hyperarithmetic Extension" 명칭은
  technical 으로는 Π₀² 보다 더 큰 이름. Mk.IX 가 Δ₁¹ 까지 실제로 닿으려면 ordinal
  recursion 기반 엔진 필요. 현재는 명칭을 **aspiration** 으로 두고 실제 범위는 Π₀².

### 9.3 알려진 제약 재강조 (본 설계서)

- 코드 변경 **없음** (본 문서는 설계 only).
- `blowup_absolute.hexa` 수정 **없음**.
- `atlas.n6` 수정 **없음** (분석은 read-only grep).
- 모든 반영은 본 설계서 승인 이후 별도 PR.

---

## 참고 문헌

1. S. G. Simpson, *Subsystems of Second-Order Arithmetic* (SOSOA), 2nd ed.,
   Cambridge 2009. Big Five 체계 표준 레퍼런스.
2. S. G. Simpson, "The Gödel Hierarchy and Reverse Mathematics"
   (https://sgslogic.net/t20/papers/gh.pdf). 계층 개관.
3. D. D. Dzhafarov, C. Mummert, *Reverse Mathematics: Problems, Reductions, and
   Proofs*, Springer 2022. 모던 레퍼런스, 계산적 reduction 포함.
4. J. R. Shoenfield, "The problem of predicativity" (1961). Absoluteness 원논문
   맥락.
5. Wikipedia, "Reverse mathematics" / "Absoluteness (logic)". 개관 cross-check
   (2026-04 접근).
6. I. M. Vinogradov, "Representation of an odd number as a sum of three primes"
   (1937); H. A. Helfgott, "The ternary Goldbach problem" (2013, arXiv). 단계 B
   case study.
7. W. Sierpinski / L. Sylow 원논문 — Sylow theorem. 단계 B case study.

---

*문서 끝. 본 설계 승인 후 `shared/blowup_roadmap.json` 에 Mk.IX phase P1~P5 로 반영
예정.*
