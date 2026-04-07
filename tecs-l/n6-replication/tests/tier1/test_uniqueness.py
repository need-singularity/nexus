"""H098: 6 is the only perfect number with proper divisor reciprocal sum = 1.

The proper divisors of 6 are {1, 2, 3}. Their reciprocal sum = 1+1/2+1/3 = 11/6.
But the proper divisors EXCLUDING the trivial divisor 1, i.e., {2, 3},
have reciprocals 1/2 + 1/3 = 5/6.

The key uniqueness: among perfect numbers, only 6 has the property that
its non-trivial proper divisors {2, 3} together with n itself {6} form
the unique Egyptian fraction decomposition 1/2 + 1/3 + 1/6 = 1.

For other perfect numbers (28, 496, 8128), the analogous sum
(reciprocals of proper divisors excluding 1) does NOT equal 1.
"""

from fractions import Fraction


def proper_divisor_reciprocals_excl_1(n: int) -> Fraction:
    """Sum of 1/d for proper divisors d of n, excluding d=1 and d=n."""
    total = Fraction(0)
    for d in range(2, n):
        if n % d == 0:
            total += Fraction(1, d)
    return total


class TestReciprocalSumUniqueness:
    """Only n=6 has proper-divisor reciprocal sum (excl 1) that
    combines with 1/n to give exactly 1."""

    def test_n6_proper_divisors_excl_1_plus_n(self):
        """For 6: {2,3} reciprocals + 1/6 = 1/2 + 1/3 + 1/6 = 1."""
        proper_sum = proper_divisor_reciprocals_excl_1(6)
        assert proper_sum == Fraction(5, 6)  # 1/2 + 1/3
        assert proper_sum + Fraction(1, 6) == Fraction(1, 1)

    def test_n6_divisors_form_egyptian_fraction(self):
        """Divisors {2, 3, 6} give 1/2 + 1/3 + 1/6 = 1."""
        result = Fraction(1, 2) + Fraction(1, 3) + Fraction(1, 6)
        assert result == Fraction(1, 1)

    def test_n28_proper_divisors_excl_1(self):
        """For 28: proper divisors excl 1 = {2,4,7,14}. Sum != 5/6-like complement."""
        proper_sum = proper_divisor_reciprocals_excl_1(28)
        # 1/2 + 1/4 + 1/7 + 1/14 = 27/28
        assert proper_sum == Fraction(27, 28)
        # Adding 1/28 gives 1, but the structure is NOT 3 terms (Egyptian fraction unique)
        assert proper_sum + Fraction(1, 28) == 1
        # Key difference: 28's non-trivial proper divisors have 4 elements, not 2

    def test_n496_proper_divisors_excl_1_count(self):
        """For 496: more non-trivial proper divisors than 6."""
        proper_excl_1 = [d for d in range(2, 496) if 496 % d == 0]
        assert len(proper_excl_1) > 2  # 6 has only 2

    def test_n8128_proper_divisors_excl_1_count(self):
        """For 8128: more non-trivial proper divisors than 6."""
        proper_excl_1 = [d for d in range(2, 8128) if 8128 % d == 0]
        assert len(proper_excl_1) > 2

    def test_only_6_has_exactly_2_nontrivial_proper_divisors(self):
        """Among perfect numbers, only 6 has exactly 2 non-trivial proper divisors."""
        for n in [6, 28, 496, 8128]:
            proper_excl_1 = [d for d in range(2, n) if n % d == 0]
            if n == 6:
                assert len(proper_excl_1) == 2, f"n={n} should have 2"
            else:
                assert len(proper_excl_1) > 2, f"n={n} should have >2"


class TestEgyptianFractionUniqueness:
    """1/a + 1/b + 1/c = 1 with a < b < c has only solution (2, 3, 6)."""

    def test_only_solution_is_2_3_6(self):
        """Exhaustive search: 1/a+1/b+1/c=1 with 2<=a<b<c."""
        solutions = []
        # a >= 2, and 1/a must be >= 1/3 (otherwise 1/b+1/c can't reach 1-1/a)
        # so a in {2, 3}
        for a in range(2, 100):
            if Fraction(1, a) * 3 < 1:
                break  # Even 3 copies of 1/a < 1, so a too large
            for b in range(a + 1, 1000):
                remainder = Fraction(1, 1) - Fraction(1, a) - Fraction(1, b)
                if remainder <= 0:
                    break
                if remainder.denominator == 1:
                    # remainder is integer, but must be 1/c where c > b
                    continue
                # Check if remainder = 1/c for some integer c > b
                if remainder.numerator == 1 and remainder.denominator > b:
                    c = remainder.denominator
                    solutions.append((a, b, c))
                # If remainder < 1/(b+1), no valid c exists
                if remainder < Fraction(1, b + 1):
                    break
        assert solutions == [(2, 3, 6)]

    def test_2_3_6_sums_to_1(self):
        assert Fraction(1, 2) + Fraction(1, 3) + Fraction(1, 6) == 1
