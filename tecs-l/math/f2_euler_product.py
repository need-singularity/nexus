#!/usr/bin/env python3
"""
Compute F(2) = Σ_{n≥1} R(n)/n² where R(n) = σ(n)φ(n)/(n·τ(n))

Key derivation:
  R is multiplicative, so F(s) has Euler product F(s) = Π_p E_p(s)

  Claimed closed form for local factor:
    E_p(2) = p·ln((p+1)/p) + 1/p

  We verify this numerically and compute F(2) = Π_p E_p(2).
"""

import math
import time
from functools import lru_cache

# ─── Part 1: Sieve-based direct computation of F(2) ───

def compute_F2_direct(N):
    """Compute Σ_{n=1}^{N} R(n)/n² directly using sieves."""
    # Sieve σ(n), φ(n), τ(n)
    sigma = [0] * (N + 1)   # sum of divisors
    phi = list(range(N + 1)) # Euler totient
    tau = [0] * (N + 1)      # number of divisors

    # Sieve tau and sigma
    for d in range(1, N + 1):
        for m in range(d, N + 1, d):
            tau[m] += 1
            sigma[m] += d

    # Sieve phi
    for p in range(2, N + 1):
        if phi[p] == p:  # p is prime
            for m in range(p, N + 1, p):
                phi[m] = phi[m] // p * (p - 1)

    # Compute sum
    total = 0.0
    for n in range(1, N + 1):
        R_n = sigma[n] * phi[n] / (n * tau[n])
        total += R_n / (n * n)

    return total

# ─── Part 2: Verify R(p^a) formula ───

def R_prime_power(p, a):
    """R(p^a) = σ(p^a)·φ(p^a) / (p^a · τ(p^a))"""
    if a == 0:
        return 1.0
    pa = p ** a
    sigma_pa = (p**(a+1) - 1) // (p - 1)
    phi_pa = pa - pa // p  # p^a - p^(a-1) = p^(a-1)(p-1)
    tau_pa = a + 1
    return sigma_pa * phi_pa / (pa * tau_pa)

def R_prime_power_formula(p, a):
    """Claimed: R(p^a) = (p^{a+1}-1)/(p(a+1)) for a≥1"""
    if a == 0:
        return 1.0
    return (p**(a+1) - 1) / (p * (a + 1))

# ─── Part 3: Verify E_p(2) local factor ───

def Ep_direct(p, terms=200):
    """E_p(2) = Σ_{a≥0} R(p^a)/p^{2a} computed directly."""
    total = 0.0
    for a in range(terms):
        total += R_prime_power(p, a) / p**(2*a)
    return total

def Ep_formula(p):
    """Claimed: E_p(2) = p·ln((p+1)/p) + 1/p"""
    return p * math.log((p + 1) / p) + 1.0 / p

def Ep_intermediate(p, terms=200):
    """E_p(2) via intermediate formulas A_p and B_p."""
    # A_p = p·ln(p/(p-1)) - 1
    A_p = p * math.log(p / (p - 1)) - 1
    # B_p = p²·ln(p²/(p²-1)) - 1
    B_p = p**2 * math.log(p**2 / (p**2 - 1)) - 1
    return 1 + A_p - B_p / p

# ─── Part 4: Prime sieve ───

def sieve_primes(limit):
    """Sieve of Eratosthenes."""
    is_prime = bytearray(b'\x01') * (limit + 1)
    is_prime[0] = is_prime[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, limit + 1, i):
                is_prime[j] = 0
    return [i for i in range(2, limit + 1) if is_prime[i]]

# ═══════════════════════════════════════════════════════
#  MAIN COMPUTATION
# ═══════════════════════════════════════════════════════

print("=" * 70)
print("F(2) = Σ_{n≥1} R(n)/n²  where R(n) = σ(n)φ(n)/(nτ(n))")
print("=" * 70)

