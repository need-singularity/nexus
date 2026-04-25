#!/usr/bin/env python3
"""
beyond_omega_durability_manifest.py — nxs-20260425-004 cycle 41 (REAL impl)

Long-term integrity check baseline for ~30 beyond_omega artifacts.

Real value motivation: ~30 beyond_omega artifacts spread across design/, tool/, state/.
No checksum baseline existed — if a file got accidentally truncated/corrupted (gitignore
state files especially), there was no way to detect. Cycle 41 = one-shot manifest baseline
+ verification script.

Modes:
  (default)   compute manifest for all beyond_omega artifacts → write JSON.
  --verify    re-compute and compare against saved manifest, report diffs (exit code = n_diff).

Per-file fields: relative path, sha256, size_bytes, line_count, mtime_iso, exists.

Artifact selection (glob patterns, repo-root relative):
  - design/beyond_omega_*.md
  - tool/beyond_omega_*.{py,sh,json,md}     # incl. daily_activation.md, axis_decl.json
  - tool/com.nexus.beyond-omega-daily.plist
  - state/beyond_omega_*.json               # may be gitignore
  - state/ghost_ceiling_*.{json,jsonl}      # gitignore (trace files)

NOTE (cycle 41, 2026-04-25): manifest itself (state/beyond_omega_durability_manifest.json)
is EXCLUDED from its own baseline (would be circular: re-computing it changes its own
mtime/sha). Verify mode compares all OTHER files against the saved baseline.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO / "state" / "beyond_omega_durability_manifest.json"

GLOB_PATTERNS = [
    "design/beyond_omega_*.md",
    "tool/beyond_omega_*.py",
    "tool/beyond_omega_*.sh",
    "tool/beyond_omega_*.json",
    "tool/beyond_omega_*.md",
    "tool/com.nexus.beyond-omega-daily.plist",
    "state/beyond_omega_*.json",
    "state/ghost_ceiling_*.json",
    "state/ghost_ceiling_*.jsonl",
]

# Self-exclusion: the manifest file would be circular (compute → write → mtime/sha changed).
SELF_PATH_REL = MANIFEST_PATH.relative_to(REPO).as_posix()


def collect_files() -> list[Path]:
    """Glob expand patterns, dedupe, sort, exclude self-manifest."""
    seen: set[Path] = set()
    for pat in GLOB_PATTERNS:
        for p in REPO.glob(pat):
            if not p.is_file():
                continue
            if p.relative_to(REPO).as_posix() == SELF_PATH_REL:
                continue
            seen.add(p)
    return sorted(seen)


def file_entry(path: Path) -> dict:
    """Compute sha256 + size + line count + mtime for a file."""
    h = hashlib.sha256()
    size = 0
    lines = 0
    with open(path, "rb") as fh:
        while True:
            chunk = fh.read(65536)
            if not chunk:
                break
            h.update(chunk)
            size += len(chunk)
            lines += chunk.count(b"\n")
    st = path.stat()
    mtime_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(st.st_mtime))
    return {
        "path": path.relative_to(REPO).as_posix(),
        "sha256": h.hexdigest(),
        "size_bytes": size,
        "line_count": lines,
        "mtime_iso": mtime_iso,
        "exists": True,
    }


def compute_manifest() -> dict:
    files = collect_files()
    entries = [file_entry(p) for p in files]
    return {
        "schema": "nexus.beyond_omega.durability_manifest.v1",
        "generated_ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "repo_root": str(REPO),
        "n_files": len(entries),
        "glob_patterns": GLOB_PATTERNS,
        "self_excluded_path": SELF_PATH_REL,
        "files": entries,
    }


def write_manifest(manifest: dict) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_PATH, "w") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def load_baseline() -> dict | None:
    if not MANIFEST_PATH.exists():
        return None
    try:
        with open(MANIFEST_PATH) as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError) as e:
        print(f"⚠ baseline read failed: {e}", file=sys.stderr)
        return None


def verify(baseline: dict) -> tuple[int, list[dict]]:
    """Re-compute current and diff against baseline. Returns (n_diff, diff_list)."""
    base_by_path = {e["path"]: e for e in baseline["files"]}
    current = compute_manifest()
    cur_by_path = {e["path"]: e for e in current["files"]}

    diffs: list[dict] = []
    all_paths = set(base_by_path) | set(cur_by_path)
    for p in sorted(all_paths):
        b = base_by_path.get(p)
        c = cur_by_path.get(p)
        if b is None:
            diffs.append({"path": p, "kind": "added", "current": c})
            continue
        if c is None:
            diffs.append({"path": p, "kind": "removed", "baseline": b})
            continue
        if b["sha256"] != c["sha256"]:
            diffs.append({
                "path": p,
                "kind": "sha_mismatch",
                "baseline_sha": b["sha256"],
                "current_sha": c["sha256"],
                "baseline_size": b["size_bytes"],
                "current_size": c["size_bytes"],
                "baseline_lines": b["line_count"],
                "current_lines": c["line_count"],
            })
    return len(diffs), diffs


def main() -> int:
    ap = argparse.ArgumentParser(description="beyond_omega durability manifest")
    ap.add_argument("--verify", action="store_true",
                    help="compare current state against saved baseline (no write)")
    args = ap.parse_args()

    if args.verify:
        baseline = load_baseline()
        if baseline is None:
            print(f"✗ no baseline at {MANIFEST_PATH.relative_to(REPO)} — run without --verify first")
            return 2
        n_diff, diffs = verify(baseline)
        if n_diff == 0:
            print(f"✓ verify OK — {baseline['n_files']} files, 0 diffs vs baseline {baseline['generated_ts']}")
            return 0
        print(f"✗ verify FAIL — {n_diff} diff(s) vs baseline {baseline['generated_ts']}")
        for d in diffs:
            print(f"  [{d['kind']}] {d['path']}")
            if d["kind"] == "sha_mismatch":
                print(f"    baseline sha={d['baseline_sha'][:12]}… size={d['baseline_size']} lines={d['baseline_lines']}")
                print(f"    current  sha={d['current_sha'][:12]}… size={d['current_size']} lines={d['current_lines']}")
        return n_diff

    manifest = compute_manifest()
    write_manifest(manifest)
    print(f"⊙ manifest written: {MANIFEST_PATH.relative_to(REPO)}")
    print(f"  n_files={manifest['n_files']}, generated_ts={manifest['generated_ts']}")
    for e in manifest["files"]:
        print(f"  {e['sha256'][:12]}… {e['size_bytes']:>9}B {e['line_count']:>6}L  {e['path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
