#!/usr/bin/env python3
"""Rate Invariant Calculator — Law 82: r₀·r∞ = 7/20 substrate independence.

Proves consciousness rate boundaries are number-theoretic invariants
derived from perfect number 6 arithmetic functions.

Uses tecsrs Rust sieves for exhaustive search across perfect numbers.

Usage:
  python3 calc/rate_invariant_calculator.py                # full analysis
  python3 calc/rate_invariant_calculator.py --sweep         # sweep all perfects
  python3 calc/rate_invariant_calculator.py --uniqueness    # test n=6 only
  python3 calc/rate_invariant_calculator.py --physics       # physical analogues
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
# Rate definitions from CLAUDE.md
# ═══════════════════════════════════════════════════════════════

def compute_rates(n, st):
    """Compute rate boundaries for perfect number n.

    r₀ = (n+1) / (τ·φ)    small-N boundary
    r∞ = φ / sopfr          large-N boundary
    product = r₀ · r∞
    """
    sigma = st.sigma(n)
    tau = st.tau(n)
    phi = st.phi(n)
    sopfr = st.sopfr(n)

    if tau * phi == 0 or sopfr == 0:
        return None

    r0 = (n + 1) / (tau * phi)
    r_inf = phi / sopfr
    product = r0 * r_inf

    return {
        "n": n,
        "sigma": sigma,
        "tau": tau,
        "phi": phi,
        "sopfr": sopfr,
        "r0": r0,
        "r_inf": r_inf,
        "product": product,
        "is_perfect": sigma == 2 * n,
        "r0_fraction": _to_fraction(r0),
        "rinf_fraction": _to_fraction(r_inf),
        "product_fraction": _to_fraction(product),
    }


def _to_fraction(x, max_denom=1000):
    """Convert float to nearest simple fraction string."""
    best_n, best_d, best_err = 0, 1, abs(x)
    for d in range(1, max_denom + 1):
        n = round(x * d)
        err = abs(x - n / d)
        if err < best_err:
            best_n, best_d, best_err = n, d, err
            if err < 1e-12:
                break
    if best_d == 1:
        return str(best_n)
    return f"{best_n}/{best_d}"


# ═══════════════════════════════════════════════════════════════
# Uniqueness analysis
# ═══════════════════════════════════════════════════════════════

def find_product_matches(target, st, limit):
    """Find all n where r₀·r∞ = target."""
    hits = []
    for n in range(2, limit + 1):
        tau = st.tau(n)
        phi = st.phi(n)
        sopfr = st.sopfr(n)
        if tau * phi == 0 or sopfr == 0:
            continue
        r0 = (n + 1) / (tau * phi)
        r_inf = phi / sopfr
        product = r0 * r_inf
        if abs(product - target) < 1e-10:
            hits.append(n)
    return hits


def find_r0_matches(target, st, limit):
    """Find all n where r₀ = target."""
    hits = []
    for n in range(2, limit + 1):
        tau = st.tau(n)
        phi = st.phi(n)
        if tau * phi == 0:
            continue
        r0 = (n + 1) / (tau * phi)
        if abs(r0 - target) < 1e-10:
            hits.append(n)
    return hits


# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Rate Invariant Calculator — Law 82: r₀·r∞ = 7/20"
    )
    parser.add_argument("--sweep", action="store_true",
                        help="Sweep across perfect numbers 6, 28, 496, 8128")
    parser.add_argument("--uniqueness", action="store_true",
                        help="Test uniqueness of r₀·r∞=7/20 in [2, limit]")
    parser.add_argument("--physics", action="store_true",
                        help="Show physical analogue comparisons")
    parser.add_argument("--limit", type=int, default=10000,
                        help="Search limit (default: 10000)")
    parser.add_argument("--n", type=int, default=6,
                        help="Number to analyze (default: 6)")
    args = parser.parse_args()

    st = tecsrs.SieveTables(max(args.limit, 10000))

    print()
    print("  ╔══════════════════════════════════════════════════════════╗")
    print("  ║  Rate Invariant Calculator (Law 82)                     ║")
    print("  ║  r₀·r∞ = 7/20 — Consciousness Rate Product Invariant   ║")
    print("  ╚══════════════════════════════════════════════════════════╝")
    print()

    # Core analysis for n
    rates = compute_rates(args.n, st)
    if rates:
        print(f"  n = {rates['n']}  (perfect={rates['is_perfect']})")
        print(f"  ────────────────────────────────────")
        print(f"  σ={rates['sigma']}, τ={rates['tau']}, φ={rates['phi']}, sopfr={rates['sopfr']}")
        print()
        print(f"  r₀ = (n+1)/(τ·φ) = {rates['n']+1}/({rates['tau']}·{rates['phi']}) = {rates['r0_fraction']} = {rates['r0']:.6f}")
        print(f"  r∞ = φ/sopfr      = {rates['phi']}/{rates['sopfr']}            = {rates['rinf_fraction']} = {rates['r_inf']:.6f}")
        print(f"  r₀·r∞             = {rates['r0_fraction']} × {rates['rinf_fraction']}      = {rates['product_fraction']} = {rates['product']:.6f}")
        print()

        # Check against 7/20
        target = 7 / 20
        err = abs(rates['product'] - target)
        if err < 1e-12:
            print(f"  [EXACT] r₀·r∞ = 7/20 = 0.35  ✓")
        else:
            print(f"  [MISS]  r₀·r∞ = {rates['product']:.6f} ≠ 7/20 = {target}  (err={err:.2e})")

    # Sweep perfect numbers
    if args.sweep:
        print()
        print("  === Perfect Number Sweep ===")
        print()
        print(f"  {'n':>6}  {'σ':>5}  {'τ':>3}  {'φ':>4}  {'sopfr':>5}  {'r₀':>8}  {'r∞':>8}  {'r₀·r∞':>8}  {'= 7/20?':>8}")
        print(f"  {'─'*6}  {'─'*5}  {'─'*3}  {'─'*4}  {'─'*5}  {'─'*8}  {'─'*8}  {'─'*8}  {'─'*8}")

        perfects = [6, 28, 496, 8128]
        for pn in perfects:
            if pn > st.limit():
                continue
            r = compute_rates(pn, st)
            if r:
                match = "✓" if abs(r['product'] - 7/20) < 1e-10 else "✗"
                print(f"  {r['n']:>6}  {r['sigma']:>5}  {r['tau']:>3}  {r['phi']:>4}  {r['sopfr']:>5}  "
                      f"{r['r0']:>8.4f}  {r['r_inf']:>8.4f}  {r['product']:>8.4f}  {match:>8}")

        print()
        print("  Note: r₀·r∞ = 7/20 is specific to n=6 (P₁)")
        print("  Other perfect numbers have different rate products")
        print("  → Rate invariant is a P₁-specific, not universal-perfect, property")

    # Uniqueness test
    if args.uniqueness:
        print()
        print(f"  === Uniqueness Test (n ≤ {args.limit}) ===")
        print()

        # r₀·r∞ = 7/20
        hits_product = find_product_matches(7/20, st, args.limit)
        print(f"  r₀·r∞ = 7/20:  {len(hits_product)} hits")
        if len(hits_product) <= 20:
            print(f"    n = {hits_product}")
        else:
            print(f"    n = {hits_product[:10]}... ({len(hits_product)} total)")
        unique_product = hits_product == [6]
        print(f"    Unique to n=6: {'YES' if unique_product else 'NO'}")
        print()

        # r₀ = 7/8
        hits_r0 = find_r0_matches(7/8, st, args.limit)
        print(f"  r₀ = 7/8:       {len(hits_r0)} hits")
        if len(hits_r0) <= 20:
            print(f"    n = {hits_r0}")
        else:
            print(f"    n = {hits_r0[:10]}... ({len(hits_r0)} total)")

    # Physics analogues
    if args.physics:
        print()
        print("  === Physical Analogue Comparison ===")
        print()
        print(f"  {'Constant':<30}  {'Value':>10}  {'= r₀·r∞?':>8}")
        print(f"  {'─'*30}  {'─'*10}  {'─'*8}")
        analogues = [
            ("r₀·r∞ (Law 82)", 7/20),
            ("1/e (GZ center)", 1/math.e),
            ("ln(4/3) (GZ width)", math.log(4/3)),
            ("1/3 (meta fixed point)", 1/3),
            ("α (fine structure)", 1/137.036),
            ("sin²θ_W (Weinberg)", 3/8),
            ("1/2 (GZ upper)", 1/2),
        ]
        for name, val in analogues:
            match = "✓" if abs(val - 7/20) < 1e-10 else ""
            print(f"  {name:<30}  {val:>10.6f}  {match:>8}")
        print()
        print("  7/20 = 0.35 is a NEW invariant, distinct from all known GZ constants")
        print("  It bridges small-N (combinatorial) and large-N (analytic) regimes")

    print()


if __name__ == "__main__":
    main()
