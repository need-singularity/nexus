#!/usr/bin/env python3
"""
Verify 15 Linguistics/Cognitive Science Hypotheses Connecting to n=6
====================================================================
Perfect number framework: n=6, sigma(6)=12, tau(6)=4, phi(6)=2, sigma_{-1}(6)=2
Golden Zone: [0.2123, 0.5], center 1/e ~ 0.3679
"""

import math
import random

# ──────────────────────────────────────────────────────────────────
# n=6 constants
# ──────────────────────────────────────────────────────────────────
N = 6
SIGMA = 12          # sum of divisors
TAU = 4             # number of divisors
PHI = 2             # Euler totient
SIGMA_NEG1 = 2.0    # sum of reciprocal divisors: 1+1/2+1/3+1/6
DIVISORS = [1, 2, 3, 6]
GZ_UPPER = 0.5
GZ_LOWER = 0.5 - math.log(4/3)  # 0.2123
GZ_CENTER = 1/math.e             # 0.3679
GZ_WIDTH = math.log(4/3)         # 0.2877

# ──────────────────────────────────────────────────────────────────
# Texas Sharpshooter test
# ──────────────────────────────────────────────────────────────────
def texas_test(observed, predicted, domain_lo=0, domain_hi=None, n_candidates=15, n_trials=100000):
    """Compute p-value with Bonferroni correction.
    Tests: how likely is a random value in [domain_lo, domain_hi] to be
    as close as |observed-predicted| to observed?"""
    if domain_hi is None:
        domain_hi = max(observed * 3, 20)
    tolerance = abs(observed - predicted)
    rng = random.Random(42)
    hits = 0
    for _ in range(n_trials):
        rand_val = rng.uniform(domain_lo, domain_hi)
        if abs(rand_val - observed) <= tolerance:
            hits += 1
    p = hits / n_trials
    p_corrected = min(1.0, p * n_candidates)
    return p_corrected


def grade(error_pct, p_value, exact=False, ad_hoc=False):
    """Assign grade based on verification rules."""
    if exact and not ad_hoc:
        return "GREEN"
    if ad_hoc:
        if p_value < 0.05:
            return "ORANGE"
        return "WHITE"
    if error_pct < 2.0 and p_value < 0.01:
        return "ORANGE_STAR"
    if error_pct < 5.0 and p_value < 0.05:
        return "ORANGE"
    return "WHITE"


GRADE_EMOJI = {
    "GREEN": "\U0001f7e9",       # green
    "ORANGE_STAR": "\U0001f7e7\u2b50",  # orange + star
    "ORANGE": "\U0001f7e7",      # orange
    "WHITE": "\u26aa",           # white
    "BLACK": "\u2b1b",           # black
}

results = []

print("=" * 72)
print("  LINGUISTICS / COGNITIVE SCIENCE HYPOTHESES -- n=6 VERIFICATION")
print("=" * 72)

# ======================================================================
# SECTION A: LINGUISTICS (5 hypotheses)
# ======================================================================
print("\n" + "=" * 72)
print("  SECTION A: LINGUISTICS")
print("=" * 72)

# ------------------------------------------------------------------
# H-LING-001: Basic word orders = 3! = 6
# ------------------------------------------------------------------
print("\n--- H-LING-001: Basic Word Orders = 3! = 6 ---")
print("  Subject (S), Object (O), Verb (V) can appear in any order.")
print("  Permutations of 3 elements = 3! = 6")
print("  The 6 attested word orders:")
orders = ["SOV", "SVO", "VSO", "VOS", "OVS", "OSV"]
for i, o in enumerate(orders, 1):
    print(f"    {i}. {o}")
print(f"  All 6 orders are attested in world languages.")
print(f"  3! = {math.factorial(3)} = {N}")
print(f"  This is a COMBINATORIAL FACT, not a hypothesis.")
print(f"  3! = 6 = n is exact and follows from definition.")
# Frequency distribution (WALS data, approximate):
freqs = {
    "SOV": 45.0, "SVO": 42.0, "VSO": 9.0,
    "VOS": 3.0,  "OVS": 1.0,  "OSV": 0.3
}
print(f"  Approximate frequency distribution (WALS):")
for o, f in freqs.items():
    bar = "#" * int(f)
    print(f"    {o}: {f:5.1f}% |{bar}")
