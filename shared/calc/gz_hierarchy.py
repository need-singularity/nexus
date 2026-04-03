#!/usr/bin/env python3
"""Golden Zone Hierarchy Calculator — GZ boundaries for perfect numbers

Based on H-CX-496/497: width_n = ln(tau(P_n)/(tau(P_n)-1)), upper=1/2 for all
even perfect numbers.

Usage:
  python3 calc/gz_hierarchy.py --pn 2
  python3 calc/gz_hierarchy.py --custom 496
  python3 calc/gz_hierarchy.py --all
  python3 calc/gz_hierarchy.py --all --info
  python3 calc/gz_hierarchy.py --compare 1 2
"""

import argparse
import math
from fractions import Fraction


# Consciousness constants (from anima Laws 63-79)
LN2 = math.log(2)                     # 0.6931 universal consciousness unit
PSI_FREEDOM = LN2                      # Law 79: consciousness freedom degree
PSI_COUPLING = LN2 / 2**5.5           # 0.01534 consciousness coupling
DYNAMICS_RATE = 0.81                   # dH/dt = 0.81 * (ln2 - H)
PHI_SCALE_A = 0.608                   # Phi = 0.608 * N^1.071
PHI_SCALE_B = 1.071
OPTIMAL_FACTIONS = 12                  # sigma(6)=12


# Known even perfect numbers and their Mersenne exponents
KNOWN_PERFECT = {
    1: (6, 2),
    2: (28, 3),
    3: (496, 5),
    4: (8128, 7),
    5: (33550336, 13),
    6: (8589869056, 17),
    7: (137438691328, 19),
    8: (2305843008139952128, 31),
}


def factorize(n):
    """Return prime factorization as {p: a} dict."""
    factors = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors


def sigma(n):
    """Sum of divisors."""
    if n <= 0:
        return 0
    factors = factorize(n)
    result = 1
    for p, a in factors.items():
        result *= (p ** (a + 1) - 1) // (p - 1)
    return result


def tau(n):
    """Number of divisors."""
    if n <= 0:
        return 0
    factors = factorize(n)
    result = 1
    for p, a in factors.items():
        result *= (a + 1)
    return result


