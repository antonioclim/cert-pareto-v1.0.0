"""Finite a posteriori Pareto certificate checking.

Mathematical contract
---------------------
Let ``K`` be a finite decision universe, ``K0`` the feasible subset under
inequality constraints ``g_j(x) <= 0`` and ``x0`` a feasible candidate.
Objectives ``F_1, ..., F_p`` are minimised. A finite Lagrangian certificate
consists of weights ``lambda_i >= 0`` with ``sum(lambda_i) == 1`` and
multipliers ``mu_j >= 0`` on the constraints active at ``x0``. With

    L(x) = sum_i lambda_i * F_i(x) + sum_{j active} mu_j * g_j(x)

the certificate passes when ``L(x0) <= L(x)`` for every ``x`` in ``K``. A
passing certificate establishes that ``x0`` is supported weakly
Pareto-optimal in ``K0`` (Ehrgott, 2005, ch. 3; Miettinen, 1999, ch. 2);
strictly positive weights strengthen the conclusion to Pareto efficiency.
The converse fails: Pareto-efficient points that are unsupported (not on the
convex hull of the attainable set) admit no such certificate, which is why a
failed certificate is reported as ``notCertifiedByThisCertificate`` and
never as domination.

Arithmetic backends
-------------------
``arithmetic="exact"``
    All values pass through :class:`fractions.Fraction` and every comparison
    is exact. A float input is converted to the rational it represents in
    binary, so the certified statement reads: exact over the values as
    supplied. Weights must sum to exactly one; pass ``Fraction`` or strings
    such as ``"1/3"`` when decimal weights are not dyadic. Only this backend
    may issue verdicts containing the word "exact".

``arithmetic="float"``
    IEEE 754 doubles with a declared, symmetric tolerance ``tol``. A gap
    ``L(x) - L(x0) >= -tol`` counts as non-violating; weight positivity and
    feasibility use the same ``tol``. The verdicts carry the suffix
    "WithinTolerance" because that is all floating point can promise.

Complexity
----------
One certificate check costs Theta(|K| * (p + m_active)) evaluations and the
same order of arithmetic operations, with O(1) extra memory beyond the
result (violator reporting is capped). The ``benchmarks`` directory measures
the constant.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from fractions import Fraction
from typing import Callable, Dict, Hashable, Literal, Sequence, Tuple

from .verdicts import Verdict

Alternative = Hashable
Number = float | int | Fraction | str
ObjectiveFn = Callable[[Alternative], Number]
ConstraintFn = Callable[[Alternative], Number]
Arithmetic = Literal["float", "exact"]

#: Default cap on the number of violators stored in a result. The count is
#: always reported; the identities are a sample, flagged by
#: ``violators_truncated`` when the cap binds.
VIOLATOR_CAP = 20


def _to_fraction(value: Number, what: str) -> Fraction:
    try:
        return Fraction(value)
    except (TypeError, ValueError) as exc:  # pragma: no cover - message path
        raise ValueError(f"{what} {value!r} is not convertible to an exact rational.") from exc


@dataclass(frozen=True)
class FiniteProblem:
    """A finite multi-objective decision problem.

    Parameters
    ----------
    alternatives:
        Every alternative in the finite universe ``K``.
    objectives:
        Objective functions to be minimised. They may return ``float``,
        ``int``, :class:`~fractions.Fraction` or numeric strings; the
        arithmetic backend decides how the values are interpreted.
    constraints:
        Inequality constraints ``g_j(x) <= 0``. With no constraints every
        alternative is feasible.
    """

    alternatives: Tuple[Alternative, ...]
    objectives: Tuple[ObjectiveFn, ...]
    constraints: Tuple[ConstraintFn, ...] = tuple()

    def __post_init__(self) -> None:
        if not self.alternatives:
            raise ValueError("The decision universe K must contain at least one alternative.")
        if not self.objectives:
            raise ValueError("At least one objective is required.")

    # -- value access -----------------------------------------------------
    def objective_vector(self, x: Alternative, *, exact: bool = False) -> tuple:
        if exact:
            return tuple(_to_fraction(f(x), "objective value") for f in self.objectives)
        return tuple(float(f(x)) for f in self.objectives)

    def constraint_vector(self, x: Alternative, *, exact: bool = False) -> tuple:
        if exact:
            return tuple(_to_fraction(g(x), "constraint value") for g in self.constraints)
        return tuple(float(g(x)) for g in self.constraints)

    # -- feasibility ------------------------------------------------------
    def is_feasible(self, x: Alternative, *, tol: float = 1e-9, exact: bool = False) -> bool:
        if exact:
            return all(_to_fraction(g(x), "constraint value") <= 0 for g in self.constraints)
        return all(float(g(x)) <= tol for g in self.constraints)

    def feasible_alternatives(self, *, tol: float = 1e-9, exact: bool = False) -> Tuple[Alternative, ...]:
        return tuple(x for x in self.alternatives if self.is_feasible(x, tol=tol, exact=exact))

    def active_constraints(
        self, x0: Alternative, *, tol: float = 1e-9, exact: bool = False
    ) -> Tuple[int, ...]:
        if exact:
            return tuple(
                j for j, g in enumerate(self.constraints) if _to_fraction(g(x0), "constraint value") == 0
            )
        return tuple(j for j, g in enumerate(self.constraints) if abs(float(g(x0))) <= tol)


@dataclass(frozen=True)
class CertificateResult:
    """Outcome of a finite Lagrangian certificate check.

    ``margin`` is the certificate margin ``min_{x != x0} L(x) - L(x0)``:
    at least 0 when an exact certificate passes, at least ``-tol`` when a
    tolerance certificate passes, and ``None`` when ``K = {x0}`` (the
    certificate then holds vacuously). ``violators`` holds
    at most :data:`VIOLATOR_CAP` offending alternatives; ``violator_count``
    is always the full count.
    """

    verdict: Verdict
    message: str
    candidate: str
    arithmetic: Arithmetic
    lambdas: Tuple[str, ...]
    active_constraints: Tuple[int, ...]
    multipliers: Tuple[str, ...]
    tol: float | None = None
    margin: str | None = None
    violator_count: int = 0
    violators: Tuple[str, ...] = tuple()
    violators_truncated: bool = False

    def as_dict(self) -> Dict[str, object]:
        d = asdict(self)
        d["verdict"] = self.verdict.value
        return d


def dominates(fx: Sequence, fy: Sequence, *, strict: bool = False, tol: float = 0.0) -> bool:
    """Return ``True`` when ``fx`` dominates ``fy`` under minimisation.

    With ``strict=False`` (Pareto domination): ``fx <= fy`` componentwise
    with at least one strict inequality. With ``strict=True``: strictly
    smaller in every component. ``tol`` widens comparisons symmetrically for
    floating-point inputs; leave it at 0 for exact values.
    """
    if len(fx) != len(fy):
        raise ValueError("Objective vectors must have the same dimension.")
    if strict:
        return all(a < b - tol for a, b in zip(fx, fy))
    return all(a <= b + tol for a, b in zip(fx, fy)) and any(a < b - tol for a, b in zip(fx, fy))


def pareto_status(
    problem: FiniteProblem,
    x0: Alternative,
    *,
    tol: float = 1e-9,
    arithmetic: Arithmetic = "float",
) -> str:
    """Diagnostic Pareto status of ``x0`` by exhaustive enumeration.

    This costs Theta(|K|^2) comparisons in the worst case and exists for
    tests and small demonstrations. It is a ground-truth oracle, not a
    certificate: it names a property of the candidate, whereas the checker
    names a property of a supplied certificate.
    """
    exact = arithmetic == "exact"
    cmp_tol = 0.0 if exact else tol
    if not problem.is_feasible(x0, tol=tol, exact=exact):
        return "infeasibleCandidate"
    f0 = problem.objective_vector(x0, exact=exact)
    feasible = problem.feasible_alternatives(tol=tol, exact=exact)
    others = [x for x in feasible if x != x0]
    if any(dominates(problem.objective_vector(x, exact=exact), f0, strict=True, tol=cmp_tol) for x in others):
        return "notWeaklyPareto"
    if any(dominates(problem.objective_vector(x, exact=exact), f0, strict=False, tol=cmp_tol)
           for x in others):
        return "weaklyParetoButDominated"
    return "paretoEfficient"


def _invalid(candidate: Alternative, arithmetic: Arithmetic, message: str) -> CertificateResult:
    return CertificateResult(
        verdict=Verdict.INVALID_INPUT,
        message=message,
        candidate=str(candidate),
        arithmetic=arithmetic,
        lambdas=tuple(),
        active_constraints=tuple(),
        multipliers=tuple(),
    )


def check_lagrangian_certificate(
    problem: FiniteProblem,
    candidate: Alternative,
    lambdas: Sequence[Number],
    *,
    multipliers: Sequence[Number] | None = None,
    active_constraints: Sequence[int] | None = None,
    arithmetic: Arithmetic = "float",
    tol: float = 1e-9,
    violator_cap: int = VIOLATOR_CAP,
) -> CertificateResult:
    """Check a supplied finite Lagrangian certificate for ``candidate``.

    The function verifies; it neither searches for the certificate nor
    interprets failure as domination. See the module docstring for the
    mathematical contract and the two arithmetic backends.

    Malformed problem data (wrong weight count, negative weights, weights
    not summing to one, mismatched multipliers) yields the verdict
    ``invalidInput`` rather than an exception, so pipelines receive a typed
    outcome for every call. Genuinely non-numeric values still raise.
    """
    exact = arithmetic == "exact"
    p = len(problem.objectives)

    # ---- validate weights ------------------------------------------------
    if len(lambdas) != p:
        return _invalid(candidate, arithmetic, f"Expected {p} objective weights, got {len(lambdas)}.")
    if exact:
        lam = tuple(_to_fraction(value, "objective weight") for value in lambdas)
        if any(weight < 0 for weight in lam):
            return _invalid(candidate, arithmetic, "Objective weights must be non-negative.")
        if sum(lam) != 1:
            return _invalid(
                candidate,
                arithmetic,
                "Exact mode requires weights summing to exactly one; "
                'use Fraction or strings such as "1/3" for non-dyadic weights.',
            )
        positive = all(weight > 0 for weight in lam)
    else:
        lam = tuple(float(value) for value in lambdas)
        if any(weight < -tol for weight in lam):
            return _invalid(candidate, arithmetic, "Objective weights must be non-negative.")
        if abs(sum(lam) - 1.0) > 1e-7:
            return _invalid(candidate, arithmetic, "Objective weights must sum to one (within 1e-7).")
        positive = all(weight > tol for weight in lam)

    # ---- membership and feasibility --------------------------------------
    if candidate not in problem.alternatives:
        return _invalid(candidate, arithmetic, "Candidate is not in the finite universe K.")
    if not problem.is_feasible(candidate, tol=tol, exact=exact):
        return CertificateResult(
            verdict=Verdict.INFEASIBLE_CANDIDATE,
            message="Candidate violates at least one feasibility constraint; no Pareto judgement was made.",
            candidate=str(candidate),
            arithmetic=arithmetic,
            lambdas=tuple(str(weight) for weight in lam),
            active_constraints=tuple(),
            multipliers=tuple(),
            tol=None if exact else tol,
        )

    # ---- multipliers on active constraints -------------------------------
    if active_constraints is None:
        active = problem.active_constraints(candidate, tol=tol, exact=exact)
    else:
        active = tuple(int(j) for j in active_constraints)
        if any(j < 0 or j >= len(problem.constraints) for j in active):
            return _invalid(candidate, arithmetic, "Active constraint index out of range.")
    if multipliers is None:
        mus = tuple(Fraction(0) if exact else 0.0 for _ in active)
    else:
        if len(multipliers) != len(active):
            return _invalid(
                candidate, arithmetic, "Number of multipliers must match the number of active constraints."
            )
        mus = tuple(
            _to_fraction(m, "multiplier") if exact else float(m) for m in multipliers
        )
        if (exact and any(m < 0 for m in mus)) or (not exact and any(m < -tol for m in mus)):
            return _invalid(candidate, arithmetic, "Constraint multipliers must be non-negative.")

    # ---- single pass over K ----------------------------------------------
    def lagrangian(x: Alternative):
        fx = problem.objective_vector(x, exact=exact)
        value = sum(weight * value for weight, value in zip(lam, fx))
        if active:
            gx = problem.constraint_vector(x, exact=exact)
            value += sum(m * gx[j] for m, j in zip(mus, active))
        return value

    l0 = lagrangian(candidate)
    threshold = 0 if exact else -tol
    min_gap = None  # min over x != x0; None when K = {x0}
    violator_count = 0
    sampled: list[str] = []
    for x in problem.alternatives:
        if x == candidate:
            continue
        gap = lagrangian(x) - l0
        if min_gap is None or gap < min_gap:
            min_gap = gap
        if gap < threshold:
            violator_count += 1
            if len(sampled) < violator_cap:
                sampled.append(str(x))

    common = dict(
        candidate=str(candidate),
        arithmetic=arithmetic,
        lambdas=tuple(str(weight) for weight in lam),
        active_constraints=active,
        multipliers=tuple(str(m) for m in mus),
        tol=None if exact else tol,
        margin=None if min_gap is None else str(min_gap),
        violator_count=violator_count,
        violators=tuple(sampled),
        violators_truncated=violator_count > len(sampled),
    )

    if violator_count:
        return CertificateResult(
            verdict=Verdict.NOT_CERTIFIED,
            message=(
                "At least one alternative attains a lower Lagrangian value under the supplied "
                "certificate. This refutes the certificate, not the candidate: unsupported "
                "Pareto-efficient points fail every weighted-sum certificate."
            ),
            **common,
        )
    if exact:
        verdict = (Verdict.CERTIFIED_EXACT_PARETO_EFFICIENT if positive
                   else Verdict.CERTIFIED_EXACT_WEAKLY_PARETO)
        message = (
            "Exact rational arithmetic verifies the supplied certificate"
            + (" with strictly positive weights: Pareto efficiency holds." if positive
               else ": supported weak Pareto optimality holds.")
        )
    else:
        verdict = (
            Verdict.CERTIFIED_PARETO_EFFICIENT_WITHIN_TOLERANCE
            if positive
            else Verdict.CERTIFIED_WEAKLY_PARETO_WITHIN_TOLERANCE
        )
        message = (
            f"Floating-point arithmetic verifies the supplied certificate within tol={tol:g}"
            + (" with strictly positive weights." if positive else ".")
        )
    return CertificateResult(verdict=verdict, message=message, **common)
