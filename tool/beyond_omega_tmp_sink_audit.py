#!/usr/bin/env python3
"""
beyond_omega_tmp_sink_audit.py — nxs-20260425-004 cycle 37 (real implementation)

/tmp emit sink audit for nexus omega / beyond-omega chains.

Motivation:
  cycles 1-2 discovered /tmp/nexus_omega_hive_statusline_v{2,3,4,5}.log as
  historical sinks. cycle 4 added /tmp/nexus_omega_cycle4_forced.{out,err}.log.
  cycle 5 daily plist outputs to /tmp/nexus_beyond_omega_daily.{out,err}.log.
  cycle 32 chain script logs to /tmp/nexus_beyond_omega_daily_chain.log.
  Each daily fire could grow these indefinitely. No rotation policy installed
  → eventual disk pressure. cycle 37 = audit + rotation recommendation
  (DO NOT execute deletion in this cycle).

This tool is read-only:
  - Lists all matching /tmp files with size + age + last-line preview
  - Computes total disk footprint
  - Recommends rotation: files older than ROTATION_DAYS_DEFAULT=7 → archive to
    state/archive/tmp_sinks/YYYY-MM-DD/ OR delete with audit row
  - Prints recommended action (does NOT execute)
"""
from __future__ import annotations

import glob as _glob
import json
import os
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SINK_GLOBS = [
    "/tmp/nexus_omega_*.log",
    "/tmp/nexus_omega_*.out.log",
    "/tmp/nexus_omega_*.err.log",
    "/tmp/nexus_beyond_omega_*.log",
    "/tmp/nexus_beyond_omega_*.out.log",
    "/tmp/nexus_beyond_omega_*.err.log",
]
ROTATION_DAYS_DEFAULT = 7
LARGE_FOOTPRINT_BYTES = 1 * 1024 * 1024  # 1MB threshold for "large" concern


def discover() -> list[Path]:
    seen: set[str] = set()
    out: list[Path] = []
    for pat in SINK_GLOBS:
        for hit in _glob.glob(pat):
            if hit in seen:
                continue
            seen.add(hit)
            p = Path(hit)
            if p.is_file():
                out.append(p)
    return sorted(out)


def last_line_preview(p: Path, max_bytes: int = 4096) -> str:
    try:
        size = p.stat().st_size
    except OSError:
        return ""
    if size == 0:
        return "(empty)"
    try:
        with open(p, "rb") as fh:
            seek_to = max(0, size - max_bytes)
            fh.seek(seek_to)
            tail = fh.read().decode("utf-8", errors="replace")
    except OSError:
        return "(read_error)"
    lines = [ln for ln in tail.splitlines() if ln.strip()]
    if not lines:
        return "(blank_tail)"
    return lines[-1][:200]


def audit(rotation_days: int = ROTATION_DAYS_DEFAULT) -> dict:
    now = time.time()
    files = discover()
    rows = []
    total_bytes = 0
    oldest_age_days = 0.0
    rotation_candidates = 0
    for p in files:
        try:
            st = p.stat()
        except OSError:
            continue
        age_days = (now - st.st_mtime) / 86400.0
        oldest_age_days = max(oldest_age_days, age_days)
        total_bytes += st.st_size
        rotate = age_days > rotation_days
        if rotate:
            rotation_candidates += 1
        rows.append({
            "path": str(p),
            "size_bytes": st.st_size,
            "size_human": _human(st.st_size),
            "mtime_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(st.st_mtime)),
            "age_days": round(age_days, 3),
            "rotation_candidate": rotate,
            "last_line_preview": last_line_preview(p),
        })
    rows.sort(key=lambda r: r["age_days"], reverse=True)

    # Recommendation
    if total_bytes < LARGE_FOOTPRINT_BYTES and rotation_candidates == 0:
        priority = "LOW"
        action = "no immediate action; revisit when files >7d or total >1MB"
    elif rotation_candidates > 0:
        priority = "MEDIUM"
        action = (
            f"{rotation_candidates} file(s) >{rotation_days}d — recommend manual run of "
            f"tool/beyond_omega_tmp_sink_rotate.sh (archive to state/archive/tmp_sinks/ then unlink) "
            f"OR plain deletion with audit row"
        )
    else:
        priority = "LOW-MEDIUM"
        action = (
            f"no files >{rotation_days}d yet, but total footprint {_human(total_bytes)} ≥ 1MB — "
            f"monitor; rotation policy still recommended for future"
        )

    return {
        "schema": "nexus.beyond_omega.tmp_sink_audit.v1",
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)),
        "rotation_days_threshold": rotation_days,
        "file_count": len(rows),
        "total_bytes": total_bytes,
        "total_human": _human(total_bytes),
        "oldest_age_days": round(oldest_age_days, 3),
        "rotation_candidate_count": rotation_candidates,
        "priority": priority,
        "recommended_action": action,
        "files": rows,
    }


def _human(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}TB"


def main(argv):
    rotation_days = ROTATION_DAYS_DEFAULT
    write_state = "--write" in argv
    for i, a in enumerate(argv):
        if a == "--days" and i + 1 < len(argv):
            try:
                rotation_days = int(argv[i + 1])
            except ValueError:
                pass

    result = audit(rotation_days=rotation_days)

    print(f"⊙ tmp_sink_audit files={result['file_count']} "
          f"total={result['total_human']} oldest={result['oldest_age_days']}d "
          f"rotation_candidates={result['rotation_candidate_count']} "
          f"priority={result['priority']}")
    print(f"  threshold = {rotation_days}d")
    print(f"  action    = {result['recommended_action']}")
    print(f"  files (sorted by age desc):")
    for r in result["files"]:
        marker = " ⚠" if r["rotation_candidate"] else "  "
        print(f"   {marker} {r['age_days']:7.2f}d  {r['size_human']:>8}  "
              f"{Path(r['path']).name}")
        print(f"        last: {r['last_line_preview'][:120]}")

    if write_state:
        out_path = REPO / "state" / "beyond_omega_tmp_sink_audit.json"
        with open(out_path, "w") as fh:
            json.dump(result, fh, ensure_ascii=False, indent=2)
        print(f"  state → {out_path.relative_to(REPO)}")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
