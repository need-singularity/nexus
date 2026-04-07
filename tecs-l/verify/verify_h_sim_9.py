#!/usr/bin/env python3
"""H-SIM-9: 6 = Optimal Simulation Parameter
Verify: E(n) = sigma(n)*phi(n)/(n*tau(n)), find all n where E(n)=1.
Count physics parameters matching 6 or divisors of 6.
Binomial p-value for physics coincidences.
"""
import math
from fractions import Fraction
from collections import defaultdict

# --- Number theory functions ---

def factorize(n):
    factors = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors

def sigma(n):
    if n <= 0: return 0
    factors = factorize(n)
    result = 1
    for p, a in factors.items():
        result *= (p**(a+1) - 1) // (p - 1)
    return result

def tau(n):
    if n <= 0: return 0
    factors = factorize(n)
    result = 1
    for a in factors.values():
        result *= (a + 1)
    return result

def phi(n):
    if n <= 0: return 0
    result = n
    factors = factorize(n)
    for p in factors:
        result = result * (p - 1) // p
    return result

def E(n):
    """Simulation efficiency: sigma(n)*phi(n) / (n*tau(n))"""
    if n <= 0: return 0
    return Fraction(sigma(n) * phi(n), n * tau(n))

# ============================================================
# PART 1: E(n) = 1 search for n = 1..10000
# ============================================================
print("=" * 70)
print("PART 1: E(n) = sigma(n)*phi(n) / (n*tau(n)) — Search for E(n) = 1")
print("=" * 70)

perfect_balance = []
near_balance = []  # |E-1| < 0.01

for n in range(1, 10001):
    e = E(n)
    if e == 1:
        perfect_balance.append(n)
    elif abs(float(e) - 1.0) < 0.01:
        near_balance.append((n, float(e)))

print(f"\nE(n) = 1 exactly for n in [1, 10000]:")
print(f"  Count: {len(perfect_balance)}")
for n in perfect_balance:
    s, t, p = sigma(n), tau(n), phi(n)
    print(f"  n={n:>5}: sigma={s}, tau={t}, phi={p}, E={s}*{p}/({n}*{t}) = {E(n)}")

print(f"\n|E(n) - 1| < 0.01 (near-balance, first 20):")
for n, e in near_balance[:20]:
    print(f"  n={n:>5}: E = {e:.6f}")

# Show E(n) distribution for n=1..30
print(f"\nE(n) for n = 1..30:")
print(f"  {'n':>4} | {'sigma':>6} | {'phi':>5} | {'tau':>4} | {'E(n)':>10} | {'float':>8} | Bar")
print(f"  {'-'*4}-+-{'-'*6}-+-{'-'*5}-+-{'-'*4}-+-{'-'*10}-+-{'-'*8}-+------")
for n in range(1, 31):
    s, t, p = sigma(n), tau(n), phi(n)
    e = E(n)
    ef = float(e)
    bar = '#' * int(ef * 20)
    marker = ' <-- E=1!' if e == 1 else ''
    print(f"  {n:>4} | {s:>6} | {p:>5} | {t:>4} | {str(e):>10} | {ef:>8.4f} | {bar}{marker}")

# ASCII histogram of E(n) for n=2..1000
print(f"\nASCII Histogram of E(n) for n=2..1000:")
bins = defaultdict(int)
for n in range(2, 1001):
    ef = float(E(n))
    b = round(ef * 10) / 10  # bin to nearest 0.1
    bins[b] += 1

max_count = max(bins.values())
for b in sorted(bins.keys()):
    bar_len = int(bins[b] / max_count * 50)
    marker = " <<<" if abs(b - 1.0) < 0.05 else ""
    print(f"  {b:>4.1f} | {'#' * bar_len} ({bins[b]}){marker}")

# ============================================================
# PART 2: Perfect numbers and E(n)
# ============================================================
print("\n" + "=" * 70)
print("PART 2: Perfect numbers and E(n)")
print("=" * 70)

perfect_nums = [6, 28, 496, 8128]
for pn in perfect_nums:
    e = E(pn)
    s, t, p = sigma(pn), tau(pn), phi(pn)
    print(f"  n={pn:>5}: sigma={s}, tau={t}, phi={p}, E = {e} = {float(e):.6f}")

# ============================================================
# PART 3: Physics parameters matching 6 or divisors of 6
# ============================================================
print("\n" + "=" * 70)
print("PART 3: Physics parameters related to 6")
print("=" * 70)

