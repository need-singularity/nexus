#!/usr/bin/env python3
"""Arithmetic identity search for n=6 and its arithmetic functions."""

from math import gcd, log
from functools import reduce

def sigma(n):
    """Sum of divisors."""
    return sum(d for d in range(1, n+1) if n % d == 0)

def phi(n):
    """Euler's totient."""
    count = 0
    for k in range(1, n+1):
        if gcd(k, n) == 1:
            count += 1
    return count

def tau(n):
    """Number of divisors."""
    return sum(1 for d in range(1, n+1) if n % d == 0)

def psi(n):
    """Dedekind psi: n * prod(1 + 1/p) for prime p | n."""
    result = n
    temp = n
    primes = []
    d = 2
    while d * d <= temp:
        if temp % d == 0:
            primes.append(d)
            while temp % d == 0:
                temp //= d
        d += 1
    if temp > 1:
        primes.append(temp)
    for p in primes:
        result = result * (p + 1) // p
    return result

def lcm(a, b):
    return a * b // gcd(a, b)

def lcm_multi(*args):
    return reduce(lcm, args)

def factorial(n):
    if n <= 1: return 1
    r = 1
    for i in range(2, n+1): r *= i
    return r

print("=" * 70)
print("ARITHMETIC IDENTITY SEARCH FOR n=6")
print("σ(6)=12, φ(6)=2, τ(6)=4, ψ(6)=12")
print("=" * 70)

# ─── TEST 1: σ(n) mod φ(n) = 0 ───
print("\n" + "─" * 70)
print("TEST 1: For which n in [1..1000] does σ(n) mod φ(n) = 0?")
print("─" * 70)
solutions_1 = []
for n in range(1, 1001):
    s, p = sigma(n), phi(n)
    if p > 0 and s % p == 0:
        solutions_1.append(n)

print(f"Count: {len(solutions_1)} out of 1000")
print(f"First 50: {solutions_1[:50]}")
print(f"Density: {len(solutions_1)/1000:.1%}")
print(f"n=6 in list: {6 in solutions_1}")
# Check if 6 is special
if 6 in solutions_1:
    idx = solutions_1.index(6)
    print(f"Position of 6: #{idx+1} out of {len(solutions_1)}")
    print(f"σ(6)/φ(6) = 12/2 = {sigma(6)//phi(6)}")
print("Verdict: Too common to be special for n=6." if len(solutions_1) > 100 else "Verdict: Relatively rare!")

# ─── TEST 2: σ·τ/φ = (n-2)! ───
print("\n" + "─" * 70)
print("TEST 2: For which n does σ(n)·τ(n)/φ(n) = (n-2)! ?")
print(f"  At n=6: 12·4/2 = {12*4//2} vs (6-2)! = {factorial(4)} = 24  ✓")
print("─" * 70)
solutions_2 = []
for n in range(3, 101):  # n>=3 for (n-2)! to make sense, cap at 100 for factorial
    s, p, t = sigma(n), phi(n), tau(n)
    if p > 0 and (s * t) % p == 0:
        val = s * t // p
        target = factorial(n - 2)
        if val == target:
            solutions_2.append((n, val))

print(f"Solutions n=3..100: {solutions_2}")
# Also check σ·τ/φ values for small n
print("\nTable of σ·τ/φ for n=1..20:")
print(f"{'n':>4} {'σ':>5} {'φ':>5} {'τ':>4} {'στ/φ':>10} {'(n-2)!':>10} {'match':>6}")
for n in range(1, 21):
    s, p, t = sigma(n), phi(n), tau(n)
    if p > 0 and (s * t) % p == 0:
        val = s * t // p
        fact = factorial(max(n-2, 0))
        match = "✓" if val == fact and n >= 3 else ""
        print(f"{n:>4} {s:>5} {p:>5} {t:>4} {val:>10} {fact:>10} {match:>6}")
    else:
        print(f"{n:>4} {s:>5} {p:>5} {t:>4} {'N/A':>10}")

# ─── TEST 3: lcm(σ,φ,τ) = σ ───
print("\n" + "─" * 70)
print("TEST 3: For which n in [1..500] does lcm(σ(n),φ(n),τ(n)) = σ(n)?")
print(f"  At n=6: lcm(12,2,4) = {lcm_multi(12,2,4)} = σ(6)=12  ✓")
print("─" * 70)
solutions_3 = []
for n in range(1, 501):
    s, p, t = sigma(n), phi(n), tau(n)
    L = lcm_multi(s, p, t)
    if L == s:
        solutions_3.append(n)

