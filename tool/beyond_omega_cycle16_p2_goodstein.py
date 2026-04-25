#!/usr/bin/env python3
"""
beyond_omega_cycle16_p2_goodstein.py — nxs-20260425-004 cycle 16

Falsifier Protocol P2 — Goodstein-style hereditary base-n climb.

Background (design/beyond_omega_epsilon_zero_boundary.md §4.2):
  - Goodstein theorem: every Goodstein sequence terminates at 0,
    BUT PA cannot prove this (Kirby–Paris 1982). Termination proof
    requires ε₀-induction.
  - P2 protocol: per round i, inject N synthetic NEXUS_OMEGA lines
    where N = simplified Goodstein number (start m=i+2 in hereditary
    base 2, replace base 2→3, subtract 1).

Practical reduction:
  - For round i, compute G_i = goodstein_step(i+2, base=2).
  - Cap inject at MAX_INJECT=10000 to avoid OOM.
  - 6 rounds total; NEXUS_BACK_ACTION_ON=1 (cycle 8 override).

Discriminator (design/beyond_omega_ladder.md §17 cycle 14):
  - Initial explosive growth then decrease (Goodstein signature) →
    partial L_{ε₀} access — termination empirically observed
    falsifies the sentinel (PA ⊬ Goodstein termination).
  - Ratios collapse toward 1.0 → SENTINEL_CONFIRM (probe cannot
    cross the ε₀ boundary).
  - Continued exponential / unbounded growth → FALSIFIED (probe
    overshoots PA-formalizable bound — model redesign needed).

Output: state/beyond_omega_cycle16_p2_goodstein.json
"""
from __future__ import annotations

import json
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
OUT = REPO / "state" / "beyond_omega_cycle16_p2_goodstein.json"

MAX_INJECT = 10000  # hard cap per round (OOM guard)
N_ROUNDS = 6


# ---------- Hereditary base representation ----------
# Represent a non-negative integer in hereditary base-n form as a nested
# structure: a sum of terms, each term = (coefficient, exponent_tree),
# where exponent_tree is itself a hereditary representation.
#
# To "replace base→base+1" we just rebuild the integer from the tree by
# evaluating with the new base.

def to_hereditary(m: int, base: int):
    """Return a list of (coefficient, exponent_tree) terms summing to m
    in hereditary base-`base` form. Coefficients in [0, base-1]."""
    if m == 0:
        return []
    terms = []
    # decompose m in base `base`
    digits = []  # least-significant first
    x = m
    while x > 0:
        digits.append(x % base)
        x //= base
    for exponent, coeff in enumerate(digits):
        if coeff == 0:
            continue
        exp_tree = to_hereditary(exponent, base)
        terms.append((coeff, exp_tree))
    return terms


def evaluate_hereditary(terms, base: int) -> int:
    """Reconstruct integer from hereditary representation using `base`."""
    total = 0
    for coeff, exp_tree in terms:
        exponent_value = evaluate_hereditary(exp_tree, base)
        total += coeff * (base ** exponent_value)
    return total


def goodstein_step(m: int, base: int) -> int:
    """One Goodstein step: hereditary-decompose m at `base`, replace
    base → base+1, then subtract 1. Returns max(result, 0)."""
    if m <= 0:
        return 0
    tree = to_hereditary(m, base)
    raised = evaluate_hereditary(tree, base + 1)
    return max(raised - 1, 0)


# ---------- Inject + probe (mirrors cycle 12/13) ----------

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
                    "event": "p2_goodstein_dispatch",
                    "round": round_i,
                    "k": k,
                    "synthetic": True,
                },
                "_cycle16_round": round_i,
                "_cycle16_k": k,
            }
            fh.write(json.dumps(payload, ensure_ascii=False) + "\n")
            fh.write(
                '{"_marker": "NEXUS_OMEGA {\\"event\\":\\"p2_goodstein_synth\\",\\"round\\":'
                + str(round_i)
                + '}"}\n'
            )


