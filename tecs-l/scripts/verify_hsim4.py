#!/usr/bin/env python3
"""H-SIM-4: Speed of Light = Maximum Clock Speed
Verify that c = lp/tp and explore computational implications."""

import math

print("=" * 70)
print("H-SIM-4: Speed of Light = Maximum Clock Speed")
print("=" * 70)

# --- Physical Constants ---
hbar = 1.054571817e-34    # Reduced Planck constant (J·s)
c = 2.99792458e8          # Speed of light (m/s)
G = 6.67430e-11           # Gravitational constant
lp = math.sqrt(hbar * G / c**3)  # Planck length
tp = math.sqrt(hbar * G / c**5)  # Planck time
mp = math.sqrt(hbar * c / G)     # Planck mass
Ep = mp * c**2                     # Planck energy

print(f"\n--- Planck Units ---")
print(f"  lp = {lp:.6e} m")
print(f"  tp = {tp:.6e} s")
print(f"  mp = {mp:.6e} kg")
print(f"  Ep = {Ep:.6e} J")

# --- 1. c = lp/tp verification ---
print(f"\n--- 1. Verify c = lp/tp ---")
c_from_planck = lp / tp
print(f"  c (defined)   = {c:.10e} m/s")
print(f"  lp / tp       = {c_from_planck:.10e} m/s")
print(f"  Difference     = {abs(c - c_from_planck):.3e} m/s")
print(f"  Relative error = {abs(c - c_from_planck)/c:.3e}")
print(f"  --> c = lp/tp EXACTLY (by definition of Planck units)")
print(f"  --> In Planck units: c = 1 cell / 1 tick = 1")
print(f"  Interpretation: light travels exactly 1 Planck length per Planck time")
print(f"  This IS the 'grid speed' of a cellular automaton on Planck lattice")

# --- 2. c in Planck units ---
print(f"\n--- 2. Planck Unit System (Natural Units) ---")
print(f"  In Planck units:")
print(f"    c = 1  (by definition)")
print(f"    hbar = 1  (by definition)")
print(f"    G = 1  (by definition)")
print(f"    lp = 1  (length unit)")
print(f"    tp = 1  (time unit)")
print(f"  --> The entire framework where c=hbar=G=1 is equivalent to")
print(f"      saying the simulator uses Planck-scale grid with speed=1")

# --- 3. Causal structure = BFS wavefront ---
print(f"\n--- 3. Causal Structure = BFS on Grid ---")
print(f"  Light cone in 1+1D spacetime:")
print(f"  (Planck units, c=1)")
print()
print(f"         t")
print(f"         ^")
print(f"     5   |   *           *")
print(f"     4   |    *         *")
print(f"     3   |     *       *")
print(f"     2   |      *     *")
print(f"     1   |       *   *")
print(f"     0   +--------*---------> x")
print(f"              -5  0  5")
print(f"")
print(f"  Each tick: wavefront expands by exactly 1 cell")
print(f"  This IS Breadth-First Search on a grid graph!")
print(f"  BFS wavefront speed = 1 cell/tick = c in Planck units")

# --- 4. Universe operations per second ---
print(f"\n--- 4. Universe Computational Capacity ---")
R = 4.4e26  # Observable universe radius (m)
N_cells = R / lp
print(f"  Observable universe radius = {R:.2e} m")
print(f"  Number of cells along 1 axis: R/lp = {N_cells:.3e}")
print(f"  N_cells^3 (spatial volume) = {N_cells**3:.3e}")
print(f"  Clock rate = 1/tp = {1/tp:.3e} ticks/s")

ops_per_sec = (N_cells**3) / tp
print(f"\n  Grid operations per second:")
print(f"    N_ops = N_cells^3 / tp = {ops_per_sec:.3e} ops/s")
print(f"    log10(N_ops) = {math.log10(ops_per_sec):.1f}")

