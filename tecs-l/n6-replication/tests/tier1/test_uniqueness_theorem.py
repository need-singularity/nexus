"""Test H-CX-502: phi(n)*sigma(n) = n*tau(n) uniqueness at n=6.

Among all integers n >= 2, the identity phi(n)*sigma(n) = n*tau(n) holds
uniquely at n=6. This ties together the four fundamental multiplicative
arithmetic functions in a single equation that singles out the perfect number 6.
"""
import math
import pytest


def sigma(n):
    """Sum of all divisors of n."""
    return sum(d for d in range(1, n + 1) if n % d == 0)


def tau(n):
    """Number of divisors of n."""
    return sum(1 for d in range(1, n + 1) if n % d == 0)


def euler_phi(n):
    """Euler's totient: count of k in [1,n] with gcd(k,n)=1."""
    count = 0
    for k in range(1, n + 1):
        if math.gcd(k, n) == 1:
            count += 1
    return count


class TestUniquenessTheorem:
    """phi(n)*sigma(n) = n*tau(n) is uniquely satisfied by n=6 for n >= 2."""

    def test_n6_satisfies(self):
        """n=6: phi(6)=2, sigma(6)=12, tau(6)=4. LHS=24, RHS=24."""
        n = 6
        lhs = euler_phi(n) * sigma(n)
        rhs = n * tau(n)
        assert lhs == rhs, f"n=6: phi*sigma={lhs}, n*tau={rhs}"

    def test_n6_values(self):
        """Verify individual values for n=6."""
        assert euler_phi(6) == 2
        assert sigma(6) == 12
        assert tau(6) == 4
        assert 6 * 4 == 24
        assert 2 * 12 == 24

    def test_unique_up_to_1000(self):
        """Exhaustive check: n=6 is the only solution for 2 <= n <= 1000."""
        solutions = []
        for n in range(2, 1001):
            if euler_phi(n) * sigma(n) == n * tau(n):
                solutions.append(n)
        assert solutions == [6], f"Expected only [6], got {solutions}"

    def test_n28_fails(self):
        """n=28 (next perfect number) does not satisfy the equation."""
        n = 28
        assert euler_phi(n) * sigma(n) != n * tau(n), (
            f"n=28 should not satisfy phi*sigma=n*tau"
        )

    def test_n496_fails(self):
        """n=496 (third perfect number) does not satisfy the equation."""
        n = 496
        assert euler_phi(n) * sigma(n) != n * tau(n), (
            f"n=496 should not satisfy phi*sigma=n*tau"
        )

    def test_primes_fail(self):
        """Prime numbers do not satisfy the equation."""
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23]
        for p in primes:
            assert euler_phi(p) * sigma(p) != p * tau(p), (
                f"Prime p={p} should not satisfy phi*sigma=n*tau"
            )

    def test_powers_of_2_fail(self):
        """Powers of 2 do not satisfy the equation."""
        for k in range(1, 10):
            n = 2**k
            assert euler_phi(n) * sigma(n) != n * tau(n), (
                f"n=2^{k}={n} should not satisfy phi*sigma=n*tau"
            )

    def test_gap_magnitude_for_neighbors(self):
        """For n=5,7 (neighbors of 6), the gap |phi*sigma - n*tau| is nonzero."""
        for n in [5, 7]:
            gap = abs(euler_phi(n) * sigma(n) - n * tau(n))
            assert gap > 0, f"n={n} unexpectedly satisfies phi*sigma=n*tau"
