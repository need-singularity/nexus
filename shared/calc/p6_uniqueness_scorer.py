#!/usr/bin/env python3
"""P6 Uniqueness Scorer — Why Perfect Number 6 is mathematically special.

Combines multiple uniqueness dimensions into a single score using tecsrs
Rust acceleration for exhaustive search.

Dimensions:
  1. R-spectrum: R(n)=1 uniqueness among all n
  2. Identity count: how many arithmetic identities hold only at n
  3. Factorial capacity: n! expressibility from divisor functions
  4. Gap ratio: distance to next perfect number
  5. Completeness: 1/d₁+1/d₂+...=1 for proper divisors

Usage:
  python3 calc/p6_uniqueness_scorer.py                   # full score
  python3 calc/p6_uniqueness_scorer.py --compare 28      # compare with P₂
  python3 calc/p6_uniqueness_scorer.py --identities      # list all unique identities
  python3 calc/p6_uniqueness_scorer.py --limit 10000     # extend search range
"""

import argparse
import math
import sys

try:
    import tecsrs
except ImportError:
    print("ERROR: tecsrs not installed. Run: cd tecsrs && maturin develop --release")
    sys.exit(1)


# ═══════════════════════════════════════════════════════════════
# Identity library — all known n=6 unique identities
# ═══════════════════════════════════════════════════════════════

