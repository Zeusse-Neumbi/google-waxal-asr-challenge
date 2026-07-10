# Skill: zindi

## Purpose
Follow Zindi competition mechanics for the WAXAL ASR challenge (submissions,
leaderboard, rules).

## Inputs
- `submission_NNN.csv` (columns: `ID`, `Target`), local eval metrics.

## Outputs
- Validated submission file uploaded to Zindi.

## Best Practices
- Validate the CSV schema (`ID`, `Target` columns, row count, IDs) before uploading.
- Always run local evaluation before submitting.
- Track each submission in `SUBMISSIONS.md`.
- Respect submission frequency limits (5/day, 200 total).
- Remember Phase 2 provides audio-only — no metadata (language, speaker) available.

## Common Mistakes
- Submitting without local validation → wasted attempts.
- Misaligned IDs between submission and the hidden test set.
- Overwriting previous submission files locally.
- Assuming metadata will be available in Phase 2.
- Using `id,transcript` columns instead of `ID,Target`.

## Examples
```bash
python -m waxal_asr.cli.submit --config configs/inference.yaml --test-csv path/to/Test.csv
```

## References
- Challenge page: https://zindi.africa/competitions/google-waxal-asr-challenge/
- Data: https://zindi.africa/competitions/google-waxal-asr-challenge/data
- Dataset: https://huggingface.co/datasets/google/WaxalNLP
