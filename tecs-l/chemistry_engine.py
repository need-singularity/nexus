```python
#!/usr/bin/env python3
"""Chemistry Element Analysis Engine — Exploring element structures through sigma(6)=12, tau(6)=4 lens

Analyzing atomic numbers, mass numbers, electron shells, and chemical bonds through sigma/tau representation.
Special focus on life's essential elements (H,C,N,O,P,S).

Usage:
  python3 chemistry_engine.py --all              # All 36 elements
  python3 chemistry_engine.py --element C        # Carbon only
  python3 chemistry_engine.py --life             # Life's essential elements
  python3 chemistry_engine.py --bonds            # Chemical bond analysis
"""

import argparse
import math

# ─────────────────────────────────────────
# Core constants: Divisor functions of perfect number 6
# ─────────────────────────────────────────
SIGMA = 12     # sigma(6) = 1+2+3+6 = sum of divisors
TAU = 4        # tau(6)   = |{1,2,3,6}| = number of divisors
P1 = 6         # First perfect number
PHI = 2        # Smallest prime (basic unit of electron pair)
M3 = 7         # Mersenne prime M3 = 2^3-1

# ─────────────────────────────────────────
# Element database (Z=1~36, periods 1~4)
# (symbol, Z, mass number A, electron configuration abbreviated, group, period)
# ─────────────────────────────────────────
ELEMENTS = [
    ("H",   1,   1, "1s1",                          1,  1),
    ("He",  2,   4, "1s2",                         18,  1),
    ("Li",  3,   7, "[He]2s1",                      1,  2),
    ("Be",  4,   9, "[He]2s2",                      2,  2),
    ("B",   5,  11, "[He]2s2 2p1",                 13,  2),
    ("C",   6,  12, "[He]2s2 2p2",                 14,  2),
    ("N",   7,  14, "[He]2s2 2p3",                 15,  2),
    ("O",   8,  16, "[He]2s2 2p4",                 16,  2),
    ("F",   9,  19, "[He]2s2 2p5",                 17,  2),
    ("Ne", 10,  20, "[He]2s2 2p6",                 18,  2),
    ("Na", 11,  23, "[Ne]3s1",                      1,  3),
    ("Mg", 12,  24, "[Ne]3s2",                      2,  3),
    ("Al", 13,  27, "[Ne]3s2 3p1",                 13,  3),
    ("Si", 14,  28, "[Ne]3s2 3p2",                 14,  3),
    ("P",  15,  31, "[Ne]3s2 3p3",                 15,  3),
    ("S",  16,  32, "[Ne]3s2 3p4",                 16,  3),
    ("Cl", 17,  35, "[Ne]3s2 3p5",                 17,  3),
    ("Ar", 18,  40, "[Ne]3s2 3p6",                 18,  3),
    ("K",  19,  39, "[Ar]4s1",                      1,  4),
    ("Ca", 20,  40, "[Ar]4s2",                      2,  4),
    ("Sc", 21,  45, "[Ar]3d1 4s2",                  3,  4),
    ("Ti", 22,  48, "[Ar]3d2 4s2",                  4,  4),
    ("V",  23,  51, "[Ar]3d3 4s2",                  5,  4),
    ("Cr", 24,  52, "[Ar]3d5 4s1",                  6,  4),
    ("Mn", 25,  55, "[Ar]3d5 4s2",                  7,  4),
    ("Fe", 26,  56, "[Ar]3d6 4s2",                  8,  4),
    ("Co", 27,  59, "[Ar]3d7 4s2",                  9,  4),
    ("Ni", 28,  58, "[Ar]3d8 4s2",                 10,  4),
    ("Cu", 29,  63, "[Ar]3d10 4s1",                11,  4),
    ("Zn", 30,  65, "[Ar]3d10 4s2",                12,  4),
    ("Ga", 31,  69, "[Ar]3d10 4s2 4p1",            13,  4),
    ("Ge", 32,  72, "[Ar]3d10 4s2 4p2",            14,  4),
    ("As", 33,  75, "[Ar]3d10 4s2 4p3",            15,  4),
    ("Se", 34,  79, "[Ar]3d10 4s2 4p4",            16,  4),
    ("Br", 35,  80, "[Ar]3d10 4s2 4p5",            17,  4),
    ("Kr", 36,  84, "[Ar]3d10 4s2 4p6",            18,  4),
]

# Life's essential elements (CHNOPS)
LIFE_ELEMENTS = {"H", "C", "N", "O", "P", "S"}

# ─────────────────────────────────────────
# sigma/tau expression search
# ─────────────────────────────────────────

def find_sigma_tau_expr(n):
    """Attempt to express integer n as a combination of sigma(12), tau(4).
    Returns list of possible expressions. Texas sharpshooter warning: post-hoc fitting possible."""
    results = []
    s, t = SIGMA, TAU

    # Simple multiples/divisors
    if n == s:
        results.append(("sigma", "exact", False))
    if n == t:
        results.append(("tau", "exact", False))
    if n == P1:
        results.append(("P1(=6)", "exact", False))

    # sigma-based arithmetic operations
    for k in range(1, 20):
        if s * k == n:
            results.append((f"sigma*{k}", "exact", k > 4))
        if s + k == n:
            results.append((f"sigma+{k}", "exact" if k <= 2 else "ad hoc", k > 2))
        if s - k == n and n > 0:
            results.append((f"sigma-{k}", "exact" if k <= 2 else "ad hoc", k > 2))
        if t * k == n:
            results.append((f"tau*{k}", "exact", k > 6))
        if t + k == n:
            results.append((f"tau+{k}", "exact" if k <= 2 else "ad hoc", k > 2))
        if t - k == n and n > 0:
            results.append((f"tau-{k}", "exact" if k <= 2 else "ad hoc", k > 2))

    # sigma/tau mixed
    if s + t == n:
        results.append(("sigma+tau", "exact", False))
    if s - t == n:
        results.append(("sigma-tau", "exact", False))
    if s * t == n:
        results.append(("sigma*tau", "exact", False))
    if t > 0 and s // t == n and s % t == 0:
        results.append(("sigma/tau", "exact", False))
    if s ** 2 == n:
        results.append(("sigma^2", "exact", False))
    if t ** 2 == n:
        results.append(("tau^2", "exact", False))
    if t ** 3 == n:
        results.append(("tau^3", "exact", False))
    if s + t**2 == n:
        results.append(("sigma+tau^2", "exact", False))

    # Perfect number related
    if 2 * P1 == n:
        results.append(("2*P1", "exact", False))
    if P1 ** 2 == n:
        results.append(("P1^2", "exact", False))
    if P1 * t == n:
        results.append(("P1*tau", "exact", False))

    # Remove duplicates, prioritize most concise
    seen = set()
    unique = []
    for expr, grade, adhoc in results:
        if expr not in seen:
            seen.add(expr)
            unique.append((expr, grade, adhoc))
    return unique


def best_expr(n):
    """Return the best sigma/tau expression"""
    exprs = find_sigma_tau_expr(n)
    if not exprs:
        return "-", ""
    # exact > ad hoc, prefer non-ad hoc
    non_adhoc = [e for e in exprs if not e[2]]
    if non_adhoc:
        return non_adhoc[0][0], non_adhoc[0][1]
    return exprs[0][0], exprs[0][1] + " (ad hoc)"


# ─────────────────────────────────────────
# Electron shell analysis
# ─────────────────────────────────────────

def analyze_shells():
    """Electron orbital capacity and sigma/tau relationships"""
    print("\n" + "=" * 60)
    print("  Electron Shell Structure — sigma/tau lens")
    print("=" * 60)
    shells = [
        ("s", 2,  "phi(=2)", "Basic unit of electron pair"),
        ("p", 6,  "P1(=6)",  "First perfect number!"),
        ("d", 10, "sigma-phi(=10)", "d-orbital = sigma - basic pair"),
        ("f", 14, "2*M3(=14)", "f-orbital = 2 × Mersenne prime 7"),
    ]
    print(f"  {'orbital':>6} {'electrons':>6} {'sigma/tau expression':>20} {'interpretation'}")
    print("  " + "-" * 56)
    for name, count, expr, note in shells:
        print(f"  {name:>6} {count:>6} {expr:>20}   {note}")

    print(f"\n  ⚠ Texas sharpshooter warning: Only 2 out of 4 orbitals (s,p) have natural matches.")
    print(f"    d=10, f=14 may be post-hoc interpretations.")
    print(f"    p=6=perfect number may be structurally meaningful (p-value needed).")


# ─────────────────────────────────────────
# Chemical bond analysis
# ─────────────────────────────────────────

def analyze_bonds():
    """Chemical bond electron numbers and sigma/tau relationships"""
    print("\n" + "=" * 60)
    print("  Chemical Bonds — sigma/tau lens")
    print("=" * 60)
    bonds = [
        ("single bond", 2, "phi(=2)",     "1 electron pair"),
        ("double bond", 4, "tau(=4)",     "number of divisors = bonding electrons!"),
        ("triple bond", 6, "P1(=6)",      "perfect number = strongest covalent bond"),
        ("metallic bond", "n", "sigma/n",   "delocalized electron sea"),
    ]
    print(f"  {'bond':>10} {'electrons':>6} {'sigma/tau expression':>16} {'interpretation'}")
    print("  " + "-" * 56)
    for name, count, expr, note in bonds:
        print(f"  {name:>10} {str(count):>6} {expr:>16}   {note}")

    print(f"\n  Key observations:")
    print(f"    single(2) + double(4) = triple(6) = P1 ✓")
    print(f"    double(4) = tau(6) — number of divisors matches bonding electrons")
    print(f"    triple(6) = sigma(6)/2 = P1 — perfect number")
    print(f"\n  ⚠ Texas: 2,4,6 are small even numbers. High matching probability.")
    print(f"    single=phi, double=tau is more numerical coincidence than structural.")

    # Octet rule
    print(f"\n  Octet rule:")
    print(f"    8 = sigma - tau = 12 - 4")
    print(f"    Stable electron configuration = sum of divisors - number of divisors")
    print(f"    ⚠ This is an exact equality but causation is unclear")


# ─────────────────────────────────────────
# Element output
# ─────────────────────────────────────────

def print_element_table(elements, title="Element Analysis"):
    """Print element table"""
    print("\n" + "=" * 78)
    print(f"  {title} — sigma(6)=12, tau(6)=4 lens")
    print("=" * 78)
    header = f"  {'symbol':>4} {'Z':>3} {'A':>4}  {'Z expression':>16} {'A expression':>16} {'life':>4} {'memo'}"
    print(header)
    print("  " + "-" * 74)

    match_z = 0
    match_a = 0
    total = len(elements)

    for sym, z, a, config, group, period in elements:
        z_expr, z_grade = best_expr(z)
        a_expr, a_grade = best_expr(a)
        life = "★" if sym in LIFE_ELEMENTS else ""
        memo = ""
        if z_expr != "-":
            match_z += 1
        if a_expr != "-":
            match_a += 1
        # Special memos
        if sym == "C":
            memo = "A=sigma!"
        elif sym == "He":
            memo = "A=tau"
        elif sym == "O":
            memo = "A=tau^2"
        elif sym == "Fe":
            memo = "A=sigma+sigma*tau"
        elif sym == "Si":
            memo = "A=sigma+tau^2"

        print(f"  {sym:>4} {z:>3} {a:>4}  {z_expr:>16} {a_expr:>16} {life:>4}  {memo}")

    print("  " + "-" * 74)
    print(f"  Z matches: {match_z}/{total} ({100*match_z/total:.0f}%)")
    print(f"  A matches: {match_a}/{total} ({100*match_a/total:.0f}%)")
    print(f"\n  ⚠ Texas sharpshooter warning:")
    print(f"    sigma=12, tau=4 with arithmetic operations can generate many integers.")
    print(f"    High matching rate doesn't imply structural relationship.")
    print(f"    Real significance: Only C(Z=6=P1, A=12=sigma), He(A=4=tau) are noteworthy.")


def print_life_analysis():
    """Deep analysis of life's essential elements"""
    life = [e for e in ELEMENTS if e[0] in LIFE_ELEMENTS]
    print("\n" + "=" * 78)
    print("  Life's Essential Elements (CHNOPS) — sigma/tau deep analysis")
    print("=" * 78)

    for sym, z, a, config, group, period in life:
        exprs_z = find_sigma_tau_expr(z)
        exprs_a = find_sigma_tau_expr(a)
        print(f"\n  ── {sym} (Z={z}, A={a}) ──")
        print(f"     Electron configuration: {config}")
        print(f"     Z expressions: {', '.join(e[0] for e in exprs_z[:5]) if exprs_z else 'none'}")
        print(f"     A expressions: {', '.join(e[0] for e in exprs_a[:5]) if exprs_a else 'none'}")

    # Summary statistics
    print(f"\n  ── Life elements summary ──")
    print(f"  H:  Z=1(unit element), A=1     — simplest, most abundant in universe")
    print(f"  C:  Z=6=P1, A=12=sigma   — perfect number & sigma! ★ key")
    print(f"  N:  Z=7=M3, A=14=2*M3    — Mersenne prime")
    print(f"  O:  Z=8=sigma-tau, A=16=tau^2  — octet=sigma-tau")
    print(f"  P:  Z=15=sigma+tau-1, A=31     — Mersenne number 2^5-1")
    print(f"  S:  Z=16=tau^2, A=32=sigma+sigma+8")
    print(f"\n  Carbon uniqueness: simultaneously satisfies Z=P1(perfect number), A=sigma(sum of divisors)!")
    print(f"  Is this why carbon is life's backbone? (hypothesis, verification needed)")


# ─────────────────────────────────────────
# Main
# ─────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Chemical Element Analysis — sigma(6)=12, tau(6)=4 lens"
    )
    parser.add_argument("--element", type=str, help="Single element symbol (e.g., C, Fe)")
    parser.add_argument("--life", action="store_true", help="Life's essential elements (CHNOPS) analysis")
    parser.add_argument("--all", action="store_true", help="All 36 elements table")
    parser.add_argument("--bonds", action="store_true", help="Chemical bonds + electron shell analysis")
    args = parser.parse_args()

    # If no arguments, run everything
    if not any([args.element, args.life, args.all, args.bonds]):
        args.all = True
        args.life = True
        args.bonds = True

    print("╔══════════════════════════════════════════════════════════╗")
    print("║  Chemistry Element Analysis Engine — sigma(6)=12, tau(6)=4 lens ║")
    print("║  sigma = sum of divisors, tau = number of divisors, P1 = perfect number 6   ║")
    print("╚══════════════════════════════════════════════════════════╝")

    if args.element:
        found = [e for e in ELEMENTS if e[0].upper() == args.element.upper()]
        if found:
            print_element_table(found, f"{args.element} element analysis")
        else:
            print(f"  ✗ Element '{args.element}' not found (Z=1~36 range)")

    if args.all:
        print_element_table(ELEMENTS, "All 36 elements")

    if args.life:
        print_life_analysis()

    if args.bonds:
        analyze_bonds()
        analyze_shells()


if __name__ == "__main__":
    main()
```