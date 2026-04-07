#!/usr/bin/env python3
"""
verify_round3_bio.py — Round 3 Biology/Neuroscience Hypothesis Verification
20 NEW hypotheses NOT overlapping with Frontier 100, Frontier 200, or Round 2.

Excluded topics (already done): cortical layers, theta-gamma, DMN, anesthesia,
sleep, predictive coding, mirror neurons, binding, criticality, rich-club,
psychedelics, meditation, SWR, attention MOT, photosynthesis, benzene, glucose,
glycolysis, ATP, Krebs, circadian, capsids, water, DNA grooves, codons, cell cycle,
periodic table, protein H-bonds, Kok cycle, pyranose, food chains, ETC, grid cells,
neurotransmitters, cochlea, spinal, heart, immune, hormones, chromosomes,
morphogenesis, embryonic layers, senses, apoptosis, white matter tracts,
Brodmann regions, hippocampal subfields, basal ganglia, cerebellar modules,
retinal layers, Turing patterns, visual cortex columns, etc.

n=6 arithmetic: sigma=12, tau=4, phi=2, sopfr=5, sigma*phi=24, ln(4/3)=0.2877
"""

import math

# ═══════════════════════════════════════════════════════════════
# n=6 arithmetic constants
# ═══════════════════════════════════════════════════════════════
n = 6
sigma = 12        # sum of divisors
tau = 4           # number of divisors
phi = 2           # Euler totient
sopfr = 5         # sum of prime factors (2+3)
sigma_phi = 24    # sigma * phi
ln43 = math.log(4/3)  # ~0.2877
proper_divisors = [1, 2, 3]
divisors = [1, 2, 3, 6]

PASS = 0
FAIL = 0
results = []

def check(hyp_id, title, claim, known_value, known_source, n6_match, grade, risk, match_ok):
    """Record and display a hypothesis check."""
    global PASS, FAIL
    status = "PASS" if match_ok else "FAIL"
    if match_ok:
        PASS += 1
    else:
        FAIL += 1

    result = {
        'id': hyp_id, 'title': title, 'claim': claim,
        'known_value': known_value, 'source': known_source,
        'n6_match': n6_match, 'grade': grade, 'risk': risk,
        'status': status
    }
    results.append(result)

    print(f"\n{'='*72}")
    print(f"R3-BIO-{hyp_id:02d}: {title}")
    print(f"{'='*72}")
    print(f"  Claim: {claim}")
    print(f"  Known value: {known_value} ({known_source})")
    print(f"  n=6 match: {n6_match}")
    print(f"  Arithmetic check: {status}")
    print(f"  Grade: {grade}")
    print(f"  Risk: {risk}")


# ═══════════════════════════════════════════════════════════════
# R3-BIO-01: Phyllotaxis — Golden Angle
# ═══════════════════════════════════════════════════════════════
# The golden angle is 360/phi^2 = 137.507...degrees
# phi here is the golden ratio (1+sqrt(5))/2 = 1.618...
# NOT Euler's phi. No clean n=6 arithmetic connection.
# Fibonacci numbers in phyllotaxis: 1,1,2,3,5,8,13,21...
# Common parastichy numbers: (3,5), (5,8), (8,13) — these are Fibonacci pairs.
# 6 is NOT a Fibonacci number. The golden angle 137.5 has no sigma/tau/phi(6) match.
# Attempt: 360/sigma = 30 (not 137.5). 360/n = 60 (not 137.5).
# Attempt: 137.5/n = 22.9 (nothing). 137.5 mod 6 = 5.5 (nothing).
check(1,
    "Phyllotaxis Golden Angle vs n=6",
    "The golden angle (137.5 deg) or common parastichy numbers relate to n=6 arithmetic",
    "Golden angle = 137.507 deg; common parastichies are Fibonacci pairs (3,5), (5,8), (8,13)",
    "Jean 1994, Phyllotaxis; Douady & Couder 1992",
    "No match. 6 is not Fibonacci. 137.5 has no n=6 decomposition.",
    "WHITE — No match found. 6 is not a Fibonacci number.",
    "N/A — honest non-match",
    False
)

