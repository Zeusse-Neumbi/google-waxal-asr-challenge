"""Filesystem and path helpers."""

from __future__ import annotations

from pathlib import Path

__all__ = ["ensure_dir", "resolve_path"]


def ensure_dir(path: str | Path) -> Path:
    """Create a directory (and parents) if it does not exist; return as Path."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def resolve_path(path: str | Path, base: str | Path | None = None) -> Path:
    """Resolve `path` against `base` if relative, otherwise return as-is."""
    p = Path(path)
    if p.is_absolute() or base is None:
        return p
    return Path(base) / p