# ─── Step 1: Verify R(p^a) formula ───
print("\n─── Step 1: Verify R(p^a) formula ───")
print(f"{'p':>4} {'a':>3} {'R(p^a) direct':>18} {'R(p^a) formula':>18} {'match':>8}")
print("-" * 55)
all_match = True
for p in [2, 3, 5, 7, 11, 13]:
    for a in range(0, 8):
        rd = R_prime_power(p, a)
        rf = R_prime_power_formula(p, a)
        match = abs(rd - rf) < 1e-12
        if not match:
            all_match = False
        if a <= 4 or not match:
            print(f"{p:4d} {a:3d} {rd:18.12f} {rf:18.12f} {'OK' if match else 'FAIL':>8}")
print(f"\nAll R(p^a) formulas match: {all_match}")

# ─── Step 2: Verify E_p(2) local factor ───
print("\n─── Step 2: Verify E_p(2) = p·ln((p+1)/p) + 1/p ───")
print(f"{'p':>4} {'E_p direct':>18} {'E_p formula':>18} {'E_p intermed':>18} {'err(formula)':>14}")
print("-" * 76)
for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
    ed = Ep_direct(p, terms=300)
    ef = Ep_formula(p)
    ei = Ep_intermediate(p, terms=300)
    err = abs(ed - ef)
    print(f"{p:4d} {ed:18.15f} {ef:18.15f} {ei:18.15f} {err:14.2e}")

# ─── Step 3: Verify intermediate step ───
print("\n─── Step 3: Verify algebra step by step for p=2 ───")
p = 2
print(f"  A_p = Σ_{{a≥1}} 1/(p^a(a+1)) = p·ln(p/(p-1)) - 1")
A_num = sum(1/(p**a * (a+1)) for a in range(1, 300))
A_formula = p * math.log(p/(p-1)) - 1
print(f"  A_2 numeric  = {A_num:.15f}")
print(f"  A_2 formula  = {A_formula:.15f}")
print(f"  error        = {abs(A_num - A_formula):.2e}")

print(f"\n  B_p = Σ_{{a≥1}} 1/(p^{{2a}}(a+1)) = p²·ln(p²/(p²-1)) - 1")
B_num = sum(1/(p**(2*a) * (a+1)) for a in range(1, 300))
B_formula = p**2 * math.log(p**2/(p**2-1)) - 1
print(f"  B_2 numeric  = {B_num:.15f}")
print(f"  B_2 formula  = {B_formula:.15f}")
print(f"  error        = {abs(B_num - B_formula):.2e}")

print(f"\n  E_p(2) = 1 + A_p - B_p/p")
E_intermediate = 1 + A_formula - B_formula / p
print(f"  E_2 intermed = {E_intermediate:.15f}")
print(f"  E_2 formula  = {Ep_formula(2):.15f}")
print(f"  E_2 direct   = {Ep_direct(2, 300):.15f}")

print(f"\n  Simplification check:")
print(f"  p·[ln(p/(p-1)) - ln(p²/(p²-1))]")
val1 = p * (math.log(p/(p-1)) - math.log(p**2/(p**2-1)))
print(f"  = p·ln[(p/(p-1))·(p²-1)/p²]")
val2 = p * math.log((p/(p-1)) * (p**2-1)/p**2)
print(f"  = p·ln[(p+1)/p]")
val3 = p * math.log((p+1)/p)
print(f"  val1 = {val1:.15f}")
print(f"  val2 = {val2:.15f}")
print(f"  val3 = {val3:.15f}")
print(f"  All equal: {abs(val1-val2) < 1e-15 and abs(val2-val3) < 1e-15}")

# ─── Step 4: Direct sum F(2) for various N ───
print("\n─── Step 4: Direct sum F(2) = Σ_{n=1}^{N} R(n)/n² ───")
for N in [1000, 10000, 50000]:
    t0 = time.time()
    val = compute_F2_direct(N)
    dt = time.time() - t0
    print(f"  N = {N:>6d}: F(2) ≈ {val:.12f}  ({dt:.1f}s)")

