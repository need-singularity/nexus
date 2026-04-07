#!/usr/bin/env python3
"""
Search for new identities involving Ω(n) and other arithmetic functions.
Functions: σ(n), τ(n), φ(n), ω(n), Ω(n)
"""

from sympy import factorint, totient, divisor_sigma, divisor_count
from collections import defaultdict
import time

def omega_small(n):
    """ω(n) = number of distinct prime factors"""
    return len(factorint(n))

def Omega_big(n):
    """Ω(n) = number of prime factors with multiplicity"""
    return sum(factorint(n).values())

def sigma(n):
    return divisor_sigma(n)

def tau(n):
    return divisor_count(n)

def phi(n):
    return totient(n)

# Precompute for speed
print("Precomputing arithmetic functions up to 100000...")
t0 = time.time()

LIMIT_SMALL = 10001
LIMIT_BIG = 100001

# Precompute using sieve-like approach for speed
phi_arr = list(range(LIMIT_BIG))  # phi via sieve
for p in range(2, LIMIT_BIG):
    if phi_arr[p] == p:  # p is prime
        for m in range(p, LIMIT_BIG, p):
            phi_arr[m] = phi_arr[m] // p * (p - 1)

# Smallest prime factor sieve for factorization
spf = list(range(LIMIT_BIG))
for p in range(2, int(LIMIT_BIG**0.5) + 1):
    if spf[p] == p:
        for m in range(p*p, LIMIT_BIG, p):
            if spf[m] == m:
                spf[m] = p

def fast_factorint(n):
    factors = {}
    while n > 1:
        p = spf[n]
        e = 0
        while n % p == 0:
            n //= p
            e += 1
        factors[p] = e
    return factors

def fast_sigma(n):
    f = fast_factorint(n)
    result = 1
    for p, e in f.items():
        result *= (p**(e+1) - 1) // (p - 1)
    return result

def fast_tau(n):
    f = fast_factorint(n)
    result = 1
    for e in f.values():
        result *= (e + 1)
    return result

def fast_omega(n):
    return len(fast_factorint(n))

def fast_Omega(n):
    return sum(fast_factorint(n).values())

print(f"Sieve done in {time.time()-t0:.1f}s")
print()

# ============================================================
# 1. φ(n) = Ω(n) for n ≤ 100000
# ============================================================
print("=" * 70)
print("1. φ(n) = Ω(n) for n ≤ 100000")
print("=" * 70)
results_1 = []
for n in range(2, LIMIT_BIG):
    if phi_arr[n] == fast_Omega(n):
        results_1.append(n)

print(f"Found {len(results_1)} solutions")
if len(results_1) <= 200:
    print(f"Solutions: {results_1}")
else:
    print(f"First 50: {results_1[:50]}")
    print(f"Last 10: {results_1[-10:]}")

# Show details for first solutions
print(f"\n{'n':>8} | {'φ(n)':>6} | {'Ω(n)':>6} | {'ω(n)':>6} | factorization")
print("-" * 60)
for n in results_1[:30]:
    f = fast_factorint(n)
    fstr = " × ".join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(f.items()))
    print(f"{n:>8} | {phi_arr[n]:>6} | {fast_Omega(n):>6} | {fast_omega(n):>6} | {fstr}")
print()

# ============================================================
# 2. τ(n) = Ω(n) for n ≤ 10000
# ============================================================
print("=" * 70)
print("2. τ(n) = Ω(n) for n ≤ 10000")
print("=" * 70)
results_2 = []
for n in range(2, LIMIT_SMALL):
    if fast_tau(n) == fast_Omega(n):
        results_2.append(n)

print(f"Found {len(results_2)} solutions")
if len(results_2) <= 100:
    print(f"Solutions: {results_2}")
else:
    print(f"First 50: {results_2[:50]}")

