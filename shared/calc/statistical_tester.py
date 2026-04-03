#!/usr/bin/env python3
"""
statistical_tester.py -- Unified statistical testing for logout project.

Functions: cohens_d, bonferroni_correct, bootstrap_ci, texas_sharpshooter,
           correlation_test, grade_discovery, multi_dataset_meta
CLI:       --test ttest|mannwhitney|correlation|effect_size|bonferroni
           --data "1,2,3;4,5,6"  --groups "ctrl,exp"
"""
import argparse, sys, math
import numpy as np
from scipy import stats
import tecsrs

# ── Common constants ────────────────────────────────────────────────────
CONSTANTS = {
    "ln2":    math.log(2),
    "ln3":    math.log(3),
    "ln4":    math.log(4),
    "ln4/3":  math.log(4/3),
    "1/e":    1/math.e,
    "1/2":    0.5,
    "1/3":    1/3,
    "1/6":    1/6,
    "5/6":    5/6,
    "pi":     math.pi,
    "sqrt2":  math.sqrt(2),
    "phi":    (1 + math.sqrt(5)) / 2,
    "euler_gamma": 0.5772156649,
}

# ── Significance helpers ────────────────────────────────────────────────
def sig_stars(p):
    if p < 0.001: return "***"
    if p < 0.01:  return "**"
    if p < 0.05:  return "*"
    return "ns"

def effect_label(d):
    d = abs(d)
    if d < 0.2:  return "negligible"
    if d < 0.5:  return "small"
    if d < 0.8:  return "medium"
    return "large"

# ── Core functions ──────────────────────────────────────────────────────
def cohens_d(g1, g2):
    """Cohen's d effect size between two groups."""
    g1, g2 = np.asarray(g1, float), np.asarray(g2, float)
    n1, n2 = len(g1), len(g2)
    pooled = math.sqrt(((n1-1)*g1.var(ddof=1) + (n2-1)*g2.var(ddof=1)) / (n1+n2-2))
    d = (g1.mean() - g2.mean()) / pooled if pooled > 0 else 0.0
    return {"d": d, "label": effect_label(d),
            "mean1": g1.mean(), "mean2": g2.mean(), "pooled_sd": pooled}

def bonferroni_correct(p_values, n_comparisons=None):
    """Bonferroni correction. n_comparisons defaults to len(p_values)."""
    pv = np.asarray(p_values, float)
    n = n_comparisons if n_comparisons else len(pv)
    corrected = np.minimum(pv * n, 1.0)
    return {"original": pv.tolist(), "corrected": corrected.tolist(),
            "n_comparisons": n,
            "significant_005": int((corrected < 0.05).sum()),
            "significant_001": int((corrected < 0.001).sum())}

def bootstrap_ci(data, stat_func=None, n_boot=10000, ci=0.95):
    """Bootstrap confidence interval. Uses Rust tecsrs for mean, Python for custom stat_func."""
    if stat_func is None or stat_func is np.mean:
        return tecsrs.bootstrap_ci(list(np.asarray(data, float)), n_boot=n_boot, ci=ci)
    # Custom stat_func: fall back to Python
    data = np.asarray(data, float)
    rng = np.random.default_rng(42)
    boots = np.array([stat_func(rng.choice(data, len(data), replace=True))
                      for _ in range(n_boot)])
    alpha = 1 - ci
    lo, hi = np.percentile(boots, [100*alpha/2, 100*(1-alpha/2)])
    return {"estimate": float(stat_func(data)), "ci_lo": float(lo),
            "ci_hi": float(hi), "ci_level": ci, "n_boot": n_boot}

def texas_sharpshooter(measured, target, search_space_size, tolerance=0.01):
    """P-value for hitting target within tolerance in a search space."""
    hit_prob = 2 * tolerance / max(search_space_size, 1e-15)
    distance = abs(measured - target)
    hit = distance <= tolerance
    p_single = hit_prob
    p_any = 1 - (1 - p_single) ** max(search_space_size, 1)
    return {"measured": measured, "target": target, "distance": distance,
            "tolerance": tolerance, "hit": hit,
            "p_single": p_single, "p_any": min(p_any, 1.0),
            "sig": sig_stars(p_single),
            "nearest_const": _nearest_constant(measured)}

