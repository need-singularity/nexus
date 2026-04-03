#!/usr/bin/env python3
"""ISCO Calculator -- Innermost Stable Circular Orbit in General Relativity.

Reusable calc/ tool derived from verify/verify_isco_extreme.py.

Usage:
  python3 calc/isco_calculator.py --schwarzschild
  python3 calc/isco_calculator.py --kerr 0.9
  python3 calc/isco_calculator.py --kerr-sweep
  python3 calc/isco_calculator.py --energy
  python3 calc/isco_calculator.py --stability 5.5
  python3 calc/isco_calculator.py --schwarzschild --json
"""

import argparse
import json
import math
import sys


# ---------------------------------------------------------------------------
# Core GR functions (G = c = M = 1 unless stated otherwise)
# ---------------------------------------------------------------------------

def schwarzschild_veff(r, L2, M=1.0):
    """Schwarzschild effective potential per unit mass."""
    return -M / r + L2 / (2.0 * r**2) - M * L2 / r**3


def schwarzschild_dvdr(r, L2, M=1.0):
    """dV_eff/dr for Schwarzschild."""
    return M / r**2 - L2 / r**3 + 3.0 * M * L2 / r**4


def schwarzschild_d2vdr2(r, L2, M=1.0):
    """d^2 V_eff/dr^2 for Schwarzschild."""
    return -2.0 * M / r**3 + 3.0 * L2 / r**4 - 12.0 * M * L2 / r**5


def circular_orbit_L2(r, M=1.0):
    """L^2 for circular orbit at radius r in Schwarzschild."""
    if r <= 3.0 * M:
        return None  # no circular orbit inside photon sphere
    return M * r**2 / (r - 3.0 * M)


def circular_orbit_energy(r, M=1.0):
    """Specific energy E/mc^2 at circular orbit radius r."""
    if r <= 3.0 * M:
        return None
    return (1.0 - 2.0 * M / r) / math.sqrt(1.0 - 3.0 * M / r)


def kerr_isco(a_over_M, M=1.0):
    """Compute Kerr ISCO radius (prograde and retrograde) via Bardeen-Press-Teukolsky.

    Parameters:
        a_over_M: spin parameter a/M in [0, 1)
    Returns:
        (r_prograde, r_retrograde) in units of M
    """
    a = abs(a_over_M)
    Z1 = 1.0 + (1.0 - a**2)**(1.0 / 3.0) * (
        (1.0 + a)**(1.0 / 3.0) + (1.0 - a)**(1.0 / 3.0)
    )
    Z2 = math.sqrt(3.0 * a**2 + Z1**2)
    r_pro = M * (3.0 + Z2 - math.sqrt((3.0 - Z1) * (3.0 + Z1 + 2.0 * Z2)))
    r_ret = M * (3.0 + Z2 + math.sqrt((3.0 - Z1) * (3.0 + Z1 + 2.0 * Z2)))
    return r_pro, r_ret


# ---------------------------------------------------------------------------
# --schwarzschild: Exact ISCO derivation
# ---------------------------------------------------------------------------

