#!/usr/bin/env python3
"""H-BIO-1: Codon = (tau, sigma/tau) — verification script."""

import math

print("=" * 70)
print("H-BIO-1: DNA Codons = (tau(6), sigma(6)/tau(6)) = (4, 3)")
print("=" * 70)

sigma_6 = 12
tau_6 = 4
sigma_over_tau = sigma_6 // tau_6  # 3

print(f"\nPerfect number 6: sigma={sigma_6}, tau={tau_6}, sigma/tau={sigma_over_tau}")
print(f"DNA: 4 bases (A,T,G,C), 3 bases per codon")
print(f"Claim: (bases, codon_length) = (tau(6), sigma(6)/tau(6)) = ({tau_6}, {sigma_over_tau})")

# --- Check 1: Information content ---
print("\n" + "-" * 50)
print("CHECK 1: Information content of codons")
print("-" * 50)
bases = 4
codon_len = 3
total_codons = bases ** codon_len
bits_per_position = math.log2(bases)
total_bits = codon_len * bits_per_position

print(f"Bases: {bases}")
print(f"Codon length: {codon_len}")
print(f"Total codons: {bases}^{codon_len} = {total_codons}")
print(f"Bits per position: log2({bases}) = {bits_per_position}")
print(f"Total bits: {codon_len} x {bits_per_position} = {total_bits}")
print(f"Note: {total_bits} bits = sigma(6)/2 = {sigma_6}/2. Coincidence.")

# --- Check 2: Alternative encodings ---
print("\n" + "-" * 50)
print("CHECK 2: Alternative encodings for ~64 codons (6 bits)")
print("-" * 50)
print(f"Constraint: b^k = 2^6 = 64 (need 6 bits to encode 20 amino acids + stops)")
print()
print(f"{'b (bases)':>10} | {'k (length)':>10} | {'b^k':>6} | {'|b-k|':>6} | {'bits':>5} | {'Assessment':<30}")
print("-" * 80)

# All factorizations of 64 = 2^6
solutions = []
for k in range(1, 7):
    b = round(64 ** (1/k))
    if b ** k == 64:
        solutions.append((b, k))

# Also add non-power-of-2 options for comparison
alt_options = [
    (2, 6, "binary"),
    (4, 3, "DNA (actual)"),
    (8, 2, "octal"),
    (64, 1, "direct lookup"),
    (3, 4, "ternary alternative"),
    (5, 3, "pentary"),
    (6, 3, "hexary"),
    (3, 3, "ternary short"),
]

for b, k, label in alt_options:
    codons = b ** k
    balance = abs(b - k)
    bits = k * math.log2(b)
    enough = "YES" if codons >= 20 else "NO (too few)"
    if codons < 20:
        assessment = f"Only {codons} codons, need >=20"
    elif codons > 200:
        assessment = f"Wasteful: {codons} codons"
    else:
        assessment = f"{codons} codons, balance={balance}"
    if label == "DNA (actual)":
        assessment += " <-- ACTUAL"
    print(f"{b:>10} | {k:>10} | {codons:>6} | {balance:>6} | {bits:>5.1f} | {assessment:<30}")

# --- Check 3: Balance metric analysis ---
print("\n" + "-" * 50)
print("CHECK 3: Balance metric for b^k >= 20 (minimum for amino acids)")
print("-" * 50)
print("Question: Is (4,3) optimal by some metric?")
print()

candidates = []
for b in range(2, 65):
    for k in range(1, 20):
        codons = b ** k
        if 20 <= codons <= 256:  # reasonable range
            bits = k * math.log2(b)
            balance = abs(b - k)
            waste = codons - 20  # unused codons
            efficiency = 20 / codons  # fraction of codons used
            candidates.append((b, k, codons, bits, balance, waste, efficiency))

# Sort by balance (|b-k|), then by total bits
candidates.sort(key=lambda x: (x[4], x[3]))

print(f"{'b':>4} | {'k':>4} | {'b^k':>6} | {'bits':>5} | {'|b-k|':>6} | {'waste':>6} | {'eff%':>6} | {'Notes':<20}")
print("-" * 75)
for b, k, codons, bits, balance, waste, eff in candidates[:20]:
    notes = ""
    if (b, k) == (4, 3):
        notes = "<-- DNA (tau, sigma/tau)"
    elif (b, k) == (3, 4):
        notes = "(sigma/tau, tau) swapped"
    elif (b, k) == (5, 3):
        notes = ""
    elif (b, k) == (3, 3):
        notes = "27 codons"
    print(f"{b:>4} | {k:>4} | {codons:>6} | {bits:>5.1f} | {balance:>6} | {waste:>6} | {eff*100:>5.1f}% | {notes:<20}")

