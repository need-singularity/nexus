#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""reality_map.json v9.3 — 5 신규 도메인 패치 병합."""
import json, os, shutil, datetime

SHARED = "/Users/ghost/Dev/nexus/shared"
RM = f"{SHARED}/reality_map.json"
PATCHES = [
    "reality_map.patch.L6_geology.jsonl",
    "reality_map.patch.L6_meteorology.jsonl",
    "reality_map.patch.L6_economics.jsonl",
    "reality_map.patch.L6_linguistics.jsonl",
    "reality_map.patch.L6_music.jsonl",
]

# 백업
bak = RM + ".bak.v93_5dom"
if not os.path.exists(bak):
    shutil.copy2(RM, bak)
    print(f"backup: {bak}")

with open(RM, "r", encoding="utf-8") as f:
    d = json.load(f)

existing_ids = {n.get("id") for n in d["nodes"] if n.get("id")}
patch_merge_log = {}
total_added = 0
total_dup = 0
total_err = 0

for pf in PATCHES:
    path = f"{SHARED}/{pf}"
    added = dup = errs = 0
    with open(path, "r", encoding="utf-8") as f:
        for ln, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                node = json.loads(line)
            except Exception as ex:
                errs += 1
                print(f"  ERR {pf}:{ln}  {ex}")
                continue
            nid = node.get("id")
            if not nid:
                errs += 1
                continue
            if nid in existing_ids:
                dup += 1
                continue
            d["nodes"].append(node)
            existing_ids.add(nid)
            added += 1
    patch_merge_log[pf] = {"added": added, "dup": dup, "errs": errs}
    total_added += added
    total_dup += dup
    total_err += errs
    print(f"  {pf}: +{added}  dup={dup}  err={errs}")

# meta 업데이트
meta = d["_meta"]
meta["version"] = "v9.3_patches"
meta["date"] = datetime.date.today().isoformat()
meta["last_updated"] = datetime.datetime.now().isoformat(timespec="seconds")
meta["node_count"] = len(d["nodes"])
meta["nodes_count"] = len(d["nodes"])
meta.setdefault("patch_merge", {})
meta["patch_merge"].update(patch_merge_log)
meta.setdefault("changelog", []).append({
    "version": "9.3",
    "date": datetime.date.today().isoformat(),
    "change": "L6 신규 5 도메인 추가 — geology/meteorology/economics/linguistics/music (각 100 노드)",
    "added": total_added,
    "dup": total_dup,
    "err": total_err,
    "before": len(d["nodes"]) - total_added,
    "after": len(d["nodes"]),
    "domains": ["L6_geology", "L6_meteorology", "L6_economics", "L6_linguistics", "L6_music"],
    "sources": [
        "USGS", "ICS 2023", "IPA", "Unicode 15.1", "Grove Music Online",
        "IPCC AR6", "WMO", "IMF WEO 2024", "Ethnologue 27", "WALS", "PREM 1981",
    ],
})
d["version"] = "v9.3_patches"

with open(RM, "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False, indent=2)

print(f"\n병합 완료: +{total_added} 노드, dup={total_dup}, err={total_err}")
print(f"총 노드: {len(d['nodes'])}")
print(f"저장: {RM}")
