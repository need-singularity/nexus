#!/usr/bin/env python3
"""Ω-saturation cycle 11: 3-branch 통합 — const reverse-engineering + 새 metric + atlas surgery.

Cycle 10 negative finding: composite paircorr R2 alignment 은 graph TYPE 매칭이지
LSR/chaos signature 매칭이 아님. Cycle 11 = (a) const 의 R2 가 어떤 graph type
인지 역설계 → (b) SFF/IPR 추가 dim → (c) atlas hub destructive surgery 재방문.

const finding (cycle 11 prelim): 40 positive eigenvalues, **log-scale 물리 상수**
(log 2, log 3, log 5, ...). LSR=0.5232 — Poisson (0.386) 와 GOE (0.5359) 사이.
GUE 0.5996 까지 chaotic 하지 않음. 약 GOE / semi-integrable.

Branches:
  (a) const_match: 후보 graph 6종의 R2 vs const R2 KL/L2 거리 → best fit
  (b) extended_metric: SFF (Spectral Form Factor) + IPR (Inverse Participation Ratio)
      를 composite alignment 의 추가 dim 으로 통합 → composite_v2
  (c) hub_surgery: degree-cap sweep (5/10/50/100/200/500) + hub-decompose K sweep
      (QRNG seed) → atlas 직접 수술 ROI
"""
import argparse, hashlib, json, os, sys, time
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components
from scipy.sparse.linalg import eigsh
from scipy.stats import unitary_group, entropy

sys.path.insert(0, os.path.expanduser("~/core/nexus/tool"))
from nxs_002_composite import (
    build_csr_from_blowup, laplacian_eigenvalues, paircorr, unfold,
    composite_aligned, load_eig_jsonl, DEFAULT_ATLAS, DEFAULT_CONST,
)


def lsr_mean(vals):
    nz = np.sort(vals[vals > 1e-10])
    s = np.diff(nz)
    if len(s) < 2:
        return None
    r = np.minimum(s[:-1], s[1:]) / np.maximum(s[:-1], s[1:])
    return float(np.mean(r))


def spectral_form_factor(vals, n_tau=50, tau_max=10.0):
    """K(τ) = |Σ exp(-i E_n τ)|² / N — connected correlations all scales.
    Atlas vs const SFF shape 비교용."""
    nz = vals[vals > 1e-10]
    if len(nz) < 5:
        return None, None
    E = nz / nz.mean()
    taus = np.linspace(0.01, tau_max, n_tau)
    sff = np.zeros(n_tau)
    for i, t in enumerate(taus):
        z = np.sum(np.exp(-1j * E * t))
        sff[i] = float(np.abs(z) ** 2 / len(E))
    return taus, sff


def ipr_proxy(vals):
    """Spectrum 의 IPR proxy: Σ p_i² where p_i = |λ_i| / Σ |λ_j|.
    Localized = high IPR, delocalized = low IPR."""
    nz = vals[vals > 1e-10]
    if len(nz) < 2:
        return None
    p = np.abs(nz) / np.sum(np.abs(nz))
    return float(np.sum(p ** 2))


def r2_kl_distance(R2_a, R2_b, eps=1e-9):
    """KL(R2_a || R2_b) — atlas 후보 vs const target."""
    pa = R2_a + eps
    pb = R2_b + eps
    pa = pa / pa.sum()
    pb = pb / pb.sum()
    return float(entropy(pa, pb))


def coo_lists(A):
    coo = A.tocoo()
    return list(coo.row), list(coo.col)


# ---------- (a) const reverse-engineering: 후보 graph 6종 ----------

def gen_er(n, p, seed):
    rng = np.random.default_rng(seed)
    rows, cols = [], []
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < p:
                rows.extend([i, j]); cols.extend([j, i])
    A = csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(n, n))
    A.sum_duplicates(); A.data[:] = 1.0
    return A


def gen_rrg(n, k, seed):
    rng = np.random.default_rng(seed)
    edge_set = set()
    for _ in range(k):
        perm = rng.permutation(n)
        for i in range(0, n - 1, 2):
            a, b = int(perm[i]), int(perm[i + 1])
            edge_set.add((min(a, b), max(a, b)))
    rows, cols = [], []
    for a, b in edge_set:
        rows.extend([a, b]); cols.extend([b, a])
    A = csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(n, n))
    A.sum_duplicates(); A.data[:] = 1.0
    return A


