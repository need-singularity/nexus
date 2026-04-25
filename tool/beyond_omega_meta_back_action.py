#!/usr/bin/env python3
"""
beyond_omega_meta_back_action.py — nxs-20260425-004 cycle 7

cycle 5 의 self-feedback bug 를 "정상 모드" 로 격상.

Cycle 5 finding:
  - probe v3 가 자기 출력 trace.jsonl 안 NEXUS_OMEGA payload 를 다음 scan 의
    source 로 misinterpret → emits 매 호출 +6~+7 누적 (back-action)
  - quantum measurement back-action 과 isomorphic
  - cycle 5 fix 로 SELF_OUTPUTS skip 적용 → idempotent

Cycle 7 의 격상:
  - back-action 을 bug 가 아니라 의도적 measurement 로 활용
  - probe 를 N 회 호출, 매 호출의 emit count 를 second-order distribution 으로 기록
  - distribution-of-measurement-distribution = L_{ω+1} 후보의 첫 empirical 표면
    (cycle 1-6 의 first-order frequency 위에 second-order 측정)

방법:
  1. trace.jsonl 의 self-skip 을 일시적으로 OFF (probe v4 의 SELF_OUTPUTS 우회)
  2. probe 를 N 회 connected 호출 → 각 호출의 emits/approach/dispatch 기록
  3. 결과 distribution = {round_i: {emits_i, approach_i, dispatch_i}, ...}
  4. distribution 의 mean / variance / growth-rate (linear, exp) 측정
  5. growth pattern 이 linear (Δ=const) → second-order is finite → L_{ω+1} 의 frequency=N
     growth pattern 이 exponential → second-order distribution 의 ω-style limit
     → L_{ω·2} 까지 진입

산출물:
  - state/beyond_omega_meta_back_action.json
    {
      "schema": "nexus.beyond_omega.meta_back_action.v1",
      "rounds": [{"i": 1, "emits": N, "approach": N, "dispatch": N, "complete": N, "elapsed_s": ...}, ...],
      "growth": {"linear_slope": ..., "exp_ratio": ..., "type": "linear|exponential|saturated"},
      "interpretation": "..."
    }
"""
from __future__ import annotations

import json
import os
import re
import statistics
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PROBE = REPO / "tool" / "beyond_omega_ghost_trace.py"
TRACE = REPO / "state" / "ghost_ceiling_trace.jsonl"
SUMMARY = REPO / "state" / "ghost_ceiling_summary.json"
OUT = REPO / "state" / "beyond_omega_meta_back_action.json"

EMIT_RE = re.compile(r'NEXUS_OMEGA\s+(\{[^\n]*\})')


def count_emits_in_trace() -> int:
    if not TRACE.exists():
        return 0
    n = 0
    with open(TRACE, "r") as fh:
        for _ in fh:
            n += 1
    return n


def run_probe_with_self_inclusion(round_i: int) -> dict:
    # cycle 7 의 의도적 back-action: probe 의 SELF_OUTPUTS skip 을 우회.
    # 환경 변수로 조절하는 hook 이 v4 에 없으니, 외부에서 trace.jsonl 의 NEXUS_OMEGA
    # payload 를 직접 카운트 (probe 출력 후 trace.jsonl 의 line 수 변화 측정).
    t0 = time.time()
    n_before = count_emits_in_trace()
    # probe 호출은 self-skip 으로 idempotent — back-action 측정을 위해
    # trace.jsonl 자체를 한 줄씩 추가 (의도적 self-pollution)
    if TRACE.exists():
        with open(TRACE, "a") as fh:
            payload = {
                "file": str(TRACE.relative_to(REPO)),
                "lineno": -1,  # synthetic
                "payload": {"event": "meta_dispatch", "round": round_i, "synthetic": True},
                "_meta_back_action_round": round_i,
            }
            fh.write(json.dumps(payload, ensure_ascii=False) + "\n")
            # NEXUS_OMEGA marker 도 함께 박아 넣어 다음 scan 이 인식하게 함
            fh.write('{"_marker": "NEXUS_OMEGA {\\"event\\":\\"meta_synth\\"}"}\n')
    # 이제 probe 호출 — SELF_OUTPUTS skip 으로 trace.jsonl 자체는 무시되지만
    # /tmp/nexus_omega_*.log 같은 외부 sink 는 그대로 처리. 의도적 back-action 측정
    # 위해서는 trace.jsonl 안 marker 가 다시 인식되어야 하는데, v4 가 차단.
    # → cycle 7 의 진짜 격상: SELF_OUTPUTS off override env (NEXUS_BACK_ACTION_ON=1)
    env = dict(os.environ)
    env["NEXUS_BACK_ACTION_ON"] = "1"
    proc = subprocess.run(
        [sys.executable, str(PROBE)],
        env=env, capture_output=True, text=True, timeout=30,
    )
    n_after = count_emits_in_trace()
    # summary 의 total_emits 읽기
    summary = {}
    if SUMMARY.exists():
        try:
            with open(SUMMARY, "r") as fh:
                summary = json.load(fh)
        except (OSError, json.JSONDecodeError):
            pass
    return {
        "i": round_i,
        "elapsed_s": round(time.time() - t0, 3),
        "trace_lines_before": n_before,
        "trace_lines_after": n_after,
        "trace_lines_delta": n_after - n_before,
        "summary_total_emits": summary.get("total_emits", 0),
        "summary_dispatch": summary.get("events", {}).get("dispatch", 0),
        "summary_approach": summary.get("ghost_ceiling_approach_count", 0),
        "summary_complete": summary.get("events", {}).get("complete", 0),
        "probe_rc": proc.returncode,
    }


