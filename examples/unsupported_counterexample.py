"""The package's defining test: a Pareto-efficient point no certificate reaches.

C = (3/5, 3/5) is Pareto-efficient by enumeration, yet it lies strictly above
the segment joining A = (0, 1) and B = (1, 0). Every weighted sum with
weights on the simplex attains a smaller value at A or at B, so every finite
Lagrangian certificate fails. The correct verdict is a statement about the
certificate family, not about C.
"""

import sys
import pathlib
# Runnable from a clean checkout; harmless once the package is installed.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from cert_pareto import FiniteProblem, check_lagrangian_certificate, pareto_status

K = ("A", "B", "C")
F = {"A": (0, 1), "B": (1, 0), "C": ("3/5", "3/5")}
problem = FiniteProblem(K, (lambda x: F[x][0], lambda x: F[x][1]))

print("C by exhaustive enumeration:", pareto_status(problem, "C", arithmetic="exact"))
for lam in (("1/2", "1/2"), ("1/5", "4/5"), ("4/5", "1/5"), ("99/100", "1/100")):
    r = check_lagrangian_certificate(problem, "C", lam, arithmetic="exact")
    print(f"weights {str(lam):24s} -> {r.verdict}  (violators: {', '.join(r.violators)})")
print("\nFailure of every tested certificate is not domination: that is the point.")
