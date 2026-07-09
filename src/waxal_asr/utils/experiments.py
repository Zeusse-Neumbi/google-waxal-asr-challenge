"""Experiment directory management.

Allocates the next monotonic experiment number and scaffolds the standard layout.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import NamedTuple

from waxal_asr.utils.io import ensure_dir

__all__ = ["Experiment", "create_experiment", "next_experiment_number"]

_DEFAULT_EXPERIMENTS_DIR = Path("experiments")

_LAYOUT = {
    "config.yaml": "# Exact config used for this run.\n",
    "metrics.json": "{}\n",
    "notes.md": (
        "# Experiment {number}: {name}\n\n"
        "## Hypothesis\n\n## Config diff vs baseline\n\n"
        "## Results\n- WER:\n- CER:\n- Combined:\n\n"
        "## Observations\n\n## Decision\n"
    ),
    "predictions.csv": "id,reference,hypothesis,language,duration\n",
    "checkpoint.md": "# Checkpoint\n\n- path:\n- git_sha:\n- seed:\n",
}


class Experiment(NamedTuple):
    number: int
    name: str
    path: Path


def next_experiment_number(experiments_dir: Path = _DEFAULT_EXPERIMENTS_DIR) -> int:
    """Return the next experiment number (zero-padded 3 digits)."""
    experiments_dir = Path(experiments_dir)
    if not experiments_dir.exists():
        return 1
    numbers = []
    for entry in experiments_dir.iterdir():
        if entry.is_dir():
            prefix = entry.name.split("_", 1)[0]
            if prefix.isdigit():
                numbers.append(int(prefix))
    return (max(numbers) + 1) if numbers else 1


def create_experiment(
    name: str,
    experiments_dir: Path | str = _DEFAULT_EXPERIMENTS_DIR,
    number: int | None = None,
) -> Experiment:
    """Create a new experiment directory with the standard layout.

    Never overwrites an existing experiment directory.
    """
    experiments_dir = Path(experiments_dir)
    ensure_dir(experiments_dir)
    if number is None:
        number = next_experiment_number(experiments_dir)
    dir_name = f"{number:03d}_{name}"
    exp_path = experiments_dir / dir_name
    if exp_path.exists():
        raise FileExistsError(f"Experiment directory already exists: {exp_path}")
    ensure_dir(exp_path)
    ensure_dir(exp_path / "logs")
    ensure_dir(exp_path / "plots")
    for rel, stub in _LAYOUT.items():
        target = exp_path / rel
        target.write_text(stub.format(number=number, name=name) if "{number}" in stub else stub)
    return Experiment(number=number, name=name, path=exp_path)


def _utc_now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"
