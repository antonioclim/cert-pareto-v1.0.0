# Reviewer-response pack

This document prepares answers to the questions a JOSS reviewer is most likely to ask. It should not be submitted as the paper; it is evidence for the author during the public review.

## Why is this not a contribution to pymoo or another optimiser?

`cert-pareto` occupies a different workflow position. Optimisers generate candidates or approximate fronts. This package verifies one externally supplied certificate claim against a declared finite universe and returns a typed verdict plus an artefact. It is therefore a post hoc audit layer, not an optimisation algorithm or a decision-support interface.

## Why is the mathematics not the claimed novelty?

The supported-point certificate rests on classical weighted-sum sufficiency. The package claims software novelty: exact-versus-tolerance verdict separation, refusal semantics for unsupported efficient points, robust-error triage, PAC-audit guard rails and a hash-pinned certificate record.

## Why does the package not consume proof logs?

Proof-log systems such as VeriPB/CakePB address solver-integrated proof production. `cert-pareto` addresses the audit setting in which an external report supplies a candidate and a finite certificate but no solver proof trail. It does not claim equivalence to formally verified proof checkers.

## Why are the examples synthetic?

A checker should be testable on instances that are small enough to inspect by hand. The examples exercise the failure modes most likely to generate false claims: supported points, unsupported efficient points, exact-versus-floating disagreement, robust margin failure and zero-violation PAC audit. Real case studies belong in downstream method papers.

## What does the artefact hash prove?

It proves only record integrity under the package's canonical JSON serialisation. It does not prove mathematical validity, authenticity of the issuer or correctness of the data. Validity requires re-running the checker on the recorded inputs.

## Why is `inconclusiveWithinDeclaredErrors` not a positive verdict?

A failed certificate whose defect lies within the declared error budget is not established; it is also not refuted by those measurements. Calling this `certifiedRobust` would over-claim. The separate verdict protects the user from that semantic error.
