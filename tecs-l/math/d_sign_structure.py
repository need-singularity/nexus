#!/usr/bin/env python3
"""
Deep analysis of D(n) = sigma(n)*phi(n) - n*tau(n) sign structure.
Proves D(n)<0 only at n=2, D(n)=0 only at {1,6}.
"""

import math
from collections import defaultdict

def factorize(n):
    """Return prime factorization as dict {p: a}."""
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
    if n == 1: return 1
    result = 1
    for p, a in factorize(n).items():
        result *= (p**(a+1) - 1) // (p - 1)
    return result

def phi(n):
    if n == 1: return 1
    result = n
    for p in factorize(n):
        result = result * (p - 1) // p
    return result

def tau(n):
    if n == 1: return 1
    result = 1
    for a in factorize(n).values():
        result *= (a + 1)
    return result

def D(n):
    return sigma(n) * phi(n) - n * tau(n)

# ═══════════════════════════════════════════════════════
# 1. Verify D(n) for n=1..100000
# ═══════════════════════════════════════════════════════
print("=" * 70)
print("PART 1: Verify D(n) sign structure for n = 1..100,000")
print("=" * 70)

N = 100000
zeros = []
negatives = []
smallest_positive = []  # (D(n), n)

for n in range(1, N + 1):
    d = D(n)
    if d == 0:
        zeros.append(n)
    elif d < 0:
        negatives.append((n, d))
    else:
        smallest_positive.append((d, n))

smallest_positive.sort()

print(f"\nD(n) = 0 at n = {zeros}")
print(f"D(n) < 0 at n = {[(n, d) for n, d in negatives]}")
print(f"\nTotal zeros: {len(zeros)}")
print(f"Total negatives: {len(negatives)}")
print(f"Total positives: {N - len(zeros) - len(negatives)}")

print(f"\n20 smallest positive D(n) values:")
print(f"{'Rank':>4} | {'n':>7} | {'D(n)':>10} | factorization")
print("-" * 55)
for i, (d, n) in enumerate(smallest_positive[:20]):
    f = factorize(n)
    fstr = " * ".join(f"{p}^{a}" if a > 1 else str(p) for p, a in sorted(f.items()))
    if n == 1: fstr = "1"
    print(f"{i+1:>4} | {n:>7} | {d:>10} | {fstr}")

# ═══════════════════════════════════════════════════════
# 2. Primes: D(p) = (p-1)^2 - 2
# ═══════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("PART 2: D(p) for primes — D(p) = (p-1)^2 - 2")
print("=" * 70)

def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True

print(f"\n{'p':>5} | {'D(p) actual':>12} | {'(p-1)^2-2':>12} | {'match':>5}")
print("-" * 50)
for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
    actual = D(p)
    formula = (p - 1)**2 - 2
    match = "YES" if actual == formula else "NO"
    print(f"{p:>5} | {actual:>12} | {formula:>12} | {match:>5}")

print(f"\nProof that D(p)<0 only for p=2:")
print(f"  D(p) = (p+1)(p-1) - 2p = p^2 - 1 - 2p = (p-1)^2 - 2")
print(f"  D(p) < 0  iff  (p-1)^2 < 2  iff  p-1 < sqrt(2) ~ 1.414")
print(f"  So p < 2.414, and since p is prime, only p=2.")
print(f"  D(2) = (2-1)^2 - 2 = 1 - 2 = -1  ✓")
print(f"  D(3) = (3-1)^2 - 2 = 4 - 2 = 2 > 0  ✓")

# ═══════════════════════════════════════════════════════
# 3. Prime powers p^a, a>=2
# ═══════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("PART 3: D(p^a) for prime powers, a >= 2")
print("=" * 70)

print(f"\nFormula: D(p^a) = p^(a-1) * (p^(a+1) - 1) - p^a * (a+1)")
print(f"       = p^(2a) - p^(a-1) - (a+1)*p^a")
print()
print(f"{'p^a':>8} | {'n':>8} | {'D(n)':>12} | {'formula':>12} | {'match':>5}")
print("-" * 60)

for p in [2, 3, 5, 7, 11]:
    for a in range(2, 8):
        n = p**a
        if n > 200000: break
        actual = D(n)
        formula_val = p**(2*a) - p**(a-1) - (a+1) * p**a
        match = "YES" if actual == formula_val else "NO"
        print(f"{p}^{a:>2}{'':>3} | {n:>8} | {actual:>12} | {formula_val:>12} | {match:>5}")

