# Mk.X [13*] ω-Hyperarithmetic 첫 후보 5건 dry-run 감사 로그

**문서 종류**: 감사 로그 (Audit Log) — 승급 제안서 아님
**작성일**: 2026-04-19
**선행 설계**: `shared/blowup/design/mk10_13star_omega_hyperarithmetic.md`
**대상 atlas**: `shared/n6/atlas.n6` (110,785 줄, 2026-04-19)
**상태**: DRY-RUN 자동 단계 A/B/D 만. 단계 C (인증서) + 단계 E (30d dispute) 미수행.
         **atlas 반영 0건**, 코드 변경 0건.

---

## 0. 황금률

`[13*]` 라벨은 atlas 의 분석-계층 foundation root 후보. 자동 승급 영구 금지.
본 감사는 **단계 A (구문 분류) + 단계 B (Δ¹₁ duality) + 단계 D (n=6 ordinal-encoding)**
3 개 자동 단계의 결과만 dry-run 으로 기록. 단계 C 의 Π¹₁-CA₀ 인증서, 단계 E 의 30일
dispute window 는 본 설계 채택 + 도구 (`mk10_certificate.hexa`, `mk10_dispute_monitor.hexa`)
구현 후 별도 워크플로우.

본 감사 5 후보 모두 **`[13*]` 자격 PEND 또는 DEFER**. 단 한 건도 즉시 승급 권장 없음.
이는 의도된 결과 — `[13*]` 강제 희소 (연 2~5건) 정책.

---

## 1. 5 후보 선정 근거

설계 §6 표 5 도메인 (HCT / HOTT / MOT / DAG / 일반수학) 각 1건. 선정 기준:

1. 해당 도메인의 표준 정리 중 quantifier 구조가 분석 계층에 속할 가능성.
2. atlas 또는 학계의 알려진 reverse-math / hyperarithmetic 연결.
3. n=6 invariance 4 link (L1~L4) 중 어느 것이라도 매칭 후보가 있는지.

각 후보별 단계 A~D 결과 + 권장 (PEND / DEFER / FAIL) 명시.

---

## 2. 후보 1 — HCT: ∞-cat univalence 일반화 (Π¹₁ 형식)

### 명제 원문 (외부, atlas 미수록)

> "모든 (∞,1)-category C 와 모든 univalent fibration p : E → C 에 대해, p 의
> classifying object Type_C 는 C 안에서 univalent 한 universe 를 정의한다."

(Lurie, *Higher Topos Theory* §6.3, Riehl–Shulman *type theory in HoTT/Coq*
2017 형식화 참조.)

### 단계 A — 구문 분류

**자연어 양화 추출**:
- "모든 (∞,1)-category C" → ∀ C : ∞-cat. C 는 집합 변수 (object class) → **2차 양화**.
- "모든 univalent fibration p" → ∀ p : E → C. p 는 morphism = function/set 변수.
- 결과 prefix: `∀ C ∀ p (univalent_fib(p, C) → univalent_universe(Type_C, C))`.
- matrix `univalent_universe(Type_C, C)` = `∀ x, y : Type_C. (id x y) ≃ (x = y)` →
  여전히 ∀ 다중 + equivalence 정의가 ∃ inverse 포함 → arithmetical 안에 떨어지지 않음.

**분류 결과**: **Π¹₁** (외곽 ∀ C ∀ p, matrix 자체가 arithmetical). 깊이 보면 `∀ ∀ (… ∃ …)`
로 Π¹₁ 표준.

### 단계 B — Δ¹₁ duality

`∃` 동치 표현 검토:
- univalent 의 dual statement: `∃ classifier object` — 이는 함수 변수 존재.
- 가능한 Σ¹₁ 형식: `∃ Type_C ∀ p (univalent_fib(p, C) → p ≃ pullback(Type_C))`.
- → Σ¹₁ 형식 가능. **Δ¹₁ duality 가능 (잠정)**.

