# Skill: feature-extraction

## Purpose
Extract model-appropriate features (log-mel, raw waveform, Whisper mel) from audio.

## Inputs
- `audio`: `torch.Tensor` `[C, T]`.
- `model_name`: e.g. `whisper`, `wav2vec2`.

## Outputs
- Feature tensor ready for the model (e.g. `[batch, n_mels, time]`).

## Best Practices
- Reuse the pretrained model's exact processor (`WhisperProcessor`,
  `Wav2Vec2Processor`) to avoid feature mismatch.
- Cache features to `data/interim/` when training I/O-bound.
- Match `n_fft`, `hop_length`, `n_mels` to the pretrained checkpoint exactly.

## Common Mistakes
- Using a different `hop_length` than the pretraining → catastrophic regressions.
- Forgetting to normalize audio before mel extraction.
- Double-resampling (loader + processor).

## Examples
```python
from waxal_asr.data.features import extract_features
feats = extract_features(audio, model_name="whisper")
```

## References
- Whisper paper: https://arxiv.org/abs/2212.04356
- HF processors: https://huggingface.co/docs/transformers/main_classes/feature_extractor