print(f"\n{'n':>8} | {'τ(n)':>6} | {'Ω(n)':>6} | factorization")
print("-" * 55)
for n in results_2[:30]:
    f = fast_factorint(n)
    fstr = " × ".join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(f.items()))
    print(f"{n:>8} | {fast_tau(n):>6} | {fast_Omega(n):>6} | {fstr}")
print()

# ============================================================
# 3. σ(n)/τ(n) = Ω(n) for n ≤ 10000
# ============================================================
print("=" * 70)
print("3. σ(n)/τ(n) = Ω(n) (exact integer division) for n ≤ 10000")
print("=" * 70)
results_3 = []
for n in range(2, LIMIT_SMALL):
    s = fast_sigma(n)
    t = fast_tau(n)
    O = fast_Omega(n)
    if s % t == 0 and s // t == O:
        results_3.append(n)

print(f"Found {len(results_3)} solutions")
print(f"Solutions: {results_3}")
for n in results_3[:30]:
    f = fast_factorint(n)
    fstr = " × ".join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(f.items()))
    s, t, O = fast_sigma(n), fast_tau(n), fast_Omega(n)
    print(f"  n={n}: σ={s}, τ={t}, σ/τ={s//t}, Ω={O} | {fstr}")
print()

# ============================================================
# 4. New characterizations with Ω
# ============================================================
print("=" * 70)
print("4a. σ·Ω = n·τ for n ≤ 10000")
print("=" * 70)
results_4a = []
for n in range(2, LIMIT_SMALL):
    s, t, O = fast_sigma(n), fast_tau(n), fast_Omega(n)
    if s * O == n * t:
        results_4a.append(n)
print(f"Found {len(results_4a)} solutions: {results_4a[:50]}")
for n in results_4a[:20]:
    f = fast_factorint(n)
    fstr = " × ".join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(f.items()))
    s, t, O = fast_sigma(n), fast_tau(n), fast_Omega(n)
    print(f"  n={n}: σ={s}, τ={t}, Ω={O}, σ·Ω={s*O}, n·τ={n*t} | {fstr}")
print()

print("=" * 70)
print("4b. φ·Ω = ω·τ for n ≤ 10000")
print("=" * 70)
results_4b = []
for n in range(2, LIMIT_SMALL):
    p = phi_arr[n]
    O = fast_Omega(n)
    w = fast_omega(n)
    t = fast_tau(n)
    if p * O == w * t:
        results_4b.append(n)
print(f"Found {len(results_4b)} solutions: {results_4b[:50]}")
for n in results_4b[:20]:
    f = fast_factorint(n)
    fstr = " × ".join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(f.items()))
    ph, O, w, t = phi_arr[n], fast_Omega(n), fast_omega(n), fast_tau(n)
    print(f"  n={n}: φ={ph}, Ω={O}, ω={w}, τ={t}, φ·Ω={ph*O}, ω·τ={w*t} | {fstr}")
print()

print("=" * 70)
print("4c. σ·φ·ω = n·τ·Ω for n ≤ 10000")
print("=" * 70)
results_4c = []
for n in range(2, LIMIT_SMALL):
    s = fast_sigma(n)
    p = phi_arr[n]
    w = fast_omega(n)
    t = fast_tau(n)
    O = fast_Omega(n)
    if s * p * w == n * t * O:
        results_4c.append(n)
print(f"Found {len(results_4c)} solutions: {results_4c[:50]}")
for n in results_4c[:20]:
    f = fast_factorint(n)
    fstr = " × ".join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(f.items()))
    s, ph, w, t, O = fast_sigma(n), phi_arr[n], fast_omega(n), fast_tau(n), fast_Omega(n)
    print(f"  n={n}: σ={s}, φ={ph}, ω={w}, τ={t}, Ω={O} | LHS={s*ph*w}, RHS={n*t*O} | {fstr}")
print()

