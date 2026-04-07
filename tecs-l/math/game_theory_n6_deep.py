"""
Deep analysis of game theory findings for n=6.
Texas Sharpshooter verification + additional connections.
"""

import math
import itertools
from fractions import Fraction
import random

print("=" * 70)
print("DEEP ANALYSIS: Game Theory n=6 Findings")
print("=" * 70)

n = 6
sigma = 12
phi_euler = 2
tau = 4
sopfr = 5
divisors = [1, 2, 3, 6]

# ============================================================
# FINDING 1: Banzhaf [12; 1,2,3,6] -> equal power = 1/tau
# ============================================================
print("\n=== FINDING 1: Banzhaf symmetry ===")
print("Game [12; 1,2,3,6]: all players Banzhaf = 1/4 = 1/tau(6)")
print()
print("WHY? At quota = total_weight = sigma(6) = 12:")
print("Only the full coalition {1,2,3,6} achieves weight >= quota")
print("So each player is a swing voter in exactly 1 winning coalition")
print("(the grand coalition minus any player fails to meet quota)")
print()
# Verify: the grand coalition has weight 12 = quota
# Remove any player: weights become 11, 10, 9, 6 -> all < 12
# So every player is critical in EXACTLY the grand coalition
print("Grand coalition weight = 12 = quota = sigma(6)")
for i, w in enumerate(divisors):
    remaining = sum(divisors) - w
    print(f"  Remove player {i+1} (w={w}): remaining = {remaining} {'< quota -> CRITICAL' if remaining < 12 else '>= quota -> not critical'}")

print(f"\nResult: Banzhaf(player_i) = 1 swing each")
print(f"  Normalized: 1/4 = 1/tau(6) for ALL players")
print(f"\nGrade: GREEN (exact, forced by structure)")
print(f"  Claim: When quota = sigma(n), Banzhaf = 1/tau(n) for each player")

# Verify for n=28 (next perfect number)
print("\n--- Generalization to n=28 ---")
divisors_28 = [1, 2, 4, 7, 14, 28]
sigma_28 = sum(divisors_28)
tau_28 = len(divisors_28)
print(f"n=28: divisors={divisors_28}, sigma={sigma_28}, tau={tau_28}")
print(f"Game [{sigma_28}; {divisors_28}]")

# At quota = sigma_28, only grand coalition wins
# So each player is critical in exactly 1 winning coalition
print(f"At quota = {sigma_28} = sigma(28):")
for i, w in enumerate(divisors_28):
    remaining = sigma_28 - w
    print(f"  Remove player (w={w}): remaining = {remaining} {'< quota -> CRITICAL' if remaining < sigma_28 else '>= quota'}")

print(f"\nSame result: Banzhaf = 1/tau(28) = 1/{tau_28} for all players")
print(f"Generalizes to ANY perfect number n!")
print(f"Because sigma(n) - d_i = sigma(n) - d_i < sigma(n) for all proper divisors d_i")
print(f"(trivially true since all weights are positive)")

# ============================================================
# FINDING 2: Shapley symmetry at quota = sigma
# ============================================================
print("\n\n=== FINDING 2: Shapley at quota = sigma(6) ===")
print("Game [12; 1,2,3,6]: all players Shapley = 1/4 = 1/tau(6)")
print()
print("This is also forced: at quota = total weight,")
print("the last player in any permutation is ALWAYS pivotal")
print("(since no proper subset reaches the quota)")
print()
print("Proof: In any ordering, the pivot is always the last player added")
print("So each player is pivot for exactly (n-1)! permutations out of n!")
print(f"Shapley = (tau-1)!/tau! = 1/tau = 1/{tau}")
print()
print("This holds for ANY game where quota = total weight!")
print("Not specific to n=6... but the connection:")
print(f"  quota = sigma(6) = total weight = 12")
print(f"  Shapley = 1/tau(6) = 1/4 = 0.25")
print(f"  This is guaranteed by perfect number structure: sigma(n) = sum(divisors)")

# ============================================================
# FINDING 3: Shapley at quota = 6 or 7
# ============================================================
print("\n\n=== FINDING 3: Shapley at quota = n = 6 ===")
print("Game [6; 1,2,3,6]: Shapley values")
# Already computed: at quota 6 and 7, Shapley(w=6) = 3/4, others = 1/12