# Comprehensive list of physics parameters
physics_params = [
    # (name, value, relation_to_6, category)
    ("Space dimensions", 3, "divisor of 6 (6/2)", "Spacetime"),
    ("Spacetime dimensions", 4, "tau(6)=4", "Spacetime"),
    ("Quark colors", 3, "divisor of 6 (6/2)", "Gauge"),
    ("Quark flavors", 6, "= 6", "Particles"),
    ("Lepton flavors", 6, "= 6", "Particles"),
    ("Fermion generations", 3, "divisor of 6 (6/2)", "Particles"),
    ("Fundamental forces", 4, "tau(6)=4", "Forces"),
    ("Gauge bosons (W+,W-,Z,gamma,8g)", 12, "sigma(6)=12", "Bosons"),
    ("Gluon types", 8, "not 6-related", "Bosons"),
    ("SM Higgs doublet components", 4, "tau(6)=4", "Higgs"),
    ("Generations x Forces", 12, "sigma(6)=12=3x4", "Cross"),
    ("Standard Model free parameters", 19, "check below", "SM"),
    ("Quark types per generation", 2, "phi(6)=2", "Particles"),
    ("Lepton types per generation", 2, "phi(6)=2", "Particles"),
    ("Up-type quarks", 3, "divisor of 6", "Particles"),
    ("Down-type quarks", 3, "divisor of 6", "Particles"),
    ("Charged leptons", 3, "divisor of 6", "Particles"),
    ("Neutrinos", 3, "divisor of 6", "Particles"),
    ("SU(3) generators", 8, "not 6-related", "Gauge"),
    ("SU(2) generators", 3, "divisor of 6", "Gauge"),
    ("U(1) generators", 1, "divisor of 6", "Gauge"),
]

# Divisors of 6
div6 = {1, 2, 3, 6}
# Number theory values of 6
nt6 = {12, 4, 2}  # sigma, tau, phi

print(f"\n  {'Parameter':<35} | {'Value':>6} | {'6-Related?':>12} | Category")
print(f"  {'-'*35}-+-{'-'*6}-+-{'-'*12}-+---------")

match_count = 0
total_params = len(physics_params)

for name, val, rel, cat in physics_params:
    is_match = (val in div6 or val in nt6 or val == 6 or val == 12)
    if is_match:
        match_count += 1
    mark = "YES" if is_match else "no"
    print(f"  {name:<35} | {val:>6} | {mark:>12} | {cat}")

print(f"\n  Total parameters: {total_params}")
print(f"  Matching 6/divisors/sigma/tau/phi: {match_count}")
print(f"  Match rate: {match_count}/{total_params} = {match_count/total_params:.1%}")

# ============================================================
# PART 4: Binomial p-value
# ============================================================
print("\n" + "=" * 70)
print("PART 4: Statistical significance (Binomial test)")
print("=" * 70)

# Under null: each parameter independently uniform on {1..20}
# P(value in {1,2,3,4,6,12}) = 6/20 = 0.30
# But more conservatively: P(value in div6 ∪ nt6) for values 1-20
target_vals = {1, 2, 3, 4, 6, 12}
p_null = len(target_vals) / 20  # 6/20 = 0.30

print(f"\n  Null hypothesis: each parameter uniform on {{1,...,20}}")
print(f"  Target values: {sorted(target_vals)}")
print(f"  P(match under null) = {len(target_vals)}/20 = {p_null:.2f}")
print(f"  Observed: k={match_count} matches out of n={total_params}")

# Binomial CDF: P(X >= k) where X ~ Binomial(n, p)
from math import comb, factorial
n_params = total_params
k_match = match_count

p_value = 0
for k in range(k_match, n_params + 1):
    p_value += comb(n_params, k) * (p_null ** k) * ((1 - p_null) ** (n_params - k))

expected = n_params * p_null
print(f"  Expected matches: {expected:.1f}")
print(f"  Observed matches: {k_match}")
print(f"  P(X >= {k_match}) = {p_value:.6f}")

if p_value < 0.01:
    print(f"  ** SIGNIFICANT at p < 0.01 **")
elif p_value < 0.05:
    print(f"  * Significant at p < 0.05 *")
else:
    print(f"  Not significant (p > 0.05)")

# More conservative test: only count exact divisors of 6 (1,2,3,6)
# P = 4/20 = 0.20
div_only_matches = sum(1 for _, v, _, _ in physics_params if v in div6)
p_null2 = len(div6) / 20  # 0.20
p_value2 = 0
for k in range(div_only_matches, n_params + 1):
    p_value2 += comb(n_params, k) * (p_null2 ** k) * ((1 - p_null2) ** (n_params - k))

print(f"\n  Conservative test (divisors of 6 only: {{1,2,3,6}}):")
print(f"  P(match) = {p_null2:.2f}")
print(f"  Observed: {div_only_matches}/{n_params}")
print(f"  P(X >= {div_only_matches}) = {p_value2:.6f}")

# ============================================================
# PART 5: Check 19 = Standard Model parameters
# ============================================================
print("\n" + "=" * 70)
print("PART 5: Is 19 special? SM has 19 free parameters")
print("=" * 70)

