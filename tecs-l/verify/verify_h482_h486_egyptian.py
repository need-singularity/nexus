#!/usr/bin/env python3
"""
H-CX-482 / H-CX-486: Egyptian Fraction Perfect Number Uniqueness

H-CX-482: Among all solutions of 1 = 1/a + 1/b + 1/c (a<=b<=c),
           {2,3,6} is the ONLY one where lcm(a,b,c) is a perfect number.

H-CX-486: Generalize to k=4,5,6 terms. Are there solutions where
           lcm equals 28, 496, or any perfect number?

Also checks partial sums (1/2) and divisor-reciprocal partition property.
"""

import math
from fractions import Fraction
from itertools import combinations_with_replacement, combinations
import time

PERFECT_NUMBERS = {6, 28, 496, 8128, 33550336}

def is_perfect(n):
    """Check if n is a perfect number."""
    if n < 2:
        return False
    if n in PERFECT_NUMBERS:
        return True
    # For safety, compute
    s = 1
    for i in range(2, int(math.isqrt(n)) + 1):
        if n % i == 0:
            s += i
            if i != n // i:
                s += n // i
    return s == n

def lcm(a, b):
    return a * b // math.gcd(a, b)

def lcm_list(lst):
    result = lst[0]
    for x in lst[1:]:
        result = lcm(result, x)
    return result

