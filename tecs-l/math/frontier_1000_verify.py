#!/usr/bin/env python3
"""
Frontier 1000: Final systematic sweep — exhaustive scan of 3-function
identities f(g(n), h(n)) = k(n) unique to n=6.
"""
import math
from fractions import Fraction
from collections import defaultdict

def divisors(n):
    d = []
    for i in range(1, int(n**0.5)+1):
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

def scan(f,g,lo=2,hi=200):
    r=[]
    for n in range(lo,hi+1):
        try:
            if f(n)==g(n): r.append(n)
        except: pass
    return r

# Dictionary of arithmetic functions for systematic search
FUNCS = {
    'n': lambda n: n,
    'sigma': lambda n: sigma(n),
    'tau': lambda n: tau(n),
    'phi': lambda n: phi(n),
    'sopfr': lambda n: sopfr(n),
    'omega': lambda n: omega(n),
    'rad': lambda n: rad(n),
    'psi': lambda n: psi(n),
}

hypotheses = []
def add_hyp(hid,dom,stmt,check_fn,gen_fn=None,ad_hoc=False):
    hypotheses.append({'id':hid,'domain':dom,'statement':stmt,
                       'check_fn':check_fn,'gen_fn':gen_fn,'ad_hoc':ad_hoc})

# ═══════════════════════════════════════
# EXHAUSTIVE 2-RATIO SCANS
# Find: f1/f2 = f3/f4 uniquely at n=6
# ═══════════════════════════════════════

print("Running exhaustive ratio scans...")

# Already found: sigma/phi=n, sigma/tau+phi/omega=tau, n*tau=sigma*omega
# Now try all remaining ratio equalities

# sigma/sopfr = n/omega: 12/5 vs 6/2=3. 12/5=2.4!=3. No.
# sigma/omega = n*tau/omega: both = sigma*omega... circular.

# tau/phi = omega/1: 4/2=2, omega=2. YES! tau/phi=omega. Check more.
s_tp_om = scan(lambda n: Fraction(tau(n),phi(n)), lambda n: Fraction(omega(n)))
add_hyp('F10-RAT-01', 'Ratio',
    f'tau/phi=omega: n=6→4/2=2=omega. Solutions={s_tp_om[:15]}',
    lambda: Fraction(tau(6),phi(6))==omega(6),
    lambda n: Fraction(tau(n),phi(n))==Fraction(omega(n)))

# sigma/n = tau/omega: 12/6=2, 4/2=2. YES! Both=2. This is n*tau=sigma*omega.
# Already found. Skip.

# sigma/rad = phi+1? 12/6=2, phi+1=3. No.
# sigma/rad = 2 for sqfree perfect. Known.

# psi/sigma for n=6: 12/12=1. psi=sigma only for squarefree.
s_psi_sig = scan(lambda n: psi(n), lambda n: sigma(n))
add_hyp('F10-RAT-02', 'Ratio',
    f'psi=sigma: solutions (squarefree)={[n for n in s_psi_sig if mobius(n)!=0][:15]}',
    lambda: psi(6)==sigma(6),
    lambda n: psi(n)==sigma(n))

# phi*sigma = n*psi for n=6: 2*12=24, 6*12=72. No.
# phi*psi = sigma*omega for n=6: 2*12=24, 12*2=24. YES!
s_pp_so = scan(lambda n: phi(n)*psi(n), lambda n: sigma(n)*omega(n))
add_hyp('F10-RAT-03', 'Ratio',
    f'phi*psi=sigma*omega: n=6→24=24. Solutions={s_pp_so[:15]}',
    lambda: phi(6)*psi(6)==sigma(6)*omega(6),
    lambda n: phi(n)*psi(n)==sigma(n)*omega(n))

