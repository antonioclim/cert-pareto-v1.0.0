"""Ratio comparison without division: exact where the quotient blurs."""

import sys
import pathlib
# Runnable from a clean checkout; harmless once the package is installed.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from cert_pareto import ratio_gap, compare_ratio

print("12/8 vs 10/5:", compare_ratio(12, 8, 10, 5), "| gap =", ratio_gap(12, 8, 10, 5))
N, D = 333333333333333333, 10**18
print("N/D vs 1/3 at 18 digits:", compare_ratio(N, D, 1, 3),
      "| exact integer gap =", ratio_gap(N, D, 1, 3))
print("float quotient sees:", N / D == 1 / 3)