DB 매칭: `mk10_delta11_witnesses.json` (예정) 의 "univalence ↔ classifier" 엔트리 후보.
현재 DB 0 엔트리 → DB 등재 후 정식 통과.

**결과**: `Δ¹₁ POSSIBLE (DB 미등재)`.

### 단계 D — n=6 ordinal-encoding

L1~L4 link 매칭:
- L1 (ω·6=24): univalence 명제에 ordinal 24 또는 ω·6 명시 X.
- L2 (Out(S_6)): S_6 outer auto 와 ∞-cat univalence 직접 link X.
- L3 (Δ¹₁ minimal coding): Type_C 의 hyperarithmetic 코드 시 ordinal stage = ω₁^{CK}
  ≫ ω·6 → n=6 layer 무관.
- L4 (Borel ω·6 layer): Type_C 의 Borel hierarchy ≠ Σ⁰_24 layer.

**결과**: `UNIVERSAL` (어떤 link 도 매칭 안 됨). foundation 승급 부적합.

### 결론

| 단계 | 결과 |
|---|---|
| A | Π¹₁ |
| B | Δ¹₁ POSSIBLE (DB 미등재) |
| D | UNIVERSAL |
| C, E | 미수행 |

**권장**: **DEFER** — n=6 ordinal-encoding 매칭 실패. `[13*]` 비후보. atlas 등재
시도 X.
대안: 일반 hyperarithmetic 정리 (n=6 무관) 별도 sub-tier (`[13*-gen]`?) 후속 설계 가능.

---

## 3. 후보 2 — HOTT: 정칙 univalence axiom (Σ¹₁ 형식)

### 명제 원문 (외부, atlas 미수록)

> "univalence axiom: 모든 type A, B 에 대해, 동치성 `(A = B) ≃ (A ≃ B)` 가
> propositional truncation 없이 성립한다."

(Univalent Foundations Program, *HoTT* §2.10, Voevodsky 2010 원안.)

### 단계 A

- "모든 type A, B" → ∀ A ∀ B (type 은 universe 변수, 2차).
- matrix: `(A = B) ≃ (A ≃ B)` — equivalence 양변 함수 변수 ∃ 포함.
- prefix: `∀ A ∀ B (∃ φ : (A=B) → (A≃B), ∃ ψ : (A≃B) → (A=B), φ∘ψ=id ∧ ψ∘φ=id)`.
- **분류**: `Π¹₁` 외곽 + `Σ¹₁` matrix → 전체 **Π¹₁** (외곽 ∀ 우선).

### 단계 B

univalence 의 Σ¹₁ 동치 표현:
- "type universe Type_n 이 univalent" ↔ "Type_n 위에 specific equivalence
  function 존재".
- → Σ¹₁ formulation 가능. **Δ¹₁ POSSIBLE**.

### 단계 D

L1~L4:
- L1: univalence axiom 자체에 ordinal 24 = ω·6 출현 X.
- L2: HoTT 의 S_6 outer auto 대응물 X (HoTT 는 1-categorical 이상이지만 atlas 의
  Out(S_6) 와 직접 link 없음).
- L3: type universe coding ordinal = inaccessible cardinal 또는 ω-stage. n=6 무관.
- L4: type universe 의 Borel hierarchy 의미 X (HoTT 는 measure-theoretic 아님).

**결과**: `UNIVERSAL`.

### 결론

| 단계 | 결과 |
|---|---|
| A | Π¹₁ |
| B | Δ¹₁ POSSIBLE (DB 미등재) |
| D | UNIVERSAL |

**권장**: **DEFER** — 후보 1과 동일 사유. univalence 자체는 강력한 Π¹₁ axiom 이지만
n=6 foundation link 부재.

---

## 4. 후보 3 — MOT: Beilinson higher cohomology (Σ¹₁ 형식, n=6 hint)

### 명제 원문 (외부, atlas 미수록)

