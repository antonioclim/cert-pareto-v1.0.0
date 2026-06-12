"""Worst-case robustness versus defect coverage: two different questions."""

import sys
import pathlib
# Runnable from a clean checkout; harmless once the package is installed.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from cert_pareto import (
    FiniteProblem,
    check_lagrangian_certificate,
    check_robust_certificate,
    check_defect_coverage,
)

K = ("A", "B", "C")
F = {"A": (0.0, 2.0), "B": (1.0, 1.0), "C": (2.0, 0.0)}
problem = FiniteProblem(K, (lambda x: F[x][0], lambda x: F[x][1]))

# 1. A passing certificate whose margin must survive declared measurement error.
base = check_lagrangian_certificate(problem, "A", (0.7, 0.3))
margin = float(base.margin)
print("modelled margin for A under (0.7, 0.3):", margin)
for rho in [(0.05, 0.05), (0.20, 0.20)]:
    r = check_robust_certificate(margin, (0.7, 0.3), rho)
    print(f"  rho={rho}: {r.verdict}  (R = margin - 2B = {r.margin:+.3f})")

# 2. A failing certificate whose defect may or may not be explained by error.
fail = check_lagrangian_certificate(problem, "B", (0.9, 0.1))
kappa = -float(fail.margin)
print(f"\nB under (0.9, 0.1) fails with defect kappa = {kappa:.2f}")
for rho in [(0.5, 0.5), (0.1, 0.1)]:
    r = check_defect_coverage(kappa, (0.9, 0.1), rho)
    print(f"  rho={rho}: {r.verdict}  (budget B = {r.error_budget:.2f})")
