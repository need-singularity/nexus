#!/usr/bin/env python3
"""
Verify Information Theory / Computer Science Hypotheses H-INFO-001 through H-INFO-015.

Each hypothesis is checked against known mathematical facts and arithmetic.
Grades:
  GREEN  = Exact equation, mathematically proven
  ORANGE = Numerically correct within stated tolerance, structurally interesting
  WHITE  = Arithmetically correct but trivial/coincidental
  BLACK  = Arithmetically wrong or factually incorrect

Run: PYTHONPATH=. python3 verify/verify_info_hypotheses.py
"""
import math
import sys

# ── Number-theoretic helpers for perfect number 6 ──
def sigma(n):
    """Sum of divisors."""
    return sum(d for d in range(1, n + 1) if n % d == 0)

def sigma_neg1(n):
    """Sum of reciprocals of divisors."""
    return sum(1.0 / d for d in range(1, n + 1) if n % d == 0)

def tau(n):
    """Number of divisors."""
    return sum(1 for d in range(1, n + 1) if n % d == 0)

def euler_phi(n):
    """Euler totient."""
    return sum(1 for k in range(1, n + 1) if math.gcd(k, n) == 1)

def is_perfect(n):
    """Check if n is a perfect number (sigma(n) = 2n)."""
    return sigma(n) == 2 * n

def divisors(n):
    """Return sorted list of divisors."""
    return sorted(d for d in range(1, n + 1) if n % d == 0)

# ── Golden Zone constants ──
GZ_UPPER = 0.5
GZ_LOWER = 0.5 - math.log(4 / 3)
GZ_CENTER = 1 / math.e
GZ_WIDTH = math.log(4 / 3)

# ── Results tracking ──
results = []
GREEN = 0
ORANGE = 0
WHITE = 0
BLACK = 0

def grade(hid, emoji, passed, desc, detail=""):
    global GREEN, ORANGE, WHITE, BLACK
    results.append((hid, emoji, passed, desc, detail))
    status = "PASS" if passed else "FAIL"
    print(f"  {emoji} {hid}: {status} -- {desc}")
    if detail:
        for line in detail.strip().split("\n"):
            print(f"       {line}")
    print()
    if emoji == "G":
        GREEN += 1
    elif emoji == "O":
        ORANGE += 1
    elif emoji == "W":
        WHITE += 1
    elif emoji == "B":
        BLACK += 1


# =============================================================================
print("=" * 72)
print("  INFORMATION THEORY & CS HYPOTHESES VERIFICATION (H-INFO-001 to 015)")
print("=" * 72)
print()

n = 6
s6 = sigma(n)       # 12
t6 = tau(n)          # 4
p6 = euler_phi(n)    # 2
sn1_6 = sigma_neg1(n)  # 2.0
divs6 = divisors(n)  # [1, 2, 3, 6]

print(f"  n = {n}, sigma(6) = {s6}, tau(6) = {t6}, phi(6) = {p6}")
print(f"  sigma_{{-1}}(6) = {sn1_6}, divisors = {divs6}")
print(f"  Golden Zone: [{GZ_LOWER:.4f}, {GZ_UPPER:.4f}], center = {GZ_CENTER:.4f}")
print()

# ── A. Information Theory ──
print("=" * 72)
print("  A. INFORMATION THEORY (H-INFO-001 to 005)")
print("=" * 72)
print()

# H-INFO-001: Shannon entropy H(6) = log2(6)
H6 = math.log2(6)
H2 = math.log2(2)
H3 = math.log2(3)
grade("H-INFO-001", "G", abs(H6 - (H2 + H3)) < 1e-12,
      f"H(6) = log2(6) = log2(2) + log2(3) = {H6:.6f} bits",
      f"log2(2) = {H2:.6f}, log2(3) = {H3:.6f}\n"
      f"Sum = {H2 + H3:.6f} = H(6)? {abs(H6 - (H2 + H3)) < 1e-12}\n"
      f"Exact by definition of log. Tautological for all n.")

