#!/usr/bin/env python3
"""H-TOP-2: Euler characteristic chi(M) = 6 — which spaces realize it?"""

import math
from itertools import product as iprod

print("=" * 70)
print("H-TOP-2: Euler Characteristic chi(M) = 6")
print("=" * 70)

# Perfect number 6 constants
sigma_6 = 12
tau_6 = 4
phi_6 = 2

print("\n## Known Euler characteristics of standard spaces")
print()

spaces = [
    ("S^n (n-sphere)", {
        0: 2, 1: 0, 2: 2, 3: 0, 4: 2, 5: 0, 6: 2, 7: 0, 8: 2
    }),
    ("CP^n (complex proj)", {
        0: 1, 1: 2, 2: 3, 3: 4, 4: 5
    }),
    ("RP^n (real proj)", {
        0: 1, 1: 0, 2: 1, 3: 0, 4: 1, 5: 0, 6: 1
    }),
    ("T^n (torus)", {
        0: 1, 1: 0, 2: 0, 3: 0, 4: 0
    }),
    ("Sigma_g (genus g surface)", {
        0: 2, 1: 0, 2: -2, 3: -4, 4: -6
    }),
]

print("| Space | n or g | chi | Notes |")
print("|---|---|---|---|")
for name, vals in spaces:
    for n, chi in sorted(vals.items()):
        note = ""
        if chi == 6:
            note = "CHI=6!"
        elif chi == 12:
            note = "sigma(6)"
        elif chi == 4:
            note = "tau(6)"
        elif chi == 2:
            note = "phi(6)"
        elif chi == 3:
            note = "sigma/tau"
        print(f"| {name} | {n} | {chi} | {note} |")

# Product manifolds: chi is multiplicative
print("\n## Product manifolds with chi = 6")
print("  chi(M x N) = chi(M) * chi(N)")
print("  6 = 2 * 3 = 1 * 6 = 6 * 1")
print()

# Catalog of small chi values and their spaces
chi_catalog = {
    0: ["T^2", "S^1", "T^n (any n>=1)", "Klein bottle"],
    1: ["point", "RP^2", "RP^(2k)"],
    2: ["S^2", "S^(2k)", "CP^1"],
    3: ["CP^2"],
    4: ["CP^3", "S^2 x S^2"],  # CP^3 has chi=4
    5: ["CP^4"],
    6: [],  # what we're looking for
    -1: ["RP^2 # RP^2 # RP^2 (3 cross-caps)"],
    -2: ["Sigma_2 (genus 2)"],
}

# Actually let me be more careful
# CP^n has chi = n+1
# S^2 has chi = 2
# S^2 x S^2 has chi = 4

print("### Factorizations of 6")
print("  6 = 2 x 3:")
print("    chi(S^2) = 2, chi(CP^2) = 3")
print("    => chi(S^2 x CP^2) = 6  ✓")
print()
print("  6 = 1 x 6:")
print("    chi(pt) = 1, need chi(M) = 6")
print("    chi(CP^5) = 6  ✓")
print()
print("  6 = 2 x 3 = chi(S^2) x chi(CP^2)")
print("  6 = 1 x 2 x 3 = chi(pt) x chi(S^2) x chi(CP^2)")
print("  6 = 6 = chi(CP^5)")

# Verify CP^5
print("\n### Verification: CP^5")
print(f"  CP^n has Betti numbers b_k = 1 for k=0,2,4,...,2n and 0 otherwise")
print(f"  CP^5: b_0=1, b_2=1, b_4=1, b_6=1, b_8=1, b_10=1")
print(f"  chi(CP^5) = 1+1+1+1+1+1 = 6  ✓")
cp5_betti = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
chi_cp5 = sum((-1)**k * b for k, b in enumerate(cp5_betti))
print(f"  Computed: chi = sum(-1)^k * b_k = {chi_cp5}")

print("\n### Verification: S^2 x CP^2")
s2_betti = [1, 0, 1]  # b0, b1, b2
cp2_betti = [1, 0, 1, 0, 1]  # b0 through b4
# Product Betti: b_k(MxN) = sum_{i+j=k} b_i(M) * b_j(N)
dim_product = len(s2_betti) + len(cp2_betti) - 2
product_betti = [0] * (dim_product + 1)
for i, bi in enumerate(s2_betti):
    for j, bj in enumerate(cp2_betti):
        product_betti[i+j] += bi * bj