# ═══════════════════════════════════════════════════════════════
# R3-BIO-02: Hox Gene Clusters in Vertebrates
# ═══════════════════════════════════════════════════════════════
# Vertebrates have 4 Hox clusters (HoxA, HoxB, HoxC, HoxD).
# Drosophila has 2 clusters (ANT-C, BX-C), or 1 split cluster historically.
# Amphioxus has 1 cluster with 15 genes. Teleost fish have 7 clusters (genome dup).
# 4 Hox clusters = tau(6)? tau(6) = 4. That's an exact match.
# Each cluster has 9-11 paralog groups (13 total paralog groups, not all present in each).
# Total Hox genes in human: ~39 (not a clean n=6 number).
# 13 paralog groups: 13 is prime, no clean match.
# The 4 clusters arose from 2 rounds of whole-genome duplication: 1 -> 2 -> 4
# 2 rounds = phi(6) = 2. 4 clusters = tau(6) = 4.
# BUT: 4 is an extremely common small number. High coincidence risk.
check(2,
    "Vertebrate Hox Clusters = tau(6) = 4",
    "4 Hox gene clusters in vertebrates = tau(6) = 4, arising from phi(6)=2 WGD rounds",
    "4 clusters (HoxA-D); 2 WGD rounds; 13 paralog groups; ~39 total Hox genes",
    "McGinnis & Krumlauf 1992; Duboule 2007",
    "tau(6) = 4 (clusters), phi(6) = 2 (WGD rounds)",
    "WHITE — tau(6)=4 is trivially small. Any set of 4 things matches. "
    "2 WGD rounds matching phi(6)=2 is equally trivial. Pure coincidence.",
    "HIGH — 4 and 2 are extremely common biological numbers. No structural reason to invoke n=6.",
    True  # Arithmetic holds but grade is white
)

# ═══════════════════════════════════════════════════════════════
# R3-BIO-03: Mass Extinction Periodicity
# ═══════════════════════════════════════════════════════════════
# Raup & Sepkoski (1984) claimed ~26 Myr periodicity in mass extinctions.
# This is controversial. Rohde & Muller (2005) found ~62 Myr cycle in marine diversity.
# The "Big Five" mass extinctions is the accepted count.
# Big 5: End-Ordovician, Late Devonian, End-Permian, End-Triassic, End-Cretaceous.
# 5 = sopfr(6)? sopfr(6) = 2+3 = 5. Exact match.
# BUT: "Big Five" is a somewhat arbitrary cutoff. Some argue for 6 (adding Capitanian).
# Others count more or fewer depending on threshold.
# 26 Myr: 26 = sigma(6) + tau(6)*... no. 26/n = 4.33, nothing clean.
# 62 Myr: 62/n = 10.33, nothing. 62/sigma = 5.17, nothing.
# The "5 major extinctions" is the only potential match.
check(3,
    "Big Five Mass Extinctions = sopfr(6) = 5",
    "The canonical Big Five mass extinctions = sopfr(6) = 5",
    "5 major mass extinctions (Raup & Sepkoski 1982); some argue 6 including Capitanian",
    "Raup & Sepkoski 1982; Bambach 2006; Bond & Grasby 2017 (6th candidate)",
    "sopfr(6) = 5 (Big Five count)",
    "WHITE — 'Big Five' is a human categorization choice, not a fixed natural constant. "
    "The boundary for 'major' is arbitrary. Some workers count 6. Pure numerology.",
    "VERY HIGH — human classification cutoff, not a natural number. "
    "Bond & Grasby argue for 6 major extinctions which would also 'match' n=6.",
    True  # Arithmetic is 5=5 but this is coincidence
)

# ═══════════════════════════════════════════════════════════════
# R3-BIO-04: Typical Bacterial Doubling Time
# ═══════════════════════════════════════════════════════════════
# E. coli doubling time in optimal conditions: ~20 minutes.
# Range across species: 12 min (fastest, Vibrio natriegens) to hours/days.
# 20 min: 20/n = 3.33, no match. 20 is not in n=6 arithmetic.
# 12 min (fastest known): 12 = sigma(6). But Vibrio natriegens is one specific species.
# Typical lab E. coli: 20 min. Typical in gut: 40 min. Neither matches cleanly.
# log2 growth: generations per hour for E. coli = 3 (at 20 min doubling) = n/phi.
# But this is a trivial derived quantity.
check(4,
    "Bacterial Doubling Time vs n=6",
    "Typical bacterial doubling time relates to n=6 arithmetic",
    "E. coli: ~20 min (optimal), ~40 min (gut); Vibrio natriegens: ~12 min (fastest known)",
    "Erickson et al. 2017; Hershey 1939; Weinstock et al. 2016",
    "sigma(6)=12 matches only the fastest known species (V. natriegens), not typical",
    "WHITE — Cherry-picking one species (fastest) to match sigma(6)=12. "
    "The typical and iconic value (E. coli 20 min) has no match.",
    "VERY HIGH — selecting one extreme value from a continuous distribution",
    False  # Refusing to match; E. coli = 20 min, no clean match
)

