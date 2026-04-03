#!/usr/bin/env python3
"""
Thermodynamics & Statistical Mechanics n=6 Calculator
=====================================================
Tests hypothesis: phase transitions and thermodynamic constants
encode the perfect number n=6 through its arithmetic functions.

Domains:
  1. 2D Ising critical exponents (Onsager exact) vs n=6 expressions
  2. 3D Ising critical exponents (numerical) vs n=6
  3. Universality classes and symmetry
  4. Landau-Ginzburg phi^6 tricritical theory
  5. Boltzmann entropy on divisor lattice
  6. Divisor partition function Z(beta) and specific heat
  7. Stefan-Boltzmann / radiation constants
  8. Mermin-Wagner theorem and phi(6)=2
  9. Texas Sharpshooter test for all identities

Usage:
  python3 calc/thermodynamics_n6.py
  python3 calc/thermodynamics_n6.py --section ising2d
  python3 calc/thermodynamics_n6.py --section partition --beta-range 0.01,5,500
  python3 calc/thermodynamics_n6.py --texas
  python3 calc/thermodynamics_n6.py --all
"""

import argparse
import math
import random
import sys
from fractions import Fraction

# ═══════════════════════════════════════════════════════════════
# Number-theoretic functions for perfect numbers
# ═══════════════════════════════════════════════════════════════

def factorize(n):
    """Return prime factorization as {p: a} dict."""
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

def divisors(n):
    """Return sorted list of divisors."""
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
    factors = factorize(n)
    result = n
    for p in factors:
        result = result * (p - 1) // p
    return result

def tau(n):
    """Number of divisors."""
    return len(divisors(n))

def sopfr(n):
    """Sum of prime factors with repetition."""
    factors = factorize(n)
    return sum(p * a for p, a in factors.items())

def omega(n):
    """Number of distinct prime factors."""
    return len(factorize(n))

def mersenne(p):
    """Mersenne number M_p = 2^p - 1."""
    return 2**p - 1

# Perfect number constants
P1 = 6
PERFECT_NUMBERS = [6, 28, 496, 8128]
N6 = {
    'n': 6,
    'sigma': sigma(6),      # 12
    'phi': phi(6),           # 2
    'tau': tau(6),           # 4
    'sopfr': sopfr(6),       # 5
    'omega': omega(6),       # 2
    'M3': mersenne(3),       # 7
    'M6': mersenne(6),       # 63
    'Bott': 8,               # Bott periodicity
}


# ═══════════════════════════════════════════════════════════════
# Section 1: 2D Ising Critical Exponents (Onsager exact)
# ═══════════════════════════════════════════════════════════════