# Check: 19 = sigma(6) + sigma_{-1}(6)*tau(6) - 1 = 12 + 2*4 - 1 = 19
val_check = sigma(6) + 2 * tau(6) - 1  # sigma_{-1}(6)=2
print(f"  sigma(6) + sigma_{{-1}}(6)*tau(6) - 1 = {sigma(6)} + 2*{tau(6)} - 1 = {val_check}")
print(f"  SM free parameters = 19")
print(f"  Match: {val_check == 19}")

# Also: 19 = prime, 19th prime = 67
# 6+1 = 7, 6*3+1 = 19
print(f"  6*3 + 1 = {6*3+1} (= 19? {6*3+1==19})")
print(f"  NOTE: 19 = sigma(6) + tau(6) + phi(6) + 1 = {sigma(6)}+{tau(6)}+{phi(6)}+1 = {sigma(6)+tau(6)+phi(6)+1}")
print(f"  NOTE: With ad-hoc +1, this is weak evidence (downgrade)")

# ============================================================
# PART 6: Generations x Forces = sigma(6)
# ============================================================
print("\n" + "=" * 70)
print("PART 6: Cross products")
print("=" * 70)

print(f"  Generations x Forces = 3 x 4 = {3*4} = sigma(6) = {sigma(6)}")
print(f"  Quarks x Colors = 6 x 3 = {6*3} = 18 = 3*sigma(6) = {3*sigma(6)}")
print(f"  Leptons + Quarks = 6 + 6 = {6+6} = sigma(6) = {sigma(6)}")
print(f"  (Quarks + Leptons) / Generations = 12/3 = {12//3} = tau(6) = {tau(6)}")

# ============================================================
# PART 7: E(n) for all n where n | 6 or tau(n) = 4
# ============================================================
print("\n" + "=" * 70)
print("PART 7: E(n) for divisors of 6 and related numbers")
print("=" * 70)

special_ns = sorted(set([1,2,3,6,12,28,496,8128] + list(range(1,31))))
print(f"  {'n':>5} | {'sigma':>6} | {'phi':>5} | {'tau':>4} | {'E(n)':>12} | {'E float':>8} | Note")
print(f"  {'-'*5}-+-{'-'*6}-+-{'-'*5}-+-{'-'*4}-+-{'-'*12}-+-{'-'*8}-+------")
for n in [1,2,3,6,12,28,496,8128]:
    s, t, p = sigma(n), tau(n), phi(n)
    e = E(n)
    note = ""
    if e == 1: note = "PERFECT BALANCE"
    elif n in [28, 496, 8128]: note = f"perfect number"
    print(f"  {n:>5} | {s:>6} | {p:>5} | {t:>4} | {str(e):>12} | {float(e):>8.4f} | {note}")

# ============================================================
# PART 8: Uniqueness analysis — what makes E(6)=1 special
# ============================================================
print("\n" + "=" * 70)
print("PART 8: Why only n=1 and n=6 have E(n)=1 in [1,10000]?")
print("=" * 70)

print(f"\n  For E(n)=1: sigma(n)*phi(n) = n*tau(n)")
print(f"  n=1: sigma=1, phi=1, tau=1 → 1*1 = 1*1 ✓ (trivial)")
print(f"  n=6: sigma=12, phi=2, tau=4 → 12*2 = 6*4 = 24 ✓ (non-trivial!)")
print(f"\n  For perfect number n=2^(p-1)(2^p-1):")
print(f"    sigma(n) = 2n (by definition)")
print(f"    So E(n) = 2n*phi(n)/(n*tau(n)) = 2*phi(n)/tau(n)")
print(f"    E(n)=1 requires phi(n)/tau(n) = 1/2")

for pn in perfect_nums:
    p, t = phi(pn), tau(pn)
    print(f"    n={pn}: phi/tau = {p}/{t} = {Fraction(p,t)} {'= 1/2 ✓' if Fraction(p,t) == Fraction(1,2) else '≠ 1/2'}")

print(f"\n  Only n=6 among perfect numbers satisfies phi(n)/tau(n) = 1/2")
print(f"  This is because 6 = 2 * 3 (simplest Mersenne prime structure)")
print(f"  For 28 = 4*7: phi=12, tau=6, phi/tau = 2 ≠ 1/2")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"""
  1. E(n)=1 holds ONLY for n=1 (trivial) and n=6 in [1, 10000]
  2. Among perfect numbers, ONLY 6 gives E=1
  3. {match_count}/{total_params} physics parameters match 6-related values
  4. Binomial p-value = {p_value:.6f}
  5. 19 SM parameters = sigma(6) + sigma_{{-1}}(6)*tau(6) - 1 (has ad-hoc -1)
  6. Generations x Forces = 3 x 4 = 12 = sigma(6) (exact, no adjustment)
""")
