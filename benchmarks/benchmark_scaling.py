"""Scaling benchmark for the certificate checker.

Measures wall time of one Lagrangian certificate check on universes of
size |K| from 10^3 to 10^6, two objectives, no constraints, both backends.
The check is a single pass, Theta(|K| * (p + m_active)); the benchmark
estimates the constant on the host. Emits a CSV and, with matplotlib
available, a log-log figure.

Run:  python benchmarks/benchmark_scaling.py [--max-exp 6] [--repeats 3]
"""

from __future__ import annotations

import argparse
import csv
import sys
import time
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cert_pareto import FiniteProblem, check_lagrangian_certificate  # noqa: E402


def build_problem(n: int, arithmetic: str) -> tuple[FiniteProblem, int]:
    """n alternatives on the line f1 + f2 = 1: f1 = i/(n-1), f2 = 1 - f1.

    Every point is supported and the middle candidate certifies under equal
    weights, so the timed pass exercises the full success path. The exact
    backend receives Fraction values: the same construction in floats is
    not exactly collinear once each i/(n-1) rounds to binary, and the exact
    checker rightly refuses it - a small live proof of why the two backends
    answer different questions.
    """
    if arithmetic == "exact":
        f1 = [Fraction(i, n - 1) for i in range(n)]
    else:
        f1 = [i / (n - 1) for i in range(n)]
    f2 = [1 - v for v in f1]
    K = tuple(range(n))
    problem = FiniteProblem(K, (lambda x: f1[x], lambda x: f2[x]))
    return problem, n // 2


def time_check(problem: FiniteProblem, candidate: int, arithmetic: str, repeats: int) -> float:
    best = float("inf")
    weights = ("1/2", "1/2") if arithmetic == "exact" else (0.5, 0.5)
    for _ in range(repeats):
        t0 = time.perf_counter()
        r = check_lagrangian_certificate(problem, candidate, weights, arithmetic=arithmetic)
        best = min(best, time.perf_counter() - t0)
        assert r.verdict.value.startswith("certified"), r.verdict
    return best


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-exp", type=int, default=6, help="largest |K| as a power of ten")
    ap.add_argument("--repeats", type=int, default=3)
    ap.add_argument("--csv", default="benchmarks/scaling.csv")
    ap.add_argument("--figure", default="figures/figure4_benchmark.png")
    args = ap.parse_args()

    rows = []
    for exp in range(3, args.max_exp + 1):
        n = 10**exp
        problem_f, candidate = build_problem(n, "float")
        t_float = time_check(problem_f, candidate, "float", args.repeats)
        problem_e, candidate = build_problem(n, "exact")
        t_exact = time_check(problem_e, candidate, "exact", max(1, args.repeats - 1))
        rows.append({"n": n, "seconds_float": t_float, "seconds_exact": t_exact,
                     "ns_per_alt_float": 1e9 * t_float / n, "ns_per_alt_exact": 1e9 * t_exact / n})
        print(f"|K|=10^{exp}: float {t_float:.4f}s ({rows[-1]['ns_per_alt_float']:.0f} ns/alt)  "
              f"exact {t_exact:.4f}s ({rows[-1]['ns_per_alt_exact']:.0f} ns/alt)")

    out = Path(args.csv)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print("csv:", out)

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib unavailable; skipped the figure")
        return 0
    fig, ax = plt.subplots(figsize=(5.4, 3.8))
    ns = [r["n"] for r in rows]
    ax.loglog(ns, [r["seconds_float"] for r in rows], "o-", label="float backend")
    ax.loglog(ns, [r["seconds_exact"] for r in rows], "s--", label="exact backend")
    ref = [rows[0]["seconds_float"] * n / ns[0] for n in ns]
    ax.loglog(ns, ref, ":", linewidth=1, label="linear reference")
    ax.set_xlabel("|K| (alternatives)")
    ax.set_ylabel("one certificate check (s)")
    ax.set_title("Single-pass scaling of the certificate check")
    ax.grid(True, which="both", linewidth=0.3)
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    Path(args.figure).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.figure, dpi=300)
    print("figure:", args.figure)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
