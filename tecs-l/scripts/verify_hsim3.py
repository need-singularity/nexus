#!/usr/bin/env python3
"""H-SIM-3: Quantum Uncertainty = Floating Point Precision
Verify that Heisenberg uncertainty arises from simulator's finite precision."""

import math

print("=" * 70)
print("H-SIM-3: Quantum Uncertainty = Floating Point Precision")
print("=" * 70)

# --- Physical Constants ---
hbar = 1.054571817e-34    # Reduced Planck constant (J·s)
c = 2.99792458e8          # Speed of light (m/s)
G = 6.67430e-11           # Gravitational constant (m³/kg/s²)
lp = math.sqrt(hbar * G / c**3)  # Planck length
tp = math.sqrt(hbar * G / c**5)  # Planck time
mp = math.sqrt(hbar * c / G)     # Planck mass
Ep = mp * c**2                     # Planck energy

print(f"\n--- Fundamental Constants ---")
print(f"  hbar  = {hbar:.6e} J·s")
print(f"  c     = {c:.6e} m/s")
print(f"  G     = {G:.5e} m³/kg/s²")
print(f"  lp    = {lp:.6e} m  (Planck length)")
print(f"  tp    = {tp:.6e} s  (Planck time)")
print(f"  mp    = {mp:.6e} kg (Planck mass)")
print(f"  Ep    = {Ep:.6e} J  (Planck energy)")

# --- 1. Minimum precision = Planck scale ---
print(f"\n--- 1. Minimum Precision at Planck Scale ---")
dx_min = lp
dp_min = hbar / lp
print(f"  Minimum Dx = lp = {dx_min:.6e} m")
print(f"  Minimum Dp = hbar/lp = {dp_min:.6e} kg·m/s")
product = dx_min * dp_min
print(f"  Dx * Dp = {product:.6e} J·s")
print(f"  hbar    = {hbar:.6e} J·s")
print(f"  Ratio   = {product/hbar:.6f}")
print(f"  --> Dx*Dp = hbar EXACTLY (by construction)")
print(f"  --> This IS the Heisenberg uncertainty relation Dx*Dp >= hbar/2")
print(f"      (saturated at minimum = hbar, factor of 2 from Gaussian minimum)")

# --- 2. Required bits for position ---
print(f"\n--- 2. Required Bits: B = log2(R/lp) ---")
R_universe = 4.4e26  # Observable universe radius (m)
B_position = math.log2(R_universe / lp)
print(f"  R (observable universe) = {R_universe:.2e} m")
print(f"  lp (Planck length)      = {lp:.6e} m")
print(f"  R/lp = {R_universe/lp:.6e}")
print(f"  B_position = log2(R/lp) = {B_position:.2f} bits")
print(f"  Rounded: {round(B_position)} bits")

# --- 3. Is 204 special? ---
B = round(B_position)
print(f"\n--- 3. Number Theory of B = {B} ---")
print(f"  {B} = 2 x {B//2}")
print(f"  {B} = 3 x {B//3}")
print(f"  {B} = 4 x {B//4}")
print(f"  {B} = 6 x {B//6}")
print(f"  {B} = 12 x {B//12}")

# Factor 204 completely
n = B
factors = []
temp = n
for p in range(2, temp + 1):
    while temp % p == 0:
        factors.append(p)
        temp //= p
    if temp == 1:
        break
print(f"  Prime factorization: {B} = {' x '.join(map(str, factors))}")

# Divisors
divisors = [i for i in range(1, B+1) if B % i == 0]
print(f"  Divisors: {divisors}")
print(f"  Number of divisors: {len(divisors)}")
print(f"  Sum of divisors: sigma({B}) = {sum(divisors)}")

# Perfect number 6 connection
sigma_6 = 12  # sigma(6) = 1+2+3+6 = 12
print(f"\n  sigma(6) = {sigma_6}")
print(f"  {B} / sigma(6) = {B} / {sigma_6} = {B/sigma_6}")
print(f"  {B} = sigma(6) x 17 = 12 x 17 = {12*17}")
print(f"  17 = Fermat prime F2 = 2^(2^2) + 1")
print(f"  17 = Amplification constant A(theta=pi) from TECS-L!")
print(f"  --> B = sigma(6) x A(pi) = 12 x 17 = 204")

# Also check 6 x 34
print(f"\n  Alternative decompositions:")
print(f"  {B} = 6 x 34 = 6 x 2 x 17")
print(f"  {B} = 6 x 34 (perfect number x 2*Fermat)")