# ─── Step 5: Euler product F(2) = Π_p E_p(2) ───
print("\n─── Step 5: Euler product F(2) = Π_p [p·ln((p+1)/p) + 1/p] ───")

# Generate primes
t0 = time.time()
primes_big = sieve_primes(1500000)  # ~114K primes
print(f"  Sieved {len(primes_big)} primes up to {primes_big[-1]} ({time.time()-t0:.1f}s)")

milestones = [100, 1000, 10000, 50000, 100000, len(primes_big)]
product = 1.0
log_product = 0.0  # use log to avoid overflow/underflow
idx = 0

print(f"\n  {'#primes':>8} {'max p':>8} {'Π E_p(2)':>20} {'log Π':>18}")
print("  " + "-" * 60)

for i, p in enumerate(primes_big):
    ep = Ep_formula(p)
    log_product += math.log(ep)

    if idx < len(milestones) and i + 1 == milestones[idx]:
        product_val = math.exp(log_product)
        print(f"  {i+1:8d} {p:8d} {product_val:20.15f} {log_product:18.15f}")
        idx += 1

F2_euler = math.exp(log_product)

# ─── Step 6: Compare direct sum vs Euler product ───
print("\n─── Step 6: Comparison ───")
F2_direct_50k = compute_F2_direct(50000)
print(f"  Direct sum   (N=50000):  {F2_direct_50k:.12f}")
print(f"  Euler product (114K p):  {F2_euler:.12f}")

# The direct sum misses tail; estimate tail contribution
# For n > N, R(n)/n² ~ C/n² on average, tail ~ C/N
# The Euler product should be more accurate
print(f"  Difference:              {F2_euler - F2_direct_50k:.6e}")

# ─── Step 7: Try to identify the constant ───
print("\n─── Step 7: Identify F(2) ───")
F2 = F2_euler
print(f"  F(2) ≈ {F2:.15f}")
print()

# Check against known constants
candidates = [
    ("π²/4", math.pi**2 / 4),
    ("π²/6", math.pi**2 / 6),
    ("e", math.e),
    ("π/√6", math.pi / math.sqrt(6)),
    ("3/2", 1.5),
    ("ln(2)·π", math.log(2) * math.pi),
    ("π²/6 · 6/π²", 1.0),
    ("2·ln(2)", 2 * math.log(2)),
    ("√e", math.sqrt(math.e)),
    ("π/2", math.pi / 2),
    ("(π²/6)·(6/π²)·F2_correction", 0),
    ("ln(π)", math.log(math.pi)),
    ("γ + 1", 0.5772156649 + 1),
    ("1/ln(2)", 1/math.log(2)),
    ("π²/4 - 1", math.pi**2/4 - 1),
    ("5/2 - 1/π", 2.5 - 1/math.pi),
    ("e/√(2π)·something", 0),
    ("2.5", 2.5),
    ("5/2", 2.5),
    ("ln(12)", math.log(12)),
    ("ζ(2)·ζ(3)/ζ(6)", 0),  # placeholder
]

# More systematic: try a/b for small a, b
print("  Checking simple fractions a/b:")
best_frac = None
best_err = 1.0
for b in range(1, 50):
    for a in range(1, 200):
        if abs(a/b - F2) < best_err:
            best_err = abs(a/b - F2)
            best_frac = (a, b)
            if best_err < 0.001:
                print(f"    {a}/{b} = {a/b:.10f}  err = {best_err:.6e}")

# Check a·π^k / b, a·e^k / b, a·ln(b)/c patterns
print("\n  Checking a·π²/b:")
for b in range(1, 30):
    for a in range(1, 30):
        val = a * math.pi**2 / b
        if abs(val - F2) < 0.001:
            print(f"    {a}π²/{b} = {val:.10f}  err = {abs(val-F2):.6e}")

print("\n  Checking combinations with ζ(2)=π²/6:")
zeta2 = math.pi**2 / 6
for a in range(1, 20):
    for b in range(1, 20):
        val = a * zeta2 / b
        if abs(val - F2) < 0.01:
            print(f"    {a}·ζ(2)/{b} = {val:.10f}  err = {abs(val-F2):.6e}")