def cmd_schwarzschild(as_json=False):
    """Exact Schwarzschild ISCO derivation and verification."""
    M = 1.0
    r_isco = 6.0 * M
    L2_isco = 12.0 * M**2
    E_isco = (1.0 - 2.0 * M / r_isco) / math.sqrt(1.0 - 3.0 * M / r_isco)
    E2_isco = E_isco**2
    binding = 1.0 - E_isco

    dv = schwarzschild_dvdr(r_isco, L2_isco, M)
    d2v = schwarzschild_d2vdr2(r_isco, L2_isco, M)

    result = {
        "r_ISCO_M": 6.0,
        "L2_ISCO_M2": 12.0,
        "E_ISCO": round(E_isco, 10),
        "E2_ISCO": round(E2_isco, 10),
        "E2_exact": "8/9",
        "binding_fraction": round(binding, 10),
        "binding_percent": round(binding * 100, 4),
        "dV_dr_at_ISCO": round(dv, 2),
        "d2V_dr2_at_ISCO": round(d2v, 2),
    }

    if as_json:
        print(json.dumps(result, indent=2))
        return

    print("Schwarzschild ISCO -- Exact Derivation")
    print("=" * 60)
    print()
    print("Effective potential (per unit mass, G=c=1):")
    print("  V_eff(r) = -M/r + L^2/(2r^2) - M*L^2/r^3")
    print()
    print("Conditions for ISCO:")
    print("  dV/dr = 0    (circular orbit)")
    print("  d2V/dr2 = 0  (marginal stability)")
    print()
    print("Derivation:")
    print("  From dV/dr = 0:  L^2_circ = M*r^2 / (r - 3M)")
    print("  Substituting into d2V/dr2 = 0:")
    print("    -2(r-3M) + 3r - 12M = 0")
    print("    r - 6M = 0")
    print("    r = 6M  [EXACT]")
    print()
    print("Results (M=1):")
    print(f"  r_ISCO     = {result['r_ISCO_M']}M")
    print(f"  L^2_ISCO   = {result['L2_ISCO_M2']}M^2")
    print(f"  E_ISCO/mc^2 = 2*sqrt(2)/3 = {result['E_ISCO']}")
    print(f"  E^2_ISCO    = 8/9 = {result['E2_ISCO']}")
    print(f"  Binding     = {result['binding_percent']:.4f}% of rest mass")
    print()
    print("Verification:")
    print(f"  dV/dr(6M)   = {dv:.2e}  (should be 0)")
    print(f"  d2V/dr2(6M) = {d2v:.2e}  (should be 0)")
    print()
    print("The (6, 12) pair:")
    print("  6 is a perfect number: 6 = 1+2+3")
    print("  sigma(6) = 1+2+3+6 = 12")
    print("  r_ISCO = 6M, L^2_ISCO = sigma(6)*M^2 = 12M^2")
    print("  E^2 = 8/9 = 2^3/3^2 (only prime factors of 6)")


# ---------------------------------------------------------------------------
# --kerr SPIN: Compute ISCO for given spin
# ---------------------------------------------------------------------------

def cmd_kerr(spin, as_json=False):
    """Compute Kerr ISCO for given spin parameter a/M."""
    r_pro, r_ret = kerr_isco(spin)
    result = {
        "a_over_M": spin,
        "r_prograde_M": round(r_pro, 6),
        "r_retrograde_M": round(r_ret, 6),
    }

    if as_json:
        print(json.dumps(result, indent=2))
        return

    print(f"Kerr ISCO for a/M = {spin}")
    print("=" * 40)
    print(f"  Prograde:   r = {result['r_prograde_M']:.6f} M")
    print(f"  Retrograde: r = {result['r_retrograde_M']:.6f} M")
    if spin == 0:
        print("  (Schwarzschild limit: both = 6M)")


# ---------------------------------------------------------------------------
# --kerr-sweep: Sweep a/M from 0 to 0.999
# ---------------------------------------------------------------------------