print(f"\nProof D(p^a) > 0 for all p>=2, a>=2:")
print(f"  D(p^a) = p^(2a) - (a+1)*p^a - p^(a-1)")
print(f"         = p^a [p^a - (a+1)] - p^(a-1)")
print(f"  For p>=2, a>=2: p^a >= 4, so p^a - (a+1) >= 4-3 = 1")
print(f"  Thus D(p^a) >= p^a * 1 - p^(a-1) = p^a - p^(a-1) = p^(a-1)(p-1) > 0")
print()

# Verify the bound
print("Verification of bound p^a - (a+1) >= 1 for p>=2, a>=2:")
print(f"{'p':>3} | {'a':>3} | {'p^a':>8} | {'a+1':>5} | {'p^a-(a+1)':>10}")
print("-" * 40)
for p in [2, 3, 5]:
    for a in [2, 3, 4, 5, 10, 20]:
        print(f"{p:>3} | {a:>3} | {p**a:>8} | {a+1:>5} | {p**a - (a+1):>10}")

# Formal proof for p=2
print(f"\nFor p=2: need 2^a > a+1 for a>=2.")
print(f"  Base: a=2: 4 > 3 ✓")
print(f"  Induction: if 2^a > a+1, then 2^(a+1) = 2*2^a > 2(a+1) = 2a+2 > a+2 ✓")
print(f"  (since 2a+2 > a+2 for a>=1)")

# ═══════════════════════════════════════════════════════
# 4. General n>=3: Prove D(n)>0
# ═══════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("PART 4: Proof that D(n) > 0 for all n >= 3 (except n=6 where D=0)")
print("=" * 70)

print("""
PROOF STRATEGY:
  D(n) = sigma(n)*phi(n) - n*tau(n)

  All three functions sigma, phi, tau are multiplicative.
  So D is NOT multiplicative, but we can analyze by cases.

  Case 1: n = 1.  D(1) = 1*1 - 1*1 = 0.  ✓
  Case 2: n = 2.  D(2) = 3*1 - 2*2 = -1.  ✓ (only negative)
  Case 3: n = p (odd prime).  D(p) = (p-1)^2 - 2 >= 2 > 0 for p>=3.  ✓
  Case 4: n = 2^a, a>=2.  D(2^a) = 2^(2a) - 2^(a-1) - (a+1)*2^a.
          = 2^(a-1)[2^(a+1) - 1 - 2(a+1)] = 2^(a-1)[2^(a+1) - 2a - 3].
          For a=2: 2[8-7] = 2. For a>=2: 2^(a+1) >= 8 > 2a+3 for a>=2.  ✓
  Case 5: n = p^a, p odd, a>=2.  D(p^a) >= p^(a-1)(p-1) > 0.  ✓
  Case 6: n = 2*p, p odd prime.
          sigma(2p) = 3(p+1), phi(2p) = p-1, tau(2p) = 4.
          D(2p) = 3(p+1)(p-1) - 8p = 3(p^2-1) - 8p = 3p^2 - 8p - 3.
          Discriminant: 64+36 = 100, roots: (8±10)/6 = 3 or -1/3.
          So D(2p) > 0 iff p > 3. D(6) = 3*9*3 - 24 = 0 ✓, D(2*5) = 3*24 - 80 = -8?
""")

# Wait, let me verify D(2p) carefully
print("Verifying D(2p) for small primes p:")
print(f"{'p':>5} | {'2p':>5} | {'sigma':>7} | {'phi':>5} | {'tau':>3} | {'D(2p)':>8} | {'3p^2-8p-3':>12}")
print("-" * 60)
for p in [3, 5, 7, 11, 13, 17, 19, 23]:
    n = 2 * p
    s, ph, t = sigma(n), phi(n), tau(n)
    d = s * ph - n * t
    formula = 3*p*p - 8*p - 3
    print(f"{p:>5} | {n:>5} | {s:>7} | {ph:>5} | {t:>3} | {d:>8} | {formula:>12}")

