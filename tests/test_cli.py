"""CLI: verify exits 0/1 correctly; demo and module entry point run."""

import json
import os
import subprocess
import sys
from pathlib import Path

from cert_pareto.cli import main
from cert_pareto import (
    FiniteProblem,
    check_lagrangian_certificate,
    make_certificate_artifact,
    write_artifact,
)


def _write(tmp: Path) -> Path:
    K = ("A", "B", "C")
    F = {"A": (0.0, 2.0), "B": (1.0, 1.0), "C": (2.0, 0.0)}
    problem = FiniteProblem(K, (lambda x: F[x][0], lambda x: F[x][1]))
    result = check_lagrangian_certificate(problem, "B", (0.5, 0.5))
    art = make_certificate_artifact(result.as_dict(), problem_id="cli-test")
    return write_artifact(art, tmp / "cli_artifact.json")


def test_verify_ok_and_tampered(tmp_path):
    path = _write(tmp_path)
    assert main(["verify", str(path)]) == 0
    data = json.loads(path.read_text())
    data["problem_id"] = "tampered"
    path.write_text(json.dumps(data))
    assert main(["verify", str(path)]) == 1


def test_verify_missing_file():
    assert main(["verify", "no/such/file.json"]) == 1


def test_demo_runs():
    assert main(["demo"]) == 0


def test_module_entrypoint_demo_runs():
    env = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[1] / "src"))
    completed = subprocess.run(
        [sys.executable, "-m", "cert_pareto", "demo"],
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )
    assert completed.returncode == 0
    assert "Ground truth for C" in completed.stdout


def test_module_entrypoint_version_runs():
    env = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[1] / "src"))
    completed = subprocess.run(
        [sys.executable, "-m", "cert_pareto", "--version"],
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )
    assert completed.returncode == 0
    assert "cert-pareto" in completed.stdout


def test_module_entrypoint_via_runpy(monkeypatch):
    import runpy

    monkeypatch.setattr(sys, "argv", ["cert_pareto", "--version"])
    with __import__("pytest").raises(SystemExit) as excinfo:
        runpy.run_module("cert_pareto.__main__", run_name="__main__")
    assert excinfo.value.code == 0
