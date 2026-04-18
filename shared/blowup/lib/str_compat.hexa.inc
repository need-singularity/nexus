// ═══════════════════════════════════════════════════════════
// str_compat.hexa.inc — Linux stage1 hexa string API polyfill
//
// 목적: Linux stage1 hexa 는 native Mac hexa 와 달리 `str.find()`/`str.slice()`
//       미지원. drill 실행 시 .find() 호출이 무한 에러 루프 → OOM kill.
// 해결: substring/contains 기반 polyfill 로 Mac/Linux 양립 구현.
//
// 지원 API (확인됨):
//   len, contains, starts_with, ends_with, substring(a,b), s[i] (char), == 문자열 비교
//
// 사용: hexa 는 import/include 미지원 — 각 콜사이트 파일 상단에 직접 copy-paste.
//
// 제공 fn:
//   str_find(s, needle)          -> i64  : needle 의 첫 출현 idx, 없으면 -1
//   str_find_from(s, needle, st) -> i64  : start offset 부터 탐색
// ═══════════════════════════════════════════════════════════

// str_find: substring-based polyfill, Mac/Linux 양립
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

// str_find_from: start offset 지원
fn str_find_from(s: str, needle: str, start: i64) -> i64 {
    if start <= 0 { return str_find(s, needle) }
    let n = s.len()
    if start >= n { return -1 }
    let tail = s.substring(start, n)
    let r = str_find(tail, needle)
    if r < 0 { return -1 }
    return r + start
}
