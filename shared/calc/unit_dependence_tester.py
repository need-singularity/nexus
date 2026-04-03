#!/usr/bin/env python3
"""
unit_dependence_tester.py -- Check whether a numerical match between a formula
value and a physical constant is unit-dependent or universal.

Many hypotheses claim matches like "Universe age 13.8 Gyr = 138" or
"CMB temp 2.725 K ~ e".  These only work in specific unit choices.
This tool automatically tests all standard unit representations.

Usage:
  python3 calc/unit_dependence_tester.py --constant CMB_temperature --formula-value 2.718
  python3 calc/unit_dependence_tester.py --constant universe_age --formula-value 138
  python3 calc/unit_dependence_tester.py --constant hubble --formula-value 70
  python3 calc/unit_dependence_tester.py --constant fine_structure --formula-value 137.036
  python3 calc/unit_dependence_tester.py --constant higgs_mass --formula-value 125
  python3 calc/unit_dependence_tester.py --list
  python3 calc/unit_dependence_tester.py --list-all   # show all values in all units
"""

import argparse
import math
import sys

# ── Match threshold ──────────────────────────────────────────────────────
MATCH_THRESHOLD = 0.05  # 5% relative error

# ── Unit conversion helpers ──────────────────────────────────────────────

# Temperature conversions (from Kelvin)
def K_to_C(k):   return k - 273.15
def K_to_F(k):   return k * 9/5 - 459.67
def K_to_R(k):   return k * 9/5

# Energy conversions: base unit = GeV
GEV_TO_MEV  = 1e3
GEV_TO_EV   = 1e9
GEV_TO_KEV  = 1e6
GEV_TO_J    = 1.602176634e-10
GEV_TO_KG   = 1.78266192e-27   # E/c^2

# Time conversions: base unit = seconds
S_TO_MIN    = 1/60
S_TO_HR     = 1/3600
S_TO_DAY    = 1/86400
S_TO_YR     = 1/3.15576e7       # Julian year
S_TO_GYR    = 1/3.15576e16

# Length conversions: base unit = meters
M_TO_CM     = 1e2
M_TO_ANG    = 1e10              # Angstrom
M_TO_FM     = 1e15              # femtometer
M_TO_PLK    = 1/1.616255e-35   # Planck lengths
M_TO_LY     = 1/9.4607e15      # light-years
M_TO_PC     = 1/3.0857e16      # parsec
M_TO_KPC    = 1/3.0857e19
M_TO_MPC    = 1/3.0857e22

# Speed conversions: base unit = m/s
MS_TO_KMS   = 1e-3
MS_TO_C     = 1/299792458      # fraction of c
MS_TO_KMSMPC = None             # special: only for Hubble

# Frequency: base unit = Hz
HZ_TO_KHZ   = 1e-3
HZ_TO_MHZ   = 1e-6
HZ_TO_GHZ   = 1e-9
HZ_TO_RADS  = 2 * math.pi      # rad/s per Hz (multiply)

# ── Constants database ───────────────────────────────────────────────────
# Each entry: {
#   "description": str,
#   "dimensionless": bool,
#   "units": { unit_name: (value, unit_symbol) }
# }

CONSTANTS = {}

def _add(name, desc, units, dimensionless=False):
    CONSTANTS[name] = {
        "description": desc,
        "dimensionless": dimensionless,
        "units": units,
    }

# --- Temperature ---
_T_cmb = 2.7255  # Kelvin
_add("CMB_temperature", "CMB Temperature", {
    "Kelvin":     (_T_cmb,          "K"),
    "Celsius":    (K_to_C(_T_cmb),  "C"),
    "Fahrenheit": (K_to_F(_T_cmb),  "F"),
    "Rankine":    (K_to_R(_T_cmb),  "R"),
    "eV":         (_T_cmb * 8.617333262e-5, "eV"),  # kT
})

