#!/usr/bin/env python3
"""H-CX-434: Phoneme System = Perfect Number Arithmetic
Verify whether linguistic phoneme universals relate to perfect number 6's arithmetic functions.
"""
import numpy as np
from scipy import stats

print("=" * 70)
print("H-CX-434: Phoneme System vs Perfect Number 6 Arithmetic")
print("=" * 70)

# Perfect number 6 arithmetic functions
sigma_6 = 12      # σ(6) = sum of divisors = 1+2+3+6
tau_6 = 4          # τ(6) = number of divisors
phi_6 = 2          # φ(6) = Euler totient
sigma_inv_6 = 2.0  # σ₋₁(6) = sum of reciprocals of divisors = 1/1+1/2+1/3+1/6
n = 6              # the perfect number itself

print(f"\n--- Perfect Number 6 Functions ---")
print(f"  n       = {n}")
print(f"  σ(6)    = {sigma_6}  (sum of divisors)")
print(f"  τ(6)    = {tau_6}   (number of divisors)")
print(f"  φ(6)    = {phi_6}   (Euler totient)")
print(f"  σ₋₁(6)  = {sigma_inv_6} (reciprocal sum of divisors)")

# ============================================================
# Linguistic universals from WALS / UPSID / phonological literature
# ============================================================
print(f"\n{'='*70}")
print("LINGUISTIC UNIVERSALS (from WALS/UPSID data)")
print("="*70)

# 1. Manner of articulation classes
manner_classes = ["Stop/Plosive", "Fricative", "Nasal", "Lateral", "Trill/Tap", "Approximant"]
n_manner = len(manner_classes)
print(f"\n[1] Manner of articulation classes: {n_manner}")
for i, m in enumerate(manner_classes, 1):
    print(f"    {i}. {m}")
print(f"    → Match with n=6? {'YES' if n_manner == n else 'NO'} ({n_manner} vs {n})")

# 2. Primary places of articulation
places = ["Labial", "Dental/Alveolar", "Retroflex", "Palatal", "Velar", "Uvular/Glottal"]
# Note: minimal systems have ~6 places, extended systems add more
n_places_core = 6  # Core places in most languages
print(f"\n[2] Core places of articulation: {n_places_core}")
for i, p in enumerate(places, 1):
    print(f"    {i}. {p}")
print(f"    → Match with n=6? {'YES' if n_places_core == n else 'NO'}")

# 3. Base vowel system
# Most common: 5-vowel system (i, e, a, o, u) — ~34% of languages
# But 6-vowel system is also very common
# Theoretical minimum: 3 heights × 2 (front/back) = 6
vowel_heights = 3  # high, mid, low
vowel_backness = 2  # front, back
base_vowels = vowel_heights * vowel_backness
print(f"\n[3] Base vowel grid: {vowel_heights} heights × {vowel_backness} backness = {base_vowels}")
print(f"    → Match with n=6? {'YES' if base_vowels == n else 'NO'}")

# WALS vowel inventory size distribution
vowel_sizes = {
    "2-4 (small)": 92,
    "5-6 (average)": 288,
    "7-14 (large)": 183,
}
total_langs = sum(vowel_sizes.values())
print(f"\n    WALS vowel inventory distribution (N={total_langs}):")
for k, v in vowel_sizes.items():
    pct = v / total_langs * 100
    bar = "#" * int(pct / 2)
    print(f"    {k:20s} | {v:4d} ({pct:5.1f}%) {bar}")

# 4. Suprasegmentals
suprasegmentals = ["Tone", "Stress", "Length", "Nasalization"]
n_supra = len(suprasegmentals)
print(f"\n[4] Universal suprasegmental categories: {n_supra}")
for i, s in enumerate(suprasegmentals, 1):
    print(f"    {i}. {s}")
print(f"    → Match with τ(6)=4? {'YES' if n_supra == tau_6 else 'NO'}")

# 5. Voicing contrasts
voicing = ["Voiced", "Voiceless"]
n_voicing = len(voicing)
print(f"\n[5] Basic voicing contrast: {n_voicing}")
print(f"    → Match with φ(6)=2? {'YES' if n_voicing == phi_6 else 'NO'}")

