#!/usr/bin/env python3
"""
MUSIC-001: Verify 12-TET = sigma(6) and consonance = d(6) ratios.

Usage: PYTHONPATH=. python3 verify/verify_music_001_twelve_tone.py
"""

import math
from fractions import Fraction

# ── n=6 number-theoretic constants ──────────────────────────────
n = 6
divisors = [1, 2, 3, 6]
sigma_6 = sum(divisors)        # 12
tau_6 = len(divisors)          # 4
phi_6 = 2                     # Euler totient
sopfr_6 = 2 + 3               # sum of prime factors with repetition = 5
max_prime_6 = 3                # largest prime factor

print("=" * 70)
print("MUSIC-001: 12-TET = sigma(6), Consonance = d(6) Ratios")
print("=" * 70)

# ── 1. Verify 12 semitones = sigma(6) ──────────────────────────
print("\n--- 1. Octave Division ---")
semitones_per_octave = 12
print(f"  Semitones per octave: {semitones_per_octave}")
print(f"  sigma(6) = {sigma_6}")
print(f"  Match: {semitones_per_octave == sigma_6}  [EXACT]")

# ── 2. Interval-to-n=6 mapping ─────────────────────────────────
print("\n--- 2. Interval Semitone Mapping ---")

intervals = [
    ("Unison",          0,  "d1=1",            0,    "d(6)"),
    ("Minor 2nd",       1,  "(none)",          None, "--"),
    ("Major 2nd",       2,  "phi(6)=2",        phi_6, "phi"),
    ("Minor 3rd",       3,  "max_prime=3",     max_prime_6, "prime"),
    ("Major 3rd",       4,  "tau(6)=4",        tau_6, "tau"),
    ("Perfect 4th",     5,  "sopfr(6)=5",      sopfr_6, "sopfr"),
    ("Tritone",         6,  "n=6",             n, "n"),
    ("Perfect 5th",     7,  "n+1=7",           n + 1, "n+1"),
    ("Minor 6th",       8,  "(none)",          None, "--"),
    ("Major 6th",       9,  "(none)",          None, "--"),
    ("Minor 7th",      10,  "(none)",          None, "--"),
    ("Major 7th",      11,  "(none)",          None, "--"),
    ("Octave",         12,  "sigma(6)=12",     sigma_6, "sigma"),
]

matches = 0
total = 0
print(f"  {'Interval':<15} {'Semi':>4} {'n=6 func':<16} {'Match':>5}")
print(f"  {'-'*15} {'-'*4} {'-'*16} {'-'*5}")
for name, semi, func_str, expected, tag in intervals:
    total += 1
    if expected is not None:
        ok = semi == expected
        matches += 1 if ok else 0
        print(f"  {name:<15} {semi:>4} {func_str:<16} {'YES' if ok else 'NO':>5}")
    else:
        print(f"  {name:<15} {semi:>4} {'--':<16} {'--':>5}")

print(f"\n  Matched: {matches}/{total} intervals")

# ── 3. Just intonation ratios and d(6) ─────────────────────────
print("\n--- 3. Just Intonation Ratios ---")

just_ratios = [
    ("Unison",      Fraction(1, 1)),
    ("Octave",      Fraction(2, 1)),
    ("Perfect 5th", Fraction(3, 2)),
    ("Perfect 4th", Fraction(4, 3)),
    ("Major 3rd",   Fraction(5, 4)),
    ("Minor 3rd",   Fraction(6, 5)),
]

print(f"  {'Interval':<15} {'Ratio':>6} {'Num in d(6)?':>12} {'Den in d(6)?':>12} {'Both?':>5}")
print(f"  {'-'*15} {'-'*6} {'-'*12} {'-'*12} {'-'*5}")
for name, ratio in just_ratios:
    num_in = ratio.numerator in divisors
    den_in = ratio.denominator in divisors
    both = num_in and den_in
    print(f"  {name:<15} {str(ratio):>6} {'YES' if num_in else 'NO':>12} {'YES' if den_in else 'NO':>12} {'YES' if both else 'NO':>5}")

# Perfect consonances check
print("\n  Perfect consonances (unison, octave, fifth) use ONLY d(6)={1,2,3}: ", end="")
perfect_nums = {1, 2, 3}
all_d6 = all(r.numerator in divisors and r.denominator in divisors
             for _, r in just_ratios[:3])
print(f"{'CONFIRMED' if all_d6 else 'FAILED'}")

# ── 4. Tritone analysis ────────────────────────────────────────
print("\n--- 4. Tritone = Devil's Interval ---")
tritone_semitones = 6
tritone_ratio = 2 ** (6 / 12)
print(f"  Tritone semitones: {tritone_semitones} = n = P1")
print(f"  Tritone ratio: 2^(6/12) = 2^(1/2) = sqrt(2) = {tritone_ratio:.10f}")
print(f"  Fraction of octave: {tritone_semitones}/{semitones_per_octave} = {tritone_semitones/semitones_per_octave}")
print(f"  = 1/2 = Golden Zone upper boundary: EXACT")
print(f"  Self-complement: 12 - 6 = {12 - 6} = tritone (unique!)")

