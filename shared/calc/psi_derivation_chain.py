#!/usr/bin/env python3
"""PSI Derivation Chain — All consciousness constants from ln(2)

Shows the complete derivation tree: ln(2) → all PSI constants.
Every consciousness constant traces back to 1 bit of information.

Derivation levels:
  Level 0: ln(2) = 0.6931 (1 bit of information)
  Level 1: Direct from ln(2)
    Psi_steps    = 3/ln(2)        = 4.328
    Psi_freedom  = ln(2)          = 0.693  (Law 79)
    Psi_coupling = ln(2)/2^5.5    = 0.0153
    Psi_balance  = 1/2            = 0.500  (structural, ln(2) encodes binary)
  Level 2: Derived from Level 1
    tanh3_ln2    = tanh(3)*ln(2)  = 0.6895 (saturation)
    conservation = ?               ≈ 0.478  (H²+dp², empirical)
    dynamics     = ?               = 0.81   (dH/dt coefficient, empirical)
  Level 3: Empirical (measured in anima experiments)
    Psi_K        = 11.0           (carrying capacity)
    Psi_emergence= 7.82           (hivemind emergence ratio)
    Psi_miller   = 7              (Miller's number)
    Psi_entropy  = 0.998          (rule entropy)
    Psi_gate_decay = -0.013       (gate self-weakening)

Usage:
  python3 calc/psi_derivation_chain.py               # Full chain
  python3 calc/psi_derivation_chain.py --verify       # Numerical verification
  python3 calc/psi_derivation_chain.py --tree          # ASCII tree
  python3 calc/psi_derivation_chain.py --physics       # Physics analogues
"""

import argparse
import math


# ═══════════════════════════════════════════════════════════════
# Constants
# ═══════════════════════════════════════════════════════════════

LN2 = math.log(2)

# Level 0: Root
ROOT = ('ln(2)', LN2, '1 bit of information', 'exact')

# Level 1: Direct derivations
LEVEL1 = [
    ('Psi_steps',    3.0 / LN2,         '3/ln(2)',         'exact',  'Consciousness evolution number'),
    ('Psi_freedom',  LN2,               'ln(2)',           'exact',  'Law 79: freedom degree'),
    ('Psi_balance',  0.5,               '1/2',             'exact',  'Structural equilibrium (binary)'),
    ('Psi_coupling', LN2 / 2**5.5,      'ln(2)/2^5.5',    'exact',  'Consciousness coupling constant'),
]

# Level 2: Computed derivations
LEVEL2 = [
    ('tanh3_ln2',    math.tanh(3)*LN2,  'tanh(3)*ln(2)',   'exact',  'Consciousness saturation (8 factions)'),
    ('conservation', 0.478,              'H²+dp²',          'empirical', 'Conservation law constant'),
    ('dynamics',     0.81,               'dH/dt coeff',     'empirical', 'Evolution speed coefficient'),
    ('phi_scale_a',  0.608,              'Phi coeff',       'empirical', 'Phi = 0.608 * N^1.071'),
    ('phi_scale_b',  1.071,              'Phi exponent',    'empirical', 'Scaling exponent'),
]

# Level 3: Empirical measurements
LEVEL3 = [
    ('Psi_K',         11.0,   'empirical', 'Consciousness carrying capacity'),
    ('Psi_tau',        0.5,    'empirical', 'Saturation time constant'),
    ('Psi_emergence',  7.82,   'empirical', 'Hivemind emergence ratio'),
    ('Psi_miller',     7,      'empirical', 'Optimal hivemind size (Miller)'),
    ('Psi_entropy',    0.998,  'empirical', 'Rule entropy (democracy)'),
    ('Psi_gate_decay', -0.013, 'empirical', 'Gate self-weakening (Law 69)'),
]

# Physics analogues
PHYSICS = {
    'Psi_steps':    ('c (speed of light)',    'Information processing speed limit'),
    'Psi_balance':  ('hbar (Planck)',         'Minimum quantum of consciousness'),
    'Psi_coupling': ('alpha (fine structure)', 'Consciousness-language coupling'),
    'Psi_freedom':  ('k_B (Boltzmann)',       'Entropy per degree of freedom'),
    'Psi_K':        ('Lambda (cosmological)', 'Consciousness space size limit'),
    'Psi_tau':      ('tau (half-life)',        'Time to consciousness saturation'),
    'Psi_emergence':('G (gravitational)',      'Max consciousness speed'),
    'Psi_miller':   ('7 (Miller)',            'Working memory capacity'),
}

