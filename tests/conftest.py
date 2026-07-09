"""Pytest configuration and shared fixtures."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

# Ensure `src/` layout package is importable without an editable install in dev.
_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

# Determinism for any code that ignores explicit seeding in tests.
os.environ.setdefault("PYTHONHASHSEED", "0")


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    return Path(__file__).parent / "fixtures"