print(f"  S^2 Betti: {s2_betti}")
print(f"  CP^2 Betti: {cp2_betti}")
print(f"  S^2 x CP^2 Betti: {product_betti}")
chi_product = sum((-1)**k * b for k, b in enumerate(product_betti))
print(f"  chi(S^2 x CP^2) = {chi_product}")
assert chi_product == 6, f"Expected 6, got {chi_product}"
print(f"  Confirmed: chi = 6 ✓")

# More exotic: wedge sums
print("\n## Wedge sums and CW complexes")
print("  chi(X v Y) = chi(X) + chi(Y) - 1 (for connected, by inclusion-exclusion)")
print()
print("  chi(S^2 v S^2) = 2 + 2 - 1 = 3")
print("  chi(S^2 v S^2 v S^2) = 2 + 2 + 2 - 2 = 4")
# More generally: chi(S^2 v ... v S^2, k copies) = 2k - (k-1) = k+1
print("  chi(S^2 v S^2 v S^2 v S^2 v S^2) = 5*2 - 4 = 6")
print("  So 5 copies of S^2 wedged gives chi=6")
print()
print("  Alternatively: wedge of spheres")
for n_spheres in range(1, 8):
    chi_wedge = n_spheres + 1
    if chi_wedge == 6:
        print(f"  {n_spheres} copies of S^2 wedged: chi = {chi_wedge} = 6 ✓")

# Non-orientable surfaces
print("\n## Non-orientable surfaces")
print("  Connected sum of k copies of RP^2: chi = 2 - k")
for k in range(1, 8):
    chi_k = 2 - k
    print(f"  #{k} RP^2: chi = {chi_k}", end="")
    if chi_k in [6, -6, 12, 4, 2, 3]:
        print(f"  <-- match!")
    else:
        print()

# Orbifolds
print("\n## Orbifolds with chi = 6")
print("  Orbifold Euler characteristic: chi_orb = chi(M) / |G|")
print("  Or: chi(M/G) = chi(M) / |G| for free actions")
print()
print("  S^2 with 3 cone points of order 2:")
print("    chi_orb = 2 - 3(1 - 1/2) = 2 - 3/2 = 1/2")
print()
print("  To get chi_orb = 6 from S^2:")
print("    Need to ADD positive curvature at cone points")
print("    chi_orb(S^2; n1,...,nk) = 2 + sum(1/ni - 1)")
print("    = 2 - k + sum(1/ni)")
print("    For chi_orb = 6: sum(1/ni) = 4 + k")
print("    This requires 1/ni > 1, impossible for ni >= 1")
print("    => No orbifold of S^2 has chi_orb = 6")
print()
print("  HOWEVER: higher-dimensional orbifolds can!")
print("  chi(CP^5 / Z_1) = chi(CP^5) = 6 (trivial)")

# The key structural analysis
print("\n" + "=" * 70)
print("## Structural Analysis: Why chi=6 is special")
print("=" * 70)

print("""
  chi=6 is realized by:

  1. CP^5 (complex projective 5-space)
     - dim_R = 10, dim_C = 5
     - 5 = sigma(6)/tau(6) + phi(6) = 3 + 2
     - 6 Betti numbers all equal to 1
     - Simplest space with chi=6

  2. S^2 x CP^2 (product of 2-sphere and complex projective plane)
     - chi = 2 x 3 = 6
     - 2 = phi(6), 3 = sigma(6)/tau(6)
     - Product structure mirrors 6 = 2 x 3

  3. CP^2 x CP^2 x CP^2 (triple product) — NO!
     - chi = 3^3 = 27, not 6

  4. S^2 x S^2 x S^2 (triple product of spheres) — NO!
     - chi = 2^3 = 8, not 6

  KEY OBSERVATION: 6 = 2 x 3 as product of chi values
  perfectly mirrors 6 = 2 x 3 as prime factorization.

  chi is multiplicative under products, and the UNIQUE factorization
  6 = 2 x 3 = chi(S^2) x chi(CP^2)
  maps the number theory of 6 to topology via the product construction.
""")

# Check all chi values achievable by products of "basic" spaces
print("## Chi values of products of basic spaces (dim <= 10)")
basic = {
    "S^2": 2, "S^4": 2, "S^6": 2,
    "CP^1": 2, "CP^2": 3, "CP^3": 4, "CP^4": 5, "CP^5": 6,
    "T^2": 0,
    "RP^2": 1,
}

