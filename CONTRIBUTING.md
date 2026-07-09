# CONTRIBUTING

Thanks for your interest in contributing to the WAXAL ASR framework!

---

## Prerequisites

- Python ≥ 3.11
- `git`
- A GPU is recommended for training, but not required for development.

---

## Setup

```bash
git clone https://github.com/nkz/google-waxal-asr-challenge.git
cd google-waxal-asr-challenge

python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements-dev.txt
pip install -e .

pre-commit install
```

Copy `.env.example` to `.env` and fill in any required tokens (e.g. Hugging Face, W&B).

---

## Workflow

We use a trunk-based workflow with short-lived feature branches.

1. Create a branch off `dev`:
   ```bash
   git checkout dev
   git pull
   git checkout -b feature/<short-description>
   ```
2. Make changes in small, focused commits using
   [Conventional Commits](https://www.conventionalcommits.org/):
   ```
   feat(training): add cosine scheduler with warmup
   fix(metrics): correct CER aggregation
   docs: update TRAINING.md
   refactor(data): simplify audio resampling
   test(metrics): add WER property tests
   ```
3. Run the full quality gate locally:
   ```bash
   pre-commit run --all-files
   pytest -m "not slow and not gpu"
   ```
4. Open a pull request against `dev`. CI must pass.
5. Request review. Address feedback with new commits.

> Never develop directly on `main`. `main` is always shippable.

---

## Coding Standards

- **Style**: PEP 8 via `black` + `ruff` (ruff handles import sorting via its `I` rule).
- **Types**: type hints on all public functions; `mypy` must be clean.
- **Docs**: docstrings (Google or NumPy style) on every public module/function/class.
- **Logging**: `loguru` — never `print()` in `src/`.
- **Paths**: `pathlib.Path` — never string concatenation.
- **Config**: hyperparameters in `configs/*.yaml` — never in code.
- **Tests**: accompany new logic with unit tests in `tests/`.

---

## Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `exp`, `perf`, `ci`.

---

## Tests

```bash
# Fast unit tests
pytest -m "not slow and not gpu"

# Everything (slow)
pytest

# Coverage report
pytest --cov=waxal_asr
```

Target ≥ 80% coverage on `metrics/`, `data/`, `config/`.

---

## Experiments

- Every training run gets its own folder: `experiments/NNN_<name>/`.
- Include `config.yaml`, `metrics.json`, `notes.md`.
- Never overwrite a previous experiment.

See [ROADMAP.md](ROADMAP.md) for planned experiments.

---

## Reporting Issues

Use the GitHub issue templates under `.github/ISSUE_TEMPLATE/`.

- **Bug** — include reproduction steps, expected vs actual, environment.
- **Feature** — describe the problem first, then the proposed solution.

---

## Code of Conduct

Be respectful, constructive, and assume good intent. We're building research-grade
software together.