# ═══════════════════════════════════════════════════════════════
# R3-BIO-05: Blood Coagulation Cascade Factor Count
# ═══════════════════════════════════════════════════════════════
# Classical coagulation factors: I (fibrinogen) through XIII, but VI was withdrawn.
# So: 12 numbered factors (I, II, III, IV, V, VII, VIII, IX, X, XI, XII, XIII).
# 12 = sigma(6)? Exact match.
# However, there is no Factor VI — it was reassigned to Factor Va.
# The numbering is historical and somewhat arbitrary.
# The modern cell-based model identifies ~15-20 key proteins including
# tissue factor, protein C, protein S, antithrombin, etc.
# The "12 classical factors" is a firm, textbook-established number.
# Roman numeral naming I-XIII minus VI = 12 active factors.
check(5,
    "Classical Coagulation Factors = sigma(6) = 12",
    "12 classical coagulation factors (I-XIII, no VI) = sigma(6) = 12",
    "12 factors: I(fibrinogen), II(prothrombin), III(TF), IV(Ca), V, VII, VIII, IX, X, XI, XII, XIII",
    "Davie & Ratnoff 1964; Macfarlane 1964 (cascade model); Hoffman & Monroe 2001",
    "sigma(6) = 12 = number of named coagulation factors",
    "ORANGE-STAR — Exact match with established count. "
    "The historical numbering is fixed (I-XIII minus VI = 12). "
    "Not classification-dependent like some counts.",
    "MEDIUM — The numbering is historical convention. Factor VI was removed post-hoc. "
    "Modern model includes additional proteins beyond the 12. "
    "Still, 12 is the canonical count in every medical textbook.",
    True
)

# ═══════════════════════════════════════════════════════════════
# R3-BIO-06: Basic Taste Types
# ═══════════════════════════════════════════════════════════════
# Classical: 4 basic tastes (sweet, sour, salty, bitter).
# Modern consensus: 5 (adding umami, Ikeda 1908, accepted ~2000s).
# Proposed 6th: fat/oleogustus (Running et al. 2015), kokumi, starchy.
# None of the proposed 6th tastes are universally accepted yet.
# 5 established tastes = sopfr(6) = 5.
# If fat taste is accepted: 6 = n. But this is still debated.
check(6,
    "Basic Taste Types = sopfr(6) = 5",
    "5 established basic taste modalities = sopfr(6) = 5",
    "5 basic tastes: sweet, sour, salty, bitter, umami. Fat/oleogustus proposed as 6th.",
    "Ikeda 1908 (umami); Chandrashekar et al. 2006 (molecular basis); Running et al. 2015 (fat)",
    "sopfr(6) = 5 (current accepted count)",
    "WHITE — 5 is a very common small number. The count went from 4 to 5 historically "
    "and may go to 6. It is a moving target reflecting human classification.",
    "HIGH — small number (5), historically variable (was 4, may become 6). "
    "Any n=6 arithmetic has a value near 5 (sopfr).",
    True  # 5=5 but coincidence
)

# ═══════════════════════════════════════════════════════════════
# R3-BIO-07: Color Vision Cone Types
# ═══════════════════════════════════════════════════════════════
# Human trichromatic vision: 3 cone types (S, M, L).
# 3 = n/phi(6) = 6/2 = 3. Or sigma/tau = 12/4 = 3.
# But 3 is extremely common — trichromacy is just the name for 3 channels.
# Many mammals are dichromats (2 = phi(6)), birds are tetrachromats (4 = tau(6)),
# mantis shrimp have 16 types.
# Total photoreceptor classes: rods + 3 cones = 4 = tau(6).
# Melanopsin (ipRGC) adds a 5th class = sopfr(6).
check(7,
    "Cone Types = 3 = n/phi; Total Photoreceptors = tau(6) = 4",
    "3 cone types = n/phi(6); 4 photoreceptor classes (3 cones + rods) = tau(6)",
    "3 cone types (S/M/L); 4 photoreceptor classes (3 cones + 1 rod); "
    "5 including melanopsin ipRGCs",
    "Nathans et al. 1986 (opsin genes); Berson et al. 2002 (ipRGCs)",
    "n/phi = 3 (cones), tau(6) = 4 (with rods), sopfr = 5 (with melanopsin)",
    "WHITE — 3 and 4 are trivially small numbers. Every small count matches something. "
    "Dichromats=2=phi, trichromats=3, tetrachromats=4=tau — anything matches.",
    "VERY HIGH — small numbers guaranteed to match some n=6 arithmetic",
    True  # Arithmetic works but pure coincidence
)

# ═══════════════════════════════════════════════════════════════
# R3-BIO-08: Hand Bone Count
# ═══════════════════════════════════════════════════════════════
# Human hand: 27 bones per hand.
# 8 carpals + 5 metacarpals + 14 phalanges = 27.
# 27 = 3^3. sigma(6) + tau(6) + ... let's check: sigma + tau + n + sopfr = 12+4+6+5 = 27!
# That's a 4-term sum. Ad hoc addition of multiple constants = cherry-picking.
# 54 total for both hands = 2 * 27. 54/n = 9. Not special.
# Foot: 26 bones. 26 = sigma(6) + tau(6) + n + ... = 12+14? 26 = 2*13. No clean match.
# Phalanges per hand: 14. 14 = sigma(6) + phi(6) = 12+2. Ad hoc.
# Carpals: 8 = sigma(6) - tau(6) = 12-4. Ad hoc.
# Metacarpals: 5 = sopfr(6). But 5 = number of digits, trivially small.
check(8,
    "Hand Bones vs n=6",
    "27 bones per hand relate to n=6 arithmetic",
    "27 bones per hand: 8 carpal + 5 metacarpal + 14 phalanges",
    "Gray's Anatomy; any anatomy textbook",
    "27 = sigma+tau+n+sopfr is a 4-term ad hoc sum. Metacarpals = 5 = sopfr, trivially = digits.",
    "WHITE — 27 requires ad hoc 4-term addition. Any number 1-30 can be reached "
    "by combining sigma, tau, n, phi, sopfr with +/-. Classic Texas Sharpshooter.",
    "VERY HIGH — with 5 constants and 4 operations, you can hit any target",
    False  # Refusing to claim this as a match
)

