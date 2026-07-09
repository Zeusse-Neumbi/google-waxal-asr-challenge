# Skill: wer

## Purpose
Compute Word Error Rate correctly and reproducibly.

## Inputs
- `references`: list[str].
- `hypotheses`: list[str].
- `normalize`: text-normalization toggle.

## Outputs
- WER (float), plus per-utterance alignments.

## Best Practices
- Always normalize text first (lowercase, strip punctuation, unify unicode, collapse
  whitespace).
- Use `jiwer` for standard WER.
- Report WER per language, not just global.
- Keep WER computation independent of training code.

## Common Mistakes
- Comparing case-sensitive strings.
- Not stripping trailing punctuation.
- Averaging per-utterance WERs instead of computing global WER.

## Examples
```python
from waxal_asr.metrics import wer
value = wer(references, hypotheses, normalize=True)
```

## References
- jiwer: https://github.com/jitsi/jiwer
- WER definition: https://en.wikipedia.org/wiki/Word_error_rate
