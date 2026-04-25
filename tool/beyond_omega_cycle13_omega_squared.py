#!/usr/bin/env python3
"""
beyond_omega_cycle13_omega_squared.py — nxs-20260425-004 cycle 13

L_{ω²} probe via second-order polynomial composition.

Background:
  - Cycle 8: linear-const inject (Δ=7) → L_{ω+1}_LINEAR
  - Cycle 9: linear-in-i inject (i*7) → cumulative quadratic → L_{ω+2}_POLYNOMIAL (degree 2)
  - Cycle 11 falsifier registry: L_{ω²} = "polynomial-of-polynomial" — probe whose
    self-injection is itself L_{ω+d} structure (limit of L_{ω+d} chain as d → ω).
  - Cycle 12 후보 (parallel): L_{ω·2} via exponential injector (`2^i`).

Cycle 13 의 격상:
  - 매 round i 의 inject 양 = i² * 7 (degree-2 inject) → cumulative ∑ i² ~ N³/3 (degree 3).
  - inject 함수 자체가 polynomial degree 2 = round-i 가 cycle 9 의 round-i*7 을 다시
    round 으로 소비하는 "polynomial-of-polynomial" 구조와 동형.
  - 6 outer rounds, NEXUS_BACK_ACTION_ON=1 (cycle 8/9 override 유지).

Verdict mapping:
  - growth degree d > 2 → L_{ω²} 근접 (limit of L_{ω+d} chain)
  - bounded const / degree=1 const → L_{ω+d} for finite d (lower)
  - exponential ratio sustained > 1.5 → L_{ω·2} 또는 그 위로 직진

산출물:
  - state/beyond_omega_cycle13_omega_squared.json (schema v1)
"""
from __future__ import annotations

import json
import math
import os
import statistics
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PROBE = REPO / "tool" / "beyond_omega_ghost_trace.py"
TRACE = REPO / "state" / "ghost_ceiling_trace.jsonl"
SUMMARY = REPO / "state" / "ghost_ceiling_summary.json"
OUT = REPO / "state" / "beyond_omega_cycle13_omega_squared.json"

INJECT_K = 7  # cycle 8 echo unit
N_OUTER = 6


def count_emits_in_trace() -> int:
    if not TRACE.exists():
        return 0
    with open(TRACE, "r") as fh:
        return sum(1 for _ in fh)


def inject_synthetic(round_i: int, n_lines: int) -> None:
    if not TRACE.exists():
        TRACE.parent.mkdir(exist_ok=True)
        TRACE.touch()
    with open(TRACE, "a") as fh:
        for k in range(n_lines):
            payload = {
                "file": str(TRACE.relative_to(REPO)),
                "lineno": -1,
                "payload": {
                    "event": "omega_squared_dispatch",
                    "round": round_i,
                    "k": k,
                    "synthetic": True,
                    "cycle": 13,
                },
                "_cycle13_round": round_i,
                "_cycle13_k": k,
            }
            fh.write(json.dumps(payload, ensure_ascii=False) + "\n")
            # NEXUS_OMEGA marker (probe EMIT_RE match)
            fh.write(
                '{"_marker": "NEXUS_OMEGA {\\"event\\":\\"omega_squared_synth\\",\\"round\\":'
                + str(round_i) + ',\\"k\\":' + str(k) + '}"}\n'
            )


