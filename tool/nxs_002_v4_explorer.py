#!/usr/bin/env python3
"""
nxs_002_v4_explorer — V4 multi-dimensional composite metric grid search
========================================================================

본 도구는 V3' (= 0.6·sff_align + 0.4·composite_v1) 의 0.93617 ceiling 너머 closure
를 시도. V3' 는 SFF + paircorr 2-dim. 본 도구는 6 개 추가 metric 후보를 측정하고
3-dim grid search 로 V4 best formula 를 발굴.

Ω-saturation cycle 2026-04-25-001 phase6_v4_metric_cycle_X.

추가 metric 후보:
  M1: spectral gap ratio        — λ_2 / λ_max (적은 → chaotic, 큰 → ordered)
  M2: clustering coefficient    — local triangle density (transitivity)
  M3: modularity Q proxy        — top-2 eigenvector sign partition
  M4: degree assortativity      — Pearson(deg_i, deg_j) over edges
  M5: IPR proxy (existing)      — Σ p_i² where p_i = |λ_i|/Σ|λ|
  M6: spectral entropy          — -Σ p_i log p_i (von Neumann form)

Each metric 의 align score = 1 - |M(atlas) - M(const_proxy)| / max(|M_a|,|M_c|,eps).

V4 = α·sff_align + β·composite_v1 + γ·extra_metric_align (α+β+γ=1).
Grid search γ ∈ [0.0, 0.5], (α,β) preserving 0.6:0.4 ratio of remaining (1-γ).
또한 4-dim 에서는 best 2 extras 추가, full grid (small step).

USAGE:
  python3 tool/nxs_002_v4_explorer.py
  python3 tool/nxs_002_v4_explorer.py --atlas n6/atlas.blowup.jsonl
  python3 tool/nxs_002_v4_explorer.py --include-anti-hub --include-rewire
  python3 tool/nxs_002_v4_explorer.py --4d --step 0.05

OUTPUT (stdout JSON, one of):
  {"schema":"nxs_002_v4_explorer.v1", "best_v4":..., "ceiling_break":..., ...}

EXIT 0 always (반드시 metrics 산출). 1 if input fail.
"""
from __future__ import annotations

import argparse, json, os, sys, time
from typing import Dict, List, Tuple

import numpy as np
from scipy.sparse import csr_matrix, diags
from scipy.sparse.linalg import eigsh
from scipy.sparse.csgraph import connected_components

# Reuse builders from nxs_002_composite (Python pipeline SSOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nxs_002_composite import (  # noqa: E402
    build_csr_from_blowup, laplacian_eigenvalues, paircorr, unfold,
    composite_aligned, load_eig_jsonl, DEFAULT_ATLAS, DEFAULT_CONST,
)

# ─────────────────────── core spectra metrics ───────────────────────

def sff(eigs: np.ndarray, n_tau: int = 200, tau_max: float = 10.0) -> np.ndarray:
    """Spectral Form Factor K(τ) = |Σ exp(-i E_n τ)|² / N (E normalized by mean)."""
    nz = np.array([v for v in eigs if v > 1e-10])
    if len(nz) < 5:
        return np.array([])
    E = nz / nz.mean()
    taus = np.linspace(0.01, tau_max, n_tau)
    out = np.zeros(n_tau)
    for ti, tau in enumerate(taus):
        z = np.exp(-1j * E * tau).sum()
        out[ti] = (z * np.conjugate(z)).real / len(E)
    return out


def sff_align(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) != len(b) or len(a) == 0:
        return 0.5
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na < 1e-12 or nb < 1e-12:
        return 0.5
    return float(np.dot(a, b) / (na * nb))


# ─────────────────────── extra metric scalars ───────────────────────

def m1_spectral_gap_ratio(eigs: np.ndarray) -> float:
    """λ_2 / λ_max — 작은 = chaotic 큰 gap; 큰 = nearly-degenerate."""
    nz = np.sort(eigs[eigs > 1e-10])
    if len(nz) < 2:
        return 0.5
    return float(nz[1] / nz[-1])


def m2_clustering_coefficient(A: csr_matrix) -> float:
    """global clustering = 3·triangles / connected_triples (transitivity)."""
    if A is None or A.shape[0] == 0:
        return 0.0
    A2 = A @ A
    A3 = A2 @ A
    triangles = float(A3.diagonal().sum()) / 6.0
    deg = np.asarray(A.sum(axis=1)).flatten()
    triples = float(np.sum(deg * (deg - 1)) / 2.0)
    if triples <= 0:
        return 0.0
    return float(3.0 * triangles / triples)