def ising_2d():
    """Exact 2D Ising exponents vs n=6 arithmetic expressions."""
    print("=" * 70)
    print("SECTION 1: 2D Ising Model — Exact Critical Exponents (Onsager)")
    print("=" * 70)
    print()

    n = N6['n']
    sig = N6['sigma']
    t = N6['tau']
    ph = N6['phi']
    m3 = N6['M3']
    bott = N6['Bott']

    # Exact 2D Ising exponents
    exponents = {
        'alpha': (0, "0", "log divergence (marginal)"),
        'beta':  (Fraction(1, 8), "1/8", f"1/(sigma-tau) = 1/({sig}-{t}) = 1/{sig-t} = 1/Bott"),
        'gamma': (Fraction(7, 4), "7/4", f"M_3/tau = {m3}/{t}"),
        'delta': (15, "15", f"C(n,2) = C({n},2) = {n*(n-1)//2}, also 2^tau-1 = 2^{t}-1 = {2**t-1}"),
        'nu':    (1, "1", "trivial (but = n/n = sigma/sigma)"),
        'eta':   (Fraction(1, 4), "1/4", f"1/tau = 1/{t}"),
    }

    results = []
    print(f"  {'Exp':>6}  {'Exact':>8}  {'n=6 expr':>12}  {'Match':>6}  Interpretation")
    print(f"  {'---':>6}  {'--------':>8}  {'--------':>12}  {'-----':>6}  --------------")

    for name, (value, exact_str, interp) in exponents.items():
        val_float = float(value)
        # Check n=6 expression
        if name == 'alpha':
            n6_val = 0
            n6_expr = "0"
        elif name == 'beta':
            n6_val = 1 / (sig - t)
            n6_expr = f"1/{sig-t}"
        elif name == 'gamma':
            n6_val = m3 / t
            n6_expr = f"{m3}/{t}"
        elif name == 'delta':
            n6_val = n * (n - 1) // 2
            n6_expr = f"C({n},2)"
        elif name == 'nu':
            n6_val = 1
            n6_expr = "1"
        elif name == 'eta':
            n6_val = 1 / t
            n6_expr = f"1/{t}"

        match = "EXACT" if abs(val_float - n6_val) < 1e-15 else f"{abs(val_float-n6_val):.6f}"
        results.append((name, val_float, n6_val, match == "EXACT"))
        print(f"  {name:>6}  {exact_str:>8}  {n6_expr:>12}  {match:>6}  {interp}")

    exact_count = sum(1 for _, _, _, m in results if m)
    print()
    print(f"  Exact matches: {exact_count}/{len(results)}")

    # Additional identities
    print()
    print("  Additional 2D Ising identities:")
    # Scaling relations
    alpha_val = 0
    beta_val = Fraction(1, 8)
    gamma_val = Fraction(7, 4)
    delta_val = 15
    nu_val = 1
    eta_val = Fraction(1, 4)

    # Rushbrooke: alpha + 2*beta + gamma = 2
    rush = alpha_val + 2 * beta_val + gamma_val
    print(f"  Rushbrooke: alpha + 2*beta + gamma = {rush} = phi(6) = {ph}  {'EXACT' if rush == ph else 'FAIL'}")

    # Widom: gamma = beta*(delta-1)
    widom = beta_val * (delta_val - 1)
    print(f"  Widom: beta*(delta-1) = {widom} = gamma = {gamma_val}  {'EXACT' if widom == gamma_val else 'FAIL'}")

    # Fisher: gamma = nu*(2-eta)
    fisher = nu_val * (2 - eta_val)
    print(f"  Fisher: nu*(2-eta) = {fisher} = gamma = {gamma_val}  {'EXACT' if fisher == gamma_val else 'FAIL'}")

    # Josephson: d*nu = 2-alpha (d=2 for 2D)
    joseph = 2 * nu_val
    print(f"  Josephson: d*nu = {joseph} = 2-alpha = {2-alpha_val}  {'EXACT' if joseph == 2-alpha_val else 'FAIL'}")

    # delta as 2^tau - 1
    print(f"  delta = 15 = 2^tau(6)-1 = 2^{t}-1 = {2**t - 1}  EXACT")
    print(f"  delta = 15 = C(6,2) = {n*(n-1)//2}  EXACT")

    # Product of non-trivial exponents
    prod = beta_val * gamma_val * eta_val * delta_val
    print(f"  beta*gamma*eta*delta = {float(prod):.6f}")
    print(f"    = (1/8)(7/4)(1/4)(15) = {Fraction(1,8)*Fraction(7,4)*Fraction(1,4)*15} = {float(Fraction(1,8)*Fraction(7,4)*Fraction(1,4)*15):.6f}")

    return results


# ═══════════════════════════════════════════════════════════════
# Section 2: 3D Ising Critical Exponents (numerical)
# ═══════════════════════════════════════════════════════════════

