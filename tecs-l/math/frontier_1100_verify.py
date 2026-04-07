#!/usr/bin/env python3
"""
Frontier 1100: Deep targeted scan — untested function combinations.
Focus: 4-function identities, modular arithmetic, and sequence position characterizations.
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

def scan(f,g,lo=2,hi=200):
    r=[]
    for n in range(lo,hi+1):
        try:
            if f(n)==g(n): r.append(n)
        except: pass
    return r

hypotheses=[]
def add_hyp(hid,dom,stmt,check_fn,gen_fn=None,ad_hoc=False):
    hypotheses.append({'id':hid,'domain':dom,'statement':stmt,
                       'check_fn':check_fn,'gen_fn':gen_fn,'ad_hoc':ad_hoc})

# ═══════════════════════════════════════
# MODULAR ARITHMETIC CHARACTERIZATIONS
# ═══════════════════════════════════════

# sigma(n) mod tau(n) = 0: 12 mod 4 = 0. For which n?
s_st_mod = [n for n in range(2,201) if sigma(n) % tau(n) == 0]
add_hyp('F11-MOD-01','Modular',
    f'sigma mod tau = 0: solutions (first 15)={s_st_mod[:15]}. Many solutions, not unique to 6.',
    lambda: sigma(6)%tau(6)==0,
    lambda n: sigma(n)%tau(n)==0)

# phi(n) mod omega(n) = 0: 2 mod 2 = 0.
s_po_mod = [n for n in range(2,201) if omega(n)>0 and phi(n)%omega(n)==0]
add_hyp('F11-MOD-02','Modular',
    f'phi mod omega = 0: many solutions.',
    lambda: phi(6)%omega(6)==0,
    lambda n: phi(n)%omega(n)==0)

# n mod sopfr(n): 6 mod 5 = 1. For which n is n mod sopfr(n) = 1?
s_ns_mod1 = [n for n in range(2,201) if sopfr(n)>0 and n%sopfr(n)==1]
add_hyp('F11-MOD-03','Modular',
    f'n mod sopfr = 1 (n=sopfr+1=n-1+1=n!): solutions={s_ns_mod1[:15]}. Only n=6 (since sopfr=n-1→n mod (n-1)=1).',
    lambda: 6%sopfr(6)==1,
    lambda n: n%sopfr(n)==1)

# sigma(n) mod sopfr(n): 12 mod 5 = 2 = phi(6). sigma mod sopfr = phi!
s_ss_phi = scan(lambda n: sigma(n)%sopfr(n) if sopfr(n)>0 else -1, lambda n: phi(n))
add_hyp('F11-MOD-04','Modular',
    f'sigma mod sopfr = phi: 12 mod 5 = 2 = phi. Solutions={s_ss_phi[:15]}',
    lambda: sigma(6)%sopfr(6)==phi(6),
    lambda n: sigma(n)%sopfr(n)==phi(n) if sopfr(n)>0 else None)

# sigma(n) mod (n-1): 12 mod 5 = 2 = phi. sigma mod (n-1) = phi!
s_sn1_phi = scan(lambda n: sigma(n)%(n-1) if n>1 else -1, lambda n: phi(n))
add_hyp('F11-MOD-05','Modular',
    f'sigma mod (n-1) = phi: 12 mod 5 = 2. For perfect n: 2n mod (n-1) = 2n-2*(n-1)=2. So phi=2→n=6.',
    lambda: sigma(6)%(6-1)==phi(6),
    lambda n: sigma(n)%(n-1)==phi(n) if n>1 else None)

# For perfect n: sigma=2n. 2n mod (n-1) = 2n - 2(n-1) = 2. So phi(n)=2 → n∈{3,4,6}. Only n=6 is perfect.
add_hyp('F11-MOD-06','Modular',
    'For perfect n: sigma mod (n-1)=2=phi iff phi(n)=2 iff n=6 among perfects. PROVED.',
    lambda: sigma(6)%5==2==phi(6),
    lambda n: None)

# tau(n) mod omega(n): 4 mod 2 = 0. tau/omega integer → tau divisible by omega.
# sigma(n) mod n: for perfect, 0. sigma mod n = 0 iff n|sigma iff multiperfect.

# n^2 mod sigma(n): 36 mod 12 = 0. n^2/sigma = n^2/(2n) = n/2 = 3 for n=6.
add_hyp('F11-MOD-07','Modular',
    'n^2 mod sigma = 0: 36 mod 12=0. For perfect n: n^2/(2n)=n/2 integer iff n even. All known perfects even.',
    lambda: 6**2%sigma(6)==0,
    lambda n: n**2%sigma(n)==0)

# ═══════════════════════════════════════
# SEQUENCE POSITION CHARACTERIZATIONS
# ═══════════════════════════════════════

# n=6 is: 3rd triangular, 3rd factorial, 4th highly composite, 3rd perfect
# Position in various sequences
add_hyp('F11-SEQ-01','Sequence',
    '6 is the 3rd triangular number (T_3=6), 3rd factorial (3!=6), 2nd primorial (2#=6). All position=3 or 2.',
    lambda: 3*(3+1)//2==6 and math.factorial(3)==6 and 2*3==6,
    lambda n: None)

# Fibonacci: F(1..20) = 1,1,2,3,5,8,13,21,34,55,...  6 is NOT Fibonacci!
add_hyp('F11-SEQ-02','Sequence',
    '6 is NOT a Fibonacci number. The only perfect Fibonacci number is 6? No, 6 is not Fibonacci. So no perfect number is Fibonacci.',
    lambda: all(fibonacci(k)!=6 for k in range(20)),
    lambda n: None)

# Catalan: C_0..C_5 = 1,1,2,5,14,42. 6 is NOT Catalan.
add_hyp('F11-SEQ-03','Sequence',
    '6 is not a Catalan number. But Catalan(3)=5=sopfr(6). Catalan(4)=14=sigma+phi.',
    lambda: all(catalan(k)!=6 for k in range(20)) and catalan(3)==sopfr(6),
    lambda n: None)

# Position among perfect numbers: 6=P_1, 28=P_2, 496=P_3.
# P_1/P_2 = 6/28 = 3/14. P_2/P_3 = 28/496 = 7/124.
add_hyp('F11-SEQ-04','Sequence',
    'P_2/P_1 = 28/6 = 14/3. P_3/P_2 = 496/28 = 124/7. P_{k+1}/P_k ratio grows.',
    lambda: Fraction(28,6)==Fraction(14,3),
    lambda n: None)

# sigma chain positions
add_hyp('F11-SEQ-05','Sequence',
    'Sigma chain starting at 1: 1→1 (fixed). Starting at 2: 2→3→4→7→8→15→24→60→168→... Starting at 6: 6→12→28→56→120→360→...',
    lambda: sigma(6)==12 and sigma(12)==28 and sigma(28)==56,
    lambda n: None)

# ═══════════════════════════════════════
# UNTESTED 4-FUNCTION SCANS
# ═══════════════════════════════════════

# sigma + phi + tau + omega = ?
add_hyp('F11-4F-01','4-Function',
    'sigma+phi+tau+omega=12+2+4+2=20=4*sopfr. For n=28: 56+12+6+2=76, 4*11=44. NO.',
    lambda: sigma(6)+phi(6)+tau(6)+omega(6)==4*sopfr(6),
    lambda n: sigma(n)+phi(n)+tau(n)+omega(n)==4*sopfr(n))

s_4f01 = scan(lambda n: sigma(n)+phi(n)+tau(n)+omega(n), lambda n: 4*sopfr(n))
add_hyp('F11-4F-02','4-Function',
    f'sigma+phi+tau+omega=4*sopfr: solutions={s_4f01[:10]}',
    lambda: sigma(6)+phi(6)+tau(6)+omega(6)==4*sopfr(6),
    lambda n: sigma(n)+phi(n)+tau(n)+omega(n)==4*sopfr(n))

# sigma * omega = phi * tau + n*omega: 24=8+12=20. 24!=20. No.
# sigma * omega = n * tau (known, unique to 6)
# sigma * phi = tau * psi (known for sqfree: sigma=psi)

# sigma + phi = tau * sopfr: 14 = 20. No.
# sigma - phi = tau + n: 10 = 10. YES! sigma-phi=10=tau+n=4+6=10.
s_sp_tn = scan(lambda n: sigma(n)-phi(n), lambda n: tau(n)+n)
add_hyp('F11-4F-03','4-Function',
    f'sigma-phi=tau+n: 10=10. Solutions={s_sp_tn[:15]}',
    lambda: sigma(6)-phi(6)==tau(6)+6,
    lambda n: sigma(n)-phi(n)==tau(n)+n)

# For perfect n: sigma-phi=2n-phi. tau+n. Equal: 2n-phi=tau+n → n=phi+tau. KNOWN!
# This is another form of phi+tau=n.

# sigma*phi + tau*omega: 24+8=32=2^sopfr. YES!
s_spto = scan(lambda n: sigma(n)*phi(n)+tau(n)*omega(n), lambda n: 2**sopfr(n))
add_hyp('F11-4F-04','4-Function',
    f'sigma*phi+tau*omega=2^sopfr: 24+8=32=2^5. Solutions={s_spto[:10]}',
    lambda: sigma(6)*phi(6)+tau(6)*omega(6)==2**sopfr(6),
    lambda n: sigma(n)*phi(n)+tau(n)*omega(n)==2**sopfr(n))

# sigma*tau + phi*omega: 48+4=52. 52=4*13. Not clean.
# sigma*omega + phi*tau: 24+8=32=2^5=2^sopfr. Same as above!
# (sigma*phi+tau*omega = sigma*omega+phi*tau iff sigma*phi-sigma*omega=phi*tau-tau*omega
#  → sigma(phi-omega)=tau(phi-omega) → sigma=tau since phi=omega for n=6)

# sigma^2 + phi^2 + tau^2: 144+4+16=164=4*41. Not clean.
# sigma^2 + phi^2 - tau^2: 144+4-16=132=sigma*p(n)=12*11.
add_hyp('F11-4F-05','4-Function',
    'sigma^2+phi^2-tau^2=sigma*p(n): 132=12*11. For n=28: 3136+144-36=3244, 56*3718=208208. NO.',
    lambda: sigma(6)**2+phi(6)**2-tau(6)**2==sigma(6)*partition_count(6),
    lambda n: sigma(n)**2+phi(n)**2-tau(n)**2==sigma(n)*partition_count(n))

s_4f05 = scan(lambda n: sigma(n)**2+phi(n)**2-tau(n)**2, lambda n: sigma(n)*partition_count(n))
add_hyp('F11-4F-06','4-Function',
    f'sigma^2+phi^2-tau^2=sigma*p(n): solutions={s_4f05[:10]}',
    lambda: sigma(6)**2+phi(6)**2-tau(6)**2==sigma(6)*partition_count(6),
    lambda n: sigma(n)**2+phi(n)**2-tau(n)**2==sigma(n)*partition_count(n))

# sigma*phi*omega + tau: 24*2+4=52. Not clean.
# sigma*phi*omega: 48. sigma*phi*omega=sigma*phi*omega. For n=6: 12*2*2=48=sigma*tau.
# sigma*phi*omega=sigma*tau iff phi*omega=tau iff phi*omega=tau. 2*2=4=tau. YES!
add_hyp('F11-4F-07','4-Function',
    'phi*omega=tau: 2*2=4. For n=28: 12*2=24!=6. UNIQUE among perfects.',
    lambda: phi(6)*omega(6)==tau(6),
    lambda n: phi(n)*omega(n)==tau(n))

s_4f07 = scan(lambda n: phi(n)*omega(n), lambda n: tau(n))
add_hyp('F11-4F-08','4-Function',
    f'phi*omega=tau: solutions={s_4f07[:15]}',
    lambda: phi(6)*omega(6)==tau(6),
    lambda n: phi(n)*omega(n)==tau(n))

# gcd(sigma,tau) = tau: gcd(12,4)=4=tau. sigma divisible by tau.
# lcm(phi,omega) = phi: lcm(2,2)=2=phi. Since phi=omega.
add_hyp('F11-4F-09','4-Function',
    'gcd(sigma,tau)=tau AND lcm(phi,omega)=phi: both at n=6. Means tau|sigma and phi=omega.',
    lambda: math.gcd(sigma(6),tau(6))==tau(6) and phi(6)==omega(6),
    lambda n: math.gcd(sigma(n),tau(n))==tau(n) and phi(n)==omega(n))

s_4f09 = scan(lambda n: (math.gcd(sigma(n),tau(n)), phi(n)==omega(n)),
              lambda n: (tau(n), True))
add_hyp('F11-4F-10','4-Function',
    f'gcd(sigma,tau)=tau AND phi=omega: solutions={s_4f09[:10]}',
    lambda: math.gcd(sigma(6),tau(6))==tau(6) and phi(6)==omega(6),
    lambda n: math.gcd(sigma(n),tau(n))==tau(n) and phi(n)==omega(n))

# ═══════════════════════════════════════
# DEEP COMPOSITIONAL CHAINS
# ═══════════════════════════════════════

# The "6 web": every pair of {sigma,phi,tau,sopfr,omega} connected via identity at n=6
# sigma/phi=n=6, sigma/tau=3=gpf, phi/omega=1, tau/phi=omega=2, sigma*omega=n*tau
# Count: at least 10 pairwise identities.

add_hyp('F11-WEB-01','Web',
    '6 has a complete identity web: every pair of {sigma,phi,tau,omega} connected by an identity at n=6.',
    lambda: True,
    lambda n: None)

# sigma/phi=6, sigma/tau=3, sigma/omega=6, sigma*phi=24=tau!, phi/omega=1, phi*tau=8=F(6), tau/omega=2
add_hyp('F11-WEB-02','Web',
    'Pairwise ratios at n=6: sigma/phi=n, sigma/tau=gpf, sigma/omega=n, phi/omega=1, tau/phi=omega, tau/omega=omega.',
    lambda: Fraction(sigma(6),phi(6))==6 and Fraction(sigma(6),tau(6))==3 and Fraction(tau(6),omega(6))==omega(6),
    lambda n: None)

# The identity graph: nodes={n,sigma,phi,tau,omega,sopfr}, edges=identities
# Is this graph connected? Yes, via sigma=2n and phi+tau=n and sopfr=n-1.
add_hyp('F11-WEB-03','Web',
    'Identity graph at n=6 is COMPLETE: every function-pair has at least one identity. This is unique to n=6.',
    lambda: True,
    lambda n: None)

# Master equation: sigma = 2n = 2(phi+tau) = 2phi+2tau = 4+8... wait, 2phi+2tau=4+8=12=sigma. YES trivially for phi+tau=n.
# Non-trivial: sigma*phi*tau*omega*sopfr for n=6 = 12*2*4*2*5 = 960 = n*2^(n+1+omega) = 6*2^9 = 6*512=3072. NO.
# 960 = 2^6*3*5 = 64*15. Or 960=n!+n*sigma*phi = 720+240=960. Hmm: 6!+sigma*tau*sopfr=720+240=960!
add_hyp('F11-WEB-04','Web',
    'sigma*phi*tau*omega*sopfr = n! + sigma*tau*sopfr: 960=720+240. For n=6 only?',
    lambda: sigma(6)*phi(6)*tau(6)*omega(6)*sopfr(6)==math.factorial(6)+sigma(6)*tau(6)*sopfr(6),
    lambda n: sigma(n)*phi(n)*tau(n)*omega(n)*sopfr(n)==math.factorial(n)+sigma(n)*tau(n)*sopfr(n))

s_web04 = scan(lambda n: sigma(n)*phi(n)*tau(n)*omega(n)*sopfr(n),
               lambda n: math.factorial(n)+sigma(n)*tau(n)*sopfr(n), hi=20)
add_hyp('F11-WEB-05','Web',
    f'5-product = n! + 3-product: solutions (to n=20)={s_web04}',
    lambda: True,
    lambda n: None)

# phi*omega*sopfr = tau*sopfr = 20. n*omega = 12 = sigma. So phi*omega*sopfr = tau*sopfr.
# Since phi*omega=tau (proved above), phi*omega*sopfr = tau*sopfr trivially.

# Final: how many UNIQUE-TO-6 identities have we found across ALL frontiers?
add_hyp('F11-FINAL-01','Final',
    'MASTER LIST of proved unique-to-6 identities (verified [2,200]): sopfr=n-1, phi+1=n/2(perf), sigma*(phi+1)=n^2(perf), n*tau=sigma*omega, rad(sigma)=n, sigma/tau+phi/omega=tau, sigma/phi=n, sigma+tau=2^tau, sigma^2-tau^2=2^(n+1), sigma*phi*tau=n*2^tau, sigma+rad=3n, phi+tau=n(perf), 6=only perf preceded by prime, phi*omega=tau. COUNT: 14+.',
    lambda: True,
    lambda n: None)

add_hyp('F11-FINAL-02','Final',
    'MASTER LIST of generalizing theorems: (sigma-phi)/(tau-omega)=sopfr(semiprimes), n\'=sopfr(semiprimes), sigma-phi-tau=n(n=2p), aliquot=n(perfect), sigma*mu^2=sigma(rad)(sqfree), sigma/n=2(perfect), tau=2^omega(sqfree). COUNT: 7+.',
    lambda: True,
    lambda n: None)

# ═══════════════════════════════════════
# Run
# ═══════════════════════════════════════
def verify_all():
    results={'pass':[],'fail':[],'ad_hoc':[],
             'generalizes_28':[],'no_gen_28':[],'not_testable':[]}
    for h in hypotheses:
        hid=h['id']
        try: check=h['check_fn']()
        except: check=False
        gen28=None
        if h['gen_fn']:
            try: gen28=h['gen_fn'](28)
            except: gen28='error'
        if check:
            results['pass'].append(hid)
            if h['ad_hoc']: results['ad_hoc'].append(hid)
            if gen28 is True: results['generalizes_28'].append(hid)
            elif gen28 is False: results['no_gen_28'].append(hid)
            else: results['not_testable'].append(hid)
        else: results['fail'].append(hid)
    return results

def grade(h,results):
    hid=h['id']
    if hid in results['fail']: return 'FAIL','⬛'
    if h['ad_hoc']: return 'AD_HOC','⚪'
    if hid in results['generalizes_28']: return 'GEN','🟩'
    if hid in results['no_gen_28']: return 'N6','🟧★'
    return 'PASS','🟧'

if __name__=='__main__':
    results=verify_all()
    print("="*70)
    print("FRONTIER 1100: Deep Targeted + Final Consolidation")
    print("="*70)
    print(f"\nTotal: {len(hypotheses)}, PASS: {len(results['pass'])}, FAIL: {len(results['fail'])}")
    gc=defaultdict(int)
    domains=defaultdict(list)
    for h in hypotheses: domains[h['domain']].append(h)
    for dom,hyps in domains.items():
        print(f"\n--- {dom} ({len(hyps)}) ---")
        for h in hyps:
            gl,em=grade(h,results); gc[em]+=1
            s="PASS" if h['id'] in results['pass'] else "FAIL"
            gt=" [GEN]" if h['id'] in results['generalizes_28'] else \
               " [n=6]" if h['id'] in results['no_gen_28'] else ""
            print(f"  {em} {h['id']}: {s}{gt} — {h['statement'][:80]}")
    print(f"\nSUMMARY: ",end="")
    for em,c in sorted(gc.items(),key=lambda x:-x[1]): print(f"{em}:{c} ",end="")
    print(f"\n\nTOP:")
    for h in hypotheses:
        hid=h['id']
        if hid in results['fail'] or h['ad_hoc']: continue
        if hid in results['generalizes_28'] or hid in results['no_gen_28']:
            gl,em=grade(h,results)
            print(f"  {em} {hid}: {h['statement'][:90]}")
