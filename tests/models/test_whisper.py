"""Unit tests for the Whisper model adapter (mocked — no GPU/network/downloads)."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import torch

from waxal_asr.config import load_config
from waxal_asr.models.registry import build_model
from waxal_asr.models.whisper import WhisperModel

_REPO_ROOT = Path(__file__).resolve().parents[2]


class _FakeInputs(dict):
    """Dict that also supports ``.to(device)`` (mimics BatchFeature)."""

    def to(self, device: Any) -> _FakeInputs:
        return self


class TestWhisperModelInit:
    @pytest.mark.unit
    def test_init_stores_defaults(self) -> None:
        m = WhisperModel()
        assert m.name == "whisper"
        assert m.sample_rate == 16000
        assert m.model_id == "openai/whisper-small"
        assert m._torch_dtype_str == "float16"
        assert m._load_in_4bit is False
        assert m._attn_implementation == "eager"
        assert m._device_map == "auto"

    @pytest.mark.unit
    def test_init_stores_custom(self) -> None:
        m = WhisperModel(
            model_id="openai/whisper-large-v3",
            torch_dtype="bfloat16",
            load_in_4bit=True,
            attn_implementation="sdpa",
            device_map="cuda:0",
        )
        assert m.model_id == "openai/whisper-large-v3"
        assert m._torch_dtype_str == "bfloat16"
        assert m._load_in_4bit is True
        assert m._attn_implementation == "sdpa"
        assert m._device_map == "cuda:0"

    @pytest.mark.unit
    def test_dtype_parsed(self) -> None:
        m = WhisperModel(torch_dtype="float32")
        assert m._dtype == torch.float32

    @pytest.mark.unit
    def test_invalid_dtype_raises(self) -> None:
        with pytest.raises(ValueError, match="Unsupported dtype"):
            WhisperModel(torch_dtype="int8")


class TestWhisperModelBeforeLoad:
    @pytest.mark.unit
    def test_model_property_raises_before_load(self) -> None:
        m = WhisperModel()
        with pytest.raises(RuntimeError, match="not loaded"):
            _ = m.model

    @pytest.mark.unit
    def test_processor_is_none_before_load(self) -> None:
        m = WhisperModel()
        assert m.processor is None


class TestWhisperModelLoad:
    @pytest.mark.unit
    def test_load_calls_from_pretrained(self) -> None:
        """load() imports transformers lazily; we inject a mock via sys.modules."""
        mock_tf = MagicMock(name="transformers")
        mock_tf.WhisperProcessor.from_pretrained.return_value = MagicMock(name="proc")
        mock_tf.WhisperForConditionalGeneration.from_pretrained.return_value = MagicMock(
            name="model"
        )

        m = WhisperModel(model_id="openai/whisper-small", torch_dtype="float16")

        with patch.dict("sys.modules", {"transformers": mock_tf}):
            m.load()

        mock_tf.WhisperProcessor.from_pretrained.assert_called_once_with("openai/whisper-small")
        mock_tf.WhisperForConditionalGeneration.from_pretrained.assert_called_once()
        call_kwargs = mock_tf.WhisperForConditionalGeneration.from_pretrained.call_args
        assert call_kwargs.args[0] == "openai/whisper-small"
        assert call_kwargs.kwargs["torch_dtype"] == torch.float16
        assert call_kwargs.kwargs["device_map"] == "auto"

        assert m._model is mock_tf.WhisperForConditionalGeneration.from_pretrained.return_value
        assert m._processor is mock_tf.WhisperProcessor.from_pretrained.return_value

    @pytest.mark.unit
    def test_load_with_checkpoint_override(self) -> None:
        m = WhisperModel(model_id="openai/whisper-small")
        mock_tf = MagicMock()
        mock_tf.WhisperProcessor.from_pretrained.return_value = MagicMock()
        mock_tf.WhisperForConditionalGeneration.from_pretrained.return_value = MagicMock()

        with patch.dict("sys.modules", {"transformers": mock_tf}):
            m.load(checkpoint="/tmp/fake-checkpoint")

        mock_tf.WhisperProcessor.from_pretrained.assert_called_once_with("/tmp/fake-checkpoint")
        mock_tf.WhisperForConditionalGeneration.from_pretrained.assert_called_once()
        assert (
            mock_tf.WhisperForConditionalGeneration.from_pretrained.call_args.args[0]
            == "/tmp/fake-checkpoint"
        )


class TestWhisperModelTranscribe:
    @pytest.mark.unit
    def test_transcribe_before_load_raises(self) -> None:
        m = WhisperModel()
        with pytest.raises(RuntimeError, match="not loaded"):
            m.transcribe(torch.zeros(16000), 16000)

    @pytest.mark.unit
    def test_transcribe_pipeline(self) -> None:
        """End-to-end transcribe() with fully mocked model + processor."""
        m = WhisperModel()

        fake_model = MagicMock(name="model")
        fake_model.device = torch.device("cpu")
        fake_model.generate.return_value = torch.tensor([[1, 2, 3, 4]])

        fake_processor = MagicMock(name="processor")
        fake_processor.return_value = _FakeInputs(
            input_features=torch.zeros(1, 80, 3000),
        )
        fake_processor.batch_decode.return_value = ["  hello world  "]

        m._model = fake_model
        m._processor = fake_processor

        audio = torch.zeros(16000)
        result = m.transcribe(audio, 16000)

        # Processor called with flattened numpy audio + sampling_rate.
        fake_processor.assert_called_once()
        call_kwargs = fake_processor.call_args.kwargs
        assert call_kwargs["sampling_rate"] == 16000
        assert call_kwargs["return_tensors"] == "pt"

        # model.generate called with input_features + max_new_tokens.
        fake_model.generate.assert_called_once()
        gen_kwargs = fake_model.generate.call_args.kwargs
        assert "input_features" in gen_kwargs
        assert gen_kwargs["max_new_tokens"] == 128

        # batch_decode called with skip_special_tokens=True.
        fake_processor.batch_decode.assert_called_once()
        decode_kwargs = fake_processor.batch_decode.call_args
        assert decode_kwargs.args[0] is fake_model.generate.return_value
        assert decode_kwargs.kwargs["skip_special_tokens"] is True

        # Return value is a stripped string.
        assert isinstance(result, str)
        assert result == "hello world"

    @pytest.mark.unit
    def test_transcribe_passes_max_new_tokens_kwarg(self) -> None:
        m = WhisperModel()

        fake_model = MagicMock()
        fake_model.device = torch.device("cpu")
        fake_model.generate.return_value = torch.tensor([[1]])
        fake_processor = MagicMock()
        fake_processor.return_value = _FakeInputs(input_features=torch.zeros(1, 80, 3000))
        fake_processor.batch_decode.return_value = ["x"]

        m._model = fake_model
        m._processor = fake_processor

        m.transcribe(
            torch.zeros(16000), 16000, max_new_tokens=256, language="en", task="transcribe"
        )

        gen_kwargs = fake_model.generate.call_args.kwargs
        assert gen_kwargs["max_new_tokens"] == 256


class TestWhisperModelSave:
    @pytest.mark.unit
    def test_save_before_load_raises(self) -> None:
        m = WhisperModel()
        with pytest.raises(RuntimeError, match="not loaded"):
            m.save("/tmp/out")

    @pytest.mark.unit
    def test_save_calls_pretrained_methods(self) -> None:
        m = WhisperModel()
        fake_model = MagicMock()
        fake_processor = MagicMock()
        m._model = fake_model
        m._processor = fake_processor

        m.save("/tmp/fake-save")

        fake_model.save_pretrained.assert_called_once_with("/tmp/fake-save")
        fake_processor.save_pretrained.assert_called_once_with("/tmp/fake-save")


class TestBuildModelWhisper:
    @pytest.mark.unit
    def test_whisper_is_registered(self) -> None:
        """build_model('whisper') should succeed (models/__init__.py imports it)."""
        m = build_model("whisper", model_id="openai/whisper-tiny")
        assert isinstance(m, WhisperModel)
        assert m.model_id == "openai/whisper-tiny"

    @pytest.mark.unit
    def test_build_model_unknown_raises(self) -> None:
        with pytest.raises(KeyError, match="Unknown model"):
            build_model("nonexistent_model")

    @pytest.mark.unit
    def test_build_model_with_config(self) -> None:
        cfg = load_config(_REPO_ROOT / "configs" / "whisper-small.yaml")
        m = build_model("whisper", config=cfg)
        assert isinstance(m, WhisperModel)
        assert m.model_id == "openai/whisper-small"
        assert m._torch_dtype_str == "float16"
        assert m._load_in_4bit is False

    @pytest.mark.unit
    def test_build_model_with_mock_config(self) -> None:
        """Factory reads config.model.{model_id, torch_dtype, ...} fields."""
        mock_cfg = MagicMock()
        mock_cfg.model.model_id = "openai/whisper-medium"
        mock_cfg.model.torch_dtype = "float32"
        mock_cfg.model.load_in_4bit = True
        mock_cfg.model.attn_implementation = "sdpa"
        mock_cfg.model.device_map = "cpu"

        m = build_model("whisper", config=mock_cfg)
        assert isinstance(m, WhisperModel)
        assert m.model_id == "openai/whisper-medium"
        assert m._torch_dtype_str == "float32"
        assert m._load_in_4bit is True
        assert m._attn_implementation == "sdpa"
        assert m._device_map == "cpu"
