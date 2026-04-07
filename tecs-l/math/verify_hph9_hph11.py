#!/usr/bin/env python3
"""
Numerical verification of H-PH-9 (Perfect Number String Unification)
and H-PH-11 (Partition M-theory) claims.
All number theory functions implemented from scratch (no sympy).
"""

def tau(n):
    """Number of divisors of n."""
    if n < 1:
        return 0
    count = 0
    i = 1
    while i * i <= n:
        if n % i == 0:
            count += 1
            if i != n // i:
                count += 1
        i += 1
    return count

def sigma(n):
    """Sum of divisors of n."""
    if n < 1:
        return 0
    s = 0
    i = 1
    while i * i <= n:
        if n % i == 0:
            s += i
            if i != n // i:
                s += n // i
        i += 1
    return s

def phi(n):
    """Euler's totient function."""
    if n < 1:
        return 0
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

def divisors(n):
    """Return sorted list of divisors of n."""
    divs = []
    i = 1
    while i * i <= n:
        if n % i == 0:
            divs.append(i)
            if i != n // i:
                divs.append(n // i)
        i += 1
    return sorted(divs)

def partitions(n):
    """Count integer partitions of n using dynamic programming."""
    dp = [0] * (n + 1)
    dp[0] = 1
    for k in range(1, n + 1):
        for j in range(k, n + 1):
            dp[j] += dp[j - k]
    return dp[n]

def mersenne_exp(pk):
    """Given perfect number P_k = 2^(p-1)*(2^p - 1), find p."""
    # For even perfect numbers, P = 2^(p-1) * (2^p - 1)
    # tau(P) = 2p
    # We can find p by factoring out powers of 2
    n = pk
    p_minus_1 = 0
    while n % 2 == 0:
        n //= 2
        p_minus_1 += 1
    # n should now be 2^p - 1, and p = p_minus_1 + 1
    p = p_minus_1 + 1
    # Verify: 2^p - 1 == n
    if (1 << p) - 1 == n:
        return p
    return None

# ============================================================
# Perfect numbers
# ============================================================
P = [6, 28, 496, 8128, 33550336, 8589869056]
P_names = ["P1", "P2", "P3", "P4", "P5", "P6"]

# Precompute
tau_P = {i+1: tau(P[i]) for i in range(6)}
sigma_P = {i+1: sigma(P[i]) for i in range(6)}
phi_P = {i+1: phi(P[i]) for i in range(6)}

print("# H-PH-9 & H-PH-11 Numerical Verification")
print()

# ============================================================
# Section 1: Basic properties
# ============================================================
print("## 1. Basic Number-Theoretic Functions for First 6 Perfect Numbers")
print()
print("| P_k | Value | tau | sigma | phi | Mersenne p | tau==2p? |")
print("|-----|-------|-----|-------|-----|------------|----------|")

results = []
pass_count = 0
fail_count = 0

for i in range(6):
    k = i + 1
    pk = P[i]
    t = tau_P[k]
    s = sigma_P[k]
    ph = phi_P[k]
    mp = mersenne_exp(pk)
    expected_tau = 2 * mp if mp else "?"
    match = t == expected_tau
    status = "PASS" if match else "FAIL"
    if match:
        pass_count += 1
    else:
        fail_count += 1
    results.append((f"tau(P{k})=2p", match))
    print(f"| P{k} | {pk} | {t} | {s} | {ph} | {mp} | {status} (tau={t}, 2p={expected_tau}) |")

print()

# ============================================================
# Section 2: Physical dimension mapping
# ============================================================
print("## 2. Physical Dimension Mapping: tau(P_k) = known dimensions")
print()
print("| Claim | Expected | Computed | Status |")
print("|-------|----------|----------|--------|")

dim_claims = [
    ("tau(6)=4 (spacetime)", 4, tau_P[1]),
    ("tau(28)=6 (Calabi-Yau)", 6, tau_P[2]),
    ("tau(496)=10 (superstring)", 10, tau_P[3]),
    ("tau(8128)=14 (G2 holonomy)", 14, tau_P[4]),
    ("tau(33550336)=26 (bosonic string)", 26, tau_P[5]),
]

for label, expected, computed in dim_claims:
    match = expected == computed
    status = "PASS" if match else "FAIL"
    if match:
        pass_count += 1
    else:
        fail_count += 1
    results.append((label, match))
    print(f"| {label} | {expected} | {computed} | {status} |")

print()

# tau(P6)
print(f"| tau(P6=8589869056) | (claimed 2p) | {tau_P[6]} | INFO (p={mersenne_exp(P[5])}, 2p={2*mersenne_exp(P[5])}) |")
print()

# ============================================================
# Section 3: Dimension addition
# ============================================================
print("## 3. Dimension Addition: tau(6)+tau(28)==tau(496)")
print()
lhs = tau_P[1] + tau_P[2]
rhs = tau_P[3]
match = lhs == rhs
status = "PASS" if match else "FAIL"
if match:
    pass_count += 1
else:
    fail_count += 1
results.append(("tau(6)+tau(28)==tau(496)", match))
print(f"| Claim | LHS | RHS | Status |")
print(f"|-------|-----|-----|--------|")
print(f"| tau(6)+tau(28)==tau(496) | {tau_P[1]}+{tau_P[2]}={lhs} | {rhs} | {status} |")
print()

# ============================================================
# Section 4: Leech lattice & E8
# ============================================================
print("## 4. Algebraic Identities (Leech, E8)")
print()
print("| Claim | Expected | Computed | Status |")
print("|-------|----------|----------|--------|")

# sigma(6)*phi(6) == 24
val = sigma_P[1] * phi_P[1]
match = val == 24
status = "PASS" if match else "FAIL"
if match: pass_count += 1
else: fail_count += 1
results.append(("sigma(6)*phi(6)==24 (Leech)", match))
print(f"| sigma(6)*phi(6)==24 (Leech lattice dim) | 24 | {val} (={sigma_P[1]}*{phi_P[1]}) | {status} |")

# phi(496)==240
match = phi_P[3] == 240
status = "PASS" if match else "FAIL"
if match: pass_count += 1
else: fail_count += 1
results.append(("phi(496)==240 (E8 roots)", match))
print(f"| phi(496)==240 (E8 root count) | 240 | {phi_P[3]} | {status} |")

# 496 == 248+248
match = P[2] == 248 + 248
status = "PASS" if match else "FAIL"
if match: pass_count += 1
else: fail_count += 1
results.append(("496==248+248 (E8xE8)", match))
print(f"| 496==248+248 (E8 x E8) | 496 | {248+248} | {status} |")

print()

# ============================================================
# Section 5: Graviton DOF
# ============================================================
print("## 5. Graviton Degrees of Freedom: D(D-3)/2")
print()
print("| D | D(D-3)/2 | Claimed match | Computed match | Status |")
print("|---|----------|---------------|----------------|--------|")

# D=4: DOF=2, claim: phi(P1)=2
dof4 = 4 * (4-3) // 2
claim4 = phi_P[1]
match = dof4 == claim4
status = "PASS" if match else "FAIL"
if match: pass_count += 1
else: fail_count += 1
results.append(("D=4 graviton: phi(P1)=2", match))
print(f"| 4 | {dof4} | phi(P1)={claim4} | phi(6)={phi_P[1]} | {status} |")

# D=6: DOF=9, claim: (sigma/tau)^2 = (12/4)^2 = 9
dof6 = 6 * (6-3) // 2
claim6_val = (sigma_P[1] / tau_P[1]) ** 2
match = dof6 == int(claim6_val)
status = "PASS" if match else "FAIL"
if match: pass_count += 1
else: fail_count += 1
results.append(("D=6 graviton: (sigma/tau)^2=9", match))
print(f"| 6 | {dof6} | (sigma(6)/tau(6))^2 | ({sigma_P[1]}/{tau_P[1]})^2={claim6_val:.0f} | {status} |")

# D=10: DOF=35, claim: (tau(P3)/2)*(tau(P4)/2)=35
dof10 = 10 * (10-3) // 2
claim10 = (tau_P[3] // 2) * (tau_P[4] // 2)
match = dof10 == claim10
status = "PASS" if match else "FAIL"
if match: pass_count += 1
else: fail_count += 1
results.append(("D=10 graviton: (tau(P3)/2)*(tau(P4)/2)=35", match))
print(f"| 10 | {dof10} | (tau(P3)/2)*(tau(P4)/2) | ({tau_P[3]}/2)*({tau_P[4]}/2)={claim10} | {status} |")

# D=11: DOF=44, claim: sigma(P2)-sigma(P1)=44
dof11 = 11 * (11-3) // 2
claim11 = sigma_P[2] - sigma_P[1]
match = dof11 == claim11
status = "PASS" if match else "FAIL"
if match: pass_count += 1
else: fail_count += 1
results.append(("D=11 graviton: sigma(P2)-sigma(P1)=44", match))
print(f"| 11 | {dof11} | sigma(P2)-sigma(P1) | {sigma_P[2]}-{sigma_P[1]}={claim11} | {status} |")

print()

# ============================================================
# Section 6: Kissing numbers
# ============================================================
print("## 6. Kissing Numbers")
print()
print("| Dimension | k(d) known | Claimed expression | Computed | Status |")
print("|-----------|------------|-------------------|----------|--------|")

kissing = [
    (1, 2, "phi(P1)", phi_P[1]),
    (2, 6, "P1", P[0]),
    (3, 12, "sigma(P1)", sigma_P[1]),
    (4, 24, "sigma(P1)*phi(P1)", sigma_P[1] * phi_P[1]),
    (8, 240, "phi(P3)", phi_P[3]),
]

for dim, known, expr, computed in kissing:
    match = known == computed
    status = "PASS" if match else "FAIL"
    if match: pass_count += 1
    else: fail_count += 1
    results.append((f"k({dim})={known}: {expr}", match))
    print(f"| {dim} | {known} | {expr} | {computed} | {status} |")

print()

# ============================================================
# Section 7: M-theory dimension
# ============================================================
print("## 7. M-theory Dimension = 11")
print()
print("| Claim | Expression | Computed | Status |")
print("|-------|-----------|----------|--------|")

mtheory = (sigma_P[2] - sigma_P[1]) / tau_P[1]
match = mtheory == 11
status = "PASS" if match else "FAIL"
if match: pass_count += 1
else: fail_count += 1
results.append(("M-theory: [sigma(P2)-sigma(P1)]/tau(P1)=11", match))
print(f"| [sigma(P2)-sigma(P1)]/tau(P1)=11 | ({sigma_P[2]}-{sigma_P[1]})/{tau_P[1]} | {mtheory:.1f} | {status} |")

print()

# ============================================================
# Section 8: GUT dimensions
# ============================================================
print("## 8. GUT Group Dimensions")
print()
print("| Group | dim | Claimed expression | Computed | Status |")
print("|-------|-----|-------------------|----------|--------|")

# SU(5): dim=24 = sigma*phi
su5 = sigma_P[1] * phi_P[1]
match = su5 == 24
status = "PASS" if match else "FAIL"
if match: pass_count += 1
else: fail_count += 1
results.append(("SU(5)=24: sigma(P1)*phi(P1)", match))
print(f"| SU(5) | 24 | sigma(P1)*phi(P1) | {su5} | {status} |")

# SO(10): dim=45 = sigma*tau - sigma/tau
so10 = sigma_P[1] * tau_P[1] - sigma_P[1] // tau_P[1]
match = so10 == 45
status = "PASS" if match else "FAIL"
if match: pass_count += 1
else: fail_count += 1
results.append(("SO(10)=45: sigma*tau-sigma/tau", match))
print(f"| SO(10) | 45 | sigma(P1)*tau(P1)-sigma(P1)/tau(P1) | {sigma_P[1]}*{tau_P[1]}-{sigma_P[1]}/{tau_P[1]}={so10} | {status} |")

# E6: dim=78 = tau(P2)*(sigma(P1)+1)
e6 = tau_P[2] * (sigma_P[1] + 1)
match = e6 == 78
status = "PASS" if match else "FAIL"
if match: pass_count += 1
else: fail_count += 1
results.append(("E6=78: tau(P2)*(sigma(P1)+1)", match))
print(f"| E6 | 78 | tau(P2)*(sigma(P1)+1) | {tau_P[2]}*({sigma_P[1]}+1)={e6} | {status} |")

# E7 fundamental: dim=56 = sigma(P2)
e7 = sigma_P[2]
match = e7 == 56
status = "PASS" if match else "FAIL"
if match: pass_count += 1
else: fail_count += 1
results.append(("E7fund=56: sigma(P2)", match))
print(f"| E7 fund | 56 | sigma(P2) | {e7} | {status} |")

# E8: dim=248 = P3/2
e8 = P[2] // 2
match = e8 == 248
status = "PASS" if match else "FAIL"
if match: pass_count += 1
else: fail_count += 1
results.append(("E8=248: P3/2", match))
print(f"| E8 | 248 | P3/2 | {e8} | {status} |")

# E8xE8: dim=496 = P3
e8e8 = P[2]
match = e8e8 == 496
status = "PASS" if match else "FAIL"
if match: pass_count += 1
else: fail_count += 1
results.append(("E8xE8=496: P3", match))
print(f"| E8 x E8 | 496 | P3 | {e8e8} | {status} |")

print()

# ============================================================
# Section 9: Minkowski signature
# ============================================================
print("## 9. Minkowski Signature from Divisors of 6")
print()
divs6 = divisors(6)
print(f"Divisors of 6: {divs6}")
print()
print("| Claim | Detail | Status |")
print("|-------|--------|--------|")

match = divs6 == [1, 2, 3, 6]
status = "PASS" if match else "FAIL"
if match: pass_count += 1
else: fail_count += 1
results.append(("Divisors of 6 = [1,2,3,6]", match))
print(f"| divisors(6)=[1,2,3,6] | {divs6} | {status} |")

# Interpretation: smallest=1 (time), next 3 are space dims → (1,3) signature
# This is interpretive, but we check the count
space_count = len(divs6) - 1  # excluding smallest
match2 = space_count == 3 and divs6[0] == 1
status2 = "PASS" if match2 else "FAIL"
if match2: pass_count += 1
else: fail_count += 1
results.append(("(1time, 3space) from divisor structure", match2))
print(f"| (1 time, 3 space) interpretation | min={divs6[0]}, remaining count={space_count} | {status2} |")

print()

# ============================================================
# Section 10: H-PH-11 — Partition M-theory
# ============================================================
print("## 10. H-PH-11: Partition Function and M-theory")
print()
print("| Claim | Expected | Computed | Status |")
print("|-------|----------|----------|--------|")

p6 = partitions(6)
match = p6 == 11
status = "PASS" if match else "FAIL"
if match: pass_count += 1
else: fail_count += 1
results.append(("p(6)=11 (M-theory dimension)", match))
print(f"| p(6)=11 (M-theory spacetime dim) | 11 | {p6} | {status} |")

# Bonus: show all partitions of 6 for verification
print()
print("Partitions of 6 enumerated:")
print("  6 = 6")
print("  6 = 5+1")
print("  6 = 4+2")
print("  6 = 4+1+1")
print("  6 = 3+3")
print("  6 = 3+2+1")
print("  6 = 3+1+1+1")
print("  6 = 2+2+2")
print("  6 = 2+2+1+1")
print("  6 = 2+1+1+1+1")
print("  6 = 1+1+1+1+1+1")
print(f"  Total: {p6} partitions")

print()

# ============================================================
# Section 11: Additional context — partition values
# ============================================================
print("## 11. Context: Partition Function for Small n")
print()
print("| n | p(n) | Physical note |")
print("|---|------|-------------|")
for n in range(1, 13):
    pn = partitions(n)
    note = ""
    if n == 6:
        note = "M-theory dim=11"
    elif n == 4:
        note = "spacetime dim, p(4)=5"
    elif n == 10:
        note = "superstring dim, p(10)=42"
    print(f"| {n} | {pn} | {note} |")

print()

# ============================================================
# Section 12: sigma_(-1)(6) = 2 check
# ============================================================
print("## 12. Perfect Number Verification: sigma_{-1}(6)=2")
print()
# sigma_{-1}(n) = sum of 1/d for d | n
divs = divisors(6)
sigma_minus1 = sum(1/d for d in divs)
match = abs(sigma_minus1 - 2.0) < 1e-10
status = "PASS" if match else "FAIL"
if match: pass_count += 1
else: fail_count += 1
results.append(("sigma_{-1}(6)=2 (perfect number)", match))
print(f"| Claim | Expected | Computed | Status |")
print(f"|-------|----------|----------|--------|")
print(f"| sigma_{{-1}}(6)=sum(1/d) for d|6 | 2 | 1/{divs[0]}+1/{divs[1]}+1/{divs[2]}+1/{divs[3]}={sigma_minus1:.6f} | {status} |")

print()

# Also verify sigma(n) = 2n for all 6 perfect numbers
print("## 13. Perfect Number Check: sigma(P_k) = 2*P_k")
print()
print("| P_k | sigma(P_k) | 2*P_k | Match? |")
print("|-----|-----------|-------|--------|")
for i in range(6):
    k = i + 1
    s = sigma_P[k]
    twop = 2 * P[i]
    match = s == twop
    status = "PASS" if match else "FAIL"
    if match: pass_count += 1
    else: fail_count += 1
    results.append((f"sigma(P{k})=2*P{k}", match))
    print(f"| P{k}={P[i]} | {s} | {twop} | {status} |")

print()

# ============================================================
# SUMMARY
# ============================================================
print("=" * 60)
print("## SUMMARY")
print("=" * 60)
print()
print(f"Total claims verified: {len(results)}")
print(f"PASS: {pass_count}")
print(f"FAIL: {fail_count}")
print(f"Pass rate: {pass_count}/{len(results)} = {100*pass_count/len(results):.1f}%")
print()

print("| # | Claim | Result |")
print("|---|-------|--------|")
for i, (claim, passed) in enumerate(results, 1):
    print(f"| {i} | {claim} | {'PASS' if passed else 'FAIL'} |")

print()
if fail_count == 0:
    print("**ALL CLAIMS VERIFIED SUCCESSFULLY.**")
else:
    print(f"**{fail_count} claim(s) FAILED verification.**")
    print()
    print("Failed claims:")
    for claim, passed in results:
        if not passed:
            print(f"  - {claim}")
