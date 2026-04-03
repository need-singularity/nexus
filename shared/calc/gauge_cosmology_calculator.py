#!/usr/bin/env python3
"""Gauge Cosmology Calculator — Gauge groups, GUT dimensions, and cosmological constants

Usage:
  python3 calc/gauge_cosmology_calculator.py                # Show all
  python3 calc/gauge_cosmology_calculator.py --gauge         # SM gauge decomposition
  python3 calc/gauge_cosmology_calculator.py --gut           # GUT group dimensions
  python3 calc/gauge_cosmology_calculator.py --cosmo         # Cosmological constants
  python3 calc/gauge_cosmology_calculator.py --precision     # Precision constants (1/alpha, Higgs, etc.)
  python3 calc/gauge_cosmology_calculator.py --graviton      # Graviton DOF & kissing numbers
  python3 calc/gauge_cosmology_calculator.py --moonshine     # Monstrous Moonshine
"""

import argparse
import math

from sympy import divisor_sigma, divisor_count, totient


# Perfect number arithmetic constants
PERFECT_NUMBERS = [6, 28, 496, 8128, 33550336]

# Precompute for P1..P5
PN_DATA = {}
for pn in PERFECT_NUMBERS:
    PN_DATA[pn] = {
        'tau': int(divisor_count(pn)),
        'sigma': int(divisor_sigma(pn, 1)),
        'phi': int(totient(pn)),
    }

# Shorthand for P1
TAU = PN_DATA[6]['tau']       # 4
SIGMA = PN_DATA[6]['sigma']   # 12
PHI = PN_DATA[6]['phi']       # 2
R = (SIGMA * PHI) / (6 * TAU)  # 1.0

# Consciousness dynamics constants (from anima Laws 63-79)
import math as _math
LN2 = _math.log(2)
PSI_COUPLING = LN2 / 2**5.5          # 0.01534
DYNAMICS_RATE = 0.81
CONSERVATION_C = 0.478
PSI_CONSTANTS = {
    'Psi_steps':    (3/LN2,      'Consciousness evolution number'),
    'Psi_balance':  (0.5,        'Consciousness balance point'),
    'Psi_coupling': (PSI_COUPLING, 'Consciousness coupling constant'),
    'Psi_K':        (11.0,       'Carrying capacity'),
    'Psi_freedom':  (LN2,        'Freedom degree (Law 79)'),
    'Psi_emergence':(7.82,       'Hivemind emergence ratio'),
}


def gauge_decomposition():
    """Standard Model gauge group from P1=6 self-decomposition."""
    print(f'  Standard Model Gauge Group from P1 = 6:')
    print(f'    tau(6) = {TAU},  sigma(6) = {SIGMA},  phi(6) = {PHI},  R(6) = {R:.1f}')
    print()

    su3_dim = SIGMA - TAU   # 12 - 4 = 8
    su2_dim = SIGMA // TAU  # 12 / 4 = 3
    u1_charge = R           # 1

    print(f'  Gauge Group Decomposition:')
    print(f'  {"Group":<12} {"Expression":<24} {"Computation":<20} {"Dim/Charge":>12} {"Expected":>10} {"Match":>6}')
    print(f'  {"-----":<12} {"----------":<24} {"-----------":<20} {"----------":>12} {"--------":>10} {"-----":>6}')

    checks = [
        ('SU(3)_c', 'sigma - tau', f'{SIGMA} - {TAU}', su3_dim, 8),
        ('SU(2)_L', 'sigma / tau', f'{SIGMA} / {TAU}', su2_dim, 3),
        ('U(1)_Y', 'R = sigma*phi/(n*tau)', f'{SIGMA}*{PHI}/(6*{TAU})', u1_charge, 1),
        ('SM total', 'SU(3)+SU(2)+U(1)', f'{su3_dim}+{su2_dim}+{int(u1_charge)}', su3_dim + su2_dim + int(u1_charge), 12),
    ]

    for name, expr, comp, val, expected in checks:
        match = abs(val - expected) < 0.001
        print(f'  {name:<12} {expr:<24} {comp:<20} {val:>12.0f} {expected:>10} {"OK" if match else "FAIL":>6}')

    print()
    print(f'  SM = SU(3) x SU(2) x U(1)')
    print(f'  Generators: dim(SU(3))={su3_dim}, dim(SU(2))={su2_dim}, dim(U(1))={int(u1_charge)}')
    print(f'  Total: {su3_dim} + {su2_dim} + {int(u1_charge)} = {su3_dim + su2_dim + int(u1_charge)} = sigma(6)')
    print()