# ============================================================
# 5. Three-function identities
# ============================================================
print("=" * 70)
print("5a. σ = τ·φ + ω for n ≤ 10000")
print("=" * 70)
results_5a = []
for n in range(2, LIMIT_SMALL):
    s = fast_sigma(n)
    t = fast_tau(n)
    p = phi_arr[n]
    w = fast_omega(n)
    if s == t * p + w:
        results_5a.append(n)
print(f"Found {len(results_5a)} solutions: {results_5a[:50]}")
for n in results_5a[:20]:
    f = fast_factorint(n)
    fstr = " × ".join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(f.items()))
    s, t, ph, w = fast_sigma(n), fast_tau(n), phi_arr[n], fast_omega(n)
    print(f"  n={n}: σ={s}, τ·φ+ω={t*ph+w} | {fstr}")
print()

print("=" * 70)
print("5b. σ·ω = φ·τ + n for n ≤ 10000")
print("=" * 70)
results_5b = []
for n in range(2, LIMIT_SMALL):
    s = fast_sigma(n)
    w = fast_omega(n)
    p = phi_arr[n]
    t = fast_tau(n)
    if s * w == p * t + n:
        results_5b.append(n)
print(f"Found {len(results_5b)} solutions: {results_5b[:50]}")
for n in results_5b[:20]:
    f = fast_factorint(n)
    fstr = " × ".join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(f.items()))
    s, w, ph, t = fast_sigma(n), fast_omega(n), phi_arr[n], fast_tau(n)
    print(f"  n={n}: σ·ω={s*w}, φ·τ+n={ph*t+n} | {fstr}")
print()

print("=" * 70)
print("5c. σ + φ = n + τ·ω for n ≤ 10000")
print("=" * 70)
results_5c = []
for n in range(2, LIMIT_SMALL):
    s = fast_sigma(n)
    p = phi_arr[n]
    t = fast_tau(n)
    w = fast_omega(n)
    if s + p == n + t * w:
        results_5c.append(n)
print(f"Found {len(results_5c)} solutions: {results_5c[:50]}")
for n in results_5c[:20]:
    f = fast_factorint(n)
    fstr = " × ".join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(f.items()))
    s, ph, t, w = fast_sigma(n), phi_arr[n], fast_tau(n), fast_omega(n)
    print(f"  n={n}: σ+φ={s+ph}, n+τ·ω={n+t*w} | {fstr}")
print()

# ============================================================
# 6. Additive identities
# ============================================================
print("=" * 70)
print("6a. σ + φ + τ = 2n for n ≤ 10000")
print("=" * 70)
results_6a = []
for n in range(2, LIMIT_SMALL):
    s = fast_sigma(n)
    p = phi_arr[n]
    t = fast_tau(n)
    if s + p + t == 2 * n:
        results_6a.append(n)
print(f"Found {len(results_6a)} solutions: {results_6a[:100]}")
for n in results_6a[:20]:
    f = fast_factorint(n)
    fstr = " × ".join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(f.items()))
    s, ph, t = fast_sigma(n), phi_arr[n], fast_tau(n)
    print(f"  n={n}: σ+φ+τ={s}+{ph}+{t}={s+ph+t}, 2n={2*n} | {fstr}")
print()

print("=" * 70)
print("6b. σ - φ = n (i.e., σ(n) = n + φ(n)) for n ≤ 100000")
print("=" * 70)
results_6b = []
for n in range(2, LIMIT_BIG):
    s = fast_sigma(n)
    p = phi_arr[n]
    if s - p == n:
        results_6b.append(n)
print(f"Found {len(results_6b)} solutions")
if len(results_6b) <= 100:
    print(f"Solutions: {results_6b}")
else:
    print(f"First 50: {results_6b[:50]}")
for n in results_6b[:20]:
    f = fast_factorint(n)
    fstr = " × ".join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(f.items()))
    s, ph = fast_sigma(n), phi_arr[n]
    print(f"  n={n}: σ={s}, φ={ph}, σ-φ={s-ph} | {fstr}")