print(f"  Shapley(w=6) = 3/4")
print(f"  Shapley(w=1) = Shapley(w=2) = Shapley(w=3) = 1/12")
print()
print(f"  Ratio: 3/4 vs 1/12 -> player w=6 has 9x more power than w=1")
print(f"  Why 9? Let's analyze...")

# The player with weight 6 = n can single-handedly reach quota 6
# Without player w=6: max achievable = 1+2+3 = 6 = quota, so just barely
print(f"  Weight 6 alone = 6 >= quota 6: player 4 is a DICTATOR at quota=6!")
print(f"  Wait - weight 6 alone meets quota exactly.")
print()
# At quota 6, player 4 alone wins
# At quota 7, player 4 alone (weight 6) can't win, needs help
print(f"  At quota 7: player 4 (w=6) alone = 6 < 7, needs help")
print(f"  Shapley(w=6) = 3/4 still! Let's verify why...")

# Actually, the formula gives 3/4 for quotas 6 and 7 both
# Let's look at quota 6 vs 7 difference
def shapley_value_detail(weights, quota):
    """Compute Shapley values with detailed analysis."""
    n_players = len(weights)
    shapley = [Fraction(0) for _ in range(n_players)]
    pivot_count = [0] * n_players

    for perm in itertools.permutations(range(n_players)):
        cumulative = 0
        for pos, player in enumerate(perm):
            cumulative += weights[player]
            prev_cumulative = cumulative - weights[player]
            if prev_cumulative < quota <= cumulative:
                shapley[player] += Fraction(1, math.factorial(n_players))
                pivot_count[player] += 1
                break

    return shapley, pivot_count

print("\n--- Shapley analysis at quota=6 ---")
sv6, pc6 = shapley_value_detail(divisors, 6)
total_perms = math.factorial(len(divisors))
for i, (w, s, c) in enumerate(zip(divisors, sv6, pc6)):
    print(f"  Player {i+1} (w={w}): pivot in {c}/{total_perms} permutations = {s}")

print("\n--- Shapley analysis at quota=7 ---")
sv7, pc7 = shapley_value_detail(divisors, 7)
for i, (w, s, c) in enumerate(zip(divisors, sv7, pc7)):
    print(f"  Player {i+1} (w={w}): pivot in {c}/{total_perms} permutations = {s}")

# Note: quota 6 and 7 give same results because weight 6 alone = 6 >= 6
# but we need to check actual computations
print()
print(f"  Note: quotas 6 and 7 give identical Shapley values!")
print(f"  This is because the 'crossing threshold' structure is the same")
print(f"  Player 4 (w=6): needs only itself for q=6, but this equals quota exactly")
print(f"  The boundary case q=6=w_4 means player 4 is pivotal in same permutations")

# ============================================================
# FINDING 4: Nash equilibria connection
# ============================================================
print("\n\n=== FINDING 4: Nash Equilibria ===")
print("E[pure NE] in random n×n game (simulation result): ~1.0 (not sqrt(pi*n/2))")
print()
print("The formula sqrt(pi*n/2) is for MIXED strategy Nash equilibria!")
print("For pure strategy NE: E[pure NE in n×n game] -> 1 as n -> infinity")
print("For mixed strategy NE: E[total NE] ~ sqrt(pi*n/2)")
print()
print("At n=6:")
print(f"  E[mixed NE] ~ sqrt(pi*6/2) = sqrt(3*pi) = {math.sqrt(3*math.pi):.6f}")
print(f"  sigma(6)/tau(6) = 12/4 = 3 (exact)")
print(f"  sqrt(3*pi) - 3 = {math.sqrt(3*math.pi) - 3:.6f} ({(math.sqrt(3*math.pi)-3)/3*100:.2f}% off)")
print()

# Is this a coincidence? Texas test
# Compare: sqrt(pi*n/2) vs sigma(n)/tau(n) for first few perfect numbers
print("--- Checking for other perfect numbers ---")
for (nn, sig, t) in [(6, 12, 4), (28, 56, 6), (496, 992, 10)]:
    ne_formula = math.sqrt(math.pi * nn / 2)
    ratio = sig / t
    diff_pct = abs(ne_formula - ratio) / ratio * 100
    print(f"  n={nn}: sqrt(pi*{nn}/2)={ne_formula:.4f}, sigma/tau={sig}/{t}={ratio:.4f}, diff={diff_pct:.2f}%")

