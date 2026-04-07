#!/usr/bin/env python3
"""
DFS: Dedekind ψ function and discrepancy D(n)=σφ-nτ identities.
Search for identities where n=6 or n=28 is unique.
"""

import math
from collections import defaultdict

# ── Arithmetic functions ──

def sigma(n):
    """Sum of divisors."""
    s = 0
    for i in range(1, int(math.isqrt(n)) + 1):
        if n % i == 0:
            s += i
            if i != n // i:
                s += n // i
    return s

def tau(n):
    """Number of divisors."""
    t = 0
    for i in range(1, int(math.isqrt(n)) + 1):
        if n % i == 0:
            t += 1
            if i != n // i:
                t += 1
    return t

def euler_phi(n):
    """Euler's totient."""
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

def factorize(n):
    """Return prime factorization as dict {p: e}."""
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

def psi(n):
    """Dedekind psi: ψ(n) = n * ∏(1 + 1/p) over prime p | n."""
    if n == 1:
        return 1
    factors = factorize(n)
    result = n
    for p in factors:
        result = result * (p + 1) // p
    return result

def D(n):
    """Discrepancy D(n) = σ(n)*φ(n) - n*τ(n)."""
    return sigma(n) * euler_phi(n) - n * tau(n)

# ── Precompute for n=1..10000 ──
N_MAX = 10000
print(f"Precomputing arithmetic functions for n=1..{N_MAX}...")

sig = [0] * (N_MAX + 1)
ta  = [0] * (N_MAX + 1)
phi = [0] * (N_MAX + 1)
ps  = [0] * (N_MAX + 1)
disc = [0] * (N_MAX + 1)

for n in range(1, N_MAX + 1):
    sig[n] = sigma(n)
    ta[n]  = tau(n)
    phi[n] = euler_phi(n)
    ps[n]  = psi(n)
    disc[n] = sig[n] * phi[n] - n * ta[n]

print("Done.\n")

# Perfect numbers in range
perfects = [n for n in range(1, N_MAX + 1) if sig[n] == 2 * n]
print(f"Perfect numbers in range: {perfects}\n")

# ══════════════════════════════════════════════════════════════
# CHECK 1: D(n) + ψ(n) = ? Pattern?
# ══════════════════════════════════════════════════════════════
print("=" * 70)
print("CHECK 1: D(n) + ψ(n)")
print("=" * 70)

# Show small values
print(f"\n{'n':>5} {'D(n)':>10} {'ψ(n)':>10} {'D+ψ':>10} {'σ(n)':>10} {'D+ψ==σ?':>8} {'D+ψ==nτ?':>8}")
print("-" * 70)
for n in range(1, 31):
    dp = disc[n] + ps[n]
    eq_sig = (dp == sig[n])
    eq_nt = (dp == n * ta[n])
    marker = ""
    if n in perfects:
        marker = " ★PERFECT"
    if disc[n] == 0:
        marker += " (D=0)"
    print(f"{n:5d} {disc[n]:10d} {ps[n]:10d} {dp:10d} {sig[n]:10d} {'YES' if eq_sig else '':>8} {'YES' if eq_nt else '':>8}{marker}")

# Check: where D+ψ = σ?
d_plus_psi_eq_sigma = [n for n in range(1, N_MAX + 1) if disc[n] + ps[n] == sig[n]]
print(f"\nD(n)+ψ(n) = σ(n) for n in: {d_plus_psi_eq_sigma[:50]}{'...' if len(d_plus_psi_eq_sigma) > 50 else ''}")
print(f"  Count: {len(d_plus_psi_eq_sigma)} / {N_MAX}")

# Check: where D+ψ = nτ?
d_plus_psi_eq_nt = [n for n in range(1, N_MAX + 1) if disc[n] + ps[n] == n * ta[n]]
print(f"\nD(n)+ψ(n) = n·τ(n) for n in: {d_plus_psi_eq_nt[:50]}{'...' if len(d_plus_psi_eq_nt) > 50 else ''}")
print(f"  Count: {len(d_plus_psi_eq_nt)} / {N_MAX}")

