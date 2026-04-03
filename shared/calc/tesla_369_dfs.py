#!/usr/bin/env python3
"""Tesla 369 DFS Identity Miner — Systematic search for {3,6,9} identities at n=6

Searches all 2-operand expressions (a OP b) over 12 arithmetic functions
for values in the Tesla 369 target set {3,6,9,18,27,36,54,81,162}.

For each identity found, checks UNIQUENESS: does it hold ONLY for n=6
among perfect numbers {6, 28, 496, 8128, 33550336}?

Phase 2 of Tesla 369 Theorem — mining identities before proving.

Usage:
  python3 calc/tesla_369_dfs.py                     # Full search
  python3 calc/tesla_369_dfs.py --unique             # Show only UNIQUE identities
  python3 calc/tesla_369_dfs.py --targets 3,6,9      # Custom targets
  python3 calc/tesla_369_dfs.py --depth 2            # Operand count (only 2)
"""

import argparse
import math
import sys
from fractions import Fraction


# ═══════════════════════════════════════════════════════════════
# Arithmetic Functions (exact, works for any positive integer)
# ═══════════════════════════════════════════════════════════════

def factorize(n):
    """Return prime factorization as dict {prime: exponent}."""
    factors = {}
    d = 2
    temp = n
    while d * d <= temp:
        while temp % d == 0:
            factors[d] = factors.get(d, 0) + 1
            temp //= d
        d += 1
    if temp > 1:
        factors[temp] = factors.get(temp, 0) + 1
    return factors


def sigma_func(n):
    """Sum of divisors sigma(n)."""
    factors = factorize(n)
    result = 1
    for p, e in factors.items():
        result *= (p ** (e + 1) - 1) // (p - 1)
    return result


def tau_func(n):
    """Number of divisors tau(n)."""
    factors = factorize(n)
    result = 1
    for e in factors.values():
        result *= (e + 1)
    return result


def phi_func(n):
    """Euler's totient phi(n)."""
    factors = factorize(n)
    result = n
    for p in factors:
        result = result * (p - 1) // p
    return result


def sopfr_func(n):
    """Sum of prime factors with multiplicity."""
    factors = factorize(n)
    return sum(p * e for p, e in factors.items())


def rad_func(n):
    """Radical: product of distinct prime factors."""
    factors = factorize(n)
    result = 1
    for p in factors:
        result *= p
    return result


def omega_func(n):
    """Number of distinct prime factors."""
    return len(factorize(n))


def bigomega_func(n):
    """Number of prime factors with multiplicity."""
    factors = factorize(n)
    return sum(factors.values())


def carmichael_func(n):
    """Carmichael lambda(n) — reduced totient."""
    if n <= 2:
        return 1
    factors = factorize(n)
    result = 1
    for p, e in factors.items():
        if p == 2 and e >= 3:
            lam = 2 ** (e - 2)
        else:
            lam = (p - 1) * p ** (e - 1)
        result = lcm(result, lam)
    return result


def lcm(a, b):
    return abs(a * b) // math.gcd(a, b) if a and b else 0


def mobius_abs_func(n):
    """|mu(n)| — absolute value of Mobius function."""
    factors = factorize(n)
    for e in factors.values():
        if e > 1:
            return 0
    return 1


def dedekind_psi_func(n):
    """Dedekind psi(n) = n * prod(1 + 1/p) for p | n."""
    factors = factorize(n)
    result = n
    for p in factors:
        result = result * (p + 1) // p
    return result


def jordan_j2_func(n):
    """Jordan J_2(n) = n^2 * prod(1 - 1/p^2) for p | n."""
    factors = factorize(n)
    result = n * n
    for p in factors:
        result = result * (p * p - 1) // (p * p)
    return result


# ═══════════════════════════════════════════════════════════════
# Function Registry
# ═══════════════════════════════════════════════════════════════

FUNC_NAMES = [
    "n", "sigma", "tau", "phi", "sopfr", "rad",
    "omega", "bigomega", "lambda", "|mu|", "psi", "J2"
]

def compute_all(n):
    """Compute all 12 arithmetic functions for n. Returns dict."""
    return {
        "n": n,
        "sigma": sigma_func(n),
        "tau": tau_func(n),
        "phi": phi_func(n),
        "sopfr": sopfr_func(n),
        "rad": rad_func(n),
        "omega": omega_func(n),
        "bigomega": bigomega_func(n),
        "lambda": carmichael_func(n),
        "|mu|": mobius_abs_func(n),
        "psi": dedekind_psi_func(n),
        "J2": jordan_j2_func(n),
    }


# ═══════════════════════════════════════════════════════════════
# Binary Operations
# ═══════════════════════════════════════════════════════════════

