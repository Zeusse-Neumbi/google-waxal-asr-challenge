"""Structured logging via `loguru`.

Configure once at the start of any entry point with `configure_logging()`, then use
`get_logger(__name__)` in modules. Never use `print()` in `src/`.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from loguru import logger as _logger

__all__ = ["configure_logging", "get_logger"]

_CONFIGURED = False


def configure_logging(
    level: str = "INFO",
    log_file: str | Path | None = None,
    rotation: str = "10 MB",
    retention: str = "14 days",
) -> None:
    """Configure the global loguru logger. Safe to call multiple times."""
    global _CONFIGURED
    _logger.remove()
    _logger.add(
        sys.stderr,
        level=level,
        colorize=True,
        backtrace=False,
        diagnose=False,
        enqueue=True,
    )
    if log_file is not None:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        _logger.add(
            str(log_file),
            level=level,
            rotation=rotation,
            retention=retention,
            encoding="utf-8",
            enqueue=True,
        )
    _CONFIGURED = True


def get_logger(name: str | None = None) -> Any:
    """Return a bound logger. Configure first; falls back to stderr-only."""
    if not _CONFIGURED:
        configure_logging()
    return _logger.bind(module=name) if name else _logger