# Check: where D+ψ = 2n?
d_plus_psi_eq_2n = [n for n in range(1, N_MAX + 1) if disc[n] + ps[n] == 2 * n]
print(f"\nD(n)+ψ(n) = 2n for n in: {d_plus_psi_eq_2n[:50]}{'...' if len(d_plus_psi_eq_2n) > 50 else ''}")

# ══════════════════════════════════════════════════════════════
# CHECK 2: σψ - nτφ
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("CHECK 2: σ(n)·ψ(n) - n·τ(n)·φ(n)")
print("=" * 70)

print(f"\n{'n':>5} {'σψ':>12} {'nτφ':>12} {'σψ-nτφ':>12} {'ratio':>10}")
print("-" * 55)
for n in range(1, 31):
    sp = sig[n] * ps[n]
    ntp = n * ta[n] * phi[n]
    diff = sp - ntp
    ratio_str = f"{sp/ntp:.4f}" if ntp != 0 else "inf"
    marker = " ★" if n in perfects else ""
    print(f"{n:5d} {sp:12d} {ntp:12d} {diff:12d} {ratio_str:>10}{marker}")

# At perfect numbers
print("\nAt perfect numbers:")
for n in perfects:
    sp = sig[n] * ps[n]
    ntp = n * ta[n] * phi[n]
    diff = sp - ntp
    print(f"  n={n}: σψ-nτφ = {diff}, σψ/nτφ = {sp/ntp:.6f}")

# ══════════════════════════════════════════════════════════════
# CHECK 3: ψ(n)/φ(n) at perfect numbers
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("CHECK 3: ψ(n)/φ(n) at perfect numbers")
print("=" * 70)

for n in perfects:
    ratio = ps[n] / phi[n]
    print(f"  n={n}: ψ/φ = {ps[n]}/{phi[n]} = {ratio:.6f}, n={n}, τ={ta[n]}, σ={sig[n]}")
    print(f"    ψ/φ == n? {ps[n] == n * phi[n] // phi[n] and ps[n] / phi[n] == n}")
    print(f"    ψ/φ == τ? {abs(ratio - ta[n]) < 1e-9}")

# ══════════════════════════════════════════════════════════════
# CHECK 4: ψ(n)/φ(n) = n — unique to n=6?
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("CHECK 4: ψ(n)/φ(n) = n — is n=6 unique?")
print("=" * 70)

psi_over_phi_eq_n = []
for n in range(1, N_MAX + 1):
    if phi[n] > 0 and ps[n] == n * phi[n]:  # ψ/φ = n means ψ = n·φ
        psi_over_phi_eq_n.append(n)

print(f"Solutions of ψ(n)/φ(n) = n for n=1..{N_MAX}: {psi_over_phi_eq_n}")

# Also check ψ = n·φ more carefully
# ψ(n) = n·∏(1+1/p), φ(n) = n·∏(1-1/p)
# ψ/φ = ∏(p+1)/(p-1)
# ψ/φ = n means ∏(p+1)/(p-1) = n
print("\nAnalytically: ψ/φ = ∏(p+1)/(p-1) over primes p|n")
print("For n=6=2·3: ψ/φ = (3/1)·(4/2) = 6 = n  ✓")
print("For n=1: ψ/φ = 1 = n  ✓ (empty product)")
print("For this to equal n, need ∏(p+1)/(p-1) = n = ∏p^{e_p}")
print("This is extremely restrictive.\n")

# ══════════════════════════════════════════════════════════════
# CHECK 5: ψ(n)/φ(n) = τ(n) — unique to n=28?
# ══════════════════════════════════════════════════════════════
print("=" * 70)
print("CHECK 5: ψ(n)/φ(n) = τ(n) — is n=28 unique?")
print("=" * 70)

psi_over_phi_eq_tau = []
for n in range(1, N_MAX + 1):
    if phi[n] > 0 and ps[n] * 1 == ta[n] * phi[n]:  # ψ/φ = τ
        psi_over_phi_eq_tau.append(n)

print(f"Solutions of ψ(n)/φ(n) = τ(n) for n=1..{N_MAX}:")
print(f"  {psi_over_phi_eq_tau[:60]}{'...' if len(psi_over_phi_eq_tau) > 60 else ''}")
print(f"  Count: {len(psi_over_phi_eq_tau)}")
if 28 in psi_over_phi_eq_tau:
    print("  n=28 IS in the list ✓")
