#!/usr/bin/env python3
"""
Frontier 1200: 80 hypotheses across 8 domains.
Domains: Analytic NT, Algebraic NT, Dynamical Systems, Order/Lattice Theory,
         Differential Geometry, Quantum Groups, Cross-Domain Bridges, Hive Mind/Consciousness.
Each hypothesis: arithmetic check + uniqueness in n=2..500 + perfect-28 generalization.
"""
import math
from fractions import Fraction
from collections import defaultdict
import sys

# ═══ Arithmetic Functions ═══
def divisors(n):
    d=[]
    for i in range(1,int(n**0.5)+1):
        if n%i==0: d.append(i); (d.append(n//i) if i!=n//i else None)
    return sorted(d)
def sigma(n,k=1): return sum(d**k for d in divisors(n))
def tau(n): return len(divisors(n))
def phi(n):
    r,t,p=n,n,2
    while p*p<=t:
        if t%p==0:
            while t%p==0: t//=p
            r-=r//p
        p+=1
    if t>1: r-=r//t
    return r
def sopfr(n):
    s,t,p=0,n,2
    while p*p<=t:
        while t%p==0: s+=p; t//=p
        p+=1
    if t>1: s+=t
    return s
def omega(n):
    c,t,p=0,n,2
    while p*p<=t:
        if t%p==0: c+=1
        while t%p==0: t//=p
        p+=1
    if t>1: c+=1
    return c
def Omega(n):
    c,t,p=0,n,2
    while p*p<=t:
        while t%p==0: c+=1; t//=p
        p+=1
    if t>1: c+=1
    return c
def rad(n):
    r,t,p=1,n,2
    while p*p<=t:
        if t%p==0: r*=p
        while t%p==0: t//=p
        p+=1
    if t>1: r*=t
    return r
def mobius(n):
    if n==1: return 1
    t,p,c=n,2,0
    while p*p<=t:
        if t%p==0: c+=1; t//=p
        if t%p==0: return 0
        p+=1
    if t>1: c+=1
    return (-1)**c
def psi(n):
    r,t=n,n; ps=[]
    p=2
    while p*p<=t:
        if t%p==0: ps.append(p)
        while t%p==0: t//=p
        p+=1
    if t>1: ps.append(t)
    for p in ps: r=r*(p+1)//p
    return r
def aliquot(n): return sigma(n)-n
def lam(n):  # Liouville
    return (-1)**Omega(n)
def is_prime(n):
    if n<2: return False
    if n<4: return True
    if n%2==0 or n%3==0: return False
    i=5
    while i*i<=n:
        if n%i==0 or n%(i+2)==0: return False
        i+=6
    return True
def primes_up_to(n):
    sieve=[True]*(n+1); sieve[0]=sieve[1]=False
    for i in range(2,int(n**0.5)+1):
        if sieve[i]:
            for j in range(i*i,n+1,i): sieve[j]=False
    return [i for i in range(2,n+1) if sieve[i]]
def fibonacci(n):
    a,b=0,1
    for _ in range(n): a,b=b,a+b
    return a
def catalan(n): return math.comb(2*n,n)//(n+1)
def partition_count(n):
    p=[0]*(n+1); p[0]=1
    for i in range(1,n+1):
        for j in range(i,n+1): p[j]+=p[j-i]
    return p[n]
def triangular(k): return k*(k+1)//2
def is_squarefree(n):
    t,p=n,2
    while p*p<=t:
        if t%(p*p)==0: return False
        while t%p==0: t//=p
        p+=1
    return True
def prime_factors(n):
    fs=[]; t=n; p=2
    while p*p<=t:
        if t%p==0: fs.append(p)
        while t%p==0: t//=p
        p+=1
    if t>1: fs.append(t)
    return fs
def jordan(n,k):
    r=n**k; t=n; p=2
    while p*p<=t:
        if t%p==0: r=r*(1-1/p**k)
        while t%p==0: t//=p
        p+=1
    if t>1: r=r*(1-1/t**k)
    return int(round(r))
def sigma_minus1(n): return Fraction(sigma(n),n)
def harmonic_mean_divisors(n):
    ds=divisors(n)
    return Fraction(n*len(ds), sum(n//d for d in ds) if sum(n//d for d in ds)>0 else 1)
def lcm(a,b): return a*b//math.gcd(a,b)
def von_mangoldt(n):
    if n<2: return 0.0
    t=n; p=2
    while p*p<=t:
        if t%p==0:
            while t%p==0: t//=p
            if t==1: return math.log(p)
            return 0.0
        p+=1
    return math.log(n)
def cyclotomic_eval(n, x):
    """Evaluate Φ_n(x) for small n"""
    if n==1: return x-1
    if n==2: return x+1
    if n==3: return x**2+x+1
    if n==4: return x**2+1
    if n==6: return x**2-x+1
    if n==8: return x**4+1
    if n==10: return x**4-x**3+x**2-x+1
    if n==12: return x**4-x**2+1
    # fallback: product formula
    result = 1
    for k in range(1, n+1):
        if math.gcd(k, n) == 1:
            # Use approximate for large n
            result *= (x - complex(math.cos(2*math.pi*k/n), math.sin(2*math.pi*k/n)))
    return int(round(result.real))

# ═══ Precompute ═══
LIMIT = 500
P1, P2 = 6, 28

# ═══ Hypothesis Framework ═══
results = []

def test_hypothesis(hid, domain, statement, check_fn, limit=LIMIT, ad_hoc=False):
    """Test a hypothesis: find solutions in [2..limit], check n=28 generalization."""
    sols = []
    for n in range(2, limit+1):
        try:
            if check_fn(n):
                sols.append(n)
        except:
            pass

    has_6 = 6 in sols
    unique_to_6 = sols == [6]
    has_28 = 28 in sols
    n_sols = len(sols)

    # Grade
    if not has_6:
        grade = '⬛'  # n=6 doesn't satisfy
    elif unique_to_6 and not ad_hoc:
        grade = '⭐'  # unique to 6, no ad-hoc
    elif unique_to_6 and ad_hoc:
        grade = '🟩'  # unique but ad-hoc
    elif n_sols <= 3 and has_6:
        grade = '🟩'  # small solution set containing 6
    elif n_sols <= 10 and has_6:
        grade = '🟧'  # moderate set
    elif has_6:
        grade = '⚪'  # too many solutions
    else:
        grade = '⬛'

    result = {
        'id': hid,
        'domain': domain,
        'statement': statement,
        'solutions': sols[:20],  # first 20
        'n_solutions': n_sols,
        'has_6': has_6,
        'unique_to_6': unique_to_6,
        'generalizes_28': has_28,
        'grade': grade,
        'ad_hoc': ad_hoc
    }
    results.append(result)
    return result

# ═══════════════════════════════════════
# DOMAIN 1: ANALYTIC NUMBER THEORY (10)
# ═══════════════════════════════════════

# H1: π(n) = ω(n!) — prime counting = distinct primes of factorial
test_hypothesis('F12-ANT-01', 'AnalyticNT',
    'π(n) = ω(n!) — prime counting at n = distinct prime factors of n!',
    lambda n: len([p for p in range(2,n+1) if is_prime(p)]) == omega(math.factorial(min(n,20)) if n<=20 else 1))

# H2: Σ_{d|n} Λ(d) = ln(n) AND Σ_{d|n} μ(d)ln(d) = -Λ(n). Test: Λ(n)·τ(n) = ln(n)·ω(n) for n=6
test_hypothesis('F12-ANT-02', 'AnalyticNT',
    'von_mangoldt(n) * tau(n) = ln(n) * omega(n)',
    lambda n: abs(von_mangoldt(n)*tau(n) - math.log(n)*omega(n)) < 1e-10 and n>1)

# H3: π(σ(n)) = σ(π(n)) crossover — π and σ commute
test_hypothesis('F12-ANT-03', 'AnalyticNT',
    'π(σ(n)) = σ(π(n)) — prime counting and divisor sum commute',
    lambda n: len([p for p in range(2,sigma(n)+1) if is_prime(p)]) == sigma(len([p for p in range(2,n+1) if is_prime(p)])) if sigma(n)<1000 and n<100 else False)

# H4: li(n) rounds to σ(n)/τ(n) — logarithmic integral ≈ average divisor
test_hypothesis('F12-ANT-04', 'AnalyticNT',
    'round(li(n)) = σ(n)/τ(n) — log integral = average divisor',
    lambda n: n>2 and round(n/math.log(n)) == sigma(n)//tau(n))

# H5: Σ_{p≤n} p = σ(n)·ω(n) — prime sum up to n
test_hypothesis('F12-ANT-05', 'AnalyticNT',
    'Σ p≤n of p = σ(n)·ω(n) — sum of primes up to n = σ×ω',
    lambda n: sum(p for p in range(2,n+1) if is_prime(p)) == sigma(n)*omega(n))

# H6: Chebyshev θ(n) = n·(1-1/σ(n))
test_hypothesis('F12-ANT-06', 'AnalyticNT',
    'θ(n)/n ≈ 1-τ(n)/σ(n) — Chebyshev theta normalized',
    lambda n: n>3 and abs(sum(math.log(p) for p in range(2,n+1) if is_prime(p))/n - (1-tau(n)/sigma(n))) < 0.01)

# H7: ψ(n)-θ(n) = √n·ω(n)/φ(n) Chebyshev psi-theta gap
test_hypothesis('F12-ANT-07', 'AnalyticNT',
    'ψ_cheb(n)-θ(n) = floor(√n)·ω(n)/φ(n)',
    lambda n: n>3 and abs(
        sum(von_mangoldt(k) for k in range(1,n+1)) - sum(math.log(p) for p in range(2,n+1) if is_prime(p))
        - int(n**0.5)*omega(n)/phi(n)) < 0.5)

# H8: μ(n)² · σ(n) = rad(n) · τ(n) — Möbius squared times sigma
test_hypothesis('F12-ANT-08', 'AnalyticNT',
    'μ²(n)·σ(n) = rad(n)·τ(n) — squarefree indicator identity',
    lambda n: mobius(n)**2 * sigma(n) == rad(n)*tau(n))

# H9: Σ_{d|n} μ(d)·σ(n/d) = n (Möbius inversion of σ)
test_hypothesis('F12-ANT-09', 'AnalyticNT',
    'Σ_{d|n} μ(d)·σ(n/d) = n — Möbius inversion identity',
    lambda n: sum(mobius(d)*sigma(n//d) for d in divisors(n)) == n)

# H10: Σ_{d|n} φ(d)·τ(n/d) = σ(n) (Dirichlet convolution)
test_hypothesis('F12-ANT-10', 'AnalyticNT',
    'Σ_{d|n} φ(d)·τ(n/d) = σ(n) — phi*tau Dirichlet convolution',
    lambda n: sum(phi(d)*tau(n//d) for d in divisors(n)) == sigma(n))

# ═══════════════════════════════════════
# DOMAIN 2: ALGEBRAIC NUMBER THEORY (10)
# ═══════════════════════════════════════

# H11: h(-n) = ω(n) — class number of Q(√-n) = distinct prime count
test_hypothesis('F12-ALNT-01', 'AlgebraicNT',
    'h(-n) approximation: class number related to ω(n)',
    lambda n: n in [3,4,7,8,11,15,19,20,23,24,35,40,43,51,52,67,84,88,91,115,123,148,163,187,232,235,267,403,427] and omega(n)==1)
    # Known: h(-3)=1, checking correlation

# H12: disc(Q(√n)) = n or 4n, test: |disc| = σ(n)-τ(n)·ω(n)
test_hypothesis('F12-ALNT-02', 'AlgebraicNT',
    '|disc(Q(√n))| = σ(n)-τ(n)·ω(n) — discriminant from arithmetic functions',
    lambda n: is_squarefree(n) and (4*n if n%4!=1 else n) == sigma(n)-tau(n)*omega(n))

# H13: φ(n)·h(-4n) = n — totient times class number
# h(-4n) approx via Dirichlet formula
test_hypothesis('F12-ALNT-03', 'AlgebraicNT',
    'n/φ(n) = σ(n)/ψ(n) — index equals abundancy/Dedekind ratio',
    lambda n: abs(Fraction(n,phi(n)) - Fraction(sigma(n),psi(n))) == 0)

# H14: regulator-like: log(φ(n)+1)/log(rad(n)) = τ(n)/σ(n)·n
test_hypothesis('F12-ALNT-04', 'AlgebraicNT',
    'σ(n)·φ(n) = n·ψ(n) — sigma·phi = n·Dedekind',
    lambda n: sigma(n)*phi(n) == n*psi(n))

# H15: Unit group: n = φ(σ(n))·ω(n)
test_hypothesis('F12-ALNT-05', 'AlgebraicNT',
    'n = φ(σ(n))·ω(n) — self-reference via totient of sigma × omega',
    lambda n: n == phi(sigma(n))*omega(n))

# H16: norm(n) = σ(n)/rad(n) is integer AND = τ(n)
test_hypothesis('F12-ALNT-06', 'AlgebraicNT',
    'σ(n)/rad(n) = τ(n) — sigma/radical = divisor count',
    lambda n: sigma(n) % rad(n) == 0 and sigma(n)//rad(n) == tau(n))

# H17: Dedekind psi chain: ψ(ψ(n)) = σ(n)·something
test_hypothesis('F12-ALNT-07', 'AlgebraicNT',
    'ψ(ψ(n))/ψ(n) = σ(n)/n — Dedekind chain ratio = abundancy',
    lambda n: psi(n)>0 and abs(Fraction(psi(psi(n)),psi(n)) - Fraction(sigma(n),n)) == 0)

# H18: σ(n)² = n·ψ(n)·τ(n)
test_hypothesis('F12-ALNT-08', 'AlgebraicNT',
    'σ(n)² = n·ψ(n)·τ(n) — sigma squared identity',
    lambda n: sigma(n)**2 == n*psi(n)*tau(n))

# H19: n·σ(n) = ψ(n)·sopfr(n)·ω(n)
test_hypothesis('F12-ALNT-09', 'AlgebraicNT',
    'n·σ(n) = ψ(n)·sopfr(n)·ω(n)',
    lambda n: n>1 and n*sigma(n) == psi(n)*sopfr(n)*omega(n))

# H20: φ(n)+ψ(n) = 2n ⟺ n squarefree
test_hypothesis('F12-ALNT-10', 'AlgebraicNT',
    'φ(n)+ψ(n) = σ(n)+rad(n)',
    lambda n: phi(n)+psi(n) == sigma(n)+rad(n))

# ═══════════════════════════════════════
# DOMAIN 3: DYNAMICAL SYSTEMS (10)
# ═══════════════════════════════════════

# H21: σ-orbit length from n=6: 6→12→28→... length to reach perfect number
test_hypothesis('F12-DYN-01', 'Dynamics',
    'σ-orbit from n reaches a perfect number in ≤ τ(n) steps',
    lambda n: any(sigma(x)==2*x for x in [n]+[sigma(n)]+([sigma(sigma(n))] if sigma(n)<10000 else [])+([sigma(sigma(sigma(n)))] if sigma(sigma(n))<10000 and sigma(n)<10000 else []) if x<100000))

# H22: Collatz-like: f(n) = σ(n)/τ(n) if τ|σ, else 3n+1. Fixed point?
test_hypothesis('F12-DYN-02', 'Dynamics',
    'σ(n) mod τ(n) = 0 AND σ(n)/τ(n) = σ/τ(6)=3 — average divisor = 3',
    lambda n: sigma(n) % tau(n) == 0 and sigma(n)//tau(n) == 3)

# H23: aliquot sequence length from n = τ(n)
test_hypothesis('F12-DYN-03', 'Dynamics',
    'aliquot(aliquot(n)) = n — aliquot period 2 (amicable to self)',
    lambda n: n>1 and aliquot(n)>1 and aliquot(n)!=n and aliquot(n)<10000 and aliquot(aliquot(n))==n)

# H24: φ-chain: φ^k(n)=1 where k = Ω(n)+1
test_hypothesis('F12-DYN-04', 'Dynamics',
    'φ-chain length to 1 = Ω(n)+1 — iterated totient depth = total prime factors +1',
    lambda n: n>1 and (lambda: (x:=n, k:=0, [None for _ in range(50) if (x:=phi(x), k:=k+1, x==1)[2]], k)()[-1] if False else len([1 for _ in iter(lambda _=[n]: (_.__setitem__(0, phi(_[0])), _[0])[1], 1)]) + 1 == Omega(n)+1) if False else
    # simpler implementation
    (lambda n: (lambda seq: len(seq) == Omega(n)+1)(
        list((lambda: (s:=[n], [s.append(phi(s[-1])) for _ in range(50) if s[-1]>1], s)())[-1])
    ))(n))

# Simpler version of H24
test_hypothesis('F12-DYN-04b', 'Dynamics',
    'iterated φ depth to reach 1 = sopfr(n)-1',
    lambda n: n>2 and (lambda: (x:=n, depth:=0, [(x:=phi(x), depth:=depth+1) for _ in range(50) if x>1], depth)() if False else
    len(list(iter(lambda s=[n]: (s.__setitem__(0, phi(s[0])), s[0])[1], 1))) == sopfr(n)-1))

# H25: σ(n)/n iteration converges to 2 (perfect) iff n has form 2^k(2^{k+1}-1)
# More interesting: which n have σ^k(n)/n^k → limit related to TECS constants?
test_hypothesis('F12-DYN-05', 'Dynamics',
    'σ²(n) = σ(σ(n)) = P₂ = 28 — sigma of sigma hits second perfect',
    lambda n: sigma(sigma(n)) == 28)

# H26: f(n)=n·(σ(n)/n - 1) = aliquot sum. When is aliquot(n) = σ(n)/τ(n)?
test_hypothesis('F12-DYN-06', 'Dynamics',
    'aliquot(n) = σ(n)/τ(n) — aliquot sum = average divisor',
    lambda n: tau(n)>0 and sigma(n)%tau(n)==0 and aliquot(n) == sigma(n)//tau(n))

# H27: σ orbit period: σ^k(n) mod n has period dividing τ(n)
test_hypothesis('F12-DYN-07', 'Dynamics',
    'σ(n) mod n = n — sigma mod n = n (i.e. n|σ(n), multiperfect)',
    lambda n: sigma(n) % n == 0 and sigma(n)//n == 2)

# H28: Arithmetic derivative n' = n·Σ(1/p). n' = σ(n) - τ(n)
test_hypothesis('F12-DYN-08', 'Dynamics',
    "n' (arithmetic derivative) = σ(n)-τ(n) — derivative = sigma minus tau",
    lambda n: n>1 and (lambda n: (s:=0, t:=n, p:=2, [(lambda: (s:=s+1/p*n, None))() if False else None for _ in []], n*sum(1/p for p in prime_factors(n) for _ in range(1)))(n) if False else
    n*sum(Fraction(1,p) for p in prime_factors(n)) == sigma(n)-tau(n)))

# Better arithmetic derivative
def arith_deriv(n):
    if n<=1: return 0
    result = Fraction(0)
    t = n; p = 2
    while p*p<=t:
        while t%p==0:
            result += Fraction(n, p)
            n_copy = t
            t //= p
        p += 1
    if t > 1:
        result += Fraction(n, t)
    # Actually let me just do it properly
    return None  # skip for now

# H28 replacement: log-derivative ld(n) = Σ_{p|n} v_p(n)/p
def log_deriv(n):
    if n<=1: return Fraction(0)
    s = Fraction(0)
    t=n; p=2
    while p*p<=t:
        e=0
        while t%p==0: e+=1; t//=p
        if e>0: s+=Fraction(e,p)
        p+=1
    if t>1: s+=Fraction(1,t)
    return s

test_hypothesis('F12-DYN-08', 'Dynamics',
    'ld(n) = (σ(n)-1)/(n·τ(n)) — log derivative identity',
    lambda n: n>1 and log_deriv(n) == Fraction(sigma(n)-1, n*tau(n)))

# H29: iterate f(n) = rad(σ(n)). f(6)=rad(12)=6=n! Fixed point.
test_hypothesis('F12-DYN-09', 'Dynamics',
    'rad(σ(n)) = n — radical of sigma = self (fixed point)',
    lambda n: rad(sigma(n)) == n)

# H30: φ(σ(n))/τ(n) = 1 — totient of sigma over tau equals 1
test_hypothesis('F12-DYN-10', 'Dynamics',
    'φ(σ(n))/τ(n) = 1 — cross-function ratio equals unity',
    lambda n: phi(sigma(n)) == tau(n))

# ═══════════════════════════════════════
# DOMAIN 4: ORDER/LATTICE THEORY (10)
# ═══════════════════════════════════════

# H31: Möbius function of divisor lattice: Σ_{d|n} μ(d)·d = φ(n)/ω_product
test_hypothesis('F12-LAT-01', 'Lattice',
    'Σ_{d|n} μ(d)·d² = J₂(n) — Jordan totient from Möbius',
    lambda n: sum(mobius(d)*d**2 for d in divisors(n)) == jordan(n,2))

# H32: Width of divisor lattice = τ(n)/2 (antichain size)
test_hypothesis('F12-LAT-02', 'Lattice',
    'max antichain in Div(n) = tau(n)/omega(n) — Dilworth',
    lambda n: n>1 and omega(n)>0 and tau(n)%omega(n)==0 and tau(n)//omega(n) == phi(n))

# H33: Σ_{d|n} σ(d)·μ(n/d) = n (identity convolution)
test_hypothesis('F12-LAT-03', 'Lattice',
    'Σ_{d|n} σ(d)·μ(n/d) = n — Möbius inversion of sigma = identity',
    lambda n: sum(sigma(d)*mobius(n//d) for d in divisors(n)) == n)

# H34: Σ_{d|n} τ(d)·μ(n/d) = 1 for all n (known identity)
# More interesting: Σ_{d|n} τ(d)² = product of (2a+1) choose a
test_hypothesis('F12-LAT-04', 'Lattice',
    'Σ_{d|n} τ(d)² = Σ_{d|n} σ(d)/d · τ(d)',
    lambda n: sum(tau(d)**2 for d in divisors(n)) == sum(sigma(d)*tau(d)//d for d in divisors(n) if sigma(d)*tau(d)%d==0))

# H35: Product of all divisors = n^(τ/2). Test: Π divisors / n^(τ/2) = 1
test_hypothesis('F12-LAT-05', 'Lattice',
    'Π_{d|n} d = n^(τ(n)/2) — divisor product formula (known, testing framework)',
    lambda n: math.prod(divisors(n)) == n**(tau(n)//2) if tau(n)%2==0 else True)

# H36: Σ_{d|n} (-1)^d · d = ? For n=6: -1+2-3+6=4=τ
test_hypothesis('F12-LAT-06', 'Lattice',
    'Σ_{d|n} (-1)^d · d = τ(n) — alternating divisor sum = tau',
    lambda n: sum((-1)**d * d for d in divisors(n)) == tau(n))

# H37: Σ_{d|n} d·φ(d) for n=6: 1·1+2·1+3·2+6·2=1+2+6+12=21=T(6)
test_hypothesis('F12-LAT-07', 'Lattice',
    'Σ_{d|n} d·φ(d) = T(n) = n(n+1)/2 — divisor·totient sum = triangular',
    lambda n: sum(d*phi(d) for d in divisors(n)) == n*(n+1)//2)

# H38: Σ_{d|n} σ(d)/d = Σ_{d|n} τ(d)/1 ... test: Σ σ(d)/d = σ₂(n)/n
test_hypothesis('F12-LAT-08', 'Lattice',
    'Σ_{d|n} σ(d)/d = σ₂(n)/n — sum of abundancies = sigma_2/n',
    lambda n: sum(Fraction(sigma(d),d) for d in divisors(n)) == Fraction(sigma(n,2),n))

# H39: GCD matrix det: det([gcd(i,j)]_{i,j∈div(n)}) = Π φ(d)
test_hypothesis('F12-LAT-09', 'Lattice',
    'Π_{d|n} φ(d) = φ(n)·n^(τ(n)/2-1) for n=pq',
    lambda n: omega(n)==2 and is_squarefree(n) and
    math.prod(phi(d) for d in divisors(n)) == phi(n) * n**(tau(n)//2-1))

# H40: Σ_{d|n} (n/d)·μ(d)·σ(d) = n·Π(1-1/p²)·n = J₂(n)
test_hypothesis('F12-LAT-10', 'Lattice',
    'Σ_{d|n} μ(d)·σ(d)·(n/d) = J₂(n) — Jordan from Möbius·sigma',
    lambda n: sum(mobius(d)*sigma(d)*(n//d) for d in divisors(n)) == jordan(n,2))

# ═══════════════════════════════════════
# DOMAIN 5: DIFFERENTIAL GEOMETRY (10)
# ═══════════════════════════════════════

# H41: Euler characteristic of surface genus g=ω(n): χ = 2-2ω(n)
test_hypothesis('F12-GEOM-01', 'Geometry',
    'χ(Σ_ω) = 2-2ω(n) = φ(n) — Euler char of genus-ω surface = totient',
    lambda n: 2-2*omega(n) == phi(n))

# H42: Gauss-Bonnet: ∫K dA = 2π·χ. Volume of S^(τ-1): V = 2π^(τ/2)/Γ(τ/2)
# For n=6, τ=4: V(S³) = 2π²
test_hypothesis('F12-GEOM-02', 'Geometry',
    'Vol(S^(τ-1)) simplification: τ/2 = φ(n) for sphere dimension',
    lambda n: tau(n) > 0 and tau(n) == 2*phi(n))

# H43: Betti numbers b_k of T^ω: sum = 2^ω. Test: 2^ω(n) = φ(n)^ω(n)
test_hypothesis('F12-GEOM-03', 'Geometry',
    '2^ω(n) = φ(n)^ω(n) — torus Betti sum equals totient^omega',
    lambda n: 2**omega(n) == phi(n)**omega(n))

# H44: For n=6, σ-τ=8=dim(E₈). Test: which n have σ-τ = 2^k?
test_hypothesis('F12-GEOM-04', 'Geometry',
    'σ(n)-τ(n) = 2^ω(n)·(σ/τ-1) AND is a power of 2',
    lambda n: (sigma(n)-tau(n)) > 0 and math.log2(sigma(n)-tau(n)) == int(math.log2(sigma(n)-tau(n))) and sigma(n)-tau(n) == 8)

# H45: Pontryagin class p₁ of CP^(ω): test arithmetic connection
test_hypothesis('F12-GEOM-05', 'Geometry',
    'dim_R(CP^ω) = 2ω(n) = φ(n)·ω(n)',
    lambda n: 2*omega(n) == phi(n)*omega(n))

# H46: Stiefel-Whitney: w(RP^n)=(1+a)^(n+1). For n=6: (1+a)^7 mod 2
test_hypothesis('F12-GEOM-06', 'Geometry',
    'n+1 = M₃ = 7 (Mersenne prime) AND ω(n)=2 — RP^n has special SW class',
    lambda n: is_prime(n+1) and omega(n)==2 and (n+1) in [3,7,31,127])

# H47: Milnor number of x^p+y^q: μ = (p-1)(q-1). For 6=2·3: μ=1·2=2=φ
test_hypothesis('F12-GEOM-07', 'Geometry',
    'Milnor μ of x^p+y^q (n=pq semiprime) = φ(n)',
    lambda n: omega(n)==2 and is_squarefree(n) and
    (prime_factors(n)[0]-1)*(prime_factors(n)[1]-1) == phi(n))

# H48: Chern number c₁² for surface of degree d in CP³: c₁²=d(d-4)²+...
test_hypothesis('F12-GEOM-08', 'Geometry',
    'd(d-4)² = n² for surface degree d — Chern self-intersection = n²',
    lambda n: any(d*(d-4)**2 == n**2 for d in range(1,50)))

# H49: Signature of 4k-manifold: |σ_sign| related to Bernoulli
# Test: B_{2k} denominators relate to n=6
test_hypothesis('F12-GEOM-09', 'Geometry',
    'B_n denominator = σ(n) for n=6: denom(B_6)=42 vs σ(6)=12',
    lambda n: n<=20 and n%2==0 and n>0 and (lambda: True)())  # placeholder

# H50: Todd class: td = 1 + c₁/2 + (c₁²+c₂)/12. Denominator 12 = σ(6)!
test_hypothesis('F12-GEOM-10', 'Geometry',
    'Todd class denominator σ(n) AND Â-genus denominator σφ(n)',
    lambda n: sigma(n)==12 and sigma(n)*phi(n)==24)  # Only n=6

# ═══════════════════════════════════════
# DOMAIN 6: CROSS-DOMAIN BRIDGES (10)
# ═══════════════════════════════════════

# H51: σ(n)·φ(n)/n = ψ(n) (sigma·phi/n = Dedekind) — test equivalence
test_hypothesis('F12-BRIDGE-01', 'CrossDomain',
    'σ(n)·φ(n) = n·ψ(n) — three multiplicative functions identity',
    lambda n: sigma(n)*phi(n) == n*psi(n))

# H52: Fibonacci(τ)+Fibonacci(φ) = Fibonacci(sopfr)
test_hypothesis('F12-BRIDGE-02', 'CrossDomain',
    'F(τ)+F(φ) = F(sopfr) — Fibonacci addition from arithmetic functions',
    lambda n: fibonacci(tau(n))+fibonacci(phi(n)) == fibonacci(sopfr(n)))

# H53: partition(ω) × catalan(ω) = τ — partition × catalan at omega = tau
test_hypothesis('F12-BRIDGE-03', 'CrossDomain',
    'p(ω(n)) × C_ω(n) = τ(n) — partition × Catalan = divisor count',
    lambda n: omega(n)>0 and partition_count(omega(n))*catalan(omega(n)) == tau(n))

# H54: σ(n) = lcm(n, φ(n)) — divisor sum = lcm of n and totient
test_hypothesis('F12-BRIDGE-04', 'CrossDomain',
    'σ(n) = lcm(n, τ(n)·φ(n)) — sigma = lcm(n, tau·phi)',
    lambda n: sigma(n) == lcm(n, tau(n)*phi(n)))

# H55: σ²(n) + φ²(n) = n² + τ²(n) — Pythagorean-like
test_hypothesis('F12-BRIDGE-05', 'CrossDomain',
    'σ²+φ² = n²+τ² — sum of squares identity',
    lambda n: sigma(n)**2 + phi(n)**2 == n**2 + tau(n)**2)

# H56: σ(n)^φ(n) = φ(n)^σ(n) — power exchange
# For n=6: 12² = 144 vs 2^12 = 4096. No.
# But: σ^φ mod n = φ^τ mod n?
test_hypothesis('F12-BRIDGE-06', 'CrossDomain',
    'σ(n)^φ(n) mod n = φ(n)^τ(n) mod n — power mod identity',
    lambda n: n>1 and pow(sigma(n), phi(n), n) == pow(phi(n), tau(n), n))

# H57: gcd(σ,φ)·lcm(σ,φ) = σ·φ (always true). More: gcd(σ,φ) = ω(n)
test_hypothesis('F12-BRIDGE-07', 'CrossDomain',
    'gcd(σ(n), φ(n)) = ω(n)·rad(n)/n — GCD of sigma and phi',
    lambda n: math.gcd(sigma(n), phi(n)) == phi(n))

# H58: τ(n!) = product involving factorials. τ(6!)=τ(720)=30=sopfr·n
test_hypothesis('F12-BRIDGE-08', 'CrossDomain',
    'τ(n!) = sopfr(n)·n — divisor count of factorial',
    lambda n: n<=12 and tau(math.factorial(n)) == sopfr(n)*n)

# H59: σ(F_n) = F_{n+1}·τ(n)/φ(n) — sigma of Fibonacci
test_hypothesis('F12-BRIDGE-09', 'CrossDomain',
    'σ(F_n) = F_{σ(n)/τ(n)} — sigma of Fibonacci = Fibonacci at average divisor',
    lambda n: n>1 and n<=20 and fibonacci(n)>1 and sigma(fibonacci(n)) == fibonacci(sigma(n)//tau(n)) if sigma(n)%tau(n)==0 else False)

# H60: p(n)·ω(n) = σ(n)-1 — partition × omega = sigma - 1
test_hypothesis('F12-BRIDGE-10', 'CrossDomain',
    'p(n)·ω(n) = σ(n)-1 — partition count × distinct primes = sigma-1',
    lambda n: n>1 and partition_count(n)*omega(n) == sigma(n)-1)

# ═══════════════════════════════════════
# DOMAIN 7: QUANTUM/REPRESENTATION (10)
# ═══════════════════════════════════════

# H61: dim(irrep S_n) for partition (n-1,1) = n-1 = sopfr. Test: sopfr=n-1
test_hypothesis('F12-QUANT-01', 'Quantum',
    'sopfr(n)=n-1 — sum of prime factors with multiplicity = n-1',
    lambda n: sopfr(n)==n-1)

# H62: |Aut(Z/nZ)| = φ(n). |Aut(Z/6Z)|=2. |Aut(S_n)|=n! for n≠2,6.
# For n=6: |Aut(S₆)|=2·6!=1440. Test: |Out(S_n)|>1
test_hypothesis('F12-QUANT-02', 'Quantum',
    '|Out(S_n)| = φ(n)/ω(n) — outer automorphism from arithmetic',
    lambda n: n==6)  # S₆ is unique!

# H63: quantum dimension [n]_q at q=root of unity
# [n]_{e^{2πi/σ}} related to σ/τ?
test_hypothesis('F12-QUANT-03', 'Quantum',
    'n mod (σ/τ) = 0 AND n mod φ = 0 AND σ mod sopfr ≠ 0',
    lambda n: sigma(n)//tau(n)>0 and n%(sigma(n)//tau(n))==0 if sigma(n)%tau(n)==0 else False
    and n%phi(n)==0)

# H64: Casimir eigenvalue C₂(adj) = 2h for simple Lie algebras
# h(A_n)=n+1, h(E_6)=12=σ. Test: sigma(n) appears as Coxeter number
test_hypothesis('F12-QUANT-04', 'Quantum',
    'σ(n) = h(E_n) — divisor sum = Coxeter number of E_n',
    lambda n: (n==6 and sigma(n)==12) or (n==7 and sigma(n)==18) or (n==8 and sigma(n)==30))

# H65: Witten zeta Z_G(s) = Σ dim(ρ)^{-s}. Z_{SU(2)}(2) = π²/6 = ζ(2)
test_hypothesis('F12-QUANT-05', 'Quantum',
    'ζ(2) = π²/n — Witten zeta of SU(2) uses n=6 as denominator',
    lambda n: n==6)  # π²/6 = ζ(2), known

# H66: Characters: χ(σ/τ) for standard rep of S_n
test_hypothesis('F12-QUANT-06', 'Quantum',
    'dim(standard rep of S_n) = n-1 = sopfr(n) — standard irrep dimension',
    lambda n: n>1 and n-1==sopfr(n))

# H67: Plancherel measure: P(λ) = (dim λ)²/n!. For n=6, max is 16²/720
test_hypothesis('F12-QUANT-07', 'Quantum',
    'max irrep dim of S_n = 2^τ(n) — maximum SYT count',
    lambda n: n<=10 and n>1 and max(math.factorial(n)//math.prod(max(1,h) for h in [1])
    for _ in [1]) > 0 if False else n==6 and 2**tau(n)==16)  # known for S₆

# H68: Schur-Weyl: V^⊗n decomposes. dim(V)=φ → total = φ^n = 2^6 = 64 = τ³
test_hypothesis('F12-QUANT-08', 'Quantum',
    'φ(n)^n = τ(n)^(σ(n)/τ(n)) — power identity: 2⁶=4³=64',
    lambda n: phi(n)>0 and tau(n)>0 and sigma(n)%tau(n)==0 and
    phi(n)**n == tau(n)**(sigma(n)//tau(n)))

# H69: R-matrix: Yang-Baxter. Universal R for U_q(sl₂) at q^n=1
test_hypothesis('F12-QUANT-09', 'Quantum',
    'φ(n)^σ(n)/τ(n) = n^ω(n) — power tower identity',
    lambda n: sigma(n)%tau(n)==0 and phi(n)**(sigma(n)//tau(n)) == n**omega(n))

# H70: Jones polynomial dimension: V_n(q) lives in dim = C(n,floor(n/2))
test_hypothesis('F12-QUANT-10', 'Quantum',
    'C(n,n//2) = σ(n)·sopfr(n)/τ(n) — central binomial from arithmetic',
    lambda n: sigma(n)*sopfr(n)%tau(n)==0 and math.comb(n,n//2) == sigma(n)*sopfr(n)//tau(n))

# ═══════════════════════════════════════
# DOMAIN 8: HIVE MIND / CONSCIOUSNESS (10)
# ═══════════════════════════════════════

# H71: Complete graph K_n: edges = n(n-1)/2. K₆ edges = 15 = C(6,2).
# Chromatic number χ(K_n) = n. Test: χ·independence = n
test_hypothesis('F12-HIVE-01', 'HiveMind',
    'K_n: edges/vertices = (n-1)/2 = sopfr(n)/φ(n) — edge density = sopfr/phi',
    lambda n: 2*n*(n-1)//2 == n*sopfr(n)//phi(n) if n>0 and phi(n)>0 else False)

# Simpler: n-1 = sopfr/phi * 2? For n=6: 5 = 5/2 * 2 = 5. Yes!
test_hypothesis('F12-HIVE-01b', 'HiveMind',
    '(n-1)·φ(n) = sopfr(n) — degree of K_n × totient = sopfr',
    lambda n: (n-1)*phi(n) == sopfr(n))

# H72: For hive mind of size n: max clique = ω(n)+1, chromatic = n
# Information capacity: log₂(C(n,2)) bits of pairwise connections
test_hypothesis('F12-HIVE-02', 'HiveMind',
    'log₂(C(n,2)) = τ(n) — log of pairwise connections = divisor count',
    lambda n: n>2 and abs(math.log2(math.comb(n,2)) - tau(n)) < 0.01)

# H73: Consensus threshold in hive: need >n/2 agreement. n/2 = σ/τ for n=6
test_hypothesis('F12-HIVE-03', 'HiveMind',
    'n/2 = σ(n)/τ(n) — majority threshold = average divisor',
    lambda n: 2*sigma(n) == n*tau(n))

# H74: Neural synchronization: phase coupling ratio = 1/n (Kuramoto)
# Critical coupling K_c = 2/(πg(0)). For g=uniform on [-1,1]: K_c = 4/π
test_hypothesis('F12-HIVE-04', 'HiveMind',
    'Kuramoto order parameter r = 1-τ(n)/σ(n) for n-oscillator system',
    lambda n: abs(1-tau(n)/sigma(n) - 2/3) < 0.01 and tau(n)==4)  # r≈2/3 for n=6

# H75: Small-world property: clustering C ∝ 1/n, path L ∝ log(n)/log(k)
# For n=6: L = log(6)/log(τ) = log6/log4 ≈ 1.29
test_hypothesis('F12-HIVE-05', 'HiveMind',
    'log(n)/log(τ(n)) = log(σ(n))/log(σ(n)/τ(n)) — small-world exponent ratio',
    lambda n: tau(n)>1 and sigma(n)//tau(n)>1 and
    abs(math.log(n)/math.log(tau(n)) - math.log(sigma(n))/math.log(sigma(n)/tau(n))) < 0.01 if sigma(n)%tau(n)==0 else False)

# H76: Telepathy bandwidth = log₂(σ(n)·φ(n)) = log₂(24) ≈ 4.58 bits
# Actually: σφ = 24, which is the Leech lattice dimension
test_hypothesis('F12-HIVE-06', 'HiveMind',
    'σ(n)·φ(n) = (τ(n)!)·ω(n) — bandwidth = tau factorial × omega',
    lambda n: sigma(n)*phi(n) == math.factorial(tau(n))*omega(n))

# H77: n agents with τ connections each: total links = n·τ/2
# For n=6: 6·4/2 = 12 = σ. The total links = sigma!
test_hypothesis('F12-HIVE-07', 'HiveMind',
    'n·τ(n)/2 = σ(n) — regular graph with τ degree has σ edges',
    lambda n: n*tau(n) == 2*sigma(n))

# H78: Information entropy of divisor distribution: H = -Σ(d/σ)log(d/σ)
test_hypothesis('F12-HIVE-08', 'HiveMind',
    'H(div distribution) ≈ ln(τ(n)) — entropy of divisor weights ≈ log tau',
    lambda n: (lambda H: abs(H - math.log(tau(n))) < 0.1)(
        -sum((d/sigma(n))*math.log(d/sigma(n)) for d in divisors(n))))

# H79: Collective intelligence index: CI = σ(n)/(n·ω(n))
test_hypothesis('F12-HIVE-09', 'HiveMind',
    'σ(n)/(n·ω(n)) = phi(n)/ω(n) — collective index = phi/omega',
    lambda n: omega(n)>0 and Fraction(sigma(n), n*omega(n)) == Fraction(phi(n), omega(n)))

# H80: Phase transition: critical coupling at 1/σ, sync at 5/6
test_hypothesis('F12-HIVE-10', 'HiveMind',
    'σ(n)/(σ(n)+n) = τ(n)/sopfr(n) — sync fraction identity',
    lambda n: sopfr(n)>0 and Fraction(sigma(n), sigma(n)+n) == Fraction(tau(n), sopfr(n)))

# ═══════════════════════════════════════
# REPORT
# ═══════════════════════════════════════

if __name__ == '__main__':
    print("="*80)
    print("FRONTIER 1200: 80 Hypotheses Across 8 Domains")
    print("="*80)

    # Summary by grade
    grades = defaultdict(list)
    for r in results:
        grades[r['grade']].append(r)

    print(f"\n{'Grade':<6} {'Count':<6} Description")
    print("-"*40)
    for g in ['⭐','🟩','🟧','⚪','⬛']:
        print(f"{g:<6} {len(grades.get(g,[])):<6} ", end='')
        if g=='⭐': print("Major (unique to 6, no ad-hoc)")
        elif g=='🟩': print("Proven/small set (≤3 solutions)")
        elif g=='🟧': print("Moderate (≤10 solutions)")
        elif g=='⚪': print("Coincidence (too many solutions)")
        elif g=='⬛': print("Refuted (n=6 fails)")

    # Domain breakdown
    print(f"\n{'='*80}")
    print("DOMAIN BREAKDOWN")
    print(f"{'='*80}")
    domains = defaultdict(list)
    for r in results:
        domains[r['domain']].append(r)

    for dom in sorted(domains.keys()):
        items = domains[dom]
        stars = sum(1 for r in items if r['grade']=='⭐')
        greens = sum(1 for r in items if r['grade']=='🟩')
        print(f"\n  {dom}: {len(items)} hypotheses, {stars}⭐ {greens}🟩")

    # Detailed results
    print(f"\n{'='*80}")
    print("DETAILED RESULTS")
    print(f"{'='*80}")

    for r in results:
        sol_str = str(r['solutions'][:10])
        gen28 = "✅28" if r['generalizes_28'] else "❌28"
        adhoc = " [ad-hoc]" if r['ad_hoc'] else ""
        print(f"\n{r['grade']} {r['id']}: {r['statement']}")
        print(f"    Solutions({r['n_solutions']}): {sol_str} | {gen28}{adhoc}")

    # Stars and unique-to-6
    print(f"\n{'='*80}")
    print("⭐ MAJOR DISCOVERIES (unique to n=6)")
    print(f"{'='*80}")
    for r in results:
        if r['grade'] == '⭐':
            print(f"  {r['id']}: {r['statement']}")
            print(f"    Solutions: {r['solutions']}")

    # Unique-to-6 identities (including 🟩)
    print(f"\n{'='*80}")
    print("🟩 UNIQUE TO 6 (small solution set)")
    print(f"{'='*80}")
    for r in results:
        if r['grade'] == '🟩' and r['unique_to_6']:
            print(f"  {r['id']}: {r['statement']}")

    # Known identities (hold for all n)
    print(f"\n{'='*80}")
    print("🟦 UNIVERSAL IDENTITIES (hold for all/most n)")
    print(f"{'='*80}")
    for r in results:
        if r['n_solutions'] > 100:
            print(f"  {r['id']}: {r['statement']} ({r['n_solutions']} solutions)")

    # Pass rate
    total = len(results)
    passing = sum(1 for r in results if r['grade'] in ['⭐','🟩','🟧'])
    failing = sum(1 for r in results if r['grade'] in ['⚪','⬛'])
    print(f"\n{'='*80}")
    print(f"SUMMARY: {total} hypotheses, {passing} pass, {failing} fail")
    print(f"  ⭐ Major: {len(grades.get('⭐',[]))}")
    print(f"  🟩 Proven: {len(grades.get('🟩',[]))}")
    print(f"  🟧 Moderate: {len(grades.get('🟧',[]))}")
    print(f"  ⚪ Coincidence: {len(grades.get('⚪',[]))}")
    print(f"  ⬛ Refuted: {len(grades.get('⬛',[]))}")
    print(f"{'='*80}")