def m3_modularity_proxy(eigs: np.ndarray) -> float:
    """signal vs noise of mid-spectrum: ratio top-half mean / bottom-half mean.
    Pure spectral-only proxy (no full Newman partition needed)."""
    nz = np.sort(eigs[eigs > 1e-10])
    n = len(nz)
    if n < 4:
        return 0.5
    half = n // 2
    bot = nz[:half].mean()
    top = nz[half:].mean()
    if top <= 0:
        return 0.5
    # Map to (0, 1] — closer to 1 if spectrum is uniform; closer to 0 if heavy tail
    r = bot / top
    return float(r)


def m4_degree_assortativity(A: csr_matrix) -> float:
    """Newman r — Pearson correlation of degrees across edges."""
    if A is None or A.shape[0] == 0:
        return 0.0
    coo = A.tocoo()
    deg = np.asarray(A.sum(axis=1)).flatten()
    src_deg = deg[coo.row]
    dst_deg = deg[coo.col]
    if len(src_deg) < 2:
        return 0.0
    sx = src_deg.std()
    sy = dst_deg.std()
    if sx < 1e-12 or sy < 1e-12:
        return 0.0
    return float(np.corrcoef(src_deg, dst_deg)[0, 1])


def m5_ipr_proxy(eigs: np.ndarray) -> float:
    """Σ p_i² where p_i = |λ_i|/Σ|λ|."""
    nz = np.abs(np.array(eigs))
    s = nz.sum()
    if s < 1e-12:
        return 0.5
    p = nz / s
    return float((p * p).sum())


def m6_spectral_entropy(eigs: np.ndarray) -> float:
    """von Neumann form entropy normalized by log(N)."""
    nz = np.abs(np.array(eigs))
    nz = nz[nz > 1e-12]
    s = nz.sum()
    if s < 1e-12 or len(nz) < 2:
        return 0.5
    p = nz / s
    H = -np.sum(p * np.log(p))
    Hmax = np.log(len(p))
    if Hmax <= 0:
        return 0.5
    return float(H / Hmax)


def align_scalar(a: float, b: float) -> float:
    """generic scalar align: 1 - |a-b| / (max(|a|,|b|) + eps)."""
    mx = max(abs(a), abs(b), 1e-12)
    return float(1.0 - abs(a - b) / mx)


# ─────────────────────── const-side metric estimation ───────────────────────

def const_metric_proxies(const_eigs: np.ndarray) -> Dict[str, float]:
    """const SSOT 는 graph 가 아니라 numeric series — A 기반 metric (M2, M4) 은
    spectrum-based proxy 로 대체. (M2 → λ heterogeneity, M4 → spectral skew)."""
    nz = np.sort(np.abs(const_eigs))
    nz = nz[nz > 1e-12]
    out: Dict[str, float] = {}
    out["m1"] = m1_spectral_gap_ratio(nz) if len(nz) > 1 else 0.5
    # M2 proxy: spectrum dispersion (cv = std/mean) mapped to (0,1)
    if len(nz) > 1 and nz.mean() > 0:
        cv = nz.std() / nz.mean()
        out["m2"] = float(1.0 / (1.0 + cv))
    else:
        out["m2"] = 0.5
    out["m3"] = m3_modularity_proxy(nz)
    # M4 proxy: spectral skew (sign of (mean - median)/std)
    if len(nz) > 2 and nz.std() > 0:
        skew = float((nz.mean() - np.median(nz)) / nz.std())
        out["m4"] = float(np.tanh(skew))  # bounded
    else:
        out["m4"] = 0.0
    out["m5"] = m5_ipr_proxy(nz)
    out["m6"] = m6_spectral_entropy(nz)
    return out


def atlas_metric_scalars(A: csr_matrix, eigs: np.ndarray) -> Dict[str, float]:
    return {
        "m1": m1_spectral_gap_ratio(eigs),
        "m2": m2_clustering_coefficient(A),
        "m3": m3_modularity_proxy(eigs),
        "m4": m4_degree_assortativity(A),
        "m5": m5_ipr_proxy(eigs),
        "m6": m6_spectral_entropy(eigs),
    }


# ─────────────────────── perturbation builders ───────────────────────