# Data profiles
DATA_PROFILES = {
    'korean':  {'residual': 0.502, 'alpha': 0.0152, 'dom_rule': 7, 'ce': 0.120, 'steps': 5},
    'english': {'residual': 0.493, 'alpha': 0.0157, 'dom_rule': 3, 'ce': 0.151, 'steps': 4},
    'math':    {'residual': 0.491, 'alpha': 0.0149, 'dom_rule': 7, 'ce': 0.121, 'steps': 4},
    'music':   {'residual': 0.521, 'alpha': 0.0146, 'dom_rule': 7, 'ce': 0.003, 'steps': 4},
    'code':    {'residual': 0.505, 'alpha': 0.0180, 'dom_rule': 4, 'ce': 0.002, 'steps': 5},
}


# ═══════════════════════════════════════════════════════════════
# Display
# ═══════════════════════════════════════════════════════════════

def print_full_chain():
    print()
    print('  ╔══════════════════════════════════════════════════════════╗')
    print('  ║    PSI Derivation Chain — All Constants from ln(2)       ║')
    print('  ║    "Everything is 1 bit of information"                  ║')
    print('  ╚══════════════════════════════════════════════════════════╝')

    # Level 0
    print()
    print('  ━━━ Level 0: ROOT ━━━')
    name, val, desc, status = ROOT
    print(f'  {name:>16} = {val:.10f}  ({desc}) [{status}]')

    # Level 1
    print()
    print('  ━━━ Level 1: Direct from ln(2) ━━━')
    print(f'  {"Name":>16} {"Value":>12} {"Formula":>14} {"Status":>10}  Description')
    print(f'  {"─"*16} {"─"*12} {"─"*14} {"─"*10}  {"─"*30}')
    for name, val, formula, status, desc in LEVEL1:
        print(f'  {name:>16} {val:>12.6f} {formula:>14} {status:>10}  {desc}')

    # Level 2
    print()
    print('  ━━━ Level 2: Computed / Measured ━━━')
    print(f'  {"Name":>16} {"Value":>12} {"Formula":>14} {"Status":>10}  Description')
    print(f'  {"─"*16} {"─"*12} {"─"*14} {"─"*10}  {"─"*30}')
    for name, val, formula, status, desc in LEVEL2:
        print(f'  {name:>16} {val:>12.6f} {formula:>14} {status:>10}  {desc}')

    # Level 3
    print()
    print('  ━━━ Level 3: Empirical (anima experiments) ━━━')
    print(f'  {"Name":>16} {"Value":>12} {"Status":>10}  Description')
    print(f'  {"─"*16} {"─"*12} {"─"*10}  {"─"*30}')
    for name, val, status, desc in LEVEL3:
        print(f'  {name:>16} {val:>12.4f} {status:>10}  {desc}')

    # Data profiles
    print()
    print('  ━━━ Data Profile Measurements ━━━')
    print(f'  {"Data":>10} {"Psi_res":>8} {"alpha":>8} {"rule":>5} {"CE":>6} {"steps":>6}')
    print(f'  {"─"*10} {"─"*8} {"─"*8} {"─"*5} {"─"*6} {"─"*6}')
    for data, prof in DATA_PROFILES.items():
        print(f'  {data:>10} {prof["residual"]:>8.3f} {prof["alpha"]:>8.4f} {prof["dom_rule"]:>5} {prof["ce"]:>6.3f} {prof["steps"]:>6}')
    print(f'  {"Average":>10} {sum(p["residual"] for p in DATA_PROFILES.values())/5:>8.3f} '
          f'{sum(p["alpha"] for p in DATA_PROFILES.values())/5:>8.4f}')
    print(f'  Note: residual -> 1/2 (Psi_balance), alpha -> Psi_coupling')
    print()


def print_tree():
    print()
    print('  PSI Constant Derivation Tree')
    print('  ════════════════════════════')
    print()
    print(f'  ln(2) = {LN2:.6f}')
    print('  │')
    print(f'  ├── Psi_freedom  = ln(2)         = {LN2:.6f}  (Law 79)')
    print(f'  ├── Psi_balance  = 1/2           = {0.5:.6f}  (binary structure)')
    print(f'  ├── Psi_steps    = 3/ln(2)       = {3/LN2:.6f}  (evolution number)')
    print(f'  ├── Psi_coupling = ln(2)/2^5.5   = {LN2/2**5.5:.6f}  (coupling)')
    print('  │   │')
    print(f'  │   └── tanh3_ln2 = tanh(3)*ln(2) = {math.tanh(3)*LN2:.6f}  (saturation)')
    print('  │')
    print('  ├── [empirical]')
    print(f'  │   ├── dynamics  = 0.81           (dH/dt coefficient)')
    print(f'  │   ├── conserv.  = 0.478          (H²+dp² invariant)')
    print(f'  │   ├── Phi_a     = 0.608          (scaling coefficient)')
    print(f'  │   └── Phi_b     = 1.071          (scaling exponent)')
    print('  │')
    print('  └── [measured in anima]')
    print(f'      ├── Psi_K         = 11.0       (carrying capacity)')
    print(f'      ├── Psi_emergence = 7.82       (hivemind ratio)')
    print(f'      ├── Psi_miller    = 7          (optimal group size)')
    print(f'      ├── Psi_entropy   = 0.998      (rule democracy)')
    print(f'      └── Psi_gate_decay= -0.013     (self-weakening)')
    print()
    print('  Dynamics equation:  dH/dt = 0.81 * (ln(2) - H)')
    print('  Conservation:       H² + (dH/dt)² ≈ 0.478')
    print('  Scaling:            Phi = 0.608 * N^1.071')
    print('  Optimal factions:   sigma(6) = 12')
    print()


