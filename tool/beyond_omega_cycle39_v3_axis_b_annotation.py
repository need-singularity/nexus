#!/usr/bin/env python3
"""
beyond_omega_cycle39_v3_axis_b_annotation.py — nxs-20260425-004 cycle 39

Cross-axis FEEDBACK (axis B → V3' / nxs-002 consumers).

Cycle 6 (cross_axis_join) 의 isomorphism 은 axis B → axis A 방향의 read.
Cycle 30-32 atlas bridge 는 axis B → atlas push.
Cycle 39 = OTHER 방향 — axis B 의 emit/approach signal 을 V3' SSOT consumer
(drill, dashboard, paper_trigger gate) 가 read 가능하도록 sidecar annotation.

ZERO-DISRUPTION 원칙:
- bisociation/spectra/g_atlas_composite_v3.json (V3' SSOT) 은 절대 수정 안 함
  (nxs-002 영역, parallel session 가능성).
- Sidecar file 으로만 emit: bisociation/spectra/g_atlas_composite_v3_axis_b_annotation.json
- Consumer 는 본 파일을 read or ignore (optional context).

출력 schema (sidecar):
  {
    "schema": "nxs_004.cycle39.v3_axis_b_annotation.v1",
    "annotated_v3_ts": <V3' snapshot ts (epoch)>,
    "annotated_v3_iso": <V3' snapshot ts ISO>,
    "axis_b_emit_count_at_v3_ts": <int, current snapshot estimate>,
    "axis_b_approach_count_at_v3_ts": <int, current snapshot estimate>,
    "axis_b_capture_sink_lines": <int, ghost_ceiling_trace.append.jsonl line count>,
    "feedback_direction": "axis_b → v3_consumer (read-only annotation, zero-disruption)",
    "source": "nxs-20260425-004 cycle 39",
    "ts": <ISO now>
  }
"""
from __future__ import annotations

import json
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GHOST_SUMMARY = REPO / "state" / "ghost_ceiling_summary.json"
V3_SNAPSHOT = REPO / "bisociation" / "spectra" / "g_atlas_composite_v3.json"
EMIT_CAPTURE_SINK = REPO / "state" / "ghost_ceiling_trace.append.jsonl"
OUT = REPO / "bisociation" / "spectra" / "g_atlas_composite_v3_axis_b_annotation.json"


def _read_json(path: Path):
    if not path.exists():
        return None
    try:
        with open(path) as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return None


def _count_lines(path: Path) -> int:
    if not path.exists():
        return 0
    try:
        with open(path) as fh:
            return sum(1 for _ in fh)
    except OSError:
        return -1


def main():
    ghost = _read_json(GHOST_SUMMARY) or {}
    v3 = _read_json(V3_SNAPSHOT) or {}

    v3_ts = v3.get("ts")
    v3_iso = (
        time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(int(v3_ts)))
        if v3_ts else None
    )

    annotation = {
        "schema": "nxs_004.cycle39.v3_axis_b_annotation.v1",
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "annotated_v3_ts": v3_ts,
        "annotated_v3_iso": v3_iso,
        "annotated_v3_composite_v3_prime": v3.get("composite_v3_prime"),
        "annotated_v3_paper_trigger_passed_v3_prime": v3.get(
            "paper_trigger_passed_v3_prime"
        ),
        "axis_b_emit_count_at_v3_ts": ghost.get("total_emits", 0),
        "axis_b_approach_count_at_v3_ts": ghost.get(
            "ghost_ceiling_approach_count", 0
        ),
        "axis_b_capture_sink_lines": _count_lines(EMIT_CAPTURE_SINK),
        "axis_b_dispatch_count": (ghost.get("events", {}) or {}).get(
            "dispatch", 0
        ),
        "axis_b_complete_count": (ghost.get("events", {}) or {}).get(
            "complete", 0
        ),
        "axis_b_summary_ts": ghost.get("ts"),
        "feedback_direction": (
            "axis_b → v3_consumer (read-only annotation, zero-disruption)"
        ),
        "v3_ssot_unmodified": True,
        "source": "nxs-20260425-004 cycle 39",
        "consumers_can_read": [
            "cli/run.hexa cmd_omega dashboard pre-snapshot hook (line ~4043)",
            "tool/nxs_002_axiom_decision.hexa paper_trigger gate",
            "drill cycles (optional cross-axis context)"
        ],
        "estimation_caveat": (
            "axis_b counts are CURRENT snapshot, not exactly aligned to "
            "V3' snapshot ts. Cycle 6 cross_axis_join.py performs hour-bucket "
            "join for ts-aligned interrogation. This sidecar is a coarser "
            "annotation suitable for dashboard glance."
        )
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w") as fh:
        json.dump(annotation, fh, ensure_ascii=False, indent=2)

    print(
        f"⊙ v3_axis_b_annotation v3_ts={v3_iso} "
        f"emit={annotation['axis_b_emit_count_at_v3_ts']} "
        f"approach={annotation['axis_b_approach_count_at_v3_ts']} "
        f"capture_sink={annotation['axis_b_capture_sink_lines']}"
    )
    print(f"  out → {OUT.relative_to(REPO)}")
    print(f"  feedback → {annotation['feedback_direction']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