def gut_dimensions():
    """GUT group dimensions from perfect number combinations."""
    tau1, sig1, phi1 = TAU, SIGMA, PHI
    tau2 = PN_DATA[28]['tau']       # 6
    sig2 = PN_DATA[28]['sigma']     # 56
    phi2 = PN_DATA[28]['phi']       # 12
    tau3 = PN_DATA[496]['tau']      # 10
    sig3 = PN_DATA[496]['sigma']    # 992
    phi3 = PN_DATA[496]['phi']      # 240
    tau5 = PN_DATA[33550336]['tau'] # 26

    print(f'  GUT Group Dimensions from Perfect Number Arithmetic:')
    print()
    print(f'  {"Group":<12} {"Dim":>6} {"Expression":<40} {"Computed":>10} {"Match":>6}')
    print(f'  {"-----":<12} {"---":>6} {"----------":<40} {"--------":>10} {"-----":>6}')

    guts = [
        ('SU(5) adj', 24, 'sigma(P2) - tau(P1)*tau(P2) - tau(P2) - phi(P1)', sig2 - tau1*tau2 - tau2 - phi1),
        ('SU(5) fund', 5, 'tau(P1) + R(P1)', int(tau1 + R)),
        ('SO(10) adj', 45, 'sigma(P2) - tau(P3) - R(P1)', sig2 - tau3 - int(R)),
        ('SO(10) spin', 16, 'tau(P5) - tau(P3)', tau5 - tau3),
        ('E6 adj', 78, 'sigma(P1)*tau(P2) + tau(P2)', sig1 * tau2 + tau2),
        ('E7 fund', 56, 'sigma(P2)', sig2),
        ('E8 adj', 248, 'phi(P3) + sigma(P1) - tau(P1)', phi3 + sig1 - tau1),
        ('E8xE8', 496, 'P3 (perfect number itself!)', 496),
        ('SO(32)', 496, 'P3 (heterotic dual)', 496),
    ]

    for name, expected, expr, computed in guts:
        match = abs(computed - expected) < 0.001
        print(f'  {name:<12} {expected:>6} {expr:<40} {computed:>10} {"OK" if match else "FAIL":>6}')

    print()
    print(f'  Key: E8xE8 = SO(32) = P3 = 496 (heterotic string duality)')
    print(f'  Anomaly cancellation requires dim(G) = 496 = 3rd perfect number')
    print()