# --- Time ---
_age_s = 4.354e17  # seconds (13.787 Gyr)
_add("universe_age", "Age of the Universe", {
    "seconds":  (_age_s,               "s"),
    "minutes":  (_age_s * S_TO_MIN,    "min"),
    "hours":    (_age_s * S_TO_HR,     "hr"),
    "days":     (_age_s * S_TO_DAY,    "days"),
    "years":    (_age_s * S_TO_YR,     "yr"),
    "Gyr":      (_age_s * S_TO_GYR,    "Gyr"),
})

# --- Hubble constant ---
# H0 in km/s/Mpc is the conventional unit; convert to other rate units
_H0_kmsmpc_planck = 67.4
_H0_kmsmpc_shoes  = 73.0
_H0_si = _H0_kmsmpc_planck * 1e3 / 3.0857e22  # 1/s
_add("hubble", "Hubble Constant (Planck 2018)", {
    "km/s/Mpc":  (_H0_kmsmpc_planck,    "km/s/Mpc"),
    "1/s":       (_H0_si,               "s^-1"),
    "1/Gyr":     (_H0_si * 3.15576e16,  "Gyr^-1"),
    "mi/s/Mpc":  (_H0_kmsmpc_planck * 0.621371, "mi/s/Mpc"),
})

_add("hubble_shoes", "Hubble Constant (SH0ES)", {
    "km/s/Mpc":  (_H0_kmsmpc_shoes,     "km/s/Mpc"),
    "1/s":       (_H0_kmsmpc_shoes * 1e3 / 3.0857e22, "s^-1"),
    "1/Gyr":     (_H0_kmsmpc_shoes * 1e3 / 3.0857e22 * 3.15576e16, "Gyr^-1"),
})

# --- Dimensionless constants ---
_add("fine_structure", "Fine Structure Constant (1/alpha)", {
    "1/alpha": (137.035999084, ""),
    "alpha":   (1/137.035999084, ""),
}, dimensionless=True)

_add("fine_structure_alpha", "Fine Structure Constant (alpha)", {
    "alpha": (1/137.035999084, ""),
}, dimensionless=True)

_add("weinberg_angle", "Weak Mixing Angle sin^2(theta_W)", {
    "sin^2(theta_W)": (0.23122, ""),
}, dimensionless=True)

# --- Particle masses (GeV base) ---
def _add_mass(name, desc, gev_val):
    _add(name, desc, {
        "GeV":  (gev_val,                      "GeV/c^2"),
        "MeV":  (gev_val * GEV_TO_MEV,         "MeV/c^2"),
        "eV":   (gev_val * GEV_TO_EV,          "eV/c^2"),
        "keV":  (gev_val * GEV_TO_KEV,         "keV/c^2"),
        "kg":   (gev_val * GEV_TO_KG,          "kg"),
        "J/c^2":(gev_val * GEV_TO_J,           "J/c^2"),
    })

_add_mass("higgs_mass",     "Higgs Boson Mass",     125.25)
_add_mass("z_boson_mass",   "Z Boson Mass",         91.1876)
_add_mass("w_boson_mass",   "W Boson Mass",         80.3692)
_add_mass("top_quark_mass", "Top Quark Mass",       172.76)
_add_mass("electron_mass",  "Electron Mass",        0.51099895e-3)
_add_mass("muon_mass",      "Muon Mass",            0.1056583755)
_add_mass("tau_mass",       "Tau Mass",             1.77686)
_add_mass("proton_mass",    "Proton Mass",          0.93827208816)
_add_mass("neutron_mass",   "Neutron Mass",         0.93956542052)

# --- Fundamental constants ---
_add("speed_of_light", "Speed of Light", {
    "m/s":   (299792458,          "m/s"),
    "km/s":  (299792.458,         "km/s"),
    "km/h":  (299792458 * 3.6,    "km/h"),
    "ft/s":  (299792458 * 3.28084,"ft/s"),
    "c":     (1.0,                "c"),
}, dimensionless=False)

_h_J = 6.62607015e-34
_add("planck_constant", "Planck Constant", {
    "J*s":    (_h_J,                "J*s"),
    "eV*s":   (_h_J / 1.602176634e-19, "eV*s"),
    "erg*s":  (_h_J * 1e7,          "erg*s"),
})

