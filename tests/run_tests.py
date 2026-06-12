"""Zero-dependency test runner.

Executes every no-argument ``test_*`` function in every ``test_*.py`` module
in this directory. CI uses pytest with coverage; this runner exists so the
core suite remains inspectable from a clean interpreter with no third-party
installs. Tests that require pytest fixtures are reported as skipped because
this runner deliberately does not emulate pytest.
"""

from __future__ import annotations

import importlib
import inspect
import pathlib
import sys
import traceback

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "src"))


def main() -> int:
    failures = 0
    total = 0
    skipped = 0
    for module_path in sorted(HERE.glob("test_*.py")):
        module = importlib.import_module(module_path.stem)
        for name in sorted(dir(module)):
            if not name.startswith("test_"):
                continue
            fn = getattr(module, name)
            if inspect.signature(fn).parameters:
                skipped += 1
                print(f"SKIP {module_path.stem}.{name} (pytest fixture required)")
                continue
            total += 1
            try:
                fn()
                print(f"PASS {module_path.stem}.{name}")
            except Exception:
                failures += 1
                print(f"FAIL {module_path.stem}.{name}")
                traceback.print_exc()
    print(f"\n{total - failures}/{total} no-fixture tests passed; {skipped} pytest-fixture tests skipped")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
