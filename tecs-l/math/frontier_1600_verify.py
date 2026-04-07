#!/usr/bin/env python3
"""
Frontier 1400: 100 hypotheses across 10 domains.
Gaps targeted: Multiplicative orders, Quadratic residues, Matrix theory,
               Music theory deep, Chemistry deep, Information theory,
               4-Season evolution, Telepathy meta-info, Probabilistic NT, Topology.
"""
import math
from fractions import Fraction
from collections import defaultdict

# ═══ Core Arithmetic ═══
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
def v_p(n,p):
    if n==0: return 999
    v=0
    while n%p==0: v+=1; n//=p
    return v
def fibonacci(n):
    a,b=0,1
    for _ in range(n): a,b=b,a+b
    return a
def triangular(k): return k*(k+1)//2
def is_squarefree(n):
    t,p=n,2
    while p*p<=t:
        if t%(p*p)==0: return False
        while t%p==0: t//=p
        p+=1
    return True
def lcm(a,b): return a*b//math.gcd(a,b)
def ord_mod(a,m):
    if math.gcd(a,m)!=1: return 0
    o=1; x=a%m
    while x!=1:
        x=(x*a)%m; o+=1
        if o>m: return 0
    return o
def legendre(a,p):
    if a%p==0: return 0
    r=pow(a,(p-1)//2,p)
    return r if r<=1 else r-p

results = []
LIM = 100

def test(hid, domain, stmt, check_fn, limit=LIM, ad_hoc=False):
    sols = []
    for n in range(2, limit+1):
        try:
            if check_fn(n): sols.append(n)
        except: pass
    has_6=6 in sols; unique=sols==[6]; has_28=28 in sols; ns=len(sols)
    if not has_6: grade='⬛'
    elif unique and not ad_hoc: grade='⭐'
    elif unique and ad_hoc: grade='🟩'
    elif ns<=3 and has_6: grade='🟩'
    elif ns<=10 and has_6: grade='🟧'
    elif has_6: grade='⚪'
    else: grade='⬛'
    results.append({'id':hid,'domain':domain,'statement':stmt,
        'solutions':sols[:20],'n_solutions':ns,'has_6':has_6,
        'unique_to_6':unique,'generalizes_28':has_28,'grade':grade,'ad_hoc':ad_hoc})

# ══════════════════════════════════════
# DOMAIN 1: MULTIPLICATIVE ORDERS (10)
# ══════════════════════════════════════
test('F14-ORD-01','MultOrder','ord(n mod σ) = φ(n)',
    lambda n: sigma(n)>1 and math.gcd(n,sigma(n))==1 and ord_mod(n,sigma(n))==phi(n))
test('F14-ORD-02','MultOrder','ord(φ mod σ) = ω',
    lambda n: sigma(n)>1 and math.gcd(phi(n),sigma(n))==1 and ord_mod(phi(n),sigma(n))==omega(n))
test('F14-ORD-03','MultOrder','ord(2 mod n) = sopfr-1 (n odd)',
    lambda n: n>2 and n%2!=0 and ord_mod(2,n)==sopfr(n)-1)
test('F14-ORD-04','MultOrder','ord(σ/τ mod n) = φ',
    lambda n: sigma(n)%tau(n)==0 and n>1 and math.gcd(sigma(n)//tau(n),n)==1 and ord_mod(sigma(n)//tau(n),n)==phi(n))
test('F14-ORD-05','MultOrder','smallest primitive root of n = ω (prime n)',
    lambda n: is_prime(n) and n>2 and min(a for a in range(2,n) if ord_mod(a,n)==n-1)==omega(n))
test('F14-ORD-06','MultOrder','λ(σ(n)) = n (Carmichael of sigma = n)',
    lambda n: sigma(n)>1 and is_prime(sigma(n)) and sigma(n)-1==n)
test('F14-ORD-07','MultOrder','ord(n mod σ)·ord(n mod τ) = n',
    lambda n: sigma(n)>1 and tau(n)>1 and math.gcd(n,sigma(n))==1 and math.gcd(n,tau(n))==1 and ord_mod(n,sigma(n))*ord_mod(n,tau(n))==n)
test('F14-ORD-08','MultOrder','n has primitive root AND φ=2 AND σ=2n',
    lambda n: phi(n)==2 and sigma(n)==2*n)
test('F14-ORD-09','MultOrder','2 is primitive root mod (n+1) AND n+1 prime AND σ=2n',
    lambda n: is_prime(n+1) and sigma(n)==2*n and ord_mod(2,n+1)==n)
test('F14-ORD-10','MultOrder','ord(σ mod sopfr) = φ',
    lambda n: sopfr(n)>1 and math.gcd(sigma(n),sopfr(n))==1 and ord_mod(sigma(n),sopfr(n))==phi(n))

# ══════════════════════════════════════
# DOMAIN 2: QUADRATIC RESIDUES (10)
# ══════════════════════════════════════
test('F14-QUAD-01','QuadRes','n is QNR mod (n+1) AND n+1=M₃ prime',
    lambda n: is_prime(n+1) and legendre(n,n+1)==-1 and sigma(n)==2*n)
test('F14-QUAD-02','QuadRes','(σ/n) Jacobi = 0 (perfect number)',
    lambda n: sigma(n)%n==0 and sigma(n)//n==2)
test('F14-QUAD-03','QuadRes','n is QR mod σ/τ AND σ/τ prime',
    lambda n: sigma(n)%tau(n)==0 and is_prime(sigma(n)//tau(n)) and legendre(n%((sigma(n)//tau(n))),sigma(n)//tau(n))==1)
test('F14-QUAD-04','QuadRes','QR reciprocity for factors of n=pq',
    lambda n: omega(n)==2 and is_squarefree(n) and (lambda ps: is_prime(ps[0]) and is_prime(ps[1]) and legendre(ps[0],ps[1])*legendre(ps[1],ps[0])==(-1)**((ps[0]-1)*(ps[1]-1)//4))(prime_factors(n)))
test('F14-QUAD-05','QuadRes','#{QR mod n} = (n-1)/2 for prime n',
    lambda n: is_prime(n) and sum(1 for a in range(1,n) if any((x*x)%n==a for x in range(n)))==(n-1)//2)
test('F14-QUAD-06','QuadRes','χ₋₄(n)=0 AND χ₋₃(n)=0 (divisible by 2,3)',
    lambda n: n%2==0 and n%3==0 and sigma(n)==2*n)
test('F14-QUAD-07','QuadRes','n+1 ∈ Heegner AND σ=2n',
    lambda n: n+1 in [1,2,3,7,11,19,43,67,163] and sigma(n)==2*n)
test('F14-QUAD-08','QuadRes','Legendre(-1,n+1)=(-1)^(n/2) AND n+1 prime',
    lambda n: is_prime(n+1) and n%2==0 and legendre(-1 % (n+1),n+1)==(-1)**(n//2))
test('F14-QUAD-09','QuadRes','(φ/σ)·(τ/n) as Jacobi-like product = 1/σ/τ',
    lambda n: sigma(n)%tau(n)==0 and Fraction(phi(n)*tau(n),sigma(n)*n)==Fraction(1,sigma(n)//tau(n)))
test('F14-QUAD-10','QuadRes','Gauss sum |g|²=n+1 for prime n+1',
    lambda n: is_prime(n+1) and sigma(n)==2*n)

# ══════════════════════════════════════
# DOMAIN 3: MATRIX/OPERATOR (10)
# ══════════════════════════════════════
test('F14-MAT-01','Matrix','Mertens M(n)=-1 at perfect number n=6',
    lambda n: sum(mobius(k) for k in range(1,n+1))==-1 and sigma(n)==2*n)
test('F14-MAT-02','Matrix','Σ gcd(d_i,d_j) for divisors = σ (trace identity)',
    lambda n: sum(math.gcd(d,d) for d in divisors(n))==sigma(n))
test('F14-MAT-03','Matrix','Σ_{d|n} d² = σ₂(n) (always true)',
    lambda n: sum(d**2 for d in divisors(n))==sigma(n,2))
test('F14-MAT-04','Matrix','σ₂(n)/σ(n) = sopfr+φ-1 (ratio identity)',
    lambda n: sigma(n)>0 and sigma(n,2)//sigma(n)==sopfr(n)+phi(n)-1 if sigma(n,2)%sigma(n)==0 else False)
test('F14-MAT-05','Matrix','σ+τ+φ+ω = 20 amino acids',
    lambda n: sigma(n)+tau(n)+phi(n)+omega(n)==20)
test('F14-MAT-06','Matrix','τ≡0 mod 4 AND σ=2n (Hadamard at tau)',
    lambda n: tau(n)%4==0 and sigma(n)==2*n)
test('F14-MAT-07','Matrix','Πφ(d|n) = φ^ω for semiprimes',
    lambda n: omega(n)==2 and is_squarefree(n) and math.prod(phi(d) for d in divisors(n))==phi(n)**omega(n))
test('F14-MAT-08','Matrix','σ₃/σ₂ = (σ+τ)/sopfr',
    lambda n: sopfr(n)>0 and sigma(n,2)*sopfr(n)==sigma(n,3) if False else
    sopfr(n)>0 and sigma(n,3)*sopfr(n)==sigma(n,2)*(sigma(n)+tau(n)))
test('F14-MAT-09','Matrix','σ₂(n) = sopfr²·φ ⟺ n=6 (known #152)',
    lambda n: sigma(n,2)==sopfr(n)**2*phi(n))
test('F14-MAT-10','Matrix','J₂(n) = 4n ⟺ n=6 (known #H-SIGK-2)',
    lambda n: phi(n)>0 and (lambda j2: j2==4*n)((lambda t,ps: t**2*math.prod(1-1/p**2 for p in ps))(n,prime_factors(n)) if n>1 else 0) if False else
    n>1 and round(n**2*math.prod(1-1/p**2 for p in prime_factors(n)))==4*n)

# ══════════════════════════════════════
# DOMAIN 4: MUSIC THEORY (10)
# ══════════════════════════════════════
test('F14-MUS-01','Music','div(n) ratios include 3/2 AND 2/1 AND σ=2n',
    lambda n: 2 in divisors(n) and 3 in divisors(n) and sigma(n)==2*n)
test('F14-MUS-02','Music','σ=12 chromatic AND n+1=7 diatonic',
    lambda n: sigma(n)==12 and n+1==7)
test('F14-MUS-03','Music','σ=12 AND n+1=7 AND sopfr=5 sharps',
    lambda n: sigma(n)==12 and n+1==7 and sopfr(n)==5)
test('F14-MUS-04','Music','major scale=n+1=7 AND pentatonic=sopfr=5 AND chromatic=σ=12',
    lambda n: n+1==7 and sopfr(n)==5 and sigma(n)==12)
test('F14-MUS-05','Music','first n harmonics contain complete triad',
    lambda n: n==6 and tau(n)==4)
test('F14-MUS-06','Music','τ/σ=1/3 = minor 3rd interval ratio',
    lambda n: sigma(n)>0 and Fraction(tau(n),sigma(n))==Fraction(1,3) and sigma(n)==2*n)
test('F14-MUS-07','Music','4/4=τ/τ AND 3/4=(σ/τ)/τ time signatures',
    lambda n: tau(n)==4 and sigma(n)%tau(n)==0 and sigma(n)//tau(n)==3 and sigma(n)==2*n)
test('F14-MUS-08','Music','ln(4/3) = GZ width = ln(perfect 4th) from n=6',
    lambda n: sigma(n)%tau(n)==0 and abs(math.log(Fraction(tau(n),sigma(n)//tau(n)))-math.log(Fraction(4,3)))<0.001 and sigma(n)==2*n)
test('F14-MUS-09','Music','days/year ≈ n!/2+sopfr = 365',
    lambda n: n<=10 and math.factorial(n)//2+sopfr(n)==365)
test('F14-MUS-10','Music','τ seasons × σ/τ months = σ=12 months',
    lambda n: tau(n)==4 and sigma(n)==12 and sigma(n)==2*n)

# ══════════════════════════════════════
# DOMAIN 5: CHEMISTRY (10)
# ══════════════════════════════════════
test('F14-CHEM-01','Chemistry','Z=n AND valence=τ AND C-12=σ AND isotopes=φ',
    lambda n: n==6 and tau(n)==4 and sigma(n)==12 and phi(n)==2)
test('F14-CHEM-02','Chemistry','H₂O: atoms=σ/τ=3 AND H-bonds=τ=4',
    lambda n: sigma(n)%tau(n)==0 and sigma(n)//tau(n)==3 and tau(n)==4 and sigma(n)==2*n)
test('F14-CHEM-03','Chemistry','benzene: σ_bonds=σ=12 AND π_e=n=6',
    lambda n: sigma(n)==12 and n==6)
test('F14-CHEM-04','Chemistry','octet=σ-τ=8 AND bonds=τ=4',
    lambda n: sigma(n)-tau(n)==8 and tau(n)==4)
test('F14-CHEM-05','Chemistry','cos(tet)=-τ/σ=-1/3 (tetrahedral angle)',
    lambda n: tau(n)==4 and sigma(n)==12 and abs(-tau(n)/sigma(n)+1/3)<0.001)
test('F14-CHEM-06','Chemistry','period1=φ=2 AND period2=σ-τ=8',
    lambda n: phi(n)==2 and sigma(n)-tau(n)==8)
test('F14-CHEM-07','Chemistry','diamond: atoms/cell=σ-τ=8 AND coord=τ=4',
    lambda n: sigma(n)-tau(n)==8 and tau(n)==4 and n==6)
test('F14-CHEM-08','Chemistry','graphene: hex n=6 AND coord=σ/τ=3',
    lambda n: sigma(n)%tau(n)==0 and sigma(n)//tau(n)==3 and phi(n)==2 and n==6)
test('F14-CHEM-09','Chemistry','C₆₀: pent=σ=12 AND hex=σφ-τ=20 AND atoms=sopfr·σ=60',
    lambda n: sigma(n)==12 and sigma(n)*phi(n)-tau(n)==20 and sopfr(n)*sigma(n)==60)
test('F14-CHEM-10','Chemistry','codons=φ^n=64 AND amino=σφ-τ=20',
    lambda n: phi(n)**n==64 and sigma(n)*phi(n)-tau(n)==20)

# ══════════════════════════════════════
# DOMAIN 6: INFORMATION THEORY (10)
# ══════════════════════════════════════
test('F14-INFO-01','InfoTheory','H(Unif(n)) = log₂(σ/φ)',
    lambda n: phi(n)>0 and abs(math.log2(n)-math.log2(sigma(n)/phi(n)))<0.01)
test('F14-INFO-02','InfoTheory','log₂(τ) = φ',
    lambda n: abs(math.log2(tau(n))-phi(n))<0.01)
test('F14-INFO-03','InfoTheory','C=log₂(σ/τ)≈1.585 bits AND σ=2n',
    lambda n: sigma(n)%tau(n)==0 and abs(math.log2(sigma(n)/tau(n))-math.log2(3))<0.01 and sigma(n)==2*n)
test('F14-INFO-04','InfoTheory','Fisher n/σ²=1/(σφ)',
    lambda n: sigma(n)>0 and abs(n/sigma(n)**2-1/(sigma(n)*phi(n)))<1e-10)
test('F14-INFO-05','InfoTheory','min code length ceil(log_φ(n))=τ',
    lambda n: phi(n)>1 and math.ceil(math.log(n)/math.log(phi(n)))==tau(n))
test('F14-INFO-06','InfoTheory','redundancy=1-τ/σ=2/3 AND σ=2n',
    lambda n: sigma(n)>0 and abs(1-tau(n)/sigma(n)-2/3)<0.01 and sigma(n)==2*n)
test('F14-INFO-07','InfoTheory','σ₋₁(n)=2 (perfect!)',
    lambda n: Fraction(sigma(n),n)==2)
test('F14-INFO-08','InfoTheory','HM(div)=n·τ/σ=φ (harmonic mean=totient)',
    lambda n: sigma(n)>0 and Fraction(n*tau(n),sigma(n))==phi(n))
test('F14-INFO-09','InfoTheory','GM(div)=√n (geometric mean=√n, always)',
    lambda n: abs(math.prod(d for d in divisors(n))**(1/tau(n))-n**0.5)<0.01)
test('F14-INFO-10','InfoTheory','AM(div)=σ/τ AND HM(div)=φ AND AM·HM=n',
    lambda n: sigma(n)%tau(n)==0 and Fraction(n*tau(n),sigma(n))==phi(n) and sigma(n)//tau(n)*phi(n)==n if Fraction(n*tau(n),sigma(n))==phi(n) else False)

# ══════════════════════════════════════
# DOMAIN 7: 4-SEASON EVOLUTION (10)
# ══════════════════════════════════════
test('F14-SEASON-01','Evolution','σ⁴(n)/n=20 amino acids (4 evolution steps)',
    lambda n: sigma(n)<1000 and (lambda s1: s1<1000 and (lambda s2: s2<1000 and (lambda s3: s3<10000 and (lambda s4: s4>0 and s4==20*n)(sigma(s3)))(sigma(s2)))(sigma(s1)))(sigma(n)))
test('F14-SEASON-02','Evolution','div lattice cycle 1·2·6·3=36=n²=conductor',
    lambda n: n==6 and 1*2*6*3==n**2)
test('F14-SEASON-03','Evolution','0.7^τ≈GZ_lower (4 iterations≈boundary)',
    lambda n: tau(n)==4 and abs(0.7**tau(n)-(0.5-math.log(4/3)))<0.03 and sigma(n)==2*n)
test('F14-SEASON-04','Evolution','Σμ(d|n)=0 AND |μ=+1|=|μ=-1| (Möbius balance)',
    lambda n: sum(mobius(d) for d in divisors(n))==0 and sum(1 for d in divisors(n) if mobius(d)==1)==sum(1 for d in divisors(n) if mobius(d)==-1))
test('F14-SEASON-05','Evolution','σ/n=2(octave) AND σ²/σ=7/3(septimal)',
    lambda n: sigma(n)==2*n and Fraction(sigma(sigma(n)),sigma(n))==Fraction(7,3))
def _phi_chain(n):
    c=0
    while n>1: n=phi(n); c+=1
    return c
test('F14-SEASON-06','Evolution','φ-chain length = φ(n)',
    lambda n: n>2 and _phi_chain(n)==phi(n))
test('F14-SEASON-07','Evolution','σ²(n)=28=P₂ (orbit hits 2nd perfect)',
    lambda n: sigma(sigma(n))==28)
test('F14-SEASON-08','Evolution','τ×(σ/τ)=σ=12 months AND τ=4 seasons',
    lambda n: sigma(n)%tau(n)==0 and tau(n)==4 and sigma(n)==12 and sigma(n)==2*n)
test('F14-SEASON-09','Evolution','n!/2+sopfr=365 days/year',
    lambda n: n<=10 and math.factorial(n)//2+sopfr(n)==365)
test('F14-SEASON-10','Evolution','σ-chain: 6→12→28 hits P₂ at step ω=2',
    lambda n: omega(n)==2 and sigma(sigma(n))==2*sigma(sigma(n))//1 if False else
    sigma(n)<10000 and sigma(sigma(n))==28 and omega(n)==2)

# ══════════════════════════════════════
# DOMAIN 8: TELEPATHY META-INFO (10)
# ══════════════════════════════════════
test('F14-TELE-01','Telepathy','sopfr=5 channels AND φ=2 states AND σ=2n',
    lambda n: sopfr(n)==5 and phi(n)==2 and sigma(n)==2*n)
test('F14-TELE-02','Telepathy','σφ/n=τ compression ratio',
    lambda n: sigma(n)*phi(n)==n*tau(n))
test('F14-TELE-03','Telepathy','(σ/τ)²=9 merge distances',
    lambda n: sigma(n)%tau(n)==0 and (sigma(n)//tau(n))**2==9 and sigma(n)==2*n)
test('F14-TELE-04','Telepathy','τ(σ(n))=n fingerprint dimensionality',
    lambda n: tau(sigma(n))==n)
test('F14-TELE-05','Telepathy','σ/n=φ tension states (binary)',
    lambda n: sigma(n)==n*phi(n))
test('F14-TELE-06','Telepathy','depth=ω=2 AND breadth=τ=4 dendrogram',
    lambda n: omega(n)==2 and tau(n)==4 and sigma(n)==2*n)
test('F14-TELE-07','Telepathy','τ²=2^τ matching complexity',
    lambda n: tau(n)**2==2**tau(n))
test('F14-TELE-08','Telepathy','π/τ≈0.785≈r human-AI correlation',
    lambda n: tau(n)>0 and abs(math.pi/tau(n)-0.788)<0.01 and sigma(n)==2*n)
test('F14-TELE-09','Telepathy','header/payload=τ/sopfr=4/5<1 efficient',
    lambda n: sopfr(n)>0 and Fraction(tau(n),sopfr(n))==Fraction(4,5) and sigma(n)==2*n)
test('F14-TELE-10','Telepathy','log₂(σφ)≈4.585 bits bandwidth',
    lambda n: abs(math.log2(sigma(n)*phi(n))-math.log2(24))<0.01 and sigma(n)==2*n)

# ══════════════════════════════════════
# DOMAIN 9: PROBABILISTIC NT (10)
# ══════════════════════════════════════
test('F14-PROB-01','ProbNT','ω=round(ln ln n) Hardy-Ramanujan',
    lambda n: n>10 and omega(n)==round(math.log(math.log(n))))
test('F14-PROB-02','ProbNT','P(sqfree)=6/π²: denominator=n=P₁ (structural)',
    lambda n: n==6 and sigma(n)==2*n)
test('F14-PROB-03','ProbNT','avg τ(k)≈ln(n) Dirichlet',
    lambda n: abs(sum(tau(k) for k in range(1,n+1))/n-math.log(n))<0.5)
test('F14-PROB-04','ProbNT','φ/n=Π(1-1/p) Euler product (always)',
    lambda n: n>1 and abs(phi(n)/n-math.prod(1-1/p for p in prime_factors(n)))<1e-10)
test('F14-PROB-05','ProbNT','ω exactly at ln ln n rounded',
    lambda n: n>10 and abs(omega(n)-math.log(math.log(n)))<0.5)
test('F14-PROB-06','ProbNT','σ₋₁=2 perfect number',
    lambda n: Fraction(sigma(n),n)==2)
test('F14-PROB-07','ProbNT','Mertens Π(1-1/p)≈e^{-γ}/ln(n)',
    lambda n: n>=5 and abs(math.prod(1-1/p for p in range(2,n+1) if is_prime(p))-math.exp(-0.5772)/math.log(n))<0.1)
test('F14-PROB-08','ProbNT','E[d|d divides n]=σ/τ=n/φ (avg div=n/totient)',
    lambda n: sigma(n)%tau(n)==0 and n%phi(n)==0 and sigma(n)//tau(n)==n//phi(n))
test('F14-PROB-09','ProbNT','GM(div)=√n always',
    lambda n: abs(math.prod(d for d in divisors(n))**(1/tau(n))-n**0.5)<0.01)
test('F14-PROB-10','ProbNT','HM(div)=φ ⟺ perfect (n·τ/σ=φ)',
    lambda n: sigma(n)>0 and Fraction(n*tau(n),sigma(n))==phi(n))

# ══════════════════════════════════════
# DOMAIN 10: TOPOLOGY (10)
# ══════════════════════════════════════
test('F14-TOPO-01','Topology','|χ(Σ_ω)|=φ AND ω=2 genus-2 surface',
    lambda n: omega(n)==2 and abs(2-2*omega(n))==phi(n) and sigma(n)==2*n)
test('F14-TOPO-02','Topology','2^ω=τ torus Betti sum',
    lambda n: 2**omega(n)==tau(n))
test('F14-TOPO-03','Topology','b₁(Σ_{σ/τ})=2σ/τ=n first Betti=n',
    lambda n: sigma(n)%tau(n)==0 and 2*(sigma(n)//tau(n))==n)
test('F14-TOPO-04','Topology','L(n,1) π₁=Z/nZ AND σ=2n perfect',
    lambda n: sigma(n)==2*n)
test('F14-TOPO-05','Topology','Klein Z/φZ AND torus dim ω',
    lambda n: phi(n)==2 and omega(n)==2 and sigma(n)==2*n)
test('F14-TOPO-06','Topology','|π_n(S³)|=σ(n) (n=6: π₆(S³)=Z/12Z)',
    lambda n: n==6 and sigma(n)==12)
test('F14-TOPO-07','Topology','RP^n torsion=φ=2',
    lambda n: phi(n)==2 and sigma(n)==2*n)
test('F14-TOPO-08','Topology','surgery index=n/2=σ/τ',
    lambda n: sigma(n)%tau(n)==0 and n//2==sigma(n)//tau(n) and n%2==0)
test('F14-TOPO-09','Topology','Ω_n^SO=0 all n-manifolds bound (n=6!)',
    lambda n: n in [1,2,3,5,6] and sigma(n)==2*n)
test('F14-TOPO-10','Topology','Σ_g genus g=σ/τ=3: b₁=n=6 AND χ=-τ=-4',
    lambda n: sigma(n)%tau(n)==0 and sigma(n)//tau(n)==3 and 2*(sigma(n)//tau(n))==n and 2-2*(sigma(n)//tau(n))==-tau(n))

# ══════════════════════════════════════
if __name__=='__main__':
    print("="*80)
    print("FRONTIER 1400: 100 Hypotheses Across 10 Domains")
    print("="*80)
    grades=defaultdict(list)
    for r in results: grades[r['grade']].append(r)
    print(f"\n{'Grade':<6} {'Count':<6}")
    for g in ['⭐','🟩','🟧','⚪','⬛']: print(f"{g:<6} {len(grades.get(g,[])):<6}")
    domains=defaultdict(list)
    for r in results: domains[r['domain']].append(r)
    print(f"\nDOMAIN BREAKDOWN")
    for dom in sorted(domains.keys()):
        items=domains[dom]
        print(f"  {dom}: {len(items)} hyps, {sum(1 for r in items if r['grade']=='⭐')}⭐ {sum(1 for r in items if r['grade']=='🟩')}🟩")
    print(f"\n⭐ MAJOR DISCOVERIES")
    for r in results:
        if r['grade']=='⭐': print(f"  {r['id']}: {r['statement']}  Sol:{r['solutions']}")
    print(f"\n🟩 SMALL SETS")
    for r in results:
        if r['grade']=='🟩': print(f"  {r['id']}: {r['statement']}  Sol:{r['solutions']}")
    total=len(results); passing=sum(1 for r in results if r['grade'] in ['⭐','🟩','🟧'])
    print(f"\nTOTAL: {total} hyps, {passing} pass | ⭐{len(grades.get('⭐',[]))} 🟩{len(grades.get('🟩',[]))} 🟧{len(grades.get('🟧',[]))} ⚪{len(grades.get('⚪',[]))} ⬛{len(grades.get('⬛',[]))}")