# 6. Syllable structure universals
# CV is universal, most common patterns: CV, CVC, V, VC, CCV, CCVC
syllable_types_common = ["V", "CV", "CVC", "VC"]
n_core_syllable = len(syllable_types_common)
print(f"\n[6] Core syllable types: {n_core_syllable}")
print(f"    → Match with τ(6)=4? {'YES' if n_core_syllable == tau_6 else 'NO'}")

# 7. Mean phoneme count
mean_phonemes = 31  # from UPSID (UCLA Phonological Segment Inventory Database)
# Check: σ(6) × φ(6) + n + 1 = 12*2+6+1 = 31?
calc_31 = sigma_6 * phi_6 + n + 1
print(f"\n[7] Mean phoneme count across languages: ~{mean_phonemes}")
print(f"    σ(6)×φ(6)+n+1 = {sigma_6}×{phi_6}+{n}+1 = {calc_31}")
print(f"    → Match? {'YES' if calc_31 == mean_phonemes else 'NO'} (but has +1 ad hoc correction!)")
# Without +1:
calc_30 = sigma_6 * phi_6 + n
print(f"    σ(6)×φ(6)+n = {calc_30} (without +1)")
# Alternative: σ(6)×τ(6)/φ(6) + n + 1 = 12*4/2 + 6 + 1 = 31
calc_31b = sigma_6 * tau_6 // phi_6 + n + 1
print(f"    σ(6)×τ(6)/φ(6)+n+1 = {calc_31b} (also +1 ad hoc)")

# 8. Consonant inventories
# WALS: small (6-14), moderately small (15-18), average (19-25),
#        moderately large (26-33), large (34+)
# Median consonant count ≈ 22
median_consonants = 22
# Check: σ(6) × σ₋₁(6) - φ(6) = 12*2-2 = 22
calc_22 = int(sigma_6 * sigma_inv_6 - phi_6)
print(f"\n[8] Median consonant inventory: ~{median_consonants}")
print(f"    σ(6)×σ₋₁(6)-φ(6) = {sigma_6}×{sigma_inv_6}-{phi_6} = {calc_22}")
print(f"    → Match? {'YES' if calc_22 == median_consonants else 'NO'}")

# ============================================================
# Statistical verification: Texas Sharpshooter test
# ============================================================
print(f"\n{'='*70}")
print("STATISTICAL VERIFICATION")
print("="*70)

# Count matches
matches = [
    ("Manner classes = n", n_manner == n),
    ("Core places = n", n_places_core == n),
    ("Base vowels = n", base_vowels == n),
    ("Suprasegmentals = τ(6)", n_supra == tau_6),
    ("Voicing contrast = φ(6)", n_voicing == phi_6),
    ("Core syllable types = τ(6)", n_core_syllable == tau_6),
    ("Mean phonemes = σ×φ+n+1", calc_31 == mean_phonemes),  # ad hoc!
    ("Median consonants = σ×σ₋₁-φ", calc_22 == median_consonants),
]

print(f"\n--- Match Summary ---")
n_total = len(matches)
n_match = 0
for name, matched in matches:
    status = "MATCH" if matched else "MISS"
    adhoc = " (ad hoc +1!)" if "+1" in name and matched else ""
    print(f"  [{status:5s}] {name}{adhoc}")
    if matched:
        n_match += 1

# Strict matches (exclude ad hoc)
n_strict = sum(1 for name, m in matches if m and "+1" not in name)
print(f"\n  Total matches: {n_match}/{n_total}")
print(f"  Strict (no ad hoc): {n_strict}/{n_total}")

# Binomial test: probability of getting this many matches by chance
# Null: each parameter could match any of {6, 12, 4, 2} = 4 target values
# Probability of random match: we need to estimate
# Linguistic parameters range roughly 2-30, so P(match one of 4 targets) ≈ 4/30 ≈ 0.133
p_random = 4 / 30  # conservative estimate
p_value_strict = stats.binomtest(n_strict, n_total, p_random, alternative='greater').pvalue
p_value_all = stats.binomtest(n_match, n_total, p_random, alternative='greater').pvalue