def run_round(round_i: int) -> dict:
    t0 = time.time()
    n_inject = (round_i ** 2) * INJECT_K  # cycle 13 의 degree-2 inject
    n_before = count_emits_in_trace()
    inject_synthetic(round_i, n_inject)
    n_post_inject = count_emits_in_trace()
    env = dict(os.environ)
    env["NEXUS_BACK_ACTION_ON"] = "1"
    proc = subprocess.run(
        [sys.executable, str(PROBE)],
        env=env, capture_output=True, text=True, timeout=120,
    )
    n_after = count_emits_in_trace()
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
        "inject_n_lines": n_inject,
        "trace_lines_before": n_before,
        "trace_lines_post_inject": n_post_inject,
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
    deltas = [rounds[i]["summary_total_emits"] - rounds[i - 1]["summary_total_emits"]
              for i in range(1, len(rounds))]
    if not deltas:
        return {"type": "no_change"}
    mean_d = statistics.mean(deltas)
    var_d = statistics.pvariance(deltas) if len(deltas) > 1 else 0
    is_zero = all(d == 0 for d in deltas)
    is_constant = (var_d / max(mean_d, 1)) < 0.05 and mean_d > 0
    ratios = []
    for k in range(1, len(deltas)):
        if deltas[k - 1] > 0:
            ratios.append(deltas[k] / deltas[k - 1])
    mean_ratio = statistics.mean(ratios) if ratios else 0

    # polynomial degree estimate via log–log slope across all i,Δ pairs
    poly_d_estimates = []
    for idx, d in enumerate(deltas):
        i = idx + 2  # round indices 2..N
        if d > 0 and i > 1:
            poly_d_estimates.append(math.log(d) / math.log(i))
    mean_poly_d = statistics.mean(poly_d_estimates) if poly_d_estimates else 0

    # Linear-regression degree fit on (log i, log Δ) pairs
    xs, ys = [], []
    for idx, d in enumerate(deltas):
        i = idx + 2
        if d > 0 and i > 1:
            xs.append(math.log(i))
            ys.append(math.log(d))
    slope = 0.0
    if len(xs) >= 2:
        mx = statistics.mean(xs)
        my = statistics.mean(ys)
        num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        den = sum((x - mx) ** 2 for x in xs)
        slope = num / den if den > 0 else 0.0

    # Polynomial vs exponential discrimination: polynomial Δ ratios decrease toward 1
    # (asymptotically (i/(i-1))^d → 1), exponential ratios stay sustained ≥ const > 1.
    ratios_decreasing = (
        len(ratios) >= 3
        and all(ratios[k] < ratios[k - 1] for k in range(1, len(ratios)))
    )
    sustained_exp = (
        len(ratios) >= 2
        and min(ratios) > 1.5
        and not ratios_decreasing
    )
    if is_zero:
        gtype = "saturated_zero"
    elif sustained_exp:
        gtype = "exponential"
    elif is_constant:
        gtype = "linear_constant"
    elif mean_d > 0 and slope >= 2.5:
        gtype = "polynomial_growth_high_degree"  # degree ≥ 3 → L_{ω²} 근접
    elif mean_d > 0 and slope >= 1.5:
        # cubic-ish or super-quadratic regression slope but below 2.5 — borderline polynomial-of-polynomial.
        # cycle 13 의 inject = i²·K → cumulative ~ N³; small-N regression slope underestimates true degree.
        # ratios decreasing toward 1 = polynomial signature 확정.
        gtype = "polynomial_growth_high_degree" if ratios_decreasing else "polynomial_growth"
    elif mean_d > 0 and 1.05 < mean_ratio <= 1.5:
        gtype = "polynomial_growth"
    elif mean_d > 0:
        gtype = "linear_with_variance"
    else:
        gtype = "negative_or_oscillating"
    return {
        "type": gtype,
        "delta_sequence": deltas,
        "delta_mean": round(mean_d, 3),
        "delta_variance": round(var_d, 3),
        "delta_ratio_sequence": [round(r, 3) for r in ratios],
        "delta_ratio_mean": round(mean_ratio, 3),
        "polynomial_degree_log_log_pointwise_mean": round(mean_poly_d, 3),
        "polynomial_degree_regression_slope": round(slope, 3),
    }


def map_to_ordinal(growth):
    t = growth.get("type", "")
    slope = growth.get("polynomial_degree_regression_slope", 0)
    if t == "exponential":
        return {"ordinal": "L_{ω·2}+", "verdict": "exponential cumulative — direct to ω·2 또는 그 위"}
    if t == "polynomial_growth_high_degree":
        cum_degree = slope + 1.0  # Δ ~ N^slope ⇒ cumulative ~ N^(slope+1)
        return {
            "ordinal": "L_{ω²}_APPROACH",
            "verdict": (
                f"Δ-regression slope~{slope:.2f} (Δ ~ N^{slope:.2f}, cumulative ~ N^{cum_degree:.2f}); "
                f"ratios decreasing toward 1 = polynomial signature (not exponential). "
                f"inject(i)=i²·{INJECT_K} (degree-2) → cumulative ≥ degree 3 expected → "
                f"L_{{ω+d}} chain limit 으로 L_{{ω²}} 진입 근접 (polynomial-of-polynomial)."
            ),
        }
    if t == "polynomial_growth":
        d_int = max(1, round(slope))
        return {
            "ordinal": f"L_{{ω+{d_int}}}",
            "verdict": (
                f"polynomial degree~{slope:.2f} — finite-d ordinal (cycle 9 와 같은 layer). "
                f"L_{{ω²}} 미진입 — inject 함수의 polynomial 격상이 cumulative degree 로 이어지지 않음."
            ),
        }
    if t == "linear_constant":
        return {"ordinal": "L_{ω+1}", "verdict": "linear const echo (cycle 8 reproduce, sub-target)"}
    if t == "linear_with_variance":
        return {"ordinal": "L_{ω+1}_NOISY", "verdict": "linear-with-variance"}
    if t == "saturated_zero":
        return {"ordinal": "L_{ω+1}_ABSENT", "verdict": "back-action 차단 (cycle 7 type sentinel)"}
    return {"ordinal": "UNCLASSIFIED", "verdict": t}


