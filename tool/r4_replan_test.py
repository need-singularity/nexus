#!/usr/bin/env python3
"""r4 replan benchmark — 5 fixtures, geo-mean assertion, action match."""
import json
import math
import os
import sys
import hashlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4_replan import parse_roadmap, vstar, schedule_replan, _start_id

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BENCH = os.path.join(ROOT, "design", "roadmap_engine", "r4_bench")
MANIFEST = os.path.join(BENCH, "MANIFEST.json")

# Map manifest expected_replan_action → r4_replan strategy keys (may differ for compound)
ACTION_MAP = {
    "soft_drop": {"soft_drop"},
    "parallel_split": {"parallel_split"},
    "seed_inject": {"seed_inject"},
    "compound": {"soft_drop", "parallel_split", "seed_inject"},
    "none": {None},
}

def main() -> int:
    with open(MANIFEST, "r") as f:
        manifest = json.load(f)
    ratios = []
    worst = 0.0
    matches = 0
    total = 0
    fail_lines = []
    for entry in manifest["entries"]:
        total += 1
        path = os.path.join(ROOT, entry["path"])
        rm = parse_roadmap(path)
        sid = _start_id(rm)
        T_pre_machine = vstar(rm, sid, include_soft=True)
        delta = schedule_replan(rm)
        expected = entry["expected_replan_action"]
        observed = delta.action if delta else None
        # Action match check
        valid_set = ACTION_MAP[expected]
        if observed in valid_set:
            matches += 1
        else:
            fail_lines.append(f"  {entry['name']}: expected={expected} observed={observed}")
        # Negative control: must return None
        if expected == "none":
            if delta is not None:
                fail_lines.append(f"  {entry['name']}: control fired delta {delta.action}")
            continue
        # Positive: T_post < expected_T_star_pre
        T_post = delta.T_post if delta else math.inf
        T_pre_expected = entry["expected_T_star_pre"]
        if T_post >= T_pre_expected:
            fail_lines.append(f"  {entry['name']}: T_post={T_post:.3f} >= expected_pre={T_pre_expected:.3f}")
        # ratio vs MACHINE T_pre (geo-mean denominator) — fall back to expected_pre if machine=0
        denom = T_pre_machine if T_pre_machine > 0 else T_pre_expected
        ratio = T_post / denom if denom > 0 else 1.0
        ratios.append(ratio)
        if ratio > worst:
            worst = ratio
        print(f"  {entry['name']}: action={observed} T_pre_m={T_pre_machine:.2f} "
              f"T_post={T_post:.2f} expected_pre={T_pre_expected:.2f} ratio={ratio:.3f}")

    if not ratios:
        print("FAIL: no positive cases")
        return 1
    log_sum = sum(math.log(r) for r in ratios if r > 0)
    geo_mean = math.exp(log_sum / len(ratios))
    if geo_mean >= 0.99:
        fail_lines.append(f"  geo_mean={geo_mean:.3f} >= 0.99 falsifier threshold")
    if fail_lines:
        print("FAIL:")
        for ln in fail_lines:
            print(ln)
        print(f"matches={matches}/{total} geo_mean={geo_mean:.3f} worst={worst:.3f}")
        return 1
    print(f"__R4_REPLAN__ PASS geo_mean={geo_mean:.3f} worst_case={worst:.3f} matches={matches}/{total}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
