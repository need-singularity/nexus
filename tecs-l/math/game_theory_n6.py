"""
Game Theory and Social Choice Theory for n=6
Focus: Items 1 (Nash equilibria), 2 (Shapley value), 4 (Sprague-Grundy/Wythoff), 7 (Banzhaf)

n=6: sigma=12, phi=2, tau=4, sopfr=5
"""

import math
import itertools
from fractions import Fraction

print("=" * 70)
print("GAME THEORY AND SOCIAL CHOICE THEORY FOR n=6")
print("n=6: sigma=12, phi=2, tau=4, sopfr=5")
print("=" * 70)

# Core constants
n = 6
sigma = 12   # sum of divisors
phi = 2      # Euler totient
tau = 4      # number of divisors
sopfr = 5    # sum of prime factors (2+3)
divisors = [1, 2, 3, 6]

print(f"\nn={n}, sigma={sigma}, phi={phi}, tau={tau}, sopfr={sopfr}")
print(f"divisors of 6: {divisors}")

# ============================================================
# ITEM 1: Nash Equilibria in 2-player n×n games
# ============================================================
print("\n" + "=" * 70)
print("ITEM 1: Nash Equilibria in 2-player n×n games")
print("=" * 70)

# Theorem (McLennan & Berg 2005): Expected number of NE in random n×n game
# E[NE] ~ sqrt(pi * n / 2) as n -> infinity
# More precisely: E[NE] = sum_{k=1}^{n} C(n,k)^2 * k! / n^k * (something)
# Simple formula: E[NE] ≈ sqrt(pi * n / 2)

print("\n--- Expected NE count formula ---")
for k in range(2, 10):
    approx = math.sqrt(math.pi * k / 2)
    print(f"  n={k}: sqrt(pi*{k}/2) = {approx:.4f}")

# At n=6
ne_n6 = math.sqrt(math.pi * 6 / 2)
ne_sigma_tau = sigma / tau  # 12/4 = 3
print(f"\nAt n=6:")
print(f"  E[NE] ~ sqrt(pi*6/2) = sqrt(3*pi) = {ne_n6:.6f}")
print(f"  sigma/tau = {sigma}/{tau} = {ne_sigma_tau}")
print(f"  Difference: {abs(ne_n6 - ne_sigma_tau):.6f}")
print(f"  Ratio: {ne_n6/ne_sigma_tau:.6f}")
print(f"  Match? sqrt(3*pi) = {ne_n6:.4f} vs sigma/tau = {ne_sigma_tau}")

# More precise formula for E[NE]
# Using the exact formula from the literature:
# E[NE_k] = C(n,k)^2 * integral ...
# Simple upper bound: sum_k C(n,k) * (k/n)^k * ((n-k)/n)^(n-k)
print("\n--- Exact computation attempt for small n ---")
# For pure strategy NE: check all strategy profiles
# Actually compute average over random 2-player games via simulation
import random
random.seed(42)

def count_pure_ne(A, B, n):
    """Count pure strategy Nash equilibria in n×n bimatrix game (A, B)."""
    ne_count = 0
    for i in range(n):
        for j in range(n):
            # Check if (i,j) is a NE
            # Player 1 best response: A[i][j] >= A[k][j] for all k
            if all(A[i][j] >= A[k][j] for k in range(n)):
                # Player 2 best response: B[i][j] >= B[i][l] for all l
                if all(B[i][j] >= B[i][l] for l in range(n)):
                    ne_count += 1
    return ne_count

num_simulations = 10000
ne_counts = {k: [] for k in range(2, 10)}

for k in ne_counts:
    total = 0
    for _ in range(num_simulations):
        A = [[random.gauss(0, 1) for _ in range(k)] for _ in range(k)]
        B = [[random.gauss(0, 1) for _ in range(k)] for _ in range(k)]
        total += count_pure_ne(A, B, k)
    ne_counts[k] = total / num_simulations

print(f"\n  Simulated E[pure NE] vs formula (10000 random games each):")
print(f"  {'n':>4} | {'Simulated':>10} | {'sqrt(pi*n/2)':>12} | {'Ratio':>8}")
print(f"  {'-'*4}-+-{'-'*10}-+-{'-'*12}-+-{'-'*8}")
for k in range(2, 10):
    sim = ne_counts[k]
    formula = math.sqrt(math.pi * k / 2)
    print(f"  {k:>4} | {sim:>10.4f} | {formula:>12.4f} | {sim/formula:>8.4f}")