def build_anti_hub_atlas(A_base: csr_matrix, n_base: int,
                         block_size: int = 800, p: float = 0.005,
                         seed: int = 2026) -> Tuple[csr_matrix, int]:
    """C1 anti-hub: pure isolated ER batch (no anchor edges)."""
    rng = np.random.RandomState(seed)
    coo = A_base.tocoo()
    rows = list(coo.row); cols = list(coo.col)
    idx_off = n_base
    new_rows: List[int] = []
    new_cols: List[int] = []
    for i in range(block_size):
        for j in range(i + 1, block_size):
            if rng.rand() < p:
                a = idx_off + i
                b = idx_off + j
                new_rows.extend([a, b])
                new_cols.extend([b, a])
    rows.extend(new_rows); cols.extend(new_cols)
    n_total = n_base + block_size
    A_new = csr_matrix(
        (np.ones(len(rows)), (np.array(rows, dtype=np.int64), np.array(cols, dtype=np.int64))),
        shape=(n_total, n_total),
    )
    A_new.sum_duplicates()
    A_new.data[:] = 1.0
    return A_new, n_total


def build_rewire_atlas(A_base: csr_matrix, n_base: int,
                       frac: float = 0.5, seed: int = 2026) -> Tuple[csr_matrix, int]:
    """C4 Maslov-Sneppen partial rewire — V3' breaker."""
    rng = np.random.RandomState(seed)
    coo = A_base.tocoo()
    # take only upper triangle to dedupe edges
    mask = coo.row < coo.col
    edges_r = coo.row[mask]
    edges_c = coo.col[mask]
    m = len(edges_r)
    n_swap = int(m * frac)
    er = edges_r.copy().astype(np.int64)
    ec = edges_c.copy().astype(np.int64)
    for _ in range(n_swap):
        i, j = rng.randint(0, m, size=2)
        if i == j:
            continue
        # swap endpoints (i.col <-> j.col)
        ec[i], ec[j] = ec[j], ec[i]
    rows = np.concatenate([er, ec])
    cols = np.concatenate([ec, er])
    A_new = csr_matrix(
        (np.ones(len(rows)), (rows, cols)),
        shape=(n_base, n_base),
    )
    A_new.sum_duplicates()
    A_new.data[:] = 1.0
    return A_new, n_base


# ─────────────────────── pipeline per atlas variant ───────────────────────

def measure_variant(label: str, A: csr_matrix, n: int,
                    R2_const: np.ndarray, sff_const: np.ndarray,
                    const_metrics: Dict[str, float],
                    K: int = 100, sigma: float = 1e-3) -> Dict:
    vals = laplacian_eigenvalues(A, K=K, sigma=sigma)
    R2_atlas = paircorr(unfold(vals))
    v1 = composite_aligned(R2_atlas, R2_const)["composite_after"]
    sff_atlas = sff(vals)
    sa = sff_align(sff_atlas, sff_const)
    v3p = 0.6 * sa + 0.4 * v1

    atlas_metrics = atlas_metric_scalars(A, vals)
    aligns: Dict[str, float] = {}
    for k in atlas_metrics:
        aligns[k] = align_scalar(atlas_metrics[k], const_metrics[k])

    n_cc, _ = connected_components(A, directed=False)
    return {
        "label": label,
        "n_nodes": int(n),
        "n_components": int(n_cc),
        "n_eig_nz": int((vals > 1e-10).sum()),
        "composite_v1": round(v1, 6),
        "sff_align": round(sa, 6),
        "composite_v3_prime": round(v3p, 6),
        "atlas_metrics": {k: round(v, 6) for k, v in atlas_metrics.items()},
        "metric_aligns": {k: round(v, 6) for k, v in aligns.items()},
    }


# ─────────────────────── grid search ───────────────────────