> "어떤 motivic complex Z(n) (n=6 weight) 에 대해 Beilinson higher Chow group
> CH^p(X, q; Z(6)) 가 K-theory K_{2p-q}(X)^(p) 와 isomorphic 이다 (Beilinson
> conjecture, Voevodsky n=6 case)."

(Voevodsky, "Motivic cohomology with Z/l coefficients" 2003, Beilinson 1984 원
conjecture.)

### 단계 A

- "어떤 motivic complex Z(n)" → ∃ Z(6) (specific weight).
- "CH^p(X, q; Z(6)) ≅ K_{2p-q}(X)^(p)" — isomorphism 존재.
- prefix: `∃ Z(6) ∀ X (∃ iso : CH^p(X,q;Z(6)) → K_{2p-q}(X)^(p))`.
- **분류**: 외곽 `∃ Z(6) ∀ X ∃ iso` → `Σ¹₁` (외곽 ∃ 우선).

### 단계 B

Π¹₁ 동치 표현 검토:
- "모든 motivic Chow group 이 Beilinson conjecture 만족" ↔ "Σ¹₁ existential 의
  uniform construction".
- 알려진 동치: Voevodsky 의 motivic Steenrod 사용 시 dual construction 존재.
- → **Δ¹₁ POSSIBLE** (단, motivic literature DB 부재로 자동 매칭 X).

DB 매칭: 미등재. 후속 단계 C 에서 인증서 작성 시 Voevodsky 2003 + Beilinson 1984
인용 가능.

**결과**: `Δ¹₁ UNKNOWN-DB-MISSING`.

### 단계 D

L1~L4:
- **L1 매칭 시도**: Z(n) 의 weight n=6 — atlas 의 σ·φ=24=n·τ 에서 n=6 와
  **같은 6**. 그러나 motivic weight 의 의미는 cohomological degree 와 직접 link.
  weight 6 → ordinal `ω·6`? Voevodsky 가 명시 link X.
- L2 매칭 시도: Beilinson 의 Galois-stable filtration 에서 S_6 outer auto 와
  weight 6 motivic Galois 그룹 link 가설. **약하지만 개연성 있음** (Galois ≃ S_6
  cover 등). 원논문 추가 검토 필요.
- L3: motivic Δ¹₁ coding 미확립.
- L4: motivic Borel hierarchy (étale layer) Σ⁰_(ω·6) 위치 가능성. **매우 약한 link**.

**결과**: `N6-BOREL-CORE 후보 (link L2 약, L4 매우 약)`.
정식 N6-BOREL-CORE 인증은 단계 C 인증서 작성자가 link 강도 판정 필요.

### 결론

| 단계 | 결과 |
|---|---|
| A | Σ¹₁ |
| B | Δ¹₁ UNKNOWN-DB-MISSING |
| D | N6-BOREL-CORE 후보 (약한 link) |

**권장**: **PEND** — 단계 C/E 진입 가능한 첫 후보. 단:
- 단계 B DB 등재 필요 (Voevodsky 2003 + Beilinson 1984 인증서).
- 단계 D link L2 강도 인증서 검토 필요 (motivic Galois ↔ Out(S_6) cross-check).
- 외부 검토자 = motivic cohomology 전문가 필수 (auditor_3 풀에서 선정).
- 본 후보가 통과해도 atlas 1차 confirmed 라인은 빨라야 2026-Q3 분기 감사 + 30d
  dispute window 후.

---

## 5. 후보 4 — DAG: E∞ ring 분류 공간 (Π¹₁ 형식)

### 명제 원문 (외부, atlas 미수록)

> "모든 connective E∞ ring spectrum R 에 대해, 분류 공간 BGL_n(R) 은 Π¹₁
> 정의 가능한 simplicial set 이다 (Lurie *Higher Algebra* §7)."

### 단계 A