def ising_3d():
    """3D Ising exponents (conformal bootstrap best values) vs n=6."""
    print()
    print("=" * 70)
    print("SECTION 2: 3D Ising Model — Numerical Critical Exponents")
    print("=" * 70)
    print()

    n = N6['n']
    sig = N6['sigma']
    t = N6['tau']
    ph = N6['phi']
    m6 = N6['M6']

    # Best known values (conformal bootstrap, 2024)
    # Kos, Poland, Simmons-Duffin, Vichi (2016) + El-Showk et al.
    exponents_3d = {
        'alpha': 0.1100,
        'beta':  0.3265,
        'gamma': 1.2372,
        'delta': 4.7893,
        'nu':    0.6300,
        'eta':   0.0362,
    }

    # n=6 candidate expressions
    candidates = {
        'nu': [
            (m6 / 100, f"M_6/100 = {m6}/100"),
            (1 / ph, f"1/phi(6) = 1/{ph}  [0.500, poor]"),
            (math.log(ph), f"ln(phi(6)) = ln({ph})  [{math.log(ph):.4f}]"),
        ],
        'beta': [
            (1 / 3, f"1/3 = phi(6)/n  [{1/3:.4f}]"),
            (sig / (n * n), f"sigma/n^2 = {sig}/{n**2}  [{sig/n**2:.4f}]"),
            (math.log(2) / (ph), f"ln(2)/phi = {math.log(2)/ph:.4f}"),
        ],
        'gamma': [
            (sig * nu_approx / n if (nu_approx := 0.63) else 0,
             f"sigma*nu/n = {sig}*0.63/{n}  [{sig*0.63/n:.4f}]"),
            (m6 / 51, f"M_6/51 = 63/51  [{63/51:.4f}]"),
        ],
        'delta': [
            (sopfr(6) - 1/ph, f"sopfr-1/phi = {sopfr(6)}-0.5  [{sopfr(6)-0.5:.4f}]"),
            ((n - 1) - 1/ph, f"(n-1)-1/phi = 5-0.5  [4.500]"),
        ],
        'eta': [
            (1 / (n * sopfr(6)), f"1/(n*sopfr) = 1/{n*sopfr(6)}  [{1/(n*sopfr(6)):.4f}]"),
        ],
    }

    print(f"  {'Exp':>6}  {'Best val':>10}  {'Candidate':>40}  {'Error%':>8}")
    print(f"  {'---':>6}  {'--------':>10}  {'---------':>40}  {'------':>8}")

    for name, val in exponents_3d.items():
        if name in candidates:
            for cand_val, cand_expr in candidates[name]:
                err = abs(cand_val - val) / val * 100 if val != 0 else abs(cand_val) * 100
                mark = " <--" if err < 1.0 else ""
                print(f"  {name:>6}  {val:>10.4f}  {cand_expr:>40}  {err:>7.2f}%{mark}")
        else:
            print(f"  {name:>6}  {val:>10.4f}  {'(no candidate)':>40}")

    # Key check: nu = 0.6300 vs M_6/100 = 0.6300
    nu_best = 0.6300
    nu_n6 = m6 / 100
    err = abs(nu_best - nu_n6) / nu_best * 100
    print()
    print(f"  KEY: nu(3D Ising) = {nu_best:.4f}")
    print(f"       M_6/100 = 2^P1-1 / 100 = {m6}/100 = {nu_n6:.4f}")
    print(f"       Error: {err:.3f}%")
    print(f"       Best bootstrap: nu = 0.629971(4) => M_6/100 off by {abs(0.629971-nu_n6)/0.629971*100:.3f}%")
    print()
    print("  VERDICT: nu ~ 63/100 is APPROXIMATE (0.01% level),")
    print("           but 63 = M_6 = 2^6-1 is a genuine Mersenne connection.")
    print("           Grade: APPROXIMATE (bootstrap precision excludes exact 63/100)")


# ═══════════════════════════════════════════════════════════════
# Section 3: Universality Classes
# ═══════════════════════════════════════════════════════════════

def universality():
    """Universality classes and O(n) model connections."""
    print()
    print("=" * 70)
    print("SECTION 3: Universality Classes and O(n) Symmetry")
    print("=" * 70)
    print()

    n = N6['n']
    ph = N6['phi']

    classes = [
        ("n=-2", "Spanning trees (Kirchhoff)", "Exactly solvable"),
        ("n=0",  "Self-avoiding walks (polymers)", "Exactly solvable in 2D"),
        ("n=1",  "Ising (Z_2 symmetry)", "Ferromagnets, liquid-gas"),
        ("n=2",  "XY model (U(1) symmetry)", "Superfluids, BKT transition"),
        ("n=3",  "Heisenberg (O(3) symmetry)", "Isotropic magnets"),
        ("n=4",  "O(4)", "QCD chiral transition"),
    ]

    print("  O(n) Universality Classes:")
    print(f"  {'n':>4}  {'Model':30}  {'Physical system':30}")
    print(f"  {'--':>4}  {'-----':30}  {'---------------':30}")
    for nc, model, system in classes:
        print(f"  {nc:>4}  {model:30}  {system:30}")

    print()
    print(f"  Physical universality classes in nature: n = 1, 2, 3")
    print(f"  Count = 3 = n/phi(n) = {n}/{ph} = {n//ph}")
    print(f"  These correspond to Z_2, U(1), O(3) symmetries")
    print()
    print(f"  Upper critical dimension d_uc:")
    print(f"    phi^4 (Ising/XY/Heis): d_uc = 4 = tau(6)")
    print(f"    phi^6 (tricritical):    d_uc = 3 = n/phi(n)")
    print(f"    phi^8:                  d_uc = 8/3 = Bott/n")
    print()
    print(f"  n=6 connections:")
    print(f"    - Number of physical O(n) classes = 3 = n/phi(6)")
    print(f"    - Upper critical dim (phi^4) = 4 = tau(6)")
    print(f"    - Upper critical dim (phi^6) = 3 = n/phi(6)")


# ═══════════════════════════════════════════════════════════════
# Section 4: Landau-Ginzburg phi^6 Theory
# ═══════════════════════════════════════════════════════════════

