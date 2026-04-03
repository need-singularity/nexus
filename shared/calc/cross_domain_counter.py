#!/usr/bin/env python3
"""Cross-Domain Match Counter -- Count how many cross-domain facts match arithmetic targets of n.

Built-in fact database spans chemistry, music, crystallography, math, biology,
medicine, physics, and institutions. Supports Monte Carlo baseline testing,
sweep ranking, efficiency analysis, and carbon-fact removal.

Usage:
  python3 calc/cross_domain_counter.py --target 6
  python3 calc/cross_domain_counter.py --sweep 2 100
  python3 calc/cross_domain_counter.py --target 6 --monte-carlo 10000
  python3 calc/cross_domain_counter.py --target 6 --efficiency
  python3 calc/cross_domain_counter.py --target 6 --remove-carbon
  python3 calc/cross_domain_counter.py --sweep 2 100 --facts-file facts.json
"""

import argparse
import json
import math
import random
import sys
from collections import Counter, defaultdict

try:
    import tecsrs
    _HAS_TECSRS = True
except ImportError:
    _HAS_TECSRS = False


# ═══════════════════════════════════════════════════════════════
# Number-theoretic helpers
# ═══════════════════════════════════════════════════════════════

_sieve_cache = {}

def _get_sieve(limit):
    """Get or create sieve tables up to limit."""
    if limit in _sieve_cache:
        return _sieve_cache[limit]
    if _HAS_TECSRS:
        tables = tecsrs.SieveTables(limit)
        _sieve_cache[limit] = tables
        return tables
    return None


