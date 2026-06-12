# cert-pareto

A posteriori Pareto certificate checking for finite decision spaces, with
exact rational arithmetic, tolerance-aware floating point, worst-case robust
margins, zero-violation PAC audits and hash-pinned JSON certificate
artefacts.

[![CI](https://github.com/antonioclim/cert-pareto/actions/workflows/ci.yml/badge.svg)](https://github.com/antonioclim/cert-pareto/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/python-3.10%E2%80%933.13-blue)

## Statement of need

Multi-objective pipelines in engineering, economics and machine learning
routinely end with the sentence "the selected configuration is
Pareto-optimal". The sentence is rarely accompanied by anything a third
party could check. Optimisation libraries such as pymoo [(Blank & Deb,
2020)](#references) generate fronts; they were never designed to audit a
single externally supplied claim, to refuse gracefully when the claim is
unreachable by their machinery, or to emit a portable record of what was
and was not established. cert-pareto fills that narrow gap: it takes a
candidate, a declared certificate and a finite universe of alternatives,
and returns a typed verdict plus a hash-pinned JSON artefact. It generates
nothing and searches for nothing; both omissions are the design.

The package is small on purpose. Its contribution is not new mathematics
(the underlying results are textbook material; see Ehrgott, 2005 and
Miettinen, 1999) but a verdict discipline and an artefact discipline that
the textbook results, as usually coded, do not enforce.

## Installation

```bash
pip install -e ".[dev]"        # development install with test tooling
pip install -e .               # runtime only; zero third-party dependencies
```

The runtime depends only on the Python standard library (Python >= 3.10).
`matplotlib` is needed only to regenerate figures (`pip install -e ".[figures]"`).

## Reviewer quick check

A reviewer can reproduce the core checks from a clean clone with:

```bash
python -m pip install -e ".[dev]"
python -m pytest --cov=cert_pareto --cov-report=term-missing -q
python -m cert_pareto demo
python examples/export_certificate_demo.py
python -m cert_pareto verify results/certificate_artifact.json
```

The API reference is in [`docs/API.md`](docs/API.md). The JOSS pre-submission evidence checklist is in [`docs/JOSS_PRE_SUBMISSION_DOSSIER.md`](docs/JOSS_PRE_SUBMISSION_DOSSIER.md), and the local quality-assurance record is in [`docs/QUALITY_ASSURANCE.md`](docs/QUALITY_ASSURANCE.md).

## Quick start

```python
from cert_pareto import FiniteProblem, check_lagrangian_certificate, pareto_status

K = ("A", "B", "C")
F = {"A": (0, 1), "B": (1, 0), "C": ("3/5", "3/5")}
problem = FiniteProblem(K, (lambda x: F[x][0], lambda x: F[x][1]))

# C is Pareto-efficient by enumeration...
print(pareto_status(problem, "C", arithmetic="exact"))   # paretoEfficient

# ...yet no weighted-sum certificate can reach it: C is unsupported.
r = check_lagrangian_certificate(problem, "C", ("1/2", "1/2"), arithmetic="exact")
print(r.verdict)        # notCertifiedByThisCertificate
print(r.violators)      # ('A', 'B')
```

The asymmetry above is the package's defining behaviour: the second answer
refutes the certificate, not the candidate, and the verdict name says so.
Figure 2 in `figures/` draws the geometry: the level line of the
scalarisation through the unsupported point C passes strictly above the
hull face through A and B, so A and B always undercut it.

## Verdicts

| Verdict | Issued by | Meaning |
|---|---|---|
| `certifiedExactParetoEfficient` | exact backend | rational arithmetic, strictly positive weights: Pareto efficiency established |
| `certifiedExactWeaklyPareto` | exact backend | rational arithmetic, boundary weights: supported weak Pareto optimality |
| `certifiedParetoEfficientWithinTolerance` | float backend | IEEE 754 with declared `tol`; the suffix is the honesty clause |
| `certifiedWeaklyParetoWithinTolerance` | float backend | as above, boundary weights |
| `certifiedRobust` | `check_robust_certificate` | the margin survives every perturbation in the declared error model (`min_gap >= 2B`) |
| `inconclusiveWithinDeclaredErrors` | `check_defect_coverage` | a failed certificate whose defect the declared errors can explain: neither established nor refuted |
| `pacAuditedNoViolation` | `pac_zero_violation_audit` | violator mass at most epsilon under the audit distribution, confidence 1 - delta; distributional, never exhaustive |
| `notCertifiedByThisCertificate` | all checkers | the certificate fails; says nothing about domination |
| `infeasibleCandidate` | finite checker | feasibility failed before any Pareto judgement |
| `invalidInput` | all checkers | malformed certificate data, returned as a verdict so pipelines always receive a typed outcome |

The word "exact" never appears in a verdict produced by floating-point
arithmetic. The `tests/test_finite.py::test_tolerance_masks_violator_exact_catches_it`
test pins the distinction: an alternative undercutting the candidate by
5e-13 is certified within `tol = 1e-9` by the float backend and refused,
with the violator named, by the exact backend. Both answers are correct
for the question each backend asks.

## Exact arithmetic semantics

In `arithmetic="exact"` mode every value passes through
`fractions.Fraction` and every comparison is exact. A float input converts
to the rational it represents in binary, so the certified statement is:
exact over the values as supplied. Weights must sum to exactly one; pass
strings such as `"1/3"` (or `Fraction` objects) when decimal weights are
not dyadic - ten copies of `0.1` do not sum to one in binary and the
checker will say so rather than guess.

## Robustness: two questions, two functions

`check_robust_certificate(min_gap, lambdas, rho, ...)` certifies that a
passing certificate survives worst-case measurement error: with budget
`B = sum(lambda*rho) + sum(mu*rho')`, perturbation at both the candidate
and the comparison point can shift the gap by at most `2B`, so
`min_gap >= 2B` implies the true margin is non-negative. The factor 2 is
derived in the module docstring.

`check_defect_coverage(kappa, ...)` answers the opposite question about a
*failed* certificate: if the defect `kappa` lies within `B`, the data
cannot distinguish a failing certificate from measurement noise and the
verdict is `inconclusiveWithinDeclaredErrors` - explicitly not a
certification. Earlier prototypes of this package computed exactly this
quantity and over-claimed it as robust certification; the rename is
recorded in the changelog because the distinction is the point.

## Distributional audit

When the universe is too large to enumerate, fix an audit distribution Q
and sample. Zero violations in `M >= ln(1/delta)/epsilon` i.i.d. draws
support `Q(violators) <= epsilon` with confidence `1 - delta` (for
`epsilon = 0.01`, `delta = 0.05`: `M = 300`). The bound is conditional on
Q and on independence; it says nothing under distribution shift and it is
never exhaustive. The verdict message repeats these caveats because they
are the statement.

## Complexity and measured scaling

One certificate check is a single pass: Theta(|K| * (p + m_active)) with
O(1) memory beyond the result (violator identities are capped at 20 with
an explicit truncation flag; the count is always exact). Measured on a
commodity container (CPython 3.12, two objectives):

| K | float backend | exact backend |
|---|---|---|
| 10^3 | 1.1 ms | 5.9 ms |
| 10^4 | 10.1 ms | 60.9 ms |
| 10^5 | 98 ms | 0.62 s |
| 10^6 | 0.98 s | 6.1 s |

Roughly 1.0 microsecond per alternative in floating point and 6.1 in exact
rationals, linear across three orders of magnitude
(`benchmarks/benchmark_scaling.py`, `figures/figure4_benchmark.png`).

## Certificate artefacts

Every result can be wrapped into a JSON artefact carrying the package
version, a caller-chosen problem identifier, the full result and a SHA-256
digest over a canonical serialisation. The schema ships in
`schema/certificate-v1.schema.json` and each artefact pins its versioned
schema URI. `cert-pareto verify artefact.json` exits 0 or 1 for pipeline
use. A verified hash certifies the record, not the mathematics: validity
is re-established only by re-running the checker on the recorded inputs,
and the CLI says so every time it verifies.

## State of the field

Proof-logging verification in combinatorial optimisation - VeriPB and the
formally verified checker CakePB, recently extended to bi-objective
problems by Jabs and colleagues (2025) - provides per-inference proof
trails for solver runs, with guarantees far stronger than anything here.
cert-pareto sits below that line on purpose: it assumes no cooperating
solver and no proof trail, only a claim, declared data and a finite
universe, which is the situation of an auditor reading someone else's
report. KKT-residual measures such as KKTPM (Deb and colleagues, 2016)
quantify proximity to stationarity for continuous problems but provide
neither typed refusals nor portable artefacts. The scenario approach
(Campi & Garatti, 2008) supplies the probabilistic machinery the PAC audit
packages. Within FAIR for research software (Barker and colleagues, 2022),
cert-pareto is an instrument for making one specific class of claims
independently checkable.

## Limitations

The checker certifies supported points only; unsupported Pareto-efficient
points fail every weighted-sum certificate, and the package treats this as
information, not as failure to be papered over. Epsilon-constraint or
achievement-scalarisation certificates, which can reach unsupported
points, are out of scope for this release. The finite checker requires an
enumerable universe; the PAC audit requires an honestly declared sampling
distribution; the robust check requires honestly declared error bounds.
Garbage error declarations yield garbage robustness, a property shared
with every robust method since Bertsimas & Sim (2004).

## Repository layout

```
src/cert_pareto/     library (verdicts, finite, robust, pac, ratios, artefact, cli)
tests/               pytest suite + zero-dependency runner (python tests/run_tests.py)
examples/            seven runnable demonstrations
benchmarks/          scaling benchmark and figure generation
schema/              JSON Schema for certificate artefacts
paper/               JOSS paper (paper.md, paper.bib)
docs/                run logs regenerated at release time
```

## Contributing, conduct, citation

See `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md`. To cite the software, use
`CITATION.cff` (GitHub renders a citation widget from it); an archived,
DOI-stamped release is produced for each version via Zenodo as described
in `RELEASING.md`.

## Use of AI assistance

Portions of the implementation, tests and documentation were drafted with
the assistance of a large language model and were reviewed, executed and
edited by the author, who takes full responsibility for the content. A
dated disclosure accompanies the JOSS paper in `paper/paper.md`.

## References

Barker, M., Chue Hong, N. P., Katz, D. S., et al. (2022). Introducing the
FAIR principles for research software. *Scientific Data*, 9, 622.

Bertsimas, D., & Sim, M. (2004). The price of robustness. *Operations
Research*, 52(1), 35-53.

Blank, J., & Deb, K. (2020). pymoo: Multi-objective optimization in
Python. *IEEE Access*, 8, 89497-89509.

Campi, M. C., & Garatti, S. (2008). The exact feasibility of randomized
solutions of uncertain convex programs. *SIAM Journal on Optimization*,
19(3), 1211-1230.

Deb, K., Abouhawwash, M., & Dutta, J. (2016). An optimality theory-based
proximity measure for evolutionary multi-objective and many-objective
optimization. In *Evolutionary Multi-Criterion Optimization* (EMO 2015).

Ehrgott, M. (2005). *Multicriteria optimization* (2nd ed.). Springer.

Jabs, C., Berg, J., Bogaerts, B., & Jarvisalo, M. (2025). Certifying
Pareto optimality in multi-objective maximum satisfiability. In *Tools
and Algorithms for the Construction and Analysis of Systems* (TACAS 2025),
LNCS 15697, 108-129.

Miettinen, K. (1999). *Nonlinear multiobjective optimization*. Kluwer.
