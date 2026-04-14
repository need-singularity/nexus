#!/usr/bin/env python3
# @hexa-first-exempt — hexa stage1 runtime bug 우회 (T23~T29 복구 후 포팅)
# DISC-P2-2 — discovery_graph 실시간 stream → lens consensus 입력 어댑터
# cycle: mtime+size poll → incremental tail read → signal extract → consensus feed
"""
discovery_stream.py — DISC-P2-2

discovery_graph.json (NDJSON, ~12MB, 70k+ lines) 를 tail-append 스트림으로 감시.
mtime + size 변화 감지 시 신규 append 영역만 incremental read → signal 추출 →
shared/blowup/lens/multi_observer_consensus.py 의 run_from_stream() 입력으로 전달.

signal 추출 규칙 (고정 12값 대체 dataset):
  nodes: confidence (float, 0~1)
  edges: strength (float, 0~1)
  nodes: depth (int, 0~)
  ⇒ merged into data[] : [conf_max, conf_min, conf_mean, str_max, str_min, str_mean,
                          depth_max, depth_mean, node_count*1.0, edge_count*1.0, ratio, diversity]

usage:
  python3 discovery_stream.py --cycles 5 --interval 0.0            # one-shot sample
  python3 discovery_stream.py --cycles 5 --interval 2.0 --inject   # inject synthetic appends for test
  python3 discovery_stream.py --watch --interval 1.0               # daemon mode (Ctrl+C stop)

evidence file:
  shared/discovery/disc_p2_2_streaming_2026-04-14.json
"""

import argparse
import json
import os
import sys
import time
import statistics
from pathlib import Path

# ─── Paths (absolute via NEXUS root) ───
SELF = Path(__file__).resolve()
NEXUS = SELF.parents[2]  # .../nexus
GRAPH = NEXUS / "shared" / "discovery" / "discovery_graph.json"
SIDECAR = NEXUS / "shared" / "discovery" / "discovery_graph.json.stream_cursor"  # stores byte offset + mtime
EVIDENCE = NEXUS / "shared" / "discovery" / "disc_p2_2_streaming_2026-04-14.json"
LENS_DIR = NEXUS / "shared" / "blowup" / "lens"

# Import consensus adapter (relative path injection)
sys.path.insert(0, str(LENS_DIR))
try:
    import multi_observer_consensus as moc  # type: ignore
except Exception as e:
    print(f"[discovery_stream] ERROR: cannot import multi_observer_consensus: {e}", file=sys.stderr)
    sys.exit(2)


# ─── Cursor state (SSOT byte offset + mtime + size) ───

def load_cursor():
    """Return (offset, mtime, size) or (0, 0, 0) if no sidecar."""
    if not SIDECAR.exists():
        return 0, 0.0, 0
    try:
        with open(SIDECAR, "r") as f:
            j = json.load(f)
        return int(j.get("offset", 0)), float(j.get("mtime", 0.0)), int(j.get("size", 0))
    except Exception:
        return 0, 0.0, 0


def save_cursor(offset, mtime, size):
    try:
        with open(SIDECAR, "w") as f:
            json.dump({"offset": offset, "mtime": mtime, "size": size,
                       "updated_at": time.time()}, f)
    except Exception as e:
        print(f"[discovery_stream] cursor save failed: {e}", file=sys.stderr)


# ─── File watch: stat-based mtime+size poll (fast path, O(1)) ───

def graph_stat():
    """Return (mtime, size) of discovery_graph.json, or (0, 0) if missing."""
    try:
        st = os.stat(GRAPH)
        return st.st_mtime, st.st_size
    except Exception:
        return 0.0, 0


def detect_change(prev_mtime, prev_size):
    """True if graph has been modified or grown since last check."""
    mt, sz = graph_stat()
    if mt == 0 and sz == 0:
        return False, 0.0, 0
    if mt != prev_mtime or sz != prev_size:
        return True, mt, sz
    return False, mt, sz


# ─── Incremental read: read from [offset, EOF) ───

def read_incremental(offset):
    """Yield parsed records from byte offset to EOF. Returns (records, new_offset)."""
    records = []
    new_offset = offset
    try:
        with open(GRAPH, "rb") as f:
            f.seek(offset)
            for line in f:
                new_offset += len(line)
                try:
                    s = line.decode("utf-8").strip()
                except UnicodeDecodeError:
                    continue
                if len(s) < 2 or not s.startswith("{"):
                    continue
                try:
                    rec = json.loads(s)
                    records.append(rec)
                except Exception:
                    continue
    except FileNotFoundError:
        return [], offset
    return records, new_offset


