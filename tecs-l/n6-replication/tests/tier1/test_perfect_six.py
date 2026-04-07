"""H090: Master formula = perfect number 6.

sigma_{-1}(6) = 2, Euler product connection, perfect number properties.
"""

from fractions import Fraction


class TestSigmaMinus1:
    """sigma_{-1}(n) = sum of reciprocals of all divisors."""

    def test_sigma_minus1_of_6_equals_2(self, sigma_minus1):
        assert sigma_minus1(6) == Fraction(2, 1)

    def test_sigma_minus1_of_6_decomposition(self, n6_divisors):
        """1 + 1/2 + 1/3 + 1/6 = 2."""
        total = sum(Fraction(1, d) for d in n6_divisors)
        assert total == Fraction(2, 1)

    def test_sigma_minus1_of_28_equals_2(self, sigma_minus1):
        assert sigma_minus1(28) == Fraction(2, 1)


class TestEulerProduct:
    """Euler product: (1 + 1/2)(1 + 1/3) = (3/2)(4/3) = 2."""

    def test_euler_product_p2_p3(self):
        product = Fraction(3, 2) * Fraction(4, 3)
        assert product == Fraction(2, 1)

    def test_euler_product_expanded(self):
        """(1 + 1/p) for p in {2, 3}."""
        p2_factor = 1 + Fraction(1, 2)
        p3_factor = 1 + Fraction(1, 3)
        assert p2_factor * p3_factor == 2


class TestPerfectNumbers:
    """Perfect number properties: n = sum of proper divisors."""

    def test_6_is_perfect(self, n6_proper_divisors):
        assert sum(n6_proper_divisors) == 6

    def test_28_is_perfect(self, n28_divisors):
        proper = [d for d in n28_divisors if d != 28]
        assert sum(proper) == 28

    def test_sigma_minus1_equals_2_for_all_perfect(self, sigma_minus1):
        """sigma_{-1}(n) = 2 is equivalent to n being perfect."""
        for n in [6, 28, 496, 8128]:
            assert sigma_minus1(n) == Fraction(2, 1), f"Failed for n={n}"