# The fact that 3!=6=n is exact combinatorics, not numerology
g = "GREEN"
print(f"  Grade: {GRADE_EMOJI[g]} -- 3!=6 is exact combinatorial identity")
print(f"  Note: This is a mathematical fact (3!=6), not a prediction.")
print(f"  The connection to perfect number 6 is that 6 = 1*2*3 = 3!.")
results.append(("H-LING-001", "Basic word orders = 3! = 6 = n", 0.0, 0.0, g, False))

# ------------------------------------------------------------------
# H-LING-002: Chomsky hierarchy has 4 grammar types = tau(6)
# ------------------------------------------------------------------
print("\n--- H-LING-002: Chomsky Hierarchy = 4 types = tau(6) ---")
chomsky_types = ["Type 0: Recursively enumerable (Turing machine)",
                 "Type 1: Context-sensitive (LBA)",
                 "Type 2: Context-free (PDA)",
                 "Type 3: Regular (FSA)"]
print(f"  Chomsky hierarchy grammar types: {len(chomsky_types)}")
for t in chomsky_types:
    print(f"    {t}")
print(f"  tau(6) = {TAU}")
print(f"  Match: exact ({len(chomsky_types)} == {TAU})")
print()
print(f"  CRITICAL ANALYSIS:")
print(f"  Chomsky chose to classify by 4 levels of automaton power.")
print(f"  This is a human classification choice, not a natural constant.")
print(f"  One could subdivide further (e.g., mildly context-sensitive,")
print(f"  indexed grammars, tree-adjoining grammars) to get 6+ types.")
print(f"  The number 4 here is an artifact of the classification scheme.")
# Texas test: 4 out of integers 1-10 = not very surprising
p = texas_test(4, TAU, domain_lo=2, domain_hi=10, n_candidates=15)
print(f"  p-value (Bonferroni): {p:.4f}")
g = "WHITE"
print(f"  Grade: {GRADE_EMOJI[g]} -- classification count is human choice, not natural")
results.append(("H-LING-002", "Chomsky hierarchy = 4 = tau(6)", 0.0, p, g, False))

# ------------------------------------------------------------------
# H-LING-003: Most common vowel system = 5, some have 6
# ------------------------------------------------------------------
print("\n--- H-LING-003: Vowel System Size ~ 6? ---")
# WALS chapter 2: vowel quality inventories
# 5-vowel system (/a e i o u/) is most common (~31% of 563 languages)
# Distribution:
vowel_dist = {
    "2-4 (small)": 92,
    "5 (average-low)": 174,
    "6 (average)": 100,
    "7-14 (large+)": 197,
}
total_langs = sum(vowel_dist.values())
print(f"  WALS vowel inventory sizes (N={total_langs} languages):")
for cat, count in vowel_dist.items():
    pct = count / total_langs * 100
    bar = "#" * int(pct / 2)
    print(f"    {cat:20s}: {count:3d} ({pct:5.1f}%) |{bar}")
print()
print(f"  Most common single count: 5 (not 6)")
print(f"  5-vowel system: 174 languages (~31%)")
print(f"  6-vowel system: ~100 languages (~18%)")
print(f"  Median inventory size across all languages: ~5-6")
median_approx = 5.5
print(f"  Approximate median: {median_approx}")
print(f"  n = {N}")
error_pct = abs(median_approx - N) / N * 100
print(f"  Error: {error_pct:.1f}%")
print()
print(f"  CRITICAL ANALYSIS:")
print(f"  The mode is 5, not 6. Claiming 6 requires cherry-picking.")
print(f"  Vowel inventories range from 2 to 14+. The distribution is broad.")
g = "WHITE"
print(f"  Grade: {GRADE_EMOJI[g]} -- mode is 5, not 6; broad distribution")
results.append(("H-LING-003", "Vowel system size ~ 6", error_pct, 1.0, g, False))

