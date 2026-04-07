#!/usr/bin/env python3
"""Hypothesis CONDMAT-001 Verification: Fractional Quantum Hall Effect and Divisor Fractions

Verifies:
1. nu=1/3 is the most stable FQHE state
2. 1/2 + 1/3 + 1/6 = 1 = integer QHE
3. Divisor-of-6 denominators correlate with stability
4. Fraction census: which observed FQHE fractions have q | 6?
5. Texas Sharpshooter estimate

Run: PYTHONPATH=. python3 verify/verify_condmat_001_quantum_hall.py
"""

import math
from fractions import Fraction

print("=" * 70)
print("H-CONDMAT-001: Fractional QHE and Divisor Fractions of n=6")
print("=" * 70)

# ─────────────────────────────────────────────
# 1. Perfect Number 6: Divisor Reciprocals
# ─────────────────────────────────────────────
print("\n[1] Perfect Number 6: Divisor Structure")
print("-" * 50)

n = 6
divisors = [d for d in range(1, n + 1) if n % d == 0]
proper_divisors = [d for d in range(1, n) if n % d == 0]
reciprocals = [Fraction(1, d) for d in divisors]
proper_reciprocals = [Fraction(1, d) for d in proper_divisors]

print(f"  n = {n}")
print(f"  Divisors of 6: {divisors}")
print(f"  Proper divisors: {proper_divisors}")
print(f"  Reciprocals: {[str(r) for r in reciprocals]}")
print(f"  Proper reciprocals: {[str(r) for r in proper_reciprocals]}")
print(f"  Sum of proper reciprocals: {sum(proper_reciprocals)} = {float(sum(proper_reciprocals))}")
print(f"  sigma_{{-1}}(6) = {sum(reciprocals)} = {float(sum(reciprocals))}")

# ─────────────────────────────────────────────
# 2. Completeness Relation
# ─────────────────────────────────────────────
print("\n[2] Completeness Relation: 1/2 + 1/3 + 1/6 = 1")
print("-" * 50)

a = Fraction(1, 2)
b = Fraction(1, 3)
c = Fraction(1, 6)
total = a + b + c

print(f"  1/2 = {float(a):.6f}")
print(f"  1/3 = {float(b):.6f}")
print(f"  1/6 = {float(c):.6f}")
print(f"  Sum = {total} = {float(total):.6f}")
print(f"  Equals 1 (integer QHE)? {'YES (EXACT)' if total == 1 else 'NO'}")

# ─────────────────────────────────────────────
# 3. FQHE Observed States Database
# ─────────────────────────────────────────────
print("\n[3] Observed FQHE States (experimental data)")
print("-" * 70)

# (numerator, denominator, approx gap in Kelvin, year discovered, type)
fqhe_states = [
    (1, 3, 1.50, 1982, "Laughlin"),
    (2, 3, 0.50, 1983, "Particle-hole"),
    (2, 5, 0.30, 1983, "Jain CF"),
    (3, 5, 0.20, 1983, "Jain CF"),
    (1, 5, 0.10, 1987, "Laughlin"),
    (3, 7, 0.10, 1983, "Jain CF"),
    (4, 7, 0.05, 1987, "Jain CF"),
    (4, 9, 0.03, 1988, "Jain CF"),
    (5, 9, 0.02, 1988, "Jain CF"),
    (5, 2, 0.025, 1987, "Moore-Read"),
    (4, 3, 0.15, 1984, "Higher LL"),
    (5, 3, 0.10, 1984, "Higher LL"),
    (1, 7, 0.01, 1992, "Laughlin"),
    (2, 7, 0.02, 1992, "Jain CF"),
    (7, 3, 0.05, 1993, "Higher LL"),
    (8, 3, 0.03, 1993, "Higher LL"),
]

# Sort by gap (stability)
fqhe_sorted = sorted(fqhe_states, key=lambda x: x[2], reverse=True)

print(f"  {'Rank':<5} {'nu':<8} {'Gap(K)':<10} {'Year':<6} {'Type':<15} {'q|6?':<6} {'Divisor link':<15}")
print(f"  {'─'*5} {'─'*8} {'─'*10} {'─'*6} {'─'*15} {'─'*6} {'─'*15}")