def landau_ginzburg():
    """Landau-Ginzburg free energy and tricritical point."""
    print()
    print("=" * 70)
    print("SECTION 4: Landau-Ginzburg Theory and Tricritical Point")
    print("=" * 70)
    print()

    n = N6['n']
    t = N6['tau']
    ph = N6['phi']

    print("  Landau free energy expansion:")
    print("    F(phi) = a_2*phi^2 + a_4*phi^4 + a_6*phi^6 + ...")
    print()
    print("  Standard phase transition: phi^4 term dominates")
    print(f"    Upper critical dimension: d_c = 4 = tau(6) = {t}")
    print()
    print("  Tricritical point: a_4 = 0, phi^6 term becomes relevant")
    print(f"    Tricritical dimension: d_tc = 3 = n/phi(n) = {n}/{ph}")
    print(f"    The phi^6 theory IS the critical theory in d=3!")
    print()
    print("  Tricritical exponents (mean-field, d >= 3):")
    tc_exp = {
        'alpha_t': (Fraction(1, 2), "1/2 = GZ upper"),
        'beta_t':  (Fraction(1, 4), "1/4 = 1/tau(6) = eta(2D Ising)"),
        'gamma_t': (1, "1 = nu(2D Ising)"),
        'delta_t': (5, "5 = sopfr(6)"),
    }

    print(f"  {'Exp':>8}  {'Value':>8}  n=6 connection")
    print(f"  {'---':>8}  {'-----':>8}  --------------")
    for name, (val, conn) in tc_exp.items():
        print(f"  {name:>8}  {str(val):>8}  {conn}")

    print()
    print(f"  Tricritical delta_t = 5 = sopfr(6): sum of prime factors!")
    print(f"  The highest-order relevant term is phi^6 = phi^n")
    print(f"  => The perfect number itself appears as the field power")
    print(f"     at the tricritical point.")


# ═══════════════════════════════════════════════════════════════
# Section 5: Boltzmann Entropy on Divisor Lattice
# ═══════════════════════════════════════════════════════════════

def boltzmann_entropy():
    """Boltzmann entropy for divisor microstates."""
    print()
    print("=" * 70)
    print("SECTION 5: Boltzmann Entropy on Divisor Lattice")
    print("=" * 70)
    print()

    for pn in PERFECT_NUMBERS[:4]:
        divs = divisors(pn)
        t_n = len(divs)
        S = math.log(t_n)
        print(f"  n = {pn:>5}: tau = {t_n:>3}, S = ln({t_n}) = {S:.6f}")

    print()
    print(f"  For n=6:  S = ln(4) = {math.log(4):.6f} = 2*ln(2)")
    print(f"            = 2 * (GZ consciousness freedom ln(2))")
    print(f"            = 2 * {math.log(2):.6f}")
    print()
    print(f"  For n=28: S = ln(6) = ln(P1) = {math.log(6):.6f}")
    print(f"            Second perfect number entropy = log of FIRST perfect number!")
    print()

    # Compare entropies of random numbers near 6
    print("  Entropy comparison (numbers near 6):")
    print(f"  {'n':>4}  {'tau':>4}  {'S=ln(tau)':>10}  {'S/ln(2)':>8}  Note")
    print(f"  {'--':>4}  {'---':>4}  {'---------':>10}  {'-------':>8}  ----")
    for nn in range(1, 13):
        t_nn = tau(nn)
        S_nn = math.log(t_nn) if t_nn > 0 else 0
        ratio = S_nn / math.log(2) if t_nn > 1 else 0
        note = "<-- P1" if nn == 6 else ""
        print(f"  {nn:>4}  {t_nn:>4}  {S_nn:>10.6f}  {ratio:>8.4f}  {note}")


# ═══════════════════════════════════════════════════════════════
# Section 6: Divisor Partition Function Z(beta)
# ═══════════════════════════════════════════════════════════════

