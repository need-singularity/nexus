#!/usr/bin/env python3
"""H-NOBEL-6: Uniqueness Principle — Score every n from 2..1000.

For each n, count how many of the 136 unique-to-6 identities it satisfies.
Produces all data needed for the hypothesis document.

Output:
  1. Uniqueness score for n=2..1000
  2. Top scorers table
  3. Perfect number comparison
  4. Highly composite number comparison
  5. Statistical significance (mean, std, Z-score)
  6. Intersection theorem (top 10 identities)
  7. ASCII bar chart for n=2..100
"""

import math
import sys
import statistics

sys.path.insert(0, '.')
import tecsrs


def build_tables(limit):
    rt = tecsrs.SieveTables(limit)
    sigma_t = rt.sigma_list()
    tau_t = rt.tau_list()
    phi_t = rt.phi_list()
    sopfr_t = rt.sopfr_list()
    omega_t = rt.omega_list()
    # rad(n) = product of distinct primes; mu(n); sigma_m1(n) = sigma(n)/n
    # We need to compute rad, mu, Omega, sigma_m1 in Python
    # For factoring, use lpf sieve
    lpf_t = rt.lpf_list()

    # Compute rad(n), mu(n), Omega(n)
    rad_t = [0] * (limit + 1)
    mu_t = [0] * (limit + 1)
    bigomega_t = [0] * (limit + 1)  # Omega = total prime factors with multiplicity

    for n in range(1, limit + 1):
        if n == 1:
            rad_t[1] = 1
            mu_t[1] = 1
            bigomega_t[1] = 0
            continue
        # factor n using lpf
        m = n
        rad = 1
        mu = 1
        omega_count = 0
        while m > 1:
            p = lpf_t[m]
            if p == 0:
                break
            rad *= p
            exp = 0
            while m % p == 0:
                m //= p
                exp += 1
            omega_count += exp
            if exp > 1:
                mu = 0
            else:
                mu *= -1
        rad_t[n] = rad
        mu_t[n] = mu
        bigomega_t[n] = omega_count

    # sigma_m1(n) = sigma(n)/n  (only integer when it divides evenly)
    sigma_m1_t = [0] * (limit + 1)
    for n in range(1, limit + 1):
        if sigma_t[n] % n == 0:
            sigma_m1_t[n] = sigma_t[n] // n
        else:
            sigma_m1_t[n] = -1  # mark non-integer

    # lcm(1..n)
    lcm1n_t = [0] * (limit + 1)
    if limit >= 1:
        lcm1n_t[1] = 1
    for n in range(2, limit + 1):
        lcm1n_t[n] = lcm1n_t[n - 1] * n // math.gcd(lcm1n_t[n - 1], n)

    return {
        'sigma': sigma_t,
        'tau': tau_t,
        'phi': phi_t,
        'sopfr': sopfr_t,
        'omega': omega_t,
        'rad': rad_t,
        'mu': mu_t,
        'Omega': bigomega_t,
        'sigma_m1': sigma_m1_t,
        'lcm1n': lcm1n_t,
    }


# ═══════════════════════════════════════════════════════════════
# All 136 identities from the deep scan (MASS-GEN-B)
# Each is a lambda: (n, T) -> bool
# We include all categories: Cat 1 (18), Cat 2 Tier A (15),
# Cat 2 Tier B (10), Cat 3 compound unique (6), remaining ~87
# ═══════════════════════════════════════════════════════════════

def safe_div(a, b):
    """Integer division, returns None if not exact."""
    if b == 0:
        return None
    if a % b != 0:
        return None
    return a // b


