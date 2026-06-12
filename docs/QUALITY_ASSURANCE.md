# Quality assurance record

This document records the public validation discipline for `cert-pareto`. It is written for reviewers, contributors and future maintainers. It intentionally avoids local-machine paths and private preparation notes; every command below can be run from a fresh clone.

## Release validation commands

Run these commands before each tagged release:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m compileall -q src tests examples benchmarks
python -m pytest --cov=cert_pareto --cov-report=term-missing -q
ruff check src tests examples benchmarks
for f in examples/*.py; do python "$f" > /dev/null; done
python examples/export_certificate_demo.py > /dev/null
python -m cert_pareto verify results/certificate_artifact.json
python benchmarks/benchmark_scaling.py --max-exp 5 --repeats 1
python -m build
python -m twine check dist/*
```

## Test philosophy

The package is a checker. The highest-risk failures are false verdicts, not slow throughput. Tests therefore prioritise verdict semantics and edge cases:

- supported exact certificates;
- unsupported Pareto-efficient points that fail weighted-sum certificates;
- exact rational refusal where floating tolerance passes;
- invalid weights, invalid active constraints and invalid multipliers;
- robust pass versus defect-coverage inconclusiveness;
- under-sized PAC samples and observed PAC violations;
- artefact tampering;
- command-line exit codes.

## Packaging checks

Every release should build a source distribution and a wheel, then validate both with `twine check`. The CI workflow includes the same checks so that a broken distribution cannot be released accidentally.

## Benchmark policy

Benchmark results are reported as indicative, not as contractual performance guarantees. Absolute timings depend on processor, Python version and operating system. Scaling behaviour and reproducibility of the benchmark script matter more than a single timing value.

## Integrity policy

The JSON artefact hash verifies record integrity only. It does not prove mathematical validity, authorship authenticity or correctness of the underlying data. Mathematical validity is re-established only by re-running the checker on the recorded problem and certificate data.
