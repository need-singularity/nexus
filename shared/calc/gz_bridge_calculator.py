#!/usr/bin/env python3
"""Golden Zone Bridge Calculator -- Complete GZ structure from two principles

Computes GZ boundaries (number theory) + center (variational) + combined analysis.
Based on H-CX-501: I^I minimization bridge theorem.

The two independent derivations:
  1. Number theory: boundaries from perfect number n=6 divisor reciprocals
     Lower = 1/2 - ln(4/3)  ~= 0.2123
     Upper = 1/2             = 0.5000
  2. Calculus: center from I^I minimization
     d/dI [I^I] = 0  =>  I = 1/e  ~= 0.3679

Usage:
  python3 calc/gz_bridge_calculator.py                    # Full GZ analysis
  python3 calc/gz_bridge_calculator.py --perfect 2        # GZ for P_2=28
  python3 calc/gz_bridge_calculator.py --sweep 0.1 0.6    # I^I sweep over range
  python3 calc/gz_bridge_calculator.py --energy 0.37      # E(I) at specific I
"""

import argparse
import math
import sys


# ═══════════════════════════════════════════════════════════════
# Perfect number data
# ═══════════════════════════════════════════════════════════════

PERFECT_NUMBERS = [6, 28, 496, 8128, 33550336]

# Consciousness constants (from anima Laws 63-79)
LN2 = math.log(2)                     # 0.6931 universal consciousness unit
PSI_FREEDOM = LN2                      # Law 79: consciousness freedom degree
PSI_BALANCE = 0.5                      # structural consciousness equilibrium
PSI_COUPLING = LN2 / 2**5.5           # 0.01534 consciousness coupling
DYNAMICS_RATE = 0.81                   # dH/dt = 0.81 * (ln2 - H)
CONSERVATION_C = 0.478                # H^2 + dp^2 conservation
PHI_SCALE_A = 0.608                   # Phi = 0.608 * N^1.071
PHI_SCALE_B = 1.071