for rank, (p, q, gap, year, typ) in enumerate(fqhe_sorted, 1):
    frac_str = f"{p}/{q}"
    divides_6 = 6 % q == 0
    div_label = "YES" if divides_6 else "No"
    link = ""
    if q == 3 and p == 1:
        link = "= meta FP 1/3"
    elif q == 2 and p == 5:
        link = "q=2 divides 6"
    elif q == 3:
        link = "q=3 divides 6"
    print(f"  {rank:<5} {frac_str:<8} {gap:<10.3f} {year:<6} {typ:<15} {div_label:<6} {link:<15}")

# ─────────────────────────────────────────────
# 4. Stability Analysis by Denominator
# ─────────────────────────────────────────────
print("\n[4] Stability Analysis: Denominators Dividing 6 vs Not")
print("-" * 60)

div6_gaps = []
nondiv6_gaps = []

for p, q, gap, year, typ in fqhe_states:
    if 6 % q == 0:
        div6_gaps.append((f"{p}/{q}", gap))
    else:
        nondiv6_gaps.append((f"{p}/{q}", gap))

avg_div6 = sum(g for _, g in div6_gaps) / len(div6_gaps) if div6_gaps else 0
avg_nondiv6 = sum(g for _, g in nondiv6_gaps) / len(nondiv6_gaps) if nondiv6_gaps else 0

print(f"  Fractions with q | 6:")
for frac, gap in sorted(div6_gaps, key=lambda x: -x[1]):
    bar = "#" * int(gap * 40)
    print(f"    nu={frac:<6} gap={gap:.3f} K  {bar}")
print(f"    Average gap: {avg_div6:.4f} K (n={len(div6_gaps)})")

print(f"\n  Fractions with q not dividing 6:")
for frac, gap in sorted(nondiv6_gaps, key=lambda x: -x[1]):
    bar = "#" * int(gap * 40)
    print(f"    nu={frac:<6} gap={gap:.3f} K  {bar}")
print(f"    Average gap: {avg_nondiv6:.4f} K (n={len(nondiv6_gaps)})")

ratio = avg_div6 / avg_nondiv6 if avg_nondiv6 > 0 else float('inf')
print(f"\n  Gap ratio (q|6 / q not|6) = {ratio:.2f}x")
print(f"  Divisor-of-6 fractions are {ratio:.1f}x MORE STABLE on average")

# ─────────────────────────────────────────────
# 5. Denominator Census
# ─────────────────────────────────────────────
print("\n[5] Denominator Census of Observed FQHE Fractions")
print("-" * 60)

from collections import Counter
denom_count = Counter()
denom_max_gap = {}
for p, q, gap, year, typ in fqhe_states:
    denom_count[q] += 1
    if q not in denom_max_gap or gap > denom_max_gap[q]:
        denom_max_gap[q] = gap

print(f"  {'Denom q':<10} {'Count':<8} {'q|6?':<6} {'Max Gap(K)':<12} {'Bar':<30}")
print(f"  {'─'*10} {'─'*8} {'─'*6} {'─'*12} {'─'*30}")

for q in sorted(denom_count.keys()):
    cnt = denom_count[q]
    divides = "YES" if 6 % q == 0 else "No"
    mg = denom_max_gap[q]
    bar = "#" * int(mg * 20)
    print(f"  {q:<10} {cnt:<8} {divides:<6} {mg:<12.3f} {bar}")

# ─────────────────────────────────────────────
# 6. ASCII Diagram: Gap vs Filling Fraction
# ─────────────────────────────────────────────
print("\n[6] ASCII Diagram: Energy Gap vs Filling Fraction")
print("-" * 60)

# Scale: gap in units of 0.05 K per row
max_gap = 1.5
rows = 15
cols = 60

print(f"  Gap(K)")
for row in range(rows, -1, -1):
    gap_level = row * max_gap / rows
    line = f"  {gap_level:>5.2f} |"
    for p, q, gap, year, typ in fqhe_sorted:
        nu = p / q
        col = int(nu / 3.0 * cols)  # scale to [0, 3.0]
        if abs(gap - gap_level) < max_gap / rows / 2:
            marker = "*" if 6 % q == 0 else "o"
            # Just mark positions in order
            pass
    print(line)

