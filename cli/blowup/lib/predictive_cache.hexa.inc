// ═══════════════════════════════════════════════════════════
// predictive_cache.hexa.inc — AV: atlas predictive cache (bigram)
//
// 목적: AL hot-shard RAM promote 는 access count 로 사후 반응.
//       AV 는 WILL-be-accessed 를 예측 → 라운드 사이 idle window 에
//       bucket prefix 를 미리 올려놓아 next-round cold miss 제거.
//
// 알고리즘 (pure n-gram, ML 없음):
//   1. _predict_record_query(prefix)  — round 내 모든 bucket query 기록
//      - 최근 K 개 이력 유지 (deque-like, 앞쪽 drop)
//      - bigram: (prev → next) 카운트 1 증가
//   2. _predict_warm_next_round(recent) — top-N next prefix 반환
//      - recent tail (last prefix) 기준 bigram lookup
//      - 없으면 전역 빈도 top-N fallback
//   3. _predict_warm_buckets(prefixes)  — 미리 bucket→list resolve (cache warmup)
//   4. _predict_hit_count(predicted, actual) — 교집합 count (hit-rate 측정)
//
// Bigram 저장: flat map (nested map 은 hexa pitfall 기록됨 — 797@blowup.hexa 참조)
//   _predict_bigram_cnt["<prev>\x1e<next>"] = count       (string 카운터)
//   _predict_unigram_cnt["<prefix>"]        = count
//   _predict_pairs_by_prev["<prev>"]        = "next1|next2|..."  (prev 별 known-nexts)
//
// 상수:
//   _PRED_K        = 100   (history window)
//   _PRED_TOP_N    = 5     (preload 개수)
//
// 제약:
//   - hexa parse clean (>=/<= 금지)
//   - pure count, no ML
//   - side-effect free except state mutation + cache warm resolve
// ═══════════════════════════════════════════════════════════

let _PRED_K: i64 = 100
let _PRED_TOP_N: i64 = 5
let _PRED_SEP: string = "|"       // bigram list separator
let _PRED_KSEP: string = "\x1e"   // ASCII record-separator for pair key

let mut _predict_history: list = []           // last K prefixes (oldest → newest)
let mut _predict_bigram_cnt: map = #{}        // "prev<sep>next" → count
let mut _predict_unigram_cnt: map = #{}       // "prefix" → count
let mut _predict_pairs_by_prev: map = #{}     // "prev" → "next1|next2|..."

// AI-native: bucket prefix 추출 — 값(f64)|문자열(str) 양쪽 대응
//   numeric seed → to_string(to_int(v))  (n6_bucket key 와 동일 규칙)
//   string seed  → first dot-segment 또는 전체
fn _predict_prefix_of_value(v: f64) -> string {
    return to_string(to_int(v))
}

fn _predict_prefix_of_string(s: string) -> string {
    let t = s.trim()
    if len(t) == 0 { return "" }
    // dot-seperated prefix 가 있으면 첫 세그먼트, 아니면 원본
    if t.contains(".") {
        let parts = t.split(".")
        if len(parts) > 0 { return parts[0] }
    }
    return t
}

// 단일 map 증가 헬퍼 (missing-key → 1, 존재 → +1)
fn _predict_bump_cnt(m: map, key: string) -> map {
    let mut cur: i64 = 0
    try { cur = to_int(m[key]) } catch e {}
    let nxt = cur + 1
    m[key] = to_string(nxt)
    return m
}

// prev 별 known-nexts 리스트에 next 추가 (중복 없이)
fn _predict_append_next_if_new(prev: string, next: string) {
    let mut cur = ""
    try { cur = _predict_pairs_by_prev[prev] } catch e {}
    if cur == "" {
        _predict_pairs_by_prev[prev] = next
        return
    }
    // 중복 체크 — "|next|" 또는 "^next|" 또는 "|next$" 또는 "==next"
    let tokens = cur.split(_PRED_SEP)
    let mut ti: i64 = 0
    while ti < len(tokens) {
        if tokens[ti] == next { return }
        ti = ti + 1
    }
    _predict_pairs_by_prev[prev] = cur + _PRED_SEP + next
}

