#!/usr/bin/env python3
"""Verify physics hypotheses H-PH-2, H-PH-15, H-PH-16 numerically."""

import math

# ─── Number theory helpers ───

def sigma(n):
    """Sum of all divisors of n."""
    s = 0
    for i in range(1, int(math.isqrt(n)) + 1):
        if n % i == 0:
            s += i
            if i != n // i:
                s += n // i
    return s

def tau(n):
    """Number of divisors of n."""
    t = 0
    for i in range(1, int(math.isqrt(n)) + 1):
        if n % i == 0:
            t += 1
            if i != n // i:
                t += 1
    return t

def phi(n):
    """Euler totient function."""
    result = n
    p = 2
    temp = n
    while p * p <= temp:
        if temp % p == 0:
            while temp % p == 0:
                temp //= p
            result -= result // p
        p += 1
    if temp > 1:
        result -= result // temp
    return result

def is_mersenne_prime(p):
    """Check if 2^p - 1 is prime (Lucas-Lehmer for p>2, direct for p=2)."""
    if p == 2:
        return True
    m = (1 << p) - 1
    s = 4
    for _ in range(p - 2):
        s = (s * s - 2) % m
    return s == 0

def dim_SO(n):
    """Dimension of SO(n) = n(n-1)/2."""
    return n * (n - 1) // 2

def perfect_number(p):
    """Even perfect number from Mersenne exponent p: 2^(p-1)*(2^p-1)."""
    return (1 << (p - 1)) * ((1 << p) - 1)


# ═══════════════════════════════════════════════════════════════
# H-PH-2: Gauge Group Six
# ═══════════════════════════════════════════════════════════════

print("# H-PH-2: Gauge Group Six — Standard Model from Perfect Number 6")
print()

n = 6
s = sigma(n)
t = tau(n)
p = phi(n)

print(f"## Basic functions for n={n}")
print()
print(f"| Function | Value |")
print(f"|----------|-------|")
print(f"| sigma(6) | {s} |")
print(f"| tau(6)   | {t} |")
print(f"| phi(6)   | {p} |")
print()

# Standard Model dimensions
su3_dim = 8
su2_dim = 3
u1_dim = 1
total_sm = su3_dim + su2_dim + u1_dim

print(f"## Standard Model: SU(3)×SU(2)×U(1)")
print()
print(f"| Gauge Group | Dimension | From sigma(6)={s} |")
print(f"|-------------|-----------|-------------------|")

# Check decomposition
sigma_minus_tau = s - t  # 12 - 4 = 8
sigma_over_tau = s // t  # 12 / 4 = 3
R = (s * p) / (n * t)   # 12*2 / (6*4) = 24/24 = 1

check_su3 = "PASS" if sigma_minus_tau == su3_dim else "FAIL"
check_su2 = "PASS" if sigma_over_tau == su2_dim else "FAIL"
check_u1 = "PASS" if R == u1_dim else "FAIL"
check_total = "PASS" if s == total_sm else "FAIL"

print(f"| SU(3): dim=8  | sigma-tau = {s}-{t} = {sigma_minus_tau} | **{check_su3}** |")
print(f"| SU(2): dim=3  | sigma/tau = {s}/{t} = {sigma_over_tau} | **{check_su2}** |")
print(f"| U(1):  dim=1  | sigma*phi/(n*tau) = {s}*{p}/({n}*{t}) = {R:.4f} | **{check_u1}** |")
print(f"| Total: dim=12 | sigma(6) = {s} | **{check_total}** |")
print()

# Verify three DIFFERENT operations
ops = ["subtraction (sigma-tau)", "division (sigma/tau)", "ratio (sigma*phi/(n*tau))"]
results = [sigma_minus_tau, sigma_over_tau, R]
print(f"## Three different arithmetic operations")
print()
print(f"| Operation | Expression | Result | Gauge Group |")
print(f"|-----------|-----------|--------|-------------|")
for op, res in zip(ops, results):
    print(f"| {op} | — | {res:.0f} | — |")

all_different = len(set([int(r) for r in results])) == 3
print()
print(f"All three results distinct: {all_different} → **{'PASS' if all_different else 'FAIL'}**")
print()

