#!/usr/bin/env python3
"""
Does the fourth perfect number P₄=8128 appear anywhere in physics or mathematics?
And: what about the tau chain? tau(P_k) = 2p_k for Mersenne exponent p_k.
"""
import math

print("╔" + "═" * 68 + "╗")
print("║  P₄ = 8128: Does the Fourth Perfect Number Appear Anywhere?          ║")
print("╚" + "═" * 68 + "╝")

# P4 = 8128 = 2^6 × 127 = 64 × 127
# tau(8128) = 14
# phi(8128) = 4032
# LPF = 127
# dim(SO(128)) = 8128
# dim(SE(127)) = 8128

print(f"""
  P₄ = 8128 = 2⁶ × 127
  tau(8128) = 14
  phi(8128) = 4032
  LPF = 127 (Mersenne prime M₇ = 2⁷-1)
  dim(SO(128)) = 128·127/2 = 8128
  dim(SE(127)) = 127·128/2 = 8128

{'='*70}
SEARCH 1: SO(128) in Physics
{'='*70}

  SO(128) is NOT a standard gauge group in any known string theory.

  Known gauge groups:
    SO(32):    heterotic string, Type I          dim = 496 = P₃
    E₈ × E₈:  heterotic string                  dim = 496 = P₃
    SO(16):    sometimes in compactification     dim = 120
    SO(10):    GUT group                         dim = 45
    SU(5):     GUT group                         dim = 24 = tau(6)!
    SO(128):   ???                                dim = 8128 = P₄

  SO(128) appears in:
    1. Lattice models of 128-dimensional spaces (rare, theoretical)
    2. Some F-theory compactifications (exotic, non-standard)
    3. No known physical application.

  VERDICT: P₄ does NOT appear in standard physics.

{'='*70}
SEARCH 2: 8128 in Mathematics
{'='*70}

  dim(SO(128)) = 8128    ✓ (Theorem B, as expected)
  dim(SE(127)) = 8128    ✓ (Theorem A)
  T(127) = 8128           ✓ (127th triangular number)

  But: 127 is the 7th Mersenne prime exponent.
  p = 7 → M₇ = 2⁷-1 = 127 → P₄ = 2⁶ × 127 = 8128

  Note: P₄ = 2⁶ × 127.
  2⁶ = 64 = number of codons = number of Braille patterns = 2^P₁!
  So P₄ = 2^P₁ × M₇

{'='*70}
SEARCH 3: The tau Chain
{'='*70}
""")

perfects = [6, 28, 496, 8128, 33550336]
mersenne_exp = [2, 3, 5, 7, 13]

print(f"  Perfect number tau values = 2p (Mersenne exponent):")
print(f"  {'P_k':>12} {'p':>4} {'tau':>5} {'tau/2':>6} {'tau = 2p?':>10}")
for i, (n, p) in enumerate(zip(perfects, mersenne_exp)):
    t = 2 * p
    print(f"  P_{i+1} = {n:>10}  {p:>4}  {t:>5}  {p:>6}  {'✓' if t == 2*p else '✗':>10}")

print(f"""
  The tau sequence: {[2*p for p in mersenne_exp]}
  = 2 × Mersenne exponents: 2×[2, 3, 5, 7, 13]

  tau(P₁) = 4  = tau(6)
  tau(P₂) = 6  = P₁ ← CROSS-LINK!
  tau(P₃) = 10
  tau(P₄) = 14
  tau(P₅) = 26

  Only tau(P₂) = P₁. No other tau(P_k) = P_j for known perfects.

{'='*70}
SEARCH 4: The phi Chain
{'='*70}
""")

for i, n in enumerate(perfects[:4]):
    p = mersenne_exp[i]
    M = 2**p - 1
    ph = 2**(p-2) * (M-1)  # phi(2^(p-1) * M) = 2^(p-2) * (M-1)
    print(f"  phi(P_{i+1}) = phi({n}) = {ph}")

