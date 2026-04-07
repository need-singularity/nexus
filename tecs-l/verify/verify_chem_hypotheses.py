#!/usr/bin/env python3
"""
Verify Chemistry Hypotheses H-CHEM-001 through H-CHEM-030.

Each hypothesis is checked against known chemistry data and arithmetic.
Grades:
  GREEN  = Exact equation, mathematically proven
  ORANGE = Numerically correct within stated tolerance, structurally interesting
  WHITE  = Arithmetically correct but trivial/coincidental
  BLACK  = Arithmetically wrong or factually incorrect

Run: PYTHONPATH=. python3 verify/verify_chem_hypotheses.py
"""
import math
import sys

# ── Number-theoretic helpers for perfect number 6 ──
def sigma(n):
    """Sum of divisors."""
    return sum(d for d in range(1, n+1) if n % d == 0)

def sigma_neg1(n):
    """Sum of reciprocals of divisors."""
    return sum(1.0/d for d in range(1, n+1) if n % d == 0)

def tau(n):
    """Number of divisors."""
    return sum(1 for d in range(1, n+1) if n % d == 0)

def euler_phi(n):
    """Euler totient."""
    return sum(1 for k in range(1, n+1) if math.gcd(k, n) == 1)

def is_perfect(n):
    """Check if n is a perfect number (sigma(n) = 2n)."""
    return sigma(n) == 2 * n

# ── Golden Zone constants ──
GZ_UPPER = 0.5
GZ_LOWER = 0.5 - math.log(4/3)
GZ_CENTER = 1/math.e
GZ_WIDTH = math.log(4/3)

# ── Results tracking ──
results = []

def grade(hid, emoji, passed, desc, detail=""):
    results.append((hid, emoji, passed, desc, detail))
    status = "PASS" if passed else "FAIL"
    print(f"  {emoji} {hid}: {status} — {desc}")
    if detail:
        for line in detail.strip().split("\n"):
            print(f"       {line}")
    print()

# =============================================================================
print("=" * 72)
print("  CHEMISTRY HYPOTHESES VERIFICATION (H-CHEM-001 to 030)")
print("=" * 72)
print()

# ── A. Quantum Chemistry / Orbitals ──
print("── A. Quantum Chemistry / Orbitals ──\n")

# H-CHEM-001: Carbon Z=6 perfect number + tau(6)=4 = sp3
# Check: 6 is perfect, tau(6)=4, and no other Z in 1-20 satisfies both
t6 = tau(6)
perf6 = is_perfect(6)
others = []
for z in range(1, 21):
    if z == 6:
        continue
    if is_perfect(z) and tau(z) == 4:
        others.append(z)
grade("H-CHEM-001", "🟩" if (perf6 and t6 == 4 and len(others) == 0) else "⬛",
      perf6 and t6 == 4 and len(others) == 0,
      "Carbon Z=6: perfect number + tau(6)=4 matching sp3",
      f"is_perfect(6)={perf6}, tau(6)={t6}, others in Z=1..20 with both={others}\n"
      f"Note: sp3 has 4 hybrid orbitals, tau(6)=4 divisors {'{1,2,3,6}'}. Exact match but mapping is ad hoc.")

# H-CHEM-002: Tetrahedral angle cos = -1/3
theta_tet = math.acos(-1/3)
theta_deg = math.degrees(theta_tet)
cos_check = math.cos(math.radians(109.4712))
grade("H-CHEM-002", "🟩", abs(cos_check - (-1/3)) < 1e-4,
      "cos(109.47°) = -1/3 exactly",
      f"cos(109.4712°) = {cos_check:.8f}, -1/3 = {-1/3:.8f}\n"
      f"Tetrahedral angle = {theta_deg:.4f}°\n"
      f"This is a well-known geometry result. 1/3 = TECS meta fixed point is coincidental mapping.")

