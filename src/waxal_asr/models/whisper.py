"""OpenAI Whisper adapter (via HuggingFace Transformers).

Implements the `ASRModel` protocol. Registered as `model.name: whisper` in config.
"""

from __future__ import annotations

# Concrete implementation is deferred to the Whisper-baseline experiment.
# When implemented, decorate the factory with @register_model("whisper") and provide:
#   - load(checkpoint)
#   - transcribe(audio, sample_rate) -> str
#   - save(path)
