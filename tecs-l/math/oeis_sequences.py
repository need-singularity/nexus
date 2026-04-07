#!/usr/bin/env python3
"""
Generate OEIS-worthy sequences from R(n) = sigma*phi/(n*tau) and related functions.
"""

from math import gcd, isqrt
from fractions import Fraction
from collections import defaultdict
import sympy
from sympy import factorint, totient, divisor_sigma, divisor_count, mobius, lcm as sym_lcm
from sympy.ntheory import isprime

def sigma(n):
    return int(divisor_sigma(n, 1))

def phi(n):
    return int(totient(n))

def tau(n):
    return int(divisor_count(n))

def mu(n):
    return int(mobius(n))

def R(n):
    """R(n) = sigma(n)*phi(n) / (n*tau(n)) as a Fraction."""
    return Fraction(sigma(n) * phi(n), n * tau(n))

def D(n):
    """D(n) = sigma(n)*phi(n)/tau(n) - n^2/tau(n) = (sigma*phi - n^2)/tau."""
    s, p, t = sigma(n), phi(n), tau(n)
    return Fraction(s * p - n * n, t)

def arithmetic_derivative(n):
    """n' = arithmetic derivative of n."""
    if n <= 1:
        return 0
    f = factorint(n)
    result = 0
    for p, e in f.items():
        result += n * e // p
    return result

def L(n):
    """L(n) = lcm(sigma(n), phi(n))."""
    s, p = sigma(n), phi(n)
    return (s * p) // gcd(s, p)

print("=" * 70)
print("OEIS SEQUENCE GENERATOR — R(n) and related number-theoretic functions")
print("=" * 70)

# ============================================================
# Sequence A: {n : R(n) is an integer} for n=1..10000
# ============================================================
print("\n" + "=" * 70)
print("SEQUENCE A: {n : R(n) = sigma(n)*phi(n)/(n*tau(n)) is an integer}")
print("=" * 70)

seq_A = []
for n in range(1, 10001):
    r = R(n)
    if r.denominator == 1:
        seq_A.append(n)

print(f"Count: {len(seq_A)} terms for n <= 10000")
print(f"Terms: {seq_A[:60]}")
if len(seq_A) > 60:
    print(f"  ... ({len(seq_A) - 60} more terms)")

# Show R(n) values for the first hits
print("\nFirst 30 with R(n) values:")
for n in seq_A[:30]:
    r = R(n)
    print(f"  n={n:>5}  R(n)={int(r):>6}  sigma={sigma(n):>6}  phi={phi(n):>6}  tau={tau(n):>3}")

# ============================================================
# Sequence B: {n : D(n) <= k}
# ============================================================
print("\n" + "=" * 70)
print("SEQUENCE B: a(k) = |{n <= 10000 : |D(n)| <= k}| for k=0,1,2,...")
print("Also: {n : D(n) = 0}")
print("=" * 70)

D_vals = {}
for n in range(1, 10001):
    D_vals[n] = D(n)

d_zero = [n for n in range(1, 10001) if D_vals[n] == 0]
print(f"D(n) = 0: {d_zero}")

# Count for small k
print("\n|{n<=10000 : |D(n)| <= k}|:")
for k in range(11):
    count = sum(1 for n in range(1, 10001) if abs(D_vals[n]) <= k)
    members = [n for n in range(1, 10001) if abs(D_vals[n]) <= k]
    if len(members) <= 20:
        print(f"  k={k:>2}: count={count:>4}  members={members}")
    else:
        print(f"  k={k:>2}: count={count:>4}  first 15: {members[:15]}...")

# ============================================================
# Sequence C: {R(n) for n=1,2,3,...} as fractions
# ============================================================
print("\n" + "=" * 70)
print("SEQUENCE C: R(n) = sigma(n)*phi(n)/(n*tau(n)) for n=1..50")
print("=" * 70)

print(f"{'n':>4} {'sigma':>6} {'phi':>6} {'tau':>4} {'R(n)':>15}  {'decimal':>10}")
print("-" * 55)
for n in range(1, 51):
    r = R(n)
    s, p, t = sigma(n), phi(n), tau(n)
    print(f"{n:>4} {s:>6} {p:>6} {t:>4} {str(r):>15}  {float(r):>10.6f}")

# ============================================================
# Sequence D: {n : tau(sigma(n)) = n}
# ============================================================
print("\n" + "=" * 70)
print("SEQUENCE D: {n : tau(sigma(n)) = n}")
print("=" * 70)

seq_D = []
for n in range(1, 10001):
    if tau(sigma(n)) == n:
        seq_D.append(n)