print("\n  Checking p·ln(q/r) + s/t patterns:")
for q in range(2, 10):
    for r in range(1, q):
        val = math.log(q/r)
        if abs(val - F2) < 0.1:
            print(f"    ln({q}/{r}) = {val:.10f}  err = {abs(val-F2):.6e}")
        for mult_n in range(1, 10):
            for mult_d in range(1, 10):
                val2 = mult_n * math.log(q/r) / mult_d
                if abs(val2 - F2) < 0.005:
                    print(f"    {mult_n}·ln({q}/{r})/{mult_d} = {val2:.10f}  err = {abs(val2-F2):.6e}")

# ─── Step 8: High-precision Euler product with mpmath ───
print("\n─── Step 8: High-precision computation with mpmath ───")
try:
    from mpmath import mp, mpf, log, exp, fsum
    mp.dps = 50  # 50 decimal digits

    log_prod = mpf(0)
    for p in primes_big:
        p_mp = mpf(p)
        ep = p_mp * log((p_mp + 1) / p_mp) + 1 / p_mp
        log_prod += log(ep)

    F2_hp = exp(log_prod)
    print(f"  F(2) [mpmath, {len(primes_big)} primes] = {F2_hp}")

    # Also check: what is F(2) / ζ(2)?
    from mpmath import zeta
    z2 = zeta(2)
    z3 = zeta(3)
    z4 = zeta(4)
    z6 = zeta(6)
    ratio_z2 = F2_hp / z2
    ratio_z3 = F2_hp / z3
    print(f"  ζ(2)  = {z2}")
    print(f"  ζ(3)  = {z3}")
    print(f"  F(2)/ζ(2) = {ratio_z2}")
    print(f"  F(2)/ζ(3) = {ratio_z3}")
    print(f"  F(2)·6/π² = {F2_hp * 6 / (mp.pi**2)}")
    print(f"  F(2)/π    = {F2_hp / mp.pi}")
    print(f"  F(2)/e    = {F2_hp / mp.e}")
    print(f"  F(2)²     = {F2_hp**2}")
    print(f"  ln(F(2))  = {log(F2_hp)}")

    # Check if F(2) = ζ(2)·Π_p(1 - 1/p²)·something
    # Since ζ(2) = Π_p 1/(1-1/p²), we have Π_p(1-1/p²) = 6/π²
    # F(2)/ζ(2) tells us the "correction factor"

    print(f"\n  Ratio analysis:")
    print(f"  F(2) / (15/ζ(2)) = {F2_hp * z2 / 15}")
    print(f"  F(2) · ζ(2)      = {F2_hp * z2}")

except ImportError:
    print("  mpmath not available, skipping high-precision computation")

# ─── Step 9: Convergence analysis ───
print("\n─── Step 9: Convergence of Euler product ───")
print("  Each factor E_p(2) for large p:")
print("  E_p(2) = p·ln(1+1/p) + 1/p")
print("         = p·[1/p - 1/(2p²) + 1/(3p³) - ...] + 1/p")
print("         = 1 - 1/(2p) + 1/(3p²) - ... + 1/p")
print("         = 1 + 1/(2p) + 1/(3p²) - 1/(4p³) + ...")
print()

# Verify expansion
for p in [2, 3, 5, 7, 101, 1009]:
    ep = Ep_formula(p)
    approx1 = 1 + 1/(2*p)
    approx2 = 1 + 1/(2*p) + 1/(3*p**2)
    approx3 = 1 + 1/(2*p) + 1/(3*p**2) - 1/(4*p**3)
    print(f"  p={p:5d}: E_p = {ep:.12f}, 1+1/2p = {approx1:.12f}, "
          f"+1/3p² = {approx2:.12f}, -1/4p³ = {approx3:.12f}")

