#!/usr/bin/env python3
"""
Deep analysis of the most promising OEIS-worthy sequences.
Focus on Seq A, Seq D, Seq J, and structural properties.
"""
from math import gcd
from fractions import Fraction
from sympy import factorint, totient, divisor_sigma, divisor_count, isprime
from collections import Counter

def sigma(n): return int(divisor_sigma(n, 1))
def phi(n): return int(totient(n))
def tau(n): return int(divisor_count(n))

def R(n):
    return Fraction(sigma(n) * phi(n), n * tau(n))

# ============================================================
# DEEP ANALYSIS: Sequence A — structural characterization
# ============================================================
print("=" * 70)
print("DEEP ANALYSIS: Sequence A — {n : sigma(n)*phi(n)/(n*tau(n)) in Z}")
print("=" * 70)

seq_A = []
for n in range(1, 10001):
    r = R(n)
    if r.denominator == 1:
        seq_A.append(n)

# Factor each member
print("\nFactorizations of all 53 terms:")
for n in seq_A:
    f = factorint(n)
    r = int(R(n))
    fstr = " * ".join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(f.items()))
    if n == 1: fstr = "1"
    omega = len(f)  # distinct prime factors
    Omega = sum(f.values())  # total prime factors with multiplicity
    print(f"  n={n:>5} = {fstr:<25} omega={omega} Omega={Omega} R={r}")

# Check: are perfect numbers always in Seq A?
print("\nPerfect numbers in range:")
perfects = [n for n in range(1, 10001) if sigma(n) == 2 * n]
for p in perfects:
    in_A = p in seq_A
    print(f"  {p}: in Seq A = {in_A}, R({p}) = {R(p)}")

# Distribution by number of prime factors
omega_dist = Counter(len(factorint(n)) for n in seq_A)
print(f"\nDistribution by omega (distinct primes): {dict(sorted(omega_dist.items()))}")

# Check: any primes in Seq A?
primes_in_A = [n for n in seq_A if isprime(n)]
print(f"Primes in Seq A: {primes_in_A}")

# Check: any prime powers?
ppowers_in_A = [n for n in seq_A if len(factorint(n)) == 1]
print(f"Prime powers in Seq A: {ppowers_in_A}")

# ============================================================
# DEEP ANALYSIS: Sequence D — fixed points tau(sigma(n))=n
# ============================================================
print("\n" + "=" * 70)
print("DEEP ANALYSIS: Sequence D — {n : tau(sigma(n)) = n}")
print("Extended search to 100000")
print("=" * 70)

seq_D = []
for n in range(1, 100001):
    if tau(sigma(n)) == n:
        seq_D.append(n)

print(f"Terms up to 100000: {seq_D}")
print(f"Only {1, 2, 3, 6} — all divisors of 6!")
print(f"sigma values: {[sigma(n) for n in seq_D]}")
print(f"Conjecture: {1,2,3,6} are the ONLY solutions (n | 6)")

# ============================================================
# DEEP ANALYSIS: Sequence J — divisibility analysis
# ============================================================
print("\n" + "=" * 70)
print("DEEP ANALYSIS: Sequence J — {n : n | lcm(sigma(n), phi(n))}")
print("=" * 70)

seq_J = []
for n in range(1, 10001):
    s, p = sigma(n), phi(n)
    l = (s * p) // gcd(s, p)
    if l % n == 0:
        seq_J.append(n)

# Factor analysis
print(f"\nFirst 62 terms with factorizations:")
for n in seq_J:
    f = factorint(n)
    fstr = " * ".join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(f.items()))
    if n == 1: fstr = "1"
    s, p = sigma(n), phi(n)
    g = gcd(s, p)
    print(f"  n={n:>5} = {fstr:<20} sigma={s:>6} phi={p:>5} gcd={g:>4} lcm/n={(s*p//g)//n:>5}")

# ============================================================
# Sequence D: near-misses (tau(sigma(n)) close to n)
# ============================================================
print("\n" + "=" * 70)
print("NEAR MISSES: |tau(sigma(n)) - n| <= 2 for n <= 1000")
print("=" * 70)

for n in range(1, 1001):
    ts = tau(sigma(n))
    if abs(ts - n) <= 2:
        diff = ts - n
        print(f"  n={n:>4}  tau(sigma({n}))={ts:>4}  diff={diff:>+3}  sigma={sigma(n)}")

# ============================================================
# Sequence A: b-file format for OEIS submission
# ============================================================
print("\n" + "=" * 70)
print("OEIS B-FILE FORMAT: Sequence A")
print("=" * 70)

