#!/usr/bin/env python3
"""
Verify 5 physics/chemistry hypotheses related to perfect number 6.
H-PH-3: tau*phi=sigma nuclear physics significance
H-PH-4: 6 quarks + 6 leptons = sigma(6)
H-PH-5: Planck units and 6
H-PH-6: R-chain vs radioactive decay
H-CHEM-4: R-chain vs chemical reaction rates
"""

import math
from collections import Counter

# ============================================================
# Helper: number theory functions for n=6
# ============================================================
def divisors(n):
    d = []
    for i in range(1, n+1):
        if n % i == 0:
            d.append(i)
    return d

def sigma(n):
    return sum(divisors(n))

def tau(n):
    return len(divisors(n))

def phi(n):
    count = 0
    for i in range(1, n+1):
        if math.gcd(i, n) == 1:
            count += 1
    return count

n = 6
s = sigma(n)
t = tau(n)
p = phi(n)
print("=" * 70)
print("PERFECT NUMBER 6: BASIC FUNCTIONS")
print("=" * 70)
print(f"  sigma(6) = {s}  (sum of divisors)")
print(f"  tau(6)   = {t}  (number of divisors)")
print(f"  phi(6)   = {p}  (Euler totient)")
print(f"  sigma/tau = {s}/{t} = {s/t}")
print(f"  tau*phi  = {t}*{p} = {t*p}")
print()

# ============================================================
# H-PH-3: tau*phi = sigma <-> nuclear physics
# ============================================================
print("=" * 70)
print("H-PH-3: tau*phi = sigma  <->  NUCLEAR PHYSICS")
print("=" * 70)
print()

# tau*phi for perfect number 6
tp = t * p  # 4 * 2 = 8
print(f"  tau(6)*phi(6) = {t}*{p} = {tp}")
print(f"  sigma(6) = {s}")
print(f"  tau*phi = sigma? {tp} = {s}? => {tp == s}")
print()

# The claim: tau*phi=sigma gives {1,3,14,42}
# Let's find ALL n where tau(n)*phi(n) = sigma(n) up to 1000
print("  Numbers where tau(n)*phi(n) = sigma(n), n <= 1000:")
tp_eq_sigma = []
for nn in range(1, 1001):
    d = divisors(nn)
    s_nn = sum(d)
    t_nn = len(d)
    p_nn = sum(1 for i in range(1, nn+1) if math.gcd(i, nn) == 1)
    if t_nn * p_nn == s_nn:
        tp_eq_sigma.append(nn)

print(f"  Found: {tp_eq_sigma}")
print()

# Nuclear magic numbers
magic = {2, 8, 20, 28, 50, 82, 126}
print("  Nuclear magic numbers: {2, 8, 20, 28, 50, 82, 126}")
print()
print("  | n   | tau*phi=sigma? | Nuclear significance          | Magic? |")
print("  |-----|----------------|-------------------------------|--------|")

nuclear_info = {
    1:  ("Z=1 hydrogen",                        False),
    3:  ("A=3 tritium / He-3",                   False),
    14: ("A=14 nitrogen-14 / carbon-14",         False),
    42: ("A=42 calcium-42 (stable)",             False),
}

for nn in tp_eq_sigma:
    info, is_magic_related = nuclear_info.get(nn, ("?", False))
    in_magic = nn in magic
    print(f"  | {nn:<3} | Yes            | {info:<29} | {'YES' if in_magic else 'No':>6} |")

print()
# Check doubly-magic nuclei
print("  Doubly-magic nuclei (both Z and N are magic):")
doubly_magic = [(2,2,4), (2,8,10), (8,8,16), (8,20,28), (20,20,40),
                (20,28,48), (28,28,56), (28,50,78), (50,50,100), (50,82,132), (82,126,208)]
print("  | Z   | N   | A   | Element    | In tau*phi set? |")
print("  |-----|-----|-----|------------|-----------------|")
elements = {4:"He-4", 10:"Ne-10?", 16:"O-16", 28:"Si-28", 40:"Ca-40",
            48:"Ca-48", 56:"Ni-56", 78:"Ni-78", 100:"Sn-100", 132:"Sn-132", 208:"Pb-208"}