# H-CHEM-003: Benzene Huckel MO gap = 2|beta|, bonding fraction = 2/3
# Huckel energies for 6-annulene: E_k = alpha + 2*beta*cos(2*pi*k/6), k=0..5
energies = sorted([2*math.cos(2*math.pi*k/6) for k in range(6)], reverse=True)
homo = energies[2]  # 3rd orbital (0-indexed: 0,1,2 occupied with 6 electrons)
lumo = energies[3]
gap = homo - lumo
bonding = sum(1 for e in energies if e > 0)
sig6 = sigma_neg1(6)
grade("H-CHEM-003", "⬛" if bonding != 4 else "🟩", abs(gap - 2.0) < 1e-10 and bonding == 4,
      "Benzene HOMO-LUMO gap = 2|beta|, bonding orbitals = 4/6",
      f"Huckel energies (units of beta): {[round(e,4) for e in energies]}\n"
      f"HOMO={homo:.4f}, LUMO={lumo:.4f}, gap={gap:.4f}|beta|\n"
      f"Bonding orbitals (E>0): {bonding}/6 = {bonding/6:.4f}\n"
      f"sigma_{{-1}}(6) = {sig6:.4f}, gap = 2.0. Match is exact but 2=sigma_-1(6) mapping is ad hoc.")

# H-CHEM-004: Carbon 2p2 fills 2/3 of p-orbitals
# Carbon: 1s2 2s2 2p2. 3 p-orbitals, 2 occupied (by Hund's rule, 1 each in 2 orbitals)
p_fill = 2/3
phi6 = euler_phi(6)  # = 2
grade("H-CHEM-004", "⚪", abs(p_fill - 2/3) < 1e-10,
      "Carbon p-orbital filling = 2/3",
      f"2p2: 2 of 3 p-orbitals occupied = {p_fill:.4f}\n"
      f"phi(6)/3 = {phi6}/3 = {phi6/3:.4f}. Correct but trivial (2/3 is common fraction).")

# H-CHEM-005: Carbon IE2/IE1 ≈ 2
# Real NIST data: IE1=1086.5 kJ/mol, IE2=2352.6 kJ/mol
IE1_C = 1086.5
IE2_C = 2352.6
ratio_IE = IE2_C / IE1_C
# Check Period 2 elements for closest to 2
# IE data (kJ/mol): Li, Be, B, C, N, O, F, Ne
ie_data = {
    'Li': (520.2, 7298.1),
    'Be': (899.5, 1757.1),
    'B':  (800.6, 2427.1),
    'C':  (1086.5, 2352.6),
    'N':  (1402.3, 2856.0),
    'O':  (1313.9, 3388.3),
    'F':  (1681.0, 3374.2),
    'Ne': (2080.7, 3952.3),
}
closest = min(ie_data.items(), key=lambda x: abs(x[1][1]/x[1][0] - 2))
all_ratios = {k: v[1]/v[0] for k, v in ie_data.items()}
err = abs(ratio_IE - 2) / 2 * 100
grade("H-CHEM-005", "⚪" if err < 9 else "⬛", err < 9,
      f"Carbon IE2/IE1 = {ratio_IE:.3f} ≈ 2 (error {err:.1f}%)",
      f"Period 2 IE2/IE1 ratios: {', '.join(f'{k}={v:.3f}' for k,v in sorted(all_ratios.items(), key=lambda x: x[1]))}\n"
      f"Closest to 2: {closest[0]} ({closest[1][1]/closest[1][0]:.3f})\n"
      f"Be(1.953) is actually closer to 2 than C(2.166). Claim 'closest' is WRONG.\n"
      f"However arithmetic (2.166, within 9%) is correct.")

# ── B. Periodic Trends ──
print("── B. Periodic Trends ──\n")

# H-CHEM-006: F/B electronegativity ≈ 2
EN_F = 3.98
EN_B = 2.04
en_ratio = EN_F / EN_B
err6 = abs(en_ratio - 2) / 2 * 100
grade("H-CHEM-006", "⚪" if err6 < 3 else "⬛", err6 < 3,
      f"F/B EN ratio = {en_ratio:.3f} ≈ 2 (error {err6:.1f}%)",
      f"F EN=3.98, B EN=2.04, ratio={en_ratio:.4f}\n"
      f"Within 3%: {'YES' if err6<3 else 'NO'}. Numerically correct but 2 is trivial target.")