# --- 5. Bremermann limit ---
print(f"\n--- 5. Bremermann Limit Comparison ---")
bremermann_per_kg = c**2 / hbar
M_universe = 1.5e53  # kg
bremermann_total = bremermann_per_kg * M_universe
print(f"  Bremermann limit = c^2/hbar = {bremermann_per_kg:.3e} ops/s/kg")
print(f"  Universe mass = {M_universe:.2e} kg")
print(f"  Total Bremermann = {bremermann_total:.3e} ops/s")
print(f"  log10(Bremermann_total) = {math.log10(bremermann_total):.1f}")
print(f"\n  Grid ops / Bremermann = {ops_per_sec / bremermann_total:.3e}")

if ops_per_sec < bremermann_total:
    print(f"  --> Grid ops < Bremermann limit: simulation is WITHIN BUDGET")
elif ops_per_sec > bremermann_total:
    print(f"  --> Grid ops > Bremermann limit: simulation EXCEEDS budget!")
    print(f"      Ratio = {ops_per_sec / bremermann_total:.2e}")

# Lloyd limit (different formulation)
print(f"\n  Lloyd limit (2000):")
E_universe = M_universe * c**2
lloyd_total = 2 * E_universe / (math.pi * hbar)
print(f"  S_Lloyd = 2*E/(pi*hbar) = {lloyd_total:.3e} ops/s")
print(f"  log10(Lloyd) = {math.log10(lloyd_total):.1f}")
print(f"  Grid ops / Lloyd = {ops_per_sec / lloyd_total:.3e}")

# --- 6. Bekenstein bound ---
print(f"\n--- 6. Bekenstein Bound (Maximum Information) ---")
k_B = 1.380649e-23  # Boltzmann constant
I_bekenstein = 2 * math.pi * R * M_universe * c / (hbar * math.log(2))
print(f"  I_Bekenstein = 2*pi*R*M*c/(hbar*ln2) = {I_bekenstein:.3e} bits")
print(f"  log10(I_Bekenstein) = {math.log10(I_bekenstein):.1f}")
B_grid = 3 * math.log2(N_cells)  # bits to specify one grid point
total_grid_bits = N_cells**3  # one bit per cell (minimum)
print(f"  Grid bits (1 bit/cell) = N^3 = {total_grid_bits:.3e}")
print(f"  log10(grid_bits) = {math.log10(total_grid_bits):.1f}")
print(f"  Bekenstein / Grid = {I_bekenstein / total_grid_bits:.3e}")

# --- 7. c^(1/6) and c^(1/sigma(6)) ---
print(f"\n--- 7. Powers of c ---")
print(f"  c = {c:.6e} m/s")
print(f"  c^(1/6) = {c**(1/6):.6f}")
print(f"  c^(1/12) = c^(1/sigma(6)) = {c**(1/12):.6f}")
print(f"  c^(1/2) = {c**(1/2):.6f}")
print(f"  c^(1/3) = {c**(1/3):.6f}")
print(f"  c^(1/17) = {c**(1/17):.6f}")
print(f"  c^(6/17) = {c**(6/17):.6f}")
print(f"  ln(c) = {math.log(c):.6f}")
print(f"  log10(c) = {math.log10(c):.6f}")
print(f"  log2(c) = {math.log2(c):.6f}")

# Check if any power is "nice"
print(f"\n  Checking for 'nice' values:")
for n in [2, 3, 5, 6, 7, 12, 17, 34, 204]:
    val = c**(1/n)
    # Check if close to integer or simple fraction
    nearest_int = round(val)
    frac = val - int(val)
    print(f"    c^(1/{n:>3}) = {val:>15.4f}  (frac part: {frac:.4f})")

# --- 8. Lorentz factor in grid terms ---
print(f"\n--- 8. Lorentz Invariance = Computational Consistency ---")
print(f"  If simulator has grid speed c_grid = 1 (Planck units):")
print(f"  Then maximum information speed = 1 cell/tick")
print(f"  Lorentz factor gamma = 1/sqrt(1 - v^2/c^2)")
print(f"  In grid units: gamma = 1/sqrt(1 - v_grid^2)")
print()
print(f"  v_grid   gamma    time_dilation")
print(f"  -------  -------  -------------")
for v_frac in [0.0, 0.1, 0.5, 0.8, 0.9, 0.99, 0.999, 0.9999]:
    if v_frac < 1:
        gamma = 1 / math.sqrt(1 - v_frac**2)
        print(f"  {v_frac:>7.4f}  {gamma:>7.3f}  {1/gamma:>13.6f}")

