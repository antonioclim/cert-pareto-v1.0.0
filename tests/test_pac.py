"""Zero-violation PAC audit: sample sizes, bounds, refusals."""

import math

from cert_pareto import Verdict, pac_sample_size, zero_violation_upper_bound, pac_zero_violation_audit
from _helpers import assert_raises


def test_sample_size_is_sound_and_documented_conservative():
    assert pac_sample_size(0.01, 0.05) == 300
    for eps, delta in [(0.01, 0.05), (0.05, 0.05), (0.5, 0.05), (0.01, 0.01)]:
        M = pac_sample_size(eps, delta)
        assert (1 - eps) ** M <= delta  # soundness of the certified statement
        exact_min = math.ceil(math.log(delta) / math.log(1 - eps))
        assert M >= exact_min  # conservative, as the docstring states
        assert M - exact_min <= math.ceil(exact_min * eps)  # and not wastefully so


def test_upper_bound_value():
    assert abs(zero_violation_upper_bound(300, 0.05) - math.log(20) / 300) < 1e-12


def test_audit_refuses_undersized_sample():
    r = pac_zero_violation_audit([False] * 100, epsilon=0.01, delta=0.05)
    assert r.verdict is Verdict.INVALID_INPUT


def test_audit_refuses_on_observed_violation():
    r = pac_zero_violation_audit([False] * 299 + [True], epsilon=0.01, delta=0.05)
    assert r.verdict is Verdict.NOT_CERTIFIED and r.violations_observed == 1


def test_audit_passes_clean_sufficient_sample():
    r = pac_zero_violation_audit([False] * 300, epsilon=0.01, delta=0.05)
    assert r.verdict is Verdict.PAC_AUDITED_NO_VIOLATION
    assert "i.i.d." in r.message and "not exhaustive" in r.message


def test_parameter_guards():
    with assert_raises(ValueError):
        pac_sample_size(0.0, 0.05)
    with assert_raises(ValueError):
        pac_sample_size(0.1, 1.0)
    with assert_raises(ValueError):
        zero_violation_upper_bound(0, 0.05)