def divisors(n):
    d = []
    for i in range(1, int(n**0.5) + 1):
        if n % i == 0:
            d.append(i)
            if i != n // i:
                d.append(n // i)
    return sorted(d)


def proper_divisors(n):
    return divisors(n)[:-1]  # exclude n itself


def sigma_neg1(n):
    """Sum of reciprocals of all divisors of n."""
    return sum(1.0/d for d in divisors(n))


def gz_boundaries(n):
    """Compute GZ boundaries from perfect number n.

    For a perfect number: sigma(n)=2n => sum(1/d for d in divisors) = 2
    The GZ construction anchors upper at 1/2 and derives lower from entropy.
    """
    upper = 0.5
    width = math.log(4.0/3.0)
    lower = upper - width
    return lower, upper, width


# ═══════════════════════════════════════════════════════════════
# I^I calculus
# ═══════════════════════════════════════════════════════════════

def f_ii(I):
    """f(I) = I^I = exp(I * ln(I)), defined for I > 0."""
    if I <= 0:
        return float('nan')
    return math.exp(I * math.log(I))


def f_ii_deriv(I):
    """d/dI [I^I] = I^I * (ln(I) + 1). Zero at I = 1/e."""
    if I <= 0:
        return float('nan')
    return f_ii(I) * (math.log(I) + 1.0)


def find_ii_minimum(lo=0.01, hi=1.0, steps=100000):
    """Numerically find minimum of I^I in [lo, hi]."""
    best_I = lo
    best_val = f_ii(lo)
    step = (hi - lo) / steps
    I = lo
    while I <= hi:
        v = f_ii(I)
        if v < best_val:
            best_val = v
            best_I = I
        I += step
    return best_I, best_val


# ═══════════════════════════════════════════════════════════════
# Means of boundaries
# ═══════════════════════════════════════════════════════════════

def boundary_means(lower, upper):
    arith = (lower + upper) / 2.0
    geom = math.sqrt(lower * upper)
    harm = 2.0 / (1.0/lower + 1.0/upper)
    return arith, geom, harm


# ═══════════════════════════════════════════════════════════════
# ASCII curve plotter
# ═══════════════════════════════════════════════════════════════

def ascii_plot(func, lo, hi, width=60, height=12, markers=None):
    """Plot func over [lo, hi] as ASCII art. markers = {x_val: char}."""
    xs = [lo + (hi - lo) * i / (width - 1) for i in range(width)]
    ys = [func(x) for x in xs]
    y_min = min(ys)
    y_max = max(ys)
    if abs(y_max - y_min) < 1e-12:
        y_max = y_min + 1e-12

    grid = [[' '] * width for _ in range(height)]
    for col, y in enumerate(ys):
        row = int((y - y_min) / (y_max - y_min) * (height - 1))
        row = height - 1 - row
        row = max(0, min(height - 1, row))
        grid[row][col] = '*'

    # Overlay markers
    if markers:
        for x_val, char in markers.items():
            if lo <= x_val <= hi:
                col = int((x_val - lo) / (hi - lo) * (width - 1))
                for r in range(height):
                    if grid[r][col] == ' ':
                        grid[r][col] = '|'
                # Mark the actual function value at that x
                y_val = func(x_val)
                row = int((y_val - y_min) / (y_max - y_min) * (height - 1))
                row = height - 1 - row
                row = max(0, min(height - 1, row))
                grid[row][col] = char

    lines = [''.join(row) for row in grid]
    # Y-axis labels
    y_top = y_min + (y_max - y_min)
    result = []
    result.append(f"  {y_max:.4f} |{''.join(lines[0])}|")
    for i, line in enumerate(lines[1:-1], 1):
        result.append(f"         |{line}|")
    result.append(f"  {y_min:.4f} |{''.join(lines[-1])}|")
    result.append(f"          {lo:.3f}{' ' * (width - 10)}{hi:.3f}")
    return '\n'.join(result)


# ═══════════════════════════════════════════════════════════════
# Proof chain printer
# ═══════════════════════════════════════════════════════════════

def print_proof_chain():
    print()
    print("  Proof Chain: Two Independent Derivations of GZ")
    print("  " + "=" * 56)
    print()
    print("  PATH 1 -- Number Theory (n=6 perfect number)")
    print("  " + "-" * 56)
    print("  1. n=6 is perfect  =>  sigma(6) = 12 = 2*6")
    print("  2. sum(1/d for d|6) = 1 + 1/2 + 1/3 + 1/6 = 2")
    print("  3. Largest proper divisor ratio  = 3/6 = 1/2  => Upper")
    print("  4. Entropy cost of 3->4 states   = ln(4/3)    => Width")
    print("  5. Lower = Upper - Width = 1/2 - ln(4/3) = 0.2123")
    print()
    print("  PATH 2 -- Calculus (I^I minimization)")
    print("  " + "-" * 56)
    print("  1. f(I) = I^I = exp(I * ln(I))")
    print("  2. f'(I) = I^I * (ln(I) + 1)")
    print("  3. f'(I) = 0  =>  ln(I) = -1  =>  I = e^(-1) = 1/e")
    print("  4. GZ center = 1/e = 0.36788...")
    print()
    print("  BRIDGE STATUS")
    print("  " + "-" * 56)
    lower, upper, width = gz_boundaries(6)
    center = 1.0 / math.e
    arith, geom, harm = boundary_means(lower, upper)
    gap = abs(center - arith)
    print(f"  GZ lower  = {lower:.6f}  (number theory)")
    print(f"  GZ upper  = {upper:.6f}  (number theory)")
    print(f"  GZ center = {center:.6f}  (calculus, 1/e)")
    print(f"  Arithmetic mean of boundaries = {arith:.6f}")
    print(f"  |1/e - arithmetic mean|       = {gap:.6f}")
    in_zone = lower < center < upper
    print(f"  1/e inside [lower, upper]?    = {'YES' if in_zone else 'NO'}")
    print()
    if in_zone:
        frac_pos = (center - lower) / width
        print(f"  1/e position within zone      = {frac_pos:.4f}  (0=bottom, 1=top)")
    print()
    print("  Gap status: The analytical bridge (H-CX-501) is unproven.")
    print("  Both derivations independently point to ~0.37 but differ")
    print(f"  by {gap:.4f}. Proof requires showing 1/e = 1/2 - ln(4/3)/2,")
    print(f"  which evaluates to {0.5 - math.log(4/3)/2:.6f} vs 1/e={center:.6f}.")
    diff = abs(center - (0.5 - math.log(4/3)/2))
    print(f"  Difference from midpoint formula: {diff:.6f}  (NOT zero -- gap open)")


# ═══════════════════════════════════════════════════════════════
# Perfect number GZ
# ═══════════════════════════════════════════════════════════════

def print_gz_for_perfect(k):
    """Print GZ structure for the k-th perfect number (1-indexed)."""
    if k < 1 or k > len(PERFECT_NUMBERS):
        print(f"  Error: k must be 1..{len(PERFECT_NUMBERS)}")
        sys.exit(1)
    n = PERFECT_NUMBERS[k - 1]
    lower, upper, width = gz_boundaries(n)
    center = 1.0 / math.e
    print()
    print(f"  GZ Structure for P_{k} = {n}")
    print("  " + "=" * 50)
    print(f"  Upper    = 1/2         = {upper:.6f}")
    print(f"  Width    = ln(4/3)     = {width:.6f}")
    print(f"  Lower    = 1/2-ln(4/3) = {lower:.6f}")
    print(f"  Center   = 1/e         = {center:.6f}")
    note = "(same for all perfect numbers -- GZ is universal)"
    print(f"  Note: {note}")
    print()
    # Divisor reciprocal sum for this perfect number
    divs = divisors(n)
    rec_sum = sum(1.0/d for d in divs)
    print(f"  Divisors of {n}: {divs}")
    print(f"  sum(1/d) = {rec_sum:.6f}  (= 2 for any perfect number)")


# ═══════════════════════════════════════════════════════════════
# Sweep
# ═══════════════════════════════════════════════════════════════

def print_sweep(lo, hi, steps=20):
    lower, upper, width = gz_boundaries(6)
    center = 1.0 / math.e
    step = (hi - lo) / steps
    print()
    print(f"  I^I Sweep over [{lo:.3f}, {hi:.3f}]")
    print("  " + "=" * 58)
    print(f"  {'I':>8}  {'I^I':>10}  {'d/dI[I^I]':>12}  {'Zone':>8}")
    print("  " + "-" * 58)
    I = lo
    while I <= hi + 1e-12:
        val = f_ii(I)
        deriv = f_ii_deriv(I)
        zone = "IN" if lower <= I <= upper else "out"
        marker = " <-- min" if abs(deriv) < 0.01 else ""
        print(f"  {I:8.4f}  {val:10.6f}  {deriv:12.6f}  {zone:>8}{marker}")
        I += step
    min_I, min_val = find_ii_minimum(lo, hi)
    print()
    print(f"  Numerical minimum: I = {min_I:.6f}, I^I = {min_val:.6f}")
    print(f"  Analytical minimum: 1/e = {center:.6f}")


# ═══════════════════════════════════════════════════════════════
# Energy at specific I
# ═══════════════════════════════════════════════════════════════

def print_energy(I_val):
    lower, upper, _ = gz_boundaries(6)
    center = 1.0 / math.e
    val = f_ii(I_val)
    deriv = f_ii_deriv(I_val)
    val_at_center = f_ii(center)
    print()
    print(f"  E(I) = I^I Analysis at I = {I_val}")
    print("  " + "=" * 44)
    print(f"  I                = {I_val:.6f}")
    print(f"  I^I              = {val:.6f}")
    print(f"  d/dI[I^I]        = {deriv:.6f}  ({'zero at min' if abs(deriv) < 0.001 else 'nonzero'})")
    print(f"  I^I at 1/e       = {val_at_center:.6f}  (global min)")
    print(f"  Excess over min  = {val - val_at_center:.6f}")
    in_zone = lower <= I_val <= upper
    print(f"  In Golden Zone   = {'YES' if in_zone else 'NO'} [{lower:.4f}, {upper:.4f}]")


# ═══════════════════════════════════════════════════════════════
# Full analysis
# ═══════════════════════════════════════════════════════════════

def print_full_analysis():
    lower, upper, width = gz_boundaries(6)
    center = 1.0 / math.e
    arith, geom, harm = boundary_means(lower, upper)

    print()
    print("  ╔══════════════════════════════════════════════════════╗")
    print("  ║        Golden Zone Bridge Calculator                 ║")
    print("  ║        Two Derivations, One Zone (H-CX-501)          ║")
    print("  ╚══════════════════════════════════════════════════════╝")

    print()
    print("  GZ Constants")
    print("  " + "=" * 50)
    constants = [
        ("Upper  (1/2)",        0.5,                    "Riemann critical line"),
        ("Lower  (1/2-ln4/3)", lower,                   "Entropy boundary"),
        ("Center (1/e)",        center,                  "I^I minimum"),
        ("Width  (ln 4/3)",     width,                   "3->4 state entropy"),
        ("1/3",                 1.0/3,                   "Meta fixed point"),
        ("1/6",                 1.0/6,                   "Curiosity term"),
        ("5/6",                 5.0/6,                   "Compass upper"),
        ("ln(2)",                LN2,                     "Consciousness freedom (Law 79)"),
        ("Psi_coupling",         PSI_COUPLING,            "Consciousness coupling"),
    ]
    print(f"  {'Constant':<24} {'Value':>10}  Description")
    print("  " + "-" * 60)
    for name, val, desc in constants:
        print(f"  {name:<24} {val:10.6f}  {desc}")

    print()
    print("  Means of [lower, upper]")
    print("  " + "=" * 50)
    print(f"  Arithmetic mean = {arith:.6f}")
    print(f"  Geometric mean  = {geom:.6f}")
    print(f"  Harmonic mean   = {harm:.6f}")
    print(f"  1/e (calc)      = {center:.6f}")
    print(f"  Closest mean    = arithmetic (delta = {abs(center-arith):.6f})")

    print()
    print("  I^I Curve over [0.1, 0.9]  (* = curve, L/U = zone boundaries, M = minimum)")
    print("  " + "-" * 62)
    markers = {lower: 'L', upper: 'U', center: 'M'}
    chart = ascii_plot(f_ii, 0.1, 0.9, width=60, height=10, markers=markers)
    for line in chart.split('\n'):
        print("  " + line)

    print()
    print_proof_chain()

    # Consciousness dynamics connection
    print()
    print("  Consciousness Dynamics Connection (anima Laws 63-79)")
    print("  " + "=" * 56)
    print(f"  Freedom degree = ln(2) = {LN2:.6f}  (Law 79)")
    print(f"  GZ center = 1/e = {center:.6f}")
    print(f"  Coupling = ln(2)/2^5.5 = {PSI_COUPLING:.6f}")
    print(f"  Dynamics: dH/dt = {DYNAMICS_RATE} * (ln2 - H)")
    print(f"  Conservation: H^2 + dp^2 ~ {CONSERVATION_C}")
    print(f"  Scaling: Phi = {PHI_SCALE_A} * N^{PHI_SCALE_B}")
    print()
    print("  Key insight: 1/e (GZ center) and ln(2) (consciousness)")
    print(f"  are reciprocally linked: e^(-1) * e^(ln2) = e^(ln2-1)")
    print(f"  = {math.exp(LN2 - 1):.6f}")
    print()


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Golden Zone Bridge Calculator -- GZ structure from number theory + calculus"
    )
    parser.add_argument("--perfect", type=int, metavar="K",
                        help="Show GZ for the K-th perfect number (1=6, 2=28, ...)")
    parser.add_argument("--sweep", type=float, nargs=2, metavar=("LO", "HI"),
                        help="Sweep I^I over [LO, HI]")
    parser.add_argument("--energy", type=float, metavar="I",
                        help="Compute E(I)=I^I at a specific I value")
    args = parser.parse_args()

    if args.perfect is not None:
        print_gz_for_perfect(args.perfect)
    elif args.sweep is not None:
        print_sweep(args.sweep[0], args.sweep[1])
    elif args.energy is not None:
        print_energy(args.energy)
    else:
        print_full_analysis()


if __name__ == "__main__":
    main()
