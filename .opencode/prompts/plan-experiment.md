# Prompt: plan-experiment

Use when the strategist proposes a new experiment and we need a structured plan.

## Input expected
- Hypothesis (one sentence).
- Targeted error mode (insertions/deletions/substitutions, language, duration, noise).
- Baseline experiment number to improve upon.

## Output
Produce a markdown plan with:

1. **Goal** — one sentence.
2. **Hypothesis** — why this should help.
3. **Config diff** — what changes from the baseline config.
4. **Steps** — ordered, with acceptance criteria.
5. **Risks** — what could go wrong.
6. **Success criterion** — what combined-score delta counts as a win.
7. **Assignees** — which sub-agents handle each step.