_hbar = _h_J / (2 * math.pi)
_add("hbar", "Reduced Planck Constant", {
    "J*s":    (_hbar,                "J*s"),
    "eV*s":   (_hbar / 1.602176634e-19, "eV*s"),
    "MeV*fm": (197.3269804,         "MeV*fm"),
})

_add("boltzmann", "Boltzmann Constant", {
    "J/K":    (1.380649e-23,       "J/K"),
    "eV/K":   (8.617333262e-5,     "eV/K"),
    "erg/K":  (1.380649e-16,       "erg/K"),
})

_add("gravitational", "Gravitational Constant", {
    "m^3/(kg*s^2)": (6.67430e-11,  "m^3 kg^-1 s^-2"),
    "cm^3/(g*s^2)": (6.67430e-8,   "cm^3 g^-1 s^-2"),
})

# --- Planck units ---
_lp = 1.616255e-35
_add("planck_length", "Planck Length", {
    "meters":   (_lp,            "m"),
    "cm":       (_lp * 1e2,      "cm"),
    "fm":       (_lp * 1e15,     "fm"),
    "Angstrom": (_lp * 1e10,     "A"),
})

_tp = 5.391247e-44
_add("planck_time", "Planck Time", {
    "seconds": (_tp,             "s"),
    "Planck":  (1.0,             "t_P"),
})

_mp = 2.176434e-8
_add("planck_mass", "Planck Mass", {
    "kg":   (_mp,                      "kg"),
    "GeV":  (_mp / GEV_TO_KG,         "GeV/c^2"),
    "eV":   (_mp / GEV_TO_KG * 1e9,   "eV/c^2"),
    "g":    (_mp * 1e3,                "g"),
})

_Tp = 1.416784e32
_add("planck_temperature", "Planck Temperature", {
    "Kelvin":     (_Tp,          "K"),
    "Celsius":    (K_to_C(_Tp),  "C"),
    "Fahrenheit": (K_to_F(_Tp),  "F"),
    "GeV":        (_Tp * 8.617333262e-5 / 1e9, "GeV"),
})

# --- Cosmological ---
_add("cosmological_constant", "Cosmological Constant (Lambda)", {
    "m^-2":    (1.1056e-52,         "m^-2"),
    "Mpc^-2":  (1.1056e-52 * (3.0857e22)**2, "Mpc^-2"),
})

_add("dark_energy_density", "Dark Energy Density", {
    "J/m^3":    (5.96e-27 * 299792458**2, "J/m^3"),
    "kg/m^3":   (5.96e-27,                "kg/m^3"),
    "GeV^4":    (2.6e-47,                 "GeV^4"),
})

_add("omega_matter", "Matter Density Parameter", {
    "Omega_m": (0.3153, ""),
}, dimensionless=True)

_add("omega_lambda", "Dark Energy Density Parameter", {
    "Omega_L": (0.6847, ""),
}, dimensionless=True)

_add("omega_baryon", "Baryon Density Parameter", {
    "Omega_b": (0.0493, ""),
}, dimensionless=True)

# --- Mathematical constants (always dimensionless) ---
_add("euler_mascheroni", "Euler-Mascheroni Constant", {
    "gamma": (0.5772156649015329, ""),
}, dimensionless=True)

_add("golden_ratio", "Golden Ratio", {
    "phi": ((1 + math.sqrt(5)) / 2, ""),
}, dimensionless=True)


# ── Core test function ───────────────────────────────────────────────────

def relative_error(measured, expected):
    """Relative error as fraction. Handles zero expected."""
    if expected == 0:
        return abs(measured) if measured != 0 else 0.0
    return abs(measured - expected) / abs(expected)