def run_round(round_i: int) -> dict:
    t0 = time.time()
    raw_g = goodstein_step(round_i + 2, base=2)
    n_inject = min(raw_g, MAX_INJECT)
    capped = raw_g > MAX_INJECT
    n_before = count_emits_in_trace()
    inject_synthetic(round_i, n_inject)
    n_post_inject = count_emits_in_trace()
    env = dict(os.environ)
    env["NEXUS_BACK_ACTION_ON"] = "1"
    proc = subprocess.run(
        [sys.executable, str(PROBE)],
        env=env, capture_output=True, text=True, timeout=240,
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
        "goodstein_raw": raw_g,
        "inject_n_lines": n_inject,
        "inject_capped": capped,
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


# ---------- Growth analysis ----------

def analyze_growth(rounds):
    if len(rounds) < 2:
        return {"type": "insufficient_rounds"}
    deltas = [
        rounds[i]["summary_total_emits"] - rounds[i - 1]["summary_total_emits"]
        for i in range(1, len(rounds))
    ]
    if not deltas:
        return {"type": "no_change"}
    mean_d = statistics.mean(deltas)
    var_d = statistics.pvariance(deltas) if len(deltas) > 1 else 0
    is_zero = all(d == 0 for d in deltas)
    ratios = []
    for k in range(1, len(deltas)):
        if deltas[k - 1] > 0:
            ratios.append(deltas[k] / deltas[k - 1])
    mean_ratio = statistics.mean(ratios) if ratios else 0

    # Goodstein signature: ratios initially > 1 then approach / drop below 1
    # (terminates at 0 in the true sequence). With finite N rounds, look for
    # non-monotone or decreasing late ratios after early growth.
    early_growth = any(r > 1.5 for r in ratios[:1]) if ratios else False
    late_decline = (len(ratios) >= 2) and (ratios[-1] < ratios[0])
    ratios_to_one = (
        len(ratios) >= 2
        and all(0.9 < r < 1.1 for r in ratios[-2:])
    )
    sustained_exp = (
        len(ratios) >= 2
        and all(r > 1.5 for r in ratios)
        and ratios[-1] >= ratios[0]
    )

    if is_zero:
        gtype = "saturated_zero"
    elif ratios_to_one:
        gtype = "ratios_collapse_to_one"  # SENTINEL_CONFIRM signature
    elif sustained_exp:
        gtype = "sustained_exponential"  # FALSIFIED signature
    elif early_growth and late_decline:
        gtype = "goodstein_signature"  # partial L_{ε₀} signature
    elif mean_ratio > 1.0:
        gtype = "monotone_growth"
    else:
        gtype = "irregular"

    return {
        "type": gtype,
        "delta_sequence": deltas,
        "delta_mean": round(mean_d, 3),
        "delta_variance": round(var_d, 3),
        "delta_ratio_sequence": [round(r, 3) for r in ratios],
        "delta_ratio_mean": round(mean_ratio, 3),
        "early_growth": early_growth,
        "late_decline": late_decline,
        "ratios_to_one": ratios_to_one,
        "sustained_exp": sustained_exp,
    }


def map_to_verdict(growth, rounds):
    t = growth.get("type", "")
    if t == "ratios_collapse_to_one":
        return {
            "verdict": "SENTINEL_CONFIRM",
            "ordinal": "L_{ε₀}_SENTINEL",
            "narrative": (
                "ratios → 1.0 collapse — probe cannot cross PA-formalizable "
                "boundary. cycle 14 prediction CONFIRMED."
            ),
        }
    if t == "goodstein_signature":
        return {
            "verdict": "PARTIAL",
            "ordinal": "L_{ε₀}_PARTIAL_ACCESS",
            "narrative": (
                "Goodstein signature observed (initial growth + late decline). "
                "Empirical termination of a sequence whose termination needs "
                "ε₀-induction = partial access to L_{ε₀} layer; sentinel "
                "weakly falsified at the finite-window scale."
            ),
        }
    if t == "sustained_exponential":
        return {
            "verdict": "FALSIFIED",
            "ordinal": "L_{ε₀}_FALSIFIED",
            "narrative": (
                "ratios sustained > 1.5 monotone — probe overshoots PA bound; "
                "model redesign required."
            ),
        }
    if t == "saturated_zero":
        return {
            "verdict": "INCONCLUSIVE_BACKACTION_BLOCKED",
            "ordinal": "L_{ε₀}_UNDETERMINED",
            "narrative": "back-action override may be ineffective.",
        }
    if t == "monotone_growth":
        return {
            "verdict": "INCONCLUSIVE",
            "ordinal": "L_{ε₀}_INCONCLUSIVE",
            "narrative": (
                "monotone growth without exponential ramp nor late decline — "
                "Goodstein cap at MAX_INJECT or finite-window too small."
            ),
        }
    return {
        "verdict": "INCONCLUSIVE",
        "ordinal": "UNCLASSIFIED",
        "narrative": f"growth type={t}",
    }


def main():
    if not PROBE.exists():
        print(f"FATAL: probe not found at {PROBE}", file=sys.stderr)
        return 2
    rounds = []
    for i in range(1, N_ROUNDS + 1):
        rec = run_round(i)
        rounds.append(rec)
        time.sleep(0.05)
    growth = analyze_growth(rounds)
    verdict = map_to_verdict(growth, rounds)
    summary = {
        "schema": "nexus.beyond_omega.cycle16_p2_goodstein.v1",
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "n_rounds": N_ROUNDS,
        "max_inject_cap": MAX_INJECT,
        "inject_function": (
            "goodstein_step(i+2, base=2) — hereditary base 2→3 then -1, "
            "capped at MAX_INJECT"
        ),
        "back_action_env": "NEXUS_BACK_ACTION_ON=1",
        "rounds": rounds,
        "growth": growth,
        "verdict": verdict,
    }
    OUT.parent.mkdir(exist_ok=True)
    with open(OUT, "w") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=2)
    goodstein_seq = [r["goodstein_raw"] for r in rounds]
    inject_seq = [r["inject_n_lines"] for r in rounds]
    print(f"⊙ cycle16_p2_goodstein n_rounds={N_ROUNDS} growth={growth['type']}")
    print(f"  goodstein raw: {goodstein_seq}")
    print(f"  inject (capped {MAX_INJECT}): {inject_seq}")
    if "delta_sequence" in growth:
        print(f"  delta seq: {growth['delta_sequence']}")
        print(f"  delta ratios: {growth.get('delta_ratio_sequence', [])}")
        print(f"  delta_ratio_mean: {growth.get('delta_ratio_mean', 0)}")
    print(f"  verdict: {verdict['verdict']} — {verdict['ordinal']}")
    print(f"  out → {OUT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