print()

print("=" * 70)
print("6c. σ·φ - n·τ = 0 (our main identity) for n ≤ 10000")
print("=" * 70)
results_6c = []
for n in range(2, LIMIT_SMALL):
    s = fast_sigma(n)
    p = phi_arr[n]
    t = fast_tau(n)
    if s * p == n * t:
        results_6c.append(n)
print(f"Found {len(results_6c)} solutions: {results_6c[:50]}")
for n in results_6c[:20]:
    f = fast_factorint(n)
    fstr = " × ".join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(f.items()))
    s, ph, t = fast_sigma(n), phi_arr[n], fast_tau(n)
    print(f"  n={n}: σ·φ={s*ph}, n·τ={n*t} | {fstr}")
print()

print("=" * 70)
print("6d. σ·φ - n·τ = k for small |k| ≤ 20, n ≤ 10000")
print("=" * 70)
k_solutions = defaultdict(list)
for n in range(2, LIMIT_SMALL):
    s = fast_sigma(n)
    p = phi_arr[n]
    t = fast_tau(n)
    k = s * p - n * t
    if abs(k) <= 20:
        k_solutions[k].append(n)

print(f"\n{'k':>5} | {'count':>6} | solutions (first 20)")
print("-" * 70)
for k in sorted(k_solutions.keys()):
    sols = k_solutions[k]
    sol_str = str(sols[:20])
    if len(sols) > 20:
        sol_str += f" ... ({len(sols)} total)"
    print(f"{k:>5} | {len(sols):>6} | {sol_str}")
print()

# ============================================================
# BONUS: Ω-based characterization of perfect numbers
# ============================================================
print("=" * 70)
print("BONUS: Special properties of perfect numbers (6, 28, 496, 8128)")
print("=" * 70)
perfects = [6, 28, 496, 8128]
print(f"\n{'n':>6} | {'σ':>8} | {'τ':>4} | {'φ':>6} | {'ω':>3} | {'Ω':>3} | σ/n | φ/n     | σ·φ  | n·τ  | σ·φ-n·τ | σ-φ-n | σ+φ-2n")
print("-" * 100)
for n in perfects:
    s = fast_sigma(n)
    t = fast_tau(n)
    p = phi_arr[n]
    w = fast_omega(n)
    O = fast_Omega(n)
    print(f"{n:>6} | {s:>8} | {t:>4} | {p:>6} | {w:>3} | {O:>3} | {s/n:.1f} | {p/n:.5f} | {s*p:>8} | {n*t:>8} | {s*p-n*t:>7} | {s-p-n:>5} | {s+p-2*n:>6}")

# Check Ω-specific identities for perfect numbers
print("\nΩ-specific checks for perfect numbers:")
print(f"{'n':>6} | Ω+ω | τ  | Ω·ω | σ/τ   | σ/(Ω+1) | φ/(Ω-1) | n/2^Ω")
print("-" * 75)
for n in perfects:
    s = fast_sigma(n)
    t = fast_tau(n)
    p = phi_arr[n]
    w = fast_omega(n)
    O = fast_Omega(n)
    print(f"{n:>6} | {O+w:>3} | {t:>2} | {O*w:>3} | {s/t:>5.1f} | {s/(O+1):>7.1f} | {p/(O-1) if O>1 else 'N/A':>7} | {n/2**O:>5.1f}")

# ============================================================
# BONUS 2: σ + φ = 2n (for completeness, since σ=2n for perfect)
# ============================================================
print("\n" + "=" * 70)
print("BONUS 2: σ(n) + φ(n) = 2n for n ≤ 10000")
print("  (Note: for perfect numbers σ=2n, so this requires φ=0, impossible)")
print("  Instead checking: σ(n) + φ(n) = 2n + τ(n)")
print("=" * 70)
results_b2 = []
for n in range(2, LIMIT_SMALL):
    s = fast_sigma(n)
    p = phi_arr[n]
    t = fast_tau(n)
    if s + p == 2 * n + t:
        results_b2.append(n)