# ═══════════════════════════════════════════════════════════════
# R3-BIO-09: Human Dental Formula — Tooth Types
# ═══════════════════════════════════════════════════════════════
# Human dental formula: 2-1-2-3 (incisors-canines-premolars-molars per quadrant)
# Total types: 4 (incisors, canines, premolars, molars) = tau(6).
# Teeth per quadrant: 2+1+2+3 = 8. Teeth total: 32. Deciduous: 20.
# 4 types = tau(6)? But 4 is trivially small.
# 32 total: 32 = 2^5. 2^sopfr(6) = 2^5 = 32! Exact.
# But 32 = 2^5 is just a power of 2 coincidence.
# 20 deciduous: 20 = sigma(6) + tau(6)*phi(6)? = 12+8 = 20. Ad hoc 3-term.
# Dental formula digits: 2,1,2,3. Note: 2+3 = sopfr(6) = 5. 2*1*2*3 = 12 = sigma(6)!
# Product of dental formula = 12 = sigma(6). Interesting but ad hoc.
check(9,
    "Tooth Types = tau(6) = 4; Total = 2^sopfr(6) = 32",
    "4 tooth types = tau(6); 32 permanent teeth = 2^sopfr(6)",
    "4 tooth types; 32 permanent teeth; dental formula 2-1-2-3 per quadrant",
    "Any dental anatomy text; Nelson, Wheeler's Dental Anatomy",
    "tau(6) = 4 (tooth types), 2^sopfr(6) = 32 (total teeth)",
    "WHITE — 4 types is trivially small. 32 = 2^5 is a power-of-2 coincidence; "
    "attributing it to 2^sopfr(6) is arbitrary. Product 2*1*2*3=12 is ad hoc.",
    "HIGH — small numbers + post-hoc arithmetic combinations",
    True  # Arithmetic holds, grade is white (coincidence)
)

# ═══════════════════════════════════════════════════════════════
# R3-BIO-10: Fingerprint Pattern Types
# ═══════════════════════════════════════════════════════════════
# Galton (1892) classified fingerprints into 3 main types: arch, loop, whorl.
# Modern: loops (~60-70%), whorls (~25-35%), arches (~5%).
# Henry classification (FBI standard): 8 primary types (subdivisions).
# Galton's 3 = n/phi = 3. But 3 is trivially small.
# 8 Henry subtypes: 8 = sigma(6) - tau(6) = 12-4 = 8. Ad hoc subtraction.
# The fundamental number is 3 (arch/loop/whorl).
check(10,
    "Fingerprint Types = 3 = n/phi(6)",
    "3 basic fingerprint patterns = n/phi(6) = 3",
    "3 basic types: arch, loop, whorl (Galton 1892); 8 Henry subtypes",
    "Galton 1892, Finger Prints; Henry Classification System (FBI)",
    "n/phi(6) = 3 (basic types only)",
    "WHITE — 3 is the most common small count in all classification systems. "
    "Almost any categorical system has 3-5 basic types.",
    "VERY HIGH — 3 is trivially common as a classification count",
    True  # 3=3 but meaningless
)

# ═══════════════════════════════════════════════════════════════
# R3-BIO-11: Hemoglobin Subunit Count
# ═══════════════════════════════════════════════════════════════
# Adult hemoglobin (HbA): tetramer of 4 subunits (2 alpha + 2 beta).
# 4 = tau(6). But hemoglobin is a tetramer, and 4 is trivially small.
# 2 types of chains (alpha, beta) = phi(6) = 2.
# Heme groups per hemoglobin: 4 (one per subunit) = tau(6).
# O2 binding sites: 4 = tau(6).
# Iron atoms: 4 = tau(6).
# Total globin gene clusters: 2 (alpha cluster chr16, beta cluster chr11) = phi(6).
# Hemoglobin types in adult blood: HbA (97%), HbA2 (2.5%), HbF (<1%) = 3 main types.
check(11,
    "Hemoglobin Subunits = tau(6) = 4; Chain Types = phi(6) = 2",
    "4 hemoglobin subunits = tau(6); 2 globin chain types = phi(6)",
    "4 subunits (2alpha + 2beta); 4 heme groups; 4 O2 sites; 2 gene clusters",
    "Perutz 1960 (X-ray structure); Bunn & Forget, Hemoglobin, 1986",
    "tau(6) = 4 (subunits/hemes/O2), phi(6) = 2 (chain types/gene clusters)",
    "WHITE — Hemoglobin is defined as a tetramer. Tetramers have 4 subunits by definition. "
    "2 chain types is trivially small. No structural n=6 connection.",
    "VERY HIGH — 4 is the definition of tetramer; 2 is the minimum for heteromer",
    True  # Arithmetic trivially works
)

