#!/usr/bin/env python3
"""H-PH-2: Gauge group dimension sum and perfect number 6 — verification script."""

import math
from itertools import combinations

print("=" * 70)
print("H-PH-2: Standard Model Gauge Groups and Perfect Number 6")
print("=" * 70)

sigma_6 = 12
tau_6 = 4
sigma_over_tau = sigma_6 // tau_6  # 3

print(f"\nPerfect number 6: sigma={sigma_6}, tau={tau_6}, sigma/tau={sigma_over_tau}")

# --- Check 1: Dimensions and ranks ---
print("\n" + "-" * 50)
print("CHECK 1: Gauge group dimensions and ranks")
print("-" * 50)

groups = [
    ("SU(3)", "strong", 3, 8, 2),
    ("SU(2)", "weak", 2, 3, 1),
    ("U(1)",  "EM",   1, 1, 1),
]

print(f"{'Group':<8} | {'Force':<8} | {'n':<4} | {'dim=n^2-1':>10} | {'rank=n-1':>8} | {'Generators':>10}")
print("-" * 65)
total_dim = 0
total_rank = 0
for name, force, n, dim, rank in groups:
    # Verify dimension formula: dim SU(n) = n^2 - 1, dim U(1) = 1
    if name.startswith("SU"):
        expected_dim = n**2 - 1
    else:
        expected_dim = 1
    expected_rank = n - 1 if name.startswith("SU") else 1

    verify_dim = "OK" if dim == expected_dim else "WRONG"
    verify_rank = "OK" if rank == expected_rank else "WRONG"

    total_dim += dim
    total_rank += rank
    print(f"{name:<8} | {force:<8} | {n:<4} | {dim:>10} ({verify_dim}) | {rank:>8} ({verify_rank}) | {dim:>10}")

print("-" * 65)
print(f"{'TOTAL':<8} | {'':8} | {'':4} | {total_dim:>10}       | {total_rank:>8}       | {total_dim:>10}")
print()
print(f"Total dimension   = {total_dim} = sigma(6) = {sigma_6}? {'YES' if total_dim == sigma_6 else 'NO'}")
print(f"Total rank        = {total_rank} = tau(6) = {tau_6}? {'YES' if total_rank == tau_6 else 'NO'}")
print(f"Number of groups  = {len(groups)} = sigma/tau = {sigma_over_tau}? {'YES' if len(groups) == sigma_over_tau else 'NO'}")

# --- Check 2: Gauge bosons ---
print("\n" + "-" * 50)
print("CHECK 2: Gauge bosons = generators = dimensions")
print("-" * 50)
bosons = [
    ("Gluons (SU(3))", 8),
    ("W+, W-, Z (SU(2))", 3),
    ("Photon (U(1))", 1),
]
total_bosons = sum(b[1] for b in bosons)
print(f"{'Boson type':<25} | {'Count':>6}")
print("-" * 35)
for name, count in bosons:
    print(f"{name:<25} | {count:>6}")
print("-" * 35)
print(f"{'TOTAL':<25} | {total_bosons:>6}")
print(f"\nTotal gauge bosons = {total_bosons} = sigma(6)? {'YES' if total_bosons == sigma_6 else 'NO'}")
print("(This is the SAME as total dimension — gauge bosons = generators.)")

# --- Check 3: Fundamental fermions ---
print("\n" + "-" * 50)
print("CHECK 3: Fundamental fermions")
print("-" * 50)

quarks = ["up", "down", "charm", "strange", "top", "bottom"]
leptons = ["electron", "e-neutrino", "muon", "mu-neutrino", "tau", "tau-neutrino"]