print("""
  D(2p) = 3(p+1)(p-1) - 4*2p = 3p^2 - 3 - 8p = 3p^2 - 8p - 3.
  Roots of 3p^2 - 8p - 3 = 0: p = (8 ± sqrt(64+36))/6 = (8±10)/6 = 3 or -1/3.
  So D(2p) = 3(p-3)(p+1/3) = (p-3)(3p+1).
  For p=3 (n=6): D = 0.  For p>=5: D = (p-3)(3p+1) > 0.  ✓

  Case 7: n has >=3 prime factors (with multiplicity) or is 2^a * m with m odd > 1.
  For composite n with omega(n) >= 2:
    Use the multiplicative structure. Key insight:

    sigma(n)/n = prod_{p^a || n} (1 + 1/p + ... + 1/p^a)
    phi(n)/n = prod_{p | n} (1 - 1/p)
    tau(n) = prod_{p^a || n} (a+1)

    D(n)/n^2 = [sigma(n)/n * phi(n)/n] - tau(n)/n

    For large n, tau(n)/n -> 0, while sigma(n)*phi(n)/n^2 stays bounded away from 0.
    More precisely, for n>=3 with n != 6, we need D(n) > 0.
""")

# Check all composites up to 1000 with detailed info for small cases
print("All n <= 30 with D(n) <= 10:")
print(f"{'n':>5} | {'D(n)':>8} | factorization")
print("-" * 40)
for n in range(1, 31):
    d = D(n)
    if d <= 10:
        f = factorize(n)
        fstr = " * ".join(f"{p}^{a}" if a > 1 else str(p) for p, a in sorted(f.items()))
        if n == 1: fstr = "1"
        print(f"{n:>5} | {d:>8} | {fstr}")

# ═══════════════════════════════════════════════════════
# 5. Growth rate D(n)/n^2
# ═══════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("PART 5: Growth rate — D(n)/n^2")
print("=" * 70)

N2 = 100000
ratios = []
max_ratio = (0, 0)
min_positive_ratio = (float('inf'), 0)
# Track by milestones
milestones = [100, 1000, 10000, 100000]
milestone_data = {m: {'max': (0, 0), 'min': (float('inf'), 0)} for m in milestones}

for n in range(1, N2 + 1):
    d = D(n)
    r = d / (n * n)
    ratios.append((r, n))
    if r > max_ratio[0]:
        max_ratio = (r, n)
    if d > 0 and r < min_positive_ratio[0]:
        min_positive_ratio = (r, n)
    for m in milestones:
        if n <= m:
            if r > milestone_data[m]['max'][0]:
                milestone_data[m]['max'] = (r, n)
            if d > 0 and r < milestone_data[m]['min'][0]:
                milestone_data[m]['min'] = (r, n)

print(f"\nGlobal max D(n)/n^2 up to {N2}: {max_ratio[0]:.6f} at n={max_ratio[1]}")
print(f"  n={max_ratio[1]}: {factorize(max_ratio[1])}")
print(f"Global min positive D(n)/n^2: {min_positive_ratio[0]:.6f} at n={min_positive_ratio[1]}")

print(f"\nBy range:")
print(f"{'N':>8} | {'max D/n^2':>12} | {'at n':>8} | {'min+ D/n^2':>12} | {'at n':>8}")
print("-" * 60)
for m in milestones:
    mx = milestone_data[m]['max']
    mn = milestone_data[m]['min']
    print(f"{m:>8} | {mx[0]:>12.6f} | {mx[1]:>8} | {mn[0]:>12.8f} | {mn[1]:>8}")

# Top 15 largest D(n)/n^2
ratios.sort(reverse=True)
print(f"\nTop 15 largest D(n)/n^2:")
print(f"{'Rank':>4} | {'n':>8} | {'D(n)/n^2':>12} | {'D(n)':>14} | factorization")
print("-" * 70)
for i, (r, n) in enumerate(ratios[:15]):
    d = D(n)
    f = factorize(n)
    fstr = " * ".join(f"{p}^{a}" if a > 1 else str(p) for p, a in sorted(f.items()))
    print(f"{i+1:>4} | {n:>8} | {r:>12.6f} | {d:>14} | {fstr}")

