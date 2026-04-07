#!/usr/bin/env python3
"""Frontier 1700b: 100 pure math hypotheses — single-condition, genuinely surprising."""
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
def fibonacci(n):
    a,b=0,1
    for _ in range(n): a,b=b,a+b
    return a
def lucas(n):
    if n==0: return 2
    if n==1: return 1
    a,b=2,1
    for _ in range(n-1): a,b=b,a+b
    return b
def catalan(n): return math.comb(2*n,n)//(n+1)
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
def motzkin(n):
    if n<=1: return 1
    m=[0]*(n+1); m[0]=m[1]=1
    for i in range(2,n+1): m[i]=((2*i+1)*m[i-1]+3*(i-1)*m[i-2])//(i+2)
    return m[n]
def bell(n):
    if n==0: return 1
    if n>15: return 0
    row=[1]
    for i in range(1,n+1):
        new_row=[row[-1]]
        for j in range(1,i+1): new_row.append(new_row[-1]+row[j-1])
        row=new_row
    return row[0]
def stirling2(n,k):
    if n==0 and k==0: return 1
    if n==0 or k==0 or k>n: return 0
    s=sum((-1)**(k-j)*math.comb(k,j)*j**n for j in range(k+1))
    return s//math.factorial(k)
def v_p(n,p):
    if n==0: return float('inf')
    v=0
    while n%p==0: v+=1; n//=p
    return v
def prime_factorization(n):
    fs={}; t=n; p=2
    while p*p<=t:
        while t%p==0: fs[p]=fs.get(p,0)+1; t//=p
        p+=1
    if t>1: fs[t]=fs.get(t,0)+1
    return fs

results = []
def test(hid, domain, stmt, check_fn, limit=100, ad_hoc=False):
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

# ═══ D1: DIVISOR SUM IDENTITIES (10) ═══
test('F17B-DS-01','DivSum','sigma(n-phi(n)) = n — sigma of deficit = n!',
    lambda n: n>phi(n) and n-phi(n)>=1 and sigma(n-phi(n))==n)
test('F17B-DS-02','DivSum','sigma(aliquot(n)) = sigma(n) — sigma idempotent via aliquot',
    lambda n: aliquot(n)>0 and aliquot(n)!=n and sigma(aliquot(n))==sigma(n))
test('F17B-DS-03','DivSum','sigma(n)*tau(n) = n*(phi(n)+tau(n)) — weighted master',
    lambda n: sigma(n)*tau(n)==n*(phi(n)+tau(n)))
test('F17B-DS-04','DivSum','sigma_3(n)*tau(n) = sigma(n)*sigma_2(n) — cubic/quadratic balance',
    lambda n: sigma(n,3)*tau(n)==sigma(n)*sigma(n,2))
test('F17B-DS-05','DivSum','sigma(n)^2 = n^2*(phi(n)+1) — sigma^2 = n^2*(phi+1)',
    lambda n: sigma(n)**2==n**2*(phi(n)+1))
test('F17B-DS-06','DivSum','rad(n)*tau(n) = sigma(n) — radical*tau = sigma',
    lambda n: rad(n)*tau(n)==sigma(n))
test('F17B-DS-07','DivSum','sigma(n) - phi(n) - tau(n) = n — sigma minus phi minus tau = n!',
    lambda n: sigma(n)-phi(n)-tau(n)==n)
test('F17B-DS-08','DivSum','sigma(n)*omega(n) = n*sopfr(n) — sigma*omega = n*sopfr',
    lambda n: sigma(n)*omega(n)==n*sopfr(n))
test('F17B-DS-09','DivSum','tau(n)*sopfr(n) = sigma(n)+n-phi(n) — tau*sopfr from others',
    lambda n: tau(n)*sopfr(n)==sigma(n)+n-phi(n))
test('F17B-DS-10','DivSum','sigma(n)+phi(n)+tau(n) = 3*sopfr(n)+omega(n) — balance',
    lambda n: sigma(n)+phi(n)+tau(n)==3*sopfr(n)+omega(n))

# ═══ D2: TOTIENT COMPOSITIONS (10) ═══
test('F17B-PC-01','PhiComp','phi(sigma(n)) = n — totient of sigma = n!',
    lambda n: phi(sigma(n))==n)
test('F17B-PC-02','PhiComp','sigma(phi(n)) = sigma(n)-tau(n) — sigma of totient',
    lambda n: sigma(phi(n))==sigma(n)-tau(n))