def grid_search_3d(measurements: Dict[str, Dict],
                   gamma_step: float = 0.05) -> Dict:
    """For each extra metric M and each γ ∈ {0,gamma_step,...,0.5}, compute
    V4 = (1-γ)*(0.6·sff_align + 0.4·v1) + γ·M_align across labels.
    Best = max over (label_baseline_or_better, M, γ) where we want V4 ≥ V3'."""
    metrics = ["m1", "m2", "m3", "m4", "m5", "m6"]
    gammas = np.arange(0.0, 0.51, gamma_step)
    rows: List[Dict] = []
    for label, data in measurements.items():
        v1 = data["composite_v1"]
        sa = data["sff_align"]
        v3p_native = 0.6 * sa + 0.4 * v1
        for m in metrics:
            ma = data["metric_aligns"][m]
            for g in gammas:
                v4 = (1.0 - g) * v3p_native + g * ma
                rows.append({
                    "label": label,
                    "extra_metric": m,
                    "gamma": float(round(g, 3)),
                    "alpha": float(round((1.0 - g) * 0.6, 4)),
                    "beta": float(round((1.0 - g) * 0.4, 4)),
                    "v4": round(v4, 6),
                    "v3_prime_native": round(v3p_native, 6),
                    "delta_vs_v3p": round(v4 - v3p_native, 6),
                })
    rows.sort(key=lambda r: r["v4"], reverse=True)
    # absolute best (includes extreme γ even if it lowers v3p; we also pick best
    # γ>0 that improves vs γ=0)
    best_overall = rows[0]
    best_improve_vs_v3p = max(rows, key=lambda r: r["delta_vs_v3p"])

    # Discriminating-power filter: V4 must keep V3' breaker discrimination.
    # I.e., for the same (extra_metric, gamma) coefficients, baseline/anti_hub
    # passes ≥0.9 AND rewire stays <0.9. This is the paper-grade requirement.
    discrim: List[Dict] = []
    by_coef: Dict[Tuple[str, float], Dict[str, float]] = {}
    for r in rows:
        key = (r["extra_metric"], r["gamma"])
        by_coef.setdefault(key, {})[r["label"]] = r["v4"]
    for (m, g), labels in by_coef.items():
        v_base = labels.get("baseline", float("nan"))
        v_ah = labels.get("anti_hub_c1", float("nan"))
        v_rw = labels.get("rewire_c4", float("nan"))
        passes_pos = (v_base >= 0.9) and (v_ah >= 0.9)
        breaks_neg = v_rw < 0.9 if not np.isnan(v_rw) else True
        if passes_pos and breaks_neg:
            discrim.append({
                "extra_metric": m, "gamma": g,
                "v4_baseline": round(v_base, 6),
                "v4_anti_hub": round(v_ah, 6),
                "v4_rewire": round(v_rw, 6) if not np.isnan(v_rw) else None,
                "discrim_gap": round(min(v_base, v_ah) - v_rw, 6) if not np.isnan(v_rw) else None,
            })
    discrim.sort(key=lambda r: r["v4_anti_hub"], reverse=True)
    return {
        "all_combinations_n": len(rows),
        "top_10": rows[:10],
        "best_overall": best_overall,
        "best_improvement_over_v3prime": best_improve_vs_v3p,
        "discriminating_top_10": discrim[:10],
        "n_discriminating": len(discrim),
    }


def grid_search_4d(measurements: Dict[str, Dict],
                   step: float = 0.1) -> Dict:
    """V4 = α·sff_align + β·v1 + γ·M_a + δ·M_b s.t. α+β+γ+δ=1, all ≥ 0."""
    metrics = ["m1", "m2", "m3", "m4", "m5", "m6"]
    rows: List[Dict] = []
    grid = np.arange(0.0, 1.0 + 1e-9, step)
    for label, data in measurements.items():
        v1 = data["composite_v1"]
        sa = data["sff_align"]
        v3p_native = 0.6 * sa + 0.4 * v1
        for i, ma_key in enumerate(metrics):
            for mb_key in metrics[i + 1:]:
                ma = data["metric_aligns"][ma_key]
                mb = data["metric_aligns"][mb_key]
                for a in grid:
                    for b in grid:
                        if a + b > 1.0 + 1e-9:
                            continue
                        for c in grid:
                            d = 1.0 - a - b - c
                            if d < -1e-9 or d > 1.0 + 1e-9:
                                continue
                            d = max(0.0, d)
                            v4 = a * sa + b * v1 + c * ma + d * mb
                            rows.append({
                                "label": label,
                                "metric_a": ma_key,
                                "metric_b": mb_key,
                                "alpha_sff": float(round(a, 3)),
                                "beta_v1": float(round(b, 3)),
                                "gamma_a": float(round(c, 3)),
                                "delta_b": float(round(d, 3)),
                                "v4": round(v4, 6),
                                "delta_vs_v3p": round(v4 - v3p_native, 6),
                            })
    rows.sort(key=lambda r: r["v4"], reverse=True)
    return {
        "all_combinations_n": len(rows),
        "top_10": rows[:10],
        "best_overall": rows[0],
        "best_improvement_over_v3prime": max(rows, key=lambda r: r["delta_vs_v3p"]),
    }


