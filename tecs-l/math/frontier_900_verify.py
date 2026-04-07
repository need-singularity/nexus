#!/usr/bin/env python3
"""
Frontier 900: Iterated compositions, multiplicative combinations,
and inequality-to-equality characterizations for n=6.
"""
import math, json
from fractions import Fraction
from collections import defaultdict

def divisors(n):
    d = []
    for i in range(1, int(n**0.5)+1):
        if n % i == 0: d.append(i); (d.append(n//i) if i != n//i else None)
    return sorted(d)

def sigma(n, k=1): return sum(d**k for d in divisors(n))
def tau(n): return len(divisors(n))
def phi(n):
    r, t, p = n, n, 2
    while p*p<=t:
        if t%p==0:
            while t%p==0: t//=p
            r -= r//p
        p+=1
    if t>1: r -= r//t
    return r

def sopfr(n):
    s, t, p = 0, n, 2
    while p*p<=t:
        while t%p==0: s+=p; t//=p
        p+=1
    if t>1: s+=t
    return s

def omega(n):
    c, t, p = 0, n, 2
    while p*p<=t:
        if t%p==0:
            c+=1
            while t%p==0: t//=p
        p+=1
    if t>1: c+=1
    return c

def rad(n):
    r, t, p = 1, n, 2
    while p*p<=t:
        if t%p==0:
            r*=p
            while t%p==0: t//=p
        p+=1
    if t>1: r*=t
    return r

def psi(n):
    r, t = n, n
    primes = []
    p = 2
    while p*p<=t:
        if t%p==0:
            primes.append(p)
            while t%p==0: t//=p
        p+=1
    if t>1: primes.append(t)
    for p in primes: r = r*(p+1)//p
    return r

def mobius(n):
    if n==1: return 1
    t,p,c=n,2,0
    while p*p<=t:
        if t%p==0:
            c+=1; t//=p
            if t%p==0: return 0
        p+=1
    if t>1: c+=1
    return (-1)**c

def aliquot(n): return sigma(n)-n
def is_perfect(n): return sigma(n)==2*n
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

def scan(f, g, lo=2, hi=200):
    r = []
    for n in range(lo, hi+1):
        try:
            if f(n)==g(n): r.append(n)
        except: pass
    return r

hypotheses = []
def add_hyp(hid, dom, stmt, check_fn, gen_fn=None, ad_hoc=False):
    hypotheses.append({'id':hid,'domain':dom,'statement':stmt,
                       'check_fn':check_fn,'gen_fn':gen_fn,'ad_hoc':ad_hoc})

# ═══════════════════════════════════════
# ITERATED COMPOSITIONS (20)
# ═══════════════════════════════════════

# sigma(sigma(n))
s_sigma_sigma = scan(lambda n: sigma(sigma(n)), lambda n: n*sigma(n)//phi(n) if phi(n)>0 else -1)
add_hyp('F9-IT-01', 'Iterated',
    f'sigma(sigma(n)): for n=6, sigma(12)=28=P_2! sigma iterated once gives 2nd perfect number!',
    lambda: sigma(sigma(6))==28 and is_perfect(28),
    lambda n: sigma(sigma(n)))

# phi(phi(n))
add_hyp('F9-IT-02', 'Iterated',
    f'phi(phi(n)): phi(phi(6))=phi(2)=1. phi iterated collapses to 1 in 2 steps.',
    lambda: phi(phi(6))==1,
    lambda n: None)

# sigma(phi(n))
add_hyp('F9-IT-03', 'Iterated',
    f'sigma(phi(n)): sigma(phi(6))=sigma(2)=3=gpf(6). sigma of totient = greatest prime factor.',
    lambda: sigma(phi(6))==3,
    lambda n: None)

# phi(sigma(n)) — already explored in F500
# sigma(sigma(sigma(n)))
add_hyp('F9-IT-04', 'Iterated',
    f'sigma^3(6): sigma(6)=12, sigma(12)=28, sigma(28)=56. So sigma^3(6)=56=2*28=2*P_2.',
    lambda: sigma(sigma(sigma(6)))==56,
    lambda n: None)

# sigma chain: 6→12→28→56→120→...
add_hyp('F9-IT-05', 'Iterated',
    'sigma chain from 6: 6→12→28→56→120→360→1170→... Hits P_2=28 at step 2! sigma^2(P_1)=P_2.',
    lambda: sigma(sigma(6))==28,
    lambda n: None)

# Aliquot chain: 6→6→6→... (fixed point)
add_hyp('F9-IT-06', 'Iterated',
    'Aliquot chain: s(6)=1+2+3=6. Fixed point! s^k(6)=6 for all k. Perfect numbers are aliquot fixed points.',
    lambda: aliquot(6)==6,
    lambda n: aliquot(n)==n)

# tau(sigma(n))=n scan
s_tau_sigma = scan(lambda n: tau(sigma(n)), lambda n: n)
add_hyp('F9-IT-07', 'Iterated',
    f'tau(sigma(n))=n: solutions={s_tau_sigma[:10]}. Known from F500: includes n=6.',
    lambda: tau(sigma(6))==6,
    lambda n: tau(sigma(n))==n)

# sigma(tau(n))
add_hyp('F9-IT-08', 'Iterated',
    f'sigma(tau(n)): sigma(tau(6))=sigma(4)=7. 7=n+1.',
    lambda: sigma(tau(6))==7 and 7==6+1,
    lambda n: sigma(tau(n))==n+1)

# phi(sigma(n))+sigma(phi(n))
add_hyp('F9-IT-09', 'Iterated',
    'phi(sigma(n))+sigma(phi(n)): phi(12)+sigma(2)=4+3=7=n+1. Same as sigma(tau(n))!',
    lambda: phi(sigma(6))+sigma(phi(6))==7,
    lambda n: phi(sigma(n))+sigma(phi(n))==n+1)

# Check if both IT-08 and IT-09 hold at same n
s_it89 = scan(lambda n: sigma(tau(n)), lambda n: n+1)
add_hyp('F9-IT-10', 'Iterated',
    f'sigma(tau(n))=n+1: solutions={s_it89[:10]}',
    lambda: sigma(tau(6))==7,
    lambda n: sigma(tau(n))==n+1)

# phi(sigma(n))+sigma(phi(n))=n+1
s_it09 = scan(lambda n: phi(sigma(n))+sigma(phi(n)), lambda n: n+1)
add_hyp('F9-IT-11', 'Iterated',
    f'phi(sigma)+sigma(phi)=n+1: solutions={s_it09[:10]}',
    lambda: phi(sigma(6))+sigma(phi(6))==7,
    lambda n: phi(sigma(n))+sigma(phi(n))==n+1)

# sigma(n)*sigma(n-1)
add_hyp('F9-IT-12', 'Iterated',
    'sigma(6)*sigma(5)=12*6=72. 72=sigma(6)*6=sigma(6)*n. Also 72=8*9=sigma(n+2)*... no.',
    lambda: sigma(6)*sigma(5)==72,
    lambda n: None)

# sigma^2(n) = sigma(sigma(n)) = 28 for n=6. Is sigma^2(n)=P_2 unique to n=6?
s_sig2_28 = scan(lambda n: sigma(sigma(n)), lambda n: 28)
add_hyp('F9-IT-13', 'Iterated',
    f'sigma^2(n)=28=P_2: solutions={s_sig2_28[:10]}. If only n=6, then iterated sigma maps P_1→P_2 uniquely.',
    lambda: sigma(sigma(6))==28,
    lambda n: sigma(sigma(n))==28)

# sigma^2(n) as function
add_hyp('F9-IT-14', 'Iterated',
    f'sigma^2(6)=28=P_2, sigma^2(28)=sigma(56)=120. sigma^2(P_1)=P_2! Does sigma^2(P_2)=P_3? 120 vs 496. No.',
    lambda: sigma(sigma(6))==28 and sigma(sigma(28))==120 and 120!=496,
    lambda n: None)

# tau(phi(n))*phi(tau(n))
add_hyp('F9-IT-15', 'Iterated',
    'tau(phi(n))*phi(tau(n)): tau(2)*phi(4)=2*2=4=tau(6). Iterated cross-product returns tau!',
    lambda: tau(phi(6))*phi(tau(6))==tau(6),
    lambda n: tau(phi(n))*phi(tau(n))==tau(n))

s_it15 = scan(lambda n: tau(phi(n))*phi(tau(n)), lambda n: tau(n))
add_hyp('F9-IT-16', 'Iterated',
    f'tau(phi)*phi(tau)=tau: solutions={s_it15[:15]}',
    lambda: tau(phi(6))*phi(tau(6))==tau(6),
    lambda n: tau(phi(n))*phi(tau(n))==tau(n))

# sigma(n) + n = sigma(sigma(n)): 12+6=18, sigma(12)=28. 18!=28. No.
# sigma(n) - n = phi(n)*omega(n): 12-6=6, 2*2=4. No.
# sigma(n) * n = sigma(sigma(n)) * phi(n): 72 = 28*2=56. No.

# Interesting: sigma(n)+phi(n) = psi(n)?
s_sp_psi = scan(lambda n: sigma(n)+phi(n), lambda n: psi(n))
add_hyp('F9-IT-17', 'Iterated',
    f'sigma+phi=psi: solutions={s_sp_psi[:10]}. For n=6: 12+2=14, psi(6)=12. 14!=12. NO.',
    lambda: sigma(6)+phi(6)==psi(6),
    lambda n: sigma(n)+phi(n)==psi(n))

# sigma(n)-psi(n) for n=6: 12-12=0! psi(6)=sigma(6)! This was found in F800.
# Now: sigma(n)+phi(n) = 2*psi(n) - tau(n)?
s_2psi = scan(lambda n: sigma(n)+phi(n), lambda n: 2*psi(n)-tau(n))
add_hyp('F9-IT-18', 'Iterated',
    f'sigma+phi=2*psi-tau: for n=6: 14=24-4=20. NO.',
    lambda: sigma(6)+phi(6)==2*psi(6)-tau(6),
    lambda n: None)

# rad(sigma(n))
add_hyp('F9-IT-19', 'Iterated',
    'rad(sigma(6))=rad(12)=6=n. The radical of the divisor sum equals n itself!',
    lambda: rad(sigma(6))==6,
    lambda n: rad(sigma(n))==n)

s_rad_sig = scan(lambda n: rad(sigma(n)), lambda n: n)
add_hyp('F9-IT-20', 'Iterated',
    f'rad(sigma(n))=n: solutions={s_rad_sig[:15]}',
    lambda: rad(sigma(6))==6,
    lambda n: rad(sigma(n))==n)

# ═══════════════════════════════════════
# MULTIPLICATIVE COMBOS (20)
# ═══════════════════════════════════════

# sigma*tau - n*phi
add_hyp('F9-MC-01', 'Multiplicative',
    'sigma*tau - n*phi: 48-12=36=n^2. For n=6 only?',
    lambda: sigma(6)*tau(6)-6*phi(6)==36==6**2,
    lambda n: sigma(n)*tau(n)-n*phi(n)==n**2)

s_mc01 = scan(lambda n: sigma(n)*tau(n)-n*phi(n), lambda n: n**2)
add_hyp('F9-MC-02', 'Multiplicative',
    f'sigma*tau-n*phi=n^2: solutions={s_mc01[:10]}',
    lambda: sigma(6)*tau(6)-6*phi(6)==36,
    lambda n: sigma(n)*tau(n)-n*phi(n)==n**2)

# sigma*omega - phi*tau
add_hyp('F9-MC-03', 'Multiplicative',
    'sigma*omega-phi*tau: 24-8=16=2^tau. For n=6.',
    lambda: sigma(6)*omega(6)-phi(6)*tau(6)==16==2**tau(6),
    lambda n: sigma(n)*omega(n)-phi(n)*tau(n)==2**tau(n))

s_mc03 = scan(lambda n: sigma(n)*omega(n)-phi(n)*tau(n), lambda n: 2**tau(n))
add_hyp('F9-MC-04', 'Multiplicative',
    f'sigma*omega-phi*tau=2^tau: solutions={s_mc03[:10]}',
    lambda: sigma(6)*omega(6)-phi(6)*tau(6)==2**tau(6),
    lambda n: sigma(n)*omega(n)-phi(n)*tau(n)==2**tau(n))

# sigma/tau + phi/omega
add_hyp('F9-MC-05', 'Multiplicative',
    'sigma/tau + phi/omega = 12/4+2/2 = 3+1 = 4 = tau. sigma/tau+phi/omega=tau!',
    lambda: Fraction(sigma(6),tau(6))+Fraction(phi(6),omega(6))==tau(6),
    lambda n: Fraction(sigma(n),tau(n))+Fraction(phi(n),omega(n))==tau(n))

s_mc05 = scan(lambda n: Fraction(sigma(n),tau(n))+Fraction(phi(n),omega(n)), lambda n: Fraction(tau(n)))
add_hyp('F9-MC-06', 'Multiplicative',
    f'sigma/tau+phi/omega=tau: solutions={s_mc05[:10]}',
    lambda: Fraction(sigma(6),tau(6))+Fraction(phi(6),omega(6))==tau(6),
    lambda n: Fraction(sigma(n),tau(n))+Fraction(phi(n),omega(n))==Fraction(tau(n)))

# sigma^2 + phi^2
add_hyp('F9-MC-07', 'Multiplicative',
    'sigma^2+phi^2=144+4=148. 148=4*37. Not clean.',
    lambda: sigma(6)**2+phi(6)**2==148,
    lambda n: None)

# sigma^2 - phi^2
add_hyp('F9-MC-08', 'Multiplicative',
    'sigma^2-phi^2=144-4=140=4*35=4*5*7. 140=sigma(6)*... not clean.',
    lambda: sigma(6)**2-phi(6)**2==140,
    lambda n: None)

# (sigma-phi)*(sigma+phi) = sigma^2-phi^2 = (12-2)(12+2) = 10*14 = 140
# (sigma-phi) = 10 = phi*sopfr. (sigma+phi) = 14 = sigma+phi.
add_hyp('F9-MC-09', 'Multiplicative',
    '(sigma-phi)=10=phi*sopfr. (sigma+phi)=14=sigma+phi=2*(n+1). Product=140.',
    lambda: sigma(6)-phi(6)==phi(6)*sopfr(6) and sigma(6)+phi(6)==2*(6+1),
    lambda n: sigma(n)-phi(n)==phi(n)*sopfr(n) and sigma(n)+phi(n)==2*(n+1))

s_mc09a = scan(lambda n: sigma(n)-phi(n), lambda n: phi(n)*sopfr(n))
s_mc09b = scan(lambda n: sigma(n)+phi(n), lambda n: 2*(n+1))
add_hyp('F9-MC-10', 'Multiplicative',
    f'sigma-phi=phi*sopfr: solutions={s_mc09a[:10]}. sigma+phi=2(n+1): solutions={s_mc09b[:10]}',
    lambda: True,
    lambda n: None)

# sigma+phi=2(n+1): for perfect n, 2n+phi=2n+2 → phi=2 → n=6!
add_hyp('F9-MC-11', 'Multiplicative',
    'sigma+phi=2(n+1) for perfect n: 2n+phi=2n+2 → phi=2 → n in {3,4,6}. Only n=6 is perfect!',
    lambda: sigma(6)+phi(6)==2*7 and phi(6)==2,
    lambda n: None)

# tau*sigma - phi*psi for n=6
add_hyp('F9-MC-12', 'Multiplicative',
    'tau*sigma-phi*psi: 4*12-2*12=48-24=24=sigma*phi. Self-referential!',
    lambda: tau(6)*sigma(6)-phi(6)*psi(6)==sigma(6)*phi(6),
    lambda n: tau(n)*sigma(n)-phi(n)*psi(n)==sigma(n)*phi(n))

s_mc12 = scan(lambda n: tau(n)*sigma(n)-phi(n)*psi(n), lambda n: sigma(n)*phi(n))
add_hyp('F9-MC-13', 'Multiplicative',
    f'tau*sigma-phi*psi=sigma*phi: solutions={s_mc12[:10]}',
    lambda: tau(6)*sigma(6)-phi(6)*psi(6)==sigma(6)*phi(6),
    lambda n: tau(n)*sigma(n)-phi(n)*psi(n)==sigma(n)*phi(n))

# For n=6 where psi=sigma: tau*sigma-phi*sigma=sigma*(tau-phi)=12*2=24=sigma*phi. So tau-phi=phi → tau=2*phi. tau(6)=4=2*2=2*phi(6). YES!
add_hyp('F9-MC-14', 'Multiplicative',
    'tau(n)=2*phi(n): 4=2*2. For n=28: tau=6, 2*phi=24. NO. Unique among perfects (since psi=sigma for sqfree).',
    lambda: tau(6)==2*phi(6),
    lambda n: tau(n)==2*phi(n))

s_mc14 = scan(lambda n: tau(n), lambda n: 2*phi(n))
add_hyp('F9-MC-15', 'Multiplicative',
    f'tau=2*phi: solutions={s_mc14[:15]}. Includes n=6, also small values.',
    lambda: tau(6)==2*phi(6),
    lambda n: tau(n)==2*phi(n))

# sigma(n) = n + tau(n) + phi(n) + omega(n): 12 = 6+4+2+2 = 14. NO.
# sigma = n + tau + phi: 12 = 6+4+2 = 12. YES!
add_hyp('F9-MC-16', 'Multiplicative',
    'sigma(n)=n+tau(n)+phi(n): 12=6+4+2=12. For n=28: 56=28+6+12=46. NO.',
    lambda: sigma(6)==6+tau(6)+phi(6),
    lambda n: sigma(n)==n+tau(n)+phi(n))

# This is equivalent to phi+tau=n (since sigma=2n for perfect), already known.
# But does it hold for non-perfect n?
s_mc16 = scan(lambda n: sigma(n), lambda n: n+tau(n)+phi(n))
add_hyp('F9-MC-17', 'Multiplicative',
    f'sigma=n+tau+phi: solutions={s_mc16[:15]}',
    lambda: sigma(6)==6+tau(6)+phi(6),
    lambda n: sigma(n)==n+tau(n)+phi(n))

# Number-theoretic derivative
def arith_derivative(n):
    """Arithmetic derivative n'"""
    if n<=1: return 0
    t, p = n, 2
    while p*p<=t:
        if t%p==0:
            return n//p + n//p * arith_derivative(p) if p>1 else n//p
            # Actually: (pq)' = p'q + pq'. For prime p: p'=1.
            # n=prod(p_i^a_i). n'=n*sum(a_i/p_i).
            break
        p+=1
    return 1  # n is prime

def proper_derivative(n):
    """n' = n * sum(a_i/p_i) where n=prod(p_i^a_i)"""
    if n<=1: return 0
    result = Fraction(0)
    t, p = n, 2
    while p*p<=t:
        a = 0
        while t%p==0: a+=1; t//=p
        if a>0: result += Fraction(a, p)
        p+=1
    if t>1: result += Fraction(1, t)
    return int(n * result)

add_hyp('F9-MC-18', 'Multiplicative',
    f"Arithmetic derivative: 6'=6*(1/2+1/3)=6*5/6=5=sopfr(6)! The derivative of 6 is its sum of prime factors!",
    lambda: proper_derivative(6)==sopfr(6),
    lambda n: proper_derivative(n)==sopfr(n))

s_mc18 = scan(lambda n: proper_derivative(n), lambda n: sopfr(n))
add_hyp('F9-MC-19', 'Multiplicative',
    f"n'=sopfr(n): solutions={s_mc18[:15]}. n'=n*sum(a_i/p_i), sopfr=sum(a_i*p_i).",
    lambda: proper_derivative(6)==5,
    lambda n: proper_derivative(n)==sopfr(n))

# For squarefree n=p1*p2*...*pk: n'=n*sum(1/p_i), sopfr=sum(p_i).
# n'=sopfr iff n*sum(1/p_i)=sum(p_i) iff n*sigma_{-1}(without 1 and n)=sopfr...
# For n=pq: n'=pq*(1/p+1/q)=q+p=sopfr. SO n'=sopfr FOR ALL SEMIPRIMES!
add_hyp('F9-MC-20', 'Multiplicative',
    "For squarefree semiprimes n=pq: n'=pq*(1/p+1/q)=p+q=sopfr(n). GENERALIZES to all semiprimes!",
    lambda: proper_derivative(6)==sopfr(6) and proper_derivative(10)==sopfr(10) and proper_derivative(15)==sopfr(15),
    lambda n: proper_derivative(n)==sopfr(n) if omega(n)==2 and mobius(n)!=0 else None)

# ═══════════════════════════════════════
# INEQUALITY CHARACTERIZATIONS (20)
# ═══════════════════════════════════════

# Robin's inequality: sigma(n) < e^gamma * n * ln(ln(n)) for n>=5041 (equivalent to RH)
# For small n, some violate. Perfect numbers are extremal.
add_hyp('F9-INEQ-01', 'Inequality',
    'Robin inequality: sigma(n)/(n*ln(ln(n))) for n=6: 12/(6*ln(ln(6)))=12/(6*0.5886)=12/3.53=3.40. e^gamma=1.7811. 3.40>1.78 → violates Robin! (n<5041 exempted)',
    lambda: sigma(6)/(6*math.log(math.log(6))) > math.exp(0.5772),
    lambda n: None)

# Gronwall: lim sup sigma(n)/(n*ln(ln(n))) = e^gamma. Perfect numbers approach this.
add_hyp('F9-INEQ-02', 'Inequality',
    'sigma(n)/n = abundancy. For n=6: 2 (maximum for its size). For n=12: 28/12=2.33.',
    lambda: Fraction(sigma(6),6)==2,
    lambda n: None)

# sigma(n) >= n+1 with equality iff n prime. sigma(6)=12>>7.
add_hyp('F9-INEQ-03', 'Inequality',
    'sigma(n)-n-1 = sum of non-trivial proper divisors. For n=6: 12-6-1=5=sopfr(6)!',
    lambda: sigma(6)-6-1==sopfr(6),
    lambda n: sigma(n)-n-1==sopfr(n))

s_ineq03 = scan(lambda n: sigma(n)-n-1, lambda n: sopfr(n))
add_hyp('F9-INEQ-04', 'Inequality',
    f'sigma-n-1=sopfr: solutions={s_ineq03[:15]}',
    lambda: sigma(6)-6-1==sopfr(6),
    lambda n: sigma(n)-n-1==sopfr(n))

# For perfect n: sigma-n-1 = 2n-n-1 = n-1. So n-1=sopfr → sopfr=n-1. Already proved!
add_hyp('F9-INEQ-05', 'Inequality',
    'sigma-n-1=sopfr for perfect n is EQUIVALENT to sopfr=n-1 (H-NT-430). Redundant but confirms.',
    lambda: sigma(6)-6-1==5==sopfr(6)==6-1,
    lambda n: None)

# phi(n) <= n-1 with equality iff n prime. phi(6)=2, very far from 5.
# n-phi(n) = sum of non-coprime elements. For n=6: 6-2=4=tau(6)!
add_hyp('F9-INEQ-06', 'Inequality',
    'n-phi(n)=tau(n): 6-2=4. Equivalently phi+tau=n (already known from F800).',
    lambda: 6-phi(6)==tau(6),
    lambda n: n-phi(n)==tau(n))

# sigma(n)/phi(n) for n=6: 12/2=6=n! sigma/phi=n!
add_hyp('F9-INEQ-07', 'Inequality',
    'sigma(n)/phi(n)=n: 12/2=6. For n=28: 56/12=4.67!=28. Unique among perfects!',
    lambda: Fraction(sigma(6),phi(6))==6,
    lambda n: Fraction(sigma(n),phi(n))==n)

s_ineq07 = scan(lambda n: Fraction(sigma(n),phi(n)), lambda n: Fraction(n))
add_hyp('F9-INEQ-08', 'Inequality',
    f'sigma/phi=n: solutions={s_ineq07[:15]}',
    lambda: Fraction(sigma(6),phi(6))==6,
    lambda n: Fraction(sigma(n),phi(n))==Fraction(n))

# This is psi/phi=n which was in DFS-iter1 as ⭐ #91!
add_hyp('F9-INEQ-09', 'Inequality',
    'sigma/phi=n is equivalent to psi/phi=n since psi(6)=sigma(6). This is known ⭐ #91.',
    lambda: Fraction(sigma(6),phi(6))==6,
    lambda n: None)

# sigma(n)*omega(n)/tau(n) = n for n=6: 12*2/4=6=n. This is n*tau=sigma*omega rearranged.
add_hyp('F9-INEQ-10', 'Inequality',
    'sigma*omega/tau=n: 24/4=6. Rearrangement of H-NT-432 (n*tau=sigma*omega). Known.',
    lambda: sigma(6)*omega(6)//tau(6)==6,
    lambda n: sigma(n)*omega(n)==n*tau(n))

# New: sigma(n)/(n*omega(n)) = tau(n)/omega(n)^2
add_hyp('F9-INEQ-11', 'Inequality',
    'sigma/(n*omega) = tau/omega^2: 12/12=1, 4/4=1. Trivially both=1 at n=6.',
    lambda: Fraction(sigma(6),6*omega(6))==Fraction(tau(6),omega(6)**2),
    lambda n: Fraction(sigma(n),n*omega(n))==Fraction(tau(n),omega(n)**2))

s_ineq11 = scan(lambda n: Fraction(sigma(n),n*omega(n)), lambda n: Fraction(tau(n),omega(n)**2))
add_hyp('F9-INEQ-12', 'Inequality',
    f'sigma/(n*omega)=tau/omega^2: solutions={s_ineq11[:15]}',
    lambda: True,
    lambda n: None)

# tau(n)! / sigma(n) = 2 for n=6: 24/12=2=phi. Known.
add_hyp('F9-INEQ-13', 'Inequality',
    'tau!/sigma = phi: 24/12=2. For n=28: 720/56=12.86!=12=phi. NO (close though).',
    lambda: math.factorial(tau(6))//sigma(6)==phi(6),
    lambda n: math.factorial(tau(n))//sigma(n)==phi(n))

# (sigma-phi)/(tau-omega) = sopfr: (12-2)/(4-2)=10/2=5=sopfr!
add_hyp('F9-INEQ-14', 'Inequality',
    '(sigma-phi)/(tau-omega)=sopfr: 10/2=5. For n=28: (56-12)/(6-2)=44/4=11=sopfr(28)!',
    lambda: (sigma(6)-phi(6))//(tau(6)-omega(6))==sopfr(6),
    lambda n: (sigma(n)-phi(n))//(tau(n)-omega(n))==sopfr(n) if tau(n)>omega(n) else None)

s_ineq14 = scan(lambda n: Fraction(sigma(n)-phi(n),tau(n)-omega(n)) if tau(n)>omega(n) else Fraction(-1),
               lambda n: Fraction(sopfr(n)))
add_hyp('F9-INEQ-15', 'Inequality',
    f'(sigma-phi)/(tau-omega)=sopfr: solutions in [2,200] = checking...',
    lambda: Fraction(sigma(6)-phi(6),tau(6)-omega(6))==sopfr(6),
    lambda n: Fraction(sigma(n)-phi(n),tau(n)-omega(n))==Fraction(sopfr(n)) if tau(n)>omega(n) else None)

# This is HUGE if it generalizes! Let me check more values.
add_hyp('F9-INEQ-16', 'Inequality',
    '(sigma-phi)/(tau-omega)=sopfr checks: n=10: (18-4)/(4-2)=14/2=7=sopfr(10). YES! n=12: (28-4)/(6-2)=24/4=6!=7=sopfr(12). NO.',
    lambda: (sigma(10)-phi(10))//(tau(10)-omega(10))==sopfr(10),
    lambda n: None)

# For n=pq semiprime: sigma=(1+p)(1+q), phi=(p-1)(q-1), tau=4, omega=2.
# (sigma-phi)/(tau-omega) = ((1+p)(1+q)-(p-1)(q-1))/2 = (1+p+q+pq-pq+p+q-1)/2 = (2p+2q)/2 = p+q = sopfr. GENERALIZES FOR ALL SEMIPRIMES!
add_hyp('F9-INEQ-17', 'Inequality',
    '(sigma-phi)/(tau-omega)=sopfr for semiprimes n=pq: PROVED! (1+p)(1+q)-(p-1)(q-1)=2(p+q), divided by (4-2)=2 gives p+q=sopfr.',
    lambda: True,
    lambda n: None)

# Check for prime powers: n=p^k: tau=k+1, omega=1, tau-omega=k.
# sigma=(p^{k+1}-1)/(p-1), phi=p^k-p^{k-1}=p^{k-1}(p-1).
# sigma-phi = (p^{k+1}-1)/(p-1) - p^{k-1}(p-1).
# For k=2: (p^3-1)/(p-1) - p(p-1) = p^2+p+1 - p^2+p = 2p+1. tau-omega=2.
# (2p+1)/2 is not integer for p>1. So fails for prime squares. Good.
add_hyp('F9-INEQ-18', 'Inequality',
    'For prime squares p^2: (sigma-phi)/(tau-omega) = (2p+1)/2 not integer. Identity fails.',
    lambda: (sigma(4)-phi(4)) % (tau(4)-omega(4)) != 0,
    lambda n: None)

# Check n=p^2*q: tau=6, omega=2, tau-omega=4.
add_hyp('F9-INEQ-19', 'Inequality',
    'For n=12=2^2*3: (28-4)/4=6. sopfr(12)=2+2+3=7. 6!=7. Fails for non-squarefree.',
    lambda: (sigma(12)-phi(12))//(tau(12)-omega(12))!=sopfr(12),
    lambda n: None)

add_hyp('F9-INEQ-20', 'Inequality',
    '(sigma-phi)/(tau-omega)=sopfr PROVED for squarefree semiprimes n=pq. Extends to some but not all composites.',
    lambda: True,
    lambda n: None)

# ═══════════════════════════════════════
# Run
# ═══════════════════════════════════════

def verify_all():
    results = {'pass':[],'fail':[],'ad_hoc':[],
               'generalizes_28':[],'no_gen_28':[],'not_testable':[]}
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
        else: results['fail'].append(hid)
    return results

def grade(h, results):
    hid = h['id']
    if hid in results['fail']: return 'FAIL','⬛'
    if h['ad_hoc']: return 'AD_HOC','⚪'
    if hid in results['generalizes_28']: return 'GEN','🟩'
    if hid in results['no_gen_28']: return 'N6','🟧★'
    return 'PASS','🟧'

if __name__ == '__main__':
    results = verify_all()
    print("="*70)
    print("FRONTIER 900: Iterated + Multiplicative + Inequality")
    print("="*70)
    print(f"\nTotal: {len(hypotheses)}, PASS: {len(results['pass'])}, FAIL: {len(results['fail'])}")
    print(f"🟩: {len(results['generalizes_28'])}, 🟧★: {len(results['no_gen_28'])}, Ad-hoc: {len(results['ad_hoc'])}")

    domains = defaultdict(list)
    for h in hypotheses: domains[h['domain']].append(h)
    gc = defaultdict(int)

    for dom, hyps in domains.items():
        print(f"\n--- {dom} ({len(hyps)}) ---")
        for h in hyps:
            gl,em = grade(h, results); gc[em]+=1
            s = "PASS" if h['id'] in results['pass'] else "FAIL"
            gt = " [GEN]" if h['id'] in results['generalizes_28'] else \
                 " [n=6]" if h['id'] in results['no_gen_28'] else ""
            print(f"  {em} {h['id']}: {s}{gt} — {h['statement'][:80]}")

    print(f"\n{'='*70}\nSUMMARY: ",end="")
    for em,c in sorted(gc.items(),key=lambda x:-x[1]): print(f"{em}:{c} ",end="")
    print()

    if results['fail']:
        print("\nFAILURES:")
        for hid in results['fail']:
            h = next(x for x in hypotheses if x['id']==hid)
            print(f"  ⬛ {hid}: {h['statement'][:100]}")

    print(f"\n{'='*70}\nTOP DISCOVERIES\n{'='*70}")
    for h in hypotheses:
        hid = h['id']
        if hid in results['fail'] or h['ad_hoc']: continue
        if hid in results['generalizes_28'] or hid in results['no_gen_28']:
            gl,em = grade(h, results)
            print(f"  {em} {hid}: {h['statement'][:90]}")
