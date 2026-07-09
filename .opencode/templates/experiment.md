# Template: experiment directory

Standard layout for every experiment. Created by the experiment-manager agent.

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

## notes.md stub

```markdown
# Experiment NNN: <name>

## Hypothesis
<one sentence>

## Config diff vs baseline
- <field>: <old> -> <new>

## Results
- WER: <value>
- CER: <value>
- Combined: <value>

## Observations
- ...

## Decision
- promote / discard / iterate
```
