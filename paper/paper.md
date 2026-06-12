---
title: 'cert-pareto: exact and tolerance-aware certificate checking for Pareto claims in finite decision spaces'
tags:
  - Python
  - multi-objective optimisation
  - Pareto optimality
  - certificate checking
  - exact arithmetic
  - reproducibility
authors:
  - name: Antonio Clim
    orcid: 0000-0003-4745-0431
    affiliation: 1
affiliations:
  - name: Department of Economic Informatics and Cybernetics, Bucharest University of Economic Studies, Romania
    index: 1
date: 12 June 2026
bibliography: paper.bib
---

# Summary

`cert-pareto` checks a narrow claim that appears often in multi-objective research: a reported candidate is said to be Pareto-optimal, yet the statement is not accompanied by a record that another reader can verify. The package takes a finite set of alternatives, a candidate, declared objective weights and optional active-constraint multipliers. It then checks the finite Lagrangian certificate and returns a typed verdict rather than a plot or a score. Exact rational arithmetic is separated from tolerance-aware floating-point checks, robust margins are reported under declared error budgets, zero-violation PAC audits are available when enumeration is replaced by sampling and ratio metrics are compared through cross-products. The output can be written as a hash-pinned JSON artefact for later integrity checking. The package does not construct Pareto fronts, optimise designs or search for certificates.

# Statement of need

Optimisation libraries such as `pymoo` [@Blank2020] search for or approximate Pareto sets. They are not designed to audit one externally supplied claim, refuse it with a precise reason or leave behind a portable certificate record. `cert-pareto` is written for that downstream position: a reviewer, modeller or teaching example already has a candidate and wants to know which certificate statement, if any, follows from the declared finite universe.

The mathematics behind the supported-point certificate is classical [@Ehrgott2005; @Miettinen1999]. The software contribution is the discipline around the claim. A failed weighted-sum certificate returns `notCertifiedByThisCertificate`, because unsupported Pareto-efficient points may fail every such certificate while remaining efficient. Floating-point checks never receive an `exact` verdict. A failed certificate whose defect lies inside a declared error budget returns `inconclusiveWithinDeclaredErrors`, not a robust pass. These distinctions are the package's central behaviour.

# State of the field

The closest verification neighbour is proof logging in combinatorial optimisation. The VeriPB/CakePB line can verify solver derivations, and Jabs, Berg, Bogaerts and Järvisalo [@Jabs2025] extended that approach to bi-objective maximum satisfiability. Those guarantees are stronger than the ones offered here, because they concern a proof-producing solver run. `cert-pareto` addresses a different audit setting: no proof log, no co-operating solver and no assumption that the candidate was produced by a particular optimiser.

A second neighbour is optimality-proximity measurement for continuous multi-objective problems, including KKTPM as implemented in `pymoo` [@Deb2016]. Such measures quantify stationarity or nearness to a continuous optimum; they do not return a finite certificate verdict or a reusable artefact. The zero-violation audit in `cert-pareto` packages the elementary PAC bound [@Valiant1984] in the spirit of scenario methods for uncertain programmes [@Campi2008], while the robust-error budget follows the worst-case tradition of @Bertsimas2004. The artefact and metadata choices follow FAIR-for-research-software practice [@Barker2022].

# Software design

The package uses a small verification-first architecture. `finite` checks one supplied Lagrangian certificate in a single pass over the finite universe. `robust` separates two questions that are easy to confuse: whether a passing certificate survives worst-case perturbation and whether a failing certificate is merely inconclusive under declared measurement error. `pac` reports a distributional zero-violation audit rather than an exhaustive result. `ratios` compares fractional metrics by exact cross-products when possible. `artefact` serialises the resulting verdict into canonical JSON and stores a SHA-256 digest over the body without the integrity block.

This design trades search breadth for audit transparency. Each public function returns a typed result or typed refusal, and the command-line verifier exits with status 0 or 1 so that artefact integrity can be checked in continuous-integration pipelines. The exact backend uses Python's `fractions.Fraction`; the floating backend is faster but emits only within-tolerance verdicts. One finite certificate check costs \(\Theta(|K|(p+m))\), where \(p\) is the number of objectives and \(m\) is the number of active constraints.

# Research impact statement

The package supports a reproducibility task that appears in optimisation papers, engineering design reports and decision-system audits: the need to distinguish a generated candidate from a certified candidate. Its immediate use is in supplementary material, review workflows and teaching examples where supported and unsupported Pareto-efficient points must not be conflated. The release includes deterministic demonstrations, an exact-versus-tolerance example, a scaling benchmark to \(|K|=10^6\), a command-line verification path and a JSON schema for certificate artefacts. The intended research impact is therefore not a new optimisation algorithm but a reusable audit layer that makes a precise class of finite Pareto claims easier to inspect, reproduce and reject when the claim is too strong.

# AI usage disclosure

Generative AI tools were used during early drafting, refactoring discussion and checklist preparation for this repository and paper. All code, tests, mathematical claims, examples, metadata and wording in the release were reviewed, executed and edited by the author, who takes responsibility for the final software and manuscript. No AI-generated output was accepted without human inspection and test execution.

# Acknowledgements

The author thanks students at the Bucharest University of Economic Studies whose project reports motivated the need for explicit verdict names.

# References
