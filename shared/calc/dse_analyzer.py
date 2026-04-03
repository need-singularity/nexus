#!/usr/bin/env python3
"""
DSE Analyzer — Universal DSE 결과 분석 계산기
- 전체 도메인 통계
- 시너지 히트맵 (Cross-DSE)
- Texas Sharpshooter 검정 (n6 정합 vs 무작위)
- 도메인 간 상관분석

Usage:
  python3 calc/dse_analyzer.py                    # 전체 분석
  python3 calc/dse_analyzer.py --heatmap          # 시너지 히트맵만
  python3 calc/dse_analyzer.py --texas N           # Texas Sharpshooter (N=trials)
  python3 calc/dse_analyzer.py --correlate         # 상관분석
"""

import subprocess
import sys
import os
import re
import random
import math
from pathlib import Path
from collections import defaultdict

DSE_DIR = Path(__file__).parent.parent / ".shared" / "dse"
DSE_BIN = DSE_DIR / "universal-dse"
DOMAINS_DIR = DSE_DIR / "domains"


def run_dse(args: list[str]) -> str:
    """Run universal-dse binary and return stdout."""
    cmd = [str(DSE_BIN)] + args
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(DSE_DIR))
    return result.stdout


def parse_batch_all() -> list[dict]:
    """Run --all and parse results."""
    output = run_dse(["--all", str(DOMAINS_DIR)])
    domains = []
    for line in output.split("\n"):
        line = line.strip()
        if not line or line.startswith("=") or line.startswith("-") or line.startswith("Domain") or "TOTAL" in line:
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 8:
            try:
                domains.append({
                    "name": parts[0],
                    "combos": int(parts[1]),
                    "compat": int(parts[2]),
                    "n6": float(parts[3]),
                    "perf": float(parts[4]),
                    "power": float(parts[5]),
                    "cost": float(parts[6]),
                    "pareto": float(parts[7]),
                })
            except (ValueError, IndexError):
                continue
    return domains


def parse_cross_all(top_n: int = 50) -> list[dict]:
    """Run --cross-all and parse results."""
    output = run_dse(["--cross-all", str(DOMAINS_DIR), "--top", str(top_n)])
    results = []
    for line in output.split("\n"):
        line = line.strip()
        if not line or line.startswith("=") or line.startswith("-") or line.startswith("Rank") or "Domain" in line:
            continue
        if line.startswith("Total") or line.startswith("Avg") or "Frequency" in line:
            break
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 8:
            try:
                results.append({
                    "rank": int(parts[0]),
                    "a": parts[1],
                    "b": parts[2],
                    "n6": float(parts[3]),
                    "perf": float(parts[4]),
                    "power": float(parts[5]),
                    "cost": float(parts[6]),
                    "score": float(parts[7]),
                })
            except (ValueError, IndexError):
                continue
    return results


def print_header(title: str):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


# ──────────────────────────────────────────────
# 1. 전체 통계
# ──────────────────────────────────────────────

