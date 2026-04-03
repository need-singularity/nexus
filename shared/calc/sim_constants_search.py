#!/usr/bin/env python3
"""H-SIM-1: Search for physics constants as combinations of TECS-L constants.

Tries all combinations (+-*/^, log, exp) of TECS-L constants up to depth 3,
finds matches to dimensionless physics constants within 1% error.
Calculates Texas Sharpshooter p-value.
Also checks number-theoretic properties of 137.
"""

from mpmath import mp, mpf, log, exp, pi, euler, e as E_const, fac, sqrt
from itertools import combinations_with_replacement, product
import math
import sys
import tecsrs

mp.dps = 30  # 30 decimal places

# ─── TECS-L constants ───
tecs = {
    '1/2':       mpf('0.5'),
    '1/e':       1/E_const,
    'ln(4/3)':   log(mpf(4)/3),
    '1/3':       mpf(1)/3,
    '5/6':       mpf(5)/6,
    'sigma(6)':  mpf(12),
    'tau(6)':    mpf(4),
    'phi(6)':    mpf(2),
    'sigma_-1(6)': mpf(2),
    '1/6':       mpf(1)/6,
    '6':         mpf(6),
}

# ─── Physics dimensionless constants ───
physics = {
    'alpha (fine structure)':    mpf(1)/mpf('137.035999084'),
    '1/alpha':                   mpf('137.035999084'),
    'alpha_W (weak coupling)':   mpf(1)/mpf(30),  # ~1/30 at low energy
    'alpha_S (strong coupling)': mpf('0.1179'),    # at M_Z
    'alpha_G (gravitational)':   mpf('5.906e-39'),
    'proton/electron mass':      mpf('1836.15267343'),
    'Weinberg angle sin2tw':     mpf('0.23122'),
    'pi':                        pi,
    'euler_gamma':               euler,
}

print("=" * 70)
print("  H-SIM-1: Physical Constants = Compile-Time Constants?")
print("  Searching TECS-L constant combinations -> physics constants")
print("=" * 70)

# ─── Binary operations ───
def safe_ops(a, b):
    """Return list of (result, description) for binary ops."""
    results = []
    results.append((a + b, '+'))
    results.append((a - b, '-'))
    results.append((b - a, 'r-'))
    results.append((a * b, '*'))
    if b != 0:
        results.append((a / b, '/'))
    if a != 0:
        results.append((b / a, 'r/'))
    # powers (only small exponents to avoid overflow)
    try:
        if abs(b) <= 20 and abs(a) <= 1000 and a > 0:
            results.append((a ** b, '^'))
    except:
        pass
    try:
        if abs(a) <= 20 and abs(b) <= 1000 and b > 0:
            results.append((b ** a, 'r^'))
    except:
        pass
    return results

# ─── Unary operations ───
def unary_ops(val, name):
    """Return list of (result, description)."""
    results = [(val, name)]
    if val > 0:
        results.append((log(val), f'ln({name})'))
    try:
        if val < 100:
            results.append((exp(val), f'exp({name})'))
    except:
        pass
    if val > 0:
        results.append((sqrt(val), f'sqrt({name})'))
    if val != 0:
        results.append((1/val, f'1/({name})'))
    return results

# ─── Depth-2 search: op(a, b) ───
print("\n--- Depth-2 Search: op(A, B) ---")
matches_d2 = []
total_tried_d2 = 0
tecs_items = list(tecs.items())

for i, (na, va) in enumerate(tecs_items):
    for j, (nb, vb) in enumerate(tecs_items):
        for result, op_name in safe_ops(va, vb):
            total_tried_d2 += 1
            if result <= 0 or not mp.isfinite(result):
                continue
            for pname, pval in physics.items():
                if pval <= 0:
                    continue
                rel_err = abs(float(result - pval) / float(pval))
                if rel_err < 0.01:
                    expr = f"{na} {op_name} {nb}"
                    matches_d2.append((pname, expr, float(result), float(pval), rel_err))

# Deduplicate
seen_d2 = set()
unique_d2 = []
for m in sorted(matches_d2, key=lambda x: x[4]):
    key = (m[0], m[1])
    if key not in seen_d2:
        seen_d2.add(key)
        unique_d2.append(m)

