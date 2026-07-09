# PROJECT RULES

Engineering rules for the WAXAL ASR project. Non-negotiable.

---

## 1. Configuration over code

- All hyperparameters, paths, model names → `configs/*.yaml`.
- Never modify Python to change a hyperparameter.
- Configs compose via inheritance; never duplicate.

## 2. Reproducibility

- Seed everything (`waxal_asr.utils.seeding`).
- Every experiment records its exact config + git SHA.
- Never overwrite a checkpoint or experiment directory.

## 3. Modularity

- One responsibility per module.
- Reusable logic lives in `src/waxal_asr/`, never in notebooks.
- Notebooks are for EDA, visualization, and quick experiments only.

## 4. No hardcoding

- No hardcoded paths (use `configs/` + `pathlib`).
- No hardcoded hyperparameters.
- No hardcoded secrets (use `.env` + `python-dotenv`).
- No magic numbers (name them, document them).

## 5. Quality gates

- Every PR must pass: `ruff`, `black --check`, `isort --check`, `mypy`, `pytest`.
- No `print()` in `src/` — use `loguru`.
- Public functions have type hints + docstrings.
- Tests for `metrics/`, `data/` utilities, and `config/`.

## 6. Evaluation discipline

- Evaluate locally before submitting.
- Evaluation code is independent of training code.
- Error analysis precedes the next model iteration.

## 7. Version control

- Commit often, with conventional-commit messages.
- Never develop directly on `main`.
- Never commit: datasets, checkpoints, caches, `.env`, temporary files.

## 8. Documentation

- Documentation is part of development, not an afterthought.
- Update `CHANGELOG.md` with every notable change.
- Update `experiments/<exp>/notes.md` for every experiment.

## 9. AI Agent behavior

- Think before coding.
- Search the repository before writing new code.
- Reuse existing modules.
- Question poor assumptions.
- Document every significant decision.
- Never produce quick hacks when a maintainable solution exists.
