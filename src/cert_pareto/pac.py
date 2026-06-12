"""Zero-violation distributional audit (PAC-style).

Setting and derivation
----------------------
When ``K0`` is too large to enumerate, fix an audit distribution ``Q`` over
the feasible alternatives and let ``V`` be the set of violators of the
chosen certificate inequality. Draw ``M`` independent samples from ``Q``.
If ``Q(V) > epsilon`` then

    P(no sampled violator) = (1 - Q(V))^M < (1 - epsilon)^M <= e^(-epsilon M),

so taking ``M >= ln(1/delta) / epsilon`` forces ``e^(-epsilon M) <= delta``.
Contrapositively, observing zero violations in ``M`` such samples supports

    Q(V) <= epsilon     with confidence at least 1 - delta.

Equivalently, for a realised sample size ``M`` the tightest such bound is
``epsilon(M, delta) = ln(1/delta) / M``. The argument is the elementary
core of PAC learning (Valiant, 1984) and of the scenario approach to
uncertain programmes (Campi & Garatti, 2008); this module only packages it
with guard rails.

What the statement does not say
-------------------------------
The guarantee is conditional on independent, identically distributed
sampling from the declared ``Q``. It says nothing about alternatives that
``Q`` rarely visits, nothing under distribution shift and nothing
exhaustive: ``pacAuditedNoViolation`` is a statement about violator mass
under ``Q``, never a claim that ``V`` is empty. Choosing a ``Q`` whose mass
concentrates where violations are plausible is the auditor's burden, not
the software's.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

from .verdicts import Verdict


@dataclass(frozen=True)
class PACAuditResult:
    verdict: Verdict
    sample_size: int
    violations_observed: int
    epsilon: float
    delta: float
    message: str


def _check_unit_interval(name: str, value: float) -> None:
    if not (0.0 < value < 1.0):
        raise ValueError(f"{name} must lie strictly inside (0, 1); got {value!r}.")


def pac_sample_size(epsilon: float, delta: float) -> int:
    """Smallest integer M with M >= ln(1/delta)/epsilon.

    This is the classical bound obtained through the relaxation
    ``(1-epsilon)^M <= e^(-epsilon M)`` and is therefore mildly
    conservative: the exact minimal sample size for
    ``(1-epsilon)^M <= delta`` is ``ceil(ln(delta)/ln(1-epsilon))``, smaller
    by a factor approaching ``1 + epsilon/2`` (for epsilon=0.01,
    delta=0.05: 300 here versus 299 exactly). The conservative form is kept
    because it is the one auditors recognise and it errs on the safe side.
    """
    _check_unit_interval("epsilon", epsilon)
    _check_unit_interval("delta", delta)
    return math.ceil(math.log(1.0 / delta) / epsilon)


def zero_violation_upper_bound(M: int, delta: float) -> float:
    """The bound epsilon(M, delta) = ln(1/delta)/M certified by M clean draws."""
    if M <= 0:
        raise ValueError("M must be a positive integer.")
    _check_unit_interval("delta", delta)
    return math.log(1.0 / delta) / M


def pac_zero_violation_audit(violations: Sequence[bool], epsilon: float, delta: float) -> PACAuditResult:
    """Audit a sequence of sampled violation indicators against (epsilon, delta).

    ``violations[k]`` is True when the k-th independent draw from the audit
    distribution violated the certificate inequality. The function refuses
    to certify on an under-sized sample (``invalidInput``) and refuses to
    certify in the presence of any observed violator
    (``notCertifiedByThisCertificate``). Only ``M >= pac_sample_size`` and
    zero violations yield ``pacAuditedNoViolation``.
    """
    _check_unit_interval("epsilon", epsilon)
    _check_unit_interval("delta", delta)
    M = len(violations)
    required = pac_sample_size(epsilon, delta)
    observed = sum(bool(v) for v in violations)
    if M < required:
        return PACAuditResult(
            Verdict.INVALID_INPUT, M, observed, epsilon, delta,
            f"Audit supplied {M} samples but (epsilon={epsilon:g}, delta={delta:g}) "
            f"requires at least {required}.",
        )
    if observed:
        return PACAuditResult(
            Verdict.NOT_CERTIFIED, M, observed, epsilon, delta,
            f"{observed} sampled violator(s) observed; the zero-violation bound does not apply.",
        )
    return PACAuditResult(
        Verdict.PAC_AUDITED_NO_VIOLATION, M, 0, epsilon, delta,
        f"Zero violations in {M} i.i.d. draws from the declared audit distribution Q: "
        f"Q(V) <= {epsilon:g} with confidence at least {1 - delta:g}. The bound is "
        "distributional, conditional on Q and on independence; it is not exhaustive.",
    )
