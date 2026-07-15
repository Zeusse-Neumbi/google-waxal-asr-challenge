# CHANGELOG

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Initial repository scaffold per `SETUP.md` and `AGENT.md`.
- Directory structure: `src/`, `configs/`, `data/`, `experiments/`, `outputs/`,
  `submissions/`, `tests/`, `notebooks/`, `scripts/`, `docs/`, `checkpoints/`.
- `.opencode/` workspace with agents, skills, memory, prompts, templates.
- Configuration system scaffolding (`pyproject.toml`, `requirements*.txt`).
- CI scaffolding under `.github/`.
- Root documentation: README, ARCHITECTURE, MODELS, TRAINING, DATASET, SUBMISSIONS,
  ROADMAP, PROJECT_RULES, CONTRIBUTING, CHANGELOG.
- `SubmissionGenerator` and `SubmissionValidator` modules in `src/waxal_asr/submission/`.

### Changed
- `configs/inference.yaml` — fixed submission schema to `[ID, Target]`, removed `test_audio_dir`.
- `configs/baseline.yaml` — added `dataset` section with HuggingFace dataset ID.
- `src/waxal_asr/data/manifest.py` — updated `REQUIRED_COLUMNS` to Zindi CSV format (`id, transcription, language, split`), added `from_zindi_train_csv()` classmethod.
- `src/waxal_asr/cli/submit.py` — replaced stub with functional submission generator.
- `src/waxal_asr/config/schemas.py` — added `DatasetConfig` and `SubmissionConfig` dataclasses.
- `DATASET.md` — corrected region (27 African languages, focus: Lingala/Shona/Luganda), added HuggingFace source, fixed manifest schema.
- `ARCHITECTURE.md` — fixed "OmegaConf / Hydra" → "custom YAML resolver".
- `README.md` — added specific focus languages to competition table.
- `ROADMAP.md` — fixed "Dataset download" → "HuggingFace dataset loading".
- `.opencode/memory/competition.md` — filled all TODOs with actual competition details (dates, rules, prizes, languages, submission limits, Phase 1/2).
- `.opencode/memory/dataset.md` — filled with Zindi CSV schema, language stats, HuggingFace reference.
- `.opencode/agents/submission.md` — specifies `ID,Target` format, HuggingFace data source.
- `.opencode/agents/dataset-engineer.md` — references HuggingFace streaming instead of local files.
- `.opencode/agents/reviewer.md` — removed stale `isort` references.
- `.opencode/skills/zindi.md` — added competition URL, submission limits, Phase 2 details.
- `.opencode/skills/dataset-analysis.md` — fixed manifest schema reference.
- `.opencode/templates/submission.md` — added `ID, Target` column reference.
- `.opencode/templates/experiment.md` — fixed predictions.csv schema.
- `AGENTS.md` — removed stale `isort` notes.

### Removed
- `omegaconf` from `pyproject.toml` dependencies (custom resolver used instead).
- `hydra-core` optional dependency (not used).
- `isort` from dev dependencies and requirements-dev.txt (ruff handles imports).
- OmegaConf and Hydra references from `requirements.txt`.

### Fixed
- Remaining stale references to OmegaConf, Hydra, and isort across docs and config.
- Pinned `datasets<5.0` and `transformers<5.0` in `requirements.txt`. The uncapped `>=` spec resolved to `datasets==5.0.0` / `transformers==5.13.0` (breaking majors). `datasets` 5.0 replaced the `Audio` feature's `{"array","sampling_rate"}` dict output with `torchcodec.decoders.AudioDecoder` objects, which crashed the data pipeline at `data/dataset.py` `.map()` (Arrow could not infer a type for `AudioDecoder`). Pin restores the dict contract the dataset/collator/trainer code expects.

### Deprecated
- None yet.

### Removed
- None yet.

### Fixed
- None yet.

### Security
- None yet.

---

## [0.1.0] - 2026-07-09

### Added
- Project bootstrap. Repository initialized and ready for implementation.