# H-INFO-002: Divisor distribution entropy
probs = [d / s6 for d in divs6]
H_div = -sum(p * math.log2(p) for p in probs)
H_max_div = math.log2(t6)
eff = H_div / H_max_div
grade("H-INFO-002", "W", abs(H_div - 1.729574) < 0.001,
      f"Divisor distribution entropy = {H_div:.6f} bits, efficiency = {eff:.4f}",
      f"Divisor probs: {[round(p, 4) for p in probs]}\n"
      f"H_max = log2({t6}) = {H_max_div:.4f}\n"
      f"Efficiency = {eff:.4f} = 86.5%. Arbitrary construction.")

# H-INFO-003: Huffman code for 6 equiprobable symbols
# Optimal lengths: [2, 2, 3, 3, 3, 3]
L_huffman = (2 * 2 + 4 * 3) / 6
redundancy = L_huffman - H6
kraft = 2 * (2**-2) + 4 * (2**-3)
grade("H-INFO-003", "W", abs(kraft - 1.0) < 1e-12 and abs(L_huffman - 8/3) < 1e-12,
      f"Huffman L = {L_huffman:.4f}, redundancy = {redundancy:.4f}, Kraft = {kraft:.4f}",
      f"Lengths: [2,2,3,3,3,3]\n"
      f"Overhead = {redundancy/H6*100:.2f}% of H\n"
      f"Kraft sum = {kraft} (equality). Generic non-power-of-2 property.")

# H-INFO-004: BSC capacity at p=1/6 in Golden Zone
p_bsc = 1 / n
H_bsc = -p_bsc * math.log2(p_bsc) - (1 - p_bsc) * math.log2(1 - p_bsc)
C_bsc = 1 - H_bsc
in_gz = GZ_LOWER <= C_bsc <= GZ_UPPER
# Check other perfect numbers
C_28 = 1 - (-1/28 * math.log2(1/28) - 27/28 * math.log2(27/28))
C_496 = 1 - (-1/496 * math.log2(1/496) - 495/496 * math.log2(495/496))
grade("H-INFO-004", "O", in_gz,
      f"BSC C(p=1/6) = {C_bsc:.6f}, in Golden Zone = {in_gz}",
      f"GZ: [{GZ_LOWER:.4f}, {GZ_UPPER:.4f}]\n"
      f"|C - 1/e| = {abs(C_bsc - GZ_CENTER):.6f} (4.9% from center)\n"
      f"|C - 1/3| = {abs(C_bsc - 1/3):.6f} (5.0% from meta fixed point)\n"
      f"n=28: C = {C_28:.4f} (above GZ)\n"
      f"n=496: C = {C_496:.4f} (above GZ)\n"
      f"Only n=6 gives C in GZ among perfect numbers.\n"
      f"But GZ width = {GZ_WIDTH:.4f} = 28.8% of [0,1]. Weak.")

# H-INFO-005: Entropy additivity reflects perfect number structure
# Check: does this hold for non-perfect numbers? (Yes, for all n)
H15 = math.log2(15)
H3_ = math.log2(3)
H5_ = math.log2(5)
sigma15 = sigma(15)
grade("H-INFO-005", "B", False,
      "Entropy additivity parallel with sigma multiplicativity",
      f"H(6) = H(2)+H(3) = {H6:.4f} (additive)\n"
      f"sigma(6) = sigma(2)*sigma(3) = 3*4 = 12 (multiplicative)\n"
      f"But also: H(15) = H(3)+H(5) = {H15:.4f}\n"
      f"sigma(15) = sigma(3)*sigma(5) = 4*6 = {sigma15}\n"
      f"Holds for ALL n with coprime factors. Not special to perfect numbers.")

# ── B. Coding Theory ──
print("=" * 72)
print("  B. CODING THEORY (H-INFO-006 to 010)")
print("=" * 72)
print()

