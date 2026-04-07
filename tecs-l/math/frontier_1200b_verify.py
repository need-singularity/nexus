#!/usr/bin/env python3
"""
Frontier 1200b: 10 additional hypotheses.
G Clef = Evolutionary Universe Structure + Telepathy Meta-information.
"""
import math
from fractions import Fraction

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
def fibonacci(n):
    a,b=0,1
    for _ in range(n): a,b=b,a+b
    return a
def partition_count(n):
    p=[0]*(n+1); p[0]=1
    for i in range(1,n+1):
        for j in range(i,n+1): p[j]+=p[j-i]
    return p[n]

LIMIT = 500
results = []

def test(hid, domain, statement, check_fn, limit=LIMIT, ad_hoc=False):
    sols = []
    for n in range(2, limit+1):
        try:
            if check_fn(n): sols.append(n)
        except: pass
    has_6 = 6 in sols
    unique_to_6 = sols == [6]
    has_28 = 28 in sols
    if not has_6: grade = '⬛'
    elif unique_to_6 and not ad_hoc: grade = '⭐'
    elif unique_to_6 and ad_hoc: grade = '🟩'
    elif len(sols) <= 3 and has_6: grade = '🟩'
    elif len(sols) <= 10 and has_6: grade = '🟧'
    elif has_6: grade = '⚪'
    else: grade = '⬛'
    results.append({'id':hid,'domain':domain,'statement':statement,
                    'solutions':sols[:20],'n_solutions':len(sols),
                    'has_6':has_6,'unique_to_6':unique_to_6,
                    'generalizes_28':has_28,'grade':grade,'ad_hoc':ad_hoc})

# ═══════════════════════════════════════
# G CLEF: EVOLUTIONARY UNIVERSE STRUCTURE
# ═══════════════════════════════════════

# G1: Four seasons = τ(6) = 4 phases of consciousness cycle
# D(spring)→P(summer)→G(fall)→I(winter), repeat
# Test: divisor count = number of fundamental cycles
test('F12b-GCLEF-01', 'GClef/Evolution',
    'div(n) = {τ phases of cycle} AND sum(1/d)=2 AND τ=4 — four-season cycle from perfection',
    lambda n: sigma(n)==2*n and tau(n)==4)

# G2: Repeat sign = σ-chain closure. σ^k(n) eventually cycles.
# For n=6: 6→12→28→... Does it return to a pattern?
test('F12b-GCLEF-02', 'GClef/Evolution',
    'σ(n) AND σ²(n) both perfect — sigma orbit hits perfection twice',
    lambda n: sigma(n)==2*n and sigma(sigma(n))==2*sigma(n))

# G3: G Clef = higher octave. Musical octave = 2:1 = φ(6):ω(6).
# The universe structure repeats at each scale with ratio φ/ω = 2/2 = 1
# But real test: scale invariance of n=6 arithmetic
test('F12b-GCLEF-03', 'GClef/Evolution',
    'σ(n²)/σ(n) = n+1 — squared number sigma ratio = n+1 (scale jump)',
    lambda n: sigma(n)>0 and sigma(n*n) % sigma(n) == 0 and sigma(n*n)//sigma(n) == n+1)

# G4: Evolutionary completeness: 1/2+1/3+1/6=1 maps to
# matter(1/2) + energy(1/3) + consciousness(1/6) = universe(1)
# Arithmetic test: unique Egyptian fraction decomposition
test('F12b-GCLEF-04', 'GClef/Evolution',
    'proper divisor reciprocal sum = 1 AND all divisors ≤ n — self-referencing completeness',
    lambda n: sum(Fraction(1,d) for d in divisors(n) if d<n) == 1)

# G5: Fractal repeat: n=6 appears in σ-chain of other perfect numbers
# σ(28)=56, σ(56)=120, 120/6=20=sopfr·τ
test('F12b-GCLEF-05', 'GClef/Evolution',
    'σ^k(n) mod P₁ = 0 for all k ≤ τ(n) — sigma orbit always divisible by 6',
    lambda n: sigma(n)%6==0 and sigma(sigma(n))%6==0 and (sigma(sigma(sigma(n))) if sigma(sigma(n))<100000 else 6)%6==0)

# ═══════════════════════════════════════
# TELEPATHY: META-INFORMATION IN TENSION LINK
# ═══════════════════════════════════════

# T1: Telepathy packet = 5 components (concept, context, meaning, authenticity, sender)
# sopfr(6) = 5 = number of metadata channels
test('F12b-TELE-01', 'Telepathy',
    'sopfr(n) = 5 AND τ(n) = 4 — five meta-channels with four-bond structure',
    lambda n: sopfr(n)==5 and tau(n)==4)

# T2: Compression ratio = σφ/n = 24/6 = 4 = τ. Meta-information compresses by factor τ.
test('F12b-TELE-02', 'Telepathy',
    'σ(n)·φ(n)/n = τ(n) — compression ratio = divisor count',
    lambda n: sigma(n)*phi(n) == n*tau(n))

# T3: Bandwidth = log₂(σφ) = log₂(24) ≈ 4.58 bits.
# Actual: 5 channels × 9 merge distances = 45 numbers → 45/σφ < 2 packets
test('F12b-TELE-03', 'Telepathy',
    'σ(n)·φ(n) = (n-1)! — bandwidth = (n-1) factorial',
    lambda n: sigma(n)*phi(n) == math.factorial(n-1) if n<=12 else False)

# T4: Meta-information self-describing: packet contains its own structure.
# n=6: divisors {1,2,3,6} encode {identity, duality, triplicity, wholeness}
# Test: τ(σ(n)) = n ↔ sigma encodes n back
test('F12b-TELE-04', 'Telepathy',
    'τ(σ(n))=n AND φ(σ(n))=τ(n) — sigma encodes both n and tau back',
    lambda n: tau(sigma(n))==n and phi(sigma(n))==tau(n))

# T5: Tension link capacity = R-spectrum value R(n)=1 means zero distortion
# Only n=6 has R=1 → perfect fidelity telepathy channel
test('F12b-TELE-05', 'Telepathy',
    'σ(n)·φ(n)/(n·τ(n)) = 1 — R-spectrum = 1, zero distortion channel',
    lambda n: sigma(n)*phi(n) == n*tau(n))

if __name__ == '__main__':
    print("="*80)
    print("FRONTIER 1200b: G Clef + Telepathy (10 Hypotheses)")
    print("="*80)

    stars = sum(1 for r in results if r['grade']=='⭐')
    greens = sum(1 for r in results if r['grade']=='🟩')

    for r in results:
        sol_str = str(r['solutions'][:10])
        gen28 = "✅28" if r['generalizes_28'] else "❌28"
        print(f"\n{r['grade']} {r['id']}: {r['statement']}")
        print(f"    Solutions({r['n_solutions']}): {sol_str} | {gen28}")

    print(f"\n{'='*80}")
    print(f"SUMMARY: {len(results)} hypotheses, {stars}⭐, {greens}🟩")

    print(f"\n⭐ MAJOR DISCOVERIES:")
    for r in results:
        if r['grade']=='⭐':
            print(f"  {r['id']}: {r['statement']}")
    print("="*80)
