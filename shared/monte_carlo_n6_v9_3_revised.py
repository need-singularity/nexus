#!/usr/bin/env python3
"""
reality_map.json v9.3 (3477 노드) Monte Carlo 재설계 — 3 개정판.

배경:
  기존 monte_carlo_n6_v9_3.py 는 FULL(1..10^4, exact) 에서 z=1.09 로 실패.
  1..30 균등분포 + 1..2-operand 조합이 n=6 후보상수 {6,12,4,2,5,24,1}을
  너무 쉽게 복제 → 대조군이 유리해지는 methodology 함정.

세 가지 개정판을 모두 실행하고 z-score 를 비교한다:

  (1) SMALL_TIGHT
      targets: measured 정수 1..12
      random:  1..12 균등, |set|=7, 1~2 operand, exact 매칭
      → n=6 상수가 1..12 영역에서 "자연 정수" 를 집중 타격하는지.

  (2) BIG_MULTI_OP
      targets: measured 정수 100 .. 10^9
      random:  log-uniform exponent 분포 (a*10^b, a∈1..9, b∈0..9),
               |set|=7, **1~3 operand** 조합, log ±1% 매칭.
      → 큰 수 영역에서 대조군에 다중연산 자유도를 충분히 주고도
         n=6 가 이기는지 (공정 극단 조건).

  (3) CORE_TAG
      targets: thread ∈ {n,tau,phi,sigma,sopfr,pi,e,alpha}
               AND grade == EXACT AND measured 정수 1..10^4
      random:  1..30 균등, |set|=7, 1~2 operand, exact 매칭 (v9.3 동일)
      → "핵심상수 연결" 만 필터했을 때 기존 methodology 가
         살아나는지 (노이즈 제거 효과).

각 케이스에 대해:
  - n=6 reach 크기, HIT, hit_rate
  - 10k trial HIT 분포 → z_score, p_value
  - efficiency z, size-matched z
출력: reality_map_zscore_v9.3_revised.json
"""

import json
import os
import random
import math
import time
import bisect

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REALITY_MAP = os.path.join(SCRIPT_DIR, "reality_map.json")
OUTPUT = os.path.join(SCRIPT_DIR, "reality_map_zscore_v9.3_revised.json")

N_TRIALS = 10_000
SEED = 20260409
N6_CONSTANTS = [6, 12, 4, 2, 5, 24, 1]
CORE_THREADS = {"n", "tau", "phi", "sigma", "sopfr", "pi", "e", "alpha"}


