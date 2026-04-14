#!/usr/bin/env python3
# @hexa-first-exempt — hexa stage1 runtime (has_key undefined + O(N) dict iteration) 우회
"""
atlas_map_export.py — Helper for atlas_map_export.hexa

atlas.n6 → docs/atlas_map_data.json 빌더. docs/atlas3d.html 가 fetch 하는 정적 JSON.

Called by: shared/n6/atlas_map_export.hexa  (orchestrator + args parser)

Input:  atlas.n6 (text @-nodes + inline JSON discovery nodes/edges)
Output: atlas_map_data.json
  meta:  {source, node_count, edge_count, generated, generator, layers}
  nodes: [{i, id, l, t, d, dom, g, e}]
  edges: [[src_i, dst_i]]

Parse rules (matches atlas_map_export.hexa awk script 1:1):
  @[A-Z?] id [= expr] :: dom[grade]     text node
  {"type":"node", "id":..., "node_type":..., "domain":..., "summary":..., "depth":...}  JSON node
  {"type":"edge", "from":..., "to":...}  JSON edge
  "  -> target, ..."  outgoing edges (cur → target)
  "  <- source, ..."  incoming edges (source → cur)
  "  == equiv"        equivalence edge (cur → equiv, skip numeric/formula)

Usage: atlas_map_export.py <atlas_path> <out_path> [--dry-run]
"""
import sys
import os
import re
import json
import time

# ─── Domain → layer mapping (matches hexa layer_map) ───
LAYER_MAP = {
    # L0: foundations / particles
    "foundation": 0, "math": 0, "mathematics": 0, "meta": 0, "particle": 0,
    "quark": 0, "sub_quark": 0, "nuclear": 0, "topology": 0, "geometry": 0,
    "algebra": 0, "number_theory": 0, "7대난제": 0, "아이디어→math": 0,
    # L1: atoms / laws
    "architecture": 1, "physics": 1, "atom": 1, "bond": 1, "chemistry": 1,
    "cryptography": 1, "anatomy": 1, "atmospheric_physics": 1, "analysis": 1,
    # L2: molecules / bio
    "biology": 2, "bio": 2, "bio_hiv": 2, "molecule": 2, "consciousness": 2,
    "genetic": 2, "genetics_applied": 2, "material": 2, "materials": 2,
    # L4: cosmic
    "celestial": 4, "convergence": 4, "cosmological": 4, "cosmology": 4,
    "galactic": 4, "multiversal": 4, "n6-canonical": 4,
    # L3: domains (default for everything else)
}
LAYER_NAMES = [
    "L0 foundations/particles",
    "L1 atoms/laws",
    "L2 molecules/bio",
    "L3 domains",
    "L4 cosmic",
]

# ─── Text-node type → docs schema type ───
TEXT_TYPE_MAP = {
    "P": "p", "C": "c", "F": "f", "L": "l", "R": "r",
    "S": "s", "X": "c", "?": "u",
}
JSON_TYPE_MAP = {
    "Discovery": "D", "RecursiveDiscovery": "R",
    "discovery": "d", "corollary": "c", "constant": "c",
}


def map_layer(dom):
    return LAYER_MAP.get(dom, 3)


def map_text_type(t):
    return TEXT_TYPE_MAP.get(t, "u")


def map_json_type(nt):
    return JSON_TYPE_MAP.get(nt, "D")


# Regex patterns (compiled once)
RE_TEXT_NODE = re.compile(r"^@([A-Z?]) (.+)$")
RE_ARROW_OUT = re.compile(r"^[ \t]+-> +(.+?)(?:\s*#.*)?$")
RE_ARROW_IN = re.compile(r"^[ \t]+<- +(.+?)(?:\s*#.*)?$")
RE_EQUIV = re.compile(r"^[ \t]+== +(.+?)(?:\s*#.*)?$")
RE_JSON_NODE = re.compile(r'^\{"type":"node"')
RE_JSON_EDGE = re.compile(r'^\{"type":"edge"')
RE_FIELD_ID = re.compile(r'"id":"([^"]*)"')
RE_FIELD_NT = re.compile(r'"node_type":"([^"]*)"')
RE_FIELD_DOMAIN = re.compile(r'"domain":"([^"]*)"')
RE_FIELD_SUMMARY = re.compile(r'"summary":"([^"]*)"')
RE_FIELD_DEPTH = re.compile(r'"depth":(\d+)')
RE_FIELD_FROM = re.compile(r'"from":"([^"]*)"')
RE_FIELD_TO = re.compile(r'"to":"([^"]*)"')