# H-CHEM-007: Carbon normalized radius in GZ boundary
r_C = 0.76  # Angstrom covalent radius (commonly cited: 0.77)
r_Li = 1.28  # (commonly cited: 1.28)
norm_r = r_C / r_Li
in_range = 0.5 <= norm_r <= 0.6
grade("H-CHEM-007", "⚪" if in_range else "⬛", in_range,
      f"C/Li covalent radius = {norm_r:.3f}, in [0.5, 0.6]: {in_range}",
      f"C={r_C}A, Li={r_Li}A. Ratio={norm_r:.4f}\n"
      f"Note: covalent radii vary by source. Using common values.\n"
      f"The [0.5, 0.6] range is broad. GZ upper + ln(4/3)/pi = {0.5+math.log(4/3)/math.pi:.4f}")

# H-CHEM-008: CHNOPS mean EA / max EA ≈ 1/e
# Electron affinities (kJ/mol): C=121.8, N=-7 (negative!), O=141.0, P=72.0, S=200.4
# (N has near-zero or slightly negative EA; commonly reported as ~0 or -7)
EA = {'C': 121.8, 'N': -7.0, 'O': 141.0, 'P': 72.0, 'S': 200.4}
# H not in the set per hypothesis (CHNOPS minus H, hypothesis says {C,N,O,P,S})
mean_EA = sum(EA.values()) / len(EA)
max_EA = max(EA.values())  # S=200.4 or O=141? Hypothesis says max=EA_O
# Hypothesis specifically says max(EA_O), so use O's EA
ratio_ea = mean_EA / EA['O']
in_range_ea = 0.3 <= ratio_ea <= 0.4
grade("H-CHEM-008", "⬛", in_range_ea,
      f"Mean EA(C,N,O,P,S)/EA(O) = {ratio_ea:.4f}, in [0.3,0.4]: {in_range_ea}",
      f"EAs (kJ/mol): {EA}\n"
      f"Mean = {mean_EA:.1f}, EA(O) = {EA['O']}, ratio = {ratio_ea:.4f}\n"
      f"N has negative EA, dragging mean down. Also S has higher EA than O.\n"
      f"Using max(all) = S(200.4): ratio = {mean_EA/200.4:.4f}\n"
      f"Neither version falls cleanly in [0.3, 0.4]. Problem: N's negative EA.")

# H-CHEM-009: Z_P - Z_C = 9 = 3^2, EN difference < 15%
Z_diff = 15 - 6
is_9 = Z_diff == 9
is_3sq = Z_diff == 3**2
# Allred-Rochow EN: C=2.50, P=2.06 (these vary by scale)
EN_C_AR = 2.50
EN_P_AR = 2.06
en_diff_pct = abs(EN_C_AR - EN_P_AR) / EN_C_AR * 100
grade("H-CHEM-009", "⬛",
      is_9 and en_diff_pct < 15,
      f"Z_P - Z_C = {Z_diff} = 3^2, EN diff = {en_diff_pct:.1f}%",
      f"15-6=9=3^2, 3|6: TRUE\n"
      f"Allred-Rochow: C={EN_C_AR}, P={EN_P_AR}, diff={en_diff_pct:.1f}% < 15%\n"
      f"Both correct. Diagonal relationship is real chemistry but 9=3^2 connection to 6 is weak.")

# H-CHEM-010: Carbon at position 4/8 = 1/2 in Period 2
# Period 2: Li Be B C N O F Ne = 8 elements, C is 4th
pos = 4
total = 8
frac = pos / total
grade("H-CHEM-010", "⚪", frac == 0.5,
      f"Carbon position in Period 2: {pos}/{total} = {frac}",
      f"C is element 4 of 8 in Period 2. 4/8 = 1/2 = GZ upper.\n"
      f"Exact. But 1/2 is the most common fraction; this is not deep.")

# ── C. Molecular Geometry / VSEPR ──
print("── C. Molecular Geometry / VSEPR ──\n")