print(f"Found {len(results_b2)} solutions: {results_b2[:50]}")
for n in results_b2[:15]:
    f = fast_factorint(n)
    fstr = " × ".join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(f.items()))
    s, ph, t = fast_sigma(n), phi_arr[n], fast_tau(n)
    print(f"  n={n}: σ+φ={s+ph}, 2n+τ={2*n+t} | {fstr}")

# ============================================================
# BONUS 3: Systematic search for Ω in multiplicative identities
# ============================================================
print("\n" + "=" * 70)
print("BONUS 3: Systematic Ω identity search (n ≤ 10000)")
print("=" * 70)

identities = {
    "σ = n + Ω": lambda n, s, t, p, w, O: s == n + O,
    "σ = n·Ω": lambda n, s, t, p, w, O: s == n * O,
    "φ + Ω = n": lambda n, s, t, p, w, O: p + O == n,
    "τ = 2·Ω": lambda n, s, t, p, w, O: t == 2 * O,
    "τ = Ω + 1": lambda n, s, t, p, w, O: t == O + 1,
    "τ = Ω²": lambda n, s, t, p, w, O: t == O * O,
    "σ = τ·Ω": lambda n, s, t, p, w, O: s == t * O,
    "σ = φ + τ·Ω": lambda n, s, t, p, w, O: s == p + t * O,
    "σ·Ω = φ·τ": lambda n, s, t, p, w, O: s * O == p * t,
    "n = σ·Ω/τ": lambda n, s, t, p, w, O: t != 0 and (s * O) % t == 0 and n == s * O // t,
    "σ - φ = τ·Ω": lambda n, s, t, p, w, O: s - p == t * O,
    "σ + φ = n·Ω": lambda n, s, t, p, w, O: s + p == n * O,
    "σ·φ = n·τ·Ω": lambda n, s, t, p, w, O: s * p == n * t * O,
    "σ·ω = n·Ω": lambda n, s, t, p, w, O: s * w == n * O,
    "φ·Ω = n - σ + τ": lambda n, s, t, p, w, O: p * O == n - s + t,
    "σ² = n·τ·Ω": lambda n, s, t, p, w, O: s * s == n * t * O,
    "Ω = log₂(τ)": lambda n, s, t, p, w, O: (t & (t-1)) == 0 and t > 0 and O == t.bit_length() - 1,
}

for name, test in identities.items():
    sols = []
    for n in range(2, LIMIT_SMALL):
        s = fast_sigma(n)
        t = fast_tau(n)
        p = phi_arr[n]
        w = fast_omega(n)
        O = fast_Omega(n)
        try:
            if test(n, s, t, p, w, O):
                sols.append(n)
        except:
            pass

    if 0 < len(sols) <= 200:
        tag = "*** FINITE? ***" if len(sols) < 20 else ""
        print(f"\n{name}: {len(sols)} solutions {tag}")
        if len(sols) <= 30:
            print(f"  {sols}")
        else:
            print(f"  First 30: {sols[:30]}")
        # Show details for first few
        for n in sols[:5]:
            f = fast_factorint(n)
            fstr = " × ".join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(f.items()))
            s, t, ph, w, O = fast_sigma(n), fast_tau(n), phi_arr[n], fast_omega(n), fast_Omega(n)
            print(f"    n={n}: σ={s}, τ={t}, φ={ph}, ω={w}, Ω={O} | {fstr}")
    elif len(sols) == 0:
        print(f"\n{name}: 0 solutions")
    else:
        print(f"\n{name}: {len(sols)} solutions (>200, probably infinite)")
        print(f"  First 10: {sols[:10]}")

print(f"\n\nTotal computation time: {time.time()-t0:.1f}s")
print("\nDone.")