print(f"\n  At v=c: gamma -> infinity, time stops")
print(f"  Interpretation: at grid speed, all computation budget is spent on movement")
print(f"  No 'ticks' left for internal state evolution = time dilation")

# --- 9. Operations comparison ASCII ---
print(f"\n--- 9. Computational Scale Comparison (ASCII) ---")
print()
items = [
    ("Human brain (ops/s)", 1e16),
    ("Frontier (2024)", 1.7e18),
    ("All computers on Earth", 1e21),
    ("Bremermann (1 kg)", bremermann_per_kg),
    ("Lloyd (universe)", lloyd_total),
    ("Bremermann (universe)", bremermann_total),
    ("Grid ops (universe)", ops_per_sec),
]

max_log = max(math.log10(v) for _, v in items)
print(f"  {'System':<28} {'log10(ops/s)':>12}  Bar")
print(f"  {'-'*28} {'-'*12}  {'-'*40}")
for name, val in items:
    log_val = math.log10(val)
    bar_len = int(log_val / max_log * 40)
    print(f"  {name:<28} {log_val:>12.1f}  {'#' * bar_len}")

# --- 10. Speed of light special values ---
print(f"\n--- 10. c in Various Unit Systems ---")
print(f"  c = {c:.6e} m/s  (SI)")
print(f"  c = 1 lp/tp         (Planck -- EXACT)")
print(f"  c = 1               (natural units)")
print(f"  c = 299792458 m/s   (exact by SI definition since 2019)")
print(f"  c = 299792.458 km/s")
print(f"  ")
print(f"  299792458 factorization:")
c_int = 299792458
temp = c_int
c_factors = []
for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
    while temp % p == 0:
        c_factors.append(p)
        temp //= p
if temp > 1:
    c_factors.append(temp)
print(f"  299792458 = {' x '.join(map(str, c_factors))}")
print(f"  (Note: c_SI is human-defined, not fundamental)")

# --- 11. Summary ---
print(f"\n{'=' * 70}")
print(f"SUMMARY")
print(f"{'=' * 70}")
print(f"")
print(f"  1. c = lp/tp is EXACT (by definition of Planck units)")
print(f"     This is a tautology, not a discovery.")
print(f"     BUT: the interpretation as 'grid speed = 1' is physically meaningful.")
print(f"")
print(f"  2. Grid operations = {ops_per_sec:.2e} ops/s")
print(f"     vs Bremermann    = {bremermann_total:.2e} ops/s")
print(f"     Ratio = {ops_per_sec/bremermann_total:.2e}")
if ops_per_sec > bremermann_total:
    print(f"     --> Grid ops EXCEED Bremermann! The universe cannot simulate itself.")
    print(f"         This is consistent: a simulator must be LARGER than the simulated.")
else:
    print(f"     --> Grid ops within Bremermann budget.")
print(f"")
print(f"  3. Lorentz invariance as computational constraint:")
print(f"     If max speed = 1 cell/tick, then relativity follows from")
print(f"     the requirement of computational consistency.")
print(f"     This is the digital physics interpretation (Zuse, Fredkin, Wolfram).")
print(f"")
print(f"  4. c^(1/n) yields no 'nice' numbers for n = 6, 12, 17, etc.")
print(f"     c in SI is human-defined (meter, second are human constructs).")
print(f"     In Planck units, c = 1. The 'magic' is in the unit choice.")
print(f"")
print(f"  GRADE: The c = lp/tp = 1 observation is well-known (Planck, 1899).")
print(f"  The grid/BFS interpretation is valid but not new (Zuse 1969).")
print(f"  The Bremermann comparison gives an interesting constraint.")
print(f"  No new TECS-L-specific constant connections found for c.")
print(f"{'=' * 70}")
