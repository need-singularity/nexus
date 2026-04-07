#!/usr/bin/env python3
"""
Verify H-STAT-1: Chi-Squared(k) Quadruple Moment Match.

For chi^2(k):
  mean = k
  variance = 2k
  mode = k-2 (for k >= 2)
  excess kurtosis = 12/k

We check: for which k do ALL of:
  mean = k = some arithmetic function of k (trivially true)
  variance = 2k = sigma(k)  [divisor sum]
  mode = k-2 = tau(k)       [number of divisors]
  excess kurtosis = 12/k = phi(k)  [Euler totient]
"""

from sympy import divisor_sigma, divisor_count, totient
from fractions import Fraction

def check_chi2_quadruple(k):
    """Check if chi^2(k) has all 4 moments matching arithmetic functions."""
    if k < 2:
        return False, {}

    mean = k
    var = 2 * k
    mode = k - 2
    kurt = Fraction(12, k)

    sig = divisor_sigma(k)      # sigma(k)
    tau = divisor_count(k)      # tau(k)
    phi = totient(k)            # phi(k)

    match_var = (var == sig)
    match_mode = (mode == tau)
    match_kurt = (kurt == phi)

    return (match_var and match_mode and match_kurt), {
        'k': k,
        'var': var, 'sigma': sig, 'match_var': match_var,
        'mode': mode, 'tau': tau, 'match_mode': match_mode,
        'kurt': kurt, 'phi': phi, 'match_kurt': match_kurt,
    }

print("=" * 70)
print("H-STAT-1 Verification: Chi-Squared Quadruple Moment Match")
print("=" * 70)

# Check perfect numbers specifically
perfect_numbers = [6, 28, 496, 8128]
print("\n--- Perfect Numbers ---")
for n in perfect_numbers:
    ok, info = check_chi2_quadruple(n)
    print(f"  k={n}: sigma={info['sigma']} (need {info['var']}), "
          f"tau={info['tau']} (need {info['mode']}), "
          f"phi={info['phi']} (need {info['kurt']})")
    print(f"    var={'YES' if info['match_var'] else 'NO'}, "
          f"mode={'YES' if info['match_mode'] else 'NO'}, "
          f"kurt={'YES' if info['match_kurt'] else 'NO'}")
    print(f"    ALL MATCH: {'YES ***' if ok else 'NO'}")

# Exhaustive search
print("\n--- Exhaustive search k=2..10000 ---")
solutions = []
for k in range(2, 10001):
    ok, info = check_chi2_quadruple(k)
    if ok:
        solutions.append(k)
        print(f"  FOUND: k={k}")

print(f"\nTotal solutions in [2, 10000]: {len(solutions)}")
print(f"Solutions: {solutions}")

# Also check which k satisfy at least 2 of 3 conditions
print("\n--- Partial matches (2 of 3) in [2, 1000] ---")
for k in range(2, 1001):
    ok, info = check_chi2_quadruple(k)
    count = sum([info['match_var'], info['match_mode'], info['match_kurt']])
    if count >= 2:
        print(f"  k={k}: {count}/3 matches "
              f"(var={info['match_var']}, mode={info['match_mode']}, kurt={info['match_kurt']})")

# Proof argument
print("\n--- Proof Argument ---")
print("Condition (3): phi(k) = 12/k requires k | 12 and phi(k) = 12/k.")
print("Divisors of 12: 1, 2, 3, 4, 6, 12")
print()
for k in [1, 2, 3, 4, 6, 12]:
    target_phi = Fraction(12, k)
    actual_phi = totient(k)
    sig = divisor_sigma(k)
    tau = divisor_count(k)
    print(f"  k={k}: phi({k})={actual_phi}, need {target_phi} -> {'YES' if actual_phi == target_phi else 'NO'}"
          f"  |  sigma={sig}, need {2*k} -> {'YES' if sig == 2*k else 'NO'}"
          f"  |  tau={tau}, need {k-2} -> {'YES' if tau == k-2 else 'NO'}")

print()
print("Condition (3) filters to k | 12.")
print("Condition (1) [sigma(k)=2k, perfect] filters to {6, 28, 496, ...}.")
print("Intersection of k | 12 and perfect numbers = {6}.")
print("Therefore k=6 is the UNIQUE solution. QED.")
