"""End-to-end artefact: check, wrap, hash, write, verify, tamper-detect."""

import sys
import pathlib
# Runnable from a clean checkout; harmless once the package is installed.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

import json
from pathlib import Path

from cert_pareto import (
    FiniteProblem,
    check_lagrangian_certificate,
    make_certificate_artifact,
    write_artifact,
    read_artifact,
    verify_artifact_hash,
)

K = ("A", "B", "C")
F = {"A": (0, 2), "B": (1, 1), "C": (2, 0)}
problem = FiniteProblem(K, (lambda x: F[x][0], lambda x: F[x][1]))
result = check_lagrangian_certificate(problem, "B", ("1/2", "1/2"), arithmetic="exact")

artifact = make_certificate_artifact(result.as_dict(), problem_id="toy-supported-line")
path = write_artifact(artifact, Path("results") / "certificate_artifact.json")
print("written:", path)
print("verify :", verify_artifact_hash(read_artifact(path)))

tampered = json.loads(path.read_text())
tampered["certificate_result"]["verdict"] = "certifiedExactWeaklyPareto"
print("tampered verify:", verify_artifact_hash(tampered))
