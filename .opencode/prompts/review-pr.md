# Prompt: review-pr

Use before opening any pull request.

## Output
For each file in the diff:

1. List violations of `PROJECT_RULES.md` with `file:line` + rule citation.
2. Check: hardcoded paths? hardcoded hyperparameters? magic numbers? `print()` in `src/`?
   missing types/docstrings? missing tests?
3. Run: `ruff check . && black --check . && mypy -p waxal_asr && pytest -m "not slow and not gpu"`.
4. Verdict: APPROVE / REQUEST_CHANGES / BLOCK.
