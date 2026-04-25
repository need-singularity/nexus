#!/usr/bin/env python3
"""drill engine axiom combinatorial interaction matrix (Ω-saturation cycle 56+).

USAGE:
    python3 nxs_002_axiom_combo.py [--quick] [--pairs] [--triplets] [--seeds N]

CONTEXT (cycle 55 부수 발견 — commit d338cf60):
  C5 = anti-hub (C1) + block (C2) additive 조합 → V3' = 0.92309 ± 0.00641 (5 seeds)
  baseline 0.92740 보다 낮음 → **negative interference (antagonistic)** 확정
  mechanism: anchored block (C2) anchor edge 가 base spectrum perturbation 일으킴 →
              isolated ER (C1) 의 K cut invariance (cycle 32 universal pattern) 깎음

본 file 의 목적: 이 isolated finding 을 axiom space 의 systematic interaction matrix 로 확장.

INDIVIDUAL AXIOM V3' (5 seeds avg, cycle 21+ 측정):
  baseline               V3' = 0.92740
  C1 anti-hub  N=800 p=0.005   V3' = 0.93617 (zero variance — isolated ER + K cut invariance)
  C2 block 2x200 p=0.020       V3' = 0.92755 (anchor edge → small spectrum nudge)
  C3 degree-cap=100            V3' = 0.92005 (destructive — hub trim)
  C4 rewire frac=0.50          V3' = 0.81659 ★ V3' breaker (Maslov-Sneppen)
  C6 hub-decompose K=10        V3' ~ 0.91-0.92 (subhub split)

INTERACTION CLASSIFICATION:
  Δ_X = V3'(X) - baseline (single axiom)
  predicted_additive(A,B) = baseline + Δ_A + Δ_B
  measured(A,B) = V3'(combo)
  interaction = measured - predicted_additive

  synergistic:    interaction > +0.005  (1+1>2)  ★ paper-grade if found
  additive:       |interaction| ≤ 0.005
  antagonistic:   interaction < -0.005  (1+1<2)
  destructive:    measured < min(V3'(A), V3'(B))

PAIR SET (15 pairs from 6 axioms, but C5 의 source 인 C1+C2 known):
  C1+C2 (cycle 55 known antagonistic), C1+C3, C1+C4, C1+C6,
  C2+C3, C2+C4, C2+C6, C3+C4, C3+C6, C4+C6
  (각 C1-C6 individual 도 sanity 측정)

TRIPLET SET (--triplets, 6C3 = 20 triplets — quick 모드 미포함, --triplets 명시 시만):
  C1+C2+C3, C1+C2+C4, C1+C2+C6, C1+C3+C4, ..., C3+C4+C6

CONSTRAINTS:
  - 의존도 0 (shell + python + scipy/numpy only — nxs_002_composite reuse)
  - file scope: 본 file 만 (기존 probe 안 만짐)
  - Ω-saturation cycle: design (header 본 docstring) + impl pair

DEFAULT seed list = [2026, 2027, 2028] (3 seeds quick) or [2026..2030] (--seeds 5 full)

OUTPUT (stdout JSON + stderr human-readable):
    {
      "baseline_v3p": 0.92740,
      "individual": {"C1": ..., "C2": ..., ...},
      "pairs": {"C1+C2": {"measured": ..., "predicted_additive": ..., "interaction": ..., "class": "..."}, ...},
      "triplets": {"C1+C2+C3": {...}, ...},
      "interaction_matrix_summary": {
        "synergistic_pairs": [...], "additive_pairs": [...], "antagonistic_pairs": [...]
      },
      "paper_grade_finding": "..."
    }
"""
import argparse, json, os, sys, time
sys.path.insert(0, os.path.expanduser("~/core/nexus/tool"))
import numpy as np
from scipy.sparse import csr_matrix
from nxs_002_composite import (
    build_csr_from_blowup, laplacian_eigenvalues, paircorr, unfold,
    composite_aligned, load_eig_jsonl, DEFAULT_ATLAS, DEFAULT_CONST,
)