print("\n  Since ln(E_p) ~ 1/(2p) for large p,")
print("  and Σ_p 1/(2p) diverges, the product diverges!")
print("  Wait — let's check: does the product converge?")

# Actually check convergence
print("\n  Checking: does Π E_p converge?")
print("  ln(E_p(2)) for large p:")
for p in [101, 1009, 10007, 100003, 1000003]:
    ep = p * math.log((p+1)/p) + 1/p
    lep = math.log(ep)
    print(f"  p={p:>8d}: ln(E_p) = {lep:.10e} ~ 1/(2p) = {1/(2*p):.10e}")

print("\n  ln(E_p) ~ 1/(2p), and Σ_p 1/p diverges (Mertens).")
print("  Therefore Π_p E_p(2) DIVERGES.")
print("  This means F(2) = Σ R(n)/n² DIVERGES... let's verify!")

# ─── Step 10: Check if direct sum is growing ───
print("\n─── Step 10: Growth check of direct sum ───")
for N in [100, 500, 1000, 5000, 10000, 50000]:
    t0 = time.time()
    val = compute_F2_direct(N)
    dt = time.time() - t0
    print(f"  N = {N:>6d}: Σ = {val:.10f}  (Σ/ln(ln(N)) = {val/math.log(math.log(N)):.6f})  ({dt:.1f}s)")

print("\n  If divergent, Σ should grow like C·ln(ln(N)) or similar.")
print("  If convergent, Σ should stabilize.")

# ─── Step 11: More careful analysis ───
print("\n─── Step 11: Average order of R(n) ───")
# R(n) = σ(n)φ(n)/(n·τ(n))
# Average of σ(n)/n ~ π²/6, average of φ(n)/n ~ 6/π²
# Average of 1/τ(n) ~ C/√(ln n)
# So average R(n) ~ C'/√(ln n)
# Then Σ R(n)/n² ~ Σ C'/(n²√(ln n)) which converges!
# But the Euler product argument says it diverges...
# There must be an error. Let me recheck.

print("  Checking R(p^a) formula more carefully...")
print()
print("  R(n) = σ(n)·φ(n) / (n·τ(n))")
print()
for p in [2, 3, 5]:
    for a in [1, 2, 3, 4]:
        pa = p**a
        sigma_val = sum(p**k for k in range(a+1))
        phi_val = pa - pa//p
        tau_val = a + 1
        R_direct = sigma_val * phi_val / (pa * tau_val)
        R_formula = (p**(a+1) - 1) / (p * (a+1))
        print(f"  p={p}, a={a}: σ={sigma_val}, φ={phi_val}, τ={tau_val}, "
              f"R_direct={R_direct:.6f}, formula={R_formula:.6f}, "
              f"match={abs(R_direct-R_formula)<1e-10}")

print("\n  Wait — R(p^a) = σ(p^a)·φ(p^a) / (p^a · τ(p^a))")
print("  σ(p^a) = (p^{a+1}-1)/(p-1)")
print("  φ(p^a) = p^{a-1}(p-1)")
print("  τ(p^a) = a+1")
print("  R(p^a) = [(p^{a+1}-1)/(p-1)] · [p^{a-1}(p-1)] / [p^a · (a+1)]")
print("         = (p^{a+1}-1) · p^{a-1} / [p^a · (a+1)]")
print("         = (p^{a+1}-1) / [p · (a+1)]")
print("  ✓ Formula confirmed")

