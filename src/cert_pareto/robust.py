"""Robustness diagnostics for finite Lagrangian certificates.

Two distinct statements live here, and conflating them was the one semantic
error in the 0.1.0 prototype. Both take a declared error model

    |F~_i(x) - F_i(x)|  <= rho_i        for every x in K,
    |g~_j(x) - g_j(x)|  <= rho'_j       for every x in K, j active,

where tildes denote the modelled (computed, measured) values and plain
symbols the true ones.

1. Worst-case robust certificate (:func:`check_robust_certificate`).
   Write L~ and L for the modelled and true Lagrangians under fixed
   weights ``lambda`` and multipliers ``mu``. For any x,

       |[L~(x) - L~(x0)] - [L(x) - L(x0)]|
           <= sum_i lambda_i * |F~_i(x) - F_i(x)|
            + sum_i lambda_i * |F~_i(x0) - F_i(x0)|
            + (same two sums for active constraints)
           <= 2 * (sum_i lambda_i rho_i + sum_j mu_j rho'_j) =: 2B.

   The factor 2 is the price of perturbation at both x and x0. Hence if
   the modelled certificate margin satisfies

       min_{x != x0} [L~(x) - L~(x0)]  >=  2B,

   the true margin is non-negative and the exact certificate survives every
   perturbation the error model allows. This is robustness in the
   worst-case tradition of Bertsimas and Sim (2004), specialised to a
   single supplied certificate rather than a full robust programme.

2. Defect coverage (:func:`check_defect_coverage`). When the modelled
   certificate FAILS with defect ``kappa = -min_gap > 0``, one may ask
   whether the failure is explicable by measurement error alone. If
   ``B >= kappa`` the data cannot distinguish "the certificate fails" from
   "the certificate holds but the measurements wobble", so the only honest
   verdict is ``inconclusiveWithinDeclaredErrors``. The 0.1.0 prototype
   computed exactly this quantity (``B - kappa``) but labelled a pass
   ``certifiedRobust``, which over-claims: covering a defect with error
   bars shows the claim is not refuted, never that it is established.
   Verdict renamed; arithmetic preserved.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .verdicts import Verdict


@dataclass(frozen=True)
class RobustResult:
    verdict: Verdict
    margin: float
    error_budget: float
    message: str


def _validate(lambdas: Sequence[float], rho: Sequence[float],
              multipliers: Sequence[float], rho_prime: Sequence[float]) -> None:
    if len(lambdas) != len(rho):
        raise ValueError("lambda and rho must have the same length.")
    if len(multipliers) != len(rho_prime):
        raise ValueError("mu and rho_prime must have the same length.")
    if any(r < 0 for r in rho) or any(r < 0 for r in rho_prime):
        raise ValueError("Error margins must be non-negative.")
    if any(weight < 0 for weight in lambdas) or any(m < 0 for m in multipliers):
        raise ValueError("Weights and multipliers must be non-negative.")


def error_budget(lambdas: Sequence[float], rho: Sequence[float],
                 multipliers: Sequence[float], rho_prime: Sequence[float]) -> float:
    """Return B = sum(lambda_i * rho_i) + sum(mu_j * rho'_j)."""
    _validate(lambdas, rho, multipliers, rho_prime)
    return float(sum(weight * margin for weight, margin in zip(lambdas, rho))
                 + sum(multiplier * margin for multiplier, margin in zip(multipliers, rho_prime)))


def check_robust_certificate(
    min_gap: float,
    lambdas: Sequence[float],
    rho: Sequence[float],
    multipliers: Sequence[float] = (),
    rho_prime: Sequence[float] = (),
) -> RobustResult:
    """Worst-case robust certificate: pass iff ``min_gap >= 2B``.

    ``min_gap`` is the modelled certificate margin reported by
    :func:`cert_pareto.finite.check_lagrangian_certificate` (the field
    ``margin``, as a float). A pass certifies that the exact certificate
    holds for every realisation of the true values inside the declared
    error model; see the module docstring for the two-line derivation of
    the factor 2.
    """
    B = error_budget(lambdas, rho, multipliers, rho_prime)
    R = float(min_gap) - 2.0 * B
    if R >= 0.0:
        return RobustResult(
            Verdict.CERTIFIED_ROBUST, R, B,
            "The modelled margin exceeds twice the error budget; the certificate "
            "survives every perturbation the declared error model allows.",
        )
    return RobustResult(
        Verdict.NOT_CERTIFIED, R, B,
        "The modelled margin does not cover the worst-case perturbation. This is a "
        "failed robust certificate, not evidence of domination.",
    )


def check_defect_coverage(
    kappa: float,
    lambdas: Sequence[float],
    rho: Sequence[float],
    multipliers: Sequence[float] = (),
    rho_prime: Sequence[float] = (),
) -> RobustResult:
    """Failed-certificate triage: is the defect within the error budget?

    ``kappa >= 0`` is the observed defect, the magnitude by which the
    modelled certificate inequality fails (``kappa = -min_gap`` for a
    failing check). With ``B >= kappa`` the declared errors suffice to
    explain the failure and the verdict is
    ``inconclusiveWithinDeclaredErrors``: the certificate is neither
    established nor refuted by these measurements. With ``B < kappa`` the
    failure exceeds what error can explain and the certificate is refuted
    at the modelled values (``notCertifiedByThisCertificate``).
    """
    if kappa < 0:
        raise ValueError("kappa is a defect magnitude and must be non-negative.")
    B = error_budget(lambdas, rho, multipliers, rho_prime)
    R = B - float(kappa)
    if R >= 0.0:
        return RobustResult(
            Verdict.INCONCLUSIVE_WITHIN_DECLARED_ERRORS, R, B,
            "The declared error budget covers the observed defect: the data cannot "
            "distinguish a failing certificate from measurement noise. Inconclusive, "
            "not certified.",
        )
    return RobustResult(
        Verdict.NOT_CERTIFIED, R, B,
        "The observed defect exceeds the declared error budget; the certificate is "
        "refuted at the modelled values.",
    )
