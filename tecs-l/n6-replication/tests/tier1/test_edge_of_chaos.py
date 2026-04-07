"""H139: Golden Zone = edge of chaos (Langton lambda_c = 0.2738).

Langton's lambda_c is inside the Golden Zone and close to 1/e.
"""

from math import e, log


# Langton's critical lambda for edge of chaos
LAMBDA_C = 0.2738


class TestEdgeOfChaos:
    """Langton lambda_c is inside the Golden Zone."""

    def test_lambda_c_inside_golden_zone(self, golden_zone):
        """lambda_c approx 0.2738 is in [0.2123, 0.5]."""
        assert golden_zone["lower"] < LAMBDA_C < float(golden_zone["upper"])

    def test_lambda_c_close_to_one_over_e(self):
        """lambda_c is close to 1/e (within 0.1)."""
        assert abs(LAMBDA_C - 1 / e) < 0.1

    def test_golden_zone_width(self, golden_zone):
        """Golden Zone width = ln(4/3)."""
        assert abs(golden_zone["width"] - log(4 / 3)) < 1e-15

    def test_lambda_c_between_0_and_1(self):
        """lambda_c is a valid probability (between 0 and 1)."""
        assert 0 < LAMBDA_C < 1

    def test_lambda_c_near_golden_zone_center(self, golden_zone):
        """lambda_c is reasonably close to the Golden Zone center (1/e)."""
        distance = abs(LAMBDA_C - golden_zone["center"])
        # Within half the zone width
        assert distance < golden_zone["width"] / 2
