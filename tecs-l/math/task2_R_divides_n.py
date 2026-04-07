"""
Task 2: R(n)|n pattern analysis
Find all n where R(n) is an integer AND R(n) | n.

R(n) = σ(n)·φ(n) / (n·τ(n))
R(p^a) = (p^(a+1)-1) / (p·(a+1))
"""

import math
from fractions import Fraction
from collections import defaultdict

def factorize(n):
    """Return prime factorization as dict {p: a}."""
    factors = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors

def R_prime_power(p, a):
    """R(p^a) = (p^(a+1) - 1) / (p * (a+1))"""
    return Fraction(p**(a+1) - 1, p * (a+1))

def compute_R(n):
    """Compute R(n) as a Fraction."""
    if n == 1:
        return Fraction(1)
    factors = factorize(n)
    result = Fraction(1)
    for p, a in factors.items():
        result *= R_prime_power(p, a)
    return result

def sigma(n):
    factors = factorize(n)
    result = 1
    for p, a in factors.items():
        result *= (p**(a+1) - 1) // (p - 1)
    return result

def phi(n):
    factors = factorize(n)
    result = n
    for p in factors:
        result = result // p * (p - 1)
    return result

def tau(n):
    factors = factorize(n)
    result = 1
    for a in factors.values():
        result *= (a + 1)
    return result

