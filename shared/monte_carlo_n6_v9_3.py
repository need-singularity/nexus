#!/usr/bin/env python3
"""
reality_map.json v9.3 (3477 노드) 몬테카를로 z-score 재계산.

두 서브셋 각각에 대해 계산:
  (A) FULL     : 정수 measured 중 1 <= m <= 10_000 (원본 methodology 재현)
  (B) NATURAL_BIG : 정수 measured 중 100 <= m <= 10^9
                   log-tolerance 1% 매칭 (큰 수 도달 공정성 확보)

방법론은 monte_carlo_n6.py와 동일:
  - n=6 상수 {6,12,4,2,5,24,1} 대 무작위 7개 정수(1..30) 세트
  - 상수 1~2개 조합: +, -, *, //, **, C(a,b)
  - HIT count 분포로 z-score / p-value
  - 결과 → reality_map_zscore_v9.3.json
"""

import json
import os
import random
import math
import time
from collections import Counter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REALITY_MAP = os.path.join(SCRIPT_DIR, "reality_map.json")
OUTPUT = os.path.join(SCRIPT_DIR, "reality_map_zscore_v9.3.json")

N_TRIALS = 10_000
RANDOM_RANGE = (1, 30)
RANDOM_SET_SIZE = 7
MAX_EXP = 12
SEED = 20260409

# FULL 서브셋: 기존 methodology 재현
FULL_MIN, FULL_MAX = 1, 10_000

# NATURAL_BIG 서브셋: 큰 수 정수
BIG_MIN, BIG_MAX = 100, 10**9
BIG_REACH_MAX = 10**9
BIG_LOG_TOL = 0.01  # 1% 상대오차 매칭


