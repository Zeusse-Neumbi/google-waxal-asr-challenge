"""Google Gemma 3n / 4n adapter (via HuggingFace Transformers).

Implements the `ASRModel` protocol for the multimodal Gemma family of models.
Registered as `model.model_type: gemma3n` in config.

Supports:
- Gemma 3n E2B (~2B params)
- Gemma 4n E4B (~4B params)
- LoRA / QLoRA fine-tuning via PEFT
"""

from __future__ import annotations

from typing import Any

import torch

from waxal_asr.models.registry import register_model

__all__ = ["Gemma3NModel", "build_gemma3n"]


class Gemma3NModel:
    """Adapter wrapping a HuggingFace Gemma3nForConditionalGeneration model."""

    def __init__(
        self,
        model_id: str = "google/gemma-3n-E2B-it",
        torch_dtype: str = "bfloat16",
        load_in_4bit: bool = False,
        attn_implementation: str = "eager",
        device_map: str = "auto",
    ) -> None:
        self.name = "gemma3n"
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
        import timm  # noqa: F401
        import transformers

        model_id = checkpoint or self.model_id

        self._processor = transformers.AutoProcessor.from_pretrained(model_id)
        self._processor.tokenizer.padding_side = "right"

        quant_kwargs: dict[str, Any] = {}
        if self._load_in_4bit:
            import bitsandbytes  # noqa: F401

            quant_kwargs["quantization_config"] = transformers.BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=self._dtype,
                bnb_4bit_use_double_quant=True,
            )

        self._model = transformers.Gemma3nForConditionalGeneration.from_pretrained(
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
        """Transcribe audio by running the full chat pipeline.

        Args:
            audio: Audio waveform tensor (1D).
            sample_rate: Input sample rate.
            **kwargs: Generation kwargs passed to model.generate().

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

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "audio", "audio": audio_np},
                    {"type": "text", "text": "Please transcribe this audio."},
                ],
            },
        ]

        text_prompt = self._processor.tokenizer.apply_chat_template(
            messages, add_generation_prompt=True, tokenize=False
        )

        inputs = self._processor(
            text=text_prompt,
            audio=[audio_np],
            return_tensors="pt",
            padding=True,
        ).to(self._model.device)

        with torch.no_grad():
            outputs = self._model.generate(
                **inputs,
                max_new_tokens=kwargs.get("max_new_tokens", 128),
                pad_token_id=self._processor.tokenizer.pad_token_id,
            )

        input_len = inputs.input_ids.shape[1]
        decoded = self._processor.tokenizer.batch_decode(
            outputs[:, input_len:], skip_special_tokens=True
        )
        return str(decoded[0]).strip()

    def save(self, path: str) -> None:
        if self._model is None or self._processor is None:
            raise RuntimeError("Model not loaded. Nothing to save.")
        self._model.save_pretrained(path)
        self._processor.save_pretrained(path)


def _parse_dtype(dtype_str: str) -> torch.dtype:
    mapping = {
        "bfloat16": torch.bfloat16,
        "float16": torch.float16,
        "float32": torch.float32,
    }
    if dtype_str not in mapping:
        raise ValueError(f"Unsupported dtype: {dtype_str}. Choose from {list(mapping)}")
    return mapping[dtype_str]


@register_model("gemma3n")
def build_gemma3n(config: Any = None, **kwargs: Any) -> Gemma3NModel:
    """Factory for Gemma3NModel. Accepts a config object or keyword arguments."""
    if config is not None:
        return Gemma3NModel(
            model_id=config.model.model_id,
            torch_dtype=config.model.torch_dtype,
            load_in_4bit=config.model.load_in_4bit,
            attn_implementation=config.model.attn_implementation,
            device_map=config.model.device_map,
        )
    return Gemma3NModel(**kwargs)
