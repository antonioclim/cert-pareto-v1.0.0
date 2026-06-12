# Release and submission procedure

## Before any JOSS submission: the development-history requirement

JOSS expects a public repository with a genuine development history, not a
code drop made public the week of submission; reviewers check commit
dates. Publish this repository as early as possible, develop in the open
(issues, commits, tagged pre-releases) and let the record accumulate.
Several months of visible history is the realistic minimum. Submitting
earlier invites a desk reject regardless of software quality.

## Per-release checklist

1. Update `CHANGELOG.md`; bump the version in `pyproject.toml`,
   `src/cert_pareto/__init__.py`, `src/cert_pareto/artefact.py`
   (`SOFTWARE_VERSION`), `CITATION.cff`, `.zenodo.json` and `codemeta.json`.
2. Regenerate evidence: `python tests/run_tests.py`,
   `python benchmarks/benchmark_scaling.py`,
   `python benchmarks/generate_figures.py`; refresh `docs/` logs, `docs/QUALITY_ASSURANCE.md` and the
   benchmark table in `README.md` if the numbers moved.
3. Confirm the schema URI in `src/cert_pareto/artefact.py` resolves: it
   must point at `schema/certificate-v1.schema.json` on the default branch
   of the public repository. Adjust the GitHub username in the URI, in
   `pyproject.toml` URLs, in `CITATION.cff` and in the badges if the
   repository lives elsewhere.
4. Tag (`git tag v0.x.y && git push --tags`); verify CI is green on the tag.
5. Archive the tagged release on Zenodo (the `.zenodo.json` metadata is
   picked up automatically once the GitHub-Zenodo integration is enabled);
   record the version DOI in the README citation section.

## JOSS submission

- `paper/paper.md` and `paper/paper.bib` live in the repository and build
  with JOSS's compiler (test via the Open Journals web preview before
  submitting).
- The submission form asks for the repository URL, the archive DOI and the
  software version; use the tagged release and its Zenodo DOI.
- The AI-assistance disclosure in the paper satisfies JOSS's authorship
  policy; keep it accurate if tooling changes.


## JOSS-specific final check

Before submission, verify that `paper/paper.md` contains exactly the required sections: Summary, Statement of need, State of the field, Software design, Research impact statement, AI usage disclosure, Acknowledgements and References. Confirm that the paper is within the current JOSS word range, that the repository has sufficient public development history and that the submission uses a tagged release with a Zenodo DOI.
