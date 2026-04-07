#!/usr/bin/env python3
"""
Verify DNA/RNA Hypotheses H-DNA-001 through H-DNA-030.

Each hypothesis is checked against known molecular biology data and arithmetic.
Grades:
  GREEN  = Exact equation, mathematically proven fact
  ORANGE = Numerically correct within stated tolerance, structurally interesting
  WHITE  = Arithmetically correct but trivial/coincidental
  BLACK  = Arithmetically wrong or factually incorrect

Run: PYTHONPATH=. python3 verify/verify_dna_hypotheses.py
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
    print(f"  {emoji} {hid}: {status} -- {desc}")
    if detail:
        for line in detail.strip().split("\n"):
            print(f"       {line}")
    print()

# =============================================================================
print("=" * 72)
print("  DNA/RNA HYPOTHESES VERIFICATION (H-DNA-001 to 030)")
print("=" * 72)
print()

# ══════════════════════════════════════════════════════════════════════════
# A. DNA Structure (H-DNA-001 to 006)
# ══════════════════════════════════════════════════════════════════════════
print("== A. DNA Structure ==\n")

# H-DNA-001: B-DNA has 10 bp/turn. 10 = sigma(6) - phi(6) = 12 - 2 = 10
# Known: B-DNA has ~10.4-10.5 bp/turn (X-ray crystallography), often rounded to 10
bp_per_turn = 10.4  # actual crystallographic value
sigma6 = sigma(6)   # 12
phi6 = euler_phi(6)  # 2
claim_001 = sigma6 - phi6  # 12 - 2 = 10
err_001 = abs(bp_per_turn - claim_001) / bp_per_turn
grade("H-DNA-001", "WHITE" if err_001 < 0.05 else "BLACK",
      err_001 < 0.05,
      f"B-DNA bp/turn={bp_per_turn}, sigma(6)-phi(6)={claim_001}, err={err_001:.3f}",
      f"sigma(6)=12, phi(6)=2, 12-2=10. Actual ~10.4 bp/turn.\n"
      f"Mapping sigma(6)-phi(6) is ad hoc subtraction of unrelated functions.\n"
      f"Grade: WHITE -- arithmetically close but mapping is contrived.")

# H-DNA-002: Minor groove width 12A = sigma(6)
# Known: B-DNA minor groove width ~5.7A, major groove ~11.7A
# Many sources: minor ~12A width (measured differently), major ~22A
minor_groove = 12.0  # Angstroms (traditional measurement, edge-to-edge)
major_groove = 22.0  # Angstroms
grade("H-DNA-002", "WHITE",
      minor_groove == sigma6,
      f"Minor groove width ~{minor_groove}A = sigma(6)={sigma6}",
      f"Major groove ~{major_groove}A. Minor groove 12A = sigma(6)=12.\n"
      f"Note: Groove widths vary by measurement convention (5.7A vs 12A).\n"
      f"The 12A value is the traditional Calladine-Drew measurement.\n"
      f"Exact integer match but units are arbitrary (Angstroms). Grade: WHITE.")

# H-DNA-003: Helix pitch 34A / rise 3.4A = 10 bp/turn. 3.4 and 34 contain no n=6.
# Check: 34 = ? No clean n=6 relation. 3.4 = ? No clean n=6 relation.
bp_rise = 3.4  # Angstroms
helix_pitch = 34.0  # Angstroms
ratio_003 = helix_pitch / bp_rise  # = 10.0
grade("H-DNA-003", "BLACK",
      False,
      f"Pitch/rise = {helix_pitch}/{bp_rise} = {ratio_003}. No n=6 connection found.",
      f"34 and 3.4 have no clean relation to 6, its divisors, or number-theoretic functions.\n"
      f"34 = 2*17. 3.4 = 17/5. Neither involves 6.\n"
      f"Grade: BLACK -- no meaningful n=6 connection.")

# H-DNA-004: 4 DNA bases = tau(6). 2 purines + 2 pyrimidines = phi(6) + phi(6)
tau6 = tau(6)  # 4
n_bases = 4
n_purines = 2   # A, G
n_pyrimidines = 2  # C, T
grade("H-DNA-004", "ORANGE",
      n_bases == tau6 and n_purines == phi6 and n_pyrimidines == phi6,
      f"4 bases = tau(6)={tau6}. 2 purines + 2 pyrimidines = phi(6)+phi(6)={phi6}+{phi6}",
      f"DNA bases: A(purine), G(purine), C(pyrimidine), T(pyrimidine).\n"
      f"tau(6)=4 = number of divisors of 6 = {{1,2,3,6}}.\n"
      f"phi(6)=2 = Euler totient = count of {{1,5}} coprime to 6.\n"
      f"2+2=4 partition matches purine/pyrimidine split exactly.\n"
      f"Grade: ORANGE -- exact match, biologically real split, but mapping is model-dependent.")

# H-DNA-005: Chargaff's rules give 2 independent ratios = phi(6)
# A=T and G=C. Given 4 bases, 2 constraints -> 2 independent parameters.
chargaff_indep = 2
grade("H-DNA-005", "WHITE",
      chargaff_indep == phi6,
      f"Chargaff gives {chargaff_indep} independent ratios = phi(6)={phi6}",
      f"A=T, G=C -> 2 independent mole fractions (knowing A and G determines all 4).\n"
      f"phi(6)=2. Match is exact but 2 is a very small number -- high coincidence probability.\n"
      f"Grade: WHITE -- trivially small number match.")

# H-DNA-006: B-DNA has 5 bp per half-turn, NOT 6.
# Known: 10.4 bp/turn -> 5.2 bp per half-turn
bp_half_turn = bp_per_turn / 2  # 5.2
grade("H-DNA-006", "BLACK",
      False,
      f"B-DNA has {bp_half_turn} bp/half-turn, NOT 6. Claim refuted.",
      f"10.4 bp/turn / 2 = 5.2 bp/half-turn.\n"
      f"Even the rounded value gives 10/2 = 5, not 6.\n"
      f"Grade: BLACK -- factually wrong.")

# ══════════════════════════════════════════════════════════════════════════
# B. Genetic Code (H-DNA-007 to 012)
# ══════════════════════════════════════════════════════════════════════════
print("== B. Genetic Code ==\n")

# H-DNA-007: 64 codons = 2^6
n_codons = 4**3  # 64
is_2_to_6 = (2**6 == 64)
grade("H-DNA-007", "ORANGE",
      n_codons == 64 and is_2_to_6,
      f"64 codons = 4^3 = 2^6. Six binary digits encode all amino acids.",
      f"4 bases in triplets: 4^3 = 64 = 2^6.\n"
      f"Each base has 2 bits of info (4 states = 2^2), so 3 bases = 6 bits.\n"
      f"This means the genetic code is fundamentally a 6-bit information system.\n"
      f"Grade: ORANGE -- mathematically exact and biologically meaningful.\n"
      f"The 6-bit encoding is not coincidental -- it is the information-theoretic\n"
      f"content of a codon. Connection to perfect number 6 is structural.")

# H-DNA-008: 3 stop codons. 3 is a divisor of 6.
n_stop = 3  # UAA, UAG, UGA
is_divisor = (6 % n_stop == 0)
grade("H-DNA-008", "WHITE",
      n_stop == 3 and is_divisor,
      f"3 stop codons (UAA, UAG, UGA). 3 | 6.",
      f"3 divides 6, yes. But 3 divides many numbers.\n"
      f"3 stop codons is well-established molecular biology.\n"
      f"Grade: WHITE -- trivial divisibility.")

# H-DNA-009: 61 sense codons / 20 amino acids = 3.05 ~= 3
n_sense = 61
n_aa = 20
avg_degeneracy = n_sense / n_aa
grade("H-DNA-009", "WHITE",
      abs(avg_degeneracy - 3.0) < 0.1,
      f"61 sense codons / 20 aa = {avg_degeneracy:.2f} ~= 3 (divisor of 6)",
      f"Average degeneracy ~3.05. Close to 3 but not exact.\n"
      f"21 amino acids if you count selenocysteine -> 61/21 = 2.90.\n"
      f"Grade: WHITE -- approximate match to a small divisor.")

# H-DNA-010: Maximum codon degeneracy = 6 (Leu, Ser, Arg each have 6 codons)
# Known: Leucine (CUU,CUC,CUA,CUG,UUA,UUG) = 6 codons
# Serine (UCU,UCC,UCA,UCG,AGU,AGC) = 6 codons
# Arginine (CGU,CGC,CGA,CGG,AGA,AGG) = 6 codons
leu_codons = ["CUU", "CUC", "CUA", "CUG", "UUA", "UUG"]
ser_codons = ["UCU", "UCC", "UCA", "UCG", "AGU", "AGC"]
arg_codons = ["CGU", "CGC", "CGA", "CGG", "AGA", "AGG"]
max_degeneracy = max(len(leu_codons), len(ser_codons), len(arg_codons))
grade("H-DNA-010", "ORANGE",
      max_degeneracy == 6,
      f"Max codon degeneracy = {max_degeneracy} = 6 (Leu, Ser, Arg)",
      f"Leucine:  {leu_codons} = {len(leu_codons)} codons\n"
      f"Serine:   {ser_codons} = {len(ser_codons)} codons\n"
      f"Arginine: {arg_codons} = {len(arg_codons)} codons\n"
      f"The maximum redundancy in the genetic code is exactly 6.\n"
      f"This is a real biological fact: the most degenerate amino acids\n"
      f"have exactly 6 codons each, not 5 or 7.\n"
      f"Grade: ORANGE -- exact match, genuinely interesting.")

# H-DNA-011: 6 reading frames on double-stranded DNA
# Known: 3 frames on sense strand + 3 frames on antisense strand = 6
n_frames = 6  # well-established
grade("H-DNA-011", "GREEN",
      n_frames == 6,
      f"6 reading frames total (3 forward + 3 reverse) = 6",
      f"Double-stranded DNA has exactly 6 reading frames.\n"
      f"This follows from: 2 strands x 3 possible frame shifts = 6.\n"
      f"tau(6)=4 bases, phi(6)=2 strands, 3 frames per strand, 2*3=6.\n"
      f"ORF finders universally search all 6 frames.\n"
      f"Grade: GREEN -- exact, well-established molecular biology fact.\n"
      f"The number 6 here is genuinely fundamental to DNA information readout.")

# H-DNA-012: 1 start codon + 3 stop codons = 4 = tau(6)
n_start = 1   # AUG (also codes Met)
n_stop_012 = 3
total_special = n_start + n_stop_012
grade("H-DNA-012", "WHITE",
      total_special == tau6,
      f"1 start + 3 stop = {total_special} = tau(6)={tau6}",
      f"AUG is the universal start codon (also codes methionine).\n"
      f"UAA, UAG, UGA are stop codons. 1+3=4=tau(6).\n"
      f"Note: Some organisms use alternative start codons (GUG, UUG).\n"
      f"Grade: WHITE -- 4 is a very common number, match likely coincidental.")

# ══════════════════════════════════════════════════════════════════════════
# C. RNA Biology (H-DNA-013 to 018)
# ══════════════════════════════════════════════════════════════════════════
print("== C. RNA Biology ==\n")

# H-DNA-013: tRNA anticodon loop = 7 nt. tRNA total ~76 nt.
# 76 = ? No clean n=6 relation. 76/6 = 12.67.
trna_length = 76   # typical tRNA
anticodon_loop = 7  # nucleotides
ratio_013 = trna_length / 6
grade("H-DNA-013", "BLACK",
      False,
      f"tRNA ~{trna_length} nt, anticodon loop {anticodon_loop} nt. No clean n=6 relation.",
      f"76/6 = {ratio_013:.2f}. 76 = 4*19. 7 is prime.\n"
      f"Neither 76 nor 7 connects to 6 or its number-theoretic functions.\n"
      f"Grade: BLACK -- no meaningful connection found.")

# H-DNA-014: Ribosome has 2 subunits = phi(6)
n_subunits = 2  # 30S+50S (prokaryote) or 40S+60S (eukaryote)
grade("H-DNA-014", "WHITE",
      n_subunits == phi6,
      f"Ribosome: {n_subunits} subunits (large+small) = phi(6)={phi6}",
      f"Prokaryote: 30S + 50S = 70S. Eukaryote: 40S + 60S = 80S.\n"
      f"2 subunits is universal across all life.\n"
      f"phi(6)=2 match is exact but 2 is trivially small.\n"
      f"Grade: WHITE -- number 2 is too common for meaningful mapping.")

# H-DNA-015: E. coli rRNAs: 23S + 16S + 5S = 3 rRNA species
n_rrna_ecoli = 3  # 23S, 16S, 5S
is_div_6 = (6 % n_rrna_ecoli == 0)
grade("H-DNA-015", "WHITE",
      n_rrna_ecoli == 3 and is_div_6,
      f"E. coli has {n_rrna_ecoli} rRNA species (23S, 16S, 5S). 3 | 6.",
      f"Eukaryotes have 4 rRNAs: 28S, 18S, 5.8S, 5S.\n"
      f"Prokaryote count 3 matches a divisor of 6, but eukaryote count 4 also = tau(6).\n"
      f"Cherry-picking which organism to match which function.\n"
      f"Grade: WHITE -- can match either way, reducing significance.")

# H-DNA-016: mRNA cap = 7-methylguanosine. Poly-A ~200 nt. No n=6 relation.
cap_methyl_pos = 7
poly_a_len = 200  # typical
grade("H-DNA-016", "BLACK",
      False,
      f"mRNA cap: 7-methylguanosine, poly-A ~{poly_a_len} nt. No n=6 connection.",
      f"7 is prime, not a divisor of 6. 200/6 = 33.33.\n"
      f"Grade: BLACK -- no meaningful connection to perfect number 6.")

# H-DNA-017: Spliceosome has 5 snRNAs (U1, U2, U4, U5, U6). U6 is named '6'.
n_snrna = 5  # U1, U2, U4, U5, U6
u6_exists = True  # U6 snRNA is real
grade("H-DNA-017", "WHITE",
      n_snrna == 5 and u6_exists,
      f"Spliceosome: {n_snrna} snRNAs. U6 snRNA exists but 5 != 6.",
      f"snRNAs: U1, U2, U4, U5, U6 (note: no U3, it is an snoRNA).\n"
      f"5 total snRNAs, not 6. U6 is just a naming convention.\n"
      f"U6 snRNA is catalytically critical (metalloenzyme activity).\n"
      f"The name 'U6' containing 6 is a nomenclature artifact, not structural.\n"
      f"Grade: WHITE -- naming coincidence only.")

# H-DNA-018: microRNA seed region = 6-8 nt. Specifically positions 2-7 = 6 nt.
mirna_length = 22  # typical
seed_start = 2
seed_end = 7
seed_length = seed_end - seed_start + 1  # 6
grade("H-DNA-018", "ORANGE",
      seed_length == 6,
      f"miRNA seed region: positions {seed_start}-{seed_end} = {seed_length} nt = 6",
      f"miRNA total ~{mirna_length} nt. Seed region (pos 2-7) = 6 nucleotides.\n"
      f"The seed is the primary determinant of target recognition.\n"
      f"Some definitions extend to pos 2-8 (7 nt), but the core seed is 6 nt.\n"
      f"This 6-nt seed has 4^6 = 4096 possible sequences,\n"
      f"enough to target ~60% of human mRNAs.\n"
      f"Grade: ORANGE -- genuinely interesting that the core recognition\n"
      f"element is exactly 6 nucleotides.")

# ══════════════════════════════════════════════════════════════════════════
# D. DNA Repair (H-DNA-019 to 024)
# ══════════════════════════════════════════════════════════════════════════
print("== D. DNA Repair ==\n")

# H-DNA-019: Major DNA repair pathways = 6?
# Standard textbook lists: BER, NER, MMR, HR, NHEJ. That's 5.
# TLS (translesion synthesis) is sometimes listed as 6th.
# Also: Direct reversal, MMEJ/alt-EJ, Fanconi anemia pathway...
# The count depends heavily on classification scheme.
pathways = ["BER", "NER", "MMR", "HR", "NHEJ"]
extended = pathways + ["TLS"]
grade("H-DNA-019", "WHITE",
      len(extended) == 6,
      f"DNA repair pathways: core={len(pathways)}, with TLS={len(extended)}",
      f"Core 5: {', '.join(pathways)}\n"
      f"Extended to 6 by adding TLS (translesion synthesis).\n"
      f"But this is classification-dependent:\n"
      f"  - Some texts list 5 (no TLS)\n"
      f"  - Others list 7+ (adding direct reversal, MMEJ, Fanconi)\n"
      f"  - Alberts 'Molecular Biology of the Cell' lists 5 main pathways\n"
      f"Cherry-picking TLS to reach 6 is ad hoc.\n"
      f"Grade: WHITE -- pathway count is classification-dependent.")

# H-DNA-020: Polymerase proofreading error rate ~10^-7
# Known: Replication fidelity ~10^-9 to 10^-10 per bp (after all correction).
# Polymerase alone (no proofreading): ~10^-4 to 10^-5
# With proofreading: ~10^-6 to 10^-7
# With mismatch repair: ~10^-9 to 10^-10
error_poly = 1e-4   # polymerase alone
error_proof = 1e-7   # with proofreading (3' -> 5' exonuclease)
error_final = 1e-10  # after mismatch repair
# Check: -log10(error_proof) = 7, not 6
neg_log_proof = -math.log10(error_proof)
grade("H-DNA-020", "BLACK",
      False,
      f"Polymerase + proofreading error ~10^-7. -log10 = {neg_log_proof}, not 6.",
      f"Error rates: polymerase only ~10^-4, +proofreading ~10^-7, +MMR ~10^-10.\n"
      f"Polymerase alone is ~10^-4 to 10^-5 per nucleotide.\n"
      f"None of these exponents equal 6.\n"
      f"Grade: BLACK -- no n=6 connection in error rates.")

# H-DNA-021: Okazaki fragments ~100-200 bp (prokaryotes), ~1000-2000 bp (eukaryotes)
# No clean n=6 connection
okazaki_prok = (100, 200)
okazaki_euk = (1000, 2000)
grade("H-DNA-021", "BLACK",
      False,
      f"Okazaki fragments: prokaryote {okazaki_prok} bp, eukaryote {okazaki_euk} bp.",
      f"No division by 6 gives meaningful results.\n"
      f"100/6=16.7, 200/6=33.3, 1000/6=166.7, 2000/6=333.3.\n"
      f"Grade: BLACK -- no n=6 connection.")

# H-DNA-022: Human telomere repeat = TTAGGG = exactly 6 nucleotides
telomere_repeat = "TTAGGG"
telomere_len = len(telomere_repeat)
grade("H-DNA-022", "GREEN",
      telomere_len == 6,
      f"Human telomere repeat '{telomere_repeat}' = {telomere_len} nucleotides = 6!",
      f"This is a verified biological fact.\n"
      f"Human (and all vertebrate) telomeres consist of tandem repeats of TTAGGG.\n"
      f"The repeat unit is exactly 6 nucleotides long.\n"
      f"~2500 repeats per telomere, total ~15,000 bp = 15 kb.\n"
      f"The 6-mer repeat is conserved across all vertebrates.\n"
      f"Note: G-rich strand forms G-quadruplex structures with 4 G-runs.\n"
      f"tau(6)=4 Gs in the repeat? Actually 3 Gs (TTAGGG), not 4.\n"
      f"Grade: GREEN -- exact, fundamental, well-established fact.\n"
      f"The basic unit of chromosome end protection is a 6-mer.")

# H-DNA-023: Telomerase RNA template ~451 nt. No obvious n=6 connection.
hterc_len = 451  # human TERC (hTR)
grade("H-DNA-023", "BLACK",
      False,
      f"Human telomerase RNA (hTERC) = {hterc_len} nt. {hterc_len}/6 = {hterc_len/6:.1f}.",
      f"451 = 11 * 41. No clean relation to 6.\n"
      f"The template region itself is ~11 nt (CUAACCCUAAC), also not 6.\n"
      f"Grade: BLACK -- no meaningful connection.")

# H-DNA-024: RecA filament: 6 RecA monomers per helical turn
# Known: RecA forms a right-handed helical filament on DNA.
# ~6.2 RecA monomers per turn of the RecA filament (not per turn of DNA).
# Each RecA monomer covers 3 nucleotides.
# Filament pitch ~95 Angstroms, 6 monomers per turn.
reca_per_turn = 6.2  # monomers per helical turn of RecA filament
reca_nt_per_monomer = 3  # nucleotides per RecA monomer
grade("H-DNA-024", "ORANGE",
      abs(reca_per_turn - 6.0) < 0.5,
      f"RecA filament: ~{reca_per_turn} monomers/turn (close to 6)",
      f"RecA forms helical filament on ssDNA for homologous recombination.\n"
      f"~6.2 monomers per helical turn (X-ray: Story et al. 1992, Nature).\n"
      f"Each monomer covers 3 nt (a divisor of 6).\n"
      f"Total nt per filament turn: 6.2 * 3 ~= 18.6 ~= 3*6.\n"
      f"Grade: ORANGE -- ~6 monomers/turn is a real structural parameter,\n"
      f"close to 6 but not exactly 6 (6.2). Still noteworthy.")

# ══════════════════════════════════════════════════════════════════════════
# E. Epigenetics & Regulation (H-DNA-025 to 030)
# ══════════════════════════════════════════════════════════════════════════
print("== E. Epigenetics & Regulation ==\n")

# H-DNA-025: 4 core histone types = tau(6). Octamer = 2*4 = 8.
n_histone_types = 4  # H2A, H2B, H3, H4
octamer = 8  # 2 copies of each
grade("H-DNA-025", "WHITE",
      n_histone_types == tau6,
      f"4 core histone types (H2A,H2B,H3,H4) = tau(6)={tau6}. Octamer = {octamer}.",
      f"Nucleosome core: 2x(H2A+H2B+H3+H4) = 8 histone proteins.\n"
      f"4 types = tau(6)=4 is exact. 8 = 2*tau(6) = phi(6)*tau(6).\n"
      f"But 4 histone types is a well-known fact and 4 is very common.\n"
      f"Grade: WHITE -- exact match but 4 is a small, common number.")

# H-DNA-026: Nucleosome wraps 147 bp. 147 = ?
# 147 = 3 * 49 = 3 * 7^2. Not obviously related to 6.
# But 147/6 = 24.5. Not clean.
nuc_wrap = 147
nuc_repeat = 200  # typical repeat length
linker = nuc_repeat - nuc_wrap  # ~53
grade("H-DNA-026", "BLACK",
      False,
      f"Nucleosome wraps {nuc_wrap} bp (repeat ~{nuc_repeat} bp). {nuc_wrap}/6={nuc_wrap/6:.1f}.",
      f"147 = 3 * 7^2. Repeat ~200 bp, linker ~{linker} bp.\n"
      f"No clean division by 6 or relation to its functions.\n"
      f"Grade: BLACK -- no meaningful n=6 connection.")

# H-DNA-027: CpG methylation at carbon 5 of cytosine.
# 5 is not a divisor of 6. 5-methylcytosine (5mC).
methyl_position = 5
grade("H-DNA-027", "BLACK",
      False,
      f"CpG methylation at position {methyl_position} of cytosine. 5 is not related to 6.",
      f"5-methylcytosine (5mC) is the main epigenetic mark.\n"
      f"Position 5 on the pyrimidine ring. 5 does not divide 6.\n"
      f"Grade: BLACK -- no n=6 connection.")

# H-DNA-028: TATA box at -25 to -30. Distance from CAAT box ~50 bp. No n=6.
tata_pos = -25  # to -30
caat_pos = -75
distance = abs(caat_pos - tata_pos)  # ~50
grade("H-DNA-028", "BLACK",
      False,
      f"TATA box at ~{tata_pos}, CAAT at ~{caat_pos}, distance ~{distance} bp.",
      f"50/6 = 8.33. 25/6 = 4.17. 75/6 = 12.5.\n"
      f"No clean relation to 6.\n"
      f"Grade: BLACK -- no meaningful connection.")

# H-DNA-029: Lac operon has 3 structural genes = divisor of 6
lac_genes = 3  # lacZ, lacY, lacA
grade("H-DNA-029", "WHITE",
      6 % lac_genes == 0,
      f"Lac operon: {lac_genes} structural genes (lacZ, lacY, lacA). 3 | 6.",
      f"3 is a divisor of 6, yes. But 3 genes in one operon is ordinary.\n"
      f"Many operons have different gene counts (trp operon has 5).\n"
      f"Grade: WHITE -- trivial match, cherry-picking this operon.")

# H-DNA-030: Gene expression steps = 6?
# Transcription, 5' capping, splicing, 3' polyadenylation, export, translation = 6
# But this is for eukaryotes only. Prokaryotes: transcription + translation = 2
# Even in eukaryotes, some count differently.
euk_steps = ["transcription", "5' capping", "splicing",
             "3' polyadenylation", "nuclear export", "translation"]
prok_steps = ["transcription", "translation"]
grade("H-DNA-030", "WHITE",
      len(euk_steps) == 6,
      f"Eukaryotic gene expression: {len(euk_steps)} steps (if counted this way).",
      f"Steps: {', '.join(euk_steps)}\n"
      f"But step count depends on granularity:\n"
      f"  - Could add: RNA editing, quality control, mRNA decay = 9\n"
      f"  - Could merge: capping+splicing+polyA = 'processing' = 4 steps\n"
      f"  - Prokaryotes: just 2 (transcription + translation, coupled)\n"
      f"Grade: WHITE -- classification-dependent, can be made to fit any number.")

# ══════════════════════════════════════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════════════════════════════════════
print("=" * 72)
print("  SUMMARY")
print("=" * 72)
print()

# Count by grade
green = sum(1 for r in results if r[1] == "GREEN")
orange = sum(1 for r in results if r[1] == "ORANGE")
white = sum(1 for r in results if r[1] == "WHITE")
black = sum(1 for r in results if r[1] == "BLACK")

print(f"  GREEN  (exact proven):           {green}")
print(f"  ORANGE (interesting match):      {orange}")
print(f"  WHITE  (trivial/coincidence):    {white}")
print(f"  BLACK  (wrong/no connection):    {black}")
print(f"  TOTAL:                           {len(results)}")
print()

# Grade distribution
total = len(results)
print(f"  Meaningful (GREEN+ORANGE): {green+orange}/{total} = {100*(green+orange)/total:.1f}%")
print(f"  Trivial (WHITE):           {white}/{total} = {100*white/total:.1f}%")
print(f"  Refuted (BLACK):           {black}/{total} = {100*black/total:.1f}%")
print()

# Top findings
print("  TOP FINDINGS (GREEN + ORANGE):")
print("  " + "-" * 60)
for r in results:
    if r[1] in ("GREEN", "ORANGE"):
        print(f"    {r[1]:6s} {r[0]}: {r[3]}")
print()

# Texas Sharpshooter analysis
print("  TEXAS SHARPSHOOTER ANALYSIS:")
print("  " + "-" * 60)
# With 30 hypotheses testing against n=6, expected random matches?
# If we pick 30 biological numbers and check if any relate to 6...
# Numbers 1-10 each have ~30% chance of being a divisor of some n
# Being generous: P(random number relates to 6) ~ 0.2
# Expected by chance: 30 * 0.2 = 6 matches
# We found: green+orange meaningful matches
p_random = 0.2  # generous estimate
expected_random = total * p_random
print(f"    Hypotheses tested:    {total}")
print(f"    Meaningful matches:   {green + orange}")
print(f"    Expected by chance:   {expected_random:.1f} (at p_random={p_random})")
print(f"    Excess:               {(green+orange) - expected_random:.1f}")
print()

# Highlight genuinely interesting ones
print("  GENUINELY INTERESTING (not just number-matching):")
print("  " + "-" * 60)
genuinely = [
    ("H-DNA-007", "64 codons = 2^6: genetic code IS a 6-bit system"),
    ("H-DNA-010", "Max codon degeneracy = exactly 6 (Leu, Ser, Arg)"),
    ("H-DNA-011", "6 reading frames on double-stranded DNA"),
    ("H-DNA-022", "Telomere repeat TTAGGG = exactly 6 nucleotides"),
]
for gid, gdesc in genuinely:
    print(f"    {gid}: {gdesc}")
print()
print("  These 4 are exact, well-established biological facts where 6 appears")
print("  as a fundamental structural parameter, not a forced mapping.")
print()

# ASCII histogram
print("  GRADE DISTRIBUTION:")
print("  " + "-" * 60)
bar_scale = 2
print(f"    GREEN  |{'#' * (green * bar_scale)}| {green}")
print(f"    ORANGE |{'#' * (orange * bar_scale)}| {orange}")
print(f"    WHITE  |{'#' * (white * bar_scale)}| {white}")
print(f"    BLACK  |{'#' * (black * bar_scale)}| {black}")
print()

print("=" * 72)
print("  VERIFICATION COMPLETE")
print("=" * 72)
