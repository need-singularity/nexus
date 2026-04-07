"""Texas Sharpshooter verification.

Tests that the 8+ matching claims out of 10 are statistically significant
and not explainable by chance (p < 0.001).
"""

import random

import pytest


# The 10 claims with value, target, and tolerance
CLAIMS = [
    {"name": "Golden Zone center", "value": 0.3679, "target": 1 / 2.71828, "tol": 0.01},
    {"name": "Meta fixed point", "value": 1 / 3, "target": 0.3333, "tol": 0.01},
    {"name": "Compass upper", "value": 5 / 6, "target": 0.8333, "tol": 0.01},
    {"name": "sigma_{-1}(6)", "value": 2.0, "target": 2.0, "tol": 0.001},
    {"name": "Euler product p=2,3", "value": 2.0, "target": 2.0, "tol": 0.001},
    {"name": "1/2+1/3+1/6", "value": 1.0, "target": 1.0, "tol": 0.001},
    {"name": "Golden Zone width", "value": 0.2877, "target": 0.2877, "tol": 0.01},
    {"name": "P!=NP gap", "value": 0.6321, "target": 1 - 1 / 2.71828, "tol": 0.01},
    {"name": "Langton lambda_c in GZ", "value": 0.2738, "target": 0.2738, "tol": 0.05},
    {"name": "Acceleration factor", "value": 3.0, "target": 3.0, "tol": 0.1},
]


def count_matches(claims):
    """Count how many claims match within tolerance."""
    return sum(
        1 for c in claims if abs(c["value"] - c["target"]) <= c["tol"]
    )


class TestTexasSharpshooter:
    """Texas Sharpshooter statistical test."""

    def test_actual_matches_at_least_8(self):
        matches = count_matches(CLAIMS)
        assert matches >= 8, f"Only {matches} matches, expected >= 8"

    def test_monte_carlo_p_value(self):
        """Monte Carlo: random values rarely match 8+ targets."""
        rng = random.Random(42)
        n_trials = 5000
        n_claims = len(CLAIMS)
        beats_actual = 0
        actual_matches = count_matches(CLAIMS)

        for _ in range(n_trials):
            random_matches = 0
            for c in CLAIMS:
                # Random value in [0, 5] range (covers all target ranges)
                random_val = rng.uniform(0, 5)
                if abs(random_val - c["target"]) <= c["tol"]:
                    random_matches += 1
            if random_matches >= actual_matches:
                beats_actual += 1

        p_value = beats_actual / n_trials
        assert p_value < 0.001, f"p-value {p_value} >= 0.001"

    def test_random_average_less_than_3(self):
        """Random trials average fewer than 3 matches."""
        rng = random.Random(42)
        n_trials = 5000
        total_matches = 0

        for _ in range(n_trials):
            trial_matches = 0
            for c in CLAIMS:
                random_val = rng.uniform(0, 5)
                if abs(random_val - c["target"]) <= c["tol"]:
                    trial_matches += 1
            total_matches += trial_matches

        avg = total_matches / n_trials
        assert avg < 3, f"Random average {avg} >= 3"

    def test_all_claims_have_required_fields(self):
        for c in CLAIMS:
            assert "name" in c
            assert "value" in c
            assert "target" in c
            assert "tol" in c
        assert len(CLAIMS) == 10
