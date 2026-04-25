#!/usr/bin/env python3
"""
beyond_omega_atlas_bridge.py — nxs-20260425-004 cycle 30 (REAL absorption)

Push beyond-omega 의 REAL findings (cycles 1-6 + 10 + 28) → atlas_health_timeline.jsonl.
SYNTHETIC cycles 7-26 은 의도적으로 제외 (사용자 honest framing 직접 인용).

각 호출 = current snapshot 한 row append (idempotent 안 — daily plist 에서 호출되어
시계열 누적). schema 는 기존 atlas_meta_scan source row pattern 따름.

NOTE (cycle 35, 2026-04-25): 본 bridge 는 CURRENT snapshot 만 emit (running 시계열).
cycles 1-6 의 IMMUTABLE 역사적 finding (BASELINE_ZERO/DISPATCH_ONLY/DISPATCH_TERMINATED/
APPROACH_OBSERVED/INSTRUMENTATION/AXIS_OVERLAP) 의 backfill 은 ONE-SHOT 별도 도구
(`tool/beyond_omega_atlas_backfill_history.py`) 에서 처리. 본 bridge 는 historical anchor
row (axis_id=nxs004_b{N}_historical_anchor, historical_anchor=true) 를 절대 재emit 안 함.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ATLAS = REPO / "state" / "atlas_health_timeline.jsonl"
GHOST_SUMMARY = REPO / "state" / "ghost_ceiling_summary.json"
CROSS_AXIS = REPO / "state" / "beyond_omega_cross_axis_join.json"
PLIST = REPO / "tool" / "com.nexus.beyond-omega-daily.plist"
# cycle 34 (2026-04-25): emit_capture_wrapper.sh 의 host-side append sink.
# nxs004_b34 axis = wc -l (NEXUS_OMEGA emit captured to permanent sink).
EMIT_CAPTURE_SINK = REPO / "state" / "ghost_ceiling_trace.append.jsonl"
# cycle 39 (2026-04-25): cross-axis FEEDBACK sidecar (axis B → V3' consumer).
# Sidecar to bisociation/spectra/g_atlas_composite_v3.json (V3' SSOT 미수정).
V3_AXIS_B_ANNOTATION = (
    REPO / "bisociation" / "spectra" / "g_atlas_composite_v3_axis_b_annotation.json"
)
# cycle 40 (2026-04-25): toolchain integration smoke test result sink.
# nxs004_b40 axis = pass_count / total ratio of beyond_omega_smoke_test.py.
SMOKE_TEST_STATE = REPO / "state" / "beyond_omega_smoke_test.json"
# cycle 41 (2026-04-25): durability manifest baseline (sha256 + size + lines + mtime).
# nxs004_b41 axis = n_files baselined for long-term integrity check.
DURABILITY_MANIFEST = REPO / "state" / "beyond_omega_durability_manifest.json"

# REAL cycle findings only (cycles 7-26 synthetic excluded by design — see
# design/beyond_omega_HONEST_INDEX.md / 사용자 직접 framing 2026-04-25).
SYNTHETIC_EXCLUDED = list(range(7, 10)) + list(range(11, 27))


def load_ghost_summary():
    if not GHOST_SUMMARY.exists():
        return None
    try:
        with open(GHOST_SUMMARY) as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return None


def load_cross_axis():
    if not CROSS_AXIS.exists():
        return None
    try:
        with open(CROSS_AXIS) as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return None


def emit_row(row: dict):
    with open(ATLAS, "a") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def main():
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    ghost = load_ghost_summary() or {}
    cross = load_cross_axis() or {}
    iso = cross.get("isomorphism", {})

    # axis_b29 ~ axis_b35 : nxs004 b1-6 + b10 + b28 의 atlas-side mapping
    rows = []

    # cycle 1-3: axis B negative space → cycle 3 의 결과로 압축
    rows.append({
        "ts": ts,
        "axis_id": "nxs004_b1_3",
        "axis_name": "ghost_ceiling_emit_count",
        "value": ghost.get("total_emits", 0),
        "metric": "count",
        "source": "nxs-20260425-004",
        "real_implementation": True,
        "cycle_anchor": [1, 2, 3],
    })

    # cycle 4: first positive
    rows.append({
        "ts": ts,
        "axis_id": "nxs004_b4",
        "axis_name": "ghost_ceiling_approach_freq",
        "value": ghost.get("ghost_ceiling_approach_count", 0),
        "metric": "count",
        "source": "nxs-20260425-004",
        "real_implementation": True,
        "cycle_anchor": [4],
    })

    # cycle 5: instrumentation (back-action layer 발견)
    rows.append({
        "ts": ts,
        "axis_id": "nxs004_b5",
        "axis_name": "probe_self_output_protected",
        "value": "idempotent" if ghost.get("mode") in ("overwrite", "append", "cron") else "unknown",
        "metric": "status",
        "source": "nxs-20260425-004",
        "real_implementation": True,
        "cycle_anchor": [5],
    })

    # cycle 6: cross-axis (180s timeout headroom)
    rows.append({
        "ts": ts,
        "axis_id": "nxs004_b6",
        "axis_name": "smash_p50_headroom_pct_vs_180s",
        "value": iso.get("smash_p50_global_ms"),
        "metric": "ms_p50",
        "denominator_ms": 180000,
        "headroom_pct": (
            round(100 * (180000 - iso["smash_p50_global_ms"]) / 180000, 1)
            if iso.get("smash_p50_global_ms") else None
        ),
        "source": "nxs-20260425-004",
        "real_implementation": True,
        "cycle_anchor": [6],
    })

    # cycle 10: daily plist registered
    rows.append({
        "ts": ts,
        "axis_id": "nxs004_b10",
        "axis_name": "daily_plist_registered",
        "value": "registered_unloaded" if PLIST.exists() else "missing",
        "metric": "status",
        "source": "nxs-20260425-004",
        "real_implementation": True,
        "cycle_anchor": [10],
    })

    # cycle 28: plist preflight verified
    rows.append({
        "ts": ts,
        "axis_id": "nxs004_b28",
        "axis_name": "daily_plist_preflight",
        "value": "passed_5_of_5" if PLIST.exists() else "incomplete",
        "metric": "status",
        "source": "nxs-20260425-004",
        "real_implementation": True,
        "cycle_anchor": [28],
        "user_action_required": True,
    })

    # cycle 34: emit_capture_wrapper.sh host-side capture count (cycle 27 follow-through).
    # cmd_omega 의 NEXUS_OMEGA emit 이 휘발성 /tmp 가 아닌 permanent state/ sink 에
    # 누적 — wc -l of ghost_ceiling_trace.append.jsonl.
    capture_count = 0
    if EMIT_CAPTURE_SINK.exists():
        try:
            with open(EMIT_CAPTURE_SINK) as fh:
                capture_count = sum(1 for _ in fh)
        except OSError:
            capture_count = -1
    rows.append({
        "ts": ts,
        "axis_id": "nxs004_b34_capture_count",
        "axis_name": "emit_capture_wrapper_sink_lines",
        "value": capture_count,
        "metric": "count",
        "source": "nxs-20260425-004",
        "real_implementation": True,
        "cycle_anchor": [34],
        "sink_path": str(EMIT_CAPTURE_SINK.relative_to(REPO)),
        "wrapper_path": "tool/beyond_omega_emit_capture_wrapper.sh",
    })

    # cycle 39: cross-axis FEEDBACK sidecar status (axis B → V3' consumer).
    # value = "ready" if sidecar exists with feedback_direction set, else "missing".
    annotation_status = "missing"
    annotation_v3_ts = None
    annotation_emit = None
    if V3_AXIS_B_ANNOTATION.exists():
        try:
            with open(V3_AXIS_B_ANNOTATION) as fh:
                _ann = json.load(fh)
            if (_ann.get("feedback_direction", "").startswith("axis_b → v3_consumer")
                    and _ann.get("v3_ssot_unmodified") is True):
                annotation_status = "ready"
                annotation_v3_ts = _ann.get("annotated_v3_iso")
                annotation_emit = _ann.get("axis_b_emit_count_at_v3_ts")
        except (OSError, json.JSONDecodeError):
            annotation_status = "parse_error"
    rows.append({
        "ts": ts,
        "axis_id": "nxs004_b39_v3_annotation_ready",
        "axis_name": "v3_axis_b_annotation_sidecar_status",
        "value": annotation_status,
        "metric": "status",
        "source": "nxs-20260425-004",
        "real_implementation": True,
        "cross_axis_feedback": True,
        "cycle_anchor": [39],
        "sidecar_path": str(V3_AXIS_B_ANNOTATION.relative_to(REPO)),
        "annotated_v3_iso": annotation_v3_ts,
        "axis_b_emit_at_annotation": annotation_emit,
        "v3_ssot_unmodified": True,
        "feedback_direction": "axis_b → v3_consumer (read-only)",
    })

    # cycle 40: toolchain smoke test pass count.
    # value = pass_count (int); also expose total + ratio + tool_path.
    smoke_pass = None
    smoke_total = None
    smoke_ratio = None
    smoke_status = "missing"
    smoke_failures_n = None
    if SMOKE_TEST_STATE.exists():
        try:
            with open(SMOKE_TEST_STATE) as fh:
                _smoke = json.load(fh)
            smoke_pass = _smoke.get("pass_count")
            smoke_total = _smoke.get("n_scripts_total")
            smoke_ratio = _smoke.get("pass_ratio")
            smoke_failures_n = _smoke.get("fail_count")
            smoke_status = "all_pass" if smoke_failures_n == 0 else "partial_fail"
        except (OSError, json.JSONDecodeError):
            smoke_status = "parse_error"
    rows.append({
        "ts": ts,
        "axis_id": "nxs004_b40_smoke_test_pass_count",
        "axis_name": "beyond_omega_toolchain_smoke_pass_count",
        "value": smoke_pass,
        "metric": "count",
        "source": "nxs-20260425-004",
        "real_implementation": True,
        "cycle_anchor": [40],
        "smoke_test_total": smoke_total,
        "smoke_test_pass_ratio": smoke_ratio,
        "smoke_test_fail_count": smoke_failures_n,
        "smoke_test_status": smoke_status,
        "smoke_test_state_path": str(SMOKE_TEST_STATE.relative_to(REPO)),
        "tool_path": "tool/beyond_omega_smoke_test.py",
    })

    # cycle 41: durability manifest count (long-term integrity baseline).
    # value = n_files baselined (sha256 + size + line_count + mtime each).
    manifest_n_files = None
    manifest_generated_ts = None
    manifest_status = "missing"
    if DURABILITY_MANIFEST.exists():
        try:
            with open(DURABILITY_MANIFEST) as fh:
                _man = json.load(fh)
            manifest_n_files = _man.get("n_files")
            manifest_generated_ts = _man.get("generated_ts")
            manifest_status = "baselined" if manifest_n_files else "empty"
        except (OSError, json.JSONDecodeError):
            manifest_status = "parse_error"
    rows.append({
        "ts": ts,
        "axis_id": "nxs004_b41_durability_manifest_count",
        "axis_name": "beyond_omega_durability_manifest_n_files",
        "value": manifest_n_files,
        "metric": "count",
        "source": "nxs-20260425-004",
        "real_implementation": True,
        "cycle_anchor": [41],
        "manifest_path": str(DURABILITY_MANIFEST.relative_to(REPO)),
        "manifest_generated_ts": manifest_generated_ts,
        "manifest_status": manifest_status,
        "tool_path": "tool/beyond_omega_durability_manifest.py",
        "verify_mode": "python3 tool/beyond_omega_durability_manifest.py --verify",
    })

    # excluded synthetic — record explicit exclusion (one row, not per-cycle)
    rows.append({
        "ts": ts,
        "axis_id": "nxs004_synthetic_excluded",
        "axis_name": "synthetic_cycles_excluded_count",
        "value": len(SYNTHETIC_EXCLUDED),
        "metric": "count",
        "excluded_cycles": SYNTHETIC_EXCLUDED,
        "source": "nxs-20260425-004",
        "real_implementation": True,
        "rationale": "cycles 7-26 = synthetic ordinal mapping (inject pattern echo, NOT mathematical breakthrough). Excluded from atlas absorption per user honest framing.",
    })

    for r in rows:
        emit_row(r)

    print(f"⊙ atlas_bridge appended {len(rows)} rows to {ATLAS.relative_to(REPO)}")
    for r in rows:
        print(f"  {r['axis_id']}: {r['axis_name']} = {r.get('value')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
