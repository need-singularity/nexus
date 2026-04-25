#!/usr/bin/env python3
"""
beyond_omega_atlas_backfill_history.py — nxs-20260425-004 cycle 35 (one-shot historical backfill)

Push cycles 1-6 의 IMMUTABLE 역사적 finding 값을 atlas_health_timeline.jsonl 의
historical anchor row 로 한 번 backfill. cycle 30 의 daily current snapshot bridge 와
명확히 구분됨 (historical_anchor=true 마커).

Source = state/proposals/inventory.json 의 nxs-20260425-004 entry 안
`cycle_{1..6}_finding_2026_04_25` block 들. 각 block 에서 finding 값 추출 후 1 anchor row 발행.

Idempotent: 본 도구는 ONE-SHOT — 재실행 시 중복 emit 방지 위해 caller 가 책임 (atlas_health_timeline.jsonl 안
historical_anchor=true + axis_id=nxs004_b{N}_historical_anchor + source=nxs-20260425-004 조합으로 dedup 가능).
실수로 여러 번 실행해도 row 가 중복될 뿐 mathematical content 동일.

cycle 30 bridge (beyond_omega_atlas_bridge.py) 와의 관계:
- bridge       = current snapshot, daily plist 에서 매번 emit, 시계열 누적
- 본 backfill   = historical anchor, ONE-SHOT, immutable finding 값 (cycle 1-6 시점)
"""
from __future__ import annotations

import json
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ATLAS = REPO / "state" / "atlas_health_timeline.jsonl"
INVENTORY = REPO / "state" / "proposals" / "inventory.json"

# Commit timestamps (git log %aI, +09:00 KST → UTC 변환)
# cycle 1: a2f2e908  2026-04-25T19:06:21+09:00 → 10:06:21Z
# cycle 2: HEAD just before rename ae11cb06    2026-04-25T19:31:35+09:00 → 10:31:35Z (proxy)
# cycle 3: 0475eef4  2026-04-25T19:43:06+09:00 → 10:43:06Z
# cycle 4: 3e73e8a6  2026-04-25T19:50:57+09:00 → 10:50:57Z
# cycle 5: 44d47a25  2026-04-25T19:57:32+09:00 → 10:57:32Z
# cycle 6: 1465ff78  2026-04-25T20:18:35+09:00 → 11:18:35Z
CYCLE_COMMIT_TS = {
    1: "2026-04-25T10:06:21Z",
    2: "2026-04-25T10:31:35Z",
    3: "2026-04-25T10:43:06Z",
    4: "2026-04-25T10:50:57Z",
    5: "2026-04-25T10:57:32Z",
    6: "2026-04-25T11:18:35Z",
}


def load_entry():
    with open(INVENTORY) as fh:
        inv = json.load(fh)
    for e in inv.get("entries", []):
        if e.get("id") == "nxs-20260425-004":
            return e
    raise SystemExit("nxs-20260425-004 entry not found in inventory.json")


