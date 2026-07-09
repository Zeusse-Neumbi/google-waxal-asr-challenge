# Skill: noise

## Purpose
Additive noise augmentation from external corpora to improve robustness.

## Inputs
- `audio`: clean speech tensor.
- `noise_dataset`: paths to noise clips.
- `snr_db`: target signal-to-noise ratio (range).

## Outputs
- Noisy `audio` tensor.

## Best Practices
- Sample SNR from a range (e.g. 5–25 dB).
- Match noise sample rate to audio.
- Trim noise to audio length; randomize start offset.
- Keep noise files in `data/external/`.

## Common Mistakes
- Adding digital clipping after gain.
- Using music as "noise" unintentionally.
- Applying to validation data.

## Examples
```python
from waxal_asr.data.augmentation import add_noise
noisy = add_noise(audio, noise_path, snr_db=15.0)
```

## References
- MUSAN corpus: https://www.openslr.org/17/