# Check: does this work for other perfect numbers? (generalization test)
print(f"## Generalization test: other perfect numbers")
print()
print(f"| n | sigma(n) | tau(n) | phi(n) | s-t | s/t | s*p/(n*t) |")
print(f"|---|----------|--------|--------|-----|-----|-----------|")
for pk_exp in [2, 3, 5, 7]:
    if is_mersenne_prime(pk_exp):
        pn = perfect_number(pk_exp)
        sn = sigma(pn)
        tn = tau(pn)
        phn = phi(pn)
        st = sn - tn
        sdivt = sn / tn if tn != 0 else float('inf')
        R_n = (sn * phn) / (pn * tn) if (pn * tn) != 0 else float('inf')
        print(f"| {pn} | {sn} | {tn} | {phn} | {st} | {sdivt:.2f} | {R_n:.4f} |")

print()
print(f"**H-PH-2 Summary**: The 8+3+1=12=sigma(6) decomposition via three distinct operations is **{'PASS' if check_su3=='PASS' and check_su2=='PASS' and check_u1=='PASS' and check_total=='PASS' else 'FAIL'}**")
print()


# ═══════════════════════════════════════════════════════════════
# H-PH-15: Anomaly Perfect Theorem
# ═══════════════════════════════════════════════════════════════

print()
print("# H-PH-15: Anomaly Perfect Theorem — dim(SO(2^p)) = P_k")
print()

# Known Mersenne prime exponents (first 8)
mersenne_exponents = [2, 3, 5, 7, 13, 17, 19, 31]

print(f"## Core claim: dim(SO(2^p)) = 2^(p-1)*(2^p-1) = P_k for Mersenne prime p")
print()
print(f"| p | 2^p | P_k = 2^(p-1)*(2^p-1) | dim(SO(2^p)) = 2^p*(2^p-1)/2 | Match? |")
print(f"|---|-----|------------------------|-------------------------------|--------|")

all_match = True
for p in mersenne_exponents:
    two_p = 1 << p
    Pk = perfect_number(p)
    dim_so = dim_SO(two_p)
    match = Pk == dim_so
    if not match:
        all_match = False
    # For large numbers, format with commas
    print(f"| {p} | {two_p:,} | {Pk:,} | {dim_so:,} | **{'PASS' if match else 'FAIL'}** |")

print()

# Algebraic proof
print(f"## Algebraic verification")
print()
print(f"```")
print(f"P_k         = 2^(p-1) * (2^p - 1)")
print(f"dim(SO(2^p)) = 2^p * (2^p - 1) / 2 = 2^(p-1) * (2^p - 1)")
print(f"Therefore: dim(SO(2^p)) = P_k  (algebraic identity, always true)")
print(f"```")
print()

# Special case: anomaly cancellation
print(f"## Anomaly cancellation in D=10 string theory (p=5)")
print()
p5 = 5
P3 = perfect_number(p5)
so32_dim = dim_SO(32)
e8_dim = 248
e8xe8_dim = 2 * e8_dim

print(f"| Gauge Group | Dimension | = P3={P3}? |")
print(f"|-------------|-----------|------------|")
print(f"| SO(32)      | {so32_dim} | **{'PASS' if so32_dim == P3 else 'FAIL'}** |")
print(f"| E8 x E8     | {e8_dim}+{e8_dim}={e8xe8_dim} | **{'PASS' if e8xe8_dim == P3 else 'FAIL'}** |")
print()

# Verify dim(E8)=248
# E8 has rank 8, dim = 248
print(f"dim(E8) = 248: This is the dimension of the exceptional Lie algebra E8")
print(f"248 + 248 = {e8xe8_dim} = P3 = {P3}: **{'PASS' if e8xe8_dim == P3 else 'FAIL'}**")
print()

# Check smaller cases
print(f"## Perfect number ↔ SO correspondence for small p")
print()
print(f"| p | Perfect P_k | SO(2^p) | dim | Physical meaning |")
print(f"|---|------------|---------|-----|-----------------|")
print(f"| 2 | P1={perfect_number(2)} | SO(4) | {dim_SO(4)} | Lorentz group SO(3,1) |")
print(f"| 3 | P2={perfect_number(3)} | SO(8) | {dim_SO(8)} | Triality, D=8 critical |")
print(f"| 5 | P3={perfect_number(5)} | SO(32) | {dim_SO(32)} | String anomaly cancellation |")
print(f"| 7 | P4={perfect_number(7)} | SO(128) | {dim_SO(128)} | {perfect_number(7)} |")
print()

