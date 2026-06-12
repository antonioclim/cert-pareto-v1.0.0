"""Why 'exact' is reserved for rational arithmetic.

Alternative A undercuts candidate B by 5e-13 in the weighted sum, three
orders of magnitude below tol = 1e-9. The float backend certifies within
tolerance; the exact backend refuses and names the violator. Both answers
are correct for the question each backend asks, and the verdict names keep
the two questions apart.
"""

import sys
import pathlib
# Runnable from a clean checkout; harmless once the package is installed.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from cert_pareto import FiniteProblem, check_lagrangian_certificate

K = ("A", "B")
F = {"A": (1.0 - 1e-12, 1.0), "B": (1.0, 1.0)}
problem = FiniteProblem(K, (lambda x: F[x][0], lambda x: F[x][1]))

f = check_lagrangian_certificate(problem, "B", (0.5, 0.5), arithmetic="float")
e = check_lagrangian_certificate(problem, "B", ("1/2", "1/2"), arithmetic="exact")
print("float backend :", f.verdict, "| margin =", f.margin)
print("exact backend :", e.verdict, "| margin =", e.margin, "| violators:", e.violators)
