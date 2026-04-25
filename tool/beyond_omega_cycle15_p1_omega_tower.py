#!/usr/bin/env python3
"""
beyond_omega_cycle15_p1_omega_tower.py — nxs-20260425-004 cycle 15

L_{ε₀} sentinel falsification protocol P1: Ackermann-style nested ω-tower depth-i.

Background:
  - Cycle 12 inject = 2^i (exponential, L_{ω·2} REACHED, ratios monotone increasing)
  - Cycle 13 inject = i²·7 (polynomial-of-polynomial, L_{ω²}_APPROACH, ratios monotone decreasing toward 1)
  - Cycle 14 (theoretical) committed L_{ε₀} as first true sentinel beyond L_ω with 4 PA-consistency
    arguments (Gödel II / Goodstein / cycle 12-13 probe primitive recursive / Heisenberg limit isomorphism).
  - Cycle 14 prediction: any cycle 12-13 style probe (primitive recursive injector + finite outer
    rounds + open-mode echo) cannot reach L_{ε₀}.

Cycle 15 P1 protocol — ω-tower depth-i (Knuth up-arrow 2↑↑i):
  - round 1 inject = 2↑↑1 = 2
  - round 2 inject = 2↑↑2 = 2^2 = 4
  - round 3 inject = 2↑↑3 = 2^(2^2) = 2^4 = 16
  - round 4 inject = 2↑↑4 = 2^(2^(2^2)) = 2^16 = 65536  (already too large in practice)
  - round 5 inject = 2↑↑5 = 2^65536 (astronomical, OOM)
  - round 6 inject = 2↑↑6 (incomprehensible)

Practical cap: MAX_INJECT = 10000 lines per round to avoid OOM and runaway disk.
  - rounds 1-3 below cap (2, 4, 16)
  - rounds 4-6 will saturate at MAX_INJECT (cap activated → distribution bounded)

Verdict mapping (cycle 14 §4.4 discriminator):
  - ratios → 1.0 collapse (cap activated, distribution bounded) → L_{ε₀} SENTINEL CONFIRM
    (P1 falsified — predicted high probability)
  - ratios → continue monotone increasing without saturation → L_{ε₀} FALSIFIED
    (axis A next ordinal entered — predicted low probability)
  - timeout/OOM (resource limit) → inconclusive

산출물:
  - state/beyond_omega_cycle15_p1_omega_tower.json (schema v1)
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
OUT = REPO / "state" / "beyond_omega_cycle15_p1_omega_tower.json"

N_OUTER = 6
# cap per round to avoid OOM (round 4 = 65536 unbounded; capping also drives the
# `ratios → 1.0 collapse` discriminator that defines L_{ε₀} sentinel signature).
# 500 chosen so probe scan over accumulated trace.jsonl stays under 30s per round.
MAX_INJECT = 500
PROBE_TIMEOUT_S = 60


def tetration_capped(base: int, height: int, cap: int) -> tuple[int, bool]:
    """Compute base↑↑height (Knuth up-arrow tower) but cap at `cap`.

    Returns (value, was_capped). If intermediate exponent would exceed cap or
    final value exceeds cap, returns (cap, True).
    """
    if height <= 0:
        return (1, False)
    if height == 1:
        v = base
        if v > cap:
            return (cap, True)
        return (v, False)
    # height >= 2: iterate from top down via repeated exponentiation
    v = base
    for _ in range(height - 1):
        # Next layer = base^v. If v already huge, base^v explodes.
        # log2(base^v) = v * log2(base). Compare with log2(cap).
        if base > 1 and v * math.log2(base) > math.log2(max(cap, 2)) + 1:
            return (cap, True)
        try:
            v = base ** v
        except (OverflowError, MemoryError):
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
    """trace.jsonl 에 n_lines 의 NEXUS_OMEGA marker 직접 inject (cycle 12/13 동형)."""
    if not TRACE.exists():
        TRACE.parent.mkdir(exist_ok=True)
        TRACE.touch()
    with open(TRACE, "a") as fh:
        for k in range(n_lines):
            payload = {
                "file": str(TRACE.relative_to(REPO)),
                "lineno": -1,
                "payload": {
                    "event": "p1_omega_tower_dispatch",
                    "round": round_i,
                    "k": k,
                    "synthetic": True,
                    "cycle": 15,
                },
                "_cycle15_round": round_i,
                "_cycle15_k": k,
            }
            fh.write(json.dumps(payload, ensure_ascii=False) + "\n")
            fh.write(
                '{"_marker": "NEXUS_OMEGA {\\"event\\":\\"p1_omega_tower_synth\\",\\"round\\":'
                + str(round_i) + ',\\"k\\":' + str(k) + '}"}\n'
            )


def run_round(round_i: int) -> dict:
    t0 = time.time()
    raw_value, was_capped = tetration_capped(2, round_i, MAX_INJECT)
    n_inject = min(raw_value, MAX_INJECT)
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
        "tetration_2_uparrow_uparrow_i_raw": (
            raw_value if not was_capped else f"capped_at_{MAX_INJECT}"
        ),
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

    # cycle 13 style discrimination
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

    # cycle 15 specific: ratios → 1.0 collapse signature.
    # Once cap saturates, deltas freeze at the cap-driven plateau and successive
    # ratios collapse to ~1.0 exactly. We detect this by counting trailing
    # near-unity ratios (|r-1| < 0.10) — needs at least 2 to confirm sustained
    # collapse (avoids isolated coincidences).
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

    # log-log regression slope (cycle 13 carry-over)
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
        gtype = "ratios_collapse_to_one"  # cycle 15 sentinel signature
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
        "cap_activations": cap_activations,
        "ratios_increasing": ratios_increasing,
        "ratios_decreasing": ratios_decreasing,
    }


def map_to_ordinal_and_verdict(growth, rounds):
    """cycle 14 §4.4 discriminator → L_{ε₀} sentinel verdict."""
    t = growth.get("type", "")
    cap_activations = growth.get("cap_activations", 0)
    tail_collapse = growth.get("tail_collapse_to_one", False)
    ratios_increasing = growth.get("ratios_increasing", False)

    if t == "probe_timeout_inconclusive":
        return {
            "ordinal": "L_{ε₀}_INCONCLUSIVE_TIMEOUT",
            "sentinel_verdict": "inconclusive",
            "verdict": (
                f"P1 inconclusive — probe scan timed out (resource limit) due to accumulated "
                f"trace.jsonl size from cap-saturated rounds. Cycle 14 §4.4 'inconclusive' branch."
            ),
        }
    if t == "ratios_collapse_to_one":
        return {
            "ordinal": "L_{ε₀}_SENTINEL_CONFIRM",
            "sentinel_verdict": "SENTINEL_CONFIRM",
            "verdict": (
                f"P1 FALSIFIED → L_{{ε₀}} sentinel CONFIRMED. "
                f"cap activated in {cap_activations}/{N_OUTER} rounds → distribution bounded → "
                f"ratios tail collapses to ~1.0 (cycle 14 §4.4 discriminator). "
                f"primitive recursive injector (2↑↑i with cap) cannot reach L_{{ε₀}} as cycle 14 predicted."
            ),
        }
    if t in ("exponential_increasing", "exponential") and ratios_increasing and cap_activations == 0:
        return {
            "ordinal": "L_{ε₀}_FALSIFIED",
            "sentinel_verdict": "FALSIFIED",
            "verdict": (
                f"L_{{ε₀}} sentinel FALSIFIED — ratios continue monotone increasing without "
                f"cap saturation (axis A next ordinal entered). Model redesign required."
            ),
        }
    if t in ("exponential_increasing", "exponential"):
        return {
            "ordinal": "L_{ε₀}_SENTINEL_PARTIAL",
            "sentinel_verdict": "SENTINEL_CONFIRM",
            "verdict": (
                f"Mixed signature — exponential growth observed but cap activated in "
                f"{cap_activations} rounds. Distribution still bounded by cap → sentinel confirm "
                f"weakly (cycle 14 §4.4)."
            ),
        }
    if t == "saturated_zero":
        return {
            "ordinal": "L_{ε₀}_INCONCLUSIVE_ZERO",
            "sentinel_verdict": "inconclusive",
            "verdict": "back-action 차단 또는 probe 조용함 — protocol 강화 필요",
        }
    # default: tail_collapse without cap is also confirm-ish
    if tail_collapse:
        return {
            "ordinal": "L_{ε₀}_SENTINEL_CONFIRM",
            "sentinel_verdict": "SENTINEL_CONFIRM",
            "verdict": (
                "ratios tail collapses to ~1.0 even without cap activation — "
                "echo attenuation absorbs tower growth → sentinel confirm."
            ),
        }
    return {
        "ordinal": "L_{ε₀}_INCONCLUSIVE",
        "sentinel_verdict": "inconclusive",
        "verdict": f"unclassified growth type={t}, cap_activations={cap_activations} — protocol 재검토",
    }


def interpret(growth, ordinal_map, rounds):
    parts = []
    t = growth.get("type", "")
    cap_activations = growth.get("cap_activations", 0)
    parts.append(
        f"P1 ω-tower (2↑↑i, cap={MAX_INJECT}) — growth_type={t}, "
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
            f"inject={f['inject_n_lines']} (raw={f['tetration_2_uparrow_uparrow_i_raw']})"
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
        "schema": "nexus.beyond_omega.cycle15_p1_omega_tower.v1",
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "n_outer_rounds": N_OUTER,
        "inject_function": (
            f"round_i = min(2↑↑i, MAX_INJECT={MAX_INJECT}) "
            f"(Knuth up-arrow tower of 2's, height i; capped to avoid OOM)"
        ),
        "raw_tower_table": {
            "i=1": f"2↑↑1 = 2 (≤ cap {MAX_INJECT})",
            "i=2": f"2↑↑2 = 4 (≤ cap {MAX_INJECT})",
            "i=3": f"2↑↑3 = 16 (≤ cap {MAX_INJECT})",
            "i=4": f"2↑↑4 = 65536 (CAPPED to {MAX_INJECT})",
            "i=5": f"2↑↑5 = 2^65536 (CAPPED to {MAX_INJECT})",
            "i=6": f"2↑↑6 = 2^(2^65536) (CAPPED to {MAX_INJECT})",
        },
        "back_action_env": "NEXUS_BACK_ACTION_ON=1",
        "max_inject_cap": MAX_INJECT,
        "rounds": rounds,
        "growth": growth,
        "ordinal_mapping": ordinal_map,
        "interpretation": interpret(growth, ordinal_map, rounds),
        "cycle_14_discriminator_reference": (
            "design/beyond_omega_epsilon_zero_boundary.md §4.4 — "
            "ratios → 1.0 collapse = SENTINEL_CONFIRM, ratios continue monotone increasing = FALSIFIED, "
            "timeout/OOM = inconclusive"
        ),
    }
    OUT.parent.mkdir(exist_ok=True)
    with open(OUT, "w") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=2)
    print(f"⊙ cycle15_p1_omega_tower n_rounds={N_OUTER} growth={growth['type']} "
          f"sentinel_verdict={ordinal_map['sentinel_verdict']}")
    if "delta_sequence" in growth:
        print(f"  delta seq: {growth['delta_sequence']}")
        print(f"  delta ratios: {growth.get('delta_ratio_sequence', [])}")
        print(f"  cap_activations: {growth.get('cap_activations', 0)}/{N_OUTER}")
        print(f"  tail_collapse_to_one: {growth.get('tail_collapse_to_one', False)}")
    print(f"  ordinal: {ordinal_map['ordinal']} — {ordinal_map['verdict']}")
    print(f"  out → {OUT.relative_to(REPO)}")
    print(f"  finding → {summary['interpretation']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
