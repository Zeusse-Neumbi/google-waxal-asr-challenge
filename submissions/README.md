# submissions

Competition submissions. **Append-only — never delete or overwrite.**

## Naming
`submission_NNN.csv` (zero-padded, strictly increasing).

## Workflow
1. Train a model → checkpoint in `outputs/models/<exp>/`.
2. Evaluate locally (`waxal-eval`).
3. Generate the next submission: `python -m waxal_asr.cli.submit --config configs/inference.yaml`.
4. Update `notes.md` with model, config, metrics, date.
5. Update `SUBMISSIONS.md` at the repo root.
6. Submit to Zindi.
7. Record the leaderboard score back in `SUBMISSIONS.md` + `.opencode/memory/leaderboard.md`.

## Notes file
See `notes.md` (created on first submission) for the per-submission log.
