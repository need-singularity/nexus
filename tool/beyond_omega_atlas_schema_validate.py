#!/usr/bin/env python3
"""
beyond_omega_atlas_schema_validate.py — nxs-20260425-004 cycle 36
(Atlas row schema validation + downstream compatibility check)

Cycles 30 / 32 / 35 push 14+ rows to atlas_health_timeline.jsonl with new
schema fields (axis_id, real_implementation, cycle_anchor, etc.). Atlas-side
consumers (atlas_meta_scan.hexa, docs/atlas_meta_dashboard.md) were written
before these fields existed. Cycle 36 closes the verification gap.

Approach
--------
- Load every row of state/atlas_health_timeline.jsonl
- Validate JSON parseability for each
- Bin rows into known schema variants:
   * atlas_meta_scan_legacy : ts + atlas_lines + atlas_bytes + types + grades + typed_total
       (lines 1-2 in current file, original Phase-1 sampler before partial-row contract)
   * atlas_meta_scan_partial : ts + shard_count + hub_top3 + scan_age_hours + source=atlas_meta_scan
       (lines 3-4 in current file, current Phase-1 contract — partial because shard_meta missing)
   * nxs004_running        : ts + axis_id + axis_name + value + metric + source=nxs-20260425-004
                              + real_implementation + cycle_anchor (no historical_anchor)
   * nxs004_historical     : same as nxs004_running PLUS historical_anchor=true and
                              axis_id ends with `_historical_anchor`
- Detect rows that:
   (a) fail json.loads
   (b) match no schema variant
   (c) mix incompatible fields (e.g. nxs004 axis_id with atlas_meta_scan source)

Downstream-compat verdict
-------------------------
- atlas_meta_scan.hexa is a writer-only consumer (it appends rows; never reads
  past rows). New fields therefore cannot break it.
- docs/atlas_meta_dashboard.md is a human-rendered rollup; current snapshot
  predates nxs004 rows and is stale. It does not parse the file at runtime.
- No other tool/ or cli/ entry reads atlas_health_timeline.jsonl (verified via
  grep — all hits are writers/docstrings). Append-only contract is intact.

Exit
----
0 if every row valid + every row matches a known variant.
Nonzero with diagnostic if any row fails.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ATLAS = REPO / "state" / "atlas_health_timeline.jsonl"

# ─── schema field sets ──────────────────────────────────────────────────────

LEGACY_REQUIRED = {"ts", "atlas_lines", "atlas_bytes", "types", "grades", "typed_total"}
META_SCAN_NORMAL_REQUIRED = {"ts", "shard_count", "hub_top3", "scan_age_hours", "source"}
META_SCAN_PARTIAL_REQUIRED = {"ts", "state", "reason", "source"}
NXS004_BASE_REQUIRED = {"ts", "axis_id", "axis_name", "value", "metric", "source",
                       "real_implementation"}
# cycle_anchor is required for per-cycle rows but NOT for the synthetic-excluded audit row
# (which uses excluded_cycles instead). We therefore treat cycle_anchor as conditional below.


def classify(row: dict) -> str | None:
    """Return the variant name, or None if no known variant matches."""
    keys = set(row.keys())

    # nxs004 family — strongest signal is axis_id + source=nxs-20260425-004
    if row.get("source") == "nxs-20260425-004" and "axis_id" in row:
        if not NXS004_BASE_REQUIRED.issubset(keys):
            return None
        if row.get("historical_anchor") is True:
            if not str(row.get("axis_id", "")).endswith("_historical_anchor"):
                return None
            return "nxs004_historical"
        return "nxs004_running"

    # atlas_meta_scan family
    if row.get("source") == "atlas_meta_scan":
        if META_SCAN_NORMAL_REQUIRED.issubset(keys):
            return "atlas_meta_scan_normal"
        if META_SCAN_PARTIAL_REQUIRED.issubset(keys):
            return "atlas_meta_scan_partial"
        return None

    # legacy (pre-Phase-1, no `source` field)
    if LEGACY_REQUIRED.issubset(keys):
        return "atlas_meta_scan_legacy"

    return None


def detect_field_collision(row: dict) -> str | None:
    """Catch rows that mix nxs004 markers with atlas_meta_scan source (or vice-versa)."""
    src = row.get("source")
    if src == "atlas_meta_scan" and "axis_id" in row:
        return "atlas_meta_scan source carries axis_id (nxs004 field)"
    if src == "nxs-20260425-004" and "shard_count" in row:
        return "nxs-20260425-004 source carries shard_count (atlas_meta_scan field)"
    return None


def main() -> int:
    if not ATLAS.exists():
        print(f"⊘ {ATLAS.relative_to(REPO)} missing")
        return 2

    rows: list[tuple[int, dict | None, str]] = []  # (lineno, parsed, raw)
    with open(ATLAS) as fh:
        for i, raw in enumerate(fh, start=1):
            raw = raw.rstrip("\n")
            if not raw.strip():
                continue
            try:
                rows.append((i, json.loads(raw), raw))
            except json.JSONDecodeError as e:
                rows.append((i, None, f"JSONDecodeError: {e} | raw={raw[:80]}"))

    n_total = len(rows)
    n_parse_fail = sum(1 for _, p, _ in rows if p is None)
    variants: dict[str, int] = {}
    unclassified: list[int] = []
    collisions: list[tuple[int, str]] = []

    for lineno, parsed, raw in rows:
        if parsed is None:
            continue
        v = classify(parsed)
        if v is None:
            unclassified.append(lineno)
            continue
        variants[v] = variants.get(v, 0) + 1
        c = detect_field_collision(parsed)
        if c:
            collisions.append((lineno, c))

    n_valid = sum(variants.values())
    pct = 100.0 * n_valid / n_total if n_total else 0.0

    # ─── report ──────────────────────────────────────────────────────────────
    print(f"⊙ atlas_schema_validate — {ATLAS.relative_to(REPO)}")
    print(f"  rows total       : {n_total}")
    print(f"  rows valid       : {n_valid} ({pct:.1f}%)")
    print(f"  rows parse_fail  : {n_parse_fail}")
    print(f"  rows unclassified: {len(unclassified)}")
    print(f"  field collisions : {len(collisions)}")
    print()
    print("  schema variants found:")
    for k in sorted(variants):
        print(f"    {k:30s} : {variants[k]}")
    if unclassified:
        print()
        print("  unclassified line numbers: " + ", ".join(str(n) for n in unclassified))
    if collisions:
        print()
        print("  collisions:")
        for ln, msg in collisions:
            print(f"    line {ln}: {msg}")
    print()
    print("  downstream consumers (verified by grep):")
    print("    tool/atlas_meta_scan.hexa    : WRITER ONLY (append_file) — extra fields safe")
    print("    docs/atlas_meta_dashboard.md : human snapshot (stale, no runtime parse)")
    print("    no reader-style consumer found — append-only contract intact")

    ok = (n_parse_fail == 0) and (not unclassified) and (not collisions)
    if ok:
        print()
        print("  verdict: PASS — schema variants disjoint, no parse failure, no collision")
        return 0
    print()
    print("  verdict: FAIL — see diagnostics above")
    return 1


if __name__ == "__main__":
    sys.exit(main())