# H-INFO-006: Hamming(7,4) parameters
n_ham = t6 + p6 + 1  # 4+2+1 = 7
k_ham = t6  # 4
r_ham = 3  # largest proper divisor of 6
sphere_ham = 2**k_ham * (1 + n_ham)  # = 16 * 8 = 128 = 2^7
grade("H-INFO-006", "W",
      n_ham == 7 and k_ham == 4 and r_ham == 3 and sphere_ham == 2**7,
      f"Hamming(7,4): tau+phi+1={n_ham}, k=tau(6)={k_ham}, r=3",
      f"Sphere packing: 2^{k_ham} * (1+{n_ham}) = {sphere_ham} = 2^7 PERFECT\n"
      f"But: {t6}+{p6}+1 = 2^2+2^1+2^0 = 2^3-1 = 7.\n"
      f"Binary arithmetic identity, not deep n=6 connection.")

# H-INFO-007: Golay(23,12) k = sigma(6)
k_golay = s6  # 12
# Verify sphere packing for Golay
sphere_golay = 2**12 * sum(math.comb(23, i) for i in range(4))
# Check n=28 generalization
s28 = sigma(28)  # 56
t28 = tau(28)  # 6
# Is there a perfect code with k=56? No known one.
# Is there a Hamming code with k=6? 2^r-r-1=6 -> r=4: k=11. No.
grade("H-INFO-007", "O",
      k_golay == 12 and sphere_golay == 2**23,
      f"Golay(23,12,7): k = sigma(6) = {k_golay}, perfect code",
      f"Sphere packing: 2^12 * sum C(23,i) = {sphere_golay} = 2^23 TIGHT\n"
      f"Both nontrivial perfect code families:\n"
      f"  Hamming: k = tau(6) = {t6}\n"
      f"  Golay:   k = sigma(6) = {s6}\n"
      f"n=28 test: sigma(28)={s28}, tau(28)={t28}\n"
      f"  No perfect code with k=56 or k=6. FAILS generalization.")

# H-INFO-008: RS(6,4) over GF(7)
# n_rs = q-1 = 6 for q=7 (prime)
n_rs = 6
k_rs = t6  # 4
d_rs = n_rs - k_rs + 1  # 3 (Singleton bound, MDS)
grade("H-INFO-008", "O",
      n_rs == 6 and k_rs == 4 and d_rs == 3,
      f"RS(6,4) over GF(7): n={n_rs}, k=tau(6)={k_rs}, d={d_rs} (MDS)",
      f"GF(7): 7 = smallest prime > 6. n = q-1 = 6.\n"
      f"Singleton bound: d = n-k+1 = {d_rs}. Maximum distance separable.\n"
      f"n=28: RS(28,k) over GF(29). 29 is prime. Works.\n"
      f"But RS(n,k) exists for any n=q-1 where q is prime power.\n"
      f"General property, not specific to perfect numbers.")

# H-INFO-009: Extended Hamming rate = 1/2 = GZ upper
rate_ext = 4 / 8  # k/n for extended Hamming(8,4,4)
grade("H-INFO-009", "W", abs(rate_ext - GZ_UPPER) < 1e-12,
      f"Extended Hamming(8,4,4) rate = {rate_ext} = GZ upper",
      f"k=4=tau(6), d=4=tau(6), n=8=2^3\n"
      f"Rate = 1/2 = GZ upper. But 1/2 is trivially common.\n"
      f"Any (2k,k,d) code has rate 1/2.")

# H-INFO-010: IPv6
grade("H-INFO-010", "B", False,
      "IPv6 version=6, 128=2^7=2^(tau+phi+1)",
      f"IPv6 version number is historical (after IPv4, skipping IPv5/ST).\n"
      f"128 bits chosen for 4x IPv4 address space (practical, not mathematical).\n"
      f"Naming coincidence. No structural content.")

# ── C. Algorithms & Graph Theory ──
print("=" * 72)
print("  C. ALGORITHMS & GRAPH THEORY (H-INFO-011 to 015)")
print("=" * 72)
print()

# H-INFO-011: R(3,3) = 6
# Verify: K5 has a 2-coloring without mono K3 (lower bound)
# Verify: K6 forces mono K3 (upper bound)
# We can verify the upper bound computationally
from itertools import combinations