def _nearest_constant(val):
    best_name, best_dist = None, float("inf")
    for name, c in CONSTANTS.items():
        d = abs(val - c)
        if d < best_dist:
            best_name, best_dist = name, d
    return {"name": best_name, "value": CONSTANTS[best_name], "distance": best_dist}

def correlation_test(x, y, method="pearson"):
    """Correlation with r, p-value, and bootstrap CI."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    if method == "pearson":
        r, p = stats.pearsonr(x, y)
    elif method == "spearman":
        r, p = stats.spearmanr(x, y)
    elif method == "kendall":
        r, p = stats.kendalltau(x, y)
    else:
        raise ValueError(f"Unknown method: {method}")
    # Bootstrap CI on r
    rng = np.random.default_rng(42)
    rs = []
    for _ in range(5000):
        idx = rng.choice(len(x), len(x), replace=True)
        try:
            if method == "pearson":
                ri, _ = stats.pearsonr(x[idx], y[idx])
            elif method == "spearman":
                ri, _ = stats.spearmanr(x[idx], y[idx])
            else:
                ri, _ = stats.kendalltau(x[idx], y[idx])
            if np.isfinite(ri):
                rs.append(ri)
        except Exception:
            pass
    ci_lo, ci_hi = np.percentile(rs, [2.5, 97.5])
    return {"r": float(r), "p": float(p), "sig": sig_stars(p),
            "method": method, "ci_lo": float(ci_lo), "ci_hi": float(ci_hi),
            "n": len(x)}

def grade_discovery(p_value, is_exact=False, has_adhoc=False):
    """Grade a discovery per DFS rules."""
    if is_exact and p_value < 0.05 and not has_adhoc:
        return "\U0001f7e9"   # green
    if not is_exact and p_value < 0.01 and not has_adhoc:
        return "\U0001f7e7\u2605"  # orange + star
    if not is_exact and p_value < 0.05:
        return "\U0001f7e7"   # orange
    if p_value >= 0.05:
        return "\u26aa"       # white
    return "\u2b1b"           # black (fallback)

def multi_dataset_meta(results_dict):
    """Fixed-effects meta-analysis (inverse-variance) + ASCII forest plot.
    results_dict: {name: {"effect": float, "se": float}}
    """
    names, effects, ses = [], [], []
    for name, r in results_dict.items():
        names.append(name)
        effects.append(r["effect"])
        ses.append(r["se"])
    effects, ses = np.array(effects), np.array(ses)
    weights = 1.0 / (ses**2 + 1e-15)
    pooled = np.sum(weights * effects) / np.sum(weights)
    pooled_se = 1.0 / math.sqrt(np.sum(weights))
    z = pooled / pooled_se if pooled_se > 0 else 0
    p = 2 * (1 - stats.norm.cdf(abs(z)))
    # Cochran's Q
    q = np.sum(weights * (effects - pooled)**2)
    q_p = 1 - stats.chi2.cdf(q, len(effects)-1) if len(effects) > 1 else 1.0
    i2 = max(0, (q - (len(effects)-1)) / q) * 100 if q > 0 else 0.0

    forest = _forest_plot(names, effects, ses, pooled, pooled_se)
    return {"pooled_effect": float(pooled), "pooled_se": float(pooled_se),
            "z": float(z), "p": float(p), "sig": sig_stars(p),
            "Q": float(q), "Q_p": float(q_p), "I2": float(i2),
            "forest_plot": forest}

def _forest_plot(names, effects, ses, pooled, pooled_se, width=50):
    """ASCII forest plot."""
    all_lo = [e - 1.96*s for e, s in zip(effects, ses)]
    all_hi = [e + 1.96*s for e, s in zip(effects, ses)]
    lo_pool, hi_pool = pooled - 1.96*pooled_se, pooled + 1.96*pooled_se
    vmin = min(min(all_lo), lo_pool) - 0.1
    vmax = max(max(all_hi), hi_pool) + 0.1
    span = vmax - vmin if vmax > vmin else 1.0
    max_name = max(len(n) for n in names) if names else 8

    def pos(v):
        return int((v - vmin) / span * (width - 1))

    lines = []
    header = " " * (max_name + 2) + f"{vmin:+.3f}" + " " * (width - 12) + f"{vmax:+.3f}"
    lines.append(header)
    for i, name in enumerate(names):
        lo_p, mid_p, hi_p = pos(all_lo[i]), pos(effects[i]), pos(all_hi[i])
        row = [" "] * width
        for j in range(lo_p, min(hi_p+1, width)):
            row[j] = "-"
        if 0 <= mid_p < width:
            row[mid_p] = "O"
        lines.append(f"{name:>{max_name}}  {''.join(row)}")
    # Pooled
    lo_p, mid_p, hi_p = pos(lo_pool), pos(pooled), pos(hi_pool)
    row = [" "] * width
    for j in range(lo_p, min(hi_p+1, width)):
        row[j] = "="
    if 0 <= mid_p < width:
        row[mid_p] = "<>"[0]
    lines.append("-" * (max_name + 2 + width))
    lines.append(f"{'Pooled':>{max_name}}  {''.join(row)}")
    # Zero line
    z_pos = pos(0)
    if 0 <= z_pos < width:
        ruler = [" "] * width
        ruler[z_pos] = "|"
        lines.append(f"{'':>{max_name}}  {''.join(ruler)}  (0)")
    return "\n".join(lines)

# ── CLI ─────────────────────────────────────────────────────────────────
def parse_data(s):
    """Parse "1,2,3;4,5,6" into list of arrays."""
    groups = s.split(";")
    return [np.array([float(x) for x in g.split(",")]) for g in groups]

def main():
    ap = argparse.ArgumentParser(description="Statistical tester for logout project")
    ap.add_argument("--test", choices=["ttest","mannwhitney","correlation",
                     "effect_size","bonferroni","bootstrap","texas","grade","meta"],
                    required=True)
    ap.add_argument("--data", type=str, help="Values: 'a,b,c;d,e,f' (semicolon separates groups)")
    ap.add_argument("--groups", type=str, default="group1,group2", help="Group labels")
    ap.add_argument("--method", type=str, default="pearson", help="Correlation method")
    ap.add_argument("--measured", type=float, help="Texas: measured value")
    ap.add_argument("--target", type=float, help="Texas: target value")
    ap.add_argument("--search-space", type=float, default=100, help="Texas: search space size")
    ap.add_argument("--tolerance", type=float, default=0.01, help="Texas: tolerance")
    ap.add_argument("--exact", action="store_true", help="Grade: is exact identity")
    ap.add_argument("--adhoc", action="store_true", help="Grade: has +1/-1 adjustment")
    ap.add_argument("--p-value", type=float, help="Grade: p-value to grade")
    args = ap.parse_args()

    labels = args.groups.split(",") if args.groups else ["group1","group2"]

    if args.test == "ttest":
        gs = parse_data(args.data)
        t, p = stats.ttest_ind(gs[0], gs[1])
        d = cohens_d(gs[0], gs[1])
        print(f"  t-test: t={t:.4f}, p={p:.6f} {sig_stars(p)}")
        print(f"  Cohen's d={d['d']:.4f} ({d['label']})")
        print(f"  {labels[0]}: mean={d['mean1']:.4f}  {labels[1]}: mean={d['mean2']:.4f}")

    elif args.test == "mannwhitney":
        gs = parse_data(args.data)
        u, p = stats.mannwhitneyu(gs[0], gs[1], alternative="two-sided")
        d = cohens_d(gs[0], gs[1])
        print(f"  Mann-Whitney U={u:.1f}, p={p:.6f} {sig_stars(p)}")
        print(f"  Cohen's d={d['d']:.4f} ({d['label']})")

    elif args.test == "correlation":
        gs = parse_data(args.data)
        res = correlation_test(gs[0], gs[1], method=args.method)
        print(f"  {res['method']} r={res['r']:.4f}, p={res['p']:.6f} {res['sig']}")
        print(f"  95% CI: [{res['ci_lo']:.4f}, {res['ci_hi']:.4f}]  n={res['n']}")

    elif args.test == "effect_size":
        gs = parse_data(args.data)
        d = cohens_d(gs[0], gs[1])
        print(f"  Cohen's d = {d['d']:.4f} ({d['label']})")
        print(f"  {labels[0]}: mean={d['mean1']:.4f}  {labels[1]}: mean={d['mean2']:.4f}")
        print(f"  Pooled SD = {d['pooled_sd']:.4f}")

    elif args.test == "bonferroni":
        pvals = [float(x) for x in args.data.split(",")]
        res = bonferroni_correct(pvals)
        print(f"  Bonferroni correction (n={res['n_comparisons']}):")
        for i, (o, c) in enumerate(zip(res["original"], res["corrected"])):
            print(f"    [{i}] {o:.6f} -> {c:.6f} {sig_stars(c)}")
        print(f"  Significant at 0.05: {res['significant_005']}/{len(pvals)}")
        print(f"  Significant at 0.001: {res['significant_001']}/{len(pvals)}")

    elif args.test == "bootstrap":
        gs = parse_data(args.data)
        res = bootstrap_ci(gs[0])
        print(f"  Bootstrap CI ({res['ci_level']*100:.0f}%, n_boot={res['n_boot']}):")
        print(f"  Estimate = {res['estimate']:.4f}")
        print(f"  CI: [{res['ci_lo']:.4f}, {res['ci_hi']:.4f}]")

    elif args.test == "texas":
        res = texas_sharpshooter(args.measured, args.target,
                                 args.search_space, args.tolerance)
        print(f"  Texas Sharpshooter Test:")
        print(f"  Measured={res['measured']:.6f}  Target={res['target']:.6f}")
        print(f"  Distance={res['distance']:.6f}  Tolerance={res['tolerance']:.4f}")
        print(f"  Hit: {'YES' if res['hit'] else 'NO'}")
        print(f"  p(single)={res['p_single']:.6f} {res['sig']}")
        print(f"  p(any in space)={res['p_any']:.6f}")
        nc = res["nearest_const"]
        print(f"  Nearest constant: {nc['name']}={nc['value']:.6f} (dist={nc['distance']:.6f})")

    elif args.test == "grade":
        p = args.p_value if args.p_value is not None else 1.0
        g = grade_discovery(p, is_exact=args.exact, has_adhoc=args.adhoc)
        print(f"  Grade: {g}  (p={p:.6f}, exact={args.exact}, adhoc={args.adhoc})")

    elif args.test == "meta":
        # Example: --data "0.5,0.1;0.3,0.05;0.6,0.2" (effect,se pairs)
        gs = parse_data(args.data)
        rd = {}
        for i, g in enumerate(gs):
            name = labels[i] if i < len(labels) else f"study{i+1}"
            rd[name] = {"effect": g[0], "se": g[1]}
        res = multi_dataset_meta(rd)
        print(f"  Meta-analysis (fixed effects):")
        print(f"  Pooled effect = {res['pooled_effect']:.4f} +/- {res['pooled_se']:.4f}")
        print(f"  z={res['z']:.4f}, p={res['p']:.6f} {res['sig']}")
        print(f"  Heterogeneity: Q={res['Q']:.2f} (p={res['Q_p']:.4f}), I2={res['I2']:.1f}%")
        print()
        print(res["forest_plot"])

if __name__ == "__main__":
    main()
