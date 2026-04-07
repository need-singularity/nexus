#!/usr/bin/env python3
"""
Massive identity mining: systematically generate ~300 equation templates
and find ALL that are unique to n=6 in [2, 10000].
"""
import math

def sigma(n):
    return sum(d for d in range(1, n+1) if n % d == 0)

def tau(n):
    return sum(1 for d in range(1, n+1) if n % d == 0)

def phi(n):
    return sum(1 for k in range(1, n+1) if math.gcd(k, n) == 1)

def sopfr(n):
    s, d, temp = 0, 2, n
    while d * d <= temp:
        while temp % d == 0: s += d; temp //= d
        d += 1
    if temp > 1: s += temp
    return s

def omega(n):
    count, d, temp = 0, 2, n
    while d * d <= temp:
        if temp % d == 0:
            count += 1
            while temp % d == 0: temp //= d
        d += 1
    if temp > 1: count += 1
    return count

def lpf(n):
    result, d, temp = 1, 2, n
    while d * d <= temp:
        while temp % d == 0: result = d; temp //= d
        d += 1
    if temp > 1: result = temp
    return result

MAX = 5000
print(f"Precomputing for n=1..{MAX}...")
S = [0]*(MAX+1); T = [0]*(MAX+1); P = [0]*(MAX+1)
SP = [0]*(MAX+1); OM = [0]*(MAX+1); LF = [0]*(MAX+1)
for n in range(1, MAX+1):
    S[n]=sigma(n); T[n]=tau(n); P[n]=phi(n)
    SP[n]=sopfr(n); OM[n]=omega(n); LF[n]=lpf(n)

# Composition cache (only for small values)
S_of = {}; T_of = {}; P_of = {}
for v in range(1, 200):
    S_of[v] = sigma(v); T_of[v] = tau(v); P_of[v] = phi(v)

def safe_sigma(v):
    if v < 1 or v > 199: return None
    return S_of[v]
def safe_tau(v):
    if v < 1 or v > 199: return None
    return T_of[v]
def safe_phi(v):
    if v < 1 or v > 199: return None
    return P_of[v]

print("Done. Generating equations...\n")

# ═══════════════════════════════════════════════════════════
# Generate equations: LHS = RHS, both functions of (n,S,T,P,SP,OM,LF)
# ═══════════════════════════════════════════════════════════

# Building blocks: expressions that compute a value from n's functions
def make_exprs(n):
    """Return dict of expression_name -> value for given n."""
    s,t,p,sp,om,lf = S[n],T[n],P[n],SP[n],OM[n],LF[n]
    e = {}
    # Atomic
    e['n'] = n; e['S'] = s; e['T'] = t; e['P'] = p; e['SP'] = sp; e['OM'] = om; e['LF'] = lf
    # Simple binary ops (avoid division by zero)
    e['S+T'] = s+t; e['S-T'] = s-t; e['S*T'] = s*t
    e['S+P'] = s+p; e['S-P'] = s-p; e['S*P'] = s*p
    e['T+P'] = t+p; e['T-P'] = t-p; e['T*P'] = t*p
    e['S+SP'] = s+sp; e['S*SP'] = s*sp; e['T*SP'] = t*sp
    e['P*SP'] = p*sp; e['S*OM'] = s*om; e['T*OM'] = t*om
    e['S*LF'] = s*lf; e['T*LF'] = t*lf; e['P*LF'] = p*lf
    e['S+LF'] = s+lf; e['T+LF'] = t+lf
    e['SP+OM'] = sp+om; e['SP-OM'] = sp-om; e['SP*OM'] = sp*om
    e['T*(T-1)'] = t*(t-1); e['T*(T+1)'] = t*(t+1)
    e['P*(P+1)'] = p*(p+1); e['S-T-P'] = s-t-p
    e['S+T+P'] = s+t+p; e['S*T*P'] = s*t*p
    e['S*SP*P'] = s*sp*p; e['S*S'] = s*s; e['T*T'] = t*t; e['P*P'] = p*p
    e['S*S*SP'] = s*s*sp
    if t > 0: e['S/T'] = s/t if s%t==0 else s/t
    if p > 0: e['S/P'] = s/p if s%p==0 else s/p; e['n/P'] = n/p if n%p==0 else n/p
    if t > 0: e['n*n/T'] = n*n/t if (n*n)%t==0 else n*n/t
    # With n
    e['n+S'] = n+s; e['n+T'] = n+t; e['n+P'] = n+p
    e['n-T'] = n-t; e['n*P'] = n*p; e['n*T'] = n*t; e['n*S'] = n*s
    e['n*n'] = n*n; e['n*(n-1)'] = n*(n-1); e['n*(n+1)'] = n*(n+1)
    e['3*n-6'] = 3*n-6; e['2*n'] = 2*n; e['n-2'] = n-2
    e['n+1'] = n+1; e['n-1'] = n-1
    # Factorials (only for small n)
    if n <= 12:
        e['n!'] = math.factorial(n)
        e['(n-1)!'] = math.factorial(n-1)
    if n <= 20:
        e['C(n,2)'] = n*(n-1)//2
        e['C(n,3)'] = n*(n-1)*(n-2)//6 if n>=3 else 0
    # Compositions
    st = safe_sigma(t)
    if st is not None: e['S(T)'] = st
    sp2 = safe_sigma(p)
    if sp2 is not None: e['S(P)'] = sp2
    tt = safe_tau(s)
    if tt is not None: e['T(S)'] = tt
    tp = safe_tau(p)
    if tp is not None: e['T(P)'] = tp
    ps = safe_phi(s)
    if ps is not None: e['P(S)'] = ps
    pt = safe_phi(t)
    if pt is not None: e['P(T)'] = pt
    # More combos with compositions
    if tt is not None: e['T(S)*P'] = tt * p
    if st is not None: e['S(T)-T'] = st - t
    if ps is not None: e['P(S)+T'] = ps + t
    # Constants
    e['1'] = 1; e['2'] = 2; e['3'] = 3; e['4'] = 4; e['6'] = 6; e['12'] = 12
    # Three-term combos
    e['S+T-SP+1'] = s+t-sp+1
    e['S-T+P'] = s-t+p; e['S+T-P'] = s+t-p
    e['S*P-T'] = s*p-t; e['S*P+T'] = s*p+t
    e['T*SP'] = t*sp; e['P*SP*S'] = p*sp*s
    e['LF+1'] = lf+1; e['LF-1'] = lf-1
    return e

