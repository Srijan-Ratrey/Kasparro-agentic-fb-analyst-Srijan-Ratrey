"""Pytest conftest for test environment setup.

This file ensures tests can import the `src` package by adding the
project root to sys.path. It also provides a lightweight fallback for
running async tests in environments that do not have `pytest-asyncio`
installed: we create a `pytest.mark.asyncio` decorator that runs the
coroutine with `asyncio.run` so tests marked with `@pytest.mark.asyncio`
still execute.
"""
import sys
from pathlib import Path
import asyncio
import functools
import pytest

ROOT = Path(__file__).resolve().parents[1]

# Add project root to sys.path so imports like `import src.core.config` work
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Provide a fallback `pytest.mark.asyncio` decorator when pytest-asyncio
# is not installed. This wraps async test functions and runs them with
# `asyncio.run`, allowing tests to run in constrained environments.
def _make_asyncio_marker():
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return asyncio.run(func(*args, **kwargs))
            return wrapper
        return func
    return decorator

# Only set the fallback if the marker is not already provided by a plugin
if not hasattr(pytest.mark, "asyncio"):
    pytest.mark.asyncio = _make_asyncio_marker()
