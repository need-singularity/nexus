"""H067 + H072: Golden Zone constant relationships.

H067: 1/2 + 1/3 = 5/6 (constant relationship)
H072: 1/2 + 1/3 + 1/6 = 1 (curiosity creates completeness)
"""

from fractions import Fraction
from math import e, log


class TestH067ConstantRelationship:
    """1/2 + 1/3 = 5/6 and related identities."""

    def test_half_plus_third_equals_five_sixths(self):
        assert Fraction(1, 2) + Fraction(1, 3) == Fraction(5, 6)

    def test_subtraction_equals_multiplication(self):
        """1/2 - 1/3 = 1/6 = 1/2 * 1/3 (subtraction = multiplication)."""
        diff = Fraction(1, 2) - Fraction(1, 3)
        prod = Fraction(1, 2) * Fraction(1, 3)
        assert diff == Fraction(1, 6)
        assert prod == Fraction(1, 6)
        assert diff == prod


class TestH072CompletenessIdentity:
    """1/2 + 1/3 + 1/6 = 1 (completeness)."""

    def test_three_fractions_sum_to_one(self):
        assert Fraction(1, 2) + Fraction(1, 3) + Fraction(1, 6) == Fraction(1, 1)

    def test_boundary_plus_convergence_plus_curiosity(self):
        """boundary(1/2) + convergence(1/3) + curiosity(1/6) = complete(1)."""
        boundary = Fraction(1, 2)
        convergence = Fraction(1, 3)
        curiosity = Fraction(1, 6)
        assert boundary + convergence + curiosity == 1


class TestGoldenZoneStructure:
    """Golden Zone numerical structure."""

    def test_center_approx_one_over_e(self, golden_zone):
        assert abs(golden_zone["center"] - 1 / e) < 1e-15

    def test_width_equals_ln_four_thirds(self, golden_zone):
        assert abs(golden_zone["width"] - log(4 / 3)) < 1e-15

    def test_upper_minus_width_equals_lower(self, golden_zone):
        computed_lower = float(golden_zone["upper"]) - golden_zone["width"]
        assert abs(computed_lower - golden_zone["lower"]) < 1e-12

    def test_upper_is_one_half(self, golden_zone):
        assert golden_zone["upper"] == Fraction(1, 2)
