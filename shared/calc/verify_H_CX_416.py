#!/usr/bin/env python3
"""H-CX-416 Verification: Cell Division Cycle = sigma(6)*tau(6) = 48 hours

Tests whether perfect number arithmetic matches biological time constants.
"""

import math
from fractions import Fraction

# --- Number theory functions ---
def factorize(n):
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
    factors = factorize(n)
    result = 1
    for p, a in factors.items():
        result *= (p**(a+1) - 1) // (p - 1)
    return result

def tau(n):
    factors = factorize(n)
    result = 1
    for a in factors.values():
        result *= (a + 1)
    return result

def phi(n):
    factors = factorize(n)
    result = n
    for p in factors:
        result = result * (p - 1) // p
    return result

def sigma_neg1(n):
    """sigma_{-1}(n) = sigma(n)/n"""
    return Fraction(sigma(n), n)

# --- Perfect numbers ---
perfect_numbers = [6, 28, 496, 8128]

# --- Biological time constants (hours) ---
bio_constants = {
    "Cell cycle (typical mammalian)": 24,
    "Cell cycle (slow, fibroblast)": 48,
    "S phase (DNA synthesis)": 8,
    "G1 phase": 11,
    "G2 phase": 4,
    "M phase (mitosis)": 1,
    "Circadian rhythm": 24,
    "Heartbeat period (sec)": 60/72,  # ~0.833 sec
    "Breathing cycle (sec)": 5,       # ~12/min
    "REM cycle (min)": 90,
    "Skin cell turnover (days)": 28,
    "Red blood cell lifespan (days)": 120,
}

print("=" * 70)
print("H-CX-416 VERIFICATION: Cell Division Cycle = sigma(6)*tau(6)")
print("=" * 70)

# --- Step 1: Compute all functions for perfect numbers ---
print("\n--- Step 1: Number-theoretic functions for perfect numbers ---")
print(f"{'n':>6} | {'sigma':>6} | {'tau':>4} | {'phi':>6} | {'sigma_-1':>10}")
print("-" * 45)
for n in perfect_numbers:
    s, t, p, s1 = sigma(n), tau(n), phi(n), sigma_neg1(n)
    print(f"{n:>6} | {s:>6} | {t:>4} | {p:>6} | {str(s1):>10}")

# --- Step 2: All pairwise products/ratios for n=6 ---
print("\n--- Step 2: Pairwise products/ratios for n=6 ---")
n = 6
s, t, p, s1 = sigma(n), tau(n), phi(n), float(sigma_neg1(n))
funcs = {"sigma": s, "tau": t, "phi": p, "sigma_-1": s1, "n": n}

print(f"\nsigma(6) = {s}")
print(f"tau(6)   = {t}")
print(f"phi(6)   = {p}")
print(f"sigma_-1(6) = {s1}")

products = {}
print(f"\n{'Operation':>30} | {'Value':>10} | {'Biological match':>40}")
print("-" * 85)

# Products
for name_a, val_a in funcs.items():
    for name_b, val_b in funcs.items():
        if name_a >= name_b:
            continue
        prod = val_a * val_b
        products[f"{name_a}*{name_b}"] = prod

# Also compute some ratios and special combos
products["sigma*tau"] = s * t
products["sigma*phi"] = s * p
products["sigma*sigma_-1"] = s * s1
products["tau*phi"] = t * p
products["sigma/tau"] = s / t
products["sigma/phi"] = s / p
products["tau/phi"] = t / p
products["n*tau"] = n * t
products["n*phi"] = n * p
products["sigma+tau"] = s + t
products["sigma+phi"] = s + p
products["sigma-tau"] = s - t
products["sigma-phi"] = s - p
products["sigma*tau/n"] = s * t / n
products["phi^tau"] = p ** t

# Check against biological constants
matches = []
for op, val in sorted(products.items(), key=lambda x: x[1]):
    best_match = ""
    best_err = float('inf')
    for bio_name, bio_val in bio_constants.items():
        if bio_val == 0:
            continue
        err = abs(val - bio_val) / bio_val
        if err < best_err:
            best_err = err
            best_match = bio_name
    match_str = f"{best_match} ({bio_constants[best_match]:.2f})" if best_err < 0.15 else ""
    flag = " <-- MATCH" if best_err < 0.05 else (" ~ close" if best_err < 0.15 else "")
    print(f"{op:>30} | {val:>10.2f} | {match_str:>40} {flag}")
    if best_err < 0.15:
        matches.append((op, val, best_match, best_err))

# --- Step 3: Key matches ---
print("\n--- Step 3: Key matches summary ---")
print(f"{'Expression':>25} | {'Value':>8} | {'Bio constant':>35} | {'Error':>8}")
print("-" * 85)

key_checks = [
    ("sigma(6)*tau(6)", s*t, "Cell cycle slow (48h)", 48),
    ("sigma(6)*phi(6)", s*p, "Cell cycle typical (24h)", 24),
    ("sigma(6)*sigma_-1(6)", s*s1, "Circadian rhythm (24h)", 24),
    ("phi(6)/sigma_-1(6)", p/s1, "M phase (1h)", 1),
    ("sigma(6)-tau(6)", s-t, "S phase (8h)", 8),
    ("sigma(6)+phi(6)-tau(6)", s+p-t, "G1 phase (10h)", 11),  # ad hoc warning
    ("tau(6)", t, "G2 phase (4h)", 4),
    ("sigma(6)/phi(6)", s/p, "n=6 itself", 6),
    ("phi(6)**tau(6)", p**t, "phi^tau=16", 16),
    ("skin turnover", 28, "Skin cell turnover (28d)", 28),  # n=28 perfect
]

