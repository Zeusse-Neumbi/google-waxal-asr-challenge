# ROADMAP

What's next for the WAXAL ASR framework.

Legend: ✅ done · 🚧 in progress · 📋 planned · 💡 idea

---

## Phase 0 — Bootstrap ✅

- ✅ Repository structure
- ✅ Config system scaffolding (custom YAML resolver, typed dataclasses)
- ✅ CI scaffolding
- ✅ Documentation skeleton
- ✅ `.opencode/` AI workspace
- ✅ Metrics: WER / CER / combined (pure Python, tested)
- ✅ Gemma 3n model adapter + ChatCollator + TRL SFTTrainer flow
- ✅ Submission generator + validator
- ✅ First push to `origin/main` (commit `51c1585`)

### Architecture note (discovered during planning)

The codebase was built around **Gemma 3n** — a multimodal decoder-only model using
chat templates + TRL `SFTTrainer`. Whisper is architecturally different
(encoder-decoder seq2seq). The "model-agnostic" claim in `ARCHITECTURE.md` is
**aspirational**: the Trainer, collator, dataset formatter, and inference batch
function are all Gemma-specific in practice. Supporting Whisper requires
model-type dispatch in four places: `models/`, `data/collator.py`,
`training/trainer.py`, `cli/infer.py`.

---

## Phase 1 — Branch workflow + Whisper baseline (exp 001) 🚧

**Goal:** Implement the Whisper-small model, refactor the Trainer to dispatch
between decoder-only (Gemma/TRL) and encoder-decoder (Whisper/Seq2Seq) paths,
and run experiment 001 end-to-end.

### Step 0 — Branch workflow setup · `github` agent

- Create `dev` branch from `main`, push to origin.
- Establish convention: feature work on `feature/*` off `dev`; `main` stays stable.
- All subsequent steps commit to `feature/whisper-baseline` → PR to `dev`.

**Acceptance:** `dev` exists on origin; `feature/whisper-baseline` checked out locally.

### Step 1 — Implement `WhisperModel` (`models/whisper.py`) · `training` agent

Current state: `whisper.py` is an empty stub (comments only). `models/__init__.py`
does not import it, so `build_model("whisper")` raises `KeyError`.

Tasks:
- Implement `ASRModel` protocol: `load()`, `transcribe()`, `save()`, `model` / `processor` properties.
- Use `transformers.WhisperForConditionalGeneration` + `WhisperProcessor`.
- `load(checkpoint)`: load from `model_id` or checkpoint path; respect `torch_dtype`, `device_map`, `attn_implementation`.
- `transcribe(audio, sample_rate)`: resample if needed → `processor(audio=..., sampling_rate=...)` → `model.generate()` → `processor.batch_decode()`.
- `save(path)`: `save_pretrained()` for model + processor.
- Decorate factory with `@register_model("whisper")`, accept `config: Config`.
- Add `WhisperModel` import to `models/__init__.py` (triggers registration).

**Acceptance:** `build_model("whisper", config=cfg)` returns a `WhisperModel`;
`model.load()` + `model.transcribe(audio_tensor, 16000)` returns a string.

### Step 2 — Add `WhisperCollator` (`data/collator.py`) · `dataset-engineer` agent

Current state: `_COLLATOR_MAP` only has `"gemma3n"`. `get_collator("whisper")` raises `ValueError`.