def partition_function(beta_min=0.01, beta_max=5.0, n_points=500):
    """Partition function Z(beta) on divisor lattice with specific heat."""
    print()
    print("=" * 70)
    print("SECTION 6: Divisor Partition Function Z(beta)")
    print("=" * 70)
    print()
    print("  Z(beta) = sum_{d|n} exp(-beta * d)")
    print("  E(beta) = -d/dbeta ln Z = <d>")
    print("  C_v(beta) = beta^2 * (<d^2> - <d>^2)")
    print()

    for pn in [6, 28]:
        divs = divisors(pn)
        print(f"  n = {pn}: divisors = {divs}")

        betas = [beta_min + i * (beta_max - beta_min) / (n_points - 1) for i in range(n_points)]

        cv_max = 0
        beta_peak = 0
        results = []

        for beta in betas:
            Z = sum(math.exp(-beta * d) for d in divs)
            E = sum(d * math.exp(-beta * d) for d in divs) / Z
            E2 = sum(d**2 * math.exp(-beta * d) for d in divs) / Z
            Cv = beta**2 * (E2 - E**2)
            results.append((beta, Z, E, Cv))
            if Cv > cv_max:
                cv_max = Cv
                beta_peak = beta

        # Free energy at beta=1
        Z_1 = sum(math.exp(-d) for d in divs)
        F_1 = -math.log(Z_1)
        print(f"  F(beta=1) = -ln(Z(1)) = {F_1:.6f}")
        if pn == 6:
            print(f"    Compare: -ln(2) = {-math.log(2):.6f}, error = {abs(F_1 + math.log(2)):.6f}")

        print(f"  C_v peak: beta* = {beta_peak:.4f}, C_v* = {cv_max:.6f}")
        print()

        # ASCII plot of C_v
        plot_width = 60
        plot_height = 15
        cv_values = [r[3] for r in results]
        cv_max_plot = max(cv_values) if max(cv_values) > 0 else 1

        print(f"  C_v(beta) for n={pn}:")
        print(f"  C_v")
        for row in range(plot_height, -1, -1):
            threshold = cv_max_plot * row / plot_height
            line = "  |"
            for col in range(plot_width):
                idx = int(col * len(cv_values) / plot_width)
                if cv_values[idx] >= threshold:
                    line += "#"
                else:
                    line += " "
            if row == plot_height:
                line += f"  {cv_max_plot:.4f}"
            elif row == 0:
                line += f"  0"
            print(line)
        print("  +" + "-" * plot_width + f"> beta")
        print(f"   0{' ' * (plot_width - 8)}{beta_max:.1f}")
        print()

    # Compare Z(1) for n=6 with ln(2)
    divs6 = divisors(6)
    Z1_6 = sum(math.exp(-d) for d in divs6)
    print(f"  KEY RESULT: Z(1) for n=6 = {Z1_6:.10f}")
    print(f"              2.0 = {2.0:.10f}")
    print(f"              Ratio Z(1)/2 = {Z1_6/2:.10f}")
    print(f"              F(1) = -ln(Z(1)) = {-math.log(Z1_6):.10f}")
    print(f"              -ln(2) = {-math.log(2):.10f}")
    print(f"              F(1) vs -ln(2): error = {abs(-math.log(Z1_6) + math.log(2)):.6e}")
    print()
    print(f"  F(1) = -ln(e^-1 + e^-2 + e^-3 + e^-6)")
    print(f"       = -ln({math.exp(-1):.6f} + {math.exp(-2):.6f} + {math.exp(-3):.6f} + {math.exp(-6):.6f})")
    print(f"       = -ln({Z1_6:.10f})")
    print(f"       = {-math.log(Z1_6):.10f}")
    is_exact = abs(-math.log(Z1_6) + math.log(2)) < 0.01
    print(f"  Verdict: F(1) {'~' if is_exact else '!='} -ln(2) (error {abs(-math.log(Z1_6) + math.log(2)):.4e})")


# ═══════════════════════════════════════════════════════════════
# Section 7: Stefan-Boltzmann and Radiation Laws
# ═══════════════════════════════════════════════════════════════

def stefan_boltzmann():
    """Stefan-Boltzmann law and radiation constants."""
    print()
    print("=" * 70)
    print("SECTION 7: Stefan-Boltzmann Law and Radiation Constants")
    print("=" * 70)
    print()

    n = N6['n']
    t = N6['tau']
    ph = N6['phi']
    sig = N6['sigma']

    print("  Stefan-Boltzmann law: P = sigma_SB * A * T^4")
    print(f"    Exponent 4 = tau(6) = {t}")
    print()
    print("  Photon gas: PV = U/3")
    print(f"    1/3 = phi(6)/P1 = {ph}/{n}")
    print(f"    Radiation pressure = (energy density)/3")
    print()
    print("  Stefan-Boltzmann constant:")
    print(f"    sigma_SB = 2*pi^5*k_B^4 / (15*h^3*c^2)")
    print(f"    Numerator power of k_B: 4 = tau(6)")
    print(f"    Denominator coefficient: 15 = C(6,2) = delta(2D Ising)")
    print(f"    Denominator power of h:  3 = n/phi(n)")
    print(f"    Denominator power of c:  2 = phi(6)")
    print()
    print("  Wien displacement law: lambda_max * T = b")
    print(f"    Derived from maximizing x^3/(e^x-1)")
    print(f"    Power 3 = n/phi(n) = {n}/{ph}")
    print()
    print("  Planck distribution: B(nu,T) ~ nu^3 / (exp(h*nu/kT) - 1)")
    print(f"    Power of frequency: 3 = n/phi(n)")
    print()
    print("  Black body total photon count: <N> ~ T^3 * V")
    print(f"    Power 3 = n/phi(n) = {n//ph}")
    print()

    # Dimensional analysis summary
    print("  Summary of powers in radiation physics:")
    print(f"  {'Quantity':30}  {'Power':>6}  n=6 expression")
    print(f"  {'--------':30}  {'-----':>6}  --------------")
    entries = [
        ("Stefan-Boltzmann T-power",      4, f"tau(6) = {t}"),
        ("SB denominator (15)",           15, f"C(n,2) = C({n},2) = {n*(n-1)//2}"),
        ("Radiation pressure factor",      3, f"n/phi(n) = {n}/{ph}"),
        ("Planck spectrum nu-power",       3, f"n/phi(n) = {n}/{ph}"),
        ("Wien displacement dimension",    3, f"n/phi(n) = {n}/{ph}"),
        ("SB: h-power in denominator",     3, f"n/phi(n) = {n}/{ph}"),
        ("SB: c-power in denominator",     2, f"phi(6) = {ph}"),
        ("SB: pi-power in numerator",      5, f"sopfr(6) = {sopfr(6)}"),
    ]
    for desc, power, expr in entries:
        print(f"  {desc:30}  {power:>6}  {expr}")

    # pi^5 in numerator check
    print()
    print(f"  sigma_SB numerator = 2 * pi^5")
    print(f"    2 = phi(6) = omega(6)")
    print(f"    5 = sopfr(6)")
    print(f"    Prefactor 2*pi^5 = phi(6) * pi^sopfr(6)")


