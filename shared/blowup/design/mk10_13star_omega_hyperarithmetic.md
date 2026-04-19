# Mk.X [13*] ω-Hyperarithmetic 등급 — 분석 계층 진입 설계서

**상태**: DESIGN ONLY (코드 변경 없음, 자동 승급 코드 없음)
**선행**:
  - Mk.VIII Δ₀-absolute (`shared/blowup/modules/blowup_absolute.hexa`)
  - Mk.IX Π₀² hyperarithmetic (`shared/blowup/design/mk9_hyperarithmetic.md`)
  - Mk.X 5축 인프라 (`shared/discovery/mkx_design_proposal.md`)
**작성일**: 2026-04-19
**범위**: `[12*]` Π₀² foundation 위 새 등급 `[13*]` 정의 — ω-hyperarithmetic / Δ¹₁ / Π¹₁-CA₀ 영역
**비목표**:
  - 실 자동 승급 코드 작성 (제안 인터페이스만)
  - 첫 후보의 atlas 반영 (드라이런 5건만)
  - `[14*]` 이상 사다리 (Mk.XI 후속)

---

## 0. 요약 (Executive Summary)

Mk.IX 의 `[12*]` 는 Π₀² 부분 판정 + 인간 감사로 atlas foundation 사다리의
**산술 계층(arithmetical hierarchy)** 의 자연스러운 천장 — `Π₀³` 이상은 alternation
폭발로 reverse-math 문헌 DB 가 사실상 비어 있다.

본 설계서는 다음 도약을 **alternation 더 쌓는 방향**(Π₀³ → Π₀^n) 이 아니라
**1차 산술 위로 한 칸 — 2차 산술의 분석 계층(analytical hierarchy)** 으로 잡는다:

```
Π₀¹ → Π₀² → ⋯ → Π₀^n (산술 천장) ⊂ ω-hyperarithmetic ≅ Δ¹₁ ⊊ Π¹₁ ⊊ Σ¹₁
                    └── [11*] ──┘     └── [12*] ──┘   └─── [13*] ───┘
```

`[13*]` 를 **Π¹₁-CA₀ 인증서 + Δ¹₁ 가능성 + Borel hierarchy 상의 well-foundedness** 세
필러 위에 정의한다. 핵심 기술적 변화 세 가지:

1. **검증 알고리즘이 증명기가 아닌 reduction-checker** — Π¹₁-CA₀ 또는 ATR₀ 에서
   알려진 동치 정리로 환원되는지 확인하고, 환원 chain 의 각 단계가 algorithmic
   ally checkable (Σ₀¹) 임을 요구.
2. **n=6 연관은 σ·φ=24 의 `well-ordering` 표현 형식**으로 — Δ¹₁ 의 ordinal-encoding
   `ω·6 = 24-th 성분` 매칭으로 invariance 정의.
3. **자동 승급 영구 금지** — `[12*]` 와 같은 단일 인간 감사가 아니라 **3인 + L0 +
   Π¹₁-CA₀ 인증서 외부 검토 + 30일 dispute window** 4중 게이트.

`[13*]` 후보는 본 설계서 적용 시 **연 2~5건 이하** 로 강제 희소. 5 도메인
드라이런(HCT/HOTT/MOT/DAG/일반수학) 은 §6 에 dry-run 결과만 기록 — atlas 반영 없음.

---

## 1. 이론 배경

### 1.1 산술 → 분석 계층 한 줄 도약

산술 계층(arithmetical hierarchy)은 1차 산술 언어(`0,S,+,×,=,<`) 위에서 quantifier
alternation 으로 만들어진다 (Mk.IX §1.1):

```
Δ₀ ⊂ Σ₀¹ ⊊ Π₀¹ ⊊ Σ₀² ⊊ Π₀² ⊊ ⋯ ⊊ Σ₀^n ⊊ Π₀^n ⊊ ⋯
```

이 모든 계층의 합집합은 **arithmetical sets** = Π_∞⁰ = ⋃_n Σ₀^n. 그 위에 2차 산술의
**집합 변수**(set variable) 를 추가하면 분석 계층(analytical hierarchy):

```
arithmetical ⊊ Σ¹₁ ⊊ Π¹₁ ⊊ Σ¹₂ ⊊ Π¹₂ ⊊ ⋯
```

여기서 가장 작은 새 단계가 `Σ¹₁` (∃X. φ(X), φ ∈ arithmetical) 와 `Π¹₁` (∀X. φ).
**hyperarithmetic** sets 는 Δ¹₁ = Σ¹₁ ∩ Π¹₁ 로 정의되며, 이것이 *analytical 안에서의
arithmetical 자연 확장* 이다 (Kleene 1955).

핵심 정리들:
- **Suslin–Kleene**: hyperarithmetic = Δ¹₁ (실수 집합으로 보면 Borel ≡ Δ¹₁ on reals).
- **Spector–Gandy**: Π¹₁ 술어는 ω₁^{CK} 까지의 hyperarithmetic 술어 합성으로 표현.
- **Π¹₁-CA₀**: reverse mathematics 의 Big Five 최강. ATR₀ ⊊ Π¹₁-CA₀.
- **Borel determinacy**: ZFC 에서 증명되지만 ZF\P 에서는 Π¹₁-CA₀ 보다 강함 (Friedman).