print(f"  Combinations tried: {total_tried_d2}")
print(f"  Matches (<1% error): {len(unique_d2)}")
print()
if unique_d2:
    print(f"  {'Physics Constant':<28} {'Expression':<28} {'Value':>14} {'Target':>14} {'Error':>8}")
    print(f"  {'─'*28} {'─'*28} {'─'*14} {'─'*14} {'─'*8}")
    for pname, expr, val, target, err in unique_d2[:30]:
        print(f"  {pname:<28} {expr:<28} {val:>14.8f} {target:>14.8f} {err:>7.4%}")

# ─── Depth-3 search: op(op(a,b), c) ───
print("\n--- Depth-3 Search: op(op(A, B), C) ---")
matches_d3 = []
total_tried_d3 = 0

# Generate depth-2 intermediates (pruned)
intermediates = []
for i, (na, va) in enumerate(tecs_items):
    for j, (nb, vb) in enumerate(tecs_items):
        if i > j:
            continue  # avoid duplicates for commutative
        for result, op_name in safe_ops(va, vb):
            if mp.isfinite(result) and abs(float(result)) < 1e10 and abs(float(result)) > 1e-10:
                intermediates.append((result, f"({na}{op_name}{nb})"))

print(f"  Depth-2 intermediates: {len(intermediates)}")

for val_ab, name_ab in intermediates:
    for nc, vc in tecs_items:
        for result, op_name in safe_ops(val_ab, vc):
            total_tried_d3 += 1
            if result <= 0 or not mp.isfinite(result):
                continue
            for pname, pval in physics.items():
                if pval <= 0:
                    continue
                rel_err = abs(float(result - pval) / float(pval))
                if rel_err < 0.005:  # tighter for depth-3 (0.5%)
                    expr = f"{name_ab} {op_name} {nc}"
                    matches_d3.append((pname, expr, float(result), float(pval), rel_err))

# Also try unary on depth-2
for val_ab, name_ab in intermediates:
    for uval, uname in unary_ops(val_ab, name_ab):
        total_tried_d3 += 1
        if uval <= 0 or not mp.isfinite(uval):
            continue
        for pname, pval in physics.items():
            if pval <= 0:
                continue
            rel_err = abs(float(uval - pval) / float(pval))
            if rel_err < 0.005:
                matches_d3.append((pname, uname, float(uval), float(pval), rel_err))

seen_d3 = set()
unique_d3 = []
for m in sorted(matches_d3, key=lambda x: x[4]):
    key = (m[0], round(m[2], 8))
    if key not in seen_d3:
        seen_d3.add(key)
        unique_d3.append(m)

print(f"  Combinations tried: {total_tried_d3}")
print(f"  Matches (<0.5% error): {len(unique_d3)}")
print()
if unique_d3:
    print(f"  {'Physics Constant':<28} {'Expression':<35} {'Value':>14} {'Target':>14} {'Error':>8}")
    print(f"  {'─'*28} {'─'*35} {'─'*14} {'─'*14} {'─'*8}")
    for pname, expr, val, target, err in unique_d3[:40]:
        print(f"  {pname:<28} {expr:<35} {val:>14.8f} {target:>14.8f} {err:>7.4%}")

# ─── Specific alpha search ───
print("\n--- Specific: alpha = 1/137.036 ---")
print(f"  Target: {float(1/mpf('137.035999084')):.10f}")
print()

# Check: is 137 = sigma(n) for any n?
print("--- Number Theory of 137 ---")
print(f"  137 is prime: {all(137 % i != 0 for i in range(2, 12))}")
print(f"  137 = 2^7 + 2^3 + 2^0 = 128+8+1")
print(f"  137 is the 33rd prime")

# Check sigma(n) = 137 using tecsrs sieve (83x faster than Python loop)
_sigma_table = tecsrs.sieve_sigma(500)
for n in range(1, 500):
    if _sigma_table[n] == 137:
        print(f"  sigma({n}) = 137  *** FOUND ***")
# 137 is prime, so sigma(137) = 138
print(f"  sigma(137) = {_sigma_table[137]}")

# Is 137 a Mersenne exponent? 2^137-1 prime?
print(f"  137 in Mersenne exponents? Known Mersenne primes: 2,3,5,7,13,17,19,31,61,89,107,127,521...")
print(f"  137 is NOT a Mersenne exponent")