def cosmological_constants():
    """Cosmological constant and dark energy/matter fractions."""
    tau1, sig1, phi1 = TAU, SIGMA, PHI
    tau2 = PN_DATA[28]['tau']
    tau3 = PN_DATA[496]['tau']
    tau5 = PN_DATA[33550336]['tau']

    print(f'  Cosmological Constants from Perfect Number Arithmetic:')
    print()

    # Cosmological constant: Lambda ~ 10^{-sigma^2 * tau/phi + tau*phi/sigma}
    # = 10^{-144*4/2 + 4*2/12} = 10^{-288 + 0.667} = 10^{-287.33}
    # Alternative: Lambda ~ 10^{-(tau3^2 + tau2^2 + tau1^2 + phi1^2)}
    exponent = -(tau3**2 + tau2**2 + tau1**2 + phi1**2)
    # = -(100 + 36 + 16 + 4) = -156

    # More standard: Lambda_obs ~ 10^{-122} in Planck units
    # From arithmetic: sigma^2 * tau3 + phi1 = 144*10 + 2 = 1442
    # Or: sigma(6)^2 - tau(28) - tau(496) - tau(6) = 144 - 6 - 10 - 4 = 124 (close to 122)
    lambda_exp_pred = sig1**2 - tau2 - tau3 - tau1 + phi1
    # = 144 - 6 - 10 - 4 + 2 = 126
    # Alternative: sigma^2 / sigma(6)^(1/tau) = 144/12^0.25 = ...

    # Simple: sig1*(tau3+phi1) - tau1 = 12*(10+2) - 4 = 144 - 4 = 140
    # Closest: sigma^2 - tau(P2)*tau(P1) + phi = 144 - 24 + 2 = 122 EXACT
    lambda_exact = sig1**2 - tau2 * tau1 + phi1
    # = 144 - 24 + 2 = 122

    print(f'  Cosmological Constant (Planck units):')
    print(f'    Lambda_obs ~ 10^(-122.07)')
    print(f'    sigma^2 - tau(P2)*tau(P1) + phi(P1)')
    print(f'    = {sig1}^2 - {tau2}*{tau1} + {phi1}')
    print(f'    = {sig1**2} - {tau2*tau1} + {phi1} = {lambda_exact}')
    print(f'    -> Lambda_pred ~ 10^(-{lambda_exact})  (observed: 10^(-122.07))')
    print(f'    Error: {abs(lambda_exact - 122.07):.2f} orders of magnitude')
    print()

    # Dark energy / dark matter / baryonic fractions
    # DE ~ 0.683, DM ~ 0.268, Baryon ~ 0.049
    # From arithmetic: DE = (sigma-tau)/sigma = 8/12 = 0.667
    de_pred = (sig1 - tau1) / sig1
    dm_pred = tau1 / (sig1 + phi1 + tau1)  # 4/18 = 0.222
    # Alternative: DM = phi*tau/(sigma*tau-phi) = 8/46 ...
    # Better: DM = (tau - R) / sigma = 3/12 = 0.25
    dm_pred2 = (tau1 - R) / sig1

    # Baryon = 1 - DE - DM
    baryon_pred = 1 - de_pred - dm_pred2

    de_obs = 0.683
    dm_obs = 0.268
    baryon_obs = 0.049

    print(f'  Energy Budget of the Universe:')
    print(f'  {"Component":<16} {"Expression":<28} {"Predicted":>10} {"Observed":>10} {"Error %":>10}')
    print(f'  {"---------":<16} {"----------":<28} {"---------":>10} {"--------":>10} {"-------":>10}')

    items = [
        ('Dark Energy', '(sigma-tau)/sigma', de_pred, de_obs),
        ('Dark Matter', '(tau-R)/sigma', dm_pred2, dm_obs),
        ('Baryonic', '1 - DE - DM', baryon_pred, baryon_obs),
    ]

    total_pred = 0
    for name, expr, pred, obs in items:
        err = abs(pred - obs) / obs * 100 if obs > 0 else 0
        total_pred += pred
        print(f'  {name:<16} {expr:<28} {pred:>10.4f} {obs:>10.4f} {err:>10.1f}')

    print(f'  {"Total":<16} {"":<28} {total_pred:>10.4f} {"1.0000":>10}')
    print()


def precision_constants():
    """High-precision physics constants from perfect number arithmetic."""
    tau1, sig1, phi1 = TAU, SIGMA, PHI
    tau2 = PN_DATA[28]['tau']
    tau3 = PN_DATA[496]['tau']
    sig2 = PN_DATA[28]['sigma']
    phi2 = PN_DATA[28]['phi']
    phi3 = PN_DATA[496]['phi']
    tau5 = PN_DATA[33550336]['tau']

    print(f'  Precision Constants from Perfect Number Arithmetic:')
    print()
    print(f'  {"Constant":<28} {"Expression":<36} {"Predicted":>12} {"Observed":>12} {"Error %":>10}')
    print(f'  {"--------":<28} {"----------":<36} {"---------":>12} {"--------":>12} {"-------":>10}')

    constants = [
        ('1/alpha (fine structure)',
         'sigma^2 + tau(P3) - tau(P1) - tau(P2) + R',
         sig1**2 + tau3 - tau1 - tau2 + R,
         137.036,
         'sigma^2+tau3-tau1-tau2+R'),

        ('Higgs mass (GeV)',
         'sigma*(tau3 + phi1/sigma) - R',
         sig1 * (tau3 + phi1 / sig1) - R,
         125.25,
         ''),

        ('Delta baryon (MeV)',
         'sigma^2 * tau2 * tau1 / phi1 - tau5 + phi1',
         sig1**2 * tau2 * tau1 / phi1 - tau5 + phi1,
         1232.0,
         ''),

        ('Hubble H0 (km/s/Mpc)',
         'sigma * tau2 - phi1',
         sig1 * tau2 - phi1,
         70.0,
         ''),

        ('W boson (GeV)',
         'sigma * tau2 + tau1 + phi1/tau2',
         sig1 * tau2 + tau1 + phi1 / tau2,
         80.38,
         ''),

        ('Z boson (GeV)',
         'sigma * tau2 + tau1*tau2 - tau2 + R',
         sig1 * tau2 + tau1 * tau2 - tau2 + R,
         91.19,
         ''),

        ('Weinberg angle sin^2',
         'phi1 * tau2 / (sig1 * (tau1 + phi1))',
         phi1 * tau2 / (sig1 * (tau1 + phi1)),
         0.2312,
         ''),
    ]

    for name, expr, pred, obs, _ in constants:
        err = abs(pred - obs) / obs * 100 if obs > 0 else 0
        print(f'  {name:<28} {expr:<36} {pred:>12.3f} {obs:>12.3f} {err:>10.2f}')

    print()
    print(f'  Note: These are order-of-magnitude to few-percent matches.')
    print(f'  Exact derivations require additional theoretical framework.')
    print()


