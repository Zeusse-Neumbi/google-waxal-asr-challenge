# ARCHITECTURE

System design for the WAXAL ASR framework.

---

## Goals

1. **Reproducibility** — every experiment is fully described by a config + seed.
2. **Modularity** — each stage of the ASR pipeline is an independent, testable module.
3. **Extensibility** — new models, datasets, decoders, and metrics plug in via interfaces.
4. **Generalization** — evaluation on held-out data is first-class, never an afterthought.
5. **Maintainability** — readable code, docstrings, type hints, no magic numbers.

---

## High-Level Pipeline

```
            ┌────────────────────────────────────────────────────────┐
            │                     CONFIG LAYER                       │
            │   configs/*.yaml  →  OmegaConf / Hydra  →  dataclass   │
            └────────────────────────────────────────────────────────┘
                                    │
   ┌────────────────────────────────┼────────────────────────────────┐
   │                                ▼                                │
   │   DATA PIPELINE                                                │
   │   audio → validate → resample → normalize → augment →          │
   │   feature-extract → tokenize                                   │
   │                                │                                │
   │                                ▼                                │
   │   MODEL INTERFACE             │                                │
   │   (Whisper | MMS | wav2vec2 | SeamlessM4T | Canary)             │
   │                                │                                │
   │                                ▼                                │
   │   TRAINING LOOP                                                │
   │   (AMP, gradient-accum, schedulers, early-stopping, ckpt)      │
   └────────────────────────────────┼────────────────────────────────┘
                                    │
                ┌───────────────────┴───────────────────┐
                ▼                                       ▼
   EVALUATION PIPELINE                    INFERENCE PIPELINE
   predictions → text-norm → WER/CER      audio → preprocess → model →
   → combined score → reports             decode → postprocess → CSV
```

---

## Package Layout (`src/waxal_asr/`)

| Subpackage      | Responsibility                                          |
| --------------- | ------------------------------------------------------- |
| `config`        | Load, validate, and merge YAML configs into dataclasses |
| `data`          | Dataset loaders, audio loading, preprocessing, augment |
| `models`        | Unified model interface + concrete architectures       |
| `training`      | Trainer, loops, schedulers, checkpointing              |
| `inference`     | Batched inference + post-processing                      |
| `evaluation`    | Metrics, error analysis, report generation              |
| `metrics`       | WER, CER, combined score (independent of training)      |
| `decoding`     | Greedy, beam-search, LM-fused decoders                 |
| `pipeline`      | End-to-end orchestration of train/eval/infer           |
| `visualization` | Plots, error heatmaps, dashboards                       |
| `utils`         | Logging, seeding, IO, audio utilities                  |
| `cli`           | Typer entry points (`waxal-train`, `waxal-eval`, ...)  |

---

## Key Interfaces

### Model Interface

All models implement a common protocol so trainers/inference code is model-agnostic:

```python
class ASRModel(Protocol):
    def transcribe(self, audio: torch.Tensor, sr: int) -> str: ...
    def forward(self, batch: Batch) -> ModelOutput: ...
```

Adding a new model = implementing the protocol + a config entry. No trainer changes.

### Config System

- YAML-first (`configs/`).
- Loaded via OmegaConf / Hydra.
- Strongly-typed via `@dataclass` schemas in `waxal_asr.config.schemas`.
- Configs compose via inheritance (`defaults: baseline.yaml`).

### Experiment Tracking

- Every run writes to `experiments/NNN_name/`:
  `config.yaml`, `metrics.json`, `notes.md`, `logs/`, `plots/`, `predictions.csv`.
- Optional W&B integration (enabled via `tracking: wandb` in config).

---

## Data Flow Details

### Audio Preprocessing

1. **Validate** — check format, sample rate, clipping, silence.
2. **Resample** — target 16 kHz mono (configurable per model).
3. **Normalize** — peak / RMS normalization.
4. **Augment** *(optional, train only)* — SpecAugment, noise, speed perturbation.
5. **Feature extraction** — model-specific (log-mel / raw waveform / Whisper mel).

### Evaluation

1. Load predictions + references.
2. Apply text normalization (lowercase, strip punctuation, unify unicode).
3. Compute WER and CER via `waxal_asr.metrics`.
4. Combined score = `0.5 × WER + 0.5 × CER`.
5. Emit JSON + HTML report with per-utterance analysis.

Evaluation code is **independent** of training code (lives in `evaluation/` + `metrics/`).

---

## Reproducibility

- `waxal_asr.utils.seeding` seeds Python, NumPy, and PyTorch (CPU + CUDA).
- Configs include `seed`, `deterministic`, `benchmark` flags.
- Each experiment directory contains the exact config used.
- Checkpoints include optimizer state for exact resume.

---

## Storage Strategy

| Location        | Purpose                                            |
| --------------- | -------------------------------------------------- |
| Git repo        | code, notebooks, docs, configs, small artifacts     |
| Google Drive    | datasets, checkpoints, cached models, predictions   |
| `outputs/`      | local run outputs (git-ignored)                    |
| `experiments/`  | experiment configs, metrics, notes (committed)     |

Datasets, checkpoints, caches, and temporary files are **never** committed.

---

## Non-Functional Requirements

- Python ≥ 3.11.
- Runs on Google Colab (T4/A100) and local GPU.
- CPU fallback for inference of small models.
- All public functions typed and documented.
- ≥ 80% test coverage on `metrics/`, `data/` utilities, and `config/`.