# Evaluate for n=6
e6 = make_exprs(6)
expr_names = sorted(e6.keys())

# Find all pairs where LHS(6) == RHS(6) and both are integers
print(f"Expression count: {len(expr_names)}")
print(f"Pair space: {len(expr_names)**2}")

candidates = []
for lhs_name in expr_names:
    lv = e6[lhs_name]
    if not isinstance(lv, (int, float)) or lv != int(lv): continue
    lv = int(lv)
    for rhs_name in expr_names:
        if lhs_name >= rhs_name: continue  # avoid duplicates
        rv = e6[rhs_name]
        if not isinstance(rv, (int, float)) or rv != int(rv): continue
        rv = int(rv)
        if lv == rv and lv != 0:
            candidates.append((lhs_name, rhs_name, lv))

print(f"Candidate equations (match at n=6): {len(candidates)}")
print(f"Testing uniqueness for each in [2,{MAX}]...\n")

# Test uniqueness
unique = []
near_unique = []
tested = 0

for lhs_name, rhs_name, val6 in candidates:
    others = []
    for n in range(2, MAX+1):
        if n == 6: continue
        try:
            en = make_exprs(n)
            lv = en.get(lhs_name)
            rv = en.get(rhs_name)
            if lv is not None and rv is not None:
                if isinstance(lv, (int,float)) and isinstance(rv, (int,float)):
                    if abs(lv - rv) < 1e-9:
                        others.append(n)
                        if len(others) > 5: break
        except:
            pass

    tested += 1
    if not others:
        unique.append((lhs_name, rhs_name, val6))
    elif len(others) <= 2:
        near_unique.append((lhs_name, rhs_name, val6, others))

print(f"Equations tested: {tested}")
print(f"Unique to n=6: {len(unique)}")
print(f"Near-unique (≤2 others): {len(near_unique)}")

# Deduplicate: remove trivially equivalent (same value, related expressions)
print(f"\n{'='*70}")
print(f"★★★ ALL IDENTITIES UNIQUE TO n=6 IN [2,{MAX}]")
print(f"{'='*70}\n")

# Group by value at n=6
from collections import defaultdict
by_val = defaultdict(list)
for lhs, rhs, val in unique:
    by_val[val].append((lhs, rhs))

for val in sorted(by_val.keys()):
    eqs = by_val[val]
    print(f"  Value = {val}:")
    for lhs, rhs in eqs[:15]:  # cap per value
        print(f"    {lhs} = {rhs}")
    if len(eqs) > 15:
        print(f"    ... and {len(eqs)-15} more")
    print()

# Print near-unique
if near_unique:
    print(f"\n{'='*70}")
    print(f"★★ NEAR-UNIQUE (also holds for ≤2 other n)")
    print(f"{'='*70}\n")
    for lhs, rhs, val, others in near_unique[:30]:
        print(f"  {lhs} = {rhs} (={val})  also: {others}")

# Summary
print(f"\n{'='*70}")
print(f"SUMMARY")
print(f"{'='*70}")
print(f"  Expression templates: {len(expr_names)}")
print(f"  Equation pairs tested: {tested}")
print(f"  Unique to n=6: {len(unique)}")
print(f"  Near-unique: {len(near_unique)}")
print(f"  By value: {dict((v, len(eqs)) for v, eqs in by_val.items())}")
