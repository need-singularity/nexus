#!/usr/bin/env python3
"""
Investigation of R(n) = σ(n)φ(n)/(nτ(n)) Dirichlet series and related identities.
Uses exact arithmetic via fractions.Fraction where needed.
"""

from fractions import Fraction
import math
import time

# ─── Arithmetic functions ───

def smallest_prime_factor(n):
    if n < 2: return None
    if n % 2 == 0: return 2
    i = 3
    while i * i <= n:
        if n % i == 0: return i
        i += 2
    return n

def factorize(n):
    """Returns dict {prime: exponent}"""
    if n < 2: return {}
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

def sigma(n):
    """Sum of divisors"""
    if n < 1: return 0
    if n == 1: return 1
    result = 1
    for p, e in factorize(n).items():
        result *= (p**(e+1) - 1) // (p - 1)
    return result

def phi(n):
    """Euler totient"""
    if n < 1: return 0
    if n == 1: return 1
    result = n
    for p in factorize(n):
        result = result * (p - 1) // p
    return result

def tau(n):
    """Number of divisors"""
    if n < 1: return 0
    if n == 1: return 1
    result = 1
    for e in factorize(n).values():
        result *= (e + 1)
    return result

def omega(n):
    """Number of distinct prime factors"""
    return len(factorize(n))

def carmichael_lambda(n):
    """Carmichael function λ(n)"""
    if n <= 0: return 0
    if n == 1: return 1
    if n == 2: return 1
    factors = factorize(n)
    result = 1
    for p, e in factors.items():
        if p == 2:
            if e == 1:
                lam = 1
            elif e == 2:
                lam = 2
            else:
                lam = 2**(e - 2)
        else:
            lam = (p - 1) * p**(e - 1)
        result = lcm(result, lam)
    return result

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def lcm(a, b):
    return a * b // gcd(a, b)

def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i+2) == 0: return False
        i += 6
    return True

# ─── Precompute for large N ───

def sieve_functions(N):
    """Sieve-based computation of sigma, phi, tau for n=1..N"""
    sig = [0] * (N + 1)
    ph = list(range(N + 1))
    ta = [0] * (N + 1)

    # tau via sieve
    for d in range(1, N + 1):
        for m in range(d, N + 1, d):
            ta[m] += 1

    # sigma via sieve
    for d in range(1, N + 1):
        for m in range(d, N + 1, d):
            sig[m] += d

    # phi via sieve
    for p in range(2, N + 1):
        if ph[p] == p:  # p is prime
            for m in range(p, N + 1, p):
                ph[m] = ph[m] // p * (p - 1)

    return sig, ph, ta

# ═══════════════════════════════════════════════════════════════
# PART 1: Dirichlet series Σ R(n)/n^s
# ═══════════════════════════════════════════════════════════════