def has_monochromatic_triangle(n_verts, coloring):
    """Check if edge 2-coloring of K_n contains monochromatic triangle."""
    for v1, v2, v3 in combinations(range(n_verts), 3):
        e1 = coloring.get((v1, v2), coloring.get((v2, v1)))
        e2 = coloring.get((v1, v3), coloring.get((v3, v1)))
        e3 = coloring.get((v2, v3), coloring.get((v3, v2)))
        if e1 == e2 == e3:
            return True
    return False

# K5 counterexample: cycle coloring
# Edges of 5-cycle red, diagonals blue
k5_coloring = {}
for i in range(5):
    k5_coloring[(i, (i + 1) % 5)] = 'R'  # cycle edge = red
for i in range(5):
    k5_coloring[(i, (i + 2) % 5)] = 'B'  # diagonal = blue
k5_has_mono = has_monochromatic_triangle(5, k5_coloring)

# K6 exhaustive check: try ALL 2^15 colorings
k6_edges = list(combinations(range(6), 2))
assert len(k6_edges) == 15
k6_all_have_mono = True
k6_counterexample = None
for mask in range(2**15):
    coloring = {}
    for idx, (u, v) in enumerate(k6_edges):
        coloring[(u, v)] = 'R' if (mask >> idx) & 1 else 'B'
    if not has_monochromatic_triangle(6, coloring):
        k6_all_have_mono = False
        k6_counterexample = mask
        break

# Check R(s,s) for small s and perfect number test
ramsey_ss = {1: 1, 2: 2, 3: 6, 4: 18}
ramsey_perfect = [s for s, r in ramsey_ss.items() if is_perfect(r)]

grade("H-INFO-011", "G",
      not k5_has_mono and k6_all_have_mono,
      f"R(3,3) = 6: PROVEN by exhaustive search",
      f"K5 counterexample exists (no mono triangle): {not k5_has_mono}\n"
      f"K6 all 2^15 = {2**15} colorings checked: all have mono triangle = {k6_all_have_mono}\n"
      f"Therefore R(3,3) = 6 exactly.\n"
      f"R(s,s) values: {ramsey_ss}\n"
      f"Perfect numbers among R(s,s): R(3,3)=6 only (s={ramsey_perfect})\n"
      f"3 = largest proper divisor of 6, 2 = phi(6) = number of colors.\n"
      f"Deep combinatorial theorem. Genuine n=6.")

# H-INFO-012: Euler V-E+F = 2 = sigma_{-1}(6)
# Verify Platonic solid data
platonic = [
    ("Tetrahedron", 4, 6, 4),
    ("Cube", 8, 12, 6),
    ("Octahedron", 6, 12, 8),
    ("Dodecahedron", 20, 30, 12),
    ("Icosahedron", 12, 30, 20),
]
all_euler = all(V - E + F == 2 for _, V, E, F in platonic)
has_6_or_12 = [(name, V, E, F) for name, V, E, F in platonic
               if V in (6, 12) or E in (6, 12) or F in (6, 12)]
# Cube-octahedron duality check
cube = platonic[1]
octa = platonic[2]
dual_check = (cube[1] == octa[3] and cube[3] == octa[1] and cube[2] == octa[2])

grade("H-INFO-012", "G",
      all_euler and abs(sn1_6 - 2.0) < 1e-12,
      f"Euler V-E+F = 2 = sigma_{{-1}}(6) for all Platonic solids",
      f"sigma_{{-1}}(6) = {sn1_6} = 2. Euler chi = 2.\n"
      + "\n".join(f"  {name}: V={V}, E={E}, F={F}, V-E+F={V-E+F}"
                  for name, V, E, F in platonic)
      + f"\n  Platonic solids with 6 or 12 in params: {len(has_6_or_12)}/5\n"
      f"  Cube-Octahedron duality: V<->F, E=12=sigma(6). Check={dual_check}\n"
      f"  Both equal 2 but for different reasons (perfect number vs topology).")

