# Skill: huggingface

## Purpose
Use the HuggingFace Hub + Transformers/Datasets/Accelerate ecosystem safely.

## Inputs
- `model_id`, `dataset_id`, optional `token`.

## Outputs
- Models, datasets, processors loaded into memory.

## Best Practices
- Use `hf_transfer` for fast downloads on Colab.
- Cache to `~/.cache/huggingface` or a Drive-backed cache dir.
- Pin `transformers` version for reproducibility.
- Use `accelerate` for distributed/mixed-precision training.
- Never commit your `HUGGING_FACE_HUB_TOKEN`.

## Common Mistakes
- Forgetting to set `cache_dir` → Colab disk fills up.
- Loading a model without its matching processor.
- Letting `transformers` auto-update mid-experiment.

## Examples
```python
from transformers import WhisperProcessor
proc = WhisperProcessor.from_pretrained("openai/whisper-small")
```

## References
- HF docs: https://huggingface.co/docs/transformers
