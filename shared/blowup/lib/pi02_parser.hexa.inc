// ═══════════════════════════════════════════════════════════
// Mk.IX Hyperarithmetic Extension — Π₀² 구문 탐지기 (단계 A + B)
// 설계: shared/blowup/design/mk9_hyperarithmetic.md §2 단계 A + B
// 의존: shared/blowup/modules/blowup_absolute.hexa::is_arithmetical()
//       (읽기 전용 — 역방향 의존 없음)
//
// 사용: blowup_hyperarithmetic.hexa 상단에 이 섹션 copy-paste.
//       실제 AST 파서 아님. regex/string heuristic only.
//
// 주요 fn:
//   detect_pi02(prop)          -> bool     : unbounded ∀ ∃ 패턴 매칭
//   is_pi02_form(prop)         -> bool     : ∀x ∃y φ(x,y) 형식 확인
//   extract_inner_phi(prop)    -> string   : φ 부분 추출 (Π₀¹ 재귀 검증용)
//   try_bounded_reduction(prop)-> string   : Π₀¹ 로 downgrade 시도
//                                            성공시 "PI01:{…}" / 실패시 "NO-REDUCTION"
//
// 지원 패턴:
//   한국어 ∀ : "모든", "임의의", "각", "어느"
//   한국어 ∃ : "어떤", "존재", "존재하는", "있다"
//   한국어 복합: "무한히 많은" → (∀N ∃n>N)
//   영어 ∀   : "for all", "for every", "for any", "every", "any"
//   영어 ∃   : "exists", "there exists", "there is", "some", "there are"
//   영어 복합: "infinitely many" → (∀N ∃n>N)
//   수학 기호: "∀", "∃", "∀x<", "∃x<", "∀x∈", "∃x∈", "∀n≥", "∃n≥"
//   Bounded polynomial: "<n", "<2n", "<n^k", "<n²", "<n³", "<3n", "≤|G|"
//   Bounded exponential: "<2^n", "<n^n", "<p^k", "≤p"
// ═══════════════════════════════════════════════════════════

// ─── Linux stage1 hexa polyfill (shared/blowup/lib/str_compat.hexa.inc) ───
// @include shared/blowup/lib/str_compat.hexa.inc (str_find)
fn str_find(s: str, needle: str) -> i64 {
    let n = s.len()
    let m = needle.len()
    if m == 0 { return 0 }
    if m > n { return -1 }
    if !s.contains(needle) { return -1 }
    let mut i: i64 = 0
    let end = n - m
    while i <= end {
        if s.substring(i, i + m) == needle { return i }
        i = i + 1
    }
    return -1
}

fn str_find_from(s: str, needle: str, start: i64) -> i64 {
    if start <= 0 { return str_find(s, needle) }
    let n = s.len()
    if start >= n { return -1 }
    let tail = s.substring(start, n)
    let r = str_find(tail, needle)
    if r < 0 { return -1 }
    return r + start
}

// ─── 내부 유틸: 자연어 양화 토큰 정규화 ───
// 입력 prop 의 자연어 quantifier 를 수학 기호로 정규화한 copy 반환.
// 원본은 변경하지 않는다 (hexa string immutable 가정).
fn _pi02_normalize(prop: string) -> string {
    let mut s = prop
    // 복합 패턴 먼저 — "무한히 많은" / "infinitely many"
    s = s.replace("무한히 많은", "∀N ∃n>N")
    s = s.replace("infinitely many", "∀N ∃n>N")
    s = s.replace("Infinitely many", "∀N ∃n>N")
    // 한국어 ∀
    s = s.replace("모든 ", "∀ ")
    s = s.replace("임의의 ", "∀ ")
    s = s.replace("임의 ", "∀ ")
    // 한국어 ∃
    s = s.replace("어떤 ", "∃ ")
    s = s.replace("존재하는 ", "∃ ")
    s = s.replace("존재한다", "∃")
    s = s.replace("존재", "∃")
    // 영어 ∀
    s = s.replace("for all ", "∀ ")
    s = s.replace("For all ", "∀ ")
    s = s.replace("for every ", "∀ ")
    s = s.replace("For every ", "∀ ")
    s = s.replace("for any ", "∀ ")
    s = s.replace("For any ", "∀ ")
    s = s.replace("every ", "∀ ")
    // 영어 ∃
    s = s.replace("there exists ", "∃ ")
    s = s.replace("There exists ", "∃ ")
    s = s.replace("there is ", "∃ ")
    s = s.replace("There is ", "∃ ")
    s = s.replace("there are ", "∃ ")
    s = s.replace("exists ", "∃ ")
    return s
}