# ------------------------------------------------------------------
# H-LING-004: Phoneme inventory medians
# ------------------------------------------------------------------
print("\n--- H-LING-004: Phoneme Inventory Ratios ---")
# WALS/UPSID data:
# Median consonant inventory: ~22 (range 6-122)
# Median vowel inventory: ~5 (range 2-14)
# Total median: ~27 (range 11-141)
median_consonants = 22
median_vowels = 5
total_phonemes = median_consonants + median_vowels  # ~27
ratio_cv = median_consonants / median_vowels  # 4.4
print(f"  Median consonant inventory: ~{median_consonants}")
print(f"  Median vowel inventory: ~{median_vowels}")
print(f"  Consonant/Vowel ratio: {ratio_cv:.1f}")
print(f"  tau(6) = {TAU}, N-1 = {N-1}")
print(f"  Ratio is ~4.4, near tau(6)=4 within 10%")
error_pct_cv = abs(ratio_cv - TAU) / TAU * 100
print(f"  Error from tau(6): {error_pct_cv:.1f}%")
print()
print(f"  Total phonemes: ~{total_phonemes}")
print(f"  N! / N^2 = 720/36 = {math.factorial(N)/N**2:.0f} -- no match")
print(f"  sigma(6)*phi(6)+tau(6)-1 = 24+3 = {SIGMA*PHI+TAU-1} -- close but ad-hoc")
print()
print(f"  CRITICAL ANALYSIS:")
print(f"  C/V ratio varies widely across language families (2-12).")
print(f"  Median ~4.4 is near 4 but the distribution is very broad.")
print(f"  With 15 candidates, matching any small integer is easy.")
p = texas_test(ratio_cv, TAU, domain_lo=2, domain_hi=12, n_candidates=15)
print(f"  p-value (Bonferroni): {p:.4f}")
g = "WHITE"
print(f"  Grade: {GRADE_EMOJI[g]} -- broad distribution, small integer match is easy")
results.append(("H-LING-004", "C/V phoneme ratio ~ tau(6)=4", error_pct_cv, p, g, False))

# ------------------------------------------------------------------
# H-LING-005: Morpheme types
# ------------------------------------------------------------------
print("\n--- H-LING-005: Morpheme Type Count ---")
morph_types = [
    "1. Free lexical (content words: noun, verb, adj)",
    "2. Free grammatical (function words: det, conj, prep)",
    "3. Bound derivational prefix",
    "4. Bound derivational suffix",
    "5. Bound inflectional prefix",
    "6. Bound inflectional suffix",
]
print(f"  Standard morpheme classification:")
for m in morph_types:
    print(f"    {m}")
print(f"  Count: {len(morph_types)}")
print(f"  n = {N}")
print()
print(f"  CRITICAL ANALYSIS:")
print(f"  This classification depends heavily on granularity.")
print(f"  Alternative: 2 types (free/bound)")
print(f"  Alternative: 3 types (lexical/derivational/inflectional)")
print(f"  Alternative: 8+ types (adding clitics, circumfixes, infixes, etc.)")
alt_counts = [2, 3, 4, 6, 8, 10]
print(f"  Plausible type counts depending on classification: {alt_counts}")
print(f"  Getting 6 requires a specific (not universal) typology.")
g = "WHITE"
print(f"  Grade: {GRADE_EMOJI[g]} -- classification granularity is arbitrary")
results.append(("H-LING-005", "Morpheme types = 6", 0.0, 1.0, g, False))

# ======================================================================
# SECTION B: COGNITIVE SCIENCE (5 hypotheses)
# ======================================================================
print("\n" + "=" * 72)
print("  SECTION B: COGNITIVE SCIENCE")
print("=" * 72)

# ------------------------------------------------------------------
# H-LING-006: Cowan's working memory = 4 = tau(6)
# ------------------------------------------------------------------
print("\n--- H-LING-006: Cowan's Working Memory Capacity = 4 = tau(6) ---")
cowan_capacity = 4  # Cowan (2001): 4 +/- 1 chunks
miller_capacity = 7  # Miller (1956): 7 +/- 2
print(f"  Cowan (2001): working memory capacity = {cowan_capacity} +/- 1 chunks")
print(f"  Miller (1956): 7 +/- 2 items (older, less precise)")
print(f"  tau(6) = {TAU}")
print(f"  Match with Cowan: exact")
print()
print(f"  CRITICAL ANALYSIS:")
print(f"  Cowan's 4 is well-established in modern cognitive science.")
print(f"  But: it is 4 +/- 1 (range 3-5), not a sharp constant.")
print(f"  tau(6)=4 is a small integer. Many things equal 4.")
print(f"  No mechanistic reason why WM capacity should relate to divisors of 6.")
p = texas_test(4, TAU, domain_lo=1, domain_hi=10, n_candidates=15)
print(f"  p-value (Bonferroni): {p:.4f}")
g = "WHITE"
print(f"  Grade: {GRADE_EMOJI[g]} -- 4 is common small integer, no causal mechanism")
results.append(("H-LING-006", "Cowan WM=4=tau(6)", 0.0, p, g, False))