def search_solutions(n_max):
    """Find all n ≤ n_max where R(n) is an integer and R(n) | n."""
    solutions = []

    for n in range(1, n_max + 1):
        r = compute_R(n)
        # Check if R(n) is integer
        if r.denominator == 1:
            r_int = r.numerator
            # Check if R(n) | n
            if n % r_int == 0:
                solutions.append((n, r_int, n // r_int))

        if n % 10000 == 0:
            print(f"  Progress: n={n}, solutions so far: {len(solutions)}")

    return solutions

def analyze_factorizations(solutions):
    """Analyze factorization patterns of solutions."""
    print("\n" + "="*70)
    print("FACTORIZATION ANALYSIS")
    print("="*70)

    for n, R, ratio in solutions:
        factors = factorize(n)
        # Sort factors
        factor_str = " · ".join(f"{p}^{a}" if a > 1 else str(p) for p, a in sorted(factors.items()))
        sigma_n = sigma(n)
        phi_n = phi(n)
        tau_n = tau(n)

        print(f"\nn = {n} = {factor_str}")
        print(f"  R(n) = {R}")
        print(f"  n/R  = {ratio}")
        print(f"  σ(n) = {sigma_n}, φ(n) = {phi_n}, τ(n) = {tau_n}")
        print(f"  σ(n)·φ(n) = {sigma_n * phi_n}, n·τ(n) = {n * tau_n}")
        print(f"  Check: {sigma_n * phi_n} / {n * tau_n} = {Fraction(sigma_n * phi_n, n * tau_n)} = {R}")

        # Check: is n/R related to perfect numbers?
        # Perfect numbers: 6, 28, 496, 8128, ...
        # Mersenne numbers: 2^p - 1 for prime p
        perfect = [6, 28, 496, 8128, 33550336]
        mersenne = [1, 3, 7, 31, 127, 8191, 131071, 524287]

        notes = []
        if ratio in perfect:
            notes.append(f"n/R = {ratio} is a PERFECT NUMBER")
        if ratio in mersenne:
            notes.append(f"n/R = {ratio} is a MERSENNE NUMBER (2^k-1)")
        if R in perfect:
            notes.append(f"R = {R} is a PERFECT NUMBER")
        if R in mersenne:
            notes.append(f"R = {R} is a MERSENNE NUMBER")

        # Check if R is related to perfect numbers
        for pn in perfect:
            if pn % R == 0:
                notes.append(f"R | perfect number {pn}")
            if R % pn == 0:
                notes.append(f"perfect number {pn} | R")

        # Check sigma/phi pattern
        # For perfect n: σ(n) = 2n
        if sigma_n == 2 * n:
            notes.append(f"n is PERFECT (σ(n)=2n)")
        # Multiply perfect: σ(n) = k·n for some integer k
        if sigma_n % n == 0:
            notes.append(f"n is MULTIPLY PERFECT (σ(n)={sigma_n//n}·n)")

        for note in notes:
            print(f"  *** {note} ***")

    print("\n")

def perfect_number_structure():
    """Check if solutions relate to perfect number structure."""
    print("="*70)
    print("PERFECT NUMBER / MERSENNE STRUCTURE")
    print("="*70)

    # Known perfect numbers (even): n = 2^(p-1) * (2^p - 1) where 2^p-1 is prime
    # σ(n) = 2n for perfect numbers

    print("""
Known pattern for even perfect numbers (Euler):
  n = 2^(p-1) * M_p where M_p = 2^p - 1 is Mersenne prime
  σ(n) = 2n

For these:
  R(2^(p-1)) = (2^p - 1) / (2 * p)
  R(M_p)     = (M_p^2 - 1) / (2 * M_p)   [since M_p is prime, a=1]
             = (M_p - 1)(M_p + 1) / (2 * M_p)
             = (2^p - 2)(2^p) / (2 * (2^p - 1))
             = 2^(p-1) * (2^p - 2) / (2^p - 1)

Wait, let me recalculate more carefully...
""")

    # Perfect numbers and their R values
    perfect_cases = [
        (6,    2, 1, [(2,1),(3,1)]),   # 6 = 2·3
        (28,   2, 2, [(2,2),(7,1)]),   # 28 = 4·7
        (496,  2, 4, [(2,4),(31,1)]),  # 496 = 16·31
        (8128, 2, 6, [(2,6),(127,1)]), # 8128 = 64·127
    ]

    print(f"\n{'n':>8} {'R(n)':>12} {'n/R':>8} {'σ(n)':>8} {'Notes'}")
    print("-"*60)
    for n, _, _, _ in perfect_cases:
        r = compute_R(n)
        sig = sigma(n)
        notes = "perfect" if sig == 2*n else ""
        if r.denominator == 1:
            div = "divides" if n % r.numerator == 0 else "not divides"
            print(f"{n:>8} {str(r):>12} {n//r.numerator if r.denominator==1 and n%r.numerator==0 else 'N/A':>8} {sig:>8} {notes} R|n:{div}")
        else:
            print(f"{n:>8} {str(r):>12} {'N/A':>8} {sig:>8} {notes} R not integer")

def characterize_solutions(solutions):
    """Attempt to characterize all solutions."""
    print("\n" + "="*70)
    print("CHARACTERIZATION ATTEMPT")
    print("="*70)

    print("\nFor R(n) to be an integer:")
    print("  R(n) = ∏_p R(p^a_p) = ∏_p (p^(a+1)-1)/(p(a+1))")
    print("  Each factor must combine to give an integer product.")
    print()

    print("Known solutions and their factorizations:")
    print(f"{'n':>8} {'factorization':>25} {'R(n)':>8} {'n/R':>8} {'n/R factored'}")
    print("-"*70)

    for n, R, ratio in solutions:
        factors = factorize(n)
        f_str = "·".join(f"{p}^{a}" if a > 1 else str(p) for p,a in sorted(factors.items()))
        rf = factorize(ratio) if ratio > 1 else {}
        r_str = "·".join(f"{p}^{a}" if a > 1 else str(p) for p,a in sorted(rf.items())) if rf else "1"
        print(f"{n:>8} {f_str:>25} {R:>8} {ratio:>8} {r_str}")

    print()
    print("Pattern observations:")
    print()

    # Check n/R patterns
    ratios = [ratio for _, _, ratio in solutions]
    print(f"n/R values: {ratios}")

    # Check if ratios are multiply perfect or related
    for n, R, ratio in solutions:
        sig_ratio = sigma(ratio)
        print(f"  n/R = {ratio}: σ({ratio}) = {sig_ratio}, ratio = {sig_ratio/ratio:.4f}")

    print()
    print("Checking if n/R follows a pattern (perfect, multiply perfect, ...):")
    for n, R, ratio in solutions:
        sig_r = sigma(ratio)
        if sig_r == 2 * ratio:
            print(f"  n/R = {ratio} is PERFECT")
        elif sig_r == 3 * ratio:
            print(f"  n/R = {ratio} is 3x MULTIPLY PERFECT")
        else:
            print(f"  n/R = {ratio}: σ/n = {sig_r}/{ratio} = {Fraction(sig_r, ratio)}")

def extended_search_analysis(solutions_extended):
    """Analyze the extended search results."""
    print("\n" + "="*70)
    print("EXTENDED SEARCH ANALYSIS (n ≤ 100000)")
    print("="*70)

    print(f"\nTotal solutions found: {len(solutions_extended)}")
    print()
    print(f"{'n':>8} {'factorization':>30} {'R':>10} {'n/R':>8}")
    print("-"*60)

    for n, R, ratio in solutions_extended:
        factors = factorize(n)
        f_str = "·".join(f"{p}^{a}" if a > 1 else str(p) for p,a in sorted(factors.items()))
        print(f"{n:>8} {f_str:>30} {R:>10} {ratio:>8}")

    # Deeper pattern analysis
    print("\nDifferences between consecutive solutions:")
    ns = [n for n, _, _ in solutions_extended]
    for i in range(1, len(ns)):
        print(f"  {ns[i]} - {ns[i-1]} = {ns[i] - ns[i-1]}")

    print("\nRatios between consecutive solutions:")
    for i in range(1, len(ns)):
        print(f"  {ns[i]} / {ns[i-1]} = {ns[i]/ns[i-1]:.4f}")

def multiply_perfect_connection(solutions):
    """Check connection to multiply perfect numbers."""
    print("\n" + "="*70)
    print("MULTIPLY PERFECT NUMBER CONNECTION")
    print("="*70)

    print("""
Multiply perfect numbers: σ(n) = k·n for integer k ≥ 2
  k=2: perfect numbers (6, 28, 496, 8128, ...)
  k=3: triperfect (120, 672, ...)  ← appear in solutions!
  k=4: 30240, 32760, ...
  k=5: 14182439040, ...
  k=6: 154345556085770649600, ...

Known triperfect numbers ≤ 100000: 120, 672, ...
""")

    known_triperfect = [120, 672, 523776, 459818240]
    known_perfect = [6, 28, 496, 8128, 33550336]

    for n, R, ratio in solutions:
        sig = sigma(n)
        k = sig // n if sig % n == 0 else None
        mult_type = f"{k}x perfect" if k else f"σ/n = {Fraction(sig,n)}"
        print(f"n = {n}: σ(n) = {sig}, {mult_type}")
        if n in known_triperfect:
            print(f"  *** n is TRIPERFECT ***")
        if n in known_perfect:
            print(f"  *** n is PERFECT ***")

def main():
    print("TASK 2: R(n)|n PATTERN ANALYSIS")
    print("="*70)

    # First verify the known solutions
    print("\nVerifying known solutions n ≤ 10000:")
    known = [(1,1,1), (6,1,6), (28,4,7), (120,6,20), (672,24,28), (1080,30,36), (1782,66,27)]
    print(f"{'n':>6} {'R':>6} {'n/R':>6} {'verified':>10}")
    for n, R_expected, ratio_expected in known:
        r = compute_R(n)
        print(f"{n:>6} {R_expected:>6} {ratio_expected:>6} {'OK' if r == R_expected and n % R_expected == 0 else 'FAIL':>10}  (computed R={r})")

    # Full search n ≤ 10000
    print("\n" + "="*70)
    print("FULL SEARCH n ≤ 10000")
    solutions_10k = search_solutions(10000)
    print(f"\nFound {len(solutions_10k)} solutions:")
    for n, R, ratio in solutions_10k:
        print(f"  n={n}, R={R}, n/R={ratio}")

    analyze_factorizations(solutions_10k)
    perfect_number_structure()
    multiply_perfect_connection(solutions_10k)
    characterize_solutions(solutions_10k)

    # Extended search n ≤ 100000
    print("\n" + "="*70)
    print("EXTENDED SEARCH n ≤ 100000")
    print("(This may take a few minutes...)")
    solutions_100k = search_solutions(100000)
    extended_search_analysis(solutions_100k)

    # Final characterization
    print("\n" + "="*70)
    print("FINAL CHARACTERIZATION ATTEMPT")
    print("="*70)

    print("\nAll solutions up to 100000:")
    for n, R, ratio in solutions_100k:
        f = factorize(n)
        sig = sigma(n)
        k = sig // n if sig % n == 0 else None
        print(f"  n={n:7d}: factors={dict(sorted(f.items()))}, R={R}, n/R={ratio}, σ(n)/n={Fraction(sig,n)}")

    print("""
THEORETICAL ANALYSIS:

For R(n) = ∏ R(p^a) to be an integer, we need:
  ∏ (p^(a+1)-1)/(p(a+1)) ∈ Z

For a=1 (prime factor p): R(p) = (p²-1)/(2p)
  = (p-1)(p+1)/(2p)
  This is NOT an integer (p is odd prime, gcd(p,2p)=p)
  For p=2: R(2) = 3/4, not integer

For a=2: R(p²) = (p³-1)/(3p)
For a=3: R(p³) = (p⁴-1)/(4p)

The integer condition requires careful divisibility.

HYPOTHESIS: Solutions are related to multiply perfect numbers:
  - n=1: trivially R=1
  - n=6 (perfect): σ(6)=12=2·6
  - n=28 (perfect): σ(28)=56=2·28
  - n=120 (triperfect): σ(120)=360=3·120
  - n=672 (triperfect): σ(672)=2016=3·672
  - n=1080, n=1782: check σ...
""")

if __name__ == "__main__":
    main()
