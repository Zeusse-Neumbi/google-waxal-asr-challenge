"""Manifest utilities.

A manifest is a CSV mapping `audio_path -> transcript -> language -> split -> duration`.
It is the single source of truth for dataset access. Loaders never hardcode paths.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

__all__ = ["Manifest", "ManifestEntry"]

REQUIRED_COLUMNS = ["audio_path", "transcript", "language", "split", "duration"]


@dataclass(frozen=True)
class ManifestEntry:
    audio_path: Path
    transcript: str
    language: str
    split: str
    duration: float


class Manifest:
    """In-memory manifest backed by a CSV file."""

    def __init__(self, df: pd.DataFrame) -> None:
        missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
        if missing:
            raise ValueError(f"Manifest missing required columns: {missing}")
        self._df = df.reset_index(drop=True)

    @classmethod
    def from_csv(cls, path: str | Path) -> Manifest:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Manifest not found: {path}")
        return cls(pd.read_csv(path))

    def __len__(self) -> int:
        return len(self._df)

    def __iter__(self) -> Iterator[ManifestEntry]:
        for _, row in self._df.iterrows():
            yield ManifestEntry(
                audio_path=Path(row["audio_path"]),
                transcript=str(row["transcript"]),
                language=str(row["language"]),
                split=str(row["split"]),
                duration=float(row["duration"]),
            )

    def filter(self, split: str | None = None, language: str | None = None) -> Manifest:
        df = self._df
        if split is not None:
            df = df[df["split"] == split]
        if language is not None:
            df = df[df["language"] == language]
        return Manifest(df)

    def to_csv(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self._df.to_csv(path, index=False)
