# Skill: zindi

## Purpose
Follow Zindi competition mechanics for the WAXAL ASR challenge (submissions,
leaderboard, rules).

## Inputs
- `submission_NNN.csv`, local eval metrics.

## Outputs
- Validated submission file uploaded to Zindi.

## Best Practices
- Validate the CSV schema (column names, row count, IDs) before uploading.
- Always run local evaluation before submitting.
- Track each submission in `SUBMISSIONS.md`.
- Respect submission frequency limits.

## Common Mistakes
- Submitting without local validation → wasted attempts.
- Misaligned IDs between submission and the hidden test set.
- Overwriting previous submission files locally.

## Examples
```bash
python -m waxal_asr.cli.submit --config configs/inference.yaml
```

## References
- Zindi: https://zindi.africa/