IDENTITIES = [
    ("φ·σ = n·τ",            lambda n, st: st.phi(n) * st.sigma(n) == n * st.tau(n)),
    ("3n-6 = σ",             lambda n, st: 3*n - 6 == st.sigma(n)),
    ("n-2 = τ",              lambda n, st: n - 2 == st.tau(n)),
    ("(n-3)! = n",           lambda n, st: n >= 4 and math.factorial(n-3) == n),
    ("sopfr·φ = n+τ",        lambda n, st: st.sopfr(n) * st.phi(n) == n + st.tau(n)),
    ("τ·sopfr = 20",         lambda n, st: st.tau(n) * st.sopfr(n) == 20),
    ("τ(τ-1) = σ",           lambda n, st: st.tau(n) * (st.tau(n)-1) == st.sigma(n)),
    ("(n-1)!/2 = sopfr·σ",   lambda n, st: n > 1 and math.factorial(n-1)//2 == st.sopfr(n)*st.sigma(n)),
    ("lcm(1..n) = sopfr·σ",  lambda n, st: _lcm(n) == st.sopfr(n)*st.sigma(n)),
    ("n·σ·sopfr·φ = n!",     lambda n, st: n*st.sigma(n)*st.sopfr(n)*st.phi(n) == math.factorial(n)),
    ("σ/φ = n",              lambda n, st: st.phi(n) != 0 and st.sigma(n) == n * st.phi(n)),
    ("φ² = τ",               lambda n, st: st.phi(n)**2 == st.tau(n)),
]


def _lcm(n):
    result = 1
    for i in range(2, n + 1):
        result = result * i // math.gcd(result, i)
    return result


# ═══════════════════════════════════════════════════════════════
# Scoring dimensions
# ═══════════════════════════════════════════════════════════════

def score_r_spectrum(n, st):
    """Dimension 1: R(n) = σφ/(nτ). Score = 1 if R=1, else 0."""
    sigma = st.sigma(n)
    tau = st.tau(n)
    phi = st.phi(n)
    if n * tau == 0:
        return 0.0, "undefined"
    R = (sigma * phi) / (n * tau)
    return (1.0 if abs(R - 1.0) < 1e-12 else 0.0), f"R({n}) = {R:.6f}"


def score_identities(n, st, limit):
    """Dimension 2: Count identities unique to n in [2, limit]."""
    unique_count = 0
    total = len(IDENTITIES)
    details = []
    for name, fn in IDENTITIES:
        try:
            if not fn(n, st):
                details.append(f"  ✗ {name} (not satisfied at n={n})")
                continue
        except (ValueError, OverflowError):
            continue

        # Check uniqueness
        hits = []
        for i in range(2, min(limit + 1, st.limit() + 1)):
            try:
                if fn(i, st):
                    hits.append(i)
            except (ValueError, OverflowError):
                continue
        if hits == [n]:
            unique_count += 1
            details.append(f"  ✓ {name} — UNIQUE to n={n}")
        elif n in hits:
            details.append(f"  ~ {name} — shared ({len(hits)} hits)")
        else:
            details.append(f"  ✗ {name} — n={n} not a solution")
    score = unique_count / total if total > 0 else 0
    return score, unique_count, total, details


def score_factorial_capacity(n, st):
    """Dimension 3: Can n! be expressed from divisor functions?"""
    sigma = st.sigma(n)
    tau = st.tau(n)
    phi = st.phi(n)
    sopfr = st.sopfr(n)
    nfact = math.factorial(n)

    expressions = [
        ("n·σ·sopfr·φ", n * sigma * sopfr * phi),
        ("σ·(n-1)!/2·2/sopfr", sigma * math.factorial(n-1) if n > 1 else 0),
    ]
    matched = sum(1 for _, val in expressions if val == nfact)
    return matched / len(expressions), f"{matched}/{len(expressions)} factorial expressions match n!={nfact}"


def score_gap_ratio(n):
    """Dimension 4: Gap to next perfect number (larger gap = more isolated)."""
    perfects = [6, 28, 496, 8128, 33550336]
    idx = perfects.index(n) if n in perfects else -1
    if idx < 0 or idx >= len(perfects) - 1:
        return 0.0, "not a known perfect number"
    gap = perfects[idx + 1] - perfects[idx]
    ratio = gap / n
    # Score: higher ratio = more isolated. P₁ has ratio 22/6 ≈ 3.67
    # Normalize: any ratio > 1 gets partial credit, >3 gets full
    score = min(ratio / 3.0, 1.0)
    return score, f"gap={gap}, ratio={ratio:.2f}"


def score_completeness(n, st):
    """Dimension 5: Sum of proper divisor reciprocals = 1."""
    sigma = st.sigma(n)
    # σ₋₁(n) = σ(n)/n. For perfect: σ₋₁ = 2, so reciprocal sum of proper divisors = 1
    sigma_neg1 = sigma / n
    # Proper divisor reciprocal sum = σ₋₁ - 1
    proper_sum = sigma_neg1 - 1.0
    score = 1.0 if abs(proper_sum - 1.0) < 1e-12 else 0.0
    return score, f"Σ(1/d) = {proper_sum:.6f}"


# ═══════════════════════════════════════════════════════════════
# Combined scorer
# ═══════════════════════════════════════════════════════════════

def compute_full_score(n, st, limit):
    """Compute weighted uniqueness score across all dimensions."""
    weights = {
        "R-spectrum":   0.20,
        "Identities":   0.35,
        "Factorial":    0.15,
        "Gap ratio":    0.15,
        "Completeness": 0.15,
    }

    s_r, d_r = score_r_spectrum(n, st)
    s_id, n_unique, n_total, d_id = score_identities(n, st, limit)
    s_fac, d_fac = score_factorial_capacity(n, st)
    s_gap, d_gap = score_gap_ratio(n)
    s_comp, d_comp = score_completeness(n, st)

    scores = {
        "R-spectrum":   (s_r, d_r),
        "Identities":   (s_id, f"{n_unique}/{n_total} unique"),
        "Factorial":    (s_fac, d_fac),
        "Gap ratio":    (s_gap, d_gap),
        "Completeness": (s_comp, d_comp),
    }

    total = sum(weights[k] * scores[k][0] for k in weights)
    return total, scores, weights, d_id


# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="P6 Uniqueness Scorer — Why Perfect Number 6 is special"
    )
    parser.add_argument("--n", type=int, default=6,
                        help="Number to score (default: 6)")
    parser.add_argument("--compare", type=int, metavar="M",
                        help="Compare with another number (e.g., 28)")
    parser.add_argument("--identities", action="store_true",
                        help="Show all identity details")
    parser.add_argument("--limit", type=int, default=1000,
                        help="Search limit for uniqueness (default: 1000)")
    args = parser.parse_args()

    limit = max(args.limit, args.n + 100)
    st = tecsrs.SieveTables(limit)

    print()
    print("  ╔══════════════════════════════════════════════════════════╗")
    print("  ║  P6 Uniqueness Scorer — Perfect Number Specialness      ║")
    print("  ║  tecsrs Rust acceleration · exhaustive search           ║")
    print("  ╚══════════════════════════════════════════════════════════╝")
    print()

    def print_score(n):
        total, scores, weights, id_details = compute_full_score(n, st, limit)
        print(f"  n = {n}  (σ={st.sigma(n)}, τ={st.tau(n)}, φ={st.phi(n)}, sopfr={st.sopfr(n)})")
        print(f"  {'─'*55}")
        print(f"  {'Dimension':<20}  {'Weight':>6}  {'Score':>6}  {'Weighted':>8}  Detail")
        print(f"  {'─'*20}  {'─'*6}  {'─'*6}  {'─'*8}  {'─'*25}")
        for dim in weights:
            s, d = scores[dim]
            w = weights[dim]
            print(f"  {dim:<20}  {w:>6.0%}  {s:>6.2f}  {w*s:>8.3f}  {d}")
        print(f"  {'─'*55}")
        print(f"  {'TOTAL SCORE':<20}         {'':<6}  {total:>8.3f}")
        print()

        # Grade
        if total >= 0.9:
            grade = "⭐⭐⭐ EXCEPTIONAL"
        elif total >= 0.7:
            grade = "⭐⭐ STRONG"
        elif total >= 0.5:
            grade = "⭐ MODERATE"
        else:
            grade = "○ WEAK"
        print(f"  Grade: {grade} ({total:.1%})")
        print()

        if args.identities:
            print("  Identity Details:")
            for line in id_details:
                print(f"    {line}")
            print()

        return total

    score_n = print_score(args.n)

    if args.compare:
        print(f"  {'═'*55}")
        print()
        score_m = print_score(args.compare)

        print(f"  === Comparison ===")
        print(f"  n={args.n}: {score_n:.3f}")
        print(f"  n={args.compare}: {score_m:.3f}")
        ratio = score_n / score_m if score_m > 0 else float('inf')
        print(f"  Ratio: {ratio:.1f}x")
        print()


if __name__ == "__main__":
    main()
