"""Zero-violation audit: sample sizes, bounds and the refusal paths."""

import sys
import pathlib
# Runnable from a clean checkout; harmless once the package is installed.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

import random

from cert_pareto import pac_sample_size, zero_violation_upper_bound, pac_zero_violation_audit

for eps, delta in [(0.05, 0.05), (0.01, 0.05), (0.01, 0.01)]:
    print(f"epsilon={eps:<5} delta={delta:<5} -> M = {pac_sample_size(eps, delta)}")
for M in (100, 300, 1000):
    print(f"M={M:<5} delta=0.05 -> certified bound epsilon = {zero_violation_upper_bound(M, 0.05):.5f}")

rng = random.Random(7)
clean = [False] * 300
print("\nclean audit  :", pac_zero_violation_audit(clean, 0.01, 0.05).verdict)
one_bad = [rng.random() < 0.003 for _ in range(300)]
print("realistic    :", pac_zero_violation_audit(one_bad, 0.01, 0.05).verdict,
      f"({sum(one_bad)} violation(s) observed)")
print("undersized   :", pac_zero_violation_audit([False] * 50, 0.01, 0.05).verdict)
