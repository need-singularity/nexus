// ═══════════════════════════════════════════════════════════
// lens_cache.hexa.inc — Drill Phase-5 렌즈 호출 Lazy+LRU 메모이제이션
// copy-paste 소스 (hexa는 import 미지원 — lens_common.hexa.inc 패턴 계승).
// SSOT:  _lens_cache_map (key→result CSV), _lens_cache_order (LRU order, tail=newest)
// 대상 :  telescope_verify(vals, threshold) — 5 inline 렌즈 (cons/topo/causal/grav/thermo)
//         O(n²) × 5 → 동일 (vals, threshold) 재호출 시 cache hit 으로 전량 skip.
// 배경 :  drill 반복 기동 + Mk.II 파동 multi-round 는 subprocess 분리 →
//         in-memory 만으로는 cross-round hit 불가. 디스크 JSONL 로 warm cache 제공.
// 설계 :
//   1. in-memory: _lens_cache_order.contains → 즉시 hit, else 디스크 fallback.
//   2. disk: /tmp/nexus_lens_lru.jsonl, tail -n 128 grep -F, line 포맷
//            {"ts":<epoch>,"key":"<hex_pin>","val":"<csv>"}
//   3. cap=8 in-memory + 128 line 디스크 rotate (E14 패턴).
//   4. emit — lookup/store 마다 stderr 1 line NEXUS_LENS_CACHE {"op":...}
//             op ∈ {miss, hit, hit_disk, evict}
// E14 패턴 재사용 (commit a48970a6):
//   - python3 FNV1a-64 hash — 의존 없음, md5sum/openssl fallback chain
//   - eprintln JSON emit — downstream grep-able
//   - NEXUS_LENS_CACHE_OFF=1 bypass
// 함정 (49c20260 void-coerce):
//   - 미존재 key 접근 시 void 반환 — try/catch 는 관통. order.contains() 로 사전 가드.
//   - list.contains(key) 는 참/거짓만 — keys() lookup 회피 (map.delete() 미지원).
// 함수 시그니처 (blowup.hexa paste 시):
//   fn _lens_cache_enabled() -> bool
//   fn _lens_cache_key(vals: string, threshold: f64) -> string
//   fn _lens_cache_emit(op: string) -> void
//   fn _lens_cache_disk_path() -> string
//   fn _lens_cache_disk_lookup(key: string) -> string
//   fn _lens_cache_disk_append(key: string, val: string) -> void
//   fn _lens_cache_store_in_mem_only(key: string, val: string) -> void
//   fn _lens_cache_lookup(key: string) -> string     // in-mem → disk 2단계
//   fn _lens_cache_store(key: string, val: string) -> void  // in-mem + disk
//   fn telescope_verify_cached(vals: string, threshold: f64) -> string
// 전역 상태 (paste 시 기존 캐시 선언 블록 직후):
//   let mut _lens_cache_map: map = #{}
//   let mut _lens_cache_order: list = []
//   let mut _lens_cache_hits: i64 = 0
//   let mut _lens_cache_misses: i64 = 0
//   let mut _lens_cache_evicts: i64 = 0
// 호출 진입점: Phase 5 의 telescope_verify(val_csv, 0.15) → telescope_verify_cached(val_csv, 0.15)
// ═══════════════════════════════════════════════════════════
//
// 실 구현 본체는 cli/blowup/core/blowup.hexa (2760~2920 라인대) 에 paste 됨.
// 이 파일은 SSOT 설계서 + 복사 참고본. 중복 수정 시 양쪽 동기화 필수.