`[13*]` 가 진짜 새 등급인 이유: Π₀^n 은 모두 arithmetical 안에 있어 0^(n) jump 로
oracle 환원되지만, Π¹₁ 은 본질적으로 **2차 양화** 가 필요. Mk.IX 의 0′ oracle 패러다임
밖이고, Mk.VIII 의 Shoenfield (Σ¹₂ 사이) 와 다른 결.

### 1.2 ω-hyperarithmetic 의 의미

표준 정의 (Sacks, *Higher Recursion Theory*, 1990):
- `0` = recursive (Δ⁰₁).
- `0^(n)` = n-th Turing jump (n < ω).
- `0^(ω)` = arithmetical = ⋃ 0^(n).
- `0^(ω+1)` = first non-arithmetical = jump of arithmetical.
- ⋯ 모든 recursive ordinal α 에 대해 `0^(α)` 정의.
- ω₁^{CK} = first non-recursive ordinal. `0^(ω₁^{CK})` 까지 hyperarithmetic.

따라서 **ω-hyperarithmetic** ≈ "alternation 을 ω 번 (또는 그 이상 recursive ordinal
번) 쌓을 수 있는 계층" = Δ¹₁ on reals.

수학적 명제 형태:
- **inductive definition fixed point**: Knaster–Tarski 고정점, monotone Γ : 2^ℕ → 2^ℕ
  의 least fixed point. Π¹₁-CA₀ 에서 표준.
- **well-foundedness statements**: "tree T 가 well-founded" = `∀ branch f ∃ n. f|n ∉ T`
  → Π¹₁ (branch 는 함수 = 집합 변수).
- **Borel sets equality / measurability**: `Borel(B) = T(B) ?` 류.
- **Σ¹₁ choice**: `∀x ∃Y. ψ(x,Y)` → `∃F ∀x. ψ(x, F(x))`. countable choice 의 분석
  버전.

### 1.3 [12*] (Mk.IX) 의 천장 분석

Mk.IX `[12*]` 는 Π₀² 까지만 다룬다. 다음 두 종류 명제는 **이미 atlas 에 후보로
존재하지만 [12*] 단계 C 가 reject 한다**:

**유형 X1 — Inductive definition** (Π¹₁ 표준 형태):
```
"모든 monotone 닫힘 연산 Γ 에 대해 least fixed point μΓ 존재"
"Sequent calculus 의 cut-elimination 이 모든 증명에 종료"
```
이들은 quantifier 가 `∀ Γ ∃ μΓ ∀ A ⊆ ℕ (Γ(A)=A → μΓ ⊆ A)` — `Γ` 자체가 함수 변수
(2차) → analytical 계층 ⇒ Mk.IX 단계 A 에서 `≥Π₀³` 로 reject (위계 구문은 산술 안에서
구분 불가).

**유형 X2 — Well-foundedness**:
```
"⊨ T well-founded → ω · ord(T) < ω₁^{CK}"
"모든 recursive ordering 의 well-foundedness 는 Π¹₁"
```
이들은 ATR₀ 에서 표준 처리. Mk.IX 의 reverse-math 5체계 중 ATR₀ / Π¹₁-CA₀ 점수
계산은 가능하나 단계 C 의 휴리스틱 임계 (`ACA₀ 이상`) 가 너무 약해 실제로 0건 통과.

**유형 X3 — Σ¹₁ choice / Borel hierarchy**:
```
"∀ Borel set B, ∃ Borel selector f"
"Σ¹₁ 집합의 Δ¹₁ 분리"
```
완전히 Mk.IX 밖. 단계 A 가 `≥Π₀³` 로만 분류.

**결론**: 이 세 유형이 atlas 에 어떤 형태로든 나타날 때, Mk.IX 는 일률적으로 reject.
Mk.X `[13*]` 는 이 reject 들을 별도 큐에 쌓아 **Π¹₁-CA₀ 인증서** 또는 **ATR₀ 인증서**
가 있는지 검토하는 새 파이프라인.

### 1.4 Π¹₁-CA₀ vs ATR₀ vs Δ¹₁

reverse mathematics Big Five (Simpson, SOSOA 2009):

| 체계 | 강도 | 표준 동치 정리 |
|---|---|---|
| RCA₀ | recursive comprehension + Σ₁⁰ induction | Soare-recursive set theory |
| WKL₀ | + weak König (compactness on 2^ω) | Heine-Borel for [0,1], Brouwer FP |
| ACA₀ | arithmetical comprehension | Bolzano-Weierstrass, Ramsey(3) |
| ATR₀ | arithmetical transfinite recursion | well-ordering 비교, Borel hierarchy 정의 |
| Π¹₁-CA₀ | Π¹₁ comprehension | Cantor-Bendixson, perfect kernel, ATR₀ 자체의 일관성 |

**`[13*]` 게이트는 ATR₀ + Π¹₁-CA₀ 두 체계 모두 PROVEN 일 때만 통과**. 단일 체계로는
`[12*]` 와의 차별이 약하다 (Mk.IX 가 ATR₀/Π¹₁-CA₀ 자명 PROVEN 처리하므로 false
positive 위험).

Δ¹₁ 정의 자체는 위 체계로 산술 인코딩이 어려워 — `[13*]` 의 Δ¹₁ 가능성은 별도
필러로 분리 (§3.2).

---

## 2. 등급 사다리 확장: `[13*]` 위치

### 2.1 등급 전체 표