def divisors(n):
    d = []
    for i in range(1, int(n**0.5) + 1):
        if n % i == 0:
            d.append(i)
            if i != n // i:
                d.append(n // i)
    return sorted(d)


def sigma(n):
    if _HAS_TECSRS:
        tables = _get_sieve(max(n + 1, 10001))
        return int(tables.sigma(n))
    return sum(divisors(n))


def tau(n):
    if _HAS_TECSRS:
        tables = _get_sieve(max(n + 1, 10001))
        return int(tables.tau(n))
    return len(divisors(n))


def phi(n):
    if _HAS_TECSRS:
        tables = _get_sieve(max(n + 1, 10001))
        return int(tables.phi(n))
    result = n
    p = 2
    temp = n
    while p * p <= temp:
        if temp % p == 0:
            while temp % p == 0:
                temp //= p
            result -= result // p
        p += 1
    if temp > 1:
        result -= result // temp
    return result


def sigma_neg1(n):
    return sum(1.0 / d for d in divisors(n))


def is_perfect(n):
    return sigma(n) == 2 * n


def lcm(a, b):
    return a * b // math.gcd(a, b)


# ═══════════════════════════════════════════════════════════════
# Arithmetic target set (identical to verify_cross_domain_texas.py)
# ═══════════════════════════════════════════════════════════════

def arithmetic_targets(n):
    """Generate the set of natural arithmetic outputs from n.

    Includes: n, divisors, sigma, tau, phi, sigma_{-1},
    products/quotients of pairs, powers, LCM of divisor pairs,
    factorials of small divisors, abundancy, n-tau.
    Same function for ALL n -- no n=6 special casing.
    """
    d = divisors(n)
    s = sigma(n)
    t = tau(n)
    p = phi(n)
    sn1 = sigma_neg1(n)

    targets = set()

    targets.add(n)
    targets.add(s)
    targets.add(t)
    targets.add(p)
    targets.add(round(sn1, 8))

    for dd in d:
        targets.add(dd)
        targets.add(round(1.0 / dd, 8))

    for dd in d:
        targets.add(n - dd)

    targets.add(n * n)
    targets.add(n ** 3)

    for dd in d:
        if dd <= 20:
            targets.add(2 ** dd)

    core = [n, s, t, p, round(sn1, 8)]
    for i, a in enumerate(core):
        for b in core[i:]:
            targets.add(round(a * b, 8))
            if b != 0:
                targets.add(round(a / b, 8))
            if a != 0:
                targets.add(round(b / a, 8))

    for i, a in enumerate(d):
        for b in d[i + 1:]:
            targets.add(lcm(a, b))

    for dd in d:
        if dd <= 10:
            targets.add(math.factorial(dd))

    targets.add(round(s / n, 8))
    targets.add(n - t)

    targets = {x for x in targets if isinstance(x, (int, float))
               and -1 <= x <= 10000 and not (isinstance(x, float) and math.isnan(x))}
    return targets


# ═══════════════════════════════════════════════════════════════
# Built-in fact database
# ═══════════════════════════════════════════════════════════════

DEFAULT_FACTS = [
    # CHEMISTRY
    {"val": 6,   "domain": "chemistry", "desc": "Carbon atomic number Z=6", "carbon": True},
    {"val": 4,   "domain": "chemistry", "desc": "sp3 bonds = 4 (tetrahedral)", "carbon": True},
    {"val": 24,  "domain": "chemistry", "desc": "Benzene D6h symmetry order = 24", "carbon": True},
    {"val": 12,  "domain": "chemistry", "desc": "Octahedron edges = 12", "carbon": False},
    {"val": 24,  "domain": "chemistry", "desc": "Methane Td symmetry order = 24", "carbon": True},
    {"val": 12,  "domain": "chemistry", "desc": "Cyclohexane has 12 H atoms", "carbon": True},
    {"val": 2,   "domain": "chemistry", "desc": "Graphene unit cell = 2 atoms", "carbon": True},
    {"val": 12,  "domain": "chemistry", "desc": "Diamond 2nd-neighbor count = 12", "carbon": True},
    {"val": 12,  "domain": "chemistry", "desc": "C60 has 12 pentagons", "carbon": True},
    {"val": 3,   "domain": "chemistry", "desc": "Max bond order = 3 (triple bond)", "carbon": False},
    {"val": 4,   "domain": "chemistry", "desc": "sigma + pi orbital types = 4 (s,px,py,pz)", "carbon": True},
    {"val": 6,   "domain": "chemistry", "desc": "CHNOPS = 6 life elements", "carbon": True},
    {"val": 6,   "domain": "chemistry", "desc": "Glycolysis: glucose C6 splits to 2x C3", "carbon": True},
    {"val": 6,   "domain": "chemistry", "desc": "6 reading frames (3 forward + 3 reverse)", "carbon": False},
    # CRYSTALLOGRAPHY
    {"val": 6,   "domain": "crystal", "desc": "Kissing number K(2D) = 6", "carbon": False},
    {"val": 12,  "domain": "crystal", "desc": "Kissing number K(3D) = 12", "carbon": False},
    {"val": 24,  "domain": "crystal", "desc": "Kissing number K(4D) = 24", "carbon": False},
    {"val": 2,   "domain": "crystal", "desc": "Kissing number K(1D) = 2", "carbon": False},
    {"val": 6,   "domain": "crystal", "desc": "Cube faces = 6", "carbon": False},
    {"val": 12,  "domain": "crystal", "desc": "Platonic solid: all have E = 6k edges", "carbon": False},
    # MUSIC
    {"val": 12,  "domain": "music", "desc": "12 semitones per octave", "carbon": False},
    {"val": 2,   "domain": "music", "desc": "Octave = frequency ratio 2:1", "carbon": False},
    {"val": 3,   "domain": "music", "desc": "Perfect fifth = 3:2 ratio", "carbon": False},
    {"val": 12,  "domain": "music", "desc": "LCM of consonance ratios = LCM(2,3,4,6) = 12", "carbon": False},
    # MATHEMATICS
    {"val": 2,   "domain": "math", "desc": "n=6: n - tau(n) = 6 - 4 = 2 = phi(6)", "carbon": False},
    {"val": 6,   "domain": "math", "desc": "R(3,3) = 6 (Ramsey number)", "carbon": False},
    {"val": 720, "domain": "math", "desc": "6! = 720, D(6)/6! ~ 1/e", "carbon": False},
    {"val": 2,   "domain": "math", "desc": "sigma(6)/6 = 2 (perfect number)", "carbon": False},
    {"val": 2,   "domain": "math", "desc": "Euler formula V-E+F = 2", "carbon": False},
    {"val": 132, "domain": "math", "desc": "Catalan(6) = 132", "carbon": False},
    {"val": 1,   "domain": "math", "desc": "1/1 + 1/2 + 1/3 + 1/6 = 2 = sigma_{-1}(6)", "carbon": False},
    # BIOLOGY
    {"val": 6,   "domain": "biology", "desc": "Telomere repeat TTAGGG = 6 nucleotides", "carbon": False},
    {"val": 64,  "domain": "biology", "desc": "Genetic code: 64 = 2^6 codons", "carbon": False},
    {"val": 6,   "domain": "biology", "desc": "ATP synthase is a hexamer (6 subunits)", "carbon": False},
    {"val": 6,   "domain": "biology", "desc": "6 major CYP450 families", "carbon": False},
    # MEDICINE
    {"val": 6,   "domain": "medicine", "desc": "SOFA score: 6 organ systems", "carbon": False},
    {"val": 12,  "domain": "medicine", "desc": "GCS range = 15-3 = 12 possible scores", "carbon": False},
    # PHYSICS
    {"val": 6,   "domain": "physics", "desc": "ISCO radius = 6M (Schwarzschild)", "carbon": False},
    {"val": 12,  "domain": "physics", "desc": "ISCO L^2 = 12M^2 (angular momentum)", "carbon": False},
    # INSTITUTIONS
    {"val": 12,  "domain": "institution", "desc": "12 months in a year", "carbon": False},
    {"val": 24,  "domain": "institution", "desc": "24 hours in a day", "carbon": False},
    {"val": 60,  "domain": "institution", "desc": "60 seconds/minutes (sexagesimal)", "carbon": False},
    {"val": 12,  "domain": "institution", "desc": "Common law jury = 12", "carbon": False},
    {"val": 6,   "domain": "institution", "desc": "Petit jury = 6 (US states)", "carbon": False},
]


# ═══════════════════════════════════════════════════════════════
# Matching logic
# ═══════════════════════════════════════════════════════════════

def matches_targets(fact_val, targets):
    """Check if fact_val matches any value in targets."""
    for t in targets:
        if isinstance(fact_val, int) or (isinstance(fact_val, float) and fact_val == int(fact_val)):
            if fact_val == t:
                return True
            if abs(fact_val - t) < 0.0001:
                return True
        else:
            if abs(fact_val) > 0.001:
                if abs(fact_val - t) / abs(fact_val) < 0.01:
                    return True
            else:
                if abs(fact_val - t) < 0.001:
                    return True
    return False


def count_matches(n, facts):
    """Count how many facts match arithmetic targets of n."""
    targets = arithmetic_targets(n)
    matched = [f for f in facts if matches_targets(f["val"], targets)]
    return len(matched), matched, len(targets)


# ═══════════════════════════════════════════════════════════════
# Monte Carlo
# ═══════════════════════════════════════════════════════════════

def monte_carlo(facts, n_trials=10000, n_range=(2, 101), seed=42):
    """Random baseline: draw random n, count matches."""
    rng = random.Random(seed)
    counts = []
    for _ in range(n_trials):
        n = rng.randint(n_range[0], n_range[1] - 1)
        c, _, _ = count_matches(n, facts)
        counts.append(c)
    return counts


# ═══════════════════════════════════════════════════════════════
# Output helpers
# ═══════════════════════════════════════════════════════════════

def print_ranking(results, top=30, label="ALL FACTS"):
    """Print ranking table."""
    sorted_r = sorted(results.items(), key=lambda x: -x[1]["count"])
    print(f"\n  Ranking (top {min(top, len(sorted_r))}, {label}):")
    print(f"  {'Rank':>4s}  {'n':>4s}  {'Matches':>7s}  {'Targets':>7s}  {'Perf':>5s}")
    print(f"  {'----':>4s}  {'----':>4s}  {'-------':>7s}  {'-------':>7s}  {'----':>5s}")
    for rank, (n, info) in enumerate(sorted_r[:top], 1):
        perf = "YES" if is_perfect(n) else ""
        print(f"  {rank:4d}  {n:4d}  {info['count']:7d}  {info['targets']:7d}  {perf:>5s}")


def print_domain_breakdown(matched):
    """Print matches grouped by domain."""
    domains = defaultdict(list)
    for f in matched:
        domains[f["domain"]].append(f["desc"])
    for dom in sorted(domains):
        print(f"    {dom:15s}: {len(domains[dom])} matches")
        for desc in domains[dom]:
            print(f"      - {desc}")


def print_mc_results(mc_counts, observed, n_trials):
    """Print Monte Carlo distribution and p-value."""
    mean = sum(mc_counts) / len(mc_counts)
    std = (sum((x - mean) ** 2 for x in mc_counts) / len(mc_counts)) ** 0.5
    z = (observed - mean) / std if std > 0 else 0
    p = sum(1 for x in mc_counts if x >= observed) / n_trials

    print(f"\n  Monte Carlo ({n_trials:,} trials):")
    print(f"    Mean:    {mean:.2f} +/- {std:.2f}")
    print(f"    Observed: {observed}")
    print(f"    Z-score: {z:.3f}")
    if p == 0:
        print(f"    p-value: < {1.0 / n_trials:.1e}")
    else:
        print(f"    p-value: {p:.6f}")

    # Histogram
    hist = Counter(mc_counts)
    lo, hi = min(hist), max(hist)
    max_bar = max(hist.values())
    print(f"\n  {'Matches':>8s}  {'Count':>7s}  {'Pct':>6s}  Histogram")
    for k in range(lo, hi + 2):
        c = hist.get(k, 0)
        pct = 100.0 * c / n_trials
        bar = "#" * int(40 * c / max_bar) if max_bar > 0 else ""
        tag = " <-- observed" if k == observed else ""
        print(f"  {k:8d}  {c:7d}  {pct:5.1f}%  {bar}{tag}")

    return z, p


# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Cross-Domain Match Counter -- rank numbers by cross-domain fact matches"
    )
    parser.add_argument("--target", type=int, help="Count matches for specific n")
    parser.add_argument("--sweep", type=int, nargs=2, metavar=("LO", "HI"),
                        help="Sweep n from LO to HI inclusive, rank by matches")
    parser.add_argument("--facts-file", type=str,
                        help="Load custom fact list from JSON (list of {val, domain, desc, carbon})")
    parser.add_argument("--monte-carlo", type=int, default=0, metavar="TRIALS",
                        help="Run Monte Carlo baseline with N trials")
    parser.add_argument("--efficiency", action="store_true",
                        help="Show matches-per-target efficiency")
    parser.add_argument("--remove-carbon", action="store_true",
                        help="Exclude carbon-specific facts")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    # Load facts
    if args.facts_file:
        with open(args.facts_file) as f:
            facts = json.load(f)
        print(f"  Loaded {len(facts)} facts from {args.facts_file}")
    else:
        facts = list(DEFAULT_FACTS)

    if args.remove_carbon:
        before = len(facts)
        facts = [f for f in facts if not f.get("carbon", False)]
        print(f"  Removed carbon facts: {before} -> {len(facts)}")

    total = len(facts)
    domains = set(f["domain"] for f in facts)
    print(f"\n  Facts: {total} across {len(domains)} domains")
    for dom, cnt in sorted(Counter(f["domain"] for f in facts).items(), key=lambda x: -x[1]):
        print(f"    {dom:15s}: {cnt}")

    # ── Single target ──
    if args.target is not None:
        n = args.target
        count, matched, tsize = count_matches(n, facts)
        print(f"\n  n={n}: {count}/{total} matches ({tsize} arithmetic targets)")
        if matched:
            print_domain_breakdown(matched)
        missed = [f for f in facts if f not in matched]
        if missed:
            print(f"\n  Missed ({len(missed)}):")
            for f in missed:
                print(f"    [{f['domain']:12s}] val={f['val']:>6g}  {f['desc']}")

        if args.efficiency:
            eff = count / tsize if tsize > 0 else 0
            print(f"\n  Efficiency: {count}/{tsize} = {eff:.4f} matches/target")

        if args.monte_carlo > 0:
            mc = monte_carlo(facts, n_trials=args.monte_carlo, seed=args.seed)
            print_mc_results(mc, count, args.monte_carlo)

    # ── Sweep ──
    if args.sweep:
        lo, hi = args.sweep
        results = {}
        for n in range(lo, hi + 1):
            c, m, ts = count_matches(n, facts)
            results[n] = {"count": c, "targets": ts, "perfect": is_perfect(n)}

        print_ranking(results, top=30,
                      label=f"n={lo}..{hi}" + (" no-carbon" if args.remove_carbon else ""))

        if args.efficiency:
            effs = sorted(
                [(n, info["count"] / info["targets"] if info["targets"] > 0 else 0)
                 for n, info in results.items()],
                key=lambda x: -x[1],
            )
            print(f"\n  Efficiency ranking (matches / targets):")
            print(f"  {'n':>4s}  {'Match':>5s}  {'Targets':>7s}  {'Eff':>8s}")
            print(f"  {'--':>4s}  {'-----':>5s}  {'-------':>7s}  {'--------':>8s}")
            for n, eff in effs[:20]:
                print(f"  {n:4d}  {results[n]['count']:5d}  {results[n]['targets']:7d}  {eff:8.4f}")

        if args.monte_carlo > 0:
            # Use best observed count as reference
            best_n = max(results, key=lambda n: results[n]["count"])
            best_c = results[best_n]["count"]
            print(f"\n  Best: n={best_n} with {best_c} matches")
            mc = monte_carlo(facts, n_trials=args.monte_carlo, seed=args.seed,
                             n_range=(lo, hi + 1))
            print_mc_results(mc, best_c, args.monte_carlo)

    if args.target is None and args.sweep is None:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
