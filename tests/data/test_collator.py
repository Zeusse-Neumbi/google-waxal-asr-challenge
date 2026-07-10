"""Unit tests for WhisperCollator + get_collator (mocked processor — no HF deps)."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import numpy as np
import pytest
import torch

from waxal_asr.data.collator import WhisperCollator, get_collator


def _make_fake_processor() -> MagicMock:
    """A mock Whisper-like processor with feature extractor + tokenizer."""
    processor = MagicMock(name="whisper_processor")
    # feature extractor path: processor(audios, sampling_rate=..., return_tensors="pt")
    processor.return_value = {
        "input_features": torch.randn(2, 80, 3000),
        "attention_mask": torch.ones(2, 3000),
    }
    # tokenizer path: processor.tokenizer(texts, padding=..., ...)
    processor.tokenizer = MagicMock(name="tokenizer")
    processor.tokenizer.pad_token_id = 50257
    processor.tokenizer.return_value = {
        "input_ids": torch.tensor([[1, 2, 3, 50257], [4, 5, 50257, 50257]]),
    }
    return processor


def _make_examples() -> list[dict[str, Any]]:
    return [
        {
            "audio": {"array": np.zeros(16000, dtype=np.float32), "sampling_rate": 16000},
            "transcription": "hello world",
            "messages": [],
        },
        {
            "audio": {"array": np.ones(16000, dtype=np.float32), "sampling_rate": 16000},
            "transcription": "goodbye",
            "messages": [],
        },
    ]


class TestWhisperCollatorCall:
    @pytest.mark.unit
    def test_returns_dict_with_input_features_and_labels(self) -> None:
        processor = _make_fake_processor()
        collator = WhisperCollator(processor, max_length=448)

        batch = collator(_make_examples())

        assert isinstance(batch, dict)
        assert "input_features" in batch
        assert "labels" in batch
        assert batch["input_features"].shape == (2, 80, 3000)
        assert batch["labels"].shape == (2, 4)

    @pytest.mark.unit
    def test_processor_called_with_audios(self) -> None:
        processor = _make_fake_processor()
        collator = WhisperCollator(processor, max_length=448)

        collator(_make_examples())

        processor.assert_called_once()
        call_args = processor.call_args
        # First positional arg is the list of audio arrays.
        audios = call_args.args[0]
        assert len(audios) == 2
        assert call_args.kwargs["sampling_rate"] == 16000
        assert call_args.kwargs["return_tensors"] == "pt"

    @pytest.mark.unit
    def test_tokenizer_called_with_transcriptions(self) -> None:
        processor = _make_fake_processor()
        collator = WhisperCollator(processor, max_length=448)

        collator(_make_examples())

        processor.tokenizer.assert_called_once()
        call_args = processor.tokenizer.call_args
        transcriptions = call_args.args[0]
        assert transcriptions == ["hello world", "goodbye"]
        assert call_args.kwargs["padding"] is True
        assert call_args.kwargs["max_length"] == 448
        assert call_args.kwargs["truncation"] is True
        assert call_args.kwargs["return_tensors"] == "pt"

    @pytest.mark.unit
    def test_pad_tokens_masked_to_minus_100(self) -> None:
        processor = _make_fake_processor()
        collator = WhisperCollator(processor, max_length=448)

        batch = collator(_make_examples())

        labels = batch["labels"]
        # pad_token_id=50257 must be replaced by -100.
        assert not torch.isin(labels, torch.tensor(50257)).any()
        # Non-pad tokens should remain unchanged.
        assert labels[0, 0].item() == 1
        assert labels[0, 1].item() == 2
        assert labels[0, 2].item() == 3
        assert labels[1, 0].item() == 4
        assert labels[1, 1].item() == 5
        # Positions that were pad are now -100.
        assert labels[0, 3].item() == -100
        assert labels[1, 2].item() == -100
        assert labels[1, 3].item() == -100

    @pytest.mark.unit
    def test_no_pad_id_skips_masking(self) -> None:
        processor = _make_fake_processor()
        processor.tokenizer.pad_token_id = None
        collator = WhisperCollator(processor, max_length=448)

        batch = collator(_make_examples())

        # Labels unchanged when pad_token_id is None.
        assert torch.isin(batch["labels"], torch.tensor(50257)).any()

    @pytest.mark.unit
    def test_max_length_passed_to_collator(self) -> None:
        processor = _make_fake_processor()
        collator = WhisperCollator(processor, max_length=128)

        collator(_make_examples())

        assert processor.tokenizer.call_args.kwargs["max_length"] == 128


class TestGetCollator:
    @pytest.mark.unit
    def test_get_collator_whisper_returns_whisper_collator(self) -> None:
        processor = _make_fake_processor()
        collator = get_collator("whisper", processor, max_length=448)
        assert isinstance(collator, WhisperCollator)
        assert collator._max_length == 448

    @pytest.mark.unit
    def test_get_collator_unknown_raises(self) -> None:
        processor = _make_fake_processor()
        with pytest.raises(ValueError, match="Unknown model type"):
            get_collator("unknown_type", processor, max_length=448)