def test_unit_dependence(constant_name, formula_value, threshold=MATCH_THRESHOLD):
    """Test whether formula_value matches constant in all or only some units.

    Returns dict with full results.
    """
    if constant_name not in CONSTANTS:
        available = ", ".join(sorted(CONSTANTS.keys()))
        raise ValueError(
            f"Unknown constant: '{constant_name}'\n"
            f"Available: {available}"
        )

    cdata = CONSTANTS[constant_name]
    desc = cdata["description"]
    is_dimless = cdata["dimensionless"]
    units = cdata["units"]

    results = []
    n_match = 0
    n_total = len(units)

    for unit_name, (value, symbol) in units.items():
        err = relative_error(formula_value, value)
        match = err <= threshold
        if match:
            n_match += 1
        results.append({
            "unit": unit_name,
            "value": value,
            "symbol": symbol,
            "error": err,
            "match": match,
        })

    # Determine verdict
    if is_dimless:
        if n_total == 1:
            verdict = "UNIT-INDEPENDENT"
            verdict_detail = "Dimensionless constant -- match is physically meaningful."
        else:
            # Multiple representations (e.g., alpha vs 1/alpha)
            if n_match == n_total:
                verdict = "UNIT-INDEPENDENT"
                verdict_detail = "Matches all representations of this dimensionless constant."
            elif n_match > 0:
                verdict = "REPRESENTATION-DEPENDENT"
                verdict_detail = (
                    f"Matches {n_match}/{n_total} representations. "
                    "Dimensionless but representation choice matters."
                )
            else:
                verdict = "NO MATCH"
                verdict_detail = "Does not match any representation."
    else:
        if n_match == n_total:
            verdict = "UNIT-INDEPENDENT"
            verdict_detail = "Matches in ALL unit systems -- robust result."
        elif n_match == 0:
            verdict = "NO MATCH"
            verdict_detail = "Does not match in any unit system."
        elif n_match == 1:
            matched_unit = [r["unit"] for r in results if r["match"]][0]
            verdict = "UNIT-DEPENDENT"
            verdict_detail = (
                f"Matches in only 1/{n_total} units ({matched_unit}). "
                f"This match is an artifact of the {matched_unit} unit choice."
            )
        else:
            verdict = "UNIT-DEPENDENT"
            matched = [r["unit"] for r in results if r["match"]]
            verdict_detail = (
                f"Matches in {n_match}/{n_total} units ({', '.join(matched)}). "
                "Partially unit-dependent."
            )

    return {
        "constant": constant_name,
        "description": desc,
        "formula_value": formula_value,
        "dimensionless": is_dimless,
        "threshold": threshold,
        "results": results,
        "n_match": n_match,
        "n_total": n_total,
        "verdict": verdict,
        "verdict_detail": verdict_detail,
    }


# ── Display ──────────────────────────────────────────────────────────────

def format_value(v):
    """Format a number for display."""
    av = abs(v)
    if av == 0:
        return "0"
    if av >= 1e6 or av < 1e-3:
        return f"{v:.4e}"
    if av >= 100:
        return f"{v:.2f}"
    if av >= 1:
        return f"{v:.4f}"
    return f"{v:.6f}"


def print_results(res):
    """Pretty-print test results."""
    print(f"\nConstant: {res['description']}")
    print(f"Formula value: {res['formula_value']}")
    if res["dimensionless"]:
        print("(dimensionless constant)")
    print(f"Match threshold: {res['threshold']*100:.1f}%")
    print()

    # Find longest unit name for alignment
    max_unit = max(len(r["unit"]) for r in res["results"])

    for r in res["results"]:
        unit_str = r["unit"].ljust(max_unit)
        val_str = format_value(r["value"]).rjust(14)
        sym = f" {r['symbol']}" if r["symbol"] else ""
        err_pct = r["error"] * 100
        if err_pct < 100:
            err_str = f"{err_pct:.2f}%"
        else:
            err_str = f"{err_pct:.0f}%"
        mark = "MATCH" if r["match"] else "NO MATCH"
        icon = "  ok" if r["match"] else "   x"
        print(f"  {unit_str}  {val_str}{sym}  ->  error {err_str.rjust(10)}  {icon}  {mark}")

    print()
    print(f"Verdict: {res['verdict']} ({res['n_match']}/{res['n_total']} units match)")
    if res["verdict"] == "UNIT-DEPENDENT":
        print(f"  WARNING: {res['verdict_detail']}")
    elif res["verdict"] == "UNIT-INDEPENDENT":
        print(f"  {res['verdict_detail']}")
    elif res["verdict"] == "REPRESENTATION-DEPENDENT":
        print(f"  NOTE: {res['verdict_detail']}")
    elif res["verdict"] == "NO MATCH":
        print(f"  {res['verdict_detail']}")
    print()


