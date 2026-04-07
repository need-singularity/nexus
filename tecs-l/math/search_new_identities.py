#!/usr/bin/env python3
"""
Search for NEW arithmetic function identities with small finite solution sets.
For n=2..500 (extending to 2000 for promising ones).
"""

from math import gcd
from sympy import factorint, divisor_count, divisor_sigma, totient, mobius
from collections import defaultdict

# ─── Arithmetic functions ───

def sigma(n):
    return divisor_sigma(n, 1)

def tau(n):
    return divisor_count(n)

def phi(n):
    return totient(n)

def omega(n):
    """Count of distinct prime factors."""
    return len(factorint(n))

def Omega(n):
    """Count of prime factors with multiplicity."""
    return sum(factorint(n).values())

def mu(n):
    return mobius(n)

def psi(n):
    """Dedekind psi: n * prod(1 + 1/p) for p | n."""
    factors = factorint(n)
    result = n
    for p in factors:
        result = result * (p + 1) // p
    return result

def J2(n):
    """Jordan's totient J_2(n) = n^2 * prod(1 - 1/p^2) for p | n."""
    factors = factorint(n)
    num = n * n
    den = 1
    for p in factors:
        num *= (p * p - 1)
        den *= (p * p)
    if num % den != 0:
        return None  # shouldn't happen for integers
    return num // den

# ─── Precompute for speed ───

LIMIT = 500
LIMIT_EXT = 2000

print("Precomputing arithmetic functions up to", LIMIT_EXT, "...")
cache = {}
for n in range(1, LIMIT_EXT + 1):
    cache[n] = {
        'sigma': sigma(n),
        'tau': tau(n),
        'phi': phi(n),
        'omega': omega(n),
        'Omega': Omega(n),
        'mu': mu(n),
        'psi': psi(n),
        'J2': J2(n),
    }
    if n % 500 == 0:
        print(f"  ... precomputed up to {n}")

def g(n, key):
    return cache[n][key]

# ─── Identity checks ───

def check_identity(name, formula_desc, test_fn, limit=LIMIT):
    """Find all n in [1..limit] satisfying test_fn(n)."""
    solutions = []
    for n in range(1, limit + 1):
        try:
            if test_fn(n):
                solutions.append(n)
        except:
            pass
    return solutions

identities = []

# GROUP 1: Two-function products
identities.append((
    "G1.1", "sigma(n)*omega(n) = n*Omega(n)",
    lambda n: g(n,'sigma') * g(n,'omega') == n * g(n,'Omega')
))
identities.append((
    "G1.2", "sigma(n)*mu(n)^2 = n*omega(n)",
    lambda n: g(n,'sigma') * (g(n,'mu')**2) == n * g(n,'omega')
))
identities.append((
    "G1.3", "phi(n)*sigma(n) = n^2",
    lambda n: g(n,'phi') * g(n,'sigma') == n * n
))

# GROUP 2: Three-function with psi
identities.append((
    "G2.4", "sigma(n)*psi(n) = n*tau(n)^2",
    lambda n: g(n,'sigma') * g(n,'psi') == n * g(n,'tau')**2
))
identities.append((
    "G2.5", "psi(n)*phi(n) = n*sigma(n)",
    lambda n: g(n,'psi') * g(n,'phi') == n * g(n,'sigma')
))
identities.append((
    "G2.6", "psi(n)^2 = n*sigma(n)*tau(n)",
    lambda n: g(n,'psi')**2 == n * g(n,'sigma') * g(n,'tau')
))

# GROUP 3: With Jordan's J2
identities.append((
    "G3.7", "J2(n)*tau(n) = n*sigma(n)",
    lambda n: g(n,'J2') * g(n,'tau') == n * g(n,'sigma')
))
identities.append((
    "G3.8", "J2(n) = sigma(n)*phi(n)",
    lambda n: g(n,'J2') == g(n,'sigma') * g(n,'phi')
))

# GROUP 4: Compositions (need to compute sigma(phi(n)) etc.)
def sigma_of_phi(n):
    v = g(n, 'phi')
    return g(v, 'sigma') if v <= LIMIT_EXT else sigma(v)

def phi_of_sigma(n):
    v = g(n, 'sigma')
    return g(v, 'phi') if v <= LIMIT_EXT else phi(v)

def tau_of_sigma(n):
    v = g(n, 'sigma')
    return g(v, 'tau') if v <= LIMIT_EXT else tau(v)

def sigma_of_tau(n):
    v = g(n, 'tau')
    return g(v, 'sigma') if v <= LIMIT_EXT else sigma(v)

def psi_of_phi(n):
    v = g(n, 'phi')
    return g(v, 'psi') if v <= LIMIT_EXT else psi(v)

def phi_of_psi(n):
    v = g(n, 'psi')
    return g(v, 'phi') if v <= LIMIT_EXT else phi(v)