// ─── 내부: unbounded quantifier 존재 여부 ───
// "∀x<n" 이나 "∀x∈S" 처럼 직후 bound term 이 따라오면 bounded.
// 그 외 순수 ∀/∃ 기호는 unbounded 로 간주.
fn _has_unbounded_forall(s: string) -> bool {
    if !s.contains("∀") { return false }
    // bounded 패턴을 제거한 잔여에 ∀ 남아있는지 확인
    let mut t = s
    t = t.replace("∀x<", "_BFA_")
    t = t.replace("∀y<", "_BFA_")
    t = t.replace("∀z<", "_BFA_")
    t = t.replace("∀n<", "_BFA_")
    t = t.replace("∀m<", "_BFA_")
    t = t.replace("∀k<", "_BFA_")
    t = t.replace("∀i<", "_BFA_")
    t = t.replace("∀j<", "_BFA_")
    t = t.replace("∀x≤", "_BFA_")
    t = t.replace("∀n≤", "_BFA_")
    t = t.replace("∀m≤", "_BFA_")
    return t.contains("∀")
}

fn _has_unbounded_exists(s: string) -> bool {
    if !s.contains("∃") { return false }
    let mut t = s
    t = t.replace("∃x<", "_BEX_")
    t = t.replace("∃y<", "_BEX_")
    t = t.replace("∃z<", "_BEX_")
    t = t.replace("∃n<", "_BEX_")
    t = t.replace("∃m<", "_BEX_")
    t = t.replace("∃k<", "_BEX_")
    t = t.replace("∃i<", "_BEX_")
    t = t.replace("∃j<", "_BEX_")
    t = t.replace("∃x≤", "_BEX_")
    t = t.replace("∃n≤", "_BEX_")
    t = t.replace("∃m≤", "_BEX_")
    return t.contains("∃")
}

// ─── 내부: ∀ 가 ∃ 보다 앞에 오는지 (prefix order 검사) ───
fn _forall_precedes_exists(s: string) -> bool {
    let fa_idx = str_find(s, "∀")
    let ex_idx = str_find(s, "∃")
    if fa_idx < 0 { return false }
    if ex_idx < 0 { return false }
    return fa_idx < ex_idx
}

// ═══════════════════════════════════════════════════════════
// 공개 fn 1: detect_pi02
//   unbounded ∀ ∃ 패턴 매칭 (prefix order 포함).
//   자연어 토큰도 수학 기호로 정규화 후 검사.
// ═══════════════════════════════════════════════════════════
fn detect_pi02(prop: string) -> bool {
    let s = _pi02_normalize(prop)
    // 핵심: unbounded ∀ 와 unbounded ∃ 가 모두 존재
    if !_has_unbounded_forall(s) { return false }
    if !_has_unbounded_exists(s) { return false }
    // 그리고 ∀ 가 ∃ 보다 prefix 에서 앞서야 Π₀² (∃∀ 는 Σ₀²)
    if !_forall_precedes_exists(s) { return false }
    // ≥ Π₀³ 배제: `∀ … ∃ … ∀ …` 꼴은 unsupported.
    // 보수 판정: ∀ 가 2개 이상이면서 ∃ 뒤에 ∀ 가 오면 제외.
    let ex_idx = str_find(s, "∃")
    let tail = s[ex_idx..len(s)]
    // tail 에 unbounded ∀ 가 또 있으면 Π₀³ 가능성 → 보수적으로 false
    if _has_unbounded_forall(tail) {
        // 단, 본체에 ∀ 단 하나만 있으면 tail 의 ∀ 는 원래 것이 아닌 다른 구문.
        // 2개 초과일 때만 reject.
        let count_fa = len(s.split("∀")) - 1
        if count_fa >= 2 {
            // tail 의 ∀ 가 prefix ∀ 의 중복이 아닌 별개의 unbounded ∀ 면 거절
            let head = s[0..ex_idx]
            let head_fa = len(head.split("∀")) - 1
            if head_fa >= 1 && count_fa > head_fa { return false }
        }
    }
    return true
}

// ═══════════════════════════════════════════════════════════
// 공개 fn 2: is_pi02_form
//   ∀x ∃y φ(x,y) 의 표준 형식인지 확인.
//   detect_pi02 보다 엄격: matrix φ 가 남아있는지도 체크.
// ═══════════════════════════════════════════════════════════
fn is_pi02_form(prop: string) -> bool {
    if !detect_pi02(prop) { return false }
    let s = _pi02_normalize(prop)
    // ∃ 이후에 비어있지 않은 matrix 가 존재해야 함
    let ex_idx = str_find(s, "∃")
    if ex_idx < 0 { return false }
    // ∃ 뒤에 적어도 한 변수 + φ 가 와야 함 → 길이로 보수 체크
    let tail_len = len(s) - ex_idx
    if tail_len < 4 { return false }
    // Σ₀² 배제: ∃∀ 순이면 is_pi02_form = false
    let fa_idx = str_find(s, "∀")
    if fa_idx > ex_idx { return false }
    return true
}