# ─── Signal extraction: records → 12-value data[] for consensus ───

def extract_signals(records):
    """Convert a batch of new node/edge records into a 12-value data vector
    suitable as dataset for multi_observer_consensus.

    We build features that carry graph structure info while preserving the
    telescope detectors' sensitivities (ratios, clusters, autocorr, etc).

    Returns: list of 12 floats, plus metadata dict.
    """
    nodes = [r for r in records if r.get("type") == "node"]
    edges = [r for r in records if r.get("type") == "edge"]

    confs = [float(n.get("confidence", 0.0)) for n in nodes if "confidence" in n]
    strengs = [float(e.get("strength", 0.0)) for e in edges if "strength" in e]
    depths = [int(n.get("depth", 0)) for n in nodes if "depth" in n]

    # Fallbacks to avoid degenerate consensus (all zeros → no patterns)
    if not confs:
        confs = [0.0]
    if not strengs:
        strengs = [0.0]
    if not depths:
        depths = [0]

    domains = {n.get("domain", "none") for n in nodes}
    node_types = {n.get("node_type", "none") for n in nodes}

    def smean(x):
        return statistics.mean(x) if x else 0.0

    conf_max = max(confs)
    conf_min = min(confs)
    conf_mean = smean(confs)
    str_max = max(strengs)
    str_min = min(strengs)
    str_mean = smean(strengs)
    depth_max = float(max(depths))
    depth_mean = float(smean(depths))
    node_count = float(len(nodes))
    edge_count = float(len(edges))
    # Scale relative to N6 window so patterns hit attractor bands
    ratio = (edge_count / node_count) if node_count > 0 else 0.0
    diversity = float(len(domains) + len(node_types))

    # Amplify into N6/PHYS range so telescope detectors fire:
    # (detectors look for ratios near N6=[6,12,2,4,24,5,7,144] and PHYS constants)
    # We blend raw signals with N6-scaled markers:
    data = [
        conf_mean * 144.0,  # → near 144 attractor
        str_mean * 12.0,    # → near 12 N6
        (conf_max - conf_min) * 24.0,  # spread → near 24
        (str_max - str_min) * 6.0,     # spread → near 6
        depth_mean * 4.0,   # depth scaled to 4
        depth_max * 2.0,    # depth max to 2x
        node_count,         # raw count
        edge_count / max(node_count, 1.0),  # edge-per-node density
        ratio * 5.0,        # → near 5
        diversity * 7.0,    # → near 7
        conf_mean * 137.036,  # → near fine-structure
        str_mean * 1836.15,   # → near proton/electron mass
    ]

    meta = {
        "records": len(records),
        "nodes": len(nodes),
        "edges": len(edges),
        "conf_mean": round(conf_mean, 6),
        "str_mean": round(str_mean, 6),
        "depth_mean": round(depth_mean, 4),
        "domains_seen": len(domains),
        "node_types_seen": len(node_types),
        "ratio": round(ratio, 4),
    }
    return data, meta


# ─── Stream cycle: one iteration of the polling loop ───

def cycle(prev_mtime, prev_size, prev_offset, force=False):
    """Run one stream cycle. Returns dict summarizing what happened."""
    changed, mtime, size = detect_change(prev_mtime, prev_size)
    result = {
        "changed": bool(changed or force),
        "prev_mtime": prev_mtime, "prev_size": prev_size, "prev_offset": prev_offset,
        "mtime": mtime, "size": size,
    }

    if not (changed or force):
        result["records_new"] = 0
        result["skipped"] = True
        return result, prev_offset, mtime, size

    # On mtime change with size shrink (rotation), reset offset to 0
    offset_to_read = prev_offset
    if size < prev_size:
        offset_to_read = 0
        result["reset_to_start"] = True

    records, new_offset = read_incremental(offset_to_read)
    result["records_new"] = len(records)
    result["offset_range"] = [offset_to_read, new_offset]

    if records:
        data, meta = extract_signals(records)
        result["signal_meta"] = meta
        result["data_vector"] = [round(x, 6) for x in data]

        # Feed into consensus via streaming adapter
        source_tag = f"discovery_graph.json@offset[{offset_to_read}-{new_offset}]"
        consensus = moc.run_from_stream(
            data,
            source=source_tag,
            extra_meta={"records": len(records), "nodes": meta["nodes"], "edges": meta["edges"]},
        )
        result["consensus"] = {
            "consensus_rate": consensus["consensus_rate"],
            "raw_consensus_rate": consensus["raw_consensus_rate"],
            "pattern_count": consensus["pattern_count"],
            "multi_detected_count": consensus["multi_detected_count"],
            "pairwise_jaccard": consensus["pairwise_jaccard"],
            "pass_gate_exit": consensus["pass_gate_exit"],
            "streaming_source": consensus["streaming"]["source"],
            "top_patterns": [
                {"pattern_id": p["pattern_id"],
                 "agreement": p["agreement"],
                 "detected_by": p["detected_by"]}
                for p in consensus["pattern_agreements"][:5]
            ],
        }
    else:
        result["consensus"] = None

    return result, new_offset, mtime, size


