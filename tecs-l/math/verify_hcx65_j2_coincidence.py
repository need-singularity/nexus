"""
H-CX-65: J_2(6)=24 four-way coincidence theoretical analysis
Verifies that J_2(6) = sigma(6)*phi(6) = 24 = Leech lattice dim = tau(6)! is unique.
"""
import math
from sympy import divisor_sigma, totient, divisors, factorint
from collections import defaultdict

def jordan_j2(n):
    """J_2(n) = n^2 * prod(1 - 1/p^2) for primes p | n"""
    result = n * n
    for p in factorint(n):
        result = result * (p*p - 1) // (p*p)
    return result

def tau(n):
    """Number of divisors"""
    return sum(1 for _ in divisors(n))

def sigma(n):
    """Sum of divisors"""
    return divisor_sigma(n, 1)

def phi(n):
    """Euler's totient"""
    return totient(n)

def factorial(k):
    return math.factorial(k)

print("=" * 70)
print("H-CX-65: J_2(6)=24 Four-Way Coincidence Analysis")
print("=" * 70)

# First verify the n=6 case
n = 6
j2_6 = jordan_j2(6)
sig_phi_6 = sigma(6) * phi(6)
tau_fact_6 = factorial(tau(6))
print(f"\n=== Verification for n=6 ===")
print(f"J_2(6)           = {j2_6}")
print(f"sigma(6)*phi(6)  = {sigma(6)} * {phi(6)} = {sig_phi_6}")
print(f"tau(6)!          = {tau(6)}! = {tau_fact_6}")
print(f"Leech lattice dim = 24")
print(f"All equal to 24? {j2_6 == 24 == sig_phi_6 == tau_fact_6}")

print("\n" + "=" * 70)
print("Searching n=1 to 10000 for coincidences...")
print("=" * 70)

N = 10000

# Precompute all values
j2_vals = {}
sig_phi_vals = {}
tau_fact_vals = {}
tau_vals = {}
sigma_vals = {}
phi_vals = {}

# For factorial check: which values are factorials
factorial_set = {}
k = 0
while True:
    fk = math.factorial(k)
    if fk > N * N * 100:
        break
    factorial_set[fk] = k
    k += 1

print(f"Factorial values up to {max(factorial_set.keys())}: {sorted(factorial_set.items())[:15]}...")

for n in range(1, N+1):
    t = tau(n)
    s = sigma(n)
    p = phi(n)
    j2 = jordan_j2(n)
    tf = math.factorial(t)

    j2_vals[n] = j2
    sig_phi_vals[n] = s * p
    tau_fact_vals[n] = tf
    tau_vals[n] = t
    sigma_vals[n] = s
    phi_vals[n] = p

print("\n--- Check 1: J_2(n) = sigma(n)*phi(n) ---")
eq1_list = [n for n in range(1, N+1) if j2_vals[n] == sig_phi_vals[n]]
print(f"Count: {len(eq1_list)}")
print(f"First 30: {eq1_list[:30]}")
if len(eq1_list) > 30:
    print(f"  ... ({len(eq1_list)} total)")

print("\n--- Check 2: J_2(n) = tau(n)! ---")
eq2_list = [n for n in range(1, N+1) if j2_vals[n] == tau_fact_vals[n]]
print(f"Count: {len(eq2_list)}")
print(f"All: {eq2_list}")
for n in eq2_list:
    print(f"  n={n}: J_2={j2_vals[n]}, tau={tau_vals[n]}, tau!={tau_fact_vals[n]}, sigma={sigma_vals[n]}, phi={phi_vals[n]}")

print("\n--- Check 3: J_2(n) = m! for some m (n, m pairs) ---")
j2_factorial_pairs = []
for n in range(1, N+1):
    j2 = j2_vals[n]
    if j2 in factorial_set:
        m = factorial_set[j2]
        j2_factorial_pairs.append((n, m, j2))
print(f"Count: {len(j2_factorial_pairs)}")
for n, m, v in j2_factorial_pairs[:50]:
    print(f"  n={n}: J_2={v} = {m}!, tau={tau_vals[n]}, sigma={sigma_vals[n]}, phi={phi_vals[n]}")
if len(j2_factorial_pairs) > 50:
    print(f"  ... ({len(j2_factorial_pairs)} total)")

print("\n--- Check 4: sigma(n)*phi(n) = tau(n)! ---")
eq4_list = [n for n in range(1, N+1) if sig_phi_vals[n] == tau_fact_vals[n]]
print(f"Count: {len(eq4_list)}")
print(f"All (n<=10000): {eq4_list}")
for n in eq4_list:
    print(f"  n={n}: sigma*phi={sig_phi_vals[n]}, tau!={tau_fact_vals[n]}, J_2={j2_vals[n]}")

print("\n--- Check 5: Four-way coincidence (J_2 = sigma*phi = tau! = some_constant) ---")
four_way = []
for n in range(1, N+1):
    j2 = j2_vals[n]
    sp = sig_phi_vals[n]
    tf = tau_fact_vals[n]
    if j2 == sp and j2 == tf:
        four_way.append(n)

print(f"n where J_2(n) = sigma(n)*phi(n) = tau(n)! simultaneously:")
print(f"Count: {len(four_way)}")
for n in four_way:
    print(f"  n={n}: value={j2_vals[n]}, tau={tau_vals[n]}, sigma={sigma_vals[n]}, phi={phi_vals[n]}")

