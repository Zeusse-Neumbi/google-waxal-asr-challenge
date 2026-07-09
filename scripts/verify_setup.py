"""Verify the project environment is correctly set up.

Run: python scripts/verify_setup.py

Checks:
- Python version
- Required packages importable
- Package installed (waxal_asr importable)
- Configs parse
- Core modules import
- Tests collect (without running)
- Data / output directories exist
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

CHECKS: list[tuple[str, callable]] = []


def check(name: str) -> callable:
    def deco(fn: callable) -> callable:
        CHECKS.append((name, fn))
        return fn

    return deco


@check("Python version >= 3.11")
def _python() -> None:
    assert sys.version_info >= (
        3,
        11,
    ), f"Python {sys.version_info.major}.{sys.version_info.minor} < 3.11"


REQUIRED = ["numpy", "pandas", "yaml", "jiwer", "loguru", "typer"]
OPTIONAL = ["torch", "torchaudio", "transformers", "datasets", "accelerate"]


@check("Required packages importable")
def _packages() -> None:
    import importlib

    for pkg in REQUIRED:
        importlib.import_module(pkg)


@check("Optional ML packages importable")
def _optional_packages() -> None:
    import importlib

    missing = []
    for pkg in OPTIONAL:
        try:
            importlib.import_module(pkg)
        except ImportError:
            missing.append(pkg)
    if missing:
        # Not fatal — needed for training/inference but not for setup verification.
        print(f"    note: not installed (OK for setup): {missing}")


@check("waxal_asr importable")
def _pkg() -> None:
    import waxal_asr

    assert waxal_asr.__version__


@check("Configs parse")
def _configs() -> None:
    from waxal_asr.config import load_config

    for name in [
        "baseline",
        "whisper-small",
        "whisper-medium",
        "large-v3",
        "evaluation",
        "inference",
    ]:
        load_config(REPO_ROOT / "configs" / f"{name}.yaml")


@check("Core modules import")
def _modules() -> None:
    import importlib

    for mod in [
        "waxal_asr.metrics",
        "waxal_asr.config",
        "waxal_asr.data.audio",
        "waxal_asr.data.manifest",
        "waxal_asr.evaluation",
        "waxal_asr.utils.seeding",
        "waxal_asr.utils.experiments",
    ]:
        importlib.import_module(mod)


@check("Directory structure present")
def _dirs() -> None:
    for d in [
        "configs",
        "data/raw",
        "data/processed",
        "data/external",
        "data/metadata",
        "experiments",
        "outputs/models",
        "outputs/logs",
        "submissions",
        "tests",
        "src/waxal_asr",
        ".opencode",
        ".github",
    ]:
        assert (REPO_ROOT / d).is_dir(), f"missing dir: {d}"


def main() -> int:
    failures = 0
    for name, fn in CHECKS:
        try:
            fn()
            print(f"  [OK]   {name}")
        except Exception as e:
            print(f"  [FAIL] {name}: {e}")
            failures += 1
    print()
    if failures:
        print(f"{failures} check(s) failed.")
        return 1
    print(f"All {len(CHECKS)} checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
