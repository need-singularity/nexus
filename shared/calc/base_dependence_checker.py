#!/usr/bin/env python3
"""
base_dependence_checker.py -- Tests if a numerical pattern is base-10 specific or universal.

Many "patterns" involving digits (digit sums, repunits, palindromes) are base-10
artifacts. This tool checks properties across multiple bases.

Usage:
  python3 calc/base_dependence_checker.py --number 12 --property digit_sum
  python3 calc/base_dependence_checker.py --number 6 --property all
  python3 calc/base_dependence_checker.py --identity "sigma(6)=12"
"""
import argparse
import math

# ── Bases to test ─────────────────────────────────────────────────────
DEFAULT_BASES = [2, 3, 6, 8, 10, 12, 16]

# ── Number theory helpers ─────────────────────────────────────────────
def to_base(n, base):
    """Convert non-negative integer n to digit list in given base (MSD first)."""
    if n == 0:
        return [0]
    digits = []
    val = abs(n)
    while val > 0:
        digits.append(val % base)
        val //= base
    return list(reversed(digits))


def digits_to_str(digits, base):
    """Convert digit list to string representation."""
    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if base <= len(alphabet):
        return "".join(alphabet[d] for d in digits)
    return ",".join(str(d) for d in digits)


def digit_sum(n, base):
    """Sum of digits of n in given base."""
    return sum(to_base(n, base))


def digital_root(n, base):
    """Iterated digit sum until single digit."""
    val = abs(n)
    while val >= base:
        val = digit_sum(val, base)
    return val


def is_palindrome(n, base):
    """Check if n is a palindrome in given base."""
    d = to_base(n, base)
    return d == d[::-1]


def is_repunit(n, base):
    """Check if n is a repunit (all 1s) in given base."""
    d = to_base(n, base)
    return all(x == 1 for x in d) and len(d) > 1


def is_repdigit(n, base):
    """Check if n is a repdigit (all same digit) in given base."""
    d = to_base(n, base)
    return len(set(d)) == 1 and len(d) > 1


def num_digits(n, base):
    """Number of digits of n in given base."""
    return len(to_base(n, base))


def sigma(n):
    """Sum of divisors of n."""
    if n <= 0:
        return 0
    total = 0
    for i in range(1, int(math.isqrt(n)) + 1):
        if n % i == 0:
            total += i
            if i != n // i:
                total += n // i
    return total


def is_perfect(n):
    """Check if n is a perfect number."""
    return n > 0 and sigma(n) == 2 * n


# ── Property checks ──────────────────────────────────────────────────
def check_digit_sum(n, bases):
    """Check digit sum across bases."""
    print(f"\n  Property: digit_sum({n})\n")
    results = {}
    for b in bases:
        ds = digit_sum(n, b)
        rep = digits_to_str(to_base(n, b), b)
        results[b] = ds
        marker = " <-- base 10" if b == 10 else ""
        print(f"    Base {b:>2}:  {rep:>12}  ->  digit_sum = {ds}{marker}")

    # Analysis
    values = list(results.values())
    unique = len(set(values))
    print(f"\n  Unique digit sums: {unique}/{len(bases)}")
    if unique == 1:
        print(f"  Result: UNIVERSAL -- digit sum = {values[0]} in ALL tested bases.")
    else:
        print(f"  Result: BASE-DEPENDENT -- digit sum varies across bases.")
    return results


def check_palindrome(n, bases):
    """Check palindrome property across bases."""
    print(f"\n  Property: is_palindrome({n})\n")
    pal_bases = []
    for b in bases:
        rep = digits_to_str(to_base(n, b), b)
        is_pal = is_palindrome(n, b)
        marker = "  PALINDROME" if is_pal else ""
        print(f"    Base {b:>2}:  {rep:>12}{marker}")
        if is_pal:
            pal_bases.append(b)

    print(f"\n  Palindrome in {len(pal_bases)}/{len(bases)} bases: {pal_bases or 'none'}")
    if len(pal_bases) == 0:
        print(f"  Result: NOT a palindrome in any tested base.")
    elif len(pal_bases) == len(bases):
        print(f"  Result: UNIVERSAL palindrome (trivially true for single-digit numbers).")
    elif 10 in pal_bases and len(pal_bases) == 1:
        print(f"  Result: BASE-10 ARTIFACT -- palindrome only in decimal.")
    else:
        print(f"  Result: PARTIALLY base-dependent.")
    return pal_bases


def check_repunit(n, bases):
    """Check repunit/repdigit property across bases."""
    print(f"\n  Property: is_repunit / is_repdigit({n})\n")
    for b in bases:
        rep = digits_to_str(to_base(n, b), b)
        ru = is_repunit(n, b)
        rd = is_repdigit(n, b)
        tags = []
        if ru:
            tags.append("REPUNIT")
        if rd and not ru:
            tags.append("REPDIGIT")
        tag_str = "  " + ", ".join(tags) if tags else ""
        print(f"    Base {b:>2}:  {rep:>12}{tag_str}")

    # Special note: repunits in base b are (b^k - 1)/(b - 1)
    print(f"\n  Note: {n} as repunit means {n} = (b^k-1)/(b-1) for some base b, k>=2.")
    for b in bases:
        if is_repunit(n, b):
            k = num_digits(n, b)
            print(f"    -> Base {b}: {n} = ({b}^{k}-1)/({b}-1)")