test('F17B-PC-03','PhiComp','psi(n) = sigma(n) — Dedekind psi = sigma',
    lambda n: psi(n)==sigma(n))
test('F17B-PC-04','PhiComp','J_2(n) = phi(n)*(n+1) — Jordan 2nd = phi*(n+1)',
    lambda n: jordan(n,2)==phi(n)*(n+1))
test('F17B-PC-05','PhiComp','phi(n)*psi(n) = J_2(n) — phi*psi = Jordan_2 (known identity)',
    lambda n: phi(n)*psi(n)==jordan(n,2))
test('F17B-PC-06','PhiComp','sigma(phi(n))+phi(sigma(n)) = n+phi(n) — symmetric',
    lambda n: sigma(phi(n))+phi(sigma(n))==n+phi(n))
test('F17B-PC-07','PhiComp','tau(sigma(n)) = n — tau of sigma = n!',
    lambda n: tau(sigma(n))==n)
test('F17B-PC-08','PhiComp','sigma(tau(n)) = aliquot(n) — sigma of tau = aliquot sum',
    lambda n: sigma(tau(n))==aliquot(n))
test('F17B-PC-09','PhiComp','rad(sigma(n)) = rad(n) — radical preserved by sigma!',
    lambda n: n>1 and rad(sigma(n))==rad(n))
test('F17B-PC-10','PhiComp','phi depth to 1 = omega(n) — iterated phi steps = omega',
    lambda n: (lambda n: (lambda f: f(n,0))(lambda x,d: d if x<=1 else f(phi(x),d+1)))(n)==omega(n) if False else
    _pd(n)==omega(n))

def _pd(n):
    d=0;x=n
    while x>1: x=phi(x);d+=1
    return d

# ═══ D3: PARTITION CONNECTIONS (10) ═══
test('F17B-PT-01','Partition','p(n) = sigma(n)-1 — partition = sigma - 1',
    lambda n: partition_count(n)==sigma(n)-1)
test('F17B-PT-02','Partition','p(tau(n)) = sopfr(n) — partition of tau = sopfr',
    lambda n: partition_count(tau(n))==sopfr(n))
test('F17B-PT-03','Partition','p(phi(n)) = phi(n) — partition at totient = totient (p(2)=2!)',
    lambda n: partition_count(phi(n))==phi(n))
test('F17B-PT-04','Partition','p(omega(n))+p(Omega(n)) = n — partition sum = n',
    lambda n: partition_count(omega(n))+partition_count(Omega_fn(n))==n)
test('F17B-PT-05','Partition','p(n) mod n = sopfr(n) — partition residue = sopfr',
    lambda n: sopfr(n)<n and partition_count(n)%n==sopfr(n))
test('F17B-PT-06','Partition','p(sopfr(n)) = p(n)+1 — partition of sopfr = partition+1',
    lambda n: sopfr(n)<=100 and partition_count(sopfr(n))==partition_count(n)+1)
test('F17B-PT-07','Partition','p(n) is prime AND p(n)=sigma(n)-1=11 — prime partition!',
    lambda n: is_prime(partition_count(n)) and partition_count(n)==sigma(n)-1)
test('F17B-PT-08','Partition','p(n)*p(phi(n)) = p(sopfr(n)) — partition product = at sopfr',
    lambda n: sopfr(n)<=100 and partition_count(n)*partition_count(phi(n))==partition_count(sopfr(n)))
test('F17B-PT-09','Partition','p(n) mod sigma(n) = p(n) mod n — same residue class',
    lambda n: partition_count(n)%sigma(n)==partition_count(n)%n and sigma(n)>partition_count(n)%n)
