"""Artefact integrity: round trip, tamper detection, schema field."""

import json
from pathlib import Path

from cert_pareto import (
    SCHEMA_URI,
    FiniteProblem,
    check_lagrangian_certificate,
    make_certificate_artifact,
    write_artifact,
    read_artifact,
    verify_artifact_hash,
)


def _artifact():
    K = ("A", "B", "C")
    F = {"A": (0.0, 2.0), "B": (1.0, 1.0), "C": (2.0, 0.0)}
    problem = FiniteProblem(K, (lambda x: F[x][0], lambda x: F[x][1]))
    result = check_lagrangian_certificate(problem, "B", ("1/2", "1/2"), arithmetic="exact")
    return make_certificate_artifact(result.as_dict(), problem_id="toy-supported-line")


def test_round_trip_verifies(tmp_path=None):
    art = _artifact()
    assert art["schema"] == SCHEMA_URI
    assert verify_artifact_hash(art)
    target = Path(tmp_path) / "a.json" if tmp_path else Path("results/_test_artifact.json")
    write_artifact(art, target)
    loaded = read_artifact(target)
    assert verify_artifact_hash(loaded)
    assert loaded["certificate_result"]["verdict"] == "certifiedExactParetoEfficient"
    if not tmp_path:
        target.unlink()


def test_tampering_detected():
    art = _artifact()
    tampered = json.loads(json.dumps(art))
    tampered["certificate_result"]["verdict"] = "certifiedExactWeaklyPareto"
    assert not verify_artifact_hash(tampered)


def test_missing_or_malformed_integrity_rejected():
    art = _artifact()
    no_block = {k: v for k, v in art.items() if k != "integrity"}
    assert not verify_artifact_hash(no_block)
    bad_block = dict(art, integrity={"sha256": "deadbeef"})
    assert not verify_artifact_hash(bad_block)


def test_artifact_conforms_to_shipped_schema_enum():
    schema = json.loads(Path(__file__).resolve().parents[1].joinpath(
        "schema", "certificate-v1.schema.json").read_text())
    allowed = set(schema["properties"]["certificate_result"]["properties"]["verdict"]["enum"])
    from cert_pareto import Verdict
    assert {v.value for v in Verdict} == allowed