# ----------------------------------------------------------------------
# V3' helpers (mirror /tmp/v3prime_*.py)
# ----------------------------------------------------------------------
def sff(eigs, n_tau=200, tau_max=10.0):
    nz = np.array([v for v in eigs if v > 1e-10])
    if len(nz) < 5: return np.array([])
    E = nz / nz.mean()
    taus = np.linspace(0.01, tau_max, n_tau)
    out = np.zeros(n_tau)
    for ti, tau in enumerate(taus):
        z = np.exp(-1j * E * tau).sum()
        out[ti] = (z * np.conjugate(z)).real / len(E)
    return out

def sff_align(a, b):
    if len(a) != len(b) or len(a) == 0: return 0.5
    na = np.linalg.norm(a); nb = np.linalg.norm(b)
    if na < 1e-12 or nb < 1e-12: return 0.5
    return float(np.dot(a, b) / (na * nb))

# ----------------------------------------------------------------------
# Composable axiom appliers — operate on (rows, cols, n_total) tuples
# instead of csr_matrix so they can be chained.
# ----------------------------------------------------------------------
def _coo_lists_from_csr(A):
    coo = A.tocoo()
    return list(coo.row.tolist()), list(coo.col.tolist())

def apply_C1(state, n_base, rng, N_new=800, p=0.005):
    """C1 anti-hub: append isolated ER batch (N_new nodes, edge prob p)."""
    rows, cols, cur, _hubs = state
    new_idx = list(range(cur, cur + N_new))
    for i in range(N_new):
        for j in range(i+1, N_new):
            if rng.rand() < p:
                rows.extend([new_idx[i], new_idx[j]]); cols.extend([new_idx[j], new_idx[i]])
    return (rows, cols, cur + N_new, _hubs)

def apply_C2(state, n_base, rng, n_blocks=2, block_size=200, p=0.020):
    """C2 block-isolation: K blocks of size sz, each anchored to base by 1 edge."""
    rows, cols, cur, _hubs = state
    for _ in range(n_blocks):
        idx = list(range(cur, cur + block_size))
        for i in range(block_size):
            for j in range(i+1, block_size):
                if rng.rand() < p:
                    rows.extend([idx[i], idx[j]]); cols.extend([idx[j], idx[i]])
        anchor = rng.randint(0, n_base)
        rows.extend([idx[0], int(anchor)]); cols.extend([int(anchor), idx[0]])
        cur += block_size
    return (rows, cols, cur, _hubs)

def apply_C3(state, n_base, rng, cap=100):
    """C3 degree-cap-rebuild: trim base graph edges to enforce per-node cap.
       Note: C3 modifies the BASE graph — must be applied to the initial state."""
    rows, cols, cur, _hubs = state
    # collect unique undirected edges from current rows/cols (they are symmetric pairs)
    seen = set()
    uniq = []
    for u, v in zip(rows, cols):
        if u >= v: continue
        if (u, v) in seen: continue
        seen.add((u, v)); uniq.append((u, v))
    keep = []
    deg = np.zeros(cur, dtype=np.int32)
    rng.shuffle(uniq)
    for u, v in uniq:
        if deg[u] < cap and deg[v] < cap:
            keep.append((u, v)); deg[u] += 1; deg[v] += 1
    # rebuild rows/cols
    new_rows = []; new_cols = []
    for u, v in keep:
        new_rows.extend([u, v]); new_cols.extend([v, u])
    return (new_rows, new_cols, cur, _hubs)

def apply_C4(state, n_base, rng, frac=0.50):
    """C4 random rewire (Maslov-Sneppen, preserves degree). Operates on entire current graph."""
    rows, cols, cur, _hubs = state
    seen = set()
    edges = []
    for u, v in zip(rows, cols):
        if u >= v: continue
        if (u, v) in seen: continue
        seen.add((u, v)); edges.append([u, v])
    n_swaps = int(len(edges) * frac)
    for _ in range(n_swaps):
        i = rng.randint(0, len(edges)); j = rng.randint(0, len(edges))
        if i == j: continue
        a, b = edges[i]; c, d = edges[j]
        if len(set([a, b, c, d])) < 4: continue
        new1 = (min(a, d), max(a, d)); new2 = (min(c, b), max(c, b))
        if new1 in seen or new2 in seen: continue
        seen.discard((a, b)); seen.discard((c, d))
        seen.add(new1); seen.add(new2)
        edges[i] = [new1[0], new1[1]]; edges[j] = [new2[0], new2[1]]
    new_rows = []; new_cols = []
    for u, v in edges:
        new_rows.extend([u, v]); new_cols.extend([v, u])
    return (new_rows, new_cols, cur, _hubs)