# --- 4. Momentum precision ---
print(f"\n--- 4. Momentum Precision ---")
max_p = mp * c  # Maximum momentum ~ Planck momentum
dp_planck = hbar / R_universe  # Minimum momentum uncertainty
B_momentum = math.log2(max_p / dp_planck)
print(f"  Max momentum (Planck) = mp*c = {max_p:.6e} kg·m/s")
print(f"  Min momentum (hbar/R) = {dp_planck:.6e} kg·m/s")
print(f"  B_momentum = log2(max_p/min_dp) = {B_momentum:.2f} bits")
print(f"  B_position  = {B_position:.2f} bits")
print(f"  Difference   = {abs(B_momentum - B_position):.2f} bits")
print(f"  --> Position and momentum require SAME number of bits!")
print(f"      This is because max_p/min_dp = (mp*c)/(hbar/R) = mp*c*R/hbar")
print(f"      And R/lp = R*sqrt(c³/(hbar*G)) while mp*c*R/hbar = R*c*sqrt(c/(hbar*G))")

# More careful: B_mom = log2(max_p * R / hbar) since Dx*Dp ~ hbar
# Actually by uncertainty: if you know x to R, then Dp ~ hbar/R
# The dynamic range is max_p / (hbar/R)
# Note: max_p could also be argued as universe_mass * c
M_universe = 1.5e53  # kg, observable universe mass
max_p2 = M_universe * c
B_momentum2 = math.log2(max_p2 / dp_planck)
print(f"\n  Alternative: max_p = M_universe * c = {max_p2:.3e} kg·m/s")
print(f"  B_momentum(alt) = {B_momentum2:.2f} bits")

# --- 5. Double precision comparison ---
print(f"\n--- 5. Double Precision (64-bit) Comparison ---")
eps_double = 2**-52  # Machine epsilon for double
print(f"  Double precision epsilon = 2^-52 = {eps_double:.3e}")
print(f"  Mantissa bits = 52")
print(f"  Planck/atomic ratio: lp / (1e-10 m) = {lp/1e-10:.3e}")
print(f"  Planck/universe ratio: lp / R = {lp/R_universe:.3e}")
print(f"  log2(atomic/Planck) = {math.log2(1e-10/lp):.1f} bits")
print(f"  log2(universe/Planck) = {math.log2(R_universe/lp):.1f} bits = B!")
print(f"  --> 64-bit double CANNOT resolve Planck scale from universe scale")
print(f"      (need {round(B_position)} bits, have 52 mantissa bits)")
print(f"  --> Deficit = {round(B_position) - 52} bits")

# --- 6. Energy-Time uncertainty ---
print(f"\n--- 6. Other Uncertainty Relations ---")

# Energy-Time: DE * Dt >= hbar/2
E_max = Ep  # Planck energy
E_min = hbar / (4.35e17)  # hbar / age_of_universe (s)
age_universe = 4.35e17  # seconds (13.8 Gyr)
B_energy = math.log2(E_max / E_min)
print(f"  Energy-Time uncertainty:")
print(f"    E_max (Planck) = {E_max:.3e} J")
print(f"    E_min (hbar/t_universe) = {E_min:.3e} J")
print(f"    B_energy = log2(E_max/E_min) = {B_energy:.2f} bits")

B_time = math.log2(age_universe / tp)
print(f"    t_max (age of universe) = {age_universe:.3e} s")
print(f"    t_min (Planck time) = {tp:.3e} s")
print(f"    B_time = log2(t_max/t_min) = {B_time:.2f} bits")

# Angle-Angular momentum: Dphi * DL >= hbar/2
# Angle range: 0 to 2*pi, Angular momentum: 0 to hbar * n_max
# n_max ~ R * max_p / hbar
print(f"\n  Angle-Angular Momentum uncertainty:")
print(f"    Angle range: 2*pi (bounded)")
print(f"    Angular momentum: quantized in units of hbar")
print(f"    L_max ~ R * max_p = {R_universe * max_p:.3e} J·s")
print(f"    L_max / hbar = {R_universe * max_p / hbar:.3e}")
B_angular = math.log2(R_universe * max_p / hbar)
print(f"    B_angular = log2(L_max/hbar) = {B_angular:.2f} bits")

print(f"\n--- 7. Summary: Bits Required per Conjugate Pair ---")
print(f"  {'Pair':<30} {'Bits':>10}")
print(f"  {'-'*30} {'-'*10}")
print(f"  {'Position (R/lp)':<30} {B_position:>10.2f}")
print(f"  {'Momentum (Planck)':<30} {B_momentum:>10.2f}")
print(f"  {'Time (age/tp)':<30} {B_time:>10.2f}")
print(f"  {'Energy (Ep/Emin)':<30} {B_energy:>10.2f}")
print(f"  {'Angular mom (Lmax/hbar)':<30} {B_angular:>10.2f}")

