"""Fractional metric comparison via cross-products.

For ratio metrics ``r_h(x) = N_h(x) / D_h(x)`` with strictly positive
denominators, the comparison against a candidate ``x0`` is carried by the
cross-product gap

    Psi_h(x; x0) = N_h(x) * D_h(x0) - N_h(x0) * D_h(x),

whose sign equals the sign of ``r_h(x) - r_h(x0)`` without performing the
division. Two errors are avoided at once: the floating-point error of the
quotient, and the modelling error of optimising numerator and denominator
as if they were independent objectives when the ratio is the claim. With
integer or :class:`~fractions.Fraction` inputs the comparison is exact.
"""

from __future__ import annotations

from fractions import Fraction
from numbers import Real
from typing import Union

Number = Union[int, float, Fraction]


def _as_number(value: Number, what: str) -> Number:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{what} must be a real number, got {type(value).__name__}.")
    return value


def ratio_gap(N_x: Number, D_x: Number, N_0: Number, D_0: Number) -> Number:
    """Return Psi = N(x) * D(x0) - N(x0) * D(x); requires D_x > 0 and D_0 > 0.

    The result type follows the inputs: exact for int/Fraction, float
    otherwise. ``sign(Psi) == sign(r(x) - r(x0))`` because multiplying the
    difference of ratios by the positive product ``D(x) * D(x0)`` preserves
    sign.
    """
    N_x, D_x = _as_number(N_x, "N_x"), _as_number(D_x, "D_x")
    N_0, D_0 = _as_number(N_0, "N_0"), _as_number(D_0, "D_0")
    if D_x <= 0 or D_0 <= 0:
        raise ValueError("Denominators must be strictly positive.")
    return N_x * D_0 - N_0 * D_x


def compare_ratio(N_x: Number, D_x: Number, N_0: Number, D_0: Number, *, tol: float = 0.0) -> str:
    """Classify r(x) against r(x0) as 'lower', 'equal' or 'higher'.

    ``tol`` widens the equality band for floating-point inputs; leave at 0
    for exact inputs.
    """
    gap = ratio_gap(N_x, D_x, N_0, D_0)
    if gap < -tol:
        return "lower"
    if gap > tol:
        return "higher"
    return "equal"