// ─── public API: record a query (called per atlas bucket access) ───
fn _predict_record_query(prefix: string) {
    if len(prefix) == 0 { return }
    // unigram
    _predict_unigram_cnt = _predict_bump_cnt(_predict_unigram_cnt, prefix)
    // bigram (이전 prefix 가 있는 경우)
    let hlen = len(_predict_history)
    if hlen > 0 {
        let prev = to_string(_predict_history[hlen - 1])
        if len(prev) > 0 {
            let key = prev + _PRED_KSEP + prefix
            _predict_bigram_cnt = _predict_bump_cnt(_predict_bigram_cnt, key)
            _predict_append_next_if_new(prev, prefix)
        }
    }
    // history push (K window 유지)
    _predict_history = _predict_history.push(prefix)
    // trim (deque drop-oldest) — len > K 이면 첫 요소 제거
    let new_len = len(_predict_history)
    if new_len > _PRED_K {
        let mut trimmed: list = []
        let drop_n = new_len - _PRED_K
        let mut ti: i64 = drop_n
        while ti < new_len {
            trimmed = trimmed.push(_predict_history[ti])
            ti = ti + 1
        }
        _predict_history = trimmed
    }
}

// ─── public API: pick top-N predicted next prefixes ───
//   입력: recent_queries (tail 이 최신). 마지막 prefix 기준 bigram lookup.
//   fallback: bigram miss → 전역 unigram top-N.
//   bigram 후보도 N 미달이면 unigram 으로 보충 (dedup).
fn _predict_warm_next_round(recent_queries: list) -> list {
    let mut picked: list = []
    let mut seen: map = #{}

    // 1) bigram lookup
    let rlen = len(recent_queries)
    if rlen > 0 {
        let last = to_string(recent_queries[rlen - 1])
        let mut nexts_raw = ""
        try { nexts_raw = _predict_pairs_by_prev[last] } catch e {}
        if nexts_raw != "" {
            let cands = nexts_raw.split(_PRED_SEP)
            // score → sort: hexa 에 정렬 builtin 가정 없음 → O(N^2) selection sort (small N)
            let mut scored_key: list = []
            let mut scored_val: list = []
            let mut ci: i64 = 0
            while ci < len(cands) {
                let nk = cands[ci]
                let bkey = last + _PRED_KSEP + nk
                let mut cnt: i64 = 0
                try { cnt = to_int(_predict_bigram_cnt[bkey]) } catch e {}
                scored_key = scored_key.push(nk)
                scored_val = scored_val.push(cnt)
                ci = ci + 1
            }
            // selection sort: pick top-N by val desc
            let total = len(scored_key)
            let mut filled: i64 = 0
            while filled < _PRED_TOP_N && filled < total {
                let mut best_idx: i64 = -1
                let mut best_val: i64 = -1
                let mut si: i64 = 0
                while si < total {
                    let v: i64 = to_int(scored_val[si])
                    if v > best_val {
                        // skip already-picked: mark via val = -1 after pick
                        if v > -1 {
                            best_val = v
                            best_idx = si
                        }
                    }
                    si = si + 1
                }
                if best_idx < 0 { filled = _PRED_TOP_N }
                else {
                    let chosen = to_string(scored_key[best_idx])
                    let mut already = false
                    try { if to_int(seen[chosen]) > 0 { already = true } } catch e {}
                    if !already {
                        picked = picked.push(chosen)
                        seen[chosen] = "1"
                    }
                    // mark picked — val = -2 so loop skips
                    scored_val[best_idx] = to_string(-2)
                    filled = filled + 1
                }
            }
        }
    }

    // 2) unigram fallback 보충 (picked 가 N 미달 시)
    if len(picked) < _PRED_TOP_N {
        // keys iteration via pairs_by_prev 는 prev 관점 — 전체 unigram 순회 필요
        // hexa map iteration: for (k, v) in map { ... } 가정 (engine 표준).
        // 안전하게 별도 누적 리스트 사용: recent_queries + history 에서 추출.
        let mut pool: list = []
        let mut pi: i64 = 0
        while pi < len(_predict_history) {
            pool = pool.push(to_string(_predict_history[pi]))
            pi = pi + 1
        }
        // dedup + count lookup
        let mut dedup_keys: list = []
        let mut dedup_vals: list = []
        let mut pj: i64 = 0
        while pj < len(pool) {
            let pk = to_string(pool[pj])
            let mut found = false
            let mut dk: i64 = 0
            while dk < len(dedup_keys) {
                if to_string(dedup_keys[dk]) == pk { found = true; dk = len(dedup_keys) }
                dk = dk + 1
            }
            if !found {
                let mut uc: i64 = 0
                try { uc = to_int(_predict_unigram_cnt[pk]) } catch e {}
                dedup_keys = dedup_keys.push(pk)
                dedup_vals = dedup_vals.push(uc)
            }
            pj = pj + 1
        }
        // top-N by val desc, dedup with picked/seen
        let utotal = len(dedup_keys)
        while len(picked) < _PRED_TOP_N {
            let mut ubest_idx: i64 = -1
            let mut ubest_val: i64 = -1
            let mut ui: i64 = 0
            while ui < utotal {
                let uv: i64 = to_int(dedup_vals[ui])
                if uv > ubest_val {
                    if uv > -1 {
                        ubest_val = uv
                        ubest_idx = ui
                    }
                }
                ui = ui + 1
            }
            if ubest_idx < 0 { return picked }
            let ukey = to_string(dedup_keys[ubest_idx])
            let mut u_already = false
            try { if to_int(seen[ukey]) > 0 { u_already = true } } catch e {}
            if !u_already {
                picked = picked.push(ukey)
                seen[ukey] = "1"
            }
            dedup_vals[ubest_idx] = to_string(-2)
        }
    }

    return picked
}