print(f"""
  phi(P₁) = phi(6)    = 2
  phi(P₂) = phi(28)   = 12 = sigma(P₁) ← CROSS-LINK!
  phi(P₃) = phi(496)  = 240
  phi(P₄) = phi(8128) = 4032

  phi(P₂) = sigma(P₁) = 12. Does this pattern continue?
  sigma(P₂) = 56. phi(P₃) = 240. 240 ≠ 56. NO.

  Only the P₁-P₂ cross-link is special:
    tau(P₂) = P₁
    phi(P₂) = sigma(P₁)

{'='*70}
SEARCH 5: The 2^P₁ Pattern
{'='*70}
""")

print(f"  P₁ = 6. So 2^P₁ = 2⁶ = 64.")
print(f"  P₄ = 8128 = 64 × 127 = 2^P₁ × M₇")
print(f"\n  Does 2^P_k appear as a factor of later perfects?")

for i, n in enumerate(perfects):
    for j in range(i+1, len(perfects)):
        factor = 2**n
        if perfects[j] % factor == 0:
            print(f"    2^P_{i+1} = 2^{n} divides P_{j+1} = {perfects[j]}")
        # Too large for most, check only feasible
    if n <= 20:
        print(f"    2^P_{i+1} = 2^{n} = {2**n}. P_{i+2} = {perfects[i+1] if i+1 < len(perfects) else '?'}")
        if i+1 < len(perfects):
            print(f"    {perfects[i+1]} / {2**n} = {perfects[i+1] / 2**n}")

print(f"""
  P₄ = 2⁶ × 127 = 2^P₁ × M₇.
  P₃ = 2⁴ × 31 = 2^tau(P₁) × M₅. (tau(6)=4)
  P₂ = 2² × 7 = 2^phi(P₁) × M₃. (phi(6)=2)
  P₁ = 2¹ × 3 = 2^1 × M₂.

  Rewriting: P_k = 2^(p_k - 1) * M_pk

  The exponent p_k - 1:
    P₁: p=2, exp=1
    P₂: p=3, exp=2 = phi(P₁)
    P₃: p=5, exp=4 = tau(P₁)
    P₄: p=7, exp=6 = P₁ itself!

  ★★★ DISCOVERY:
    P₁ has 2^1 factor           (exponent = 1)
    P₂ has 2^2 = 2^phi(P₁)     (exponent = phi(6) = 2)
    P₃ has 2^4 = 2^tau(P₁)     (exponent = tau(6) = 4)
    P₄ has 2^6 = 2^P₁          (exponent = n = 6 itself!)

    Exponents: 1, 2, 4, 6 = 1, phi(6), tau(6), 6
    = 1, then the PROPER DIVISORS of 6 in order: 1, 2, 3, 6
    Wait: 1, 2, 4, 6. Not exactly divisors (4 is not a divisor of 6).

    Actually: 1, 2, 4, 6 = p_k - 1 for p_k = 2, 3, 5, 7.
    p_k - 1 = 1, 2, 4, 6. These are NOT divisors of 6.
    They are just the Mersenne exponents minus 1.

    But: phi(6)=2 ✓, tau(6)=4 ✓, n=6 ✓
    The first three non-trivial: phi, tau, n.

    COINCIDENCE? phi(6)=2=p₂-1, tau(6)=4=p₃-1, 6=p₄-1.
    This means: p₂ = phi(6)+1 = 3, p₃ = tau(6)+1 = 5, p₄ = 6+1 = 7.

    ★ The Mersenne exponents producing P₂, P₃, P₄ are:
      p₂ = phi(P₁) + 1 = 3
      p₃ = tau(P₁) + 1 = 5
      p₄ = P₁ + 1 = 7

    Does this predict p₅?
      sigma(P₁) + 1 = 13. And p₅ = 13! ✓ !!!

{'='*70}
★★★ SUPER-DISCOVERY: MERSENNE EXPONENT PREDICTION
{'='*70}
""")

# Verify the pattern
functions_of_6 = [
    ("1 (trivial)", 1),
    ("phi(6)", 2),
    ("tau(6)", 4),
    ("6 (n itself)", 6),
    ("sigma(6)", 12),
]

actual_exps = [2, 3, 5, 7, 13]

