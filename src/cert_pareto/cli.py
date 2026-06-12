"""Command line interface: artefact verification and a built-in demo.

``cert-pareto verify <artefact.json>`` exits 0 on a valid hash and 1
otherwise, so the check composes with shell pipelines and CI. ``cert-pareto
demo`` runs the supported/unsupported toy pair on both arithmetic backends.
"""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .artefact import read_artifact, verify_artifact_hash
from .finite import FiniteProblem, check_lagrangian_certificate, pareto_status


def _cmd_verify(path: str) -> int:
    try:
        artifact = read_artifact(path)
    except (OSError, ValueError) as exc:
        print(f"error: cannot read artefact: {exc}", file=sys.stderr)
        return 1
    if verify_artifact_hash(artifact):
        verdict = artifact.get("certificate_result", {}).get("verdict", "<missing>")
        print(f"integrity OK  (recorded verdict: {verdict})")
        print("note: a valid hash certifies the record, not the mathematics; "
              "re-run the checker on the recorded inputs to re-establish validity.")
        return 0
    print("integrity FAILED: the artefact does not match its stored digest.", file=sys.stderr)
    return 1


def _cmd_demo() -> int:
    K = ("A", "B", "C")
    F = {"A": (0, 1), "B": (1, 0), "C": ("3/5", "3/5")}  # 3/5 = 0.6, exact as a rational
    problem = FiniteProblem(K, (lambda x: F[x][0], lambda x: F[x][1]))
    print("Ground truth for C by enumeration:", pareto_status(problem, "C", arithmetic="exact"))
    for lam in (("1/2", "1/2"), ("1/5", "4/5"), ("4/5", "1/5")):
        r = check_lagrangian_certificate(problem, "C", lam, arithmetic="exact")
        print(f"  weights {lam}: {r.verdict}")
    print("Supported point B on the segment A-C of a second toy:")
    F2 = {"A": (0, 2), "B": (1, 1), "C": (2, 0)}
    p2 = FiniteProblem(K, (lambda x: F2[x][0], lambda x: F2[x][1]))
    r = check_lagrangian_certificate(p2, "B", ("1/2", "1/2"), arithmetic="exact")
    print(f"  weights ('1/2', '1/2'): {r.verdict}  margin={r.margin}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="cert-pareto",
                                     description="A posteriori Pareto certificate checking.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)
    p_verify = sub.add_parser("verify", help="verify the integrity hash of a certificate artefact")
    p_verify.add_argument("artifact", help="path to a certificate artefact JSON file")
    sub.add_parser("demo", help="run the supported/unsupported toy demonstration")
    args = parser.parse_args(argv)
    if args.command == "verify":
        return _cmd_verify(args.artifact)
    return _cmd_demo()


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