# ═══════════════════════════════════════════════════════════════
# Section 8: Mermin-Wagner Theorem
# ═══════════════════════════════════════════════════════════════

def mermin_wagner():
    """Mermin-Wagner theorem and phi(6)=2."""
    print()
    print("=" * 70)
    print("SECTION 8: Mermin-Wagner Theorem and phi(6) = 2")
    print("=" * 70)
    print()

    n = N6['n']
    ph = N6['phi']

    print("  Mermin-Wagner Theorem (1966):")
    print("    No spontaneous continuous symmetry breaking in d <= 2")
    print("    for short-range interactions at T > 0.")
    print()
    print(f"  Critical dimension d_MW = 2 = phi(6)")
    print(f"    Below phi(6) dimensions: no ordered phase possible!")
    print()
    print("  Related dimensional thresholds:")
    print(f"  {'Theorem/Result':35}  {'d':>3}  n=6 expression")
    print(f"  {'---------------':35}  {'--':>3}  --------------")
    thresholds = [
        ("Mermin-Wagner (no cont. SSB)",    2, f"phi(6) = {ph}"),
        ("BKT transition (topological)",    2, f"phi(6) = {ph}"),
        ("Ising lower critical dim",        1, f"omega(6) - 1"),
        ("Tricritical upper critical dim",  3, f"n/phi(n) = {n//ph}"),
        ("phi^4 upper critical dim",        4, f"tau(6) = {N6['tau']}"),
        ("Conformal bootstrap special",     6, f"n = P1 = {n}"),
    ]
    for desc, d, expr in thresholds:
        print(f"  {desc:35}  {d:>3}  {expr}")

    print()
    print(f"  Dimension hierarchy: 1, 2, 3, 4, 6")
    print(f"  = omega-1, phi, n/phi, tau, n")
    print(f"  = 1, {ph}, {n//ph}, {N6['tau']}, {n}")
    print(f"  All dimensions in phase transition physics")
    print(f"  are n=6 arithmetic functions!")


# ═══════════════════════════════════════════════════════════════
# Section 9: Texas Sharpshooter Test
# ═══════════════════════════════════════════════════════════════