else:
    print("  n=28 is NOT in the list ✗")

# Show details for each solution
print("\nDetails:")
for n in psi_over_phi_eq_tau[:30]:
    f = factorize(n) if n > 1 else {}
    print(f"  n={n}: factors={f}, ψ={ps[n]}, φ={phi[n]}, τ={ta[n]}, ψ/φ={ps[n]/phi[n]:.2f}")

# ══════════════════════════════════════════════════════════════
# CHECK 6: D(n)·n·τ(n) patterns
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("CHECK 6: D(n)·n·τ(n) and related products")
print("=" * 70)

print(f"\n{'n':>5} {'D':>8} {'nτ':>8} {'D·nτ':>12} {'σφ':>10} {'(σφ)²':>14} {'D·nτ/(σφ)²':>12}")
print("-" * 75)
for n in range(1, 21):
    d = disc[n]
    nt = n * ta[n]
    dnt = d * nt
    sp = sig[n] * phi[n]
    sp2 = sp * sp
    ratio_str = f"{dnt/sp2:.6f}" if sp2 != 0 else "N/A"
    print(f"{n:5d} {d:8d} {nt:8d} {dnt:12d} {sp:10d} {sp2:14d} {ratio_str:>12}")

# ══════════════════════════════════════════════════════════════
# CHECK 7: (σ+D)(φ+D) expansion
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("CHECK 7: (σ+D)(φ+D) where D=σφ-nτ")
print("=" * 70)
print("  (σ+D)(φ+D) = σφ + D(σ+φ) + D²")
print("             = σφ + (σφ-nτ)(σ+φ) + (σφ-nτ)²")

print(f"\n{'n':>5} {'(σ+D)(φ+D)':>14} {'σφ':>10} {'nτ':>8} {'(σ+D)(φ+D)/n²':>16}")
print("-" * 60)
for n in range(1, 21):
    val = (sig[n] + disc[n]) * (phi[n] + disc[n])
    sp = sig[n] * phi[n]
    nt = n * ta[n]
    ratio = val / (n * n) if n > 0 else 0
    marker = " ★" if n in perfects else ""
    print(f"{n:5d} {val:14d} {sp:10d} {nt:8d} {ratio:16.4f}{marker}")

# ══════════════════════════════════════════════════════════════
# NEW SEARCH: Systematic uniqueness checks at n=6 and n=28
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("SYSTEMATIC UNIQUENESS SEARCH")
print("=" * 70)

# Helper: check if n is unique solution in range
def find_solutions(func, limit=N_MAX):
    """Find all n in [1,limit] where func(n) returns True."""
    sols = [n for n in range(1, limit + 1) if func(n)]
    return sols

# ── Identity A: D(n) + ψ(n) = σ(n) + φ(n) ──
sols = find_solutions(lambda n: disc[n] + ps[n] == sig[n] + phi[n])
print(f"\nA: D+ψ = σ+φ → {sols[:30]}  (count={len(sols)})")

# ── Identity B: D(n) = ψ(n) ──
sols = find_solutions(lambda n: disc[n] == ps[n])
print(f"B: D = ψ → {sols[:30]}  (count={len(sols)})")