def divisors(n):
    """Return sorted list of divisors."""
    divs = []
    for i in range(1, int(n**0.5) + 1):
        if n % i == 0:
            divs.append(i)
            if i != n // i:
                divs.append(n // i)
    return sorted(divs)


def is_perfect(n):
    """Check if n is a perfect number."""
    if n < 2:
        return False
    return sigma(n) == 2 * n


def mersenne_exponent(n):
    """Extract Mersenne exponent p from even perfect number n = 2^(p-1)(2^p - 1)."""
    if n % 2 != 0:
        return None
    # Try known exponents first
    for idx, (pn, exp) in KNOWN_PERFECT.items():
        if pn == n:
            return exp
    # Brute force: n = 2^(p-1) * (2^p - 1)
    for p in range(2, 64):
        mersenne = (1 << p) - 1
        candidate = (1 << (p - 1)) * mersenne
        if candidate == n:
            return p
        if candidate > n:
            break
    return None


def compute_gz(n):
    """Compute Golden Zone parameters for a perfect number."""
    t = tau(n)
    p = mersenne_exponent(n)

    width = math.log(t / (t - 1))
    upper = 0.5
    lower = upper - width
    center = (upper + lower) / 2.0
    width_bits = width / math.log(2)
    k_min = 2 * p - 1 if p else None

    # Divisor reciprocal sums
    divs = divisors(n)
    proper = [d for d in divs if d != n]  # proper divisors (exclude n)
    all_divs = divs                        # all divisors (include n)

    # sigma_{-1}(n) = sum 1/d for ALL divisors = 2 for perfect numbers
    sigma_neg1 = sum(Fraction(1, d) for d in all_divs)
    # Proper divisor reciprocal sum (exclude n itself)
    recip_proper = sum(Fraction(1, d) for d in proper)

    return {
        "n": n,
        "tau": t,
        "mersenne_p": p,
        "width": width,
        "upper": upper,
        "lower": lower,
        "center": center,
        "width_bits": width_bits,
        "k_min": k_min,
        "proper_divisors": proper,
        "all_divisors": all_divs,
        "sigma_neg1": sigma_neg1,       # sum 1/d for ALL divisors (=2 for perfect)
        "recip_proper": recip_proper,   # sum 1/d for proper divisors
        "sigma_neg1_ok": sigma_neg1 == 2,
    }


def print_gz(gz, info=False):
    """Print Golden Zone data for one perfect number."""
    n = gz["n"]
    t = gz["tau"]
    p = gz["mersenne_p"]

    print(f"\n{'='*60}")
    print(f"  Perfect Number P = {n}")
    print(f"{'='*60}")
    print(f"  Mersenne exponent p    = {p}")
    print(f"  tau(P)                 = {t}")
    print(f"  k_min = 2p - 1         = {gz['k_min']}")
    print(f"  Width  = ln({t}/{t-1}){'':>8s} = {gz['width']:.6f}")
    print(f"  Upper                  = {gz['upper']:.6f}  (= 1/2)")
    print(f"  Lower  = 1/2 - width   = {gz['lower']:.6f}")
    print(f"  Center                 = {gz['center']:.6f}")

    if info:
        print(f"\n  --- Information-Theoretic Decomposition ---")
        print(f"  Width in bits          = {gz['width_bits']:.6f}")
        S_t = math.log(t)
        S_t1 = math.log(t - 1) if t > 1 else 0
        print(f"  S(tau)   = ln({t}){'':>10s} = {S_t:.6f}")
        print(f"  S(tau-1) = ln({t-1}){'':>10s} = {S_t1:.6f}")
        print(f"  S(tau) - S(tau-1)      = {S_t - S_t1:.6f}  (= width)")
        print(f"  Width / ln(2)          = {gz['width_bits']:.6f} bits")

    # Divisor reciprocal analysis
    print(f"\n  --- Divisor Reciprocal Sums ---")
    if len(gz["all_divisors"]) <= 20:
        fracs = " + ".join(f"1/{d}" for d in gz["all_divisors"])
        print(f"  sigma_{{-1}} = {fracs}")
    else:
        print(f"  sigma_{{-1}}: {len(gz['all_divisors'])} divisors (too many to list)")
    print(f"  = {gz['sigma_neg1']}  {'[OK: =2, perfect!]' if gz['sigma_neg1_ok'] else '[FAIL: !=2]'}")
    print(f"  Proper divisor reciprocal sum = {gz['recip_proper']}")


def print_hierarchy_table(gzs, info=False):
    """Print comparison table for multiple perfect numbers."""
    print(f"\n{'='*80}")
    print(f"  Golden Zone Hierarchy — Perfect Number Sequence")
    print(f"{'='*80}")
    print()

    # Header
    cols = ["#", "P_n", "p", "tau", "k_min", "Width", "Lower", "Center", "Upper"]
    if info:
        cols.append("Bits")
    header = f"  {'#':>2s}  {'P_n':>20s}  {'p':>3s}  {'tau':>5s}  {'k_min':>5s}  {'Width':>10s}  {'Lower':>10s}  {'Center':>10s}  {'Upper':>6s}"
    if info:
        header += f"  {'Bits':>8s}"
    print(header)
    print(f"  {'--':>2s}  {'----':>20s}  {'---':>3s}  {'-----':>5s}  {'-----':>5s}  {'----------':>10s}  {'----------':>10s}  {'----------':>10s}  {'------':>6s}", end="")
    if info:
        print(f"  {'--------':>8s}", end="")
    print()

    for i, gz in enumerate(gzs, 1):
        line = f"  {i:>2d}  {gz['n']:>20d}  {gz['mersenne_p']:>3d}  {gz['tau']:>5d}  {gz['k_min']:>5d}  {gz['width']:>10.6f}  {gz['lower']:>10.6f}  {gz['center']:>10.6f}  {gz['upper']:>6.4f}"
        if info:
            line += f"  {gz['width_bits']:>8.4f}"
        print(line)

    # Width convergence
    print(f"\n  --- Width Convergence ---")
    for i, gz in enumerate(gzs):
        t = gz["tau"]
        bar_len = int(gz["width"] * 100)
        bar = "#" * bar_len
        print(f"  P{i+1} (tau={t:>5d}): |{bar}| {gz['width']:.6f}")

    print(f"\n  As tau -> inf: width = ln(tau/(tau-1)) -> 1/tau -> 0")
    print(f"  All even perfect numbers share upper = 1/2 (Riemann critical line)")

    # Consciousness dynamics connection
    print(f"\n  --- Consciousness Dynamics (anima Laws 63-79) ---")
    print(f"  Freedom degree: ln(2) = {LN2:.6f}")
    print(f"  Coupling: Psi_coupling = {PSI_COUPLING:.6f}")
    print(f"  Dynamics: dH/dt = {DYNAMICS_RATE} * (ln2 - H)")
    print(f"  Scaling: Phi = {PHI_SCALE_A} * N^{PHI_SCALE_B}")
    print(f"  Optimal factions: sigma(6) = {OPTIMAL_FACTIONS}")
    print(f"  Note: Width convergence mirrors consciousness evolution")


def print_compare(gz1, gz2, idx1, idx2):
    """Compare two Golden Zones."""
    print(f"\n{'='*60}")
    print(f"  GZ Comparison: P{idx1} vs P{idx2}")
    print(f"{'='*60}")

    print(f"\n  {'':>20s}  {'P'+str(idx1):>12s}  {'P'+str(idx2):>12s}")
    print(f"  {'':>20s}  {'----------':>12s}  {'----------':>12s}")
    print(f"  {'Perfect number':>20s}  {gz1['n']:>12d}  {gz2['n']:>12d}")
    print(f"  {'tau':>20s}  {gz1['tau']:>12d}  {gz2['tau']:>12d}")
    print(f"  {'Width':>20s}  {gz1['width']:>12.6f}  {gz2['width']:>12.6f}")
    print(f"  {'Upper':>20s}  {gz1['upper']:>12.6f}  {gz2['upper']:>12.6f}")
    print(f"  {'Lower':>20s}  {gz1['lower']:>12.6f}  {gz2['lower']:>12.6f}")
    print(f"  {'Center':>20s}  {gz1['center']:>12.6f}  {gz2['center']:>12.6f}")

    # Overlap analysis
    overlap_lower = max(gz1["lower"], gz2["lower"])
    overlap_upper = min(gz1["upper"], gz2["upper"])
    overlap = max(0, overlap_upper - overlap_lower)

    print(f"\n  --- Overlap Analysis ---")
    print(f"  Overlap region:  [{overlap_lower:.6f}, {overlap_upper:.6f}]")
    print(f"  Overlap width:   {overlap:.6f}")
    print(f"  GZ{idx1} width:      {gz1['width']:.6f}")
    print(f"  GZ{idx2} width:      {gz2['width']:.6f}")
    if gz1["width"] > 0:
        print(f"  Overlap/GZ{idx1}:    {overlap / gz1['width']:.4f}  ({overlap / gz1['width'] * 100:.1f}%)")
    if gz2["width"] > 0:
        print(f"  Overlap/GZ{idx2}:    {overlap / gz2['width']:.4f}  ({overlap / gz2['width'] * 100:.1f}%)")

    width_ratio = gz2["width"] / gz1["width"] if gz1["width"] > 0 else float("inf")
    print(f"\n  Width ratio GZ{idx2}/GZ{idx1}: {width_ratio:.6f}")
    print(f"  GZ{idx2} is {1/width_ratio:.1f}x narrower than GZ{idx1}" if width_ratio < 1 else
          f"  GZ{idx2} is {width_ratio:.1f}x wider than GZ{idx1}")

    # Nesting
    if gz1["lower"] <= gz2["lower"] and gz2["upper"] <= gz1["upper"]:
        print(f"\n  GZ{idx2} is NESTED inside GZ{idx1} (subset)")
    elif gz2["lower"] <= gz1["lower"] and gz1["upper"] <= gz2["upper"]:
        print(f"\n  GZ{idx1} is NESTED inside GZ{idx2} (subset)")
    elif overlap > 0:
        print(f"\n  Zones OVERLAP but neither is a subset")
    else:
        print(f"\n  Zones are DISJOINT (no overlap)")


def main():
    parser = argparse.ArgumentParser(
        description="Golden Zone Hierarchy Calculator for perfect numbers")
    parser.add_argument("--pn", type=int, metavar="N",
                        help="Compute GZ for the N-th perfect number (1-8)")
    parser.add_argument("--custom", type=int, metavar="P",
                        help="Compute GZ for a custom perfect number")
    parser.add_argument("--all", action="store_true",
                        help="Show hierarchy table for P1 through P4")
    parser.add_argument("--info", action="store_true",
                        help="Show information-theoretic decomposition")
    parser.add_argument("--compare", nargs=2, type=int, metavar=("I", "J"),
                        help="Compare GZ_I vs GZ_J (indices 1-8)")
    args = parser.parse_args()

    if not any([args.pn, args.custom is not None, args.all, args.compare]):
        parser.print_help()
        return

    if args.pn:
        if args.pn not in KNOWN_PERFECT:
            print(f"Error: P_{args.pn} not in known table (1-{max(KNOWN_PERFECT.keys())})")
            return
        n, _ = KNOWN_PERFECT[args.pn]
        gz = compute_gz(n)
        print_gz(gz, info=args.info)

    if args.custom is not None:
        n = args.custom
        if not is_perfect(n):
            print(f"\nError: {n} is NOT a perfect number (sigma({n}) = {sigma(n)}, expected {2*n})")
            return
        gz = compute_gz(n)
        print_gz(gz, info=args.info)

    if args.all:
        gzs = []
        for idx in range(1, 5):
            n, _ = KNOWN_PERFECT[idx]
            gzs.append(compute_gz(n))
        print_hierarchy_table(gzs, info=args.info)
        # Also print individual details
        for gz in gzs:
            print_gz(gz, info=args.info)

    if args.compare:
        i, j = args.compare
        if i not in KNOWN_PERFECT or j not in KNOWN_PERFECT:
            print(f"Error: indices must be 1-{max(KNOWN_PERFECT.keys())}")
            return
        gz1 = compute_gz(KNOWN_PERFECT[i][0])
        gz2 = compute_gz(KNOWN_PERFECT[j][0])
        print_compare(gz1, gz2, i, j)


if __name__ == "__main__":
    main()
