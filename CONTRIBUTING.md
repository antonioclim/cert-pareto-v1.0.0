# Contributing to cert-pareto

Thank you for considering a contribution. The package is intentionally
small; contributions that preserve that property are the most welcome.

## Development setup

```bash
git clone https://github.com/antonioclim/cert-pareto
cd cert-pareto
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Running the checks

```bash
pytest --cov=cert_pareto          # full suite with coverage (CI gates at 95%)
python tests/run_tests.py         # same suite, zero third-party dependencies
ruff check src tests examples benchmarks tools
python -m build && python -m twine check dist/*
for f in examples/*.py; do python "$f"; done
```

## Ground rules

- The runtime must keep zero third-party dependencies. Test and figure
  tooling lives behind the `dev` and `figures` extras.
- Verdict semantics are the public contract. Any change to the `Verdict`
  vocabulary or to what a verdict claims requires a changelog entry, a
  schema update and tests pinning the new behaviour.
- The word "exact" may only describe results of the rational backend.
- New checkers must return typed verdicts for malformed input rather than
  raising, must document their mathematical contract in the module
  docstring, and must state explicitly what a passing verdict does not
  establish.

## Reporting issues

Use the GitHub issue tracker. For suspected wrong verdicts, include a
minimal `FiniteProblem` reproducing the behaviour and the artefact JSON if
one was produced; the artefact exists precisely for this conversation.

## Documentation changes

Public API changes must update `docs/API.md`, `README.md`, the JSON schema when artefact fields change and the JOSS evidence dossier when release or submission evidence changes.
