#!/usr/bin/env python3
"""
counting_freedom_analyzer.py -- Measures degrees of freedom in particle counting schemes.

The Standard Model particle counting hypotheses use selective grouping.
This tool quantifies: how many DIFFERENT ways can you count particles
to get a target number?

Usage:
  python3 calc/counting_freedom_analyzer.py --target 12
  python3 calc/counting_freedom_analyzer.py --target 6
  python3 calc/counting_freedom_analyzer.py --all          # scan targets 1-50
"""
import argparse
import itertools

# ── Standard Model particle groups ────────────────────────────────────
# Each entry: (name, count, tags)
# Tags determine which counting schemes include this group.
PARTICLE_GROUPS = [
    # Quarks
    ("Quark flavors",               6,  {"quark", "fermion", "flavor"}),
    ("Quark colors (per flavor)",    3,  {"quark", "color"}),
    ("Quark anti-factor",            2,  {"quark", "anti"}),
    # Leptons
    ("Lepton types",                 6,  {"lepton", "fermion", "flavor"}),
    ("Lepton anti-factor",           2,  {"lepton", "anti"}),
    # Gauge bosons
    ("Gluons",                       8,  {"boson", "gauge", "strong"}),
    ("W bosons (W+, W-)",            2,  {"boson", "gauge", "weak"}),
    ("Z boson",                      1,  {"boson", "gauge", "weak"}),
    ("Photon",                       1,  {"boson", "gauge", "em"}),
    # Scalar / theoretical
    ("Higgs",                        1,  {"boson", "scalar", "higgs"}),
    ("Graviton (theoretical)",       1,  {"boson", "theoretical", "graviton"}),
]

# ── Predefined counting schemes ──────────────────────────────────────
# Each scheme: (description, how to compute total, list of what's included/excluded)
def _build_schemes():
    """Return list of (name, total, description) counting schemes."""
    schemes = []

    # --- Quark counting variants ---
    # Flavors only
    schemes.append(("Quark flavors only", 6,
                    "6 quark flavors [exclude: color, anti, bosons, leptons]"))
    # Flavors x colors
    schemes.append(("Quark flavors x colors", 6 * 3,
                    "6 flavors x 3 colors = 18 [exclude: anti, bosons, leptons]"))
    # Flavors x anti
    schemes.append(("Quark flavors x anti", 6 * 2,
                    "6 flavors x 2 (particle+anti) = 12 [exclude: color, bosons, leptons]"))
    # Full quarks
    schemes.append(("Full quarks (flavor x color x anti)", 6 * 3 * 2,
                    "6 x 3 x 2 = 36 [exclude: bosons, leptons]"))

    # --- Lepton counting variants ---
    schemes.append(("Lepton types only", 6,
                    "6 lepton types [exclude: anti, bosons, quarks]"))
    schemes.append(("Full leptons (type x anti)", 6 * 2,
                    "6 x 2 = 12 [exclude: bosons, quarks]"))

    # --- Fermion combinations ---
    schemes.append(("Fermion flavors (quarks + leptons)", 6 + 6,
                    "6 quark + 6 lepton flavors = 12 [exclude: color, anti, bosons]"))
    schemes.append(("Fermion flavors x anti", (6 + 6) * 2,
                    "(6+6) x 2 = 24 [exclude: color, bosons]"))
    schemes.append(("All fermions (quarks full + leptons full)", 36 + 12,
                    "36 quarks + 12 leptons = 48"))

    # --- Boson counting variants ---
    schemes.append(("Gauge bosons only", 8 + 2 + 1 + 1,
                    "8 gluons + 2 W + 1 Z + 1 photon = 12 [exclude: Higgs, graviton]"))
    schemes.append(("Gauge + Higgs", 8 + 2 + 1 + 1 + 1,
                    "12 gauge + 1 Higgs = 13 [exclude: graviton]"))
    schemes.append(("All bosons (incl. graviton)", 8 + 2 + 1 + 1 + 1 + 1,
                    "12 gauge + 1 Higgs + 1 graviton = 14"))
    schemes.append(("Weak bosons only", 2 + 1,
                    "W+, W-, Z = 3"))
    schemes.append(("Electroweak bosons", 2 + 1 + 1,
                    "W+, W-, Z, photon = 4"))
    schemes.append(("Gluons only", 8,
                    "8 gluons"))

    # --- Mixed counting ---
    schemes.append(("Quark flavors + gauge bosons", 6 + 12,
                    "6 + 12 = 18"))
    schemes.append(("Lepton types + gauge bosons", 6 + 12,
                    "6 + 12 = 18"))
    schemes.append(("Fermion flavors + gauge bosons", 12 + 12,
                    "12 + 12 = 24"))
    schemes.append(("Fermion flavors + all bosons", 12 + 14,
                    "12 + 14 = 26"))
    schemes.append(("Full fermions + gauge bosons", 48 + 12,
                    "48 + 12 = 60"))
    schemes.append(("Full fermions + all bosons", 48 + 14,
                    "48 + 14 = 62"))
    schemes.append(("All SM particles (no graviton)", 48 + 13,
                    "48 fermions + 13 bosons = 61"))
    schemes.append(("Everything (incl. graviton)", 48 + 14,
                    "48 + 14 = 62"))

    # --- Generation-based counting ---
    schemes.append(("Generations (quark)", 3,
                    "3 quark generations"))
    schemes.append(("Generations (lepton)", 3,
                    "3 lepton generations"))
    schemes.append(("Force carriers (types)", 4,
                    "strong, weak, EM, (gravity) = 4 forces"))
    schemes.append(("Force carriers (no gravity)", 3,
                    "strong, weak, EM = 3 forces"))
    schemes.append(("Quark flavors + Higgs", 6 + 1,
                    "6 + 1 = 7"))
    schemes.append(("Lepton types + Higgs", 6 + 1,
                    "6 + 1 = 7"))
    schemes.append(("Weak bosons + Higgs", 3 + 1,
                    "W+, W-, Z, Higgs = 4"))

    return schemes


