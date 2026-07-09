# Google WAXAL ASR Challenge

A state-of-the-art, reproducible multilingual **Automatic Speech Recognition (ASR)** pipeline
for the [Google WAXAL ASR Challenge](https://zindi.africa/competitions/google-waxal-asr-challenge/).

> ⚠️ **Status:** Bootstrapped — repository structure, configuration system, and tooling are in place.
> Model implementation is in progress. See [ROADMAP.md](ROADMAP.md).

---

## Mission

Engineer a complete, reproducible, research-quality speech recognition pipeline capable of
achieving a competitive leaderboard position while remaining clean, modular, and extensible —
not just a competition notebook, but a reusable multilingual ASR research framework.

---

## Competition

| Field     | Value                                          |
| --------- | ---------------------------------------------- |
| Challenge | Google WAXAL ASR Challenge                     |
| Dataset   | Google WAXAL Dataset (multilingual speech)     |
| Metric    | `0.5 × WER + 0.5 × CER` (lower is better)      |
| Eval      | Hidden leaderboard, unseen recordings           |

Generalization is prioritized over memorization.

---

## Repository Layout

```
google-waxal-asr-challenge/
├── .github/          # CI, issue/PR templates, CODEOWNERS, Dependabot
├── .opencode/        # AI agent resources (agents, skills, memory, prompts)
├── configs/          # YAML experiment & pipeline configs
├── data/             # raw / processed / interim / external / metadata (git-ignored)
├── docs/             # architecture, dataset, training, results, future work
├── experiments/      # one folder per experiment (config, metrics, notes, predictions)
├── notebooks/        # EDA, visualization, quick experiments (no business logic)
├── outputs/          # models / logs / figures / predictions / temporary (git-ignored)
├── scripts/          # CLI entry points & operational scripts
├── src/waxal_asr/    # production package: data, models, training, evaluation, decoding
├── submissions/      # one CSV per submission + notes.md
├── tests/            # unit + integration tests
├── checkpoints/      # model checkpoints (git-ignored)
├── pyproject.toml    # packaging, lint, type-check, test configuration
└── requirements*.txt # pinned dependencies
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full design.

---

## Quickstart

### 1. Clone & install

```bash
git clone https://github.com/nkz/google-waxal-asr-challenge.git
cd google-waxal-asr-challenge

python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements-dev.txt
pip install -e .
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env: set WANDB_PROJECT, HUGGING_FACE_HUB_TOKEN, data paths, etc.
```

### 3. Run the test suite

```bash
pytest -m "not slow and not gpu"
```

### 4. Run an experiment

```bash
# Train a Whisper-small baseline
python -m waxal_asr.cli.train --config configs/baseline.yaml

# Evaluate a checkpoint
python -m waxal_asr.cli.evaluate --config configs/evaluation.yaml

# Generate a submission
python -m waxal_asr.cli.submit   --config configs/inference.yaml
```

---

## Development

| Task                 | Command                                  |
| -------------------- | ---------------------------------------- |
| Lint                 | `ruff check .`                           |
| Format               | `ruff format . && black .`               |
| Type-check           | `mypy -p waxal_asr`                       |
| Tests                | `pytest`                                 |
| Pre-commit hooks     | `pre-commit install && pre-commit run -a` |

See [CONTRIBUTING.md](CONTRIBUTING.md) and [PROJECT_RULES.md](PROJECT_RULES.md) for the
full workflow.

---

## Supported Models

The framework targets a unified model interface so new architectures plug in easily.
See [MODELS.md](MODELS.md).

- Whisper / Whisper Turbo
- MMS (Massively Multilingual Speech)
- wav2vec2 / XLSR
- SeamlessM4T
- Canary

---

## Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) — system design & pipeline
- [DATASET.md](DATASET.md) — WAXAL dataset description
- [TRAINING.md](TRAINING.md) — training methodology
- [MODELS.md](MODELS.md) — model zoo & interface
- [SUBMISSIONS.md](SUBMISSIONS.md) — submission log
- [ROADMAP.md](ROADMAP.md) — what's next
- [CHANGELOG.md](CHANGELOG.md) — release history
- [PROJECT_RULES.md](PROJECT_RULES.md) — engineering rules
- [CONTRIBUTING.md](CONTRIBUTING.md) — how to contribute

---

## License

[MIT](LICENSE) © WAXAL ASR Contributors.