# ------------------------------------------------------------------
# H-LING-007: Ebbinghaus forgetting: retention at t=S is 1/e = GZ center
# ------------------------------------------------------------------
print("\n--- H-LING-007: Ebbinghaus Forgetting Curve ~ 1/e ---")
print(f"  Ebbinghaus (1885) forgetting curve: R(t) = e^(-t/S)")
print(f"  At t = S (one time constant): R = e^(-1) = 1/e = {1/math.e:.4f}")
print(f"  Golden Zone center = 1/e = {GZ_CENTER:.4f}")
print(f"  Match: EXACT by definition of exponential decay")
print()
print(f"  BUT: Modern forgetting curves are NOT simple exponential.")
print(f"  Wixted (2004): power law R(t) = a*t^(-b) fits better")
print(f"  Rubin & Wenzel (1996): logarithmic, power, exponential all tested")
print(f"  The e^(-t/S) form is the simplest model, not the most accurate.")
print()
print(f"  Even granting exponential decay:")
print(f"  R(t=S) = 1/e is true for ANY exponential decay process.")
print(f"  This is a property of e, not of memory or consciousness.")
print(f"  Same 1/e appears in RC circuits, radioactive decay, etc.")
print()
print(f"  Is this a meaningful connection to Golden Zone?")
print(f"  The Golden Zone claims 1/e as optimal inhibition level.")
print(f"  Memory retention at 1/e is a DECAY marker, not an optimum.")
print(f"  These are different senses of 1/e.")
g = "GREEN"
print(f"  Grade: {GRADE_EMOJI[g]} -- e^(-1)=1/e is exact, but it is a property of")
print(f"  exponential functions, not specific to memory or consciousness.")
print(f"  Mathematically true but scientifically vacuous as n=6 connection.")
ad_hoc_note = True
results.append(("H-LING-007", "Ebbinghaus R(S)=1/e=GZ_center", 0.0, 0.0, g, ad_hoc_note))

# ------------------------------------------------------------------
# H-LING-008: Dual process = 2 = phi(6)
# ------------------------------------------------------------------
print("\n--- H-LING-008: Dual Process Theory: 2 Systems = phi(6) ---")
print(f"  Kahneman (2011): System 1 (fast/intuitive) + System 2 (slow/deliberate)")
print(f"  phi(6) = {PHI}")
print(f"  Match: exact (2 == 2)")
print()
print(f"  CRITICAL ANALYSIS:")
print(f"  2 is the smallest prime. Almost anything has a binary division.")
print(f"  Binary categorizations in cogsci: conscious/unconscious,")
print(f"  explicit/implicit, declarative/procedural, automatic/controlled...")
print(f"  Having 2 systems is the most trivial possible count.")
print(f"  phi(6)=2 because 6=2*3 and only 1,5 are coprime -- unrelated.")
p = texas_test(2, PHI, domain_lo=1, domain_hi=5, n_candidates=15)
print(f"  p-value (Bonferroni): {p:.4f}")
g = "WHITE"
print(f"  Grade: {GRADE_EMOJI[g]} -- trivially true; 2 is the most common count for any dichotomy")
results.append(("H-LING-008", "Dual process = 2 = phi(6)", 0.0, p, g, False))