# Expression/numeric filter for == edges
RE_SKIP_EQUIV = re.compile(r'^["0-9]|[+*/^]')


def parse_text_header(line):
    """Parse '@<TYPE> <id> [= <expr>] :: <dom>[<grade>]' into (type, id, dom, grade, expr)."""
    m = RE_TEXT_NODE.match(line)
    if not m:
        return None
    typ = m.group(1)
    rest = m.group(2)
    cop = rest.find(" :: ")
    if cop < 0:
        return None
    eqp = rest.find(" = ")
    if 0 <= eqp < cop:
        cur = rest[:eqp].strip()
        expr = rest[eqp + 3 : cop].strip()
    else:
        cur = rest[:cop].strip()
        expr = ""
    after = rest[cop + 4 :]
    bp = after.find("[")
    if bp >= 0:
        ep = after.find("]", bp)
        grade = after[bp + 1 : ep] if ep > bp else ""
        dom = after[:bp].strip()
    else:
        grade = ""
        dom = after.strip()
    # Sanitize tabs (match hexa gsub)
    cur = cur.replace("\t", " ")
    dom = dom.replace("\t", " ")
    grade = grade.replace("\t", " ")
    expr = expr.replace("\t", " ")
    return (typ, cur, dom, grade, expr)


def parse_atlas(atlas_path):
    """Single-pass parser: emits nodes (dedup) + edge candidates."""
    node_ids = []
    node_meta = {}
    id_to_i = {}
    edge_buf = []
    cur = ""

    with open(atlas_path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.rstrip("\n").rstrip("\r")
            if not line:
                continue
            c0 = line[0]
            if c0 == "@":
                cur = ""
                res = parse_text_header(line)
                if res is None:
                    continue
                typ, cid, dom, grade, expr = res
                if not cid:
                    continue
                cur = cid
                if cid in id_to_i:
                    continue
                id_to_i[cid] = len(node_ids)
                node_ids.append(cid)
                node_meta[cid] = {
                    "t": map_text_type(typ),
                    "dom": dom,
                    "g": grade,
                    "e": expr,
                }
            elif c0 in (" ", "\t"):
                stripped = line.lstrip()
                if not cur or not stripped:
                    continue
                head = stripped[:2]
                if head == "->":
                    body = stripped[2:].strip()
                    body = re.sub(r"\s*#.*", "", body)
                    for p in re.split(r",\s+", body):
                        p = p.strip()
                        if p and not p.startswith('"'):
                            edge_buf.append((cur, p))
                elif head == "<-":
                    body = stripped[2:].strip()
                    body = re.sub(r"\s*#.*", "", body)
                    for p in re.split(r",\s+", body):
                        p = p.strip()
                        if p and not p.startswith('"'):
                            edge_buf.append((p, cur))
                elif head == "==":
                    body = stripped[2:].strip()
                    body = re.sub(r"\s*#.*", "", body)
                    p = body.strip()
                    if p and not RE_SKIP_EQUIV.match(p):
                        edge_buf.append((cur, p))
            elif c0 == "{":
                # JSON node or edge
                if RE_JSON_NODE.match(line):
                    mid = RE_FIELD_ID.search(line)
                    if not mid:
                        continue
                    nid = mid.group(1)
                    if not nid or nid in id_to_i:
                        continue
                    mnt = RE_FIELD_NT.search(line)
                    mdm = RE_FIELD_DOMAIN.search(line)
                    msm = RE_FIELD_SUMMARY.search(line)
                    # depth intentionally not stored (matches hexa which reads but doesn't emit)
                    nt = mnt.group(1) if mnt else ""
                    dom = mdm.group(1) if mdm else ""
                    sm = msm.group(1) if msm else ""
                    id_to_i[nid] = len(node_ids)
                    node_ids.append(nid)
                    node_meta[nid] = {
                        "t": map_json_type(nt),
                        "dom": dom.replace("\t", " "),
                        "g": "",
                        "e": sm.replace("\t", " "),
                    }
                elif RE_JSON_EDGE.match(line):
                    mf = RE_FIELD_FROM.search(line)
                    mt = RE_FIELD_TO.search(line)
                    if mf and mt:
                        f = mf.group(1)
                        t = mt.group(1)
                        if f and t:
                            edge_buf.append((f, t))

    return node_ids, node_meta, id_to_i, edge_buf


def resolve_edges(id_to_i, edge_buf):
    """Dedup edges, drop self-loops, require both endpoints exist. Return (edges, degrees)."""
    seen = set()
    edges = []
    degrees = {}
    for src, dst in edge_buf:
        if src == dst:
            continue
        si = id_to_i.get(src)
        if si is None:
            continue
        di = id_to_i.get(dst)
        if di is None:
            continue
        key = (src, dst)
        if key in seen:
            continue
        seen.add(key)
        edges.append([si, di])
        degrees[src] = degrees.get(src, 0) + 1
        degrees[dst] = degrees.get(dst, 0) + 1
    return edges, degrees


def build_output(atlas_path, node_ids, node_meta, edges, degrees):
    """Build output dict matching hexa schema."""
    nodes = []
    for i, nid in enumerate(node_ids):
        m = node_meta[nid]
        dom = m["dom"]
        nodes.append({
            "i": i,
            "id": nid,
            "l": map_layer(dom),
            "t": m["t"],
            "d": degrees.get(nid, 0),
            "dom": dom,
            "g": m["g"],
            "e": m["e"],
        })
    return {
        "meta": {
            "source": atlas_path,
            "node_count": len(node_ids),
            "edge_count": len(edges),
            "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "generator": "shared/n6/atlas_map_export.hexa",
            "layers": LAYER_NAMES,
        },
        "nodes": nodes,
        "edges": edges,
    }


def main():
    argv = sys.argv[1:]
    dry_run = "--dry-run" in argv
    argv = [a for a in argv if a != "--dry-run"]
    if len(argv) < 2:
        print("usage: atlas_map_export.py <atlas_path> <out_path> [--dry-run]", file=sys.stderr)
        sys.exit(2)
    atlas_path, out_path = argv[0], argv[1]
    if not os.path.exists(atlas_path):
        print(f"error: atlas not found: {atlas_path}", file=sys.stderr)
        sys.exit(1)

    t0 = time.time()
    print(f"=== atlas_map_export ===")
    print(f"  source: {atlas_path}")
    print(f"  target: {out_path}")
    print(f"  parsing...")

    node_ids, node_meta, id_to_i, edge_buf = parse_atlas(atlas_path)
    t1 = time.time()
    print(f"  parse:  {int((t1 - t0) * 1000)}ms, nodes: {len(node_ids)}, edge candidates: {len(edge_buf)}")

    edges, degrees = resolve_edges(id_to_i, edge_buf)
    t2 = time.time()
    print(f"  edges (deduped, valid): {len(edges)} ({int((t2 - t1) * 1000)}ms)")

    out = build_output(atlas_path, node_ids, node_meta, edges, degrees)
    payload = json.dumps(out, ensure_ascii=False, separators=(",", ":"))
    size = len(payload.encode("utf-8"))

    if dry_run:
        print(f"dry-run: would write {out_path} ({size} bytes)")
        return

    # atomic write
    tmp = out_path + ".tmp"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(payload)
    os.replace(tmp, out_path)
    t3 = time.time()
    print(f"✓ wrote {out_path} ({len(node_ids)} nodes, {len(edges)} edges, {int((t3 - t0) * 1000)}ms, {size} bytes)")


if __name__ == "__main__":
    main()