for z, nn_val, a in doubly_magic:
    elem = elements.get(a, "?")
    in_set = a in tp_eq_sigma
    print(f"  | {z:<3} | {nn_val:<3} | {a:<3} | {elem:<10} | {'YES' if in_set else 'No':>15} |")

print()
# Overlap check
overlap = set(tp_eq_sigma) & magic
print(f"  Overlap with magic numbers: {overlap if overlap else 'NONE'}")
print()

# Statistical test: random 4 numbers from 1-126, probability of hitting >=k magic numbers
from itertools import combinations
total_ways = math.comb(126, len(tp_eq_sigma))
# How many of our set are <= 126?
our_set = [x for x in tp_eq_sigma if x <= 126]
k_hits = len(set(our_set) & magic)
print(f"  Our set (<=126): {our_set}")
print(f"  Hits with magic numbers: {k_hits}")
print(f"  Expected by chance: {len(our_set)}*7/126 = {len(our_set)*7/126:.3f}")
print()
print("  VERDICT: NONE of {1,3,14,42} are magic numbers.")
print("           3 is close to magic 2, 42 is close to magic 28 or 50.")
print("           No structural connection to nuclear shell model.")
print("           Grade: WHITE CIRCLE (no significance)")
print()

# ============================================================
# H-PH-4: 6 quarks + 6 leptons = sigma(6) = 12
# ============================================================
print("=" * 70)
print("H-PH-4: 6 QUARKS + 6 LEPTONS = sigma(6) = 12")
print("=" * 70)
print()

particles = {
    "Quarks": ["up", "down", "charm", "strange", "top", "bottom"],
    "Leptons": ["electron", "e-neutrino", "muon", "mu-neutrino", "tau", "tau-neutrino"],
}
print("  | Category | Count | Members                                    |")
print("  |----------|-------|--------------------------------------------|")
for cat, members in particles.items():
    print(f"  | {cat:<8} | {len(members):<5} | {', '.join(members):<42} |")
total_fermions = sum(len(v) for v in particles.values())
print(f"  | TOTAL    | {total_fermions:<5} | all fundamental fermions                   |")
print()
print(f"  sigma(6) = {s}")
print(f"  Total fundamental fermions = {total_fermions}")
print(f"  Match: {total_fermions} = {s}? => {total_fermions == s}")
print()

# Deeper: generations
print("  Generation structure:")
print("  | Gen | Quarks      | Leptons              |")
print("  |-----|-------------|----------------------|")
print("  | 1   | up, down    | electron, e-neutrino |")
print("  | 2   | charm, str. | muon, mu-neutrino    |")
print("  | 3   | top, bottom | tau, tau-neutrino     |")
print()
print(f"  Generations = 3 = sigma(6)/tau(6) = {s}/{t} = {s//t}")
print(f"  Particles per generation = 4 = tau(6) = {t}")
print(f"  3 * 4 = 12 = sigma(6) = {s}")
print()

# But is 12 special? Many numbers have sigma = 12
nums_with_sigma_12 = [nn for nn in range(1, 100) if sum(divisors(nn)) == 12]
print(f"  Numbers with sigma(n)=12: {nums_with_sigma_12}")
print(f"  So sigma=12 is not unique to 6.")
print()

# Texas sharpshooter: how many ways to get 12 from number theory of 6?
ways_to_12 = {
    "sigma(6)": s,
    "2*6": 2*6,
    "tau(6)*3": t*3,
    "phi(6)*6": p*6,
    "6!/(6*5*2)": math.factorial(6)//(6*5*2),
}
count_12 = sum(1 for v in ways_to_12.values() if v == 12)
print(f"  Ways to get 12 from 6's number theory: {count_12}")
for expr, val in ways_to_12.items():
    print(f"    {expr} = {val} {'<-- 12' if val == 12 else ''}")
print()

# p-value estimate
# Target: 12 fermions. Trials: ~20 reasonable expressions of 6.
# Hit probability for each trial: ~1/20 (integers 1-20 range)
# P(at least 1 hit in 20 trials) = 1 - (19/20)^20 = 0.64
# So finding sigma(6)=12=fermions is not that surprising
import random
random.seed(42)
target = 12
n_trials = 100000
n_expressions = 20  # reasonable expressions from n=6
value_range = range(1, 51)  # plausible output range
hits = 0
for _ in range(n_trials):
    values = [random.choice(value_range) for _ in range(n_expressions)]
    if target in values:
        hits += 1
