"""Unified ASR model protocol.

Every supported architecture (Whisper, MMS, wav2vec2, SeamlessM4T, Canary, Gemma)
implements this protocol so that training/inference/evaluation code is model-agnostic.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

import torch

__all__ = ["ASRModel"]


@runtime_checkable
class ASRModel(Protocol):
    """Protocol every ASR model must satisfy.

    Supports both encoder-decoder (Whisper) and decoder-only multimodal (Gemma) models.
    For decoder-only models the `processor` carries the tokenizer and chat template.
    """

    name: str
    sample_rate: int

    @property
    def model(self) -> torch.nn.Module:
        """Return the underlying PyTorch module."""
        ...

    @property
    def processor(self) -> Any | None:
        """Return the model processor (tokenizer + feature extractor), or None."""
        ...

    def load(self, checkpoint: str | None = None) -> None: ...

    def transcribe(self, audio: torch.Tensor, sample_rate: int, **kwargs: Any) -> str: ...

    def save(self, path: str) -> None: ...
