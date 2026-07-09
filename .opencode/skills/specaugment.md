# Skill: specaugment

## Purpose
Time/frequency masking on mel-spectrograms to regularize ASR models.

## Inputs
- `features`: mel tensor `[batch, n_mels, time]`.
- `time_mask_param`, `freq_mask_param`, `n_masks`.

## Outputs
- Masked features (same shape).

## Best Practices
- Apply after feature extraction, before the encoder.
- Use HF's built-in `SpecAugment` where available.
- Tune mask params relative to your `n_mels` and audio duration.

## Common Mistakes
- Masking too aggressively on short utterances.
- Applying to the validation set.
- Not seeding → non-reproducible runs.

## Examples
```python
from waxal_asr.data.augmentation import spec_augment
masked = spec_augment(features, time_mask_param=30, freq_mask_param=15)
```

## References
- SpecAugment paper: https://arxiv.org/abs/1904.08779
- torchaudio.transforms.FrequencyMasking / TimeMasking