// ─── public API: warm predicted buckets (idle window) ───
//   bucket key → _n6_bucket lookup (이미 로드된 map 내 resolve) + prefix touch.
//   하드 I/O 없음 — in-memory lookup (추후 disk prefetch 확장 여지).
fn _predict_warm_buckets(prefixes: list) -> i64 {
    let mut warmed: i64 = 0
    let mut pi: i64 = 0
    while pi < len(prefixes) {
        let pk = to_string(prefixes[pi])
        if len(pk) > 0 {
            // _n6_bucket 존재 가정 (blowup.hexa 에서 include). try 로 안전화.
            try {
                let idxs = _bucket_indices(_n6_bucket, pk)
                if len(idxs) > 0 { warmed = warmed + 1 }
            } catch e {}
        }
        pi = pi + 1
    }
    return warmed
}

// ─── public API: hit-rate measurement (next-round start) ───
//   predicted ∩ actual 의 크기. hit_rate = hits / len(predicted).
fn _predict_hit_count(predicted: list, actual: list) -> i64 {
    let mut hits: i64 = 0
    let mut pi: i64 = 0
    while pi < len(predicted) {
        let p = to_string(predicted[pi])
        let mut aj: i64 = 0
        while aj < len(actual) {
            if to_string(actual[aj]) == p {
                hits = hits + 1
                aj = len(actual)
            }
            aj = aj + 1
        }
        pi = pi + 1
    }
    return hits
}

// ─── helper: JSON-escape predicted list for NEXUS_PREDICTIVE_WARM emit ───
fn _predict_json_list(xs: list) -> string {
    let mut out = "["
    let mut i: i64 = 0
    while i < len(xs) {
        if i > 0 { out = out + "," }
        let s = to_string(xs[i])
        out = out + "\"" + s + "\""
        i = i + 1
    }
    out = out + "]"
    return out
}

// ─── helper: float hit-rate (picked가 0 이면 0.0) ───
fn _predict_hit_rate(hits: i64, predicted_n: i64) -> f64 {
    if predicted_n < 1 { return 0.0 }
    return to_float(hits) / to_float(predicted_n)
}
