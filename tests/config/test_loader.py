"""Tests for the config loader."""

from pathlib import Path

import pytest

from waxal_asr.config import Config, load_config


def test_baseline_loads(tmp_path: Path) -> None:
    # Use the real shipped baseline config.
    repo_root = Path(__file__).resolve().parents[2]
    cfg_path = repo_root / "configs" / "baseline.yaml"
    cfg = load_config(cfg_path)
    assert isinstance(cfg, Config)
    assert cfg.project.name == "waxal-asr"
    assert cfg.audio.sample_rate == 16000
    assert cfg.repro.seed == 42


def test_inheritance(tmp_path: Path) -> None:
    # Write a parent + child config and verify inheritance + override.
    (tmp_path / "parent.yaml").write_text("audio:\n  sample_rate: 8000\nrepro:\n  seed: 1\n")
    (tmp_path / "child.yaml").write_text("defaults: [parent]\naudio:\n  sample_rate: 16000\n")
    cfg = load_config(tmp_path / "child.yaml")
    assert cfg.audio.sample_rate == 16000  # overridden
    assert cfg.repro.seed == 1  # inherited


def test_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_config(tmp_path / "nope.yaml")
