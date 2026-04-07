#!/usr/bin/env python3
"""H-CS-5: Graph coloring and the number 6 — verification script."""

import math
from itertools import combinations

print("=" * 70)
print("H-CS-5: Graph Coloring and the Number 6")
print("=" * 70)

# Perfect number 6 constants
sigma_6 = 12  # sum of divisors
tau_6 = 4     # number of divisors
sigma_over_tau = sigma_6 // tau_6  # = 3

print(f"\nPerfect number 6 constants: sigma(6)={sigma_6}, tau(6)={tau_6}, sigma/tau={sigma_over_tau}")

# --- Check 1: chi(K_6) = 6 ---
print("\n" + "-" * 50)
print("CHECK 1: chi(K_n) = n (chromatic number of complete graph)")
print("-" * 50)
print("By definition, K_n requires exactly n colors (every vertex adjacent to every other).")
print(f"chi(K_6) = 6 = first perfect number. Trivially true but tautological.")
print(f"chi(K_{{tau(6)}}) = chi(K_4) = 4 = tau(6). Also tautological.")

# --- Check 2: Petersen graph ---
print("\n" + "-" * 50)
print("CHECK 2: Petersen graph chromatic number")
print("-" * 50)
print(f"Petersen graph: chi = 3 (well-known, needs exactly 3 colors)")
print(f"sigma(6)/tau(6) = {sigma_6}/{tau_6} = {sigma_over_tau}")
print(f"Match: chi(Petersen) = 3 = sigma/tau? YES, but 3 is extremely common.")

# --- Check 3: Edge chromatic number of K_6 ---
print("\n" + "-" * 50)
print("CHECK 3: Edge chromatic index of K_n")
print("-" * 50)
print("By Vizing's theorem: Delta(G) <= chi'(G) <= Delta(G)+1")
print("For K_n: Delta = n-1")
print("  If n even: chi'(K_n) = n-1 (class 1)")
print("  If n odd:  chi'(K_n) = n   (class 2)")
print(f"\nchi'(K_6) = 6-1 = 5 (since 6 is even)")
print(f"Connection to 6: chi'(K_6) = 5 = 6-1. Not a deep connection.")

# --- Check 4-5-6: Ramsey numbers ---
print("\n" + "-" * 50)
print("CHECK 4-6: Ramsey numbers and R(3,3) = 6")
print("-" * 50)

# Known Ramsey numbers R(s,t) for small values
known_ramsey = {
    (2,2): 2, (2,3): 3, (2,4): 4, (2,5): 5, (2,6): 6, (2,7): 7, (2,8): 8, (2,9): 9,
    (3,3): 6, (3,4): 9, (3,5): 14, (3,6): 18, (3,7): 23, (3,8): 28, (3,9): 36,
    (4,4): 18, (4,5): 25,
}

print(f"R(3,3) = {known_ramsey[(3,3)]} = 6 (first perfect number)")
print(f"R(3,8) = {known_ramsey[(3,8)]} = 28 (second perfect number!)")
print()
print("This is REMARKABLE: R(3,3)=6 and R(3,8)=28 are both perfect numbers.")
print("But is it coincidence?")
print()

# Check: R(3,n) values
print("R(3,n) series:")
print(f"{'n':>4} | {'R(3,n)':>8} | {'Perfect?':>10} | {'sigma_-1':>10}")
print("-" * 45)
for n in range(3, 10):
    r = known_ramsey.get((3, n), "?")
    if isinstance(r, int):
        divs = [d for d in range(1, r+1) if r % d == 0]
        sigma = sum(divs)
        is_perfect = "YES" if sigma == 2*r else "no"
        sigma_ratio = sigma / r
    else:
        is_perfect = "?"
        sigma_ratio = "?"
    print(f"{n:>4} | {str(r):>8} | {str(is_perfect):>10} | {str(round(sigma_ratio,4) if isinstance(sigma_ratio,float) else sigma_ratio):>10}")

print()
print("R(3,3)=6 (perfect), R(3,8)=28 (perfect). Two out of 7 known values.")
print("Probability of 2 perfect numbers in 7 random integers [6..36]:")
# Perfect numbers in range: 6, 28. Out of 31 integers [6..36].
# P(exactly 2 in 7) with p=2/31
p_single = 2/31
from math import comb
p_2_of_7 = comb(7,2) * p_single**2 * (1-p_single)**5
print(f"p = C(7,2) * (2/31)^2 * (29/31)^5 = {p_2_of_7:.6f}")
print(f"This is about {p_2_of_7:.1%} — notable but not highly significant.")
print(f"Note: Ramsey numbers grow fast and only ~5 perfect numbers exist < 10^10.")
print(f"The R(3,8)=28 match is more interesting than R(3,3)=6 (since 6 is small).")

# --- Table: K_n properties for n=2..20 ---
print("\n" + "=" * 70)
print("COMPREHENSIVE TABLE: K_n for n=2..20")
print("=" * 70)
print(f"{'n':>4} | {'chi(Kn)':>8} | {'chi_edge':>9} | {'|E|':>6} | {'R(n,n)':>12} | {'Notes':>20}")
print("-" * 70)

# Known diagonal Ramsey numbers R(n,n)
diagonal_ramsey = {
    2: 2, 3: 6, 4: 18, 5: "43-48"
}
# R(n,n) for n>=5 are only bounds

for n in range(2, 21):
    chi = n
    chi_edge = n - 1 if n % 2 == 0 else n
    edges = n * (n - 1) // 2
    r_nn = diagonal_ramsey.get(n, "unknown")

    notes = ""
    if n == 6:
        notes = "PERFECT NUMBER"
    elif n == 4:
        notes = "tau(6)"
    elif n == 12:
        notes = "sigma(6)"
    elif n == 3:
        notes = "sigma/tau"
    elif n == 28:
        notes = "2nd perfect"

    print(f"{n:>4} | {chi:>8} | {chi_edge:>9} | {edges:>6} | {str(r_nn):>12} | {notes:>20}")

# --- Significance Assessment ---
print("\n" + "=" * 70)
print("SIGNIFICANCE ASSESSMENT")
print("=" * 70)

assessments = [
    ("chi(K_6) = 6", "Tautological", "N/A", "white"),
    ("chi(Petersen) = 3 = sigma/tau", "True but 3 is common", "p ~ 0.3", "white"),
    ("chi'(K_6) = 5 = 6-1", "Trivial (Vizing)", "N/A", "white"),
    ("R(3,3) = 6 (perfect)", "True, but 6 is small", "p ~ 0.15", "white/yellow"),
    ("R(3,8) = 28 (perfect)", "Notable coincidence", "p ~ 0.06", "yellow"),
    ("Two R(3,n) = perfect", "Interesting pattern", "p ~ 0.06", "yellow"),
]

print(f"{'Claim':<35} | {'Verdict':<25} | {'p-value':<10} | {'Grade':<15}")
print("-" * 90)
for claim, verdict, pval, grade in assessments:
    print(f"{claim:<35} | {verdict:<25} | {pval:<10} | {grade:<15}")

print()
print("OVERALL VERDICT: H-CS-5")
print("  Most connections are tautological or trivial (white circle).")
print("  The R(3,3)=6, R(3,8)=28 coincidence with perfect numbers is mildly interesting")
print("  but likely a Small Number effect. No deep structural connection established.")
print("  Grade: white circle (trivial/coincidental)")