def emit_row(row: dict):
    with open(ATLAS, "a") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def build_anchor_rows(entry: dict):
    """Extract historical findings from cycle 1-6 blocks."""
    rows = []

    # cycle 1: BASELINE_ZERO — files_scanned=453, total_emits=0
    c1 = entry.get("cycle_1_first_finding_2026_04_25", {})
    rows.append({
        "ts": CYCLE_COMMIT_TS[1],
        "axis_id": "nxs004_b1_historical_anchor",
        "axis_name": "ghost_ceiling_emit_count_anchor",
        "value": 0,
        "metric": "count",
        "source": "nxs-20260425-004",
        "real_implementation": True,
        "historical_anchor": True,
        "cycle_anchor": [1],
        "finding_summary": "BASELINE_ZERO — files_scanned=453, total_emits=0 (axis B start, falsified by cycle 2 over-narrow scan)",
        "raw_result": c1.get("result", ""),
    })

    # cycle 2: DISPATCH_ONLY — files_scanned=476, total_emits=4 (all dispatch)
    c2 = entry.get("cycle_2_finding_2026_04_25", {})
    rows.append({
        "ts": CYCLE_COMMIT_TS[2],
        "axis_id": "nxs004_b2_historical_anchor",
        "axis_name": "ghost_ceiling_emit_count_anchor",
        "value": 4,
        "metric": "count",
        "source": "nxs-20260425-004",
        "real_implementation": True,
        "historical_anchor": True,
        "cycle_anchor": [2],
        "finding_summary": "DISPATCH_ONLY — files_scanned=476, total_emits=4 (all dispatch axes=0 path=drill, 4 /tmp/nexus_omega_hive_statusline_v{2,3,4,5}.log)",
        "dispatch_count": 4,
        "complete_count": 0,
        "approach_count": 0,
        "raw_result": c2.get("result", ""),
    })

    # cycle 3: DISPATCH_TERMINATED — 4/4 termination markers, rc=143 (1)
    c3 = entry.get("cycle_3_finding_2026_04_25", {})
    rows.append({
        "ts": CYCLE_COMMIT_TS[3],
        "axis_id": "nxs004_b3_historical_anchor",
        "axis_name": "dispatch_terminated_ratio_anchor",
        "value": 1.0,  # 4/4 loose marker
        "metric": "ratio",
        "source": "nxs-20260425-004",
        "real_implementation": True,
        "historical_anchor": True,
        "cycle_anchor": [3],
        "finding_summary": "DISPATCH_TERMINATED — 4/4 dispatches followed by termination marker (kill-after=4 ubiquitous), strict SIGTERM rc=143 = 1/4 (25%). 180s timeout invariant 발견.",
        "termination_markers": {"kill-after": 4, "Terminated": 1, "external_fallback": 1, "rc=143": 1, "retry exhausted": 1},
        "raw_result": c3.get("result", ""),
    })

    # cycle 4: APPROACH_OBSERVED — first positive, axes=3 path=chain, approach=1
    c4 = entry.get("cycle_4_finding_2026_04_25", {})
    rows.append({
        "ts": CYCLE_COMMIT_TS[4],
        "axis_id": "nxs004_b4_historical_anchor",
        "axis_name": "ghost_ceiling_approach_freq_anchor",
        "value": 1,
        "metric": "count",
        "source": "nxs-20260425-004",
        "real_implementation": True,
        "historical_anchor": True,
        "cycle_anchor": [4],
        "finding_summary": "★ APPROACH_OBSERVED — first positive measurement of axis B. dispatch=1 approach=1 complete=1 elapsed=2s rc=0, axes=3 path=chain (engines_multi+multi_variant+multi_seed = L4 surge, L_ω 근접 신호).",
        "axes": 3,
        "path": "chain",
        "raw_result": c4.get("result", ""),
    })

    # cycle 5: INSTRUMENTATION + MEASUREMENT BACK-ACTION — probe v4 cron-able, idempotent
    c5 = entry.get("cycle_5_finding_2026_04_25", {})
    rows.append({
        "ts": CYCLE_COMMIT_TS[5],
        "axis_id": "nxs004_b5_historical_anchor",
        "axis_name": "probe_self_output_protected_anchor",
        "value": "idempotent",
        "metric": "status",
        "source": "nxs-20260425-004",
        "real_implementation": True,
        "historical_anchor": True,
        "cycle_anchor": [5],
        "finding_summary": "INSTRUMENTATION + MEASUREMENT BACK-ACTION — probe v4 (--append + --cron + idempotent). pre-fix: emits +6~7 누적 self-feedback bug, post-fix: SELF_OUTPUTS skip → new=0 idempotent. quantum measurement back-action isomorphism.",
        "raw_result": c5.get("result", ""),
    })

    # cycle 6: AXIS_OVERLAP + HEADROOM — smash_p50_global_ms=83258 (180s 의 46.3%)
    c6 = entry.get("cycle_6_finding_2026_04_25", {})
    metrics_6 = c6.get("join_metrics", {})
    rows.append({
        "ts": CYCLE_COMMIT_TS[6],
        "axis_id": "nxs004_b6_historical_anchor",
        "axis_name": "smash_p50_headroom_pct_vs_180s_anchor",
        "value": metrics_6.get("smash_p50_global_ms", 83258),
        "metric": "ms_p50",
        "denominator_ms": 180000,
        "headroom_pct": 53.7,  # 100 - 46.3
        "source": "nxs-20260425-004",
        "real_implementation": True,
        "historical_anchor": True,
        "cycle_anchor": [6],
        "finding_summary": "AXIS_OVERLAP + TIMEOUT_HEADROOM_DISTRIBUTION — overlap=3/6 (50%), smash_p50=83258ms (180s 의 46.3%, 53.7% headroom), smash_max history=183012ms (180s 의 101.7% 초과). cycle 3 의 100% SIGTERM 가 RIGHT-TAIL SIGTERM 으로 refined.",
        "overlap_ratio": metrics_6.get("overlap_ratio", 0.5),
        "smash_max_history_ms": 183012,
        "raw_result": c6.get("result", ""),
    })

    return rows


def main():
    entry = load_entry()
    rows = build_anchor_rows(entry)

    # baseline line count
    before = sum(1 for _ in open(ATLAS)) if ATLAS.exists() else 0

    for r in rows:
        emit_row(r)

    after = sum(1 for _ in open(ATLAS))
    delta = after - before

    print(f"⊙ atlas_backfill_history appended {len(rows)} historical anchor rows to {ATLAS.relative_to(REPO)}")
    print(f"  atlas_health_timeline.jsonl: {before} → {after} ({delta:+d})")
    for r in rows:
        print(f"  {r['axis_id']}: {r['axis_name']} = {r.get('value')} (ts={r['ts']})")

    # sanity
    assert delta == len(rows), f"line count delta {delta} != emitted {len(rows)}"
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