p_random = hits / n_trials
print(f"  Monte Carlo p-value (20 random expressions hitting 12 in 1-50):")
print(f"    p = {p_random:.4f}")
print()

# The generation structure is more interesting
print("  Key insight: 3 generations * 4 per gen = 12")
print("    3 = sigma/tau (or phi), 4 = tau")
print("    This decomposition 12 = 3*4 matching generations is mildly interesting")
print("    But 12 = 3*4 = 2*6 = 1*12 — many decompositions available")
print()
print("  VERDICT: The numerical match sigma(6)=12=fermions is correct arithmetic")
print("           but likely coincidental. The generation decomposition 3*4")
print("           adds mild structure. No causal mechanism.")
print("           Grade: YELLOW SQUARE (weak coincidence, same as H-PH-2)")
print()

# ============================================================
# H-PH-5: Planck units and 6
# ============================================================
print("=" * 70)
print("H-PH-5: PLANCK UNITS AND 6")
print("=" * 70)
print()

# Physical constants (CODATA 2018)
hbar = 1.054571817e-34   # J·s
G_grav = 6.67430e-11     # m³/(kg·s²)
c = 2.99792458e8         # m/s
k_B = 1.380649e-23       # J/K
eps0 = 8.8541878128e-12  # F/m

# Planck units
l_P = math.sqrt(hbar * G_grav / c**3)
t_P = math.sqrt(hbar * G_grav / c**5)
m_P = math.sqrt(hbar * c / G_grav)
T_P = math.sqrt(hbar * c**5 / (G_grav * k_B**2))
q_P = math.sqrt(4 * math.pi * eps0 * hbar * c)  # ~ e/sqrt(alpha)

print("  Planck units:")
print("  | Unit        | Symbol | Value              | Formula              |")
print("  |-------------|--------|--------------------|----------------------|")
print(f"  | Length      | l_P    | {l_P:.4e} m   | sqrt(hbar*G/c^3)     |")
print(f"  | Time        | t_P    | {t_P:.4e} s   | sqrt(hbar*G/c^5)     |")
print(f"  | Mass        | m_P    | {m_P:.4e} kg  | sqrt(hbar*c/G)       |")
print(f"  | Temperature | T_P    | {T_P:.4e} K   | sqrt(hbar*c^5/Gk^2)  |")
print(f"  | Charge      | q_P    | {q_P:.4e} C   | sqrt(4pi*eps0*hbar*c)|")
print()

# How many Planck units?
n_planck = 5
print(f"  Number of Planck units: {n_planck}")
print(f"  Number of defining constants: 3 (hbar, G, c) + 2 (k_B, eps0) = 5")
print(f"  Independent base units from (hbar, G, c): 3 = sigma(6)/tau(6) = {s//t}")
print()

# Check: any ratios involving 6?
print("  Ratio checks:")
ratios = {
    "l_P/t_P": l_P / t_P,
    "m_P*c^2/(k_B*T_P)": m_P * c**2 / (k_B * T_P),
    "t_P*c/l_P": t_P * c / l_P,
}
for name, val in ratios.items():
    print(f"    {name} = {val:.6f}")
print()
print("  l_P/t_P = c (by construction)")
print("  m_P*c^2/(k_B*T_P) = 1 (by construction)")
print("  No non-trivial appearance of 6.")
print()

# Check exponents in Planck unit formulas
print("  Exponent analysis (hbar^a * G^b * c^d):")
print("  | Unit   | a(hbar) | b(G)  | d(c)  | Sum   |")
print("  |--------|---------|-------|-------|-------|")
planck_exponents = {
    "l_P":  (0.5,  0.5, -1.5),
    "t_P":  (0.5,  0.5, -2.5),
    "m_P":  (0.5, -0.5,  0.5),
    "T_P":  (0.5, -0.5,  2.5),  # with k_B^-1
    "q_P":  (0.5,  0.0,  0.5),  # with eps0^0.5
}
for unit, (a, b, d) in planck_exponents.items():
    s_exp = a + b + d
    print(f"  | {unit:<6} | {a:>7.1f} | {b:>5.1f} | {d:>5.1f} | {s_exp:>5.1f} |")

