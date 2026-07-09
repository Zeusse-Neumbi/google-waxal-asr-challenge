# Skill: whisper

## Purpose
Use, fine-tune, and decode OpenAI Whisper models via HuggingFace.

## Inputs
- `model_id`: e.g. `openai/whisper-small`, `whisper-large-v3`.
- `audio`: 16 kHz mono.
- `language`: target language code (optional).

## Outputs
- Transcribed text.

## Best Practices
- Always feed 16 kHz mono — Whisper's processor expects it.
- Use `WhisperProcessor` for features and `WhisperTokenizer` for text.
- For fine-tuning, freeze the encoder initially; lower LR on decoder.
- Set `language` and `task="transcribe"` for stable multilingual behavior.

## Common Mistakes
- Letting Whisper auto-detect language on short clips → flaky outputs.
- Forgetting `forced_decoder_ids` for the target language during fine-tune.
- Using a different processor than the pretraining checkpoint.

## Examples
```python
from waxal_asr.models.whisper import WhisperModel
m = WhisperModel(model_id="openai/whisper-small")
text = m.transcribe(audio, sample_rate=16000, language="fr")
```

## References
- Whisper paper: https://arxiv.org/abs/2212.04356
- HF fine-tuning guide: https://huggingface.co/blog/fine-tune-whisper