print()
print("Is there a reason sigma/tau should equal sqrt(pi*n/2)?")
print("For even perfect numbers: sigma(n) = 2n (from Euler's formula)")
print("tau(n) = 2k for n = 2^(k-1)*(2^k-1)")
print(f"sigma/tau = 2n/(2k) = n/k")
print()
print("Perfect number formula: n = 2^(p-1)*(2^p-1) where 2^p-1 is prime")
print(f"n=6: p=2, k=2, sigma/tau = 6/2 = 3")
print(f"n=28: p=3, k=3, sigma/tau = 28/3 = 9.33...")
print(f"sqrt(pi*6/2)=3.07 vs sigma/tau(6)=3: coincidental near-match for n=6 only")

# ============================================================
# FINDING 5: XOR(divisors of 6) = 6
# ============================================================
print("\n\n=== FINDING 5: XOR(divisors) = n ===")
print("XOR(1, 2, 3, 6) = 6 = n")
print()

# Check for other numbers
print("--- Checking all numbers 1..30 ---")
matches = []
for num in range(1, 50):
    divs = [d for d in range(1, num+1) if num % d == 0]
    xor_val = 0
    for d in divs:
        xor_val ^= d
    if xor_val == num:
        matches.append((num, divs, xor_val))

print(f"Numbers where XOR(divisors) = n:")
for (num, divs, xv) in matches:
    print(f"  n={num}: divisors={divs}, XOR={xv}")

print()
print(f"n=6 is {'among them' if any(m[0]==6 for m in matches) else 'NOT among them'}")

# Perfect numbers: check
perf_check = [(6, [1,2,3,6]), (28, [1,2,4,7,14,28])]
for (pn, pdivs) in perf_check:
    xv = 0
    for d in pdivs:
        xv ^= d
    print(f"Perfect n={pn}: XOR(divisors) = {xv} {'= n' if xv == pn else f'!= {pn}'}")

# ============================================================
# FINDING 6: Wythoff position (2,3) analysis
# ============================================================
print("\n\n=== FINDING 6: Wythoff (2,3) = (phi(6), sigma/tau(6)) ===")
phi_golden = (1 + math.sqrt(5)) / 2
print(f"  (2,3) is NOT a Wythoff P-position (Grundy = 5, winning)")
print()
print(f"  The Wythoff P-positions near (2,3):")
print(f"  k=1: (1,2) -> Grundy=0 (P-position)")
print(f"  k=2: (3,5) -> Grundy=0 (P-position)")
print(f"  (2,3) is between these P-positions")
print()
print(f"  Grundy(2,3) = 5 = sopfr(6)!")
print(f"  sopfr(6) = 2+3 = 5 (sum of prime factors with repetition)")
print(f"  Wythoff Grundy value at (phi(6), sigma/tau(6)) = sopfr(6)")
print()
# verify
print(f"  Is this a coincidence? Check:")
print(f"  (phi(6), sigma/tau(6)) = (2, 3)")
print(f"  Grundy at (2,3) in Wythoff = 5")
print(f"  sopfr(6) = 2+3 = 5 = sum of coordinates!")
print(f"  Actually: Grundy(a,b) = a XOR b... for standard Nim? No, Wythoff is different.")
print()
print(f"  Wait: phi(6)=2, sigma/tau=3, sum=5=sopfr(6)")
print(f"  And Grundy(2,3) in Wythoff = 5")
print(f"  This could be Wythoff Grundy = sum of coordinates for this position?")
print()

# Compute Grundy for all positions and check if Grundy = sum ever
def wythoff_grundy_full(max_pos=10):
    G = {}
    for total in range(max_pos * 2 + 1):
        for a in range(min(total + 1, max_pos + 1)):
            b = total - a
            if b > max_pos or a > b:
                continue
            mex_set = set()
            for k in range(1, a + 1):
                pos = (min(a-k, b), max(a-k, b))
                if pos in G:
                    mex_set.add(G[pos])
            for k in range(1, b + 1):
                pos = (min(a, b-k), max(a, b-k))
                if pos in G:
                    mex_set.add(G[pos])
            for k in range(1, min(a, b) + 1):
                pos = (min(a-k, b-k), max(a-k, b-k))
                if pos in G:
                    mex_set.add(G[pos])
            mex = 0
            while mex in mex_set:
                mex += 1
            G[(a, b)] = mex
    return G

