#!/usr/bin/env python3
"""Music Consonance Calculator -- Euler Gradus Suavitatis, N-TET analysis, circle of fifths.

Reusable calc/ tool derived from verify/verify_music_extreme.py.

Usage:
  python3 calc/music_consonance_calculator.py --gradus 3 2
  python3 calc/music_consonance_calculator.py --ranking 12
  python3 calc/music_consonance_calculator.py --ntet 12
  python3 calc/music_consonance_calculator.py --ntet-sweep 1 100
  python3 calc/music_consonance_calculator.py --circle-of-fifths 12
  python3 calc/music_consonance_calculator.py --divisor-test 6
  python3 calc/music_consonance_calculator.py --gradus 5 4 --json
"""

import argparse
import json
import math
import sys
from fractions import Fraction


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

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


def euler_gradus(a, b):
    """Euler Gradus Suavitatis for ratio a:b.
    GS(a/b) = 1 + sum(e_i * (p_i - 1)) for the LCM of the reduced fraction.
    """
    f = Fraction(a, b)
    num, den = f.numerator, f.denominator
    lcm_val = (num * den) // math.gcd(num, den)
    factors = prime_factorization(lcm_val)
    if not factors:
        return 1
    return 1 + sum(e * (p - 1) for p, e in factors.items())


def primes_used(a, b):
    """Set of primes used in reduced ratio a:b."""
    f = Fraction(a, b)
    num, den = f.numerator, f.denominator
    lcm_val = (num * den) // math.gcd(num, den)
    return set(prime_factorization(lcm_val).keys())


