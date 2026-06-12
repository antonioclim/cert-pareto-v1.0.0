"""Supported point, certified on both backends. B lies on the segment A-C."""

import sys
import pathlib
# Runnable from a clean checkout; harmless once the package is installed.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from cert_pareto import FiniteProblem, check_lagrangian_certificate, pareto_status

K = ("A", "B", "C", "D")
F = {"A": (0, 2), "B": (1, 1), "C": (2, 0), "D": (2, 2)}
problem = FiniteProblem(K, (lambda x: F[x][0], lambda x: F[x][1]))

exact = check_lagrangian_certificate(problem, "B", ("1/2", "1/2"), arithmetic="exact")
within = check_lagrangian_certificate(problem, "B", (0.5, 0.5), arithmetic="float")
print("exact backend  :", exact.verdict, "| margin =", exact.margin)
print("float backend  :", within.verdict, "| margin =", within.margin, "| tol =", within.tol)
print("enumeration    :", pareto_status(problem, "B", arithmetic="exact"))
