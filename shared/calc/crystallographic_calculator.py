#!/usr/bin/env python3
"""Crystallographic Calculator — Crystallographic restriction, Platonic solids, kissing numbers, point groups.

Reusable calc/ tool derived from verify/verify_crystal_extreme.py.

Usage:
  python3 calc/crystallographic_calculator.py --restriction
  python3 calc/crystallographic_calculator.py --platonic
  python3 calc/crystallographic_calculator.py --kissing
  python3 calc/crystallographic_calculator.py --cyclotomic 30
  python3 calc/crystallographic_calculator.py --point-groups
  python3 calc/crystallographic_calculator.py --restriction --json
"""

import argparse
import json
import math
import sys
from fractions import Fraction
from collections import defaultdict


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def euler_totient(n):
    """Euler totient phi(n) via direct computation."""
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


def divisors(n):
    """All divisors of n in sorted order."""
    divs = []
    for i in range(1, int(n**0.5) + 1):
        if n % i == 0:
            divs.append(i)
            if i != n // i:
                divs.append(n // i)
    return sorted(divs)


def sigma(n, k=1):
    """Sum of k-th powers of divisors."""
    return sum(d**k for d in divisors(n))


def sigma_neg1(n):
    """Sum of reciprocals of divisors."""
    return Fraction(sum(Fraction(1, d) for d in divisors(n)))


def prime_factorization(n):
    """Return dict {prime: exponent}."""
    if n <= 1:
        return {}
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


# ---------------------------------------------------------------------------
# --restriction: Show n with phi(n) <= 2 (crystallographic restriction set)
# ---------------------------------------------------------------------------

def cmd_restriction(as_json=False):
    """Show all n where phi(n) <= 2, i.e., crystallographic rotations are allowed."""
    results = []
    for n in range(1, 101):
        phi_n = euler_totient(n)
        c = math.cos(2 * math.pi / n)
        two_c = 2 * c
        is_half_int = abs(two_c - round(two_c)) < 1e-10
        results.append({
            "n": n,
            "phi_n": phi_n,
            "cos_2pi_n": round(c, 10),
            "2cos": round(two_c, 6),
            "half_integer": is_half_int,
            "allowed": phi_n <= 2,
        })

    allowed = [r for r in results if r["allowed"]]
    allowed_ns = [r["n"] for r in allowed]

    if as_json:
        print(json.dumps({"allowed_n": allowed_ns, "data": results}, indent=2))
        return

    print("Crystallographic Restriction: n where phi(n) <= 2")
    print("=" * 66)
    print()
    print(f"{'n':>4}  {'phi(n)':>6}  {'cos(2pi/n)':>14}  {'2*cos':>10}  {'half-int?':>10}")
    print("-" * 56)

    for r in results:
        if r["allowed"] or r["n"] <= 10:
            marker = " <<<" if r["allowed"] else ""
            hi = "YES" if r["half_integer"] else "no"
            print(f"{r['n']:>4}  {r['phi_n']:>6}  {r['cos_2pi_n']:>14.10f}  {r['2cos']:>10.6f}  {hi:>10}{marker}")

    print()
    print(f"Result: n with phi(n) <= 2: {allowed_ns}")
    print(f"These are exactly the allowed crystallographic rotation orders in 3D.")
    print()
    print("WHY: cos(2*pi/n) has minimal polynomial degree phi(n)/2 (n >= 3).")
    print("     For it to be rational (half-integer), need phi(n) <= 2.")


# ---------------------------------------------------------------------------
# --platonic: Platonic solid V, E, F table with n=6 connections
# ---------------------------------------------------------------------------

PLATONIC_SOLIDS = [
    ("Tetrahedron",    4,  6,  4, 3, 3, "Tetrahedron"),
    ("Cube",           8, 12,  6, 4, 3, "Octahedron"),
    ("Octahedron",     6, 12,  8, 3, 4, "Cube"),
    ("Dodecahedron",  20, 30, 12, 5, 3, "Icosahedron"),
    ("Icosahedron",   12, 30, 20, 3, 5, "Dodecahedron"),
]


def cmd_platonic(as_json=False):
    """Platonic solid table with n=6 connections."""
    rows = []
    for name, v, e, f, p, q, dual in PLATONIC_SOLIDS:
        euler = v - e + f
        e_div6 = (e % 6 == 0)
        vef_has_6_or_12 = bool({v, e, f} & {6, 12})
        rows.append({
            "name": name, "V": v, "E": e, "F": f,
            "euler": euler, "schlafli": f"{{{p},{q}}}",
            "E_div_6": e_div6, "VEF_in_6_12": vef_has_6_or_12,
            "dual": dual,
        })

    if as_json:
        print(json.dumps(rows, indent=2))
        return

    print("Platonic Solids and n=6 Connections")
    print("=" * 72)
    print()
    s_neg1 = sigma_neg1(6)
    print(f"sigma_{{-1}}(6) = {s_neg1} = {float(s_neg1):.0f}  (Euler characteristic of S^2)")
    print()

    print(f"{'Solid':>14}  {'V':>3}  {'E':>3}  {'F':>3}  {'V-E+F':>5}  {'6|E':>4}  {'VEF in {{6,12}}':>14}  {{p,q}}")
    print("-" * 72)
    for r in rows:
        print(f"{r['name']:>14}  {r['V']:>3}  {r['E']:>3}  {r['F']:>3}  {r['euler']:>5}  "
              f"{'yes' if r['E_div_6'] else 'no':>4}  "
              f"{'yes' if r['VEF_in_6_12'] else 'no':>14}  {r['schlafli']}")

    print()
    print("Key observations:")
    print("  - ALL edge counts are multiples of 6 (6, 12, 12, 30, 30)")
    print("  - Euler formula V-E+F = 2 = sigma_{-1}(6) for all")
    print("  - Every solid has at least one of V, E, F in {6, 12}")
    print()
    print("Dual pairs (shared edge count, V<->F swap):")
    for r in rows:
        if r["name"] <= r["dual"]:
            print(f"  {r['name']:>14} <-> {r['dual']}")


# ---------------------------------------------------------------------------
# --kissing: Kissing numbers d=1..8 with arithmetic function mapping
# ---------------------------------------------------------------------------

KISSING_NUMBERS = {
    1: 2,
    2: 6,
    3: 12,
    4: 24,
    5: 40,
    6: 72,
    7: 126,
    8: 240,
}


def cmd_kissing(as_json=False):
    """Kissing numbers d=1..8 with n=6 arithmetic function decomposition."""
    phi6 = euler_totient(6)
    s6 = sigma(6)
    s_neg1_6 = sigma_neg1(6)

    rows = []
    for d in range(1, 9):
        k = KISSING_NUMBERS[d]
        decomp = ""
        if d == 1:
            decomp = f"phi(6) = {phi6}"
        elif d == 2:
            decomp = "6 = n itself"
        elif d == 3:
            decomp = f"sigma(6) = {s6}"
        elif d == 4:
            decomp = f"sigma(6)*sigma_{{-1}}(6) = {s6}*{int(s_neg1_6)} = {s6 * int(s_neg1_6)}"
        elif d == 8:
            decomp = f"6!/3 = {math.factorial(6)//3}"
        else:
            if k % 6 == 0:
                decomp = f"6 * {k // 6}"
            else:
                decomp = f"(no clean 6-decomposition)"

        rows.append({
            "dimension": d,
            "kissing_number": k,
            "decomposition": decomp,
            "divisible_by_6": k % 6 == 0,
        })

    if as_json:
        print(json.dumps(rows, indent=2))
        return

    print("Kissing Numbers and n=6 Connections")
    print("=" * 66)
    print()
    print(f"n=6 constants: phi(6)={phi6}, sigma(6)={s6}, sigma_{{-1}}(6)={s_neg1_6}")
    print()
    print(f"{'dim':>4}  {'kissing':>8}  {'6|k':>4}  {'n=6 decomposition'}")
    print("-" * 60)
    for r in rows:
        print(f"{r['dimension']:>4}  {r['kissing_number']:>8}  "
              f"{'yes' if r['divisible_by_6'] else 'no':>4}  {r['decomposition']}")

    print()
    print("Summary:")
    print("  d=1: kiss(1) =  2  = phi(6)")
    print("  d=2: kiss(2) =  6  = the number itself")
    print("  d=3: kiss(3) = 12  = sigma(6)")
    print("  d=4: kiss(4) = 24  = sigma(6) * sigma_{-1}(6)")
    print("  d=8: kiss(8) = 240 = 6!/3")


# ---------------------------------------------------------------------------
# --cyclotomic N: Compute cyclotomic polynomial degree for n=1..N
# ---------------------------------------------------------------------------

def cmd_cyclotomic(N, as_json=False):
    """Compute cyclotomic polynomial degree (= phi(n)) for n=1..N."""
    rows = []
    deg_le2 = []

    for n in range(1, N + 1):
        phi_n = euler_totient(n)
        rows.append({
            "n": n,
            "phi_n": phi_n,
            "deg_le_2": phi_n <= 2,
        })
        if phi_n <= 2:
            deg_le2.append(n)

    if as_json:
        print(json.dumps({"deg_le_2": deg_le2, "data": rows}, indent=2))
        return

    print(f"Cyclotomic Polynomial Degree (= phi(n)) for n=1..{N}")
    print("=" * 50)
    print()
    print(f"{'n':>4}  {'phi(n)':>6}  {'deg<=2':>6}")
    print("-" * 22)
    for r in rows:
        marker = " <<<" if r["deg_le_2"] else ""
        print(f"{r['n']:>4}  {r['phi_n']:>6}  {'YES' if r['deg_le_2'] else '':>6}{marker}")

    print()
    print(f"n with deg(Phi_n) <= 2: {deg_le2}")
    print("These are exactly {1, 2, 3, 4, 6} -- the crystallographic set.")


# ---------------------------------------------------------------------------
# --point-groups: 32 crystallographic point groups
# ---------------------------------------------------------------------------

POINT_GROUPS = [
    # (Schoenflies, Hermann-Mauguin, order, crystal_system, has_C6_subgroup)
    ("C1",  "1",      1,  "Triclinic",    False),
    ("Ci",  "-1",     2,  "Triclinic",    False),
    ("C2",  "2",      2,  "Monoclinic",   False),
    ("Cs",  "m",      2,  "Monoclinic",   False),
    ("C2h", "2/m",    4,  "Monoclinic",   False),
    ("D2",  "222",    4,  "Orthorhombic", False),
    ("C2v", "mm2",    4,  "Orthorhombic", False),
    ("D2h", "mmm",    8,  "Orthorhombic", False),
    ("C4",  "4",      4,  "Tetragonal",   False),
    ("S4",  "-4",     4,  "Tetragonal",   False),
    ("C4h", "4/m",    8,  "Tetragonal",   False),
    ("D4",  "422",    8,  "Tetragonal",   False),
    ("C4v", "4mm",    8,  "Tetragonal",   False),
    ("D2d", "-42m",   8,  "Tetragonal",   False),
    ("D4h", "4/mmm", 16,  "Tetragonal",   False),
    ("C3",  "3",      3,  "Trigonal",     False),
    ("S6",  "-3",     6,  "Trigonal",     True),
    ("D3",  "32",     6,  "Trigonal",     False),
    ("C3v", "3m",     6,  "Trigonal",     False),
    ("D3d", "-3m",   12,  "Trigonal",     False),
    ("C6",  "6",      6,  "Hexagonal",    True),
    ("C3h", "-6",     6,  "Hexagonal",    False),
    ("C6h", "6/m",   12,  "Hexagonal",    True),
    ("D6",  "622",   12,  "Hexagonal",    True),
    ("C6v", "6mm",   12,  "Hexagonal",    True),
    ("D3h", "-6m2",  12,  "Hexagonal",    False),
    ("D6h", "6/mmm", 24,  "Hexagonal",    True),
    ("T",   "23",    12,  "Cubic",        False),
    ("Th",  "m-3",   24,  "Cubic",        False),
    ("O",   "432",   24,  "Cubic",        False),
    ("Td",  "-43m",  24,  "Cubic",        False),
    ("Oh",  "m-3m",  48,  "Cubic",        False),
]


def cmd_point_groups(as_json=False):
    """List all 32 crystallographic point groups with C6 subgroup check."""
    rows = []
    system_counts = defaultdict(int)
    for sch, hm, order, system, has_c6 in POINT_GROUPS:
        system_counts[system] += 1
        rows.append({
            "schoenflies": sch, "hermann_mauguin": hm,
            "order": order, "system": system,
            "order_div_6": order % 6 == 0, "has_C6": has_c6,
        })

    if as_json:
        print(json.dumps({
            "total": len(rows),
            "groups": rows,
            "system_counts": dict(system_counts),
        }, indent=2))
        return

    print("32 Crystallographic Point Groups (3D)")
    print("=" * 62)
    print()
    print(f"{'#':>2} {'Schoenflies':>11} {'H-M':>7} {'Order':>6} {'System':>14} {'6|ord':>5} {'C6?':>4}")
    print("-" * 58)

    for i, r in enumerate(rows, 1):
        print(f"{i:>2} {r['schoenflies']:>11} {r['hermann_mauguin']:>7} {r['order']:>6} "
              f"{r['system']:>14} {'yes' if r['order_div_6'] else '':>5} "
              f"{'yes' if r['has_C6'] else '':>4}")

    print()
    print("Crystal system distribution:")
    for sys_name in ["Triclinic", "Monoclinic", "Orthorhombic", "Tetragonal",
                      "Trigonal", "Hexagonal", "Cubic"]:
        count = system_counts[sys_name]
        bar = "#" * count
        print(f"  {sys_name:>14}: {count:>2}  {bar}")

    hex_trig = system_counts["Hexagonal"] + system_counts["Trigonal"]
    print()
    print(f"Hexagonal + Trigonal = {hex_trig} = sigma(6) = 12")
    c6_count = sum(1 for r in rows if r["has_C6"])
    div6_count = sum(1 for r in rows if r["order_div_6"])
    print(f"Groups with order divisible by 6: {div6_count}")
    print(f"Groups containing C6 as subgroup:  {c6_count}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Crystallographic Calculator -- restriction theorem, Platonic solids, kissing numbers, point groups"
    )
    parser.add_argument("--restriction", action="store_true",
                        help="Show n with phi(n)<=2 (crystallographic restriction set)")
    parser.add_argument("--platonic", action="store_true",
                        help="Platonic solid V,E,F table with n=6 connections")
    parser.add_argument("--kissing", action="store_true",
                        help="Kissing numbers d=1..8 with arithmetic function mapping")
    parser.add_argument("--cyclotomic", type=int, metavar="N",
                        help="Compute cyclotomic polynomial degree for n=1..N")
    parser.add_argument("--point-groups", action="store_true",
                        help="32 crystallographic point groups, orders, C6 subgroup check")
    parser.add_argument("--json", action="store_true",
                        help="Output in JSON format")

    args = parser.parse_args()

    ran_any = False

    if args.restriction:
        cmd_restriction(as_json=args.json)
        ran_any = True
    if args.platonic:
        if ran_any:
            print()
        cmd_platonic(as_json=args.json)
        ran_any = True
    if args.kissing:
        if ran_any:
            print()
        cmd_kissing(as_json=args.json)
        ran_any = True
    if args.cyclotomic is not None:
        if ran_any:
            print()
        cmd_cyclotomic(args.cyclotomic, as_json=args.json)
        ran_any = True
    if args.point_groups:
        if ran_any:
            print()
        cmd_point_groups(as_json=args.json)
        ran_any = True

    if not ran_any:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