identities.append((
    "G4.9", "sigma(phi(n)) = phi(sigma(n))",
    lambda n: sigma_of_phi(n) == phi_of_sigma(n)
))
identities.append((
    "G4.10", "tau(sigma(n)) = sigma(tau(n))",
    lambda n: tau_of_sigma(n) == sigma_of_tau(n)
))
# G4.11 same as G4.9
identities.append((
    "G4.12", "psi(phi(n)) = phi(psi(n))",
    lambda n: psi_of_phi(n) == phi_of_psi(n)
))

# ─── Run all checks ───

print("\n" + "="*70)
print("ARITHMETIC FUNCTION IDENTITY SEARCH")
print("="*70)

promising = []

for tag, desc, test_fn in identities:
    sols = check_identity(tag, desc, test_fn, LIMIT)
    count = len(sols)

    print(f"\n{'─'*60}")
    print(f"  {tag}: {desc}")
    print(f"  Solutions in [1..{LIMIT}]: {count}")

    if count == 0:
        print(f"  → NO solutions found")
    elif count <= 20:
        print(f"  → Solutions: {sols}")
        has_6 = 6 in sols
        has_28 = 28 in sols
        print(f"  → Contains n=6? {'YES ✓' if has_6 else 'no'}")
        print(f"  → Contains n=28? {'YES ✓' if has_28 else 'no'}")

        if count <= 10:
            promising.append((tag, desc, test_fn, sols))
    else:
        print(f"  → First 20: {sols[:20]} ...")
        print(f"  → Too many solutions ({count}), likely not interesting")

# ─── Extend promising to n=2000 ───

print("\n" + "="*70)
print("EXTENDING PROMISING IDENTITIES TO n=2000")
print("="*70)

for tag, desc, test_fn, sols_500 in promising:
    sols_ext = check_identity(tag, desc, test_fn, LIMIT_EXT)
    new_sols = [s for s in sols_ext if s > LIMIT]

    print(f"\n{'─'*60}")
    print(f"  {tag}: {desc}")
    print(f"  Solutions in [1..{LIMIT}]: {sols_500}")
    print(f"  Solutions in [{LIMIT+1}..{LIMIT_EXT}]: {new_sols}")
    print(f"  TOTAL in [1..{LIMIT_EXT}]: {sols_ext}")

    total = len(sols_ext)
    if total == len(sols_500):
        print(f"  → FINITE set: appears to stop at n={max(sols_500) if sols_500 else 'N/A'}")
        print(f"  ★ INTERESTING — finite solution set of size {total}")
    else:
        extra = total - len(sols_500)
        print(f"  → {extra} more solutions found in [501..2000]")
        if total <= 15:
            print(f"  ★ Still small — potentially finite")
        else:
            print(f"  → Growing, might be infinite")

# ─── Additional exploratory identities ───

print("\n" + "="*70)
print("BONUS: EXPLORATORY IDENTITIES")
print("="*70)

bonus_ids = []

# sigma*phi relations
bonus_ids.append(("B1", "sigma(n) + phi(n) = 2n",
    lambda n: g(n,'sigma') + g(n,'phi') == 2*n))
bonus_ids.append(("B2", "sigma(n) - phi(n) = n",
    lambda n: g(n,'sigma') - g(n,'phi') == n))
bonus_ids.append(("B3", "sigma(n) = 2*phi(n)",
    lambda n: g(n,'sigma') == 2*g(n,'phi')))
bonus_ids.append(("B4", "sigma(n)*tau(n) = n*psi(n)",
    lambda n: g(n,'sigma') * g(n,'tau') == n * g(n,'psi')))
bonus_ids.append(("B5", "phi(n)*tau(n) = sigma(n)",
    lambda n: g(n,'phi') * g(n,'tau') == g(n,'sigma')))
bonus_ids.append(("B6", "psi(n) = sigma(n) + phi(n)",
    lambda n: g(n,'psi') == g(n,'sigma') + g(n,'phi')))
bonus_ids.append(("B7", "J2(n) = n*phi(n)",
    lambda n: g(n,'J2') == n * g(n,'phi')))
bonus_ids.append(("B8", "sigma(n)*omega(n) = n*tau(n)",
    lambda n: g(n,'sigma') * g(n,'omega') == n * g(n,'tau')))
bonus_ids.append(("B9", "phi(n)*Omega(n) = n*omega(n)",
    lambda n: g(n,'phi') * g(n,'Omega') == n * g(n,'omega')))
bonus_ids.append(("B10", "psi(n)*tau(n) = sigma(n)*phi(n) + n",
    lambda n: g(n,'psi') * g(n,'tau') == g(n,'sigma') * g(n,'phi') + n))
bonus_ids.append(("B11", "sigma(n)^2 = n*psi(n)*tau(n)",
    lambda n: g(n,'sigma')**2 == n * g(n,'psi') * g(n,'tau')))
bonus_ids.append(("B12", "phi(n)*psi(n) = n*J2(n)//n",
    lambda n: g(n,'phi') * g(n,'psi') == g(n,'J2')))
