"""Batched inference engine."""

from __future__ import annotations

__all__ = ["Inferencer"]


class Inferencer:
    """Placeholder inference engine."""

    def __init__(self, model: object, config: object) -> None:
        self.model = model
        self.config = config

    def transcribe_batch(self, audio_paths: list[str]) -> list[str]:  # pragma: no cover
        raise NotImplementedError("Inferencer will be implemented in the inference phase.")