# H-INFO-013: Sorting 6 elements requires 10 comparisons
factorial6 = math.factorial(6)
lb_sort = math.ceil(math.log2(factorial6))
sigma_minus_phi = s6 - p6
# Check tightness for other n
tight_counts = []
# Known optimal: from Knuth TAOCP
optimal_sort = {1: 0, 2: 1, 3: 3, 4: 5, 5: 7, 6: 10, 7: 13, 8: 16,
                9: 19, 10: 22, 11: 26, 12: 30}
for nn in range(1, 13):
    lb_nn = math.ceil(math.log2(math.factorial(nn))) if nn > 0 else 0
    opt_nn = optimal_sort[nn]
    tight_counts.append((nn, lb_nn, opt_nn, lb_nn == opt_nn))

grade("H-INFO-013", "W",
      lb_sort == 10 and sigma_minus_phi == 10,
      f"Sort(6): lower bound = ceil(log2(720)) = {lb_sort} = sigma-phi = {sigma_minus_phi}",
      f"6! = {factorial6}, log2(720) = {math.log2(720):.4f}\n"
      f"sigma(6)-phi(6) = {s6}-{p6} = {sigma_minus_phi}\n"
      f"Tightness across n:\n"
      + "\n".join(f"  n={nn}: lb={lb}, opt={opt}, tight={t}"
                  for nn, lb, opt, t in tight_counts)
      + f"\n  Tight for n=1..11. NOT unique to n=6. sigma-phi match is ad hoc.")

# H-INFO-014: Four Color Theorem 4 = tau(6)
# Check how many n have tau(n)=4
tau_4_numbers = [nn for nn in range(1, 50) if tau(nn) == 4]
grade("H-INFO-014", "B", False,
      f"Four Color Theorem: 4 = tau(6). Coincidental.",
      f"tau(n)=4 for n in 1..50: {tau_4_numbers}\n"
      f"That's {len(tau_4_numbers)} numbers! 4 is too common for meaningful mapping.\n"
      f"The theorem was proven by computer search (Appel-Haken 1976).\n"
      f"No connection to divisor functions.")

# H-INFO-015: K_{3,3} has 6 vertices
k33_verts = 3 + 3
k33_edges = 3 * 3
# Planarity check: for bipartite graphs, E <= 2V - 4
planar_bound = 2 * k33_verts - 4
grade("H-INFO-015", "W",
      k33_verts == 6,
      f"K_{{3,3}}: V={k33_verts}=n, E={k33_edges}, non-planar (E={k33_edges} > {planar_bound})",
      f"K_{{3,3}} = complete bipartite graph with parts of size 3.\n"
      f"3 = largest prime factor of 6 = n/2.\n"
      f"Kuratowski: K_5 and K_{{3,3}} are the two minimal non-planar graphs.\n"
      f"But K_5 has 5 vertices, not 6. The V=6 follows trivially from 3+3.")

# =============================================================================
print("=" * 72)
print("  SUMMARY")
print("=" * 72)
print()
print(f"  Total hypotheses: {len(results)}")
print(f"  GREEN  (Exact):       {GREEN}")
print(f"  ORANGE (Structural):  {ORANGE}")
print(f"  WHITE  (Trivial):     {WHITE}")
print(f"  BLACK  (Wrong):       {BLACK}")
print()

# Grade distribution bar
print("  Grade distribution:")
print(f"  {'G' * GREEN}{'O' * ORANGE}{'W' * WHITE}{'B' * BLACK}")
print(f"  {'|' * GREEN}{'|' * ORANGE}{'|' * WHITE}{'|' * BLACK}")
print()

# Pass/fail summary
print("  Results by hypothesis:")
for hid, emoji, passed, desc, _ in results:
    status = "PASS" if passed else "FAIL"
    print(f"    {emoji} {hid}: {status}")

print()
print("  STANDOUT: R(3,3) = 6 is the strongest finding (deep combinatorial theorem).")
print("  Euler V-E+F = 2 = sigma_{-1}(6) and Golay k=12=sigma(6) are noteworthy.")
print()

# Exit code
n_pass = sum(1 for _, _, p, _, _ in results if p)
n_fail = len(results) - n_pass
print(f"  {n_pass} passed, {n_fail} failed (expected: failures are honest grades)")
sys.exit(0)