print(f"Terms up to 10000: {seq_D}")
for n in seq_D:
    print(f"  n={n}: sigma({n})={sigma(n)}, tau({sigma(n)})={tau(sigma(n))}")

# Also check: tau(sigma(n)) values as a sequence
print("\nFirst 40 values of tau(sigma(n)):")
ts_vals = [tau(sigma(n)) for n in range(1, 41)]
print(f"  {ts_vals}")

# ============================================================
# Sequence E: {n : mu(n)*sigma(n) = 2n}
# ============================================================
print("\n" + "=" * 70)
print("SEQUENCE E: {n : mu(n)*sigma(n) = 2n}")
print("=" * 70)

seq_E = []
for n in range(1, 10001):
    if mu(n) * sigma(n) == 2 * n:
        seq_E.append(n)
        print(f"  n={n}: mu={mu(n)}, sigma={sigma(n)}, 2n={2*n}")

print(f"Terms up to 10000: {seq_E}")

# ============================================================
# Sequence F: {n : phi(n)^2 = tau(n)*n}  (corrected: phi^2 = tau*n? or phi^2=tau?)
# Actually: {n : phi(n)^2 = tau(n)}
# ============================================================
print("\n" + "=" * 70)
print("SEQUENCE F: {n : phi(n)^2 = tau(n)}")
print("=" * 70)

seq_F = []
for n in range(1, 100001):
    if phi(n) ** 2 == tau(n):
        seq_F.append(n)

print(f"Terms up to 100000: {seq_F}")
for n in seq_F:
    print(f"  n={n}: phi={phi(n)}, tau={tau(n)}, phi^2={phi(n)**2}")

# ============================================================
# Sequence G: D-spectrum (sorted distinct values of D(n))
# ============================================================
print("\n" + "=" * 70)
print("SEQUENCE G: D-spectrum — sorted distinct values of D(n) for n=1..10000")
print("=" * 70)

d_set = set()
for n in range(1, 10001):
    d = D_vals[n]
    if d.denominator == 1:
        d_set.add(int(d))

d_sorted = sorted(d_set)
print(f"Number of distinct integer D(n) values: {len(d_sorted)}")
print(f"First 50 non-negative: {[x for x in d_sorted if x >= 0][:50]}")
print(f"First 30 negative: {sorted([x for x in d_sorted if x < 0], key=lambda x: -x)[:30]}")

# Also: which D(n) are non-integer?
non_int_d = [(n, D_vals[n]) for n in range(1, 101) if D_vals[n].denominator != 1]
print(f"\nNon-integer D(n) for n<=100: {len(non_int_d)} cases")
for n, d in non_int_d[:20]:
    print(f"  D({n}) = {d} = {float(d):.4f}")

# ============================================================
# Sequence H: {n : sigma(n) = 2*lcm(prime_factors(n))}
# ============================================================
print("\n" + "=" * 70)
print("SEQUENCE H: {n : sigma(n) = 2*lcm(prime factors of n)}")
print("=" * 70)

seq_H = []
for n in range(1, 10001):
    f = factorint(n)
    primes = list(f.keys())
    if not primes:
        lp = 1
    elif len(primes) == 1:
        lp = primes[0]
    else:
        from functools import reduce
        from math import lcm as math_lcm
        lp = reduce(math_lcm, primes)
    if sigma(n) == 2 * lp:
        seq_H.append(n)
        print(f"  n={n}: sigma={sigma(n)}, primes={primes}, lcm={lp}")

print(f"Terms up to 10000: {seq_H}")

# ============================================================
# Sequence I: {n : n' = n-1} (arithmetic derivative)
# ============================================================
print("\n" + "=" * 70)
print("SEQUENCE I: {n : n' = n-1} (arithmetic derivative)")
print("Known: A054377 — primary pseudoperfect numbers")
print("=" * 70)

seq_I = []
for n in range(1, 100001):
    if arithmetic_derivative(n) == n - 1:
        seq_I.append(n)

print(f"Terms up to 100000: {seq_I}")
print("Known A054377: 2, 6, 42, 1806, 47058, ...")

# ============================================================
# Sequence J: {n : L(n)/n is a positive integer}
# L(n) = lcm(sigma(n), phi(n))
# ============================================================
print("\n" + "=" * 70)
print("SEQUENCE J: {n : lcm(sigma(n), phi(n)) / n is a positive integer}")
print("=" * 70)

seq_J = []
for n in range(1, 10001):
    ln = L(n)
    if ln % n == 0:
        k = ln // n
        seq_J.append((n, k))

print(f"Count up to 10000: {len(seq_J)}")
print(f"Terms (n, L(n)/n):")
for n, k in seq_J[:40]:
    print(f"  n={n:>5}  L(n)/n={k:>5}  sigma={sigma(n):>6}  phi={phi(n):>6}  L(n)={L(n):>8}")