print("\n  Now E_p(2) = Σ_{a≥0} R(p^a) / p^{2a}")
print("  = 1 + Σ_{a≥1} (p^{a+1}-1) / [p(a+1) · p^{2a}]")
print("  = 1 + Σ_{a≥1} (p^{a+1}-1) / [p^{2a+1}(a+1)]")
print("  = 1 + Σ_{a≥1} [p^{a+1}/(p^{2a+1}(a+1)) - 1/(p^{2a+1}(a+1))]")
print("  = 1 + Σ_{a≥1} [1/(p^a(a+1)) - 1/(p^{2a+1}(a+1))]")
print("  = 1 + A_p - B_p/p")
print()
print("  A_p = Σ_{a≥1} 1/(p^a(a+1))")
print("  Let t = 1/p. Then A_p = Σ_{a≥1} t^a/(a+1)")
print("  = (1/t)·Σ_{a≥1} t^{a+1}/(a+1)")
print("  = (1/t)·[Σ_{k≥2} t^k/k]")
print("  = (1/t)·[-ln(1-t) - t]")
print("  = -ln(1-t)/t - 1")
print("  = -p·ln(1-1/p) - 1")
print("  = p·ln(p/(p-1)) - 1  ✓")
print()
print("  B_p = Σ_{a≥1} 1/(p^{2a}(a+1))")
print("  Same with t = 1/p²:")
print("  = -p²·ln(1-1/p²) - 1")
print("  = p²·ln(p²/(p²-1)) - 1  ✓")
print()
print("  E_p = 1 + [p·ln(p/(p-1))-1] - [p²·ln(p²/(p²-1))-1]/p")
print("      = p·ln(p/(p-1)) - p·ln(p²/(p²-1)) + 1/p")
print()
print("  Key simplification:")
print("  p·[ln(p/(p-1)) - ln(p²/(p²-1))]")
print("  = p·ln[(p/(p-1)) · (p²-1)/p²]")
print("  = p·ln[(p/(p-1)) · (p-1)(p+1)/p²]")
print("  = p·ln[(p+1)/p]  ✓")
print()
print("  So E_p(2) = p·ln((p+1)/p) + 1/p  ✓")
print()
print("  Expansion for large p:")
print("  p·ln(1+1/p) = p·[1/p - 1/(2p²) + 1/(3p³) - ...]")
print("              = 1 - 1/(2p) + 1/(3p²) - 1/(4p³) + ...")
print("  Plus 1/p:    E_p = 1 + 1/(2p) + 1/(3p²) - 1/(4p³) + ...")
print()
print("  ln(E_p) = 1/(2p) + O(1/p²)")
print("  Σ_p ln(E_p) ~ Σ_p 1/(2p) → ∞  (diverges by Mertens)")

print("\n  BUT the direct sum appears to converge!")
print("  RESOLUTION: R(n) is NOT multiplicative in the standard sense!")
print("  Let's check: R(6) vs R(2)·R(3)")

# Check multiplicativity
n_vals = [(2,3), (2,5), (3,5), (2,7), (3,7), (4,9), (6,5)]
print(f"\n  {'m':>4} {'n':>4} {'R(m)':>10} {'R(n)':>10} {'R(mn)':>10} {'R(m)R(n)':>10} {'mult?':>8}")
print("  " + "-" * 58)

# Need actual R function
def sigma_n(n):
    s = 0
    for d in range(1, n+1):
        if n % d == 0:
            s += d
    return s

def phi_n(n):
    count = 0
    for k in range(1, n+1):
        if math.gcd(k, n) == 1:
            count += 1
    return count

def tau_n(n):
    count = 0
    for d in range(1, n+1):
        if n % d == 0:
            count += 1
    return count

def R(n):
    if n == 1:
        return 1.0
    return sigma_n(n) * phi_n(n) / (n * tau_n(n))

for m, n in n_vals:
    if math.gcd(m, n) == 1:
        rm = R(m)
        rn = R(n)
        rmn = R(m * n)
        prod = rm * rn
        is_mult = abs(rmn - prod) < 1e-10
        print(f"  {m:4d} {n:4d} {rm:10.6f} {rn:10.6f} {rmn:10.6f} {prod:10.6f} {'YES' if is_mult else 'NO':>8}")

print("\n═══ CONCLUSION ═══")
print("If R is multiplicative → Euler product is valid → but product diverges")
print("If R is NOT multiplicative → Euler product is invalid")
print("The direct sum tells us which is true.")

print("\n" + "=" * 70)
print("DONE")
print("=" * 70)