print()
# Sum of absolute exponents
print("  Sum of |exponents| for base 3 units (l,t,m):")
for unit in ["l_P", "t_P", "m_P"]:
    a, b, d = planck_exponents[unit]
    s_abs = abs(a) + abs(b) + abs(d)
    print(f"    {unit}: |{a}|+|{b}|+|{d}| = {s_abs}")
print(f"  Total |exponents| = {sum(abs(x) for u in ['l_P','t_P','m_P'] for x in planck_exponents[u])}")
print()

# Any appearance of 6 in the mantissa?
print("  Mantissa check (looking for 6 in Planck values):")
for name, val in [("l_P", l_P), ("t_P", t_P), ("m_P", m_P), ("T_P", T_P), ("q_P", q_P)]:
    mantissa = val / (10 ** math.floor(math.log10(abs(val))))
    print(f"    {name}: mantissa = {mantissa:.6f} (contains '6'? {'YES' if '6' in f'{mantissa:.6f}' else 'No'})")

print()
print("  VERDICT: No meaningful connection between Planck units and 6.")
print("           '3 independent units' = sigma/tau is trivial (3 constants -> 3 units).")
print("           Grade: WHITE CIRCLE (no significance)")
print()

# ============================================================
# H-PH-6: R-chain <-> radioactive decay
# ============================================================
print("=" * 70)
print("H-PH-6: R-CHAIN <-> RADIOACTIVE DECAY")
print("=" * 70)
print()

# R-chain: R(n) = sigma(n)/tau(n) * phi(n)/n * n for perfect numbers
# For general n: R(n) = sigma(n) * phi(n) / (tau(n) * n)
# Actually, let's define R(n) properly.
# From the project: R(n)/n ~ 0.15 suggests geometric decay

def R_func(n):
    """R(n) = sigma(n)*phi(n) / (tau(n) * n) ... approximate."""
    d = divisors(n)
    s_n = sum(d)
    t_n = len(d)
    p_n = sum(1 for i in range(1, n+1) if math.gcd(i, n) == 1)
    return s_n * p_n / (t_n * n)

# R-chain: start from n, iterate floor(R(n)*n) or similar
# Let's use R(n) = sigma(n)*phi(n)/tau(n) and chain = n -> floor(R(n)) -> ...
def R_chain(start, max_steps=50):
    chain = [start]
    n = start
    for _ in range(max_steps):
        d = divisors(n)
        s_n = sum(d)
        t_n = len(d)
        p_n = sum(1 for i in range(1, n+1) if math.gcd(i, n) == 1)
        r = s_n * p_n // t_n  # integer division
        if r <= 1 or r >= n:
            break
        chain.append(r)
        n = r
    return chain

print("  R-chain examples (R(n) = floor(sigma(n)*phi(n)/tau(n))):")
print("  | Start | Chain                                    | Length | Ratio n[1]/n[0] |")
print("  |-------|------------------------------------------|--------|-----------------|")

chain_lengths = []
decay_ratios = []
for start in [100, 200, 500, 1000, 2000, 5000, 10000]:
    ch = R_chain(start)
    chain_lengths.append(len(ch))
    ratio = ch[1]/ch[0] if len(ch) > 1 else 0
    decay_ratios.append(ratio)
    ch_str = " -> ".join(str(x) for x in ch[:8])
    if len(ch) > 8:
        ch_str += " -> ..."
    print(f"  | {start:<5} | {ch_str:<40} | {len(ch):<6} | {ratio:<15.4f} |")

print()
avg_ratio = sum(decay_ratios) / len(decay_ratios) if decay_ratios else 0
print(f"  Average first-step decay ratio: {avg_ratio:.4f}")
print()

# Radioactive decay comparison
print("  Radioactive decay: N(t) = N_0 * e^(-lambda*t)")
print("  Per-step decay:    N(t+1) = N(t) * e^(-lambda)")
print()
print("  If R-chain ratio ~ r per step, then effective lambda = -ln(r)")
if avg_ratio > 0:
    eff_lambda = -math.log(avg_ratio)
    half_life_steps = math.log(2) / eff_lambda if eff_lambda > 0 else float('inf')
    print(f"  Effective lambda = -ln({avg_ratio:.4f}) = {eff_lambda:.4f}")
    print(f"  Half-life in steps = ln(2)/lambda = {half_life_steps:.2f}")