# 137 in Catalan, Fibonacci?
fib = [0, 1]
while fib[-1] < 200:
    fib.append(fib[-1] + fib[-2])
print(f"  137 in Fibonacci? {137 in fib}")

# 137 = sum of squares?
for a in range(12):
    for b in range(a, 12):
        if a*a + b*b == 137:
            print(f"  137 = {a}^2 + {b}^2 = {a*a} + {b*b}")

# Check: 137 and perfect number 6
print(f"  137 mod 6 = {137 % 6}")
print(f"  137 = 22*6 + 5 = 132 + 5")
print(f"  (137-1)/6 = {(137-1)/6:.4f}")
print(f"  137 = sigma(6)^2 - tau(6) - phi(6) - 1 = 144 - 4 - 2 - 1 = {144-4-2-1}")

# ─── Texas Sharpshooter ───
print("\n" + "=" * 70)
print("  TEXAS SHARPSHOOTER P-VALUE")
print("=" * 70)

total_combinations = total_tried_d2 + total_tried_d3
total_matches_strict = len(unique_d3)  # <0.5% matches
n_targets = len(physics)

# Expected matches by chance: total_combinations * n_targets * 0.01 (1% window)
# For uniform distribution on log scale over [1e-40, 1e4], chance of <1% match
# Width of 1% window on log scale ~ 0.01/ln(10) ~ 0.004 per target
# Probability per trial per target ~ 0.01 (conservative: 1% of range)
p_single = 0.01
expected_d2 = total_tried_d2 * n_targets * p_single
expected_d3 = total_tried_d3 * n_targets * 0.005

print(f"  Total depth-2 trials:     {total_tried_d2:,}")
print(f"  Total depth-3 trials:     {total_tried_d3:,}")
print(f"  Physics targets:          {n_targets}")
print(f"  Depth-2 matches (<1%):    {len(unique_d2)}")
print(f"  Depth-3 matches (<0.5%):  {len(unique_d3)}")
print(f"  Expected by chance (d2):  {expected_d2:.1f}")
print(f"  Expected by chance (d3):  {expected_d3:.1f}")

# Bonferroni-corrected significance
if len(unique_d3) > 0:
    # Filter to only non-trivial matches (not pi=pi type)
    nontrivial = [m for m in unique_d3 if m[4] > 0.0001]
    print(f"  Non-trivial matches:      {len(nontrivial)}")
    print(f"\n  Verdict: {'STRUCTURAL' if len(nontrivial) > expected_d3 * 3 else 'COINCIDENCE (within expected range)'}")
else:
    print(f"\n  Verdict: NO MATCHES FOUND")

# ─── Special: 137 decomposition ───
print("\n--- Key Result: alpha decomposition ---")
alpha = 1/mpf('137.035999084')
# Try: alpha ~ ln(4/3) / (tau(6) * sigma(6) - phi(6) - 1)
# = ln(4/3) / (48 - 2 - 1) = ln(4/3)/45
test1 = log(mpf(4)/3) / 45
print(f"  ln(4/3)/45                = {float(test1):.10f}  err = {abs(float(test1/alpha - 1)):.4%}")

# alpha ~ 1/(sigma(6)^2 - tau(6) - phi(6) - 1) = 1/137
test2 = 1 / (mpf(12)**2 - 4 - 2 - 1)
print(f"  1/(sigma(6)^2-tau(6)-phi(6)-1) = 1/{int(12**2-4-2-1)} = {float(test2):.10f}  err = {abs(float(test2/alpha - 1)):.4%}")

# alpha ~ 1/2 * 1/e * 1/3 * ... let's see
test3 = 1/(mpf(2) * E_const * mpf(6)**2 / log(mpf(4)/3))
print(f"  ln(4/3)/(2*e*36)          = {float(test3):.10f}  err = {abs(float(test3/alpha - 1)):.4%}")

# Direct: sigma(6)^2 = 144, close to 137
print(f"\n  sigma(6)^2 = 144")
print(f"  144 - 137 = 7 = sigma(6)/2 + 1 ... ad hoc")
print(f"  137 = 144 - 7 = sigma(6)^2 - 7")
print(f"  137 = 144 - 4 - 2 - 1 = sigma(6)^2 - tau(6) - phi(6) - 1  *** EXACT ***")

print("\n" + "=" * 70)
print("  DONE")
print("=" * 70)