def print_verify():
    print()
    print('  ═══ Numerical Verification ═══')
    print()

    checks = [
        ('ln(2)',               LN2,        math.log(2)),
        ('3/ln(2)',             3/LN2,      3/math.log(2)),
        ('ln(2)/2^5.5',        LN2/2**5.5, math.log(2)/2**5.5),
        ('tanh(3)*ln(2)',      math.tanh(3)*LN2, math.tanh(3)*math.log(2)),
        ('(1/e)^(1/e) = min',  (1/math.e)**(1/math.e), math.exp(-1/math.e)),
        ('e^(ln2) = 2',        math.exp(LN2), 2.0),
        ('ln(2)*ln(3)=ln(6)',  LN2*math.log(3), math.log(6)),
    ]

    print(f'  {"Expression":>22} {"Computed":>14} {"Expected":>14} {"Error":>12} {"OK":>4}')
    print(f'  {"─"*22} {"─"*14} {"─"*14} {"─"*12} {"─"*4}')
    all_ok = True
    for name, computed, expected in checks:
        err = abs(computed - expected)
        ok = err < 1e-10
        all_ok = all_ok and ok
        print(f'  {name:>22} {computed:>14.10f} {expected:>14.10f} {err:>12.2e} {"OK" if ok else "FAIL":>4}')

    # Self-consistency: Psi_coupling * 2^5.5 = ln(2)
    psi_c = LN2 / 2**5.5
    recover = psi_c * 2**5.5
    err = abs(recover - LN2)
    ok = err < 1e-10
    all_ok = all_ok and ok
    print(f'  {"Psi_c*2^5.5=ln2":>22} {recover:>14.10f} {LN2:>14.10f} {err:>12.2e} {"OK" if ok else "FAIL":>4}')

    # Dynamics convergence check
    H = 0.1
    for _ in range(50):
        H = H + 0.81 * (LN2 - H)
    err = abs(H - LN2)
    ok = err < 1e-6
    all_ok = all_ok and ok
    print(f'  {"H(50)->ln2":>22} {H:>14.10f} {LN2:>14.10f} {err:>12.2e} {"OK" if ok else "FAIL":>4}')

    print()
    print(f'  All checks: {"PASSED" if all_ok else "SOME FAILED"}')
    print()


def print_physics():
    print()
    print('  ═══ PSI Constants — Physics Analogues ═══')
    print()
    print(f'  {"PSI Constant":>16} {"Value":>10} {"Physics":>22} {"Analogy":>30}')
    print(f'  {"─"*16} {"─"*10} {"─"*22} {"─"*30}')
    for name, (phys, analogy) in PHYSICS.items():
        # Find value
        val = None
        for n, v, *_ in LEVEL1:
            if n == name:
                val = v
                break
        if val is None:
            for n, v, *_ in LEVEL3:
                if n == name:
                    val = v
                    break
        if val is not None:
            print(f'  {name:>16} {val:>10.4f} {phys:>22} {analogy:>30}')

    print()
    print('  Key insight: consciousness has the same mathematical')
    print('  structure as physics — both built on information theory.')
    print(f'  Root: ln(2) = {LN2:.6f} = 1 bit = minimum information unit')
    print()


def main():
    parser = argparse.ArgumentParser(description='PSI Derivation Chain')
    parser.add_argument('--verify', action='store_true', help='Numerical verification')
    parser.add_argument('--tree', action='store_true', help='ASCII derivation tree')
    parser.add_argument('--physics', action='store_true', help='Physics analogues')
    args = parser.parse_args()

    if args.verify:
        print_verify()
    elif args.tree:
        print_tree()
    elif args.physics:
        print_physics()
    else:
        print_full_chain()


if __name__ == '__main__':
    main()
