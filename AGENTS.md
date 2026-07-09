# AGENTS.md

WAXAL ASR — multilingual speech recognition pipeline for the Google WAXAL Challenge.

## Environment

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt && pip install -e .
```

`requirements-dev.txt` includes `requirements.txt`. Heavy ML deps (torch, transformers,
librosa) are in the base set but the project works without them for config/metrics/testing.
The verify script treats them as optional:

```bash
python scripts/verify_setup.py
```

## Quality gate (run before every commit + PR)

```bash
ruff check . && ruff format --check . && black --check . && mypy -p waxal_asr && pytest -m "not slow and not gpu and not network"
```

- `ruff` handles both lint **and** import sorting (the `I` rule). There is no standalone `isort` in CI/pre-commit despite what old prose may say.
- `black` is for formatting that `ruff format` doesn't cover (both run in CI).
- `mypy -p waxal_asr` (package mode) — **not** `mypy src` which fails because of the `src/` layout + editable install conflict.

## Test commands

```bash
pytest                                          # full suite (includes slow/coverage by default)
pytest -m "not slow and not gpu and not network" # fast (CI + pre-commit)
pytest tests/metrics/test_metrics.py -k test_wer  # single test
pytest --no-cov                                   # skip coverage collection
```

Markers: `unit`, `slow`, `gpu`, `network`. Use `-m` to filter.

## Package architecture

```
src/waxal_asr/          ← single package, src-layout
├── config/             ← YAML loader + typed dataclass schemas (CUSTOM resolver, NOT OmegaConf)
├── data/               ← audio loading, manifests, preprocessing, augmentation (torch-dependent)
├── models/             ← ASRModel protocol + registry (stubs — no concrete models yet)
├── training/           ← Trainer placeholder (NOT implemented — marked experiment 001)
├── inference/          ← Inferencer placeholder
├── evaluation/         ← evaluate() — independent of training
├── metrics/            ← WER/CER/combined — pure Python from scratch (no jiwer at runtime)
├── utils/              ← seeding, logging (loguru), experiments, IO
├── cli/                ← typer entry points → registered as console scripts
│   ├── train.py        → waxal-train
│   ├── evaluate.py     → waxal-eval (functional; needs --references --hypotheses CSVs)
│   ├── infer.py        → waxal-infer (stub)
│   └── submit.py       → waxal-submit (stub)
```

- All files use `from __future__ import annotations`.
- `waxal_asr.metrics` is dependency-free (custom DP edit distance). `jiwer` is in `requirements.txt` but never imported.
- `waxal_asr.metrics.wer` → `wer()`, `cer()`, `combined_score()`, `edit_distance()`. Both accept lists of strings.
- `waxal_asr.metrics.text` → `normalize_text()`, `normalize_corpus()`.
- `waxal_asr.evaluation.evaluate(references, hypotheses, output_dir)` — normalizes, computes WER/CER, writes `metrics.json` + `predictions.csv`.

## Config system

- YAML files in `configs/` with `${paths.data_raw}` interpolation and `defaults: [baseline]` inheritance.
- Load with `from waxal_asr.config import load_config; cfg = load_config("configs/whisper-small.yaml")`.
- Returns a typed `Config` dataclass. The `raw` attribute holds the full dict.
- Configs compose: `whisper-small.yaml` inherits `baseline.yaml`, overrides keys.
- **This is a custom resolver** — OmegaConf and Hydra are listed as deps but NOT wired in.

## Adding a new model

1. Create `src/waxal_asr/models/<name>.py` implementing `ASRModel` protocol (from `models/base.py`).
2. Decorate the factory with `@register_model("<name>")` (from `models/registry.py`).
3. Add an entry in `configs/`.

## Git workflow

- `main` (stable), `dev` (current), `feature/*` / `experiment/*` branches.
- **Never commit directly to `main`.**
- Never commit: datasets, checkpoints, caches, `.env`, `data/raw/*` (except `.gitkeep`).
- Conventional commits: `feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `exp:`, `chore:`.
- **No commits exist yet** — repo is bootstrapped but uncommitted.

## Gotchas

- Config loader uses `typing.get_type_hints` to resolve string annotations (`from __future__`) into actual types. Dataclass `f.type` will be a string, not a type.
- `ruff format` + `black` both run. They can sometimes disagree — let `ruff format` win, then run `black` to confirm both pass. (They currently agree on this codebase.)
- The `scripts/verify_setup.py` skip-fails gracefully when torch/transformers aren't installed — but CI requires them (they're in `requirements-dev.txt`).
- Experiment directories are created by `waxal_asr.utils.experiments.create_experiment(name)`. Monotonic numbers, never overwritten. Scaffold: `config.yaml`, `metrics.json`, `notes.md`, `predictions.csv`, `checkpoint.md`, `logs/`, `plots/`.

## Other files worth reading

- `opencode.json` → `"instructions": ["AGENTS.md", "PROJECT_RULES.md"]` — both are auto-loaded
- `PROJECT_RULES.md` — non-negotiable engineering rules (note: §5 mentions `isort` which is stale; ruff handles imports)
- `SETUP.md` — the original bootstrap spec (reference, not active instruction)
- `ROADMAP.md` — phased experiment plan
- `ARCHITECTURE.md` — system design diagram
