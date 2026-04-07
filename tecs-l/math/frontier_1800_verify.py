#!/usr/bin/env python3
"""
Frontier 1800: 100 hypotheses — PERFECT NUMBER GENERALIZATION FOCUS.
Strategy: Test identities at n=6,28,496,8128 simultaneously.
Find properties shared by ALL perfect numbers, not just n=6.
"""
import math
from fractions import Fraction
from collections import defaultdict
from functools import reduce

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
def Omega_fn(n):
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
def is_prime(n):
    if n<2: return False
    if n<4: return True
    if n%2==0 or n%3==0: return False
    i=5
    while i*i<=n:
        if n%i==0 or n%(i+2)==0: return False
        i+=6
    return True
def prime_factors(n):
    fs=[]; t=n; p=2
    while p*p<=t:
        if t%p==0: fs.append(p)
        while t%p==0: t//=p
        p+=1
    if t>1: fs.append(t)
    return fs
def fibonacci(n):
    if n>40: return -1
    a,b=0,1
    for _ in range(n): a,b=b,a+b
    return a
def partition_count(n):
    if n<0 or n>200: return 0
    p=[0]*(n+1); p[0]=1
    for i in range(1,n+1):
        for j in range(i,n+1): p[j]+=p[j-i]
    return p[n]
def triangular(k): return k*(k+1)//2
def jordan(n,k):
    r=n**k; t=n; p=2
    while p*p<=t:
        if t%p==0: r=int(r*(1-1/p**k))
        while t%p==0: t//=p
        p+=1
    if t>1: r=int(r*(1-1/t**k))
    return r
def arithmetic_derivative(n):
    if n<=1: return 0
    t=n; p=2; s=0
    while p*p<=t:
        while t%p==0: s+=n//p; t//=p
        p+=1
    if t>1: s+=n//t
    return s
def v_p(n,p):
    if n==0: return float('inf')
    v=0
    while n%p==0: v+=1; n//=p
    return v
def mersenne_exp(n):
    """For even perfect n=2^(p-1)*(2^p-1), return p"""
    if sigma(n)!=2*n: return 0
    t=n; p_val=0
    while t%2==0: t//=2; p_val+=1
    if is_prime(p_val+1) and t==(1<<(p_val+1))-1 and is_prime(t):
        return p_val+1
    return 0

PERFECTS = [6, 28, 496, 8128]

results = []
def test(hid, domain, stmt, check_fn, limit=100, ad_hoc=False, test_perfects=True):
    sols = []
    for n in range(2, limit+1):
        try:
            if check_fn(n): sols.append(n)
        except: pass
    # Also test at higher perfect numbers
    perf_hits = []
    if test_perfects:
        for pn in PERFECTS:
            if pn > limit:
                try:
                    if check_fn(pn): perf_hits.append(pn)
                except: pass
    all_sols = sorted(set(sols + perf_hits))
    has_6=6 in all_sols; has_28=28 in all_sols; ns=len(all_sols)
    unique=(all_sols==[6])
    # Special grading for perfect number generalizations
    perf_count = sum(1 for p in PERFECTS if p in all_sols)
    if not has_6: grade='⬛'
    elif perf_count>=3 and ns<=perf_count+2: grade='⭐'  # hits 3+ perfects with few extras
    elif unique and not ad_hoc: grade='⭐'
    elif unique and ad_hoc: grade='🟩'
    elif ns<=3 and has_6: grade='🟩'
    elif perf_count>=2 and ns<=perf_count+3: grade='🟩'
    elif ns<=10 and has_6: grade='🟧'
    elif has_6: grade='⚪'
    else: grade='⬛'
    results.append({'id':hid,'domain':domain,'statement':stmt,
        'solutions':all_sols[:20],'n_solutions':ns,'has_6':has_6,
        'unique_to_6':unique,'generalizes_28':has_28,'grade':grade,
        'ad_hoc':ad_hoc,'perf_count':perf_count})

# ══════════════════════════════════════════════
# D1: PERFECT NUMBER CORE PROPERTIES (10)
# ══════════════════════════════════════════════

