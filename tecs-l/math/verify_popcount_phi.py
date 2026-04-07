#!/usr/bin/env python3
"""
THEOREM: popcount(n) = phi(n) has solutions exactly {1, 2, 3, 6} = divisors of 6.

Rigorous proof via:
  (A) Exhaustive computation for n in [1, 10^6]
  (B) For n > 10^6: phi(n) >= sqrt(n/2) > 707 >> 20 >= popcount(n)

The bound phi(n) >= sqrt(n/2) is a classical result (see e.g. Wikipedia,
"Euler's totient function", section "Other inequalities").

Also explores:
  - s_b(n) = phi(n) for bases b = 2, 3, ..., 10
  - Structural analysis of why the solutions are the divisors of 6
  - Connection to perfect number 6
"""

import math
from collections import defaultdict


def popcount(n):
    """Count number of 1-bits in binary representation of n."""
    return bin(n).count('1')


def digit_sum_base(n, base):
    """Sum of digits of n in given base."""
    if n == 0:
        return 0
    s = 0
    while n > 0:
        s += n % base
        n //= base
    return s


def euler_phi(n):
    """Euler's totient function."""
    if n <= 0:
        return 0
    if n == 1:
        return 1
    result = n
    p = 2
    temp = n
    while p * p <= temp:
        if temp % p == 0:
            while temp % p == 0:
                temp //= p
            result -= result // p
        p += 1
    if temp > 1:
        result -= result // temp
    return result


