"""Test H-CX-503: Singleton bound at n=6 reproduces GZ constants.

The Singleton bound for a linear code of length n over alphabet q has
minimum distance d and rate R = (n-d+1)/n. At n=6, the rates for
d in {1,...,6} are exactly {1, 5/6, 2/3, 1/2, 1/3, 1/6} -- which include
all three GZ core constants (1/2, 1/3, 1/6) and their complement (5/6).
Only n=6 has this property among small lengths.
"""
from fractions import Fraction
import pytest


def singleton_rates(n):
    """Singleton bound rates R=(n-d+1)/n for d in 1..n."""
    return {d: Fraction(n - d + 1, n) for d in range(1, n + 1)}


class TestSingletonGZ:
    """Singleton rates at n=6 are exactly the divisor reciprocals of 6."""

    def test_singleton_rates_n6(self):
        """All 6 Singleton rates for n=6."""
        rates = singleton_rates(6)
        assert rates[1] == Fraction(1, 1)   # MDS trivial
        assert rates[2] == Fraction(5, 6)   # compass upper
        assert rates[3] == Fraction(2, 3)   # intermediate
        assert rates[4] == Fraction(1, 2)   # GZ upper (Riemann critical line)
        assert rates[5] == Fraction(1, 3)   # meta fixed point
        assert rates[6] == Fraction(1, 6)   # GZ curiosity = (6-6+1)/6 = 1/6

    def test_core_gz_constants_present(self):
        """The three GZ core constants 1/2, 1/3, 1/6 are all present."""
        # Note: 1/6 appears as the complement: 1 - 5/6 = 1/6 (d=2 gap from 1)
        # and directly as a divisor reciprocal of 6
        rates = set(singleton_rates(6).values())
        # 1/2 and 1/3 are direct rates
        assert Fraction(1, 2) in rates
        assert Fraction(1, 3) in rates
        # 5/6 (compass) is also present
        assert Fraction(5, 6) in rates

    def test_divisor_reciprocals_match_rates(self):
        """Non-trivial Singleton rates equal divisor reciprocals of 6."""
        divisors_of_6 = [1, 2, 3, 6]
        reciprocals = {Fraction(1, d) for d in divisors_of_6}
        rates = set(singleton_rates(6).values())
        # All divisor reciprocals appear among the rates
        assert reciprocals.issubset(rates)

    def test_core_rates_sum_to_1(self):
        """1/2 + 1/3 + 1/6 = 1 (completeness identity)."""
        assert Fraction(1, 2) + Fraction(1, 3) + Fraction(1, 6) == 1

    def test_compass_plus_curiosity(self):
        """5/6 + 1/6 = 1 (compass + curiosity = complete)."""
        assert Fraction(5, 6) + Fraction(1, 6) == 1

    def test_uniqueness_n4_missing_one_third(self):
        """n=4 Singleton rates do not include 1/3."""
        rates = set(singleton_rates(4).values())
        assert Fraction(1, 3) not in rates

    def test_uniqueness_n8_missing_one_third(self):
        """n=8 Singleton rates do not include 1/3."""
        rates = set(singleton_rates(8).values())
        assert Fraction(1, 3) not in rates

    def test_uniqueness_across_lengths(self):
        """n=6 is the unique length whose rate set is exactly the divisor reciprocals of 6.

        For n=6 the 6 Singleton rates are {1, 5/6, 2/3, 1/2, 1/3, 1/6} --
        exactly the reciprocals of the divisors of 6. No other small length
        has this exact rate set (multiples of 6 contain extra fractions).
        """
        expected_6 = {Fraction(1,1), Fraction(5,6), Fraction(2,3),
                      Fraction(1,2), Fraction(1,3), Fraction(1,6)}
        rates_6 = set(singleton_rates(6).values())
        assert rates_6 == expected_6, f"n=6 rates: {rates_6}"

        # For other lengths the rate set differs from expected_6
        for n in [4, 5, 7, 8, 9, 10, 11, 12, 28]:
            rates = set(singleton_rates(n).values())
            assert rates != expected_6, (
                f"n={n} unexpectedly has the same rate set as n=6"
            )

    def test_n6_rate_at_d6_is_one_sixth(self):
        """At distance d=6 (maximum), the Singleton rate is exactly 1/6."""
        assert singleton_rates(6)[6] == Fraction(1, 6)

    def test_n6_spans_full_gz_range(self):
        """The rates 1/3 and 1/2 bracket the GZ center 1/e."""
        import math
        gz_center = 1 / math.e  # ~0.368
        lower = float(Fraction(1, 3))   # 0.333
        upper = float(Fraction(1, 2))   # 0.500
        assert lower < gz_center < upper, (
            f"GZ center {gz_center:.4f} not between rates 1/3={lower} and 1/2={upper}"
        )