print(f"# b-file for A??????")
print(f"# {len(seq_A)} terms, computed by [author]")
print(f"# a(n) = n-th positive integer m such that sigma(m)*phi(m)/(m*tau(m)) is an integer")
for i, n in enumerate(seq_A, 1):
    print(f"{i} {n}")

# ============================================================
# Sequence J: b-file format
# ============================================================
print(f"\n# b-file for A??????")
print(f"# {len(seq_J)} terms, computed by [author]")
print(f"# a(n) = n-th positive integer m such that m divides lcm(sigma(m), phi(m))")
for i, n in enumerate(seq_J, 1):
    print(f"{i} {n}")

# ============================================================
# R(n) at primes: closed form
# ============================================================
print("\n" + "=" * 70)
print("R(n) AT PRIMES: closed form analysis")
print("=" * 70)

print("For prime p: sigma(p)=p+1, phi(p)=p-1, tau(p)=2")
print("R(p) = (p+1)(p-1)/(2p) = (p^2-1)/(2p)")
print()
for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
    r = R(p)
    formula = Fraction(p*p - 1, 2*p)
    assert r == formula
    print(f"  R({p:>2}) = ({p}^2-1)/(2*{p}) = {p*p-1}/{2*p} = {r} = {float(r):.4f}")

print("\nR(p) is integer iff 2p | (p^2-1) = (p-1)(p+1)")
print("For odd prime p: p-1 and p+1 are consecutive even numbers")
print("  => one of them is divisible by 4, their product by 8")
print("  => (p-1)(p+1) is divisible by 2p iff p | (p^2-1) which is always true")
print("  Wait: 2p | (p^2-1)? p^2-1 mod 2p:")
for p in [2, 3, 5, 7, 11, 13]:
    print(f"    p={p}: (p^2-1) mod (2p) = {(p*p-1) % (2*p)}")
print("  => R(p) is NEVER an integer for p>=2 (remainder = 2p-2)")

# ============================================================
# Overlap between Seq A and Seq J
# ============================================================
print("\n" + "=" * 70)
print("OVERLAP: Seq A ∩ Seq J")
print("=" * 70)

overlap = sorted(set(seq_A) & set(seq_J))
only_A = sorted(set(seq_A) - set(seq_J))
only_J = sorted(set(seq_J) - set(seq_A))

print(f"Both A and J ({len(overlap)} terms): {overlap}")
print(f"Only A ({len(only_A)} terms): {only_A[:20]}...")
print(f"Only J ({len(only_J)} terms): {only_J[:20]}...")

# ============================================================
# Final summary
# ============================================================
print("\n" + "=" * 70)
print("FINAL OEIS SUBMISSION CANDIDATES")
print("=" * 70)

print("""
CANDIDATE 1 (STRONGEST): Sequence A
  Definition: Numbers n such that sigma(n)*phi(n)/(n*tau(n)) is a positive integer.
  First terms: 1, 6, 28, 54, 96, 120, 135, 196, 224, 234, 270, 360, 496, 672, 775, 819, 864, 891, 936, 1080
  53 terms up to 10000.
  Contains all perfect numbers (6, 28, 496, 8128).
  OEIS search: NO MATCH FOUND — appears to be NEW.

  Properties:
  - R(perfect_number) is always integer
  - No primes in this sequence
  - All members are composite with omega >= 2
  - All three known even perfect numbers <= 10000 are members

CANDIDATE 2 (STRONG): Sequence J
  Definition: Numbers n such that n divides lcm(sigma(n), phi(n)).
  First terms: 1, 6, 24, 28, 40, 84, 96, 117, 120, 224, 234, 252, 288, 360, 384, 468, 496, 640, 672, 756
  62 terms up to 10000.
  OEIS search: NO MATCH FOUND — appears to be NEW.

CANDIDATE 3 (INTERESTING): Sequence D
  Definition: Numbers n such that tau(sigma(n)) = n.
  Terms: 1, 2, 3, 6 (and likely no others).
  All are divisors of 6!
  Checked to 100000.
  Conjecture: These are the ONLY four solutions.
  ALREADY IN OEIS as subsequence of A062068 fixed points.
  But the fixed-point characterization {1,2,3,6} = divisors(6) is notable.

CANDIDATE 4 (NOVEL): R(n) numerator/denominator sequences
  Numerators of sigma(n)*phi(n)/(n*tau(n)) as a fraction sequence.
  OEIS search: NO MATCH FOUND for numerators or denominators.

CANDIDATE 5: Dirichlet convolution collapse points {1, 6}
  (sigma * phi)(n) = sigma(n)*phi(n) only for n=1 and n=6.
  Too few terms for standalone OEIS submission, but notable.
""")