print(f"\n  At n=6 specifically:")
print(f"    Simulated E[pure NE] = {ne_counts[6]:.4f}")
print(f"    sqrt(3*pi) = {ne_n6:.4f}")
print(f"    sigma/tau = {ne_sigma_tau} (= 3 exactly)")
print(f"    |sqrt(3*pi) - 3| = {abs(ne_n6 - 3):.4f} ({abs(ne_n6-3)/3*100:.2f}% off)")

# ============================================================
# ITEM 2: Shapley Value for weighted voting game [quota; 1,2,3,6]
# ============================================================
print("\n" + "=" * 70)
print("ITEM 2: Shapley Value for weighted voting game")
print("=" * 70)
print("Game: [quota; w1, w2, w3, w4] = [?; 1, 2, 3, 6]")
print("Weights = divisors of 6")
print("Total weight = 1+2+3+6 = 12 = sigma(6)")

weights = [1, 2, 3, 6]
total_weight = sum(weights)
players = list(range(len(weights)))  # 0,1,2,3
print(f"Total weight = {total_weight} = sigma(6) = {sigma}")

def shapley_value(weights, quota):
    """Compute Shapley values for weighted voting game [quota; weights]."""
    n_players = len(weights)
    shapley = [Fraction(0) for _ in range(n_players)]

    # Iterate over all permutations
    for perm in itertools.permutations(range(n_players)):
        cumulative = 0
        for pos, player in enumerate(perm):
            cumulative += weights[player]
            # Check if this player is pivotal (crosses quota)
            prev_cumulative = cumulative - weights[player]
            if prev_cumulative < quota <= cumulative:
                shapley[player] += Fraction(1, math.factorial(n_players))
                break

    return shapley

print("\n--- Shapley values for different quotas ---")
print(f"{'Quota':>6} | {'phi1(w=1)':>12} | {'phi2(w=2)':>12} | {'phi3(w=3)':>12} | {'phi4(w=6)':>12} | {'Sum':>6}")
print(f"{'-'*6}-+-{'-'*12}-+-{'-'*12}-+-{'-'*12}-+-{'-'*12}-+-{'-'*6}")

# Test various quotas
quota_results = {}
for quota in range(1, total_weight + 1):
    sv = shapley_value(weights, quota)
    sv_sum = sum(sv)
    quota_results[quota] = sv
    if quota in [6, 7, 8, 9, 10, 11, 12]:  # interesting quotas
        sv_float = [float(s) for s in sv]
        print(f"  {quota:>4} | {str(sv[0]):>12} | {str(sv[1]):>12} | {str(sv[2]):>12} | {str(sv[3]):>12} | {float(sv_sum):.3f}")

# Focus on quota = sigma/2 = 6 (majority) and quota = sigma = 12
print(f"\n--- Key quotas ---")
for quota in [6, 7, 12]:
    sv = quota_results[quota]
    print(f"\n  Quota = {quota}:")
    for i, (w, s) in enumerate(zip(weights, sv)):
        print(f"    Player {i+1} (weight={w}): Shapley = {s} = {float(s):.6f}")
    # Check ratios
    if sv[0] != 0:
        ratios = [s/sv[0] for s in sv]
        print(f"    Ratios relative to w=1: {[str(r) for r in ratios]}")

# Focus on quota = 7 (simple majority of 12)
print("\n--- Quota = 7 (strict majority of total=12) ---")
sv7 = quota_results[7]
print(f"  Player weights: {weights}")
print(f"  Shapley values: {[str(s) for s in sv7]}")
print(f"  As decimals:    {[f'{float(s):.4f}' for s in sv7]}")
print(f"  n=6 connections:")
print(f"    phi(6)=2, Shapley(w=6) = {sv7[3]} = {float(sv7[3]):.4f}")
print(f"    tau(6)=4 (number of players)")
print(f"    sigma(6)=12 (total weight)")
print(f"    Sum Shapley = {sum(sv7)} = 1")