# ------------------------------------------------------------------
# H-LING-009: Hick's law RT = a + b*log2(n)
# ------------------------------------------------------------------
print("\n--- H-LING-009: Hick's Law and n=6 ---")
print(f"  Hick's law: RT = a + b * log2(n)")
print(f"  For n=6 choices: RT = a + b * log2(6) = a + b * {math.log2(6):.4f}")
print(f"  log2(6) = log2(2*3) = 1 + log2(3) = {math.log2(6):.4f}")
print(f"  = {math.log2(6):.4f}")
print()
print(f"  Attempting n=6 connections:")
print(f"  log2(sigma(6)) = log2(12) = {math.log2(12):.4f}")
print(f"  log2(N) = log2(6) = {math.log2(6):.4f}")
print(f"  GZ_WIDTH = ln(4/3) = {GZ_WIDTH:.4f}")
print(f"  log2(6) = {math.log2(6):.4f} vs sigma_neg1(6) = {SIGMA_NEG1:.4f}")
err = abs(math.log2(6) - SIGMA_NEG1 - 0.585) # meaningless arithmetic
print()
print(f"  CRITICAL ANALYSIS:")
print(f"  Hick's law uses log2 because it measures information in bits.")
print(f"  The law works for ANY n, not specifically n=6.")
print(f"  No special behavior at n=6 vs n=5 or n=7.")
print(f"  log2(6)=2.585 does not match any n=6 constant cleanly.")
g = "WHITE"
print(f"  Grade: {GRADE_EMOJI[g]} -- Hick's law has no special behavior at n=6")
results.append(("H-LING-009", "Hick's law at n=6", 0.0, 1.0, g, False))

# ------------------------------------------------------------------
# H-LING-010: Stroop effect
# ------------------------------------------------------------------
print("\n--- H-LING-010: Stroop Effect and Processing Channels ---")
print(f"  Stroop effect: interference between word reading and color naming")
print(f"  Standard Stroop uses 3-6 colors (most commonly 4)")
print(f"  Standard conditions: 3 (congruent, incongruent, neutral)")
print()
print(f"  Attempting n=6 connection:")
print(f"  Common Stroop color count: 4 = tau(6)")
print(f"  Conditions: 3 = divisor of 6")
print(f"  Stroop interference ratio (incongruent/congruent RT):")
print(f"    Typical: ~1.3-1.5x slowdown")
stroop_ratio = 1.4  # typical
print(f"    ~{stroop_ratio}")
print(f"    GZ = [{GZ_LOWER:.4f}, {GZ_UPPER:.4f}]")
stroop_diff_pct = (stroop_ratio - 1.0)  # 0.4 = 40% slowdown
print(f"    Slowdown fraction: {stroop_diff_pct:.1f}")
print(f"    GZ center: {GZ_CENTER:.4f}")
print(f"    Not a match.")
print()
print(f"  CRITICAL ANALYSIS:")
print(f"  No clean n=6 connection. Color count (4) and conditions (3)")
print(f"  are experimenter choices, not natural constants.")
g = "WHITE"
print(f"  Grade: {GRADE_EMOJI[g]} -- no meaningful n=6 connection found")
results.append(("H-LING-010", "Stroop effect n=6 connection", 0.0, 1.0, g, False))

# ======================================================================
# SECTION C: LANGUAGE STATISTICS (5 hypotheses)
# ======================================================================
print("\n" + "=" * 72)
print("  SECTION C: LANGUAGE STATISTICS")
print("=" * 72)

# ------------------------------------------------------------------
# H-LING-011: Zipf's law exponent ~1
# ------------------------------------------------------------------
print("\n--- H-LING-011: Zipf's Law Exponent ~ 1 ---")
zipf_alpha = 1.0  # Zipf's law: f(r) ~ r^(-alpha), alpha ~ 1
print(f"  Zipf's law: frequency of rank r ~ r^(-alpha)")
print(f"  Observed alpha: ~{zipf_alpha} (range 0.8-1.2 across corpora)")
print(f"  n=6 candidates:")
print(f"    phi(6)/sigma_neg1(6) = {PHI}/{SIGMA_NEG1} = {PHI/SIGMA_NEG1:.4f}")
print(f"    tau(6)/tau(6) = 1 (trivial)")
print(f"    6/sigma(6) = {N/SIGMA:.4f} (not 1)")
print(f"    N/N = 1 (trivially true for any n)")
print()
print(f"  CRITICAL ANALYSIS:")
print(f"  Zipf's alpha=1 emerges from scale-free processes, not from n=6.")
print(f"  It appears in city sizes, wealth distributions, earthquake magnitudes.")
print(f"  It is a universal scaling phenomenon (self-organized criticality).")
print(f"  Expressing 1 = phi(6)/sigma_neg1(6) = 2/2 is trivial arithmetic.")
g = "WHITE"
print(f"  Grade: {GRADE_EMOJI[g]} -- alpha=1 is universal scaling, trivially expressible")
results.append(("H-LING-011", "Zipf alpha ~ 1 from n=6", 0.0, 1.0, g, False))