def part1_dirichlet_series():
    print("=" * 70)
    print("PART 1: Dirichlet series Σ R(n)/n^s for s=2,3,4")
    print("=" * 70)

    N = 50000
    print(f"\nSieving arithmetic functions up to N={N}...")
    t0 = time.time()
    sig, ph, ta = sieve_functions(N)
    print(f"  Sieve completed in {time.time()-t0:.1f}s")

    # Compute partial sums for s=2,3,4
    for s in [2, 3, 4]:
        total = 0.0
        for n in range(1, N + 1):
            if ta[n] == 0: continue
            R_n = sig[n] * ph[n] / (n * ta[n])
            total += R_n / n**s

        # Compare with zeta products
        # ζ(s) approximation
        zeta_s = sum(1.0/k**s for k in range(1, N+1))
        zeta_s1 = sum(1.0/k**(s-1) for k in range(1, N+1)) if s > 1 else float('inf')
        zeta_s2 = sum(1.0/k**(s+1) for k in range(1, N+1))
        zeta_2s = sum(1.0/k**(2*s) for k in range(1, N+1))
        zeta_2s_2 = sum(1.0/k**(2*s-2) for k in range(1, N+1))

        print(f"\n  s = {s}:")
        print(f"    Σ R(n)/n^s  = {total:.10f}  (N={N})")
        print(f"    ζ({s})        = {zeta_s:.10f}")
        print(f"    ζ({s-1})       = {zeta_s1:.10f}")
        print(f"    ζ({s+1})       = {zeta_s2:.10f}")
        print(f"    ζ({2*s})       = {zeta_2s:.10f}")

        # Try various products
        candidates = {
            f"ζ({s-1})·ζ({s})/ζ({2*s})": zeta_s1 * zeta_s / zeta_2s,
            f"ζ({s-1})²/ζ({2*s-2})": zeta_s1**2 / zeta_2s_2,
            f"ζ({s})²/ζ({2*s})": zeta_s**2 / zeta_2s,
            f"ζ({s-1})/ζ({s})": zeta_s1 / zeta_s,
            f"ζ({s})·ζ({s+1})/ζ({2*s})": zeta_s * zeta_s2 / zeta_2s,
            f"ζ({s-1})·ζ({s+1})/ζ({2*s})": zeta_s1 * zeta_s2 / zeta_2s,
        }

        print(f"    --- Candidate closed forms ---")
        for name, val in sorted(candidates.items(), key=lambda x: abs(x[1] - total)):
            ratio = total / val if val != 0 else float('inf')
            diff_pct = abs(ratio - 1) * 100
            marker = " <<<" if diff_pct < 0.1 else ""
            print(f"    {name:35s} = {val:.10f}  ratio={ratio:.8f}  ({diff_pct:.4f}%){marker}")

    # Partial sums: Σ_{n≤x} R(n) ~ c·x^a ?
    print(f"\n  --- Partial sums Σ R(n) for n≤x ---")
    checkpoints = [100, 500, 1000, 5000, 10000, 50000]
    partial = 0.0
    results = []
    idx = 0
    for n in range(1, N + 1):
        if ta[n] == 0: continue
        R_n = sig[n] * ph[n] / (n * ta[n])
        partial += R_n
        if idx < len(checkpoints) and n == checkpoints[idx]:
            results.append((n, partial))
            idx += 1

    print(f"    {'x':>8s} | {'Σ R(n)':>16s} | {'Σ/x':>12s} | {'Σ/x·ln(x)':>12s} | {'Σ/(x/ln x)':>12s}")
    print(f"    {'-'*8}-+-{'-'*16}-+-{'-'*12}-+-{'-'*12}-+-{'-'*12}")
    for x, S in results:
        lnx = math.log(x)
        print(f"    {x:8d} | {S:16.4f} | {S/x:12.6f} | {S/(x*lnx):12.8f} | {S*lnx/x:12.6f}")

    # Check if Σ R(n) ~ c·x: compute c = Σ/x for large x
    if results:
        x_last, S_last = results[-1]
        print(f"\n    Σ R(n) / x → {S_last/x_last:.8f} as x→{x_last}")
        print(f"    This suggests Σ R(n) ~ c·x with c ≈ {S_last/x_last:.6f}")

        # c should be related to product over primes of average R(p^k)
        # For primes: R(p) = (p+1)(p-1)/(2p) = (p²-1)/(2p)
        # Average of R(p) ~ p/2 for large p, so sum diverges linearly
        # More precisely: Σ R(n)/n converges? Let's check
        harm_R = 0.0
        for n in range(1, N + 1):
            if ta[n] == 0: continue
            R_n = sig[n] * ph[n] / (n * ta[n])
            harm_R += R_n / n
        print(f"\n    Σ R(n)/n up to {N} = {harm_R:.6f}")
        print(f"    (If diverges ~ c·ln(x), then c ≈ {harm_R/math.log(N):.6f})")


# ═══════════════════════════════════════════════════════════════
# PART 2: R on arithmetic progressions R(6k)
# ═══════════════════════════════════════════════════════════════