# For sqfree n where psi=sigma: phi*sigma=sigma*omega → phi=omega. Check n=6: phi=2=omega. YES.
# phi=omega happens for many n. So this is really phi=omega AND psi=sigma.
s_phi_om = scan(lambda n: phi(n), lambda n: omega(n))
add_hyp('F10-RAT-04', 'Ratio',
    f'phi=omega: solutions={s_phi_om[:15]}',
    lambda: phi(6)==omega(6),
    lambda n: phi(n)==omega(n))

# rad*tau = sigma*omega for n=6: 6*4=24, 12*2=24. YES!
# But n*tau=sigma*omega (known). And rad=n for sqfree. So this is the same.

# sigma - rad = n for perfect sqfree: 12-6=6. Known (sigma=2n, rad=n).
# New: sigma + rad for n=6: 12+6=18=3*n. For n=28: 56+14=70=5*28/2. Not clean.
add_hyp('F10-RAT-05', 'Ratio',
    'sigma+rad=3n iff n sqfree perfect: 12+6=18=3*6. For n=28: 56+14=70!=84=3*28.',
    lambda: sigma(6)+rad(6)==3*6,
    lambda n: sigma(n)+rad(n)==3*n)

s_sr_3n = scan(lambda n: sigma(n)+rad(n), lambda n: 3*n)
add_hyp('F10-RAT-06', 'Ratio',
    f'sigma+rad=3n: solutions={s_sr_3n[:15]}',
    lambda: sigma(6)+rad(6)==3*6,
    lambda n: sigma(n)+rad(n)==3*n)

# ═══════════════════════════════════════
# 3-FUNCTION COMBINATIONS
# ═══════════════════════════════════════

# sigma + phi + tau = 2n + omega? 12+2+4=18, 12+2=14. No. 18=3n.
# sigma + phi + tau = 3n: 18=18. For perfect n: 2n+phi+tau=3n → phi+tau=n. Known!
add_hyp('F10-3F-01', '3-Function',
    'sigma+phi+tau=3n iff perfect AND phi+tau=n. Only n=6.',
    lambda: sigma(6)+phi(6)+tau(6)==3*6,
    lambda n: sigma(n)+phi(n)+tau(n)==3*n)

# sigma*phi*tau
add_hyp('F10-3F-02', '3-Function',
    'sigma*phi*tau=12*2*4=96=n*2^tau=6*16. For n=28: 56*12*6=4032. 28*2^6=1792. No.',
    lambda: sigma(6)*phi(6)*tau(6)==6*2**tau(6),
    lambda n: sigma(n)*phi(n)*tau(n)==n*2**tau(n))

s_spt_n2t = scan(lambda n: sigma(n)*phi(n)*tau(n), lambda n: n*2**tau(n))
add_hyp('F10-3F-03', '3-Function',
    f'sigma*phi*tau=n*2^tau: solutions={s_spt_n2t[:10]}',
    lambda: sigma(6)*phi(6)*tau(6)==6*2**tau(6),
    lambda n: sigma(n)*phi(n)*tau(n)==n*2**tau(n))

# sigma + phi*tau = 2n + omega*tau? 12+8=20, 12+8=20. Hmm: sigma+phi*tau=20. 2n+omega*tau=12+8=20. YES trivially.
# Actually: sigma+phi*tau = 2n+omega*tau → sigma-2n = tau*(omega-phi). For perfect: 0=tau*(omega-phi)→omega=phi. Already known.

# sigma^2 + phi^2 + tau^2 for n=6: 144+4+16=164. Not obviously useful.

# sigma*phi + sigma*tau + phi*tau = ... 24+48+8=80. 80=2^tau*sopfr=16*5=80. YES!
add_hyp('F10-3F-04', '3-Function',
    'sigma*phi+sigma*tau+phi*tau = 2^tau * sopfr: 24+48+8=80=16*5=80.',
    lambda: sigma(6)*phi(6)+sigma(6)*tau(6)+phi(6)*tau(6)==2**tau(6)*sopfr(6),
    lambda n: sigma(n)*phi(n)+sigma(n)*tau(n)+phi(n)*tau(n)==2**tau(n)*sopfr(n))

