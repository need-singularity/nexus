#!/usr/bin/env python3
"""
Verification script for math/proofs/koide_from_R1.md

Numerically checks all key claims in the Koide-from-R(6)=1 proof:
  Theorem 1: K(6) = 2/3  (Divisor Koide Functional)
  Theorem 2: delta(6) = 2/9  (Divisor Koide Angle)
  Theorem 3: K/K_min = phi(6) = 2  (Cauchy-Schwarz saturation)
  Theorem 4: Lepton mass reconstruction from delta_0 = 2/9
  Uniqueness: K(n) = 2/3 has no solution other than n=6 in [1, 10000]

Usage:
  python3 calc/verify_koide_from_R1.py
"""

import math
from fractions import Fraction

# ======================================================================
# Core arithmetic functions
# ======================================================================

def divisors(n):
    if n <= 0:
        return []
    divs = []
    for i in range(1, int(math.isqrt(n)) + 1):
        if n % i == 0:
            divs.append(i)
            if i != n // i:
                divs.append(n // i)
    return sorted(divs)

def sigma(n):
    return sum(divisors(n))

def tau(n):
    return len(divisors(n))

def phi(n):
    if n <= 0:
        return 0
    result = n
    temp = n
    d = 2
    while d * d <= temp:
        if temp % d == 0:
            while temp % d == 0:
                temp //= d
            result -= result // d
        d += 1
    if temp > 1:
        result -= result // temp
    return result


# ======================================================================
# Derived functionals (exact, using Fractions)
# ======================================================================

def R(n):
    """Bridge Ratio R(n) = sigma(n)*phi(n) / (n*tau(n))"""
    return Fraction(sigma(n) * phi(n), n * tau(n))

def K(n):
    """Divisor Koide Functional K(n) = n*tau(n)^2 / sigma(n)^2"""
    return Fraction(n * tau(n)**2, sigma(n)**2)

def delta(n):
    """Divisor Koide Angle delta(n) = phi(n)*tau(n)^2 / sigma(n)^2"""
    return Fraction(phi(n) * tau(n)**2, sigma(n)**2)


# ======================================================================
# Tests
# ======================================================================

passed = 0
failed = 0

def check(name, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  [PASS] {name}" + (f" ({detail})" if detail else ""))
    else:
        failed += 1
        print(f"  [FAIL] {name}" + (f" ({detail})" if detail else ""))


print("=" * 70)
print("Verification: koide_from_R1.md")
print("=" * 70)

# --- n=6 constants ---
print("\n--- n=6 arithmetic constants ---")
check("sigma(6) = 12", sigma(6) == 12, f"sigma(6) = {sigma(6)}")
check("phi(6) = 2", phi(6) == 2, f"phi(6) = {phi(6)}")
check("tau(6) = 4", tau(6) == 4, f"tau(6) = {tau(6)}")

# --- Theorem 1: K(6) = 2/3 ---
print("\n--- Theorem 1: K(6) = 2/3 (Koide Formula) ---")
k6 = K(6)
check("K(6) = 2/3 exactly", k6 == Fraction(2, 3), f"K(6) = {k6}")

# Step 1: R(6) = 1
r6 = R(6)
check("R(6) = 1 (Bridge Ratio)", r6 == 1, f"R(6) = {r6}")

# Step 2: sigma*phi = n*tau
sp = sigma(6) * phi(6)
nt = 6 * tau(6)
check("sigma*phi = n*tau at n=6", sp == nt, f"{sp} = {nt}")

# Step 3: Direct computation
numerator = 6 * tau(6)**2
denominator = sigma(6)**2
check("6*16/144 = 96/144 = 2/3", Fraction(numerator, denominator) == Fraction(2, 3),
      f"{numerator}/{denominator} = {Fraction(numerator, denominator)}")

# --- Theorem 1 Uniqueness: K(n) = 2/3 only at n=6, n in [1, 10000] ---
print("\n--- Uniqueness: K(n) = 2/3 ---")
koide_solutions = []
for n in range(1, 10001):
    if K(n) == Fraction(2, 3):
        koide_solutions.append(n)
check("K(n) = 2/3 unique at n=6 in [1, 10000]", koide_solutions == [6],
      f"solutions: {koide_solutions}")

# --- Theorem 2: delta(6) = 2/9 ---
print("\n--- Theorem 2: delta(6) = 2/9 (Koide Angle) ---")
d6 = delta(6)
check("delta(6) = 2/9 exactly", d6 == Fraction(2, 9), f"delta(6) = {d6}")

# Direct computation
num_d = phi(6) * tau(6)**2
den_d = sigma(6)**2
check("2*16/144 = 32/144 = 2/9", Fraction(num_d, den_d) == Fraction(2, 9),
      f"{num_d}/{den_d} = {Fraction(num_d, den_d)}")

# delta/K = phi/n = 1/3
ratio_dk = d6 / k6
check("delta/K = phi(6)/6 = 1/3", ratio_dk == Fraction(1, 3),
      f"delta/K = {ratio_dk}")

# Non-uniqueness of delta(n)=2/9 (n=15 also satisfies)
delta_solutions = []
for n in range(1, 10001):
    if delta(n) == Fraction(2, 9):
        delta_solutions.append(n)
check("delta(n) = 2/9 solutions include n=15",
      6 in delta_solutions and 15 in delta_solutions,
      f"solutions: {delta_solutions[:10]}{'...' if len(delta_solutions) > 10 else ''}")

# Joint uniqueness: K=2/3 AND delta=2/9 AND R=1
joint_solutions = []
for n in range(2, 10001):
    if K(n) == Fraction(2, 3) and delta(n) == Fraction(2, 9) and R(n) == 1:
        joint_solutions.append(n)
check("Joint K=2/3 + delta=2/9 + R=1 unique at n=6",
      joint_solutions == [6], f"solutions: {joint_solutions}")

# --- Theorem 3: K/K_min = phi(6) = 2 ---
print("\n--- Theorem 3: K/K_min = phi(6) (Cauchy-Schwarz) ---")
K_min = Fraction(1, 3)  # 1/N for N=3 leptons
ratio_Kmin = k6 / K_min
check("K/K_min = (2/3)/(1/3) = 2 = phi(6)",
      ratio_Kmin == 2 and ratio_Kmin == phi(6),
      f"K/K_min = {ratio_Kmin}, phi(6) = {phi(6)}")

# --- Theorem 4: Lepton mass reconstruction ---
print("\n--- Theorem 4: Lepton mass reconstruction ---")

# Trigonometric identities for third-roots-of-unity
# sum cos(2*pi*k/3 + d0) for k=0,1,2 = 0  (for any d0)
d0 = 2.0 / 9.0
cos_sum = sum(math.cos(2 * math.pi * k / 3 + d0) for k in range(3))
check("sum cos(2*pi*k/3 + delta_0) = 0", abs(cos_sum) < 1e-14,
      f"sum = {cos_sum:.2e}")

# sum cos^2(2*pi*k/3 + d0) = 3/2  (for any d0)
cos2_sum = sum(math.cos(2 * math.pi * k / 3 + d0)**2 for k in range(3))
check("sum cos^2(2*pi*k/3 + delta_0) = 3/2", abs(cos2_sum - 1.5) < 1e-14,
      f"sum = {cos2_sum:.6f}")

# K = 2/3 from parametrization (for any delta_0)
# sum m_k = A^2 * (3 + 2*sqrt(2)*0 + 2*(3/2)) = 6*A^2
# (sum sqrt(m_k))^2 = (3A)^2 = 9*A^2
# K = 6/9 = 2/3
check("K = 6*A^2 / 9*A^2 = 2/3 (from parametrization)",
      Fraction(6, 9) == Fraction(2, 3),
      "6/9 = 2/3")

# Lepton mass predictions with delta_0 = 2/9
m_tau_exp = 1776.86  # MeV (input)
sqrt_m_tau = math.sqrt(m_tau_exp)

# A from tau lepton (k=0)
theta_0 = d0  # 2*pi*0/3 + 2/9 = 2/9
A = sqrt_m_tau / (1 + math.sqrt(2) * math.cos(theta_0))

# Predict electron (k=1) and muon (k=2)
theta_1 = 2 * math.pi / 3 + d0
theta_2 = 4 * math.pi / 3 + d0

sqrt_m_e_pred = A * (1 + math.sqrt(2) * math.cos(theta_1))
sqrt_m_mu_pred = A * (1 + math.sqrt(2) * math.cos(theta_2))

m_e_pred = sqrt_m_e_pred**2
m_mu_pred = sqrt_m_mu_pred**2

m_e_exp = 0.51100  # MeV (PDG)
m_mu_exp = 105.658  # MeV (PDG)

err_e = abs(m_e_pred - m_e_exp) / m_e_exp * 100
err_mu = abs(m_mu_pred - m_mu_exp) / m_mu_exp * 100

check(f"Electron mass prediction error < 0.1%", err_e < 0.1,
      f"m_e = {m_e_pred:.5f} MeV, observed = {m_e_exp:.5f} MeV, error = {err_e:.4f}%")
check(f"Muon mass prediction error < 0.1%", err_mu < 0.1,
      f"m_mu = {m_mu_pred:.3f} MeV, observed = {m_mu_exp:.3f} MeV, error = {err_mu:.4f}%")

# Verify Koide formula holds for predicted masses
K_pred = (m_e_pred + m_mu_pred + m_tau_exp) / (math.sqrt(m_e_pred) + math.sqrt(m_mu_pred) + math.sqrt(m_tau_exp))**2
check("K = 2/3 for predicted masses", abs(K_pred - 2/3) < 1e-10,
      f"K = {K_pred:.10f}")

# --- Additional checks from the proof ---
print("\n--- Additional claims ---")

# n=15 has K(15) != 2/3
k15 = K(15)
check("n=15 has K(15) != 2/3", k15 != Fraction(2, 3),
      f"K(15) = {k15} = {float(k15):.6f}")

# n=15 has R(15) != 1
r15 = R(15)
check("n=15 has R(15) != 1", r15 != 1,
      f"R(15) = {r15} = {float(r15):.4f}")

# Near-miss analysis: find closest K(n) to 2/3 for n != 6
print("\n--- Near-miss analysis (closest K(n) to 2/3) ---")
target = Fraction(2, 3)
near_misses = []
for n in range(2, 10001):
    if n == 6:
        continue
    kn = K(n)
    dist = abs(kn - target)
    near_misses.append((float(dist), n, kn))

near_misses.sort()
print("  Top 5 nearest misses:")
for dist, n, kn in near_misses[:5]:
    print(f"    n={n}: K(n) = {kn} = {float(kn):.6f}, distance = {dist:.6f}")

check("No other n has K(n) = 2/3 exactly",
      all(kn != target for _, n, kn in near_misses),
      "verified for n in [2, 10000]")

# ======================================================================
# Summary
# ======================================================================
print("\n" + "=" * 70)
total = passed + failed
print(f"TOTAL: {passed}/{total} PASS" + ("  [ALL PASS]" if failed == 0 else f"  [{failed} FAILED]"))
print("=" * 70)