def run_stats():
    """전체 도메인 통계 요약."""
    print_header("DSE 전체 도메인 통계")
    domains = parse_batch_all()
    if not domains:
        print("  No domains found!")
        return

    n = len(domains)
    total_combos = sum(d["combos"] for d in domains)
    total_compat = sum(d["compat"] for d in domains)

    n6_values = [d["n6"] for d in domains]
    pareto_values = [d["pareto"] for d in domains]

    n6_100 = sum(1 for v in n6_values if v >= 100.0)
    n6_90 = sum(1 for v in n6_values if v >= 90.0)

    print(f"  도메인 수:       {n}")
    print(f"  총 조합:         {total_combos:,} (호환: {total_compat:,})")
    print(f"  Top-1 n6 평균:   {sum(n6_values)/n:.1f}%")
    print(f"  Top-1 n6=100%:   {n6_100}/{n} ({n6_100/n*100:.0f}%)")
    print(f"  Top-1 n6>=90%:   {n6_90}/{n} ({n6_90/n*100:.0f}%)")
    print(f"  Pareto 평균:     {sum(pareto_values)/n:.4f}")
    print(f"  Pareto 최고:     {max(pareto_values):.4f} ({max(domains, key=lambda d:d['pareto'])['name']})")
    print(f"  Pareto 최저:     {min(pareto_values):.4f} ({min(domains, key=lambda d:d['pareto'])['name']})")
    print()

    # Bar chart
    sorted_d = sorted(domains, key=lambda d: d["pareto"], reverse=True)
    print("  Pareto Score 분포:")
    print()
    for d in sorted_d:
        bar_len = int(d["pareto"] * 50)
        bar = "█" * bar_len
        n6_mark = "●" if d["n6"] >= 100 else "○" if d["n6"] >= 95 else "·"
        print(f"  {d['name']:>20} {d['pareto']:.3f} {bar} {n6_mark}")
    print()
    print("  ● n6=100%  ○ n6≥95%  · n6<95%")

    return domains


# ──────────────────────────────────────────────
# 2. 시너지 히트맵
# ──────────────────────────────────────────────

def run_heatmap():
    """Cross-DSE 시너지 히트맵 생성."""
    print_header("Cross-DSE 시너지 히트맵")

    # Get all domain names
    domains = parse_batch_all()
    if not domains:
        return

    # Run cross-all with high top-N to get all pairs
    output = run_dse(["--cross-all", str(DOMAINS_DIR), "--top", "435"])

    # Parse all results into matrix
    names = [d["name"] for d in domains]
    name_idx = {n: i for i, n in enumerate(names)}
    n = len(names)
    matrix = [[0.0] * n for _ in range(n)]

    for line in output.split("\n"):
        line = line.strip()
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 8:
            try:
                a, b = parts[1], parts[2]
                score = float(parts[7])
                if a in name_idx and b in name_idx:
                    i, j = name_idx[a], name_idx[b]
                    matrix[i][j] = score
                    matrix[j][i] = score
            except (ValueError, IndexError):
                continue

    # Fill diagonal with single-domain Pareto
    for d in domains:
        if d["name"] in name_idx:
            i = name_idx[d["name"]]
            matrix[i][i] = d["pareto"]

    # Print top synergies
    pairs = []
    for i in range(n):
        for j in range(i+1, n):
            if matrix[i][j] > 0:
                synergy = matrix[i][j] - (matrix[i][i] + matrix[j][j]) / 2
                pairs.append((names[i], names[j], matrix[i][j], synergy))

    pairs.sort(key=lambda p: p[2], reverse=True)

    print("  Top-20 시너지 쌍 (Score | Synergy vs avg single):")
    print()
    print(f"  {'Rank':>4} | {'Domain A':>18} | {'Domain B':>18} | {'Score':>6} | {'Synergy':>8}")
    print(f"  {'-'*65}")
    for i, (a, b, sc, syn) in enumerate(pairs[:20]):
        sign = "+" if syn >= 0 else ""
        print(f"  {i+1:>4} | {a:>18} | {b:>18} | {sc:.4f} | {sign}{syn:.4f}")

    # Compact heatmap (top 10 domains only)
    top10_names = [d["name"] for d in sorted(domains, key=lambda d: d["pareto"], reverse=True)[:10]]
    print()
    print("  히트맵 (Top-10 도메인, 10=0.90+):")
    print()

    # Header
    short_names = [n[:6] for n in top10_names]
    print(f"  {'':>12}", end="")
    for sn in short_names:
        print(f" {sn:>6}", end="")
    print()

    for i, name_a in enumerate(top10_names):
        ia = name_idx[name_a]
        print(f"  {name_a[:12]:>12}", end="")
        for name_b in top10_names:
            ib = name_idx[name_b]
            val = matrix[ia][ib]
            if val >= 0.90:
                sym = "██"
            elif val >= 0.85:
                sym = "▓▓"
            elif val >= 0.80:
                sym = "▒▒"
            elif val >= 0.75:
                sym = "░░"
            elif val > 0:
                sym = "··"
            else:
                sym = "  "
            score_int = int(val * 10) if val > 0 else 0
            print(f"  {sym}{score_int:>2}", end="")
        print()

    print()
    print("  ██ ≥0.90  ▓▓ ≥0.85  ▒▒ ≥0.80  ░░ ≥0.75  ·· <0.75")


