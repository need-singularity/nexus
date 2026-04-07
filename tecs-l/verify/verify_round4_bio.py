#!/usr/bin/env python3
"""
verify_round4_bio.py — Round 4 Biology/Neuroscience/Medicine Hypothesis Verification
25 NEW hypotheses NOT overlapping with ANY previous round.

Excluded topics (already done in R1-R3): cortical layers, theta-gamma, DMN,
anesthesia, sleep, predictive coding, mirror neurons, binding, criticality,
rich-club, psychedelics, meditation, SWR, attention MOT, photosynthesis,
benzene, glucose, glycolysis, ATP, Krebs, circadian rhythm, capsids, water,
DNA grooves, codons, cell cycle, periodic table, protein H-bonds, Kok cycle,
pyranose, food chains, ETC, grid cells, neurotransmitters, cochlea, spinal,
heart, immune, hormones, chromosomes, morphogenesis, embryonic layers, senses,
apoptosis, white matter tracts, Brodmann regions, hippocampal subfields,
basal ganglia (partial), cerebellar modules, retinal layers, Turing patterns,
visual cortex columns, phyllotaxis, Hox genes, mass extinctions, organ systems,
cranial nerves, blood types, taste receptors, etc.

NEW AREAS for Round 4:
  Gestalt, working memory, Piaget, Maslow, Kubler-Ross, SCN oscillations,
  gate control theory, reflex arc, action potential channels, myelin,
  cortical minicolumns, Broca/Brodmann 44, visual cortex V areas, auditory
  tonotopy, motor homunculus, basal ganglia nuclei, cerebellum layers,
  thalamic nuclei, hypothalamic nuclei, brainstem divisions, bilateral
  symmetry, insect morphology, starfish arms, honeybee hexagons, bird
  V-formation.

n=6 arithmetic: σ=12, τ=4, φ=2, sopfr=5, σφ=24, ln(4/3)≈0.2877
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
WHITE = 0  # ⚪ coincidence counter
results = []

def check(hyp_id, title, claim, known_value, known_source,
          n6_match, grade, risk, match_ok):
    """Record and display a hypothesis check."""
    global PASS, FAIL, WHITE
    status = "PASS" if match_ok else "FAIL"
    if match_ok:
        PASS += 1
    else:
        FAIL += 1
    if "WHITE" in grade or "⚪" in grade:
        WHITE += 1

    result = {
        'id': hyp_id, 'title': title, 'claim': claim,
        'known_value': known_value, 'source': known_source,
        'n6_match': n6_match, 'grade': grade, 'risk': risk,
        'status': status
    }
    results.append(result)

    print(f"\n{'='*72}")
    print(f"R4-BIO-{hyp_id:02d}: {title}")
    print(f"{'='*72}")
    print(f"  Claim: {claim}")
    print(f"  Known value: {known_value}")
    print(f"  Source: {known_source}")
    print(f"  n=6 match: {n6_match}")
    print(f"  Arithmetic check: {status}")
    print(f"  Grade: {grade}")
    print(f"  Risk: {risk}")


# ═══════════════════════════════════════════════════════════════
# R4-BIO-01: Classical Gestalt Laws Count
# ═══════════════════════════════════════════════════════════════
# Wertheimer (1923) proposed the original Gestalt grouping principles.
# Classical count: proximity, similarity, closure, good continuation,
# common fate, Pragnanz (good figure). That's 6 principles.
# Later additions: common region (Palmer 1992), connectedness, synchrony —
# but these are POST-classical.
# 6 classical Gestalt laws = n = 6. Exact match.
# HOWEVER: The count depends on who's counting. Some textbooks list 5
# (omitting Pragnanz or common fate). Others list 7+ (adding symmetry).
# Wertheimer's 1923 paper itself has ~5-7 principles depending on parsing.
# This is a "counting a list" problem — high arbitrariness risk.
check(1,
    "Classical Gestalt Laws = n = 6",
    "The 6 classical Gestalt grouping principles (Wertheimer 1923) = n = 6",
    "Usually listed as 6: proximity, similarity, closure, continuation, "
    "common fate, Pragnanz. But counts vary 5-7 across sources.",
    "Wertheimer 1923; Koffka 1935; Wagemans et al. 2012 review",
    "n = 6 (if the 6-count version is accepted)",
    "⚪ WHITE — List count is author-dependent (5-7 in different sources). "
    "Selecting the 6-count version is cherry-picking. No structural reason.",
    "HIGH — Taxonomy lists of perceptual principles are arbitrary. "
    "No geometric or physical constraint forces exactly 6.",
    True  # Arithmetic holds for the 6-count version
)

# ═══════════════════════════════════════════════════════════════
# R4-BIO-02: Baddeley's Working Memory Components
# ═══════════════════════════════════════════════════════════════
# Baddeley & Hitch (1974): 3 components — central executive,
# phonological loop, visuospatial sketchpad.
# Baddeley (2000) added episodic buffer → 4 components.
# 4 = tau(6). Exact arithmetic match.
# BUT: 4 is an extremely small number. Any model with 4 boxes matches.
# The number 4 comes from Baddeley's theoretical framework, not from
# any physical constraint. He could have proposed 3 or 5 or 7.
check(2,
    "Baddeley Working Memory Components = tau(6) = 4",
    "4 components of Baddeley's working memory model = tau(6) = 4",
    "4: central executive, phonological loop, visuospatial sketchpad, "
    "episodic buffer. (Originally 3, expanded to 4 in 2000.)",
    "Baddeley & Hitch 1974; Baddeley 2000",
    "tau(6) = 4",
    "⚪ WHITE — 4 is trivially common. The model was expanded from 3 to 4 "
    "by the author's choice. No physical constraint yields exactly 4.",
    "HIGH — Theoretical model count, not empirically forced.",
    True
)

# ═══════════════════════════════════════════════════════════════
# R4-BIO-03: Piaget's Stages of Cognitive Development
# ═══════════════════════════════════════════════════════════════
# Piaget proposed 4 stages: sensorimotor, preoperational, concrete
# operational, formal operational.
# 4 = tau(6). Same trivial match as Baddeley.
# Some neo-Piagetians add stages (e.g., Robbie Case: 4 stages but
# with substages; Fischer: 13 levels). The 4-stage model is Piaget's
# choice, not empirically forced.
check(3,
    "Piaget's Cognitive Development Stages = tau(6) = 4",
    "4 Piagetian stages = tau(6) = 4",
    "4: sensorimotor, preoperational, concrete operational, formal operational",
    "Piaget 1952; Piaget & Inhelder 1969",
    "tau(6) = 4",
    "⚪ WHITE — Same as R4-BIO-02. A theorist's model with 4 categories. "
    "Erikson proposed 8 stages, Kohlberg 6 stages. The number is framework-dependent.",
    "HIGH — Purely theoretical classification. Different theorists pick different counts.",
    True
)

# ═══════════════════════════════════════════════════════════════
# R4-BIO-04: Maslow's Hierarchy of Needs
# ═══════════════════════════════════════════════════════════════
# Classic Maslow (1943): 5 levels — physiological, safety, love/belonging,
# esteem, self-actualization.
# Later Maslow (1970): 7-8 levels (adding cognitive, aesthetic, transcendence).
# 5 = sopfr(6) = 2 + 3. Arithmetic match.
# But: The 5-level version is one of several Maslow proposed.
# And sopfr(6) = 5 is a very common small number.
check(4,
    "Maslow's 5 Needs Levels = sopfr(6) = 5",
    "5 levels of Maslow's hierarchy = sopfr(6) = 5",
    "5: physiological, safety, love, esteem, self-actualization (classic version). "
    "Maslow himself later expanded to 7-8.",
    "Maslow 1943; Maslow 1970 (expanded)",
    "sopfr(6) = 5",
    "⚪ WHITE — 5 is the CLASSIC version only. Maslow later had 7-8. "
    "sopfr(6) = 5 matching is trivially likely for any small-number system.",
    "HIGH — The count is framework-version-dependent.",
    True
)

# ═══════════════════════════════════════════════════════════════
# R4-BIO-05: Kubler-Ross 5 Stages of Grief
# ═══════════════════════════════════════════════════════════════
# Kubler-Ross (1969): denial, anger, bargaining, depression, acceptance = 5.
# 5 = sopfr(6) again. Same trivial match.
# The model is widely criticized as non-empirical. The "5 stages" is a
# cultural meme more than a validated scientific model.
check(5,
    "Kubler-Ross Grief Stages = sopfr(6) = 5",
    "5 stages of grief = sopfr(6) = 5",
    "5: denial, anger, bargaining, depression, acceptance",
    "Kubler-Ross 1969; widely criticized, see Stroebe et al. 2017",
    "sopfr(6) = 5",
    "⚪ WHITE — Non-empirical model. The '5 stages' is a cultural simplification. "
    "Many grief models use different counts. Trivially small number.",
    "HIGH — Not empirically validated as exactly 5. Cultural artifact.",
    True
)

# ═══════════════════════════════════════════════════════════════
# R4-BIO-06: SCN Oscillation Frequency Bands
# ═══════════════════════════════════════════════════════════════
# The suprachiasmatic nucleus (SCN) generates circadian rhythms.
# Individual SCN neurons oscillate with periods of ~22-26 hours.
# The SCN doesn't really have "frequency bands" like EEG.
# EEG has delta, theta, alpha, beta, gamma = 5 classical bands
# (sometimes 6 with high-gamma, sometimes 7 with mu/sigma).
# For SCN specifically: it's a single circadian band (~0.04 Hz = 1/24hr).
# There are ultradian sub-harmonics but these aren't discrete bands.
# Attempting: SCN period ~24h. sigma_phi = 24. Match!
# But this is already related to circadian rhythm (excluded topic).
# Independently: 24 hours = sigma(6) * phi(6) is interesting but
# the 24-hour day is an astronomical coincidence, not biological.
check(6,
    "SCN Period 24h = sigma*phi = 24",
    "SCN circadian period ~24h = sigma(6)*phi(6) = 24",
    "SCN free-running period: 24.18 +/- 0.04 h in humans (not exactly 24). "
    "24 hours is Earth's rotation period, not a biological constant.",
    "Czeisler et al. 1999 (24.18h); Earth rotation = 23h 56m sidereal",
    "sigma*phi = 24, close to ~24.18h (0.75% off)",
    "⚪ WHITE — The 24h day is astronomical, not biological. SCN EVOLVED to "
    "match Earth's rotation. Any organism on this planet has ~24h rhythms. "
    "Also: human free-running period is 24.18h, not exactly 24.",
    "HIGH — Earth's rotation period is external. Biology adapted to it.",
    True  # 24 is arithmetically sigma*phi, but it's coincidence
)

# ═══════════════════════════════════════════════════════════════
# R4-BIO-07: Gate Control Theory Layers
# ═══════════════════════════════════════════════════════════════
# Melzack & Wall (1965) Gate Control Theory of pain.
# The model has 3 components: large fiber (A-beta), small fiber (C/A-delta),
# and the substantia gelatinosa "gate" in the spinal cord dorsal horn.
# The dorsal horn has laminae I-VI (Rexed laminae), with pain processing
# mainly in laminae I, II (substantia gelatinosa), and V.
# 3 pain-relevant laminae: I, II, V. Or 6 total dorsal horn laminae.
# Rexed (1952) classified spinal cord gray matter into 10 laminae (I-X).
# Dorsal horn = laminae I-VI = 6 laminae. Match: n = 6.
# This is a genuine anatomical classification based on cytoarchitecture.
check(7,
    "Dorsal Horn Laminae (Rexed) = n = 6",
    "6 Rexed laminae in dorsal horn (I-VI) = n = 6",
    "Rexed laminae I-VI constitute the dorsal horn. "
    "Total spinal cord = 10 laminae (I-X). Dorsal horn = I-VI = 6.",
    "Rexed 1952, 1954; standard neuroanatomy (e.g., Standring, Gray's Anatomy)",
    "n = 6 (dorsal horn laminae I through VI)",
    "⚪ WHITE — The Rexed classification is based on cytoarchitecture, "
    "but the boundary between laminae is somewhat arbitrary. Also, "
    "10 total laminae split as 6 dorsal + 3 ventral + 1 central is a "
    "conventional partition, not physically forced. Small-number risk.",
    "MODERATE — Rexed laminae are established anatomy, but the 6-count "
    "for dorsal horn depends on where you draw ventral boundary.",
    True
)

# ═══════════════════════════════════════════════════════════════
# R4-BIO-08: Simplest Reflex Arc Neuron Count
# ═══════════════════════════════════════════════════════════════
# The simplest reflex arc (monosynaptic) has 2 neurons:
# sensory (afferent) neuron → motor (efferent) neuron.
# Example: knee-jerk (patellar) reflex.
# 2 = phi(6). Match.
# Polysynaptic reflex arcs have 3+ neurons (adding interneurons).
# A "typical" reflex arc (polysynaptic) has 3 neurons:
# sensory → interneuron → motor. 3 = sigma/tau = n/phi.
# BUT: 2 and 3 are THE most common small numbers. Everything matches
# 2 or 3 in some n=6 arithmetic expression.
check(8,
    "Monosynaptic Reflex Arc = phi(6) = 2 neurons",
    "Simplest reflex arc has 2 neurons = phi(6) = 2",
    "Monosynaptic: 2 neurons (sensory + motor). "
    "Polysynaptic: 3 neurons (+ interneuron). Both are textbook.",
    "Sherrington 1906; Kandel et al. Principles of Neural Science",
    "phi(6) = 2",
    "⚪ WHITE — 2 is the minimum for any arc (input + output). "
    "This is a trivial architectural minimum, not an n=6 relationship.",
    "VERY HIGH — 2 is literally the smallest possible neural circuit.",
    True
)

# ═══════════════════════════════════════════════════════════════
# R4-BIO-09: Na/K Channel Types in Action Potential
# ═══════════════════════════════════════════════════════════════
# Action potential involves voltage-gated Na+ and K+ channels.
# Na channel subtypes: Nav1.1 through Nav1.9 = 9 subtypes.
# K channel families: Kv (voltage-gated) alone has >40 genes.
# Total ion channel types involved: Na, K, Ca, Cl = 4 major ion types.
# 4 = tau(6). But 4 ion types is just "the 4 common biological ions."
# Na channel has 4 homologous domains (I-IV), each with 6 transmembrane
# segments (S1-S6). 6 TM segments per domain = n = 6!
# K channel subunit: also 6 transmembrane segments (S1-S6).
# This is a STRUCTURAL feature: S1-S4 = voltage sensor, S5-S6 = pore.
# The 6-TM topology is shared across voltage-gated ion channel superfamily.
# This is physically constrained by the need for voltage sensing + pore.
check(9,
    "Voltage-Gated Ion Channel = 6 Transmembrane Segments",
    "Voltage-gated Na+/K+/Ca2+ channels have 6 TM segments per subunit/domain = n = 6",
    "6 TM segments (S1-S6): S1-S4 = voltage sensor domain, S5-S6 = pore domain. "
    "This is the canonical topology for ALL voltage-gated cation channels. "
    "Na+ has 4 domains x 6 TM = 24 total TM. K+ has 4 subunits x 6 TM = 24.",
    "Catterall 2000; Hille, Ion Channels of Excitable Membranes; "
    "Long et al. 2005 (Kv1.2 crystal structure)",
    "n = 6 (TM per domain), sigma_phi = 24 (total TM in tetramer)",
    "⭐ INTERESTING — The 6-TM topology is a genuine structural constraint. "
    "Voltage sensing requires ~4 TM helices, pore requires ~2. "
    "The 6-TM architecture is conserved across >500 million years of evolution. "
    "24 total TM in tetrameric channel = sigma*phi. HOWEVER: the 4-fold "
    "symmetry (4 domains/subunits) is also matching tau(6)=4, which is suspicious "
    "-- too many simultaneous matches suggests we're post-hoc fitting.",
    "MODERATE — 6-TM is genuine protein topology, not arbitrary counting. "
    "But claiming n, tau, AND sigma*phi all match simultaneously is overfitting.",
    True
)

# ═══════════════════════════════════════════════════════════════
# R4-BIO-10: Myelin Internode Structure
# ═══════════════════════════════════════════════════════════════
# Myelinated axons have internodes (myelinated segments) separated by
# Nodes of Ranvier. Internode length: 200-2000 um (varies with axon diameter).
# Internode/diameter ratio: ~100-200 (not a clean integer).
# Number of myelin wraps: 10-160 (varies).
# No clean discrete number characterizes myelin geometry.
# Attempting: Schwann cells myelinate 1 internode each (in PNS).
# Oligodendrocytes myelinate up to ~50 internodes (in CNS).
# No clean n=6 arithmetic.
check(10,
    "Myelin Internode Ratios vs n=6",
    "Myelin internode/diameter ratio or wrap count relates to n=6 arithmetic",
    "Internode/diameter ~ 100-200 (continuous, varies). "
    "Myelin wraps: 10-160 (varies). No discrete characterizing integer.",
    "Waxman & Bennett 1972 (internode ratio); Nave & Werner 2014 (myelin)",
    "No clean match. Ratios are continuous and variable, not discrete.",
    "FAIL — No discrete n=6 match. Myelin geometry is continuously variable.",
    "N/A — Honest no-match.",
    False
)

# ═══════════════════════════════════════════════════════════════
# R4-BIO-11: Cortical Minicolumn Neuron Count
# ═══════════════════════════════════════════════════════════════
# Cortical minicolumns contain ~80-120 neurons (Mountcastle 1997).
# Some estimates: ~110 neurons per minicolumn.
# Macrocolumn: ~80-100 minicolumns = ~10,000 neurons.
# 80-120 range: no clean n=6 match.
# sigma_phi = 24 doesn't fit. sigma^2 = 144 — too high.
# n*sigma = 72, n*tau = 24 — not in range.
# 100 = ? No clean n=6 expression for 80-120.
check(11,
    "Cortical Minicolumn Neuron Count vs n=6",
    "~80-120 neurons per minicolumn relates to n=6 arithmetic",
    "~80-120 neurons per minicolumn (Mountcastle). Varies by cortical area. "
    "V1 minicolumns: ~80-100; prefrontal: ~100-120.",
    "Mountcastle 1997; Buxhoeveden & Casanova 2002",
    "No clean match. Range 80-120 has no simple n=6 expression.",
    "FAIL — 80-120 is continuous and variable. No discrete n=6 arithmetic.",
    "N/A — Honest no-match.",
    False
)

# ═══════════════════════════════════════════════════════════════
# R4-BIO-12: Broca Area = Brodmann Area 44
# ═══════════════════════════════════════════════════════════════
# Broca's area: Brodmann areas 44 (pars opercularis) and 45 (pars triangularis).
# BA 44 = ? Let's check: 44 = 4 * 11. Not a clean n=6 expression.
# 44 mod 6 = 2 = phi(6). That's a very weak match.
# sigma * tau - 4 = 48 - 4 = 44? That's ad hoc arithmetic.
# BA 45 = ? 45 = 9 * 5. Not clean either.
# The Brodmann numbering is sequential (1-52, with gaps), assigned in order
# of when Brodmann studied each area. The numbers are ARBITRARY labels,
# not reflecting any structural hierarchy.
check(12,
    "Broca Area (BA 44) vs n=6 Arithmetic",
    "Brodmann area 44 (Broca) relates to n=6 arithmetic",
    "BA 44 and BA 45. The Brodmann numbering is sequential/arbitrary, "
    "assigned by order of histological study, not structural principle.",
    "Brodmann 1909; Amunts et al. 1999",
    "No meaningful match. 44 requires ad hoc expressions like sigma*tau-4.",
    "FAIL — Brodmann numbers are arbitrary labels. Matching them to n=6 "
    "is numerology, not structure.",
    "N/A — The numbers are sequential labels, not structural constants.",
    False
)

# ═══════════════════════════════════════════════════════════════
# R4-BIO-13: Visual Cortex Areas V1-V6
# ═══════════════════════════════════════════════════════════════
# Visual areas: V1, V2, V3, V3A, V4, V5/MT, V6.
# If you count V1-V6 as labeled: that's 6 (but V3A is extra, V5=MT).
# Actually V6 exists (Galletti et al. 1999, in parieto-occipital cortex).
# So "V1 through V6" = 6 named visual areas = n = 6?
# PROBLEMS:
# - The numbering is sequential and DEFINED to go 1,2,3,...
#   Any sequence V1-Vk gives k areas. If you stop at V6, you get 6.
# - There are actually 30+ visual areas (Felleman & Van Essen 1991).
# - V6 is less standard than V1-V5. Many textbooks stop at V5/MT.
# - This is "the number of items in a sequence that we define to stop at 6."
check(13,
    "Visual Cortex V1-V6 = n = 6 Areas",
    "6 primary visual areas V1-V6 = n = 6",
    "V1-V5 are standard. V6 exists but is less commonly listed. "
    "Total visual areas: 30+ (Felleman & Van Essen 1991). "
    "The V-numbering is sequential by definition.",
    "Felleman & Van Essen 1991; Galletti et al. 1999",
    "n = 6 (if counting V1-V6). But stopping at V6 is arbitrary.",
    "⚪ WHITE — Sequential numbering V1-Vk trivially gives k. "
    "Stopping at V6 to match n=6 is circular. There are 30+ visual areas.",
    "VERY HIGH — This is literally choosing where to stop counting a sequence.",
    True
)

# ═══════════════════════════════════════════════════════════════
# R4-BIO-14: Auditory Cortex Tonotopic Organization
# ═══════════════════════════════════════════════════════════════
# The auditory cortex is tonotopically organized (frequency maps).
# Primary auditory cortex (A1) has a single tonotopic gradient.
# Number of distinct auditory cortical fields: varies by species.
# Human: ~6-8 auditory cortical areas (Da Costa et al. 2011).
# Macaque: ~10-12 areas (Kaas & Hackett 2000).
# Frequency range: 20 Hz - 20 kHz (human). Octave span: ~10 octaves.
# Critical bands (Bark scale): 24 bands. sigma_phi = 24!
# The Bark scale has 24 critical bands from 0-24 Bark.
# This is based on cochlear mechanics (place theory).
check(14,
    "Bark Critical Bands = sigma*phi = 24",
    "24 Bark critical bands in human auditory perception = sigma(6)*phi(6) = 24",
    "Bark scale: 24 critical bands (0-24 Bark), each ~1.3 mm on basilar membrane. "
    "Based on Zwicker 1961. ERB scale (Moore & Glasberg 1983) is continuous, "
    "giving ~38 ERBs across hearing range — different count.",
    "Zwicker 1961; Zwicker & Terhardt 1980; Moore & Glasberg 1983 (ERB)",
    "sigma*phi = 24 (matches Bark scale count)",
    "⚪ WHITE — The Bark scale's 24 bands is a DEFINITION choice. "
    "Zwicker defined each band as ~100 mel wide. Different bandwidth "
    "criteria give different counts (ERB scale gives ~38). The '24' is "
    "not a physical constant but a psychoacoustic convention.",
    "HIGH — The count depends on bandwidth definition. ERB gives 38, not 24.",
    True
)

# ═══════════════════════════════════════════════════════════════
# R4-BIO-15: Motor Homunculus Major Body Regions
# ═══════════════════════════════════════════════════════════════
# Penfield's motor homunculus (1937, 1950) maps body parts to motor cortex.
# "Major body regions" depends on how you count:
# Common listing: toes, ankle, knee, hip, trunk, shoulder, elbow, wrist,
# hand, fingers (individual), thumb, neck, brow, eye, face, lips, jaw,
# tongue, larynx. That's ~15-20 zones.
# If you group coarsely: leg, trunk, arm, hand, face, mouth = 6?
# But this grouping is arbitrary. You could do 5 or 8 or 12.
check(15,
    "Motor Homunculus Major Regions vs n=6",
    "Motor homunculus has 6 major body regions = n = 6",
    "Penfield mapped ~15-20 somatotopic zones. Coarse grouping is arbitrary: "
    "could be 5 (limbs + trunk), 6 (leg/trunk/arm/hand/face/mouth), "
    "or 12+ (by individual body part).",
    "Penfield & Rasmussen 1950; Schieber 2001 (modern revision)",
    "n = 6 only with specific arbitrary grouping",
    "⚪ WHITE — The number of 'regions' depends entirely on grouping granularity. "
    "No natural boundary forces exactly 6.",
    "HIGH — Completely arbitrary grouping.",
    True
)

# ═══════════════════════════════════════════════════════════════
# R4-BIO-16: Basal Ganglia Nuclei Count
# ═══════════════════════════════════════════════════════════════
# Basal ganglia components:
# 1. Caudate nucleus
# 2. Putamen
# 3. Globus pallidus external (GPe)
# 4. Globus pallidus internal (GPi)
# 5. Subthalamic nucleus (STN)
# 6. Substantia nigra pars compacta (SNc)
# 7. Substantia nigra pars reticulata (SNr)
# That's 7 if you split GP and SN, or 5 if you lump them.
# Striatum = caudate + putamen (sometimes counted as 1).
# 5 nuclei (lumped): striatum, GPe, GPi, STN, SN = 5 = sopfr(6).
# 7 nuclei (split): no clean match.
# Nucleus accumbens is sometimes included → 6 or 8.
# HIGHLY variable depending on what you include.
check(16,
    "Basal Ganglia Nuclei = sopfr(6) = 5 (or 6 or 7)",
    "Basal ganglia nuclei count relates to n=6 arithmetic",
    "Count varies: 5 (lumped), 6 (with accumbens), 7 (split GP and SN). "
    "No consensus on exact count.",
    "Lanciego et al. 2012; Graybiel 2000",
    "sopfr(6) = 5 (if lumped). But 6 or 7 by other counts.",
    "⚪ WHITE — The count depends on lumping/splitting decisions. "
    "You can get 5, 6, or 7, guaranteeing a match with SOMETHING.",
    "HIGH — Anatomical taxonomy with flexible boundaries.",
    True
)

# ═══════════════════════════════════════════════════════════════
# R4-BIO-17: Cerebellar Cortex Layers
# ═══════════════════════════════════════════════════════════════
# Cerebellar cortex has exactly 3 layers:
# 1. Molecular layer (outer)
# 2. Purkinje cell layer (middle)
# 3. Granular layer (inner)
# 3 = n/phi = sigma/tau = a divisor of 6. Trivial match.
# Purkinje cell dendritic tree: ~200,000 dendritic spines (not clean).
# Purkinje cells receive 2 types of excitatory input:
#   climbing fibers (from inferior olive) + parallel fibers (from granule cells) = 2
# 2 = phi(6). But "2 types of input" is extremely common.
# Cell types in cerebellar cortex: 5 main types (Purkinje, granule,
# basket, stellate, Golgi). 5 = sopfr(6).
check(17,
    "Cerebellar Cortex: 3 Layers, 5 Cell Types",
    "3 cerebellar cortex layers and 5 major cell types = n=6 arithmetic",
    "3 layers (molecular, Purkinje, granular). "
    "5 cell types (Purkinje, granule, basket, stellate, Golgi). "
    "Sometimes Lugaro and unipolar brush cells added = 7.",
    "Eccles et al. 1967; Llinas et al. 2004",
    "3 = n/2, 5 = sopfr(6). But both are trivially small.",
    "⚪ WHITE — 3 layers is genuine anatomy but 3 is trivially common. "
    "5 cell types depends on including/excluding minor types. "
    "Both numbers are too small to be meaningful matches.",
    "HIGH — Small numbers. Including Lugaro cells makes it 6 or 7.",
    True
)

# ═══════════════════════════════════════════════════════════════
# R4-BIO-18: Thalamic Nuclear Groups
# ═══════════════════════════════════════════════════════════════
# Major thalamic nuclear groups:
# 1. Anterior group
# 2. Medial group (mediodorsal)
# 3. Lateral group (ventral + dorsal tier)
# 4. Posterior group (pulvinar, LGN, MGN)
# 5. Intralaminar nuclei
# 6. Reticular nucleus
# 7. Midline nuclei
# That's 7 major groups. Some classify as 5 (merging intralaminar + midline
# and omitting reticular), or 6 (common textbook grouping).
# Specific nuclei within thalamus: ~50-60 (highly variable in classification).
# If textbook says 6 groups: n = 6. But this is taxonomy-dependent.
check(18,
    "Thalamic Nuclear Groups vs n=6",
    "Major thalamic nuclear groups = n = 6",
    "Classification varies: 5-7 major groups depending on source. "
    "Common textbook: anterior, medial, lateral, posterior, intralaminar, reticular = 6. "
    "But other groupings give 5 or 7.",
    "Jones 2007, The Thalamus; Sherman & Guillery 2006",
    "n = 6 (one common textbook classification)",
    "⚪ WHITE — Another anatomy taxonomy with flexible counts. "
    "Getting 6 requires specific grouping choices. 5 and 7 equally valid.",
    "HIGH — Classification-dependent.",
    True
)

# ═══════════════════════════════════════════════════════════════
# R4-BIO-19: Hypothalamic Major Nuclei Regions
# ═══════════════════════════════════════════════════════════════
# Hypothalamus is divided into regions:
# Lateral-medial: 3 zones (periventricular, medial, lateral)
# Anterior-posterior: 4 regions (preoptic, anterior/supraoptic,
#   tuberal/middle, mammillary/posterior)
# Total discrete nuclei: ~15-20 named nuclei.
# 3 zones x 4 regions = 12 = sigma(6). This is a grid structure.
# BUT: The 3x4 grid is one organizational scheme. Others use different
# axes. The 12 is a product of two classification choices.
check(19,
    "Hypothalamic Organization: 3x4 = sigma(6) = 12",
    "3 medial-lateral zones x 4 anterior-posterior regions = 12 = sigma(6)",
    "3 zones (periventricular, medial, lateral) x 4 regions (preoptic, "
    "supraoptic, tuberal, mammillary) = 12 compartments. "
    "Individual nuclei: ~15-20.",
    "Saper & Lowell 2014; Kandel et al., standard neuroanatomy texts",
    "sigma(6) = 12 = 3 x 4",
    "⚪ WHITE — The 3x4 grid is one classification scheme. The '3' and '4' "
    "are independently chosen axis divisions. 3x4=12 matching sigma(6) is "
    "a coincidence of two small numbers multiplied.",
    "MODERATE-HIGH — Organizational scheme, not physically forced dimensions.",
    True
)

# ═══════════════════════════════════════════════════════════════
# R4-BIO-20: Brainstem Major Divisions
# ═══════════════════════════════════════════════════════════════
# Brainstem has 3 major divisions:
# 1. Midbrain (mesencephalon)
# 2. Pons (metencephalon)
# 3. Medulla oblongata (myelencephalon)
# 3 = n/2 = sigma/tau. Trivial small number.
# If you include the diencephalon (thalamus+hypothalamus): 4 = tau(6).
# But diencephalon is usually classified as forebrain, not brainstem.
check(20,
    "Brainstem Divisions = 3 = n/phi",
    "3 brainstem divisions = n/phi(6) = 3",
    "3: midbrain, pons, medulla. Universal textbook classification.",
    "Standard neuroanatomy (e.g., Haines, Neuroanatomy; Blumenfeld 2010)",
    "n/phi = 3",
    "⚪ WHITE — 3 is the most trivially common number in anatomy. "
    "Nearly every body region has '3 parts' by some classification. "
    "No structural connection to n=6.",
    "VERY HIGH — 3 is trivially ubiquitous.",
    True
)

# ═══════════════════════════════════════════════════════════════
# R4-BIO-21: Bilateral Symmetry and phi(6) = 2
# ═══════════════════════════════════════════════════════════════
# Bilateral symmetry: 2-fold symmetry. Found in >99% of animals (Bilateria).
# 2 = phi(6). Match.
# BUT: bilateral symmetry is the simplest non-trivial symmetry.
# It's the MINIMAL symmetry for a mobile organism (front/back distinction
# + single axis of locomotion). It's determined by physics of movement
# through a medium, not by abstract number theory.
# Bilateral = Z_2 symmetry group, which is the simplest nontrivial group.
check(21,
    "Bilateral Symmetry = phi(6) = 2",
    "Bilateral (2-fold) symmetry in vertebrates = phi(6) = 2",
    "Virtually all animals in Bilateria have bilateral symmetry. "
    "This is 2-fold (Z_2) symmetry, the simplest possible.",
    "Valentine 2004, On the Origin of Phyla",
    "phi(6) = 2",
    "⚪ WHITE — Bilateral symmetry is the MINIMUM symmetry for directed "
    "locomotion. 2 is forced by physics of movement, not n=6. "
    "Matching phi(6)=2 is trivially guaranteed for any 2-fold symmetry.",
    "VERY HIGH — 2 is the minimum nontrivial symmetry. Universal.",
    True
)

# ═══════════════════════════════════════════════════════════════
# R4-BIO-22: Insect Morphology: 6 Legs, 3 Segments
# ═══════════════════════════════════════════════════════════════
# Insects: 6 legs (defining characteristic of Hexapoda).
# 3 body segments: head, thorax, abdomen.
# 6 legs = n = 6. EXACT match.
# 3 segments = sigma/tau = n/phi = 3. Also matches.
# 6 legs / 3 segments = 2 legs per segment (in thorax) = phi(6).
# This is one of the STRONGEST biological matches because:
# - 6 legs is a DEFINING feature of the largest animal class
# - It's not a flexible taxonomy — it's a hard morphological fact
# - The 3+6 combination is highly specific
# WHY 6 legs? Biomechanical stability: 6 legs allow static stability
# during locomotion (tripod gait — always 3 legs on ground).
# Tripod gait needs >= 6 legs. So 6 is the MINIMUM for static stability.
# This IS structurally forced! But by mechanics, not number theory.
# The match n=6 ↔ hexapod legs is real but the REASON is biomechanics.
check(22,
    "Insect 6 Legs = n, 3 Segments = sigma/tau",
    "6 legs (Hexapoda) = n = 6; 3 body segments = sigma/tau = 3",
    "6 legs: defining feature of Insecta/Hexapoda (~1M+ species). "
    "3 segments: head, thorax, abdomen. 2 legs per thoracic segment. "
    "6 is minimum for static walking stability (tripod gait).",
    "Grimaldi & Engel 2005; Full & Tu 1991 (tripod gait biomechanics)",
    "n = 6 (legs), 3 = n/phi (segments), 2 = phi (legs/segment)",
    "⭐ NOTABLE — 6 legs is a hard biological fact, not a taxonomy choice. "
    "The 6=minimum-for-tripod-gait is a genuine biomechanical constraint. "
    "HOWEVER: the connection to n=6 perfect number theory is still just "
    "numerical coincidence. The biomechanical reason is about stability "
    "geometry (tripod needs 2k legs, k>=3), not about divisor sums. "
    "Downgraded from structural to notable coincidence.",
    "MODERATE — The NUMBER 6 is genuinely forced by physics. But the "
    "CONNECTION to perfect number n=6 is unestablished. Nice coincidence.",
    True
)

# ═══════════════════════════════════════════════════════════════
# R4-BIO-23: Starfish 5 Arms = sopfr(6) = 5
# ═══════════════════════════════════════════════════════════════
# Most starfish (Asteroidea) have 5 arms. Pentaradial (5-fold) symmetry.
# 5 = sopfr(6) = 2 + 3. Match.
# BUT: not all starfish have 5 arms. Many species have 6-40+ arms.
# The CLASS Asteroidea includes species with 5 to 50 arms.
# Even "standard" 5-armed starfish: 5-fold symmetry is shared by ALL
# echinoderms (sea urchins, sea cucumbers, etc.) — it's the phylum
# Echinodermata's defining feature, not specific to starfish.
# WHY 5-fold? Echinoderm larvae are bilateral; pentamery arises during
# metamorphosis. The reason for 5 (not 4 or 6) is debated — possibly
# related to developmental constraints in the water vascular system.
# 5-fold symmetry is rare in nature (it's impossible in crystal lattices).
check(23,
    "Starfish 5-fold Symmetry = sopfr(6) = 5",
    "5 arms in starfish (pentaradial symmetry) = sopfr(6) = 5",
    "Most starfish: 5 arms. But many species: 6-50 arms. "
    "5-fold symmetry is a phylum-level echinoderm feature. "
    "5 is crystallographically forbidden → biologically unusual.",
    "Mooi & David 2008 (echinoderm symmetry); Smith 2005",
    "sopfr(6) = 5",
    "⚪ WHITE — 5 is the MODAL starfish arm count, but not universal. "
    "The match sopfr(6)=5 is coincidental. The developmental reason for "
    "5-fold symmetry in echinoderms is unrelated to prime factorization.",
    "HIGH — Many starfish have 6+ arms. sopfr is a derived quantity.",
    True
)

# ═══════════════════════════════════════════════════════════════
# R4-BIO-24: Honeybee Hexagonal Comb
# ═══════════════════════════════════════════════════════════════
# Honeycomb cells are regular hexagons. A regular hexagon has 6 sides.
# 6 = n = 6. Exact match.
# The hexagonal packing IS mathematically forced:
# Honeycomb conjecture (proved by Hales 1999): hexagonal tiling is the
# MOST EFFICIENT partition of a plane into equal areas with minimum
# total perimeter. So hexagons are OPTIMAL.
# Regular hexagons tile the plane (one of only 3 regular polygon tilings:
# triangle=3, square=4, hexagon=6). Hexagon has MAXIMUM sides among these.
# Hexagonal packing: each cell has 6 neighbors.
# THIS IS GEOMETRY-FORCED, not arbitrary.
# However: the n=6 in perfect numbers and the 6 in hexagonal geometry
# share mathematical roots? 6 = 2 × 3, and hexagons tile because
# 360/60 = 6 (interior angle math). The connection to σ(6)=12 is
# still not established.
check(24,
    "Honeybee Hexagonal Comb: 6 Sides",
    "Hexagonal honeycomb cells have 6 sides = n = 6",
    "Regular hexagons: 6 sides, 120-degree angles. "
    "Hexagonal tiling is optimal plane partition (Hales 1999). "
    "Only 3 regular polygon tilings: 3, 4, 6 sides.",
    "Hales 2001 (honeycomb conjecture proof); Thompson 1917 (On Growth and Form)",
    "n = 6 (hexagon sides)",
    "⭐ GEOMETRY-FORCED — Hexagonal tiling is mathematically optimal. "
    "The number 6 here arises from 360/60 = 6, which is about planar "
    "geometry, not divisor theory. The match n=6 ↔ hexagon is that "
    "6 = 1+2+3 = 1x2x3, and 6 appears in both perfect number theory "
    "and regular polygon tiling. Same number, DIFFERENT mathematical reasons. "
    "The coincidence is notable but not structurally connected.",
    "MODERATE — 6 is genuinely geometry-forced. But the connection to "
    "PERFECT NUMBER 6 specifically (vs just the integer 6) is unestablished.",
    True
)

# ═══════════════════════════════════════════════════════════════
# R4-BIO-25: Bird V-Formation Angle
# ═══════════════════════════════════════════════════════════════
# Birds flying in V-formation: the angle between the two arms of the V
# is variable, typically 30-45 degrees half-angle (60-90 degrees full V).
# Optimal wing-tip spacing: ~1 wingspan apart (Lissaman & Shollenberger 1970).
# V angle varies with flock size, wind, species.
# Portugal et al. (2014, Nature): ibises phase-match wingbeats for
# optimal upwash, optimal angle depends on wingspan and speed.
# 60 degrees = 360/n = 360/6? Full V angle of ~60 degrees would mean
# half-angle of 30 degrees. Some measurements show ~60 deg full angle.
# But the angle is HIGHLY variable (40-80 degrees measured in wild flocks).
check(25,
    "Bird V-Formation Angle vs n=6",
    "V-formation angle relates to 360/n = 60 degrees",
    "V-formation angle: highly variable, typically 30-45 deg half-angle "
    "(60-90 deg full V). Depends on species, wind, flock size. "
    "No single characteristic angle.",
    "Portugal et al. 2014 (Nature); Lissaman & Shollenberger 1970",
    "360/n = 60 (within measured range but not a fixed value)",
    "⚪ WHITE — The V angle is continuously variable, not a discrete constant. "
    "60 degrees is within the measured range but so are 50, 70, 80 degrees. "
    "Cherry-picking 60 from a wide distribution is not a valid match.",
    "HIGH — Continuous variable. Selecting one value from a range.",
    True
)


# ═══════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("ROUND 4 BIOLOGY/NEUROSCIENCE SUMMARY")
print("=" * 72)

# Count grades
star_count = 0
white_count = 0
fail_count = 0
for r in results:
    if "FAIL" in r['grade'] or r['status'] == 'FAIL':
        if r['status'] == 'FAIL':
            fail_count += 1
    if "WHITE" in r['grade'] or "⚪" in r['grade']:
        white_count += 1
    if "⭐" in r['grade'] or "NOTABLE" in r['grade'] or "INTERESTING" in r['grade'] or "GEOMETRY" in r['grade']:
        star_count += 1

print(f"\nTotal hypotheses: {len(results)}")
print(f"Arithmetic PASS:  {PASS}")
print(f"Arithmetic FAIL:  {FAIL}")
print(f"⚪ Coincidence:   {white_count}")
print(f"⭐ Notable:       {star_count}")
print(f"No-match (honest): {fail_count}")

print(f"\n{'─'*72}")
print(f"{'ID':<12} {'Title':<45} {'Grade':<8}")
print(f"{'─'*72}")

for r in results:
    rid = f"R4-BIO-{r['id']:02d}"
    title = r['title'][:44]
    if r['status'] == 'FAIL':
        grade = "FAIL"
    elif "⭐" in r['grade'] or "NOTABLE" in r['grade'] or "INTERESTING" in r['grade'] or "GEOMETRY" in r['grade']:
        grade = "⭐"
    elif "WHITE" in r['grade'] or "⚪" in r['grade']:
        grade = "⚪"
    else:
        grade = "?"
    print(f"{rid:<12} {title:<45} {grade}")

print(f"\n{'='*72}")
print("BRUTAL HONESTY ASSESSMENT")
print("="*72)
print("""
Of 25 hypotheses tested:

GENUINE STRUCTURAL MATCHES: 0
  None of these are structurally connected to perfect number theory.

NOTABLE COINCIDENCES (⭐, interesting but NOT structural):
  R4-BIO-09: Ion channel 6-TM topology — Real protein structure, but
             the connection to n=6 perfect number is unestablished.
  R4-BIO-22: Insect 6 legs — Real biomechanical constraint (tripod gait
             minimum), but forced by stability geometry, not number theory.
  R4-BIO-24: Honeycomb hexagons — Geometry-forced optimality (Hales 1999),
             but 6 arises from planar angle math, not divisor sums.

TRIVIAL COINCIDENCES (⚪, small number matching): 19
  Most biology numbers are 2-6. With n=6 having divisors {1,2,3,6},
  tau=4, phi=2, sopfr=5, the n=6 system covers {1,2,3,4,5,6,12,24}.
  Almost ANY small biological number will match something.

HONEST FAILURES: 3
  R4-BIO-10 (myelin), R4-BIO-11 (minicolumns), R4-BIO-12 (Brodmann 44)

THE CORE PROBLEM:
  n=6 arithmetic {1,2,3,4,5,6,12,24} covers most small integers.
  Biology uses small integers for classification (layers, stages, types).
  Matching is EXPECTED by chance, not evidence of structure.

  A proper test: What biological constants are LARGE and SPECIFIC,
  and still match n=6 arithmetic? Almost none.

  The 3 notable cases (⭐) are notable because the NUMBER 6 itself
  appears for genuine physical reasons (stability, packing, topology),
  but the connection to PERFECT NUMBER n=6 remains unestablished.
""")

print("="*72)
print("TEXAS SHARPSHOOTER CHECK")
print("="*72)
print(f"""
  Target set: {{1, 2, 3, 4, 5, 6, 12, 24}} (n=6 arithmetic outputs)
  Coverage of integers 1-6: 6/6 = 100%
  Coverage of integers 1-10: 8/10 = 80%

  P(random biology number 1-10 matches) ≈ 80%
  P(random biology number 1-6 matches) = 100%

  Since most biology classification numbers ARE in 1-6 range,
  the expected match rate is ~80-100% by pure chance.

  Observed match rate: {PASS}/{len(results)} = {PASS/len(results)*100:.0f}%
  Expected by chance:  ~80-90% (for numbers in 1-10 range)

  CONCLUSION: Match rate is CONSISTENT WITH CHANCE.
  No evidence of non-random structure in biology-n=6 mapping.

  The 3 FAIL cases are actually INFORMATIVE — they show the method
  can honestly reject non-matches, unlike a biased search.
""")

if __name__ == "__main__":
    pass
