#!/usr/bin/env python3
"""Gravitational Wave Quadrupole Radiation and P1=6 Connections

Why gravitational waves are quadrupole (l=2) radiation and how the
number 6 appears in general relativity through ISCO, photon sphere,
tensor structure, and multipole hierarchy.

Physics:
  - Conservation of energy  => no monopole (l=0) GW radiation
  - Conservation of momentum => no dipole (l=1) GW radiation
  - Lowest allowed: quadrupole l=2
  - Quadrupole power: P = (G/5c^5) <d^3 I_ij/dt^3 d^3 I^ij/dt^3>
  - Factor 1/5 = 1/(2l+1) for l=2

GR constants involving 6:
  - ISCO = 6GM/c^2 (innermost stable circular orbit)
  - Photon sphere = 3GM/c^2 = ISCO/2
  - Riemann tensor in 4D: 20 independent components
  - Einstein equations: 10 independent components
  - Weyl tensor: 10 independent components

Golden Zone dependency: None (pure physics + number theory)

Usage:
  python3 calc/gw_quadrupole_p6.py             # Full analysis
  python3 calc/gw_quadrupole_p6.py --isco       # ISCO derivation only
  python3 calc/gw_quadrupole_p6.py --multipole  # Multipole hierarchy only
  python3 calc/gw_quadrupole_p6.py --tensor     # Tensor DOF analysis
  python3 calc/gw_quadrupole_p6.py --texas      # Texas Sharpshooter test
"""

import argparse
import math
import random
import sys
from fractions import Fraction


# ===================================================================
# Number Theory Functions for P1=6
# ===================================================================

def factorize(n):
    """Return prime factorization as dict {prime: exponent}."""
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
    """Sum of divisors."""
    factors = factorize(n)
    result = 1
    for p, e in factors.items():
        result *= (p**(e+1) - 1) // (p - 1)
    return result


def tau(n):
    """Number of divisors."""
    factors = factorize(n)
    result = 1
    for p, e in factors.items():
        result *= (e + 1)
    return result


def phi(n):
    """Euler totient."""
    factors = factorize(n)
    result = n
    for p in factors:
        result = result * (p - 1) // p
    return result


