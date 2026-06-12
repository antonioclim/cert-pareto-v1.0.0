"""Typed verdicts for cert-pareto.

The verdict vocabulary is the package's central design decision. Each member
names exactly what was established and, by omission, what was not. Two rules
govern the vocabulary:

1. The word "exact" appears only in verdicts issued by the rational-arithmetic
   backend. Floating-point certification is reported "within tolerance".
2. A failed certificate is never reported as evidence of domination. The
   verdict ``notCertifiedByThisCertificate`` speaks about the certificate,
   not about the candidate.
"""

from __future__ import annotations

from enum import Enum


class Verdict(str, Enum):
    """Verdicts returned by cert-pareto checkers.

    Subclassing :class:`str` keeps members JSON-serialisable and printable
    as plain strings while preserving enum identity for comparisons.
    """

    # Exact rational arithmetic only (arithmetic="exact").
    CERTIFIED_EXACT_WEAKLY_PARETO = "certifiedExactWeaklyPareto"
    CERTIFIED_EXACT_PARETO_EFFICIENT = "certifiedExactParetoEfficient"

    # Floating point with an explicit tolerance (arithmetic="float").
    CERTIFIED_WEAKLY_PARETO_WITHIN_TOLERANCE = "certifiedWeaklyParetoWithinTolerance"
    CERTIFIED_PARETO_EFFICIENT_WITHIN_TOLERANCE = "certifiedParetoEfficientWithinTolerance"

    # Robust and distributional statements.
    CERTIFIED_ROBUST = "certifiedRobust"
    INCONCLUSIVE_WITHIN_DECLARED_ERRORS = "inconclusiveWithinDeclaredErrors"
    PAC_AUDITED_NO_VIOLATION = "pacAuditedNoViolation"

    # Negative and guard verdicts.
    NOT_CERTIFIED = "notCertifiedByThisCertificate"
    INFEASIBLE_CANDIDATE = "infeasibleCandidate"
    INVALID_INPUT = "invalidInput"

    def __str__(self) -> str:  # pragma: no cover - cosmetic
        return self.value


#: Verdicts that assert a positive certification claim.
POSITIVE_VERDICTS = frozenset(
    {
        Verdict.CERTIFIED_EXACT_WEAKLY_PARETO,
        Verdict.CERTIFIED_EXACT_PARETO_EFFICIENT,
        Verdict.CERTIFIED_WEAKLY_PARETO_WITHIN_TOLERANCE,
        Verdict.CERTIFIED_PARETO_EFFICIENT_WITHIN_TOLERANCE,
        Verdict.CERTIFIED_ROBUST,
        Verdict.PAC_AUDITED_NO_VIOLATION,
    }
)
