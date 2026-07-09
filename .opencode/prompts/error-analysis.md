# Prompt: error-analysis

Use after an evaluation run, before choosing the next experiment.

## Input expected
- Experiment path with `predictions.csv` and `metrics.json`.

## Output
A markdown report at `experiments/<exp>/error_summary.md` containing:

1. **Headline metrics** — WER, CER, combined, vs baseline.
2. **Error composition** — % insertions / deletions / substitutions.
3. **Stratified errors** — by language, duration bucket, SNR bucket, speaker.
4. **Top-10 worst utterances** — with references and hypotheses.
5. **Hypotheses** — what's causing the dominant error mode.
6. **Next-experiment proposal** — handed to the strategist.