def safe_op(a, b, op):
    """Evaluate a OP b safely, return Fraction or None."""
    try:
        fa, fb = Fraction(a), Fraction(b)
        if op == "+":
            return fa + fb
        elif op == "-":
            return fa - fb
        elif op == "*":
            return fa * fb
        elif op == "/":
            if fb == 0:
                return None
            return fa / fb
        elif op == "^":
            # Only integer exponents, limit size
            if fb.denominator != 1:
                return None
            exp = int(fb)
            if exp < 0 or exp > 20:
                return None
            if fa == 0 and exp == 0:
                return Fraction(1)
            result = fa ** exp
            if result.numerator > 10**15:
                return None
            return result
        elif op == "mod":
            if fb == 0:
                return None
            if fa.denominator != 1 or fb.denominator != 1:
                return None
            return Fraction(int(fa) % int(fb))
    except (OverflowError, ZeroDivisionError, ValueError):
        return None
    return None


COMMUTATIVE_OPS = {"+", "*"}
ALL_OPS = ["+", "-", "*", "/", "^", "mod"]


# ═══════════════════════════════════════════════════════════════
# DFS Search Engine
# ═══════════════════════════════════════════════════════════════

def search_identities(targets, perfect_numbers=None):
    """Search all 2-operand expressions for target values.

    Returns list of dicts:
      {expr, value, unique, other_matches}
    """
    if perfect_numbers is None:
        perfect_numbers = [6, 28, 496, 8128, 33550336]

    target_set = set(Fraction(t) for t in targets)

    # Precompute all function values for all perfect numbers
    all_vals = {}
    for pn in perfect_numbers:
        all_vals[pn] = compute_all(pn)

    vals6 = all_vals[6]
    names = FUNC_NAMES

    results = []
    seen = set()

    for i, name_a in enumerate(names):
        for j, name_b in enumerate(names):
            a6 = vals6[name_a]
            b6 = vals6[name_b]
            for op in ALL_OPS:
                # Deduplicate commutative ops
                if op in COMMUTATIVE_OPS and j < i:
                    continue

                val = safe_op(a6, b6, op)
                if val is None or val not in target_set:
                    continue

                expr = f"{name_a} {op} {name_b}"
                if expr in seen:
                    continue
                seen.add(expr)

                # Check uniqueness among perfect numbers
                other_matches = []
                for pn in perfect_numbers:
                    if pn == 6:
                        continue
                    vpn = all_vals[pn]
                    a_pn = vpn[name_a]
                    b_pn = vpn[name_b]
                    val_pn = safe_op(a_pn, b_pn, op)
                    if val_pn is not None and val_pn == val:
                        other_matches.append(pn)

                # Get n=28 value for display
                a28 = all_vals[28][name_a]
                b28 = all_vals[28][name_b]
                val28 = safe_op(a28, b28, op)

                results.append({
                    "expr": expr,
                    "op": op,
                    "name_a": name_a,
                    "name_b": name_b,
                    "value": val,
                    "unique": len(other_matches) == 0,
                    "other_matches": other_matches,
                    "val28": val28,
                })

    # Sort: unique first, then by value, then expr
    results.sort(key=lambda r: (not r["unique"], float(r["value"]), r["expr"]))
    return results


# ═══════════════════════════════════════════════════════════════
# Display
# ═══════════════════════════════════════════════════════════════

SEP = "=" * 72
SUBSEP = "-" * 72


def print_arith_table():
    """Print arithmetic function values for all perfect numbers."""
    pns = [6, 28, 496, 8128, 33550336]
    print(SEP)
    print("  ARITHMETIC FUNCTION VALUES FOR PERFECT NUMBERS")
    print(SEP)
    header = f"  {'func':<10}" + "".join(f"{'n='+str(p):>12}" for p in pns)
    print(header)
    print(SUBSEP)
    for name in FUNC_NAMES:
        row = f"  {name:<10}"
        for pn in pns:
            v = compute_all(pn)[name]
            row += f"{v:>12}"
        print(row)
    print()


def print_results(results, unique_only=False):
    """Print results table."""
    filtered = [r for r in results if r["unique"]] if unique_only else results

    grade_label = "UNIQUE-ONLY" if unique_only else "ALL"
    print(SEP)
    print(f"  TESLA 369 IDENTITY TABLE ({grade_label}) — {len(filtered)} identities")
    print(SEP)
    print(f"  {'#':<4} {'Expression':<25} {'= Value':<10} {'Grade':<10} {'n=28 value':<15}")
    print(SUBSEP)

    for idx, r in enumerate(filtered, 1):
        val_str = str(r["value"])
        if r["value"].denominator == 1:
            val_str = str(int(r["value"]))
        grade = "UNIQUE" if r["unique"] else f"shared({len(r['other_matches'])})"
        v28 = r["val28"]
        if v28 is None:
            v28_str = "undef"
        elif v28.denominator == 1:
            v28_str = str(int(v28))
        else:
            v28_str = f"{v28.numerator}/{v28.denominator}"
        print(f"  {idx:<4} {r['expr']:<25} = {val_str:<8} {grade:<10} {v28_str:<15}")
    print()


