# cert-pareto API reference

This page is the reviewer-facing public API reference for `cert-pareto`. The package is intentionally small; every public symbol listed here is exported from `cert_pareto.__init__` and is covered by the test suite.

## Finite certificate checking

### `FiniteProblem(alternatives, objectives, constraints=())`

Finite decision universe and objective/constraint container.

- `alternatives`: finite iterable of hashable alternatives.
- `objectives`: tuple of callables returning numbers to be minimised.
- `constraints`: tuple of callables for inequalities `g_j(x) <= 0`.

```python
from cert_pareto import FiniteProblem

K = ("A", "B", "C")
F = {"A": (0, 2), "B": (1, 1), "C": (2, 0)}
problem = FiniteProblem(K, (lambda x: F[x][0], lambda x: F[x][1]))
```

### `check_lagrangian_certificate(problem, candidate, lambdas, *, multipliers=None, active_constraints=None, arithmetic="float", tol=1e-9, violator_cap=20)`

Checks one supplied finite Lagrangian certificate. It does not search for weights and it does not generate a Pareto frontier.

```python
from cert_pareto import check_lagrangian_certificate

result = check_lagrangian_certificate(
    problem,
    "B",
    ("1/2", "1/2"),
    arithmetic="exact",
)
print(result.verdict)       # certifiedExactParetoEfficient
print(result.margin)        # 0
print(result.as_dict())     # JSON-ready dictionary
```

Use `arithmetic="exact"` for rational arithmetic through `fractions.Fraction`. Use `arithmetic="float"` only when a within-tolerance verdict is scientifically acceptable.

### `pareto_status(problem, candidate, *, tol=1e-9, arithmetic="float")`

Exhaustive diagnostic oracle for small examples. It is not a certificate checker.

```python
print(pareto_status(problem, "B", arithmetic="exact"))
```

### `dominates(fx, fy, *, strict=False, tol=0.0)`

Componentwise dominance predicate under minimisation. With `strict=False`, it checks Pareto domination: no worse in every objective and better in at least one.

## Robustness diagnostics

### `error_budget(lambdas, rho, multipliers=(), rho_prime=())`

Computes the declared worst-case error budget

```text
B = sum(lambda_i * rho_i) + sum(mu_j * rho_prime_j).
```

### `check_robust_certificate(min_gap, lambdas, rho, multipliers=(), rho_prime=())`

Certifies robustness of a passing certificate when `min_gap >= 2B`. The factor two accounts for perturbation at the candidate and at the rival alternative.

### `check_defect_coverage(kappa, lambdas, rho, multipliers=(), rho_prime=())`

Triage for a failing certificate. If the defect is covered by the declared error budget, the result is `inconclusiveWithinDeclaredErrors`, not `certifiedRobust`.

## PAC zero-violation audit

### `pac_sample_size(epsilon, delta)`

Returns the conservative sample size `ceil(log(1/delta)/epsilon)`.

### `zero_violation_upper_bound(M, delta)`

Returns `log(1/delta)/M`, the certified upper bound after `M` clean independent draws.

### `pac_zero_violation_audit(violations, epsilon, delta)`

Consumes a sequence of boolean violation indicators. It refuses under-sized samples and any observed violation; only a sufficient clean sample yields `pacAuditedNoViolation`.

```python
from cert_pareto import pac_zero_violation_audit

result = pac_zero_violation_audit([False] * 300, epsilon=0.01, delta=0.05)
print(result.verdict)  # pacAuditedNoViolation
```

## Ratio comparison

### `ratio_gap(N_x, D_x, N_0, D_0)`

Returns the cross-product gap

```text
N(x)D(x0) - N(x0)D(x).
```

Positive denominators are required. For integer and `Fraction` inputs the comparison is exact.

### `compare_ratio(N_x, D_x, N_0, D_0, *, tol=0.0)`

Returns `lower`, `equal` or `higher` for the ratio at `x` compared with the ratio at `x0`.

## Artefacts and CLI

### `make_certificate_artifact(result, *, problem_id, software_version="0.2.2")`

Wraps a result dictionary into a canonical JSON-compatible artefact with package version, schema URI and SHA-256 digest.

### `write_artifact(artifact, path)`, `read_artifact(path)` and `verify_artifact_hash(artifact)`

Write, read and verify the artefact integrity hash. A valid hash establishes record integrity only; it does not re-establish the mathematical certificate.

```bash
cert-pareto verify certificate_artifact.json
python -m cert_pareto demo
```

## Verdicts

All checkers return a member of `cert_pareto.Verdict`:

- `certifiedExactWeaklyPareto`
- `certifiedExactParetoEfficient`
- `certifiedWeaklyParetoWithinTolerance`
- `certifiedParetoEfficientWithinTolerance`
- `certifiedRobust`
- `inconclusiveWithinDeclaredErrors`
- `pacAuditedNoViolation`
- `notCertifiedByThisCertificate`
- `infeasibleCandidate`
- `invalidInput`

Only the first five and `pacAuditedNoViolation` are positive certification or audit verdicts. `notCertifiedByThisCertificate` is a refusal about the certificate, not a judgement that the candidate is dominated.