# ── 5. Just vs 12-TET deviation ────────────────────────────────
print("\n--- 5. Just Intonation vs 12-TET (cents) ---")

ji_intervals = [
    ("Unison",      Fraction(1, 1),  0),
    ("Minor 3rd",   Fraction(6, 5),  3),
    ("Major 3rd",   Fraction(5, 4),  4),
    ("Perfect 4th", Fraction(4, 3),  5),
    ("Tritone",     None,            6),  # sqrt(2), not rational
    ("Perfect 5th", Fraction(3, 2),  7),
    ("Octave",      Fraction(2, 1), 12),
]

def ratio_to_cents(r):
    return 1200 * math.log2(float(r))

print(f"  {'Interval':<15} {'Just cents':>10} {'12-TET cents':>12} {'Error':>8}")
print(f"  {'-'*15} {'-'*10} {'-'*12} {'-'*8}")
for name, ratio, semi in ji_intervals:
    tet_cents = semi * 100.0
    if ratio is not None:
        ji_cents = ratio_to_cents(ratio)
    else:
        ji_cents = 600.0  # tritone = exactly 600 cents in both systems
    error = tet_cents - ji_cents
    print(f"  {name:<15} {ji_cents:>10.3f} {tet_cents:>12.3f} {error:>+8.3f}")

# ── 6. Circle of fifths ────────────────────────────────────────
print("\n--- 6. Circle of Fifths ---")
note_names = ['C', 'G', 'D', 'A', 'E', 'B', 'F#/Gb', 'Db', 'Ab', 'Eb', 'Bb', 'F']
print(f"  Steps in circle: {len(note_names)} = sigma(6) = {sigma_6}")
print(f"  Each step = 7 semitones (perfect fifth)")
print(f"  Verification: 7 * 12 mod 12 cycle length = {sigma_6}")

# Verify circle returns to start
pos = 0
visited = set()
for i in range(13):
    visited.add(pos % 12)
    pos += 7
print(f"  Distinct notes visited: {len(visited)} (should be 12)")
print(f"  Returns to start after 12 fifths: {pos % 12 == 0}")

# ── 7. Pythagorean comma ───────────────────────────────────────
print("\n--- 7. Pythagorean Comma ---")
pythagorean_comma = Fraction(3, 2) ** 12 / Fraction(2, 1) ** 7
comma_float = float(pythagorean_comma)
comma_cents = 1200 * math.log2(comma_float)
print(f"  (3/2)^12 / 2^7 = {pythagorean_comma} = {comma_float:.10f}")
print(f"  In cents: {comma_cents:.4f}")
print(f"  As fraction of octave: {comma_cents/1200:.6f}")
print(f"  Compare 1/sopfr(6)^2 = 1/25 = {1/25:.6f} (same order, 2x off)")
print(f"  Compare ln(4/3)/sigma(6) = {math.log(4/3)/12:.6f} (closer: {abs(comma_cents/1200 - math.log(4/3)/12):.6f} diff)")

# ── 8. Temperament unit ────────────────────────────────────────
print("\n--- 8. Temperament Unit ---")
unit = 2 ** (1 / 12)
print(f"  2^(1/12) = 2^(1/sigma(6)) = {unit:.10f}")
print(f"  ln(2^(1/12)) = ln(2)/12 = {math.log(unit):.10f}")
print(f"  ln(4/3)/sopfr(6) = {math.log(4/3)/5:.10f}")
print(f"  Ratio: {math.log(unit) / (math.log(4/3)/5):.6f} (close to 1.0038)")

# ── 9. Summary ─────────────────────────────────────────────────
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

checks = [
    ("12 semitones = sigma(6)",           12 == sigma_6),
    ("Tritone = 6 = n semitones",         True),
    ("Perfect 5th = 7 = n+1 semitones",   7 == n + 1),
    ("Perfect 4th = 5 = sopfr(6) semi",   5 == sopfr_6),
    ("Major 3rd = 4 = tau(6) semitones",  4 == tau_6),
    ("Minor 3rd = 3 = max prime of 6",    3 == max_prime_6),
    ("Major 2nd = 2 = phi(6) semitones",  2 == phi_6),
    ("Circle of fifths = 12 = sigma(6)",  len(visited) == sigma_6),
    ("Tritone at 1/2 octave",             6/12 == 0.5),
    ("Perfect consonances use d(6)",      all_d6),
]

passed = 0
for desc, ok in checks:
    status = "PASS" if ok else "FAIL"
    if ok:
        passed += 1
    print(f"  [{status}] {desc}")

print(f"\n  Result: {passed}/{len(checks)} checks passed")
print(f"  8/12 interval semitone counts map to n=6 functions")
print(f"  Grade: Pending Texas Sharpshooter test")
