# Skill: augmentation

## Purpose
Apply train-only audio augmentations to improve generalization.

## Inputs
- `audio`: `torch.Tensor`.
- `config`: augmentation spec from `configs/augmentation.yaml`.

## Outputs
- Augmented `audio` tensor (same shape).

## Best Practices
- Augment train only — never dev/test.
- Compose: speed perturbation → noise → SpecAugment.
- Keep augmentation parameters in config, not in code.
- Seed RNGs for reproducibility.

## Common Mistakes
- Augmenting validation data → inflated metrics.
- Over-augmenting → model never sees clean speech.
- Forgetting to handle clipping after gain.

## Examples
```python
from waxal_asr.data.augmentation import compose
aug = compose(audio, config=cfg.augmentation)
```

## References
- SpecAugment: https://arxiv.org/abs/1904.08779
- Speed perturbation: https://arxiv.org/abs/1904.08779