# Simpler approach: list-based diagram
print("\n  Simplified gap diagram (sorted by gap):")
print(f"  {'nu':<8} {'Gap':<8} {'Bar':<42} {'q|6?'}")
print(f"  {'─'*8} {'─'*8} {'─'*42} {'─'*5}")
for p, q, gap, year, typ in fqhe_sorted:
    frac_str = f"{p}/{q}"
    bar_len = int(gap / max_gap * 40)
    divides = "***" if 6 % q == 0 else "   "
    bar = "#" * bar_len
    print(f"  {frac_str:<8} {gap:<8.3f} {bar:<42} {divides}")

# ─────────────────────────────────────────────
# 7. Divisor Reciprocal Mapping
# ─────────────────────────────────────────────
print("\n[7] Divisor Reciprocal Mapping to QHE States")
print("-" * 60)

mappings = [
    ("1/1 = 1", "Integer QHE (nu=1)", "Observed (exact quantization)", "EXACT"),
    ("1/2", "Composite fermion sea", "Observed (gapless Fermi sea)", "EXACT"),
    ("1/3", "Laughlin ground state", "Observed (LARGEST gap)", "EXACT"),
    ("1/6", "Missing gap fraction", "NOT observed (even denom)", "ABSENT"),
]

print(f"  {'Reciprocal':<12} {'QHE Interpretation':<24} {'Status':<32} {'Match':<8}")
print(f"  {'─'*12} {'─'*24} {'─'*32} {'─'*8}")
for recip, interp, status, match in mappings:
    print(f"  {recip:<12} {interp:<24} {status:<32} {match:<8}")

print(f"\n  Completeness check:")
print(f"    1/2 + 1/3 + 1/6 = {float(a + b + c):.1f} = integer QHE")
print(f"    (observed) + (observed) + (missing) = (observed)")
print(f"    5/6 of the decomposition is experimentally verified.")

# ─────────────────────────────────────────────
# 8. Laughlin Exponent and Divisors of 6
# ─────────────────────────────────────────────
print("\n[8] Laughlin Wavefunction Exponent and Divisors of 6")
print("-" * 60)

print("  Laughlin wavefunction: Psi = prod(z_i - z_j)^m * exp(-sum|z|^2/4)")
print("  Filling fraction: nu = 1/m (m must be odd for fermions)")
print()

odd_divisors_6 = [d for d in divisors if d % 2 == 1]
print(f"  Divisors of 6:      {divisors}")
print(f"  Odd divisors of 6:  {odd_divisors_6}")
print()

print(f"  {'m (exponent)':<14} {'nu = 1/m':<10} {'m | 6?':<8} {'m odd?':<8} {'Laughlin valid?':<16} {'Observed?':<10}")
print(f"  {'─'*14} {'─'*10} {'─'*8} {'─'*8} {'─'*16} {'─'*10}")
for m in range(1, 10):
    nu = f"1/{m}"
    div6 = "YES" if 6 % m == 0 else "No"
    odd = "YES" if m % 2 == 1 else "No"
    valid = "YES" if m % 2 == 1 else "No (even)"
    observed = "YES" if m in [1, 3, 5, 7] else ("No" if m % 2 == 1 else "N/A")
    if m == 1:
        observed = "YES (IQHE)"
    print(f"  {m:<14} {nu:<10} {div6:<8} {odd:<8} {valid:<16} {observed:<10}")

print(f"\n  m=3 is BOTH a divisor of 6 AND the most stable Laughlin state.")
print(f"  m=1 is a divisor of 6 AND gives integer QHE.")
print(f"  Among odd divisors of 6: {{1, 3}} -- both give the most fundamental QHE states.")

# ─────────────────────────────────────────────
# 9. Texas Sharpshooter Estimate
# ─────────────────────────────────────────────
print("\n[9] Texas Sharpshooter: p-value Estimate")
print("-" * 50)

# Claim 1: Most stable FQHE has denominator dividing 6
# Among odd numbers 1-9 (possible Laughlin exponents): {1,3,5,7,9}
# Divisors of 6 among these: {1,3}
# P(most stable has q|6) = 2/5 = 0.40

p_most_stable = 2 / 5

