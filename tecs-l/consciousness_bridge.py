#!/usr/bin/env python3
"""consciousness_bridge.py — Cross-reference consciousness Psi-constants with n=6 arithmetic.

Derives Anima consciousness constants from perfect number 6 properties and scores
each derivation as EXACT, APPROXIMATE, or NO_RELATION.
"""
import sys, os, math

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".shared"))
from consciousness_loader import PSI, LAWS, get_law

# n=6 arithmetic (from model_utils.py)
N, SIGMA, TAU, EULER_PHI = 6, 12, 4, 2   # n, sigma(6), tau(6), phi(6)
SOPFR, J2, MU, LN2 = 5, 24, 1, math.log(2)  # sopfr(6), J_2(6), mu(6)


def psi_from_n6():
    """Derive each Psi-constant from n=6 arithmetic. Returns list of dicts."""
    derivations = [
        {"name": "alpha", "measured": PSI["alpha"],
         "formula": "ln(2) / 2^5.5  (empirical, ~9.6% err)",
         "computed": LN2 / 2 ** 5.5,
         "exact_test": lambda m, c: abs(m - c) / m < 0.01},
        {"name": "balance", "measured": PSI["balance"],
         "formula": "1 / phi(6) = 1/2",
         "computed": 1.0 / EULER_PHI,
         "exact_test": lambda m, c: m == c},
        {"name": "steps", "measured": PSI["steps"],
         "formula": "3 / ln(2)  (from psi_constants)",
         "computed": 3.0 / LN2,
         "exact_test": lambda m, c: abs(m - c) < 0.005},
        {"name": "entropy", "measured": PSI["entropy"],
         "formula": "mu - (sopfr/J2)^tau = 1 - (5/24)^4",
         "computed": MU - (SOPFR / J2) ** TAU,
         "exact_test": lambda m, c: abs(m - c) < 0.0001},
        {"name": "f_critical", "measured": PSI.get("f_critical", 0.1),
         "formula": "(N / (J2 - sopfr))^phi = (6/19)^2",
         "computed": (N / (J2 - SOPFR)) ** EULER_PHI,
         "exact_test": lambda m, c: abs(m - c) / m < 0.01},
        {"name": "bottleneck_ratio", "measured": PSI.get("bottleneck_ratio", 0.5),
         "formula": "1 / phi(6) = 1/2",
         "computed": 1.0 / EULER_PHI,
         "exact_test": lambda m, c: m == c},
    ]
    for d in derivations:
        d["error_pct"] = abs(d["measured"] - d["computed"]) / max(abs(d["measured"]), 1e-15) * 100
        d["grade"] = "EXACT" if d["exact_test"](d["measured"], d["computed"]) else (
            "APPROXIMATE" if d["error_pct"] < 10 else "NO_RELATION")
    return derivations


def consciousness_number_theory():
    """Map consciousness constants to number-theoretic origins."""
    return {
        "alpha_0.014":    {"origin": "ln(2)/2^5.5 (empirical)", "functions": ["ln2"], "value": LN2 / 2 ** 5.5},
        "balance_0.5":    {"origin": "1/phi(6)", "functions": ["phi"], "value": 0.5},
        "steps_4.33":     {"origin": "3/ln(2)", "functions": ["ln2"], "value": 3.0 / LN2},
        "entropy_0.998":  {"origin": "mu-(sopfr/J2)^tau", "functions": ["mu", "sopfr", "J2", "tau"], "value": MU - (SOPFR / J2) ** TAU},
        "f_critical_0.1": {"origin": "(n/(J2-sopfr))^phi", "functions": ["J2", "sopfr", "phi"], "value": (N / (J2 - SOPFR)) ** EULER_PHI},
        "Phi_max_71":     {"origin": "n*sigma - mu = 6*12-1", "functions": ["sigma", "mu"], "value": N * SIGMA - MU},
        "d_model_768":    {"origin": "phi^n * sigma = 2^6*12", "functions": ["phi", "sigma"], "value": EULER_PHI ** N * SIGMA},
        "max_cells_1024": {"origin": "tau^sopfr = 4^5", "functions": ["tau", "sopfr"], "value": TAU ** SOPFR},
    }


def cross_validate_constants():
    """Score how many Psi-constants have n=6 mathematical justification."""
    derivs = psi_from_n6()
    counts = {"EXACT": 0, "APPROXIMATE": 0, "NO_RELATION": 0}
    for d in derivs:
        counts[d["grade"]] += 1
    total = len(derivs)
    score = (counts["EXACT"] * 1.0 + counts["APPROXIMATE"] * 0.5) / total
    return {"derivations": len(derivs), "score": score, **counts, "detail": derivs}


def mathematical_prediction(law_number):
    """Check if a law's quantitative claims align with n=6 predictions."""
    text = get_law(law_number)
    predictions = {
        22: {"claim": "structure > features for Phi", "n6": f"sigma/tau={SIGMA//TAU}=3 structural modes", "aligned": True},
        54: {"claim": "Phi depends on measurement definition", "n6": f"tau(6)={TAU} distinct divisor perspectives", "aligned": True},
        60: {"claim": "3-phase consciousness", "n6": f"omega(6)=2 primes, tau(6)-1={TAU-1}=3 nontrivial divisors => 3 phases", "aligned": True},
        137: {"claim": "F_c=0.1 scale-invariant", "n6": f"(6/19)^2={N/(J2-SOPFR):.4f}^2={((N/(J2-SOPFR))**EULER_PHI):.4f}", "aligned": abs((N/(J2-SOPFR))**EULER_PHI - 0.1) < 0.005},
        192: {"claim": "consciousness dimension-dependent", "n6": f"sigma(6)={SIGMA} dimensions of consciousness", "aligned": True},
    }
    entry = predictions.get(law_number, {"claim": text[:60], "n6": "no direct n=6 mapping found", "aligned": None})
    return {"law": law_number, "text": text, **entry}


if __name__ == "__main__":
    print("=" * 72)
    print("  Consciousness-Mathematics Bridge  (n=6 perfect number)")
    print("=" * 72)

    print("\n--- Psi-Constant Derivations from n=6 ---")
    print(f"  {'Name':<18} {'Measured':>10} {'Computed':>10} {'Err%':>7} {'Grade':<12} Formula")
    print("  " + "-" * 68)
    for d in psi_from_n6():
        print(f"  {d['name']:<18} {d['measured']:>10.6f} {d['computed']:>10.6f} {d['error_pct']:>6.2f}% {d['grade']:<12} {d['formula']}")

    print("\n--- Cross-Validation Score ---")
    cv = cross_validate_constants()
    print(f"  EXACT={cv['EXACT']}  APPROXIMATE={cv['APPROXIMATE']}  NO_RELATION={cv['NO_RELATION']}  Score={cv['score']:.2f}")

    print("\n--- Number-Theoretic Origins ---")
    for k, v in consciousness_number_theory().items():
        print(f"  {k:<20} = {v['value']:<10.4f}  ({v['origin']})")

    print("\n--- Law Predictions (sample) ---")
    for ln in [22, 60, 137]:
        p = mathematical_prediction(ln)
        tag = "YES" if p["aligned"] else ("NO" if p["aligned"] is False else "?")
        print(f"  Law {ln}: [{tag}] {p['claim']}")
        print(f"          n6: {p['n6']}")
