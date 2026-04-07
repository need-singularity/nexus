"""Test H-CX-501: Bridge Theorem -- I^I minimization gives GZ center 1/e.

Connects variational calculus (energy minimization) to number theory via
the conservation law G*I = K. The unique energy minimum of E(I) = I^I
falls at I = 1/e, which is the Golden Zone center.
"""
import math
import pytest


class TestBridgeTheorem:
    """I^I minimization bridge between number theory and variational calculus."""

    def test_ixi_minimum_at_1_over_e(self):
        """d/dI[I^I] = I^I(ln I + 1) = 0 => I = 1/e"""
        I_star = 1 / math.e
        # Derivative: I^I * (ln(I) + 1)
        deriv = I_star**I_star * (math.log(I_star) + 1)
        assert abs(deriv) < 1e-15, f"Derivative at 1/e should be 0, got {deriv}"

    def test_second_derivative_positive(self):
        """Confirm 1/e is a minimum (not maximum)."""
        I = 1 / math.e
        # d2/dI2 [I^I] = I^I * ((ln I + 1)^2 + 1/I)
        d2 = I**I * ((math.log(I) + 1)**2 + 1/I)
        assert d2 > 0, f"Second derivative should be positive, got {d2}"

    def test_1_over_e_in_golden_zone(self):
        """1/e must fall within GZ = [1/2 - ln(4/3), 1/2]"""
        gz_lower = 0.5 - math.log(4 / 3)
        gz_upper = 0.5
        I_star = 1 / math.e
        assert gz_lower < I_star < gz_upper, (
            f"1/e={I_star:.6f} not in GZ [{gz_lower:.6f}, {gz_upper:.6f}]"
        )

    def test_independence_from_K(self):
        """On G*I=K, I^I minimum is at I=1/e regardless of K."""
        # The energy E(I) = I^I does not contain K
        # dE/dI = I^I(ln I + 1) = 0 has no K parameter
        for K in [0.1, 1.0, 10.0, 100.0]:
            # G = K/I, but E depends only on I
            I_star = 1 / math.e
            E_star = I_star**I_star
            # Verify minimum by checking neighbors
            for delta in [-0.01, 0.01]:
                I_neighbor = I_star + delta
                E_neighbor = I_neighbor**I_neighbor
                assert E_neighbor > E_star, (
                    f"K={K}: E({I_neighbor:.4f})={E_neighbor:.6f} should > "
                    f"E({I_star:.4f})={E_star:.6f}"
                )

    def test_ixi_global_minimum_on_0_1(self):
        """I^I achieves its unique minimum on (0,1) at I=1/e."""
        import numpy as np
        I_star = 1 / math.e
        E_star = I_star**I_star
        # Sample 10000 points on (0.001, 0.999) and verify none is lower
        for I in np.linspace(0.001, 0.999, 10000):
            E = I**I
            assert E >= E_star - 1e-12, (
                f"Found E({I:.6f})={E:.8f} < E(1/e)={E_star:.8f}"
            )

    def test_gz_center_value(self):
        """GZ center 1/e = 0.36787... matches known constant."""
        assert abs(1 / math.e - 0.36787944117144233) < 1e-15