def gen_ba_scale_free(n, m, seed):
    """Barabási–Albert preferential attachment."""
    rng = np.random.default_rng(seed)
    rows, cols = [], []
    deg = np.zeros(n, dtype=np.int64)
    for i in range(m):
        for j in range(i + 1, m):
            rows.extend([i, j]); cols.extend([j, i])
            deg[i] += 1; deg[j] += 1
    for new in range(m, n):
        targets = set()
        while len(targets) < m:
            total = deg[:new].sum()
            r = rng.random() * total
            cum = 0.0
            for k_idx in range(new):
                cum += deg[k_idx]
                if r <= cum:
                    targets.add(k_idx); break
        for t in targets:
            rows.extend([new, t]); cols.extend([t, new])
            deg[new] += 1; deg[t] += 1
    A = csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(n, n))
    A.sum_duplicates(); A.data[:] = 1.0
    return A


def gen_modular(n, n_blocks, p_in, p_out, seed):
    rng = np.random.default_rng(seed)
    block_size = n // n_blocks
    rows, cols = [], []
    for b in range(n_blocks):
        idx = list(range(b * block_size, (b + 1) * block_size))
        for i in range(len(idx)):
            for j in range(i + 1, len(idx)):
                if rng.random() < p_in:
                    rows.extend([idx[i], idx[j]]); cols.extend([idx[j], idx[i]])
    n_total = block_size * n_blocks
    for i in range(n_total):
        for j in range(i + 1, n_total):
            if (i // block_size) != (j // block_size):
                if rng.random() < p_out:
                    rows.extend([i, j]); cols.extend([j, i])
    A = csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(n_total, n_total))
    A.sum_duplicates(); A.data[:] = 1.0
    return A


def gen_goe_thresholded(n, threshold, seed):
    """GOE matrix → |H_ij| > threshold 이면 edge → real-symmetric chaotic spectrum."""
    rng = np.random.default_rng(seed)
    H = rng.standard_normal((n, n))
    H = (H + H.T) / 2
    np.fill_diagonal(H, 0)
    mask = np.abs(H) > threshold
    rows, cols = np.where(mask)
    A = csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(n, n))
    A.sum_duplicates(); A.data[:] = 1.0
    return A


def gen_path_like(n, p_extra, seed):
    """Path/chain + ER perturbation — log-scale const 의 monotone-like 구조 시뮬."""
    rng = np.random.default_rng(seed)
    rows, cols = [], []
    for i in range(n - 1):
        rows.extend([i, i + 1]); cols.extend([i + 1, i])
    for i in range(n):
        for j in range(i + 2, n):
            if rng.random() < p_extra:
                rows.extend([i, j]); cols.extend([j, i])
    A = csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(n, n))
    A.sum_duplicates(); A.data[:] = 1.0
    return A


def measure_graph_spectrum(A, K=None, sigma=1e-3):
    n = A.shape[0]
    K = min(K or 40, n - 2)
    try:
        deg = np.array(A.sum(axis=1)).flatten()
        from scipy.sparse import diags
        L = (diags(deg) - A).tocsc()
        vals, _ = eigsh(L, k=K, sigma=sigma, which='LM', tol=1e-5, maxiter=3000)
        return np.sort(np.clip(vals, 0.0, None))
    except Exception as e:
        return None


def reverse_engineer_const(const_path, n_synth=400, K_match=40, n_runs=3):
    """const R2 와 가장 가까운 graph type 찾기."""
    const_vals = load_eig_jsonl(const_path)
    R2_const = paircorr(unfold(const_vals))
    lsr_const = lsr_mean(const_vals)
    candidates = [
        ("ER p=0.005", lambda s: gen_er(n_synth, 0.005, s)),
        ("ER p=0.010", lambda s: gen_er(n_synth, 0.010, s)),
        ("ER p=0.020", lambda s: gen_er(n_synth, 0.020, s)),
        ("ER p=0.050", lambda s: gen_er(n_synth, 0.050, s)),
        ("RRG k=3", lambda s: gen_rrg(n_synth, 3, s)),
        ("RRG k=4", lambda s: gen_rrg(n_synth, 4, s)),
        ("RRG k=6", lambda s: gen_rrg(n_synth, 6, s)),
        ("BA m=2", lambda s: gen_ba_scale_free(min(n_synth, 100), 2, s)),
        ("BA m=4", lambda s: gen_ba_scale_free(min(n_synth, 100), 4, s)),
        ("Modular 4×100 in=0.05 out=0.001", lambda s: gen_modular(n_synth, 4, 0.05, 0.001, s)),
        ("Modular 4×100 in=0.10 out=0.005", lambda s: gen_modular(n_synth, 4, 0.10, 0.005, s)),
        ("GOE-thresh τ=2.0", lambda s: gen_goe_thresholded(n_synth, 2.0, s)),
        ("GOE-thresh τ=2.5", lambda s: gen_goe_thresholded(n_synth, 2.5, s)),
        ("Path+ER p=0.005", lambda s: gen_path_like(n_synth, 0.005, s)),
        ("Path+ER p=0.020", lambda s: gen_path_like(n_synth, 0.020, s)),
    ]
    results = []
    for name, gen in candidates:
        kls, lsrs, n_ccs = [], [], []
        for run in range(n_runs):
            seed = 4000 + run * 31 + hash(name) % 997
            try:
                A = gen(seed)
                vals = measure_graph_spectrum(A, K=K_match)
                if vals is None or len(vals) < 5:
                    continue
                R2 = paircorr(unfold(vals))
                kls.append(r2_kl_distance(R2, R2_const))
                lsrs.append(lsr_mean(vals))
                n_ccs.append(connected_components(A, directed=False)[0])
            except Exception as e:
                continue
        if not kls:
            continue
        results.append({
            "name": name,
            "kl_mean": round(float(np.mean(kls)), 5),
            "kl_min": round(float(np.min(kls)), 5),
            "lsr_mean": round(float(np.mean([x for x in lsrs if x is not None])), 4) if lsrs else None,
            "lsr_const": round(lsr_const, 4),
            "n_cc_mean": round(float(np.mean(n_ccs)), 1),
            "n_runs": len(kls),
        })
    results.sort(key=lambda r: r["kl_mean"])
    return {"const_lsr": round(lsr_const, 4),
            "const_n_eigenvalues": int((const_vals > 1e-10).sum()),
            "candidates_ranked_by_kl": results}


