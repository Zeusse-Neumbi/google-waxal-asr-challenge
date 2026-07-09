# Skill: speed-perturbation

## Purpose
Time-stretch audio by factors (e.g. {0.9, 1.0, 1.1}) to expand effective data.

## Inputs
- `audio`: `torch.Tensor`.
- `factors`: list of playback speeds.

## Outputs
- Perturbed `audio` tensor (length changes accordingly).

## Best Practices
- Use factors {0.9, 1.0, 1.1} as a sensible default.
- Preserve pitch (use phase vocoder) unless pitch shift is desired.
- Apply per-epoch with random factor.

## Common Mistakes
- Forgetting to update transcript alignment (not relevant for end-to-end ASR but
  relevant for CTC forced alignment).
- Introducing audible artifacts with naive resampling.

## Examples
```python
from waxal_asr.data.augmentation import speed_perturb
out = speed_perturb(audio, factor=1.1)
```

## References
- SpecAugment paper (introduced speed perturbation for ASR): https://arxiv.org/abs/1904.08779
- torchaudio SoX effects: https://docs.pytorch.org/audio/stable/sox_effects.html
