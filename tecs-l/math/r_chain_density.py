#!/usr/bin/env python3
"""Deeper analysis: density scaling, chain structure, why only 6->1."""

import math

# Density data from main run
data = [
    (100, 4),
    (500, 12),
    (1000, 18),
    (5000, 39),
    (10000, 52),
    (50000, 110),
    (100000, 151),
    (200000, 206),
    (500000, 288),
]

print("=" * 60)
print("DENSITY SCALING ANALYSIS")
print("=" * 60)

print(f"\n  {'N':>10} | {'count':>6} | {'density':>10} | {'log(N)':>8} | {'count/sqrt(N)':>14} | {'count/N^a':>10}")
print(f"  {'-'*10}-+-{'-'*6}-+-{'-'*10}-+-{'-'*8}-+-{'-'*14}-+-{'-'*10}")

# Check various scaling hypotheses
for N, c in data:
    d = c / N
    lnN = math.log(N)
    c_sqrtN = c / math.sqrt(N)
    # Try c ~ N^alpha: log(c) = alpha * log(N) + const
    print(f"  {N:>10} | {c:>6} | {d:>10.6f} | {lnN:>8.3f} | {c_sqrtN:>14.4f} | ")

# Log-log regression
print("\nLog-log fit: log(count) vs log(N)")
import numpy as np
xs = [math.log(N) for N, c in data]
ys = [math.log(c) for N, c in data]

# Simple linear regression
n = len(xs)
sx = sum(xs)
sy = sum(ys)
sxy = sum(x*y for x, y in zip(xs, ys))
sxx = sum(x*x for x in xs)
alpha = (n * sxy - sx * sy) / (n * sxx - sx * sx)
beta = (sy - alpha * sx) / n

print(f"  alpha (exponent) = {alpha:.4f}")
print(f"  const = {math.exp(beta):.4f}")
print(f"  => count(N) ~ {math.exp(beta):.3f} * N^{alpha:.4f}")
print(f"  => density(N) ~ N^{alpha - 1:.4f} -> {'0' if alpha < 1 else 'const' if abs(alpha-1)<0.01 else 'infinity'}")

# ASCII graph of log-log
print("\n  ASCII: log(count) vs log(N)")
print("  " + "-" * 52)
min_x, max_x = min(xs), max(xs)
min_y, max_y = min(ys), max(ys)
height = 15
width = 50
grid = [[' ' for _ in range(width)] for _ in range(height)]
for x, y in zip(xs, ys):
    col = int((x - min_x) / (max_x - min_x) * (width - 1))
    row = height - 1 - int((y - min_y) / (max_y - min_y) * (height - 1))
    grid[row][col] = '*'
# Fit line
for col in range(width):
    x = min_x + col * (max_x - min_x) / (width - 1)
    y_fit = alpha * x + beta
    row = height - 1 - int((y_fit - min_y) / (max_y - min_y) * (height - 1))
    if 0 <= row < height and grid[row][col] == ' ':
        grid[row][col] = '.'
for i, row in enumerate(grid):
    y_val = max_y - i * (max_y - min_y) / (height - 1)
    print(f"  {y_val:5.2f} |{''.join(row)}|")
print(f"        +{'-'*width}+")
print(f"        {min_x:.1f}{' '*(width-8)}{max_x:.1f}")
print(f"        {'log(N)':^{width}}")

# Why is R(n)=1 equivalent to sigma(n)*phi(n) = n*tau(n)?
print("\n" + "=" * 60)
print("WHY R(n)=1 iff n is PERFECT NUMBER with specific tau/phi?")
print("=" * 60)
print("""
R(n) = sigma(n)*phi(n) / (n*tau(n)) = 1
  => sigma(n)*phi(n) = n*tau(n)

For n=6: sigma(6)=12, phi(6)=2, tau(6)=4
  12*2 = 6*4 = 24  ✓

For n=28: sigma(28)=56, phi(28)=12, tau(28)=6
  56*12 = 672,  28*6 = 168
  672/168 = 4 ≠ 1

So R(28) = 4, not 1. Only n=6 among perfect numbers gives R=1.
""")

# Check all perfect numbers we can
perfects = [6, 28, 496, 8128]
for p in perfects:
    # Compute manually for verification
    def sigma_n(n):
        s = 0
        for d in range(1, n+1):
            if n % d == 0:
                s += d
        return s
    def phi_n(n):
        count = 0
        for k in range(1, n+1):
            if math.gcd(k, n) == 1:
                count += 1
        return count
    def tau_n(n):
        count = 0
        for d in range(1, n+1):
            if n % d == 0:
                count += 1
        return count
    s, ph, t = sigma_n(p), phi_n(p), tau_n(p)
    r = s * ph / (p * t)
    print(f"  R({p}) = {s}*{ph}/({p}*{t}) = {s*ph}/{p*t} = {r}")

# What's special about the chain 6->1?
print("\n" + "=" * 60)
print("CHAIN TERMINATION ANALYSIS")
print("=" * 60)
print("""
The basin of 1 is remarkably thin:

  Depth 0: {1}           (1 node)
  Depth 1: {6}           (1 node)  -- the ONLY perfect number with R=1
  Depth 2: {120}         (1 node)
  Depth 3: {6048, 6552}  (2 nodes) -- first branching!
  Depth 4: {193750}      (1 node)  -- only from 6048 branch

The tree is almost a CHAIN, not a tree.
Total reachable nodes up to 500000: only 6.

Meanwhile, 147 out of 151 integer-R values in [2,100000]
terminate at non-integer R before reaching 1.

The chain to 1 is extraordinarily rare.
""")

# Distribution of terminal values (where chains die)
print("TERMINAL VALUES (where R is not integer, chains die):")
# Recompute for this script
# Let's just show the frequency of terminal values from the main output
terminals = {
    4: "R(28)=4",
    5: "R(54)=5",
    7: "R(96)=7, R(1550->96)=7",
    16: "R(135)=16, R(2176->135)=16",
    19: "R(196)=19, R(6318->196)=19",
    18: "R(224)=18",
    14: "R(234)=14",
    12: "R(270)=12",
    13: "R(360)=13",
    48: "R(496)=48, R(1638)=48",
    24: "R(672)=24",
}
print("\nTerminal values (R not integer) and how chains reach them:")
for v, desc in sorted(terminals.items()):
    print(f"  {v:>4}: {desc}")

print("\nKey insight: most chains die at SMALL values (< 100)")
print("where R is not integer. The 'funnel' to 1 requires")
print("passing through 6, and R(n)=6 requires n=120 exactly.")

if __name__ == "__main__":
    pass