print(f"**H-PH-15 Summary**: dim(SO(2^p)) = P_k is an algebraic identity → **{'PASS' if all_match else 'FAIL'}** (verified for p={mersenne_exponents})")
print()


# ═══════════════════════════════════════════════════════════════
# H-PH-16: Self-Reference Cycle  6 → 12 → 28 → 6
# ═══════════════════════════════════════════════════════════════

print()
print("# H-PH-16: Self-Reference Cycle — sigma→sigma→tau returns to 6")
print()

# Verify the specific cycle
s6 = sigma(6)
s12 = sigma(s6)
t28 = tau(s12)

print(f"## The cycle")
print()
print(f"| Step | Function | Input | Output |")
print(f"|------|----------|-------|--------|")
print(f"| 1 | sigma | 6 | {s6} |")
print(f"| 2 | sigma | {s6} | {s12} |")
print(f"| 3 | tau | {s12} | {t28} |")
print()
cycle_works = (t28 == 6)
print(f"Cycle 6 → {s6} → {s12} → {t28}: **{'PASS' if cycle_works else 'FAIL'}**")
print()

# Note: 12 and 28 are special
print(f"## Significance of intermediate values")
print()
print(f"| Value | Property |")
print(f"|-------|----------|")
print(f"| 6  | P1 (1st perfect number) |")
print(f"| 12 | sigma(6) = 2×6 (perfect number property) |")
print(f"| 28 | P2 (2nd perfect number), sigma(12)={sigma(12)} |")
print(f"| tau(28) = {tau(28)} | Returns to P1 |")
print()

# Exhaustive search: uniqueness up to 10000
print(f"## Exhaustive search: n where tau(sigma(sigma(n))) = n, for n=1..10000")
print()

solutions = []
for n in range(1, 10001):
    s1 = sigma(n)
    s2 = sigma(s1)
    t3 = tau(s2)
    if t3 == n:
        solutions.append((n, s1, s2, t3))

print(f"| n | sigma(n) | sigma(sigma(n)) | tau(sigma(sigma(n))) | = n? |")
print(f"|---|----------|-----------------|---------------------|------|")
for (n, s1, s2, t3) in solutions:
    print(f"| {n} | {s1} | {s2} | {t3} | **PASS** |")

print()
print(f"Total solutions found in [1, 10000]: **{len(solutions)}**")

unique_6 = (len(solutions) == 1 and solutions[0][0] == 6)
print(f"6 is the ONLY solution: **{'PASS' if unique_6 else 'FAIL'}**")
print()

# Also check: what about near-misses?
print(f"## Near-misses: |tau(sigma(sigma(n))) - n| <= 2, n=1..10000")
print()
near_misses = []
for n in range(1, 10001):
    s1 = sigma(n)
    s2 = sigma(s1)
    t3 = tau(s2)
    if abs(t3 - n) <= 2 and t3 != n:
        near_misses.append((n, s1, s2, t3, t3 - n))

print(f"| n | sigma(n) | sigma(sigma(n)) | tau(sigma(sigma(n))) | Difference |")
print(f"|---|----------|-----------------|---------------------|------------|")
for (n, s1, s2, t3, diff) in near_misses[:20]:  # show up to 20
    print(f"| {n} | {s1} | {s2} | {t3} | {diff:+d} |")
if len(near_misses) > 20:
    print(f"| ... | ... | ... | ... | ({len(near_misses)} total) |")
print()
print(f"Near-misses found: {len(near_misses)}")
print()


# ═══════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════

print()
print("# ═══ FINAL SUMMARY ═══")
print()
print(f"| Hypothesis | Claim | Verdict |")
print(f"|------------|-------|---------|")

hph2_pass = (check_su3=='PASS' and check_su2=='PASS' and check_u1=='PASS' and check_total=='PASS')
print(f"| H-PH-2  | sigma(6)=12=8+3+1 via three operations | **{'PASS' if hph2_pass else 'FAIL'}** |")
print(f"| H-PH-15 | dim(SO(2^p))=P_k (algebraic identity) | **{'PASS' if all_match else 'FAIL'}** |")
print(f"| H-PH-16 | 6→12→28→6 unique in [1,10000] | **{'PASS' if unique_6 else 'FAIL'}** |")