# --- 8. ASCII Visualization ---
print(f"\n--- 8. Precision Hierarchy (ASCII) ---")
print()
scales = [
    ("Planck length", lp),
    ("Proton radius", 8.75e-16),
    ("Atomic radius", 1e-10),
    ("Virus", 1e-7),
    ("Human", 1.7),
    ("Earth radius", 6.371e6),
    ("Solar system", 4.5e12),
    ("Milky Way", 9.5e20),
    ("Observable R", R_universe),
]

print("  Scale                  log2(x/lp)  Bits from Planck")
print("  " + "-" * 58)
max_bits = B_position
for name, val in scales:
    bits = math.log2(val / lp)
    bar_len = int(bits / max_bits * 40)
    print(f"  {name:<22} {bits:>7.1f}    {'|' + '#' * bar_len}")

print()
print(f"  Total dynamic range: {B_position:.1f} bits")
print(f"  = sigma(6) x 17 = 12 x 17 = 204 (rounded)")

# --- 9. 204 in TECS-L constant system ---
print(f"\n--- 9. TECS-L Constant System Connections ---")
print(f"  B = 204 = sigma(6) x A(pi)")
print(f"  where sigma(6) = 12 (sum of divisors of perfect number 6)")
print(f"  and   A(pi) = 17 (amplification at theta=pi, Fermat prime)")
print(f"")
print(f"  sigma(6) = 1+2+3+6 = 12")
print(f"  sigma_{{-1}}(6) = 1/1+1/2+1/3+1/6 = 2 (harmonic sum)")
print(f"  17 = 2^(2^2)+1 = Fermat prime F2")
print(f"")
print(f"  Connection chain:")
print(f"    Perfect number 6")
print(f"       |")
print(f"    sigma(6) = 12")
print(f"       |")
print(f"    x Fermat prime 17 = A(pi)")
print(f"       |")
print(f"    = 204 bits = Universe dynamic range")
print(f"       |")
print(f"    = Heisenberg uncertainty lower bound")
print(f"       |")
print(f"    Quantum mechanics!")
print(f"")
print(f"  Ad-hoc check:")
print(f"    B_exact = {B_position:.4f} (not exactly 204)")
print(f"    B_rounded = {round(B_position)}")
print(f"    Fractional part = {B_position - int(B_position):.4f}")
print(f"    Depends on R_universe = {R_universe:.2e} m (measured, ~10% uncertainty)")
print(f"    If R = 4.4e26 -> B = {math.log2(4.4e26/lp):.2f}")
print(f"    If R = 4.0e26 -> B = {math.log2(4.0e26/lp):.2f}")
print(f"    If R = 5.0e26 -> B = {math.log2(5.0e26/lp):.2f}")
print(f"    --> B ~ 203-205 depending on R. 204 is within range but not exact.")

# --- 10. Texas Sharpshooter check ---
print(f"\n--- 10. Texas Sharpshooter Analysis ---")
print(f"  Hypothesis: B = sigma(6) x 17")
print(f"  B_exact = {B_position:.4f}")
print(f"  Target = 204")
print(f"  Error = |{B_position:.4f} - 204| / 204 = {abs(B_position - 204)/204 * 100:.2f}%")
print(f"")
print(f"  How many 'interesting' factorizations could 204 have?")
interesting = []
for a in range(2, 204):
    if 204 % a == 0:
        b = 204 // a
        interesting.append(f"{a} x {b}")
print(f"  All factorizations of 204: {interesting}")
print(f"  Count: {len(interesting)} factorizations")
print(f"")
print(f"  If we allow B in range [200, 210] (due to R uncertainty):")
for test_b in range(200, 211):
    facs = [(a, test_b//a) for a in range(2, test_b) if test_b % a == 0]
    has_6 = any(a == 6 or b == 6 for a, b in facs)
    has_12 = any(a == 12 or b == 12 for a, b in facs)
    has_17 = any(a == 17 or b == 17 for a, b in facs)
    markers = []
    if has_6: markers.append("6|")
    if has_12: markers.append("12|")
    if has_17: markers.append("17|")
    print(f"    B={test_b}: div by {','.join(markers) if markers else 'none of 6,12,17'}")

print(f"\n  p-value estimate:")
print(f"  P(random integer near 204 is divisible by 12 AND 17) = 1/204 = {1/204:.4f}")
print(f"  But we chose 12 and 17 post-hoc from constants.")
print(f"  With ~10 'interesting' constants to try: p ~ 10/204 = {10/204:.3f}")
print(f"  --> Weak evidence. The 204 = 12x17 connection is SUGGESTIVE but not strong.")

print(f"\n{'=' * 70}")
print(f"VERDICT: Heisenberg uncertainty IS consistent with finite precision,")
print(f"but this is well-known (Planck scale = minimum resolution).")
print(f"The 204 = sigma(6) x 17 connection is numerically approximate")
print(f"and depends on the measured universe size (10% uncertainty).")
print(f"Grade: Ad-hoc warning due to R_universe dependence.")
print(f"{'=' * 70}")
