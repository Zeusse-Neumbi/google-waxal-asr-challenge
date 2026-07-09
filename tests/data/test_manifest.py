"""Tests for the Manifest helper (no real audio files required)."""

from pathlib import Path

import pandas as pd
import pytest

from waxal_asr.data.manifest import Manifest


def _write_manifest(path: Path) -> None:
    df = pd.DataFrame(
        {
            "audio_path": ["a.wav", "b.wav", "c.wav"],
            "transcript": ["hi", "hello", "hey"],
            "language": ["x", "x", "y"],
            "split": ["train", "train", "test"],
            "duration": [1.0, 2.0, 3.0],
        }
    )
    df.to_csv(path, index=False)


def test_manifest_loads_and_filters(tmp_path: Path) -> None:
    p = tmp_path / "manifest.csv"
    _write_manifest(p)
    m = Manifest.from_csv(p)
    assert len(m) == 3
    train = m.filter(split="train")
    assert len(train) == 2
    test_y = m.filter(split="test", language="y")
    assert len(test_y) == 1


def test_manifest_missing_columns_raises(tmp_path: Path) -> None:
    bad = tmp_path / "bad.csv"
    pd.DataFrame({"audio_path": ["a.wav"], "transcript": ["hi"]}).to_csv(bad, index=False)
    with pytest.raises(ValueError):
        Manifest.from_csv(bad)