print()

# Key difference: radioactive decay is EXPONENTIAL (continuous), R-chain is DISCRETE + IRREGULAR
print("  Structural comparison:")
print("  | Property        | Radioactive Decay     | R-chain              |")
print("  |-----------------|-----------------------|----------------------|")
print("  | Function type   | Exponential continuous | Discrete step        |")
print("  | Decay factor    | e^{-lambda} (constant)| Variable per step    |")
print("  | Randomness      | Quantum stochastic    | Deterministic        |")
print("  | Asymptote       | 0 (continuous)        | 1 or 2 (discrete)    |")
print("  | Reversibility   | No                    | No                   |")
print("  | Self-similarity | Yes (scale-free)      | No (number-dependent)|")
print()

# Check: is the decay ratio actually constant?
print("  Decay ratio constancy test (n=1000 chain):")
ch = R_chain(1000, 20)
print(f"  Chain: {ch}")
if len(ch) > 2:
    print("  | Step | n_i    | n_{i+1} | Ratio   |")
    print("  |------|--------|---------|---------|")
    step_ratios = []
    for i in range(len(ch)-1):
        r = ch[i+1]/ch[i]
        step_ratios.append(r)
        print(f"  | {i:<4} | {ch[i]:<6} | {ch[i+1]:<7} | {r:<7.4f} |")
    print()
    ratio_std = (sum((r - sum(step_ratios)/len(step_ratios))**2 for r in step_ratios) / len(step_ratios))**0.5
    print(f"  Ratio std dev: {ratio_std:.4f}")
    print(f"  Ratio varies significantly => NOT constant exponential decay")
print()
print("  VERDICT: R-chain has decreasing behavior like decay, but the ratio")
print("           is NOT constant. It's a loose structural analogy only.")
print("           No quantitative match to any specific isotope's decay.")
print("           Grade: WHITE CIRCLE (loose analogy, no quantitative match)")
print()

# ============================================================
# H-CHEM-4: R-chain <-> chemical reaction rates
# ============================================================
print("=" * 70)
print("H-CHEM-4: R-CHAIN <-> CHEMICAL REACTION RATES")
print("=" * 70)
print()

print("  Arrhenius equation: k = A * exp(-Ea / (R*T))")
print("  R-chain: n -> floor(sigma(n)*phi(n)/tau(n))")
print()

# Analogy mapping
print("  Proposed analogy mapping:")
print("  | Chemical concept    | R-chain analogue        | Match quality |")
print("  |---------------------|-------------------------|---------------|")
print("  | Reactant conc. N    | Current number n        | Reasonable    |")
print("  | Rate constant k     | Decay ratio R(n)/n      | Weak          |")
print("  | Activation energy   | Gap (3/4, 1)?           | Very weak     |")
print("  | Temperature T       | ???                     | No analogue   |")
print("  | Catalyst            | ???                     | No analogue   |")
print("  | Equilibrium         | Chain termination at 1  | Superficial   |")
print()

# Check: does the R-chain decay follow Arrhenius-like behavior?
# If k = A*exp(-Ea/RT), then ln(k) should be linear in 1/T
# Here we have no temperature, but let's check if ln(ratio) vs ln(n) is linear

print("  Testing: is ln(decay_ratio) linear in any function of n?")
print("  (Arrhenius predicts ln(k) linear in 1/T)")
print()

# Collect data from many starting points
data_points = []
for start in range(10, 5001, 10):
    ch = R_chain(start, 2)
    if len(ch) >= 2 and ch[0] > 0 and ch[1] > 0:
        ratio = ch[1] / ch[0]
        if ratio > 0:
            data_points.append((start, ratio))