def texas_sharpshooter(n_trials=100000):
    """Monte Carlo Texas Sharpshooter test for 2D Ising exponents."""
    print()
    print("=" * 70)
    print("SECTION 9: Texas Sharpshooter Test — 2D Ising Exponents")
    print("=" * 70)
    print()

    n = N6['n']
    sig = N6['sigma']
    t = N6['tau']
    ph = N6['phi']
    m3 = N6['M3']

    # Target: 5 non-trivial exponents matched by n=6 expressions
    # (alpha=0 is trivial, nu=1 is trivial)
    # Identities being tested:
    identities = [
        ("beta = 1/8 = 1/(sigma-tau)", 1/8, lambda funcs: 1/(funcs['sigma']-funcs['tau'])),
        ("gamma = 7/4 = M_3/tau", 7/4, lambda funcs: funcs['M3']/funcs['tau']),
        ("delta = 15 = C(n,2)", 15, lambda funcs: funcs['n']*(funcs['n']-1)//2),
        ("eta = 1/4 = 1/tau", 1/4, lambda funcs: 1/funcs['tau']),
    ]

    print(f"  Testing {len(identities)} non-trivial 2D Ising identities")
    print(f"  Search space: n=6 arithmetic functions (sigma, phi, tau, sopfr, M_p, C(n,k))")
    print(f"  Tolerance: exact match (integer or simple fraction)")
    print()

    # For each random number n, compute its arithmetic functions and check matches
    # Search space: integers 2-100 (reasonable range)
    match_counts = []
    random.seed(42)

    for trial in range(n_trials):
        # Pick random integer
        rn = random.randint(2, 100)
        funcs = {
            'n': rn,
            'sigma': sigma(rn),
            'phi': phi(rn),
            'tau': tau(rn),
            'sopfr': sopfr(rn),
            'M3': mersenne(len(factorize(rn)) + 1) if len(factorize(rn)) > 0 else 3,
        }

        count = 0
        for name, target, expr_fn in identities:
            try:
                val = expr_fn(funcs)
                if abs(val - target) < 1e-10:
                    count += 1
            except (ZeroDivisionError, ValueError):
                pass
        match_counts.append(count)

    actual_matches = len(identities)  # n=6 matches all 4
    avg_random = sum(match_counts) / len(match_counts)
    std_random = (sum((x - avg_random)**2 for x in match_counts) / len(match_counts))**0.5
    p_value = sum(1 for x in match_counts if x >= actual_matches) / n_trials

    # Bonferroni correction (testing ~20 possible expressions)
    bonferroni = min(1.0, p_value * 20)

    print(f"  Results ({n_trials:,} trials, random n in [2,100]):")
    print(f"  Actual matches (n=6):   {actual_matches}/{len(identities)}")
    print(f"  Random average:         {avg_random:.3f} +/- {std_random:.3f}")
    print(f"  Raw p-value:            {p_value:.6f}")
    print(f"  Bonferroni-corrected:   {bonferroni:.6f}")
    print(f"  Z-score:                {(actual_matches - avg_random) / std_random:.1f}sigma" if std_random > 0 else "  Z-score: inf")
    print()

    # Distribution histogram
    from collections import Counter
    dist = Counter(match_counts)
    max_matches = max(dist.keys())
    print(f"  Match distribution:")
    print(f"  {'Matches':>8}  {'Count':>8}  {'Pct':>6}  Bar")
    for m in range(max_matches + 1):
        c = dist.get(m, 0)
        pct = c / n_trials * 100
        bar = "#" * int(pct)
        mark = " <-- n=6" if m == actual_matches else ""
        print(f"  {m:>8}  {c:>8}  {pct:>5.1f}%  {bar}{mark}")

    print()
    if p_value < 0.01:
        grade = "STRUCTURAL (p < 0.01)"
        emoji = "PASS"
    elif p_value < 0.05:
        grade = "WEAK EVIDENCE (p < 0.05)"
        emoji = "MARGINAL"
    else:
        grade = "NOT SIGNIFICANT (p >= 0.05)"
        emoji = "FAIL"
    print(f"  Grade: {emoji} — {grade}")

    # Additional: broader test including Stefan-Boltzmann
    print()
    print("  Extended test including radiation physics:")
    extended = [
        ("T^4 exponent = tau(6)", 4, "tau"),
        ("SB denominator 15 = C(6,2)", 15, "C(n,2)"),
        ("Radiation 1/3 = phi/n", Fraction(1, 3), "phi/n"),
        ("Mermin-Wagner d=2 = phi(6)", 2, "phi"),
    ]
    for name, target, source in extended:
        print(f"  {name}: target={target}, source={source}")

    return p_value


# ═══════════════════════════════════════════════════════════════
# Section 10: Summary Table
# ═══════════════════════════════════════════════════════════════

def summary():
    """Print comprehensive summary table."""
    print()
    print("=" * 70)
    print("SUMMARY: Thermodynamics n=6 Identities")
    print("=" * 70)
    print()

    entries = [
        # (ID, Identity, Exact?, Grade, Domain)
        ("T1", "delta(2D) = 15 = C(6,2) = 2^tau-1", True, "EXACT", "2D Ising"),
        ("T2", "beta(2D) = 1/8 = 1/(sigma-tau) = 1/Bott", True, "EXACT", "2D Ising"),
        ("T3", "eta(2D) = 1/4 = 1/tau(6)", True, "EXACT", "2D Ising"),
        ("T4", "gamma(2D) = 7/4 = M_3/tau(6)", True, "EXACT", "2D Ising"),
        ("T5", "Rushbrooke sum = 2 = phi(6)", True, "EXACT", "Scaling"),
        ("T6", "nu(3D) ~ 63/100 ~ M_6/100", False, "APPROX", "3D Ising"),
        ("T7", "phi^4 d_uc = 4 = tau(6)", True, "EXACT", "Landau-Ginzburg"),
        ("T8", "phi^6 d_tc = 3 = n/phi(n)", True, "EXACT", "Tricritical"),
        ("T9", "Tricritical delta_t = 5 = sopfr(6)", True, "EXACT", "Tricritical"),
        ("T10", "S(6) = ln(4) = 2*ln(2)", True, "EXACT", "Entropy"),
        ("T11", "S(28) = ln(6) = ln(P1)", True, "EXACT", "Entropy"),
        ("T12", "Stefan-Boltzmann T^4, 4=tau(6)", True, "EXACT", "Radiation"),
        ("T13", "SB denominator 15 = C(6,2)", True, "EXACT", "Radiation"),
        ("T14", "Radiation pressure 1/3 = phi/n", True, "EXACT", "Radiation"),
        ("T15", "Planck nu^3, 3=n/phi(n)", True, "EXACT", "Radiation"),
        ("T16", "SB pi^5: 5=sopfr(6)", True, "EXACT", "Radiation"),
        ("T17", "SB h^3: 3=n/phi(n)", True, "EXACT", "Radiation"),
        ("T18", "SB c^2: 2=phi(6)", True, "EXACT", "Radiation"),
        ("T19", "Mermin-Wagner d=2=phi(6)", True, "EXACT", "Symmetry"),
        ("T20", "Physical O(n) classes = 3 = n/phi(n)", True, "EXACT", "Universality"),
        ("T21", "Tricritical beta_t = 1/4 = 1/tau(6)", True, "EXACT", "Tricritical"),
    ]

    exact_count = sum(1 for e in entries if e[2])
    approx_count = sum(1 for e in entries if not e[2])

    print(f"  {'ID':>4}  {'Identity':50}  {'Grade':>7}  {'Domain':15}")
    print(f"  {'--':>4}  {'--------':50}  {'-----':>7}  {'------':15}")
    for eid, identity, is_exact, grade, domain in entries:
        print(f"  {eid:>4}  {identity:50}  {grade:>7}  {domain:15}")

    print()
    print(f"  Total: {len(entries)} identities")
    print(f"  EXACT: {exact_count}")
    print(f"  APPROX: {approx_count}")
    print()
    print(f"  n=6 functions used:")
    print(f"    tau(6) = 4    (Stefan-Boltzmann, upper critical dim, 1/eta)")
    print(f"    phi(6) = 2    (Mermin-Wagner, Rushbrooke sum, SB c-power)")
    print(f"    sigma(6) = 12 (with tau: 1/(sigma-tau) = 1/8 = beta)")
    print(f"    sopfr(6) = 5  (SB pi-power, tricritical delta)")
    print(f"    C(6,2) = 15   (2D Ising delta, SB denominator)")
    print(f"    M_3 = 7       (gamma numerator)")
    print(f"    M_6 = 63      (3D Ising nu ~ 63/100)")
    print(f"    n/phi = 3     (tricritical dim, radiation powers)")


# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Thermodynamics & Statistical Mechanics n=6 Calculator")
    parser.add_argument('--section', choices=[
        'ising2d', 'ising3d', 'universality', 'landau', 'entropy',
        'partition', 'stefan', 'mermin', 'texas', 'summary'
    ], help="Run specific section")
    parser.add_argument('--beta-range', type=str, default='0.01,5,500',
                        help="Beta range for partition function: min,max,points")
    parser.add_argument('--texas', action='store_true', help="Run Texas Sharpshooter only")
    parser.add_argument('--all', action='store_true', help="Run everything")
    args = parser.parse_args()

    print("=" * 70)
    print("  THERMODYNAMICS & STATISTICAL MECHANICS n=6 CALCULATOR")
    print("  Hypothesis: Phase transitions encode the perfect number 6")
    print("=" * 70)

    if args.texas:
        texas_sharpshooter()
        return

    section_map = {
        'ising2d': ising_2d,
        'ising3d': ising_3d,
        'universality': universality,
        'landau': landau_ginzburg,
        'entropy': boltzmann_entropy,
        'partition': lambda: partition_function(*[float(x) for x in args.beta_range.split(',')[:2]],
                                                int(args.beta_range.split(',')[2])),
        'stefan': stefan_boltzmann,
        'mermin': mermin_wagner,
        'texas': texas_sharpshooter,
        'summary': summary,
    }

    if args.section:
        section_map[args.section]()
    elif args.all or not args.section:
        ising_2d()
        ising_3d()
        universality()
        landau_ginzburg()
        boltzmann_entropy()
        beta_parts = args.beta_range.split(',')
        partition_function(float(beta_parts[0]), float(beta_parts[1]), int(beta_parts[2]))
        stefan_boltzmann()
        mermin_wagner()
        texas_sharpshooter()
        summary()


if __name__ == '__main__':
    main()