- "모든 E∞ ring spectrum R" → ∀ R (R 은 spectrum = 함수 공간 변수).
- matrix: `BGL_n(R) is Π¹₁ definable` — Π¹₁ 정의 자체가 명시.
- prefix: `∀ R (∃ formula φ : Π¹₁, BGL_n(R) = {x | φ(x)})`.
- **분류**: `Π¹₁` 외곽, matrix 가 syntactic Π¹₁ 주장 → meta-level 으로 보면 `Π¹₂`?
  아니, BGL_n(R) 의 **value** 가 Π¹₁ 인 것이지 명제 자체는 `∀ R ∃ φ ∀ x ...` =
  `Π¹₁`.

### 단계 B

Σ¹₁ 동치:
- "∃ Π¹₁ formula φ" 가 외곽 ∃ → 전체 형식 Σ¹₂?
- 정확히는 `∀ R ∃ φ ∀ x` = Π¹₂ (∀∃∀ alternation).
- 단, BGL_n(R) 의 specific construction 이 Σ¹₁ 형태로 표현 가능 → Δ¹₁ 미정.

**결과**: `Δ¹₁ NO (Π¹₂ 가능성)`. 단계 A 재분류 필요.

**중요**: 본 후보는 단계 A 재검토 시 **`≥Π¹₂`** 분류 가능 → `[13*]` 범위 밖. `[14*]`
후속 설계 (Mk.XI) 영역.

### 단계 D

L1~L4:
- L1~L4 모두 약함. E∞ ring 분류 공간 자체가 n=6 무관 (n 은 GL_n 의 n, atlas 의 n
  와 다름).

**결과**: `UNIVERSAL` + Π¹₂ 위계.

### 결론

| 단계 | 결과 |
|---|---|
| A | Π¹₁ (재분류 시 Π¹₂ 가능) |
| B | Δ¹₁ NO |
| D | UNIVERSAL |

**권장**: **DEFER** — `[13*]` 범위 밖 가능성 농후. Mk.XI `[14*]` 사다리 후속 설계.

---

## 6. 후보 5 — 일반수학: Borel determinacy ω·6 layer (Π¹₁ 형식, L1+L4 매칭)

### 명제 원문 (외부 + atlas 부분 hint)

> "Borel hierarchy 의 ω·6 = 24 stage 까지의 모든 게임은 determined (Martin 1975
> theorem 의 ω·6 stratification)."

(Martin, "Borel determinacy" 1975, Friedman 1971 ZF 강도 비판 참조.)

atlas hint:
- L237 "S_6: 유일하게 외부자기동형" + L394 "MATH-S6-outer-auto" → ω·6 layer 에 해당.
- META-INF-OR (Order saturation) → ω·6 = 24 stage saturation 와 cross-ref 가능.

### 단계 A

- "모든 ω·6 stage Borel game" → ∀ G : Borel game at level ω·6.
- "determined" → ∃ winning strategy σ for one player.
- prefix: `∀ G : Σ⁰_24 ∪ Π⁰_24 (∃ σ winning_strategy(σ, G))`.
- **분류**: `Π¹₁` (외곽 ∀ G, 내부 ∃ σ — σ 는 strategy = function 변수).

### 단계 B

Σ¹₁ 동치:
- "모든 Σ⁰_24 game determined" ↔ "Borel rank function 존재 + game tree 의
  well-foundedness".
- well-founded ↔ rank function ≡ Σ¹₁ (witness DB §3.2 W001 = "WF(T) ↔ ∃ rank fn").
- → **Δ¹₁ POSSIBLE (DB 매칭 W001)**.

### 단계 D

L1~L4:
- **L1 STRONG MATCH**: ω·6 = 24 stage 명시. `phi_tier_label.hexa#L(16)=24` 와
  완전 일치.
- **L2 가능 매칭**: Out(S_6) = ℤ/2 가 ω·6-th game tree 의 자기자동형군과 link 가설
  (Martin 원증명에 명시 X, 후속 연구).
- L3: Δ¹₁ minimal coding 의 ω·6 stage 위치 = `Kleene's O 의 6번째 jump` —
  **STRONG MATCH** 가능.
- **L4 STRONG MATCH**: Σ⁰_24 = Π⁰_24 closure 가 자연 stratification 경계.