def cmd_kerr_sweep(as_json=False):
    """Sweep a/M from 0 to 0.999 with ASCII plot."""
    N = 200
    spins = [i * 0.999 / (N - 1) for i in range(N)]
    data = []
    for a in spins:
        rp, rr = kerr_isco(a)
        data.append({"a_over_M": round(a, 6), "r_pro": round(rp, 6), "r_retro": round(rr, 6)})

    if as_json:
        print(json.dumps(data, indent=2))
        return

    print("Kerr ISCO Sweep: a/M = 0 to 0.999")
    print("=" * 66)

    # Table at key spins
    key_spins = [0.0, 0.1, 0.2, 0.3, 0.5, 0.7, 0.9, 0.95, 0.99, 0.999]
    print()
    print(f"  | {'a/M':>5} | {'r_ISCO(pro)/M':>14} | {'r_ISCO(retro)/M':>16} |")
    print(f"  |-------|----------------|------------------|")
    for a_val in key_spins:
        rp, rr = kerr_isco(a_val)
        print(f"  | {a_val:5.3f} | {rp:14.6f} | {rr:16.6f} |")

    # ASCII plot
    print()
    print("  r_ISCO/M vs a/M (prograde = -, retrograde = +)")
    print("  " + "-" * 62)

    rows = 18
    cols = 58
    r_min, r_max = 0.5, 10.0
    chart = [[' ' for _ in range(cols)] for _ in range(rows)]

    for i, d in enumerate(data):
        col = int(i / N * cols)
        if col >= cols:
            col = cols - 1

        # Prograde
        row_pro = int((r_max - d["r_pro"]) / (r_max - r_min) * (rows - 1))
        if 0 <= row_pro < rows:
            chart[row_pro][col] = '-'

        # Retrograde
        row_ret = int((r_max - d["r_retro"]) / (r_max - r_min) * (rows - 1))
        if 0 <= row_ret < rows:
            chart[row_ret][col] = '+'

    # Reference lines
    for c in range(cols):
        for ref_r in [6.0, 3.0, 1.0]:
            row_ref = int((r_max - ref_r) / (r_max - r_min) * (rows - 1))
            if 0 <= row_ref < rows and chart[row_ref][c] == ' ':
                chart[row_ref][c] = '.'

    for row_idx in range(rows):
        r_val = r_max - row_idx / (rows - 1) * (r_max - r_min)
        label = f"{r_val:5.1f} |"
        print(f"  {label}{''.join(chart[row_idx])}|")

    print(f"        {''.join(['-'] * cols)}")
    print(f"  a/M:  0.0" + " " * (cols - 16) + "0.5" + " " * 5 + "1.0")
    print("  Legend: - prograde, + retrograde, . reference lines (r=1,3,6)")


# ---------------------------------------------------------------------------
# --energy: Orbital energy and angular momentum at ISCO
# ---------------------------------------------------------------------------

def cmd_energy(as_json=False):
    """Energy and angular momentum at ISCO for Schwarzschild and Kerr limits."""
    M = 1.0
    r_isco = 6.0 * M
    E_isco = circular_orbit_energy(r_isco, M)
    L_isco = math.sqrt(12.0) * M
    binding = 1.0 - E_isco
    E_kerr_max = 1.0 / math.sqrt(3.0)
    binding_kerr = 1.0 - E_kerr_max

    result = {
        "schwarzschild": {
            "r_ISCO": 6.0,
            "E_over_mc2": round(E_isco, 10),
            "E_exact": "2*sqrt(2)/3",
            "E2": round(E_isco**2, 10),
            "E2_exact": "8/9",
            "L_over_M": round(L_isco, 10),
            "L_exact": "2*sqrt(3)",
            "L2_over_M2": 12.0,
            "binding_percent": round(binding * 100, 4),
        },
        "kerr_maximal": {
            "E_over_mc2": round(E_kerr_max, 10),
            "E_exact": "1/sqrt(3)",
            "binding_percent": round(binding_kerr * 100, 2),
        }
    }

    if as_json:
        print(json.dumps(result, indent=2))
        return

    print("Orbital Energy and Angular Momentum at ISCO")
    print("=" * 55)
    print()
    print("Schwarzschild (a=0):")
    print(f"  E/mc^2 = (1-2M/r)/sqrt(1-3M/r)")
    print(f"  At r=6M: E/mc^2 = (2/3)/sqrt(1/2) = 2*sqrt(2)/3 = {E_isco:.10f}")
    print(f"  E^2 = 8/9 = {E_isco**2:.10f}")
    print(f"  L = sqrt(12)*M = 2*sqrt(3)*M = {L_isco:.10f} M")
    print(f"  L^2 = 12 M^2")
    print(f"  Binding energy = {binding * 100:.4f}% of rest mass")
    print()
    print("Kerr maximal spin (a -> M, prograde):")
    print(f"  E/mc^2 -> 1/sqrt(3) = {E_kerr_max:.10f}")
    print(f"  Binding energy -> {binding_kerr * 100:.2f}%")
    print(f"  (Maximum energy extractable from accreting matter)")
    print()
    print("Energy decomposition:")
    print("  E^2 = 8/9 = 2^3 / 3^2")
    print("  Since 6 = 2 * 3, only prime factors of 6 appear.")


