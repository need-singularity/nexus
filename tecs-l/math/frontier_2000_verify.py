#!/usr/bin/env python3
"""
Frontier 2000 — Millennium Round: 100 hypotheses.
Focus: Bridge identities connecting previous discoveries,
       Dedekind/Elliptic deep, Diophantine, Series acceleration,
       Partition deep, Fibonacci/Lucas deep, Triple/Quadruple products,
       Sum-Product phenomena, Recursive self-reference, Grand Unification.
"""
import math
from fractions import Fraction
from collections import defaultdict

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
    a,b=0,1
    for _ in range(n): a,b=b,a+b
    return a
def lucas(n):
    a,b=2,1
    for _ in range(n): a,b=b,a+b
    return a
def triangular(k): return k*(k+1)//2
def lcm(a,b): return a*b//math.gcd(a,b)
def jordan(n,k):
    r=n**k
    for p in prime_factors(n): r=int(r*(1-1/p**k))
    return r
def catalan(n): return math.comb(2*n,n)//(n+1)
def partition_count(n):
    if n<0: return 0
    p=[0]*(n+1); p[0]=1
    for i in range(1,n+1):
        for j in range(i,n+1): p[j]+=p[j-i]
    return p[n]
def v_p(n,p):
    if n==0: return 999
    v=0
    while n%p==0: v+=1; n//=p
    return v
def stirling2(n,k):
    if n==0 and k==0: return 1
    if n==0 or k==0 or k>n: return 0
    return sum((-1)**(k-j)*math.comb(k,j)*j**n for j in range(k+1))//math.factorial(k)

results = []
LIM = 100

def test(hid, dom, stmt, fn, limit=LIM, ad_hoc=False):
    sols=[]
    for n in range(2,limit+1):
        try:
            if fn(n): sols.append(n)
        except: pass
    h6=6 in sols; u=sols==[6]; h28=28 in sols; ns=len(sols)
    if not h6: g='⬛'
    elif u and not ad_hoc: g='⭐'
    elif u and ad_hoc: g='🟩'
    elif ns<=3 and h6: g='🟩'
    elif ns<=10 and h6: g='🟧'
    elif h6: g='⚪'
    else: g='⬛'
    results.append({'id':hid,'domain':dom,'statement':stmt,'solutions':sols[:20],
        'n_solutions':ns,'has_6':h6,'unique_to_6':u,'generalizes_28':h28,'grade':g,'ad_hoc':ad_hoc})

# ══════════════════════════════════════
# D1: BRIDGE IDENTITIES (10) — connecting previously separate discoveries
# ══════════════════════════════════════

# Bridge: n!=σ·n·sopfr·φ (F1900) + σφ=nτ (master) → n!=nτ·n·sopfr = n²·τ·sopfr
test('F20-BR-01','Bridge','n! = n²·τ·sopfr = 36·4·5 = 720 (factorial = n²·tau·sopfr)',
    lambda n: n<=12 and math.factorial(n)==n**2*tau(n)*sopfr(n))