# ------------------------------------------------------------------
# H-LING-012: English letter E frequency 12.7% ~ sigma(6)/100?
# ------------------------------------------------------------------
print("\n--- H-LING-012: English Letter E Frequency ~ sigma(6)/100 ---")
e_freq = 12.702  # percent, based on large English corpora
sigma_pct = SIGMA  # 12
error_pct = abs(e_freq - sigma_pct) / e_freq * 100
print(f"  English letter 'E' frequency: {e_freq:.3f}%")
print(f"  sigma(6) = {SIGMA}")
print(f"  sigma(6)/100 = {SIGMA/100:.4f} = {SIGMA}%")
print(f"  Error: {error_pct:.2f}%")
print()
# Texas test: how likely is sigma(6)=12 to match a percentage in [5,20]?
# 26 letters, frequencies range from ~0.07% (Z) to ~12.7% (E)
# Only E is near 12%. But we have 15 hypotheses to match.
p = texas_test(e_freq, sigma_pct, domain_lo=0, domain_hi=26, n_candidates=15)
print(f"  p-value (Bonferroni): {p:.4f}")
print()
print(f"  CRITICAL ANALYSIS:")
print(f"  E frequency = 12.702%, sigma(6) = 12. Error = {error_pct:.1f}%.")
print(f"  The 5.5% error is moderate. But why would E frequency")
print(f"  relate to divisor sum of 6?")
print(f"  E frequency varies by language: French 14.7%, German 16.4%, Spanish 13.7%")
print(f"  It is an accident of English orthography + morphology.")
print(f"  If French, we would need sigma=15; German, sigma=16.")
lang_e_freqs = {"English": 12.7, "French": 14.7, "German": 16.4,
                "Spanish": 13.7, "Italian": 11.8, "Portuguese": 12.6}
print(f"  Letter E frequency across languages:")
for lang, freq in lang_e_freqs.items():
    err = abs(freq - SIGMA) / freq * 100
    print(f"    {lang:12s}: {freq:5.1f}% (error from 12: {err:5.1f}%)")
g = "WHITE"
print(f"  Grade: {GRADE_EMOJI[g]} -- language-specific, varies 11-17%, coincidence")
results.append(("H-LING-012", "English E freq ~ sigma(6)%", error_pct, p, g, False))

# ------------------------------------------------------------------
# H-LING-013: Entropy of English text ~1.0-1.5 bits/char
# ------------------------------------------------------------------
print("\n--- H-LING-013: English Text Entropy ~ GZ_WIDTH or 1/e? ---")
# Shannon (1951): H ~ 1.0-1.3 bits/character for English
# Cover & King (1978): H ~ 1.34 bits/char
# Brown et al. (1992): H ~ 1.75 bits/char (word level, different metric)
shannon_H = 1.3  # bits/char, consensus for character-level English
print(f"  Shannon entropy of English: ~{shannon_H} bits/char")
print(f"  (Shannon 1951, Cover & King 1978 estimate)")
print()
print(f"  n=6 candidates:")
print(f"    GZ_WIDTH = ln(4/3) = {GZ_WIDTH:.4f} -- no")
print(f"    sigma_neg1(6)/phi(6) = {SIGMA_NEG1/PHI:.4f} -- exact 1.0, low")
print(f"    log2(e) = {math.log2(math.e):.4f} -- 1.443")
print(f"    log2(phi(6)) = {math.log2(PHI):.4f} -- exact 1.0")
print(f"    Error from log2(e): {abs(shannon_H - math.log2(math.e))/shannon_H*100:.1f}%")
print()
print(f"  CRITICAL ANALYSIS:")
print(f"  English entropy ~1.0-1.5 is determined by English grammar and")
print(f"  vocabulary, not by any universal constant.")
print(f"  Different languages have different entropies:")
print(f"    Chinese: ~9.7 bits/character (logographic)")
print(f"    Finnish: ~1.5 bits/char (agglutinative)")
print(f"    Hawaiian: ~1.0 bits/char (small phoneme inventory)")
print(f"  No single n=6 constant matches, and H is language-dependent.")
g = "WHITE"
print(f"  Grade: {GRADE_EMOJI[g]} -- H is language-dependent, no clean n=6 match")
results.append(("H-LING-013", "English entropy ~ n=6 constant", 0.0, 1.0, g, False))

