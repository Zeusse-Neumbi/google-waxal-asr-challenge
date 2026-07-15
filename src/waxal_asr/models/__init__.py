"""Model layer: unified ASR model interface + concrete architectures.

All models implement `waxal_asr.models.base.ASRModel`. The trainer, evaluator, and
inference engine are model-agnostic — they depend only on the protocol.

To add a new model:
1. Create `waxal_asr/models/<name>.py`.
2. Implement `ASRModel`.
3. Register in `waxal_asr/models/registry.py`.
4. Add a config entry.
"""

from waxal_asr.models.base import ASRModel
from waxal_asr.models.gemma3n import Gemma3NModel  # — trigger @register_model
from waxal_asr.models.registry import build_model
from waxal_asr.models.whisper import WhisperModel  # — trigger @register_model

__all__ = ["ASRModel", "Gemma3NModel", "WhisperModel", "build_model"]