# ---------------------------------------------------------------------------
# --stability R: Check if orbit at r=R*M is stable
# ---------------------------------------------------------------------------

def cmd_stability(R, as_json=False):
    """Check stability of circular orbit at r = R*M."""
    M = 1.0
    r = R * M

    if r <= 3.0 * M:
        result = {
            "r_over_M": R,
            "stable": None,
            "reason": "Inside photon sphere (r <= 3M), no circular orbit exists",
        }
        if as_json:
            print(json.dumps(result, indent=2))
        else:
            print(f"r = {R}M is inside the photon sphere (r <= 3M).")
            print("No circular orbit exists here.")
        return

    L2 = circular_orbit_L2(r, M)
    E = circular_orbit_energy(r, M)
    d2v = schwarzschild_d2vdr2(r, L2, M)
    dv = schwarzschild_dvdr(r, L2, M)

    if d2v > 1e-12:
        stability = "STABLE"
    elif d2v < -1e-12:
        stability = "UNSTABLE"
    else:
        stability = "MARGINAL (ISCO)"

    result = {
        "r_over_M": R,
        "L2_over_M2": round(L2, 6),
        "E_over_mc2": round(E, 10),
        "dV_dr": round(dv, 10),
        "d2V_dr2": round(d2v, 10),
        "stability": stability,
    }

    if as_json:
        print(json.dumps(result, indent=2))
        return

    print(f"Stability Check: Circular Orbit at r = {R}M")
    print("=" * 50)
    print(f"  L^2_circ = {result['L2_over_M2']:.6f} M^2")
    print(f"  E/mc^2   = {result['E_over_mc2']:.10f}")
    print(f"  dV/dr    = {result['dV_dr']:.2e}  (should be ~0 for circular)")
    print(f"  d2V/dr2  = {result['d2V_dr2']:.10f}")
    print(f"  Status:    {stability}")

    if stability == "STABLE":
        print(f"\n  Orbit oscillates around r={R}M under small perturbation.")
    elif stability == "UNSTABLE":
        print(f"\n  Orbit plunges inward under small inward perturbation.")
    else:
        print(f"\n  This is the ISCO (r=6M). Any perturbation causes slow spiral.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="ISCO Calculator -- Innermost Stable Circular Orbit in GR"
    )
    parser.add_argument("--schwarzschild", action="store_true",
                        help="Exact Schwarzschild ISCO derivation")
    parser.add_argument("--kerr", type=float, metavar="SPIN",
                        help="Compute ISCO for given spin parameter a/M")
    parser.add_argument("--kerr-sweep", action="store_true",
                        help="Sweep a/M from 0 to 0.999, ASCII plot")
    parser.add_argument("--energy", action="store_true",
                        help="Orbital energy and angular momentum at ISCO")
    parser.add_argument("--stability", type=float, metavar="R",
                        help="Check if orbit at r=R*M is stable")
    parser.add_argument("--json", action="store_true",
                        help="Output in JSON format")

    args = parser.parse_args()

    ran_any = False

    if args.schwarzschild:
        cmd_schwarzschild(as_json=args.json)
        ran_any = True
    if args.kerr is not None:
        if ran_any:
            print()
        cmd_kerr(args.kerr, as_json=args.json)
        ran_any = True
    if args.kerr_sweep:
        if ran_any:
            print()
        cmd_kerr_sweep(as_json=args.json)
        ran_any = True
    if args.energy:
        if ran_any:
            print()
        cmd_energy(as_json=args.json)
        ran_any = True
    if args.stability is not None:
        if ran_any:
            print()
        cmd_stability(args.stability, as_json=args.json)
        ran_any = True

    if not ran_any:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