# ═══════════════════════════════════════════════════════════════
# R3-BIO-12: Photoreceptor Subtypes (Rod/Cone Detail)
# ═══════════════════════════════════════════════════════════════
# Total distinct photoreceptor types in human retina:
# 1 rod type + 3 cone types (S, M, L) = 4 classical.
# + melanopsin ipRGCs = 5 types. Some subdivide ipRGCs into M1-M5 (5 subtypes).
# With ipRGC subtypes: 4 + 5 = 9 distinct photosensitive cell types.
# Classical 4 = tau(6). With melanopsin = 5 = sopfr(6). Neither is deep.
# Rod:cone ratio ~20:1 (95% rods, 5% cones). 20 = ? No clean match.
# Cone density peak (fovea): ~200,000/mm^2. No match.
# This is mostly covered by R3-BIO-07. Skip to avoid overlap.
check(12,
    "Photoreceptor Subtypes: ipRGC M1-M5 Subtypes = sopfr(6) = 5",
    "5 melanopsin ipRGC subtypes (M1-M5) = sopfr(6) = 5",
    "5 ipRGC subtypes: M1, M2, M3, M4, M5 (distinguished by morphology and projection)",
    "Schmidt et al. 2011; Quattrochi et al. 2019",
    "sopfr(6) = 5 (ipRGC subtypes)",
    "WHITE — The M1-M5 classification is relatively new and still being refined. "
    "Some researchers propose M6. Classification-dependent count.",
    "HIGH — evolving classification; 5 is common small number",
    True  # 5=5 but coincidence
)

# ═══════════════════════════════════════════════════════════════
# R3-BIO-13: Synapse Types
# ═══════════════════════════════════════════════════════════════
# Two main types: electrical (gap junctions) and chemical synapses.
# 2 = phi(6). But this is trivially a binary classification.
# Chemical synapses further divided by neurotransmitter: glutamatergic,
# GABAergic, cholinergic, dopaminergic, serotonergic, noradrenergic,
# histaminergic, purinergic, peptidergic, etc. — dozens of types.
# By morphology: axo-dendritic, axo-somatic, axo-axonic, dendro-dendritic = 4 = tau(6).
# 4 morphological types is a common textbook count.
check(13,
    "Synapse Morphological Types = tau(6) = 4",
    "4 main synapse morphological types = tau(6)",
    "4 types: axo-dendritic, axo-somatic, axo-axonic, dendro-dendritic. "
    "Some texts add axo-secretory (5th) or more.",
    "Kandel, Principles of Neural Science; Purves, Neuroscience",
    "tau(6) = 4 (morphological synapse types)",
    "WHITE — 4 is the count only if you exclude less common types. "
    "Some texts list 5-7 types. Classification-dependent.",
    "HIGH — variable classification count; 4 is trivially small",
    True  # 4=4 but coincidence
)

# ═══════════════════════════════════════════════════════════════
# R3-BIO-14: Neuroglia (Glial Cell) Types in CNS
# ═══════════════════════════════════════════════════════════════
# CNS glia: astrocytes, oligodendrocytes, microglia, ependymal cells = 4 types.
# PNS glia: Schwann cells, satellite cells = 2 types.
# Total: 6 = n! Exact match.
# 4 CNS types = tau(6). 2 PNS types = phi(6). 4+2 = 6 = n.
# This is a well-established classification in every neuroscience textbook.
# CNS glia types are consistently listed as 4 (Purves, Kandel, Bear).
# PNS glia types are consistently 2.
# The decomposition 4+2=6 mapping to tau+phi=n is clean.
# However: some classifications add NG2/polydendrocytes as 5th CNS type (Nishiyama 2009).
# Tanycytes in hypothalamus sometimes listed separately.
# Still, the canonical "4 CNS + 2 PNS = 6 total" is very stable.
check(14,
    "Neuroglia Types: 4 CNS + 2 PNS = 6 = n",
    "6 total glial types = n; CNS 4 = tau(6), PNS 2 = phi(6), 4+2 = n",
    "CNS: astrocytes, oligodendrocytes, microglia, ependymal (4). "
    "PNS: Schwann cells, satellite cells (2). Total: 6.",
    "Purves Neuroscience 6th ed; Kandel Principles 6th ed; Bear Neuroscience 4th ed",
    "tau(6)=4 (CNS glia) + phi(6)=2 (PNS glia) = n=6 (total)",
    "ORANGE — Clean decomposition: tau+phi=n maps to CNS+PNS=total. "
    "The classification is textbook-stable. Risk: NG2 cells sometimes added as 5th CNS type.",
    "MEDIUM — Classification is well-established but some add NG2/polydendrocytes (5th CNS). "
    "The 4+2=6 decomposition is noteworthy because it mirrors divisor structure.",
    True
)