Tasks:
- Implement `WhisperCollator` (standard HF `DataCollatorSpeechSeq2SeqWithPadding` pattern):
  - `input_features` = log-mel spectrogram from `audio["array"]` (pad to 30s).
  - `labels` = tokenized `transcription` (pad with `processor.tokenizer`).
  - Mask label padding to `-100`.
  - Ignores `messages` key (Whisper doesn't use chat formatting).
- Register in `_COLLATOR_MAP` as `"whisper"`.
- Fix `get_collator` return type annotation (currently `-> ChatCollator`).

**Acceptance:** `get_collator("whisper", processor, max_length=448)` returns a
collator; calling it on a list of `{"audio": {...}, "transcription": "..."}` examples
produces `{"input_features": Tensor, "labels": Tensor, "attention_mask": Tensor}`.

### Step 3 — Dataset path (no change needed) · `documentation` agent

`load_waxal_dataset()` applies `format_for_chat()` which adds a `messages` key but
preserves `audio` and `transcription` via `**example`. The `WhisperCollator` reads
`audio["array"]` and `transcription` directly and ignores `messages`. No code change.
Document this in `ARCHITECTURE.md` and `whisper.py` docstring.

**Acceptance:** `load_waxal_dataset(...)` output works with `WhisperCollator` as-is.

### Step 4 — Refactor `Trainer` to dispatch by model type · `training` agent

Current state: `Trainer.fit()` is hardcoded to TRL `SFTTrainer` + chat-template
flow (Gemma-only). `trl` is imported at module level (line 12) — importing
`training.trainer` fails if `trl` isn't installed, even for Whisper. Output dir
hardcodes `f"gemma3n-asr-{language}"`.

Tasks:
- Make `trl` and `peft` imports **lazy** (inside the Gemma path, not module level).
- Split `fit()` into dispatch: `cfg.model.model_type == "gemma3n"` → `_fit_gemma()`,
  `== "whisper"` → `_fit_whisper()`.
- `_fit_whisper()`:
  - Use `transformers.Seq2SeqTrainer` + `Seq2SeqTrainingArguments`.
  - `predict_with_generate=True`, `generation_max_length=cfg.training.max_seq_length`.
  - `compute_metrics` callback: normalize predictions + references → WER/CER via `waxal_asr.metrics`.
  - Optional LoRA (see Step 6 re: target_modules).
  - Save model + processor to `cfg.paths.outputs / f"whisper-{language}"`.
  - Evaluate on test split with `trainer.predict()`.
- Replace hardcoded `gemma3n-asr-` strings with `f"{cfg.model.model_type}-asr-{language}"`.

**Acceptance:** `waxal-train -c configs/whisper-small.yaml` uses `Seq2SeqTrainer`
(not `SFTTrainer`); completes without `trl` installed.

### Step 5 — Fix `cli/infer.py` dispatch · `training` agent

Current state: `_transcribe_batch` is Gemma-specific (chat template + audio content).

Tasks:
- Dispatch by `cfg.model.model_type`:
  - `"gemma3n"` → existing chat-template path.
  - `"whisper"` → `processor(audio=audio_list, sampling_rate=16000, return_tensors="pt", padding=True)` → `model.generate()` → `processor.batch_decode()`.
- Fix `ids` generation (currently `range(len(batch["transcription"]))` — should use
  actual utterance IDs from the dataset if available, or index from offset).

**Acceptance:** `waxal-infer -c configs/whisper-small.yaml --checkpoint <path>`
produces `outputs/predictions.csv` with `ID,Target` columns.

### Step 6 — Config: fix `whisper-small.yaml` LoRA settings · `general` agent

`whisper-small.yaml` inherits `lora.enabled: true` + `target_modules: [v_proj, o_proj]`
from `baseline.yaml`. These are Gemma-specific; Whisper's linear layers differ.

Tasks:
- Set `lora.enabled: false` in `whisper-small.yaml` (whisper-small is 244M params — full fine-tune is feasible on a single GPU).
- Alternatively, if LoRA is desired, set `target_modules` to Whisper-appropriate layers (`q_proj, v_proj`).
- Verify `load_config("configs/whisper-small.yaml")` populates all `Config` fields.

**Acceptance:** Config loads; `cfg.lora.enabled == False` for whisper-small.

### Step 7 — Fix hardcoded path in `cli/submit.py` · `general` agent

Line 44: `test_csv = Path("google-waxal-asr-challenge20260630-10570-elxebu/Test.csv")`
violates PROJECT_RULES.md §4 (no hardcoded paths).

Tasks:
- Add `test_csv: Path | None = None` to `SubmissionConfig` schema.
- Add `submission.test_csv` to `configs/inference.yaml` (or `baseline.yaml`).
- `cli/submit.py`: read from `cfg.submission.test_csv` as the default, CLI arg overrides.

**Acceptance:** No hardcoded data-dir path in source; `grep -r "10570-elxebu" src/` returns nothing.

### Step 8 — Tests · `general` agent

- `tests/models/test_whisper.py`: mock `transformers.WhisperForConditionalGeneration`
  + `WhisperProcessor`; verify `WhisperModel.load()`, `transcribe()`, `save()`,
  registry lookup `build_model("whisper")`.
- `tests/data/test_collator.py`: mock processor; verify `WhisperCollator` output shapes
  + label masking (`-100`).
- `tests/training/test_trainer_dispatch.py`: verify `model_type="whisper"` routes to
  `_fit_whisper` (mock both paths, assert correct trainer class instantiated).
- All tests use mocks — no GPU/network needed. Mark with `@pytest.mark.unit`.

**Acceptance:** `pytest -m "not slow and not gpu and not network"` passes with new tests.

### Step 9 — Experiment 001 scaffold + run · `experiment-manager` + `training` agents

- `create_experiment("whisper_small_baseline")` → `experiments/001_whisper_small_baseline/`.
- Fill `notes.md`: hypothesis (Whisper-small zero-shot/fine-tune baseline on Shona),
  expected WER range, config diff vs baseline.
- Copy `configs/whisper-small.yaml` → `experiments/001_whisper_small_baseline/config.yaml`.
- Run: `waxal-train -c configs/whisper-small.yaml` (GPU — local or Colab).
- Record metrics in `metrics.json` (WER, CER, combined, val_loss, train_time).
- Record git SHA + seed in `checkpoint.md`.

**Acceptance:** `experiments/001_whisper_small_baseline/` has `config.yaml`,
`metrics.json` with real WER/CER, `notes.md` with observations, `checkpoint.md`.

### Step 10 — Quality gate + PR · `reviewer` agent

- `ruff check . && ruff format --check . && black --check . && mypy -p waxal_asr && pytest -m "not slow and not gpu and not network"`.
- Review on `feature/whisper-baseline`, PR to `dev`.
- Update `CHANGELOG.md`.

**Acceptance:** All gates pass; PR merged to `dev`.

### Risks (Phase 1)

| # | Risk | Mitigation |
|---|------|------------|
| R1 | **GPU availability** — Whisper-small fine-tune needs ≥8 GB VRAM (fp16, bs=16) | Run on Colab T4 if no local GPU; reduce batch size if OOM |
| R2 | **`trl` module-level import** — breaks `training.trainer` import if trl missing | Make lazy (Step 4) |
| R3 | **LoRA target_modules** — `[v_proj, o_proj]` are Gemma-specific, wrong for Whisper | Disable LoRA for whisper-small (Step 6) |
| R4 | **HF dataset access** — `google/WaxalNLP` may be gated | Verify `HF_TOKEN` env var; add to `.env` |
| R5 | **Streaming + Seq2SeqTrainer** — `Seq2SeqTrainer` may not support `IterableDataset` well | Set `streaming: false` + `max_train_samples` to materialize a subset; or pre-download |
| R6 | **Evaluation path** — current `_evaluate` is Gemma-specific | Whisper path uses `trainer.predict()` + `compute_metrics` (Step 4) |

---

## Phase 2 — Fine-tuning & Augmentation 📋

- 📋 Augmentation: SpecAugment, noise, speed perturbation (`data/augmentation/` exists — wire into collator)
- 📋 Experiment logging + W&B integration (`tracking.backend: wandb`)
- 📋 Multi-language training via `interleaved_shuffle()`
- 📋 First competition submission (`submissions/submission_001.csv`)
- 📋 `notebooks/02_dataset_analysis.ipynb` EDA
- 📋 Error analysis notebook (`notebooks/05_error_analysis.ipynb`)

## Phase 3 — Stronger Models 📋

- 📋 Whisper-medium / large-v3 fine-tuning
- 📋 Whisper Turbo for fast inference
- 📋 Beam-search decoding (`waxal_asr/decoding/`)
- 📋 Shallow LM fusion (optional)

## Phase 4 — Model Diversity 📋

- 📋 MMS adapter
- 📋 wav2vec2 / XLSR CTC fine-tuning
- 📋 SeamlessM4T evaluation
- 📋 Canary evaluation
- 📋 Model ensemble / selection per language

## Phase 5 — Error Analysis & Hardening 📋

- 📋 `notebooks/05_error_analysis.ipynb`
- 📋 Per-language error breakdown
- 📋 Duration / SNR / speaker stratified evaluation
- 📋 Robustness: noise, accent, code-switching
- 📋 Final submission strategy

## Phase 6 — Framework Polish 💡

- 💡 Documentation site (mkdocs)
- 💡 Reproducibility CI (deterministic seed check)
- 💡 Public release of the framework beyond the competition

---

## Decision Log

Each phase is informed by the previous phase's error analysis. Never skip analysis.