seq_J_ns = [n for n, k in seq_J]
print(f"\nJust the n values (first 40): {seq_J_ns[:40]}")

# ============================================================
# Sequence K: convolution collapse points
# (sigma * phi)(n) = sigma(n) * phi(n) where * is Dirichlet convolution
# ============================================================
print("\n" + "=" * 70)
print("SEQUENCE K: Dirichlet convolution (sigma * phi)(n) vs sigma(n)*phi(n)")
print("=" * 70)

def dirichlet_conv_sigma_phi(n):
    """(sigma * phi)(n) = sum_{d|n} sigma(d) * phi(n/d)."""
    total = 0
    for d in range(1, n + 1):
        if n % d == 0:
            total += sigma(d) * phi(n // d)
    return total

seq_K = []
print(f"{'n':>4} {'(s*p)(n)':>10} {'s(n)*p(n)':>10} {'equal':>6}")
print("-" * 40)
for n in range(1, 101):
    conv = dirichlet_conv_sigma_phi(n)
    prod = sigma(n) * phi(n)
    eq = conv == prod
    if n <= 30 or eq:
        print(f"{n:>4} {conv:>10} {prod:>10} {'YES' if eq else '':>6}")
    if eq:
        seq_K.append(n)

# Extend to 500 (slower)
print("\nExtending to n=500...")
for n in range(101, 501):
    conv = dirichlet_conv_sigma_phi(n)
    prod = sigma(n) * phi(n)
    if conv == prod:
        seq_K.append(n)
        print(f"  n={n}: match!")

print(f"\nConvolution collapse points up to 500: {seq_K}")

# ============================================================
# BONUS: Additional potentially OEIS-worthy sequences
# ============================================================
print("\n" + "=" * 70)
print("BONUS SEQUENCES")
print("=" * 70)

# B1: {n : sigma(n) * phi(n) = n^2} (known: n=1 and all primes)
print("\n--- B1: {n : sigma(n)*phi(n) mod n^2 = 0, not prime} ---")
seq_B1 = []
for n in range(1, 10001):
    sp = sigma(n) * phi(n)
    if sp % (n * n) == 0 and not isprime(n):
        seq_B1.append(n)
print(f"Terms: {seq_B1[:40]}")

# B2: R(n) numerators and denominators
print("\n--- B2: Numerator of R(n) for n=1..40 ---")
nums = [R(n).numerator for n in range(1, 41)]
dens = [R(n).denominator for n in range(1, 41)]
print(f"Numerators:   {nums}")
print(f"Denominators: {dens}")

# B3: {n : R(n) = R(n+1)}
print("\n--- B3: {n : R(n) = R(n+1)} ---")
seq_B3 = []
for n in range(1, 10000):
    if R(n) == R(n + 1):
        seq_B3.append(n)
        print(f"  R({n}) = R({n+1}) = {R(n)}")
print(f"Terms: {seq_B3}")

# B4: Record values of R(n)
print("\n--- B4: Record values of R(n) (new maximum) ---")
max_r = Fraction(0)
records = []
for n in range(1, 1001):
    r = R(n)
    if r > max_r:
        max_r = r
        records.append((n, r))

print(f"First 20 records:")
for n, r in records[:20]:
    print(f"  n={n:>5}  R(n)={str(r):>15} = {float(r):.6f}")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("SUMMARY FOR OEIS SUBMISSION")
print("=" * 70)

print(f"""
Sequence A: {{n : R(n) is integer}}
  First terms: {seq_A[:20]}
  Total up to 10000: {len(seq_A)}
  STATUS: {'POTENTIALLY NEW' if len(seq_A) > 2 else 'TOO SHORT'}

Sequence D: {{n : tau(sigma(n)) = n}}
  Terms: {seq_D}
  STATUS: {'Check A-number' if seq_D else 'EMPTY'}

Sequence F: {{n : phi(n)^2 = tau(n)}}
  Terms: {seq_F}
  STATUS: {'POTENTIALLY NEW' if len(seq_F) >= 2 else 'TOO SHORT'}

Sequence J: {{n : n | lcm(sigma(n), phi(n))}}
  First terms: {seq_J_ns[:20]}
  Total up to 10000: {len(seq_J_ns)}
  STATUS: POTENTIALLY NEW

Sequence K: Dirichlet convolution collapse points
  Terms: {seq_K}
  STATUS: {'POTENTIALLY NEW' if len(seq_K) >= 2 else 'TOO SHORT'}

R(n) numerators: {nums[:15]}
R(n) denominators: {dens[:15]}
""")

print("\nDone!")
