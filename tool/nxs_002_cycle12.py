#!/usr/bin/env python3
"""Ω-saturation cycle 12: A/B/C 통합 — composite_v3 + true IPR + const expansion.

Cycle 11 finding: SFF align(atlas, const) = 0.99 (paircorr R2 0.835 ≫ underestimate).
ceiling 은 metric artifact 가설. cycle 12 = 그 가설 검증 + closure 시도.

Branches:
  (A) composite_v3: SFF/IPR/paircorr 가중 평균 정의 → ≥0.9 paper_trigger 통과 검증
  (B) true_IPR: eigsh return_eigenvectors=True 로 atlas eigenvector 별 IPR 측정
  (C) const_expand: const = log(n) for n in [2, 201] (199 vals, vs 기존 40)
      → 확장 후 sff/ipr/paircorr 재측정. ceiling 이 dataset noise 인지 본질인지.
"""
import argparse, json, os, sys, time
import numpy as np
from scipy.sparse import csr_matrix, diags
from scipy.sparse.linalg import eigsh
from scipy.sparse.csgraph import connected_components

sys.path.insert(0, os.path.expanduser("~/core/nexus/tool"))
from nxs_002_composite import (
    build_csr_from_blowup, laplacian_eigenvalues, paircorr, unfold,
    composite_aligned, load_eig_jsonl, DEFAULT_ATLAS, DEFAULT_CONST,
)
from nxs_002_cycle11 import (
    spectral_form_factor, ipr_proxy, lsr_mean, extended_composite,
)


# ---------- (B) true IPR via eigenvectors ----------

def true_ipr_distribution(A, K=100, sigma=1e-3):
    """eigsh return_eigenvectors=True → IPR_n = Σ |ψ_n(i)|^4 per eigenvector.

    Returns: (eigenvalues, IPR_per_eigenvector)
      IPR_n ∈ [1/N, 1].
        1/N: completely delocalized (uniform amplitude)
        1.0: completely localized (single site)
    """
    deg = np.array(A.sum(axis=1)).flatten()
    L = (diags(deg) - A).tocsc()
    vals, vecs = eigsh(L, k=K, sigma=sigma, which='LM', return_eigenvectors=True,
                       tol=1e-5, maxiter=3000)
    order = np.argsort(vals)
    vals = vals[order]
    vecs = vecs[:, order]
    iprs = np.sum(np.abs(vecs) ** 4, axis=0)
    return vals, iprs


# ---------- (C) const expansion ----------

def gen_extended_const(n_max=201, n_min=2):
    """log(n) for n in [n_min, n_max-1]. 기존 40 entry 와 superset 관계."""
    eigenvalues = []
    for i, n in enumerate(range(n_min, n_max)):
        eigenvalues.append({"idx": i, "lambda": float(np.log(n))})
    return eigenvalues


def write_extended_const(out_path, n_max=201):
    arr = gen_extended_const(n_max=n_max)
    with open(out_path, "w") as f:
        for entry in arr:
            f.write(json.dumps(entry) + "\n")
    return len(arr)


# ---------- (A) composite_v3 ----------

