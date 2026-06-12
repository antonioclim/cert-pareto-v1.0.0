"""Additional finite-checker guards for JOSS pre-submission hardening."""

from fractions import Fraction

from cert_pareto import FiniteProblem, Verdict, check_lagrangian_certificate, pareto_status
from _helpers import assert_raises


def test_exact_objective_and_constraint_vectors_are_fractional():
    problem = FiniteProblem(
        ("x",),
        (lambda x: "1/3", lambda x: 2),
        constraints=(lambda x: "0",),
    )
    assert problem.objective_vector("x", exact=True) == (Fraction(1, 3), Fraction(2, 1))
    assert problem.constraint_vector("x", exact=True) == (Fraction(0, 1),)
    assert problem.active_constraints("x", exact=True) == (0,)


def test_pareto_status_detects_weakly_pareto_but_dominated():
    K = ("x0", "x1")
    F = {"x0": (1, 1), "x1": (1, 0)}
    problem = FiniteProblem(K, (lambda x: F[x][0], lambda x: F[x][1]))
    assert pareto_status(problem, "x0", arithmetic="exact") == "weaklyParetoButDominated"


def test_active_constraint_index_out_of_range_is_typed_invalid_input():
    K = ("A", "B")
    F = {"A": (0, 0), "B": (1, 1)}
    problem = FiniteProblem(K, (lambda x: F[x][0], lambda x: F[x][1]), constraints=(lambda x: 0,))
    result = check_lagrangian_certificate(
        problem, "A", ("1/2", "1/2"), active_constraints=(3,), arithmetic="exact"
    )
    assert result.verdict is Verdict.INVALID_INPUT


def test_exact_negative_weight_and_multiplier_are_typed_invalid_input():
    K = ("A", "B")
    F = {"A": (0, 0), "B": (1, 1)}
    problem = FiniteProblem(K, (lambda x: F[x][0], lambda x: F[x][1]), constraints=(lambda x: 0,))
    result = check_lagrangian_certificate(problem, "A", ("-1/2", "3/2"), arithmetic="exact")
    assert result.verdict is Verdict.INVALID_INPUT
    result2 = check_lagrangian_certificate(
        problem, "A", ("1/2", "1/2"), multipliers=("-1",), arithmetic="exact"
    )
    assert result2.verdict is Verdict.INVALID_INPUT


def test_unconvertible_exact_value_raises_clear_value_error():
    problem = FiniteProblem(("A",), (lambda x: "not-a-number",))
    with assert_raises(ValueError):
        check_lagrangian_certificate(problem, "A", ("1",), arithmetic="exact")