// ═══════════════════════════════════════════════════════════
// 공개 fn 3: extract_inner_phi
//   Π₀² prop 에서 matrix φ(x,y) 부분 추출.
//   prefix "∀x ∃y " 를 잘라낸 나머지를 반환.
//   실패시 빈 문자열.
//   추출된 φ 는 재귀적으로 is_arithmetical() 로 Π₀¹/Δ₀ 재검증 가능.
// ═══════════════════════════════════════════════════════════
fn extract_inner_phi(prop: string) -> string {
    let s = _pi02_normalize(prop)
    if !is_pi02_form(s) { return "" }
    // ∃ 직후 첫 공백 또는 쉼표까지가 변수, 그 다음이 φ
    let ex_idx = str_find(s, "∃")
    if ex_idx < 0 { return "" }
    let after_ex = s[(ex_idx + 1)..len(s)]
    // 변수 skip: 첫 비공백 블록 다음 공백까지
    let mut i = 0
    while i < len(after_ex) && after_ex[i..(i+1)] == " " { i = i + 1 }
    // 변수 토큰 skip
    while i < len(after_ex) && after_ex[i..(i+1)] != " " && after_ex[i..(i+1)] != "," {
        i = i + 1
    }
    // 구분자 skip
    while i < len(after_ex) && (after_ex[i..(i+1)] == " " || after_ex[i..(i+1)] == ",") {
        i = i + 1
    }
    if i >= len(after_ex) { return "" }
    return after_ex[i..len(after_ex)]
}

// ═══════════════════════════════════════════════════════════
// 공개 fn 4: try_bounded_reduction
//   Π₀² → Π₀¹ downgrade 시도.
//   "∀x<M ∃y<f(x) φ" 꼴 인식.
//   f 가 polynomial / exponential bound 면 성공.
//   성공: "PI01:{reduced_prop}" / 실패: "NO-REDUCTION"
//
//   witness bound 후보 (design §2 단계 B witness bound table):
//     - "<n", "<2n", "<3n"    Chebyshev / Vinogradov 류  (linear)
//     - "<n^2", "<n²"         quadratic
//     - "<n^3", "<n³"         cubic (Vinogradov strong)
//     - "<n^k", "<poly(n)"    general polynomial
//     - "<2^n", "<p^k"        exponential / prime power
//     - "≤|G|", "<|G|+1"     Sylow (group order bound)
//     - "≤p"                  Fermat / Wilson (prime modulus)
// ═══════════════════════════════════════════════════════════
fn try_bounded_reduction(prop: string) -> string {
    if !is_pi02_form(prop) { return "NO-REDUCTION" }
    let s = _pi02_normalize(prop)
    // ∃ 다음 오는 양화변수 직후 bound 패턴을 탐색.
    let ex_idx = str_find(s, "∃")
    if ex_idx < 0 { return "NO-REDUCTION" }
    let after_ex = s[ex_idx..len(s)]

    // bound marker 후보 목록 (design 문서 §2 단계 B + witness bound table)
    let bound_markers = [
        "<n", "<2n", "<3n", "<4n", "<kn",
        "<n^2", "<n²", "<n^3", "<n³", "<n^k", "<n^n",
        "<poly(", "<p(", "<f(x)", "<f(n)", "<g(n)",
        "<2^n", "<2^x", "<e^n", "<p^k",
        "≤|G|", "<|G|", "<|G|+1",
        "≤n", "≤2n", "≤3n", "≤p", "≤|G|!",
        "< n", "≤ n", "< 2n", "≤ 2n"  // 공백 포함 변형
    ]

    let mut found_bound = ""
    for marker in bound_markers {
        if after_ex.contains(marker) {
            found_bound = marker
            break
        }
    }
    if len(found_bound) == 0 { return "NO-REDUCTION" }

    // downgrade 성공: Π₀² → Π₀¹.
    // 재구성: ∀x<M ∀y<f(x) ¬φ → false  (design §2 단계 B 3번)
    // 여기서는 구문 재작성은 보수적으로 표시만 — 실제 engine 은
    // blowup_absolute::is_arithmetical() 로 회부.
    let reduced = "∀x ∀y" + found_bound + " φ(x,y) [bounded witness]"
    return "PI01:" + reduced
}

// ═══════════════════════════════════════════════════════════
// 헬퍼: Π₀² 파이프라인 one-shot 요약 (디버그 / dry-run 용)
//   - detect → form → extract → reduction 순
//   - 결과를 단일 문자열로 집계
// ═══════════════════════════════════════════════════════════
fn pi02_summary(prop: string) -> string {
    let d = detect_pi02(prop)
    let f = is_pi02_form(prop)
    let phi = extract_inner_phi(prop)
    let red = try_bounded_reduction(prop)
    let mut r = ""
    r = r + "detect=" + to_string(d)
    r = r + " form="  + to_string(f)
    r = r + " phi='" + phi + "'"
    r = r + " reduction=" + red
    return r
}