G = wythoff_grundy_full(10)
print("Positions where Grundy(a,b) = a+b (Wythoff Grundy = coordinate sum):")
sum_matches = [(a,b) for (a,b) in G if G[(a,b)] == a+b and (a,b) != (0,0)]
for pos in sorted(sum_matches)[:20]:
    print(f"  {pos}: Grundy={G[pos]}, sum={pos[0]+pos[1]}")

print(f"\nTotal such positions (up to max=10): {len(sum_matches)}")
print(f"(2,3) is one of them: Grundy(2,3)={G[(2,3)]}, sum=5")
print()
print(f"Grade for (2,3) Grundy=5=sopfr(6): partial connection")
print(f"The sum a+b = phi(6)+sigma/tau = 5 = sopfr(6) is the real pattern")

# ============================================================
# SUMMARY TABLE
# ============================================================
print("\n\n" + "=" * 70)
print("GRADED SUMMARY TABLE")
print("=" * 70)

findings = [
    ("1", "Nash: E[mixed NE] ~ sqrt(3*pi) ~ 3 = sigma/tau",
     "Approximation (2.3% off). sigma/tau=3 is exact but formula is asymptotic.",
     "YELLOW"),
    ("2a", "Shapley [sigma; divs]: all equal = 1/tau(6)",
     "Forced by quota=total_weight structure. Trivially true for any n.",
     "GREEN (trivial)"),
    ("2b", "Shapley [6 or 7; 1,2,3,6]: player w=n gets 3/4",
     "n=6 player dominates; small player gets 1/12 = 1/sigma(6).",
     "GREEN (exact, exact fractions)"),
    ("4a", "XOR(divisors of 6) = 6 = n",
     "Previously confirmed. n=6 is among few numbers where XOR(divs)=n.",
     "GREEN (exact)"),
    ("4b", "Wythoff Grundy(phi,sigma/tau) = (2,3) -> 5 = sopfr(6)",
     "Position (2,3) has Grundy=5=a+b=phi+sigma/tau=sopfr. Not unique - many (a,b) satisfy Grundy=a+b.",
     "WHITE (coincidence likely)"),
    ("7a", "Banzhaf [sigma; divs]: all equal = 1/tau(6)",
     "Same as Shapley at quota=total. Trivially true.",
     "GREEN (trivial)"),
    ("7b", "Banzhaf [6 or 7; 1,2,3,6]: player w=6 gets 7/10",
     "7/10 vs expected tau/sigma=4/12=1/3... no clean n=6 constant.",
     "WHITE (no n=6 connection)"),
    ("NEW", "Shapley(w=1) = 1/sigma(6) = 1/12 in [6;1,2,3,6]",
     "Weak players (w < quota alone) get 1/sigma(6) power. Clean exact formula.",
     "GREEN (exact)"),
]

print(f"\n{'#':>5} | {'Grade':>12} | Finding")
print(f"{'-'*5}-+-{'-'*12}-+{'-'*50}")
for f in findings:
    print(f"  {f[0]:>3} | {f[3]:>12} | {f[1][:50]}")
    if len(f[1]) > 50:
        print(f"        |              | {f[1][50:]}")
    print(f"        |              | -> {f[2][:60]}")
    print()

# ============================================================
# STRONGEST FINDING: Shapley 1/sigma connection
# ============================================================
print("=" * 70)
print("STRONGEST FINDING: Shapley value = 1/sigma(n) for weak players")
print("=" * 70)
print()
print("Game [n; divisors of n] (quota = n itself)")
print("For perfect number n=6:")
print("  Small players (w=1,2,3 each < quota=6) need w=6 to form coalition")
print("  Shapley(w in {1,2,3}) = 1/sigma(6) = 1/12 exactly")
print()
print("Why 1/12?")
print("  In [6; 1,2,3,6]: player w=6 can only win with at least one small player")
print("  when quota=7, OR player w=6 alone wins at quota=6")
print()
print("For n=28 (check):")
sv28_7, _ = shapley_value_detail([1,2,4,7,14,28], 28)
print(f"  Game [28; 1,2,4,7,14,28]:")
for w, s in zip([1,2,4,7,14,28], sv28_7):
    print(f"    Player w={w}: Shapley = {s} = {float(s):.6f}")
print()
print(f"  sigma(28) = {56}, 1/sigma = {1/56:.6f}")
print(f"  Smallest player Shapley = {sv28_7[0]} = {float(sv28_7[0]):.6f}")

print("\nDone.")
