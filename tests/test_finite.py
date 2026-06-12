"""Finite checker: supported, unsupported, dominated, guards, margins."""

from fractions import Fraction

from cert_pareto import (
    FiniteProblem,
    Verdict,
    check_lagrangian_certificate,
    dominates,
    pareto_status,
)
from _helpers import assert_raises


def _toy_supported():
    K = ("A", "B", "C")
    F = {"A": (0.0, 2.0), "B": (1.0, 1.0), "C": (2.0, 0.0)}
    return FiniteProblem(K, (lambda x: F[x][0], lambda x: F[x][1]))


def _toy_unsupported():
    K = ("A", "B", "C")
    F = {"A": (0.0, 1.0), "B": (1.0, 0.0), "C": (0.6, 0.6)}
    return FiniteProblem(K, (lambda x: F[x][0], lambda x: F[x][1]))


def test_supported_point_certified_within_tolerance():
    r = check_lagrangian_certificate(_toy_supported(), "B", (0.5, 0.5))
    assert r.verdict is Verdict.CERTIFIED_PARETO_EFFICIENT_WITHIN_TOLERANCE
    assert r.arithmetic == "float" and r.tol == 1e-9
    assert float(r.margin) >= -1e-9 and r.violator_count == 0


def test_supported_point_certified_exact():
    r = check_lagrangian_certificate(_toy_supported(), "B", ("1/2", "1/2"), arithmetic="exact")
    assert r.verdict is Verdict.CERTIFIED_EXACT_PARETO_EFFICIENT
    assert Fraction(r.margin) == 0  # B sits on the segment between A and C


def test_boundary_weight_gives_weak_verdict_only():
    r = check_lagrangian_certificate(_toy_supported(), "A", ("1", "0"), arithmetic="exact")
    assert r.verdict is Verdict.CERTIFIED_EXACT_WEAKLY_PARETO


def test_unsupported_point_never_certified_yet_pareto():
    problem = _toy_unsupported()
    assert pareto_status(problem, "C", arithmetic="exact") == "paretoEfficient"
    for lam in (("1/2", "1/2"), ("1/5", "4/5"), ("9/10", "1/10")):
        r = check_lagrangian_certificate(problem, "C", lam, arithmetic="exact")
        assert r.verdict is Verdict.NOT_CERTIFIED
        assert r.violator_count >= 1


def test_dominated_point_diagnosed_by_enumeration():
    K = ("A", "B", "D")
    F = {"A": (0.0, 1.0), "B": (1.0, 0.0), "D": (1.5, 1.5)}
    problem = FiniteProblem(K, (lambda x: F[x][0], lambda x: F[x][1]))
    assert pareto_status(problem, "D") == "notWeaklyPareto"


def test_tolerance_masks_violator_exact_catches_it():
    """The reason 'exact' is reserved for the rational backend.

    Alternative A undercuts the candidate by 5e-13, far below tol=1e-9: the
    float path certifies within tolerance, the exact path refuses. Neither
    is wrong; they answer different questions, and the verdict names say so.
    """
    K = ("A", "B")
    F = {"A": (1.0 - 1e-12, 1.0), "B": (1.0, 1.0)}
    problem = FiniteProblem(K, (lambda x: F[x][0], lambda x: F[x][1]))
    r_float = check_lagrangian_certificate(problem, "B", (0.5, 0.5), arithmetic="float")
    assert r_float.verdict is Verdict.CERTIFIED_PARETO_EFFICIENT_WITHIN_TOLERANCE
    r_exact = check_lagrangian_certificate(problem, "B", ("1/2", "1/2"), arithmetic="exact")
    assert r_exact.verdict is Verdict.NOT_CERTIFIED
    assert Fraction(r_exact.margin) < 0


def test_exact_mode_rejects_inexact_weight_sum():
    problem = _toy_supported()
    # 0.1 and 0.9 as binary doubles sum to 1 + 2.77e-17, not to 1 exactly.
    r = check_lagrangian_certificate(problem, "B", (0.1, 0.9), arithmetic="exact")
    assert r.verdict is Verdict.INVALID_INPUT


def test_guard_verdicts():
    problem = _toy_supported()
    assert check_lagrangian_certificate(problem, "Z", (0.5, 0.5)).verdict is Verdict.INVALID_INPUT
    assert check_lagrangian_certificate(problem, "B", (0.5,)).verdict is Verdict.INVALID_INPUT
    assert check_lagrangian_certificate(problem, "B", (0.7, 0.7)).verdict is Verdict.INVALID_INPUT
    assert check_lagrangian_certificate(problem, "B", (-0.2, 1.2)).verdict is Verdict.INVALID_INPUT


def test_infeasible_candidate():
    K = ("A", "B")
    F = {"A": (0.0, 0.0), "B": (1.0, 1.0)}
    problem = FiniteProblem(
        K,
        (lambda x: F[x][0], lambda x: F[x][1]),
        constraints=(lambda x: 1.0 if x == "A" else -1.0,),  # A violates g <= 0
    )
    r = check_lagrangian_certificate(problem, "A", (0.5, 0.5))
    assert r.verdict is Verdict.INFEASIBLE_CANDIDATE


def test_active_constraint_multipliers_validated():
    K = ("A", "B")
    F = {"A": (0.0, 0.0), "B": (1.0, 1.0)}
    def active_constraint(x):
        return 0.0 if x == "A" else -1.0  # active at A

    problem = FiniteProblem(K, (lambda x: F[x][0], lambda x: F[x][1]), constraints=(active_constraint,))
    r = check_lagrangian_certificate(problem, "A", (0.5, 0.5), multipliers=(0.3,))
    assert r.active_constraints == (0,)
    assert r.verdict is Verdict.CERTIFIED_PARETO_EFFICIENT_WITHIN_TOLERANCE
    bad = check_lagrangian_certificate(problem, "A", (0.5, 0.5), multipliers=(0.3, 0.1))
    assert bad.verdict is Verdict.INVALID_INPUT


def test_violator_cap_and_count():
    n = 100
    K = tuple(range(n))
    problem = FiniteProblem(K, (lambda x: float(x), lambda x: float(x)))
    # Candidate n-1 is beaten by all others under any weights.
    r = check_lagrangian_certificate(problem, n - 1, (0.5, 0.5), violator_cap=5)
    assert r.verdict is Verdict.NOT_CERTIFIED
    assert r.violator_count == n - 1
    assert len(r.violators) == 5 and r.violators_truncated


def test_singleton_universe_vacuous_pass():
    problem = FiniteProblem(("only",), (lambda x: 0.0, lambda x: 0.0))
    r = check_lagrangian_certificate(problem, "only", (0.5, 0.5))
    assert r.margin is None and r.violator_count == 0
    assert r.verdict is Verdict.CERTIFIED_PARETO_EFFICIENT_WITHIN_TOLERANCE


def test_dominates_contract():
    assert dominates((0, 0), (1, 1))
    assert dominates((0, 1), (1, 1))
    assert not dominates((0, 1), (1, 0))
    assert not dominates((1, 1), (1, 1))
    assert dominates((0, 0), (1, 1), strict=True)
    with assert_raises(ValueError):
        dominates((0,), (1, 2))


def test_empty_problem_rejected():
    with assert_raises(ValueError):
        FiniteProblem(tuple(), (lambda x: 0.0,))
    with assert_raises(ValueError):
        FiniteProblem(("A",), tuple())
