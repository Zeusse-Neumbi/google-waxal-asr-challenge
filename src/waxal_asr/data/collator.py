"""Data collators for model-specific batched processing.

Each collator converts a list of raw examples into a model-ready batch
with input_ids, attention_mask, and labels tensors.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np
import torch

__all__ = ["ChatCollator", "WhisperCollator", "get_collator"]


def _mask_labels(
    labels: torch.Tensor,
    tokenizer: Any,
) -> torch.Tensor:
    """Sets padding and special-token positions to -100 (ignored by CE loss)."""
    labels = labels.clone()
    special_attrs = [
        "pad_token_id",
        "image_token_id",
        "audio_token_id",
        "boi_token_id",
        "eoi_token_id",
    ]
    mask_ids = [
        getattr(tokenizer, attr)
        for attr in special_attrs
        if getattr(tokenizer, attr, None) is not None
    ]
    if mask_ids:
        labels[torch.isin(labels, torch.tensor(mask_ids, device=labels.device))] = -100
    return labels


class ChatCollator:
    """Collator for chat-formatted models (Gemma 3n etc.).

    Applies the processor's chat template, tokenises audio and text,
    and masks padding / special tokens in labels.
    """

    def __init__(self, processor: Any, max_length: int = 64) -> None:
        self._processor = processor
        self._max_length = max_length

    def __call__(self, examples: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
        texts = [
            self._processor.apply_chat_template(
                ex["messages"], tokenize=False, add_generation_prompt=False
            )
            for ex in examples
        ]
        audios = [np.asarray(ex["audio"]["array"]).flatten() for ex in examples]

        batch: dict[str, Any] = self._processor(
            text=texts,
            audio=audios,
            return_tensors="pt",
            padding=True,
        )
        for k, v in list(batch.items()):
            if isinstance(v, torch.Tensor):
                batch[k] = v.detach().clone()
        batch["labels"] = _mask_labels(batch["input_ids"], self._processor.tokenizer)
        return batch


class WhisperCollator:
    """Collator for Whisper-style encoder-decoder models.

    Processes audio waveforms into log-mel spectrogram ``input_features``
    and tokenizes transcriptions into ``labels`` (decoder input IDs).
    Does **not** use chat templates — reads ``audio`` and ``transcription``
    directly from each example.
    """

    def __init__(self, processor: Any, max_length: int = 448) -> None:
        self._processor = processor
        self._max_length = max_length

    def __call__(self, examples: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
        audios = [np.asarray(ex["audio"]["array"]).flatten() for ex in examples]
        transcriptions = [str(ex["transcription"]) for ex in examples]

        # 1. Audio → log-mel input_features
        batch: dict[str, Any] = self._processor(
            audios,
            sampling_rate=16000,
            return_tensors="pt",
        )

        # 2. Transcriptions → label IDs
        labels_batch = self._processor.tokenizer(
            transcriptions,
            padding=True,
            max_length=self._max_length,
            truncation=True,
            return_tensors="pt",
        )
        batch["labels"] = labels_batch["input_ids"]

        # 3. Mask padding tokens to -100 (ignored by cross-entropy loss)
        pad_id = self._processor.tokenizer.pad_token_id
        if pad_id is not None:
            batch["labels"][batch["labels"] == pad_id] = -100

        return batch


_COLLATOR_MAP = {
    "gemma3n": ChatCollator,
    "whisper": WhisperCollator,
}


def get_collator(
    model_type: str,
    processor: Any,
    max_length: int = 64,
) -> Any:
    """Return a collator instance for the given model type.

    Args:
        model_type: One of 'gemma3n', 'whisper'.
        processor: The model processor (tokenizer + feature extractor).
        max_length: Maximum sequence length for labels.

    Returns:
        An instance of the appropriate collator class.
    """
    collator_cls = _COLLATOR_MAP.get(model_type)
    if collator_cls is None:
        raise ValueError(f"Unknown model type '{model_type}'. " f"Available: {list(_COLLATOR_MAP)}")
    return collator_cls(processor, max_length=max_length)