| 등급 | 의미 | 절대성 층위 | 자동? |
|---|---|---|---|
| `[7]` | EMPIRICAL | 수치 일치 | 자동 |
| `[9]` | NEAR | 근접 | 자동 |
| `[10]` | EXACT | 수치 검증만 | 자동 |
| `[10*]` | EXACT-검증 | Π₀¹ arithmetical | 자동 (Mk.II~VII) |
| `[10**]` | self-ref closure | Phase 10 meta-closure | 자동 (Mk.IX phase 10) |
| `[11*]` | Δ₀-absolute foundation | Shoenfield, transitive model invariant | 자동 (Mk.VIII) |
| `[11**]` | tier 6~9 substrate | A6 meta_closure + AN14 Knuth | 자동 (Mk.V.1, anima) |
| `[12*]` | Π₀² hyperarithmetic foundation | ACA₀ + n=6 core | 인간 감사 (Mk.IX) |
| **`[13*]`** | **ω-hyperarithmetic / Δ¹₁ foundation** | **ATR₀ + Π¹₁-CA₀ + n=6 ordinal-encoding** | **3인 + 외부 + 30d** |
| `[14*]` (예정) | analytical Σ¹₁ / determinacy | Σ¹₂ / projective | TBD (Mk.XI+) |

### 2.2 [12*] vs [13*] 차이점 (정형)

| 축 | `[12*]` | `[13*]` |
|---|---|---|
| 산술 위계 | Π₀² (2 alternation, bounded matrix) | Π¹₁ / Δ¹₁ (2차 양화) |
| Oracle | 0′ (Halting) | 0^(α), α < ω₁^{CK} |
| Reverse-math 임계 | ACA₀ 이상 3/5 | ATR₀ 이상 + Π¹₁-CA₀ 인증 |
| n=6 invariance | 수치 치환 (`6 ↦ k`) | ordinal-encoding (`ω·6 = 24-th`) |
| 인간 게이트 | 1인 감사 + L0 | 3인 + L0 + 외부 검토 + 30d dispute |
| 후보 빈도 | 연 5~10 | 연 2~5 (강제 희소) |
| 표기 | `foundation [12*]` | `foundation [13*] omega-hyper` |
| 1차 atlas 반영 | Mk.IX W2 (Out(S_6)) | 본 설계 채택 후 Mk.X.5 (TBD) |

### 2.3 사다리 위 칸 보존 정합성

`[13*]` 는 `[12*]` 를 **strict 상위**:
- `[13*]` 후보는 자동으로 `[12*]` 후보가 되어야 한다 (단계 A~D 통과).
- 단, `[12*]` 단계 C 가 reverse-math 5체계 중 ATR₀/Π¹₁-CA₀ 두 칸 모두 PROVEN 이어야
  `[13*]` 추가 검증 진입.
- `[13*]` 후보의 atlas line 수정은 `[10*] → [12*] → [13*]` 2 step 거치거나, Mk.X 의
  `promote_13star.hexa` (예정) 가 `[10*] → [13*]` 직접 점프 가능 (단, `[12*]` 인증서
  동봉 의무).

---

## 3. `[13*]` 검증 5-Phase Pipeline

Mk.IX 의 4단계 (A 구문 / B bounded / C reverse / D n=6) 를 **5단계** 로 확장.
새 단계 E 가 `[13*]` 전용.

### 3.1 단계 A — 구문 탐지 확장 (Π¹₁ / Σ¹₁ 인식)

기존 Mk.IX 의 `is_pi02()` 는 1차 산술 구문만 본다. 새 inspector:

```
classify_analytical(expr) -> {
  Δ₀, Π₀¹, Σ₀¹, Π₀², Σ₀², ≥Π₀³,
  Π¹₁, Σ¹₁, Δ¹₁, ≥Π¹₂
}
```

핵심 추가 패턴:

| 자연어 / 수식 패턴 | 분류 |
|---|---|
| `∀ X ⊆ ℕ, φ(X)`, "모든 부분집합", "for every set" | Π¹₁ (φ arithmetical 시) |
| `∃ f : ℕ → ℕ, ψ(f)`, "어떤 함수가 존재", "there exists a function" | Σ¹₁ (ψ arithmetical 시) |
| `∀ tree T well-founded`, "모든 well-founded tree" | Π¹₁ (well-foundedness 표준) |
| `∀ Γ monotone, μΓ`, "최소 고정점" | Π¹₁-CA₀ 영역 |
| `Borel set`, `Δ¹₁`, `analytic set`, "해석 집합" | Σ¹₁ family |
| `recursive ordinal`, `ω₁^{CK}`, "Church-Kleene" | hyperarithmetic 명시 |

분류 보수성:
- 자연어 "모든 함수" 가 단순 `f: A → B` (A,B 유한) 이면 **여전히 Δ₀** — 단계 A 의
  보수 룰: bound 정보가 명시될 때만 산술로 다운그레이드.
- "set" 이 finite set (cardinality bounded) 이면 산술. unbounded ℕ 위 부분집합이면
  analytical.
- 한국어 조사 부재로 인한 모호성 — `@analytic_marker` annotation 필수 (atlas line 에
  명시) 시에만 Π¹₁/Σ¹₁ 진입.

**실패 모드**:
- "모든 컴팩트 집합" → measure-theoretic, 형식상 Π¹₁ 이지만 atlas 의 일반 사용은
  arithmetical 으로 간주되는 경우 — 감사자 판정 필요.
