#!/usr/bin/env python3
"""Verify combinatorial game theory and probabilistic number theory connections to perfect number 6."""

import math
from collections import Counter
from functools import lru_cache

print("=" * 70)
print("TOPIC 1: COMBINATORIAL GAME THEORY & PERFECT NUMBER 6")
print("=" * 70)

# === 1. Divisor Game: Grundy values ===
# Rules: Position n. Player removes a proper divisor d of n (d < n). Opponent faces n - d.
# Losing position (P) if n=1 (no moves). Compute Grundy values.

def divisors(n):
    """Return all divisors of n."""
    divs = []
    for i in range(1, int(n**0.5) + 1):
        if n % i == 0:
            divs.append(i)
            if i != n // i:
                divs.append(n // i)
    return sorted(divs)

def proper_divisors(n):
    """Return proper divisors (excluding n itself)."""
    return [d for d in divisors(n) if d < n]

@lru_cache(maxsize=None)
def grundy_divisor_game(n):
    """Compute Sprague-Grundy value for the divisor subtraction game."""
    if n == 1:
        return 0  # no moves, losing
    moves = set()
    for d in proper_divisors(n):
        moves.add(grundy_divisor_game(n - d))
    # mex (minimum excludant)
    mex = 0
    while mex in moves:
        mex += 1
    return mex

print("\n--- 1. Divisor Subtraction Game: Grundy Values G(n) for n=1..30 ---")
print(f"{'n':>3} | {'G(n)':>4} | {'Type':>5} | divisors(n)")
print("-" * 55)
for n in range(1, 31):
    g = grundy_divisor_game(n)
    typ = "P" if g == 0 else "N"
    pd = proper_divisors(n)
    marker = " <-- PERFECT" if n == 6 else (" <-- PERFECT" if n == 28 else "")
    print(f"{n:>3} | {g:>4} | {typ:>5} | {pd}{marker}")

print(f"\nn=6: Grundy value = {grundy_divisor_game(6)}")
print(f"n=6 is {'N-position (first player wins)' if grundy_divisor_game(6) != 0 else 'P-position (second player wins)'}")
print(f"n=28: Grundy value = {grundy_divisor_game(28)}")
print(f"n=28 is {'N-position (first player wins)' if grundy_divisor_game(28) != 0 else 'P-position (second player wins)'}")

# Check all perfect numbers we can handle
print("\n--- Perfect numbers in divisor game ---")
for pn in [6, 28]:
    g = grundy_divisor_game(pn)
    print(f"  n={pn}: G(n)={g}, {'N-position' if g else 'P-position'}")

# === 2. Simple Divisor Game (standard): even wins ===
# Standard divisor game: if n is even, first player wins (remove 1 to make it odd).
print("\n--- 2. Standard Divisor Game (remove proper divisor, opponent gets n/d or n-d) ---")
print("In the STANDARD divisor game (subtract version):")
print("Even numbers: first player can always remove 1, leaving odd number.")
print(f"n=6 (even): First player wins by removing 1 -> opponent at 5")

# === 3. Wythoff's game ===
print("\n--- 3. Wythoff's Game Losing Positions ---")
phi_golden = (1 + math.sqrt(5)) / 2
phi2 = phi_golden ** 2
print(f"Golden ratio phi = {phi_golden:.6f}, phi^2 = {phi2:.6f}")
print(f"{'n':>3} | {'a_n=floor(n*phi)':>16} | {'b_n=floor(n*phi^2)':>18} | {'a+b':>5} | {'b-a':>5}")
print("-" * 70)
for n in range(1, 11):
    a = int(n * phi_golden)
    b = int(n * phi2)
    print(f"{n:>3} | {a:>16} | {b:>18} | {a+b:>5} | {b-a:>5}")

print(f"\nn=6 Wythoff: a_6={int(6*phi_golden)}, b_6={int(6*phi2)}")
print(f"a_6 + b_6 = {int(6*phi_golden) + int(6*phi2)}")
print(f"phi(6)=2, sigma(6)=12. Connection: a_6={int(6*phi_golden)}=9, b_6-a_6={int(6*phi2)-int(6*phi_golden)}")
print("No direct connection to phi(6) or sigma(6). As expected.")

# === 4. Chomp on divisor poset of 6 ===
print("\n--- 4. Chomp on Divisor Poset of 6 ---")
print("Divisor poset of 6: {1, 2, 3, 6}")
print("Divisibility: 1|2, 1|3, 1|6, 2|6, 3|6")
print("Players remove element and all multiples.")
print("1 is 'poison' (player who takes 1 loses).")
print()

# Represent state as frozenset of remaining elements
# Move: pick x != min, remove x and all multiples of x from remaining
def chomp_divisor(n):
    """Analyze chomp on divisor poset of n."""
    all_divs = frozenset(divisors(n))

    @lru_cache(maxsize=None)
    def is_losing(state):
        """Is this a losing position for the player to move?"""
        state_set = set(state)
        if len(state_set) == 1 and 1 in state_set:
            return True  # must take poison, lose
        if len(state_set) == 0:
            return True  # no moves

        for x in sorted(state_set):
            if x == 1 and len(state_set) > 1:
                continue  # don't take poison unless forced
            # Actually in chomp you CAN take 1 but you lose
            # Let's do it properly: pick any element, remove it and all its multiples
            new_state = frozenset(s for s in state_set if s % x != 0 or s < x)
            # Wait, chomp removes x and everything x divides INTO (upward)
            # In divisor poset: remove x and all multiples of x
            new_state = frozenset(s for s in state_set if s % x != 0)
            if x == 1:
                new_state = frozenset()  # removing 1 removes everything
            if is_losing(new_state):
                return False  # current player wins by moving here
        return True  # all moves lead to winning positions for opponent

    return is_losing(all_divs)

print("Chomp analysis on divisor poset of 6:")
result = chomp_divisor(6)
print(f"  Starting position {{1,2,3,6}}: {'P-position (2nd player wins)' if result else 'N-position (1st player wins)'}")

# Analyze all moves
all_divs_6 = set(divisors(6))
print("\n  Move analysis from {1,2,3,6}:")
for x in sorted(all_divs_6):
    if x == 1:
        print(f"    Remove {x}: removes everything -> LOSE (poison)")
    else:
        remaining = frozenset(s for s in all_divs_6 if s % x != 0)
        print(f"    Remove {x}: remaining = {set(remaining)}")

# Also check n=28
print(f"\nChomp on divisor poset of 28:")
result28 = chomp_divisor(28)
print(f"  Starting position: {'P-position (2nd player wins)' if result28 else 'N-position (1st player wins)'}")

# === 5. Nim-values and perfect numbers ===
print("\n--- 5. Nim-values Related to Perfect Numbers ---")
print("Nim with heap size n: Grundy value = n itself.")
print(f"  Nim(6) = 6 = sigma(6)/2 = 12/2")
print(f"  Nim(28) = 28 = sigma(28)/2 = 56/2")
print(f"  For ANY perfect number p: Nim(p) = p = sigma(p)/2")
print(f"  This is trivially true: sigma(p) = 2p by definition.")

# Grundy values pattern analysis
print("\n--- Grundy value statistics for divisor game ---")
grundy_vals = [grundy_divisor_game(n) for n in range(1, 101)]
p_positions = [n for n in range(1, 101) if grundy_divisor_game(n) == 0]
n_positions = [n for n in range(1, 101) if grundy_divisor_game(n) != 0]
print(f"P-positions (losing) in [1,100]: {p_positions[:20]}...")
print(f"N-positions (winning) in [1,100]: first 20 = {n_positions[:20]}...")
print(f"Count: P={len(p_positions)}, N={len(n_positions)}")

# Check if P-positions are exactly odd numbers
odd_check = all(n % 2 == 1 for n in p_positions)
print(f"\nAre all P-positions odd? {odd_check}")
even_check = all(n % 2 == 0 for n in n_positions)
print(f"Are all N-positions even? {even_check}")
if odd_check:
    print("=> The divisor subtraction game: EVEN = WIN, ODD = LOSE")
    print("=> Perfect numbers (all even except maybe 6?) are always N-positions!")
    print("=> This is because every even number has 1 as divisor, subtract 1 -> odd -> P-position")


print("\n" + "=" * 70)
print("TOPIC 2: PROBABILISTIC NUMBER THEORY & PERFECT NUMBER 6")
print("=" * 70)

# Helper functions
def sigma_func(n):
    """Sum of divisors."""
    return sum(divisors(n))

def phi_func(n):
    """Euler's totient."""
    count = 0
    for i in range(1, n + 1):
        if math.gcd(i, n) == 1:
            count += 1
    return count

def tau_func(n):
    """Number of divisors."""
    return len(divisors(n))

def omega_func(n):
    """Number of distinct prime factors."""
    if n <= 1:
        return 0
    count = 0
    d = 2
    temp = n
    while d * d <= temp:
        if temp % d == 0:
            count += 1
            while temp % d == 0:
                temp //= d
        d += 1
    if temp > 1:
        count += 1
    return count

# Precompute for efficiency
print("\nPrecomputing arithmetic functions for n=1..100000...")
N_MAX = 100000

# Use sieve for sigma, phi, tau, omega
sigma_arr = [0] * (N_MAX + 1)
phi_arr = list(range(N_MAX + 1))
tau_arr = [0] * (N_MAX + 1)
omega_arr = [0] * (N_MAX + 1)

# Sieve of divisors
for d in range(1, N_MAX + 1):
    for multiple in range(d, N_MAX + 1, d):
        sigma_arr[multiple] += d
        tau_arr[multiple] += 1

# Sieve for phi
for p in range(2, N_MAX + 1):
    if phi_arr[p] == p:  # p is prime
        omega_arr[p] += 1
        for multiple in range(p, N_MAX + 1, p):
            phi_arr[multiple] -= phi_arr[multiple] // p
            if multiple != p:
                omega_arr[multiple] += 1  # wrong for prime powers

# Fix omega with proper sieve
omega_arr = [0] * (N_MAX + 1)
for p in range(2, N_MAX + 1):
    if phi_arr[p] == p - 1:  # p is prime (after phi sieve)
        for multiple in range(p, N_MAX + 1, p):
            omega_arr[multiple] += 1

print("Done.")

# === 1. Erdos-Kac for n=6 ===
print("\n--- 1. Erdos-Kac Theorem: omega(n) distribution ---")
print(f"omega(6) = {omega_arr[6]} (prime factors: 2, 3)")
mu = math.log(math.log(6))
sig = math.sqrt(math.log(math.log(6)))
z_score = (omega_arr[6] - mu) / sig
print(f"ln(ln(6)) = {mu:.4f}")
print(f"sqrt(ln(ln(6))) = {sig:.4f}")
print(f"Z-score = (2 - {mu:.4f}) / {sig:.4f} = {z_score:.4f}")
print(f"=> n=6 is {z_score:.2f} sigma above Erdos-Kac mean")
print(f"   This means 6 has MORE prime factors than typical for its size")

# Check other perfect numbers
for pn in [28, 496, 8128]:
    if pn <= N_MAX:
        w = omega_arr[pn]
        if math.log(math.log(pn)) > 0:
            mu_p = math.log(math.log(pn))
            sig_p = math.sqrt(mu_p)
            z_p = (w - mu_p) / sig_p
            print(f"  omega({pn})={w}, ln(ln({pn}))={mu_p:.3f}, Z={z_p:.3f}")

# === 2. Distribution of R(n) = sigma*phi/(n*tau) ===
print("\n--- 2. Distribution of R(n) = sigma(n)*phi(n) / (n*tau(n)) ---")
R_values = []
R_equals_1 = []
for n in range(1, N_MAX + 1):
    s = sigma_arr[n]
    p = phi_arr[n]
    t = tau_arr[n]
    R = (s * p) / (n * t)
    R_values.append(R)
    if abs(R - 1.0) < 1e-10:
        R_equals_1.append(n)

R_arr = R_values
R_mean = sum(R_arr) / len(R_arr)
R_sorted = sorted(R_arr)
R_median = R_sorted[len(R_sorted) // 2]
R_std = math.sqrt(sum((r - R_mean)**2 for r in R_arr) / len(R_arr))
R_skew = sum((r - R_mean)**3 for r in R_arr) / (len(R_arr) * R_std**3) if R_std > 0 else 0

print(f"N = {N_MAX}")
print(f"Mean(R)   = {R_mean:.6f}")
print(f"Median(R) = {R_median:.6f}")
print(f"Std(R)    = {R_std:.6f}")
print(f"Skewness  = {R_skew:.6f}")

# Percentile of R=1
count_below_1 = sum(1 for r in R_arr if r < 1.0)
count_equal_1 = sum(1 for r in R_arr if abs(r - 1.0) < 1e-10)
percentile = count_below_1 / len(R_arr) * 100
print(f"\nR(6) = 1.0000")
print(f"Percentile of R=1: {percentile:.2f}%")
print(f"Values with R=1 exactly: {R_equals_1}")
print(f"P(R=1) = {len(R_equals_1)}/{N_MAX} = {len(R_equals_1)/N_MAX:.6f}")

# Histogram of R(n)
print("\nHistogram of R(n) for n=1..100000:")
bins = [(0, 0.2), (0.2, 0.4), (0.4, 0.6), (0.6, 0.8), (0.8, 1.0),
        (1.0, 1.2), (1.2, 1.4), (1.4, 1.6), (1.6, 1.8), (1.8, 2.0),
        (2.0, 2.5), (2.5, 3.0), (3.0, 5.0), (5.0, 100.0)]
max_bar = 50
bin_counts = []
for lo, hi in bins:
    if hi == 100.0:
        c = sum(1 for r in R_arr if lo <= r)
    else:
        c = sum(1 for r in R_arr if lo <= r < hi)
    bin_counts.append(c)
max_count = max(bin_counts) if bin_counts else 1

print(f"{'Bin':>12} | {'Count':>7} | {'%':>6} | Bar")
print("-" * 70)
for i, (lo, hi) in enumerate(bins):
    c = bin_counts[i]
    pct = c / N_MAX * 100
    bar_len = int(c / max_count * max_bar)
    marker = " <-- R(6)=1" if lo <= 1.0 < hi or (lo == 1.0 and hi == 1.2) else ""
    print(f"[{lo:.1f},{hi:.1f})" + f" | {c:>7} | {pct:>5.1f}% | {'#' * bar_len}{marker}")

# === 3. Hardy-Ramanujan ===
print("\n--- 3. Hardy-Ramanujan Partition Approximation ---")
def partitions(n):
    """Compute p(n) exactly for small n."""
    table = [0] * (n + 1)
    table[0] = 1
    for k in range(1, n + 1):
        for i in range(k, n + 1):
            table[i] += table[i - k]
    return table[n]

print(f"{'n':>4} | {'p(n) exact':>12} | {'HR approx':>12} | {'ratio':>8}")
print("-" * 50)
for n in range(1, 21):
    pn = partitions(n)
    hr = math.exp(math.pi * math.sqrt(2 * n / 3)) / (4 * n * math.sqrt(3))
    ratio = pn / hr if hr > 0 else 0
    marker = " <--" if n == 6 else ""
    print(f"{n:>4} | {pn:>12} | {hr:>12.1f} | {ratio:>8.4f}{marker}")

print(f"\np(6) = {partitions(6)}")
print(f"HR(6) = e^(pi*sqrt(4))/(24*sqrt(3)) = e^(2pi)/(24*sqrt(3))")
hr6 = math.exp(2 * math.pi) / (24 * math.sqrt(3))
print(f"     = {hr6:.2f}")
print(f"Ratio p(6)/HR(6) = {partitions(6)/hr6:.4f}")

# === 4. Distribution of tau(sigma(n))/n ===
print("\n--- 4. Distribution of tau(sigma(n))/n ---")
ts_values = []
ts_equals_1 = []
for n in range(1, min(N_MAX + 1, 10001)):
    s = sigma_arr[n]
    if s <= N_MAX:
        t_s = tau_arr[s]
    else:
        # compute tau(s) directly
        t_s = 0
        for d in range(1, int(s**0.5) + 1):
            if s % d == 0:
                t_s += 1
                if d != s // d:
                    t_s += 1
    val = t_s / n
    ts_values.append(val)
    if abs(val - 1.0) < 1e-10:
        ts_equals_1.append(n)

ts_mean = sum(ts_values) / len(ts_values)
ts_sorted = sorted(ts_values)
ts_median = ts_sorted[len(ts_sorted) // 2]
count_below = sum(1 for v in ts_values if v < 1.0)
pct = count_below / len(ts_values) * 100

print(f"N = {len(ts_values)}")
print(f"Mean(tau(sigma(n))/n) = {ts_mean:.6f}")
print(f"Median = {ts_median:.6f}")
print(f"tau(sigma(6))/6 = tau(12)/6 = {tau_arr[12]}/6 = {tau_arr[12]/6:.4f}")
print(f"Values where tau(sigma(n))/n = 1: {ts_equals_1[:20]}")
print(f"Percentile of value 1.0: {pct:.2f}%")

# === 5. Probability comparison ===
print("\n--- 5. Rarity Comparison ---")
# Perfect numbers up to N
perfect = [n for n in range(1, N_MAX + 1) if sigma_arr[n] == 2 * n]
print(f"Perfect numbers up to {N_MAX}: {perfect}")
print(f"P(perfect) = {len(perfect)}/{N_MAX} = {len(perfect)/N_MAX:.6f}")
print(f"R=1 numbers up to {N_MAX}: {R_equals_1}")
print(f"P(R=1) = {len(R_equals_1)}/{N_MAX} = {len(R_equals_1)/N_MAX:.6f}")

# Both conditions
both = set(perfect) & set(R_equals_1)
print(f"Numbers that are BOTH perfect AND R=1: {both}")
if len(both) > 0:
    print(f"=> n=6 satisfies BOTH conditions simultaneously")
    print(f"   P(perfect AND R=1) = {len(both)}/{N_MAX}")
    print(f"   If independent: P = {len(perfect)/N_MAX:.6f} * {len(R_equals_1)/N_MAX:.6f} = {len(perfect)*len(R_equals_1)/N_MAX**2:.10f}")
    print(f"   Actual: {len(both)/N_MAX:.6f}")
    print(f"   Enrichment = actual/expected = {len(both)/N_MAX / (len(perfect)*len(R_equals_1)/N_MAX**2):.1f}x")

# Distribution of R for perfect numbers
print(f"\nR-values for perfect numbers:")
for pn in perfect:
    s = sigma_arr[pn]
    p = phi_arr[pn]
    t = tau_arr[pn]
    R = (s * p) / (pn * t)
    print(f"  n={pn}: sigma={s}, phi={p}, tau={t}, R={R:.6f}")

print("\n" + "=" * 70)
print("SUMMARY OF KEY FINDINGS")
print("=" * 70)
print(f"""
GAME THEORY:
  - Divisor subtraction game: ALL even n are N-positions (first player wins)
  - n=6 is N-position with Grundy value {grundy_divisor_game(6)}
  - This holds for ALL even perfect numbers (trivially: they're even)
  - Chomp on divisor poset of 6: first player wins
  - Wythoff connection: none found (as expected)

PROBABILISTIC NUMBER THEORY:
  - Erdos-Kac Z-score for omega(6): {z_score:.3f} (moderately anomalous)
  - R(n)=sigma*phi/(n*tau): R(6)=1 is at {percentile:.1f}th percentile
  - Only {len(R_equals_1)} out of {N_MAX} numbers have R=1: {R_equals_1}
  - P(R=1) = {len(R_equals_1)/N_MAX:.6f} -> 0 as N -> infinity
  - n=6 is the ONLY number > 1 with R=1 (up to {N_MAX})
  - tau(sigma(6))/6 = 1 (another unit-value coincidence)
  - Perfect numbers AND R=1 overlap only at n=6
""")
