// ═══════════════════════════════════════════════════════════
// argv — 런타임 편차 (Mac/Linux stage1) 흡수용 공용 헬퍼
// 2026-04-19  NEXUS-6 entry.hexa argv 오프셋 버그 체계적 해결
//
// 배경:
//   hexa 인터프리터 build 경로에 따라 args() 반환 prefix 길이가 다름:
//     Mac  (hexa native)   : [hexa-bin, script.hexa, user1, user2, ...]  (prefix=2)
//     Linux (stage1 hexa)  : [hexa-bin, "run", script.hexa, user1, ...]  (prefix=3)
//   즉 Linux 에서 argv[2] 를 "첫 user arg" 로 가정한 코드는 실제로는
//   `script.hexa` (path) 를 집어서 심각한 오인 분기.
//
//   이 헬퍼는 argv 를 스캔해 `.hexa` 로 끝나는 최초 토큰을 script path
//   자리로 간주하고, 그 다음부터를 user arg 로 slice 하여 plaform 편차를
//   0 으로 흡수.  "run" / "eval" / "-e" 등 Linux stage1 의 subcommand 가
//   script path 앞에 더 추가되더라도 .hexa 앵커로 자동 정렬.
//
// 사용법:
//   // (1) 모듈 상단에 복사 붙여넣기 (hexa 미지원 import 우회).
//   // (2) 기존 argv 오프셋 대신 user_arg* 사용.
//   let mode = user_arg(0)                      // 이전의 argv[2] 에 해당
//   let target = user_arg(1)                    // 이전의 argv[3] 에 해당
//   if user_arg_count() >= 2 { ... }            // 이전의 argv.len() >= 4
//   let all = user_args()                       // user args only
//
// 설계:
//   * pure — I/O/exec 없음.  import 하지 않아도 카피만으로 작동.
//   * fail-soft — .hexa 앵커 못 찾으면 fallback:
//       len(argv) >= 3 && argv[1] in ["run","eval"] → prefix 3
//       else → prefix 2 (Mac 규약)
//   * 빈 접근 안전 — out-of-range 는 빈 문자열 반환.
// ═══════════════════════════════════════════════════════════

// 내부: script path 의 argv index.  못 찾으면 -1.
fn _argv_script_idx() -> i64 {
    let a = args()
    let n = a.len()
    let mut i: i64 = 0
    while i < n {
        let s = to_string(a[i])
        if s.ends_with(".hexa") { return i }
        i = i + 1
    }
    return -1
}

// 내부: 첫 user arg 의 argv index (prefix length).
// .hexa 앵커 우선, fallback 은 stage1 vs native 추정.
fn _argv_user_start() -> i64 {
    let idx = _argv_script_idx()
    if idx >= 0 { return idx + 1 }
    // fallback: stage1 "run" / "eval" subcommand 감지
    let a = args()
    if a.len() >= 3 {
        let sub = to_string(a[1])
        if sub == "run" { return 3 }
        if sub == "eval" { return 3 }
        if sub == "-e" { return 3 }
    }
    // Mac native 규약
    return 2
}

// user args 전체 (argv 에서 user 인자만 slice).
fn user_args() -> list {
    let a = args()
    let start = _argv_user_start()
    let n = a.len()
    if start >= n { return [] }
    return a[start..n]
}

// user arg 개수 (음수 없이 안전).
fn user_arg_count() -> i64 {
    let a = args()
    let start = _argv_user_start()
    let n = a.len()
    if start >= n { return 0 }
    return n - start
}

// i 번째 user arg.  out-of-range → "".
fn user_arg(i: i64) -> string {
    let a = args()
    let start = _argv_user_start()
    let n = a.len()
    let pos = start + i
    if pos < 0 { return "" }
    if pos >= n { return "" }
    return to_string(a[pos])
}

// i 번째 user arg (fallback 지정).  out-of-range → fb.
fn user_arg_or(i: i64, fb: string) -> string {
    let a = args()
    let start = _argv_user_start()
    let n = a.len()
    let pos = start + i
    if pos < 0 { return fb }
    if pos >= n { return fb }
    return to_string(a[pos])
}
