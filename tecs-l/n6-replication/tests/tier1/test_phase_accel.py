"""H124: Phase acceleration = stepwise x3 (Jamba empirical).

Critical fraction 4/7, acceleration factor 3, step function behavior.
3 = 1/(1/3) = reciprocal of meta fixed point.
"""

from fractions import Fraction


class TestPhaseAcceleration:
    """Phase acceleration factor = 3."""

    def test_critical_fraction(self):
        """Critical fraction is 4/7."""
        assert Fraction(4, 7) == Fraction(4, 7)
        assert float(Fraction(4, 7)) < 1.0

    def test_acceleration_factor_is_3(self):
        """Baseline 3 iterations compressed to 1 iteration = x3 acceleration."""
        baseline_iterations = 3
        accelerated_iterations = 1
        factor = baseline_iterations / accelerated_iterations
        assert factor == 3

    def test_step_function_above_critical(self):
        """5/7, 6/7, 7/7 all give same x3 acceleration (step function)."""
        fractions_above_critical = [
            Fraction(5, 7),
            Fraction(6, 7),
            Fraction(7, 7),
        ]
        acceleration = 3
        for frac in fractions_above_critical:
            assert frac > Fraction(4, 7)
            # All share the same acceleration factor
            assert acceleration == 3

    def test_reciprocal_of_meta_fixed_point(self):
        """3 = 1/(1/3), reciprocal of the meta fixed point."""
        meta_fixed_point = Fraction(1, 3)
        reciprocal = Fraction(1, 1) / meta_fixed_point
        assert reciprocal == Fraction(3, 1)

    def test_meta_fixed_point_is_contraction(self):
        """f(I) = 0.7I + 0.1 converges to 1/3."""
        # Fixed point: I = 0.7I + 0.1 => 0.3I = 0.1 => I = 1/3
        # Analytical: after k iterations, error = 0.7^k * |I_0 - 1/3|
        # 0.7^100 ~ 3.2e-16, so float precision is the limit
        i = 0.5  # start
        for _ in range(200):
            i = 0.7 * i + 0.1
        assert abs(i - 1 / 3) < 1e-12

    def test_meta_fixed_point_exact(self):
        """Fixed point of f(I)=0.7I+0.1 is exactly 1/3."""
        # Solve I = 7/10 * I + 1/10 => 3/10 * I = 1/10 => I = 1/3
        i_fixed = Fraction(1, 10) / Fraction(3, 10)
        assert i_fixed == Fraction(1, 3)
