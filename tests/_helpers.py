"""Shared test helpers usable both under pytest and the standalone runner."""

from __future__ import annotations

from contextlib import contextmanager


@contextmanager
def assert_raises(exc_type):
    """Minimal stand-in for pytest.raises, runnable without pytest."""
    try:
        yield
    except exc_type:
        return
    except Exception as other:  # pragma: no cover - diagnostic path
        raise AssertionError(f"expected {exc_type.__name__}, got {type(other).__name__}: {other}")
    raise AssertionError(f"expected {exc_type.__name__}, nothing was raised")