# Check if Shapley value of w=1 player matches something
print(f"\n  Shapley(w=1) = {sv7[0]} = {float(sv7[0]):.6f}")
print(f"  phi/sigma = {phi}/{sigma} = {phi/sigma:.6f} (phi(6)/sigma(6))")
print(f"  1/tau = 1/{tau} = {1/tau:.6f}")
print(f"  1/sigma = 1/{sigma} = {1/sigma:.6f}")

# ============================================================
# ITEM 4: Sprague-Grundy / Wythoff's Game at (phi, sigma/tau) = (2, 3)
# ============================================================
print("\n" + "=" * 70)
print("ITEM 4: Sprague-Grundy / Wythoff's Game")
print("=" * 70)
print(f"Position (phi, sigma/tau) = ({phi}, {sigma//tau}) = (2, 3)")

# Wythoff's game: two piles, can remove any from one pile OR equal from both
# Losing positions (P-positions): (floor(k*phi_golden), floor(k*phi_golden^2))
phi_golden = (1 + math.sqrt(5)) / 2
print(f"\nGolden ratio phi = {phi_golden:.6f}")
print(f"phi^2 = {phi_golden**2:.6f}")

print("\n--- Wythoff P-positions (losing positions for player to move) ---")
print(f"{'k':>4} | {'floor(k*phi)':>12} | {'floor(k*phi^2)':>14}")
print(f"{'-'*4}-+-{'-'*12}-+-{'-'*14}")
for k in range(10):
    a = int(k * phi_golden)
    b = int(k * phi_golden**2)
    marker = " <-- (phi(6), sigma/tau)" if (a, b) == (phi, sigma//tau) else ""
    marker2 = " <-- (2,3)" if (a, b) == (2, 3) else ""
    print(f"  {k:>2} | {a:>12} | {b:>14}{marker}{marker2}")

# Compute Grundy value (nim-value) for Wythoff's game at (2,3)
def wythoff_grundy(max_pos=20):
    """Compute Grundy values for Wythoff's game."""
    G = {}
    for total in range(max_pos * 2 + 1):
        for a in range(min(total + 1, max_pos + 1)):
            b = total - a
            if b > max_pos:
                continue
            if a > b:
                continue
            # Moves:
            # 1. Remove k from pile a (k >= 1): (a-k, b) -> (min, max)
            # 2. Remove k from pile b (k >= 1): (a, b-k) -> (min, max)
            # 3. Remove k from both: (a-k, b-k) -> (min, max)
            mex_set = set()

            # Remove from first pile
            for k in range(1, a + 1):
                pos = (min(a-k, b), max(a-k, b))
                if pos in G:
                    mex_set.add(G[pos])

            # Remove from second pile
            for k in range(1, b + 1):
                pos = (min(a, b-k), max(a, b-k))
                if pos in G:
                    mex_set.add(G[pos])

            # Remove from both
            for k in range(1, min(a, b) + 1):
                pos = (min(a-k, b-k), max(a-k, b-k))
                if pos in G:
                    mex_set.add(G[pos])

            # MEX
            mex = 0
            while mex in mex_set:
                mex += 1
            G[(a, b)] = mex

    return G

print("\n--- Computing Wythoff Grundy values ---")
G = wythoff_grundy(15)

print(f"\nGrundy value at (2, 3) = {G.get((2,3), 'N/A')}")
print(f"(phi(6)=2, sigma/tau=3)")
print(f"\nP-positions (Grundy=0) up to (6,6):")
p_positions = [(a,b) for (a,b),g in sorted(G.items()) if g == 0 and a <= 6 and b <= 6]
for pos in p_positions:
    print(f"  {pos}")

# Also Sprague-Grundy for Nim with divisors of 6
print("\n--- XOR of divisors of 6 ---")
xor_val = 0
for d in divisors:
    xor_val ^= d
    print(f"  After XOR {d}: {xor_val}")
print(f"  XOR(1,2,3,6) = {xor_val} = n = {n}")
print(f"  (Confirmed: XOR of divisors of 6 = 6)")

# Nim sum analysis
print("\n--- Nim at position (phi, sigma/tau) = (2, 3) ---")
nim_val = phi ^ (sigma // tau)
print(f"  Nim value (2 XOR 3) = {phi} XOR {sigma//tau} = {nim_val}")
print(f"  Position (2,3) is {'P-position (losing)' if nim_val == 0 else 'N-position (winning)'}")
print(f"  Note: 2 XOR 3 = 1, so it's a winning position")

# Wythoff check
print(f"\n--- Is (2,3) a Wythoff P-position? ---")
# P-positions: (floor(k*phi), floor(k*phi^2))
wythoff_p = [(int(k*phi_golden), int(k*phi_golden**2)) for k in range(20)]
print(f"  (2,3) in Wythoff P-positions? {(2,3) in wythoff_p}")
print(f"  Grundy value at (2,3) = {G.get((2,3), 'N/A')}")
if G.get((2,3)) == 0:
    print(f"  -> P-position (second player wins)")
else:
    print(f"  -> N-position (first player wins), Grundy = {G.get((2,3))}")

# ============================================================
# ITEM 7: Banzhaf Power Index for [sigma; divisors of 6]
# ============================================================
print("\n" + "=" * 70)
print("ITEM 7: Banzhaf Power Index")
print("=" * 70)
print(f"Game: [sigma; divisors] = [{sigma}; {divisors}]")
print(f"Quota = sigma(6) = {sigma}")
print(f"Total weight = {total_weight}")

def banzhaf_index(weights, quota):
    """Compute Banzhaf power index for weighted voting game."""
    n_players = len(weights)
    critical_swings = [0] * n_players
    total_swings = 0

    # Iterate over all subsets
    for coalition_bits in range(1 << n_players):
        coalition = [i for i in range(n_players) if coalition_bits & (1 << i)]
        coalition_weight = sum(weights[i] for i in coalition)

        if coalition_weight >= quota:
            # Check which members are critical (swing voters)
            for i in coalition:
                if coalition_weight - weights[i] < quota:
                    critical_swings[i] += 1
                    total_swings += 1

    # Normalized Banzhaf
    if total_swings > 0:
        normalized = [Fraction(c, total_swings) for c in critical_swings]
    else:
        normalized = [Fraction(0) for _ in range(n_players)]

    # Absolute Banzhaf (proportion of all coalitions where player is critical)
    absolute = [Fraction(c, 2**(n_players-1)) for c in critical_swings]

    return critical_swings, normalized, absolute

print(f"\n--- Banzhaf for [12; 1, 2, 3, 6] ---")
critical, normalized, absolute = banzhaf_index(weights, sigma)
print(f"  {'Player':>8} | {'Weight':>6} | {'Swings':>6} | {'Normalized':>12} | {'Absolute':>12} | {'Float':>8}")
print(f"  {'-'*8}-+-{'-'*6}-+-{'-'*6}-+-{'-'*12}-+-{'-'*12}-+-{'-'*8}")
for i, (w, c, norm, abso) in enumerate(zip(weights, critical, normalized, absolute)):
    print(f"  Player {i+1:>2} | {w:>6} | {c:>6} | {str(norm):>12} | {str(abso):>12} | {float(norm):.4f}")

# Check if all players have equal power
print(f"\n  Are all Banzhaf values equal? {len(set(normalized)) == 1}")
print(f"  Sum of normalized = {sum(normalized)}")
print(f"  Total swings = {sum(critical)}")

# Try quota = 7 (strict majority)
print(f"\n--- Banzhaf for [7; 1, 2, 3, 6] ---")
critical7, normalized7, absolute7 = banzhaf_index(weights, 7)
print(f"  {'Player':>8} | {'Weight':>6} | {'Swings':>6} | {'Normalized':>12} | {'Float':>8}")
print(f"  {'-'*8}-+-{'-'*6}-+-{'-'*6}-+-{'-'*12}-+-{'-'*8}")
for i, (w, c, norm) in enumerate(zip(weights, critical7, normalized7)):
    print(f"  Player {i+1:>2} | {w:>6} | {c:>6} | {str(norm):>12} | {float(norm):.6f}")

# Check specific relationships
print(f"\n  n=6 constant connections:")
print(f"    Banzhaf(w=6) normalized = {normalized7[3]} = {float(normalized7[3]):.6f}")
print(f"    Banzhaf(w=1) normalized = {normalized7[0]} = {float(normalized7[0]):.6f}")
print(f"    Ratio Banzhaf(w=6)/Banzhaf(w=1) = {normalized7[3]/normalized7[0] if normalized7[0] != 0 else 'inf'}")
print(f"    phi(6)/1 = {phi}")
print(f"    tau(6) = {tau}")

# Try quota = 6
print(f"\n--- Banzhaf for [6; 1, 2, 3, 6] ---")
critical6, normalized6, absolute6 = banzhaf_index(weights, 6)
print(f"  {'Player':>8} | {'Weight':>6} | {'Swings':>6} | {'Normalized':>12} | {'Float':>8}")
print(f"  {'-'*8}-+-{'-'*6}-+-{'-'*6}-+-{'-'*12}-+-{'-'*8}")
for i, (w, c, norm) in enumerate(zip(weights, critical6, normalized6)):
    print(f"  Player {i+1:>2} | {w:>6} | {c:>6} | {str(norm):>12} | {float(norm):.6f}")

# ============================================================
# SUMMARY: Check all n=6 constant connections
# ============================================================
print("\n" + "=" * 70)
print("SUMMARY: n=6 Constant Connections in Game Theory")
print("=" * 70)

print(f"\n1. Nash Equilibria:")
print(f"   E[NE] ~ sqrt(pi*n/2) at n=6 = sqrt(3*pi) = {ne_n6:.6f}")
print(f"   sigma/tau = {sigma}/{tau} = {ne_sigma_tau} (exact integer)")
print(f"   Difference = {abs(ne_n6 - ne_sigma_tau):.6f} = {abs(ne_n6-3)/3*100:.2f}%")
print(f"   MATCH QUALITY: sqrt(3*pi) ~ 3 = sigma/tau (2.3% off)")

print(f"\n2. Shapley Value [7; 1,2,3,6]:")
sv_ratio = normalized7[3] / normalized7[0] if normalized7[0] != 0 else float('inf')
print(f"   Shapley(w=6)/Shapley(w=1) = {sv_ratio}")
print(f"   sigma/phi = {sigma}/{phi} = {sigma//phi}")

print(f"\n4. Wythoff's Game at (phi,sigma/tau) = (2,3):")
print(f"   Grundy value = {G.get((2,3))}")
print(f"   XOR(divisors of 6) = {xor_val} = n")

print(f"\n7. Banzhaf [12; 1,2,3,6] (quota = sigma):")
print(f"   All players have equal Banzhaf power: {len(set(normalized)) == 1}")
if len(set(normalized)) == 1 and normalized[0] != 0:
    print(f"   Each player has power = {normalized[0]} = {float(normalized[0]):.4f} = 1/tau(6) = 1/{tau}")
elif normalized[0] == 0:
    print(f"   NOTE: Quota=12 means only the full coalition wins -> all have 0 power")
    print(f"   This is a degenerate case (quota = total weight)")

# Bonus: check if quota = total_weight makes any single player a dictator
print(f"\n--- Bonus: Dictator check ---")
for i, w in enumerate(weights):
    if w >= sigma:
        print(f"   Player {i+1} (w={w}) is a DICTATOR (weight >= quota={sigma})")
    elif w >= sigma - (total_weight - w):
        pass  # veto power
print(f"   Player 4 (w=6=n): veto power?")
# Player 4 has veto if total - w4 < quota
print(f"   Without player 4: weight = {total_weight - weights[3]} vs quota {sigma} -> {'has veto' if total_weight - weights[3] < sigma else 'no veto'}")
for quota_test in [7, 8, 9]:
    no_p4 = total_weight - weights[3]
    has_veto = no_p4 < quota_test
    print(f"   Quota={quota_test}: without player4={no_p4}, veto={'YES' if has_veto else 'NO'}")

print(f"\n--- Final Grade Assessment ---")
print(f"1. Nash: sqrt(3*pi) ~ 3 = sigma/tau ... near-miss (2.3%), not exact")
print(f"   Grade: YELLOW (approximation, needs Texas test)")
print(f"2. Shapley [7;1,2,3,6]: computed above")
print(f"4. Wythoff (2,3): Grundy = {G.get((2,3))}, XOR(divisors)=6=n -> GREEN (exact)")
print(f"7. Banzhaf [12;1,2,3,6]: degenerate (quota=total), try quota=7 or n=6")

print("\nDone.")