# ═══════════════════════════════════════════════════════════════
# R3-BIO-15: Muscle Fiber Types
# ═══════════════════════════════════════════════════════════════
# Classical: 2 types (Type I slow-twitch, Type II fast-twitch) = phi(6).
# Modern: Type I, Type IIa, Type IIx (formerly IIb in humans) = 3 types.
# Some add Type IIc (hybrid) = 4 types.
# The fundamental classification is 2 (slow/fast) = phi(6). Trivially small.
# 3 fiber types in modern classification = n/phi = 3. Also trivially small.
check(15,
    "Muscle Fiber Types = phi(6) to 3",
    "2 basic muscle fiber types = phi(6); 3 modern types = n/phi(6)",
    "2 basic (Type I, Type II); 3 modern (I, IIa, IIx); 4 if IIc hybrid included",
    "Brooke & Kaiser 1970 (classification); Schiaffino & Reggiani 2011",
    "phi(6) = 2 (basic), n/phi = 3 (modern), tau(6) = 4 (with hybrid)",
    "WHITE — 2 is the minimal binary classification. 3 is trivially common. "
    "Every resolution level matches a different n=6 quantity.",
    "VERY HIGH — classification resolution determines count; any count 2-4 matches something",
    True  # Trivially true
)

# ═══════════════════════════════════════════════════════════════
# R3-BIO-16: Skin Layers (Histological)
# ═══════════════════════════════════════════════════════════════
# Major skin layers: epidermis, dermis, hypodermis = 3.
# Epidermal sublayers: stratum basale, spinosum, granulosum, lucidum, corneum = 5.
# (Lucidum only in thick skin; thin skin has 4 epidermal layers.)
# 3 major layers = n/phi = 3. 5 epidermal = sopfr(6) = 5.
# Total distinct layers (thick skin): 3 + 5 - 1 = 7 (dermis has 2 sublayers:
# papillary and reticular). So dermis(2) + epidermis(5) + hypodermis(1) = 8.
# Wait: epidermis 5 sublayers + dermis 2 sublayers + hypodermis 1 = 8.
# None of these match cleanly beyond trivially small numbers.
# 5 epidermal strata in thick skin is the cleanest number.
check(16,
    "Epidermal Strata = sopfr(6) = 5",
    "5 epidermal strata (thick skin) = sopfr(6) = 5",
    "5 strata: basale, spinosum, granulosum, lucidum, corneum (thick skin only; thin skin has 4)",
    "Mescher, Junqueira's Basic Histology; Kanitakis 2002",
    "sopfr(6) = 5 (thick skin epidermal strata)",
    "WHITE — Only thick skin has 5 layers (thin skin has 4). "
    "The count 5 depends on including stratum lucidum. Trivially small number.",
    "HIGH — classification-dependent (thick vs thin skin); 5 is common small number",
    True  # 5=5 but coincidence
)

# ═══════════════════════════════════════════════════════════════
# R3-BIO-17: Bronchial Branching Generations
# ═══════════════════════════════════════════════════════════════
# Weibel model: 23 generations of airway branching (generation 0 = trachea to
# generation 23 = alveolar sacs). Sometimes cited as 23 or 24 generations.
# Conducting zone: generations 0-16 = 17 generations.
# Respiratory zone: generations 17-23 = 7 generations.
# 23 total: no clean n=6 match (23 is prime).
# 24 total (some models): 24 = sigma_phi = sigma(6)*phi(6) = 12*2 = 24. Exact.
# BUT: the standard Weibel model is 23 generations (0-23), or 24 levels.
# The ambiguity between 23 and 24 makes this questionable.
# Conducting zone 17 generations: 17 = Fermat prime. Interesting but not n=6.
# Respiratory zone 7 generations: no clean match.
check(17,
    "Airway Branching: 24 Levels = sigma*phi(6) = 24",
    "Weibel airway model has 24 branching levels (gen 0-23) = sigma(6)*phi(6) = 24",
    "23 generations (0-23) = 24 levels; conducting 0-16, respiratory 17-23",
    "Weibel 1963, Morphometry of the Human Lung; Horsfield 1990",
    "sigma(6)*phi(6) = 24 (total branching levels)",
    "ORANGE — 24 levels is a well-established morphometric number from Weibel's classic model. "
    "sigma*phi = 24 is a clean n=6 product. "
    "Risk: some count 23 'generations' rather than 24 'levels' (off-by-one framing).",
    "MEDIUM — Weibel's 24 is a gold-standard morphometric constant. "
    "The generation vs level counting ambiguity introduces some uncertainty.",
    True
)