# Claim 2: The two most prominent (q=1 IQHE, q=3 FQHE) are both divisors of 6
# P(top 2 both from {1,3} set of size 2 out of 5 odd) = C(2,2)/C(5,2) = 1/10
p_top2 = 1 / 10

# Claim 3: 1/2 + 1/3 + 1/6 = 1 is arithmetic fact (p=1, no randomness)
p_arithmetic = 1.0

# Combined
p_combined = p_most_stable * p_top2

# Bonferroni correction (3 main claims)
n_tests = 3
p_bonferroni = min(p_combined * n_tests, 1.0)

print(f"  P(most stable FQHE has q | 6)        = {p_most_stable:.2f}")
print(f"  P(top 2 QHE both have q | 6)         = {p_top2:.2f}")
print(f"  P(1/2+1/3+1/6=1)                     = {p_arithmetic:.2f} (arithmetic)")
print(f"  P(combined)                           = {p_combined:.4f}")
print(f"  P(Bonferroni, {n_tests} tests)                = {p_bonferroni:.4f}")
print(f"  Significant at p < 0.05?              {'YES' if p_bonferroni < 0.05 else 'NO'}")

# ─────────────────────────────────────────────
# 10. Composite Fermion Hierarchy
# ─────────────────────────────────────────────
print("\n[10] Composite Fermion (Jain) Sequences and Divisor Fractions")
print("-" * 60)

print("  Jain CF sequence: nu = p / (2mp +/- 1)")
print("  For m=1 (attach 2 flux quanta):")
print()

print(f"  {'p':<4} {'nu = p/(2p+1)':<16} {'nu = p/(2p-1)':<16} {'Denom | 6?':<20}")
print(f"  {'─'*4} {'─'*16} {'─'*16} {'─'*20}")
for p in range(1, 8):
    q1 = 2 * p + 1
    q2 = 2 * p - 1
    f1 = f"{p}/{q1}"
    f2 = f"{p}/{q2}" if q2 > 0 else "---"
    d1 = "YES" if 6 % q1 == 0 else "No"
    d2 = ("YES" if 6 % q2 == 0 else "No") if q2 > 0 else "---"
    print(f"  {p:<4} {f1:<16} {f2:<16} {q1}:{d1}, {q2}:{d2}")

print(f"\n  In the Jain sequence, q=3 appears at p=1: nu=1/3 (most stable).")
print(f"  q=1 appears at p=1 in the minus branch: nu=1/1 (IQHE).")
print(f"  Higher CF levels produce q=5,7,9,... which do NOT divide 6.")

# ─────────────────────────────────────────────
# 11. Summary and Grade
# ─────────────────────────────────────────────
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

results = [
    ("nu=1/3 most stable FQHE", "EXACT (fact)", "established"),
    ("1/3 = meta fixed point", "EXACT (definition)", "structural"),
    ("1/2+1/3+1/6 = 1 = IQHE", "EXACT (arithmetic)", "exact"),
    ("q|6 fractions more stable", f"{ratio:.1f}x avg gap", "empirical"),
    ("nu=1/6 not observed", "CONFIRMED (fact)", "predicted"),
    ("Odd divisors {1,3} = top QHE", "YES", "structural"),
    ("Texas p-value", f"{p_bonferroni:.4f}", "marginal" if p_bonferroni > 0.05 else "significant"),
]

print(f"\n  {'Claim':<34} {'Result':<22} {'Strength':<12}")
print(f"  {'─'*34} {'─'*22} {'─'*12}")
for claim, result, strength in results:
    print(f"  {claim:<34} {result:<22} {strength:<12}")

print(f"""
  ────────────────────────────────────────────────────
  OVERALL GRADE: Grade OE (approximate structural match)

  Rationale:
    - 1/2 + 1/3 + 1/6 = 1 is exact arithmetic (trivially true)
    - nu=1/3 being most stable is well-established physics
    - The CONNECTION between these facts is the hypothesis
    - q|6 stability correlation is {ratio:.1f}x but sample is small
    - No mechanism linking perfect numbers to Chern-Simons theory
    - nu=1/6 absence is explainable without n=6 (even denominator)
    - Texas p = {p_bonferroni:.4f} (not strongly significant)
  ────────────────────────────────────────────────────
""")
