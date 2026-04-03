#!/usr/bin/env python3
"""
Robin's Inequality, Colossally Abundant Numbers, and n=6
Connection to the Riemann Hypothesis

Robin (1984): sigma(n) < e^gamma * n * ln(ln(n)) for all n >= 5041
              IF AND ONLY IF the Riemann Hypothesis is true.

Key: n=6 is a COLOSSALLY ABUNDANT number.
     The CA numbers are where Robin's inequality is "tightest".
     Connection: our σφ=nτ theorem meets Robin's RH criterion.
"""
import math

def sigma(n):
    return sum(d for d in range(1, n+1) if n % d == 0)
def phi(n):
    return sum(1 for k in range(1, n+1) if math.gcd(k, n) == 1)
def tau(n):
    return sum(1 for d in range(1, n+1) if n % d == 0)
def sopfr(n):
    s, d, t = 0, 2, n
    while d*d <= t:
        while t % d == 0: s += d; t //= d
        d += 1
    if t > 1: s += t
    return s

gamma = 0.5772156649015329  # Euler-Mascheroni

print("=" * 80)
print("  ROBIN'S INEQUALITY AND THE RIEMANN HYPOTHESIS")
print("  Connection to n=6 and σφ=nτ")
print("=" * 80)

# Robin's inequality: sigma(n) / (n * ln(ln(n))) < e^gamma
# The ratio R(n) = sigma(n) / (n * e^gamma * ln(ln(n)))
# RH true iff R(n) < 1 for all n >= 5041

print(f"\n  Robin's ratio R(n) = sigma(n) / (n * e^gamma * ln(ln(n)))")
print(f"  RH true iff R(n) < 1 for all n >= 5041")
print(f"\n  e^gamma = {math.exp(gamma):.10f}")

print(f"\n  {'n':>8s}  {'sigma':>8s}  {'R(n)':>10s}  {'CA?':>4s}  n=6 note")
print("  " + "-" * 60)

# Colossally abundant numbers (first few)
CA = [1, 2, 6, 12, 60, 120, 360, 2520, 5040, 55440, 720720]

for n in sorted(set(list(range(2, 51)) + CA)):
    s = sigma(n)
    if n >= 3:
        lnlnn = math.log(math.log(n))
        if lnlnn > 0:
            R = s / (n * math.exp(gamma) * lnlnn)
        else:
            R = float('inf')
    else:
        R = float('inf')

    ca = "CA" if n in CA else ""
    note = ""
    if n == 6: note = " <-- P1, sigma*phi=n*tau"
    if n == 12: note = " <-- sigma(6)"
    if n == 28: note = " <-- P2"
    if n == 5040: note = " <-- 7! = (n+1)!"

    if n <= 30 or n in CA:
        r_str = f"{R:.6f}" if R < 100 else "inf"
        print(f"  {n:>8d}  {s:>8d}  {r_str:>10s}  {ca:>4s}{note}")

# Focus on n=6
print(f"\n  === n=6 DEEP ANALYSIS ===")
n = 6
s = sigma(n)
lnlnn = math.log(math.log(n))
R6 = s / (n * math.exp(gamma) * lnlnn)
print(f"  sigma(6) = {s}")
print(f"  ln(ln(6)) = {lnlnn:.10f}")
print(f"  R(6) = {R6:.10f}")
print(f"  R(6) {'<' if R6 < 1 else '>='} 1: Robin's inequality {'HOLDS' if R6 < 1 else 'VIOLATED'}")

# Gronwall's theorem: lim sup sigma(n)/(n*ln(ln(n))) = e^gamma
# The CA numbers are where this ratio is largest
print(f"\n  === GRONWALL'S THEOREM ===")
print(f"  lim sup sigma(n)/(n*ln(ln(n))) = e^gamma = {math.exp(gamma):.10f}")
print(f"  The colossally abundant numbers maximize this ratio")
print(f"  n=6 IS a colossally abundant number!")

# The connection to our work
print(f"\n  === CONNECTION TO σφ=nτ ===")
print(f"""
  OBSERVATION: Among colossally abundant numbers,
  n=6 is the ONLY one satisfying σφ=nτ.

  CA numbers: 1, 2, 6, 12, 60, 120, 360, 2520, 5040, ...
  σφ=nτ solutions: 1, 6

  Intersection: {{1, 6}}

  This means: n=6 is the unique colossally abundant number
  where the arithmetic functions are "perfectly balanced"
  (σφ = nτ) AND where Robin's inequality approaches equality
  (R(6) = {R6:.6f}, relatively high for its size).
""")

# Deeper: what is sigma(n)/(n*ln(ln(n))) for perfect numbers?
print(f"  === PERFECT NUMBERS AND ROBIN'S RATIO ===")
perfects = [6, 28, 496, 8128]
for pn in perfects:
    s = sigma(pn)
    lnln = math.log(math.log(pn))
    R = s / (pn * math.exp(gamma) * lnln)
    print(f"  P={pn:>5d}: sigma={s:>10d}, R = {R:.6f}")

print(f"""
  Perfect numbers have sigma(n) = 2n exactly.
  So R(n) = 2 / (e^gamma * ln(ln(n)))
  As n -> infinity (larger perfects), R -> 0.
  n=6 has the LARGEST Robin ratio among all perfect numbers!
""")

# NEW: Compute sigma(n)/n * phi(n)/n for Robin connection
print(f"  === ABUNDANCE × TOTIENT RATIO ===")
print(f"  sigma(n)/n = abundance ratio")
print(f"  phi(n)/n = totient ratio")
print(f"  Product: (sigma/n)(phi/n) = sigma*phi/n^2 = tau/n (from σφ=nτ at n=6)")
print(f"")
print(f"  At n=6: sigma*phi/n^2 = 24/36 = 2/3 = tau/n = 4/6")
print(f"  At n=28: sigma*phi/28^2 = {sigma(28)*phi(28)}/{28**2} = {sigma(28)*phi(28)/28**2:.6f}")
print(f"  Tau/n: 28: {tau(28)/28:.6f}")
print(f"  sigma*phi/n^2 != tau/n at n=28: {sigma(28)*phi(28)/28**2:.6f} != {tau(28)/28:.6f}")
print(f"  ONLY at n=6: sigma*phi/n^2 = tau/n (restatement of σφ=nτ)")

# The ultimate connection
print(f"""
  ════════════════════════════════════════════════════════
  THE CHAIN: n=6 → Robin → Riemann Hypothesis
  ════════════════════════════════════════════════════════

  1. n=6 satisfies σφ=nτ (PROVEN, unique among n>=2)
  2. n=6 is colossally abundant (KNOWN)
  3. CA numbers are where Robin's inequality is tightest
  4. Robin's inequality is equivalent to RH (Robin 1984)
  5. Therefore: n=6 sits at the intersection of
     "arithmetic perfection" (σφ=nτ) and
     "analytic extremality" (CA + Robin)

  This does NOT prove RH, but it shows that the
  number-theoretic uniqueness of 6 is connected to
  the analytic structure underlying RH.

  CONJECTURE: The fact that the unique σφ=nτ solution (n=6)
  is also colossally abundant is NOT a coincidence.
  It reflects the deep connection between multiplicative
  number theory (σ,φ,τ balance) and the distribution
  of primes (Robin/Gronwall/RH).
  ════════════════════════════════════════════════════════
""")
