# Quality assurance record

## Local validation performed for v0.2.1 hardening

The following commands should pass before a public release:

```bash
python -m pytest --cov=cert_pareto --cov-report=term-missing -q
python -m compileall -q src tests examples benchmarks
python tests/run_tests.py
for f in examples/*.py; do python "$f" > /dev/null; done
python benchmarks/benchmark_scaling.py --max-exp 5 --repeats 1
```

The submission kit generated on 12 June 2026 passed the pytest suite with 44 tests and 98.64% overall coverage in the local container used for preparation. The zero-dependency runner passed 41 no-fixture tests and skipped three pytest-fixture tests, as intended. The exact values should be regenerated after any public repository changes.

## Test philosophy

The package is a checker. The highest-risk failures are therefore not numerical performance failures but false verdicts. Tests should cover:

- supported exact certificates;
- unsupported Pareto-efficient points that fail weighted-sum certificates;
- exact rational refusal where floating tolerance passes;
- invalid weights, invalid active constraints and invalid multipliers;
- robust pass versus defect-coverage inconclusiveness;
- under-sized PAC samples and observed PAC violations;
- artefact tampering;
- command-line exit codes.

## Packaging checks

If `build` and `twine` are available locally, run:

```bash
python -m build
python -m twine check dist/*
```

These commands are also included in the recommended CI workflow.

## Style and paper hygiene

The JOSS paper was checked with `tools/style_fingerprint_check.py`. For the v0.2.1 hardening kit, the script reported 834 prose words, 41 sentences, mean sentence length 19.37, sentence-length coefficient of variation 0.43, zero focal-word occurrences and zero counted generic phrase patterns. This script is not an authorship detector; it is a low-cost warning system for repetitive or over-smoothed prose.
