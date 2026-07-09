# experiments

One directory per experiment: `NNN_<name>/` (zero-padded, monotonically increasing).

## Standard layout (created by `waxal_asr.utils.experiments.create_experiment`)

```
experiments/NNN_<name>/
├── config.yaml         # exact config used for the run
├── metrics.json        # WER, CER, combined, losses, timing
├── notes.md            # hypothesis, observations, decisions
├── predictions.csv     # id, reference, hypothesis, language, duration
├── checkpoint.md       # path to best/last checkpoint + git SHA + seed
├── logs/               # training logs
└── plots/              # loss curves, error heatmaps
```

## Rules

- Never overwrite an existing experiment directory.
- Never delete an experiment.
- Large artifacts (checkpoints, raw logs) are git-ignored; configs, metrics, notes, and
  predictions are committed.
- Each experiment is fully reproducible from `config.yaml` + the recorded seed + git SHA.