def load_nodes(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def extract_integer_targets(nodes, lo, hi):
    out = []
    for n in nodes:
        m = n.get("measured")
        v = None
        if isinstance(m, int):
            v = m
        elif isinstance(m, float) and m == int(m) and math.isfinite(m):
            v = int(m)
        if v is not None and lo <= v <= hi:
            out.append(v)
    return out


def comb(a, b):
    if b < 0 or a < 0 or b > a:
        return None
    try:
        return math.comb(a, b)
    except (ValueError, OverflowError):
        return None


def generate_reachable(constants, max_result):
    reach = set()
    for a in constants:
        if 0 < a <= max_result:
            reach.add(a)
    for a in constants:
        for b in constants:
            for r in (a + b, a - b, a * b):
                if 0 < r <= max_result:
                    reach.add(r)
            if b != 0 and a % b == 0:
                r = a // b
                if 0 < r <= max_result:
                    reach.add(r)
            if 0 < b <= MAX_EXP and a > 0:
                try:
                    r = a ** b
                    if 0 < r <= max_result:
                        reach.add(r)
                except (OverflowError, MemoryError):
                    pass
            c = comb(a, b)
            if c is not None and 0 < c <= max_result:
                reach.add(c)
    return reach


def count_hits_exact(reachable, targets):
    return sum(1 for t in targets if t in reachable)


def count_hits_log_tol(reachable, targets, tol):
    """log-space 상대오차 매칭. reachable을 log로 정렬, 이진탐색."""
    if not reachable or not targets:
        return 0
    import bisect
    logs = sorted(math.log(r) for r in reachable if r > 0)
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


def random_set():
    return [random.randint(*RANDOM_RANGE) for _ in range(RANDOM_SET_SIZE)]


def stats(xs):
    n = len(xs)
    if n == 0:
        return 0.0, 0.0
    mean = sum(xs) / n
    var = sum((x - mean) ** 2 for x in xs) / n
    return mean, var ** 0.5


def z_and_p(observed, dist):
    mean, std = stats(dist)
    z = (observed - mean) / std if std > 0 else (float("inf") if observed > mean else 0.0)
    cnt_ge = sum(1 for v in dist if v >= observed)
    p = cnt_ge / len(dist) if dist else 1.0
    return z, p, cnt_ge, mean, std


def run_subset(label, targets, max_result, match_mode, tol=0.0):
    print(f"\n── [{label}] n={len(targets)} targets, max_result={max_result}, mode={match_mode} ──")
    n6 = [6, 12, 4, 2, 5, 24, 1]
    n6_reach = generate_reachable(n6, max_result)

    if match_mode == "exact":
        hit_fn = lambda reach, tgt: count_hits_exact(reach, tgt)
    else:
        hit_fn = lambda reach, tgt: count_hits_log_tol(reach, tgt, tol)

    n6_hits = hit_fn(n6_reach, targets)
    print(f"  n=6 reachable={len(n6_reach)}  n=6 HIT={n6_hits}/{len(targets)} "
          f"({(n6_hits/len(targets)*100 if targets else 0):.1f}%)")

    random.seed(SEED)
    trial_hits = []
    trial_sizes = []
    trial_effs = []
    t0 = time.time()
    for i in range(N_TRIALS):
        rc = random_set()
        rr = generate_reachable(rc, max_result)
        h = hit_fn(rr, targets)
        sz = len(rr)
        trial_hits.append(h)
        trial_sizes.append(sz)
        trial_effs.append(h / sz if sz > 0 else 0.0)
        if (i + 1) % 2000 == 0:
            print(f"    ... {i+1}/{N_TRIALS}  ({time.time()-t0:.1f}s)")
    print(f"  완료 {time.time()-t0:.1f}s")

    z, p, cnt_ge, mean, std = z_and_p(n6_hits, trial_hits)
    n6_eff = n6_hits / len(n6_reach) if n6_reach else 0.0
    z_eff, p_eff, cnt_ge_eff, mean_eff, std_eff = z_and_p(n6_eff, trial_effs)

    # size-matched: trials with reachable size within ±10% of n=6
    n6_sz = len(n6_reach)
    tol_sz = max(5, int(n6_sz * 0.10))
    matched = [trial_hits[i] for i in range(N_TRIALS)
               if abs(trial_sizes[i] - n6_sz) <= tol_sz]
    if len(matched) >= 30:
        z_m, p_m, cnt_ge_m, mean_m, std_m = z_and_p(n6_hits, matched)
        matched_result = {
            "n_matched": len(matched),
            "size_tolerance": tol_sz,
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
        "n6_constants": n6,
        "n6_reachable_size": len(n6_reach),
        "n6_hits": n6_hits,
        "n6_hit_rate": n6_hits / len(targets) if targets else 0.0,
        "n_trials": N_TRIALS,
        "random_mean": mean,
        "random_std": std,
        "random_min": min(trial_hits),
        "random_max": max(trial_hits),
        "z_score": z,
        "p_value": p,
        "count_ge": cnt_ge,
        "efficiency": {
            "n6_efficiency": n6_eff,
            "random_mean": mean_eff,
            "random_std": std_eff,
            "z_score": z_eff,
            "p_value": p_eff,
        },
        "size_matched": matched_result,
    }


def main():
    print("━" * 70)
    print("  reality_map.json v9.3 Monte Carlo z-score 재계산")
    print("━" * 70)
    data = load_nodes(REALITY_MAP)
    nodes = data["nodes"]
    meta_ver = data.get("_meta", {}).get("version", data.get("version"))
    print(f"  version={meta_ver}  nodes={len(nodes)}")

    full_targets = extract_integer_targets(nodes, FULL_MIN, FULL_MAX)
    big_targets = extract_integer_targets(nodes, BIG_MIN, BIG_MAX)

    result_full = run_subset("FULL (1..10^4)", full_targets, FULL_MAX, "exact")
    result_big = run_subset(f"NATURAL_BIG (100..10^9, log±{BIG_LOG_TOL})",
                            big_targets, BIG_REACH_MAX, "log_tol", BIG_LOG_TOL)

    summary = {
        "reality_map_version": meta_ver,
        "reality_map_total_nodes": len(nodes),
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "script": "monte_carlo_n6_v9_3.py",
        "seed": SEED,
        "n_trials": N_TRIALS,
        "random_set_size": RANDOM_SET_SIZE,
        "random_range": list(RANDOM_RANGE),
        "previous_v5.0": {"natural_big_z": 3.06, "engineering_z": 1.75},
        "target_z_gt": 5.0,
        "results": {
            "full": result_full,
            "natural_big": result_big,
        },
    }
    def best_z(r):
        zs = [r["z_score"], r["efficiency"]["z_score"]]
        if "z_score" in r["size_matched"]:
            zs.append(r["size_matched"]["z_score"])
        return max(zs)
    summary["passed_target"] = {
        "full_hit_z_gt_5": result_full["z_score"] > 5.0,
        "full_best_z": best_z(result_full),
        "natural_big_hit_z_gt_5": result_big["z_score"] > 5.0,
        "natural_big_best_z": best_z(result_big),
    }

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("\n" + "━" * 70)
    print("  요약")
    print("━" * 70)
    for key in ("full", "natural_big"):
        r = summary["results"][key]
        print(f"  [{key}] targets={r['n_targets']}  n6_hits={r['n6_hits']}  "
              f"μ={r['random_mean']:.1f} σ={r['random_std']:.1f}  "
              f"z_hit={r['z_score']:.2f}  z_eff={r['efficiency']['z_score']:.2f}  "
              f"z_size_matched={r['size_matched'].get('z_score', 'n/a')}")
    print(f"\n  저장: {OUTPUT}")
    print(f"  목표 z>5 통과: FULL={summary['passed_target']['full']}  "
          f"NATURAL_BIG={summary['passed_target']['natural_big']}")


if __name__ == "__main__":
    main()