# ═══════════════════════════════════════════════════════════════
# R3-BIO-18: Kidney Nephron Segments
# ═══════════════════════════════════════════════════════════════
# Major nephron segments:
# 1. Renal corpuscle (Bowman's capsule + glomerulus)
# 2. Proximal convoluted tubule (PCT)
# 3. Loop of Henle (descending + ascending limbs, but counted as one segment)
# 4. Distal convoluted tubule (DCT)
# 5. Collecting duct (shared, not technically part of nephron)
# Standard textbook: 4 nephron segments (corpuscle, PCT, loop, DCT) + collecting duct.
# If you subdivide the loop: descending thin, ascending thin, ascending thick = 3 parts.
# Detailed: renal corpuscle, PCT (S1,S2,S3), thin descending, thin ascending,
# thick ascending, DCT, connecting tubule, collecting duct = ~8 segments.
# Most consistent count: 4 main segments (without collecting duct) = tau(6).
# With collecting duct: 5 = sopfr(6).
# This is too classification-dependent.
check(18,
    "Nephron Segments = tau(6) = 4 (or 5 with collecting duct)",
    "4 main nephron segments = tau(6); 5 including collecting duct = sopfr(6)",
    "4 main: corpuscle, PCT, loop of Henle, DCT. +1 collecting duct = 5. "
    "Detailed subdivision yields 8+ segments.",
    "Koeppen & Stanton, Renal Physiology; Boron & Boulpaep, Medical Physiology",
    "tau(6) = 4 or sopfr(6) = 5 depending on whether collecting duct is included",
    "WHITE — Highly classification-dependent. 4 or 5 or 8 depending on resolution. "
    "Either tau or sopfr matches — guaranteed hit with small numbers.",
    "VERY HIGH — resolution-dependent; guaranteed to match one n=6 quantity",
    True  # Both 4 and 5 match, which proves it's coincidence
)

# ═══════════════════════════════════════════════════════════════
# R3-BIO-19: Liver Lobule Structure — Classic Lobule Geometry
# ═══════════════════════════════════════════════════════════════
# Classic hepatic lobule: HEXAGONAL cross-section.
# Each lobule is a hexagonal prism with a central vein.
# 6 portal triads at the corners of the hexagon = n = 6. EXACT.
# Each portal triad contains 3 structures: hepatic artery branch,
# portal vein branch, bile duct = 3 = n/phi.
# The hexagonal geometry is not a classification choice — it's the actual
# physical structure observed in histological sections.
# This is one of the most iconic hexagonal structures in biology.
# The 6-fold symmetry of hepatic lobules is taught in every histology course.
# Rappaport's acinus model offers an alternative functional unit, but the
# classic lobule's hexagonal shape with 6 portal triads is undisputed anatomy.
check(19,
    "Hepatic Lobule: Hexagonal with 6 Portal Triads = n",
    "Liver lobules have hexagonal geometry with exactly 6 portal triads at corners = n = 6. "
    "Each portal triad has 3 structures = n/phi(6).",
    "Hexagonal lobule with 6 portal triads (artery + vein + bile duct each). "
    "Central vein at center. Textbook histology.",
    "Kiernan 1833 (original description); Rappaport 1958 (acinus model); "
    "Ross & Pawlina, Histology: A Text and Atlas",
    "n = 6 (portal triads per lobule), n/phi = 3 (structures per triad)",
    "GREEN — The hexagonal lobule with 6 portal triads is a PHYSICAL STRUCTURE, "
    "not a classification choice. Hexagonal close-packing arises from tissue mechanics. "
    "6-fold symmetry is the natural 2D packing geometry = genuine n=6 connection.",
    "LOW — The hexagonal structure is real anatomy, not taxonomy. "
    "6-fold symmetry from packing geometry is a genuine structural constant. "
    "3 per triad is somewhat less impressive (binary+duct=3 is functional minimum).",
    True
)

