"""Tests for experiment directory allocation."""

from pathlib import Path

import pytest

from waxal_asr.utils.experiments import create_experiment, next_experiment_number


def test_next_number_on_empty_dir(tmp_path: Path) -> None:
    assert next_experiment_number(tmp_path) == 1


def test_create_experiment_scaffolds_layout(tmp_path: Path) -> None:
    exp = create_experiment("baseline", experiments_dir=tmp_path)
    assert exp.number == 1
    assert exp.path.name == "001_baseline"
    assert (exp.path / "config.yaml").exists()
    assert (exp.path / "metrics.json").exists()
    assert (exp.path / "predictions.csv").exists()
    assert (exp.path / "logs").is_dir()
    assert (exp.path / "plots").is_dir()


def test_numbers_increment(tmp_path: Path) -> None:
    e1 = create_experiment("a", experiments_dir=tmp_path)
    e2 = create_experiment("b", experiments_dir=tmp_path)
    assert (e1.number, e2.number) == (1, 2)


def test_no_overwrite(tmp_path: Path) -> None:
    create_experiment("x", experiments_dir=tmp_path, number=5)
    with pytest.raises(FileExistsError):
        create_experiment("x", experiments_dir=tmp_path, number=5)
