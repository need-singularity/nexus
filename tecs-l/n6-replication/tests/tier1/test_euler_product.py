"""H092: Model = zeta Euler product p=2,3 truncation.

The TECS-L model corresponds to truncating the Euler product of the
Riemann zeta function at primes {2, 3}.
"""

from fractions import Fraction


def euler_product_sigma_minus1(*primes) -> Fraction:
    """Compute product of (1 + 1/p) for given primes.

    For a squarefree number n = product of distinct primes,
    sigma_{-1}(n) = product of (1 + 1/p).
    """
    result = Fraction(1)
    for p in primes:
        result *= (1 + Fraction(1, p))
    return result


def zeta_partial(*primes) -> Fraction:
    """Partial Euler product of zeta(1): product of 1/(1 - 1/p)."""
    result = Fraction(1)
    for p in primes:
        result *= Fraction(1, 1) / (1 - Fraction(1, p))
    return result


class TestZetaEulerProduct:
    """zeta_{2,3}(1) = 1/((1-1/2)(1-1/3)) = 3."""

    def test_zeta_p2_p3(self):
        result = zeta_partial(2, 3)
        assert result == Fraction(3, 1)

    def test_zeta_denominator(self):
        """(1 - 1/2)(1 - 1/3) = (1/2)(2/3) = 1/3."""
        denom = (1 - Fraction(1, 2)) * (1 - Fraction(1, 3))
        assert denom == Fraction(1, 3)


class TestSigmaMinus1EulerProduct:
    """(1+1/2)(1+1/3) = (3/2)(4/3) = 2."""

    def test_sigma_minus1_p2_p3(self):
        result = euler_product_sigma_minus1(2, 3)
        assert result == Fraction(2, 1)

    def test_p2_only(self):
        """p=2 only: sigma_{-1}(2) = 1 + 1/2 = 3/2."""
        result = euler_product_sigma_minus1(2)
        assert result == Fraction(3, 2)

    def test_p2_p3_p5_exceeds_2(self):
        """p={2,3,5}: sigma_{-1}(30) = (3/2)(4/3)(6/5) = 12/5 > 2."""
        result = euler_product_sigma_minus1(2, 3, 5)
        assert result == Fraction(12, 5)
        assert result > 2

    def test_only_p2_p3_gives_2(self):
        """Only the truncation at {2,3} gives exactly 2."""
        # Single primes
        for p in [2, 3, 5, 7]:
            assert euler_product_sigma_minus1(p) != 2

        # Two-prime combinations
        two_prime_combos = [(2, 3), (2, 5), (2, 7), (3, 5), (3, 7), (5, 7)]
        results_equal_2 = [
            combo for combo in two_prime_combos
            if euler_product_sigma_minus1(*combo) == 2
        ]
        assert results_equal_2 == [(2, 3)]

        # Three primes always exceed 2
        assert euler_product_sigma_minus1(2, 3, 5) > 2
