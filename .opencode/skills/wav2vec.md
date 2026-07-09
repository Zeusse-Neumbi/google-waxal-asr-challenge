# Skill: wav2vec

## Purpose
Fine-tune wav2vec2 / wav2vec2-XLSR for CTC-based ASR.

## Inputs
- `model_id`: e.g. `facebook/wav2vec2-large-xlsr-53`.
- `audio`: 16 kHz mono.
- Tokenizer / vocab.

## Outputs
- CTC logits → decoded transcript via greedy or beam search.

## Best Practices
- Use `Wav2Vec2Processor` for features and `Wav2Vec2CTCTokenizer` for text.
- Pad masks carefully — incorrect attention masks wreck CTC.
- Lower LR (e.g. 1e-5 to 3e-5) on the pretrained encoder.
- Build a vocab file from the training transcripts.

## Common Mistakes
- Forgetting to pad input lengths to a multiple of the model's downsample factor.
- CTC blank token mis-indexed.
- Not normalizing transcripts (case, punctuation) before building vocab.

## Examples
```python
from waxal_asr.models.wav2vec2 import Wav2Vec2Model
m = Wav2Vec2Model(model_id="facebook/wav2vec2-xls-r-300m")
text = m.transcribe(audio, sample_rate=16000)
```

## References
- wav2vec2 paper: https://arxiv.org/abs/2006.11477
- XLS-R: https://arxiv.org/abs/2111.09296