- self-reference (Berry, Gödel 류) — Mk.IX 블랙리스트 (`mk9_first_candidates.md` §4.2)
  계승 + analytical 변종 추가 차단.

### 3.2 단계 B — Δ¹₁ 가능성 (Σ¹₁ ∩ Π¹₁ 동시 표현)

명제 `P` 가 Π¹₁ 로 분류되면, **Σ¹₁ 동치 표현이 존재하는가**를 확인. 존재하면 Δ¹₁
→ hyperarithmetic 확정.

알고리즘:
1. P 의 Π¹₁ 표현 `∀X φ(X)`.
2. 알려진 동치 표현 DB (`shared/blowup/design/mk10_delta11_witnesses.json` 예정)
   조회:
   - "well-founded" → 동치 "rank function 존재" (Σ¹₁).
   - "monotone Γ 의 fixed point" → 동치 "least pre-fixed point 존재" (Σ¹₁).
   - "Borel set" → 동치 "Σ⁰_α + Π⁰_α layered" (Σ¹₁ 표현 가능).
3. Σ¹₁ 동치 발견 → **Δ¹₁-VIA-DUAL** 라벨 → Mk.IX 의 ABSOLUTE-PASS 와 유사 위상.
4. 미발견 → Π¹₁-only 경로 (단계 D 로 fallback).

**witness DB 초기 엔트리** (예정):

| Π¹₁ 형태 | Σ¹₁ 동치 | 근거 |
|---|---|---|
| WF(T) (tree T well-founded) | ∃ rank fn ρ : T → ω₁^{CK} | Kunen, *Set Theory* |
| LFP(Γ) ⊆ A (monotone Γ, A inductively defined) | ∃ stage σ < ω₁^{CK}, Γ^σ(∅) ⊆ A | Aczel, *Inductive Defn* |
| Borel(B) = T(B) | ∃ Borel code w, Eval(w) = B | Moschovakis, *Descriptive Set Theory* |
| ATR₀ ⊢ φ | ∃ proof tree π, π : ATR₀ → φ | Simpson, SOSOA §V |

### 3.3 단계 C — Π¹₁-CA₀ 인증서

ATR₀ + Π¹₁-CA₀ 두 체계의 **증명 인증서** 를 명시 요구. Mk.IX 의 reverse-math
"5/5 PROVEN" 휴리스틱과 다르게, `[13*]` 는 인증서 자체를 atlas 에 첨부:

```yaml
certificate:
  system: PI11_CA0           # ATR0 또는 PI11_CA0
  reference:
    type: paper              # paper | textbook | formalization
    title: "..."
    author: "..."
    year: 2009
    section: "§V.6.2"
    doi: "10.1017/CBO9780511581007"
  proof_sketch: |
    1. P 를 well-foundedness 형태로 환원: ...
    2. ATR₀ 의 transfinite recursion 으로 rank fn 구성: ...
    3. Π¹₁-CA₀ comprehension 으로 fixed point 추출: ...
  formal_check:
    formalized: true|false
    tool: "Coq / Lean / Isabelle / Mizar"
    repo_url: "https://..."
  verifier_signoff:
    auditor_1: "<handle>"   # 수론·논리
    auditor_2: "<handle>"   # 분석·DST
    auditor_3: "<handle>"   # 외부 (Simpson SOSOA 인용 가능자)
    sign_ts: "2026-MM-DDTHH:MM:SS+09:00"
```

**인증서 검증 자동화 가능 부분**:
- DOI / ISBN 형식 검증 (regex).
- formalized=true 일 때 repo_url 도달성 확인 (HTTP 200).
- proof_sketch 가 ATR₀ / Π¹₁-CA₀ 키워드 포함 여부.

**자동화 불가능 부분** (인간 필수):
- proof_sketch 의 수학적 정합성.
- reference 의 신뢰도.
- 외부 검토자 (auditor_3) 의 독립성.

### 3.4 단계 D — n=6 ordinal-encoding invariance

Mk.IX 의 n=6 치환 (`6 ↦ k`) 은 Π₀² 명제의 1차 구문에서만 의미가 있다. Π¹₁ /
Δ¹₁ 명제는 ordinal 변수 (well-ordering) 위에 정의되므로, n=6 invariance 도
**ordinal-encoding** 로 재정의.

**n=6 ordinal embedding**:
- 기본 axiom: `σ·φ = n·τ = 24` 는 곱셈 결과 24. ω·6 = 24 (시리얼 ordinal sum
  `ω + ω + ω + ω + ω + ω` ≡ 4·ω + 6·1 의 24-th 성분).
- ordinal expression `α = ω · 6` 가 `[13*]` 후보 명제의 well-foundedness 구조 안에
  나타나면 invariance 성립.
- 부재 시 — 명제는 일반 hyperarithmetic, n=6 foundation 승급 부적합 (`UNIVERSAL`
  classification).

**판정 알고리즘**:
1. `[13*]` 후보의 Π¹₁ 표현에서 ordinal 변수 `α` 추출.
2. `α = ω · 6`, `α = 6^ω`, `α = ω₁^{CK}` 같은 패턴이 자연 표현인지 검사.
3. ordinal 치환 `α ↦ ω · k` (k ∈ {2,3,4,5,7,12,28,496}) 으로 명제가 깨지는지:
   - 깨짐 → `N6-ORDINAL-UNIQUE`.
   - 유지 → `UNIVERSAL`.
   - 28, 496 에서만 유지 → `PERFECT-ORDINAL-CLASS`.
