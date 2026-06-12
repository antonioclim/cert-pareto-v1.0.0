"""Portable certificate artefacts: canonical JSON, hashed, schema-pinned.

Integrity versus validity
-------------------------
The SHA-256 digest binds the artefact to its bytes under a fixed canonical
serialisation (sorted keys, minimal separators, UTF-8, non-ASCII allowed).
A verified hash means the record is unaltered since emission. It does not
re-establish the mathematics: validity requires re-running the checker on
the recorded inputs. The two notions are kept apart on purpose; an artefact
that conflates them is theatre.

The canonicalisation here is self-consistent and sufficient for
self-verification. Interoperable signing across independent
implementations would call for RFC 8785 (JSON Canonicalization Scheme);
that is future work, noted rather than imitated.
"""

from __future__ import annotations

import json
import hashlib
from pathlib import Path
from typing import Any, Dict, Mapping

#: Versioned, resolvable schema identifier. The file ships in the
#: repository at schema/certificate-v1.schema.json; the URI below resolves
#: once the repository is public (see RELEASING.md for the release-time
#: check).
SCHEMA_URI = (
    "https://antonioclim.github.io/cert-pareto/schema/certificate-v1.schema.json"
    "schema/certificate-v1.schema.json"
)

SOFTWARE_NAME = "cert-pareto"
SOFTWARE_VERSION = "0.2.1"


def _canonical_json(data: Mapping[str, Any]) -> bytes:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_json(data: Mapping[str, Any]) -> str:
    """SHA-256 hex digest of the canonical serialisation of ``data``."""
    return hashlib.sha256(_canonical_json(data)).hexdigest()


def make_certificate_artifact(
    result: Mapping[str, Any],
    *,
    problem_id: str,
    software_version: str = SOFTWARE_VERSION,
) -> Dict[str, Any]:
    """Wrap a checker result dictionary into a hash-pinned artefact.

    ``result`` is typically ``CertificateResult.as_dict()`` or the dict
    form of a robust or PAC result. The digest is computed over the body
    without the ``integrity`` block, then attached inside it.
    """
    body: Dict[str, Any] = {
        "schema": SCHEMA_URI,
        "software": {"name": SOFTWARE_NAME, "version": software_version},
        "problem_id": str(problem_id),
        "certificate_result": dict(result),
    }
    body["integrity"] = {"sha256_without_integrity": sha256_json(body)}
    return body


def write_artifact(artifact: Mapping[str, Any], path: str | Path) -> Path:
    """Write the artefact as indented, sorted, UTF-8 JSON; returns the path."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    return path


def read_artifact(path: str | Path) -> Dict[str, Any]:
    """Load an artefact from disk."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def verify_artifact_hash(artifact: Mapping[str, Any]) -> bool:
    """True iff the stored digest matches the canonical body.

    Integrity only: a True result certifies nothing mathematical.
    """
    body = dict(artifact)
    integrity = body.pop("integrity", None)
    if not isinstance(integrity, Mapping) or "sha256_without_integrity" not in integrity:
        return False
    return sha256_json(body) == integrity["sha256_without_integrity"]