# ──────────────────────────────────────────────
# 3. Texas Sharpshooter (도메인 간 교차 검정)
# ──────────────────────────────────────────────

def run_texas(n_trials: int = 10000):
    """Texas Sharpshooter: n6 정합이 우연인지 검정.

    방법: 30개 도메인의 Top-1 n6% 값을 수집하고,
    무작위로 [0,1] 범위의 n6 점수를 할당했을 때
    관측된 평균 n6%를 이길 확률을 계산.
    """
    print_header(f"Texas Sharpshooter 검정 (N={n_trials:,})")

    domains = parse_batch_all()
    if not domains:
        return

    actual_n6_values = [d["n6"] / 100.0 for d in domains]
    actual_mean = sum(actual_n6_values) / len(actual_n6_values)
    actual_n6_100 = sum(1 for v in actual_n6_values if v >= 1.0)

    print(f"  관측값:")
    print(f"    도메인 수:     {len(domains)}")
    print(f"    평균 Top-1 n6: {actual_mean*100:.1f}%")
    print(f"    n6=100% 수:    {actual_n6_100}/{len(domains)}")
    print()

    # Monte Carlo: 각 도메인에 대해 랜덤 n6 값 할당
    # 각 도메인의 후보 수를 유지하면서 n6를 [0,1] uniform으로 교체
    random.seed(42)
    n = len(domains)

    beat_mean = 0
    beat_count_100 = 0
    random_means = []

    for _ in range(n_trials):
        # 각 도메인에 대해 랜덤 n6 값 (5-level 평균)
        trial_n6 = []
        for _ in range(n):
            # 5개 레벨 각각에서 후보 5-10개 중 max를 뽑는 시뮬레이션
            level_maxes = []
            for _ in range(5):  # 5 levels
                n_cands = random.randint(4, 10)
                level_max = max(random.random() for _ in range(n_cands))
                level_maxes.append(level_max)
            trial_n6.append(sum(level_maxes) / 5)

        trial_mean = sum(trial_n6) / n
        trial_100 = sum(1 for v in trial_n6 if v >= 1.0)
        random_means.append(trial_mean)

        if trial_mean >= actual_mean:
            beat_mean += 1
        if trial_100 >= actual_n6_100:
            beat_count_100 += 1

    p_mean = beat_mean / n_trials
    p_100 = beat_count_100 / n_trials
    random_avg = sum(random_means) / len(random_means)
    random_std = (sum((x - random_avg)**2 for x in random_means) / len(random_means)) ** 0.5
    z_score = (actual_mean - random_avg) / random_std if random_std > 0 else 0

    print(f"  Monte Carlo 결과 ({n_trials:,} trials):")
    print(f"    랜덤 평균 n6:  {random_avg*100:.1f}% ± {random_std*100:.1f}%")
    print(f"    관측 평균 n6:  {actual_mean*100:.1f}%")
    print(f"    Z-score:       {z_score:.1f}σ")
    print(f"    p-value (평균): {p_mean:.6f} ({beat_mean}/{n_trials})")
    print(f"    p-value (100%): {p_100:.6f} ({beat_count_100}/{n_trials})")
    print()

    # Histogram
    print("  랜덤 n6 평균 분포:")
    bins = defaultdict(int)
    for v in random_means:
        b = round(v * 100, 0)
        bins[int(b // 2) * 2] += 1  # 2% bins

    max_count = max(bins.values()) if bins else 1
    for b in sorted(bins.keys()):
        bar = "█" * (bins[b] * 40 // max_count)
        marker = " ◄ ACTUAL" if abs(b - actual_mean * 100) < 2 else ""
        print(f"    {b:>3}% |{bar}{marker}")

    print()
    if z_score > 5:
        print(f"  판정: Z={z_score:.1f}σ — n6 정합은 우연이 아님 (p < 0.001)")
        print(f"  강도: 🔴 극도로 유의 (Z>5σ)")
    elif z_score > 3:
        print(f"  판정: Z={z_score:.1f}σ — 유의미한 n6 정합 (p < 0.01)")
        print(f"  강도: 🟠 매우 유의 (Z>3σ)")
    elif z_score > 2:
        print(f"  판정: Z={z_score:.1f}σ — 약한 유의성 (p < 0.05)")
        print(f"  강도: 🟡 유의 (Z>2σ)")
    else:
        print(f"  판정: Z={z_score:.1f}σ — 유의하지 않음")


# ──────────────────────────────────────────────
# 4. 상관분석
# ──────────────────────────────────────────────

def run_correlate():
    """도메인 속성 간 상관분석."""
    print_header("DSE 도메인 상관분석")

    domains = parse_batch_all()
    if not domains:
        return

    # Extract columns
    cols = {
        "n6": [d["n6"] for d in domains],
        "perf": [d["perf"] for d in domains],
        "power": [d["power"] for d in domains],
        "cost": [d["cost"] for d in domains],
        "pareto": [d["pareto"] for d in domains],
        "combos": [d["combos"] for d in domains],
        "compat": [d["compat"] for d in domains],
        "filter%": [(d["combos"] - d["compat"]) / d["combos"] * 100 if d["combos"] > 0 else 0
                    for d in domains],
    }

    def pearson(x, y):
        n = len(x)
        mx, my = sum(x)/n, sum(y)/n
        num = sum((xi-mx)*(yi-my) for xi,yi in zip(x,y))
        dx = sum((xi-mx)**2 for xi in x) ** 0.5
        dy = sum((yi-my)**2 for yi in y) ** 0.5
        return num / (dx * dy) if dx > 0 and dy > 0 else 0

    keys = ["n6", "perf", "power", "cost", "pareto", "combos", "filter%"]

    # Correlation matrix
    print(f"  {'':>8}", end="")
    for k in keys:
        print(f" {k:>8}", end="")
    print()

    for ki in keys:
        print(f"  {ki:>8}", end="")
        for kj in keys:
            r = pearson(cols[ki], cols[kj])
            if abs(r) >= 0.5:
                print(f" {r:>7.2f}*", end="")
            else:
                print(f" {r:>8.2f}", end="")
        print()

    print()
    print("  * |r| >= 0.5 (강한 상관)")
    print()

    # Key findings
    r_n6_pareto = pearson(cols["n6"], cols["pareto"])
    r_perf_pareto = pearson(cols["perf"], cols["pareto"])
    r_n6_cost = pearson(cols["n6"], cols["cost"])

    print("  핵심 상관관계:")
    print(f"    n6 vs Pareto:  r={r_n6_pareto:.3f}  {'(양의 상관)' if r_n6_pareto > 0.3 else '(약한 상관)'}")
    print(f"    perf vs Pareto: r={r_perf_pareto:.3f}  {'(양의 상관)' if r_perf_pareto > 0.3 else '(약한 상관)'}")
    print(f"    n6 vs cost:    r={r_n6_cost:.3f}  {'(trade-off)' if r_n6_cost < -0.3 else ''}")


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────

def main():
    args = sys.argv[1:]

    if "--heatmap" in args:
        run_heatmap()
    elif "--texas" in args:
        idx = args.index("--texas")
        n = int(args[idx + 1]) if idx + 1 < len(args) else 10000
        run_texas(n)
    elif "--correlate" in args:
        run_correlate()
    else:
        # Full analysis
        run_stats()
        run_texas(10000)
        run_correlate()


if __name__ == "__main__":
    main()