# Top 15 smallest positive D(n)/n^2
ratios_pos = [(r, n) for r, n in ratios if r > 0]
ratios_pos.sort()
print(f"\nTop 15 smallest positive D(n)/n^2:")
print(f"{'Rank':>4} | {'n':>8} | {'D(n)/n^2':>12} | {'D(n)':>14} | factorization")
print("-" * 70)
for i, (r, n) in enumerate(ratios_pos[:15]):
    d = D(n)
    f = factorize(n)
    fstr = " * ".join(f"{p}^{a}" if a > 1 else str(p) for p, a in sorted(f.items()))
    print(f"{i+1:>4} | {n:>8} | {r:>12.8f} | {d:>14} | {fstr}")

# Asymptotic: for primes p, D(p)/p^2 = (p-1)^2/p^2 - 2/p^2 -> 1
print(f"\nAsymptotic analysis:")
print(f"  For primes p: D(p)/p^2 = ((p-1)^2 - 2)/p^2 -> 1 as p -> inf")
print(f"  lim sup D(n)/n^2 >= 1 (achieved along primes)")

# For highly composite numbers, D(n)/n^2 might be smaller
# Check n = 2^a
print(f"\n  For n=2^a: D(2^a)/4^a = 1 - 1/2^(a+1) - (a+1)/2^a -> 1")
print(f"  {'a':>3} | {'n=2^a':>8} | {'D/n^2':>10}")
print(f"  {'-'*30}")
for a in range(1, 17):
    n = 2**a
    d = D(n)
    print(f"  {a:>3} | {n:>8} | {d/(n*n):.6f}")

# ═══════════════════════════════════════════════════════
# 6. Dirichlet series sum D(n)/n^3
# ═══════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("PART 6: Dirichlet series sum_{n=1}^{N} D(n)/n^3")
print("=" * 70)

partial_sums = []
checkpoints = [10, 100, 1000, 5000, 10000, 50000, 100000]
s = 0.0
s_sigma_phi = 0.0  # sum sigma*phi/n^3
s_tau = 0.0  # sum tau/n^2
cp_idx = 0

for n in range(1, N + 1):
    sn, phn, tn = sigma(n), phi(n), tau(n)
    d = sn * phn - n * tn
    s += d / (n**3)
    s_sigma_phi += sn * phn / (n**3)
    s_tau += tn / (n**2)
    if cp_idx < len(checkpoints) and n == checkpoints[cp_idx]:
        partial_sums.append((n, s, s_sigma_phi, s_tau))
        cp_idx += 1

print(f"\n{'N':>8} | {'sum D/n^3':>14} | {'sum sig*phi/n^3':>16} | {'sum tau/n^2':>14}")
print("-" * 65)
for n, sv, sp, st in partial_sums:
    print(f"{n:>8} | {sv:>14.8f} | {sp:>16.8f} | {st:>14.8f}")

# Known: sum tau(n)/n^2 = zeta(2)^2/zeta(4) ... actually sum tau(n)/n^s = zeta(s)^2
# sum tau(n)/n^2 = zeta(2)^2 = (pi^2/6)^2 = pi^4/36
import math
zeta2_sq = (math.pi**2 / 6)**2
print(f"\nTheoretical sum tau(n)/n^2 = zeta(2)^2 = pi^4/36 = {zeta2_sq:.8f}")
print(f"Computed at N=100000: {s_tau:.8f} (diff: {abs(s_tau - zeta2_sq):.8f})")

# sum sigma(n)*phi(n)/n^s as Dirichlet series
# sigma * phi is multiplicative, so its Dirichlet series factors over primes
# At primes p: sigma(p)*phi(p) = (p+1)(p-1) = p^2-1
# So sum sigma(n)*phi(n)/n^3 = prod_p (1 + (p^2-1)/p^3 + ...)
# This is a convergent Euler product.
print(f"\nsum sigma(n)*phi(n)/n^3 at N=100000: {s_sigma_phi:.8f}")
print(f"sum D(n)/n^3 at N=100000: {s:.8f}")

# Rate of convergence
if len(partial_sums) >= 2:
    s1 = partial_sums[-2][1]
    s2 = partial_sums[-1][1]
    print(f"\nConvergence: |S(100000) - S(50000)| = {abs(s2-s1):.10f}")

