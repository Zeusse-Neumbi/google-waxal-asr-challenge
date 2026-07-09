# Skill: experiment-tracking

## Purpose
Record every experiment so it can be reproduced and compared.

## Inputs
- `config` (YAML/dataclass), `metrics`, `notes`, predictions.

## Outputs
- `experiments/NNN_<name>/` containing: `config.yaml`, `metrics.json`, `notes.md`,
  `logs/`, `plots/`, `predictions.csv`, `checkpoint.md`.

## Best Practices
- Allocate experiment numbers monotonically; never reuse.
- Copy the exact run config (not a reference).
- Record git SHA + config hash + seed.
- Optional: mirror to W&B (configurable).

## Common Mistakes
- Overwriting a previous experiment's metrics.
- Forgetting to record the seed or config version.
- Letting two experiments share a directory name.

## Examples
```python
from waxal_asr.utils.experiments import create_experiment
exp = create_experiment(name="whisper_small_baseline")
```

## References
- See `SETUP.md` "EXPERIMENTS" section.