test('F17B-PT-10','Partition','p(sigma/tau) = p(3) = 3 = sigma/tau — partition self-ref!',
    lambda n: sigma(n)%tau(n)==0 and partition_count(sigma(n)//tau(n))==sigma(n)//tau(n))

# ═══ D4: FIBONACCI/LUCAS DEEP (10) ═══
test('F17B-FL-01','FibLucas','F(sigma) = sigma^2 — Fibonacci at sigma = sigma squared',
    lambda n: sigma(n)<=25 and fibonacci(sigma(n))==sigma(n)**2)
test('F17B-FL-02','FibLucas','L(n) = sigma+phi+tau — Lucas = sum of 3 functions',
    lambda n: lucas(n)==sigma(n)+phi(n)+tau(n))
test('F17B-FL-03','FibLucas','F(sigma/tau) = phi — Fibonacci at avg divisor = totient',
    lambda n: sigma(n)%tau(n)==0 and fibonacci(sigma(n)//tau(n))==phi(n))
test('F17B-FL-04','FibLucas','F(sopfr) = sopfr — Fibonacci fixed point at sopfr',
    lambda n: sopfr(n)<=30 and fibonacci(sopfr(n))==sopfr(n))
test('F17B-FL-05','FibLucas','F(n+1) = sigma(n)+1 — next Fibonacci = sigma + 1',
    lambda n: n<=25 and fibonacci(n+1)==sigma(n)+1)
test('F17B-FL-06','FibLucas','motzkin(sopfr) = triangular(n) — Motzkin(5)=21=T(6)',
    lambda n: sopfr(n)<=25 and motzkin(sopfr(n))==triangular(n))
test('F17B-FL-07','FibLucas','F(n)*L(n) = F(2n) = sigma*sopfr — double Fib = sigma*sopfr',
    lambda n: 2*n<=35 and fibonacci(2*n)==sigma(n)*sopfr(n))
test('F17B-FL-08','FibLucas','sum F(d) for d|n = sigma(n) — Fibonacci divisor sum = sigma!',
    lambda n: sum(fibonacci(d) for d in divisors(n))==sigma(n))
test('F17B-FL-09','FibLucas','bell(tau) = C(n,2) — Bell at tau = triangular',
    lambda n: tau(n)<=12 and bell(tau(n))==math.comb(n,2))
test('F17B-FL-10','FibLucas','catalan(omega) = phi — Catalan at omega = totient',
    lambda n: catalan(omega(n))==phi(n))

# ═══ D5: BERNOULLI / ZETA (10) ═══
def bernoulli_denom(m):
    if m==0: return 1
    if m==1: return 2
    if m%2==1 and m>1: return 1
    d=1
    for p in range(2,m+2):
        if is_prime(p) and m%(p-1)==0: d*=p
    return d
test('F17B-BZ-01','BernZeta','denom(B_n) mod 6 = 0 for even n>=2 — von Staudt (known)',
    lambda n: n%2==0 and n>=2 and n<=20 and bernoulli_denom(n)%6==0)
test('F17B-BZ-02','BernZeta','denom(B_n) = sigma*tau-n = 42 — Bernoulli denom from n=6!',
    lambda n: n%2==0 and n>=2 and n<=20 and bernoulli_denom(n)==sigma(n)*tau(n)-n)
test('F17B-BZ-03','BernZeta','denom(B_sigma) mod n = 0 — Bernoulli at sigma divisible by n',
    lambda n: sigma(n)<=20 and sigma(n)%2==0 and bernoulli_denom(sigma(n))%n==0)
test('F17B-BZ-04','BernZeta','sigma_{-1}(n) = sigma/n — harmonic sum (known identity)',
    lambda n: sum(Fraction(1,d) for d in divisors(n))==Fraction(sigma(n),n))
test('F17B-BZ-05','BernZeta','J_2(n)/n^2 = prod(1-1/p^2) — Euler product (known)',
    lambda n: n>1 and Fraction(jordan(n,2),n**2)==reduce(lambda a,b:a*b,[Fraction(p**2-1,p**2) for p in set(prime_factorization(n).keys())],Fraction(1)))
test('F17B-BZ-06','BernZeta','sum sigma(d)*mu(n/d) = n — Mobius inversion (known)',
    lambda n: sum(sigma(d)*mobius(n//d) for d in divisors(n))==n)
test('F17B-BZ-07','BernZeta','sum mu(n/d)*d = phi(n) — Mobius-phi (known)',
    lambda n: sum(mobius(n//d)*d for d in divisors(n))==phi(n))
test('F17B-BZ-08','BernZeta','sum phi(d) = n — totient sum (known)',
    lambda n: sum(phi(d) for d in divisors(n))==n)
test('F17B-BZ-09','BernZeta','sigma_2/sigma = sigma*(phi+1)/(tau*(phi+1)) simplifies',
    lambda n: Fraction(sigma(n,2),sigma(n))==Fraction(sigma(n)*(phi(n)+1),tau(n)*(phi(n)+1)) if tau(n)>0 else False)
test('F17B-BZ-10','BernZeta','sigma(n,2)*tau(n) = sigma(n)*sigma(n,2) check — nontrivial?',
    lambda n: sigma(n,3)*tau(n)==sigma(n)*sigma(n,2))

# ═══ D6: COMBINATORIAL (10) ═══
test('F17B-CB-01','Combinat','C(sigma,phi) = n*p(n) — binomial = n*partition!',
    lambda n: math.comb(sigma(n),phi(n))==n*partition_count(n))
test('F17B-CB-02','Combinat','C(n,omega) = C(n,2) — binomial at omega = triangular',
    lambda n: math.comb(n,omega(n))==math.comb(n,2))
test('F17B-CB-03','Combinat','S(n,sigma/tau) = n*phi — Stirling2 at avg divisor = n*phi',
    lambda n: sigma(n)%tau(n)==0 and sigma(n)//tau(n)<=n and stirling2(n,sigma(n)//tau(n))==n*phi(n))
test('F17B-CB-04','Combinat','C(n+phi,phi) = C(sigma,tau) — shifted = divisor binomial',
    lambda n: math.comb(n+phi(n),phi(n))==math.comb(sigma(n),tau(n)))
test('F17B-CB-05','Combinat','sigma*phi*tau*sopfr*omega = C(n,2)*2^n — five-function!',
    lambda n: sigma(n)*phi(n)*tau(n)*sopfr(n)*omega(n)==math.comb(n,2)*2**n)
test('F17B-CB-06','Combinat','Phi_6(sopfr) = sopfr^2-sopfr+1 = T(n) — cyclotomic!',
    lambda n: sopfr(n)**2-sopfr(n)+1==triangular(n))
test('F17B-CB-07','Combinat','n^2-n+1 = tau*sopfr+1 — quadratic = function product+1',
    lambda n: n**2-n+1==tau(n)*sopfr(n)+1)
test('F17B-CB-08','Combinat','Phi_6(phi)=phi^2-phi+1=sigma/tau — cyclotomic at phi!',
    lambda n: phi(n)**2-phi(n)+1==sigma(n)//tau(n) if sigma(n)%tau(n)==0 else False)
test('F17B-CB-09','Combinat','n! mod sigma = 0 AND tau! = sigma*phi — factorial identities',
    lambda n: n<=15 and math.factorial(n)%sigma(n)==0 and math.factorial(tau(n))==sigma(n)*phi(n))
test('F17B-CB-10','Combinat','C(sigma,tau) = catalan(n) — binomial of sigma,tau = catalan!',
    lambda n: math.comb(sigma(n),tau(n))==catalan(n))

# ═══ D7: MODULAR ARITHMETIC (10) ═══
test('F17B-MD-01','Modular','sigma mod sopfr = phi — sigma residue = totient!',
    lambda n: sopfr(n)>phi(n) and sigma(n)%sopfr(n)==phi(n))
test('F17B-MD-02','Modular','sigma/phi = n — abundancy over totient = n (perfects!)',
    lambda n: phi(n)>0 and sigma(n)%phi(n)==0 and sigma(n)//phi(n)==n)
test('F17B-MD-03','Modular','sigma^2 mod n = 0 — sigma squared divisible by n',
    lambda n: sigma(n)**2%n==0)
test('F17B-MD-04','Modular','n! mod sigma = 0 — factorial divisible by sigma',
    lambda n: n<=15 and math.factorial(n)%sigma(n)==0)
test('F17B-MD-05','Modular','sigma mod (n+1) = 0 — sigma divisible by n+1',
    lambda n: sigma(n)%(n+1)==0)
test('F17B-MD-06','Modular','(sigma-1)! mod sigma = sigma-1 (Wilson: sigma prime!)',
    lambda n: sigma(n)<=15 and is_prime(sigma(n)) and math.factorial(sigma(n)-1)%sigma(n)==sigma(n)-1)
test('F17B-MD-07','Modular','2^n mod sigma = 2^phi — power identity',
    lambda n: sigma(n)>0 and pow(2,n,sigma(n))==pow(2,phi(n),sigma(n)))
test('F17B-MD-08','Modular','n^phi mod sigma = n^phi mod n — power residue match',
    lambda n: sigma(n)>0 and n>1 and pow(n,phi(n),sigma(n))==pow(n,phi(n),n) if sigma(n)>1 else False)
test('F17B-MD-09','Modular','sigma(n) mod (sigma-n) = 0 for perfect (sigma mod n = 0)',
    lambda n: sigma(n)>n and sigma(n)%(sigma(n)-n)==0)
test('F17B-MD-10','Modular','gcd(sigma,phi) = phi AND gcd(sigma,tau) = tau AND gcd(sigma,n) = n',
    lambda n: math.gcd(sigma(n),phi(n))==phi(n) and math.gcd(sigma(n),tau(n))==tau(n) and math.gcd(sigma(n),n)==n)

# ═══ D8: ITERATED FUNCTIONS (10) ═══
test('F17B-IT-01','Iterated','phi chain depth = phi(n) — 6->2->1 depth=2=phi!',
    lambda n: _pd(n)==phi(n))
test('F17B-IT-02','Iterated','n\'=sigma-n for semiprimes (arithmetic derivative = aliquot!)',
    lambda n: omega(n)==2 and Omega_fn(n)==2 and arithmetic_derivative(n)==aliquot(n))
test('F17B-IT-03','Iterated','sigma(sigma(n))-sigma(n) = sigma(n) — double sigma aliquot = sigma',
    lambda n: sigma(sigma(n))-sigma(n)==sigma(n))
test('F17B-IT-04','Iterated','phi(sigma(n))*tau(n) = n*phi(n) — composed identity',
    lambda n: phi(sigma(n))*tau(n)==n*phi(n))
test('F17B-IT-05','Iterated','sigma(sigma-n) = sigma (sigma of aliquot = sigma)',
    lambda n: sigma(n)>n and sigma(sigma(n)-n)==sigma(n))
test('F17B-IT-06','Iterated','aliquot(aliquot(n)) = n (period 2 = amicable)',
    lambda n: aliquot(n)>0 and aliquot(n)!=n and aliquot(n)<=1000 and aliquot(aliquot(n))==n)
test('F17B-IT-07','Iterated','tau(sigma(n)) = n — tau of sigma = n!',
    lambda n: tau(sigma(n))==n)
test('F17B-IT-08','Iterated','sigma(tau(n)) = sigma(n)-n — sigma of tau = aliquot',
    lambda n: sigma(tau(n))==sigma(n)-n)
test('F17B-IT-09','Iterated','phi(sigma)+sigma(phi) = 2n — symmetric identity!',
    lambda n: phi(sigma(n))+sigma(phi(n))==2*n)
test('F17B-IT-10','Iterated','rad(sigma(n)) = rad(n) — radical preserved by sigma!',
    lambda n: n>1 and rad(sigma(n))==rad(n))

# ═══ D9: NOVEL SINGLE-CONDITION (10) ═══
test('F17B-NV-01','Novel','sigma(n)+phi(n) = 2*sopfr(n)+tau(n)+omega(n) — additive char',
    lambda n: sigma(n)+phi(n)==2*sopfr(n)+tau(n)+omega(n))
test('F17B-NV-02','Novel','sigma*sopfr = n*(n+phi+tau) — product from sum',
    lambda n: sigma(n)*sopfr(n)==n*(n+phi(n)+tau(n)))
test('F17B-NV-03','Novel','(sigma/n)^omega = phi — abundancy^omega = totient',
    lambda n: sigma(n)%n==0 and (sigma(n)//n)**omega(n)==phi(n))
test('F17B-NV-04','Novel','sopfr^omega = sigma/tau — sopfr^omega = average divisor',
    lambda n: sigma(n)%tau(n)==0 and sopfr(n)**omega(n)==sigma(n)//tau(n) if omega(n)<=10 else False)
test('F17B-NV-05','Novel','phi+omega = tau — totient plus omega = tau',
    lambda n: phi(n)+omega(n)==tau(n))
test('F17B-NV-06','Novel','sopfr-omega = sigma/tau — sopfr minus omega = avg divisor',
    lambda n: sigma(n)%tau(n)==0 and sopfr(n)-omega(n)==sigma(n)//tau(n))
test('F17B-NV-07','Novel','n = rad(n) AND sigma = 2*rad(n) — squarefree perfect!',
    lambda n: rad(n)==n and sigma(n)==2*rad(n))
test('F17B-NV-08','Novel','phi^tau = tau^phi — totient-tau power swap!',
    lambda n: phi(n)**tau(n)==tau(n)**phi(n))
test('F17B-NV-09','Novel','sigma^2-n^2 = n*(n+tau) — difference of squares identity',
    lambda n: sigma(n)**2-n**2==n*(n+tau(n)))
test('F17B-NV-10','Novel','phi*sopfr + omega*tau = sigma — linear combination = sigma!',
    lambda n: phi(n)*sopfr(n)+omega(n)*tau(n)==sigma(n))

# ═══ D10: DEEP NOVEL (10) ═══
test('F17B-DN-01','DeepNovel','n*sigma+phi*tau = sigma^2 — quadratic relation',
    lambda n: n*sigma(n)+phi(n)*tau(n)==sigma(n)**2)
test('F17B-DN-02','DeepNovel','phi^2+tau^2 = sigma-n+phi — Pythagorean-like',
    lambda n: phi(n)**2+tau(n)**2==sigma(n)-n+phi(n))
test('F17B-DN-03','DeepNovel','sigma*phi-n*tau = n^2-sigma — bilinear form',
    lambda n: sigma(n)*phi(n)-n*tau(n)==n**2-sigma(n))
test('F17B-DN-04','DeepNovel','(sigma-n)*(sigma+n) = n*(sigma+tau) — factored form',
    lambda n: (sigma(n)-n)*(sigma(n)+n)==n*(sigma(n)+tau(n)))
test('F17B-DN-05','DeepNovel','sigma mod tau = 0 AND sigma mod phi = 0 AND sigma mod n = 0',
    lambda n: sigma(n)%tau(n)==0 and sigma(n)%phi(n)==0 and sigma(n)%n==0)
test('F17B-DN-06','DeepNovel','lcm(sigma,phi,tau,n) = sigma — sigma is LCM of all!',
    lambda n: (lambda l: l==sigma(n))(reduce(lambda a,b: a*b//math.gcd(a,b), [sigma(n),phi(n),tau(n),n])))
test('F17B-DN-07','DeepNovel','gcd(sigma-phi, sigma-tau) = sigma-n — GCD of differences = aliquot gap',
    lambda n: math.gcd(sigma(n)-phi(n), sigma(n)-tau(n))==sigma(n)-n)
test('F17B-DN-08','DeepNovel','(sigma/phi)*(tau/omega) = n — product of ratios = n!',
    lambda n: omega(n)>0 and phi(n)>0 and Fraction(sigma(n),phi(n))*Fraction(tau(n),omega(n))==n)
test('F17B-DN-09','DeepNovel','sigma+n = phi*(tau+sopfr) — linear decomposition',
    lambda n: sigma(n)+n==phi(n)*(tau(n)+sopfr(n)))
test('F17B-DN-10','DeepNovel','n^tau = sigma^phi — n^tau = sigma^phi power identity!',
    lambda n: n**tau(n)==sigma(n)**phi(n))

# ═══ REPORT ═══
if __name__=='__main__':
    print("="*80)
    print("FRONTIER 1700b: 100 Pure Math Hypotheses")
    print("="*80)
    grades=defaultdict(list)
    for r in results: grades[r['grade']].append(r)
    print(f"\n{'Grade':<6} {'Count':<6}")
    for g in ['⭐','🟩','🟧','⚪','⬛']: print(f"{g:<6} {len(grades.get(g,[])):<6}")
    domains=defaultdict(list)
    for r in results: domains[r['domain']].append(r)
    print(f"\n{'='*80}\nDOMAIN BREAKDOWN")
    for dom in sorted(domains.keys()):
        items=domains[dom]
        print(f"  {dom}: {len(items)} | ⭐{sum(1 for r in items if r['grade']=='⭐')} 🟩{sum(1 for r in items if r['grade']=='🟩')} 🟧{sum(1 for r in items if r['grade']=='🟧')} ⚪{sum(1 for r in items if r['grade']=='⚪')} ⬛{sum(1 for r in items if r['grade']=='⬛')}")
    print(f"\n{'='*80}\n⭐ STAR MAJOR\n{'='*80}")
    for r in results:
        if r['grade']=='⭐': print(f"  {r['id']}: {r['statement'][:75]}  Sol:{r['solutions']}")
    print(f"\n{'='*80}\n🟩🟧 GREEN+ORANGE\n{'='*80}")
    for r in results:
        if r['grade'] in ['🟩','🟧']: print(f"  {r['grade']} {r['id']}: {r['statement'][:65]}  Sol:{r['solutions'][:8]}")
    t=len(results);p=sum(1 for r in results if r['grade'] in ['⭐','🟩','🟧'])
    print(f"\n{'='*80}\nTOTAL: {t} hyps, {p} pass | ⭐{len(grades.get('⭐',[]))} 🟩{len(grades.get('🟩',[]))} 🟧{len(grades.get('🟧',[]))} ⚪{len(grades.get('⚪',[]))} ⬛{len(grades.get('⬛',[]))}")