def apply_C6(state, n_base, rng, K=10):
    """C6 hub-decompose: split each top-8 base hub into K subhub replicas."""
    rows, cols, cur, hubs = state
    hub_to_replicas = {}
    for h in hubs:
        hub_to_replicas[h] = list(range(cur, cur + K))
        cur += K
    # collect unique edges, redirect endpoints touching hubs
    new_rows = []; new_cols = []
    seen = set()
    src_seen = set()
    for u, v in zip(rows, cols):
        if u >= v: continue
        if (u, v) in src_seen: continue
        src_seen.add((u, v))
        ru = rng.choice(hub_to_replicas[u]) if u in hub_to_replicas else u
        rv = rng.choice(hub_to_replicas[v]) if v in hub_to_replicas else v
        if (ru, rv) in seen: continue
        seen.add((ru, rv))
        new_rows.extend([ru, rv]); new_cols.extend([rv, ru])
    return (new_rows, new_cols, cur, hubs)

AXIOM_APPLIERS = {
    "C1": apply_C1, "C2": apply_C2, "C3": apply_C3,
    "C4": apply_C4, "C6": apply_C6,
}
# C5 omitted intentionally — C5 = C1+C2 by definition (cycle 55 source).
# NOTE: C3, C4 modify base graph; C1, C2 append; C6 expands base hubs. Order matters
# only between modifying axioms; appliers handle current state immutably (return new tuple).
AXIOM_ORDER = ["C3", "C4", "C6", "C1", "C2"]  # apply base-modifiers first, then appenders

def initial_state(A_base, n_base, top_hubs):
    rows, cols = _coo_lists_from_csr(A_base)
    return (rows, cols, n_base, top_hubs)

def state_to_csr(state):
    rows, cols, cur, _ = state
    if not rows:
        return csr_matrix((cur, cur))
    A = csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(cur, cur))
    A.sum_duplicates(); A.data[:] = 1.0
    return A

def measure_v3p(A, R2_const, sff_c, K=100, sigma=1e-3):
    vals = laplacian_eigenvalues(A, K=K, sigma=sigma)
    R2_a = paircorr(unfold(vals))
    v1 = composite_aligned(R2_a, R2_const)["composite_after"]
    sa = sff_align(sff(vals), sff_c)
    v3p = 0.6 * sa + 0.4 * v1
    return float(v1), float(sa), float(v3p)

def measure_combo(combo, A_base, n_base, top_hubs, R2_const, sff_c, seeds, log=sys.stderr):
    """Apply axiom combo for each seed, return list of (v1, sff_align, v3p)."""
    results = []
    for s in seeds:
        rng = np.random.RandomState(s)
        st = initial_state(A_base, n_base, top_hubs)
        for axiom in AXIOM_ORDER:
            if axiom in combo:
                st = AXIOM_APPLIERS[axiom](st, n_base, rng)
        A = state_to_csr(st)
        v1, sa, v3p = measure_v3p(A, R2_const, sff_c)
        results.append((v1, sa, v3p))
        print(f"  combo={'+'.join(combo):<14s} seed={s} n={A.shape[0]} v1={v1:.5f} sff={sa:.5f} v3'={v3p:.5f}", file=log)
    arr = np.array(results)
    return {
        "v1_mean": float(arr[:,0].mean()), "v1_std": float(arr[:,0].std()),
        "sff_mean": float(arr[:,1].mean()), "sff_std": float(arr[:,1].std()),
        "v3p_mean": float(arr[:,2].mean()), "v3p_std": float(arr[:,2].std()),
        "n_seeds": len(seeds),
    }