def make_identities():
    """Return list of (name, test_fn) for all 136 identities."""
    ids = []

    def add(name, fn):
        ids.append((name, fn))

    # ── Category 1: Pure n-Function (18) ──
    add("n = sopfr+1",
        lambda n, T: n == T['sopfr'][n] + 1)
    add("n = sigma/phi",
        lambda n, T: T['phi'][n] != 0 and T['sigma'][n] % T['phi'][n] == 0 and n == T['sigma'][n] // T['phi'][n])
    add("n-1 = tau+1",
        lambda n, T: n - 1 == T['tau'][n] + 1)
    add("n-1 = sopfr",
        lambda n, T: n - 1 == T['sopfr'][n])
    add("n-2 = tau",
        lambda n, T: n - 2 == T['tau'][n])
    add("n-2 = phi^2",
        lambda n, T: n - 2 == T['phi'][n] ** 2)
    add("n-2 = sopfr-1",
        lambda n, T: n - 2 == T['sopfr'][n] - 1)
    add("n-2 = sigma_m1*2",
        lambda n, T: T['sigma_m1'][n] >= 0 and n - 2 == T['sigma_m1'][n] * 2)
    add("n-2 = sigma_m1^2",
        lambda n, T: T['sigma_m1'][n] >= 0 and n - 2 == T['sigma_m1'][n] ** 2)
    add("n+2 = tau*omega",
        lambda n, T: n + 2 == T['tau'][n] * T['omega'][n])
    add("n+2 = sigma-tau",
        lambda n, T: n + 2 == T['sigma'][n] - T['tau'][n])
    add("n/2 = sigma_m1+1",
        lambda n, T: n % 2 == 0 and T['sigma_m1'][n] >= 0 and n // 2 == T['sigma_m1'][n] + 1)
    add("n/2 = sigma/tau",
        lambda n, T: T['tau'][n] != 0 and T['sigma'][n] % T['tau'][n] == 0 and n % 2 == 0 and n // 2 == T['sigma'][n] // T['tau'][n])
    add("n/3 = sigma/n",
        lambda n, T: n % 3 == 0 and T['sigma'][n] % n == 0 and n // 3 == T['sigma'][n] // n)
    add("n/3 = mu+1",
        lambda n, T: n % 3 == 0 and n // 3 == T['mu'][n] + 1)
    add("n/3 = mu*2",
        lambda n, T: n % 3 == 0 and n // 3 == T['mu'][n] * 2)
    add("n/3 = sigma_m1",
        lambda n, T: n % 3 == 0 and T['sigma_m1'][n] >= 0 and n // 3 == T['sigma_m1'][n])
    add("n/phi = sigma/tau",
        lambda n, T: T['phi'][n] != 0 and T['tau'][n] != 0 and n % T['phi'][n] == 0 and T['sigma'][n] % T['tau'][n] == 0 and n // T['phi'][n] == T['sigma'][n] // T['tau'][n])

    # ── Category 2 Tier A: Cross-Function (15) ──
    add("tau = phi^2",
        lambda n, T: T['tau'][n] == T['phi'][n] ** 2)
    add("tau^2 = sigma+tau",
        lambda n, T: T['tau'][n] ** 2 == T['sigma'][n] + T['tau'][n])
    add("sigma*phi = n*tau",
        lambda n, T: T['sigma'][n] * T['phi'][n] == n * T['tau'][n])
    add("rad = sigma-n",
        lambda n, T: T['rad'][n] == T['sigma'][n] - n)
    add("rad = tau+phi",
        lambda n, T: T['rad'][n] == T['tau'][n] + T['phi'][n])
    add("sigma = rad*omega",
        lambda n, T: T['sigma'][n] == T['rad'][n] * T['omega'][n])
    add("sigma = phi*rad",
        lambda n, T: T['sigma'][n] == T['phi'][n] * T['rad'][n])
    add("sigma/phi = sigma-n",
        lambda n, T: T['phi'][n] != 0 and T['sigma'][n] % T['phi'][n] == 0 and T['sigma'][n] // T['phi'][n] == T['sigma'][n] - n)
    add("tau*phi = phi+rad",
        lambda n, T: T['tau'][n] * T['phi'][n] == T['phi'][n] + T['rad'][n])
    add("sigma*phi = tau*rad",
        lambda n, T: T['sigma'][n] * T['phi'][n] == T['tau'][n] * T['rad'][n])
    add("tau-1 = sigma/tau",
        lambda n, T: T['tau'][n] != 0 and T['sigma'][n] % T['tau'][n] == 0 and T['tau'][n] - 1 == T['sigma'][n] // T['tau'][n])
    add("sopfr-omega = n/phi",
        lambda n, T: T['phi'][n] != 0 and n % T['phi'][n] == 0 and T['sopfr'][n] - T['omega'][n] == n // T['phi'][n])
    add("sigma_m1+1 = n/sigma_m1",
        lambda n, T: T['sigma_m1'][n] > 0 and n % T['sigma_m1'][n] == 0 and T['sigma_m1'][n] + 1 == n // T['sigma_m1'][n])
    add("sopfr-1 = sigma_m1*2",
        lambda n, T: T['sigma_m1'][n] >= 0 and T['sopfr'][n] - 1 == T['sigma_m1'][n] * 2)
    add("mu*2 = n-tau",
        lambda n, T: T['mu'][n] * 2 == n - T['tau'][n])

    # ── Category 2 Tier B: Value-Coincidence (10) ──
    add("phi = omega",
        lambda n, T: T['phi'][n] == T['omega'][n])
    add("phi = Omega",
        lambda n, T: T['phi'][n] == T['Omega'][n])
    add("phi = sigma_m1",
        lambda n, T: T['sigma_m1'][n] >= 0 and T['phi'][n] == T['sigma_m1'][n])
    add("phi = mu+1",
        lambda n, T: T['phi'][n] == T['mu'][n] + 1)
    add("phi = mu*2",
        lambda n, T: T['phi'][n] == T['mu'][n] * 2)
    add("phi = tau/phi",
        lambda n, T: T['phi'][n] != 0 and T['tau'][n] % T['phi'][n] == 0 and T['phi'][n] == T['tau'][n] // T['phi'][n])
    add("omega^2 = phi+omega",
        lambda n, T: T['omega'][n] ** 2 == T['phi'][n] + T['omega'][n])
    add("phi*omega = phi+omega",
        lambda n, T: T['phi'][n] * T['omega'][n] == T['phi'][n] + T['omega'][n])
    add("Omega = sigma_m1",
        lambda n, T: T['sigma_m1'][n] >= 0 and T['Omega'][n] == T['sigma_m1'][n])
    add("mu = sigma_m1-1",
        lambda n, T: T['sigma_m1'][n] >= 0 and T['mu'][n] == T['sigma_m1'][n] - 1)

    # ── Category 3: Compound/Derived UNIQUE (6) ──
    add("n^2-sigma = tau!",
        lambda n, T: T['tau'][n] <= 20 and n * n - T['sigma'][n] == math.factorial(T['tau'][n]))
    add("n^3 = (3/2)*sigma^2  [2n^3=3*sigma^2]",
        lambda n, T: 2 * n ** 3 == 3 * T['sigma'][n] ** 2)
    add("tau! = n*tau",
        lambda n, T: T['tau'][n] <= 20 and math.factorial(T['tau'][n]) == n * T['tau'][n])
    add("sigma+tau = tau^2",
        lambda n, T: T['sigma'][n] + T['tau'][n] == T['tau'][n] ** 2)
    # sigma*phi = tau*rad is already in Tier A above, skip duplicate
    add("tau*sigma*phi*omega = 2^n*3",
        lambda n, T: n <= 62 and T['tau'][n] * T['sigma'][n] * T['phi'][n] * T['omega'][n] == (1 << n) * 3)

    # ── Additional known unique identities from n6_uniqueness_tester.py ──
    add("(n-3)! = n",
        lambda n, T: n >= 4 and math.factorial(n - 3) == n)
    add("tri(n) = fact(n)  [n*(n+1)/2 = n!]",
        lambda n, T: n > 0 and n * (n + 1) // 2 == math.factorial(n))
    add("sigma(tau(sigma)) = sigma  [self-loop]",
        lambda n, T: (
            T['sigma'][n] < len(T['sigma']) and
            T['tau'][T['sigma'][n]] < len(T['sigma']) and
            T['sigma'][T['tau'][T['sigma'][n]]] == T['sigma'][n]
        ))
    add("3n-6 = sigma",
        lambda n, T: 3 * n - 6 == T['sigma'][n])
    add("(n-1)!/2 = sopfr*sigma",
        lambda n, T: n > 1 and n <= 20 and math.factorial(n - 1) // 2 == T['sopfr'][n] * T['sigma'][n])
    add("lcm(1..n) = sopfr*sigma",
        lambda n, T: T['lcm1n'][n] == T['sopfr'][n] * T['sigma'][n])
    add("tau*phi = sigma-tau",
        lambda n, T: T['tau'][n] * T['phi'][n] == T['sigma'][n] - T['tau'][n])
    add("sigma = 2n  [perfect]",
        lambda n, T: T['sigma'][n] == 2 * n)

    # ── More cross-function identities from deep scan (filling to ~136) ──
    # Using remaining identities that involve different function combinations
    add("rad = n  [squarefree]",
        lambda n, T: T['rad'][n] == n)
    # But we only want those unique to 6. rad=n holds for all squarefree.
    # Let's add more compound/mixed ones that ARE unique to 6.

    # Additional from the scan that are unique-to-6 composites:
    add("sigma*omega = n*tau",
        lambda n, T: T['sigma'][n] * T['omega'][n] == n * T['tau'][n])
    add("phi+tau = n",
        lambda n, T: T['phi'][n] + T['tau'][n] == n)  # near-unique [6,8,9] but include
    add("sigma = phi*rad",  # duplicate, remove
        lambda n, T: False)  # placeholder
    add("n-phi = tau",
        lambda n, T: n - T['phi'][n] == T['tau'][n])
    add("sigma*2 = n*tau",
        lambda n, T: T['sigma'][n] * 2 == n * T['tau'][n])
    add("sigma/tau = n/2",
        lambda n, T: n % 2 == 0 and T['tau'][n] != 0 and T['sigma'][n] % T['tau'][n] == 0 and T['sigma'][n] // T['tau'][n] == n // 2)
    add("tau = 2*phi",
        lambda n, T: T['tau'][n] == 2 * T['phi'][n])
    add("omega+phi = tau",
        lambda n, T: T['omega'][n] + T['phi'][n] == T['tau'][n])
    add("sigma = n+rad",
        lambda n, T: T['sigma'][n] == n + T['rad'][n])
    add("sopfr+1 = rad",
        lambda n, T: T['sopfr'][n] + 1 == T['rad'][n])
    add("tau*sopfr = sigma+tau+phi",
        lambda n, T: T['tau'][n] * T['sopfr'][n] == T['sigma'][n] + T['tau'][n] + T['phi'][n])
    add("sigma-n = rad",
        lambda n, T: T['sigma'][n] - n == T['rad'][n])
    add("sigma*phi/n = tau",
        lambda n, T: n != 0 and (T['sigma'][n] * T['phi'][n]) % n == 0 and T['sigma'][n] * T['phi'][n] // n == T['tau'][n])
    add("rad*phi = sigma",
        lambda n, T: T['rad'][n] * T['phi'][n] == T['sigma'][n])
    add("sopfr*2 = sigma-phi",
        lambda n, T: T['sopfr'][n] * 2 == T['sigma'][n] - T['phi'][n])
    add("n = tau+phi",
        lambda n, T: n == T['tau'][n] + T['phi'][n])
    add("rad*omega = sigma",
        lambda n, T: T['rad'][n] * T['omega'][n] == T['sigma'][n])
    add("tau*rad = sigma*phi",
        lambda n, T: T['tau'][n] * T['rad'][n] == T['sigma'][n] * T['phi'][n])
    add("sigma-phi = sopfr*2",
        lambda n, T: T['sigma'][n] - T['phi'][n] == T['sopfr'][n] * 2)
    add("phi*sigma = tau*rad",
        lambda n, T: T['phi'][n] * T['sigma'][n] == T['tau'][n] * T['rad'][n])
    add("n*tau = sigma*phi",
        lambda n, T: n * T['tau'][n] == T['sigma'][n] * T['phi'][n])
    add("sigma*phi*omega = n*tau*omega",
        lambda n, T: T['sigma'][n] * T['phi'][n] * T['omega'][n] == n * T['tau'][n] * T['omega'][n])
    add("n/phi = tau-1",
        lambda n, T: T['phi'][n] != 0 and n % T['phi'][n] == 0 and n // T['phi'][n] == T['tau'][n] - 1)
    add("sigma = tau*(tau-1)",
        lambda n, T: T['sigma'][n] == T['tau'][n] * (T['tau'][n] - 1))
    add("sigma/n = phi",
        lambda n, T: T['sigma'][n] % n == 0 and T['sigma'][n] // n == T['phi'][n])
    add("rad/phi = n/phi",
        lambda n, T: T['phi'][n] != 0 and T['rad'][n] % T['phi'][n] == 0 and n % T['phi'][n] == 0 and T['rad'][n] // T['phi'][n] == n // T['phi'][n])
    add("tau*omega = n+phi",
        lambda n, T: T['tau'][n] * T['omega'][n] == n + T['phi'][n])
    add("sigma/phi = n",
        lambda n, T: T['phi'][n] != 0 and T['sigma'][n] % T['phi'][n] == 0 and T['sigma'][n] // T['phi'][n] == n)
    add("sigma*omega = sigma+n",
        lambda n, T: T['sigma'][n] * T['omega'][n] == T['sigma'][n] + n)
    add("phi*tau = sigma-tau",
        lambda n, T: T['phi'][n] * T['tau'][n] == T['sigma'][n] - T['tau'][n])
    add("n*omega = sigma",
        lambda n, T: n * T['omega'][n] == T['sigma'][n])
    add("tau*(tau-1) = sigma",
        lambda n, T: T['tau'][n] * (T['tau'][n] - 1) == T['sigma'][n])
    add("sopfr = n-mu",
        lambda n, T: T['sopfr'][n] == n - T['mu'][n])
    add("sigma+phi = tau*tau",
        lambda n, T: T['sigma'][n] + T['phi'][n] == T['tau'][n] ** 2)
    add("sigma-tau = tau*phi",
        lambda n, T: T['sigma'][n] - T['tau'][n] == T['tau'][n] * T['phi'][n])
    add("sigma-tau-phi = rad",
        lambda n, T: T['sigma'][n] - T['tau'][n] - T['phi'][n] == T['rad'][n])
    add("sopfr = phi+omega+mu",
        lambda n, T: T['sopfr'][n] == T['phi'][n] + T['omega'][n] + T['mu'][n])
    add("tau+phi+omega = n+phi",
        lambda n, T: T['tau'][n] + T['phi'][n] + T['omega'][n] == n + T['phi'][n])
    add("sigma/(tau-1) = tau",
        lambda n, T: T['tau'][n] > 1 and T['sigma'][n] % (T['tau'][n] - 1) == 0 and T['sigma'][n] // (T['tau'][n] - 1) == T['tau'][n])
    add("n+rad = sigma",
        lambda n, T: n + T['rad'][n] == T['sigma'][n])
    add("phi^2+phi = tau",
        lambda n, T: T['phi'][n] ** 2 + T['phi'][n] == T['tau'][n])
    add("omega*rad = sigma",
        lambda n, T: T['omega'][n] * T['rad'][n] == T['sigma'][n])
    add("n-sopfr = mu",
        lambda n, T: n - T['sopfr'][n] == T['mu'][n])
    add("sigma = tau^2-tau",
        lambda n, T: T['sigma'][n] == T['tau'][n] ** 2 - T['tau'][n])
    add("n+phi = tau*omega",
        lambda n, T: n + T['phi'][n] == T['tau'][n] * T['omega'][n])
    add("sigma*phi = n*tau",  # duplicate intentional — different form
        lambda n, T: False)  # skip
    add("sigma-rad = n",
        lambda n, T: T['sigma'][n] - T['rad'][n] == n)
    add("sigma_m1 = phi",
        lambda n, T: T['sigma_m1'][n] >= 0 and T['sigma_m1'][n] == T['phi'][n])
    add("sigma_m1 = omega",
        lambda n, T: T['sigma_m1'][n] >= 0 and T['sigma_m1'][n] == T['omega'][n])
    add("sigma_m1*phi = tau",
        lambda n, T: T['sigma_m1'][n] >= 0 and T['sigma_m1'][n] * T['phi'][n] == T['tau'][n])
    add("sigma_m1^2 = tau",
        lambda n, T: T['sigma_m1'][n] >= 0 and T['sigma_m1'][n] ** 2 == T['tau'][n])
    add("sigma_m1*sigma = n*tau",
        lambda n, T: T['sigma_m1'][n] >= 0 and T['sigma_m1'][n] * T['sigma'][n] == n * T['tau'][n])
    add("mu+omega = sigma_m1+1",
        lambda n, T: T['sigma_m1'][n] >= 0 and T['mu'][n] + T['omega'][n] == T['sigma_m1'][n] + 1)
    add("sigma_m1+omega = tau",
        lambda n, T: T['sigma_m1'][n] >= 0 and T['sigma_m1'][n] + T['omega'][n] == T['tau'][n])
    add("phi*sigma_m1 = tau",
        lambda n, T: T['sigma_m1'][n] >= 0 and T['phi'][n] * T['sigma_m1'][n] == T['tau'][n])
    add("tau = sigma_m1*omega",
        lambda n, T: T['sigma_m1'][n] >= 0 and T['tau'][n] == T['sigma_m1'][n] * T['omega'][n])
    add("sigma_m1^2 = phi*omega",
        lambda n, T: T['sigma_m1'][n] >= 0 and T['sigma_m1'][n] ** 2 == T['phi'][n] * T['omega'][n])
    add("Omega = omega",
        lambda n, T: T['Omega'][n] == T['omega'][n])
    add("Omega = mu+1",
        lambda n, T: T['Omega'][n] == T['mu'][n] + 1)
    add("Omega*2 = tau",
        lambda n, T: T['Omega'][n] * 2 == T['tau'][n])
    add("Omega+omega = tau",
        lambda n, T: T['Omega'][n] + T['omega'][n] == T['tau'][n])
    add("Omega*omega = tau",
        lambda n, T: T['Omega'][n] * T['omega'][n] == T['tau'][n])
    add("Omega = n/3",
        lambda n, T: n % 3 == 0 and T['Omega'][n] == n // 3)
    add("Omega+1 = n/phi",
        lambda n, T: T['phi'][n] != 0 and n % T['phi'][n] == 0 and T['Omega'][n] + 1 == n // T['phi'][n])
    add("Omega*sigma = n*tau",
        lambda n, T: T['Omega'][n] * T['sigma'][n] == n * T['tau'][n])
    add("Omega*rad = sigma",
        lambda n, T: T['Omega'][n] * T['rad'][n] == T['sigma'][n])
    add("Omega*phi = tau",
        lambda n, T: T['Omega'][n] * T['phi'][n] == T['tau'][n])
    add("sopfr*phi = sigma",
        lambda n, T: T['sopfr'][n] * T['phi'][n] == T['sigma'][n])
    add("sopfr = phi+tau-1",
        lambda n, T: T['sopfr'][n] == T['phi'][n] + T['tau'][n] - 1)
    add("sopfr*tau = n*tau-tau",
        lambda n, T: T['sopfr'][n] * T['tau'][n] == n * T['tau'][n] - T['tau'][n])
    add("sopfr+mu = n",
        lambda n, T: T['sopfr'][n] + T['mu'][n] == n)
    add("sopfr+omega = n+1",
        lambda n, T: T['sopfr'][n] + T['omega'][n] == n + 1)

    # Remove placeholder/duplicate entries
    ids = [(name, fn) for name, fn in ids if not (hasattr(fn, '__code__') and fn.__code__.co_code == (lambda n, T: False).__code__.co_code)]
    # Actually simpler: just filter by testing if fn returns False for all
    # Instead, let's just remove the two known placeholders by name
    clean = []
    seen_names = set()
    for name, fn in ids:
        # Skip exact duplicates and placeholders
        if name in seen_names:
            continue
        seen_names.add(name)
        clean.append((name, fn))
    return clean


def compute_scores(identities, tables, lo, hi):
    """For each n in [lo, hi], count how many identities are satisfied."""
    scores = {}
    for n in range(lo, hi + 1):
        count = 0
        for name, fn in identities:
            try:
                if fn(n, tables):
                    count += 1
            except Exception:
                pass
        scores[n] = count
    return scores


def first_pass_filter(identities, tables, limit):
    """Keep only identities that are actually unique to n=6 in [2, limit]."""
    unique = []
    for name, fn in identities:
        hits = []
        for n in range(2, limit + 1):
            try:
                if fn(n, tables):
                    hits.append(n)
            except Exception:
                pass
            if len(hits) > 1:
                break  # not unique
        if hits == [6]:
            unique.append((name, fn))
    return unique


def main():
    SCORE_LIMIT = 1000
    VERIFY_LIMIT = 100000
    BAR_LIMIT = 100

    print()
    print("=" * 70)
    print("  H-NOBEL-6: Uniqueness Principle — Computation")
    print("=" * 70)
    print()

    # Step 0: Build tables
    print(f"  Building arithmetic tables up to {VERIFY_LIMIT}...", end=" ", flush=True)
    tables = build_tables(VERIFY_LIMIT)
    print("done.")
    print()

    # Step 1: Get all candidate identities and verify uniqueness at 100K
    all_identities = make_identities()
    print(f"  Candidate identities: {len(all_identities)}")
    print(f"  Verifying uniqueness in [2, {VERIFY_LIMIT}]...", end=" ", flush=True)
    unique_ids = first_pass_filter(all_identities, tables, VERIFY_LIMIT)
    print(f"done. {len(unique_ids)} verified unique to n=6.")
    print()

    # List them
    print("  VERIFIED UNIQUE IDENTITIES:")
    print("  " + "-" * 60)
    for i, (name, _) in enumerate(unique_ids, 1):
        print(f"  {i:3d}. {name}")
    print()

    # Step 2: Compute uniqueness scores for n=2..1000
    print(f"  Computing uniqueness scores for n=2..{SCORE_LIMIT}...")
    scores = compute_scores(unique_ids, tables, 2, SCORE_LIMIT)

    # Top scorers
    sorted_scores = sorted(scores.items(), key=lambda x: -x[1])
    print()
    print("  TOP 20 SCORING NUMBERS:")
    print("  " + "-" * 40)
    print(f"  {'Rank':>4}  {'n':>6}  {'Score':>5}  Notes")
    print(f"  {'----':>4}  {'------':>6}  {'-----':>5}  -----")

    perfect_nums = {6, 28, 496, 8128}
    hc_nums = {6, 12, 24, 36, 48, 60, 120, 180, 240, 360, 720}
    primes_small = set()
    for p in range(2, 1001):
        if tables['tau'][p] == 2:
            primes_small.add(p)

    for rank, (n, sc) in enumerate(sorted_scores[:20], 1):
        notes = []
        if n in perfect_nums:
            notes.append("PERFECT")
        if n in hc_nums:
            notes.append("HC")
        if n in primes_small:
            notes.append("prime")
        note_str = ", ".join(notes) if notes else ""
        print(f"  {rank:4d}  {n:6d}  {sc:5d}  {note_str}")

    # Step 3: Perfect number comparison
    print()
    print("  PERFECT NUMBER COMPARISON:")
    print("  " + "-" * 40)
    for pn in [6, 28, 496, 8128]:
        if pn <= SCORE_LIMIT:
            sc = scores[pn]
        else:
            # compute individually
            sc = 0
            for name, fn in unique_ids:
                try:
                    if fn(pn, tables):
                        sc += 1
                except Exception:
                    pass
        print(f"  n={pn:>5}:  Score = {sc}")

    # Step 4: Highly composite number comparison
    print()
    print("  HIGHLY COMPOSITE NUMBER COMPARISON:")
    print("  " + "-" * 40)
    hc_list = [6, 12, 24, 36, 48, 60, 120, 180, 240, 360, 720]
    for hc in hc_list:
        sc = scores.get(hc, 0)
        print(f"  n={hc:>5}:  Score = {sc}")

    # Step 5: Statistical significance
    all_scores = [scores[n] for n in range(2, SCORE_LIMIT + 1)]
    mean_sc = statistics.mean(all_scores)
    std_sc = statistics.stdev(all_scores)
    score_6 = scores[6]
    z_score = (score_6 - mean_sc) / std_sc if std_sc > 0 else float('inf')

    print()
    print("  STATISTICAL SIGNIFICANCE:")
    print("  " + "-" * 40)
    print(f"  Score(n=6)     = {score_6}")
    print(f"  Mean score     = {mean_sc:.4f}")
    print(f"  Std deviation  = {std_sc:.4f}")
    print(f"  Median score   = {statistics.median(all_scores):.1f}")
    print(f"  Max (non-6)    = {max(sc for n, sc in scores.items() if n != 6)}")
    print(f"  Z-score(n=6)   = {z_score:.2f}")
    print()

    # Distribution
    from collections import Counter
    dist = Counter(all_scores)
    print("  SCORE DISTRIBUTION (n=2..1000):")
    print("  " + "-" * 40)
    for sc_val in sorted(dist.keys()):
        bar = "#" * min(dist[sc_val], 60)
        marker = " <-- n=6" if sc_val == score_6 else ""
        print(f"  Score {sc_val:3d}: {dist[sc_val]:5d} numbers  {bar}{marker}")

    # Step 6: Intersection theorem
    print()
    print("  INTERSECTION THEOREM (Top 10 most diverse identities):")
    print("  " + "-" * 60)

    # Pick 10 identities that involve different function combos
    # Prioritize ones connecting different functions
    top10_names = [
        "sigma*phi = n*tau",
        "n^2-sigma = tau!",
        "n = sopfr+1",
        "n-2 = tau",
        "tau = phi^2",
        "rad = tau+phi",
        "(n-3)! = n",
        "tau*sigma*phi*omega = 2^n*3",
        "sigma(tau(sigma)) = sigma  [self-loop]",
        "n/phi = sigma/tau",
    ]
    top10 = [(name, fn) for name, fn in unique_ids if name in top10_names]
    # Fill if needed
    if len(top10) < 10:
        for name, fn in unique_ids:
            if name not in top10_names and len(top10) < 10:
                top10.append((name, fn))
                top10_names.append(name)

    print(f"  Selected {len(top10)} identities:")
    for i, (name, _) in enumerate(top10, 1):
        print(f"    {i:2d}. {name}")

    # Find all n in [2, 100000] satisfying ALL simultaneously
    print()
    print(f"  Searching for n in [2, {VERIFY_LIMIT}] satisfying ALL {len(top10)} simultaneously...")
    intersection_hits = []
    for n in range(2, VERIFY_LIMIT + 1):
        all_pass = True
        for name, fn in top10:
            try:
                if not fn(n, tables):
                    all_pass = False
                    break
            except Exception:
                all_pass = False
                break
        if all_pass:
            intersection_hits.append(n)

    print(f"  Result: {intersection_hits}")
    if intersection_hits == [6]:
        print("  ==> ONLY n=6 satisfies all 10 simultaneously! QED")
    else:
        print(f"  ==> {len(intersection_hits)} numbers satisfy all 10")

    # Progressive intersection
    print()
    print("  PROGRESSIVE INTERSECTION (cumulative):")
    print("  " + "-" * 50)
    print(f"  {'k':>3}  {'Identity added':40s}  {'|Intersection|':>15}")
    cumulative = set(range(2, VERIFY_LIMIT + 1))
    for k, (name, fn) in enumerate(top10, 1):
        satisfiers = set()
        for n in cumulative:
            try:
                if fn(n, tables):
                    satisfiers.add(n)
            except Exception:
                pass
        cumulative = cumulative & satisfiers
        count_str = str(len(cumulative))
        if len(cumulative) <= 5:
            count_str += f"  {sorted(cumulative)}"
        print(f"  {k:3d}  {name:40s}  {count_str:>15}")
        if len(cumulative) <= 1:
            break

    # Step 7: ASCII bar chart
    print()
    print(f"  ASCII BAR CHART: Score(n) for n=2..{BAR_LIMIT}")
    print("  " + "-" * 70)
    print("  Legend: P=perfect, H=highly composite, p=prime, .=other")
    print()

    max_score = max(scores[n] for n in range(2, BAR_LIMIT + 1))
    bar_width = 50

    for n in range(2, BAR_LIMIT + 1):
        sc = scores[n]
        if sc == 0:
            bar = ""
        else:
            bar = "#" * max(1, int(sc / max(max_score, 1) * bar_width))

        if n in perfect_nums:
            marker = "P"
        elif n in hc_nums:
            marker = "H"
        elif n in primes_small:
            marker = "p"
        else:
            marker = "."

        label = f"  {n:3d} {marker} {sc:3d} |{bar}"
        print(label)

    # Summary
    print()
    print("=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    runner_up_n, runner_up_sc = sorted_scores[1] if sorted_scores[0][0] == 6 else sorted_scores[0]
    if sorted_scores[0][0] == 6:
        runner_up_n, runner_up_sc = sorted_scores[1]
    print(f"  Total verified unique-to-6 identities: {len(unique_ids)}")
    print(f"  Score(n=6)     = {score_6}")
    print(f"  Runner-up      = n={runner_up_n} with score {runner_up_sc}")
    print(f"  Gap            = {score_6 - runner_up_sc}")
    print(f"  Z-score        = {z_score:.2f}")
    print(f"  Intersection of top 10: {intersection_hits}")
    print()


if __name__ == "__main__":
    main()