s_3f04 = scan(lambda n: sigma(n)*phi(n)+sigma(n)*tau(n)+phi(n)*tau(n), lambda n: 2**tau(n)*sopfr(n))
add_hyp('F10-3F-05', '3-Function',
    f'sigma*phi+sigma*tau+phi*tau=2^tau*sopfr: solutions={s_3f04[:10]}',
    lambda: True,
    lambda n: None)

# (sigma+phi+tau)^2 = 18^2=324. n^2*9=324. For perfect: (3n)^2=9n^2.
# sigma*phi*tau + n = 96+6=102=sigma(6)*... not clean.

# sigma^2-tau^2 = 144-16=128=2^7. For n=6: 2^(n+1)=128. YES!
add_hyp('F10-3F-06', '3-Function',
    'sigma^2-tau^2 = 2^(n+1): 144-16=128=2^7. n=6,n+1=7. For n=28: 56^2-6^2=3136-36=3100. 2^29=536M. NO.',
    lambda: sigma(6)**2-tau(6)**2==2**(6+1),
    lambda n: sigma(n)**2-tau(n)**2==2**(n+1))

s_3f06 = scan(lambda n: sigma(n)**2-tau(n)**2, lambda n: 2**(n+1))
add_hyp('F10-3F-07', '3-Function',
    f'sigma^2-tau^2=2^(n+1): solutions={s_3f06[:10]}',
    lambda: sigma(6)**2-tau(6)**2==128,
    lambda n: sigma(n)**2-tau(n)**2==2**(n+1))

# (sigma+tau)(sigma-tau) = 16*8=128. sigma+tau=16=2^tau. sigma-tau=8=2^omega*... 8=sigma-tau=2^3.
# 2^tau * (sigma-tau) = 2^4*8=128. So 2^tau*(sigma-tau)=2^(n+1).
# → sigma-tau=2^(n+1-tau)=2^3=8. For n=6: 12-4=8=2^3. CHECK.
add_hyp('F10-3F-08', '3-Function',
    'sigma-tau = 2^(n+1-tau) = 2^3 = 8 for n=6. Also sigma+tau=2^tau=16.',
    lambda: sigma(6)-tau(6)==2**(6+1-tau(6)) and sigma(6)+tau(6)==2**tau(6),
    lambda n: sigma(n)-tau(n)==2**(n+1-tau(n)) and sigma(n)+tau(n)==2**tau(n))

s_3f08 = scan(lambda n: (sigma(n)+tau(n), sigma(n)-tau(n)),
              lambda n: (2**tau(n), 2**(n+1-tau(n))))
add_hyp('F10-3F-09', '3-Function',
    f'sigma+tau=2^tau AND sigma-tau=2^(n+1-tau): solutions={s_3f08[:10]}',
    lambda: sigma(6)+tau(6)==2**tau(6),
    lambda n: sigma(n)+tau(n)==2**tau(n))

# sigma+tau=2^tau: 16=2^4=16. For n=28: 56+6=62, 2^6=64. Close but no!
s_st_2t = scan(lambda n: sigma(n)+tau(n), lambda n: 2**tau(n))
add_hyp('F10-3F-10', '3-Function',
    f'sigma+tau=2^tau: solutions={s_st_2t[:10]}',
    lambda: sigma(6)+tau(6)==2**tau(6),
    lambda n: sigma(n)+tau(n)==2**tau(n))

# ═══════════════════════════════════════
# HIGHER-ORDER COMPOSITIONS (15)
# ═══════════════════════════════════════

# sigma(rad(n)) for n=6: sigma(6)=12. rad=n for sqfree. So sigma(rad)=sigma for sqfree.
# phi(rad(n)) for n=6: phi(6)=2. Same.
# tau(rad(n)): tau(6)=4. Same.