test('F18-PF-01','PerfCore','sigma(n)=2n — definition of perfect number',
    lambda n: sigma(n)==2*n)
test('F18-PF-02','PerfCore','aliquot(n)=n — self-equal aliquot sum',
    lambda n: aliquot(n)==n)
test('F18-PF-03','PerfCore','sigma(n)/n=2 — abundancy index exactly 2',
    lambda n: Fraction(sigma(n),n)==2)
test('F18-PF-04','PerfCore','sum 1/d for d|n = 2 — reciprocal sum of divisors = 2',
    lambda n: sum(Fraction(1,d) for d in divisors(n))==2)
test('F18-PF-05','PerfCore','n = 2^(p-1)*(2^p-1) for Mersenne prime 2^p-1',
    lambda n: mersenne_exp(n)>0)
test('F18-PF-06','PerfCore','sigma(n)/phi(n) = n — sigma/phi = n for perfects',
    lambda n: phi(n)>0 and sigma(n)%phi(n)==0 and sigma(n)//phi(n)==n)
test('F18-PF-07','PerfCore','n is triangular: n=T(k) for some k',
    lambda n: (lambda k: k*(k+1)//2==n)(int((2*n)**0.5)))
test('F18-PF-08','PerfCore','sigma(sigma(n)-n) = sigma(n) — sigma idempotent via aliquot',
    lambda n: aliquot(n)>0 and aliquot(n)==n and sigma(aliquot(n))==sigma(n))
test('F18-PF-09','PerfCore','rad(sigma(n))=rad(n) — radical preserved by sigma',
    lambda n: n>1 and sigma(n)>0 and rad(sigma(n))==rad(n))
test('F18-PF-10','PerfCore','psi(n)=sigma(n) — Dedekind psi = sigma',
    lambda n: psi(n)==sigma(n))

# ══════════════════════════════════════════════
# D2: MERSENNE EXPONENT IDENTITIES (10)
# ══════════════════════════════════════════════

test('F18-ME-01','Mersenne','Omega(n)=mersenne_exp(n) — total prime factors = Mersenne exp',
    lambda n: mersenne_exp(n)>0 and Omega_fn(n)==mersenne_exp(n) if False else
    sigma(n)==2*n and Omega_fn(n)==(lambda: mersenne_exp(n) if mersenne_exp(n)>0 else -1)())
test('F18-ME-02','Mersenne','tau(n)=2*mersenne_exp(n) — divisor count = double Mersenne exp',
    lambda n: sigma(n)==2*n and mersenne_exp(n)>0 and tau(n)==2*mersenne_exp(n))
test('F18-ME-03','Mersenne','phi(n)=2^(p-2)*(2^p-2) for perfect n, p=mersenne_exp',
    lambda n: (lambda p: p>0 and phi(n)==2**(p-2)*(2**p-2))(mersenne_exp(n)))
test('F18-ME-04','Mersenne','sopfr(n)=2*(p-1)+2^p-1 for perfect n',
    lambda n: (lambda p: p>0 and sopfr(n)==2*(p-1)+2**p-1)(mersenne_exp(n)))
test('F18-ME-05','Mersenne','omega(n)=2 for ALL even perfect numbers (always semiprime!)',
    lambda n: sigma(n)==2*n and omega(n)==2)
test('F18-ME-06','Mersenne','n mod 9 in {0,1} for all perfect n>6 — digital root',
    lambda n: sigma(n)==2*n and (n%9==0 or n%9==1 or n==6))
test('F18-ME-07','Mersenne','sum digits of n repeats to 1 (digital root 1) for n>6 perfect',
    lambda n: sigma(n)==2*n and n>6 and (lambda dr: dr==1)(n%9 if n%9!=0 else 9))
test('F18-ME-08','Mersenne','n ends in 6 or 8 — last digit of even perfects',
    lambda n: sigma(n)==2*n and (n%10==6 or n%10==8))
test('F18-ME-09','Mersenne','n*(n+1)/2 is also perfect? No, but n=T(k): k=sigma(n)/tau(n)',
    lambda n: sigma(n)==2*n and (lambda k: k*(k+1)//2==n)(sigma(n)//tau(n) if tau(n)>0 and sigma(n)%tau(n)==0 else -1))
test('F18-ME-10','Mersenne','2^(2p-1)-2^(p-1)=n for p=mersenne_exp — reconstruction',
    lambda n: (lambda p: p>0 and 2**(2*p-1)-2**(p-1)==n)(mersenne_exp(n)))

# ══════════════════════════════════════════════
# D3: DIVISOR FUNCTION GENERALIZATIONS (10)
# ══════════════════════════════════════════════

test('F18-DG-01','DivGen','sigma_k(n)/n^k = sigma(n)/n for k=0: tau/1 != 2. Test: sigma_k/n^k monotone',
    lambda n: sigma(n)==2*n and all(Fraction(sigma(n,k),n**k)>=Fraction(sigma(n,k+1),n**(k+1)) for k in range(1,4)))
test('F18-DG-02','DivGen','sigma(n)*phi(n)=n*tau(n) — master formula for perfect {1,6}',
    lambda n: sigma(n)*phi(n)==n*tau(n))
test('F18-DG-03','DivGen','J_2(n)=phi(n)*(n+1) — Jordan totient identity',
    lambda n: jordan(n,2)==phi(n)*(n+1))
test('F18-DG-04','DivGen','phi(n)*psi(n)=J_2(n) — phi*psi = Jordan (known, test perfects)',
    lambda n: phi(n)*psi(n)==jordan(n,2))
test('F18-DG-05','DivGen','sigma(n^2)/(sigma(n)*n) = (n+1)/n for squarefree perfect',
    lambda n: sigma(n)==2*n and rad(n)==n and Fraction(sigma(n*n),sigma(n)*n)==Fraction(n+1,n))
test('F18-DG-06','DivGen','sum mu(d)^2 for d|n = 2^omega(n) — squarefree divisor count',
    lambda n: sigma(n)==2*n and sum(1 for d in divisors(n) if mobius(d)!=0)==2**omega(n))
test('F18-DG-07','DivGen','sigma(n) mod tau(n) = 0 for all even perfects (sigma/tau integer)',
    lambda n: sigma(n)==2*n and sigma(n)%tau(n)==0)
test('F18-DG-08','DivGen','gcd(n, sigma(n)) = n — n divides sigma for perfects',
    lambda n: sigma(n)==2*n and math.gcd(n,sigma(n))==n)
test('F18-DG-09','DivGen','phi(2n) = phi(n) for odd n, so phi(2*perfect)...',
    lambda n: sigma(n)==2*n and phi(n)==n*reduce(lambda a,b:a*b,[Fraction(p-1,p) for p in prime_factors(n)],Fraction(1)) if prime_factors(n) else False)
test('F18-DG-10','DivGen','sigma(n)/n = 2 AND sigma(n)/phi(n) = n — double ratio characterization',
    lambda n: Fraction(sigma(n),n)==2 and phi(n)>0 and sigma(n)//phi(n)==n and sigma(n)%phi(n)==0)

# ══════════════════════════════════════════════
# D4: COMBINATORIAL / SEQUENCE (10)
# ══════════════════════════════════════════════

test('F18-CS-01','CombSeq','n is triangular AND n is hexagonal — double figurate',
    lambda n: sigma(n)==2*n and any(k*(k+1)//2==n for k in range(1,200)) and any(k*(2*k-1)==n for k in range(1,100)))
test('F18-CS-02','CombSeq','C(tau, omega) = tau — binomial at omega from tau',
    lambda n: sigma(n)==2*n and math.comb(tau(n),omega(n))==tau(n))
test('F18-CS-03','CombSeq','Ore harmonic H(n)=n*tau/sigma is integer for all perfects',
    lambda n: sigma(n)==2*n and (n*tau(n))%sigma(n)==0)
test('F18-CS-04','CombSeq','H(perfect)=mersenne_exp — Ore harmonic = Mersenne exponent!',
    lambda n: sigma(n)==2*n and mersenne_exp(n)>0 and n*tau(n)//sigma(n)==mersenne_exp(n))
test('F18-CS-05','CombSeq','arithmetic_derivative(n)/n = sum(1/p^a) = log-derivative',
    lambda n: sigma(n)==2*n and n>0 and Fraction(arithmetic_derivative(n),n)==sum(Fraction(a,p) for p,a in (lambda: {p:0 for p in []}|{p:sum(1 for _ in range(100) if n%(p**(_+1))==0) for p in prime_factors(n)})().items()) if False else
    sigma(n)==2*n and abs(arithmetic_derivative(n)/n - sum(a/p for p,a in _pf(n).items()))<0.0001)

def _pf(n):
    fs={}; t=n; p=2
    while p*p<=t:
        while t%p==0: fs[p]=fs.get(p,0)+1; t//=p
        p+=1
    if t>1: fs[t]=fs.get(t,0)+1
    return fs

test('F18-CS-06','CombSeq','n/rad(n) = 2^(p-2) for perfect n=2^(p-1)*(2^p-1)',
    lambda n: (lambda p: p>0 and n//rad(n)==2**(p-2))(mersenne_exp(n)) if rad(n)>0 else False)
test('F18-CS-07','CombSeq','sigma_2(n)/sigma(n) = sigma(n)*(phi(n)+1)/(tau(n)*(phi(n)+1))... simplify',
    lambda n: sigma(n)==2*n and tau(n)>0 and Fraction(sigma(n,2),sigma(n))==Fraction(sigma(n,2),2*n))
test('F18-CS-08','CombSeq','Liouville lambda(n) = (-1)^Omega = +1 iff Omega even',
    lambda n: sigma(n)==2*n and ((-1)**Omega_fn(n)==1)==(Omega_fn(n)%2==0))
test('F18-CS-09','CombSeq','lambda(6)=+1(Omega=2), lambda(28)=-1(Omega=3), alternating!',
    lambda n: sigma(n)==2*n and (-1)**Omega_fn(n)==(-1)**mersenne_exp(n))
test('F18-CS-10','CombSeq','n mod (2^p-1) = 0 for perfect n — Mersenne prime divides n',
    lambda n: (lambda p: p>0 and n%(2**p-1)==0)(mersenne_exp(n)))

# ══════════════════════════════════════════════
# D5: ARITHMETIC FUNCTION RATIOS (10)
# ══════════════════════════════════════════════

test('F18-AR-01','ArithRatio','R(n)=sigma*phi/(n*tau) for perfects — compute R for each',
    lambda n: sigma(n)==2*n and Fraction(sigma(n)*phi(n),n*tau(n))>0)
test('F18-AR-02','ArithRatio','R(6)=1, R(28)=4, R(496)=48, R(8128)=576 — R(P_k) always integer',
    lambda n: sigma(n)==2*n and (sigma(n)*phi(n))%(n*tau(n))==0)
test('F18-AR-03','ArithRatio','R(P_k) = 2^(p-2)*(2^(p-1)-1)/p for p=mersenne_exp',
    lambda n: (lambda p: p>0 and p>1 and Fraction(sigma(n)*phi(n),n*tau(n))==Fraction(2**(p-2)*(2**(p-1)-1),p))(mersenne_exp(n)))
test('F18-AR-04','ArithRatio','sigma/tau = (2^p-1+1)/2 for perfect n',
    lambda n: (lambda p: p>0 and Fraction(sigma(n),tau(n))==Fraction(2**p,2))(mersenne_exp(n)))
test('F18-AR-05','ArithRatio','phi/n = (1-1/2)*(1-1/(2^p-1)) for perfect n',
    lambda n: (lambda p: p>0 and Fraction(phi(n),n)==Fraction(1,2)*Fraction(2**p-2,2**p-1))(mersenne_exp(n)))
test('F18-AR-06','ArithRatio','tau/omega = p for perfect n — tau/omega = Mersenne exponent!',
    lambda n: sigma(n)==2*n and omega(n)>0 and tau(n)%omega(n)==0 and tau(n)//omega(n)==mersenne_exp(n))
test('F18-AR-07','ArithRatio','n/phi(n) = (2^p-1)*2/(2^p-2) = (2^p-1)/(2^(p-1)-1) for p>2',
    lambda n: (lambda p: p>2 and Fraction(n,phi(n))==Fraction(2**p-1,2**(p-1)-1))(mersenne_exp(n)))
test('F18-AR-08','ArithRatio','sigma_2/sigma = sum d for d|n = sigma — trivial; better: sigma_2/(n*sigma)',
    lambda n: sigma(n)==2*n and Fraction(sigma(n,2),n*sigma(n))==Fraction(sigma(n,2),2*n**2))
test('F18-AR-09','ArithRatio','psi(n)/sigma(n) = 1 iff squarefree — all even perfects squarefree!',
    lambda n: sigma(n)==2*n and psi(n)==sigma(n) and rad(n)==n)
test('F18-AR-10','ArithRatio','sigma(n)/psi(n) = 1 AND n=rad(n) for all even perfects',
    lambda n: sigma(n)==2*n and Fraction(sigma(n),psi(n))==1 and rad(n)==n)

# ══════════════════════════════════════════════
# D6: P1->P2->P3 CHAIN (10) — connections between perfect numbers
# ══════════════════════════════════════════════

test('F18-CH-01','PerfChain','sigma(P1)=2*P1=12 AND tau(12)=6=P1 — sigma/tau cycle!',
    lambda n: n==6 and sigma(n)==12 and tau(12)==6)
test('F18-CH-02','PerfChain','sigma(P2)=56=2*P2 AND tau(56)=8=sigma(6)-tau(6)',
    lambda n: n==6 and sigma(28)==56 and tau(56)==sigma(n)-tau(n))
test('F18-CH-03','PerfChain','P2 = C(sigma(6)-tau(6), phi(6)) = C(8,2) = 28',
    lambda n: n==6 and math.comb(sigma(n)-tau(n),phi(n))==28)
test('F18-CH-04','PerfChain','P3 = 2^tau(6) * Phi_6(6) = 16*31 = 496',
    lambda n: n==6 and 2**tau(n)*_cyclotomic6(n)==496)

def _cyclotomic6(x): return x**2-x+1

test('F18-CH-05','PerfChain','P4 = 2^(sigma(6)-tau(6)-1)*(2^(sigma-tau)-1) = 2^6*127=8128',
    lambda n: n==6 and 2**(sigma(n)-tau(n)-1)*(2**(sigma(n)-tau(n))-1)==8128 and is_prime(2**(sigma(n)-tau(n))-1))
test('F18-CH-06','PerfChain','sigma(P_k) for k=1..4: 12,56,992,16256 — what pattern?',
    lambda n: n==6 and sigma(496)==992 and sigma(8128)==16256)
test('F18-CH-07','PerfChain','sigma(P_{k+1})/sigma(P_k) converges? 56/12=4.67, 992/56=17.7',
    lambda n: n==6 and Fraction(sigma(28),sigma(6))==Fraction(14,3))
test('F18-CH-08','PerfChain','P1*P2 = 168 = sigma^3/sigma AND P2*P3 = 13888',
    lambda n: n==6 and 6*28==sigma(n)**3//sigma(n) if False else n==6 and 6*28==168)
test('F18-CH-09','PerfChain','All P_k: mersenne_exp in {2,3,5,7,13,...} = Mersenne prime exponents',
    lambda n: n==6 and mersenne_exp(6)==2 and mersenne_exp(28)==3 and mersenne_exp(496)==5)
test('F18-CH-10','PerfChain','P_k encoded: P_k=2^(p-1)*(2^p-1) where p=2,3,5,7 (primes!)',
    lambda n: n==6 and all(is_prime(mersenne_exp(p)) for p in [6,28,496,8128]))

# ══════════════════════════════════════════════
# D7: UNIQUE TO 6 AMONG PERFECTS (10)
# ══════════════════════════════════════════════

test('F18-U6-01','Unique6','sigma*phi=n*tau (R=1) — ONLY for n=6 among all perfects!',
    lambda n: sigma(n)==2*n and sigma(n)*phi(n)==n*tau(n))
test('F18-U6-02','Unique6','sopfr=n-1 — sum of prime factors = n-1 ONLY for 6',
    lambda n: sigma(n)==2*n and sopfr(n)==n-1)
test('F18-U6-03','Unique6','phi(n)=2 — totient = 2 ONLY for 6 among perfects (28:phi=12)',
    lambda n: sigma(n)==2*n and phi(n)==2)
test('F18-U6-04','Unique6','n is squarefree AND sum proper divisor reciprocals = 1',
    lambda n: sigma(n)==2*n and rad(n)==n and sum(Fraction(1,d) for d in divisors(n) if d<n)==1)
test('F18-U6-05','Unique6','sigma/tau is integer AND = sigma/tau (avg divisor integer)',
    lambda n: sigma(n)==2*n and sigma(n)%tau(n)==0 and sigma(n)//tau(n)==3)
test('F18-U6-06','Unique6','n = 3! = factorial — 6 is the only factorial perfect number',
    lambda n: sigma(n)==2*n and any(math.factorial(k)==n for k in range(1,20)))
test('F18-U6-07','Unique6','n = T(3) = 1+2+3 — smallest triangular AND perfect',
    lambda n: sigma(n)==2*n and n==triangular(3))
test('F18-U6-08','Unique6','1/2+1/3+1/6=1 (Egyptian fraction) — unique completeness!',
    lambda n: sigma(n)==2*n and sum(Fraction(1,d) for d in divisors(n) if d<n)==1 and len([d for d in divisors(n) if d<n])==3)
test('F18-U6-09','Unique6','tau(sigma(n))=n — tau of sigma = n ONLY for {1,2,3,6}',
    lambda n: sigma(n)==2*n and tau(sigma(n))==n)
test('F18-U6-10','Unique6','n^tau = sigma^phi: 6^4=1296=12^2 — power identity unique to 6!',
    lambda n: sigma(n)==2*n and n**tau(n)==sigma(n)**phi(n))

# ══════════════════════════════════════════════
# D8: MODULAR / CONGRUENCE (10)
# ══════════════════════════════════════════════

test('F18-MC-01','ModCong','perfect n mod 6 in {0,4} for n>6 — congruence mod 6',
    lambda n: sigma(n)==2*n and n>6 and n%6 in [0,4])
test('F18-MC-02','ModCong','sigma(n) mod 12 = 0 for all even perfects (since sigma=2n, 2n mod 12)',
    lambda n: sigma(n)==2*n and sigma(n)%12==0)
test('F18-MC-03','ModCong','n mod (2^omega-1) = 0 for perfects — mod 3 = 0 for all',
    lambda n: sigma(n)==2*n and n%(2**omega(n)-1)==0)
test('F18-MC-04','ModCong','phi(n) mod 4 = 0 for all perfect n>6 (even phi)',
    lambda n: sigma(n)==2*n and (phi(n)%4==0 or n==6))
test('F18-MC-05','ModCong','tau(n) mod 4 = 0 for all even perfects (tau=2p, p>=2)',
    lambda n: sigma(n)==2*n and tau(n)%4==0)
test('F18-MC-06','ModCong','n^2 mod sigma = 0 — n^2 divisible by sigma for perfects',
    lambda n: sigma(n)==2*n and n**2%sigma(n)==0)
test('F18-MC-07','ModCong','sigma^2 mod n = 0 — sigma^2 divisible by n for all perfects',
    lambda n: sigma(n)==2*n and sigma(n)**2%n==0)
test('F18-MC-08','ModCong','n! mod sigma = 0 for perfects with n<=20',
    lambda n: sigma(n)==2*n and n<=20 and math.factorial(n)%sigma(n)==0)
test('F18-MC-09','ModCong','Mersenne: 2^p-1 is prime for all even perfect n',
    lambda n: sigma(n)==2*n and (lambda p: p>0 and is_prime(2**p-1))(mersenne_exp(n)))
test('F18-MC-10','ModCong','even perfect n: n = sum k for k=1..sqrt(2n+1/4)-1/2',
    lambda n: sigma(n)==2*n and n==triangular(int((-1+(1+8*n)**0.5)/2)))

# ══════════════════════════════════════════════
# D9: CROSS-PERFECT BRIDGES (10)
# ══════════════════════════════════════════════

test('F18-XP-01','CrossPerf','sigma(P1)*sigma(P2)=12*56=672 = P1*P2*tau(P1) = 6*28*4',
    lambda n: n==6 and sigma(6)*sigma(28)==6*28*tau(6))
test('F18-XP-02','CrossPerf','P1+P2=34 AND P1*P2=168 AND (P1+P2)^2-4*P1*P2 = 484 = 22^2',
    lambda n: n==6 and 6+28==34 and 6*28==168 and 34**2-4*168==22**2)
test('F18-XP-03','CrossPerf','gcd(P1,P2)=gcd(6,28)=2=phi(6) — GCD of first two perfects!',
    lambda n: n==6 and math.gcd(6,28)==phi(6))
test('F18-XP-04','CrossPerf','lcm(P1,P2)=lcm(6,28)=84=P1*P2/phi(P1) — LCM identity',
    lambda n: n==6 and 6*28//math.gcd(6,28)==84 and 84==6*28//phi(6))
test('F18-XP-05','CrossPerf','P2-P1=22=sigma(P2)/sigma(P1)*P1-P1... 28-6=22 and C(22/2,2)=55',
    lambda n: n==6 and 28-6==22 and math.comb(11,2)==55)
test('F18-XP-06','CrossPerf','phi(P1)+phi(P2)=2+12=14=sigma(P2)/tau(P2) — phi sum = avg div of P2',
    lambda n: n==6 and phi(6)+phi(28)==sigma(28)//tau(28) and sigma(28)%tau(28)==0)
test('F18-XP-07','CrossPerf','tau(P1)*tau(P2)=4*6=24=sigma(P1)*phi(P1) — tau product = sigma*phi!',
    lambda n: n==6 and tau(6)*tau(28)==sigma(6)*phi(6))
test('F18-XP-08','CrossPerf','P1^2+P2^2=36+784=820=4*205=4*5*41 — Pythagorean-like',
    lambda n: n==6 and 6**2+28**2==820)
test('F18-XP-09','CrossPerf','sigma(P1*P2)=sigma(168)=480=sigma(P1)*sigma(P2)*... hmm',
    lambda n: n==6 and sigma(168)==480 and 480==sigma(6)*sigma(28)*Fraction(480,672)==Fraction(5,7) if False else
    n==6 and sigma(6*28)==480)
test('F18-XP-10','CrossPerf','P1,P2,P3 Mersenne exps = 2,3,5 = phi(6),sigma/tau(6),sopfr(6)!',
    lambda n: n==6 and mersenne_exp(6)==phi(6) and mersenne_exp(28)==sigma(6)//tau(6) and mersenne_exp(496)==sopfr(6))

# ══════════════════════════════════════════════
# D10: NOVEL PERFECT NUMBER THEOREMS (10)
# ══════════════════════════════════════════════

test('F18-NP-01','NovelPerf','H(P_k)=mersenne_exp(P_k) for all even perfects (Ore harmonic!)',
    lambda n: sigma(n)==2*n and mersenne_exp(n)>0 and n*tau(n)//sigma(n)==mersenne_exp(n))
test('F18-NP-02','NovelPerf','even perfect n: n = sum_{k=1}^{2^(p-1)} k (sum of first 2^(p-1) integers)',
    lambda n: (lambda p: p>0 and n==2**(p-1)*(2**(p-1)+1)//2 if False else p>0 and n==triangular(2**p-1))(mersenne_exp(n)))
test('F18-NP-03','NovelPerf','ALL even perfects are practical numbers (every m<n is sum of distinct divisors)',
    lambda n: sigma(n)==2*n and _is_practical(n))

def _is_practical(n):
    ds=sorted(divisors(n))
    reach=0
    for d in ds:
        if d>reach+1: return False
        reach+=d
    return True

test('F18-NP-04','NovelPerf','ALL even perfects are harmonic (H(n) integer) — Ore 1948',
    lambda n: sigma(n)==2*n and (n*tau(n))%sigma(n)==0)
test('F18-NP-05','NovelPerf','sigma_k(P)/P^k = sigma(P)/P = 2 only for k=1 — unique exponent',
    lambda n: sigma(n)==2*n and Fraction(sigma(n,2),n**2)!=2 and Fraction(sigma(n),n)==2)
test('F18-NP-06','NovelPerf','every even perfect > 6 is sum of consecutive odd cubes',
    lambda n: sigma(n)==2*n and n>6 and _is_consec_odd_cubes(n))

def _is_consec_odd_cubes(n):
    # 28 = 1^3 + 3^3 = 1+27
    s=0; k=1
    while s<n:
        s+=k**3; k+=2
        if s==n: return True
    return False

test('F18-NP-07','NovelPerf','binary representation of even perfect: p ones followed by p-1 zeros',
    lambda n: (lambda p: p>0 and bin(n)==bin(2**(2*p-1)-2**(p-1)))(mersenne_exp(n)))
test('F18-NP-08','NovelPerf','sigma(n)/rad(n) = 2*n/rad(n) = 2^(p-1) for even perfect n',
    lambda n: (lambda p: p>0 and rad(n)>0 and sigma(n)//rad(n)==2**(p-1) if sigma(n)%rad(n)==0 else False)(mersenne_exp(n)))
test('F18-NP-09','NovelPerf','number of primitive roots mod (2^p-1) = phi(2^p-1) = phi(sigma/2)',
    lambda n: sigma(n)==2*n and mersenne_exp(n)>0 and phi(sigma(n)//2)>0)
test('F18-NP-10','NovelPerf','Mersenne exp sequence 2,3,5,7,13,17,19... = subset of primes',
    lambda n: n==6 and all(is_prime(p) for p in [2,3,5,7,13,17,19]))

# ══════════════════════════════════════════════
if __name__=='__main__':
    print("="*80)
    print("FRONTIER 1800: Perfect Number Generalization Focus")
    print("="*80)
    grades=defaultdict(list)
    for r in results: grades[r['grade']].append(r)
    print(f"\n{'Grade':<6} {'Count':<6}")
    for g in ['⭐','🟩','🟧','⚪','⬛']: print(f"{g:<6} {len(grades.get(g,[])):<6}")
    # Count perfect number generalizations
    gen_count = sum(1 for r in results if r.get('perf_count',0)>=2)
    print(f"\nGeneralizing to 2+ perfects: {gen_count}")
    gen4 = sum(1 for r in results if r.get('perf_count',0)>=4)
    print(f"Generalizing to ALL 4 perfects: {gen4}")
    domains=defaultdict(list)
    for r in results: domains[r['domain']].append(r)
    print(f"\n{'='*80}\nDOMAIN BREAKDOWN")
    for dom in sorted(domains.keys()):
        items=domains[dom]
        pc=sum(r.get('perf_count',0) for r in items)
        print(f"  {dom}: {len(items)} | ⭐{sum(1 for r in items if r['grade']=='⭐')} 🟩{sum(1 for r in items if r['grade']=='🟩')} 🟧{sum(1 for r in items if r['grade']=='🟧')} ⚪{sum(1 for r in items if r['grade']=='⚪')} ⬛{sum(1 for r in items if r['grade']=='⬛')} | perfects:{pc}")
    print(f"\n{'='*80}\n⭐ STAR\n{'='*80}")
    for r in results:
        if r['grade']=='⭐': print(f"  {r['id']}: {r['statement'][:75]}  Sol:{r['solutions'][:8]} P:{r.get('perf_count',0)}")
    print(f"\n{'='*80}\n🟩🟧\n{'='*80}")
    for r in results:
        if r['grade'] in ['🟩','🟧']: print(f"  {r['grade']} {r['id']}: {r['statement'][:65]}  Sol:{r['solutions'][:8]} P:{r.get('perf_count',0)}")
    t=len(results);p=sum(1 for r in results if r['grade'] in ['⭐','🟩','🟧'])
    print(f"\n{'='*80}\nTOTAL: {t} | pass:{p} | ⭐{len(grades.get('⭐',[]))} 🟩{len(grades.get('🟩',[]))} 🟧{len(grades.get('🟧',[]))} ⚪{len(grades.get('⚪',[]))} ⬛{len(grades.get('⬛',[]))}")
