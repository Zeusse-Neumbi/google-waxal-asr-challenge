"""OpenAI Whisper adapter (via HuggingFace Transformers).

Implements the `ASRModel` protocol for encoder-decoder Whisper models.
Registered as `model.model_type: whisper` in config.

Supports:
- Whisper-small, medium, large-v3, etc.
- Resampling in transcribe()
- Optional 4-bit quantization via BitsAndBytes
"""

from __future__ import annotations

from typing import Any

import torch

from waxal_asr.models.registry import register_model

__all__ = ["WhisperModel", "build_whisper"]


class WhisperModel:
    """Adapter wrapping a HuggingFace WhisperForConditionalGeneration model.

    Whisper is an encoder-decoder seq2seq model. The `WhisperProcessor` wraps
    a log-mel feature extractor and a tokenizer. Transcription does NOT use
    chat templates — audio is passed directly to the feature extractor.
    """

    def __init__(
        self,
        model_id: str = "openai/whisper-small",
        torch_dtype: str = "float16",
        load_in_4bit: bool = False,
        attn_implementation: str = "eager",
        device_map: str = "auto",
    ) -> None:
        self.name = "whisper"
        self.sample_rate = 16000
        self.model_id = model_id
        self._torch_dtype_str = torch_dtype
        self._dtype = _parse_dtype(torch_dtype)
        self._load_in_4bit = load_in_4bit
        self._attn_implementation = attn_implementation
        self._device_map = device_map
        self._model: torch.nn.Module | None = None
        self._processor: Any = None

    @property
    def model(self) -> torch.nn.Module:
        if self._model is None:
            raise RuntimeError("Model not loaded. Call load() first.")
        return self._model

    @property
    def processor(self) -> Any | None:
        return self._processor

    def load(self, checkpoint: str | None = None) -> None:
        """Load the Whisper model and processor from HuggingFace Hub or a local checkpoint.

        Args:
            checkpoint: Optional path to a local checkpoint directory. If None,
                loads from `self.model_id` on the Hub.
        """
        import transformers

        model_id = checkpoint or self.model_id

        self._processor = transformers.WhisperProcessor.from_pretrained(model_id)

        quant_kwargs: dict[str, Any] = {}
        if self._load_in_4bit:
            import bitsandbytes  # noqa: F401

            quant_kwargs["quantization_config"] = transformers.BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=self._dtype,
                bnb_4bit_use_double_quant=True,
            )

        self._model = transformers.WhisperForConditionalGeneration.from_pretrained(
            model_id,
            torch_dtype=self._dtype,
            device_map=self._device_map,
            attn_implementation=self._attn_implementation,
            **quant_kwargs,
        )

    def transcribe(
        self,
        audio: torch.Tensor,
        sample_rate: int,
        **kwargs: Any,
    ) -> str:
        """Transcribe audio by running the Whisper encoder-decoder pipeline.

        Args:
            audio: Audio waveform tensor (1D).
            sample_rate: Input sample rate.
            **kwargs: Generation kwargs passed to model.generate().
                Common keys: ``max_new_tokens``, ``language``, ``task``.

        Returns:
            Transcribed text string.
        """
        if self._model is None or self._processor is None:
            raise RuntimeError("Model not loaded. Call load() first.")

        if sample_rate != self.sample_rate:
            import librosa

            audio_np = audio.cpu().numpy() if isinstance(audio, torch.Tensor) else audio
            audio = torch.from_numpy(
                librosa.resample(audio_np, orig_sr=sample_rate, target_sr=self.sample_rate)
            )

        audio_np = audio.cpu().numpy().flatten()

        inputs = self._processor(
            audio=audio_np,
            sampling_rate=self.sample_rate,
            return_tensors="pt",
        ).to(self._model.device)

        with torch.no_grad():
            predicted_ids = self._model.generate(
                **inputs,
                max_new_tokens=kwargs.get("max_new_tokens", 128),
            )

        decoded = self._processor.batch_decode(predicted_ids, skip_special_tokens=True)
        return str(decoded[0]).strip()

    def save(self, path: str) -> None:
        """Save the model and processor to a directory.

        Args:
            path: Directory path to save to.
        """
        if self._model is None or self._processor is None:
            raise RuntimeError("Model not loaded. Nothing to save.")
        self._model.save_pretrained(path)
        self._processor.save_pretrained(path)


def _parse_dtype(dtype_str: str) -> torch.dtype:
    """Convert a dtype string to a PyTorch dtype."""
    mapping = {
        "bfloat16": torch.bfloat16,
        "float16": torch.float16,
        "float32": torch.float32,
    }
    if dtype_str not in mapping:
        raise ValueError(f"Unsupported dtype: {dtype_str}. Choose from {list(mapping)}")
    return mapping[dtype_str]


@register_model("whisper")
def build_whisper(config: Any = None, **kwargs: Any) -> WhisperModel:
    """Factory for WhisperModel. Accepts a config object or keyword arguments."""
    if config is not None:
        return WhisperModel(
            model_id=config.model.model_id,
            torch_dtype=config.model.torch_dtype,
            load_in_4bit=config.model.load_in_4bit,
            attn_implementation=config.model.attn_implementation,
            device_map=config.model.device_map,
        )
    return WhisperModel(**kwargs)