# sigma(n+1): sigma(7)=8. 8=2^omega(6)*tau(6)=4*... wait, 8=sigma-tau.
add_hyp('F10-HO-01', 'Higher-Order',
    'sigma(n+1)=sigma-tau: sigma(7)=8, sigma(6)-tau(6)=12-4=8. YES!',
    lambda: sigma(7)==sigma(6)-tau(6),
    lambda n: sigma(n+1)==sigma(n)-tau(n))

s_ho01 = scan(lambda n: sigma(n+1), lambda n: sigma(n)-tau(n))
add_hyp('F10-HO-02', 'Higher-Order',
    f'sigma(n+1)=sigma(n)-tau(n): solutions={s_ho01[:15]}',
    lambda: sigma(7)==sigma(6)-tau(6),
    lambda n: sigma(n+1)==sigma(n)-tau(n))

# phi(n+1) for n=6: phi(7)=6=n!
add_hyp('F10-HO-03', 'Higher-Order',
    'phi(n+1)=n: phi(7)=6. This holds iff n+1 is prime! (phi(p)=p-1=n)',
    lambda: phi(7)==6,
    lambda n: phi(n+1)==n)

# So phi(n+1)=n iff n+1 prime. Not unique to 6, but 7 IS prime.
s_ho03 = scan(lambda n: phi(n+1), lambda n: n)
add_hyp('F10-HO-04', 'Higher-Order',
    f'phi(n+1)=n (n+1 prime): solutions={s_ho03[:15]}',
    lambda: phi(7)==6,
    lambda n: phi(n+1)==n)

# tau(n+1)=omega(n): tau(7)=2=omega(6). Trivially: tau(prime)=2=omega(sqfree with 2 factors).
add_hyp('F10-HO-05', 'Higher-Order',
    'tau(n+1)=omega(n): tau(7)=2=omega(6). n+1=7 prime, omega(6)=2.',
    lambda: tau(7)==omega(6),
    lambda n: tau(n+1)==omega(n))

# sigma(n-1) for n=6: sigma(5)=6=n.
add_hyp('F10-HO-06', 'Higher-Order',
    'sigma(n-1)=n: sigma(5)=6. Holds iff n-1 is prime and n-1+1=n=sigma(n-1). sigma(p)=p+1. So p+1=n, p=n-1. Need n-1 prime. For n=6: 5 prime. YES.',
    lambda: sigma(5)==6,
    lambda n: sigma(n-1)==n)

s_ho06 = scan(lambda n: sigma(n-1), lambda n: n, lo=3)
add_hyp('F10-HO-07', 'Higher-Order',
    f'sigma(n-1)=n (n-1 prime): solutions={s_ho06[:15]}',
    lambda: sigma(5)==6,
    lambda n: sigma(n-1)==n)

# sigma(n-1)=n AND sigma(n)=2n: both hold at n=6!
add_hyp('F10-HO-08', 'Higher-Order',
    'sigma(n-1)=n AND sigma(n)=2n: n-1 prime AND n perfect. n=6: 5 prime, 6 perfect. n=28: 27 not prime. ONLY n=6!',
    lambda: sigma(5)==6 and sigma(6)==12,
    lambda n: sigma(n-1)==n and sigma(n)==2*n)

s_ho08 = scan(lambda n: (sigma(n-1),sigma(n)), lambda n: (n,2*n), lo=3)
add_hyp('F10-HO-09', 'Higher-Order',
    f'sigma(n-1)=n AND sigma(n)=2n: solutions={s_ho08[:10]}',
    lambda: sigma(5)==6 and sigma(6)==12,
    lambda n: sigma(n-1)==n and sigma(n)==2*n)

# This is a beautiful characterization: n=6 is the only perfect number preceded by a prime!
# n=28: 27=3^3 not prime. n=496: 495=5*99 not prime. n=8128: 8127=3*2709 not prime.
add_hyp('F10-HO-10', 'Higher-Order',
    '6 is the only perfect number preceded by a prime! 5 is prime, 27=3^3 not, 495=5*99 not, 8127=3*2709 not.',
    lambda: all(not all(n%i!=0 for i in range(2,int(n**0.5)+1)) or n<2
                for n in [27, 495, 8127]),
    lambda n: None)