# Products of 2 spaces
print("\n### Two-fold products with chi=6:")
for (n1, c1), (n2, c2) in iprod(basic.items(), basic.items()):
    if c1 * c2 == 6 and n1 <= n2:
        print(f"  {n1} x {n2}: chi = {c1} x {c2} = 6")

# Connection to divisor structure
print("\n## Connection to divisor structure of 6")
print()
print("| Divisor d | sigma(6)/d | Topological realization | chi |")
print("|---|---|---|---|")
print("| 1 | 12 | point | 1 |")
print("| 2 | 6 | S^2 or CP^1 | 2 |")
print("| 3 | 4 | CP^2 | 3 |")
print("| 6 | 2 | CP^5 or S^2 x CP^2 | 6 |")

print("\n  Divisors of 6: {1, 2, 3, 6}")
print("  All divisors of 6 are realizable as chi of standard spaces!")
print("  1 = chi(pt), 2 = chi(S^2), 3 = chi(CP^2), 6 = chi(CP^5)")
print("  And the PRODUCTS work: chi(S^2) x chi(CP^2) = 2 x 3 = 6 = chi(S^2 x CP^2)")

# Verify the Betti number structure
print("\n## Full Betti number tables")
print("\n### CP^5 (dimension 10)")
for k in range(11):
    b = 1 if k % 2 == 0 else 0
    sign = "+" if (-1)**k > 0 else "-"
    print(f"  b_{k} = {b}  ({sign}{b})")
print(f"  chi = {sum(1 if k%2==0 else 0 for k in range(11))} - {0} = 6")

print("\n### S^2 x CP^2 (dimension 6)")
print(f"  Betti numbers: {product_betti}")
for k, b in enumerate(product_betti):
    sign = "+" if (-1)**k > 0 else "-"
    print(f"  b_{k} = {b}  ({sign}{b})")

# Significance
print("\n" + "=" * 70)
print("## Significance Assessment")
print("=" * 70)
print()
print("| Connection | Formula | Structural? | p-value est |")
print("|---|---|---|---|")
print("| 6 = chi(CP^5) | CP^n has chi=n+1 | YES (trivial) | 1.0 (by def) |")
print("| 6 = chi(S^2 x CP^2) | chi multiplicative | YES | ~0.1 |")
print("| 6 = 2 x 3 = chi x chi | prime factorization | YES (structural) | ~0.05 |")
print("| All div(6) are chi | 1,2,3,6 all realized | Moderate | ~0.02 |")
print("| CP^5: dim_C = 5 = 3+2 | sigma/tau + phi | Weak (small #) | ~0.2 |")
print("| Surface chi=6 impossible | 2-2g=6 => g=-2 | YES (topological) | N/A |")

print("""
## Texas Sharpshooter Analysis

  The multiplicativity chi(MxN) = chi(M)*chi(N) is a theorem.
  The fact that 6 = 2*3 is prime factorization is number theory.
  The matching chi(S^2)=2 and chi(CP^2)=3 follows from CP^n having chi=n+1.

  So: CP^(n-1) always has chi = n.
  For any n, chi(S^2 x CP^(n/gcd-1)) gives factorizations.
  This works for ALL integers, not just 6.

  VERDICT: The chi=6 product construction is NOT special to 6.
  It's a general fact about integers and product manifolds.
  The surface impossibility (chi=6 needs g=-2) IS genuinely topological.

  HOWEVER: the fact that all divisors of 6 are chi of "natural" spaces
  (point, sphere, CP^2, CP^5) is mildly interesting because:
  - chi=1 = point (trivial)
  - chi=2 = sphere (fundamental)
  - chi=3 = CP^2 (fundamental)
  - chi=6 = CP^5 (less fundamental, but standard)

  For comparison, divisors of 12: {1,2,3,4,6,12}
  - chi=4 = S^2 x S^2 or CP^3 (standard)
  - chi=12 = CP^11 (standard but large)
  Any integer n has chi(CP^(n-1)) = n, so this is universal.
""")

print("## Final Verdict")
print("  H-TOP-2 RATING: WHITE CIRCLE (trivial/universal)")
print("  chi=6 is achievable by CP^5 and S^2 x CP^2,")
print("  but this follows from general facts (CP^(n-1) has chi=n)")
print("  that work for ALL integers, not specifically 6.")
print("  The product 6=2x3 mapping to S^2 x CP^2 is cute but not deep.")
print("  No special topological property of 6 is revealed beyond")
print("  what holds for every positive integer.")