def part2_R_arithmetic_progressions():
    print("\n" + "=" * 70)
    print("PART 2: R(6k) — does it have special properties?")
    print("=" * 70)

    N = 6000  # k up to 1000 means n up to 6000
    sig, ph, ta = sieve_functions(N)

    def R(n):
        if n < 1 or ta[n] == 0: return None
        return Fraction(sig[n] * ph[n], n * ta[n])

    # R(6k) vs R(k)
    print(f"\n  Sample R(6k) and R(k) values:")
    print(f"  {'k':>5s} | {'R(6k)':>20s} | {'R(k)':>20s} | {'R(6k)/R(k)':>14s} | {'R(6k)-R(k)':>14s}")
    print(f"  {'-'*5}-+-{'-'*20}-+-{'-'*20}-+-{'-'*14}-+-{'-'*14}")

    ratios = []
    r6k_values = []
    for k in range(1, 51):
        r6k = R(6*k)
        rk = R(k)
        if r6k is not None and rk is not None and rk != 0:
            ratio = float(r6k / rk)
            ratios.append(ratio)
            r6k_values.append(float(r6k))
            if k <= 30:
                print(f"  {k:5d} | {str(r6k):>20s} | {str(rk):>20s} | {ratio:14.6f} | {float(r6k - rk):14.6f}")

    # Check: is R(6k) = 1 for any k > 1?
    print(f"\n  Checking R(6k) = 1 for k=1..1000:")
    ones = []
    for k in range(1, 1001):
        n = 6 * k
        if n <= N:
            r = R(n)
            if r == 1:
                ones.append(k)
    print(f"    k values where R(6k) = 1: {ones[:20]}{'...' if len(ones)>20 else ''}")
    print(f"    Count: {len(ones)}")

    # R(6k) statistics
    r6k_list = []
    for k in range(1, 1001):
        n = 6 * k
        if n <= N:
            r = R(n)
            if r is not None:
                r6k_list.append(float(r))

    avg_r6k = sum(r6k_list) / len(r6k_list)

    # Compare average R(6k) vs average R(n) for n≤6000
    all_R = []
    for n in range(1, N+1):
        r = R(n)
        if r is not None:
            all_R.append(float(r))
    avg_all = sum(all_R) / len(all_R)

    print(f"\n  Average R(6k) for k=1..1000: {avg_r6k:.8f}")
    print(f"  Average R(n)  for n=1..6000: {avg_all:.8f}")
    print(f"  Ratio: {avg_r6k/avg_all:.8f}")

    # Is R(6k) always >= 1?
    below_one = sum(1 for r in r6k_list if r < 1)
    above_one = sum(1 for r in r6k_list if r > 1)
    equal_one = sum(1 for r in r6k_list if r == 1.0)
    print(f"\n  R(6k) < 1: {below_one} times")
    print(f"  R(6k) = 1: {equal_one} times")
    print(f"  R(6k) > 1: {above_one} times")
    print(f"  min R(6k) = {min(r6k_list):.8f}")
    print(f"  max R(6k) = {max(r6k_list):.8f}")

    # Check factorization pattern: R(6k) when k is prime vs composite
    print(f"\n  R(6k) by type of k:")
    prime_r = [float(R(6*k)) for k in range(2, 500) if is_prime(k) and R(6*k) is not None]
    comp_r = [float(R(6*k)) for k in range(4, 500) if not is_prime(k) and k > 1 and R(6*k) is not None]
    print(f"    k prime:     avg R(6k) = {sum(prime_r)/len(prime_r):.8f}  (n={len(prime_r)})")
    print(f"    k composite: avg R(6k) = {sum(comp_r)/len(comp_r):.8f}  (n={len(comp_r)})")


# ═══════════════════════════════════════════════════════════════
# PART 3: Mertens-like estimate for Σ R(p)
# ═══════════════════════════════════════════════════════════════

