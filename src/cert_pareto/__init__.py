"""cert-pareto: a posteriori Pareto certificate checking for finite decision spaces.

The package verifies supplied certificates and exports portable, hash-pinned
artefacts. It does not generate Pareto frontiers and it does not search for
certificates; both omissions are design decisions, documented in the README.
"""

from .verdicts import Verdict, POSITIVE_VERDICTS
from .finite import (
    FiniteProblem,
    CertificateResult,
    check_lagrangian_certificate,
    dominates,
    pareto_status,
    VIOLATOR_CAP,
)
from .robust import RobustResult, error_budget, check_robust_certificate, check_defect_coverage
from .pac import PACAuditResult, pac_sample_size, zero_violation_upper_bound, pac_zero_violation_audit
from .ratios import ratio_gap, compare_ratio
from .artefact import (
    SCHEMA_URI,
    make_certificate_artifact,
    write_artifact,
    read_artifact,
    verify_artifact_hash,
    sha256_json,
)

__version__ = "0.2.1"

__all__ = [
    "Verdict",
    "POSITIVE_VERDICTS",
    "FiniteProblem",
    "CertificateResult",
    "check_lagrangian_certificate",
    "dominates",
    "pareto_status",
    "VIOLATOR_CAP",
    "RobustResult",
    "error_budget",
    "check_robust_certificate",
    "check_defect_coverage",
    "PACAuditResult",
    "pac_sample_size",
    "zero_violation_upper_bound",
    "pac_zero_violation_audit",
    "ratio_gap",
    "compare_ratio",
    "SCHEMA_URI",
    "make_certificate_artifact",
    "write_artifact",
    "read_artifact",
    "verify_artifact_hash",
    "sha256_json",
    "__version__",
]