def print_triad_analysis(results):
    """Print 369 triad analysis."""
    print(SEP)
    print("  369 TRIAD ANALYSIS")
    print(SEP)

    for target in [3, 6, 9]:
        ft = Fraction(target)
        total = [r for r in results if r["value"] == ft]
        unique = [r for r in total if r["unique"]]
        print(f"\n  Target = {target}:  {len(total)} total,  {len(unique)} UNIQUE")
        print(SUBSEP)
        for r in total:
            tag = " *** UNIQUE ***" if r["unique"] else ""
            print(f"    {r['expr']:<25} = {target}{tag}")

    print()

    # Extended targets
    extended = [18, 27, 36, 54, 81, 162]
    print(f"\n  EXTENDED TARGETS (multiples of 9):")
    print(SUBSEP)
    for target in extended:
        ft = Fraction(target)
        total = [r for r in results if r["value"] == ft]
        unique = [r for r in total if r["unique"]]
        if total:
            print(f"\n  Target = {target}:  {len(total)} total,  {len(unique)} UNIQUE")
            for r in total:
                tag = " *** UNIQUE ***" if r["unique"] else ""
                print(f"    {r['expr']:<25} = {target}{tag}")

    print()


def print_key_identities(results):
    """Print key identities section."""
    print(SEP)
    print("  KEY IDENTITIES — Theorem Candidates")
    print(SEP)

    key_exprs = {
        "sigma / tau": "sigma/tau = 3 (divisor ratio)",
        "sigma / phi": "sigma/phi = 6 (self-referential: sigma/phi = n)",
        "n + sopfr - phi": "n + sopfr - phi = 9 (additive triad)",
        "sigma - n": "sigma - n = 6 (perfect number: sigma(n) = 2n)",
        "sigma / n": "sigma/n = 2 (perfect number signature)",
        "n / phi": "n/phi = 3 (totient ratio)",
    }

    for r in results:
        expr_key = r["expr"].replace("  ", " ").strip()
        if expr_key in key_exprs:
            tag = "UNIQUE" if r["unique"] else "SHARED"
            v28 = r["val28"]
            if v28 is None:
                v28_str = "undefined"
            elif v28.denominator == 1:
                v28_str = str(int(v28))
            else:
                v28_str = f"{v28.numerator}/{v28.denominator}"

            print(f"\n  {key_exprs[expr_key]}")
            print(f"    n=6:  {r['expr']} = {int(r['value'])}")
            print(f"    n=28: {r['expr']} = {v28_str}")
            print(f"    Grade: {tag}")
            if r["other_matches"]:
                print(f"    Also holds for: {r['other_matches']}")

    print()


def print_summary(results):
    """Print summary statistics."""
    total = len(results)
    unique = sum(1 for r in results if r["unique"])
    shared = total - unique

    print(SEP)
    print("  SUMMARY")
    print(SEP)
    print(f"  Total identities found:  {total}")
    print(f"  UNIQUE to n=6:           {unique}")
    print(f"  Shared with other P_k:   {shared}")
    print()

    # Count by target value
    from collections import Counter
    val_counts = Counter()
    val_unique = Counter()
    for r in results:
        v = int(r["value"]) if r["value"].denominator == 1 else float(r["value"])
        val_counts[v] += 1
        if r["unique"]:
            val_unique[v] += 1

    print(f"  {'Target':<10} {'Total':<8} {'UNIQUE':<8}")
    print(SUBSEP)
    for v in sorted(val_counts.keys()):
        print(f"  {v:<10} {val_counts[v]:<8} {val_unique[v]:<8}")
    print()


# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Tesla 369 DFS Identity Miner — search n=6 arithmetic for {3,6,9} targets"
    )
    parser.add_argument("--unique", action="store_true",
                        help="Show only UNIQUE identities (n=6 only)")
    parser.add_argument("--targets", type=str, default="3,6,9,18,27,36,54,81,162",
                        help="Comma-separated target values (default: 3,6,9,18,27,36,54,81,162)")
    parser.add_argument("--depth", type=int, default=2,
                        help="Operand count (only 2 implemented)")
    args = parser.parse_args()

    targets = [int(t.strip()) for t in args.targets.split(",")]

    print()
    print(SEP)
    print("  TESLA 369 DFS IDENTITY MINER")
    print(f"  Targets: {targets}")
    print(f"  Depth: {args.depth} operands")
    print(f"  Functions: {len(FUNC_NAMES)} ({', '.join(FUNC_NAMES)})")
    print(f"  Operations: {ALL_OPS}")
    print(SEP)
    print()

    # Print arithmetic table
    print_arith_table()

    if args.depth != 2:
        print("  ERROR: Only depth=2 is implemented.")
        sys.exit(1)

    # Run search
    results = search_identities(targets)

    # Display
    print_results(results, unique_only=args.unique)
    print_triad_analysis(results)
    print_key_identities(results)
    print_summary(results)


if __name__ == "__main__":
    main()