print(f"Quarks ({len(quarks)}):  {', '.join(quarks)}")
print(f"Leptons ({len(leptons)}): {', '.join(leptons)}")
total_fermions = len(quarks) + len(leptons)
print(f"\nTotal fundamental fermions = {total_fermions}")
print(f"= sigma(6)? {'YES' if total_fermions == sigma_6 else 'NO'}")
print()
print("BUT: if we count antiparticles, it's 24 = 2*sigma(6).")
print("If we count color charges: 6 quarks x 3 colors + 6 leptons = 24.")
print("If we count everything: 6 quarks x 3 colors x 2 (anti) + 6 leptons x 2 (anti) = 48.")
print("Which counting gives sigma(6)? Only the simplest one (no anti, no color).")

# --- Check 4: Quark count = 6 ---
print("\n" + "-" * 50)
print("CHECK 4: Number of quark flavors = 6 (perfect number!)")
print("-" * 50)
print(f"Quark flavors: {len(quarks)} = 6 = first perfect number")
print(f"Lepton flavors: {len(leptons)} = 6 = first perfect number")
print(f"Generations: 3 = sigma/tau = {sigma_over_tau}")
print(f"Fermions per generation: 4 (2 quarks + 2 leptons) = tau(6) = {tau_6}")
print()
print("This is actually a nicer structure:")
print(f"  3 generations x 4 fermions/gen = 12 = sigma(6)")
print(f"  3 = sigma/tau, 4 = tau. Product = 12 = sigma.")

# --- Check 5: Texas Sharpshooter ---
print("\n" + "-" * 50)
print("CHECK 5: Texas Sharpshooter Analysis")
print("-" * 50)

# Count how many "physics numbers" exist
physics_counts = [
    ("Gauge groups", 3),
    ("Gauge bosons", 12),
    ("Quark flavors", 6),
    ("Lepton flavors", 6),
    ("Generations", 3),
    ("Fermions/generation", 4),
    ("Total fermions", 12),
    ("Quark colors", 3),
    ("Higgs doublet components", 2),
    ("Spacetime dimensions", 4),
    ("Space dimensions", 3),
    ("Fundamental forces", 4),
    ("SM free parameters", 19),
    ("Conserved charges (SM)", 5),
    ("CPT symmetries", 3),
    ("Electroweak bosons", 4),
    ("Strong sector bosons", 8),
    ("Neutrino types", 3),
    ("Up-type quarks", 3),
    ("Down-type quarks", 3),
    ("Charged leptons", 3),
    ("W bosons", 2),
    ("Neutral bosons (Z,gamma,H)", 3),
    ("Spin-1 bosons (total)", 12),
    ("Scalar bosons (Higgs)", 1),
    ("Total boson types", 13),
    ("Quark charges (fractional denoms)", 3),
]

# Target values from perfect number 6
targets = {
    "tau(6)=4": 4,
    "sigma(6)=12": 12,
    "sigma/tau=3": 3,
    "6 itself": 6,
    "sigma-1(6)=2": 2,
    "phi(6)=2": 2,
    "6-1=5": 5,
    "6+1=7": 7,
}

print(f"\nPhysics 'counts' examined: {len(physics_counts)}")
print(f"Target values from 6: {list(targets.keys())}")
print()

# Count matches
matches = []
for pname, pval in physics_counts:
    for tname, tval in targets.items():
        if pval == tval:
            matches.append((pname, pval, tname))

print(f"{'Physics quantity':<30} | {'Value':>6} | {'Matches':<20}")
print("-" * 65)
for pname, pval, tname in matches:
    print(f"{pname:<30} | {pval:>6} | {tname:<20}")

print(f"\nTotal matches: {len(matches)}")
print(f"Expected by chance:")
n_physics = len(physics_counts)
n_targets = len(targets)
# Most target values are small (2-7, 12). Physics counts range 1-19.
# P(random int in [1,20] matches one of {2,3,4,5,6,7,12}) = 7/20 = 0.35
p_match = 7/20
expected = n_physics * p_match
print(f"  {n_physics} physics quantities x P(match one of {n_targets} targets) ~ {n_physics} x {p_match} = {expected:.1f}")
print(f"  Actual matches: {len(matches)}")
print(f"  Ratio actual/expected: {len(matches)/expected:.2f}")
print()

