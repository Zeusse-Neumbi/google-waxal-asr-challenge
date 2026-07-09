# SUBMISSIONS

Log of every competition submission. Append-only.

---

## Format

Each submission is a CSV produced by `waxal_asr/cli/submit.py` from a config + checkpoint.
Filenames follow the pattern `submission_NNN.csv` (zero-padded, monotonically increasing).

A submission is **never** deleted or overwritten. Use the next number instead.

---

## Submission Log

| #    | Date       | Model           | Config                          | Local WER | Local CER | Local Combined | Notes              |
| ---- | ---------- | --------------- | ------------------------------- | --------- | --------- | -------------- | ------------------ |
| —    | —          | —               | —                               | —         | —         | —              | (none yet)         |

---

## Submission Workflow

1. Train / fine-tune a model → checkpoint in `outputs/models/<exp>/`.
2. Evaluate locally on the held-out dev/test split (`waxal-eval`).
3. Run `waxal-submit --config configs/inference.yaml` to generate the next
   `submission_NNN.csv`.
4. Update `submissions/notes.md` with model, config, metrics, date.
5. Update the table above.
6. Submit to the leaderboard.
7. Record the leaderboard score back here.
