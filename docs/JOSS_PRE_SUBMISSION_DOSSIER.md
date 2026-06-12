# JOSS pre-submission dossier

This file collects evidence that reviewers commonly ask for in an open JOSS review. It should be completed immediately before submission and kept in the public repository.

## Public development history

- Repository URL: https://github.com/antonioclim/cert-pareto
- First public commit date: TODO: fill from GitHub history.
- First tagged release: TODO: fill after first public release.
- Public issues before submission: TODO: list issue numbers and topics.
- Pull requests before submission: TODO: list PR numbers and merge dates.
- Evidence of development over at least six months: TODO: fill from public commit log.

If the public history is shorter than the current JOSS pre-review requirement, do not submit yet. Continue developing in public, opening issues for planned work and making tagged pre-releases.

## Scope and significance evidence

- Deterministic examples: `examples/`.
- Benchmark to one million alternatives: `benchmarks/benchmark_scaling.py`.
- CLI verification path: `cert-pareto verify` and `python -m cert_pareto demo`.
- Typed verdict vocabulary: `src/cert_pareto/verdicts.py`.
- Exact-versus-tolerance branch: `tests/test_finite.py::test_tolerance_masks_violator_exact_catches_it`.
- Review/readiness use case: post hoc auditing of finite Pareto certificate claims.
- Teaching use case: supported versus unsupported Pareto-efficient points.

## Release evidence

- Version: 0.2.1.
- Release tag: TODO: v0.2.1 after repository is public and CI is green.
- Zenodo DOI: TODO: add version DOI after tagged GitHub release is archived.
- CITATION.cff synchronised: yes, verify before release.
- .zenodo.json synchronised: yes, verify before release.

## Reviewer smoke commands

```bash
python -m pip install -e ".[dev]"
python -m pytest --cov=cert_pareto --cov-report=term-missing -q
python -m cert_pareto demo
python examples/export_certificate_demo.py
python -m cert_pareto verify results/certificate_artifact.json
for f in examples/*.py; do python "$f"; done
```

## Known non-goals to state if asked

- The package does not generate Pareto fronts.
- The package does not search for certificate weights.
- The package does not emit proof logs comparable to VeriPB/CakePB.
- The package does not certify unsupported efficient points in v0.2.1.
- A valid artefact hash proves record integrity, not mathematical validity.