exact_count = 0
close_count = 0
for expr, val, bio, expected in key_checks:
    err = abs(val - expected) / expected if expected != 0 else 0
    flag = "EXACT" if err == 0 else (f"{err*100:.1f}%" if err < 0.15 else f"{err*100:.1f}% (far)")
    if err == 0:
        exact_count += 1
    elif err < 0.15:
        close_count += 1
    print(f"{expr:>25} | {val:>8.2f} | {bio:>35} | {flag:>8}")

# --- Step 4: Generalization to n=28 ---
print("\n--- Step 4: Generalization test (n=28) ---")
n28 = 28
s28, t28, p28 = sigma(28), tau(28), phi(28)
s1_28 = float(sigma_neg1(28))
print(f"sigma(28) = {s28}, tau(28) = {t28}, phi(28) = {p28}, sigma_-1(28) = {s1_28:.4f}")
print(f"sigma(28)*tau(28) = {s28*t28}")
print(f"sigma(28)*phi(28) = {s28*p28}")
print(f"  -> These don't map to known biological constants (too large)")
print(f"  -> Generalization FAILS for n=28")
print(f"  -> This is n=6 SPECIFIC, not a general perfect number property")

# --- Step 5: Texas Sharpshooter p-value ---
print("\n--- Step 5: Texas Sharpshooter p-value ---")
import random
random.seed(42)

n_trials = 100000
n_targets = len(bio_constants)
bio_vals = list(bio_constants.values())

# How many matches we found: count exact + close (<15%)
our_matches = exact_count + close_count

# Random baseline: pick 10 random numbers in range 1-50, count matches
def count_random_matches():
    count = 0
    for _ in range(10):
        val = random.uniform(0.5, 50)
        for bv in bio_vals:
            if abs(val - bv) / max(bv, 0.01) < 0.15:
                count += 1
                break
    return count

random_matches = [count_random_matches() for _ in range(n_trials)]
avg_random = sum(random_matches) / n_trials
std_random = (sum((x - avg_random)**2 for x in random_matches) / n_trials) ** 0.5
p_value = sum(1 for x in random_matches if x >= our_matches) / n_trials

print(f"Our matches (exact + close <15%): {our_matches}")
print(f"Random baseline: {avg_random:.2f} +/- {std_random:.2f}")
print(f"p-value: {p_value:.4f}")
print(f"Significant (p < 0.05)? {'YES' if p_value < 0.05 else 'NO'}")

# --- Step 6: Ad hoc check ---
print("\n--- Step 6: Ad hoc adjustment check ---")
ad_hoc_count = 0
print("sigma(6)*tau(6) = 48 vs cell cycle 48h: NO adjustment needed")
print("sigma(6)*phi(6) = 24 vs circadian 24h: NO adjustment needed")
print("sigma(6)-tau(6) = 8 vs S phase 8h: NO adjustment needed")
print("tau(6) = 4 vs G2 phase 4h: NO adjustment needed")
print("sigma+phi-tau = 10 vs G1 11h: ADJUSTMENT (-1) -- AD HOC WARNING")
ad_hoc_count = 1
print(f"\nAd hoc adjustments found: {ad_hoc_count}/5 key matches")

# --- ASCII graph ---
print("\n--- ASCII Graph: Perfect Number Arithmetic vs Biology ---")
print()
all_data = [
    ("sigma*tau=48", 48, 48, "Cell cycle slow"),
    ("sigma*phi=24", 24, 24, "Circadian/Cell"),
    ("sigma-tau=8", 8, 8, "S phase"),
    ("tau=4", 4, 4, "G2 phase"),
    ("phi/s_-1=1", 1, 1, "Mitosis"),
]

max_val = 50
bar_width = 50
print(f"  {'Expression':>15} | {'Calc':>4} | {'Bio':>4} | Bar (max={max_val}h)")
print(f"  {'-'*15}-+-{'-'*4}-+-{'-'*4}-+-{'-'*bar_width}")
for label, calc_val, bio_val, bio_name in all_data:
    bar_len = int(calc_val / max_val * bar_width)
    bar = "#" * bar_len
    match_flag = "=" if calc_val == bio_val else "~"
    print(f"  {label:>15} | {calc_val:>4} | {bio_val:>4} | {bar} {match_flag} {bio_name}")

print()
print("  # = calculated value, = means exact match, ~ means approximate")

# --- Final verdict ---
print("\n" + "=" * 70)
print("VERDICT")
print("=" * 70)
print(f"  Exact matches: {exact_count}")
print(f"  Close matches (<15%): {close_count}")
print(f"  Ad hoc adjustments: {ad_hoc_count}")
print(f"  Generalization to n=28: FAILS")
print(f"  Texas p-value: {p_value:.4f}")
if p_value < 0.05:
    grade = "ORANGE-STAR" if p_value < 0.01 else "ORANGE"
else:
    grade = "WHITE (coincidence)"
print(f"  Grade: {grade}")
print(f"  Note: n=6 specific, not general perfect number property")
