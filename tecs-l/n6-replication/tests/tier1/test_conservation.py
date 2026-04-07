"""H172: G*I = D*P conservation law.

G = D*P/I implies G*I = D*P (algebraic identity / conservation law).
"""

import random

import pytest


class TestConservationAlgebraic:
    """G = D*P/I => G*I = D*P is an algebraic identity."""

    def test_basic_identity(self):
        d, p, i = 0.7, 0.8, 0.15
        g = d * p / i
        assert abs(g * i - d * p) < 1e-15

    def test_across_inhibition_range(self):
        """Test conservation across I in [0.1, 0.5]."""
        d, p = 0.6, 0.7
        for i_int in range(1, 6):  # 0.1, 0.2, 0.3, 0.4, 0.5
            i = i_int / 10.0
            g = d * p / i
            assert abs(g * i - d * p) < 1e-14, f"Failed at I={i}"

    def test_100_random_values(self):
        """Conservation holds for 100 random (D, P, I) values."""
        rng = random.Random(42)
        for _ in range(100):
            d = rng.uniform(0.01, 1.0)
            p = rng.uniform(0.01, 1.0)
            i = rng.uniform(0.01, 1.0)
            g = d * p / i
            assert abs(g * i - d * p) < 1e-12


class TestConservationEdgeCases:
    """Edge cases for G*I = D*P."""

    def test_high_inhibition(self):
        d, p, i = 0.5, 0.5, 0.99
        g = d * p / i
        assert abs(g * i - d * p) < 1e-14

    def test_low_inhibition(self):
        d, p, i = 0.5, 0.5, 0.01
        g = d * p / i
        assert abs(g * i - d * p) < 1e-12

    def test_equal_values(self):
        """When D=P=I, G=D and G*I=D*P=D^2."""
        val = 0.42
        g = val * val / val  # = val
        assert abs(g * val - val * val) < 1e-15