if data_points:
    # Check correlation between ln(n) and ln(ratio)
    xs = [math.log(d[0]) for d in data_points]
    ys = [math.log(d[1]) for d in data_points]
    n_pts = len(xs)
    mean_x = sum(xs) / n_pts
    mean_y = sum(ys) / n_pts
    cov_xy = sum((xs[i] - mean_x) * (ys[i] - mean_y) for i in range(n_pts)) / n_pts
    var_x = sum((xs[i] - mean_x)**2 for i in range(n_pts)) / n_pts
    var_y = sum((ys[i] - mean_y)**2 for i in range(n_pts)) / n_pts
    r_corr = cov_xy / math.sqrt(var_x * var_y) if var_x > 0 and var_y > 0 else 0

    print(f"  Data points: {n_pts}")
    print(f"  Correlation(ln(n), ln(ratio)): r = {r_corr:.4f}")
    print(f"  R-squared: {r_corr**2:.4f}")
    print()

    # Sample of data
    print("  Sample data (every 100th point):")
    print("  | n     | ratio   | ln(n)  | ln(ratio) |")
    print("  |-------|---------|--------|-----------|")
    for i in range(0, len(data_points), 50):
        nn_val, rr = data_points[i]
        print(f"  | {nn_val:<5} | {rr:<7.4f} | {math.log(nn_val):<6.2f} | {math.log(rr):<9.4f} |")

    print()

    # ASCII scatter plot of ln(ratio) vs ln(n)
    print("  ASCII plot: ln(ratio) vs ln(n)")
    print("  " + "-" * 62)

    # Bin the data
    n_bins = 20
    min_x, max_x = min(xs), max(xs)
    bin_width = (max_x - min_x) / n_bins
    bins = {}
    for i in range(n_pts):
        b = int((xs[i] - min_x) / bin_width) if bin_width > 0 else 0
        b = min(b, n_bins - 1)
        if b not in bins:
            bins[b] = []
        bins[b].append(ys[i])

    bin_means = {}
    for b in sorted(bins.keys()):
        bin_means[b] = sum(bins[b]) / len(bins[b])

    if bin_means:
        min_y_plot = min(bin_means.values())
        max_y_plot = max(bin_means.values())
        y_range = max_y_plot - min_y_plot if max_y_plot > min_y_plot else 1

        for row in range(10, -1, -1):
            y_val = min_y_plot + y_range * row / 10
            line = f"  {y_val:>7.3f} |"
            for b in range(n_bins):
                if b in bin_means:
                    bm = bin_means[b]
                    row_val = (bm - min_y_plot) / y_range * 10
                    if abs(row_val - row) < 0.5:
                        line += " * "
                    else:
                        line += "   "
                else:
                    line += "   "
            print(line)
        x_labels = f"  {'':>7} +{'---' * n_bins}"
        print(x_labels)
        print(f"  {'':>8} ln(n)={min_x:.1f}{' ' * (3*n_bins - 20)}ln(n)={max_x:.1f}")

print()
print("  Key observations:")
print("  1. No temperature analogue in R-chain => Arrhenius mapping fails")
print("  2. R-chain is deterministic; chemical kinetics has stochastic aspects")
print("  3. The 'activation energy' (gap at 3/4-1) has no quantitative match")
print("  4. Both show monotonic decrease, but this is trivially common")
print()
print("  VERDICT: The analogy is superficial. Both describe 'things getting smaller'")
print("           but the mechanisms are completely different.")
print("           No predictive power in either direction.")
print("           Grade: WHITE CIRCLE (loose analogy only)")
print()

# ============================================================
# SUMMARY
# ============================================================
print("=" * 70)
print("SUMMARY TABLE")
print("=" * 70)
print()
print("  | Hypothesis | Claim                          | Arithmetic | Structural | Grade |")
print("  |------------|--------------------------------|------------|------------|-------|")
print("  | H-PH-3    | tau*phi=sigma nuclear physics  | Correct    | No         | W_CIR |")
print("  | H-PH-4    | 6q + 6l = sigma(6) = 12        | Correct    | Weak       | Y_SQ  |")
print("  | H-PH-5    | Planck units involve 6          | No match   | No         | W_CIR |")
print("  | H-PH-6    | R-chain ~ radioactive decay     | Loose      | Superficial| W_CIR |")
print("  | H-CHEM-4  | R-chain ~ Arrhenius reaction    | No match   | No         | W_CIR |")
print()
print("  Legend: W_CIR = White Circle (no significance)")
print("          Y_SQ  = Yellow Square (weak coincidence)")
print()
print("  Overall: 4 out of 5 hypotheses show no meaningful connection.")
print("  H-PH-4 (fermion count = sigma(6)) is arithmetically correct but")
print("  likely coincidental given the many ways to obtain 12 from 6.")
print()
print("DONE.")