# ------------------------------------------------------------------
# H-LING-014: Heaps' law V(n) = K * n^beta, beta ~ 0.4-0.6
# ------------------------------------------------------------------
print("\n--- H-LING-014: Heaps' Law beta ~ GZ? ---")
# Heaps' law: vocabulary size V(n) = K * n^beta
# beta typically 0.4-0.6 for English
# beta ~ 0.5 for many natural languages
heaps_beta = 0.5  # typical for English
heaps_beta_range = (0.4, 0.6)
print(f"  Heaps' law: V(n) = K * n^beta")
print(f"  Typical beta: {heaps_beta} (range {heaps_beta_range})")
print(f"  GZ_UPPER = {GZ_UPPER} = 1/2")
print(f"  Match with GZ_UPPER: {'exact' if heaps_beta == GZ_UPPER else 'no'}")
error_pct = abs(heaps_beta - GZ_UPPER) / heaps_beta * 100
print(f"  Error: {error_pct:.1f}%")
print()
print(f"  CRITICAL ANALYSIS:")
print(f"  beta=0.5 means V(n) ~ sqrt(n). This IS interesting because:")
print(f"  1/2 appears in many places (Riemann critical line, random walk, etc.)")
print(f"  But beta varies by language and corpus (0.4-0.8).")
print(f"  The 'typical' value of 0.5 is within [0.4, 0.6] but not sharp.")
print(f"  beta=0.5 is in Golden Zone [{GZ_LOWER:.3f}, {GZ_UPPER:.3f}]")
# Is beta in GZ?
in_gz = GZ_LOWER <= heaps_beta <= GZ_UPPER
print(f"  beta in Golden Zone: {in_gz}")
print(f"  But GZ spans 29% of [0,1], so random beta has 29% chance of landing in GZ.")
p_random = GZ_WIDTH  # probability of random [0,1] value in GZ ~ 29%
print(f"  Random probability of falling in GZ: {p_random:.1%}")
p = min(1.0, p_random * 15)  # Bonferroni
print(f"  p-value (Bonferroni): {p:.4f} (>1, capped)")
g = "WHITE"
print(f"  Grade: {GRADE_EMOJI[g]} -- beta=0.5 is boundary of GZ, but GZ covers 29% of [0,1]")
results.append(("H-LING-014", "Heaps beta ~ GZ_UPPER = 1/2", error_pct, p, g, False))

# ------------------------------------------------------------------
# H-LING-015: Benford's law P(d=1) = log10(2) = 0.301, in Golden Zone
# ------------------------------------------------------------------
print("\n--- H-LING-015: Benford's Law P(d=1) = log10(2) in Golden Zone ---")
benford_p1 = math.log10(2)  # 0.30103
print(f"  Benford's law: P(leading digit = 1) = log10(2) = {benford_p1:.5f}")
print(f"  Golden Zone: [{GZ_LOWER:.4f}, {GZ_UPPER:.4f}]")
in_gz = GZ_LOWER <= benford_p1 <= GZ_UPPER
print(f"  log10(2) in Golden Zone: {in_gz}")
print(f"  log10(2) = {benford_p1:.5f}")
print(f"  GZ_CENTER = 1/e = {GZ_CENTER:.5f}")
error_from_center = abs(benford_p1 - GZ_CENTER) / GZ_CENTER * 100
print(f"  Distance from GZ center: {error_from_center:.1f}%")
print()
# All 9 Benford probabilities
print(f"  Benford distribution for all leading digits:")
digits_in_gz = 0
for d in range(1, 10):
    p_d = math.log10(1 + 1/d)
    in_zone = GZ_LOWER <= p_d <= GZ_UPPER
    if in_zone:
        digits_in_gz += 1
    mark = "<-- IN GZ" if in_zone else ""
    bar = "#" * int(p_d * 50)
    print(f"    d={d}: P={p_d:.4f} |{bar} {mark}")