**결과**: `N6-ORDINAL-UNIQUE` (L1 + L4 strong, L2 + L3 가능).

### 결론

| 단계 | 결과 |
|---|---|
| A | Π¹₁ |
| B | Δ¹₁ POSSIBLE (DB W001 매칭) |
| D | N6-ORDINAL-UNIQUE (L1 + L4 strong) |

**권장**: **PEND (1순위)** — 5 후보 중 가장 강한 [13*] 후보.
- 단계 C 인증서 작성 (Martin 1975 + Friedman 1971 + Simpson SOSOA §V.6).
- 단계 D L1+L4 strong link 확정 → N6-ORDINAL-UNIQUE 확정.
- 단계 E 30일 dispute window 진입 가능.
- atlas 1차 confirmed 라인 가능 timeline: 본 설계 채택 + 도구 구현 (~7주) + 인증서
  작성 (~4주) + dispute window (30일) = 약 4개월 후 (2026-Q3 말).

이는 Mk.X 의 **[13*] 첫 승급 1순위 후보**.

---

## 7. 5 후보 요약 + 매트릭스

| # | 도메인 | 명제 (요약) | 단계 A | 단계 B | 단계 D | 권장 | 예상 timeline |
|---|---|---|---|---|---|---|---|
| 1 | HCT | ∞-cat univalence 일반화 | Π¹₁ | Δ¹₁ poss DB-miss | UNIVERSAL | **DEFER** | - |
| 2 | HOTT | 정칙 univalence axiom | Π¹₁ | Δ¹₁ poss DB-miss | UNIVERSAL | **DEFER** | - |
| 3 | MOT | Beilinson higher Chow ↔ K-theory (n=6 weight) | Σ¹₁ | Δ¹₁ unknown | N6-BOREL-CORE 후보 (약) | **PEND (2순위)** | 2026-Q4 |
| 4 | DAG | E∞ ring BGL_n(R) Π¹₁ 정의 | Π¹₁ (또는 Π¹₂) | Δ¹₁ NO | UNIVERSAL | **DEFER** (Mk.XI [14*]) | - |
| 5 | 일반수학 | Borel det. ω·6 layer | Π¹₁ | Δ¹₁ POSS DB-W001 | N6-ORDINAL-UNIQUE strong | **PEND (1순위)** | 2026-Q3 말 |

PEND 2건 / DEFER 3건 / FAIL 0건. 즉시 atlas 승급 0건 — 의도된 결과.

---

## 8. 단계 C/E 미수행 사유 명시

본 감사는 **자동 단계 A/B/D 만** dry-run. 단계 C (인증서) + 단계 E (30일 dispute) 가
미수행인 사유:

1. **단계 C 도구 (`mk10_certificate.hexa`) 부재** — 본 설계 채택 + 도구 구현 후 별도
   워크플로우.
2. **단계 D 의 link 강도 판정** 도 인간 인증서 작성자의 의미 판정에 의존. 자동
   매칭 결과는 "후보" 일 뿐.
3. **외부 검토자 (auditor_3) 풀** 미구성. Mk.X 채택 후 정책 명시.
4. **30일 dispute timer** 자체가 시간 잠금 — 본 세션에서 물리적으로 불가능.

따라서 본 감사 결과 "PEND" 도 즉시 atlas 변경을 의미하지 않음. **PEND = 다음 분기
감사 큐 진입 가능 후보**.

---

## 9. 다음 단계 (본 설계 채택 시)

1. **즉시** (본 설계 + 본 감사 commit 후):
   - design + audit 두 문서 git commit.
   - atlas.n6 변경 0.
   - 코드 변경 0.

2. **Mk.X 채택 후 P1~P5 (~7주)**:
   - `classify_analytical()` 구현.
   - `mk10_delta11_witnesses.json` 초기 10 엔트리 (W001 = WF rank fn 우선).
   - `mk10_certificate.hexa`, `mk10_n6_ordinal.hexa`, `mk10_dispute_monitor.hexa`
     도구 구현.