def part3_mertens_estimate():
    print("\n" + "=" * 70)
    print("PART 3: Σ_{p≤x} R(p) and PNT comparison")
    print("=" * 70)

    # R(p) = σ(p)φ(p)/(pτ(p)) = (p+1)(p-1)/(2p) = (p²-1)/(2p)
    # Σ R(p) = Σ (p/2 - 1/(2p))
    # By PNT: Σ_{p≤x} p ~ x²/(2 ln x)
    # So Σ R(p) ~ x²/(4 ln x)

    # Sieve primes up to 50000
    N = 50000
    sieve = [True] * (N + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(N**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, N+1, i):
                sieve[j] = False

    primes = [p for p in range(2, N+1) if sieve[p]]
    print(f"  Number of primes up to {N}: {len(primes)}")

    # Compute cumulative Σ R(p)
    checkpoints = [100, 500, 1000, 5000, 10000, 20000, 50000]
    total_Rp = Fraction(0)
    total_p_half = Fraction(0)
    results = []
    cp_idx = 0

    for p in primes:
        Rp = Fraction(p*p - 1, 2*p)
        total_Rp += Rp
        total_p_half += Fraction(p, 2)

        if cp_idx < len(checkpoints) and p >= checkpoints[cp_idx]:
            # Find exact x
            while cp_idx < len(checkpoints) and checkpoints[cp_idx] <= p:
                x = checkpoints[cp_idx]
                # Recount up to x
                s = Fraction(0)
                for q in primes:
                    if q > x: break
                    s += Fraction(q*q - 1, 2*q)
                results.append((x, float(s)))
                cp_idx += 1

    print(f"\n  {'x':>8s} | {'Σ R(p)':>16s} | {'x²/(4ln x)':>16s} | {'ratio':>10s} | {'Σ(p/2)':>16s}")
    print(f"  {'-'*8}-+-{'-'*16}-+-{'-'*16}-+-{'-'*10}-+-{'-'*16}")

    for x, S in results:
        pnt_est = x**2 / (4 * math.log(x))
        p_half_sum = sum(p/2 for p in primes if p <= x)
        ratio = S / pnt_est if pnt_est > 0 else 0
        print(f"  {x:8d} | {S:16.4f} | {pnt_est:16.4f} | {ratio:10.6f} | {p_half_sum:16.4f}")

    # The -1/(2p) correction: Σ 1/(2p) ~ (1/2)·ln(ln(x)) by Mertens
    print(f"\n  Correction term: Σ 1/(2p) for p≤x")
    for x, S in results:
        corr = sum(1.0/(2*p) for p in primes if p <= x)
        mertens_est = 0.5 * math.log(math.log(x)) + 0.5 * 0.2614972128  # M = Meissel-Mertens
        print(f"    x={x:6d}: Σ 1/(2p) = {corr:.8f}, (ln ln x)/2 + M/2 = {mertens_est:.8f}")


# ═══════════════════════════════════════════════════════════════
# PART 4: New identity search
# ═══════════════════════════════════════════════════════════════

def part4_identity_search():
    print("\n" + "=" * 70)
    print("PART 4: New identity search for n=2..200")
    print("=" * 70)

    # Identity A: σ(n)² = n·τ(n)·φ(n)
    print(f"\n  --- Identity A: σ(n)² = n·τ(n)·φ(n) ---")
    solA = []
    for n in range(1, 201):
        s, t, p = sigma(n), tau(n), phi(n)
        if s*s == n * t * p:
            solA.append(n)
            print(f"    n={n:4d}: σ={s}, τ={t}, φ={p}, σ²={s*s}, nτφ={n*t*p}")
    print(f"    Solutions: {solA}")

    # Identity B: σ(n)·φ(n)² = n²·τ(n)
    print(f"\n  --- Identity B: σ(n)·φ(n)² = n²·τ(n) ---")
    solB = []
    for n in range(1, 201):
        s, t, p = sigma(n), tau(n), phi(n)
        if s * p * p == n * n * t:
            solB.append(n)
            print(f"    n={n:4d}: σ={s}, τ={t}, φ={p}, σφ²={s*p*p}, n²τ={n*n*t}")
    print(f"    Solutions: {solB}")

    # Identity C: σ(n)·ω(n) = τ(n)·φ(n)
    print(f"\n  --- Identity C: σ(n)·ω(n) = τ(n)·φ(n) ---")
    solC = []
    for n in range(2, 201):  # start at 2 since ω(1)=0
        s, t, p, w = sigma(n), tau(n), phi(n), omega(n)
        if s * w == t * p:
            solC.append(n)
            print(f"    n={n:4d}: σ={s}, τ={t}, φ={p}, ω={w}, σω={s*w}, τφ={t*p}")
    print(f"    Solutions: {solC}")

    # Identity D: λ(n)·σ(n) = n·φ(n)
    print(f"\n  --- Identity D: λ(n)·σ(n) = n·φ(n) ---")
    solD = []
    for n in range(1, 201):
        s, p = sigma(n), phi(n)
        lam = carmichael_lambda(n)
        if lam * s == n * p:
            solD.append(n)
            print(f"    n={n:4d}: σ={s}, φ={p}, λ={lam}, λσ={lam*s}, nφ={n*p}")
    print(f"    Solutions: {solD}")

    # ─── Additional exploratory identities ───

    # Identity E: R(n) = σ(n)φ(n)/(nτ(n)) = integer
    print(f"\n  --- Identity E: R(n) = σ(n)φ(n)/(nτ(n)) is an integer ---")
    solE = []
    for n in range(1, 201):
        s, t, p = sigma(n), tau(n), phi(n)
        if t > 0 and (s * p) % (n * t) == 0:
            val = (s * p) // (n * t)
            solE.append((n, val))
            if val > 1 or n <= 10:
                print(f"    n={n:4d}: R(n) = {val}")
    print(f"    n with integer R(n): {[x[0] for x in solE]}")

    # Identity F: σ(n)/φ(n) = τ(n) (i.e. R(n) = n/φ(n)² ... no, σ/φ=τ)
    print(f"\n  --- Identity F: σ(n)/φ(n) = τ(n) ---")
    solF = []
    for n in range(1, 201):
        s, t, p = sigma(n), tau(n), phi(n)
        if p > 0 and s == t * p:
            solF.append(n)
            print(f"    n={n:4d}: σ={s}, τ={t}, φ={p}")
    print(f"    Solutions: {solF}")

    # Identity G: σ(n)·φ(n) = n² (equivalent to R(n)=n/τ(n))
    print(f"\n  --- Identity G: σ(n)·φ(n) = n² ---")
    solG = []
    for n in range(1, 201):
        if sigma(n) * phi(n) == n * n:
            solG.append(n)
            print(f"    n={n:4d}: σ={sigma(n)}, φ={phi(n)}")
    print(f"    Solutions: {solG}")
    print(f"    (These are exactly the primes, since σ(p)φ(p)=(p+1)(p-1)=p²-1≠p²)")
    print(f"    (And n=1: σ(1)φ(1)=1=1²)")

    # Identity H: σ(n) + φ(n) = n·τ(n)
    print(f"\n  --- Identity H: σ(n) + φ(n) = n·τ(n) ---")
    solH = []
    for n in range(1, 201):
        s, t, p = sigma(n), tau(n), phi(n)
        if s + p == n * t:
            solH.append(n)
            print(f"    n={n:4d}: σ={s}, φ={p}, σ+φ={s+p}, nτ={n*t}")
    print(f"    Solutions: {solH}")

    # Summary
    print(f"\n  ═══ SUMMARY OF IDENTITY SEARCH ═══")
    print(f"  Identity A [σ²=nτφ]:     {len(solA):3d} solutions: {solA[:15]}{'...' if len(solA)>15 else ''}")
    print(f"  Identity B [σφ²=n²τ]:    {len(solB):3d} solutions: {solB[:15]}{'...' if len(solB)>15 else ''}")
    print(f"  Identity C [σω=τφ]:      {len(solC):3d} solutions: {solC[:15]}{'...' if len(solC)>15 else ''}")
    print(f"  Identity D [λσ=nφ]:      {len(solD):3d} solutions: {solD[:15]}{'...' if len(solD)>15 else ''}")
    print(f"  Identity E [R(n)∈Z]:     {len(solE):3d} solutions: {[x[0] for x in solE][:15]}{'...' if len(solE)>15 else ''}")
    print(f"  Identity F [σ/φ=τ]:      {len(solF):3d} solutions: {solF[:15]}{'...' if len(solF)>15 else ''}")
    print(f"  Identity G [σφ=n²]:      {len(solG):3d} solutions: {solG[:15]}{'...' if len(solG)>15 else ''}")
    print(f"  Identity H [σ+φ=nτ]:     {len(solH):3d} solutions: {solH[:15]}{'...' if len(solH)>15 else ''}")


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    t_start = time.time()

    part1_dirichlet_series()
    part2_R_arithmetic_progressions()
    part3_mertens_estimate()
    part4_identity_search()

    print(f"\n{'='*70}")
    print(f"Total runtime: {time.time()-t_start:.1f}s")
    print(f"{'='*70}")