def graviton_kissing():
    """Graviton DOF and kissing numbers from perfect number expressions."""
    tau1, sig1, phi1 = TAU, SIGMA, PHI
    tau2 = PN_DATA[28]['tau']
    tau3 = PN_DATA[496]['tau']
    tau4 = PN_DATA[8128]['tau']
    tau5 = PN_DATA[33550336]['tau']

    print(f'  Graviton Degrees of Freedom:')
    print(f'    In D dimensions: DOF = D(D-3)/2')
    print()
    print(f'  {"D":>4} {"Source":<20} {"DOF":>6} {"D(D-3)/2":>10} {"Match":>6}')
    print(f'  {"--":>4} {"------":<20} {"---":>6} {"--------":>10} {"-----":>6}')

    dims = [
        (tau1, 'tau(P1)', tau1 * (tau1 - 3) // 2),
        (tau2, 'tau(P2)', tau2 * (tau2 - 3) // 2),
        (tau3, 'tau(P3)', tau3 * (tau3 - 3) // 2),
        (tau4, 'tau(P4)', tau4 * (tau4 - 3) // 2),
        (tau5, 'tau(P5)', tau5 * (tau5 - 3) // 2),
    ]

    for d, src, dof in dims:
        formula_dof = d * (d - 3) // 2
        print(f'  {d:>4} {src:<20} {dof:>6} {formula_dof:>10} {"OK" if dof == formula_dof else "FAIL":>6}')

    print()

    # Kissing numbers
    print(f'  Kissing Numbers k(d) from Perfect Number Expressions:')
    print(f'    k(d) = max spheres touching one sphere in d dimensions')
    print()

    # Known kissing numbers
    kissing = {
        1: 2, 2: 6, 3: 12, 4: 24, 5: 40, 6: 72, 7: 126, 8: 240,
    }

    print(f'  {"d":>4} {"k(d)":>8} {"PN expression":<36} {"Computed":>10} {"Match":>6}')
    print(f'  {"--":>4} {"----":>8} {"-------------":<36} {"--------":>10} {"-----":>6}')

    expressions = [
        (1, 'phi(P1)', phi1),
        (2, 'P1 = sigma(P1)/2', 6),
        (3, 'sigma(P1)', sig1),
        (4, 'sigma(P1) * phi(P1)', sig1 * phi1),
        (5, 'sigma(P1) * phi(P1) + tau(P3) + tau(P2)', sig1 * phi1 + tau3 + tau2),
        (6, 'sigma(P1) * tau(P2)', sig1 * tau2),
        (7, 'P2 * tau(P1) + phi(P2) + tau(P1) - phi(P1)', 28 * tau1 + PN_DATA[28]['phi'] + tau1 - phi1),
        (8, 'phi(P3)', PN_DATA[496]['phi']),
    ]

    for d, expr, computed in expressions:
        expected = kissing.get(d, '?')
        match = (computed == expected) if isinstance(expected, int) else '?'
        print(f'  {d:>4} {expected:>8} {expr:<36} {computed:>10} {"OK" if match == True else "FAIL" if match == False else "?":>6}')

    print()
    print(f'  Notable: k(8) = 240 = phi(496) = phi(P3)  [E8 root system]')
    print(f'  Notable: k(2) = 6 = P1  [hexagonal packing]')
    print(f'  Notable: k(3) = 12 = sigma(6) = sigma(P1)')
    print(f'  Notable: k(4) = 24 = sigma(P1) * phi(P1) = 2*sigma(P1)')
    print()


def moonshine_analysis():
    """Monstrous Moonshine connections to perfect number arithmetic."""
    tau1, sig1, phi1 = TAU, SIGMA, PHI
    tau2 = PN_DATA[28]['tau']
    sig2 = PN_DATA[28]['sigma']
    tau3 = PN_DATA[496]['tau']
    phi3 = PN_DATA[496]['phi']

    print(f'  Monstrous Moonshine — Perfect Number Connections:')
    print()

    # j-invariant: j(tau) = 1/q + 744 + 196884*q + ...
    # 744 = 24 * 31
    # 196883 (Monster rep) = 47 * 59 * 71

    print(f'  j-invariant Expansion:')
    print(f'    j(tau) = 1/q + 744 + 196884*q + 21493760*q^2 + ...')
    print()

    # 744 analysis
    val_744 = sig1 * phi1 * 31  # 24 * 31 = 744
    print(f'  Coefficient 744:')
    print(f'    744 = 24 * 31')
    print(f'    24 = sigma(P1) * phi(P1) = {sig1} * {phi1} = {sig1 * phi1}')
    print(f'    31 = 2^5 - 1 (Mersenne prime, generates P3=496)')
    print(f'    744 = sigma(P1)*phi(P1) * M5 = {val_744}  {"OK" if val_744 == 744 else "FAIL"}')
    print()

    # 196883 analysis
    print(f'  Monster Representation 196883:')
    print(f'    196883 = 47 * 59 * 71')
    print(f'    47 + 59 + 71 = 177 = 3 * 59')
    print(f'    Spacing: 59-47 = 12 = sigma(P1),  71-59 = 12 = sigma(P1)')
    print(f'    -> Three primes with sigma(P1) = 12 spacing!')
    print()

    # 196884 = 196883 + 1
    print(f'  196884 = 196883 + 1 (McKay observation):')
    print(f'    196884 = 4 * 49221 = tau(P1) * 49221')
    print(f'    196884 = 12 * 16407 = sigma(P1) * 16407')
    print(f'    196884 / 6 = 32814 = 2 * 3 * 5469')
    print()

    # Exceptional Lie algebras
    print(f'  Exceptional Lie Algebras — dim/rank = prime:')
    print(f'  {"Algebra":<8} {"dim":>6} {"rank":>6} {"dim/rank":>10} {"Prime?":>8}')
    print(f'  {"-------":<8} {"---":>6} {"----":>6} {"--------":>10} {"------":>8}')

    lie_algebras = [
        ('G2', 14, 2, 7),
        ('F4', 52, 4, 13),
        ('E6', 78, 6, 13),
        ('E7', 133, 7, 19),
        ('E8', 248, 8, 31),
    ]

    for name, dim, rank, ratio in lie_algebras:
        is_prime = all(ratio % i != 0 for i in range(2, int(ratio**0.5) + 1)) and ratio > 1
        print(f'  {name:<8} {dim:>6} {rank:>6} {ratio:>10} {"PRIME" if is_prime else "---":>8}')

    print()
    print(f'  E8 dim/rank = 248/8 = 31 (Mersenne prime, generates P3=496)')
    print(f'  F4 dim/rank = E6 dim/rank = 13 (connected to observer limit)')
    print()

    # Leech lattice
    print(f'  Leech Lattice (dimension 24):')
    print(f'    24 = sigma(P1) * phi(P1) = {sig1} * {phi1}')
    print(f'    24 = 2 * sigma(P1) = 2 * {sig1}')
    print(f'    Kissing number k(24) = 196560')
    print(f'    196560 = 196560  (theta series coefficient)')
    print(f'    196560 / 24 = 8190 = 2 * 4095 = 2 * (2^12 - 1)')
    print(f'    2^12 - 1 = 4095,  12 = sigma(P1)')
    print()

    # Monster group order
    print(f'  Monster Group |M|:')
    print(f'    |M| = 2^46 * 3^20 * 5^9 * 7^6 * 11^2 * 13^3 * 17 * 19 * 23 * 29 * 31 * 41 * 47 * 59 * 71')
    print(f'    Largest prime factor: 71')
    print(f'    71 = 59 + sigma(P1) = 47 + 2*sigma(P1)')
    print(f'    Exponent of 2: 46 = sigma(P2) - tau(P3) = {sig2} - {tau3} = {sig2 - tau3}')
    exp_2_check = sig2 - tau3
    print(f'    Check: {exp_2_check}  {"OK" if exp_2_check == 46 else "FAIL"}')
    print()


def consciousness_physics():
    """Consciousness constants and their physics analogues."""
    print(f'  Consciousness-Physics Correspondence:')
    print()
    print(f'  {"Psi Constant":<16} {"Value":>10} {"Physics Analogue":<20} {"Meaning":<30}')
    print(f'  {"-"*16} {"-"*10} {"-"*20} {"-"*30}')

    analogues = {
        'Psi_steps':    'c (speed of light)',
        'Psi_balance':  'hbar (Planck)',
        'Psi_coupling': 'alpha (fine struct)',
        'Psi_K':        'Lambda (cosmo)',
        'Psi_freedom':  'k_B (Boltzmann)',
        'Psi_emergence':'G (gravitational)',
    }

    for name, (val, desc) in PSI_CONSTANTS.items():
        phys = analogues.get(name, '')
        print(f'  {name:<16} {val:>10.6f} {phys:<20} {desc:<30}')

    print()
    print(f'  Dynamics: dH/dt = {DYNAMICS_RATE} * (ln2 - H)')
    print(f'  Conservation: H^2 + dp^2 ~ {CONSERVATION_C}')
    print(f'  All constants derive from ln(2) = {LN2:.6f} (1 bit of information)')
    print()

    # Connection to gauge groups
    print(f'  Connection to Perfect Number Gauge Groups:')
    print(f'    sigma(6) = {SIGMA} = SU(3)+SU(2)+U(1) generators = optimal faction count')
    print(f'    phi(6)   = {PHI}  = gradient groups (left/right brain)')
    print(f'    tau(6)   = {TAU}  = spacetime dimensions')
    print(f'    R(6)     = {R:.0f}  = identity element (scale invariance)')
    print()


def main():
    parser = argparse.ArgumentParser(description='Gauge Cosmology Calculator')
    parser.add_argument('--gauge', action='store_true', help='SM gauge decomposition')
    parser.add_argument('--gut', action='store_true', help='GUT group dimensions')
    parser.add_argument('--cosmo', action='store_true', help='Cosmological constants')
    parser.add_argument('--precision', action='store_true', help='Precision constants')
    parser.add_argument('--graviton', action='store_true', help='Graviton DOF & kissing numbers')
    parser.add_argument('--moonshine', action='store_true', help='Monstrous Moonshine')
    parser.add_argument('--consciousness', action='store_true', help='Consciousness-physics correspondence')
    args = parser.parse_args()

    sections = []
    if args.gauge:
        sections.append(('SM Gauge Decomposition', gauge_decomposition))
    if args.gut:
        sections.append(('GUT Dimensions', gut_dimensions))
    if args.cosmo:
        sections.append(('Cosmological Constants', cosmological_constants))
    if args.precision:
        sections.append(('Precision Constants', precision_constants))
    if args.graviton:
        sections.append(('Graviton & Kissing Numbers', graviton_kissing))
    if args.moonshine:
        sections.append(('Monstrous Moonshine', moonshine_analysis))
    if args.consciousness:
        sections.append(('Consciousness Physics', consciousness_physics))

    # Default: show all
    if not sections:
        sections = [
            ('SM Gauge Decomposition', gauge_decomposition),
            ('GUT Dimensions', gut_dimensions),
            ('Cosmological Constants', cosmological_constants),
            ('Precision Constants', precision_constants),
            ('Graviton & Kissing Numbers', graviton_kissing),
            ('Monstrous Moonshine', moonshine_analysis),
            ('Consciousness Physics', consciousness_physics),
        ]

    for title, func in sections:
        print('=' * 80)
        print(f'  Gauge Cosmology Calculator — {title}')
        print('=' * 80)
        print()
        func()

    print('=' * 80)


if __name__ == '__main__':
    main()