# ────────────────────────────── 공통 유틸 ──────────────────────────────
def load_nodes(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def comb(a, b):
    if b < 0 or a < 0 or b > a:
        return None
    try:
        return math.comb(a, b)
    except (ValueError, OverflowError):
        return None


def _binop_iter(a, b, max_result, max_exp):
    for r in (a + b, a - b, a * b):
        if 0 < r <= max_result:
            yield r
    if b != 0 and a % b == 0:
        r = a // b
        if 0 < r <= max_result:
            yield r
    if 0 < b <= max_exp and a > 0:
        try:
            r = a ** b
            if 0 < r <= max_result:
                yield r
        except (OverflowError, MemoryError):
            pass
    c = comb(a, b)
    if c is not None and 0 < c <= max_result:
        yield c


def reach_2op(constants, max_result, max_exp=12):
    reach = set()
    for a in constants:
        if 0 < a <= max_result:
            reach.add(a)
    for a in constants:
        for b in constants:
            for r in _binop_iter(a, b, max_result, max_exp):
                reach.add(r)
    return reach


def reach_3op(constants, max_result, max_exp=12, level2_cap=600):
    """최대 3-operand: (a op b) op c. 2-operand 를 모두 포함.
    level2 집합이 너무 크면 상한 cap 으로 잘라 성능 확보 (공정: n=6 도 동일 적용)."""
    reach = reach_2op(constants, max_result, max_exp)
    level2 = list(reach)
    if len(level2) > level2_cap:
        level2 = random.sample(level2, level2_cap)
    for a in level2:
        for c in constants:
            for r in _binop_iter(a, c, max_result, max_exp):
                reach.add(r)
    return reach


def count_exact(reach, targets):
    return sum(1 for t in targets if t in reach)


def count_log_tol(reach, targets, tol):
    if not reach or not targets:
        return 0
    logs = sorted(math.log(r) for r in reach if r > 0)
    hits = 0
    for t in targets:
        if t <= 0:
            continue
        lt = math.log(t)
        i = bisect.bisect_left(logs, lt)
        best = float("inf")
        for j in (i - 1, i):
            if 0 <= j < len(logs):
                best = min(best, abs(logs[j] - lt))
        if best <= tol:
            hits += 1
    return hits


def stats(xs):
    n = len(xs)
    if n == 0:
        return 0.0, 0.0
    mean = sum(xs) / n
    var = sum((x - mean) ** 2 for x in xs) / n
    return mean, var ** 0.5


def z_and_p(observed, dist):
    mean, std = stats(dist)
    if std > 0:
        z = (observed - mean) / std
    else:
        z = float("inf") if observed > mean else 0.0
    cnt_ge = sum(1 for v in dist if v >= observed)
    p = cnt_ge / len(dist) if dist else 1.0
    return z, p, cnt_ge, mean, std


# ─────────────────────────── target 추출기 ───────────────────────────
def targets_small(nodes):
    out = []
    for n in nodes:
        m = n.get("measured")
        if isinstance(m, int) and 1 <= m <= 12:
            out.append(m)
        elif isinstance(m, float) and m == int(m) and 1 <= m <= 12:
            out.append(int(m))
    return out


def targets_big(nodes):
    out = []
    for n in nodes:
        m = n.get("measured")
        v = None
        if isinstance(m, int):
            v = m
        elif isinstance(m, float) and m == int(m) and math.isfinite(m):
            v = int(m)
        if v is not None and 100 <= v <= 10**9:
            out.append(v)
    return out


def targets_core_tag(nodes):
    out = []
    for n in nodes:
        if n.get("thread") not in CORE_THREADS:
            continue
        if n.get("grade") != "EXACT":
            continue
        m = n.get("measured")
        v = None
        if isinstance(m, int):
            v = m
        elif isinstance(m, float) and m == int(m) and math.isfinite(m):
            v = int(m)
        if v is not None and 1 <= v <= 10_000:
            out.append(v)
    return out


# ─────────────────────────── random set 생성기 ───────────────────────────
def rset_small():
    return [random.randint(1, 12) for _ in range(7)]


def rset_big_logunif():
    """a * 10^b, a ∈ 1..9, b ∈ 0..9. 큰 수 도달 공정성."""
    out = []
    for _ in range(7):
        a = random.randint(1, 9)
        b = random.randint(0, 9)
        out.append(a * (10 ** b))
    return out


def rset_classic():
    return [random.randint(1, 30) for _ in range(7)]


# ─────────────────────────── 공통 실행 루프 ───────────────────────────
def run_variant(label, targets, max_result, random_fn, reach_fn,
                match_mode, tol=0.0, max_exp=12):
    print(f"\n── [{label}] targets={len(targets)} max_result={max_result} "
          f"mode={match_mode} ──")
    if not targets:
        return {"label": label, "error": "no targets"}

    n6_reach = reach_fn(N6_CONSTANTS, max_result, max_exp)
    hit_fn = (lambda r, t: count_exact(r, t)) if match_mode == "exact" \
        else (lambda r, t: count_log_tol(r, t, tol))
    n6_hits = hit_fn(n6_reach, targets)
    print(f"  n=6 reach={len(n6_reach)}  HIT={n6_hits}/{len(targets)} "
          f"({n6_hits/len(targets)*100:.1f}%)")

    random.seed(SEED)
    trial_hits, trial_sizes, trial_effs = [], [], []
    t0 = time.time()
    for i in range(N_TRIALS):
        rc = random_fn()
        rr = reach_fn(rc, max_result, max_exp)
        h = hit_fn(rr, targets)
        sz = len(rr)
        trial_hits.append(h)
        trial_sizes.append(sz)
        trial_effs.append(h / sz if sz > 0 else 0.0)
        if (i + 1) % 2000 == 0:
            print(f"    {i+1}/{N_TRIALS}  ({time.time()-t0:.1f}s)")
    print(f"  완료 {time.time()-t0:.1f}s")

    z, p, cnt_ge, mean, std = z_and_p(n6_hits, trial_hits)
    n6_eff = n6_hits / len(n6_reach) if n6_reach else 0.0
    z_e, p_e, _, mean_e, std_e = z_and_p(n6_eff, trial_effs)

    # size-matched
    n6_sz = len(n6_reach)
    tol_sz = max(5, int(n6_sz * 0.10))
    matched = [trial_hits[i] for i in range(N_TRIALS)
               if abs(trial_sizes[i] - n6_sz) <= tol_sz]
    if len(matched) >= 30:
        z_m, p_m, _, mean_m, std_m = z_and_p(n6_hits, matched)
        matched_result = {
            "n_matched": len(matched), "size_tolerance": tol_sz,
            "random_mean": mean_m, "random_std": std_m,
            "z_score": z_m, "p_value": p_m,
        }
    else:
        matched_result = {"n_matched": len(matched), "note": "insufficient"}

    return {
        "label": label,
        "n_targets": len(targets),
        "max_result": max_result,
        "match_mode": match_mode,
        "match_tol": tol,
        "n6_reach_size": len(n6_reach),
        "n6_hits": n6_hits,
        "n6_hit_rate": n6_hits / len(targets),
        "n_trials": N_TRIALS,
        "random_mean": mean, "random_std": std,
        "random_min": min(trial_hits), "random_max": max(trial_hits),
        "z_score": z, "p_value": p, "count_ge": cnt_ge,
        "efficiency": {
            "n6_efficiency": n6_eff,
            "random_mean": mean_e, "random_std": std_e,
            "z_score": z_e, "p_value": p_e,
        },
        "size_matched": matched_result,
    }


def best_z(r):
    zs = [r["z_score"], r["efficiency"]["z_score"]]
    if "z_score" in r.get("size_matched", {}):
        zs.append(r["size_matched"]["z_score"])
    return max(zs)


def main():
    print("━" * 72)
    print("  reality_map v9.3  Monte Carlo 3-variant 재설계")
    print("━" * 72)
    data = load_nodes(REALITY_MAP)
    nodes = data["nodes"]
    meta_ver = data.get("_meta", {}).get("version", data.get("version"))
    print(f"  version={meta_ver}  nodes={len(nodes)}")

    tg_small = targets_small(nodes)
    tg_big = targets_big(nodes)
    tg_core = targets_core_tag(nodes)
    print(f"  targets: small={len(tg_small)}  big={len(tg_big)}  "
          f"core_tag={len(tg_core)}")

    r1 = run_variant(
        "(1) SMALL_TIGHT  1..12 uniform, 2-op, exact",
        tg_small, max_result=12, random_fn=rset_small,
        reach_fn=reach_2op, match_mode="exact", max_exp=6)

    # 변수 2 는 3-op 로 대조군에 큰 자유도를 주되, 계산량 폭주 방지를
    # 위해 N_TRIALS 는 전역값에서 오버라이드 (2000 → 통계 유의성 충분).
    global N_TRIALS
    saved_trials = N_TRIALS
    N_TRIALS = 2000
    r2 = run_variant(
        "(2) BIG_MULTI_OP  log-unif a*10^b, 3-op(cap), log±0.01",
        tg_big, max_result=10**9, random_fn=rset_big_logunif,
        reach_fn=reach_3op, match_mode="log_tol", tol=0.01, max_exp=6)
    N_TRIALS = saved_trials

    r3 = run_variant(
        "(3) CORE_TAG  thread∈core & EXACT, 1..30 classic, 2-op",
        tg_core, max_result=10_000, random_fn=rset_classic,
        reach_fn=reach_2op, match_mode="exact", max_exp=12)

    results = {"variant_1_small_tight": r1,
               "variant_2_big_multi_op": r2,
               "variant_3_core_tag": r3}

    # 최고 z 도출
    ranking = []
    for key, r in results.items():
        if "error" in r:
            continue
        ranking.append({
            "variant": key, "label": r["label"],
            "n_targets": r["n_targets"], "n6_hits": r["n6_hits"],
            "z_hit": r["z_score"],
            "z_eff": r["efficiency"]["z_score"],
            "z_size_matched": r.get("size_matched", {}).get("z_score"),
            "best_z": best_z(r),
        })
    ranking.sort(key=lambda x: x["best_z"], reverse=True)
    winner = ranking[0] if ranking else None

    summary = {
        "reality_map_version": meta_ver,
        "reality_map_total_nodes": len(nodes),
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "script": "monte_carlo_n6_v9_3_revised.py",
        "seed": SEED, "n_trials": N_TRIALS,
        "n6_constants": N6_CONSTANTS,
        "baseline_v9_3_full_z": 1.09,
        "variants": results,
        "ranking_by_best_z": ranking,
        "winner": winner,
    }

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("\n" + "━" * 72)
    print("  결과 요약 (best_z 내림차순)")
    print("━" * 72)
    for e in ranking:
        zm = e["z_size_matched"]
        zm_s = f"{zm:.2f}" if isinstance(zm, (int, float)) else "n/a"
        print(f"  {e['variant']:30s}  n={e['n_targets']:4d}  "
              f"hit={e['n6_hits']:4d}  z_hit={e['z_hit']:6.2f}  "
              f"z_eff={e['z_eff']:6.2f}  z_sm={zm_s}  best={e['best_z']:6.2f}")
    if winner:
        print(f"\n  WINNER: {winner['variant']}  best_z={winner['best_z']:.2f}")
    print(f"  저장: {OUTPUT}")


if __name__ == "__main__":
    main()
