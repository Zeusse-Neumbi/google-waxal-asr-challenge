# Skill: xlsr

## Purpose
Use XLS-R (cross-lingual speech representation) models for multilingual ASR.

## Inputs
- `model_id`: e.g. `facebook/wav2vec2-xls-r-300m`, `1b`, `2b`.
- `audio`: 16 kHz mono.
- Language-specific vocab / tokenizer.

## Outputs
- CTC-decoded transcript.

## Best Practices
- Larger XLS-R = better transfer, but heavier GPU memory.
- Fine-tune with a language-balanced sampler for multilingual WAXAL.
- Use UniGram/BBPE tokenizers carefully; verify special tokens.

## Common Mistakes
- Treating XLS-R like wav2vec2 English (it isn't — multilingual vocab matters).
- Ignoring the CTC blank token index from the tokenizer.

## Examples
```python
from waxal_asr.models.wav2vec2 import Wav2Vec2Model
m = Wav2Vec2Model(model_id="facebook/wav2vec2-xls-r-1b")
```

## References
- XLS-R paper: https://arxiv.org/abs/2111.09296
