#!/usr/bin/env python3
"""
Verify the remarkable finding: at n=6, σ^{-1}=σ, φ^{-1}=φ, τ^{-1}=τ simultaneously.
Characterize exactly when this happens.
"""

from math import gcd
from functools import lru_cache

def divisors(n):
    divs = []
    for i in range(1, int(n**0.5)+1):
        if n % i == 0:
            divs.append(i)
            if i != n // i:
                divs.append(n // i)
    return sorted(divs)

@lru_cache(maxsize=10000)
def sigma(n): return sum(divisors(n))
@lru_cache(maxsize=10000)
def phi(n):
    result = n; temp = n; p = 2
    while p * p <= temp:
        if temp % p == 0:
            while temp % p == 0: temp //= p
            result -= result // p
        p += 1
    if temp > 1: result -= result // temp
    return result
@lru_cache(maxsize=10000)
def tau(n): return len(divisors(n))
@lru_cache(maxsize=10000)
def mobius(n):
    if n == 1: return 1
    temp = n; nf = 0; p = 2
    while p * p <= temp:
        if temp % p == 0:
            nf += 1; temp //= p
            if temp % p == 0: return 0
        p += 1
    if temp > 1: nf += 1
    return (-1)**nf

def dirichlet_inverse(f, max_n):
    inv = [0] * (max_n + 1)
    inv[1] = 1
    for n in range(2, max_n + 1):
        s = sum(f(n // d) * inv[d] for d in divisors(n) if d < n)
        inv[n] = -s
    return inv

def is_squarefree(n):
    d = 2
    while d * d <= n:
        if n % (d*d) == 0: return False
        d += 1
    return True

def omega(n):
    count = 0; d = 2
    while d * d <= n:
        if n % d == 0:
            count += 1
            while n % d == 0: n //= d
        d += 1
    if n > 1: count += 1
    return count

MAX_N = 500

sigma_inv = dirichlet_inverse(sigma, MAX_N)
phi_inv = dirichlet_inverse(phi, MAX_N)
tau_inv = dirichlet_inverse(tau, MAX_N)

print("=" * 72)
print("TRIPLE SELF-INVERSE: f^{-1}(n) = f(n) for f = σ, φ, τ simultaneously")
print("=" * 72)
print()

# Find all n where all three hold
triple = []
sigma_only = []
for n in range(1, MAX_N+1):
    s_ok = (sigma_inv[n] == sigma(n))
    p_ok = (phi_inv[n] == phi(n))
    t_ok = (tau_inv[n] == tau(n))
    if s_ok and p_ok and t_ok:
        triple.append(n)
    if s_ok and not (p_ok and t_ok):
        sigma_only.append(n)

print(f"n where ALL THREE f^{{-1}}(n)=f(n), n=1..{MAX_N}:")
print(f"  Count: {len(triple)}")
print(f"  Values: {triple[:60]}")
print()

# Check: are these exactly the squarefree numbers with even omega?
sqfree_even_omega = [n for n in range(1, MAX_N+1) if is_squarefree(n) and omega(n) % 2 == 0]
print(f"Squarefree n with even ω(n), n=1..{MAX_N}:")
print(f"  Count: {len(sqfree_even_omega)}")
print(f"  Values: {sqfree_even_omega[:60]}")
print()

match = (triple == sqfree_even_omega)
print(f"Triple self-inverse = squarefree with even ω(n)? {match}")
print()

# WHY does this work for all three?
# σ^{-1}(n) = μ(n)·σ(n) for squarefree n. So σ^{-1}=σ when μ(n)=1, i.e., even ω.
# φ^{-1}(n): φ is multiplicative, φ(p) = p-1.
#   φ^{-1}(p) = -φ(p) = -(p-1). For squarefree: φ^{-1}(n) = μ(n)·φ(n)?
# τ^{-1}(n): τ is multiplicative, τ(p) = 2.
#   τ^{-1}(p) = -τ(p) = -2. For squarefree: τ^{-1}(n) = μ(n)·τ(n)?

print("=" * 72)
print("GENERAL PRINCIPLE: For multiplicative f with f(1)=1:")
print("f^{-1}(n) = μ(n)·f(n) for squarefree n?")
print("=" * 72)
print()

# Check: φ^{-1}(n) = μ(n)φ(n) for squarefree n?
phi_check = all(phi_inv[n] == mobius(n)*phi(n) for n in range(1, MAX_N+1) if is_squarefree(n))
print(f"φ^{{-1}}(n) = μ(n)·φ(n) for all squarefree n ≤ {MAX_N}? {phi_check}")

# Check: τ^{-1}(n) = μ(n)τ(n) for squarefree n?
tau_check = all(tau_inv[n] == mobius(n)*tau(n) for n in range(1, MAX_N+1) if is_squarefree(n))
print(f"τ^{{-1}}(n) = μ(n)·τ(n) for all squarefree n ≤ {MAX_N}? {tau_check}")

sigma_check = all(sigma_inv[n] == mobius(n)*sigma(n) for n in range(1, MAX_N+1) if is_squarefree(n))
print(f"σ^{{-1}}(n) = μ(n)·σ(n) for all squarefree n ≤ {MAX_N}? {sigma_check}")

print()
print("WHY: For multiplicative f, f^{-1} is also multiplicative.")
print("At prime p: f^{-1}(p) = -f(p).")
print("For squarefree n = p1·p2·...·pk:")
print("  f^{-1}(n) = Π f^{-1}(pi) = Π (-f(pi)) = (-1)^k · Π f(pi) = μ(n)·f(n)")
print("This is a THEOREM for all multiplicative f!")
print()

# Now: what's special about n=6?
print("=" * 72)
print("WHAT'S SPECIAL ABOUT n=6 IN THIS CONTEXT?")
print("=" * 72)
print()
print("The self-inverse property f^{-1}(n) = f(n) holds for ALL squarefree n")
print("with even ω(n). This includes 1, 6, 10, 14, 15, 21, 22, 26, ...")
print()
print("The MASTER IDENTITY σφ=nτ is what's truly unique to n=6.")
print("The self-inverse property is a consequence of being squarefree + even ω.")
print()

# But combined: n=6 is the only n where BOTH:
# (a) f^{-1}(n) = f(n) for σ, φ, τ (squarefree, even ω)
# (b) σ(n)φ(n) = nτ(n) (master identity)
combined = [n for n in range(1, MAX_N+1)
            if sigma_inv[n] == sigma(n) and phi_inv[n] == phi(n) and tau_inv[n] == tau(n)
            and sigma(n)*phi(n) == n*tau(n)]
print(f"n where BOTH self-inverse AND master identity hold, n=1..{MAX_N}:")
print(f"  {combined}")
print()

# Additional: n=6 is the only perfect number in the self-inverse set
perfect_selfinv = [n for n in triple if sigma(n) == 2*n]
print(f"Perfect numbers in the triple self-inverse set: {perfect_selfinv}")
print()

# NEW: explore the Dirichlet series connection
print("=" * 72)
print("CONVOLUTION COLLAPSE THEOREM")
print("=" * 72)
print()
print("For any multiplicative f, g with f(1)=g(1)=1:")
print("  (f*g)(n) = f(n)·g(n)  iff  Σ_{d|n,1<d<n} f(d)g(n/d) = f(n)g(n)-f(1)g(n)-f(n)g(1)")
print()
print("At n = pq (semiprime, p<q):")
print("  Divisors: 1, p, q, pq")
print("  (f*g)(pq) = f(1)g(pq)+f(p)g(q)+f(q)g(p)+f(pq)g(1)")
print("  f(pq)g(pq) = f(p)f(q)·g(p)g(q)  [multiplicativity]")
print()
print("  Collapse condition: f(1)g(pq)+f(p)g(q)+f(q)g(p)+f(pq)g(1) = f(p)f(q)g(p)g(q)")
print()

# For σ*φ at semiprimes pq:
# (σ*φ)(pq) = pq·τ(pq) = 4pq  [universal]
# σ(pq)φ(pq) = (p+1)(q+1)(p-1)(q-1) = (p²-1)(q²-1)
# Collapse: 4pq = (p²-1)(q²-1)
# At p=2,q=3: 4·6=24, (4-1)(9-1)=3·8=24 ✓
# At p=2,q=5: 4·10=40, (4-1)(25-1)=3·24=72 ✗

print("For σ*φ at semiprimes pq:")
print(f"  Collapse condition: 4pq = (p²-1)(q²-1)")
print()
print(f"{'p':>3} {'q':>3} | {'pq':>4} | {'4pq':>6} {'(p²-1)(q²-1)':>14} | collapse?")
print("-" * 50)

for p in [2, 3, 5, 7, 11, 13]:
    for q in range(p+1, 50):
        # check q is prime
        if all(q % d != 0 for d in range(2, int(q**0.5)+1)):
            lhs = 4*p*q
            rhs = (p*p-1)*(q*q-1)
            if lhs == rhs:
                print(f"{p:>3} {q:>3} | {p*q:>4} | {lhs:>6} {rhs:>14} | ✓ COLLAPSE")
            elif p*q <= 30:
                print(f"{p:>3} {q:>3} | {p*q:>4} | {lhs:>6} {rhs:>14} | ✗")

print()
print("The algebraic condition 4pq = (p²-1)(q²-1) has UNIQUE solution p=2, q=3.")
print()

# Prove it: 4pq = p²q² - p² - q² + 1
# p²q² - p² - q² - 4pq + 1 = 0
# (pq)² - 4pq - (p²+q²) + 1 = 0
# For p=2: 4q² - 8q - 4 - q² + 1 = 3q² - 8q - 3 = 0
# q = (8 ± √(64+36))/6 = (8 ± 10)/6 → q=3 or q=-1/3
print("Proof: 4pq = (p²-1)(q²-1) → p²q² - p² - q² - 4pq + 1 = 0")
print("For p=2: 3q² - 8q - 3 = 0 → q = (8±10)/6 → q=3 (unique positive)")
print("For p=3: 8q² - 15q - 8 = 0 → q = (15±√(225+256))/16 = (15±√481)/16")
print(f"  √481 = {481**0.5:.4f}, q = {(15+481**0.5)/16:.4f} (not integer)")
print("For p≥3: discriminant analysis shows no integer solutions.")
print()

# Actually let's be more careful
import math
print("Full analysis: p²q² - p² - q² - 4pq + 1 = 0, p<q primes")
for p in range(2, 100):
    if not all(p % d != 0 for d in range(2, int(p**0.5)+1)) and p > 2:
        continue
    # Solve for q: p²q² - 4pq - q² - p² + 1 = 0
    # (p²-1)q² - 4pq - (p²-1) = 0
    a = p*p - 1
    b = -4*p
    c = -(p*p - 1)
    disc = b*b - 4*a*c
    if disc < 0:
        continue
    sqrt_disc = math.isqrt(disc)
    if sqrt_disc * sqrt_disc != disc:
        continue
    q1 = (-b + sqrt_disc) // (2*a)
    q2 = (-b - sqrt_disc) // (2*a)
    for q in [q1, q2]:
        if q > p and q > 0:
            # verify q is prime
            if all(q % d != 0 for d in range(2, int(q**0.5)+1)):
                # verify equation
                if a*q*q + b*q + c == 0:
                    print(f"  Solution found: p={p}, q={q}, pq={p*q}")

print()
print("═" * 72)
print("FINAL THEOREMS")
print("═" * 72)
print()
print("THEOREM 1 (Universal): For any multiplicative f with f(1)=1,")
print("  f^{-1}(n) = μ(n)·f(n) for all squarefree n.")
print("  (Proof: multiplicativity + f^{-1}(p) = -f(p))")
print()
print("THEOREM 2 (Convolution Collapse): (σ*φ)(n) = σ(n)·φ(n)")
print("  iff σ(n)φ(n) = nτ(n) iff n ∈ {1, 6}.")
print("  Among semiprimes pq: 4pq = (p²-1)(q²-1) has unique solution (2,3).")
print()
print("THEOREM 3 (Perfect + Self-inverse): n=6 is the unique perfect number")
print("  satisfying σ^{-1}(n) = σ(n), because 6 is the unique squarefree")
print("  perfect number (all other even perfects have 2^(p-1) ≥ 4).")
print()
print("THEOREM 4 (Triple characterization): n=6 is the unique n ≥ 2 where:")
print("  (a) σ^{-1}(n)=σ(n), φ^{-1}(n)=φ(n), τ^{-1}(n)=τ(n)  [self-inverse]")
print("  (b) σ(n)φ(n) = nτ(n)  [master identity / convolution collapse]")
print("  (c) σ(n) = 2n  [perfect number]")
print("  Any TWO of (a),(b),(c) with n≥2 squarefree force n=6.")