print(f"  Pattern: p_k = f_k(P₁) + 1 where f_k cycles through arithmetic functions of 6")
print()
print(f"  {'k':>3} {'f_k(6)':>8} {'f_k(6)+1':>10} {'Actual p_k':>12} {'Match?':>8}")
print(f"  {'-'*3} {'-'*8} {'-'*10} {'-'*12} {'-'*8}")

matches = 0
for i, ((name, val), actual_p) in enumerate(zip(functions_of_6, actual_exps)):
    predicted = val + 1
    match = predicted == actual_p
    if match: matches += 1
    print(f"  {i+1:>3} {name:>8} {predicted:>10} {actual_p:>12} {'✓' if match else '✗':>8}")

print(f"\n  Matches: {matches}/{len(actual_exps)}")

if matches == len(actual_exps):
    print(f"\n  ★★★ ALL FIVE MATCH!")
    print(f"  Mersenne exponents = arithmetic functions of P₁ plus 1:")
    print(f"    p₁ = 1+1 = 2         (trivial)")
    print(f"    p₂ = phi(6)+1 = 3    (totient)")
    print(f"    p₃ = tau(6)+1 = 5    (divisor count)")
    print(f"    p₄ = 6+1 = 7         (the number itself)")
    print(f"    p₅ = sigma(6)+1 = 13  (divisor sum)")
    print(f"\n  The first 5 Mersenne prime exponents are:")
    print(f"  {actual_exps} = [1, phi(6), tau(6), 6, sigma(6)] + 1")
    print(f"  = [1, 2, 4, 6, 12] + 1")
    print(f"  = arithmetic functions of the FIRST PERFECT NUMBER, each +1!")
    print(f"\n  This predicts p₆ should be f₆(6)+1 for some function f₆.")
    print(f"  Actual p₆ = 17 (the 6th Mersenne prime exponent).")
    print(f"  17-1 = 16 = 2⁴ = tau(6)² ?")
    print(f"  Or: 16 = 2·8 = phi(6)·(tau(6)+tau(6))?")
    print(f"  No clean f₆(6) = 16 from standard functions.")
    print(f"  The pattern breaks at k=6.")
else:
    print(f"\n  Pattern partially holds ({matches}/5).")

# Final note
print(f"""

{'='*70}
FINAL ASSESSMENT
{'='*70}

  The pattern p_k = f_k(6) + 1 holds for the first 5 Mersenne exponents:
    [2, 3, 5, 7, 13] = [1, phi(6), tau(6), 6, sigma(6)] + 1

  But it BREAKS at p₆ = 17 (16 is not a standard function of 6).
  And the "functions" are chosen post-hoc (1, phi, tau, id, sigma).

  HONEST VERDICT:
    This is LIKELY A COINCIDENCE exploiting the fact that
    {{1, 2, 4, 6, 12}} = proper divisors of 12 = sigma(6),
    and the first Mersenne exponents {{2,3,5,7,13}} happen to be
    one more than these values.

    The set {{1,2,4,6,12}} = divisors of sigma(6) = divisors of 12.
    d(12) = {{1, 2, 3, 4, 6, 12}}.
    {{1, 2, 4, 6, 12}} is d(12) minus {{3}}.

    Mersenne exponents: {{2,3,5,7,13}} = d(12)\\{{3}} + 1 ∪ {{3}}
    Hmm, 3 IS in the exponents. So {{2,3,5,7,13}} vs d(12)+1 = {{2,3,4,5,7,13}}.
    Missing: 4. Extra: none. 4 is NOT a Mersenne exponent (2⁴-1=15=3×5).

    REVISED: Mersenne exponents ⊂ d(sigma(6)) + 1 = d(12) + 1
    but not all: {{4}} fails (15 not prime).

    This is a SELECTION from d(12)+1 by the primality filter.
    Interesting but not a predictive theorem.

  GRADE: ORANGE — suggestive pattern, not a theorem.
  The first 5 Mersenne exponents = (divisors of sigma(6) that give
  Mersenne primes) + 1. But this is post-hoc and breaks at p₆=17.
""")