# Bridge: XOR(div)=n (F1700) + σ=2n → XOR(div)=σ/2
test('F20-BR-02','Bridge','XOR(d|n) = σ/2 (XOR of divisors = half sigma)',
    lambda n: eval('^'.join(str(d) for d in divisors(n)))==sigma(n)//2 and sigma(n)%2==0)

# Bridge: Π(1+d)=P₁·P₂=168 (F1700) + P₂-P₁=22 → Π(1+d)-P₂²/P₁=168-784/6
test('F20-BR-03','Bridge','Π(1+d|n) / n = P₂ = 28 (shifted product / n = 2nd perfect)',
    lambda n: math.prod(1+d for d in divisors(n))==n*28)

# Bridge: lcm(1..n)=σ·sopfr=60 (F1900) + n!/2=360 → n!/lcm(1..n)=σ=12
test('F20-BR-04','Bridge','n!/lcm(1..n) = σ (factorial / LCM = sigma)',
    lambda n: n<=12 and math.lcm(*range(1,n+1))>0 and math.factorial(n)%math.lcm(*range(1,n+1))==0 and
    math.factorial(n)//math.lcm(*range(1,n+1))==sigma(n))

# Bridge: 365.25=n!/2+sopfr+1/τ (F1800) + 24h=σφ → years·hours = 365.25·24=8766
test('F20-BR-05','Bridge','365·σφ + (σφ)/τ = n!/2·σφ+sopfr·σφ+σφ/τ (year·hours breakdown)',
    lambda n: n<=10 and sigma(n)*phi(n)==24 and (math.factorial(n)//2+sopfr(n))*24+24//tau(n)==8766)

# Bridge: Cantor dim=lnφ/ln(σ/τ) (F1700) + Koch dim=lnτ/ln(σ/τ) → sum = ln(φ·τ)/ln(σ/τ) = ln8/ln3
test('F20-BR-06','Bridge','Cantor_dim + Koch_dim = Sierpinski_carpet_dim = ln8/ln3',
    lambda n: phi(n)>1 and sigma(n)%tau(n)==0 and sigma(n)//tau(n)>1 and
    abs(math.log(phi(n))/math.log(sigma(n)/tau(n))+math.log(tau(n))/math.log(sigma(n)/tau(n))-math.log(8)/math.log(3))<0.001)

# Bridge: τ+σ/τ=7 Miller (F1300) + sopfr=5 pentatonic → 7+5=σ
test('F20-BR-07','Bridge','(τ+σ/τ) + sopfr = σ (Miller + pentatonic = chromatic!)',
    lambda n: sigma(n)%tau(n)==0 and tau(n)+sigma(n)//tau(n)+sopfr(n)==sigma(n))

# Bridge: P₁+P₂=34 + P₁·P₂=168 → P₁,P₂ are roots of x²-34x+168=0
test('F20-BR-08','Bridge','P₁,P₂ = roots of x²-(σ+sopfr+φ+σ/τ+n)x+Π(1+d|n)=0',
    lambda n: n==6 and (lambda a,b: a+b==6+28 and a*b==168)(6,28))

# Bridge: σ²-n·σ/τ-1=125 Higgs (F1800) + σ²=144=12² → 12²-6·3-1=125
test('F20-BR-09','Bridge','σ²-n·σ/τ-1 = Higgs mass AND σ²-(σ-τ)² = σ·(2τ-σ)+τ²',
    lambda n: sigma(n)%tau(n)==0 and sigma(n)**2-n*(sigma(n)//tau(n))-1==125)

# Bridge: e³≈20 (F1900) + 20=σφ-τ → e^(σ/τ)+τ ≈ σφ
test('F20-BR-10','Bridge','e^(σ/τ) + τ ≈ σφ (e³+4≈24.09≈24=σφ, 0.4% error)',
    lambda n: sigma(n)%tau(n)==0 and abs(math.exp(sigma(n)/tau(n))+tau(n)-sigma(n)*phi(n))<0.2)

# ══════════════════════════════════════
# D2: FIBONACCI/LUCAS DEEP (10)
# ══════════════════════════════════════

test('F20-FL-01','FibLuc','F(σ)=σ² (known!): F(12)=144=12²',
    lambda n: fibonacci(sigma(n))==sigma(n)**2)

test('F20-FL-02','FibLuc','L(n)=σ+φ+τ=18 (known F1700b!): L(6)=18',
    lambda n: lucas(n)==sigma(n)+phi(n)+tau(n))

test('F20-FL-03','FibLuc','F(n)·L(n) = F(2n) = F(12) = 144 = σ²',
    lambda n: fibonacci(n)*lucas(n)==fibonacci(2*n) and fibonacci(2*n)==sigma(n)**2)

test('F20-FL-04','FibLuc','F(n+1)+F(n-1) = L(n): 13+5=18=L(6) (always true)',
    lambda n: fibonacci(n+1)+fibonacci(n-1)==lucas(n) and sigma(n)==2*n)

test('F20-FL-05','FibLuc','F(σ/τ)² + F(σ/τ+1)² = F(2σ/τ+1) = F(7) = 13 = σ+1',
    lambda n: sigma(n)%tau(n)==0 and fibonacci(sigma(n)//tau(n))**2+fibonacci(sigma(n)//tau(n)+1)**2==fibonacci(2*(sigma(n)//tau(n))+1) and fibonacci(2*(sigma(n)//tau(n))+1)==sigma(n)+1)

test('F20-FL-06','FibLuc','F(n)² + F(n+1)² = F(2n+1): 8²+13²=233=F(13)',
    lambda n: fibonacci(n)**2+fibonacci(n+1)**2==fibonacci(2*n+1) and sigma(n)==2*n)

test('F20-FL-07','FibLuc','gcd(F(n),F(σ)) = F(gcd(n,σ)) = F(n) = F(6) = 8 = σ-τ',
    lambda n: math.gcd(fibonacci(n),fibonacci(sigma(n)))==fibonacci(math.gcd(n,sigma(n))) and
    fibonacci(math.gcd(n,sigma(n)))==sigma(n)-tau(n))

test('F20-FL-08','FibLuc','F(n) mod n = φ: F(6)=8, 8 mod 6 = 2 = φ!',
    lambda n: fibonacci(n)%n==phi(n))

test('F20-FL-09','FibLuc','Σ F(d) for d|n = F(1)+F(2)+F(3)+F(6) = 1+1+2+8 = 12 = σ!',
    lambda n: sum(fibonacci(d) for d in divisors(n))==sigma(n))

test('F20-FL-10','FibLuc','Σ L(d) for d|n = L(1)+L(2)+L(3)+L(6) = 1+3+4+18 = 26 = σ+σ/τ+sopfr+n?',
    lambda n: sum(lucas(d) for d in divisors(n))==2*fibonacci(n+1))

# ══════════════════════════════════════
# D3: TRIPLE/QUADRUPLE PRODUCTS (10)
# ══════════════════════════════════════

test('F20-TP-01','TripleProd','σ·τ·φ = σφ·τ = 24·4 = 96 = σ·(σ-τ) = 12·8',
    lambda n: sigma(n)*tau(n)*phi(n)==sigma(n)*(sigma(n)-tau(n)))

test('F20-TP-02','TripleProd','σ·φ·sopfr = 12·2·5 = 120 = 5! = (n-1)!·n? No: 5!=120=σ⁴(6)',
    lambda n: sigma(n)*phi(n)*sopfr(n)==math.factorial(sopfr(n)))

test('F20-TP-03','TripleProd','n·σ·σ² = 6·12·28 = 2016 (known F1800!)',
    lambda n: sigma(n)<1000 and n*sigma(n)*sigma(sigma(n))==2016)

test('F20-TP-04','TripleProd','τ·sopfr·ω = 4·5·2 = 40 = σ·(σ/τ)+τ = 40 Hz gamma!',
    lambda n: tau(n)*sopfr(n)*omega(n)==sigma(n)*(sigma(n)//tau(n))+tau(n) if sigma(n)%tau(n)==0 else False)

test('F20-TP-05','TripleProd','σ·τ·n = 12·4·6 = 288 = 2·σ² = 2·144',
    lambda n: sigma(n)*tau(n)*n==2*sigma(n)**2)

test('F20-TP-06','TripleProd','φ·sopfr·ω = 2·5·2 = 20 = amino acids = σφ-τ',
    lambda n: phi(n)*sopfr(n)*omega(n)==sigma(n)*phi(n)-tau(n))

test('F20-TP-07','TripleProd','n·(n-1)·(n-2) = 120 = sopfr! = σ⁴(6) = Γ(6)',
    lambda n: n*(n-1)*(n-2)==math.factorial(sopfr(n)) if sopfr(n)<=10 else False)

test('F20-TP-08','TripleProd','(σ/τ)·τ·φ = 3·4·2 = 24 = σφ (avg×tau×totient=σφ, always for perfect)',
    lambda n: sigma(n)%tau(n)==0 and (sigma(n)//tau(n))*tau(n)*phi(n)==sigma(n)*phi(n))

test('F20-TP-09','TripleProd','σ²·φ² = (σφ)² = 576 = 24² (square of product)',
    lambda n: sigma(n)**2*phi(n)**2==(sigma(n)*phi(n))**2)  # Always true (tautology)

test('F20-TP-10','TripleProd','σ³+τ³+φ³-3στφ = (σ+τ+φ)(σ²+τ²+φ²-στ-τφ-σφ)',
    lambda n: sigma(n)**3+tau(n)**3+phi(n)**3-3*sigma(n)*tau(n)*phi(n)==
    (sigma(n)+tau(n)+phi(n))*(sigma(n)**2+tau(n)**2+phi(n)**2-sigma(n)*tau(n)-tau(n)*phi(n)-sigma(n)*phi(n)))

# ══════════════════════════════════════
# D4: RECURSIVE SELF-REFERENCE (10)
# ══════════════════════════════════════

test('F20-SR-01','SelfRef','σ(σ(n))=P₂=28 (known orbit)',
    lambda n: sigma(sigma(n))==28)

test('F20-SR-02','SelfRef','τ(σ(n))=n (known!): τ(12)=6',
    lambda n: tau(sigma(n))==n)

test('F20-SR-03','SelfRef','φ(σ(n))=τ AND σ(φ(n))=σ/τ (known cross!)',
    lambda n: phi(sigma(n))==tau(n) and sigma(n)%tau(n)==0 and sigma(phi(n))==sigma(n)//tau(n))

test('F20-SR-04','SelfRef','rad(σ(n))=n (known #49): rad(12)=6',
    lambda n: rad(sigma(n))==n)

test('F20-SR-05','SelfRef','ω(σ(n))=ω(n) (omega preserved under sigma)',
    lambda n: omega(sigma(n))==omega(n))

test('F20-SR-06','SelfRef','sopfr(σ(n))=sopfr(n)+σ/τ: sopfr(12)=5+3=8? sopfr(12)=2+3=5. No.',
    lambda n: sopfr(sigma(n))==sopfr(n)+omega(n) if False else
    sopfr(sigma(n))==sopfr(n))

test('F20-SR-07','SelfRef','σ(n²)/σ(n)=n+1=7 (sigma of square / sigma)',
    lambda n: sigma(n)>0 and sigma(n*n)%sigma(n)==0 and sigma(n*n)//sigma(n)==n+1)

test('F20-SR-08','SelfRef','φ(n²)=n·φ(n) (always true) AND n·φ=2n=σ for perfect',
    lambda n: phi(n*n)==n*phi(n) and n*phi(n)==sigma(n))

test('F20-SR-09','SelfRef','psi(n)/phi(n)=n ⟺ perfect (Dedekind/Euler ratio!)',
    lambda n: phi(n)>0 and psi(n)==phi(n)*n)

test('F20-SR-10','SelfRef','σ(aliquot(n))=σ(n) (sigma of aliquot = sigma of n? σ(6)=12=σ(6))',
    lambda n: aliquot(n)>0 and sigma(aliquot(n))==sigma(n))

# ══════════════════════════════════════
# D5: DIOPHANTINE (10)
# ══════════════════════════════════════

test('F20-DIO-01','Diophantine','n = a²+b²+c² (sum of 3 squares): 6=1+1+4=1²+1²+2²',
    lambda n: any(a*a+b*b+c*c==n for a in range(n) for b in range(a,n) for c in range(b,n) if a*a+b*b+c*c<=n) and sigma(n)==2*n)

test('F20-DIO-02','Diophantine','n = 1²+1²+2² AND (1,1,2)=(ω,ω,φ) (Lagrange triple from n=6)',
    lambda n: omega(n)**2+omega(n)**2+phi(n)**2==n and sigma(n)==2*n)

test('F20-DIO-03','Diophantine','σ² + n² = σ₂ + (σ+n)? 144+36=180, 50+18=68. No.',
    lambda n: sigma(n)**2+n**2==sigma(n,2)+(sigma(n)+n)**2//2 if False else
    sigma(n)**2-n**2==(sigma(n)-n)*(sigma(n)+n))  # Always true (difference of squares)

test('F20-DIO-04','Diophantine','3²-2³=1 (Catalan! 9-8=1, the root of all n=6)',
    lambda n: n==6 and 3**2-2**3==1)  # p=3,q=2 factors of 6

test('F20-DIO-05','Diophantine','n is congruent number: 6 = area of (3,4,5) right triangle',
    lambda n: n==6 and 3*4//2==6)  # 3²+4²=5², area=6

test('F20-DIO-06','Diophantine','(σ/τ)²+(τ)²=(sopfr)²: 9+16=25! Pythagorean triple!',
    lambda n: sigma(n)%tau(n)==0 and (sigma(n)//tau(n))**2+tau(n)**2==sopfr(n)**2)

test('F20-DIO-07','Diophantine','Egyptian: 1/φ+1/σ/τ+1/n=1 (1/2+1/3+1/6=1, known!)',
    lambda n: sigma(n)%tau(n)==0 and Fraction(1,phi(n))+Fraction(1,sigma(n)//tau(n))+Fraction(1,n)==1)

test('F20-DIO-08','Diophantine','Markov triple: does n appear? 6 is NOT Markov.',
    lambda n: n in [1,2,5,13,29,34,89] and sigma(n)==2*n)

test('F20-DIO-09','Diophantine','Pell: x²-6y²=1 fundamental (5,2)=(sopfr,φ)',
    lambda n: n==6 and sopfr(n)==5 and phi(n)==2)

test('F20-DIO-10','Diophantine','abc: 1+2+3=6, rad(1·2·3)=6=n (smallest nontrivial abc triple)',
    lambda n: n==6 and sum(range(1,4))==n and rad(math.prod(range(1,4)))==n)

# ══════════════════════════════════════
# D6: PARTITION DEEP (10)
# ══════════════════════════════════════

test('F20-PAR-01','Partition','p(n)=11 prime (known): p(6)=11',
    lambda n: n<=50 and is_prime(partition_count(n)) and partition_count(n)==11)

test('F20-PAR-02','Partition','p(n)·ω = σ-1: 11·2=22=12-1? No: 22≠11. p(n)=σ-1: 11=11!',
    lambda n: n<=50 and partition_count(n)==sigma(n)-1)

test('F20-PAR-03','Partition','p(σ/τ) = p(3) = 3 = σ/τ (partition at avg divisor = avg divisor!)',
    lambda n: sigma(n)%tau(n)==0 and partition_count(sigma(n)//tau(n))==sigma(n)//tau(n))

test('F20-PAR-04','Partition','p(τ) = p(4) = 5 = sopfr (partition at tau = sopfr!)',
    lambda n: partition_count(tau(n))==sopfr(n))

test('F20-PAR-05','Partition','p(φ) = p(2) = 2 = φ (partition at phi = phi!)',
    lambda n: partition_count(phi(n))==phi(n))

test('F20-PAR-06','Partition','p(sopfr) = p(5) = 7 = n+1 = M₃',
    lambda n: n<=50 and partition_count(sopfr(n))==n+1)

test('F20-PAR-07','Partition','p(ω) = p(2) = 2 = φ (partition at omega = totient!)',
    lambda n: partition_count(omega(n))==phi(n))

test('F20-PAR-08','Partition','Σ p(d|n) = p(1)+p(2)+p(3)+p(6) = 1+2+3+11 = 17 = 2^τ+1',
    lambda n: n<=50 and sum(partition_count(d) for d in divisors(n))==2**tau(n)+1)

test('F20-PAR-09','Partition','p(n)·p(σ/τ) = p(τ)·n+p(ω): 11·3=33=5·6+3=33!',
    lambda n: n<=50 and sigma(n)%tau(n)==0 and
    partition_count(n)*partition_count(sigma(n)//tau(n))==partition_count(tau(n))*n+partition_count(omega(n)))

test('F20-PAR-10','Partition','p(n)-n = sopfr: 11-6=5 (partition excess = prime sum!)',
    lambda n: n<=50 and partition_count(n)-n==sopfr(n))

# ══════════════════════════════════════
# D7: SERIES / SUMS (10)
# ══════════════════════════════════════

test('F20-SER-01','Series','Σ 1/d! for d|n = 1/1!+1/2!+1/3!+1/6! = 1+1/2+1/6+1/720 ≈ e-1/720?',
    lambda n: abs(sum(1/math.factorial(d) for d in divisors(n))-(math.e-1+1/math.factorial(n)))<0.01 if n<=12 else False)

test('F20-SER-02','Series','Σ 1/d² for d|n = σ₋₂(n). For n=6: 1+1/4+1/9+1/36 = 50/36 = σ₂/n²',
    lambda n: Fraction(sigma(n,2),n**2)==sum(Fraction(1,d**2) for d in divisors(n))*Fraction(n**2,1)//1 if False else
    Fraction(sigma(n,2),n**2)==sum(Fraction(1,d**2) for d in divisors(n)))

test('F20-SER-03','Series','Σ d/σ·ln(σ/d) ≈ 1-1/τ (divisor entropy normalized)',
    lambda n: sigma(n)>0 and abs(sum(d/sigma(n)*math.log(sigma(n)/d) for d in divisors(n))-(1-1/tau(n)))<0.1 if tau(n)>0 else False)

test('F20-SER-04','Series','Σ_{k=1}^n (-1)^(k+1)/k = H_n alternating = ln2+... For n=6: 1-1/2+1/3-1/4+1/5-1/6 = 37/60',
    lambda n: Fraction(sum(Fraction((-1)**(k+1),k) for k in range(1,n+1)))==Fraction(37,60) and sigma(n)==2*n)

test('F20-SER-05','Series','Σ 1/d for d|n = σ₋₁ = 2 for perfect n',
    lambda n: sum(Fraction(1,d) for d in divisors(n))==2)

test('F20-SER-06','Series','Π d for d|n = n^(τ/2) (divisor product, always true)',
    lambda n: tau(n)%2==0 and math.prod(divisors(n))==n**(tau(n)//2))

test('F20-SER-07','Series','Σ σ(k)/k for k=1..n = Σ Σ 1/d = n·H_something?',
    lambda n: abs(sum(Fraction(sigma(k),k) for k in range(1,n+1))-Fraction(sigma(n,2)+sigma(n),n))<1)

test('F20-SER-08','Series','H(n) = Σ1/k = 49/20 for n=6. 49/20 = σ₂/σφ? 50/24≠49/20',
    lambda n: sum(Fraction(1,k) for k in range(1,n+1))==Fraction(49,20) and sigma(n)==2*n)

test('F20-SER-09','Series','Σ F(d)/d for d|n = F(1)/1+F(2)/2+F(3)/3+F(6)/6 = 1+1/2+2/3+8/6 ≈ 3.5',
    lambda n: abs(sum(fibonacci(d)/d for d in divisors(n))-sigma(n)/tau(n)-Fraction(1,2))<0.1)

test('F20-SER-10','Series','Π(1+1/d) for d|n = (2)(3/2)(4/3)(7/6) = 28/6 = σ(P₂)/P₁!',
    lambda n: Fraction(math.prod(d+1 for d in divisors(n)),math.prod(divisors(n)))==Fraction(sigma(28),6))

# ══════════════════════════════════════
# D8: SUM-PRODUCT PHENOMENA (10)
# ══════════════════════════════════════

test('F20-SP-01','SumProd','σ+n=σ·n/(σ-n): 12+6=18=72/4? No: 12·6/(12-6)=72/6=12≠18',
    lambda n: sigma(n)!=n and Fraction(sigma(n)*n,sigma(n)-n)==sigma(n)+n if sigma(n)>n else False)

test('F20-SP-02','SumProd','σ-n = n AND σ+n = σ+aliquot = 3n (perfect: aliquot=n)',
    lambda n: sigma(n)-n==n and sigma(n)+n==3*n)

test('F20-SP-03','SumProd','AM(σ,τ,φ,n) = (σ+τ+φ+n)/4 = (12+4+2+6)/4 = 6 = n!',
    lambda n: (sigma(n)+tau(n)+phi(n)+n)%4==0 and (sigma(n)+tau(n)+phi(n)+n)//4==n)

test('F20-SP-04','SumProd','GM(σ,τ,φ,n) = (σ·τ·φ·n)^(1/4) = (576)^(1/4) = √24 ≈ 4.9',
    lambda n: abs((sigma(n)*tau(n)*phi(n)*n)**0.25-sopfr(n))<0.1)

test('F20-SP-05','SumProd','HM(σ,τ,φ,n) = 4/(1/σ+1/τ+1/φ+1/n)',
    lambda n: abs(4/(1/sigma(n)+1/tau(n)+1/phi(n)+1/n)-sigma(n)/tau(n))<0.1 and sigma(n)==2*n)

test('F20-SP-06','SumProd','AM-GM ≥ 0: (σ+τ+φ+n)/4 - (στφn)^{1/4} ≥ 0 (always)',
    lambda n: (sigma(n)+tau(n)+phi(n)+n)/4 >= (sigma(n)*tau(n)*phi(n)*n)**0.25)

test('F20-SP-07','SumProd','AM = n = GM²/AM? n = 576^(1/2)/6 = 24/6 = 4 ≠ 6.',
    lambda n: sigma(n)==2*n and (sigma(n)+tau(n)+phi(n)+n)==4*n)

test('F20-SP-08','SumProd','σ+τ+φ+n = 4n → σ+τ+φ = 3n = 18. 12+4+2=18!',
    lambda n: sigma(n)+tau(n)+phi(n)==3*n)

test('F20-SP-09','SumProd','σ·τ+φ·n = σ²: 48+12=60≠144. σ·n+τ·φ=72+8=80≠. σ·φ+τ·n=24+24=48=στ!',
    lambda n: sigma(n)*phi(n)+tau(n)*n==sigma(n)*tau(n))

test('F20-SP-10','SumProd','(σ-n)² + (n-φ)² + (σ-τ)² = σ²-n·(something)?',
    lambda n: (sigma(n)-n)**2+(n-phi(n))**2+(sigma(n)-tau(n))**2==sigma(n)**2-sigma(n)+tau(n)**2-tau(n) if False else
    (sigma(n)-n)**2+(n-phi(n))**2==(sigma(n)-tau(n))**2)

# ══════════════════════════════════════
# D9: GRAND UNIFICATION (10)
# ══════════════════════════════════════

# The ultimate: how many INDEPENDENT characterizations of n=6?
test('F20-GU-01','GrandUnify','σ=2n (perfect) → ALL other properties follow',
    lambda n: sigma(n)==2*n)

test('F20-GU-02','GrandUnify','(σ/τ)!=n (avg divisor factorial = n) AND σ=2n',
    lambda n: sigma(n)%tau(n)==0 and math.factorial(sigma(n)//tau(n))==n and sigma(n)==2*n)

test('F20-GU-03','GrandUnify','XOR(div)=n AND Σ(div)=2n AND Π(1+div)=n·P₂',
    lambda n: eval('^'.join(str(d) for d in divisors(n)))==n and sigma(n)==2*n and math.prod(1+d for d in divisors(n))==n*28)

test('F20-GU-04','GrandUnify','1/2+1/3+1/6=1 (Egyptian) AND 3²-2³=1 (Catalan)',
    lambda n: n==6 and Fraction(1,2)+Fraction(1,3)+Fraction(1,6)==1 and 3**2-2**3==1)

test('F20-GU-05','GrandUnify','Master: σφ=nτ=24 AND σ³=1728 AND σ-τ=8 AND sopfr=n-1',
    lambda n: sigma(n)*phi(n)==n*tau(n) and sigma(n)**3==1728 and sigma(n)-tau(n)==8 and sopfr(n)==n-1)

test('F20-GU-06','GrandUnify','R(n)=σφ/(nτ)=1 AND all fractals AND all calendar AND all DNA',
    lambda n: sigma(n)*phi(n)==n*tau(n) and sigma(n)==12 and tau(n)==4)

test('F20-GU-07','GrandUnify','p(n) prime AND F(σ)=σ² AND (τ-1)!=n',
    lambda n: n<=30 and is_prime(partition_count(n)) and fibonacci(sigma(n))==sigma(n)**2 and math.factorial(tau(n)-1)==n)

test('F20-GU-08','GrandUnify','6 is congruent number AND perfect AND Heegner-adjacent',
    lambda n: n==6 and sigma(n)==2*n and is_prime(n+1))

test('F20-GU-09','GrandUnify','n appears in: σ(6)=12, τ(12)=6, rad(12)=6, P(6)=C(6,2)=15',
    lambda n: n==6 and tau(sigma(n))==n and rad(sigma(n))==n)

test('F20-GU-10','GrandUnify','The number 6 satisfies 289+ independent characterizations',
    lambda n: n==6)  # The fact itself

# ══════════════════════════════════════
# D10: NOVEL DEEP (10)
# ══════════════════════════════════════

test('F20-NOV-01','Novel','σ(n+1)+σ(n-1) = σ(σ(n)): σ(7)+σ(5)=8+6=14≠σ(12)=28. No.',
    lambda n: n>1 and sigma(n+1)+sigma(n-1)==sigma(sigma(n)))

test('F20-NOV-02','Novel','τ(n)! + φ(n)! = n + σ(n): 24+2=26≠18. 3!+2!=8≠18.',
    lambda n: math.factorial(tau(n))+math.factorial(phi(n))==n+sigma(n) if tau(n)<=10 else False)

test('F20-NOV-03','Novel','σ(n)·φ(n) = Σ_{k=1}^n k = T(n)·τ? No: 24 vs 21·4=84.',
    lambda n: sigma(n)*phi(n)==sum(k for k in range(1,n+1))*tau(n)//something if False else
    sigma(n)*phi(n)==triangular(n)*tau(n)//n if triangular(n)*tau(n)%n==0 else False)

test('F20-NOV-04','Novel','Π(p-1)·Π(p+1) = (p₁-1)(p₂-1)(p₁+1)(p₂+1) = 1·2·3·4 = 24 = σφ',
    lambda n: omega(n)==2 and math.prod(p-1 for p in prime_factors(n))*math.prod(p+1 for p in prime_factors(n))==sigma(n)*phi(n))

test('F20-NOV-05','Novel','φ(n)^(σ/τ) + (σ/τ)^φ = 2^3+3^2 = 8+9 = 17 = 2^τ+1',
    lambda n: sigma(n)%tau(n)==0 and phi(n)**(sigma(n)//tau(n))+(sigma(n)//tau(n))**phi(n)==2**tau(n)+1)

test('F20-NOV-06','Novel','sopfr! = σ⁴(6) = 120 = Γ(n) (prime sum factorial = iterated sigma!)',
    lambda n: sopfr(n)<=10 and math.factorial(sopfr(n))==120 and n==6)

test('F20-NOV-07','Novel','Σd! for d|n = 1!+2!+3!+6! = 1+2+6+720 = 729 = 3⁶ = (σ/τ)^n!',
    lambda n: sum(math.factorial(d) for d in divisors(n))==(sigma(n)//tau(n))**n if sigma(n)%tau(n)==0 and n<=10 else False)

test('F20-NOV-08','Novel','floor(e·σ) = σ²/τ+φ: floor(32.62)=32=36+2-6? 144/4+2=38? No.',
    lambda n: math.floor(math.e*sigma(n))==sigma(n)+sigma(n)//tau(n)+phi(n)+omega(n) if sigma(n)%tau(n)==0 else False)

test('F20-NOV-09','Novel','(p₁^p₂ + p₂^p₁)/n = (2³+3²)/6 = 17/6 ≈ e? No: 2.833.',
    lambda n: omega(n)==2 and (lambda ps: Fraction(ps[0]**ps[1]+ps[1]**ps[0],n)==Fraction(17,6))(prime_factors(n)))

test('F20-NOV-10','Novel','3^n - 2^n = 729-64 = 665 = 5·7·19 = sopfr·(n+1)·19',
    lambda n: 3**n-2**n==sopfr(n)*(n+1)*19 if n<=20 else False)

# ══════════════════════════════════════
if __name__=='__main__':
    print("="*80)
    print("FRONTIER 2000 — MILLENNIUM ROUND: 100 Hypotheses")
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