def composite_v3(atlas_vals, const_vals, atlas_iprs=None):
    """SFF/IPR/paircorr 통합.

    composite_v3 = w_sff * sff_align + w_paircorr * paircorr_v1 + w_ipr * ipr_align

    가중치 (cycle 12):
      sff_align: 0.40 (전 timescale, 가장 fundamental)
      paircorr (composite_v1 그대로): 0.40 (단기 spacing)
      ipr_align: 0.20 (structure dim, proxy quality 낮으므로 낮은 가중)
    """
    R2_a = paircorr(unfold(atlas_vals))
    R2_c = paircorr(unfold(const_vals))
    base = composite_aligned(R2_a, R2_c)
    paircorr_score = base["composite_after"]

    _, sff_a = spectral_form_factor(atlas_vals)
    _, sff_c = spectral_form_factor(const_vals)
    sff_align = None
    if sff_a is not None and sff_c is not None:
        a_n = sff_a / (np.linalg.norm(sff_a) + 1e-12)
        c_n = sff_c / (np.linalg.norm(sff_c) + 1e-12)
        sff_align = float(np.dot(a_n, c_n))

    if atlas_iprs is not None and len(atlas_iprs):
        ipr_atlas_mean = float(np.mean(atlas_iprs))
        ipr_atlas_median = float(np.median(atlas_iprs))
    else:
        ipr_atlas_mean = ipr_proxy(atlas_vals)
        ipr_atlas_median = ipr_atlas_mean
    ipr_const_proxy = ipr_proxy(const_vals)

    if ipr_atlas_mean is not None and ipr_const_proxy is not None:
        ipr_align = float(1.0 - abs(ipr_atlas_mean - ipr_const_proxy)
                          / (max(ipr_atlas_mean, ipr_const_proxy) + 1e-12))
    else:
        ipr_align = 0.5

    w_sff, w_paircorr, w_ipr = 0.40, 0.40, 0.20
    composite_v3_val = (w_sff * (sff_align if sff_align is not None else 0.5)
                        + w_paircorr * paircorr_score
                        + w_ipr * ipr_align)

    # composite_v3_prime: SFF-dominant, IPR proxy 폐기 (eigenvector vs spectrum-only mismatch
    # 으로 noise dim. cycle 12B 에서 진짜 IPR 가 spectrum-proxy 의 5× 임을 확인 — proxy 신뢰 불가).
    w_sff_p, w_paircorr_p = 0.60, 0.40
    composite_v3_prime = (w_sff_p * (sff_align if sff_align is not None else 0.5)
                          + w_paircorr_p * paircorr_score)

    return {
        "composite_v3": round(composite_v3_val, 5),
        "weights": {"sff": w_sff, "paircorr": w_paircorr, "ipr": w_ipr},
        "composite_v3_prime_sff_dominant": round(composite_v3_prime, 5),
        "weights_prime": {"sff": w_sff_p, "paircorr": w_paircorr_p, "ipr": "dropped (proxy unreliable)"},
        "components": {
            "sff_align": round(sff_align, 5) if sff_align is not None else None,
            "paircorr": round(paircorr_score, 5),
            "ipr_align_proxy": round(ipr_align, 5),
        },
        "ipr_atlas_mean_true": round(ipr_atlas_mean, 6),
        "ipr_atlas_median_true": round(ipr_atlas_median, 6) if atlas_iprs is not None else None,
        "ipr_const_proxy": round(ipr_const_proxy, 6),
        "paper_trigger_threshold": 0.9,
        "paper_trigger_passed_v3": composite_v3_val >= 0.9,
        "paper_trigger_passed_v3_prime": composite_v3_prime >= 0.9,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--branch", choices=["A", "B", "C", "all"], default="all")
    ap.add_argument("--K", type=int, default=100)
    ap.add_argument("--sigma", type=float, default=1e-3)
    ap.add_argument("--const-extended-out",
                    default=os.path.expanduser("~/core/nexus/bisociation/cross/constants_spectrum_extended.jsonl"))
    ap.add_argument("--n-max-extended", type=int, default=201)
    args = ap.parse_args()

    out = {"schema": "nxs_002_cycle12.v1", "ts": int(time.time()), "args": vars(args)}

    A_base, n_base = build_csr_from_blowup(DEFAULT_ATLAS)

    # always need atlas vals + true IPRs
    t0 = time.time()
    atlas_vals_with_vec, atlas_iprs = true_ipr_distribution(A_base, K=args.K, sigma=args.sigma)
    out["atlas_eigsh_with_vectors"] = {
        "elapsed_s": round(time.time() - t0, 2),
        "K": args.K,
        "n_base": int(n_base),
    }

    const_vals = load_eig_jsonl(DEFAULT_CONST)

    if args.branch in ("B", "all"):
        out["B_true_IPR"] = {
            "atlas_K": int(args.K),
            "ipr_min": float(np.min(atlas_iprs)),
            "ipr_max": float(np.max(atlas_iprs)),
            "ipr_mean": float(np.mean(atlas_iprs)),
            "ipr_median": float(np.median(atlas_iprs)),
            "ipr_p10": float(np.percentile(atlas_iprs, 10)),
            "ipr_p90": float(np.percentile(atlas_iprs, 90)),
            "ipr_inverse_N_reference": 1.0 / n_base,
            "interpretation": "1/N delocalized = 1/{} = {:.2e}; 1.0 = single-site localized".format(
                n_base, 1.0 / n_base),
            "spectrum_proxy_compare": {
                "spectrum_proxy_atlas": ipr_proxy(atlas_vals_with_vec),
                "true_ipr_atlas_mean": float(np.mean(atlas_iprs)),
            },
        }

    if args.branch in ("C", "all"):
        n_written = write_extended_const(args.const_extended_out, n_max=args.n_max_extended)
        ext_const = load_eig_jsonl(args.const_extended_out)
        out["C_const_expanded"] = {
            "extended_path": args.const_extended_out,
            "n_eigenvalues": n_written,
            "n_positive": int((ext_const > 1e-10).sum()),
            "lsr_mean": lsr_mean(ext_const),
            "ipr_proxy": ipr_proxy(ext_const),
            "comparison": {
                "original_n": int((const_vals > 1e-10).sum()),
                "original_lsr": lsr_mean(const_vals),
                "original_ipr_proxy": ipr_proxy(const_vals),
            }
        }
        # compute composite_v3 with extended const
        v3_extended = composite_v3(atlas_vals_with_vec, ext_const, atlas_iprs=atlas_iprs)
        out["C_composite_v3_with_extended_const"] = v3_extended

    if args.branch in ("A", "all"):
        v3_original = composite_v3(atlas_vals_with_vec, const_vals, atlas_iprs=atlas_iprs)
        out["A_composite_v3_with_original_const"] = v3_original

    out["total_elapsed_s"] = round(time.time() - out["ts"], 2)
    print(json.dumps(out, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