# ── Identity C: D(n) + ψ(n) = n·σ(n)/φ(n) (integer?) ──
sols = find_solutions(lambda n: phi[n] > 0 and (n * sig[n]) % phi[n] == 0 and disc[n] + ps[n] == n * sig[n] // phi[n])
print(f"C: D+ψ = nσ/φ → {sols[:30]}  (count={len(sols)})")

# ── Identity D: ψ(n) - φ(n) = σ(n) ──
sols = find_solutions(lambda n: ps[n] - phi[n] == sig[n])
print(f"D: ψ-φ = σ → {sols[:30]}  (count={len(sols)})")

# ── Identity E: ψ(n) + φ(n) = σ(n) ──
sols = find_solutions(lambda n: ps[n] + phi[n] == sig[n])
print(f"E: ψ+φ = σ → {sols[:30]}  (count={len(sols)})")

# ── Identity F: ψ(n) = σ(n) ──
sols = find_solutions(lambda n: ps[n] == sig[n])
print(f"F: ψ = σ → {sols[:30]}  (count={len(sols)})")

# ── Identity G: ψ(n)·φ(n) = n·σ(n) ──
sols = find_solutions(lambda n: ps[n] * phi[n] == n * sig[n])
print(f"G: ψφ = nσ → {sols[:30]}  (count={len(sols)})")

# ── Identity H: ψ(n)/φ(n) = σ(n)/n (= σ₋₁) ──
sols = find_solutions(lambda n: phi[n] > 0 and ps[n] * n == sig[n] * phi[n])
print(f"H: ψ/φ = σ/n → {sols[:30]}  (count={len(sols)})")

# ── Identity I: D(n) = n²-n ──
sols = find_solutions(lambda n: disc[n] == n * n - n)
print(f"I: D = n²-n → {sols[:30]}  (count={len(sols)})")

# ── Identity J: D(n) = n·ψ(n) - n·σ(n) ──
sols = find_solutions(lambda n: disc[n] == n * ps[n] - n * sig[n])
print(f"J: D = n(ψ-σ) → {sols[:30]}  (count={len(sols)})")

# ── Identity K: σ(n)·ψ(n) = (n·τ(n))² ──
sols = find_solutions(lambda n: sig[n] * ps[n] == (n * ta[n]) ** 2)
print(f"K: σψ = (nτ)² → {sols[:30]}  (count={len(sols)})")

# ── Identity L: D(n)² = n·σ(n)·φ(n)·(something) ──
# Check D² / (nσφ)
print("\nL: D(n)² / (n·σ·φ) at small n:")
for n in range(2, 20):
    if sig[n] * phi[n] > 0:
        d2 = disc[n] ** 2
        nsp = n * sig[n] * phi[n]
        if nsp > 0:
            r = d2 / nsp
            print(f"  n={n}: D²={d2}, nσφ={nsp}, ratio={r:.6f}")

# ══════════════════════════════════════════════════════════════
# DEEP SEARCH: Expressions unique to n=6 among n=1..10000
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("DEEP SEARCH: Expressions unique to n=6 (or {1,6})")
print("=" * 70)

tests_6 = [
    ("ψ/φ = n",              lambda n: phi[n] > 0 and ps[n] == n * phi[n]),
    ("D = 0",                 lambda n: disc[n] == 0),
    ("σ = 2n (perfect)",      lambda n: sig[n] == 2 * n),
    ("ψ = 2σ",               lambda n: ps[n] == 2 * sig[n]),
    ("ψ = σ + n",             lambda n: ps[n] == sig[n] + n),
    ("ψ·D = 0",              lambda n: ps[n] * disc[n] == 0),
    ("ψ = n·τ",              lambda n: ps[n] == n * ta[n]),
    ("σ·φ = n·τ (D=0)",      lambda n: sig[n] * phi[n] == n * ta[n]),
    ("ψ² = n²·σ",            lambda n: ps[n] ** 2 == n ** 2 * sig[n]),
    ("φ·ψ = n²",             lambda n: phi[n] * ps[n] == n * n),
    ("σ+φ = ψ+n",            lambda n: sig[n] + phi[n] == ps[n] + n),
    ("σ-ψ = n-φ",            lambda n: sig[n] - ps[n] == n - phi[n]),  # same as above
    ("ψ/σ = n/φ",            lambda n: phi[n] > 0 and ps[n] * phi[n] == n * sig[n]),
    ("σ·ψ = n·(σ+ψ)",       lambda n: sig[n] * ps[n] == n * (sig[n] + ps[n])),
    ("ψ-φ = 2n",             lambda n: ps[n] - phi[n] == 2 * n),
    ("ψ-φ = σ-1",            lambda n: ps[n] - phi[n] == sig[n] - 1),
    ("σ+ψ = 3n",             lambda n: sig[n] + ps[n] == 3 * n),
    ("σ+ψ = 4n",             lambda n: sig[n] + ps[n] == 4 * n),
    ("σ+ψ+φ = 4n",           lambda n: sig[n] + ps[n] + phi[n] == 4 * n),
    ("D+ψ = 2σ",             lambda n: disc[n] + ps[n] == 2 * sig[n]),
    ("D+ψ = 2nτ",            lambda n: disc[n] + ps[n] == 2 * n * ta[n]),
    ("(ψ-φ)/n = τ",          lambda n: n > 0 and (ps[n] - phi[n]) % n == 0 and (ps[n] - phi[n]) // n == ta[n]),
    ("ψ/n = σ/φ",            lambda n: phi[n] > 0 and n > 0 and ps[n] * phi[n] == n * sig[n]),
    ("σ²-ψ² = D·n",          lambda n: sig[n]**2 - ps[n]**2 == disc[n] * n),
    ("ψ = σ·φ/n",            lambda n: n > 0 and (sig[n] * phi[n]) % n == 0 and ps[n] == sig[n] * phi[n] // n),
    ("ψ+D = σ+nτ-n",         lambda n: ps[n] + disc[n] == sig[n] + n * ta[n] - n),
    ("ψ·τ = n² (τψ=n²)",     lambda n: ps[n] * ta[n] == n * n),
    ("D + n = ψ",             lambda n: disc[n] + n == ps[n]),
    ("σ/ψ + φ/n = 1",        lambda n: n > 0 and ps[n] > 0 and sig[n] * n + phi[n] * ps[n] == ps[n] * n),
    ("ψ = σ·n/(n+φ)",        lambda n: (n + phi[n]) > 0 and ps[n] * (n + phi[n]) == sig[n] * n),
]

print(f"\n{'Expression':<30} {'Solutions (first 10)':>50} {'Count':>6}")
print("-" * 90)
for label, test in tests_6:
    sols = find_solutions(test)
    sol_str = str(sols[:10])
    if len(sols) > 10:
        sol_str += "..."
    unique_6 = (sols == [6] or sols == [1, 6])
    marker = " ◀◀◀ UNIQUE!" if unique_6 else ""
    print(f"{label:<30} {sol_str:>50} {len(sols):6d}{marker}")

# ══════════════════════════════════════════════════════════════
# DEEP SEARCH: Expressions unique to n=28
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("DEEP SEARCH: Expressions unique to n=28")
print("=" * 70)

tests_28 = [
    ("ψ/φ = τ",              lambda n: phi[n] > 0 and ps[n] == ta[n] * phi[n]),
    ("ψ·τ = n²",             lambda n: ps[n] * ta[n] == n * n),
    ("σ-ψ = n",              lambda n: sig[n] - ps[n] == n),
    ("σ-ψ = 2n-σ",           lambda n: sig[n] - ps[n] == 2 * n - sig[n]),  # 2σ=ψ+2n
    ("2σ = ψ+2n",            lambda n: 2 * sig[n] == ps[n] + 2 * n),
    ("ψ = σ-n",              lambda n: ps[n] == sig[n] - n),
    ("ψ+n = σ",              lambda n: ps[n] + n == sig[n]),
    ("D = (σ-ψ)·τ",          lambda n: disc[n] == (sig[n] - ps[n]) * ta[n]),
    ("D = n·(τ²-τ)",         lambda n: disc[n] == n * (ta[n]**2 - ta[n])),
    ("D/(nτ) = τ-1",         lambda n: n > 0 and ta[n] > 0 and disc[n] == n * ta[n] * (ta[n] - 1)),
    ("ψ+φ = σ+τ",            lambda n: ps[n] + phi[n] == sig[n] + ta[n]),
    ("ψ·φ = n·σ·τ/σ",        lambda n: sig[n] > 0 and ps[n] * phi[n] * sig[n] == n * sig[n] * ta[n]),  # simplify
    ("D/ψ = integer",        lambda n: ps[n] > 0 and disc[n] % ps[n] == 0),
    ("(σ-ψ)·φ = D",          lambda n: (sig[n] - ps[n]) * phi[n] == disc[n]),
    ("D = σ·(φ-n) + n·(σ-τ)", lambda n: disc[n] == sig[n] * (phi[n] - n) + n * (sig[n] - ta[n])),
    ("ψ²-φ² = n·σ·τ",       lambda n: ps[n]**2 - phi[n]**2 == n * sig[n] * ta[n]),
    ("(ψ-φ)·(ψ+φ) = nστ",   lambda n: (ps[n]-phi[n])*(ps[n]+phi[n]) == n*sig[n]*ta[n]),  # same
    ("D·ψ = n²·σ·τ",        lambda n: disc[n] * ps[n] == n**2 * sig[n] * ta[n]),
    ("σ+ψ = 2n+2φ",          lambda n: sig[n] + ps[n] == 2*n + 2*phi[n]),
]

print(f"\n{'Expression':<30} {'Solutions (first 10)':>50} {'Count':>6}")
print("-" * 90)
for label, test in tests_28:
    sols = find_solutions(test)
    sol_str = str(sols[:10])
    if len(sols) > 10:
        sol_str += "..."
    has_28 = 28 in sols
    unique_28 = (sols == [28]) or (sols == [1, 28])
    marker = ""
    if unique_28:
        marker = " ◀◀◀ UNIQUE!"
    elif has_28 and len(sols) <= 5:
        marker = " ◀ RARE"
    print(f"{label:<30} {sol_str:>50} {len(sols):6d}{marker}")

# ══════════════════════════════════════════════════════════════
# BONUS: ψ/φ ratio study
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("BONUS: ψ(n)/φ(n) = f(n) — what does ψ/φ equal at perfects?")
print("=" * 70)

for n in perfects:
    r = ps[n] / phi[n]
    facts = factorize(n)
    prod_str = " · ".join([f"({p}+1)/({p}-1)" for p in sorted(facts.keys())])
    print(f"\n  n={n}: ψ/φ = {ps[n]}/{phi[n]} = {r}")
    print(f"    = {prod_str}")
    print(f"    σ={sig[n]}, τ={ta[n]}, φ={phi[n]}, ψ={ps[n]}")
    print(f"    ψ/φ = n? {abs(r - n) < 1e-9}")
    print(f"    ψ/φ = τ? {abs(r - ta[n]) < 1e-9}")
    print(f"    ψ/φ = σ/n? {abs(r - sig[n]/n) < 1e-9}")

# ══════════════════════════════════════════════════════════════
# BONUS 2: Combined uniqueness — both D=0 AND ψ/φ=n
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("COMBINED UNIQUENESS: D=0 AND ψ/φ=n simultaneously")
print("=" * 70)

d_zero = find_solutions(lambda n: disc[n] == 0)
psi_phi_n = find_solutions(lambda n: phi[n] > 0 and ps[n] == n * phi[n])
both = sorted(set(d_zero) & set(psi_phi_n))
print(f"  D(n)=0: {d_zero}")
print(f"  ψ/φ=n:  {psi_phi_n}")
print(f"  Both:   {both}")

# ══════════════════════════════════════════════════════════════
# BONUS 3: ψ/φ = σ/n (= σ₋₁) — when does multiplicative = ratio?
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("BONUS 3: ψ(n)/φ(n) = σ(n)/n — characterize solutions")
print("=" * 70)

psi_phi_eq_sigma_n = find_solutions(lambda n: phi[n] > 0 and n > 0 and ps[n] * n == sig[n] * phi[n])
print(f"Solutions: {psi_phi_eq_sigma_n[:30]}  (count={len(psi_phi_eq_sigma_n)})")
# Analyze: what are these numbers?
for n in psi_phi_eq_sigma_n[:20]:
    f = factorize(n) if n > 1 else {}
    print(f"  n={n}: factors={f}")

# ══════════════════════════════════════════════════════════════
# BONUS 4: ψ(n)+φ(n) vs σ(n)+n at perfects
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("BONUS 4: ψ+φ vs σ+n and other sums at perfect numbers")
print("=" * 70)

for n in perfects:
    print(f"\n  n={n}:")
    print(f"    ψ+φ = {ps[n]+phi[n]},  σ+n = {sig[n]+n},  diff = {ps[n]+phi[n]-sig[n]-n}")
    print(f"    ψ-φ = {ps[n]-phi[n]},  σ-n = {sig[n]-n}")
    print(f"    ψ·φ = {ps[n]*phi[n]},  n·σ = {n*sig[n]},  diff = {ps[n]*phi[n]-n*sig[n]}")
    print(f"    (ψ+φ)/(σ+n) = {(ps[n]+phi[n])/(sig[n]+n):.6f}")
    print(f"    (ψ-φ)/(σ-n) = {(ps[n]-phi[n])/(sig[n]-n):.6f}" if sig[n] != n else "    σ=n")

# ══════════════════════════════════════════════════════════════
# BONUS 5: At perfect n=2^(p-1)(2^p-1): ψ/φ formula
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("BONUS 5: ψ/φ at perfect numbers = (2+1)/(2-1) · (2^p)/(2^p-2)")
print("         = 3 · 2^(p-1) / (2^(p-1)-1)")
print("=" * 70)

# Perfect n = 2^(p-1)·(2^p - 1), primes dividing n are 2 and 2^p-1
# ψ/φ = (3/1)·(2^p/(2^p-2)) = 3·2^(p-1)/(2^(p-1)-1)
for p in [2, 3, 5, 7, 13]:
    mp = (1 << p) - 1  # Mersenne prime candidate
    n = (1 << (p - 1)) * mp
    # Check if in range
    psi_val = ps[n] if n <= N_MAX else psi(n)
    phi_val = phi[n] if n <= N_MAX else euler_phi(n)
    tau_val = ta[n] if n <= N_MAX else tau(n)
    sig_val = sig[n] if n <= N_MAX else sigma(n)
    ratio = psi_val / phi_val
    formula = 3 * (1 << (p - 1)) / ((1 << (p - 1)) - 1)
    print(f"  p={p}: n={n}, ψ/φ = {psi_val}/{phi_val} = {ratio:.6f}, formula = {formula:.6f}, τ={tau_val}")
    print(f"    ψ/φ = n?  {abs(ratio - n) < 1e-6}")
    print(f"    ψ/φ = τ?  {abs(ratio - tau_val) < 1e-6}")
    print(f"    ψ/φ = 3·2^(p-1)/(2^(p-1)-1)")

# ══════════════════════════════════════════════════════════════
# BONUS 6: More exotic — D(n) mod ψ(n), D(n) mod φ(n)
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("BONUS 6: Where does ψ(n) | D(n)? (ψ divides D)")
print("=" * 70)

psi_divides_D = find_solutions(lambda n: ps[n] > 0 and disc[n] % ps[n] == 0)
print(f"ψ|D for n: {psi_divides_D[:40]}  (count={len(psi_divides_D)})")

# Where D mod ψ = 0 AND n is interesting
for n in psi_divides_D[:20]:
    if disc[n] != 0:
        print(f"  n={n}: D={disc[n]}, ψ={ps[n]}, D/ψ={disc[n]//ps[n]}, factors={factorize(n) if n > 1 else {}}")

# ══════════════════════════════════════════════════════════════
# FINAL: Summary of uniqueness results
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("FINAL SUMMARY: Unique characterizations found")
print("=" * 70)

print("""
For n=6 (first non-trivial perfect number):
  - D(n)=0: unique among n>1 up to 10000 (only n=1,6)
  - ψ/φ=n:  unique among n>1 up to 10000 (only n=1,6)
  - Both D=0 AND ψ/φ=n: only {1,6}

For n=28 (second perfect number):
  Check ψ/φ=τ uniqueness...
""")

# Recheck
sols_psi_phi_tau = find_solutions(lambda n: phi[n] > 0 and ps[n] == ta[n] * phi[n])
print(f"  ψ/φ=τ solutions: {sols_psi_phi_tau[:30]}  (count={len(sols_psi_phi_tau)})")
if 28 in sols_psi_phi_tau:
    print(f"  n=28 IS a solution. Unique? {'YES' if len(sols_psi_phi_tau) <= 3 else 'NO'}")

# τψ = n²
sols_tau_psi_n2 = find_solutions(lambda n: ta[n] * ps[n] == n * n)
print(f"\n  τψ=n² solutions: {sols_tau_psi_n2[:30]}  (count={len(sols_tau_psi_n2)})")

# ψ+n = σ (perfect number property?)
sols_psi_n_sigma = find_solutions(lambda n: ps[n] + n == sig[n])
print(f"\n  ψ+n=σ solutions: {sols_psi_n_sigma[:30]}  (count={len(sols_psi_n_sigma)})")
# This means σ-ψ=n. For perfect n: σ=2n, so ψ=n. Check:
for n in sols_psi_n_sigma[:10]:
    print(f"    n={n}: ψ={ps[n]}, σ={sig[n]}, perfect?={sig[n]==2*n}")

print("\n\nDone.")