4. **추가 검증**: Mk.V.1 의 `phi_tier_label.hexa` 와 연결 — `L(k) = 24^(k-15)` 의
   k=16 base 가 `[13*]` 후보의 자연 ordinal 과 일치하는지 cross-check.

**예시**:
- `WF(ω · 6)` (rank-6 well-foundedness) → `N6-ORDINAL-UNIQUE`.
- `LFP(Γ) at stage ω₁^{CK}` (일반 inductive) → `UNIVERSAL`.
- `Borel(B) at level Σ⁰_(ω·6)` → `N6-ORDINAL-UNIQUE` (matrix 가 24-level 에서 닫힘).

### 3.5 단계 E — 30일 Dispute Window

`[13*]` 자동 승급 영구 금지 + 인간 감사 후에도 **30일 dispute window**:

1. 단계 A~D 통과 + 3인 sign-off 후 `[13*?]` (provisional) 마크.
2. `shared/blowup/audit/mk10_dispute_queue.jsonl` 에 30일 dispute window open.
3. 외부 검토자 (auditor_3) 의 독립 의견 + 신규 논문 / 형식화 결과 모니터링.
4. 30일 만료 + dispute 0건 → `[13*]` 확정 atlas write.
5. dispute 1건 이상 → `[13*?]` 유지 또는 `[12*]` 강등 결정 (재 3인 감사).
6. 강등 시 atlas dependency 그래프 전수 재검증 (Mk.IX 비상 중단 트리거 §3.4 동일).

이 단계 E 가 `[13*]` 의 결정적 차별점 — `[12*]` 는 단일 인간 감사로 즉시 승급, `[13*]`
는 4중 게이트 + 시간 잠금.

---

## 4. n=6 연관: Δ¹₁ 와 σ·φ=24 의 link

`[13*]` 가 진짜 n=6 foundation 인지 의문이 자연스럽다. 본 절은 link 4가지를 명시.

### 4.1 link L1 — ω·6 = 24 ordinal identity

n=6 axiom `σ·φ = n·τ = 24` 의 24 는 ordinal arithmetic 에서 `ω·6` 의 정확한
finite stage. 즉 transfinite ordinal 표현 `ω·6` 의 `24-th 성분` (서수합 6·ω = ω·6 의
6 카피 합) 는 atlas META-LK017~500 의 `[11*]` 인증과 호환.

이 identity 는 `phi_tier_label.hexa` 의 `L(k) = 24^(k-15)` 공식의 k=16 base (`L(16) =
24` ) 와 동치 — Mk.V.1 의 Knuth bridge 가 이미 사용하는 표현.

### 4.2 link L2 — n=6 unique well-ordering 결정

S_6 의 outer automorphism `Out(S_6) = ℤ/2` 는 n=6 에서만 발생 (Hölder 1895, atlas
L13418). 이를 well-ordering 의미로 풀면:

> "ω·6 길이의 well-ordering 위에서 자기준동형군이 trivial 이 아닌 유일한 ordinal
>  product 는 ω·6"

이는 Π¹₁ 명제 (`∀ ordinal α, |Aut(α)| = 1 ↔ α ≠ ω·6`) 로 인코딩 가능. `[13*]` 후보
1순위.

### 4.3 link L3 — n=6 Δ¹₁ minimal coding

