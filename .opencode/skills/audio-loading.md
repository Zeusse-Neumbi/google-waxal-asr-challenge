# Skill: audio-loading

## Purpose
Load audio files robustly into a normalized tensor suitable for ASR.

## Inputs
- `path`: audio file path (wav, mp3, flac, ogg).
- `target_sr`: desired sample rate (default 16000).
- `mono`: force mono (default True).

## Outputs
- `torch.Tensor` of shape `[channels, samples]` (mono: `[1, T]`).
- `sample_rate`: int.

## Best Practices
- Use `torchaudio.load` for speed; `librosa` as a fallback for exotic formats.
- Always resample to the model's expected rate.
- Trim leading/trailing silence only if downstream code expects it.
- Read from manifests, never hardcode paths.

## Common Mistakes
- Forgetting to resample → silent metric regressions.
- Loading stereo without averaging → shape mismatches.
- Mixing `librosa` (numpy) and `torchaudio` (torch) tensors without conversion.

## Examples
```python
from waxal_asr.data.audio import load_audio
audio, sr = load_audio("data/raw/sample.wav", target_sr=16000)
```

## References
- torchaudio docs: https://docs.pytorch.org/audio/
- librosa docs: https://librosa.org/doc/