def proper_divisors(n):
    divs = [1]
    for i in range(2, int(math.isqrt(n)) + 1):
        if n % i == 0:
            divs.append(i)
            if i != n // i:
                divs.append(n // i)
    return sorted(divs)

# ============================================================
# Task 1: k=3, 1 = 1/a + 1/b + 1/c, 1 <= a <= b <= c <= 1000
# ============================================================
def search_k3(limit=1000):
    print("=" * 60)
    print(f"Task 1: k=3, 1 = 1/a + 1/b + 1/c, a<=b<=c<={limit}")
    print("=" * 60)

    solutions = []
    perfect_solutions = []

    # a ranges from 1 to floor(3) since 1/a >= 1/3 => a <= 3
    # Actually 1/a + 1/b + 1/c = 1 with a<=b<=c means 1/a >= 1/3, so a<=3
    # But a=1 means 1/b+1/c=0, impossible for positive. So a>=2.
    # a=2: 1/b+1/c = 1/2, b<=c, 1/b >= 1/4 => b<=4, b>=2 (since b>=a=2... wait b>=a)
    #   Actually b>=a=2.
    # a=3: 1/b+1/c = 2/3, b>=3, 1/b >= 1/3 => b<=4... wait 1/b >= (2/3)/2=1/3 => b<=4
    #   but also b>=3

    for a in range(2, 4):  # a can be 2 or 3
        remainder_a = Fraction(1) - Fraction(1, a)
        # b >= a, and 1/b >= remainder_a / 2 => b <= 2/remainder_a
        b_max = min(limit, int(2 / remainder_a) + 1)
        for b in range(a, b_max + 1):
            remainder_b = remainder_a - Fraction(1, b)
            if remainder_b <= 0:
                continue
            # 1/c = remainder_b => c = 1/remainder_b
            c_frac = Fraction(1) / remainder_b
            if c_frac.denominator == 1:
                c = c_frac.numerator
                if c >= b and c <= limit:
                    L = lcm_list([a, b, c])
                    solutions.append((a, b, c, L))
                    if is_perfect(L):
                        perfect_solutions.append((a, b, c, L))

    print(f"\nTotal solutions found: {len(solutions)}")
    print("\nAll solutions:")
    for a, b, c, L in solutions:
        pf = " *** PERFECT ***" if is_perfect(L) else ""
        print(f"  1/{a} + 1/{b} + 1/{c} = 1, lcm={L}{pf}")

    print(f"\nSolutions with lcm = perfect number: {len(perfect_solutions)}")
    for s in perfect_solutions:
        print(f"  {s}")

    if len(perfect_solutions) == 1 and perfect_solutions[0][:3] == (2, 3, 6):
        print("\n>>> H-CX-482 CONFIRMED: {2,3,6} is the ONLY solution with perfect lcm <<<")
    else:
        print("\n>>> H-CX-482 STATUS: Check results above <<<")

    return solutions, perfect_solutions

# ============================================================
# Task 2: k=4, 1 = 1/a + 1/b + 1/c + 1/d, a<=b<=c<=d<=200
# ============================================================
def search_k4(limit=200):
    print("\n" + "=" * 60)
    print(f"Task 2: k=4, 1 = 1/a+1/b+1/c+1/d, a<=b<=c<=d<={limit}")
    print("=" * 60)

    solutions = []
    perfect_solutions = []

    # 1/a >= 1/4 => a <= 4, and a >= 2 (since a=1 leaves sum=0 for 3 positive terms...
    # actually a=1 leaves 0 for 3 terms which is impossible)
    for a in range(2, 5):
        rem_a = Fraction(1) - Fraction(1, a)
        b_max = min(limit, int(3 / rem_a) + 1)
        for b in range(a, b_max + 1):
            rem_b = rem_a - Fraction(1, b)
            if rem_b <= 0:
                continue
            c_max = min(limit, int(2 / rem_b) + 1)
            for c in range(b, c_max + 1):
                rem_c = rem_b - Fraction(1, c)
                if rem_c <= 0:
                    continue
                d_frac = Fraction(1) / rem_c
                if d_frac.denominator == 1:
                    d = d_frac.numerator
                    if d >= c and d <= limit:
                        L = lcm_list([a, b, c, d])
                        solutions.append((a, b, c, d, L))
                        if is_perfect(L):
                            perfect_solutions.append((a, b, c, d, L))

    print(f"\nTotal solutions found: {len(solutions)}")
    print(f"Solutions with lcm = perfect number: {len(perfect_solutions)}")
    if perfect_solutions:
        for s in perfect_solutions:
            print(f"  terms={s[:-1]}, lcm={s[-1]}")
    else:
        print("  NONE found.")

    # Show a few example solutions
    print(f"\nFirst 20 solutions (of {len(solutions)}):")
    for s in solutions[:20]:
        terms = s[:-1]
        L = s[-1]
        pf = " *** PERFECT ***" if is_perfect(L) else ""
        print(f"  1/{' + 1/'.join(str(t) for t in terms)} = 1, lcm={L}{pf}")

    return solutions, perfect_solutions

# ============================================================
# Task 3: k=5, 1 = sum 1/ai, ai <= 100 (smart pruning)
# ============================================================
def search_k5(limit=100):
    print("\n" + "=" * 60)
    print(f"Task 3: k=5, 1 = sum(1/ai), a1<=...<=a5<={limit}")
    print("=" * 60)

    solutions = []
    perfect_solutions = []
    count = 0

    for a in range(2, 6):  # a <= 5 since 5*(1/5)=1
        rem_a = Fraction(1) - Fraction(1, a)
        b_max = min(limit, int(4 / rem_a) + 1)
        for b in range(a, b_max + 1):
            rem_b = rem_a - Fraction(1, b)
            if rem_b <= 0:
                continue
            c_max = min(limit, int(3 / rem_b) + 1)
            for c in range(b, c_max + 1):
                rem_c = rem_b - Fraction(1, c)
                if rem_c <= 0:
                    continue
                d_max = min(limit, int(2 / rem_c) + 1)
                for d in range(c, d_max + 1):
                    rem_d = rem_c - Fraction(1, d)
                    if rem_d <= 0:
                        continue
                    e_frac = Fraction(1) / rem_d
                    if e_frac.denominator == 1:
                        e = e_frac.numerator
                        if e >= d and e <= limit:
                            L = lcm_list([a, b, c, d, e])
                            count += 1
                            if is_perfect(L):
                                perfect_solutions.append((a, b, c, d, e, L))
                                solutions.append((a, b, c, d, e, L))

    print(f"\nTotal solutions found: {count}")
    print(f"Solutions with lcm = perfect number: {len(perfect_solutions)}")
    if perfect_solutions:
        for s in perfect_solutions:
            terms = s[:-1]
            L = s[-1]
            print(f"  1/{' + 1/'.join(str(t) for t in terms)} = 1, lcm={L}")
    else:
        print("  NONE found.")

    return count, perfect_solutions

# ============================================================
# Task 4: Partial sums - 1/2 = sum 1/ai
# ============================================================
def search_half_sum_k3(limit=200):
    print("\n" + "=" * 60)
    print(f"Task 4a: k=3, 1/2 = 1/a+1/b+1/c, a<=b<=c<={limit}")
    print("=" * 60)

    target = Fraction(1, 2)
    solutions = []
    perfect_solutions = []

    for a in range(2, int(6) + 1):  # 1/a >= target/3 = 1/6
        rem_a = target - Fraction(1, a)
        if rem_a <= 0:
            continue
        b_max = min(limit, int(2 / rem_a) + 1)
        for b in range(a, b_max + 1):
            rem_b = rem_a - Fraction(1, b)
            if rem_b <= 0:
                continue
            c_frac = Fraction(1) / rem_b
            if c_frac.denominator == 1:
                c = c_frac.numerator
                if c >= b and c <= limit:
                    L = lcm_list([a, b, c])
                    solutions.append((a, b, c, L))
                    if is_perfect(L):
                        perfect_solutions.append((a, b, c, L))

    print(f"\nTotal solutions: {len(solutions)}")
    for a, b, c, L in solutions:
        pf = " *** PERFECT ***" if is_perfect(L) else ""
        print(f"  1/{a} + 1/{b} + 1/{c} = 1/2, lcm={L}{pf}")
    print(f"\nPerfect lcm solutions: {len(perfect_solutions)}")
    if perfect_solutions:
        for s in perfect_solutions:
            print(f"  terms=({s[0]},{s[1]},{s[2]}), lcm={s[3]}")

    return solutions, perfect_solutions

def search_half_sum_k4(limit=100):
    print(f"\nTask 4b: k=4, 1/2 = sum 1/ai, ai<={limit}")

    target = Fraction(1, 2)
    count = 0
    perfect_solutions = []

    for a in range(2, 9):  # 1/a >= target/4 = 1/8
        rem_a = target - Fraction(1, a)
        if rem_a <= 0:
            continue
        b_max = min(limit, int(3 / rem_a) + 1)
        for b in range(a, b_max + 1):
            rem_b = rem_a - Fraction(1, b)
            if rem_b <= 0:
                continue
            c_max = min(limit, int(2 / rem_b) + 1)
            for c in range(b, c_max + 1):
                rem_c = rem_b - Fraction(1, c)
                if rem_c <= 0:
                    continue
                d_frac = Fraction(1) / rem_c
                if d_frac.denominator == 1:
                    d = d_frac.numerator
                    if d >= c and d <= limit:
                        L = lcm_list([a, b, c, d])
                        count += 1
                        if is_perfect(L):
                            perfect_solutions.append((a, b, c, d, L))

    print(f"  Total solutions: {count}")
    print(f"  Perfect lcm solutions: {len(perfect_solutions)}")
    if perfect_solutions:
        for s in perfect_solutions:
            print(f"    terms={s[:-1]}, lcm={s[-1]}")

    return count, perfect_solutions

# ============================================================
# Task 5: Divisor reciprocal partition into exactly 3 terms = 1
# ============================================================
def check_divisor_partition(n):
    """
    For perfect number n, check if proper divisor reciprocals {1/d : d|n, d<n}
    can be partitioned into a subset of exactly 3 terms summing to 1.
    """
    divs = proper_divisors(n)
    recips = [Fraction(1, d) for d in divs]

    # Check all 3-element subsets
    found = []
    for combo in combinations_with_replacement(range(len(recips)), 3):
        # Actually we need combinations (not with replacement) since each divisor used once
        pass

    for combo in combinations(recips, 3):
        if sum(combo) == 1:
            found.append(combo)

    return divs, found

def all_divisors(n):
    divs = []
    for i in range(1, int(math.isqrt(n)) + 1):
        if n % i == 0:
            divs.append(i)
            if i != n // i:
                divs.append(n // i)
    return sorted(divs)

def task5_divisor_partition():
    print("\n" + "=" * 60)
    print("Task 5: Divisor reciprocal partition into 3 terms = 1")
    print("  For perfect number P, take {1/d : d | P} (all divisors).")
    print("  Can we choose exactly 3 reciprocals summing to 1?")
    print("=" * 60)

    for pn in [6, 28, 496, 8128]:
        divs = all_divisors(pn)
        print(f"\nPerfect number {pn}:")
        print(f"  All divisors: {divs}")
        recips = [Fraction(1, d) for d in divs]
        print(f"  Reciprocals: {[str(r) for r in recips]}")
        print(f"  sigma_{{-1}}({pn}) = {sum(recips)} (should be 2 for perfect numbers)")

        # Find all 3-element subsets summing to 1
        found_3 = []
        for combo in combinations(recips, 3):
            if sum(combo) == 1:
                found_3.append(combo)

        if found_3:
            print(f"  3-term subsets summing to 1: {len(found_3)}")
            for c in found_3:
                denoms = [x.denominator for x in c]
                print(f"    1/{denoms[0]} + 1/{denoms[1]} + 1/{denoms[2]} = 1")
        else:
            print(f"  3-term subsets summing to 1: NONE")

        # Also check k=4,5,6 for completeness
        max_k = min(6, len(recips))
        for k in range(4, max_k + 1):
            found_k = []
            for combo in combinations(recips, k):
                if sum(combo) == 1:
                    found_k.append(combo)
            if found_k:
                print(f"  {k}-term subsets summing to 1: {len(found_k)}")
                for c in found_k[:3]:
                    denoms = [x.denominator for x in c]
                    print(f"    {' + '.join('1/'+str(d) for d in denoms)} = 1")
                if len(found_k) > 3:
                    print(f"    ... and {len(found_k)-3} more")
            else:
                print(f"  {k}-term subsets summing to 1: NONE")

# ============================================================
# Task 6: Summary Table
# ============================================================
def print_summary(results):
    print("\n" + "=" * 60)
    print("SUMMARY TABLE")
    print("=" * 60)
    print(f"{'k':>3} | {'target':>8} | {'solutions':>10} | {'lcm=perf':>10} | {'which perfect':>20}")
    print("-" * 60)
    for row in results:
        k, target, nsol, nperf, which = row
        print(f"{k:>3} | {target:>8} | {nsol:>10} | {nperf:>10} | {which:>20}")

# ============================================================
# Main
# ============================================================
if __name__ == "__main__":
    t0 = time.time()
    summary = []

    # Task 1
    sol3, perf3 = search_k3(1000)
    which3 = ", ".join(f"{s[-1]}" for s in perf3) if perf3 else "NONE"
    summary.append((3, "1", len(sol3), len(perf3), which3))

    # Task 2
    sol4, perf4 = search_k4(200)
    which4 = ", ".join(f"{s[-1]}" for s in perf4) if perf4 else "NONE"
    summary.append((4, "1", len(sol4), len(perf4), which4))

    # Task 3
    count5, perf5 = search_k5(100)
    which5 = ", ".join(f"{s[-1]}" for s in perf5) if perf5 else "NONE"
    summary.append((5, "1", count5, len(perf5), which5))

    # Task 4
    sol_h3, perf_h3 = search_half_sum_k3(200)
    which_h3 = ", ".join(f"{s[-1]}" for s in perf_h3) if perf_h3 else "NONE"
    summary.append((3, "1/2", len(sol_h3), len(perf_h3), which_h3))

    count_h4, perf_h4 = search_half_sum_k4(100)
    which_h4 = ", ".join(f"{s[-1]}" for s in perf_h4) if perf_h4 else "NONE"
    summary.append((4, "1/2", count_h4, len(perf_h4), which_h4))

    # Task 5
    task5_divisor_partition()

    # Task 6
    print_summary(summary)

    elapsed = time.time() - t0
    print(f"\nTotal runtime: {elapsed:.1f}s")

    # Final verdict
    print("\n" + "=" * 60)
    print("FINAL VERDICT")
    print("=" * 60)

    all_perfect_count = len(perf3) + len(perf4) + len(perf5) + len(perf_h3) + len(perf_h4)
    if len(perf3) == 1 and perf3[0][:3] == (2, 3, 6) and len(perf4) == 0 and len(perf5) == 0:
        print("H-CX-482: CONFIRMED")
        print("  {2,3,6} is the ONLY k=3 solution with perfect lcm.")
        print()
        print("H-CX-486: CONFIRMED (within search bounds)")
        print("  No k=4 (limit=200) or k=5 (limit=100) solutions have perfect lcm.")
        print(f"  Total perfect-lcm solutions across all searches: {all_perfect_count}")
        print("  (Only {2,3,6} with lcm=6)")
    else:
        print("CHECK RESULTS ABOVE - unexpected findings!")