# H-CHEM-011: D6h order = 24 = sigma(6) * sigma_{-1}(6)
d6h_order = 24  # Standard: D6h has order 24
sig6_val = sigma(6)  # 12
sig_neg1_6 = sigma_neg1(6)  # 2.0
product = sig6_val * sig_neg1_6
grade("H-CHEM-011", "⚪", d6h_order == product,
      f"D6h order = {d6h_order}, sigma(6)*sigma_-1(6) = {sig6_val}*{sig_neg1_6} = {product}",
      f"WAIT: D6h actually has order 24? Let me verify.\n"
      f"D6h = {{E, 2C6, 2C3, C2, 3C2', 3C2'', i, 2S3, 2S6, sigma_h, 3sigma_d, 3sigma_v}}\n"
      f"Count: 1+2+2+1+3+3+1+2+2+1+3+3 = 24. YES, order=24.\n"
      f"12 * 2.0 = 24.0. Arithmetic exact.\n"
      f"But this is just 24 = 12*2, a trivial factorization.")

# H-CHEM-012: Octahedron edges = 12 = sigma(6)
oct_edges = 12  # standard geometry
grade("H-CHEM-012", "🟩", oct_edges == sigma(6),
      f"Octahedron edges = {oct_edges} = sigma(6) = {sigma(6)}",
      f"Octahedron: 6 vertices, 12 edges, 8 faces. Exact.\n"
      f"Coordination number = 6 = n. Both exact geometric facts.")

# H-CHEM-013: Water angle deviation
theta_water = 104.5
theta_tet_exact = math.degrees(math.acos(-1/3))  # 109.4712°
dev = theta_tet_exact - theta_water
frac_dev = dev / theta_tet_exact
val = frac_dev * tau(6)
target = 1/6
err13 = abs(val - target) / target * 100
grade("H-CHEM-013", "⚪" if err13 < 10 else "⬛", err13 < 10,
      f"(deviation/tetrahedral)*tau(6) = {val:.4f} ≈ 1/6 = {target:.4f} (err {err13:.1f}%)",
      f"Water=104.5°, Tetrahedral={theta_tet_exact:.2f}°, dev={dev:.2f}°\n"
      f"{dev:.2f}/{theta_tet_exact:.2f} * 4 = {val:.4f}, target 1/6={target:.4f}\n"
      f"Error={err13:.1f}%. Within 9%: {'YES' if err13<9 else 'NO, exceeds 9%'}. Within 10%: {'YES' if err13<10 else 'NO'}.")

# H-CHEM-014: CH4 Td order = 24, bond count = 4 = tau(6)
td_order = 24  # Td has 24 symmetry operations
ch4_bonds = 4
grade("H-CHEM-014", "🟩" if (td_order == 24 and ch4_bonds == tau(6)) else "⬛",
      td_order == 24 and ch4_bonds == tau(6),
      f"CH4: Td order={td_order}=sigma(6)*sigma_-1(6), bonds={ch4_bonds}=tau(6)",
      f"Td order=24, tau(6)=4. Both exact.\n"
      f"But 24 = sigma(6)*sigma_-1(6) is same as H-CHEM-011. Mapping is ad hoc.")

# H-CHEM-015: Cyclohexane C6H12 has 12 H = sigma(6)
c6h12_H = 12
grade("H-CHEM-015", "🟩", c6h12_H == sigma(6),
      f"C6H12 has {c6h12_H} hydrogens = sigma(6) = {sigma(6)}",
      f"Cyclohexane C6H12: 12 H atoms. sigma(6)=12. Exact.\n"
      f"But H-count = 2*C-count for CnH2n, so 2*6=12 is just the formula. Trivial.")

# ── D. Reaction Kinetics / Thermodynamics ──
print("── D. Reaction Kinetics / Thermodynamics ──\n")