# --- Check 4: Why exactly 4 bases? Chemical constraints ---
print("\n" + "-" * 50)
print("CHECK 4: Chemical constraints on base count")
print("-" * 50)
print("""
Chemical reality constrains b (number of bases):
  - Bases pair via hydrogen bonds: A-T (2 bonds), G-C (3 bonds)
  - Watson-Crick pairing requires complementary pairs: b must be EVEN
  - 2 bases: only 1 pair, too little information per position
  - 4 bases: 2 pairs (purine-pyrimidine), 2 bits/position -- SWEET SPOT
  - 6 bases: 3 pairs possible but stereochemistry becomes difficult
  - 8 bases: synthetic biology has achieved this (hachimoji DNA) but
    error rates increase significantly

Key insight: b=4 is constrained by CHEMISTRY (H-bond geometry),
not by information theory alone. The codon length k=3 then follows
from needing b^k >= 20 amino acids: 4^2=16 (too few), 4^3=64 (works).
""")

# --- Check 5: Is (tau, sigma/tau) meaningful? ---
print("-" * 50)
print("CHECK 5: Is the (tau(6), sigma(6)/tau(6)) connection meaningful?")
print("-" * 50)
print(f"""
The claim: DNA uses (4 bases, 3 per codon) = (tau(6), sigma(6)/tau(6))

Counter-arguments:
  1. b=4 is chemically constrained (H-bond pairs), not chosen by math
  2. k=3 follows from b=4 + need for >=20 amino acids: 4^2=16<20, 4^3=64>=20
  3. tau(6)=4 and sigma(6)/tau(6)=3 are EXTREMELY common small integers
  4. Any pair (a,b) where a,b in {{2,3,4,5}} has ~15 possible "connections"
     to number theory. Finding one that matches is not surprising.

Pro-arguments:
  1. (4,3) IS the most balanced factorization of 64=2^6 (|b-k|=1, minimum)
  2. The total information is 6 bits = the perfect number itself
  3. 64 = 2^6 codons, and 6 is the first perfect number

Texas Sharpshooter analysis:
  - Number of small integer pairs in biology: ~20 (base pairs, codon length,
    amino acids, chromosome pairs, etc.)
  - Number of functions of 6 giving small integers: ~10 (tau, sigma, sigma/tau,
    phi, divisors, etc.)
  - Expected random matches: 20 x 10 x P(match) ~ 20 x 10 x 0.1 = 20
  - Finding 1 match among 200 tries: p ~ 1.0 (certain!)
""")

# --- Significance Assessment ---
print("=" * 70)
print("SIGNIFICANCE ASSESSMENT: H-BIO-1")
print("=" * 70)

assessments = [
    ("(4,3) = (tau, sigma/tau)", "True, but trivial small numbers", "p > 0.5", "white"),
    ("4^3=64, 6 bits = perfect number", "True, but 6 bits is standard CS unit", "p ~ 0.3", "white"),
    ("(4,3) most balanced for 2^6", "TRUE and INTERESTING", "p ~ 0.05", "yellow"),
    ("b=4 from chemistry, k=3 forced", "Correct causal explanation", "N/A", "established"),
    ("Overall (tau,sigma/tau) connection", "Numerological coincidence", "p > 0.2", "white"),
]

print(f"{'Claim':<35} | {'Verdict':<35} | {'p-value':<10} | {'Grade':<12}")
print("-" * 95)
for claim, verdict, pval, grade in assessments:
    print(f"{claim:<35} | {verdict:<35} | {pval:<10} | {grade:<12}")

print()
print("OVERALL VERDICT: H-BIO-1")
print("  The REAL reason for (4,3) is chemistry + combinatorics:")
print("    - 4 bases: hydrogen bond geometry forces paired bases (b even, b=4 sweet spot)")
print("    - 3 per codon: 4^2=16 < 20 amino acids, so k=3 is forced")
print("  The (tau, sigma/tau) mapping is a post-hoc numerological coincidence.")
print("  The only mildly interesting fact: (4,3) minimizes |b-k| for b^k=64.")
print("  Grade: white circle (coincidence with known causal explanation)")