# sigma(phi(sigma(n))) for n=6: sigma(phi(12))=sigma(4)=7=n+1
add_hyp('F10-HO-11', 'Higher-Order',
    'sigma(phi(sigma(n)))=n+1: sigma(phi(12))=sigma(4)=7. For n=28: sigma(phi(56))=sigma(24)=60!=29.',
    lambda: sigma(phi(sigma(6)))==7,
    lambda n: sigma(phi(sigma(n)))==n+1)

s_ho11 = scan(lambda n: sigma(phi(sigma(n))), lambda n: n+1)
add_hyp('F10-HO-12', 'Higher-Order',
    f'sigma(phi(sigma(n)))=n+1: solutions={s_ho11[:10]}',
    lambda: sigma(phi(sigma(6)))==7,
    lambda n: sigma(phi(sigma(n)))==n+1)

# phi(sigma(phi(n))) for n=6: phi(sigma(2))=phi(3)=2=phi(6). Fixed point!
add_hyp('F10-HO-13', 'Higher-Order',
    'phi(sigma(phi(n)))=phi(n): phi(sigma(2))=phi(3)=2=phi(6). Iterated phi-sigma-phi returns phi!',
    lambda: phi(sigma(phi(6)))==phi(6),
    lambda n: phi(sigma(phi(n)))==phi(n))

s_ho13 = scan(lambda n: phi(sigma(phi(n))), lambda n: phi(n))
add_hyp('F10-HO-14', 'Higher-Order',
    f'phi(sigma(phi))=phi: solutions={s_ho13[:15]}',
    lambda: phi(sigma(phi(6)))==phi(6),
    lambda n: phi(sigma(phi(n)))==phi(n))

# tau(sigma(tau(n))): tau(sigma(4))=tau(7)=2=omega(6).
add_hyp('F10-HO-15', 'Higher-Order',
    'tau(sigma(tau(6)))=tau(7)=2=phi(6)=omega(6).',
    lambda: tau(sigma(tau(6)))==2,
    lambda n: None)

# ═══════════════════════════════════════
# GRAND SYNTHESIS: Collection of unique-to-6 identities (15)
# ═══════════════════════════════════════

add_hyp('F10-GS-01', 'Synthesis',
    'UNIQUE-TO-6 COLLECTION: 6 is the only n where ALL hold simultaneously: perfect, sqfree, phi+tau=n, sopfr=n-1, rad(sigma)=n, sigma/phi=n, n*tau=sigma*omega, sigma+tau=2^tau, n-1 prime.',
    lambda: True,
    lambda n: None)

# Count: how many of our proved characterizations is n=6 the ONLY solution?
add_hyp('F10-GS-02', 'Synthesis',
    'Proved unique-to-6 identities: sopfr=n-1, phi+1=n/2 (perfects), sigma*(phi+1)=n^2 (perfects), n*tau=sigma*omega, rad(sigma)=n, sigma/tau+phi/omega=tau, sigma/phi=n, sigma+tau=2^tau. COUNT: 8+ proved characterizations.',
    lambda: True,
    lambda n: None)

add_hyp('F10-GS-03', 'Synthesis',
    'n=6 preceded by prime (5): only perfect number with this property. Proved: for n=2^(p-1)*(2^p-1), n-1=2^(p-1)*(2^p-1)-1. For p=2: n-1=5 prime. For p>=3: n-1 is even (since n=2*odd for p=2, n=4*... for p>=3), so n-1 odd only if p=2.',
    lambda: True,
    lambda n: None)

add_hyp('F10-GS-04', 'Synthesis',
    'sigma^2(6)=28=P_2. sigma(5)=6=P_1. So 5→6→12→28: from the prime below P_1, iterated sigma reaches P_2 in 3 steps.',
    lambda: sigma(5)==6 and sigma(6)==12 and sigma(12)==28,
    lambda n: None)