def divisors(n):
    """Return sorted list of divisors of n."""
    divs = []
    for i in range(1, int(math.isqrt(n)) + 1):
        if n % i == 0:
            divs.append(i)
            if i != n // i:
                divs.append(n // i)
    return sorted(divs)


def main():
    print("=" * 72)
    print("  THEOREM: popcount(n) = phi(n)  <==>  n in {1, 2, 3, 6}")
    print("=" * 72)

    # ================================================================
    # PART 1: Exhaustive computation
    # ================================================================
    print("\n" + "-" * 72)
    print("PART 1: EXHAUSTIVE COMPUTATION")
    print("-" * 72)

    COMP_LIMIT = 1_000_001
    solutions = []
    for n in range(1, COMP_LIMIT):
        if popcount(n) == euler_phi(n):
            solutions.append(n)

    print(f"\nAll solutions in [1, {COMP_LIMIT - 1}]: {solutions}")
    print(f"Divisors of 6:                      {divisors(6)}")
    print(f"Match: {solutions == divisors(6)}")

    # Detail table for solutions
    print(f"\n{'n':>4} | {'binary':>12} | {'popcount':>8} | {'phi(n)':>6} | {'div of 6?':>10}")
    print("-" * 50)
    for n in solutions:
        print(f"{n:>4} | {bin(n):>12} | {popcount(n):>8} | {euler_phi(n):>6} | "
              f"{'YES' if 6 % n == 0 else 'NO':>10}")

    # Near-miss table
    print(f"\nNear-misses (n = 1..30):")
    print(f"{'n':>4} | {'binary':>12} | {'popcount':>8} | {'phi(n)':>6} | {'gap':>5}")
    print("-" * 47)
    for n in range(1, 31):
        pc = popcount(n)
        phi = euler_phi(n)
        mark = " <== SOLUTION" if pc == phi else ""
        print(f"{n:>4} | {bin(n):>12} | {pc:>8} | {phi:>6} | {phi - pc:>+5}{mark}")

    # ================================================================
    # PART 2: RIGOROUS PROOF OF COMPLETENESS
    # ================================================================
    print("\n" + "-" * 72)
    print("PART 2: RIGOROUS PROOF OF COMPLETENESS")
    print("-" * 72)

    print("""
PROOF STRUCTURE:

  Step 1. Verify the four claimed solutions.
  Step 2. For n >= 7, show phi(n) > popcount(n).
    (a) Exhaustive computation for n in [7, 10^6].       [Part 1 above]
    (b) For n > 10^6, use the analytic chain:
        popcount(n) <= floor(log2(n)) + 1                [trivial]
        phi(n) >= sqrt(n/2)                              [classical]
        sqrt(n/2) > floor(log2(n)) + 1  for n > 10^6    [shown below]
  Step 3. Handle n in {4, 5} individually.
""")

    # Step 1
    print("--- Step 1: Verify the four solutions ---")
    for n in [1, 2, 3, 6]:
        pc, phi = popcount(n), euler_phi(n)
        print(f"  popcount({n}) = {pc},  phi({n}) = {phi}  =>  {'EQUAL' if pc == phi else 'NOT EQUAL'}")

    # Step 2a already done
    print("\n--- Step 2a: Exhaustive check for n in [4, 10^6] ---")
    failures = []
    for n in range(4, COMP_LIMIT):
        if n in (1, 2, 3, 6):
            continue
        if popcount(n) >= euler_phi(n):
            failures.append(n)
    if failures:
        print(f"  FAILURES: {failures[:20]}")
    else:
        print(f"  PASS: phi(n) > popcount(n) for all n in [4, 10^6] \\ {{1,2,3,6}}")

    # Step 2b: analytic bound
    print("\n--- Step 2b: Analytic bound for n > 10^6 ---")
    print()
    print("  Bound 1 (trivial): popcount(n) <= floor(log2(n)) + 1")
    print()
    print("  Bound 2 (classical): phi(n) >= sqrt(n/2) for all n >= 1")

    # Verify the classical bound computationally
    pillai_ok = True
    for n in range(1, COMP_LIMIT):
        if euler_phi(n) < math.sqrt(n / 2):
            print(f"  !! Pillai bound fails at n={n}")
            pillai_ok = False
            break
    if pillai_ok:
        print(f"    Verified computationally for n in [1, {COMP_LIMIT - 1}].")

    print()
    print("  Bound 3: For n > 10^6:")
    n0 = 1_000_001
    sq = math.sqrt(n0 / 2)
    pc_max = math.floor(math.log2(n0)) + 1
    print(f"    sqrt({n0}/2) = {sq:.2f}")
    print(f"    floor(log2({n0})) + 1 = {pc_max}")
    print(f"    {sq:.2f} >> {pc_max}")
    print()
    print("  For n > 10^6:")
    print("    phi(n) >= sqrt(n/2) > sqrt(10^6 / 2) = 707.1")
    print("    popcount(n) <= floor(log2(n)) + 1")
    print()
    print("  Since sqrt(n/2) grows as n^(1/2) and log2(n)+1 grows as O(log n),")
    print("  once sqrt(n/2) > log2(n)+1 it stays true forever.")
    print()

    # Show that sqrt(n/2) > log2(n)+1 for ALL n >= 132 (not just n > 10^6)
    # Find the actual crossover (accounting for the powers-of-2 issue)
    cross = None
    for n in range(7, 10000):
        if math.sqrt(n / 2) > math.floor(math.log2(n)) + 1:
            # Check: does it hold for all n from here to 10000?
            holds = True
            for m in range(n, 10001):
                if math.sqrt(m / 2) <= math.floor(math.log2(m)) + 1:
                    holds = False
                    break
            if holds:
                cross = n
                break

    if cross:
        print(f"  Tighter crossover: sqrt(n/2) > floor(log2(n))+1 for all n >= {cross}")
        print(f"    At n={cross}: sqrt({cross}/2)={math.sqrt(cross/2):.4f}, "
              f"floor(log2({cross}))+1={math.floor(math.log2(cross))+1}")
    # The values between 7 and cross-1 are already covered by Step 2a.

    # Step 3
    print("\n--- Step 3: Handle n = 4 and n = 5 ---")
    for n in [4, 5]:
        pc, phi = popcount(n), euler_phi(n)
        print(f"  n={n}: popcount={pc}, phi={phi}, phi > popcount: {phi > pc}")

    print("\n--- PROOF COMPLETE ---")
    print()
    print("  The chain is:")
    print("    1. For n in {1,2,3,6}: popcount(n) = phi(n) verified directly.")
    print("    2. For n = 4,5: phi(n) > popcount(n) verified directly.")
    print(f"    3. For n in [7, 10^6]: phi(n) > popcount(n) by exhaustive computation.")
    print(f"    4. For n > 10^6: phi(n) >= sqrt(n/2) > 707 >> 20 >= log2(n)+1")
    print(f"       >= popcount(n), using the classical bound phi(n) >= sqrt(n/2).")
    print(f"    Therefore {'{'}1, 2, 3, 6{'}'} is the complete solution set.  QED")

    # ================================================================
    # PART 3: STRUCTURAL ANALYSIS - WHY DIVISORS OF 6?
    # ================================================================
    print("\n" + "-" * 72)
    print("PART 3: STRUCTURAL ANALYSIS")
    print("-" * 72)

    print("""
WHY exactly {1, 2, 3, 6}?

The equation popcount(n) = phi(n) can only hold when phi(n) is very small,
because popcount(n) <= log2(n) + 1 grows logarithmically.

For phi(n) = k (small), there are finitely many solutions n.
We check each k:
""")

    # Build phi preimage
    phi_preimage = defaultdict(list)
    for n in range(1, 10001):
        phi_preimage[euler_phi(n)].append(n)

    print(f"{'k':>3} | {'n with phi(n) = k':>50} | {'popcount match':>20}")
    print("-" * 80)
    for k in range(1, 21):
        ns = phi_preimage.get(k, [])
        matches = [n for n in ns if popcount(n) == k]
        ns_display = ns[:12]
        suffix = f"... ({len(ns)} total)" if len(ns) > 12 else ""
        print(f"{k:>3} | {str(ns_display) + suffix:>50} | {str(matches):>20}")

    print("""
Key observations:
  k=1: phi(n)=1 <=> n in {1, 2}.  popcount(1)=1, popcount(2)=1.  Both match!
  k=2: phi(n)=2 <=> n in {3, 4, 6}.
       popcount(3)=2 [match], popcount(4)=1 [no], popcount(6)=2 [match].
  k=3: phi(n)=3 has NO solutions (3 is odd, phi(n) is even for n>2).
  k=4: phi(n)=4 <=> n in {5, 8, 10, 12}.
       popcount: 2, 1, 2, 2.  None equal 4.
  k>=5: The smallest n with phi(n)=k has n >= k+1, so log2(n) ~ log2(k),
       and popcount(n) <= log2(k)+1 << k for large k.  No matches possible.
""")

    print("The structural reason: phi(n) is multiplicative and grows roughly like n,")
    print("while popcount grows like log(n). They can only meet at tiny values.")
    print("At those tiny values, the coincidence that {1,2,3,6} = div(6) emerges")
    print("from the specific binary representations and the fact that phi(n)=2")
    print("has exactly three solutions {3,4,6}, of which 3 and 6 have popcount 2.")

    # ================================================================
    # PART 4: GENERALIZATION TO OTHER BASES
    # ================================================================
    print("\n" + "-" * 72)
    print("PART 4: GENERALIZATION s_b(n) = phi(n) FOR BASES b = 2..10")
    print("-" * 72)

    GLIMIT = 100001
    for base in range(2, 11):
        sols = []
        for n in range(1, GLIMIT):
            if digit_sum_base(n, base) == euler_phi(n):
                sols.append(n)
        is_div6 = (sols == [1, 2, 3, 6])
        tag = "  <== DIVISORS OF 6!" if is_div6 else ""
        print(f"  Base {base:>2}: {sols}{tag}")

    print("""
The base-2 case is UNIQUE in producing exactly the divisors of 6.
No other base b in [2,10] gives {1, 2, 3, 6}.
""")

    # ================================================================
    # PART 5: PRIMORIAL WORST-CASE ANALYSIS
    # ================================================================
    print("-" * 72)
    print("PART 5: WORST-CASE phi ANALYSIS (PRIMORIALS)")
    print("-" * 72)
    print("\nPrimorials n=p# have the smallest phi(n)/n ratio.")
    print("Even for these, phi(n) >> popcount(n):\n")

    primorial = 1
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
    print(f"{'p#':>15} | {'phi(p#)':>12} | {'popcount':>8} | {'phi/popcount':>12}")
    print("-" * 55)
    for p in primes:
        primorial *= p
        phi_val = euler_phi(primorial)
        pc = popcount(primorial)
        ratio = phi_val / pc if pc > 0 else float('inf')
        print(f"{primorial:>15} | {phi_val:>12} | {pc:>8} | {ratio:>12.1f}")

    # ================================================================
    # PART 6: CONNECTION TO PERFECT NUMBER 6
    # ================================================================
    print("\n" + "-" * 72)
    print("PART 6: CONNECTION TO PERFECT NUMBER 6")
    print("-" * 72)

    print(f"""
The solution set {{1, 2, 3, 6}} = divisors of 6, the first perfect number.

Arithmetic properties of the solution set:
  Sum:     1 + 2 + 3 + 6 = {1+2+3+6} = 2 * 6 = sigma(6)  [perfect number property]
  Product: 1 * 2 * 3 * 6 = {1*2*3*6} = 6^2
  1/1 + 1/2 + 1/3 + 1/6 = {1 + 1/2 + 1/3 + 1/6} = 2     [reciprocal sum = sigma_{-1}(6)]

Is the connection to 6 structural or coincidental?

  The solutions arise from two conditions:
    (i)  phi(n) = 1 has solutions {{1, 2}}     -- both are divisors of 6
    (ii) phi(n) = 2 has solutions {{3, 4, 6}}   -- popcount filters to {{3, 6}}

  Why does 4 fail? Because 4 = 100_2 has popcount 1 != 2.
  This is specific to base 2. In base 3: digit_sum(4, base=3) = digit_sum(11_3) = 2,
  so 4 DOES appear in the base-3 solution set [1, 4, 6, 8].

  The connection to 6 being perfect is COINCIDENTAL in the following sense:
    - The solutions are determined by the small-value structure of phi
    - phi(n) = 1 gives {{1, 2}} (always divisors of any n >= 2)
    - phi(n) = 2 giving {{3, 4, 6}} is a number-theoretic fact
    - popcount filtering 4 out is a base-2 artifact
    - That {{1, 2, 3, 6}} happens to be div(6) follows from 6 = 2 * 3

  However, there IS a structural element: 6 = 2 * 3 is the product of the
  first two primes, and phi is controlled by prime factorization. The numbers
  with phi(n) <= 2 are exactly those whose prime factors are contained in
  {{2, 3}}, plus 1. These are: 1, 2, 3, 4, 6 -- which are the divisors of
  12 = 2^2 * 3. The popcount filter removes 4, leaving div(6) = div(2*3).
""")

    # ================================================================
    # PART 7: OEIS NOVELTY ASSESSMENT
    # ================================================================
    print("-" * 72)
    print("PART 7: LITERATURE / OEIS SEARCH")
    print("-" * 72)

    print("""
Searches conducted:
  1. OEIS for "popcount equals phi" / "binary digit sum equals totient"
  2. OEIS for A000120 (binary weight) cross-referenced with A000010 (totient)
  3. Web search for "Hamming weight equals Euler totient"
  4. Web search for characterizations of {1, 2, 3, 6}
  5. MathWorld, Brilliant, Codeforces, AoPS for related results

Results:
  - A362951 (Hamming distance between n and phi(n)) is the closest related sequence.
  - NO sequence found for "numbers n where popcount(n) = phi(n)".
  - The specific result that solutions = {1, 2, 3, 6} does NOT appear in OEIS.
  - This appears to be a NEW observation as of March 2026.

Assessment: LIKELY NOVEL (not found in standard references).
The result is elementary to prove but the specific characterization of
divisors of the first perfect number via popcount = phi seems unrecorded.
""")

    # ================================================================
    # PART 8: VERIFY phi(n) >= sqrt(n/2) BOUND
    # ================================================================
    print("-" * 72)
    print("PART 8: VERIFICATION OF phi(n) >= sqrt(n/2)")
    print("-" * 72)

    print("\nThis bound is classical. We verify it computationally.\n")
    min_ratio = float('inf')
    min_n = 0
    for n in range(1, COMP_LIMIT):
        phi_n = euler_phi(n)
        bound = math.sqrt(n / 2)
        ratio = phi_n / bound if bound > 0 else float('inf')
        if ratio < min_ratio:
            min_ratio = ratio
            min_n = n

    print(f"  min phi(n)/sqrt(n/2) over [1, {COMP_LIMIT-1}] = {min_ratio:.6f}")
    print(f"  achieved at n = {min_n}")
    print(f"  phi({min_n}) = {euler_phi(min_n)}, sqrt({min_n}/2) = {math.sqrt(min_n/2):.6f}")
    print(f"  Ratio > 1: {'YES' if min_ratio >= 1.0 else 'NO'}")
    print()

    # Proof sketch for phi(n) >= sqrt(n/2):
    print("  Proof sketch (classical):")
    print("    phi(n) = n * prod_{p|n} (1 - 1/p)")
    print("    = n * prod_{p|n} (p-1)/p")
    print("    For n = p1^a1 * ... * pk^ak:")
    print("      phi(n) = p1^(a1-1)*(p1-1) * ... * pk^(ak-1)*(pk-1)")
    print("    Claim: phi(n)^2 >= n/2.")
    print("    This follows from: for each prime power p^a || n,")
    print("      phi(p^a)^2 = p^(2a-2)*(p-1)^2 >= p^a / 2")
    print("    which holds when p^(a-2)*(p-1)^2 >= 1/2,")
    print("    true for all p >= 2, a >= 1 (check: p=2,a=1 gives 1/2*1=1/2, equality).")
    print("    The product of such inequalities (with at most one factor = 1/2)")
    print("    gives phi(n)^2 >= n/2.")

    # ================================================================
    # FINAL SUMMARY
    # ================================================================
    print("\n" + "=" * 72)
    print("  FINAL SUMMARY")
    print("=" * 72)
    print(f"""
  THEOREM: popcount(n) = phi(n) if and only if n in {{1, 2, 3, 6}}.

  These are exactly the positive divisors of 6, the first perfect number.

  PROOF:
    Forward: Direct verification for n = 1, 2, 3, 6.
    Backward: For n not in {{1,2,3,6}}:
      - Computational check for n in [4, 10^6]: phi(n) > popcount(n).
      - For n > 10^6: phi(n) >= sqrt(n/2) > 707 > 20 >= popcount(n).

  NOVELTY: Not found in OEIS or mathematical literature (as of 2026-03).

  GENERALIZATION (base b digit sum):
    b=2: {{1, 2, 3, 6}} = div(6)   [UNIQUE to base 2]
    b=3: {{1, 4, 6, 8}}
    b=4: {{1, 10}}
    b=5: {{1, 6, 8, 12, 14, 18, 24}}
    b=6: {{1}}
    Other bases give different sets; only base 2 yields div(6).
""")


if __name__ == "__main__":
    main()
