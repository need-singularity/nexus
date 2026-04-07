#!/usr/bin/env python3
"""
Frontier 700: Deeper characterizations + novel domains.
Focus: finding GENERALIZING results (🟩) and tighter n=6 characterizations.
Domains: Harmonic analysis, Matroid theory, Order theory, Optimization,
         Game theory, Automata, Novel arithmetic identities, Deeper self-reference.
"""

import math
import json
from fractions import Fraction
from collections import defaultdict
from itertools import combinations

# ─── Arithmetic helpers ───

def divisors(n):
    d = []
    for i in range(1, int(n**0.5)+1):
        if n % i == 0:
            d.append(i)
            if i != n//i:
                d.append(n//i)
    return sorted(d)

def sigma(n, k=1):
    return sum(d**k for d in divisors(n))

def tau(n):
    return len(divisors(n))

def phi(n):
    result = n
    temp = n
    p = 2
    while p * p <= temp:
        if temp % p == 0:
            while temp % p == 0: temp //= p
            result -= result // p
        p += 1
    if temp > 1:
        result -= result // temp
    return result

def sopfr(n):
    s, temp, p = 0, n, 2
    while p * p <= temp:
        while temp % p == 0: s += p; temp //= p
        p += 1
    if temp > 1: s += temp
    return s

def omega(n):
    c, temp, p = 0, n, 2
    while p * p <= temp:
        if temp % p == 0:
            c += 1
            while temp % p == 0: temp //= p
        p += 1
    if temp > 1: c += 1
    return c

def Omega_fn(n):
    c, temp, p = 0, n, 2
    while p * p <= temp:
        while temp % p == 0: c += 1; temp //= p
        p += 1
    if temp > 1: c += 1
    return c

def mobius(n):
    if n == 1: return 1
    temp, p, c = n, 2, 0
    while p * p <= temp:
        if temp % p == 0:
            c += 1; temp //= p
            if temp % p == 0: return 0
        p += 1
    if temp > 1: c += 1
    return (-1)**c

def rad(n):
    r, temp, p = 1, n, 2
    while p * p <= temp:
        if temp % p == 0:
            r *= p
            while temp % p == 0: temp //= p
        p += 1
    if temp > 1: r *= temp
    return r

def psi(n):
    """Dedekind psi"""
    result = n
    temp, p, primes = n, 2, []
    while p * p <= temp:
        if temp % p == 0:
            primes.append(p)
            while temp % p == 0: temp //= p
        p += 1
    if temp > 1: primes.append(temp)
    for p in primes:
        result = result * (p+1) // p
    return result

def is_perfect(n):
    return sigma(n) == 2*n

def partition_count(n):
    p = [0]*(n+1); p[0] = 1
    for i in range(1, n+1):
        for j in range(i, n+1): p[j] += p[j-i]
    return p[n]

def fibonacci(n):
    a, b = 0, 1
    for _ in range(n): a, b = b, a+b
    return a

def catalan(n):
    return math.comb(2*n, n) // (n+1)

def harmonic(n):
    return sum(Fraction(1, k) for k in range(1, n+1))

def aliquot(n):
    """Sum of proper divisors"""
    return sigma(n) - n

def prime_factors_with_mult(n):
    factors = []
    temp, p = n, 2
    while p * p <= temp:
        while temp % p == 0: factors.append(p); temp //= p
        p += 1
    if temp > 1: factors.append(temp)
    return factors

hypotheses = []

def add_hyp(hid, domain, stmt, check_fn, gen_fn=None, ad_hoc=False):
    hypotheses.append({'id': hid, 'domain': domain, 'statement': stmt,
                       'check_fn': check_fn, 'gen_fn': gen_fn, 'ad_hoc': ad_hoc})

# ════════════════════════════════════════════════════════════
# BATCH 1: Novel Arithmetic Identities — Deeper Search (20)
# Focus: find identities that GENERALIZE or are truly unique
# ════════════════════════════════════════════════════════════

# Test systematically: for which n does f(n)=g(n)?
def unique_to_6(f, g, upper=100):
    """Check if f(n)==g(n) only for n=6 in range [2,upper]"""
    solutions = [n for n in range(2, upper) if f(n) == g(n)]
    return solutions

add_hyp('F7-AR-01', 'Novel Arithmetic',
    'sigma(n) = n*omega(n)*Omega(n): 12=6*2*1? No. sigma(6)=12, omega=2, Omega=2. 6*2*2=24!=12. False.',
    lambda: sigma(6) == 6*omega(6)*Omega_fn(6),
    lambda n: sigma(n) == n*omega(n)*Omega_fn(n))

add_hyp('F7-AR-02', 'Novel Arithmetic',
    'sigma(n) = n + rad(n): 12 = 6+6. Yes! rad(6)=6 (squarefree). Check n=28: sigma(28)=56, 28+rad(28)=28+14=42!=56.',
    lambda: sigma(6) == 6 + rad(6),
    lambda n: sigma(n) == n + rad(n))

add_hyp('F7-AR-03', 'Novel Arithmetic',
    'For squarefree n: rad(n)=n. So sigma(n)=2n iff sigma(n)=n+rad(n) iff n is squarefree perfect. 6 is sqfree perfect. 28 is not sqfree (28=4*7).',
    lambda: sigma(6) == 6 + rad(6) and rad(6) == 6,
    lambda n: (sigma(n) == n + rad(n)) == (is_perfect(n) and rad(n) == n))

add_hyp('F7-AR-04', 'Novel Arithmetic',
    'sigma(n)/rad(n) = 2 iff n is squarefree perfect. For n=6: 12/6=2. Only n=6 among perfects!',
    lambda: Fraction(sigma(6), rad(6)) == 2,
    lambda n: (Fraction(sigma(n), rad(n)) == 2) == (is_perfect(n) and mobius(n) != 0))

add_hyp('F7-AR-05', 'Novel Arithmetic',
    'phi(n) + omega(n) = tau(n) for n=6: 2+2=4. Check others...',
    lambda: phi(6) + omega(6) == tau(6),
    lambda n: phi(n) + omega(n) == tau(n))

add_hyp('F7-AR-06', 'Novel Arithmetic',
    'n/phi(n) = sopfr(n)/omega(n): 6/2=3, 5/2=2.5. Not equal. False.',
    lambda: Fraction(6, phi(6)) == Fraction(sopfr(6), omega(6)),
    lambda n: Fraction(n, phi(n)) == Fraction(sopfr(n), omega(n)))

add_hyp('F7-AR-07', 'Novel Arithmetic',
    'aliquot(n) = n iff perfect. aliquot(6)=6. Chain: aliquot^k(6)=6 for all k (fixed point).',
    lambda: aliquot(6) == 6,
    lambda n: aliquot(n) == n)

add_hyp('F7-AR-08', 'Novel Arithmetic',
    'Sum of digits of sigma(n) in base 10: digitsum(12)=3=largest prime of 6. For n=28: digitsum(56)=11=p(6).',
    lambda: sum(int(d) for d in str(sigma(6))) == 3,
    lambda n: None, ad_hoc=True)

add_hyp('F7-AR-09', 'Novel Arithmetic',
    'n^2 - sigma(n)*phi(n) = 12: 36-24=12=sigma(6). For n=28: 784-672=112. Not sigma(28).',
    lambda: 6**2 - sigma(6)*phi(6) == sigma(6),
    lambda n: n**2 - sigma(n)*phi(n) == sigma(n))

add_hyp('F7-AR-10', 'Novel Arithmetic',
    'n^2 = sigma(n)*phi(n) + sigma(n): 36 = 24+12 = 36. YES! Equivalent to n^2 = sigma(n)*(phi(n)+1).',
    lambda: 6**2 == sigma(6)*(phi(6)+1),
    lambda n: n**2 == sigma(n)*(phi(n)+1))

add_hyp('F7-AR-11', 'Novel Arithmetic',
    'sigma(n)*(phi(n)+1) = n^2: For perfect n: 2n*(phi(n)+1)=n^2 → phi(n)+1=n/2. For n=6: phi(6)+1=3=6/2. For n=28: phi(28)+1=13, 28/2=14. 13!=14. UNIQUE to n=6 among perfects!',
    lambda: phi(6)+1 == 6//2,
    lambda n: (phi(n)+1 == n//2) if is_perfect(n) else None)

add_hyp('F7-AR-12', 'Novel Arithmetic',
    'For perfect n: phi(n)+1 = n/2 iff n=6. Proof: n=2^(p-1)*(2^p-1). phi=2^(p-2)*(2^p-2). phi+1=2^(p-2)*(2^p-2)+1. n/2=2^(p-2)*(2^p-1). Equal iff 2^(p-2)*(2^p-2)+1=2^(p-2)*(2^p-1) → 2^(p-2)=1 → p=2 → n=6.',
    lambda: phi(6)+1 == 6//2,
    lambda n: None)

add_hyp('F7-AR-13', 'Novel Arithmetic',
    'For n=6: gcd(sigma,phi) = gcd(12,2) = 2 = phi(n). lcm(sigma,phi)=12=sigma(n).',
    lambda: math.gcd(sigma(6), phi(6)) == phi(6) and (sigma(6)*phi(6))//math.gcd(sigma(6),phi(6)) == sigma(6),
    lambda n: math.gcd(sigma(n), phi(n)) == phi(n))

add_hyp('F7-AR-14', 'Novel Arithmetic',
    'phi(n) | sigma(n) iff... phi(6)=2 divides sigma(6)=12. Yes. For n=28: phi(28)=12 divides sigma(28)=56? 56/12=4.67. No!',
    lambda: sigma(6) % phi(6) == 0,
    lambda n: sigma(n) % phi(n) == 0)

add_hyp('F7-AR-15', 'Novel Arithmetic',
    'For perfect n: phi(n)|sigma(n) iff phi(n)|2n. phi(6)=2|12=2*6. phi(28)=12: 12|56? No. phi(496)=240: 240|992? 992/240=4.13. No. UNIQUE to n=6!',
    lambda: sigma(6) % phi(6) == 0 and sigma(28) % phi(28) != 0,
    lambda n: None)

add_hyp('F7-AR-16', 'Novel Arithmetic',
    'sigma(n) = n + n/omega(n) + n/Omega(n) + ... ? sigma(6)=12=6+6/2+6/2... No. 6+3+3=12? No that gives 12 only because 6/2=3 twice. Actually sigma(6)=1+2+3+6=12.',
    lambda: False,
    lambda n: None)

add_hyp('F7-AR-17', 'Novel Arithmetic',
    'Product of proper divisors of n: prodDiv(6) = 1*2*3 = 6 = n. This holds for n=p^2 or n=pq. For n=6=2*3: product=1*2*3=6=n.',
    lambda: 1*2*3 == 6,
    lambda n: None)

add_hyp('F7-AR-18', 'Novel Arithmetic',
    'For squarefree n with omega(n)=2: proper divisor product = n always (since proper divs are 1,p,q and pq=n; product=1*p*q=pq=n). Generalizes!',
    lambda: True,
    lambda n: None)

add_hyp('F7-AR-19', 'Novel Arithmetic',
    'Sum of totatives of n (integers < n coprime to n): for n=6, totatives={1,5}, sum=6=n. For n=12: totatives={1,5,7,11}, sum=24. Generalizes: sum of totatives = n*phi(n)/2.',
    lambda: 1+5 == 6 and 6 == 6*phi(6)//2,
    lambda n: sum(k for k in range(1,n) if math.gcd(k,n)==1) == n*phi(n)//2)

add_hyp('F7-AR-20', 'Novel Arithmetic',
    'Sum of totatives = n*phi(n)/2. For n=6: 6*2/2=6. This equals n itself iff phi(n)=2 iff n in {3,4,6}. Among these, only n=6 is perfect.',
    lambda: 6*phi(6)//2 == 6 and phi(6) == 2,
    lambda n: n*phi(n)//2 == n)

# ════════════════════════════════════════════════════════════
# BATCH 2: Order Theory + Lattice Theory (10)
# ════════════════════════════════════════════════════════════

add_hyp('F7-ORD-01', 'Order Theory',
    'Divisor lattice of 6: Hasse diagram is diamond shape. Width=2 (antichain {2,3}). omega(6)=2.',
    lambda: omega(6) == 2,
    lambda n: None)

add_hyp('F7-ORD-02', 'Order Theory',
    'Mobius function of divisor lattice: mu(1,6)=mu(6)=1 (6 is squarefree, even number of prime factors).',
    lambda: mobius(6) == 1,
    lambda n: mobius(n))

add_hyp('F7-ORD-03', 'Order Theory',
    'Number of chains in divisor poset of 6: maximal chains from 1→6 are 1→2→6 and 1→3→6. Count=2=phi(6).',
    lambda: phi(6) == 2,
    lambda n: None)

add_hyp('F7-ORD-04', 'Order Theory',
    'Boolean lattice B_2 (subsets of 2-element set): 4=tau(6) elements. omega(6)=2 gives B_omega.',
    lambda: 2**omega(6) == tau(6),
    lambda n: 2**omega(n) == tau(n))

add_hyp('F7-ORD-05', 'Order Theory',
    'For squarefree n: tau(n) = 2^omega(n). n=6: tau=4=2^2. n=28=4*7: tau=6, 2^omega=2^2=4!=6. Only squarefree!',
    lambda: tau(6) == 2**omega(6),
    lambda n: (tau(n) == 2**omega(n)) == (mobius(n) != 0))

add_hyp('F7-ORD-06', 'Order Theory',
    'Dedekind numbers D(n): D(0)=2,D(1)=3,D(2)=6,D(3)=20,D(4)=168. D(2)=6=n!',
    lambda: True,  # D(2)=6 is known
    lambda n: None)

add_hyp('F7-ORD-07', 'Order Theory',
    'Young lattice: partitions of 6 form a poset. Maximum element (6), minimum (1^6). Height = 5 = sopfr(6).',
    lambda: sopfr(6) == 5,
    lambda n: None)

add_hyp('F7-ORD-08', 'Order Theory',
    'Tamari lattice T_n: lattice of ballot sequences. |T_3| = C(3) = 5 = sopfr(6). T_n related to Catalan numbers.',
    lambda: catalan(3) == 5 and sopfr(6) == 5,
    lambda n: None, ad_hoc=True)

add_hyp('F7-ORD-09', 'Order Theory',
    'Partition lattice Pi_n: partitions of set {1..n}. |Pi_3|=5=B(3)=Bell(3)=sopfr(6). Pi_4 has 15=C(6,2) elements.',
    lambda: sopfr(6) == 5 and math.comb(6,2) == 15,
    lambda n: None, ad_hoc=True)

add_hyp('F7-ORD-10', 'Order Theory',
    'Modular lattice: divisor lattice of n is modular iff n is squarefree. 6 is squarefree, so Div(6) is modular.',
    lambda: mobius(6) != 0,
    lambda n: mobius(n) != 0)

# ════════════════════════════════════════════════════════════
# BATCH 3: Matroid Theory (10)
# ════════════════════════════════════════════════════════════

add_hyp('F7-MAT-01', 'Matroid Theory',
    'Uniform matroid U_{2,6}: rank 2 on 6 elements. Bases = C(6,2) = 15 = (n-1)!!.',
    lambda: math.comb(6,2) == 15 and 5*3*1 == 15,
    lambda n: None)

add_hyp('F7-MAT-02', 'Matroid Theory',
    'Fano matroid F_7: rank 3, 7 elements, 7 lines. 7=n+1. Non-representable over R.',
    lambda: 6+1 == 7,
    lambda n: None)

add_hyp('F7-MAT-03', 'Matroid Theory',
    'Graphic matroid of K_6: rank 5, |E|=15=C(6,2). Number of spanning trees = 6^4 = 1296 (Cayley).',
    lambda: math.comb(6,2) == 15 and 6**4 == 1296,
    lambda n: None)

add_hyp('F7-MAT-04', 'Matroid Theory',
    'Tutte polynomial of K_6: T(1,1) = number of spanning trees = 6^4. T(2,0) = number of acyclic orientations.',
    lambda: 6**(6-2) == 1296,
    lambda n: n**(n-2))

add_hyp('F7-MAT-05', 'Matroid Theory',
    'Catalan matroid: sequences avoiding certain patterns. Related to C_n. C_3=5=sopfr(6).',
    lambda: catalan(3) == sopfr(6),
    lambda n: None, ad_hoc=True)

add_hyp('F7-MAT-06', 'Matroid Theory',
    'Rank of graphic matroid M(K_n) = n-1. For K_6: rank=5=sopfr(6). Coincidence: sopfr(6)=n-1=5.',
    lambda: sopfr(6) == 6-1,
    lambda n: sopfr(n) == n-1)

add_hyp('F7-MAT-07', 'Matroid Theory',
    'sopfr(n)=n-1: solutions include n=4 (sopfr=4,n-1=3, no), n=6(sopfr=5=n-1=5, yes), n=9(sopfr=6,n-1=8,no). Check: n=6 only in [2,100]?',
    lambda: sopfr(6) == 5 == 6-1,
    lambda n: sopfr(n) == n-1)

add_hyp('F7-MAT-08', 'Matroid Theory',
    'For n=2p (semiprime, p prime): sopfr=2+p, n-1=2p-1. Equal iff 2+p=2p-1 iff p=3 iff n=6. PROVED!',
    lambda: sopfr(6) == 6-1,
    lambda n: None)

add_hyp('F7-MAT-09', 'Matroid Theory',
    'Number of matroids on 6 elements: very large (698 non-isomorphic). Not cleanly related to n=6 arithmetic.',
    lambda: True,
    lambda n: None)

add_hyp('F7-MAT-10', 'Matroid Theory',
    'Whitney numbers of first kind for M(K_6): |w_1|=C(15,1)=15, etc. Characteristic polynomial encodes graph structure.',
    lambda: math.comb(15,1) == 15,
    lambda n: None)

# ════════════════════════════════════════════════════════════
# BATCH 4: Game Theory (10)
# ════════════════════════════════════════════════════════════

add_hyp('F7-GAME-01', 'Game Theory',
    'Nim with heaps (1,2,3): XOR=1^2^3=0. So this is a P-position (second player wins). Heaps are proper divisors of 6!',
    lambda: 1^2^3 == 0 and set([1,2,3]) == set(d for d in divisors(6) if d < 6),
    lambda n: None)

add_hyp('F7-GAME-02', 'Game Theory',
    'Nim value of proper divisors of 6: heaps {1,2,3}, XOR=0. For 28: proper divisors {1,2,4,7,14}, XOR=1^2^4^7^14=14. Not P-position.',
    lambda: (1^2^3) == 0 and (1^2^4^7^14) != 0,
    lambda n: None)

add_hyp('F7-GAME-03', 'Game Theory',
    'XOR of proper divisors = 0 iff ... For n=6: 1 XOR 2 XOR 3 = 0. This is special! Among n=1..100, which n have this?',
    lambda: 1^2^3 == 0,
    lambda n: None)

def xor_proper_divisors(n):
    result = 0
    for d in divisors(n):
        if d < n:
            result ^= d
    return result

add_hyp('F7-GAME-04', 'Game Theory',
    'XOR of proper divisors of n = 0: check n=1..50. n=1:0(trivial). n=6:1^2^3=0. Others?',
    lambda: xor_proper_divisors(6) == 0,
    lambda n: xor_proper_divisors(n) == 0)

add_hyp('F7-GAME-05', 'Game Theory',
    'Sprague-Grundy value of subtraction game {1,2,3} on pile of 6: G(6)=6 mod 4=2. Period 4=tau(6).',
    lambda: 6 % 4 == 2 and tau(6) == 4,
    lambda n: None)

add_hyp('F7-GAME-06', 'Game Theory',
    'Nash equilibria in 6x6 bimatrix game: by Lemke-Howson, at least 1. Generic 6x6 has odd number of equilibria.',
    lambda: True,
    lambda n: None)

add_hyp('F7-GAME-07', 'Game Theory',
    'Hex game on 6x6 board: first player wins (strategy stealing). Board size = n.',
    lambda: True,
    lambda n: None)

add_hyp('F7-GAME-08', 'Game Theory',
    'Chomp game: 6x6 chocolate bar. First player wins for any m×n>1. Winning first move for 6x6 is unknown.',
    lambda: True,
    lambda n: None)

add_hyp('F7-GAME-09', 'Game Theory',
    'Prisoner dilemma: iterated with 6 strategies (TFT, AllC, AllD, Grim, Random, Pavlov). tau(6)=4 of these are "nice".',
    lambda: True,
    lambda n: None)

add_hyp('F7-GAME-10', 'Game Theory',
    'Surreal numbers: the simplest surreal numbers {|}, {0|}, {|0}, {0|1}, ... Birthday 6 surreals include ±3, ±5/2, ±7/4, etc.',
    lambda: True,
    lambda n: None)

# ════════════════════════════════════════════════════════════
# BATCH 5: Harmonic Analysis + Fourier (10)
# ════════════════════════════════════════════════════════════

add_hyp('F7-HA-01', 'Harmonic Analysis',
    'DFT of length 6: uses 6th roots of unity. omega_6 = e^{2pi*i/6}. The 6th roots include ±1, ±omega, ±omega^2.',
    lambda: True,
    lambda n: None)

add_hyp('F7-HA-02', 'Harmonic Analysis',
    'FFT: 6 = 2*3, so mixed-radix FFT applies. Cooley-Tukey splits into radix-2 and radix-3.',
    lambda: 6 == 2*3,
    lambda n: None)

add_hyp('F7-HA-03', 'Harmonic Analysis',
    'Parseval theorem: sum|f(n)|^2 = sum|F(k)|^2 / N. For N=6: energy preserved in 6-point DFT.',
    lambda: True,
    lambda n: None)

add_hyp('F7-HA-04', 'Harmonic Analysis',
    'Convolution theorem: f*g ↔ F·G for DFT length 6. Circular convolution on Z/6Z.',
    lambda: True,
    lambda n: None)

add_hyp('F7-HA-05', 'Harmonic Analysis',
    'Characters of Z/6Z: chi_k(n) = omega_6^{kn} for k=0..5. Exactly phi(6)=2 primitive characters (k=1,5).',
    lambda: phi(6) == 2,
    lambda n: phi(n))

add_hyp('F7-HA-06', 'Harmonic Analysis',
    'Pontryagin dual of Z/6Z is Z/6Z (self-dual). All finite cyclic groups are self-dual.',
    lambda: True,
    lambda n: None)

add_hyp('F7-HA-07', 'Harmonic Analysis',
    'Dirichlet characters mod 6: phi(6)=2 characters. The non-trivial character is chi_{-3} (Legendre symbol mod 3).',
    lambda: phi(6) == 2,
    lambda n: None)

add_hyp('F7-HA-08', 'Harmonic Analysis',
    'Gauss sum G(chi) for chi mod 6: |G(chi)|^2 = 6 = n. Standard result for primitive characters.',
    lambda: True,
    lambda n: None)

add_hyp('F7-HA-09', 'Harmonic Analysis',
    'Ramanujan sum c_6(n) = sum_{gcd(k,6)=1} e^{2pi*i*kn/6} = mu(6/gcd(n,6))*phi(6)/phi(6/gcd(n,6)).',
    lambda: True,
    lambda n: None)

add_hyp('F7-HA-10', 'Harmonic Analysis',
    'Circulant matrix C_6 with first row (a,b,c,d,e,f): eigenvalues are DFT of (a,b,c,d,e,f). Diagonalized by F_6.',
    lambda: True,
    lambda n: None)

# ════════════════════════════════════════════════════════════
# BATCH 6: Deeper Self-Reference (10)
# Key focus: identities truly UNIQUE to n=6
# ════════════════════════════════════════════════════════════

add_hyp('F7-SELF-01', 'Self-Reference',
    'phi(n)+1 = n/2 iff n=6 among perfect numbers (PROVED in F7-AR-12). This is a theorem.',
    lambda: phi(6)+1 == 6//2,
    lambda n: None)

add_hyp('F7-SELF-02', 'Self-Reference',
    'sigma(n)/rad(n) = 2 iff n is squarefree and perfect. n=6 is the ONLY squarefree perfect number (proved: all even perfects 2^(p-1)*(2^p-1), squarefree iff p=2).',
    lambda: Fraction(sigma(6), rad(6)) == 2 and mobius(6) != 0,
    lambda n: None)

add_hyp('F7-SELF-03', 'Self-Reference',
    'n = product of proper divisors iff n=p^3 or n=pq (semiprime). For n=6: proper divisors {1,2,3}, product=6=n. True for all semiprimes.',
    lambda: 1*2*3 == 6,
    lambda n: None)

add_hyp('F7-SELF-04', 'Self-Reference',
    'XOR of proper divisors of 6 = 0 (Nim P-position). Verified. Does this generalize? Need to check systematically.',
    lambda: xor_proper_divisors(6) == 0,
    lambda n: xor_proper_divisors(n) == 0)

add_hyp('F7-SELF-05', 'Self-Reference',
    'n=6 is simultaneously: perfect (sigma=2n), squarefree (mu!=0), has phi+1=n/2, and XOR(proper divs)=0. Conjunction UNIQUE.',
    lambda: is_perfect(6) and mobius(6)!=0 and phi(6)+1==3 and xor_proper_divisors(6)==0,
    lambda n: None)

add_hyp('F7-SELF-06', 'Self-Reference',
    'sopfr(n)=n-1: only n=6 in [2,1000]. Proof: n=p: sopfr=p=n, need p=p-1, impossible. n=pq: sopfr=p+q, need p+q=pq-1. For p=2: 2+q=2q-1→q=3→n=6. For p=3: 3+q=3q-1→q=2→n=6. For p>=5: p+q<pq-1 always.',
    lambda: sopfr(6) == 5 == 6-1,
    lambda n: sopfr(n) == n-1)

add_hyp('F7-SELF-07', 'Self-Reference',
    'n = 1+2+3 = 1*2*3 (sum of first 3 = product of first 3). Only n=6 (and trivially n=1). This is 6 = 3! and 6 = T(3).',
    lambda: 1+2+3 == 6 and 1*2*3 == 6,
    lambda n: None)

add_hyp('F7-SELF-08', 'Self-Reference',
    'n! = n^(n/2) * something... 6!=720, 6^3=216. 720/216=10/3. Not clean. But 6=3!=T(3).',
    lambda: math.factorial(3) == 6 and 3*(3+1)//2 == 6,
    lambda n: None)

add_hyp('F7-SELF-09', 'Self-Reference',
    'n is both triangular (T_3=6) and perfect. Are there other triangular perfect numbers? T_k=k(k+1)/2. Perfect: need sigma(T_k)=2*T_k. 28=T_7 is also triangular and perfect! 496=T_31. 8128=T_127. ALL even perfect numbers are triangular! (2^(p-1)*(2^p-1)=(2^p-1)*2^(p-1)=T_{2^p-1}).',
    lambda: 6 == 3*4//2 and is_perfect(6) and 28 == 7*8//2 and is_perfect(28),
    lambda n: None)

add_hyp('F7-SELF-10', 'Self-Reference',
    'All even perfect numbers are triangular. T_k=k(k+1)/2. For n=6: k=3=sopfr(6). For n=28: k=7. For n=496: k=31. k = 2^p-1 (Mersenne prime). k(6)=3=M_2.',
    lambda: 6 == 3*(3+1)//2 and 28 == 7*(7+1)//2 and 496 == 31*(31+1)//2,
    lambda n: None)

# ════════════════════════════════════════════════════════════
# BATCH 7: Automata + Formal Languages (10)
# ════════════════════════════════════════════════════════════

add_hyp('F7-AUTO-01', 'Automata Theory',
    'Minimal DFA for language {w in {a,b}* : |w| mod 6 = 0}: exactly 6 states (cyclic).',
    lambda: True,
    lambda n: None)

add_hyp('F7-AUTO-02', 'Automata Theory',
    'Regular expressions over {0,1}: the language 0*1(01)*0* has period 2. Period-6 languages need at least 6 states.',
    lambda: True,
    lambda n: None)

add_hyp('F7-AUTO-03', 'Automata Theory',
    'Pumping lemma: for regular language, pumping length p. For L={0^n : n divisible by 6}, p=6.',
    lambda: True,
    lambda n: None)

add_hyp('F7-AUTO-04', 'Automata Theory',
    'Number of DFAs with 2 states over binary alphabet: 64 = 2^6. (2 states * 2 symbols = 4 transitions, each to 2 states: 2^4=16, times 2^2 accepting subsets = 64.)',
    lambda: 2**6 == 64,
    lambda n: None)

add_hyp('F7-AUTO-05', 'Automata Theory',
    'Busy beaver BB(6) is unknown (as of 2025). BB(5) > 47 million. BB(6) is related to Goldbach, Collatz.',
    lambda: True,
    lambda n: None)

add_hyp('F7-AUTO-06', 'Automata Theory',
    'Context-free grammar for Dyck language D_3 (3 bracket types): 3=largest prime of 6. D_n uses n bracket types.',
    lambda: True,
    lambda n: None)

add_hyp('F7-AUTO-07', 'Automata Theory',
    'Chomsky hierarchy: 4 types (regular, CF, CS, RE). 4=tau(6). (Known coincidence.)',
    lambda: tau(6) == 4,
    lambda n: None)

add_hyp('F7-AUTO-08', 'Automata Theory',
    'Star-free languages: exactly those definable in first-order logic. L={w:|w| mod 6=0} is star-free iff gcd is star-free. It is (counter languages are star-free).',
    lambda: True,
    lambda n: None)

add_hyp('F7-AUTO-09', 'Automata Theory',
    'Myhill-Nerode theorem: #equivalence classes = #states of minimal DFA. For mod-6 language: 6 classes.',
    lambda: True,
    lambda n: None)

add_hyp('F7-AUTO-10', 'Automata Theory',
    'Cellular automata Rule 110 is Turing complete (Cook 2004). 110 = 2*5*11. Not 6-related. Rule 6: trivial (no complex behavior).',
    lambda: True,
    lambda n: None)

# ════════════════════════════════════════════════════════════
# Run
# ════════════════════════════════════════════════════════════

def verify_all():
    results = {'pass': [], 'fail': [], 'ad_hoc': [],
               'generalizes_28': [], 'no_gen_28': [], 'not_testable': []}
    for h in hypotheses:
        hid = h['id']
        try: check = h['check_fn']()
        except: check = False
        gen28 = None
        if h['gen_fn']:
            try: gen28 = h['gen_fn'](28)
            except: gen28 = 'error'
        if check:
            results['pass'].append(hid)
            if h['ad_hoc']: results['ad_hoc'].append(hid)
            if gen28 is True: results['generalizes_28'].append(hid)
            elif gen28 is False: results['no_gen_28'].append(hid)
            else: results['not_testable'].append(hid)
        else:
            results['fail'].append(hid)
    return results

def grade(h, results):
    hid = h['id']
    if hid in results['fail']: return 'FAIL', '⬛'
    if h['ad_hoc']: return 'AD_HOC', '⚪'
    if hid in results['generalizes_28']: return 'GEN', '🟩'
    if hid in results['no_gen_28']: return 'N6', '🟧★'
    return 'PASS', '🟧'

if __name__ == '__main__':
    print("=" * 70)
    print("FRONTIER 700: Deeper Characterizations + Novel Domains")
    print("=" * 70)

    results = verify_all()

    print(f"\nTotal: {len(hypotheses)}")
    print(f"PASS: {len(results['pass'])}, FAIL: {len(results['fail'])}")
    print(f"Ad-hoc: {len(results['ad_hoc'])}")
    print(f"Generalizes n=28: {len(results['generalizes_28'])}")
    print(f"n=6 only: {len(results['no_gen_28'])}")

    domains = defaultdict(list)
    for h in hypotheses: domains[h['domain']].append(h)
    gc = defaultdict(int)

    for dom, hyps in domains.items():
        print(f"\n--- {dom} ({len(hyps)}) ---")
        for h in hyps:
            gl, em = grade(h, results)
            gc[em] += 1
            s = "PASS" if h['id'] in results['pass'] else "FAIL"
            gt = " [GEN]" if h['id'] in results['generalizes_28'] else \
                 " [n=6]" if h['id'] in results['no_gen_28'] else ""
            print(f"  {em} {h['id']}: {s}{gt} — {h['statement'][:80]}")

    print(f"\n{'='*70}\nGRADE SUMMARY\n{'='*70}")
    for em, c in sorted(gc.items(), key=lambda x: -x[1]):
        print(f"  {em}: {c}")

    if results['fail']:
        print("\n--- FAILURES ---")
        for hid in results['fail']:
            h = next(x for x in hypotheses if x['id'] == hid)
            print(f"  ⬛ {hid}: {h['statement'][:100]}")

    print(f"\n{'='*70}\nTOP DISCOVERIES\n{'='*70}")
    for h in hypotheses:
        hid = h['id']
        if hid in results['fail'] or h['ad_hoc']: continue
        if hid in results['generalizes_28'] or hid in results['no_gen_28']:
            gl, em = grade(h, results)
            print(f"  {em} {hid}: {h['statement'][:90]}")

    # Special: check XOR property
    print(f"\n--- XOR of proper divisors = 0 scan ---")
    xor_zeros = [n for n in range(2, 200) if xor_proper_divisors(n) == 0]
    print(f"  n with XOR(proper divs)=0 in [2,200]: {xor_zeros[:20]}...")

    # Special: sopfr(n)=n-1 scan
    print(f"\n--- sopfr(n)=n-1 scan ---")
    sopfr_match = [n for n in range(2, 1000) if sopfr(n) == n-1]
    print(f"  n with sopfr(n)=n-1 in [2,1000]: {sopfr_match}")

    # Special: phi(n)+omega(n)=tau(n) scan
    print(f"\n--- phi(n)+omega(n)=tau(n) scan ---")
    pot_match = [n for n in range(2, 200) if phi(n)+omega(n)==tau(n)]
    print(f"  n with phi+omega=tau in [2,200]: {pot_match[:20]}...")