def list_constants(verbose=False):
    """List all available constants."""
    print("\nAvailable constants:")
    print("=" * 70)
    for name in sorted(CONSTANTS.keys()):
        c = CONSTANTS[name]
        tag = " [dimensionless]" if c["dimensionless"] else ""
        units_list = list(c["units"].keys())
        first_val = list(c["units"].values())[0]
        print(f"  {name:<30s}  {c['description']}{tag}")
        if verbose:
            for uname, (val, sym) in c["units"].items():
                sym_str = f" {sym}" if sym else ""
                print(f"    {uname:<16s}  = {format_value(val)}{sym_str}")
            print()
    print(f"\nTotal: {len(CONSTANTS)} constants")
    print()


# ── CLI ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Unit Dependence Tester -- check if formula-constant "
                    "matches are unit-dependent or universal."
    )
    parser.add_argument("--constant", "-c", type=str,
                        help="Name of physical constant to test")
    parser.add_argument("--formula-value", "-f", type=float,
                        help="Claimed formula value to compare")
    parser.add_argument("--threshold", "-t", type=float, default=MATCH_THRESHOLD,
                        help=f"Match threshold as fraction (default {MATCH_THRESHOLD})")
    parser.add_argument("--list", action="store_true",
                        help="List all available constants")
    parser.add_argument("--list-all", action="store_true",
                        help="List all constants with all unit values")
    parser.add_argument("--batch", type=str,
                        help="Batch test: comma-separated constant:value pairs "
                             "(e.g. 'CMB_temperature:2.718,universe_age:138')")

    args = parser.parse_args()

    if args.list or args.list_all:
        list_constants(verbose=args.list_all)
        return

    if args.batch:
        pairs = args.batch.split(",")
        summary = []
        for pair in pairs:
            parts = pair.strip().split(":")
            if len(parts) != 2:
                print(f"ERROR: Bad batch format '{pair}', expected 'name:value'")
                continue
            cname, fval = parts[0].strip(), float(parts[1].strip())
            res = test_unit_dependence(cname, fval, args.threshold)
            print_results(res)
            summary.append((cname, fval, res["verdict"], res["n_match"], res["n_total"]))
        # Print summary table
        if len(summary) > 1:
            print("\n" + "=" * 70)
            print("BATCH SUMMARY")
            print("=" * 70)
            print(f"  {'Constant':<30s} {'Value':>10s}  {'Match':>7s}  Verdict")
            print(f"  {'-'*30} {'-'*10}  {'-'*7}  {'-'*20}")
            for cname, fval, verdict, nm, nt in summary:
                print(f"  {cname:<30s} {fval:>10g}  {nm:>2}/{nt:<2}    {verdict}")
            print()
        return

    if not args.constant or args.formula_value is None:
        parser.print_help()
        print("\nExamples:")
        print('  python3 calc/unit_dependence_tester.py --constant CMB_temperature --formula-value 2.718')
        print('  python3 calc/unit_dependence_tester.py --constant universe_age --formula-value 138')
        print('  python3 calc/unit_dependence_tester.py --constant fine_structure --formula-value 137.036')
        print('  python3 calc/unit_dependence_tester.py --list')
        sys.exit(1)

    try:
        res = test_unit_dependence(args.constant, args.formula_value, args.threshold)
    except ValueError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    print_results(res)


if __name__ == "__main__":
    main()