print(f"\n--- Binomial Test ---")
print(f"  P(random match) ≈ {p_random:.3f} (4 targets in range 2-30)")
print(f"  Strict: {n_strict}/{n_total} matches, p = {p_value_strict:.6f}")
print(f"  All:    {n_match}/{n_total} matches, p = {p_value_all:.6f}")

# Expected matches under null
expected = n_total * p_random
print(f"\n  Expected random matches: {expected:.1f} ± {np.sqrt(n_total * p_random * (1-p_random)):.1f}")
print(f"  Observed (strict): {n_strict}")
print(f"  Observed (all): {n_match}")

# Bonferroni correction: we tested multiple formulas for items 7,8
n_formulas_tried = 5  # rough estimate of formulas tried
p_bonferroni = min(p_value_strict * n_formulas_tried, 1.0)
print(f"\n  Bonferroni correction (×{n_formulas_tried}): p = {p_bonferroni:.6f}")

# ============================================================
# Perfect number 28 generalization test
# ============================================================
print(f"\n{'='*70}")
print("GENERALIZATION TEST: Perfect Number 28")
print("="*70)

sigma_28 = 56  # 1+2+4+7+14+28
tau_28 = 6
phi_28 = 12  # 28 × (1-1/2)(1-1/7) = 12
n_28 = 28

print(f"  σ(28)={sigma_28}, τ(28)={tau_28}, φ(28)={phi_28}")
print(f"  Manner classes=6 vs τ(28)=6: MATCH (but different function!)")
print(f"  This means the pattern is n=6-specific, NOT a general perfect number law.")
print(f"  → Conclusion: patterns are tied to the NUMBER 6, not to 'perfect number' property")

# ============================================================
# ASCII Graph: Linguistic parameters vs n=6 functions
# ============================================================
print(f"\n{'='*70}")
print("ASCII GRAPH: Match Landscape")
print("="*70)

params = ["Manner", "Places", "Vowels", "Supra", "Voice", "Syllable", "Mean_Ph", "Med_Con"]
observed = [6, 6, 6, 4, 2, 4, 31, 22]
targets  = [6, 6, 6, 4, 2, 4, 31, 22]  # what we matched to
functions= ["n", "n", "n", "τ", "φ", "τ", "σφ+n+1", "σσ₋₁-φ"]

print(f"\n  Parameter   | Observed | Target    | Function  | Match")
print(f"  -----------+---------+-----------+-----------+------")
for p, o, t, f in zip(params, observed, targets, functions):
    m = "YES" if o == t else "NO"
    print(f"  {p:11s} | {o:7d} | {t:9d} | {f:9s} | {m}")

print(f"\n  Deviation from targets:")
print(f"  {'Parameter':11s} | Deviation bar")
print(f"  -----------+{'─'*40}")
for p, o, t in zip(params, observed, targets):
    dev = o - t
    if dev == 0:
        bar = "█ EXACT"
    elif dev > 0:
        bar = "+" * min(dev, 30) + f" (+{dev})"
    else:
        bar = "-" * min(abs(dev), 30) + f" ({dev})"
    print(f"  {p:11s} | {bar}")

print(f"\n{'='*70}")
print("FINAL ASSESSMENT")
print("="*70)
grade = "🟧" if p_value_strict < 0.05 else "⚪"
if p_value_strict < 0.01:
    grade = "🟧★"
print(f"  Strict matches: {n_strict}/{n_total}")
print(f"  p-value (strict, Bonferroni): {p_bonferroni:.6f}")
print(f"  Grade: {grade}")
print(f"  Note: Direct matches (manner=6, places=6, vowels=6) are striking")
print(f"        but composite formula matches have ad hoc issues")
print(f"  Generalization to n=28: FAILS (n=6 specific)")
print(f"  → Structural coincidence or anthropic constraint, not general law")