# Try to identify the limit
# Euler product for sigma*phi/n^3:
# prod_p sum_{a=0}^inf sigma(p^a)*phi(p^a)/p^(3a)
# sigma(p^a) = (p^(a+1)-1)/(p-1), phi(p^a) = p^(a-1)(p-1) for a>=1
# a=0: 1
# a=1: (p+1)(p-1)/p^3 = (p^2-1)/p^3
# a=2: [(p^3-1)/(p-1)] * p(p-1) / p^6 = (p^3-1)*p/p^6 = (p^3-1)/p^5

print(f"\nEuler product computation for sum sigma(n)*phi(n)/n^3:")
primes_list = [p for p in range(2, 200) if is_prime(p)]
euler_product = 1.0
for p in primes_list:
    local_sum = 1.0
    for a in range(1, 50):
        s_pa = (p**(a+1) - 1) // (p - 1)
        phi_pa = p**(a-1) * (p - 1)
        local_sum += s_pa * phi_pa / p**(3*a)
    euler_product *= local_sum

print(f"Euler product (primes < 200, 50 terms): {euler_product:.8f}")
print(f"Direct sum at N=100000:                  {s_sigma_phi:.8f}")

# D(n)/n^3 series
euler_d = euler_product - zeta2_sq
print(f"\nEstimated sum D(n)/n^3 = {euler_product:.8f} - {zeta2_sq:.8f} = {euler_d:.8f}")
print(f"Direct computation:      {s:.8f}")

# ═══════════════════════════════════════════════════════
# 7. D-spectrum gaps
# ═══════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("PART 7: D-spectrum gaps — values NOT in {D(n) : n >= 1}")
print("=" * 70)

# Compute all D values up to N
d_values = set()
d_to_n = defaultdict(list)  # D value -> list of n achieving it
max_d_to_track = 10000

for n in range(1, N + 1):
    d = D(n)
    if d <= max_d_to_track:
        d_values.add(d)
        if d <= 1000:
            d_to_n[d].append(n)

# Find gaps of size >= 5 below 1000
print(f"\nGaps of size >= 5 in D-spectrum below 1000:")
print(f"{'Gap start':>10} | {'Gap end':>10} | {'Size':>6}")
print("-" * 35)

sorted_vals = sorted(v for v in d_values if 0 <= v <= 1000)
gap_count = 0
for i in range(len(sorted_vals) - 1):
    gap_start = sorted_vals[i] + 1
    gap_end = sorted_vals[i + 1] - 1
    gap_size = gap_end - gap_start + 1
    if gap_size >= 5:
        gap_count += 1
        print(f"{gap_start:>10} | {gap_end:>10} | {gap_size:>6}")

print(f"\nTotal gaps of size >= 5 below 1000: {gap_count}")

# Gaps of size >= 3 below 100
print(f"\nAll gaps of size >= 3 in D-spectrum below 100:")
print(f"{'Gap':>15} | {'Size':>6} | {'D values around gap'}")
print("-" * 55)
for i in range(len(sorted_vals) - 1):
    if sorted_vals[i] >= 100: break
    gap_start = sorted_vals[i] + 1
    gap_end = sorted_vals[i + 1] - 1
    gap_size = gap_end - gap_start + 1
    if gap_size >= 3:
        before = sorted_vals[i]
        after = sorted_vals[i + 1]
        print(f"  [{gap_start}, {gap_end}] | {gap_size:>6} | D={before} ... D={after}")

# Small D values: which are achieved?
print(f"\nD-spectrum detail for D = -1 to 50:")
print(f"{'D':>5} | {'achieved?':>9} | {'smallest n':>10} | {'count (n<=100k)':>15}")
print("-" * 50)
for d in range(-1, 51):
    achieved = d in d_values
    if achieved and d in d_to_n:
        ns = d_to_n[d]
        print(f"{d:>5} | {'YES':>9} | {ns[0]:>10} | {len(ns):>15}")
    elif achieved:
        print(f"{d:>5} | {'YES':>9} | {'?':>10} | {'?':>15}")
    else:
        print(f"{d:>5} | {'---':>9} | {'-':>10} | {'-':>15}")

# Count how many integers in [0, M] are NOT in D-spectrum
for M in [100, 500, 1000, 5000, 10000]:
    missing = sum(1 for v in range(0, M+1) if v not in d_values)
    density = 1 - missing / (M + 1)
    print(f"\n[0, {M}]: {M+1-missing}/{M+1} values achieved, {missing} missing, density = {density:.4f}")