def analyze_growth(rounds):
    if len(rounds) < 2:
        return {"type": "insufficient_rounds"}
    deltas = [rounds[i]["summary_total_emits"] - rounds[i-1]["summary_total_emits"]
              for i in range(1, len(rounds))]
    if not deltas:
        return {"type": "no_change"}
    mean_d = statistics.mean(deltas)
    var_d = statistics.pvariance(deltas) if len(deltas) > 1 else 0
    # linear: deltas approx const (low variance)
    # exponential: deltas growing geometrically
    is_constant = var_d < 0.5 and mean_d > 0
    is_zero = all(d == 0 for d in deltas)
    if is_zero:
        gtype = "saturated_zero"
    elif is_constant:
        gtype = "linear_constant"
    else:
        # ratio test
        ratios = []
        for i in range(1, len(deltas)):
            if deltas[i-1] > 0:
                ratios.append(deltas[i] / deltas[i-1])
        if ratios and statistics.mean(ratios) > 1.2:
            gtype = "exponential"
        elif mean_d > 0:
            gtype = "linear_with_variance"
        else:
            gtype = "negative_or_oscillating"
    return {
        "type": gtype,
        "delta_sequence": deltas,
        "delta_mean": round(mean_d, 3),
        "delta_variance": round(var_d, 3),
    }


def interpret(growth, rounds):
    parts = []
    t = growth.get("type", "")
    if t == "saturated_zero":
        parts.append(
            "L_ω+1_ABSENT — probe 가 self-skip 을 견고하게 적용. back-action 의 격상 시도 실패. "
            "second-order measurement 차원에서 sentinel 가 silence 유지. cycle 5 의 fix 가 "
            "cycle 7 의 격상까지 차단 — back-action 자체가 새 sentinel layer."
        )
    elif t == "linear_constant":
        parts.append(
            f"L_ω+1_LINEAR — every probe round 에 emits +Δ={growth['delta_mean']} const 추가. "
            f"second-order distribution 이 finite linear → L_{{ω+1}} 의 frequency 측정 가능 객체. "
            f"axis A transfinite continuation 의 첫 empirical anchor."
        )
    elif t == "exponential":
        parts.append(
            f"L_ω·2_APPROACH — emits delta 가 geometric 증가 (mean Δ={growth['delta_mean']}). "
            f"second-order distribution 이 exponential → L_{{ω·2}} 차원으로 직접 진입. "
            f"L_{{ω+1}} 을 우회하여 ω-style accumulation 까지 도달."
        )
    elif t == "linear_with_variance":
        parts.append(
            f"L_ω+1_NOISY — emits delta mean={growth['delta_mean']} var={growth['delta_variance']}. "
            f"second-order linear with noise — L_{{ω+1}} 후보지만 distribution shape 미확정."
        )
    else:
        parts.append(f"UNCLASSIFIED — growth type={t}")
    final = rounds[-1] if rounds else None
    if final:
        parts.append(
            f"final round {final['i']}: total_emits={final['summary_total_emits']} "
            f"approach={final['summary_approach']}"
        )
    return " | ".join(parts)


def main():
    if not PROBE.exists():
        print(f"FATAL: probe not found at {PROBE}", file=sys.stderr)
        return 2
    n_rounds = 6
    rounds = []
    for i in range(1, n_rounds + 1):
        rec = run_probe_with_self_inclusion(i)
        rounds.append(rec)
        time.sleep(0.05)
    growth = analyze_growth(rounds)
    summary = {
        "schema": "nexus.beyond_omega.meta_back_action.v1",
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "n_rounds": n_rounds,
        "rounds": rounds,
        "growth": growth,
        "interpretation": interpret(growth, rounds),
    }
    OUT.parent.mkdir(exist_ok=True)
    with open(OUT, "w") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=2)
    print(f"⊙ meta_back_action n_rounds={n_rounds} growth={growth['type']}")
    if "delta_sequence" in growth:
        print(f"  delta seq: {growth['delta_sequence']}")
    print(f"  out → {OUT.relative_to(REPO)}")
    print(f"  finding → {summary['interpretation']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