# H-CHEM-016: At T=Ea/R, Boltzmann factor = e^{-1} = 1/e
# Arrhenius: k = A*exp(-Ea/(RT)). At T=Ea/R: exp(-Ea/(R*Ea/R)) = exp(-1) = 1/e
val16 = math.exp(-1)
grade("H-CHEM-016", "🟩", abs(val16 - 1/math.e) < 1e-15,
      f"exp(-Ea/(R*Ea/R)) = exp(-1) = 1/e = {val16:.6f}",
      f"This is a tautology: T=Ea/R → exp(-Ea/RT)=exp(-1)=1/e.\n"
      f"Exact to arbitrary precision. True but definitional.")

# H-CHEM-017: At K_eq=1, forward fraction = 1/2
# K_eq = kf/kr = 1 → kf = kr → kf/(kf+kr) = 1/2
grade("H-CHEM-017", "🟩", True,
      "At K_eq=1: kf/(kf+kr) = 1/2 = GZ upper",
      "K=kf/kr=1 → kf=kr → fraction=1/2. Exact tautology.")

# H-CHEM-018: 4/3 temperature ratio and ln(k) change
# Arrhenius: ln(k2/k1) = (Ea/R)*(1/T1 - 1/T2)
Ea = 50000  # 50 kJ/mol
R = 8.314
T1, T2 = 300, 400
delta_lnk = (Ea / R) * (1/T1 - 1/T2)
grade("H-CHEM-018", "⚪", abs(delta_lnk - 5.01) < 0.1,
      f"delta_ln(k) at 300→400K, Ea=50kJ/mol: {delta_lnk:.3f}",
      f"(50000/8.314)*(1/300 - 1/400) = {delta_lnk:.4f}\n"
      f"Claimed 5.01. Actual={delta_lnk:.4f}. Close.\n"
      f"T2/T1 = 400/300 = 4/3 = GZ width origin. Connection is forced.")

# H-CHEM-019: Insulin hexamer Hill coefficient ≈ 6
# Real data: Insulin hexamer cooperativity is complex. Hill coefficients
# reported in literature for insulin hexamer binding are typically 2-4, not 6.
# The Hill coefficient reflects cooperativity of ligand binding, not subunit count.
grade("H-CHEM-019", "⬛", False,
      "Insulin hexamer Hill coefficient ≈ 6: INCORRECT",
      "Hill coefficient != subunit count. For insulin hexamer, published Hill\n"
      "coefficients for phenol/zinc binding are typically 2-4, not 6.\n"
      "n_Hill = 6 would require perfect infinite cooperativity, which doesn't occur.\n"
      "Conflating stoichiometry with cooperativity parameter.")

# H-CHEM-020: C-C bond energy fraction in cyclohexane combustion
# Cyclohexane C6H12: 6 C-C bonds, 12 C-H bonds
# Bond energies: C-C = 346 kJ/mol, C-H = 411 kJ/mol (standard values)
cc_total = 6 * 346
ch_total = 12 * 411
frac20 = cc_total / (cc_total + ch_total)
in_gz = GZ_LOWER <= frac20 <= GZ_UPPER
grade("H-CHEM-020", "⬛", False,
      f"C-C energy fraction = {frac20:.4f} != claimed 0.421 (ARITHMETIC ERROR)",
      f"6*346 = {cc_total}, 12*411 = {ch_total}, total = {cc_total+ch_total}\n"
      f"Fraction = {frac20:.4f}. Claimed 0.421 is WRONG.\n"
      f"Actual value {frac20:.4f} IS in GZ [{GZ_LOWER:.3f}, {GZ_UPPER:.3f}] but stated number is wrong.")

# ── E. Biochemistry / Life Chemistry ──
print("── E. Biochemistry / Life Chemistry ──\n")

# H-CHEM-021: CHNOPS = 6 elements
chnops = {'C', 'H', 'N', 'O', 'P', 'S'}
grade("H-CHEM-021", "⚪", len(chnops) == 6,
      f"CHNOPS count = {len(chnops)} = 6",
      f"Standard biochemistry: life's 6 bulk elements = CHNOPS.\n"
      f"Count = 6 is a well-known fact. Perfect number connection is numerological.")