def divisors(n):
    """All divisors of n in sorted order."""
    divs = []
    for i in range(1, int(n**0.5) + 1):
        if n % i == 0:
            divs.append(i)
            if i != n // i:
                divs.append(n // i)
    return sorted(divs)


# ---------------------------------------------------------------------------
# --gradus A B: Euler GS for ratio A:B
# ---------------------------------------------------------------------------

def cmd_gradus(a, b, as_json=False):
    """Compute Euler Gradus Suavitatis for ratio A:B."""
    gs = euler_gradus(a, b)
    f = Fraction(a, b)
    ps = sorted(primes_used(a, b))
    lcm_val = (f.numerator * f.denominator) // math.gcd(f.numerator, f.denominator)
    factors = prime_factorization(lcm_val)
    cents = 1200 * math.log2(max(a, b) / min(a, b)) if a != b else 0

    result = {
        "a": a, "b": b,
        "reduced": str(f),
        "gradus_suavitatis": gs,
        "primes_used": ps,
        "lcm": lcm_val,
        "factorization": {str(p): e for p, e in factors.items()},
        "cents": round(cents, 3),
    }

    if as_json:
        print(json.dumps(result, indent=2))
        return

    print(f"Euler Gradus Suavitatis for {a}:{b}")
    print("=" * 40)
    print(f"  Reduced fraction: {f}")
    print(f"  LCM: {lcm_val}")
    factor_str = " * ".join(f"{p}^{e}" if e > 1 else str(p)
                            for p, e in sorted(factors.items()))
    print(f"  Factorization: {factor_str}")
    print(f"  GS = 1 + sum(e_i * (p_i - 1)) = {gs}")
    print(f"  Primes used: {ps}")
    print(f"  Interval: {cents:.3f} cents")
    print()
    if gs <= 4:
        print("  Rating: Highly consonant")
    elif gs <= 7:
        print("  Rating: Consonant")
    elif gs <= 10:
        print("  Rating: Mildly dissonant")
    else:
        print("  Rating: Dissonant")


# ---------------------------------------------------------------------------
# --ranking N: Rank all intervals a:b with a,b <= N by consonance
# ---------------------------------------------------------------------------

def cmd_ranking(N, as_json=False):
    """Rank all intervals a:b with a,b <= N by Euler GS (lowest = most consonant)."""
    seen = set()
    ratios = []
    for a in range(1, N + 1):
        for b in range(a + 1, N + 1):
            f = Fraction(a, b)
            key = (f.numerator, f.denominator)
            if key not in seen:
                seen.add(key)
                gs = euler_gradus(a, b)
                ps = sorted(primes_used(a, b))
                cents = 1200 * math.log2(b / a)
                ratios.append({
                    "a": a, "b": b, "reduced": str(f),
                    "gs": gs, "primes": ps, "cents": round(cents, 3),
                })
    ratios.sort(key=lambda x: (x["gs"], x["cents"]))

    if as_json:
        print(json.dumps(ratios, indent=2))
        return

    print(f"Consonance Ranking: all intervals a:b with a,b <= {N}")
    print("=" * 65)
    print(f"Total unique ratios: {len(ratios)}")
    print()
    print(f"{'Rank':<6}{'Ratio':<10}{'Fraction':<12}{'GS':<6}{'Cents':<10}{'Primes'}")
    print("-" * 55)
    for i, r in enumerate(ratios):
        print(f"{i+1:<6}{r['a']}:{r['b']:<7}{r['reduced']:<12}{r['gs']:<6}{r['cents']:<10.3f}{r['primes']}")

    # Summary stats
    top4 = ratios[:4]
    all_23 = all(set(r["primes"]) <= {2, 3} for r in top4)
    print()
    print(f"Top 4 most consonant all use only primes {{2,3}}: {all_23}")


# ---------------------------------------------------------------------------
# --ntet N: Evaluate N-TET quality for perfect consonances
# ---------------------------------------------------------------------------

# Just intonation targets
JI_TARGETS = {
    "P5 (3:2)": 1200 * math.log2(3 / 2),
    "P4 (4:3)": 1200 * math.log2(4 / 3),
    "M3 (5:4)": 1200 * math.log2(5 / 4),
    "m3 (6:5)": 1200 * math.log2(6 / 5),
}


def evaluate_ntet(n):
    """Evaluate N-TET for all 4 target intervals. Returns dict of errors."""
    step = 1200.0 / n
    errors = {}
    for name, target_cents in JI_TARGETS.items():
        closest = round(target_cents / step) * step
        errors[name] = abs(target_cents - closest)
    return errors


def cmd_ntet(n, as_json=False):
    """Evaluate N-TET quality for perfect consonances."""
    errors = evaluate_ntet(n)
    step = 1200.0 / n
    sse_perfect = sum(errors[k]**2 for k in errors if k.startswith("P"))
    sse_all = sum(e**2 for e in errors.values())

    result = {
        "N": n, "step_cents": round(step, 6),
        "errors": {k: round(v, 6) for k, v in errors.items()},
        "SSE_perfect": round(sse_perfect, 6),
        "SSE_all": round(sse_all, 6),
    }

    if as_json:
        print(json.dumps(result, indent=2))
        return

    print(f"{n}-TET Evaluation")
    print("=" * 50)
    print(f"  Step size: {step:.6f} cents")
    print()
    print(f"  {'Interval':<12}{'JI (cents)':<14}{'N-TET':<14}{'Error (cents)'}")
    print(f"  {'-'*50}")
    for name, target in JI_TARGETS.items():
        closest = round(target / step) * step
        err = errors[name]
        print(f"  {name:<12}{target:<14.3f}{closest:<14.3f}{err:.3f}")
    print()
    print(f"  SSE (perfect P5+P4): {sse_perfect:.6f}")
    print(f"  SSE (all 4):         {sse_all:.6f}")


# ---------------------------------------------------------------------------
# --ntet-sweep LO HI: Find optimal N
# ---------------------------------------------------------------------------

def cmd_ntet_sweep(lo, hi, as_json=False):
    """Sweep N-TET from lo to hi, rank by consonance quality."""
    results = []
    for n in range(lo, hi + 1):
        if n < 1:
            continue
        errors = evaluate_ntet(n)
        sse_p = sum(errors[k]**2 for k in errors if k.startswith("P"))
        sse_a = sum(e**2 for e in errors.values())
        results.append({
            "N": n, "SSE_perfect": round(sse_p, 6), "SSE_all": round(sse_a, 6),
            "P5_err": round(errors["P5 (3:2)"], 3),
            "P4_err": round(errors["P4 (4:3)"], 3),
            "M3_err": round(errors["M3 (5:4)"], 3),
            "m3_err": round(errors["m3 (6:5)"], 3),
        })

    by_perfect = sorted(results, key=lambda x: x["SSE_perfect"])
    by_all = sorted(results, key=lambda x: x["SSE_all"])

    if as_json:
        print(json.dumps({"by_perfect": by_perfect, "by_all": by_all}, indent=2))
        return

    print(f"N-TET Sweep: N={lo} to {hi}")
    print("=" * 75)

    print(f"\nJust intonation targets:")
    for name, cents in JI_TARGETS.items():
        print(f"  {name}: {cents:.3f} cents")

    print(f"\n--- Top 15 by PERFECT consonance (P5+P4) ---")
    print(f"{'Rank':<6}{'N':<6}{'SSE(P5+P4)':<14}{'P5 err':<10}{'P4 err':<10}{'M3 err':<10}{'m3 err':<10}")
    print("-" * 66)
    for i, r in enumerate(by_perfect[:15]):
        print(f"{i+1:<6}{r['N']:<6}{r['SSE_perfect']:<14.3f}"
              f"{r['P5_err']:<10.3f}{r['P4_err']:<10.3f}"
              f"{r['M3_err']:<10.3f}{r['m3_err']:<10.3f}")

    print(f"\n--- Top 15 by ALL 4 intervals ---")
    print(f"{'Rank':<6}{'N':<6}{'SSE(all4)':<14}{'P5 err':<10}{'P4 err':<10}{'M3 err':<10}{'m3 err':<10}")
    print("-" * 66)
    for i, r in enumerate(by_all[:15]):
        print(f"{i+1:<6}{r['N']:<6}{r['SSE_all']:<14.3f}"
              f"{r['P5_err']:<10.3f}{r['P4_err']:<10.3f}"
              f"{r['M3_err']:<10.3f}{r['m3_err']:<10.3f}")

    # Where does N=12 rank?
    rank_12_p = next((i + 1 for i, r in enumerate(by_perfect) if r["N"] == 12), None)
    rank_12_a = next((i + 1 for i, r in enumerate(by_all) if r["N"] == 12), None)
    if rank_12_p is not None:
        print(f"\nN=12 rank: #{rank_12_p} for perfect, #{rank_12_a} for all (out of {hi - lo + 1})")


# ---------------------------------------------------------------------------
# --circle-of-fifths N: Test closure at N steps
# ---------------------------------------------------------------------------

def cmd_circle_of_fifths(N, as_json=False):
    """Test circle of fifths closure: (3/2)^N closest to power of 2."""
    log2_ratio = math.log2(3 / 2)

    results = []
    for n in range(1, N + 1):
        val = n * log2_ratio
        m = round(val)
        error_log2 = abs(val - m)
        error_cents = error_log2 * 1200
        ratio = (3 / 2)**n / 2**m
        results.append({
            "N": n, "M": m,
            "ratio": round(ratio, 10),
            "error_cents": round(error_cents, 6),
        })

    results_sorted = sorted(results, key=lambda x: x["error_cents"])

    if as_json:
        print(json.dumps({"sorted_by_closure": results_sorted}, indent=2))
        return

    print(f"Circle of Fifths Closure Test (N=1..{N})")
    print("=" * 60)
    print(f"\nlog2(3/2) = {log2_ratio:.10f}")
    print(f"\nSearching for N where (3/2)^N is closest to a power of 2...")
    print()
    print(f"{'Rank':<6}{'N':<6}{'M':<6}{'(3/2)^N / 2^M':<18}{'error (cents)'}")
    print("-" * 50)
    for i, r in enumerate(results_sorted[:20]):
        print(f"{i+1:<6}{r['N']:<6}{r['M']:<6}{r['ratio']:<18.10f}{r['error_cents']:.6f}")

    best = results_sorted[0]
    print(f"\nBest closure: N={best['N']} (error = {best['error_cents']:.6f} cents)")

    # Pythagorean comma
    comma_float = (3 / 2)**12 / 2**7
    comma_cents = 1200 * math.log2(comma_float)
    print(f"\nPythagorean comma (N=12):")
    print(f"  (3/2)^12 / 2^7 = 3^12 / 2^19 = {3**12}/{2**19} = {comma_float:.10f}")
    print(f"  = {comma_cents:.6f} cents")


# ---------------------------------------------------------------------------
# --divisor-test N: Which top-K consonances use only divisors of N?
# ---------------------------------------------------------------------------

def cmd_divisor_test(N, as_json=False):
    """Check which top-K consonant intervals use only divisors of N as ratios."""
    divs_N = set(divisors(N))

    # Build all intervals up to 12
    seen = set()
    pool = []
    for a in range(1, 13):
        for b in range(a + 1, 13):
            f = Fraction(a, b)
            key = (f.numerator, f.denominator)
            if key not in seen:
                seen.add(key)
                gs = euler_gradus(a, b)
                pool.append((gs, f.numerator, f.denominator))
    pool.sort()

    # Check top K
    K_values = [4, 6, 8, 10]
    results = {}
    for K in K_values:
        top_k = pool[:K]
        matches = sum(1 for gs, num, den in top_k
                      if num in divs_N and den in divs_N)
        results[K] = {
            "top_K": K,
            "matches": matches,
            "intervals": [
                {"ratio": f"{num}:{den}", "gs": gs,
                 "both_divide_N": num in divs_N and den in divs_N}
                for gs, num, den in top_k
            ],
        }

    # Also sweep other n for comparison
    sweep = []
    for n in range(2, 101):
        divs_n = set(divisors(n))
        top4 = pool[:4]
        matches = sum(1 for gs, num, den in top4
                      if num in divs_n and den in divs_n)
        sweep.append({"n": n, "matches_top4": matches})

    max_matches = max(s["matches_top4"] for s in sweep)
    best_ns = [s["n"] for s in sweep if s["matches_top4"] == max_matches]

    if as_json:
        print(json.dumps({
            "N": N, "divisors": sorted(divs_N),
            "top_K_analysis": results,
            "sweep_best": {"max_matches": max_matches, "best_n": best_ns},
        }, indent=2))
        return

    print(f"Divisor Test: Which top-K consonances use only divisors of {N}?")
    print("=" * 60)
    print(f"divisors({N}) = {sorted(divs_N)}")
    print()

    for K in K_values:
        r = results[K]
        print(f"Top {K} most consonant intervals:")
        for iv in r["intervals"]:
            marker = " <-- both divide " + str(N) if iv["both_divide_N"] else ""
            print(f"  {iv['ratio']:>6}  GS={iv['gs']}{marker}")
        print(f"  Matches: {r['matches']}/{K}")
        print()

    print(f"Sweep n=2..100 (top-4 matches):")
    print(f"  Maximum matches: {max_matches}/4")
    print(f"  Achieved by n = {best_ns}")
    notable = [s for s in sweep if s["matches_top4"] >= 3 or s["n"] in [6, 12, 28]]
    if notable:
        print(f"\n  Notable n values (matches >= 3 or special):")
        for s in notable:
            print(f"    n={s['n']:>3}: {s['matches_top4']}/4 matches")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Music Consonance Calculator -- Euler Gradus, N-TET, circle of fifths, divisor analysis"
    )
    parser.add_argument("--gradus", nargs=2, type=int, metavar=("A", "B"),
                        help="Compute Euler Gradus Suavitatis for ratio A:B")
    parser.add_argument("--ranking", type=int, metavar="N",
                        help="Rank all intervals a:b with a,b <= N by consonance")
    parser.add_argument("--ntet", type=int, metavar="N",
                        help="Evaluate N-TET quality for perfect consonances")
    parser.add_argument("--ntet-sweep", nargs=2, type=int, metavar=("LO", "HI"),
                        help="Sweep N-TET from LO to HI, find optimal N")
    parser.add_argument("--circle-of-fifths", type=int, metavar="N",
                        help="Test circle of fifths closure at N steps")
    parser.add_argument("--divisor-test", type=int, metavar="N",
                        help="Which top-K consonances use only divisors of N?")
    parser.add_argument("--json", action="store_true",
                        help="Output in JSON format")

    args = parser.parse_args()

    ran_any = False

    if args.gradus is not None:
        cmd_gradus(args.gradus[0], args.gradus[1], as_json=args.json)
        ran_any = True
    if args.ranking is not None:
        if ran_any:
            print()
        cmd_ranking(args.ranking, as_json=args.json)
        ran_any = True
    if args.ntet is not None:
        if ran_any:
            print()
        cmd_ntet(args.ntet, as_json=args.json)
        ran_any = True
    if args.ntet_sweep is not None:
        if ran_any:
            print()
        cmd_ntet_sweep(args.ntet_sweep[0], args.ntet_sweep[1], as_json=args.json)
        ran_any = True
    if args.circle_of_fifths is not None:
        if ran_any:
            print()
        cmd_circle_of_fifths(args.circle_of_fifths, as_json=args.json)
        ran_any = True
    if args.divisor_test is not None:
        if ran_any:
            print()
        cmd_divisor_test(args.divisor_test, as_json=args.json)
        ran_any = True

    if not ran_any:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
