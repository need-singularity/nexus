"""Shared fixtures for Tier 1 tests (8 Major Discoveries)."""

from fractions import Fraction
from math import e, log

import pytest


@pytest.fixture
def n6_divisors():
    """All divisors of 6."""
    return [1, 2, 3, 6]


@pytest.fixture
def n6_proper_divisors():
    """Proper divisors of 6 (excluding 6 itself)."""
    return [1, 2, 3]


@pytest.fixture
def n28_divisors():
    """All divisors of 28."""
    return [1, 2, 4, 7, 14, 28]


@pytest.fixture
def golden_zone():
    """Golden Zone boundaries and constants."""
    width = log(Fraction(4, 3))
    return {
        "upper": Fraction(1, 2),
        "lower": 0.5 - log(4 / 3),
        "center": 1 / e,
        "width": width,
    }


@pytest.fixture
def sigma_minus1():
    """Function computing sigma_{-1}(n) = sum of 1/d for all divisors d of n."""

    def _sigma_minus1(n: int) -> Fraction:
        result = Fraction(0)
        for d in range(1, n + 1):
            if n % d == 0:
                result += Fraction(1, d)
        return result

    return _sigma_minus1