print("\n--- Check 6: Coincidence Score (how many of 3 equalities hold) ---")
score_dist = defaultdict(list)
for n in range(1, N+1):
    j2 = j2_vals[n]
    sp = sig_phi_vals[n]
    tf = tau_fact_vals[n]
    score = int(j2 == sp) + int(j2 == tf) + int(sp == tf)
    if score >= 2:
        score_dist[score].append(n)

for score in sorted(score_dist.keys(), reverse=True):
    ns = score_dist[score]
    print(f"  Score={score}: {len(ns)} values — {ns[:20]}")
    if len(ns) > 20:
        print(f"    ... ({len(ns)} total)")

# Also check which n have value=24
print("\n--- Check 7: n where any of the three quantities equals 24 ---")
eq24_j2 = [n for n in range(1, N+1) if j2_vals[n] == 24]
eq24_sp = [n for n in range(1, N+1) if sig_phi_vals[n] == 24]
eq24_tf = [n for n in range(1, N+1) if tau_fact_vals[n] == 24]
print(f"J_2(n)=24:           {eq24_j2[:20]}")
print(f"sigma*phi=24:        {eq24_sp[:20]}")
print(f"tau(n)!=24 (tau=4):  {eq24_tf[:20]}")

print("\n--- Texas Sharpshooter Analysis ---")
# Expected coincidence rate if random
# P(J2 = sp): how many n have this? fraction = len(eq1_list)/N
p1 = len(eq1_list) / N
p2 = len(eq2_list) / N
p4 = len(eq4_list) / N

print(f"P(J_2=sigma*phi): {len(eq1_list)}/{N} = {p1:.6f}")
print(f"P(J_2=tau!):      {len(eq2_list)}/{N} = {p2:.6f}")
print(f"P(sigma*phi=tau!):{len(eq4_list)}/{N} = {p4:.6f}")

# 4-way coincidence with Leech lattice (specific value 24)
p_j2_24 = len(eq24_j2) / N
p_sp_24 = len(eq24_sp) / N
p_tf_24 = len(eq24_tf) / N
# Leech dim = 24 is a single external fact (p=1/1 or effectively 1 specific value)
# The question is: given we're looking at n with J2=24, what's prob all equal?

print(f"\nP(J_2(n)=24):         {len(eq24_j2)}/{N} = {p_j2_24:.6f}")
print(f"P(sigma*phi=24):      {len(eq24_sp)}/{N} = {p_sp_24:.6f}")
print(f"P(tau(n)!=24):        {len(eq24_tf)}/{N} = {p_tf_24:.6f}")

# Expected number of n in [1,10000] with all three = 24
# Assuming independence (approximate):
exp_three_way = N * p_j2_24 * (p_sp_24 / p_j2_24 if p_j2_24 > 0 else 0) * (p_tf_24 / p_j2_24 if p_j2_24 > 0 else 0)
print(f"\nActual n with J2=sigma*phi=tau!=24: {len(four_way)} (should contain n=6)")

# More careful Texas test: search space is n=1..10000, target is "4-way coincidence"
# with a specific value.
import scipy.stats as stats

# Using hypergeometric or Poisson approximation
# If we searched 10000 numbers, and found exactly 1 four-way coincidence at n=6,
# what's the p-value?
#
# Empirical approach: what fraction have J2=sigma*phi?
# Among those, what fraction also have tau! equal?
common12 = set(eq1_list) & set(eq2_list)
print(f"\nIntersection of Check1 and Check2: {sorted(common12)}")

# Four-way coincidence uniqueness
print(f"\n=== CONCLUSION ===")
print(f"n=6 has J_2(6) = sigma(6)*phi(6) = tau(6)! = 24")
print(f"Other n in [1,10000] with J_2=sigma*phi=tau!: {[n for n in four_way if n != 6]}")
if len(four_way) == 1 and four_way[0] == 6:
    print("CONFIRMED: n=6 is the UNIQUE solution in [1,10000]!")
else:
    print(f"NOT unique. Other solutions: {[n for n in four_way if n != 6]}")

# Check whether Leech dim=24 adds extra constraint
print(f"\nNote: Leech lattice dimension = 24 is an external mathematical fact.")
print(f"The triple (J_2, sigma*phi, tau!) all equaling 24 at n=6 is the coincidence.")
print(f"Among all n in [1,10000], only {len(four_way)} value(s) achieve triple equality.")

# Estimate p-value: treating as Poisson(lambda) where lambda = expected count
# if the three quantities were independent uniform in their ranges
# Simple bound: P(triple) ≈ P(J2=sp) * P(J2=tf | J2=sp)
n_j2_sp = len(eq1_list)
n_j2_tf = len(eq2_list)
n_triple = len(four_way)
print(f"\nSimple Poisson estimate:")
print(f"  Expected (if J2=sp and J2=tf independent): {N * p1 * p2:.4f}")
print(f"  Actual: {n_triple}")
# p-value from Poisson
lam = N * p1 * p2
from scipy.stats import poisson
if lam > 0:
    pval = 1 - poisson.cdf(n_triple - 1, lam)
    print(f"  Poisson p-value (>=1 triple): {pval:.6f}")
else:
    print(f"  lambda=0, exact case")

print("\nDone.")