Δ¹₁ 의 표준 hyperarithmetic 코드 시스템 (Kleene's O) 은 ordinal `α < ω₁^{CK}` 에 자연
번호 코드 `|α|` 부여. `|ω·6| = 6 + 1 + ω-code = recursive ordinal 의 가장 단순한
multi-stage 표현`.

n=6 의 `최소 완전수` 성질 (1+2+3=6, 1·2·3=6, σ(6)=12=2·6) 과 직접 대응:
- `1+2+3` ↔ `1+ω+ω·2 = ω·3` ?— 부분 대응만, 강한 link 아님.
- `1·2·3` ↔ `1·ω·(ω·2)` — ordinal 곱은 비가환, link 약함.
- `σ(6)=12` ↔ `σ(ω·6) = ω·12` ? — divisor sum 의 ordinal 확장은 표준 미정의.

**결론**: link L3 는 약함 — design 시 명시.

### 4.4 link L4 — Borel hierarchy n=6 layer

Borel hierarchy `Σ⁰_α, Π⁰_α (α < ω₁)` 는 ordinal stage. **`Σ⁰_(ω·6) = Σ⁰_24` 위치는
finite Borel hierarchy 가 saturate 되는 첫 transfinite stage**.

이 위치에서 `Σ⁰_24 = Π⁰_24 ?` (즉 closure under complement at level 24) 가 n=6
invariant 와 연결 — atlas META-INF-OR (Order of saturation) 와 cross-ref 가능.

`[13*]` 후보 2순위: `Σ⁰_24 의 closure properties` 류 명제.

### 4.5 link 종합

4 link 중 L1, L2, L4 는 강함. L3 약함. `[13*]` n=6 invariance 판정은:
- L1 또는 L2 매칭 → `N6-ORDINAL-UNIQUE` 가능.
- L4 매칭 → `N6-BOREL-CORE` (새 sub-classification).
- 어느 것도 매칭 X → `UNIVERSAL` (foundation 승급 부적합).

---

## 5. 자동 승급 vs 인간 게이트 정책

### 5.1 자동 승급 영구 금지

`[13*]` 는 다음 4 가지 이유로 자동 승급 금지:

1. **Π¹₁-CA₀ 인증서 자체가 외부 (논문/형식화) 의존** — atlas 내부 휴리스틱으로
   생성 불가.
2. **Δ¹₁ duality 검증은 알려진 동치 DB 룩업** — DB 가 미완 상태에서 자동 통과 시
   false positive 위험 매우 큼.
3. **n=6 ordinal-encoding link** 는 4가지 중 적어도 1가지가 strong 매칭이어야 하며,
   매칭 strength 판정은 의미적.
4. **30일 dispute window** 자체가 시간 인자 — 자동화 불가.

### 5.2 4중 게이트 정확 절차

```
[10*] candidate
  │
  ▼
단계 A: classify_analytical()  ← 자동 (구문)
  │  └─ 결과 ∈ {Π¹₁, Σ¹₁, Δ¹₁, ≥Π¹₂} → 진행
  │     그 외 → Mk.IX 로 회부
  ▼
단계 B: Δ¹₁ duality DB lookup ← 자동 (DB)
  │
  ▼
단계 C: Π¹₁-CA₀ certificate  ← 인간 (3인 sign + 외부 검토)
  │     - reference / proof_sketch / formal_check / verifier_signoff
  │
  ▼
단계 D: n=6 ordinal-encoding ← 자동 + 인간 (자동 매칭 + 의미 판정)
  │     - L1~L4 link 검사
  │     - N6-ORDINAL-UNIQUE / N6-BOREL-CORE / UNIVERSAL 분류
  ▼
[13*?] provisional mark  ← atlas 미반영
  │
  ▼
단계 E: 30-day dispute window  ← 시간 (자동 timer + 인간 모니터)
  │     - shared/blowup/audit/mk10_dispute_queue.jsonl
  │     - 외부 검토 결과 dispatch
  ▼
[13*] confirmed → atlas.live.n6 write (promote_13star.hexa, 인증서 동봉)
```

### 5.3 게이트 도구 (예정 인터페이스만)

```bash
# 단계 A~B 자동 dry-run
hexa shared/blowup/audit/mk10_classify.hexa <candidate_id>

# 단계 C 인증서 작성 도우미 (인터액티브)
hexa shared/blowup/audit/mk10_certificate.hexa <candidate_id>

# 단계 D n6-ordinal 매칭 dry-run
hexa shared/blowup/audit/mk10_n6_ordinal.hexa <candidate_id>

# 단계 E dispute window 모니터
hexa shared/blowup/audit/mk10_dispute_monitor.hexa --list

# 30일 만료 + dispute 0 → atlas write (모든 인증서 동봉 강제)
hexa shared/blowup/audit/promote_13star.hexa <candidate_id> --commit
```

위 도구 5종은 본 설계 채택 후 별도 commit 으로 작성. 본 세션은 인터페이스만.

### 5.4 인간 게이트 cadence

`[12*]` 는 월 1회 감사 (Mk.IX `mk9_first_candidates.md` §3.1). `[13*]` 는:
- **분기 1회 감사** (3, 6, 9, 12월) — 인증서 작성 시간 고려.
- 분기당 후보 ≤ 2건 처리 한도.
- 연 최대 8건, 실제 통과는 2~5건 예상.
- `[13*]` atlas 누적 기대: 5년 후 ≤ 30건. 강제 희소.

---

## 6. 5 후보 dry-run (각 1건)

각 후보는 단계 A~D 자동 판정만 dry-run. 단계 C/E 인증서·dispute 는 미수행.
**atlas 반영 0건**, 본 설계 §6 는 read-only 분석.

상세는 `shared/blowup/audit/mk10_13star_first_candidates.md` 참조. 본 절은 요약.

| # | 도메인 | 명제 | 단계 A | 단계 B | 단계 D | 권장 |
|---|---|---|---|---|---|---|
| 1 | HCT (∞-cat) | univalence 일반화 | Π¹₁ | Δ¹₁ 가능 | UNIVERSAL | DEFER |
| 2 | HOTT | univalence axiom 정칙성 | Π¹₁ | Δ¹₁ 가능 | UNIVERSAL | DEFER |
| 3 | MOT (motivic) | Beilinson higher cohomology | Σ¹₁ | UNKNOWN | N6-BOREL-CORE 후보 | PEND |
| 4 | DAG | E∞ ring 분류 공간 | Π¹₁ | Δ¹₁ 미정 | UNIVERSAL | DEFER |
| 5 | 일반수학 | Borel determinacy (ω·6 layer) | Π¹₁ | Σ¹₁ 동치 미발견 | N6-ORDINAL-UNIQUE 후보 | PEND |

5 후보 중 `[13*]` PEND 자격 = 2건 (MOT, Borel-ω·6). DEFER 3건은 단계 D 에서 n=6
ordinal link 약함 → foundation 승급 부적합.

**중요**: PEND 2건도 본 설계서 단계 C (Π¹₁-CA₀ 인증서) + 단계 E (30일 dispute) 미수행
이라 즉시 atlas write 금지. Mk.X 채택 후 2026-Q3 분기 감사 큐에 진입 가능.

---

## 7. atlas 반영 형식 (예정)

### 7.1 [13*] 라인 형식 (최종 확정 전)

```
@L NAME :: foundation [13*] omega-hyper
  <- dependencies
  => "Π¹₁ statement in prose"
  => "delta11_dual: ∃ Σ¹₁ dual via WF rank function (witness_db_id=W003)"
  => "reverse-math certificate: ATR₀ + Π¹₁-CA₀ proven (Simpson SOSOA §V.6.2)"
  => "n6 ordinal-encoding: N6-ORDINAL-UNIQUE (link L2 strong: Out(S_6) ω·6)"
  => "formal_check: Lean (https://github.com/.../...)"
  => "verifier_signoff: A1=박민우, A2=<handle>, A3=<external>, sign_ts=2026-MM-DDTHH:MM:SS+09:00"
  => "dispute_window: 2026-MM-DD 까지 dispute=0 → confirmed"
  !! breakthrough-2026-MM-DD "13star confirmed after 30d dispute window"
```

기존 `[12*]` Mk.IX 양식 + 4 줄 (delta11_dual / formal_check / dispute_window /
breakthrough) 추가.

### 7.2 sidecar 메타 확장

`atlas.n6.stats` schema 4 (예정):

```json
{
  "schema": 4,
  "...": "...",
  "hierarchy": {
    "delta0": N1, "pi01": N2, "sigma01": N3,
    "pi02": N4, "sigma02": N5, "higher_arith": N6,
    "pi11": N7, "sigma11": N8, "delta11": N9,
    "higher_analytic": N10, "unknown": N11
  },
  "foundation_tiers": {
    "10_star": A, "10_dstar": A2, "11_star": B,
    "11_dstar": B2, "12_star": C, "13_star": D
  }
}
```

`schema` 3 → 4 migration 은 sharding (Mk.X 축 1) 도입 후 `atlas.live.n6` 만 적용.

### 7.3 검증 algorithm hash

`[13*]` 라인의 인증서 무결성 hash (sidecar):

```
shared/blowup/audit/mk10_certificates/<candidate_id>.yaml
shared/blowup/audit/mk10_certificates/<candidate_id>.sha256
```

hash 가 atlas 라인의 `=> "verifier_signoff: ..."` 필드와 cross-check 통과 시 atlas
read 단계에서 무결성 보장. 위반 시 L0 guard 이벤트.

---

## 8. 리스크 & 한계

### 8.1 Π¹₁-CA₀ 인증서 위조 위험

3인 sign-off + 외부 검토자가 cartel 형성하면 가짜 인증서 가능. mitigation:
- 외부 검토자는 **무작위 선정** (atlas committers 이외 풀에서).
- proof_sketch 의 ATR₀/Π¹₁-CA₀ 키워드 자동 검사 + 수동 cross-check.
- 30일 dispute window 가 사후 catch-up 기회.

### 8.2 Δ¹₁ duality DB 미완성

`mk10_delta11_witnesses.json` 초기 엔트리 4건 (§3.2 표). 미수록 명제는 단계 B
fallback 으로 단계 D 직행 — Π¹₁-only 처리. DB 확장은 분기 단위 + 인간 감사.

### 8.3 n=6 ordinal-encoding 강제성

L1~L4 4개 link 중 하나라도 strong 매칭 요구 — atlas 의 진짜 hyperarithmetic 정리가
n=6 와 무관할 수 있다. 그 경우 `[13*]` 비후보, `[12*]` 또는 별도 sub-tier (예:
`[12**]` "general hyper", n=6 무관) 후속 설계 필요. 본 문서 범위 밖.

### 8.4 dispute window 30일의 적정성

선택 근거:
- 외부 논문 등재 cycle (대략 월 1~2회 신규 발표).
- 형식화 도구 (Lean / Coq) 의 평균 PR review 시간.
- 너무 짧으면 (예: 7일) 외부 cross-check 기회 부족.
- 너무 길면 (예: 90일) atlas update cadence 침식.

30일 = 현재 추정. Mk.X 운용 데이터 누적 후 조정 가능 (분기 1회 감사와 align).

### 8.5 자동화 불가 영역

`[13*]` 의 절반 이상이 인간 의존:
- 인증서 작성 (proof_sketch).
- 외부 검토자 선정.
- n=6 ordinal-encoding 매칭 강도 판정.
- dispute 의견 평가.

이는 `[13*]` 의 본질 — 자동화하면 foundation 의 신뢰도 자체가 무너진다.
agent 가 할 수 있는 것은 **준비, 메타 검증, monitoring** 까지.

### 8.6 Mk.IX 와의 회귀 호환성

`[13*]` 도입이 기존 `[12*]` 후보 / 인증서 / atlas 라인에 영향:
- `[12*]` Mk.IX 양식은 그대로 유지.
- `[13*]` 후보가 동시에 `[12*]` 자격이면 두 라벨 병기 가능 (`[12*][13*]`)? — 아니,
  단일 라벨 정책. `[13*]` 가 strict 상위이므로 `[13*]` 만 표시.
- 기존 `[12*]` 라인이 `[13*]` 로 승급되는 경우 in-place 치환 (Mk.VIII `[10*]→[11*]`
  선례 동일). `[10*] → [12*] → [13*]` 2-step 가능.

### 8.7 ω-hyperarithmetic 명칭 모호성

Mk.IX 가 모듈 이름을 `blowup_hyperarithmetic.hexa` 로 사용했으나 실제 범위는 Π₀² —
Mk.IX 설계 §9.2 자체가 "aspiration" 으로 표현. `[13*]` 가 실제 ω-hyperarithmetic =
Δ¹₁ 도달.

향후 명칭 정리:
- `blowup_hyperarithmetic.hexa` (Mk.IX) → `blowup_pi02.hexa` 로 rename 권장 (Mk.XI).
- `blowup_omega_hyperarithmetic.hexa` (Mk.X 신규) → 진짜 Δ¹₁ 엔진.
- 단, rename 은 본 설계 채택 + Mk.X 본격 구현 시점.

---

## 9. 구현 우선순위 (Mk.X 채택 시)

| Phase | 작업 | 기간 | 산출물 |
|---|---|---|---|
| P1 | `classify_analytical()` 구현 + atlas 전수 dry-run | 2주 | `pi11_parser.hexa.inc`, `atlas.n6.analytic_hierarchy` sidecar |
| P2 | `mk10_delta11_witnesses.json` 초기 10 엔트리 + 단계 B 자동화 | 2주 | witness DB JSON + `delta11_dual_check.hexa` |
| P3 | `mk10_certificate.hexa` 인터액티브 도우미 + 인증서 형식 | 1주 | tool + YAML schema |
| P4 | `mk10_n6_ordinal.hexa` 4 link 매칭 + 시각화 | 1주 | tool + L1~L4 매트릭스 |
| P5 | `mk10_dispute_monitor.hexa` 30일 timer + JSONL queue | 1주 | tool + queue |
| P6 | 첫 후보 (Borel determinacy ω·6) end-to-end dry-run | 4주 | 인증서 1건 + 30d window 시작 |
| P7 | dispute window 만료 + 첫 `[13*]` confirmed | (자동, 30일) | atlas.live.n6 라인 1건 |

총 예상: 11~15주 (약 3개월). Mk.X 5축 인프라 (sharding 등) 완료 후 시작 권장.

---

## 10. 비-목표 (Non-Goals)

- 본 설계서는 **자동 승급 코드 작성 안 함** — 인터페이스만.
- 5 후보 중 어느 것도 atlas 에 반영하지 않음.
- `[14*]` (analytical Σ¹₁ / determinacy) 는 Mk.XI 후속.
- Borel determinacy 의 ZF 형식화 자체 — 본 설계는 atlas foundation 등급 정의만.
- 외부 검토자 풀 구체화 — 정책 명시만, 실 명단은 별도 sealed 문서.
- Mk.IX `[12*]` 의 자동화 강화 — Mk.IX 그대로 유지.
- HoTT / ∞-cat / motivic / DAG 의 새 도메인 모듈 깊이 구현 — Mk.X 축 4 별도.

---

## 11. 결론

`[13*]` 는 atlas 의 **첫 분석 계층 foundation**. Mk.IX 의 산술 천장 위로 한 칸 도약,
Π¹₁-CA₀ 인증서 + Δ¹₁ duality + n=6 ordinal-encoding + 30일 dispute window 의 4중
게이트로 보호.

핵심 원칙 5:

1. **자동 승급 영구 금지** — 4중 인간/시간 게이트.
2. **Π¹₁-CA₀ 인증서 외부화** — atlas 내부 휴리스틱 의존 X.
3. **n=6 ordinal-encoding 강제** — `ω·6 = 24` link 명시.
4. **30일 dispute window** — 시간 잠금으로 false positive 차단.
5. **희소성 강제** — 연 2~5건, 5년 누적 ≤ 30건.

5 후보 dry-run 결과 (`mk10_13star_first_candidates.md`):
- DEFER 3건 (HCT / HOTT / DAG — n=6 link 약함)
- PEND 2건 (MOT / Borel-ω·6 — 단계 C/E 미수행)
- 즉시 승급 0건

본 설계 채택 시 P1~P5 구현 (~7주), 첫 후보 dry-run P6 (4주), 첫 confirmed P7 (30일).
총 ~14주.

---

## 참고 문헌

1. S. C. Kleene, "Hierarchies of Number-Theoretic Predicates" (1955) — hyperarithmetic
   원논문.
2. G. E. Sacks, *Higher Recursion Theory* (Springer 1990) — ω-hyperarithmetic 표준.
3. S. G. Simpson, *Subsystems of Second-Order Arithmetic* (SOSOA, Cambridge 2009)
   — Big Five 표준, 특히 §V (ATR₀), §VI (Π¹₁-CA₀).
4. Y. N. Moschovakis, *Descriptive Set Theory* (2nd ed., AMS 2009) — Borel hierarchy
   + Suslin–Kleene.
5. K. Kunen, *Set Theory: An Introduction to Independence Proofs* (1980) —
   well-foundedness 표준.
6. P. Aczel, *An Introduction to Inductive Definitions* (Handbook of Math. Logic,
   1977) — LFP / Π¹₁-CA₀.
7. H. M. Friedman, "Higher set theory and mathematical practice" (1971) — Borel
   determinacy 와 ZFC 강도.
8. D. D. Dzhafarov, C. Mummert, *Reverse Mathematics: Problems, Reductions, and
   Proofs* (Springer 2022) — modern 시각.
9. Univalent Foundations Program, *Homotopy Type Theory* (2013) — HoTT 표준 (단계
   B 의 inductive type 형식화 참조).
10. J. Lurie, *Higher Topos Theory* — ∞-cat 표준 (단계 A 의 ∞-categorical 양화 인식).

---

*문서 끝. 본 설계 채택은 사용자 + 3인 외부 검토자 추후 결정. 채택 전 코드 변경 0,
atlas 반영 0.*
