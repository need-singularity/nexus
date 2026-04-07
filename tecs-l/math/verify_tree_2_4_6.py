#!/usr/bin/env python3
"""
Verify three TREE branch hypotheses: H-TREE-2 (p-adic), H-TREE-4 (Dirichlet ring), H-TREE-6 (tropical).
All results printed as tables.
"""

import math
from collections import defaultdict
from fractions import Fraction

# ─── Arithmetic function helpers ───

def divisors(n):
    """Return sorted list of divisors of n."""
    divs = []
    for i in range(1, int(n**0.5) + 1):
        if n % i == 0:
            divs.append(i)
            if i != n // i:
                divs.append(n // i)
    return sorted(divs)

def sigma(n):
    """Sum of divisors."""
    return sum(divisors(n))

def phi(n):
    """Euler totient."""
    result = n
    p = 2
    temp = n
    while p * p <= temp:
        if temp % p == 0:
            while temp % p == 0:
                temp //= p
            result -= result // p
        p += 1
    if temp > 1:
        result -= result // temp
    return result

def tau(n):
    """Number of divisors."""
    return len(divisors(n))

def factorize(n):
    """Return dict {prime: exponent}."""
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

def R_fraction(n):
    """R(n) = σ(n)φ(n)/(nτ(n)) as a Fraction."""
    return Fraction(sigma(n) * phi(n), n * tau(n))

def v_p(n, p):
    """p-adic valuation of integer n. v_p(0) = infinity (return 999)."""
    if n == 0:
        return 999
    count = 0
    while n % p == 0:
        n //= p
        count += 1
    return count

def v_p_fraction(frac, p):
    """p-adic valuation of a Fraction."""
    if frac == 0:
        return 999
    return v_p(abs(frac.numerator), p) - v_p(abs(frac.denominator), p)


# ══════════════════════════════════════════════════════════════
# H-TREE-2: p-adic branch
# ══════════════════════════════════════════════════════════════
print("=" * 80)
print("H-TREE-2: p-ADIC BRANCH VERIFICATION")
print("=" * 80)

# --- Part 1: v_2 of numerator and denominator for n=2..200 ---
print("\n─── Part 1: v_2(num(R(n))) and v_2(den(R(n))) for n=2..50 (sample) ───")
print(f"{'n':>4} {'R(n)':>20} {'v2(num)':>8} {'v2(den)':>8} {'v2(R)':>7} {'v2(n)':>6}")
print("-" * 60)
for n in range(2, 51):
    r = R_fraction(n)
    vn = v_p(abs(r.numerator), 2)
    vd = v_p(abs(r.denominator), 2)
    vr = vn - vd
    v2n = v_p(n, 2)
    print(f"{n:>4} {str(r):>20} {vn:>8} {vd:>8} {vr:>7} {v2n:>6}")

# --- Part 2: Pattern in v_2(R(n)) as function of v_2(n) ---
print("\n─── Part 2: v_2(R(n)) grouped by v_2(n) for n=2..200 ───")
groups = defaultdict(list)
for n in range(2, 201):
    r = R_fraction(n)
    vr = v_p_fraction(r, 2)
    v2n = v_p(n, 2)
    groups[v2n].append((n, vr))

for k in sorted(groups.keys()):
    vals = groups[k]
    vr_vals = [v[1] for v in vals]
    vr_min = min(vr_vals)
    vr_max = max(vr_vals)
    vr_avg = sum(vr_vals) / len(vr_vals)
    print(f"  v_2(n) = {k}: count={len(vals):>3}, v_2(R) range=[{vr_min:>4}, {vr_max:>4}], mean={vr_avg:>7.3f}")
    # Show first few examples
    for n_ex, vr_ex in vals[:5]:
        print(f"    n={n_ex:>4}, v_2(R(n))={vr_ex:>4}")

# --- Part 3: n = 2^k, R(2^k) = (2^(k+1)-1)/(2(k+1)) ---
print("\n─── Part 3: R(2^k) for k=1..15 ───")
print(f"{'k':>4} {'2^k':>8} {'R(2^k)':>25} {'v2(R)':>7} {'predicted':>10} {'match':>6}")
print("-" * 70)
for k in range(1, 16):
    n = 2**k
    r = R_fraction(n)
    vr = v_p_fraction(r, 2)
    # Prediction: v_2(R(2^k)) = -v_2(2(k+1)) = -(1 + v_2(k+1))
    predicted = -(1 + v_p(k + 1, 2))
    match = "YES" if vr == predicted else "NO"
    r_str = str(r) if len(str(r)) <= 25 else f"{float(r):.10f}"
    print(f"{k:>4} {n:>8} {r_str:>25} {vr:>7} {predicted:>10} {match:>6}")

# --- Part 4: n = 2^k * m, m odd ---
print("\n─── Part 4: v_2(R(2^k · m)) for small k,m ───")
print(f"{'k':>3} {'m':>5} {'n':>6} {'v2(R)':>7} {'σ(n)':>8} {'φ(n)':>8} {'τ(n)':>6}")
print("-" * 55)
for k in range(1, 7):
    for m in [1, 3, 5, 7, 9, 15]:
        n = (2**k) * m
        if n > 200:
            continue
        r = R_fraction(n)
        vr = v_p_fraction(r, 2)
        print(f"{k:>3} {m:>5} {n:>6} {vr:>7} {sigma(n):>8} {phi(n):>8} {tau(n):>6}")

# --- Part 5: p-adic absolute values for p=2,3,5 ---
print("\n─── Part 5: |R(n)|_p for p=2,3,5 and n=1..100 ───")
print(f"{'n':>4} {'R(n)':>15} {'|R|_2':>12} {'|R|_3':>12} {'|R|_5':>12}")
print("-" * 60)
for n in range(1, 101):
    r = R_fraction(n)
    vals = {}
    for p in [2, 3, 5]:
        vp = v_p_fraction(r, p)
        vals[p] = p ** (-vp)  # |x|_p = p^(-v_p(x))
    r_str = str(r) if len(str(r)) <= 15 else f"{float(r):.6f}"
    print(f"{n:>4} {r_str:>15} {vals[2]:>12.6f} {vals[3]:>12.6f} {vals[5]:>12.6f}")

# Special: highlight perfect numbers and n=6
print("\n─── Part 5b: Perfect numbers p-adic highlight ───")
for n in [6, 28, 496]:
    r = R_fraction(n)
    print(f"  n={n}: R(n)={r} = {float(r):.8f}")
    for p in [2, 3, 5]:
        vp = v_p_fraction(r, p)
        abs_p = p ** (-vp)
        print(f"    |R({n})|_{p} = {p}^(-({vp})) = {abs_p:.6f}")


# ══════════════════════════════════════════════════════════════
# H-TREE-4: Operator algebra / Dirichlet ring
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("H-TREE-4: OPERATOR ALGEBRA / DIRICHLET RING VERIFICATION")
print("=" * 80)

# --- Part 1: Multiplicativity checks ---
print("\n─── Part 1: Multiplicativity of σ·φ and id·τ ───")
print("Testing: for coprime m,n: f(mn) = f(m)·f(n)")
print()

def sigma_phi(n):
    return sigma(n) * phi(n)

def id_tau(n):
    return n * tau(n)

# Test multiplicativity for coprime pairs
print(f"{'m':>4} {'n':>4} {'gcd':>4} {'σφ(mn)':>12} {'σφ(m)σφ(n)':>12} {'match':>6} {'idτ(mn)':>10} {'idτ(m)idτ(n)':>14} {'match':>6}")
print("-" * 85)
coprime_pairs = [(2,3),(2,5),(3,5),(2,7),(3,7),(4,9),(5,6),(6,7),(4,15),(7,9),(8,9),(11,13)]
all_sp_mult = True
all_it_mult = True
for m, n_val in coprime_pairs:
    g = math.gcd(m, n_val)
    sp_mn = sigma_phi(m * n_val)
    sp_m_n = sigma_phi(m) * sigma_phi(n_val)
    it_mn = id_tau(m * n_val)
    it_m_n = id_tau(m) * id_tau(n_val)
    sp_ok = "YES" if sp_mn == sp_m_n else "NO"
    it_ok = "YES" if it_mn == it_m_n else "NO"
    if sp_mn != sp_m_n: all_sp_mult = False
    if it_mn != it_m_n: all_it_mult = False
    print(f"{m:>4} {n_val:>4} {g:>4} {sp_mn:>12} {sp_m_n:>12} {sp_ok:>6} {it_mn:>10} {it_m_n:>14} {it_ok:>6}")

# Non-coprime pairs as control
print("\nNon-coprime pairs (should fail):")
non_coprime = [(2,4),(3,6),(4,6),(6,10),(2,6)]
for m, n_val in non_coprime:
    g = math.gcd(m, n_val)
    sp_mn = sigma_phi(m * n_val)
    sp_m_n = sigma_phi(m) * sigma_phi(n_val)
    it_mn = id_tau(m * n_val)
    it_m_n = id_tau(m) * id_tau(n_val)
    sp_ok = "YES" if sp_mn == sp_m_n else "NO"
    it_ok = "YES" if it_mn == it_m_n else "NO"
    print(f"  m={m}, n={n_val}, gcd={g}: σφ match={sp_ok}, idτ match={it_ok}")

print(f"\n  σ·φ multiplicative on coprime pairs: {all_sp_mult}")
print(f"  id·τ multiplicative on coprime pairs: {all_it_mult}")
print(f"  → R = (σ·φ)/(id·τ) multiplicative: {all_sp_mult and all_it_mult}")

# --- Part 2: Dirichlet convolution (σ*1)(n) vs nτ(n) ---
print("\n─── Part 2: (σ*1)(n) = Σ_{d|n} σ(d) vs nτ(n) ───")
print(f"{'n':>4} {'(σ*1)(n)':>12} {'nτ(n)':>10} {'ratio':>10} {'match':>6}")
print("-" * 50)
for n in range(1, 31):
    sigma_star_1 = sum(sigma(d) for d in divisors(n))
    ntau = n * tau(n)
    ratio = Fraction(sigma_star_1, ntau)
    match = "YES" if sigma_star_1 == ntau else "NO"
    print(f"{n:>4} {sigma_star_1:>12} {ntau:>10} {str(ratio):>10} {match:>6}")

# Also try (σ*μ) = id (Mobius inversion), and other convolutions
print("\n─── Part 2b: Other Dirichlet convolutions for context ───")
def mobius(n):
    """Möbius function."""
    factors = factorize(n)
    for p, e in factors.items():
        if e > 1:
            return 0
    return (-1) ** len(factors)

print(f"{'n':>4} {'(σ*μ)(n)':>10} {'id(n)':>7} {'(φ*1)(n)':>10} {'n':>5}")
print("-" * 45)
for n in range(1, 31):
    sigma_mu = sum(sigma(d) * mobius(n // d) for d in divisors(n))
    phi_one = sum(phi(d) for d in divisors(n))
    print(f"{n:>4} {sigma_mu:>10} {n:>7} {phi_one:>10} {n:>5}")

# --- Part 3: Decomposition R = f * g ? ---
print("\n─── Part 3: Can R be written as a Dirichlet convolution f * g? ───")
print("R is multiplicative, so R = R_mult. For multiplicative f:")
print("  f = Σ f(p^a)/p^(as) as Euler product.")
print()
print("R on prime powers p^a:")
print(f"{'p':>4} {'a':>3} {'n=p^a':>7} {'R(p^a)':>20} {'float':>12}")
print("-" * 50)
for p in [2, 3, 5, 7, 11]:
    for a in range(1, 6):
        n = p ** a
        if n > 500:
            break
        r = R_fraction(n)
        print(f"{p:>4} {a:>3} {n:>7} {str(r):>20} {float(r):>12.6f}")

print("\nR(p) = (p+1)(p-1)/(2p) = (p²-1)/(2p) for all primes p:")
print(f"{'p':>4} {'R(p)':>15} {'(p²-1)/(2p)':>15} {'match':>6}")
print("-" * 45)
for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]:
    r = R_fraction(p)
    formula = Fraction(p**2 - 1, 2 * p)
    match = "YES" if r == formula else "NO"
    print(f"{p:>4} {str(r):>15} {str(formula):>15} {match:>6}")

print("\nR(p²) = σ(p²)φ(p²)/(p²τ(p²)) = (p²+p+1)(p²-p)/(3p²):")
print(f"{'p':>4} {'R(p²)':>20} {'formula':>20} {'match':>6}")
print("-" * 55)
for p in [2, 3, 5, 7, 11, 13]:
    r = R_fraction(p**2)
    formula = Fraction((p**2 + p + 1) * (p**2 - p), 3 * p**2)
    match = "YES" if r == formula else "NO"
    print(f"{p:>4} {str(r):>20} {str(formula):>20} {match:>6}")

# --- Part 4: Dirichlet inverse of R ---
print("\n─── Part 4: Dirichlet inverse R^(-1) for n=1..20 ───")
R_inv = {}
for n in range(1, 21):
    if n == 1:
        R_inv[1] = Fraction(1, 1) / R_fraction(1)
    else:
        s = Fraction(0)
        for d in divisors(n):
            if d < n:
                s += R_fraction(n // d) * R_inv[d]
        R_inv[n] = -s / R_fraction(1)

print(f"{'n':>4} {'R^(-1)(n)':>25} {'float':>14}")
print("-" * 48)
for n in range(1, 21):
    r_str = str(R_inv[n]) if len(str(R_inv[n])) <= 25 else f"{float(R_inv[n]):.10f}"
    print(f"{n:>4} {r_str:>25} {float(R_inv[n]):>14.8f}")

# Verify: (R * R^(-1))(n) should = ε(n) (1 if n=1, else 0)
print("\nVerification: (R * R^(-1))(n) = ε(n)?")
print(f"{'n':>4} {'(R*R^-1)(n)':>20} {'expected':>10} {'match':>6}")
print("-" * 45)
for n in range(1, 21):
    conv = sum(R_fraction(n // d) * R_inv[d] for d in divisors(n))
    expected = Fraction(1) if n == 1 else Fraction(0)
    match = "YES" if conv == expected else "NO"
    print(f"{n:>4} {str(conv):>20} {str(expected):>10} {match:>6}")


# ══════════════════════════════════════════════════════════════
# H-TREE-6: Tropical geometry
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("H-TREE-6: TROPICAL GEOMETRY VERIFICATION")
print("=" * 80)

def f_trop(p, a):
    """Tropical version: f_trop(p,a) = (a+1)·ln(p) - ln(a+1)."""
    return (a + 1) * math.log(p) - math.log(a + 1)

def R_trop(n):
    """Tropical R: min over prime powers p^a || n of f_trop(p,a)."""
    factors = factorize(n)
    if not factors:
        return float('inf')
    return min(f_trop(p, a) for p, a in factors.items())

def R_trop_which(n):
    """Return (value, winning prime, winning exponent)."""
    factors = factorize(n)
    if not factors:
        return float('inf'), 0, 0
    best = None
    for p, a in factors.items():
        v = f_trop(p, a)
        if best is None or v < best[0]:
            best = (v, p, a)
    return best

# --- Part 1: R_trop(n) for n=2..100 ---
print("\n─── Part 1: R_trop(n) for n=2..100 ───")
print(f"{'n':>4} {'R_trop(n)':>12} {'winner':>10} {'R(n)':>12} {'factorization':>20}")
print("-" * 65)
trop_values = {}
for n in range(2, 101):
    val, wp, wa = R_trop_which(n)
    r_classic = float(R_fraction(n))
    factors = factorize(n)
    fact_str = "·".join(f"{p}^{a}" if a > 1 else str(p) for p, a in sorted(factors.items()))
    trop_values[n] = val
    print(f"{n:>4} {val:>12.6f} {f'{wp}^{wa}':>10} {r_classic:>12.6f} {fact_str:>20}")

# --- Part 2: R_trop(6) special? ---
print("\n─── Part 2: R_trop for perfect numbers and neighbors ───")
print(f"{'n':>4} {'R_trop(n)':>12} {'winner':>10} {'details':>40}")
print("-" * 70)
for n in [5, 6, 7, 27, 28, 29, 495, 496, 497]:
    val, wp, wa = R_trop_which(n)
    factors = factorize(n)
    details = ", ".join(f"f_trop({p},{a})={f_trop(p,a):.6f}" for p, a in sorted(factors.items()))
    print(f"{n:>4} {val:>12.6f} {f'{wp}^{wa}':>10} {details:>40}")

print(f"\n  R_trop(6) = min(f_trop(2,1), f_trop(3,1))")
print(f"           = min({f_trop(2,1):.6f}, {f_trop(3,1):.6f})")
print(f"           = {R_trop(6):.6f}")
print(f"  ln(2) = {math.log(2):.6f}")
print(f"  Match: {abs(R_trop(6) - math.log(2)) < 1e-12}")

# --- Part 3: Tropical gaps ---
print("\n─── Part 3: Tropical R distribution and gaps ───")

# Collect and sort unique values
all_trop = sorted(set(trop_values[n] for n in range(2, 101)))
print(f"\nUnique R_trop values (n=2..100): {len(all_trop)}")
print(f"{'rank':>5} {'R_trop':>12} {'count':>6} {'gap_to_next':>12} {'example_n':>10}")
print("-" * 50)

# Count occurrences
from collections import Counter
trop_counter = Counter()
trop_examples = {}
for n in range(2, 101):
    v = round(trop_values[n], 10)
    trop_counter[v] += 1
    if v not in trop_examples:
        trop_examples[v] = n

sorted_vals = sorted(trop_counter.keys())
for i, v in enumerate(sorted_vals[:30]):
    gap = sorted_vals[i+1] - v if i + 1 < len(sorted_vals) else float('nan')
    gap_str = f"{gap:.6f}" if not math.isnan(gap) else "---"
    print(f"{i+1:>5} {v:>12.6f} {trop_counter[v]:>6} {gap_str:>12} {trop_examples[v]:>10}")

# Gap analysis
print("\n─── Gap analysis ───")
gaps = []
for i in range(len(sorted_vals) - 1):
    gaps.append((sorted_vals[i+1] - sorted_vals[i], sorted_vals[i], sorted_vals[i+1]))
gaps.sort(reverse=True)
print("Largest gaps:")
print(f"{'rank':>5} {'gap':>12} {'from':>12} {'to':>12}")
print("-" * 45)
for i, (g, f, t) in enumerate(gaps[:10]):
    print(f"{i+1:>5} {g:>12.6f} {f:>12.6f} {t:>12.6f}")

# ASCII histogram of tropical R values
print("\n─── ASCII histogram of R_trop(n), n=2..100 ───")
nbins = 20
vals_list = [trop_values[n] for n in range(2, 101)]
vmin, vmax = min(vals_list), max(vals_list)
bin_width = (vmax - vmin) / nbins
bins = [0] * nbins
for v in vals_list:
    idx = min(int((v - vmin) / bin_width), nbins - 1)
    bins[idx] += 1

max_count = max(bins)
for i in range(nbins):
    lo = vmin + i * bin_width
    hi = lo + bin_width
    bar = "#" * int(bins[i] / max_count * 40) if max_count > 0 else ""
    print(f"  [{lo:>6.3f},{hi:>6.3f}) |{bar:<40}| {bins[i]:>3}")

# Compare classical R vs tropical R correlation
print("\n─── Classical R(n) vs Tropical R(n) correlation ───")
classic_vals = [float(R_fraction(n)) for n in range(2, 101)]
trop_vals_list = [trop_values[n] for n in range(2, 101)]

# Pearson correlation
n_pts = len(classic_vals)
mean_c = sum(classic_vals) / n_pts
mean_t = sum(trop_vals_list) / n_pts
cov = sum((c - mean_c) * (t - mean_t) for c, t in zip(classic_vals, trop_vals_list)) / n_pts
std_c = (sum((c - mean_c)**2 for c in classic_vals) / n_pts) ** 0.5
std_t = (sum((t - mean_t)**2 for t in trop_vals_list) / n_pts) ** 0.5
corr = cov / (std_c * std_t) if std_c * std_t > 0 else 0

print(f"  Pearson correlation: r = {corr:.6f}")
print(f"  Classical R mean:  {mean_c:.6f}")
print(f"  Tropical R mean:   {mean_t:.6f}")

# Final summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

print("""
H-TREE-2 (p-adic):
  - v_2(R(2^k)) = -(1 + v_2(k+1)) confirmed for k=1..15
  - R is multiplicative → p-adic valuations decompose over prime powers
  - |R(n)|_p shows structured dependence on v_p(n)

H-TREE-4 (Dirichlet ring):
  - σ·φ multiplicative on coprime pairs: """ + str(all_sp_mult) + """
  - id·τ multiplicative on coprime pairs: """ + str(all_it_mult) + """
  - R multiplicative: """ + str(all_sp_mult and all_it_mult) + """
  - (σ*1)(n) ≠ nτ(n) in general (ratio varies)
  - R(p) = (p²-1)/(2p) for all primes p
  - Dirichlet inverse R^(-1) exists and verified (R * R^(-1) = ε)

H-TREE-6 (tropical):
  - R_trop(6) = ln(2) ≈ 0.6931 (exact)
  - R_trop is piecewise, determined by smallest prime power contribution
  - Distribution shows clustering at small values (dominated by factor 2)
  - Classical vs tropical correlation: r = """ + f"{corr:.4f}" + """
""")

print("Done.")
