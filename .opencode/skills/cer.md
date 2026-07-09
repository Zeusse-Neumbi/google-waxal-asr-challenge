# Skill: cer

## Purpose
Compute Character Error Rate correctly, especially for multilingual scripts.

## Inputs
- `references`: list[str].
- `hypotheses`: list[str].
- `normalize`: text-normalization toggle.

## Outputs
- CER (float), per-utterance alignments.

## Best Practices
- Normalize unicode (NFC) before computing CER — critical for accented characters.
- Strip punctuation unless character-level punctuation matters for the challenge.
- Use `jiwer.cer`.
- Report per-language CER.

## Common Mistakes
- Mixing composed/decomposed unicode forms.
- Including whitespace as a "character" inconsistently.
- Averaging per-utterance CERs instead of computing global CER.

## Examples
```python
from waxal_asr.metrics import cer
value = cer(references, hypotheses, normalize=True)
```

## References
- jiwer: https://github.com/jitsi/jiwer
- Unicode normalization: https://docs.python.org/3/library/unicodedata.html
