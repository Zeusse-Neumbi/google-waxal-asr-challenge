"""Unified ASR model protocol.

Every supported architecture (Whisper, MMS, wav2vec2, SeamlessM4T, Canary) implements
this protocol so that training/inference/evaluation code is model-agnostic.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

import torch

__all__ = ["ASRModel"]


@runtime_checkable
class ASRModel(Protocol):
    """Protocol every ASR model must satisfy."""

    name: str
    sample_rate: int

    def load(self, checkpoint: str | None = None) -> None: ...

    def transcribe(self, audio: torch.Tensor, sample_rate: int) -> str: ...

    def save(self, path: str) -> None: ...