def check_digital_root(n, bases):
    """Check digital root across bases."""
    print(f"\n  Property: digital_root({n})\n")
    for b in bases:
        dr = digital_root(n, b)
        rep = digits_to_str(to_base(n, b), b)
        # Digital root formula: 1 + (n-1) % (b-1) for n > 0
        formula_dr = 1 + (n - 1) % (b - 1) if n > 0 else 0
        print(f"    Base {b:>2}:  {rep:>12}  ->  digital_root = {dr}  [= 1+({n}-1)%{b-1}]")


def check_all_properties(n, bases):
    """Run all property checks."""
    check_digit_sum(n, bases)
    check_palindrome(n, bases)
    check_repunit(n, bases)
    check_digital_root(n, bases)

    # Number-theoretic properties (base-independent by definition)
    print(f"\n  {'='*55}")
    print(f"  Base-INDEPENDENT properties of {n}:")
    print(f"  {'='*55}")
    print(f"    sigma({n})     = {sigma(n)}")
    print(f"    is_perfect({n}) = {is_perfect(n)}")
    print(f"    is_prime({n})  = {_is_prime(n)}")
    divs = [i for i in range(1, n + 1) if n % i == 0] if n > 0 else []
    print(f"    divisors({n})  = {divs}")
    if n > 0 and divs:
        proper = divs[:-1]
        recip_sum = sum(1 / d for d in proper) if proper else 0
        print(f"    proper_divisor_reciprocal_sum = {recip_sum:.6f}")

    print(f"\n  Key insight: sigma({n})={sigma(n)} is a NUMBER-THEORETIC fact (base-independent).")
    print(f"  Any digit-based pattern (digit sum, palindrome, repunit) is BASE-DEPENDENT.")


def _is_prime(n):
    """Simple primality test."""
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


# ── Identity checker ──────────────────────────────────────────────────
def check_identity(identity_str, bases):
    """Parse and check a simple identity like 'sigma(6)=12'."""
    print(f"\n{'='*65}")
    print(f"  Identity check: {identity_str}")
    print(f"{'='*65}")

    identity_str = identity_str.strip()

    # Parse sigma(n)=m
    if identity_str.startswith("sigma("):
        try:
            inner = identity_str.split("sigma(")[1]
            n_str, m_str = inner.split(")")
            m_str = m_str.strip().lstrip("=").strip()
            n = int(n_str)
            m = int(m_str)
        except (ValueError, IndexError):
            print(f"  Error: could not parse identity. Use format: sigma(6)=12")
            return

        actual = sigma(n)
        print(f"\n  sigma({n}) = {actual}  (claimed: {m})")
        if actual == m:
            print(f"  Identity is TRUE.")
        else:
            print(f"  Identity is FALSE! sigma({n}) = {actual}, not {m}.")
            return

        print(f"\n  Base-dependence analysis:")
        print(f"    The equality sigma({n})={m} is a number-theoretic FACT.")
        print(f"    It holds regardless of base representation.")
        print()
        print(f"  However, the DIGITS of {n} and {m} are base-dependent:")
        check_digit_sum(n, bases)
        check_digit_sum(m, bases)
    else:
        # Generic: try to evaluate as Python expression
        print(f"  Unrecognized identity format. Supported: sigma(n)=m")
        print(f"  Falling back to number analysis...")
        # Try to extract numbers
        import re
        nums = [int(x) for x in re.findall(r'\d+', identity_str)]
        for num in nums:
            print(f"\n  --- Analysis of {num} ---")
            check_all_properties(num, bases)


# ── CLI ───────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Base Dependence Checker -- tests if numerical patterns "
                    "are base-10 specific or universal.")
    parser.add_argument("--number", type=int,
                        help="Number to analyze")
    parser.add_argument("--property", type=str, default="all",
                        choices=["digit_sum", "palindrome", "repunit",
                                 "digital_root", "all"],
                        help="Property to check (default: all)")
    parser.add_argument("--identity", type=str,
                        help='Identity to check, e.g. "sigma(6)=12"')
    parser.add_argument("--bases", type=str, default=None,
                        help="Comma-separated bases to test (default: 2,3,6,8,10,12,16)")
    args = parser.parse_args()

    bases = DEFAULT_BASES
    if args.bases:
        bases = [int(b) for b in args.bases.split(",")]

    if args.identity:
        check_identity(args.identity, bases)
    elif args.number is not None:
        n = args.number
        print(f"\n{'='*65}")
        print(f"  Base Dependence Check: n = {n}")
        print(f"  Bases tested: {bases}")
        print(f"{'='*65}")

        prop = args.property
        if prop == "digit_sum":
            check_digit_sum(n, bases)
        elif prop == "palindrome":
            check_palindrome(n, bases)
        elif prop == "repunit":
            check_repunit(n, bases)
        elif prop == "digital_root":
            check_digital_root(n, bases)
        else:
            check_all_properties(n, bases)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