# ---------- (b) extended composite metric (SFF + IPR + paircorr) ----------

def extended_composite(A_atlas_vals, const_vals):
    """SFF + IPR + paircorr 3 dim alignment."""
    R2_a = paircorr(unfold(A_atlas_vals))
    R2_c = paircorr(unfold(const_vals))
    base = composite_aligned(R2_a, R2_c)

    _, sff_a = spectral_form_factor(A_atlas_vals)
    _, sff_c = spectral_form_factor(const_vals)
    sff_dist = None
    sff_align = None
    if sff_a is not None and sff_c is not None:
        sff_a_n = sff_a / (np.linalg.norm(sff_a) + 1e-12)
        sff_c_n = sff_c / (np.linalg.norm(sff_c) + 1e-12)
        sff_align = float(np.dot(sff_a_n, sff_c_n))
        sff_dist = float(np.linalg.norm(sff_a_n - sff_c_n))

    ipr_a = ipr_proxy(A_atlas_vals)
    ipr_c = ipr_proxy(const_vals)
    ipr_align = None
    if ipr_a is not None and ipr_c is not None:
        ipr_align = float(1.0 - abs(ipr_a - ipr_c) / (max(ipr_a, ipr_c) + 1e-12))

    extra_dims = [x for x in [sff_align, ipr_align] if x is not None]
    composite_v2 = (base["composite_after"] * 3 + sum(extra_dims)) / (3 + len(extra_dims))
    return {
        "composite_v1": round(base["composite_after"], 5),
        "composite_v2": round(composite_v2, 5),
        "sff_align": round(sff_align, 5) if sff_align is not None else None,
        "sff_dist": round(sff_dist, 5) if sff_dist is not None else None,
        "ipr_atlas": round(ipr_a, 6) if ipr_a is not None else None,
        "ipr_const": round(ipr_c, 6) if ipr_c is not None else None,
        "ipr_align": round(ipr_align, 5) if ipr_align is not None else None,
    }


# ---------- (c) atlas hub destructive surgery sweep ----------

def c3_degree_cap(A_base, n_base, cap, ss):
    rng = np.random.default_rng(ss)
    coo = A_base.tocoo()
    seen = set()
    uniq = []
    for u, v in zip(coo.row.tolist(), coo.col.tolist()):
        if u >= v:
            continue
        if (u, v) in seen:
            continue
        seen.add((u, v))
        uniq.append((u, v))
    keep = []
    deg = np.zeros(n_base, dtype=np.int32)
    rng.shuffle(uniq)
    for u, v in uniq:
        if deg[u] < cap and deg[v] < cap:
            keep.append((u, v)); deg[u] += 1; deg[v] += 1
    rows, cols = [], []
    for u, v in keep:
        rows.extend([u, v]); cols.extend([v, u])
    A_new = csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(n_base, n_base))
    A_new.sum_duplicates(); A_new.data[:] = 1.0
    return A_new


def c6_hub_decompose(A_base, n_base, top_hubs, K, ss):
    rng = np.random.default_rng(ss)
    coo = A_base.tocoo()
    edges = list(zip(coo.row.tolist(), coo.col.tolist()))
    hub_to_replicas = {}
    cur = n_base
    for h in top_hubs:
        hub_to_replicas[int(h)] = list(range(cur, cur + K))
        cur += K
    n_total = cur
    rows, cols = [], []
    seen = set()
    for u, v in edges:
        if u >= v:
            continue
        ru = int(rng.choice(hub_to_replicas[u])) if u in hub_to_replicas else u
        rv = int(rng.choice(hub_to_replicas[v])) if v in hub_to_replicas else v
        if (ru, rv) in seen:
            continue
        seen.add((ru, rv))
        rows.extend([ru, rv]); cols.extend([rv, ru])
    A_new = csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(n_total, n_total))
    A_new.sum_duplicates(); A_new.data[:] = 1.0
    return A_new