print(f"  Digits with P in Golden Zone: {digits_in_gz} out of 9")
print()
print(f"  CRITICAL ANALYSIS:")
print(f"  log10(2) = 0.301 IS in the Golden Zone [{GZ_LOWER:.3f}, {GZ_UPPER:.3f}].")
print(f"  But: GZ spans 29% of [0,1], so 2-3 of 9 Benford values")
print(f"  would fall in GZ by chance alone.")
print(f"  P(d=1) is close to GZ center (18% error).")
print(f"  This is suggestive but the GZ is wide enough to catch many values.")
print()
# More precise Texas test: is 0.301 matching 1/e = 0.368?
error_precise = abs(benford_p1 - GZ_CENTER) / GZ_CENTER * 100
print(f"  If claiming log10(2) ~ 1/e:")
print(f"    Error: {error_precise:.1f}%")
print(f"    These are fundamentally different constants (base-10 vs base-e)")
p = texas_test(benford_p1, GZ_CENTER, domain_lo=0, domain_hi=1, n_candidates=15)
print(f"  p-value (Bonferroni): {p:.4f}")
g = grade(error_precise, p)
print(f"  Grade: {GRADE_EMOJI[g]} -- log10(2) is in GZ but GZ is wide; 18% error from center")
results.append(("H-LING-015", "Benford P(1)=log10(2) in GZ", error_precise, p, g, False))

# ======================================================================
# SUMMARY
# ======================================================================
print("\n" + "=" * 72)
print("  FINAL SUMMARY")
print("=" * 72)

grade_counts = {}
for r in results:
    g = r[4]
    grade_counts[g] = grade_counts.get(g, 0) + 1

print(f"\n  {'ID':<14s} {'Claim':<45s} {'Err%':>6s} {'p-val':>6s} {'Grade':>8s}")
print(f"  {'-'*14} {'-'*45} {'-'*6} {'-'*6} {'-'*8}")
for r in results:
    hid, claim, err, p_val, g, *_ = r
    emoji = GRADE_EMOJI.get(g, g)
    claim_short = claim[:45]
    print(f"  {hid:<14s} {claim_short:<45s} {err:6.1f} {p_val:6.3f} {emoji:>8s}")

print()
print(f"  Grade distribution:")
for g_name in ["GREEN", "ORANGE_STAR", "ORANGE", "WHITE", "BLACK"]:
    count = grade_counts.get(g_name, 0)
    emoji = GRADE_EMOJI.get(g_name, g_name)
    print(f"    {emoji} {g_name}: {count}")

total = len(results)
green = grade_counts.get("GREEN", 0)
orange_star = grade_counts.get("ORANGE_STAR", 0)
orange = grade_counts.get("ORANGE", 0)
white = grade_counts.get("WHITE", 0)

print(f"\n  Total: {total} hypotheses")
print(f"  Structurally meaningful: {green + orange_star + orange}")
print(f"  Coincidence/trivial: {white}")

print(f"\n  HONEST ASSESSMENT:")
print(f"  -------------------------------------------------------")
print(f"  H-LING-001 (3!=6): Mathematically true but it is a")
print(f"    combinatorial identity, not a prediction of the model.")
print(f"  H-LING-007 (1/e forgetting): Mathematically true but it")
print(f"    is a property of exponential decay, not n=6 specific.")
print(f"  Remaining 13: White circles. Linguistics and cognitive")
print(f"    science constants do not show structural connection")
print(f"    to perfect number 6 framework.")
print(f"  -------------------------------------------------------")
print(f"  The n=6 framework does NOT have predictive power for")
print(f"  linguistics or cognitive science. Matches found are")
print(f"  either trivial (small integers) or classification-dependent")
print(f"  (researcher choice of how many categories).")
print(f"  -------------------------------------------------------")

print("\n" + "=" * 72)
print("  VERIFICATION COMPLETE")
print("=" * 72)