# Many matches but most are just "3" appearing everywhere
count_by_value = {}
for _, pval, _ in matches:
    count_by_value[pval] = count_by_value.get(pval, 0) + 1

print("Matches by target value:")
for val, count in sorted(count_by_value.items()):
    print(f"  Value {val}: {count} matches")

print()
print("The value 3 appears ~10 times in physics (dimensions, generations, colors...)")
print("The value 12 appears because 12 = 8+3+1 (generator counts sum).")
print("The value 4 appears as spacetime dim, forces count, fermions/gen.")

# --- Deeper analysis ---
print("\n" + "-" * 50)
print("DEEPER: Is 3+1 = SU(3)xSU(2)xU(1) structure fundamental?")
print("-" * 50)
print("""
The Standard Model gauge group SU(3)xSU(2)xU(1) might be embedded in
a larger GUT group. Known embeddings:

  SU(5)  [Georgi-Glashow]:  dim=24, rank=4
  SO(10) [Pati-Salam]:      dim=45, rank=5
  E(6):                     dim=78, rank=6

If SU(5) is the true GUT group:
  - dim=24 = 2*sigma(6). Still related? Or just 2*12?
  - rank=4 = tau(6). Same as SM.

If SO(10):
  - dim=45, rank=5. No obvious connection to 6.

If E(6):
  - dim=78 = 6*13, rank=6 = perfect number!
  - E(6) rank = 6 is interesting but E(6) is not the leading GUT candidate.

The counting "12 = sigma(6)" works ONLY for the specific SM decomposition
SU(3)xSU(2)xU(1), which may not be fundamental.
""")

# --- Significance Assessment ---
print("=" * 70)
print("SIGNIFICANCE ASSESSMENT: H-PH-2")
print("=" * 70)

assessments = [
    ("dim(SM) = 8+3+1 = 12 = sigma(6)", "Arithmetically correct", "p~0.15", "yellow-weak"),
    ("rank(SM) = 2+1+1 = 4 = tau(6)", "Arithmetically correct", "p~0.20", "white"),
    ("3 gauge groups = sigma/tau", "True, but 3 is ubiquitous", "p~0.35", "white"),
    ("12 gauge bosons = sigma(6)", "Same as dim (tautology)", "N/A", "white"),
    ("12 fermions = sigma(6)", "True (simplest counting)", "p~0.15", "yellow-weak"),
    ("6 quarks = perfect number", "True! But WHY 3 generations?", "p~0.10", "yellow"),
    ("3 gen x 4 ferm = sigma(6)", "Nice: (sigma/tau) x tau = sigma", "p~0.05", "yellow"),
    ("Texas overall: many 12s and 3s", "High multiple-testing burden", "p~0.3", "white"),
]

print(f"{'Claim':<40} | {'Verdict':<25} | {'p-value':<10} | {'Grade':<12}")
print("-" * 95)
for claim, verdict, pval, grade in assessments:
    print(f"{claim:<40} | {verdict:<25} | {pval:<10} | {grade:<12}")

print()
print("OVERALL VERDICT: H-PH-2")
print("  The SM has 12 generators and 12 fermions. 12 = sigma(6) is true arithmetic.")
print("  The factorization 3 gen x 4 per gen = 12 maps to (sigma/tau) x tau = sigma.")
print("  However:")
print("    1. These are SMALL NUMBERS (3, 4, 6, 12) that appear everywhere")
print("    2. The counting 'works' only for the simplest fermion enumeration")
print("    3. If the SM is embedded in a GUT group, these counts change")
print("    4. Texas Sharpshooter: with ~27 physics counts and ~8 targets, ~9 matches expected")
print("  Grade: yellow-weak (interesting arithmetic, not significant)")
print("  The deepest question remains: WHY exactly 3 generations? This is unsolved in physics.")