# ─────────────────────── main ───────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(description="V4 multi-dim composite explorer")
    ap.add_argument("--atlas", default=DEFAULT_ATLAS)
    ap.add_argument("--const", default=DEFAULT_CONST)
    ap.add_argument("-K", type=int, default=100)
    ap.add_argument("--sigma", type=float, default=1e-3)
    ap.add_argument("--include-anti-hub", action="store_true", default=True,
                    help="C1 anti-hub variant 측정 (default ON)")
    ap.add_argument("--no-anti-hub", dest="include_anti_hub", action="store_false")
    ap.add_argument("--include-rewire", action="store_true", default=True,
                    help="C4 rewire variant 측정 (default ON)")
    ap.add_argument("--no-rewire", dest="include_rewire", action="store_false")
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--block-size", type=int, default=800)
    ap.add_argument("--p", type=float, default=0.005)
    ap.add_argument("--gamma-step", type=float, default=0.05)
    ap.add_argument("--4d", dest="four_d", action="store_true",
                    help="4-dim full grid search 추가 (느림)")
    ap.add_argument("--step-4d", type=float, default=0.2,
                    help="4-dim grid step (default 0.2 — 6 levels per axis)")
    args = ap.parse_args()

    t0 = time.time()
    if not os.path.isfile(args.atlas):
        print(json.dumps({"error": f"atlas missing: {args.atlas}"}), file=sys.stderr)
        return 1
    if not os.path.isfile(args.const):
        print(json.dumps({"error": f"const missing: {args.const}"}), file=sys.stderr)
        return 1

    print(f"[v4] loading atlas: {args.atlas}", file=sys.stderr)
    A_base, n_base = build_csr_from_blowup(args.atlas)
    if A_base is None or n_base == 0:
        print(json.dumps({"error": "empty atlas"}), file=sys.stderr)
        return 1

    print(f"[v4] loading const: {args.const}", file=sys.stderr)
    const_eigs = load_eig_jsonl(args.const)
    R2_const = paircorr(unfold(const_eigs))
    sff_const = sff(const_eigs)
    const_metrics = const_metric_proxies(const_eigs)
    print(f"[v4] const_metrics: {const_metrics}", file=sys.stderr)

    measurements: Dict[str, Dict] = {}

    # Baseline
    print(f"[v4] measuring baseline (n={n_base})...", file=sys.stderr)
    measurements["baseline"] = measure_variant(
        "baseline", A_base, n_base, R2_const, sff_const, const_metrics,
        K=args.K, sigma=args.sigma,
    )
    print(f"[v4] baseline V3'={measurements['baseline']['composite_v3_prime']}", file=sys.stderr)

    # C1 anti-hub
    if args.include_anti_hub:
        print(f"[v4] measuring C1 anti-hub (block={args.block_size}, p={args.p})...", file=sys.stderr)
        A_ah, n_ah = build_anti_hub_atlas(A_base, n_base,
                                          block_size=args.block_size,
                                          p=args.p, seed=args.seed)
        measurements["anti_hub_c1"] = measure_variant(
            "anti_hub_c1", A_ah, n_ah, R2_const, sff_const, const_metrics,
            K=args.K, sigma=args.sigma,
        )
        print(f"[v4] anti_hub V3'={measurements['anti_hub_c1']['composite_v3_prime']}", file=sys.stderr)

    # C4 rewire
    if args.include_rewire:
        print(f"[v4] measuring C4 rewire (frac=0.5)...", file=sys.stderr)
        A_rw, n_rw = build_rewire_atlas(A_base, n_base, frac=0.5, seed=args.seed)
        measurements["rewire_c4"] = measure_variant(
            "rewire_c4", A_rw, n_rw, R2_const, sff_const, const_metrics,
            K=args.K, sigma=args.sigma,
        )
        print(f"[v4] rewire V3'={measurements['rewire_c4']['composite_v3_prime']}", file=sys.stderr)

    # 3-dim grid search
    print("[v4] 3-dim grid search...", file=sys.stderr)
    g3 = grid_search_3d(measurements, gamma_step=args.gamma_step)

    out: Dict = {
        "schema": "nxs_002_v4_explorer.v1",
        "ts": int(time.time()),
        "atlas_path": args.atlas,
        "const_path": args.const,
        "K": args.K,
        "sigma": args.sigma,
        "n_atlas_base": int(n_base),
        "const_metrics_proxy": {k: round(v, 6) for k, v in const_metrics.items()},
        "measurements": measurements,
        "grid_3d": g3,
        "v3prime_known_max": 0.93617,
        "paper_trigger_threshold": 0.9,
    }

    if args.four_d:
        print("[v4] 4-dim grid search (slow)...", file=sys.stderr)
        g4 = grid_search_4d(measurements, step=args.step_4d)
        out["grid_4d"] = g4

    # ceiling break analysis
    best_v4 = g3["best_overall"]["v4"]
    out["ceiling_break_vs_v3p"] = round(best_v4 - 0.93617, 6)
    out["paper_trigger_passed"] = bool(best_v4 >= 0.9)
    out["elapsed_s"] = round(time.time() - t0, 3)

    print(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