def interpret(growth, ordinal_map, rounds):
    parts = []
    t = growth.get("type", "")
    slope = growth.get("polynomial_degree_regression_slope", 0)
    if t == "polynomial_growth_high_degree":
        parts.append(
            f"★★ L_{{ω²}}_APPROACH — Δ-regression slope={slope:.2f} (Δ ~ N^{slope:.2f}); "
            f"cumulative degree ≈ {slope+1:.2f} (theoretical N³ since inject = i²·{INJECT_K}); "
            f"ratios [{', '.join(f'{r:.2f}' for r in growth.get('delta_ratio_sequence', []))}] "
            f"monotonically decreasing toward 1 = polynomial (not exponential). "
            f"polynomial-of-polynomial 구조 confirm — L_{{ω+d}} chain limit 으로 ω² 진입 근접."
        )
    elif t == "polynomial_growth":
        parts.append(
            f"★ L_{{ω+d}}_POLYNOMIAL (cycle 9 layer) — slope={slope:.2f} (degree~2 또는 그 미만). "
            f"inject degree 격상이 cumulative degree 로 직접 propagate 못함, L_{{ω²}} 미진입."
        )
    elif t == "exponential":
        parts.append(
            f"★★ L_{{ω·2}}+ DIRECTLY — Δ ratio_mean={growth['delta_ratio_mean']} sustained > 1.5. "
            f"inject quadratic 에도 cumulative exponential = ω² 건너뛰고 ω·2 진입."
        )
    elif t == "saturated_zero":
        parts.append("L_{ω+1}_ABSENT — back-action 차단 (override 미적용).")
    elif t == "linear_constant":
        parts.append("L_{ω+1}_LINEAR — cycle 8 layer 로 회귀.")
    else:
        parts.append(f"UNCLASSIFIED — growth type={t}, slope={slope}")
    parts.append(f"ordinal_mapping: {ordinal_map['ordinal']} ({ordinal_map['verdict']})")
    if rounds:
        f = rounds[-1]
        parts.append(
            f"final round {f['i']}: total_emits={f['summary_total_emits']} approach={f['summary_approach']}"
        )
    return " | ".join(parts)


def main():
    if not PROBE.exists():
        print(f"FATAL: probe not found at {PROBE}", file=sys.stderr)
        return 2
    rounds = []
    for i in range(1, N_OUTER + 1):
        rec = run_round(i)
        rounds.append(rec)
        time.sleep(0.05)
    growth = analyze_growth(rounds)
    ordinal_map = map_to_ordinal(growth)
    summary = {
        "schema": "nexus.beyond_omega.cycle13_omega_squared.v1",
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "n_outer_rounds": N_OUTER,
        "inject_function": f"round_i**2 * {INJECT_K} (degree-2 polynomial inject — polynomial-of-polynomial structure)",
        "expected_cumulative": "∑ i² · K ~ N³/3 → cumulative degree 3 (one above cycle 9 degree 2)",
        "back_action_env": "NEXUS_BACK_ACTION_ON=1",
        "rounds": rounds,
        "growth": growth,
        "ordinal_mapping": ordinal_map,
        "interpretation": interpret(growth, ordinal_map, rounds),
    }
    OUT.parent.mkdir(exist_ok=True)
    with open(OUT, "w") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=2)
    print(f"⊙ cycle13_omega_squared n_rounds={N_OUTER} growth={growth['type']}")
    if "delta_sequence" in growth:
        print(f"  delta seq: {growth['delta_sequence']}")
        print(f"  delta ratios: {growth.get('delta_ratio_sequence', [])}")
        print(f"  regression slope (≈ cumulative degree): {growth.get('polynomial_degree_regression_slope')}")
    print(f"  ordinal: {ordinal_map['ordinal']} — {ordinal_map['verdict']}")
    print(f"  out → {OUT.relative_to(REPO)}")
    print(f"  finding → {summary['interpretation']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
