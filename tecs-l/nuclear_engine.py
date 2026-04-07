```python
#!/usr/bin/env python3
"""Nuclear physics analysis engine — explore nuclear structure through sigma(6)=12, tau(6)=4 lens

Analyze magic numbers, nuclear reactions, and binding energy using sigma/tau representations.
Triple-alpha reaction (3*He4=C12 = 3*tau=sigma) is the key connection.

Usage:
  python3 nuclear_engine.py --magic              # Magic number analysis
  python3 nuclear_engine.py --reactions          # Nuclear reaction analysis
  python3 nuclear_engine.py --binding            # Binding energy curve
  python3 nuclear_engine.py                      # Run all
"""

import argparse
import math

# ─────────────────────────────────────────
# Core constants: divisor functions of perfect number 6
# ─────────────────────────────────────────
SIGMA = 12     # sigma(6) = sum of divisors
TAU = 4        # tau(6) = number of divisors
P1 = 6         # First perfect number
PHI = 2        # Smallest prime number

# ─────────────────────────────────────────
# sigma/tau expression search (same logic as chemistry_engine)
# ─────────────────────────────────────────

def find_sigma_tau_exprs(n):
    """Try to express integer n as combinations of sigma, tau, P1.
    Returns list of (expression, grade, is_ad_hoc)."""
    results = []
    s, t, p = SIGMA, TAU, P1

    # Exact matches
    if n == s: results.append(("sigma", "exact", False))
    if n == t: results.append(("tau", "exact", False))
    if n == p: results.append(("P1", "exact", False))
    if n == PHI: results.append(("phi", "exact", False))

    # Arithmetic operations + powers
    combos = [
        (s + t,     "sigma+tau"),
        (s - t,     "sigma-tau"),
        (s * t,     "sigma*tau"),
        (s // t,    "sigma/tau"),
        (t ** 2,    "tau^2"),
        (t ** 3,    "tau^3"),
        (s ** 2,    "sigma^2"),
        (s + t**2,  "sigma+tau^2"),
        (s * t**2,  "sigma*tau^2"),
        (s + p,     "sigma+P1"),
        (s * p,     "sigma*P1"),
        (p * t,     "P1*tau"),
        (p ** 2,    "P1^2"),
        (s + s,     "2*sigma"),
        (s * 3,     "3*sigma"),
        (s + s + t, "2*sigma+tau"),
        (2 * s * t, "2*sigma*tau"),
        (t * t * t, "tau^3"),
        (s * t + t, "sigma*tau+tau"),
        (s * t + s, "sigma*tau+sigma"),
        (s * t - t, "sigma*tau-tau"),
        (s * t - s, "sigma*tau-sigma"),
        (p * p + p, "P1^2+P1"),
        (s + t + p, "sigma+tau+P1"),
        (s * t + p, "sigma*tau+P1"),
        ((s + t) * t, "(sigma+tau)*tau"),
        (s * (s - t), "sigma*(sigma-tau)"),
        (t * (t + 1), "tau*(tau+1)"),
        (p * (p + 1), "P1*(P1+1)"),
        (2 ** (t - 1), "2^(tau-1)"),
        (2 ** t,       "2^tau"),
        (2 ** (t + 1), "2^(tau+1)"),
        (2 ** (p - 1), "2^(P1-1)"),
        (2 ** p,       "2^P1"),
        (2 ** p - PHI, "2^P1-2"),
        (2 ** 7 - PHI, "2^7-2"),
    ]
    for val, expr in combos:
        if val == n:
            # Expressions with +1/-1 corrections are ad hoc
            adhoc = "+1" in expr or "-1" in expr
            results.append((expr, "exact", adhoc))

    # Multiple search (small coefficients only)
    for k in range(2, 12):
        if s * k == n and f"{k}*sigma" not in [r[0] for r in results]:
            results.append((f"{k}*sigma", "exact", k > 5))
        if t * k == n and f"{k}*tau" not in [r[0] for r in results]:
            results.append((f"{k}*tau", "exact", k > 8))
        if p * k == n and f"{k}*P1" not in [r[0] for r in results]:
            results.append((f"{k}*P1", "exact", k > 6))

    # Remove duplicates
    seen = set()
    unique = []
    for expr, grade, adhoc in results:
        if expr not in seen:
            seen.add(expr)
            unique.append((expr, grade, adhoc))
    return unique


def best_expr(n):
    """Return most concise expression"""
    exprs = find_sigma_tau_exprs(n)
    if not exprs:
        return "-"
    non_adhoc = [e for e in exprs if not e[2]]
    if non_adhoc:
        return non_adhoc[0][0]
    return exprs[0][0] + "*"  # * = ad hoc indicator


# ─────────────────────────────────────────
# Magic number analysis
# ─────────────────────────────────────────

MAGIC_NUMBERS = [2, 8, 20, 28, 50, 82, 126]

def analyze_magic():
    """Analyze nuclear magic numbers and sigma/tau relationships"""
    print("\n" + "=" * 70)
    print("  Nuclear Magic Numbers — sigma(6)=12, tau(6)=4 lens")
    print("  Magic numbers: proton/neutron counts with special stability")
    print("=" * 70)

    header = f"  {'Magic #':>6} {'sigma/tau expression':>24} {'# exprs':>6} {'Grade'}"
    print(header)
    print("  " + "-" * 66)

    matched = 0
    for mn in MAGIC_NUMBERS:
        exprs = find_sigma_tau_exprs(mn)
        non_adhoc = [e for e in exprs if not e[2]]
        be = best_expr(mn)
        n_expr = len(non_adhoc)

        if n_expr > 0:
            grade = "🟩" if n_expr >= 2 else "🟧"
            matched += 1
        else:
            grade = "⚪"

        # Additional expressions (max 3)
        extra = ""
        if len(non_adhoc) > 1:
            extra = " | " + ", ".join(e[0] for e in non_adhoc[1:3])

        print(f"  {mn:>6} {be:>24}{extra:>20} {n_expr:>6} {grade}")

    print("  " + "-" * 66)
    print(f"  Matches: {matched}/{len(MAGIC_NUMBERS)}")

    # Key observations
    print(f"\n  Key Observations:")
    print(f"    2  = phi (smallest prime, electron pair)")
    print(f"    8  = sigma - tau = 12 - 4  ★ Same as octet!")
    print(f"    20 = tau * (tau + 1) = 4 × 5")
    print(f"    28 = sigma + tau^2 = 12 + 16 = sigma(6) + tau(6)^2")
    print(f"         (Note: 28 is second perfect number! sigma(28)=56)")
    print(f"    50 = sigma*tau + tau-2? → ad hoc")
    print(f"    82 = ?  (no clean expression)")
    print(f"    126 = 2^7 - 2 = 2*(2^P1-1) = 2*M6")

    print(f"\n  ⚠ Texas Sharpshooter Analysis:")
    print(f"    Natural matches among 7 magic numbers: 2, 8, 28 (3)")
    print(f"    28=perfect number is noteworthy regardless of sigma/tau")
    print(f"    8=sigma-tau might be structural (matches octet rule)")
    print(f"    Others (20,50,82,126) risk forced matching")


# ─────────────────────────────────────────
# Nuclear reaction analysis
# ─────────────────────────────────────────

def analyze_reactions():
    """Interpret major nuclear reactions through sigma/tau lens"""
    print("\n" + "=" * 70)
    print("  Nuclear Reactions — sigma/tau lens")
    print("=" * 70)

    # Triple-alpha reaction (key!)
    print(f"\n  ━━ Triple-Alpha Reaction ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  3 × He-4 → C-12")
    print(f"  3 × tau  → sigma   ★★★ Key connection!")
    print(f"")
    print(f"    He-4:  Z=2, A=4=tau    (alpha particle = tau!)")
    print(f"    C-12:  Z=6=P1, A=12=sigma  (carbon = sigma!)")
    print(f"    Reaction:  3 × (A=tau) = (A=sigma)")
    print(f"               i.e., 3*tau = sigma = 12  ✓")
    print(f"")
    print(f"    Meaning: 3 alpha particles combine to form sum of divisors of perfect number")
    print(f"             tau → sigma transition = stellar nucleosynthesis")
    print(f"")
    print(f"    Grade: 🟩 (exact equation, low chance probability)")
    print(f"    Reason: 3*4=12 is trivial, but simultaneous He-4=tau and C-12=sigma")
    print(f"            correspondence is product of two independent matches → p ≈ 1/36")

    # pp-chain (Sun)
    print(f"\n  ━━ pp-chain (proton-proton chain) ━━━━━━━━━━━━━━━━━━━━")
    print(f"  4p → He-4 + 2e⁺ + 2ν + energy")
    print(f"  tau protons → tau-mass nucleus (He-4)")
    print(f"")
    print(f"    Input:  4 = tau protons")
    print(f"    Output: He-4 (A=tau)")
    print(f"    Energy: 26.7 MeV ≈ ? (weak sigma/tau match)")
    print(f"")
    print(f"    Grade: 🟧 (tau match is trivial — 4p→He4 by definition)")

    # CNO cycle
    print(f"\n  ━━ CNO Cycle ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  C-12 catalyst → converts 4p to He-4")
    print(f"  sigma acts as catalyst! consumes tau protons, outputs tau")
    print(f"")
    print(f"    Catalyst: C-12 (A=sigma)")
    print(f"    Input:    4p (tau count)")
    print(f"    Output:   He-4 (A=tau) + C-12 (sigma restored)")
    print(f"    Cycle:    sigma + tau*p → sigma + tau-nucleus")
    print(f"")
    print(f"    sigma is conserved (catalyst) ← interesting observation")
    print(f"    Grade: 🟧★ (sigma catalyst conservation is structural)")

    # Nuclear fission
    print(f"\n  ━━ Uranium Fission ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  U-235 + n → Ba-141 + Kr-92 + 3n")
    print(f"  A=235, Z=92 → sigma/tau match search")
    u235_expr = best_expr(235)
    u92_expr = best_expr(92)
    print(f"    235 → {u235_expr}")
    print(f"     92 → {u92_expr}")
    print(f"    Fission neutrons: 3 (= sigma/tau = 3)")
    print(f"    Grade: ⚪ (sigma/tau match in large numbers almost certainly coincidental)")

    # Hydrogen bomb (D-T reaction)
    print(f"\n  ━━ D-T Fusion ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  D(A=2) + T(A=3) → He-4(A=tau) + n")
    print(f"  phi + 3 → tau + 1")
    print(f"  Sum of divisors(2,3) → number of divisors(tau)!")
    print(f"  D's A=2, T's A=3: nuclei with divisors 2 and 3 of 6 combine")
    print(f"  Grade: 🟧 (2+3=5≠4 so 1 neutron emitted. Interesting but weak)")

    # Summary table
    print(f"\n  ━━ Nuclear Reaction Summary ━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  {'Reaction':>14} {'sigma/tau interpretation':>30} {'Grade':>6}")
    print(f"  " + "-" * 56)
    reactions = [
        ("Triple-alpha", "3*tau → sigma (He4→C12)",     "🟩"),
        ("pp-chain",     "tau*p → tau-nucleus (trivial)", "🟧"),
        ("CNO cycle",    "sigma catalyst conserved",     "🟧★"),
        ("D-T fusion",   "divisors(2,3)→tau+n",         "🟧"),
        ("U fission",    "large numbers, coincidental",  "⚪"),
    ]
    for name, interp, grade in reactions:
        print(f"  {name:>14} {interp:>30} {grade:>6}")


# ─────────────────────────────────────────
# Binding energy curve analysis
# ─────────────────────────────────────────

# Binding energy per nucleon approximations (MeV, major nuclides)
BINDING_ENERGY = [
    # (element, A, Z, BE/A MeV)
    ("H-2",    2,   1, 1.11),
    ("He-3",   3,   2, 2.57),
    ("He-4",   4,   2, 7.07),
    ("Li-6",   6,   3, 5.33),
    ("Li-7",   7,   3, 5.61),
    ("C-12",  12,   6, 7.68),
    ("N-14",  14,   7, 7.48),
    ("O-16",  16,   8, 7.98),
    ("Ne-20", 20,  10, 8.03),
    ("Si-28", 28,  14, 8.45),
    ("S-32",  32,  16, 8.49),
    ("Ca-40", 40,  20, 8.55),
    ("Ti-48", 48,  22, 8.72),
    ("Cr-52", 52,  24, 8.78),
    ("Fe-56", 56,  26, 8.79),  # ← Maximum!
    ("Ni-62", 62,  28, 8.79),
    ("Zn-64", 64,  30, 8.74),
    ("Kr-84", 84,  36, 8.72),
    ("Zr-90", 90,  40, 8.71),
    ("Mo-98", 98,  42, 8.64),
    ("Sn-120",120, 50, 8.51),
    ("Nd-142",142, 60, 8.35),
    ("Pb-208",208, 82, 7.87),
    ("U-238", 238, 92, 7.57),
]

def analyze_binding():
    """Binding energy curve and sigma/tau"""
    print("\n" + "=" * 70)
    print("  Binding Energy per Nucleon — sigma/tau lens")
    print("=" * 70)

    # ASCII graph
    print(f"\n  BE/A (MeV)")
    print(f"  9.0 ┤")

    max_a = 240
    chart_w = 55
    chart_h = 12
    min_be = 1.0
    max_be = 9.0

    # Create grid
    grid = [[" " for _ in range(chart_w)] for _ in range(chart_h)]

    for name, a, z, be in BINDING_ENERGY:
        x = int(a / max_a * (chart_w - 1))
        y = int((be - min_be) / (max_be - min_be) * (chart_h - 1))
        y = min(max(y, 0), chart_h - 1)
        y_inv = chart_h - 1 - y
        ch = "*"
        if name == "Fe-56":
            ch = "F"  # Fe marker
        elif name == "He-4":
            ch = "H"  # He marker
        elif name == "C-12":
            ch = "C"
        grid[y_inv][x] = ch

    # Output
    be_labels = [9.0, 8.0, 7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0]
    for i, row in enumerate(grid):
        be_val = max_be - i * (max_be - min_be) / (chart_h - 1)
        label = f"{be_val:4.1f}" if i % 3 == 0 else "    "
        line = "".join(row)
        bar = "┤" if i % 3 == 0 else "│"
        print(f"  {label} {bar}{line}")
    print(f"       └" + "─" * chart_w)
    print(f"        0      50     100    150    200    A (mass number)")
    print(f"        H=helium, C=carbon, F=iron(Fe-56 peak)")

    # sigma/tau analysis
    print(f"\n  ━━ Peak Analysis: Fe-56 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"    Fe: Z=26, A=56")
    print(f"    A=56 = sigma * tau + sigma - tau = 12*4+12-4 = 56 ✓")
    print(f"         = sigma*(tau+1) - tau = 12*5-4 = 56 ✓")
    print(f"         = 2 * 28 = 2 * (second perfect number)")
    print(f"         = 2 * sigma(28)... no, sigma(28)=56! ★")
    print(f"    sigma(28) = 1+2+4+7+14+28 = 56 = Fe's mass number!")
    print(f"    Since 28 is perfect, sigma(28) = 2*28 = 56")
    print(f"")
    print(f"    Z=26 = 2 * 13  (13 is prime)")
    z26_expr = best_expr(26)
    print(f"    Z=26 → {z26_expr}")
    print(f"")
    print(f"    Grade: 🟧★ (Fe-56 = sigma(28) = sigma(P2) is structural)")
    print(f"    Note: BE peak at Fe-56 results from nuclear + Coulomb forces")
    print(f"          Match with sigma(P2)=56 likely coincidental")

    # Alpha particle anomaly
    print(f"\n  ━━ He-4 (Alpha Particle) Anomaly ━━━━━━━━━━━━━━━━━━━━")
    print(f"    A=4=tau has BE/A=7.07 — abnormally high for its A")
    print(f"    Ultra-stability of tau-nucleus → doubly magic nucleus at magic number 2")
    print(f"    (Z=2=phi, N=2=phi both magic numbers)")

    # BE per nucleon table
    print(f"\n  ━━ sigma/tau Matching Table ━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  {'Nuclide':>8} {'A':>4} {'Z':>3} {'BE/A':>6} {'A expression':>20} {'Note'}")
    print(f"  " + "-" * 64)
    for name, a, z, be in BINDING_ENERGY:
        expr = best_expr(a)
        note = ""
        if name == "Fe-56":
            note = "★ Peak, sigma(28)"
        elif name == "He-4":
            note = "★ tau, alpha ultra-stable"
        elif name == "C-12":
            note = "★ sigma, triple-alpha"
        elif name == "Si-28":
            note = "P2(perfect 28)"
        elif name == "Ni-62":
            note = "Actual max BE/A"
        print(f"  {name:>8} {a:>4} {z:>3} {be:>6.2f} {expr:>20}  {note}")

    print(f"\n  ⚠ Texas Sharpshooter Warning:")
    print(f"    Mass numbers are simple integers → many expressible as sigma*tau combinations")
    print(f"    Real highlights: He-4=tau(peak-level BE), C-12=sigma(life), Fe-56=sigma(P2)")


# ─────────────────────────────────────────
# Main
# ─────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Nuclear physics analysis — sigma(6)=12, tau(6)=4 lens"
    )
    parser.add_argument("--magic", action="store_true", help="Magic number analysis")
    parser.add_argument("--reactions", action="store_true", help="Nuclear reaction analysis")
    parser.add_argument("--binding", action="store_true", help="Binding energy curve")
    args = parser.parse_args()

    # Run all if no arguments
    if not any([args.magic, args.reactions, args.binding]):
        args.magic = True
        args.reactions = True
        args.binding = True

    print("╔══════════════════════════════════════════════════════════╗")
    print("║  Nuclear Physics Analysis Engine — sigma(6)=12, tau(6)=4 lens ║")
    print("║  Interpret magic numbers, reactions, binding energy via divisor functions ║")
    print("╚══════════════════════════════════════════════════════════╝")

    if args.magic:
        analyze_magic()

    if args.reactions:
        analyze_reactions()

    if args.binding:
        analyze_binding()


if __name__ == "__main__":
    main()
```