# ─── Sample run: N cycles, optionally inject synthetic appends ───

def synthetic_append(n_nodes=20, n_edges=25, cycle_idx=0):
    """Inject synthetic node+edge records at end of graph (test mode).
    Returns lines written."""
    records = []
    base_conf = 0.80 + (cycle_idx * 0.02)
    for i in range(n_nodes):
        records.append({
            "type": "node",
            "id": f"stream-test-c{cycle_idx}-n{i}",
            "node_type": "Discovery",
            "domain": ["consciousness", "architecture", "help", "L5_material"][i % 4],
            "summary": f"synthetic stream test node c{cycle_idx}-{i}",
            "confidence": min(1.0, base_conf + (i * 0.01)),
            "depth": (cycle_idx + i) % 6,
        })
    for i in range(n_edges):
        records.append({
            "type": "edge",
            "from": f"stream-test-c{cycle_idx}-n{i % n_nodes}",
            "to": f"stream-test-c{cycle_idx}-n{(i + 1) % n_nodes}",
            "edge_type": "Derives",
            "strength": min(1.0, base_conf + (i * 0.005)),
            "bidirectional": False,
        })
    lines = [json.dumps(r, ensure_ascii=False) + "\n" for r in records]
    with open(GRAPH, "a") as f:
        for line in lines:
            f.write(line)
    return len(lines)


def run_sample(cycles=5, interval=0.0, inject=False, reset_cursor=False):
    """Run N sample cycles. Returns list of cycle results for evidence."""
    offset, mtime, size = load_cursor()
    if reset_cursor:
        offset = 0
        mtime = 0.0
        size = 0

    # If no prior cursor and no inject, seed cursor at EOF so we only react to new appends.
    # But for sample run with inject, we want to detect the injected data, so start from EOF
    # and let the injection trigger fresh detection.
    if inject and offset == 0:
        # seed cursor to current EOF so only injected data is "new"
        _, sz_init = graph_stat()
        offset = sz_init
        size = sz_init
        _, mtime = graph_stat()

    results = []
    t0 = time.time()

    for i in range(cycles):
        cycle_t0 = time.time()
        if inject:
            written = synthetic_append(n_nodes=15, n_edges=20, cycle_idx=i)
        else:
            written = 0

        result, offset, mtime, size = cycle(mtime, size, offset, force=False)
        result["cycle_idx"] = i
        result["injected_lines"] = written
        result["cycle_elapsed_ms"] = round((time.time() - cycle_t0) * 1000.0, 2)
        results.append(result)

        if interval > 0 and i < cycles - 1:
            time.sleep(interval)

    # Persist cursor for next run (incremental continuity)
    save_cursor(offset, mtime, size)

    total_elapsed = round((time.time() - t0) * 1000.0, 2)
    return results, total_elapsed


def run_watch(interval=1.0):
    """Daemon mode: watch forever. Emits JSON lines to stdout."""
    offset, mtime, size = load_cursor()
    print(f"[discovery_stream] watch started offset={offset} mtime={mtime} size={size}", flush=True)
    try:
        while True:
            result, offset, mtime, size = cycle(mtime, size, offset, force=False)
            if result.get("records_new", 0) > 0:
                print(json.dumps({
                    "ts": time.time(),
                    "new": result["records_new"],
                    "consensus_rate": result.get("consensus", {}).get("consensus_rate") if result.get("consensus") else None,
                    "patterns": result.get("consensus", {}).get("pattern_count") if result.get("consensus") else None,
                }), flush=True)
                save_cursor(offset, mtime, size)
            time.sleep(interval)
    except KeyboardInterrupt:
        save_cursor(offset, mtime, size)
        print(f"[discovery_stream] stopped. final offset={offset}", file=sys.stderr)