def hub_surgery_sweep(A_base, n_base, R2_const, const_vals, K=100, sigma=1e-3, n_runs=3):
    deg = np.array(A_base.sum(axis=1)).flatten()
    top_hubs = np.argsort(-deg)[:8].tolist()
    base_vals = laplacian_eigenvalues(A_base, K=K, sigma=sigma)
    base = composite_aligned(paircorr(unfold(base_vals)), R2_const)
    base_composite = base["composite_after"]

    sweeps = [
        ("C3 degree-cap=5", "c3", 5),
        ("C3 degree-cap=10", "c3", 10),
        ("C3 degree-cap=20", "c3", 20),
        ("C3 degree-cap=50", "c3", 50),
        ("C3 degree-cap=100", "c3", 100),
        ("C3 degree-cap=200", "c3", 200),
        ("C3 degree-cap=500", "c3", 500),
        ("C6 hub-decompose K=10", "c6", 10),
        ("C6 hub-decompose K=20", "c6", 20),
        ("C6 hub-decompose K=50", "c6", 50),
        ("C6 hub-decompose K=100", "c6", 100),
    ]
    out = []
    for label, kind, param in sweeps:
        deltas = []
        v2s = []
        ccs = []
        ns = []
        for run in range(n_runs):
            ss = np.random.SeedSequence(int.from_bytes(os.urandom(8), "big"))
            t0 = time.time()
            if kind == "c3":
                A_new = c3_degree_cap(A_base, n_base, param, ss)
            else:
                A_new = c6_hub_decompose(A_base, n_base, top_hubs, param, ss)
            try:
                vals = laplacian_eigenvalues(A_new, K=K, sigma=sigma)
            except Exception:
                continue
            res = composite_aligned(paircorr(unfold(vals)), R2_const)
            ext = extended_composite(vals, const_vals)
            deltas.append(res["composite_after"] - base_composite)
            v2s.append(ext["composite_v2"] - base_composite)
            ccs.append(connected_components(A_new, directed=False)[0])
            ns.append(A_new.shape[0])
        if not deltas:
            continue
        out.append({
            "label": label,
            "delta_v1_mean": round(float(np.mean(deltas)), 5),
            "delta_v1_stdev": round(float(np.std(deltas)) if len(deltas) > 1 else 0.0, 5),
            "delta_v2_mean": round(float(np.mean(v2s)), 5),
            "delta_v2_stdev": round(float(np.std(v2s)) if len(v2s) > 1 else 0.0, 5),
            "n_cc_mean": round(float(np.mean(ccs)), 1),
            "n_total": int(ns[0]),
            "n_runs": len(deltas),
        })
    return {"baseline_composite_v1": round(base_composite, 5),
            "top_hubs": top_hubs,
            "sweeps": out}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--branch", choices=["a", "b", "c", "all"], default="all")
    ap.add_argument("--n-runs", type=int, default=3)
    ap.add_argument("--n-synth", type=int, default=400)
    ap.add_argument("--K", type=int, default=100)
    ap.add_argument("--sigma", type=float, default=1e-3)
    args = ap.parse_args()

    out = {"schema": "nxs_002_cycle11.v1", "ts": int(time.time()), "args": vars(args)}

    const_vals = load_eig_jsonl(DEFAULT_CONST)
    R2_const = paircorr(unfold(const_vals))

    if args.branch in ("a", "all"):
        t0 = time.time()
        out["a_const_match"] = reverse_engineer_const(DEFAULT_CONST, n_synth=args.n_synth,
                                                      K_match=40, n_runs=args.n_runs)
        out["a_const_match"]["elapsed_s"] = round(time.time() - t0, 2)

    if args.branch in ("b", "all"):
        t0 = time.time()
        A_base, n_base = build_csr_from_blowup(DEFAULT_ATLAS)
        atlas_vals = laplacian_eigenvalues(A_base, K=args.K, sigma=args.sigma)
        ext = extended_composite(atlas_vals, const_vals)
        out["b_extended_metric"] = {
            "atlas_baseline": ext,
            "elapsed_s": round(time.time() - t0, 2),
        }

    if args.branch in ("c", "all"):
        t0 = time.time()
        if "A_base" not in dir():
            A_base, n_base = build_csr_from_blowup(DEFAULT_ATLAS)
        out["c_hub_surgery"] = hub_surgery_sweep(A_base, n_base, R2_const, const_vals,
                                                  K=args.K, sigma=args.sigma, n_runs=args.n_runs)
        out["c_hub_surgery"]["elapsed_s"] = round(time.time() - t0, 2)

    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
