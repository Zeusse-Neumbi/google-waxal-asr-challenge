# MODELS

Catalog of supported and planned ASR models, and the unified interface every model must implement.

---

## Model Interface

All models live under `src/waxal_asr/models/` and conform to a single protocol defined in
`waxal_asr/models/base.py`. This keeps the trainer, evaluator, and inference engine
model-agnostic.

```python
from typing import Protocol
import torch

class ASRModel(Protocol):
    name: str
    sample_rate: int   # expected audio sample rate (e.g. 16000)

    def load(self, checkpoint: str | None = None) -> None: ...
    def transcribe(self, audio: torch.Tensor, sample_rate: int) -> str: ...
    def save(self, path: str) -> None: ...
```

HuggingFace-based models additionally expose a `forward(batch)` returning a standard
`ModelOutput` for fine-tuning.

To add a new model:

1. Create `src/waxal_asr/models/<name>.py`.
2. Implement the `ASRModel` protocol.
3. Register it in `waxal_asr/models/registry.py`.
4. Add a config block to `configs/`.

---

## Model Zoo

| Model              | Status      | Module                          | Notes                              |
| ------------------ | ----------- | ------------------------------- | ---------------------------------- |
| Whisper (small)    | Planned     | `models/whisper.py`             | Baseline, multilingual             |
| Whisper (medium)   | Planned     | `models/whisper.py`             | Stronger baseline                  |
| Whisper large-v3   | Planned     | `models/whisper.py`             | Top-tier pretrained                |
| Whisper Turbo      | Planned     | `models/whisper.py`             | Distilled, fast inference          |
| MMS                | Planned     | `models/mms.py`                 | Massively Multilingual Speech      |
| wav2vec2 / XLSR    | Planned     | `models/wav2vec2.py`            | CTC-based                           |
| SeamlessM4T        | Planned     | `models/seamless.py`            | Multimodal, many-to-many          |
| Canary             | Planned     | `models/canary.py`              | NVIDIA Canary-1B                   |

---

## Selection Guidance

- **Start**: Whisper-small baseline → fast feedback loop.
- **Improve**: Whisper-medium / large-v3 with fine-tuning.
- **Production speed**: Whisper Turbo or distilled variants.
- **Low-resource languages**: MMS or wav2vec2 fine-tuned on WAXAL.
- **Cross-lingual transfer**: SeamlessM4T.

Final selection driven by error analysis, not leaderboard chasing.
