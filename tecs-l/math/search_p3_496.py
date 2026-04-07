#!/usr/bin/env python3
"""
Systematic search for P3=496 as "shadow" in n=6 identities.
Compare with H-CROSS-2 result: P2=28 appears 26 times (14.6% density).
"""

import math
from fractions import Fraction
from functools import reduce

TARGET = 496
P2 = 28
P1 = 6

results = []  # (domain, formula, value, note)

# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────

def sigma(n):
    """Sum of all divisors."""
    s = 0
    for i in range(1, int(n**0.5) + 1):
        if n % i == 0:
            s += i
            if i != n // i:
                s += n // i
    return s

def sigma_k(n, k):
    """Sum of k-th powers of divisors."""
    return sum(d**k for d in range(1, n+1) if n % d == 0)

def tau(n):
    """Number of divisors."""
    return sum(1 for i in range(1, n+1) if n % i == 0)

def phi(n):
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

def moebius(n):
    """Möbius function."""
    if n == 1:
        return 1
    factors = []
    temp = n
    p = 2
    while p * p <= temp:
        if temp % p == 0:
            factors.append(p)
            temp //= p
            if temp % p == 0:
                return 0
        p += 1
    if temp > 1:
        factors.append(temp)
    return (-1)**len(factors)

def cyclotomic(n, x=1):
    """Cyclotomic polynomial Phi_n(x) evaluated at x using explicit formula."""
    # For small n, use known formulas:
    # Phi_1(x) = x-1
    # Phi_2(x) = x+1
    # Phi_3(x) = x^2+x+1
    # Phi_4(x) = x^2+1
    # Phi_5(x) = x^4+x^3+x^2+x+1
    # Phi_6(x) = x^2-x+1
    # Phi_n for prime p: x^(p-1)+...+1
    # Use Mobius-based formula carefully
    from fractions import Fraction
    # Compute as ratio of polynomials at x
    # Phi_n(x) = prod_{d|n} (x^d - 1)^{mu(n/d)}
    # Separate numerator and denominator
    num = 1
    den = 1
    for d in range(1, n+1):
        if n % d == 0:
            val = x**d - 1
            if val == 0:
                # x is a primitive d-th root of unity; use L'Hopital / limit
                # For x=1: Phi_n(1) = 1 if n not prime-power, = p if n=p^k
                # Just use a small perturbation or known formula
                raise ValueError(f"x={x} is a root of x^{d}-1, use limit formula")
            m = moebius(n // d)
            if m == 1:
                num *= val
            elif m == -1:
                den *= val
    return num // den

def bernoulli(n):
    """Bernoulli numbers B_n as fractions."""
    B = [Fraction(0)] * (n+1)
    B[0] = Fraction(1)
    for m in range(1, n+1):
        s = sum(math.comb(m+1, k) * B[k] for k in range(m))
        B[m] = -s / (m+1)
    return B[n]

def catalan(n):
    return math.comb(2*n, n) // (n+1)

def bell(n):
    """Bell number B_n."""
    tri = [[0]*(n+2) for _ in range(n+2)]
    tri[0][0] = 1
    for i in range(1, n+1):
        tri[i][0] = tri[i-1][i-1]
        for j in range(1, i+1):
            tri[i][j] = tri[i][j-1] + tri[i-1][j-1]
    return tri[n][0]

def stirling2(n, k):
    """Stirling numbers of the second kind."""
    if n == 0 and k == 0:
        return 1
    if n == 0 or k == 0:
        return 0
    return k * stirling2(n-1, k) + stirling2(n-1, k-1)

def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a+b
    return a

def lucas(n):
    a, b = 2, 1
    for _ in range(n):
        a, b = b, a+b
    return a

def pell(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, 2*b+a
    return a

def triangular(n):
    return n*(n+1)//2

def square(n):
    return n*n

def pentagonal(n):
    return n*(3*n-1)//2

def hexagonal(n):
    return n*(2*n-1)

def primes_up_to(n):
    sieve = [True]*(n+1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(n**0.5)+1):
        if sieve[i]:
            for j in range(i*i, n+1, i):
                sieve[j] = False
    return [i for i in range(2, n+1) if sieve[i]]

def nth_prime(n):
    """1-indexed."""
    primes = []
    candidate = 2
    while len(primes) < n:
        if all(candidate % p != 0 for p in primes):
            primes.append(candidate)
        candidate += 1
    return primes[-1]

def check(domain, formula, value, note=""):
    hit = (value == TARGET)
    results.append({
        "domain": domain,
        "formula": formula,
        "value": value,
        "hit": hit,
        "note": note
    })
    if hit:
        print(f"  *** HIT *** {domain}: {formula} = {value}  [{note}]")

# ─────────────────────────────────────────
# 1. SIGMA CHAIN from n=6
# ─────────────────────────────────────────
print("\n=== 1. SIGMA CHAIN FROM n=6 ===")
chain = [6]
v = 6
for _ in range(20):
    v = sigma(v)
    chain.append(v)
    if v > 10**9:
        break
print("sigma^k(6):", chain[:15])
for i, v in enumerate(chain):
    check("Sigma Chain", f"sigma^{i}(6)", v, f"k={i}")

# ─────────────────────────────────────────
# 2. sigma_k(6) for various k
# ─────────────────────────────────────────
print("\n=== 2. sigma_k(6) FOR VARIOUS k ===")
for k in range(0, 10):
    v = sigma_k(6, k)
    print(f"  sigma_{k}(6) = {v}")
    check("sigma_k(6)", f"sigma_{k}(6)", v)

# ─────────────────────────────────────────
# 3. SEQUENCES AT INDEX 6
# ─────────────────────────────────────────
print("\n=== 3. SEQUENCES AT INDEX n=6 ===")
seqs = {
    "Fibonacci(n)":   [(i, fib(i)) for i in range(1, 50)],
    "Lucas(n)":       [(i, lucas(i)) for i in range(1, 50)],
    "Pell(n)":        [(i, pell(i)) for i in range(1, 50)],
    "Bell(n)":        [(i, bell(i)) for i in range(1, 20)],
    "Catalan(n)":     [(i, catalan(i)) for i in range(1, 20)],
    "Triangular(n)":  [(i, triangular(i)) for i in range(1, 100)],
    "Square(n)":      [(i, square(i)) for i in range(1, 100)],
    "Pentagonal(n)":  [(i, pentagonal(i)) for i in range(1, 100)],
    "Hexagonal(n)":   [(i, hexagonal(i)) for i in range(1, 100)],
}
for name, seq in seqs.items():
    for i, v in seq:
        if v == TARGET:
            check("Sequences", f"{name} at n={i}", v, f"index={i}")
            print(f"  {name}: {name}({i}) = {v}")

# ─────────────────────────────────────────
# 4. FACTORIZATION IDENTITY: 496 = 2^4 * 31 = 2^tau(6) * Phi_6(6)
# ─────────────────────────────────────────
print("\n=== 4. FACTORIZATION IDENTITY ===")
tau6 = tau(6)  # = 4
phi6_at_6 = cyclotomic(6, 6)  # Phi_6(x) = x^2 - x + 1, at x=6: 36-6+1=31
v = (2**tau6) * phi6_at_6
print(f"  2^tau(6) = 2^{tau6} = {2**tau6}")
print(f"  Phi_6(6) = 6^2 - 6 + 1 = {phi6_at_6}")
print(f"  2^tau(6) * Phi_6(6) = {v}")
check("Factorization", "2^tau(6) * Phi_6(6)", v, "tau(6)=4, Phi_6(6)=31")

# Also: 496 = 16 * 31, note 31 = 2^5 - 1 (Mersenne prime)
print(f"  31 = 2^5 - 1 (Mersenne): {31 == 2**5 - 1}")
check("Factorization", "2^4 * (2^5 - 1)", 16*31, "Mersenne form")

# Perfect number formula: 2^(p-1)*(2^p - 1)
# For p=5: 2^4 * 31 = 496
print(f"  Perfect number formula: 2^(5-1)*(2^5-1) = {2**4 * (2**5 - 1)}")
check("Perfect Number", "2^(p-1)*(2^p-1) for p=5", 2**4*(2**5-1), "P3 definition")

# ─────────────────────────────────────────
# 5. GRAPH THEORY: K_32 edges
# ─────────────────────────────────────────
print("\n=== 5. GRAPH THEORY ===")
# C(n,2) = 496 => n*(n-1)/2 = 496 => n=32
for n in range(1, 100):
    v = math.comb(n, 2)
    if v == TARGET:
        check("Graph Theory", f"C({n},2) = K_{n} edges", v, f"n={n}")
        print(f"  K_{n} complete graph edges = {v}")

# C(n,k) = 496 for various k
print("  Binomial coefficients equal to 496:")
for n in range(1, 200):
    for k in range(2, n):
        v = math.comb(n, k)
        if v == TARGET:
            check("Binomial", f"C({n},{k})", v)
            print(f"  C({n},{k}) = {v}")
        if v > TARGET:
            break

# ─────────────────────────────────────────
# 6. LIE ALGEBRAS & ROOT SYSTEMS
# ─────────────────────────────────────────
print("\n=== 6. LIE ALGEBRAS & ROOT SYSTEMS ===")
# dim(SO(n)) = n*(n-1)/2
for n in range(1, 200):
    v = n*(n-1)//2
    if v == TARGET:
        check("Lie Algebra", f"dim(SO({n})) = {n}({n}-1)/2", v, f"n={n}")
        print(f"  dim(SO({n})) = {v}")

# dim(Sp(2n)) = n*(2n+1)
for n in range(1, 100):
    v = n*(2*n+1)
    if v == TARGET:
        check("Lie Algebra", f"dim(Sp(2*{n})) = {n}(2*{n}+1)", v)
        print(f"  dim(Sp({2*n})) = {v}")

# dim(SU(n)) = n^2 - 1
for n in range(1, 100):
    v = n**2 - 1
    if v == TARGET:
        check("Lie Algebra", f"dim(SU({n})) = {n}^2-1", v)
        print(f"  dim(SU({n})) = {v}")

# dim(E8 x E8) = 2 * 248 = 496
v = 2 * 248
print(f"  dim(E8 x E8) = 2*248 = {v}")
check("Lie Algebra", "dim(E8 x E8) = 2*248", v, "E8 has dim 248")

# dim(SO(32)) = 32*31/2 = 496
v = 32*31//2
print(f"  dim(SO(32)) = 32*31/2 = {v}")
check("Lie Algebra", "dim(SO(32))", v, "Heterotic string gauge group")

# Number of roots in E8: 240, root system D16: ?
# E8 root system: 240 roots
# B_16 = SO(33) root system: 16^2 + 16 = ... no
# Let's check positive roots for some systems
print(f"  Note: SO(32) and E8xE8 are the TWO anomaly-free gauge groups in 10D string theory!")

# ─────────────────────────────────────────
# 7. EXOTIC SPHERES: Theta_n
# ─────────────────────────────────────────
print("\n=== 7. EXOTIC SPHERES ===")
# |Theta_n| values (Kervaire-Milnor): known sequence
# n: 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23...
theta = {
    1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 28, 8: 2, 9: 8, 10: 6,
    11: 992, 12: 1, 13: 3, 14: 2, 15: 16256, 16: 2, 17: 16, 18: 16,
    19: 523264, 20: 24, 21: 1, 22: 2, 23: 8, 24: 1
}
print("  Theta_n values:")
for n, v in theta.items():
    if v == TARGET:
        check("Exotic Spheres", f"|Theta_{n}|", v)
        print(f"  |Theta_{n}| = {v}  *** HIT ***")
    else:
        print(f"  |Theta_{n}| = {v}")

# Check sigma of exotic sphere counts
print("\n  sigma(|Theta_n|) values:")
for n, v in theta.items():
    sv = sigma(v)
    if sv == TARGET:
        check("Exotic Spheres", f"sigma(|Theta_{n}|)", sv, f"|Theta_{n}|={v}")
        print(f"  sigma(|Theta_{n}|) = sigma({v}) = {sv}  *** HIT ***")
    # Check if TARGET appears as sigma of something
    # sigma(496) = ?
print(f"  sigma(496) = {sigma(TARGET)}")
print(f"  sigma(248) = {sigma(248)}")
print(f"  |Theta_11| = 992 = 2*496: {theta[11]} == 2*496: {theta[11] == 2*TARGET}")
check("Exotic Spheres", "|Theta_11| = 2 * 496", theta[11], "992 = 2*P3")

# sigma(496) = 992 = |Theta_11|!
sv = sigma(TARGET)
print(f"\n  KEY: sigma(496) = {sv} = |Theta_11| = {theta[11]}: {sv == theta[11]}")
check("Exotic Spheres", "sigma(496) = |Theta_11|", sigma(TARGET), "perfect number sigma = Theta_11")

# ─────────────────────────────────────────
# 8. CODING THEORY
# ─────────────────────────────────────────
print("\n=== 8. CODING THEORY ===")
# Golay code, Hamming codes, etc.
# Perfect codes: sphere-packing bound
# Weight enumerators

# Extended binary Golay code [24, 12, 8]
# |Aut(G24)| = |M24| = 244823040
# The [32, 16] Reed-Muller code?

# Check if 496 = dimension of some code
# Self-dual codes in dimension n: must be divisible by 8
# n=32: number of codewords = 2^16 = 65536
# Weight distribution of extended binary Golay code -- no direct 496

# Leech lattice: in R^24, 196560 minimal vectors
# E8 lattice: 240 minimal vectors

# Check [n, k, d] codes where parameters involve 496
# Hamming code parameters: n = 2^r - 1, k = n-r, d = 3
# r=9: n=511, k=502 -- no

# Reed-Muller: RM(r, m), length 2^m
# RM(4, 9): length 512, dim = sum C(9,i) for i=0..4 -- check
v = sum(math.comb(9, i) for i in range(5))
print(f"  dim(RM(4,9)) = sum C(9,i) i=0..4 = {v}")
check("Coding Theory", "dim(RM(4,9))", v)

# RM(4, 10): length 1024
v = sum(math.comb(10, i) for i in range(5))
print(f"  dim(RM(4,10)) = sum C(10,i) i=0..4 = {v}")
check("Coding Theory", "dim(RM(4,10))", v)

# ─────────────────────────────────────────
# 9. n=6 ARITHMETIC IDENTITIES
# ─────────────────────────────────────────
print("\n=== 9. n=6 ARITHMETIC IDENTITIES ===")

# Basic n=6 constants
n = 6
phi_6 = phi(n)        # 2
sigma_6 = sigma(n)    # 12
tau_6 = tau(n)        # 4
sigma0_6 = tau_6

print(f"  n=6 properties: phi={phi_6}, sigma={sigma_6}, tau={tau_6}")

# Formulas
formulas_6 = {
    "6^3 - 2^3":       6**3 - 2**3,
    "6^3 - 6^2 + 6^1": 6**3 - 6**2 + 6,
    "6! / 6 - 2":      math.factorial(6)//6 - 2,
    "6! / tau(6) - 2":  math.factorial(6)//tau_6 - 2,
    "sigma(6)^3 / 6":  sigma_6**3 // 6,
    "sigma(6)^3 // 4": sigma_6**3 // 4,
    "12^2 + 12*4":     sigma_6**2 + sigma_6*tau_6,
    "2*6^2 + 4*6 + 2": 2*6**2 + 4*6 + 2,
    "2*sigma_k(6,2)":   2*sigma_k(6,2),
    "sigma_k(6,2)":     sigma_k(6, 2),
    "sigma_k(6,2)+sigma_k(6,3)": sigma_k(6,2) + sigma_k(6,3),
    "4*sigma_k(6,2)":  4*sigma_k(6,2),
    "sigma_k(6,3)/6":  sigma_k(6,3)//6,
    "sigma_k(6,3)/4":  sigma_k(6,3)//4,
    "6^4/6 + 6^2/6":   6**4//6 + 6**2//6,
    "tau(6)*sigma(6)^2/6": tau_6*sigma_6**2//6,
    "phi(6)*sigma(6)^2//3": phi_6*sigma_6**2//3,
}
for name, v in formulas_6.items():
    print(f"  {name} = {v}")
    check("n=6 Arithmetic", name, v)

# Cyclotomic at various x values: Phi_6(x) = x^2 - x + 1
print("\n  Phi_6(x) = x^2-x+1 values:")
for x_val in range(2, 50):
    v = x_val**2 - x_val + 1
    if v == TARGET:
        check("Cyclotomic", f"Phi_6({x_val}) = {x_val}^2-{x_val}+1", v, f"x={x_val}")
        print(f"  Phi_6({x_val}) = {v}  *** HIT ***")

# Cyclotomic Phi_n(6) for various n — use explicit formulas
# Phi_n(6) for small n:
print("\n  Phi_n(6) for n=1..20:")
cyclo_explicit = {
    1: lambda x: x-1,
    2: lambda x: x+1,
    3: lambda x: x**2+x+1,
    4: lambda x: x**2+1,
    5: lambda x: x**4+x**3+x**2+x+1,
    6: lambda x: x**2-x+1,
    7: lambda x: x**6+x**5+x**4+x**3+x**2+x+1,
    8: lambda x: x**4+1,
    9: lambda x: x**6+x**3+1,
    10: lambda x: x**4-x**3+x**2-x+1,
    12: lambda x: x**4-x**2+1,
    14: lambda x: x**6-x**5+x**4-x**3+x**2-x+1,
    15: lambda x: x**8-x**7+x**5-x**4+x**3-x+1,
    18: lambda x: x**6-x**3+1,
    20: lambda x: x**8-x**6+x**4-x**2+1,
}
for nn, fn in sorted(cyclo_explicit.items()):
    v = fn(6)
    print(f"  Phi_{nn}(6) = {v}")
    if v == TARGET:
        check("Cyclotomic", f"Phi_{nn}(6)", v, f"n={nn}")
        print(f"  *** HIT ***")

# ─────────────────────────────────────────
# 10. MODULAR / NUMBER THEORY
# ─────────────────────────────────────────
print("\n=== 10. MODULAR/NUMBER THEORY ===")

# Ramanujan tau function: tau(n) (not divisor count)
# tau(1)=1, tau(2)=-24, tau(3)=252, tau(4)=-1472, tau(5)=4830, tau(6)=-6048...
# |tau(6)| = 6048, not 496

# Sum of sigma over divisors of 6
# sigma(1)+sigma(2)+sigma(3)+sigma(6) = 1+3+4+12 = 20, no

# Multiply perfect numbers
v = P1 * P2
print(f"  P1*P2 = 6*28 = {v}")
check("Perfect Products", "6*28", v)

v = P2 + P1**2
print(f"  P2 + P1^2 = 28 + 36 = {v}")
check("Perfect Products", "P2 + P1^2 = 28+36", v)

# 496 / 6 = 82.67, 496 / 28 = 17.71...
print(f"  496/6 = {TARGET/P1:.4f}")
print(f"  496/28 = {TARGET/P2:.4f}")
print(f"  496 mod 6 = {TARGET % P1}")
print(f"  496 mod 28 = {TARGET % P2}")

check("Mod Relations", "496 mod 6", TARGET % P1)
check("Mod Relations", "496 mod 28", TARGET % P2)

# 496 = sum of consecutive integers from a to b
print("\n  496 as sum of consecutive integers:")
for a in range(1, 100):
    for b in range(a+1, 1000):
        s = (b-a+1)*(a+b)//2
        if s == TARGET:
            n_terms = b - a + 1
            print(f"  sum({a}..{b}) = {s}, {n_terms} terms")
            check("Consecutive Sum", f"sum({a}..{b})", s, f"{n_terms} terms")
        if s > TARGET:
            break

# ─────────────────────────────────────────
# 11. REPRESENTATIONS / PARTITIONS at n=6
# ─────────────────────────────────────────
print("\n=== 11. PARTITIONS & REPRESENTATIONS ===")

# Number of partitions of n
import functools

@functools.lru_cache(maxsize=None)
def partitions(n, k=None):
    if k is None:
        k = n
    if n == 0:
        return 1
    if n < 0 or k == 0:
        return 0
    return partitions(n, k-1) + partitions(n-k, k)

print("  p(n) partition counts:")
for nn in range(1, 60):
    v = partitions(nn)
    if v == TARGET:
        check("Partitions", f"p({nn})", v)
        print(f"  p({nn}) = {v}  *** HIT ***")

# Stirling numbers
print("\n  Stirling2(n,k) equal to 496:")
for nn in range(1, 20):
    for k in range(1, nn+1):
        v = stirling2(nn, k)
        if v == TARGET:
            check("Stirling", f"S2({nn},{k})", v)
            print(f"  S2({nn},{k}) = {v}  *** HIT ***")

# ─────────────────────────────────────────
# 12. WEYL GROUP ORDERS
# ─────────────────────────────────────────
print("\n=== 12. WEYL GROUP ORDERS ===")
weyl = {
    "A1": 2, "A2": 6, "A3": 24, "A4": 120, "A5": 720, "A6": 5040,
    "B2": 8, "B3": 48, "B4": 384, "B5": 3840, "B6": 46080,
    "D4": 192, "D5": 1920, "D6": 23040,
    "G2": 12, "F4": 1152, "E6": 51840, "E7": 2903040, "E8": 696729600,
}
print("  Checking Weyl group orders:")
for name, v in weyl.items():
    if v == TARGET:
        check("Weyl Group", f"|W({name})|", v)
        print(f"  |W({name})| = {v}  *** HIT ***")

# ─────────────────────────────────────────
# 13. DIMENSION FORMULAS
# ─────────────────────────────────────────
print("\n=== 13. DIMENSION FORMULAS ===")
# Symmetric polynomials, representations

# Dimension of Sym^k(V) for dim(V)=n
def sym_dim(n, k):
    return math.comb(n+k-1, k)

def ext_dim(n, k):
    return math.comb(n, k)

print("  Sym^k(R^n) dimensions equal to 496:")
for n in range(2, 30):
    for k in range(2, 30):
        if sym_dim(n, k) == TARGET:
            check("Sym Rep", f"Sym^{k}(R^{n})", TARGET, f"C({n+k-1},{k})")
            print(f"  Sym^{k}(R^{n}) = C({n+k-1},{k}) = {TARGET}")

print("  Exterior power dim = 496:")
for n in range(2, 100):
    for k in range(2, n):
        if ext_dim(n, k) == TARGET:
            check("Ext Rep", f"Lambda^{k}(R^{n})", TARGET, f"C({n},{k})")
            print(f"  Lambda^{k}(R^{n}) = C({n},{k}) = {TARGET}")

# ─────────────────────────────────────────
# 14. SPECIAL VALUES AT n=6
# ─────────────────────────────────────────
print("\n=== 14. SPECIAL VALUES AT n=6 ===")

# Sum of first n perfect numbers
perfect_numbers = [6, 28, 496, 8128]
print(f"  Perfect numbers: {perfect_numbers}")
v = sum(perfect_numbers[:3])
print(f"  Sum of first 3 perfect numbers: {v}")
check("Perfect Sum", "P1+P2+P3 = 6+28+496", v)

# Gaps between perfect numbers
gaps = [28-6, 496-28, 8128-496]
print(f"  Gaps: {gaps}")  # 22, 468, 7632

# Perfect number ratios
print(f"  P3/P2 = {TARGET/P2:.6f}")
print(f"  P3/P1 = {TARGET/P1:.6f}")
print(f"  P2/P1 = {P2/P1:.6f}")

# ─────────────────────────────────────────
# 15. THETA SERIES / LATTICE CONNECTIONS
# ─────────────────────────────────────────
print("\n=== 15. THETA SERIES / LATTICE ===")
# Theta series of E8: coefficients are multiples of 240
# Theta_E8(q) = 1 + 240*q + 2160*q^2 + ...
# Theta_Leech(q) = 1 + 0*q + 196560*q^2 + ...

# sigma(496):
sv = sigma(TARGET)
print(f"  sigma(496) = {sv}  (perfect number so sigma = 2*496 = 992)")
print(f"  |Theta_11| = 992 = sigma(496): {sv == 992}")
check("Theta/Sigma", "sigma(496) = |Theta_11| = 992", sv, "perfect number relation")

# sigma(8128):
sv2 = sigma(8128)
print(f"  sigma(8128) = {sv2}  (= |Theta_15| = 16256?): {sv2 == 16256}")
check("Theta/Sigma", "sigma(8128) = |Theta_15| = 16256", sv2, "P4 perfect number")

# For all perfect numbers P: sigma(P) = 2P = |Theta_{4k+3}| ?
# P1=6: sigma(6)=12=2*6, P2=28: sigma(28)=56=2*28
# So sigma(Pn) = 2*Pn always (definition of perfect)
# |Theta_7| = 28 = P2! Check
print(f"  |Theta_7| = {theta[7]} = P2 = {P2}: {theta[7] == P2}")
check("Exotic/Perfect", "|Theta_7| = P2 = 28", theta[7], "28 is both P2 and Theta_7")

# ─────────────────────────────────────────
# 16. CONNECTIONS VIA STRING THEORY
# ─────────────────────────────────────────
print("\n=== 16. STRING THEORY CONNECTIONS ===")
# Heterotic string: 16D gauge group
# SO(32): rank=16, dim=496
# E8xE8: rank=16, dim=496
# Both anomaly-free in 10D!
# The number 496 is fundamental here

# In 26D bosonic string: critical dimension = 26
# Tachyon mass^2 = -2/alpha', M^2 = (N - 1)/alpha'
# Level N=0: tachyon, N=1: massless, etc.

# Green-Schwarz mechanism: anomaly cancellation requires
# tr F^6 = (1/48)(tr F^2)(tr F^4) - (1/14400)(tr F^2)^3
# For SO(32) or E8xE8 only!
# Key identity: dim = 496

# L-function values
# zeta(2) = pi^2/6, zeta(4) = pi^4/90, etc.
print(f"  496 in string theory: dim(SO(32)) = dim(E8xE8) = 496")
print(f"  Both are anomaly-free gauge groups in 10D heterotic string theory")

# ─────────────────────────────────────────
# 17. ADDITIONAL SEQUENCES
# ─────────────────────────────────────────
print("\n=== 17. ADDITIONAL SEQUENCES ===")

# Powers and near-powers
for base in range(2, 25):
    for exp in range(2, 10):
        v = base**exp
        if v == TARGET:
            check("Powers", f"{base}^{exp}", v)
            print(f"  {base}^{exp} = {v}")

# n*(n+1) form
for n in range(1, 100):
    v = n*(n+1)
    if v == TARGET:
        check("n(n+1)", f"{n}*{n+1}", v)

# Sum of squares
for n in range(1, 30):
    v = sum(i**2 for i in range(1, n+1))
    if v == TARGET:
        check("Sum of squares", f"sum(i^2, 1..{n})", v)
        print(f"  sum(i^2, 1..{n}) = {v}  *** HIT ***")

# Sum of cubes
for n in range(1, 20):
    v = sum(i**3 for i in range(1, n+1))
    if v == TARGET:
        check("Sum of cubes", f"sum(i^3, 1..{n})", v)
        print(f"  sum(i^3, 1..{n}) = {v}  *** HIT ***")

# sum of sigma(k) for k=1..n
for nn in range(1, 100):
    v = sum(sigma(k) for k in range(1, nn+1))
    if v == TARGET:
        check("Sum sigma", f"sum(sigma(k), k=1..{nn})", v)
        print(f"  sum(sigma(k), k=1..{nn}) = {v}  *** HIT ***")

# ─────────────────────────────────────────
# 18. SHADOW DENSITY COMPARISON
# ─────────────────────────────────────────
print("\n\n" + "="*60)
print("SUMMARY: P3=496 SHADOW SEARCH RESULTS")
print("="*60)

hits = [r for r in results if r["hit"]]
total = len(results)

print(f"\nTotal formulas checked: {total}")
print(f"Hits (= 496): {len(hits)}")
print(f"Shadow density: {len(hits)/total*100:.1f}%")
print(f"\nFor comparison:")
print(f"  P2=28 shadow: 26 hits (H-CROSS-2 result, density ~14.6%)")
print(f"  P3=496 shadow: {len(hits)} hits, density {len(hits)/total*100:.1f}%")

print(f"\n--- HIT LIST ---")
for r in hits:
    print(f"  [{r['domain']}] {r['formula']} = {r['value']}  ({r['note']})")

# Domain breakdown
domains = {}
for r in hits:
    d = r["domain"]
    domains[d] = domains.get(d, 0) + 1

print(f"\n--- HITS BY DOMAIN ---")
for d, count in sorted(domains.items(), key=lambda x: -x[1]):
    print(f"  {d}: {count}")

# ─────────────────────────────────────────
# 19. KEY STRUCTURAL IDENTITIES
# ─────────────────────────────────────────
print("\n=== KEY STRUCTURAL IDENTITIES ===")
print(f"  496 = P3 (3rd perfect number)")
print(f"  496 = 2^4 * 31 = 2^(5-1) * (2^5 - 1)")
print(f"  496 = 2^tau(6) * Phi_6(6)  [tau(6)=4, Phi_6(6)=31]")
print(f"  496 = dim(SO(32)) = dim(E8 x E8)  [both anomaly-free in 10D]")
print(f"  496 = C(32,2)  [complete graph K_32 edges]")
print(f"  sigma(496) = 992 = 2*496  [perfect number]")
print(f"  992 = |Theta_11|  [exotic 11-spheres]")
print(f"  496 mod 6 = {496 % 6}")
print(f"  496 mod 28 = {496 % 28}")
print(f"  sum(1..31) = {sum(range(1,32))} = 496  [triangular number T_31]")
v = sum(range(1, 32))
check("Triangular", "T_31 = sum(1..31)", v, "31=Mersenne prime")
print(f"  {v} = T_31 = {v == TARGET}")