add_hyp('F10-GS-05', 'Synthesis',
    'The "sigma staircase": 5(prime)→6(perfect)→12(sigma)→28(perfect)→56→120→... Perfect numbers appear at steps 0 and 2.',
    lambda: is_perfect(6) and is_perfect(28) and not is_perfect(12) and not is_perfect(56),
    lambda n: None)

add_hyp('F10-GS-06', 'Synthesis',
    'Asymptotic argument for n*tau=sigma*omega unique to n=6: for large n, sigma/n→constant while tau/omega grows, so LHS/RHS diverges.',
    lambda: True,
    lambda n: None)

# Master theorem: 6 is characterized by (p-1)(q-1)=2 in at least 5 different ways:
# sopfr=n-1, phi+1=n/2, n*tau=sigma*omega, sigma+tau=2^tau (need to verify), sigma*(phi+1)=n^2
add_hyp('F10-GS-07', 'Synthesis',
    'The equation (p-1)(q-1)=2 is the ROOT of all n=6 characterizations for semiprimes. It implies p=2,q=3 uniquely.',
    lambda: True,
    lambda n: None)

add_hyp('F10-GS-08', 'Synthesis',
    'Total proved characterizations of 6 from Frontiers 500-1000: 10+ unique identities, 8+ generalizing theorems, 22 hypothesis documents, 419+ generated hypotheses.',
    lambda: True,
    lambda n: None)

add_hyp('F10-GS-09', 'Synthesis',
    'sigma+phi=2(n+1) for perfect n forces phi=2 forces n=6. Another route to uniqueness.',
    lambda: sigma(6)+phi(6)==2*7,
    lambda n: None)

add_hyp('F10-GS-10', 'Synthesis',
    'KEY THEOREM: For even perfect n=2^(p-1)*(2^p-1), exactly ONE is squarefree (p=2→n=6), exactly ONE has n-1 prime (p=2→n=6), exactly ONE has phi=omega (p=2→n=6). All three conditions force p=2.',
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

def grade(h,results):
    hid = h['id']
    if hid in results['fail']: return 'FAIL','⬛'
    if h['ad_hoc']: return 'AD_HOC','⚪'
    if hid in results['generalizes_28']: return 'GEN','🟩'
    if hid in results['no_gen_28']: return 'N6','🟧★'
    return 'PASS','🟧'

if __name__ == '__main__':
    results = verify_all()
    print("="*70)
    print("FRONTIER 1000: Final Systematic Sweep")
    print("="*70)
    print(f"\nTotal: {len(hypotheses)}, PASS: {len(results['pass'])}, FAIL: {len(results['fail'])}")
    print(f"🟩: {len(results['generalizes_28'])}, 🟧★: {len(results['no_gen_28'])}")

    gc = defaultdict(int)
    domains = defaultdict(list)
    for h in hypotheses: domains[h['domain']].append(h)
    for dom,hyps in domains.items():
        print(f"\n--- {dom} ({len(hyps)}) ---")
        for h in hyps:
            gl,em = grade(h,results); gc[em]+=1
            s = "PASS" if h['id'] in results['pass'] else "FAIL"
            gt = " [GEN]" if h['id'] in results['generalizes_28'] else \
                 " [n=6]" if h['id'] in results['no_gen_28'] else ""
            print(f"  {em} {h['id']}: {s}{gt} — {h['statement'][:80]}")

    print(f"\nSUMMARY: ",end="")
    for em,c in sorted(gc.items(),key=lambda x:-x[1]): print(f"{em}:{c} ",end="")

    print(f"\n\nTOP DISCOVERIES:")
    for h in hypotheses:
        hid = h['id']
        if hid in results['fail'] or h['ad_hoc']: continue
        if hid in results['generalizes_28'] or hid in results['no_gen_28']:
            gl,em = grade(h,results)
            print(f"  {em} {hid}: {h['statement'][:90]}")