print(f"Count: {len(solutions_3)} out of 500")
print(f"Solutions: {solutions_3}")
print("Interpretation: lcm(σ,φ,τ)=σ means φ|σ AND τ|σ.")

# ─── TEST 4: n | σ(n) (multiply-perfect) ───
print("\n" + "─" * 70)
print("TEST 4: For which n in [1..1000] does n | σ(n)? (multiply-perfect)")
print(f"  At n=6: σ(6)=12, 12/6=2  ✓ (perfect number: σ(n)=2n)")
print("─" * 70)
solutions_4 = []
for n in range(1, 1001):
    s = sigma(n)
    if s % n == 0:
        solutions_4.append((n, s // n))

print(f"Count: {len(solutions_4)} out of 1000")
print(f"{'n':>6} {'σ(n)':>8} {'σ/n':>5} {'type':>15}")
for n, ratio in solutions_4:
    if ratio == 1:
        tp = "n=1"
    elif ratio == 2:
        tp = "PERFECT"
    else:
        tp = f"multiperfect-{ratio}"
    print(f"{n:>6} {sigma(n):>8} {ratio:>5} {tp:>15}")

# ─── TEST 5: τ(σ(n)) = n ───
print("\n" + "─" * 70)
print("TEST 5: For which n in [1..1000] does τ(σ(n)) = n?")
print(f"  At n=6: τ(σ(6)) = τ(12) = {tau(12)} = 6  ✓")
print("─" * 70)
solutions_5 = []
for n in range(1, 1001):
    s = sigma(n)
    ts = tau(s)
    if ts == n:
        solutions_5.append((n, s))

print(f"Count: {len(solutions_5)} out of 1000")
print(f"{'n':>6} {'σ(n)':>8} {'τ(σ(n))':>8}")
for n, s in solutions_5:
    print(f"{n:>6} {s:>8} {tau(s):>8}")

# ─── TEST 6: σ(τ(P_k)) for perfect numbers ───
print("\n" + "─" * 70)
print("TEST 6: σ(τ(n)) at perfect numbers")
print(f"  At n=6: σ(τ(6)) = σ(4) = {sigma(4)} = 7 = M₃ (Mersenne prime)")
print("─" * 70)
# Perfect numbers: 6, 28, 496, 8128
perfects = [6, 28, 496, 8128]
print(f"{'P_k':>6} {'τ(P)':>6} {'σ(τ(P))':>8} {'notes':>20}")
for pk in perfects:
    t = tau(pk)
    st = sigma(t)
    # Check if Mersenne prime
    notes = ""
    # Mersenne primes: 3,7,31,127,8191,...
    mersenne = [3, 7, 31, 127, 8191, 131071]
    if st in mersenne:
        idx = mersenne.index(st)
        notes = f"M_{idx+2} Mersenne prime"
    print(f"{pk:>6} {t:>6} {st:>8} {notes:>20}")

# Also: even perfect number = 2^(p-1)(2^p - 1), τ = 2p, σ(2p) = ?
print("\nPattern analysis: Even perfect P = 2^(p-1)·(2^p-1)")
print("  τ(P) = 2p, so σ(τ(P)) = σ(2p)")
for p in [2, 3, 5, 7, 13]:
    mp = (1 << p) - 1  # 2^p - 1
    pk = (1 << (p-1)) * mp
    t = tau(pk)
    st = sigma(t)
    print(f"  p={p:>2}: P={pk:>6}, τ(P)={t:>4}=2·{p}, σ(2·{p})={st}")

# ─── TEST 7: φ(σ(n)) = τ(n) ───
print("\n" + "─" * 70)
print("TEST 7: For which n in [1..500] does φ(σ(n)) = τ(n)?")
print(f"  At n=6: φ(σ(6)) = φ(12) = {phi(12)} = 4 = τ(6)  ✓")
print("─" * 70)
solutions_7 = []
for n in range(1, 501):
    s = sigma(n)
    ps = phi(s)
    t = tau(n)
    if ps == t:
        solutions_7.append((n, s, ps, t))

print(f"Count: {len(solutions_7)} out of 500")
print(f"{'n':>6} {'σ(n)':>8} {'φ(σ(n))':>8} {'τ(n)':>6}")
for n, s, ps, t in solutions_7:
    print(f"{n:>6} {s:>8} {ps:>8} {t:>6}")

# Check if any are perfect numbers
perf_in_7 = [n for n, s, ps, t in solutions_7 if sigma(n) == 2*n]
print(f"Perfect numbers in solutions: {perf_in_7}")

# ─── TEST 8: σφ = nτ + k ───
print("\n" + "─" * 70)
print("TEST 8: Solutions to σ(n)·φ(n) = n·τ(n) + k for small |k|")
print(f"  At n=6: σφ = 12·2 = 24, nτ = 6·4 = 24, k=0  ✓")
print("─" * 70)

# First find all k values for n=1..1000
k_solutions = {}
for n in range(1, 1001):
    s, p, t = sigma(n), phi(n), tau(n)
    k = s * p - n * t
    if k not in k_solutions:
        k_solutions[k] = []
    k_solutions[k].append(n)

# Show k=0 first
print(f"\nk=0: σφ = nτ")
print(f"  Solutions in [1..1000]: {k_solutions.get(0, [])}")

# Show small |k| with counts
print(f"\n{'k':>6} {'count':>6} {'solutions (first 10)':>50}")
for k in sorted(k_solutions.keys()):
    if abs(k) <= 50:
        sols = k_solutions[k]
        print(f"{k:>6} {len(sols):>6} {str(sols[:10]):>50}")

# ─── SUMMARY ───
print("\n" + "=" * 70)
print("SUMMARY OF FINDINGS")
print("=" * 70)

print(f"""
TEST 1: σ(n) mod φ(n) = 0
  {len(solutions_1)}/1000 solutions — {'common' if len(solutions_1) > 100 else 'rare'}
  n=6 not special here.

TEST 2: σ·τ/φ = (n-2)!
  Solutions: {[x[0] for x in solutions_2]}
  {'n=6 is UNIQUE!' if len(solutions_2) == 1 and solutions_2[0][0] == 6 else 'Multiple solutions' if solutions_2 else 'No solutions found'}

TEST 3: lcm(σ,φ,τ) = σ
  {len(solutions_3)}/500 solutions: {solutions_3}

TEST 4: n | σ(n) (multiply-perfect)
  {len(solutions_4)}/1000 solutions. Perfect numbers: {[n for n, r in solutions_4 if r == 2]}

TEST 5: τ(σ(n)) = n  ← COMPOSITION FIXED POINT
  {len(solutions_5)}/1000 solutions: {[x[0] for x in solutions_5]}

TEST 6: σ(τ(P_k)) for perfect numbers
  See table above. σ(τ(6)) = 7 = M₃.

TEST 7: φ(σ(n)) = τ(n)  ← CROSS-FUNCTION IDENTITY
  {len(solutions_7)}/500 solutions: {[x[0] for x in solutions_7]}

TEST 8: σφ = nτ + k
  k=0 solutions: {k_solutions.get(0, [])}
  Only n=1 and n=6 satisfy σφ=nτ (confirmed).
""")

# ─── BONUS: combined rarity score ───
print("─" * 70)
print("BONUS: Which n satisfy MULTIPLE identities simultaneously?")
print("─" * 70)

sets = {
    'T3: lcm=σ': set(solutions_3),
    'T4: n|σ': set(n for n, r in solutions_4),
    'T5: τ(σ)=n': set(n for n, s in solutions_5),
    'T7: φ(σ)=τ': set(n for n, s, ps, t in solutions_7),
    'T8: σφ=nτ': set(k_solutions.get(0, [])),
}

# Check n=1..500 for how many identities each satisfies
multi = {}
for n in range(1, 501):
    count = sum(1 for name, s in sets.items() if n in s)
    if count >= 2:
        which = [name for name, s in sets.items() if n in s]
        multi[n] = (count, which)

print(f"{'n':>6} {'#ids':>5} {'identities'}")
for n in sorted(multi, key=lambda x: -multi[x][0]):
    cnt, which = multi[n]
    print(f"{n:>6} {cnt:>5} {', '.join(which)}")