# H-CHEM-022: DNA H-bonds: A-T=2, G-C=3, divisors of 6
at_hbonds = 2
gc_hbonds = 3
divs_6 = [d for d in range(2, 6) if 6 % d == 0]  # [2, 3]
grade("H-CHEM-022", "⚪", set([at_hbonds, gc_hbonds]) == set(divs_6),
      f"A-T={at_hbonds}, G-C={gc_hbonds} H-bonds = non-trivial proper divisors of 6: {divs_6}",
      f"{{2,3}} = proper divisors of 6 (excluding 1 and 6). Exact match.\n"
      f"But 2 and 3 appear everywhere. Selection of 'non-trivial proper' is cherry-picked.")

# H-CHEM-023: Maximum codon degeneracy = 6
# Standard genetic code: Leu(6), Ser(6), Arg(6) each have 6 codons
# Actually: Leu=6 (CUN+UUA+UUG), Ser=6 (UCN+AGU+AGC), Arg=6 (CGN+AGA+AGG)
max_degen = 6
grade("H-CHEM-023", "⚪", max_degen == 6,
      f"Maximum codon degeneracy = {max_degen}",
      f"Leu, Ser, Arg each have 6 codons (the maximum).\n"
      f"This is a well-known genetic code fact. Match to n=6 is coincidental.")

# H-CHEM-024: Carbon allotropes = 4 = tau(6)
# "4 major allotropes" is debatable. Diamond, graphite, fullerenes, CNTs, graphene,
# amorphous carbon, lonsdaleite, carbon nanobuds...
# The number depends on classification. Claiming exactly 4 is selective.
grade("H-CHEM-024", "⬛", False,
      "Carbon allotropes = 4 = tau(6): INCORRECT (count is subjective)",
      "Diamond, graphite, fullerenes, nanotubes, graphene, amorphous carbon,\n"
      "lonsdaleite, carbon nanobuds, glassy carbon, Q-carbon...\n"
      "At minimum 5+ recognized allotropes. Claiming exactly 4 is cherry-picked.\n"
      "If you include graphene (2004 Nobel Prize), already 5.")

# H-CHEM-025: |DG_ATP|/(RT) ≈ 12 = sigma(6)
DG_ATP = 30500  # J/mol (standard: ~30.5 kJ/mol)
T_body = 310  # K (37°C)
ratio_atp = DG_ATP / (R * T_body)
err25 = abs(ratio_atp - 12) / 12 * 100
grade("H-CHEM-025", "🟧" if err25 < 2 else "⚪", err25 < 5,
      f"|DG_ATP|/RT = {ratio_atp:.2f} ≈ sigma(6) = 12 (error {err25:.1f}%)",
      f"|DG| = 30.5 kJ/mol, RT = {R}*{T_body} = {R*T_body:.1f} J/mol\n"
      f"Ratio = {ratio_atp:.4f}. Error from 12: {err25:.2f}%\n"
      f"Within 1.4%: {'YES' if err25<1.5 else 'NO'}. Within 2%: {'YES' if err25<2 else 'NO'}.\n"
      f"Note: DG_ATP varies 30-35 kJ/mol depending on conditions. Sensitive to chosen value.")

# ── F. Materials / Crystallography ──
print("── F. Materials / Crystallography ──\n")

# H-CHEM-026: Graphene 2 atoms/cell = phi(6), coord=3
graphene_atoms = 2
graphene_coord = 3
grade("H-CHEM-026", "🟩", graphene_atoms == euler_phi(6) and 6 % graphene_coord == 0,
      f"Graphene: {graphene_atoms} atoms/cell = phi(6)={euler_phi(6)}, coord={graphene_coord} | 6",
      f"Graphene unit cell has 2 C atoms. phi(6)=2. Coordination=3, 3|6.\n"
      f"Both facts are exact. But phi(6)=2 is trivial (2 appears everywhere).")

# H-CHEM-027: Diamond 2nd neighbors = 12 = sigma(6)
diamond_2nd = 12
grade("H-CHEM-027", "🟩", diamond_2nd == sigma(6),
      f"Diamond 2nd-nearest neighbors = {diamond_2nd} = sigma(6) = {sigma(6)}",
      f"Each C in diamond: 4 nearest neighbors, 12 second-nearest. Exact.\n"
      f"Standard crystallography fact.")