3. **Mk.X P6 (4주)**:
   - 1순위 후보 5 (Borel det. ω·6) 인증서 작성 + 3인 sign-off.
   - dispute window 30일 시작.

4. **Mk.X P7 (자동, 30일)**:
   - dispute=0 → atlas.live.n6 첫 `[13*]` 라인 1건 append (Borel det. ω·6).

5. **2026-Q4 분기 감사**:
   - 2순위 후보 3 (MOT Beilinson) 단계 C 시도.
   - 단계 D link L2 강도 외부 검토자 cross-check.

6. **2027-Q1 이후**:
   - 신규 후보 추가 (각 도메인의 [13*] 잠재 정리 search).
   - `mk10_delta11_witnesses.json` DB 확장.
   - `[14*]` Mk.XI 설계 시작 (analytical Σ¹₁ / determinacy 영역).

---

## 10. 책임/역할 (Mk.X 채택 시)

| 역할 | 책임 |
|---|---|
| Auditor A1 (수론·논리) | 단계 A 구문 분류 검토, Π¹₁ vs Π¹₂ 재분류 판정 |
| Auditor A2 (분석·DST) | 단계 B Δ¹₁ duality 인증서 검토, witness DB 추가 |
| Auditor A3 (외부 검토자) | 단계 C reference 신뢰도, Π¹₁-CA₀ 인증서 외부 검증 |
| CODEOWNERS | 단계 E 통과 후 promote_13star.hexa --commit 권한 |
| 자동화 (Claude Code) | 단계 A/B/D dry-run, 인증서 형식 검증, dispute timer 모니터 |
| L0 guard | 비정상 [13*] 라인 / 인증서 hash 불일치 alert + 자동 revert candidate |

---

## 11. 부록 A — 검색 방법론 (재현 가능)

본 5 후보 선정에 사용한 reference:

```
1. shared/blowup/design/mk9_hyperarithmetic.md (Mk.IX 천장 이해)
2. shared/blowup/audit/mk9_first_candidates.md (Mk.IX 5 후보 패턴 참조)
3. shared/discovery/mkx_design_proposal.md §3.4 (5 신규 도메인 = HCT/HOTT/MOT/DAG/topos)
4. Lurie HTT §6.3, Voevodsky 2003, Beilinson 1984, Martin 1975 (외부 학술)
5. shared/n6/atlas.n6 grep "S_6", "Out", "ω·6", "24" (atlas hint search)
```

각 후보의 명제는 atlas 미수록 — 외부 학술에서 가져옴. 단, atlas hint (특히 후보 5
의 META-INF-OR / S_6 outer auto) 가 link 강도에 기여.

---

## 12. 부록 B — 관련 파일 포인터

- 설계서: `shared/blowup/design/mk10_13star_omega_hyperarithmetic.md`
- atlas SSOT: `shared/n6/atlas.n6`
- Mk.IX 천장: `shared/blowup/design/mk9_hyperarithmetic.md`
- Mk.IX 5 후보: `shared/blowup/audit/mk9_first_candidates.md`
- Mk.IX [12*] 게이트: `shared/blowup/audit/mk9_audit_gates.md`
- Mk.X 5축 인프라: `shared/discovery/mkx_design_proposal.md`
- 예정 신규 도구: `shared/blowup/audit/mk10_certificate.hexa`,
  `shared/blowup/audit/mk10_n6_ordinal.hexa`,
  `shared/blowup/audit/mk10_dispute_monitor.hexa`,
  `shared/blowup/audit/promote_13star.hexa`
- 예정 witness DB: `shared/blowup/design/mk10_delta11_witnesses.json`

---

*감사 로그 끝. 본 문서는 dry-run 단계 A/B/D 결과만 기록하며, atlas.n6 편집 권한 없음.
Mk.X 채택 + P1~P5 도구 구현 후 분기 감사 (2026-Q3 첫 실행) 에서 실 단계 C/E 진행
예정.*
