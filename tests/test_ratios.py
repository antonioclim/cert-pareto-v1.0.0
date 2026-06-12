"""Cross-product ratio comparison, including exact integer arithmetic."""

from fractions import Fraction

from cert_pareto import ratio_gap, compare_ratio
from _helpers import assert_raises


def test_sign_matches_ratio_difference():
    # 12/8 = 1.5 < 2 = 10/5
    assert ratio_gap(12, 8, 10, 5) < 0
    assert compare_ratio(12, 8, 10, 5) == "lower"
    assert compare_ratio(21, 10, 10, 5) == "higher"
    assert compare_ratio(4, 2, 10, 5) == "equal"


def test_exact_with_fractions_where_floats_blur():
    # 1/3 vs 333333.../10^18: floats see equality at double precision rounding,
    # the cross-product over exact integers does not.
    N0, D0 = 1, 3
    Nx, Dx = 333333333333333333, 10**18
    assert compare_ratio(Nx, Dx, N0, D0) == "lower"
    assert ratio_gap(Fraction(1, 3), Fraction(1), Fraction(1, 3), Fraction(1)) == 0


def test_guards():
    with assert_raises(ValueError):
        ratio_gap(1, 0, 1, 1)
    with assert_raises(ValueError):
        ratio_gap(1, 1, 1, -2)
    with assert_raises(TypeError):
        ratio_gap("12", 8, 10, 5)
    with assert_raises(TypeError):
        ratio_gap(True, 8, 10, 5)  # bool is excluded on purpose