# H-CHEM-028: HCP void fraction in GZ
hcp_packing = math.pi / (3 * math.sqrt(2))
hcp_void = 1 - hcp_packing
hcp_coord = 12
in_gz_28 = GZ_LOWER <= hcp_void <= GZ_UPPER
grade("H-CHEM-028", "🟩" if (in_gz_28 and hcp_coord == sigma(6)) else "⚪",
      in_gz_28 and hcp_coord == sigma(6),
      f"HCP void = {hcp_void:.4f}, in GZ: {in_gz_28}, coord={hcp_coord}=sigma(6)",
      f"Packing fraction = pi/(3*sqrt(2)) = {hcp_packing:.6f}\n"
      f"Void = {hcp_void:.6f}. GZ = [{GZ_LOWER:.4f}, {GZ_UPPER:.4f}]\n"
      f"Coordination = 12 = sigma(6). Both correct.\n"
      f"But GZ is 29% wide, and HCP void is a single well-known constant.")

# H-CHEM-029: C60 pentagons = 12 = sigma(6), Euler char = 2 = sigma_{-1}(6)
c60_pent = 12
c60_V, c60_E, c60_F = 60, 90, 32
euler_char = c60_V - c60_E + c60_F
grade("H-CHEM-029", "🟩", c60_pent == sigma(6) and euler_char == 2,
      f"C60: pentagons={c60_pent}=sigma(6), Euler V-E+F={euler_char}=sigma_-1(6)",
      f"C60: 60 vertices, 90 edges, 32 faces (12 pentagons + 20 hexagons)\n"
      f"V-E+F = 60-90+32 = 2 = sigma_{{-1}}(6). Both exact.\n"
      f"Note: Euler characteristic=2 holds for ALL convex polyhedra (not specific to C60).")

# H-CHEM-030: Ice residual entropy ln(3/2) in GZ
ln_3_2 = math.log(3/2)
in_gz_30 = GZ_LOWER <= ln_3_2 <= GZ_UPPER
grade("H-CHEM-030", "🟩", in_gz_30,
      f"Pauling ice entropy: ln(3/2) = {ln_3_2:.4f}, in GZ: {in_gz_30}",
      f"S0 = R*ln(3/2). ln(3/2) = {ln_3_2:.6f}\n"
      f"GZ = [{GZ_LOWER:.4f}, {GZ_UPPER:.4f}]. In range: {in_gz_30}.\n"
      f"Exact. But GZ spans 29% of [0,1]—many constants land in it.")

# ── Summary ──
print("=" * 72)
print("  SUMMARY")
print("=" * 72)
print()

counts = {"🟩": 0, "🟧": 0, "⚪": 0, "⬛": 0}
for hid, emoji, passed, desc, _ in results:
    counts[emoji] = counts.get(emoji, 0) + 1

total_pass = sum(1 for _, _, p, _, _ in results if p)
total = len(results)

print(f"  Total: {total} hypotheses")
print(f"  PASS:  {total_pass}")
print(f"  FAIL:  {total - total_pass}")
print()
print(f"  🟩 Exact/Proven:       {counts['🟩']}")
print(f"  🟧 Structural match:   {counts['🟧']}")
print(f"  ⚪ Trivial/Coincidence: {counts['⚪']}")
print(f"  ⬛ Wrong/Incorrect:     {counts['⬛']}")
print()

# Reclassification note
print("  NOTE ON GRADES:")
print("  Many 🟩 are exact arithmetic but with ad hoc mappings to number 6.")
print("  The chemistry facts are correct; the TECS connections are mostly numerological.")
print("  🟩 means the stated equation/fact is correct, not that the TECS mapping is deep.")
print()

# Print table
print("  Grade | ID          | Result")
print("  ------+-------------+--------")
for hid, emoji, passed, desc, _ in results:
    status = "PASS" if passed else "FAIL"
    short = desc[:55] + "..." if len(desc) > 58 else desc
    print(f"  {emoji}    | {hid:11s} | {status:4s}  {short}")

print()
print("=" * 72)
