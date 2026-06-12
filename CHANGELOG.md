# Changelog

All notable changes to cert-pareto are documented here. The format follows
Keep a Changelog and the project adheres to semantic versioning.

## [0.2.1] - 2026-06-12

### Added
- JOSS-compliant paper sections: Software design, Research impact statement and AI usage disclosure.
- Public API reference in `docs/API.md`.
- JOSS pre-submission evidence dossier in `docs/JOSS_PRE_SUBMISSION_DOSSIER.md`.
- Local quality-assurance record in `docs/QUALITY_ASSURANCE.md`.
- Cross-platform CI matrix with Linux, macOS and Windows smoke tests.
- Build and distribution validation in CI through `python -m build` and `twine check`.
- `codemeta.json` for FAIR software metadata interoperability.
- Additional tests for module entry point, exact arithmetic guards, active-constraint validation, infeasible/weakly-dominated diagnostics and robustness boundary cases.

### Changed
- Version synchronised across `pyproject.toml`, `__init__.py`, artefact metadata, `CITATION.cff` and `.zenodo.json`.
- Paper title and repository metadata now emphasise exact and tolerance-aware certificate checking rather than general Pareto optimality.
- README now includes reviewer quick-check commands and explicit links to API, QA and JOSS evidence documents.

### Fixed
- Replaced the older AI-assistance wording in the paper with the exact JOSS-required heading `AI usage disclosure`.
- Tightened wording around artefact integrity: the hash verifies the record, not the mathematics.

## [0.2.0] - 2026-06-12

### Added
- Exact rational arithmetic backend (`arithmetic="exact"`) built on
  `fractions.Fraction`. The verdicts `certifiedExactWeaklyPareto` and
  `certifiedExactParetoEfficient` are now issued only by this backend.
- `Verdict` enumeration in `cert_pareto.verdicts`; every checker returns a
  member of this enumeration rather than a bare string.
- `check_defect_coverage` in `cert_pareto.robust`, returning the new verdict
  `inconclusiveWithinDeclaredErrors`: a failed exact certificate whose defect
  lies within the declared error budget is reported as inconclusive, not as
  certified. This replaces the 0.1.0 robust check, whose pass condition had
  the same arithmetic but an over-strong name.
- Worst-case robust certificate `check_robust_certificate` with the derived
  pass condition `min_gap >= 2 * (sum(lambda*rho) + sum(mu*rho_prime))` and a
  full derivation in the docstring.
- JSON Schema for certificate artefacts (`schema/certificate-v1.schema.json`)
  and a resolvable schema URI embedded in every artefact.
- Command line interface: `cert-pareto verify <artefact.json>` and
  `cert-pareto demo`.
- Benchmark script scaling the exact and tolerance checkers to |K| = 10^6,
  with CSV output and an optional figure.
- pytest suite (7 modules), GitHub Actions CI across Python 3.10-3.13 with
  lint, coverage gate at 90 percent and example smoke tests.
- Violator reporting is capped (default 20 entries) with an explicit
  `violators_truncated` flag, so large instances do not bloat results.

### Changed
- **Breaking**: `PADAuditResult` renamed to `PACAuditResult` (typo fix; the
  0.1.x name was never in a public release).
- **Breaking**: floating-point certification verdicts renamed to
  `certifiedWeaklyParetoWithinTolerance` and
  `certifiedParetoEfficientWithinTolerance`, reserving the word "exact" for
  the rational backend.
- Package moved to a `src/` layout; licence fixed to MIT everywhere.

## [0.1.0] - 2026-06-11
- Initial research prototype: finite Lagrangian check, robust margin, PAC
  helpers, ratio comparison, JSON artefact export, terminal examples.
