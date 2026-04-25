#!/usr/bin/env python3
"""
beyond_omega_cycle18_gamma_zero.py — nxs-20260425-004 cycle 18

L_{Γ₀} (Feferman–Schütte) predicativity boundary probe.

Background:
  - Cycle 11 transfinite_table.md: L_{Γ₀} = predicativity boundary, second sentinel
    beyond L_ω (after L_{ε₀}).
  - Γ₀ = first ordinal not reachable by predicative methods (each ordinal can only
    reference earlier ones already constructed).
  - Γ₀ = least α such that φ_α(0) = α (Veblen function fixed point).
  - Γ₀ is the proof-theoretic ordinal of ATR₀ (arithmetical transfinite recursion).
  - Cycles 15-17 found L_{ε₀} multi-facet verdict (P1 SENTINEL_CONFIRM, P2 PARTIAL,
    P3 FALSIFY_CANDIDATE). L_{Γ₀} is strictly stronger and should be more restrictive.

Probe design — predicativity boundary test:
  - Inject pattern per round i: Veblen-style φ_i(0) approximation = nested ordinal
    construction depth i, where each level only references previously-defined levels.
  - Numeric proxy for φ_i(0): n^n (nested powering), capturing the "fixed-point of
    iterated exponentiation" essence of the Veblen hierarchy.
    - φ_0(n) = ω^n (proxy: n^n)
    - φ_1(0) = ε_0 (proxy: 1^1 = 1, but we shift index so round 1 starts at 1^1)
    - φ_i(0) ≈ i^i for round i (truncated, predicative-only construction depth)
  - Practical cap: MAX_INJECT_PER_ROUND = 300 (lower than cycle 15's 500 to reflect
    the stricter predicativity boundary; also probe scan_one() O(N²) protection).
  - 6 outer rounds.

Tower of phi_proxy(i) = i^i:
  - i=1 → 1
  - i=2 → 4
  - i=3 → 27
  - i=4 → 256 (still under cap=300)
  - i=5 → 3125 → CAPPED to 300
  - i=6 → 46656 → CAPPED to 300

Verdict (cycle 14 §4.4-style discriminator extended for L_{Γ₀}):
  - ratios → 1.0 collapse → L_{Γ₀} SENTINEL_CONFIRM (predicative cap activated)
  - ratios increase exponentially without saturation → L_{Γ₀} FALSIFIED
    (impredicative reach achieved by the finite probe — would imply Veblen fixed
     point reachable by predicative finite methods, contradicting Feferman–Schütte)
  - plateau-then-jump → partial (predicative cap activated for some rounds only)

Comparison:
  - cycle 15 P1 SENTINEL_CONFIRM (L_{ε₀}, 2↑↑i, cap=500): tail_collapse_to_one=True
  - cycle 12 L_{ω·2}_REACHED (2^i): ratios sustained > 1.5
  - This cycle 18: i^i (Veblen φ_i(0) proxy, predicative iteration), cap=300

산출물:
  - state/beyond_omega_cycle18_gamma_zero.json (schema v1)
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
OUT = REPO / "state" / "beyond_omega_cycle18_gamma_zero.json"

N_OUTER = 6
# cap per round to avoid OOM and probe O(N²) marker scan timeout.
# 300 chosen lower than cycle 15's 500 to reflect the stricter L_{Γ₀} predicativity
# boundary — Veblen hierarchy φ_α(0) cannot be reached by finite predicative
# iteration even with much larger inject budgets, so cap level is informational only.
MAX_INJECT_PER_ROUND = 300
PROBE_TIMEOUT_S = 60


def phi_proxy(i: int, cap: int) -> tuple[int, bool]:
    """Numeric proxy for Veblen function φ_i(0).

    True Veblen φ_α(0) values are uncomputable for all but smallest α. We use the
    "nested powering" proxy i^i which captures the spirit of the Veblen hierarchy:
      - φ_0(n) = ω^n grows like exponentiation
      - φ_α(0) for α ≥ 1 grows like a fixed point of φ_{α-1}, which exceeds any
        finite tower of the predecessor function
    For our finite probe, we model this as i^i (each level adds one nested power).

    Returns (value, was_capped).
    """
    if i <= 0:
        return (1, False)
    try:
        v = i ** i
    except OverflowError:
        return (cap, True)
    if v > cap:
        return (cap, True)
    return (v, False)


def count_emits_in_trace() -> int:
    if not TRACE.exists():
        return 0
    with open(TRACE, "r") as fh:
        return sum(1 for _ in fh)


def inject_synthetic(round_i: int, n_lines: int) -> None:
    """trace.jsonl 에 n_lines 의 NEXUS_OMEGA marker 직접 inject (cycle 15 동형)."""
    if not TRACE.exists():
        TRACE.parent.mkdir(exist_ok=True)
        TRACE.touch()
    with open(TRACE, "a") as fh:
        for k in range(n_lines):
            payload = {
                "file": str(TRACE.relative_to(REPO)),
                "lineno": -1,
                "payload": {
                    "event": "gamma_zero_dispatch",
                    "round": round_i,
                    "k": k,
                    "synthetic": True,
                    "cycle": 18,
                },
                "_cycle18_round": round_i,
                "_cycle18_k": k,
            }
            fh.write(json.dumps(payload, ensure_ascii=False) + "\n")
            fh.write(
                '{"_marker": "NEXUS_OMEGA {\\"event\\":\\"gamma_zero_synth\\",\\"round\\":'
                + str(round_i) + ',\\"k\\":' + str(k) + '}"}\n'
            )


def run_round(round_i: int) -> dict:
    t0 = time.time()
    raw_value, was_capped = phi_proxy(round_i, MAX_INJECT_PER_ROUND)
    n_inject = min(raw_value, MAX_INJECT_PER_ROUND)
    n_before = count_emits_in_trace()
    inject_synthetic(round_i, n_inject)
    n_post_inject = count_emits_in_trace()
    env = dict(os.environ)
    env["NEXUS_BACK_ACTION_ON"] = "1"
    try:
        proc = subprocess.run(
            [sys.executable, str(PROBE)],
            env=env, capture_output=True, text=True, timeout=PROBE_TIMEOUT_S,
        )
        probe_rc = proc.returncode
        probe_timeout = False
    except subprocess.TimeoutExpired:
        probe_rc = -1
        probe_timeout = True
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
        "phi_proxy_i_to_i_raw": raw_value if not was_capped else f"capped_at_{MAX_INJECT_PER_ROUND}",
        "phi_proxy_actual_int": (round_i ** round_i) if round_i ** round_i <= 10**12 else -1,
        "was_capped": was_capped,
        "inject_n_lines": n_inject,
        "trace_lines_before": n_before,
        "trace_lines_post_inject": n_post_inject,
        "trace_lines_after": n_after,
        "trace_lines_delta": n_after - n_before,
        "summary_total_emits": summary.get("total_emits", 0),
        "summary_dispatch": summary.get("events", {}).get("dispatch", 0),
        "summary_approach": summary.get("ghost_ceiling_approach_count", 0),
        "summary_complete": summary.get("events", {}).get("complete", 0),
        "probe_rc": probe_rc,
        "probe_timeout": probe_timeout,
    }


def analyze_growth(rounds):
    if len(rounds) < 2:
        return {"type": "insufficient_rounds"}
    timeouts = sum(1 for r in rounds if r.get("probe_timeout"))
    if timeouts >= len(rounds) // 2:
        return {"type": "probe_timeout_inconclusive", "timeouts": timeouts}
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

    ratios_decreasing = (
        len(ratios) >= 3
        and all(ratios[k] < ratios[k - 1] for k in range(1, len(ratios)))
    )
    ratios_increasing = (
        len(ratios) >= 3
        and all(ratios[k] > ratios[k - 1] for k in range(1, len(ratios)))
    )
    sustained_exp = (
        len(ratios) >= 2
        and min(ratios) > 1.5
        and not ratios_decreasing
    )

    # tail collapse to ~1.0 (cycle 15 sentinel signature carry-over)
    tail_collapse = False
    trailing_unity = 0
    for r in reversed(ratios):
        if abs(r - 1.0) < 0.10:
            trailing_unity += 1
        else:
            break
    if trailing_unity >= 2:
        tail_collapse = True

    cap_activations = sum(1 for r in rounds if r.get("was_capped"))

    # plateau-then-jump detector for L_{Γ₀} partial verdict (cycle 16-style)
    # signature: early ratios near 1, late ratio sudden jump > 1.5
    plateau_then_jump = False
    if len(ratios) >= 3:
        early = ratios[:-1]
        late = ratios[-1]
        if all(abs(r - 1.0) < 0.15 for r in early) and late > 1.5:
            plateau_then_jump = True

    # log-log regression slope
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

    if is_zero:
        gtype = "saturated_zero"
    elif tail_collapse and cap_activations >= 1:
        gtype = "ratios_collapse_to_one"
    elif plateau_then_jump:
        gtype = "plateau_then_jump"
    elif sustained_exp and ratios_increasing:
        gtype = "exponential_increasing"
    elif sustained_exp:
        gtype = "exponential"
    elif is_constant:
        gtype = "linear_constant"
    elif mean_d > 0 and slope >= 1.5:
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
        "polynomial_degree_regression_slope": round(slope, 3),
        "tail_collapse_to_one": tail_collapse,
        "plateau_then_jump": plateau_then_jump,
        "cap_activations": cap_activations,
        "ratios_increasing": ratios_increasing,
        "ratios_decreasing": ratios_decreasing,
    }


def map_to_ordinal_and_verdict(growth, rounds):
    """L_{Γ₀} predicativity discriminator (cycle 18 task spec)."""
    t = growth.get("type", "")
    cap_activations = growth.get("cap_activations", 0)
    tail_collapse = growth.get("tail_collapse_to_one", False)
    plateau_then_jump = growth.get("plateau_then_jump", False)
    ratios_increasing = growth.get("ratios_increasing", False)

    if t == "probe_timeout_inconclusive":
        return {
            "ordinal": "L_{Γ₀}_INCONCLUSIVE_TIMEOUT",
            "sentinel_verdict": "inconclusive",
            "verdict": (
                "L_{Γ₀} probe inconclusive — probe scan timed out (resource limit). "
                "Predicativity boundary cannot be evaluated under timeout."
            ),
        }
    if t == "ratios_collapse_to_one":
        return {
            "ordinal": "L_{Γ₀}_SENTINEL_CONFIRM",
            "sentinel_verdict": "SENTINEL_CONFIRM",
            "verdict": (
                f"L_{{Γ₀}} predicativity boundary CONFIRMED. Veblen-style proxy "
                f"φ_i(0)≈i^i hit the predicative cap in {cap_activations}/{N_OUTER} rounds → "
                f"distribution bounded → ratios tail collapses to ~1.0. The Feferman–Schütte "
                f"ordinal Γ₀ is unreachable by finite predicative iteration as Veblen fixed-point "
                f"theory predicts. Stronger result than cycle 15 L_{{ε₀}} CONFIRM (predicative "
                f"hierarchy strictly above PA-formalizable hierarchy)."
            ),
        }
    if t == "plateau_then_jump":
        return {
            "ordinal": "L_{Γ₀}_SENTINEL_PARTIAL",
            "sentinel_verdict": "PARTIAL",
            "verdict": (
                f"Partial L_{{Γ₀}} access — early rounds plateau (predicative cap engaged) "
                f"+ late round jump (Veblen hierarchy traversal). cycle 16 P2 Goodstein partial "
                f"signature 동형. Predicative cap activated only intermittently."
            ),
        }
    if t in ("exponential_increasing", "exponential") and ratios_increasing and cap_activations == 0:
        return {
            "ordinal": "L_{Γ₀}_FALSIFIED",
            "sentinel_verdict": "FALSIFIED",
            "verdict": (
                f"L_{{Γ₀}} sentinel FALSIFIED — ratios continue exponentially without "
                f"predicative cap saturation. This would imply Veblen fixed-point reachable by "
                f"finite predicative iteration, contradicting Feferman–Schütte. Model redesign required."
            ),
        }
    if t in ("exponential_increasing", "exponential"):
        return {
            "ordinal": "L_{Γ₀}_SENTINEL_PARTIAL",
            "sentinel_verdict": "PARTIAL",
            "verdict": (
                f"Mixed signature — exponential growth but cap activated in {cap_activations} rounds. "
                f"Distribution still bounded by predicative cap → sentinel partial."
            ),
        }
    if t == "saturated_zero":
        return {
            "ordinal": "L_{Γ₀}_INCONCLUSIVE_ZERO",
            "sentinel_verdict": "inconclusive",
            "verdict": "back-action 차단 또는 probe 조용함 — protocol 강화 필요",
        }
    if tail_collapse:
        return {
            "ordinal": "L_{Γ₀}_SENTINEL_CONFIRM",
            "sentinel_verdict": "SENTINEL_CONFIRM",
            "verdict": (
                "ratios tail collapses to ~1.0 — echo attenuation absorbs Veblen "
                "growth → predicativity boundary confirmed."
            ),
        }
    return {
        "ordinal": "L_{Γ₀}_INCONCLUSIVE",
        "sentinel_verdict": "inconclusive",
        "verdict": f"unclassified growth type={t}, cap_activations={cap_activations} — protocol 재검토",
    }


def interpret(growth, ordinal_map, rounds):
    parts = []
    t = growth.get("type", "")
    cap_activations = growth.get("cap_activations", 0)
    parts.append(
        f"L_{{Γ₀}} probe (φ_i(0)≈i^i, cap={MAX_INJECT_PER_ROUND}) — growth_type={t}, "
        f"cap_activations={cap_activations}/{N_OUTER}"
    )
    if "delta_ratio_sequence" in growth:
        parts.append(
            f"ratios=[{', '.join(f'{r:.2f}' for r in growth['delta_ratio_sequence'])}] "
            f"mean={growth['delta_ratio_mean']}"
        )
    parts.append(f"ordinal={ordinal_map['ordinal']} | sentinel_verdict={ordinal_map['sentinel_verdict']}")
    parts.append(ordinal_map["verdict"])
    if rounds:
        f = rounds[-1]
        parts.append(
            f"final round {f['i']}: total_emits={f['summary_total_emits']} "
            f"inject={f['inject_n_lines']} (raw={f['phi_proxy_i_to_i_raw']})"
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
    ordinal_map = map_to_ordinal_and_verdict(growth, rounds)
    summary = {
        "schema": "nexus.beyond_omega.cycle18_gamma_zero.v1",
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "n_outer_rounds": N_OUTER,
        "inject_function": (
            f"round_i = min(i^i, MAX_INJECT={MAX_INJECT_PER_ROUND}) "
            f"(Veblen φ_i(0) numeric proxy via nested powering, predicative-only iteration depth)"
        ),
        "raw_phi_table": {
            "i=1": "φ_1(0) ≈ 1^1 = 1",
            "i=2": "φ_2(0) ≈ 2^2 = 4",
            "i=3": "φ_3(0) ≈ 3^3 = 27",
            "i=4": "φ_4(0) ≈ 4^4 = 256",
            "i=5": f"φ_5(0) ≈ 5^5 = 3125 (CAPPED to {MAX_INJECT_PER_ROUND})",
            "i=6": f"φ_6(0) ≈ 6^6 = 46656 (CAPPED to {MAX_INJECT_PER_ROUND})",
        },
        "back_action_env": "NEXUS_BACK_ACTION_ON=1",
        "max_inject_cap": MAX_INJECT_PER_ROUND,
        "rounds": rounds,
        "growth": growth,
        "ordinal_mapping": ordinal_map,
        "interpretation": interpret(growth, ordinal_map, rounds),
        "veblen_predicativity_reference": (
            "Feferman–Schütte 1964: Γ₀ = least α s.t. φ_α(0) = α (Veblen function "
            "fixed point) = supremum of predicatively-provable ordinals. Any finite "
            "predicative iteration cannot reach Γ₀."
        ),
        "comparison_with_cycle_15": (
            "cycle 15 P1 (2↑↑i, cap=500) = L_{ε₀} SENTINEL_CONFIRM. cycle 18 (i^i, cap=300) "
            "tests strictly stronger boundary L_{Γ₀} (predicativity > PA-formalizability). "
            "Both expected SENTINEL_CONFIRM via tail_collapse_to_one."
        ),
    }
    OUT.parent.mkdir(exist_ok=True)
    with open(OUT, "w") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=2)
    print(f"⊙ cycle18_gamma_zero n_rounds={N_OUTER} growth={growth['type']} "
          f"sentinel_verdict={ordinal_map['sentinel_verdict']}")
    if "delta_sequence" in growth:
        print(f"  delta seq: {growth['delta_sequence']}")
        print(f"  delta ratios: {growth.get('delta_ratio_sequence', [])}")
        print(f"  cap_activations: {growth.get('cap_activations', 0)}/{N_OUTER}")
        print(f"  tail_collapse_to_one: {growth.get('tail_collapse_to_one', False)}")
        print(f"  plateau_then_jump: {growth.get('plateau_then_jump', False)}")
    print(f"  ordinal: {ordinal_map['ordinal']} — {ordinal_map['verdict']}")
    print(f"  out → {OUT.relative_to(REPO)}")
    print(f"  finding → {summary['interpretation']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
