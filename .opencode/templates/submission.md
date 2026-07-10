# Template: submission notes

Append to `submissions/notes.md` for every submission.

```markdown
## Submission NNN — <YYYY-MM-DD>

- Model: <model_id>
- Experiment: experiments/NNN_<name>/
- Config: configs/<file>.yaml
- Checkpoint: outputs/models/<exp>/best.ckpt
- Format: CSV with columns `ID, Target` (Zindi competition spec)
- Local WER: <value>
- Local CER: <value>
- Local Combined: <value>
- Notes: <one paragraph on what changed and why>
- Leaderboard score: <to fill after submission>
```