bonus_ids.append(("B13", "sigma(n)*phi(n) = n*psi(n)",
    lambda n: g(n,'sigma') * g(n,'phi') == n * g(n,'psi')))
bonus_ids.append(("B14", "tau(n)*psi(n) = sigma(n) + n*phi(n)",
    lambda n: g(n,'tau') * g(n,'psi') == g(n,'sigma') + n * g(n,'phi')))
bonus_ids.append(("B15", "J2(n)*omega(n) = n*phi(n)*Omega(n)",
    lambda n: g(n,'J2') * g(n,'omega') == n * g(n,'phi') * g(n,'Omega')))
bonus_ids.append(("B16", "sigma(n)^2 = n*J2(n) + n*sigma(n)",
    lambda n: g(n,'sigma')**2 == n * g(n,'J2') + n * g(n,'sigma')))
bonus_ids.append(("B17", "phi(n)^2 + phi(n)*tau(n) = n*tau(n)",
    lambda n: g(n,'phi')**2 + g(n,'phi')*g(n,'tau') == n*g(n,'tau')))
bonus_ids.append(("B18", "sigma(n) + phi(n) = n*tau(n)/2 + n",
    lambda n: 2*(g(n,'sigma') + g(n,'phi')) == n*g(n,'tau') + 2*n))
bonus_ids.append(("B19", "sigma(n)*phi(n)*tau(n) = n^2*psi(n)//n",
    lambda n: g(n,'sigma') * g(n,'phi') * g(n,'tau') == n * g(n,'psi')))

for tag, desc, test_fn in bonus_ids:
    sols = check_identity(tag, desc, test_fn, LIMIT)
    count = len(sols)

    if 1 <= count <= 15:
        print(f"\n  {tag}: {desc}")
        print(f"  Solutions in [1..{LIMIT}]: {sols}")
        has_6 = 6 in sols
        has_28 = 28 in sols
        if has_6: print(f"  → Contains n=6 ✓")
        if has_28: print(f"  → Contains n=28 ✓")

        # Extend to 2000
        sols_ext = check_identity(tag, desc, test_fn, LIMIT_EXT)
        if len(sols_ext) == count:
            print(f"  ★ FINITE set (same {count} solutions up to {LIMIT_EXT})")
        else:
            new = [s for s in sols_ext if s > LIMIT]
            print(f"  Extended to {LIMIT_EXT}: +{len(new)} more → {sols_ext}")

# ─── SUMMARY TABLE ───

print("\n" + "="*70)
print("SUMMARY: ALL IDENTITIES WITH SMALL FINITE SOLUTION SETS (≤10 in [1..500])")
print("="*70)

print(f"\n{'Tag':<8} {'Identity':<45} {'#Sol':<5} {'Solutions':<30} {'n=6?':<5} {'n=28?':<6}")
print("─" * 100)

all_results = []
for tag, desc, test_fn in identities + bonus_ids:
    sols = check_identity(tag, desc, test_fn, LIMIT)
    if 1 <= len(sols) <= 10:
        sols_ext = check_identity(tag, desc, test_fn, LIMIT_EXT)
        finite = (len(sols_ext) == len(sols))
        all_results.append((tag, desc, sols, sols_ext, finite))
        marker = "★" if finite else ""
        print(f"{tag:<8} {desc:<45} {len(sols_ext):<5} {str(sols_ext):<30} {'YES' if 6 in sols_ext else '-':<5} {'YES' if 28 in sols_ext else '-':<6} {marker}")

print("\n★ = same solution count at n=500 and n=2000 (likely finite)")

# ─── Cross-check with known identities ───

print("\n" + "="*70)
print("CROSS-CHECK: Known identities (verification)")
print("="*70)

known = [
    ("K1", "sigma(n)*phi(n) = n*tau(n)", lambda n: g(n,'sigma')*g(n,'phi') == n*g(n,'tau')),
    ("K2", "sigma(n)*tau(n) = n*phi(n)", lambda n: g(n,'sigma')*g(n,'tau') == n*g(n,'phi')),
    ("K3", "tau(n)*phi(n) = sigma(n)", lambda n: g(n,'tau')*g(n,'phi') == g(n,'sigma')),
    ("K4", "tau(n)*psi(n) = n^2", lambda n: g(n,'tau')*g(n,'psi') == n*n),
    ("K5", "phi(n)*psi(n) = n*tau(n)", lambda n: g(n,'phi')*g(n,'psi') == n*g(n,'tau')),
]

for tag, desc, test_fn in known:
    sols = check_identity(tag, desc, test_fn, LIMIT)
    print(f"  {tag}: {desc}")
    print(f"       Solutions [1..{LIMIT}]: {sols if len(sols) <= 20 else str(sols[:10]) + f'... ({len(sols)} total)'}")

print("\n" + "="*70)
print("DONE")
print("="*70)