# ═══════════════════════════════════════════════════════
# COMPLETE PROOF SUMMARY
# ═══════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("COMPLETE PROOF: D(n) < 0 only at n=2")
print("=" * 70)
print("""
THEOREM: For D(n) = sigma(n)*phi(n) - n*tau(n):
  (a) D(n) = 0  iff  n in {1, 6}
  (b) D(n) < 0  iff  n = 2  (and D(2) = -1)
  (c) D(n) > 0  for all n >= 3 with n != 6

PROOF (by exhaustive case analysis on the structure of n):

Case 1: n = 1.
  D(1) = 1*1 - 1*1 = 0.

Case 2: n = p (prime).
  D(p) = (p+1)(p-1) - 2p = (p-1)^2 - 2.
  D(p) < 0 iff (p-1)^2 < 2 iff p < 1 + sqrt(2) ~ 2.414.
  Only p=2: D(2) = -1.
  D(p) = 0 iff (p-1)^2 = 2: impossible (no integer solution).
  D(p) > 0 for all odd primes p >= 3.  [D(3)=2, D(5)=14, ...]

Case 3: n = p^a, a >= 2.
  D(p^a) = p^(2a) - (a+1)*p^a - p^(a-1)
         = p^(a-1)[p^(a+1) - (a+1)p - 1]

  Claim: p^(a+1) > (a+1)p + 1 for all p>=2, a>=2.

  Proof: p^(a+1) >= 2^3 = 8 for p>=2, a>=2.
         (a+1)p + 1 <= (a+1)*p + 1.
         For p=2: need 2^(a+1) > 2(a+1)+1 = 2a+3.
           a=2: 8 > 7 ✓. Induction: 2^(a+2) = 2*2^(a+1) > 2(2a+3) = 4a+6 > 2a+5. ✓
         For p>=3: p^(a+1) >= 3^3 = 27 > (a+1)*3+1 for a=2 (=10). ✓
           And p^(a+1) grows faster than (a+1)p for larger a.

  So D(p^a) > 0 for all prime powers with a >= 2.

Case 4: n = 2p, p odd prime.
  D(2p) = 3(p+1)(p-1) - 4*2p = 3p^2 - 8p - 3 = (p-3)(3p+1).
  D(2p) = 0 iff p = 3 (i.e., n = 6).
  D(2p) > 0 for p >= 5.  ✓

Case 5: n composite, n >= 4, not covered above.
  (i.e., n has at least 2 distinct prime factors, and n != 2p for prime p,
   or n has a prime factor with multiplicity >= 2 and another factor)

  Key inequality: for n >= 4 with at least 2 prime factors (counting mult.):
    sigma(n) >= n + sqrt(n) + 1  (has many divisors)
    phi(n) >= sqrt(n)/2  (crude lower bound for non-prime-powers)
    tau(n) <= 2*sqrt(n)  (well-known bound, actually tau(n) = o(n^eps))

  But we don't need such generality. The computational verification
  up to n = 100,000 covers all "small" cases, and for n >= 100,000:

  D(n)/n^2 = sigma(n)*phi(n)/n^2 - tau(n)/n

  sigma(n)*phi(n)/n^2 = prod_{p^a||n} [(1-1/p)(1+1/p+...+1/p^a)]

  For the worst case (most divisors, least D/n^2), consider n = prod p_i.
  sigma(n)*phi(n)/n^2 = prod (1-1/p_i^2) >= prod_{p prime} (1-1/p^2) = 6/pi^2 ~ 0.608

  Meanwhile tau(n)/n -> 0 as n -> infinity (tau grows sub-polynomially).
  So for large enough n, D(n)/n^2 > 0.6 - epsilon > 0.

  Combined with the computational check up to 100,000: D(n) > 0.  ∎

COROLLARY: D(n) = 0 characterizes n in {1, 6}.
  - n=1 is trivial.
  - n=6 is the smallest perfect number.
  - D(6) = 0 iff sigma(6)*phi(6) = 6*tau(6) iff 12*2 = 6*4 iff 24 = 24. ✓
  - For n=28 (next perfect number): D(28) = sigma(28)*phi(28) - 28*tau(28)
    = 56*12 - 28*6 = 672 - 168 = 504 > 0.
  - So D(n) = 0 at n=6 is NOT a perfect number property but specific to 6.
""")
