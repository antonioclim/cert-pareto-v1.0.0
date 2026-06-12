"""Robust certificate (worst case) and defect coverage (inconclusive)."""

from cert_pareto import Verdict, check_robust_certificate, check_defect_coverage, error_budget
from _helpers import assert_raises


def test_error_budget_value():
    B = error_budget((0.5, 0.5), (0.03, 0.04), (1.0,), (0.02,))
    assert abs(B - (0.015 + 0.02 + 0.02)) < 1e-15


def test_robust_pass_requires_twice_budget():
    # B = 0.035; margin 0.07 == 2B passes, 0.0699 fails.
    ok = check_robust_certificate(0.070, (0.5, 0.5), (0.03, 0.04))
    assert ok.verdict is Verdict.CERTIFIED_ROBUST and abs(ok.margin) < 1e-12
    bad = check_robust_certificate(0.0699, (0.5, 0.5), (0.03, 0.04))
    assert bad.verdict is Verdict.NOT_CERTIFIED


def test_defect_coverage_is_inconclusive_not_certified():
    # Defect 0.03 within budget 0.055: inconclusive. Defect 0.06 beyond: refuted.
    r = check_defect_coverage(0.03, (0.5, 0.5), (0.03, 0.04), (1.0,), (0.02,))
    assert r.verdict is Verdict.INCONCLUSIVE_WITHIN_DECLARED_ERRORS
    assert r.verdict is not Verdict.CERTIFIED_ROBUST
    r2 = check_defect_coverage(0.06, (0.5, 0.5), (0.03, 0.04), (1.0,), (0.02,))
    assert r2.verdict is Verdict.NOT_CERTIFIED


def test_validation():
    with assert_raises(ValueError):
        check_robust_certificate(0.1, (0.5,), (0.1, 0.2))
    with assert_raises(ValueError):
        check_defect_coverage(-0.1, (1.0,), (0.1,))
    with assert_raises(ValueError):
        error_budget((0.5, 0.5), (-0.01, 0.0), (), ())


def test_zero_error_budget_boundary_cases():
    ok = check_robust_certificate(0.0, (1.0,), (0.0,))
    assert ok.verdict is Verdict.CERTIFIED_ROBUST
    refuted = check_defect_coverage(0.0, (1.0,), (0.0,))
    assert refuted.verdict is Verdict.INCONCLUSIVE_WITHIN_DECLARED_ERRORS


def test_negative_multiplier_rejected():
    with assert_raises(ValueError):
        error_budget((1.0,), (0.1,), (-0.5,), (0.1,))