def classify_interaction(measured_v3p, predicted_additive, individual_v3ps):
    """Return (class_name, interaction_value)."""
    interaction = measured_v3p - predicted_additive
    min_individual = min(individual_v3ps)
    if measured_v3p < min_individual:
        cls = "destructive"
    elif interaction > 0.005:
        cls = "synergistic"
    elif interaction < -0.005:
        cls = "antagonistic"
    else:
        cls = "additive"
    return cls, float(interaction)

def main():
    ap = argparse.ArgumentParser(description="axiom combinatorial interaction matrix")
    ap.add_argument("--quick", action="store_true", help="3 seeds + skip C4 pair (slow due to rewire)")
    ap.add_argument("--pairs", action="store_true", help="run pair sweep (default ON)")
    ap.add_argument("--triplets", action="store_true", help="run triplet sweep (10 triplets, slower)")
    ap.add_argument("--seeds", type=int, default=3, help="seed count (default 3, or 5 for paper)")
    ap.add_argument("--out", default="-", help="JSON output path (default stdout)")
    args = ap.parse_args()

    # default: pairs ON unless --triplets only
    do_pairs = args.pairs or not args.triplets

    seeds = [2026 + i for i in range(args.seeds)]
    print(f"=== axiom combo interaction matrix — {len(seeds)} seeds ===", file=sys.stderr)
    print(f"seeds={seeds}", file=sys.stderr)

    t0 = time.time()
    A_base, n_base = build_csr_from_blowup(DEFAULT_ATLAS)
    const_eigs = load_eig_jsonl(DEFAULT_CONST)
    R2_const = paircorr(unfold(const_eigs))
    sff_c = sff(const_eigs)
    deg_base = np.array(A_base.sum(axis=1)).flatten()
    top_hubs = set(np.argsort(-deg_base)[:8].tolist())
    print(f"atlas n={n_base} hubs={sorted(top_hubs)} t_load={time.time()-t0:.2f}s", file=sys.stderr)

    # baseline (no axiom)
    t1 = time.time()
    base_res = measure_combo([], A_base, n_base, top_hubs, R2_const, sff_c, seeds)
    baseline_v3p = base_res["v3p_mean"]
    print(f"\nbaseline V3'={baseline_v3p:.5f} ± {base_res['v3p_std']:.5f} (t={time.time()-t1:.1f}s)\n", file=sys.stderr)

    # individual axioms
    individual = {}
    individual["baseline"] = base_res
    for axiom in ["C1", "C2", "C3", "C4", "C6"]:
        if args.quick and axiom == "C4":
            print(f"--quick: skipping C4 individual (rewire heavy, use known V3'≈0.81659)", file=sys.stderr)
            individual["C4"] = {"v3p_mean": 0.81659, "v3p_std": 0.01206, "n_seeds": 0, "_quick_known": True}
            continue
        t1 = time.time()
        individual[axiom] = measure_combo([axiom], A_base, n_base, top_hubs, R2_const, sff_c, seeds)
        print(f"individual {axiom} V3'={individual[axiom]['v3p_mean']:.5f} ± {individual[axiom]['v3p_std']:.5f} (t={time.time()-t1:.1f}s)\n", file=sys.stderr)

    delta = {k: individual[k]["v3p_mean"] - baseline_v3p for k in individual if k != "baseline"}
    print(f"individual Δ vs baseline: {json.dumps({k: round(v, 5) for k, v in delta.items()})}\n", file=sys.stderr)

    # ---------------- Pair sweep ----------------
    pair_results = {}
    if do_pairs:
        pair_set = [
            ("C1", "C2"), ("C1", "C3"), ("C1", "C4"), ("C1", "C6"),
            ("C2", "C3"), ("C2", "C4"), ("C2", "C6"),
            ("C3", "C4"), ("C3", "C6"), ("C4", "C6"),
        ]
        for (a, b) in pair_set:
            if args.quick and "C4" in (a, b):
                print(f"--quick: skipping pair {a}+{b} (C4 rewire heavy)", file=sys.stderr)
                continue
            t1 = time.time()
            label = f"{a}+{b}"
            res = measure_combo([a, b], A_base, n_base, top_hubs, R2_const, sff_c, seeds)
            predicted = baseline_v3p + delta[a] + delta[b]
            cls, interaction = classify_interaction(
                res["v3p_mean"], predicted,
                [individual[a]["v3p_mean"], individual[b]["v3p_mean"]]
            )
            pair_results[label] = {
                **res, "predicted_additive": float(predicted),
                "interaction": interaction, "class": cls,
            }
            print(f"PAIR {label} V3'={res['v3p_mean']:.5f}±{res['v3p_std']:.5f} pred_add={predicted:.5f} Δ={interaction:+.5f} class={cls} (t={time.time()-t1:.1f}s)\n", file=sys.stderr)

    # ---------------- Triplet sweep (optional) ----------------
    triplet_results = {}
    if args.triplets:
        from itertools import combinations
        triplet_set = list(combinations(["C1", "C2", "C3", "C6"], 3))  # skip C4 by default
        if not args.quick:
            triplet_set += list(combinations(["C1", "C2", "C3", "C4"], 3))
        triplet_set = [list(t) for t in triplet_set]
        seen = set()
        for combo in triplet_set:
            key = "+".join(sorted(combo))
            if key in seen: continue
            seen.add(key)
            t1 = time.time()
            res = measure_combo(combo, A_base, n_base, top_hubs, R2_const, sff_c, seeds)
            predicted = baseline_v3p + sum(delta[c] for c in combo)
            cls, interaction = classify_interaction(
                res["v3p_mean"], predicted,
                [individual[c]["v3p_mean"] for c in combo]
            )
            triplet_results[key] = {
                **res, "predicted_additive": float(predicted),
                "interaction": interaction, "class": cls,
            }
            print(f"TRIPLET {key} V3'={res['v3p_mean']:.5f}±{res['v3p_std']:.5f} pred_add={predicted:.5f} Δ={interaction:+.5f} class={cls} (t={time.time()-t1:.1f}s)\n", file=sys.stderr)

    # ---------------- Interaction matrix summary ----------------
    by_class = {"synergistic": [], "additive": [], "antagonistic": [], "destructive": []}
    for label, r in pair_results.items():
        by_class[r["class"]].append({"combo": label, "interaction": round(r["interaction"], 5), "v3p": round(r["v3p_mean"], 5)})
    for label, r in triplet_results.items():
        by_class[r["class"]].append({"combo": label, "interaction": round(r["interaction"], 5), "v3p": round(r["v3p_mean"], 5)})

    paper_finding = "no synergistic combos found — axiom space appears antagonistic/additive only"
    if by_class["synergistic"]:
        best = max(by_class["synergistic"], key=lambda x: x["interaction"])
        paper_finding = f"SYNERGISTIC AXIOM FAMILY DISCOVERED: {best['combo']} interaction=+{best['interaction']} (1+1>2 — drill engine new axiom family candidate)"

    output = {
        "schema": "nxs_002_axiom_combo_v1",
        "namespace": "nxs-20260425-001",
        "phase": "phase7_combinatorial",
        "baseline_v3p": baseline_v3p,
        "individual": individual,
        "individual_delta_vs_baseline": {k: round(v, 5) for k, v in delta.items()},
        "pairs": pair_results,
        "triplets": triplet_results,
        "interaction_matrix_summary": by_class,
        "paper_grade_finding": paper_finding,
        "elapsed_s": round(time.time() - t0, 2),
        "config": {
            "C1": "anti-hub N=800 p=0.005",
            "C2": "block 2x200 p=0.020",
            "C3": "degree-cap=100",
            "C4": "rewire frac=0.50",
            "C6": "hub-decompose K=10",
            "apply_order": AXIOM_ORDER,
        },
    }
    payload = json.dumps(output, indent=2, ensure_ascii=False)
    if args.out == "-":
        print(payload)
    else:
        with open(args.out, "w") as f:
            f.write(payload)
        print(f"wrote {args.out}", file=sys.stderr)
    print(f"\n=== INTERACTION MATRIX SUMMARY ===", file=sys.stderr)
    for cls in ["synergistic", "additive", "antagonistic", "destructive"]:
        items = by_class[cls]
        print(f"  {cls:<13s} ({len(items):2d}): {items}", file=sys.stderr)
    print(f"\nPAPER FINDING: {paper_finding}", file=sys.stderr)
    return 0

if __name__ == "__main__":
    sys.exit(main())