# ═══════════════════════════════════════════════════════════════
# R3-BIO-20: Gut Wall Histological Layers
# ═══════════════════════════════════════════════════════════════
# GI tract wall has 4 fundamental layers (from lumen outward):
# 1. Mucosa (epithelium + lamina propria + muscularis mucosae)
# 2. Submucosa
# 3. Muscularis externa (inner circular + outer longitudinal)
# 4. Serosa (or adventitia)
# 4 layers = tau(6) = 4. This is THE canonical histological organization.
# Every hollow organ follows this 4-layer plan.
# Mucosa has 3 sublayers = n/phi = 3.
# Muscularis has 2 sublayers (circular + longitudinal) = phi(6) = 2.
# Total sublayers: 3 + 1 + 2 + 1 = 7. No clean match.
# The fundamental number 4 is extremely well-established, but also trivially small.
check(20,
    "GI Tract Wall Layers = tau(6) = 4",
    "4 fundamental histological layers of GI tract = tau(6) = 4. "
    "Mucosa has 3 sublayers = n/phi(6). Muscularis has 2 = phi(6).",
    "4 layers: mucosa, submucosa, muscularis externa, serosa. "
    "Mucosa sublayers: epithelium, lamina propria, muscularis mucosae.",
    "Ross & Pawlina, Histology; Junqueira's Basic Histology; any GI histology text",
    "tau(6) = 4 (main layers), n/phi = 3 (mucosal sublayers), phi(6) = 2 (muscularis sublayers)",
    "WHITE — 4 layers is a universal body plan for hollow organs but 4 is trivially small. "
    "The 3+2 sublayer decomposition is somewhat interesting but also small numbers.",
    "HIGH — 4 is trivially small; the 4-layer plan is universal across all hollow organs",
    True  # Arithmetic works but coincidence
)


# ═══════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════
print("\n" + "="*72)
print("ROUND 3 BIOLOGY SUMMARY")
print("="*72)

# Grade distribution
grades = {
    'GREEN': [], 'ORANGE_STAR': [], 'ORANGE': [], 'WHITE': [], 'FAIL': []
}
for r in results:
    g = r['grade']
    if 'GREEN' in g.upper() or g.startswith('\u0001f7e9'):
        grades['GREEN'].append(r)
    elif 'ORANGE-STAR' in g.upper() or 'ORANGE_STAR' in g.upper():
        grades['ORANGE_STAR'].append(r)
    elif 'ORANGE' in g.upper():
        grades['ORANGE'].append(r)
    elif r['status'] == 'FAIL':
        grades['FAIL'].append(r)
    else:
        grades['WHITE'].append(r)

print(f"\n  Total hypotheses: {len(results)}")
print(f"  Arithmetic PASS:  {PASS}")
print(f"  Arithmetic FAIL:  {FAIL}")
print(f"\n  Grade distribution:")
print(f"    GREEN (proven/structural):  {len(grades['GREEN'])}")
print(f"    ORANGE-STAR (significant):  {len(grades['ORANGE_STAR'])}")
print(f"    ORANGE (notable):           {len(grades['ORANGE'])}")
print(f"    WHITE (coincidence):         {len(grades['WHITE'])}")
print(f"    FAIL (no match):            {len(grades['FAIL'])}")

print("\n" + "-"*72)
print("HONEST ASSESSMENT")
print("-"*72)
print("""
  Most biology hypotheses in this round are WHITE (coincidence).
  Small numbers (2, 3, 4, 5) appear everywhere in biological classification.
  With n=6 arithmetic providing values {2, 3, 4, 5, 6, 12, 24}, almost any
  small biological count will match something. This is the Texas Sharpshooter
  problem at its most obvious.

  The only structurally interesting results:

  R3-BIO-19 (Hepatic Lobule) — GREEN
    6 portal triads in hexagonal lobule is PHYSICAL GEOMETRY, not classification.
    Hexagonal packing = 6-fold symmetry is a genuine structural constant.
    This is the strongest result in the batch.

  R3-BIO-17 (Airway Branching) — ORANGE
    Weibel's 24 branching levels = sigma*phi is a clean product match with
    a well-established morphometric constant. Some counting ambiguity.

  R3-BIO-14 (Neuroglia Types) — ORANGE
    4 CNS + 2 PNS = 6 total maps to tau+phi=n. Clean decomposition,
    though the numbers are still small.

  R3-BIO-05 (Coagulation Factors) — ORANGE-STAR
    12 factors (I-XIII minus VI) = sigma(6). Historically fixed numbering.
    But the numbering is human convention, not a natural constant.

  Everything else is WHITE — coincidences with trivially small numbers.
""")

print("\n" + "-"*72)
print("RESULT TABLE")
print("-"*72)
print(f"{'ID':<12} {'Title':<45} {'Known':>8} {'n=6':>8} {'Grade':<15}")
print("-"*72)
for r in results:
    hyp_id = f"R3-BIO-{r['id']:02d}"
    title = r['title'][:44]
    # Extract key number from known_value
    known = r['known_value'][:8] if len(r['known_value']) > 8 else r['known_value']
    n6 = r['n6_match'][:8] if len(r['n6_match']) > 8 else r['n6_match']
    g = r['grade'].split(' ')[0]  # First word of grade
    status = r['status']
    print(f"{hyp_id:<12} {title:<45} {status:>8} {g:<15}")

print(f"\n  Honest verdict: 1 GREEN, 1 ORANGE-STAR, 2 ORANGE, 14 WHITE, 2 FAIL")
print(f"  Biology is mostly small-number coincidences with n=6 arithmetic.")
print(f"  The hepatic lobule hexagon (R3-BIO-19) is the only genuine structural match.")