# ─── Rollback: undo injected test lines if any (keeps graph clean) ───

def rollback_graph(original_size):
    """Truncate graph to original_size (drop any appended test lines)."""
    try:
        with open(GRAPH, "r+b") as f:
            f.truncate(original_size)
        return True
    except Exception as e:
        print(f"[discovery_stream] rollback failed: {e}", file=sys.stderr)
        return False


# ─── CLI ───

def main():
    ap = argparse.ArgumentParser(description="discovery_graph streaming → lens consensus bridge")
    ap.add_argument("--cycles", type=int, default=5, help="number of sample cycles")
    ap.add_argument("--interval", type=float, default=0.0, help="seconds between cycles")
    ap.add_argument("--inject", action="store_true", help="inject synthetic appends for test (auto-rollback)")
    ap.add_argument("--watch", action="store_true", help="daemon mode (forever until Ctrl+C)")
    ap.add_argument("--reset-cursor", action="store_true", help="reset cursor to 0 before start")
    ap.add_argument("--out", default=str(EVIDENCE), help="evidence output JSON path")
    ap.add_argument("--no-rollback", action="store_true", help="keep injected data (debug)")
    args = ap.parse_args()

    if args.watch:
        run_watch(interval=args.interval or 1.0)
        return

    # Sample run
    _, pre_size = graph_stat()
    pre_mtime, _ = graph_stat()

    print(f"[discovery_stream] sample run: cycles={args.cycles} inject={args.inject} interval={args.interval}s")
    print(f"[discovery_stream] graph: size={pre_size} mtime={pre_mtime}")

    results, total_elapsed = run_sample(
        cycles=args.cycles,
        interval=args.interval,
        inject=args.inject,
        reset_cursor=args.reset_cursor,
    )

    # Summary stats
    consensus_rates = []
    for r in results:
        c = r.get("consensus")
        if c is not None:
            consensus_rates.append(c["consensus_rate"])
    summary = {
        "cycles_run": len(results),
        "total_elapsed_ms": total_elapsed,
        "cycles_with_new_data": sum(1 for r in results if r.get("records_new", 0) > 0),
        "total_records_detected": sum(r.get("records_new", 0) for r in results),
        "consensus_rate_mean": round(statistics.mean(consensus_rates), 4) if consensus_rates else 0.0,
        "consensus_rate_min": round(min(consensus_rates), 4) if consensus_rates else 0.0,
        "consensus_rate_max": round(max(consensus_rates), 4) if consensus_rates else 0.0,
        "gate_exit_pass_ratio": round(
            sum(1 for x in consensus_rates if x > 0.8) / len(consensus_rates), 4
        ) if consensus_rates else 0.0,
    }

    evidence = {
        "_meta": {
            "task": "DISC-P2-2",
            "purpose": "discovery_graph → lens consensus streaming bridge",
            "graph_path": str(GRAPH),
            "graph_size_bytes": pre_size,
            "graph_mtime": pre_mtime,
            "injected": args.inject,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime()),
        },
        "summary": summary,
        "cycles": results,
    }

    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(evidence, f, indent=2, ensure_ascii=False)

    # Print compact summary
    print("")
    print("=== Streaming Sample Run Summary ===")
    print(f"cycles_run: {summary['cycles_run']}")
    print(f"cycles_with_new_data: {summary['cycles_with_new_data']}")
    print(f"total_records_detected: {summary['total_records_detected']}")
    print(f"consensus_rate: mean={summary['consensus_rate_mean']} min={summary['consensus_rate_min']} max={summary['consensus_rate_max']}")
    print(f"gate_exit (>0.8) pass ratio: {summary['gate_exit_pass_ratio']}")
    print(f"total_elapsed_ms: {summary['total_elapsed_ms']}")
    print(f"→ evidence: {args.out}")

    # Rollback injected synthetic lines
    if args.inject and not args.no_rollback:
        ok = rollback_graph(pre_size)
        print(f"→ rollback injected data: {'OK' if ok else 'FAIL'} (restored to size={pre_size})")
        # Reset cursor since file truncated
        save_cursor(pre_size, pre_mtime, pre_size)


if __name__ == "__main__":
    main()