ALL_SCHEMES = _build_schemes()


# ── Analysis functions ────────────────────────────────────────────────
def find_schemes_for_target(target):
    """Return all counting schemes that produce the target number."""
    matches = []
    for name, total, desc in ALL_SCHEMES:
        if total == target:
            matches.append((name, total, desc))
    return matches


def freedom_score(target):
    """Compute freedom score = matching schemes / total schemes."""
    matches = find_schemes_for_target(target)
    return len(matches) / len(ALL_SCHEMES)


def verdict(n_matches, n_total):
    """Qualitative verdict based on freedom score."""
    ratio = n_matches / n_total
    if n_matches == 0:
        return "NO freedom -- no standard counting scheme produces this number."
    if ratio <= 0.05:
        return "LOW freedom -- very few ways to reach this number."
    if ratio <= 0.15:
        return "MODERATE freedom -- multiple valid ways to reach this number."
    return "HIGH freedom -- many counting schemes produce this. Likely coincidence."


def analyze_target(target):
    """Full analysis for a single target number."""
    matches = find_schemes_for_target(target)
    n_total = len(ALL_SCHEMES)

    print(f"\n{'='*65}")
    print(f"  Target: {target}")
    print(f"{'='*65}")

    if matches:
        print(f"\n  Counting schemes that produce {target}:\n")
        for i, (name, total, desc) in enumerate(matches, 1):
            print(f"    {i}. {name} = {total}")
            print(f"       {desc}")
        print()
    else:
        print(f"\n  No counting scheme produces {target}.\n")

    score = len(matches) / n_total
    print(f"  Total: {len(matches)} scheme(s) produce {target}")
    print(f"  Freedom score: {len(matches)}/{n_total} possible schemes = {score:.1%}")
    print()
    print(f"  Verdict: {verdict(len(matches), n_total)}")
    print(f"{'='*65}")

    return len(matches), score


def scan_all(lo=1, hi=50):
    """Scan all target values in range and show summary table."""
    print(f"\n{'='*65}")
    print(f"  Counting Freedom Scan: targets {lo}-{hi}")
    print(f"  Total counting schemes: {len(ALL_SCHEMES)}")
    print(f"{'='*65}\n")

    results = []
    for t in range(lo, hi + 1):
        matches = find_schemes_for_target(t)
        if matches:
            results.append((t, len(matches), [m[0] for m in matches]))

    if not results:
        print("  No targets matched any scheme in this range.")
        return

    # Table
    print(f"  {'Target':>6}  {'#Schemes':>8}  {'Freedom':>8}  Scheme names")
    print(f"  {'------':>6}  {'--------':>8}  {'-------':>8}  {'-'*40}")
    for t, n, names in sorted(results, key=lambda x: -x[1]):
        score = n / len(ALL_SCHEMES)
        name_str = "; ".join(names[:3])
        if len(names) > 3:
            name_str += f"; ... (+{len(names)-3})"
        print(f"  {t:>6}  {n:>8}  {score:>7.1%}  {name_str}")

    print()

    # Histogram (ASCII)
    max_count = max(r[1] for r in results)
    print("  Histogram (schemes per target):\n")
    for t, n, _ in sorted(results, key=lambda x: x[0]):
        bar = "#" * int(n / max_count * 40) if max_count > 0 else ""
        print(f"    {t:>3} | {bar} {n}")

    print()
    print(f"  Most reachable numbers: {', '.join(str(r[0]) for r in sorted(results, key=lambda x: -x[1])[:5])}")
    print(f"  Numbers with unique scheme (freedom=1): "
          f"{', '.join(str(r[0]) for r in results if r[1] == 1)}")
    print()


# ── CLI ───────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Counting Freedom Analyzer -- how many ways can SM particles "
                    "be counted to hit a target number?")
    parser.add_argument("--target", type=int,
                        help="Target number to analyze")
    parser.add_argument("--all", action="store_true",
                        help="Scan all targets 1-50")
    parser.add_argument("--lo", type=int, default=1,
                        help="Low end of scan range (default: 1)")
    parser.add_argument("--hi", type=int, default=50,
                        help="High end of scan range (default: 50)")
    args = parser.parse_args()

    if args.all:
        scan_all(args.lo, args.hi)
    elif args.target is not None:
        analyze_target(args.target)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