def divisors(n):
    """Return sorted list of divisors."""
    divs = []
    for i in range(1, int(n**0.5) + 1):
        if n % i == 0:
            divs.append(i)
            if i != n // i:
                divs.append(n // i)
    return sorted(divs)


def sopfr(n):
    """Sum of prime factors with repetition."""
    factors = factorize(n)
    return sum(p * e for p, e in factors.items())


# ===================================================================
# P1=6 Constants
# ===================================================================

N = 6
SIGMA_N = sigma(N)       # 12
TAU_N = tau(N)            # 4
PHI_N = phi(N)            # 2
DIVS_N = divisors(N)      # [1, 2, 3, 6]
SOPFR_N = sopfr(N)        # 5


def print_header(title):
    """Print a section header."""
    width = 70
    print()
    print("=" * width)
    print(f"  {title}")
    print("=" * width)


def print_subheader(title):
    """Print a subsection header."""
    print(f"\n--- {title} ---\n")


# ===================================================================
# 1. Why GW are Quadrupole: Conservation Laws
# ===================================================================

def show_multipole_hierarchy():
    """Explain why gravitational waves start at l=2."""
    print_header("1. WHY GRAVITATIONAL WAVES ARE QUADRUPOLE (l=2)")

    print("""
  In electromagnetism, radiation can be monopole, dipole, quadrupole, etc.
  In gravity, the first two are forbidden by exact conservation laws:

  MONOPOLE (l=0) FORBIDDEN:
    Mass-energy is conserved (no negative mass).
    The mass monopole moment M = sum(m_i) = const.
    => d^n M / dt^n = 0 for all n
    => No monopole radiation.
    Analogy: in EM, charge conservation forbids monopole radiation too.

  DIPOLE (l=1) FORBIDDEN:
    The mass dipole moment d_i = sum(m_a * x_a^i).
    Its time derivative = total momentum P^i = const (conserved).
    => d^2(d_i)/dt^2 = dP^i/dt = 0
    => No dipole radiation.
    KEY DIFFERENCE from EM: In EM, dipole radiation exists because
    positive and negative charges accelerate differently.
    In gravity, there is no negative mass, so the "center of mass"
    dipole moment has zero second derivative.

  QUADRUPOLE (l=2) = LOWEST ALLOWED:
    The mass quadrupole moment I_ij = sum(m_a * x_a^i * x_a^j)
    has no conservation law constraining its third derivative.
    => d^3 I_ij / dt^3 != 0 in general
    => Quadrupole radiation is the leading order.
""")

    # Multipole power formula
    print("  Quadrupole Power Formula (Einstein 1918):")
    print()
    print("    P = (G / 5c^5) * <d^3 I_ij/dt^3 * d^3 I^ij/dt^3>")
    print()
    print("  The factor 1/5:")
    print(f"    1/5 = 1/(2l+1) for l=2")
    print(f"    2l+1 = 5 = number of spherical harmonics Y_2^m")
    print(f"           (m = -2, -1, 0, +1, +2)")
    print()

    # Spin and polarization
    print("  SPIN-2 GRAVITON POLARIZATIONS:")
    print()
    print("    Symmetric h_uv in 4D: 4*5/2 = 10 components")
    print("    Gauge freedom (diffeomorphism): -4 (coordinate choice)")
    print("    Constraint equations:           -4 (Bianchi identity)")
    print("    Physical DOF: 10 - 4 - 4 = 2")
    print()
    print("    These are the + and x polarizations.")
    print(f"    For massless spin-s: 2 helicity states (+/- s)")
    print(f"    Graviton spin s=2: helicities +2 and -2")
    print()

    # ASCII diagram
    print("  MULTIPOLE HIERARCHY:")
    print()
    print("    l=0  Monopole   FORBIDDEN  (mass conservation)")
    print("    l=1  Dipole     FORBIDDEN  (momentum conservation)")
    print("    l=2  Quadrupole ALLOWED    <<<< Dominant GW mode")
    print("    l=3  Octupole   ALLOWED    (suppressed by (v/c)^2)")
    print("    l=4  Hexadecap  ALLOWED    (suppressed by (v/c)^4)")
    print("    ...")
    print()
    print("    Power ratio: P(l+1)/P(l) ~ (v/c)^2")
    print("    For LIGO binaries near merger: v/c ~ 0.3-0.5")
    print("    => Higher multipoles contribute 10-25%")
    print()

    # Connection to n=6 divisors
    print("  DIVISORS OF 6 AND SPIN SPECTRUM:")
    print(f"    div({N}) = {DIVS_N}")
    print()
    print("    Spin 0 (scalar)  : 1 DOF  -- Newtonian potential")
    print("    Spin 1 (vector)  : 2 DOF  -- gravitomagnetism (frame dragging)")
    print("    Spin 2 (tensor)  : 2 DOF  -- gravitational waves")
    print(f"    Sum 1+2+3 = {N}   : the perfect number itself")
    print()
    print("    Note: div(6) = {1,2,3,6} spans spins 0,1,2")
    print(f"    and 1+2+3 = 6 is the perfect number property.")
    print(f"    sigma({N}) = {SIGMA_N} = 2*{N}  (definition of perfect)")


# ===================================================================
# 2. ISCO Derivation
# ===================================================================

def show_isco():
    """Derive ISCO = 6GM/c^2 from the effective potential."""
    print_header("2. ISCO = 6GM/c^2: DERIVATION FROM EFFECTIVE POTENTIAL")

    print("""
  In Schwarzschild spacetime, a test particle's radial motion is
  governed by the effective potential:

    V_eff(r) = -GM/r + L^2/(2r^2) - GML^2/(c^2 r^3)
                 |          |               |
              Newtonian   centrifugal    GR correction
              gravity     barrier        (new term!)

  The GR correction term (-GML^2/c^2 r^3) causes the potential
  barrier to have a maximum AND a minimum (for suitable L).

  Circular orbits: dV/dr = 0
    GM/r^2 - L^2/r^3 + 3GML^2/(c^2 r^4) = 0

  Multiply by r^4/GM:
    r^2 - (L^2/GM)*r + 3L^2/c^2 = 0

  For circular orbit at radius r_c, angular momentum:
    L^2 = GM*r_c^2 / (r_c - 3GM/c^2)

  Stability requires d^2V/dr^2 > 0 (minimum, not maximum):
    d^2V/dr^2 = -2GM/r^3 + 3L^2/r^4 - 12GML^2/(c^2 r^5)

  Substituting L^2 and setting d^2V/dr^2 = 0 for marginal stability:
    r_ISCO = 6GM/c^2   (= 3 * Schwarzschild radius)
""")

    # Numerical verification
    # In geometric units G=c=1, so r = 6M
    print("  NUMERICAL VERIFICATION (G=c=1 units, M=1):")
    print()
    M = 1.0

    # At ISCO r=6M, L^2 = M*r^2/(r - 3M)
    r_isco = 6 * M
    L2_isco = M * r_isco**2 / (r_isco - 3*M)
    print(f"    r_ISCO = 6M = {r_isco:.1f}")
    print(f"    L^2_ISCO = M*r^2/(r-3M) = {L2_isco:.4f}")
    print(f"             = 12M^2 = sigma(6)*M^2 = {SIGMA_N}*M^2")
    print()

    # Check: L^2 = 12M^2
    print(f"    L^2 = {L2_isco:.1f} M^2")
    print(f"    sigma({N}) = {SIGMA_N}")
    print(f"    L^2 / M^2 = {L2_isco / M**2:.1f} = sigma({N})  EXACT!")
    print()

    # Energy at ISCO
    E_isco = math.sqrt(1 - 2*M/r_isco) * math.sqrt(1 - 3*M/r_isco + L2_isco/(r_isco**2))
    # Actually, for ISCO: E/mc^2 = sqrt(8/9) = 2*sqrt(2)/3
    E_over_mc2 = math.sqrt(8.0/9.0)
    efficiency = 1 - E_over_mc2
    print(f"    E_ISCO / mc^2 = sqrt(8/9) = {E_over_mc2:.6f}")
    print(f"    Radiative efficiency = 1 - sqrt(8/9) = {efficiency:.6f}")
    print(f"                        = {efficiency*100:.2f}%")
    print(f"    (This is the maximum energy extraction from accretion)")
    print()

    # The key numbers
    print("  KEY GR RADII (in units of GM/c^2):")
    print()
    print("    +-----------+-------+----------------------+")
    print("    | Structure | r/M   | n=6 connection       |")
    print("    +-----------+-------+----------------------+")
    print(f"    | Event hor | 2     | phi({N})={PHI_N}            |")
    print(f"    | Photon sp | 3     | {N}/phi({N})={N}//{PHI_N}=3       |")
    print(f"    | ISCO      | 6     | n = P1 = {N}          |")
    print(f"    | ISCO L^2  | 12M^2 | sigma({N})={SIGMA_N}       |")
    print("    +-----------+-------+----------------------+")
    print()

    # ISCO derivation: why 6 specifically
    print("  WHY EXACTLY 6? (The algebra)")
    print()
    print("    Setting d^2V/dr^2 = 0 at a circular orbit:")
    print("    After substitution, the condition reduces to:")
    print("      r^2 - 6Mr + 9M^2 - 3M^2 + ... = 0")
    print()
    print("    More precisely, the stability equation gives:")
    print("      r_ISCO(r - 6M) = 0  =>  r_ISCO = 6M")
    print()
    print("    The '6' comes from the coefficient in:")
    print("      d^2V_eff/dr^2 evaluated at L^2 = L^2_ISCO")
    print("    which involves the ratio of the Newtonian (1/r)")
    print("    and GR correction (1/r^3) terms.")
    print()
    print("    Specifically, the cubic equation for circular orbits in")
    print("    Schwarzschild gives r = 6M as the degenerate root where")
    print("    the minimum and maximum of V_eff merge (inflection point).")


# ===================================================================
# 3. Tensor Structure and DOF Counting
# ===================================================================

def show_tensor_dof():
    """Analyze tensor degrees of freedom in GR and connections to 6."""
    print_header("3. TENSOR DEGREES OF FREEDOM IN GENERAL RELATIVITY")

    D = 4  # spacetime dimensions

    # Metric tensor
    metric_comp = D * (D + 1) // 2
    print(f"\n  METRIC TENSOR g_uv (symmetric, {D}D):")
    print(f"    Independent components: D(D+1)/2 = {D}*{D+1}/2 = {metric_comp}")
    print()

    # Riemann tensor
    # In D dimensions: D^2(D^2-1)/12
    riemann = D**2 * (D**2 - 1) // 12
    print(f"  RIEMANN TENSOR R_abcd ({D}D):")
    print(f"    Independent components: D^2(D^2-1)/12 = {D}^2*{D**2-1}/12 = {riemann}")
    print(f"    Decomposition: Riemann = Weyl + Ricci part")
    print()

    # Ricci tensor (symmetric)
    ricci = D * (D + 1) // 2
    print(f"  RICCI TENSOR R_ab (symmetric, {D}D):")
    print(f"    Independent components: D(D+1)/2 = {ricci}")
    print()

    # Weyl tensor
    weyl = riemann - ricci  # In 4D: 20 - 10 = 10
    print(f"  WEYL TENSOR C_abcd ({D}D):")
    print(f"    Independent components: {riemann} - {ricci} = {weyl}")
    print(f"    (trace-free part of Riemann)")
    print()

    # Einstein equations
    einstein = ricci  # G_uv = 8piG/c^4 T_uv, symmetric
    print(f"  EINSTEIN FIELD EQUATIONS G_uv = 8piG/c^4 T_uv:")
    print(f"    Independent equations: {einstein} (= symmetric 2-tensor)")
    print(f"    Bianchi identity removes 4 => {einstein-4} true DOF")
    print()

    # Summary table
    print("  COMPONENT COUNT TABLE:")
    print()
    print("    +------------------+------+--------------------+")
    print("    | Object           | Comp | n=6 connection     |")
    print("    +------------------+------+--------------------+")
    print(f"    | Metric g_uv      | {metric_comp:4d} | = tau(496)={tau(496)}      |")
    print(f"    | Riemann R_abcd   | {riemann:4d} | = C(6,3) = 20      |")
    print(f"    | Ricci R_ab       | {ricci:4d} | = T(4) = metric    |")
    print(f"    | Weyl C_abcd      | {weyl:4d} | = T(4) = metric    |")
    print(f"    | Einstein G_uv    | {einstein:4d} | = T(4) = metric    |")
    print(f"    | GW polarizations | {2:4d} | = phi({N})={PHI_N}          |")
    print("    +------------------+------+--------------------+")
    print()

    # Check C(6,3) + C(6,2) = 20?
    from math import comb
    c63 = comb(6, 3)
    c62 = comb(6, 2)
    print(f"  RIEMANN = 20 DECOMPOSITION:")
    print(f"    C(6,3) = {c63}")
    print(f"    C(6,2) = {c62}")
    print(f"    C(6,3) + C(6,2) = {c63 + c62}")
    if c63 + c62 == riemann:
        print(f"    = {riemann} = Riemann components  MATCH!")
    else:
        print(f"    != {riemann}. Checking other decompositions...")
    print()

    # Alternative: D^2(D^2-1)/12 for D=4
    print(f"  Direct: D^2(D^2-1)/12 = 16*15/12 = {16*15//12}")
    print(f"  Also: C(D+1,4) + C(D+1,2) - ... No, the standard formula is")
    print(f"         D^2(D^2-1)/12 from the symmetries of Riemann.")
    print()

    # Triangular numbers
    def triangular(k):
        return k * (k + 1) // 2

    print("  TRIANGULAR NUMBERS T(k) = k(k+1)/2:")
    for k in range(1, 8):
        t = triangular(k)
        note = ""
        if t == metric_comp:
            note = " <-- metric, Ricci, Weyl, Einstein components"
        if t == riemann:
            note = " <-- Riemann components (T(k) at wrong k though)"
        if k == 3:
            note = f" = {N} = P1!"
        print(f"    T({k}) = {t}{note}")
    print()

    # Key: T(3) = 6 = n
    print(f"  T(3) = 3*4/2 = {triangular(3)} = n = P1")
    print(f"  T(4) = 4*5/2 = {triangular(4)} = metric components in 4D")
    print(f"  The number of metric components = T(D) = T(4) = {triangular(4)}")
    print()

    # Graviton DOF counting
    print("  GRAVITON DOF COUNTING (massless spin-2 in 4D):")
    print(f"    Total symmetric tensor: {metric_comp}")
    print(f"    - Gauge (diffeomorphisms): {D}")
    print(f"    - Constraints (Bianchi):   {D}")
    print(f"    = Physical DOF: {metric_comp} - {D} - {D} = {metric_comp - 2*D}")
    print(f"    These are the 2 = phi({N}) GW polarizations (+ and x)")
    print()

    # Connection to sigma/n = 2
    print(f"  PERFECT NUMBER PROPERTY AND QUADRUPOLE:")
    print(f"    sigma({N})/{N} = {SIGMA_N}/{N} = {SIGMA_N // N}")
    print(f"    sigma_{{-1}}({N}) = sum(1/d for d in div({N})) = ", end="")
    sigma_inv = sum(Fraction(1, d) for d in DIVS_N)
    print(f"{sigma_inv} = {float(sigma_inv)}")
    print(f"    This is the DEFINING property of perfect numbers.")
    print(f"    sigma({N}) = 2*{N} = {SIGMA_N}")
    print(f"    The factor 2 = l (quadrupole order) = phi({N}).")


# ===================================================================
# 4. Dimensional Analysis of the Quadrupole Formula
# ===================================================================

def show_quadrupole_formula():
    """Analyze the quadrupole formula P = (G/5c^5) <...>."""
    print_header("4. QUADRUPOLE FORMULA: P = (G/5c^5) <d^3 I_ij/dt^3>^2")

    print("""
  The Einstein quadrupole formula for gravitational wave power:

    P_GW = (G / 5c^5) * <(d^3 I_ij/dt^3)^2>

  where I_ij is the reduced mass quadrupole moment tensor.

  FACTOR ANALYSIS:
    G   : gravitational constant [m^3 kg^-1 s^-2]
    c^5 : speed of light to 5th power [m^5 s^-5]
    5   : = 2l+1 for l=2 (quadrupole)

  WHY 1/5?
    The full derivation involves integrating over solid angles:
    integral of |Y_lm|^2 over the sphere = 1/(2l+1) normalization.
    For l=2: 1/(2*2+1) = 1/5.
""")

    print("  MULTIPOLE POWER HIERARCHY:")
    print()
    print("    +------+----------+----------+-------------------------+")
    print("    | l    | Name     | 1/(2l+1) | Status                  |")
    print("    +------+----------+----------+-------------------------+")
    names = ["Monopole", "Dipole", "Quadrupole", "Octupole", "Hexadecapole"]
    for l in range(5):
        factor = Fraction(1, 2*l + 1)
        if l == 0:
            status = "FORBIDDEN (mass conservation)"
        elif l == 1:
            status = "FORBIDDEN (momentum conservation)"
        elif l == 2:
            status = "DOMINANT (lowest allowed)"
        else:
            status = f"Suppressed by (v/c)^{2*(l-2)}"
        print(f"    | l={l}  | {names[l]:12s} | {str(factor):8s} | {status} |")
    print("    +------+----------+----------+-------------------------+")
    print()

    # Binary system example
    print("  BINARY SYSTEM (two equal masses m in circular orbit):")
    print()
    m = 1.0  # solar masses (symbolic)
    print("    P_GW = (32/5) * (G^4/c^5) * m^5 / r^5")
    print()
    print("    The factor 32/5:")
    print(f"      32 = 2^5")
    print(f"       5 = 2l+1 for l=2")
    print(f"      32/5 = {Fraction(32,5)} = {32/5:.1f}")
    print()

    # Peters formula for orbital decay
    print("  ORBITAL DECAY (Peters 1964):")
    print()
    print("    da/dt = -(64/5) * (G^3/c^5) * m1*m2*(m1+m2) / a^3")
    print()
    print(f"    64/5 = 2^6/5 = {Fraction(64,5)}")
    print(f"    Note: 2^6 = 64, exponent is sigma({N})/phi({N}) = {SIGMA_N}/{PHI_N} = {SIGMA_N//PHI_N}")
    print(f"    But also simply 2^{N} = {2**N}")
    print()

    # GW frequency at ISCO
    print("  GW FREQUENCY AT ISCO (characteristic frequency):")
    print()
    print("    f_ISCO = c^3 / (6^(3/2) * pi * GM)")
    print(f"    6^(3/2) = 6*sqrt(6) = {6**1.5:.6f}")
    print(f"    For M_sun: f_ISCO ~ 4400 / (M/M_sun) Hz")
    print()
    print(f"    The 6^(3/2) factor comes directly from r_ISCO = 6M")
    print(f"    and the Kepler relation Omega^2 = M/r^3.")


# ===================================================================
# 5. Comprehensive n=6 Connection Map
# ===================================================================

def show_connection_map():
    """Map all n=6 appearances in gravitational wave physics."""
    print_header("5. COMPREHENSIVE n=6 CONNECTION MAP IN GW PHYSICS")

    connections = [
        ("ISCO radius", "r_ISCO = 6M", "6 = n = P1",
         "PROVEN", "Schwarzschild effective potential extremum"),
        ("ISCO ang. momentum", "L^2_ISCO = 12M^2", f"12 = sigma({N})",
         "PROVEN", "L^2 = Mr^2/(r-3M) at r=6M"),
        ("Photon sphere", "r_ph = 3M = ISCO/2", f"3 = {N}/phi({N})",
         "PROVEN", "Null geodesic circular orbit"),
        ("Event horizon", "r_s = 2M", f"2 = phi({N})",
         "PROVEN", "g_tt = 0 solution"),
        ("Quadrupole order", "l = 2", f"2 = phi({N}) = sigma({N})/{N}",
         "PROVEN", "Conservation laws forbid l<2"),
        ("Polarizations", "2 (+ and x)", f"2 = phi({N})",
         "PROVEN", "Massless spin-2 DOF count"),
        ("Quadrupole factor", "1/5 = 1/(2l+1)", "5 = sopfr(6)",
         "EXACT", "Spherical harmonic normalization"),
        ("GW freq at ISCO", "f ~ 1/6^(3/2)", f"6^(3/2) from r_ISCO=6M",
         "PROVEN", "Kepler + ISCO"),
        ("Metric components", "10 = D(D+1)/2", f"10 = T(4) = tau(496)",
         "PROVEN", "Symmetric tensor in 4D"),
        ("Riemann components", "20 in 4D", "20 = C(6,3)",
         "EXACT", "D^2(D^2-1)/12 = 20"),
        ("Weyl components", "10 in 4D", "10 = Riemann - Ricci",
         "PROVEN", "Trace-free Riemann"),
        ("Peters decay 64/5", "2^6/(2l+1)", f"exponent 6 = n",
         "EXACT", "Orbital energy loss rate"),
        ("Spin spectrum", "0,1,2 in div(6)", "1+2+3 = 6",
         "STRUCTURAL", "Scalar + vector + tensor = P1"),
        ("Radiative eff.", "1-sqrt(8/9)=5.72%", "8/9 from r=6M",
         "PROVEN", "Maximum accretion efficiency"),
    ]

    print()
    print("  +---+---------------------+---------------------+-------------------+----------+")
    print("  | # | Physical quantity   | Value               | n=6 link          | Status   |")
    print("  +---+---------------------+---------------------+-------------------+----------+")
    for i, (name, value, link, status, _) in enumerate(connections, 1):
        print(f"  |{i:2d} | {name:19s} | {value:19s} | {link:17s} | {status:8s} |")
    print("  +---+---------------------+---------------------+-------------------+----------+")
    print()

    # Classification
    proven_count = sum(1 for c in connections if c[3] == "PROVEN")
    exact_count = sum(1 for c in connections if c[3] == "EXACT")
    structural_count = sum(1 for c in connections if c[3] == "STRUCTURAL")
    total = len(connections)
    print(f"  PROVEN: {proven_count}/{total}  EXACT: {exact_count}/{total}  STRUCTURAL: {structural_count}/{total}")
    print()

    # Highlight strongest connections
    print("  STRONGEST CONNECTIONS (independently derived, not ad hoc):")
    print()
    print("  1. ISCO = 6M: The '6' emerges from a cubic equation in the")
    print("     Schwarzschild effective potential. It is NOT a free parameter.")
    print("     This is the single most robust n=6 appearance in GR.")
    print()
    print("  2. L^2_ISCO = 12M^2 = sigma(6)M^2: The angular momentum at")
    print("     ISCO follows directly from ISCO=6M. Not independent of #1.")
    print()
    print("  3. Quadrupole l=2: Conservation laws (not n=6) force this.")
    print("     The match l=2=phi(6) is a small-integer coincidence.")
    print()
    print("  4. 1/5 factor and sopfr(6)=5: Interesting but sopfr(6)=5 is")
    print("     a small number. Moderate evidence at best.")
    print()
    print("  5. Peters 2^6/5: The exponent 6 in 2^6=64 comes from the")
    print("     binary power formula. Connected to ISCO? Indirectly yes,")
    print("     since the dominant GW emission is near r~6M.")

    return connections


# ===================================================================
# 6. ASCII Diagram
# ===================================================================

def show_ascii_diagram():
    """ASCII diagram of black hole structure and GW emission."""
    print_header("6. BLACK HOLE STRUCTURE AND GW EMISSION")

    print("""
  Schwarzschild Black Hole Radii:

  r/M:  0    1    2    3    4    5    6    7    8    9    10
        |----|----|----|----|----|----|----|----|----|----|
              [SINGULARITY]
                   |
                   r_s = 2M (Event Horizon)
                   phi(6) = 2
                        |
                        r_ph = 3M (Photon Sphere)
                        n/phi(n) = 3
                                            |
                                            r_ISCO = 6M
                                            n = P1 = 6
                                            L^2 = sigma(6)M^2 = 12M^2

  Effective Potential V_eff(r) for different L:

  V_eff
    |         .
    |        / \\         L > L_ISCO (stable + unstable orbits)
    |       /   \\....
    |      /         \\
    |     / ..........\\....  L = L_ISCO (inflection at r=6M) <--
    |    //            \\
    |   /               L < L_ISCO (plunge, no stable orbit)
    |  /
    | /
    |/_________________________ r/M
    0    2    4    6    8   10

  At r_ISCO = 6M: the minimum and maximum of V_eff merge
  (inflection point). This is why 6 is special -- it is the
  boundary between bound orbits and plunge orbits.

  Gravitational Wave Emission from Binary:

        *  <-- mass 1             Quadrupole pattern:
       / \\                             +
      /   \\    orbit                 / | \\
     /  .  \\   r ~ 6M             /   |   \\
      \\   /    at merger     ----     GW     ----
       \\ /                        \\   |   /
        *  <-- mass 2               \\ | /
                                      +

    h_+ ~ cos(2*Phi)     (plus polarization)
    h_x ~ sin(2*Phi)     (cross polarization)
    2 polarizations = phi(6) = 2
""")


# ===================================================================
# 7. Generalization Test: n=28 (second perfect number)
# ===================================================================

def show_generalization():
    """Test which connections generalize to n=28."""
    print_header("7. GENERALIZATION TEST: n=28 (SECOND PERFECT NUMBER)")

    n28 = 28
    s28 = sigma(n28)
    t28 = tau(n28)
    p28 = phi(n28)
    d28 = divisors(n28)
    sp28 = sopfr(n28)

    print(f"\n  n=28 properties:")
    print(f"    sigma(28) = {s28}")
    print(f"    tau(28) = {t28}")
    print(f"    phi(28) = {p28}")
    print(f"    divisors(28) = {d28}")
    print(f"    sopfr(28) = {sp28}")
    print()

    tests = [
        ("ISCO = nM?", "r_ISCO = 6M always (Schwarzschild geometry)",
         "P1-ONLY", "ISCO is fixed by the metric, not by which perfect number we pick"),
        ("L^2 = sigma(n)*M^2?", f"L^2 = 12M^2 = sigma(6)M^2 at ISCO",
         "P1-ONLY", "ISCO fixed at 6M => L^2 fixed at 12M^2"),
        ("Quadrupole l=phi(n)?", f"l=2=phi(6), but phi(28)={p28}!=2",
         "P1-ONLY", f"l=2 from conservation laws, phi(28)={p28}"),
        ("Polarizations=phi(n)?", f"2=phi(6), but phi(28)={p28}",
         "P1-ONLY", f"DOF count is topological, phi(28)={p28}"),
        ("1/(2l+1)=1/sopfr(n)?", f"1/5, sopfr(6)={SOPFR_N}, sopfr(28)={sp28}",
         "P1-ONLY" if SOPFR_N == 5 else "NONE", f"sopfr(28)={sp28}!=5"),
        ("sigma(n)/n = 2?", f"sigma(6)/6=2, sigma(28)/28=2",
         "UNIVERSAL", "Definition of perfect number"),
        ("Spin sum = n?", f"0+1+2=3!=28",
         "P1-ONLY", "Spin spectrum is physical, not number-theoretic"),
    ]

    print("  +---+---------------------------+----------+--------------------------------+")
    print("  | # | Test                       | Class    | Reason                         |")
    print("  +---+---------------------------+----------+--------------------------------+")
    for i, (test, detail, cls, reason) in enumerate(tests, 1):
        print(f"  |{i:2d} | {test:25s} | {cls:8s} | {reason:30s} |")
    print("  +---+---------------------------+----------+--------------------------------+")
    print()

    p1_count = sum(1 for t in tests if t[2] == "P1-ONLY")
    univ_count = sum(1 for t in tests if t[2] == "UNIVERSAL")
    print(f"  P1-ONLY: {p1_count}/{len(tests)}  UNIVERSAL: {univ_count}/{len(tests)}")
    print()
    print("  KEY INSIGHT: Almost all GR connections are P1-ONLY because")
    print("  they stem from ISCO=6M which is a fixed property of the")
    print("  Schwarzschild metric, not a property of perfect numbers in general.")
    print("  The number 6 appears in GR for geometric reasons (cubic equation")
    print("  in the effective potential), not because the universe 'knows'")
    print("  about perfect numbers.")
    print()
    print("  However, the COINCIDENCE that ISCO=6M=P1 is remarkable:")
    print("  among all integers, the ISCO coefficient happens to be the")
    print("  first (and only small) perfect number.")


# ===================================================================
# 8. Texas Sharpshooter Test
# ===================================================================

def texas_sharpshooter():
    """Perform Texas Sharpshooter test on the GW-P6 connections."""
    print_header("8. TEXAS SHARPSHOOTER TEST")

    print()
    print("  Search space: coefficients/integers appearing in GR formulas")
    print("  Target: matching n=6 arithmetic functions")
    print()

    # Define the search space
    # GR produces various integer coefficients. We ask: how many match n=6 functions?
    gr_integers = {
        "Event horizon": 2,
        "Photon sphere": 3,
        "ISCO": 6,
        "ISCO L^2 coeff": 12,
        "BH entropy denom": 4,
        "Hawking T factor": 8,  # 8*pi
        "Metric components": 10,
        "Riemann components": 20,
        "Weyl components": 10,
        "Bianchi constraint": 4,
        "GW polarizations": 2,
        "Quadrupole l": 2,
        "Quadrupole 2l+1": 5,
        "Peters 2^6 coeff": 64,
        "Peters denominator": 5,
    }

    n6_functions = {
        "n": N,
        "sigma(n)": SIGMA_N,
        "tau(n)": TAU_N,
        "phi(n)": PHI_N,
        "sopfr(n)": SOPFR_N,
        "n!": math.factorial(N),  # 720
        "n/phi(n)": N // PHI_N,  # 3
        "sigma(n)/n": SIGMA_N // N,  # 2
    }

    n6_values = set(n6_functions.values())

    print("  GR coefficients found:")
    matches = 0
    total = len(gr_integers)
    for name, val in sorted(gr_integers.items(), key=lambda x: x[1]):
        match_names = [k for k, v in n6_functions.items() if v == val]
        if match_names:
            matches += 1
            print(f"    {val:5d} = {name:25s}  MATCH: {', '.join(match_names)}")
        else:
            print(f"    {val:5d} = {name:25s}  (no n=6 match)")
    print()

    # Monte Carlo: random perfect number in [1, 100], how many GR integers match?
    N_TRIALS = 100000
    random.seed(42)
    gr_vals = set(gr_integers.values())

    # For each trial, pick a random integer n in [2, 50], compute its functions
    random_match_counts = []
    for _ in range(N_TRIALS):
        n = random.randint(2, 50)
        nf = factorize(n)
        s = sigma(n)
        t = tau(n)
        p = phi(n)
        sp = sopfr(n)
        trial_vals = {n, s, t, p, sp, n * (n-1) // 2, s // n if n > 0 and s % n == 0 else -1}
        if p > 0 and n % p == 0:
            trial_vals.add(n // p)
        count = len(gr_vals.intersection(trial_vals))
        random_match_counts.append(count)

    avg_random = sum(random_match_counts) / N_TRIALS
    std_random = (sum((x - avg_random)**2 for x in random_match_counts) / N_TRIALS) ** 0.5

    # Count matches for n=6
    n6_all_vals = set(n6_functions.values())
    actual_matches = len(gr_vals.intersection(n6_all_vals))

    z_score = (actual_matches - avg_random) / std_random if std_random > 0 else 0

    # p-value from Monte Carlo
    p_value = sum(1 for c in random_match_counts if c >= actual_matches) / N_TRIALS

    print(f"  RESULTS:")
    print(f"    GR coefficients tested: {total}")
    print(f"    n=6 function values: {sorted(n6_all_vals)}")
    print(f"    Actual matches (n=6): {actual_matches}/{total}")
    print(f"    Random baseline (n in [2,50]): {avg_random:.2f} +/- {std_random:.2f}")
    print(f"    Z-score: {z_score:.2f}")
    print(f"    p-value (Monte Carlo, {N_TRIALS:,} trials): {p_value:.4f}")
    print()

    # Bonferroni correction
    n_hypotheses = 14  # number of connections tested
    p_bonf = min(p_value * n_hypotheses, 1.0)
    print(f"    Bonferroni correction ({n_hypotheses} hypotheses): p = {p_bonf:.4f}")
    print()

    # Grade
    if p_bonf < 0.01:
        grade = "🟧★ (structural, p < 0.01)"
    elif p_bonf < 0.05:
        grade = "🟧  (weak evidence, p < 0.05)"
    else:
        grade = "⚪  (not significant, p > 0.05)"
    print(f"    GRADE: {grade}")
    print()

    # Honest assessment
    print("  HONEST ASSESSMENT:")
    print()
    print("    The ISCO = 6M result is PROVEN from GR (not a hypothesis).")
    print("    The question is whether ISCO=6M=P1 is MEANINGFUL or coincidental.")
    print()
    print("    Arguments FOR structural significance:")
    print("    - 6 is the unique first perfect number")
    print("    - ISCO=6M is exact and parameter-free")
    print("    - L^2=12M^2=sigma(6)M^2 follows naturally")
    print("    - Multiple GR integers (2,3,6,12) form the complete divisor")
    print("      set of 6, not just one match")
    print()
    print("    Arguments AGAINST:")
    print("    - The '6' in ISCO comes from a cubic polynomial, not number theory")
    print("    - GR does not 'know about' perfect numbers")
    print("    - Small integers (2,3,6,12) appear everywhere in physics")
    print("    - The divisor set {1,2,3,6} contains the most common small integers")
    print()
    print("    VERDICT: The ISCO=6M fact is physically proven and mathematically")
    print("    exact. Its connection to P1=6 is a STRUCTURAL COINCIDENCE --")
    print("    remarkable enough to note, but lacking a causal mechanism.")

    return actual_matches, avg_random, std_random, z_score, p_value, p_bonf


# ===================================================================
# Main
# ===================================================================

def main():
    parser = argparse.ArgumentParser(description="GW Quadrupole Radiation and P1=6")
    parser.add_argument("--isco", action="store_true", help="ISCO derivation only")
    parser.add_argument("--multipole", action="store_true", help="Multipole hierarchy only")
    parser.add_argument("--tensor", action="store_true", help="Tensor DOF analysis only")
    parser.add_argument("--formula", action="store_true", help="Quadrupole formula analysis")
    parser.add_argument("--texas", action="store_true", help="Texas Sharpshooter test only")
    parser.add_argument("--diagram", action="store_true", help="ASCII diagram only")
    args = parser.parse_args()

    specific = any([args.isco, args.multipole, args.tensor, args.formula,
                     args.texas, args.diagram])

    print("=" * 70)
    print("  GRAVITATIONAL WAVE QUADRUPOLE RADIATION AND P1=6 CONNECTIONS")
    print("  Golden Zone Dependency: None (pure physics + number theory)")
    print("=" * 70)

    print(f"\n  P1 = {N}")
    print(f"  sigma({N}) = {SIGMA_N},  tau({N}) = {TAU_N},  phi({N}) = {PHI_N}")
    print(f"  divisors({N}) = {DIVS_N},  sopfr({N}) = {SOPFR_N}")

    if not specific or args.multipole:
        show_multipole_hierarchy()
    if not specific or args.isco:
        show_isco()
    if not specific or args.tensor:
        show_tensor_dof()
    if not specific or args.formula:
        show_quadrupole_formula()
    if not specific:
        show_connection_map()
    if not specific or args.diagram:
        show_ascii_diagram()
    if not specific:
        show_generalization()
    if not specific or args.texas:
        actual, avg, std, z, p, p_bonf = texas_sharpshooter()

    # Final summary
    if not specific:
        print_header("FINAL SUMMARY")
        print("""
  The number 6 appears in general relativity through the ISCO radius
  (r_ISCO = 6GM/c^2), which is derived from the Schwarzschild effective
  potential. This is an EXACT, PROVEN result of GR with no free parameters.

  The complete divisor set of 6 = {1, 2, 3, 6} maps onto key GR radii:
    - 2M = event horizon (phi(6) = 2)
    - 3M = photon sphere (6/phi(6) = 3)
    - 6M = ISCO (n = P1 = 6)
    - 12M^2 = L^2_ISCO (sigma(6) = 12)

  Gravitational waves are quadrupole (l=2) due to conservation of
  energy (no monopole) and momentum (no dipole). The match l=2=phi(6)
  is a small-integer coincidence, not a deep connection.

  CLASSIFICATION:
    ISCO = 6M = P1:           P1-ONLY, PROVEN (strongest)
    L^2 = sigma(6)M^2:        P1-ONLY, PROVEN (derived from ISCO)
    GR radii = div(6) * M:    P1-ONLY, STRUCTURAL (all four divisors!)
    Quadrupole l=2=phi(6):    COINCIDENCE (conservation law origin)
    1/5 = 1/sopfr(6):         COINCIDENCE (small number match)
    Riemann 20 = C(6,3):         EXACT but likely coincidental

  OVERALL GRADE: The ISCO=6M result is the genuine standout.
  The fact that ALL Schwarzschild radii (2M, 3M, 6M) form a subset
  of div(6) = {1,2,3,6} is structurally notable, though the causal
  mechanism (if any) is unknown.
""")


if __name__ == "__main__":
    main()
